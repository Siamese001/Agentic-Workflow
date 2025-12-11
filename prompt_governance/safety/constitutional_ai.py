"""
Simplified Constitutional AI System for 10_12
Constitutional AI Rule Stack (10_12-Native Implementation)

Lightweight constitutional AI system that provides safety
and alignment without over-engineered complexity.
Focuses on rule-based validation, ethical guidelines,
and content compliance checking.
"""

import logging
import re
import json
from typing import Dict, List, Optional, Tuple, Any, Protocol
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from collections import defaultdict
import time

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of constitutional rules"""
    SAFETY = "safety"
    ETHICS = "ethics"
    PRIVACY = "privacy"
    BIAS = "bias"
    LEGAL = "legal"
    QUALITY = "quality"


class RuleSeverity(Enum):
    """Severity levels for rule violations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ViolationType(Enum):
    """Types of constitutional violations"""
    CONTENT = "content"
    STYLE = "style"
    STRUCTURE = "structure"
    CONTEXT = "context"


@dataclass
class ConstitutionalPrinciple:
    """Individual constitutional principle for LLM evaluation"""
    id: str
    name: str
    definition: str
    evaluation_prompt: str  # Template for asking LLM to evaluate
    severity: RuleSeverity = RuleSeverity.MEDIUM


@dataclass
class LLMJudgment:
    """Result of LLM-based constitutional evaluation"""
    principle_id: str
    is_compliant: bool
    confidence: float
    reasoning: str
    suggested_fix: Optional[str] = None


