"""Safety Filters Enforcement - Enforces safety filters on content and operations.

This module provides safety filter enforcement for AI operations,
including content filtering, profanity detection, and harmful content blocking.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Set, Pattern
import logging
import re
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class FilterType(Enum):
    """Types of safety filters."""
    PROFANITY = "profanity"
    TOXICITY = "toxicity"
    VIOLENCE = "violence"
    HATE_SPEECH = "hate_speech"
    SELF_HARM = "self_harm"
    SEXUAL_CONTENT = "sexual_content"
    MISINFORMATION = "misinformation"
    ILLEGAL_CONTENT = "illegal_content"


class FilterAction(Enum):
    """Actions to take when filter is triggered."""
    BLOCK = "block"
    WARN = "warn"
    REDACT = "redact"
    FLAG = "flag"
    LOG = "log"


@dataclass
class SafetyFilter:
    """Definition of a safety filter."""
    id: str
    name: str
    filter_type: FilterType
    patterns: List[str]
    action: FilterAction
    enabled: bool = True
    severity: str = "medium"
    description: str = ""
    keywords: List[str] = field(default_factory=list)


@dataclass
class FilterMatch:
    """Record of a filter match."""
    filter_id: str
    filter_name: str
    filter_type: FilterType
    action: FilterAction
    matched_content: str
    position: Optional[int] = None
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FilterResult:
    """Result of safety filtering."""
    safe: bool
    filtered_content: Optional[str] = None
    matches: List[FilterMatch] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    blocked_content: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyFiltersConfig:
    """Configuration for safety filters enforcement."""
    enabled_filters: List[FilterType] = field(default_factory=lambda: [
        FilterType.PROFANITY, FilterType.TOXICITY, FilterType.VIOLENCE
    ])
    default_action: FilterAction = FilterAction.WARN
    strict_mode: bool = False
    auto_redact: bool = True
    custom_filters: List[SafetyFilter] = field(default_factory=list)
    allowed_domains: Set[str] = field(default_factory=set)
    log_level: str = "INFO"


class SafetyFiltersEnforcer:
    """Main class for safety filters enforcement."""

    def __init__(self, config: Optional[SafetyFiltersConfig] = None):
        self.config = config or SafetyFiltersConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._filters = []
        self._compiled_patterns = {}
        self._load_default_filters()

    def enforce_filters(self, content: str, context: Optional[Dict[str, Any]] = None) -> FilterResult:
        """Enforce safety filters on content.
        
        Args:
            content: Content to filter
            context: Optional context information
            
        Returns:
            FilterResult: Filter enforcement results
        """
        self.logger.info(f"Enforcing safety filters on content ({len(content)} chars)")
        
        matches = []
        warnings = []
        blocked_content = []
        filtered_content = content
        
        try:
            # Apply each enabled filter
            for filter_type in self.config.enabled_filters:
                type_filters = [f for f in self._filters if f.filter_type == filter_type and f.enabled]
                
                for safety_filter in type_filters:
                    filter_matches = self._apply_filter(safety_filter, content)
                    matches.extend(filter_matches)
            
            # Apply custom filters
            for safety_filter in self.config.custom_filters:
                if safety_filter.enabled:
                    filter_matches = self._apply_filter(safety_filter, content)
                    matches.extend(filter_matches)
            
            # Process matches based on actions
            for match in matches:
                if match.action == FilterAction.BLOCK:
                    blocked_content.append(match.matched_content)
                elif match.action == FilterAction.WARN:
                    warnings.append(f"Warning: {match.filter_name} detected")
                elif match.action == FilterAction.REDACT and self.config.auto_redact:
                    filtered_content = self._redact_content(filtered_content, match)
            
            # Determine if content is safe
            safe = not any(m.action == FilterAction.BLOCK for m in matches)
            
            result = FilterResult(
                safe=safe,
                filtered_content=filtered_content if filtered_content != content else None,
                matches=matches,
                warnings=warnings,
                blocked_content=blocked_content,
                metadata={
                    "filtered_at": datetime.utcnow().isoformat(),
                    "original_length": len(content),
                    "filters_applied": len(self._filters) + len(self.config.custom_filters),
                    "enforcer": "SafetyFiltersEnforcer"
                }
            )
            
            self.logger.info(
                f"Filter enforcement completed: {'safe' if safe else 'unsafe'} "
                f"({len(matches)} matches, {len(blocked_content)} blocked)"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Filter enforcement failed: {str(e)}")
            return FilterResult(
                safe=False,
                matches=[FilterMatch(
                    filter_id="system_error",
                    filter_name="System Error",
                    filter_type=FilterType.PROFANITY,
                    action=FilterAction.BLOCK,
                    matched_content=str(e),
                    confidence=1.0
                )],
                metadata={"error": str(e)}
            )

    def _apply_filter(self, safety_filter: SafetyFilter, content: str) -> List[FilterMatch]:
        """Apply a single safety filter to content."""
        matches = []
        
        try:
            # Get compiled patterns for this filter
            patterns = self._compiled_patterns.get(safety_filter.id, [])
            
            # Check each pattern
            for pattern in patterns:
                for match in pattern.finditer(content):
                    filter_match = FilterMatch(
                        filter_id=safety_filter.id,
                        filter_name=safety_filter.name,
                        filter_type=safety_filter.filter_type,
                        action=safety_filter.action,
                        matched_content=match.group(),
                        position=match.start(),
                        confidence=0.9
                    )
                    matches.append(filter_match)
            
            # Check keywords
            for keyword in safety_filter.keywords:
                if keyword.lower() in content.lower():
                    positions = [m.start() for m in re.finditer(re.escape(keyword), content, re.IGNORECASE)]
                    for pos in positions:
                        filter_match = FilterMatch(
                            filter_id=safety_filter.id,
                            filter_name=safety_filter.name,
                            filter_type=safety_filter.filter_type,
                            action=safety_filter.action,
                            matched_content=keyword,
                            position=pos,
                            confidence=0.8
                        )
                        matches.append(filter_match)
            
        except Exception as e:
            self.logger.warning(f"Filter {safety_filter.id} failed: {str(e)}")
        
        return matches

    def _redact_content(self, content: str, match: FilterMatch) -> str:
        """Redact matched content from text."""
        if match.position is not None:
            start = match.position
            end = start + len(match.matched_content)
            return content[:start] + "[REDACTED]" + content[end:]
        return content.replace(match.matched_content, "[REDACTED]")

    def _load_default_filters(self) -> None:
        """Load default safety filters."""
        # Profanity filter
        profanity_filter = SafetyFilter(
            id="profanity_filter",
            name="Profanity Filter",
            filter_type=FilterType.PROFANITY,
            patterns=[
                r'\b(damn|hell|shit|crap|bullshit)\b',
                r'\b(fuck|screw|piss|bitch|bastard)\b'
            ],
            action=FilterAction.REDACT,
            severity="medium",
            description="Filters profane language"
        )
        self._filters.append(profanity_filter)
        
        # Toxicity filter
        toxicity_filter = SafetyFilter(
            id="toxicity_filter",
            name="Toxicity Filter",
            filter_type=FilterType.TOXICITY,
            patterns=[
                r'\b(kill|die|harm|hurt)\s+(yourself|you)',
                r'\b(stupid|idiot|moron|dumb)\s+(person|people|human)'
            ],
            action=FilterAction.WARN,
            severity="high",
            description="Detects toxic content"
        )
        self._filters.append(toxicity_filter)
        
        # Violence filter
        violence_filter = SafetyFilter(
            id="violence_filter",
            name="Violence Filter",
            filter_type=FilterType.VIOLENCE,
            patterns=[
                r'\b(violence|attack|assault|murder|kill)\b',
                r'\b(weapon|gun|knife|bomb|explosive)\b'
            ],
            action=FilterAction.FLAG,
            severity="high",
            description="Detects violent content"
        )
        self._filters.append(violence_filter)
        
        # Hate speech filter
        hate_speech_filter = SafetyFilter(
            id="hate_speech_filter",
            name="Hate Speech Filter",
            filter_type=FilterType.HATE_SPEECH,
            patterns=[
                r'\b(hate|despise|loathe)\s+\w+\s+(people|persons|race|religion)',
                r'\b(superior|inferior)\s+(race|gender|religion)'
            ],
            action=FilterAction.BLOCK,
            severity="critical",
            description="Blocks hate speech"
        )
        self._filters.append(hate_speech_filter)
        
        # Self harm filter
        self_harm_filter = SafetyFilter(
            id="self_harm_filter",
            name="Self Harm Filter",
            filter_type=FilterType.SELF_HARM,
            patterns=[
                r'\b(suicide|kill\s+myself|end\s+my\s+life)',
                r'\b(self\s+harm|hurt\s+myself)'
            ],
            action=FilterAction.BLOCK,
            severity="critical",
            description="Blocks self-harm content"
        )
        self._filters.append(self_harm_filter)
        
        # Compile all patterns
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns for all filters."""
        for safety_filter in self._filters:
            compiled = []
            for pattern in safety_filter.patterns:
                try:
                    compiled.append(re.compile(pattern, re.IGNORECASE))
                except re.error as e:
                    self.logger.warning(f"Invalid regex pattern in {safety_filter.id}: {str(e)}")
            self._compiled_patterns[safety_filter.id] = compiled

    def add_filter(self, safety_filter: SafetyFilter) -> None:
        """Add a custom safety filter.
        
        Args:
            safety_filter: Filter to add
        """
        self.logger.info(f"Adding safety filter: {safety_filter.id}")
        self.config.custom_filters.append(safety_filter)
        
        # Compile patterns for new filter
        compiled = []
        for pattern in safety_filter.patterns:
            try:
                compiled.append(re.compile(pattern, re.IGNORECASE))
            except re.error as e:
                self.logger.warning(f"Invalid regex pattern in {safety_filter.id}: {str(e)}")
        self._compiled_patterns[safety_filter.id] = compiled

    def remove_filter(self, filter_id: str) -> bool:
        """Remove a safety filter.
        
        Args:
            filter_id: ID of filter to remove
            
        Returns:
            bool: True if filter was removed
        """
        # Remove from default filters
        original_length = len(self._filters)
        self._filters = [f for f in self._filters if f.id != filter_id]
        
        # Remove from custom filters
        self.config.custom_filters = [f for f in self.config.custom_filters if f.id != filter_id]
        
        # Remove compiled patterns
        if filter_id in self._compiled_patterns:
            del self._compiled_patterns[filter_id]
        
        return len(self._filters) < original_length

    def get_filter_summary(self) -> Dict[str, Any]:
        """Get summary of filter configuration.
        
        Returns:
            Dict: Filter configuration summary
        """
        return {
            "enabled_filters": [f.value for f in self.config.enabled_filters],
            "total_filters": len(self._filters) + len(self.config.custom_filters),
            "default_action": self.config.default_action.value,
            "strict_mode": self.config.strict_mode,
            "auto_redact": self.config.auto_redact
        }


# Factory function for easy instantiation
def create_safety_filters_enforcer(
    enabled_filters: List[str] = None,
    default_action: str = "warn",
    strict_mode: bool = False,
    **kwargs
) -> SafetyFiltersEnforcer:
    """Create a configured safety filters enforcer."""
    config = SafetyFiltersConfig(
        enabled_filters=[FilterType(f) for f in (enabled_filters or ["profanity", "toxicity", "violence"])],
        default_action=FilterAction(default_action),
        strict_mode=strict_mode,
        **kwargs
    )
    return SafetyFiltersEnforcer(config)


# Convenience function for direct usage
def enforce_safety_filters(
    content: str,
    filters: List[str] = None,
    strict_mode: bool = False,
    auto_redact: bool = True,
    context: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Enforce safety filters on content.
    
    Args:
        content: Content to filter
        filters: List of filter types to apply
        strict_mode: Whether to use strict mode
        auto_redact: Whether to automatically redact content
        context: Optional context information
        config: Optional enforcer configuration
        
    Returns:
        Dict: Filter enforcement results
    """
    # Create enforcer and execute
    enforcer_config = SafetyFiltersConfig(
        enabled_filters=[FilterType(f) for f in (filters or ["profanity", "toxicity", "violence"])],
        strict_mode=strict_mode,
        auto_redact=auto_redact,
        **config or {}
    )
    enforcer = SafetyFiltersEnforcer(enforcer_config)
    result = enforcer.enforce_filters(content, context)
    
    # Convert result to dict for JSON serialization
    return {
        "safe": result.safe,
        "filtered_content": result.filtered_content,
        "matches": [
            {
                "filter_id": m.filter_id,
                "filter_name": m.filter_name,
                "filter_type": m.filter_type.value,
                "action": m.action.value,
                "matched_content": m.matched_content,
                "position": m.position,
                "confidence": m.confidence,
                "timestamp": m.timestamp.isoformat()
            }
            for m in result.matches
        ],
        "warnings": result.warnings,
        "blocked_content": result.blocked_content,
        "metadata": result.metadata
    }
