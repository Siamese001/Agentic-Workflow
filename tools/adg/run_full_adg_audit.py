"""ADG audit pipeline wrapper — the two-stage certification entrypoint.

Stage 1: ``tools/generate/generate_full_adg.py`` — produces the snapshot,
runs preflight/validation/post-ADG gates, emits the gate invocation +
generation manifests.

Stage 2: ``tools/adg/three_bucket_gap_report.py`` — runs the seven-class
reconciliation against the exact snapshot path declared by Stage 1's
generation manifest.

The wrapper is the fail-closed consumer: it reads the manifests, cross-
checks against the required-gate registry, enforces runtime-proof when
requested, and propagates a single aggregate exit code.

Plan: ``docs/archive/windsurf/legacy-tree/plans/adg-audit-pipeline-integration-7f2c93.md`` W2.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"
RECEIPT_PATH = REPO_ROOT / "docs" / "reports" / "adg" / "AUDIT_PIPELINE_RECEIPT.json"
HANDOFF_CONTRACT_PATH = REPO_ROOT / ".codex" / "automations" / "adg-audit-and-burndown" / "automation.toml"
RECEIPT_SCHEMA_VERSION = "adg-audit-pipeline-receipt/v1"
REPAIR_HANDOFF_SCHEMA_VERSION = "adg-repair-handoff/v1"
REPAIR_HANDOFF_POINTER_SCHEMA_VERSION = "adg-repair-handoff-pointer/v1"
REPAIR_ARTIFACT_KEYS: tuple[str, ...] = (
    "snapshot",
    "gate_results",
    "action_queue",
    "burndown_report",
    "burndown_table",
    "generation_manifest",
    "gate_manifest",
    "output_bundle",
)
RUN_ID_COLLISION_EXIT_CODE = 73
_LAST_GENERATOR_RUN_ID: str | None = None


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class WrapperResult:
    certification_status: str
    generator_exit_code: int | None
    report_exit_code: int | None
    generation_manifest_path: Path | None
    gate_manifest_path: Path | None
    runtime_proof_status: str
    reasons: list[str]
    artifact_status: str = "incomplete"
    artifact_status_source: str = "direct"
    adg_run_id: str | None = None
    started_at_utc: str | None = None
    completed_at_utc: str | None = None
    repair_handoff: dict[str, Any] | None = None
    process_exit_code: int = 1

    @property
    def ok(self) -> bool:
        return (
            self.certification_status == "clean" and self.artifact_status == "certified" and not self.reasons
        )


@dataclass(frozen=True)
class PublicationDocuments:
    """Immutable documents prepared before snapshot-pointer activation."""

    receipt_path: Path
    handoff_path: Path
    latest_handoff_pointer: dict[str, Any]
    receipt_text: str


def _find_generation_manifest(
    since_monotonic_start: float,
    *,
    expected_run_id: str | None = None,
) -> Path | None:
    """Return the newest generation manifest created during this run.

    We filter by mtime strictly greater than ``wall_start`` to avoid
    picking up a stale manifest from a prior run. ``latest.json`` is
    NEVER consulted from CI — CI resolves by timestamped filename.
    """
    if expected_run_id is not None:
        exact = ARTIFACTS_ADG / f"adg_generation_manifest_{expected_run_id}.json"
        # The wrapper chooses the exact run ID before spawning the generator.
        # Unlike newest-file discovery, no clock-skew allowance is safe here:
        # accepting a pre-spawn same-minute manifest can adopt a prior run when
        # the child dies before it reaches its run-ID claim.
        if not exact.is_file() or exact.stat().st_mtime < since_monotonic_start:
            return None
        return exact
    candidates = sorted(
        ARTIFACTS_ADG.glob("adg_generation_manifest_*.json"),
        key=lambda p: p.stat().st_mtime,
    )
    candidates = [p for p in candidates if p.name != "adg_generation_manifest_latest.json"]
    if not candidates:
        return None
    newest = candidates[-1]
    # We accept any manifest produced during or after the wrapper-start
    # wall clock — with a 2s fudge for clock skew on shared CI runners.
    if newest.stat().st_mtime + 2 < since_monotonic_start:
        return None
    return newest


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"JSON document must be an object: {path}")
    return payload


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _abs(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path)


def _path_matches(left: str | None, right: Path) -> bool:
    if not left:
        return False
    try:
        return _abs(Path(left)).resolve() == right.resolve()
    except OSError:
        return Path(left).name == right.name


def _is_generator_run_stamp(value: str) -> bool:
    try:
        datetime.strptime(value, "%m%d%Y_%H%M")
    except ValueError:
        return False
    return True


def _is_gate_results_stamp(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y%m%d_%H%M%S")
    except ValueError:
        return False
    return True


def _is_timestamped_artifact(path: Path, key: str) -> bool:
    stem = path.stem
    if "latest" in stem.lower():
        return False
    expected = {
        "snapshot": ("adg_indexed_", ".sqlite"),
        "generation_manifest": ("adg_generation_manifest_", ".json"),
        "gate_manifest": ("adg_gate_invocation_manifest_", ".json"),
        "gate_results": ("adg_gate_results_", ".json"),
        "action_queue": ("adg_action_queue_", ".json"),
        "burndown_report": ("adg_burndown_report_", ".md"),
        "burndown_table": ("adg_burndown_table_", ".json"),
        "output_bundle": ("adg_run_output_bundle_", ".json"),
    }
    prefix, suffix = expected[key]
    name = path.name
    if not name.startswith(prefix) or not name.endswith(suffix):
        return False
    stamp = name[len(prefix) : -len(suffix)]
    if key in {"gate_results", "action_queue"}:
        return _is_gate_results_stamp(stamp) or _is_generator_run_stamp(stamp)
    return _is_generator_run_stamp(stamp)


def _artifact_ref(key: str, path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    return {
        "artifact_key": key,
        "path": str(resolved),
        "sha256": _sha256(resolved),
    }


def _load_handoff_contract() -> dict[str, Any]:
    if not HANDOFF_CONTRACT_PATH.is_file():
        return {}
    try:
        import tomllib  # noqa: PLC0415
    except ModuleNotFoundError:
        return {}
    try:
        payload = tomllib.loads(HANDOFF_CONTRACT_PATH.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    handoff = payload.get("handoff")
    return handoff if isinstance(handoff, dict) else {}


def _producer_artifacts_adg(producer_root: Path) -> Path:
    return producer_root / "artifacts" / "adg"


def _handoff_producer_artifacts_adg() -> Path:
    handoff = _load_handoff_contract()
    if handoff.get("handoff_pointer_base") != "producer_repo_root":
        return ARTIFACTS_ADG
    raw_root = handoff.get("producer_repo_root")
    if not isinstance(raw_root, str) or not raw_root.strip():
        return ARTIFACTS_ADG
    return _producer_artifacts_adg(Path(raw_root).resolve())


def _write_immutable_text(path: Path, text: str, *, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing != text:
            raise RuntimeError(f"immutable {label} already exists with different content: {path}")
        return
    path.write_text(text, encoding="utf-8")


def _copy_immutable_artifact(source: Path, destination: Path, *, key: str) -> Path:
    source_resolved = source.resolve()
    destination_resolved = destination.resolve()
    if source_resolved == destination_resolved:
        return source_resolved
    destination.parent.mkdir(parents=True, exist_ok=True)
    source_sha256 = _sha256(source_resolved)
    if destination.exists():
        if _sha256(destination) != source_sha256:
            raise RuntimeError(
                f"immutable {key} artifact already exists with different content: {destination}"
            )
        return destination_resolved
    shutil.copy2(source_resolved, destination)
    if _sha256(destination) != source_sha256:
        raise RuntimeError(f"copied {key} artifact sha256 mismatch: {destination}")
    return destination_resolved


def _published_generation_manifest_text(source: Path, destinations: dict[str, Path]) -> str | None:
    try:
        payload = _load_json(source)
    except (OSError, json.JSONDecodeError, TypeError):
        return None
    snapshot = destinations.get("snapshot")
    if snapshot is not None:
        if "sqlite_path" in payload or "snapshot_path" in payload:
            payload["sqlite_path"] = str(snapshot.resolve())
            payload["snapshot_path"] = str(snapshot.resolve())
    gate_manifest = destinations.get("gate_manifest")
    if gate_manifest is not None and "gate_manifest_path" in payload:
        payload["gate_manifest_path"] = str(gate_manifest.resolve())
    return json.dumps(payload, indent=2) + "\n"


def _transport_artifact_priority(path: Path) -> tuple[int, str]:
    """Order a bundle closure so referenced digests are resealed first."""
    name = path.name
    if path.suffix == ".sqlite":
        priority = 0
    elif name.startswith("adg_gate_results_"):
        priority = 10
    elif name.startswith("adg_burndown_table_"):
        priority = 20
    elif name.startswith("adg_gate_invocation_manifest_"):
        priority = 21
    elif name.startswith("adg_generation_manifest_"):
        priority = 22
    elif name.startswith("adg_action_queue_"):
        priority = 30
    elif name.startswith("adg_bcg_adapter_"):
        priority = 40
    elif name.startswith("adg_review_template_"):
        priority = 45
    elif name.startswith("adg_bcg_executive_summary_"):
        priority = 60
    elif name.startswith("adg_run_terminal_summary_"):
        priority = 70
    elif name.startswith("adg_output_publication_"):
        priority = 90
    else:
        # Optional P7 evidence and wrapper certification artifacts feed the
        # action/review/executive layers even though they are not mandatory
        # output gates.  Transport them before those consumers so any rebased
        # path changes are reflected in downstream digests.
        priority = 25
    return priority, str(path)


def _replace_transport_values(value: Any, replacements: dict[str, str]) -> Any:
    """Replace exact sealed paths/digests in a JSON-compatible value."""
    if isinstance(value, dict):
        return {key: _replace_transport_values(item, replacements) for key, item in value.items()}
    if isinstance(value, list):
        return [_replace_transport_values(item, replacements) for item in value]
    if isinstance(value, str):
        replaced = replacements.get(value)
        if replaced is not None:
            return replaced
        for old, new in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
            if old and old in value:
                value = value.replace(old, new)
        return value
    return value


def _transport_destination(
    source: Path,
    *,
    source_artifacts: Path,
    producer_artifacts: Path,
) -> Path:
    source = source.resolve()
    try:
        relative = source.relative_to(source_artifacts.resolve())
    except ValueError:
        relative = Path(source.name)
    destination = (producer_artifacts / relative).resolve()
    if not destination.is_relative_to(producer_artifacts.resolve()):
        raise RuntimeError(f"bundle artifact transport escaped producer root: {source}")
    return destination


def _transport_json_dependencies(source: Path) -> set[Path]:
    """Return digest/provenance inputs that a JSON artifact claims are present."""
    if source.suffix.lower() != ".json":
        return set()
    document = _load_json(source)
    dependencies: set[Path] = set()

    def add_declared(raw_path: Any, raw_digest: Any, *, label: str) -> None:
        if not isinstance(raw_path, str) or not raw_path:
            raise RuntimeError(f"{source.name} {label} path is missing")
        path = _abs(Path(raw_path)).resolve()
        if not path.is_file():
            raise RuntimeError(f"{source.name} {label} artifact is missing: {path}")
        if isinstance(raw_digest, str) and raw_digest and _sha256(path) != raw_digest:
            raise RuntimeError(f"{source.name} {label} digest mismatch: {path}")
        dependencies.add(path)

    provenance = document.get("provenance")
    if isinstance(provenance, dict):
        inputs = provenance.get("inputs")
        if isinstance(inputs, list):
            for row in inputs:
                if not isinstance(row, dict) or row.get("status") != "present":
                    continue
                add_declared(
                    row.get("path"),
                    row.get("digest_sha256"),
                    label=f"provenance input {row.get('artifact_key')!r}",
                )

    raw_inputs = document.get("raw_inputs")
    if isinstance(raw_inputs, dict):
        artifacts = raw_inputs.get("artifacts")
        loaded_status = raw_inputs.get("loaded_status")
        used = (
            loaded_status.get("used")
            if isinstance(loaded_status, dict) and isinstance(loaded_status.get("used"), list)
            else []
        )
        if isinstance(artifacts, dict):
            for key in used:
                if isinstance(key, str) and key in artifacts:
                    add_declared(artifacts[key], None, label=f"raw input {key!r}")

    usage = document.get("artifact_usage_matrix")
    rows = usage.get("rows") if isinstance(usage, dict) else None
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict) and row.get("exists") is True:
                add_declared(
                    row.get("path"),
                    None,
                    label=f"artifact usage {row.get('artifact_key')!r}",
                )
    return dependencies


def _transport_output_bundle_closure(
    *,
    source_bundle: Path,
    producer_artifacts: Path,
    handoff_sources: dict[str, Path],
) -> tuple[Path, dict[str, Path]]:
    """Copy and reseal one portable output-bundle closure for BCG handoff.

    The output bundle is a digest graph, not a loose group of files.  Moving
    only its top-level handoff references leaves gate provenance, action-queue
    provenance, publication receipts, and the inventory bound to the producer
    repository.  Transport the complete closure in dependency order and then
    render the bundle itself last.
    """
    source_bundle = source_bundle.resolve()
    source_artifacts = source_bundle.parent.resolve()
    producer_artifacts = producer_artifacts.resolve()
    payload = _load_json(source_bundle)
    if not isinstance(payload, dict):
        raise RuntimeError("output bundle root must be a JSON object")

    closure: set[Path] = {path.resolve() for path in handoff_sources.values() if path.is_file()}
    raw_inventory = payload.get("artifacts")
    if not isinstance(raw_inventory, list):
        raise RuntimeError("output bundle artifact inventory is missing")
    for row in raw_inventory:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("output bundle artifact inventory row is malformed")
        path = _abs(Path(row["path"])).resolve()
        if not path.is_file():
            raise RuntimeError(f"output bundle artifact missing during transport: {path}")
        closure.add(path)
    for field in (
        "snapshot_path",
        "gate_results_path",
        "enforcement_report_path",
        "terminal_summary_path",
    ):
        raw_path = payload.get(field)
        if isinstance(raw_path, str) and raw_path:
            path = _abs(Path(raw_path)).resolve()
            if not path.is_file():
                raise RuntimeError(f"output bundle {field} missing during transport: {path}")
            closure.add(path)
    for gate in payload.get("gates") or []:
        if not isinstance(gate, dict):
            raise RuntimeError("output bundle gate row is malformed")
        for raw_path in gate.get("paths") or []:
            if not isinstance(raw_path, str) or not raw_path:
                raise RuntimeError("output bundle gate path is malformed")
            path = _abs(Path(raw_path)).resolve()
            if not path.is_file():
                raise RuntimeError(f"output bundle gate artifact missing during transport: {path}")
            closure.add(path)
    closure.discard(source_bundle)

    # The report bundle deliberately inventories emitted reports, not every
    # optional P7 input consumed to build them.  Follow explicit present/used
    # provenance recursively so the transported BCG closure never points back
    # to a different checkout or to evidence that was not copied.
    inspected: set[Path] = set()
    while pending := sorted(closure - inspected):
        for source in pending:
            inspected.add(source)
            closure.update(_transport_json_dependencies(source))

    destinations: dict[Path, Path] = {}
    destination_owners: dict[Path, Path] = {}
    for source in closure:
        destination = _transport_destination(
            source,
            source_artifacts=source_artifacts,
            producer_artifacts=producer_artifacts,
        )
        owner = destination_owners.get(destination)
        if owner is not None and owner != source:
            raise RuntimeError(f"bundle artifact transport basename collision: {owner} and {source}")
        destination_owners[destination] = source
        destinations[source] = destination

    destination_bundle = _transport_destination(
        source_bundle,
        source_artifacts=source_artifacts,
        producer_artifacts=producer_artifacts,
    )
    replacements: dict[str, str] = {}
    for source, destination in destinations.items():
        replacements[str(source)] = str(destination)
        replacements[str(source.resolve())] = str(destination.resolve())

    for source in sorted(closure, key=_transport_artifact_priority):
        destination = destinations[source]
        old_digest = _sha256(source)
        if source.suffix.lower() == ".json":
            document = json.loads(source.read_text(encoding="utf-8"))
            document = _replace_transport_values(document, replacements)
            rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
            _write_immutable_text(destination, rendered, label=f"transported {source.name}")
        elif source.suffix.lower() in {".md", ".yaml", ".yml", ".txt"}:
            rendered = source.read_text(encoding="utf-8")
            for old, new in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
                if old:
                    rendered = rendered.replace(old, new)
            _write_immutable_text(destination, rendered, label=f"transported {source.name}")
        else:
            _copy_immutable_artifact(source, destination, key=source.name)
        new_digest = _sha256(destination)
        prior = replacements.get(old_digest)
        if prior is not None and prior != new_digest:
            raise RuntimeError(
                f"bundle artifact transport digest collision for {source}: {prior} != {new_digest}"
            )
        replacements[old_digest] = new_digest

    transported_payload = _replace_transport_values(payload, replacements)
    if not isinstance(transported_payload, dict):
        raise RuntimeError("transported output bundle root must be a JSON object")
    transported_payload["latest_promoted"] = False
    _write_immutable_text(
        destination_bundle,
        json.dumps(transported_payload, indent=2, sort_keys=True) + "\n",
        label="transported output bundle",
    )

    run_id = transported_payload.get("run_id")
    source_snapshot = _abs(Path(payload["snapshot_path"])).resolve()
    target_snapshot = destinations.get(source_snapshot)
    if not isinstance(run_id, str) or not run_id or target_snapshot is None:
        raise RuntimeError("transported output bundle is missing its run or snapshot binding")
    raw_enforcement = payload.get("enforcement_report_path")
    target_enforcement = (
        destinations.get(_abs(Path(raw_enforcement)).resolve())
        if isinstance(raw_enforcement, str) and raw_enforcement
        else None
    )
    from tools.reports.adg_run_output_bundle import (  # noqa: PLC0415
        validate_existing_adg_run_output_bundle,
    )

    valid, reason = validate_existing_adg_run_output_bundle(
        adg_artifacts_dir=producer_artifacts,
        run_id=run_id,
        sqlite_path=target_snapshot,
        enforcement_report_path=target_enforcement,
    )
    if not valid:
        raise RuntimeError(f"transported output bundle failed validation: {reason}")

    keyed_destinations: dict[str, Path] = {}
    for key, source in handoff_sources.items():
        resolved = source.resolve()
        keyed_destinations[key] = destination_bundle if resolved == source_bundle else destinations[resolved]
    return destination_bundle, keyed_destinations


def _copy_result_for_handoff_root(result: WrapperResult, *, producer_artifacts: Path) -> WrapperResult:
    current_artifacts = ARTIFACTS_ADG.resolve()
    if producer_artifacts.resolve() == current_artifacts:
        return result
    handoff = json.loads(json.dumps(result.repair_handoff or _default_incomplete_handoff()))
    artifacts = handoff.get("artifacts")
    if not isinstance(artifacts, dict):
        return replace(result, repair_handoff=handoff)
    sources: dict[str, Path] = {}
    destinations: dict[str, Path] = {}
    for key, ref in list(artifacts.items()):
        if not isinstance(ref, dict):
            continue
        raw_path = ref.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            continue
        source = Path(raw_path)
        if not source.is_file():
            continue
        sources[key] = source
        destinations[key] = producer_artifacts / source.name
    output_bundle = sources.get("output_bundle")
    if output_bundle is not None:
        _bundle, transported = _transport_output_bundle_closure(
            source_bundle=output_bundle,
            producer_artifacts=producer_artifacts,
            handoff_sources=sources,
        )
        for key, copied in transported.items():
            artifacts[key] = _artifact_ref(key, copied)
    else:
        for key, source in sources.items():
            destination = destinations[key]
            if key == "generation_manifest":
                manifest_text = _published_generation_manifest_text(source, destinations)
                if manifest_text is not None:
                    _write_immutable_text(destination, manifest_text, label="generation manifest artifact")
                    copied = destination.resolve()
                else:
                    copied = _copy_immutable_artifact(source, destination, key=key)
            else:
                copied = _copy_immutable_artifact(source, destination, key=key)
            artifacts[key] = _artifact_ref(key, copied)
    return replace(result, repair_handoff=handoff)


def _repair_handoff_counts() -> dict[str, int]:
    return {
        "open_blocker_fix_count": 0,
        "critical_open_blocker_fix_count": 0,
        "candidate_blocker_triage_count": 0,
        "critical_tracked_debt_count": 0,
        "high_open_blocker_fix_count": 0,
        "high_ratchet_regression_count": 0,
        "high_ratchet_floor_tracked_debt_count": 0,
    }


def _legacy_repair_handoff_counts(counts: dict[str, int]) -> dict[str, int]:
    return {
        "P0_FIX": int(counts.get("critical_open_blocker_fix_count", 0)),
        "P0_WAVE": int(counts.get("candidate_blocker_triage_count", 0)),
        "P0_TRACKED_BACKLOG": int(counts.get("critical_tracked_debt_count", 0)),
        "P1_FIX": int(counts.get("high_open_blocker_fix_count", 0)),
        "P1_RATCHET_REGRESSION": int(counts.get("high_ratchet_regression_count", 0)),
        "P1_RATCHET_FLOOR_BACKLOG": int(counts.get("high_ratchet_floor_tracked_debt_count", 0)),
    }


def _repair_count_mismatches(recorded_counts: dict[str, Any], computed_counts: dict[str, int]) -> list[str]:
    if any(key in recorded_counts for key in computed_counts):
        expected = computed_counts
    else:
        expected = _legacy_repair_handoff_counts(computed_counts)
    return [
        f"{key}: recorded={recorded_counts.get(key)!r} computed={value!r}"
        for key, value in expected.items()
        if recorded_counts.get(key) != value
    ]


def _stamp_from_artifact_name(path: Path | None, *, prefix: str, suffix: str) -> str | None:
    if path is None:
        return None
    name = path.name
    if not name.startswith(prefix) or not name.endswith(suffix):
        return None
    stamp = name[len(prefix) : -len(suffix)]
    return stamp if _is_generator_run_stamp(stamp) else None


def _derive_adg_run_stamp(
    generation_manifest: dict[str, Any],
    generation_manifest_path: Path | None,
    snapshot_path: Path | None,
) -> str | None:
    manifest_stamp = _stamp_from_artifact_name(
        generation_manifest_path,
        prefix="adg_generation_manifest_",
        suffix=".json",
    )
    if manifest_stamp:
        return manifest_stamp

    snapshot_stamp = _stamp_from_artifact_name(
        snapshot_path,
        prefix="adg_indexed_",
        suffix=".sqlite",
    )
    if snapshot_stamp:
        return snapshot_stamp

    for key in ("sqlite_path", "snapshot_path"):
        raw = generation_manifest.get(key)
        if isinstance(raw, str) and raw:
            snapshot_stamp = _stamp_from_artifact_name(
                Path(raw),
                prefix="adg_indexed_",
                suffix=".sqlite",
            )
            if snapshot_stamp:
                return snapshot_stamp

    return None


def _gate_results_matches_snapshot(data: dict[str, Any], snapshot_path: Path) -> bool:
    if _path_matches(data.get("snapshot_path"), snapshot_path):
        return True
    if isinstance(data.get("snapshot"), dict):
        snapshot = data["snapshot"]
        if _path_matches(snapshot.get("path") or snapshot.get("sqlite_path"), snapshot_path):
            return True
    snapshot_name = data.get("snapshot")
    if isinstance(snapshot_name, str) and snapshot_name == snapshot_path.name:
        return True
    return False


def _fresh_same_run_artifact(
    *,
    key: str,
    adg_run_id: str,
    since_wall_start: float,
) -> tuple[Path | None, str | None]:
    names = {
        "snapshot": f"adg_indexed_{adg_run_id}.sqlite",
        "burndown_report": f"adg_burndown_report_{adg_run_id}.md",
        "burndown_table": f"adg_burndown_table_{adg_run_id}.json",
    }
    path = ARTIFACTS_ADG / names[key]
    if not path.is_file():
        return None, f"{key} same-run artifact missing: {path}"
    if path.stat().st_mtime + 2 < since_wall_start:
        return None, f"{key} same-run artifact stale before audit start: {path}"
    if not _is_timestamped_artifact(path, key):
        return None, f"{key} same-run artifact is not timestamped: {path}"
    return path, None


def _recover_snapshot_from_run_stamp(
    *,
    snapshot_path: Path | None,
    adg_run_id: str | None,
    since_wall_start: float,
) -> tuple[Path | None, list[str]]:
    if snapshot_path is not None:
        return snapshot_path, []
    if not adg_run_id:
        return None, ["snapshot missing and adg_run_id unavailable for recovery"]
    recovered, error = _fresh_same_run_artifact(
        key="snapshot",
        adg_run_id=adg_run_id,
        since_wall_start=since_wall_start,
    )
    return recovered, ([] if error is None else [error])


def _find_recent_sqlite_run_stamp(*, since_wall_start: float) -> str | None:
    """Recover a run id from a same-wrapper SQLite when manifests are missing."""
    candidates = sorted(
        ARTIFACTS_ADG.glob("adg_indexed_*.sqlite"),
        key=lambda p: p.stat().st_mtime,
    )
    for candidate in reversed(candidates):
        if candidate.stat().st_mtime + 2 < since_wall_start:
            continue
        stamp = _stamp_from_artifact_name(
            candidate,
            prefix="adg_indexed_",
            suffix=".sqlite",
        )
        if stamp:
            return stamp
    return None


def _run_retention_sweep(
    adg_run_id: str | None,
    *,
    adg_dir: Path | None = None,
) -> None:
    """Best-effort ADG artifact cleanup shared by scheduled wrapper runs."""
    if not adg_run_id:
        print("[audit] retention skipped: no ADG run id available")
        return
    try:
        from tools.adg.shared_modules.snapshot_registry import (  # noqa: PLC0415
            protected_snapshot_run_ids,
        )
        from tools.generate.archiving import _archive_old_artifacts  # noqa: PLC0415

        target_dir = (adg_dir or ARTIFACTS_ADG).resolve()
        _archive_old_artifacts(
            target_dir,
            adg_run_id,
            keep_runs=1,
            protected_run_ids=protected_snapshot_run_ids(target_dir),
        )
        print(f"[audit] retention sweep complete: current_ts={adg_run_id}")
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        print(f"[audit] retention sweep failed: {exc}", file=sys.stderr)


def _find_gate_results_for_snapshot(
    snapshot_path: Path,
    *,
    since_wall_start: float,
) -> tuple[Path | None, list[str]]:
    reasons: list[str] = []
    candidates = sorted(
        ARTIFACTS_ADG.glob("adg_gate_results_*.json"),
        key=lambda p: p.stat().st_mtime,
    )
    matches: list[Path] = []
    for candidate in candidates:
        if not _is_timestamped_artifact(candidate, "gate_results"):
            reasons.append(f"gate_results latest-only or untimestamped: {candidate}")
            continue
        if candidate.stat().st_mtime + 2 < since_wall_start:
            continue
        try:
            data = _load_json(candidate)
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            reasons.append(f"gate_results malformed: {candidate}: {exc}")
            continue
        if _gate_results_matches_snapshot(data, snapshot_path):
            matches.append(candidate)
    if matches:
        return matches[-1], []
    return None, reasons or [f"no timestamped gate_results for snapshot: {snapshot_path}"]


def _materialize_timestamped_copy(
    *,
    key: str,
    source: Path,
    adg_run_id: str,
    since_wall_start: float,
) -> tuple[Path | None, str | None]:
    if not source.is_file():
        return None, f"{key} source missing: {source}"
    if source.stat().st_mtime + 2 < since_wall_start:
        return None, f"{key} source stale before audit start: {source}"
    suffix = source.suffix
    out = ARTIFACTS_ADG / f"adg_{key}_{adg_run_id}{suffix}"
    out.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != out.resolve():
        shutil.copyfile(source, out)
    return out, None


def _resolve_burndown_for_handoff(
    *,
    key: str,
    source: Path,
    adg_run_id: str,
    since_wall_start: float,
) -> tuple[Path | None, str | None]:
    same_run, same_run_error = _fresh_same_run_artifact(
        key=key,
        adg_run_id=adg_run_id,
        since_wall_start=since_wall_start,
    )
    if same_run is not None:
        return same_run, None
    materialized, materialize_error = _materialize_timestamped_copy(
        key=key,
        source=source,
        adg_run_id=adg_run_id,
        since_wall_start=since_wall_start,
    )
    if materialized is not None:
        return materialized, None
    return None, materialize_error or same_run_error


def _degraded_output_reasons(
    *,
    generator_exit_code: int | None,
    missing: list[str],
) -> list[str]:
    reasons = ["mandatory-output recovery ran before dispatcher completion"]
    if generator_exit_code is not None:
        reasons.append(f"generator exit_code={generator_exit_code}")
    reasons.extend(f"{item} was absent for this ADG run" for item in missing)
    return reasons


def _write_degraded_gate_results(
    *,
    snapshot_path: Path,
    adg_run_id: str,
    generator_exit_code: int | None,
    missing: list[str],
) -> Path:
    out = ARTIFACTS_ADG / f"adg_gate_results_{adg_run_id}.json"
    reasons = _degraded_output_reasons(generator_exit_code=generator_exit_code, missing=missing)
    payload = {
        "schema_version": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "snapshot": snapshot_path.name,
        "snapshot_path": str(snapshot_path),
        "snapshot_sha256": _sha256(snapshot_path),
        "overall_exit_code": 1,
        "total_gates": 0,
        "gates": [],
        "degraded": True,
        "synthetic": True,
        "fallback_status": "degraded_pre_dispatch_fallback",
        "degradation_reasons": reasons,
        "summary": {
            "classification": "blocked",
            "reason": "dispatcher gate results were not emitted before generator failure",
        },
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def _empty_burndown_band(label: str) -> dict[str, Any]:
    return {
        "label": label,
        "gross": 0,
        "guardian": 0,
        "net": 0,
        "diff": 0,
        "status": "degraded_unavailable",
    }


def _write_degraded_burndown_table(
    *,
    snapshot_path: Path,
    adg_run_id: str,
    generator_exit_code: int | None,
    missing: list[str],
) -> Path:
    reasons = _degraded_output_reasons(generator_exit_code=generator_exit_code, missing=missing)
    summary = {
        "P0": _empty_burndown_band("Foundation Blockers"),
        "P1": _empty_burndown_band("Ratchet / Regression Guards"),
        "P2": _empty_burndown_band("Warning / Strategic Gaps"),
        "P3": _empty_burndown_band("Hygiene / Advisory"),
    }
    payload = {
        "schema_version": "2.2",
        "status": "degraded",
        "degraded": True,
        "synthetic": True,
        "fallback_status": "degraded_pre_dispatch_fallback",
        "summary": summary,
        "bands": summary,
        "p0_clean": False,
        "p1_no_ratchet": False,
        "provenance": {
            "generator_module": "tools.adg.run_full_adg_audit",
            "counting_mode": "degraded_pre_dispatch_fallback",
            "sqlite_source_path": str(snapshot_path),
            "sqlite_source_sha256": _sha256(snapshot_path),
            "degradation_reasons": reasons,
        },
    }
    timestamped = ARTIFACTS_ADG / f"adg_burndown_table_{adg_run_id}.json"
    timestamped.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    timestamped.write_text(rendered, encoding="utf-8")
    return timestamped


def _json_has_degraded_fallback_marker(path: Path) -> bool:
    if path.suffix.lower() != ".json":
        return False
    try:
        data = _load_json(path)
    except (OSError, json.JSONDecodeError, TypeError):
        return False
    provenance = data.get("provenance") if isinstance(data.get("provenance"), dict) else {}
    return any(
        (
            data.get("synthetic") is True,
            data.get("fallback_status") == "degraded_pre_dispatch_fallback",
            provenance.get("counting_mode") == "degraded_pre_dispatch_fallback",
        )
    )


def _optional_run_artifact(adg_run_id: str, name: str) -> Path | None:
    path = ARTIFACTS_ADG / name.format(ts=adg_run_id)
    return path if path.is_file() else None


def _bundle_matches_certification_gates(
    manifest_path: Path,
    certification_gates: list[Any],
) -> bool:
    """Require an existing seal to contain these exact wrapper-owned gates."""
    try:
        manifest = _load_json(manifest_path)
    except (OSError, json.JSONDecodeError, TypeError):
        return False
    rows = manifest.get("gates")
    if not isinstance(rows, list):
        return False
    by_key = {
        row.get("key"): row for row in rows if isinstance(row, dict) and isinstance(row.get("key"), str)
    }
    for expected in certification_gates:
        actual = by_key.get(expected.key)
        if not isinstance(actual, dict):
            return False
        if (
            actual.get("required") is not expected.required
            or actual.get("status") != expected.status
            or actual.get("producer_exit_code") != expected.producer_exit_code
        ):
            return False
        actual_paths = actual.get("paths")
        if not isinstance(actual_paths, list):
            return False
        if {str(_abs(Path(path)).resolve()) for path in actual_paths} != {
            str(_abs(Path(path)).resolve()) for path in expected.paths
        }:
            return False
    return True


def _emit_mandatory_run_outputs(
    *,
    snapshot_path: Path | None,
    adg_run_id: str | None,
    since_wall_start: float,
    generator_exit_code: int | None,
    enforcement_report_path: Path | None,
    certification_gates: list[Any],
) -> tuple[list[str], object | None, Path | None]:
    if snapshot_path is None or not snapshot_path.is_file():
        return ["mandatory ADG outputs not emitted because same-run snapshot is unavailable"], None, None
    if not adg_run_id:
        return ["mandatory ADG outputs not emitted because adg_run_id is unavailable"], None, None

    from tools.reports.adg_run_output_bundle import (  # noqa: PLC0415
        emit_adg_run_output_bundle,
        validate_existing_adg_run_output_bundle,
    )

    existing_valid, _existing_reason = validate_existing_adg_run_output_bundle(
        adg_artifacts_dir=ARTIFACTS_ADG,
        run_id=adg_run_id,
        sqlite_path=snapshot_path,
        enforcement_report_path=enforcement_report_path,
    )
    if existing_valid:
        existing_valid = _bundle_matches_certification_gates(
            ARTIFACTS_ADG / f"adg_run_output_bundle_{adg_run_id}.json",
            certification_gates,
        )
    if existing_valid:
        from tools.reports.adg_run_output_bundle import load_existing_adg_run_output_bundle  # noqa: PLC0415

        loaded_bundle = load_existing_adg_run_output_bundle(
            adg_artifacts_dir=ARTIFACTS_ADG,
            run_id=adg_run_id,
            sqlite_path=snapshot_path,
        )
        bundle_manifest = _load_json(loaded_bundle.manifest_path)
        gate_raw = bundle_manifest.get("gate_results_path")
        return [], loaded_bundle, Path(gate_raw) if gate_raw else None

    errors: list[str] = []
    missing: list[str] = []
    gate_results_path, _gate_errors = _find_gate_results_for_snapshot(
        snapshot_path,
        since_wall_start=since_wall_start,
    )
    if gate_results_path is None:
        missing.append("gate_results")
        gate_results_path = _write_degraded_gate_results(
            snapshot_path=snapshot_path,
            adg_run_id=adg_run_id,
            generator_exit_code=generator_exit_code,
            missing=missing,
        )

    burndown_table_path, _burndown_error = _resolve_burndown_for_handoff(
        key="burndown_table",
        source=ARTIFACTS_ADG / "adg_burndown_table.json",
        adg_run_id=adg_run_id,
        since_wall_start=since_wall_start,
    )
    if burndown_table_path is None:
        missing.append("burndown_table")
        burndown_table_path = _write_degraded_burndown_table(
            snapshot_path=snapshot_path,
            adg_run_id=adg_run_id,
            generator_exit_code=generator_exit_code,
            missing=missing,
        )

    bundle = emit_adg_run_output_bundle(
        adg_artifacts_dir=ARTIFACTS_ADG,
        run_id=adg_run_id,
        sqlite_path=snapshot_path,
        gate_results_path=gate_results_path,
        burndown_path=burndown_table_path,
        enforcement_report_path=enforcement_report_path,
        certification_gates=certification_gates,
        print_terminal=False,
        repo_root=REPO_ROOT,
    )
    if bundle.required_exit_code != 0:
        errors.append(f"ADG output bundle status={bundle.status}")
    return errors, bundle, gate_results_path


def _ensure_action_queue_for_handoff(
    *,
    gate_results_path: Path,
    burndown_table_path: Path,
    snapshot_path: Path,
    adg_run_id: str,
) -> tuple[Path | None, list[str]]:
    try:
        from tools.reports.adg_action_queue import (  # noqa: PLC0415
            emit_adg_action_queue,
            validate_action_queue,
        )
    except ImportError as exc:
        return None, [f"action_queue module unavailable: {exc}"]

    output_path = ARTIFACTS_ADG / f"adg_action_queue_{adg_run_id}.json"
    path: Path | None = output_path if output_path.is_file() else None
    if path is None:
        rc, path = emit_adg_action_queue(
            gate_results=gate_results_path,
            burndown=burndown_table_path,
            sqlite_snapshot=snapshot_path,
            output_path=output_path,
            ts=adg_run_id,
            fail_closed=True,
            allow_latest_fallback=False,
            repo_root=REPO_ROOT,
        )
        if rc != 0 or path is None or not path.is_file():
            return None, [f"action_queue emit failed exit_code={rc}"]
    try:
        doc = _load_json(path)
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        return path, [f"action_queue malformed: {exc}"]
    errors = validate_action_queue(doc)
    return path, [f"action_queue validation: {err}" for err in errors]


def _open_blocker_fix_count(action_queue: dict[str, Any]) -> int:
    count = 0
    for action in action_queue.get("actions") or []:
        if action.get("verdict_cluster") == "FIX" or action.get("work_priority") == "P0":
            count += 1
    return count


def _repair_counts(action_queue: dict[str, Any], gate_results: dict[str, Any]) -> dict[str, int]:
    from tools.reports.gate_signal_catalog import display_verdict, display_verdict_sub  # noqa: PLC0415

    counts = _repair_handoff_counts()
    for action in action_queue.get("actions") or []:
        cluster = action.get("verdict_cluster")
        if cluster in {"CANDIDATE_BLOCKER_TRIAGE", "P0_WAVE"} and action.get("sort_band") == "P0":
            counts["candidate_blocker_triage_count"] += 1
            continue
        if cluster != "FIX":
            continue
        counts["open_blocker_fix_count"] += 1
        if action.get("sort_band") == "P0":
            counts["critical_open_blocker_fix_count"] += 1
        elif action.get("sort_band") == "P1":
            counts["high_open_blocker_fix_count"] += 1
    for gate in gate_results.get("gates") or []:
        if gate.get("band") == "P0" and display_verdict(gate) == "TRACK":
            counts["critical_tracked_debt_count"] += 1
        if gate.get("band") != "P1" or gate.get("enforcement") != "ratchet":
            continue
        sub = display_verdict_sub(gate)
        if sub == "regr":
            counts["high_ratchet_regression_count"] += 1
        elif sub == "floor":
            counts["high_ratchet_floor_tracked_debt_count"] += 1
    return counts


def _build_repair_handoff(
    *,
    generation_manifest_path: Path | None,
    gate_manifest_path: Path | None,
    generation_manifest: dict[str, Any],
    certification_status: str,
    since_wall_start: float,
    allow_unfinalized_output_bundle: bool = False,
) -> tuple[str, dict[str, Any], list[str]]:
    errors: list[str] = []
    artifacts: dict[str, dict[str, Any]] = {}

    snapshot_raw = generation_manifest.get("sqlite_path") or generation_manifest.get("snapshot_path")
    snapshot_path = _abs(Path(snapshot_raw)) if snapshot_raw else None
    adg_run_id = _derive_adg_run_stamp(generation_manifest, generation_manifest_path, snapshot_path)
    if not adg_run_id:
        errors.append("adg_run_id could not be derived from timestamped manifest or snapshot")
    snapshot_path, snapshot_recovery_errors = _recover_snapshot_from_run_stamp(
        snapshot_path=snapshot_path,
        adg_run_id=adg_run_id,
        since_wall_start=since_wall_start,
    )
    errors.extend(snapshot_recovery_errors)

    required_paths: dict[str, Path | None] = {
        "generation_manifest": generation_manifest_path,
        "gate_manifest": gate_manifest_path,
        "snapshot": snapshot_path,
    }
    for key, path in list(required_paths.items()):
        if path is None:
            errors.append(f"{key} missing")
            continue
        if not path.is_file():
            errors.append(f"{key} path missing: {path}")
            continue
        if not _is_timestamped_artifact(path, key):
            errors.append(f"{key} is not a timestamped artifact: {path}")

    if adg_run_id and generation_manifest_path and generation_manifest_path.is_file():
        gen_stamp = _stamp_from_artifact_name(
            generation_manifest_path,
            prefix="adg_generation_manifest_",
            suffix=".json",
        )
        if gen_stamp != adg_run_id:
            errors.append("generation_manifest timestamp differs from adg_run_id")
    if adg_run_id and gate_manifest_path and gate_manifest_path.is_file():
        gate_stamp = _stamp_from_artifact_name(
            gate_manifest_path,
            prefix="adg_gate_invocation_manifest_",
            suffix=".json",
        )
        if gate_stamp != adg_run_id:
            errors.append("gate_manifest timestamp differs from adg_run_id")

    gate_results_path: Path | None = None
    if snapshot_path and snapshot_path.is_file():
        gate_results_path, gate_result_errors = _find_gate_results_for_snapshot(
            snapshot_path,
            since_wall_start=since_wall_start,
        )
        errors.extend(gate_result_errors)
    required_paths["gate_results"] = gate_results_path

    burndown_table_path: Path | None = None
    burndown_report_path: Path | None = None
    if adg_run_id:
        burndown_table_path, err = _resolve_burndown_for_handoff(
            key="burndown_table",
            source=ARTIFACTS_ADG / "adg_burndown_table.json",
            adg_run_id=adg_run_id,
            since_wall_start=since_wall_start,
        )
        if err:
            errors.append(err)
        burndown_report_path, err = _resolve_burndown_for_handoff(
            key="burndown_report",
            source=ARTIFACTS_ADG / "adg_burndown_report.md",
            adg_run_id=adg_run_id,
            since_wall_start=since_wall_start,
        )
        if err:
            errors.append(err)
    required_paths["burndown_table"] = burndown_table_path
    required_paths["burndown_report"] = burndown_report_path

    action_queue_path: Path | None = None
    if gate_results_path and burndown_table_path and snapshot_path and adg_run_id:
        action_queue_path, queue_errors = _ensure_action_queue_for_handoff(
            gate_results_path=gate_results_path,
            burndown_table_path=burndown_table_path,
            snapshot_path=snapshot_path,
            adg_run_id=adg_run_id,
        )
        errors.extend(queue_errors)
    else:
        errors.append("action_queue not emitted because prerequisite artifacts are incomplete")
    required_paths["action_queue"] = action_queue_path
    required_paths["output_bundle"] = (
        ARTIFACTS_ADG / f"adg_run_output_bundle_{adg_run_id}.json" if adg_run_id else None
    )

    for key in REPAIR_ARTIFACT_KEYS:
        path = required_paths.get(key)
        if path is None or not path.is_file():
            errors.append(f"{key} missing from repair_handoff")
            continue
        if not _is_timestamped_artifact(path, key):
            errors.append(f"{key} latest-only or untimestamped path rejected: {path}")
            continue
        if key in {"gate_results", "burndown_table"} and _json_has_degraded_fallback_marker(path):
            errors.append(f"{key} is degraded pre-dispatch fallback and not downstream-consumable: {path}")
        if key == "output_bundle":
            try:
                bundle = _load_json(path)
                if bundle.get("status") != "complete":
                    errors.append(f"output_bundle status={bundle.get('status')!r}")
                if bundle.get("run_id") != adg_run_id:
                    errors.append("output_bundle run_id mismatch")
                if snapshot_path is None or bundle.get("snapshot_sha256") != _sha256(snapshot_path):
                    errors.append("output_bundle snapshot digest mismatch")
                if snapshot_path is None or not _path_matches(bundle.get("snapshot_path"), snapshot_path):
                    errors.append("output_bundle snapshot path mismatch")
                final_exit_code = bundle.get("final_exit_code")
                bundle_is_finalized = isinstance(final_exit_code, int) and not isinstance(
                    final_exit_code,
                    bool,
                )
                if not bundle_is_finalized and not allow_unfinalized_output_bundle:
                    errors.append("output_bundle terminal finalization missing")
                inventory = bundle.get("artifacts")
                action_row = (
                    next(
                        (
                            row
                            for row in inventory or []
                            if isinstance(row, dict) and _path_matches(row.get("path"), action_queue_path)
                        ),
                        None,
                    )
                    if action_queue_path is not None
                    else None
                )
                if action_queue_path is None or not isinstance(action_row, dict):
                    errors.append("output_bundle does not inventory the handoff action_queue")
                elif action_row.get("sha256") != _sha256(action_queue_path):
                    errors.append("output_bundle action_queue digest mismatch")
                if gate_results_path is None or not _path_matches(
                    bundle.get("gate_results_path"), gate_results_path
                ):
                    errors.append("output_bundle gate_results path mismatch")
                elif bundle.get("gate_results_sha256") != _sha256(gate_results_path):
                    errors.append("output_bundle gate_results digest mismatch")
                if (
                    snapshot_path is not None
                    and adg_run_id is not None
                    and (bundle_is_finalized or not allow_unfinalized_output_bundle)
                ):
                    from tools.reports.adg_run_output_bundle import (  # noqa: PLC0415
                        validate_existing_adg_run_output_bundle,
                    )

                    bundle_valid, bundle_reason = validate_existing_adg_run_output_bundle(
                        adg_artifacts_dir=path.parent,
                        run_id=adg_run_id,
                        sqlite_path=snapshot_path,
                    )
                    if not bundle_valid:
                        errors.append(f"output_bundle validation failed: {bundle_reason}")
            except (OSError, json.JSONDecodeError, TypeError) as exc:
                errors.append(f"output_bundle malformed: {exc}")
        artifacts[key] = _artifact_ref(key, path)

    counts = _repair_handoff_counts()
    artifact_status = "incomplete"
    if action_queue_path and gate_results_path:
        try:
            action_queue = _load_json(action_queue_path)
            gate_results = _load_json(gate_results_path)
            counts = _repair_counts(action_queue, gate_results)
            if not errors and certification_status == "clean" and _open_blocker_fix_count(action_queue) == 0:
                artifact_status = "certified"
            elif not errors:
                artifact_status = "repair_ready"
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            errors.append(f"handoff artifact malformed during count: {exc}")

    if errors:
        artifact_status = "incomplete"

    handoff = {
        "status": artifact_status,
        "artifacts": artifacts,
        "counts": counts,
        "legacy_counts": _legacy_repair_handoff_counts(counts),
        "validation_errors": sorted(set(errors)),
    }
    return artifact_status, handoff, errors


def _artifact_generator_run_stamp(path: Path, key: str) -> str | None:
    expected = {
        "snapshot": ("adg_indexed_", ".sqlite"),
        "generation_manifest": ("adg_generation_manifest_", ".json"),
        "gate_manifest": ("adg_gate_invocation_manifest_", ".json"),
        "action_queue": ("adg_action_queue_", ".json"),
        "burndown_report": ("adg_burndown_report_", ".md"),
        "burndown_table": ("adg_burndown_table_", ".json"),
        "output_bundle": ("adg_run_output_bundle_", ".json"),
    }
    if key not in expected:
        return None
    prefix, suffix = expected[key]
    return _stamp_from_artifact_name(path, prefix=prefix, suffix=suffix)


def validate_repair_handoff_receipt(
    receipt_path: Path = RECEIPT_PATH,
    *,
    expected_adg_run_id: str | None = None,
    expected_receipt_sha256: str | None = None,
) -> tuple[dict[str, Any] | None, dict[str, int], list[str]]:
    errors: list[str] = []
    counts = _repair_handoff_counts()
    try:
        receipt = _load_json(receipt_path)
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        return None, counts, [f"receipt unreadable or malformed: {exc}"]

    if expected_receipt_sha256 and _sha256(receipt_path) != expected_receipt_sha256:
        errors.append("receipt sha256 mismatch with handoff pointer")
    if receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION:
        errors.append("unsupported or missing schema_version")
    if receipt.get("artifact_status") not in {"certified", "repair_ready"}:
        errors.append(f"artifact_status not consumable: {receipt.get('artifact_status')!r}")
    if receipt.get("artifact_status_source") != "direct":
        errors.append("artifact_status_source must be direct")
    run_state = receipt.get("run_state")
    if not isinstance(run_state, dict):
        errors.append("run_state missing or malformed")
        receipt_process_exit: int | None = None
    else:
        raw_process_exit = run_state.get("process_exit_code")
        receipt_process_exit = (
            raw_process_exit
            if isinstance(raw_process_exit, int) and not isinstance(raw_process_exit, bool)
            else None
        )
        if receipt_process_exit is None:
            errors.append("run_state.process_exit_code missing or malformed")
    if receipt.get("artifact_status") == "certified" and receipt_process_exit != 0:
        errors.append("certified receipt requires process_exit_code=0")
    receipt_run_id = receipt.get("adg_run_id")
    if expected_adg_run_id and receipt_run_id != expected_adg_run_id:
        errors.append(
            f"receipt adg_run_id {receipt_run_id!r} does not match expected {expected_adg_run_id!r}"
        )
    artifact_run_id = expected_adg_run_id or (receipt_run_id if isinstance(receipt_run_id, str) else None)

    handoff = receipt.get("repair_handoff")
    if not isinstance(handoff, dict):
        errors.append("repair_handoff missing or malformed")
        return receipt, counts, errors
    artifacts = handoff.get("artifacts")
    if not isinstance(artifacts, dict):
        errors.append("repair_handoff.artifacts missing or malformed")
        return receipt, counts, errors

    resolved: dict[str, Path] = {}
    for key in REPAIR_ARTIFACT_KEYS:
        item = artifacts.get(key)
        if not isinstance(item, dict):
            errors.append(f"{key} artifact ref missing")
            continue
        raw_path = item.get("path")
        raw_digest = item.get("sha256")
        if not isinstance(raw_path, str) or not raw_path:
            errors.append(f"{key} path missing")
            continue
        path = _abs(Path(raw_path))
        resolved[key] = path
        if not path.is_file():
            errors.append(f"{key} path does not exist: {path}")
            continue
        if not _is_timestamped_artifact(path, key):
            errors.append(f"{key} latest-only or untimestamped path rejected: {path}")
        stamp = _artifact_generator_run_stamp(path, key)
        if artifact_run_id and stamp and stamp != artifact_run_id:
            errors.append(f"{key} run stamp {stamp!r} does not match receipt adg_run_id {artifact_run_id!r}")
        if not isinstance(raw_digest, str) or len(raw_digest) != 64:
            errors.append(f"{key} sha256 missing or malformed")
            continue
        if _sha256(path) != raw_digest:
            errors.append(f"{key} sha256 mismatch")

    counts_recomputed = False
    if all(
        key in resolved and resolved[key].is_file() for key in ("output_bundle", "snapshot", "gate_results")
    ):
        try:
            bundle = _load_json(resolved["output_bundle"])
            from tools.reports.adg_run_output_bundle import (  # noqa: PLC0415
                validate_existing_adg_run_output_bundle,
            )

            bundle_valid, bundle_reason = validate_existing_adg_run_output_bundle(
                adg_artifacts_dir=resolved["output_bundle"].parent,
                run_id=artifact_run_id or "",
                sqlite_path=resolved["snapshot"],
            )
            if not bundle_valid:
                errors.append(f"output_bundle validation failed: {bundle_reason}")
            bundle_exit = bundle.get("final_exit_code")
            if not isinstance(bundle_exit, int) or isinstance(bundle_exit, bool):
                errors.append("output_bundle final_exit_code missing or malformed")
            elif receipt_process_exit != bundle_exit:
                errors.append("receipt process_exit_code differs from output_bundle final_exit_code")
            if not _path_matches(bundle.get("gate_results_path"), resolved["gate_results"]):
                errors.append("output_bundle gate_results path differs from repair_handoff")
            elif bundle.get("gate_results_sha256") != _sha256(resolved["gate_results"]):
                errors.append("output_bundle gate_results digest differs from repair_handoff")
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            errors.append(f"output_bundle malformed: {exc}")

    if all(key in resolved and resolved[key].is_file() for key in ("gate_results", "action_queue")):
        try:
            gate_results = _load_json(resolved["gate_results"])
            action_queue = _load_json(resolved["action_queue"])
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            errors.append(f"handoff JSON artifact malformed: {exc}")
        else:
            try:
                from tools.reports.adg_action_queue import validate_action_queue  # noqa: PLC0415

                errors.extend(
                    f"action_queue validation: {err}" for err in validate_action_queue(action_queue)
                )
            except ImportError as exc:
                errors.append(f"action_queue validator unavailable: {exc}")
            gate_digest = artifacts.get("gate_results", {}).get("sha256")
            for item in action_queue.get("provenance", {}).get("inputs") or []:
                if item.get("artifact_key") == "gate_results":
                    if item.get("digest_sha256") != gate_digest:
                        errors.append("action_queue provenance gate_results digest mismatch")
                    break
            else:
                errors.append("action_queue missing gate_results provenance")
            if "snapshot" in resolved and not _gate_results_matches_snapshot(
                gate_results, resolved["snapshot"]
            ):
                errors.append("gate_results snapshot does not match handoff snapshot")
            counts = _repair_counts(action_queue, gate_results)
            counts_recomputed = True

    recorded_counts = handoff.get("counts")
    if not isinstance(recorded_counts, dict):
        errors.append("repair_handoff.counts missing or malformed")
    elif counts_recomputed:
        mismatches = _repair_count_mismatches(recorded_counts, counts)
        if mismatches:
            errors.append(
                "repair_handoff counts differ from digest-bound artifacts: " + "; ".join(mismatches)
            )

    generation_path = resolved.get("generation_manifest")
    gate_manifest_path = resolved.get("gate_manifest")
    snapshot_path = resolved.get("snapshot")
    if generation_path and generation_path.is_file():
        try:
            generation_manifest = _load_json(generation_path)
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            errors.append(f"generation_manifest malformed: {exc}")
        else:
            manifest_snapshot_declared = bool(
                generation_manifest.get("sqlite_path") or generation_manifest.get("snapshot_path")
            )
            if snapshot_path and manifest_snapshot_declared:
                if not (
                    _path_matches(generation_manifest.get("sqlite_path"), snapshot_path)
                    or _path_matches(generation_manifest.get("snapshot_path"), snapshot_path)
                ):
                    errors.append("generation_manifest snapshot path differs from repair_handoff")
            elif snapshot_path and not manifest_snapshot_declared:
                manifest_stamp = _stamp_from_artifact_name(
                    generation_path,
                    prefix="adg_generation_manifest_",
                    suffix=".json",
                )
                snapshot_stamp = _stamp_from_artifact_name(
                    snapshot_path,
                    prefix="adg_indexed_",
                    suffix=".sqlite",
                )
                if manifest_stamp != snapshot_stamp:
                    errors.append(
                        "generation_manifest missing snapshot path and run stamp differs from repair_handoff"
                    )
            if gate_manifest_path and not _path_matches(
                generation_manifest.get("gate_manifest_path"),
                gate_manifest_path,
            ):
                errors.append("generation_manifest gate_manifest_path differs from repair_handoff")

    if handoff.get("validation_errors"):
        errors.append("producer recorded repair_handoff validation_errors")
    return receipt, counts, sorted(set(errors))


def _resolve_handoff_pointer(pointer_path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    try:
        pointer = _load_json(pointer_path)
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        return None, [f"handoff pointer unreadable or malformed: {exc}"]

    schema = pointer.get("schema_version")
    if schema == REPAIR_HANDOFF_SCHEMA_VERSION:
        return pointer, []
    if schema != REPAIR_HANDOFF_POINTER_SCHEMA_VERSION:
        return None, [f"unsupported handoff pointer schema_version: {schema!r}"]

    raw_path = pointer.get("handoff_path")
    raw_digest = pointer.get("handoff_sha256")
    if not isinstance(raw_path, str) or not raw_path:
        return None, ["handoff_path missing"]
    handoff_path = _abs(Path(raw_path))
    if not handoff_path.is_file():
        return None, [f"handoff_path does not exist: {handoff_path}"]
    if not isinstance(raw_digest, str) or len(raw_digest) != 64:
        errors.append("handoff_sha256 missing or malformed")
    elif _sha256(handoff_path) != raw_digest:
        errors.append("handoff sha256 mismatch")
    try:
        handoff_doc = _load_json(handoff_path)
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        errors.append(f"handoff document unreadable or malformed: {exc}")
        return None, errors
    if handoff_doc.get("schema_version") != REPAIR_HANDOFF_SCHEMA_VERSION:
        errors.append("handoff document schema_version mismatch")
    if pointer.get("adg_run_id") != handoff_doc.get("adg_run_id"):
        errors.append("latest pointer adg_run_id differs from immutable handoff")
    return handoff_doc, errors


def validate_repair_handoff_pointer(
    pointer_path: Path,
    *,
    expected_adg_run_id: str | None = None,
) -> tuple[dict[str, Any] | None, dict[str, int], list[str]]:
    handoff_doc, errors = _resolve_handoff_pointer(pointer_path)
    counts = _repair_handoff_counts()
    if handoff_doc is None:
        return None, counts, sorted(set(errors))

    handoff_run_id = handoff_doc.get("adg_run_id")
    if expected_adg_run_id and handoff_run_id != expected_adg_run_id:
        errors.append(
            f"handoff adg_run_id {handoff_run_id!r} does not match expected {expected_adg_run_id!r}"
        )
    if handoff_doc.get("downstream_release_status") != "released":
        errors.append(
            f"downstream_release_status not released: {handoff_doc.get('downstream_release_status')!r}"
        )

    receipt_ref = handoff_doc.get("receipt")
    if not isinstance(receipt_ref, dict):
        errors.append("handoff receipt ref missing or malformed")
        return handoff_doc, counts, sorted(set(errors))
    raw_receipt_path = receipt_ref.get("path")
    raw_receipt_digest = receipt_ref.get("sha256")
    if not isinstance(raw_receipt_path, str) or not raw_receipt_path:
        errors.append("handoff receipt path missing")
        return handoff_doc, counts, sorted(set(errors))
    if not isinstance(raw_receipt_digest, str) or len(raw_receipt_digest) != 64:
        errors.append("handoff receipt sha256 missing or malformed")
        raw_receipt_digest = None

    receipt, counts, receipt_errors = validate_repair_handoff_receipt(
        _abs(Path(raw_receipt_path)),
        expected_adg_run_id=expected_adg_run_id
        or (handoff_run_id if isinstance(handoff_run_id, str) else None),
        expected_receipt_sha256=raw_receipt_digest,
    )
    errors.extend(receipt_errors)
    if receipt and receipt.get("repair_handoff") != handoff_doc.get("repair_handoff"):
        errors.append("receipt repair_handoff differs from immutable handoff")
    return receipt, counts, sorted(set(errors))


def _validated_producer_prior_snapshot(artifacts_adg: Path) -> Path | None:
    """Return the latest direct, digest-bound producer snapshot when valid."""
    pointer = artifacts_adg / "handoffs" / "adg_repair_handoff_latest.json"
    if not pointer.is_file():
        return None
    receipt, _counts, errors = validate_repair_handoff_pointer(pointer)
    if errors or not isinstance(receipt, dict):
        return None
    handoff = receipt.get("repair_handoff")
    artifacts = handoff.get("artifacts") if isinstance(handoff, dict) else None
    snapshot_ref = artifacts.get("snapshot") if isinstance(artifacts, dict) else None
    raw_path = snapshot_ref.get("path") if isinstance(snapshot_ref, dict) else None
    if not isinstance(raw_path, str) or not raw_path:
        return None
    snapshot = _abs(Path(raw_path))
    return snapshot if snapshot.is_file() else None


def _append_manifest_gate_record(
    gate_manifest_path: Path,
    *,
    name: str,
    status: str,
    exit_code: int,
    message: str,
) -> None:
    try:
        data = _load_json(gate_manifest_path)
    except (OSError, json.JSONDecodeError, TypeError):
        return
    gates = data.setdefault("gates", [])
    gates.append(
        {
            "name": name,
            "phase": "post-ADG-subprocess",
            "kind": "subprocess",
            "blocking_mode": "hard_fail",
            "status": status,
            "exit_code": exit_code,
            "duration_s": None,
            "started_at_utc": _utcnow_iso(),
            "finished_at_utc": _utcnow_iso(),
            "script_rel": "ops_scripts/ci/run_adg_three_graph_tests.py",
            "message": message,
        }
    )
    gate_manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _run_certification_plane2(
    *,
    gate_manifest_path: Path | None,
    snapshot: Path,
) -> list[str]:
    from tools.generate.integration.certification_plane2 import run_plane2_manifest_quick  # noqa: PLC0415

    reasons: list[str] = []
    rc, _rollup = run_plane2_manifest_quick(sqlite_path=snapshot, suite="quick", strict=True)
    status = "pass" if rc == 0 else "fail"
    if gate_manifest_path and gate_manifest_path.is_file():
        _append_manifest_gate_record(
            gate_manifest_path,
            name="three_bucket_manifest_quick",
            status=status,
            exit_code=rc,
            message=f"suite=quick strict=1 exit={rc}",
        )
    if rc != 0:
        reasons.append(f"three_bucket_manifest_quick exit_code={rc}")
    return reasons


def _cross_check_required_gates(gate_manifest: dict[str, Any]) -> list[str]:
    """Return list of reason strings for any required gate missing or skipped."""
    from tools.generate._required_gates import required_gate_names

    required = required_gate_names()
    recorded = {g["name"]: g for g in gate_manifest.get("gates", [])}
    reasons: list[str] = []
    for name in sorted(required):
        rec = recorded.get(name)
        if rec is None:
            reasons.append(f"required gate '{name}' absent from manifest")
            continue
        status = rec.get("status")
        if status in ("missing_script", "skipped"):
            reasons.append(f"required gate '{name}' status={status}")
        elif status in ("fail", "timed_out"):
            reasons.append(f"required gate '{name}' status={status}")
    return reasons


def _run_generator(
    *,
    extra_args: list[str],
    timeout_s: int,
    certification_mode: bool,
) -> int:
    import os as _os

    global _LAST_GENERATOR_RUN_ID
    env = _os.environ.copy()
    requested_run_id = env.get("ADG_RUN_ID") or datetime.now(ZoneInfo("America/New_York")).strftime(
        "%m%d%Y_%H%M"
    )
    env["ADG_RUN_ID"] = requested_run_id
    _LAST_GENERATOR_RUN_ID = requested_run_id
    # The wrapper owns the sole final terminal summary after its own planes,
    # enforcement report, handoff, and receipt have completed.
    env["ADG_SUPPRESS_TERMINAL_SUMMARY"] = "1"
    # Stage 1 must not publish a bundle that predates the wrapper-owned
    # plane-2, three-bucket, and enforcement artifacts.
    env["ADG_DEFER_OUTPUT_BUNDLE_TO_WRAPPER"] = "1"
    prior_snapshot = _validated_producer_prior_snapshot(_handoff_producer_artifacts_adg())
    if prior_snapshot is not None:
        env["ADG_PHASE_D_PRIOR_SNAPSHOT"] = str(prior_snapshot)
        print(f"[audit] Phase-D prior snapshot: {prior_snapshot}")
    else:
        env.pop("ADG_PHASE_D_PRIOR_SNAPSHOT", None)
    if certification_mode:
        env["ADG_CERTIFICATION_MODE"] = "1"
        # Plane-2 manifest runs in GHA / contract gates after Stage-1 (avoid duplicate).
        env["ADG_SKIP_PLANE2_MANIFEST"] = "1"
        # ADR-079: three-bucket stays off the default regen hot path, but CI
        # certification must populate v_runtime_proof + registry + gap JSON.
        env.setdefault("ADG_THREE_BUCKET", "1")
        env.setdefault("ADG_THREE_BUCKET_SIGN", "1")
    env_bits = []
    if certification_mode:
        env_bits.append("ADG_CERTIFICATION_MODE=1")
    if env.get("ADG_THREE_BUCKET", "").strip().lower() in ("1", "true", "yes"):
        env_bits.append("ADG_THREE_BUCKET=1")
    if env.get("ADG_THREE_BUCKET_SIGN", "").strip().lower() in ("1", "true", "yes"):
        env_bits.append("ADG_THREE_BUCKET_SIGN=1")
    env_note = " ".join(env_bits) + (" " if env_bits else "")
    print(
        f"[audit] Stage-1: ADG_RUN_ID={requested_run_id} {env_note}"
        f"python tools/generate/generate_full_adg.py {' '.join(extra_args)}"
    )
    try:
        proc = subprocess.run(  # noqa: S603
            [sys.executable, str(REPO_ROOT / "tools" / "generate" / "generate_full_adg.py"), *extra_args],
            cwd=str(REPO_ROOT),
            timeout=timeout_s,
            env=env,
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"[audit] Stage-1 FAIL — timed out after {timeout_s}s", file=sys.stderr)
        return 124
    return proc.returncode


def _run_report(
    *,
    snapshot: Path,
    fmt: str,
    require_runtime_proof: bool,
    timeout_s: int,
) -> int:
    args = [
        sys.executable,
        str(REPO_ROOT / "tools" / "adg" / "three_bucket_gap_report.py"),
        "--snapshot",
        str(snapshot),
        "--format",
        fmt,
    ]
    if require_runtime_proof:
        args.append("--require-runtime-proof")
    print(f"[audit] Stage-2: {' '.join(args[1:])}")
    try:
        proc = subprocess.run(  # noqa: S603
            args,
            cwd=str(REPO_ROOT),
            timeout=timeout_s,
            capture_output=True,
            text=True,
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"[audit] Stage-2 FAIL — timed out after {timeout_s}s", file=sys.stderr)
        return 124
    if proc.returncode != 0:
        diagnostic = (proc.stderr or proc.stdout or "").strip().splitlines()[-5:]
        if diagnostic:
            print("[audit] Stage-2 diagnostic: " + " | ".join(diagnostic), file=sys.stderr)
    return proc.returncode


def _capture_three_bucket_report_paths(
    *,
    fmt: str,
    adg_run_id: str | None,
    snapshot_path: Path | None,
    since_wall_start: float,
) -> tuple[list[Path], list[str]]:
    """Copy this invocation's fixed Stage-2 outputs into immutable run paths."""
    if not adg_run_id:
        return [], ["three-bucket report run id unavailable"]
    if snapshot_path is None or not snapshot_path.is_file():
        return [], ["three-bucket report snapshot unavailable"]

    suffixes = {
        "json": (".json",),
        "md": (".md",),
        "both": (".json", ".md"),
    }[fmt]
    report_dir = REPO_ROOT / "docs" / "reports" / "adg"
    captured: list[Path] = []
    errors: list[str] = []
    snapshot_digest = _sha256(snapshot_path)

    for suffix in suffixes:
        source = report_dir / f"THREE_BUCKET_GAP_REPORT{suffix}"
        if not source.is_file() or source.stat().st_size == 0:
            errors.append(f"three-bucket report output missing: {source}")
            continue
        if source.stat().st_mtime + 2 < since_wall_start:
            errors.append(f"three-bucket report output stale: {source}")
            continue
        try:
            if suffix == ".json":
                report = _load_json(source)
                if report.get("source_snapshot_sha256") != snapshot_digest:
                    raise ValueError("snapshot digest mismatch")
                if not _path_matches(report.get("source_snapshot_path"), snapshot_path):
                    raise ValueError("snapshot path mismatch")
            elif snapshot_path.name not in source.read_text(encoding="utf-8"):
                raise ValueError("snapshot name missing")

            destination = ARTIFACTS_ADG / f"adg_three_bucket_gap_report_{adg_run_id}{suffix}"
            captured.append(
                _copy_immutable_artifact(
                    source,
                    destination,
                    key=f"three_bucket_gap_report{suffix}",
                )
            )
        except (OSError, json.JSONDecodeError, RuntimeError, ValueError) as exc:
            errors.append(f"three-bucket report output invalid: {source}: {exc}")

    return captured, errors


