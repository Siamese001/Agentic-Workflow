"""
Reflection Agent - Self-Critique and Learning for L5+ Autonomy.

Implements the Canon Validator ReflectionAgent pattern for autonomous
self-assessment, strategy adjustment, and memory consolidation.

Canon Validator Patterns Implemented:
- Self-critique with structured questions
- Decision keywords: CONVERGE_AND_COMMIT, ROLLBACK, ESCALATE, etc.
- Memory consolidation via embeddings
- Execution log analysis
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ReflectionDecision(str, Enum):
    """Decision keywords matching Canon Validator ReflectionAgent output."""

    CONVERGE_AND_COMMIT = "CONVERGE_AND_COMMIT"
    MARK_FLAPPING_SKIP_FILE = "MARK_FLAPPING_SKIP_FILE"
    ROLLBACK_LAST_CHANGE_AND_RETRY = "ROLLBACK_LAST_CHANGE_AND_RETRY"
    ESCALATE_TO_HUMAN_WITH_REPORT = "ESCALATE_TO_HUMAN_WITH_REPORT"
    CONTINUE_NEXT_CYCLE = "CONTINUE_NEXT_CYCLE"
    ADJUST_STRATEGY = "ADJUST_STRATEGY"


@dataclass
class ReflectionResult:
    """Result of a reflection cycle."""

    decision: ReflectionDecision
    reasoning: str
    recommendations: List[str] = field(default_factory=list)
    quality_trend: str = "stable"  # improving, stable, degrading
    signal_analysis: Dict[str, Any] = field(default_factory=dict)
    cycle: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "decision": self.decision.value,
            "reasoning": self.reasoning,
            "recommendations": self.recommendations,
            "quality_trend": self.quality_trend,
            "signal_analysis": self.signal_analysis,
            "cycle": self.cycle,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ExecutionTrace:
    """Trace of a single execution for reflection analysis."""

    cycle: int
    phase: str
    agent: str
    success: bool
    duration_ms: float
    input_summary: str = ""
    output_summary: str = ""
    signals_emitted: List[str] = field(default_factory=list)
    quality_score: Optional[float] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ReflectionAgent:
    """
    Self-critique agent for L5+ autonomous systems.

    Analyzes execution history, signals, and quality metrics to:
    1. Determine if system should converge, rollback, or escalate
    2. Identify patterns in failures
    3. Recommend strategy adjustments
    4. Consolidate successful patterns into memory

    Canon Validator Pattern:
        reflection_prompt = '''
        Ask:
        1. Did modifications reduce signals?
        2. Did any new signals appear? → regression?
        3. Are files still subatomic and at correct depth?
        4. What strategy failed/succeeded?
        5. What should change next cycle?
        '''
    """

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        min_quality_threshold: float = 0.7,
        max_consecutive_failures: int = 3
    ) -> None:
        """
        Initialize the reflection agent.

        Args:
            llm_client: Optional LLM client for advanced reflection
            min_quality_threshold: Minimum acceptable quality score
            max_consecutive_failures: Max failures before escalation
        """
        self.llm_client = llm_client
        self.min_quality_threshold = min_quality_threshold
        self.max_consecutive_failures = max_consecutive_failures

        self.execution_history: List[ExecutionTrace] = []
        self.reflection_history: List[ReflectionResult] = []
        self.successful_patterns: List[Dict[str, Any]] = []
        self.consecutive_failures: int = 0

        logger.info("ReflectionAgent initialized - Canon Validator self-critique active")

    async def reflect_on_execution(
        self,
        execution_log: List[Dict[str, Any]],
        signals_summary: Dict[str, Any],
        cycle: int,
        quality_scores: Optional[Dict[str, float]] = None
    ) -> ReflectionResult:
        """
        Perform self-critique on the current execution cycle.

        Args:
            execution_log: List of execution events from the cycle
            signals_summary: Summary of signals from SignalBus
            cycle: Current cycle number
            quality_scores: Optional quality metrics

        Returns:
            ReflectionResult with decision and recommendations
        """
        logger.info(f"[REFLECTION] Analyzing cycle {cycle}...")

        # Analyze the execution
        analysis = self._analyze_execution(execution_log, signals_summary, quality_scores)

        # Determine decision based on analysis
        decision, reasoning = self._determine_decision(analysis, cycle)

        # Generate recommendations
        recommendations = self._generate_recommendations(analysis, decision)

        # Determine quality trend
        quality_trend = self._assess_quality_trend(quality_scores)

        result = ReflectionResult(
            decision=decision,
            reasoning=reasoning,
            recommendations=recommendations,
            quality_trend=quality_trend,
            signal_analysis=analysis,
            cycle=cycle
        )

        self.reflection_history.append(result)

        # Update consecutive failure counter
        if decision in [
            ReflectionDecision.ROLLBACK_LAST_CHANGE_AND_RETRY,
            ReflectionDecision.ESCALATE_TO_HUMAN_WITH_REPORT
        ]:
            self.consecutive_failures += 1
        else:
            self.consecutive_failures = 0

        # Consolidate successful patterns
        if decision == ReflectionDecision.CONVERGE_AND_COMMIT:
            self._consolidate_successful_patterns(execution_log)

        logger.info(f"[REFLECTION] Decision: {decision.value}")
        logger.info(f"[REFLECTION] Reasoning: {reasoning}")

        return result

    def _analyze_execution(
        self,
        execution_log: List[Dict[str, Any]],
        signals_summary: Dict[str, Any],
        quality_scores: Optional[Dict[str, float]]
    ) -> Dict[str, Any]:
        """Analyze execution data for reflection."""

        # Count successes and failures
        total_steps = len(execution_log)
        successful_steps = sum(1 for e in execution_log if e.get("success", False))
        failed_steps = total_steps - successful_steps

        # Analyze signals
        active_signals = signals_summary.get("active_signals", [])
        signal_count = signals_summary.get("signal_count", 0)

        # Check for critical signals
        critical_signals = [s for s in active_signals if s in [
            "CRITICAL_FAIL", "SECURE_REBOOT", "VETOED"
        ]]

        # Check for regression signals
        regression_signals = [s for s in active_signals if s in [
            "TEST_FAILURE", "PERFORMANCE_REGRESSION", "QUALITY_BELOW_THRESHOLD"
        ]]

        # Calculate average quality if available
        avg_quality = None
        if quality_scores:
            scores = [v for v in quality_scores.values() if v is not None]
            if scores:
                avg_quality = sum(scores) / len(scores)

        return {
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "success_rate": successful_steps / total_steps if total_steps > 0 else 0,
            "active_signals": active_signals,
            "signal_count": signal_count,
            "critical_signals": critical_signals,
            "regression_signals": regression_signals,
            "has_critical": len(critical_signals) > 0,
            "has_regression": len(regression_signals) > 0,
            "average_quality": avg_quality,
            "quality_acceptable": avg_quality >= self.min_quality_threshold if avg_quality else True,
            "consecutive_failures": self.consecutive_failures
        }

    def _determine_decision(
        self,
        analysis: Dict[str, Any],
        cycle: int
    ) -> tuple[ReflectionDecision, str]:
        """Determine the reflection decision based on analysis."""

        # Critical failure → Escalate
        if analysis["has_critical"]:
            return (
                ReflectionDecision.ESCALATE_TO_HUMAN_WITH_REPORT,
                f"Critical signals detected: {analysis['critical_signals']}. Human intervention required."
            )

        # Too many consecutive failures → Escalate
        if self.consecutive_failures >= self.max_consecutive_failures:
            return (
                ReflectionDecision.ESCALATE_TO_HUMAN_WITH_REPORT,
                f"Max consecutive failures ({self.max_consecutive_failures}) reached. Escalating to human."
            )

        # Regression detected → Rollback
        if analysis["has_regression"]:
            return (
                ReflectionDecision.ROLLBACK_LAST_CHANGE_AND_RETRY,
                f"Regression detected: {analysis['regression_signals']}. Rolling back to retry with different strategy."
            )

        # Quality below threshold → Adjust strategy
        if not analysis["quality_acceptable"]:
            return (
                ReflectionDecision.ADJUST_STRATEGY,
                f"Quality score {analysis['average_quality']:.2f} below threshold {self.min_quality_threshold}. Adjusting strategy."
            )

        # High success rate and no issues → Converge
        if analysis["success_rate"] >= 0.9 and analysis["signal_count"] == 0:
            return (
                ReflectionDecision.CONVERGE_AND_COMMIT,
                f"High success rate ({analysis['success_rate']:.1%}) with no active signals. Ready to converge."
            )

        # Some failures but manageable → Continue
        if analysis["success_rate"] >= 0.7:
            return (
                ReflectionDecision.CONTINUE_NEXT_CYCLE,
                f"Success rate {analysis['success_rate']:.1%} acceptable. Continuing to next cycle."
            )

        # Low success rate → Adjust strategy
        return (
            ReflectionDecision.ADJUST_STRATEGY,
            f"Low success rate ({analysis['success_rate']:.1%}). Strategy adjustment needed."
        )

    def _generate_recommendations(
        self,
        analysis: Dict[str, Any],
        decision: ReflectionDecision
    ) -> List[str]:
        """Generate actionable recommendations based on analysis."""

        recommendations = []

        if analysis["failed_steps"] > 0:
            recommendations.append(
                f"Review {analysis['failed_steps']} failed steps for common patterns"
            )

        if analysis["has_regression"]:
            recommendations.append(
                "Check recent changes that may have caused regression"
            )
            recommendations.append(
                "Consider reverting to last known good state"
            )

        if not analysis["quality_acceptable"]:
            recommendations.append(
                f"Improve quality metrics - current: {analysis['average_quality']:.2f}, target: {self.min_quality_threshold}"
            )

        if decision == ReflectionDecision.ADJUST_STRATEGY:
            recommendations.append(
                "Consider adjusting temperature or prompt parameters"
            )
            recommendations.append(
                "Review few-shot examples for relevance"
            )

        if decision == ReflectionDecision.ESCALATE_TO_HUMAN_WITH_REPORT:
            recommendations.append(
                "Generate detailed report for human review"
            )
            recommendations.append(
                "Document all attempted strategies and outcomes"
            )

        return recommendations

    def _assess_quality_trend(
        self,
        current_scores: Optional[Dict[str, float]]
    ) -> str:
        """Assess quality trend across recent reflections."""

        if not current_scores or len(self.reflection_history) < 2:
            return "stable"

        # Get recent quality scores
        recent_qualities = []
        for r in self.reflection_history[-3:]:
            if r.signal_analysis.get("average_quality"):
                recent_qualities.append(r.signal_analysis["average_quality"])

        if len(recent_qualities) < 2:
            return "stable"

        # Calculate trend
        trend = recent_qualities[-1] - recent_qualities[0]

        if trend > 0.05:
            return "improving"
        elif trend < -0.05:
            return "degrading"
        else:
            return "stable"

    def _consolidate_successful_patterns(
        self,
        execution_log: List[Dict[str, Any]]
    ) -> None:
        """Consolidate successful execution patterns for future recall."""

        successful_executions = [e for e in execution_log if e.get("success", False)]

        for execution in successful_executions:
            pattern = {
                "agent": execution.get("agent", "unknown"),
                "input_type": execution.get("input_type", "unknown"),
                "strategy": execution.get("strategy", {}),
                "quality_score": execution.get("quality_score"),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.successful_patterns.append(pattern)

        # Keep only recent patterns
        if len(self.successful_patterns) > 100:
            self.successful_patterns = self.successful_patterns[-100:]

        logger.debug(f"Consolidated {len(successful_executions)} successful patterns")

    async def reflect_with_llm(
        self,
        execution_log: List[Dict[str, Any]],
        signals_summary: Dict[str, Any],
        cycle: int
    ) -> ReflectionResult:
        """
        Perform LLM-enhanced reflection (Canon Validator pattern).

        Uses structured prompt for self-critique.
        """
        if not self.llm_client:
            return await self.reflect_on_execution(execution_log, signals_summary, cycle)

        # Build reflection prompt (Canon Validator pattern)
        reflection_prompt = f"""
