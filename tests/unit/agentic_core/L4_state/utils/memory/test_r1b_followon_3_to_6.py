"""Tests for R1B follow-on items #3-#6.

#3 per-tier-thresholds  (tier_similarity_threshold)
#4 L1-cache-key-hardening  (_normalize_l1_context, _compute_hash legacy path)
#5 threshold-sweep-harness  (tools.cache.threshold_sweep_harness.sweep)
#6 prom-dashboards  (config/dashboards/semantic_cache.json shape)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


# ----- #3 per-tier-thresholds -----------------------------------------------


def test_tier_threshold_defaults(monkeypatch):
    monkeypatch.delenv("SEMANTIC_CACHE_THRESHOLD_STATIC", raising=False)
    monkeypatch.delenv("SEMANTIC_CACHE_THRESHOLD_DYNAMIC", raising=False)
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
        tier_similarity_threshold,
    )

    assert tier_similarity_threshold("static") == 1.0
    assert tier_similarity_threshold("dynamic") == 0.95


def test_tier_threshold_env_override(monkeypatch):
    monkeypatch.setenv("SEMANTIC_CACHE_THRESHOLD_DYNAMIC", "0.88")
    monkeypatch.setenv("SEMANTIC_CACHE_THRESHOLD_STATIC", "0.99")
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
        tier_similarity_threshold,
    )

    assert tier_similarity_threshold("dynamic") == pytest.approx(0.88)
    assert tier_similarity_threshold("static") == pytest.approx(0.99)


def test_tier_threshold_invalid_falls_through(monkeypatch):
    monkeypatch.setenv("SEMANTIC_CACHE_THRESHOLD_DYNAMIC", "not-a-float")
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
        tier_similarity_threshold,
    )

    assert tier_similarity_threshold("dynamic") == 0.95


def test_tier_threshold_unknown_tier_is_safe(monkeypatch):
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
        tier_similarity_threshold,
    )

    # Unknown tier returns most conservative (1.0) so callers can't accidentally
    # serve a low-similarity hit.
    assert tier_similarity_threshold("nonexistent") == 1.0


# ----- #4 L1-cache-key-hardening --------------------------------------------


def test_normalize_l1_strips_and_collapses_whitespace(monkeypatch):
    monkeypatch.delenv("SEMANTIC_CACHE_L1_KEY_HARDENING", raising=False)
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
        _normalize_l1_context,
    )

    assert _normalize_l1_context("  hello   world  \n") == "hello world"
    assert _normalize_l1_context("a\tb\nc") == "a b c"


def test_normalize_l1_nfkc_unicode(monkeypatch):
    monkeypatch.delenv("SEMANTIC_CACHE_L1_KEY_HARDENING", raising=False)
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
        _normalize_l1_context,
    )

    # Half-width katakana → full-width via NFKC
    assert _normalize_l1_context("ｶﾀｶﾅ") == "カタカナ"
    # Ligature ﬁ → fi
    assert _normalize_l1_context("ﬁnal") == "final"


def test_normalize_l1_disabled_passthrough(monkeypatch):
    monkeypatch.setenv("SEMANTIC_CACHE_L1_KEY_HARDENING", "0")
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
        _normalize_l1_context,
    )

    assert _normalize_l1_context("  hello   world  ") == "  hello   world  "


def test_compute_hash_normalizes_whitespace_legacy_path(monkeypatch):
    monkeypatch.delenv("SEMANTIC_CACHE_L1_KEY_HARDENING", raising=False)
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
        SemanticCacheManager,
    )

    mgr = SemanticCacheManager.__new__(SemanticCacheManager)
    # legacy path ⇒ no tenant_id ⇒ normalization applies
    h1 = mgr._compute_hash("hello world", "ns")
    h2 = mgr._compute_hash("  hello   world  ", "ns")
    h3 = mgr._compute_hash("hello\tworld", "ns")
    assert h1 == h2 == h3


def test_compute_hash_preserves_case(monkeypatch):
    """Case is intentionally preserved."""
    monkeypatch.delenv("SEMANTIC_CACHE_L1_KEY_HARDENING", raising=False)
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
        SemanticCacheManager,
    )

    mgr = SemanticCacheManager.__new__(SemanticCacheManager)
    assert mgr._compute_hash("Apple", "ns") != mgr._compute_hash("apple", "ns")


# ----- #5 threshold-sweep-harness -------------------------------------------


def _make_fixture(tmp_path: Path) -> Path:
    """3 candidates with different similarities, 2 correct, 1 incorrect."""
    rows = [
        {
            "query": "q1",
            "expected_answer_id": "a1",
            "candidate_answer_id": "a1",
            "candidate_similarity": 0.99,
        },
        {
            "query": "q2",
            "expected_answer_id": "a2",
            "candidate_answer_id": "a2",
            "candidate_similarity": 0.92,
        },
        {
            "query": "q3",
            "expected_answer_id": "a3",
            "candidate_answer_id": "WRONG",
            "candidate_similarity": 0.97,
        },
    ]
    p = tmp_path / "fix.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    return p


def test_sweep_basic_counts():
    from tools.cache.threshold_sweep_harness import sweep  # noqa: PLC0415

    fixtures = [
        {"expected_answer_id": "a", "candidate_answer_id": "a", "candidate_similarity": 0.99},
        {"expected_answer_id": "a", "candidate_answer_id": "b", "candidate_similarity": 0.96},
        {"expected_answer_id": "c", "candidate_answer_id": "c", "candidate_similarity": 0.80},
    ]
    rows = sweep(fixtures, [0.95, 0.90, 0.70])
    by_t = {r.threshold: r for r in rows}
    # t=0.95: only the first two qualify → 1 TP, 1 FP
    assert by_t[0.95].hits == 2
    assert by_t[0.95].true_positives == 1
    assert by_t[0.95].false_positives == 1
    # t=0.70: all 3 qualify → 2 TP, 1 FP
    assert by_t[0.70].hits == 3
    assert by_t[0.70].true_positives == 2
    assert by_t[0.70].false_positives == 1


def test_sweep_writes_csv_and_md(tmp_path):
    from tools.cache.threshold_sweep_harness import (  # noqa: PLC0415
        _load_fixtures,
        sweep,
        write_csv,
        write_md,
    )

    fix_path = _make_fixture(tmp_path)
    fixtures = _load_fixtures(fix_path)
    rows = sweep(fixtures, [0.95, 0.90])
    csv_path = tmp_path / "sweep.csv"
    md_path = tmp_path / "sweep.md"
    write_csv(rows, csv_path)
    write_md(rows, md_path)
    csv_text = csv_path.read_text(encoding="utf-8")
    assert "threshold,total,hits" in csv_text
    assert "0.950" in csv_text
    md_text = md_path.read_text(encoding="utf-8")
    assert "Threshold Sweep Report" in md_text
    assert "| 0.950 |" in md_text


def test_sweep_main_cli(tmp_path, capsys):
    from tools.cache.threshold_sweep_harness import main  # noqa: PLC0415

    fix_path = _make_fixture(tmp_path)
    csv_path = tmp_path / "out.csv"
    md_path = tmp_path / "out.md"
    rc = main(
        [
            "--fixtures",
            str(fix_path),
            "--thresholds",
            "0.95,0.90",
            "--out-csv",
            str(csv_path),
            "--out-md",
            str(md_path),
        ]
    )
    assert rc == 0
    assert csv_path.exists() and md_path.exists()


# ----- #6 prom-dashboards ---------------------------------------------------


def test_dashboard_json_is_valid_grafana_shape():
    path = Path(__file__).resolve().parents[6] / "config" / "dashboards" / "semantic_cache.json"
    assert path.exists(), f"dashboard not found at {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    # Required Grafana top-level keys
    for key in ("title", "uid", "panels", "schemaVersion", "tags"):
        assert key in data, f"missing required Grafana key: {key}"
    assert data["uid"] == "r1b-semantic-cache"
    assert "semantic-cache" in data["tags"]
    # Every panel must have id + type + title
    for panel in data["panels"]:
        assert "id" in panel and "type" in panel and "title" in panel


def test_dashboard_covers_all_event_codes():
    """Dashboard must reference the prom event codes the cache actually emits."""
    path = Path(__file__).resolve().parents[6] / "config" / "dashboards" / "semantic_cache.json"
    text = path.read_text(encoding="utf-8")
    # Codes recorded via _record_semantic_cache_prom_event() across the cache:
    required_codes = [
        "hit",
        "miss",
        "bypass",
        "scope_mismatch",
        "hybrid_reject",
        "support_manifest_reject",
        "cdc_evict",
        "neighborhood_evict",
    ]
    for code in required_codes:
        assert code in text, f"dashboard missing event code: {code}"
