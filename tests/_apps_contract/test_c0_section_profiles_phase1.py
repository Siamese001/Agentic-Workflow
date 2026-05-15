"""Phase-1: section_retrieval_profile covers six golden apps_rg C0 section IDs."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PROFILE = REPO / "apps_rg" / "config" / "domain_contract" / "section_retrieval_profile.yaml"
FACT_SCHEMA = REPO / "apps_rg" / "config" / "domain_contract" / "fact_vectors_schema.yaml"

GOLDEN_SIX = frozenset(
    {
        "executive_summary",
        "unify_bullets",
        "unify_narrative",
        "ibm_bullets",
        "ibm_narrative",
        "competencies",
    }
)


def test_section_profile_covers_six_golden_ids() -> None:
    pytest.importorskip("yaml")
    import yaml

    data = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
    assert data.get("ssot_collection_strategy", {}).get("primary_collection") == "fact_vectors"
    assert data.get("ssot_collection_strategy", {}).get("embedding_dim") == 1024
    max_sec = data.get("global_constraints", {}).get("max_sections_to_query", 0)
    sections = data.get("sections") or []
    ids = {s["section_id"] for s in sections}
    assert GOLDEN_SIX <= ids, f"missing golden section_ids; have {sorted(ids)}"
    assert max_sec >= len(sections), "max_sections_to_query must cover all configured sections"


def test_fact_vectors_schema_embedding_matches_ssot() -> None:
    pytest.importorskip("yaml")
    import yaml

    data = yaml.safe_load(FACT_SCHEMA.read_text(encoding="utf-8"))
    emb = data.get("embedding") or {}
    assert emb.get("model_id") == "BAAI/bge-m3"
    assert emb.get("dimensions") == 1024
    assert (data.get("metadata_schema") or {}).get("app", {}).get("allowed_values") == ["apps_rg"]
