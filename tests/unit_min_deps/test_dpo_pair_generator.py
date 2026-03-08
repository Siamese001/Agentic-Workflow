"""Unit tests for DPO Pair Generator - deterministic HITL feedback processing."""

import pytest

from agentic_core.L6_observability.engines.hitl_dpo_pair_generator import (
    DefaultDeterministicDPOPairGenerator,
)
from agentic_core.L6_observability.types.dpo_types import DPOExampleId

pytestmark = pytest.mark.unit_min_deps


class TestDPOPairGenerator:
    """Test suite for DPO Pair Generator deterministic behavior."""

    def test_hash_stable_same_inputs(self):
        """Same inputs must produce identical hashes and content_hash."""
        generator = DefaultDeterministicDPOPairGenerator()

        control_output = b"control_output_data"
        candidate_output = b"candidate_output_data"
        human_decision = "APPROVE"
        reason_codes = ("good_quality", "meets_requirements")

        # Generate pair twice
        pair1 = generator.generate(
            control_output_bytes=control_output,
            candidate_output_bytes=candidate_output,
            human_decision=human_decision,
            reason_codes=reason_codes,
        )

        pair2 = generator.generate(
            control_output_bytes=control_output,
            candidate_output_bytes=candidate_output,
            human_decision=human_decision,
            reason_codes=reason_codes,
        )

        # Must be identical
        assert pair1.content_hash() == pair2.content_hash()
        assert pair1.example_id.control_hash == pair2.example_id.control_hash
        assert pair1.example_id.candidate_hash == pair2.example_id.candidate_hash
        assert pair1.human_decision == pair2.human_decision
        assert pair1.reasons == pair2.reasons

    def test_different_inputs_different_hashes(self):
        """Different inputs must produce different hashes."""
        generator = DefaultDeterministicDPOPairGenerator()

        control_output1 = b"control_output_1"
        candidate_output1 = b"candidate_output_1"

        control_output2 = b"control_output_2"
        candidate_output2 = b"candidate_output_2"

        pair1 = generator.generate(
            control_output_bytes=control_output1,
            candidate_output_bytes=candidate_output1,
            human_decision="APPROVE",
            reason_codes=("test",),
        )

        pair2 = generator.generate(
            control_output_bytes=control_output2,
            candidate_output_bytes=candidate_output2,
            human_decision="APPROVE",
            reason_codes=("test",),
        )

        # Should have different hashes
        assert pair1.content_hash() != pair2.content_hash()
        assert pair1.example_id.control_hash != pair2.example_id.control_hash
        assert pair1.example_id.candidate_hash != pair2.example_id.candidate_hash

    def test_approve_vs_reject_different_pairs(self):
        """APPROVE and REJECT decisions should create different pairs."""
        generator = DefaultDeterministicDPOPairGenerator()

        control_output = b"same_control"
        candidate_output = b"same_candidate"

        approve_pair = generator.generate(
            control_output_bytes=control_output,
            candidate_output_bytes=candidate_output,
            human_decision="APPROVE",
            reason_codes=("good_quality",),
        )

        reject_pair = generator.generate(
            control_output_bytes=control_output,
            candidate_output_bytes=candidate_output,
            human_decision="REJECT",
            reason_codes=("poor_quality",),
        )

        # Same example_id but different decision
        assert approve_pair.example_id.control_hash == reject_pair.example_id.control_hash
        assert approve_pair.example_id.candidate_hash == reject_pair.example_id.candidate_hash
        assert approve_pair.human_decision != reject_pair.human_decision
        assert approve_pair.content_hash() != reject_pair.content_hash()

    def test_invalid_human_decision_raises_error(self):
        """Invalid human decision should raise ValueError."""
        generator = DefaultDeterministicDPOPairGenerator()

        with pytest.raises(ValueError, match="human_decision must be 'APPROVE' or 'REJECT'"):
            generator.generate(
                control_output_bytes=b"control",
                candidate_output_bytes=b"candidate",
                human_decision="INVALID",
                reason_codes=("test",),
            )

    def test_canonical_bytes_ascii_only(self):
        """canonical_bytes() must be ASCII-only."""
        generator = DefaultDeterministicDPOPairGenerator()

        pair = generator.generate(
            control_output_bytes=b"control",
            candidate_output_bytes=b"candidate",
            human_decision="APPROVE",
            reason_codes=("test_reason", "another_reason"),
        )

        canonical = pair.canonical_bytes()

        # Must be bytes
        assert isinstance(canonical, bytes)

        # Must be ASCII-only
        try:
            canonical.decode("ascii")
        except UnicodeDecodeError:
            pytest.fail("canonical_bytes() must be ASCII-only")

        # Must be stable across calls
        assert canonical == pair.canonical_bytes()

    def test_content_hash_stability(self):
        """content_hash() must be stable 64-character hex string."""
        generator = DefaultDeterministicDPOPairGenerator()

        pair = generator.generate(
            control_output_bytes=b"control",
            candidate_output_bytes=b"candidate",
            human_decision="REJECT",
            reason_codes=("performance_issue",),
        )

        content_hash = pair.content_hash()

        # Must be 64-character hex string
        assert isinstance(content_hash, str)
        assert len(content_hash) == 64
        assert all(c in "0123456789abcdef" for c in content_hash)

        # Must be stable across calls
        assert content_hash == pair.content_hash()

    def test_example_id_deterministic_construction(self):
        """DPOExampleId should be deterministic from hashes."""
        control_hash = "a1b2c3d4" * 8  # 32 chars * 8 = 256 chars, but we need 64
        control_hash = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
        candidate_hash = "fedcba09" * 8
        candidate_hash = "fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321"

        example_id = DPOExampleId(
            control_hash=control_hash,
            candidate_hash=candidate_hash,
        )

        # Should have correct hashes
        assert example_id.control_hash == control_hash
        assert example_id.candidate_hash == candidate_hash

        # Content hash should be deterministic
        content_hash = example_id.content_hash()
        assert len(content_hash) == 64
        assert content_hash == example_id.content_hash()

    def test_reason_codes_preserved(self):
        """Reason codes should be preserved exactly as provided."""
        generator = DefaultDeterministicDPOPairGenerator()

        reason_codes = ("performance", "accuracy", "user_satisfaction")

        pair = generator.generate(
            control_output_bytes=b"control",
            candidate_output_bytes=b"candidate",
            human_decision="APPROVE",
            reason_codes=reason_codes,
        )

        # Should preserve exact tuple
        assert pair.reasons == reason_codes
        assert isinstance(pair.reasons, tuple)
        assert len(pair.reasons) == 3
