"""Wave 4.2 — unit tests for claim_proof_split_policy.

Covers the I0-aligned claim_text vs proof_text policy: normalization, banned
substring + mechanism-inventory-chain detection, row validation invariants, and
the deterministic W2.2 offending-fact migrations.
"""

from __future__ import annotations

from apps_rg.fact_inventory.claim_proof_split_policy import (
    CLAIM_PROOF_SCHEMA_VERSION,
    apply_w2_offending_fact_migrations,
    claim_text_violates_i0_display_policy,
    normalize_claim_text_for_audit,
    validate_claim_proof_row,
)


class TestNormalize:
    def test_collapses_whitespace_and_lowercases(self) -> None:
        assert normalize_claim_text_for_audit("  Hello   WORLD\n") == "hello world"

    def test_none_and_empty(self) -> None:
        assert normalize_claim_text_for_audit(None) == ""
        assert normalize_claim_text_for_audit("") == ""


class TestI0DisplayPolicy:
    def test_empty_flagged(self) -> None:
        assert claim_text_violates_i0_display_policy("") == ["claim_text_empty"]

    def test_clean_claim_passes(self) -> None:
        assert claim_text_violates_i0_display_policy("Led a platform team.") == []

    def test_banned_substring_detected(self) -> None:
        out = claim_text_violates_i0_display_policy("Holds AWS Certified badge.")
        assert any(v.startswith("banned_substring:aws certified") for v in out)

    def test_fsa_credential_banned(self) -> None:
        out = claim_text_violates_i0_display_policy("Earned FSA credential in 2010.")
        assert any("fsa credential" in v for v in out)

    def test_mechanism_chain_three_hits_flagged(self) -> None:
        text = "deterministic routing, graphrag, and sandboxed execution everywhere"
        out = claim_text_violates_i0_display_policy(text)
        assert any(v.startswith("mechanism_inventory_chain_hits:") for v in out)

    def test_mechanism_chain_below_threshold_not_flagged(self) -> None:
        text = "deterministic routing improved throughput"
        out = claim_text_violates_i0_display_policy(text)
        assert not any("mechanism_inventory_chain_hits" in v for v in out)


class TestValidateClaimProofRow:
    def test_missing_claim_text(self) -> None:
        assert validate_claim_proof_row({"claim_text": "  "}) == ["missing_claim_text"]

    def test_proof_none_is_ok(self) -> None:
        assert validate_claim_proof_row({"claim_text": "Led a team.", "proof_text": None}) == []

    def test_empty_proof_flagged(self) -> None:
        out = validate_claim_proof_row({"claim_text": "Led a team.", "proof_text": "  "})
        assert out == ["empty_proof_text"]

    def test_claim_equals_proof_flagged(self) -> None:
        out = validate_claim_proof_row(
            {"claim_text": "Led a team.", "proof_text": "Led a team."}
        )
        assert "claim_text_equals_proof_text" in out

    def test_claim_banned_substring_surfaced(self) -> None:
        out = validate_claim_proof_row(
            {"claim_text": "AWS Certified architect.", "proof_text": "Different proof."}
        )
        assert any("banned_substring:aws certified" in v for v in out)

    def test_fully_clean_row(self) -> None:
        out = validate_claim_proof_row(
            {"claim_text": "Led a platform team.", "proof_text": "Delivered X by Y."}
        )
        assert out == []


class TestW2Migrations:
    def test_unknown_fact_passthrough(self) -> None:
        row = {"candidate_fact_id": "fact_other_001", "claim_text": "orig"}
        assert apply_w2_offending_fact_migrations(row) == row

    def test_platform_001_rewrites_claim_and_preserves_proof(self) -> None:
        row = {"candidate_fact_id": "fact_engineering_platform_001", "claim_text": "ORIGINAL"}
        out = apply_w2_offending_fact_migrations(row)
        assert out["proof_text"] == "ORIGINAL"  # original claim demoted to proof
        assert "governed agentic AI platform" in out["claim_text"]
        assert out["claim_proof_split_version"] == CLAIM_PROOF_SCHEMA_VERSION

    def test_platform_002_adds_forward_projection(self) -> None:
        row = {"candidate_fact_id": "fact_engineering_platform_002", "claim_text": "ORIG2"}
        out = apply_w2_offending_fact_migrations(row)
        assert "forward_projection_preferred_c0_display_text" in out
        assert out["proof_text"] == "ORIG2"
        assert out["claim_proof_split_version"] == CLAIM_PROOF_SCHEMA_VERSION

    def test_quant_hpc_003_adds_preferred_display_text(self) -> None:
        row = {"candidate_fact_id": "fact_quant_hpc_003", "claim_text": "ORIG3"}
        out = apply_w2_offending_fact_migrations(row)
        assert "preferred_c0_display_text" in out
        assert "FSA-chartered" in out["preferred_c0_display_text"]

    def test_fact_id_fallback_key(self) -> None:
        # falls back to "fact_id" when candidate_fact_id absent
        row = {"fact_id": "fact_engineering_platform_001", "claim_text": "ORIG"}
        out = apply_w2_offending_fact_migrations(row)
        assert "governed agentic AI platform" in out["claim_text"]

    def test_input_not_mutated_in_place(self) -> None:
        row = {"candidate_fact_id": "fact_engineering_platform_001", "claim_text": "ORIG"}
        apply_w2_offending_fact_migrations(row)
        assert row == {"candidate_fact_id": "fact_engineering_platform_001", "claim_text": "ORIG"}
