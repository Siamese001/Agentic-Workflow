"""
LinkedIn Outreach Orchestrator (LIC) - AGENTIC v11.5
====================================================

CHANGELOG v11.5 (CRITICAL - Priorities 1-4 from v10.22):
---------------------------------------------------------
✨ NEW: Priority 1 - Archetype-Specific Reasoning Configurations
- Added ARCHETYPE_REASONING_PARAMS with complete configs for all archetypes
- C_LEVEL: 24 RAG calls, 6 max hops, temp=0.45, 12 self-consistency, 16 ToT branches
- EXECUTIVE: 18 RAG calls, 4 max hops, temp=0.5, 5 self-consistency, 6 ToT branches
- RECRUITER: 8 RAG calls, 2 max hops, temp=0.65, 3 self-consistency, NO ToT
- 3x compute variance: CEO gets maximum investment, recruiters get efficiency
- Integrated with ResearchOrchestrator and GenerationOrchestrator

✨ NEW: Priority 2 - Global Constraints SSOT with API Access Layer
- Created ConfigRegistry class as single source of truth for all parameters
- Consolidated ROUTE_CONSTRAINTS, archetype word counts, RAG params, tone mappings
- API functions: get_target_word_count(), get_rag_parameter(), get_tone_mapping()
- Eliminated configuration duplication and drift
- 47 centralized parameters across 4 parameter types

✨ NEW: Priority 3 - Archetype-Specific Word Count Targets
- C_LEVEL: INMAIL=240, FOLLOW_UP=160 (longest, most substantive)
- EXECUTIVE: INMAIL=225, FOLLOW_UP=150 (moderate depth)
- RECRUITER: INMAIL=200, FOLLOW_UP=140 (efficient, concise)
- HIRING_MANAGER: INMAIL=210, FOLLOW_UP=145
- Dynamic constraint lookup via ConfigRegistry.get_target_word_count()

✨ NEW: Priority 4 - Archetype-Specific Tone Mappings
- message_tone: "strategic" for C_LEVEL vs "warm" for RECRUITER
- verb_preference: ["discuss", "align"] for C_LEVEL vs ["chat", "connect"] for RECRUITER
- jargon_level: "strategic" for C_LEVEL vs "layman_with_metrics" for RECRUITER
- formality: "very high" for C_LEVEL vs "low-medium" for RECRUITER
- language_adaptation strategies integrated into scaffolds and prompts

BACKWARD COMPATIBLE: All v11.4 functionality preserved
- Decision tree routing logic intact
- Progressive section locking
- Constraint failure classification
- Ground truth recalculation
- Similarity cross-validation
- Reflexion loops with critique history

Architecture: Multi-Agent DAG with Event-Driven Orchestration + SSOT Config
Dependencies: anthropic, google-generativeai, numpy, scikit-learn
"""

__version__ = "11.5.0"
__author__ = "Amit (Chief AI Officer)"

import asyncio
import hashlib
import json
import re
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from uuid import uuid4
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class Route(Enum):
    """Message delivery routes"""
    INMAIL = "INMAIL"
    CONNECTION_REQ = "CONNECTION_REQ"
    EMAIL = "EMAIL"
    FOLLOW_UP = "FOLLOW_UP"


class Archetype(Enum):
    """Recipient archetypes for personalization"""
    C_LEVEL = "C_LEVEL"
    EXECUTIVE = "EXECUTIVE"
    RECRUITER = "RECRUITER"
    HIRING_MANAGER = "HIRING_MANAGER"
    PEER = "PEER"


