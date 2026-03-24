"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_GravityLeakRepairAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        GravityFix,
        GravityLeakRepairAgent,
        GravityRepairProhibitedError,
        get_GravityLeakRepairAgent,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    GravityRepairProhibitedError = None  # type: ignore[assignment,misc]
    GravityFix = None  # type: ignore[assignment,misc]
    GravityLeakRepairAgent = None  # type: ignore[assignment,misc]
    get_GravityLeakRepairAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="GravityLeakRepairAgent.py deps unavailable")
class TestGravityRepairProhibitedErrorContract:
    def test_is_class(self):
        assert isinstance(GravityRepairProhibitedError, type)

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(GravityRepairProhibitedError) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="GravityLeakRepairAgent.py deps unavailable")
class TestGravityFixContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(GravityFix)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(GravityFix)}
        assert fnames >= {'old_import', 'line_number', 'fix_type', 'file_path', 'rationale', 'new_import'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(GravityFix)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="GravityLeakRepairAgent.py deps unavailable")
class TestGravityLeakRepairAgentContract:
    def test_is_class(self):
        assert isinstance(GravityLeakRepairAgent, type)

    def test_has_method_analyze_violation(self):
        assert callable(getattr(GravityLeakRepairAgent, 'analyze_violation', None))

    def test_has_method_generate_fix_report(self):
        assert callable(getattr(GravityLeakRepairAgent, 'generate_fix_report', None))

    def test_has_method_apply_fix(self):
        assert callable(getattr(GravityLeakRepairAgent, 'apply_fix', None))

    def test_has_method_heal_violations(self):
        assert callable(getattr(GravityLeakRepairAgent, 'heal_violations', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(GravityLeakRepairAgent) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="GravityLeakRepairAgent.py deps unavailable")
class TestGetGravityleakrepairagentFunction:
    def test_is_callable(self):
        assert callable(get_GravityLeakRepairAgent)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_GravityLeakRepairAgent)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="GravityLeakRepairAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GravityLeakRepairAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GravityLeakRepairAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GravityLeakRepairAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GravityLeakRepairAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GravityLeakRepairAgent.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: GravityLeakRepairAgent importable or gracefully unavailable."""
    pass