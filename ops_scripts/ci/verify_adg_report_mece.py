"""Verify generated ADG executive reports use MECE gate ownership.

The gate is intentionally artifact-level: report wording can change, but the
generated JSON and markdown must not blend decision gates, work queues,
watchlists, and severity inventory into one pseudo-priority list.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE_MANIFEST = REPO_ROOT / "artifacts" / "adg" / "adg_run_output_bundle_latest.json"
BUNDLE_SCHEMA_VERSION = "adg-run-output-bundle/v1"
PUBLICATION_SCHEMA_VERSION = "adg-output-publication/v1"
REQUIRED_OUTPUT_FORMATS = {
    "bcg_gate_adapter": ("adg_bcg_adapter_{run_id}.json", "adg_bcg_adapter_{run_id}.md"),
    "burndown_report": ("adg_burndown_report_{run_id}.md",),
    "action_queue": ("adg_action_queue_{run_id}.json",),
    "review_template": ("adg_review_template_{run_id}.json", "adg_review_template_{run_id}.yaml"),
    "bcg_executive_summary": (
        "adg_bcg_executive_summary_{run_id}.json",
        "adg_bcg_executive_summary_{run_id}.yaml",
        "adg_bcg_executive_summary_{run_id}.md",
    ),
    "latest_publication": ("adg_output_publication_{run_id}.json",),
}
P3_HYGIENE_IDS = {
    "S4_unused_imports_ratchet",
    "Q2_cyclomatic_complexity_ratchet",
    "M1_module_loc_ratchet",
}
DECISION_GATE_ACTION_TYPES = {"decision_gate", "repair_reporting", "repair_runtime"}
DECISION_GATE_MOVES = {
    "repair graph/report consistency",
    "repair missing decision-grade adg artifact",
    "restore decision-grade artifacts",
    "fix failing runtime proof",
}


@dataclass(frozen=True)
class ReportInputs:
    """Three same-run report artifacts selected from one sealed bundle."""

    summary_json: Path
    adapter_json: Path
    summary_md: Path
    run_id: str


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _declared_path(raw: object, *, repo_root: Path) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("artifact path must be a non-empty string")
    candidate = Path(raw)
    return (candidate if candidate.is_absolute() else repo_root / candidate).resolve()


def _validate_source_run_ids(*, summary: dict[str, Any], adapter: dict[str, Any], run_id: str) -> None:
    summary_run = summary.get("run")
    if not isinstance(summary_run, dict) or summary_run.get("run_id") != run_id:
        raise ValueError("executive summary run_id does not match output bundle")

    adapter_source = adapter.get("source")
    if isinstance(adapter_source, dict) and "run_id" in adapter_source:
        if adapter_source.get("run_id") != run_id:
            raise ValueError("BCG adapter source run_id does not match output bundle")


def load_bundle_report_inputs(
    manifest_path: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> ReportInputs:
    """Resolve exact MECE inputs from a digest-bound, complete output bundle."""
    manifest_path = manifest_path.resolve()
    artifact_dir = manifest_path.parent.resolve()
    manifest = _load_json(manifest_path)
    if manifest.get("schema_version") != BUNDLE_SCHEMA_VERSION:
        raise ValueError("output bundle schema mismatch")
    if manifest.get("status") != "complete":
        raise ValueError(f"output bundle status is not complete: {manifest.get('status')!r}")
    run_id = manifest.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("output bundle run_id is missing")

    artifact_rows = manifest.get("artifacts")
    if not isinstance(artifact_rows, list) or not artifact_rows:
        raise ValueError("output bundle artifact inventory is missing")
    inventory: dict[Path, str] = {}
    for row in artifact_rows:
        if not isinstance(row, dict) or set(row) != {"path", "sha256"}:
            raise ValueError("output bundle artifact inventory row is invalid")
        path = _declared_path(row.get("path"), repo_root=repo_root)
        digest = row.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError(f"output bundle artifact digest is invalid: {path}")
        if path in inventory:
            raise ValueError(f"output bundle artifact path is duplicated: {path}")
        if not path.is_relative_to(artifact_dir):
            raise ValueError(f"output bundle artifact escapes the ADG artifact directory: {path}")
        if not path.is_file() or path.stat().st_size <= 0:
            raise ValueError(f"output bundle artifact is missing or empty: {path}")
        if _sha256(path) != digest:
            raise ValueError(f"output bundle artifact digest mismatch: {path}")
        inventory[path] = digest

    gate_rows = manifest.get("gates")
    if not isinstance(gate_rows, list):
        raise ValueError("output bundle gates are missing")
    gates: dict[str, dict[str, Any]] = {}
    gate_fields = {"key", "required", "status", "producer_exit_code", "paths", "diagnostic"}
    for row in gate_rows:
        if not isinstance(row, dict) or set(row) != gate_fields:
            raise ValueError("output bundle gate row is invalid")
        key = row.get("key")
        if not isinstance(key, str) or not key:
            raise ValueError("output bundle gate key is invalid")
        if key in gates:
            raise ValueError(f"output bundle gate is duplicated: {key}")
        if not isinstance(row.get("required"), bool):
            raise ValueError(f"output bundle gate required flag is invalid: {key}")
        if row.get("status") not in {"pass", "fail", "blocked"}:
            raise ValueError(f"output bundle gate status is invalid: {key}")
        exit_code = row.get("producer_exit_code")
        if exit_code is not None and (not isinstance(exit_code, int) or isinstance(exit_code, bool)):
            raise ValueError(f"output bundle gate producer exit code is invalid: {key}")
        raw_paths = row.get("paths")
        if not isinstance(raw_paths, list) or not all(
            isinstance(raw, str) and raw.strip() for raw in raw_paths
        ):
            raise ValueError(f"output bundle gate paths are invalid: {key}")
        if not isinstance(row.get("diagnostic"), str):
            raise ValueError(f"output bundle gate diagnostic is invalid: {key}")
        gates[key] = row

    missing = sorted(set(REQUIRED_OUTPUT_FORMATS) - set(gates))
    if missing:
        raise ValueError(f"output bundle required gates are missing: {', '.join(missing)}")

    paths_by_gate: dict[str, set[Path]] = {}
    for key, gate in gates.items():
        if gate["required"] is not True:
            continue
        if gate["status"] != "pass" or gate["producer_exit_code"] != 0:
            raise ValueError(f"output bundle required gate did not pass cleanly: {key}")
        if not gate["paths"]:
            raise ValueError(f"output bundle required gate has no artifact path: {key}")
        for raw in gate["paths"]:
            path = _declared_path(raw, repo_root=repo_root)
            if path not in inventory:
                raise ValueError(f"output bundle gate artifact is not digest-inventoried: {path}")

    for key, templates in REQUIRED_OUTPUT_FORMATS.items():
        gate = gates[key]
        if gate.get("required") is not True:
            raise ValueError(f"output bundle required gate is not marked required: {key}")
        raw_paths = gate.get("paths")
        if not isinstance(raw_paths, list) or len(raw_paths) != len(templates):
            raise ValueError(f"output bundle required gate format count mismatch: {key}")
        declared = {_declared_path(raw, repo_root=repo_root) for raw in raw_paths}
        expected = {(artifact_dir / template.format(run_id=run_id)).resolve() for template in templates}
        if declared != expected:
            raise ValueError(f"output bundle required gate paths do not match run {run_id}: {key}")
        for path in declared:
            if path not in inventory:
                raise ValueError(f"output bundle gate artifact is not digest-inventoried: {path}")
        paths_by_gate[key] = declared

    publication_path = next(iter(paths_by_gate["latest_publication"]))
    publication = _load_json(publication_path)
    if publication.get("schema_version") != PUBLICATION_SCHEMA_VERSION:
        raise ValueError("output bundle publication receipt schema mismatch")
    if publication.get("run_id") != run_id:
        raise ValueError("output bundle publication receipt run_id mismatch")
    if publication.get("mutable_report_aliases_published") is not False:
        raise ValueError("output bundle publication used mutable report aliases")
    publication_rows = publication.get("artifacts")
    if not isinstance(publication_rows, list):
        raise ValueError("output bundle publication artifact set is missing")
    published: dict[Path, str] = {}
    for row in publication_rows:
        if not isinstance(row, dict) or set(row) != {"path", "sha256"}:
            raise ValueError("output bundle publication artifact row is invalid")
        path = _declared_path(row.get("path"), repo_root=repo_root)
        digest = row.get("sha256")
        if path in published:
            raise ValueError(f"output bundle publication artifact is duplicated: {path}")
        if path not in inventory or digest != inventory[path]:
            raise ValueError(f"output bundle publication artifact is not digest-bound: {path}")
        published[path] = digest
    expected_published = set().union(
        paths_by_gate["bcg_gate_adapter"],
        paths_by_gate["burndown_report"],
        paths_by_gate["review_template"],
        paths_by_gate["bcg_executive_summary"],
    )
    if set(published) != expected_published:
        raise ValueError("output bundle publication artifact set is incomplete or mixed-run")

    summary_json = artifact_dir / f"adg_bcg_executive_summary_{run_id}.json"
    summary_md = artifact_dir / f"adg_bcg_executive_summary_{run_id}.md"
    adapter_json = artifact_dir / f"adg_bcg_adapter_{run_id}.json"
    summary = _load_json(summary_json)
    adapter = _load_json(adapter_json)
    _validate_source_run_ids(summary=summary, adapter=adapter, run_id=run_id)
    return ReportInputs(
        summary_json=summary_json,
        adapter_json=adapter_json,
        summary_md=summary_md,
        run_id=run_id,
    )


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a JSON object")
    return data


def _rows_by_section(adapter: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    sections = adapter.get("sections") or {}
    return {
        name: list((sections.get(name) or {}).get("rows") or [])
        for name in ("fix_now", "burn_down", "kpi_watchlist", "clear")
    }


def _gate_id(row: dict[str, Any]) -> str:
    return str(row.get("gate_id") or row.get("scope") or "").strip()


def _row_move(row: dict[str, Any]) -> str:
    return str(row.get("move") or row.get("action") or row.get("work") or "").strip()


def _validate_unique_gate_ownership(adapter: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    owner_by_gate: dict[str, str] = {}
    for section, rows in _rows_by_section(adapter).items():
        for row in rows:
            gate_id = _gate_id(row)
            if not gate_id:
                continue
            previous = owner_by_gate.setdefault(gate_id, section)
            if previous != section:
                errors.append(f"gate {gate_id!r} appears in both {previous!r} and {section!r}")
    return errors


def _validate_watchlist_not_work(adapter: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sections = _rows_by_section(adapter)
    watchlist = {_gate_id(row) for row in sections["kpi_watchlist"] if _gate_id(row)}
    work = {
        _gate_id(row) for section in ("fix_now", "burn_down") for row in sections[section] if _gate_id(row)
    }
    overlap = sorted(watchlist & work)
    for gate_id in overlap:
        errors.append(f"KPI/watchlist gate {gate_id!r} also appears in a work section")
    return errors


def _validate_ranked_actions(summary: dict[str, Any], adapter: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    actions = list((summary.get("canonical_next_best_actions") or {}).get("rows") or [])
    decision_gates = list((summary.get("gate_mece_summary") or {}).get("decision_gates") or [])
    for row in actions:
        action_type = str(row.get("action_type") or row.get("decision") or "")
        move = _row_move(row).lower()
        if action_type in DECISION_GATE_ACTION_TYPES or move in DECISION_GATE_MOVES:
            errors.append(f"decision gate {move!r} appears in canonical_next_best_actions")

    for row in decision_gates:
        gate_move = _row_move(row)
        for action in actions:
            if gate_move and gate_move == _row_move(action):
                errors.append(f"decision gate {gate_move!r} also appears in ranked work actions")

    fix_rows = _rows_by_section(adapter)["fix_now"]
    live_p0 = {_gate_id(row) for row in fix_rows if str(row.get("band") or "").upper() == "P0"}
    if not live_p0:
        return errors
    first_p0_index = None
    for index, row in enumerate(actions):
        if str(row.get("scope") or "") in live_p0:
            first_p0_index = index
            break
    if first_p0_index is None:
        ranked_p3 = sorted(
            str(row.get("scope") or "") for row in actions if str(row.get("scope") or "") in P3_HYGIENE_IDS
        )
        for scope in ranked_p3:
            errors.append(f"P3 hygiene gate {scope!r} outranks live P0 gates")
        if not decision_gates and not ranked_p3:
            errors.append("P0 live FIX gates exist but none appear in canonical_next_best_actions")
        return errors
    for index, row in enumerate(actions):
        scope = str(row.get("scope") or "")
        if index < first_p0_index and scope in P3_HYGIENE_IDS:
            errors.append(f"P3 hygiene gate {scope!r} outranks live P0 gates")
    return errors


def _validate_severity_inventory_not_actions(summary: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    actions = list((summary.get("canonical_next_best_actions") or {}).get("rows") or [])
    for row in actions:
        action_type = str(row.get("action_type") or "")
        scope = str(row.get("scope") or "")
        move = _row_move(row).lower()
        if action_type == "severity_inventory" or scope in {"P0", "P1", "P2", "P3"}:
            errors.append(f"severity inventory row {scope!r} appears in ranked work actions")
        if "audit net" in move or "severity inventory" in move:
            errors.append(f"severity inventory wording appears as ranked work: {move!r}")
    return errors


def _validate_markdown(summary_md: str) -> list[str]:
    errors: list[str] = []
    lowered = summary_md.lower()
    if "decision gate:" not in lowered:
        errors.append("BCG markdown is missing a Decision gate section")
    if "fix now:" not in lowered:
        errors.append("BCG markdown is missing a Fix now section")
    if "| 1 | repair graph/report consistency |" in lowered:
        errors.append("BCG markdown ranks report consistency as priority work")
    return errors


def validate(summary: dict[str, Any], adapter: dict[str, Any], summary_md: str = "") -> list[str]:
    errors: list[str] = []
    errors.extend(_validate_unique_gate_ownership(adapter))
    errors.extend(_validate_watchlist_not_work(adapter))
    errors.extend(_validate_ranked_actions(summary, adapter))
    errors.extend(_validate_severity_inventory_not_actions(summary))
    if summary_md:
        errors.extend(_validate_markdown(summary_md))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary-json",
        type=Path,
    )
    parser.add_argument(
        "--adapter-json",
        type=Path,
    )
    parser.add_argument(
        "--summary-md",
        type=Path,
    )
    parser.add_argument(
        "--bundle-manifest",
        type=Path,
        default=DEFAULT_BUNDLE_MANIFEST,
        help="Sealed latest bundle used unless all three report paths are explicitly supplied.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable result.")
    args = parser.parse_args(argv)

    explicit_override = all(
        path is not None for path in (args.summary_json, args.adapter_json, args.summary_md)
    )
    errors: list[str] = []
    run_id: str | None = None
    try:
        if explicit_override:
            summary_json = args.summary_json.resolve()
            adapter_json = args.adapter_json.resolve()
            summary_md_path = args.summary_md.resolve()
            mode = "explicit"
        else:
            inputs = load_bundle_report_inputs(args.bundle_manifest)
            summary_json = inputs.summary_json
            adapter_json = inputs.adapter_json
            summary_md_path = inputs.summary_md
            run_id = inputs.run_id
            mode = "bundle"
        summary = _load_json(summary_json)
        adapter = _load_json(adapter_json)
        summary_md = summary_md_path.read_text(encoding="utf-8")
        errors.extend(validate(summary, adapter, summary_md))
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        mode = "explicit" if explicit_override else "bundle"
        summary_json = args.summary_json
        adapter_json = args.adapter_json
        summary_md_path = args.summary_md
        errors.append(str(exc))
    result = {
        "status": "FAIL" if errors else "PASS",
        "mode": mode,
        "run_id": run_id,
        "bundle_manifest": str(args.bundle_manifest) if mode == "bundle" else None,
        "summary_json": str(summary_json) if summary_json is not None else None,
        "adapter_json": str(adapter_json) if adapter_json is not None else None,
        "summary_md": str(summary_md_path) if summary_md_path is not None else None,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif errors:
        print("[verify_adg_report_mece] FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print("[verify_adg_report_mece] PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
