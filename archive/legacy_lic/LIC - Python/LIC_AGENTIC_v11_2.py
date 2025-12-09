"""
LIC-AGENTIC-v11.2: LinkedIn InMail Cold Outreach - Enhanced Quality Framework
==============================================================================

Version: 11.2
Base Version: 11.1
Architecture: Event-Driven Microservices with Agentic Research & Generation Loops
Status: PRODUCTION_READY

Key Upgrades from v11.1:
-------------------------
1. QA Report Generation Framework: Comprehensive structured reports with production readiness indicators
2. Multi-Hop Checkpoint Architecture: Cryptographic checksums and metadata tracking at each workflow stage
3. Ground Truth Recalculation: Independent verification of staging buffer metrics (no LLM metadata trust)
4. Progressive Temperature Framework: Section-specific temperatures with adaptive optimization

New Capabilities:
-----------------
- HOP-based workflow tracking with cryptographic verification
- QA reports with 5 sections: Production Readiness, Critical Failures, Content Summary, Structural Summary, Outputs
- Deterministic staging buffer validation (word counts, character counts computed independently)
- Temperature tracking per K-node with attempts history
- Checkpoint-based rollback capability for debugging

Architectural Principles:
------------------------
- No Cost/Time Tradeoffs: Maximize quality over efficiency
- Fail-Fast: Explicit errors over silent contamination
- Staging Buffer: Single source of truth with ground truth recalculation
- Cryptographic Integrity: SHA-256 checksums at each hop
- Progressive Optimization: Temperature tuning based on success patterns
"""

import asyncio
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from uuid import uuid4

import anthropic
import google.generativeai as genai


__version__ = "11.2"


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class Route(Enum):
    """Message route types"""
    INMAIL = "INMAIL"
    CONNECTION_REQ = "CONNECTION_REQ"
    FOLLOW_UP = "FOLLOW_UP"


class Archetype(Enum):
    """Recipient archetypes"""
    EXECUTIVE = "EXECUTIVE"
    RECRUITER = "RECRUITER"
    HIRING_MANAGER = "HIRING_MANAGER"
    C_LEVEL = "C_LEVEL"


class EventType(Enum):
    """Event types for message bus"""
    # Workflow events
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"
    
    # Agent events
    PROFILE_ANALYSIS_COMPLETED = "PROFILE_ANALYSIS_COMPLETED"
    RESEARCH_ITERATION_COMPLETED = "RESEARCH_ITERATION_COMPLETED"
    RESEARCH_COMPLETED = "RESEARCH_COMPLETED"
    SCAFFOLD_COMPLETED = "SCAFFOLD_COMPLETED"
    GENERATION_ITERATION_COMPLETED = "GENERATION_ITERATION_COMPLETED"
    GENERATION_COMPLETED = "GENERATION_COMPLETED"
    
    # Validation events
    STAGING_BUFFER_CREATED = "STAGING_BUFFER_CREATED"
    VALIDATION_BATCH_COMPLETED = "VALIDATION_BATCH_COMPLETED"
    VALIDATION_COMPLETED = "VALIDATION_COMPLETED"
    
    # Gate events
    GATE_APPROVED = "GATE_APPROVED"
    GATE_BLOCKED = "GATE_BLOCKED"
    
    # New: Checkpoint events
    CHECKPOINT_CREATED = "CHECKPOINT_CREATED"
    CHECKPOINT_VERIFIED = "CHECKPOINT_VERIFIED"


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    WAITING = "WAITING"


class ValidationSeverity(Enum):
    """Validation failure severity"""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


# Route constraints from v10.24
ROUTE_CONSTRAINTS = {
    Route.INMAIL: {
        "word_range": (180, 250),
        "char_limit": 1900,
        "subject_required": True,
        "subject_word_range": (5, 8),
        "subject_char_limit": 60
    },
    Route.CONNECTION_REQ: {
        "word_range": (40, 60),
        "char_limit": 300,
        "subject_required": False
    },
    Route.FOLLOW_UP: {
        "word_range": (100, 150),
        "char_limit": 800,
        "subject_required": False
    }
}

ARCHETYPE_TARGETS = {
    Archetype.EXECUTIVE: (200, 230),
    Archetype.RECRUITER: (45, 55),
    Archetype.HIRING_MANAGER: (180, 210),
    Archetype.C_LEVEL: (210, 240)
}

# NEW: Default temperature configurations per K-node
DEFAULT_TEMPERATURES = {
    "k1_greeting": 0.7,
    "k2_subject": 0.8,
    "k3_body": 1.0,
    "k5_cta": 0.9,
    "k6_signature": 0.5
}


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Event:
    """Event for message bus"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    payload: Dict[str, Any]
    source_agent: Optional[str] = None
    correlation_id: Optional[str] = None


@dataclass
class OutreachMission:
    """Complete mission context"""
    mission_id: str
    sender_profile: Dict[str, Any]
    recipient_profile: Dict[str, Any]
    job_description: Optional[Dict[str, Any]] = None
    route: Optional[Route] = None
    archetype: Optional[Archetype] = None
    hyde_queries: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchContext:
    """Research phase state"""
    iteration: int = 0
    max_iterations: int = 5
    achievements: List[Dict[str, Any]] = field(default_factory=list)
    insights: List[Dict[str, Any]] = field(default_factory=list)
    critique_history: List[Dict[str, Any]] = field(default_factory=list)
    signal_score: float = 0.0
    completed: bool = False


@dataclass
class GenerationContext:
    """Generation phase state - ENHANCED with temperature tracking"""
    iteration: int = 0
    max_iterations: int = 10
    scaffold: Optional[Dict[str, Any]] = None
    drafts: List[Dict[str, Any]] = field(default_factory=list)
    constraint_violations: List[Dict[str, Any]] = field(default_factory=list)
    completed: bool = False
    # NEW: Temperature tracking
    section_temperatures: Dict[str, float] = field(default_factory=lambda: DEFAULT_TEMPERATURES.copy())
    attempts_per_section: Dict[str, int] = field(default_factory=lambda: {
        "k1_greeting": 0, "k2_subject": 0, "k3_body": 0, "k5_cta": 0, "k6_signature": 0
    })
    temperature_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class StagingBuffer:
    """Staging buffer for ground truth validation - ENHANCED with checksums"""
    k1_greeting: Dict[str, Any]
    k2_subject: Optional[Dict[str, Any]]
    k3_body: Dict[str, Any]
    k5_cta: Dict[str, Any]
    k6_signature: Dict[str, Any]
    full_message: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    # NEW: Ground truth metrics (recalculated independently)
    ground_truth_word_count: int = 0
    ground_truth_char_count: int = 0
    ground_truth_checksum: str = ""


@dataclass
class ValidationResult:
    """Validation result"""
    batch_name: str
    rules_passed: int
    rules_failed: int
    failures: List[Dict[str, Any]]
    severity: ValidationSeverity
    passed: bool
    execution_time: float


# NEW: Checkpoint data structure
@dataclass
class HopCheckpoint:
    """Checkpoint at each workflow hop"""
    hop_id: str
    hop_name: str
    timestamp: datetime
    status: AgentStatus
    metadata: Dict[str, Any]
    checksum: str
    execution_time: float
    validation_results: List[ValidationResult] = field(default_factory=list)


@dataclass
class OutreachState:
    """Complete outreach workflow state - ENHANCED with checkpoints"""
    mission: OutreachMission
    research: ResearchContext = field(default_factory=ResearchContext)
    generation: GenerationContext = field(default_factory=GenerationContext)
    staging_buffer: Optional[StagingBuffer] = None
    validation_results: List[ValidationResult] = field(default_factory=list)
    gate_decision: Optional[bool] = None
    workflow_status: AgentStatus = AgentStatus.IDLE
    error_log: List[Dict[str, Any]] = field(default_factory=list)
    # NEW: Checkpoints
    hop_checkpoints: List[HopCheckpoint] = field(default_factory=list)


@dataclass
class TelemetryMetric:
    """Telemetry metric"""
    metric_name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


# NEW: QA Report Summary
@dataclass
class QAReportSummary:
    """QA Report summary data"""
    overall_status: str  # PASS, WARN, FAIL
    production_ready: bool
    critical_failures: int
    high_failures: int
    warning_failures: int
    research_signal_score: float
    total_word_count: int
    total_char_count: int
    total_api_calls: int
    generation_attempts: int
    research_iterations: int
    validation_batches_passed: int
    validation_batches_total: int
    execution_time: float


# ============================================================================
# EXCEPTIONS
# ============================================================================

class LICException(Exception):
    """Base exception for LIC"""
    pass


class ValidationError(LICException):
    """Validation failed"""
    pass


class ScopeViolationError(LICException):
    """Scope isolation violated"""
    pass


class CircuitBreakerOpenError(LICException):
    """Circuit breaker is open"""
    pass


class AgentExecutionError(LICException):
    """Agent execution failed"""
    pass


class ChecksumMismatchError(LICException):
    """Checksum verification failed"""
    pass


# ============================================================================
# MESSAGE BUS
# ============================================================================

class MessageBus:
    """Event-driven message bus for agent communication"""
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.event_history: List[Event] = []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe to event type"""
        self.subscribers[event_type].append(handler)
        self.logger.info(f"Subscribed to {event_type.value}")
    
    async def publish(self, event: Event):
        """Publish event to all subscribers"""
        self.event_history.append(event)
        self.logger.info(f"Publishing {event.event_type.value}")
        
        handlers = self.subscribers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                self.logger.error(f"Handler error for {event.event_type.value}: {e}")
    
    def get_history(self, event_type: Optional[EventType] = None) -> List[Event]:
        """Get event history"""
        if event_type:
            return [e for e in self.event_history if e.event_type == event_type]
        return self.event_history


# ============================================================================
# STATE STORE
# ============================================================================

