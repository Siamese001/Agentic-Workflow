"""W1 (apps-rg-insurtech-ey-unlock-a4c0f0) — InsurTech/EY role-episode bundle foundation.

Deterministic, hermetic. Guards the dependency-root invariants for the two new employer lanes:

1. Both bundle JSONs are well-formed and mirror the IBM/Unify role-episode schema.
2. Identity (employer, node_id, dates) is taken from the static employment spine — not invented.
3. Every graph_skill_node_id resolves to a real node in the master skills graph (grounding rule).
4. section_eligibility targets only the matching employer's generated lanes.
5. Metric outcome nodes are graph-native, approved by presence, and bundle-linked.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FI = REPO / "apps_rg" / "fact_inventory"
LEDGER = FI / "master_skills_arsenal_ledger.json"
BASE_RESUME = REPO / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"

REQUIRED_BUNDLE_FIELDS = {
    "role_episode_bundle_id",
    "employer",
    "title",
    "employer_node_id",
    "bundle_theme",
    "graph_skill_node_ids",
    "linked_source_fact_ids",
    "linked_metric_outcome_ids",
    "held_metrics",
    "excluded_metrics",
    "section_eligibility",
    "config_gate",
}

CASES = [
    {
        "file": FI / "insurtech_role_episode_bundles.json",
        "employer": "InsurTech Cloud Solutions",
        "node_id": "employment_exp_insurtech_001",
        "lanes": {"insurtech_bullets", "insurtech_narrative"},
        "source_fact": "exp_insurtech_001",
        "bundle_count": 12,
        "extra_required": {"claim_text", "support_level", "metric_candidates"},
    },
    {
        "file": FI / "ey_role_episode_bundles.json",
        "employer": "Ernst & Young",
        "node_id": "employment_exp_ey_001",
        "lanes": {"ey_bullets", "ey_narrative"},
        "source_fact": "exp_ey_001",
        "bundle_count": 5,
        "extra_required": {"claim_text", "support_level", "metric_candidates"},
    },
]

INSURTECH_REQUIRED_ROOTS = {
    "reb_insurtech_founder_led_market_creation",
    "reb_insurtech_founder_led_gtm_revenue",
    "reb_insurtech_lean_delivery_operating_model",
    "reb_insurtech_public_vs_private_cloud_strategy",
    "reb_insurtech_aws_cloud_economics",
    "reb_insurtech_aws_migration_execution",
    "reb_insurtech_aws_shared_responsibility_operating_model",
    "reb_insurtech_insurance_regulatory_cloud_adoption_standards",
    "reb_insurtech_regulated_aws_control_implementation",
    "reb_insurtech_aws_guidewire_core_modernization",
    "reb_insurtech_insurance_data_bi_decisioning",
    "reb_insurtech_resilient_core_operations",
}

EY_REQUIRED_ROOTS = {
    "reb_ey_regulatory_analytics_modernization",
    "reb_ey_capital_optimization_solvency",
    "reb_ey_ccar_capital_liquidity_stress_testing",
    "reb_ey_insurance_core_modernization",
    "reb_ey_erm_risk_governance",
}

GENERIC_METRIC_FORBIDDEN_SUBSTRINGS = {
    "saved $10m",
    "$10m tco",
    "10m tco",
    "generic tco",
}


def _real_graph_node_ids() -> set[str]:
    """A graph skill node is real if it resolves in EITHER the graph_nodes index (node_id) OR
    the skill_rows index (skill_id). The role-episode evidence module enriches bound_skills from
    skill_rows; higher-level nodes live in graph_nodes. Either is a valid grounding reference."""
    led = json.loads(LEDGER.read_text(encoding="utf-8"))
    nodes = {str(n.get("node_id")) for n in led.get("graph_nodes", []) if isinstance(n, dict)}
    rows = {str(r.get("skill_id")) for r in led.get("skill_rows", []) if isinstance(r, dict)}
    return nodes | rows


def _base_employment(fact_id: str) -> dict:
    base = json.loads(BASE_RESUME.read_text(encoding="utf-8"))
    found: dict = {}

    def walk(o: object) -> None:
        nonlocal found
        if isinstance(o, dict):
            if o.get("fact_id") == fact_id and o.get("employer"):
                found = o
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(base)
    return found


def test_bundles_wellformed_and_identity_verbatim() -> None:
    for c in CASES:
        doc = json.loads(c["file"].read_text(encoding="utf-8"))
        assert doc["employer"] == c["employer"]
        assert doc["employer_node_id"] == c["node_id"]
        assert doc["bundles"], "no bundles"
        emp = _base_employment(c["source_fact"])
        assert emp, f"base-resume employment {c['source_fact']} not found"
        # Identity must be verbatim from the base resume (dates window endpoints present).
        assert emp["start_date"] in doc["time_window"]
        assert emp["end_date"] in doc["time_window"]
        assert doc["employer"] == emp["employer"]


def test_every_graph_skill_node_resolves() -> None:
    real = _real_graph_node_ids()
    assert real, "ledger graph_nodes empty — fixture drift"
    for c in CASES:
        doc = json.loads(c["file"].read_text(encoding="utf-8"))
        for b in doc["bundles"]:
            assert b["graph_skill_node_ids"], f"{b['role_episode_bundle_id']} empty skills"
            unresolved = [s for s in b["graph_skill_node_ids"] if s not in real]
            assert not unresolved, f"{b['role_episode_bundle_id']} unresolved skill nodes: {unresolved}"


def test_bundle_required_fields_and_employer_consistency() -> None:
    for c in CASES:
        doc = json.loads(c["file"].read_text(encoding="utf-8"))
        for b in doc["bundles"]:
            missing = (REQUIRED_BUNDLE_FIELDS | c["extra_required"]) - set(b)
            assert not missing, f"{b.get('role_episode_bundle_id')} missing {missing}"
            assert b["employer"] == c["employer"]
            assert b["employer_node_id"] == c["node_id"]
            assert set(b["section_eligibility"]) <= c["lanes"]
            assert c["source_fact"] in b["linked_source_fact_ids"]


def test_expected_bundles_per_employer() -> None:
    for c in CASES:
        doc = json.loads(c["file"].read_text(encoding="utf-8"))
        assert len(doc["bundles"]) == c["bundle_count"]
        ids = {b["role_episode_bundle_id"] for b in doc["bundles"]}
        assert len(ids) == c["bundle_count"], "duplicate role_episode_bundle_id"


def test_metric_outcome_nodes_are_graph_ssot_and_bundle_linked() -> None:
    # Graph metric nodes are the claim surface. Candidate/deferred metrics are not proof.
    for c in CASES:
        doc = json.loads(c["file"].read_text(encoding="utf-8"))
        nodes = doc.get("metric_outcome_nodes") or {}
        approved = doc.get("approved_metric_outcome_ids") or {}
        policy = doc.get("metric_surface_policy") or {}
        assert nodes, f"{c['file'].name} missing metric_outcome_nodes"
        assert set(nodes) == set(approved)
        assert policy.get("approval_model") == "presence_in_metric_outcome_nodes_is_approval"
        assert policy.get("approved_metric_outcome_ids_role") == "derived_review_index_not_claim_authority"
        assert policy.get("bundle_metric_surface") == (
            "linked_metric_outcome_ids only; metric_outcome_nodes is claim authority"
        )

        linked_seen: set[str] = set()
        for mid, node in nodes.items():
            assert node["metric_outcome_id"] == mid
            assert node["employer"] == c["employer"]
            assert "time_window" not in node
            assert node["approved"] is True
            assert node["approval_status"] == "APPROVED_GRAPH_SSOT"
            assert node["support_level"] == "approved_by_graph_presence"
            assert node["bundle_bindings"], f"{mid} missing bundle_bindings"
            assert node["metric"].strip(), f"{mid} missing metric label"

        for b in doc["bundles"]:
            linked = list(b.get("linked_metric_outcome_ids") or [])
            assert linked, f"{b['role_episode_bundle_id']} missing linked metric ids"
            assert "promotable_metrics" not in b
            for mid in linked:
                assert mid in nodes, f"{b['role_episode_bundle_id']} links unknown metric {mid}"
                assert b["role_episode_bundle_id"] in nodes[mid]["bundle_bindings"]
                linked_seen.add(mid)
            for hm in b.get("held_metrics", []):
                assert "HOLD" in hm and "source artifact required" in hm, f"held metric needs provenance: {hm}"

        assert linked_seen == set(nodes)


def test_role_episode_graphs_do_not_use_base_resume_bullet_ids_as_proof() -> None:
    forbidden_by_file = {
        FI / "insurtech_role_episode_bundles.json": "bul_insurtech_",
        FI / "ey_role_episode_bundles.json": "bul_ey_",
    }
    for path, forbidden in forbidden_by_file.items():
        raw = path.read_text(encoding="utf-8")
        assert forbidden not in raw


def test_insurtech_roots_are_mece_and_reviewable_with_derived_edges() -> None:
    doc = json.loads((FI / "insurtech_role_episode_bundles.json").read_text(encoding="utf-8"))
    ids = {b["role_episode_bundle_id"] for b in doc["bundles"]}
    assert ids == INSURTECH_REQUIRED_ROOTS
    for b in doc["bundles"]:
        serialized = json.dumps(b, sort_keys=True)
        assert "graph_edge_contract" not in b
        assert "root_to_skill_edges" not in serialized
        assert b["employer_node_id"] == "employment_exp_insurtech_001"
        assert b["graph_skill_node_ids"], f"{b['role_episode_bundle_id']} missing skill edges"
        assert b["claim_text"].strip(), f"{b['role_episode_bundle_id']} missing claim_text"
        assert b["linked_metric_outcome_ids"], f"{b['role_episode_bundle_id']} missing linked metric ids"


def test_insurtech_deferred_metrics_are_not_graph_claim_authority() -> None:
    doc = json.loads((FI / "insurtech_role_episode_bundles.json").read_text(encoding="utf-8"))
    candidates = list(doc.get("metric_candidates_for_approval") or [])
    for b in doc["bundles"]:
        candidates.extend(b.get("metric_candidates") or [])

    assert candidates, "InsurTech should retain held/deferred metric candidates as audit backlog"
    for m in candidates:
        status = str(m.get("approval_status") or "")
        assert status != "APPROVED_GRAPH_SSOT"
        assert m.get("claim_authority") == "not_claimable_until_promoted_to_metric_outcome_nodes" or status.startswith("HELD")
        haystack = json.dumps(m, sort_keys=True).lower()
        forbidden = [s for s in GENERIC_METRIC_FORBIDDEN_SUBSTRINGS if s in haystack]
        assert not forbidden, f"generic metric language leaked into {m.get('metric_id')}: {forbidden}"
        assert "proof_shape" in m and m["proof_shape"], f"{m.get('metric_id')} missing proof_shape"

    for node in (doc.get("metric_outcome_nodes") or {}).values():
        approved_surface = " ".join(
            [
                str(node.get("metric") or ""),
                str(node.get("claim_text") or ""),
                " ".join(str(x) for x in node.get("surface_tokens") or []),
            ]
        ).lower()
        assert "tco" not in approved_surface


def test_ey_roots_are_complete_without_typed_edge_payloads() -> None:
    doc = json.loads((FI / "ey_role_episode_bundles.json").read_text(encoding="utf-8"))
    ids = {b["role_episode_bundle_id"] for b in doc["bundles"]}
    assert ids == EY_REQUIRED_ROOTS
    invariants = doc.get("invariants") or {}
    assert "phase_plan" not in doc
    assert "typed_edge_policy" not in invariants
    assert "edge_model" not in invariants
    assert "graph_edge_contract_policy" not in invariants
    for b in doc["bundles"]:
        serialized = json.dumps(b, sort_keys=True)
        assert "graph_edge_contract" not in b
        assert "root_to_skill_edges" not in serialized
        assert "edge_type" not in serialized
        assert b["claim_text"].strip(), f"{b['role_episode_bundle_id']} missing claim_text"
        assert b["support_level"].strip(), f"{b['role_episode_bundle_id']} missing support_level"
        assert b["linked_metric_outcome_ids"], f"{b['role_episode_bundle_id']} missing linked metric ids"


def test_ey_metrics_are_promoted_to_graph_nodes_not_stale_candidates() -> None:
    doc = json.loads((FI / "ey_role_episode_bundles.json").read_text(encoding="utf-8"))
    candidates = list(doc.get("metric_candidates_for_approval") or [])
    for b in doc["bundles"]:
        candidates.extend(b.get("metric_candidates") or [])

    assert candidates == []
    nodes = doc.get("metric_outcome_nodes") or {}
    assert len(nodes) >= 18
    approved_blob = json.dumps(nodes, sort_keys=True).lower()
    forbidden = [s for s in GENERIC_METRIC_FORBIDDEN_SUBSTRINGS if s in approved_blob]
    assert not forbidden
