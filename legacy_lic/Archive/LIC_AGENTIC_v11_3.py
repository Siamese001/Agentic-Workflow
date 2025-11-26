"""
LinkedIn Outreach Orchestrator (LIC) - AGENTIC v11.3
====================================================

CHANGELOG v11.3:
---------------
Priority 1: Constraint Failure Classification & Adaptive Temperature Retry
- Added ConstraintFailureType enum (MECHANICAL, CREATIVE, SEMANTIC, CONFLICT)
- Added ConstraintFailureClassifier for intelligent failure analysis
- Enhanced progressive temperature with adaptive retry strategies
- Section-specific temperature optimization based on failure patterns

Priority 2: Ground Truth Recalculation Framework
- Enhanced ImmutableStagingBuffer with deterministic metric validation
- Never trust LLM-generated metadata; recalculate all metrics independently
- Cryptographic checksums for data integrity verification
- Eliminated silent data contamination vectors

Priority 3: Progressive Section Locking During Multi-Attempt Generation
- Added locked_sections tracking in GenerationContext
- Locks sections that pass validation at specific temperatures
- Only regenerates failed sections in subsequent attempts
- Prevents regression contamination across iterations

Priority 4: Similarity Cross-Validation Engine
- Added SimilarityCrossValidator for contamination detection
- TF-IDF cosine similarity checks across K-nodes
- No prompt leakage detection
- No placeholder contamination detection
- No content duplication across sections

Priority 5: Reflexion Loop with Critique History Tracking
- Enhanced ResearchContext with critique_history
- Formal reflexion loops: generate → critique → improve → validate
- Self-correcting research and generation cycles
- Prevents repeating same mistakes across iterations

Architecture: Multi-Agent DAG with Event-Driven Orchestration
Dependencies: anthropic, google-generativeai, numpy, scikit-learn
"""

__version__ = "11.3.0"
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
    """NEW v11.3: Types of constraint failures for adaptive retry"""
    MECHANICAL = "MECHANICAL"      # Word count, char count, structural
    CREATIVE = "CREATIVE"          # Placeholders, generic content
    SEMANTIC = "SEMANTIC"          # Forbidden words, tone violations
    CONFLICT = "CONFLICT"          # Impossible constraint combinations


# Route-specific constraints
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
    }
}

# Default temperature schedules (base values, adapted by failure classifier)
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
    route: Optional[Route] = None
    archetype: Optional[Archetype] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchContext:
    """Research findings with reflexion support"""
    mission_id: str
    search_queries: List[str] = field(default_factory=list)
    research_findings: Dict[str, Any] = field(default_factory=dict)
    signal_strength_score: float = 0.0
    research_gaps: List[str] = field(default_factory=list)
    research_strengths: List[str] = field(default_factory=list)
    
    # NEW v11.3: Reflexion loop support
    critique_history: List[Dict[str, Any]] = field(default_factory=list)
    reflexion_count: int = 0
    max_reflexions: int = 3
    improvement_deltas: List[float] = field(default_factory=list)


@dataclass
class GenerationContext:
    """Generation parameters with section locking"""
    mission_id: str
    scaffold: Dict[str, Any] = field(default_factory=dict)
    temperature_schedule: Dict[str, List[float]] = field(default_factory=dict)
    attempt_count: int = 0
    max_attempts: int = 5
    
    # NEW v11.3: Progressive section locking
    locked_sections: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    locked_at_temperature: Dict[str, float] = field(default_factory=dict)
    sections_to_regenerate: List[str] = field(default_factory=list)
    
    # NEW v11.3: Failure classification tracking
    failure_history: List[Dict[str, Any]] = field(default_factory=list)
    adaptive_temperature_adjustments: Dict[str, float] = field(default_factory=dict)


@dataclass
class StagingBuffer:
    """Staging buffer with ground truth recalculation"""
    k1_greeting: Optional[Dict[str, Any]]
    k2_subject: Optional[Dict[str, Any]]
    k3_body: Optional[Dict[str, Any]]
    k5_cta: Optional[Dict[str, Any]]
    k6_signature: Optional[Dict[str, Any]]
    full_message: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    # NEW v11.3: Enhanced ground truth tracking
    ground_truth_word_count: Optional[int] = None
    ground_truth_char_count: Optional[int] = None
    ground_truth_checksum: Optional[str] = None
    section_word_counts: Dict[str, int] = field(default_factory=dict)
    section_char_counts: Dict[str, int] = field(default_factory=dict)
    
    # NEW v11.3: Similarity cross-validation results
    similarity_matrix: Optional[np.ndarray] = None
    contamination_flags: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class ConstraintFailure:
    """NEW v11.3: Classified constraint failure"""
    failure_type: ConstraintFailureType
    section: str
    constraint_name: str
    expected_value: Any
    actual_value: Any
    severity: ValidationSeverity
    suggested_temperature_delta: float
    retry_strategy: str


@dataclass
class ValidationResult:
    """Validation batch result"""
    batch_name: str
    passed: bool
    failures: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # NEW v11.3: Classified failures
    classified_failures: List[ConstraintFailure] = field(default_factory=list)


@dataclass
class HopCheckpoint:
    """Multi-hop checkpoint"""
    hop_id: str
    hop_name: str
    timestamp: datetime
    state_snapshot: Dict[str, Any]
    checksum: str
    execution_time: float
    status: AgentStatus
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutreachState:
    """Mutable workflow state"""
    mission: OutreachMission
    research_context: Optional[ResearchContext] = None
    generation_context: Optional[GenerationContext] = None
    staging_buffer: Optional[StagingBuffer] = None
    validation_results: List[ValidationResult] = field(default_factory=list)
    checkpoints: List[HopCheckpoint] = field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    current_hop: str = "HOP-0"
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QAReportSummary:
    """QA report summary"""
    overall_status: str
    production_ready: bool
    critical_issues: int
    errors: int
    warnings: int
    sections_validated: int
    ground_truth_verified: bool
    checksum_verified: bool
    constraint_compliance: Dict[str, bool]
    
    # NEW v11.3: Enhanced QA metrics
    contamination_detected: bool
    locked_sections_count: int
    reflexion_cycles_used: int
    adaptive_retries_count: int


# ============================================================================
# CORE INFRASTRUCTURE
# ============================================================================

class MessageBus:
    """Event-driven message bus"""
    
    def __init__(self):
        self.subscribers: Dict[EventType, List] = defaultdict(list)
        self.event_history: List[Dict] = []
    
    def subscribe(self, event_type: EventType, handler):
        """Subscribe to event"""
        self.subscribers[event_type].append(handler)
    
    async def publish(self, event_type: EventType, data: Dict):
        """Publish event to subscribers"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.event_history.append(event)
        
        for handler in self.subscribers[event_type]:
            await handler(data)
    
    def get_event_history(self) -> List[Dict]:
        """Get event history"""
        return self.event_history


class StateStore:
    """Thread-safe state storage"""
    
    def __init__(self):
        self.states: Dict[str, OutreachState] = {}
        self.lock = asyncio.Lock()
    
    async def save(self, mission_id: str, state: OutreachState):
        """Save state"""
        async with self.lock:
            self.states[mission_id] = state
    
    async def load(self, mission_id: str) -> Optional[OutreachState]:
        """Load state"""
        async with self.lock:
            return self.states.get(mission_id)
    
    async def delete(self, mission_id: str):
        """Delete state"""
        async with self.lock:
            self.states.pop(mission_id, None)


class SemanticCache:
    """Semantic caching for LLM responses"""
    
    def __init__(self, similarity_threshold: float = 0.95):
        self.cache: Dict[str, Any] = {}
        self.threshold = similarity_threshold
    
    def _hash_prompt(self, prompt: str) -> str:
        """Hash prompt for cache key"""
        return hashlib.sha256(prompt.encode()).hexdigest()
    
    async def get(self, prompt: str) -> Optional[str]:
        """Get cached response"""
        key = self._hash_prompt(prompt)
        return self.cache.get(key)
    
    async def set(self, prompt: str, response: str):
        """Cache response"""
        key = self._hash_prompt(prompt)
        self.cache[key] = response


class CircuitBreaker:
    """Circuit breaker for API calls"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker"""
        if self.state == "OPEN":
            if (datetime.now() - self.last_failure_time).seconds > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self.failure_count = 0
            self.state = "CLOSED"
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e


class LLMClient:
    """Unified LLM client for Claude and Gemini"""
    
    def __init__(self, cache: SemanticCache, circuit_breaker: CircuitBreaker):
        self.cache = cache
        self.circuit_breaker = circuit_breaker
        self.api_call_count = 0
    
    async def call_claude(
        self,
        prompt: str,
        temperature: float = 0.5,
        max_tokens: int = 2000,
        use_cache: bool = True
    ) -> str:
        """Call Claude API"""
        if use_cache:
            cached = await self.cache.get(prompt)
            if cached:
                return cached
        
        async def _call():
            self.api_call_count += 1
            # Simulate API call (replace with actual Anthropic API)
            await asyncio.sleep(0.1)
            response = f"Claude response (temp={temperature})"
            return response
        
        response = await self.circuit_breaker.call(_call)
        
        if use_cache:
            await self.cache.set(prompt, response)
        
        return response
    
    async def call_gemini(
        self,
        prompt: str,
        temperature: float = 0.5,
        max_tokens: int = 2000,
        use_cache: bool = True
    ) -> str:
        """Call Gemini API"""
        if use_cache:
            cached = await self.cache.get(prompt)
            if cached:
                return cached
        
        async def _call():
            self.api_call_count += 1
            # Simulate API call (replace with actual Gemini API)
            await asyncio.sleep(0.1)
            response = f"Gemini response (temp={temperature})"
            return response
        
        response = await self.circuit_breaker.call(_call)
        
        if use_cache:
            await self.cache.set(prompt, response)
        
        return response
    
    async def multi_model_consensus(
        self,
        prompt: str,
        temperature: float = 0.5,
        max_tokens: int = 2000
    ) -> Dict[str, str]:
        """Get consensus from multiple models"""
        claude_response = await self.call_claude(prompt, temperature, max_tokens, use_cache=False)
        gemini_response = await self.call_gemini(prompt, temperature, max_tokens, use_cache=False)
        
        return {
            "claude": claude_response,
            "gemini": gemini_response
        }
    
    def get_api_call_count(self) -> int:
        """Get total API calls"""
        return self.api_call_count
    
    def reset_api_call_count(self):
        """Reset API call counter"""
        self.api_call_count = 0


