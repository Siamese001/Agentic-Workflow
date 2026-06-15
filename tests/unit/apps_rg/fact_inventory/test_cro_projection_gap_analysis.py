from __future__ import annotations

from apps_rg.fact_inventory import build_cro_projection_gap_analysis as cro


def test_build_gap_payload_tracks_underlinked_facts_rejections_and_non_claims(monkeypatch) -> None:
    monkeypatch.setattr(cro, "_archive_mining_notes", lambda: [{"variant": "sales", "status": "PRESENT"}])
    ledger = {
        "role_family_projection_profiles": {
            cro.PROFILE_ID: {
                "label": "CRO composite",
                "role_family_weights": {"REVENUE_OPERATIONS": 0.8},
                "top_weighted_pillars": [{"pillar_id": "pillar_revenue_operations", "weight": 0.9}],
            }
        },
        "pillars": [{"pillar_id": "pillar_revenue_operations", "linked_fact_ids": ["fact_linked"]}],
    }
    candidate = {
        "candidate_facts": [
            {
                "candidate_fact_id": "fact_linked",
                "confidence": "HIGH",
                "role_families_supported": ["REVENUE_OPERATIONS"],
            },
            {
                "candidate_fact_id": "fact_underlinked",
                "confidence": "MEDIUM",
                "role_families_supported": ["CUSTOMER_SUCCESS"],
            },
        ]
    }

    payload = cro.build_gap_payload(
        ledger=ledger,
        design={"stats": {"skills": 10}},
        candidate=candidate,
        wired_facts=[{"candidate_fact_id": "fact_new", "pillar_id": "pillar_customer_stakeholder"}],
        new_skills=["skill_customer_success"],
        rejected=[{"candidate_fact_id": "fact_rejected", "reason": "LOW confidence"}],
    )

    assert payload["profile_label"] == "CRO composite"
    assert payload["archive_mining"] == [{"variant": "sales", "status": "PRESENT"}]
    assert payload["facts_newly_wired"][0]["candidate_fact_id"] == "fact_new"
    assert payload["new_skill_rows"] == ["skill_customer_success"]
    assert payload["facts_rejected"][0]["candidate_fact_id"] == "fact_rejected"
    assert payload["under_linked_commercial_facts_remaining"] == [
        {
            "candidate_fact_id": "fact_underlinked",
            "confidence": "MEDIUM",
            "reason": "not_linked_to_any_pillar_source_refs",
        }
    ]
    assert payload["unsupported_cro_capability_gaps"]
    assert "JD and briefing text are targeting-only; never proof." in payload["explicit_non_claims"]


def test_render_markdown_includes_gap_sections_and_rejected_facts() -> None:
    md = cro.render_markdown(
        {
            "generated_at_utc": "2026-06-15T00:00:00Z",
            "profile_id": cro.PROFILE_ID,
            "profile_label": "CRO composite",
            "standalone_cro_role_family_present": False,
            "role_family_weights": {"REVENUE_OPERATIONS": 0.8},
            "top_weighted_pillars": [{"pillar_id": "pillar_revenue_operations", "weight": 0.9}],
            "facts_newly_wired": [],
            "new_skill_rows": ["skill_customer_success"],
            "facts_rejected": [{"candidate_fact_id": "fact_low", "reason": "LOW confidence"}],
            "under_linked_commercial_facts_remaining": [{"candidate_fact_id": "fact_gap", "confidence": "MEDIUM"}],
            "unsupported_cro_capability_gaps": [
                {"capability_id": "marketing_demand_generation", "description": "Demand gen"}
            ],
            "explicit_non_claims": ["JD and briefing text are targeting-only; never proof."],
        }
    )

    assert "# CRO composite projection" in md
    assert "`fact_low`: LOW confidence" in md
    assert "`fact_gap` (MEDIUM)" in md
    assert "**marketing_demand_generation:** Demand gen" in md
