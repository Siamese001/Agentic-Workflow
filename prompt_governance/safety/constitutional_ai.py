"""Constitutional AI implementation for prompt governance.

Provides rule-based content validation and safety checks.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConstitutionalPrinciple:
    """A constitutional principle for AI governance."""
    id: str
    name: str
    description: str
    category: str
    priority: int = 0
    examples: List[str] = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []


@dataclass
class LLMJudgment:
    """Judgment from an LLM on content compliance."""
    content: str
    principle_id: str
    judgment: str  # "compliant" or "violation"
    reasoning: str
    confidence: float
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            from datetime import datetime
            self.timestamp = datetime.now().isoformat()


class LLMClient:
    """Mock LLM client for constitutional AI judgments."""
    
    def __init__(self, model: str = "gpt-4"):
        """Initialize LLM client.
        
        Args:
            model: Model name to use
        """
        self.model = model
    
    def judge_content(self, content: str, principle: ConstitutionalPrinciple) -> LLMJudgment:
        """Judge content against a constitutional principle.
        
        Args:
            content: Content to judge
            principle: Principle to judge against
            
        Returns:
            LLM judgment
        """
        # Simple mock judgment based on keyword matching
        content_lower = content.lower()
        
        # Check for obvious violations
        violation_keywords = ["harmful", "illegal", "unethical", "biased", "unfair"]
        is_violation = any(keyword in content_lower for keyword in violation_keywords)
        
        return LLMJudgment(
            content=content,
            principle_id=principle.id,
            judgment="violation" if is_violation else "compliant",
            reasoning=f"Content appears {'to violate' if is_violation else 'to comply with'} principle {principle.name}",
            confidence=0.8 if is_violation else 0.9
        )


class MockLLMClient(LLMClient):
    """Mock LLM client for testing."""
    
    def __init__(self, model: str = "gpt-4", responses: Optional[Dict[str, LLMJudgment]] = None):
        """Initialize mock LLM client.
        
        Args:
            model: Model name to use
            responses: Predefined responses for testing
        """
        super().__init__(model)
        self.responses = responses or {}
        self.call_history: List[Dict[str, Any]] = []
    
    def judge_content(self, content: str, principle: ConstitutionalPrinciple) -> LLMJudgment:
        """Judge content against a constitutional principle.
        
        Args:
            content: Content to judge
            principle: Principle to judge against
            
        Returns:
            LLM judgment
        """
        # Record the call for testing
        self.call_history.append({
            "content": content,
            "principle_id": principle.id,
            "timestamp": self._get_timestamp()
        })
        
        # Return predefined response if available
        key = f"{content}:{principle.id}"
        if key in self.responses:
            return self.responses[key]
        
        # Default mock behavior
        return super().judge_content(content, principle)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


class RuleType(Enum):
    """Types of constitutional rules."""
    HARMFUL_CONTENT = "harmful_content"
    BIAS = "bias"
    PRIVACY = "privacy"
    MISINFORMATION = "misinformation"
    TOXICITY = "toxicity"
    LEGAL = "legal"


class RuleSeverity(Enum):
    """Severity levels for rule violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ViolationType(Enum):
    """Types of violations."""
    NONE = "none"
    WARNING = "warning"
    ERROR = "error"
    BLOCK = "block"


class RuleAction(Enum):
    """Actions to take on violations."""
    NONE = "none"
    LOG = "log"
    WARN = "warn"
    REJECT = "reject"
    ESCALATE = "escalate"


@dataclass
class ConstitutionalRule:
    """A single constitutional rule."""
    id: str
    name: str
    type: RuleType
    severity: RuleSeverity
    description: str
    pattern: Optional[str] = None
    keywords: List[str] = None
    action: RuleAction = RuleAction.WARN
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


@dataclass
class ViolationReport:
    """Report of a rule violation."""
    rule_id: str
    rule_name: str
    violation_type: ViolationType
    severity: RuleSeverity
    message: str
    matched_text: Optional[str] = None
    confidence: float = 0.0


