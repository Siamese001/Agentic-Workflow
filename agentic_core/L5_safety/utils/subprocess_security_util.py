from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "subprocess_security_util")
emit_determinism_digest("p0", "subprocess_security_util")

_emit_dispatches_healing_run("p1", "subprocess_security_util", "L5")
_emit_routes_through("p1", "subprocess_security_util", "L5")
_emit_escalates_to_human("p1", "subprocess_security_util", "L5")
_emit_reads_policy_state("p1", "subprocess_security_util", "L5")
_emit_authorize_and_execute("p2", "subprocess_security_util", "execution_auth")
_emit_validates_capability("p2", "subprocess_security_util", "capability_check")
_emit_routes_to_capability("p2", "subprocess_security_util", "capability_route")
_emit_writes_via_uwg("p2", "subprocess_security_util", "uwg_write")
_emit_blocks_direct_write("p2", "subprocess_security_util", "direct_write_block")
_emit_records_tool_invocation("p2", "subprocess_security_util", "tool_invocation")
_emit_captures_execution_output("p2", "subprocess_security_util", "exec_output")
_emit_dispatches_agent("p3", "subprocess_security_util", "agent_dispatch")
_emit_coordinates_agents("p3", "subprocess_security_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "subprocess_security_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "subprocess_security_util", "healing_outcome")
_emit_escalates_failure("p3", "subprocess_security_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "subprocess_security_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "subprocess_security_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "subprocess_security_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "subprocess_security_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "subprocess_security_util", "eval_metric")
_emit_stores_embedding("p4", "subprocess_security_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "subprocess_security_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "subprocess_security_util", "exec_snapshot_link")

"\nSecurity Utilities for Agentic Workflow\n\nZero-Trust subprocess execution wrapper with comprehensive input validation,\ninjection prevention, and observability integration.\n\nZero-Ambiguity Standard: Renamed from SecurityViolationError.py to subprocess_security_util.py\nCategory: UTILITY (Security utilities, not just an Error class)\n\nCreated: 2026-01-20\nPurpose: Harden all subprocess calls against shell injection attacks\n"
import logging
import re
import subprocess
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

Logger = logging.getLogger(__name__)
SHELL_METACHARACTERS = {
    "|": "pipe operator",
    "&&": "AND operator",
    "||": "OR operator",
    "`": "backtick command substitution",
    "$(": "command substitution",
    "&": "background execution",
}


def _is_shell_injection_risk(arg: str) -> bool:
    """
    Determine if an argument poses a shell injection risk.

    Python code via -c flag is safe because shell=False prevents interpretation.
    We only block patterns that could be exploited if shell=True were used.

    Args:
        arg: Command argument to check

    Returns:
        True if injection risk detected, False otherwise
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_is_shell_injection_risk", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_is_shell_injection_risk", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "_is_shell_injection_risk")
    if arg.startswith("import ") or "import " in arg[:50]:
        return False
    if "|" in arg and "||" not in arg:
        return True
    if "&&" in arg:
        return True
    if "||" in arg:
        return True
    if "`" in arg:
        return True
    if "$(" in arg:
        return True
    if re.search(">\\s*[/\\\\]", arg):
        return True
    if re.search("<\\s*[/\\\\]", arg):
        return True
    if arg.strip().endswith("&"):
        return True
    return False


INJECTION_REGEX = re.compile("\\||&&|\\|\\||`|\\$\\(|>\\s*[/\\\\]|<\\s*[/\\\\]|&\\s*$")


class SecurityViolationError(Exception):
    """Raised when a security violation is detected in subprocess arguments."""

    pass


def safe_execute(
    args: list[str],
    cwd: str | Path | None = None,
    timeout: int | None = None,
    capture_output: bool = True,
    text: bool = True,
    check: bool = True,
    env: dict[str, str] | None = None,
    input_data: str | None = None,
) -> subprocess.CompletedProcess:
    """
    Hardened wrapper for subprocess.run with zero-trust security constraints.

    **Security Guarantees:**
    - NO shell execution (shell=False enforced)
    - List-only arguments (no string commands)
    - Input sanitization (blocks injection characters)
    - Comprehensive logging for observability
    - Timeout enforcement

    Args:
        args: Command and arguments as a list of strings (REQUIRED)
        cwd: Working directory for command execution
        timeout: Maximum execution time in seconds (default: None)
        capture_output: Capture stdout/stderr (default: True)
        text: Return output as text instead of bytes (default: True)
        check: Raise CalledProcessError on non-zero exit (default: True)
        env: Environment variables dict (default: None = inherit)
        input_data: Data to send to stdin (default: None)

    Returns:
        subprocess.CompletedProcess with stdout, stderr, returncode

    Raises:
        SecurityViolationError: If injection patterns detected
        TypeError: If args is not a list
        subprocess.CalledProcessError: If check=True and command fails
        subprocess.TimeoutExpired: If timeout exceeded

    Example:
        >>> result = safe_execute(['git', 'status'])
        >>> result = safe_execute(['python', 'script.py'], timeout=DEFAULT_TIMEOUT)
        >>> result = safe_execute(['ls', '-la'], cwd='/tmp')
    """
    if not isinstance(args, list):
        raise TypeError(
            f"safe_execute requires args as List[str], got {type(args).__name__}. This prevents accidental shell injection via string commands."
        )
    if not args:
        raise ValueError("safe_execute requires non-empty args list")
    for i, arg in enumerate(args):
        if not isinstance(arg, str):
            raise TypeError(f"Argument {i} must be str, got {type(arg).__name__}: {arg}")
        if _is_shell_injection_risk(arg):
            truncated = arg[:100] + "..." if len(arg) > 100 else arg
            raise SecurityViolationError(
                f"Shell injection pattern detected in argument {i}: '{truncated}'\nBlocked patterns: | && || ` $( > /path < /path & (at end)\nThis is a security violation. Use safe alternatives or file-based I/O."
            )
    if cwd is not None:
        cwd_path = Path(cwd)
        if not cwd_path.exists():
            Logger.warning(f"[Security] Working directory does not exist: {cwd}")
        cwd = str(cwd_path)
    cmd_str = " ".join(args)
    Logger.info(f"[Security] Executing safe command: {cmd_str}")
    if cwd:
        Logger.debug(f"[Security] Working directory: {cwd}")
    if timeout:
        Logger.debug(f"[Security] Timeout: {timeout}s")
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            timeout=timeout,
            capture_output=capture_output,
            text=text,
            check=check,
            env=env,
            input=input_data,
            shell=False,
        )
        Logger.info(f"[Security] Command completed successfully: {args[0]} (exit code: {result.returncode})")
        return result
    except subprocess.CalledProcessError as e:
        Logger.error(
            f"[Security] Command failed: {cmd_str}\nExit code: {e.returncode}\nStderr: {(e.stderr[:500] if e.stderr else 'N/A')}"
        )
        raise
    except subprocess.TimeoutExpired:
        Logger.error(f"[Security] Command timeout after {timeout}s: {cmd_str}")
        raise
    except Exception as e:
        Logger.error(f"[Security] Unexpected error executing command: {cmd_str}\nError: {e}")
        raise


def safe_popen(
    args: list[str],
    cwd: str | Path | None = None,
    stdout: int | None = subprocess.PIPE,
    stderr: int | None = subprocess.PIPE,
    text: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.Popen:
    """
    Hardened wrapper for subprocess.Popen with zero-trust security constraints.

    Use this for long-running processes that need streaming output.
    For simple command execution, prefer safe_execute().

    Args:
        args: Command and arguments as a list of strings (REQUIRED)
        cwd: Working directory for command execution
        stdout: stdout handling (default: PIPE)
        stderr: stderr handling (default: PIPE)
        text: Return output as text instead of bytes (default: True)
        env: Environment variables dict (default: None = inherit)

    Returns:
        subprocess.Popen object for process management

    Raises:
        SecurityViolationError: If injection patterns detected
        TypeError: If args is not a list

    Example:
        >>> proc = safe_popen(['python', 'server.py'])
        >>> for line in proc.stdout:
        ...     print(line, end='')
        >>> proc.wait()
    """
    if not isinstance(args, list):
        raise TypeError(f"safe_popen requires args as List[str], got {type(args).__name__}")
    if not args:
        raise ValueError("safe_popen requires non-empty args list")
    for i, arg in enumerate(args):
        if not isinstance(arg, str):
            raise TypeError(f"Argument {i} must be str, got {type(arg).__name__}: {arg}")
        if _is_shell_injection_risk(arg):
            truncated = arg[:100] + "..." if len(arg) > 100 else arg
            raise SecurityViolationError(f"Shell injection pattern detected in argument {i}: '{truncated}'")
    if cwd is not None:
        cwd = str(Path(cwd))
    cmd_str = " ".join(args)
    Logger.info(f"[Security] Starting Popen process: {cmd_str}")
    try:
        proc = subprocess.Popen(args, cwd=cwd, stdout=stdout, stderr=stderr, text=text, env=env, shell=False)
        Logger.info(f"[Security] Popen process started: PID {proc.pid}")
        return proc
    except Exception as e:
        Logger.error(f"[Security] Failed to start Popen process: {cmd_str}\nError: {e}")
        raise


def validate_command_whitelist(args: list[str], allowed_commands: list[str]) -> bool:
    """
    Validate that the command is in an allowed whitelist.

    Use this for additional security when only specific commands should be allowed.

    Args:
        args: Command and arguments list
        allowed_commands: List of allowed command names (e.g., ['git', 'python', 'black'])

    Returns:
        True if command is allowed, False otherwise

    Example:
        >>> args = ['git', 'status']
        >>> if validate_command_whitelist(args, ['git', 'python']):
        ...     safe_execute(args)
    """
    if not args:
        return False
    command = args[0]
    if "/" in command or "\\" in command:
        command = Path(command).name
    if command.endswith(".exe"):
        command = command[:-4]
    is_allowed = command in allowed_commands
    if not is_allowed:
        Logger.warning(f"[Security] Command '{command}' not in whitelist: {allowed_commands}")
    return is_allowed


# guardian: allow-magic-config
def safe_git_execute(
    git_args: list[str], repo_root: str | Path | None = None, timeout: int = 30
) -> subprocess.CompletedProcess:
    """
    Convenience wrapper for safe git command execution.

    Args:
        git_args: Git subcommand and arguments (without 'git' prefix)
        repo_root: Repository root directory (default: current directory)
        timeout: Command timeout in seconds (default: 30)

    Returns:
        subprocess.CompletedProcess

    Example:
        >>> result = safe_git_execute(['status'])
        >>> result = safe_git_execute(['commit', '-m', 'message'], repo_root='/path/to/repo')
    """
    args = ["git"] + git_args
    return safe_execute(args, cwd=repo_root, timeout=timeout)
