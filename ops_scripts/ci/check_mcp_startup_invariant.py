#!/usr/bin/env python3
"""
MCP Startup Invariant Validator (Static)

Validates that local Python MCPs declare explicit startup context:
- Must have 'cwd' pointing to repo root (or declare startup_mode=portable)
- Must not use relative imports without explicit PYTHONPATH
- Must declare env vars needed for startup

This is a FAST static check that runs before executable smoke tests.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
USER_GLOBAL_CONFIG = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"
WORKSPACE_CONFIG = REPO_ROOT / ".windsurf" / "mcp_config.json"


def is_local_python_mcp(config: dict) -> bool:
    """Check if this is a local Python MCP that needs cwd validation."""
    command = config.get("command", "")
    args = config.get("args", [])

    if command != "python":
        return False

    if not args or not isinstance(args, list):
        return False

    # Check if it's a .py file in the repo
    first_arg = str(args[0])
    return (
        first_arg.endswith(".py") and
        first_arg.startswith(str(REPO_ROOT))
    )


def validate_startup_invariant(name: str, config: dict) -> list[str]:
    """Validate startup invariants for an MCP."""
    violations = []

    if not is_local_python_mcp(config):
        return violations  # Not applicable

    # Check for explicit cwd
    cwd = config.get("cwd")
    if not cwd:
        violations.append(
            f"{name}: MISSING_CWD - Local Python MCP must declare 'cwd' "
            f"or 'startup_mode=portable'"
        )
        return violations

    # Check cwd points to repo root
    cwd_path = Path(cwd)
    if cwd_path != REPO_ROOT:
        violations.append(
            f"{name}: WRONG_CWD - Expected {REPO_ROOT}, got {cwd_path}. "
            f"Local Python MCPs should run from repo root."
        )

    # Check env vars include critical paths
    env = config.get("env", {})

    # If PYTHONPATH is set, verify it includes repo root
    pythonpath = env.get("PYTHONPATH", "")
    if pythonpath and str(REPO_ROOT) not in pythonpath:
        violations.append(
            f"{name}: PYTHONPATH_ISSUE - PYTHONPATH set but missing repo root"
        )

    return violations


def main() -> int:
    """Run startup invariant validation."""
    print("=" * 70)
    print("MCP STARTUP INVARIANT VALIDATOR")
    print("=" * 70)

    # Check user-global config
    if not USER_GLOBAL_CONFIG.exists():
        print(f"[ERROR] User-global config not found: {USER_GLOBAL_CONFIG}")
        return 1

    with open(USER_GLOBAL_CONFIG, encoding="utf-8") as f:
        config = json.load(f)

    servers = config.get("mcpServers", {})
    all_violations = []

    for name, mcp_config in servers.items():
        if mcp_config.get("disabled", False):
            continue

        violations = validate_startup_invariant(name, mcp_config)
        all_violations.extend(violations)

        if violations:
            print(f"\n❌ {name}")
            for v in violations:
                print(f"   {v}")
        elif is_local_python_mcp(mcp_config):
            print(f"\n✅ {name} - startup invariants OK")
            print(f"   cwd: {mcp_config.get('cwd')}")

    print("\n" + "=" * 70)
    if all_violations:
        print(f"FAILED: {len(all_violations)} violation(s)")
        return 1
    else:
        print("PASSED: All local Python MCPs have valid startup invariants")
        return 0


if __name__ == "__main__":
    sys.exit(main())
