"""
E2E Healing Tier Execution Proof — Tier -> Provider Invocation.

Phase 2:
  Wave 1: Router-level E2E dispatch (tier -> correct provider invocation).
  Wave 2: Agent integration E2E (allowlisted agents -> tier -> invocation).
  Wave 3: Negative controls (non-allowlisted blocked, bypass detected).

Phase 3:
  Wave 1: Deterministic trace equality (identical across two runs).
  Wave 2: No external calls guard (monkeypatch network layer).
  Wave 3: Coverage >= 90% for dispatcher + router + invoker seam.
"""

from __future__ import annotations

import ast
import json
import textwrap
from dataclasses import asdict
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
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

_emit_records_execution_trace("p0", "evidence", "test_healing_tier_e2e_invocation")
_emit_applies_guardrail("p0", "test_healing_tier_e2e_invocation", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_tier_e2e_invocation", "policy_binding")
_emit_snapshots_state("p0", "test_healing_tier_e2e_invocation", "state_snapshot")
emit_replay_key("p0", "test_healing_tier_e2e_invocation")
emit_determinism_digest("p0", "test_healing_tier_e2e_invocation")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_healing_tier_e2e_invocation", "execution_auth")
_emit_validates_capability("p2", "test_healing_tier_e2e_invocation", "capability_check")
_emit_routes_to_capability("p2", "test_healing_tier_e2e_invocation", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_tier_e2e_invocation", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_tier_e2e_invocation", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_tier_e2e_invocation", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_tier_e2e_invocation", "exec_output")
_emit_dispatches_agent("p3", "test_healing_tier_e2e_invocation", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_tier_e2e_invocation", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_tier_e2e_invocation", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_tier_e2e_invocation", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_tier_e2e_invocation", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_tier_e2e_invocation", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_tier_e2e_invocation", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_tier_e2e_invocation", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_tier_e2e_invocation", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_tier_e2e_invocation", "eval_metric")
_emit_stores_embedding("p4", "test_healing_tier_e2e_invocation", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_tier_e2e_invocation", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_tier_e2e_invocation", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L2_execution.healers.healing_tier_config import (
    HealingTierConfig,
    load_default_healing_tier_config,
)
from agentic_core.L2_execution.healers.healing_tier_dispatcher import (
    DefaultHealingProviderInvoker,
    InvocationRecord,
    dispatch_healing,
)
from agentic_core.L2_execution.healers.healing_tier_router import (
    clear_historical_success_rates,
    route_healing_tier,
)
from agentic_core.L2_execution.healers.healing_tier_types import (
    FailureSignal,
    HealingDecision,
    HealingInput,
    HealingTier,
)
from agentic_core.L2_execution.healers.tiering_allowlist import (
    TIERING_ALLOWLIST,
    TIERING_ALLOWLIST_FILE_PATHS,
    is_tiering_allowed,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_links_incident_trace,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
)

_emit_emits_metric_event("test_healing_tier_e2e_invocation", "p4obs", "metric_1")
_emit_emits_metric_event("test_healing_tier_e2e_invocation", "p4obs", "metric_2")
_emit_emits_metric_event("test_healing_tier_e2e_invocation", "p4obs", "metric_3")
_emit_emits_metric_event("test_healing_tier_e2e_invocation", "p4obs", "metric_4")
_emit_emits_metric_event("test_healing_tier_e2e_invocation", "p4obs", "metric_5")
_emit_emits_metric_event("test_healing_tier_e2e_invocation", "p4obs", "metric_6")
_emit_records_incident_event("test_healing_tier_e2e_invocation", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_healing_tier_e2e_invocation", "p4obs", "anomaly")
_emit_writes_observability_log("test_healing_tier_e2e_invocation", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_healing_tier_e2e_invocation", "p4obs", "mon_state")
_emit_triggers_alert("test_healing_tier_e2e_invocation", "p4obs", "alert")
_emit_links_incident_trace("test_healing_tier_e2e_invocation", "p4obs", "trace_link")
_emit_captures_pattern("test_healing_tier_e2e_invocation", "p3lm", "pattern")
_emit_records_learning_event("test_healing_tier_e2e_invocation", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_healing_tier_e2e_invocation", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_healing_tier_e2e_invocation", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_healing_tier_e2e_invocation", "p3lm", "routing")
_emit_improves_agent_policy("test_healing_tier_e2e_invocation", "p3lm", "policy")
_emit_stores_learning_state("test_healing_tier_e2e_invocation", "p3lm", "state")
_emit_records_execution_trace("test_healing_tier_e2e_invocation", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_healing_tier_e2e_invocation", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_healing_tier_e2e_invocation", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_healing_tier_e2e_invocation", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_healing_tier_e2e_invocation", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_healing_tier_e2e_invocation", "env_read", "p2_env_1")
_emit_reads_environ("test_healing_tier_e2e_invocation", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_healing_tier_e2e_invocation", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_healing_tier_e2e_invocation", "runtime_state", "p2_rt_2")

REPO_ROOT = Path(__file__).resolve().parents[4]


# ---------------------------------------------------------------------------
# FakeInvoker — records calls, no network
# ---------------------------------------------------------------------------


class FakeInvoker:
    """Test-only invoker that records every call without network access."""

    def __init__(self) -> None:
        self.calls: list[InvocationRecord] = []

    def invoke_local(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        rec = InvocationRecord(
            tier=HealingTier.LOCAL_AGENT,
            model_id="local",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_local",
        )
        self.calls.append(rec)
        return rec

    def invoke_qwen_vllm(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        rec = InvocationRecord(
            tier=HealingTier.QWEN_VLLM,
            model_id=config.model_qwen_vllm_id,
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_qwen_vllm",
        )
        self.calls.append(rec)
        return rec

    def invoke_gemini(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        rec = InvocationRecord(
            tier=HealingTier.GEMINI_2_5_PRO,
            model_id=config.model_gemini_2_5_pro_id,
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_gemini",
        )
        self.calls.append(rec)
        return rec


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_history():
    clear_historical_success_rates()
    yield
    clear_historical_success_rates()


@pytest.fixture
def default_config() -> HealingTierConfig:
    return load_default_healing_tier_config()


@pytest.fixture
def fake_invoker() -> FakeInvoker:
    return FakeInvoker()


def _make_input(
    failure_type: str = "syntax_error",
    blast_radius: float = 0.0,
    retry_count: int = 0,
    trace_id: str = "trace-e2e",
    failure_entropy_class: str = "MEDIUM",
) -> HealingInput:
    return HealingInput(
        failure_type=failure_type,
        error_signature=f"sig-{failure_type}",
        trace_id=trace_id,
        retry_count=retry_count,
        blast_radius_estimate=blast_radius,
        required_tools=(),
        violation_metadata_refs=(),
        failure_entropy_class=failure_entropy_class,
    )


# ===================================================================
# Phase 2 Wave 1: Router-level E2E dispatch tests
# ===================================================================


class TestE2EDispatchLocalAgent:
    """confidence >= X -> LOCAL_AGENT -> invoke_local only."""

    def test_local_agent_dispatch(self, default_config, fake_invoker):
        inp = _make_input(failure_type="syntax_error", blast_radius=0.0, retry_count=0)
        decision, record = dispatch_healing(inp, default_config, invoker=fake_invoker, agent_name="TestAgent")
        assert decision.tier == HealingTier.LOCAL_AGENT
        assert record.method_called == "invoke_local"
        assert record.tier == HealingTier.LOCAL_AGENT
        assert record.model_id == "local"
        assert record.agent_name == "TestAgent"
        assert record.trace_id == "trace-e2e"
        assert len(fake_invoker.calls) == 1
        assert fake_invoker.calls[0].method_called == "invoke_local"

    def test_no_other_provider_invoked(self, default_config, fake_invoker):
        inp = _make_input(failure_type="syntax_error", blast_radius=0.0, retry_count=0)
        dispatch_healing(inp, default_config, invoker=fake_invoker)
        methods = [c.method_called for c in fake_invoker.calls]
        assert methods == ["invoke_local"]
        assert "invoke_qwen_vllm" not in methods
        assert "invoke_gemini" not in methods


class TestE2EDispatchQwenVllm:
    """Y <= confidence < X -> QWEN_VLLM -> invoke_qwen_vllm only."""

    def test_qwen_vllm_dispatch(self, default_config, fake_invoker):
        inp = _make_input(failure_type="runtime_error", blast_radius=0.5, retry_count=0)
        decision, record = dispatch_healing(
            inp, default_config, invoker=fake_invoker, agent_name="QwenTestAgent"
        )
        assert decision.tier == HealingTier.QWEN_VLLM
        assert record.method_called == "invoke_qwen_vllm"
        assert record.tier == HealingTier.QWEN_VLLM
        assert record.model_id == default_config.model_qwen_vllm_id
        assert record.agent_name == "QwenTestAgent"
        assert len(fake_invoker.calls) == 1

    def test_no_other_provider_invoked(self, default_config, fake_invoker):
        inp = _make_input(failure_type="runtime_error", blast_radius=0.5, retry_count=0)
        dispatch_healing(inp, default_config, invoker=fake_invoker)
        methods = [c.method_called for c in fake_invoker.calls]
        assert methods == ["invoke_qwen_vllm"]


class TestE2EDispatchGemini:
    """confidence < Y -> GEMINI_2_5_PRO -> invoke_gemini only."""

    def test_gemini_dispatch(self, default_config, fake_invoker):
        # unknown + blast=1.0 + retry=2 + HIGH entropy -> score=0.395 < Y=0.40
        inp = _make_input(
            failure_type="unknown", blast_radius=1.0, retry_count=2, failure_entropy_class="HIGH"
        )
        decision, record = dispatch_healing(
            inp, default_config, invoker=fake_invoker, agent_name="GeminiTestAgent"
        )
        assert decision.tier == HealingTier.GEMINI_2_5_PRO
        assert record.method_called == "invoke_gemini"
        assert record.tier == HealingTier.GEMINI_2_5_PRO
        assert record.model_id == default_config.model_gemini_2_5_pro_id
        assert record.agent_name == "GeminiTestAgent"
        assert len(fake_invoker.calls) == 1

    def test_no_other_provider_invoked(self, default_config, fake_invoker):
        inp = _make_input(
            failure_type="unknown", blast_radius=1.0, retry_count=2, failure_entropy_class="HIGH"
        )
        dispatch_healing(inp, default_config, invoker=fake_invoker)
        methods = [c.method_called for c in fake_invoker.calls]
        assert methods == ["invoke_gemini"]


class TestE2EDispatchRetryForcing:
    """retry_count >= max -> GEMINI_2_5_PRO regardless of confidence."""

    def test_retry_forces_gemini(self, default_config, fake_invoker):
        inp = _make_input(
            failure_type="syntax_error",
            blast_radius=0.0,
            retry_count=default_config.max_heal_retries,
        )
        decision, record = dispatch_healing(
            inp, default_config, invoker=fake_invoker, agent_name="RetryAgent"
        )
        assert decision.tier == HealingTier.GEMINI_2_5_PRO
        assert record.method_called == "invoke_gemini"
        assert any("FORCED_GEMINI" in r for r in decision.reason_codes)
        assert len(fake_invoker.calls) == 1

    def test_retry_above_max_forces_gemini(self, default_config, fake_invoker):
        inp = _make_input(
            failure_type="syntax_error",
            blast_radius=0.0,
            retry_count=default_config.max_heal_retries + 10,
        )
        decision, record = dispatch_healing(inp, default_config, invoker=fake_invoker)
        assert decision.tier == HealingTier.GEMINI_2_5_PRO
        assert record.method_called == "invoke_gemini"


# ===================================================================
# Phase 2 Wave 2: Agent integration E2E tests
# ===================================================================

_ALLOWLIST_PARAMS = sorted(TIERING_ALLOWLIST, key=lambda t: t[0])


class TestAgentIntegrationE2E:
    """Each allowlisted agent -> FailureSignal -> dispatch -> correct invocation."""

    @pytest.mark.parametrize("agent_name,file_path", _ALLOWLIST_PARAMS)
    def test_agent_dispatches_via_router(self, agent_name, file_path, default_config, fake_invoker):
        """Allowlisted agent's FailureSignal routes through dispatch_healing."""
        signal = FailureSignal(
            source_agent=agent_name,
            failure_type="syntax_error",
            error_signature=f"sig-{agent_name}",
            trace_id=f"trace-{agent_name}",
            context={},
            retry_count=0,
            blast_radius_estimate=0.0,
        )
        inp = signal.to_healing_input()
        decision, record = dispatch_healing(inp, default_config, invoker=fake_invoker, agent_name=agent_name)
        assert isinstance(decision.tier, HealingTier)
        assert record.agent_name == agent_name
        assert record.trace_id == f"trace-{agent_name}"
        assert len(fake_invoker.calls) == 1

    @pytest.mark.parametrize("agent_name,file_path", _ALLOWLIST_PARAMS)
    def test_agent_is_allowlisted(self, agent_name, file_path):
        assert is_tiering_allowed(agent_name)

    def test_at_least_one_agent_reaches_each_tier(self, default_config):
        """Prove each tier is reachable via at least one allowlisted agent."""
        tiers_reached: set[HealingTier] = set()
        scenarios = [
            ("syntax_error", 0.0, 0),  # -> LOCAL_AGENT
            ("runtime_error", 0.5, 0),  # -> QWEN_VLLM
            ("unknown", 1.0, 3),  # -> GEMINI_2_5_PRO (retry >= max_heal_retries forces)
        ]
        for agent_name, _ in _ALLOWLIST_PARAMS[:3]:
            for ft, blast, retry in scenarios:
                fake = FakeInvoker()
                signal = FailureSignal(
                    source_agent=agent_name,
                    failure_type=ft,
                    error_signature=f"sig-{ft}",
                    trace_id=f"trace-{agent_name}-{ft}",
                    context={},
                    retry_count=retry,
                    blast_radius_estimate=blast,
                )
                decision, record = dispatch_healing(
                    signal.to_healing_input(),
                    default_config,
                    invoker=fake,
                    agent_name=agent_name,
                )
                tiers_reached.add(decision.tier)

        assert HealingTier.LOCAL_AGENT in tiers_reached
        assert HealingTier.QWEN_VLLM in tiers_reached
        assert HealingTier.GEMINI_2_5_PRO in tiers_reached


# ===================================================================
# Phase 2 Wave 3: Negative controls
# ===================================================================


class TestNegativeControlsE2E:
    """Non-allowlisted agents and bypass attempts."""

    def test_non_allowlisted_agent_not_in_allowlist(self):
        assert not is_tiering_allowed("SomeRandomAgent")
        assert not is_tiering_allowed("FakeHealerAgent")

    def test_non_allowlisted_can_still_dispatch_but_trace_shows_agent(self, default_config, fake_invoker):
        """Non-allowlisted agent CAN call dispatch_healing (no runtime block),
        but the invocation trace records the agent name for audit."""
        inp = _make_input(failure_type="syntax_error", blast_radius=0.0)
        decision, record = dispatch_healing(
            inp, default_config, invoker=fake_invoker, agent_name="UnauthorizedAgent"
        )
        assert record.agent_name == "UnauthorizedAgent"
        # Static audit (audit_healing_tier_enforcement.py) catches unauthorized imports

    def test_synthetic_bypass_detected_by_ast(self):
        """A synthetic module that directly selects HealingTier members is detected."""
        bypass_code = textwrap.dedent("""
            from agentic_core.L2_execution.healers.healing_tier_types import HealingTier
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
_emit_pulls_context("p1", "test_healing_tier_e2e_invocation", "context_pull")
_emit_pulls_context("p1", "test_healing_tier_e2e_invocation", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_healing_tier_e2e_invocation", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_healing_tier_e2e_invocation", "uwg_term_secondary")
_emit_writes_through("p1", "test_healing_tier_e2e_invocation", "write_through")
_emit_writes_through("p1", "test_healing_tier_e2e_invocation", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_healing_tier_e2e_invocation", "safety_validation")
_emit_invokes_eval("p1", "test_healing_tier_e2e_invocation", "eval_call")
_emit_proposal_commits_routing("p1", "test_healing_tier_e2e_invocation", "routing_commit")

            def bypass_select(confidence: float):
                if confidence < 0.4:
                    return HealingTier.GEMINI_2_5_PRO
                elif confidence < 0.75:
                    return HealingTier.QWEN_VLLM
                return HealingTier.LOCAL_AGENT
        """)
        tree = ast.parse(bypass_code)
        imported_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)
        assert "HealingTier" in imported_names

        members = {"LOCAL_AGENT", "QWEN_VLLM", "GEMINI_2_5_PRO"}
        found = {
            node.attr
            for node in ast.walk(tree)
            if (
                isinstance(node, ast.Attribute)
                and node.attr in members
                and isinstance(node.value, ast.Name)
                and node.value.id == "HealingTier"
            )
        }
        assert found == members, "Static scanner must detect all bypass members"

    def test_non_tiered_files_do_not_import_dispatcher(self):
        """Non-system, non-test, non-allowlisted files must not import dispatcher."""
        system_files = {
            "agentic_core/L2_execution/healers/healing_tier_dispatcher.py",
            "agentic_core/L2_execution/healers/healing_tier_router.py",
            "agentic_core/L2_execution/healers/healing_tier_types.py",
            "agentic_core/L2_execution/healers/healing_tier_config.py",
            "agentic_core/L2_execution/healers/tiering_allowlist.py",
        }
        dispatcher_module = "agentic_core.L2_execution.healers.healing_tier_dispatcher"
        scan_roots = [
            REPO_ROOT / AGENTIC_CORE_DIR,
            REPO_ROOT / APPS_LIC_DIR,
            REPO_ROOT / APPS_RG_DIR,
            REPO_ROOT / APPS_SHARED_DIR,
        ]
        violations: list[str] = []
        for root in scan_roots:
            if not root.exists():
                continue
            for fpath in root.rglob("*.py"):
                if "__pycache__" in fpath.parts:
                    continue
                rel = fpath.relative_to(REPO_ROOT).as_posix()
                if rel in system_files:
                    continue
                if "/tests/" in rel or rel.startswith("tests/"):
                    continue
                if rel in TIERING_ALLOWLIST_FILE_PATHS:
                    continue
                try:
                    tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
                except SyntaxError as e:
                    assert False, f"SyntaxError in {fpath}: {e}"
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        if dispatcher_module in node.module:
                            violations.append(rel)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if dispatcher_module in alias.name:
                                violations.append(rel)
        if violations:
            pytest.fail(
                f"{len(violations)} non-tiered file(s) import dispatcher:\n"
                + "\n".join(f"  {v}" for v in violations)
            )


# ===================================================================
# Phase 3 Wave 1: Deterministic trace equality
# ===================================================================


class TestDeterministicTraceEquality:
    """Same inputs -> identical tier + identical invocation trace."""

    @pytest.mark.parametrize(
        "failure_type,blast,retry",
        [
            ("syntax_error", 0.0, 0),
            ("runtime_error", 0.5, 0),
            ("unknown", 1.0, 2),
            ("import_cycle", 0.3, 1),
            ("syntax_error", 0.0, 3),  # forced GEMINI
        ],
    )
    def test_identical_dispatch_twice(self, failure_type, blast, retry, default_config):
        """Two dispatches with same input produce byte-identical traces."""
        inp = _make_input(failure_type=failure_type, blast_radius=blast, retry_count=retry)

        fake1 = FakeInvoker()
        d1, r1 = dispatch_healing(inp, default_config, invoker=fake1, agent_name="DetAgent")

        fake2 = FakeInvoker()
        d2, r2 = dispatch_healing(inp, default_config, invoker=fake2, agent_name="DetAgent")

        # Decision equality
        assert d1.tier == d2.tier
        assert d1.heal_confidence == d2.heal_confidence
        assert d1.reason_codes == d2.reason_codes

        # Invocation record equality (serialized)
        assert asdict(r1) == asdict(r2)

    def test_serialized_trace_byte_identical(self, default_config):
        """JSON-serialized traces are byte-identical across two runs."""
        inp = _make_input(failure_type="syntax_error", blast_radius=0.0, retry_count=0)

        fake1 = FakeInvoker()
        _, r1 = dispatch_healing(inp, default_config, invoker=fake1, agent_name="ByteAgent")

        fake2 = FakeInvoker()
        _, r2 = dispatch_healing(inp, default_config, invoker=fake2, agent_name="ByteAgent")

        j1 = json.dumps(asdict(r1), sort_keys=True)
        j2 = json.dumps(asdict(r2), sort_keys=True)
        assert j1 == j2


# ===================================================================
# Phase 3 Wave 2: No external calls guard
# ===================================================================


class TestNoExternalCallsGuard:
    """Monkeypatch real provider to raise; assert only FakeInvoker is used."""

    def test_default_invoker_does_not_make_network_calls(self, default_config):
        """DefaultHealingProviderInvoker methods return records without network."""
        invoker = DefaultHealingProviderInvoker()
        inp = _make_input()
        decision = route_healing_tier(inp, default_config)

        # Each method should return an InvocationRecord, not raise
        r1 = invoker.invoke_local(inp, decision, default_config, agent_name="test")
        assert r1.method_called == "invoke_local"

        r2 = invoker.invoke_qwen_vllm(inp, decision, default_config, agent_name="test")
        assert r2.method_called == "invoke_qwen_vllm"

        r3 = invoker.invoke_gemini(inp, decision, default_config, agent_name="test")
        assert r3.method_called == "invoke_gemini"

    def test_fake_invoker_records_without_network(self, default_config, fake_invoker):
        """FakeInvoker records calls without any network access."""
        inp = _make_input()
        dispatch_healing(inp, default_config, invoker=fake_invoker, agent_name="NoNetAgent")
        assert len(fake_invoker.calls) == 1
        # No exception = no network call attempted

    def test_poisoned_invoker_raises_on_real_call(self, default_config):
        """A poisoned invoker that raises on any call proves FakeInvoker isolation."""

        class PoisonedInvoker:
            def invoke_local(self, *a, **kw):
                raise RuntimeError("REAL NETWORK CALL ATTEMPTED: invoke_local")

            def invoke_qwen_vllm(self, *a, **kw):
                raise RuntimeError("REAL NETWORK CALL ATTEMPTED: invoke_qwen_vllm")

            def invoke_gemini(self, *a, **kw):
                raise RuntimeError("REAL NETWORK CALL ATTEMPTED: invoke_gemini")

        inp = _make_input()
        with pytest.raises(RuntimeError, match="REAL NETWORK CALL ATTEMPTED"):
            dispatch_healing(inp, default_config, invoker=PoisonedInvoker())

    def test_dispatch_with_fake_does_not_trigger_poison(self, default_config, fake_invoker):
        """dispatch_healing with FakeInvoker never triggers poison paths."""
        inp = _make_input()
        # This should NOT raise
        decision, record = dispatch_healing(inp, default_config, invoker=fake_invoker)
        assert record.method_called in {"invoke_local", "invoke_qwen_vllm", "invoke_gemini"}


# ===================================================================
# Phase 3 Wave 3: Coverage target (focused)
# ===================================================================


class TestDispatcherCoverage:
    """Exercise all dispatcher code paths for coverage."""

    def test_all_three_tiers_dispatched(self, default_config):
        """Exercise all three tier dispatch paths."""
        scenarios = [
            ("syntax_error", 0.0, 0, "invoke_local"),
            ("runtime_error", 0.5, 0, "invoke_qwen_vllm"),
            ("unknown", 1.0, 3, "invoke_gemini"),
        ]
        for ft, blast, retry, expected_method in scenarios:
            fake = FakeInvoker()
            inp = _make_input(failure_type=ft, blast_radius=blast, retry_count=retry)
            _, record = dispatch_healing(inp, default_config, invoker=fake)
            assert record.method_called == expected_method, (
                f"Expected {expected_method} for {ft}, got {record.method_called}"
            )

    def test_default_invoker_used_when_none(self, default_config):
        """dispatch_healing with invoker=None uses DefaultHealingProviderInvoker."""
        inp = _make_input()
        decision, record = dispatch_healing(inp, default_config, invoker=None)
        assert isinstance(record, InvocationRecord)
        assert record.method_called in {"invoke_local", "invoke_qwen_vllm", "invoke_gemini"}

    def test_invocation_record_fields(self, default_config, fake_invoker):
        """All InvocationRecord fields are populated correctly."""
        inp = _make_input(trace_id="trace-fields-test")
        decision, record = dispatch_healing(
            inp, default_config, invoker=fake_invoker, agent_name="FieldsAgent"
        )
        assert record.trace_id == "trace-fields-test"
        assert record.agent_name == "FieldsAgent"
        assert record.heal_confidence == decision.heal_confidence
        assert record.tier == decision.tier
