from __future__ import annotations

import logging
import uuid
from typing import Any

from agentic_core.L1_cognition.planning.capability_analyzer_types import (
    AnalysisReport,
    CapabilityGap,
    CapabilityGapType,
    Recommendation,
    RecommendationType,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,
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

from agentic_core.runtime.lifecycle_trace_contract import (
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

LOGGER = logging.getLogger(__name__)
Logger: Any = logging.getLogger(__name__)


def _get_reason_and_record():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_reason_and_record", "state_snapshot")
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_reason_and_record", "p0_governance")
    from agentic_core.L1_cognition.enforcement.reasoning_chokepoint import reason_and_record  # noqa: PLC0415

    return reason_and_record


def _invoke_reason_and_record(ctx, prompt, retrieved, fn, **kw):
    from agentic_core.L1_cognition.enforcement.reasoning_chokepoint import reason_and_record  # noqa: PLC0415

    return reason_and_record(ctx, prompt, retrieved, fn, **kw)


def _make_reasoning_context(run_id: str, policy_hash: str, prompt: str, model_id: str, clock_tick: float):
    from agentic_core.L1_cognition.context.reasoning_context_builder import (
        build_reasoning_context,  # noqa: PLC0415
    )

    return build_reasoning_context(
        run_id=run_id,
        trace_id=str(uuid.uuid4()),
        policy_context=policy_hash or "default",
        prompt=prompt,
        model_id=model_id or "capability_analyzer",
    )


class CapabilityAnalyzer:
    """Analyzes capability gaps and generates improvement recommendations.

    Features:
    - Failure pattern analysis
    - Capability gap identification
    - Tool/sub-agent recommendations
    - Retraining suggestions
    - Impact estimation
    """

    def __init__(self, enable_logging: bool = True):
        """Initialize capability analyzer.

        Args:
            enable_logging: Enable logging
        """
        self.enable_logging = enable_logging
        self._gap_history: dict[str, list[CapabilityGap]] = {}
        self._recommendation_history: dict[str, list[Recommendation]] = {}
        if self.enable_logging:
            LOGGER.info("capability_analyzer_initialized")

    def analyze_failures(self, agent_id: str, failure_reports: list[dict[str, Any]]) -> list[CapabilityGap]:
        """Analyze failure reports to identify capability gaps.

        Args:
            agent_id: Agent identifier
            failure_reports: List of failure reports

        Returns:
            List of identified capability gaps
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "CapabilityAnalyzer.analyze_failures"
        )

        gaps: list[CapabilityGap] = []
        failure_patterns: Any = self._identify_failure_patterns(failure_reports)
        for pattern_type, pattern_failures in failure_patterns.items():
            gap: Any = self._create_gap_from_pattern(
                agent_id=agent_id, pattern_type=pattern_type, failures=pattern_failures
            )
            if gap:
                gaps.append(gap)
        if agent_id not in self._gap_history:
            self._gap_history[agent_id] = []
        self._gap_history[agent_id].extend(gaps)
        if self.enable_logging:
            LOGGER.info("capability_gaps_identified", EXTRA={"agent_id": agent_id, "gap_count": len(gaps)})
        return gaps

    def generate_recommendations(self, agent_id: str, gaps: list[CapabilityGap]) -> list[Recommendation]:
        """Generate improvement recommendations for capability gaps.

        Args:
            agent_id: Agent identifier
            gaps: Identified capability gaps

        Returns:
            List of recommendations
        """
        recommendations: list[Recommendation] = []
        for gap in gaps:
            recs: Any = self._generate_recommendations_for_gap(gap)
            recommendations.extend(recs)
        recommendations.sort(key=lambda r: r.priority, reverse=True)
        if agent_id not in self._recommendation_history:
            self._recommendation_history[agent_id] = []
        self._recommendation_history[agent_id].extend(recommendations)
        if self.enable_logging:
            LOGGER.info(
                "recommendations_generated",
                EXTRA={"agent_id": agent_id, "recommendation_count": len(recommendations)},
            )
        return recommendations

    def create_analysis_report(self, agent_id: str, failure_reports: list[dict[str, Any]]) -> AnalysisReport:
        """Create complete capability gap analysis report.

        Args:
            agent_id: Agent identifier
            failure_reports: List of failure reports

        Returns:
            AnalysisReport
        """
        _clk = get_clock().now_epoch()
        _rctx = _make_reasoning_context(
            run_id=f"{agent_id}:{int(_clk)}",
            policy_hash="default",
            prompt=str(failure_reports)[:256],
            model_id="capability_analyzer",
            clock_tick=_clk,
        )
        _, _trace = _invoke_reason_and_record(
            _rctx,
            failure_reports,
            {},
            lambda p, c: p,
        )
        gaps: Any = self.analyze_failures(agent_id, failure_reports)
        recommendations: Any = self.generate_recommendations(agent_id, gaps)
        health_score: Any = self._calculate_health_score(gaps)
        report: Any = AnalysisReport(
            report_id=f"analysis_{agent_id}_{int(get_clock().now_epoch())}",
            agent_id=agent_id,
            gaps_identified=gaps,
            recommendations=recommendations,
            overall_health_score=health_score,
            analysis_timestamp=get_clock().now_epoch(),
        )
        return report

    def _identify_failure_patterns(
        self, failure_reports: list[dict[str, Any]]
    ) -> dict[str, list[dict[str, Any]]]:
        """Identify common failure patterns.

        Args:
            failure_reports: List of failure reports

        Returns:
            Dict mapping pattern type to failures
        """
        patterns: dict[str, list[dict[str, Any]]] = {}
        for report in failure_reports:
            error_type = report.get("error_type", "unknown")
            if "tool" in error_type.lower() or "not found" in error_type.lower():
                pattern_type = "missing_tool"
            elif "knowledge" in error_type.lower() or "unknown" in error_type.lower():
                pattern_type = "insufficient_knowledge"
            elif "timeout" in error_type.lower() or "slow" in error_type.lower():
                pattern_type = "performance"
            elif "reasoning" in error_type.lower() or "logic" in error_type.lower():
                pattern_type = "reasoning"
            else:
                pattern_type = "integration"
            if pattern_type not in patterns:
                patterns[pattern_type] = []
            patterns[pattern_type].append(report)
        return patterns

    def _create_gap_from_pattern(
        self, agent_id: str, pattern_type: str, failures: list[dict[str, Any]]
    ) -> CapabilityGap | None:
        """Create capability gap from failure pattern.

        Args:
            agent_id: Agent identifier
            pattern_type: Pattern type
            failures: Failures matching pattern

        Returns:
            CapabilityGap or None
        """
        if not failures:
            return None
        gap_type_map = {
            "missing_tool": CapabilityGapType.MISSING_TOOL,
            "insufficient_knowledge": CapabilityGapType.INSUFFICIENT_KNOWLEDGE,
            "performance": CapabilityGapType.PERFORMANCE_DEGRADATION,
            "reasoning": CapabilityGapType.REASONING_LIMITATION,
            "integration": CapabilityGapType.INTEGRATION_FAILURE,
        }
        GapType = gap_type_map.get(pattern_type, CapabilityGapType.INTEGRATION_FAILURE)
        scenarios = list({f.get("scenario_id", "unknown") for f in failures})
        Severity = min(len(failures) / 10.0, 1.0)
        evidence = [f.get("error_message", "") for f in failures[:5]]
        gap = CapabilityGap(
            gap_id=f"gap_{agent_id}_{pattern_type}_{int(get_clock().now_epoch())}",
            GapType=GapType,
            description=f"{pattern_type.replace('_', ' ').title()} detected in {len(failures)} cases",
            affected_scenarios=scenarios,
            failure_count=len(failures),
            Severity=Severity,
            evidence=evidence,
        )
        return gap

    def _generate_recommendations_for_gap(self, gap: CapabilityGap) -> list[Recommendation]:
        """Generate recommendations for a specific gap.

        Args:
            gap: Capability gap

        Returns:
            List of recommendations
        """
        recommendations: list[Recommendation] = []
        if gap.GapType == CapabilityGapType.MISSING_TOOL:
            rec = Recommendation(
                recommendation_id=f"rec_{gap.gap_id}_add_tool",
                RecommendationType=RecommendationType.ADD_TOOL,
                title="Add Missing Tool",
                description=f"Add tool to handle scenarios: {', '.join(gap.affected_scenarios[:3])}",
                addresses_gaps=[gap.gap_id],
                priority=gap.Severity,
                implementation_steps=[
                    "Identify required tool functionality",
                    "Search tool registry or implement custom tool",
                    "Integrate tool with action plane",
                    "Test in Agent Gym",
                ],
                estimated_impact=0.8,
            )
            recommendations.append(rec)
        elif gap.GapType == CapabilityGapType.INSUFFICIENT_KNOWLEDGE:
            rec = Recommendation(
                recommendation_id=f"rec_{gap.gap_id}_update_knowledge",
                RecommendationType=RecommendationType.UPDATE_KNOWLEDGE,
                title="# SQL removed: Update Knowledge Base",
                description="Enhance knowledge base with Missing information",
                addresses_gaps=[gap.gap_id],
                priority=gap.Severity * 0.8,
                implementation_steps=[
                    "Identify knowledge gaps from failures",
                    "Source authoritative information",
                    "# SQL removed: Update RAG knowledge base",
                    "Validate with golden datasets",
                ],
                estimated_impact=0.7,
            )
            recommendations.append(rec)
        elif gap.GapType == CapabilityGapType.PERFORMANCE_DEGRADATION:
            rec = Recommendation(
                recommendation_id=f"rec_{gap.gap_id}_optimize",
                RecommendationType=RecommendationType.OPTIMIZE_PERFORMANCE,
                title="Optimize Performance",
                description="Improve response time and resource usage",
                addresses_gaps=[gap.gap_id],
                priority=gap.Severity * 0.7,
                implementation_steps=[
                    "Profile execution bottlenecks",
                    "Optimize slow operations",
                    "Add caching where appropriate",
                    "Consider model routing for efficiency",
                ],
                estimated_impact=0.6,
            )
            recommendations.append(rec)
        elif gap.GapType == CapabilityGapType.REASONING_LIMITATION:
            rec = Recommendation(
                recommendation_id=f"rec_{gap.gap_id}_retrain",
                RecommendationType=RecommendationType.RETRAIN_AGENT,
                title="Retrain Agent in Gym",
                description="Improve reasoning capabilities through training",
                addresses_gaps=[gap.gap_id],
                priority=gap.Severity * 0.9,
                implementation_steps=[
                    "Create adversarial scenarios in Agent Gym",
                    "Run training sessions",
                    "Analyze performance improvements",
                    "Deploy if improvements validated",
                ],
                estimated_impact=0.75,
            )
            recommendations.append(rec)
        return recommendations

    def _calculate_health_score(self, gaps: list[CapabilityGap]) -> float:
        """Calculate overall health score.

        Args:
            gaps: List of capability gaps

        Returns:
            Health score (0.0-1.0)
        """
        if not gaps:
            return 1.0
        total_severity = sum(g.Severity for g in gaps)
        avg_severity = total_severity / len(gaps)
        health_score = 1.0 - min(avg_severity, 1.0)
        return health_score


def create_capability_analyzer() -> CapabilityAnalyzer:
    """Factory function to create capability analyzer.

    Returns:
        CapabilityAnalyzer instance
    """
    return CapabilityAnalyzer()
