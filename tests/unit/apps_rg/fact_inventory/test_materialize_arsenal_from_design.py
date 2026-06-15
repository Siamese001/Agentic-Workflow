from __future__ import annotations

from apps_rg.fact_inventory import materialize_arsenal_from_design as materialize


def test_activation_and_matrix_rows_preserve_visibility_and_claim_policy() -> None:
    assert materialize._activation_and_visibility("USER_CONFIRMED_PENDING_SOURCE", True) == (
        "DRAFT",
        "human_confirm",
        True,
    )
    assert materialize._activation_and_visibility("BLOCKED", False) == ("RETIRED", "never_external", True)

    row = materialize._matrix_revops_row(
        {
            "skill_id": "skill_salesforce_pipeline_analytics",
            "skill": "salesforce_pipeline_analytics",
            "support_status": "DERIVED_SUPPORTED",
            "linked_fact_id": "fact_1",
            "source_resume_file": "resume.txt",
            "source_evidence": "Built pipeline analytics.",
            "role_relevance": ["REVENUE_OPERATIONS"],
            "allowed_phrases": ["pipeline analytics"],
            "where_to_use": ["executive_summary"],
            "risk_notes": "medium risk",
        }
    )

    assert row["pillar"] == materialize.PILLAR_REVOPS
    assert row["external_claim_policy"] == "derived_supported_with_fact"
    assert row["evidence_risk"] == "medium"
    assert row["role_family_weights"] == {"REVENUE_OPERATIONS": 1.0}


def test_build_ledger_payload_wraps_w4a_package_and_validation_rules(monkeypatch) -> None:
    def fake_w4a_graph_package(*, pillars, legacy_skill_rows, bridge_specs):
        assert pillars == [
            {
                "pillar_id": "pillar_revenue_operations",
                "name": "Revenue Ops",
                "description": "Revenue operations",
                "subskills": [],
                "linked_fact_ids": [],
                "allowed_phrases": [],
                "forbidden_phrases_without_stronger_support": [],
                "role_family_weights": {},
                "section_fit": {},
                "archive_snippets": [],
                "evidence_sources": [],
                "user_confirmed_pending_source": [],
            }
        ]
        assert legacy_skill_rows[0]["skill_id"] == "skill_salesforce_pipeline_analytics"
        assert bridge_specs == [{"edge": "bridge"}]
        return {
            "skill_rows": [{"skill_id": "skill_salesforce_pipeline_analytics"}],
            "graph_metadata": {"deep_agentic_row_count": 7, "edge_count": 3},
            "graph_layers": [],
            "graph_nodes": [],
            "graph_edges": [],
            "external_claim_policies": [],
            "agentic_runtime_matrix": [],
            "agentic_capability_domains": [{"domain_id": "domain"}],
            "graph_validation_rules": {"ok": True},
            "resume_generation_policy": {"policy": "ok"},
        }

    monkeypatch.setattr(materialize, "build_w4a_graph_package", fake_w4a_graph_package)

    payload = materialize.build_ledger_payload(
        {
            "capability_taxonomy": [
                {
                    "pillar_id": "pillar_revenue_operations",
                    "name": "Revenue Ops",
                    "description": "Revenue operations",
                }
            ],
            "revenue_operations_matrix": [
                {
                    "skill_id": "skill_salesforce_pipeline_analytics",
                    "skill": "salesforce_pipeline_analytics",
                    "support_status": "DERIVED_SUPPORTED",
                    "linked_fact_id": "fact_1",
                    "role_relevance": ["REVENUE_OPERATIONS"],
                }
            ],
            "senior_role_bridge_edges": [{"edge": "bridge"}],
        }
    )

    assert payload["metadata"]["schema_version"] == "master_skills_arsenal_graph_v1"
    assert payload["metadata"]["skill_row_count"] == 1
    assert payload["metadata"]["deep_agentic_row_count"] == 7
    assert payload["metadata"]["capability_domain_count"] == 1
    assert payload["validation_rules"]["jd_briefing_never_proof"] is True
