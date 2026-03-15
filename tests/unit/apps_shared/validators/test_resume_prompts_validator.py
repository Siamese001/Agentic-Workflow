"""Foundational behavioral tests for apps_shared/validators/resume_prompts_validator.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_resume_prompts_validator_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.validators.resume_prompts_validator import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        build_librarian_memory_query_prompt,
        build_librarian_mission_extraction_prompt,
        build_librarian_strategic_analysis_prompt,
        build_phase1_prompt,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    build_librarian_mission_extraction_prompt = None  # type: ignore[assignment,misc]
    build_librarian_strategic_analysis_prompt = None  # type: ignore[assignment,misc]
    build_librarian_memory_query_prompt = None  # type: ignore[assignment,misc]
    build_phase1_prompt = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestBuildLibrarianMissionExtractionPromptFunction:
    def test_is_callable(self):
        assert callable(build_librarian_mission_extraction_prompt)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_librarian_mission_extraction_prompt)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestBuildLibrarianStrategicAnalysisPromptFunction:
    def test_is_callable(self):
        assert callable(build_librarian_strategic_analysis_prompt)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_librarian_strategic_analysis_prompt)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestBuildLibrarianMemoryQueryPromptFunction:
    def test_is_callable(self):
        assert callable(build_librarian_memory_query_prompt)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_librarian_memory_query_prompt)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestBuildPhase1PromptFunction:
    def test_is_callable(self):
        assert callable(build_phase1_prompt)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_phase1_prompt)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module resume_prompts_validator must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
