"""
Script Bridge Interface - Phase 3 Optimization
Bridge between agents and deterministic scripts.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from apps_shared.scripts.io_operations_validator import (
    DataCollectionOperations,
    FileOperations,
    MonitoringOperations,
)

logger = logging.getLogger(__name__)


@dataclass
class ScriptResult:
    """Result from script execution."""

    success: bool
    data: Any
    errors: list[str]
    metadata: dict[str, Any]


class ScriptBridge:
    """
    Bridge interface for agents to call deterministic scripts.

    Provides a clean separation between agent logic and I/O operations,
    improving testability and reducing agent complexity.
    """

    def __init__(self):
        """Initialize script bridge."""
        self.file_ops = FileOperations()
        self.data_ops = DataCollectionOperations()
        self.monitor_ops = MonitoringOperations()

    def execute_script(self, script_name: str, operation: str, **kwargs: Any) -> ScriptResult:
        """
        Execute a script operation.

        Args:
            script_name: Name of script module (file, data, monitor)
            operation: Operation to execute
            **kwargs: Arguments for the operation

        Returns:
            ScriptResult with execution results
        """
        try:
            # Route to appropriate script module
            if script_name == "file":
                result = self._execute_file_operation(operation, **kwargs)
            elif script_name == "data":
                result = self._execute_data_operation(operation, **kwargs)
            elif script_name == "monitor":
                result = self._execute_monitor_operation(operation, **kwargs)
            else:
                return ScriptResult(
                    success=False,
                    data=None,
                    errors=[f"Unknown script module: {script_name}"],
                    metadata={},
                )

            return ScriptResult(success=True, data=result, errors=[], metadata={})

        except Exception as e:
            logger.error(f"Script execution failed: {script_name}.{operation} - {e}")
            return ScriptResult(
                success=False,
                data=None,
                errors=[str(e)],
                metadata={"script": script_name, "operation": operation},
            )

    def _execute_file_operation(self, operation: str, **kwargs: Any) -> Any:
        """Execute file operation."""
        operations = {
            "read_json": self.file_ops.read_json,
            "write_json": self.file_ops.write_json,
            "read_text": self.file_ops.read_text,
            "write_text": self.file_ops.write_text,
            "list_files": self.file_ops.list_files,
            "file_exists": self.file_ops.file_exists,
            "delete_file": self.file_ops.delete_file,
        }

        if operation not in operations:
            raise ValueError(f"Unknown file operation: {operation}")

        return operations[operation](**kwargs)

    def _execute_data_operation(self, operation: str, **kwargs: Any) -> Any:
        """Execute data collection operation."""
        operations = {
            "collect_metrics": self.data_ops.collect_metrics,
            "aggregate_results": self.data_ops.aggregate_results,
            "filter_data": self.data_ops.filter_data,
        }

        if operation not in operations:
            raise ValueError(f"Unknown data operation: {operation}")

        return operations[operation](**kwargs)

    def _execute_monitor_operation(self, operation: str, **kwargs: Any) -> Any:
        """Execute monitoring operation."""
        operations = {
            "check_system_state": self.monitor_ops.check_system_state,
            "record_event": self.monitor_ops.record_event,
            "get_recent_events": self.monitor_ops.get_recent_events,
        }

        if operation not in operations:
            raise ValueError(f"Unknown monitor operation: {operation}")

        return operations[operation](**kwargs)

    def read_config_file(self, file_path: str) -> ScriptResult:
        """
        Convenience method to read config file.

        Args:
            file_path: Path to config file

        Returns:
            ScriptResult with config data
        """
        return self.execute_script("file", "read_json", file_path=file_path)

    def collect_agent_metrics(
        self,
        data_points: list[dict[str, Any]],
        metric_keys: list[str],
    ) -> ScriptResult:
        """
        Convenience method to collect metrics.

        Args:
            data_points: List of data dictionaries
            metric_keys: Keys to collect

        Returns:
            ScriptResult with collected metrics
        """
        return self.execute_script(
            "data",
            "collect_metrics",
            data_points=data_points,
            metric_keys=metric_keys,
        )

    def monitor_system(self, state_file: str) -> ScriptResult:
        """
        Convenience method to check system state.

        Args:
            state_file: Path to state file

        Returns:
            ScriptResult with system state
        """
        return self.execute_script("monitor", "check_system_state", state_file=state_file)


# Global script bridge instance
_script_bridge = None


def get_script_bridge() -> ScriptBridge:
    """Get global script bridge instance."""
    global _script_bridge
    if _script_bridge is None:
        _script_bridge = ScriptBridge()
    return _script_bridge
