from __future__ import annotations

from tools.reports.adg_bcg_adapter import (
    build_bcg_brief,
    build_deprecation_deletion_plan,
    render_bcg_brief_md,
)


def test_render_bcg_brief_md_uses_shared_business_and_technical_style() -> None:
    brief = build_bcg_brief(
        title="BCG Sample Brief",
        status="PASS",
        business_read="Fix the blocker first, then clean the waste.",
        technical_read=["FIX gates: 1", "TRACK gates: 2"],
        priority_rule="Blockers before backlog.",
        priority_rows=[
            {
                "priority": 1,
                "move": "Fix blocker",
                "scope": "P0",
                "business_reason": "Keeps the run credible.",
                "technical_reason": "1 red gate.",
                "why_this_rank": "Blocks green.",
                "decision": "now",
            }
        ],
        why_this_order=["Confirmed waste first.", "Noise comes after evidence is clean."],
        next_step="Fix blocker",
    )

    md = render_bcg_brief_md(brief)

    assert "Maintain SVP engineer-level repo standards" in md
    assert "### BCG Sample Brief" in md
    assert "- **Business read:** Fix the blocker first, then clean the waste." in md
    assert "| Priority | Move | Scope | Business reason | Technical reason | Why this order | Decision |" in md
    assert "Why this order:" in md


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
    assert "Confirmed dead code first" in plan["brief"]["priority_rule"]
