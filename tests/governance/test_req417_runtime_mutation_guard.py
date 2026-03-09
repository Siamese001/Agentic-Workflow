"""REQ-417: runtime mutation guard — block core-module reload and sys.modules injection."""

from __future__ import annotations

import importlib

import pytest

from agentic_core.L0_routing.config.path_constants import (
    OPS_SCRIPTS_DIR,
)
from agentic_core.L5_safety.enforcement.runtime_mutation_guardrail import (
    _CORE_PREFIXES,
    _guarded_setattr,
    _GuardedSysModules,
    install_guards,
)


@pytest.mark.governance
def test_install_guards_is_idempotent() -> None:
    """install_guards() MUST be callable multiple times without error or double-patching."""
    install_guards()
    install_guards()
    install_guards()
    assert True  # no-exception contract


@pytest.mark.governance
def test_importlib_reload_core_module_is_blocked() -> None:
    """importlib.reload of a core-prefix module MUST raise ImportError with REQ-417."""
    import agentic_core.L2_execution.UniversalWriteGateway as _uwg_mod

    with pytest.raises(ImportError, match="REQ-417"):
        importlib.reload(_uwg_mod)


@pytest.mark.governance
def test_importlib_reload_stdlib_module_is_allowed() -> None:
    """importlib.reload of a stdlib module MUST NOT be blocked by the guard."""
    import json

    result = importlib.reload(json)
    assert result is json


@pytest.mark.governance
def test_core_prefixes_cover_all_layers() -> None:
    """_CORE_PREFIXES MUST include all canonical app-layer namespaces."""
    required = {"agentic_core.", "apps_lic.", "apps_rg.", "apps_shared.", "system_learning."}
    missing = required - set(_CORE_PREFIXES)
    assert not missing, f"Missing core prefixes: {missing}"


# =============================================================================
# sys.modules guard (_GuardedSysModules)
# =============================================================================


@pytest.mark.governance
def test_guarded_sys_modules_allows_new_key() -> None:
    """_GuardedSysModules MUST allow adding a new core-prefix key (initial import)."""
    guarded: _GuardedSysModules = _GuardedSysModules()
    guarded["agentic_core.new_module_xyz"] = object()
    assert True  # no-exception contract


@pytest.mark.governance
def test_sys_modules_replacement_blocked_for_core_module() -> None:
    """_GuardedSysModules MUST raise ImportError when replacing an already-loaded core key."""
    guarded: _GuardedSysModules = _GuardedSysModules()
    sentinel = object()
    guarded["agentic_core.L2_execution.UniversalWriteGateway"] = sentinel

    with pytest.raises(ImportError, match="REQ-417"):
        guarded["agentic_core.L2_execution.UniversalWriteGateway"] = object()


@pytest.mark.governance
def test_guarded_sys_modules_allows_non_core_replacement() -> None:
    """_GuardedSysModules MUST allow replacement of non-core-prefix keys."""
    guarded: _GuardedSysModules = _GuardedSysModules()
    guarded["third_party.lib"] = object()
    guarded["third_party.lib"] = object()
    assert True  # no-exception contract


# =============================================================================
# setattr reference guard
# =============================================================================


@pytest.mark.governance
def test_guarded_setattr_raises_for_core_instance() -> None:
    """_guarded_setattr MUST raise AttributeError with REQ-417 for core-layer instances."""
    from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway

    uwg = UniversalWriteGateway()
    with pytest.raises(AttributeError, match="REQ-417"):
        _guarded_setattr(uwg, "injected_attr", "bad_value")


@pytest.mark.governance
def test_guarded_setattr_allows_non_core_instance() -> None:
    """_guarded_setattr MUST allow attribute setting on non-core instances."""

    class _Innocent:
        pass

    obj = _Innocent()
    _guarded_setattr(obj, "x", 42)
    assert obj.x == 42


# =============================================================================
# SOV-DELTA: object.__setattr__ AST scanner smoke test
# =============================================================================


@pytest.mark.governance
def test_object_dunder_setattr_scanner_exists() -> None:
    """SOV-DELTA: ops_scripts/ci/check_object_dunder_setattr.py MUST exist and be importable."""
    from pathlib import Path

    scanner = Path(__file__).resolve().parents[2] / OPS_SCRIPTS_DIR / "ci" / "check_object_dunder_setattr.py"
    assert scanner.exists(), "check_object_dunder_setattr.py not found"


@pytest.mark.governance
def test_object_dunder_setattr_scanner_detects_core_pattern() -> None:
    """SOV-DELTA AST scanner MUST detect object.__setattr__(uwg, ...) patterns."""
    import ast
    import sys

    sys.path.insert(0, str(__file__))

    from pathlib import Path

    scanner_path = (
        Path(__file__).resolve().parents[2] / OPS_SCRIPTS_DIR / "ci" / "check_object_dunder_setattr.py"
    )
    snippet = "object.__setattr__(uwg, 'x', 1)"
    tree = ast.parse(snippet)

    import importlib.util

    spec = importlib.util.spec_from_file_location("check_osd", scanner_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    call_node = tree.body[0].value  # type: ignore[attr-defined]
    assert mod._is_object_dunder_setattr(call_node) is True
    assert mod._arg0_is_core_name(call_node) is True