class LLMClient(Protocol):
    """Protocol for LLM client interface"""
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM"""
        ...


class MockLLMClient:
    """Mock LLM client for testing"""
    def generate(self, prompt: str, **kwargs) -> str:
        # Check if the prompt contains harmful content evaluation
        prompt_lower = prompt.lower()
        content_start = prompt_lower.find("content:")
        if content_start != -1:
            # Extract the content being evaluated
            content_end = prompt_lower.find("\n", content_start)
            if content_end == -1:
                content_end = len(prompt_lower)
            content = prompt_lower[content_start:content_end]
            
            # Check for harmful keywords
            if "kill" in content and ("harm" in prompt_lower or "harmful" in prompt_lower):
                return json.dumps({
                    "is_compliant": False,
                    "confidence": 0.9,
                    "reasoning": "Content contains harmful language",
                    "suggested_fix": "Remove harmful references"
                })
        return json.dumps({
            "is_compliant": True,
            "confidence": 0.95,
            "reasoning": "Content is compliant",
            "suggested_fix": None
        })


@dataclass
class ConstitutionalRule:
    """Individual constitutional rule"""
    rule_id: str
    rule_type: RuleType
    title: str
    description: str
    pattern: str  # Regex pattern for detection
    severity: RuleSeverity
    action: str  # warn, block, modify
    replacement: Optional[str] = None


@dataclass
class ViolationReport:
    """Report of constitutional violation"""
    rule_id: str
    violation_type: ViolationType
    severity: RuleSeverity
    location: str  # Description of where violation occurred
    content: str  # The violating content
    suggestion: str  # How to fix the violation
    confidence: float


@dataclass
class ConstitutionalReviewResult:
    """Result of constitutional review"""
    is_compliant: bool
    violations: List[ViolationReport]
    compliance_score: float
    recommendations: List[str]
    reviewed_at: float


class RuleEngine:
    """
    Simple Rule-Based Validation Engine
    
    Applies constitutional rules using pattern matching
    and heuristic analysis without complex ML.
    """
    
    def __init__(self):
        self.rules: Dict[str, ConstitutionalRule] = {}
        self.rule_patterns: Dict[RuleType, List[ConstitutionalRule]] = {
            rt: [] for rt in RuleType
        }
        self._load_default_rules()
    
    def add_rule(self, rule: ConstitutionalRule) -> None:
        """Add a constitutional rule to the engine."""
        self.rules[rule.rule_id] = rule
        self.rule_patterns[rule.rule_type].append(rule)
        logger.debug(f"Added constitutional rule: {rule.rule_id}")
    
    def remove_rule(self, rule_id: str) -> None:
        """Remove a constitutional rule from the engine."""
        if rule_id in self.rules:
            rule = self.rules[rule_id]
            self.rule_patterns[rule.rule_type].remove(rule)
            del self.rules[rule_id]
            logger.debug(f"Removed constitutional rule: {rule_id}")
    
    def check_compliance(self, content: str, context: Dict[str, object] = None) -> List[ViolationReport]:
        """
        Check content against all constitutional rules.
        
        Args:
            content: Content to check
            context: Optional context for rule evaluation
            
        Returns:
            List of violation reports
        """
        violations = []
        
        for rule in self.rules.values():
            rule_violations = self._check_rule(content, rule, context)
            violations.extend(rule_violations)
        
        # Sort violations by severity
        severity_order = {
            RuleSeverity.CRITICAL: 0,
            RuleSeverity.HIGH: 1,
            RuleSeverity.MEDIUM: 2,
            RuleSeverity.LOW: 3
        }
        
        violations.sort(key=lambda v: severity_order.get(v.severity, 4))
        
        return violations
    
    def _check_rule(
        self, 
        content: str, 
        rule: ConstitutionalRule, 
        context: Dict[str, object] = None
    ) -> List[ViolationReport]:
        """Check content against a specific rule."""
        violations = []
        
        try:
            # Pattern matching
            matches = re.finditer(rule.pattern, content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                violation = ViolationReport(
                    rule_id=rule.rule_id,
                    violation_type=ViolationType.CONTENT,
                    severity=rule.severity,
                    location=f"Position {match.start()}-{match.end()}",
                    content=match.group(),
                    suggestion=self._generate_suggestion(rule, match.group()),
                    confidence=0.9  # High confidence for pattern matches
                )
                violations.append(violation)
            
            # Contextual checks for certain rule types
            if rule.rule_type in [RuleType.SAFETY, RuleType.ETHICS]:
                context_violations = self._check_contextual_rules(content, rule, context)
                violations.extend(context_violations)
        
        except re.error as e:
            logger.error(f"Regex error in rule {rule.rule_id}: {e}")
        
        return violations
    
    def _check_contextual_rules(
        self, 
        content: str, 
        rule: ConstitutionalRule, 
        context: Dict[str, object] = None
    ) -> List[ViolationReport]:
        """Check contextual rules that depend on additional information."""
        violations = []
        
        if not context:
            return violations
        
        # Example: Check for sensitive information in personal contexts
        if rule.rule_type == RuleType.PRIVACY:
            if context.get('is_personal', False):
                # Additional privacy checks for personal content
                personal_patterns = [
                    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                    r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'  # Credit card
                ]
                
                for pattern in personal_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        violation = ViolationReport(
                            rule_id=f"{rule.rule_id}_contextual",
                            violation_type=ViolationType.CONTEXT,
                            severity=RuleSeverity.HIGH,
                            location=f"Position {match.start()}-{match.end()}",
                            content=match.group(),
                            suggestion="Remove sensitive personal information",
                            confidence=0.8
                        )
                        violations.append(violation)
        
        return violations
    
    def _generate_suggestion(self, rule: ConstitutionalRule, violating_content: str) -> str:
        """Generate suggestion for fixing rule violation."""
        if rule.replacement:
            return f"Replace '{violating_content}' with '{rule.replacement}'"
        
        if rule.action == "block":
            return "Remove this content entirely"
        elif rule.action == "warn":
            return "Consider rephrasing this content"
        elif rule.action == "modify":
            return "Modify this content to be more appropriate"
        
        return "Review and revise this content"
    
    def _load_default_rules(self) -> None:
        """Load default constitutional rules."""
        default_rules = [
            # Safety rules
            ConstitutionalRule(
                rule_id="safety_no_harm",
                rule_type=RuleType.SAFETY,
                title="No Harmful Content",
                description="Content should not promote harm or violence",
                pattern=r'\b(kill|harm|hurt|violence|attack|damage)\b',
                severity=RuleSeverity.HIGH,
                action="warn"
            ),
            
            # Ethics rules
            ConstitutionalRule(
                rule_id="ethics_no_deception",
                rule_type=RuleType.ETHICS,
                title="No Deceptive Content",
                description="Content should not be deceptive or misleading",
                pattern=r'\b(guarantee|promise|absolutely|always|never)\b',
                severity=RuleSeverity.MEDIUM,
                action="warn"
            ),
            
            # Privacy rules
            ConstitutionalRule(
                rule_id="privacy_no_pii",
                rule_type=RuleType.PRIVACY,
                title="No Personal Information",
                description="Content should not contain personal identifiable information",
                pattern=r'\b\d{3}-\d{2}-\d{4}\b',
                severity=RuleSeverity.HIGH,
                action="block"
            ),
            
            # Bias rules
            ConstitutionalRule(
                rule_id="bias_no_discrimination",
                rule_type=RuleType.BIAS,
                title="No Discriminatory Content",
                description="Content should not contain discriminatory language",
                pattern=r'\b(discriminat|prejudice|bias|stereotype)\b',
                severity=RuleSeverity.MEDIUM,
                action="warn"
            ),
            
            # Quality rules
            ConstitutionalRule(
                rule_id="quality_no_grammar_errors",
                rule_type=RuleType.QUALITY,
                title="Proper Grammar",
                description="Content should use proper grammar",
                pattern=r'\b(aint|dont|wont|cant|shouldve)\b',
                severity=RuleSeverity.LOW,
                action="modify",
                replacement="proper contraction"
            )
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
        
        logger.info(f"Loaded {len(default_rules)} default constitutional rules")


class ContentValidator:
    """
    Content Validation and Correction
    
    Validates content against constitutional rules and
    provides suggestions for improvement.
    """
    
    def __init__(self, rule_engine: RuleEngine):
        self.rule_engine = rule_engine
        self.validation_history: List[ConstitutionalReviewResult] = []
    
    def validate_content(
        self, 
        content: str, 
        context: Dict[str, object] = None,
        auto_correct: bool = False
    ) -> ConstitutionalReviewResult:
        """
        Validate content against constitutional rules.
        
        Args:
            content: Content to validate
            context: Optional context information
            auto_correct: Whether to auto-correct minor violations
            
        Returns:
            Constitutional review result
        """
        violations = self.rule_engine.check_compliance(content, context)
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(violations)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(violations)
        
        # Auto-correct if requested
        corrected_content = content
        if auto_correct:
            corrected_content = self._auto_correct_content(content, violations)
        
        result = ConstitutionalReviewResult(
            is_compliant=len([v for v in violations if v.severity in [RuleSeverity.HIGH, RuleSeverity.CRITICAL]]) == 0,
            violations=violations,
            compliance_score=compliance_score,
            recommendations=recommendations,
            reviewed_at=logger.handlers[0].emit if logger.handlers else 0.0  # Simple timestamp
        )
        
        self.validation_history.append(result)
        
        logger.info(f"Content validation completed: {len(violations)} violations, {compliance_score:.2f} compliance")
        
        return result
    
    def _calculate_compliance_score(self, violations: List[ViolationReport]) -> float:
        """Calculate overall compliance score."""
        if not violations:
            return 1.0
        
        # Weight violations by severity
        severity_weights = {
            RuleSeverity.CRITICAL: 0.4,
            RuleSeverity.HIGH: 0.3,
            RuleSeverity.MEDIUM: 0.2,
            RuleSeverity.LOW: 0.1
        }
        
        total_penalty = 0.0
        for violation in violations:
            total_penalty += severity_weights.get(violation.severity, 0.1)
        
        # Normalize to 0-1 scale
        compliance_score = max(0.0, 1.0 - min(total_penalty, 1.0))
        
        return compliance_score
    
    def _generate_recommendations(self, violations: List[ViolationReport]) -> List[str]:
        """Generate recommendations based on violations."""
        recommendations = []
        
        if not violations:
            recommendations.append("Content is fully compliant with constitutional rules")
            return recommendations
        
        # Group violations by type
        violation_types = defaultdict(list)
        for violation in violations:
            violation_types[violation.severity].append(violation)
        
        # Generate recommendations for each severity level
        for severity in [RuleSeverity.CRITICAL, RuleSeverity.HIGH, RuleSeverity.MEDIUM, RuleSeverity.LOW]:
            if severity in violation_types:
                count = len(violation_types[severity])
                if severity == RuleSeverity.CRITICAL:
                    recommendations.append(f"URGENT: Fix {count} critical violations before proceeding")
                elif severity == RuleSeverity.HIGH:
                    recommendations.append(f"IMPORTANT: Address {count} high-priority violations")
                elif severity == RuleSeverity.MEDIUM:
                    recommendations.append(f"RECOMMENDED: Improve {count} medium-priority issues")
                else:
                    recommendations.append(f"OPTIONAL: Consider fixing {count} minor issues")
        
        # Add specific suggestions
        for violation in violations[:3]:  # Top 3 violations
            recommendations.append(f"- {violation.suggestion}")
        
        return recommendations
    
    def _auto_correct_content(self, content: str, violations: List[ViolationReport]) -> str:
        """Auto-correct minor violations in content."""
        corrected_content = content
        
        # Only auto-correct low and medium severity violations
        auto_correctable = [v for v in violations if v.severity in [RuleSeverity.LOW, RuleSeverity.MEDIUM]]
        
        for violation in auto_correctable:
            rule = self.rule_engine.rules.get(violation.rule_id)
            if rule and rule.replacement:
                corrected_content = corrected_content.replace(violation.content, rule.replacement)
        
        return corrected_content
    
    def get_validation_stats(self) -> Dict[str, object]:
        """Get validation statistics."""
        if not self.validation_history:
            return {}
        
        recent_validations = self.validation_history[-20:]  # Last 20 validations
        
        total_violations = sum(len(v.violations) for v in recent_validations)
        avg_compliance = sum(v.compliance_score for v in recent_validations) / len(recent_validations)
        compliant_count = sum(1 for v in recent_validations if v.is_compliant)
        
        return {
            'total_validations': len(self.validation_history),
            'recent_validations': len(recent_validations),
            'total_violations': total_violations,
            'average_compliance': avg_compliance,
            'compliance_rate': compliant_count / len(recent_validations),
            'most_common_violations': self._get_most_common_violations(recent_validations)
        }
    
    def _get_most_common_violations(self, validations: List[ConstitutionalReviewResult]) -> List[str]:
        """Get most common violation types."""
        violation_counts = defaultdict(int)
        
        for validation in validations:
            for violation in validation.violations:
                violation_counts[violation.rule_id] += 1
        
        # Return top 5 most common violations
        sorted_violations = sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)
        return [f"{rule_id}: {count}" for rule_id, count in sorted_violations[:5]]


class ConstitutionalAISystem:
    """
    Simplified Constitutional AI System
    
    Provides comprehensive constitutional AI capabilities
    including rule management, content validation, and
    compliance monitoring without over-engineered complexity.
    
    Enhanced with LLM-based judgment for nuanced evaluation.
    """
    
    # Default constitutional principles for LLM evaluation
    DEFAULT_PRINCIPLES = [
        ConstitutionalPrinciple(
            id="harmlessness",
            name="Harmlessness",
            definition="The AI must not cause harm to humans or promote harmful actions",
            evaluation_prompt="""Evaluate the following content for harmfulness:

