# LIC Error Handler for L3 orchestration
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import traceback

@dataclass
class ErrorContext:
    """Error context information"""
    error_id: str = ""
    error_type: str = ""
    message: str = ""
    traceback_str: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    severity: str = "medium"

@dataclass
class RecoveryAction:
    """Recovery action definition"""
    action_id: str = ""
    action_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3

class LICErrorHandler:
    """Error handler for outreach orchestration"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.error_log = {}
        self.recovery_actions = {}

    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorContext:
        """Handle and log error"""
        error_context = ErrorContext(
            error_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            error_type=type(error).__name__,
            message=str(error),
            traceback_str=traceback.format_exc(),
            context=context or {},
            severity=self._classify_severity(error)
        )

        self.error_log[error_context.error_id] = error_context
        return error_context

    def _classify_severity(self, error: Exception) -> str:
        """Classify error severity"""
        if isinstance(error, (ValueError, TypeError)):
            return "low"
        elif isinstance(error, (ConnectionError, TimeoutError)):
            return "medium"
        else:
            return "high"

    def create_recovery_action(self, error_context: ErrorContext) -> RecoveryAction:
        """Create recovery action for error"""
        action_type = "retry" if error_context.severity in ["low", "medium"] else "escalate"

        recovery = RecoveryAction(
            action_id=f"recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            action_type=action_type,
            parameters={"error_id": error_context.error_id}
        )

        self.recovery_actions[recovery.action_id] = recovery
        return recovery

    def execute_recovery(self, recovery_action: RecoveryAction) -> Dict[str, Any]:
        """Execute recovery action"""
        if recovery_action.retry_count >= recovery_action.max_retries:
            return {"success": False, "message": "Max retries exceeded"}

        recovery_action.retry_count += 1

        if recovery_action.action_type == "retry":
            return {"success": True, "message": "Retry initiated"}
        else:
            return {"success": True, "message": "Escalated to human"}

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error handling summary"""
        return {
            "total_errors": len(self.error_log),
            "severity_breakdown": {
                severity: len([e for e in self.error_log.values() if e.severity == severity])
                for severity in ["low", "medium", "high"]
            },
            "recovery_actions": len(self.recovery_actions)
        }
