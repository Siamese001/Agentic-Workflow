"""
Safe subprocess wrapper that enforces mutation fence protection.
"""

import subprocess
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.enforcement.mutation_prohibition import enforce_protected_root
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "safe_subprocess")
_emit_applies_guardrail("p0", "safe_subprocess", "p0_governance")


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_invoke_authorize_and_execute", "state_snapshot")
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L2_execution.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id="safe_subprocess",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.PRIVILEGED_LOCAL,
    )


def safe_subprocess_run(
    argv: list[str],
    *,
    cwd: str | Path | None = None,
    capture_output: bool = False,
    text: bool = False,
    check: bool = False,
    allow_protected_root_mutation: bool = False,
    **kwargs: Any,
) -> subprocess.CompletedProcess:
    """
    Safe subprocess.run wrapper with mutation fence protection.

    Args:
        argv: Command arguments as a list (no shell)
        cwd: Working directory for the command
        capture_output: Whether to capture stdout/stderr
        text: Whether to decode output as text
        check: Whether to raise exception on non-zero exit
        allow_protected_root_mutation: Whether to allow commands that can mutate protected roots
        **kwargs: Additional arguments passed to subprocess.run

    Returns:
        subprocess.CompletedProcess result

    Raises:
        RuntimeError: If command attempts protected root mutation without override
    """
    dangerous_commands = {
        "git",
        "rm",
        "mv",
        "cp",
        "chmod",
        "chown",
        "touch",
        "mkdir",
        "rmdir",
        "find",
        "sed",
        "awk",
        "perl",
        "python",
        "pip",
        "npm",
        "yarn",
    }
    if argv and argv[0] in dangerous_commands:
        if not allow_protected_root_mutation:
            if cwd:
                cwd_path = Path(cwd).resolve()
                if enforce_protected_root(cwd_path, operation="check"):
                    raise RuntimeError(
                        f"Command '{argv[0]}' may affect protected root {cwd_path}. Use allow_protected_root_mutation=True if intentional."
                    )
    if not isinstance(argv, list):
        raise TypeError("argv must be a list of strings")
    _ectx = _make_execution_context(" ".join(str(a) for a in argv), "safe_subprocess.safe_subprocess_run")
    _invoke_authorize_and_execute(
        _ectx,
        lambda p: p,
        "default",
        " ".join(str(a) for a in argv),
        target_name="safe_subprocess.safe_subprocess_run",
    )
    return subprocess.run(argv, cwd=cwd, capture_output=capture_output, text=text, check=check, **kwargs)


def safe_subprocess_call(
    argv: list[str],
    *,
    cwd: str | Path | None = None,
    allow_protected_root_mutation: bool = False,
    **kwargs: Any,
) -> int:
    """Safe subprocess.call wrapper."""
    result = safe_subprocess_run(
        argv, cwd=cwd, allow_protected_root_mutation=allow_protected_root_mutation, **kwargs
    )
    return result.returncode


def safe_subprocess_check_call(
    argv: list[str],
    *,
    cwd: str | Path | None = None,
    allow_protected_root_mutation: bool = False,
    **kwargs: Any,
) -> None:
    """Safe subprocess.check_call wrapper."""
    safe_subprocess_run(
        argv, cwd=cwd, check=True, allow_protected_root_mutation=allow_protected_root_mutation, **kwargs
    )


def safe_subprocess_check_output(
    argv: list[str],
    *,
    cwd: str | Path | None = None,
    text: bool = True,
    allow_protected_root_mutation: bool = False,
    **kwargs: Any,
) -> str | bytes:
    """Safe subprocess.check_output wrapper."""
    result = safe_subprocess_run(
        argv,
        cwd=cwd,
        capture_output=True,
        text=text,
        allow_protected_root_mutation=allow_protected_root_mutation,
        **kwargs,
    )
    return result.stdout


def safe_subprocess_popen(
    argv: list[str],
    *,
    cwd: str | Path | None = None,
    allow_protected_root_mutation: bool = False,
    **kwargs: Any,
) -> subprocess.Popen:
    """Safe subprocess.Popen wrapper."""
    dangerous_commands = {
        "git",
        "rm",
        "mv",
        "cp",
        "chmod",
        "chown",
        "touch",
        "mkdir",
        "rmdir",
        "find",
        "sed",
        "awk",
        "perl",
        "python",
        "pip",
        "npm",
        "yarn",
    }
    if argv and argv[0] in dangerous_commands:
        if not allow_protected_root_mutation:
            if cwd:
                cwd_path = Path(cwd).resolve()
                if enforce_protected_root(cwd_path, operation="check"):
                    raise RuntimeError(
                        f"Command '{argv[0]}' may affect protected root {cwd_path}. Use allow_protected_root_mutation=True if intentional."
                    )
    if not isinstance(argv, list):
        raise TypeError("argv must be a list of strings")
    return subprocess.Popen(argv, cwd=cwd, **kwargs)
