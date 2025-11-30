"""
Self Correction Framework Module
LEVEL 5 - Self-correction and error recovery framework for agentic operations
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
from enum import Enum

class CorrectionStrategy(Enum):
    RETRY = "retry"
    ALTERNATIVE_PATH = "alternative_path"
    ROLLBACK = "rollback"
    ADAPTIVE_RETRY = "adaptive_retry"

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ErrorContext:
    """Context information for error correction"""
    error_type: str
    error_message: str
    node_id: str
    execution_context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    severity: ErrorSeverity = ErrorSeverity.MEDIUM

@dataclass
class CorrectionAction:
    """Represents a correction action to be taken"""
    action_id: str
    strategy: CorrectionStrategy
    target_node: str
    parameters: Dict[str, Any]
    success_probability: float = 0.5

@dataclass
class CorrectionResult:
    """Result of a correction attempt"""
    action_id: str
    success: bool
    corrected_result: Any = None
    error_message: Optional[str] = None
    execution_time: float = 0.0

class SelfCorrectionEngine:
    """Self-correction engine for handling errors and recovery"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.correction_history: List[CorrectionResult] = []
        self.error_patterns: Dict[str, List[CorrectionStrategy]] = {
            "timeout_error": [CorrectionStrategy.RETRY, CorrectionStrategy.ADAPTIVE_RETRY],
            "connection_error": [CorrectionStrategy.RETRY, CorrectionStrategy.ALTERNATIVE_PATH],
            "validation_error": [CorrectionStrategy.ALTERNATIVE_PATH, CorrectionStrategy.ROLLBACK],
            "permission_error": [CorrectionStrategy.ALTERNATIVE_PATH],
            "data_error": [CorrectionStrategy.RETRY, CorrectionStrategy.ALTERNATIVE_PATH]
        }

    async def handle_error(
        self,
        error_context: ErrorContext,
        original_function: Callable,
        original_parameters: Dict[str, Any]
    ) -> CorrectionResult:
        """Handle an error with appropriate correction strategy"""
        try:
            # Determine correction strategies
            strategies = self._determine_correction_strategies(error_context)

            # Try each strategy in order
            for strategy in strategies:
                correction_result = await self._apply_correction_strategy(
                    strategy, error_context, original_function, original_parameters
                )

                if correction_result.success:
                    self.correction_history.append(correction_result)
                    self.logger.info(f"Successfully corrected error using {strategy.value}")
                    return correction_result

            # All strategies failed
            failure_result = CorrectionResult(
                action_id=f"failed_{int(datetime.utcnow().timestamp())}",
                success=False,
                error_message="All correction strategies failed"
            )

            self.correction_history.append(failure_result)
            return failure_result

        except Exception as e:
            self.logger.error(f"Error correction failed: {str(e)}")
            return CorrectionResult(
                action_id=f"critical_failure_{int(datetime.utcnow().timestamp())}",
                success=False,
                error_message=str(e)
            )

    def _determine_correction_strategies(self, error_context: ErrorContext) -> List[CorrectionStrategy]:
        """Determine appropriate correction strategies based on error context"""
        error_type = error_context.error_type.lower()

        # Get strategies for this error type
        strategies = self.error_patterns.get(error_type, [CorrectionStrategy.RETRY])

        # Adjust based on severity
        if error_context.severity == ErrorSeverity.CRITICAL:
            strategies = [CorrectionStrategy.ROLLBACK] + strategies
        elif error_context.severity == ErrorSeverity.LOW:
            strategies = strategies[:2]  # Limit to first two strategies for low severity

        return strategies

    async def _apply_correction_strategy(
        self,
        strategy: CorrectionStrategy,
        error_context: ErrorContext,
        original_function: Callable,
        original_parameters: Dict[str, Any]
    ) -> CorrectionResult:
        """Apply a specific correction strategy"""
        start_time = datetime.utcnow()
        action_id = f"{strategy.value}_{int(start_time.timestamp())}"

        try:
            if strategy == CorrectionStrategy.RETRY:
                result = await self._retry_execution(original_function, original_parameters)
            elif strategy == CorrectionStrategy.ADAPTIVE_RETRY:
                result = await self._adaptive_retry_execution(original_function, original_parameters)
            elif strategy == CorrectionStrategy.ALTERNATIVE_PATH:
                result = await self._alternative_path_execution(error_context, original_parameters)
            elif strategy == CorrectionStrategy.ROLLBACK:
                result = await self._rollback_execution(error_context, original_parameters)
            else:
                raise ValueError(f"Unknown correction strategy: {strategy}")

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return CorrectionResult(
                action_id=action_id,
                success=True,
                corrected_result=result,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return CorrectionResult(
                action_id=action_id,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )

    async def _retry_execution(
        self,
        original_function: Callable,
        original_parameters: Dict[str, Any]
    ) -> Any:
        """Simple retry execution"""
        if asyncio.iscoroutinefunction(original_function):
            return await original_function(**original_parameters)
        else:
            return original_function(**original_parameters)

    async def _adaptive_retry_execution(
        self,
        original_function: Callable,
        original_parameters: Dict[str, Any]
    ) -> Any:
        """Adaptive retry with parameter adjustment"""
        # Adjust parameters for retry
        adjusted_parameters = original_parameters.copy()

        # Add timeout if not present
        if "timeout" not in adjusted_parameters:
            adjusted_parameters["timeout"] = 60.0

        # Add retry count
        adjusted_parameters["retry_attempt"] = adjusted_parameters.get("retry_attempt", 0) + 1

        if asyncio.iscoroutinefunction(original_function):
            return await original_function(**adjusted_parameters)
        else:
            return original_function(**adjusted_parameters)

    async def _alternative_path_execution(
        self,
        error_context: ErrorContext,
        original_parameters: Dict[str, Any]
    ) -> Any:
        """Execute alternative path based on error context"""
        # Mock alternative path execution
        await asyncio.sleep(0.1)  # Simulate alternative processing

        # Return mock result
        return {
            "alternative_path_used": True,
            "original_error": error_context.error_type,
            "result": "Alternative execution completed successfully"
        }

    async def _rollback_execution(
        self,
        error_context: ErrorContext,
        original_parameters: Dict[str, Any]
    ) -> Any:
        """Execute rollback to safe state"""
        # Mock rollback execution
        await asyncio.sleep(0.05)  # Simulate rollback

        # Return rollback result
        return {
            "rollback_executed": True,
            "safe_state": True,
            "message": "System rolled back to safe state"
        }

    def learn_from_error(self, error_context: ErrorContext, successful_strategy: CorrectionStrategy) -> None:
        """Learn from successful error corrections"""
        error_type = error_context.error_type.lower()

        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = []

        if successful_strategy not in self.error_patterns[error_type]:
            self.error_patterns[error_type].append(successful_strategy)

            # Move successful strategy to front for future use
            self.error_patterns[error_type].sort(
                key=lambda s: s != successful_strategy
            )

        self.logger.info(f"Learned correction strategy {successful_strategy.value} for error type {error_type}")

    def get_correction_statistics(self) -> Dict[str, Any]:
        """Get statistics about correction performance"""
        if not self.correction_history:
            return {"total_corrections": 0}

        total_corrections = len(self.correction_history)
        successful_corrections = sum(1 for result in self.correction_history if result.success)

        strategy_success = {}
        for result in self.correction_history:
            strategy = result.action_id.split('_')[0]
            if strategy not in strategy_success:
                strategy_success[strategy] = {"total": 0, "successful": 0}
            strategy_success[strategy]["total"] += 1
            if result.success:
                strategy_success[strategy]["successful"] += 1

        return {
            "total_corrections": total_corrections,
            "successful_corrections": successful_corrections,
            "success_rate": successful_corrections / total_corrections,
            "strategy_performance": strategy_success
        }

    def clear_history(self) -> None:
        """Clear correction history"""
        self.correction_history.clear()
        self.logger.info("Cleared correction history")

# Mock error handling functions for demonstration
async def handle_timeout_error(error_context: ErrorContext) -> Dict[str, Any]:
    """Mock function to handle timeout errors"""
    await asyncio.sleep(0.1)
    return {"timeout_handled": True, "extended_timeout": 120.0}

async def handle_connection_error(error_context: ErrorContext) -> Dict[str, Any]:
    """Mock function to handle connection errors"""
    await asyncio.sleep(0.2)
    return {"connection_reestablished": True, "alternative_endpoint": "backup.api.com"}

__all__ = [
    "SelfCorrectionEngine", "ErrorContext", "CorrectionAction",
    "CorrectionResult", "CorrectionStrategy", "ErrorSeverity",
    "handle_timeout_error", "handle_connection_error"
]
