"""
Base Guard Implementation

Provides comprehensive guard mechanisms for prompt safety, validation,
and real-time protection across the L1-L5 architecture.
"""

from __future__ import annotations

import asyncio
import re
import time
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple
from enum import Enum
import json

from .policy_base import BasePolicy, PolicyResult, PolicyViolation


class GuardType(str, Enum):
    """Types of guards available."""
    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"
    CONTEXTUAL = "contextual"
    BEHAVIORAL = "behavioral"


class GuardAction(str, Enum):
    """Actions guards can take."""
    ALLOW = "allow"
    BLOCK = "block"
    MODIFY = "modify"
    WARN = "warn"
    QUARANTINE = "quarantine"
    ESCALATE = "escalate"


class GuardStatus(str, Enum):
    """Guard operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"


@dataclass
class GuardCheck:
    """Individual guard check result."""
    guard_name: str
    guard_type: GuardType
    passed: bool
    action: GuardAction
    confidence: float
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "guard_name": self.guard_name,
            "guard_type": self.guard_type.value,
            "passed": self.passed,
            "action": self.action.value,
            "confidence": self.confidence,
            "reason": self.reason,
            "details": self.details,
            "timestamp": self.timestamp,
        }


@dataclass
class GuardResult:
    """Combined result from multiple guard checks."""
    overall_status: GuardAction
    checks: List[GuardCheck] = field(default_factory=list)
    modified_content: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    
    def add_check(self, check: GuardCheck) -> None:
        """Add a guard check result."""
        self.checks.append(check)
        
        # Update overall status based on most restrictive action
        action_priority = {
            GuardAction.ALLOW: 0,
            GuardAction.WARN: 1,
            GuardAction.MODIFY: 2,
            GuardAction.QUARANTINE: 3,
            GuardAction.ESCALATE: 4,
            GuardAction.BLOCK: 5,
        }
        
        current_priority = action_priority.get(self.overall_status, 0)
        new_priority = action_priority.get(check.action, 0)
        
        if new_priority > current_priority:
            self.overall_status = check.action
    
    def get_failed_checks(self) -> List[GuardCheck]:
        """Get all failed guard checks."""
        return [check for check in self.checks if not check.passed]
    
    def get_blocked_checks(self) -> List[GuardCheck]:
        """Get all checks that resulted in blocking action."""
        return [check for check in self.checks if check.action == GuardAction.BLOCK]


class BaseGuard(ABC):
    """Base class for all prompt guards."""
    
    def __init__(self, name: str, guard_type: GuardType, 
                 action: GuardAction = GuardAction.BLOCK,
                 enabled: bool = True):
        self.name = name
        self.guard_type = guard_type
        self.action = action
        self.enabled = enabled
        self.status = GuardStatus.ACTIVE
        
        # Statistics
        self.check_count = 0
        self.block_count = 0
        self.warn_count = 0
        self.modify_count = 0
        self.last_checked: Optional[float] = None
        
        # Configuration
        self.config: Dict[str, Any] = {}
        self.thresholds: Dict[str, float] = {}
        self.exceptions: Set[str] = set()
    
    @abstractmethod
    def check(self, content: str, context: Optional[Dict[str, Any]] = None) -> GuardCheck:
        """Check content against this guard."""
        pass
    
    def is_enabled(self) -> bool:
        """Check if guard is enabled."""
        return self.enabled and self.status == GuardStatus.ACTIVE
    
    def enable(self) -> None:
        """Enable the guard."""
        self.enabled = True
        self.status = GuardStatus.ACTIVE
    
    def disable(self) -> None:
        """Disable the guard."""
        self.enabled = True
        self.status = GuardStatus.INACTIVE
    
    def add_exception(self, pattern: str) -> None:
        """Add an exception pattern."""
        self.exceptions.add(pattern)
    
    def remove_exception(self, pattern: str) -> None:
        """Remove an exception pattern."""
        self.exceptions.discard(pattern)
    
    def is_exception(self, content: str) -> bool:
        """Check if content matches any exception pattern."""
        for pattern in self.exceptions:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def update_config(self, **kwargs) -> None:
        """Update guard configuration."""
        self.config.update(kwargs)
    
    def set_threshold(self, name: str, value: float) -> None:
        """Set a threshold value."""
        self.thresholds[name] = value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get guard statistics."""
        return {
            "name": self.name,
            "guard_type": self.guard_type.value,
            "action": self.action.value,
            "enabled": self.enabled,
            "status": self.status.value,
            "check_count": self.check_count,
            "block_count": self.block_count,
            "warn_count": self.warn_count,
            "modify_count": self.modify_count,
            "block_rate": self.block_count / max(self.check_count, 1),
            "last_checked": self.last_checked,
        }


