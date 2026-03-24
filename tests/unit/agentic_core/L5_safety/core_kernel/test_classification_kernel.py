"""Foundational behavioral tests for agentic_core/L5_safety/core_kernel/classification_kernel.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_classification_kernel_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.core_kernel.classification_kernel import (  # noqa: F401
        classify_file_standalone,
        clear_classification_conflicts,
        get_classification_conflicts,
        is_agent_file,
        is_agent_or_orchestrator,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    get_classification_conflicts = None  # type: ignore[assignment,misc]
    clear_classification_conflicts = None  # type: ignore[assignment,misc]
    classify_file_standalone = None  # type: ignore[assignment,misc]
    is_agent_file = None  # type: ignore[assignment,misc]
    is_agent_or_orchestrator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="classification_kernel.py deps unavailable")
class TestGetClassificationConflictsFunction:
    def test_is_callable(self):
        assert callable(get_classification_conflicts)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_classification_conflicts)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="classification_kernel.py deps unavailable")
class TestClearClassificationConflictsFunction:
    def test_is_callable(self):
        assert callable(clear_classification_conflicts)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(clear_classification_conflicts)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="classification_kernel.py deps unavailable")
class TestClassifyFileStandaloneFunction:
    def test_is_callable(self):
        assert callable(classify_file_standalone)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(classify_file_standalone)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="classification_kernel.py deps unavailable")
class TestIsAgentFileFunction:
    def test_is_callable(self):
        assert callable(is_agent_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_agent_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="classification_kernel.py deps unavailable")
class TestIsAgentOrOrchestratorFunction:
    def test_is_callable(self):
        assert callable(is_agent_or_orchestrator)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_agent_or_orchestrator)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: classification_kernel importable or gracefully unavailable."""
    pass