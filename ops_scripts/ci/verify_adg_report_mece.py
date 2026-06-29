"""Verify generated ADG executive reports use MECE gate ownership.

The gate is intentionally artifact-level: report wording can change, but the
generated JSON and markdown must not blend decision gates, work queues,
watchlists, and severity inventory into one pseudo-priority list.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DOCS_DIR = REPO_ROOT / "docs" / "reports" / "adg"
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
        _gate_id(row)
        for section in ("fix_now", "burn_down")
        for row in sections[section]
        if _gate_id(row)
    }
    overlap = sorted(watchlist & work)
    for gate_id in overlap:
        errors.append(f"KPI/watchlist gate {gate_id!r} also appears in a work section")
    return errors


def _validate_ranked_actions(summary: dict[str, Any], adapter: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    actions = list((summary.get("canonical_next_best_actions") or {}).get("rows") or [])
    for row in actions:
        action_type = str(row.get("action_type") or row.get("decision") or "")
        move = _row_move(row).lower()
        if action_type in DECISION_GATE_ACTION_TYPES or move in DECISION_GATE_MOVES:
            errors.append(f"decision gate {move!r} appears in canonical_next_best_actions")

    mece = summary.get("gate_mece_summary") or {}
    for row in mece.get("decision_gates") or []:
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
        default=DEFAULT_DOCS_DIR / "adg_bcg_executive_summary_latest.json",
    )
    parser.add_argument(
        "--adapter-json",
        type=Path,
        default=DEFAULT_DOCS_DIR / "adg_bcg_adapter_latest.json",
    )
    parser.add_argument(
        "--summary-md",
        type=Path,
        default=DEFAULT_DOCS_DIR / "adg_bcg_executive_summary_latest.md",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable result.")
    args = parser.parse_args(argv)

    summary = _load_json(args.summary_json)
    adapter = _load_json(args.adapter_json)
    summary_md = args.summary_md.read_text(encoding="utf-8") if args.summary_md.is_file() else ""
    errors = validate(summary, adapter, summary_md)
    result = {
        "status": "FAIL" if errors else "PASS",
        "summary_json": str(args.summary_json),
        "adapter_json": str(args.adapter_json),
        "summary_md": str(args.summary_md),
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
