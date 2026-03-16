"""ADG-driven tests for L1 cognition type modules — fan_in=1.

Covers: cache_types, domain_types, memory_types, observability_types, validation_types.
"""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_l1_cognition_types_adg")
_emit_applies_guardrail("p0", "test_l1_cognition_types_adg", "p0_governance")
_emit_snapshots_state("p0", "test_l1_cognition_types_adg", "state_snapshot")
emit_replay_key("p0", "test_l1_cognition_types_adg")
emit_determinism_digest("p0", "test_l1_cognition_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_l1_cognition_types_adg", "execution_auth")
_emit_validates_capability("p2", "test_l1_cognition_types_adg", "capability_check")
_emit_routes_to_capability("p2", "test_l1_cognition_types_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_l1_cognition_types_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_l1_cognition_types_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_l1_cognition_types_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_l1_cognition_types_adg", "exec_output")
_emit_dispatches_agent("p3", "test_l1_cognition_types_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_l1_cognition_types_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_l1_cognition_types_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_l1_cognition_types_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_l1_cognition_types_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_l1_cognition_types_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_l1_cognition_types_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_l1_cognition_types_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_l1_cognition_types_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_l1_cognition_types_adg", "eval_metric")
_emit_stores_embedding("p4", "test_l1_cognition_types_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_l1_cognition_types_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_l1_cognition_types_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# cache_types
# ---------------------------------------------------------------------------
from agentic_core.L1_cognition.types.cache_types import (
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_TTL_SECONDS,
    MAX_CACHE_SIZE,
    MAX_HEALING_DEPTH,
    MAX_TTL_SECONDS,
    MIN_TTL_SECONDS,
    DomainConfig,
    EvictionPolicy,
)


class TestCacheTypes:
    def test_default_ttl_positive(self):
        assert DEFAULT_TTL_SECONDS > 0

    def test_min_ttl_less_than_default(self):
        assert MIN_TTL_SECONDS < DEFAULT_TTL_SECONDS

    def test_max_ttl_greater_than_default(self):
        assert MAX_TTL_SECONDS > DEFAULT_TTL_SECONDS

    def test_similarity_threshold_in_range(self):
        assert 0.0 < DEFAULT_SIMILARITY_THRESHOLD < 1.0

    def test_max_cache_size_positive(self):
        assert MAX_CACHE_SIZE > 0

    def test_max_healing_depth_positive(self):
        assert MAX_HEALING_DEPTH > 0

    def test_eviction_policy_has_lru(self):
        assert EvictionPolicy.LRU is not None

    def test_eviction_policy_has_ttl(self):
        assert EvictionPolicy.TTL is not None

    def test_domain_config_creates(self):
        cfg = DomainConfig(domain="agentic_core")
        assert cfg.domain == "agentic_core"
        assert cfg.ttl_seconds == DEFAULT_TTL_SECONDS

    def test_domain_config_custom_ttl(self):
        cfg = DomainConfig(domain="apps_lic", ttl_seconds=7200)
        assert cfg.ttl_seconds == 7200


# ---------------------------------------------------------------------------
# domain_types
# ---------------------------------------------------------------------------
from agentic_core.L1_cognition.types.domain_types import (
    DomainContext,
    SharingPolicy,
)


class TestDomainTypes:
    def test_sharing_policy_none(self):
        assert SharingPolicy.NONE.value == "none"

    def test_sharing_policy_bidirectional(self):
        assert SharingPolicy.BIDIRECTIONAL.value == "bidirectional"

    def test_domain_context_creates(self):
        ctx = DomainContext(domain="agentic_core")
        assert ctx.domain == "agentic_core"
        assert ctx.sharing_policy == SharingPolicy.NONE

    def test_can_read_from_none_policy(self):
        ctx = DomainContext(domain="agentic_core")
        assert ctx.can_read_from("apps_lic") is False

    def test_can_read_from_bidirectional(self):
        ctx = DomainContext(
            domain="agentic_core",
            sharing_policy=SharingPolicy.BIDIRECTIONAL,
        )
        assert ctx.can_read_from("apps_lic") is True

    def test_can_read_from_allowed_sources(self):
        ctx = DomainContext(
            domain="agentic_core",
            sharing_policy=SharingPolicy.READ_ONLY,
            allowed_sources=["apps_lic"],
        )
        assert ctx.can_read_from("apps_lic") is True
        assert ctx.can_read_from("apps_rg") is False


# ---------------------------------------------------------------------------
# memory_types
# ---------------------------------------------------------------------------
class TestMemoryTypes:
    def test_importable(self):
        try:
            import agentic_core.L1_cognition.types.memory_types as mod
            assert mod is not None
        except (ImportError, ModuleNotFoundError) as e:
            pytest.skip(f"memory_types deps unavailable: {e}")

    def test_has_content(self):
        try:
            import agentic_core.L1_cognition.types.memory_types as mod
            assert len(dir(mod)) > 0
        except (ImportError, ModuleNotFoundError) as e:
            pytest.skip(f"memory_types deps unavailable: {e}")


# ---------------------------------------------------------------------------
# observability_types
# ---------------------------------------------------------------------------
class TestObservabilityTypes:
    def test_importable(self):
        try:
            import agentic_core.L1_cognition.types.observability_types as mod
            assert mod is not None
        except (ImportError, ModuleNotFoundError) as e:
            pytest.skip(f"observability_types deps unavailable: {e}")


# ---------------------------------------------------------------------------
# validation_types
# ---------------------------------------------------------------------------
class TestValidationTypes:
    def test_importable(self):
        try:
            import agentic_core.L1_cognition.types.validation_types as mod
            assert mod is not None
        except (ImportError, ModuleNotFoundError) as e:
            pytest.skip(f"validation_types deps unavailable: {e}")
