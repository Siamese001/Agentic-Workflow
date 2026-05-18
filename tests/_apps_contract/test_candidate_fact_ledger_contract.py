"""Contract gates for candidate ledger ingest + taxonomy (no generator seam changes)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from apps_rg.fact_inventory.candidate_fact_ledger import (
    FactUsageBand,
    assert_selection_bounded_to_ledger,
    candidate_fact_tag_universe,
    fact_usage_band,
    jd_briefing_cannot_create_facts_note,
    is_promotable_to_canonical_external,
    ledger_fact_ids,
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
    normalize_role_family_id,
    taxonomy_role_family_ids,
    validate_fact_shape,
    validate_role_family_references_for_fact,
)

REPO = Path(__file__).resolve().parents[2]
LEDGER_PATH = REPO / "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json"
TAXONOMY_PATH = REPO / "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml"


def test_ledger_payload_loads_every_fact_row_shapes() -> None:
    ledger = load_master_candidate_fact_ledger(path=LEDGER_PATH)
    assert ledger.get("status") == "candidate_ledger_requires_human_confirmation"
    ids = ledger_fact_ids(ledger)
    assert len(ids) == len(ledger["candidate_facts"])  # uniqueness by id enforced below
    assert len(ids) == len(set(ids))


def test_top_level_role_families_match_taxonomy_ids() -> None:
    taxonomy = load_master_role_family_taxonomy(path=TAXONOMY_PATH)
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    top_rf = ledger.get("role_families") or []
    taxonomy_ids = taxonomy_role_family_ids(taxonomy)
    assert set(top_rf) == set(taxonomy_ids)
    assert len(taxonomy_ids) == 13


def test_field_solutions_alias_normalizes_into_canonical_ai_solutions_architecture() -> None:
    taxonomy = load_master_role_family_taxonomy(path=TAXONOMY_PATH)
    nid = normalize_role_family_id("FIELD_SOLUTIONS_ARCHITECTURE", taxonomy=taxonomy)
    assert nid == "AI_SOLUTIONS_ARCHITECTURE"


def test_confidence_controls_canonical_promotion_hypothesis_without_weakening_x_defaults() -> None:
    """MEDIUM/LOW/NEEDS_VERIFICATION are never silently canonical; HIGH may pass normal lane."""
    assert is_promotable_to_canonical_external("HIGH")
    for band in ("MEDIUM", "LOW", "NEEDS_VERIFICATION"):
        assert not is_promotable_to_canonical_external(band)


def test_fact_usage_band_reflects_human_gate_discipline() -> None:
    assert fact_usage_band("HIGH") is FactUsageBand.ALLOW_AFTER_NORMAL_VALIDATION
    assert fact_usage_band("MEDIUM") is FactUsageBand.REQUIRE_HUMAN_REVIEW_FOR_CANONICAL_USE
    assert fact_usage_band("LOW") is FactUsageBand.BLOCK_FINAL_EXTERNAL
    assert fact_usage_band("NEEDS_VERIFICATION") is FactUsageBand.BLOCK_FINAL_EXTERNAL


def test_capability_tag_universe_is_non_empty() -> None:
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    tags = candidate_fact_tag_universe(ledger)
    assert len(tags) >= 100


def test_jd_policy_surface_docstring_explicitly_forbids_minted_facts() -> None:
    note = jd_briefing_cannot_create_facts_note().lower()
    assert "never" in note
    assert "ledger" in note


def test_fact_selection_bounded_to_ledger_rejects_unknown_ids() -> None:
    """JD/briefing cannot mint new fact ids — defensive guard for forthcoming wiring."""
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="not backed"):
        assert_selection_bounded_to_ledger(
            ["fact_engineering_platform_001", "jd_invented_fact_404"],
            ledger,
        )


def test_all_facts_normalize_role_family_references_via_taxonomy() -> None:
    taxonomy = yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    for row in ledger["candidate_facts"]:
        validate_fact_shape(row)
        validate_role_family_references_for_fact(row["role_families_supported"], taxonomy)


def test_capabilities_block_has_consistent_capability_ids_when_present() -> None:
    """Cross-check ancillary capability aggregates for basic presence + schema."""
    payload = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    caps = payload.get("capabilities")
    assert isinstance(caps, list)
    assert len({c["capability_id"] for c in caps if isinstance(c, dict)}) == len(caps)