class ToxicityGuard(BaseGuard):
    """Guard for detecting toxic content."""
    
    def __init__(self, name: str = "toxicity_guard"):
        super().__init__(name, GuardType.INPUT, GuardAction.BLOCK)
        
        # Toxic content patterns
        self.toxic_patterns = [
            r'\b(toxic|poisonous|harmful|dangerous)\b',
            r'\b(hate|despise|loathe|detest)\b',
            r'\b(kill|murder|harm|injure|hurt)\b',
            r'\b(stupid|idiot|moron|retard)\b',
            r'\b(racist|sexist|homophobic|bigot)\b',
        ]
        
        self.set_threshold("toxicity_threshold", 0.7)
        self.config.update({
            "max_toxic_matches": 2,
            "case_sensitive": False,
        })
    
    def check(self, content: str, context: Optional[Dict[str, Any]] = None) -> GuardCheck:
        """Check content for toxicity."""
        self.check_count += 1
        self.last_checked = time.time()
        
        if not self.enabled or self.is_exception(content):
            return GuardCheck(
                guard_name=self.name,
                guard_type=self.guard_type,
                passed=True,
                action=GuardAction.ALLOW,
                confidence=1.0,
                reason="Guard disabled or content matches exception",
            )
        
        # Count toxic pattern matches
        matches = 0
        matched_patterns = []
        
        for pattern in self.toxic_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                matches += 1
                matched_patterns.append(pattern)
        
        # Calculate toxicity score
        toxicity_score = min(matches / len(self.toxic_patterns), 1.0)
        threshold = self.thresholds.get("toxicity_threshold", 0.7)
        max_matches = self.config.get("max_toxic_matches", 2)
        
        passed = toxicity_score < threshold and matches <= max_matches
        
        if not passed:
            self.block_count += 1
            action = self.action
        else:
            action = GuardAction.ALLOW
        
        return GuardCheck(
            guard_name=self.name,
            guard_type=self.guard_type,
            passed=passed,
            action=action,
            confidence=1.0 - toxicity_score,
            reason=f"Toxicity score: {toxicity_score:.2f}, Matches: {matches}",
            details={
                "toxicity_score": toxicity_score,
                "matches": matches,
                "matched_patterns": matched_patterns,
                "threshold": threshold,
            },
        )


class LengthGuard(BaseGuard):
    """Guard for content length validation."""
    
    def __init__(self, name: str = "length_guard"):
        super().__init__(name, GuardType.INPUT, GuardAction.WARN)
        
        self.set_threshold("min_length", 1)
        self.set_threshold("max_length", 10000)
        self.config.update({
            "strict_mode": False,
        })
    
    def check(self, content: str, context: Optional[Dict[str, Any]] = None) -> GuardCheck:
        """Check content length."""
        self.check_count += 1
        self.last_checked = time.time()
        
        if not self.enabled or self.is_exception(content):
            return GuardCheck(
                guard_name=self.name,
                guard_type=self.guard_type,
                passed=True,
                action=GuardAction.ALLOW,
                confidence=1.0,
                reason="Guard disabled or content matches exception",
            )
        
        content_length = len(content)
        min_length = int(self.thresholds.get("min_length", 1))
        max_length = int(self.thresholds.get("max_length", 10000))
        strict_mode = self.config.get("strict_mode", False)
        
        passed = min_length <= content_length <= max_length
        
        if not passed:
            if strict_mode:
                self.block_count += 1
                action = GuardAction.BLOCK
            else:
                self.warn_count += 1
                action = GuardAction.WARN
        else:
            action = GuardAction.ALLOW
        
        reason = f"Length: {content_length} (allowed: {min_length}-{max_length})"
        
        return GuardCheck(
            guard_name=self.name,
            guard_type=self.guard_type,
            passed=passed,
            action=action,
            confidence=1.0,
            reason=reason,
            details={
                "content_length": content_length,
                "min_length": min_length,
                "max_length": max_length,
                "strict_mode": strict_mode,
            },
        )


