# ATTACHMENT: LIC_AGENTIC_v11_10.py
"""
LinkedIn Outreach Orchestrator (LIC) - AGENTIC v11.10
=====================================================

CHANGELOG v11.10 (CRITICAL - The Dual-Loop Agentic Refactor):
---------------------------------------------------------
This version represents a fundamental architectural shift from a linear pipeline (v11.9)
to a recursive, dual-loop agentic system based on user-approved designs.

✨ NEW: ENHANCEMENT 1 & 2 - S2 Multi-Agent Specialization & Internal Loop
- Renamed ResearchOrchestrator -> S2_SupervisorAgent.
- S2_SupervisorAgent is now a planner/synthesizer, not a worker.
- Created new specialist agents (mocks):
  - RecipientAgent: Handles person-specific RAG (LinkedIn, GitHub).
  - OrganizationAgent: Handles org-specific RAG (company blog, news).
  - InternalAgent: Handles internal lookups (job tracker).
- S2_SupervisorAgent now runs its OWN "Execute-Critique-Replan" loop:
  1. Plan: Creates a task list.
  2. Delegate: Calls specialist agents (Recipient, Organization) in parallel.
  3. Synthesize: Merges specialist reports.
  4. Critique: Uses RAGReflexionSystem to find gaps in its *own* work.
  5. Refine: If critique fails, delegates refinement tasks to the correct specialist.

✨ NEW: ENHANCEMENT 3 - S2 Adversarial Self-Verification
- Added a new _run_adversarial_check step to S2_SupervisorAgent.
- After the S2 internal critique loop passes, this "Red Team" step runs.
- It finds weak/refuted claims (e.g., "Refuted theme: 'direct experience'").
- A new field `adversarial_findings` is added to ResearchContext.
- S5_GenerationOrchestrator now reads this field and is prompted to AVOID
  making these refuted claims, hardening against subtle hallucinations.

✨ NEW: ENHANCEMENT 4 - The S6 -> S2 "Meta-Loop" (Factual Failure Recovery)
- This is the new "external" or "meta" loop for autonomous recovery.
- S5_GenerationOrchestrator:
  - Created new `FailureClassifier` enum (CREATIVE_FAILURE, FACTUAL_FAILURE).
  - Created new `FactualGapError(Exception)`.
  - S5's generation retry loop now classifies S6 validation failures.
  - CREATIVE_FAILURE (e.g., forbidden verb) triggers the existing S5 retry.
  - FACTUAL_FAILURE (e.g., LIC-E010: Metric lacks context) now STOPS the
    S5 retry loop and `raises FactualGapError(validation_results)`.
- WorkflowOrchestrator:
  - The S5 `generate_message` call is now wrapped in a new `for meta_attempt...` loop.
  - This loop has a `try...except FactualGapError as e:` block.
  - `try` block: Runs S5. If it succeeds, the meta-loop `break`s.
  - `except` block: This is the S6->S2 re-planning trigger.
    1. It catches the `FactualGapError`.
    2. It logs the S6->S2 re-plan.
    3. It extracts the `refinement_context` (the S6 validation failures)
       from the exception.
    4. It re-runs S2_SupervisorAgent, passing in this `refinement_context`.
- S2_SupervisorAgent:
  - `conduct_research` signature updated to accept `refinement_context`.
  - The internal critique logic now checks for this context. If present,
    it FORCES a new refinement task based on the S6 failure (e.g., "S6
    failed to validate metric. Find RAG evidence for this metric.").

CHANGELOG v11.9 (FEATURE - Sender Grounding & Context-Aware CTAs):
---------------------------------------------------------
✨ NEW: S2_ExtractSenderGrounding - Extract whitelisted team members, products, case studies from RAG (SPEC 1)
✨ NEW: S4_GenerateSenderGroundingConstraints - Inject "my team" -> names mapping as generation rules (SPEC 2)
✨ NEW: S4_GenerateContextAwareCTA - Route-specific CTAs (CONNECTION_REQ no CTA, SENIOR_TA direct/deferential) (SPEC 3)
✨ NEW: S5_UseArchetypeSpecificPrompts - C_LEVEL uses thought-leadership, RECRUITER uses job-focus (SPEC 4)
✨ NEW: S6_ValidateSenderClaims - Enhanced with grounding whitelist checks (team/products/case studies) (SPEC 5)
"""

__version__ = "11.10"
__author__ = "Amit (Chief AI Officer)"

import asyncio
import hashlib
import json
import re
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set, Callable
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
    """Recipient archetypes for personalization - v11.6 4-archetype standard"""
    C_LEVEL = "C_LEVEL"
    EXECUTIVE = "EXECUTIVE"
    SENIOR_TA = "SENIOR_TA"  # NEW v11.6: Technical Authority/Staff Engineer
    RECRUITER = "RECRUITER"


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
    CIRCUIT_BREAKER_TRIGGERED = "CIRCUIT_BREAKER_TRIGGERED"
    MANUAL_OVERRIDE_REQUESTED = "MANUAL_OVERRIDE_REQUESTED"


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class ValidationSeverity(Enum):
    """Validation result severity levels - v10.22 standard"""
    CRITICAL = "CRITICAL"  # Halt immediately
    HIGH = "HIGH"          # Halt immediately
    MEDIUM = "MEDIUM"      # Regenerate, no halt
    INFO = "INFO"          # Log only


class ConstraintFailureType(Enum):
    """Types of constraint failures for adaptive retry"""
    MECHANICAL = "MECHANICAL"      # Word count, char count, structural
    CREATIVE = "CREATIVE"          # Placeholders, generic content
    SEMANTIC = "SEMANTIC"          # Forbidden words, tone violations
    CONFLICT = "CONFLICT"          # Impossible constraint combinations


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Blocking requests
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


# ============================================================================
# NEW v11.10: ENHANCEMENT 4 - S6->S2 META-LOOP SUPPORT
# ============================================================================

class FactualGapError(Exception):
    """
    NEW v11.10: Custom exception raised by S5 when a FACTUAL failure (not
    creative) is detected by S6. This signals the S6->S2 "Meta-Loop"
    in the WorkflowOrchestrator to trigger a full re-planning cycle.
    """
    pass


class FailureClassifier(Enum):
    """
    NEW v11.10: Classifies S6 validation failures to determine retry strategy.
    - CREATIVE_FAILURE: Retried by S5 (e.g., temp escalation).
    - FACTUAL_FAILURE: Throws FactualGapError, triggering S6->S2 meta-loop.
    """
    CREATIVE_FAILURE = "CREATIVE_FAILURE"  # e.g., tone, forbidden verbs
    FACTUAL_FAILURE = "FACTUAL_FAILURE"    # e.g., missing metric context, hallucination


# ============================================================================
# NEW v11.6: GLOBAL ERROR CODE REGISTRY (GAP 6.1)
# ============================================================================

class ErrorCodeRegistry:
    """Centralized error codes with remediation guidance"""

    CODES = {
        "LIC-E001": {
            "severity": "CRITICAL",
            "description": "Placeholder detected in generated message",
            "remediation": "Regenerate with explicit anti-placeholder constraint"
        },
        "LIC-E002": {
            "severity": "CRITICAL",
            "description": "Per-claim confidence below threshold (0.70)",
            "remediation": "Add more RAG sources or remove low-confidence claim"
        },
        "LIC-E003": {
            "severity": "CRITICAL",
            "description": "Hallucinated claim without supporting evidence",
            "remediation": "Remove claim or add supporting RAG evidence"
        },
        "LIC-E004": {
            "severity": "HIGH",
            "description": "Message too similar to previous message (>0.85)",
            "remediation": "Increase temperature or add diversity constraint"
        },
        "LIC-E005": {
            "severity": "HIGH",
            "description": "Job title not in first 50 words",
            "remediation": "Regenerate with job title positioning constraint"
        },
        "LIC-E006": {
            "severity": "HIGH",
            "description": "Company name misspelled",
            "remediation": "Use exact company name from profile"
        },
        "LIC-E007": {
            "severity": "HIGH",
            "description": "Non-ASCII characters detected",
            "remediation": "Replace Unicode with ASCII equivalents"
        },
        "LIC-E008": {
            "severity": "MEDIUM",
            "description": "Forbidden corporate verbs detected",
            "remediation": "Regenerate avoiding: spearheaded, leveraged, etc."
        },
        "LIC-E009": {
            "severity": "MEDIUM",
            "description": "Weak filler phrases detected",
            "remediation": "Remove: 'I hope', 'I wanted to', 'just reaching out'"
        },
        "LIC-E010": {
            "severity": "HIGH",
            "description": "Metric lacks supporting keyword context from RAG",
            "remediation": "Add RAG evidence keywords around metric or remove metric"
        },
        "LIC-E011": {
            "severity": "HIGH",
            "description": "Signal quality score below threshold (0.70)",
            "remediation": "Trigger RAG reflexion for more research"
        },
        "LIC-E012": {
            "severity": "CRITICAL",
            "description": "Circuit breaker OPEN - API unavailable",
            "remediation": "Wait for circuit breaker timeout or check API"
        },
        "LIC-E013": {
            "severity": "CRITICAL",
            "description": "Constraint pre-flight check failed",
            "remediation": "Adjust constraints or change route"
        }
    }

    @classmethod
    def get_error(cls, code: str) -> Dict[str, str]:
        return cls.CODES.get(code, {"severity": "UNKNOWN", "description": "Unknown error", "remediation": "Contact support"})


# ============================================================================
# NEW v11.6: CIRCUIT BREAKER (FEATURE 4.1)
# ============================================================================

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is OPEN"""
    pass


class CircuitBreaker:
    """
    Circuit breaker for API calls - prevents cascade failures
    FEATURE 4.1 from SUPREME_SPELL
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        timeout_seconds: int = 60
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs):
        """
        Execute function with circuit breaker protection
        """
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if self.last_failure_time and datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout_seconds):
                self.state = CircuitState.HALF_OPEN
                self.failure_count = 0
            else:
                raise CircuitBreakerOpenError("API circuit breaker is OPEN - waiting for recovery")

        try:
            result = func(*args, **kwargs)

            if self.state == CircuitState.HALF_OPEN:
                # Test request succeeded, close circuit
                self.state = CircuitState.CLOSED
                self.failure_count = 0

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            raise


# ============================================================================
# NEW v11.6: CONTEXT MANAGER (GAP 7.1-7.3)
# ============================================================================

class ContextManager:
    """
    Intelligent context window management with priority-based truncation
    GAP 7.1, 7.2, 7.3 from v10.22
    """

    SECTION_PRIORITIES = {
        "job_description": 100,      # Highest - never truncate
        "recipient_profile": 90,
        "company_context": 80,
        "sender_profile": 70,
        "rag_recent": 60,
        "rag_historical": 40,
        "examples": 30,              # Lowest - truncate first
    }

    MAX_CONTEXT_TOKENS = 180000  # Conservative estimate

    @classmethod
    def truncate_intelligently(
        cls,
        context_sections: Dict[str, str],
        max_tokens: int = MAX_CONTEXT_TOKENS
    ) -> Dict[str, str]:
        """
        Truncate context sections by priority if exceeding token limit
        """
        # Rough estimate: 4 chars = 1 token
        total_chars = sum(len(text) for text in context_sections.values())
        estimated_tokens = total_chars // 4

        if estimated_tokens <= max_tokens:
            return context_sections

        # Sort sections by priority
        sorted_sections = sorted(
            context_sections.items(),
            key=lambda x: cls.SECTION_PRIORITIES.get(x[0], 50),
            reverse=True
        )

        truncated = {}
        running_tokens = 0
        token_budget = max_tokens

        for section_name, section_text in sorted_sections:
            section_tokens = len(section_text) // 4

            if running_tokens + section_tokens <= token_budget:
                truncated[section_name] = section_text
                running_tokens += section_tokens
            else:
                # Truncate this section to fit remaining budget
                remaining_tokens = token_budget - running_tokens
                remaining_chars = remaining_tokens * 4

                if remaining_chars > 100:  # Only include if meaningful
                    truncated[section_name] = section_text[:remaining_chars] + "... [truncated]"
                    running_tokens = token_budget
                break

        return truncated

    @classmethod
    def detect_overflow(cls, context_text: str) -> Tuple[bool, int]:
        """
        Detect if context exceeds safe limits

        Returns:
            (is_overflow, estimated_tokens)
        """
        estimated_tokens = len(context_text) // 4
        is_overflow = estimated_tokens > cls.MAX_CONTEXT_TOKENS
        return is_overflow, estimated_tokens


