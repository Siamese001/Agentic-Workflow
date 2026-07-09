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
)


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

    @property
    def ok(self) -> bool:
        return self.certification_status == "clean"


def _find_generation_manifest(since_monotonic_start: float) -> Path | None:
    """Return the newest generation manifest created during this run.

    We filter by mtime strictly greater than ``wall_start`` to avoid
    picking up a stale manifest from a prior run. ``latest.json`` is
    NEVER consulted from CI — CI resolves by timestamped filename.
    """
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
    return json.loads(path.read_text(encoding="utf-8"))


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
    }
    prefix, suffix = expected[key]
    name = path.name
    if not name.startswith(prefix) or not name.endswith(suffix):
        return False
    stamp = name[len(prefix):-len(suffix)]
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
            raise RuntimeError(f"immutable {key} artifact already exists with different content: {destination}")
        return destination_resolved
    shutil.copy2(source_resolved, destination)
    if _sha256(destination) != source_sha256:
        raise RuntimeError(f"copied {key} artifact sha256 mismatch: {destination}")
    return destination_resolved


def _published_generation_manifest_text(source: Path, destinations: dict[str, Path]) -> str | None:
    try:
        payload = _load_json(source)
    except (OSError, json.JSONDecodeError):
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
        "P0_FIX": 0,
        "P0_WAVE": 0,
        "P0_TRACKED_BACKLOG": 0,
        "P1_FIX": 0,
        "P1_RATCHET_REGRESSION": 0,
        "P1_RATCHET_FLOOR_BACKLOG": 0,
    }


def _stamp_from_artifact_name(path: Path | None, *, prefix: str, suffix: str) -> str | None:
    if path is None:
        return None
    name = path.name
    if not name.startswith(prefix) or not name.endswith(suffix):
        return None
    stamp = name[len(prefix):-len(suffix)]
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


def _run_retention_sweep(adg_run_id: str | None) -> None:
    """Best-effort ADG artifact cleanup shared by scheduled wrapper runs."""
    if not adg_run_id:
        print("[audit] retention skipped: no ADG run id available")
        return
    try:
        from tools.generate.archiving import _archive_old_artifacts  # noqa: PLC0415

        _archive_old_artifacts(ARTIFACTS_ADG, adg_run_id, keep_runs=1)
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
        except (OSError, json.JSONDecodeError) as exc:
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
            "degradation_reasons": reasons,
        },
    }
    latest = ARTIFACTS_ADG / "adg_burndown_table.json"
    timestamped = ARTIFACTS_ADG / f"adg_burndown_table_{adg_run_id}.json"
    latest.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    latest.write_text(rendered, encoding="utf-8")
    timestamped.write_text(rendered, encoding="utf-8")
    return timestamped


def _json_has_degraded_fallback_marker(path: Path) -> bool:
    if path.suffix.lower() != ".json":
        return False
    try:
        data = _load_json(path)
    except (OSError, json.JSONDecodeError):
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


def _emit_mandatory_run_outputs(
    *,
    snapshot_path: Path | None,
    adg_run_id: str | None,
    since_wall_start: float,
    generator_exit_code: int | None,
) -> list[str]:
    if snapshot_path is None or not snapshot_path.is_file():
        return ["mandatory ADG outputs not emitted because same-run snapshot is unavailable"]
    if not adg_run_id:
        return ["mandatory ADG outputs not emitted because adg_run_id is unavailable"]

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

    action_queue_path, queue_errors = _ensure_action_queue_for_handoff(
        gate_results_path=gate_results_path,
        burndown_table_path=burndown_table_path,
        snapshot_path=snapshot_path,
        adg_run_id=adg_run_id,
    )
    errors.extend(queue_errors)

    try:
        from tools.reports.adg_bcg_executive_synthesis import emit_bcg_executive_summary  # noqa: PLC0415

        bcg_rc, _bcg_path = emit_bcg_executive_summary(
            adg_artifacts_dir=ARTIFACTS_ADG,
            ts=adg_run_id,
            sqlite_path=snapshot_path,
            gate_results_path=gate_results_path,
            action_queue_path=action_queue_path,
            review_template_path=_optional_run_artifact(adg_run_id, "adg_review_template_{ts}.json"),
            burndown_path=burndown_table_path,
            p7_paths={
                "structural_outputs": _optional_run_artifact(adg_run_id, "adg_structural_outputs_{ts}.json"),
                "refactor_accelerator": _optional_run_artifact(adg_run_id, "adg_refactor_accelerator_{ts}.json"),
                "graphdb_queries": _optional_run_artifact(adg_run_id, "adg_graphdb_queries_{ts}.json"),
                "runtime_spine": _optional_run_artifact(adg_run_id, "adg_runtime_spine_{ts}.json"),
                "graphdb_projection": _optional_run_artifact(adg_run_id, "adg_graphdb_projection_{ts}.json"),
                "graphdb_metadata": _optional_run_artifact(adg_run_id, "adg_graphdb_metadata_{ts}.json"),
                "graphdb_index": _optional_run_artifact(adg_run_id, "adg_graphdb_index_{ts}.json"),
                "graph_watchlist": _optional_run_artifact(adg_run_id, "adg_graph_watchlist_{ts}.json"),
                "p0_wave_plan": ARTIFACTS_ADG / "issues" / f"p0_remediation_wave_plan_{adg_run_id}.json",
                "dead_code_report": _optional_run_artifact(adg_run_id, "dead_code_zone_control_report_{ts}.json"),
            },
            print_inline=True,
            fail_closed=False,
        )
        if bcg_rc != 0:
            errors.append(f"BCG executive summary emit exit_code={bcg_rc}")
    except ImportError as exc:
        errors.append(f"BCG executive summary module unavailable: {exc}")

    try:
        from tools.reports.adg_burndown_report import (  # noqa: PLC0415
            emit_existing_burndown_markdown,
            emit_mandatory_adg_burndown_report,
        )

        burndown_rc = emit_mandatory_adg_burndown_report(
            gate_results=gate_results_path,
            burndown=burndown_table_path,
            fail_closed=False,
            print_inline=False,
        )
        if burndown_rc != 0:
            errors.append(f"burndown report emit exit_code={burndown_rc}")
        elif emit_existing_burndown_markdown() != 0:
            errors.append("burndown inline replay exit_code=2")
    except ImportError as exc:
        errors.append(f"burndown report module unavailable: {exc}")

    return errors


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
    rc, path = emit_adg_action_queue(
        gate_results=gate_results_path,
        burndown=burndown_table_path,
        sqlite_snapshot=snapshot_path,
        output_path=output_path,
        ts=adg_run_id,
        fail_closed=True,
        repo_root=REPO_ROOT,
    )
    if rc != 0 or path is None or not path.is_file():
        return None, [f"action_queue emit failed exit_code={rc}"]
    try:
        doc = _load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return path, [f"action_queue malformed: {exc}"]
    errors = validate_action_queue(doc)
    return path, [f"action_queue validation: {err}" for err in errors]


def _p0_p1_fix_count(action_queue: dict[str, Any]) -> int:
    count = 0
    for action in action_queue.get("actions") or []:
        if action.get("verdict_cluster") == "FIX" and action.get("sort_band") in {"P0", "P1"}:
            count += 1
    return count


