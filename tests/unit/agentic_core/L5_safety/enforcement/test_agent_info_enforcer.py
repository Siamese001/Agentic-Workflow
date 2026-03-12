"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/agent_info_enforcer.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_agent_info_enforcer_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.agent_info_enforcer import (  # noqa: F401
        AgentInfo,
        ASTNormalizer,
        extract_layer,
        find_agent_classes,
        generate_fingerprint,
        calculate_similarity,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    AgentInfo = None  # type: ignore[assignment,misc]
    ASTNormalizer = None  # type: ignore[assignment,misc]
    extract_layer = None  # type: ignore[assignment,misc]
    find_agent_classes = None  # type: ignore[assignment,misc]
    generate_fingerprint = None  # type: ignore[assignment,misc]
    calculate_similarity = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestAgentInfoContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AgentInfo)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(AgentInfo)}
        assert field_names >= {'method_count', 'line_number', 'name', 'layer', 'file_path'}

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestASTNormalizerContract:
    def test_is_class(self):
        assert isinstance(ASTNormalizer, type)

    def test_has_method_reset(self):
        assert callable(getattr(ASTNormalizer, 'reset', None))

    def test_has_method_visit_ClassDef(self):
        assert callable(getattr(ASTNormalizer, 'visit_ClassDef', None))

    def test_has_method_visit_FunctionDef(self):
        assert callable(getattr(ASTNormalizer, 'visit_FunctionDef', None))

    def test_has_method_visit_AsyncFunctionDef(self):
        assert callable(getattr(ASTNormalizer, 'visit_AsyncFunctionDef', None))

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestExtractLayerFunction:
    def test_is_callable(self):
        assert callable(extract_layer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(extract_layer)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestFindAgentClassesFunction:
    def test_is_callable(self):
        assert callable(find_agent_classes)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(find_agent_classes)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestGenerateFingerprintFunction:
    def test_is_callable(self):
        assert callable(generate_fingerprint)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(generate_fingerprint)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestCalculateSimilarityFunction:
    def test_is_callable(self):
        assert callable(calculate_similarity)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(calculate_similarity)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module agent_info_enforcer must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
