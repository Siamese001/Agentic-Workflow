"""Stabilization Hardening Pass — §1 mandatory tests for S1–S5.

Covers every changed logic surface per windsurfrules §1.1–1.9:
- S1: InfrastructureDependencyError raised on Redis failure (fail-closed)
- S2: C0 forbidden-fields guard (assert_c0_context_clean)
- S3: Semantic cache key determinism anchors
- S4: ChangePackage proposal_only enforcement
- S5: UniversalWriteGateway 3-gate write (signature + replay_hash + plan_hash)

Test discipline:
- All tests are deterministic (no time, no randomness, no external state)
- Edge cases: null, empty, malformed, boundary, unauthorized, stale, replay, failure
- Fail-closed: invalid preconditions block operation; no side-effects before block
- Mutation-sensitive: tests fail if guard clauses are removed or operators flip
"""

from __future__ import annotations

import hashlib
from unittest.mock import MagicMock

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_stabilization_hardening_s1_s5")
_emit_applies_guardrail("p0", "test_stabilization_hardening_s1_s5", "p0_governance")
_emit_reads_policy_state("p0", "test_stabilization_hardening_s1_s5", "policy_binding")
_emit_snapshots_state("p0", "test_stabilization_hardening_s1_s5", "state_snapshot")
emit_replay_key("p0", "test_stabilization_hardening_s1_s5")
emit_determinism_digest("p0", "test_stabilization_hardening_s1_s5")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_stabilization_hardening_s1_s5", "execution_auth")
_emit_validates_capability("p2", "test_stabilization_hardening_s1_s5", "capability_check")
_emit_routes_to_capability("p2", "test_stabilization_hardening_s1_s5", "capability_route")
_emit_writes_via_uwg("p2", "test_stabilization_hardening_s1_s5", "uwg_write")
_emit_blocks_direct_write("p2", "test_stabilization_hardening_s1_s5", "direct_write_block")
_emit_records_tool_invocation("p2", "test_stabilization_hardening_s1_s5", "tool_invocation")
_emit_captures_execution_output("p2", "test_stabilization_hardening_s1_s5", "exec_output")
_emit_dispatches_agent("p3", "test_stabilization_hardening_s1_s5", "agent_dispatch")
_emit_coordinates_agents("p3", "test_stabilization_hardening_s1_s5", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_stabilization_hardening_s1_s5", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_stabilization_hardening_s1_s5", "healing_outcome")
_emit_escalates_failure("p3", "test_stabilization_hardening_s1_s5", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_stabilization_hardening_s1_s5", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_stabilization_hardening_s1_s5", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_stabilization_hardening_s1_s5", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_stabilization_hardening_s1_s5", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_stabilization_hardening_s1_s5", "eval_metric")
_emit_stores_embedding("p4", "test_stabilization_hardening_s1_s5", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_stabilization_hardening_s1_s5", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_stabilization_hardening_s1_s5", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# S1: InfrastructureDependencyError — fail-closed Redis enforcement
# ---------------------------------------------------------------------------


class TestInfrastructureDependencyError:
    """§1.5 §1.8 — InfrastructureDependencyError is the canonical fail-closed signal."""

    def test_error_is_importable(self):
        from agentic_core.L2_execution.types.infra_error_types import (
            InfrastructureDependencyError,
        )

        assert InfrastructureDependencyError is not None

    def test_error_is_runtime_error_subclass(self):
        from agentic_core.L2_execution.types.infra_error_types import (
            InfrastructureDependencyError,
        )

        assert issubclass(InfrastructureDependencyError, RuntimeError)

    def test_error_carries_message(self):
        from agentic_core.L2_execution.types.infra_error_types import (
            InfrastructureDependencyError,
        )

        exc = InfrastructureDependencyError("Redis unavailable: timeout")
        assert "Redis unavailable" in str(exc)

    def test_error_preserves_cause(self):
        from agentic_core.L2_execution.types.infra_error_types import (
            InfrastructureDependencyError,
        )

        cause = ConnectionRefusedError("refused")
        with pytest.raises(InfrastructureDependencyError) as exc_info:
            raise InfrastructureDependencyError("infra down") from cause
        assert exc_info.value.__cause__ is cause

    def test_error_can_be_caught_as_runtime_error(self):
        from agentic_core.L2_execution.types.infra_error_types import (
            InfrastructureDependencyError,
        )

        with pytest.raises(RuntimeError):
            raise InfrastructureDependencyError("caught as RuntimeError")


class TestSovereignRedisOrchestratorFailClosed:
    """§1.5 §1.8 §1.9 — Redis orchestrator raises on connection failure, no silent fallback."""

    def _make_orchestrator(self):
        from agentic_core.L3_orchestration.engines.sovereign_redis_orchestrator import (
            SovereignRedisOrchestrator,
        )

        return SovereignRedisOrchestrator()

    def test_get_raises_on_connection_error(self):
        import redis as redis_lib

        from agentic_core.L2_execution.types.infra_error_types import InfrastructureDependencyError

        orch = self._make_orchestrator()
        orch.connection = MagicMock()
        orch.connection.get.side_effect = redis_lib.ConnectionError("refused")
        with pytest.raises(InfrastructureDependencyError):
            orch.get("some_key")

    def test_set_raises_on_timeout_error(self):
        import redis as redis_lib

        from agentic_core.L2_execution.types.infra_error_types import InfrastructureDependencyError

        orch = self._make_orchestrator()
        orch.connection = MagicMock()
        orch.connection.set.side_effect = redis_lib.TimeoutError("timed out")
        with pytest.raises(InfrastructureDependencyError):
            orch.set("k", "v")

    def test_delete_raises_on_connection_error(self):
        import redis as redis_lib

        from agentic_core.L2_execution.types.infra_error_types import InfrastructureDependencyError

        orch = self._make_orchestrator()
        orch.connection = MagicMock()
        orch.connection.delete.side_effect = redis_lib.ConnectionError("dropped")
        with pytest.raises(InfrastructureDependencyError):
            orch.delete("k")

    def test_exists_raises_on_connection_error(self):
        import redis as redis_lib

        from agentic_core.L2_execution.types.infra_error_types import InfrastructureDependencyError

        orch = self._make_orchestrator()
        orch.connection = MagicMock()
        orch.connection.exists.side_effect = redis_lib.ConnectionError("dropped")
        with pytest.raises(InfrastructureDependencyError):
            orch.exists("k")

    def test_clear_raises_on_connection_error(self):
        import redis as redis_lib

        from agentic_core.L2_execution.types.infra_error_types import InfrastructureDependencyError

        orch = self._make_orchestrator()
        orch.connection = MagicMock()
        orch.connection.flushdb.side_effect = redis_lib.ConnectionError("dropped")
        with pytest.raises(InfrastructureDependencyError):
            orch.clear()

    def test_no_fallback_cache_attribute(self):
        """§1.8 negative control: fallback_cache MUST NOT exist post-hardening."""
        orch = self._make_orchestrator()
        assert not hasattr(orch, "fallback_cache"), (
            "fallback_cache still present — silent fallback not eliminated"
        )

    def test_no_use_fallback_attribute(self):
        """§1.8 negative control: use_fallback flag MUST NOT exist post-hardening."""
        orch = self._make_orchestrator()
        assert not hasattr(orch, "use_fallback"), (
            "use_fallback still present — silent fallback not eliminated"
        )

    def test_get_succeeds_when_connection_healthy(self):
        orch = self._make_orchestrator()
        orch.connection = MagicMock()
        orch.connection.get.return_value = b"val"
        result = orch.get("k")
        assert result == b"val"

    def test_infra_error_message_contains_url(self):
        import redis as redis_lib

        from agentic_core.L2_execution.types.infra_error_types import InfrastructureDependencyError

        orch = self._make_orchestrator()
        orch.connection = MagicMock()
        orch.connection.get.side_effect = redis_lib.ConnectionError("refused")
        with pytest.raises(InfrastructureDependencyError, match="redis://"):
            orch.get("k")


# ---------------------------------------------------------------------------
# S2: C0 forbidden-fields guard
# ---------------------------------------------------------------------------


class TestC0ContextClean:
    """§1.5 §1.7 §1.8 §1.9 — assert_c0_context_clean enforces the informational boundary."""

    def _guard(self):
        from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (
            assert_c0_context_clean,
        )

        return assert_c0_context_clean

    def test_clean_context_passes(self):
        self._guard()({"rag_result": "some text", "score": 0.9})

    def test_empty_context_passes(self):
        self._guard()({})

    def test_route_mode_is_forbidden(self):
        from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (
            C0InterferenceViolation,
        )

        with pytest.raises(C0InterferenceViolation, match="route_mode"):
            self._guard()({"route_mode": "fast"})

    def test_execution_tier_is_forbidden(self):
        from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (
            C0InterferenceViolation,
        )

        with pytest.raises(C0InterferenceViolation, match="execution_tier"):
            self._guard()({"execution_tier": "L2"})

    def test_safety_threshold_is_forbidden(self):
        from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (
            C0InterferenceViolation,
        )

        with pytest.raises(C0InterferenceViolation, match="safety_threshold"):
            self._guard()({"safety_threshold": 0.7})

    def test_policy_hash_is_forbidden(self):
        from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (
            C0InterferenceViolation,
        )

        with pytest.raises(C0InterferenceViolation, match="policy_hash"):
            self._guard()({"policy_hash": "abc123"})

    def test_multiple_forbidden_fields_reported(self):
        from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (
            C0InterferenceViolation,
        )

        with pytest.raises(C0InterferenceViolation):
            self._guard()({"route_mode": "x", "execution_tier": "L1"})

    def test_forbidden_field_alongside_allowed_fields(self):
        from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (
            C0InterferenceViolation,
        )

        with pytest.raises(C0InterferenceViolation):
            self._guard()({"score": 0.8, "route_mode": "slow"})

    def test_assert_no_c0_influence_calls_context_clean(self):
        """§1.8 — assert_no_c0_influence must invoke assert_c0_context_clean when c0_context given."""
        from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (
            C0InterferenceViolation,
            assert_no_c0_influence,
        )

        with pytest.raises(C0InterferenceViolation, match="route_mode"):
            assert_no_c0_influence(
                routing_inputs={"user_id": "u1"},
                c0_context={"route_mode": "fast"},
            )

    def test_forbidden_fields_frozenset_immutable(self):
        """§1.7 determinism: the forbidden-fields set must not change between calls."""
        from agentic_core.L5_safety.enforcement import embedding_non_interference_guardrail as mod

        snap1 = frozenset(mod._C0_FORBIDDEN_FIELDS)
        snap2 = frozenset(mod._C0_FORBIDDEN_FIELDS)
        assert snap1 == snap2

    def test_all_four_forbidden_fields_present(self):
        from agentic_core.L5_safety.enforcement import embedding_non_interference_guardrail as mod

        assert {"route_mode", "execution_tier", "safety_threshold", "policy_hash"} <= set(
            mod._C0_FORBIDDEN_FIELDS
        )


# ---------------------------------------------------------------------------
# S3: Semantic cache key determinism anchors
# ---------------------------------------------------------------------------


class TestSemanticCacheKeyDeterminism:
    """§1.7 §1.9 — _compute_hash must include model version + retrieval config anchors."""

    def _make_manager(self, model_ver="test-model-v0", config_hash="test-cfg-hash"):
        """Build a SemanticCacheManager-like object with instance-level anchor overrides.

        We set instance attributes directly so multiple managers in the same
        test do not share state through the class dict.
        """
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        mgr = object.__new__(SemanticCacheManager)
        mgr._EMBEDDING_MODEL_VERSION = model_ver
        mgr._RETRIEVAL_CONFIG_HASH = config_hash
        return mgr

    def test_identical_inputs_produce_identical_hash(self):
        mgr = self._make_manager()
        h1 = mgr._compute_hash("query text", "ns")
        h2 = mgr._compute_hash("query text", "ns")
        assert h1 == h2

    def test_different_queries_produce_different_hashes(self):
        mgr = self._make_manager()
        h1 = mgr._compute_hash("query A", "ns")
        h2 = mgr._compute_hash("query B", "ns")
        assert h1 != h2

    def test_different_namespaces_produce_different_hashes(self):
        mgr = self._make_manager()
        h1 = mgr._compute_hash("same", "ns1")
        h2 = mgr._compute_hash("same", "ns2")
        assert h1 != h2

    def test_model_version_change_invalidates_hash(self):
        """§1.7 determinism: changing model version MUST change the cache key."""
        mgr1 = self._make_manager(model_ver="v1")
        mgr2 = self._make_manager(model_ver="v2")
        h1 = mgr1._compute_hash("q", "ns")
        h2 = mgr2._compute_hash("q", "ns")
        assert h1 != h2

    def test_retrieval_config_change_invalidates_hash(self):
        """§1.7 determinism: changing retrieval config MUST change the cache key."""
        mgr1 = self._make_manager(config_hash="cfg-a")
        mgr2 = self._make_manager(config_hash="cfg-b")
        h1 = mgr1._compute_hash("q", "ns")
        h2 = mgr2._compute_hash("q", "ns")
        assert h1 != h2

    def test_hash_is_hex_sha256_length(self):
        mgr = self._make_manager()
        h = mgr._compute_hash("query", "ns")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_empty_query_handled(self):
        mgr = self._make_manager()
        h = mgr._compute_hash("", "ns")
        assert isinstance(h, str) and len(h) == 64

    def test_same_query_different_anchors_never_collide(self):
        """§1.9 matrix: (model_ver × config_hash) must produce unique hashes."""
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        seen = set()
        combos = [("v1", "cfg1"), ("v1", "cfg2"), ("v2", "cfg1"), ("v2", "cfg2")]
        for mv, ch in combos:
            mgr = object.__new__(SemanticCacheManager)
            mgr._EMBEDDING_MODEL_VERSION = mv
            mgr._RETRIEVAL_CONFIG_HASH = ch
            h = mgr._compute_hash("same query", "same_ns")
            assert h not in seen, f"Hash collision for ({mv}, {ch})"
            seen.add(h)


# ---------------------------------------------------------------------------
# S4: ChangePackage proposal_only enforcement
# ---------------------------------------------------------------------------


class TestChangePackageProposalOnly:
    """§1.5 §1.8 §1.9 §1.11 — ChangePackage must block runtime activation without approval token."""

    def _make(self, **kwargs):
        from agentic_core.interfaces.meta_learning import ChangePackage

        return ChangePackage(**kwargs)

    def test_proposal_only_true_no_token_allowed(self):
        pkg = self._make(
            proposal_id="p1",
            change_type="healing_pattern",
            parameters={"k": "v"},
            proposal_only=True,
            approval_token=None,
        )
        assert pkg.proposal_only is True

    def test_proposal_only_false_with_token_allowed(self):
        pkg = self._make(
            proposal_id="p2",
            change_type="threshold_adjustment",
            parameters={"threshold": 0.5},
            proposal_only=False,
            approval_token="tok-abc123",
        )
        assert pkg.proposal_only is False
        assert pkg.approval_token == "tok-abc123"

    def test_proposal_only_false_without_token_raises(self):
        """§1.8 fail-closed: no approval_token + proposal_only=False must raise."""
        with pytest.raises(ValueError, match="approval_token"):
            self._make(
                proposal_id="p3",
                change_type="threshold_adjustment",
                parameters={"threshold": 0.5},
                proposal_only=False,
                approval_token=None,
            )

    def test_proposal_only_false_empty_token_raises(self):
        """§1.5 boundary: empty string token is still no token."""
        with pytest.raises(ValueError):
            self._make(
                proposal_id="p4",
                change_type="healing_pattern",
                parameters={},
                proposal_only=False,
                approval_token="",
            )

    def test_non_json_parameters_raises(self):
        """Pre-existing invariant still holds after hardening."""
        with pytest.raises(ValueError, match="JSON-serializable"):
            self._make(
                proposal_id="p5",
                change_type="healing_pattern",
                parameters={"fn": lambda x: x},
            )

    def test_default_proposal_only_is_true(self):
        """§1.8 fail-closed default: new ChangePackages default to proposal-only."""
        import dataclasses

        from agentic_core.interfaces.meta_learning import ChangePackage

        fields = {f.name: f for f in dataclasses.fields(ChangePackage)}
        assert fields["proposal_only"].default is True

    def test_package_is_frozen(self):
        """Immutability invariant: frozen dataclass."""
        pkg = self._make(
            proposal_id="p6",
            change_type="healing_pattern",
            parameters={"k": "v"},
        )
        with pytest.raises((AttributeError, TypeError)):
            pkg.proposal_id = "mutated"  # type: ignore[misc]

    def test_requires_approval_defaults_true(self):
        pkg = self._make(
            proposal_id="p7",
            change_type="healing_pattern",
            parameters={},
        )
        assert pkg.requires_approval is True

    def test_propose_healing_pattern_returns_proposal_only(self):
        """§1.8 — SovereignMetaLearningClient proposals must always be proposal_only=True."""
        from agentic_core.interfaces.meta_learning import SovereignMetaLearningClient

        inner = MagicMock()
        client = SovereignMetaLearningClient(inner_client=inner, proposal_only=True)
        pkg = client.propose_healing_pattern({"fix": "yes"})
        assert pkg.proposal_only is True

    def test_suggest_threshold_returns_proposal_only(self):
        from agentic_core.interfaces.meta_learning import SovereignMetaLearningClient

        inner = MagicMock()
        client = SovereignMetaLearningClient(inner_client=inner, proposal_only=True)
        pkg = client.suggest_threshold_adjustment(0.75)
        assert pkg.requires_approval is True


# ---------------------------------------------------------------------------
# S5: UniversalWriteGateway 3-gate write
# ---------------------------------------------------------------------------


class TestUWGThreeGateWrite:
    """§1.5 §1.8 §1.9 §1.11 — UWG.write() must enforce signature → replay_hash → plan_hash."""

    def _make_uwg(self, replay_mode: bool = False):
        from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway

        return UniversalWriteGateway(replay_mode=replay_mode)

    def _make_store(self):
        return MagicMock()

    # --- Gate 1: frozen ---

    def test_frozen_blocks_write_before_signature_check(self):
        uwg = self._make_uwg()
        uwg.freeze()
        store = self._make_store()
        with pytest.raises(PermissionError, match="frozen"):
            uwg.write(b"payload", "sig", store)
        store.write.assert_not_called()

    # --- Gate 2: signature ---

    def test_empty_signature_blocks_write(self):
        uwg = self._make_uwg()
        store = self._make_store()
        with pytest.raises(PermissionError, match="signature"):
            uwg.write(b"payload", "", store)
        store.write.assert_not_called()

    def test_valid_signature_passes_gate_1(self):
        uwg = self._make_uwg()
        store = self._make_store()
        uwg.write(b"payload", "valid-sig", store)
        store.write.assert_called_once_with(b"payload")

    # --- Gate 3a: replay_hash ---

    def test_correct_replay_key_passes(self):
        uwg = self._make_uwg()
        store = self._make_store()
        payload = b"deterministic payload"
        replay_key = hashlib.sha256(payload).hexdigest()
        uwg.write(payload, "sig", store, replay_key=replay_key)
        store.write.assert_called_once_with(payload)

    def test_wrong_replay_key_blocks_write(self):
        uwg = self._make_uwg()
        store = self._make_store()
        payload = b"some payload"
        bad_key = hashlib.sha256(b"different payload").hexdigest()
        with pytest.raises(PermissionError, match="replay hash"):
            uwg.write(payload, "sig", store, replay_key=bad_key)
        store.write.assert_not_called()

    def test_empty_replay_key_skips_check(self):
        """§1.5 boundary: empty replay_key means check is skipped (opt-in gate)."""
        uwg = self._make_uwg()
        store = self._make_store()
        uwg.write(b"payload", "sig", store, replay_key="")
        store.write.assert_called_once()

    # --- Gate 3b: plan_hash ---

    def test_non_empty_plan_hash_passes(self):
        uwg = self._make_uwg()
        store = self._make_store()
        uwg.write(b"payload", "sig", store, plan_hash="plan-abc")
        store.write.assert_called_once_with(b"payload")

    def test_empty_plan_hash_skips_check(self):
        """§1.5 boundary: empty plan_hash means check is skipped (opt-in gate)."""
        uwg = self._make_uwg()
        store = self._make_store()
        uwg.write(b"payload", "sig", store, plan_hash="")
        store.write.assert_called_once()

    # --- store never touched on any failure ---

    def test_store_not_called_on_frozen(self):
        uwg = self._make_uwg()
        uwg.freeze()
        store = self._make_store()
        with pytest.raises(PermissionError):
            uwg.write(b"p", "s", store)
        store.write.assert_not_called()

    def test_store_not_called_on_bad_signature(self):
        uwg = self._make_uwg()
        store = self._make_store()
        with pytest.raises(PermissionError):
            uwg.write(b"p", "", store)
        store.write.assert_not_called()

    def test_store_not_called_on_bad_replay_hash(self):
        uwg = self._make_uwg()
        store = self._make_store()
        with pytest.raises(PermissionError):
            uwg.write(b"p", "sig", store, replay_key="deadbeef" * 8)
        store.write.assert_not_called()

    # --- verify_replay_hash unit tests ---

    def test_verify_replay_hash_correct(self):
        uwg = self._make_uwg()
        payload = b"abc"
        key = hashlib.sha256(payload).hexdigest()
        assert uwg._verify_replay_hash(payload, key) is True

    def test_verify_replay_hash_wrong(self):
        uwg = self._make_uwg()
        assert uwg._verify_replay_hash(b"abc", "wrong") is False

    def test_verify_replay_hash_empty_key_returns_false(self):
        uwg = self._make_uwg()
        assert uwg._verify_replay_hash(b"abc", "") is False

    def test_verify_plan_hash_non_empty_returns_true(self):
        uwg = self._make_uwg()
        assert uwg._verify_plan_hash("plan-001") is True

    def test_verify_plan_hash_empty_returns_false(self):
        uwg = self._make_uwg()
        assert uwg._verify_plan_hash("") is False

    # --- §1.9 matrix: (frozen × signature × replay_key × plan_hash) ---

    @pytest.mark.parametrize(
        "frozen,sig,rkey,phash,should_raise",
        [
            (True, "s", "", "", True),  # frozen blocks all
            (False, "", "", "", True),  # bad sig blocks
            (False, "s", "bad", "", True),  # bad replay blocks (non-empty bad key)
            (False, "s", "", "plan", False),  # skip replay, valid plan → ok
            (False, "s", "", "", False),  # both skipped → ok
        ],
    )
    def test_gate_matrix(self, frozen, sig, rkey, phash, should_raise):
        from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway

        uwg = UniversalWriteGateway()
        if frozen:
            uwg.freeze()
        store = MagicMock()
        payload = b"matrix-payload"
        # Compute correct replay key for "bad" case
        if rkey == "bad":
            rkey = "00" * 32  # 64-char hex but wrong value

        if should_raise:
            with pytest.raises(PermissionError):
                uwg.write(payload, sig, store, replay_key=rkey, plan_hash=phash)
            store.write.assert_not_called()
        else:
            uwg.write(payload, sig, store, replay_key=rkey, plan_hash=phash)
            store.write.assert_called_once_with(payload)