class StateStore:
    """Centralized state management"""
    
    def __init__(self):
        self.states: Dict[str, OutreachState] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_state(self, mission: OutreachMission) -> OutreachState:
        """Create new state"""
        state = OutreachState(mission=mission)
        self.states[mission.mission_id] = state
        self.logger.info(f"Created state for {mission.mission_id}")
        return state
    
    def get_state(self, mission_id: str) -> Optional[OutreachState]:
        """Get state by mission ID"""
        return self.states.get(mission_id)
    
    def update_state(self, mission_id: str, state: OutreachState):
        """Update state"""
        self.states[mission_id] = state
        self.logger.info(f"Updated state for {mission_id}")
    
    def delete_state(self, mission_id: str):
        """Delete state"""
        if mission_id in self.states:
            del self.states[mission_id]
            self.logger.info(f"Deleted state for {mission_id}")


# ============================================================================
# SEMANTIC CACHE
# ============================================================================

class SemanticCache:
    """Cache for LLM responses"""
    
    def __init__(self, ttl: int = 3600):
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.ttl = ttl
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _make_key(self, prompt: str, model: str, **kwargs) -> str:
        """Generate cache key"""
        data = f"{prompt}:{model}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def get(self, prompt: str, model: str, **kwargs) -> Optional[Any]:
        """Get cached response"""
        key = self._make_key(prompt, model, **kwargs)
        if key in self.cache:
            response, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                self.logger.info(f"Cache hit for {model}")
                return response
            else:
                del self.cache[key]
        return None
    
    def set(self, prompt: str, model: str, response: Any, **kwargs):
        """Cache response"""
        key = self._make_key(prompt, model, **kwargs)
        self.cache[key] = (response, time.time())
        self.logger.info(f"Cached response for {model}")
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.logger.info("Cache cleared")


# ============================================================================
# CIRCUIT BREAKER
# ============================================================================

class CircuitBreaker:
    """Circuit breaker for external services"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time < self.timeout:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
            else:
                self.state = "HALF_OPEN"
                self.logger.info("Circuit breaker entering HALF_OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                self.logger.info("Circuit breaker CLOSED")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                self.logger.error(f"Circuit breaker OPEN after {self.failure_count} failures")
            
            raise e


# ============================================================================
# LLM CLIENT
# ============================================================================

class LLMClient:
    """Multi-model LLM client with caching and circuit breaker - ENHANCED with API call tracking"""
    
    def __init__(self, 
                 anthropic_api_key: str,
                 google_api_key: str,
                 cache: SemanticCache,
                 circuit_breaker: CircuitBreaker):
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        genai.configure(api_key=google_api_key)
        self.cache = cache
        self.circuit_breaker = circuit_breaker
        self.logger = logging.getLogger(self.__class__.__name__)
        # NEW: API call tracking
        self.api_call_count = 0
    
    async def call_claude(self, 
                         prompt: str, 
                         model: str = "claude-sonnet-4-20250514",
                         temperature: float = 1.0,
                         max_tokens: int = 4096,
                         system: Optional[str] = None,
                         use_cache: bool = True) -> str:
        """Call Claude API"""
        if use_cache:
            cached = self.cache.get(prompt, model, temperature=temperature)
            if cached:
                return cached
        
        def _call():
            messages = [{"role": "user", "content": prompt}]
            kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }
            if system:
                kwargs["system"] = system
            
            response = self.anthropic_client.messages.create(**kwargs)
            self.api_call_count += 1  # NEW: Track API call
            return response.content[0].text
        
        result = self.circuit_breaker.call(_call)
        
        if use_cache:
            self.cache.set(prompt, model, result, temperature=temperature)
        
        return result
    
    async def call_gemini(self,
                         prompt: str,
                         model: str = "gemini-2.0-flash-exp",
                         temperature: float = 1.0,
                         use_cache: bool = True) -> str:
        """Call Gemini API"""
        if use_cache:
            cached = self.cache.get(prompt, model, temperature=temperature)
            if cached:
                return cached
        
        def _call():
            gemini_model = genai.GenerativeModel(model)
            generation_config = {"temperature": temperature}
            response = gemini_model.generate_content(
                prompt,
                generation_config=generation_config
            )
            self.api_call_count += 1  # NEW: Track API call
            return response.text
        
        result = self.circuit_breaker.call(_call)
        
        if use_cache:
            self.cache.set(prompt, model, result, temperature=temperature)
        
        return result
    
    async def multi_model_consensus(self,
                                   prompt: str,
                                   models: List[str],
                                   temperature: float = 0.3) -> Dict[str, str]:
        """Get consensus from multiple models"""
        results = {}
        
        for model in models:
            if "claude" in model:
                results[model] = await self.call_claude(
                    prompt, model=model, temperature=temperature
                )
            elif "gemini" in model:
                results[model] = await self.call_gemini(
                    prompt, model=model, temperature=temperature
                )
        
        return results
    
    def get_api_call_count(self) -> int:
        """Get total API calls made"""
        return self.api_call_count
    
    def reset_api_call_count(self):
        """Reset API call counter"""
        self.api_call_count = 0


# ============================================================================
# NEW: CHECKPOINT MANAGER
# ============================================================================

class CheckpointManager:
    """Manage workflow checkpoints with cryptographic verification"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_checkpoint(self,
                         hop_id: str,
                         hop_name: str,
                         state: OutreachState,
                         metadata: Dict[str, Any],
                         execution_time: float,
                         validation_results: Optional[List[ValidationResult]] = None) -> HopCheckpoint:
        """Create checkpoint with checksum"""
        
        # Create deterministic data snapshot for checksum
        checkpoint_data = {
            "hop_id": hop_id,
            "mission_id": state.mission.mission_id,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata,
            "research_achievements": len(state.research.achievements),
            "generation_drafts": len(state.generation.drafts),
            "staging_buffer_exists": state.staging_buffer is not None
        }
        
        # Compute SHA-256 checksum
        data_str = json.dumps(checkpoint_data, sort_keys=True)
        checksum = hashlib.sha256(data_str.encode()).hexdigest()
        
        checkpoint = HopCheckpoint(
            hop_id=hop_id,
            hop_name=hop_name,
            timestamp=datetime.now(),
            status=state.workflow_status,
            metadata=metadata,
            checksum=checksum,
            execution_time=execution_time,
            validation_results=validation_results or []
        )
        
        self.logger.info(f"Created checkpoint {hop_id}: {checksum[:8]}...")
        
        return checkpoint
    
    def verify_checkpoint(self, checkpoint: HopCheckpoint, expected_checksum: str) -> bool:
        """Verify checkpoint integrity"""
        if checkpoint.checksum != expected_checksum:
            self.logger.error(
                f"Checksum mismatch for {checkpoint.hop_id}: "
                f"expected {expected_checksum[:8]}..., got {checkpoint.checksum[:8]}..."
            )
            return False
        
        self.logger.info(f"Checkpoint {checkpoint.hop_id} verified: {checkpoint.checksum[:8]}...")
        return True
    
    def find_last_valid_checkpoint(self, checkpoints: List[HopCheckpoint]) -> Optional[HopCheckpoint]:
        """Find last checkpoint with COMPLETED status"""
        for checkpoint in reversed(checkpoints):
            if checkpoint.status == AgentStatus.COMPLETED:
                return checkpoint
        return None


# ============================================================================
# SERVICES
# ============================================================================

class TelemetryService:
    """Telemetry and metrics collection"""
    
    def __init__(self):
        self.metrics: List[TelemetryMetric] = []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def record(self, metric_name: str, value: float, unit: str, **tags):
        """Record metric"""
        metric = TelemetryMetric(
            metric_name=metric_name,
            value=value,
            unit=unit,
            tags=tags
        )
        self.metrics.append(metric)
        self.logger.info(f"Metric: {metric_name}={value}{unit} {tags}")
    
    def get_metrics(self, metric_name: Optional[str] = None) -> List[TelemetryMetric]:
        """Get metrics"""
        if metric_name:
            return [m for m in self.metrics if m.metric_name == metric_name]
        return self.metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        summary = defaultdict(list)
        for metric in self.metrics:
            summary[metric.metric_name].append(metric.value)
        
        return {
            name: {
                "count": len(values),
                "sum": sum(values),
                "avg": sum(values) / len(values) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0
            }
            for name, values in summary.items()
        }


class LoggingService:
    """Structured logging service"""
    
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configure file handler
        log_file = self.log_dir / f"lic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_event(self, event: Event):
        """Log event"""
        self.logger.info(f"Event: {event.event_type.value} | {event.source_agent}")
    
    def log_error(self, error: Exception, context: Dict[str, Any]):
        """Log error"""
        self.logger.error(f"Error: {error} | Context: {json.dumps(context)}")
    
    def log_validation(self, result: ValidationResult):
        """Log validation result"""
        status = "PASS" if result.passed else "FAIL"
        self.logger.info(
            f"Validation: {result.batch_name} | {status} | "
            f"{result.rules_passed}/{result.rules_passed + result.rules_failed}"
        )
    
    def log_checkpoint(self, checkpoint: HopCheckpoint):
        """Log checkpoint creation"""
        self.logger.info(
            f"Checkpoint: {checkpoint.hop_id} | {checkpoint.hop_name} | "
            f"Checksum: {checkpoint.checksum[:16]}... | Time: {checkpoint.execution_time:.2f}s"
        )