class RepetitionGuard(BaseGuard):
    """Guard for detecting excessive repetition."""
    
    def __init__(self, name: str = "repetition_guard"):
        super().__init__(name, GuardType.INPUT, GuardAction.WARN)
        
        self.set_threshold("repetition_threshold", 0.3)
        self.set_threshold("min_repeated_chars", 3)
        self.config.update({
            "check_words": True,
            "check_chars": True,
        })
    
    def check(self, content: str, context: Optional[Dict[str, Any]] = None) -> GuardCheck:
        """Check for excessive repetition."""
        self.check_count += 1
        self.last_checked = time.time()
        
        if not self.enabled or self.is_exception(content):
            return GuardCheck(
                guard_name=self.name,
                guard_type=self.guard_type,
                passed=True,
                action=GuardAction.ALLOW,
                confidence=1.0,
                reason="Guard disabled or content matches exception",
            )
        
        threshold = self.thresholds.get("repetition_threshold", 0.3)
        min_chars = int(self.thresholds.get("min_repeated_chars", 3))
        check_words = self.config.get("check_words", True)
        check_chars = self.config.get("check_chars", True)
        
        repetition_score = 0.0
        repetition_details = {}
        
        # Check character repetition
        if check_chars:
            char_repetitions = self._check_char_repetition(content, min_chars)
            repetition_details["char_repetitions"] = char_repetitions
            repetition_score = max(repetition_score, char_repetitions["score"])
        
        # Check word repetition
        if check_words:
            word_repetitions = self._check_word_repetition(content)
            repetition_details["word_repetitions"] = word_repetitions
            repetition_score = max(repetition_score, word_repetitions["score"])
        
        passed = repetition_score < threshold
        
        if not passed:
            self.warn_count += 1
            action = GuardAction.WARN
        else:
            action = GuardAction.ALLOW
        
        return GuardCheck(
            guard_name=self.name,
            guard_type=self.guard_type,
            passed=passed,
            action=action,
            confidence=1.0 - repetition_score,
            reason=f"Repetition score: {repetition_score:.2f}",
            details={
                "repetition_score": repetition_score,
                "threshold": threshold,
                **repetition_details,
            },
        )
    
    def _check_char_repetition(self, content: str, min_chars: int) -> Dict[str, Any]:
        """Check for character repetition."""
        # Find repeated character sequences
        repeated_patterns = []
        
        for i in range(len(content) - min_chars + 1):
            pattern = content[i:i + min_chars]
            if pattern * 3 in content:  # Pattern repeated 3+ times
                repeated_patterns.append(pattern)
        
        unique_patterns = set(repeated_patterns)
        score = len(unique_patterns) / max(len(set(content)), 1)
        
        return {
            "score": score,
            "repeated_patterns": list(unique_patterns),
            "pattern_count": len(unique_patterns),
        }
    
    def _check_word_repetition(self, content: str) -> Dict[str, Any]:
        """Check for word repetition."""
        words = content.lower().split()
        word_counts = {}
        
        for word in words:
            if len(word) > 2:  # Ignore short words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Find words repeated multiple times
        repeated_words = {word: count for word, count in word_counts.items() if count > 2}
        
        # Calculate repetition score
        total_words = len([w for w in words if len(w) > 2])
        repeated_word_count = sum(repeated_words.values())
        score = repeated_word_count / max(total_words, 1)
        
        return {
            "score": score,
            "repeated_words": repeated_words,
            "total_words": total_words,
            "repeated_count": repeated_word_count,
        }


