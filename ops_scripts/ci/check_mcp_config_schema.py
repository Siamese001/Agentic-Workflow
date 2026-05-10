#!/usr/bin/env python3
"""
MCP Config Schema Validation Gate (MCP-SCHEMA)

Validates that .windsurf/mcp_config.json conforms to the canonical schema:
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

Rule: .windsurf/rules/windsurf-config-lookup.md + constitutional §27
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / ".windsurf" / "mcp_config.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "ci" / "mcp_config_schema.json"

# Required MCP servers per AGENTS.md Quick Reference (must be present and enabled)
REQUIRED_SERVERS: frozenset[str] = frozenset({
    "GitKraken",
    "adg_sqlite",
    "memory",
    "notion",
    "otel_mcp",
    "pytest_mcp",
    "redis",
    "vector_db",
    "io.windsurf/mcp-playwright",
    "deepwiki",
    "context7",
    "tavily",
})

# Servers that can be disabled (shadow-disabled or intentionally off)
OPTIONAL_SERVERS: frozenset[str] = frozenset({
    "filesystem",  # shadow-disabled per ADR-095
    "task_manager",  # shadow-disabled per ADR-095
})

# Valid top-level keys in mcp_config.json (constitutional §27)
VALID_TOP_KEYS: frozenset[str] = frozenset({
    "_note",
    "mcpServers",
    "_bootstrap_env",
})

# Valid per-server keys
VALID_SERVER_KEYS: frozenset[str] = frozenset({
    "command",
    "args",
    "env",
    "disabled",
    "url",
    "_note",
    "_comment",
    "_startup",
    "_shadow_disable",
    "_tuning_note",
    "_auth",
})


@dataclass(frozen=True)
class Violation:
    severity: str  # ERROR | WARNING
    code: str
    message: str
    path: str = ""  # JSON path to violation


def load_config() -> tuple[dict[str, Any] | None, list[Violation]]:
    """Load and parse mcp_config.json. Returns (data, parse_errors)."""
    errors: list[Violation] = []
    
    if not CONFIG_PATH.exists():
        errors.append(Violation(
            severity="ERROR",
            code="CONFIG_MISSING",
            message=f"mcp_config.json not found at {CONFIG_PATH}",
        ))
        return None, errors
    
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
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


def check_required_servers(servers: dict[str, Any]) -> list[Violation]:
    """Verify all required servers are present."""
    violations: list[Violation] = []
    present_servers = set(servers.keys())
    
    missing = REQUIRED_SERVERS - present_servers
    for server in sorted(missing):
        violations.append(Violation(
            severity="ERROR",
            code="REQUIRED_SERVER_MISSING",
            message=f"Required MCP server '{server}' not defined",
            path=f".mcpServers.{server}",
        ))
    
    return violations


def check_server_structure(name: str, config: Any) -> list[Violation]:
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
    
    # Warn if required server is disabled
    if name in REQUIRED_SERVERS and disabled is True:
        violations.append(Violation(
            severity="WARNING",
            code="REQUIRED_SERVER_DISABLED",
            message=f"Required server '{name}' is disabled — MCP calls will fail",
            path=f"{path_prefix}.disabled",
        ))
    
    return violations


def evaluate() -> dict[str, Any]:
    """Run full schema validation. Returns report dict."""
    report: dict[str, Any] = {
        "checked_at": "",
        "config_path": str(CONFIG_PATH),
        "valid": False,
        "errors": [],
        "warnings": [],
        "server_count": 0,
        "required_present": [],
        "required_missing": [],
    }
    
    data, parse_errors = load_config()
    
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
        all_violations.extend(check_required_servers(servers))
        
        for name, config in servers.items():
            all_violations.extend(check_server_structure(name, config))
    
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
        report["required_present"] = sorted(REQUIRED_SERVERS & present)
        report["required_missing"] = sorted(REQUIRED_SERVERS - present)
    
    report["valid"] = len(report["errors"]) == 0
    
    return report


def write_report(report: dict[str, Any]) -> None:
    """Write report to artifact path."""
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def main(argv: list[str] | None = None) -> int:
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Config Schema Validation")
    parser.add_argument("--fail-closed", action="store_true", help="Exit 1 on violations")
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    args = parser.parse_args(argv)
    
    # Bypass check
    if os.environ.get("MCP_CONFIG_SCHEMA_BYPASS") == "1":
        print("[check_mcp_config_schema] BYPASS=1 — skipping", file=sys.stderr)
        return 0
    
    fail_closed = args.fail_closed or (os.environ.get("MCP_CONFIG_SCHEMA_FAIL_CLOSED") == "1")
    
    report = evaluate()
    write_report(report)
    
    error_count = len(report["errors"])
    warning_count = len(report["warnings"])
    
    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    
    # Summary output
    print("=== MCP Config Schema Validation ===")
    print(f"Config: {report['config_path']}")
    print(f"Servers: {report['server_count']}")
    print(f"Required present: {len(report['required_present'])}/{len(REQUIRED_SERVERS)}")
    
    if report["required_present"]:
        print(f"  ✓ {', '.join(report['required_present'][:5])}{'...' if len(report['required_present']) > 5 else ''}")
    
    if report["errors"]:
        print(f"\n❌ ERRORS: {error_count}")
        for e in report["errors"]:
            print(f"  [{e['code']}] {e['message']}")
            if e.get("path"):
                print(f"    Path: {e['path']}")
    
    if report["warnings"]:
        print(f"\n⚠️  WARNINGS: {warning_count}")
        for w in report["warnings"]:
            print(f"  [{w['code']}] {w['message']}")
    
    if not report["errors"] and not report["warnings"]:
        print("\n✅ Schema valid — all required servers present and properly configured")
    elif not report["errors"]:
        print("\n✅ Schema valid with warnings")
    
    if fail_closed and error_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
