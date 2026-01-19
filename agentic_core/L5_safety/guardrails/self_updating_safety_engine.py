from __future__ import annotations
"""
Self-Updating Safety Engine - L5 Safety Enhancement

Dynamically learns and updates safety rules based on detected threats.
Automatically adapts to new attack patterns and security vulnerabilities.
"""
import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from archives.location_violations.file_utils import safe_read_file, safe_write_file

Logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat Severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RuleType(Enum):
    """Types of safety rules."""
    PATTERN_MATCH = "pattern_match"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    BEHAVIORAL = "behavioral"
    CONTEXTUAL = "contextual"


@dataclass
class ThreatPattern:
    """Represents a detected threat pattern."""
    pattern_id: str
    pattern_type: RuleType
    pattern_signature: str
    ThreatLevel: ThreatLevel
    detection_count: int = 0
    false_positive_count: int = 0
    last_detected: Optional[datetime] = None
    examples: List[str] = field(default_factory=list)
    
    @property
    def confidence_score(self) -> float:
        """Calculate confidence score for this pattern."""
        total = self.detection_count + self.false_positive_count
        if total == 0:
            return 0.5
        return self.detection_count / total


@dataclass
class SafetyRule:
    """Represents a safety rule."""
    rule_id: str
    RuleType: RuleType
    pattern: str
    description: str
    ThreatLevel: ThreatLevel
    enabled: bool = True
    auto_generated: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def matches(self, text: str) -> bool:
        """Check if text matches this rule."""
        if not self.enabled:
            return False
        
        if self.RuleType == RuleType.PATTERN_MATCH:
            return bool(re.search(self.pattern, text, re.IGNORECASE))
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary."""
        return {
            'rule_id': self.rule_id,
            'RuleType': self.RuleType.value,
            'pattern': self.pattern,
            'description': self.description,
            'ThreatLevel': self.ThreatLevel.value,
            'enabled': self.enabled,
            'auto_generated': self.auto_generated,
            'created_at': self.created_at.isoformat(),
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'trigger_count': self.trigger_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SafetyRule':
        """Create rule from dictionary."""
        return cls(
            rule_id=data['rule_id'],
            RuleType=RuleType(data['RuleType']),
            pattern=data['pattern'],
            description=data['description'],
            ThreatLevel=ThreatLevel(data['ThreatLevel']),
            enabled=data.get('enabled', True),
            auto_generated=data.get('auto_generated', False),
            created_at=datetime.fromisoformat(data['created_at']),
            last_triggered=datetime.fromisoformat(data['last_triggered']) if data.get('last_triggered') else None,
            trigger_count=data.get('trigger_count', 0)
        )


@dataclass
class ThreatDetection:
    """Result of threat detection."""
    detected: bool
    ThreatLevel: ThreatLevel
    matched_rules: List[SafetyRule]
    confidence: float
    recommendations: List[str]


class SelfUpdatingSafetyEngine:
    """
    Safety engine that learns and adapts to new threats.
    
    Features:
    - Automatic threat pattern detection
    - Dynamic rule generation
    - False positive learning
    - Threat Severity escalation
    - Rule effectiveness tracking
    """
    
    def __init__(self, rules_storage_path: Optional[str] = None):
        """Initialize the self-updating safety engine."""
        self.rules_storage_path = rules_storage_path or os.path.join(
            os.getcwd(), ".canon_memory", "safety_rules.json"
        )
        
        self.rules: Dict[str, SafetyRule] = {}
        self.threat_patterns: Dict[str, ThreatPattern] = {}
        self.detection_history: List[Dict[str, Any]] = []
        self.false_positive_feedback: Dict[str, int] = {}
        
        self._initialize_base_rules()
        self._load_rules()
        
        Logger.info("Self-Updating Safety Engine initialized")
    
    def _initialize_base_rules(self):
        """Initialize base safety rules."""
        base_rules = [
            SafetyRule(
                rule_id="base_001",
                RuleType=RuleType.PATTERN_MATCH,
                pattern=r"(?i)(api[_-]?key|secret[_-]?key|password|token)\s*[=:]\s*['\"][^'\"]{8,}['\"]",
                description="Hardcoded secrets detection",
                ThreatLevel=ThreatLevel.CRITICAL,
                auto_generated=False
            ),
            SafetyRule(
                rule_id="base_002",
                RuleType=RuleType.PATTERN_MATCH,
                pattern=r"(?i)eval\s*\(|exec\s*\(",
                description="Dangerous code execution",
                ThreatLevel=ThreatLevel.HIGH,
                auto_generated=False
            ),
            SafetyRule(
                rule_id="base_003",
                RuleType=RuleType.PATTERN_MATCH,
                pattern=r"(?i)__import__\s*\(\s*['\"]os['\"]|subprocess\.call",
                description="System command execution",
                ThreatLevel=ThreatLevel.HIGH,
                auto_generated=False
            ),
            SafetyRule(
                rule_id="base_004",
                RuleType=RuleType.PATTERN_MATCH,
                pattern=r"(?i)DROP\s+TABLE|DELETE\s+FROM.*WHERE\s+1\s*=\s*1",
                description="SQL injection patterns",
                ThreatLevel=ThreatLevel.CRITICAL,
                auto_generated=False
            ),
            SafetyRule(
                rule_id="base_005",
                RuleType=RuleType.PATTERN_MATCH,
                pattern=r"(?i)<script[^>]*>.*?</script>|javascript:",
                description="XSS attack patterns",
                ThreatLevel=ThreatLevel.HIGH,
                auto_generated=False
            ),
        ]
        
        for rule in base_rules:
            self.rules[rule.rule_id] = rule
    
    def _load_rules(self):
        """Load rules from storage."""
        if not os.path.exists(self.rules_storage_path):
            Logger.info("No existing rules found, using base rules only")
            return
        
        try:
            with open(self.rules_storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for rule_data in data.get('rules', []):
                if rule_data['auto_generated']:
                    rule = SafetyRule.from_dict(rule_data)
                    self.rules[rule.rule_id] = rule
            
            Logger.info(f"Loaded {len(self.rules)} safety rules")
        except Exception as e:
            Logger.error(f"Failed to load rules: {e}")
    
    def _save_rules(self):
        """Save rules to storage."""
        try:
            os.makedirs(os.path.dirname(self.rules_storage_path), exist_ok=True)
            
            data = {
                'rules': [rule.to_dict() for rule in self.rules.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.rules_storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            Logger.debug(f"Saved {len(self.rules)} rules")
        except Exception as e:
            Logger.error(f"Failed to save rules: {e}")
    
    async def detect_threats(self, text: str, context: Optional[Dict[str, Any]] = None) -> ThreatDetection:
        """
        Detect threats in text.
        
        Args:
            text: Text to analyze
            context: Optional context information
            
        Returns:
            Threat detection result
        """
        matched_rules = []
        max_threat_level = ThreatLevel.LOW
        
        for rule in self.rules.values():
            if rule.matches(text):
                matched_rules.append(rule)
                rule.trigger_count += 1
                rule.last_triggered = datetime.now()
                
                if self._compare_threat_levels(rule.ThreatLevel, max_threat_level) > 0:
                    max_threat_level = rule.ThreatLevel
        
        confidence = 0.0
        if matched_rules:
            confidence = sum(
                1.0 if not rule.auto_generated else 0.8
                for rule in matched_rules
            ) / len(matched_rules)
        
        recommendations = self._generate_recommendations(matched_rules)
        
        detection = ThreatDetection(
            detected=len(matched_rules) > 0,
            ThreatLevel=max_threat_level,
            matched_rules=matched_rules,
            confidence=confidence,
            recommendations=recommendations
        )
        
        self.detection_history.append({
            'timestamp': datetime.now().isoformat(),
            'detected': detection.detected,
            'ThreatLevel': detection.ThreatLevel.value,
            'rules_matched': len(matched_rules)
        })
        
        if detection.detected:
            await self._learn_from_detection(text, matched_rules)
        
        return detection
    
    async def _learn_from_detection(self, text: str, matched_rules: List[SafetyRule]):
        """Learn from a threat detection."""
        for rule in matched_rules:
            pattern_id = f"pattern_{rule.rule_id}"
            
            if pattern_id not in self.threat_patterns:
                self.threat_patterns[pattern_id] = ThreatPattern(
                    pattern_id=pattern_id,
                    pattern_type=rule.RuleType,
                    pattern_signature=rule.pattern,
                    ThreatLevel=rule.ThreatLevel
                )
            
            pattern = self.threat_patterns[pattern_id]
            pattern.detection_count += 1
            pattern.last_detected = datetime.now()
            
            if len(pattern.examples) < 5:
                pattern.examples.append(text[:200])
        
        await self._generate_new_rules_if_needed()
    
    async def _generate_new_rules_if_needed(self):
        """Generate new rules based on detected patterns."""
        for pattern in self.threat_patterns.values():
            if pattern.confidence_score < 0.7:
                continue
            
            if pattern.detection_count < 5:
                continue
            
            existing_rule_ids = {rule.rule_id for rule in self.rules.values()}
            new_rule_id = f"auto_{pattern.pattern_id}"
            
            if new_rule_id in existing_rule_ids:
                continue
            
            variations = self._generate_pattern_variations(pattern)
            
            for i, variation in enumerate(variations[:3]):
                rule_id = f"{new_rule_id}_v{i}"
                if rule_id not in existing_rule_ids:
                    new_rule = SafetyRule(
                        rule_id=rule_id,
                        RuleType=pattern.pattern_type,
                        pattern=variation,
                        description=f"Auto-generated rule from pattern {pattern.pattern_id}",
                        ThreatLevel=pattern.ThreatLevel,
                        auto_generated=True
                    )
                    
                    self.rules[rule_id] = new_rule
                    Logger.info(f"Generated new safety rule: {rule_id}")
        
        self._save_rules()
    
    def _generate_pattern_variations(self, pattern: ThreatPattern) -> List[str]:
        """Generate variations of a threat pattern."""
        base_pattern = pattern.pattern_signature
        variations = [base_pattern]
        
        if pattern.pattern_type == RuleType.PATTERN_MATCH:
            variations.append(base_pattern.replace(r"\s*", r"\s+"))
            variations.append(base_pattern.replace(r"['\"]", r"['\"`]"))
        
        return variations
    
    def report_false_positive(self, rule_id: str, text: str):
        """
        Report a false positive detection.
        
        Args:
            rule_id: Rule that triggered false positive
            text: Text that was incorrectly flagged
        """
        if rule_id not in self.rules:
            Logger.warning(f"Rule {rule_id} not found for false positive report")
            return
        
        self.false_positive_feedback[rule_id] = self.false_positive_feedback.get(rule_id, 0) + 1
        
        rule = self.rules[rule_id]
        
        pattern_id = f"pattern_{rule_id}"
        if pattern_id in self.threat_patterns:
            self.threat_patterns[pattern_id].false_positive_count += 1
        
        if self.false_positive_feedback[rule_id] >= 5:
            if rule.auto_generated:
                rule.enabled = False
                Logger.info(f"Disabled rule {rule_id} due to high false positive rate")
            else:
                Logger.warning(f"Base rule {rule_id} has high false positive rate")
        
        self._save_rules()
    
    def _compare_threat_levels(self, level1: ThreatLevel, level2: ThreatLevel) -> int:
        """Compare two threat levels."""
        order = {
            ThreatLevel.LOW: 1,
            ThreatLevel.MEDIUM: 2,
            ThreatLevel.HIGH: 3,
            ThreatLevel.CRITICAL: 4
        }
        return order[level1] - order[level2]
    
    def _generate_recommendations(self, matched_rules: List[SafetyRule]) -> List[str]:
        """Generate recommendations based on matched rules."""
        recommendations = []
        
        for rule in matched_rules:
            if rule.ThreatLevel == ThreatLevel.CRITICAL:
                recommendations.append(f"CRITICAL: {rule.description} - Immediate action required")
            elif rule.ThreatLevel == ThreatLevel.HIGH:
                recommendations.append(f"HIGH: {rule.description} - Review and fix urgently")
            elif rule.ThreatLevel == ThreatLevel.MEDIUM:
                recommendations.append(f"MEDIUM: {rule.description} - Should be addressed")
        
        return recommendations
    
    def escalate_threat_level(self, rule_id: str):
        """
        Escalate threat level for a rule.
        
        Args:
            rule_id: Rule to escalate
        """
        if rule_id not in self.rules:
            return
        
        rule = self.rules[rule_id]
        
        if rule.ThreatLevel == ThreatLevel.LOW:
            rule.ThreatLevel = ThreatLevel.MEDIUM
        elif rule.ThreatLevel == ThreatLevel.MEDIUM:
            rule.ThreatLevel = ThreatLevel.HIGH
        elif rule.ThreatLevel == ThreatLevel.HIGH:
            rule.ThreatLevel = ThreatLevel.CRITICAL
        
        Logger.info(f"Escalated threat level for rule {rule_id} to {rule.ThreatLevel.value}")
        self._save_rules()
    
    def get_rule_effectiveness(self) -> Dict[str, Any]:
        """Get effectiveness metrics for rules."""
        total_rules = len(self.rules)
        enabled_rules = sum(1 for rule in self.rules.values() if rule.enabled)
        auto_generated = sum(1 for rule in self.rules.values() if rule.auto_generated)
        
        total_triggers = sum(rule.trigger_count for rule in self.rules.values())
        
        most_triggered = sorted(
            self.rules.values(),
            key=lambda r: r.trigger_count,
            reverse=True
        )[:5]
        
        return {
            'total_rules': total_rules,
            'enabled_rules': enabled_rules,
            'auto_generated_rules': auto_generated,
            'total_triggers': total_triggers,
            'most_triggered_rules': [
                {
                    'rule_id': rule.rule_id,
                    'description': rule.description,
                    'trigger_count': rule.trigger_count,
                    'ThreatLevel': rule.ThreatLevel.value
                }
                for rule in most_triggered
            ],
            'false_positive_reports': sum(self.false_positive_feedback.values())
        }
    
    def get_threat_statistics(self) -> Dict[str, Any]:
        """Get threat detection statistics."""
        total_detections = len(self.detection_history)
        
        if total_detections == 0:
            return {
                'total_detections': 0,
                'threat_distribution': {},
                'detection_rate': 0.0
            }
        
        threat_counts = {}
        for detection in self.detection_history:
            level = detection['ThreatLevel']
            threat_counts[level] = threat_counts.get(level, 0) + 1
        
        detected_count = sum(1 for d in self.detection_history if d['detected'])
        
        return {
            'total_detections': total_detections,
            'threats_detected': detected_count,
            'detection_rate': detected_count / total_detections,
            'threat_distribution': threat_counts,
            'unique_patterns': len(self.threat_patterns)
        }


def create_self_updating_safety_engine(rules_storage_path: Optional[str] = None) -> SelfUpdatingSafetyEngine:
    """Factory function to create self-updating safety engine."""
    return SelfUpdatingSafetyEngine(rules_storage_path=rules_storage_path)