@dataclass
class ConstitutionalReviewResult:
    """Result of constitutional review."""
    approved: bool
    violations: List[ViolationReport]
    score: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def has_violations(self) -> bool:
        """Check if there are any violations."""
        return len(self.violations) > 0
    
    @property
    def critical_violations(self) -> List[ViolationReport]:
        """Get only critical violations."""
        return [v for v in self.violations if v.severity == RuleSeverity.CRITICAL]


class RuleEngine:
    """Engine for evaluating constitutional rules."""
    
    def __init__(self):
        """Initialize rule engine."""
        self.rules: List[ConstitutionalRule] = []
        self.compiled_patterns: Dict[str, re.Pattern] = {}
    
    def add_rule(self, rule: ConstitutionalRule) -> None:
        """Add a rule to the engine.
        
        Args:
            rule: Rule to add
        """
        self.rules.append(rule)
        
        # Compile pattern if provided
        if rule.pattern:
            try:
                self.compiled_patterns[rule.id] = re.compile(
                    rule.pattern, 
                    re.IGNORECASE | re.MULTILINE
                )
            except re.error as e:
                logger.warning(f"Failed to compile pattern for rule {rule.id}: {e}")
    
    def evaluate(self, content: str) -> List[ViolationReport]:
        """Evaluate content against all rules.
        
        Args:
            content: Content to evaluate
            
        Returns:
            List of violation reports
        """
        violations = []
        
        for rule in self.rules:
            violation = self._check_rule(content, rule)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_rule(self, content: str, rule: ConstitutionalRule) -> Optional[ViolationReport]:
        """Check a single rule against content.
        
        Args:
            content: Content to check
            rule: Rule to check
            
        Returns:
            Violation report if rule is violated
        """
        # Check pattern match
        matched_text = None
        confidence = 0.0
        
        if rule.id in self.compiled_patterns:
            match = self.compiled_patterns[rule.id].search(content)
            if match:
                matched_text = match.group(0)
                confidence = 0.8
        
        # Check keyword matches
        keyword_matches = 0
        for keyword in rule.keywords:
            if keyword.lower() in content.lower():
                keyword_matches += 1
                if not matched_text:
                    matched_text = keyword
        
        if keyword_matches > 0:
            keyword_confidence = min(keyword_matches / len(rule.keywords), 1.0)
            confidence = max(confidence, keyword_confidence * 0.6)
        
        # Determine if violation occurred
        if confidence > 0.5:
            violation_type = self._determine_violation_type(rule, confidence)
            
            return ViolationReport(
                rule_id=rule.id,
                rule_name=rule.name,
                violation_type=violation_type,
                severity=rule.severity,
                message=f"Rule '{rule.name}' violated: {rule.description}",
                matched_text=matched_text,
                confidence=confidence
            )
        
        return None
    
    def _determine_violation_type(self, rule: ConstitutionalRule, confidence: float) -> ViolationType:
        """Determine violation type based on rule and confidence.
        
        Args:
            rule: The violated rule
            confidence: Confidence score (0-1)
            
        Returns:
            Type of violation
        """
        if rule.severity == RuleSeverity.CRITICAL:
            return ViolationType.BLOCK
        elif rule.severity == RuleSeverity.HIGH:
            return ViolationType.ERROR if confidence > 0.8 else ViolationType.WARNING
        elif rule.severity == RuleSeverity.MEDIUM:
            return ViolationType.WARNING if confidence > 0.7 else ViolationType.WARNING
        else:
            return ViolationType.WARNING