class GuardEngine:
    """Engine for managing and executing guards."""
    
    def __init__(self):
        self.guards: Dict[str, BaseGuard] = {}
        self.guard_chains: Dict[str, List[str]] = {}
        
        # Initialize default guards
        self._initialize_default_guards()
    
    def _initialize_default_guards(self) -> None:
        """Initialize default guards."""
        self.register_guard(ToxicityGuard())
        self.register_guard(LengthGuard())
        self.register_guard(RepetitionGuard())
    
    def register_guard(self, guard: BaseGuard) -> None:
        """Register a guard."""
        self.guards[guard.name] = guard
    
    def unregister_guard(self, name: str) -> None:
        """Unregister a guard."""
        if name in self.guards:
            del self.guards[name]
    
    def get_guard(self, name: str) -> Optional[BaseGuard]:
        """Get guard by name."""
        return self.guards.get(name)
    
    def list_guards(self, guard_type: Optional[GuardType] = None) -> List[str]:
        """List registered guards, optionally filtered by type."""
        if guard_type:
            return [name for name, guard in self.guards.items() 
                   if guard.guard_type == guard_type]
        return list(self.guards.keys())
    
    def check_content(self, content: str, 
                      guard_names: Optional[List[str]] = None,
                      context: Optional[Dict[str, Any]] = None) -> GuardResult:
        """Check content against specified guards."""
        start_time = time.time()
        
        guards_to_check = guard_names or list(self.guards.keys())
        result = GuardResult(overall_status=GuardAction.ALLOW)
        
        for guard_name in guards_to_check:
            guard = self.get_guard(guard_name)
            if guard and guard.is_enabled():
                check = guard.check(content, context)
                result.add_check(check)
                
                # Update statistics
                if not check.passed:
                    if check.action == GuardAction.BLOCK:
                        guard.block_count += 1
                    elif check.action == GuardAction.WARN:
                        guard.warn_count += 1
                    elif check.action == GuardAction.MODIFY:
                        guard.modify_count += 1
        
        result.processing_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def check_content_async(self, content: str,
                                 guard_names: Optional[List[str]] = None,
                                 context: Optional[Dict[str, Any]] = None) -> GuardResult:
        """Check content asynchronously."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.check_content, content, guard_names, context
        )
    
    def create_guard_chain(self, chain_name: str, guard_names: List[str]) -> None:
        """Create a chain of guards to execute in order."""
        self.guard_chains[chain_name] = guard_names
    
    def execute_guard_chain(self, chain_name: str, content: str,
                           context: Optional[Dict[str, Any]] = None) -> GuardResult:
        """Execute a guard chain."""
        guard_names = self.guard_chains.get(chain_name)
        if not guard_names:
            raise ValueError(f"Guard chain '{chain_name}' not found")
        
        return self.check_content(content, guard_names, context)
    
    def get_guard_stats(self) -> Dict[str, Any]:
        """Get statistics for all guards."""
        return {
            "total_guards": len(self.guards),
            "active_guards": len([g for g in self.guards.values() if g.is_enabled()]),
            "guard_chains": len(self.guard_chains),
            "guard_details": {name: guard.get_stats() for name, guard in self.guards.items()},
        }


# Global guard engine
_guard_engine: Optional[GuardEngine] = None


def get_guard_engine() -> GuardEngine:
    """Get the global guard engine instance."""
    global _guard_engine
    if _guard_engine is None:
        _guard_engine = GuardEngine()
    return _guard_engine


def check_content(content: str, guard_names: Optional[List[str]] = None,
                 context: Optional[Dict[str, Any]] = None) -> GuardResult:
    """Check content using global guard engine."""
    return get_guard_engine().check_content(content, guard_names, context)


__all__ = [
    "BaseGuard",
    "ToxicityGuard",
    "LengthGuard",
    "RepetitionGuard",
    "GuardEngine",
    "GuardType",
    "GuardAction",
    "GuardStatus",
    "GuardCheck",
    "GuardResult",
    "get_guard_engine",
    "check_content",
]
