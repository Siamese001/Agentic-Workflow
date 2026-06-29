from __future__ import annotations

from ops_scripts.ci.verify_adg_report_mece import validate


def _adapter() -> dict:
    return {
        "sections": {
            "fix_now": {
                "rows": [
                    {"gate_id": "10_infra_wiring", "band": "P0", "rows": 3},
                    {"gate_id": "S4_unused_imports_ratchet", "band": "P3", "rows": 10},
                ]
            },
            "burn_down": {"rows": [{"gate_id": "G_REACH_l0_reachability", "band": "P0", "rows": 100}]},
            "kpi_watchlist": {"rows": [{"gate_id": "D2_role_duplication_warn", "band": "P2", "rows": 7}]},
            "clear": {"rows": [{"gate_id": "1_critical_path_integrity", "band": "P0", "rows": 0}]},
        }
    }


def _summary() -> dict:
    return {
        "gate_mece_summary": {
            "decision_gates": [
                {
                    "move": "Repair graph/report consistency",
                    "why_it_matters": "Report mismatch.",
                    "evidence": "1 mismatch.",
                    "next_step": "Repair before ranking.",
                }
            ]
        },
        "canonical_next_best_actions": {
            "rows": [
                {"action_type": "fix_blocker", "scope": "10_infra_wiring", "move": "Clear infra wiring P0 block"},
                {"action_type": "fix_blocker", "scope": "S4_unused_imports_ratchet", "move": "Remove unused-import regression only"},
            ]
        },
    }


def test_verify_adg_report_mece_accepts_separated_decision_and_work_sections() -> None:
    errors = validate(_summary(), _adapter(), "Decision gate:\n\nFix now:\n")

    assert errors == []


def test_verify_adg_report_mece_rejects_decision_gate_in_ranked_actions() -> None:
    summary = _summary()
    summary["canonical_next_best_actions"]["rows"].insert(
        0,
        {
            "action_type": "repair_reporting",
            "scope": "mv_graph_vs_report_mismatches",
            "move": "Repair graph/report consistency",
        },
    )

    errors = validate(summary, _adapter(), "Decision gate:\n\nFix now:\n")

    assert any("decision gate" in error for error in errors)


def test_verify_adg_report_mece_rejects_watchlist_work_overlap() -> None:
    adapter = _adapter()
    adapter["sections"]["burn_down"]["rows"].append({"gate_id": "D2_role_duplication_warn", "band": "P2", "rows": 7})

    errors = validate(_summary(), adapter, "Decision gate:\n\nFix now:\n")

    assert any("KPI/watchlist gate" in error for error in errors)


def test_verify_adg_report_mece_rejects_p3_hygiene_before_p0_live_gate() -> None:
    summary = _summary()
    summary["canonical_next_best_actions"]["rows"] = [
        {"action_type": "fix_blocker", "scope": "S4_unused_imports_ratchet", "move": "Remove unused-import regression only"},
        {"action_type": "fix_blocker", "scope": "10_infra_wiring", "move": "Clear infra wiring P0 block"},
    ]

    errors = validate(summary, _adapter(), "Decision gate:\n\nFix now:\n")

    assert any("P3 hygiene gate" in error for error in errors)


def test_verify_adg_report_mece_rejects_markdown_without_decision_gate() -> None:
    errors = validate(_summary(), _adapter(), "Fix now:\n")

    assert any("missing a Decision gate" in error for error in errors)
