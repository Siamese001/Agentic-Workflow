from __future__ import annotations

import json
from pathlib import Path

from apps_rg.fact_inventory.c03_graph_authority_reconciliation import (
    reconcile_graph_authority,
)
from apps_rg.fact_inventory.c03_skill_assertion_corpus import (
    build_skill_assertion_corpus,
    canonical_sha256,
    validate_skill_assertion_corpus,
)


ROOT = Path(__file__).resolve().parents[4]


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _corpus() -> tuple[dict, dict]:
    graph = reconcile_graph_authority(
        _load("apps_rg/fact_inventory/master_skills_arsenal_ledger.json")
    )
    facts = _load(
        "artifacts/apps_rg/fact_inventory/"
        "master_candidate_skills_fact_ledger_20260518T1100Z.json"
    )
    resume = _load("apps_rg/resume/base/amit_ayer_base_resume_v1.json")
    corpus = build_skill_assertion_corpus(
        graph_payload=graph,
        candidate_fact_payload=facts,
        base_resume_payload=resume,
    )
    return graph, corpus


def test_corpus_has_one_assertion_per_eligible_skill_and_explicit_exclusions() -> None:
    graph, corpus = _corpus()
    eligible = {row["skill_id"] for row in graph["skill_rows"] if row["retrieval_eligible"]}
    excluded = {row["skill_id"] for row in graph["skill_rows"] if not row["retrieval_eligible"]}

    assert {row["assertion_id"] for row in corpus["assertions"]} == eligible
    assert {row["skill_id"] for row in corpus["exclusions"]} == excluded
    assert corpus["counts"] == {
        "canonical_skill_count": 254,
        "eligible_assertion_count": len(eligible),
        "non_retrieval_eligible_count": len(excluded),
    }
    assert len(corpus["assertions"]) == len(eligible)
    assert all(row["reason"] for row in corpus["exclusions"])


def test_assertions_bind_semantics_facts_lineage_sections_and_digests() -> None:
    _graph, corpus = _corpus()
    for assertion in corpus["assertions"]:
        assert assertion["assertion_id"] == assertion["skill_id"]
        assert assertion["semantic_card"]["label"]
        assert assertion["fact_links"]
        assert assertion["source_lineage"]
        assert assertion["allowed_sections"]
        assert assertion["authority_envelope_sha256"]
        unsigned = dict(assertion)
        digest = unsigned.pop("assertion_document_sha256")
        assert digest == canonical_sha256(unsigned)


def test_corpus_is_deterministic_and_self_validating() -> None:
    graph, first = _corpus()
    _graph, second = _corpus()
    assert first == second
    assert validate_skill_assertion_corpus(first, graph_payload=graph) == []

    unsigned = dict(first)
    digest = unsigned.pop("corpus_sha256")
    assert digest == canonical_sha256(unsigned)

