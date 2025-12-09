"""
Constitutional AI System - Rule-Based Content Validation
Ported from legacy_engines/constitutional_ai_system.py

Lightweight constitutional AI system that provides safety
and alignment without over-engineered complexity.
Focuses on rule-based validation, ethical guidelines,
and content compliance checking.
"""

import re
import logging
import time
from typing import Dict, List, object, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of constitutional rules"""
    SAFETY = "safety"
    ETHICS = "ethics"
    PRIVACY = "privacy"
    BIAS = "bias"
    LEGAL = "legal"
    QUALITY = "quality"
    COMPLIANCE = "compliance"


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


class RuleAction(Enum):
    """Actions to take on rule violation"""
    WARN = "warn"
    BLOCK = "block"
    MODIFY = "modify"
    LOG = "log"


@dataclass
class ConstitutionalRule:
    """Individual constitutional rule"""
    rule_id: str
    rule_type: RuleType
    title: str
    description: str
    pattern: str  # Regex pattern for detection
    severity: RuleSeverity
    action: RuleAction
    replacement: Optional[str] = None
    enabled: bool = True
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class ViolationReport:
    """Report of constitutional violation"""
    rule_id: str
    rule_type: RuleType
    violation_type: ViolationType
    severity: RuleSeverity
    action: RuleAction
    location: str  # Description of where violation occurred
    content: str  # The violating content
    suggestion: str  # How to fix the violation
    confidence: float
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class ConstitutionalReviewResult:
    """Result of constitutional review"""
    is_compliant: bool
    violations: List[ViolationReport]
    compliance_score: float
    recommendations: List[str]
    reviewed_at: float
    corrected_content: Optional[str] = None
    metadata: Dict[str, object] = field(default_factory=dict)


class RuleEngine:
    """
    basic Rule-Based Validation Engine
    
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
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a constitutional rule from the engine."""
        if rule_id in self.rules:
            rule = self.rules[rule_id]
            self.rule_patterns[rule.rule_type].remove(rule)
            del self.rules[rule_id]
            logger.debug(f"Removed constitutional rule: {rule_id}")
            return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[ConstitutionalRule]:
        """Get a rule by ID."""
        return self.rules.get(rule_id)
    
    def check_compliance(
        self, 
        content: str, 
        context: Optional[Dict[str, object]] = None,
        rule_types: Optional[List[RuleType]] = None
    ) -> List[ViolationReport]:
        """
        Check content against constitutional rules.
        
        Args:
            content: Content to check
            context: Optional context for rule evaluation
            rule_types: Optional list of rule types to check
            
        Returns:
            List of violation reports
        """
        violations = []
        context = context or {}
        
        # Determine which rules to check
        rules_to_check = []
        if rule_types:
            for rt in rule_types:
                rules_to_check.extend(self.rule_patterns.get(rt, []))
        else:
            rules_to_check = list(self.rules.values())
        
        for rule in rules_to_check:
            if not rule.enabled:
                continue
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
        context: Dict[str, object]
    ) -> List[ViolationReport]:
        """Check content against a specific rule."""
        violations = []
        
        try:
            # Pattern matching
            matches = re.finditer(rule.pattern, content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                violation = ViolationReport(
                    rule_id=rule.rule_id,
                    rule_type=rule.rule_type,
                    violation_type=ViolationType.CONTENT,
                    severity=rule.severity,
                    action=rule.action,
                    location=f"Position {match.start()}-{match.end()}",
                    content=match.group(),
                    suggestion=self._generate_suggestion(rule, match.group()),
                    confidence=0.9  # High confidence for pattern matches
                )
                violations.append(violation)
            
            # Contextual checks for certain rule types
            if rule.rule_type in [RuleType.SAFETY, RuleType.ETHICS, RuleType.PRIVACY]:
                context_violations = self._check_contextual_rules(content, rule, context)
                violations.extend(context_violations)
        
        except re.error as e:
            logger.error("Regex error in rule {rule.rule_id}: %s", e)
        
        return violations
    
    def _check_contextual_rules(
        self, 
        content: str, 
        rule: ConstitutionalRule, 
        context: Dict[str, object]
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
                    (r'\b\d{3}-\d{2}-\d{4}\b', "SSN detected"),
                    (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', "Credit card detected")
                ]
                
                for pattern, description in personal_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        violation = ViolationReport(
                            rule_id=f"{rule.rule_id}_contextual",
                            rule_type=rule.rule_type,
                            violation_type=ViolationType.CONTEXT,
                            severity=RuleSeverity.HIGH,
                            action=RuleAction.BLOCK,
                            location=f"Position {match.start()}-{match.end()}",
                            content=match.group(),
                            suggestion=f"Remove sensitive personal information: {description}",
                            confidence=0.85
                        )
                        violations.append(violation)
        
        return violations
    
    def _generate_suggestion(self, rule: ConstitutionalRule, violating_content: str) -> str:
        """Generate suggestion for fixing rule violation."""
        if rule.replacement:
            return f"Replace '{violating_content}' with '{rule.replacement}'"
        
        if rule.action == RuleAction.BLOCK:
            return "Remove this content entirely"
        elif rule.action == RuleAction.WARN:
            return "Consider rephrasing this content"
        elif rule.action == RuleAction.MODIFY:
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
                pattern=r'\b(kill|harm|hurt|violence|attack|damage|destroy|murder)\b',
                severity=RuleSeverity.HIGH,
                action=RuleAction.WARN
            ),
            ConstitutionalRule(
                rule_id="safety_no_threats",
                rule_type=RuleType.SAFETY,
                title="No Threatening Content",
                description="Content should not contain threats",
                pattern=r'\b(threaten|threat|intimidate|terrorize)\b',
                severity=RuleSeverity.CRITICAL,
                action=RuleAction.BLOCK
            ),
            
            # Ethics rules
            ConstitutionalRule(
                rule_id="ethics_no_deception",
                rule_type=RuleType.ETHICS,
                title="No Deceptive Content",
                description="Content should not be deceptive or misleading",
                pattern=r'\b(guarantee|promise|absolutely|always|never|100%)\b',
                severity=RuleSeverity.MEDIUM,
                action=RuleAction.WARN
            ),
            ConstitutionalRule(
                rule_id="ethics_no_manipulation",
                rule_type=RuleType.ETHICS,
                title="No Manipulative Content",
                description="Content should not manipulate or exploit",
                pattern=r'\b(manipulate|exploit|deceive|trick|scam)\b',
                severity=RuleSeverity.HIGH,
                action=RuleAction.WARN
            ),
            
            # Privacy rules
            ConstitutionalRule(
                rule_id="privacy_no_ssn",
                rule_type=RuleType.PRIVACY,
                title="No Social Security Numbers",
                description="Content should not contain SSNs",
                pattern=r'\b\d{3}-\d{2}-\d{4}\b',
                severity=RuleSeverity.CRITICAL,
                action=RuleAction.BLOCK
            ),
            ConstitutionalRule(
                rule_id="privacy_no_credit_card",
                rule_type=RuleType.PRIVACY,
                title="No Credit Card Numbers",
                description="Content should not contain credit card numbers",
                pattern=r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                severity=RuleSeverity.CRITICAL,
                action=RuleAction.BLOCK
            ),
            
            # Quality rules
            ConstitutionalRule(
                rule_id="quality_no_profanity",
                rule_type=RuleType.QUALITY,
                title="No Profanity",
                description="Content should not contain profanity",
                pattern=r'\b(damn|hell|crap)\b',
                severity=RuleSeverity.LOW,
                action=RuleAction.WARN
            ),
            ConstitutionalRule(
                rule_id="quality_grammar",
                rule_type=RuleType.QUALITY,
                title="Proper Grammar",
                description="Content should use proper grammar",
                pattern=r'\b(aint|dont|wont|cant|shouldve|couldve|wouldve)\b',
                severity=RuleSeverity.LOW,
                action=RuleAction.MODIFY,
                replacement="proper contraction"
            ),
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
    
    def __init__(self, rule_engine: Optional[RuleEngine] = None):
        self.rule_engine = rule_engine or RuleEngine()
        self.validation_history: List[ConstitutionalReviewResult] = []
    
    def validate_content(
        self, 
        content: str, 
        context: Optional[Dict[str, object]] = None,
        auto_correct: bool = False,
        rule_types: Optional[List[RuleType]] = None
    ) -> ConstitutionalReviewResult:
        """
        Validate content against constitutional rules.
        
        Args:
            content: Content to validate
            context: Optional context information
            auto_correct: Whether to auto-correct minor violations
            rule_types: Optional list of rule types to check
            
        Returns:
            Constitutional review result
        """
        violations = self.rule_engine.check_compliance(content, context, rule_types)
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(violations)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(violations)
        
        # Auto-correct if requested
        corrected_content = None
        if auto_correct:
            corrected_content = self._auto_correct_content(content, violations)
        
        # Determine compliance (no HIGH or CRITICAL violations)
        is_compliant = not any(
            v.severity in [RuleSeverity.HIGH, RuleSeverity.CRITICAL] 
            for v in violations
        )
        
        result = ConstitutionalReviewResult(
            is_compliant=is_compliant,
            violations=violations,
            compliance_score=compliance_score,
            recommendations=recommendations,
            reviewed_at=time.time(),
            corrected_content=corrected_content,
            metadata={
                "auto_corrected": auto_correct and corrected_content is not None,
                "rule_types_checked": [rt.value for rt in rule_types] if rule_types else "all"
            }
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
        
        return round(compliance_score, 3)
    
    def _generate_recommendations(self, violations: List[ViolationReport]) -> List[str]:
        """Generate recommendations based on violations."""
        recommendations = []
        
        if not violations:
            recommendations.append("Content is fully compliant with constitutional rules")
            return recommendations
        
        # Group violations by severity
        violation_by_severity: Dict[RuleSeverity, List[ViolationReport]] = defaultdict(list)
        for violation in violations:
            violation_by_severity[violation.severity].append(violation)
        
        # Generate recommendations for each severity level
        for severity in [RuleSeverity.CRITICAL, RuleSeverity.HIGH, RuleSeverity.MEDIUM, RuleSeverity.LOW]:
            if severity in violation_by_severity:
                count = len(violation_by_severity[severity])
                if severity == RuleSeverity.CRITICAL:
                    recommendations.append(f"URGENT: Fix {count} critical violations before proceeding")
                elif severity == RuleSeverity.HIGH:
                    recommendations.append(f"IMPORTANT: Address {count} high-priority violations")
                elif severity == RuleSeverity.MEDIUM:
                    recommendations.append(f"RECOMMENDED: Improve {count} medium-priority issues")
                else:
                    recommendations.append(f"OPTIONAL: Consider fixing {count} minor issues")
        
        # Add specific suggestions for top violations
        for violation in violations[:3]:
            recommendations.append(f"- {violation.suggestion}")
        
        return recommendations
    
    def _auto_correct_content(self, content: str, violations: List[ViolationReport]) -> str:
        """Auto-correct minor violations in content."""
        corrected_content = content
        
        # Only auto-correct LOW and MEDIUM severity violations with MODIFY action
        auto_correctable = [
            v for v in violations 
            if v.severity in [RuleSeverity.LOW, RuleSeverity.MEDIUM] 
            and v.action == RuleAction.MODIFY
        ]
        
        for violation in auto_correctable:
            rule = self.rule_engine.get_rule(violation.rule_id)
            if rule and rule.replacement:
                corrected_content = corrected_content.replace(violation.content, rule.replacement)
        
        return corrected_content
    
    def get_validation_stats(self) -> Dict[str, object]:
        """Get validation statistics."""
        if not self.validation_history:
            return {}
        
        recent_validations = self.validation_history[-20:]
        
        total_violations = sum(len(v.violations) for v in recent_validations)
        avg_compliance = sum(v.compliance_score for v in recent_validations) / len(recent_validations)
        compliant_count = sum(1 for v in recent_validations if v.is_compliant)
        
        return {
            'total_validations': len(self.validation_history),
            'recent_validations': len(recent_validations),
            'total_violations': total_violations,
            'average_compliance': round(avg_compliance, 3),
            'compliance_rate': round(compliant_count / len(recent_validations), 3),
            'most_common_violations': self._get_most_common_violations(recent_validations)
        }
    
    def _get_most_common_violations(self, validations: List[ConstitutionalReviewResult]) -> List[str]:
        """Get most common violation types."""
        violation_counts: Dict[str, int] = defaultdict(int)
        
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
    """
    
    def __init__(self, auto_load_rules: bool = True):
        self.rule_engine = RuleEngine() if auto_load_rules else RuleEngine()
        self.content_validator = ContentValidator(self.rule_engine)
        
        self.system_stats = {
            'rules_loaded': len(self.rule_engine.rules),
            'validations_performed': 0,
            'compliance_rate': 0.0,
            'last_updated': time.time()
        }
    
    def review_content(
        self, 
        content: str, 
        context: Optional[Dict[str, object]] = None,
        auto_correct: bool = False,
        rule_types: Optional[List[RuleType]] = None
    ) -> ConstitutionalReviewResult:
        """
        Review content against constitutional rules.
        
        Args:
            content: Content to review
            context: Optional context information
            auto_correct: Whether to auto-correct minor violations
            rule_types: Optional list of rule types to check
            
        Returns:
            Constitutional review result
        """
        result = self.content_validator.validate_content(
            content, context, auto_correct, rule_types
        )
        
        # Update system statistics
        self.system_stats['validations_performed'] += 1
        
        # Update compliance rate (rolling average)
        if self.system_stats['validations_performed'] == 1:
            self.system_stats['compliance_rate'] = result.compliance_score
        else:
            alpha = 0.1  # Smoothing factor
            self.system_stats['compliance_rate'] = (
                alpha * result.compliance_score + 
                (1 - alpha) * self.system_stats['compliance_rate']
            )
        
        return result
    
    def add_rule(
        self,
        rule_id: str,
        rule_type: RuleType,
        title: str,
        description: str,
        pattern: str,
        severity: RuleSeverity,
        action: RuleAction = RuleAction.WARN,
        replacement: Optional[str] = None
    ) -> None:
        """Add a new constitutional rule to the system."""
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
        self.system_stats['last_updated'] = time.time()
        
        logger.info(f"Added constitutional rule: {rule_id}")
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a constitutional rule from the system."""
        result = self.rule_engine.remove_rule(rule_id)
        if result:
            self.system_stats['rules_loaded'] = len(self.rule_engine.rules)
            self.system_stats['last_updated'] = time.time()
        return result
    
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
    
    def get_rules_by_type(self, rule_type: RuleType) -> List[ConstitutionalRule]:
        """Get all rules of a specific type."""
        return self.rule_engine.rule_patterns.get(rule_type, [])
    
    def is_content_safe(self, content: str) -> bool:
        """Quick check if content is safe (no CRITICAL or HIGH violations)."""
        result = self.review_content(content)
        return result.is_compliant


# Factory functions
def create_constitutional_ai_system(auto_load_rules: bool = True) -> ConstitutionalAISystem:
    """Create constitutional AI system instance."""
    return ConstitutionalAISystem(auto_load_rules)


def create_rule_engine() -> RuleEngine:
    """Create rule engine instance."""
    return RuleEngine()


def create_content_validator(rule_engine: Optional[RuleEngine] = None) -> ContentValidator:
    """Create content validator instance."""
    return ContentValidator(rule_engine)


def review_content(
    content: str, 
    auto_correct: bool = False,
    rule_types: Optional[List[RuleType]] = None
) -> ConstitutionalReviewResult:
    """Convenience function to review content."""
    system = ConstitutionalAISystem()
    return system.review_content(content, auto_correct=auto_correct, rule_types=rule_types)