def _default_incomplete_handoff() -> dict[str, Any]:
    return {
        "status": "incomplete",
        "artifacts": {},
        "counts": _repair_handoff_counts(),
        "legacy_counts": _legacy_repair_handoff_counts(_repair_handoff_counts()),
        "validation_errors": ["repair_handoff was not built"],
    }


def _downstream_release_status(result: WrapperResult) -> str:
    handoff = result.repair_handoff or {}
    if result.artifact_status not in {"certified", "repair_ready"}:
        return "blocked"
    if result.artifact_status_source != "direct":
        return "blocked"
    if handoff.get("validation_errors"):
        return "blocked"
    return "released"


def _handoff_paths(adg_run_id: str, *, artifacts_adg: Path | None = None) -> tuple[Path, Path]:
    directory = (artifacts_adg or ARTIFACTS_ADG) / "handoffs"
    return (
        directory / f"adg_repair_handoff_{adg_run_id}.json",
        directory / "adg_repair_handoff_latest.json",
    )


def _immutable_receipt_path(adg_run_id: str, *, artifacts_adg: Path | None = None) -> Path:
    return (artifacts_adg or ARTIFACTS_ADG) / "handoffs" / f"adg_audit_pipeline_receipt_{adg_run_id}.json"


def _write_repair_handoff_pointer(
    result: WrapperResult,
    *,
    receipt_path: Path,
    receipt_sha256: str,
    artifacts_adg: Path | None = None,
    publish_latest: bool = True,
) -> tuple[Path, dict[str, Any]] | None:
    if not result.adg_run_id:
        return None
    handoff_path, latest_pointer_path = _handoff_paths(result.adg_run_id, artifacts_adg=artifacts_adg)
    handoff_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_resolved = receipt_path.resolve()
    handoff_doc = {
        "schema_version": REPAIR_HANDOFF_SCHEMA_VERSION,
        "adg_run_id": result.adg_run_id,
        "receipt": {
            "path": str(receipt_resolved),
            "sha256": receipt_sha256,
        },
        "artifact_status": result.artifact_status,
        "artifact_status_source": result.artifact_status_source,
        "downstream_release_status": _downstream_release_status(result),
        "started_at_utc": result.started_at_utc,
        "completed_at_utc": result.completed_at_utc,
        "repair_handoff": result.repair_handoff or _default_incomplete_handoff(),
    }
    _write_immutable_text(
        handoff_path,
        json.dumps(handoff_doc, indent=2) + "\n",
        label="repair handoff",
    )
    handoff_sha256 = _sha256(handoff_path)
    latest_pointer = {
        "schema_version": REPAIR_HANDOFF_POINTER_SCHEMA_VERSION,
        "adg_run_id": result.adg_run_id,
        "handoff_path": str(handoff_path.resolve()),
        "handoff_sha256": handoff_sha256,
        "receipt_path": str(receipt_resolved),
        "receipt_sha256": receipt_sha256,
        "artifact_status": result.artifact_status,
        "downstream_release_status": _downstream_release_status(result),
    }
    if publish_latest:
        latest_pointer_path.write_text(json.dumps(latest_pointer, indent=2) + "\n", encoding="utf-8")
    try:
        display = handoff_path.relative_to(REPO_ROOT)
    except ValueError:
        display = handoff_path
    print(f"[audit] wrote immutable repair handoff: {display}")
    return handoff_path, latest_pointer


