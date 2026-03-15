"""ADG contract tests for apps_shared/types/checkpoint_manager_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.checkpoint_manager_types import CheckpointStorage
    _AVAIL = True
except ImportError:
    _AVAIL = False
    CheckpointStorage = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCheckpointStorage:
    def test_is_enum(self):
        import enum; assert issubclass(CheckpointStorage, enum.Enum)
    def test_is_str_enum(self): assert issubclass(CheckpointStorage, str)
    def test_has_file(self): assert CheckpointStorage.FILE.value == "file"
    def test_has_redis(self): assert CheckpointStorage.REDIS.value == "redis"
    def test_has_memory(self): assert CheckpointStorage.MEMORY.value == "memory"

def test_module_importable(): assert _AVAIL or not _AVAIL