def _repair_counts(action_queue: dict[str, Any], gate_results: dict[str, Any]) -> dict[str, int]:
    from tools.reports.gate_signal_catalog import display_verdict, display_verdict_sub  # noqa: PLC0415
    from tools.reports.adg_bcg_adapter import normalize_bcg_gate_row  # noqa: PLC0415

    counts = _repair_handoff_counts()
    for action in action_queue.get("actions") or []:
        cluster = action.get("verdict_cluster")
        if cluster == "P0_WAVE" and action.get("sort_band") == "P0":
            counts["P0_WAVE"] += 1
            continue
        if cluster != "FIX":
            continue
        if action.get("sort_band") == "P0":
            counts["P0_FIX"] += 1
        elif action.get("sort_band") == "P1":
            counts["P1_FIX"] += 1
    for gate in gate_results.get("gates") or []:
        if (
            gate.get("band") == "P0"
            and display_verdict(gate) == "TRACK"
            and normalize_bcg_gate_row(gate).get("section") == "burn_down"
        ):
            counts["P0_TRACKED_BACKLOG"] += 1
        if gate.get("band") != "P1" or gate.get("enforcement") != "ratchet":
            continue
        sub = display_verdict_sub(gate)
        if sub == "regr":
            counts["P1_RATCHET_REGRESSION"] += 1
        elif sub == "floor":
            counts["P1_RATCHET_FLOOR_BACKLOG"] += 1
    return counts


def _build_repair_handoff(
    *,
    generation_manifest_path: Path | None,
    gate_manifest_path: Path | None,
    generation_manifest: dict[str, Any],
    certification_status: str,
    since_wall_start: float,
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
        artifacts[key] = _artifact_ref(key, path)

    counts = _repair_handoff_counts()
    artifact_status = "incomplete"
    if action_queue_path and gate_results_path:
        try:
            action_queue = _load_json(action_queue_path)
            gate_results = _load_json(gate_results_path)
            counts = _repair_counts(action_queue, gate_results)
            if not errors and certification_status == "clean" and _p0_p1_fix_count(action_queue) == 0:
                artifact_status = "certified"
            elif not errors:
                artifact_status = "repair_ready"
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"handoff artifact malformed during count: {exc}")

    if errors:
        artifact_status = "incomplete"

    handoff = {
        "status": artifact_status,
        "artifacts": artifacts,
        "counts": counts,
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
    except (OSError, json.JSONDecodeError) as exc:
        return None, counts, [f"receipt unreadable or malformed: {exc}"]

    if expected_receipt_sha256 and _sha256(receipt_path) != expected_receipt_sha256:
        errors.append("receipt sha256 mismatch with handoff pointer")
    if receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION:
        errors.append("unsupported or missing schema_version")
    if receipt.get("artifact_status") not in {"certified", "repair_ready"}:
        errors.append(f"artifact_status not consumable: {receipt.get('artifact_status')!r}")
    if receipt.get("artifact_status_source") != "direct":
        errors.append("artifact_status_source must be direct")
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
    if all(key in resolved and resolved[key].is_file() for key in ("gate_results", "action_queue")):
        try:
            gate_results = _load_json(resolved["gate_results"])
            action_queue = _load_json(resolved["action_queue"])
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"handoff JSON artifact malformed: {exc}")
        else:
            try:
                from tools.reports.adg_action_queue import validate_action_queue  # noqa: PLC0415

                errors.extend(f"action_queue validation: {err}" for err in validate_action_queue(action_queue))
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
            if "snapshot" in resolved and not _gate_results_matches_snapshot(gate_results, resolved["snapshot"]):
                errors.append("gate_results snapshot does not match handoff snapshot")
            counts = _repair_counts(action_queue, gate_results)
            counts_recomputed = True

    recorded_counts = handoff.get("counts")
    if not isinstance(recorded_counts, dict):
        errors.append("repair_handoff.counts missing or malformed")
    elif counts_recomputed:
        mismatches = [
            f"{key}: recorded={recorded_counts.get(key)!r} computed={value!r}"
            for key, value in counts.items()
            if recorded_counts.get(key) != value
        ]
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
        except (OSError, json.JSONDecodeError) as exc:
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
                    errors.append("generation_manifest missing snapshot path and run stamp differs from repair_handoff")
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
    except (OSError, json.JSONDecodeError) as exc:
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
    except (OSError, json.JSONDecodeError) as exc:
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
        expected_adg_run_id=expected_adg_run_id or (handoff_run_id if isinstance(handoff_run_id, str) else None),
        expected_receipt_sha256=raw_receipt_digest,
    )
    errors.extend(receipt_errors)
    if receipt and receipt.get("repair_handoff") != handoff_doc.get("repair_handoff"):
        errors.append("receipt repair_handoff differs from immutable handoff")
    return receipt, counts, sorted(set(errors))


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
    except (OSError, json.JSONDecodeError):
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

    env = _os.environ.copy()
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
    print(f"[audit] Stage-1: {env_note}python tools/generate/generate_full_adg.py {' '.join(extra_args)}")
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
        "--snapshot", str(snapshot),
        "--format", fmt,
    ]
    if require_runtime_proof:
        args.append("--require-runtime-proof")
    print(f"[audit] Stage-2: {' '.join(args[1:])}")
    try:
        proc = subprocess.run(  # noqa: S603
            args,
            cwd=str(REPO_ROOT),
            timeout=timeout_s,
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"[audit] Stage-2 FAIL — timed out after {timeout_s}s", file=sys.stderr)
        return 124
    return proc.returncode


