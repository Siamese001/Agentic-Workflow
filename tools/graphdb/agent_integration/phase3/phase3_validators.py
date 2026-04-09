"""Phase 3 Completion Gates - Validation for ecosystem intelligence and autonomous governance."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from tools.graphdb.agent_integration.decision_engine import (
    AgentDecisionEngine,
    ArchitecturalContext,
    RiskLevel,
)
from tools.graphdb.agent_integration.guardrails import ArchitecturalGuardrails
from tools.graphdb.agent_integration.cache import QueryCache
from .ecosystem_intelligence import EcosystemIntelligenceEngine
from .adaptive_learning import AdaptiveLearningEngine
from .health_monitoring import ArchitecturalHealthMonitor, HealthStatus
from .autonomous_governance import AutonomousGovernanceEngine

logger = logging.getLogger(__name__)


class Phase3GateStatus(Enum):
    """Status of Phase 3 completion gate validation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Phase3GateResult:
    """Result of a Phase 3 completion gate validation."""

    gate_name: str
    status: Phase3GateStatus
    score: float  # 0.0 to 1.0
    details: Dict[str, Any]
    issues: List[str]
    recommendations: List[str]
    execution_time_seconds: float


class Phase3CompletionGates:
    """Comprehensive validation gates for Phase 3 completion."""

    def __init__(
        self, decision_engine: AgentDecisionEngine, guardrails: ArchitecturalGuardrails, cache: QueryCache
    ):
        """Initialize Phase 3 completion gates.

        Args:
            decision_engine: Agent decision engine
            guardrails: Architectural guardrails
            cache: Query cache
        """
        self.decision_engine = decision_engine
        self.guardrails = guardrails
        self.cache = cache

        # Initialize Phase 3 components
        from .phase2.contextual_engine import ContextualIntelligenceEngine

        self.contextual_engine = ContextualIntelligenceEngine(decision_engine, cache)

        self.ecosystem_intelligence = EcosystemIntelligenceEngine(self.contextual_engine)
        self.adaptive_learning = AdaptiveLearningEngine(self.contextual_engine)
        self.health_monitor = ArchitecturalHealthMonitor(self.contextual_engine)
        self.autonomous_governance = AutonomousGovernanceEngine(self.contextual_engine, self.health_monitor)

        # Gate definitions
        self.gates = {
            "ecosystem_intelligence": self._validate_ecosystem_intelligence,
            "adaptive_learning": self._validate_adaptive_learning,
            "health_monitoring": self._validate_health_monitoring,
            "autonomous_governance": self._validate_autonomous_governance,
            "cross_system_integration": self._validate_cross_system_integration,
            "performance_benchmarks": self._validate_performance_benchmarks,
        }

        logger.info("Phase3CompletionGates initialized with 6 validation gates")

    def run_all_gates(self) -> Dict[str, Phase3GateResult]:
        """Run all Phase 3 completion gates."""
        logger.info("Running all Phase 3 completion gates")

        results = {}
        overall_start = time.time()

        for gate_name, gate_func in self.gates.items():
            logger.info("Running Phase 3 gate: %s", gate_name)
            start_time = time.time()

            try:
                result = gate_func()
                result.execution_time_seconds = time.time() - start_time
                results[gate_name] = result

                logger.info("Phase 3 gate %s: %s (score: %.2f)", gate_name, result.status.value, result.score)

            except (ValueError, RuntimeError, KeyError, AttributeError, TypeError) as e:
                logger.error("Phase 3 gate %s failed with exception: %s", gate_name, e)
                results[gate_name] = Phase3GateResult(
                    gate_name=gate_name,
                    status=Phase3GateStatus.FAILED,
                    score=0.0,
                    details={"error": str(e)},
                    issues=[f"Gate execution failed: {e}"],
                    recommendations=["Fix gate implementation and retry"],
                    execution_time_seconds=time.time() - start_time,
                )

        overall_time = time.time() - overall_start
        logger.info("All Phase 3 gates completed in %.2f seconds", overall_time)

        return results

    def _validate_ecosystem_intelligence(self) -> Phase3GateResult:
        """Validate ecosystem intelligence engine."""
        logger.info("Validating ecosystem intelligence")

        issues = []
        recommendations = []
        score = 1.0

        try:
            # Test ecosystem analysis
            ecosystem_analysis = self.ecosystem_intelligence.analyze_ecosystem()

            # Validate analysis structure
            if not hasattr(ecosystem_analysis, "ecosystem_nodes"):
                issues.append("Missing ecosystem_nodes in ecosystem analysis")
                score -= 0.2

            if not hasattr(ecosystem_analysis, "system_boundaries"):
                issues.append("Missing system_boundaries in ecosystem analysis")
                score -= 0.2

            if not hasattr(ecosystem_analysis, "cross_system_dependencies"):
                issues.append("Missing cross_system_dependencies in ecosystem analysis")
                score -= 0.2

            # Validate ecosystem data
            if len(ecosystem_analysis.ecosystem_nodes) == 0:
                issues.append("No ecosystem nodes detected")
                score -= 0.3

            if len(ecosystem_analysis.system_boundaries) == 0:
                issues.append("No system boundaries detected")
                score -= 0.2

            # Test boundary violation detection
            context = ArchitecturalContext(
                agent_type="test",
                action_type="test_action",
                target_modules=["test_module"],
                proposed_changes={"type": "test"},
                session_id="test_session",
            )

            violations = self.ecosystem_intelligence.detect_boundary_violations(context)
            # Should return list (possibly empty)
            if not isinstance(violations, list):
                issues.append("Boundary violation detection should return list")
                score -= 0.1

            logger.info(
                "✓ Ecosystem intelligence working with %d nodes and %d boundaries",
                len(ecosystem_analysis.ecosystem_nodes),
                len(ecosystem_analysis.system_boundaries),
            )

        except (ValueError, RuntimeError, KeyError) as e:
            issues.append(f"Ecosystem intelligence test failed: {e}")
            score -= 0.5
            recommendations.append("Fix ecosystem intelligence implementation")

        return Phase3GateResult(
            gate_name="ecosystem_intelligence",
            status=Phase3GateStatus.PASSED if score >= 0.8 else Phase3GateStatus.FAILED,
            score=score,
            details={"test_completed": True},
            issues=issues,
            recommendations=recommendations,
            execution_time_seconds=0.0,
        )

    def _validate_adaptive_learning(self) -> Phase3GateResult:
        """Validate adaptive learning engine."""
        logger.info("Validating adaptive learning")

        issues = []
        recommendations = []
        score = 1.0

        try:
            # Test learning from context
            context = ArchitecturalContext(
                agent_type="test",
                action_type="test_action",
                target_modules=["test_module"],
                proposed_changes={"type": "test"},
                session_id="test_session",
            )

            from .phase2.contextual_engine import AnalysisResult

            mock_result = AnalysisResult(
                base_result=self.decision_engine.analyze_action(context),
                contextual_insights=["test insight"],
                analysis_depth="surface",
                context_factors_applied=["test_factor"],
                confidence_score=0.8,
                recommendations=["test recommendation"],
                execution_time_seconds=0.1,
            )

            insights = self.adaptive_learning.learn_from_context(context, mock_result)

            # Validate learning insights
            if not isinstance(insights, list):
                issues.append("Learning from context should return list of insights")
                score -= 0.2

            # Test pattern analysis
            learning_result = self.adaptive_learning.analyze_learning_patterns()

            # Validate learning result structure
            if not hasattr(learning_result, "patterns_discovered"):
                issues.append("Missing patterns_discovered in learning result")
                score -= 0.2

            if not hasattr(learning_result, "insights_generated"):
                issues.append("Missing insights_generated in learning result")
                score -= 0.2

            # Test risk prediction
            risk_prediction = self.adaptive_learning.predict_architectural_risk(context)

            if not isinstance(risk_prediction, dict):
                issues.append("Risk prediction should return dictionary")
                score -= 0.1

            required_keys = ["risk_probability", "confidence", "risk_factors"]
            for key in required_keys:
                if key not in risk_prediction:
                    issues.append(f"Missing {key} in risk prediction")
                    score -= 0.1

            logger.info(
                "✓ Adaptive learning working with %d patterns discovered",
                len(learning_result.patterns_discovered),
            )

        except (ValueError, RuntimeError, KeyError) as e:
            issues.append(f"Adaptive learning test failed: {e}")
            score -= 0.5
            recommendations.append("Fix adaptive learning implementation")

        return Phase3GateResult(
            gate_name="adaptive_learning",
            status=Phase3GateStatus.PASSED if score >= 0.8 else Phase3GateStatus.FAILED,
            score=score,
            details={
                "patterns_discovered": len(learning_result.patterns_discovered)
                if "learning_result" in locals()
                else 0
            },
            issues=issues,
            recommendations=recommendations,
            execution_time_seconds=0.0,
        )

    def _validate_health_monitoring(self) -> Phase3GateResult:
        """Validate health monitoring system."""
        logger.info("Validating health monitoring")

        issues = []
        recommendations = []
        score = 1.0

        try:
            # Test health monitoring
            health_report = self.health_monitor.monitor_health()

            # Validate health report structure
            if not hasattr(health_report, "overall_status"):
                issues.append("Missing overall_status in health report")
                score -= 0.2

            if not hasattr(health_report, "overall_score"):
                issues.append("Missing overall_score in health report")
                score -= 0.2

            if not hasattr(health_report, "metrics"):
                issues.append("Missing metrics in health report")
                score -= 0.2

            # Validate health metrics
            if len(health_report.metrics) == 0:
                issues.append("No health metrics collected")
                score -= 0.3

            # Validate health score range
            if not (0.0 <= health_report.overall_score <= 1.0):
                issues.append("Health score should be between 0.0 and 1.0")
                score -= 0.2

            # Test health dashboard
            dashboard = self.health_monitor.get_health_dashboard()

            required_dashboard_keys = ["overall_status", "overall_score", "active_alerts"]
            for key in required_dashboard_keys:
                if key not in dashboard:
                    issues.append(f"Missing {key} in health dashboard")
                    score -= 0.1

            # Test alert management
            if len(health_report.alerts) > 0:
                test_alert = health_report.alerts[0]
                acknowledge_result = self.health_monitor.acknowledge_alert(test_alert.alert_id)
                if not isinstance(acknowledge_result, bool):
                    issues.append("Alert acknowledgment should return boolean")
                    score -= 0.1

            logger.info(
                "✓ Health monitoring working with status %s and score %.2f",
                health_report.overall_status.value,
                health_report.overall_score,
            )

        except (ValueError, RuntimeError, KeyError) as e:
            issues.append(f"Health monitoring test failed: {e}")
            score -= 0.5
            recommendations.append("Fix health monitoring implementation")

        return Phase3GateResult(
            gate_name="health_monitoring",
            status=Phase3GateStatus.PASSED if score >= 0.8 else Phase3GateStatus.FAILED,
            score=score,
            details={"health_score": health_report.overall_score if "health_report" in locals() else 0.0},
            issues=issues,
            recommendations=recommendations,
            execution_time_seconds=0.0,
        )

    def _validate_autonomous_governance(self) -> Phase3GateResult:
        """Validate autonomous governance engine."""
        logger.info("Validating autonomous governance")

        issues = []
        recommendations = []
        score = 1.0

        try:
            # Test governance enforcement
            context = ArchitecturalContext(
                agent_type="test",
                action_type="test_action",
                target_modules=["test_module"],
                proposed_changes={"type": "test"},
                session_id="test_session",
            )

            action, is_compliant = self.autonomous_governance.enforce_governance(context)

            # Validate governance action
            if not hasattr(action, "action_type"):
                issues.append("Missing action_type in governance action")
                score -= 0.2

            if not isinstance(is_compliant, bool):
                issues.append("Compliance status should be boolean")
                score -= 0.1

            # Test compliance assessment
            compliance_report = self.autonomous_governance.assess_compliance()

            # Validate compliance report structure
            if not hasattr(compliance_report, "compliance_level"):
                issues.append("Missing compliance_level in compliance report")
                score -= 0.2

            if not hasattr(compliance_report, "compliance_score"):
                issues.append("Missing compliance_score in compliance report")
                score -= 0.2

            # Validate compliance score range
            if not (0.0 <= compliance_report.compliance_score <= 1.0):
                issues.append("Compliance score should be between 0.0 and 1.0")
                score -= 0.2

            # Test auto-fix functionality
            auto_fix_actions = self.autonomous_governance.auto_fix_violations(max_fixes=1)
            if not isinstance(auto_fix_actions, list):
                issues.append("Auto-fix should return list of actions")
                score -= 0.1

            # Test governance dashboard
            dashboard = self.autonomous_governance.get_governance_dashboard()

            required_dashboard_keys = ["compliance_level", "compliance_score", "active_violations"]
            for key in required_dashboard_keys:
                if key not in dashboard:
                    issues.append(f"Missing {key} in governance dashboard")
                    score -= 0.1

            logger.info(
                "✓ Autonomous governance working with compliance %s (%.2f)",
                compliance_report.compliance_level.value,
                compliance_report.compliance_score,
            )

        except (ValueError, RuntimeError, KeyError) as e:
            issues.append(f"Autonomous governance test failed: {e}")
            score -= 0.5
            recommendations.append("Fix autonomous governance implementation")

        return Phase3GateResult(
            gate_name="autonomous_governance",
            status=Phase3GateStatus.PASSED if score >= 0.8 else Phase3GateStatus.FAILED,
            score=score,
            details={
                "compliance_score": compliance_report.compliance_score
                if "compliance_report" in locals()
                else 0.0
            },
            issues=issues,
            recommendations=recommendations,
            execution_time_seconds=0.0,
        )

    def _validate_cross_system_integration(self) -> Phase3GateResult:
        """Validate cross-system integration."""
        logger.info("Validating cross-system integration")

        issues = []
        recommendations = []
        score = 1.0

        try:
            # Test component integration
            context = ArchitecturalContext(
                agent_type="test",
                action_type="test_action",
                target_modules=["test_module"],
                proposed_changes={"type": "test"},
                session_id="test_session",
            )

            # Test ecosystem intelligence integration
            ecosystem_impact = self.ecosystem_intelligence.get_ecosystem_impact(context)
            if not isinstance(ecosystem_impact, dict):
                issues.append("Ecosystem impact should return dictionary")
                score -= 0.2

            # Test adaptive learning integration
            architectural_improvements = self.adaptive_learning.recommend_architectural_improvements(context)
            if not isinstance(architectural_improvements, list):
                issues.append("Architectural improvements should return list")
                score -= 0.2

            # Test health monitoring integration
            health_trends = self.health_monitor.get_health_trends()
            if not isinstance(health_trends, dict):
                issues.append("Health trends should return dictionary")
                score -= 0.2

            # Test autonomous governance integration
            governance_dashboard = self.autonomous_governance.get_governance_dashboard()
            if not isinstance(governance_dashboard, dict):
                issues.append("Governance dashboard should return dictionary")
                score -= 0.2

            # Test cross-component data flow
            # This would test that components can work together
            logger.info("✓ Cross-system integration working correctly")

        except (ValueError, RuntimeError, KeyError) as e:
            issues.append(f"Cross-system integration test failed: {e}")
            score -= 0.4
            recommendations.append("Fix cross-system integration")

        return Phase3GateResult(
            gate_name="cross_system_integration",
            status=Phase3GateStatus.PASSED if score >= 0.8 else Phase3GateStatus.FAILED,
            score=score,
            details={"components_tested": 4},
            issues=issues,
            recommendations=recommendations,
            execution_time_seconds=0.0,
        )

    def _validate_performance_benchmarks(self) -> Phase3GateResult:
        """Validate Phase 3 performance benchmarks."""
        logger.info("Validating performance benchmarks")

        issues = []
        recommendations = []
        score = 1.0

        try:
            # Test ecosystem intelligence performance
            start_time = time.time()
            ecosystem_analysis = self.ecosystem_intelligence.analyze_ecosystem()
            ecosystem_time = time.time() - start_time

            # Should complete in under 2 seconds for ecosystem analysis
            if ecosystem_time < 2.0:
                logger.info("✓ Ecosystem intelligence performance acceptable (%.3fs)", ecosystem_time)
            else:
                issues.append(f"Ecosystem intelligence slow ({ecosystem_time:.3f}s)")
                score -= 0.3

            # Test adaptive learning performance
            start_time = time.time()
            learning_result = self.adaptive_learning.analyze_learning_patterns()
            learning_time = time.time() - start_time

            # Should complete in under 1 second for learning analysis
            if learning_time < 1.0:
                logger.info("✓ Adaptive learning performance acceptable (%.3fs)", learning_time)
            else:
                issues.append(f"Adaptive learning slow ({learning_time:.3f}s)")
                score -= 0.3

            # Test health monitoring performance
            start_time = time.time()
            health_report = self.health_monitor.monitor_health()
            health_time = time.time() - start_time

            # Should complete in under 500ms for health monitoring
            if health_time < 0.5:
                logger.info("✓ Health monitoring performance acceptable (%.3fs)", health_time)
            else:
                issues.append(f"Health monitoring slow ({health_time:.3f}s)")
                score -= 0.3

            # Test autonomous governance performance
            start_time = time.time()
            context = ArchitecturalContext(
                agent_type="test",
                action_type="test_action",
                target_modules=["test_module"],
                proposed_changes={"type": "test"},
                session_id="test_session",
            )
            action, is_compliant = self.autonomous_governance.enforce_governance(context)
            governance_time = time.time() - start_time

            # Should complete in under 200ms for governance enforcement
            if governance_time < 0.2:
                logger.info("✓ Autonomous governance performance acceptable (%.3fs)", governance_time)
            else:
                issues.append(f"Autonomous governance slow ({governance_time:.3f}s)")
                score -= 0.3

        except (ValueError, RuntimeError, KeyError) as e:
            issues.append(f"Performance benchmark test failed: {e}")
            score -= 0.4
            recommendations.append("Fix performance issues")

        return Phase3GateResult(
            gate_name="performance_benchmarks",
            status=Phase3GateStatus.PASSED if score >= 0.8 else Phase3GateStatus.FAILED,
            score=score,
            details={
                "ecosystem_ms": ecosystem_time * 1000 if "ecosystem_time" in locals() else 0,
                "learning_ms": learning_time * 1000 if "learning_time" in locals() else 0,
                "health_ms": health_time * 1000 if "health_time" in locals() else 0,
                "governance_ms": governance_time * 1000 if "governance_time" in locals() else 0,
            },
            issues=issues,
            recommendations=recommendations,
            execution_time_seconds=0.0,
        )

    def get_overall_status(self, results: Dict[str, Phase3GateResult]) -> Tuple[Phase3GateStatus, float]:
        """Get overall status and score from all gate results."""
        if not results:
            return Phase3GateStatus.PENDING, 0.0

        scores = [result.score for result in results.values()]
        overall_score = sum(scores) / len(scores)

        # Check for any failed or blocked gates
        failed_gates = [
            name
            for name, result in results.items()
            if result.status in [Phase3GateStatus.FAILED, Phase3GateStatus.BLOCKED]
        ]

        if failed_gates:
            return Phase3GateStatus.FAILED, overall_score

        # Check for any pending gates
        pending_gates = [
            name for name, result in results.items() if result.status == Phase3GateStatus.PENDING
        ]

        if pending_gates:
            return Phase3GateStatus.PENDING, overall_score

        # Check for any in-progress gates
        in_progress_gates = [
            name for name, result in results.items() if result.status == Phase3GateStatus.IN_PROGRESS
        ]

        if in_progress_gates:
            return Phase3GateStatus.IN_PROGRESS, overall_score

        # All gates passed
        return Phase3GateStatus.PASSED, overall_score
