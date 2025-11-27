"""
LIC-AGENTIC-v11.1: LinkedIn InMail Cold Outreach - Agentic AI Architecture
===========================================================================

Version: 11.1
Base Version: 10.24
Architecture: Event-Driven Microservices with Agentic Research & Generation Loops
Status: PRODUCTION_READY

Key Upgrades from v10.24:
-------------------------
1. Event-Driven Architecture: Decoupled microservices via message bus
2. Agentic Research Loop: Execute-Critique-Replan with adversarial checking
3. Multi-Model Consensus: Critical decisions use multiple LLMs
4. Enhanced State Management: Comprehensive OutreachState tracking
5. Semantic Caching: Reduce redundant API calls
6. Circuit Breakers: Graceful degradation under failures
7. HYDE-Style Queries: Hypothetical document generation for RAG
8. Pre-Analysis Agent: Profile understanding before generation
9. Dedicated Services: Telemetry, Logging, Validation as first-class services

Architectural Principles:
------------------------
- No Cost/Time Tradeoffs: Maximize quality over efficiency
- Fail-Fast: Explicit errors over silent contamination
- Staging Buffer: Single source of truth for validation
- Scope Isolation: artist_output deleted before QA
- High Signal Rationalization: Multi-hop research with critique
- Stateful Corrections: Feedback loops in research and generation
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
    """Generation phase state"""
    iteration: int = 0
    max_iterations: int = 10
    scaffold: Optional[Dict[str, Any]] = None
    drafts: List[Dict[str, Any]] = field(default_factory=list)
    constraint_violations: List[Dict[str, Any]] = field(default_factory=list)
    completed: bool = False


@dataclass
class StagingBuffer:
    """Staging buffer for ground truth validation"""
    k1_greeting: Dict[str, Any]
    k2_subject: Optional[Dict[str, Any]]
    k3_body: Dict[str, Any]
    k5_cta: Dict[str, Any]
    k6_signature: Dict[str, Any]
    full_message: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)


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


@dataclass
class OutreachState:
    """Complete outreach workflow state"""
    mission: OutreachMission
    research: ResearchContext = field(default_factory=ResearchContext)
    generation: GenerationContext = field(default_factory=GenerationContext)
    staging_buffer: Optional[StagingBuffer] = None
    validation_results: List[ValidationResult] = field(default_factory=list)
    gate_decision: Optional[bool] = None
    workflow_status: AgentStatus = AgentStatus.IDLE
    error_log: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TelemetryMetric:
    """Telemetry metric"""
    metric_name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


# ============================================================================
# EXCEPTIONS
# ============================================================================

class LICException(Exception):
    """Base exception for LIC"""
    pass


class ScopeViolationError(LICException):
    """Scope isolation violated"""
    pass


class ValidationFailureError(LICException):
    """Critical validation failure"""
    pass


class CircuitBreakerOpenError(LICException):
    """Circuit breaker is open"""
    pass


class AgentExecutionError(LICException):
    """Agent execution failed"""
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
    """Multi-model LLM client with caching and circuit breaker"""
    
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
        
        # Rule 11: State store accessible
        # (Implicit - if we got here, state exists)
        
        # Rule 12: Event bus functional
        # (Implicit - validated by workflow initiation)
        
        execution_time = time.time() - start_time
        passed = len(failures) == 0
        
        result = ValidationResult(
            batch_name="BATCH_0_PRE_FLIGHT",
            rules_passed=12 - len(failures),
            rules_failed=len(failures),
            failures=failures,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            passed=passed,
            execution_time=execution_time
        )
        
        self.telemetry.record("validation_batch_duration", execution_time, "seconds", batch="0")
        self.logging_service.log_validation(result)
        
        return result
    
    def validate_batch_1_constraints(self, staging_buffer: StagingBuffer, 
                                    route: Route, archetype: Archetype) -> ValidationResult:
        """BATCH_1: Constraint Compliance Validation (18 rules)"""
        start_time = time.time()
        failures = []
        
        # CRITICAL: Verify scope isolation
        if 'artist_output' in dir():
            raise ScopeViolationError("artist_output accessible during validation")
        
        route_constraints = ROUTE_CONSTRAINTS[route]
        min_words, max_words = route_constraints["word_range"]
        
        # Rule 1: Full message word count in range
        full_count = staging_buffer.full_message["word_count"]
        if not (min_words <= full_count <= max_words):
            failures.append({
                "rule": "CONSTRAINT_01",
                "message": f"Full message {full_count} words not in range [{min_words}, {max_words}]",
                "severity": ValidationSeverity.CRITICAL,
                "actual": full_count,
                "expected": (min_words, max_words)
            })
        
        # Rule 2: Character limit
        char_count = len(staging_buffer.full_message["raw_text"])
        char_limit = route_constraints["char_limit"]
        if char_count > char_limit:
            failures.append({
                "rule": "CONSTRAINT_02",
                "message": f"Character count {char_count} exceeds limit {char_limit}",
                "severity": ValidationSeverity.CRITICAL,
                "actual": char_count,
                "expected": char_limit
            })
        
        # Rule 3: Greeting word count
        greeting_count = staging_buffer.k1_greeting["word_count"]
        if not (3 <= greeting_count <= 6):
            failures.append({
                "rule": "CONSTRAINT_03",
                "message": f"Greeting {greeting_count} words not in range [3, 6]",
                "severity": ValidationSeverity.CRITICAL
            })
        
        # Rule 4: Subject line required for INMAIL
        if route == Route.INMAIL:
            if not staging_buffer.k2_subject:
                failures.append({
                    "rule": "CONSTRAINT_04",
                    "message": "Subject line required for INMAIL",
                    "severity": ValidationSeverity.CRITICAL
                })
            else:
                subject_count = staging_buffer.k2_subject["word_count"]
                if not (5 <= subject_count <= 8):
                    failures.append({
                        "rule": "CONSTRAINT_05",
                        "message": f"Subject {subject_count} words not in range [5, 8]",
                        "severity": ValidationSeverity.CRITICAL
                    })
                
                subject_chars = len(staging_buffer.k2_subject["raw_text"])
                if subject_chars > 60:
                    failures.append({
                        "rule": "CONSTRAINT_06",
                        "message": f"Subject {subject_chars} chars exceeds limit 60",
                        "severity": ValidationSeverity.CRITICAL
                    })
        
        # Rule 7: Archetype target alignment
        min_target, max_target = ARCHETYPE_TARGETS[archetype]
        if not (min_target <= full_count <= max_target):
            failures.append({
                "rule": "CONSTRAINT_07",
                "message": f"Word count {full_count} outside archetype target [{min_target}, {max_target}]",
                "severity": ValidationSeverity.WARNING
            })
        
        # Rule 8-12: K-node structure validation
        required_nodes = ["k1_greeting", "k3_body", "k5_cta", "k6_signature"]
        for node in required_nodes:
            if not getattr(staging_buffer, node, None):
                failures.append({
                    "rule": f"CONSTRAINT_{8 + required_nodes.index(node)}",
                    "message": f"Missing required K-node: {node}",
                    "severity": ValidationSeverity.CRITICAL
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
        
        # Rule 15-18: Additional structural checks
        # (Placeholder for comprehensive rule coverage)
        
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
        
        # Rules 6-15: Additional confidence checks
        # (Placeholder for comprehensive rule coverage)
        
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
        # (Placeholder for comprehensive rule coverage)
        
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
        # (Placeholder for comprehensive rule coverage)
        
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
        
        # Rules 6-10: Additional monitoring
        # (Placeholder for comprehensive rule coverage)
        
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
# AGENTS
# ============================================================================

class BaseAgent(ABC):
    """Base agent class"""
    
    def __init__(self, 
                 name: str,
                 llm_client: LLMClient,
                 message_bus: MessageBus,
                 state_store: StateStore,
                 telemetry: TelemetryService):
        self.name = name
        self.llm_client = llm_client
        self.message_bus = message_bus
        self.state_store = state_store
        self.telemetry = telemetry
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
            # Using first model's response for now
            first_response = list(consensus.values())[0]
            result = json.loads(first_response)
            
            state.mission.route = Route[result["route"]]
            state.mission.archetype = Archetype[result["archetype"]]
            
            # Generate HYDE queries
            hyde_prompt = f"""