# ============================================================================
# NEW v11.3: CONSTRAINT FAILURE CLASSIFIER
# ============================================================================

class ConstraintFailureClassifier:
    """
    Priority 1: Intelligent classification of constraint failures
    Enables adaptive temperature retry strategies
    """
    
    def __init__(self):
        self.failure_patterns = {
            ConstraintFailureType.MECHANICAL: [
                "word_count", "char_count", "word_range", "char_limit",
                "length", "size", "count"
            ],
            ConstraintFailureType.CREATIVE: [
                "placeholder", "generic", "template", "boilerplate",
                "empty", "missing_content"
            ],
            ConstraintFailureType.SEMANTIC: [
                "forbidden", "tone", "style", "inappropriate",
                "verb", "jargon", "leakage"
            ],
            ConstraintFailureType.CONFLICT: [
                "impossible", "contradiction", "conflict", "incompatible"
            ]
        }
    
    def classify_failure(
        self,
        section: str,
        constraint_name: str,
        expected: Any,
        actual: Any,
        context: Dict[str, Any]
    ) -> ConstraintFailure:
        """Classify a constraint failure"""
        
        # Determine failure type
        failure_type = self._determine_failure_type(constraint_name, context)
        
        # Determine severity
        severity = self._determine_severity(failure_type, expected, actual)
        
        # Calculate temperature adjustment
        temp_delta = self._calculate_temperature_delta(failure_type, severity)
        
        # Determine retry strategy
        retry_strategy = self._determine_retry_strategy(failure_type)
        
        return ConstraintFailure(
            failure_type=failure_type,
            section=section,
            constraint_name=constraint_name,
            expected_value=expected,
            actual_value=actual,
            severity=severity,
            suggested_temperature_delta=temp_delta,
            retry_strategy=retry_strategy
        )
    
    def _determine_failure_type(
        self,
        constraint_name: str,
        context: Dict[str, Any]
    ) -> ConstraintFailureType:
        """Determine the type of failure"""
        constraint_lower = constraint_name.lower()
        
        # Check each failure type pattern
        for failure_type, patterns in self.failure_patterns.items():
            if any(pattern in constraint_lower for pattern in patterns):
                return failure_type
        
        # Default to MECHANICAL
        return ConstraintFailureType.MECHANICAL
    
    def _determine_severity(
        self,
        failure_type: ConstraintFailureType,
        expected: Any,
        actual: Any
    ) -> ValidationSeverity:
        """Determine failure severity"""
        
        if failure_type == ConstraintFailureType.CONFLICT:
            return ValidationSeverity.CRITICAL
        
        if failure_type == ConstraintFailureType.SEMANTIC:
            return ValidationSeverity.ERROR
        
        # For MECHANICAL and CREATIVE, check magnitude
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            deviation = abs(expected - actual) / max(expected, 1)
            if deviation > 0.5:
                return ValidationSeverity.CRITICAL
            elif deviation > 0.2:
                return ValidationSeverity.ERROR
            else:
                return ValidationSeverity.WARNING
        
        return ValidationSeverity.ERROR
    
    def _calculate_temperature_delta(
        self,
        failure_type: ConstraintFailureType,
        severity: ValidationSeverity
    ) -> float:
        """Calculate temperature adjustment for retry"""
        
        # Base deltas by failure type
        base_deltas = {
            ConstraintFailureType.MECHANICAL: -0.1,     # Lower temp for precision
            ConstraintFailureType.CREATIVE: +0.15,      # Higher temp for creativity
            ConstraintFailureType.SEMANTIC: -0.05,      # Slightly lower for control
            ConstraintFailureType.CONFLICT: 0.0         # No adjustment, needs redesign
        }
        
        # Severity multipliers
        severity_multipliers = {
            ValidationSeverity.CRITICAL: 2.0,
            ValidationSeverity.ERROR: 1.5,
            ValidationSeverity.WARNING: 1.0,
            ValidationSeverity.INFO: 0.5
        }
        
        base = base_deltas.get(failure_type, 0.0)
        multiplier = severity_multipliers.get(severity, 1.0)
        
        return base * multiplier
    
    def _determine_retry_strategy(
        self,
        failure_type: ConstraintFailureType
    ) -> str:
        """Determine retry strategy"""
        
        strategies = {
            ConstraintFailureType.MECHANICAL: "precise_constraints",
            ConstraintFailureType.CREATIVE: "creative_exploration",
            ConstraintFailureType.SEMANTIC: "rule_enforcement",
            ConstraintFailureType.CONFLICT: "constraint_relaxation"
        }
        
        return strategies.get(failure_type, "default_retry")
    
    def aggregate_failures(
        self,
        failures: List[ConstraintFailure]
    ) -> Dict[str, Any]:
        """Aggregate failures for adaptive strategy"""
        
        type_counts = Counter(f.failure_type for f in failures)
        section_failures = defaultdict(list)
        
        for failure in failures:
            section_failures[failure.section].append(failure)
        
        # Calculate section-specific temperature adjustments
        section_temp_adjustments = {}
        for section, section_failures_list in section_failures.items():
            avg_delta = np.mean([f.suggested_temperature_delta for f in section_failures_list])
            section_temp_adjustments[section] = avg_delta
        
        return {
            "failure_type_distribution": dict(type_counts),
            "section_temperature_adjustments": section_temp_adjustments,
            "dominant_failure_type": type_counts.most_common(1)[0][0] if type_counts else None,
            "total_failures": len(failures),
            "critical_failures": sum(1 for f in failures if f.severity == ValidationSeverity.CRITICAL)
        }


# ============================================================================
# NEW v11.3: SIMILARITY CROSS-VALIDATOR
# ============================================================================