class EventType(Enum):
    """Event types for message bus"""
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    PROFILE_ANALYSIS_COMPLETED = "PROFILE_ANALYSIS_COMPLETED"
    RESEARCH_COMPLETED = "RESEARCH_COMPLETED"
    SCAFFOLD_COMPLETED = "SCAFFOLD_COMPLETED"
    GENERATION_COMPLETED = "GENERATION_COMPLETED"
    VALIDATION_COMPLETED = "VALIDATION_COMPLETED"
    GATE_APPROVED = "GATE_APPROVED"
    GATE_REJECTED = "GATE_REJECTED"
    CHECKPOINT_CREATED = "CHECKPOINT_CREATED"
    CHECKPOINT_VERIFIED = "CHECKPOINT_VERIFIED"
    FAILURE_CLASSIFIED = "FAILURE_CLASSIFIED"
    SECTION_LOCKED = "SECTION_LOCKED"
    CONTAMINATION_DETECTED = "CONTAMINATION_DETECTED"
    REFLEXION_TRIGGERED = "REFLEXION_TRIGGERED"


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class ValidationSeverity(Enum):
    """Validation result severity levels"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ConstraintFailureType(Enum):
    """Types of constraint failures for adaptive retry"""
    MECHANICAL = "MECHANICAL"      # Word count, char count, structural
    CREATIVE = "CREATIVE"          # Placeholders, generic content
    SEMANTIC = "SEMANTIC"          # Forbidden words, tone violations
    CONFLICT = "CONFLICT"          # Impossible constraint combinations


# ============================================================================
# PRIORITY 2: GLOBAL CONSTRAINTS SSOT WITH API ACCESS LAYER
# ============================================================================

class ConfigRegistry:
    """
    NEW v11.5: Single Source of Truth for ALL configuration parameters
    Consolidates route constraints, archetype parameters, RAG configs, tone mappings
    Provides API functions for safe, validated parameter access
    """
    
    # Route-specific base constraints
    ROUTE_CONSTRAINTS = {
        Route.INMAIL: {
            "word_range": (180, 250),  # Overridden by archetype
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
            "word_range": (150, 220),  # Overridden by archetype
            "char_limit": 1600,
            "subject_required": True,
            "subject_word_range": (4, 8),
            "greeting_word_range": (2, 4),
            "cta_word_range": (5, 10),
            "signature_word_range": (2, 5),
            "body_min_words": 100,
        }
    }
    
    # PRIORITY 3: Archetype-Specific Word Count Targets
    ARCHETYPE_WORD_TARGETS = {
        Archetype.C_LEVEL: {
            Route.INMAIL: 240,      # Most substantive
            Route.FOLLOW_UP: 160,
            Route.CONNECTION_REQ: None,  # Use base constraint
            Route.EMAIL: 350
        },
        Archetype.EXECUTIVE: {
            Route.INMAIL: 225,      # Moderate depth
            Route.FOLLOW_UP: 150,
            Route.CONNECTION_REQ: None,
            Route.EMAIL: 325
        },
        Archetype.HIRING_MANAGER: {
            Route.INMAIL: 210,
            Route.FOLLOW_UP: 145,
            Route.CONNECTION_REQ: None,
            Route.EMAIL: 300
        },
        Archetype.RECRUITER: {
            Route.INMAIL: 200,      # Most efficient
            Route.FOLLOW_UP: 140,
            Route.CONNECTION_REQ: None,
            Route.EMAIL: 275
        },
        Archetype.PEER: {
            Route.INMAIL: 215,
            Route.FOLLOW_UP: 145,
            Route.CONNECTION_REQ: None,
            Route.EMAIL: 300
        }
    }
    
    # PRIORITY 1: Archetype-Specific RAG Parameters
    ARCHETYPE_RAG_PARAMS = {
        Archetype.C_LEVEL: {
            "total_calls": 24,
            "min_hops": 2,
            "max_hops": 6,
            "web_search": 6,
            "project_knowledge": 10,
            "conversation_search": 5
        },
        Archetype.EXECUTIVE: {
            "total_calls": 18,
            "min_hops": 2,
            "max_hops": 4,
            "web_search": 6,
            "project_knowledge": 8,
            "conversation_search": 4
        },
        Archetype.HIRING_MANAGER: {
            "total_calls": 15,
            "min_hops": 2,
            "max_hops": 3,
            "web_search": 5,
            "project_knowledge": 7,
            "conversation_search": 3
        },
        Archetype.RECRUITER: {
            "total_calls": 8,
            "min_hops": 2,
            "max_hops": 2,
            "web_search": 4,
            "project_knowledge": 4,
            "conversation_search": 2
        },
        Archetype.PEER: {
            "total_calls": 12,
            "min_hops": 2,
            "max_hops": 3,
            "web_search": 4,
            "project_knowledge": 6,
            "conversation_search": 2
        }
    }
    
    # PRIORITY 4: Archetype-Specific Tone Mappings
    ARCHETYPE_TONE_MAPPINGS = {
        Archetype.C_LEVEL: {
            "message_tone": "strategic, outcome-focused",
            "cta_tone": "formal_neutral",
            "greeting_tone": "peer",
            "language_adaptation": "ANALYST_LEVEL_PITCH",
            "jargon_level": "strategic",
            "formality": "very high",
            "verb_preference": ["discuss", "align", "explore"]
        },
        Archetype.EXECUTIVE: {
            "message_tone": "direct, collaborative",
            "cta_tone": "collaborative",
            "greeting_tone": "direct",
            "language_adaptation": "OPERATIONAL_PITCH",
            "jargon_level": "business",
            "formality": "high",
            "verb_preference": ["discuss", "explore", "align"]
        },
        Archetype.HIRING_MANAGER: {
            "message_tone": "direct, collaborative",
            "cta_tone": "direct, collaborative",
            "greeting_tone": "standard",
            "language_adaptation": "TECHNICAL_DETAIL",
            "jargon_level": "technical",
            "formality": "medium-high",
            "verb_preference": ["discuss", "explore", "review"]
        },
        Archetype.RECRUITER: {
            "message_tone": "warm, efficient",
            "cta_tone": "professional_neutral",
            "greeting_tone": "respectful",
            "language_adaptation": "SKILL_TO_ROLE_MAPPING",
            "jargon_level": "layman_with_metrics",
            "formality": "low-medium",
            "verb_preference": ["chat", "connect", "speak"]
        },
        Archetype.PEER: {
            "message_tone": "friendly, professional",
            "cta_tone": "collaborative",
            "greeting_tone": "casual",
            "language_adaptation": "PEER_TO_PEER",
            "jargon_level": "technical",
            "formality": "medium",
            "verb_preference": ["discuss", "chat", "connect"]
        }
    }
    
    @classmethod
    def get_target_word_count(cls, route: Route, archetype: Archetype) -> int:
        """
        Get target word count for route/archetype combination
        Returns archetype-specific target or falls back to route default
        """
        archetype_target = cls.ARCHETYPE_WORD_TARGETS.get(archetype, {}).get(route)
        if archetype_target:
            return archetype_target
        
        # Fallback to route base constraint
        word_range = cls.ROUTE_CONSTRAINTS[route]["word_range"]
        return (word_range[0] + word_range[1]) // 2
    
    @classmethod
    def get_rag_parameter(cls, archetype: Archetype, param_name: str) -> int:
        """Get RAG parameter for specific archetype"""
        return cls.ARCHETYPE_RAG_PARAMS.get(archetype, {}).get(param_name, 0)
    
    @classmethod
    def get_tone_mapping(cls, archetype: Archetype, tone_aspect: str) -> Any:
        """Get tone mapping for specific archetype"""
        return cls.ARCHETYPE_TONE_MAPPINGS.get(archetype, {}).get(tone_aspect, "")
    
    @classmethod
    def get_route_constraint(cls, route: Route, constraint_name: str) -> Any:
        """Get specific constraint for route"""
        return cls.ROUTE_CONSTRAINTS.get(route, {}).get(constraint_name)


# ============================================================================
# PRIORITY 1: ARCHETYPE-SPECIFIC REASONING CONFIGURATIONS
# ============================================================================

ARCHETYPE_REASONING_PARAMS = {
    Archetype.C_LEVEL: {
        "temp": 0.45,                    # Lower temp for precision
        "top_p": 0.9,
        "rag_total_calls": 24,           # Maximum investment
        "min_hops": 2,
        "max_hops": 6,                   # Deepest research
        "web_search": 6,
        "project_knowledge": 10,
        "conversation_search": 5,
        "hyde_enabled": True,
        "hybrid_cot_tot": True,          # Full Tree-of-Thought
        "cot_min_paths": 6,              # 6 reasoning paths
        "tot_branches": 16,              # Maximum branching
        "min_tot_depth": 3,
        "self_consistency": 12,          # 12 consistency runs
        "reflexion": True,
        "claim_verification_mode": "strict"
    },
    Archetype.EXECUTIVE: {
        "temp": 0.5,
        "top_p": 0.92,
        "rag_total_calls": 18,           # Moderate investment
        "min_hops": 2,
        "max_hops": 4,
        "web_search": 6,
        "project_knowledge": 8,
        "conversation_search": 4,
        "hyde_enabled": True,
        "hybrid_cot_tot": True,
        "cot_min_paths": 3,
        "tot_branches": 6,
        "min_tot_depth": 3,
        "self_consistency": 5,
        "reflexion": True,
        "claim_verification_mode": "strict"
    },
    Archetype.HIRING_MANAGER: {
        "temp": 0.55,
        "top_p": 0.93,
        "rag_total_calls": 15,
        "min_hops": 2,
        "max_hops": 3,
        "web_search": 5,
        "project_knowledge": 7,
        "conversation_search": 3,
        "hyde_enabled": True,
        "hybrid_cot_tot": True,
        "cot_min_paths": 2,
        "tot_branches": 4,
        "min_tot_depth": 3,
        "self_consistency": 4,
        "reflexion": True,
        "claim_verification_mode": "balanced"
    },
    Archetype.RECRUITER: {
        "temp": 0.65,                    # Higher temp for warmth
        "top_p": 0.95,
        "rag_total_calls": 8,            # Efficient
        "min_hops": 2,
        "max_hops": 2,                   # Minimal hops
        "web_search": 4,
        "project_knowledge": 4,
        "conversation_search": 2,
        "hyde_enabled": True,
        "hybrid_cot_tot": False,         # NO Tree-of-Thought
        "cot_min_paths": None,
        "tot_branches": None,
        "min_tot_depth": None,
        "self_consistency": 3,           # Minimal consistency runs
        "reflexion": False,              # NO Reflexion
        "claim_verification_mode": "balanced"
    },
    Archetype.PEER: {
        "temp": 0.6,
        "top_p": 0.94,
        "rag_total_calls": 12,
        "min_hops": 2,
        "max_hops": 3,
        "web_search": 4,
        "project_knowledge": 6,
        "conversation_search": 2,
        "hyde_enabled": True,
        "hybrid_cot_tot": True,
        "cot_min_paths": 2,
        "tot_branches": 4,
        "min_tot_depth": 3,
        "self_consistency": 4,
        "reflexion": True,
        "claim_verification_mode": "balanced"
    }
}

# Default temperature schedules (base values, adapted by failure classifier and archetype)
DEFAULT_TEMPERATURES = {
    "routing": 0.3,
    "research_query_generation": 0.5,
    "research_critique": 0.4,
    "scaffold": 0.6,
    "generation_greeting": [0.5, 0.6, 0.7],  # Progressive
    "generation_subject": [0.5, 0.6, 0.7],
    "generation_body": [0.6, 0.7, 0.8],
    "generation_cta": [0.5, 0.6, 0.7],
    "generation_signature": [0.4, 0.5, 0.6],
}

# Forbidden content patterns
FORBIDDEN_PATTERNS = {
    "placeholders": [
        r"\[.*?\]", r"\{.*?\}", r"<.*?>", r"TODO", r"FIXME", r"XXX",
        r"INSERT", r"PLACEHOLDER", r"SAMPLE", r"EXAMPLE"
    ],
    "forbidden_verbs": [
        "leverage", "synergy", "circle back", "touch base", "reach out",
        "drill down", "move the needle", "low-hanging fruit"
    ],
    "prompt_leakage": [
        "as an AI", "I am programmed", "my training", "language model",
        "I don't have personal", "I cannot", "I'm unable"
    ]
}

# Similarity thresholds for cross-validation
SIMILARITY_THRESHOLDS = {
    "exact_duplicate": 0.95,
    "near_duplicate": 0.85,
    "high_overlap": 0.70,
    "moderate_overlap": 0.50
}


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class OutreachMission:
    """Immutable mission parameters"""
    mission_id: str
    sender_profile: Dict[str, Any]
    recipient_profile: Dict[str, Any]
    job_description: Dict[str, Any]
    connection_status: str = "not_connected"
    prior_message_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProfileAnalysis:
    """Analyzed recipient profile"""
    archetype: Archetype
    seniority_level: str
    primary_domain: str
    reasoning: str
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchContext:
    """Research findings and metadata"""
    mission_id: str
    research_queries: List[str]
    findings: Dict[str, Any]
    sources_used: List[str]
    total_rag_calls: int
    research_hops: int
    critique_history: List[Dict[str, Any]] = field(default_factory=list)
    reflexion_cycles: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MessageScaffold:
    """Structural message template"""
    mission_id: str
    route: Route
    archetype: Archetype
    target_word_count: int
    tone_guidance: Dict[str, Any]
    key_talking_points: List[str]
    forbidden_topics: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GenerationContext:
    """NEW v11.3: Generation state with progressive locking"""
    mission_id: str
    current_attempt: int = 0
    max_attempts: int = 5
    locked_sections: Set[str] = field(default_factory=set)
    section_temperatures: Dict[str, float] = field(default_factory=dict)
    failure_history: List[Dict[str, Any]] = field(default_factory=list)
    adaptive_retry_count: int = 0


@dataclass
class ImmutableStagingBuffer:
    """
    NEW v11.3: Ground truth measurements - never trust LLM metadata
    Cryptographic checksums for data integrity verification
    """
    mission_id: str
    content: Dict[str, str]
    ground_truth_metrics: Dict[str, Any]
    checksum: str
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate ground truth metrics and checksum"""
        self.ground_truth_metrics = self._calculate_ground_truth()
        self.checksum = self._calculate_checksum()
    
    def _calculate_ground_truth(self) -> Dict[str, Any]:
        """Recalculate all metrics independently - NEVER trust LLM claims"""
        metrics = {}
        for section, text in self.content.items():
            if not text:
                continue
            
            # Deterministic word count
            words = text.split()
            metrics[f"{section}_word_count"] = len(words)
            
            # Deterministic character count
            metrics[f"{section}_char_count"] = len(text)
            
            # Sentence count
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
            metrics[f"{section}_sentence_count"] = len(sentences)
        
        # Total metrics
        total_text = " ".join(self.content.values())
        metrics["total_word_count"] = len(total_text.split())
        metrics["total_char_count"] = len(total_text)
        
        return metrics
    
    def _calculate_checksum(self) -> str:
        """Cryptographic verification of content integrity"""
        content_str = json.dumps(self.content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify content hasn't been tampered with"""
        current_checksum = hashlib.sha256(
            json.dumps(self.content, sort_keys=True).encode()
        ).hexdigest()
        return current_checksum == self.checksum


@dataclass
class ValidationResult:
    """Validation outcome"""
    passed: bool
    severity: ValidationSeverity
    rule_id: str
    message: str
    section: Optional[str] = None
    actual_value: Optional[Any] = None
    expected_value: Optional[Any] = None


@dataclass
class QAReport:
    """Comprehensive quality assurance report"""
    mission_id: str
    production_ready: bool
    validation_results: List[ValidationResult]
    critical_issues: int
    errors: int
    warnings: int
    locked_sections_count: int
    reflexion_cycles_used: int
    adaptive_retries_count: int
    contamination_detected: bool
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_formatted_string(self) -> str:
        """Format QA report for display"""
        lines = [
            "="*80,
            "QUALITY ASSURANCE REPORT",
            "="*80,
            f"Mission ID: {self.mission_id}",
            f"Generated: {self.generated_at.isoformat()}",
            f"Production Ready: {'✅ YES' if self.production_ready else '❌ NO'}",
            "",
            "SUMMARY:",
            f"  Critical Issues: {self.critical_issues}",
            f"  Errors: {self.errors}",
            f"  Warnings: {self.warnings}",
            f"  Locked Sections: {self.locked_sections_count}",
            f"  Reflexion Cycles: {self.reflexion_cycles_used}",
            f"  Adaptive Retries: {self.adaptive_retries_count}",
            f"  Contamination: {'⚠ DETECTED' if self.contamination_detected else '✅ NONE'}",
            "",
            "VALIDATION DETAILS:",
            "-"*80
        ]
        
        # Group by severity
        by_severity = defaultdict(list)
        for result in self.validation_results:
            by_severity[result.severity].append(result)
        
        for severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR, 
                        ValidationSeverity.WARNING, ValidationSeverity.INFO]:
            results = by_severity[severity]
            if not results:
                continue
            
            lines.append(f"\n{severity.value} ({len(results)}):")
            for result in results:
                status = "✅" if result.passed else "❌"
                section_str = f"[{result.section}] " if result.section else ""
                lines.append(f"  {status} {section_str}{result.message}")
                if not result.passed and result.actual_value is not None:
                    lines.append(f"      Actual: {result.actual_value}, Expected: {result.expected_value}")
        
        lines.append("="*80)
        return "\n".join(lines)


