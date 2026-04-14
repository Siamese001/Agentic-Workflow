#!/usr/bin/env python3
"""
Environment setup for sequential thinking prioritization.

This script applies variables to the current Python process and can also
materialize shell-specific environment files for persistent/manual loading.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Final


ENV_VARS: Final[dict[str, str]] = {
    "SEQUENTIAL_THINKING_ENABLED": "true",
    "SEQUENTIAL_THINKING_PRIORITY": "0",
    "SEQUENTIAL_THINKING_AUTO_TRIGGER": "true",
    "SEQUENTIAL_THINKING_MIN_COMPLEXITY": "minimal",
    "SEQUENTIAL_THINKING_MAX_THOUGHTS": "25",
    "SEQUENTIAL_THINKING_TOKEN_BUDGET": "50000",
    "WINDSURF_TOOL_PREFERENCE": "sequential-thinking",
    "WINDSURF_MCP_BOOST_MODE": "aggressive",
    "WINDSURF_REASONING_MODE": "sequential-only",
    "KIMI25_SEQUENTIAL_THINKING": "enabled",
    "KIMI25_REASONING_BOOST": "maximum",
    "KIMI25_TOKEN_ALLOCATION": "0.35",
    "KIMI25_AUTO_ANALYSIS": "true",
    "KIMI_K2_5_DOMINANCE": "enabled",
    "MCP_SEQUENTIAL_THINKING_BOOST": "aggressive",
    "MCP_TOOL_ORDERING": "sequential-dominance",
    "MCP_KIMI25_MODE": "hardened",
    "CASCADE_CHAT_FALLBACK": "disabled",
    "CASCADE_CHAT_SUPPRESS_ON_PLANNING": "true",
    "CASCADE_CHAT_MIN_COMPLEXITY": "high",
    "SEQUENTIAL_THINKING_CACHE_ENABLED": "true",
    "SEQUENTIAL_THINKING_ASYNC_MODE": "false",
    "SEQUENTIAL_THINKING_LOG_LEVEL": "INFO",
    "SEQUENTIAL_THINKING_AGGRESSIVE_MODE": "enabled",
}

CRITICAL_VARS: Final[tuple[str, ...]] = (
    "SEQUENTIAL_THINKING_ENABLED",
    "SEQUENTIAL_THINKING_PRIORITY",
    "WINDSURF_TOOL_PREFERENCE",
    "KIMI25_SEQUENTIAL_THINKING",
    "CASCADE_CHAT_FALLBACK",
    "KIMI_K2_5_DOMINANCE",
)

STATUS_VARS: Final[tuple[str, ...]] = (
    "SEQUENTIAL_THINKING_ENABLED",
    "SEQUENTIAL_THINKING_PRIORITY",
    "WINDSURF_TOOL_PREFERENCE",
    "KIMI25_SEQUENTIAL_THINKING",
    "MCP_SEQUENTIAL_THINKING_BOOST",
)

VALID_ENV_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")


def _default_format() -> str:
    return "powershell" if os.name == "nt" else "posix"


def _default_output_path(fmt: str) -> Path:
    suffixes = {
        "posix": ".seq_thinking_env.sh",
        "dotenv": ".seq_thinking_env",
        "powershell": ".seq_thinking_env.ps1",
        "cmd": ".seq_thinking_env.cmd",
    }
    return Path(__file__).parent / suffixes[fmt]


def _validate_env_vars(env_vars: dict[str, str]) -> None:
    invalid = [
        key
        for key, value in env_vars.items()
        if not VALID_ENV_NAME.fullmatch(key) or not isinstance(value, str) or not value
    ]
    if invalid:
        joined = ", ".join(sorted(invalid))
        raise ValueError(f"Invalid environment variable definitions: {joined}")


def apply_env_vars(env_vars: dict[str, str]) -> None:
    """Apply environment variables to the current process only."""
    _validate_env_vars(env_vars)
    print("Applying sequential thinking environment variables to current process...")
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"  SET {key}={value}")


def verify_critical_vars(critical_vars: tuple[str, ...] = CRITICAL_VARS) -> bool:
    """Verify critical variables exist in the current process environment."""
    print("\nVerifying critical environment variables:")
    all_set = True
    for var in critical_vars:
        value = os.environ.get(var)
        if value:
            print(f"  OK {var}={value}")
        else:
            print(f"  MISSING {var} not set")
            all_set = False
    return all_set


def print_env_status() -> None:
    """Print current environment status for sequential thinking."""
    print("\nSequential Thinking Environment Status:")
    print("=" * 50)
    for var in STATUS_VARS:
        value = os.environ.get(var, "not set")
        status = "OK" if value != "not set" else "MISSING"
        print(f"  {status} {var}: {value}")


def _render_env_content(fmt: str, env_vars: dict[str, str]) -> str:
    if fmt == "dotenv":
        return "\n".join(f"{key}={value}" for key, value in env_vars.items()) + "\n"
    if fmt == "posix":
        return "\n".join(f"export {key}='{value}'" for key, value in env_vars.items()) + "\n"
    if fmt == "powershell":
        return "\n".join(f"$Env:{key} = '{value}'" for key, value in env_vars.items()) + "\n"
    if fmt == "cmd":
        return "\n".join(f"set {key}={value}" for key, value in env_vars.items()) + "\n"
    raise ValueError(f"Unsupported format: {fmt}")


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        delete=False,
        dir=path.parent,
        prefix=path.name,
        suffix=".tmp",
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def create_env_file(fmt: str | None = None, output_path: Path | None = None) -> Path:
    """Create a shell-specific environment file for manual loading."""
    fmt = fmt or _default_format()
    path = output_path or _default_output_path(fmt)
    content = _render_env_content(fmt, ENV_VARS)
    _write_text_atomic(path, content)
    print(f"\nEnvironment file created: {path}")
    if fmt == "posix":
        print(f"Load with: source {path.name}")
    elif fmt == "powershell":
        print(f"Load with: . .\\{path.name}")
    elif fmt == "cmd":
        print(f"Load with: call {path.name}")
    else:
        print(f"Load via your dotenv-compatible tool using: {path.name}")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply or materialize sequential thinking environment settings."
    )
    parser.add_argument("--status", action="store_true", help="Show current process status only.")
    parser.add_argument(
        "--create-env",
        action="store_true",
        help="Write a shell-specific environment file instead of applying variables only.",
    )
    parser.add_argument(
        "--format",
        choices=("posix", "dotenv", "powershell", "cmd"),
        default=_default_format(),
        help="Output format for --create-env.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional explicit path for the generated environment file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.status:
        print_env_status()
        return 0

    if args.create_env:
        try:
            create_env_file(fmt=args.format, output_path=args.output)
            return 0
        except (OSError, ValueError) as exc:
            print(f"FAILED to create environment file: {exc}")
            return 1

    try:
        apply_env_vars(ENV_VARS)
    except ValueError as exc:
        print(f"FAILED invalid environment configuration: {exc}")
        return 1

    all_set = verify_critical_vars()
    print_env_status()

    if all_set:
        print("\nSUCCESS Critical environment variables are active in the current process.")
        return 0

    print("\nFAILED Some critical variables are missing from the current process.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