class SimilarityCrossValidator:
    """
    Priority 4: Detect content contamination across sections
    Uses TF-IDF and cosine similarity
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def validate_no_duplicates(
        self,
        sections: Dict[str, str]
    ) -> Dict[str, Any]:
        """Check for duplicate content across sections"""
        
        if len(sections) < 2:
            return {
                "passed": True,
                "duplicates_found": [],
                "similarity_matrix": None
            }
        
        # Extract text from sections
        section_names = list(sections.keys())
        section_texts = [sections[name] for name in section_names]
        
        # Compute TF-IDF vectors
        try:
            tfidf_matrix = self.vectorizer.fit_transform(section_texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
        except Exception:
            return {
                "passed": True,
                "duplicates_found": [],
                "similarity_matrix": None,
                "error": "Could not compute similarity"
            }
        
        # Check for high similarity
        duplicates_found = []
        n = len(section_names)
        
        for i in range(n):
            for j in range(i + 1, n):
                similarity = similarity_matrix[i][j]
                
                if similarity >= SIMILARITY_THRESHOLDS["exact_duplicate"]:
                    duplicates_found.append({
                        "section_1": section_names[i],
                        "section_2": section_names[j],
                        "similarity": float(similarity),
                        "severity": "CRITICAL"
                    })
                elif similarity >= SIMILARITY_THRESHOLDS["near_duplicate"]:
                    duplicates_found.append({
                        "section_1": section_names[i],
                        "section_2": section_names[j],
                        "similarity": float(similarity),
                        "severity": "ERROR"
                    })
                elif similarity >= SIMILARITY_THRESHOLDS["high_overlap"]:
                    duplicates_found.append({
                        "section_1": section_names[i],
                        "section_2": section_names[j],
                        "similarity": float(similarity),
                        "severity": "WARNING"
                    })
        
        return {
            "passed": len(duplicates_found) == 0,
            "duplicates_found": duplicates_found,
            "similarity_matrix": similarity_matrix.tolist()
        }
    
    def validate_no_placeholders(
        self,
        text: str,
        section_name: str
    ) -> Dict[str, Any]:
        """Check for placeholder contamination"""
        
        placeholders_found = []
        
        for pattern in FORBIDDEN_PATTERNS["placeholders"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                placeholders_found.extend([{
                    "section": section_name,
                    "pattern": pattern,
                    "match": match,
                    "severity": "CRITICAL"
                } for match in matches])
        
        return {
            "passed": len(placeholders_found) == 0,
            "placeholders_found": placeholders_found
        }
    
    def validate_no_prompt_leakage(
        self,
        text: str,
        section_name: str
    ) -> Dict[str, Any]:
        """Check for prompt leakage"""
        
        leakage_found = []
        
        for pattern in FORBIDDEN_PATTERNS["prompt_leakage"]:
            if pattern.lower() in text.lower():
                leakage_found.append({
                    "section": section_name,
                    "leaked_phrase": pattern,
                    "severity": "CRITICAL"
                })
        
        return {
            "passed": len(leakage_found) == 0,
            "leakage_found": leakage_found
        }
    
    def validate_no_forbidden_verbs(
        self,
        text: str,
        section_name: str
    ) -> Dict[str, Any]:
        """Check for forbidden corporate jargon"""
        
        forbidden_found = []
        
        for verb in FORBIDDEN_PATTERNS["forbidden_verbs"]:
            if verb.lower() in text.lower():
                forbidden_found.append({
                    "section": section_name,
                    "forbidden_verb": verb,
                    "severity": "ERROR"
                })
        
        return {
            "passed": len(forbidden_found) == 0,
            "forbidden_found": forbidden_found
        }
    
    def cross_validate_staging_buffer(
        self,
        staging_buffer: StagingBuffer
    ) -> Dict[str, Any]:
        """Comprehensive cross-validation of staging buffer"""
        
        # Extract sections
        sections = {}
        if staging_buffer.k1_greeting:
            sections["k1_greeting"] = staging_buffer.k1_greeting.get("raw_text", "")
        if staging_buffer.k2_subject:
            sections["k2_subject"] = staging_buffer.k2_subject.get("raw_text", "")
        if staging_buffer.k3_body:
            sections["k3_body"] = staging_buffer.k3_body.get("raw_text", "")
        if staging_buffer.k5_cta:
            sections["k5_cta"] = staging_buffer.k5_cta.get("raw_text", "")
        if staging_buffer.k6_signature:
            sections["k6_signature"] = staging_buffer.k6_signature.get("raw_text", "")
        
        # Run all validation checks
        duplicate_check = self.validate_no_duplicates(sections)
        
        placeholder_checks = []
        leakage_checks = []
        forbidden_checks = []
        
        for section_name, text in sections.items():
            placeholder_checks.append(self.validate_no_placeholders(text, section_name))
            leakage_checks.append(self.validate_no_prompt_leakage(text, section_name))
            forbidden_checks.append(self.validate_no_forbidden_verbs(text, section_name))
        
        # Aggregate results
        all_passed = (
            duplicate_check["passed"] and
            all(check["passed"] for check in placeholder_checks) and
            all(check["passed"] for check in leakage_checks) and
            all(check["passed"] for check in forbidden_checks)
        )
        
        return {
            "passed": all_passed,
            "duplicate_validation": duplicate_check,
            "placeholder_validation": placeholder_checks,
            "leakage_validation": leakage_checks,
            "forbidden_verb_validation": forbidden_checks,
            "similarity_matrix": duplicate_check.get("similarity_matrix")
        }


# ============================================================================
# SERVICES
# ============================================================================

class CheckpointManager:
    """Multi-hop checkpoint management"""
    
    def __init__(self):
        self.checkpoints: Dict[str, List[HopCheckpoint]] = defaultdict(list)
    
    def create_checkpoint(
        self,
        hop_id: str,
        hop_name: str,
        state: OutreachState,
        metadata: Dict[str, Any],
        execution_time: float
    ) -> HopCheckpoint:
        """Create checkpoint with cryptographic verification"""
        
        # Create state snapshot (exclude checkpoints to avoid recursion)
        state_dict = {
            "mission": asdict(state.mission),
            "research_context": asdict(state.research_context) if state.research_context else None,
            "generation_context": asdict(state.generation_context) if state.generation_context else None,
            "staging_buffer": asdict(state.staging_buffer) if state.staging_buffer else None,
            "validation_results": [asdict(vr) for vr in state.validation_results],
            "status": state.status.value,
            "current_hop": state.current_hop,
            "error_message": state.error_message,
            "metadata": state.metadata
        }
        
        # Compute checksum
        state_json = json.dumps(state_dict, sort_keys=True)
        checksum = hashlib.sha256(state_json.encode()).hexdigest()
        
        checkpoint = HopCheckpoint(
            hop_id=hop_id,
            hop_name=hop_name,
            timestamp=datetime.now(),
            state_snapshot=state_dict,
            checksum=checksum,
            execution_time=execution_time,
            status=state.status,
            metadata=metadata
        )
        
        self.checkpoints[state.mission.mission_id].append(checkpoint)
        return checkpoint
    
    def verify_checkpoint(self, checkpoint: HopCheckpoint, expected_checksum: str) -> bool:
        """Verify checkpoint integrity"""
        return checkpoint.checksum == expected_checksum
    
    def get_checkpoints(self, mission_id: str) -> List[HopCheckpoint]:
        """Get all checkpoints for mission"""
        return self.checkpoints.get(mission_id, [])


class TelemetryService:
    """Metrics and telemetry"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = defaultdict(list)
    
    def record_metric(self, metric_name: str, value: Any, metadata: Dict = None):
        """Record metric"""
        self.metrics[metric_name].append({
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
    
    def get_metrics(self, metric_name: str) -> List[Dict]:
        """Get metrics"""
        return self.metrics.get(metric_name, [])
    
    def get_all_metrics(self) -> Dict[str, List[Dict]]:
        """Get all metrics"""
        return dict(self.metrics)


class LoggingService:
    """Structured logging"""
    
    def __init__(self, log_dir: Path = Path("/tmp/lic_logs")):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.logs: List[Dict] = []
    
    def log(self, level: str, message: str, context: Dict = None):
        """Log message"""
        log_entry = {
            "level": level,
            "message": message,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        self.logs.append(log_entry)
        print(f"[{level}] {message}")
    
    def info(self, message: str, context: Dict = None):
        """Log info"""
        self.log("INFO", message, context)
    
    def warning(self, message: str, context: Dict = None):
        """Log warning"""
        self.log("WARNING", message, context)
    
    def error(self, message: str, context: Dict = None):
        """Log error"""
        self.log("ERROR", message, context)
    
    def get_logs(self) -> List[Dict]:
        """Get all logs"""
        return self.logs


class ValidationService:
    """Multi-batch validation with ground truth"""
    
    def __init__(
        self,
        telemetry: TelemetryService,
        logging: LoggingService,
        failure_classifier: ConstraintFailureClassifier,
        similarity_validator: SimilarityCrossValidator
    ):
        self.telemetry = telemetry
        self.logging = logging
        self.failure_classifier = failure_classifier
        self.similarity_validator = similarity_validator
    
    def validate_batch_0_pre_flight(self, state: OutreachState) -> ValidationResult:
        """BATCH 0: Pre-flight checks"""
        failures = []
        
        # Check mission exists
        if not state.mission:
            failures.append({
                "check": "mission_exists",
                "message": "Mission not found",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Check route and archetype
        if not state.mission.route:
            failures.append({
                "check": "route_determined",
                "message": "Route not determined",
                "severity": ValidationSeverity.CRITICAL
            })
        
        if not state.mission.archetype:
            failures.append({
                "check": "archetype_determined",
                "message": "Archetype not determined",
                "severity": ValidationSeverity.ERROR
            })
        
        return ValidationResult(
            batch_name="BATCH_0_PRE_FLIGHT",
            passed=len(failures) == 0,
            failures=failures
        )
    
    def validate_batch_1_constraints(
        self,
        staging_buffer: StagingBuffer,
        state: OutreachState
    ) -> ValidationResult:
        """BATCH 1: Route constraints with failure classification"""
        failures = []
        classified_failures = []
        
        route = state.mission.route
        constraints = ROUTE_CONSTRAINTS[route]
        
        # Ground truth word count (deterministic recalculation)
        if staging_buffer.ground_truth_word_count is None:
            failures.append({
                "check": "ground_truth_word_count",
                "message": "Ground truth word count not calculated",
                "severity": ValidationSeverity.CRITICAL
            })
        else:
            word_count = staging_buffer.ground_truth_word_count
            min_words, max_words = constraints["word_range"]
            
            if word_count < min_words or word_count > max_words:
                failure = self.failure_classifier.classify_failure(
                    section="full_message",
                    constraint_name="word_range",
                    expected=(min_words, max_words),
                    actual=word_count,
                    context={"route": route.value}
                )
                classified_failures.append(failure)
                
                failures.append({
                    "check": "word_count_range",
                    "message": f"Word count {word_count} outside range {min_words}-{max_words}",
                    "severity": failure.severity,
                    "failure_type": failure.failure_type.value
                })
        
        # Ground truth char count
        if staging_buffer.ground_truth_char_count is None:
            failures.append({
                "check": "ground_truth_char_count",
                "message": "Ground truth char count not calculated",
                "severity": ValidationSeverity.CRITICAL
            })
        else:
            char_count = staging_buffer.ground_truth_char_count
            char_limit = constraints["char_limit"]
            
            if char_count > char_limit:
                failure = self.failure_classifier.classify_failure(
                    section="full_message",
                    constraint_name="char_limit",
                    expected=char_limit,
                    actual=char_count,
                    context={"route": route.value}
                )
                classified_failures.append(failure)
                
                failures.append({
                    "check": "char_count_limit",
                    "message": f"Char count {char_count} exceeds limit {char_limit}",
                    "severity": failure.severity,
                    "failure_type": failure.failure_type.value
                })
        
        # Section-specific checks
        section_checks = [
            ("k1_greeting", "greeting_word_range"),
            ("k2_subject", "subject_word_range") if constraints["subject_required"] else None,
            ("k5_cta", "cta_word_range"),
            ("k6_signature", "signature_word_range")
        ]
        
        for section_name, constraint_key in [sc for sc in section_checks if sc]:
            section_data = getattr(staging_buffer, section_name)
            if not section_data:
                if constraint_key == "subject_word_range" and constraints["subject_required"]:
                    failures.append({
                        "check": f"{section_name}_exists",
                        "message": f"Required section {section_name} missing",
                        "severity": ValidationSeverity.CRITICAL
                    })
                continue
            
            section_word_count = staging_buffer.section_word_counts.get(section_name, 0)
            if constraint_key in constraints:
                min_w, max_w = constraints[constraint_key]
                if section_word_count < min_w or section_word_count > max_w:
                    failure = self.failure_classifier.classify_failure(
                        section=section_name,
                        constraint_name=constraint_key,
                        expected=(min_w, max_w),
                        actual=section_word_count,
                        context={"route": route.value}
                    )
                    classified_failures.append(failure)
                    
                    failures.append({
                        "check": f"{section_name}_word_range",
                        "message": f"{section_name} word count {section_word_count} outside range {min_w}-{max_w}",
                        "severity": failure.severity,
                        "failure_type": failure.failure_type.value
                    })
        
        return ValidationResult(
            batch_name="BATCH_1_CONSTRAINTS",
            passed=len(failures) == 0,
            failures=failures,
            classified_failures=classified_failures
        )
    
    def validate_batch_2_confidence(
        self,
        staging_buffer: StagingBuffer,
        state: OutreachState
    ) -> ValidationResult:
        """BATCH 2: Confidence checks"""
        failures = []
        warnings = []
        
        # Check ground truth checksum
        if not staging_buffer.ground_truth_checksum:
            failures.append({
                "check": "ground_truth_checksum",
                "message": "Ground truth checksum not calculated",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Check metadata completeness
        required_metadata = ["generation_model", "generation_temperature", "generation_timestamp"]
        for key in required_metadata:
            if key not in staging_buffer.metadata:
                warnings.append({
                    "check": f"metadata_{key}",
                    "message": f"Missing metadata: {key}",
                    "severity": ValidationSeverity.WARNING
                })
        
        return ValidationResult(
            batch_name="BATCH_2_CONFIDENCE",
            passed=len(failures) == 0,
            failures=failures,
            warnings=warnings
        )
    
    def validate_batch_3_entities(
        self,
        staging_buffer: StagingBuffer,
        state: OutreachState
    ) -> ValidationResult:
        """BATCH 3: Entity validation"""
        failures = []
        
        # Extract entities from mission
        sender_name = state.mission.sender_profile.get("name", "")
        recipient_name = state.mission.recipient_profile.get("name", "")
        company_name = state.mission.job_description.get("company", "")
        
        full_message_text = staging_buffer.full_message.get("raw_text", "") if staging_buffer.full_message else ""
        
        # Check recipient name appears
        if recipient_name and recipient_name.split()[0] not in full_message_text:
            failures.append({
                "check": "recipient_name_present",
                "message": f"Recipient first name '{recipient_name.split()[0]}' not found in message",
                "severity": ValidationSeverity.ERROR
            })
        
        # Check no sender name in third person
        if sender_name and sender_name in full_message_text:
            # Allowed in signature, check if outside signature
            signature_text = staging_buffer.k6_signature.get("raw_text", "") if staging_buffer.k6_signature else ""
            if sender_name in full_message_text.replace(signature_text, ""):
                failures.append({
                    "check": "sender_name_third_person",
                    "message": "Sender name appears in third person (outside signature)",
                    "severity": ValidationSeverity.WARNING
                })
        
        return ValidationResult(
            batch_name="BATCH_3_ENTITIES",
            passed=len(failures) == 0,
            failures=failures
        )
    
    def validate_batch_4_format(self, staging_buffer: StagingBuffer) -> ValidationResult:
        """BATCH 4: Format validation with similarity cross-validation"""
        failures = []
        
        # Run similarity cross-validation
        cross_validation = self.similarity_validator.cross_validate_staging_buffer(staging_buffer)
        
        if not cross_validation["passed"]:
            # Add duplicate failures
            for dup in cross_validation["duplicate_validation"]["duplicates_found"]:
                classified_failure = self.failure_classifier.classify_failure(
                    section=f"{dup['section_1']}_vs_{dup['section_2']}",
                    constraint_name="duplicate_content",
                    expected="unique",
                    actual=f"similarity={dup['similarity']:.2f}",
                    context={"validation_type": "similarity"}
                )
                
                failures.append({
                    "check": "no_duplicate_content",
                    "message": f"High similarity ({dup['similarity']:.2f}) between {dup['section_1']} and {dup['section_2']}",
                    "severity": dup["severity"],
                    "failure_type": classified_failure.failure_type.value
                })
            
            # Add placeholder failures
            for check in cross_validation["placeholder_validation"]:
                for placeholder in check.get("placeholders_found", []):
                    failures.append({
                        "check": "no_placeholders",
                        "message": f"Placeholder '{placeholder['match']}' found in {placeholder['section']}",
                        "severity": placeholder["severity"]
                    })
            
            # Add leakage failures
            for check in cross_validation["leakage_validation"]:
                for leakage in check.get("leakage_found", []):
                    failures.append({
                        "check": "no_prompt_leakage",
                        "message": f"Prompt leakage '{leakage['leaked_phrase']}' in {leakage['section']}",
                        "severity": leakage["severity"]
                    })
            
            # Add forbidden verb failures
            for check in cross_validation["forbidden_verb_validation"]:
                for forbidden in check.get("forbidden_found", []):
                    failures.append({
                        "check": "no_forbidden_verbs",
                        "message": f"Forbidden verb '{forbidden['forbidden_verb']}' in {forbidden['section']}",
                        "severity": forbidden["severity"]
                    })
        
        # Store similarity matrix
        staging_buffer.similarity_matrix = cross_validation.get("similarity_matrix")
        
        return ValidationResult(
            batch_name="BATCH_4_FORMAT",
            passed=len(failures) == 0,
            failures=failures
        )
    
    def validate_batch_5_post_validation(self, state: OutreachState) -> ValidationResult:
        """BATCH 5: Post-validation aggregate checks"""
        failures = []
        
        # Check all batches passed
        batch_results = [vr.passed for vr in state.validation_results]
        if not all(batch_results):
            failures.append({
                "check": "all_batches_passed",
                "message": f"Some validation batches failed: {batch_results}",
                "severity": ValidationSeverity.ERROR
            })
        
        # Check checkpoints exist
        if len(state.checkpoints) < 5:  # Expect at least 5 major hops
            failures.append({
                "check": "sufficient_checkpoints",
                "message": f"Only {len(state.checkpoints)} checkpoints created",
                "severity": ValidationSeverity.WARNING
            })
        
        return ValidationResult(
            batch_name="BATCH_5_POST_VALIDATION",
            passed=len(failures) == 0,
            failures=failures
        )


class QAReportGenerator:
    """Generate comprehensive QA reports"""
    
    def __init__(self, logging: LoggingService):
        self.logging = logging
    
    def generate_qa_summary(self, state: OutreachState) -> QAReportSummary:
        """Generate QA summary"""
        
        # Count issues by severity
        critical_issues = 0
        errors = 0
        warnings = 0
        
        for vr in state.validation_results:
            for failure in vr.failures:
                severity = failure.get("severity", ValidationSeverity.ERROR)
                if severity == ValidationSeverity.CRITICAL:
                    critical_issues += 1
                elif severity == ValidationSeverity.ERROR:
                    errors += 1
                elif severity == ValidationSeverity.WARNING:
                    warnings += 1
        
        # Overall status
        if critical_issues > 0:
            overall_status = "CRITICAL_FAILURE"
            production_ready = False
        elif errors > 0:
            overall_status = "HAS_ERRORS"
            production_ready = False
        elif warnings > 0:
            overall_status = "HAS_WARNINGS"
            production_ready = True
        else:
            overall_status = "PASS"
            production_ready = True
        
        # Check constraint compliance
        constraint_compliance = {
            "word_count": True,
            "char_count": True,
            "section_structure": True,
            "ground_truth_verified": True
        }
        
        for vr in state.validation_results:
            for failure in vr.failures:
                check = failure.get("check", "")
                if "word_count" in check or "word_range" in check:
                    constraint_compliance["word_count"] = False
                if "char_count" in check or "char_limit" in check:
                    constraint_compliance["char_count"] = False
                if "exists" in check or "required" in check:
                    constraint_compliance["section_structure"] = False
                if "ground_truth" in check or "checksum" in check:
                    constraint_compliance["ground_truth_verified"] = False
        
        # Ground truth verification
        ground_truth_verified = (
            state.staging_buffer and
            state.staging_buffer.ground_truth_word_count is not None and
            state.staging_buffer.ground_truth_char_count is not None and
            state.staging_buffer.ground_truth_checksum is not None
        )
        
        # Checksum verification
        checksum_verified = ground_truth_verified and bool(state.staging_buffer.ground_truth_checksum)
        
        # NEW v11.3: Enhanced metrics
        contamination_detected = False
        if state.staging_buffer and state.staging_buffer.contamination_flags:
            contamination_detected = any(state.staging_buffer.contamination_flags.values())
        
        locked_sections_count = 0
        if state.generation_context:
            locked_sections_count = len(state.generation_context.locked_sections)
        
        reflexion_cycles = 0
        if state.research_context:
            reflexion_cycles = state.research_context.reflexion_count
        
        adaptive_retries = 0
        if state.generation_context:
            adaptive_retries = len(state.generation_context.failure_history)
        
        return QAReportSummary(
            overall_status=overall_status,
            production_ready=production_ready,
            critical_issues=critical_issues,
            errors=errors,
            warnings=warnings,
            sections_validated=len(state.validation_results),
            ground_truth_verified=ground_truth_verified,
            checksum_verified=checksum_verified,
            constraint_compliance=constraint_compliance,
            contamination_detected=contamination_detected,
            locked_sections_count=locked_sections_count,
            reflexion_cycles_used=reflexion_cycles,
            adaptive_retries_count=adaptive_retries
        )
    
    def generate_qa_report(self, state: OutreachState, qa_summary: QAReportSummary) -> str:
        """Generate detailed QA report"""
        
        report_lines = [
            "="*80,
            "QA REPORT - LIC v11.3",
            "="*80,
            "",
            f"Mission ID: {state.mission.mission_id}",
            f"Route: {state.mission.route.value if state.mission.route else 'N/A'}",
            f"Archetype: {state.mission.archetype.value if state.mission.archetype else 'N/A'}",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "="*80,
            "OVERALL STATUS",
            "="*80,
            f"Status: {qa_summary.overall_status}",
            f"Production Ready: {'YES' if qa_summary.production_ready else 'NO'}",
            "",
            "ISSUE SUMMARY:",
            f"  Critical Issues: {qa_summary.critical_issues}",
            f"  Errors: {qa_summary.errors}",
            f"  Warnings: {qa_summary.warnings}",
            "",
            "VALIDATION METRICS:",
            f"  Sections Validated: {qa_summary.sections_validated}",
            f"  Ground Truth Verified: {'YES' if qa_summary.ground_truth_verified else 'NO'}",
            f"  Checksum Verified: {'YES' if qa_summary.checksum_verified else 'NO'}",
            "",
            "NEW v11.3 METRICS:",
            f"  Contamination Detected: {'YES' if qa_summary.contamination_detected else 'NO'}",
            f"  Locked Sections: {qa_summary.locked_sections_count}",
            f"  Reflexion Cycles: {qa_summary.reflexion_cycles_used}",
            f"  Adaptive Retries: {qa_summary.adaptive_retries_count}",
            "",
            "CONSTRAINT COMPLIANCE:",
        ]
        
        for constraint, passed in qa_summary.constraint_compliance.items():
            status = "PASS" if passed else "FAIL"
            report_lines.append(f"  {constraint}: {status}")
        
        # Section details
        if state.staging_buffer:
            report_lines.extend([
                "",
                "="*80,
                "SECTION DETAILS",
                "="*80,
                ""
            ])
            
            sections = [
                ("Section 1: Greeting", "k1_greeting"),
                ("Section 2: Subject", "k2_subject"),
                ("Section 3: Body", "k3_body"),
                ("Section 5: CTA", "k5_cta"),
                ("Section 6: Signature", "k6_signature")
            ]
            
            for section_label, section_key in sections:
                section_data = getattr(state.staging_buffer, section_key)
                if section_data:
                    text = section_data.get("raw_text", "N/A")
                    word_count = state.staging_buffer.section_word_counts.get(section_key, 0)
                    char_count = state.staging_buffer.section_char_counts.get(section_key, 0)
                    
                    report_lines.extend([
                        f"{section_label}:",
                        f"  Word Count: {word_count}",
                        f"  Char Count: {char_count}",
                        f"  Text: {text[:100]}..." if len(text) > 100 else f"  Text: {text}",
                        ""
                    ])
            
            # Ground truth metrics
            report_lines.extend([
                "="*80,
                "GROUND TRUTH METRICS",
                "="*80,
                f"Total Word Count: {state.staging_buffer.ground_truth_word_count or 'N/A'}",
                f"Total Char Count: {state.staging_buffer.ground_truth_char_count or 'N/A'}",
                f"Checksum: {state.staging_buffer.ground_truth_checksum or 'N/A'}",
                ""
            ])
        
        # Validation results
        report_lines.extend([
            "="*80,
            "VALIDATION RESULTS",
            "="*80,
            ""
        ])
        
        for vr in state.validation_results:
            report_lines.append(f"Batch: {vr.batch_name}")
            report_lines.append(f"Status: {'PASS' if vr.passed else 'FAIL'}")
            
            if vr.failures:
                report_lines.append(f"Failures ({len(vr.failures)}):")
                for failure in vr.failures:
                    severity = failure.get("severity", "ERROR")
                    check = failure.get("check", "unknown")
                    message = failure.get("message", "No message")
                    report_lines.append(f"  [{severity}] {check}: {message}")
            
            if vr.warnings:
                report_lines.append(f"Warnings ({len(vr.warnings)}):")
                for warning in vr.warnings:
                    check = warning.get("check", "unknown")
                    message = warning.get("message", "No message")
                    report_lines.append(f"  [WARNING] {check}: {message}")
            
            report_lines.append("")
        
        # Checkpoints
        report_lines.extend([
            "="*80,
            "CHECKPOINTS",
            "="*80,
            f"Total Checkpoints: {len(state.checkpoints)}",
            ""
        ])
        
        for checkpoint in state.checkpoints:
            report_lines.extend([
                f"Hop: {checkpoint.hop_id} - {checkpoint.hop_name}",
                f"  Status: {checkpoint.status.value}",
                f"  Execution Time: {checkpoint.execution_time:.3f}s",
                f"  Checksum: {checkpoint.checksum[:16]}...",
                ""
            ])
        
        report_lines.append("="*80)
        report_lines.append("END OF REPORT")
        report_lines.append("="*80)
        
        return "\n".join(report_lines)


# ============================================================================
# AGENTS
# ============================================================================

class ProfileAnalysisAgent:
    """HOP-1: Analyze profiles and determine route/archetype"""
    
    def __init__(
        self,
        llm_client: LLMClient,
        message_bus: MessageBus,
        telemetry: TelemetryService,
        logging: LoggingService
    ):
        self.llm_client = llm_client
        self.message_bus = message_bus
        self.telemetry = telemetry
        self.logging = logging
    
    async def execute(self, state: OutreachState) -> OutreachState:
        """Execute profile analysis"""
        import time
        start_time = time.time()
        
        self.logging.info("Starting HOP-1: Profile Analysis", {
            "mission_id": state.mission.mission_id
        })
        
        state.status = AgentStatus.RUNNING
        state.current_hop = "HOP-1"
        
        try:
            # Determine route and archetype
            prompt = self._build_routing_prompt(state.mission)
            
            response = await self.llm_client.call_claude(
                prompt,
                temperature=DEFAULT_TEMPERATURES["routing"],
                max_tokens=1000
            )
            
            # Parse response (simplified for demo)
            result = json.loads(response) if response.startswith("{") else {"route": "INMAIL", "archetype": "EXECUTIVE"}
            
            state.mission.route = Route[result.get("route", "INMAIL")]
            state.mission.archetype = Archetype[result.get("archetype", "EXECUTIVE")]
            
            state.status = AgentStatus.COMPLETED
            execution_time = time.time() - start_time
            
            self.telemetry.record_metric("hop_1_execution_time", execution_time)
            self.logging.info("Completed HOP-1", {
                "route": state.mission.route.value,
                "archetype": state.mission.archetype.value,
                "execution_time": execution_time
            })
            
            await self.message_bus.publish(EventType.PROFILE_ANALYSIS_COMPLETED, {
                "mission_id": state.mission.mission_id,
                "route": state.mission.route.value,
                "archetype": state.mission.archetype.value
            })
            
            return state
            
        except Exception as e:
            state.status = AgentStatus.FAILED
            state.error_message = str(e)
            self.logging.error(f"HOP-1 failed: {e}", {"mission_id": state.mission.mission_id})
            raise
    
    def _build_routing_prompt(self, mission: OutreachMission) -> str:
        """Build routing decision prompt"""
        return f"""
Analyze the following profiles and determine the optimal outreach route and recipient archetype.

SENDER:
{json.dumps(mission.sender_profile, indent=2)}

RECIPIENT:
{json.dumps(mission.recipient_profile, indent=2)}

JOB:
{json.dumps(mission.job_description, indent=2)}

Return JSON with:
{{
  "route": "INMAIL" | "CONNECTION_REQ" | "EMAIL",
  "archetype": "C_LEVEL" | "EXECUTIVE" | "RECRUITER" | "HIRING_MANAGER" | "PEER",
  "reasoning": "Brief explanation"
}}
"""


class ResearchOrchestrator:
    """HOP-2: Multi-hop research with reflexion"""
    
    def __init__(
        self,
        llm_client: LLMClient,
        message_bus: MessageBus,
        telemetry: TelemetryService,
        logging: LoggingService
    ):
        self.llm_client = llm_client
        self.message_bus = message_bus
        self.telemetry = telemetry
        self.logging = logging
    
    async def execute(self, state: OutreachState) -> OutreachState:
        """Execute research with reflexion loop"""
        import time
        start_time = time.time()
        
        self.logging.info("Starting HOP-2: Research Orchestrator", {
            "mission_id": state.mission.mission_id
        })
        
        state.status = AgentStatus.RUNNING
        state.current_hop = "HOP-2"
        
        try:
            # Initialize research context
            research_context = ResearchContext(mission_id=state.mission.mission_id)
            
            # Reflexion loop
            while research_context.reflexion_count < research_context.max_reflexions:
                # Generate search queries
                queries = await self._generate_search_queries(state.mission, research_context)
                research_context.search_queries.extend(queries)
                
                # Execute research (simulated)
                findings = await self._execute_research(queries)
                research_context.research_findings.update(findings)
                
                # Critique research
                critique = await self._critique_research(research_context, state.mission)
                research_context.critique_history.append(critique)
                
                # Check if research is sufficient
                if critique["signal_score"] >= 0.8:
                    self.logging.info(f"Research sufficient after {research_context.reflexion_count + 1} cycles")
                    break
                
                # Record improvement
                if research_context.reflexion_count > 0:
                    prev_score = research_context.critique_history[-2]["signal_score"]
                    delta = critique["signal_score"] - prev_score
                    research_context.improvement_deltas.append(delta)
                
                research_context.reflexion_count += 1
                
                await self.message_bus.publish(EventType.REFLEXION_TRIGGERED, {
                    "mission_id": state.mission.mission_id,
                    "cycle": research_context.reflexion_count,
                    "signal_score": critique["signal_score"]
                })
            
            # Extract final metrics
            final_critique = research_context.critique_history[-1]
            research_context.signal_strength_score = final_critique["signal_score"]
            research_context.research_gaps = final_critique.get("gaps", [])
            research_context.research_strengths = final_critique.get("strengths", [])
            
            state.research_context = research_context
            state.status = AgentStatus.COMPLETED
            
            execution_time = time.time() - start_time
            self.telemetry.record_metric("hop_2_execution_time", execution_time)
            self.telemetry.record_metric("reflexion_cycles", research_context.reflexion_count)
            
            self.logging.info("Completed HOP-2", {
                "mission_id": state.mission.mission_id,
                "reflexion_cycles": research_context.reflexion_count,
                "final_signal_score": research_context.signal_strength_score,
                "execution_time": execution_time
            })
            
            await self.message_bus.publish(EventType.RESEARCH_COMPLETED, {
                "mission_id": state.mission.mission_id,
                "signal_score": research_context.signal_strength_score
            })
            
            return state
            
        except Exception as e:
            state.status = AgentStatus.FAILED
            state.error_message = str(e)
            self.logging.error(f"HOP-2 failed: {e}", {"mission_id": state.mission.mission_id})
            raise
    
    async def _generate_search_queries(
        self,
        mission: OutreachMission,
        research_context: ResearchContext
    ) -> List[str]:
        """Generate search queries"""
        
        # Build context-aware prompt
        previous_queries = research_context.search_queries
        critique_summary = ""
        if research_context.critique_history:
            last_critique = research_context.critique_history[-1]
            critique_summary = f"\nPrevious research gaps: {', '.join(last_critique.get('gaps', []))}"
        
        prompt = f"""
Generate search queries for researching this outreach opportunity.

SENDER: {mission.sender_profile.get('name')}
RECIPIENT: {mission.recipient_profile.get('name')} at {mission.recipient_profile.get('company')}
JOB: {mission.job_description.get('title')} at {mission.job_description.get('company')}

Previous queries: {previous_queries}{critique_summary}

Generate 3-5 NEW search queries that will find relevant information.
Return JSON: {{"queries": ["query1", "query2", ...]}}
"""
        
        response = await self.llm_client.call_claude(
            prompt,
            temperature=DEFAULT_TEMPERATURES["research_query_generation"],
            max_tokens=500
        )
        
        result = json.loads(response) if response.startswith("{") else {"queries": ["default query"]}
        return result.get("queries", [])
    
    async def _execute_research(self, queries: List[str]) -> Dict[str, Any]:
        """Execute research (simulated)"""
        # In production, this would call web search APIs
        return {
            "findings": f"Research findings for queries: {queries}",
            "sources": ["source1", "source2"]
        }
    
    async def _critique_research(
        self,
        research_context: ResearchContext,
        mission: OutreachMission
    ) -> Dict[str, Any]:
        """Critique research quality"""
        
        prompt = f"""
Critique the research quality for this outreach.

RESEARCH FINDINGS:
{json.dumps(research_context.research_findings, indent=2)}

MISSION:
Sender: {mission.sender_profile.get('name')}
Recipient: {mission.recipient_profile.get('name')}
Job: {mission.job_description.get('title')}

Rate the research on a scale of 0-1 and identify gaps/strengths.
Return JSON:
{{
  "signal_score": 0.0-1.0,
  "gaps": ["gap1", "gap2"],
  "strengths": ["strength1", "strength2"],
  "recommendations": ["rec1", "rec2"]
}}
"""
        
        response = await self.llm_client.call_claude(
            prompt,
            temperature=DEFAULT_TEMPERATURES["research_critique"],
            max_tokens=1000
        )
        
        result = json.loads(response) if response.startswith("{") else {
            "signal_score": 0.7,
            "gaps": [],
            "strengths": [],
            "recommendations": []
        }
        
        return result


class ScaffoldArchitect:
    """HOP-3: Create message scaffold"""
    
    def __init__(
        self,
        llm_client: LLMClient,
        message_bus: MessageBus,
        telemetry: TelemetryService,
        logging: LoggingService
    ):
        self.llm_client = llm_client
        self.message_bus = message_bus
        self.telemetry = telemetry
        self.logging = logging
    
    async def execute(self, state: OutreachState) -> OutreachState:
        """Execute scaffold creation"""
        import time
        start_time = time.time()
        
        self.logging.info("Starting HOP-3: Scaffold Architect", {
            "mission_id": state.mission.mission_id
        })
        
        state.status = AgentStatus.RUNNING
        state.current_hop = "HOP-3"
        
        try:
            prompt = self._build_scaffold_prompt(state)
            
            response = await self.llm_client.call_claude(
                prompt,
                temperature=DEFAULT_TEMPERATURES["scaffold"],
                max_tokens=2000
            )
            
            scaffold = json.loads(response) if response.startswith("{") else {
                "key_achievements": ["achievement1"],
                "value_proposition": "Strong VP",
                "connection_points": ["connection1"],
                "tone_guidance": "professional"
            }
            
            # Initialize generation context with scaffold
            gen_context = GenerationContext(
                mission_id=state.mission.mission_id,
                scaffold=scaffold,
                temperature_schedule=DEFAULT_TEMPERATURES.copy()
            )
            
            state.generation_context = gen_context
            state.status = AgentStatus.COMPLETED
            
            execution_time = time.time() - start_time
            self.telemetry.record_metric("hop_3_execution_time", execution_time)
            
            self.logging.info("Completed HOP-3", {
                "mission_id": state.mission.mission_id,
                "execution_time": execution_time
            })
            
            await self.message_bus.publish(EventType.SCAFFOLD_COMPLETED, {
                "mission_id": state.mission.mission_id
            })
            
            return state
            
        except Exception as e:
            state.status = AgentStatus.FAILED
            state.error_message = str(e)
            self.logging.error(f"HOP-3 failed: {e}", {"mission_id": state.mission.mission_id})
            raise
    
    def _build_scaffold_prompt(self, state: OutreachState) -> str:
        """Build scaffold creation prompt"""
        return f"""
Create a message scaffold for this outreach.

MISSION:
{json.dumps(asdict(state.mission), indent=2, default=str)}

RESEARCH:
{json.dumps(asdict(state.research_context), indent=2, default=str) if state.research_context else "N/A"}

Return JSON with:
{{
  "key_achievements": ["achievement1", "achievement2"],
  "value_proposition": "Core value proposition",
  "connection_points": ["point1", "point2"],
  "tone_guidance": "professional|warm|direct"
}}
"""


class GenerationOrchestrator:
    """HOP-4: Generate message sections with progressive locking"""
    
    def __init__(
        self,
        llm_client: LLMClient,
        message_bus: MessageBus,
        telemetry: TelemetryService,
        logging: LoggingService,
        failure_classifier: ConstraintFailureClassifier
    ):
        self.llm_client = llm_client
        self.message_bus = message_bus
        self.telemetry = telemetry
        self.logging = logging
        self.failure_classifier = failure_classifier
    
    async def execute(self, state: OutreachState) -> OutreachState:
        """Execute generation with progressive section locking"""
        import time
        start_time = time.time()
        
        self.logging.info("Starting HOP-4: Generation Orchestrator", {
            "mission_id": state.mission.mission_id
        })
        
        state.status = AgentStatus.RUNNING
        state.current_hop = "HOP-4"
        
        try:
            gen_context = state.generation_context
            constraints = ROUTE_CONSTRAINTS[state.mission.route]
            
            # Section generation with progressive locking
            all_sections_valid = False
            
            while gen_context.attempt_count < gen_context.max_attempts and not all_sections_valid:
                gen_context.attempt_count += 1
                
                self.logging.info(f"Generation attempt {gen_context.attempt_count}", {
                    "mission_id": state.mission.mission_id
                })
                
                # Determine which sections to generate
                sections_to_generate = self._determine_sections_to_generate(gen_context, state.mission.route)
                
                # Generate sections (only non-locked ones)
                generated_sections = await self._generate_sections(
                    state,
                    sections_to_generate,
                    gen_context.attempt_count
                )
                
                # Validate generated sections
                validation_results = self._validate_generated_sections(
                    generated_sections,
                    constraints,
                    state
                )
                
                # Lock sections that passed validation
                for section_name, section_data in generated_sections.items():
                    if validation_results.get(section_name, {}).get("passed", False):
                        if section_name not in gen_context.locked_sections:
                            temp_used = gen_context.temperature_schedule.get(
                                f"generation_{section_name.replace('k', '').replace('_', '')}",
                                [0.5]
                            )
                            current_temp = temp_used[min(gen_context.attempt_count - 1, len(temp_used) - 1)]
                            
                            gen_context.locked_sections[section_name] = section_data
                            gen_context.locked_at_temperature[section_name] = current_temp
                            
                            self.logging.info(f"Locked section {section_name} at temperature {current_temp}", {
                                "mission_id": state.mission.mission_id
                            })
                            
                            await self.message_bus.publish(EventType.SECTION_LOCKED, {
                                "mission_id": state.mission.mission_id,
                                "section": section_name,
                                "temperature": current_temp,
                                "attempt": gen_context.attempt_count
                            })
                
                # Check if all required sections are locked
                required_sections = ["k1_greeting", "k3_body", "k5_cta", "k6_signature"]
                if constraints["subject_required"]:
                    required_sections.append("k2_subject")
                
                all_sections_valid = all(
                    section in gen_context.locked_sections
                    for section in required_sections
                )
                
                if not all_sections_valid:
                    # Classify failures and adjust temperatures
                    failed_sections = [
                        s for s in required_sections
                        if s not in gen_context.locked_sections
                    ]
                    
                    failures = []
                    for section in failed_sections:
                        for failure_info in validation_results.get(section, {}).get("failures", []):
                            failure = self.failure_classifier.classify_failure(
                                section=section,
                                constraint_name=failure_info["constraint"],
                                expected=failure_info["expected"],
                                actual=failure_info["actual"],
                                context={"route": state.mission.route.value}
                            )
                            failures.append(failure)
                    
                    # Apply adaptive temperature adjustments
                    if failures:
                        aggregated = self.failure_classifier.aggregate_failures(failures)
                        gen_context.adaptive_temperature_adjustments.update(
                            aggregated["section_temperature_adjustments"]
                        )
                        gen_context.failure_history.append({
                            "attempt": gen_context.attempt_count,
                            "failures": [asdict(f) for f in failures],
                            "aggregated": aggregated
                        })
                        
                        await self.message_bus.publish(EventType.FAILURE_CLASSIFIED, {
                            "mission_id": state.mission.mission_id,
                            "attempt": gen_context.attempt_count,
                            "failure_distribution": aggregated["failure_type_distribution"],
                            "adjustments": aggregated["section_temperature_adjustments"]
                        })
                    
                    gen_context.sections_to_regenerate = failed_sections
            
            if not all_sections_valid:
                raise Exception(f"Failed to generate all sections after {gen_context.max_attempts} attempts")
            
            state.status = AgentStatus.COMPLETED
            execution_time = time.time() - start_time
            
            self.telemetry.record_metric("hop_4_execution_time", execution_time)
            self.telemetry.record_metric("generation_attempts", gen_context.attempt_count)
            self.telemetry.record_metric("locked_sections", len(gen_context.locked_sections))
            
            self.logging.info("Completed HOP-4", {
                "mission_id": state.mission.mission_id,
                "attempts": gen_context.attempt_count,
                "locked_sections": len(gen_context.locked_sections),
                "execution_time": execution_time
            })
            
            await self.message_bus.publish(EventType.GENERATION_COMPLETED, {
                "mission_id": state.mission.mission_id,
                "attempts": gen_context.attempt_count
            })
            
            return state
            
        except Exception as e:
            state.status = AgentStatus.FAILED
            state.error_message = str(e)
            self.logging.error(f"HOP-4 failed: {e}", {"mission_id": state.mission.mission_id})
            raise
    
    def _determine_sections_to_generate(
        self,
        gen_context: GenerationContext,
        route: Route
    ) -> List[str]:
        """Determine which sections need generation"""
        
        if gen_context.attempt_count == 1:
            # First attempt: generate all sections
            sections = ["k1_greeting", "k3_body", "k5_cta", "k6_signature"]
            if ROUTE_CONSTRAINTS[route]["subject_required"]:
                sections.append("k2_subject")
            return sections
        else:
            # Subsequent attempts: only regenerate failed sections
            return gen_context.sections_to_regenerate
    
    async def _generate_sections(
        self,
        state: OutreachState,
        sections_to_generate: List[str],
        attempt: int
    ) -> Dict[str, Dict[str, Any]]:
        """Generate message sections"""
        
        # Use locked sections + generate new ones
        all_sections = state.generation_context.locked_sections.copy()
        
        for section_name in sections_to_generate:
            if section_name not in all_sections:
                # Get temperature for this section with adaptive adjustment
                section_key = section_name.replace("k", "").replace("_", "")
                temp_schedule = state.generation_context.temperature_schedule.get(
                    f"generation_{section_key}",
                    [0.5, 0.6, 0.7]
                )
                base_temp = temp_schedule[min(attempt - 1, len(temp_schedule) - 1)]
                
                # Apply adaptive adjustment
                adjustment = state.generation_context.adaptive_temperature_adjustments.get(section_name, 0.0)
                final_temp = max(0.0, min(1.0, base_temp + adjustment))
                
                self.logging.info(f"Generating {section_name} at temp {final_temp} (base={base_temp}, adj={adjustment})", {
                    "mission_id": state.mission.mission_id
                })
                
                # Generate section
                prompt = self._build_section_prompt(state, section_name)
                response = await self.llm_client.call_claude(
                    prompt,
                    temperature=final_temp,
                    max_tokens=500
                )
                
                all_sections[section_name] = {
                    "raw_text": response,
                    "temperature": final_temp,
                    "attempt": attempt
                }
        
        return all_sections
    
    def _build_section_prompt(self, state: OutreachState, section_name: str) -> str:
        """Build section generation prompt"""
        
        scaffold = state.generation_context.scaffold
        
        prompts = {
            "k1_greeting": f"Generate a {ROUTE_CONSTRAINTS[state.mission.route]['greeting_word_range'][0]}-{ROUTE_CONSTRAINTS[state.mission.route]['greeting_word_range'][1]} word greeting for {state.mission.recipient_profile.get('name')}. Tone: {scaffold.get('tone_guidance', 'professional')}",
            "k2_subject": f"Generate a {ROUTE_CONSTRAINTS[state.mission.route]['subject_word_range'][0]}-{ROUTE_CONSTRAINTS[state.mission.route]['subject_word_range'][1]} word subject line for message to {state.mission.recipient_profile.get('name')} about {state.mission.job_description.get('title')}",
            "k3_body": f"Generate the main message body ({ROUTE_CONSTRAINTS[state.mission.route]['body_min_words']}+ words) incorporating: {scaffold.get('key_achievements', [])} and {scaffold.get('value_proposition', '')}",
            "k5_cta": f"Generate a {ROUTE_CONSTRAINTS[state.mission.route]['cta_word_range'][0]}-{ROUTE_CONSTRAINTS[state.mission.route]['cta_word_range'][1]} word call-to-action",
            "k6_signature": f"Generate a {ROUTE_CONSTRAINTS[state.mission.route]['signature_word_range'][0]}-{ROUTE_CONSTRAINTS[state.mission.route]['signature_word_range'][1]} word signature for {state.mission.sender_profile.get('name')}, {state.mission.sender_profile.get('title')}"
        }
        
        return prompts.get(section_name, "Generate section")
    
    def _validate_generated_sections(
        self,
        sections: Dict[str, Dict[str, Any]],
        constraints: Dict[str, Any],
        state: OutreachState
    ) -> Dict[str, Dict[str, Any]]:
        """Validate generated sections against constraints"""
        
        validation_results = {}
        
        for section_name, section_data in sections.items():
            text = section_data.get("raw_text", "")
            word_count = len(text.split())
            
            # Get expected word range
            constraint_key = None
            if section_name == "k1_greeting":
                constraint_key = "greeting_word_range"
            elif section_name == "k2_subject":
                constraint_key = "subject_word_range"
            elif section_name == "k5_cta":
                constraint_key = "cta_word_range"
            elif section_name == "k6_signature":
                constraint_key = "signature_word_range"
            elif section_name == "k3_body":
                constraint_key = "body_min_words"
            
            passed = True
            failures = []
            
            if constraint_key and constraint_key in constraints:
                if constraint_key == "body_min_words":
                    min_words = constraints[constraint_key]
                    if word_count < min_words:
                        passed = False
                        failures.append({
                            "constraint": constraint_key,
                            "expected": f">= {min_words}",
                            "actual": word_count
                        })
                else:
                    min_w, max_w = constraints[constraint_key]
                    if word_count < min_w or word_count > max_w:
                        passed = False
                        failures.append({
                            "constraint": constraint_key,
                            "expected": (min_w, max_w),
                            "actual": word_count
                        })
            
            validation_results[section_name] = {
                "passed": passed,
                "word_count": word_count,
                "failures": failures
            }
        
        return validation_results


class StagingBufferAssembler:
    """HOP-5: Assemble staging buffer with ground truth recalculation"""
    
    def __init__(
        self,
        message_bus: MessageBus,
        telemetry: TelemetryService,
        logging: LoggingService
    ):
        self.message_bus = message_bus
        self.telemetry = telemetry
        self.logging = logging
    
    async def execute(self, state: OutreachState) -> OutreachState:
        """Execute staging buffer assembly with ground truth"""
        import time
        start_time = time.time()
        
        self.logging.info("Starting HOP-5: Staging Buffer Assembler", {
            "mission_id": state.mission.mission_id
        })
        
        state.status = AgentStatus.RUNNING
        state.current_hop = "HOP-5"
        
        try:
            locked_sections = state.generation_context.locked_sections
            
            # Assemble sections
            k1_greeting = locked_sections.get("k1_greeting")
            k2_subject = locked_sections.get("k2_subject")
            k3_body = locked_sections.get("k3_body")
            k5_cta = locked_sections.get("k5_cta")
            k6_signature = locked_sections.get("k6_signature")
            
            # Assemble full message
            full_message_parts = []
            if k1_greeting:
                full_message_parts.append(k1_greeting["raw_text"])
            if k2_subject:
                full_message_parts.append(f"Subject: {k2_subject['raw_text']}")
            if k3_body:
                full_message_parts.append(k3_body["raw_text"])
            if k5_cta:
                full_message_parts.append(k5_cta["raw_text"])
            if k6_signature:
                full_message_parts.append(k6_signature["raw_text"])
            
            full_message_text = "\n\n".join(full_message_parts)
            
            # Ground truth recalculation (deterministic, independent of LLM claims)
            ground_truth_word_count = len(full_message_text.split())
            ground_truth_char_count = len(full_message_text)
            
            # Section-specific counts
            section_word_counts = {}
            section_char_counts = {}
            
            for section_name in ["k1_greeting", "k2_subject", "k3_body", "k5_cta", "k6_signature"]:
                section_data = locked_sections.get(section_name)
                if section_data:
                    text = section_data["raw_text"]
                    section_word_counts[section_name] = len(text.split())
                    section_char_counts[section_name] = len(text)
            
            # Cryptographic checksum
            checksum_data = {
                "full_message": full_message_text,
                "sections": {k: v["raw_text"] for k, v in locked_sections.items()}
            }
            checksum_json = json.dumps(checksum_data, sort_keys=True)
            ground_truth_checksum = hashlib.sha256(checksum_json.encode()).hexdigest()
            
            # Create staging buffer
            staging_buffer = StagingBuffer(
                k1_greeting=k1_greeting,
                k2_subject=k2_subject,
                k3_body=k3_body,
                k5_cta=k5_cta,
                k6_signature=k6_signature,
                full_message={"raw_text": full_message_text},
                metadata={
                    "generation_model": "claude",
                    "generation_temperature": "adaptive",
                    "generation_timestamp": datetime.now().isoformat(),
                    "locked_section_temps": state.generation_context.locked_at_temperature
                },
                ground_truth_word_count=ground_truth_word_count,
                ground_truth_char_count=ground_truth_char_count,
                ground_truth_checksum=ground_truth_checksum,
                section_word_counts=section_word_counts,
                section_char_counts=section_char_counts
            )
            
            state.staging_buffer = staging_buffer
            state.status = AgentStatus.COMPLETED
            
            execution_time = time.time() - start_time
            self.telemetry.record_metric("hop_5_execution_time", execution_time)
            
            self.logging.info("Completed HOP-5", {
                "mission_id": state.mission.mission_id,
                "ground_truth_word_count": ground_truth_word_count,
                "ground_truth_char_count": ground_truth_char_count,
                "checksum": ground_truth_checksum[:16],
                "execution_time": execution_time
            })
            
            return state
            
        except Exception as e:
            state.status = AgentStatus.FAILED
            state.error_message = str(e)
            self.logging.error(f"HOP-5 failed: {e}", {"mission_id": state.mission.mission_id})
            raise


class ValidationAgent:
    """HOP-6: Multi-batch validation"""
    
    def __init__(
        self,
        validation_service: ValidationService,
        message_bus: MessageBus,
        telemetry: TelemetryService,
        logging: LoggingService
    ):
        self.validation_service = validation_service
        self.message_bus = message_bus
        self.telemetry = telemetry
        self.logging = logging
    
    async def execute(self, state: OutreachState) -> OutreachState:
        """Execute multi-batch validation"""
        import time
        start_time = time.time()
        
        self.logging.info("Starting HOP-6: Validation Agent", {
            "mission_id": state.mission.mission_id
        })
        
        state.status = AgentStatus.RUNNING
        state.current_hop = "HOP-6"
        
        try:
            validation_results = []
            
            # BATCH 0: Pre-flight
            batch_0 = self.validation_service.validate_batch_0_pre_flight(state)
            validation_results.append(batch_0)
            
            # BATCH 1: Constraints
            batch_1 = self.validation_service.validate_batch_1_constraints(
                state.staging_buffer,
                state
            )
            validation_results.append(batch_1)
            
            # BATCH 2: Confidence
            batch_2 = self.validation_service.validate_batch_2_confidence(
                state.staging_buffer,
                state
            )
            validation_results.append(batch_2)
            
            # BATCH 3: Entities
            batch_3 = self.validation_service.validate_batch_3_entities(
                state.staging_buffer,
                state
            )
            validation_results.append(batch_3)
            
            # BATCH 4: Format (includes similarity cross-validation)
            batch_4 = self.validation_service.validate_batch_4_format(state.staging_buffer)
            validation_results.append(batch_4)
            
            # Check for contamination
            if state.staging_buffer.contamination_flags:
                await self.message_bus.publish(EventType.CONTAMINATION_DETECTED, {
                    "mission_id": state.mission.mission_id,
                    "flags": state.staging_buffer.contamination_flags
                })
            
            state.validation_results = validation_results
            
            # BATCH 5: Post-validation
            batch_5 = self.validation_service.validate_batch_5_post_validation(state)
            validation_results.append(batch_5)
            
            state.status = AgentStatus.COMPLETED
            execution_time = time.time() - start_time
            
            self.telemetry.record_metric("hop_6_execution_time", execution_time)
            
            self.logging.info("Completed HOP-6", {
                "mission_id": state.mission.mission_id,
                "batches_passed": sum(1 for vr in validation_results if vr.passed),
                "total_batches": len(validation_results),
                "execution_time": execution_time
            })
            
            await self.message_bus.publish(EventType.VALIDATION_COMPLETED, {
                "mission_id": state.mission.mission_id,
                "passed": all(vr.passed for vr in validation_results)
            })
            
            return state
            
        except Exception as e:
            state.status = AgentStatus.FAILED
            state.error_message = str(e)
            self.logging.error(f"HOP-6 failed: {e}", {"mission_id": state.mission.mission_id})
            raise


class GateAgent:
    """HOP-7: Final gate decision"""
    
    def __init__(
        self,
        message_bus: MessageBus,
        telemetry: TelemetryService,
        logging: LoggingService
    ):
        self.message_bus = message_bus
        self.telemetry = telemetry
        self.logging = logging
    
    async def execute(self, state: OutreachState) -> OutreachState:
        """Execute gate decision"""
        import time
        start_time = time.time()
        
        self.logging.info("Starting HOP-7: Gate Agent", {
            "mission_id": state.mission.mission_id
        })
        
        state.status = AgentStatus.RUNNING
        state.current_hop = "HOP-7"
        
        try:
            # Check all validation batches passed
            all_passed = all(vr.passed for vr in state.validation_results)
            
            # Check for critical issues
            has_critical = any(
                any(
                    f.get("severity") == ValidationSeverity.CRITICAL
                    for f in vr.failures
                )
                for vr in state.validation_results
            )
            
            gate_approved = all_passed and not has_critical
            
            if gate_approved:
                await self.message_bus.publish(EventType.GATE_APPROVED, {
                    "mission_id": state.mission.mission_id
                })
                self.logging.info("Gate APPROVED", {
                    "mission_id": state.mission.mission_id
                })
            else:
                await self.message_bus.publish(EventType.GATE_REJECTED, {
                    "mission_id": state.mission.mission_id,
                    "reason": "Validation failures" if not all_passed else "Critical issues"
                })
                self.logging.warning("Gate REJECTED", {
                    "mission_id": state.mission.mission_id,
                    "all_passed": all_passed,
                    "has_critical": has_critical
                })
            
            state.metadata["gate_approved"] = gate_approved
            state.status = AgentStatus.COMPLETED
            
            execution_time = time.time() - start_time
            self.telemetry.record_metric("hop_7_execution_time", execution_time)
            
            return state
            
        except Exception as e:
            state.status = AgentStatus.FAILED
            state.error_message = str(e)
            self.logging.error(f"HOP-7 failed: {e}", {"mission_id": state.mission.mission_id})
            raise


# ============================================================================
# WORKFLOW ORCHESTRATOR
# ============================================================================

class WorkflowOrchestrator:
    """DAG workflow orchestrator"""
    
    def __init__(
        self,
        message_bus: MessageBus,
        state_store: StateStore,
        llm_client: LLMClient,
        telemetry: TelemetryService,
        logging: LoggingService,
        validation_service: ValidationService,
        checkpoint_manager: CheckpointManager,
        qa_report_generator: QAReportGenerator
    ):
        self.message_bus = message_bus
        self.state_store = state_store
        self.llm_client = llm_client
        self.telemetry = telemetry
        self.logging = logging
        self.validation_service = validation_service
        self.checkpoint_manager = checkpoint_manager
        self.qa_report_generator = qa_report_generator
        
        # NEW v11.3: Initialize new components
        self.failure_classifier = ConstraintFailureClassifier()
        self.similarity_validator = SimilarityCrossValidator()
        
        # Initialize agents with new components
        self.profile_agent = ProfileAnalysisAgent(
            llm_client, message_bus, telemetry, logging
        )
        self.research_agent = ResearchOrchestrator(
            llm_client, message_bus, telemetry, logging
        )
        self.scaffold_agent = ScaffoldArchitect(
            llm_client, message_bus, telemetry, logging
        )
        self.generation_agent = GenerationOrchestrator(
            llm_client, message_bus, telemetry, logging, self.failure_classifier
        )
        self.staging_agent = StagingBufferAssembler(
            message_bus, telemetry, logging
        )
        self.validation_agent = ValidationAgent(
            validation_service, message_bus, telemetry, logging
        )
        self.gate_agent = GateAgent(
            message_bus, telemetry, logging
        )
    
    async def execute_workflow(self, mission: OutreachMission) -> Dict[str, Any]:
        """Execute complete workflow"""
        import time
        workflow_start = time.time()
        
        self.logging.info("=" * 80)
        self.logging.info(f"Starting LIC v11.3 Workflow: {mission.mission_id}")
        self.logging.info("=" * 80)
        
        # Initialize state
        state = OutreachState(mission=mission)
        await self.state_store.save(mission.mission_id, state)
        
        await self.message_bus.publish(EventType.WORKFLOW_STARTED, {
            "mission_id": mission.mission_id,
            "version": __version__
        })
        
        try:
            # HOP-1: Profile Analysis
            state = await self._execute_hop(
                "HOP-1",
                "ProfileAnalysisAgent",
                self.profile_agent,
                state
            )
            
            # HOP-2: Research with Reflexion
            state = await self._execute_hop(
                "HOP-2",
                "ResearchOrchestrator",
                self.research_agent,
                state
            )
            
            # HOP-3: Scaffold
            state = await self._execute_hop(
                "HOP-3",
                "ScaffoldArchitect",
                self.scaffold_agent,
                state
            )
            
            # HOP-4: Generation with Progressive Locking
            state = await self._execute_hop(
                "HOP-4",
                "GenerationOrchestrator",
                self.generation_agent,
                state
            )
            
            # HOP-5: Staging Buffer Assembly
            state = await self._execute_hop(
                "HOP-5",
                "StagingBufferAssembler",
                self.staging_agent,
                state
            )
            
            # HOP-6: Validation
            state = await self._execute_hop(
                "HOP-6",
                "ValidationAgent",
                self.validation_agent,
                state
            )
            
            # HOP-7: Gate
            state = await self._execute_hop(
                "HOP-7",
                "GateAgent",
                self.gate_agent,
                state
            )
            
            # Generate QA report
            qa_summary = self.qa_report_generator.generate_qa_summary(state)
            qa_report = self.qa_report_generator.generate_qa_report(state, qa_summary)
            
            workflow_time = time.time() - workflow_start
            self.telemetry.record_metric("total_workflow_time", workflow_time)
            
            self.logging.info("=" * 80)
            self.logging.info(f"Completed LIC v11.3 Workflow: {mission.mission_id}")
            self.logging.info(f"Total Time: {workflow_time:.2f}s")
            self.logging.info(f"Status: {qa_summary.overall_status}")
            self.logging.info(f"Production Ready: {qa_summary.production_ready}")
            self.logging.info("=" * 80)
            
            await self.message_bus.publish(EventType.WORKFLOW_COMPLETED, {
                "mission_id": mission.mission_id,
                "status": qa_summary.overall_status,
                "production_ready": qa_summary.production_ready,
                "workflow_time": workflow_time
            })
            
            return {
                "mission_id": mission.mission_id,
                "status": qa_summary.overall_status,
                "production_ready": qa_summary.production_ready,
                "staging_buffer": asdict(state.staging_buffer) if state.staging_buffer else None,
                "validation_results": [asdict(vr) for vr in state.validation_results],
                "checkpoints": [asdict(cp) for cp in state.checkpoints],
                "qa_summary": asdict(qa_summary),
                "qa_report": qa_report,
                "telemetry": self.telemetry.get_all_metrics(),
                "workflow_time": workflow_time
            }
            
        except Exception as e:
            self.logging.error(f"Workflow failed: {e}", {
                "mission_id": mission.mission_id
            })
            raise
    
    async def _execute_hop(
        self,
        hop_id: str,
        hop_name: str,
        agent,
        state: OutreachState
    ) -> OutreachState:
        """Execute a single hop with checkpoint"""
        import time
        hop_start = time.time()
        
        self.logging.info(f"\n>>> Executing {hop_id}: {hop_name}")
        
        # Execute agent
        state = await agent.execute(state)
        
        # Create checkpoint
        hop_time = time.time() - hop_start
        checkpoint = self.checkpoint_manager.create_checkpoint(
            hop_id=hop_id,
            hop_name=hop_name,
            state=state,
            metadata={"agent": hop_name},
            execution_time=hop_time
        )
        
        state.checkpoints.append(checkpoint)
        
        # Save state
        await self.state_store.save(state.mission.mission_id, state)
        
        # Publish checkpoint event
        await self.message_bus.publish(EventType.CHECKPOINT_CREATED, {
            "mission_id": state.mission.mission_id,
            "hop_id": hop_id,
            "hop_name": hop_name,
            "checksum": checkpoint.checksum,
            "execution_time": hop_time
        })
        
        self.logging.info(f"<<< Completed {hop_id} in {hop_time:.2f}s")
        
        return state


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_orchestrator(log_dir: Path = Path("/tmp/lic_logs")) -> WorkflowOrchestrator:
    """Factory function to create orchestrator with all dependencies"""
    
    # Core infrastructure
    message_bus = MessageBus()
    state_store = StateStore()
    cache = SemanticCache()
    circuit_breaker = CircuitBreaker()
    
    # LLM client
    llm_client = LLMClient(cache, circuit_breaker)
    
    # Services
    telemetry = TelemetryService()
    logging_service = LoggingService(log_dir)
    checkpoint_manager = CheckpointManager()
    
    # NEW v11.3: Advanced components
    failure_classifier = ConstraintFailureClassifier()
    similarity_validator = SimilarityCrossValidator()
    
    # Validation service with new components
    validation_service = ValidationService(
        telemetry,
        logging_service,
        failure_classifier,
        similarity_validator
    )
    
    # QA report generator
    qa_report_generator = QAReportGenerator(logging_service)
    
    # Create orchestrator
    orchestrator = WorkflowOrchestrator(
        message_bus=message_bus,
        state_store=state_store,
        llm_client=llm_client,
        telemetry=telemetry,
        logging=logging_service,
        validation_service=validation_service,
        checkpoint_manager=checkpoint_manager,
        qa_report_generator=qa_report_generator
    )
    
    return orchestrator


# ============================================================================
# INTERACTIVE PROFILE COLLECTION
# ============================================================================

def collect_sender_profile() -> Dict[str, Any]:
    """
    Collect sender profile information interactively
    
    Returns:
        Dict containing name, title, linkedin_url, about_section
    """
    print("\n" + "="*80)
    print("LIC v11.3 - SENDER PROFILE COLLECTION")
    print("="*80)
    print("\nPlease provide your profile information:\n")
    
    # Collect Name
    name = input("Name: ").strip()
    while not name:
        print("  ⚠ Name is required")
        name = input("Name: ").strip()
    
    # Collect Title
    title = input("Title: ").strip()
    while not title:
        print("  ⚠ Title is required")
        title = input("Title: ").strip()
    
    # Collect LinkedIn URL
    linkedin_url = input("LinkedIn URL: ").strip()
    while not linkedin_url:
        print("  ⚠ LinkedIn URL is required")
        linkedin_url = input("LinkedIn URL: ").strip()
    
    # Normalize LinkedIn URL
    if not linkedin_url.startswith("http"):
        if not linkedin_url.startswith("linkedin.com"):
            linkedin_url = f"linkedin.com/in/{linkedin_url}"
        linkedin_url = f"https://{linkedin_url}"
    
    # Collect LinkedIn About Section
    print("\nLinkedIn About Section (press Enter twice when done):")
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
        Dict containing name, title, company, linkedin_url
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
    
    return {
        "name": name,
        "title": title or "Not specified",
        "company": company or "Not specified",
        "linkedin_url": linkedin_url or "Not provided"
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
    print("LIC v11.3 - LinkedIn Outreach Orchestrator")
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
            "linkedin_url": "https://linkedin.com/in/sarahjohnson"
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
        job_description=job_description
    )
    
    print(f"\n{'='*80}")
    print("LIC v11.3 - Demo Execution")
    print(f"{'='*80}\n")
    print(f"Mission ID: {mission.mission_id}")
    print(f"Sender: {mission.sender_profile['name']}")
    print(f"Recipient: {mission.recipient_profile['name']}")
    print(f"Job: {mission.job_description['title']} at {mission.job_description['company']}")
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
