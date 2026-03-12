"""Feedback Loop Orchestrator - Adaptive Regeneration Engine.

This module provides the orchestration layer for adaptive regeneration with
intelligent failure correction, temperature escalation, and reversion policies.

Primary Responsibilities:
1. Manage regeneration attempts with max 5 attempts
2. Classify failure types and adjust temperature adaptively
3. Implement reversion policy (revert if attempt N worse than N-1)
4. Build regeneration prompts with exact failure details
5. Support message type transitions for dynamic workflow adaptation
"""
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)

class ConstraintFailureType(str, Enum):
    """Types of constraint failures for adaptive retry."""
    MECHANICAL = 'MECHANICAL'
    CREATIVE = 'CREATIVE'
    SEMANTIC = 'SEMANTIC'
    CONFLICT = 'CONFLICT'

@dataclass
class RegenerationCheckpoint:
    """Checkpoint for a single regeneration attempt."""
    attempt: int
    timestamp: datetime
    content: str
    validation_result: Any
    temperature: float
    failure_type: ConstraintFailureType | None = None
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        return {'attempt': self.attempt, 'timestamp': self.timestamp.isoformat(), 'temperature': self.temperature, 'failure_type': self.failure_type.value if self.failure_type else None, 'score': self.score, 'validation_status': self.validation_result.status.value if self.validation_result else None}

@dataclass
class RegenerationResult:
    """Result of regeneration process."""
    success: bool
    final_content: str
    attempts: int
    checkpoints: list[RegenerationCheckpoint]
    final_validation: Any
    reverted: bool = False
    exhausted: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        return {'success': self.success, 'attempts': self.attempts, 'reverted': self.reverted, 'exhausted': self.exhausted, 'checkpoints': [cp.to_dict() for cp in self.checkpoints]}

