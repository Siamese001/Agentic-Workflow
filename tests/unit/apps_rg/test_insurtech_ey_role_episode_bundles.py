"""W1 (apps-rg-insurtech-ey-unlock-a4c0f0) — InsurTech/EY role-episode bundle foundation.

Deterministic, hermetic. Guards the dependency-root invariants for the two new employer lanes:

1. Both bundle JSONs are well-formed and mirror the IBM/Unify role-episode schema.
2. Identity (employer, node_id, dates) is verbatim from the base resume — not invented.
3. Every graph_skill_node_id resolves to a real node in the master skills graph (grounding rule).
4. section_eligibility targets only the matching employer's generated lanes.
5. The three bundles per employer anchor the three base-resume bullet_ids.
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
    "time_window",
    "employer_node_id",
    "bundle_theme",
    "graph_skill_node_ids",
    "linked_source_fact_ids",
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
    },
    {
        "file": FI / "ey_role_episode_bundles.json",
        "employer": "Ernst & Young",
        "node_id": "employment_exp_ey_001",
        "lanes": {"ey_bullets", "ey_narrative"},
        "source_fact": "exp_ey_001",
    },
]


def _real_graph_node_ids() -> set[str]:
    led = json.loads(LEDGER.read_text(encoding="utf-8"))
    return {str(n.get("node_id")) for n in led.get("graph_nodes", []) if isinstance(n, dict)}


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
            missing = REQUIRED_BUNDLE_FIELDS - set(b)
            assert not missing, f"{b.get('role_episode_bundle_id')} missing {missing}"
            assert b["employer"] == c["employer"]
            assert b["employer_node_id"] == c["node_id"]
            assert set(b["section_eligibility"]) <= c["lanes"]
            assert c["source_fact"] in b["linked_source_fact_ids"]


def test_three_bundles_per_employer() -> None:
    for c in CASES:
        doc = json.loads(c["file"].read_text(encoding="utf-8"))
        assert len(doc["bundles"]) == 3
        ids = {b["role_episode_bundle_id"] for b in doc["bundles"]}
        assert len(ids) == 3, "duplicate role_episode_bundle_id"


def test_no_promotable_metrics_yet_held_are_provenance_tagged() -> None:
    # W1 discipline: base-resume metrics are HELD (single canonical source), not promoted,
    # until the X2 gates (P4) define promotion. No metric is silently promotable.
    for c in CASES:
        doc = json.loads(c["file"].read_text(encoding="utf-8"))
        for b in doc["bundles"]:
            assert b.get("promotable_metrics", []) == [], "no metric should be promotable pre-X2"
            for hm in b.get("held_metrics", []):
                assert "HOLD" in hm and "base_resume" in hm, f"held metric needs provenance: {hm}"