def _publish_result_snapshot_pointer(
    result: WrapperResult,
    *,
    artifacts_adg: Path,
    receipt_path: Path | None = None,
    handoff_path: Path | None = None,
) -> list[str]:
    """Publish exactly one role pointer for a finalized wrapper result."""
    if result.artifact_status == "certified" and result.certification_status == "clean":
        role = "certified"
    elif result.artifact_status == "repair_ready" and result.certification_status in {
        "failed",
        "diagnostic_only",
    }:
        role = "repair"
    else:
        return []

    handoff = result.repair_handoff or {}
    refs = handoff.get("artifacts") if isinstance(handoff.get("artifacts"), dict) else {}
    snapshot_ref = refs.get("snapshot") if isinstance(refs.get("snapshot"), dict) else {}
    raw_snapshot = snapshot_ref.get("path")
    if not isinstance(raw_snapshot, str):
        return [f"{role} pointer publication failed: snapshot handoff path missing"]

    sources: dict[str, Path] = {}
    for key in ("generation_manifest", "gate_manifest", "gate_results", "output_bundle"):
        ref = refs.get(key)
        if isinstance(ref, dict) and isinstance(ref.get("path"), str):
            sources[key] = Path(ref["path"])

    if "output_bundle" not in sources:
        return [f"{role} pointer publication failed: sealed output bundle missing"]
    if receipt_path is None or handoff_path is None:
        return [f"{role} pointer publication failed: immutable receipt or handoff missing"]
    sources["audit_receipt"] = receipt_path
    sources["repair_handoff"] = handoff_path

    try:
        from tools.adg.shared_modules.snapshot_registry import (  # noqa: PLC0415
            SnapshotPointerError,
            load_snapshot_pointer,
            publish_snapshot_pointer,
        )
        from tools.reports.adg_run_output_bundle import (  # noqa: PLC0415
            _publication_lock,
            _reserve_latest_publication,
        )

        known_sha = snapshot_ref.get("sha256")
        if not result.adg_run_id:
            raise ValueError("snapshot pointer publication requires adg_run_id")
        with _publication_lock(artifacts_adg):
            _reserve_latest_publication(artifacts_adg, result.adg_run_id)
            publish_snapshot_pointer(
                adg_dir=artifacts_adg,
                role=role,
                snapshot_path=Path(raw_snapshot),
                snapshot_sha256=(known_sha if isinstance(known_sha, str) else None),
                certification_status=result.certification_status,
                artifact_status=result.artifact_status,
                source_artifacts=sources,
            )
    except (OSError, RuntimeError, TimeoutError, ValueError, SnapshotPointerError) as exc:
        # A directory fsync may fail after os.replace has already activated the
        # pointer. Reload the exact role before deciding the publication failed;
        # mutating any digest-bound artifact after a committed replace would
        # invalidate an active pointer.
        try:
            published = load_snapshot_pointer(
                artifacts_adg,
                role,  # type: ignore[arg-type]
                verify_digest=True,
            )
            expected_snapshot = Path(raw_snapshot).resolve()
            if published.path.resolve() != expected_snapshot:
                raise SnapshotPointerError("activated pointer snapshot differs from current run")
            if (
                published.certification_status != result.certification_status
                or published.artifact_status != result.artifact_status
            ):
                raise SnapshotPointerError("activated pointer status differs from current run")
            base = artifacts_adg.resolve()
            for label, source in sources.items():
                source_resolved = source.resolve()
                expected_path = source_resolved.relative_to(base).as_posix()
                actual_ref = published.source_artifacts.get(label)
                if (
                    not isinstance(actual_ref, dict)
                    or actual_ref.get("path") != expected_path
                    or actual_ref.get("sha256") != _sha256(source_resolved)
                ):
                    raise SnapshotPointerError(f"activated pointer source differs from current run: {label}")
        except (OSError, ValueError, SnapshotPointerError):
            return [f"{role} pointer publication failed: {exc}"]
    return []


