"""Emit a mandatory machine-readable ADG run review template.

The full JSON file is the review packet. A compact markdown projection is also
printed inline after ``generate_full_adg`` so the operator sees the important
review output in chat without opening the JSON file.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

from tools.generate.core.helpers import _write_text_artifact
from tools.reports.adg_decision_synthesis import (
    after_green_plan,
    artifact_consistency_status,
    band_decision_summary,
)
from tools.reports.exhaustive_adg_ci_report import MV_DESCRIPTIONS
from tools.reports.gate_signal_catalog import (
    display_verdict,
    display_verdict_sub,
    format_gate_signal,
    recommended_next_step,
    what_counts,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"
DOCS_ADG = REPO_ROOT / "docs" / "reports" / "adg"
REVIEW_TEMPLATE_LATEST = ARTIFACTS_ADG / "adg_review_template_latest.json"
REVIEW_TEMPLATE_DOCS_LATEST = DOCS_ADG / "adg_review_template_latest.json"
REVIEW_TEMPLATE_YAML_LATEST = ARTIFACTS_ADG / "adg_review_template_latest.yaml"
REVIEW_TEMPLATE_DOCS_YAML_LATEST = DOCS_ADG / "adg_review_template_latest.yaml"

GATE_SHORT_NAMES = {
    "G_REACH_l0_reachability": "G_REACH",
    "S2_uwg_bypass_ratchet": "S2_UWG",
    "L2_lpg_drift_ratchet": "L2_LPG",
    "3_write_sovereignty": "write_sovereignty",
    "J1_canonical_pipeline_wiring": "pipeline_wiring",
    "C3_silent_writes_ratchet": "C3_silent_writes",
    "E1_trace_stub_module": "E1_trace_stub",
    "B2_layer_skip_ratchet": "B2_layer_skip",
    "I2_replay_surface_gaps_ratchet": "I2_replay_gaps",
    "F1_untyped_seam_ratchet": "F1_untyped_seam",
    "S4_unused_imports_ratchet": "S4_unused_imports",
    "Q2_cyclomatic_complexity_ratchet": "Q2_complexity",
    "M1_module_loc_ratchet": "M1_module_loc",
    "D1_layer_doc_binding": "D1_layer_doc",
    "D2_role_duplication_warn": "D2_role_duplication",
}

BAND_PRIORITY = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
ATTACK_CLASS_PRIORITY = {
    "Fix now": 0,
    "Burn down ratchets": 1,
    "Open non-ratchet work": 2,
    "Severity audit": 3,
}

MV_GATE_DRIVERS: dict[str, tuple[str, ...]] = {
    "mv_actionable_surface_without_schema": ("M_taint_actionable_ratchet",),
    "mv_authority_boundary_breaches": ("2_authority_boundary",),
    "mv_capability_and_egress_gaps": ("4_capability_egress",),
    "mv_determinism_provenance_drift": ("6_determinism_provenance",),
    "mv_exit_disposition_coverage": ("I1_exit_disposition_ratchet",),
    "mv_gateway_bypass_paths": ("C1_uwg_bypass_pview",),
    "mv_graph_vs_report_mismatches": ("H4_mv_staleness_ratchet",),
    "mv_heal_retry_exit_gaps": ("8_trace_replay_eval",),
    "mv_hitl_reclearance_gaps": ("11_architecture_witness",),
    "mv_l2_phase_coverage": ("7_lifecycle_coverage",),
    "mv_new_write_bypass_paths": ("S2_uwg_bypass_ratchet", "3_write_sovereignty"),
    "mv_prompt_assembly_wiring_gaps": ("12_prompt_assembly_wiring",),
    "mv_replay_surface_gaps": ("I2_replay_surface_gaps_ratchet",),
    "mv_runtime_spine_gaps": ("11_architecture_witness",),
    "mv_structured_output_gaps": ("P_structured_output_ratchet",),
    "mv_trace_replay_eval_gaps": ("8_trace_replay_eval",),
    "mv_untrusted_text_to_action_risk": ("5_text_to_action",),
    "mv_write_sovereignty_paths": ("3_write_sovereignty", "S2_uwg_bypass_ratchet"),
}

MV_ANALYST_SIGNALS: dict[str, str] = {
    "mv_debt_concentration_hotspots": "Rank refactor slices after red gates clear.",
    "mv_dependency_cone_risk": "Prefer fixes that reduce downstream blast radius.",
    "mv_exemptions_near_critical_paths": "Audit guardian exceptions near critical paths.",
    "mv_graph_chokepoint_bridges": "Avoid risky edits at single-bridge chokepoints without tests.",
    "mv_graph_critical_path_blast_radius": "Choose high-blast-radius seams for careful refactor/test work.",
    "mv_graph_reverse_dependency_hotspots": "Treat highly imported hubs as test-required change areas.",
    "mv_high_fan_in_out_with_defects": "Prioritize defects in high fan-in/fan-out symbols.",
    "mv_hotspot_centrality": "Use as structural leverage ranking for refactor waves.",
    "mv_hotspot_coverage_risk": "Use as first-class testing-hotspot next-step input.",
    "mv_modified_area_regressions": "Check defects in files touched by this run.",
    "mv_new_cross_layer_dependencies": "Review newly introduced layer drift before it becomes baseline debt.",
    "mv_new_provider_surfaces": "Review new provider surfaces for egress/control gaps.",
    "mv_newly_introduced_critical_paths": "Inspect newly created critical-path edges for regressions.",
    "mv_path_criticality_rollup": "Use as impact weighting for any fix or refactor slice.",
    "mv_repeated_p3_near_critical_paths": "Promote recurring style debt near critical paths when planning P3 work.",
    "mv_snapshot_integrity_anomalies": "Treat as generator/ingest health signal, not product-code work by itself.",
}


def _utcnow_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data: dict[str, Any] = json.load(fh)
    return data


def _dump_yaml(doc: dict[str, Any]) -> str:
    try:
        import yaml  # noqa: PLC0415

        return yaml.safe_dump(doc, sort_keys=False, allow_unicode=False)
    except ImportError:
        # JSON is valid YAML, so this keeps the YAML artifact mandatory even in
        # stripped-down environments.
        return json.dumps(doc, indent=2, sort_keys=False) + "\n"


def _safe_load_json(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.is_file():
        return None
    return _load_json(path)


def _resolve_latest(pattern: str, root: Path = ARTIFACTS_ADG) -> Path | None:
    candidates = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None


def _repo_rel(path: Path | None, repo_root: Path = REPO_ROOT) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(repo_root.resolve()))
    except ValueError:
        return str(resolved)


def _inline_bypassed() -> bool:
    return os.environ.get("ADG_REVIEW_TEMPLATE_INLINE_BYPASS", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _md_cell(value: Any, *, limit: int | None = None) -> str:
    text = str(value or "").replace("\n", " ").replace("|", "\\|").strip()
    if limit is not None and len(text) > limit:
        return text[: max(0, limit - 3)].rstrip() + "..."
    return text


def _sha256(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _artifact_ref(key: str, path: Path | None, *, required: bool = False) -> dict[str, Any]:
    exists = bool(path and path.is_file())
    return {
        "artifact_key": key,
        "path": _repo_rel(path),
        "exists": exists,
        "required": required,
        "sha256": _sha256(path) if exists else None,
    }


def _fmt_int(value: Any) -> str:
    return f"{int(value or 0):,}"


def _int_value(value: Any, *, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _float_value(value: Any, *, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _plural(value: int, singular: str, plural: str | None = None) -> str:
    word = singular if value == 1 else (plural or f"{singular}s")
    return f"{_fmt_int(value)} {word}"


def _tracked_record_label(gates: int, records: int) -> str:
    return f"{_plural(gates, 'gate')} / {_plural(records, 'tracked record')}"


def _short_gate_id(gate_id: str) -> str:
    if gate_id in GATE_SHORT_NAMES:
        return GATE_SHORT_NAMES[gate_id]
    label = gate_id
    for suffix in ("_ratchet", "_warn"):
        if label.endswith(suffix):
            label = label[: -len(suffix)]
    return label


def _gate_action_item(gate: dict[str, Any]) -> dict[str, Any]:
    gate_id = str(gate.get("gate_id", "?"))
    return {
        "gate_id": gate_id,
        "label": _short_gate_id(gate_id),
        "records": int(gate.get("violation_count") or 0),
        "sub": display_verdict_sub(gate),
        "record_type": what_counts(gate_id, str(gate.get("gate_class") or "")),
    }


def _format_action_items(items: list[dict[str, Any]], *, max_items: int = 5) -> str:
    if not items:
        return "None"
    sorted_items = sorted(
        items,
        key=lambda row: (-int(row.get("records", 0) or 0), str(row.get("label", ""))),
    )
    if len(sorted_items) <= max_items:
        return "; ".join(
            f"`{_md_cell(item.get('label'))}` {_fmt_int(item.get('records', 0))}"
            for item in sorted_items
        )
    visible = sorted_items[:3]
    visible_text = "; ".join(
        f"`{_md_cell(item.get('label'))}` {_fmt_int(item.get('records', 0))}"
        for item in visible
    )
    remaining = len(sorted_items) - len(visible)
    total = sum(int(item.get("records", 0) or 0) for item in sorted_items)
    return f"{visible_text}; +{remaining} more = {_fmt_int(total)} total"


def _format_bullet_items(items: list[dict[str, Any]], *, max_items: int = 5) -> str:
    if not items:
        return "none"
    sorted_items = sorted(
        items,
        key=lambda row: (-int(row.get("records", 0) or 0), str(row.get("label", ""))),
    )
    visible = sorted_items[:max_items]
    text = "; ".join(
        f"`{_md_cell(item.get('label'))}` {_fmt_int(item.get('records', 0))}"
        for item in visible
    )
    if len(sorted_items) > max_items:
        remaining = len(sorted_items) - max_items
        total = sum(int(item.get("records", 0) or 0) for item in sorted_items)
        text += f"; +{remaining} more ({_fmt_int(total)} total)"
    return text


def _allowed_floor_display(gate: dict[str, Any]) -> str:
    enforcement = str(gate.get("enforcement", ""))
    baseline = gate.get("baseline_count")
    sub = display_verdict_sub(gate)
    if enforcement == "ratchet":
        if baseline is not None:
            return str(baseline)
        return "missing seed" if sub == "seed" else "unseeded"
    if enforcement == "warn":
        return "advisory"
    if sub == "inventory":
        return "warn inventory"
    return "0"


def _empty_band_row(band: str) -> dict[str, Any]:
    return {
        "band": band,
        "status": "PASS",
        "fix_gates": 0,
        "fix_records": 0,
        "tracked_gates": 0,
        "tracked_records": 0,
        "tracked_record_label": _tracked_record_label(0, 0),
        "ratchet_floor_gates": 0,
        "ratchet_floor_records": 0,
        "ratchet_floor_items": [],
        "ratchet_burn_down": "None",
        "cleanup_gates": 0,
        "cleanup_records": 0,
        "cleanup_items": [],
        "cleanup_backlog": "None",
        "open_non_ratchet_work": "None",
        "clear_gates": 0,
        "read_it_as": "green; no backlog records",
        "next_move": "no action",
    }


def _finalize_band_row(row: dict[str, Any]) -> dict[str, Any]:
    if int(row["fix_gates"]):
        row["status"] = "BLOCKED"
        row["read_it_as"] = "red gates present"
        row["next_move"] = "fix red gates first"
    elif int(row["tracked_gates"]) or int(row["tracked_records"]):
        row["status"] = "PASS"
        row["read_it_as"] = "green; ratchet burn-down/open work remains"
        if int(row["ratchet_floor_records"]) and int(row["cleanup_records"]):
            row["next_move"] = "1) burn down ratchets; 2) close open non-ratchet work"
        elif int(row["ratchet_floor_records"]):
            row["next_move"] = "burn down listed ratchets"
        else:
            row["next_move"] = "close open non-ratchet work"
    row["tracked_record_label"] = _tracked_record_label(
        int(row["tracked_gates"]),
        int(row["tracked_records"]),
    )
    row["ratchet_burn_down"] = _format_action_items(list(row["ratchet_floor_items"]))
    row["cleanup_backlog"] = _format_action_items(list(row["cleanup_items"]))
    row["open_non_ratchet_work"] = row["cleanup_backlog"]
    return row


def _band_status_rows(gates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = {band: _empty_band_row(band) for band in ("P0", "P1", "P2", "P3")}
    for gate in gates:
        band = str(gate.get("band", "P3"))
        row = rows.setdefault(band, _empty_band_row(band))
        records = int(gate.get("violation_count") or 0)
        action = display_verdict(gate)
        if action == "FIX":
            row["fix_gates"] += 1
            row["fix_records"] += records
        elif action == "TRACK":
            row["tracked_gates"] += 1
            row["tracked_records"] += records
            item = _gate_action_item(gate)
            if display_verdict_sub(gate) == "floor":
                row["ratchet_floor_gates"] += 1
                row["ratchet_floor_records"] += records
                row["ratchet_floor_items"].append(item)
            else:
                row["cleanup_gates"] += 1
                row["cleanup_records"] += records
                row["cleanup_items"].append(item)
        else:
            row["clear_gates"] += 1
    return [_finalize_band_row(rows[band]) for band in ("P0", "P1", "P2", "P3")]


def _gate_rows(gates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    band_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    action_order = {"FIX": 0, "TRACK": 1, "CLEAR": 2}
    out: list[dict[str, Any]] = []
    for gate in sorted(
        gates,
        key=lambda g: (
            band_order.get(str(g.get("band", "P3")), 9),
            action_order.get(display_verdict(g), 9),
            str(g.get("gate_id", "")),
        ),
    ):
        gate_id = str(gate.get("gate_id", "?"))
        gate_class = str(gate.get("gate_class") or "")
        out.append(
            {
                "gate_id": gate_id,
                "band": gate.get("band", "?"),
                "enforcement": gate.get("enforcement", "?"),
                "action": display_verdict(gate),
                "sub": display_verdict_sub(gate),
                "records": int(gate.get("violation_count") or 0),
                "record_type": what_counts(gate_id, gate_class),
                "allowed_floor": _allowed_floor_display(gate),
                "signal": format_gate_signal(gate),
                "next_best_action": recommended_next_step(gate),
            }
        )
    return out


def _severity_inventory(burndown: dict[str, Any]) -> list[dict[str, Any]]:
    summary = burndown.get("summary") or {}
    rows: list[dict[str, Any]] = []
    for band in ("P0", "P1", "P2", "P3"):
        row = summary.get(band) or {}
        rows.append(
            {
                "band": band,
                "label": row.get("label", "?"),
                "gross": int(row.get("gross", 0) or 0),
                "guardian": int(row.get("guardian", 0) or 0),
                "net": int(row.get("net", 0) or 0),
                "diff_vs_prev": int(row.get("diff", 0) or 0),
                "formula": "net = gross - guardian",
            }
        )
    return rows


def _action_rows(action_queue: dict[str, Any] | None, *, limit: int = 10) -> list[dict[str, Any]]:
    if not action_queue:
        return []
    rows: list[dict[str, Any]] = []
    for action in (action_queue.get("actions") or [])[:limit]:
        rows.append(
            {
                "rank": action.get("rank"),
                "lane": action.get("verdict_cluster"),
                "kind": action.get("action_kind"),
                "target": action.get("gate_id")
                or action.get("file_path")
                or action.get("source_id")
                or action.get("target")
                or "?",
                "band": action.get("sort_band"),
                "records": int(action.get("violation_count") or 0),
                "ordering_reason": action.get("ordering_reason"),
                "source_artifact": action.get("source_artifact"),
                "signal": action.get("signal", ""),
            }
        )
    return rows


def _testing_hotspot_overlay(action_rows: list[dict[str, Any]], *, limit: int = 3) -> dict[str, Any]:
    rows = [
        row
        for row in action_rows
        if row.get("lane") == "GRAPHDB" and str(row.get("kind", "")).startswith("test_hotspot")
    ][:limit]
    ranked: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        ranked.append(
            {
                "rank": idx,
                "target": row.get("target"),
                "kind": row.get("kind"),
                "signal": row.get("signal"),
                "how_to_use": (
                    "Add or repair tests here if the current slice touches this path or its callers."
                ),
            }
        )
    return {
        "title": "Internal Testing Hotspot Map",
        "purpose": (
            "GraphDB/MV hotspots do not replace the gate priority order; they tell where tests should "
            "be added while executing the next burn-down or cleanup slice."
        ),
        "rows": ranked,
        "comments": [
            "Use hotspot rows as a test-placement overlay for the next implementation slice.",
            "A hotspot does not become Fix now by itself; it changes where tests are most valuable.",
            "If a burn-down target overlaps a hotspot path, include the test in the same change.",
        ],
    }


def _resolve_snapshot_path(gate_results: dict[str, Any], gate_results_path: Path) -> Path | None:
    raw = gate_results.get("snapshot_path")
    if not raw and isinstance(gate_results.get("snapshot"), dict):
        raw = gate_results["snapshot"].get("path") or gate_results["snapshot"].get("sqlite_path")
    if not raw:
        return None
    path = Path(str(raw))
    if not path.is_absolute():
        path = (gate_results_path.parent / path).resolve()
        if not path.exists():
            path = (REPO_ROOT / raw).resolve()
    return path if path.exists() else None


def _mv_action_names(action_rows: list[dict[str, Any]]) -> set[str]:
    names: set[str] = set()
    for row in action_rows:
        source = str(row.get("source_artifact") or "")
        if source.startswith("sqlite:mv_"):
            names.add(source.split("sqlite:", 1)[1])
        reason = str(row.get("ordering_reason") or "")
        if reason.startswith("mv_"):
            names.add(reason.rsplit("_priority", 1)[0])
    return names


def _gate_status_by_id(gate_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("gate_id")): row for row in gate_rows}


def _mv_description(name: str) -> str:
    desc = MV_DESCRIPTIONS.get(name)
    if desc:
        return desc[0]
    return "Materialized-view signal from the ADG SQLite graph."


def _mv_driver_status(
    *,
    name: str,
    count: int,
    action_mv_names: set[str],
    gate_status: dict[str, dict[str, Any]],
) -> tuple[str, str, str, str]:
    """Return routing_status, priority, role, next_action for an MV."""
    gate_ids = MV_GATE_DRIVERS.get(name, ())
    related_gates = [gate_status[gate_id] for gate_id in gate_ids if gate_id in gate_status]
    related_fix = [row for row in related_gates if row.get("action") == "FIX"]
    related_track = [row for row in related_gates if row.get("action") == "TRACK"]

    if count <= 0:
        return (
            "clean",
            "none",
            "No rows in this run.",
            "No action from this MV.",
        )
    if name in action_mv_names:
        return (
            "action_driver",
            "next",
            "Directly promoted into the action queue.",
            "Use this MV to choose where to add tests or scope the next slice.",
        )
    if related_fix:
        gates = ", ".join(f"`{_md_cell(row.get('gate_id'))}`" for row in related_fix)
        return (
            "gate_driver",
            "next",
            f"Supports current FIX gate(s): {gates}.",
            "Inspect this MV's rows while clearing the red gate.",
        )
    if related_track:
        gates = ", ".join(f"`{_md_cell(row.get('gate_id'))}`" for row in related_track)
        return (
            "gate_driver",
            "later",
            f"Supports TRACK/backlog gate(s): {gates}.",
            "Use after red gates clear to burn down the related floor or inventory.",
        )
    if name in MV_ANALYST_SIGNALS:
        return (
            "analyst_signal",
            "supporting",
            MV_ANALYST_SIGNALS[name],
            "Use as a tie-breaker for scope, test placement, or refactor order.",
        )
    return (
        "diagnostic_only",
        "monitor",
        "Recorded by GraphDB/MV but not currently promoted into gates or the action queue.",
        "Do not treat as immediate work unless it explains a FIX gate or planned slice.",
    )


def _mv_sort_key(row: dict[str, Any]) -> tuple[int, int, str]:
    priority_order = {"next": 0, "later": 1, "supporting": 2, "monitor": 3, "none": 4}
    return (
        priority_order.get(str(row.get("priority")), 9),
        -int(row.get("rows", 0) or 0),
        str(row.get("mv_name", "")),
    )


def _coverage_pct_text(value: Any) -> str:
    try:
        pct = float(value)
    except (TypeError, ValueError):
        return "absent"
    if pct < 0:
        return "absent"
    return f"{pct:.1f}%"


def _empty_testing_gap_summary() -> dict[str, Any]:
    return {
        "status": "missing",
        "plain_language": (
            "No mv_hotspot_coverage_risk table was available, so GraphDB could not quantify "
            "high-risk under-tested files for this run."
        ),
        "counts": {},
        "top_files": [],
        "what_to_do": [
            "Use the ranked action queue for test placement if GraphDB hotspot rows are present.",
        ],
    }


def _graphdb_mv_analyst_summary(
    *,
    gate_results: dict[str, Any],
    gate_results_path: Path,
    gate_rows: list[dict[str, Any]],
    action_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    snapshot_path = _resolve_snapshot_path(gate_results, gate_results_path)
    action_mv_names = _mv_action_names(action_rows)
    gate_status = _gate_status_by_id(gate_rows)

    inventory: list[dict[str, Any]] = []
    testing_gap_summary = _empty_testing_gap_summary()
    if snapshot_path is not None:
        try:
            con = sqlite3.connect(f"file:{snapshot_path}?mode=ro", uri=True)
            try:
                mv_names = [
                    str(row[0])
                    for row in con.execute(
                        "SELECT name FROM sqlite_master "
                        "WHERE type='table' AND name LIKE 'mv_%' ORDER BY name"
                    ).fetchall()
                ]
                for name in mv_names:
                    try:
                        count = int(con.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0])
                    except sqlite3.Error:
                        count = 0
                    routing_status, priority, role, next_action = _mv_driver_status(
                        name=name,
                        count=count,
                        action_mv_names=action_mv_names,
                        gate_status=gate_status,
                    )
                    inventory.append(
                        {
                            "mv_name": name,
                            "rows": count,
                            "routing_status": routing_status,
                            "priority": priority,
                            "role": role,
                            "description": _mv_description(name),
                            "next_action": next_action,
                            "related_gates": list(MV_GATE_DRIVERS.get(name, ())),
                        }
                    )
                if "mv_hotspot_coverage_risk" in mv_names:
                    agg = con.execute(
                        """
                        SELECT
                          COUNT(*) AS total,
                          SUM(CASE WHEN priority_band = 'P1_URGENT' THEN 1 ELSE 0 END) AS p1_urgent,
                          SUM(CASE WHEN priority_band = 'P2_GAP' THEN 1 ELSE 0 END) AS p2_gap,
                          SUM(CASE WHEN coverage_band = 'ABSENT' THEN 1 ELSE 0 END) AS absent,
                          SUM(CASE WHEN coverage_band = 'LOW' THEN 1 ELSE 0 END) AS low,
                          SUM(CASE WHEN risk_band = 'CRITICAL' THEN 1 ELSE 0 END) AS critical,
                          SUM(CASE WHEN risk_band = 'HIGH' THEN 1 ELSE 0 END) AS high
                        FROM mv_hotspot_coverage_risk
                        """
                    ).fetchone()
                    top_rows = con.execute(
                        """
                        SELECT file, layer, priority_band, risk_band, coverage_band,
                               coverage_pct, criticality_score, combined_risk_score,
                               fan_in, fan_out, violation_count
                        FROM mv_hotspot_coverage_risk
                        WHERE priority_band IN ('P1_URGENT', 'P2_GAP')
                        ORDER BY
                          CASE priority_band WHEN 'P1_URGENT' THEN 0 ELSE 1 END,
                          CASE risk_band WHEN 'CRITICAL' THEN 0 WHEN 'HIGH' THEN 1 ELSE 2 END,
                          criticality_score DESC,
                          combined_risk_score DESC,
                          fan_in DESC,
                          file ASC
                        LIMIT 8
                        """
                    ).fetchall()
                    top_files: list[dict[str, Any]] = []
                    for idx, row in enumerate(top_rows, start=1):
                        top_files.append(
                            {
                                "rank": idx,
                                "file": str(row[0] or "").replace("\\", "/"),
                                "layer": row[1],
                                "priority_band": row[2],
                                "risk_band": row[3],
                                "coverage_band": row[4],
                                "coverage_pct": _coverage_pct_text(row[5]),
                                "criticality_score": _float_value(row[6]),
                                "combined_risk_score": _float_value(row[7]),
                                "fan_in": _int_value(row[8]),
                                "fan_out": _int_value(row[9]),
                                "violation_count": _int_value(row[10]),
                                "analyst_read": (
                                    "High-blast-radius code with weak or absent tests. "
                                    "Test this when a gate fix or burn-down slice touches it."
                                ),
                            }
                        )
                    counts = {
                        "total_hotspots": _int_value(agg[0] if agg else 0),
                        "p1_urgent": _int_value(agg[1] if agg else 0),
                        "p2_gap": _int_value(agg[2] if agg else 0),
                        "coverage_absent": _int_value(agg[3] if agg else 0),
                        "coverage_low": _int_value(agg[4] if agg else 0),
                        "risk_critical": _int_value(agg[5] if agg else 0),
                        "risk_high": _int_value(agg[6] if agg else 0),
                    }
                    testing_gap_summary = {
                        "status": "present",
                        "plain_language": (
                            "GraphDB found important files with absent or weak test coverage. "
                            "These are not abstract metrics: they are the files where a change is most likely "
                            "to create an undetected regression."
                        ),
                        "counts": counts,
                        "top_files": top_files,
                        "what_to_do": [
                            "Treat this as the test-placement map for the next gate fix or ratchet burn-down slice.",
                            "Start with P1_URGENT + CRITICAL + ABSENT rows.",
                            "When a current fix touches a listed file or its callers, add or repair tests in that same change.",
                            "Do not open a separate mega testing project; attach tests to the work already being prioritized.",
                        ],
                    }
            finally:
                con.close()
        except (OSError, sqlite3.Error):
            inventory = []
            testing_gap_summary = _empty_testing_gap_summary()

    routed_next = [row for row in inventory if row.get("priority") == "next"]
    routed_later = [row for row in inventory if row.get("priority") == "later"]
    supporting = [row for row in inventory if row.get("priority") == "supporting"]
    diagnostic = [row for row in inventory if row.get("routing_status") == "diagnostic_only"]
    clean = [row for row in inventory if row.get("routing_status") == "clean"]
    nonempty = [row for row in inventory if int(row.get("rows", 0) or 0) > 0]

    priority_rows: list[dict[str, Any]] = []
    fix_actions = [row for row in action_rows if row.get("lane") == "FIX"]
    graph_actions = [row for row in action_rows if row.get("lane") == "GRAPHDB"]
    refactor_actions = [row for row in action_rows if row.get("lane") == "REFACTOR"]
    if fix_actions:
        priority_rows.append(
            {
                "rank": len(priority_rows) + 1,
                "priority": "Unblock red ADG gates",
                "plain_language": "The run is not green. Fix the red gates before burn-down work.",
                "graphdb_mv_signal": (
                    "Use any gate-driver MVs marked priority=next to inspect the failing surface."
                ),
                "next_action": "Fix the first FIX row in the ranked queue, rerun ADG, then continue.",
            }
        )
    if graph_actions:
        targets = "; ".join(
            f"`{_md_cell(row.get('target'), limit=80)}`" for row in graph_actions[:3]
        )
        priority_rows.append(
            {
                "rank": len(priority_rows) + 1,
                "priority": "Place tests where GraphDB says risk is highest",
                "plain_language": "GraphDB is telling you where a change is most likely under-tested.",
                "graphdb_mv_signal": targets,
                "next_action": "When the current fix or burn-down slice touches these paths, add or repair tests there.",
            }
        )
    if refactor_actions:
        targets = "; ".join(
            f"`{_md_cell(row.get('target'), limit=80)}`" for row in refactor_actions[:3]
        )
        priority_rows.append(
            {
                "rank": len(priority_rows) + 1,
                "priority": "Use structural hotspots after blockers",
                "plain_language": "These are leverage points, not emergency blockers.",
                "graphdb_mv_signal": targets,
                "next_action": "Use after FIX gates are green or when a blocker overlaps the same file.",
            }
        )
    if not fix_actions and routed_later:
        top = sorted(routed_later, key=_mv_sort_key)[:3]
        priority_rows.append(
            {
                "rank": len(priority_rows) + 1,
                "priority": "Burn down gate-driver MV backlog",
                "plain_language": "These MVs explain the tracked gate floors and inventories.",
                "graphdb_mv_signal": "; ".join(
                    f"`{_md_cell(row.get('mv_name'))}` {_fmt_int(row.get('rows'))}" for row in top
                ),
                "next_action": "Start with the matching P0/P1 ratchet or inventory gate, not the raw largest MV.",
            }
        )

    if not priority_rows:
        priority_rows.append(
            {
                "rank": 1,
                "priority": "No GraphDB/MV action promoted",
                "plain_language": "The MV layer did not emit a first-class action for this run.",
                "graphdb_mv_signal": "No promoted GraphDB/MV rows.",
                "next_action": "Use ADG gates as the work queue and keep MV rows as diagnostics.",
            }
        )

    routing_counts: dict[str, int] = {}
    for row in inventory:
        status = str(row.get("routing_status") or "unknown")
        routing_counts[status] = routing_counts.get(status, 0) + 1

    return {
        "title": "ADG + GraphDB/MV Analyst Summary",
        "snapshot_sqlite": _repo_rel(snapshot_path),
        "summary": {
            "mv_tables": len(inventory),
            "nonempty_mv_tables": len(nonempty),
            "empty_mv_tables": len(clean),
            "routing_counts": routing_counts,
            "action_driver_mvs": len([row for row in inventory if row.get("routing_status") == "action_driver"]),
            "gate_driver_mvs": len([row for row in inventory if row.get("routing_status") == "gate_driver"]),
            "diagnostic_only_mvs": len(diagnostic),
        },
        "plain_english": [
            "P0-P3 gates say what must be fixed or burned down.",
            "GraphDB/MVs say where the risk lives, where tests are missing, and which areas have the most blast radius.",
            "A large MV count is not automatically next work; it becomes next work when it feeds a red gate, a ratchet, or the action queue.",
            "Diagnostic-only MVs are still useful, but they should explain or scope a chosen gate/action rather than create a parallel backlog.",
        ],
        "testing_gap_summary": testing_gap_summary,
        "priority_rows": priority_rows,
        "top_mv_signals": sorted(nonempty, key=_mv_sort_key)[:10],
        "top_unrouted_mv_signals": sorted(diagnostic, key=lambda row: -int(row.get("rows", 0) or 0))[:8],
        "mv_inventory": sorted(inventory, key=lambda row: str(row.get("mv_name", ""))),
    }


def _testing_gap_counts_text(testing_gap: dict[str, Any]) -> str:
    counts = testing_gap.get("counts") or {}
    if not counts:
        return "testing gap not quantified"
    return (
        f"{_fmt_int(counts.get('p1_urgent', 0))} urgent; "
        f"{_fmt_int(counts.get('risk_critical', 0))} critical-risk; "
        f"{_fmt_int(counts.get('coverage_absent', 0))} absent coverage"
    )


def _testing_gap_targets(testing_gap: dict[str, Any], *, limit: int = 3) -> str:
    files = testing_gap.get("top_files") or []
    if not files:
        return "No GraphDB test-gap targets emitted."
    return "; ".join(f"`{_md_cell(row.get('file'), limit=80)}`" for row in files[:limit])


def _executive_decision_brief(
    *,
    operator_summary: dict[str, Any],
    graphdb_summary: dict[str, Any],
    action_rows: list[dict[str, Any]],
    priority_actions: list[str],
) -> dict[str, Any]:
    verdict = str(operator_summary.get("overall_verdict") or "UNKNOWN")
    fix_gates = int(operator_summary.get("fix_gates", 0) or 0)
    fix_records = int(operator_summary.get("fix_records", 0) or 0)
    ratchet_records = int(operator_summary.get("ratchet_floor_records", 0) or 0)
    cleanup_records = int(operator_summary.get("cleanup_records", 0) or 0)
    testing_gap = graphdb_summary.get("testing_gap_summary") or {}
    testing_counts = testing_gap.get("counts") or {}
    urgent_tests = int(testing_counts.get("p1_urgent", 0) or 0)
    critical_tests = int(testing_counts.get("risk_critical", 0) or 0)
    absent_tests = int(testing_counts.get("coverage_absent", 0) or 0)
    mv_summary = graphdb_summary.get("summary") or {}

    if fix_gates:
        decision = "Fund a narrow unblock-and-test slice now."
        situation = (
            f"ADG is {verdict}: {_fmt_int(fix_gates)} red gate(s) covering "
            f"{_fmt_int(fix_records)} record(s). The run is not green."
        )
        priority = "Clear red gates first; use GraphDB test gaps to decide where tests must be added in the same slice."
    else:
        decision = "Do not declare the system done; fund a ratchet burn-down slice with targeted tests."
        situation = (
            f"ADG is {verdict}: no red gates, but {_fmt_int(ratchet_records)} ratchet-floor "
            f"records and {_fmt_int(cleanup_records)} open non-ratchet records remain."
        )
        priority = "Burn down ratchets first; attach tests where GraphDB shows hotspot coverage risk."

    risk = "High" if fix_gates or urgent_tests or critical_tests else "Moderate"
    test_readout = (
        f"Testing risk is {risk}: {_fmt_int(urgent_tests)} urgent GraphDB hotspots, "
        f"{_fmt_int(critical_tests)} critical-risk hotspots, "
        f"{_fmt_int(absent_tests)} with absent coverage."
    )
    mv_readout = (
        f"GraphDB/MV is not unused: {_fmt_int(mv_summary.get('action_driver_mvs', 0))} MV(s) "
        "drive the action queue, "
        f"{_fmt_int(mv_summary.get('gate_driver_mvs', 0))} feed gates, and "
        f"{_fmt_int(mv_summary.get('diagnostic_only_mvs', 0))} are diagnostic/context only."
    )
    fix_actions = [row for row in action_rows if row.get("lane") == "FIX"]
    if fix_actions:
        first_fix = fix_actions[0]
        stabilize_action = (
            f"Fix first red gate: `{_md_cell(first_fix.get('target'))}` "
            f"({_md_cell(first_fix.get('band') or '?')}, "
            f"{_fmt_int(first_fix.get('records', 0))} record(s)); then continue down Priority Execution Plan."
        )
    else:
        stabilize_action = priority_actions[0] if priority_actions else priority

    actions = [
        {
            "rank": 1,
            "move": "Stabilize the run",
            "action": stabilize_action,
            "why": "This is the smallest path to a credible green ADG signal.",
            "graphdb_mv_signal": "Use gate-driver MVs and the hotspot table to scope the fix.",
        },
        {
            "rank": 2,
            "move": "Close the testing exposure",
            "action": (
                "Use the Testing Gap Risk table below; start with ranks 1-3 when the current slice touches them."
            ),
            "why": "These are high-blast-radius files with weak or absent test coverage.",
            "graphdb_mv_signal": _testing_gap_counts_text(testing_gap),
        },
        {
            "rank": 3,
            "move": "Reduce accepted debt",
            "action": (
                "After red gates are clear, burn down ratchet floors before broad cleanup."
                if fix_gates
                else "Burn down the largest P0/P1 ratchet floors before broad cleanup."
            ),
            "why": "Ratchet burn-down lowers the accepted baseline; broad cleanup does not.",
            "graphdb_mv_signal": "Use centrality, blast-radius, and coverage MVs as tie-breakers.",
        },
    ]

    return {
        "title": "Executive Decision Brief",
        "decision": decision,
        "situation": situation,
        "risk": risk,
        "testing_gap_readout": test_readout,
        "graphdb_mv_readout": mv_readout,
        "priority": priority,
        "actions": actions,
        "what_not_to_do": [
            "Do not chase the largest raw MV table just because it is large.",
            "Do not treat guardian exemptions as the work queue.",
            "Do not run broad cleanup before red gates and ratchet floors are controlled.",
        ],
    }


def _execution_test_action(bullet: str, testing_gap: dict[str, Any]) -> str:
    if bullet.startswith("Rerun ADG"):
        return "Run focused tests plus ADG; confirm the new review output reflects the lower risk."
    if bullet.startswith("Fix ") or "ratchet" in bullet.lower() or "open non-ratchet" in bullet.lower():
        return "If this work touches a Testing Gap Risk file or caller, add/repair tests in the same change."
    if "guardian" in bullet.lower():
        return "No test work; this is audit context, not the execution queue."
    return "Use GraphDB/MV signals as scope guardrails for the selected work."


def _execution_done_when(bullet: str) -> str:
    text = bullet.lower()
    if bullet.startswith("Fix `"):
        return "Gate no longer appears as FIX after rerun."
    if "burn down" in text and "ratchet" in text:
        return "Record count drops and the ratchet floor can be lowered."
    if "open non-ratchet" in text:
        return "Open work count drops without creating a new red gate."
    if bullet.startswith("Rerun ADG"):
        return "Fresh ADG review is generated and read before the next slice."
    if "guardian" in text:
        return "Only escalated if it maps to a failing gate or critical-path risk."
    return "Action either closed or deliberately deferred with evidence."


def _execution_priority_work(bullet: str) -> str:
    if ": " in bullet:
        return bullet.split(": ", 1)[0]
    return bullet


def _execution_reason(bullet: str) -> str:
    if ": " in bullet:
        return bullet.split(": ", 1)[1]
    if bullet.startswith("Rerun ADG"):
        return "Locks in the corrected state before burn-down work starts."
    if "guardian" in bullet.lower():
        return "Keeps exception math separate from the engineering queue."
    return "Next item in ADG priority order."


def _execution_plan_rows(priority_bullets: list[str], testing_gap: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for bullet in priority_bullets:
        if bullet.startswith("While fixing red gates, use GraphDB/MV testing hotspots"):
            continue
        if bullet.startswith("Apply GraphDB/MV testing hotspot overlay"):
            continue
        rows.append(
            {
                "rank": str(len(rows) + 1),
                "priority_work": _execution_priority_work(bullet),
                "why_now": _execution_reason(bullet),
                "testing_mv_action": _execution_test_action(bullet, testing_gap),
                "done_when": _execution_done_when(bullet),
            }
        )
    if not rows:
        rows.append(
            {
                "rank": "1",
                "priority_work": "No immediate ADG work emitted.",
                "why_now": "No red gate, ratchet, or open-work action was emitted.",
                "testing_mv_action": _execution_test_action("", testing_gap),
                "done_when": "No ADG action required for this run.",
            }
        )
    return rows


def _priority_execution_plan(
    *,
    priority_actions: list[str],
    graphdb_summary: dict[str, Any],
) -> dict[str, Any]:
    testing_gap = graphdb_summary.get("testing_gap_summary") or {}
    return {
        "title": "Priority Execution Plan",
        "purpose": (
            "One merged work queue. It combines red gates, ratchets, rerun steps, guardian audit context, "
            "and GraphDB/MV testing guidance so the next action is not split across repeated sections."
        ),
        "rows": _execution_plan_rows(priority_actions, testing_gap),
        "merged_from": [
            "ADG gate priority bullets",
            "GraphDB/MV testing gap risk",
            "guardian exception audit context",
        ],
    }


def _p0_priority_why(*, work_type: str, ordinal: int, records: int) -> str:
    if work_type == "Fix now":
        return "Blocks green ADG; fix before burn-down work."
    if work_type == "Burn down ratchet":
        if ordinal == 1:
            return "Largest P0 ratchet floor; reduces the biggest accepted baseline first."
        if records <= 5:
            return "Small P0 ratchet; close opportunistically after the larger P0 floors."
        return "Next-largest P0 ratchet floor; keep burning down accepted baseline debt."
    if records <= 5:
        return "Small open P0 work item; bundle if it is already in the same files."
    return "Real open P0 work, but it does not reduce the ratchet floor."


def _p0_next_step(*, work_type: str, records: int) -> str:
    if work_type == "Fix now":
        return "Fix the gate condition and rerun ADG before treating the run as green."
    if work_type == "Burn down ratchet":
        if records <= 5:
            return "Close or bundle this small floor, rerun ADG, then absorb the lower baseline."
        return "Open a burn-down slice for this gate, reduce records, rerun ADG, then absorb the lower baseline."
    if records <= 5:
        return "Close when touching nearby code; it is open work but not ratchet burn-down."
    return "Schedule after P0 ratchets unless the fix is tiny, already in hand, or high-leverage."


def _p0_action_plan(gate_rows: list[dict[str, Any]]) -> dict[str, Any]:
    p0_rows = [
        row
        for row in gate_rows
        if row.get("band") == "P0"
        and row.get("action") in {"FIX", "TRACK"}
        and int(row.get("records", 0) or 0) > 0
    ]
    fix_rows = sorted(
        (row for row in p0_rows if row.get("action") == "FIX"),
        key=lambda row: (-int(row.get("records", 0) or 0), str(row.get("gate_id", ""))),
    )
    ratchet_rows = sorted(
        (row for row in p0_rows if row.get("action") == "TRACK" and row.get("sub") == "floor"),
        key=lambda row: (-int(row.get("records", 0) or 0), str(row.get("gate_id", ""))),
    )
    open_rows = sorted(
        (row for row in p0_rows if row.get("action") == "TRACK" and row.get("sub") != "floor"),
        key=lambda row: (-int(row.get("records", 0) or 0), str(row.get("gate_id", ""))),
    )

    ordered: list[dict[str, Any]] = []
    for work_type, rows in (
        ("Fix now", fix_rows),
        ("Burn down ratchet", ratchet_rows),
        ("Open non-ratchet work", open_rows),
    ):
        for ordinal, row in enumerate(rows, start=1):
            records = int(row.get("records", 0) or 0)
            gate_id = str(row.get("gate_id", "?"))
            ordered.append(
                {
                    "rank": len(ordered) + 1,
                    "work_type": work_type,
                    "gate_id": gate_id,
                    "label": _short_gate_id(gate_id),
                    "records": records,
                    "record_type": row.get("record_type"),
                    "why_this_priority": _p0_priority_why(
                        work_type=work_type,
                        ordinal=ordinal,
                        records=records,
                    ),
                    "next_step": _p0_next_step(work_type=work_type, records=records),
                }
            )

    comments = [
        "Read this table top to bottom. If Fix now rows exist, they override ratchets because ADG is not green.",
        "With Fix now = 0, P0 ratchets are sorted by tracked records so the largest accepted floor burns down first.",
        "Open non-ratchet work is still real work; it is second because it does not lower the P0 ratchet floor.",
        "Guardian/non-exempt severity counts are an exception audit and should not reorder this P0 work list.",
    ]
    return {
        "title": "P0 Action Plan",
        "priority_rule": "Fix-now gates first; otherwise P0 ratchets by tracked-record count; then P0 open non-ratchet work.",
        "rows": ordered,
        "comments": comments,
    }


def _attack_row_sort_key(row: dict[str, Any]) -> tuple[int, int, int, str]:
    return (
        ATTACK_CLASS_PRIORITY.get(str(row.get("work_class")), 99),
        BAND_PRIORITY.get(str(row.get("band")), 99),
        -int(row.get("records", 0) or 0),
        str(row.get("target", "")),
    )


def _adg_attack_order(
    band_rows: list[dict[str, Any]],
    severity_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for row in band_rows:
        band = str(row.get("band", "?"))
        fix_records = int(row.get("fix_records", 0) or 0)
        if int(row.get("fix_gates", 0) or 0) or fix_records:
            rows.append(
                {
                    "band": band,
                    "work_class": "Fix now",
                    "target": f"{band} CI blockers",
                    "records": fix_records,
                    "why_this_priority": "CI blocker; ADG is not green until this clears.",
                    "next_step": "Fix the blocking gate condition and rerun ADG before burn-down work.",
                }
            )
        ratchet_records = int(row.get("ratchet_floor_records", 0) or 0)
        if ratchet_records:
            rows.append(
                {
                    "band": band,
                    "work_class": "Burn down ratchets",
                    "target": row.get("ratchet_burn_down"),
                    "records": ratchet_records,
                    "why_this_priority": (
                        "Ratchet floor work lowers accepted baseline debt; P-band outranks raw size."
                    ),
                    "next_step": (
                        "Use the P0 Action Plan below."
                        if band == "P0"
                        else "Open a burn-down slice for the listed ratchets, rerun ADG, then absorb the lower baseline."
                    ),
                }
            )
        open_records = int(row.get("cleanup_records", 0) or 0)
        if open_records:
            rows.append(
                {
                    "band": band,
                    "work_class": "Open non-ratchet work",
                    "target": row.get("open_non_ratchet_work") or row.get("cleanup_backlog"),
                    "records": open_records,
                    "why_this_priority": (
                        "Real open work, but it does not lower a ratchet floor or block CI."
                    ),
                    "next_step": "Schedule after ratchets unless the item is tiny, already in hand, or high-leverage.",
                }
            )

    for row in severity_rows:
        net = int(row.get("net", 0) or 0)
        if not net:
            continue
        gross = int(row.get("gross", 0) or 0)
        rows.append(
            {
                "band": row.get("band"),
                "work_class": "Severity audit",
                "target": f"{_fmt_int(net)} non-exempt from {_fmt_int(gross)} gross",
                "records": net,
                "why_this_priority": (
                    "Review-only audit signal; not Fix now unless it maps to a failing gate."
                ),
                "next_step": "Audit or map to a gate; do not treat as a CI blocker by itself.",
            }
        )

    ordered = sorted(rows, key=_attack_row_sort_key)
    if not ordered:
        ordered = [
            {
                "band": "ALL",
                "work_class": "No action",
                "target": "No fix, ratchet, open-work, or severity-audit rows",
                "records": 0,
                "why_this_priority": "All tracked ADG work buckets are empty.",
                "next_step": "No ADG burn-down action.",
            }
        ]
    for rank, row in enumerate(ordered, start=1):
        row["rank"] = rank

    return {
        "title": "ADG Heuristic Attack Order",
        "priority_rule": (
            "Sort by work class first (Fix now > ratchets > open work > severity audit), "
            "then P-band (P0 > P1 > P2 > P3), then record count within the same class and band."
        ),
        "rows": ordered,
        "comments": [
            "Non-exempt severity rows are included for review, but they do not populate Fix now unless a gate is failing.",
            "Record count breaks ties inside the same work class and P-band; it does not make P3 outrank P0.",
            "When the top row is P0 ratchets, use the P0 Action Plan for the exact gate order.",
        ],
    }


def _priority_actions(
    band_rows: list[dict[str, Any]],
    action_rows: list[dict[str, Any]],
    p0_plan: dict[str, Any],
    hotspot_overlay: dict[str, Any],
) -> list[str]:
    bullets: list[str] = []
    fix_bands = [row for row in band_rows if int(row.get("fix_gates", 0) or 0)]
    if fix_bands:
        fix_actions = [row for row in action_rows if row.get("lane") == "FIX"]
        if fix_actions:
            for row in fix_actions[:5]:
                target = _md_cell(row.get("target"), limit=90)
                band = _md_cell(row.get("band") or "?")
                records = _fmt_int(row.get("records", 0))
                signal = _md_cell(row.get("signal"), limit=150)
                bullets.append(
                    f"Fix `{target}` ({band}, {records} record(s)): {signal}"
                )
        else:
            for row in fix_bands:
                bullets.append(
                    f"Fix {row['band']} red gates first: "
                    f"{_fmt_int(row.get('fix_gates', 0))} gate(s), "
                    f"{_fmt_int(row.get('fix_records', 0))} record(s)."
                )
        if len(fix_actions) > 5:
            bullets.append(
                f"Fix remaining red gates after the top five: {_fmt_int(len(fix_actions) - 5)} more gate(s)."
            )
        if hotspot_overlay.get("rows"):
            targets = "; ".join(
                f"`{_md_cell(item.get('target'), limit=80)}`"
                for item in list(hotspot_overlay.get("rows") or [])[:3]
            )
            bullets.append(
                "While fixing red gates, use GraphDB/MV testing hotspots as the test-placement map: "
                + targets
                + "."
            )
        bullets.append("Rerun ADG after the red gates clear; only then treat ratchet burn-down as the main queue.")
        bullets.append("Review guardian exceptions separately; they are severity audit math, not burn-down work.")
        return bullets

    inserted_hotspot_overlay = False
    for row in p0_plan.get("rows") or []:
        if row.get("work_type") == "Burn down ratchet":
            bullets.append(
                f"Burn down P0 ratchet `{_md_cell(row.get('label'))}` "
                f"({_fmt_int(row.get('records', 0))}): {_md_cell(row.get('next_step'))}"
            )
            continue

        if not inserted_hotspot_overlay and hotspot_overlay.get("rows"):
            targets = "; ".join(
                f"`{_md_cell(item.get('target'), limit=80)}`"
                for item in list(hotspot_overlay.get("rows") or [])[:3]
            )
            bullets.append(
                "Apply GraphDB/MV testing hotspot overlay while executing the next burn-down slice: "
                + targets
                + "."
            )
            inserted_hotspot_overlay = True

        if row.get("work_type") == "Open non-ratchet work":
            bullets.append(
                f"Close P0 open non-ratchet work `{_md_cell(row.get('label'))}` "
                f"({_fmt_int(row.get('records', 0))}): {_md_cell(row.get('next_step'))}"
            )

    if not inserted_hotspot_overlay and hotspot_overlay.get("rows"):
        targets = "; ".join(
            f"`{_md_cell(item.get('target'), limit=80)}`"
            for item in list(hotspot_overlay.get("rows") or [])[:3]
        )
        bullets.append(
            "Apply GraphDB/MV testing hotspot overlay before the next code slice: "
            + targets
            + "."
        )

    p0 = next((row for row in band_rows if row.get("band") == "P0"), None)
    if p0 and int(p0.get("cleanup_records", 0) or 0) and not bullets:
        bullets.append(
            "Close P0 open non-ratchet work after ratchets: "
            + _format_bullet_items(list(p0.get("cleanup_items") or []))
            + ". These records are real open work, but they do not add to the P0 ratchet count."
        )

    for row in band_rows:
        if row.get("band") == "P0":
            continue
        if int(row.get("ratchet_floor_records", 0) or 0):
            bullets.append(
                f"Then burn down {row['band']} ratchets by size: "
                + _format_bullet_items(list(row.get("ratchet_floor_items") or []), max_items=3)
                + "."
            )
        if int(row.get("cleanup_records", 0) or 0):
            bullets.append(
                f"Close {row['band']} open non-ratchet work: "
                + _format_bullet_items(list(row.get("cleanup_items") or []))
                + "."
            )

    bullets.append("Review guardian exceptions separately; they are severity audit math, not burn-down work.")
    return bullets


def _high_signal_review(
    *,
    summary: dict[str, Any],
    band_rows: list[dict[str, Any]],
    severity_rows: list[dict[str, Any]],
    action_rows: list[dict[str, Any]],
    priority_actions: list[str],
    p0_plan: dict[str, Any],
    attack_order: dict[str, Any],
) -> dict[str, Any]:
    p0 = next((row for row in band_rows if row.get("band") == "P0"), {})
    p0_severity = next((row for row in severity_rows if row.get("band") == "P0"), {})
    p0_ratchets = _format_bullet_items(list(p0.get("ratchet_floor_items") or []))
    p0_cleanup = _format_bullet_items(list(p0.get("cleanup_items") or []))
    top_graphdb = next((row for row in action_rows if row.get("lane") == "GRAPHDB"), None)
    fix_gates = int(summary.get("fix_gates", 0) or 0)
    verdict = str(summary.get("overall_verdict") or "UNKNOWN")

    if fix_gates:
        run_meaning = (
            f"The ADG run is {verdict}: {_fmt_int(fix_gates)} gate(s) must be fixed "
            "before treating the run as green."
        )
        headline = "Fix red ADG gates before burn-down work."
    else:
        run_meaning = (
            f"The ADG run is {verdict}: 0 fix-now gates. There is no current blocker "
            "or ratchet regression."
        )
        headline = "Green for enforcement; burn-down work remains."

    what_this_means = [
        run_meaning,
        (
            "Green does not mean done: "
            f"{_fmt_int(summary.get('ratchet_floor_records', 0))} ratchet-floor records "
            "still need burn-down."
        ),
        "Use the ADG Heuristic Attack Order to choose the next bucket across P0-P3.",
        "Use the P0 Action Plan top to bottom; it prioritizes ratchets by tracked-record count.",
        f"P0 ratchets in order: {p0_ratchets}.",
        (
            f"P0 open non-ratchet work is separate from P0 ratchets: {p0_cleanup}. "
            "Do it after ratchets unless an item is tiny or high-leverage."
        ),
        (
            "Guardian is exception audit only: "
            f"P0 has {_fmt_int(p0_severity.get('net', 0))} non-exempt severity items "
            f"from {_fmt_int(p0_severity.get('gross', 0))} gross. "
            "Do not use guardian math as the burn-down queue."
        ),
    ]
    if top_graphdb:
        what_this_means.append(
            "GraphDB/MV says the first testing hotspot is "
            f"`{top_graphdb.get('target') or '?'}`."
        )

    return {
        "headline": headline,
        "what_this_means": what_this_means,
        "do_this_next": priority_actions,
        "adg_attack_order": attack_order,
        "p0_action_plan": p0_plan,
        "p0_relationships": {
            "ratchet_burn_down_records": int(p0.get("ratchet_floor_records", 0) or 0),
            "ratchet_burn_down_items": list(p0.get("ratchet_floor_items") or []),
            "non_ratchet_cleanup_records": int(p0.get("cleanup_records", 0) or 0),
            "non_ratchet_cleanup_items": list(p0.get("cleanup_items") or []),
            "open_non_ratchet_work_records": int(p0.get("cleanup_records", 0) or 0),
            "open_non_ratchet_work_items": list(p0.get("cleanup_items") or []),
            "cleanup_relation_to_ratchets": (
                "Separate open work. These records do not add to, subtract from, "
                "or change the ratchet-floor count."
            ),
            "guardian_relation_to_burn_down": (
                "Separate exception audit. Guardian changes severity net math, "
                "not the ratchet or open-work queue."
            ),
        },
        "first_testing_hotspot": top_graphdb,
    }


def build_review_template(
    *,
    gate_results_path: Path,
    burndown_path: Path,
    action_queue_path: Path | None = None,
    generation_manifest_path: Path | None = None,
    enforcement_report_path: Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    gate_results = _load_json(gate_results_path)
    burndown = _load_json(burndown_path)
    action_queue = _safe_load_json(action_queue_path)
    generation_manifest = _safe_load_json(generation_manifest_path)
    enforcement_report = _safe_load_json(enforcement_report_path)

    gates = list(gate_results.get("gates") or [])
    band_rows = _band_status_rows(gates)
    gate_rows = _gate_rows(gates)
    p0_plan = _p0_action_plan(gate_rows)
    action_counts = {
        "fix_gates": sum(1 for g in gates if display_verdict(g) == "FIX"),
        "track_gates": sum(1 for g in gates if display_verdict(g) == "TRACK"),
        "clear_gates": sum(1 for g in gates if display_verdict(g) == "CLEAR"),
        "fix_records": sum(int(g.get("violation_count") or 0) for g in gates if display_verdict(g) == "FIX"),
        "tracked_records": sum(
            int(g.get("violation_count") or 0) for g in gates if display_verdict(g) == "TRACK"
        ),
        "ratchet_floor_records": sum(int(row["ratchet_floor_records"]) for row in band_rows),
        "cleanup_records": sum(int(row["cleanup_records"]) for row in band_rows),
    }
    action_rows = _action_rows(action_queue)
    severity_rows = _severity_inventory(burndown)
    attack_order = _adg_attack_order(band_rows, severity_rows)
    hotspot_overlay = _testing_hotspot_overlay(action_rows)
    priority_actions = _priority_actions(band_rows, action_rows, p0_plan, hotspot_overlay)
    operator_summary = {
        "overall_verdict": "PASS" if gate_results.get("overall_exit_code", 1) == 0 else "BLOCKED",
        **action_counts,
        "band_status": band_rows,
    }
    graphdb_summary = _graphdb_mv_analyst_summary(
        gate_results=gate_results,
        gate_results_path=gate_results_path,
        gate_rows=gate_rows,
        action_rows=action_rows,
    )
    executive_brief = _executive_decision_brief(
        operator_summary=operator_summary,
        graphdb_summary=graphdb_summary,
        action_rows=action_rows,
        priority_actions=priority_actions,
    )
    priority_execution_plan = _priority_execution_plan(
        priority_actions=priority_actions,
        graphdb_summary=graphdb_summary,
    )

    artifacts = {
        "gate_results": _artifact_ref("gate_results", gate_results_path, required=True),
        "burndown": _artifact_ref("burndown", burndown_path, required=True),
        "action_queue": _artifact_ref("action_queue", action_queue_path),
        "generation_manifest": _artifact_ref("generation_manifest", generation_manifest_path),
        "enforcement_report": _artifact_ref("enforcement_report", enforcement_report_path),
        "markdown_burndown": _artifact_ref(
            "markdown_burndown",
            ARTIFACTS_ADG / "adg_burndown_report.md",
        ),
        "docs_markdown_burndown": _artifact_ref(
            "docs_markdown_burndown",
            DOCS_ADG / "adg_burndown_report.md",
        ),
    }

    return {
        "schema_version": "1.0",
        "artifact_kind": "adg_run_review_template",
        "run_id": run_id,
        "generated_at_utc": _utcnow_iso(),
        "snapshot_ts": gate_results.get("timestamp"),
        "review_template": {
            "reviewer": "",
            "reviewed_at": "",
            "decision": "pending",
            "notes": "",
        },
        "terminology": {
            "tracked_records": (
                "Gate-specific violation_count entries, such as orphan modules, "
                "UWG bypass paths, write-inventory paths, or complexity records."
            ),
            "ratchet_floor": "Known debt that CI allows only because it has not regressed; burn it down.",
            "open_non_ratchet_work": (
                "Real open work from warn/inventory gates. Close it after ratchets unless the item "
                "is tiny or high-leverage. It is not a current run blocker."
            ),
            "cleanup_backlog": (
                "Compatibility alias for open_non_ratchet_work."
            ),
            "not_counted_as": [
                "guardian exemptions",
                "test failures",
                "new failures",
                "files unless the gate record_type says files",
            ],
            "guardian_math_location": "severity_inventory; net = gross - guardian",
        },
        "operator_summary": operator_summary,
        "executive_decision_brief": executive_brief,
        "graphdb_mv_analyst_summary": graphdb_summary,
        "priority_execution_plan": priority_execution_plan,
        "adg_attack_order": attack_order,
        "p0_action_plan": p0_plan,
        "adg_ci_gates": gate_rows,
        "severity_inventory": severity_rows,
        "high_signal_review": _high_signal_review(
            summary=operator_summary,
            band_rows=band_rows,
            severity_rows=severity_rows,
            action_rows=action_rows,
            priority_actions=priority_actions,
            p0_plan=p0_plan,
            attack_order=attack_order,
        ),
        "next_best_action": {
            "source": _repo_rel(action_queue_path),
            "emit_status": action_queue.get("emit_status") if action_queue else "missing",
            "degraded": action_queue.get("provenance", {}).get("degraded") if action_queue else True,
            "actions": action_rows,
            "priority_bullets": priority_actions,
        },
        "graphdb_mv_positioning": {
            "purpose": "GraphDB/MV actions rank structural test hotspots and refactor targets after FIX gates.",
            "graphdb_actions_present": any(row.get("lane") == "GRAPHDB" for row in action_rows),
            "testing_hotspots_promoted": bool(hotspot_overlay.get("rows")),
        },
        "decision_synthesis": {
            "band_counts": band_decision_summary(gates),
            "after_green_plan": after_green_plan(band_rows),
            "artifact_consistency": artifact_consistency_status(
                required_artifacts=list(artifacts.values()),
                fail_closed=True,
            ),
            "audit_notes": [
                "FIX/TRACK/CLEAR routing is synthesized once and projected into JSON, YAML, and markdown.",
                "Ratchet floor records and open non-ratchet records are intentionally separate work buckets.",
            ],
        },
        "artifacts": artifacts,
        "raw_rollups": {
            "gate_results_summary": gate_results.get("summary", {}),
            "burndown_flags": {
                "p0_clean": burndown.get("p0_clean"),
                "p1_no_ratchet": burndown.get("p1_no_ratchet"),
                "counting_mode": (burndown.get("provenance") or {}).get("counting_mode"),
            },
            "generation_manifest": generation_manifest or {},
            "enforcement_report_status": (enforcement_report or {}).get("certified_rollup"),
        },
    }


def validate_review_template(doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in (
        "schema_version",
        "artifact_kind",
        "review_template",
        "terminology",
        "operator_summary",
        "executive_decision_brief",
        "graphdb_mv_analyst_summary",
        "priority_execution_plan",
        "adg_attack_order",
        "p0_action_plan",
        "adg_ci_gates",
        "severity_inventory",
        "high_signal_review",
        "next_best_action",
        "decision_synthesis",
        "artifacts",
    ):
        if key not in doc:
            errors.append(f"missing top-level field: {key}")
    if doc.get("artifact_kind") != "adg_run_review_template":
        errors.append("artifact_kind must be adg_run_review_template")
    bands = [row.get("band") for row in doc.get("operator_summary", {}).get("band_status", [])]
    if bands != ["P0", "P1", "P2", "P3"]:
        errors.append("operator_summary.band_status must be ordered P0,P1,P2,P3")
    required = [
        key
        for key, ref in (doc.get("artifacts") or {}).items()
        if isinstance(ref, dict) and ref.get("required") and not ref.get("exists")
    ]
    if required:
        errors.append(f"required artifacts missing: {', '.join(required)}")
    high_signal = doc.get("high_signal_review") or {}
    if not high_signal.get("what_this_means"):
        errors.append("high_signal_review.what_this_means must not be empty")
    if not high_signal.get("do_this_next"):
        errors.append("high_signal_review.do_this_next must not be empty")
    executive = doc.get("executive_decision_brief") or {}
    if not executive.get("actions"):
        errors.append("executive_decision_brief.actions must not be empty")
    graphdb = doc.get("graphdb_mv_analyst_summary") or {}
    testing_gap = graphdb.get("testing_gap_summary") or {}
    if "top_files" not in testing_gap:
        errors.append("graphdb_mv_analyst_summary.testing_gap_summary.top_files must be present")
    execution_plan = doc.get("priority_execution_plan") or {}
    if not execution_plan.get("rows"):
        errors.append("priority_execution_plan.rows must not be empty")
    p0_plan = doc.get("p0_action_plan") or {}
    if not p0_plan.get("comments"):
        errors.append("p0_action_plan.comments must not be empty")
    attack_order = doc.get("adg_attack_order") or {}
    if not attack_order.get("rows"):
        errors.append("adg_attack_order.rows must not be empty")
    synthesis = doc.get("decision_synthesis") or {}
    if not synthesis.get("band_counts"):
        errors.append("decision_synthesis.band_counts must not be empty")
    artifact_status = synthesis.get("artifact_consistency") or {}
    if artifact_status.get("status") not in {"ok", "fail_open", "fail_closed"}:
        errors.append("decision_synthesis.artifact_consistency.status must be valid")
    return errors


def render_inline_review_template(
    doc: dict[str, Any],
    *,
    output_path: Path | None = None,
) -> str:
    """Return the compact markdown projection printed inline after ADG runs."""
    summary = doc.get("operator_summary", {})
    terminology = doc.get("terminology", {})
    actions = doc.get("next_best_action", {}).get("actions") or []
    band_rows = summary.get("band_status") or []
    high_signal = doc.get("high_signal_review") or {}
    attack_order = doc.get("adg_attack_order") or high_signal.get("adg_attack_order") or {}
    p0_plan = doc.get("p0_action_plan") or high_signal.get("p0_action_plan") or {}
    executive = doc.get("executive_decision_brief") or {}
    graphdb = doc.get("graphdb_mv_analyst_summary") or {}
    testing_gap = graphdb.get("testing_gap_summary") or {}
    execution_plan = doc.get("priority_execution_plan") or {}
    what_this_means = high_signal.get("what_this_means") or []
    priority_bullets = high_signal.get("do_this_next") or doc.get("next_best_action", {}).get(
        "priority_bullets",
    ) or []
    yaml_path = output_path.with_suffix(".yaml") if output_path is not None else None

    lines: list[str] = [
        "## ADG Review",
        "",
        f"- **JSON:** `{_repo_rel(output_path) or 'not written'}`",
        f"- **YAML:** `{_repo_rel(yaml_path) or 'not written'}`",
        f"- **Run ID:** `{doc.get('run_id') or 'n/a'}`",
        "",
        "### Executive Decision Brief",
        "",
        f"- **Decision:** {_md_cell(executive.get('decision'))}",
        f"- **Situation:** {_md_cell(executive.get('situation'))}",
        f"- **Risk:** {_md_cell(executive.get('risk'))}",
        f"- **Testing gap:** {_md_cell(executive.get('testing_gap_readout'))}",
        f"- **GraphDB/MV read:** {_md_cell(executive.get('graphdb_mv_readout'))}",
        "",
        "| # | Move | Action | Why | GraphDB/MV signal |",
        "|--:|------|--------|-----|-------------------|",
    ]
    for row in executive.get("actions") or []:
        lines.append(
            f"| {_fmt_int(row.get('rank', 0))} | {_md_cell(row.get('move'), limit=42)} | "
            f"{_md_cell(row.get('action'), limit=120)} | "
            f"{_md_cell(row.get('why'), limit=90)} | "
            f"{_md_cell(row.get('graphdb_mv_signal'), limit=90)} |"
        )
    lines.extend(
        [
            "",
            "### Testing Gap Risk",
            "",
            f"- **Analyst read:** {_md_cell(testing_gap.get('plain_language'))}",
            "",
            "| Rank | File | Risk | Coverage | Testing implication |",
            "|-----:|------|------|----------|------------|",
        ]
    )
    top_test_files = testing_gap.get("top_files") or []
    if top_test_files:
        for row in top_test_files[:5]:
            risk = (
                f"{_md_cell(row.get('priority_band'))} / "
                f"{_md_cell(row.get('risk_band'))}"
            )
            coverage = (
                f"{_md_cell(row.get('coverage_band'))} "
                f"({_md_cell(row.get('coverage_pct'))})"
            )
            lines.append(
                f"| {_fmt_int(row.get('rank', 0))} | "
                f"`{_md_cell(row.get('file'), limit=88)}` | "
                f"{risk} | {coverage} | "
                f"{_md_cell(row.get('analyst_read'), limit=115)} |"
            )
    else:
        lines.append("| - | None | Not quantified | Not quantified | No GraphDB testing-gap table available. |")
    lines.extend(
        [
            "",
            "### Priority Execution Plan",
            "",
            "| # | Priority work | Why now | Testing / MV action | Done when |",
            "|--:|---------------|---------|---------------------|-----------|",
        ]
    )
    execution_rows = execution_plan.get("rows") or _execution_plan_rows(priority_bullets, testing_gap)
    for row in execution_rows:
        lines.append(
            f"| {row.get('rank')} | {_md_cell(row.get('priority_work'), limit=130)} | "
            f"{_md_cell(row.get('why_now'), limit=110)} | "
            f"{_md_cell(row.get('testing_mv_action'), limit=105)} | "
            f"{_md_cell(row.get('done_when'), limit=95)} |"
        )
    lines.extend(
        [
            "",
            "### What This Means",
            "",
        ]
    )
    lines.extend(f"- {_md_cell(item)}" for item in what_this_means)

    lines.extend(
        [
            "",
            "### ADG Heuristic Attack Order",
            "",
            f"- **Rule:** {_md_cell(attack_order.get('priority_rule'))}",
            "",
            "| # | Attack | Band | Records | Why | Next step |",
            "|--:|--------|------|--------:|-----|-----------|",
        ]
    )
    for row in attack_order.get("rows") or []:
        lines.append(
            f"| {_fmt_int(row.get('rank', 0))} | {_md_cell(row.get('work_class'))}: "
            f"{_md_cell(row.get('target'))} | {row.get('band')} | "
            f"{_fmt_int(row.get('records', 0))} | "
            f"{_md_cell(row.get('why_this_priority'), limit=90)} | "
            f"{_md_cell(row.get('next_step'), limit=100)} |"
        )
    lines.extend(["", "Comments:"])
    for comment in attack_order.get("comments") or []:
        lines.append(f"- {_md_cell(comment)}")

    lines.extend(
        [
            "",
            "### P0 Action Plan",
            "",
            f"- **Priority rule:** {_md_cell(p0_plan.get('priority_rule'))}",
            "",
            "| # | Work | Gate | Records | Why this priority | Next step |",
            "|--:|------|------|--------:|-------------------|-----------|",
        ]
    )
    p0_rows = p0_plan.get("rows") or []
    if p0_rows:
        for row in p0_rows:
            lines.append(
                f"| {_fmt_int(row.get('rank', 0))} | {_md_cell(row.get('work_type'))} | "
                f"`{_md_cell(row.get('label'))}` | {_fmt_int(row.get('records', 0))} | "
                f"{_md_cell(row.get('why_this_priority'), limit=96)} | "
                f"{_md_cell(row.get('next_step'), limit=110)} |"
            )
    else:
        lines.append("| — | None | None | 0 | No P0 fix, ratchet, or open-work records. | No P0 action. |")

    lines.extend(["", "Comments:"])
    for comment in p0_plan.get("comments") or []:
        lines.append(f"- {_md_cell(comment)}")

    lines.extend(
        [
            "",
            "### Details If Needed",
            "",
            f"- **Ratchet floor:** {_md_cell(terminology.get('ratchet_floor'))}",
            f"- **Open non-ratchet work:** {_md_cell(terminology.get('open_non_ratchet_work'))}",
            f"- **Not counted as:** {_md_cell(', '.join(terminology.get('not_counted_as') or []))}",
            "",
            "#### P0-P3 Rollup (Status Only)",
            "",
            "| Band | Fix now | 1) Burn down ratchets | 2) Open non-ratchet work | Work order |",
            "|------|--------:|-----------------------|---------------------------|------------|",
        ]
    )
    for row in band_rows:
        lines.append(
            f"| {row.get('band')} | {_fmt_int(row.get('fix_gates', 0))} | "
            f"{_md_cell(row.get('ratchet_burn_down'))} | "
            f"{_md_cell(row.get('open_non_ratchet_work') or row.get('cleanup_backlog'))} | "
            f"{_md_cell(row.get('next_move'))} |"
        )

    lines.extend(
        [
            "",
            "### Exception Audit",
            "",
            "| Band | Gross | Guardian | Non-exempt |",
            "|------|------:|---------:|-----------:|",
        ]
    )
    for row in doc.get("severity_inventory") or []:
        lines.append(
            f"| {row.get('band')} | {_fmt_int(row.get('gross', 0))} | "
            f"{_fmt_int(row.get('guardian', 0))} | {_fmt_int(row.get('net', 0))} |"
        )

    lines.extend(
        [
            "",
            "### Ranked Queue",
            "",
            "| Rank | Lane | Kind | Target |",
            "|-----:|------|------|--------|",
        ]
    )
    if actions:
        for action in actions[:5]:
            lines.append(
                f"| {action.get('rank')} | {_md_cell(action.get('lane'))} | "
                f"{_md_cell(action.get('kind'))} | `{_md_cell(action.get('target'), limit=80)}` |"
            )
    else:
        lines.append("| - | - | - | No current actions emitted |")

    return "\n".join(lines) + "\n"


def emit_mandatory_adg_review_template(
    *,
    adg_artifacts_dir: Path = ARTIFACTS_ADG,
    ts: str | None = None,
    gate_results: Path | None = None,
    burndown: Path | None = None,
    action_queue: Path | None = None,
    generation_manifest: Path | None = None,
    enforcement_report: Path | None = None,
    output_path: Path | None = None,
    write_latest: bool = True,
    write_yaml: bool = True,
    print_inline: bool = True,
    fail_closed: bool = True,
) -> tuple[int, Path | None]:
    """Write the review template JSON/YAML. Returns ``(exit_code, json_path_or_none)``."""
    artifacts = Path(adg_artifacts_dir)
    gate_path = gate_results or _resolve_latest("adg_gate_results_*.json", artifacts)
    burndown_path = burndown or (artifacts / "adg_burndown_table.json")

    if action_queue is None and ts:
        candidate = artifacts / f"adg_action_queue_{ts}.json"
        if candidate.is_file():
            action_queue = candidate
    if action_queue is None:
        action_queue = _resolve_latest("adg_action_queue_*.json", artifacts)

    if generation_manifest is None and ts:
        candidate = artifacts / f"adg_generation_manifest_{ts}.json"
        if candidate.is_file():
            generation_manifest = candidate
    if generation_manifest is None:
        generation_manifest = _resolve_latest("adg_generation_manifest_*.json", artifacts)

    if enforcement_report is None and ts:
        candidate = artifacts / f"adg_enforcement_report_{ts}.json"
        if candidate.is_file():
            enforcement_report = candidate
    if enforcement_report is None:
        enforcement_report = _resolve_latest("adg_enforcement_report_*.json", artifacts)

    missing: list[str] = []
    if gate_path is None or not gate_path.is_file():
        missing.append("gate_results")
    if not burndown_path.is_file():
        missing.append("burndown")
    if missing:
        print(f"[adg_review_template] REVIEW_TEMPLATE_ERROR=missing {', '.join(missing)}", file=sys.stderr)
        return (1 if fail_closed else 0, None)

    assert gate_path is not None
    try:
        doc = build_review_template(
            gate_results_path=gate_path,
            burndown_path=burndown_path,
            action_queue_path=action_queue,
            generation_manifest_path=generation_manifest,
            enforcement_report_path=enforcement_report,
            run_id=ts,
        )
        errors = validate_review_template(doc)
        if errors:
            print(f"[adg_review_template] REVIEW_TEMPLATE_ERROR={errors[0]}", file=sys.stderr)
            return (1 if fail_closed else 0, None)

        if output_path is None:
            if ts:
                out_name = f"adg_review_template_{ts}.json"
            else:
                stem = gate_path.stem.replace("adg_gate_results_", "")
                out_name = f"adg_review_template_{stem}.json"
            output_path = artifacts / out_name

        _write_text_artifact(output_path, json.dumps(doc, indent=2, sort_keys=True) + "\n")
        yaml_path = output_path.with_suffix(".yaml")
        if write_yaml:
            _write_text_artifact(yaml_path, _dump_yaml(doc))

        if write_latest:
            _write_text_artifact(
                REVIEW_TEMPLATE_LATEST,
                json.dumps(doc, indent=2, sort_keys=True) + "\n",
            )
            if write_yaml:
                _write_text_artifact(REVIEW_TEMPLATE_YAML_LATEST, _dump_yaml(doc))
            _write_text_artifact(
                REVIEW_TEMPLATE_DOCS_LATEST,
                json.dumps(doc, indent=2, sort_keys=True) + "\n",
            )
            if write_yaml:
                _write_text_artifact(REVIEW_TEMPLATE_DOCS_YAML_LATEST, _dump_yaml(doc))

        if print_inline and not _inline_bypassed():
            inline = render_inline_review_template(doc, output_path=output_path)
            sys.stdout.write("\n")
            sys.stdout.write(inline)
            if not inline.endswith("\n"):
                sys.stdout.write("\n")
            print(
                "[adg_review_template] inline markdown emitted to stdout for Cursor display",
                file=sys.stderr,
            )
        elif _inline_bypassed():
            print(
                "[adg_review_template] WARNING: inline stdout suppressed "
                "(ADG_REVIEW_TEMPLATE_INLINE_BYPASS=1)",
                file=sys.stderr,
            )

        print(f"[adg_review_template] REVIEW_TEMPLATE={_repo_rel(output_path)}", file=sys.stderr)
        if write_yaml:
            print(f"[adg_review_template] REVIEW_TEMPLATE_YAML={_repo_rel(yaml_path)}", file=sys.stderr)
        return (0, output_path)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"[adg_review_template] REVIEW_TEMPLATE_ERROR={exc}", file=sys.stderr)
        return (1 if fail_closed else 0, None)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit ADG run review template JSON.")
    parser.add_argument("--gate-results", type=Path, default=None)
    parser.add_argument("--burndown", type=Path, default=None)
    parser.add_argument("--action-queue", type=Path, default=None)
    parser.add_argument("--generation-manifest", type=Path, default=None)
    parser.add_argument("--enforcement-report", type=Path, default=None)
    parser.add_argument("--ts", default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--no-latest", action="store_true")
    parser.add_argument("--no-yaml", action="store_true")
    parser.add_argument("--no-inline", action="store_true")
    args = parser.parse_args(argv)

    rc, _path = emit_mandatory_adg_review_template(
        ts=args.ts,
        gate_results=args.gate_results,
        burndown=args.burndown,
        action_queue=args.action_queue,
        generation_manifest=args.generation_manifest,
        enforcement_report=args.enforcement_report,
        output_path=args.out,
        write_latest=not args.no_latest,
        write_yaml=not args.no_yaml,
        print_inline=not args.no_inline,
        fail_closed=True,
    )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
