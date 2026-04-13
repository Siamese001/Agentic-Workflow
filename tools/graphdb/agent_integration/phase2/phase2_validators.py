"""Phase 2 Completion Gates - Validation for contextual intelligence and predictive insights."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple

from tqdm import tqdm

from ..cache import QueryCache
from ..decision_engine import AgentDecisionEngine, ArchitecturalContext
from ..guardrails import ArchitecturalGuardrails
from .collaborative_intelligence import AgentProfile, CollaborationMode, CollaborativeIntelligence
from .contextual_engine import AnalysisDepth, ContextualIntelligenceEngine
from .explanation_generator import ExplanationGenerator
from .predictive_analytics import PredictiveAnalytics

logger = logging.getLogger(__name__)


class Phase2GateStatus(Enum):
    """Status of a Phase 2 completion gate."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Phase2GateResult:
    """Result of a Phase 2 completion gate validation."""

    gate_name: str
    status: Phase2GateStatus
    score: float
    details: Dict[str, Any]
    issues: List[str]
    recommendations: List[str]
    execution_time_seconds: float = 0.0


class Phase2CompletionGates:
    """Comprehensive validation gates for Phase 2 completion."""

    def __init__(
        self,
        decision_engine: AgentDecisionEngine,
        guardrails: ArchitecturalGuardrails,
        cache: QueryCache,
    ) -> None:
        self.decision_engine = decision_engine
        self.guardrails = guardrails
        self.cache = cache

        self.contextual_engine = ContextualIntelligenceEngine(decision_engine, cache)
        self.collaborative_intelligence = CollaborativeIntelligence(self.contextual_engine)
        self.predictive_analytics = PredictiveAnalytics(self.contextual_engine)
        self.explanation_generator = ExplanationGenerator(self.contextual_engine)

        self.collaborative_intelligence.register_agent(
            AgentProfile(
                agent_id="phase2-validator",
                agent_type="validator",
                capabilities=["architecture", "risk", "analysis"],
                experience_level="expert",
                domain_expertise={"architecture": 1.0, "safety": 0.9},
            )
        )

        self.gates = {
            "contextual_intelligence": self._validate_contextual_intelligence,
            "collaborative_intelligence": self._validate_collaborative_intelligence,
            "predictive_analytics": self._validate_predictive_analytics,
            "explanation_generation": self._validate_explanation_generation,
            "cross_component_integration": self._validate_cross_component_integration,
            "performance_benchmarks": self._validate_performance_benchmarks,
        }

        logger.info("Phase2CompletionGates initialized with %d validation gates", len(self.gates))

    def run_all_gates(self) -> Dict[str, Phase2GateResult]:
        """Run all Phase 2 completion gates."""
        logger.info("Running all Phase 2 completion gates")
        results: Dict[str, Phase2GateResult] = {}
        overall_start = time.time()

        for gate_name, gate_func in tqdm(self.gates.items(), desc="gates", unit="gate"):
            logger.info("Progress: running Phase 2 gate: %s", gate_name)
            start = time.time()
            try:
                result = gate_func()
                result.execution_time_seconds = time.time() - start
                results[gate_name] = result
                logger.info("Phase 2 gate %s: %s (score: %.2f)", gate_name, result.status.value, result.score)
            except (ValueError, RuntimeError, KeyError, AttributeError, TypeError) as exc:
                logger.error("Phase 2 gate %s failed with exception: %s", gate_name, exc)
                results[gate_name] = Phase2GateResult(
                    gate_name=gate_name,
                    status=Phase2GateStatus.FAILED,
                    score=0.0,
                    details={"error": str(exc)},
                    issues=[f"Gate execution failed: {exc}"],
                    recommendations=["Fix gate implementation and retry"],
                    execution_time_seconds=time.time() - start,
                )

        logger.info("All Phase 2 gates completed in %.2f seconds", time.time() - overall_start)
        return results

    def get_overall_status(self, results: Dict[str, Phase2GateResult]) -> Tuple[Phase2GateStatus, float]:
        """Compute overall status and mean score from all gate results."""
        if not results:
            return Phase2GateStatus.PENDING, 0.0

        scores = [r.score for r in results.values()]
        overall_score = sum(scores) / len(scores)

        terminal_bad = {Phase2GateStatus.FAILED, Phase2GateStatus.BLOCKED}
        if any(r.status in terminal_bad for r in results.values()):
            return Phase2GateStatus.FAILED, overall_score
        if any(r.status == Phase2GateStatus.PENDING for r in results.values()):
            return Phase2GateStatus.PENDING, overall_score
        if any(r.status == Phase2GateStatus.IN_PROGRESS for r in results.values()):
            return Phase2GateStatus.IN_PROGRESS, overall_score
        return Phase2GateStatus.PASSED, overall_score

    def _make_test_context(self) -> ArchitecturalContext:
        return ArchitecturalContext(
            agent_type="test",
            action_type="analyze_code",
            target_modules=["test_module"],
            proposed_changes={"type": "test"},
            session_id="phase2_validation",
        )

    def _validate_contextual_intelligence(self) -> Phase2GateResult:
        issues: List[str] = []
        recommendations: List[str] = []
        score = 1.0

        try:
            result = self.contextual_engine.analyze_with_context(self._make_test_context())

            if not hasattr(result, "base_result"):
                issues.append("Missing base_result in contextual analysis output")
                score -= 0.25
            if not hasattr(result, "contextual_insights"):
                issues.append("Missing contextual_insights in contextual analysis output")
                score -= 0.25
            if result.analysis_depth not in set(AnalysisDepth):
                issues.append("Analysis depth is not a valid AnalysisDepth enum")
                score -= 0.2
            if result.confidence_score < 0.0 or result.confidence_score > 1.0:
                issues.append("Confidence score must be normalized to [0.0, 1.0]")
                score -= 0.15

        except (ValueError, RuntimeError, KeyError, AttributeError, TypeError) as exc:
            issues.append(f"Contextual intelligence test failed: {exc}")
            recommendations.append("Fix contextual analysis result assembly")
            score -= 0.5

        return Phase2GateResult(
            gate_name="contextual_intelligence",
            status=Phase2GateStatus.PASSED if score >= 0.8 else Phase2GateStatus.FAILED,
            score=max(score, 0.0),
            details={"test_completed": True},
            issues=issues,
            recommendations=recommendations,
        )

    def _validate_collaborative_intelligence(self) -> Phase2GateResult:
        issues: List[str] = []
        recommendations: List[str] = []
        score = 1.0

        try:
            result = self.collaborative_intelligence.analyze_collaboratively(
                self._make_test_context(),
                requesting_agent="phase2-validator",
                collaboration_mode=CollaborationMode.INDEPENDENT,
            )

            if "phase2-validator" not in result.participating_agents:
                issues.append("Requesting agent missing from participating_agents")
                score -= 0.2
            if not isinstance(result.collaborative_insights, list):
                issues.append("collaborative_insights should be a list")
                score -= 0.2
            if result.confidence_boost < 0.0:
                issues.append("confidence_boost should not be negative")
                score -= 0.1

        except (ValueError, RuntimeError, KeyError, AttributeError, TypeError) as exc:
            issues.append(f"Collaborative intelligence test failed: {exc}")
            recommendations.append("Fix collaboration orchestration and result normalization")
            score -= 0.5

        return Phase2GateResult(
            gate_name="collaborative_intelligence",
            status=Phase2GateStatus.PASSED if score >= 0.8 else Phase2GateStatus.FAILED,
            score=max(score, 0.0),
            details={"test_completed": True},
            issues=issues,
            recommendations=recommendations,
        )

    def _validate_predictive_analytics(self) -> Phase2GateResult:
        issues: List[str] = []
        recommendations: List[str] = []
        score = 1.0

        try:
            result = self.predictive_analytics.analyze_impact(self._make_test_context())

            if not isinstance(result.affected_modules, list):
                issues.append("affected_modules should be a list")
                score -= 0.2
            if not isinstance(result.blast_radius, int):
                issues.append("blast_radius should be an integer")
                score -= 0.2
            if not hasattr(result.risk_level, "value"):
                issues.append("risk_level should be an enum-like object")
                score -= 0.15
            if not isinstance(result.ecosystem_implications, dict):
                issues.append("ecosystem_implications should be a dictionary")
                score -= 0.15

        except (ValueError, RuntimeError, KeyError, AttributeError, TypeError) as exc:
            issues.append(f"Predictive analytics test failed: {exc}")
            recommendations.append("Fix impact prediction result generation")
            score -= 0.5

        return Phase2GateResult(
            gate_name="predictive_analytics",
            status=Phase2GateStatus.PASSED if score >= 0.8 else Phase2GateStatus.FAILED,
            score=max(score, 0.0),
            details={"test_completed": True},
            issues=issues,
            recommendations=recommendations,
        )

    def _validate_explanation_generation(self) -> Phase2GateResult:
        issues: List[str] = []
        recommendations: List[str] = []
        score = 1.0

        try:
            context = self._make_test_context()
            decision = self.decision_engine.analyze_action(context)
            explanation = self.explanation_generator.explain_decision(context, decision)

            if not hasattr(explanation, "components"):
                issues.append("Explanation missing components")
                score -= 0.25
            if not hasattr(explanation, "summary"):
                issues.append("Explanation missing summary")
                score -= 0.2
            if not isinstance(explanation.components, list) or not explanation.components:
                issues.append("Explanation should include at least one component")
                score -= 0.2

        except (ValueError, RuntimeError, KeyError, AttributeError, TypeError) as exc:
            issues.append(f"Explanation generation test failed: {exc}")
            recommendations.append("Fix explanation builder and component rendering")
            score -= 0.5

        return Phase2GateResult(
            gate_name="explanation_generation",
            status=Phase2GateStatus.PASSED if score >= 0.8 else Phase2GateStatus.FAILED,
            score=max(score, 0.0),
            details={"test_completed": True},
            issues=issues,
            recommendations=recommendations,
        )

    def _validate_cross_component_integration(self) -> Phase2GateResult:
        issues: List[str] = []
        recommendations: List[str] = []
        score = 1.0

        try:
            context = self._make_test_context()
            analysis = self.contextual_engine.analyze_with_context(context)
            prediction = self.predictive_analytics.analyze_impact(context)
            explanation = self.explanation_generator.explain_decision(context, analysis.base_result)

            if analysis.base_result.risk_level != prediction.risk_level:
                issues.append("Prediction risk_level drifted from base contextual analysis")
                score -= 0.2
            if not explanation.summary:
                issues.append("Integrated explanation should generate a summary")
                score -= 0.15
            if not analysis.contextual_insights:
                issues.append("Integrated contextual analysis produced no insights")
                score -= 0.15

        except (ValueError, RuntimeError, KeyError, AttributeError, TypeError) as exc:
            issues.append(f"Cross-component integration test failed: {exc}")
            recommendations.append("Fix data contracts between Phase 2 components")
            score -= 0.5

        return Phase2GateResult(
            gate_name="cross_component_integration",
            status=Phase2GateStatus.PASSED if score >= 0.8 else Phase2GateStatus.FAILED,
            score=max(score, 0.0),
            details={"test_completed": True},
            issues=issues,
            recommendations=recommendations,
        )

    def _validate_performance_benchmarks(self) -> Phase2GateResult:
        issues: List[str] = []
        recommendations: List[str] = []
        score = 1.0

        try:
            context = self._make_test_context()
            start = time.time()
            analysis = self.contextual_engine.analyze_with_context(context)
            elapsed = time.time() - start

            if elapsed > 2.0:
                issues.append(f"Contextual analysis exceeded benchmark: {elapsed:.3f}s > 2.000s")
                score -= 0.3
            if analysis.execution_time_seconds < 0.0:
                issues.append("Reported execution_time_seconds must be non-negative")
                score -= 0.2

        except (ValueError, RuntimeError, KeyError, AttributeError, TypeError) as exc:
            issues.append(f"Performance benchmark test failed: {exc}")
            recommendations.append("Profile contextual analysis hot paths and cache misses")
            score -= 0.5

        return Phase2GateResult(
            gate_name="performance_benchmarks",
            status=Phase2GateStatus.PASSED if score >= 0.8 else Phase2GateStatus.FAILED,
            score=max(score, 0.0),
            details={"test_completed": True},
            issues=issues,
            recommendations=recommendations,
        )