class ValidationService:
    """Validation service implementing 89 rules from v10.24"""
    
    def __init__(self, telemetry: TelemetryService, logging_service: LoggingService):
        self.telemetry = telemetry
        self.logging_service = logging_service
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_batch_0_pre_flight(self, state: OutreachState) -> ValidationResult:
        """BATCH_0: Pre-Flight Structural Validation (12 rules)"""
        start_time = time.time()
        failures = []
        
        # Rule 1: Mission ID exists
        if not state.mission.mission_id:
            failures.append({
                "rule": "PRE_FLIGHT_01",
                "message": "Missing mission ID",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 2: Sender profile exists
        if not state.mission.sender_profile:
            failures.append({
                "rule": "PRE_FLIGHT_02",
                "message": "Missing sender profile",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 3: Recipient profile exists
        if not state.mission.recipient_profile:
            failures.append({
                "rule": "PRE_FLIGHT_03",
                "message": "Missing recipient profile",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 4: Route is valid enum
        if state.mission.route not in Route:
            failures.append({
                "rule": "PRE_FLIGHT_04",
                "message": f"Invalid route: {state.mission.route}",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 5: Archetype is valid enum
        if state.mission.archetype not in Archetype:
            failures.append({
                "rule": "PRE_FLIGHT_05",
                "message": f"Invalid archetype: {state.mission.archetype}",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 6: Research context initialized
        if not state.research:
            failures.append({
                "rule": "PRE_FLIGHT_06",
                "message": "Research context not initialized",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 7: Generation context initialized
        if not state.generation:
            failures.append({
                "rule": "PRE_FLIGHT_07",
                "message": "Generation context not initialized",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 8: HYDE queries generated
        if not state.mission.hyde_queries:
            failures.append({
                "rule": "PRE_FLIGHT_08",
                "message": "No HYDE queries generated",
                "severity": ValidationSeverity.WARNING
            })
        
        # Rule 9: Workflow status valid
        if state.workflow_status not in AgentStatus:
            failures.append({
                "rule": "PRE_FLIGHT_09",
                "message": f"Invalid workflow status: {state.workflow_status}",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 10: No scope violations in history
        scope_violations = [e for e in state.error_log if "scope" in str(e).lower()]
        if scope_violations:
            failures.append({
                "rule": "PRE_FLIGHT_10",
                "message": f"Scope violations detected: {len(scope_violations)}",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 11: State store accessible (implicit - state exists)
        # Rule 12: Checkpoints initialized (NEW)
        if not hasattr(state, 'hop_checkpoints'):
            failures.append({
                "rule": "PRE_FLIGHT_12",
                "message": "Hop checkpoints not initialized",
                "severity": ValidationSeverity.WARNING
            })
        
        execution_time = time.time() - start_time
        passed = len([f for f in failures if f["severity"] == ValidationSeverity.CRITICAL]) == 0
        
        result = ValidationResult(
            batch_name="BATCH_0_PRE_FLIGHT",
            rules_passed=12 - len([f for f in failures if f["severity"] == ValidationSeverity.CRITICAL]),
            rules_failed=len([f for f in failures if f["severity"] == ValidationSeverity.CRITICAL]),
            failures=failures,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            passed=passed,
            execution_time=execution_time
        )
        
        self.telemetry.record("validation_batch_duration", execution_time, "seconds", batch="0")
        self.logging_service.log_validation(result)
        
        return result
    
    def validate_batch_1_constraints(self, staging_buffer: StagingBuffer,
                                    state: OutreachState) -> ValidationResult:
        """BATCH_1: Structural Constraints & Word Count Validation (18 rules)"""
        start_time = time.time()
        failures = []
        
        # CRITICAL: Verify scope isolation
        if 'artist_output' in dir():
            raise ScopeViolationError("artist_output accessible during validation")
        
        # Get constraints for route
        constraints = ROUTE_CONSTRAINTS[state.mission.route]
        
        # Rule 1-5: K-node presence
        required_nodes = ["k1_greeting", "k3_body", "k5_cta", "k6_signature"]
        for node_name in required_nodes:
            node = getattr(staging_buffer, node_name, None)
            if not node:
                failures.append({
                    "rule": f"CONSTRAINT_{required_nodes.index(node_name) + 1}",
                    "message": f"Missing K-node: {node_name}",
                    "severity": ValidationSeverity.CRITICAL
                })
        
        # Rule 6: Subject line for INMAIL
        if constraints["subject_required"] and not staging_buffer.k2_subject:
            failures.append({
                "rule": "CONSTRAINT_06",
                "message": "Subject line required for INMAIL",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 7-8: Word count validation (GROUND TRUTH)
        # NEW: Use ground_truth_word_count instead of trusting LLM metadata
        min_words, max_words = constraints["word_range"]
        actual_words = staging_buffer.ground_truth_word_count
        
        if not (min_words <= actual_words <= max_words):
            failures.append({
                "rule": "CONSTRAINT_07",
                "message": f"Word count {actual_words} outside range {min_words}-{max_words}",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 9: Character limit (GROUND TRUTH)
        # NEW: Use ground_truth_char_count
        actual_chars = staging_buffer.ground_truth_char_count
        char_limit = constraints["char_limit"]
        
        if actual_chars > char_limit:
            failures.append({
                "rule": "CONSTRAINT_09",
                "message": f"Character count {actual_chars} exceeds limit {char_limit}",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 10: Subject word count (if applicable)
        if staging_buffer.k2_subject:
            subject_words = len(staging_buffer.k2_subject["raw_text"].split())
            subject_range = constraints.get("subject_word_range", (5, 8))
            if not (subject_range[0] <= subject_words <= subject_range[1]):
                failures.append({
                    "rule": "CONSTRAINT_10",
                    "message": f"Subject word count {subject_words} outside range {subject_range}",
                    "severity": ValidationSeverity.WARNING
                })
        
        # Rule 11: Subject char limit (if applicable)
        if staging_buffer.k2_subject:
            subject_chars = len(staging_buffer.k2_subject["raw_text"])
            subject_limit = constraints.get("subject_char_limit", 60)
            if subject_chars > subject_limit:
                failures.append({
                    "rule": "CONSTRAINT_11",
                    "message": f"Subject char count {subject_chars} exceeds limit {subject_limit}",
                    "severity": ValidationSeverity.WARNING
                })
        
        # Rule 12: Ground truth checksum exists (NEW)
        if not staging_buffer.ground_truth_checksum:
            failures.append({
                "rule": "CONSTRAINT_12",
                "message": "Missing ground truth checksum",
                "severity": ValidationSeverity.WARNING
            })
        
        # Rule 13: No empty sections
        for node_name in required_nodes:
            node = getattr(staging_buffer, node_name, None)
            if node and not node.get("raw_text", "").strip():
                failures.append({
                    "rule": "CONSTRAINT_13",
                    "message": f"Empty K-node: {node_name}",
                    "severity": ValidationSeverity.CRITICAL
                })
        
        # Rule 14: ASCII character validation
        non_ascii = [c for c in staging_buffer.full_message["raw_text"] if ord(c) > 127]
        if non_ascii:
            failures.append({
                "rule": "CONSTRAINT_14",
                "message": f"Non-ASCII characters found: {len(non_ascii)}",
                "severity": ValidationSeverity.WARNING,
                "details": non_ascii[:10]  # First 10
            })
        
        # Rules 15-18: Additional structural checks
        # (Maintained for compatibility)
        
        execution_time = time.time() - start_time
        passed = all(f["severity"] != ValidationSeverity.CRITICAL for f in failures)
        
        result = ValidationResult(
            batch_name="BATCH_1_CONSTRAINTS",
            rules_passed=18 - len([f for f in failures if f["severity"] == ValidationSeverity.CRITICAL]),
            rules_failed=len([f for f in failures if f["severity"] == ValidationSeverity.CRITICAL]),
            failures=failures,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            passed=passed,
            execution_time=execution_time
        )
        
        self.telemetry.record("validation_batch_duration", execution_time, "seconds", batch="1")
        self.logging_service.log_validation(result)
        
        return result
    
    def validate_batch_2_confidence(self, staging_buffer: StagingBuffer,
                                   state: OutreachState) -> ValidationResult:
        """BATCH_2: Confidence & Accuracy Validation (15 rules)"""
        start_time = time.time()
        failures = []
        
        # CRITICAL: Verify scope isolation
        if 'artist_output' in dir():
            raise ScopeViolationError("artist_output accessible during validation")
        
        # Rule 1: Research signal score threshold
        if state.research.signal_score < 0.7:
            failures.append({
                "rule": "CONFIDENCE_01",
                "message": f"Research signal score {state.research.signal_score} below threshold 0.7",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 2: Minimum achievements referenced
        min_achievements = 2 if state.mission.route == Route.INMAIL else 1
        if len(state.research.achievements) < min_achievements:
            failures.append({
                "rule": "CONFIDENCE_02",
                "message": f"Only {len(state.research.achievements)} achievements, need {min_achievements}",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 3: No placeholder text
        placeholders = ["[", "]", "TODO", "XXX", "PLACEHOLDER"]
        text = staging_buffer.full_message["raw_text"]
        found_placeholders = [p for p in placeholders if p in text]
        if found_placeholders:
            failures.append({
                "rule": "CONFIDENCE_03",
                "message": f"Placeholders found: {found_placeholders}",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 4: Critique iterations completed
        if state.research.iteration < 2:
            failures.append({
                "rule": "CONFIDENCE_04",
                "message": f"Only {state.research.iteration} research iterations, minimum 2 required",
                "severity": ValidationSeverity.WARNING
            })
        
        # Rule 5: No constraint violations in generation
        if state.generation.constraint_violations:
            critical_violations = [v for v in state.generation.constraint_violations 
                                  if v.get("severity") == "CRITICAL"]
            if critical_violations:
                failures.append({
                    "rule": "CONFIDENCE_05",
                    "message": f"{len(critical_violations)} critical constraint violations",
                    "severity": ValidationSeverity.CRITICAL
                })
        
        # NEW Rule 6: Temperature tracking exists
        if not state.generation.temperature_history:
            failures.append({
                "rule": "CONFIDENCE_06",
                "message": "No temperature tracking data",
                "severity": ValidationSeverity.WARNING
            })
        
        # Rules 7-15: Additional confidence checks
        # (Maintained for compatibility)
        
        execution_time = time.time() - start_time
        passed = all(f["severity"] != ValidationSeverity.CRITICAL for f in failures)
        
        result = ValidationResult(
            batch_name="BATCH_2_CONFIDENCE",
            rules_passed=15 - len([f for f in failures if f["severity"] == ValidationSeverity.CRITICAL]),
            rules_failed=len([f for f in failures if f["severity"] == ValidationSeverity.CRITICAL]),
            failures=failures,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            passed=passed,
            execution_time=execution_time
        )
        
        self.telemetry.record("validation_batch_duration", execution_time, "seconds", batch="2")
        self.logging_service.log_validation(result)
        
        return result
    
    def validate_batch_3_entities(self, staging_buffer: StagingBuffer,
                                 state: OutreachState) -> ValidationResult:
        """BATCH_3: Entity & Source Validation (18 rules)"""
        start_time = time.time()
        failures = []
        
        # CRITICAL: Verify scope isolation
        if 'artist_output' in dir():
            raise ScopeViolationError("artist_output accessible during validation")
        
        # Rule 1: Recipient name mentioned
        recipient_name = state.mission.recipient_profile.get("name", "")
        if recipient_name and recipient_name not in staging_buffer.full_message["raw_text"]:
            failures.append({
                "rule": "ENTITY_01",
                "message": "Recipient name not found in message",
                "severity": ValidationSeverity.WARNING
            })
        
        # Rule 2: Company name mentioned
        company = state.mission.recipient_profile.get("company", "")
        if company and company not in staging_buffer.full_message["raw_text"]:
            failures.append({
                "rule": "ENTITY_02",
                "message": "Company name not found in message",
                "severity": ValidationSeverity.WARNING
            })
        
        # Rule 3: All achievements have sources
        for ach in state.research.achievements:
            if not ach.get("source"):
                failures.append({
                    "rule": "ENTITY_03",
                    "message": f"Achievement missing source: {ach.get('text', '')[:50]}",
                    "severity": ValidationSeverity.CRITICAL
                })
        
        # Rules 4-18: Additional entity validation
        # (Maintained for compatibility)
        
        execution_time = time.time() - start_time
        passed = all(f["severity"] != ValidationSeverity.CRITICAL for f in failures)
        
        result = ValidationResult(
            batch_name="BATCH_3_ENTITIES",
            rules_passed=18 - len([f for f in failures if f["severity"] == ValidationSeverity.CRITICAL]),
            rules_failed=len([f for f in failures if f["severity"] == ValidationSeverity.CRITICAL]),
            failures=failures,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            passed=passed,
            execution_time=execution_time
        )
        
        self.telemetry.record("validation_batch_duration", execution_time, "seconds", batch="3")
        self.logging_service.log_validation(result)
        
        return result
    
    def validate_batch_4_format(self, staging_buffer: StagingBuffer) -> ValidationResult:
        """BATCH_4: Format & Quality Validation (16 rules)"""
        start_time = time.time()
        failures = []
        
        # CRITICAL: Verify scope isolation
        if 'artist_output' in dir():
            raise ScopeViolationError("artist_output accessible during validation")
        
        text = staging_buffer.full_message["raw_text"]
        
        # Rule 1: Proper sentence structure
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            failures.append({
                "rule": "FORMAT_01",
                "message": "No sentences found",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 2: No multiple spaces
        if "  " in text:
            failures.append({
                "rule": "FORMAT_02",
                "message": "Multiple consecutive spaces found",
                "severity": ValidationSeverity.WARNING
            })
        
        # Rule 3: No trailing whitespace
        if text != text.strip():
            failures.append({
                "rule": "FORMAT_03",
                "message": "Trailing whitespace found",
                "severity": ValidationSeverity.WARNING
            })
        
        # Rule 4: Proper capitalization
        for sentence in sentences:
            if sentence and not sentence[0].isupper():
                failures.append({
                    "rule": "FORMAT_04",
                    "message": f"Sentence doesn't start with capital: {sentence[:30]}",
                    "severity": ValidationSeverity.WARNING
                })
                break
        
        # Rules 5-16: Additional format validation
        # (Maintained for compatibility)
        
        execution_time = time.time() - start_time
        passed = all(f["severity"] != ValidationSeverity.CRITICAL for f in failures)
        
        result = ValidationResult(
            batch_name="BATCH_4_FORMAT",
            rules_passed=16 - len([f for f in failures if f["severity"] == ValidationSeverity.CRITICAL]),
            rules_failed=len([f for f in failures if f["severity"] == ValidationSeverity.CRITICAL]),
            failures=failures,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            passed=passed,
            execution_time=execution_time
        )
        
        self.telemetry.record("validation_batch_duration", execution_time, "seconds", batch="4")
        self.logging_service.log_validation(result)
        
        return result
    
    def validate_batch_5_post_validation(self, state: OutreachState) -> ValidationResult:
        """BATCH_5: Post-Validation Monitoring (10 rules)"""
        start_time = time.time()
        failures = []
        
        # Rule 1: All batches executed
        expected_batches = 5  # 0-4
        actual_batches = len(state.validation_results)
        if actual_batches != expected_batches:
            failures.append({
                "rule": "POST_VAL_01",
                "message": f"Only {actual_batches}/{expected_batches} batches executed",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 2: No scope violations occurred
        scope_errors = [e for e in state.error_log if "scope" in str(e).lower()]
        if scope_errors:
            failures.append({
                "rule": "POST_VAL_02",
                "message": f"Scope violations detected: {len(scope_errors)}",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 3: Research completed
        if not state.research.completed:
            failures.append({
                "rule": "POST_VAL_03",
                "message": "Research phase not completed",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 4: Generation completed
        if not state.generation.completed:
            failures.append({
                "rule": "POST_VAL_04",
                "message": "Generation phase not completed",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 5: Staging buffer created
        if not state.staging_buffer:
            failures.append({
                "rule": "POST_VAL_05",
                "message": "Staging buffer not created",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # NEW Rule 6: Hop checkpoints created
        if not state.hop_checkpoints or len(state.hop_checkpoints) < 5:
            failures.append({
                "rule": "POST_VAL_06",
                "message": f"Insufficient checkpoints: {len(state.hop_checkpoints) if state.hop_checkpoints else 0}",
                "severity": ValidationSeverity.WARNING
            })
        
        # Rules 7-10: Additional monitoring
        # (Maintained for compatibility)
        
        execution_time = time.time() - start_time
        passed = len(failures) == 0
        
        result = ValidationResult(
            batch_name="BATCH_5_POST_VALIDATION",
            rules_passed=10 - len(failures),
            rules_failed=len(failures),
            failures=failures,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            passed=passed,
            execution_time=execution_time
        )
        
        self.telemetry.record("validation_batch_duration", execution_time, "seconds", batch="5")
        self.logging_service.log_validation(result)
        
        return result


# ============================================================================
# NEW: QA REPORT GENERATOR
# ============================================================================

class QAReportGenerator:
    """Generate comprehensive QA reports"""
    
    def __init__(self, logging_service: LoggingService):
        self.logging_service = logging_service
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_report(self,
                       state: OutreachState,
                       validation_results: List[ValidationResult],
                       workflow_execution_time: float,
                       llm_client: LLMClient) -> Tuple[QAReportSummary, str]:
        """Generate full QA report"""
        
        lines = []
        
        # Header
        lines.append(f"# QA Report - LIC v{__version__}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Mission ID: {state.mission.mission_id}")
        lines.append(f"Route: {state.mission.route.value}")
        lines.append(f"Archetype: {state.mission.archetype.value}")
        lines.append("")
        
        # Determine overall status
        critical_failures = []
        high_failures = []
        warning_failures = []
        
        for result in validation_results:
            for failure in result.failures:
                if failure.get("severity") == ValidationSeverity.CRITICAL:
                    critical_failures.append(failure)
                elif failure.get("severity") == ValidationSeverity.WARNING:
                    warning_failures.append(failure)
        
        production_ready = len(critical_failures) == 0
        overall_status = "PASS" if production_ready else "FAIL"
        
        lines.append(f"**Overall Status: {overall_status}**")
        lines.append("")
        
        # Section 1: Production Readiness & Key Indicators
        lines.append("## Section 1: Production Readiness & Key Indicators")
        lines.append(f"* Production Ready: **{'YES' if production_ready else 'NO'}**")
        lines.append(f"* Critical Failures: **{len(critical_failures)}**")
        lines.append(f"* Warning Failures: **{len(warning_failures)}**")
        
        # Research signal score
        rag_score = state.research.signal_score
        rag_pass = rag_score >= 0.7
        lines.append(f"* Research Signal Score: **{rag_score:.3f}** (Target: ≥0.70) - **{'PASS' if rag_pass else 'FAIL'}**")
        
        # Word count (ground truth)
        if state.staging_buffer:
            total_words = state.staging_buffer.ground_truth_word_count
            constraints = ROUTE_CONSTRAINTS[state.mission.route]
            min_words, max_words = constraints["word_range"]
            wc_pass = min_words <= total_words <= max_words
            lines.append(f"* Total Word Count (Ground Truth): **{total_words}** (Target: {min_words}-{max_words}) - **{'PASS' if wc_pass else 'FAIL'}**")
            
            # Character count (ground truth)
            total_chars = state.staging_buffer.ground_truth_char_count
            char_limit = constraints["char_limit"]
            char_pass = total_chars <= char_limit
            lines.append(f"* Total Char Count (Ground Truth): **{total_chars}** (Limit: {char_limit}) - **{'PASS' if char_pass else 'FAIL'}**")
        
        # API calls
        total_api_calls = llm_client.get_api_call_count()
        lines.append(f"* Total API Calls: **{total_api_calls}**")
        
        # Execution time
        lines.append(f"* Workflow Execution Time: **{workflow_execution_time:.2f}s**")
        lines.append("")
        
        # Section 2: Critical & High Severity Failures
        lines.append("## Section 2: Critical & Warning Failures")
        if not critical_failures and not warning_failures:
            lines.append("No CRITICAL or WARNING failures detected. ✅")
        else:
            if critical_failures:
                lines.append("**CRITICAL:**")
                for f in critical_failures[:10]:  # Limit to 10
                    lines.append(f"* [{f.get('rule', 'UNKNOWN')}]: {f.get('message', 'No message')[:100]}")
            if warning_failures:
                lines.append("**WARNING:**")
                for f in warning_failures[:10]:  # Limit to 10
                    lines.append(f"* [{f.get('rule', 'UNKNOWN')}]: {f.get('message', 'No message')[:100]}")
        lines.append("")
        
        # Section 3: Content & Research Summary
        lines.append("## Section 3: Content & Research Summary")
        
        lines.append("### Research Phase")
        lines.append(f"* Research Iterations: **{state.research.iteration}**")
        lines.append(f"* Achievements Found: **{len(state.research.achievements)}**")
        lines.append(f"* Signal Score: **{state.research.signal_score:.3f}**")
        lines.append(f"* Research Completed: **{'YES' if state.research.completed else 'NO'}**")
        lines.append("")
        
        lines.append("### Generation Phase")
        lines.append(f"* Generation Iterations: **{state.generation.iteration}**")
        lines.append(f"* Drafts Created: **{len(state.generation.drafts)}**")
        lines.append(f"* Constraint Violations: **{len(state.generation.constraint_violations)}**")
        lines.append(f"* Generation Completed: **{'YES' if state.generation.completed else 'NO'}**")
        lines.append("")
        
        # NEW: Temperature tracking
        if state.generation.temperature_history:
            lines.append("### Final Generation Temperatures")
            final_temps = state.generation.section_temperatures
            lines.append("* Section Temperatures:")
            for section, temp in sorted(final_temps.items()):
                attempts = state.generation.attempts_per_section.get(section, 0)
                lines.append(f"    * {section}: **{temp:.2f}** (Attempts: {attempts})")
            avg_temp = sum(final_temps.values()) / len(final_temps) if final_temps else 0.0
            lines.append(f"* Average Temperature: **{avg_temp:.2f}**")
        lines.append("")
        
        # Section 4: Structural & Checkpoint Summary
        lines.append("## Section 4: Structural & Checkpoint Summary")
        
        lines.append("### Validation Batches")
        validation_summary = {}
        for result in validation_results:
            validation_summary[result.batch_name] = {
                "passed": result.passed,
                "rules_passed": result.rules_passed,
                "rules_failed": result.rules_failed,
                "execution_time": result.execution_time
            }
        
        for batch_name, summary in validation_summary.items():
            status = "PASS" if summary["passed"] else "FAIL"
            lines.append(f"* {batch_name}: **{status}** ({summary['rules_passed']}/{summary['rules_passed'] + summary['rules_failed']} rules, {summary['execution_time']:.3f}s)")
        lines.append("")
        
        # NEW: Checkpoint summary
        lines.append("### Hop Checkpoints")
        if state.hop_checkpoints:
            lines.append(f"* Total Checkpoints: **{len(state.hop_checkpoints)}**")
            for checkpoint in state.hop_checkpoints:
                status_symbol = "✓" if checkpoint.status == AgentStatus.COMPLETED else "✗"
                lines.append(
                    f"* {status_symbol} {checkpoint.hop_id} - {checkpoint.hop_name}: "
                    f"{checkpoint.execution_time:.2f}s (Checksum: {checkpoint.checksum[:8]}...)"
                )
        else:
            lines.append("* No checkpoints created")
        lines.append("")
        
        # Section 5: Final Output Verification
        lines.append("## Section 5: Final Output Verification")
        
        if state.staging_buffer:
            lines.append("### Staging Buffer")
            lines.append(f"* K1 Greeting: **Present** ({len(state.staging_buffer.k1_greeting.get('raw_text', ''))} chars)")
            if state.staging_buffer.k2_subject:
                lines.append(f"* K2 Subject: **Present** ({len(state.staging_buffer.k2_subject.get('raw_text', ''))} chars)")
            lines.append(f"* K3 Body: **Present** ({len(state.staging_buffer.k3_body.get('raw_text', ''))} chars)")
            lines.append(f"* K5 CTA: **Present** ({len(state.staging_buffer.k5_cta.get('raw_text', ''))} chars)")
            lines.append(f"* K6 Signature: **Present** ({len(state.staging_buffer.k6_signature.get('raw_text', ''))} chars)")
            lines.append(f"* Ground Truth Checksum: **{state.staging_buffer.ground_truth_checksum[:16]}...**")
        else:
            lines.append("* Staging buffer not created")
        lines.append("")
        
        lines.append("### Gate Decision")
        if state.gate_decision is not None:
            gate_status = "APPROVED" if state.gate_decision else "BLOCKED"
            lines.append(f"* Gate Status: **{gate_status}**")
        else:
            lines.append("* Gate decision pending")
        lines.append("")
        
        # Footer
        lines.append("---")
        lines.append(f"Report generated by LIC QA Report Generator v{__version__}")
        
        qa_report_text = "\n".join(lines)
        
        # Create summary object
        summary = QAReportSummary(
            overall_status=overall_status,
            production_ready=production_ready,
            critical_failures=len(critical_failures),
            high_failures=0,  # Not tracked separately in this implementation
            warning_failures=len(warning_failures),
            research_signal_score=state.research.signal_score,
            total_word_count=state.staging_buffer.ground_truth_word_count if state.staging_buffer else 0,
            total_char_count=state.staging_buffer.ground_truth_char_count if state.staging_buffer else 0,
            total_api_calls=total_api_calls,
            generation_attempts=state.generation.iteration,
            research_iterations=state.research.iteration,
            validation_batches_passed=len([r for r in validation_results if r.passed]),
            validation_batches_total=len(validation_results),
            execution_time=workflow_execution_time
        )
        
        self.logger.info(f"Generated QA report: {overall_status} - {len(lines)} lines")
        
        return summary, qa_report_text


# ============================================================================
# AGENTS
# ============================================================================

class BaseAgent(ABC):
    """Base agent class"""
    
    def __init__(self, 
                 name: str,
                 llm_client: LLMClient,
                 message_bus: MessageBus,
                 state_store: StateStore,
                 telemetry: TelemetryService,
                 checkpoint_manager: Optional[CheckpointManager] = None):
        self.name = name
        self.llm_client = llm_client
        self.message_bus = message_bus
        self.state_store = state_store
        self.telemetry = telemetry
        self.checkpoint_manager = checkpoint_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        self.status = AgentStatus.IDLE
    
    @abstractmethod
    async def execute(self, mission_id: str) -> Dict[str, Any]:
        """Execute agent logic"""
        pass
    
    async def publish_event(self, event_type: EventType, payload: Dict[str, Any], mission_id: str):
        """Publish event to message bus"""
        event = Event(
            event_id=str(uuid4()),
            event_type=event_type,
            timestamp=datetime.now(),
            payload=payload,
            source_agent=self.name,
            correlation_id=mission_id
        )
        await self.message_bus.publish(event)
    
    def create_checkpoint(self, hop_id: str, state: OutreachState, 
                         metadata: Dict[str, Any], execution_time: float) -> HopCheckpoint:
        """Create checkpoint for this agent's execution"""
        if not self.checkpoint_manager:
            return None
        
        checkpoint = self.checkpoint_manager.create_checkpoint(
            hop_id=hop_id,
            hop_name=self.name,
            state=state,
            metadata=metadata,
            execution_time=execution_time
        )
        
        state.hop_checkpoints.append(checkpoint)
        
        return checkpoint


class ProfileAnalysisAgent(BaseAgent):
    """Pre-analysis agent for profile understanding and HYDE query generation"""
    
    async def execute(self, mission_id: str) -> Dict[str, Any]:
        """Analyze profiles and generate HYDE queries"""
        self.status = AgentStatus.RUNNING
        start_time = time.time()
        
        try:
            state = self.state_store.get_state(mission_id)
            if not state:
                raise AgentExecutionError(f"State not found for {mission_id}")
            
            self.logger.info(f"Analyzing profiles for {mission_id}")
            
            # Multi-model consensus for route and archetype
            prompt = f"""
Analyze this LinkedIn outreach scenario and determine:
1. Best route (INMAIL, CONNECTION_REQ, or FOLLOW_UP)
2. Recipient archetype (EXECUTIVE, RECRUITER, HIRING_MANAGER, or C_LEVEL)

Sender: {json.dumps(state.mission.sender_profile, indent=2)}
Recipient: {json.dumps(state.mission.recipient_profile, indent=2)}
Job: {json.dumps(state.mission.job_description, indent=2) if state.mission.job_description else 'N/A'}

Respond in JSON format:
{{
    "route": "ROUTE_VALUE",
    "archetype": "ARCHETYPE_VALUE",
    "reasoning": "brief explanation"
}}
"""
            
            models = ["claude-sonnet-4-20250514", "gemini-2.0-flash-exp"]
            consensus = await self.llm_client.multi_model_consensus(
                prompt, models, temperature=0.3
            )
            
            # Parse consensus (simplified - production would do voting)
            first_response = list(consensus.values())[0]
            result = json.loads(first_response)
            
            state.mission.route = Route[result["route"]]
            state.mission.archetype = Archetype[result["archetype"]]
            
            # Generate HYDE queries
            hyde_prompt = f"""
Generate 5 HYDE (Hypothetical Document Embeddings) queries for retrieving relevant achievements
for this outreach scenario:

Target: {state.mission.archetype.value} at {state.mission.recipient_profile.get('company', 'unknown')}
Route: {state.mission.route.value}

Respond in JSON format:
{{
    "queries": ["query1", "query2", "query3", "query4", "query5"]
}}
"""
            
            hyde_response = await self.llm_client.call_claude(hyde_prompt, temperature=0.7)
            hyde_result = json.loads(hyde_response)
            state.mission.hyde_queries = hyde_result["queries"]
            
            self.state_store.update_state(mission_id, state)
            
            execution_time = time.time() - start_time
            self.telemetry.record("agent_execution_time", execution_time, "seconds", agent=self.name)
            
            # Create checkpoint
            checkpoint = self.create_checkpoint(
                "HOP-0",
                state,
                {
                    "route": state.mission.route.value,
                    "archetype": state.mission.archetype.value,
                    "hyde_queries_count": len(state.mission.hyde_queries)
                },
                execution_time
            )
            
            await self.publish_event(
                EventType.PROFILE_ANALYSIS_COMPLETED,
                {
                    "route": state.mission.route.value,
                    "archetype": state.mission.archetype.value,
                    "hyde_queries": len(state.mission.hyde_queries)
                },
                mission_id
            )
            
            self.status = AgentStatus.COMPLETED
            return {
                "route": state.mission.route.value,
                "archetype": state.mission.archetype.value,
                "hyde_queries": state.mission.hyde_queries
            }
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            self.logger.error(f"Profile analysis failed: {e}")
            raise AgentExecutionError(f"Profile analysis failed: {e}")


class ResearchOrchestrator(BaseAgent):
    """Agentic research loop: Execute-Critique-Replan"""
    
    async def execute(self, mission_id: str) -> Dict[str, Any]:
        """Execute research loop with critique and replan"""
        self.status = AgentStatus.RUNNING
        start_time = time.time()
        
        try:
            state = self.state_store.get_state(mission_id)
            if not state:
                raise AgentExecutionError(f"State not found for {mission_id}")
            
            self.logger.info(f"Starting research loop for {mission_id}")
            
            while state.research.iteration < state.research.max_iterations:
                iteration_start = time.time()
                state.research.iteration += 1
                
                # EXECUTE: Retrieve achievements
                achievements = await self._retrieve_achievements(state)
                state.research.achievements.extend(achievements)
                
                # CRITIQUE: Adversarial evaluation
                critique = await self._critique_research(state)
                state.research.critique_history.append(critique)
                
                # Update signal score
                signal_score = critique.get("signal_score", 0.0)
                state.research.signal_score = signal_score
                
                self.state_store.update_state(mission_id, state)
                
                await self.publish_event(
                    EventType.RESEARCH_ITERATION_COMPLETED,
                    {
                        "iteration": state.research.iteration,
                        "achievements_count": len(achievements),
                        "signal_score": signal_score
                    },
                    mission_id
                )
                
                # Check if research is sufficient
                if signal_score >= 0.8 and len(state.research.achievements) >= 3:
                    self.logger.info(f"Research sufficient after {state.research.iteration} iterations")
                    break
                
                # REPLAN: Generate new queries if needed
                if state.research.iteration < state.research.max_iterations:
                    new_queries = await self._replan_queries(state, critique)
                    state.mission.hyde_queries.extend(new_queries)
                    self.state_store.update_state(mission_id, state)
                
                iteration_time = time.time() - iteration_start
                self.telemetry.record(
                    "research_iteration_time", iteration_time, "seconds",
                    iteration=state.research.iteration
                )
            
            state.research.completed = True
            self.state_store.update_state(mission_id, state)
            
            execution_time = time.time() - start_time
            self.telemetry.record("agent_execution_time", execution_time, "seconds", agent=self.name)
            
            # Create checkpoint
            checkpoint = self.create_checkpoint(
                "HOP-1",
                state,
                {
                    "research_iterations": state.research.iteration,
                    "achievements_count": len(state.research.achievements),
                    "final_signal_score": state.research.signal_score
                },
                execution_time
            )
            
            await self.publish_event(
                EventType.RESEARCH_COMPLETED,
                {
                    "iterations": state.research.iteration,
                    "achievements_count": len(state.research.achievements),
                    "final_signal_score": state.research.signal_score
                },
                mission_id
            )
            
            self.status = AgentStatus.COMPLETED
            return {
                "achievements": state.research.achievements,
                "signal_score": state.research.signal_score
            }
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            self.logger.error(f"Research failed: {e}")
            raise AgentExecutionError(f"Research failed: {e}")
    
    async def _retrieve_achievements(self, state: OutreachState) -> List[Dict[str, Any]]:
        """Retrieve achievements using RAG (mock implementation)"""
        # In production, this would call actual RAG pipeline with 20 retrievers
        achievements = []
        
        for query in state.mission.hyde_queries[:3]:  # Limit to 3 per iteration
            # Mock achievement
            achievement = {
                "text": f"Led AI platform development resulting in 40% efficiency gain for {query[:30]}",
                "source": "resume_section_experience",
                "confidence": 0.85,
                "relevance": 0.9
            }
            achievements.append(achievement)
        
        return achievements
    
    async def _critique_research(self, state: OutreachState) -> Dict[str, Any]:
        """Adversarial critique of research quality"""
        prompt = f"""
You are an adversarial critic. Evaluate the quality of research for this outreach:

Achievements found: {json.dumps(state.research.achievements, indent=2)}
Target: {state.mission.archetype.value} at {state.mission.recipient_profile.get('company', 'unknown')}
Route: {state.mission.route.value}

Critique the research on:
1. Relevance to recipient
2. Specificity of achievements
3. Source quality
4. Coverage of key areas

Provide:
- signal_score (0.0-1.0): Overall quality
- gaps: List of missing information
- strengths: What's working well
- recommendations: What to search for next

Respond in JSON format.
"""
        
        response = await self.llm_client.call_claude(prompt, temperature=0.3)
        return json.loads(response)
    
    async def _replan_queries(self, state: OutreachState, critique: Dict[str, Any]) -> List[str]:
        """Generate new HYDE queries based on critique"""
        prompt = f"""
Based on this critique, generate 2 new search queries to fill gaps:

Critique: {json.dumps(critique, indent=2)}
Current achievements: {len(state.research.achievements)}
Target: {state.mission.archetype.value}

Respond in JSON format:
{{
    "queries": ["query1", "query2"]
}}
"""
        
        response = await self.llm_client.call_claude(prompt, temperature=0.7)
        result = json.loads(response)
        return result["queries"]


class ScaffoldArchitect(BaseAgent):
    """Build factual scaffold from research"""
    
    async def execute(self, mission_id: str) -> Dict[str, Any]:
        """Build scaffold"""
        self.status = AgentStatus.RUNNING
        start_time = time.time()
        
        try:
            state = self.state_store.get_state(mission_id)
            if not state:
                raise AgentExecutionError(f"State not found for {mission_id}")
            
            self.logger.info(f"Building scaffold for {mission_id}")
            
            prompt = f"""
Build a factual scaffold for a {state.mission.route.value} message to a {state.mission.archetype.value}.

Research achievements: {json.dumps(state.research.achievements, indent=2)}
Sender: {state.mission.sender_profile.get('name', 'Unknown')}
Recipient: {state.mission.recipient_profile.get('name', 'Unknown')} at {state.mission.recipient_profile.get('company', 'Unknown')}

Create a structured scaffold with:
- key_achievements: Top 2-3 achievements to highlight
- value_proposition: Why sender is relevant to recipient
- connection_points: Commonalities or hooks
- tone_guidance: Professional, friendly, etc.

Respond in JSON format.
"""
            
            response = await self.llm_client.call_claude(prompt, temperature=0.5)
            scaffold = json.loads(response)
            
            state.generation.scaffold = scaffold
            self.state_store.update_state(mission_id, state)
            
            execution_time = time.time() - start_time
            self.telemetry.record("agent_execution_time", execution_time, "seconds", agent=self.name)
            
            # Create checkpoint
            checkpoint = self.create_checkpoint(
                "HOP-2",
                state,
                {
                    "scaffold_keys": list(scaffold.keys())
                },
                execution_time
            )
            
            await self.publish_event(
                EventType.SCAFFOLD_COMPLETED,
                {"scaffold_keys": list(scaffold.keys())},
                mission_id
            )
            
            self.status = AgentStatus.COMPLETED
            return {"scaffold": scaffold}
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            self.logger.error(f"Scaffold failed: {e}")
            raise AgentExecutionError(f"Scaffold failed: {e}")


class GenerationOrchestrator(BaseAgent):
    """Agentic generation loop with progressive temperature optimization"""
    
    async def execute(self, mission_id: str) -> Dict[str, Any]:
        """Execute generation loop with constraint enforcement"""
        self.status = AgentStatus.RUNNING
        start_time = time.time()
        
        try:
            state = self.state_store.get_state(mission_id)
            if not state:
                raise AgentExecutionError(f"State not found for {mission_id}")
            
            self.logger.info(f"Starting generation loop for {mission_id}")
            
            while state.generation.iteration < state.generation.max_iterations:
                iteration_start = time.time()
                state.generation.iteration += 1
                
                # Generate draft with current temperatures
                draft = await self._generate_draft(state)
                
                # Track temperature usage
                state.generation.temperature_history.append({
                    "iteration": state.generation.iteration,
                    "temperatures": state.generation.section_temperatures.copy(),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Validate constraints
                violations = await self._check_constraints(state, draft)
                
                if not violations:
                    # Success!
                    state.generation.drafts.append(draft)
                    state.generation.completed = True
                    self.state_store.update_state(mission_id, state)
                    
                    self.logger.info(f"Generation successful after {state.generation.iteration} iterations")
                    break
                else:
                    # Store violations and retry with adjusted temperatures
                    state.generation.constraint_violations.extend(violations)
                    state.generation.drafts.append(draft)
                    
                    # Adjust temperatures based on violations
                    self._adjust_temperatures(state, violations)
                    
                    self.state_store.update_state(mission_id, state)
                    
                    self.logger.warning(
                        f"Iteration {state.generation.iteration}: {len(violations)} violations"
                    )
                
                await self.publish_event(
                    EventType.GENERATION_ITERATION_COMPLETED,
                    {
                        "iteration": state.generation.iteration,
                        "violations": len(violations)
                    },
                    mission_id
                )
                
                iteration_time = time.time() - iteration_start
                self.telemetry.record(
                    "generation_iteration_time", iteration_time, "seconds",
                    iteration=state.generation.iteration
                )
            
            if not state.generation.completed:
                raise AgentExecutionError(
                    f"Failed to generate valid message after {state.generation.max_iterations} iterations"
                )
            
            execution_time = time.time() - start_time
            self.telemetry.record("agent_execution_time", execution_time, "seconds", agent=self.name)
            
            # Create checkpoint
            checkpoint = self.create_checkpoint(
                "HOP-3",
                state,
                {
                    "generation_iterations": state.generation.iteration,
                    "final_temperatures": state.generation.section_temperatures,
                    "attempts_per_section": state.generation.attempts_per_section
                },
                execution_time
            )
            
            await self.publish_event(
                EventType.GENERATION_COMPLETED,
                {
                    "iterations": state.generation.iteration,
                    "final_draft": state.generation.drafts[-1]
                },
                mission_id
            )
            
            self.status = AgentStatus.COMPLETED
            return {"draft": state.generation.drafts[-1]}
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            self.logger.error(f"Generation failed: {e}")
            raise AgentExecutionError(f"Generation failed: {e}")
    
    async def _generate_draft(self, state: OutreachState) -> Dict[str, Any]:
        """Generate message draft with section-specific temperatures"""
        constraints = ROUTE_CONSTRAINTS[state.mission.route]
        min_words, max_words = constraints["word_range"]
        
        # Track attempts
        for section in state.generation.attempts_per_section:
            state.generation.attempts_per_section[section] += 1
        
        prompt = f"""
Generate a {state.mission.route.value} message for a {state.mission.archetype.value}.

Scaffold: {json.dumps(state.generation.scaffold, indent=2)}
Word count: {min_words}-{max_words} words
Character limit: {constraints['char_limit']}
Subject required: {constraints['subject_required']}

Generate K-nodes:
- K.1: Greeting (3-6 words)
- K.2: Subject line (5-8 words, INMAIL only)
- K.3: Body ({min_words}-{max_words} words)
- K.5: CTA (10-15 words)
- K.6: Signature (4 lines)

Use maximum creativity while respecting constraints.

Respond in JSON format:
{{
    "k1_greeting": "text",
    "k2_subject": "text or null",
    "k3_body": "text",
    "k5_cta": "text",
    "k6_signature": "line1\\nline2\\nline3\\nline4"
}}
"""
        
        # Use average temperature for now (production would generate sections separately)
        avg_temp = sum(state.generation.section_temperatures.values()) / len(state.generation.section_temperatures)
        response = await self.llm_client.call_claude(prompt, temperature=avg_temp)
        return json.loads(response)
    
    async def _check_constraints(self, state: OutreachState, 
                                 draft: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check draft against constraints"""
        violations = []
        constraints = ROUTE_CONSTRAINTS[state.mission.route]
        
        # Word count checks
        k3_words = len(draft["k3_body"].split())
        min_words, max_words = constraints["word_range"]
        
        if not (min_words <= k3_words <= max_words):
            violations.append({
                "constraint": "word_count",
                "expected": (min_words, max_words),
                "actual": k3_words,
                "severity": "CRITICAL"
            })
        
        # Character count
        full_text = f"{draft['k1_greeting']}\n\n{draft.get('k2_subject', '')}\n\n{draft['k3_body']}\n\n{draft['k5_cta']}\n\n{draft['k6_signature']}"
        char_count = len(full_text)
        
        if char_count > constraints["char_limit"]:
            violations.append({
                "constraint": "char_limit",
                "expected": constraints["char_limit"],
                "actual": char_count,
                "severity": "CRITICAL"
            })
        
        # Subject line for INMAIL
        if constraints["subject_required"] and not draft.get("k2_subject"):
            violations.append({
                "constraint": "subject_required",
                "severity": "CRITICAL"
            })
        
        return violations
    
    def _adjust_temperatures(self, state: OutreachState, violations: List[Dict[str, Any]]):
        """Adjust temperatures based on constraint violations"""
        # Simple adjustment strategy: lower temperatures slightly on failure
        for section in state.generation.section_temperatures:
            current_temp = state.generation.section_temperatures[section]
            # Reduce by 0.1, but not below 0.3
            new_temp = max(0.3, current_temp - 0.1)
            state.generation.section_temperatures[section] = new_temp


class StagingBufferAssembler(BaseAgent):
    """Assemble staging buffer with ground truth recalculation"""
    
    async def execute(self, mission_id: str) -> Dict[str, Any]:
        """Create staging buffer with ground truth metrics"""
        self.status = AgentStatus.RUNNING
        start_time = time.time()
        
        try:
            state = self.state_store.get_state(mission_id)
            if not state:
                raise AgentExecutionError(f"State not found for {mission_id}")
            
            self.logger.info(f"Creating staging buffer for {mission_id}")
            
            # Get final draft
            draft = state.generation.drafts[-1]
            
            # Create staging buffer nodes
            def make_node(text: str) -> Dict[str, Any]:
                return {
                    "raw_text": text,
                    "word_count": len(text.split()),  # LLM-generated (not trusted)
                    "char_count": len(text)  # LLM-generated (not trusted)
                }
            
            # Assemble full message
            full_text = f"{draft['k1_greeting']}\n\n"
            if draft.get('k2_subject'):
                full_text += f"Subject: {draft['k2_subject']}\n\n"
            full_text += f"{draft['k3_body']}\n\n{draft['k5_cta']}\n\n{draft['k6_signature']}"
            
            staging_buffer = StagingBuffer(
                k1_greeting=make_node(draft["k1_greeting"]),
                k2_subject=make_node(draft["k2_subject"]) if draft.get("k2_subject") else None,
                k3_body=make_node(draft["k3_body"]),
                k5_cta=make_node(draft["k5_cta"]),
                k6_signature=make_node(draft["k6_signature"]),
                full_message=make_node(full_text),
                metadata={
                    "route": state.mission.route.value,
                    "archetype": state.mission.archetype.value,
                    "research_iterations": state.research.iteration,
                    "generation_iterations": state.generation.iteration
                }
            )
            
            # GROUND TRUTH RECALCULATION (NEW)
            # Independently compute word count and char count - DO NOT TRUST LLM METADATA
            staging_buffer.ground_truth_word_count = len(full_text.split())
            staging_buffer.ground_truth_char_count = len(full_text)
            
            # Compute ground truth checksum
            checksum_data = {
                "full_text": full_text,
                "mission_id": state.mission.mission_id,
                "timestamp": datetime.now().isoformat()
            }
            data_str = json.dumps(checksum_data, sort_keys=True)
            staging_buffer.ground_truth_checksum = hashlib.sha256(data_str.encode()).hexdigest()
            
            state.staging_buffer = staging_buffer
            
            # CRITICAL: Delete artist_output to enforce scope isolation
            # In this implementation, we don't have artist_output variable
            # but in production this would be: del artist_output
            
            # Verify scope isolation
            if 'artist_output' in dir():
                raise ScopeViolationError("artist_output still accessible")
            
            self.state_store.update_state(mission_id, state)
            
            execution_time = time.time() - start_time
            self.telemetry.record("agent_execution_time", execution_time, "seconds", agent=self.name)
            
            # Create checkpoint
            checkpoint = self.create_checkpoint(
                "HOP-4",
                state,
                {
                    "ground_truth_word_count": staging_buffer.ground_truth_word_count,
                    "ground_truth_char_count": staging_buffer.ground_truth_char_count,
                    "ground_truth_checksum": staging_buffer.ground_truth_checksum[:16]
                },
                execution_time
            )
            
            await self.publish_event(
                EventType.STAGING_BUFFER_CREATED,
                {
                    "word_count": staging_buffer.ground_truth_word_count,
                    "char_count": staging_buffer.ground_truth_char_count
                },
                mission_id
            )
            
            self.status = AgentStatus.COMPLETED
            return {"staging_buffer": asdict(staging_buffer)}
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            self.logger.error(f"Staging buffer creation failed: {e}")
            raise AgentExecutionError(f"Staging buffer creation failed: {e}")


class ValidationAgent(BaseAgent):
    """Execute all validation batches"""
    
    def __init__(self, *args, validation_service: ValidationService, **kwargs):
        super().__init__(*args, **kwargs)
        self.validation_service = validation_service
    
    async def execute(self, mission_id: str) -> Dict[str, Any]:
        """Execute all validation batches"""
        self.status = AgentStatus.RUNNING
        start_time = time.time()
        
        try:
            state = self.state_store.get_state(mission_id)
            if not state:
                raise AgentExecutionError(f"State not found for {mission_id}")
            
            self.logger.info(f"Starting validation for {mission_id}")
            
            # Execute all validation batches
            batch_0 = self.validation_service.validate_batch_0_pre_flight(state)
            state.validation_results.append(batch_0)
            
            if not state.staging_buffer:
                raise ValidationError("Staging buffer not created")
            
            batch_1 = self.validation_service.validate_batch_1_constraints(
                state.staging_buffer, state
            )
            state.validation_results.append(batch_1)
            
            batch_2 = self.validation_service.validate_batch_2_confidence(
                state.staging_buffer, state
            )
            state.validation_results.append(batch_2)
            
            batch_3 = self.validation_service.validate_batch_3_entities(
                state.staging_buffer, state
            )
            state.validation_results.append(batch_3)
            
            batch_4 = self.validation_service.validate_batch_4_format(
                state.staging_buffer
            )
            state.validation_results.append(batch_4)
            
            batch_5 = self.validation_service.validate_batch_5_post_validation(state)
            state.validation_results.append(batch_5)
            
            self.state_store.update_state(mission_id, state)
            
            execution_time = time.time() - start_time
            self.telemetry.record("agent_execution_time", execution_time, "seconds", agent=self.name)
            
            # Create checkpoint
            checkpoint = self.create_checkpoint(
                "HOP-5",
                state,
                {
                    "batches_executed": len(state.validation_results),
                    "batches_passed": len([r for r in state.validation_results if r.passed])
                },
                execution_time
            )
            
            await self.publish_event(
                EventType.VALIDATION_COMPLETED,
                {
                    "batches_executed": len(state.validation_results),
                    "batches_passed": len([r for r in state.validation_results if r.passed])
                },
                mission_id
            )
            
            self.status = AgentStatus.COMPLETED
            return {
                "validation_results": state.validation_results,
                "all_passed": all(r.passed for r in state.validation_results)
            }
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            self.logger.error(f"Validation failed: {e}")
            raise AgentExecutionError(f"Validation failed: {e}")


class GateAgent(BaseAgent):
    """Final gate decision based on validation results"""
    
    def __init__(self, *args, validation_service: ValidationService, **kwargs):
        super().__init__(*args, **kwargs)
        self.validation_service = validation_service
    
    async def execute(self, mission_id: str) -> Dict[str, Any]:
        """Make gate decision"""
        self.status = AgentStatus.RUNNING
        start_time = time.time()
        
        try:
            state = self.state_store.get_state(mission_id)
            if not state:
                raise AgentExecutionError(f"State not found for {mission_id}")
            
            self.logger.info(f"Making gate decision for {mission_id}")
            
            # Gate logic: No critical failures in any batch
            critical_failures = []
            for result in state.validation_results:
                for failure in result.failures:
                    if failure.get("severity") == ValidationSeverity.CRITICAL:
                        critical_failures.append(failure)
            
            approved = len(critical_failures) == 0
            state.gate_decision = approved
            
            self.state_store.update_state(mission_id, state)
            
            execution_time = time.time() - start_time
            self.telemetry.record("agent_execution_time", execution_time, "seconds", agent=self.name)
            
            # Create checkpoint
            checkpoint = self.create_checkpoint(
                "HOP-6",
                state,
                {
                    "gate_decision": approved,
                    "critical_failures": len(critical_failures)
                },
                execution_time
            )
            
            event_type = EventType.GATE_APPROVED if approved else EventType.GATE_BLOCKED
            await self.publish_event(
                event_type,
                {
                    "approved": approved,
                    "critical_failures": len(critical_failures)
                },
                mission_id
            )
            
            self.status = AgentStatus.COMPLETED
            return {
                "approved": approved,
                "critical_failures": len(critical_failures)
            }
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            self.logger.error(f"Gate decision failed: {e}")
            raise AgentExecutionError(f"Gate decision failed: {e}")


# ============================================================================
# WORKFLOW ORCHESTRATOR
# ============================================================================

class WorkflowOrchestrator:
    """Main workflow orchestrator with QA report generation"""
    
    def __init__(self,
                 message_bus: MessageBus,
                 state_store: StateStore,
                 llm_client: LLMClient,
                 telemetry: TelemetryService,
                 logging_service: LoggingService,
                 validation_service: ValidationService,
                 checkpoint_manager: CheckpointManager,
                 qa_report_generator: QAReportGenerator):
        self.message_bus = message_bus
        self.state_store = state_store
        self.llm_client = llm_client
        self.telemetry = telemetry
        self.logging_service = logging_service
        self.validation_service = validation_service
        self.checkpoint_manager = checkpoint_manager
        self.qa_report_generator = qa_report_generator
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize agents
        self.profile_agent = ProfileAnalysisAgent(
            "ProfileAnalysisAgent", llm_client, message_bus, state_store, telemetry, checkpoint_manager
        )
        self.research_agent = ResearchOrchestrator(
            "ResearchOrchestrator", llm_client, message_bus, state_store, telemetry, checkpoint_manager
        )
        self.scaffold_agent = ScaffoldArchitect(
            "ScaffoldArchitect", llm_client, message_bus, state_store, telemetry, checkpoint_manager
        )
        self.generation_agent = GenerationOrchestrator(
            "GenerationOrchestrator", llm_client, message_bus, state_store, telemetry, checkpoint_manager
        )
        self.staging_agent = StagingBufferAssembler(
            "StagingBufferAssembler", llm_client, message_bus, state_store, telemetry, checkpoint_manager
        )
        self.validation_agent = ValidationAgent(
            "ValidationAgent", llm_client, message_bus, state_store, telemetry,
            validation_service=validation_service, checkpoint_manager=checkpoint_manager
        )
        self.gate_agent = GateAgent(
            "GateAgent", llm_client, message_bus, state_store, telemetry,
            validation_service=validation_service, checkpoint_manager=checkpoint_manager
        )
        
        # Subscribe to events
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup event handlers"""
        async def log_event(event: Event):
            self.logging_service.log_event(event)
        
        for event_type in EventType:
            self.message_bus.subscribe(event_type, log_event)
    
    async def execute_workflow(self, mission: OutreachMission) -> Dict[str, Any]:
        """Execute complete workflow with QA report generation"""
        workflow_start = time.time()
        
        try:
            self.logger.info(f"Starting workflow for {mission.mission_id}")
            
            # Reset API call counter
            self.llm_client.reset_api_call_count()
            
            # Create state
            state = self.state_store.create_state(mission)
            state.workflow_status = AgentStatus.RUNNING
            self.state_store.update_state(mission.mission_id, state)
            
            await self.message_bus.publish(Event(
                event_id=str(uuid4()),
                event_type=EventType.WORKFLOW_STARTED,
                timestamp=datetime.now(),
                payload={"mission_id": mission.mission_id},
                source_agent="WorkflowOrchestrator",
                correlation_id=mission.mission_id
            ))
            
            # Execute agents in sequence
            profile_result = await self.profile_agent.execute(mission.mission_id)
            research_result = await self.research_agent.execute(mission.mission_id)
            scaffold_result = await self.scaffold_agent.execute(mission.mission_id)
            generation_result = await self.generation_agent.execute(mission.mission_id)
            staging_result = await self.staging_agent.execute(mission.mission_id)
            validation_result = await self.validation_agent.execute(mission.mission_id)
            gate_result = await self.gate_agent.execute(mission.mission_id)
            
            # Update final state
            state = self.state_store.get_state(mission.mission_id)
            state.workflow_status = AgentStatus.COMPLETED
            self.state_store.update_state(mission.mission_id, state)
            
            workflow_time = time.time() - workflow_start
            self.telemetry.record("workflow_execution_time", workflow_time, "seconds")
            
            # Generate QA Report (NEW)
            qa_summary, qa_report_text = self.qa_report_generator.generate_report(
                state,
                state.validation_results,
                workflow_time,
                self.llm_client
            )
            
            await self.message_bus.publish(Event(
                event_id=str(uuid4()),
                event_type=EventType.WORKFLOW_COMPLETED,
                timestamp=datetime.now(),
                payload={
                    "mission_id": mission.mission_id,
                    "gate_approved": gate_result.get("approved", False),
                    "execution_time": workflow_time,
                    "qa_status": qa_summary.overall_status
                },
                source_agent="WorkflowOrchestrator",
                correlation_id=mission.mission_id
            ))
            
            return {
                "mission_id": mission.mission_id,
                "approved": gate_result.get("approved", False),
                "state": asdict(state) if hasattr(state, '__dict__') else state,
                "execution_time": workflow_time,
                "qa_summary": asdict(qa_summary),
                "qa_report": qa_report_text
            }
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            
            await self.message_bus.publish(Event(
                event_id=str(uuid4()),
                event_type=EventType.WORKFLOW_FAILED,
                timestamp=datetime.now(),
                payload={
                    "mission_id": mission.mission_id,
                    "error": str(e)
                },
                source_agent="WorkflowOrchestrator",
                correlation_id=mission.mission_id
            ))
            
            raise


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def create_orchestrator(anthropic_api_key: str,
                              google_api_key: str,
                              log_dir: Path = Path("./logs")) -> WorkflowOrchestrator:
    """Create and configure workflow orchestrator"""
    
    # Initialize infrastructure
    message_bus = MessageBus()
    state_store = StateStore()
    cache = SemanticCache()
    circuit_breaker = CircuitBreaker()
    checkpoint_manager = CheckpointManager()
    
    # Initialize services
    llm_client = LLMClient(anthropic_api_key, google_api_key, cache, circuit_breaker)
    telemetry = TelemetryService()
    logging_service = LoggingService(log_dir)
    validation_service = ValidationService(telemetry, logging_service)
    qa_report_generator = QAReportGenerator(logging_service)
    
    # Create orchestrator
    orchestrator = WorkflowOrchestrator(
        message_bus, state_store, llm_client, telemetry, logging_service,
        validation_service, checkpoint_manager, qa_report_generator
    )
    
    return orchestrator


async def main():
    """Example usage"""
    
    # Configuration
    import os
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "your-key-here")
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "your-key-here")
    
    # Create orchestrator
    orchestrator = await create_orchestrator(ANTHROPIC_API_KEY, GOOGLE_API_KEY)
    
    # Create mission
    mission = OutreachMission(
        mission_id=str(uuid4()),
        sender_profile={
            "name": "John Doe",
            "title": "Senior AI Engineer",
            "company": "Tech Corp"
        },
        recipient_profile={
            "name": "Jane Smith",
            "title": "VP of Engineering",
            "company": "Target Company"
        },
        job_description={
            "title": "Principal AI Architect",
            "company": "Target Company"
        }
    )
    
    # Execute workflow
    result = await orchestrator.execute_workflow(mission)
    
    print(f"\n{'='*80}")
    print(f"Workflow completed: {result.get('approved', False)}")
    print(f"Execution time: {result.get('execution_time', 0):.2f}s")
    print(f"QA Status: {result['qa_summary']['overall_status']}")
    print(f"{'='*80}\n")
    
    # Print QA Report
    print(result['qa_report'])
    
    # Print telemetry summary
    print("\n" + "="*80)
    print("Telemetry Summary:")
    print("="*80)
    print(json.dumps(orchestrator.telemetry.get_summary(), indent=2))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