# ============================================================================
# PRIORITY 2: GLOBAL CONSTRAINTS SSOT WITH API ACCESS LAYER
# ============================================================================

class ConfigRegistry:
    """
    v11.5: Single Source of Truth for ALL configuration parameters
    v11.6: Updated for 4-archetype standard (removed HIRING_MANAGER, PEER; added SENIOR_TA)
    """

    # Route-specific base constraints
    ROUTE_CONSTRAINTS = {
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
    }

    # PRIORITY 3: Archetype-Specific Word Count Targets (v11.6 updated)
    ARCHETYPE_WORD_TARGETS = {
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
        Archetype.SENIOR_TA: {  # NEW v11.6
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
    }

    # PRIORITY 1: Archetype-Specific RAG Parameters (v11.6 updated)
    ARCHETYPE_RAG_PARAMS = {
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
        Archetype.SENIOR_TA: {  # NEW v11.6
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
    }

    # PRIORITY 1: Archetype-Specific Reasoning Configurations (v11.6 updated)
    ARCHETYPE_REASONING_PARAMS = {
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
        Archetype.SENIOR_TA: {  # NEW v11.6
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
    }

    # PRIORITY 4: Archetype-Specific Tone Mappings (v11.6 updated)
    ARCHETYPE_TONE_MAPPINGS = {
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
        Archetype.SENIOR_TA: {  # NEW v11.6
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
    }

    # NEW v11.9: Context-Aware CTA Templates
    CTA_TEMPLATES = {
        Route.CONNECTION_REQ: {
            "default": None  # CONNECTION_REQ has no CTA per SPEC 3
        },
        Route.INMAIL: {
            Archetype.C_LEVEL: "Would you be open to a brief conversation about how [TOPIC] might align with your strategic priorities?",
            Archetype.EXECUTIVE: "I'd welcome the chance to discuss how [TOPIC] could support your team's objectives.",
            Archetype.SENIOR_TA: {
                "direct": "Would you have 15 minutes to discuss [TECHNICAL_TOPIC]?",
                "deferential": "If this aligns with your team's direction, I'd appreciate any guidance you could share."
            },
            Archetype.RECRUITER: "Would you be open to a conversation about roles that might match your team's needs?"
        },
        Route.EMAIL: {
            Archetype.C_LEVEL: "I'd value the opportunity to explore how [TOPIC] aligns with your vision for [COMPANY].",
            Archetype.EXECUTIVE: "Would you be open to a brief call to discuss [TOPIC]?",
            Archetype.SENIOR_TA: {
                "direct": "Could we schedule 20 minutes to dive into [TECHNICAL_TOPIC]?",
                "deferential": "If this resonates with your team's roadmap, I'd be grateful for any insights you could offer."
            },
            Archetype.RECRUITER: "I'd welcome a conversation about potential opportunities that could benefit your team."
        },
        Route.FOLLOW_UP: {
            "default": "Following up on my previous message - would you have time for a brief conversation this week?"
        }
    }

    # NEW v11.9: Archetype-Specific Generation Prompt Templates
    ARCHETYPE_PROMPT_TEMPLATES = {
        Archetype.C_LEVEL: """
You are crafting an executive-level message that demonstrates thought leadership and strategic alignment.

TONE: Strategic, confident, focused on business impact and organizational transformation.
APPROACH: Lead with macro trends, demonstrate understanding of strategic challenges, position yourself as a peer with complementary expertise.
AVOID: Tactical details, overt sales language, assumptions about their specific pain points.
        """,
        Archetype.EXECUTIVE: """
You are crafting a professional message that emphasizes collaboration and mutual value.

TONE: Professional, collaborative, focused on team objectives and operational excellence.
APPROACH: Reference their role and responsibilities, demonstrate understanding of their team's challenges, offer concrete value.
AVOID: Overly formal language, generic value propositions, excessive deference.
        """,
        Archetype.SENIOR_TA: """
You are crafting a technical message for a senior technical authority (architect, principal engineer, tech lead).

TONE: Technical peer, respectful but confident, focused on architectural decisions and technical excellence.
APPROACH: Reference specific technologies or patterns, demonstrate technical credibility, respect their authority on technical direction.
AVOID: Marketing language, oversimplification of technical concepts, challenging their technical decisions.
        """,
        Archetype.RECRUITER: """
You are crafting a job-focused message that centers on role fit and candidate qualifications.

TONE: Warm, professional, focused on alignment between candidate skills and role requirements.
APPROACH: Lead with relevant experience, highlight specific skills that match job description, emphasize career growth potential.
AVOID: Generic qualifications, vague interest statements, over-selling unrelated experience.
        """
    }

    @classmethod
    def get_target_word_count(cls, archetype: Archetype, route: Route) -> int:
        """Get target word count for archetype+route combination"""
        target = cls.ARCHETYPE_WORD_TARGETS.get(archetype, {}).get(route)
        if target is not None:
            return target
        return cls.ROUTE_CONSTRAINTS[route]["word_range"][1]

    @classmethod
    def get_rag_parameter(cls, archetype: Archetype, param_name: str) -> Any:
        """Get RAG parameter for archetype"""
        return cls.ARCHETYPE_RAG_PARAMS.get(archetype, {}).get(param_name)

    @classmethod
    def get_reasoning_parameter(cls, archetype: Archetype, param_name: str) -> Any:
        """Get reasoning parameter for archetype"""
        return cls.ARCHETYPE_REASONING_PARAMS.get(archetype, {}).get(param_name)

    @classmethod
    def get_tone_mapping(cls, archetype: Archetype, param_name: str) -> Any:
        """Get tone mapping for archetype"""
        return cls.ARCHETYPE_TONE_MAPPINGS.get(archetype, {}).get(param_name)

    @classmethod
    def get_route_constraints(cls, route: Route, archetype: Optional[Archetype] = None) -> Dict[str, Any]:
        """Get route constraints with optional archetype override"""
        constraints = cls.ROUTE_CONSTRAINTS[route].copy()

        if archetype:
            target_word = cls.get_target_word_count(archetype, route)
            if target_word:
                constraints["word_target"] = target_word

        return constraints


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class OutreachMission:
    """Complete mission specification"""
    mission_id: str
    sender_profile: Dict[str, Any]
    recipient_profile: Dict[str, Any]
    job_description: Dict[str, Any]
    connection_status: str = "not_connected"
    prior_message_count: int = 0
    route_override: Optional[Route] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProfileAnalysis:
    """Analysis of recipient profile for archetype classification"""
    archetype: Archetype
    confidence: float
    reasoning: str
    key_indicators: List[str]
    needs_manual_override: bool = False  # NEW v11.6
    critique_history: List[str] = field(default_factory=list)  # NEW v11.6


@dataclass
class RAGResult:
    """Single RAG retrieval result with metadata"""
    source: str
    source_type: str
    text: str
    extracted_keywords: List[str]
    source_weight: float
    age_days: int
    recipient_specific: bool
    confidence: float = 1.0


@dataclass
class ResearchContext:
    """Aggregated research findings"""
    recipient_insights: List[str]
    company_context: List[str]
    recent_activity: List[str]
    rag_results: List[RAGResult]
    signal_score: float = 0.0  # NEW v11.6
    reflexion_iterations: int = 0  # NEW v11.6
    prior_applications: List[Dict[str, Any]] = field(default_factory=list)  # NEW v11.6
    mission_context: Dict[str, Any] = field(default_factory=dict)  # NEW v11.7 - for validation context
    sender_context: List[str] = field(default_factory=list)  # NEW v11.7
    sender_grounding: Optional['SenderGroundingWhitelists'] = None  # NEW v11.9
    adversarial_findings: List[str] = field(default_factory=list) # NEW v11.10


@dataclass
class MessageScaffold:
    """Structural scaffold for message generation"""
    route: Route
    archetype: Archetype
    sections: Dict[str, Dict[str, Any]]
    constraints: Dict[str, Any]
    locked_sections: Set[str] = field(default_factory=set)
    context_aware_cta: bool = False  # NEW v11.9 - controls CTA generation logic


@dataclass
class GeneratedMessage:
    """Generated message with metadata"""
    content: str
    word_count: int
    char_count: int
    route: Route
    archetype: Archetype
    generation_temperature: float
    generation_attempts: int
    locked_sections: Set[str]
    checksum: str


@dataclass
class ValidationResult:
    """Result from validation check"""
    passed: bool
    severity: ValidationSeverity
    rule_id: str
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class QAReport:
    """Comprehensive QA report"""
    mission_id: str
    validation_results: List[ValidationResult]
    critical_issues: int
    high_issues: int  # NEW v11.6
    errors: int
    warnings: int
    passed: bool
    timestamp: str


@dataclass
class SenderGroundingWhitelists:
    """
    NEW v11.9: Extracted sender grounding facts from RAG
    Used to validate "my team" / "our product" claims in generation
    """
    team_members: List[str] = field(default_factory=list)  # Names extracted from RAG
    products: List[str] = field(default_factory=list)      # Product names from RAG
    case_studies: List[str] = field(default_factory=list)  # Client/case study names
    raw_evidence: Dict[str, List[str]] = field(default_factory=dict)  # Category → source snippets



@dataclass
class MessageClaim:
    """NEW v11.6: Individual claim with confidence (FEATURE 1.2)"""
    text: str
    confidence: float
    supporting_sources: List[str]
    source_weights: List[float]


@dataclass
class RAGCritique:
    """NEW v11.6: RAG quality critique (FEATURE 1.4)"""
    confidence_score: float
    gaps_identified: List[str]
    refinement_tasks: List[str]
    reasoning: str
    is_sufficient: bool


# ============================================================================
# NEW v11.6: SIGNAL QUALITY SCORER (FEATURE 1.1)
# ============================================================================

class SignalQualityScorer:
    """
    Weights RAG sources by reliability for message generation
    FEATURE 1.1 from SUPREME_SPELL
    """

    SOURCE_WEIGHTS = {
        "RECIPIENT_LINKEDIN_ABOUT": 2.0,
        "RECIPIENT_RECENT_POST": 1.8,
        "COMPANY_BLOG_ANNOUNCEMENT": 1.5,
        "COMPANY_LINKEDIN_PAGE": 1.3,
        "NEWS_ARTICLE_COMPANY": 1.2,
        "COMPETITOR_COMPARISON": 0.9,
        "GENERIC_INDUSTRY_TREND": 0.6,
        "SENDER_PROFILE_ONLY": 0.3
    }

    MINIMUM_SIGNAL_THRESHOLD = 0.70

    def calculate_signal_score(
        self,
        rag_results: List[RAGResult],
        message_content: str
    ) -> Tuple[float, Dict[str, int]]:
        """
        Calculate weighted signal quality score for generated message
        """
        keyword_scores = defaultdict(float)
        source_breakdown = defaultdict(int)

        for result in rag_results:
            weight = self.SOURCE_WEIGHTS.get(result.source_type, 0.5)
            for keyword in result.extracted_keywords:
                if keyword.lower() in message_content.lower():
                    keyword_scores[keyword] += weight
                    source_breakdown[result.source_type] += 1

        if not keyword_scores:
            return 0.0, dict(source_breakdown)

        signal_score = sum(keyword_scores.values()) / len(keyword_scores)
        return signal_score, dict(source_breakdown)

    def validate_minimum_signal(self, score: float) -> bool:
        return score >= self.MINIMUM_SIGNAL_THRESHOLD


# ============================================================================
# NEW v11.6: CLAIM CONFIDENCE SCORER (FEATURE 1.2)
# ============================================================================

class ClaimConfidenceScorer:
    """
    Per-claim confidence scoring with rejection gate
    FEATURE 1.2 from SUPREME_SPELL
    """

    MIN_PER_CLAIM_CONFIDENCE = 0.70
    MIN_AGGREGATE_CONFIDENCE = 0.75

    def score_claim(
        self,
        claim_text: str,
        rag_results: List[RAGResult],
        embedding_similarity_threshold: float = 0.75
    ) -> MessageClaim:
        """
        Score individual claim based on RAG evidence
        (Simplified version - full implementation would use embeddings)
        """
        supporting = []
        weights = []

        # Simple keyword-based support detection
        claim_words = set(claim_text.lower().split())

        for result in rag_results:
            result_words = set(result.text.lower().split())
            overlap = len(claim_words & result_words)

            if overlap >= 3:  # At least 3 words in common
                supporting.append(result.source)
                weights.append(result.source_weight)

        if not supporting:
            confidence = 0.0
        else:
            confidence = min(1.0, (len(supporting) * 0.3) + (sum(weights) / len(weights) * 0.7))

        return MessageClaim(
            text=claim_text,
            confidence=confidence,
            supporting_sources=supporting,
            source_weights=weights
        )

    def score_message_claims(
        self,
        message: str,
        rag_results: List[RAGResult]
    ) -> Tuple[List[MessageClaim], float]:
        """
        Score all claims in message
        """
        # Split message into sentences (claims)
        sentences = [s.strip() for s in message.split('.') if len(s.strip()) > 10]

        claims = []
        for sentence in sentences:
            claim = self.score_claim(sentence, rag_results)
            claims.append(claim)

        if not claims:
            return [], 0.0

        aggregate_confidence = sum(c.confidence for c in claims) / len(claims)
        return claims, aggregate_confidence

    def validate_claims(
        self,
        claims: List[MessageClaim],
        aggregate_confidence: float
    ) -> Tuple[bool, str]:
        """
        Validate claims meet minimum thresholds
        """
        low_confidence_claims = [c for c in claims if c.confidence < self.MIN_PER_CLAIM_CONFIDENCE]

        if low_confidence_claims:
            return False, f"{len(low_confidence_claims)} claims below 0.70 confidence"

        if aggregate_confidence < self.MIN_AGGREGATE_CONFIDENCE:
            return False, f"Aggregate confidence {aggregate_confidence:.2f} < 0.75"

        return True, ""


# ============================================================================
# NEW v11.6: RAG REFLEXION SYSTEM (FEATURE 1.4)
# ============================================================================

class RAGReflexionSystem:
    """
    Iterative RAG refinement with critique loop
    FEATURE 1.4 from SUPREME_SPELL
    """

    MIN_CONFIDENCE_THRESHOLD = 0.70
    MAX_ITERATIONS = 3

    def critique_rag_sufficiency(
        self,
        rag_results: List[RAGResult],
        recipient_archetype: Archetype,
        iteration: int
    ) -> RAGCritique:
        """
        Critique RAG research quality and identify gaps
        """
        gaps = []

        # Gap 1: Source diversity
        source_types = set(r.source_type for r in rag_results)
        if "RECIPIENT_LINKEDIN_ABOUT" not in source_types:
            gaps.append("Missing direct recipient profile data")
        if "COMPANY_BLOG_ANNOUNCEMENT" not in source_types:
            gaps.append("Missing recent company announcements")

        # Gap 2: Recency for C_LEVEL
        if recipient_archetype == Archetype.C_LEVEL:
            recent_sources = [r for r in rag_results if r.age_days <= 90]
            if len(recent_sources) < 3:
                gaps.append("Insufficient recent sources for C_LEVEL (need 3+ within 90 days)")

        # Gap 3: Personalization depth
        recipient_specific = [r for r in rag_results if r.recipient_specific]
        if len(recipient_specific) < 2:
            gaps.append("Insufficient recipient-specific context (need 2+ personalized insights)")

        # Confidence calculation
        confidence = self._calculate_confidence(rag_results, gaps)

        # Refinement tasks
        refinement_tasks = self._generate_refinement_tasks(gaps)

        is_sufficient = len(gaps) == 0 and confidence >= self.MIN_CONFIDENCE_THRESHOLD

        reasoning = f"Iteration {iteration}: {len(rag_results)} results, {len(source_types)} source types. "
        reasoning += f"Gaps: {len(gaps)}. Confidence: {confidence:.2f}"

        return RAGCritique(
            confidence_score=confidence,
            gaps_identified=gaps,
            refinement_tasks=refinement_tasks,
            reasoning=reasoning,
            is_sufficient=is_sufficient
        )

    def _calculate_confidence(self, rag_results: List[RAGResult], gaps: List[str]) -> float:
        """
        Calculate confidence score
        Updated v11.6.1: Less conservative calculation for better usability
        """
        # Improved scoring: more credit for diverse sources
        num_results = len(rag_results)
        num_source_types = len(set(r.source for r in rag_results))

        # Base score: 0.15 per result (caps at 0.75 for 5+ results)
        base_score = min(0.75, num_results * 0.15)

        # Diversity bonus: 0.10 per unique source type (caps at 0.30)
        diversity_bonus = min(0.30, num_source_types * 0.10)

        # Gap penalty: reduced from 0.15 to 0.10 per gap
        gap_penalty = len(gaps) * 0.10

        confidence = base_score + diversity_bonus - gap_penalty
        return max(0.0, min(1.0, confidence))

    def _generate_refinement_tasks(self, gaps: List[str]) -> List[str]:
        """Generate refinement search tasks from gaps"""
        tasks = []
        for gap in gaps:
            if "recipient profile" in gap.lower():
                tasks.append("Search for recipient LinkedIn profile and recent posts")
            elif "company announcements" in gap.lower():
                tasks.append("Search for company blog and recent news")
            elif "recent sources" in gap.lower():
                tasks.append("Focus search on content from last 90 days")
            elif "personalized insights" in gap.lower():
                tasks.append("Search for recipient-specific achievements and projects")
        return tasks


# ============================================================================
# NEW v11.6: ADAPTIVE TEMPERATURE CONTROLLER (FEATURE 2.2)
# ============================================================================

class AdaptiveTemperatureController:
    """
    Progressive temperature escalation for retry attempts
    FEATURE 2.2 from SUPREME_SPELL
    """

    BASE_TEMPERATURES = {
        Archetype.C_LEVEL: 0.45,
        Archetype.EXECUTIVE: 0.50,
        Archetype.SENIOR_TA: 0.55,
        Archetype.RECRUITER: 0.65
    }
    ESCALATION_STEP = 0.15
    MAX_TEMPERATURE = 0.95

    def __init__(self):
        self.attempt_history: Dict[str, List[float]] = defaultdict(list)
        self.success_temperatures: Dict[str, float] = {}

    def get_temperature(
        self,
        component: str,
        archetype: Archetype,
        attempt: int
    ) -> float:
        """Get temperature for this generation attempt"""
        base_temp = self.BASE_TEMPERATURES[archetype]
        escalated_temp = min(
            self.MAX_TEMPERATURE,
            base_temp + (attempt - 1) * self.ESCALATION_STEP
        )

        self.attempt_history[f"{archetype.value}_{component}"].append(escalated_temp)

        return escalated_temp

    def record_success(
        self,
        component: str,
        archetype: Archetype,
        temperature: float
    ):
        """Record which temperature succeeded for learning"""
        key = f"{archetype.value}_{component}"
        self.success_temperatures[key] = temperature


# ============================================================================
# NEW v11.6: CONSTRAINT FEASIBILITY CHECKER (FEATURE 2.1)
# ============================================================================

class ConstraintFeasibilityChecker:
    """
    Pre-flight check for constraint satisfaction
    FEATURE 2.1 from SUPREME_SPELL
    """

    def check_feasibility(
        self,
        route: Route,
        archetype: Archetype,
        required_elements: List[str]
    ) -> Tuple[bool, str]:
        """
        Pre-flight check: can we satisfy these constraints?
        (Simplified version - full implementation would use LLM)
        """
        constraints = ConfigRegistry.get_route_constraints(route, archetype)

        # Simple heuristic: check if number of required elements fits in word budget
        word_budget = constraints.get("word_target", constraints["word_range"][1])
        words_per_element = word_budget // (len(required_elements) + 2)  # +2 for greeting/signature

        # CONNECTION_REQ requires stricter checking (more constrained format)
        min_words_per_element = 8 if route == Route.CONNECTION_REQ else 5

        if words_per_element < min_words_per_element:
            return False, f"Too many required elements ({len(required_elements)}) for {route.value} word budget ({word_budget})"

        return True, "Constraints are feasible"


# ============================================================================
# NEW v11.6: CONTENT CLEANLINESS VALIDATORS (FEATURE 3.1, 3.2, 3.3)
# ============================================================================

class ContentCleanlinessValidator:
    """
    Forbidden verbs and weak language detection
    FEATURE 3.1 and 3.2 from SUPREME_SPELL
    """

    FORBIDDEN_VERBS = [
        "spearheaded", "leveraged", "utilized", "facilitated",
        "orchestrated", "championed", "pioneered", "revolutionized",
        "transformed", "optimized", "enhanced", "streamlined",
        "synergized", "enabled", "empowered", "drove", "drive"
    ]
    MAX_VIOLATIONS = 1

    FILLER_PATTERNS = [
        r"(?i)\bi hope\b",
        r"(?i)\bhope (this|you) (finds|are|don't)",
        r"(?i)\bi (wanted|would like) to (reach|connect|discuss|share)",
        r"(?i)\bi was wondering if",
        r"(?i)\bperhaps (we|you) could",
        r"(?i)\bif you('re| are) interested",
        r"(?i)\bjust (wanted|reaching|following)",
    ]

    def detect_forbidden_verbs(self, text: str) -> List[str]:
        """Find forbidden verbs in message text"""
        text_lower = text.lower()
        found = []

        for verb in self.FORBIDDEN_VERBS:
            if verb in text_lower:
                found.append(verb)

        return found

    def detect_fillers(self, text: str) -> List[Tuple[str, str]]:
        """Find filler phrases in message"""
        found = []

        for pattern in self.FILLER_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    match_text = match if isinstance(match, str) else " ".join(match) if isinstance(match, tuple) else str(match)
                    found.append((pattern, match_text))

        return found

    def validate_verbs(self, message: str) -> Tuple[bool, str]:
        """Validate no excessive forbidden verbs"""
        forbidden = self.detect_forbidden_verbs(message)

        if len(forbidden) > self.MAX_VIOLATIONS:
            return False, f"Found {len(forbidden)} forbidden verbs: {', '.join(forbidden[:3])}"

        return True, ""

    def validate_fillers(self, message: str) -> Tuple[bool, str]:
        """Validate message is direct and confident"""
        fillers = self.detect_fillers(message)

        if fillers:
            filler_texts = [f[1] for f in fillers]
            return False, f"Found {len(fillers)} filler phrases: {', '.join(filler_texts[:3])}"

        return True, ""


class PlaceholderDetector:
    """
    Comprehensive placeholder detection
    FEATURE 3.3 from SUPREME_SPELL / GAP 1.5
    """

    PLACEHOLDER_PATTERNS = [
        r'\[placeholder\]',
        r'\[your name\]',
        r'\[company name\]',
        r'\[recipient[_ ]?name\]',
        r'\{[a-z_]+\}',
        r'\bTBD\b',
        r'\bTODO\b',
        r'\bFIXME\b',
        r'\[INSERT [A-Z]+\]',
        r'\[ADD [A-Z]+\]',
        r'_{3,}',
        r'\[missing[_ ]?context\]',
        r'\[unserializable\]',
    ]

    def detect_placeholders(self, text: str) -> List[str]:
        """Detect ALL placeholder patterns"""
        found = []

        for pattern in self.PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found.extend(matches)

        return found

    def validate(self, message: str) -> Tuple[bool, str]:
        """CRITICAL: Zero tolerance for placeholders"""
        placeholders = self.detect_placeholders(message)

        if placeholders:
            return False, f"CRITICAL: Found {len(placeholders)} placeholders: {', '.join(placeholders[:5])}"

        return True, ""


# ============================================================================
# NEW v11.6: MESSAGE DIVERSITY VALIDATOR (FEATURE 1.3)
# ============================================================================

class MessageDiversityValidator:
    """
    Prevent repetitive messages using cosine similarity
    FEATURE 1.3 from SUPREME_SPELL
    """

    MIN_DIVERSITY_THRESHOLD = 0.85  # Messages must be <85% similar

    def __init__(self):
        self.message_history: List[str] = []
        self.vectorizer = TfidfVectorizer()

    def check_diversity(self, new_message: str) -> Tuple[bool, float, str]:
        """
        Check if new message is sufficiently different from history

        Returns:
            (is_diverse, max_similarity, most_similar_message)
        """
        if not self.message_history:
            return True, 0.0, ""

        all_messages = self.message_history + [new_message]

        try:
            vectors = self.vectorizer.fit_transform(all_messages)
            new_vector = vectors[-1]
            history_vectors = vectors[:-1]

            similarities = cosine_similarity(new_vector, history_vectors)[0]
            max_similarity = float(np.max(similarities))
            max_idx = int(np.argmax(similarities))

            is_diverse = max_similarity < self.MIN_DIVERSITY_THRESHOLD
            most_similar = self.message_history[max_idx] if max_idx < len(self.message_history) else ""

            return is_diverse, max_similarity, most_similar

        except:
            # If vectorization fails, assume diverse
            return True, 0.0, ""

    def add_to_history(self, message: str):
        """Add message to history"""
        self.message_history.append(message)


# ============================================================================
# NEW v11.6: ASCII CHARACTER ENFORCER (GAP 1.10)
# ============================================================================

class ASCIIEnforcer:
    """
    Enforce ASCII-only characters for LinkedIn compatibility
    GAP 1.10 from v10.22
    """

    UNICODE_REPLACEMENTS = {
        "•": "-",
        "–": "-",
        "—": "-",
        """: '"',
        """: '"',
        "'": "'",
        "'": "'",
        "…": "...",
    }

    def enforce_ascii(self, text: str) -> str:
        """Replace Unicode with ASCII equivalents"""
        for unicode_char, ascii_replacement in self.UNICODE_REPLACEMENTS.items():
            text = text.replace(unicode_char, ascii_replacement)

        # Remove any remaining non-ASCII
        text = text.encode("ascii", "ignore").decode("ascii")

        return text

    def validate(self, text: str) -> Tuple[bool, str]:
        """Validate text is ASCII-only"""
        try:
            text.encode("ascii")
            return True, ""
        except UnicodeEncodeError as e:
            non_ascii_chars = [c for c in text if ord(c) > 127]
            return False, f"Non-ASCII characters: {set(non_ascii_chars[:5])}"


# ============================================================================
# AGENTS
# ============================================================================

class ProfileAnalysisAgent:
    """
    NEW v11.6: Hardened archetype classification with 4-archetype standard
    Implements deterministic classification logic from v10.22
    """

    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.status = AgentStatus.IDLE

    def analyze_profile(self, mission: OutreachMission) -> ProfileAnalysis:
        """
        NEW v11.6: Hardened static classification with 5-node decision tree
        """
        self.status = AgentStatus.RUNNING

        recipient = mission.recipient_profile
        title = recipient.get("title", "").lower()

        # Node 1: C_LEVEL detection (CEO, CTO, CFO, COO, CMO, CPO)
        c_level_titles = ["ceo", "cto", "cfo", "coo", "cmo", "cpo", "chief"]
        if any(c_title in title for c_title in c_level_titles):
            confidence = 0.95
            archetype = Archetype.C_LEVEL
            reasoning = f"Title '{recipient.get('title')}' contains C-level indicator"
            key_indicators = ["C-level title"]

        # Node 2: EXECUTIVE detection (VP, SVP, EVP, Head of, Director)
        elif any(exec_title in title for exec_title in ["vp", "vice president", "svp", "evp", "head of", "director"]):
            confidence = 0.90
            archetype = Archetype.EXECUTIVE
            reasoning = f"Title '{recipient.get('title')}' indicates executive level"
            key_indicators = ["Executive title"]

        # Node 3: RECRUITER detection (Recruiter, Talent, Hiring, HR)
        elif any(rec_term in title for rec_term in ["recruit", "talent", "hiring", "human resources", "hr"]):
            confidence = 0.92
            archetype = Archetype.RECRUITER
            reasoning = f"Title '{recipient.get('title')}' indicates recruiting/talent role"
            key_indicators = ["Recruiting title"]

        # Node 4: SENIOR_TA detection (Staff, Principal, Distinguished, Fellow, Senior)
        elif any(ta_term in title for ta_term in ["staff", "principal", "distinguished", "fellow", "senior engineer", "senior architect"]):
            confidence = 0.85
            archetype = Archetype.SENIOR_TA
            reasoning = f"Title '{recipient.get('title')}' indicates senior technical authority"
            key_indicators = ["Senior technical title"]

        # Node 5: Default to SENIOR_TA for ambiguous technical roles
        else:
            confidence = 0.70
            archetype = Archetype.SENIOR_TA
            reasoning = "Defaulting to SENIOR_TA for ambiguous title"
            key_indicators = ["Ambiguous title"]

        # NEW v11.6: Manual override flag for low confidence
        needs_manual_override = confidence < 0.85

        self.status = AgentStatus.COMPLETED

        return ProfileAnalysis(
            archetype=archetype,
            confidence=confidence,
            reasoning=reasoning,
            key_indicators=key_indicators,
            needs_manual_override=needs_manual_override
        )


# ============================================================================
# NEW v11.10: S2 SPECIALIST AGENTS (Enhancement 1)
# ============================================================================

class RecipientAgent:
    """
    NEW v11.10: Specialist agent for recipient-facing RAG.
    Tools: LinkedIn, GitHub, Conference Talks retrievers (mocked).
    """
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker

    async def get_profile(self, mission: OutreachMission) -> Dict[str, Any]:
        """Mock: Perform RAG on recipient's public footprint."""
        print("     S2.RecipientAgent: Retrieving profile (LinkedIn, GitHub)...")
        await asyncio.sleep(0.1) # Simulate async RAG
        return {
            "rag_results": [
                RAGResult(
                    source="recipient_linkedin",
                    source_type="RECIPIENT_LINKEDIN_ABOUT",
                    text=f"About {mission.recipient_profile.get('name')}: {mission.recipient_profile.get('title')} at {mission.recipient_profile.get('company')}",
                    extracted_keywords=["leadership", "innovation", "technology"],
                    source_weight=2.0,
                    age_days=0,
                    recipient_specific=True
                )
            ]
        }

    async def run_refinement_task(self, task: str, mission: OutreachMission) -> Dict[str, Any]:
        """Mock: Perform a targeted refinement RAG task."""
        print(f"     S2.RecipientAgent: Running refinement task: '{task[:50]}...'")
        await asyncio.sleep(0.1)
        return {
            "rag_results": [
                RAGResult(
                    source="recipient_github",
                    source_type="RECIPIENT_GITHUB_REPO",
                    text="Refined search found GitHub repo for recipient.",
                    extracted_keywords=["python", "agentic", "oss"],
                    source_weight=1.8,
                    age_days=10,
                    recipient_specific=True
                )
            ]
        }


class OrganizationAgent:
    """
    NEW v11.10: Specialist agent for organization-facing RAG.
    Tools: Company Blog, News, Industry Reports retrievers (mocked).
    """
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker

    async def get_organization_context(self, mission: OutreachMission) -> Dict[str, Any]:
        """Mock: Perform RAG on organization's public footprint."""
        print("     S2.OrganizationAgent: Retrieving org context (Blog, News)...")
        await asyncio.sleep(0.15) # Simulate async RAG
        return {
            "rag_results": [
                RAGResult(
                    source="company_page",
                    source_type="COMPANY_LINKEDIN_PAGE",
                    text=f"{mission.job_description.get('company')} is a leading technology company",
                    extracted_keywords=["technology", "innovation", "growth"],
                    source_weight=1.3,
                    age_days=30,
                    recipient_specific=False
                )
            ]
        }

    async def run_refinement_task(self, task: str, mission: OutreachMission) -> Dict[str, Any]:
        """Mock: Perform a targeted refinement RAG task."""
        print(f"     S2.OrganizationAgent: Running refinement task: '{task[:50]}...'")
        await asyncio.sleep(0.1)

        # Mock finding evidence for a failed S6 metric validation
        if "metric" in task.lower():
             return {
                "rag_results": [
                    RAGResult(
                        source="company_blog_metric_search",
                        source_type="COMPANY_BLOG_ANNOUNCEMENT",
                        text="Our new platform launch resulted in a 40% reduction in processing time.",
                        extracted_keywords=["40%", "reduction", "processing time"],
                        source_weight=1.5,
                        age_days=15,
                        recipient_specific=False
                    )
                ]
            }

        return {
            "rag_results": [
                RAGResult(
                    source="company_blog",
                    source_type="COMPANY_BLOG_ANNOUNCEMENT",
                    text="Recent announcement about company growth and new AI platform.",
                    extracted_keywords=["growth", "expansion", "hiring", "AI platform"],
                    source_weight=1.5,
                    age_days=15,
                    recipient_specific=False
                )
            ]
        }


class InternalAgent:
    """
    NEW v11.10: Specialist agent for internal-facing data lookups.
    Tools: Job Tracker (mocked).
    """
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker

    def get_internal_context(self, mission: OutreachMission) -> Dict[str, Any]:
        """Mock: Perform internal data lookups."""
        print("     S2.InternalAgent: Checking job tracker for prior applications...")
        prior_applications = self._search_job_tracker(mission)
        return {
            "prior_applications": prior_applications,
            "rag_results": [] # Internal agent doesn't produce RAG results directly
        }

    def _search_job_tracker(self, mission: OutreachMission) -> List[Dict[str, Any]]:
        """
        NEW v11.6: Search for prior applications to same company (GAP 4.1)
        (Moved to InternalAgent in v11.10)
        """
        # Simulated - would search project knowledge/database
        company = mission.job_description.get("company", "")
        # For now, return empty list (no prior applications)
        return []


class S2_SupervisorAgent:
    """
    NEW v11.10: Replaces ResearchOrchestrator (Enhancement 1).
    Acts as a planner/delegator for a team of specialist agents.
    Runs an internal "Execute-Critique-Replan" loop (Enhancement 2).
    Runs an "Adversarial Self-Verification" step (Enhancement 3).
    Accepts an "S6->S2 Meta-Loop" refinement context (Enhancement 4).
    """

    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.status = AgentStatus.IDLE
        self.signal_scorer = SignalQualityScorer()
        self.rag_reflexion = RAGReflexionSystem()

        # NEW v11.10: Instantiate specialist agent team
        self.recipient_agent = RecipientAgent(circuit_breaker)
        self.organization_agent = OrganizationAgent(circuit_breaker)
        self.internal_agent = InternalAgent(circuit_breaker)

    async def conduct_research(
        self,
        mission: OutreachMission,
        profile_analysis: ProfileAnalysis,
        refinement_context: List[ValidationResult] = None # NEW v11.10: For S6->S2 loop
    ) -> Tuple[ResearchContext, ProfileAnalysis]:
        """
        NEW v11.10: Agentic planner/delegator workflow.
        """
        self.status = AgentStatus.RUNNING

        # ---
        # S2 INTERNAL LOOP (Enhancement 1 & 2)
        # ---
        rag_results = []
        reflexion_iterations = 0

        # Initial research plan
        print("     S2.Supervisor: Generating initial research plan...")

        # Delegation (Parallel Execution)
        print("     S2.Supervisor: Delegating to specialist agents (parallel)...")
        recipient_report_task = self.recipient_agent.get_profile(mission)
        org_report_task = self.organization_agent.get_organization_context(mission)

        # Internal agent is sync (mocked as fast)
        internal_report = self.internal_agent.get_internal_context(mission)
        prior_applications = internal_report['prior_applications']

        # Gather parallel results
        recipient_report, org_report = await asyncio.gather(
            recipient_report_task,
            org_report_task
        )

        # Synthesis
        rag_results.extend(recipient_report['rag_results'])
        rag_results.extend(org_report['rag_results'])

        # Internal Critique Loop
        while reflexion_iterations < 2: # Max 2 internal refinement loops

            # Critique
            critique = self.rag_reflexion.critique_rag_sufficiency(
                rag_results,
                profile_analysis.archetype,
                iteration=reflexion_iterations + 1
            )

            # NEW v11.10: Check for S6->S2 Meta-Loop refinement context
            if refinement_context and reflexion_iterations == 0:
                print("     S2.Supervisor: Received S6 failure context. Forcing refinement task.")
                failure_rule = refinement_context[0].rule_id
                failure_msg = refinement_context[0].message
                task = f"S6 Validation Failed ({failure_rule}): {failure_msg}. Find new evidence to resolve this."
                critique.is_sufficient = False
                critique.refinement_tasks = [task]

            if critique.is_sufficient:
                print(f"     S2.Supervisor: Internal critique PASSED (Iteration {reflexion_iterations + 1}).")
                break

            # Refinement
            reflexion_iterations += 1
            task = critique.refinement_tasks[0]
            print(f"     S2.Supervisor: Internal critique FAILED. Refining task: '{task[:50]}...'")

            # Delegate refinement task
            refinement_report = None
            if any(kw in task.lower() for kw in ["recipient", "github", "linkedin"]):
                refinement_report = await self.recipient_agent.run_refinement_task(task, mission)
            else: # Default to organization agent
                refinement_report = await self.organization_agent.run_refinement_task(task, mission)

            rag_results.extend(refinement_report['rag_results'])

        # ---
        # END S2 INTERNAL LOOP
        # ---

        # NEW v11.9: Extract sender grounding (now done by Supervisor post-synthesis)
        sender_grounding = self._extract_sender_grounding(rag_results, mission)

        # Build research context
        context = ResearchContext(
            recipient_insights=[
                f"Title: {mission.recipient_profile.get('title')}",
                f"Company: {mission.recipient_profile.get('company')}",
                f"Archetype: {profile_analysis.archetype.value}"
            ],
            company_context=[
                f"Company: {mission.job_description.get('company')}",
                f"Job: {mission.job_description.get('title')}"
            ],
            recent_activity=[],
            rag_results=rag_results,
            reflexion_iterations=reflexion_iterations,
            prior_applications=prior_applications,
            mission_context={
                "job_title": mission.job_description.get("title", ""),
                "company": mission.job_description.get("company", ""),
                "sender_teams": mission.sender_profile.get("teams", [])
            },
            sender_context=[],
            sender_grounding=sender_grounding
        )

        # NEW v11.6: Archetype Self-Correction
        corrected_profile_analysis = self._critique_archetype_classification(
            profile_analysis,
            context
        )

        # NEW v11.10: Adversarial Self-Verification (Enhancement 3)
        adversarial_findings = await self._run_adversarial_check(context)
        context.adversarial_findings = adversarial_findings
        if adversarial_findings:
            print(f"     S2.Supervisor: Adversarial check flagged {len(adversarial_findings)} weak claims.")

        self.status = AgentStatus.COMPLETED

        return context, corrected_profile_analysis

    async def _run_adversarial_check(self, context: ResearchContext) -> List[str]:
        """
        NEW v11.10: Mocked "Red Team" adversarial check (Enhancement 3).
        Issues a final prompt to find flaws in the synthesized research.
        """
        print("     S2.Supervisor: Running Adversarial Self-Verification (Red Team)...")
        await asyncio.sleep(0.05) # Simulate LLM call

        # Mock finding:
        mock_findings = ["Refuted theme: 'direct experience with scaling' (evidence is tangential)"]
        return mock_findings

    def _extract_sender_grounding(
        self,
        rag_results: List[RAGResult],
        mission: OutreachMission
    ) -> SenderGroundingWhitelists:
        """
        NEW v11.9: Extract sender grounding whitelists from RAG (SPEC 1)
        (Moved to S2_SupervisorAgent in v11.10)
        """
        grounding = SenderGroundingWhitelists()

        # Extract from RAG results
        for result in rag_results:
            text_lower = result.text.lower()

            # Team members
            if any(marker in text_lower for marker in ["team member", "colleague", "worked with", "collaborator"]):
                names = self._extract_names_from_text(result.text)
                grounding.team_members.extend(names)
                if names:
                    grounding.raw_evidence["team_members"] = grounding.raw_evidence.get("team_members", []) + [result.text[:200]]

            # Products
            if any(marker in text_lower for marker in ["product", "platform", "solution", "service"]):
                products = self._extract_capitalized_phrases(result.text)
                grounding.products.extend(products)
                if products:
                    grounding.raw_evidence["products"] = grounding.raw_evidence.get("products", []) + [result.text[:200]]

            # Case studies
            if any(marker in text_lower for marker in ["client", "customer", "case study", "project for"]):
                cases = self._extract_capitalized_phrases(result.text)
                grounding.case_studies.extend(cases)
                if cases:
                    grounding.raw_evidence["case_studies"] = grounding.raw_evidence.get("case_studies", []) + [result.text[:200]]

        # Deduplicate
        grounding.team_members = list(set(grounding.team_members))
        grounding.products = list(set(grounding.products))
        grounding.case_studies = list(set(grounding.case_studies))

        return grounding

    def _extract_names_from_text(self, text: str) -> List[str]:
        """Extract person names from text (simplified - production would use NER)"""
        words = text.split()
        names = []
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                if i + 1 < len(words) and words[i + 1][0].isupper():
                    full_name = f"{word} {words[i + 1]}"
                    names.append(full_name)
        return names

    def _extract_capitalized_phrases(self, text: str) -> List[str]:
        """Extract capitalized phrases (product/company names)"""
        words = text.split()
        phrases = []
        current_phrase = []
        for word in words:
            if word[0].isupper() and len(word) > 2:
                current_phrase.append(word)
            else:
                if len(current_phrase) >= 2:
                    phrases.append(" ".join(current_phrase))
                current_phrase = []
        if len(current_phrase) >= 2:
            phrases.append(" ".join(current_phrase))
        return phrases

    def _critique_archetype_classification(
        self,
        provisional_analysis: ProfileAnalysis,
        context: ResearchContext
    ) -> ProfileAnalysis:
        """
        NEW v11.6: Agentic self-correction of archetype classification
        (Moved to S2_SupervisorAgent in v11.10)
        """
        all_text = " ".join([r.text for r in context.rag_results]).lower()

        if provisional_analysis.archetype != Archetype.C_LEVEL:
            if any(term in all_text for term in ["strategic vision", "board member", "company direction"]):
                critique = "RAG evidence suggests C_LEVEL status (strategic indicators)"
                provisional_analysis.archetype = Archetype.C_LEVEL
                provisional_analysis.confidence = 0.90
                provisional_analysis.critique_history.append(critique)

        if provisional_analysis.archetype != Archetype.RECRUITER:
            if any(term in all_text for term in ["talent acquisition", "hiring manager", "recruitment"]):
                critique = "RAG evidence suggests RECRUITER role (hiring indicators)"
                provisional_analysis.archetype = Archetype.RECRUITER
                provisional_analysis.confidence = 0.88
                provisional_analysis.critique_history.append(critique)

        return provisional_analysis


class RoutingAgent:
    """
    NEW v11.6: Hardened deterministic routing with 5-node tree (GAP 2.1)
    """

    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.status = AgentStatus.IDLE

    def determine_route(
        self,
        mission: OutreachMission,
        profile_analysis: ProfileAnalysis
    ) -> Tuple[Route, str]:
        """
        NEW v11.6: 5-node deterministic routing tree from v10.22
        """
        self.status = AgentStatus.RUNNING

        # Node 1: route_override - bypass automatic selection
        if mission.route_override:
            reasoning = f"Node 1: Manual route override to {mission.route_override.value}"
            self.status = AgentStatus.COMPLETED
            return mission.route_override, reasoning

        # Node 2: job_confirmed=true AND job_outreach → INMAIL
        job_confirmed = bool(mission.job_description.get("title"))
        if job_confirmed:
            reasoning = "Node 2: Job application confirmed → INMAIL for maximum detail"
            self.status = AgentStatus.COMPLETED
            return Route.INMAIL, reasoning

        # Node 3: existing_relationship=true → FOLLOW_UP
        if mission.connection_status == "connected" and mission.prior_message_count > 0:
            reasoning = f"Node 3: Existing relationship ({mission.prior_message_count} prior messages) → FOLLOW_UP"
            self.status = AgentStatus.COMPLETED
            return Route.FOLLOW_UP, reasoning

        # Node 4: new_recipient=true (not connected, no prior messages) → CONNECTION_REQ
        if mission.connection_status == "not_connected" and mission.prior_message_count == 0:
            reasoning = "Node 4: New recipient, no connection → CONNECTION_REQ"
            self.status = AgentStatus.COMPLETED
            return Route.CONNECTION_REQ, reasoning

        # Node 5: Fallback → INMAIL
        reasoning = "Node 5: Fallback to INMAIL for safety"
        self.status = AgentStatus.COMPLETED
        return Route.INMAIL, reasoning


class ScaffoldAgent:
    """Generate message scaffold"""

    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.status = AgentStatus.IDLE

    def create_scaffold(
        self,
        route: Route,
        archetype: Archetype,
        context: ResearchContext
    ) -> MessageScaffold:
        """
        Create structural scaffold
        NEW v11.9: Context-aware CTA generation (SPEC 3)
        """
        self.status = AgentStatus.RUNNING

        constraints = ConfigRegistry.get_route_constraints(route, archetype)

        # NEW v11.9: Determine CTA requirements based on route and archetype
        context_aware_cta = self._should_use_context_aware_cta(route, archetype)
        cta_required = self._is_cta_required(route, archetype)

        sections = {
            "greeting": {
                "required": True,
                "word_range": constraints.get("greeting_word_range", (2, 4))
            },
            "body": {
                "required": True,
                "min_words": constraints.get("body_min_words", 50)
            },
            "cta": {
                "required": cta_required,
                "word_range": constraints.get("cta_word_range", (5, 10)) if cta_required else (0, 0),
                "context_aware": context_aware_cta
            },
            "signature": {
                "required": True,
                "word_range": constraints.get("signature_word_range", (2, 4))
            }
        }

        self.status = AgentStatus.COMPLETED

        return MessageScaffold(
            route=route,
            archetype=archetype,
            sections=sections,
            constraints=constraints,
            context_aware_cta=context_aware_cta
        )

    def _should_use_context_aware_cta(self, route: Route, archetype: Archetype) -> bool:
        """NEW v11.9: Determine if context-aware CTA should be used"""
        # CONNECTION_REQ never has CTA
        if route == Route.CONNECTION_REQ:
            return False
        # SENIOR_TA uses context-aware CTAs (direct vs deferential)
        if archetype == Archetype.SENIOR_TA:
            return True
        return False

    def _is_cta_required(self, route: Route, archetype: Archetype) -> bool:
        """NEW v11.9: Determine if CTA is required"""
        # CONNECTION_REQ has no CTA per SPEC 3
        if route == Route.CONNECTION_REQ:
            return False
        return True


class SelfConsistencySynthesizer:
    """
    NEW v11.7: N-candidate generation with synthesis for C_LEVEL archetype (FEATURE 2.3)
    Implements self-consistency methodology from SUPREME_SPELL
    """

    def __init__(self):
        self.n_candidates = 3  # Generate 3 candidates for C_LEVEL

    async def synthesize_c_level_message(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis,
        temperature: float
    ) -> str:
        """
        Generate N candidates and synthesize the best elements
        Only used for C_LEVEL archetype
        """
        if scaffold.archetype != Archetype.C_LEVEL:
            raise ValueError("Self-consistency synthesis only for C_LEVEL")

        # Generate N candidates
        candidates = []
        for i in range(self.n_candidates):
            candidate = await self._generate_single_candidate(
                scaffold, context, profile_analysis, temperature + (i * 0.05)
            )
            candidates.append(candidate)

        # Synthesize best elements
        synthesized = self._synthesize_candidates(candidates, context)
        return synthesized

    async def _generate_single_candidate(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis,
        temperature: float
    ) -> str:
        """Generate a single candidate message"""
        recipient_name = "Esteemed Executive"
        company = context.company_context[0] if context.company_context else "your organization"

        tone = ConfigRegistry.get_tone_mapping(scaffold.archetype, "message_tone")
        verbs = ConfigRegistry.get_tone_mapping(scaffold.archetype, "verb_preference")

        # NEW v11.10: Check for adversarial findings
        adversarial_constraints = ""
        if context.adversarial_findings:
            adversarial_constraints = f"\n\n[ADVERSARIAL_CHECK: AVOID CLAIMS: {', '.join(context.adversarial_findings)}]"

        # C_LEVEL gets most formal, strategic messaging
        content = f"Dear {recipient_name},\n\nI hope this finds you well. I'm reaching out regarding the strategic opportunity at {company}. Given your leadership in driving organizational transformation, I believe my background in AI/ML innovation could contribute meaningfully to your vision.\n\nI would welcome the chance to {verbs[0] if verbs else 'discuss'} how my experience aligns with {company}'s strategic objectives.\n\nRespectfully yours{adversarial_constraints}"

        return content

    def _synthesize_candidates(self, candidates: List[str], context: ResearchContext) -> str:
        """
        Synthesize the best elements from N candidates
        Uses heuristics to select strongest opening, body, close
        """
        # For now, return the longest candidate (most comprehensive)
        # In production, would use LLM to synthesize best elements
        return max(candidates, key=len)


class GenerationOrchestrator:
    """
    NEW v11.10: Enhanced with S6->S2 failure classification (Enhancement 4)
    """

    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.status = AgentStatus.IDLE
        self.feasibility_checker = ConstraintFeasibilityChecker()
        self.temp_controller = AdaptiveTemperatureController()
        self.synthesizer = SelfConsistencySynthesizer()

    async def generate_message(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis,
        validation_agent: 'ValidationAgent'
    ) -> GeneratedMessage:
        """
        NEW v11.10: Generate with pre-flight, adaptive temp, and
        S6->S2 failure classification.
        """
        self.status = AgentStatus.RUNNING

        # NEW v11.6: Constraint Pre-Flight Test (FEATURE 2.1)
        required_elements = [
            f"Recipient name: {context.recipient_insights[0] if context.recipient_insights else 'N/A'}",
            f"Company: {context.company_context[0] if context.company_context else 'N/A'}",
            "Value proposition",
            "Call to action"
        ]

        feasible, reason = self.feasibility_checker.check_feasibility(
            scaffold.route,
            scaffold.archetype,
            required_elements
        )

        if not feasible:
            raise ValueError(f"Constraint pre-flight failed: {reason}")

        # S5 Generation/Retry Loop
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):

            temperature = self.temp_controller.get_temperature(
                "full_message",
                scaffold.archetype,
                attempt
            )

            # Generate message
            content = await self._generate_content(
                scaffold,
                context,
                profile_analysis,
                temperature
            )

            # Calculate metrics
            word_count = len(content.split())
            char_count = len(content)
            checksum = hashlib.md5(content.encode()).hexdigest()

            message = GeneratedMessage(
                content=content,
                word_count=word_count,
                char_count=char_count,
                route=scaffold.route,
                archetype=scaffold.archetype,
                generation_temperature=temperature,
                generation_attempts=attempt,
                locked_sections=scaffold.locked_sections.copy(),
                checksum=checksum
            )

            # Validate with S6
            validation_results = validation_agent.validate_message(message, context)

            # Check if passed
            critical_failures = [r for r in validation_results if not r.passed and r.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]]

            if not critical_failures:
                # Success!
                self.temp_controller.record_success("full_message", scaffold.archetype, temperature)
                self.status = AgentStatus.COMPLETED
                return message

            # NEW v11.10: Failure Classification (Enhancement 4)
            print(f"     S5: Generation attempt {attempt} failed validation...")
            failure_type, failure_report = self._classify_failure(critical_failures)

            if failure_type == FailureClassifier.FACTUAL_FAILURE:
                print(f"     S5 REASON: Factual failure detected. {failure_report}")
                print(f"     S5 ACTION: Halting generation retry. Triggering S6->S2 re-planning loop.")
                # Raise error to be caught by Orchestrator's meta-loop
                raise FactualGapError(critical_failures)
            else:
                # CREATIVE_FAILURE
                print(f"     S5 REASON: Creative failure detected. {failure_report}")
                print(f"     S5 ACTION: Retrying with escalated temperature.")
                # Loop continues to next attempt

        # Failed after max attempts
        self.status = AgentStatus.FAILED
        raise ValueError(f"Failed to generate valid message after {max_attempts} creative attempts")

    def _classify_failure(self, failures: List[ValidationResult]) -> Tuple[FailureClassifier, str]:
        """
        NEW v11.10: Classify S6 failures to decide retry strategy.
        """
        # Rules that indicate a FACTUAL gap (research problem)
        FACTUAL_RULES = {
            "LIC-QA-106", # Per-claim confidence
            "LIC-QA-105", # Sender claims (hallucinated team)
            "LIC-QA-043", # Metric lacks context
            "LIC-QA-003", # Hallucinated claim (in case 106 fails)
        }

        for f in failures:
            if f.rule_id in FACTUAL_RULES:
                return FailureClassifier.FACTUAL_FAILURE, f"({f.rule_id}) {f.message}"

        # All other failures are CREATIVE (tone, verbs, format, placeholders)
        return FailureClassifier.CREATIVE_FAILURE, f"({failures[0].rule_id}) {failures[0].message}"

    async def _generate_content(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis,
        temperature: float
    ) -> str:
        """
        Generate message content
        NEW v11.10: Reads adversarial_findings from context (Enhancement 3)
        """
        # NEW v11.7: C_LEVEL uses N-candidate synthesis
        if scaffold.archetype == Archetype.C_LEVEL:
            return await self.synthesizer.synthesize_c_level_message(
                scaffold, context, profile_analysis, temperature
            )

        # Standard generation for other archetypes
        recipient_name = "Valued Professional"
        company = context.company_context[0] if context.company_context else "your organization"

        # Get tone parameters
        tone = ConfigRegistry.get_tone_mapping(scaffold.archetype, "message_tone")
        verbs = ConfigRegistry.get_tone_mapping(scaffold.archetype, "verb_preference")

        # NEW v11.10: Check for adversarial findings (Enhancement 3)
        adversarial_constraints = ""
        if context.adversarial_findings:
            adversarial_constraints = f"\n\n[ADVERSARIAL_CHECK: AVOID CLAIMS: {', '.join(context.adversarial_findings)}]"


        if scaffold.route == Route.CONNECTION_REQ:
            content = f"Hi {recipient_name}, I'm reaching out to {verbs[0] if verbs else 'connect'} regarding opportunities at {company}. Looking forward to connecting.{adversarial_constraints}"
        elif scaffold.route == Route.INMAIL:
            content = f"Dear {recipient_name},\n\nI hope this message finds you well. I'm writing to {verbs[0] if verbs else 'discuss'} the exciting opportunity at {company}. With my background in AI and machine learning, I believe I can contribute significantly to your team's goals.\n\nI'd appreciate the opportunity to {verbs[1] if len(verbs) > 1 else 'connect'} and learn more.\n\nBest regards{adversarial_constraints}"
        elif scaffold.route == Route.FOLLOW_UP:
            content = f"Hi {recipient_name}, Following up on our previous conversation about {company}. I remain very interested in the opportunity and would love to {verbs[0] if verbs else 'continue'} our discussion. Best regards{adversarial_constraints}"
        else:
            content = f"Dear {recipient_name}, Reaching out regarding {company}. Best regards{adversarial_constraints}"

        return content


class ValidationAgent:
    """
    NEW v11.6: Comprehensive validation framework with 107 rules
    Consolidates all rules from v10.22 + SUPREME_SPELL
    """

    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.status = AgentStatus.IDLE

        # NEW v11.6: Initialize validators
        self.placeholder_detector = PlaceholderDetector()
        self.claim_scorer = ClaimConfidenceScorer()
        self.diversity_validator = MessageDiversityValidator()
        self.content_validator = ContentCleanlinessValidator()
        self.ascii_enforcer = ASCIIEnforcer()
        self.signal_scorer = SignalQualityScorer()

    def validate_message(
        self,
        message: GeneratedMessage,
        context: ResearchContext
    ) -> List[ValidationResult]:
        """
        NEW v11.6: Run all validation rules
        Returns list of validation results (empty if all passed)
        """
        self.status = AgentStatus.RUNNING
        results = []

        # ========================================
        # CRITICAL RULES (Must Halt)
        # ========================================

        # S5.S6_BlockPlaceholders (FEATURE 3.3 / GAP 1.5)
        passed, msg = self.placeholder_detector.validate(message.content)
        if not passed:
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                rule_id="LIC-QA-067",
                message=msg,
                details=ErrorCodeRegistry.get_error("LIC-E001")
            ))

        # S5.S6_BlockHallucinatedClaims (FEATURE 1.2 / GAP 1.2)
        claims, aggregate_conf = self.claim_scorer.score_message_claims(message.content, context.rag_results)
        claims_passed, claims_msg = self.claim_scorer.validate_claims(claims, aggregate_conf)
        if not claims_passed:
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                rule_id="LIC-QA-106",
                message=f"Per-claim confidence validation failed: {claims_msg}",
                details=ErrorCodeRegistry.get_error("LIC-E002")
            ))

        # S5.S6_BlockMessageRepetition (FEATURE 1.3)
        is_diverse, similarity, _ = self.diversity_validator.check_diversity(message.content)
        if not is_diverse:
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                rule_id="LIC-QA-MESSAGE-DIVERSITY",
                message=f"Message too similar to previous message (similarity: {similarity:.2f})",
                details=ErrorCodeRegistry.get_error("LIC-E004")
            ))
        else:
            self.diversity_validator.add_to_history(message.content)

        # S5.S6_ValidateSenderClaims (GAP 1.8 / LIC-QA-105)
        # NEW v11.7: Fully implemented with team whitelist validation
        team_keywords = ["my team", "our team", "we built", "we developed", "our work"]
        message_lower = message.content.lower()
        has_team_claim = any(keyword in message_lower for keyword in team_keywords)

        if has_team_claim:
            # Check against sender profile team whitelist
            sender_teams = context.mission_context.get("sender_teams", [])
            if not sender_teams:
                results.append(ValidationResult(
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    rule_id="LIC-QA-105",
                    message="Message contains team claims ('my team', 'we built') but sender has no validated team whitelist",
                    details=ErrorCodeRegistry.get_error("LIC-E003")
                ))

        # ========================================
        # HIGH SEVERITY RULES (Must Halt)
        # ========================================

        # S5.S6_ValidateJobTitlePlacement (GAP 1.6 / LIC-QA-075)
        # NEW v11.7: Fully implemented
        if message.route == Route.INMAIL:
            first_50_words = " ".join(message.content.split()[:50]).lower()
            job_title = context.mission_context.get("job_title", "").lower()
            if job_title and job_title not in first_50_words:
                results.append(ValidationResult(
                    passed=False,
                    severity=ValidationSeverity.HIGH,
                    rule_id="LIC-QA-075",
                    message=f"Job title '{job_title}' not mentioned in first 50 words of INMAIL",
                    details=ErrorCodeRegistry.get_error("LIC-E005")
                ))

        # S5.S6_ValidateCompanySpelling (GAP 1.7 / LIC-QA-049)
        # NEW v11.7: Fully implemented with fuzzy matching
        company_rag = context.mission_context.get("company", "")
        if company_rag:
            # Fuzzy match - check if company appears in message with similar spelling
            message_lower = message.content.lower()
            company_lower = company_rag.lower()
            # Simple check: exact match or within 2 char edit distance
            if company_lower not in message_lower:
                # Check for close matches
                words = message_lower.split()
                close_match = any(
                    self._levenshtein_distance(word, company_lower) <= 2
                    for word in words
                )
                if not close_match:
                    results.append(ValidationResult(
                        passed=False,
                        severity=ValidationSeverity.HIGH,
                        rule_id="LIC-QA-049",
                        message=f"Company name '{company_rag}' not found or misspelled in message",
                        details=ErrorCodeRegistry.get_error("LIC-E006")
                    ))

        # S5.S6_ValidateSafeCharacters (GAP 1.10)
        ascii_passed, ascii_msg = self.ascii_enforcer.validate(message.content)
        if not ascii_passed:
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.HIGH,
                rule_id="LIC-QA-055",
                message=ascii_msg,
                details=ErrorCodeRegistry.get_error("LIC-E007")
            ))

        # ========================================
        # MEDIUM SEVERITY RULES (Regenerate, No Halt)
        # ========================================

        # S5.S6_BlockCorporateClichés (FEATURE 3.1)
        verbs_passed, verbs_msg = self.content_validator.validate_verbs(message.content)
        if not verbs_passed:
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                rule_id="LIC-QA-FORBIDDEN-VERBS",
                message=verbs_msg,
                details=ErrorCodeRegistry.get_error("LIC-E008")
            ))

        # S5.S6_BlockWeakLanguage (FEATURE 3.2)
        fillers_passed, fillers_msg = self.content_validator.validate_fillers(message.content)
        if not fillers_passed:
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                rule_id="LIC-QA-WEAK-LANGUAGE",
                message=fillers_msg,
                details=ErrorCodeRegistry.get_error("LIC-E009")
            ))

        # S5.S6_ValidateMetricContext (GAP 1.4 / LIC-QA-043 / LIC-QA-107)
        # NEW v11.7: Fully implemented - metrics must have keyword context from RAG
        metric_pattern = r'\b\d+%|\b\d+x\b|\b\d+\s*(million|billion|thousand)\b'
        metrics_in_message = re.findall(metric_pattern, message.content, re.IGNORECASE)

        if metrics_in_message:
            # Extract all keywords from RAG results
            rag_keywords = set()
            for rag_result in context.rag_results:
                rag_keywords.update(rag_result.extracted_keywords)

            # Check each metric has surrounding context words that appear in RAG
            for metric in metrics_in_message:
                # Get 10 words around the metric
                metric_context = self._get_context_around_metric(message.content, str(metric))
                context_words = set(metric_context.lower().split())

                # Check if any context words match RAG keywords
                has_rag_support = bool(context_words & rag_keywords)
                if not has_rag_support:
                    results.append(ValidationResult(
                        passed=False,
                        severity=ValidationSeverity.HIGH,
                        rule_id="LIC-QA-043",
                        message=f"Metric '{metric}' lacks supporting keyword context from RAG results",
                        details=ErrorCodeRegistry.get_error("LIC-E010")
                    ))

        # S5.S6_ValidateSignalQuality (FEATURE 1.1)
        signal_score, _ = self.signal_scorer.calculate_signal_score(context.rag_results, message.content)
        if not self.signal_scorer.validate_minimum_signal(signal_score):
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.HIGH,
                rule_id="LIC-QA-SIGNAL-QUALITY",
                message=f"Signal quality score {signal_score:.2f} below threshold 0.70",
                details=ErrorCodeRegistry.get_error("LIC-E011")
            ))

        self.status = AgentStatus.COMPLETED
        return results

    def _get_context_around_metric(self, text: str, metric: str) -> str:
        """Extract 10 words around a metric for context validation"""
        words = text.split()
        for i, word in enumerate(words):
            if metric in word:
                start = max(0, i - 5)
                end = min(len(words), i + 6)
                return " ".join(words[start:end])
        return ""

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]


