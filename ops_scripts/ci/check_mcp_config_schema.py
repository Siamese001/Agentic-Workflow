#!/usr/bin/env python3
"""MCP Config Schema Validation Gate (MCP-SCHEMA).

Validates the repo SSOT `.mcp.json`:
- Required servers present: GitKraken, adg_sqlite, memory, notion, otel_mcp, pytest_mcp, redis, vector_db
- Each server has required fields: command, args (array)
- Optional fields valid: env (object), disabled (boolean), url (for remote)
- No unknown top-level keys (constitutional §27 compliance)

Exit codes:
    0 = Schema valid (or advisory mode with warnings)
    1 = Schema violations found (fail-closed mode)
    2 = File unreadable / JSON parse error

Environment:
    MCP_CONFIG_SCHEMA_BYPASS=1 → skip check
    MCP_CONFIG_SCHEMA_FAIL_CLOSED=1 → exit 1 on violations

Output:
    artifacts/ci/mcp_config_schema.json

Rule: `.codex/rules/mcp-config-ssot.mdc` + constitutional §27
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_CI_DIR = Path(__file__).resolve().parent
if str(_CI_DIR) not in sys.path:
    sys.path.insert(0, str(_CI_DIR))

from _mcp_ci_common import (  # noqa: E402
    MCP_PROFILES,
    OPTIONAL_SERVERS,
    REPO_MCP_PATH,
    REPO_REQUIRED_SERVERS,
    VALID_SERVER_KEYS,
    VALID_TOP_KEYS,
    profile_config_path,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_MCP_PATH
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "ci" / "mcp_config_schema.json"
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "ci"

REQUIRED_SERVERS = REPO_REQUIRED_SERVERS
VECTOR_DB_REQUIRED_ENV = {
    "VECTOR_DB_DEVICE": "cuda",
    "EMBEDDING_DEVICE": "cuda",
    "VECTOR_DB_ENABLE_MODEL_PREWARM": "1",
}
VECTOR_DB_MODEL_LOAD_TIMEOUT_MAX_SECONDS = 119.0


@dataclass(frozen=True)
class Violation:
    severity: str  # ERROR | WARNING
    code: str
    message: str
    path: str = ""  # JSON path to violation


def load_config(config_path: Path | None = None) -> tuple[dict[str, Any] | None, list[Violation]]:
    """Load and parse an MCP config file. Returns (data, parse_errors)."""
    path = config_path if config_path is not None else CONFIG_PATH
    errors: list[Violation] = []
    
    if not path.exists():
        errors.append(Violation(
            severity="ERROR",
            code="CONFIG_MISSING",
            message=f"MCP config not found at {path}",
        ))
        return None, errors
    
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        errors.append(Violation(
            severity="ERROR",
            code="JSON_PARSE_ERROR",
            message=f"Invalid JSON: {exc}",
            path="",
        ))
        return None, errors
    except OSError as exc:
        errors.append(Violation(
            severity="ERROR",
            code="FILE_READ_ERROR",
            message=f"Cannot read file: {exc}",
        ))
        return None, errors
    
    return data, errors


def check_top_level_keys(data: dict[str, Any]) -> list[Violation]:
    """Check for unknown top-level keys (constitutional §27)."""
    violations: list[Violation] = []
    extra_keys = set(data.keys()) - VALID_TOP_KEYS
    
    for key in extra_keys:
        violations.append(Violation(
            severity="ERROR",
            code="UNKNOWN_TOP_KEY",
            message=f"Unknown top-level key '{key}' — risks schema rejection (§27)",
            path=f".{key}",
        ))
    
    return violations


def check_required_servers(
    servers: dict[str, Any],
    required_servers: frozenset[str] = REQUIRED_SERVERS,
) -> list[Violation]:
    """Verify all required servers are present."""
    violations: list[Violation] = []
    present_servers = set(servers.keys())
    
    missing = required_servers - present_servers
    for server in sorted(missing):
        violations.append(Violation(
            severity="ERROR",
            code="REQUIRED_SERVER_MISSING",
            message=f"Required MCP server '{server}' not defined",
            path=f".mcpServers.{server}",
        ))
    
    return violations


def check_server_structure(
    name: str,
    config: Any,
    required_servers: frozenset[str] = REQUIRED_SERVERS,
) -> list[Violation]:
    """Validate a single server's configuration structure."""
    violations: list[Violation] = []
    path_prefix = f".mcpServers.{name}"
    
    if not isinstance(config, dict):
        violations.append(Violation(
            severity="ERROR",
            code="INVALID_SERVER_CONFIG",
            message=f"Server '{name}' config must be an object",
            path=path_prefix,
        ))
        return violations
    
    # Check for unknown keys
    extra_keys = set(config.keys()) - VALID_SERVER_KEYS
    for key in extra_keys:
        violations.append(Violation(
            severity="WARNING",
            code="UNKNOWN_SERVER_KEY",
            message=f"Unknown key '{key}' in server '{name}'",
            path=f"{path_prefix}.{key}",
        ))
    
    # Remote servers (deepwiki, context7, tavily) need url, not command/args
    is_remote = "url" in config
    
    if is_remote:
        # Remote server validation
        url = config.get("url", "")
        if not isinstance(url, str) or not url.startswith(("https://", "http://")):
            violations.append(Violation(
                severity="ERROR",
                code="INVALID_REMOTE_URL",
                message=f"Remote server '{name}' must have valid https:// URL",
                path=f"{path_prefix}.url",
            ))
    else:
        # Local server validation
        if "command" not in config:
            violations.append(Violation(
                severity="ERROR",
                code="MISSING_COMMAND",
                message=f"Local server '{name}' missing required 'command' field",
                path=path_prefix,
            ))
        
        args = config.get("args")
        if args is None:
            violations.append(Violation(
                severity="ERROR",
                code="MISSING_ARGS",
                message=f"Server '{name}' missing required 'args' array",
                path=f"{path_prefix}.args",
            ))
        elif not isinstance(args, list):
            violations.append(Violation(
                severity="ERROR",
                code="INVALID_ARGS_TYPE",
                message=f"Server '{name}' 'args' must be an array",
                path=f"{path_prefix}.args",
            ))
    
    # Validate disabled field if present
    disabled = config.get("disabled")
    if disabled is not None and not isinstance(disabled, bool):
        violations.append(Violation(
            severity="ERROR",
            code="INVALID_DISABLED_TYPE",
            message=f"Server '{name}' 'disabled' must be boolean",
            path=f"{path_prefix}.disabled",
        ))
    
    # Validate env field if present
    env = config.get("env")
    if env is not None and not isinstance(env, dict):
        violations.append(Violation(
            severity="ERROR",
            code="INVALID_ENV_TYPE",
            message=f"Server '{name}' 'env' must be an object",
            path=f"{path_prefix}.env",
        ))
    elif name == "vector_db":
        violations.extend(check_vector_db_runtime_env(env or {}, path_prefix))
    
    # Warn if required server is disabled
    if name in required_servers and disabled is True:
        violations.append(Violation(
            severity="WARNING",
            code="REQUIRED_SERVER_DISABLED",
            message=f"Required server '{name}' is disabled — MCP calls will fail",
            path=f"{path_prefix}.disabled",
        ))
    
    return violations


