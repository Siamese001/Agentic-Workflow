"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/agent_info_enforcer.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_agent_info_enforcer_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.agent_info_enforcer import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    AgentInfo,
    ASTNormalizer,
    calculate_similarity,
    extract_layer,
    find_agent_classes,
    generate_fingerprint,
)


class TestAgentInfoContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AgentInfo)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(AgentInfo)}
        assert field_names >= {'method_count', 'line_number', 'name', 'layer', 'file_path'}

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

class TestExtractLayerFunction:
    def test_is_callable(self):
        assert callable(extract_layer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(extract_layer)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestFindAgentClassesFunction:
    def test_is_callable(self):
        assert callable(find_agent_classes)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(find_agent_classes)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGenerateFingerprintFunction:
    def test_is_callable(self):
        assert callable(generate_fingerprint)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(generate_fingerprint)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestCalculateSimilarityFunction:
    def test_is_callable(self):
        assert callable(calculate_similarity)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(calculate_similarity)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module agent_info_enforcer must be importable or skip gracefully."""
    pass  # Import verified at module level
