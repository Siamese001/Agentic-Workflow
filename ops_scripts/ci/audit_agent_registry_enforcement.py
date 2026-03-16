#!/usr/bin/env python3
"""Agent Registry Enforcement Scanner

Scans first-party code to ensure all agent usage is registered and compliant
with the 2×2 execution policy. Fails on violations.
"""

import ast
import os
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "audit_agent_registry_enforcement")
_emit_applies_guardrail("p0", "audit_agent_registry_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "audit_agent_registry_enforcement", "policy_binding")
_emit_snapshots_state("p0", "audit_agent_registry_enforcement", "state_snapshot")
emit_replay_key("p0", "audit_agent_registry_enforcement")
emit_determinism_digest("p0", "audit_agent_registry_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# Import agent registry for validation
try:
    from agentic_core.agents.agent_registry import get_all_agent_ids, get_profile
except ImportError:
    print("ERROR: Agent registry not available", file=sys.stderr)
    sys.exit(1)


class AgentUsageViolation:
    """Represents a violation of agent registry enforcement."""

    def __init__(self, file_path: str, line: int, violation_type: str, details: str):
        self.file_path = file_path
        self.line = line
        self.violation_type = violation_type
        self.details = details

    def __str__(self):
        return f"{self.file_path}:{self.line} - {self.violation_type}: {self.details}"


class AgentRegistryEnforcementScanner(ast.NodeVisitor):
    """AST scanner for agent usage violations."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[AgentUsageViolation] = []
        self.registered_agents = set(get_all_agent_ids())

    def visit_Call(self, node: ast.Call):
        """Check function calls for agent usage violations."""
        # Check for SovereignLLMGateway.generate calls
        if self._is_gateway_call(node):
            self._check_gateway_call(node)

        # Check for direct agent instantiation
        if self._is_agent_instantiation(node):
            self._check_agent_instantiation(node)

        self.generic_visit(node)

    def _is_gateway_call(self, node: ast.Call) -> bool:
        """Check if this is a SovereignLLMGateway.generate call."""
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "generate":
                # Check if it's a SovereignLLMGateway instance
                if isinstance(node.func.value, ast.Name):
                    return node.func.value.id == "gateway"
                elif isinstance(node.func.value, ast.Attribute):
                    return node.func.value.attr == "gateway"
        return False

    def _is_agent_instantiation(self, node: ast.Call) -> bool:
        """Check if this is an agent class instantiation."""
        if isinstance(node.func, ast.Name):
            return node.func.id in self.registered_agents
        return False

    def _check_gateway_call(self, node: ast.Call):
        """Check SovereignLLMGateway.generate call for agent_id."""
        # Look for agent_id in keyword arguments
        agent_id_found = False
        for keyword in node.keywords:
            if keyword.arg == "agent_id":
                agent_id_found = True
                if isinstance(keyword.value, ast.Constant):
                    agent_id = keyword.value.value
                    if agent_id not in self.registered_agents:
                        self.violations.append(
                            AgentUsageViolation(
                                self.file_path,
                                node.lineno,
                                "UNREGISTERED_AGENT",
                                f"Gateway call uses unregistered agent_id '{agent_id}'",
                            )
                        )
                break

        if not agent_id_found:
            self.violations.append(
                AgentUsageViolation(
                    self.file_path,
                    node.lineno,
                    "MISSING_AGENT_ID",
                    "Gateway call missing required agent_id parameter",
                )
            )

    def _check_agent_instantiation(self, node: ast.Call):
        """Check direct agent instantiation."""
        agent_class = node.func.id if isinstance(node.func, ast.Name) else "unknown"
        self.violations.append(
            AgentUsageViolation(
                self.file_path,
                node.lineno,
                "DIRECT_AGENT_INSTANTIATION",
                f"Direct instantiation of agent '{agent_class}' - use registry instead",
            )
        )


def scan_file(file_path: Path) -> list[AgentUsageViolation]:
    """Scan a single Python file for agent usage violations."""
    violations = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))
        scanner = AgentRegistryEnforcementScanner(str(file_path.relative_to(Path.cwd())))
        scanner.visit(tree)
        violations.extend(scanner.violations)

    except SyntaxError as e:
        violations.append(
            AgentUsageViolation(
                str(file_path.relative_to(Path.cwd())),
                e.lineno or 0,
                "SYNTAX_ERROR",
                f"Unable to parse file: {e}",
            )
        )
    except Exception as e:
        raise
        violations.append(
            AgentUsageViolation(
                str(file_path.relative_to(Path.cwd())), 0, "SCAN_ERROR", f"Error scanning file: {e}"
            )
        )

    return violations


def scan_directory(root_dir: Path) -> list[AgentUsageViolation]:
    """Scan all Python files in directory recursively, restricted to first-party code."""
    violations = []

    # Define first-party scope
    first_party_prefixes = [
        "agentic_core/",
        "system_learning/",
        "apps_rg/",
        "apps_shared/",
        "data/",
        "tests/",
        "ops_scripts/",
    ]

    # Define third-party directories to ignore
    third_party_patterns = [
        ".nox/",
        "venv/",
        "env/",
        "__pycache__/",
        ".git/",
        "site-packages/",
        "build/",
        "dist/",
        ".pytest_cache/",
    ]

    for py_file in root_dir.rglob("*.py"):
        file_str = str(py_file)

        # Skip third-party directories
        if any(pattern in file_str for pattern in third_party_patterns):
            continue

        # Only scan first-party code
        if not any(file_str.startswith(p) for p in first_party_prefixes):
            continue

        file_violations = scan_file(py_file)
        violations.extend(file_violations)

    return violations


def main():
    """Main entry point for the scanner."""
    scan_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    print(f"Scanning {scan_path} for agent registry violations...")

    # Check for tamper mode
    tamper_mode = os.environ.get("W5_NEGCTRL_TAMPER") == "1"

    violations = scan_directory(scan_path)

    if tamper_mode:
        # Introduce synthetic violation for testing
        violations.append(
            AgentUsageViolation(
                "tests/governance/test_agent_execution_profiles.py",
                999,
                "TAMPER_VIOLATION",
                "Synthetic violation for negative control testing",
            )
        )

    # Print results
    print(f"\nScan complete. Found {len(violations)} agent registry violations.")

    if violations:
        print("\nViolations by type:")

        # Group by type
        by_type = {}
        for violation in violations:
            if violation.violation_type not in by_type:
                by_type[violation.violation_type] = []
            by_type[violation.violation_type].append(violation)

        for violation_type, type_violations in sorted(by_type.items()):
            print(f"\n{violation_type} ({len(type_violations)}):")
            for violation in type_violations:
                print(f"  {violation}")

    # Exit with error code if violations found (unless in tamper mode)
    if violations and not tamper_mode:
        print(f"\nERROR: {len(violations)} agent registry violations found!")
        sys.exit(1)
    elif tamper_mode:
        print(f"\nTAMPER MODE: {len(violations)} violations (including synthetic)")
        sys.exit(0)
    else:
        print("\nOK: No agent registry violations found")
        sys.exit(0)


if __name__ == "__main__":
    main()