def check_vector_db_runtime_env(env: dict[str, Any], path_prefix: str) -> list[Violation]:
    """Validate vector_db runtime env required to avoid cold CPU MCP timeouts."""
    violations: list[Violation] = []

    for key, expected in VECTOR_DB_REQUIRED_ENV.items():
        actual = env.get(key)
        if actual != expected:
            violations.append(Violation(
                severity="ERROR",
                code="VECTOR_DB_RUNTIME_ENV_MISSING",
                message=f"vector_db must set {key}={expected!r} for CUDA-backed warm semantic search",
                path=f"{path_prefix}.env.{key}",
            ))

    raw_timeout = env.get("VECTOR_DB_MODEL_LOAD_TIMEOUT")
    if raw_timeout is None:
        violations.append(Violation(
            severity="ERROR",
            code="VECTOR_DB_MODEL_LOAD_TIMEOUT_MISSING",
            message=(
                "vector_db must set VECTOR_DB_MODEL_LOAD_TIMEOUT below the Codex tool-call timeout "
                "so cold model load fails before wedging stdio"
            ),
            path=f"{path_prefix}.env.VECTOR_DB_MODEL_LOAD_TIMEOUT",
        ))
        return violations

    try:
        timeout = float(raw_timeout)
    except (TypeError, ValueError):
        violations.append(Violation(
            severity="ERROR",
            code="VECTOR_DB_MODEL_LOAD_TIMEOUT_INVALID",
            message="vector_db VECTOR_DB_MODEL_LOAD_TIMEOUT must be numeric seconds",
            path=f"{path_prefix}.env.VECTOR_DB_MODEL_LOAD_TIMEOUT",
        ))
        return violations

    if timeout <= 0 or timeout >= VECTOR_DB_MODEL_LOAD_TIMEOUT_MAX_SECONDS:
        violations.append(Violation(
            severity="ERROR",
            code="VECTOR_DB_MODEL_LOAD_TIMEOUT_UNBOUNDED",
            message=(
                "vector_db VECTOR_DB_MODEL_LOAD_TIMEOUT must be >0 and <119s "
                "to stay below the 120s Codex tool-call timeout"
            ),
            path=f"{path_prefix}.env.VECTOR_DB_MODEL_LOAD_TIMEOUT",
        ))

    return violations