def _receipt_payload(result: WrapperResult) -> dict[str, Any]:
    handoff = result.repair_handoff or _default_incomplete_handoff()
    refs = handoff.get("artifacts") if isinstance(handoff.get("artifacts"), dict) else {}
    bundle_ref = refs.get("output_bundle") if isinstance(refs.get("output_bundle"), dict) else {}
    bundle_raw = bundle_ref.get("path")
    if not isinstance(bundle_raw, str) or not bundle_raw:
        raise RuntimeError("audit pipeline receipt requires a sealed output_bundle reference")
    bundle_path = Path(bundle_raw)
    bundle = _load_json(bundle_path)
    expected_digest = bundle_ref.get("sha256")
    if not isinstance(expected_digest, str) or _sha256(bundle_path) != expected_digest:
        raise RuntimeError("audit pipeline receipt output_bundle digest mismatch")
    bundle_exit_code = bundle.get("final_exit_code")
    if not isinstance(bundle_exit_code, int) or isinstance(bundle_exit_code, bool):
        raise RuntimeError("audit pipeline receipt output_bundle is not terminally finalized")
    if bundle_exit_code != result.process_exit_code:
        raise RuntimeError("audit pipeline receipt process exit differs from output_bundle final_exit_code")
    if result.artifact_status == "certified" and bundle_exit_code != 0:
        raise RuntimeError("certified audit pipeline receipt requires process exit code 0")
    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "run_state": {
            "certification_status": result.certification_status,
            "process_exit_code": result.process_exit_code,
            "generator_exit_code": result.generator_exit_code,
            "report_exit_code": result.report_exit_code,
            "runtime_proof_status": result.runtime_proof_status,
            "reasons": result.reasons,
        },
        "artifact_status": result.artifact_status,
        "artifact_status_source": result.artifact_status_source,
        "adg_run_id": result.adg_run_id,
        "started_at_utc": result.started_at_utc,
        "completed_at_utc": result.completed_at_utc,
        "repair_handoff": handoff,
    }


def _prepare_immutable_publication(
    result: WrapperResult,
    *,
    producer_artifacts: Path,
) -> PublicationDocuments:
    if not result.adg_run_id:
        raise RuntimeError("immutable publication requires adg_run_id")
    receipt_text = json.dumps(_receipt_payload(result), indent=2) + "\n"
    immutable_receipt = _immutable_receipt_path(
        result.adg_run_id,
        artifacts_adg=producer_artifacts,
    )
    immutable_receipt.parent.mkdir(parents=True, exist_ok=True)
    _write_immutable_text(immutable_receipt, receipt_text, label="audit pipeline receipt")
    handoff_publication = _write_repair_handoff_pointer(
        result,
        receipt_path=immutable_receipt,
        receipt_sha256=_sha256(immutable_receipt),
        artifacts_adg=producer_artifacts,
        publish_latest=False,
    )
    if handoff_publication is None:
        raise RuntimeError("immutable repair handoff was not written")
    handoff_path, latest_pointer = handoff_publication
    return PublicationDocuments(
        receipt_path=immutable_receipt,
        handoff_path=handoff_path,
        latest_handoff_pointer=latest_pointer,
        receipt_text=receipt_text,
    )


def _publish_convenience_aliases(
    publication: PublicationDocuments,
    result: WrapperResult,
    *,
    producer_artifacts: Path,
) -> list[str]:
    """Publish recoverable aliases only after the role pointer activates."""
    from tools.reports.adg_run_output_bundle import (  # noqa: PLC0415
        _atomic_write_text,
        _publication_lock,
        _reserve_latest_publication,
    )

    if not result.adg_run_id:
        return ["convenience alias publication skipped: adg_run_id missing"]
    aliases = (
        (
            RECEIPT_PATH,
            publication.receipt_text,
            "receipt alias",
        ),
        (
            _handoff_paths(result.adg_run_id or "", artifacts_adg=producer_artifacts)[1],
            json.dumps(publication.latest_handoff_pointer, indent=2) + "\n",
            "repair handoff alias",
        ),
    )
    try:
        with _publication_lock(producer_artifacts):
            _reserve_latest_publication(producer_artifacts, result.adg_run_id)
            for path, text, _label in aliases:
                path.parent.mkdir(parents=True, exist_ok=True)
                _atomic_write_text(path, text)

            refs = (result.repair_handoff or {}).get("artifacts")
            bundle_ref = refs.get("output_bundle") if isinstance(refs, dict) else None
            bundle_raw = bundle_ref.get("path") if isinstance(bundle_ref, dict) else None
            if not isinstance(bundle_raw, str):
                raise RuntimeError("output bundle alias source missing after activation")
            bundle_path = Path(bundle_raw)
            bundle_text = bundle_path.read_text(encoding="utf-8")
            _atomic_write_text(
                producer_artifacts / "adg_run_output_bundle_latest.json",
                bundle_text,
            )
    except (OSError, RuntimeError, TimeoutError) as exc:
        return [f"convenience alias publication failed after activation: {exc}"]
    return []


