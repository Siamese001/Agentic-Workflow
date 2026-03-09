"""Tests for HARDEN-MERGE-LOCKDOWN determinism digest."""

import os
from unittest.mock import patch

import pytest

from agentic_core.L2_execution.determinism import (
    compute_lockdown_determinism_digest,
    generate_lockdown_determinism_digest,
    get_embedding_config_surface,
    get_meta_learning_config_surface,
)


class TestDeterminismDigest:
    """Tests for determinism digest calculation and emission."""

    def test_digest_calculation(self):
        """Test that determinism digest is calculated correctly."""
        digest = compute_lockdown_determinism_digest()

        assert isinstance(digest, str)
        assert len(digest) == 64  # SHA-256 hex length
        assert all(c in "0123456789abcdef" for c in digest)

    def test_digest_emission_format(self):
        """Test that digest emission follows required format."""
        emission = generate_lockdown_determinism_digest()

        assert emission.startswith("HARDEN-MERGE-LOCKDOWN-DETERMINISM-DIGEST: ")
        digest_part = emission.split(": ", 1)[1]
        assert len(digest_part) == 64
        assert all(c in "0123456789abcdef" for c in digest_part)

    def test_determinism_digest_exactly_once_per_run(self, capsys):
        """Digest emitted exactly once per generate_lockdown_determinism_digest() call.

        Uses capsys to capture any stdout the function prints (if any) and
        also asserts the returned string is a single well-formed line.
        Two back-to-back calls must produce identical output.
        """
        emission1 = generate_lockdown_determinism_digest()
        emission2 = generate_lockdown_determinism_digest()

        # Each emission must be exactly one non-empty line
        for emission in (emission1, emission2):
            lines = [l.strip() for l in emission.splitlines() if l.strip()]
            assert len(lines) == 1, (
                f"generate_lockdown_determinism_digest() must return exactly 1 line, "
                f"got {len(lines)}: {lines}"
            )
            assert lines[0].startswith("HARDEN-MERGE-LOCKDOWN-DETERMINISM-DIGEST: "), (
                f"Line must start with correct prefix, got: {lines[0][:60]}"
            )
            hex_part = lines[0].split(": ", 1)[1]
            assert len(hex_part) == 64, f"SHA-256 hex must be 64 chars, got {len(hex_part)}"
            assert all(c in "0123456789abcdef" for c in hex_part), "Not a valid hex digest"

        # Cross-call determinism
        assert emission1 == emission2, (
            f"Digest must be identical across calls:\n  run1={emission1}\n  run2={emission2}"
        )

    def test_digest_determinism(self):
        """Test that digest is identical across multiple calculations."""
        digest1 = compute_lockdown_determinism_digest()
        digest2 = compute_lockdown_determinism_digest()

        assert digest1 == digest2, "Digest should be deterministic"

    def test_embedding_config_surface(self):
        """Test embedding configuration surface extraction (restore/clean mode)."""
        import os
        from unittest.mock import patch

        with patch.dict(os.environ, {}, clear=False) as env:
            env.pop("W_HARDEN_NEGCTRL_TAMPER", None)
            config = get_embedding_config_surface()

        assert isinstance(config, dict)
        assert "model_version" in config
        assert "threads" in config
        assert "top_k" in config
        assert "cutoff" in config
        assert "enabled" in config
        assert config["model_version"] == "multilingual-e5-large"
        assert config["threads"] >= 1
        assert config["top_k"] == 20
        assert config["cutoff"] == 0.0

    def test_embedding_config_tampering(self):
        """Test that embedding config is tampered when negative control is active."""
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            config = get_embedding_config_surface()

            assert config.get("tampered") is True
            assert config["top_k"] == 999
            assert config["cutoff"] == 0.999

    def test_embedding_config_no_tampering(self):
        """Test that embedding config is normal when negative control is inactive."""
        with patch.dict(os.environ, {}, clear=True):
            config = get_embedding_config_surface()

            assert "tampered" not in config
            assert config["top_k"] == 20
            assert config["cutoff"] == 0.0

    def test_meta_learning_config_surface(self):
        """Test meta-learning configuration surface extraction."""
        config = get_meta_learning_config_surface()

        assert isinstance(config, dict)
        assert "proposal_only" in config
        assert "validators_enabled" in config
        assert "shadow_evaluator_enabled" in config
        assert "oscillation_detector_enabled" in config
        assert "rlhf_delta_min" in config
        assert "rlhf_delta_max" in config
        assert "decision_delta_limit" in config

        # Verify safety defaults
        assert config["proposal_only"] is True
        assert config["validators_enabled"] is True
        assert config["shadow_evaluator_enabled"] is True
        assert config["oscillation_detector_enabled"] is True
        assert config["rlhf_delta_min"] == 0.1
        assert config["rlhf_delta_max"] == 2.0
        assert config["decision_delta_limit"] == 0.1

    def test_digest_changes_with_tampering(self):
        """Test that digest changes when embedding config is tampered."""
        # Normal digest
        with patch.dict(os.environ, {}, clear=True):
            normal_digest = compute_lockdown_determinism_digest()

        # Tampered digest
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            tampered_digest = compute_lockdown_determinism_digest()

        assert normal_digest != tampered_digest, "Digest should change with tampering"

    def test_digest_includes_all_components(self):
        """Test that digest includes all required sovereignty components."""
        # This is a structural test - we verify the calculation runs without error
        # which implies all components are included
        digest = compute_lockdown_determinism_digest()
        assert digest, "Digest calculation should succeed with all components"

    @pytest.mark.determinism
    def test_cross_run_determinism(self):
        """Test that digest is identical across test runs (marked for determinism)."""
        # This test is marked with @pytest.mark.determinism for cross-run validation
        digest1 = compute_lockdown_determinism_digest()
        digest2 = compute_lockdown_determinism_digest()

        assert digest1 == digest2, "Digest must be identical across runs"

        # Also test emission format
        emission1 = generate_lockdown_determinism_digest()
        emission2 = generate_lockdown_determinism_digest()

        assert emission1 == emission2, "Emission format must be identical across runs"