def evaluate(
    config_path: Path | None = None,
    required_servers: frozenset[str] | None = None,
    profile: str = "repo",
) -> dict[str, Any]:
    """Run full schema validation for one editor profile. Returns report dict."""
    path = config_path if config_path is not None else CONFIG_PATH
    required = required_servers if required_servers is not None else REQUIRED_SERVERS
    report: dict[str, Any] = {
        "checked_at": "",
        "profile": profile,
        "config_path": str(path),
        "valid": False,
        "errors": [],
        "warnings": [],
        "server_count": 0,
        "required_present": [],
        "required_missing": [],
    }
    
    data, parse_errors = load_config(path)
    
    if parse_errors:
        for v in parse_errors:
            entry = {"code": v.code, "message": v.message, "path": v.path}
            if v.severity == "ERROR":
                report["errors"].append(entry)
            else:
                report["warnings"].append(entry)
        return report
    
    assert data is not None
    all_violations: list[Violation] = []
    
    # Top-level checks
    all_violations.extend(check_top_level_keys(data))
    
    # mcpServers checks
    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        all_violations.append(Violation(
            severity="ERROR",
            code="INVALID_MCPSERVERS",
            message="'mcpServers' must be an object",
            path=".mcpServers",
        ))
    else:
        report["server_count"] = len(servers)
        all_violations.extend(check_required_servers(servers, required))
        
        for name, config in servers.items():
            all_violations.extend(check_server_structure(name, config, required))
    
    # Build report
    for v in all_violations:
        entry = {"severity": v.severity, "code": v.code, "message": v.message, "path": v.path}
        if v.severity == "ERROR":
            report["errors"].append(entry)
        else:
            report["warnings"].append(entry)
    
    # Track required server presence
    if isinstance(servers, dict):
        present = set(servers.keys())
        report["required_present"] = sorted(required & present)
        report["required_missing"] = sorted(required - present)
    
    report["valid"] = len(report["errors"]) == 0
    
    return report


def write_report(report: dict[str, Any]) -> None:
    """Write report to artifact path."""
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def evaluate_all_profiles() -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    for profile, required in MCP_PROFILES.items():
        reports[profile] = evaluate(
            profile_config_path(profile, CONFIG_PATH),
            required,
            profile=profile,
        )
        artifact = ARTIFACT_DIR / f"mcp_config_schema_{profile}.json"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(json.dumps(reports[profile], indent=2), encoding="utf-8")
    return reports


def main(argv: list[str] | None = None) -> int:
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Config Schema Validation")
    parser.add_argument(
        "--profile",
        choices=("repo", "all"),
        default="repo",
        help="Which MCP config to validate (default: repo; CI uses --profile all)",
    )
    parser.add_argument("--fail-closed", action="store_true", help="Exit 1 on violations")
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    args = parser.parse_args(argv)
    
    # Bypass check
    if os.environ.get("MCP_CONFIG_SCHEMA_BYPASS") == "1":
        print("[check_mcp_config_schema] BYPASS=1 — skipping", file=sys.stderr)
        return 0
    
    fail_closed = args.fail_closed or (os.environ.get("MCP_CONFIG_SCHEMA_FAIL_CLOSED") == "1")
    
    if args.profile == "all":
        reports = evaluate_all_profiles()
        write_report(reports["repo"])
        combined_errors = sum(len(r["errors"]) for r in reports.values())
        combined_warnings = sum(len(r["warnings"]) for r in reports.values())
    else:
        required = MCP_PROFILES[args.profile]
        reports = {
            args.profile: evaluate(
                profile_config_path(args.profile, CONFIG_PATH),
                required,
                profile=args.profile,
            ),
        }
        write_report(reports[args.profile])
        combined_errors = len(reports[args.profile]["errors"])
        combined_warnings = len(reports[args.profile]["warnings"])
    
    if args.json:
        if args.profile == "all":
            print(json.dumps(reports, indent=2))
        else:
            print(json.dumps(reports[args.profile], indent=2))
        return 0
    
    print("=== MCP Config Schema Validation ===")
    exit_code = 0
    for profile, report in reports.items():
        required = MCP_PROFILES[profile]
        print(f"\n--- {profile} ---")
        print(f"Config: {report['config_path']}")
        print(f"Servers: {report['server_count']}")
        print(f"Required present: {len(report['required_present'])}/{len(required)}")
        if report["errors"]:
            print(f"❌ ERRORS: {len(report['errors'])}")
            for err in report["errors"]:
                print(f"  [{err['code']}] {err['message']}")
            exit_code = 1
        elif report["warnings"]:
            print(f"⚠️  WARNINGS: {len(report['warnings'])}")
            for warn in report["warnings"]:
                print(f"  [{warn['code']}] {warn['message']}")
            print("✅ Schema valid with warnings")
        else:
            print("✅ Schema valid")
    
    if fail_closed and (combined_errors > 0 or exit_code != 0):
        return 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
