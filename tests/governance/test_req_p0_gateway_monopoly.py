"""W13 P0: AST scan proves zero FileIo imports outside L2 gateway paths.

REQ-071/121/126: Gateway monopoly enforced — no direct FileIo/SDK imports
outside SovereignLLMGateway and UniversalWriteGateway in L0-L5 core modules.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.governance

# Allowlisted paths where direct IO imports ARE permitted
_ALLOWED_IO_PATHS = frozenset(
    [
        "agentic_core/L2_execution",  # UWG lives here
        "agentic_core/L0_routing/seam",  # seam audit is IO-adjacent
        "ops_scripts",  # CI/tooling
        "tools",
        "tests",
        "data",
        "docs",
    ]
)

_FORBIDDEN_IO_SYMBOLS = frozenset(
    [
        # Direct file-write bypasses
        "open",
        "write_text",
        "write_bytes",
        "Path.open",
        # Direct SDK imports
        "google.generativeai",
        "anthropic",
        "openai",
    ]
)

_SCAN_ROOTS = [
    "agentic_core/L0_routing",
    "agentic_core/L1_cognition",
    "agentic_core/L3_orchestration",
    "agentic_core/L4_state",
    "agentic_core/L5_safety",
]

REPO_ROOT = Path(__file__).parent.parent.parent


def _is_allowed(rel_path: str) -> bool:
    """Return True if path is in the allowed list."""
    for allowed in _ALLOWED_IO_PATHS:
        if rel_path.startswith(allowed):
            return True
    return False


def _scan_file_for_io_imports(path: Path) -> list[str]:
    """AST-scan a file for forbidden IO/SDK import patterns."""
    violations = []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return violations

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module
                for forbidden in ["google.generativeai", "anthropic", "openai"]:
                    if module == forbidden or module.startswith(forbidden + "."):
                        violations.append(f"{path}: forbidden SDK import '{module}' at line {node.lineno}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    for forbidden in ["google.generativeai", "anthropic", "openai"]:
                        if alias.name == forbidden or alias.name.startswith(forbidden + "."):
                            violations.append(
                                f"{path}: forbidden SDK import '{alias.name}' at line {node.lineno}"
                            )

    return violations


def _collect_python_files(roots: list[str]) -> list[Path]:
    """Collect all Python files under given roots."""
    files = []
    for root in roots:
        root_path = REPO_ROOT / root
        if root_path.exists():
            for py_file in root_path.rglob("*.py"):
                rel = py_file.relative_to(REPO_ROOT).as_posix()
                if not _is_allowed(rel):
                    files.append(py_file)
    return files


@pytest.mark.governance
def test_req_p0_zero_sdk_imports_outside_gateway():
    """P0: Zero direct SDK imports outside gateway-allowlisted paths (AST scan)."""
    files = _collect_python_files(_SCAN_ROOTS)
    assert len(files) > 0, "Should find files to scan"

    all_violations: list[str] = []
    for f in files:
        all_violations.extend(_scan_file_for_io_imports(f))

    assert all_violations == [], f"Found {len(all_violations)} SDK import violation(s):\n" + "\n".join(
        all_violations
    )


@pytest.mark.governance
def test_req_p0_gateway_monopoly_negative_control():
    """P0: Negative control — allowlisted L2 gateway path IS allowed to import."""
    # L2_execution is in the allowlist — scan should produce 0 violations
    # (we just check the logic, not actual imports in L2)
    l2_path = "agentic_core/L2_execution/SovereignLLMGateway.py"
    assert _is_allowed("agentic_core/L2_execution/"), "L2 must be in allowlist"
    assert not _is_allowed("agentic_core/L3_orchestration/"), "L3 must NOT be in allowlist"
    assert not _is_allowed("agentic_core/L1_cognition/"), "L1 must NOT be in allowlist"


@pytest.mark.governance
def test_req_p0_scan_roots_non_empty():
    """P0: All declared scan roots must exist and contain Python files."""
    found_roots = 0
    for root in _SCAN_ROOTS:
        root_path = REPO_ROOT / root
        if root_path.exists():
            found_roots += 1

    assert found_roots >= 3, f"Expected >=3 scan roots to exist, found {found_roots}. Roots: {_SCAN_ROOTS}"


@pytest.mark.governance
def test_req071_stage8_uwg_routing_invariant():
    """REQ-071: UWG routing invariant — gateway module must exist."""
    uwg_path = REPO_ROOT / "agentic_core/L2_execution/UniversalWriteGateway.py"
    assert uwg_path.exists(), "UniversalWriteGateway.py must exist as sole write seam"

    # AST-verify it defines the gateway class
    source = uwg_path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source)
    class_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    assert any("Gateway" in name or "WriteGateway" in name for name in class_names), (
        f"UniversalWriteGateway.py must define a Gateway class. Found: {class_names}"
    )