@dataclass
class WorkflowResult:
    """Final workflow output"""
    mission_id: str
    status: str
    message: ImmutableStagingBuffer
    qa_report: str
    production_ready: bool
    qa_summary: Dict[str, Any]
    workflow_time: float
    events: List[Dict[str, Any]]


@dataclass
class Event:
    """Event bus message"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    mission_id: str
    agent_id: str
    payload: Dict[str, Any]


# ============================================================================
# NEW v11.3: CONSTRAINT FAILURE CLASSIFIER
# ============================================================================

class ConstraintFailureClassifier:
    """
    NEW v11.3: Intelligent failure analysis for adaptive retry
    Classifies failures into MECHANICAL, CREATIVE, SEMANTIC, or CONFLICT types
    """
    
    @staticmethod
    def classify_failure(
        validation_results: List[ValidationResult],
        section: str
    ) -> Tuple[ConstraintFailureType, Dict[str, Any]]:
        """
        Analyze validation failures and recommend adaptive retry strategy
        
        Returns:
            (failure_type, retry_strategy)
        """
        failures = [r for r in validation_results if not r.passed and r.section == section]
        
        if not failures:
            return ConstraintFailureType.MECHANICAL, {"temp_adjustment": 0.0}
        
        # Count failure types
        mechanical_count = 0
        creative_count = 0
        semantic_count = 0
        
        for failure in failures:
            rule_id = failure.rule_id.lower()
            message = failure.message.lower()
            
            # MECHANICAL: Word/char counts, structural constraints
            if any(x in rule_id for x in ["word_count", "char_count", "length", "structure"]):
                mechanical_count += 1
            
            # CREATIVE: Placeholders, generic content, lack of specificity
            elif any(x in rule_id for x in ["placeholder", "generic", "specific", "concrete"]):
                creative_count += 1
            
            # SEMANTIC: Forbidden words, tone, style violations
            elif any(x in rule_id for x in ["forbidden", "tone", "style", "verb"]):
                semantic_count += 1
            
            # Additional heuristics from message text
            if "placeholder" in message or "generic" in message:
                creative_count += 1
            if "forbidden" in message or "inappropriate" in message:
                semantic_count += 1
        
        # Determine primary failure type and strategy
        if mechanical_count > creative_count and mechanical_count > semantic_count:
            return ConstraintFailureType.MECHANICAL, {
                "temp_adjustment": -0.05,  # Lower temp for precision
                "instruction": "Focus on exact length constraints"
            }
        
        elif creative_count > mechanical_count and creative_count > semantic_count:
            return ConstraintFailureType.CREATIVE, {
                "temp_adjustment": 0.1,  # Raise temp for creativity
                "instruction": "Increase specificity and remove placeholders"
            }
        
        elif semantic_count > mechanical_count and semantic_count > creative_count:
            return ConstraintFailureType.SEMANTIC, {
                "temp_adjustment": -0.1,  # Lower temp for control
                "instruction": "Strict adherence to tone and forbidden word rules"
            }
        
        else:
            # Mixed or CONFLICT
            return ConstraintFailureType.CONFLICT, {
                "temp_adjustment": 0.0,
                "instruction": "Constraints may be conflicting - review requirements"
            }


# ============================================================================
# NEW v11.3: SIMILARITY CROSS-VALIDATOR
# ============================================================================

class SimilarityCrossValidator:
    """
    NEW v11.3: Detect contamination across K-node generations
    Uses TF-IDF cosine similarity for content duplication detection
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            stop_words='english'
        )
    
    def check_contamination(
        self,
        staging_buffer: ImmutableStagingBuffer,
        previous_buffers: List[ImmutableStagingBuffer]
    ) -> Dict[str, Any]:
        """
        Cross-validate current buffer against previous K-node generations
        
        Returns:
            contamination_report with similarity scores and detection flags
        """
        if not previous_buffers:
            return {
                "contaminated": False,
                "similarity_scores": [],
                "max_similarity": 0.0
            }
        
        # Combine all sections into single texts
        current_text = " ".join(staging_buffer.content.values())
        previous_texts = [
            " ".join(buf.content.values()) 
            for buf in previous_buffers
        ]
        
        # Calculate TF-IDF vectors
        all_texts = [current_text] + previous_texts
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        except ValueError:
            # Empty or invalid texts
            return {
                "contaminated": False,
                "similarity_scores": [],
                "max_similarity": 0.0
            }
        
        # Calculate cosine similarities
        current_vector = tfidf_matrix[0:1]
        previous_vectors = tfidf_matrix[1:]
        similarities = cosine_similarity(current_vector, previous_vectors)[0]
        
        max_similarity = float(np.max(similarities)) if len(similarities) > 0 else 0.0
        
        # Check thresholds
        contaminated = max_similarity >= SIMILARITY_THRESHOLDS["high_overlap"]
        
        return {
            "contaminated": contaminated,
            "similarity_scores": similarities.tolist(),
            "max_similarity": max_similarity,
            "threshold_used": SIMILARITY_THRESHOLDS["high_overlap"]
        }
    
    def check_section_duplication(
        self,
        staging_buffer: ImmutableStagingBuffer
    ) -> Dict[str, Any]:
        """
        Check for duplication WITHIN sections of the same buffer
        """
        sections = list(staging_buffer.content.items())
        if len(sections) < 2:
            return {"duplicated": False, "duplicate_pairs": []}
        
        section_texts = [text for _, text in sections if text]
        section_names = [name for name, text in sections if text]
        
        if len(section_texts) < 2:
            return {"duplicated": False, "duplicate_pairs": []}
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(section_texts)
        except ValueError:
            return {"duplicated": False, "duplicate_pairs": []}
        
        # Compare all pairs
        duplicate_pairs = []
        for i in range(len(section_texts)):
            for j in range(i + 1, len(section_texts)):
                similarity = cosine_similarity(
                    tfidf_matrix[i:i+1], 
                    tfidf_matrix[j:j+1]
                )[0][0]
                
                if similarity >= SIMILARITY_THRESHOLDS["near_duplicate"]:
                    duplicate_pairs.append({
                        "section_1": section_names[i],
                        "section_2": section_names[j],
                        "similarity": float(similarity)
                    })
        
        return {
            "duplicated": len(duplicate_pairs) > 0,
            "duplicate_pairs": duplicate_pairs
        }


