"""Unit tests for claim_text vs proof_text I0 display policy (W2)."""

from __future__ import annotations

from apps_rg.fact_inventory.claim_proof_split_policy import (
    CLAIM_PROOF_SCHEMA_VERSION,
    apply_w2_offending_fact_migrations,
    claim_text_violates_i0_display_policy,
    normalize_claim_text_for_audit,
    validate_claim_proof_row,
)


def test_normalize_claim_text_collapses_whitespace_and_lowercases() -> None:
    assert normalize_claim_text_for_audit("  GraphRAG   Retrieval  ") == "graphrag retrieval"


def test_claim_text_empty_violates_display_policy() -> None:
    assert claim_text_violates_i0_display_policy("") == ["claim_text_empty"]
    assert claim_text_violates_i0_display_policy("   ") == ["claim_text_empty"]


def test_claim_text_banned_substring_detected_case_insensitive() -> None:
    violations = claim_text_violates_i0_display_policy(
        "Platform uses GraphRAG retrieval for enterprise search."
    )
    assert any(v.startswith("banned_substring:graphrag retrieval") for v in violations)


def test_claim_text_mechanism_inventory_chain_flags_three_or_more_hits() -> None:
    text = (
        "Stack includes deterministic routing, multi-agent orchestration, graphrag, "
        "sandboxed execution, and validation controls."
    )
    violations = claim_text_violates_i0_display_policy(text)
    assert any(v.startswith("mechanism_inventory_chain_hits:") for v in violations)


def test_claim_text_clean_passes_display_policy() -> None:
    assert (
        claim_text_violates_i0_display_policy(
            "Governed platform delivery with audit-ready execution for regulated workflows."
        )
        == []
    )


def test_validate_claim_proof_row_missing_claim() -> None:
    assert validate_claim_proof_row({"proof_text": "provenance only"}) == ["missing_claim_text"]


def test_validate_claim_proof_row_claim_equals_proof() -> None:
    row = {"claim_text": "Same body.", "proof_text": "Same body."}
    assert "claim_text_equals_proof_text" in validate_claim_proof_row(row)


def test_validate_claim_proof_row_proof_none_skips_split_checks() -> None:
    row = {"claim_text": "Display-safe claim without proof split yet."}
    assert validate_claim_proof_row(row) == []


def test_validate_claim_proof_row_empty_proof() -> None:
    row = {"claim_text": "Display claim.", "proof_text": "  "}
    assert validate_claim_proof_row(row) == ["empty_proof_text"]


def test_apply_w2_migration_engineering_platform_fact() -> None:
    original = (
        "Designed agentic AI with deterministic routing, multi-agent orchestration, "
        "graphrag retrieval, sandboxed execution."
    )
    row = {"candidate_fact_id": "fact_engineering_platform_001", "claim_text": original}
    migrated = apply_w2_offending_fact_migrations(row)
    assert migrated["proof_text"] == original
    assert migrated["claim_text"] != original
    assert "graphrag" not in migrated["claim_text"].lower()
    assert migrated["claim_proof_split_version"] == CLAIM_PROOF_SCHEMA_VERSION
    assert validate_claim_proof_row(migrated) == []


def test_apply_w2_migration_quant_hpc_fact() -> None:
    original = "Built quantitative foundation through derivatives pricing and multi-Greek hedging."
    row = {"candidate_fact_id": "fact_quant_hpc_003", "claim_text": original}
    migrated = apply_w2_offending_fact_migrations(row)
    assert migrated["proof_text"] == original
    assert "multi-greek hedging" not in migrated["claim_text"].lower()
    assert migrated["claim_text"] != original
    assert migrated["claim_proof_split_version"] == CLAIM_PROOF_SCHEMA_VERSION
    assert validate_claim_proof_row(migrated) == []


def test_apply_w2_migration_noop_for_unlisted_fact() -> None:
    row = {"candidate_fact_id": "fact_exec_002", "claim_text": "Unchanged claim."}
    assert apply_w2_offending_fact_migrations(row) == row
