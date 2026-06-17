#!/usr/bin/env python3
"""MCP Config Sovereignty gate — Constitutional Rule #0 (filesystem scope).

Validates that the root MCP config keeps the filesystem server scoped to the
repo root only:

- ``filesystem`` entry present in ``mcpServers``
- ``args`` = ``[<editor-launcher>, "${env:AGENTIC_REPO_ROOT}"]`` (exactly two path slots)
- No forbidden out-of-repo path fragments in any server string field
- ``disabled: true`` is allowed (shadow-disable policy; scope is still structural)

Profile: root ``.mcp.json`` (Claude Code SSOT).

Bypass: ``MCP_CONFIG_SOVEREIGNTY_BYPASS=1``
Artifact: ``artifacts/ci/mcp_config_sovereignty.json``
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_CI_DIR = Path(__file__).resolve().parent
if str(_CI_DIR) not in sys.path:
    sys.path.insert(0, str(_CI_DIR))

from _mcp_ci_common import REPO_MCP_PATH, load_mcp_json  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "ci" / "mcp_config_sovereignty.json"

ALLOWED_ROOT_ARG = "${env:AGENTIC_REPO_ROOT}"
ALLOWED_REPO_ROOT_MARKER = "${env:AGENTIC_REPO_ROOT}"

FORBIDDEN_PATH_FRAGMENTS: tuple[str, ...] = (
    r"c:\users",
    r"c:/users",
    "/users/",
    ".claude/plans",
    ".claude\\plans",
)

PROFILE_LAUNCHERS: dict[str, tuple[Path, str]] = {
    "repo": (REPO_MCP_PATH, ".claude/governance/scripts/filesystem_mcp_launcher.js"),
}


@dataclass(frozen=True)
class Violation:
    profile: str
    code: str
    message: str


def _normalise(path_str: str) -> str:
    return path_str.replace("\\", "/").lower()


_OPERATIONAL_KEYS = frozenset({"command", "args", "env", "cwd", "url"})


def _iter_operational_strings(entry: dict[str, Any]) -> list[str]:
    found: list[str] = []
    for key, value in entry.items():
        if key.startswith("_") or key not in _OPERATIONAL_KEYS:
            continue
        if isinstance(value, str):
            found.append(value)
        elif isinstance(value, list):
            found.extend(str(item) for item in value if isinstance(item, str))
        elif isinstance(value, dict):
            found.extend(str(item) for item in value.values() if isinstance(item, str))
    return found


def _check_forbidden_paths(profile: str, servers: dict[str, Any]) -> list[Violation]:
    violations: list[Violation] = []
    for server_name, entry in servers.items():
        if not isinstance(entry, dict):
            continue
        for text in _iter_operational_strings(entry):
            text_norm = _normalise(text)
            for forbidden in FORBIDDEN_PATH_FRAGMENTS:
                if _normalise(forbidden) in text_norm:
                    violations.append(
                        Violation(
                            profile=profile,
                            code="FORBIDDEN_PATH_FRAGMENT",
                            message=(
                                f"server '{server_name}' references forbidden fragment "
                                f"'{forbidden}' in '{text}'"
                            ),
                        )
                    )
    return violations


def _check_filesystem_scope(
    profile: str,
    servers: dict[str, Any],
    launcher_substr: str,
) -> list[Violation]:
    violations: list[Violation] = []
    if "filesystem" not in servers:
        return [
            Violation(
                profile=profile,
                code="MISSING_FILESYSTEM",
                message="'filesystem' key absent from mcpServers",
            )
        ]

    fs_entry = servers["filesystem"]
    if not isinstance(fs_entry, dict):
        return [
            Violation(
                profile=profile,
                code="INVALID_FILESYSTEM_CONFIG",
                message="filesystem entry must be an object",
            )
        ]

    args = fs_entry.get("args")
    if not isinstance(args, list):
        return [
            Violation(
                profile=profile,
                code="INVALID_FILESYSTEM_ARGS",
                message="filesystem.args must be an array",
            )
        ]

    if len(args) != 2:
        violations.append(
            Violation(
                profile=profile,
                code="FILESYSTEM_ARGS_COUNT",
                message=(
                    f"filesystem.args must have exactly 2 entries (launcher + repo root); "
                    f"got {len(args)}"
                ),
            )
        )
        return violations

    launcher_arg, root_arg = args[0], args[1]
    if not isinstance(launcher_arg, str) or launcher_substr not in launcher_arg.replace("\\", "/"):
        violations.append(
            Violation(
                profile=profile,
                code="FILESYSTEM_LAUNCHER_PATH",
                message=(
                    f"filesystem launcher arg must include '{launcher_substr}'; "
                    f"got '{launcher_arg}'"
                ),
            )
        )
    if root_arg != ALLOWED_ROOT_ARG:
        violations.append(
            Violation(
                profile=profile,
                code="FILESYSTEM_ROOT_ARG",
                message=(
                    f"filesystem allowed-directory arg must be exactly '{ALLOWED_ROOT_ARG}'; "
                    f"got '{root_arg}'"
                ),
            )
        )
    if isinstance(launcher_arg, str) and ALLOWED_REPO_ROOT_MARKER not in launcher_arg:
        violations.append(
            Violation(
                profile=profile,
                code="FILESYSTEM_LAUNCHER_ENV",
                message=(
                    "filesystem launcher path must use ${env:AGENTIC_REPO_ROOT} "
                    f"prefix; got '{launcher_arg}'"
                ),
            )
        )

    comment_blob = " ".join(
        str(fs_entry.get(key, ""))
        for key in ("_comment", "_startup", "_shadow_disable", "_note")
    ).lower()
    if "repo root" not in comment_blob and "rule #0" not in comment_blob:
        violations.append(
            Violation(
                profile=profile,
                code="FILESYSTEM_SCOPE_DOCUMENTATION",
                message=(
                    "filesystem entry must document repo-root scope in _comment/_startup "
                    "(mention 'repo root' or 'Rule #0')"
                ),
            )
        )

    return violations


def validate_profile(profile: str, config_path: Path, launcher_substr: str) -> list[Violation]:
    violations: list[Violation] = []
    if not config_path.exists():
        return [
            Violation(
                profile=profile,
                code="CONFIG_MISSING",
                message=f"config not found at {config_path}",
            )
        ]

    try:
        data = load_mcp_json(config_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [
            Violation(
                profile=profile,
                code="CONFIG_PARSE_ERROR",
                message=f"cannot read {config_path}: {exc}",
            )
        ]

    servers = data.get("mcpServers", {})
    if not isinstance(servers, dict):
        return [
            Violation(
                profile=profile,
                code="INVALID_MCPSERVERS",
                message="mcpServers must be an object",
            )
        ]

    violations.extend(_check_filesystem_scope(profile, servers, launcher_substr))
    violations.extend(_check_forbidden_paths(profile, servers))
    return violations


def evaluate() -> dict[str, Any]:
    all_violations: list[Violation] = []
    for profile, (path, launcher_substr) in PROFILE_LAUNCHERS.items():
        all_violations.extend(validate_profile(profile, path, launcher_substr))

    return {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "valid": not all_violations,
        "violation_count": len(all_violations),
        "violations": [
            {"profile": v.profile, "code": v.code, "message": v.message}
            for v in all_violations
        ],
    }


def _write_artifact(report: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if os.environ.get("MCP_CONFIG_SOVEREIGNTY_BYPASS") == "1":
        print("[check_mcp_config_sovereignty] BYPASS=1 — skipping")
        return 0

    report = evaluate()
    _write_artifact(report)

    if report["valid"]:
        print(
            "[check_mcp_config_sovereignty] OK: Rule #0 filesystem scope valid for "
            "root MCP config"
        )
        return 0

    print(
        f"[check_mcp_config_sovereignty] FAIL: {report['violation_count']} violation(s):",
        file=sys.stderr,
    )
    for item in report["violations"]:
        print(
            f"  - [{item['profile']}] {item['code']}: {item['message']}",
            file=sys.stderr,
        )
    print(
        "[check_mcp_config_sovereignty] Fix: lock filesystem.args to "
        f"[<editor-launcher>, '{ALLOWED_ROOT_ARG}'] only. "
        "Never add C:\\Users\\... or non-SSOT plan paths.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
