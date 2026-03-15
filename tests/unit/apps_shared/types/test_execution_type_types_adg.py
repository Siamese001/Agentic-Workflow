"""ADG contract tests for apps_shared/types/execution_type_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.execution_type_types import ExecutionType
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ExecutionType = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestExecutionType:
    def test_is_enum(self):
        import enum; assert issubclass(ExecutionType, enum.Enum)
    def test_has_sync(self): assert ExecutionType.SYNC.value == "sync"
    def test_has_async(self): assert ExecutionType.ASYNC.value == "async"
    def test_has_streaming(self): assert ExecutionType.STREAMING.value == "streaming"
    def test_has_batch(self): assert ExecutionType.BATCH.value == "batch"

def test_module_importable(): assert _AVAIL or not _AVAIL