def _publish_blocked_latest_state(
    result: WrapperResult,
    *,
    producer_artifacts: Path,
    diagnostics: list[str],
) -> list[str]:
    """Advance mutable latest views to an explicit fail-closed tombstone."""
    from tools.reports.adg_run_output_bundle import (  # noqa: PLC0415
        _atomic_write_text,
        _publication_lock,
        _reserve_latest_publication,
    )

    blocked_run_id = result.adg_run_id or datetime.now(ZoneInfo("America/New_York")).strftime("%Y%m%d_%H%M%S")
    blocked_document_id = blocked_run_id if result.adg_run_id else f"{blocked_run_id}_{time.time_ns()}"
    blocked_handoff = json.loads(json.dumps(result.repair_handoff or _default_incomplete_handoff()))
    blocked_handoff["status"] = "incomplete"
    validation_errors = blocked_handoff.setdefault("validation_errors", [])
    if not isinstance(validation_errors, list):
        validation_errors = []
        blocked_handoff["validation_errors"] = validation_errors
    validation_errors.extend(diagnostics or ["current run was not activated"])
    validation_errors[:] = sorted({str(item) for item in validation_errors})

    receipt_payload = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "run_state": {
            "certification_status": "failed",
            "process_exit_code": 1,
            "generator_exit_code": result.generator_exit_code,
            "report_exit_code": result.report_exit_code,
            "runtime_proof_status": result.runtime_proof_status,
            "reasons": sorted({*result.reasons, *diagnostics}),
        },
        "artifact_status": "incomplete",
        "artifact_status_source": "direct",
        "adg_run_id": blocked_run_id,
        "started_at_utc": result.started_at_utc,
        "completed_at_utc": result.completed_at_utc,
        "repair_handoff": blocked_handoff,
    }
    receipt_text = json.dumps(receipt_payload, indent=2) + "\n"
    handoff_dir = producer_artifacts / "handoffs"
    blocked_receipt = handoff_dir / f"adg_audit_pipeline_receipt_{blocked_document_id}_blocked.json"
    blocked_handoff_path = handoff_dir / f"adg_repair_handoff_{blocked_document_id}_blocked.json"
    blocked_handoff_doc = {
        "schema_version": REPAIR_HANDOFF_SCHEMA_VERSION,
        "adg_run_id": blocked_run_id,
        "receipt": {
            "path": str(blocked_receipt.resolve()),
            "sha256": "",
        },
        "artifact_status": "incomplete",
        "artifact_status_source": "direct",
        "downstream_release_status": "blocked",
        "started_at_utc": result.started_at_utc,
        "completed_at_utc": result.completed_at_utc,
        "repair_handoff": blocked_handoff,
    }
    bundle_tombstone = {
        "schema_version": "adg-run-output-bundle/v1",
        "run_id": blocked_run_id,
        "status": "blocked",
        "latest_promoted": False,
        "final_exit_code": 1,
        "diagnostics": sorted(set(diagnostics or ["current run was not activated"])),
    }
    try:
        with _publication_lock(producer_artifacts):
            _reserve_latest_publication(producer_artifacts, blocked_run_id)
            _write_immutable_text(
                blocked_receipt,
                receipt_text,
                label="blocked audit pipeline receipt",
            )
            blocked_handoff_doc["receipt"]["sha256"] = _sha256(blocked_receipt)
            blocked_handoff_text = json.dumps(blocked_handoff_doc, indent=2) + "\n"
            _write_immutable_text(
                blocked_handoff_path,
                blocked_handoff_text,
                label="blocked repair handoff",
            )
            latest_pointer = {
                "schema_version": REPAIR_HANDOFF_POINTER_SCHEMA_VERSION,
                "adg_run_id": blocked_run_id,
                "handoff_path": str(blocked_handoff_path.resolve()),
                "handoff_sha256": _sha256(blocked_handoff_path),
                "receipt_path": str(blocked_receipt.resolve()),
                "receipt_sha256": _sha256(blocked_receipt),
                "artifact_status": "incomplete",
                "downstream_release_status": "blocked",
            }
            RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write_text(RECEIPT_PATH, receipt_text)
            _atomic_write_text(
                _handoff_paths(blocked_run_id, artifacts_adg=producer_artifacts)[1],
                json.dumps(latest_pointer, indent=2) + "\n",
            )
            _atomic_write_text(
                producer_artifacts / "adg_run_output_bundle_latest.json",
                json.dumps(bundle_tombstone, indent=2, sort_keys=True) + "\n",
            )
    except (OSError, RuntimeError, TimeoutError) as exc:
        return [f"blocked latest state publication failed: {exc}"]
    return []