class ContentValidator:
    """Validates content against constitutional rules."""
    
    def __init__(self, rule_engine: Optional[RuleEngine] = None):
        """Initialize content validator.
        
        Args:
            rule_engine: Optional rule engine
        """
        self.rule_engine = rule_engine or RuleEngine()
        self._setup_default_rules()
    
    def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> ConstitutionalReviewResult:
        """Validate content against constitutional rules.
        
        Args:
            content: Content to validate
            context: Optional validation context
            
        Returns:
            Review result with violations
        """
        violations = self.rule_engine.evaluate(content)
        
        # Calculate approval score
        score = self._calculate_score(violations)
        approved = score >= 0.7 and not any(v.severity == RuleSeverity.CRITICAL for v in violations)
        
        return ConstitutionalReviewResult(
            approved=approved,
            violations=violations,
            score=score,
            metadata={"context": context or {}}
        )
    
    def _calculate_score(self, violations: List[ViolationReport]) -> float:
        """Calculate approval score based on violations.
        
        Args:
            violations: List of violations
            
        Returns:
            Score between 0 and 1
        """
        if not violations:
            return 1.0
        
        # Weight violations by severity
        severity_weights = {
            RuleSeverity.LOW: 0.1,
            RuleSeverity.MEDIUM: 0.3,
            RuleSeverity.HIGH: 0.6,
            RuleSeverity.CRITICAL: 1.0,
        }
        
        total_penalty = sum(
            severity_weights[v.severity] * v.confidence
            for v in violations
        )
        
        return max(0.0, 1.0 - total_penalty)
    
    def _setup_default_rules(self) -> None:
        """Setup default constitutional rules."""
        default_rules = [
            ConstitutionalRule(
                id="harmful_content",
                name="Harmful Content",
                type=RuleType.HARMFUL_CONTENT,
                severity=RuleSeverity.HIGH,
                description="Content that may cause harm",
                keywords=["harm", "hurt", "damage", "injure"],
                action=RuleAction.REJECT
            ),
            ConstitutionalRule(
                id="bias_detection",
                name="Bias Detection",
                type=RuleType.BIAS,
                severity=RuleSeverity.MEDIUM,
                description="Detect potential bias in content",
                keywords=["biased", "prejudice", "stereotype"],
                action=RuleAction.WARN
            ),
            ConstitutionalRule(
                id="privacy_protection",
                name="Privacy Protection",
                type=RuleType.PRIVACY,
                severity=RuleSeverity.HIGH,
                description="Protect private information",
                pattern=r"\b\d{3}-\d{2}-\d{4}\b|\b\d{16}\b",  # SSN or credit card
                action=RuleAction.ESCALATE
            ),
        ]
        
        for rule in default_rules:
            self.rule_engine.add_rule(rule)


class ConstitutionalAISystem:
    """Main constitutional AI system."""
    
    def __init__(self, validator: Optional[ContentValidator] = None):
        """Initialize constitutional AI system.
        
        Args:
            validator: Optional content validator
        """
        self.validator = validator or ContentValidator()
        self.review_history: List[ConstitutionalReviewResult] = []
    
    def review_content(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ConstitutionalReviewResult:
        """Review content for constitutional compliance.
        
        Args:
            content: Content to review
            context: Optional review context
            
        Returns:
            Review result
        """
        result = self.validator.validate(content, context)
        self.review_history.append(result)
        
        # Log violations if any
        if result.has_violations:
            logger.warning(f"Content review found {len(result.violations)} violations")
        
        return result
    
    def get_review_stats(self) -> Dict[str, Any]:
        """Get statistics about content reviews.
        
        Returns:
            Review statistics
        """
        if not self.review_history:
            return {"total_reviews": 0}
        
        total = len(self.review_history)
        approved = sum(1 for r in self.review_history if r.approved)
        with_violations = sum(1 for r in self.review_history if r.has_violations)
        
        return {
            "total_reviews": total,
            "approved": approved,
            "rejected": total - approved,
            "with_violations": with_violations,
            "approval_rate": approved / total,
            "average_score": sum(r.score for r in self.review_history) / total
        }


def create_constitutional_ai_system(config: Optional[Dict[str, Any]] = None) -> ConstitutionalAISystem:
    """Create a constitutional AI system.
    
    Args:
        config: Optional configuration
        
    Returns:
        ConstitutionalAISystem instance
    """
    return ConstitutionalAISystem()


def review_content(content: str, context: Optional[Dict[str, Any]] = None) -> ConstitutionalReviewResult:
    """Review content for constitutional compliance.
    
    Args:
        content: Content to review
        context: Optional review context
        
    Returns:
        Review result
    """
    system = create_constitutional_ai_system()
    return system.review_content(content, context)
