"""Unit tests for retired rewrite-intensity field stripping on employment bullet JSON."""

from __future__ import annotations

from apps_rg.runtime.reasoning.employment_bullet_output_sanitize import (
    find_rewrite_intensity_model_violations,
    sanitize_l2_employment_bullet_record,
    strip_employment_bullet_intensity_model,
)


def test_strip_removes_top_level_and_per_bullet_intensity():
    raw = {
        "bullets": [
            {"bullet_id": "bul_unify_001", "bullet_text": "x", "rewrite_intensity": "HEAVY"},
        ],
        "rewrite_distribution": {"HEAVY": 1, "MODERATE": 0, "LIGHT_PROTECTED": 0, "total": 1},
        "self_check": {"distribution_valid": True, "normalized_by_lane": True},
    }
    cleaned = strip_employment_bullet_intensity_model(raw)
    assert cleaned is not None
    assert "rewrite_distribution" not in cleaned
    assert "rewrite_intensity" not in cleaned["bullets"][0]
    assert "distribution_valid" not in cleaned["self_check"]
    assert find_rewrite_intensity_model_violations(parsed_output=cleaned) == []


def test_sanitize_l2_record_strips_persisted_fields():
    l2 = {
        "bullets": [{"bullet_id": "bul_ibm_001", "rewrite_intensity": "MODERATE"}],
        "rewrite_distribution": {"HEAVY": 0},
        "self_check": {"distribution_valid": True},
    }
    cleaned = sanitize_l2_employment_bullet_record(l2)
    assert "rewrite_distribution" not in cleaned
    assert "rewrite_intensity" not in cleaned["bullets"][0]


def test_find_violations_detects_nested_intensity():
    parsed = {
        "bullets": [{"bullet_id": "bul_ibm_001", "rewrite_intensity": "MODERATE"}],
    }
    hits = find_rewrite_intensity_model_violations(parsed_output=parsed)
    assert any("rewrite_intensity" in h for h in hits)
