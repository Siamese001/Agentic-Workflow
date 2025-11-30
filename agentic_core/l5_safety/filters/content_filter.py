"""
Content Filter Implementation for Safety Layer
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re


class FilterAction(Enum):
    """Actions to take when content is filtered"""
    ALLOW = "allow"
    BLOCK = "block"
    MODIFY = "modify"
    FLAG = "flag"


@dataclass
class FilterResult:
    """Result of content filtering"""
    action: FilterAction
    filtered_content: str
    violations: List[str]
    confidence: float
    timestamp: datetime
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ContentFilter:
    """Content filtering system for safety compliance"""
    
    def __init__(self):
        self.blocked_words: Set[str] = set()
        self.blocked_patterns: List[re.Pattern] = []
        self.allowed_domains: Set[str] = set()
        self.filter_rules: Dict[str, Dict[str, Any]] = {}
        self.violation_history: List[FilterResult] = []
        self.stats = {
            "total_filtered": 0,
            "blocked": 0,
            "modified": 0,
            "flagged": 0,
            "allowed": 0
        }
        self.created_at = datetime.now()
    
    def add_blocked_word(self, word: str):
        """Add a word to the blocked list"""
        self.blocked_words.add(word.lower())
    
    def add_blocked_pattern(self, pattern: str, flags: int = 0):
        """Add a regex pattern to the blocked list"""
        try:
            compiled_pattern = re.compile(pattern, flags)
            self.blocked_patterns.append(compiled_pattern)
        except re.error:
            pass  # Invalid regex pattern
    
    def add_allowed_domain(self, domain: str):
        """Add a domain to the allowed list"""
        self.allowed_domains.add(domain.lower())
    
    def add_filter_rule(self, rule_name: str, rule_config: Dict[str, Any]):
        """Add a custom filter rule"""
        self.filter_rules[rule_name] = rule_config
    
    def filter_content(self, content: str, context: Dict[str, Any] = None) -> FilterResult:
        """Filter content based on configured rules"""
        violations = []
        filtered_content = content
        max_confidence = 0.0
        
        # Check blocked words
        for word in self.blocked_words:
            if word.lower() in content.lower():
                violations.append(f"Blocked word detected: {word}")
                max_confidence = max(max_confidence, 0.8)
        
        # Check blocked patterns
        for pattern in self.blocked_patterns:
            if pattern.search(content):
                violations.append(f"Blocked pattern detected: {pattern.pattern}")
                max_confidence = max(max_confidence, 0.9)
        
        # Apply custom filter rules
        for rule_name, rule_config in self.filter_rules.items():
            rule_violations = self._apply_filter_rule(content, rule_name, rule_config)
            violations.extend(rule_violations)
            if rule_violations:
                max_confidence = max(max_confidence, rule_config.get("confidence", 0.7))
        
        # Determine action based on violations and confidence
        if violations:
            if max_confidence >= 0.8:
                action = FilterAction.BLOCK
                filtered_content = "[CONTENT BLOCKED]"
                self.stats["blocked"] += 1
            elif max_confidence >= 0.6:
                action = FilterAction.MODIFY
                filtered_content = self._modify_content(content, violations)
                self.stats["modified"] += 1
            else:
                action = FilterAction.FLAG
                self.stats["flagged"] += 1
        else:
            action = FilterAction.ALLOW
            self.stats["allowed"] += 1
        
        self.stats["total_filtered"] += 1
        
        result = FilterResult(
            action=action,
            filtered_content=filtered_content,
            violations=violations,
            confidence=max_confidence,
            timestamp=datetime.now()
        )
        
        self.violation_history.append(result)
        return result
    
    def _apply_filter_rule(self, content: str, rule_name: str, rule_config: Dict[str, Any]) -> List[str]:
        """Apply a custom filter rule"""
        violations = []
        rule_type = rule_config.get("type", "")
        
        if rule_type == "length":
            min_length = rule_config.get("min_length", 0)
            max_length = rule_config.get("max_length", float('inf'))
            
            if len(content) < min_length:
                violations.append(f"Content too short: {len(content)} < {min_length}")
            elif len(content) > max_length:
                violations.append(f"Content too long: {len(content)} > {max_length}")
        
        elif rule_type == "keywords":
            keywords = rule_config.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    violations.append(f"Keyword detected: {keyword}")
        
        elif rule_type == "personal_info":
            # Simple patterns for PII detection
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'\b\d{3}-\d{3}-\d{4}\b'
            
            if re.search(email_pattern, content):
                violations.append("Email address detected")
            if re.search(phone_pattern, content):
                violations.append("Phone number detected")
        
        return violations
    
    def _modify_content(self, content: str, violations: List[str]) -> str:
        """Modify content to remove violations"""
        modified = content
        
        # Replace blocked words with asterisks
        for word in self.blocked_words:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            modified = pattern.sub("*" * len(word), modified)
        
        # Replace blocked patterns with [REDACTED]
        for pattern in self.blocked_patterns:
            modified = pattern.sub("[REDACTED]", modified)
        
        return modified
    
    def is_domain_allowed(self, domain: str) -> bool:
        """Check if a domain is allowed"""
        return domain.lower() in self.allowed_domains
    
    def filter_url(self, url: str) -> FilterResult:
        """Filter a URL"""
        # Extract domain from URL (simple implementation)
        try:
            domain = url.split("//")[1].split("/")[0] if "//" in url else url.split("/")[0]
            
            if not self.is_domain_allowed(domain):
                return FilterResult(
                    action=FilterAction.BLOCK,
                    filtered_content="[URL BLOCKED]",
                    violations=[f"Domain not allowed: {domain}"],
                    confidence=1.0,
                    timestamp=datetime.now()
                )
            
            return FilterResult(
                action=FilterAction.ALLOW,
                filtered_content=url,
                violations=[],
                confidence=0.0,
                timestamp=datetime.now()
            )
            
        except Exception:
            return FilterResult(
                action=FilterAction.BLOCK,
                filtered_content="[URL BLOCKED]",
                violations=["Invalid URL format"],
                confidence=1.0,
                timestamp=datetime.now()
            )
    
    def get_violation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent violation history"""
        recent_violations = self.violation_history[-limit:]
        return [
            {
                "action": result.action.value,
                "violations": result.violations,
                "confidence": result.confidence,
                "timestamp": result.timestamp.isoformat()
            }
            for result in recent_violations
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get filtering statistics"""
        return {
            "stats": self.stats.copy(),
            "blocked_words_count": len(self.blocked_words),
            "blocked_patterns_count": len(self.blocked_patterns),
            "allowed_domains_count": len(self.allowed_domains),
            "custom_rules_count": len(self.filter_rules),
            "total_violations": len(self.violation_history),
            "created_at": self.created_at.isoformat()
        }
    
    def clear_history(self):
        """Clear violation history"""
        self.violation_history.clear()
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "total_filtered": 0,
            "blocked": 0,
            "modified": 0,
            "flagged": 0,
            "allowed": 0
        }
    
    def export_config(self) -> Dict[str, Any]:
        """Export filter configuration"""
        return {
            "blocked_words": list(self.blocked_words),
            "blocked_patterns": [p.pattern for p in self.blocked_patterns],
            "allowed_domains": list(self.allowed_domains),
            "filter_rules": self.filter_rules.copy(),
            "stats": self.get_stats()
        }
    
    def import_config(self, config: Dict[str, Any]) -> bool:
        """Import filter configuration"""
        try:
            if "blocked_words" in config:
                self.blocked_words = set(config["blocked_words"])
            
            if "blocked_patterns" in config:
                self.blocked_patterns = []
                for pattern_str in config["blocked_patterns"]:
                    try:
                        self.blocked_patterns.append(re.compile(pattern_str))
                    except re.error:
                        continue
            
            if "allowed_domains" in config:
                self.allowed_domains = set(config["allowed_domains"])
            
            if "filter_rules" in config:
                self.filter_rules = config["filter_rules"].copy()
            
            return True
            
        except Exception:
            return False
    
    def __str__(self):
        return f"ContentFilter(blocked_words={len(self.blocked_words)}, rules={len(self.filter_rules)})"
    
    def __repr__(self):
        return self.__str__()
