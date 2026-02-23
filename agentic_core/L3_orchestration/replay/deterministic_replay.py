"""
Deterministic Replay Engine - Record and Replay Module

Provides immutable data structures and functions for recording and replaying
command executions deterministically for governance verification.

This module performs NO file writes or mutations - it only returns data
structures that callers can persist as needed.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime

# =============================================================================
# Data Structures (Frozen/Immutable)
# =============================================================================


@dataclass(frozen=True)
class ReplayCommand:
    """Immutable command definition for replay."""

    argv: list[str]
    cwd: str
    env_allowlist: dict[str, str]
    timeout_s: int = 300


@dataclass(frozen=True)
class ReplayResult:
    """Immutable result of a command execution."""

    exit_code: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class ReplayRecord:
    """Immutable record of command executions for replay."""

    version: int = 1
    created_utc: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    commands: list[ReplayCommand] = field(default_factory=list)
    results: list[ReplayResult] = field(default_factory=list)
    hashes: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ComparisonResult:
    """Result of replay comparison."""

    is_match: bool
    mismatches: list[str] = field(default_factory=list)
    first_diff_summary: str = ""


# =============================================================================
# Environment Allowlist
# =============================================================================

_ENV_ALLOWLIST = {
    "AGENTIC_BYPASS_LONGPATHS_CHECK",
    "PYTHONUTF8",
    "PYTHONPATH",
    "PATH",
}

# =============================================================================
# Core Functions
# =============================================================================


def _hash_command_result(command: ReplayCommand, result: ReplayResult) -> str:
    """Compute SHA256 hash of command and result for integrity verification."""
    data = {
        "argv": command.argv,
        "cwd": command.cwd,
        "env_allowlist": command.env_allowlist,
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    data_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data_str.encode("utf-8")).hexdigest()


def _filter_env_vars() -> dict[str, str]:
    """Filter environment variables to only allowlisted keys."""
    filtered = {}
    for key, value in os.environ.items():
        if key in _ENV_ALLOWLIST:
            filtered[key] = value
    return filtered


def run_and_record(commands: list[ReplayCommand]) -> ReplayRecord:
    """Execute commands and record results deterministically.

    Args:
        commands: List of commands to execute

    Returns:
        ReplayRecord with commands, results, and per-command hashes

    Raises:
        RuntimeError: If any argv0 contains pwsh/powershell
    """
    results = []
    hashes = {}

    for command in commands:
        # Guard against PowerShell usage
        if len(command.argv) > 0 and ("pwsh" in command.argv[0] or "powershell" in command.argv[0]):
            raise RuntimeError(f"PowerShell usage forbidden in argv0: {command.argv[0]}")

        # Prepare environment (only allowlisted vars)
        env = _filter_env_vars()
        env.update(command.env_allowlist)

        # Execute command
        result = subprocess.run(
            command.argv,
            shell=False,
            text=True,
            capture_output=True,
            cwd=command.cwd,
            env=env,
            timeout=command.timeout_s,
        )

        replay_result = ReplayResult(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )

        results.append(replay_result)

        # Compute hash for integrity
        cmd_hash = _hash_command_result(command, replay_result)
        hashes[f"cmd_{len(results)}"] = cmd_hash

    return ReplayRecord(
        commands=commands,
        results=results,
        hashes=hashes,
    )


def record_to_json(record: ReplayRecord) -> str:
    """Serialize ReplayRecord to deterministic JSON.

    Returns:
        JSON string with sorted keys and stable formatting
    """
    return json.dumps(
        {
            "version": record.version,
            "created_utc": record.created_utc,
            "commands": [
                {
                    "argv": cmd.argv,
                    "cwd": cmd.cwd,
                    "env_allowlist": cmd.env_allowlist,
                    "timeout_s": cmd.timeout_s,
                }
                for cmd in record.commands
            ],
            "results": [
                {
                    "exit_code": res.exit_code,
                    "stdout": res.stdout,
                    "stderr": res.stderr,
                }
                for res in record.results
            ],
            "hashes": record.hashes,
        },
        sort_keys=True,
        indent=2,
    )


def record_from_json(json_str: str) -> ReplayRecord:
    """Deserialize JSON string to ReplayRecord."""
    data = json.loads(json_str)

    commands = [
        ReplayCommand(
            argv=cmd["argv"],
            cwd=cmd["cwd"],
            env_allowlist=cmd["env_allowlist"],
            timeout_s=cmd.get("timeout_s", 300),
        )
        for cmd in data["commands"]
    ]

    results = [
        ReplayResult(
            exit_code=res["exit_code"],
            stdout=res["stdout"],
            stderr=res["stderr"],
        )
        for res in data["results"]
    ]

    return ReplayRecord(
        version=data["version"],
        created_utc=data["created_utc"],
        commands=commands,
        results=results,
        hashes=data["hashes"],
    )


# =============================================================================
# Replay and Comparison
# =============================================================================


def _normalize_output(output: str) -> str:
    """Normalize output by stripping timestamps and absolute paths."""
    # Strip ISO timestamps (e.g., 2026-02-23T04:18:00.123Z)
    output = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z", "<TIMESTAMP>", output)

    # Strip common log datetime prefixes (e.g., 2026-02-23 04:18:00,123)
    output = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}", "<TIMESTAMP>", output)

    # Replace absolute repo root paths with <REPO_ROOT>
    # guardian: allow-path-fragility
    # guardian: allow-path-fragility
    repo_root = os.path.abspath(os.getcwd())
    # Normalize path separators for cross-platform consistency
    repo_root_normalized = repo_root.replace("\\", "/")
    output = output.replace(repo_root, "<REPO_ROOT>")
    output = output.replace(repo_root_normalized, "<REPO_ROOT>")

    # Also handle Windows drive letters (C:/...)
    output = re.sub(r"[A-Za-z]:/[^ \n\r]*", "<ABSOLUTE_PATH>", output)

    return output


def replay_and_compare(record: ReplayRecord) -> ComparisonResult:
    """Replay commands and compare with original results.

    Args:
        record: Original record to replay

    Returns:
        ComparisonResult with match status and any mismatches
    """
    if len(record.commands) != len(record.results):
        return ComparisonResult(
            is_match=False,
            mismatches=["Command and result count mismatch"],
        )

    mismatches = []
    first_diff_lines = []

    for i, (command, original_result) in enumerate(zip(record.commands, record.results)):
        # Re-execute command
        try:
            env = _filter_env_vars()
            env.update(command.env_allowlist)

            result = subprocess.run(
                command.argv,
                shell=False,
                text=True,
                capture_output=True,
                cwd=command.cwd,
                env=env,
                timeout=command.timeout_s,
            )

            current_result = ReplayResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )

            # Compare exit codes
            if current_result.exit_code != original_result.exit_code:
                mismatches.append(
                    f"Command {i + 1}: Exit code mismatch "
                    f"(original={original_result.exit_code}, current={current_result.exit_code})"
                )

            # Compare normalized outputs
            orig_stdout_norm = _normalize_output(original_result.stdout)
            curr_stdout_norm = _normalize_output(current_result.stdout)

            if orig_stdout_norm != curr_stdout_norm:
                mismatches.append(f"Command {i + 1}: Stdout mismatch after normalization")
                if not first_diff_lines:
                    # Generate bounded diff summary
                    orig_lines = orig_stdout_norm.splitlines()
                    curr_lines = curr_stdout_norm.splitlines()
                    for j, (orig, curr) in enumerate(zip(orig_lines, curr_lines)):
                        if orig != curr:
                            first_diff_lines.extend(
                                [
                                    f"First difference at line {j + 1}:",
                                    f"Original: {orig}",
                                    f"Current:  {curr}",
                                ]
                            )
                            break

            orig_stderr_norm = _normalize_output(original_result.stderr)
            curr_stderr_norm = _normalize_output(current_result.stderr)

            if orig_stderr_norm != curr_stderr_norm:
                mismatches.append(f"Command {i + 1}: Stderr mismatch after normalization")

        except subprocess.TimeoutExpired:
            mismatches.append(f"Command {i + 1}: Timeout during replay")
        # guardian: allow-silent-swallower
        except Exception as e:
            mismatches.append(f"Command {i + 1}: Exception during replay: {e}")

    return ComparisonResult(
        is_match=len(mismatches) == 0,
        mismatches=mismatches,
        first_diff_summary="\n".join(first_diff_lines[:200]),  # Bounded to 200 lines
    )


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "ReplayCommand",
    "ReplayResult",
    "ReplayRecord",
    "ComparisonResult",
    "run_and_record",
    "record_to_json",
    "record_from_json",
    "replay_and_compare",
]
