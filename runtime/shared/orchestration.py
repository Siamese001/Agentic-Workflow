"""
Orchestration Patterns - Error Recovery, Execution Trace, Fusion Planning
Ported from legacy_engines/lic_orchestrator.py, lic_enhanced_orchestrator.py, lic_fusion_planner.py

Core orchestration patterns for multi-stage pipeline execution
with error recovery, execution tracing, and fusion planning.
"""

import logging
import time
from typing import Dict, List, Optional, Callable, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


# ============================================================================
# Error Recovery
# ============================================================================

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


class RecoveryStrategy(Enum):
    """Recovery strategies"""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ABORT = "abort"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 60
    half_open_max_calls: int = 3


@dataclass
class RetryConfig:
    """Retry configuration"""
    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0
    exponential_backoff: bool = True


@dataclass
class RecoveryResult:
    """Result of error recovery"""
    success: bool
    strategy_used: RecoveryStrategy
    attempts: int
    final_error: Optional[str]
    recovered_value: Optional[Any]


class CircuitBreaker:
    """
    Circuit Breaker Pattern

    Prevents cascading failures by temporarily blocking
    calls to failing services.
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker.

        Args:
            config: Circuit breaker configuration
        """
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.config.recovery_timeout_seconds:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                    return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.config.half_open_max_calls

        return False

    def record_success(self) -> None:
        """Record successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.half_open_max_calls:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info("Circuit breaker CLOSED after recovery")
        else:
            self.failure_count = max(0, self.failure_count - 1)

    def record_failure(self) -> None:
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker OPEN after half-open failure")
        elif self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker OPEN after {self.failure_count} failures")

    def get_state(self) -> Dict[str, object]:
        """Get circuit breaker state."""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time
        }


class ErrorRecoveryManager:
    """
    Error Recovery coordinator

    Manages error recovery with retry, fallback, and circuit breaker patterns.
    """

    def __init__(
        self,
        retry_config: Optional[RetryConfig] = None,
        circuit_config: Optional[CircuitBreakerConfig] = None
    ):
        """
        Initialize error recovery coordinator.

        Args:
            retry_config: Retry configuration
            circuit_config: Circuit breaker configuration
        """
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker = CircuitBreaker(circuit_config)
        self.fallback_handlers: Dict[str, Callable] = {}
        self.recovery_stats = {
            'total_recoveries': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0
        }

    def register_fallback(self, operation_name: str, executor: Callable) -> None:
        """Register a fallback executor for an operation."""
        self.fallback_handlers[operation_name] = executor

    def execute_with_recovery(
        self,
        operation: Callable,
        operation_name: str,
        *args,
        **kwargs
    ) -> RecoveryResult:
        """
        Execute operation with error recovery.

        Args:
            operation: Operation to execute
            operation_name: Name of operation
            *args: Operation arguments
            **kwargs: Operation keyword arguments

        Returns:
            RecoveryResult with execution outcome
        """
        self.recovery_stats['total_recoveries'] += 1

        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            return self._try_fallback(operation_name, args, kwargs, "Circuit breaker open")

        # Try with retries
        last_error = None
        for attempt in range(1, self.retry_config.max_attempts + 1):
            try:
                result = operation(*args, **kwargs)
                self.circuit_breaker.record_success()
                self.recovery_stats['successful_recoveries'] += 1

                return RecoveryResult(
                    success=True,
                    strategy_used=RecoveryStrategy.RETRY if attempt > 1 else RecoveryStrategy.RETRY,
                    attempts=attempt,
                    final_error=None,
                    recovered_value=result
                )

            except (ValueError, TypeError, KeyError) as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt} failed for {operation_name}: {e}")

                if attempt < self.retry_config.max_attempts:
                    delay = self._calculate_delay(attempt)
                    time.sleep(delay)

        # All retries failed
        self.circuit_breaker.record_failure()

        # Try fallback
        return self._try_fallback(operation_name, args, kwargs, last_error)

    def _try_fallback(
        self,
        operation_name: str,
        args: tuple,
        kwargs: dict,
        error: Optional[str]
    ) -> RecoveryResult:
        """Try fallback executor."""
        if operation_name in self.fallback_handlers:
            try:
                result = self.fallback_handlers[operation_name](*args, **kwargs)
                self.recovery_stats['successful_recoveries'] += 1

                return RecoveryResult(
                    success=True,
                    strategy_used=RecoveryStrategy.FALLBACK,
                    attempts=self.retry_config.max_attempts,
                    final_error=None,
                    recovered_value=result
                )
            except (ValueError, TypeError, KeyError) as e:
                error = str(e)

        self.recovery_stats['failed_recoveries'] += 1

        return RecoveryResult(
            success=False,
            strategy_used=RecoveryStrategy.ABORT,
            attempts=self.retry_config.max_attempts,
            final_error=error,
            recovered_value=None
        )

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate retry delay."""
        if self.retry_config.exponential_backoff:
            delay = self.retry_config.base_delay_seconds * (2 ** (attempt - 1))
        else:
            delay = self.retry_config.base_delay_seconds

        return min(delay, self.retry_config.max_delay_seconds)

    def get_stats(self) -> Dict[str, object]:
        """Get recovery statistics."""
        return {
            **self.recovery_stats,
            'circuit_breaker': self.circuit_breaker.get_state(),
            'success_rate': (
                self.recovery_stats['successful_recoveries'] /
                max(self.recovery_stats['total_recoveries'], 1)
            )
        }