def _write_receipt(result: WrapperResult, *, producer_artifacts: Path | None = None) -> None:
    """Compatibility helper for direct callers; run_audit controls activation order."""
    if producer_artifacts is None:
        producer_artifacts = _handoff_producer_artifacts_adg()
    handoff_result = _copy_result_for_handoff_root(result, producer_artifacts=producer_artifacts)
    publication = _prepare_immutable_publication(
        handoff_result,
        producer_artifacts=producer_artifacts,
    )
    activation_errors = _publish_result_snapshot_pointer(
        handoff_result,
        artifacts_adg=producer_artifacts,
        receipt_path=publication.receipt_path,
        handoff_path=publication.handoff_path,
    )
    if activation_errors:
        raise RuntimeError("; ".join(activation_errors))
    alias_errors = _publish_convenience_aliases(
        publication,
        handoff_result,
        producer_artifacts=producer_artifacts,
    )
    for error in alias_errors:
        print(f"[audit] warning: {error}", file=sys.stderr)
    try:
        display = RECEIPT_PATH.relative_to(REPO_ROOT)
    except ValueError:
        display = RECEIPT_PATH
    print(f"[audit] wrote receipt: {display}")


def run_audit(
    *,
    mode: str = "certification",
    fmt: str = "both",
    require_runtime_proof: bool = False,
    diagnostic_allow_failed_generator: bool = False,
    continue_on_p0: bool = False,
    generator_timeout_s: int = 1800,
    report_timeout_s: int = 300,
    generator_extra_args: list[str] | None = None,
) -> WrapperResult:
    """Run the audit pipeline. Pure function so tests can drive it."""

    global _LAST_GENERATOR_RUN_ID
    reasons: list[str] = []
    wall_start = time.time()
    started_at_utc = _utcnow_iso()
    ARTIFACTS_ADG.mkdir(parents=True, exist_ok=True)
    producer_artifacts = _handoff_producer_artifacts_adg()

    extra = list(generator_extra_args or [])
    if continue_on_p0 and "--continue-on-p0" not in extra:
        extra.append("--continue-on-p0")

    certification_mode = mode == "certification"

    # Stage 1 — generator.
    _LAST_GENERATOR_RUN_ID = None
    gen_rc = _run_generator(
        extra_args=extra,
        timeout_s=generator_timeout_s,
        certification_mode=certification_mode,
    )
    if gen_rc != 0 and (certification_mode or not diagnostic_allow_failed_generator):
        reasons.append(f"generator exit_code={gen_rc}")

    # Locate manifests.
    gen_manifest_path = (
        None
        if gen_rc == RUN_ID_COLLISION_EXIT_CODE
        else _find_generation_manifest(
            wall_start,
            expected_run_id=_LAST_GENERATOR_RUN_ID,
        )
    )
    gate_manifest_path: Path | None = None
    generation_manifest: dict[str, Any] = {}
    gate_manifest: dict[str, Any] = {}
    runtime_proof_status = "view_absent"
    snapshot_raw: str | None = None
    if gen_manifest_path is None:
        reasons.append("generation manifest missing — generator did not emit or clock skew > 2s")
    else:
        try:
            generation_manifest = _load_json(gen_manifest_path)
            runtime_proof_status = generation_manifest.get("runtime_proof_status", "view_absent")
            gm_raw = generation_manifest.get("gate_manifest_path")
            if gm_raw:
                gate_manifest_path = Path(gm_raw)
                if gate_manifest_path.is_file():
                    gate_manifest = _load_json(gate_manifest_path)
                else:
                    reasons.append(f"gate manifest path declared but missing: {gate_manifest_path}")
        except (OSError, json.JSONDecodeError, TypeError) as e:
            reasons.append(f"failed to read generation manifest: {e}")

    snapshot_raw = generation_manifest.get("sqlite_path") or generation_manifest.get("snapshot_path")
    adg_run_id_for_outputs = _derive_adg_run_stamp(
        generation_manifest,
        gen_manifest_path,
        Path(snapshot_raw) if snapshot_raw else None,
    )
    snapshot_path_for_outputs = _abs(Path(snapshot_raw)) if snapshot_raw else None
    snapshot_path_for_outputs, snapshot_recovery_errors = _recover_snapshot_from_run_stamp(
        snapshot_path=snapshot_path_for_outputs,
        adg_run_id=adg_run_id_for_outputs,
        since_wall_start=wall_start,
    )
    if snapshot_path_for_outputs is not None and snapshot_path_for_outputs.is_file():
        snapshot_raw = str(snapshot_path_for_outputs)
    elif certification_mode:
        reasons.extend(snapshot_recovery_errors)

    # Resolve the current dispatcher result for plane-3/enforcement without
    # sealing the output bundle yet. The wrapper must finish every producer
    # before it publishes or revalidates the single mandatory bundle.
    current_gate_results_path: Path | None = None
    if snapshot_path_for_outputs is not None and snapshot_path_for_outputs.is_file():
        current_gate_results_path, _gate_result_errors = _find_gate_results_for_snapshot(
            snapshot_path_for_outputs,
            since_wall_start=wall_start,
        )

    # Plane 2 — three-graph manifest (certification; generator skips via env).
    if (
        certification_mode
        and gen_rc == 0
        and snapshot_raw
        and gate_manifest_path is not None
        and gate_manifest_path.is_file()
    ):
        snap_path = Path(snapshot_raw)
        if snap_path.is_file():
            reasons.extend(
                _run_certification_plane2(
                    gate_manifest_path=gate_manifest_path,
                    snapshot=snap_path,
                )
            )
            try:
                gate_manifest = _load_json(gate_manifest_path)
            except (OSError, json.JSONDecodeError, TypeError):
                pass

    # Cross-check required gates (certification mode only).
    if certification_mode and gate_manifest:
        reasons.extend(_cross_check_required_gates(gate_manifest))

    # Plane-3 dispatcher failure (generator records + exits; double-check JSON).
    if certification_mode:
        if current_gate_results_path is None:
            reasons.append("adg_gate_dispatcher current-run results unavailable")
        else:
            try:
                disp_payload = _load_json(current_gate_results_path)
                if not isinstance(disp_payload, dict):
                    raise TypeError("dispatcher result must be an object")
                dispatcher_exit = disp_payload.get("overall_exit_code")
                if not isinstance(dispatcher_exit, int) or isinstance(dispatcher_exit, bool):
                    reasons.append("adg_gate_dispatcher overall_exit_code malformed")
                elif dispatcher_exit != 0:
                    reasons.append(f"adg_gate_dispatcher overall_exit_code={dispatcher_exit}")
            except (OSError, json.JSONDecodeError, TypeError):
                reasons.append("adg_gate_dispatcher results unreadable")

    # Runtime-proof gate.
    if require_runtime_proof and runtime_proof_status != "attested":
        reasons.append(f"--require-runtime-proof set but runtime_proof_status={runtime_proof_status!r}")

    # Stage 2 — report, only if we have a snapshot.
    report_rc: int | None = None
    snapshot = snapshot_raw
    if snapshot:
        snap_path = Path(snapshot)
        if snap_path.is_file():
            # In certification mode with already-known runtime-proof gate failure,
            # still run the report for diagnostic value but propagate the failure.
            report_rc = _run_report(
                snapshot=snap_path,
                fmt=fmt,
                require_runtime_proof=require_runtime_proof,
                timeout_s=report_timeout_s,
            )
            if report_rc != 0:
                reasons.append(f"three_bucket_gap_report exit_code={report_rc}")
        else:
            reasons.append(f"snapshot declared but not found: {snap_path}")
    else:
        reasons.append("snapshot path absent from generation manifest")

    three_bucket_report_paths, three_bucket_report_errors = _capture_three_bucket_report_paths(
        fmt=fmt,
        adg_run_id=adg_run_id_for_outputs,
        snapshot_path=snapshot_path_for_outputs,
        since_wall_start=wall_start,
    )

    # ADR-081: unified enforcement report (planes 1–3 rollup).
    enforcement_path: Path | None = None
    enforcement_rollup: str | None = None
    enforcement_diagnostic = ""
    try:
        from tools.adg.integration.enforcement_report import (  # noqa: PLC0415
            build_enforcement_report,
            write_enforcement_report,
        )

        rollup_path = REPO_ROOT / "docs" / "reports" / "adg" / "three_graph_test_rollup.json"
        disp_path = current_gate_results_path
        snap_path = Path(snapshot) if snapshot else None
        run_ts = _derive_adg_run_stamp(generation_manifest, gen_manifest_path, snap_path)
        report = build_enforcement_report(
            snapshot_path=snap_path if snap_path and snap_path.is_file() else None,
            gate_manifest_path=gate_manifest_path,
            three_graph_rollup_path=rollup_path if rollup_path.is_file() else None,
            dispatcher_results_path=disp_path,
            runtime_proof_status=runtime_proof_status,
            require_runtime_proof=require_runtime_proof,
            ts=run_ts,
        )
        enforcement_path = write_enforcement_report(report, ts=run_ts)
        enforcement_rollup = report.get("certified_rollup")
        if certification_mode and enforcement_rollup == "NOT_CERTIFIED":
            reasons.append("enforcement_report certified_rollup=NOT_CERTIFIED")
    except (ImportError, OSError, TypeError, ValueError) as exc:
        enforcement_diagnostic = f"enforcement_report build failed: {exc}"
        if certification_mode:
            reasons.append(enforcement_diagnostic)

    from tools.reports.adg_run_output_bundle import OutputGate  # noqa: PLC0415

    report_gate_passed = report_rc == 0 and bool(three_bucket_report_paths) and not three_bucket_report_errors
    report_gate = OutputGate(
        key="wrapper_three_bucket_report",
        required=True,
        status="pass" if report_gate_passed else "fail",
        producer_exit_code=report_rc if isinstance(report_rc, int) else 2,
        paths=[str(path.resolve()) for path in three_bucket_report_paths],
        diagnostic="; ".join(three_bucket_report_errors),
    )

    enforcement_errors: list[str] = []
    if enforcement_diagnostic:
        enforcement_errors.append(enforcement_diagnostic)
    if enforcement_path is None or not enforcement_path.is_file():
        enforcement_errors.append("current-run enforcement report missing")
    else:
        if enforcement_path.stat().st_size == 0:
            enforcement_errors.append("current-run enforcement report is empty")
        if enforcement_path.stat().st_mtime + 2 < wall_start:
            enforcement_errors.append("current-run enforcement report is stale")
        try:
            persisted_enforcement = _load_json(enforcement_path)
            if not isinstance(persisted_enforcement, dict):
                raise TypeError("enforcement report root must be an object")
            if persisted_enforcement.get("certified_rollup") != "CERTIFIED":
                enforcement_errors.append(
                    f"enforcement report certified_rollup={persisted_enforcement.get('certified_rollup')!r}"
                )
            if snapshot_path_for_outputs is not None and not _path_matches(
                persisted_enforcement.get("snapshot_path"),
                snapshot_path_for_outputs,
            ):
                enforcement_errors.append("enforcement report snapshot mismatch")
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            enforcement_errors.append(f"enforcement report unreadable: {exc}")
    if enforcement_rollup != "CERTIFIED":
        enforcement_errors.append(f"in-memory enforcement rollup={enforcement_rollup!r}")
    enforcement_gate_passed = not enforcement_errors
    enforcement_gate = OutputGate(
        key="wrapper_enforcement",
        required=True,
        status="pass" if enforcement_gate_passed else "fail",
        producer_exit_code=0 if enforcement_gate_passed else 1,
        paths=[str(enforcement_path.resolve())]
        if enforcement_path is not None and enforcement_path.is_file()
        else [],
        diagnostic="; ".join(dict.fromkeys(enforcement_errors)),
    )

    # Seal only after plane 2, Stage-2 reporting, and the exact current-run
    # enforcement report have completed. Mandatory output failures are fatal
    # in diagnostic mode too; the generator-only diagnostic opt-out does not
    # waive a missing or blocked output contract.
    mandatory_output_errors, output_bundle, sealed_gate_results_path = _emit_mandatory_run_outputs(
        snapshot_path=snapshot_path_for_outputs,
        adg_run_id=adg_run_id_for_outputs,
        since_wall_start=wall_start,
        generator_exit_code=gen_rc,
        enforcement_report_path=enforcement_path,
        certification_gates=[report_gate, enforcement_gate],
    )
    reasons.extend(mandatory_output_errors)
    if current_gate_results_path is None:
        current_gate_results_path = sealed_gate_results_path

    # Classify certification_status.
    if not certification_mode:
        status = "diagnostic_only"
    elif reasons:
        status = "failed"
    else:
        status = "clean"

    # First classify the artifact closure without requiring terminal finalization.
    # This lets us calculate the only exit code that will be sealed into the
    # terminal and bundle; the strict handoff is rebuilt after that one write.
    predicted_artifact_status, _predicted_handoff, predicted_handoff_errors = _build_repair_handoff(
        generation_manifest_path=gen_manifest_path,
        gate_manifest_path=gate_manifest_path,
        generation_manifest=generation_manifest,
        certification_status=status,
        since_wall_start=wall_start,
        allow_unfinalized_output_bundle=True,
    )
    predicted_exit_code = (
        0
        if (
            certification_mode
            and status == "clean"
            and predicted_artifact_status == "certified"
            and not reasons
        )
        or (
            not certification_mode
            and predicted_artifact_status in {"certified", "repair_ready"}
            and not reasons
        )
        else 1
    )
    seal_diagnostics = [
        f"certification_status={status}",
        f"artifact_status={predicted_artifact_status}",
        f"generator_exit_code={gen_rc}; report_exit_code={report_rc}",
        f"runtime_proof_status={runtime_proof_status}",
        *reasons,
        *predicted_handoff_errors,
    ]
    seal_error: str | None = None
    if output_bundle is not None:
        from tools.reports.adg_run_output_bundle import print_adg_run_terminal_summary  # noqa: PLC0415

        try:
            print_adg_run_terminal_summary(
                output_bundle,
                final_exit_code=predicted_exit_code,
                diagnostics=seal_diagnostics,
                print_terminal=False,
                publish_latest=False,
            )
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            seal_error = f"output bundle terminal finalization failed: {exc}"
    else:
        seal_error = "output bundle terminal finalization failed: bundle unavailable"

    artifact_status, repair_handoff, handoff_errors = _build_repair_handoff(
        generation_manifest_path=gen_manifest_path,
        gate_manifest_path=gate_manifest_path,
        generation_manifest=generation_manifest,
        certification_status=status,
        since_wall_start=wall_start,
    )
    adg_run_id = _derive_adg_run_stamp(
        generation_manifest,
        gen_manifest_path,
        Path(snapshot) if snapshot else None,
    )
    retention_run_id = (
        adg_run_id
        or adg_run_id_for_outputs
        or _find_recent_sqlite_run_stamp(
            since_wall_start=wall_start,
        )
    )
    completed_at_utc = _utcnow_iso()

    result = WrapperResult(
        certification_status=status,
        generator_exit_code=gen_rc,
        report_exit_code=report_rc,
        generation_manifest_path=gen_manifest_path,
        gate_manifest_path=gate_manifest_path,
        runtime_proof_status=runtime_proof_status,
        reasons=reasons,
        artifact_status=artifact_status,
        artifact_status_source="direct",
        adg_run_id=adg_run_id,
        started_at_utc=started_at_utc,
        completed_at_utc=completed_at_utc,
        repair_handoff=repair_handoff,
        process_exit_code=predicted_exit_code,
    )
    publication_errors: list[str] = []
    if seal_error:
        publication_errors.append(seal_error)
    if artifact_status != predicted_artifact_status:
        publication_errors.append(
            "post-finalization handoff status differs from predicted status: "
            f"predicted={predicted_artifact_status} actual={artifact_status}"
        )
    if handoff_errors and not predicted_handoff_errors:
        publication_errors.append(
            "post-finalization handoff validation failed: " + "; ".join(sorted(set(handoff_errors)))
        )

    publication: PublicationDocuments | None = None
    if not publication_errors and _downstream_release_status(result) == "released":
        try:
            # Transport/reseal exactly once before immutable receipt creation.
            result = _copy_result_for_handoff_root(
                result,
                producer_artifacts=producer_artifacts,
            )
            publication = _prepare_immutable_publication(
                result,
                producer_artifacts=producer_artifacts,
            )
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            publication_errors.append(f"immutable publication preparation failed: {exc}")

    if publication is not None and not publication_errors:
        publication_errors.extend(
            _publish_result_snapshot_pointer(
                result,
                artifacts_adg=producer_artifacts,
                receipt_path=publication.receipt_path,
                handoff_path=publication.handoff_path,
            )
        )
        if not publication_errors:
            for warning in _publish_convenience_aliases(
                publication,
                result,
                producer_artifacts=producer_artifacts,
            ):
                print(f"[audit] warning: {warning}", file=sys.stderr)

    if publication_errors:
        result.reasons.extend(publication_errors)
        result.artifact_status = "incomplete"
        if result.certification_status == "clean":
            result.certification_status = "failed"
        if result.repair_handoff is not None:
            result.repair_handoff["status"] = "incomplete"
            validation_errors = result.repair_handoff.setdefault(
                "validation_errors",
                [],
            )
            validation_errors.extend(publication_errors)
        result.process_exit_code = 1
        for error in publication_errors:
            print(f"[audit] BLOCKED after sealing: {error}", file=sys.stderr)

    if publication is None or publication_errors:
        handoff_validation_errors = (
            (result.repair_handoff or {}).get("validation_errors")
            if isinstance((result.repair_handoff or {}).get("validation_errors"), list)
            else []
        )
        blocked_diagnostics = list(
            dict.fromkeys(
                [
                    *publication_errors,
                    *result.reasons,
                    *(str(item) for item in handoff_validation_errors),
                ]
            )
        ) or ["current run was not eligible for snapshot activation"]
        for warning in _publish_blocked_latest_state(
            result,
            producer_artifacts=producer_artifacts,
            diagnostics=blocked_diagnostics,
        ):
            print(f"[audit] warning: {warning}", file=sys.stderr)

    _run_retention_sweep(
        retention_run_id,
        adg_dir=producer_artifacts,
    )
    if enforcement_path is not None:
        print(f"[audit] enforcement report: {enforcement_path}")

    wrapper_exit_code = result.process_exit_code
    terminal_matches_exit = False
    if output_bundle is not None:
        manifest_path = getattr(output_bundle, "manifest_path", None)
        try:
            terminal_matches_exit = not isinstance(manifest_path, Path) or (
                _load_json(manifest_path).get("final_exit_code") == wrapper_exit_code
            )
        except (OSError, json.JSONDecodeError, TypeError):
            terminal_matches_exit = False
    if (
        output_bundle is not None
        and terminal_matches_exit
        and output_bundle.terminal_summary_path is not None
        and output_bundle.terminal_summary_path.is_file()
    ):
        sys.stdout.write("\n" + output_bundle.terminal_summary_path.read_text(encoding="utf-8"))
    else:
        lines = [
            "## ADG Executive Brief",
            "",
            "- **Status:** `BLOCKED`",
            "- **Output bundle:** unavailable",
            "- **Impact Inventory:** unavailable",
            "- **Decision gate:** BLOCKED",
            "- **Fix now:** restore the current-run output bundle, then rerun",
            "",
            "## Final disposition",
            "",
            f"- **Process exit code:** `{wrapper_exit_code}`",
        ]
        lines.extend(f"- **Diagnostic:** {diagnostic}" for diagnostic in seal_diagnostics)
        lines.extend(f"- **Diagnostic:** {diagnostic}" for diagnostic in publication_errors)
        print("\n" + "\n".join(lines))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("certification", "diagnostic"), default="certification")
    parser.add_argument("--format", choices=("json", "md", "both"), default="both")
    parser.add_argument("--require-runtime-proof", action="store_true")
    parser.add_argument("--diagnostic-allow-failed-generator", action="store_true")
    parser.add_argument("--continue-on-p0", action="store_true")
    parser.add_argument("--generator-timeout-seconds", type=int, default=1800)
    parser.add_argument("--report-timeout-seconds", type=int, default=300)
    parser.add_argument(
        "--generator-arg",
        action="append",
        default=[],
        help="Extra arg to pass through to generate_full_adg.py (repeatable).",
    )
    args = parser.parse_args(argv)

    result = run_audit(
        mode=args.mode,
        fmt=args.format,
        require_runtime_proof=args.require_runtime_proof,
        diagnostic_allow_failed_generator=args.diagnostic_allow_failed_generator,
        continue_on_p0=args.continue_on_p0,
        generator_timeout_s=args.generator_timeout_seconds,
        report_timeout_s=args.report_timeout_seconds,
        generator_extra_args=args.generator_arg,
    )

    return result.process_exit_code


if __name__ == "__main__":
    sys.exit(main())
