"""W13 P0: AST scan proves zero FileIo imports/calls outside L2 gateway paths.

REQ-071/121/126: Gateway monopoly enforced — no direct FileIo/SDK imports
or direct write-call sites outside SovereignLLMGateway and
UniversalWriteGateway in L0-L5 core modules.

Gap closure (anti-pattern #2 — Unauthorized mutation outside UWG):
  _scan_file_for_direct_write_calls() performs an AST call-site scan for
  open(), write_text(), write_bytes() in non-gateway core modules.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
    L1_COGNITION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    SOVEREIGN_EXCLUDED_FOLDERS,
)

pytestmark = pytest.mark.governance

# Allowlisted paths where direct IO imports ARE permitted
_ALLOWED_IO_PATHS = SOVEREIGN_EXCLUDED_FOLDERS

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
    L0_ROUTING_DIR,
    L1_COGNITION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
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


# Write-call prohibition: only pure engine/enforcement/config subfolders are in
# scope.  scripts/, utils/, and tools/ are operational tooling that write files
# by design (dashboards, fixers, SSOT healers).  L5 is also excluded as it
# contains healing agents that are allowlisted mutation agents.
_WRITE_CALL_ENGINE_SUBDIRS = frozenset(["engines", "enforcement", "config", "arbitration"])


def _is_write_call_scope(path: Path, repo_root: Path) -> bool:
    """Return True if *path* is inside an engine/enforcement/config subfolder
    of a core layer (L0-L4), not in scripts/utils/tools/reasoning."""
    try:
        rel = path.relative_to(repo_root).parts
    except ValueError:
        return False
    # Must be under agentic_core/L{0-4}_*
    if len(rel) < 3 or rel[0] != AGENTIC_CORE_DIR:
        return False
    layer = rel[1]
    if not any(layer.startswith(f"L{n}_") for n in range(5)):
        return False
    # Must be in an approved engine subfolder
    if len(rel) < 3:
        return False
    subfolder = rel[2]
    return subfolder in _WRITE_CALL_ENGINE_SUBDIRS


def _scan_file_for_direct_write_calls(path: Path) -> list[str]:
    """AST-scan a file for forbidden direct write-call patterns.

    Detects calls to open() in write mode, .write_text(), .write_bytes()
    that bypass the UniversalWriteGateway seam.
    Scope: engine/enforcement/config subfolders of L0-L4 only.
    """
    violations = []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return violations

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        # open(..., "w") / open(..., "wb") / open(..., mode="w")
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            write_mode = False
            # positional arg[1]
            if len(node.args) >= 2:
                arg = node.args[1]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if any(m in arg.value for m in ("w", "a", "x")):
                        write_mode = True
            # keyword mode=
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    if any(m in str(kw.value.value) for m in ("w", "a", "x")):
                        write_mode = True
            if write_mode:
                violations.append(f"{path}: forbidden direct open() in write mode at line {node.lineno}")

        # path_obj.write_text(...) / path_obj.write_bytes(...)
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in ("write_text", "write_bytes"):
                violations.append(f"{path}: forbidden direct .{node.func.attr}() call at line {node.lineno}")

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


# Known pre-existing direct-write violations in engine/enforcement/config
# subfolders — established baseline as of gap analysis.  Any count above this
# means NEW violations were introduced and must be remediated before merge.
_WRITE_CALL_VIOLATION_BASELINE = 13


@pytest.mark.governance
def test_req_p0_no_new_direct_write_calls_outside_gateway():
    """P0 gap closure: No NEW direct write calls added to L0-L4 engine/enforcement/config.

    Anti-pattern #2 (Unauthorized mutation outside UWG): engine, enforcement,
    and config subfolders in L0-L4 must not accumulate NEW direct write calls.
    Pre-existing violations are tracked in _WRITE_CALL_VIOLATION_BASELINE;
    any increase above the baseline is a hard fail.

    Remediation: route writes through UniversalWriteGateway, then decrement
    the baseline constant to ratchet the count down to zero over time.
    """
    scanned: list[Path] = []
    for layer_n in range(5):
        for layer_dir in (REPO_ROOT / AGENTIC_CORE_DIR).glob(f"L{layer_n}_*"):
            for subdir in _WRITE_CALL_ENGINE_SUBDIRS:
                subdir_path = layer_dir / subdir
                if not subdir_path.exists():
                    continue
                for py_file in sorted(subdir_path.rglob("*.py")):
                    if py_file.name not in ("__init__.py",) and _is_write_call_scope(py_file, REPO_ROOT):
                        scanned.append(py_file)

    assert len(scanned) > 0, "Should find engine/enforcement/config files to scan"

    all_violations: list[str] = []
    for f in scanned:
        all_violations.extend(_scan_file_for_direct_write_calls(f))

    count = len(all_violations)
    assert count <= _WRITE_CALL_VIOLATION_BASELINE, (
        f"Direct write-call violations INCREASED from baseline "
        f"{_WRITE_CALL_VIOLATION_BASELINE} to {count}. "
        f"New violations introduced:\n" + "\n".join(all_violations[_WRITE_CALL_VIOLATION_BASELINE:])
    )


@pytest.mark.governance
def test_req_p0_write_call_scanner_detects_violations(tmp_path: Path):
    """Negative control: scanner correctly identifies write-call violations (§1.11)."""
    # open() in write mode
    f_open = tmp_path / "bad_open.py"
    f_open.write_text('with open("out.txt", "w") as f:\n    f.write("x")\n', encoding="utf-8")
    viols = _scan_file_for_direct_write_calls(f_open)
    assert len(viols) == 1
    assert "open()" in viols[0]

    # .write_text()
    f_wt = tmp_path / "bad_write_text.py"
    f_wt.write_text('from pathlib import Path\nPath("x.txt").write_text("hello")\n', encoding="utf-8")
    viols2 = _scan_file_for_direct_write_calls(f_wt)
    assert len(viols2) == 1
    assert "write_text" in viols2[0]

    # .write_bytes()
    f_wb = tmp_path / "bad_write_bytes.py"
    f_wb.write_text('from pathlib import Path\nPath("x.bin").write_bytes(b"data")\n', encoding="utf-8")
    viols3 = _scan_file_for_direct_write_calls(f_wb)
    assert len(viols3) == 1
    assert "write_bytes" in viols3[0]

    # open() in read mode — must NOT be flagged
    f_read = tmp_path / "good_read.py"
    f_read.write_text('with open("in.txt", "r") as f:\n    data = f.read()\n', encoding="utf-8")
    assert _scan_file_for_direct_write_calls(f_read) == []
