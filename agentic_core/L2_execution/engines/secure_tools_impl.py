from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_applies_guardrail("p0", "secure_tools_impl", "p0_governance")
_emit_snapshots_state("p0", "secure_tools_impl", "state_snapshot")

"\nSecure Tools - Atomic Module\nExtracted from ActionNode.py via Atomic Fission Protocol\nImplements sandboxed file operations and command execution\n"
import logging
import subprocess
import uuid
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_verifies_boundary,
)


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str, action_class_name: str = "MUTATION"):
    from agentic_core.L2_execution.context.execution_context import (  # noqa: PLC0415
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

    def __init__(self, work_dir: Path):
        """
        Initialize secure tools.

        Args:
            work_dir (Path): Working directory for sandboxing
        """
        self.work_dir = work_dir

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
                f"SECURITY VIOLATION: Path '{filename}' attempts to escape workspace. Resolved path: '{target}' is outside '{self.work_dir}'."
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
        _emit_verifies_boundary(str(uuid.uuid4()), "SecureToolsImpl.tool_write_file", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "SecureToolsImpl.tool_write_file")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SecureToolsImpl.tool_write_file".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        if any(b in command for b in self.BLACKLIST_COMMANDS):
            Logger.error(f"SECURITY VIOLATION: Command '{command}' contains blacklisted patterns.")
            raise ValueError(
                "SECURITY VIOLATION: Command contains blacklisted patterns. Refusing to execute."
            )
        Logger.warning(f"Executing potentially dangerous command: '{command}' in '{self.work_dir}'")
        try:
            result: Any = subprocess.run(
                command,
                shell=True,
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT,
            )
            if result.returncode != 0:
                Logger.error(f"Command failed with return code {result.returncode}: {result.stderr}")
                return f"Command Error (Exit {result.returncode}): {result.stderr}"
            Logger.info(f"Command executed successfully: {command}")
            return result.stdout
        except subprocess.TimeoutExpired:
            Logger.error(f"Command timed out: {command}")
            return "Command Error: Execution timed out (30s limit)."
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Command execution failed: {e}")
            return f"Command Error: {str(e)}"


__all__ = ["SecureToolsImpl"]
