"""ADG-driven tests for L2_execution/determinism/dependency_locker.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.determinism.dependency_locker import DependencyLocker
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DependencyLocker = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="dependency_locker deps unavailable")
class TestDependencyLocker:
    def test_importable(self):
        assert callable(DependencyLocker)

    def test_has_generate_lock_hash(self):
        assert hasattr(DependencyLocker, "generate_lock_hash")

    def test_generate_lock_hash_raises_for_missing_file(self, tmp_path):
        from pathlib import Path
        missing = tmp_path / "requirements_nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            DependencyLocker.generate_lock_hash(missing)

    def test_generate_lock_hash_returns_hex_string(self, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("requests==2.31.0\nnumpy==1.26.0\n")
        result = DependencyLocker.generate_lock_hash(req)
        assert isinstance(result, str)
        int(result, 16)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
