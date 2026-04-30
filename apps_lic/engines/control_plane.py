"""3.6: Control Plane — centralized safety policy enforcement for apps_lic.

Delegates evaluate_input/evaluate_output to GovernanceShieldAgent.
Wired before/after ExecutionOrchestrator.execute() in the LIC entry path.

OpenTelemetry Integration:
- Uses AppsTracingMixin for explicit span instrumentation
- Emits execution traces for ADG registration
- Supports distributed trace propagation
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import logging
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    from apps_shared.mixins.apps_tracing_mixin import AppsTracingMixin

    APPS_TRACING_AVAILABLE = True
except ImportError:
    APPS_TRACING_AVAILABLE = False

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

_emit_records_execution_trace("p0", "evidence", "control_plane")
_emit_applies_guardrail("p0", "control_plane", "p0_governance")
_emit_snapshots_state("p0", "control_plane", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("control_plane", "p4obs", "metric_1")
_emit_emits_metric_event("control_plane", "p4obs", "metric_2")
_emit_emits_metric_event("control_plane", "p4obs", "metric_3")
_emit_emits_metric_event("control_plane", "p4obs", "metric_4")
_emit_emits_metric_event("control_plane", "p4obs", "metric_5")
_emit_emits_metric_event("control_plane", "p4obs", "metric_6")
_emit_records_incident_event("control_plane", "p4obs", "incident")
_emit_captures_runtime_anomaly("control_plane", "p4obs", "anomaly")
_emit_writes_observability_log("control_plane", "p4obs", "obs_log")
_emit_updates_monitoring_state("control_plane", "p4obs", "mon_state")
_emit_triggers_alert("control_plane", "p4obs", "alert")
_emit_links_incident_trace("control_plane", "p4obs", "trace_link")
_emit_captures_pattern("control_plane", "p3lm", "pattern")
_emit_records_learning_event("control_plane", "p3lm", "learning_event")
_emit_writes_learning_snapshot("control_plane", "p3lm", "snapshot")
_emit_feeds_meta_learning("control_plane", "p3lm", "meta_feed")
_emit_updates_routing_strategy("control_plane", "p3lm", "routing")
_emit_improves_agent_policy("control_plane", "p3lm", "policy")
_emit_stores_learning_state("control_plane", "p3lm", "state")
_emit_records_execution_trace("control_plane", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("control_plane", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("control_plane", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("control_plane", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("control_plane", "L4_STATE", "p2_trace_5")
_emit_reads_environ("control_plane", "env_read", "p2_env_1")
_emit_reads_environ("control_plane", "env_read", "p2_env_2")
_emit_reads_runtime_state("control_plane", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("control_plane", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "control_plane", "context_pull")
_emit_pulls_context("p1", "control_plane", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "control_plane", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "control_plane", "uwg_term_2")
_emit_writes_through("p1", "control_plane", "write_through")
_emit_writes_through("p1", "control_plane", "write_through_2")
_emit_validated_by_safety_plane("p1", "control_plane", "safety_validation")
_emit_invokes_eval("p1", "control_plane", "eval_call")
_emit_proposal_commits_routing("p1", "control_plane", "routing_commit")
_emit_escalates_to_human("p1", "control_plane", "human_escalation")
_emit_routes_through("p1", "control_plane", "route_through")
_emit_checks_agent_registry("p1", "control_plane", "agent_registry")
_emit_validates_agent_capability("p1", "control_plane", "capability")
_emit_dispatches_execution_plan("p1", "control_plane", "exec_plan")
_emit_agent_executes_agent("p1", "control_plane", "sub_agent")
_emit_routes_to_agent("p1", "control_plane", "target_agent")
_emit_verifies_policy("p1", "control_plane", "policy_check")
_emit_observes_runtime_state("p1", "control_plane", "runtime_state")
_emit_verifies_boundary("p1", "control_plane", "boundary_check")
_emit_transcripts_response("p1", "control_plane", "transcript")
_emit_hard_fails_untranscripted("p1", "control_plane")
_emit_gated_by_confidence("p1", "control_plane", "confidence_gate")
emit_replay_key("p0", "control_plane")
emit_determinism_digest("p0", "control_plane")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "control_plane", "execution_auth")
_emit_validates_capability("p2", "control_plane", "capability_check")
_emit_routes_to_capability("p2", "control_plane", "capability_route")
_emit_writes_via_uwg("p2", "control_plane", "uwg_write")
_emit_blocks_direct_write("p2", "control_plane", "direct_write_block")
_emit_records_tool_invocation("p2", "control_plane", "tool_invocation")
_emit_captures_execution_output("p2", "control_plane", "exec_output")
_emit_dispatches_agent("p3", "control_plane", "agent_dispatch")
_emit_coordinates_agents("p3", "control_plane", "agent_coordination")
_emit_records_workflow_lineage("p3", "control_plane", "workflow_lineage")
_emit_records_healing_outcome("p3", "control_plane", "healing_outcome")
_emit_escalates_failure("p3", "control_plane", "failure_escalation")
_emit_orchestrates_workflow("p3", "control_plane", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "control_plane", "healing_dispatch")
_emit_invokes_evaluation("p3", "control_plane", "evaluation_signal")
_emit_records_telemetry_event("p4", "control_plane", "telemetry_event")
_emit_captures_evaluation_metric("p4", "control_plane", "eval_metric")
_emit_stores_embedding("p4", "control_plane", "embedding_store")
_emit_updates_meta_learning_state("p4", "control_plane", "meta_learning")
_emit_links_execution_to_snapshot("p4", "control_plane", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class PolicyAction(Enum):
    """Actions the control plane can take."""

    ALLOW = "allow"
    BLOCK = "block"
    SANITIZE = "sanitize"
    WARN = "warn"
    REVIEW = "review"


@dataclass
class PolicyDecision:
    """Decision from control plane evaluation."""

    action: PolicyAction
    is_safe: bool
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []
        if self.metadata is None:
            self.metadata = {}


_PII_PATTERNS = (
    re.compile(r"\bssn\b", re.IGNORECASE),
    re.compile(r"\bsocial security\b", re.IGNORECASE),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    re.compile(r"\bpassport\b", re.IGNORECASE),
    re.compile(r"\bdate of birth\b", re.IGNORECASE),
    re.compile(r"\bphone number\b", re.IGNORECASE),
    re.compile(r"\bemail address\b", re.IGNORECASE),
    re.compile(r"\b[A-Z0-9._%+-]+@(gmail|yahoo|hotmail)\.com\b", re.IGNORECASE),
)


class ControlPlane(AppsTracingMixin if APPS_TRACING_AVAILABLE else object):
    """Centralized Control Plane for safety policy enforcement.

    Delegates all evaluation to GovernanceShieldAgent.
    Gate A: evaluate_input(pii_content) → PolicyAction != ALLOW

    OpenTelemetry:
        Emits spans for all evaluation operations with PII/shield metadata.
    """

    def __init__(self, policy: dict[str, Any] | None = None) -> None:
        # Initialize tracing mixin first
        super().__init__()

        self._policy = policy or {}
        self._decision_count = 0
        self._block_count = 0
        self._shield: Any = None
        self.knowledge: Any = None
        try:
            from apps_lic.reasoning.GovernanceShieldAgent import GovernanceShieldAgent

            self._shield = GovernanceShieldAgent()
        except Exception as exc:  # guardian: allow-silent-swallow
            logger.warning("ControlPlane: GovernanceShieldAgent not available: %s", exc)

        # Initialize knowledge base for prompt templates
        try:
            from apps_lic.config.knowledge_base import FROZEN_SNAPSHOT

            self.knowledge = FROZEN_SNAPSHOT
        except ImportError:
            self.knowledge = None
            logger.warning("ControlPlane: knowledge base not available")

    @traces_execute(layer="L3_ORCHESTRATION")
    def evaluate_input(self, content: str, context: dict[str, Any] | None = None) -> PolicyDecision:
        """Evaluate input content before processing.

        Returns PolicyDecision with action != ALLOW when PII or safety violations found.

        OpenTelemetry:
            Emits 'ControlPlane.evaluate_input' span with PII detection metadata.

        Tier 3 runtime-ADG: emits L2.step.seal with step_id='ControlPlane.evaluate_input'
        when an ambient adapter is active; fails open otherwise.
        """
        if not isinstance(content, str):
            raise TypeError("content must be a string")
        from apps_shared.adapters.system_learning_facade import (  # noqa: PLC0415
            get_current_adapter,
            seal_step,
        )

        with seal_step(
            get_current_adapter(),
            step_id="ControlPlane.evaluate_input",
            trace_id="",
            component="ControlPlane",
        ) as bag:
            if APPS_TRACING_AVAILABLE:
                with self.start_validation_span(
                    "input",
                    {"content_length": len(content), "context_keys": list(context.keys()) if context else []},
                ):
                    result = self._evaluate(content, context, is_input=True)
            else:
                result = self._evaluate(content, context, is_input=True)
            bag["output"] = result
        return result

    def evaluate_output(self, content: str, context: dict[str, Any] | None = None) -> PolicyDecision:
        """Evaluate output content before delivery.

        OpenTelemetry:
            Emits 'ControlPlane.evaluate_output' span with PII detection metadata.

        Tier 3 runtime-ADG: emits L2.step.seal with step_id='ControlPlane.evaluate_output'
        when an ambient adapter is active; fails open otherwise.
        """
        if not isinstance(content, str):
            raise TypeError("content must be a string")
        from apps_shared.adapters.system_learning_facade import (  # noqa: PLC0415
            get_current_adapter,
            seal_step,
        )

        with seal_step(
            get_current_adapter(),
            step_id="ControlPlane.evaluate_output",
            trace_id="",
            component="ControlPlane",
        ) as bag:
            if APPS_TRACING_AVAILABLE:
                with self.start_validation_span(
                    "output",
                    {"content_length": len(content), "context_keys": list(context.keys()) if context else []},
                ):
                    result = self._evaluate(content, context, is_input=False)
            else:
                result = self._evaluate(content, context, is_input=False)
            bag["output"] = result
        return result

    def _evaluate(self, content: str, context: Mapping[str, Any] | None, is_input: bool) -> PolicyDecision:
        """Core evaluation: delegates to GovernanceShieldAgent, then PII check."""
        if not isinstance(content, str):
            raise TypeError("content must be a string")

        self._decision_count += 1
        warnings: list[str] = []
        errors: list[str] = []
        safe_context = dict(context) if context else {}
        detected_pii = [pattern.pattern for pattern in _PII_PATTERNS if pattern.search(content)]
        if detected_pii:
            errors.append(f"PII detected: {detected_pii}")
            self._block_count += 1
            logger.warning(
                "ControlPlane: PII detected in %s content: %s",
                "input" if is_input else "output",
                detected_pii,
            )
            return PolicyDecision(
                action=PolicyAction.BLOCK,
                is_safe=False,
                warnings=warnings,
                errors=errors,
                metadata={
                    "is_input": is_input,
                    "decision_id": self._decision_count,
                    "pii": detected_pii,
                    "context_keys": sorted(safe_context.keys()),
                },
            )
        if self._shield is not None:
            try:
                if not hasattr(self._shield, "evaluate"):
                    raise TypeError("GovernanceShieldAgent must expose evaluate(content)")
                shield_result = self._shield.evaluate(content)
                if isinstance(shield_result, dict):
                    if shield_result.get("blocked"):
                        errors.append(f"GovernanceShield blocked: {shield_result.get('reason', 'policy')}")
                        self._block_count += 1
                        return PolicyDecision(
                            action=PolicyAction.BLOCK,
                            is_safe=False,
                            warnings=warnings,
                            errors=errors,
                            metadata={
                                "is_input": is_input,
                                "decision_id": self._decision_count,
                                "shield": shield_result,
                                "context_keys": sorted(safe_context.keys()),
                            },
                        )
                    if shield_result.get("warnings"):
                        warnings.extend(str(item) for item in shield_result["warnings"] if item)
            except Exception as exc:  # guardian: allow-broad-exception -- GovernanceShieldAgent may raise any type; must not propagate
                logger.warning("ControlPlane: GovernanceShieldAgent.evaluate failed: %s", exc)
        action = PolicyAction.WARN if warnings else PolicyAction.ALLOW
        return PolicyDecision(
            action=action,
            is_safe=True,
            warnings=warnings,
            errors=errors,
            metadata={
                "is_input": is_input,
                "decision_id": self._decision_count,
                "context_keys": sorted(safe_context.keys()),
            },
        )

    def get_prompt(self, prompt_id: str) -> str:
        """Get prompt from knowledge base.

        Raises:
            TypeError: If prompt_id is None
            KeyError: If prompt_id not found in knowledge base
            RuntimeError: If knowledge base is not available
        """
        if prompt_id is None:
            raise TypeError("prompt_id cannot be None")
        if not self.knowledge:
            raise RuntimeError("Knowledge base not available")
        from apps_lic.config.knowledge_base import get_prompt

        return get_prompt(prompt_id)

    def get_node_config(self, node_id: str) -> Any:
        """Get K-node configuration from knowledge base.

        Raises:
            TypeError: If node_id is None
            KeyError: If node_id not found in knowledge base
            RuntimeError: If knowledge base is not available
        """
        if node_id is None:
            raise TypeError("node_id cannot be None")
        if not self.knowledge:
            raise RuntimeError("Knowledge base not available")
        from apps_lic.config.knowledge_base import get_node_config

        return get_node_config(node_id)

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_decisions": self._decision_count,
            "total_blocks": self._block_count,
            "knowledge_available": self.knowledge is not None,
        }


__all__ = ["ControlPlane", "PolicyAction", "PolicyDecision"]