# ============================================================================
# Execution Trace
# ============================================================================

class TraceLevel(Enum):
    """Trace detail levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"
    DEBUG = "debug"


@dataclass
class TraceStep:
    """Individual trace step"""
    step_id: str
    step_name: str
    phase: str
    start_time: float
    end_time: Optional[float]
    duration_ms: int = 0
    status: str = "pending"
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class ExecutionTrace:
    """Complete execution trace"""
    trace_id: str
    pipeline_name: str
    steps: List[TraceStep]
    start_time: float
    end_time: Optional[float]
    total_duration_ms: int = 0
    status: str = "running"
    metadata: Dict[str, object] = field(default_factory=dict)


class ExecutionTracer:
    """
    Execution Tracing System

    Tracks pipeline execution with detailed step-by-step tracing.
    """

    def __init__(self, level: TraceLevel = TraceLevel.STANDARD):
        """
        Initialize execution tracer.

        Args:
            level: Trace detail level
        """
        self.level = level
        self.traces: Dict[str, ExecutionTrace] = {}
        self.current_trace: Optional[ExecutionTrace] = None

    def start_trace(self, pipeline_name: str) -> ExecutionTrace:
        """
        Start a new execution trace.

        Args:
            pipeline_name: Name of pipeline

        Returns:
            Created ExecutionTrace
        """
        trace_id = f"trace_{int(time.time())}_{len(self.traces)}"

        trace = ExecutionTrace(
            trace_id=trace_id,
            pipeline_name=pipeline_name,
            steps=[],
            start_time=time.time(),
            end_time=None
        )

        self.traces[trace_id] = trace
        self.current_trace = trace

        logger.info(f"Started trace {trace_id} for pipeline {pipeline_name}")

        return trace

    def start_step(
        self,
        step_name: str,
        phase: str,
        input_data: Optional[Any] = None
    ) -> TraceStep:
        """
        Start a trace step.

        Args:
            step_name: Name of step
            phase: Phase name
            input_data: Optional input data

        Returns:
            Created TraceStep
        """
        if not self.current_trace:
            raise RuntimeError("No active trace")

        step_id = f"step_{len(self.current_trace.steps)}"

        step = TraceStep(
            step_id=step_id,
            step_name=step_name,
            phase=phase,
            start_time=time.time(),
            end_time=None,
            status="running",
            input_summary=self._summarize(input_data) if input_data else None
        )

        self.current_trace.steps.append(step)

        if self.level in [TraceLevel.DETAILED, TraceLevel.DEBUG]:
            logger.debug(f"Started step {step_name} in phase {phase}")

        return step

    def end_step(
        self,
        step: TraceStep,
        output_data: Optional[Any] = None,
        error: Optional[str] = None
    ) -> None:
        """
        End a trace step.

        Args:
            step: Step to end
            output_data: Optional output data
            error: Optional error message
        """
        step.end_time = time.time()
        step.duration_ms = int((step.end_time - step.start_time) * 1000)
        step.status = "error" if error else "completed"
        step.error = error
        step.output_summary = self._summarize(output_data) if output_data else None

        if self.level in [TraceLevel.DETAILED, TraceLevel.DEBUG]:
            logger.debug(f"Ended step {step.step_name}: {step.status} ({step.duration_ms}ms)")

    def end_trace(self, error: Optional[str] = None) -> ExecutionTrace:
        """
        End the current trace.

        Args:
            error: Optional error message

        Returns:
            Completed ExecutionTrace
        """
        if not self.current_trace:
            raise RuntimeError("No active trace")

        trace = self.current_trace
        trace.end_time = time.time()
        trace.total_duration_ms = int((trace.end_time - trace.start_time) * 1000)
        trace.status = "error" if error else "completed"

        if error:
            trace.metadata['error'] = error

        logger.info(f"Ended trace {trace.trace_id}: {trace.status} ({trace.total_duration_ms}ms)")

        self.current_trace = None

        return trace

    def _summarize(self, data: object) -> str:
        """Summarize data for trace."""
        if data is None:
            return "None"

        if isinstance(data, str):
            return data[:100] + "..." if len(data) > 100 else data

        if isinstance(data, dict):
            return f"Dict with {len(data)} keys"

        if isinstance(data, list):
            return f"List with {len(data)} items"

        return str(type(data).__name__)

    def get_trace(self, trace_id: str) -> Optional[ExecutionTrace]:
        """Get trace by ID."""
        return self.traces.get(trace_id)

    def get_trace_summary(self, trace: ExecutionTrace) -> Dict[str, object]:
        """Get summary of trace."""
        step_durations = [s.duration_ms for s in trace.steps if s.duration_ms > 0]

        return {
            'trace_id': trace.trace_id,
            'pipeline_name': trace.pipeline_name,
            'status': trace.status,
            'total_duration_ms': trace.total_duration_ms,
            'step_count': len(trace.steps),
            'avg_step_duration_ms': sum(step_durations) / len(step_durations) if step_durations else 0,
            'error_count': sum(1 for s in trace.steps if s.status == "error")
        }


# ============================================================================
# Fusion Planner
# ============================================================================

@dataclass
class ValueProposition:
    """Value proposition for outreach"""
    prop_id: str
    achievement_snippet: str
    signal_snippet: str
    archetype_target: str
    priority: int
    angle: str
    expected_impact: float
    relevance_score: float
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class MessageSectionPlan:
    """Plan for message section"""
    section_type: str  # opening, body, cta
    archetype_target: str
    value_proposition_ids: List[str]
    tone_guidance: str
    cta_guidance: Optional[str]
    word_count_target: int
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class FusionPlan:
    """Complete fusion plan"""
    role_title: str
    company_name: str
    archetype: str
    value_propositions: List[ValueProposition]
    sections: List[MessageSectionPlan]
    primary_cta_style: str
    fallback_cta_style: str
    confidence_score: float
    metadata: Dict[str, object] = field(default_factory=dict)


class FusionPlanner:
    """
    Fusion Planning for Message Generation

    Creates structured message blueprints by combining
    sender achievements with research signals.
    """

    def __init__(self):
        """Initialize fusion planner."""
        self.archetype_configs = self._load_archetype_configs()
        self.cta_styles = self._load_cta_styles()

    def create_plan(
        self,
        role_title: str,
        company_name: str,
        archetype: str,
        achievements: List[Dict[str, object]],
        signals: List[Dict[str, object]],
        context: Optional[Dict[str, object]] = None
    ) -> FusionPlan:
        """
        Create a fusion plan.

        Args:
            role_title: Target role title
            company_name: Target company name
            archetype: Target archetype
            achievements: Sender achievements
            signals: Research signals
            context: Additional context

        Returns:
            FusionPlan with structured blueprint
        """
        context = context or {}

        # Generate value propositions
        value_propositions = self._generate_value_propositions(
            achievements, signals, archetype
        )

        # Create section plans
        sections = self._create_section_plans(
            value_propositions, archetype, context
        )

        # Determine CTA styles
        primary_cta, fallback_cta = self._determine_cta_styles(archetype, context)

        # Calculate confidence
        confidence = self._calculate_confidence(value_propositions, signals)

        logger.info(f"Created fusion plan for {role_title} at {company_name}: {len(value_propositions)} propositions")

        return FusionPlan(
            role_title=role_title,
            company_name=company_name,
            archetype=archetype,
            value_propositions=value_propositions,
            sections=sections,
            primary_cta_style=primary_cta,
            fallback_cta_style=fallback_cta,
            confidence_score=confidence
        )

    def _generate_value_propositions(
        self,
        achievements: List[Dict[str, object]],
        signals: List[Dict[str, object]],
        archetype: str
    ) -> List[ValueProposition]:
        """Generate value propositions from achievements and signals."""
        propositions = []

        for i, achievement in enumerate(achievements[:5]):  # Limit to top 5
            # Find matching signal
            matching_signal = self._find_matching_signal(achievement, signals)

            if matching_signal:
                prop = ValueProposition(
                    prop_id=f"vp_{i}",
                    achievement_snippet=achievement.get('text', ''),
                    signal_snippet=matching_signal.get('content', ''),
                    archetype_target=archetype,
                    priority=i + 1,
                    angle=self._determine_angle(achievement, matching_signal),
                    expected_impact=self._calculate_impact(achievement, matching_signal),
                    relevance_score=matching_signal.get('relevance_score', 0.5)
                )
                propositions.append(prop)

        # Sort by expected impact
        propositions.sort(key=lambda p: p.expected_impact, reverse=True)

        return propositions

    def _find_matching_signal(
        self,
        achievement: Dict[str, object],
        signals: List[Dict[str, object]]
    ) -> Optional[Dict[str, object]]:
        """Find signal that matches achievement."""
        achievement_text = achievement.get('text', '').lower()
        achievement_words = set(achievement_text.split())

        best_match = None
        best_score = 0.0

        for signal in signals:
            signal_text = signal.get('content', '').lower()
            signal_words = set(signal_text.split())

            if achievement_words and signal_words:
                overlap = len(achievement_words & signal_words)
                score = overlap / len(achievement_words | signal_words)

                if score > best_score:
                    best_score = score
                    best_match = signal

        return best_match if best_score > 0.1 else (signals[0] if signals else None)

    def _determine_angle(
        self,
        achievement: Dict[str, object],
        signal: Dict[str, object]
    ) -> str:
        """Determine messaging angle."""
        achievement_text = achievement.get('text', '').lower()

        if any(word in achievement_text for word in ['led', 'managed', 'directed']):
            return "leadership"
        elif any(word in achievement_text for word in ['built', 'created', 'developed']):
            return "builder"
        elif any(word in achievement_text for word in ['grew', 'increased', 'improved']):
            return "growth"
        elif any(word in achievement_text for word in ['saved', 'reduced', 'optimized']):
            return "efficiency"
        else:
            return "expertise"

    def _calculate_impact(
        self,
        achievement: Dict[str, object],
        signal: Dict[str, object]
    ) -> float:
        """Calculate expected impact of value proposition."""
        base_impact = 0.5

        # Boost for quantified achievements
        if any(c.isdigit() for c in achievement.get('text', '')):
            base_impact += 0.2

        # Boost for high relevance signals
        if signal.get('relevance_score', 0) > 0.7:
            base_impact += 0.15

        # Boost for authority signals
        if signal.get('authority_score', 0) > 0.7:
            base_impact += 0.1

        return min(base_impact, 1.0)

    def _create_section_plans(
        self,
        value_propositions: List[ValueProposition],
        archetype: str,
        context: Dict[str, object]
    ) -> List[MessageSectionPlan]:
        """Create section plans for message."""
        sections = []

        # Opening section
        sections.append(MessageSectionPlan(
            section_type="opening",
            archetype_target=archetype,
            value_proposition_ids=[value_propositions[0].prop_id] if value_propositions else [],
            tone_guidance=self._get_tone_guidance(archetype, "opening"),
            cta_guidance=None,
            word_count_target=30
        ))

        # Body section
        body_props = [vp.prop_id for vp in value_propositions[1:3]] if len(value_propositions) > 1 else []
        sections.append(MessageSectionPlan(
            section_type="body",
            archetype_target=archetype,
            value_proposition_ids=body_props,
            tone_guidance=self._get_tone_guidance(archetype, "body"),
            cta_guidance=None,
            word_count_target=60
        ))

        # CTA section
        sections.append(MessageSectionPlan(
            section_type="cta",
            archetype_target=archetype,
            value_proposition_ids=[],
            tone_guidance=self._get_tone_guidance(archetype, "cta"),
            cta_guidance="soft_ask",
            word_count_target=20
        ))

        return sections

    def _get_tone_guidance(self, archetype: str, section: str) -> str:
        """Get tone guidance for section."""
        config = self.archetype_configs.get(archetype, {})
        return config.get(f"{section}_tone", "professional and engaging")

    def _determine_cta_styles(
        self,
        archetype: str,
        context: Dict[str, object]
    ) -> Tuple[str, str]:
        """Determine primary and fallback CTA styles."""
        config = self.archetype_configs.get(archetype, {})

        primary = config.get('primary_cta', 'soft_ask')
        fallback = config.get('fallback_cta', 'value_offer')

        return primary, fallback

    def _calculate_confidence(
        self,
        value_propositions: List[ValueProposition],
        signals: List[Dict[str, object]]
    ) -> float:
        """Calculate plan confidence score."""
        if not value_propositions:
            return 0.3

        # Average relevance of propositions
        avg_relevance = sum(vp.relevance_score for vp in value_propositions) / len(value_propositions)

        # Signal quality
        signal_quality = sum(s.get('authority_score', 0.5) for s in signals) / len(signals) if signals else 0.5

        confidence = (avg_relevance * 0.6) + (signal_quality * 0.4)

        return round(confidence, 3)

    def _load_archetype_configs(self) -> Dict[str, Dict[str, object]]:
        """Load archetype configurations."""
        return {
            "executive": {
                "opening_tone": "strategic and peer-level",
                "body_tone": "value-focused and concise",
                "cta_tone": "respectful and direct",
                "primary_cta": "strategic_discussion",
                "fallback_cta": "insight_share"
            },
            "technical": {
                "opening_tone": "technically credible",
                "body_tone": "specific and detailed",
                "cta_tone": "collaborative",
                "primary_cta": "technical_exchange",
                "fallback_cta": "resource_share"
            },
            "recruiter": {
                "opening_tone": "professional and helpful",
                "body_tone": "clear and informative",
                "cta_tone": "open and flexible",
                "primary_cta": "availability_check",
                "fallback_cta": "connection_request"
            }
        }

    def _load_cta_styles(self) -> Dict[str, str]:
        """Load CTA style templates."""
        return {
            "soft_ask": "Would you be open to a brief conversation?",
            "strategic_discussion": "I'd welcome the chance to discuss how this might apply to your initiatives.",
            "technical_exchange": "Happy to share more details on the technical approach if helpful.",
            "insight_share": "I can share some insights from similar situations if useful.",
            "resource_share": "I have some resources that might be valuable - happy to send them over.",
            "availability_check": "What does your calendar look like for a quick chat?",
            "connection_request": "Would love to connect and stay in touch."
        }


# ============================================================================
# builder Functions
# ============================================================================

def create_error_recovery_manager(
    max_retries: int = 3,
    failure_threshold: int = 5
) -> ErrorRecoveryManager:
    """Create error recovery coordinator instance."""
    retry_config = RetryConfig(max_attempts=max_retries)
    circuit_config = CircuitBreakerConfig(failure_threshold=failure_threshold)
    return ErrorRecoveryManager(retry_config, circuit_config)


def create_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60
) -> CircuitBreaker:
    """Create circuit breaker instance."""
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        recovery_timeout_seconds=recovery_timeout
    )
    return CircuitBreaker(config)


def create_execution_tracer(level: TraceLevel = TraceLevel.STANDARD) -> ExecutionTracer:
    """Create execution tracer instance."""
    return ExecutionTracer(level)


def create_fusion_planner() -> FusionPlanner:
    """Create fusion planner instance."""
    return FusionPlanner()
