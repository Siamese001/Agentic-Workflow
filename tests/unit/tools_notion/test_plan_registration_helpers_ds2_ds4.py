"""
DS-2 and DS-4 unit tests for tools/notion/_plan_registration_helpers.py.

DS-2: _update_cache_entry() — cache-on-write discipline
DS-4: _rotate_if_large() — telemetry log rotation
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "tools" / "notion" / "_plan_registration_helpers.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "_plan_registration_helpers", MODULE_PATH
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("_plan_registration_helpers", mod)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load_module()


# ===========================================================================
# DS-4: _rotate_if_large
# ===========================================================================


def test_rotate_if_large_triggers_when_above_threshold(mod, tmp_path):
    log = tmp_path / "test.jsonl"
    log.write_bytes(b"x" * (mod.LOG_ROTATION_BYTES + 1))
    mod._rotate_if_large(log, max_bytes=mod.LOG_ROTATION_BYTES)
    rotated = log.with_suffix(".jsonl.1")
    assert rotated.exists(), "backup file .jsonl.1 should exist"
    assert not log.exists(), "original should be renamed away"


def test_rotate_if_large_does_not_trigger_below_threshold(mod, tmp_path):
    log = tmp_path / "test.jsonl"
    log.write_bytes(b"x" * 100)
    mod._rotate_if_large(log, max_bytes=mod.LOG_ROTATION_BYTES)
    assert log.exists(), "file below threshold should not be rotated"


def test_rotate_if_large_noop_when_absent(mod, tmp_path):
    log = tmp_path / "nonexistent.jsonl"
    mod._rotate_if_large(log, max_bytes=1)  # should not raise
    assert not log.exists()


def test_rotate_if_large_overwrites_previous_backup(mod, tmp_path):
    log = tmp_path / "test.jsonl"
    log.write_bytes(b"new" * 100)
    old_backup = log.with_suffix(".jsonl.1")
    old_backup.write_bytes(b"old")
    mod._rotate_if_large(log, max_bytes=1)
    assert old_backup.read_bytes() == b"new" * 100


def test_rotate_log_rotation_bytes_constant(mod):
    """DS-4: LOG_ROTATION_BYTES must be 10 MB."""
    assert mod.LOG_ROTATION_BYTES == 10 * 1024 * 1024


# ===========================================================================
# DS-2: _update_cache_entry
# ===========================================================================


def test_update_cache_entry_creates_cache_when_missing(mod, tmp_path):
    cache = tmp_path / "plan_registration_cache.json"
    mod._update_cache_entry("my-plan-aabbcc", "page-123", "In Progress", cache)
    assert cache.exists()
    data = json.loads(cache.read_text())
    assert data["plans"]["my-plan-aabbcc"]["page_id"] == "page-123"
    assert data["plans"]["my-plan-aabbcc"]["status"] == "In Progress"


def test_update_cache_entry_merges_into_existing_cache(mod, tmp_path):
    cache = tmp_path / "plan_registration_cache.json"
    existing = {
        "fetched_at": "2026-01-01T00:00:00Z",
        "fetched_at_epoch": 0.0,
        "plans": {
            "old-plan-111111": {"page_id": "old-page", "status": "Completed"},
        },
    }
    cache.write_text(json.dumps(existing), encoding="utf-8")
    mod._update_cache_entry("new-plan-222222", "new-page", "Not Started", cache)
    data = json.loads(cache.read_text())
    # Old entry preserved
    assert data["plans"]["old-plan-111111"]["page_id"] == "old-page"
    # New entry added
    assert data["plans"]["new-plan-222222"]["page_id"] == "new-page"
    assert data["plans"]["new-plan-222222"]["status"] == "Not Started"


def test_update_cache_entry_atomic_write(mod, tmp_path):
    """Atomic write: no .json.tmp should remain after successful write."""
    cache = tmp_path / "plan_registration_cache.json"
    mod._update_cache_entry("plan-atomic-aaaaaa", "pg-1", "In Progress", cache)
    tmp = cache.with_suffix(".json.tmp")
    assert not tmp.exists(), ".json.tmp must be cleaned up after atomic replace"


def test_update_cache_entry_handles_corrupt_cache(mod, tmp_path):
    """Corrupt cache is silently treated as empty — no exception raised."""
    cache = tmp_path / "plan_registration_cache.json"
    cache.write_text("NOT VALID JSON", encoding="utf-8")
    mod._update_cache_entry("plan-recover-bbbbbb", "pg-2", "Not Started", cache)
    data = json.loads(cache.read_text())
    assert data["plans"]["plan-recover-bbbbbb"]["page_id"] == "pg-2"


def test_update_cache_entry_updates_existing_slug(mod, tmp_path):
    """Updating a slug that already exists overwrites the entry."""
    cache = tmp_path / "plan_registration_cache.json"
    mod._update_cache_entry("plan-update-cccccc", "old-pg", "Not Started", cache)
    mod._update_cache_entry("plan-update-cccccc", "new-pg", "In Progress", cache)
    data = json.loads(cache.read_text())
    assert data["plans"]["plan-update-cccccc"]["page_id"] == "new-pg"
    assert data["plans"]["plan-update-cccccc"]["status"] == "In Progress"
