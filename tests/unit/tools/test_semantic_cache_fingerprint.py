"""Semantic cache fingerprint capture (plan c9f1a3)."""
from __future__ import annotations

import json
from pathlib import Path

from tools.cache.capture_semantic_cache_fingerprint import capture_fingerprint, write_artifacts


def test_capture_fingerprint_has_composite_sha256(tmp_path: Path) -> None:
    doc = capture_fingerprint(namespace="apps_rg", label="unit_test")
    assert doc["composite_sha256"]
    assert len(doc["composite_sha256"]) == 64
    assert "apps_rg" in doc["scope_limit"]


def test_write_artifacts_roundtrip(tmp_path: Path) -> None:
    doc = capture_fingerprint(namespace="apps_rg", label="unit_write")
    out = tmp_path / "fp.json"
    write_artifacts(doc, out)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["composite_sha256"] == doc["composite_sha256"]
