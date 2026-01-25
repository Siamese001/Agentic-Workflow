"""
Phase 3: Cryptographic Gates Test Suite
Validates HMAC-SHA256 signatures and chain of custody for content validation.
"""

import pytest
import os
from apps_rg.validation.validation_gate import ValidationGate
from apps_rg.validation.word_count_enforcer import WordCountEnforcementEngine
from apps_rg.logic_nodes.two_phase_generation_node import (
    TwoPhaseGenerationNode,
    BulletGenerationOutput,
)
from apps_rg.logic_nodes.thematic_analysis_node import (
    ThematicAnalysisOutput,
    AuthenticityPatterns,
    CompetitiveIntelligence,
)


class TestPhase3CryptographicGates:
    def test_gate_signing_and_verification(self):
        """
        Verify that ValidationGate correctly signs and verifies payloads.
        """
        gate = ValidationGate("TEST_GATE")
        payload = {"status": "VALID", "count": 100}

        # 1. Sign
        signature = gate.sign_payload(payload)
        assert len(signature) == 64  # SHA256 hex digest length

        # 2. Verify Valid
        assert gate.verify(payload, signature)

        # 3. Verify Tamper Detection
        tampered_payload = {"status": "VALID", "count": 99}  # Changed count
        assert not gate.verify(tampered_payload, signature)

    def test_enforcer_returns_signed_result(self):
        """
        Verify WordCountEnforcer returns a signature in its output.
        """
        enforcer = WordCountEnforcementEngine()
        content = "Valid content length for overview."  # ~5 words, need more for 25 min
        content += " word" * 25  # Ensure valid length

        result = enforcer.enforce_with_regeneration(content, "resume_overview")

        assert "signature" in result
        assert "validation_payload" in result

        # Verify the signature matches the internal gate
        gate = ValidationGate("VG_WORD_COUNT")  # Re-instantiate same gate type
        assert gate.verify(result["validation_payload"], result["signature"])

    def test_two_phase_node_propagates_signature(self):
        """
        Verify the signature bubbles up to the Synthesis Output.
        """
        node = TwoPhaseGenerationNode()

        # Mock inputs
        bullet_out = BulletGenerationOutput([], {}, 1.0)
        thematic_out = ThematicAnalysisOutput(
            "Theme",
            [],
            AuthenticityPatterns([], [], [], []),
            CompetitiveIntelligence([], [], []),
            "Corp",
        )

        output = node.synthesize_overview_phase_b(bullet_out, thematic_out, "resume_overview")

        # The validation_result field now holds the signature
        signature = output.validation_result
        assert isinstance(signature, str)
        assert len(signature) == 64

    def test_signature_prevents_content_tampering(self):
        """
        Verify that tampering with content invalidates the signature.
        """
        gate = ValidationGate("SECURITY_TEST")
        original_payload = {"content_hash": "abc123", "word_count": 30, "status": "VALID"}

        # Sign original payload
        signature = gate.sign_payload(original_payload)

        # Verify original is valid
        assert gate.verify(original_payload, signature)

        # Tamper with payload
        tampered_payload = {"content_hash": "def456", "word_count": 30, "status": "VALID"}

        # Verify tampered is invalid
        assert not gate.verify(tampered_payload, signature)

    def test_deterministic_signing(self):
        """
        Verify that the same payload always produces the same signature.
        """
        gate = ValidationGate("DETERMINISM_TEST")
        payload = {"status": "VALID", "count": 42}

        # Sign multiple times
        sig1 = gate.sign_payload(payload)
        sig2 = gate.sign_payload(payload)
        sig3 = gate.sign_payload(payload)

        # All signatures should be identical
        assert sig1 == sig2 == sig3

    def test_content_hash_stability(self):
        """
        Verify that content hashing is stable across calls.
        """
        enforcer = WordCountEnforcementEngine()
        content = "Test content for hashing stability."

        result1 = enforcer.enforce_with_regeneration(content, "resume_overview")
        result2 = enforcer.enforce_with_regeneration(content, "resume_overview")

        # Content hashes should be identical
        hash1 = result1["validation_payload"]["content_hash"]
        hash2 = result2["validation_payload"]["content_hash"]

        assert hash1 == hash2

    def test_gate_id_isolation(self):
        """
        Verify that different gate IDs produce different signatures.
        """
        gate1 = ValidationGate("GATE_A")
        gate2 = ValidationGate("GATE_B")

        payload = {"status": "VALID", "count": 100}

        sig1 = gate1.sign_payload(payload)
        sig2 = gate2.sign_payload(payload)

        # Different gates should produce different signatures
        assert sig1 != sig2

        # Each gate should verify its own signature
        assert gate1.verify(payload, sig1)
        assert gate2.verify(payload, sig2)

        # Cross-verification should fail
        assert not gate1.verify(payload, sig2)
        assert not gate2.verify(payload, sig1)

    def test_environment_secret_injection(self):
        """
        Verify that environment variables affect signature generation.
        """
        # Test with default secret
        gate1 = ValidationGate("TEST")
        payload = {"test": "value"}
        sig1 = gate1.sign_payload(payload)

        # Test with custom secret
        os.environ["RG_VALIDATION_SECRET"] = "custom_secret_key"
        gate2 = ValidationGate("TEST")
        sig2 = gate2.sign_payload(payload)

        # Different secrets should produce different signatures
        assert sig1 != sig2

        # Clean up
        del os.environ["RG_VALIDATION_SECRET"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