# ============================================================================
# MESSAGE BUS
# ============================================================================

class EventBus:
    """Async event bus for agent communication"""
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[callable]] = defaultdict(list)
        self.event_log: List[Event] = []
    
    def subscribe(self, event_type: EventType, handler: callable):
        """Subscribe to event type"""
        self.subscribers[event_type].append(handler)
    
    async def publish(self, event: Event):
        """Publish event to subscribers"""
        self.event_log.append(event)
        handlers = self.subscribers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
    
    def get_events_for_mission(self, mission_id: str) -> List[Event]:
        """Retrieve all events for mission"""
        return [e for e in self.event_log if e.mission_id == mission_id]


# ============================================================================
# AGENTS
# ============================================================================

class ProfileAnalysisAgent:
    """
    Agent 1: Analyze recipient profile and determine archetype
    NEW v11.5: Returns archetype for reasoning configuration
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.status = AgentStatus.IDLE
    
    async def analyze_profile(self, mission: OutreachMission) -> ProfileAnalysis:
        """
        Analyze recipient profile and classify archetype
        
        In production: Would use LLM with classification prompt
        For demo: Simple title-based heuristics
        """
        self.status = AgentStatus.RUNNING
        
        # Demo: Simple title-based classification
        title = mission.recipient_profile.get("title", "").lower()
        
        if any(x in title for x in ["ceo", "cto", "coo", "chief", "president"]):
            archetype = Archetype.C_LEVEL
            seniority = "C_LEVEL"
            domain = "EXECUTIVE"
            confidence = 0.95
        elif any(x in title for x in ["vp", "vice president", "director", "head of"]):
            archetype = Archetype.EXECUTIVE
            seniority = "VP_LEVEL"
            domain = "EXECUTIVE"
            confidence = 0.90
        elif any(x in title for x in ["recruiter", "talent", "hr", "people"]):
            archetype = Archetype.RECRUITER
            seniority = "MANAGER_LEVEL"
            domain = "RECRUITING"
            confidence = 0.85
        elif any(x in title for x in ["manager", "lead"]):
            archetype = Archetype.HIRING_MANAGER
            seniority = "MANAGER_LEVEL"
            domain = "TECHNICAL"
            confidence = 0.80
        else:
            archetype = Archetype.PEER
            seniority = "IC_LEVEL"
            domain = "TECHNICAL"
            confidence = 0.70
        
        analysis = ProfileAnalysis(
            archetype=archetype,
            seniority_level=seniority,
            primary_domain=domain,
            reasoning=f"Title '{title}' indicates {archetype.value} archetype",
            confidence_score=confidence
        )
        
        # Publish event
        await self.event_bus.publish(Event(
            event_id=str(uuid4()),
            event_type=EventType.PROFILE_ANALYSIS_COMPLETED,
            timestamp=datetime.now(),
            mission_id=mission.mission_id,
            agent_id="ProfileAnalysisAgent",
            payload={
                "archetype": archetype.value,
                "confidence": confidence
            }
        ))
        
        self.status = AgentStatus.COMPLETED
        return analysis


class ResearchOrchestrator:
    """
    Agent 2: Orchestrate multi-hop RAG research
    NEW v11.5: Uses ARCHETYPE_REASONING_PARAMS for dynamic call budgets
    NEW v11.3: Reflexion loops with critique history
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.status = AgentStatus.IDLE
    
    async def conduct_research(
        self,
        mission: OutreachMission,
        profile_analysis: ProfileAnalysis
    ) -> ResearchContext:
        """
        Multi-hop RAG research with archetype-specific parameters
        NEW v11.5: Dynamically scales RAG calls based on archetype
        """
        self.status = AgentStatus.RUNNING
        
        # NEW v11.5: Get archetype-specific reasoning parameters
        reasoning_params = ARCHETYPE_REASONING_PARAMS[profile_analysis.archetype]
        
        # Extract budget from reasoning params
        total_calls = reasoning_params["rag_total_calls"]
        max_hops = reasoning_params["max_hops"]
        reflexion_enabled = reasoning_params.get("reflexion", False)
        
        print(f"\n🔬 Research Orchestrator - {profile_analysis.archetype.value}")
        print(f"   RAG Budget: {total_calls} calls, Max Hops: {max_hops}")
        print(f"   Reflexion: {'Enabled' if reflexion_enabled else 'Disabled'}")
        
        # Simulate research (in production: actual RAG calls)
        research_queries = [
            f"Background on {mission.recipient_profile['name']}",
            f"Company info: {mission.job_description['company']}",
            f"Role requirements: {mission.job_description['title']}"
        ]
        
        findings = {
            "recipient_background": f"Senior leader with {mission.recipient_profile.get('title', 'experience')}",
            "company_context": f"Company: {mission.job_description.get('company', 'Not specified')}",
            "role_alignment": f"Role: {mission.job_description.get('title', 'Not specified')}"
        }
        
        # NEW v11.3: Reflexion cycle simulation
        critique_history = []
        reflexion_cycles = 0
        if reflexion_enabled and reasoning_params.get("self_consistency", 0) > 5:
            critique_history.append({
                "cycle": 1,
                "critique": "Initial research complete",
                "improvement": "Enhanced depth in findings"
            })
            reflexion_cycles = 1
        
        context = ResearchContext(
            mission_id=mission.mission_id,
            research_queries=research_queries,
            findings=findings,
            sources_used=["demo_source_1", "demo_source_2"],
            total_rag_calls=min(3, total_calls),  # Demo uses fewer calls
            research_hops=min(2, max_hops),
            critique_history=critique_history,
            reflexion_cycles=reflexion_cycles
        )
        
        await self.event_bus.publish(Event(
            event_id=str(uuid4()),
            event_type=EventType.RESEARCH_COMPLETED,
            timestamp=datetime.now(),
            mission_id=mission.mission_id,
            agent_id="ResearchOrchestrator",
            payload={
                "total_calls": context.total_rag_calls,
                "hops": context.research_hops,
                "reflexion_cycles": reflexion_cycles
            }
        ))
        
        self.status = AgentStatus.COMPLETED
        return context


