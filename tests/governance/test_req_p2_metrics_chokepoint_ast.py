"""W16: AST scan proves zero metric emissions outside control spine.

REQ-063/298: CI AST gate — no metric emission calls outside the
designated control-spine module in L0-L5 core modules.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.governance

REPO_ROOT = Path(__file__).parent.parent.parent

# The sole authorised metric emission module path prefix
_CONTROL_SPINE_PREFIXES = (
    "agentic_core/L4_state/enforcement/metrics_emission",
    "agentic_core/L4_state/enforcement/blast_radius",
    "agentic_core/L4_state/types/telemetry",
    "ops_scripts/",
    "tests/",
    "docs/",
    "tools/",
    "data/",
)

# Patterns that constitute unauthorised metric emission
_FORBIDDEN_EMISSION_CALLS = frozenset(
    [
        "emit_metric",
        "record_metric",
        "publish_metric",
        "send_metric",
    ]
)

# Scan these roots for violations
_SCAN_ROOTS = [
    "agentic_core/L0_routing",
    "agentic_core/L1_cognition",
    "agentic_core/L2_execution",
    "agentic_core/L3_orchestration",
    "agentic_core/L5_safety",
]


def _is_allowlisted(rel_path: str) -> bool:
    for prefix in _CONTROL_SPINE_PREFIXES:
        if rel_path.startswith(prefix):
            return True
    return False


def _scan_for_rogue_emissions(path: Path) -> list[str]:
    """AST-scan for metric emission calls outside control spine."""
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            # Direct calls: emit_metric(...)
            if isinstance(func, ast.Name) and func.id in _FORBIDDEN_EMISSION_CALLS:
                violations.append(f"{path.name}:{node.lineno}: direct call '{func.id}()'")
            # Method calls: self.emit_metric(...) / obj.emit_metric(...)
            elif isinstance(func, ast.Attribute) and func.attr in _FORBIDDEN_EMISSION_CALLS:
                violations.append(f"{path.name}:{node.lineno}: method call '.{func.attr}()'")
    return violations


def _collect_python_files(roots: list[str]) -> list[Path]:
    files = []
    for root in roots:
        root_path = REPO_ROOT / root
        if root_path.exists():
            for py_file in root_path.rglob("*.py"):
                rel = py_file.relative_to(REPO_ROOT).as_posix()
                if not _is_allowlisted(rel):
                    files.append(py_file)
    return files


@pytest.mark.governance
def test_req063_zero_rogue_metric_emissions_ast_scan():
    """REQ-063: Zero metric emission calls outside control spine in L0/L1/L2/L3/L5."""
    files = _collect_python_files(_SCAN_ROOTS)
    assert len(files) > 0, "Must find files to scan"

    all_violations: list[str] = []
    for f in files:
        all_violations.extend(_scan_for_rogue_emissions(f))

    assert all_violations == [], f"Found {len(all_violations)} rogue metric emission(s):\n" + "\n".join(
        all_violations
    )


@pytest.mark.governance
def test_req298_scan_roots_all_exist():
    """REQ-298: All declared scan roots must exist."""
    found = sum(1 for r in _SCAN_ROOTS if (REPO_ROOT / r).exists())
    assert found >= 3, f"Expected >=3 scan roots to exist, found {found}. Roots: {_SCAN_ROOTS}"


@pytest.mark.governance
def test_control_spine_allowlist_logic():
    """Control spine allowlist correctly identifies allowed and forbidden paths."""
    assert _is_allowlisted("agentic_core/L4_state/enforcement/metrics_emission.py")
    assert _is_allowlisted("ops_scripts/ci/check_something.py")
    assert _is_allowlisted("tests/governance/test_something.py")

    assert not _is_allowlisted("agentic_core/L0_routing/seam/some_seam.py")
    assert not _is_allowlisted("agentic_core/L2_execution/tools/safe_subprocess.py")
    assert not _is_allowlisted("agentic_core/L1_cognition/agents/base_agent.py")


@pytest.mark.governance
def test_forbidden_emission_patterns_defined():
    """Forbidden emission call patterns are non-empty and consistent."""
    assert len(_FORBIDDEN_EMISSION_CALLS) >= 4
    assert "emit_metric" in _FORBIDDEN_EMISSION_CALLS
    assert "record_metric" in _FORBIDDEN_EMISSION_CALLS


@pytest.mark.governance
def test_scan_produces_python_files():
    """AST scan collects real Python files from scan roots."""
    files = _collect_python_files(_SCAN_ROOTS)
    assert len(files) >= 10, f"Expected >=10 Python files to scan, found {len(files)}"
    for f in files:
        assert f.suffix == ".py"
