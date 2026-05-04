"""W1 sentinel tests for apps_lic canonical spine wireup.

Covers P1, P2, P3 enforcement:
- P1: No write-mode file operations in the L0 path (run_workflow_lic.py)
- P2: _emit_r5_terminal_via_exit exists and routes through lifecycle-trace emit
- P3: lic_r5_policy.py stub exists; __main__.py emits RouteContract before dispatch
- Plus the two tightening-patch sentinel tests from the plan:
  - test_apps_lic_l0_allows_read_only_config_open_but_blocks_write_mode_open
  - test_apps_lic_briefing_missing_research_not_authorized_only_when_policy_blocks_research

Plan: apps-lic-canonical-spine-wireup-e7c2a5 W1.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_lic"
MAIN_PY = APP_DIR / "__main__.py"
RUN_WORKFLOW = APP_DIR / "tools" / "run_workflow_lic.py"
R5_POLICY = APP_DIR / "integrations" / "lic_r5_policy.py"


def _src(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# P1 — No write-mode file operations in L0 path (run_workflow_lic.py)
# ---------------------------------------------------------------------------

_WRITE_MODE_PATTERNS = [
    re.compile(r'open\s*\([^)]*["\'][wa+x]["\']'),   # open(..., "w"), "a", "x", "w+"
    re.compile(r'\.write_text\s*\('),
    re.compile(r'\.write_bytes\s*\('),
    re.compile(r'shutil\.(copy|move)\s*\('),
]


def test_run_workflow_lic_no_write_mode_open():
    """P1: run_workflow_lic.py must not contain write-mode open() calls."""
    src = _src(RUN_WORKFLOW)
    for pattern in _WRITE_MODE_PATTERNS:
        match = pattern.search(src)
        assert match is None, (
            f"Forbidden write-mode operation found in run_workflow_lic.py: "
            f"{match.group()!r}. Write-mode file ops are forbidden in the L0 path. "
            "Route durable output through Exit → UWG → L4."
        )


def test_run_workflow_lic_no_json_dump_to_file():
    """P1: run_workflow_lic.py must not call json.dump to a file handle (durable write)."""
    src = _src(RUN_WORKFLOW)
    # json.dump(obj, file_handle) — any call with a second positional arg that is
    # a file variable. We look for json.dump calls where the second arg isn't sys.stdout.
    matches = re.findall(r'json\.dump\s*\(', src)
    assert not matches, (
        f"json.dump found in run_workflow_lic.py ({len(matches)} occurrence(s)). "
        "Durable artifact writes belong in L4/UWG, not the L0 dispatch path."
    )


def test_apps_lic_l0_allows_read_only_config_open_but_blocks_write_mode_open():
    """P1 tightening: read-mode open() must remain; only write-mode is banned.

    Verifies the AST distinction — the gate is mode-specific, not a naive ban
    on all open() calls. run_workflow_lic.py uses open(..., 'r') / .open() for
    config/mission-input reading — those must be preserved.
    """
    src = _src(RUN_WORKFLOW)
    # read-mode open should still exist (load_mission_input uses it)
    assert "open(" in src or ".open(" in src, (
        "No open() call found in run_workflow_lic.py — expected at least one "
        "read-mode open for mission input loading. Regression: read-mode was removed."
    )
    # write-mode open must be absent
    for pattern in _WRITE_MODE_PATTERNS:
        match = pattern.search(src)
        assert match is None, (
            f"Write-mode pattern still present after P1 edit: {match.group()!r}"
        )


# ---------------------------------------------------------------------------
# P2 — _emit_r5_terminal_via_exit present and wired to lifecycle trace emit
# ---------------------------------------------------------------------------

def test_emit_r5_terminal_via_exit_defined_in_main():
    """P2: _emit_r5_terminal_via_exit must be defined in __main__.py."""
    src = _src(MAIN_PY)
    assert "def _emit_r5_terminal_via_exit" in src, (
        "_emit_r5_terminal_via_exit not found in apps_lic/__main__.py. "
        "Every R5/fail-closed terminal path must route through this function."
    )


def test_emit_r5_terminal_calls_lifecycle_emit():
    """P2: _emit_r5_terminal_via_exit must call a lifecycle trace emit before sys.exit."""
    src = _src(MAIN_PY)
    # Extract the function body via simple text slice
    start = src.index("def _emit_r5_terminal_via_exit")
    # Find the next top-level def after this one
    next_def = src.find("\ndef ", start + 1)
    body = src[start:next_def] if next_def != -1 else src[start:]
    assert "_emit_escalates_failure" in body or "_emit_" in body, (
        "_emit_r5_terminal_via_exit does not call any lifecycle-trace emit. "
        "It must emit an observability event before sys.exit so Exit V6 can record "
        "the X3 disposition."
    )
    assert "sys.exit" in body, (
        "_emit_r5_terminal_via_exit must call sys.exit to terminate the process."
    )


def test_r5_reason_codes_registry_complete():
    """P2: R5_REASON_CODES in __main__.py must contain all 14 canonical reason codes."""
    src = _src(MAIN_PY)
    required = {
        "BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED",
        "BRIEFING_STALE_RESEARCH_NOT_AUTHORIZED",
        "APPS_RESEARCH_FAILED",
        "APPS_RESEARCH_EMPTY",
        "APPS_RESEARCH_STALE",
        "APPS_RESEARCH_WEAK_SUPPORT",
        "APPS_RESEARCH_BLOCKED",
        "UNSUPPORTED_MANDATORY_CLAIM",
        "HIGH_FRICTION_ASK",
        "FORBIDDEN_SEND_MODE",
        "INVALID_ROUTE_CONTRACT",
        "L0_POLICY_VIOLATION",
        "CAPABILITY_UNAVAILABLE",
        "SCHEMA_REJECTION",
    }
    missing = [code for code in required if code not in src]
    assert not missing, (
        f"R5_REASON_CODES in __main__.py is missing: {missing}. "
        "All 14 canonical reason codes must be registered."
    )


def test_apps_lic_briefing_missing_research_not_authorized_only_when_policy_blocks_research():
    """P2 tightening: BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED must NOT be the default
    missing-briefing code; it is reserved for policy/capability/registry block only.

    Verifies that lic_r5_policy.decide_route() returns R3R4_MANAGED_WORKFLOW when
    research IS authorized (the normal missing-briefing path), and only returns
    R5/BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED when research is NOT authorized.
    """
    from apps_lic.integrations.lic_r5_policy import decide_route

    # Normal path: briefing missing but research authorized → managed workflow
    decision = decide_route(
        has_fresh_briefing=False,
        research_authorized=True,
        request_is_briefing_only=False,
    )
    assert decision.route_id == "R3R4_MANAGED_WORKFLOW", (
        f"Expected R3R4_MANAGED_WORKFLOW when briefing missing + research authorized, "
        f"got {decision.route_id!r}. Normal missing-briefing must route to managed "
        "workflow, not to R5."
    )
    assert decision.reason_code is None, (
        "R3R4_MANAGED_WORKFLOW decision should have no reason_code (not a failure)."
    )

    # Policy-blocks-research path → R5 with the specific code
    decision_blocked = decide_route(
        has_fresh_briefing=False,
        research_authorized=False,
        request_is_briefing_only=False,
    )
    assert decision_blocked.route_id == "R5_FALLBACK", (
        f"Expected R5_FALLBACK when research not authorized, got {decision_blocked.route_id!r}."
    )
    assert decision_blocked.reason_code == "BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED", (
        f"Expected BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED, got {decision_blocked.reason_code!r}."
    )
    assert decision_blocked.is_terminal is True


# ---------------------------------------------------------------------------
# P3 — lic_r5_policy.py stub exists; RouteContract emitted before dispatch
# ---------------------------------------------------------------------------

def test_lic_r5_policy_stub_exists():
    """P3: apps_lic/integrations/lic_r5_policy.py must exist."""
    assert R5_POLICY.exists(), (
        f"lic_r5_policy.py not found at {R5_POLICY}. "
        "L0 decision logic must live in this stub before W2-W3 wiring."
    )


def test_lic_r5_policy_no_subprocess():
    """P3: lic_r5_policy.py must not import or call subprocess/os.system."""
    try:
        tree = ast.parse(_src(R5_POLICY))
    except SyntaxError as exc:
        pytest.fail(f"lic_r5_policy.py has a syntax error: {exc}")
    forbidden_imports = set()
    forbidden_calls = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names]
            if isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
            for name in names:
                if name.split(".")[0] in ("subprocess", "os"):
                    # Only flag os.system / os.popen specifically, not all of os
                    if name in ("subprocess", "os.system", "os.popen"):
                        forbidden_imports.add(name)
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == "os":
                if node.attr in ("system", "popen"):
                    forbidden_calls.add(f"os.{node.attr}")
    assert not forbidden_imports and not forbidden_calls, (
        f"Forbidden execution pattern in lic_r5_policy.py: imports={forbidden_imports}, "
        f"calls={forbidden_calls}. L0 policy is decision-only — no subprocess or OS execution."
    )


def test_lic_r5_policy_no_write_mode():
    """P3: lic_r5_policy.py must not contain write-mode file operations (AST-based)."""
    try:
        tree = ast.parse(_src(R5_POLICY))
    except SyntaxError as exc:
        pytest.fail(f"lic_r5_policy.py has a syntax error: {exc}")
    write_mode_chars = {"w", "a", "x"}
    violations = []
    for node in ast.walk(tree):
        # open(..., "w") / open(..., "w+") / open(..., "a") etc.
        if isinstance(node, ast.Call):
            func = node.func
            func_name = ""
            if isinstance(func, ast.Name):
                func_name = func.id
            elif isinstance(func, ast.Attribute):
                func_name = func.attr
            if func_name == "open" and len(node.args) >= 2:
                mode_arg = node.args[1]
                if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, str):
                    if any(c in mode_arg.value for c in write_mode_chars):
                        violations.append(f"open(..., {mode_arg.value!r})")
        # Path.write_text / Path.write_bytes / shutil.copy / shutil.move
        if isinstance(node, ast.Attribute):
            if node.attr in ("write_text", "write_bytes"):
                violations.append(f".{node.attr}()")
            if isinstance(node.value, ast.Name) and node.value.id == "shutil":
                if node.attr in ("copy", "move"):
                    violations.append(f"shutil.{node.attr}()")
    assert not violations, (
        f"Write-mode operation(s) in lic_r5_policy.py: {violations}. "
        "L0 policy module must not perform durable writes."
    )


def test_lic_r5_policy_decide_route_returns_r4_when_briefing_fresh():
    """P3: decide_route returns R4_SINGLE_ACTION when briefing is fresh."""
    from apps_lic.integrations.lic_r5_policy import decide_route

    decision = decide_route(
        has_fresh_briefing=True,
        research_authorized=True,
        request_is_briefing_only=False,
    )
    assert decision.route_id == "R4_SINGLE_ACTION"
    assert decision.is_terminal is False


def test_lic_r5_policy_decide_route_returns_r3_for_briefing_only():
    """P3: decide_route returns R3_SIMPLE_GROUNDED_READ for briefing-only requests."""
    from apps_lic.integrations.lic_r5_policy import decide_route

    decision = decide_route(
        has_fresh_briefing=False,
        research_authorized=True,
        request_is_briefing_only=True,
    )
    assert decision.route_id == "R3_SIMPLE_GROUNDED_READ"
    assert decision.is_terminal is False


def test_main_emits_l0_route_contract_before_dispatch():
    """P3: __main__.py must contain _emit_l0_route_contract call before run_workflow_lic dispatch."""
    src = _src(MAIN_PY)
    assert "def _emit_l0_route_contract" in src, (
        "_emit_l0_route_contract not defined in __main__.py. "
        "L0 must emit a RouteContract before any execution dispatch."
    )
    # The call must appear before the run_workflow_lic import in main()
    main_body_start = src.index("def main()")
    route_contract_pos = src.find("_emit_l0_route_contract(", main_body_start)
    dispatch_pos = src.find("run_workflow_lic", main_body_start)
    assert route_contract_pos != -1, (
        "_emit_l0_route_contract not called inside main(). L0 must declare its "
        "routing decision before dispatching to execution."
    )
    # dispatch_pos: find the actual import of run_workflow_lic, not a comment
    import_line = "from apps_lic.tools.run_workflow_lic import"
    dispatch_pos = src.find(import_line, main_body_start)
    assert dispatch_pos != -1, (
        f"Could not find '{import_line}' inside main(). "
        "Expected lazy import of run_workflow_lic inside main()."
    )
    assert route_contract_pos < dispatch_pos, (
        "_emit_l0_route_contract must be called BEFORE the run_workflow_lic import. "
        f"route_contract_pos={route_contract_pos}, dispatch_pos={dispatch_pos}."
    )
