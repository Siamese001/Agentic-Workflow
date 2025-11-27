# File: config.py
# Description: Configuration registry for the LIC workflow.

__version__ = "11.10"
# Holds all static configs for routes, archetypes, RAG, and reasoning.

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from models import Route, Archetype

# ============================================================================
# PRIORITY 2: GLOBAL CONSTRAINTS SSOT WITH API ACCESS LAYER
# ============================================================================

@dataclass
class ConfigRegistry:
    """
    v11.5: Single Source of Truth for ALL configuration parameters
    v11.6: Updated for 4-archetype standard
    v11.10: Prompts (CTA_TEMPLATES, ARCHETYPE_PROMPT_TEMPLATES) moved to prompts.py
    """
    
    # Route-specific base constraints
    ROUTE_CONSTRAINTS: Dict[Route, Dict[str, Any]] = field(default_factory=lambda: {
        Route.INMAIL: {
            "word_range": (180, 250),
            "char_limit": 1900,
            "subject_required": True,
            "subject_word_range": (4, 8),
            "greeting_word_range": (2, 5),
            "cta_word_range": (5, 12),
            "signature_word_range": (2, 6),
            "body_min_words": 120,
        },
        Route.CONNECTION_REQ: {
            "word_range": (40, 60),
            "char_limit": 300,
            "subject_required": False,
            "greeting_word_range": (2, 4),
            "cta_word_range": (4, 8),
            "signature_word_range": (2, 4),
            "body_min_words": 25,
        },
        Route.EMAIL: {
            "word_range": (200, 350),
            "char_limit": 2500,
            "subject_required": True,
            "subject_word_range": (4, 10),
            "greeting_word_range": (2, 6),
            "cta_word_range": (6, 15),
            "signature_word_range": (3, 8),
            "body_min_words": 150,
        },
        Route.FOLLOW_UP: {
            "word_range": (150, 220),
            "char_limit": 1600,
            "subject_required": True,
            "subject_word_range": (4, 8),
            "greeting_word_range": (2, 4),
            "cta_word_range": (5, 10),
            "signature_word_range": (2, 5),
            "body_min_words": 100,
        }
    })
    
    # PRIORITY 3: Archetype-Specific Word Count Targets (v11.6 updated)
    ARCHETYPE_WORD_TARGETS: Dict[Archetype, Dict[Route, Optional[int]]] = field(default_factory=lambda: {
        Archetype.C_LEVEL: {
            Route.INMAIL: 240,
            Route.FOLLOW_UP: 160,
            Route.CONNECTION_REQ: None,
            Route.EMAIL: 350
        },
        Archetype.EXECUTIVE: {
            Route.INMAIL: 225,
            Route.FOLLOW_UP: 150,
            Route.CONNECTION_REQ: None,
            Route.EMAIL: 325
        },
        Archetype.SENIOR_TA: {
            Route.INMAIL: 220,
            Route.FOLLOW_UP: 148,
            Route.CONNECTION_REQ: None,
            Route.EMAIL: 310
        },
        Archetype.RECRUITER: {
            Route.INMAIL: 200,
            Route.FOLLOW_UP: 140,
            Route.CONNECTION_REQ: None,
            Route.EMAIL: 275
        }
    })
    
    # PRIORITY 1: Archetype-Specific RAG Parameters (v11.6 updated)
    ARCHETYPE_RAG_PARAMS: Dict[Archetype, Dict[str, Any]] = field(default_factory=lambda: {
        Archetype.C_LEVEL: {
            "total_calls": 24,
            "retrievers": ["linkedin", "company_blog", "news", "industry_reports"],
            "recency_weight": 0.85,
            "depth_priority": "maximum"
        },
        Archetype.EXECUTIVE: {
            "total_calls": 18,
            "retrievers": ["linkedin", "company_blog", "news"],
            "recency_weight": 0.75,
            "depth_priority": "high"
        },
        Archetype.SENIOR_TA: {
            "total_calls": 16,
            "retrievers": ["linkedin", "github", "tech_blogs", "conference_talks"],
            "recency_weight": 0.70,
            "depth_priority": "technical"
        },
        Archetype.RECRUITER: {
            "total_calls": 8,
            "retrievers": ["linkedin", "company_careers"],
            "recency_weight": 0.60,
            "depth_priority": "efficient"
        }
    })
    
    # PRIORITY 1: Archetype-Specific Reasoning Configurations (v11.6 updated)
    ARCHETYPE_REASONING_PARAMS: Dict[Archetype, Dict[str, Any]] = field(default_factory=lambda: {
        Archetype.C_LEVEL: {
            "max_hops": 6,
            "temperature": 0.45,
            "self_consistency_runs": 12,
            "tot_branches": 16,
            "reasoning_depth": "maximum",
            "synthesis_enabled": True
        },
        Archetype.EXECUTIVE: {
            "max_hops": 4,
            "temperature": 0.50,
            "self_consistency_runs": 5,
            "tot_branches": 6,
            "reasoning_depth": "high",
            "synthesis_enabled": True
        },
        Archetype.SENIOR_TA: {
            "max_hops": 4,
            "temperature": 0.55,
            "self_consistency_runs": 4,
            "tot_branches": 4,
            "reasoning_depth": "technical",
            "synthesis_enabled": False
        },
        Archetype.RECRUITER: {
            "max_hops": 2,
            "temperature": 0.65,
            "self_consistency_runs": 3,
            "tot_branches": 0,
            "reasoning_depth": "efficient",
            "synthesis_enabled": False
        }
    })
    
    # PRIORITY 4: Archetype-Specific Tone Mappings (v11.6 updated)
    ARCHETYPE_TONE_MAPPINGS: Dict[Archetype, Dict[str, Any]] = field(default_factory=lambda: {
        Archetype.C_LEVEL: {
            "message_tone": "strategic",
            "verb_preference": ["discuss", "align", "explore", "advance"],
            "jargon_level": "strategic",
            "formality": "very high"
        },
        Archetype.EXECUTIVE: {
            "message_tone": "professional",
            "verb_preference": ["collaborate", "discuss", "connect", "share"],
            "jargon_level": "professional",
            "formality": "high"
        },
        Archetype.SENIOR_TA: {
            "message_tone": "technical_peer",
            "verb_preference": ["build", "implement", "architect", "optimize"],
            "jargon_level": "technical",
            "formality": "moderate"
        },
        Archetype.RECRUITER: {
            "message_tone": "warm_professional",
            "verb_preference": ["match", "connect", "support", "assist"],
            "jargon_level": "minimal",
            "formality": "moderate"
        }
    })
    
    # --- Class Methods to Access Config ---
    
    def get_target_word_count(self, archetype: Archetype, route: Route) -> int:
        """Get target word count for archetype+route combination"""
        target = self.ARCHETYPE_WORD_TARGETS.get(archetype, {}).get(route)
        if target is not None:
            return target
        return self.ROUTE_CONSTRAINTS[route]["word_range"][1]
    
    def get_rag_parameter(self, archetype: Archetype, param_name: str) -> Any:
        """Get RAG parameter for archetype"""
        return self.ARCHETYPE_RAG_PARAMS.get(archetype, {}).get(param_name)
    
    def get_reasoning_parameter(self, archetype: Archetype, param_name: str) -> Any:
        """Get reasoning parameter for archetype"""
        return self.ARCHETYPE_REASONING_PARAMS.get(archetype, {}).get(param_name)
    
    def get_tone_mapping(self, archetype: Archetype, param_name: str) -> Any:
        """Get tone mapping for archetype"""
        return self.ARCHETYPE_TONE_MAPPINGS.get(archetype, {}).get(param_name)
    
    def get_route_constraints(self, route: Route, archetype: Optional[Archetype] = None) -> Dict[str, Any]:
        """Get route constraints with optional archetype override"""
        constraints = self.ROUTE_CONSTRAINTS[route].copy()
        
        if archetype:
            target_word = self.get_target_word_count(archetype, route)
            if target_word:
                constraints["word_target"] = target_word
        
        return constraints

# Create a single global instance
CONFIG_REGISTRY = ConfigRegistry()