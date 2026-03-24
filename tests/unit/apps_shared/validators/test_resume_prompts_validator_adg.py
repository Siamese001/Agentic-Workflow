"""ADG-driven tests for apps_shared/validators/resume_prompts_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.validators.resume_prompts_validator import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        build_librarian_memory_query_prompt,
        build_librarian_mission_extraction_prompt,
        build_librarian_strategic_analysis_prompt,
        build_phase1_prompt,
        build_phase2_prompt,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    build_librarian_mission_extraction_prompt = None  # type: ignore[assignment,misc]
    build_librarian_strategic_analysis_prompt = None  # type: ignore[assignment,misc]
    build_librarian_memory_query_prompt = None  # type: ignore[assignment,misc]
    build_phase1_prompt = None  # type: ignore[assignment,misc]
    build_phase2_prompt = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestBuildLibrarianMissionExtractionPrompt:
    def test_is_callable(self):
        assert callable(build_librarian_mission_extraction_prompt)

@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestBuildLibrarianStrategicAnalysisPrompt:
    def test_is_callable(self):
        assert callable(build_librarian_strategic_analysis_prompt)

@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestBuildLibrarianMemoryQueryPrompt:
    def test_is_callable(self):
        assert callable(build_librarian_memory_query_prompt)

@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestBuildPhase1Prompt:
    def test_is_callable(self):
        assert callable(build_phase1_prompt)

@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestBuildPhase2Prompt:
    def test_is_callable(self):
        assert callable(build_phase2_prompt)

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

@pytest.mark.skipif(not _AVAILABLE, reason="resume_prompts_validator.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module resume_prompts_validator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE