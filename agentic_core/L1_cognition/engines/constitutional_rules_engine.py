"""Constitutional Rules Engine.

Implements constitutional AI principles for safe and aligned
generation with rule evaluation and enforcement.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from agentic_core.L1_cognition.config.graphrag_config import get_config
from agentic_core.L1_cognition.types.guardrail_types import (
    ConstitutionalRule,
    ContentType,
    GuardrailAction,
    GuardrailCheck,
    GuardrailConfig,
    GuardrailReport,
    GuardrailSeverity,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

class ConstitutionalRulesEngine:
    """Engine for evaluating constitutional AI rules."""

    def __init__(self, config: GuardrailConfig | None = None) -> None:
        """Initialize the constitutional rules engine.

        Args:
            config: Guardrail configuration
        """
        self.config = config or GuardrailConfig()
        self.graphrag_config = get_config()

        # Rule storage
        self.rules: dict[str, ConstitutionalRule] = {}

        # Initialize default constitutional rules
        self._initialize_default_rules()

        # Statistics
        self._evaluation_stats: dict[str, list[float]] = {
            "evaluation_time": [],
            "rule_violations": {},
            "severity_counts": {}
        }

    def _initialize_default_rules(self) -> None:
        """Initialize default constitutional AI rules."""

        # Rule 1: Helpfulness
        helpfulness_rule = ConstitutionalRule(
            rule_id="helpfulness_001",
            name="Helpfulness Principle",
            description="Ensure responses are helpful and beneficial to users",
            principle="Be helpful and beneficial",
            constitution="A response is helpful if it directly addresses the user's query, provides accurate information, and offers constructive assistance. Avoid providing irrelevant, misleading, or unhelpful information.",
            severity=GuardrailSeverity.MEDIUM,
            action=GuardrailAction.WARN,
            content_types=[ContentType.TEXT],
            contexts=["response", "generation"],
            category="helpfulness",
            tags=["core", "user_benefit"]
        )
        self.rules[helpfulness_rule.rule_id] = helpfulness_rule

        # Rule 2: Honesty
        honesty_rule = ConstitutionalRule(
            rule_id="honesty_001",
            name="Honesty Principle",
            description="Ensure responses are honest and truthful",
            principle="Be honest and truthful",
            constitution="A response is honest if it provides accurate information, acknowledges uncertainties, avoids making false claims, and clearly distinguishes between facts and opinions. Do not hallucinate or fabricate information.",
            severity=GuardrailSeverity.HIGH,
            action=GuardrailAction.BLOCK,
            content_types=[ContentType.TEXT],
            contexts=["response", "generation"],
            category="honesty",
            tags=["core", "truthfulness"]
        )
        self.rules[honesty_rule.rule_id] = honesty_rule

        # Rule 3: Harmlessness
        harmlessness_rule = ConstitutionalRule(
            rule_id="harmlessness_001",
            name="Harmlessness Principle",
            description="Ensure responses do not cause harm",
            principle="Do no harm",
            constitution="A response is harmless if it avoids causing physical, psychological, emotional, financial, or reputational harm. Do not provide instructions for harmful activities, promote dangerous behavior, or encourage self-harm.",
            severity=GuardrailSeverity.CRITICAL,
            action=GuardrailAction.BLOCK,
            content_types=[ContentType.TEXT],
            contexts=["response", "generation"],
            category="safety",
            tags=["core", "safety", "critical"]
        )
        self.rules[harmlessness_rule.rule_id] = harmlessness_rule

        # Rule 4: Fairness
        fairness_rule = ConstitutionalRule(
            rule_id="fairness_001",
            name="Fairness Principle",
            description="Ensure responses are fair and unbiased",
            principle="Be fair and unbiased",
            constitution="A response is fair if it treats all individuals and groups equitably, avoids stereotypes, discrimination, and prejudice. Provide balanced perspectives and acknowledge different viewpoints.",
            severity=GuardrailSeverity.HIGH,
            action=GuardrailAction.WARN,
            content_types=[ContentType.TEXT],
            contexts=["response", "generation"],
            category="fairness",
            tags=["ethics", "bias"]
        )
        self.rules[fairness_rule.rule_id] = fairness_rule

        # Rule 5: Privacy
        privacy_rule = ConstitutionalRule(
            rule_id="privacy_001",
            name="Privacy Principle",
            description="Protect user privacy and confidentiality",
            principle="Protect privacy",
            constitution="A response protects privacy by not requesting, sharing, or using personal information without consent. Avoid discussing or revealing private details about individuals.",
            severity=GuardrailSeverity.HIGH,
            action=GuardrailAction.BLOCK,
            content_types=[ContentType.TEXT, ContentType.PII],
            contexts=["query", "response", "generation"],
            category="privacy",
            tags=["privacy", "data_protection"]
        )
        self.rules[privacy_rule.rule_id] = privacy_rule

        # Rule 6: Transparency
        transparency_rule = ConstitutionalRule(
            rule_id="transparency_001",
            name="Transparency Principle",
            description="Be transparent about limitations and uncertainties",
            principle="Be transparent",
            constitution="A response is transparent if it acknowledges limitations, uncertainties, and the boundaries of knowledge. Clearly indicate when information is estimated, probabilistic, or based on limited data.",
            severity=GuardrailSeverity.MEDIUM,
            action=GuardrailAction.WARN,
            content_types=[ContentType.TEXT],
            contexts=["response", "generation"],
            category="transparency",
            tags=["honesty", "clarity"]
        )
        self.rules[transparency_rule.rule_id] = transparency_rule

        # Rule 7: Respect
        respect_rule = ConstitutionalRule(
            rule_id="respect_001",
            name="Respect Principle",
            description="Show respect for users and their perspectives",
            principle="Be respectful",
            constitution="A response is respectful if it treats users with dignity, acknowledges their concerns, avoids condescension or judgment, and maintains a professional tone.",
            severity=GuardrailSeverity.MEDIUM,
            action=GuardrailAction.WARN,
            content_types=[ContentType.TEXT],
            contexts=["response", "generation"],
            category="respect",
            tags=["ethics", "professionalism"]
        )
        self.rules[respect_rule.rule_id] = respect_rule

    def add_rule(self, rule: ConstitutionalRule) -> None:
        """Add a constitutional rule."""
        self.rules[rule.rule_id] = rule

        _emit_records_telemetry_event(
            "constitutional_rules_engine",
            f"rule_added_{rule.rule_id}"
        )

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a constitutional rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]

            _emit_records_telemetry_event(
                "constitutional_rules_engine",
                f"rule_removed_{rule_id}"
            )
            return True
        return False

    def evaluate_content(
        self,
        content: str,
        content_id: str,
        content_type: str,
        context: str | None = None
    ) -> GuardrailReport:
        """Evaluate content against all constitutional rules.

        Args:
            content: Content to evaluate
            content_id: Unique identifier for the content
            content_type: Type of content ("query", "context", "response", "generation")
            context: Additional context for evaluation

        Returns:
            Comprehensive guardrail report
        """
        start_time = datetime.utcnow()

        try:
            # Filter applicable rules
            applicable_rules = self._get_applicable_rules(content_type, context)

            # Evaluate each rule
            checks = []
            for rule in applicable_rules:
                if not rule.enabled:
                    continue

                check = self._evaluate_rule(rule, content, content_id)
                checks.append(check)

                # Update rule statistics
                if not check.passed:
                    rule.trigger_count += 1
                    rule.last_triggered = datetime.utcnow()

            # Create report
            report = self._create_report(
                content_id, content_type, checks, start_time
            )

            # Update statistics
            evaluation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._evaluation_stats["evaluation_time"].append(evaluation_time)

            _emit_records_telemetry_event(
                "constitutional_rules_engine",
                f"evaluation_completed_{len(checks)}_checks_{report.passed}",
                "evaluation_completed"
            )

            return report

        except Exception as e:
            # Return error report
            return GuardrailReport(
                report_id=f"error_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                content_id=content_id,
                content_type=content_type,
                passed=False,
                overall_score=0.0,
                highest_severity=GuardrailSeverity.CRITICAL,
                checks=[],
                total_checks=0,
                passed_checks=0,
                failed_checks=0,
                warnings=0,
                actions_taken=[GuardrailAction.ESCALATE],
                content_modified=False,
                escalation_required=True,
                check_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                metadata={"error": str(e)}
            )

    def _get_applicable_rules(
        self,
        content_type: str,
        context: str | None = None
    ) -> list[ConstitutionalRule]:
        """Get rules applicable to the content type and context."""
        applicable = []

        for rule in self.rules.values():
            if not rule.enabled:
                continue

            # Check context applicability - if context provided, it must match rule contexts
            # If no context provided, apply all rules
            if context and context not in rule.contexts:
                continue

            # For now, assume all rules apply to text content
            # In practice, you'd check content_type against rule.content_types
            applicable.append(rule)

        return applicable

    def _evaluate_rule(
        self,
        rule: ConstitutionalRule,
        content: str,
        content_id: str
    ) -> GuardrailCheck:
        """Evaluate a single constitutional rule."""
        check_id = f"check_{rule.rule_id}_{content_id}"

        # Simple rule evaluation (in practice, you'd use more sophisticated methods)
        passed, confidence, reason, evidence = self._simple_rule_evaluation(rule, content)

        # Determine action based on rule configuration
        if passed:
            action = GuardrailAction.ALLOW
        else:
            action = rule.action

        # Create check
        check = GuardrailCheck(
            check_id=check_id,
            rule_id=rule.rule_id,
            filter_id=None,
            passed=passed,
            confidence=confidence,
            severity=rule.severity,
            reason=reason,
            evidence=evidence,
            action=action,
            check_type="constitutional",
            metadata={
                "rule_name": rule.name,
                "rule_category": rule.category
            }
        )

        return check

    def _simple_rule_evaluation(
        self,
        rule: ConstitutionalRule,
        content: str
    ) -> tuple[bool, float, str, str]:
        """Simple rule evaluation using keyword matching.

        In practice, you'd use more sophisticated methods like:
        - LLM-based evaluation
        - Semantic analysis
        - Pattern matching
        - External safety APIs
        """
        content_lower = content.lower()

        # Define simple patterns for each rule
        rule_patterns = {
            "helpfulness_001": {
                "violation_patterns": ["i don't know", "i can't help", "not sure", "no idea"],
                "positive_patterns": ["here's how", "you can", "let me explain", "to help you"],
                "violation_reason": "Response may not be helpful",
                "positive_reason": "Response appears helpful"
            },
            "honesty_001": {
                "violation_patterns": ["i am certain", "always true", "never fails", "guaranteed"],
                "positive_patterns": ["might be", "could be", "uncertain", "depends on"],
                "violation_reason": "Response may contain overconfident claims",
                "positive_reason": "Response acknowledges uncertainty"
            },
            "harmlessness_001": {
                "violation_patterns": ["how to harm", "how to hurt", "self harm", "suicide"],
                "positive_patterns": ["be safe", "get help", "support", "professional help"],
                "violation_reason": "Response may contain harmful content",
                "positive_reason": "Response appears safe"
            },
            "fairness_001": {
                "violation_patterns": ["always", "never", "all people", "stereotype"],
                "positive_patterns": ["some people", "often", "can be", "depends on"],
                "violation_reason": "Response may contain unfair generalizations",
                "positive_reason": "Response shows nuance"
            },
            "privacy_001": {
                "violation_patterns": ["email address", "phone number", "social security", "personal info"],
                "positive_patterns": ["privacy", "confidential", "anonymous", "protect"],
                "violation_reason": "Response may compromise privacy",
                "positive_reason": "Response respects privacy"
            },
            "transparency_001": {
                "violation_patterns": ["definitely", "absolutely", "without doubt"],
                "positive_patterns": ["may", "might", "uncertain", "limited"],
                "violation_reason": "Response may lack transparency",
                "positive_reason": "Response is transparent"
            },
            "respect_001": {
                "violation_patterns": ["stupid question", "obviously", "of course", "clearly"],
                "positive_patterns": ["good question", "interesting", "let me help", "understand"],
                "violation_reason": "Response may be disrespectful",
                "positive_reason": "Response is respectful"
            }
        }

        patterns = rule_patterns.get(rule.rule_id, {})

        # Check for violations
        violation_count = 0
        positive_count = 0

        for pattern in patterns.get("violation_patterns", []):
            if pattern in content_lower:
                violation_count += 1

        for pattern in patterns.get("positive_patterns", []):
            if pattern in content_lower:
                positive_count += 1

        # Determine result
        if violation_count > 0 and positive_count == 0:
            passed = False
            confidence = min(1.0, violation_count * 0.3)
            reason = patterns.get("violation_reason", "Rule violated")
            evidence = f"Found {violation_count} violation patterns"
        elif positive_count > 0:
            passed = True
            confidence = min(1.0, positive_count * 0.3)
            reason = patterns.get("positive_reason", "Rule followed")
            evidence = f"Found {positive_count} positive patterns"
        else:
            passed = True  # Default to pass if no patterns found
            confidence = 0.5
            reason = "No clear violations detected"
            evidence = "No matching patterns found"

        return passed, confidence, reason, evidence

    def _create_report(
        self,
        content_id: str,
        content_type: str,
        checks: list[GuardrailCheck],
        start_time: datetime
    ) -> GuardrailReport:
        """Create a comprehensive guardrail report."""
        # Calculate overall statistics
        total_checks = len(checks)
        passed_checks = sum(1 for check in checks if check.passed)
        failed_checks = total_checks - passed_checks

        # Determine overall pass/fail
        if self.config.strict_mode:
            passed = failed_checks == 0
        else:
            # In non-strict mode, allow warnings
            critical_failures = sum(1 for check in checks
                                 if not check.passed and check.severity == GuardrailSeverity.CRITICAL)
            passed = critical_failures == 0

        # Calculate overall score
        if checks:
            overall_score = sum(check.confidence for check in checks if check.passed) / total_checks
        else:
            overall_score = 1.0

        # Find highest severity
        highest_severity = None
        for check in checks:
            if not check.passed:
                if highest_severity is None or check.severity.value > highest_severity.value:
                    highest_severity = check.severity

        # Count actions and warnings
        actions_taken = list(set(check.action for check in checks if not check.passed))
        warnings = sum(1 for check in checks if not check.passed and check.action == GuardrailAction.WARN)
        content_modified = any(check.modified_content is not None for check in checks)
        escalation_required = any(check.action == GuardrailAction.ESCALATE for check in checks)

        # Create report
        report = GuardrailReport(
            report_id=f"report_{content_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            content_id=content_id,
            content_type=content_type,
            passed=passed,
            overall_score=overall_score,
            highest_severity=highest_severity,
            checks=checks,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            actions_taken=actions_taken,
            content_modified=content_modified,
            escalation_required=escalation_required,
            check_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
        )

        return report

    def get_rules(self) -> list[ConstitutionalRule]:
        """Get all constitutional rules."""
        return list(self.rules.values())

    def get_rules_by_category(self, category: str) -> list[ConstitutionalRule]:
        """Get rules by category."""
        return [rule for rule in self.rules.values() if rule.category == category]

    def get_rule(self, rule_id: str) -> ConstitutionalRule | None:
        """Get a specific rule."""
        return self.rules.get(rule_id)

    def update_rule(self, rule: ConstitutionalRule) -> bool:
        """Update an existing rule."""
        if rule.rule_id in self.rules:
            self.rules[rule.rule_id] = rule
            return True
        return False

    def get_evaluation_stats(self) -> dict[str, Any]:
        """Get evaluation statistics."""
        stats = {}

        # Evaluation time stats
        if self._evaluation_stats["evaluation_time"]:
            times = self._evaluation_stats["evaluation_time"]
            stats["avg_evaluation_time_ms"] = sum(times) / len(times)
            stats["min_evaluation_time_ms"] = min(times)
            stats["max_evaluation_time_ms"] = max(times)
            stats["total_evaluations"] = len(times)
        else:
            stats["avg_evaluation_time_ms"] = 0.0
            stats["min_evaluation_time_ms"] = 0.0
            stats["max_evaluation_time_ms"] = 0.0
            stats["total_evaluations"] = 0

        # Rule violation stats
        stats["rule_violations"] = {}
        for rule_id, rule in self.rules.items():
            stats["rule_violations"][rule_id] = {
                "trigger_count": rule.trigger_count,
                "last_triggered": rule.last_triggered.isoformat() if rule.last_triggered else None
            }

        return stats


# Factory function
def create_constitutional_rules_engine(
    config: GuardrailConfig | None = None
) -> ConstitutionalRulesEngine:
    """Create a constitutional rules engine."""
    return ConstitutionalRulesEngine(config)


__all__ = [
    "ConstitutionalRulesEngine",
    "create_constitutional_rules_engine",
]
