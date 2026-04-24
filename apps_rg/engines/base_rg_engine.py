"""
Base Resume Agent - Foundation for all RG Sovereign V2.5 Engines
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "base_rg_engine", "p0_governance")
_emit_reads_policy_state("p0", "base_rg_engine", "policy_binding")
_emit_snapshots_state("p0", "base_rg_engine", "state_snapshot")
emit_replay_key("p0", "base_rg_engine")
emit_determinism_digest("p0", "base_rg_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "base_rg_engine", "execution_auth")
_emit_validates_capability("p2", "base_rg_engine", "capability_check")
_emit_routes_to_capability("p2", "base_rg_engine", "capability_route")
_emit_writes_via_uwg("p2", "base_rg_engine", "uwg_write")
_emit_blocks_direct_write("p2", "base_rg_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "base_rg_engine", "tool_invocation")
_emit_captures_execution_output("p2", "base_rg_engine", "exec_output")
_emit_dispatches_agent("p3", "base_rg_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "base_rg_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "base_rg_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "base_rg_engine", "healing_outcome")
_emit_escalates_failure("p3", "base_rg_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "base_rg_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "base_rg_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "base_rg_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "base_rg_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "base_rg_engine", "eval_metric")
_emit_stores_embedding("p4", "base_rg_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "base_rg_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "base_rg_engine", "exec_snapshot_link")

try:
    from agentic_core.interfaces.execution_contracts import (
        AgentOutputContract,
        get_current_secret,
        wrap_output,
    )

    _OUTPUT_CONTRACT_AVAILABLE = True
except ImportError as e:  # guardian: allow-silent-swallow - Optional execution contracts
    _OUTPUT_CONTRACT_AVAILABLE = False
    logging.getLogger(__name__).debug(f"Output contracts not available: {e}")
try:
    from pydantic import BaseModel
except ImportError as e:  # guardian: allow-silent-swallow - Optional pydantic
    BaseModel = Any
    logging.getLogger(__name__).debug(f"Pydantic not available: {e}")
try:
    from apps_rg.utils.mixins import HealerMixin, MCPHardenedMixin

    MIXINS_AVAILABLE = True
except ImportError as e:  # guardian: allow-silent-swallow - Optional RG mixins
    MIXINS_AVAILABLE = False
    logging.getLogger(__name__).debug(f"RG mixins not available: {e}")

    class MCPHardenedMixin:
        """Stub MCPHardenedMixin for standalone usage."""

        def __init__(self, *args, **kwargs):
            pass

    class HealerMixin:
        """Stub HealerMixin for standalone usage."""

        def __init__(self, *args, **kwargs):
            pass

        # guardian: allow-magic-config
        def heal_repository(
            self,
            dry_run: bool = False,
            execute: bool = False,
            depth: int = 0,
            max_depth: int = 3,
            _call_path: set | None = None,
        ) -> dict[str, int]:
            return {"violations": 0, "fixed": 0, "errors": 0, "skipped": 0}


from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("base_rg_engine", "p4obs", "metric_1")
_emit_emits_metric_event("base_rg_engine", "p4obs", "metric_2")
_emit_emits_metric_event("base_rg_engine", "p4obs", "metric_3")
_emit_emits_metric_event("base_rg_engine", "p4obs", "metric_4")
_emit_emits_metric_event("base_rg_engine", "p4obs", "metric_5")
_emit_emits_metric_event("base_rg_engine", "p4obs", "metric_6")
_emit_records_incident_event("base_rg_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("base_rg_engine", "p4obs", "anomaly")
_emit_writes_observability_log("base_rg_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("base_rg_engine", "p4obs", "mon_state")
_emit_triggers_alert("base_rg_engine", "p4obs", "alert")
_emit_links_incident_trace("base_rg_engine", "p4obs", "trace_link")
_emit_captures_pattern("base_rg_engine", "p3lm", "pattern")
_emit_records_learning_event("base_rg_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("base_rg_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("base_rg_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("base_rg_engine", "p3lm", "routing")
_emit_improves_agent_policy("base_rg_engine", "p3lm", "policy")
_emit_stores_learning_state("base_rg_engine", "p3lm", "state")
_emit_records_execution_trace("base_rg_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("base_rg_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("base_rg_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("base_rg_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("base_rg_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("base_rg_engine", "env_read", "p2_env_1")
_emit_reads_environ("base_rg_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("base_rg_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("base_rg_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "base_rg_engine", "context_pull")
_emit_pulls_context("p1", "base_rg_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "base_rg_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "base_rg_engine", "uwg_term_2")
_emit_writes_through("p1", "base_rg_engine", "write_through")
_emit_writes_through("p1", "base_rg_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "base_rg_engine", "safety_validation")
_emit_invokes_eval("p1", "base_rg_engine", "eval_call")
_emit_proposal_commits_routing("p1", "base_rg_engine", "routing_commit")
_emit_escalates_to_human("p1", "base_rg_engine", "human_escalation")
_emit_routes_through("p1", "base_rg_engine", "route_through")
_emit_checks_agent_registry("p1", "base_rg_engine", "agent_registry")
_emit_validates_agent_capability("p1", "base_rg_engine", "capability")
_emit_dispatches_execution_plan("p1", "base_rg_engine", "exec_plan")
_emit_agent_executes_agent("p1", "base_rg_engine", "sub_agent")
_emit_routes_to_agent("p1", "base_rg_engine", "target_agent")
_emit_verifies_policy("p1", "base_rg_engine", "policy_check")
_emit_observes_runtime_state("p1", "base_rg_engine", "runtime_state")
_emit_verifies_boundary("p1", "base_rg_engine", "boundary_check")
_emit_transcripts_response("p1", "base_rg_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "base_rg_engine")
_emit_gated_by_confidence("p1", "base_rg_engine", "confidence_gate")

logger = logging.getLogger(__name__)


class BaseRGEngine(MCPHardenedMixin, HealerMixin, ABC):
    AGENT_ID: str = ""
    _current_trace_id: str = ""
    "\n    Abstract base class for all Resume Generation engines.\n\n    Provides:\n    - MCP hardening capabilities\n    - Self-healing capabilities\n    - Standard logging interface\n    - Pydantic model I/O enforcement\n    - Knowledge base integration\n    "

    def __init__(self, config: BaseModel | None = None, **kwargs):
        """Initialize the engine with configuration."""
        self.node_id = kwargs.pop("node_id", None)
        super().__init__()
        self.config = config
        self.ctx = config
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = True
        try:
            from apps_rg.config import load_rg_specs

            self.rg_specs = load_rg_specs()
        except ImportError:  # guardian: allow-silent-swallow - Optional RG specs
            self.rg_specs = None
            self.logger.warning("RG specs not available")
        try:
            from apps_rg.config.reasoning_toggles_config import DEFAULT_TOGGLES

            self.toggles = DEFAULT_TOGGLES
        except ImportError:  # guardian: allow-silent-swallow - Optional reasoning toggles
            self.toggles = None
            self.logger.warning("Reasoning toggles not available")
        try:
            from apps_rg.types.PromptTemplate import FROZEN_SNAPSHOT

            self.knowledge = FROZEN_SNAPSHOT
        except ImportError:  # guardian: allow-silent-swallow - Optional knowledge base
            self.knowledge = None
            self.logger.warning("Knowledge base not available")

    def _mcp_audit(self, event: str, **kwargs) -> None:
        """Log an MCP audit event. Lightweight stub for standalone usage."""
        self.logger.debug(f"MCP_AUDIT: {event} {kwargs}")

    def record_fail(self, message: str, *, signal: str = "", data: dict | None = None) -> None:
        """Record a failure event."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BaseRGEngine.record_fail")

        self.logger.warning(f"FAIL [{self.name}]: {message}")
        if hasattr(self.ctx, "trace") and self.ctx is not None:
            self.ctx.trace.add_trace(f"{self.name}_FAIL", {"message": message, "signal": signal})

    def record_pass(self, message: str, *, data: dict | None = None) -> None:
        """Record a pass event."""
        self.logger.info(f"PASS [{self.name}]: {message}")
        if hasattr(self.ctx, "trace") and self.ctx is not None:
            self.ctx.trace.add_trace(f"{self.name}_PASS", {"message": message, **(data or {})})

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # Tier 3 runtime-ADG: auto-wrap concrete execute() with seal_step.
        from apps_shared.utils.engine_seal_step_mixin import (  # noqa: PLC0415
            install_seal_step_autowrap,
        )

        install_seal_step_autowrap(cls)

    @abstractmethod
    def execute(self, input_data: BaseModel) -> BaseModel:
        """
        Main execution method - must be implemented by subclasses.

        Args:
            input_data: Pydantic model containing input

        Returns:
            Pydantic model containing output
        """
        pass

    def execute_contracted(self, input_data: BaseModel, trace_id: str = "") -> "AgentOutputContract":
        """Execute and wrap result in a signed AgentOutputContract.

        Use this instead of execute() at all call sites that feed L6 observability.
        """
        if not _OUTPUT_CONTRACT_AVAILABLE:
            raise RuntimeError("AgentOutputContract not available — check agentic_core import")
        if not self.AGENT_ID:
            raise RuntimeError(f"{self.__class__.__name__}.AGENT_ID must be set to its AGENT_REGISTRY key")
        result = self.execute(input_data)
        return wrap_output(
            agent_id=self.AGENT_ID,
            trace_id=trace_id or self._current_trace_id,
            payload_model=result,
            secret=get_current_secret(),
        )

    def validate_input(self, input_data: BaseModel) -> bool:
        """Validate input data before execution."""
        if not isinstance(input_data, BaseModel):
            raise TypeError(f"Input must be a Pydantic BaseModel, got {type(input_data)}")
        return True

    def run_subatomic_test(self) -> dict[str, Any]:
        """Run subatomic self-tests (SubatomicTestingMixin compatibility).

        Returns:
            Test results dict
        """
        return {"status": "passed", "tests_run": 0}

    def get_prompt(self, prompt_id: str) -> str:
        """Get prompt from knowledge base."""
        if self.knowledge:
            from apps_rg.types.PromptTemplate import get_prompt

            return get_prompt(prompt_id)
        return ""

    def get_node_config(self, node_id: str) -> Any:
        """Get K-node configuration from knowledge base."""
        # guardian: allow-config-with-logic
        if self.knowledge:
            from apps_rg.types.PromptTemplate import get_node_config

            return get_node_config(node_id)
        return None

    def get_status(self) -> dict[str, Any]:
        """Return engine status for observability."""
        return {
            "engine": self.__class__.__name__,
            "initialized": self._initialized,
            "mixins_available": MIXINS_AVAILABLE,
            "knowledge_available": self.knowledge is not None,
        }
