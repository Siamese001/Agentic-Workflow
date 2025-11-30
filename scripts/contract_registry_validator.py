#!/usr/bin/env python3
"""
contract_registry_validator.py

Contract Registry Validator for Agentic-Workflow-10_11
======================================================

This script enforces that the contract registry (contracts.yaml) meets
Agentic L5 expectations for:

- Pillar 3  Structural / Typed Contracts
- Pillar 8  Tool Ecosystem & Resilience
- Pillar 9  Safety & Policy Control Plane
- Pillar 11 Cost & Optimization (timeouts, retries, tiers)

It validates, at minimum:

1) Presence and structure of contracts.yaml
   - Located at repo root or under schemas/ (first match wins)
   - Must be a mapping with well-defined top-level sections

2) Global uniqueness of IDs and semver compliance
   - Every contract (tool, planner, executor, agent, mcp_server) has an `id`
   - IDs are globally unique across all sections
   - `version` is a semantic version (e.g. "1.0.0")

3) Tool / planner / executor contracts
   Required keys per entry:
     - id:           unique str
     - kind:         {"tool","planner","executor"} (or inferred by section)
     - name:         human-readable name
     - description:  non-empty string
     - version:      semver string
     - input_schema: path or dotted reference
     - output_schema:path or dotted reference
     - timeout_sec:  positive number
     - max_retries:  integer >= 0
     - cost_tier:    one of {"free","standard","premium","experimental"} (configurable)
     - safety_policy:non-empty string (policy id or path)
     - enabled:      bool

4) MCP server / tool contracts (if present)
   Required keys:
     - id
     - name
     - description
     - version
     - tools: list of tools, each with:
         - name
         - description
         - input_schema
         - output_schema
         - error_codes: list[str]
         - timeout_sec: > 0
         - retry_policy: present (dict or str)
         - security_policies: present (dict or str)

5) Schema existence & format sanity
   - For any path-like schema reference (e.g. "schemas/....json"):
       -> File must exist under REPO_ROOT
   - For dotted references, only existence is checked at string-level;
     deeper validation is left to schema tooling.

6) Safety & policy hooks
   - Every contract must specify `safety_policy`
   - There must be a top-level `safety_policies` mapping for policy IDs
   - Each referenced safety_policy must be defined in that mapping

7) Timeouts and retries
   - timeout_sec > 0
   - max_retries >= 0
   - For MCP tools, timeout_sec > 0 and retry_policy present

Exit code:
- 0: all checks pass
- 1: any violation detected
"""

import os
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import yaml
except ImportError:
    print("[contract_registry_validator] ERROR: PyYAML is required (pip install pyyaml).")
    sys.exit(1)


DEFAULT_REPO_ROOT = (
    r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines"
    r"\Resume Gen\Git\Agentic_Workflow-10_11"
)
REPO_ROOT = os.getenv("AGENTIC_REPO_ROOT", DEFAULT_REPO_ROOT)

CONTRACT_FILE_CANDIDATES = [
    "contracts.yaml",
    os.path.join("schemas", "contracts.yaml"),
]

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

# Minimal set of allowed cost tiers (can be extended later)
ALLOWED_COST_TIERS = {"free", "standard", "premium", "experimental"}


@dataclass
class Violation:
    code: str
    message: str
    path: str


# =====================================================================
# HELPERS
# =====================================================================

def rel(path: str) -> str:
    try:
        return os.path.relpath(path, REPO_ROOT)
    except ValueError:
        return path


def find_contracts_file() -> Optional[str]:
    for candidate in CONTRACT_FILE_CANDIDATES:
        full = os.path.join(REPO_ROOT, candidate)
        if os.path.isfile(full):
            return full
    return None


