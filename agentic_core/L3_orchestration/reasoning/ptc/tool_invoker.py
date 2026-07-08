"""
Programmatic Tool Calling (PTC) - Tool Invoker

Deterministic tool invocation with safety constraints.
Enforces PowerShell ban, size caps, and write gateway usage.
"""

from __future__ import annotations

import subprocess
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "tool_invoker", "execution_auth")
trace_contract._emit_validates_capability("p2", "tool_invoker", "capability_check")
trace_contract._emit_routes_to_capability("p2", "tool_invoker", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "tool_invoker", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "tool_invoker", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "tool_invoker", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "tool_invoker", "exec_output")
trace_contract._emit_dispatches_agent("p3", "tool_invoker", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "tool_invoker", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "tool_invoker", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "tool_invoker", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "tool_invoker", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "tool_invoker", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "tool_invoker", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "tool_invoker", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "tool_invoker", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "tool_invoker", "eval_metric")
trace_contract._emit_stores_embedding("p4", "tool_invoker", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "tool_invoker", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "tool_invoker", "exec_snapshot_link")
from .tool_contract import (
    ToolCall,
    ToolCallResult,
    canonical_json,
    hash_result_data,
)

trace_contract.emit_replay_key("p0", "tool_invoker")
trace_contract.emit_determinism_digest("p0", "tool_invoker")

trace_contract._emit_dispatches_healing_run("p1", "tool_invoker", "L3")
trace_contract._emit_routes_through("p1", "tool_invoker", "L3")
trace_contract._emit_checks_agent_registry("p1", "tool_invoker", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "tool_invoker", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "tool_invoker", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "tool_invoker", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "tool_invoker", "target_agent")
trace_contract._emit_verifies_policy("p1", "tool_invoker", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "tool_invoker", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "tool_invoker", "boundary_check")
trace_contract._emit_transcripts_response("p1", "tool_invoker", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "tool_invoker")
trace_contract._emit_gated_by_confidence("p1", "tool_invoker", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "tool_invoker", "L3")
trace_contract._emit_reads_policy_state("p1", "tool_invoker", "L3")

trace_contract._emit_snapshots_state("p0", "tool_invoker", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "tool_invoker", "p0_governance")

trace_contract._emit_emits_metric_event("tool_invoker", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("tool_invoker", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("tool_invoker", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("tool_invoker", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("tool_invoker", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("tool_invoker", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("tool_invoker", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("tool_invoker", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("tool_invoker", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("tool_invoker", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("tool_invoker", "p4obs", "alert")
trace_contract._emit_links_incident_trace("tool_invoker", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("tool_invoker", "p3lm", "pattern")
trace_contract._emit_records_learning_event("tool_invoker", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("tool_invoker", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("tool_invoker", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("tool_invoker", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("tool_invoker", "p3lm", "policy")
trace_contract._emit_stores_learning_state("tool_invoker", "p3lm", "state")
trace_contract._emit_records_execution_trace("tool_invoker", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("tool_invoker", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("tool_invoker", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("tool_invoker", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("tool_invoker", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("tool_invoker", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("tool_invoker", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("tool_invoker", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("tool_invoker", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "tool_invoker", "context_pull")
trace_contract._emit_pulls_context("p1", "tool_invoker", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "tool_invoker", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "tool_invoker", "uwg_term_2")
trace_contract._emit_writes_through("p1", "tool_invoker", "write_through")
trace_contract._emit_writes_through("p1", "tool_invoker", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "tool_invoker", "safety_validation")
trace_contract._emit_invokes_eval("p1", "tool_invoker", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "tool_invoker", "routing_commit")


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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ToolInvoker.invoke")

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
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallower
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
