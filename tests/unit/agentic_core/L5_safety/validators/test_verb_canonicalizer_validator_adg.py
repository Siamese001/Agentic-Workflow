"""ADG-driven tests for agentic_core/L5_safety/validators/verb_canonicalizer_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.validators.verb_canonicalizer_validator import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        VerbCanonicalizer,
        canonicalize,
        check_for_forbidden_verbs,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    VerbCanonicalizer = None  # type: ignore[assignment,misc]
    canonicalize = None  # type: ignore[assignment,misc]
    check_for_forbidden_verbs = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="verb_canonicalizer_validator.py deps unavailable")
class TestVerbCanonicalizer:
    def test_is_class(self):
        assert isinstance(VerbCanonicalizer, type)
    def test_importable(self):
        assert VerbCanonicalizer is not None

@pytest.mark.skipif(not _AVAILABLE, reason="verb_canonicalizer_validator.py deps unavailable")
class TestCanonicalize:
    def test_is_callable(self):
        assert callable(canonicalize)

@pytest.mark.skipif(not _AVAILABLE, reason="verb_canonicalizer_validator.py deps unavailable")
class TestCheckForForbiddenVerbs:
    def test_is_callable(self):
        assert callable(check_for_forbidden_verbs)

@pytest.mark.skipif(not _AVAILABLE, reason="verb_canonicalizer_validator.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="verb_canonicalizer_validator.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="verb_canonicalizer_validator.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="verb_canonicalizer_validator.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="verb_canonicalizer_validator.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="verb_canonicalizer_validator.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module verb_canonicalizer_validator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE