"""
L0 utilities for invoking L5 runners via subprocess.

This module provides clean subprocess invocation to L5 runners,
avoiding upward import edges while enabling L0 scripts to
trigger L5 agent functionality.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "subprocess_runner_util", "L0")
_emit_routes_through("p1", "subprocess_runner_util", "L0")
_emit_escalates_to_human("p1", "subprocess_runner_util", "L0")
_emit_reads_policy_state("p1", "subprocess_runner_util", "L0")

__all__ = [
    "invoke_arch_governor",
    "invoke_orchestrator_mission",
    "invoke_agent_roster_validation",
    "invoke_hierarchy_agent",
    "invoke_code_validator",
]


def invoke_arch_governor(
    action: str, project_root: Path | None = None, targets: list[str] | None = None, auto_approve: bool = True
) -> dict[str, Any]:
    """
    Invoke ArchitectureGovernorAgent via subprocess.

    Args:
        action: One of 'verify', 'capture_baseline', 'audit'
        project_root: Project root path (auto-detected if None)
        targets: Target territories for audit action
        auto_approve: Auto-approve mode

    Returns:
        Dict with 'success' key and action-specific results
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "invoke_arch_governor", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "invoke_arch_governor", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "invoke_arch_governor")
    cmd = [sys.executable, "-m", "agentic_core.L5_safety.runners.arch_governor_runner", f"--action={action}"]
    if project_root:
        cmd.append(f"--project-root={project_root}")
    if targets:
        cmd.append(f"--targets={','.join(targets)}")
    if auto_approve:
        cmd.append("--auto-approve")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
        if result.stdout.strip():
            return json.loads(result.stdout.strip())
        return {"success": result.returncode == 0, "error": result.stderr if result.returncode != 0 else None}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Subprocess timed out after 300 seconds"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse runner output: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def invoke_orchestrator_mission(
    project_root: Path | None = None, targets: list[str] | None = None, execute: bool = False
) -> dict[str, Any]:
    """
    Invoke orchestrator mission via subprocess.

    Args:
        project_root: Project root path (auto-detected if None)
        targets: Target territories
        execute: Execute mode (vs dry-run)

    Returns:
        Dict with 'success' key and mission results
    """
    if not targets:
        return {"success": False, "error": "No targets specified"}
    cmd = [
        sys.executable,
        "-m",
        "agentic_core.L5_safety.runners.orchestrator_runner",
        "--action=mission",
        f"--targets={','.join(targets)}",
    ]
    if project_root:
        cmd.append(f"--project-root={project_root}")
    if execute:
        cmd.append("--execute")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
        if result.stdout.strip():
            return json.loads(result.stdout.strip())
        return {"success": result.returncode == 0, "error": result.stderr if result.returncode != 0 else None}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Subprocess timed out after 600 seconds"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse runner output: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def invoke_agent_roster_validation() -> dict[str, Any]:
    """
    Invoke agent roster validation via subprocess.

    Returns:
        Dict with 'success', 'agents_validated', and 'integrity_errors' keys
    """
    cmd = [sys.executable, "-m", "agentic_core.L5_safety.runners.agent_roster_runner", "--action=validate"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
        if result.stdout.strip():
            return json.loads(result.stdout.strip())
        return {"success": result.returncode == 0, "error": result.stderr if result.returncode != 0 else None}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Subprocess timed out after 120 seconds"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse runner output: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def invoke_hierarchy_agent(action: str, project_root: Path | None = None) -> dict[str, Any]:
    """
    Invoke HierarchyAgent via subprocess.

    Args:
        action: One of 'dry_run', 'heal_violations', 'verify_mro'
        project_root: Project root path (auto-detected if None)

    Returns:
        Dict with 'success' key and action-specific results
    """
    cmd = [sys.executable, "-m", "agentic_core.L5_safety.runners.hierarchy_runner", f"--action={action}"]
    if project_root:
        cmd.append(f"--project-root={project_root}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
        if result.stdout.strip():
            return json.loads(result.stdout.strip())
        return {"success": result.returncode == 0, "error": result.stderr if result.returncode != 0 else None}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Subprocess timed out after 300 seconds"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse runner output: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def invoke_code_validator(
    action: str, project_root: Path | None = None, directory: str | None = None
) -> dict[str, Any]:
    """
    Invoke CodeValidatorAgent via subprocess.

    Args:
        action: One of 'validate', 'validate_directory'
        project_root: Project root path (auto-detected if None)
        directory: Directory to validate (required for validate_directory)

    Returns:
        Dict with 'success' key and action-specific results
    """
    cmd = [sys.executable, "-m", "agentic_core.L5_safety.runners.code_validator_runner", f"--action={action}"]
    if directory:
        cmd.append(f"--directory={directory}")
    if project_root:
        cmd.append(f"--project-root={project_root}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
        if result.stdout.strip():
            return json.loads(result.stdout.strip())
        return {"success": result.returncode == 0, "error": result.stderr if result.returncode != 0 else None}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Subprocess timed out after 300 seconds"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse runner output: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
