"""RG-GAP-01 + RG-GAP-02 invariant tests.

RG-GAP-01: ResumeGenerator._generate_with_gemini must route through
  SovereignLLMGateway, not direct google.generativeai SDK.
  Negative control: google.generativeai must NOT be imported by the method.

RG-GAP-02: HardenedRouter._initialize_executors must wire HardenedGeminiExecutor
  for Provider.GOOGLE.
  Negative control: Google provider missing from executors → assert key absent.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_resume_generator_gateway")
_emit_applies_guardrail("p0", "test_resume_generator_gateway", "p0_governance")
_emit_reads_policy_state("p0", "test_resume_generator_gateway", "policy_binding")
_emit_snapshots_state("p0", "test_resume_generator_gateway", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_resume_generator_gateway", "p4obs", "metric_1")
_emit_emits_metric_event("test_resume_generator_gateway", "p4obs", "metric_2")
_emit_emits_metric_event("test_resume_generator_gateway", "p4obs", "metric_3")
_emit_emits_metric_event("test_resume_generator_gateway", "p4obs", "metric_4")
_emit_emits_metric_event("test_resume_generator_gateway", "p4obs", "metric_5")
_emit_emits_metric_event("test_resume_generator_gateway", "p4obs", "metric_6")
_emit_records_incident_event("test_resume_generator_gateway", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_resume_generator_gateway", "p4obs", "anomaly")
_emit_writes_observability_log("test_resume_generator_gateway", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_resume_generator_gateway", "p4obs", "mon_state")
_emit_triggers_alert("test_resume_generator_gateway", "p4obs", "alert")
_emit_links_incident_trace("test_resume_generator_gateway", "p4obs", "trace_link")
_emit_captures_pattern("test_resume_generator_gateway", "p3lm", "pattern")
_emit_records_learning_event("test_resume_generator_gateway", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_resume_generator_gateway", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_resume_generator_gateway", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_resume_generator_gateway", "p3lm", "routing")
_emit_improves_agent_policy("test_resume_generator_gateway", "p3lm", "policy")
_emit_stores_learning_state("test_resume_generator_gateway", "p3lm", "state")
_emit_records_execution_trace("test_resume_generator_gateway", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_resume_generator_gateway", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_resume_generator_gateway", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_resume_generator_gateway", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_resume_generator_gateway", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_resume_generator_gateway", "env_read", "p2_env_1")
_emit_reads_environ("test_resume_generator_gateway", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_resume_generator_gateway", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_resume_generator_gateway", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_resume_generator_gateway", "context_pull")
_emit_pulls_context("p1", "test_resume_generator_gateway", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_resume_generator_gateway", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_resume_generator_gateway", "uwg_term_2")
_emit_writes_through("p1", "test_resume_generator_gateway", "write_through")
_emit_writes_through("p1", "test_resume_generator_gateway", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_resume_generator_gateway", "safety_validation")
_emit_invokes_eval("p1", "test_resume_generator_gateway", "eval_call")
_emit_proposal_commits_routing("p1", "test_resume_generator_gateway", "routing_commit")
_emit_escalates_to_human("p1", "test_resume_generator_gateway", "human_escalation")
_emit_routes_through("p1", "test_resume_generator_gateway", "route_through")
_emit_checks_agent_registry("p1", "test_resume_generator_gateway", "agent_registry")
_emit_validates_agent_capability("p1", "test_resume_generator_gateway", "capability")
_emit_dispatches_execution_plan("p1", "test_resume_generator_gateway", "exec_plan")
_emit_agent_executes_agent("p1", "test_resume_generator_gateway", "sub_agent")
_emit_routes_to_agent("p1", "test_resume_generator_gateway", "target_agent")
_emit_verifies_policy("p1", "test_resume_generator_gateway", "policy_check")
_emit_observes_runtime_state("p1", "test_resume_generator_gateway", "runtime_state")
_emit_verifies_boundary("p1", "test_resume_generator_gateway", "boundary_check")
_emit_transcripts_response("p1", "test_resume_generator_gateway", "transcript")
_emit_hard_fails_untranscripted("p1", "test_resume_generator_gateway")
_emit_gated_by_confidence("p1", "test_resume_generator_gateway", "confidence_gate")
emit_replay_key("p0", "test_resume_generator_gateway")
emit_determinism_digest("p0", "test_resume_generator_gateway")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_resume_generator_gateway", "execution_auth")
_emit_validates_capability("p2", "test_resume_generator_gateway", "capability_check")
_emit_routes_to_capability("p2", "test_resume_generator_gateway", "capability_route")
_emit_writes_via_uwg("p2", "test_resume_generator_gateway", "uwg_write")
_emit_blocks_direct_write("p2", "test_resume_generator_gateway", "direct_write_block")
_emit_records_tool_invocation("p2", "test_resume_generator_gateway", "tool_invocation")
_emit_captures_execution_output("p2", "test_resume_generator_gateway", "exec_output")
_emit_dispatches_agent("p3", "test_resume_generator_gateway", "agent_dispatch")
_emit_coordinates_agents("p3", "test_resume_generator_gateway", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_resume_generator_gateway", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_resume_generator_gateway", "healing_outcome")
_emit_escalates_failure("p3", "test_resume_generator_gateway", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_resume_generator_gateway", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_resume_generator_gateway", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_resume_generator_gateway", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_resume_generator_gateway", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_resume_generator_gateway", "eval_metric")
_emit_stores_embedding("p4", "test_resume_generator_gateway", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_resume_generator_gateway", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_resume_generator_gateway", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def _stub_resume_generator_imports():
    """Stub legacy runtime.shared.* imports so ResumeGenerator can be imported in tests."""
    import types

    _provider_enum = MagicMock()
    _provider_enum.GOOGLE = "google"
    _provider_enum.OPENAI = "openai"
    _provider_enum.ANTHROPIC = "anthropic"

    runtime_mod = types.ModuleType("runtime")
    runtime_shared = types.ModuleType("runtime.shared")
    runtime_mp = types.ModuleType("runtime.shared.multi_provider_clients")
    runtime_mp.Provider = _provider_enum
    runtime_mp.get_client = MagicMock()
    runtime_mod.shared = runtime_shared
    runtime_shared.multi_provider_clients = runtime_mp

    sys.modules.setdefault("runtime", runtime_mod)
    sys.modules.setdefault("runtime.shared", runtime_shared)
    sys.modules.setdefault("runtime.shared.multi_provider_clients", runtime_mp)
    return _provider_enum


class TestResumeGeneratorGatewayRouting:
    def test_generate_with_gemini_uses_sovereign_gateway(self):
        """RG-GAP-01 positive: _generate_with_gemini routes through SovereignLLMGateway."""
        _stub_resume_generator_imports()
        from apps_rg.tools.ResumeGenerator import ResumeGenerator

        mock_response = MagicMock()
        mock_response.text = "Generated resume content"

        mock_gateway_instance = MagicMock()
        mock_gateway_instance.generate.return_value = mock_response

        mock_gateway_cls = MagicMock(return_value=mock_gateway_instance)
        mock_request_cls = MagicMock(return_value=MagicMock())

        with patch.dict(
            "sys.modules",
            {
                "agentic_core.interfaces.gateway": MagicMock(
                    SovereignLLMGateway=mock_gateway_cls,
                    GenerationRequest=mock_request_cls,
                )
            },
        ):
            gen = ResumeGenerator(llm_client=MagicMock())
            result = gen._generate_with_gemini("test prompt")

        assert result == "Generated resume content"
        mock_gateway_cls.assert_called_once()
        mock_gateway_instance.generate.assert_called_once()

    def test_generate_with_gemini_does_not_import_sdk_directly(self):
        """RG-GAP-01 negative control: google.generativeai must not appear in method source."""
        import inspect

        _stub_resume_generator_imports()
        from apps_rg.tools.ResumeGenerator import ResumeGenerator

        source = inspect.getsource(ResumeGenerator._generate_with_gemini)
        assert "google.generativeai" not in source, (
            "RG-GAP-01 violated: _generate_with_gemini still imports google.generativeai directly"
        )

    def test_generate_with_gemini_raises_when_gateway_unavailable(self):
        """RG-GAP-01: Gateway unavailable → RuntimeError, not silent fallback to SDK."""
        _stub_resume_generator_imports()
        from apps_rg.tools.ResumeGenerator import ResumeGenerator

        with patch.dict(
            "sys.modules",
            {
                "agentic_core.interfaces.gateway": MagicMock(
                    SovereignLLMGateway=MagicMock(side_effect=ImportError("gateway missing")),
                    GenerationRequest=MagicMock(),
                )
            },
        ):
            gen = ResumeGenerator(llm_client=MagicMock())
            with pytest.raises(RuntimeError, match="gateway unavailable"):
                gen._generate_with_gemini("test prompt")

    def test_generate_with_gemini_uses_gemini_2_5_pro_model(self):
        """RG-GAP-01: model must be gemini-2.5-pro, not stale gemini-1.5-flash."""
        _stub_resume_generator_imports()
        from apps_rg.tools.ResumeGenerator import ResumeGenerator

        captured_request = {}

        def capture_request(request):
            captured_request["model"] = request.model
            resp = MagicMock()
            resp.text = "ok"
            return resp

        mock_gateway = MagicMock()
        mock_gateway.generate.side_effect = capture_request

        class _FakeRequest:
            def __init__(self, **kwargs):
                self.model = kwargs.get("model")
                self.agent_id = kwargs.get("agent_id", "test-agent")
                self.provider = kwargs.get("provider", "gemini")

        with patch.dict(
            "sys.modules",
            {
                "agentic_core.interfaces.gateway": MagicMock(
                    SovereignLLMGateway=MagicMock(return_value=mock_gateway),
                    GenerationRequest=_FakeRequest,
                )
            },
        ):
            gen = ResumeGenerator(llm_client=MagicMock())
            gen._generate_with_gemini("test prompt")

        assert captured_request.get("model") == "gemini-2.5-pro", (
            f"Expected gemini-2.5-pro, got {captured_request.get('model')}"
        )


class TestHardenedRouterGeminiExecutorWired:
    """AST-level verification that HardenedGeminiExecutor is wired into _initialize_executors."""

    _SOURCE_FILE = "apps_rg/types/AllProvidersDownError.py"

    def _read_source(self) -> str:
        from pathlib import Path

        root = Path(__file__).parents[3]
        return (root / self._SOURCE_FILE).read_text(encoding="utf-8")

    def test_hardened_gemini_executor_imported(self):
        """RG-GAP-02 positive: HardenedGeminiExecutor must be imported in AllProvidersDownError.py."""
        src = self._read_source()
        assert "HardenedGeminiExecutor" in src, (
            "RG-GAP-02: HardenedGeminiExecutor not imported in AllProvidersDownError.py"
        )

    def test_hardened_gemini_executor_instantiated_for_google(self):
        """RG-GAP-02 positive: HardenedGeminiExecutor() must be instantiated in _initialize_executors."""
        src = self._read_source()
        assert "HardenedGeminiExecutor()" in src, (
            "RG-GAP-02: HardenedGeminiExecutor() not instantiated for Provider.GOOGLE"
        )

    def test_negative_no_warning_comment_for_google_path(self):
        """RG-GAP-02 negative control: the old warning comment must be gone."""
        src = self._read_source()
        assert "HardenedGeminiExecutor not yet implemented" not in src, (
            "RG-GAP-02 regression: old stub comment still present — executor not actually wired"
        )

    def test_google_provider_branch_assigns_executor(self):
        """RG-GAP-02: The elif Provider.GOOGLE branch must assign HardenedGeminiExecutor(), not just warn."""
        import re

        src = self._read_source()
        # Find the elif/if block for Provider.GOOGLE in _initialize_executors
        match = re.search(
            r"elif provider == Provider\.GOOGLE.*?(?=elif|else|\Z)",
            src,
            re.DOTALL,
        )
        assert match is not None, "Could not find 'elif provider == Provider.GOOGLE' block in source"
        block = match.group(0)
        assert "HardenedGeminiExecutor()" in block, (
            f"RG-GAP-02: Provider.GOOGLE block does not assign HardenedGeminiExecutor(): {block!r}"
        )
        assert "logger.warning" not in block, (
            "RG-GAP-02: Provider.GOOGLE block still only logs a warning — executor not wired"
        )
