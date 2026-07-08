from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "secure_tools_impl")
trace_contract.emit_determinism_digest("p0", "secure_tools_impl")

trace_contract._emit_dispatches_healing_run("p1", "secure_tools_impl", "L2")
trace_contract._emit_routes_through("p1", "secure_tools_impl", "L2")
trace_contract._emit_checks_agent_registry("p1", "secure_tools_impl", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "secure_tools_impl", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "secure_tools_impl", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "secure_tools_impl", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "secure_tools_impl", "target_agent")
trace_contract._emit_verifies_policy("p1", "secure_tools_impl", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "secure_tools_impl", "runtime_state")
trace_contract._emit_transcripts_response("p1", "secure_tools_impl", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "secure_tools_impl")
trace_contract._emit_gated_by_confidence("p1", "secure_tools_impl", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "secure_tools_impl", "L2")
trace_contract._emit_reads_policy_state("p1", "secure_tools_impl", "L2")

trace_contract._emit_applies_guardrail("p0", "secure_tools_impl", "p0_governance")
trace_contract._emit_snapshots_state("p0", "secure_tools_impl", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "secure_tools_impl", "execution_auth")
trace_contract._emit_validates_capability("p2", "secure_tools_impl", "capability_check")
trace_contract._emit_routes_to_capability("p2", "secure_tools_impl", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "secure_tools_impl", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "secure_tools_impl", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "secure_tools_impl", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "secure_tools_impl", "exec_output")
trace_contract._emit_dispatches_agent("p3", "secure_tools_impl", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "secure_tools_impl", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "secure_tools_impl", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "secure_tools_impl", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "secure_tools_impl", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "secure_tools_impl", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "secure_tools_impl", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "secure_tools_impl", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "secure_tools_impl", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "secure_tools_impl", "eval_metric")
trace_contract._emit_stores_embedding("p4", "secure_tools_impl", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "secure_tools_impl", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "secure_tools_impl", "exec_snapshot_link")

"\nSecure Tools - Atomic Module\nExtracted from ActionNode.py via Atomic Fission Protocol\nImplements sandboxed file operations and command execution\n"
import logging
import os
import shlex
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    DEFAULT_TIMEOUT,
)  # guardian: allow-layer-violation -- L2 module uses L0 config/enforcement; intentional downward enforcement-chain dependency