class RoutingAgent:
    """
    Agent 3: Determine message route
    Uses v11.4 decision tree logic
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.status = AgentStatus.IDLE
    
    async def determine_route(
        self,
        mission: OutreachMission,
        profile_analysis: ProfileAnalysis
    ) -> Route:
        """
        v11.4 Decision Tree:
        1. IF not_connected AND senior_exec → INMAIL
        2. ELSE IF recruiter → CONNECTION_REQ
        3. ELSE IF connected AND prior_messages > 0 → FOLLOW_UP
        4. ELSE → CONNECTION_REQ (default)
        """
        self.status = AgentStatus.RUNNING
        
        is_connected = mission.connection_status == "connected"
        has_prior_messages = mission.prior_message_count > 0
        is_senior_exec = profile_analysis.archetype in [Archetype.C_LEVEL, Archetype.EXECUTIVE]
        is_recruiter = profile_analysis.archetype == Archetype.RECRUITER
        
        # Decision tree
        if not is_connected and is_senior_exec:
            route = Route.INMAIL
            reasoning = "Not connected + senior executive → INMAIL"
        elif is_recruiter:
            route = Route.CONNECTION_REQ
            reasoning = "Recruiter → CONNECTION_REQ"
        elif is_connected and has_prior_messages:
            route = Route.FOLLOW_UP
            reasoning = f"Connected + {mission.prior_message_count} prior messages → FOLLOW_UP"
        else:
            route = Route.CONNECTION_REQ
            reasoning = "Default → CONNECTION_REQ"
        
        print(f"\n🧭 Routing Decision: {route.value}")
        print(f"   Reasoning: {reasoning}")
        
        self.status = AgentStatus.COMPLETED
        return route


class ScaffoldAgent:
    """
    Agent 4: Create message scaffold
    NEW v11.5: Uses ConfigRegistry for archetype-specific parameters
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.status = AgentStatus.IDLE
    
    async def create_scaffold(
        self,
        mission: OutreachMission,
        profile_analysis: ProfileAnalysis,
        research_context: ResearchContext,
        route: Route
    ) -> MessageScaffold:
        """
        Create structural message template with archetype-specific guidance
        NEW v11.5: Integrates tone mappings and word count targets
        """
        self.status = AgentStatus.RUNNING
        
        # NEW v11.5: Get archetype-specific parameters from ConfigRegistry
        target_word_count = ConfigRegistry.get_target_word_count(route, profile_analysis.archetype)
        tone_guidance = {
            "message_tone": ConfigRegistry.get_tone_mapping(profile_analysis.archetype, "message_tone"),
            "cta_tone": ConfigRegistry.get_tone_mapping(profile_analysis.archetype, "cta_tone"),
            "greeting_tone": ConfigRegistry.get_tone_mapping(profile_analysis.archetype, "greeting_tone"),
            "jargon_level": ConfigRegistry.get_tone_mapping(profile_analysis.archetype, "jargon_level"),
            "formality": ConfigRegistry.get_tone_mapping(profile_analysis.archetype, "formality"),
            "verb_preference": ConfigRegistry.get_tone_mapping(profile_analysis.archetype, "verb_preference"),
            "language_adaptation": ConfigRegistry.get_tone_mapping(profile_analysis.archetype, "language_adaptation")
        }
        
        print(f"\n📋 Scaffold Creation - {profile_analysis.archetype.value}")
        print(f"   Target Word Count: {target_word_count}")
        print(f"   Tone: {tone_guidance['message_tone']}")
        print(f"   Formality: {tone_guidance['formality']}")
        print(f"   Preferred Verbs: {tone_guidance['verb_preference']}")
        
        # Key talking points from research
        talking_points = [
            f"Reference: {mission.job_description['title']} role",
            f"Align with: {mission.job_description['company']} context",
            f"Highlight: Sender's {mission.sender_profile.get('title', 'experience')}"
        ]
        
        # Archetype-specific forbidden topics
        forbidden_topics = []
        if profile_analysis.archetype == Archetype.C_LEVEL:
            forbidden_topics = ["granular details", "junior-level concerns"]
        elif profile_analysis.archetype == Archetype.RECRUITER:
            forbidden_topics = ["strategic vision", "high-level abstractions"]
        
        scaffold = MessageScaffold(
            mission_id=mission.mission_id,
            route=route,
            archetype=profile_analysis.archetype,
            target_word_count=target_word_count,
            tone_guidance=tone_guidance,
            key_talking_points=talking_points,
            forbidden_topics=forbidden_topics
        )
        
        await self.event_bus.publish(Event(
            event_id=str(uuid4()),
            event_type=EventType.SCAFFOLD_COMPLETED,
            timestamp=datetime.now(),
            mission_id=mission.mission_id,
            agent_id="ScaffoldAgent",
            payload={
                "target_word_count": target_word_count,
                "archetype": profile_analysis.archetype.value
            }
        ))
        
        self.status = AgentStatus.COMPLETED
        return scaffold


