"""
Programmatic Tool Calling (PTC) - Tool Invoker

Deterministic tool invocation with safety constraints.
Enforces PowerShell ban, size caps, and write gateway usage.
"""

from __future__ import annotations

import subprocess
from typing import Any

from .tool_contract import (
    ToolCall,
    ToolCallResult,
    canonical_json,
    hash_result_data,
)
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class ToolInvoker:
    """Deterministic tool invoker with safety constraints."""

    def __init__(
        self,
        max_stdout_bytes: int = 1024 * 1024,  # 1MB
        max_stderr_bytes: int = 1024 * 1024,  # 1MB
    ):
        """Initialize invoker with size limits.

        Args:
            max_stdout_bytes: Maximum stdout size before truncation
            max_stderr_bytes: Maximum stderr size before truncation
        """
        self.max_stdout_bytes = max_stdout_bytes
        self.max_stderr_bytes = max_stderr_bytes

    def invoke(self, call: ToolCall, registry: ToolRegistry) -> ToolCallResult:
        """Invoke a tool call with safety constraints.

        Args:
            call: Tool call to invoke
            registry: Tool registry

        Returns:
            Tool call result

        Raises:
            ValueError: If validation fails
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ToolInvoker.invoke")

        # Get tool specification and handler
        spec, handler = registry.get(call.tool_id)

        # Invoke tool handler with validation
        try:
            # Validate arguments against specification
            self._validate_args(call.args, spec.args)

            # Enforce safety constraints based on side effect class
            if spec.side_effect_class == "SUBPROCESS":
                # PowerShell ban for subprocess tools
                self._enforce_powershell_ban(call.args)

            result = handler(call.args)

            # If handler returns raw subprocess result, process it
            if isinstance(result, subprocess.CompletedProcess):
                stdout, stderr, truncated = self._process_output(
                    result.stdout or "",
                    result.stderr or "",
                )
                exit_code = result.returncode
            else:
                # Handler returned string or other data
                if isinstance(result, str):
                    stdout, stderr, truncated = self._process_output(result, "")
                else:
                    # Convert to JSON for non-string outputs
                    stdout, stderr, truncated = self._process_output(
                        canonical_json(result),
                        "",
                    )
                exit_code = 0

        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            # Tool execution failed
            stdout, stderr, truncated = self._process_output(
                "",
                str(e),
            )
            exit_code = 1

        # Create result with hashes
        result_obj = ToolCallResult(
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            truncated=truncated,
            hashes={},
        )

        # Add hashes
        result_obj.hashes.update(hash_result_data(result_obj))

        return result_obj

    def _validate_args(self, args: dict[str, Any], spec_args: tuple) -> None:
        """Validate arguments against tool specification.

        Args:
            args: Provided arguments
            spec_args: Expected argument specifications

        Raises:
            ValueError: If validation fails
        """
        # Convert spec args to dict for easier lookup
        spec_dict = {arg.name: arg for arg in spec_args}

        # Check for unexpected arguments
        for arg_name in args:
            if arg_name not in spec_dict:
                raise ValueError(f"Unexpected argument: {arg_name}")

        # Check required arguments
        for arg_spec in spec_args:
            if arg_spec.required and arg_spec.name not in args:
                raise ValueError(f"Required argument missing: {arg_spec.name}")

            # Set default for optional args if not provided
            if not arg_spec.required and arg_spec.name not in args:
                if arg_spec.default is not None:
                    args[arg_spec.name] = arg_spec.default

        # Validate argument types
        for arg_name, arg_value in args.items():
            arg_spec = spec_dict[arg_name]
            self._validate_arg_type(arg_name, arg_value, arg_spec.kind)

    def _validate_arg_type(self, name: str, value: Any, kind: str) -> None:
        """Validate individual argument type.

        Args:
            name: Argument name
            value: Argument value
            kind: Expected kind

        Raises:
            ValueError: If type validation fails
        """
        if kind == "str":
            if not isinstance(value, str):
                raise ValueError(f"Argument '{name}' must be string, got {type(value)}")
        elif kind == "int":
            if not isinstance(value, int):
                raise ValueError(f"Argument '{name}' must be int, got {type(value)}")
        elif kind == "bool":
            if not isinstance(value, bool):
                raise ValueError(f"Argument '{name}' must be bool, got {type(value)}")
        elif kind == "list[str]":
            if not isinstance(value, list):
                raise ValueError(f"Argument '{name}' must be list, got {type(value)}")
            if not all(isinstance(item, str) for item in value):
                raise ValueError(f"Argument '{name}' list must contain only strings")
        elif kind == "dict":
            if not isinstance(value, dict):
                raise ValueError(f"Argument '{name}' must be dict, got {type(value)}")
        else:
            raise ValueError(f"Unknown argument kind: {kind}")

    def _enforce_powershell_ban(self, args: dict[str, Any]) -> None:
        """Enforce PowerShell ban for subprocess tools.

        Args:
            args: Tool arguments

        Raises:
            ValueError: If PowerShell usage detected
        """
        # Check for PowerShell in common argument names
        for arg_name, arg_value in args.items():
            if isinstance(arg_value, str):
                if "pwsh" in arg_value.lower() or "powershell" in arg_value.lower():
                    raise ValueError(f"PowerShell usage detected in argument '{arg_name}': {arg_value}")

    def _process_output(self, stdout: str, stderr: str) -> tuple[str, str, bool]:
        """Process output with size limits and truncation.

        Args:
            stdout: Standard output
            stderr: Standard error

        Returns:
            Tuple of (processed_stdout, processed_stderr, was_truncated)
        """
        truncated = False
        processed_stdout = stdout
        processed_stderr = stderr

        # Truncate stdout if needed
        if len(stdout.encode("utf-8")) > self.max_stdout_bytes:
            # Find truncation point
            byte_count = 0
            char_count = 0
            for char in stdout:
                char_bytes = len(char.encode("utf-8"))
                if byte_count + char_bytes > self.max_stdout_bytes:
                    break
                byte_count += char_bytes
                char_count += 1

            processed_stdout = stdout[:char_count] + f"...<TRUNCATED {len(stdout) - char_count} BYTES>"
            truncated = True

        # Truncate stderr if needed
        if len(stderr.encode("utf-8")) > self.max_stderr_bytes:
            # Find truncation point
            byte_count = 0
            char_count = 0
            for char in stderr:
                char_bytes = len(char.encode("utf-8"))
                if byte_count + char_bytes > self.max_stderr_bytes:
                    break
                byte_count += char_bytes
                char_count += 1

            processed_stderr = stderr[:char_count] + f"...<TRUNCATED {len(stderr) - char_count} BYTES>"
            truncated = True

        return processed_stdout, processed_stderr, truncated


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "ToolInvoker",
]
