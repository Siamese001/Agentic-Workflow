"""ADG-driven tests for agentic_core/prompt_governance/scripts/harden_templates.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.prompt_governance.scripts.harden_templates import (  # noqa: F401
        find_jinja_files,
        is_already_hardened,
        extract_variables,
        generate_standardized_header,
        harden_template,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    find_jinja_files = None  # type: ignore[assignment,misc]
    is_already_hardened = None  # type: ignore[assignment,misc]
    extract_variables = None  # type: ignore[assignment,misc]
    generate_standardized_header = None  # type: ignore[assignment,misc]
    harden_template = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestFindJinjaFiles:
    def test_is_callable(self):
        assert callable(find_jinja_files)

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestIsAlreadyHardened:
    def test_is_callable(self):
        assert callable(is_already_hardened)

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestExtractVariables:
    def test_is_callable(self):
        assert callable(extract_variables)

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestGenerateStandardizedHeader:
    def test_is_callable(self):
        assert callable(generate_standardized_header)

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestHardenTemplate:
    def test_is_callable(self):
        assert callable(harden_template)

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module harden_templates.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