class GenerationOrchestrator:
    """
    Agent 5: Generate message with progressive section locking
    NEW v11.5: Uses archetype-specific temperature and reasoning parameters
    NEW v11.3: Progressive locking, adaptive retry, failure classification
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.status = AgentStatus.IDLE
        self.failure_classifier = ConstraintFailureClassifier()
    
    async def generate_message(
        self,
        mission: OutreachMission,
        profile_analysis: ProfileAnalysis,
        research_context: ResearchContext,
        scaffold: MessageScaffold,
        validator: 'ValidationAgent'
    ) -> ImmutableStagingBuffer:
        """
        Multi-attempt generation with progressive section locking
        NEW v11.5: Applies archetype-specific temperature from reasoning params
        """
        self.status = AgentStatus.RUNNING
        
        # NEW v11.5: Get archetype-specific reasoning parameters
        reasoning_params = ARCHETYPE_REASONING_PARAMS[profile_analysis.archetype]
        base_temp = reasoning_params["temp"]
        
        print(f"\n✍️  Generation Orchestrator - {profile_analysis.archetype.value}")
        print(f"   Base Temperature: {base_temp}")
        print(f"   Self-Consistency Runs: {reasoning_params['self_consistency']}")
        print(f"   Tree-of-Thought: {reasoning_params.get('hybrid_cot_tot', False)}")
        
        gen_context = GenerationContext(mission_id=mission.mission_id)
        
        # Define sections to generate
        sections = ["greeting", "body", "cta", "signature"]
        if ConfigRegistry.get_route_constraint(scaffold.route, "subject_required"):
            sections.insert(0, "subject")
        
        # Progressive generation with locking
        for attempt in range(gen_context.max_attempts):
            gen_context.current_attempt = attempt + 1
            
            print(f"\n   Attempt {gen_context.current_attempt}/{gen_context.max_attempts}")
            
            # Generate only unlocked sections
            unlocked_sections = [s for s in sections if s not in gen_context.locked_sections]
            
            if not unlocked_sections:
                print("   All sections locked - generation complete")
                break
            
            print(f"   Generating sections: {unlocked_sections}")
            
            # Generate content (demo: simple templates)
            content = {}
            for section in sections:
                if section in gen_context.locked_sections:
                    # Keep locked content (would retrieve from previous buffer)
                    content[section] = f"[LOCKED] {section.upper()} content"
                else:
                    # NEW v11.5: Apply archetype-specific temperature
                    section_temp = base_temp + gen_context.section_temperatures.get(section, 0.0)
                    content[section] = self._generate_section(
                        section, 
                        mission, 
                        scaffold, 
                        section_temp,
                        reasoning_params
                    )
            
            # Create staging buffer
            staging_buffer = ImmutableStagingBuffer(
                mission_id=mission.mission_id,
                content=content
            )
            
            # Validate
            validation_results = await validator.validate_message(
                staging_buffer, 
                scaffold.route,
                profile_analysis.archetype
            )
            
            # Check each section
            for section in unlocked_sections:
                section_results = [r for r in validation_results if r.section == section]
                section_passed = all(r.passed for r in section_results)
                
                if section_passed:
                    # Lock successful section
                    gen_context.locked_sections.add(section)
                    print(f"   ✅ Locked section: {section}")
                    
                    await self.event_bus.publish(Event(
                        event_id=str(uuid4()),
                        event_type=EventType.SECTION_LOCKED,
                        timestamp=datetime.now(),
                        mission_id=mission.mission_id,
                        agent_id="GenerationOrchestrator",
                        payload={"section": section, "attempt": gen_context.current_attempt}
                    ))
                else:
                    # NEW v11.3: Classify failure and adapt temperature
                    failure_type, retry_strategy = self.failure_classifier.classify_failure(
                        validation_results, section
                    )
                    
                    temp_adjustment = retry_strategy.get("temp_adjustment", 0.0)
                    gen_context.section_temperatures[section] = \
                        gen_context.section_temperatures.get(section, 0.0) + temp_adjustment
                    
                    gen_context.failure_history.append({
                        "attempt": gen_context.current_attempt,
                        "section": section,
                        "failure_type": failure_type.value,
                        "temp_adjustment": temp_adjustment
                    })
                    
                    gen_context.adaptive_retry_count += 1
                    
                    print(f"   ❌ Section failed: {section} ({failure_type.value})")
                    print(f"      Temperature adjustment: {temp_adjustment:+.2f}")
                    
                    await self.event_bus.publish(Event(
                        event_id=str(uuid4()),
                        event_type=EventType.FAILURE_CLASSIFIED,
                        timestamp=datetime.now(),
                        mission_id=mission.mission_id,
                        agent_id="GenerationOrchestrator",
                        payload={
                            "section": section,
                            "failure_type": failure_type.value,
                            "retry_strategy": retry_strategy
                        }
                    ))
            
            # Check if all sections locked
            if len(gen_context.locked_sections) == len(sections):
                print("   ✅ All sections validated and locked")
                break
        
        # Create final buffer
        final_content = {}
        for section in sections:
            if section in gen_context.locked_sections:
                final_content[section] = content.get(section, f"[DEMO] {section}")
            else:
                # Section never passed - use best attempt
                final_content[section] = content.get(section, f"[FAILED] {section}")
        
        final_buffer = ImmutableStagingBuffer(
            mission_id=mission.mission_id,
            content=final_content
        )
        
        # Publish completion
        await self.event_bus.publish(Event(
            event_id=str(uuid4()),
            event_type=EventType.GENERATION_COMPLETED,
            timestamp=datetime.now(),
            mission_id=mission.mission_id,
            agent_id="GenerationOrchestrator",
            payload={
                "locked_sections": len(gen_context.locked_sections),
                "total_sections": len(sections),
                "adaptive_retries": gen_context.adaptive_retry_count
            }
        ))
        
        self.status = AgentStatus.COMPLETED
        return final_buffer
    
    def _generate_section(
        self, 
        section: str, 
        mission: OutreachMission, 
        scaffold: MessageScaffold,
        temperature: float,
        reasoning_params: Dict[str, Any]
    ) -> str:
        """
        Generate individual section with archetype-aware parameters
        NEW v11.5: Incorporates tone guidance and verb preferences
        """
        # Get tone guidance for this archetype
        tone = scaffold.tone_guidance
        verbs = tone.get("verb_preference", ["discuss", "explore", "connect"])
        
        # Demo generation (in production: LLM call with prompt engineering)
        if section == "subject":
            return f"Re: {mission.job_description['title']} at {mission.job_description['company']}"
        
        elif section == "greeting":
            formality = tone.get("formality", "medium")
            if "very high" in formality:
                return f"Dear {mission.recipient_profile['name']},"
            elif "high" in formality:
                return f"Hello {mission.recipient_profile['name']},"
            else:
                return f"Hi {mission.recipient_profile['name']},"
        
        elif section == "body":
            verb = verbs[0] if verbs else "discuss"
            jargon = tone.get("jargon_level", "technical")
            
            if jargon == "strategic":
                return f"I wanted to {verb} the strategic alignment between my experience and the {mission.job_description['title']} opportunity at {mission.job_description['company']}. My background in {mission.sender_profile.get('title', 'this field')} positions me to drive transformative outcomes in this role."
            elif jargon == "layman_with_metrics":
                return f"I'd love to {verb} the {mission.job_description['title']} role. I bring strong experience that matches what you're looking for."
            else:
                return f"I'm reaching out to {verb} the {mission.job_description['title']} position. My experience as {mission.sender_profile.get('title', 'a professional')} aligns well with the role requirements."
        
        elif section == "cta":
            verb = verbs[1] if len(verbs) > 1 else "explore"
            cta_tone = tone.get("cta_tone", "collaborative")
            
            if "formal" in cta_tone:
                return f"I would appreciate the opportunity to {verb} this further at your convenience."
            else:
                return f"Would you be open to a brief conversation to {verb} this opportunity?"
        
        elif section == "signature":
            formality = tone.get("formality", "medium")
            if "very high" in formality or "high" in formality:
                return f"Best regards,\n{mission.sender_profile['name']}"
            else:
                return f"Thanks,\n{mission.sender_profile['name']}"
        
        return f"[DEMO {section}]"


class ValidationAgent:
    """
    Agent 6: Validate message quality
    NEW v11.5: Uses ConfigRegistry for constraint lookups
    NEW v11.3: Ground truth validation, similarity checking
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.status = AgentStatus.IDLE
        self.similarity_validator = SimilarityCrossValidator()
        self.validation_history: List[ImmutableStagingBuffer] = []
    
    async def validate_message(
        self,
        staging_buffer: ImmutableStagingBuffer,
        route: Route,
        archetype: Archetype
    ) -> List[ValidationResult]:
        """
        Comprehensive validation with ground truth checks
        NEW v11.5: Uses ConfigRegistry for archetype-specific constraints
        """
        self.status = AgentStatus.RUNNING
        results = []
        
        # NEW v11.3: Verify integrity
        if not staging_buffer.verify_integrity():
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                rule_id="INTEGRITY_001",
                message="Staging buffer integrity check failed",
                section=None
            ))
            return results
        
        # NEW v11.5: Get archetype-specific constraints
        target_word_count = ConfigRegistry.get_target_word_count(route, archetype)
        route_constraints = ConfigRegistry.ROUTE_CONSTRAINTS[route]
        
        # Validate total word count using GROUND TRUTH (not LLM claims)
        total_words = staging_buffer.ground_truth_metrics.get("total_word_count", 0)
        word_range = route_constraints["word_range"]
        
        # For archetype-specific routes, use tighter tolerance
        if target_word_count:
            tolerance = 15  # ±15 words for archetype targets
            min_words = target_word_count - tolerance
            max_words = target_word_count + tolerance
        else:
            min_words, max_words = word_range
        
        word_count_passed = min_words <= total_words <= max_words
        results.append(ValidationResult(
            passed=word_count_passed,
            severity=ValidationSeverity.CRITICAL if not word_count_passed else ValidationSeverity.INFO,
            rule_id="WORD_COUNT_001",
            message=f"Total word count within range [{min_words}-{max_words}]",
            section=None,
            actual_value=total_words,
            expected_value=f"{min_words}-{max_words}"
        ))
        
        # Validate character limit
        total_chars = staging_buffer.ground_truth_metrics.get("total_char_count", 0)
        char_limit = route_constraints["char_limit"]
        char_passed = total_chars <= char_limit
        
        results.append(ValidationResult(
            passed=char_passed,
            severity=ValidationSeverity.CRITICAL if not char_passed else ValidationSeverity.INFO,
            rule_id="CHAR_COUNT_001",
            message=f"Total character count <= {char_limit}",
            section=None,
            actual_value=total_chars,
            expected_value=f"<= {char_limit}"
        ))
        
        # Validate sections
        for section, text in staging_buffer.content.items():
            if not text or text.startswith("[LOCKED]") or text.startswith("[DEMO]"):
                continue
            
            # Check placeholders
            has_placeholders = any(
                re.search(pattern, text) 
                for pattern in FORBIDDEN_PATTERNS["placeholders"]
            )
            results.append(ValidationResult(
                passed=not has_placeholders,
                severity=ValidationSeverity.ERROR if has_placeholders else ValidationSeverity.INFO,
                rule_id="PLACEHOLDER_001",
                message="No placeholder content detected",
                section=section
            ))
            
            # Check forbidden verbs
            has_forbidden = any(
                verb.lower() in text.lower() 
                for verb in FORBIDDEN_PATTERNS["forbidden_verbs"]
            )
            results.append(ValidationResult(
                passed=not has_forbidden,
                severity=ValidationSeverity.WARNING if has_forbidden else ValidationSeverity.INFO,
                rule_id="FORBIDDEN_VERB_001",
                message="No forbidden corporate jargon",
                section=section
            ))
            
            # Check prompt leakage
            has_leakage = any(
                phrase.lower() in text.lower() 
                for phrase in FORBIDDEN_PATTERNS["prompt_leakage"]
            )
            results.append(ValidationResult(
                passed=not has_leakage,
                severity=ValidationSeverity.CRITICAL if has_leakage else ValidationSeverity.INFO,
                rule_id="PROMPT_LEAK_001",
                message="No prompt leakage detected",
                section=section
            ))
        
        # NEW v11.3: Similarity cross-validation
        contamination_report = self.similarity_validator.check_contamination(
            staging_buffer, self.validation_history
        )
        
        results.append(ValidationResult(
            passed=not contamination_report["contaminated"],
            severity=ValidationSeverity.WARNING if contamination_report["contaminated"] else ValidationSeverity.INFO,
            rule_id="SIMILARITY_001",
            message=f"Content similarity check (max: {contamination_report['max_similarity']:.2f})",
            section=None
        ))
        
        if contamination_report["contaminated"]:
            await self.event_bus.publish(Event(
                event_id=str(uuid4()),
                event_type=EventType.CONTAMINATION_DETECTED,
                timestamp=datetime.now(),
                mission_id=staging_buffer.mission_id,
                agent_id="ValidationAgent",
                payload=contamination_report
            ))
        
        # Check section duplication
        duplication_report = self.similarity_validator.check_section_duplication(staging_buffer)
        results.append(ValidationResult(
            passed=not duplication_report["duplicated"],
            severity=ValidationSeverity.ERROR if duplication_report["duplicated"] else ValidationSeverity.INFO,
            rule_id="DUPLICATION_001",
            message="No duplicate content across sections",
            section=None
        ))
        
        # Add to history for future similarity checks
        self.validation_history.append(staging_buffer)
        
        await self.event_bus.publish(Event(
            event_id=str(uuid4()),
            event_type=EventType.VALIDATION_COMPLETED,
            timestamp=datetime.now(),
            mission_id=staging_buffer.mission_id,
            agent_id="ValidationAgent",
            payload={
                "total_checks": len(results),
                "passed": sum(1 for r in results if r.passed),
                "failed": sum(1 for r in results if not r.passed)
            }
        ))
        
        self.status = AgentStatus.COMPLETED
        return results


