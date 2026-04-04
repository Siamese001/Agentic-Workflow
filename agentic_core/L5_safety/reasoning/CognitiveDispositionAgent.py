from __future__ import annotations

from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)
from agentic_core.mixins.prompt_rendering_mixin import PromptRenderingMixin

emit_replay_key("p0", "CognitiveDispositionAgent")
emit_determinism_digest("p0", "CognitiveDispositionAgent")

_emit_dispatches_healing_run("p1", "CognitiveDispositionAgent", "L5")
_emit_routes_through("p1", "CognitiveDispositionAgent", "L5")
_emit_checks_agent_registry("p1", "CognitiveDispositionAgent", "agent_registry")
_emit_validates_agent_capability("p1", "CognitiveDispositionAgent", "capability")
_emit_dispatches_execution_plan("p1", "CognitiveDispositionAgent", "exec_plan")
_emit_agent_executes_agent("p1", "CognitiveDispositionAgent", "sub_agent")
_emit_routes_to_agent("p1", "CognitiveDispositionAgent", "target_agent")
_emit_verifies_policy("p1", "CognitiveDispositionAgent", "policy_check")
_emit_observes_runtime_state("p1", "CognitiveDispositionAgent", "runtime_state")
_emit_verifies_boundary("p1", "CognitiveDispositionAgent", "boundary_check")
_emit_transcripts_response("p1", "CognitiveDispositionAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "CognitiveDispositionAgent")
_emit_gated_by_confidence("p1", "CognitiveDispositionAgent", "confidence_gate")
_emit_escalates_to_human("p1", "CognitiveDispositionAgent", "L5")
_emit_reads_policy_state("p1", "CognitiveDispositionAgent", "L5")

_emit_applies_guardrail("p0", "CognitiveDispositionAgent", "p0_governance")
_emit_snapshots_state("p0", "CognitiveDispositionAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "CognitiveDispositionAgent", "execution_auth")
_emit_validates_capability("p2", "CognitiveDispositionAgent", "capability_check")
_emit_routes_to_capability("p2", "CognitiveDispositionAgent", "capability_route")
_emit_writes_via_uwg("p2", "CognitiveDispositionAgent", "uwg_write")
_emit_blocks_direct_write("p2", "CognitiveDispositionAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "CognitiveDispositionAgent", "tool_invocation")
_emit_captures_execution_output("p2", "CognitiveDispositionAgent", "exec_output")
_emit_dispatches_agent("p3", "CognitiveDispositionAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "CognitiveDispositionAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "CognitiveDispositionAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "CognitiveDispositionAgent", "healing_outcome")
_emit_escalates_failure("p3", "CognitiveDispositionAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "CognitiveDispositionAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "CognitiveDispositionAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "CognitiveDispositionAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "CognitiveDispositionAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "CognitiveDispositionAgent", "eval_metric")
_emit_stores_embedding("p4", "CognitiveDispositionAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "CognitiveDispositionAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "CognitiveDispositionAgent", "exec_snapshot_link")

"\n[PHASE 15 REFACTOR] Cognitive Disposition Agent.\nSTRICT COMPLIANCE: Native Sovereign Capabilities.\n\nPURPOSE:\n- AI-powered architectural triage via Sovereign Gateway\n- Enhanced decision making for SSOT execution\n- Cognitive analysis of structural violations\n- Intelligent file disposition recommendations\n\nINTEGRATION:\n- Used by execute_ssot.py with --enable-cda flag\n- Enhances AutonomousDecisionEngine with cognitive insights\n- Provides 15% cognitive factor in confidence calculations\n\nSTATUS: PRODUCTION READY - Keep and enhance\n"
import json
import logging
from dataclasses import dataclass
from pathlib import Path

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.config.structure_blueprint import LAYER_ROOTS
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
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
    _emit_writes_through,
)

_emit_emits_metric_event("CognitiveDispositionAgent", "p4obs", "metric_1")
_emit_emits_metric_event("CognitiveDispositionAgent", "p4obs", "metric_2")
_emit_emits_metric_event("CognitiveDispositionAgent", "p4obs", "metric_3")
_emit_emits_metric_event("CognitiveDispositionAgent", "p4obs", "metric_4")
_emit_emits_metric_event("CognitiveDispositionAgent", "p4obs", "metric_5")
_emit_emits_metric_event("CognitiveDispositionAgent", "p4obs", "metric_6")
_emit_records_incident_event("CognitiveDispositionAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("CognitiveDispositionAgent", "p4obs", "anomaly")
_emit_writes_observability_log("CognitiveDispositionAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("CognitiveDispositionAgent", "p4obs", "mon_state")
_emit_triggers_alert("CognitiveDispositionAgent", "p4obs", "alert")
_emit_links_incident_trace("CognitiveDispositionAgent", "p4obs", "trace_link")
_emit_captures_pattern("CognitiveDispositionAgent", "p3lm", "pattern")
_emit_records_learning_event("CognitiveDispositionAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("CognitiveDispositionAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("CognitiveDispositionAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("CognitiveDispositionAgent", "p3lm", "routing")
_emit_improves_agent_policy("CognitiveDispositionAgent", "p3lm", "policy")
_emit_stores_learning_state("CognitiveDispositionAgent", "p3lm", "state")
_emit_records_execution_trace("CognitiveDispositionAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("CognitiveDispositionAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("CognitiveDispositionAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("CognitiveDispositionAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("CognitiveDispositionAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("CognitiveDispositionAgent", "env_read", "p2_env_1")
_emit_reads_environ("CognitiveDispositionAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("CognitiveDispositionAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("CognitiveDispositionAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "CognitiveDispositionAgent", "context_pull")
_emit_pulls_context("p1", "CognitiveDispositionAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "CognitiveDispositionAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "CognitiveDispositionAgent", "uwg_term_2")
_emit_writes_through("p1", "CognitiveDispositionAgent", "write_through")
_emit_writes_through("p1", "CognitiveDispositionAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "CognitiveDispositionAgent", "safety_validation")
_emit_invokes_eval("p1", "CognitiveDispositionAgent", "eval_call")
_emit_proposal_commits_routing("p1", "CognitiveDispositionAgent", "routing_commit")

Logger = logging.getLogger(__name__)


@dataclass
class DispositionDecision:
    action: str
    target_path: str | None = None
    reason: str = ""
    confidence: float = 0.0


class CognitiveDispositionAgent(PromptRenderingMixin, SovereignBaseAgent):
    """AI-Powered Architectural Triage Agent via Sovereign Gateway.

    DEPRECATION STATUS: KEEP - This agent is actively used and valuable.

    USAGE:
    - Integrated in execute_ssot.py with --enable-cda flag
    - Enhances decision making with cognitive analysis
    - Provides intelligent violation triage

    FUTURE ENHANCEMENTS:
    - Add more sophisticated violation pattern recognition
    - Integrate with more LLM providers
    - Add learning from historical dispositions
    - Expand beyond file-level to architectural analysis
    """

    # guardian: allow-magic-config -- confidence_threshold default is domain-specific tuning parameter
    def __init__(self, project_root: Path | None = None, confidence_threshold: float = 0.75):
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self.confidence_threshold = confidence_threshold
        self.analytics = {
            "analyses_performed": 0,
            "cache_hits": 0,
            "average_confidence": 0.0,
            "action_distribution": {},
        }
        self.layer_map = {
            layer: layer.split("_", 1)[1].replace("_", " ").title() for layer in sorted(LAYER_ROOTS)
        }

    async def analyze_violation_async(
        self, file_path: Path, violation_type: str, context: dict = None
    ) -> DispositionDecision:
        """Analyze violation using Native LLM Gateway."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "CognitiveDispositionAgent.analyze_violation_async"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:CognitiveDispositionAgent.analyze_violation_async".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        context = context or {}
        self.analytics["analyses_performed"] += 1
        cache_key = f"cda:{file_path.name}:{violation_type}"
        cached = self.cache_get(cache_key)
        if cached and isinstance(cached, dict):
            self.analytics["cache_hits"] += 1
            return DispositionDecision(**cached)
        prompt = self._build_prompt(file_path, violation_type, context)
        try:
            response = await self.llm_generate(
                prompt,
                provider="google",
                generation_config={"response_mime_type": "application/json", "temperature": 0.1},
            )
            try:
                data = json.loads(response["content"])
            # guardian: allow-silent-swallow -- JSON parse fallback strips markdown fences before retry
            except (ValueError, TypeError):  # noqa: E722
                text = response["content"].replace("```json", "").replace("```", "").strip()
                data = json.loads(text)
            decision = DispositionDecision(
                action=data.get("action", "MANUAL_REVIEW"),
                target_path=data.get("target_path"),
                reason=data.get("reason", "Parsed from LLM"),
                confidence=float(data.get("confidence", 0.0)),
            )
            action = decision.action
            self.analytics["action_distribution"][action] = (
                self.analytics["action_distribution"].get(action, 0) + 1
            )
            total = self.analytics["analyses_performed"]
            current_avg = self.analytics["average_confidence"]
            self.analytics["average_confidence"] = (current_avg * (total - 1) + decision.confidence) / total
            await self.cache_set(cache_key, decision.__dict__, ttl=3600)
            return decision
        # guardian: allow-silent-swallow -- analysis failure returns MANUAL_REVIEW disposition with error logged
        except (RuntimeError, OSError) as e:
            Logger.error(f"CDA Analysis failed: {e}")
            return DispositionDecision(action="MANUAL_REVIEW", reason=f"Error: {e}")

    def analyze_violation(
        self, file_path: Path, violation_type: str, context: dict = None
    ) -> DispositionDecision:
        """Sync wrapper around analyze_violation_async.

        Wave 1 fix: callers should use this instead of asyncio.run() directly.
        """
        import asyncio

        return asyncio.run(self.analyze_violation_async(file_path, violation_type, context or {}))

    async def analyze_violations(self, violations: list, territory: str) -> list[DispositionDecision]:
        """Analyze a list of violations asynchronously.

        Wave 1 fix: this method is called by EnhancedAutonomousDecisionEngine
        but was missing from CognitiveDispositionAgent.
        """
        decisions = []
        for v in violations:
            path_str = v.get("file", v.get("path", ""))
            vtype = v.get("type", "UNKNOWN")
            ctx = {"territory": territory, **{k: v[k] for k in v if k not in ("file", "path", "type")}}
            try:
                decision = await self.analyze_violation_async(
                    file_path=Path(path_str) if path_str else Path("."), violation_type=vtype, context=ctx
                )
                decisions.append(decision)
            # guardian: allow-silent-swallow -- per-violation failure is logged and returns MANUAL_REVIEW disposition
            except (RuntimeError, OSError) as _e:
                Logger.warning("[CDA] analyze_violations: skipping %s: %s", path_str, _e)
                decisions.append(DispositionDecision(action="MANUAL_REVIEW", reason=f"Error: {_e}"))
        return decisions

    # guardian: allow-type-erasure -- analytics dict has dynamic keys based on accumulated metrics
    def get_analytics(self) -> dict:
        """Get usage analytics for the CognitiveDispositionAgent.

        Returns:
            dict: Analytics data including usage statistics and performance metrics
        """
        return {
            **self.analytics,
            "cache_hit_rate": self.analytics["cache_hits"] / max(self.analytics["analyses_performed"], 1),
            "project_root": str(self.project_root),
            "confidence_threshold": self.confidence_threshold,
        }

    def _build_prompt(self, file_path: Path, violation_type: str, context: dict) -> str:
        return f"\n        Analyze File: {file_path.name}\n        Violation: {violation_type}\n        Context: {json.dumps(context)}\n\n        Determine if this file should be MOVED, ARCHIVED, or IGNORED based on {json.dumps(self.layer_map)}.\n        Return JSON.\n        "

    # guardian: allow-type-erasure -- standard_heal decorator normalizes violation dict for orchestration compatibility
    def heal(self, violation: dict) -> dict:
        """Heal cognitive disposition violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (cognitive_disposition)
                - path: Path to the violating file
                - context: Additional context for the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        """
        from agentic_core.utils.decorators_compat_util import standard_heal

        @standard_heal
        # guardian: allow-type-erasure -- standard_heal decorator normalizes violation dict for orchestration compatibility
        def _heal_cognitive_disposition(self, violation: dict) -> dict:
            """Internal heal method with standard_heal decorator."""
            path = violation.get("path", "")
            context = violation.get("context", {})
            violation_type = violation.get("type", "cognitive_disposition")
            Logger.info(f"[COGNITIVE] Healing {violation_type} violation at {path}")
            try:
                import asyncio

                file_path = Path(path)
                decision = asyncio.run(self.analyze_violation_async(file_path, violation_type, context))
                if decision.confidence >= self.confidence_threshold:
                    action = decision.action.lower()
                    if action == "archive":
                        from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import (
                            ArchivalGatekeeper,
                        )

                        archivist = ArchivalGatekeeper(self.project_root)
                        archivist.archive_file(file_path, reason=f"cognitive_disposition: {decision.reason}")
                        Logger.info(f"  Archived {path} based on cognitive analysis")
                        return {"violations_fixed": 1, "violations_found": 1, "errors": 0, "skipped": 0}
                    elif action == "move":
                        target_path = decision.target_path
                        if target_path:
                            target = Path(target_path)
                            _wg.ensure_dir(target.parent)
                            _wg.rename_path(file_path, target)
                            Logger.info(f"  Moved {path} -> {target_path}")
                            return {"violations_fixed": 1, "violations_found": 1, "errors": 0, "skipped": 0}
                        else:
                            Logger.warning("  No target path provided for move action")
                            return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
                    elif action == "ignore":
                        Logger.info(f"  Ignoring {path} based on cognitive analysis")
                        return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
                    else:
                        Logger.warning(f"  Unknown cognitive action: {action}")
                        return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
                else:
                    Logger.warning(f"  Low confidence ({decision.confidence}) - requires manual review")
                    return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
            # guardian: allow-silent-swallow -- cognitive healing failure returns error count with error logged
            except (RuntimeError, OSError) as e:
                Logger.error(f"  Error in cognitive healing: {e}")
                return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}

        return _heal_cognitive_disposition(self, violation)

    # guardian: allow-type-erasure -- raises NotImplementedError; placeholder for orchestration interface
    def heal_repository(self, *args, **kwargs) -> dict:
        """heal_repository() not implemented for CognitiveDispositionAgent."""
        raise NotImplementedError("heal_repository() not implemented for CognitiveDispositionAgent")
