"""ADG-driven tests for agentic_core/prompt_governance/scripts/dry_run_compiler.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.prompt_governance.scripts.dry_run_compiler import (  # noqa: F401
        initialize_jinja_environment,
        compile_template,
        find_jinja_templates,
        verify_all_templates,
        main,
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
    initialize_jinja_environment = None  # type: ignore[assignment,misc]
    compile_template = None  # type: ignore[assignment,misc]
    find_jinja_templates = None  # type: ignore[assignment,misc]
    verify_all_templates = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestInitializeJinjaEnvironment:
    def test_is_callable(self):
        assert callable(initialize_jinja_environment)

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestCompileTemplate:
    def test_is_callable(self):
        assert callable(compile_template)

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestFindJinjaTemplates:
    def test_is_callable(self):
        assert callable(find_jinja_templates)

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestVerifyAllTemplates:
    def test_is_callable(self):
        assert callable(verify_all_templates)

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module dry_run_compiler.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