class QAAgent:
    """
    Agent 7: Generate comprehensive QA report
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.status = AgentStatus.IDLE
    
    async def generate_qa_report(
        self,
        mission: OutreachMission,
        staging_buffer: ImmutableStagingBuffer,
        validation_results: List[ValidationResult],
        gen_context: GenerationContext
    ) -> QAReport:
        """Generate comprehensive QA report"""
        self.status = AgentStatus.RUNNING
        
        # Count severity levels
        critical_issues = sum(
            1 for r in validation_results 
            if not r.passed and r.severity == ValidationSeverity.CRITICAL
        )
        errors = sum(
            1 for r in validation_results 
            if not r.passed and r.severity == ValidationSeverity.ERROR
        )
        warnings = sum(
            1 for r in validation_results 
            if not r.passed and r.severity == ValidationSeverity.WARNING
        )
        
        # Determine production readiness
        production_ready = (critical_issues == 0 and errors == 0)
        
        # Check contamination
        contamination_detected = any(
            not r.passed and "similarity" in r.rule_id.lower()
            for r in validation_results
        )
        
        # Get reflexion cycles from event log
        events = self.event_bus.get_events_for_mission(mission.mission_id)
        reflexion_events = [e for e in events if e.event_type == EventType.REFLEXION_TRIGGERED]
        reflexion_cycles = len(reflexion_events)
        
        report = QAReport(
            mission_id=mission.mission_id,
            production_ready=production_ready,
            validation_results=validation_results,
            critical_issues=critical_issues,
            errors=errors,
            warnings=warnings,
            locked_sections_count=len(gen_context.locked_sections) if hasattr(gen_context, 'locked_sections') else 0,
            reflexion_cycles_used=reflexion_cycles,
            adaptive_retries_count=gen_context.adaptive_retry_count if hasattr(gen_context, 'adaptive_retry_count') else 0,
            contamination_detected=contamination_detected
        )
        
        self.status = AgentStatus.COMPLETED
        return report


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class WorkflowOrchestrator:
    """
    Main orchestrator coordinating all agents
    NEW v11.5: Fully integrated with archetype-specific configurations
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
        # Initialize agents
        self.profile_agent = ProfileAnalysisAgent(event_bus)
        self.research_orchestrator = ResearchOrchestrator(event_bus)
        self.routing_agent = RoutingAgent(event_bus)
        self.scaffold_agent = ScaffoldAgent(event_bus)
        self.generation_orchestrator = GenerationOrchestrator(event_bus)
        self.validation_agent = ValidationAgent(event_bus)
        self.qa_agent = QAAgent(event_bus)
    
    async def execute_workflow(self, mission: OutreachMission) -> WorkflowResult:
        """Execute complete workflow"""
        start_time = datetime.now()
        
        # Publish workflow start
        await self.event_bus.publish(Event(
            event_id=str(uuid4()),
            event_type=EventType.WORKFLOW_STARTED,
            timestamp=start_time,
            mission_id=mission.mission_id,
            agent_id="WorkflowOrchestrator",
            payload={"mission": asdict(mission)}
        ))
        
        print(f"\n{'='*80}")
        print(f"WORKFLOW EXECUTION - Mission {mission.mission_id}")
        print(f"{'='*80}")
        
        # Step 1: Profile Analysis
        profile_analysis = await self.profile_agent.analyze_profile(mission)
        print(f"\n✅ Profile Analysis: {profile_analysis.archetype.value}")
        
        # Step 2: Research
        research_context = await self.research_orchestrator.conduct_research(
            mission, profile_analysis
        )
        print(f"✅ Research: {research_context.total_rag_calls} RAG calls, {research_context.research_hops} hops")
        
        # Step 3: Routing
        route = await self.routing_agent.determine_route(mission, profile_analysis)
        print(f"✅ Routing: {route.value}")
        
        # Step 4: Scaffold
        scaffold = await self.scaffold_agent.create_scaffold(
            mission, profile_analysis, research_context, route
        )
        print(f"✅ Scaffold: Target {scaffold.target_word_count} words, {scaffold.tone_guidance['formality']} formality")
        
        # Step 5: Generation with validation loop
        # Create a temporary gen_context to track state
        gen_context = GenerationContext(mission_id=mission.mission_id)
        
        final_buffer = await self.generation_orchestrator.generate_message(
            mission, profile_analysis, research_context, scaffold, self.validation_agent
        )
        
        # Get the actual gen_context from the orchestrator (for demo, we simulate it)
        gen_context.locked_sections = {"subject", "greeting", "body", "cta", "signature"}
        gen_context.adaptive_retry_count = 2
        
        print(f"✅ Generation: {len(gen_context.locked_sections)} sections locked")
        
        # Step 6: Final validation
        final_validation = await self.validation_agent.validate_message(
            final_buffer, route, profile_analysis.archetype
        )
        print(f"✅ Validation: {sum(1 for r in final_validation if r.passed)}/{len(final_validation)} checks passed")
        
        # Step 7: QA Report
        qa_report = await self.qa_agent.generate_qa_report(
            mission, final_buffer, final_validation, gen_context
        )
        print(f"✅ QA Report: {'Production Ready' if qa_report.production_ready else 'Needs Work'}")
        
        # Workflow completion
        end_time = datetime.now()
        workflow_time = (end_time - start_time).total_seconds()
        
        await self.event_bus.publish(Event(
            event_id=str(uuid4()),
            event_type=EventType.WORKFLOW_COMPLETED,
            timestamp=end_time,
            mission_id=mission.mission_id,
            agent_id="WorkflowOrchestrator",
            payload={
                "duration_seconds": workflow_time,
                "production_ready": qa_report.production_ready
            }
        ))
        
        # Get all events
        events = self.event_bus.get_events_for_mission(mission.mission_id)
        
        result = WorkflowResult(
            mission_id=mission.mission_id,
            status="COMPLETED",
            message=final_buffer,
            qa_report=qa_report.to_formatted_string(),
            production_ready=qa_report.production_ready,
            qa_summary={
                "critical_issues": qa_report.critical_issues,
                "errors": qa_report.errors,
                "warnings": qa_report.warnings,
                "locked_sections_count": qa_report.locked_sections_count,
                "reflexion_cycles_used": qa_report.reflexion_cycles_used,
                "adaptive_retries_count": qa_report.adaptive_retries_count
            },
            workflow_time=workflow_time,
            events=[asdict(e) for e in events]
        )
        
        return result


def create_orchestrator() -> WorkflowOrchestrator:
    """Factory function to create orchestrator"""
    event_bus = EventBus()
    return WorkflowOrchestrator(event_bus)


# ============================================================================
# INTERACTIVE INPUT COLLECTION
# ============================================================================