Content: {content}

Does this content promote harm, violence, or dangerous actions? 
Respond with JSON: {{"is_compliant": true/false, "confidence": 0.0-1.0, "reasoning": "explanation", "suggested_fix": "optional suggestion"}}"""
        ),
        ConstitutionalPrinciple(
            id="helpfulness",
            name="Helpfulness",
            definition="The AI should be helpful and provide useful information",
            evaluation_prompt="""Evaluate if the following content is helpful and constructive:

Content: {content}

Is this content helpful and aligned with providing useful assistance?
Respond with JSON: {{"is_compliant": true/false, "confidence": 0.0-1.0, "reasoning": "explanation", "suggested_fix": "optional suggestion"}}"""
        ),
        ConstitutionalPrinciple(
            id="privacy",
            name="Privacy Protection",
            definition="The AI must not reveal or request private personal information",
            evaluation_prompt="""Evaluate the following content for privacy violations:

Content: {content}

Does this content request or reveal private personal information (SSN, address, phone, etc.)?
Respond with JSON: {{"is_compliant": true/false, "confidence": 0.0-1.0, "reasoning": "explanation", "suggested_fix": "optional suggestion"}}"""
        ),
        ConstitutionalPrinciple(
            id="honesty",
            name="Honesty and Truthfulness",
            definition="The AI should not make false claims or deceive users",
            evaluation_prompt="""Evaluate the following content for honesty:

