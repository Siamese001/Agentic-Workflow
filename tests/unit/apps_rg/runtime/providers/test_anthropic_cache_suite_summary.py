from __future__ import annotations

import json

from apps_rg.runtime.providers.anthropic_cache_suite_summary import (
    discover_cache_receipts,
    write_suite_cache_summary,
)


def _write(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _receipt(section: str, creation: int, read: int, savings: float) -> dict:
    return {
        "provider": "external_claude",
        "model": "claude-sonnet-5",
        "section_id": section,
        "cache_enabled": True,
        "stable_prefix_hash": f"stable-{section}",
        "effective_cached_prefix_hash": f"effective-{section}",
        "input_tokens": 10,
        "output_tokens": 2,
        "cache_creation_input_tokens": creation,
        "cache_read_input_tokens": read,
        "estimated_uncached_input_tokens": creation + read + 10,
        "estimated_cached_input_tokens": 10,
        "estimated_input_token_savings": savings,
        "estimated_input_cost_without_cache_usd": 0.01,
        "estimated_input_cost_with_cache_usd": 0.004,
        "estimated_input_cost_savings_usd": 0.006,
    }


def test_suite_summary_prefers_lane_receipts_and_aggregates_selector_receipt(tmp_path) -> None:
    lane = tmp_path / "lanes" / "competencies"
    _write(
        lane / "lane_cache_summary.json",
        {"receipts": [_receipt("competencies", 100, 0, -25), _receipt("competencies", 0, 200, 180)]},
    )
    # Last-writer-wins leaf must not be double counted when lane summary exists.
    _write(lane / "provider_cache_receipt.json", _receipt("competencies", 0, 200, 180))
    _write(
        tmp_path / "selectors" / "bullet_pool_selector_cache_receipt.json",
        _receipt("bullet_pool_selector", 50, 100, 80),
    )

    receipts = discover_cache_receipts(tmp_path)
    assert len(receipts) == 3

    summary = write_suite_cache_summary(tmp_path)
    assert summary["receipt_count"] == 3
    assert summary["cache_creation_input_tokens"] == 150
    assert summary["cache_read_input_tokens"] == 300
    assert summary["estimated_input_token_savings"] == 235.0
    assert summary["estimated_input_cost_savings_usd"] == 0.018
    assert summary["cache_read_receipt_count"] == 2
    assert summary["by_section"]["competencies"]["receipt_count"] == 2
    assert (tmp_path / "anthropic_cache_suite_summary.json").is_file()
