"""Determinism Closure Invariant Tests.

Covers all 6 closure components:
  1. DeterminismDigestEmitter   — emit-once, stable 64-hex artifact
  2. NegativeControlHarness     — tamper changes digest; restore restores it
  3. SemanticClockHashValidator  — artifact_hash matches re-computed hash
  4. ProviderBindingFingerprint  — identical bindings -> identical fingerprint
  5. EmbeddingNonInterferenceGuard — C0 context cannot leak into routing inputs
  6. OscillationFirewall         — tier oscillation is blocked

Plus: two-run identical digest proof (the ultimate closure test).
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    L0_ROUTING_DIR,
    L6_OBSERVABILITY_DIR,
)

pytestmark = pytest.mark.unit_min_deps


# ===========================================================================
# 1. DeterminismDigestEmitter
# ===========================================================================


class TestDeterminismDigestEmitter:
    def _zero(self, char: str = "0") -> str:
        return char * 64

    def _emitter(self):
        from agentic_core.L6_observability.engines.determinism_digest_emitter import (
            DeterminismDigestEmitter,
        )

        return DeterminismDigestEmitter()

    @pytest.mark.unit_min_deps
    def test_compute_returns_64_hex(self):
        e = self._emitter()
        digest = e.compute(
            policy_hash=self._zero("a"),
            registry_hash=self._zero("b"),
            config_surface_hash=self._zero("c"),
            transcript_hash=self._zero("d"),
            dependency_lock_hash=self._zero("e"),
        )
        assert isinstance(digest, str)
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)

    @pytest.mark.unit_min_deps
    def test_compute_is_deterministic(self):
        e = self._emitter()
        kwargs = {
            "policy_hash": self._zero("a"),
            "registry_hash": self._zero("b"),
            "config_surface_hash": self._zero("c"),
            "transcript_hash": self._zero("d"),
            "dependency_lock_hash": self._zero("e"),
        }
        assert e.compute(**kwargs) == e.compute(**kwargs)

    @pytest.mark.unit_min_deps
    def test_compute_different_inputs_different_digest(self):
        e = self._emitter()
        d1 = e.compute(
            policy_hash=self._zero("a"),
            registry_hash=self._zero("b"),
            config_surface_hash=self._zero("c"),
            transcript_hash=self._zero("d"),
            dependency_lock_hash=self._zero("e"),
        )
        d2 = e.compute(
            policy_hash=self._zero("f"),
            registry_hash=self._zero("b"),
            config_surface_hash=self._zero("c"),
            transcript_hash=self._zero("d"),
            dependency_lock_hash=self._zero("e"),
        )
        assert d1 != d2

    @pytest.mark.unit_min_deps
    def test_emit_once_returns_formatted_line(self):
        e = self._emitter()
        digest = self._zero("a")
        line = e.emit_once(digest)
        assert line == f"DETERMINISM-DIGEST: {digest}"

    @pytest.mark.unit_min_deps
    def test_emit_once_raises_on_second_call(self):
        from agentic_core.L6_observability.engines.determinism_digest_emitter import (
            DuplicateEmissionError,
        )

        e = self._emitter()
        e.emit_once(self._zero("a"))
        with pytest.raises(DuplicateEmissionError):
            e.emit_once(self._zero("a"))

    @pytest.mark.unit_min_deps
    def test_emit_once_rejects_non_hex(self):
        e = self._emitter()
        with pytest.raises(ValueError):
            e.emit_once("not-a-hash")

    @pytest.mark.unit_min_deps
    def test_reset_for_testing_clears_emit_guard(self):
        e = self._emitter()
        e.emit_once(self._zero("a"))
        e.reset_for_testing()
        line = e.emit_once(self._zero("b"))
        assert line.startswith("DETERMINISM-DIGEST: ")

    @pytest.mark.unit_min_deps
    def test_stable_config_surface_is_deterministic(self):
        from agentic_core.L6_observability.engines.determinism_digest_emitter import (
            build_stable_config_surface,
            hash_config_surface,
        )

        s1 = build_stable_config_surface()
        s2 = build_stable_config_surface()
        assert s1 == s2
        assert hash_config_surface(s1) == hash_config_surface(s2)

    @pytest.mark.unit_min_deps
    def test_stable_config_surface_no_wallclock_keys(self):
        from agentic_core.L6_observability.engines.determinism_digest_emitter import (
            build_stable_config_surface,
        )

        surface = build_stable_config_surface()
        for key in surface:
            assert "time" not in key.lower(), f"wall-clock key found: {key}"
            assert "clock" not in key.lower(), f"wall-clock key found: {key}"
            assert "random" not in key.lower(), f"random key found: {key}"


# ===========================================================================
# 2. NegativeControlHarness
# ===========================================================================


class TestNegativeControlHarness:
    @pytest.mark.unit_min_deps
    def test_tamper_active_only_when_env_is_1(self):
        from agentic_core.L2_execution.determinism.negative_control_harness import (
            is_tamper_active,
        )

        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            assert is_tamper_active() is True
        with patch.dict(os.environ, {}, clear=True):
            assert is_tamper_active() is False
        for val in ("true", "True", "yes", "0"):
            with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": val}):
                assert is_tamper_active() is False, f"should not tamper for {val!r}"

    @pytest.mark.unit_min_deps
    def test_tampered_surface_differs_from_clean(self):
        from agentic_core.L2_execution.determinism.negative_control_harness import (
            get_config_surface,
            hash_config_surface,
        )

        with patch.dict(os.environ, {}, clear=True):
            clean = hash_config_surface(get_config_surface())
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            tampered = hash_config_surface(get_config_surface())
        assert clean != tampered

    @pytest.mark.unit_min_deps
    def test_restore_returns_clean_digest(self):
        from agentic_core.L2_execution.determinism.negative_control_harness import (
            get_config_surface,
            hash_config_surface,
        )

        with patch.dict(os.environ, {}, clear=True):
            clean1 = hash_config_surface(get_config_surface())
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            _ = hash_config_surface(get_config_surface())
        with patch.dict(os.environ, {}, clear=True):
            restored = hash_config_surface(get_config_surface())
        assert clean1 == restored

    @pytest.mark.unit_min_deps
    def test_assert_digest_differs_raises_on_equal(self):
        from agentic_core.L2_execution.determinism.negative_control_harness import (
            assert_digest_differs,
        )

        same = "a" * 64
        with pytest.raises(AssertionError, match="identical"):
            assert_digest_differs(same, same)

    @pytest.mark.unit_min_deps
    def test_assert_digest_differs_passes_on_unequal(self):
        from agentic_core.L2_execution.determinism.negative_control_harness import (
            assert_digest_differs,
        )

        assert_digest_differs("a" * 64, "b" * 64)
        assert True  # no-exception contract

    @pytest.mark.unit_min_deps
    def test_assert_digest_stable_passes_on_equal(self):
        from agentic_core.L2_execution.determinism.negative_control_harness import (
            assert_digest_stable,
        )

        same = "c" * 64
        assert_digest_stable(same, same)
        assert True  # no-exception contract

    @pytest.mark.unit_min_deps
    def test_assert_digest_stable_raises_on_unequal(self):
        from agentic_core.L2_execution.determinism.negative_control_harness import (
            assert_digest_stable,
        )

        with pytest.raises(AssertionError, match="non-determinism"):
            assert_digest_stable("a" * 64, "b" * 64)

    @pytest.mark.unit_min_deps
    def test_tampered_surface_has_marker(self):
        from agentic_core.L2_execution.determinism.negative_control_harness import (
            get_config_surface,
        )

        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            surface = get_config_surface()
        assert surface.get("tampered") is True
        assert surface["top_k"] == 999
        assert surface["cutoff"] == 0.999


# ===========================================================================
# 3. SemanticClockHashValidator
# ===========================================================================


class TestSemanticClockHashValidator:
    def _make_artifact(self, **kwargs):
        from agentic_core.L0_routing.types.determinism_types import (
            SemanticClockAdvancementArtifact,
        )

        defaults = {
            "advancement_id": "adv_001",
            "previous_tick": 5,
            "new_tick": 6,
            "advancement_reason": "phase_transition",
            "l4_version_binding": "l4_v1.0.0",
            "provider_id": "provider_deterministic",
            "timestamp": 1234567890.0,
        }
        defaults.update(kwargs)
        return SemanticClockAdvancementArtifact(**defaults)

    @pytest.mark.unit_min_deps
    def test_valid_artifact_passes_validation(self):
        from agentic_core.L6_observability.engines.semantic_clock_validator import (
            validate_artifact,
        )

        artifact = self._make_artifact()
        result = validate_artifact(artifact)
        assert result.valid is True

    @pytest.mark.unit_min_deps
    def test_two_identical_artifacts_have_same_hash(self):
        a1 = self._make_artifact()
        a2 = self._make_artifact()
        assert a1.artifact_hash == a2.artifact_hash

    @pytest.mark.unit_min_deps
    def test_different_tick_produces_different_hash(self):
        a1 = self._make_artifact(new_tick=6)
        a2 = self._make_artifact(new_tick=99)
        assert a1.artifact_hash != a2.artifact_hash

    @pytest.mark.unit_min_deps
    def test_artifact_hash_is_64_hex(self):
        a = self._make_artifact()
        assert isinstance(a.artifact_hash, str)
        assert len(a.artifact_hash) == 64
        assert all(c in "0123456789abcdef" for c in a.artifact_hash)

    @pytest.mark.unit_min_deps
    def test_scan_module_finds_no_wallclock_in_clock_types(self):
        from pathlib import Path

        from agentic_core.L6_observability.engines.semantic_clock_validator import (
            scan_module_for_wallclock,
        )

        clock_module = Path(__file__).resolve().parents[2] / L0_ROUTING_DIR / "types" / "determinism_types.py"
        violations = scan_module_for_wallclock(clock_module)
        assert violations == [], "Wall-clock calls found in determinism_types.py:\n" + "\n".join(violations)

    @pytest.mark.unit_min_deps
    def test_validator_module_itself_has_no_wallclock(self):
        from pathlib import Path

        from agentic_core.L6_observability.engines.semantic_clock_validator import (
            scan_module_for_wallclock,
        )

        validator_module = (
            Path(__file__).resolve().parents[2]
            / L6_OBSERVABILITY_DIR
            / "engines"
            / "semantic_clock_validator.py"
        )
        violations = scan_module_for_wallclock(validator_module)
        assert violations == [], "Wall-clock calls found in semantic_clock_validator.py:\n" + "\n".join(
            violations
        )


# ===========================================================================
# 4. ProviderBindingFingerprint
# ===========================================================================


class TestProviderBindingFingerprint:
    @pytest.mark.unit_min_deps
    def test_fingerprint_is_64_hex(self):
        from agentic_core.L6_observability.engines.provider_binding_fingerprint import (
            capture_provider_bindings,
        )

        fp = capture_provider_bindings()
        assert isinstance(fp.fingerprint, str)
        assert len(fp.fingerprint) == 64
        assert all(c in "0123456789abcdef" for c in fp.fingerprint)

    @pytest.mark.unit_min_deps
    def test_two_clean_captures_identical(self):
        from agentic_core.L6_observability.engines.provider_binding_fingerprint import (
            capture_provider_bindings,
            fingerprint_matches,
        )

        fp1 = capture_provider_bindings()
        fp2 = capture_provider_bindings()
        assert fingerprint_matches(fp1, fp2)

    @pytest.mark.unit_min_deps
    def test_override_changes_fingerprint(self):
        from agentic_core.L6_observability.engines.provider_binding_fingerprint import (
            capture_provider_bindings,
            fingerprint_matches,
        )

        fp_clean = capture_provider_bindings()
        fp_overridden = capture_provider_bindings(overrides={"qwen": "Qwen2.5-72B-different"})
        assert not fingerprint_matches(fp_clean, fp_overridden)

    @pytest.mark.unit_min_deps
    def test_bindings_are_sorted(self):
        from agentic_core.L6_observability.engines.provider_binding_fingerprint import (
            capture_provider_bindings,
        )

        fp = capture_provider_bindings()
        pids = [b.provider_id for b in fp.bindings]
        assert pids == sorted(pids), "bindings must be in sorted provider_id order"

    @pytest.mark.unit_min_deps
    def test_deterministic_provider_is_present(self):
        from agentic_core.L6_observability.engines.provider_binding_fingerprint import (
            capture_provider_bindings,
        )

        fp = capture_provider_bindings()
        pids = {b.provider_id for b in fp.bindings}
        assert "deterministic" in pids, "deterministic provider must be registered"


# ===========================================================================
# 5. EmbeddingNonInterferenceGuard
# ===========================================================================


class TestEmbeddingNonInterferenceGuard:
    @pytest.mark.unit_min_deps
    def test_clean_routing_inputs_pass(self):
        from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (
            assert_no_c0_influence,
        )

        clean = {"tier": "DETERMINISTIC", "agent_id": "ssot_audit", "confidence": 0.9}
        assert_no_c0_influence(clean)
        assert True  # no-exception contract

    @pytest.mark.unit_min_deps
    def test_c0_marker_key_raises(self):
        from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (
            C0InterferenceViolation,
            assert_no_c0_influence,
        )

        dirty = {"tier": "DETERMINISTIC", "rag_context": "some retrieved text"}
        with pytest.raises(C0InterferenceViolation):
            assert_no_c0_influence(dirty)

    @pytest.mark.unit_min_deps
    def test_c0_value_fragment_raises(self):
        from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (
            C0InterferenceViolation,
            assert_no_c0_influence,
        )

        dirty = {"tier": "QWEN", "extra": "c0_context was appended here"}
        with pytest.raises(C0InterferenceViolation):
            assert_no_c0_influence(dirty)

    @pytest.mark.unit_min_deps
    def test_c0_key_collision_raises(self):
        from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (
            C0InterferenceViolation,
            assert_no_c0_influence,
        )

        routing = {"tier": "DETERMINISTIC", "agent_id": "x"}
        c0 = {"agent_id": "injected_from_rag", "docs": ["..."]}
        with pytest.raises(C0InterferenceViolation):
            assert_no_c0_influence(routing, c0_context=c0)

    @pytest.mark.unit_min_deps
    def test_verify_routing_decision_clean_returns_bool(self):
        from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (
            verify_routing_decision_clean,
        )

        clean = {"tier": "GEMINI", "confidence": 0.6}
        dirty = {"tier": "GEMINI", "c0_embedding": "data"}
        assert verify_routing_decision_clean(clean) is True
        assert verify_routing_decision_clean(dirty) is False

    @pytest.mark.unit_min_deps
    def test_assert_routing_decision_clean_raises_on_dirty(self):
        from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (
            C0InterferenceViolation,
            assert_routing_decision_clean,
        )

        dirty = {"tier": "QWEN", "embedding_context": "leaked"}
        with pytest.raises(C0InterferenceViolation):
            assert_routing_decision_clean(dirty)


# ===========================================================================
# 6. OscillationFirewall
# ===========================================================================


class TestOscillationFirewall:
    def _fw(self, cooldown=4, freeze=3):
        from agentic_core.L5_safety.enforcement.oscillation_firewall_gate import (
            OscillationFirewall,
            OscillationFirewallConfig,
        )

        cfg = OscillationFirewallConfig(cooldown_window=cooldown, freeze_cycles=freeze)
        fw = OscillationFirewall(cfg)
        return fw

    @pytest.mark.unit_min_deps
    def test_stable_sequence_does_not_trip(self):
        from agentic_core.L5_safety.enforcement.oscillation_firewall_gate import (
            OscillationFirewall,
            OscillationFirewallConfig,
        )

        cfg = OscillationFirewallConfig(cooldown_window=4, freeze_cycles=3)
        fw = OscillationFirewall(cfg)
        for cycle, tier in enumerate(["DETERMINISTIC", "DETERMINISTIC", "DETERMINISTIC", "QWEN"]):
            fw.assert_no_oscillation(tier, cycle)
            assert True  # no-exception contract

    @pytest.mark.unit_min_deps
    def test_oscillating_sequence_trips_firewall(self):
        from agentic_core.L5_safety.enforcement.oscillation_firewall_gate import (
            OscillationFirewall,
            OscillationFirewallConfig,
            OscillationFirewallTripped,
        )

        cfg = OscillationFirewallConfig(cooldown_window=4, freeze_cycles=5)
        fw = OscillationFirewall(cfg)
        fw.assert_no_oscillation("DETERMINISTIC", 0)
        fw.assert_no_oscillation("QWEN", 1)
        # 3rd call completes the A-B-A pattern -> oscillation fires here
        with pytest.raises(OscillationFirewallTripped):
            fw.assert_no_oscillation("DETERMINISTIC", 2)

    @pytest.mark.unit_min_deps
    def test_reset_clears_frozen_state(self):
        from agentic_core.L5_safety.enforcement.oscillation_firewall_gate import (
            OscillationFirewall,
            OscillationFirewallConfig,
            OscillationFirewallTripped,
        )

        cfg = OscillationFirewallConfig(cooldown_window=4, freeze_cycles=5)
        fw = OscillationFirewall(cfg)
        fw.assert_no_oscillation("DETERMINISTIC", 0)
        fw.assert_no_oscillation("QWEN", 1)
        with pytest.raises(OscillationFirewallTripped):
            fw.assert_no_oscillation("DETERMINISTIC", 2)
        fw.reset_for_testing()
        # after reset, should accept any tier without error
        fw.assert_no_oscillation("QWEN", 3)

    @pytest.mark.unit_min_deps
    def test_validate_threshold_stable_sequence(self):
        from agentic_core.L5_safety.enforcement.oscillation_firewall_gate import (
            validate_threshold,
        )

        stable = ("DETERMINISTIC",) * 6
        assert validate_threshold(stable) is True

    @pytest.mark.unit_min_deps
    def test_validate_threshold_oscillating_sequence(self):
        from agentic_core.L5_safety.enforcement.oscillation_firewall_gate import (
            OscillationFirewallConfig,
            validate_threshold,
        )

        cfg = OscillationFirewallConfig(cooldown_window=4, freeze_cycles=3)
        osc = ("DETERMINISTIC", "QWEN", "DETERMINISTIC", "QWEN", "DETERMINISTIC", "QWEN")
        assert validate_threshold(osc, cfg) is False

    @pytest.mark.unit_min_deps
    def test_config_rejects_small_cooldown(self):
        from agentic_core.L5_safety.enforcement.oscillation_firewall_gate import (
            OscillationFirewallConfig,
        )

        with pytest.raises(ValueError):
            OscillationFirewallConfig(cooldown_window=1, freeze_cycles=5)

    @pytest.mark.unit_min_deps
    def test_config_rejects_zero_freeze(self):
        from agentic_core.L5_safety.enforcement.oscillation_firewall_gate import (
            OscillationFirewallConfig,
        )

        with pytest.raises(ValueError):
            OscillationFirewallConfig(cooldown_window=4, freeze_cycles=0)


# ===========================================================================
# TWO-RUN IDENTICAL DIGEST PROOF
# ===========================================================================


class TestTwoRunIdenticalDigest:
    """Prove that two independent executions produce identical digest artifacts."""

    def _compute_full_digest(self) -> str:
        import hashlib

        from agentic_core.L2_execution.determinism.negative_control_harness import (
            get_config_surface,
            hash_config_surface,
        )
        from agentic_core.L6_observability.engines.determinism_digest_emitter import (
            DeterminismDigestEmitter,
        )
        from agentic_core.L6_observability.engines.provider_binding_fingerprint import (
            capture_provider_bindings,
        )

        # Config surface via negative_control_harness so tamper env changes digest
        config_hash = hash_config_surface(get_config_surface())

        # Provider binding surface
        fp = capture_provider_bindings()
        registry_hash = fp.fingerprint

        # Policy hash (structural constant — hash of canonical policy string)
        policy_hash = hashlib.sha256(b"sovereign-policy-v1.0").hexdigest()

        # Transcript hash (empty canonical transcript for clean-run)
        transcript_hash = hashlib.sha256(b"transcript:empty").hexdigest()

        # Dependency lock hash (canonical zero-hash for test isolation)
        dependency_lock_hash = hashlib.sha256(b"dependency-lock:stable").hexdigest()

        emitter = DeterminismDigestEmitter()
        return emitter.compute(
            policy_hash=policy_hash,
            registry_hash=registry_hash,
            config_surface_hash=config_hash,
            transcript_hash=transcript_hash,
            dependency_lock_hash=dependency_lock_hash,
        )

    @pytest.mark.unit_min_deps
    def test_two_independent_runs_identical_digest(self):
        """Two independent calls to the full digest pipeline must return identical
        64-hex strings.  This is the closure proof: the system is deterministic."""
        run1 = self._compute_full_digest()
        run2 = self._compute_full_digest()

        assert isinstance(run1, str) and len(run1) == 64
        assert isinstance(run2, str) and len(run2) == 64
        assert run1 == run2, f"Two-run digest mismatch:\n  run1={run1}\n  run2={run2}"

    @pytest.mark.unit_min_deps
    def test_digest_format_is_emission_ready(self):
        """Digest can be wrapped in emit_once and returns the canonical line."""
        from agentic_core.L6_observability.engines.determinism_digest_emitter import (
            DeterminismDigestEmitter,
        )

        digest = self._compute_full_digest()
        emitter = DeterminismDigestEmitter()
        line = emitter.emit_once(digest)
        assert line == f"DETERMINISM-DIGEST: {digest}"
        assert line.startswith("DETERMINISM-DIGEST: ")
        assert all(c in "0123456789abcdef" for c in line.split(": ", 1)[1])

    @pytest.mark.unit_min_deps
    def test_negative_control_breaks_identical_digest(self):
        """With W_HARDEN_NEGCTRL_TAMPER=1 the digest must differ from clean run."""
        clean_digest = self._compute_full_digest()

        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            tampered_digest = self._compute_full_digest()

        assert clean_digest != tampered_digest, (
            "Negative control FAILED: tamper env did not change the digest. "
            "The digest surface is not sensitive to config tampering."
        )

    @pytest.mark.unit_min_deps
    def test_clean_run_after_tamper_restores_identical_digest(self):
        """After tamper is removed, clean run must again equal original digest."""
        clean1 = self._compute_full_digest()

        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            _ = self._compute_full_digest()

        clean2 = self._compute_full_digest()
        assert clean1 == clean2, (
            f"Digest did not restore after tamper removal:\n  pre-tamper={clean1}\n  post-restore={clean2}"
        )