def load_yaml(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_semver(s: str) -> bool:
    return bool(SEMVER_RE.match(s))


def is_path_like(schema_ref: str) -> bool:
    # Heuristic: slash or backslash or endswith common extensions
    if any(ch in schema_ref for ch in ("/", "\\")):
        return True
    if schema_ref.lower().endswith((".json", ".yaml", ".yml")):
        return True
    return False


def schema_path_exists(schema_ref: str) -> bool:
    if not is_path_like(schema_ref):
        return True  # dotted references are allowed but not resolved here
    full = os.path.join(REPO_ROOT, schema_ref)
    return os.path.isfile(full)


def is_non_empty_str(val: Any) -> bool:
    return isinstance(val, str) and val.strip() != ""


# =====================================================================
# CORE VALIDATION
# =====================================================================

def validate_contracts_structure(data: Any, path: str, violations: List[Violation]) -> Dict[str, Any]:
    """
    Top-level structural checks. Returns the data if valid, otherwise records violations.
    Expected structure (minimal, extensible):

    contracts.yaml:
      tools:          [ {...}, ... ]
      planners:       [ {...}, ... ]
      executors:      [ {...}, ... ]
      agents:         [ {...}, ... ]
      mcp_servers:    [ {...}, ... ]
      safety_policies:{ policy_id: {...}, ... }
    """
    if not isinstance(data, dict):
        violations.append(
            Violation(
                code="CONTRACTS_ROOT_NOT_MAPPING",
                message="contracts.yaml root must be a mapping/object",
                path=rel(path),
            )
        )
        return {}

    # Not all sections are mandatory, but if present they must be lists/mappings as appropriate.
    sections = {
        "tools": list,
        "planners": list,
        "executors": list,
        "agents": list,
        "mcp_servers": list,
        "safety_policies": dict,
    }

    for key, expected_type in sections.items():
        if key in data and not isinstance(data[key], expected_type):
            violations.append(
                Violation(
                    code="CONTRACTS_SECTION_WRONG_TYPE",
                    message=f"Section '{key}' must be {expected_type.__name__}",
                    path=rel(path),
                )
            )

    return data


def validate_global_ids_unique(
    data: Dict[str, Any],
    path: str,
    violations: List[Violation],
) -> None:
    seen_ids: Set[str] = set()
    sections = ["tools", "planners", "executors", "agents", "mcp_servers"]

    for sec in sections:
        entries = data.get(sec, []) or []
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                violations.append(
                    Violation(
                        code="CONTRACT_ENTRY_NOT_MAPPING",
                        message=f"Entry in section '{sec}' must be a mapping/object",
                        path=rel(path),
                    )
                )
                continue
            cid = entry.get("id")
            if not is_non_empty_str(cid):
                violations.append(
                    Violation(
                        code="CONTRACT_ID_MISSING",
                        message=f"Entry in '{sec}' missing non-empty 'id'",
                        path=rel(path),
                    )
                )
                continue
            if cid in seen_ids:
                violations.append(
                    Violation(
                        code="CONTRACT_ID_DUPLICATE",
                        message=f"Duplicate contract id '{cid}' across sections",
                        path=rel(path),
                    )
                )
            seen_ids.add(cid)


def validate_semver_and_common_fields(
    entry: Dict[str, Any],
    sec: str,
    path: str,
    violations: List[Violation],
) -> None:
    section_kind_map = {
        "tools": "tool",
        "planners": "planner",
        "executors": "executor",
        "agents": "agent",
        "mcp_servers": "mcp_server",
    }
    kind = entry.get("kind") or section_kind_map.get(sec, sec)

    cid = entry.get("id", "<unknown>")
    prefix = f"{sec}:{cid}"

    # name
    if not is_non_empty_str(entry.get("name")):
        violations.append(
            Violation(
                code="CONTRACT_NAME_MISSING",
                message=f"{prefix}: missing non-empty 'name'",
                path=rel(path),
            )
        )

    # description
    if not is_non_empty_str(entry.get("description")):
        violations.append(
            Violation(
                code="CONTRACT_DESCRIPTION_MISSING",
                message=f"{prefix}: missing non-empty 'description'",
                path=rel(path),
            )
        )

    # version
    ver = entry.get("version")
    if not is_non_empty_str(ver) or not is_semver(ver):
        violations.append(
            Violation(
                code="CONTRACT_VERSION_INVALID",
                message=f"{prefix}: 'version' must be semver (e.g. '1.0.0')",
                path=rel(path),
            )
        )

    # enabled
    if "enabled" not in entry or not isinstance(entry["enabled"], bool):
        violations.append(
            Violation(
                code="CONTRACT_ENABLED_INVALID",
                message=f"{prefix}: 'enabled' must be a boolean",
                path=rel(path),
            )
        )

    # safety_policy
    if not is_non_empty_str(entry.get("safety_policy")):
        violations.append(
            Violation(
                code="CONTRACT_SAFETY_POLICY_MISSING",
                message=f"{prefix}: 'safety_policy' must be specified",
                path=rel(path),
            )
        )

    # cost_tier
    cost_tier = entry.get("cost_tier")
    if cost_tier not in ALLOWED_COST_TIERS:
        violations.append(
            Violation(
                code="CONTRACT_COST_TIER_INVALID",
                message=(
                    f"{prefix}: 'cost_tier' must be one of "
                    f"{sorted(ALLOWED_COST_TIERS)}, got '{cost_tier}'"
                ),
                path=rel(path),
            )
        )

    # timeouts / retries (tools, planners, executors, agents)
    # agents may not have explicit timeouts, but enforcing is safer.
    timeout = entry.get("timeout_sec")
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        violations.append(
            Violation(
                code="CONTRACT_TIMEOUT_INVALID",
                message=f"{prefix}: 'timeout_sec' must be > 0",
                path=rel(path),
            )
        )

    retries = entry.get("max_retries")
    if not isinstance(retries, int) or retries < 0:
        violations.append(
            Violation(
                code="CONTRACT_RETRIES_INVALID",
                message=f"{prefix}: 'max_retries' must be integer >= 0",
                path=rel(path),
            )
        )

    # input/output schemas
    for key in ("input_schema", "output_schema"):
        schema_ref = entry.get(key)
        if not is_non_empty_str(schema_ref):
            violations.append(
                Violation(
                    code="CONTRACT_SCHEMA_MISSING",
                    message=f"{prefix}: '{key}' must be a non-empty string",
                    path=rel(path),
                )
            )
        else:
            if not schema_path_exists(schema_ref):
                violations.append(
                    Violation(
                        code="CONTRACT_SCHEMA_MISSING_FILE",
                        message=f"{prefix}: schema path not found: '{schema_ref}'",
                        path=rel(path),
                    )
                )


def validate_tools_planners_executors(
    data: Dict[str, Any],
    path: str,
    violations: List[Violation],
) -> None:
    for sec in ("tools", "planners", "executors", "agents"):
        entries = data.get(sec, []) or []
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                violations.append(
                    Violation(
                        code="CONTRACT_ENTRY_NOT_MAPPING",
                        message=f"Entry in section '{sec}' must be a mapping/object",
                        path=rel(path),
                    )
                )
                continue
            validate_semver_and_common_fields(entry, sec, path, violations)


def validate_mcp_servers(
    data: Dict[str, Any],
    path: str,
    violations: List[Violation],
) -> None:
    servers = data.get("mcp_servers", []) or []
    if not isinstance(servers, list):
        return

    for server in servers:
        if not isinstance(server, dict):
            violations.append(
                Violation(
                    code="MCP_SERVER_NOT_MAPPING",
                    message="Each mcp_server entry must be a mapping/object",
                    path=rel(path),
                )
            )
            continue

        cid = server.get("id", "<unknown>")
        prefix = f"mcp_server:{cid}"

        # minimal fields
        for key in ("id", "name", "description", "version"):
            if not is_non_empty_str(server.get(key)):
                violations.append(
                    Violation(
                        code="MCP_SERVER_FIELD_MISSING",
                        message=f"{prefix}: missing non-empty '{key}'",
                        path=rel(path),
                    )
                )

        ver = server.get("version")
        if not is_non_empty_str(ver) or not is_semver(ver):
            violations.append(
                Violation(
                    code="MCP_SERVER_VERSION_INVALID",
                    message=f"{prefix}: 'version' must be semver (e.g. '1.0.0')",
                    path=rel(path),
                )
            )

        tools = server.get("tools", [])
        if not isinstance(tools, list) or not tools:
            violations.append(
                Violation(
                    code="MCP_SERVER_TOOLS_MISSING",
                    message=f"{prefix}: 'tools' must be a non-empty list",
                    path=rel(path),
                )
            )
            continue

        for t in tools:
            if not isinstance(t, dict):
                violations.append(
                    Violation(
                        code="MCP_TOOL_NOT_MAPPING",
                        message=f"{prefix}: tool entry must be a mapping/object",
                        path=rel(path),
                    )
                )
                continue

            tname = t.get("name", "<unknown>")
            tprefix = f"{prefix}.tool:{tname}"

            for key in ("name", "description", "input_schema", "output_schema"):
                if not is_non_empty_str(t.get(key)):
                    violations.append(
                        Violation(
                            code="MCP_TOOL_FIELD_MISSING",
                            message=f"{tprefix}: missing non-empty '{key}'",
                            path=rel(path),
                        )
                    )

            # schema existence
            for sk in ("input_schema", "output_schema"):
                sref = t.get(sk)
                if is_non_empty_str(sref) and not schema_path_exists(sref):
                    violations.append(
                        Violation(
                            code="MCP_TOOL_SCHEMA_MISSING_FILE",
                            message=f"{tprefix}: schema file not found '{sref}'",
                            path=rel(path),
                        )
                    )

            # error_codes
            err_codes = t.get("error_codes")
            if not isinstance(err_codes, list) or not all(is_non_empty_str(e) for e in err_codes):
                violations.append(
                    Violation(
                        code="MCP_TOOL_ERROR_CODES_INVALID",
                        message=f"{tprefix}: 'error_codes' must be a list of strings",
                        path=rel(path),
                    )
                )

            # timeout
            timeout = t.get("timeout_sec")
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                violations.append(
                    Violation(
                        code="MCP_TOOL_TIMEOUT_INVALID",
                        message=f"{tprefix}: 'timeout_sec' must be > 0",
                        path=rel(path),
                    )
                )

            # retry_policy
            if "retry_policy" not in t:
                violations.append(
                    Violation(
                        code="MCP_TOOL_RETRY_POLICY_MISSING",
                        message=f"{tprefix}: 'retry_policy' must be defined",
                        path=rel(path),
                    )
                )

            # security_policies
            if "security_policies" not in t:
                violations.append(
                    Violation(
                        code="MCP_TOOL_SECURITY_POLICIES_MISSING",
                        message=f"{tprefix}: 'security_policies' must be defined",
                        path=rel(path),
                    )
                )


def validate_safety_policies(
    data: Dict[str, Any],
    path: str,
    violations: List[Violation],
) -> None:
    safety_policies = data.get("safety_policies", {})
    if not isinstance(safety_policies, dict):
        violations.append(
            Violation(
                code="SAFETY_POLICIES_MISSING",
                message="Top-level 'safety_policies' mapping must be present",
                path=rel(path),
            )
        )
        return

    # ensure each policy id is non-empty string
    for pid, pol in safety_policies.items():
        if not is_non_empty_str(pid):
            violations.append(
                Violation(
                    code="SAFETY_POLICY_ID_INVALID",
                    message="Safety policy id must be a non-empty string",
                    path=rel(path),
                )
            )
        if not isinstance(pol, dict):
            violations.append(
                Violation(
                    code="SAFETY_POLICY_NOT_MAPPING",
                    message=f"Safety policy '{pid}' must be a mapping/object",
                    path=rel(path),
                )
            )


def validate_safety_references(
    data: Dict[str, Any],
    path: str,
    violations: List[Violation],
) -> None:
    safety_policies = data.get("safety_policies", {})
    if not isinstance(safety_policies, dict):
        # Already flagged by validate_safety_policies
        return

    available_policies: Set[str] = set(safety_policies.keys())
    sections = ["tools", "planners", "executors", "agents", "mcp_servers"]

    for sec in sections:
        entries = data.get(sec, []) or []
        if not isinstance(entries, list):
            continue

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            cid = entry.get("id", "<unknown>")
            sp = entry.get("safety_policy")
            if not is_non_empty_str(sp):
                # Already flagged in common field validation.
                continue
            if sp not in available_policies:
                violations.append(
                    Violation(
                        code="SAFETY_POLICY_REFERENCE_UNKNOWN",
                        message=f"{sec}:{cid}: safety_policy '{sp}' not defined in safety_policies",
                        path=rel(path),
                    )
                )


# =====================================================================
# MAIN
# =====================================================================

def main() -> None:
    violations: List[Violation] = []

    if not os.path.isdir(REPO_ROOT):
        print(f"[contract_registry_validator] ERROR: REPO_ROOT does not exist: {REPO_ROOT}")
        sys.exit(1)

    contracts_path = find_contracts_file()
    if not contracts_path:
        violations.append(
            Violation(
                code="CONTRACTS_FILE_MISSING",
                message=f"No contracts.yaml found (checked: {', '.join(CONTRACT_FILE_CANDIDATES)})",
                path=rel(REPO_ROOT),
            )
        )
    else:
        try:
            data = load_yaml(contracts_path)
        except Exception as e:
            violations.append(
                Violation(
                    code="CONTRACTS_YAML_LOAD_ERROR",
                    message=f"Failed to load contracts.yaml: {e}",
                    path=rel(contracts_path),
                )
            )
            data = {}

        if data:
            data = validate_contracts_structure(data, contracts_path, violations)
            if data:
                validate_global_ids_unique(data, contracts_path, violations)
                validate_tools_planners_executors(data, contracts_path, violations)
                validate_mcp_servers(data, contracts_path, violations)
                validate_safety_policies(data, contracts_path, violations)
                validate_safety_references(data, contracts_path, violations)

    if not violations:
        print("[contract_registry_validator] OK: All contract registry checks passed.")
        sys.exit(0)

    print("[contract_registry_validator] FAIL: Violations detected.")
    for v in violations:
        print(f"[{v.code}] {v.message} :: {v.path}")
    sys.exit(1)


if __name__ == "__main__":
    main()