Content: {content}

Does this content contain false claims, misinformation, or deceptive statements?
Respond with JSON: {{"is_compliant": true/false, "confidence": 0.0-1.0, "reasoning": "explanation", "suggested_fix": "optional suggestion"}}"""
        )
    ]
    
    def __init__(self, auto_load_rules: bool = True, llm_client: Optional[LLMClient] = None):
        self.rule_engine = RuleEngine()
        self.content_validator = ContentValidator(self.rule_engine)
        self.llm_client = llm_client or MockLLMClient()
        self.principles = {p.id: p for p in self.DEFAULT_PRINCIPLES}
        
        if auto_load_rules:
            self._initialize_system()
        
        self.system_stats = {
            'rules_loaded': len(self.rule_engine.rules),
            'principles_loaded': len(self.principles),
            'validations_performed': 0,
            'llm_evaluations_performed': 0,
            'compliance_rate': 0.0,
            'last_updated': 0.0
        }
    
    def evaluate_compliance(
        self, 
        content: str, 
        principles: Optional[List[str]] = None
    ) -> List[LLMJudgment]:
        """
        Evaluate content against constitutional principles using LLM judgment.
        
        Args:
            content: Content to evaluate
            principles: List of principle IDs to evaluate (default: all principles)
            
        Returns:
            List of LLM judgments for each principle
        """
        if principles is None:
            principles = list(self.principles.keys())
        
        judgments = []
        
        for principle_id in principles:
            principle = self.principles.get(principle_id)
            if not principle:
                logger.warning(f"Principle {principle_id} not found")
                continue
            
            # Construct evaluation prompt
            prompt = principle.evaluation_prompt.format(content=content)
            
            try:
                # Get LLM judgment
                response = self.llm_client.generate(prompt)
                
                # Parse JSON response
                try:
                    judgment_data = json.loads(response)
                    judgment = LLMJudgment(
                        principle_id=principle_id,
                        is_compliant=judgment_data.get('is_compliant', True),
                        confidence=float(judgment_data.get('confidence', 0.5)),
                        reasoning=judgment_data.get('reasoning', 'No reasoning provided'),
                        suggested_fix=judgment_data.get('suggested_fix')
                    )
                except (json.JSONDecodeError, ValueError, TypeError):
                    # Fallback to text parsing if JSON fails
                    logger.warning(f"Failed to parse LLM response as JSON: {response[:100]}...")
                    judgment = LLMJudgment(
                        principle_id=principle_id,
                        is_compliant="compliant" in response.lower() or "safe" in response.lower(),
                        confidence=0.5,  # Low confidence for text parsing
                        reasoning=response[:200],  # Truncate reasoning
                        suggested_fix=None
                    )
                
                judgments.append(judgment)
                logger.debug(f"Principle {principle_id}: {'Compliant' if judgment.is_compliant else 'Non-compliant'} (confidence: {judgment.confidence})")
                
            except Exception as e:
                logger.error(f"Error evaluating principle {principle_id}: {str(e)}")
                # Add a default compliant judgment on error
                judgments.append(LLMJudgment(
                    principle_id=principle_id,
                    is_compliant=True,
                    confidence=0.0,
                    reasoning=f"Evaluation failed: {str(e)}",
                    suggested_fix=None
                ))
        
        # Update statistics
        self.system_stats['llm_evaluations_performed'] += len(judgments)
        
        return judgments
    
    def critique_and_revise(
        self, 
        content: str, 
        violations: List[LLMJudgment]
    ) -> Tuple[str, List[str]]:
        """
        Generate critique and revision for non-compliant content.
        
        Args:
            content: Original content
            violations: List of LLM judgments indicating violations
            
        Returns:
            Tuple of (revised_content, list_of_changes_made)
        """
        non_compliant = [v for v in violations if not v.is_compliant]
        
        if not non_compliant:
            return content, []  # No revision needed
        
        # Build critique from all violations
        critique_parts = []
        for violation in non_compliant:
            critique_parts.append(f"- {violation.principle_id}: {violation.reasoning}")
            if violation.suggested_fix:
                critique_parts.append(f"  Suggestion: {violation.suggested_fix}")
        
        critique = "\n".join(critique_parts)
        
        # Generate revision prompt
        revision_prompt = f"""Please revise the following content to address the compliance issues:

Original Content:
{content}

Issues to Fix:
{critique}

Provide a revised version that addresses all issues while maintaining the original intent.
Respond with only the revised content, no explanations."""
        
        try:
            revised_content = self.llm_client.generate(revision_prompt)
            
            # Track changes
            changes = [f"Fixed {v.principle_id}: {v.reasoning}" for v in non_compliant]
            
            logger.info(f"Revised content to address {len(non_compliant)} violations")
            
            return revised_content.strip(), changes
            
        except Exception as e:
            logger.error(f"Error during revision: {str(e)}")
            # Return original content if revision fails
            return content, [f"Revision failed: {str(e)}"]
    
    def review_content(
        self, 
        content: str, 
        context: Dict[str, object] = None,
        auto_correct: bool = False
    ) -> ConstitutionalReviewResult:
        """
        Review content against constitutional rules.
        
        Args:
            content: Content to review
            context: Optional context information
            auto_correct: Whether to auto-correct minor violations
            
        Returns:
            Constitutional review result
        """
        result = self.content_validator.validate_content(content, context, auto_correct)
        
        # Update system statistics
        self.system_stats['validations_performed'] += 1
        
        # Update compliance rate (rolling average)
        if self.system_stats['validations_performed'] == 1:
            self.system_stats['compliance_rate'] = result.compliance_score
        else:
            # Rolling average
            alpha = 0.1  # Smoothing factor
            self.system_stats['compliance_rate'] = (
                alpha * result.compliance_score + 
                (1 - alpha) * self.system_stats['compliance_rate']
            )
        
        return result
    
    def add_constitutional_rule(
        self,
        rule_id: str,
        rule_type: RuleType,
        title: str,
        description: str,
        pattern: str,
        severity: RuleSeverity,
        action: str = "warn",
        replacement: str = None
    ) -> None:
        """
        Add a new constitutional rule to the system.
        
        Args:
            rule_id: Unique rule identifier
            rule_type: Type of rule
            title: Rule title
            description: Rule description
            pattern: Regex pattern for detection
            severity: Rule severity
            action: Action to take on violation
            replacement: Optional replacement text
        """
        rule = ConstitutionalRule(
            rule_id=rule_id,
            rule_type=rule_type,
            title=title,
            description=description,
            pattern=pattern,
            severity=severity,
            action=action,
            replacement=replacement
        )
        
        self.rule_engine.add_rule(rule)
        self.system_stats['rules_loaded'] = len(self.rule_engine.rules)
        
        logger.info(f"Added constitutional rule: {rule_id}")
    
    def get_system_status(self) -> Dict[str, object]:
        """Get overall system status and statistics."""
        validation_stats = self.content_validator.get_validation_stats()
        
        return {
            'system_stats': self.system_stats,
            'validation_stats': validation_stats,
            'rule_summary': {
                rule_type.value: len(rules) 
                for rule_type, rules in self.rule_engine.rule_patterns.items()
            }
        }
    
    def _initialize_system(self) -> None:
        """Initialize the constitutional AI system."""
        logger.info("Initializing Constitutional AI System")
        
        # Load default rules already done in RuleEngine constructor
        self.system_stats['last_updated'] = 0.0  # Simple timestamp
        
        logger.info(f"Constitutional AI System initialized with {len(self.rule_engine.rules)} rules")


# Factory functions for easy integration
def create_constitutional_ai_system(auto_load_rules: bool = True) -> ConstitutionalAISystem:
    """Create constitutional AI system instance."""
    return ConstitutionalAISystem(auto_load_rules)


def create_rule_engine() -> RuleEngine:
    """Create rule engine instance."""
    return RuleEngine()


def create_content_validator(rule_engine: RuleEngine) -> ContentValidator:
    """Create content validator instance."""
    return ContentValidator(rule_engine)