<self_critique_guidance>
You are reflecting on healing cycle {cycle}.

Execution Summary:
- Total steps: {len(execution_log)}
- Successful: {sum(1 for e in execution_log if e.get('success', False))}
- Failed: {sum(1 for e in execution_log if not e.get('success', False))}

Active Signals: {signals_summary.get('active_signals', [])}

Recent Execution Log:
{json.dumps(execution_log[-5:], indent=2, default=str)}

Ask yourself:
1. Did modifications reduce signals? (Goal: zero signals)
2. Did any new signals appear? → regression?
3. Is quality improving, stable, or degrading?
4. What strategy failed/succeeded?
5. What should change next cycle?
</self_critique_guidance>

Based on your analysis, respond with EXACTLY ONE of these keywords followed by a brief explanation:
- CONVERGE_AND_COMMIT: System is stable, ready to finalize
- MARK_FLAPPING_SKIP_FILE: Specific component is unstable, skip it
- ROLLBACK_LAST_CHANGE_AND_RETRY: Recent change caused regression, revert
- ESCALATE_TO_HUMAN_WITH_REPORT: Cannot resolve autonomously, need human
- CONTINUE_NEXT_CYCLE: Progress being made, continue
- ADJUST_STRATEGY: Need to change approach

Response format:
KEYWORD: explanation
"""

        try:
            response = await self.llm_client.generate(reflection_prompt)
            decision, reasoning = self._parse_llm_response(response)

            result = ReflectionResult(
                decision=decision,
                reasoning=reasoning,
                recommendations=self._generate_recommendations(
                    self._analyze_execution(execution_log, signals_summary, None),
                    decision
                ),
                cycle=cycle
            )

            self.reflection_history.append(result)
            return result

        except Exception as e:
            logger.error(f"LLM reflection failed: {e}")
            return await self.reflect_on_execution(execution_log, signals_summary, cycle)

    def _parse_llm_response(self, response: str) -> tuple[ReflectionDecision, str]:
        """Parse LLM response to extract decision and reasoning."""

        response = response.strip()

        # Try to match decision keywords
        for decision in ReflectionDecision:
            if decision.value in response.upper():
                # Extract reasoning after the keyword
                parts = response.split(":", 1)
                reasoning = parts[1].strip() if len(parts) > 1 else response
                return decision, reasoning

        # Default to continue if no clear decision
        return ReflectionDecision.CONTINUE_NEXT_CYCLE, response

    def get_reflection_summary(self) -> Dict[str, Any]:
        """Get summary of reflection history for reporting."""

        if not self.reflection_history:
            return {"status": "no_reflections"}

        decisions = [r.decision.value for r in self.reflection_history]

        return {
            "total_reflections": len(self.reflection_history),
            "latest_decision": self.reflection_history[-1].decision.value,
            "latest_reasoning": self.reflection_history[-1].reasoning,
            "decision_distribution": {
                d: decisions.count(d) for d in set(decisions)
            },
            "consecutive_failures": self.consecutive_failures,
            "successful_patterns_count": len(self.successful_patterns),
            "quality_trend": self.reflection_history[-1].quality_trend
        }

    async def store_successful_trace(self, execution_log: List[Dict[str, Any]], cycle: int) -> bool:
        """
        Store a successful execution trace as embedding for learning.

        Args:
            execution_log: List of execution steps
            cycle: Current cycle number

        Returns:
            True if stored successfully
        """
        try:
            # Import deep brain
            from agentic_core.L4_state.checkpointing import get_deep_brain
            deep_brain = get_deep_brain()

            # Create learning record from successful trace
            successful_steps = [e for e in execution_log if e.get('success', False)]

            if not successful_steps:
                return False

            # Extract patterns from successful execution
            pattern_text = self._extract_pattern_text(successful_steps)

            # Store with metadata
            metadata = {
                "cycle": cycle,
                "success_rate": len(successful_steps) / len(execution_log),
                "total_steps": len(execution_log),
                "pattern_type": "successful_trace",
                "timestamp": datetime.utcnow().isoformat()
            }

            # Generate embedding ID
            import hashlib
            embedding_id = hashlib.md5(pattern_text.encode()).hexdigest()

            # Store in deep brain
            result = await deep_brain.upsert_embedding(
                text=pattern_text,
                metadata=metadata,
                embedding_id=embedding_id
            )

            if result:
                logger.info(f"Stored successful trace embedding: {embedding_id[:8]}...")
                self.successful_patterns.append({
                    "id": embedding_id,
                    "cycle": cycle,
                    "pattern": pattern_text[:200] + "..."
                })

            return result

        except Exception as e:
            logger.error(f"Failed to store successful trace: {e}")
            return False

    def _extract_pattern_text(self, successful_steps: List[Dict[str, Any]]) -> str:
        """Extract learning pattern text from successful steps."""
        patterns = []

        for step in successful_steps:
            pattern = f"Action: {step.get('action', 'unknown')}\n"
            pattern += f"Result: {step.get('result', 'unknown')}\n"
            if 'strategy' in step:
                pattern += f"Strategy: {step['strategy']}\n"
            pattern += "---\n"
            patterns.append(pattern)

        return "\n".join(patterns)

    async def recall_similar_patterns(self, current_context: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Recall similar successful patterns from memory.

        Args:
            current_context: Description of current situation
            limit: Maximum number of patterns to recall

        Returns:
            List of similar patterns with metadata
        """
        try:
            from agentic_core.L4_state.checkpointing import get_deep_brain
            deep_brain = get_deep_brain()

            # Search for similar patterns
            results = await deep_brain.search_embeddings(
                query=current_context,
                top_k=limit,
                filter_dict={"pattern_type": "successful_trace"}
            )

            logger.info(f"Recalled {len(results)} similar patterns")
            return results

        except Exception as e:
            logger.error(f"Failed to recall patterns: {e}")
            return []

    def reset(self) -> None:
        """Reset reflection state for new workflow."""
        self.execution_history.clear()
        self.reflection_history.clear()
        self.consecutive_failures = 0
        logger.info("ReflectionAgent state reset")


# Factory function
def create_reflection_agent(
    llm_client: Optional[Any] = None,
    min_quality_threshold: float = 0.7,
    max_consecutive_failures: int = 3
) -> ReflectionAgent:
    """Create a ReflectionAgent instance."""
    return ReflectionAgent(
        llm_client=llm_client,
        min_quality_threshold=min_quality_threshold,
        max_consecutive_failures=max_consecutive_failures
    )
