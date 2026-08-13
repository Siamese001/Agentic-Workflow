from __future__ import annotations

# apps-test-model: APP CONTRACT
import json
import sys
from pathlib import Path

import pytest

from apps_rg.fact_inventory.apply_c03_graph_full_zero_loss_overwrite import (
    apply_overwrite,
)
from apps_rg.fact_inventory.graph_metric_heterogeneity_policy import (
    POLICY_VERSION,
    diversity_summary,
    infer_metric_bucket,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    graph_node_requires_source_refs,
)
from apps_rg.fact_inventory.validate_c03_graph_hardening import (
    main as validate_main,
)
from apps_rg.fact_inventory.validate_c03_graph_hardening import (
    validate_c03_graph_hardening_payload,
)

REPO = Path(__file__).resolve().parents[4]
LEDGER_PATH = REPO / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"


def _provenance_complete_canonical_payload() -> dict:
    payload = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    for node in payload["graph_nodes"]:
        if graph_node_requires_source_refs(node) and not node.get("source_refs"):
            node["source_refs"] = [f"fixture://provenance/{node['node_id']}"]
    return payload


def _base_payload():
    return {
        "metadata": {"w4a_hardened": True},
        "support_levels": ["DIRECT_FROM_RESUME_ARCHIVE", "INTERNAL_ONLY"],
        "visibility_rules": ["internal_runtime_only", "internal_runtime_and_resume_when_fact_backed"],
        "activation_statuses": ["ACTIVE_CONFIRMED"],
        "pillars": [],
        "skill_rows": [],
        "actuarial_career_matrix": {},
        "partner_gtm_matrix": {},
        "role_family_projection_profiles": {},
        "validation_rules": {},
        "graph_metadata": {},
        "graph_layers": [],
        "graph_nodes": [
            {
                "node_id": "existing_node",
                "node_type": "capability_domain",
                "label": "Existing",
                "description": "Existing node retained.",
                "support_level": "INTERNAL_ONLY",
                "visibility_rule": "internal_runtime_only",
                "activation_status": "ACTIVE_CONFIRMED",
                "evidence_risk": "low",
                "source_refs": [],
                "projection_behavior": "existing",
                "external_claim_policy": "internal_only",
            },
            {
                "node_id": "existing_skill",
                "node_type": "skill",
                "label": "Existing skill",
                "description": "Existing skill node retained.",
                "support_level": "INTERNAL_ONLY",
                "visibility_rule": "internal_runtime_only",
                "activation_status": "ACTIVE_CONFIRMED",
                "evidence_risk": "low",
                "source_refs": [],
                "projection_behavior": "existing",
                "external_claim_policy": "internal_only",
            },
        ],
        "graph_edges": [
            {
                "edge_id": "existing_edge",
                "edge_type": "capability_domain_contains_skill",
                "source_node_id": "existing_node",
                "target_node_id": "existing_skill",
                "rationale": "Existing edge retained.",
                "projection_behavior": "existing",
                "external_claim_policy": "internal_only",
                "validation_status": "ACTIVE_CONFIRMED",
            }
        ],
        "external_claim_policies": [],
        "agentic_runtime_matrix": {},
        "agentic_capability_domains": [],
        "graph_validation_rules": {},
        "resume_generation_policy": {},
    }


def test_apply_overwrite_is_append_only_and_idempotent():
    payload = _base_payload()
    first = apply_overwrite(payload)
    second = apply_overwrite(payload)
    assert first["before"]["graph_nodes"] == 2
    assert first["after"]["graph_nodes"] > first["before"]["graph_nodes"]
    assert second["added_nodes"] == []
    assert second["added_skills"] == []
    assert second["added_edges"] == []
    assert any(n["node_id"] == "existing_node" for n in payload["graph_nodes"])
    assert any(e["edge_id"] == "existing_edge" for e in payload["graph_edges"])


def test_validation_hard_fails_when_overwrite_has_insufficient_heterogeneity():
    payload = _base_payload()
    apply_overwrite(payload)
    with pytest.raises(ValueError, match="GRAPH_METRIC_HETEROGENEITY"):
        validate_c03_graph_hardening_payload(payload)


def test_validation_accepts_current_canonical_provenance():
    payload = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    receipt = validate_c03_graph_hardening_payload(payload)
    assert receipt["status"] == "PASS"
    assert receipt.get("issues", []) == []


def test_validation_passes_for_provenance_complete_canonical_fixture():
    payload = _provenance_complete_canonical_payload()
    receipt = validate_c03_graph_hardening_payload(payload)
    assert receipt["status"] == "PASS"
    assert receipt["heterogeneity_warnings"] == []
    assert receipt["diversity_summary"]["max_same_metric_bucket_share"] <= 0.34


@pytest.mark.parametrize("tampered_field", ["version", "summary"])
def test_validation_recomputes_stored_heterogeneity_receipt(tampered_field: str) -> None:
    payload = _provenance_complete_canonical_payload()
    marker = payload["metadata"]["c03_actual_graph_full_zero_loss_overwrite"]
    if tampered_field == "version":
        marker["metric_heterogeneity_policy_version"] = "self_attested.v999"
    else:
        marker["diversity_summary"]["row_count"] += 1
    with pytest.raises(ValueError, match="GRAPH_METRIC_HETEROGENEITY_STORED_PARITY"):
        validate_c03_graph_hardening_payload(payload)


def test_pipeline_tokens_are_disambiguated_for_metric_heterogeneity():
    assert POLICY_VERSION == "c03_graph_metric_heterogeneity_policy_v2"
    assert infer_metric_bucket("$20M sales pipeline growth") == "revenue_growth"
    assert infer_metric_bucket("deal pipeline conversion") == "revenue_growth"
    assert infer_metric_bucket("deployment pipeline orchestration") == "delivery_velocity"
    assert infer_metric_bucket("narrative architecture") == "general_business_outcome"
    payload = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    assert diversity_summary(payload["skill_rows"])["max_same_metric_bucket_share"] <= 0.34


def test_hardening_validator_cli_is_stdout_only_unless_output_is_explicit(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    canonical_fixture = tmp_path / "canonical.json"
    canonical_fixture.write_text(
        json.dumps(_provenance_complete_canonical_payload(), indent=2) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["validate_c03_graph_hardening", "--graph-path", str(canonical_fixture)],
    )
    validate_main()
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["status"] == "PASS"
    assert not (tmp_path / "docs").exists()

    output = tmp_path / "explicit" / "hardening.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_c03_graph_hardening",
            "--graph-path",
            str(canonical_fixture),
            "--output",
            str(output),
        ],
    )
    validate_main()
    assert json.loads(capsys.readouterr().out)["status"] == "PASS"
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "PASS"


def test_hardening_validator_cli_emits_structured_pass_receipt(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    validate_main(["--graph-path", str(LEDGER_PATH)])
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["status"] == "PASS"
    assert receipt["issues"] == []
    assert not (tmp_path / "docs").exists()
