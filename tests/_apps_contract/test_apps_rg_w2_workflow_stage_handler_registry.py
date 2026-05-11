"""
W2 acceptance tests — workflow stage handler registry + quarantine guards.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W2
Tests:
  - test_managed_workflow_engine_constructs_without_import_error
  - test_workflow_stage_handler_registry_resolves_registered_handler
  - test_workflow_stage_handler_registry_fails_closed_on_missing_handler
  - test_workflow_stage_handler_registry_fails_closed_on_duplicate_handler
  - test_workflow_stage_handler_registry_rejects_quarantined_handler_source
  - test_core_runtime_does_not_import_apps_rg_integrations_hops
  - test_core_runtime_does_not_import_apps_rg_integrations_gates
  - test_quarantined_apps_rg_prompt_assembly_not_imported_by_core_runtime
  - test_quarantined_apps_rg_judge_not_used_as_runtime_authority
  - test_missing_stage_handler_does_not_fallback_to_single_step
  - test_stage_handler_registry_does_not_write_l4
  - test_stage_handler_registry_does_not_emit_x3
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any, Mapping
import pytest

# ---------------------------------------------------------------------------
# Resolve repo root (tests run from repo root OR via pytest discovery)
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _source_files_under(directory: Path, suffix: str = ".py"):
    """Yield all .py files under *directory* recursively."""
    return list(directory.rglob(f"*{suffix}"))


def _file_contains_import_of(source_path: Path, target_module_prefix: str) -> bool:
    """Return True if *source_path* AST-imports from *target_module_prefix*."""
    try:
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == target_module_prefix or alias.name.startswith(
                    target_module_prefix + "."
                ):
                    return True
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == target_module_prefix or module.startswith(
                target_module_prefix + "."
            ):
                return True
    return False


def _agentic_core_active_runtime_files() -> list[Path]:
    """Return .py files in agentic_core/ that are NOT test files."""
    core_dir = _REPO_ROOT / "agentic_core"
    return [
        p for p in core_dir.rglob("*.py")
        if "test_" not in p.name and "__pycache__" not in str(p)
    ]


# ---------------------------------------------------------------------------
# 1. ManagedWorkflowEngine constructs without ImportError
# ---------------------------------------------------------------------------

def test_managed_workflow_engine_constructs_without_import_error():
    """W2 primary blocker: importing ManagedWorkflowEngine must not raise."""
    from agentic_core.L3_orchestration.managed_workflow_router import ManagedWorkflowEngine
    engine = ManagedWorkflowEngine()
    assert engine is not None


# ---------------------------------------------------------------------------
# 2. STAGE_HANDLERS sentinel is empty (no default domain handlers pre-wired)
# ---------------------------------------------------------------------------

def test_stage_handlers_sentinel_is_empty():
    """STAGE_HANDLERS must be an empty dict — no domain handlers pre-registered."""
    from agentic_core.L3_orchestration.workflow_stage_handlers import STAGE_HANDLERS
    assert isinstance(STAGE_HANDLERS, dict)
    assert len(STAGE_HANDLERS) == 0, (
        f"STAGE_HANDLERS must be empty at module level; got {list(STAGE_HANDLERS.keys())}"
    )


# ---------------------------------------------------------------------------
# 3. Registry resolves a registered handler
# ---------------------------------------------------------------------------

def test_workflow_stage_handler_registry_resolves_registered_handler():
    from agentic_core.L3_orchestration.workflow_stage_handlers import (
        WorkflowStageHandlerRegistry,
    )

    def _my_handler(step_packet: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"result": "ok"}

    _my_handler.__module__ = "some.domain.module"  # not quarantined

    registry = WorkflowStageHandlerRegistry()
    registry.register("content_generation", _my_handler)
    resolved = registry.resolve("content_generation")
    assert resolved is _my_handler


# ---------------------------------------------------------------------------
# 4. Registry fails closed on missing handler (no single-step fallback)
# ---------------------------------------------------------------------------

def test_workflow_stage_handler_registry_fails_closed_on_missing_handler():
    from agentic_core.L3_orchestration.workflow_stage_handlers import (
        WorkflowStageHandlerRegistry,
        MissingWorkflowStageHandlerError,
    )

    registry = WorkflowStageHandlerRegistry()
    with pytest.raises(MissingWorkflowStageHandlerError) as exc_info:
        registry.resolve("nonexistent_stage")

    assert "nonexistent_stage" in str(exc_info.value)
    assert "single-step" in str(exc_info.value).lower(), (
        "Error message must explicitly state no fallback to single-step"
    )


# ---------------------------------------------------------------------------
# 5. Registry fails closed on duplicate registration
# ---------------------------------------------------------------------------

def test_workflow_stage_handler_registry_fails_closed_on_duplicate_handler():
    from agentic_core.L3_orchestration.workflow_stage_handlers import (
        WorkflowStageHandlerRegistry,
        DuplicateWorkflowStageHandlerError,
    )

    def _handler_a(p: Mapping[str, Any]) -> Mapping[str, Any]:
        return {}

    def _handler_b(p: Mapping[str, Any]) -> Mapping[str, Any]:
        return {}

    for fn in (_handler_a, _handler_b):
        fn.__module__ = "clean.domain.module"

    registry = WorkflowStageHandlerRegistry()
    registry.register("my_stage", _handler_a)

    with pytest.raises(DuplicateWorkflowStageHandlerError) as exc_info:
        registry.register("my_stage", _handler_b)

    assert "my_stage" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 6. Registry rejects quarantined handler source
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("quarantined_module", [
    "apps_rg.integrations.hops._ensemble_runner",
    "apps_rg.integrations.gates.pre_llm_gates",
    "apps_rg.prompt_assembly.rg_pa_compiler",
    "apps_rg.prompt_assembly.contracts",
    "apps_rg._quarantine.compiler",
])
def test_workflow_stage_handler_registry_rejects_quarantined_handler_source(
    quarantined_module: str,
):
    from agentic_core.L3_orchestration.workflow_stage_handlers import (
        WorkflowStageHandlerRegistry,
        QuarantinedWorkflowHandlerError,
    )

    def _bad_handler(p: Mapping[str, Any]) -> Mapping[str, Any]:
        return {}

    _bad_handler.__module__ = quarantined_module

    registry = WorkflowStageHandlerRegistry()
    with pytest.raises(QuarantinedWorkflowHandlerError) as exc_info:
        registry.register("some_stage", _bad_handler)

    assert quarantined_module in str(exc_info.value)
    assert "DO_NOT_IMPORT_FROM_CORE_RUNTIME" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 7. agentic_core active runtime does not import apps_rg.integrations.hops
# ---------------------------------------------------------------------------

def test_core_runtime_does_not_import_apps_rg_integrations_hops():
    """AST-scan agentic_core/ — no active runtime file may import integrations.hops."""
    violations = []
    for src in _agentic_core_active_runtime_files():
        if _file_contains_import_of(src, "apps_rg.integrations.hops"):
            violations.append(str(src.relative_to(_REPO_ROOT)))

    assert not violations, (
        "agentic_core active runtime files import quarantined apps_rg.integrations.hops:\n"
        + "\n".join(f"  {v}" for v in violations)
    )


# ---------------------------------------------------------------------------
# 8. agentic_core active runtime does not import apps_rg.integrations.gates
# ---------------------------------------------------------------------------

def test_core_runtime_does_not_import_apps_rg_integrations_gates():
    """AST-scan agentic_core/ — no active runtime file may import integrations.gates."""
    violations = []
    for src in _agentic_core_active_runtime_files():
        if _file_contains_import_of(src, "apps_rg.integrations.gates"):
            violations.append(str(src.relative_to(_REPO_ROOT)))

    assert not violations, (
        "agentic_core active runtime files import quarantined apps_rg.integrations.gates:\n"
        + "\n".join(f"  {v}" for v in violations)
    )


# ---------------------------------------------------------------------------
# 9. Quarantined apps_rg.prompt_assembly not imported by active core runtime
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("quarantined_prefix", [
    "apps_rg.prompt_assembly.rg_pa_compiler",
    "apps_rg.prompt_assembly.contracts",
])
def test_quarantined_apps_rg_prompt_assembly_not_imported_by_core_runtime(
    quarantined_prefix: str,
):
    """AST-scan agentic_core/ — quarantined prompt_assembly modules not imported."""
    violations = []
    for src in _agentic_core_active_runtime_files():
        if _file_contains_import_of(src, quarantined_prefix):
            violations.append(str(src.relative_to(_REPO_ROOT)))

    assert not violations, (
        f"agentic_core active runtime files import quarantined {quarantined_prefix}:\n"
        + "\n".join(f"  {v}" for v in violations)
    )


# ---------------------------------------------------------------------------
# 10. Quarantined apps_rg judge not used as runtime authority
# ---------------------------------------------------------------------------

def test_quarantined_apps_rg_judge_not_used_as_runtime_authority():
    """AST-scan agentic_core/ — executive_positioning_judge not imported."""
    violations = []
    for src in _agentic_core_active_runtime_files():
        if _file_contains_import_of(src, "apps_rg.engines.judges"):
            violations.append(str(src.relative_to(_REPO_ROOT)))

    assert not violations, (
        "agentic_core active runtime files import quarantined apps_rg.engines.judges:\n"
        + "\n".join(f"  {v}" for v in violations)
    )


# ---------------------------------------------------------------------------
# 11. Missing stage handler does NOT fall back to single-step
# ---------------------------------------------------------------------------

def test_missing_stage_handler_does_not_fallback_to_single_step():
    """Calling resolve() on an empty registry must raise, not return a stub handler."""
    from agentic_core.L3_orchestration.workflow_stage_handlers import (
        WorkflowStageHandlerRegistry,
        MissingWorkflowStageHandlerError,
    )

    registry = WorkflowStageHandlerRegistry()
    # Confirm registry is empty
    assert len(registry) == 0

    # Must raise — no silent fallback, no stub returned
    with pytest.raises(MissingWorkflowStageHandlerError):
        registry.resolve("content_generation")

    # Confirm it does NOT return None or a callable
    result = None
    raised = False
    try:
        result = registry.resolve("content_generation")
    except MissingWorkflowStageHandlerError:
        raised = True

    assert raised, "resolve() must raise, not return silently"
    assert result is None, "resolve() must not return a value when raising"


# ---------------------------------------------------------------------------
# 12. workflow_stage_handlers.py source does not write L4
# ---------------------------------------------------------------------------

def test_stage_handler_registry_does_not_write_l4():
    """AST-check: workflow_stage_handlers.py must not import from L4 state modules."""
    handler_file = _REPO_ROOT / "agentic_core" / "L3_orchestration" / "workflow_stage_handlers.py"
    assert handler_file.exists(), f"Missing: {handler_file}"

    forbidden_prefixes = [
        "agentic_core.L4_state",
        "agentic_core.runtime.state",
    ]
    for prefix in forbidden_prefixes:
        assert not _file_contains_import_of(handler_file, prefix), (
            f"workflow_stage_handlers.py imports from forbidden L4 module: {prefix}"
        )


# ---------------------------------------------------------------------------
# 13. workflow_stage_handlers.py source does not emit X3
# ---------------------------------------------------------------------------

def test_stage_handler_registry_does_not_emit_x3():
    """AST-check: workflow_stage_handlers.py must not import X3/disposition contracts."""
    handler_file = _REPO_ROOT / "agentic_core" / "L3_orchestration" / "workflow_stage_handlers.py"
    assert handler_file.exists(), f"Missing: {handler_file}"

    forbidden_prefixes = [
        "agentic_core.runtime.exit",
        "agentic_core.runtime.contracts.exit",
    ]
    # Also text-scan for X3Disposition or emit_x3 as a belt-and-suspenders check
    source_text = handler_file.read_text(encoding="utf-8")
    forbidden_strings = ["X3Disposition", "emit_x3", "ExitDisposition"]

    for prefix in forbidden_prefixes:
        assert not _file_contains_import_of(handler_file, prefix), (
            f"workflow_stage_handlers.py imports from forbidden X3 module: {prefix}"
        )
    for token in forbidden_strings:
        assert token not in source_text, (
            f"workflow_stage_handlers.py contains forbidden X3 token: {token!r}"
        )


# ---------------------------------------------------------------------------
# 14. DO_NOT_IMPORT_FROM_CORE_RUNTIME sentinel present in all quarantined files
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rel_path", [
    "apps_rg/integrations/hops/__init__.py",
    "apps_rg/integrations/gates/__init__.py",
    "apps_rg/prompt_assembly/rg_pa_compiler.py",
    "apps_rg/prompt_assembly/contracts.py",
    "apps_rg/engines/judges/executive_positioning_judge.py",
])
def test_quarantine_sentinel_present_in_file(rel_path: str):
    """Every quarantined file must contain the DO_NOT_IMPORT_FROM_CORE_RUNTIME sentinel."""
    path = _REPO_ROOT / rel_path
    assert path.exists(), f"Expected quarantined file not found: {rel_path}"
    content = path.read_text(encoding="utf-8")
    assert "DO_NOT_IMPORT_FROM_CORE_RUNTIME" in content, (
        f"Quarantined file missing DO_NOT_IMPORT_FROM_CORE_RUNTIME sentinel: {rel_path}"
    )


# ---------------------------------------------------------------------------
# 15. WorkflowStageHandlerRef.as_dict() returns expected shape
# ---------------------------------------------------------------------------

def test_workflow_stage_handler_ref_as_dict():
    from agentic_core.L3_orchestration.workflow_stage_handlers import (
        WorkflowStageHandlerRef,
    )

    def _clean_handler(p: Mapping[str, Any]) -> Mapping[str, Any]:
        return {}

    _clean_handler.__module__ = "my.domain.handlers"
    ref = WorkflowStageHandlerRef("my_stage", _clean_handler)
    d = ref.as_dict()
    assert d["stage_type"] == "my_stage"
    assert d["handler_name"] == "_clean_handler"
    assert d["handler_module"] == "my.domain.handlers"