class FeedbackLoopOrchestrator:
    """Orchestrate adaptive regeneration with intelligent failure correction.

    This orchestrator wraps generation and validation steps, managing the
    regeneration process with adaptive temperature escalation, reversion
    policies, and detailed failure feedback.
    """

    # guardian: allow-magic-config
    def __init__(self, max_attempts: int=5, checkpoint_saving: bool=True, reversion_enabled: bool=True, adaptive_temperature_config: dict[str, Any] | None=None, message_type_transitions: dict[str, Any] | None=None):
        """Initialize feedback loop orchestrator.

        Args:
            max_attempts: Maximum regeneration attempts (default 5)
            checkpoint_saving: Enable checkpoint saving
            reversion_enabled: Enable reversion to better prior attempts
            adaptive_temperature_config: ADAPTIVE_TEMPERATURE_CONFIG from config
            message_type_transitions: MESSAGE_TYPE_TRANSITIONS from config
        """
        self.max_attempts = max_attempts
        self.checkpoint_saving = checkpoint_saving
        self.reversion_enabled = reversion_enabled
        self.adaptive_temperature_config = adaptive_temperature_config or {'initial_temperature': 0.5, 'max_temperature': 0.9, 'escalation_per_retry': 0.1, 'constraint_failure_types': {'MECHANICAL': 0.05, 'CREATIVE': 0.15, 'SEMANTIC': 0.1, 'CONFLICT': 0.0}}
        self.message_type_transitions = message_type_transitions or {}
        logger.info(f'Initialized FeedbackLoopOrchestrator: max_attempts={max_attempts}, reversion={reversion_enabled}')

    async def execute_with_feedback(self, generator: Callable, validator: Callable, initial_context: dict[str, Any], k_node_id: str) -> RegenerationResult:
        """Execute generation with feedback loop.

        Args:
            generator: Async function that generates content
                       Signature: async def generate(context, temperature) -> str
            validator: Async function that validates content
                       Signature: async def validate(content, context) -> ValidationResult
            initial_context: Initial context for generation
            k_node_id: K-node identifier

        Returns:
            RegenerationResult with final content and metadata
        """
        checkpoints = []
        temperature = self.adaptive_temperature_config['initial_temperature']
        context = initial_context.copy()
        for attempt in range(1, self.max_attempts + 1):
            logger.info(f'Attempt {attempt}/{self.max_attempts} for {k_node_id} (temp={temperature:.2f})')
            try:
                content = await generator(context, temperature)
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.error(f'Generation failed on attempt {attempt}: {e}')
                continue
            validation_result = await validator(content, context)
            checkpoint = RegenerationCheckpoint(attempt=attempt, timestamp=datetime.now(), content=content, validation_result=validation_result, temperature=temperature, score=validation_result.score if hasattr(validation_result, 'score') else 0.0)
            if self.checkpoint_saving:
                checkpoints.append(checkpoint)
            if validation_result.passed:
                logger.info(f'Validation passed on attempt {attempt}')
                return RegenerationResult(success=True, final_content=content, attempts=attempt, checkpoints=checkpoints, final_validation=validation_result)
            failure_type = self._classify_failure(validation_result)
            checkpoint.failure_type = failure_type
            logger.warning(f'Validation failed on attempt {attempt}: type={failure_type.value}, score={checkpoint.score:.2f}')
            if self.reversion_enabled and attempt > 1:
                prev_checkpoint = checkpoints[-2]
                if checkpoint.score < prev_checkpoint.score:
                    logger.info(f'Reverting to attempt {attempt - 1} (score {prev_checkpoint.score:.2f} > {checkpoint.score:.2f})')
                    return RegenerationResult(success=True, final_content=prev_checkpoint.content, attempts=attempt, checkpoints=checkpoints, final_validation=prev_checkpoint.validation_result, reverted=True)
            if attempt < self.max_attempts:
                temperature = self._adjust_temperature(temperature, failure_type)
                context = self._build_regeneration_context(initial_context, validation_result, content, attempt)
        logger.error(f'Exhausted all {self.max_attempts} attempts for {k_node_id}')
        if self.reversion_enabled and checkpoints:
            best_checkpoint = max(checkpoints, key=lambda cp: cp.score)
            logger.info(f'Returning best attempt {best_checkpoint.attempt} (score={best_checkpoint.score:.2f})')
            return RegenerationResult(success=False, final_content=best_checkpoint.content, attempts=self.max_attempts, checkpoints=checkpoints, final_validation=best_checkpoint.validation_result, exhausted=True)
        last_checkpoint = checkpoints[-1] if checkpoints else None
        return RegenerationResult(success=False, final_content=last_checkpoint.content if last_checkpoint else '', attempts=self.max_attempts, checkpoints=checkpoints, final_validation=last_checkpoint.validation_result if last_checkpoint else None, exhausted=True)

    def _classify_failure(self, validation_result: Any) -> ConstraintFailureType:
        """Classify failure type based on validation result.

        Args:
            validation_result: ValidationResult from validator

        Returns:
            ConstraintFailureType
        """
        if not hasattr(validation_result, 'failures') or not validation_result.failures:
            return ConstraintFailureType.MECHANICAL
        has_word_count = False
        has_placeholder = False
        has_redundancy = False
        has_forbidden = False
        for failure in validation_result.failures:
            rule_id = failure.rule_id.lower()
            if 'word' in rule_id or 'char' in rule_id or 'variance' in rule_id:
                has_word_count = True
            elif 'placeholder' in rule_id:
                has_placeholder = True
            elif 'dedup' in rule_id or 'similarity' in rule_id or 'redundancy' in rule_id:
                has_redundancy = True
            elif 'forbidden' in rule_id or 'filler' in rule_id:
                has_forbidden = True
        if has_placeholder or has_redundancy:
            return ConstraintFailureType.CREATIVE
        elif has_forbidden:
            return ConstraintFailureType.SEMANTIC
        elif has_word_count:
            return ConstraintFailureType.MECHANICAL
        else:
            return ConstraintFailureType.MECHANICAL

    def _adjust_temperature(self, current_temp: float, failure_type: ConstraintFailureType) -> float:
        """Adjust temperature based on failure type.

        Args:
            current_temp: Current temperature
            failure_type: Type of constraint failure

        Returns:
            Adjusted temperature
        """
        escalation = self.adaptive_temperature_config['constraint_failure_types'].get(failure_type.value, self.adaptive_temperature_config['escalation_per_retry'])
        new_temp = current_temp + escalation
        max_temp = self.adaptive_temperature_config['max_temperature']
        adjusted_temp = min(new_temp, max_temp)
        logger.info(f'Temperature adjustment: {current_temp:.2f} -> {adjusted_temp:.2f} (failure_type={failure_type.value}, escalation={escalation})')
        return adjusted_temp

    def _build_regeneration_context(self, initial_context: dict[str, Any], validation_result: Any, previous_content: str, attempt: int) -> dict[str, Any]:
        """Build context for regeneration with exact failure details.

        Args:
            initial_context: Original context
            validation_result: Validation result with failures
            previous_content: Previously generated content
            attempt: Current attempt number

        Returns:
            Enhanced context with failure feedback
        """
        context = initial_context.copy()
        context['regeneration_attempt'] = attempt
        context['previous_content'] = previous_content
        if hasattr(validation_result, 'failures') and validation_result.failures:
            failure_details = []
            for failure in validation_result.failures:
                detail = {'rule_id': failure.rule_id, 'rule_name': failure.rule_name, 'message': failure.message, 'actual': failure.actual, 'expected': failure.expected}
                failure_details.append(detail)
            context['validation_failures'] = failure_details
            failure_summary = self._build_failure_summary(validation_result.failures)
            context['failure_summary'] = failure_summary
        return context

    def _build_failure_summary(self, failures: list[Any]) -> str:
        """Build human-readable failure summary for regeneration prompt.

        Args:
            failures: List of RuleFailure objects

        Returns:
            Formatted failure summary
        """
        summary_lines = ['VALIDATION FAILURES:']
        for i, failure in enumerate(failures, 1):
            summary_lines.append(f'{i}. {failure.rule_name}: {failure.message}')
            if hasattr(failure, 'actual') and hasattr(failure, 'expected'):
                summary_lines.append(f'   Actual: {failure.actual}, Expected: {failure.expected}')
        summary_lines.append('\nREGENERATION INSTRUCTIONS:')
        summary_lines.append('Fix ONLY the failing sections listed above.')
        summary_lines.append('Maintain all other content unchanged.')
        return '\n'.join(summary_lines)

    def apply_message_transition(self, current_route: str, target_route: str, content: str, context: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Apply message type transition logic.

        Args:
            current_route: Current message route
            target_route: Target message route
            content: Current content
            context: Current context

        Returns:
            Tuple of (modified_content, modified_context)
        """
        transition_key = f'{current_route}_to_{target_route}'
        transition = self.message_type_transitions.get(transition_key)
        if not transition:
            logger.warning(f'No transition defined for {transition_key}')
            return (content, context)
        logger.info(f'Applying transition: {transition_key}')
        if 'action' in transition:
            action = transition['action']
            if 'Regenerate K.3' in action:
                if 'continuity' in action.lower():
                    context['add_continuity_clause'] = True
                    context['prior_content'] = content
            elif 'Expand K.3' in action:
                if 'expansions' in transition:
                    context['expansion_requirements'] = transition['expansions']
            elif 'Enable job-specific RAG' in action:
                context['job_specific_mode'] = True
                if 'requirements' in transition:
                    context['job_requirements'] = transition['requirements']
        return (content, context)

    def generate_failure_report(self, result: RegenerationResult, k_node_id: str) -> str:
        """Generate detailed failure report for exhausted attempts.

        Args:
            result: RegenerationResult from execute_with_feedback
            k_node_id: K-node identifier

        Returns:
            Formatted failure report
        """
        report_lines = [f'REGENERATION FAILURE REPORT: {k_node_id}', '=' * 60, f"Status: {('REVERTED' if result.reverted else 'EXHAUSTED')}", f'Total Attempts: {result.attempts}', f'Max Attempts: {self.max_attempts}', '', 'ATTEMPT HISTORY:']
        for checkpoint in result.checkpoints:
            report_lines.append(f'\nAttempt {checkpoint.attempt}:')
            report_lines.append(f'  Temperature: {checkpoint.temperature:.2f}')
            report_lines.append(f'  Score: {checkpoint.score:.2f}')
            report_lines.append(f"  Failure Type: {(checkpoint.failure_type.value if checkpoint.failure_type else 'N/A')}")
            if hasattr(checkpoint.validation_result, 'failures'):
                report_lines.append(f'  Failures: {len(checkpoint.validation_result.failures)}')
                for failure in checkpoint.validation_result.failures[:3]:
                    report_lines.append(f'    - {failure.rule_name}: {failure.message}')
        if result.reverted:
            report_lines.append(f'\nREVERTED TO: Attempt {result.checkpoints[-2].attempt}')
        report_lines.append('\nRECOMMENDATIONS:')
        if result.exhausted:
            report_lines.append('- Review constraint conflicts')
            report_lines.append('- Adjust generation parameters')
            report_lines.append('- Verify input data quality')
        return '\n'.join(report_lines)
