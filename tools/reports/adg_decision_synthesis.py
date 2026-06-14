"""Shared ADG decision synthesis for report renderers.

This module is intentionally stdlib-only and report-layer-only. It turns raw
``adg_gate_results`` gates into one canonical decision surface so markdown,
JSON, YAML, and burndown projections use the same FIX/TRACK/CLEAR semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools.reports.gate_signal_catalog import display_verdict, display_verdict_sub

BANDS: tuple[str, ...] = ("P0", "P1", "P2", "P3")
BAND_PRIORITY = {band: idx for idx, band in enumerate(BANDS)}


@dataclass(frozen=True)
class GateDecision:
    """Normalized report-layer view of a single ADG gate."""

    gate: dict[str, Any]
    gate_id: str
    band: str
    action: str
    sub: str
    records: int

    @property
    def is_fix(self) -> bool:
        return self.action == "FIX"

    @property
    def is_ratchet_floor(self) -> bool:
        return self.action == "TRACK" and self.sub == "floor"

    @property
    def is_open_non_ratchet(self) -> bool:
        return self.action == "TRACK" and self.sub != "floor"

    @property
    def is_clear(self) -> bool:
        return self.action == "CLEAR"


def _records(gate: dict[str, Any]) -> int:
    try:
        return int(gate.get("violation_count") or 0)
    except (TypeError, ValueError):
        return 0


def normalize_gate(gate: dict[str, Any]) -> GateDecision:
    """Return a canonical decision record for one raw gate row."""

    return GateDecision(
        gate=gate,
        gate_id=str(gate.get("gate_id") or "?"),
        band=str(gate.get("band") or "P3"),
        action=display_verdict(gate),
        sub=display_verdict_sub(gate),
        records=_records(gate),
    )


def normalize_gates(gates: list[dict[str, Any]]) -> list[GateDecision]:
    """Return canonical gate decisions in stable action order."""

    action_order = {"FIX": 0, "TRACK": 1, "CLEAR": 2}
    return sorted(
        (normalize_gate(gate) for gate in gates),
        key=lambda row: (
            BAND_PRIORITY.get(row.band, 99),
            action_order.get(row.action, 99),
            -row.records,
            row.gate_id,
        ),
    )


def band_decision_summary(gates: list[dict[str, Any]]) -> dict[str, dict[str, int | str]]:
    """Summarize gate and record counts by FIX/floor/open/CLEAR buckets."""

    rows: dict[str, dict[str, int | str]] = {
        band: {
            "band": band,
            "total_gates": 0,
            "total_records": 0,
            "fix_gates": 0,
            "fix_records": 0,
            "fix_block_gates": 0,
            "fix_regressed_gates": 0,
            "fix_seed_missing_gates": 0,
            "ratchet_floor_gates": 0,
            "ratchet_floor_records": 0,
            "open_non_ratchet_gates": 0,
            "open_non_ratchet_records": 0,
            "clear_gates": 0,
            "clear_records": 0,
            "status": "PASS",
        }
        for band in BANDS
    }
    for decision in normalize_gates(gates):
        row = rows.setdefault(
            decision.band,
            {
                "band": decision.band,
                "total_gates": 0,
                "total_records": 0,
                "fix_gates": 0,
                "fix_records": 0,
                "fix_block_gates": 0,
                "fix_regressed_gates": 0,
                "fix_seed_missing_gates": 0,
                "ratchet_floor_gates": 0,
                "ratchet_floor_records": 0,
                "open_non_ratchet_gates": 0,
                "open_non_ratchet_records": 0,
                "clear_gates": 0,
                "clear_records": 0,
                "status": "PASS",
            },
        )
        row["total_gates"] = int(row["total_gates"]) + 1
        row["total_records"] = int(row["total_records"]) + decision.records
        if decision.is_fix:
            row["fix_gates"] = int(row["fix_gates"]) + 1
            row["fix_records"] = int(row["fix_records"]) + decision.records
            if decision.sub == "block":
                row["fix_block_gates"] = int(row["fix_block_gates"]) + 1
            elif decision.sub == "regr":
                row["fix_regressed_gates"] = int(row["fix_regressed_gates"]) + 1
            elif decision.sub == "seed":
                row["fix_seed_missing_gates"] = int(row["fix_seed_missing_gates"]) + 1
            row["status"] = "BLOCKED"
        elif decision.is_ratchet_floor:
            row["ratchet_floor_gates"] = int(row["ratchet_floor_gates"]) + 1
            row["ratchet_floor_records"] = int(row["ratchet_floor_records"]) + decision.records
        elif decision.is_open_non_ratchet:
            row["open_non_ratchet_gates"] = int(row["open_non_ratchet_gates"]) + 1
            row["open_non_ratchet_records"] = int(row["open_non_ratchet_records"]) + decision.records
        else:
            row["clear_gates"] = int(row["clear_gates"]) + 1
            row["clear_records"] = int(row["clear_records"]) + decision.records
    return rows


def artifact_consistency_status(*, required_artifacts: list[dict[str, Any]], fail_closed: bool) -> dict[str, Any]:
    """Return fail-open/fail-closed artifact health for review packets."""

    required = [row for row in required_artifacts if row.get("required")]
    missing = [row for row in required if not row.get("exists")]
    status = "ok" if not missing else ("fail_closed" if fail_closed else "fail_open")
    return {
        "status": status,
        "fail_closed": fail_closed,
        "missing_required": [row.get("artifact_key") for row in missing],
        "required_count": len(required),
        "present_required_count": len([row for row in required if row.get("exists")]),
        "present_count": len([row for row in required_artifacts if row.get("exists")]),
        "optional_present_count": len(
            [row for row in required_artifacts if not row.get("required") and row.get("exists")]
        ),
    }


def after_green_plan(band_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a small, deterministic post-green plan from synthesized bands."""

    rows: list[dict[str, Any]] = []
    for band_row in band_rows:
        band = str(band_row.get("band") or "?")
        ratchet = int(band_row.get("ratchet_floor_records") or 0)
        open_work = int(band_row.get("cleanup_records") or band_row.get("open_non_ratchet_records") or 0)
        if ratchet:
            rows.append(
                {
                    "band": band,
                    "work": "burn_down_ratchet_floor",
                    "records": ratchet,
                    "why": "Lowers accepted baseline debt after red gates are green.",
                }
            )
        if open_work:
            rows.append(
                {
                    "band": band,
                    "work": "close_open_non_ratchet_work",
                    "records": open_work,
                    "why": "Closes real open work that does not lower a ratchet floor.",
                }
            )
    return {
        "title": "After-Green Plan",
        "rows": rows,
        "notes": [
            "Red FIX gates remain the first priority.",
            "Once green, burn down ratchet floors before broad non-ratchet cleanup.",
        ],
    }
