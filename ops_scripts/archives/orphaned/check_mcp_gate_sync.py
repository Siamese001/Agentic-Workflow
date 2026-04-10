#!/usr/bin/env python3
"""
CI gate: MCP gate constant ↔ mcp_config.json key synchronisation.

Prevents the class of regression where:
  - A server is added to mcp_config.json but no gate constant is added → silent miss
  - A gate constant is renamed but mcp_config.json key is not → dead gate (never fires)

Policy:
  - Every gated server name constant in pre_mcp_gate.py MUST match a key in mcp_config.json.
  - Every server in mcp_config.json that is NOT in the explicit fail-open set MUST have a
    matching gate constant.
  - Fail-open servers (GitKraken, enhanced_http) are documented here — new servers default
    to MUST_BE_GATED; explicitly add to FAIL_OPEN_SERVERS only after deliberate review.

Exits 0 on full compliance. Exits 1 on any violation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MCP_CONFIG_PATH = REPO_ROOT / ".windsurf" / "mcp_config.json"
GATE_PATH = REPO_ROOT / "ops_scripts" / "hooks" / "windsurf" / "pre_mcp_gate.py"

# Servers deliberately fail-open — no gate needed because:
#   GitKraken  — native binary managed by OS; no probe possible from Python
#   enhanced_http — HTTP client; "backend" is the internet, not local infra
FAIL_OPEN_SERVERS: frozenset[str] = frozenset({"GitKraken", "enhanced_http"})


def _load_config_keys() -> set[str]:
    if not MCP_CONFIG_PATH.exists():
        print(f"ERROR: mcp_config.json not found at {MCP_CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(MCP_CONFIG_PATH.read_text(encoding="utf-8"))
    return set(data.get("mcpServers", {}).keys())


def _load_gate_constants() -> set[str]:
    """
    Extract *_SERVER_NAME = "..." constant values from pre_mcp_gate.py.
    Uses text parsing — no import needed (avoids side-effects from the module).
    """
    if not GATE_PATH.exists():
        print(f"ERROR: pre_mcp_gate.py not found at {GATE_PATH}", file=sys.stderr)
        sys.exit(1)

    constants: set[str] = set()
    for line in GATE_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if "SERVER_NAME" not in stripped or "=" not in stripped:
            continue
        # Strip inline comment before parsing the value
        code_part = stripped.split("#")[0].rstrip()
        if not code_part.endswith('"') and not code_part.endswith("'"):
            continue
        _, _, rhs = code_part.partition("=")
        value = rhs.strip().strip('"').strip("'").strip()
        if value:
            constants.add(value)
    return constants


def main() -> int:
    config_keys = _load_config_keys()
    gate_constants = _load_gate_constants()

    must_be_gated = config_keys - FAIL_OPEN_SERVERS
    violations: list[str] = []

    # Dead gates: constant exists in gate but not in config (typo / stale rename)
    dead_gates = gate_constants - config_keys
    for name in sorted(dead_gates):
        violations.append(
            f"DEAD_GATE: '{name}' has a *_SERVER_NAME constant in pre_mcp_gate.py "
            f"but is NOT a key in mcp_config.json — stale rename or typo."
        )

    # Ungated servers: in config, not fail-open, but no gate constant
    ungated = must_be_gated - gate_constants
    for name in sorted(ungated):
        violations.append(
            f"UNGATED_SERVER: '{name}' is in mcp_config.json but has no "
            f"*_SERVER_NAME constant in pre_mcp_gate.py. "
            f"Add a gate or add to FAIL_OPEN_SERVERS with justification."
        )

    if violations:
        print("❌ MCP gate sync violations found:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        print("\nConfig keys    :", sorted(config_keys), file=sys.stderr)
        print("Gate constants :", sorted(gate_constants), file=sys.stderr)
        print("Fail-open      :", sorted(FAIL_OPEN_SERVERS), file=sys.stderr)
        return 1

    print(
        f"✅ MCP gate sync OK — {len(gate_constants)} gated, "
        f"{len(FAIL_OPEN_SERVERS)} fail-open, "
        f"{len(config_keys)} total in config."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
