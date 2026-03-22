"""
Wave 4 Phase 11 — Cryptographic Integrity Tests

§4-compliant test suite covering:
- DigestCalculator: 5-component hash, validation guards, determinism, zero_hash
- DeterminismDigestEmitter: compute, emit_once, duplicate emission guard, reset
- build_stable_config_surface / hash_config_surface: determinism, key presence
- capture_provider_bindings: fingerprint, overrides, determinism
- ProviderBindingFingerprint: frozen, fingerprint validation, fingerprint_matches
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.determinism.digest_calculator import DigestCalculator
from agentic_core.L6_observability.engines.determinism_digest_emitter import (
    DeterminismDigestEmitter,
    DuplicateEmissionError,
    build_stable_config_surface,
    hash_config_surface,
)
from agentic_core.L6_observability.engines.provider_binding_fingerprint import (
    ProviderBinding,
    ProviderBindingFingerprint,
    capture_provider_bindings,
    fingerprint_matches,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_cryptographic_integrity", "p4obs", "metric_1")
_emit_emits_metric_event("test_cryptographic_integrity", "p4obs", "metric_2")
_emit_emits_metric_event("test_cryptographic_integrity", "p4obs", "metric_3")
_emit_emits_metric_event("test_cryptographic_integrity", "p4obs", "metric_4")
_emit_emits_metric_event("test_cryptographic_integrity", "p4obs", "metric_5")
_emit_emits_metric_event("test_cryptographic_integrity", "p4obs", "metric_6")
_emit_records_incident_event("test_cryptographic_integrity", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_cryptographic_integrity", "p4obs", "anomaly")
_emit_writes_observability_log("test_cryptographic_integrity", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_cryptographic_integrity", "p4obs", "mon_state")
_emit_triggers_alert("test_cryptographic_integrity", "p4obs", "alert")
_emit_links_incident_trace("test_cryptographic_integrity", "p4obs", "trace_link")
_emit_captures_pattern("test_cryptographic_integrity", "p3lm", "pattern")
_emit_records_learning_event("test_cryptographic_integrity", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_cryptographic_integrity", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_cryptographic_integrity", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_cryptographic_integrity", "p3lm", "routing")
_emit_improves_agent_policy("test_cryptographic_integrity", "p3lm", "policy")
_emit_stores_learning_state("test_cryptographic_integrity", "p3lm", "state")
_emit_records_execution_trace("test_cryptographic_integrity", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_cryptographic_integrity", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_cryptographic_integrity", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_cryptographic_integrity", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_cryptographic_integrity", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_cryptographic_integrity", "env_read", "p2_env_1")
_emit_reads_environ("test_cryptographic_integrity", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_cryptographic_integrity", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_cryptographic_integrity", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_cryptographic_integrity")
_emit_applies_guardrail("p0", "test_cryptographic_integrity", "p0_governance")
_emit_reads_policy_state("p0", "test_cryptographic_integrity", "policy_binding")
_emit_snapshots_state("p0", "test_cryptographic_integrity", "state_snapshot")
_emit_pulls_context("p1", "test_cryptographic_integrity", "context_pull")
_emit_pulls_context("p1", "test_cryptographic_integrity", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_cryptographic_integrity", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_cryptographic_integrity", "uwg_term_secondary")
_emit_writes_through("p1", "test_cryptographic_integrity", "write_through")
_emit_writes_through("p1", "test_cryptographic_integrity", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_cryptographic_integrity", "safety_validation")
_emit_invokes_eval("p1", "test_cryptographic_integrity", "eval_call")
_emit_proposal_commits_routing("p1", "test_cryptographic_integrity", "routing_commit")
_emit_escalates_to_human("p1", "test_cryptographic_integrity", "human_escalation")
_emit_routes_through("p1", "test_cryptographic_integrity", "route_through")
_emit_checks_agent_registry("p1", "test_cryptographic_integrity", "agent_registry")
_emit_validates_agent_capability("p1", "test_cryptographic_integrity", "capability")
_emit_dispatches_execution_plan("p1", "test_cryptographic_integrity", "exec_plan")
_emit_agent_executes_agent("p1", "test_cryptographic_integrity", "sub_agent")
_emit_routes_to_agent("p1", "test_cryptographic_integrity", "target_agent")
_emit_verifies_policy("p1", "test_cryptographic_integrity", "policy_check")
_emit_observes_runtime_state("p1", "test_cryptographic_integrity", "runtime_state")
_emit_verifies_boundary("p1", "test_cryptographic_integrity", "boundary_check")
_emit_transcripts_response("p1", "test_cryptographic_integrity", "transcript")
_emit_hard_fails_untranscripted("p1", "test_cryptographic_integrity")
_emit_gated_by_confidence("p1", "test_cryptographic_integrity", "confidence_gate")
emit_replay_key("p0", "test_cryptographic_integrity")
emit_determinism_digest("p0", "test_cryptographic_integrity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_cryptographic_integrity", "execution_auth")
_emit_validates_capability("p2", "test_cryptographic_integrity", "capability_check")
_emit_routes_to_capability("p2", "test_cryptographic_integrity", "capability_route")
_emit_writes_via_uwg("p2", "test_cryptographic_integrity", "uwg_write")
_emit_blocks_direct_write("p2", "test_cryptographic_integrity", "direct_write_block")
_emit_records_tool_invocation("p2", "test_cryptographic_integrity", "tool_invocation")
_emit_captures_execution_output("p2", "test_cryptographic_integrity", "exec_output")
_emit_dispatches_agent("p3", "test_cryptographic_integrity", "agent_dispatch")
_emit_coordinates_agents("p3", "test_cryptographic_integrity", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_cryptographic_integrity", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_cryptographic_integrity", "healing_outcome")
_emit_escalates_failure("p3", "test_cryptographic_integrity", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_cryptographic_integrity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_cryptographic_integrity", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_cryptographic_integrity", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_cryptographic_integrity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_cryptographic_integrity", "eval_metric")
_emit_stores_embedding("p4", "test_cryptographic_integrity", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_cryptographic_integrity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_cryptographic_integrity", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_HEX64 = "a" * 64


def _five_hashes(**overrides) -> dict:
    base = {
        "policy_hash": "a" * 64,
        "registry_hash": "b" * 64,
        "config_surface_hash": "c" * 64,
        "transcript_hash": "d" * 64,
        "dependency_lock_hash": "e" * 64,
    }
    return {**base, **overrides}


def _compute(**overrides) -> str:
    return DigestCalculator.compute(**_five_hashes(**overrides))


def _emitter_compute(emitter: DeterminismDigestEmitter | None = None, **overrides) -> str:
    e = emitter or DeterminismDigestEmitter()
    return e.compute(**_five_hashes(**overrides))


# ===========================================================================
# 1. DigestCalculator
# ===========================================================================


class TestDigestCalculator:
    @pytest.mark.governance
    def test_compute_returns_64_hex_chars(self):
        result = _compute()
        assert len(result) == 64
        int(result, 16)

    @pytest.mark.governance
    def test_compute_deterministic_for_same_inputs(self):
        assert _compute() == _compute()

    @pytest.mark.governance
    def test_compute_differs_when_policy_hash_changes(self):
        assert _compute(policy_hash="a" * 64) != _compute(policy_hash="1" * 64)

    @pytest.mark.governance
    def test_compute_differs_when_registry_hash_changes(self):
        assert _compute(registry_hash="b" * 64) != _compute(registry_hash="2" * 64)

    @pytest.mark.governance
    def test_compute_differs_when_config_surface_hash_changes(self):
        assert _compute(config_surface_hash="c" * 64) != _compute(config_surface_hash="3" * 64)

    @pytest.mark.governance
    def test_compute_differs_when_transcript_hash_changes(self):
        assert _compute(transcript_hash="d" * 64) != _compute(transcript_hash="4" * 64)

    @pytest.mark.governance
    def test_compute_differs_when_dependency_lock_hash_changes(self):
        assert _compute(dependency_lock_hash="e" * 64) != _compute(dependency_lock_hash="5" * 64)

    @pytest.mark.governance
    @pytest.mark.parametrize(
        "field",
        [
            "policy_hash",
            "registry_hash",
            "config_surface_hash",
            "transcript_hash",
            "dependency_lock_hash",
        ],
    )
    def test_raises_when_component_is_not_64_chars(self, field):
        with pytest.raises(ValueError, match=field):
            DigestCalculator.compute(**_five_hashes(**{field: "short"}))

    @pytest.mark.governance
    @pytest.mark.parametrize(
        "field",
        [
            "policy_hash",
            "registry_hash",
            "config_surface_hash",
            "transcript_hash",
            "dependency_lock_hash",
        ],
    )
    def test_raises_when_component_is_too_long(self, field):
        with pytest.raises(ValueError, match=field):
            DigestCalculator.compute(**_five_hashes(**{field: "a" * 65}))

    @pytest.mark.governance
    @pytest.mark.parametrize(
        "field",
        [
            "policy_hash",
            "registry_hash",
            "config_surface_hash",
            "transcript_hash",
            "dependency_lock_hash",
        ],
    )
    def test_raises_when_component_is_none(self, field):
        with pytest.raises((ValueError, TypeError)):
            DigestCalculator.compute(**_five_hashes(**{field: None}))

    @pytest.mark.governance
    def test_zero_hash_returns_64_zeros(self):
        z = DigestCalculator.zero_hash()
        assert z == "0" * 64

    @pytest.mark.governance
    def test_zero_hash_is_valid_input_to_compute(self):
        z = DigestCalculator.zero_hash()
        result = DigestCalculator.compute(
            policy_hash=z,
            registry_hash=z,
            config_surface_hash=z,
            transcript_hash=z,
            dependency_lock_hash=z,
        )
        assert len(result) == 64

    @pytest.mark.governance
    def test_component_keys_tuple_contains_all_five(self):
        keys = set(DigestCalculator.COMPONENT_KEYS)
        assert keys == {
            "policy_hash",
            "registry_hash",
            "config_surface_hash",
            "transcript_hash",
            "dependency_lock_hash",
        }


# ===========================================================================
# 2. DeterminismDigestEmitter
# ===========================================================================


class TestDeterminismDigestEmitter:
    @pytest.mark.governance
    def test_compute_returns_64_hex_chars(self):
        e = DeterminismDigestEmitter()
        result = _emitter_compute(e)
        assert len(result) == 64

    @pytest.mark.governance
    def test_compute_deterministic_for_same_inputs(self):
        e = DeterminismDigestEmitter()
        r1 = _emitter_compute(e)
        r2 = _emitter_compute(e)
        assert r1 == r2

    @pytest.mark.governance
    def test_compute_matches_digest_calculator_output(self):
        dc_result = _compute()
        e = DeterminismDigestEmitter()
        em_result = _emitter_compute(e)
        assert dc_result == em_result

    @pytest.mark.governance
    @pytest.mark.parametrize(
        "field",
        [
            "policy_hash",
            "registry_hash",
            "config_surface_hash",
            "transcript_hash",
            "dependency_lock_hash",
        ],
    )
    def test_compute_raises_when_component_not_64_chars(self, field):
        e = DeterminismDigestEmitter()
        with pytest.raises(ValueError, match=field):
            e.compute(**_five_hashes(**{field: "short"}))

    @pytest.mark.governance
    def test_emit_once_returns_formatted_line(self):
        e = DeterminismDigestEmitter()
        digest = _emitter_compute(e)
        line = e.emit_once(digest)
        assert line == f"DETERMINISM-DIGEST: {digest}"

    @pytest.mark.governance
    def test_emit_once_raises_on_second_call(self):
        e = DeterminismDigestEmitter()
        digest = _emitter_compute(e)
        e.emit_once(digest)
        with pytest.raises(DuplicateEmissionError):
            e.emit_once(digest)

    @pytest.mark.governance
    def test_emit_once_raises_for_non_64_char_digest(self):
        e = DeterminismDigestEmitter()
        with pytest.raises(ValueError, match="64-char"):
            e.emit_once("short_digest")

    @pytest.mark.governance
    def test_emit_once_raises_for_none_digest(self):
        e = DeterminismDigestEmitter()
        with pytest.raises((ValueError, TypeError)):
            e.emit_once(None)  # type: ignore

    @pytest.mark.governance
    def test_reset_for_testing_allows_second_emit(self):
        e = DeterminismDigestEmitter()
        digest = _emitter_compute(e)
        e.emit_once(digest)
        e.reset_for_testing()
        # Must not raise after reset
        line = e.emit_once(digest)
        assert line.startswith("DETERMINISM-DIGEST:")

    @pytest.mark.governance
    def test_fresh_emitter_is_not_emitted(self):
        e = DeterminismDigestEmitter()
        assert e._emitted is False

    @pytest.mark.governance
    def test_after_emit_once_emitted_flag_is_true(self):
        e = DeterminismDigestEmitter()
        digest = _emitter_compute(e)
        e.emit_once(digest)
        assert e._emitted is True


# ===========================================================================
# 3. build_stable_config_surface / hash_config_surface
# ===========================================================================


class TestStableConfigSurface:
    @pytest.mark.governance
    def test_build_returns_non_empty_dict(self):
        surface = build_stable_config_surface()
        assert isinstance(surface, dict)
        assert len(surface) > 0

    @pytest.mark.governance
    def test_build_contains_model_version_key(self):
        surface = build_stable_config_surface()
        assert "model_version" in surface

    @pytest.mark.governance
    def test_build_contains_top_k_key(self):
        surface = build_stable_config_surface()
        assert "top_k" in surface

    @pytest.mark.governance
    def test_build_contains_embedding_enabled_key(self):
        surface = build_stable_config_surface()
        assert "embedding_enabled" in surface

    @pytest.mark.governance
    def test_build_is_deterministic_across_calls(self):
        s1 = build_stable_config_surface()
        s2 = build_stable_config_surface()
        assert s1 == s2

    @pytest.mark.governance
    def test_hash_config_surface_returns_64_hex_chars(self):
        surface = build_stable_config_surface()
        h = hash_config_surface(surface)
        assert len(h) == 64
        int(h, 16)

    @pytest.mark.governance
    def test_hash_config_surface_deterministic(self):
        surface = build_stable_config_surface()
        h1 = hash_config_surface(surface)
        h2 = hash_config_surface(surface)
        assert h1 == h2

    @pytest.mark.governance
    def test_hash_config_surface_differs_when_surface_changes(self):
        surface = build_stable_config_surface()
        modified = {**surface, "top_k": surface["top_k"] + 1}
        assert hash_config_surface(surface) != hash_config_surface(modified)


# ===========================================================================
# 4. capture_provider_bindings / fingerprint_matches
# ===========================================================================


class TestProviderBindingFingerprint:
    @pytest.mark.governance
    def test_capture_returns_provider_binding_fingerprint(self):
        fp = capture_provider_bindings()
        assert isinstance(fp, ProviderBindingFingerprint)

    @pytest.mark.governance
    def test_fingerprint_is_64_hex_chars(self):
        fp = capture_provider_bindings()
        assert len(fp.fingerprint) == 64
        int(fp.fingerprint, 16)

    @pytest.mark.governance
    def test_capture_deterministic_without_overrides(self):
        fp1 = capture_provider_bindings()
        fp2 = capture_provider_bindings()
        assert fp1.fingerprint == fp2.fingerprint

    @pytest.mark.governance
    def test_capture_with_same_overrides_is_deterministic(self):
        overrides = {"openai": "gpt-4-turbo"}
        fp1 = capture_provider_bindings(overrides=overrides)
        fp2 = capture_provider_bindings(overrides=overrides)
        assert fp1.fingerprint == fp2.fingerprint

    @pytest.mark.governance
    def test_capture_differs_with_different_overrides(self):
        fp1 = capture_provider_bindings(overrides={"openai": "gpt-4-turbo"})
        fp2 = capture_provider_bindings(overrides={"openai": "gpt-3.5-turbo"})
        assert fp1.fingerprint != fp2.fingerprint

    @pytest.mark.governance
    def test_capture_bindings_contains_canonical_providers(self):
        fp = capture_provider_bindings()
        provider_ids = {b.provider_id for b in fp.bindings}
        assert "anthropic" in provider_ids
        assert "openai" in provider_ids

    @pytest.mark.governance
    def test_capture_bindings_sorted_by_provider_id(self):
        fp = capture_provider_bindings()
        ids = [b.provider_id for b in fp.bindings]
        assert ids == sorted(ids)

    @pytest.mark.governance
    def test_override_replaces_canonical_provider(self):
        fp = capture_provider_bindings(overrides={"openai": "gpt-custom"})
        openai_binding = next(b for b in fp.bindings if b.provider_id == "openai")
        assert openai_binding.model_id == "gpt-custom"

    @pytest.mark.governance
    def test_fingerprint_matches_returns_true_for_identical(self):
        fp1 = capture_provider_bindings()
        fp2 = capture_provider_bindings()
        assert fingerprint_matches(fp1, fp2) is True

    @pytest.mark.governance
    def test_fingerprint_matches_returns_false_for_different(self):
        fp1 = capture_provider_bindings()
        fp2 = capture_provider_bindings(overrides={"openai": "custom"})
        assert fingerprint_matches(fp1, fp2) is False

    @pytest.mark.governance
    def test_provider_binding_fingerprint_is_frozen(self):
        fp = capture_provider_bindings()
        with pytest.raises((AttributeError, TypeError)):
            fp.fingerprint = "x" * 64  # type: ignore[misc]

    @pytest.mark.governance
    def test_provider_binding_fingerprint_rejects_short_fingerprint(self):
        with pytest.raises(ValueError, match="fingerprint"):
            ProviderBindingFingerprint(bindings=(), fingerprint="short")

    @pytest.mark.governance
    def test_provider_binding_is_frozen(self):
        b = ProviderBinding(provider_id="openai", model_id="gpt-4o", tier="LLM_API")
        with pytest.raises((AttributeError, TypeError)):
            b.model_id = "changed"  # type: ignore[misc]

    @pytest.mark.governance
    def test_capture_none_overrides_same_as_no_overrides(self):
        fp1 = capture_provider_bindings(overrides=None)
        fp2 = capture_provider_bindings()
        assert fp1.fingerprint == fp2.fingerprint
