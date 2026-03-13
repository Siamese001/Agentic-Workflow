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


@dataclass(frozen=True)
class ReplayMetrics:
    """Deterministic performance metrics for replay operations."""

    per_command_bytes_out: list[int] = field(default_factory=list)
    per_command_bytes_err: list[int] = field(default_factory=list)
    total_bytes_out: int = 0
    total_bytes_err: int = 0


@dataclass(frozen=True)
class ReplayCommand:
    """Immutable command definition for replay."""

    argv: list[str]
    cwd: str
    env_allowlist: dict[str, str]
    timeout_s: int = 300
    max_stdout_bytes: int = 1024 * 1024
    max_stderr_bytes: int = 1024 * 1024


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
    metrics: ReplayMetrics | None = None


@dataclass(frozen=True)
class ComparisonResult:
    """Result of replay comparison."""

    is_match: bool
    mismatches: list[str] = field(default_factory=list)
    first_diff_summary: str = ""


_ENV_ALLOWLIST = {"AGENTIC_BYPASS_LONGPATHS_CHECK", "PYTHONUTF8", "PYTHONPATH", "PATH"}


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


def _truncate_if_needed(text: str, max_bytes: int) -> tuple[str, bool]:
    """Truncate text if it exceeds max_bytes deterministically.

    Args:
        text: Text to potentially truncate
        max_bytes: Maximum allowed bytes

    Returns:
        Tuple of (truncated_text, was_truncated)
    """
    text_bytes = text.encode("utf-8")
    if len(text_bytes) <= max_bytes:
        return (text, False)
    suffix = f"...<TRUNCATED {len(text_bytes) - max_bytes} BYTES>"
    suffix_bytes = suffix.encode("utf-8")
    allowed_text_bytes = max_bytes - len(suffix_bytes)
    if allowed_text_bytes <= 0:
        return (suffix, True)
    truncated_bytes = text_bytes[:allowed_text_bytes]
    try:
        truncated_text = truncated_bytes.decode("utf-8")
    except UnicodeDecodeError:
        truncated_text = truncated_bytes.decode("utf-8", errors="replace")
        truncated_text = truncated_text.rstrip("�")
    return (truncated_text + suffix, True)


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
    per_command_bytes_out = []
    per_command_bytes_err = []
    for command in commands:
        if len(command.argv) > 0 and ("pwsh" in command.argv[0] or "powershell" in command.argv[0]):
            raise RuntimeError(f"PowerShell usage forbidden in argv0: {command.argv[0]}")
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
        truncated_stdout, stdout_truncated = _truncate_if_needed(result.stdout, command.max_stdout_bytes)
        truncated_stderr, stderr_truncated = _truncate_if_needed(result.stderr, command.max_stderr_bytes)
        replay_result = ReplayResult(
            exit_code=result.returncode, stdout=truncated_stdout, stderr=truncated_stderr
        )
        results.append(replay_result)
        per_command_bytes_out.append(len(replay_result.stdout.encode("utf-8")))
        per_command_bytes_err.append(len(replay_result.stderr.encode("utf-8")))
        cmd_hash = _hash_command_result(command, replay_result)
        hashes[f"cmd_{len(results)}"] = cmd_hash
    metrics = ReplayMetrics(
        per_command_bytes_out=per_command_bytes_out,
        per_command_bytes_err=per_command_bytes_err,
        total_bytes_out=sum(per_command_bytes_out),
        total_bytes_err=sum(per_command_bytes_err),
    )
    return ReplayRecord(commands=commands, results=results, hashes=hashes, metrics=metrics)


def record_to_json(record: ReplayRecord) -> str:
    """Serialize ReplayRecord to deterministic JSON.

    Returns:
        JSON string with sorted keys and stable formatting
    """
    data = {
        "version": record.version,
        "created_utc": record.created_utc,
        "commands": [
            {"argv": cmd.argv, "cwd": cmd.cwd, "env_allowlist": cmd.env_allowlist, "timeout_s": cmd.timeout_s}
            for cmd in record.commands
        ],
        "results": [
            {"exit_code": res.exit_code, "stdout": res.stdout, "stderr": res.stderr} for res in record.results
        ],
        "hashes": record.hashes,
    }
    if record.metrics is not None:
        data["metrics"] = {
            "per_command_bytes_out": record.metrics.per_command_bytes_out,
            "per_command_bytes_err": record.metrics.per_command_bytes_err,
            "total_bytes_out": record.metrics.total_bytes_out,
            "total_bytes_err": record.metrics.total_bytes_err,
        }
    return json.dumps(data, sort_keys=True, indent=2)


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
        ReplayResult(exit_code=res["exit_code"], stdout=res["stdout"], stderr=res["stderr"])
        for res in data["results"]
    ]
    metrics = None
    if "metrics" in data:
        metrics_data = data["metrics"]
        metrics = ReplayMetrics(
            per_command_bytes_out=metrics_data["per_command_bytes_out"],
            per_command_bytes_err=metrics_data["per_command_bytes_err"],
            total_bytes_out=metrics_data["total_bytes_out"],
            total_bytes_err=metrics_data["total_bytes_err"],
        )
    return ReplayRecord(
        version=data["version"],
        created_utc=data["created_utc"],
        commands=commands,
        results=results,
        hashes=data["hashes"],
        metrics=metrics,
    )


def _normalize_output(output: str) -> str:
    """Normalize output by stripping timestamps and absolute paths."""
    output = re.sub("\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{3})?Z", "<TIMESTAMP>", output)
    output = re.sub("\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2},\\d{3}", "<TIMESTAMP>", output)
    # guardian: allow-path-string
    repo_root = os.path.abspath(os.getcwd())
    repo_root_normalized = repo_root.replace("\\", "/")
    output = output.replace(repo_root, "<REPO_ROOT>")
    output = output.replace(repo_root_normalized, "<REPO_ROOT>")
    output = re.sub("[A-Za-z]:/[^ \\n\\r]*", "<ABSOLUTE_PATH>", output)
    return output


def replay_and_compare(record: ReplayRecord) -> ComparisonResult:
    """Replay commands and compare with original results.

    Args:
        record: Original record to replay

    Returns:
        ComparisonResult with match status and any mismatches
    """
    if len(record.commands) != len(record.results):
        return ComparisonResult(is_match=False, mismatches=["Command and result count mismatch"])
    mismatches = []
    first_diff_lines = []
    for i, (command, original_result) in enumerate(zip(record.commands, record.results)):
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
                exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr
            )
            if current_result.exit_code != original_result.exit_code:
                mismatches.append(
                    f"Command {i + 1}: Exit code mismatch (original={original_result.exit_code}, current={current_result.exit_code})"
                )
            orig_stdout_norm = _normalize_output(original_result.stdout)
            curr_stdout_norm = _normalize_output(current_result.stdout)
            if orig_stdout_norm != curr_stdout_norm:
                mismatches.append(f"Command {i + 1}: Stdout mismatch after normalization")
                if not first_diff_lines:
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
        # guardian: allow-silent-swallow
        except Exception as e:
            mismatches.append(f"Command {i + 1}: Exception during replay: {e}")
    return ComparisonResult(
        is_match=len(mismatches) == 0,
        mismatches=mismatches,
        first_diff_summary="\n".join(first_diff_lines[:200]),
    )


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