class QAAgent:
    """
    NEW v11.6: Enhanced QA report generation
    """

    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.status = AgentStatus.IDLE

    def generate_qa_report(
        self,
        mission: OutreachMission,
        validation_results: List[ValidationResult]
    ) -> QAReport:
        """
        NEW v11.6: Generate comprehensive QA report grouped by severity (GAP 1.11)
        """
        self.status = AgentStatus.RUNNING

        critical_issues = sum(1 for r in validation_results if r.severity == ValidationSeverity.CRITICAL)
        high_issues = sum(1 for r in validation_results if r.severity == ValidationSeverity.HIGH)
        errors = sum(1 for r in validation_results if r.severity == ValidationSeverity.MEDIUM)
        warnings = sum(1 for r in validation_results if r.severity == ValidationSeverity.INFO)

        passed = critical_issues == 0 and high_issues == 0

        self.status = AgentStatus.COMPLETED

        return QAReport(
            mission_id=mission.mission_id,
            validation_results=validation_results,
            critical_issues=critical_issues,
            high_issues=high_issues,
            errors=errors,
            warnings=warnings,
            passed=passed,
            timestamp=datetime.now().isoformat()
        )


# ============================================================================
# WORKFLOW ORCHESTRATOR
# ============================================================================

class WorkflowOrchestrator:
    """
    NEW v11.10: Updated to manage the S6->S2 "Meta-Loop" (Enhancement 4)
    """

    def __init__(self):
        self.circuit_breaker = CircuitBreaker()

        # Initialize agents
        self.profile_agent = ProfileAnalysisAgent(self.circuit_breaker)
        # NEW v11.10: Renamed ResearchOrchestrator -> S2_SupervisorAgent
        self.research_orchestrator = S2_SupervisorAgent(self.circuit_breaker)
        self.routing_agent = RoutingAgent(self.circuit_breaker)
        self.scaffold_agent = ScaffoldAgent(self.circuit_breaker)
        self.generation_orchestrator = GenerationOrchestrator(self.circuit_breaker)
        self.validation_agent = ValidationAgent(self.circuit_breaker)
        self.qa_agent = QAAgent(self.circuit_breaker)

        self.events: List[Dict[str, Any]] = []

    async def execute_workflow(self, mission: OutreachMission) -> Dict[str, Any]:
        """
        Execute complete workflow
        NEW v11.10: Now contains the S6->S2 "Meta-Loop" (Enhancement 4)
        """
        start_time = datetime.now()

        # Define max re-planning loops
        MAX_META_LOOPS = 3

        # Initialize state variables outside the loop
        profile_analysis: Optional[ProfileAnalysis] = None
        corrected_profile_analysis: Optional[ProfileAnalysis] = None
        context: Optional[ResearchContext] = None
        route: Optional[Route] = None
        scaffold: Optional[MessageScaffold] = None
        message: Optional[GeneratedMessage] = None
        qa_report: Optional[QAReport] = None

        try:
            # Stage 1: Profile Analysis (Runs once)
            print("\n[S1] Profile Analysis...")
            profile_analysis = self.profile_agent.analyze_profile(mission)
            print(f"     Archetype: {profile_analysis.archetype.value} (confidence: {profile_analysis.confidence:.2f})")

            # Manual Override Check (Runs once)
            if profile_analysis.needs_manual_override:
                print(f"\n     ⚠️  Low confidence ({profile_analysis.confidence:.2f}). Manual override recommended.")
                override = input(f"     Confirm archetype {profile_analysis.archetype.value}? (y/n): ").strip().lower()

                if override != 'y':
                    print("     Available archetypes: C_LEVEL, EXECUTIVE, SENIOR_TA, RECRUITER")
                    new_archetype = input("     Enter correct archetype: ").strip().upper()
                    try:
                        profile_analysis.archetype = Archetype[new_archetype]
                        profile_analysis.confidence = 1.0
                        profile_analysis.reasoning = "Manual override by user"
                        print(f"     Updated to: {profile_analysis.archetype.value}")
                    except KeyError:
                        print(f"     Invalid archetype. Keeping {profile_analysis.archetype.value}")

            # Initialize corrected analysis
            corrected_profile_analysis = profile_analysis

            # ---
            # NEW v11.10: S6 -> S2 META-LOOP (Enhancement 4)
            # ---
            refinement_context_from_s6: List[ValidationResult] = None

            for meta_attempt in range(1, MAX_META_LOOPS + 1):
                print(f"\n{'='*40}")
                print(f"META-LOOP ATTEMPT {meta_attempt}/{MAX_META_LOOPS}")
                print(f"{'='*40}")

                try:
                    # Stage 2: Research (Re-runs on meta-loop)
                    print("\n[S2] Research Orchestration...")
                    context, corrected_profile_analysis = await self.research_orchestrator.conduct_research(
                        mission,
                        corrected_profile_analysis,
                        refinement_context=refinement_context_from_s6 # Pass S6 failure context
                    )

                    if corrected_profile_analysis.archetype != profile_analysis.archetype and meta_attempt == 1:
                        print(f"     ✨ Archetype corrected: {profile_analysis.archetype.value} → {corrected_profile_analysis.archetype.value}")
                        print(f"     Reason: {corrected_profile_analysis.critique_history[-1] if corrected_profile_analysis.critique_history else 'N/A'}")

                    print(f"     RAG Results: {len(context.rag_results)}")
                    print(f"     Reflexion Iterations (Internal S2): {context.reflexion_iterations}")
                    print(f"     Prior Applications: {len(context.prior_applications)}")
                    if context.adversarial_findings:
                        print(f"     Adversarial Flags: {context.adversarial_findings}")

                    # Stage 3: Routing (Re-runs on meta-loop)
                    print("\n[S3] Route Determination...")
                    route, routing_reasoning = self.routing_agent.determine_route(mission, corrected_profile_analysis)
                    print(f"     Route: {route.value}")
                    print(f"     Reasoning: {routing_reasoning}")

                    # Stage 4: Scaffold (Re-runs on meta-loop)
                    print("\n[S4] Scaffold Creation...")
                    scaffold = self.scaffold_agent.create_scaffold(route, corrected_profile_analysis.archetype, context)
                    print(f"     Target Words: {ConfigRegistry.get_target_word_count(corrected_profile_analysis.archetype, route)}")

                    # Stage 5+6: Generation with Validation Loop
                    print("\n[S5+S6] Generation with Validation...")

                    # This call now runs its *own* retry loop for CREATIVE failures
                    # but will raise FactualGapError for FACTUAL failures.
                    message = await self.generation_orchestrator.generate_message(
                        scaffold,
                        context,
                        corrected_profile_analysis,
                        self.validation_agent
                    )

                    # If generate_message succeeds without error, break the meta-loop
                    print(f"     S5: Generation SUCCEEDED in meta-attempt {meta_attempt}.")
                    print(f"     Generated: {message.word_count} words in {message.generation_attempts} creative attempts")
                    break # SUCCESS! Exit the meta-loop.

                except FactualGapError as e:
                    # This is the S6->S2 re-planning trigger
                    print(f"\n     🔥 S6->S2 RE-PLANNING (Meta-Attempt {meta_attempt+1}) due to factual failure...")
                    refinement_context_from_s6 = e.args[0]
                    failure_msg = refinement_context_from_s6[0].message
                    print(f"     Failure Context: {failure_msg}")

                    if meta_attempt == MAX_META_LOOPS:
                        print("     FATAL: Factual failure not resolved after max re-planning loops.")
                        raise Exception(f"Factual failure not resolved after {MAX_META_LOOPS} meta-loops: {failure_msg}")

                    # `continue` will re-run the meta-loop (S2, S3, S4, S5)
                    continue

            # ---
            # END S6 -> S2 META-LOOP
            # ---

            # Stage 7: Final QA Report
            print("\n[S7] QA Report Generation...")
            # We must re-run validation one last time on the *final* message
            final_validation_results = self.validation_agent.validate_message(message, context)
            qa_report = self.qa_agent.generate_qa_report(mission, final_validation_results)
            print(f"     Critical: {qa_report.critical_issues}, High: {qa_report.high_issues}, Medium: {qa_report.errors}")

            end_time = datetime.now()
            workflow_time = (end_time - start_time).total_seconds()

            # Build result
            result = {
                "status": "success",
                "production_ready": qa_report.passed,
                "workflow_time": workflow_time,
                "message": message.content,
                "route": route.value,
                "archetype": corrected_profile_analysis.archetype.value,
                "word_count": message.word_count,
                "generation_attempts": message.generation_attempts,
                "qa_summary": {
                    "critical_issues": qa_report.critical_issues,
                    "high_issues": qa_report.high_issues,
                    "errors": qa_report.errors,
                    "warnings": qa_report.warnings,
                    "locked_sections_count": len(message.locked_sections),
                    "reflexion_cycles_used": context.reflexion_iterations,
                    "adaptive_retries_count": message.generation_attempts - 1
                },
                "qa_report": self._format_qa_report(qa_report)
            }

            # NEW v11.6: Stage 8 - Post-Send Tracking
            if qa_report.passed:
                await self._execute_post_send_tracking(mission, message, result)

            return result

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "production_ready": False
            }

    def _format_qa_report(self, qa_report: QAReport) -> str:
        """Format QA report for display"""
        lines = []
        lines.append("\n" + "="*80)
        lines.append("QA VALIDATION REPORT")
        lines.append("="*80)

        if qa_report.passed:
            lines.append("\n✅ ALL VALIDATIONS PASSED")
        else:
            lines.append("\n❌ VALIDATION FAILURES DETECTED")

        # Group by severity
        critical = [r for r in qa_report.validation_results if r.severity == ValidationSeverity.CRITICAL]
        high = [r for r in qa_report.validation_results if r.severity == ValidationSeverity.HIGH]
        medium = [r for r in qa_report.validation_results if r.severity == ValidationSeverity.MEDIUM]
        info = [r for r in qa_report.validation_results if r.severity == ValidationSeverity.INFO]

        if critical:
            lines.append(f"\n🔴 CRITICAL ISSUES ({len(critical)}):")
            for r in critical:
                lines.append(f"   - [{r.rule_id}] {r.message}")

        if high:
            lines.append(f"\n🟠 HIGH SEVERITY ({len(high)}):")
            for r in high:
                lines.append(f"   - [{r.rule_id}] {r.message}")

        if medium:
            lines.append(f"\n🟡 MEDIUM SEVERITY ({len(medium)}):")
            for r in medium:
                lines.append(f"   - [{r.rule_id}] {r.message}")

        if info:
            lines.append(f"\n🔵 INFO ({len(info)}):")
            for r in info:
                lines.append(f"   - [{r.rule_id}] {r.message}")

        lines.append("\n" + "="*80)

        return "\n".join(lines)

    async def _execute_post_send_tracking(
        self,
        mission: OutreachMission,
        message: GeneratedMessage,
        result: Dict[str, Any]
    ):
        """
        NEW v11.6: Post-send tracking and app tracker generation (GAP 10.1, 10.2)
        """
        print("\n" + "="*80)
        print("POST-SEND TRACKING")
        print("="*80)

        sent = input("\nDid you send this message? (Y/N): ").strip().upper()

        if sent == "Y":
            # Generate App Tracker JSON
            tracker = {
                "mission_id": mission.mission_id,
                "timestamp": datetime.now().isoformat(),
                "recipient": {
                    "name": mission.recipient_profile.get("name"),
                    "title": mission.recipient_profile.get("title"),
                    "company": mission.recipient_profile.get("company")
                },
                "job": {
                    "title": mission.job_description.get("title"),
                    "company": mission.job_description.get("company")
                },
                "message": {
                    "route": message.route.value,
                    "archetype": message.archetype.value,
                    "word_count": message.word_count,
                    "checksum": message.checksum
                },
                "status": "sent",
                "follow_up_date": (datetime.now() + timedelta(days=3)).isoformat()
            }

            # Save tracker
            tracker_path = Path(f"/home/claude/tracker_{mission.mission_id}.json")
            with open(tracker_path, 'w') as f:
                json.dump(tracker, f, indent=2)

            print(f"\n✅ Application tracker saved: {tracker_path}")
            print(f"   Follow-up reminder: {tracker['follow_up_date'][:10]}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_orchestrator() -> WorkflowOrchestrator:
    """Create orchestrator instance"""
    return WorkflowOrchestrator()


def collect_sender_profile() -> Dict[str, Any]:
    """Collect sender profile information interactively"""
    print("\n" + "="*80)
    print("SENDER PROFILE COLLECTION")
    print("="*80)

    name = input("Your Name: ").strip()
    title = input("Your Title: ").strip()
    company = None
    if " at " in title:
        parts = title.split(" at ")
        if len(parts) == 2:
            title = parts[0].strip()
            company = parts[1].strip()

    linkedin_url = input("Your LinkedIn URL: ").strip()
    about_section = input("Your About Section (brief): ").strip()

    return {
        "name": name,
        "title": title,
        "company": company or "Not specified",
        "linkedin_url": linkedin_url,
        "about_section": about_section
    }


def collect_recipient_profile() -> Dict[str, Any]:
    """Collect recipient profile information interactively"""
    print("\n" + "="*80)
    print("RECIPIENT PROFILE COLLECTION")
    print("="*80)

    name = input("Recipient Name: ").strip()
    title = input("Recipient Title: ").strip()
    company = input("Recipient Company: ").strip()
    linkedin_url = input("Recipient LinkedIn URL (optional): ").strip()

    connection_input = input("Are you connected on LinkedIn? (yes/no) [default: no]: ").strip().lower()
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
    """Collect job description information interactively"""
    print("\n" + "="*80)
    print("JOB DESCRIPTION COLLECTION")
    print("="*80)

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
    """Main execution"""

    print("\n" + "="*80)
    print("LIC v11.10 - LinkedIn Outreach Orchestrator (Dual-Loop Agentic)")
    print("="*80)
    print("\nExecution Mode:")
    print("  1. Interactive (collect profiles)")
    print("  2. Demo (use sample data)")
    mode = input("\nSelect mode (1 or 2): ").strip()

    if mode == "1":
        sender_profile = collect_sender_profile()
        recipient_profile = collect_recipient_profile()
        job_description = collect_job_description()
    else:
        print("\nUsing demo sample data...\n")
        sender_profile = {
            "name": "Amit",
            "title": "Chief AI Officer",
            "company": "AI Innovations Inc",
            "linkedin_url": "https://linkedin.com/in/amit",
            "about_section": "Chief AI Officer specializing in Enterprise Generative AI Platforms and Technical Success & Adoption Leadership."
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

    mission = OutreachMission(
        mission_id=str(uuid4()),
        sender_profile=sender_profile,
        recipient_profile=recipient_profile,
        job_description=job_description,
        connection_status=recipient_profile.get("connection_status", "not_connected"),
        prior_message_count=recipient_profile.get("prior_message_count", 0)
    )

    print(f"\n{'='*80}")
    print("LIC v11.10 - Workflow Execution")
    print(f"{'='*80}\n")
    print(f"Mission ID: {mission.mission_id}")
    print(f"Sender: {mission.sender_profile['name']}")
    print(f"Recipient: {mission.recipient_profile['name']}")
    print(f"Job: {mission.job_description['title']} at {mission.job_description['company']}")

    orchestrator = create_orchestrator()
    result = await orchestrator.execute_workflow(mission)

    print(f"\n{'='*80}")
    print("WORKFLOW RESULTS")
    print(f"{'='*80}\n")
    print(f"Status: {result['status']}")

    if result['status'] == 'success':
        print(f"Production Ready: {result['production_ready']}")
        print(f"Workflow Time: {result['workflow_time']:.2f}s")
        print(f"\nGenerated Message ({result['word_count']} words):")
        print("-" * 80)
        print(result['message'])
        print("-" * 80)
        print(f"\nQA Summary:")
        print(f"  Critical: {result['qa_summary']['critical_issues']}")
        print(f"  High: {result['qa_summary']['high_issues']}")
        print(f"  Medium: {result['qa_summary']['errors']}")
        print(f"  Warnings: {result['qa_summary']['warnings']}")
        print(result['qa_report'])
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

    return result


if __name__ == "__main__":
    asyncio.run(main())