def _default_incomplete_handoff() -> dict[str, Any]:
    return {
        "status": "incomplete",
        "artifacts": {},
        "counts": _repair_handoff_counts(),
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
) -> None:
    if not result.adg_run_id:
        return
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
    latest_pointer_path.write_text(json.dumps(latest_pointer, indent=2) + "\n", encoding="utf-8")
    try:
        display = handoff_path.relative_to(REPO_ROOT)
    except ValueError:
        display = handoff_path
    print(f"[audit] wrote repair handoff pointer: {display}")


def _write_receipt(result: WrapperResult, *, producer_artifacts: Path | None = None) -> None:
    if producer_artifacts is None:
        producer_artifacts = _handoff_producer_artifacts_adg()
    handoff_result = _copy_result_for_handoff_root(result, producer_artifacts=producer_artifacts)
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "run_state": {
            "certification_status": handoff_result.certification_status,
            "generator_exit_code": handoff_result.generator_exit_code,
            "report_exit_code": handoff_result.report_exit_code,
            "runtime_proof_status": handoff_result.runtime_proof_status,
            "reasons": handoff_result.reasons,
        },
        "artifact_status": handoff_result.artifact_status,
        "artifact_status_source": handoff_result.artifact_status_source,
        "adg_run_id": handoff_result.adg_run_id,
        "started_at_utc": handoff_result.started_at_utc,
        "completed_at_utc": handoff_result.completed_at_utc,
        "repair_handoff": handoff_result.repair_handoff or _default_incomplete_handoff(),
    }
    receipt_text = json.dumps(payload, indent=2) + "\n"
    RECEIPT_PATH.write_text(receipt_text, encoding="utf-8")
    if handoff_result.adg_run_id:
        immutable_receipt = _immutable_receipt_path(handoff_result.adg_run_id, artifacts_adg=producer_artifacts)
        immutable_receipt.parent.mkdir(parents=True, exist_ok=True)
        _write_immutable_text(immutable_receipt, receipt_text, label="audit pipeline receipt")
        _write_repair_handoff_pointer(
            handoff_result,
            receipt_path=immutable_receipt,
            receipt_sha256=_sha256(immutable_receipt),
            artifacts_adg=producer_artifacts,
        )
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
    gen_rc = _run_generator(
        extra_args=extra,
        timeout_s=generator_timeout_s,
        certification_mode=certification_mode,
    )
    if gen_rc != 0:
        if certification_mode and not diagnostic_allow_failed_generator:
            reasons.append(f"generator exit_code={gen_rc}")

    # Locate manifests.
    gen_manifest_path = _find_generation_manifest(wall_start)
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
        except (OSError, json.JSONDecodeError) as e:
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

    # Mandatory BCG + burndown inline ordering. Use same-run artifacts only;
    # when dispatcher output is absent, emit degraded artifacts that remain
    # blocked for downstream repair consumption.
    mandatory_output_errors = _emit_mandatory_run_outputs(
        snapshot_path=snapshot_path_for_outputs,
        adg_run_id=adg_run_id_for_outputs,
        since_wall_start=wall_start,
        generator_exit_code=gen_rc,
    )
    if certification_mode:
        reasons.extend(mandatory_output_errors)

    # Plane 2 — three-graph manifest (certification; generator skips via env).
    if certification_mode and snapshot_raw and gate_manifest_path:
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
            except (OSError, json.JSONDecodeError):
                pass

    # Cross-check required gates (certification mode only).
    if certification_mode and gate_manifest:
        reasons.extend(_cross_check_required_gates(gate_manifest))

    # Plane-3 dispatcher failure (generator records + exits; double-check JSON).
    if certification_mode:
        disp_candidates = sorted(
            ARTIFACTS_ADG.glob("adg_gate_results_*.json"),
            key=lambda p: p.stat().st_mtime,
        )
        for disp_candidate in reversed(disp_candidates):
            try:
                disp_payload = _load_json(disp_candidate)
                if _json_has_degraded_fallback_marker(disp_candidate):
                    continue
                if int(disp_payload.get("overall_exit_code", 0)) != 0:
                    reasons.append(
                        f"adg_gate_dispatcher overall_exit_code={disp_payload.get('overall_exit_code')}"
                    )
                    break
                break
            except (OSError, json.JSONDecodeError):
                reasons.append("adg_gate_dispatcher results unreadable")
                break

    # Runtime-proof gate.
    if require_runtime_proof and runtime_proof_status != "attested":
        reasons.append(
            f"--require-runtime-proof set but runtime_proof_status={runtime_proof_status!r}"
        )

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

    # ADR-081: unified enforcement report (planes 1–3 rollup).
    enforcement_path: Path | None = None
    try:
        from tools.adg.integration.enforcement_report import (  # noqa: PLC0415
            build_enforcement_report,
            write_enforcement_report,
        )

        rollup_path = REPO_ROOT / "docs" / "reports" / "adg" / "three_graph_test_rollup.json"
        disp_candidates = sorted(
            ARTIFACTS_ADG.glob("adg_gate_results_*.json"),
            key=lambda p: p.stat().st_mtime,
        )
        disp_path = disp_candidates[-1] if disp_candidates else None
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
        if certification_mode and report.get("certified_rollup") == "NOT_CERTIFIED":
            reasons.append("enforcement_report certified_rollup=NOT_CERTIFIED")
    except (ImportError, OSError, TypeError, ValueError) as exc:
        if certification_mode:
            reasons.append(f"enforcement_report build failed: {exc}")

    # Classify certification_status.
    if not certification_mode:
        status = "diagnostic_only"
    elif reasons:
        status = "failed"
    else:
        status = "clean"

    artifact_status, repair_handoff, _handoff_errors = _build_repair_handoff(
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
    retention_run_id = adg_run_id or adg_run_id_for_outputs or _find_recent_sqlite_run_stamp(
        since_wall_start=wall_start,
    )
    _run_retention_sweep(retention_run_id)
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
    )
    _write_receipt(result, producer_artifacts=producer_artifacts)
    if enforcement_path is not None:
        print(f"[audit] enforcement report: {enforcement_path}")

    # Render summary.
    print(f"[audit] certification_status={status}")
    print(f"[audit] artifact_status={artifact_status}")
    print(f"[audit] generator_exit_code={gen_rc}  report_exit_code={report_rc}")
    print(f"[audit] runtime_proof_status={runtime_proof_status}")
    if reasons:
        print("[audit] reasons:")
        for r in reasons:
            print(f"  - {r}")
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
    parser.add_argument("--generator-arg", action="append", default=[],
                        help="Extra arg to pass through to generate_full_adg.py (repeatable).")
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

    if args.mode == "diagnostic":
        # Diagnostic mode: generator failure is tolerated if flag set; otherwise propagate.
        if args.diagnostic_allow_failed_generator:
            return 0
        return 1 if (result.generator_exit_code or 0) != 0 else 0

    # Certification mode: any reason = non-zero.
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
