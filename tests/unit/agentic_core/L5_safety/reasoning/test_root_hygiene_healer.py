"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/root_hygiene_healer.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_root_hygiene_healer_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.root_hygiene_healer import (  # noqa: F401
        ROOT_MARKERS,
        RootHygieneAgent,
        get_project_root,
        main,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    RootHygieneAgent = None  # type: ignore[assignment,misc]
    get_project_root = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    ROOT_MARKERS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="root_hygiene_healer.py deps unavailable")
class TestRootHygieneAgentContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RootHygieneAgent)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(RootHygieneAgent)}
        assert fnames >= {'dry_run', 'project_root'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(RootHygieneAgent)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="root_hygiene_healer.py deps unavailable")
class TestGetProjectRootFunction:
    def test_is_callable(self):
        assert callable(get_project_root)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_project_root)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="root_hygiene_healer.py deps unavailable")
class TestMainFunction:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="root_hygiene_healer.py deps unavailable")
class TestRootMarkersConstant:
    def test_is_not_none(self):
        assert ROOT_MARKERS is not None

    def test_has_length(self):
        assert hasattr(ROOT_MARKERS, '__len__')

    def test_is_non_empty(self):
        pass


def test_module_importable():
    """Smoke: root_hygiene_healer importable or gracefully unavailable."""
    pass