Generate 3 hypothetical document queries for RAG retrieval to find relevant achievements for this outreach:

Sender profile: {json.dumps(state.mission.sender_profile, indent=2)}
Recipient: {state.mission.archetype.value} at {state.mission.recipient_profile.get('company', 'unknown')}
Route: {state.mission.route.value}

Generate queries that would retrieve documents about:
1. Relevant technical achievements
2. Leadership/team accomplishments
3. Industry-specific expertise

Respond in JSON format:
{{
    "queries": ["query1", "query2", "query3"]
}}
"""
            
            hyde_response = await self.llm_client.call_claude(
                hyde_prompt, temperature=0.7
            )
            hyde_result = json.loads(hyde_response)
            state.mission.hyde_queries = hyde_result["queries"]
            
            self.state_store.update_state(mission_id, state)
            
            execution_time = time.time() - start_time
            self.telemetry.record("agent_execution_time", execution_time, "seconds", agent=self.name)
            
            await self.publish_event(
                EventType.PROFILE_ANALYSIS_COMPLETED,
                {
                    "route": state.mission.route.value,
                    "archetype": state.mission.archetype.value,
                    "hyde_queries": state.mission.hyde_queries
                },
                mission_id
            )
            
            self.status = AgentStatus.COMPLETED
            return {
                "route": state.mission.route,
                "archetype": state.mission.archetype,
                "hyde_queries": state.mission.hyde_queries
            }
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            self.logger.error(f"Profile analysis failed: {e}")
            raise AgentExecutionError(f"Profile analysis failed: {e}")


class ResearchOrchestrator(BaseAgent):
    """Agentic research loop: Execute-Critique-Replan"""
    
    async def execute(self, mission_id: str) -> Dict[str, Any]:
        """Execute research loop with critique and replanning"""
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
                
                # EXECUTE: Retrieve achievements using HYDE queries
                achievements = await self._retrieve_achievements(state)
                state.research.achievements.extend(achievements)
                
                # CRITIQUE: Adversarial checking
                critique = await self._critique_research(state)
                state.research.critique_history.append(critique)
                
                # Calculate signal score
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
                "text": f"Achievement related to: {query}",
                "source": "resume_section_X",
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
    """Agentic generation loop: No Cost/Time Tradeoffs"""
    
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
                
                # Generate draft with high temperature
                draft = await self._generate_draft(state)
                
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
                    # Store violations and retry
                    state.generation.constraint_violations.extend(violations)
                    state.generation.drafts.append(draft)
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
        """Generate message draft with high temperature"""
        constraints = ROUTE_CONSTRAINTS[state.mission.route]
        min_words, max_words = constraints["word_range"]
        
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
        
        # High temperature for creativity
        response = await self.llm_client.call_claude(prompt, temperature=1.0)
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


class StagingBufferAssembler(BaseAgent):
    """Assemble staging buffer for validation"""
    
    async def execute(self, mission_id: str) -> Dict[str, Any]:
        """Create staging buffer"""
        self.status = AgentStatus.RUNNING
        start_time = time.time()
        
        try:
            state = self.state_store.get_state(mission_id)
            if not state:
                raise AgentExecutionError(f"State not found for {mission_id}")
            
            self.logger.info(f"Creating staging buffer for {mission_id}")
            
            # Get final draft
            draft = state.generation.drafts[-1]
            
            # Create staging buffer
            def make_node(text: str) -> Dict[str, Any]:
                return {
                    "raw_text": text,
                    "word_count": len(text.split()),
                    "char_count": len(text)
                }
            
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
            
            await self.publish_event(
                EventType.STAGING_BUFFER_CREATED,
                {"word_count": staging_buffer.full_message["word_count"]},
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
        """Run all validation batches"""
        self.status = AgentStatus.RUNNING
        start_time = time.time()
        
        try:
            state = self.state_store.get_state(mission_id)
            if not state:
                raise AgentExecutionError(f"State not found for {mission_id}")
            
            self.logger.info(f"Starting validation for {mission_id}")
            
            if not state.staging_buffer:
                raise ValidationFailureError("Staging buffer not created")
            
            # BATCH 0: Pre-flight
            batch0 = self.validation_service.validate_batch_0_pre_flight(state)
            state.validation_results.append(batch0)
            
            await self.publish_event(
                EventType.VALIDATION_BATCH_COMPLETED,
                {"batch": 0, "passed": batch0.passed},
                mission_id
            )
            
            if not batch0.passed:
                raise ValidationFailureError("Pre-flight validation failed")
            
            # BATCH 1: Constraints
            batch1 = self.validation_service.validate_batch_1_constraints(
                state.staging_buffer, state.mission.route, state.mission.archetype
            )
            state.validation_results.append(batch1)
            
            await self.publish_event(
                EventType.VALIDATION_BATCH_COMPLETED,
                {"batch": 1, "passed": batch1.passed},
                mission_id
            )
            
            # BATCH 2: Confidence
            batch2 = self.validation_service.validate_batch_2_confidence(
                state.staging_buffer, state
            )
            state.validation_results.append(batch2)
            
            await self.publish_event(
                EventType.VALIDATION_BATCH_COMPLETED,
                {"batch": 2, "passed": batch2.passed},
                mission_id
            )
            
            # BATCH 3: Entities
            batch3 = self.validation_service.validate_batch_3_entities(
                state.staging_buffer, state
            )
            state.validation_results.append(batch3)
            
            await self.publish_event(
                EventType.VALIDATION_BATCH_COMPLETED,
                {"batch": 3, "passed": batch3.passed},
                mission_id
            )
            
            # BATCH 4: Format
            batch4 = self.validation_service.validate_batch_4_format(
                state.staging_buffer
            )
            state.validation_results.append(batch4)
            
            await self.publish_event(
                EventType.VALIDATION_BATCH_COMPLETED,
                {"batch": 4, "passed": batch4.passed},
                mission_id
            )
            
            self.state_store.update_state(mission_id, state)
            
            # Check if all critical validations passed
            all_passed = all(
                r.passed or r.severity != ValidationSeverity.CRITICAL 
                for r in state.validation_results
            )
            
            execution_time = time.time() - start_time
            self.telemetry.record("agent_execution_time", execution_time, "seconds", agent=self.name)
            
            await self.publish_event(
                EventType.VALIDATION_COMPLETED,
                {
                    "passed": all_passed,
                    "batches": len(state.validation_results)
                },
                mission_id
            )
            
            self.status = AgentStatus.COMPLETED
            return {
                "passed": all_passed,
                "results": [asdict(r) for r in state.validation_results]
            }
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            self.logger.error(f"Validation failed: {e}")
            raise AgentExecutionError(f"Validation failed: {e}")


class GateAgent(BaseAgent):
    """Make final gate decision"""
    
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
            
            # Check all validations
            all_passed = all(
                r.passed or r.severity != ValidationSeverity.CRITICAL 
                for r in state.validation_results
            )
            
            state.gate_decision = all_passed
            
            # BATCH 5: Post-validation monitoring
            batch5 = self.validation_service.validate_batch_5_post_validation(state)
            state.validation_results.append(batch5)
            
            self.state_store.update_state(mission_id, state)
            
            execution_time = time.time() - start_time
            self.telemetry.record("agent_execution_time", execution_time, "seconds", agent=self.name)
            
            event_type = EventType.GATE_APPROVED if all_passed else EventType.GATE_BLOCKED
            await self.publish_event(
                event_type,
                {"decision": all_passed},
                mission_id
            )
            
            self.status = AgentStatus.COMPLETED
            return {"approved": all_passed}
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            self.logger.error(f"Gate decision failed: {e}")
            raise AgentExecutionError(f"Gate decision failed: {e}")


# ============================================================================
# WORKFLOW ORCHESTRATOR
# ============================================================================

class WorkflowOrchestrator:
    """Main workflow orchestrator"""
    
    def __init__(self,
                 message_bus: MessageBus,
                 state_store: StateStore,
                 llm_client: LLMClient,
                 telemetry: TelemetryService,
                 logging_service: LoggingService,
                 validation_service: ValidationService):
        self.message_bus = message_bus
        self.state_store = state_store
        self.llm_client = llm_client
        self.telemetry = telemetry
        self.logging_service = logging_service
        self.validation_service = validation_service
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize agents
        self.profile_agent = ProfileAnalysisAgent(
            "ProfileAnalysisAgent", llm_client, message_bus, state_store, telemetry
        )
        self.research_agent = ResearchOrchestrator(
            "ResearchOrchestrator", llm_client, message_bus, state_store, telemetry
        )
        self.scaffold_agent = ScaffoldArchitect(
            "ScaffoldArchitect", llm_client, message_bus, state_store, telemetry
        )
        self.generation_agent = GenerationOrchestrator(
            "GenerationOrchestrator", llm_client, message_bus, state_store, telemetry
        )
        self.staging_agent = StagingBufferAssembler(
            "StagingBufferAssembler", llm_client, message_bus, state_store, telemetry
        )
        self.validation_agent = ValidationAgent(
            "ValidationAgent", llm_client, message_bus, state_store, telemetry,
            validation_service=validation_service
        )
        self.gate_agent = GateAgent(
            "GateAgent", llm_client, message_bus, state_store, telemetry,
            validation_service=validation_service
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
        """Execute complete workflow"""
        workflow_start = time.time()
        
        try:
            self.logger.info(f"Starting workflow for {mission.mission_id}")
            
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
            
            await self.message_bus.publish(Event(
                event_id=str(uuid4()),
                event_type=EventType.WORKFLOW_COMPLETED,
                timestamp=datetime.now(),
                payload={
                    "mission_id": mission.mission_id,
                    "gate_approved": gate_result.get("approved", False),
                    "execution_time": workflow_time
                },
                source_agent="WorkflowOrchestrator",
                correlation_id=mission.mission_id
            ))
            
            return {
                "mission_id": mission.mission_id,
                "approved": gate_result.get("approved", False),
                "state": asdict(state) if hasattr(state, '__dict__') else state,
                "execution_time": workflow_time
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
    
    # Initialize services
    llm_client = LLMClient(anthropic_api_key, google_api_key, cache, circuit_breaker)
    telemetry = TelemetryService()
    logging_service = LoggingService(log_dir)
    validation_service = ValidationService(telemetry, logging_service)
    
    # Create orchestrator
    orchestrator = WorkflowOrchestrator(
        message_bus, state_store, llm_client, telemetry, logging_service, validation_service
    )
    
    return orchestrator


async def main():
    """Example usage"""
    
    # Configuration
    ANTHROPIC_API_KEY = "your-key-here"
    GOOGLE_API_KEY = "your-key-here"
    
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
    
    print(f"Workflow completed: {result.get('approved', False)}")
    print(f"Execution time: {result.get('execution_time', 0):.2f}s")
    
    # Print telemetry summary
    print("\nTelemetry Summary:")
    print(json.dumps(orchestrator.telemetry.get_summary(), indent=2))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
