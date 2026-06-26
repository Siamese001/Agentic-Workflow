from __future__ import annotations

from tools.reports.adg_bcg_adapter import (
    build_bcg_brief,
    build_report_bcg_findings,
    has_bcg_findings,
    build_deprecation_deletion_plan,
    render_bcg_brief_md,
)


def test_render_bcg_brief_md_uses_shared_business_and_technical_style() -> None:
    brief = build_bcg_brief(
        title="BCG Sample Brief",
        status="PASS",
        status_label="Source status",
        secondary_statuses={"Decision status": "BLOCKED"},
        business_read="Fix the blocker first, then clean the waste.",
        technical_read=["FIX gates: 1", "TRACK gates: 2"],
        priority_rule="Blockers before backlog.",
        priority_rows=[
            {
                "priority": 1,
                "move": "Fix blocker",
                "why_it_matters": "Keeps the run credible.",
                "evidence": "1 red gate.",
                "next_step": "Fix the blocker now.",
                "business_reason": "Keeps the run credible.",
                "technical_reason": "1 red gate.",
                "why_this_rank": "Blocks green.",
                "decision": "now",
                "decision_options": [{"label": "Fix", "description": "Remove the direct dependency."}],
                "done_condition": "The gate is green.",
            }
        ],
        why_this_order=["Confirmed waste first.", "Noise comes after evidence is clean."],
        next_step="Fix blocker",
    )

    md = render_bcg_brief_md(brief)

    assert "Maintain SVP engineer-level repo standards" in md
    assert "### BCG Sample Brief" in md
    assert "- **Source status:** PASS" in md
    assert "- **Decision status:** BLOCKED" in md
    assert "- **Status:** PASS" not in md
    assert "- **Business read:** Fix the blocker first, then clean the waste." in md
    assert "| Priority | Move | Why it matters | Evidence | Next step |" in md
    assert "Business reason" not in md
    assert "Technical reason" not in md
    assert "Why this order" not in md
    assert "fix_blocker" not in md
    row = brief["priority_rows"][0]
    assert row["decision_options"]
    assert row["done_condition"] == "The gate is green."


def test_deprecation_deletion_plan_brief_prioritizes_dead_code_before_noise() -> None:
    plan = build_deprecation_deletion_plan(
        {
            "status": "PASS",
            "summary": {
                "total_dead_imports": 0,
                "total_dead_code_candidates": 2,
                "total_unresolved_imports": 17,
                "first_party_low_confidence_ratio": 2.5,
                "inferred_symbol_ratio": 9.0,
            },
            "dead_code_candidates": {
                "dead_code_hotspots": [
                    ("ADG::Module::legacy_path", 4),
                    ("ADG::Module::stale_path", 2),
                ]
            },
            "unresolved_imports": {"unresolved_hotspots": [("ADG::Module::tests/foo.py", 7)]},
            "low_confidence_zones": {"first_party_low_confidence_ratio": 2.5},
            "inferred_symbols": {"inferred_symbol_ratio": 9.0},
        },
        None,
        None,
    )

    assert plan["summary"]["cleanup_candidate_count"] == 0
    assert plan["priority_rows"][0]["scope"] == "ADG::Module::legacy_path"
    assert plan["priority_rows"][0]["decision"] == "delete_after_deprecation"
    assert plan["brief"]["title"] == "BCG Deletion Brief"
    assert plan["brief"]["status"] == "DELETION_CANDIDATES"
    assert plan["brief"]["status_label"] == "Deletion status"
    assert "Confirmed dead code first" in plan["brief"]["priority_rule"]


def test_deprecation_deletion_plan_labels_no_delete_status_not_source_pass() -> None:
    plan = build_deprecation_deletion_plan(
        {
            "status": "PASS",
            "summary": {
                "total_dead_imports": 0,
                "total_dead_code_candidates": 0,
                "total_unresolved_imports": 17,
            },
            "dead_code_candidates": {"dead_code_hotspots": []},
            "unresolved_imports": {"unresolved_hotspots": [("ADG::Module::tests/foo.py", 7)]},
        },
        None,
        None,
    )

    md = render_bcg_brief_md(plan["brief"])

    assert "- **Deletion status:** NO_DELETIONS_APPROVED" in md
    assert "- **Source report status:** PASS" in md
    assert "- **Status:** PASS" not in md


def test_build_report_bcg_findings_emits_required_management_story() -> None:
    findings = build_report_bcg_findings(
        report_kind="adg_test_report",
        title="BCG Test Brief",
        status="BLOCKED",
        status_label="Decision status",
        business_read="Fix the blocker before funding cleanup.",
        technical_read=["FIX gates: 1", "TRACK gates: 2"],
        priority_rule="Blockers before backlog.",
        priority_rows=[
            {
                "priority": 1,
                "move": "Fix blocker",
                "why_it_matters": "The run is not decision-grade while blocked.",
                "evidence": "1 red gate.",
                "next_step": "Fix and rerun ADG.",
            }
        ],
        why_this_order=["Blockers stop the line."],
        next_step="Fix and rerun ADG.",
    )

    assert findings["schema_version"] == "1.0"
    assert findings["report_kind"] == "adg_test_report"
    assert findings["brief"]["title"] == "BCG Test Brief"
    assert findings["business_read"] == "Fix the blocker before funding cleanup."
    assert findings["priority_rows"][0]["move"] == "Fix blocker"
    assert has_bcg_findings({"bcg_findings": findings}) is True
    assert has_bcg_findings({"brief": findings["brief"]}) is True
    assert has_bcg_findings({"not_bcg": {}}) is False