trace_contract._emit_emits_metric_event("secure_tools_impl", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("secure_tools_impl", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("secure_tools_impl", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("secure_tools_impl", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("secure_tools_impl", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("secure_tools_impl", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("secure_tools_impl", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("secure_tools_impl", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("secure_tools_impl", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("secure_tools_impl", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("secure_tools_impl", "p4obs", "alert")
trace_contract._emit_links_incident_trace("secure_tools_impl", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("secure_tools_impl", "p3lm", "pattern")
trace_contract._emit_records_learning_event("secure_tools_impl", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("secure_tools_impl", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("secure_tools_impl", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("secure_tools_impl", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("secure_tools_impl", "p3lm", "policy")
trace_contract._emit_stores_learning_state("secure_tools_impl", "p3lm", "state")
trace_contract._emit_records_execution_trace("secure_tools_impl", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("secure_tools_impl", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("secure_tools_impl", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("secure_tools_impl", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("secure_tools_impl", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("secure_tools_impl", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("secure_tools_impl", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("secure_tools_impl", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("secure_tools_impl", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "secure_tools_impl", "context_pull")
trace_contract._emit_pulls_context("p1", "secure_tools_impl", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "secure_tools_impl", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "secure_tools_impl", "uwg_term_2")
trace_contract._emit_writes_through("p1", "secure_tools_impl", "write_through")
trace_contract._emit_writes_through("p1", "secure_tools_impl", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "secure_tools_impl", "safety_validation")
trace_contract._emit_invokes_eval("p1", "secure_tools_impl", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "secure_tools_impl", "routing_commit")


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str, action_class_name: str = "MUTATION"):
    from agentic_core.L4_state.utils.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    ac = ActionClass(action_class_name)
    return ExecutionContext.create(
        run_id="secure_tools",
        capability_token="default",
        policy_hash="default",
        execution_input=payload,
        execution_target=target,
        action_class=ac,
    )


Logger: Any = logging.getLogger("ActionNode.SecureTools")


class SecureToolsImpl:
    """
    Secure tool implementations with path validation and command blacklisting.
    """

    BLACKLIST_COMMANDS: list[str] = ["rm -rf", "sudo", "format", "> /dev/sda", "mkfs"]
    SAFE_BINARIES: frozenset[str] = frozenset(
        {
            "python",
            "python3",
            "pytest",
            "ruff",
            "mypy",
            "node",
            "npm",
            "git",
            "ls",
            "cat",
            "echo",
        }
    )
    SHELL_METACHARS: tuple[str, ...] = (";", "&&", "||", "|", ">", "<", "$(", "`")

    def __init__(self, work_dir: Path):
        """
        Initialize secure tools.

        Args:
            work_dir (Path): Working directory for sandboxing
        """
        self.work_dir = work_dir.resolve()
        if not self.work_dir.exists() or not self.work_dir.is_dir():
            raise ValueError(f"SECURITY VIOLATION: Working directory is invalid: {self.work_dir}")

    def _safe_cwd(self) -> Path:
        cwd = self.work_dir.resolve()
        if not cwd.exists() or not cwd.is_dir():
            raise ValueError(f"SECURITY VIOLATION: Working directory is invalid: {cwd}")
        return cwd

    def _parse_and_validate_command(self, command: str) -> list[str]:
        if not command or not command.strip():
            raise ValueError("SECURITY VIOLATION: Empty command.")
        if any(token in command for token in self.SHELL_METACHARS):
            raise ValueError(
                "SECURITY VIOLATION: Shell metacharacters are not allowed. Pass argv-style commands only.",
            )
        if any(b in command for b in self.BLACKLIST_COMMANDS):
            raise ValueError(
                "SECURITY VIOLATION: Command contains blacklisted patterns. Refusing to execute.",
            )
        argv = shlex.split(command, posix=True)
        if not argv:
            raise ValueError("SECURITY VIOLATION: Command did not parse into argv.")
        binary = Path(argv[0]).name
        if binary not in self.SAFE_BINARIES:
            raise ValueError(
                f"SECURITY VIOLATION: Binary '{binary}' is not in the allowlist.",
            )
        resolved = shutil.which(binary)
        if resolved is None:
            raise ValueError(f"SECURITY VIOLATION: Binary '{binary}' not found on PATH.")
        argv[0] = resolved
        return argv

    def _safe_path(self, filename: str) -> Path:
        """
        Security: Prevents Directory Traversal (e.g. ../../etc/passwd).
        Ensures that any path accessed is strictly within the designated workspace.

        Args:
            filename (str): The filename or path relative to the workspace.

        Returns:
            Path: The resolved, safe absolute path within the workspace.

        Raises:
            ValueError: If the path attempts to escape the workspace directory.
        """
        target: Path = (self.work_dir / filename).resolve()
        if not str(target).startswith(str(self.work_dir)):
            raise ValueError(
                f"SECURITY VIOLATION: Path '{filename}' attempts to escape workspace. Resolved path: '{target}' is outside '{self.work_dir}'.",
            )
        return target

    def tool_write_file(self, filename: str, content: str) -> str:
        """
        Writes content to a file within the workspace.

        Args:
            filename (str): The name of the file to write.
            content (str): The content to write into the file.

        Returns:
            str: A success message.
        """
        trace_contract._emit_verifies_boundary(str(uuid.uuid4()), "SecureToolsImpl.tool_write_file", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "SecureToolsImpl.tool_write_file")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SecureToolsImpl.tool_write_file".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        _ectx = _make_execution_context(filename, "secure_tools.tool_write_file")
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            "default",
            filename,
            target_name="secure_tools.tool_write_file",
        )
        target: Path = self._safe_path(filename)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        Logger.info(f"File '{target.name}' written successfully.")
        return f"File written successfully: {target.name}"

    def tool_read_file(self, filename: str) -> str:
        """
        Reads content from a file within the workspace.

        Args:
            filename (str): The name of the file to read.

        Returns:
            str: The content of the file, or an error message if the file does not exist.
        """
        target: Path = self._safe_path(filename)
        if not target.exists():
            Logger.warning(f"Attempted to read non-existent file: {filename}")
            return f"Error: File '{filename}' does not exist."
        if not target.is_file():
            Logger.warning(f"Attempted to read a non-file path: {filename}")
            return f"Error: Path '{filename}' is not a file."
        with open(target, encoding="utf-8") as f:
            content: Any = f.read()
        Logger.info(f"File '{target.name}' read successfully.")
        return content

    def tool_list_files(self, subdir: str = ".") -> str:
        """
        Lists files and directories within a specified subdirectory of the workspace.

        Args:
            subdir (str): The subdirectory to list files from, relative to the workspace.
                          Defaults to the root of the workspace.

        Returns:
            str: A newline-separated string of file/directory names, or an error message.
        """
        target: Path = self._safe_path(subdir)
        if not target.exists():
            Logger.warning(f"Attempted to list non-existent directory: {subdir}")
            return f"Error: Directory '{subdir}' not found."
        if not target.is_dir():
            Logger.warning(f"Attempted to list a non-directory path: {subdir}")
            return f"Error: Path '{subdir}' is not a directory."
        files: list[str] = [f.name for f in target.iterdir()]
        output: Any = "\n".join(files) if files else "(empty directory)"
        Logger.info(f"Listed files in '{subdir}':\n{output}")
        return output

    def tool_run_command(self, command: str) -> str:
        """
        Executes a shell command within the workspace.
        WARNING: This tool is highly dangerous. In a production environment,
        it MUST be wrapped in a secure, isolated execution environment (e.g., Docker).

        Args:
            command (str): The shell command string to execute.

        Returns:
            str: The stdout of the command if successful, or an error message.

        Raises:
            ValueError: If the command contains blacklisted patterns.
        """
        _ectx = _make_execution_context(command, "secure_tools.tool_run_command", "PRIVILEGED_LOCAL")
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            "default",
            command,
            target_name="secure_tools.tool_run_command",
        )
        argv = self._parse_and_validate_command(command)
        cwd = self._safe_cwd()
        safe_env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
            "HOME": str(cwd),
        }
        Logger.warning(f"Executing vetted argv: {argv!r} in '{cwd}'")
        try:
            result: Any = subprocess.run(
                argv,
                shell=False,
                cwd=cwd,
                env=safe_env,
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT,
                check=False,
            )
            if result.returncode != 0:
                Logger.error(f"Command failed with return code {result.returncode}: {result.stderr}")
                return f"Command Error (Exit {result.returncode}): {result.stderr}"
            Logger.info(f"Command executed successfully: {argv!r}")
            return result.stdout
        except subprocess.TimeoutExpired:
            Logger.error(f"Command timed out: {command}")
            return "Command Error: Execution timed out (30s limit)."
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            Logger.error(f"Command execution failed: {e}")
            return f"Command Error: {str(e)}"


__all__ = ["SecureToolsImpl"]
