"""Regression tests — W2.P3: R1A cache invalidation on policy/blueprint version bump.

Covers:
- stamp_r1a_cache writes JSON envelope with policy/blueprint metadata (W2.P1)
- check_r1a_cache respects per-entry policy_hash (returns None on mismatch)
- check_r1a_cache respects per-entry blueprint_hash (returns None on mismatch)
- check_r1a_cache falls back to legacy r1a_key.txt (read-compat for pre-W2 entries)
- prune_stale_r1a_entries removes dirs with mismatched policy/blueprint
- prune_stale_r1a_entries dry_run=True does NOT delete
- r1b_adapter uses SEMANTIC_CACHE_THRESHOLD env var when no explicit threshold
- r1b_adapter uses SEMANTIC_CACHE_TTL_SECONDS env var when storing
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from apps_rg.cache.r1a_adapter import (
    CACHE_SCHEMA_VERSION,
    check_r1a_cache,
    prune_stale_r1a_entries,
    stamp_r1a_cache,
)
from apps_rg.cache.r1b_adapter import (
    DEFAULT_CACHE_TTL_SECONDS,
    DEFAULT_SIMILARITY_THRESHOLD,
    _get_cache_ttl_seconds,
    _get_similarity_threshold,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_run_dir(runs_dir: Path, name: str) -> Path:
    run_dir = runs_dir / name
    run_dir.mkdir(parents=True)
    (run_dir / "generated_resume.json").write_text("{}", encoding="utf-8")
    return run_dir


# ---------------------------------------------------------------------------
# stamp_r1a_cache tests
# ---------------------------------------------------------------------------


def test_stamp_writes_json_envelope(tmp_path):
    run_dir = _make_run_dir(tmp_path, "run_001")
    stamp_r1a_cache("abc123key", str(run_dir), policy_hash="ph1", blueprint_hash="bh1")
    stamp = json.loads((run_dir / "r1a_stamp.json").read_text())
    assert stamp["key"] == "abc123key"
    assert stamp["schema_version"] == CACHE_SCHEMA_VERSION
    assert stamp["policy_hash"] == "ph1"
    assert stamp["blueprint_hash"] == "bh1"
    assert "stamped_at" in stamp


def test_stamp_omits_optional_fields_when_none(tmp_path):
    run_dir = _make_run_dir(tmp_path, "run_002")
    stamp_r1a_cache("key_no_meta", str(run_dir))
    stamp = json.loads((run_dir / "r1a_stamp.json").read_text())
    assert "policy_hash" not in stamp
    assert "blueprint_hash" not in stamp


# ---------------------------------------------------------------------------
# check_r1a_cache tests
# ---------------------------------------------------------------------------


def test_r1a_hit_with_matching_policy_and_blueprint(tmp_path):
    run_dir = _make_run_dir(tmp_path, "run_match")
    stamp_r1a_cache("mykey", str(run_dir), policy_hash="phA", blueprint_hash="bhA")
    result = check_r1a_cache("mykey", runs_dir=tmp_path, policy_hash="phA", blueprint_hash="bhA")
    assert result == str(run_dir)


def test_r1a_miss_on_policy_mismatch(tmp_path):
    run_dir = _make_run_dir(tmp_path, "run_policy_stale")
    stamp_r1a_cache("mykey", str(run_dir), policy_hash="old_policy")
    result = check_r1a_cache("mykey", runs_dir=tmp_path, policy_hash="new_policy")
    assert result is None


def test_r1a_miss_on_blueprint_mismatch(tmp_path):
    run_dir = _make_run_dir(tmp_path, "run_bp_stale")
    stamp_r1a_cache("mykey", str(run_dir), blueprint_hash="old_bp")
    result = check_r1a_cache("mykey", runs_dir=tmp_path, blueprint_hash="new_bp")
    assert result is None


def test_r1a_hit_no_policy_check_when_none_passed(tmp_path):
    run_dir = _make_run_dir(tmp_path, "run_no_check")
    stamp_r1a_cache("mykey2", str(run_dir), policy_hash="any_policy")
    # No policy_hash arg → stamp field ignored → hit
    result = check_r1a_cache("mykey2", runs_dir=tmp_path)
    assert result == str(run_dir)


def test_r1a_legacy_txt_compat(tmp_path):
    run_dir = _make_run_dir(tmp_path, "run_legacy")
    (run_dir / "r1a_key.txt").write_text("legacykey\n", encoding="utf-8")
    result = check_r1a_cache("legacykey", runs_dir=tmp_path)
    assert result == str(run_dir)


def test_r1a_legacy_txt_ignored_if_json_stamp_exists(tmp_path):
    run_dir = _make_run_dir(tmp_path, "run_both")
    stamp_r1a_cache("jsonkey", str(run_dir))
    (run_dir / "r1a_key.txt").write_text("differentkey\n", encoding="utf-8")
    # JSON stamp wins; txt key should NOT be used
    assert check_r1a_cache("jsonkey", runs_dir=tmp_path) == str(run_dir)
    assert check_r1a_cache("differentkey", runs_dir=tmp_path) is None


# ---------------------------------------------------------------------------
# prune_stale_r1a_entries tests
# ---------------------------------------------------------------------------


def test_prune_removes_stale_policy_entry(tmp_path):
    run_dir = _make_run_dir(tmp_path, "run_stale_policy")
    stamp_r1a_cache("k", str(run_dir), policy_hash="old")
    pruned = prune_stale_r1a_entries(runs_dir=tmp_path, policy_hash="new")
    assert run_dir.name in pruned
    assert not run_dir.exists()


def test_prune_dry_run_does_not_delete(tmp_path):
    run_dir = _make_run_dir(tmp_path, "run_dry")
    stamp_r1a_cache("k", str(run_dir), policy_hash="old")
    pruned = prune_stale_r1a_entries(runs_dir=tmp_path, policy_hash="new", dry_run=True)
    assert run_dir.name in pruned
    assert run_dir.exists()  # NOT deleted


def test_prune_keeps_matching_entry(tmp_path):
    run_dir = _make_run_dir(tmp_path, "run_fresh")
    stamp_r1a_cache("k", str(run_dir), policy_hash="current")
    pruned = prune_stale_r1a_entries(runs_dir=tmp_path, policy_hash="current")
    assert run_dir.name not in pruned
    assert run_dir.exists()


# ---------------------------------------------------------------------------
# r1b_adapter env var tests
# ---------------------------------------------------------------------------


def test_r1b_default_threshold_when_env_unset():
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("SEMANTIC_CACHE_THRESHOLD", None)
        assert _get_similarity_threshold() == DEFAULT_SIMILARITY_THRESHOLD


def test_r1b_threshold_from_env():
    with patch.dict(os.environ, {"SEMANTIC_CACHE_THRESHOLD": "0.80"}):
        assert abs(_get_similarity_threshold() - 0.80) < 1e-9


def test_r1b_threshold_clamps_below_zero():
    with patch.dict(os.environ, {"SEMANTIC_CACHE_THRESHOLD": "-0.5"}):
        assert _get_similarity_threshold() == 0.0


def test_r1b_threshold_clamps_above_one():
    with patch.dict(os.environ, {"SEMANTIC_CACHE_THRESHOLD": "1.5"}):
        assert _get_similarity_threshold() == 1.0


def test_r1b_threshold_ignores_invalid_string():
    with patch.dict(os.environ, {"SEMANTIC_CACHE_THRESHOLD": "not_a_float"}):
        assert _get_similarity_threshold() == DEFAULT_SIMILARITY_THRESHOLD


def test_r1b_default_ttl_when_env_unset():
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("SEMANTIC_CACHE_TTL_SECONDS", None)
        assert _get_cache_ttl_seconds() == DEFAULT_CACHE_TTL_SECONDS


def test_r1b_ttl_from_env():
    with patch.dict(os.environ, {"SEMANTIC_CACHE_TTL_SECONDS": "3600"}):
        assert _get_cache_ttl_seconds() == 3600


def test_r1b_ttl_zero_disables_expiry():
    with patch.dict(os.environ, {"SEMANTIC_CACHE_TTL_SECONDS": "0"}):
        assert _get_cache_ttl_seconds() == 0


def test_r1b_ttl_ignores_negative():
    with patch.dict(os.environ, {"SEMANTIC_CACHE_TTL_SECONDS": "-100"}):
        assert _get_cache_ttl_seconds() == DEFAULT_CACHE_TTL_SECONDS


def test_r1b_ttl_ignores_invalid_string():
    with patch.dict(os.environ, {"SEMANTIC_CACHE_TTL_SECONDS": "never"}):
        assert _get_cache_ttl_seconds() == DEFAULT_CACHE_TTL_SECONDS