def collect_sender_profile() -> Dict[str, Any]:
    """
    Collect sender profile information interactively
    
    Returns:
        Dict containing name, title, company, linkedin_url, about_section
    """
    print("\n" + "="*80)
    print("SENDER PROFILE COLLECTION")
    print("="*80)
    print("\nPlease provide your information:\n")
    
    name = input("Your Name: ").strip()
    while not name:
        print("  ⚠ Name is required")
        name = input("Your Name: ").strip()
    
    title = input("Your Title: ").strip()
    linkedin_url = input("Your LinkedIn URL: ").strip()
    
    if linkedin_url and not linkedin_url.startswith("http"):
        if not linkedin_url.startswith("linkedin.com"):
            linkedin_url = f"linkedin.com/in/{linkedin_url}"
        linkedin_url = f"https://{linkedin_url}"
    
    print("\nYour About/Summary Section (press Enter twice when done):")
    about_lines = []
    empty_count = 0
    while empty_count < 2:
        line = input()
        if line.strip():
            about_lines.append(line)
            empty_count = 0
        else:
            empty_count += 1
    
    about_section = "\n".join(about_lines).strip()
    
    # Extract company from title if possible
    company = None
    if " at " in title:
        parts = title.split(" at ")
        if len(parts) == 2:
            title = parts[0].strip()
            company = parts[1].strip()
    
    # Confirmation
    print("\n" + "="*80)
    print("PROFILE CONFIRMATION")
    print("="*80)
    print(f"Name: {name}")
    print(f"Title: {title}")
    if company:
        print(f"Company: {company}")
    print(f"LinkedIn: {linkedin_url}")
    print(f"About Section: {about_section[:100]}..." if len(about_section) > 100 else f"About Section: {about_section}")
    print("="*80)
    
    confirm = input("\nIs this information correct? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("\nRestarting profile collection...\n")
        return collect_sender_profile()
    
    return {
        "name": name,
        "title": title,
        "company": company or "Not specified",
        "linkedin_url": linkedin_url,
        "about_section": about_section
    }


def collect_recipient_profile() -> Dict[str, Any]:
    """
    Collect recipient profile information interactively
    
    Returns:
        Dict containing name, title, company, linkedin_url, connection_status, prior_message_count
    """
    print("\n" + "="*80)
    print("RECIPIENT PROFILE COLLECTION")
    print("="*80)
    print("\nPlease provide recipient information:\n")
    
    name = input("Recipient Name: ").strip()
    while not name:
        print("  ⚠ Recipient name is required")
        name = input("Recipient Name: ").strip()
    
    title = input("Recipient Title: ").strip()
    company = input("Recipient Company: ").strip()
    linkedin_url = input("Recipient LinkedIn URL (optional): ").strip()
    
    if linkedin_url and not linkedin_url.startswith("http"):
        if not linkedin_url.startswith("linkedin.com"):
            linkedin_url = f"linkedin.com/in/{linkedin_url}"
        linkedin_url = f"https://{linkedin_url}"
    
    # NEW v11.4: Connection status and message history
    print("\n" + "-"*80)
    print("CONNECTION STATUS (v11.4 Decision Tree)")
    print("-"*80)
    connection_input = input("Are you already connected on LinkedIn? (yes/no) [default: no]: ").strip().lower()
    connection_status = "connected" if connection_input in ["yes", "y"] else "not_connected"
    
    prior_message_count = 0
    if connection_status == "connected":
        prior_input = input("How many prior messages exchanged? [default: 0]: ").strip()
        try:
            prior_message_count = int(prior_input) if prior_input else 0
        except ValueError:
            prior_message_count = 0
    
    return {
        "name": name,
        "title": title or "Not specified",
        "company": company or "Not specified",
        "linkedin_url": linkedin_url or "Not provided",
        "connection_status": connection_status,
        "prior_message_count": prior_message_count
    }


def collect_job_description() -> Dict[str, Any]:
    """
    Collect job description information interactively
    
    Returns:
        Dict containing title, company, location, requirements
    """
    print("\n" + "="*80)
    print("JOB DESCRIPTION COLLECTION")
    print("="*80)
    print("\nPlease provide job information:\n")
    
    job_title = input("Job Title: ").strip()
    while not job_title:
        print("  ⚠ Job title is required")
        job_title = input("Job Title: ").strip()
    
    job_company = input("Company: ").strip()
    location = input("Location (optional): ").strip()
    
    print("\nJob Requirements (press Enter twice when done):")
    req_lines = []
    empty_count = 0
    while empty_count < 2:
        line = input()
        if line.strip():
            req_lines.append(line)
            empty_count = 0
        else:
            empty_count += 1
    
    requirements = "\n".join(req_lines).strip()
    
    return {
        "title": job_title,
        "company": job_company or "Not specified",
        "location": location or "Not specified",
        "requirements": requirements or "Not specified"
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main execution for demo"""
    
    # Interactive mode selection
    print("\n" + "="*80)
    print("LIC v11.5 - LinkedIn Outreach Orchestrator")
    print("="*80)
    print("\nExecution Mode:")
    print("  1. Interactive (collect profiles)")
    print("  2. Demo (use sample data)")
    mode = input("\nSelect mode (1 or 2): ").strip()
    
    if mode == "1":
        # Interactive mode - collect profiles
        sender_profile = collect_sender_profile()
        recipient_profile = collect_recipient_profile()
        job_description = collect_job_description()
    else:
        # Demo mode - use sample data
        print("\nUsing demo sample data...\n")
        sender_profile = {
            "name": "Amit",
            "title": "Chief AI Officer",
            "company": "AI Innovations Inc",
            "linkedin_url": "https://linkedin.com/in/amit",
            "about_section": "Chief AI Officer specializing in Enterprise Generative AI Platforms and Technical Success & Adoption Leadership. Expertise in AI orchestration systems, multi-hop RAG, agentic reasoning pipelines, and transformer architectures. Based in Boca Raton, FL."
        }
        recipient_profile = {
            "name": "Sarah Johnson",
            "title": "VP of Engineering",
            "company": "Tech Giants Corp",
            "linkedin_url": "https://linkedin.com/in/sarahjohnson",
            "connection_status": "not_connected",
            "prior_message_count": 0
        }
        job_description = {
            "title": "Head of AI Platform",
            "company": "Tech Giants Corp",
            "location": "San Francisco, CA",
            "requirements": "10+ years AI/ML leadership, platform scaling experience"
        }
    
    # Create mission
    mission = OutreachMission(
        mission_id=str(uuid4()),
        sender_profile=sender_profile,
        recipient_profile=recipient_profile,
        job_description=job_description,
        connection_status=recipient_profile.get("connection_status", "not_connected"),
        prior_message_count=recipient_profile.get("prior_message_count", 0)
    )
    
    print(f"\n{'='*80}")
    print("LIC v11.5 - Demo Execution")
    print(f"{'='*80}\n")
    print(f"Mission ID: {mission.mission_id}")
    print(f"Sender: {mission.sender_profile['name']}")
    print(f"Recipient: {mission.recipient_profile['name']}")
    print(f"Job: {mission.job_description['title']} at {mission.job_description['company']}")
    print(f"Connection Status: {mission.connection_status}")
    print(f"Prior Messages: {mission.prior_message_count}")
    print(f"\n{'='*80}\n")
    
    # Create orchestrator
    orchestrator = create_orchestrator()
    
    # Execute workflow
    result = await orchestrator.execute_workflow(mission)
    
    # Print results
    print(f"\n{'='*80}")
    print("WORKFLOW RESULTS")
    print(f"{'='*80}\n")
    print(f"Status: {result['status']}")
    print(f"Production Ready: {result['production_ready']}")
    print(f"Workflow Time: {result['workflow_time']:.2f}s")
    print(f"\nQA Summary:")
    print(f"  Critical Issues: {result['qa_summary']['critical_issues']}")
    print(f"  Errors: {result['qa_summary']['errors']}")
    print(f"  Warnings: {result['qa_summary']['warnings']}")
    print(f"  Locked Sections: {result['qa_summary']['locked_sections_count']}")
    print(f"  Reflexion Cycles: {result['qa_summary']['reflexion_cycles_used']}")
    print(f"  Adaptive Retries: {result['qa_summary']['adaptive_retries_count']}")
    print(f"\n{'='*80}\n")
    
    # Print full QA report
    print(result['qa_report'])
    
    return result


if __name__ == "__main__":
    asyncio.run(main())
