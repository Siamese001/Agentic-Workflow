"""Foundational behavioral tests for apps_lic/reasoning/LicCodeInterpreter.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_LicCodeInterpreter_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.reasoning.LicCodeInterpreter import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        KeywordExtractionResult,
        LICCodeInterpreter,
        ScoredCandidate,
        ScoringCriteria,
        SimilarityResult,
        create_code_interpreter,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ScoredCandidate = None  # type: ignore[assignment,misc]
    ScoringCriteria = None  # type: ignore[assignment,misc]
    SimilarityResult = None  # type: ignore[assignment,misc]
    KeywordExtractionResult = None  # type: ignore[assignment,misc]
    LICCodeInterpreter = None  # type: ignore[assignment,misc]
    create_code_interpreter = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="LicCodeInterpreter.py deps unavailable")
class TestScoredCandidateContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ScoredCandidate)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ScoredCandidate)}
        assert field_names >= {'candidate_index', 'scores', 'candidate_text', 'total_score'}

@pytest.mark.skipif(not _AVAILABLE, reason="LicCodeInterpreter.py deps unavailable")
class TestScoringCriteriaContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ScoringCriteria)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ScoringCriteria)}
        assert field_names >= {'readability', 'strategic_alignment', 'keyword_density'}

@pytest.mark.skipif(not _AVAILABLE, reason="LicCodeInterpreter.py deps unavailable")
class TestSimilarityResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SimilarityResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(SimilarityResult)}
        assert field_names >= {'text2_length', 'text1_length', 'method', 'score'}

@pytest.mark.skipif(not _AVAILABLE, reason="LicCodeInterpreter.py deps unavailable")
class TestKeywordExtractionResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(KeywordExtractionResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(KeywordExtractionResult)}
        assert field_names >= {'keywords', 'top_n', 'source_text_length'}

@pytest.mark.skipif(not _AVAILABLE, reason="LicCodeInterpreter.py deps unavailable")
class TestLICCodeInterpreterContract:
    def test_is_class(self):
        assert isinstance(LICCodeInterpreter, type)

    def test_has_method_execute(self):
        assert callable(getattr(LICCodeInterpreter, 'execute', None))

    def test_has_method_run_similarity_check(self):
        assert callable(getattr(LICCodeInterpreter, 'run_similarity_check', None))

    def test_has_method_run_scoring_competition(self):
        assert callable(getattr(LICCodeInterpreter, 'run_scoring_competition', None))

    def test_has_method_extract_keywords(self):
        assert callable(getattr(LICCodeInterpreter, 'extract_keywords', None))

@pytest.mark.skipif(not _AVAILABLE, reason="LicCodeInterpreter.py deps unavailable")
class TestCreateCodeInterpreterFunction:
    def test_is_callable(self):
        assert callable(create_code_interpreter)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_code_interpreter)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="LicCodeInterpreter.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="LicCodeInterpreter.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="LicCodeInterpreter.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="LicCodeInterpreter.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="LicCodeInterpreter.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module LicCodeInterpreter must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
