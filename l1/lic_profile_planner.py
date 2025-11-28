"""LIC Profile Analysis Planner - L1 Planning Layer

Implements HOP-1 profile analysis functionality from legacy LIC system.
Classifies recipient archetype based on title and role indicators.
Pure planning - no execution, IO, or LLM calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum


class ArchetypeType(Enum):
    """LIC recipient archetype classifications"""
    EXECUTIVE = "executive"
    HIRING_MANAGER = "hiring_manager"
    TECHNICAL_LEAD = "technical_lead"
    RECRUITER = "recruiter"
    INFLUENCER = "influencer"
    PEER = "peer"
    UNKNOWN = "unknown"


@dataclass
class ArchetypeIndicators:
    """Configuration for archetype classification indicators"""
    keywords: List[str]
    confidence: float
    priority: int = 1


@dataclass
class ProfileAnalysisPlan:
    """Output plan for HOP-1 profile analysis"""
    archetype: ArchetypeType
    confidence: float
    reasoning: str
    key_indicators: List[str]
    needs_manual_override: bool
    recipient_title: str
    recipient_name: str
    recipient_company: str
    
    # Planning metadata
    plan_id: str
    created_at: str
    classification_rules_applied: List[str]


class LICProfilePlanner:
    """
    L1 Planner for LIC HOP-1 Profile Analysis
    
    Transforms recipient profile data into archetype classification plan.
    Pure deterministic logic - no LLM calls or external dependencies.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize planner with archetype classification rules
        
        Args:
            config: Optional configuration dict with archetype indicators
        """
        self.config = config or self._get_default_config()
        self.archetype_indicators = self._load_archetype_indicators()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for archetype classification"""
        return {
            "profile_analysis_agent": {
                "archetype_indicators": {
                    "executive": {
                        "keywords": ["ceo", "cto", "cfo", "chief", "president", "vp", "vice president", "director"],
                        "confidence": 0.9,
                        "priority": 1
                    },
                    "hiring_manager": {
                        "keywords": ["manager", "head of", "lead", "supervisor", "team lead"],
                        "confidence": 0.8,
                        "priority": 2
                    },
                    "technical_lead": {
                        "keywords": ["senior", "principal", "staff", "architect", "engineer"],
                        "confidence": 0.7,
                        "priority": 3
                    },
                    "recruiter": {
                        "keywords": ["recruiter", "talent acquisition", "sourcing", "people"],
                        "confidence": 0.8,
                        "priority": 2
                    },
                    "influencer": {
                        "keywords": ["founder", "advisor", "consultant", "strategist"],
                        "confidence": 0.6,
                        "priority": 4
                    }
                },
                "default_archetype": "peer",
                "default_confidence": 0.5,
                "manual_override_threshold": 0.7
            }
        }
    
    def _load_archetype_indicators(self) -> Dict[str, ArchetypeIndicators]:
        """Load archetype indicators from configuration"""
        indicators = {}
        config_indicators = self.config["profile_analysis_agent"]["archetype_indicators"]
        
        for arch_name, arch_config in config_indicators.items():
            indicators[arch_name] = ArchetypeIndicators(
                keywords=arch_config["keywords"],
                confidence=arch_config["confidence"],
                priority=arch_config.get("priority", 1)
            )
        
        return indicators
    
    def plan_profile_analysis(
        self,
        recipient_name: str,
        recipient_title: str,
        recipient_company: str,
        plan_id: Optional[str] = None
    ) -> ProfileAnalysisPlan:
        """
        Create profile analysis plan for recipient
        
        Args:
            recipient_name: Name of the recipient
            recipient_title: Job title of the recipient
            recipient_company: Company of the recipient
            plan_id: Optional plan identifier
            
        Returns:
            ProfileAnalysisPlan with archetype classification
        """
        # Normalize title for analysis
        title_lower = recipient_title.lower()
        
        # Find best archetype match
        best_archetype = None
        best_confidence = 0.0
        best_reasoning = ""
        best_indicators = []
        rules_applied = []
        
        # Check each archetype configuration
        for arch_name, indicators in self.archetype_indicators.items():
            for keyword in indicators.keywords:
                if keyword in title_lower:
                    confidence = indicators.confidence
                    reasoning = f"Title '{recipient_title}' contains '{keyword}' indicator"
                    indicators_found = [keyword]
                    
                    # Update if this is the best match
                    if confidence > best_confidence:
                        best_archetype = arch_name
                        best_confidence = confidence
                        best_reasoning = reasoning
                        best_indicators = indicators_found
                        rules_applied = [f"keyword_match_{arch_name}"]
                    
                    break
        
        # Apply default if no match found
        if best_archetype is None:
            default_config = self.config["profile_analysis_agent"]
            best_archetype = default_config["default_archetype"]
            best_confidence = default_config["default_confidence"]
            best_reasoning = f"Default classification - ambiguous title '{recipient_title}'"
            best_indicators = [recipient_title]
            rules_applied = ["default_classification"]
        
        # Check if manual override is needed
        override_threshold = self.config["profile_analysis_agent"]["manual_override_threshold"]
        needs_manual_override = best_confidence < override_threshold
        
        # Convert archetype string to enum
        try:
            archetype_enum = ArchetypeType(best_archetype)
        except ValueError:
            archetype_enum = ArchetypeType.UNKNOWN
            best_reasoning += f" (unknown archetype '{best_archetype}' mapped to UNKNOWN)"
        
        # Generate plan ID if not provided
        if plan_id is None:
            import hashlib
            id_string = f"{recipient_name}_{recipient_company}_{recipient_title}"
            plan_id = hashlib.md5(id_string.encode()).hexdigest()[:12]
        
        # Get current timestamp
        from datetime import datetime
        created_at = datetime.now().isoformat()
        
        return ProfileAnalysisPlan(
            archetype=archetype_enum,
            confidence=best_confidence,
            reasoning=best_reasoning,
            key_indicators=best_indicators,
            needs_manual_override=needs_manual_override,
            recipient_title=recipient_title,
            recipient_name=recipient_name,
            recipient_company=recipient_company,
            plan_id=plan_id,
            created_at=created_at,
            classification_rules_applied=rules_applied
        )
    
    def validate_plan(self, plan: ProfileAnalysisPlan) -> List[str]:
        """
        Validate profile analysis plan for completeness and correctness
        
        Args:
            plan: Profile analysis plan to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not plan.recipient_name:
            errors.append("recipient_name is required")
        
        if not plan.recipient_title:
            errors.append("recipient_title is required")
        
        if not plan.recipient_company:
            errors.append("recipient_company is required")
        
        if plan.confidence < 0.0 or plan.confidence > 1.0:
            errors.append("confidence must be between 0.0 and 1.0")
        
        if not plan.reasoning:
            errors.append("reasoning is required")
        
        if not plan.key_indicators:
            errors.append("key_indicators cannot be empty")
        
        if not plan.plan_id:
            errors.append("plan_id is required")
        
        if not plan.created_at:
            errors.append("created_at is required")
        
        return errors
    
    def get_supported_archetypes(self) -> List[ArchetypeType]:
        """Get list of supported archetype types"""
        return list(ArchetypeType)
    
    def get_archetype_config(self, archetype: ArchetypeType) -> Optional[ArchetypeIndicators]:
        """Get configuration for specific archetype"""
        return self.archetype_indicators.get(archetype.value)
