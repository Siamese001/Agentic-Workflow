"""Tests for positional bullet_id injection into pool samples.

Closes Bug:BulletPoolSelectorBulletIdMissing — Brown SVP run
``full_resume_183cf9252e02`` ibm_bullets X3_BLOCK loop where RetiredProvider self-consistency
samples emitted bullets shaped ``{bullet_theme, bullet_text}`` (no ``bullet_id``),
``_bullet_by_id`` returned None for every required slot, and the Claude pool
selector merged zero bullets even though RetiredProvider's text was fully populated.
"""

from __future__ import annotations

from typing import Any

from apps_rg.runtime.judges.bullet_pool_claude_selector import (
    _bullet_by_id,
    _format_bullet_pool,
    inject_positional_bullet_ids_into_pool,
)
from apps_rg.runtime.reasoning.bullet_lane_self_consistency import SelfConsistencyPath


def _path(idx: int, bullets: list[dict[str, Any]]) -> SelfConsistencyPath:
    return SelfConsistencyPath(
        path_index=idx,
        temperature=0.5,
        runtime_generation_status="REAL_LLM",
        raw_output="",
        parsed={"bullets": bullets, "claim_ledger": []},
        parse_error="",
        provider_result=None,
    )


def _retired_provider_style_pool_sample() -> list[dict[str, Any]]:
    """Mirror the actual RetiredProvider pool shape captured in provider_response.json on the failing run."""
    return [
        {"bullet_theme": "Regulatory IT Transformations", "bullet_text": "Directed large-scale regulatory IT transformations and legacy-modernization programs."},
        {"bullet_theme": "Salesforce Analytics", "bullet_text": "Designed analytics in Salesforce to prioritize high-potential deals, generating $10M in new ARR."},
        {"bullet_theme": "Cost Optimization", "bullet_text": "Deployed transparent budget dashboards and microservices to reallocate resources, driving 30% cost optimization."},
        {"bullet_theme": "M&A Due Diligence", "bullet_text": "Conducted preliminary M&A due diligence and developed synergy models."},
        {"bullet_theme": "AI and Cloud Revenue Expansion", "bullet_text": "Expanded AI and cloud-focused revenue streams, boosting joint revenue by 20%."},
    ]


IBM_REQUIRED = ("bul_ibm_001", "bul_ibm_002", "bul_ibm_003", "bul_ibm_004", "bul_ibm_005")


def test_injection_assigns_bullet_ids_when_missing() -> None:
    paths = [_path(0, _retired_provider_style_pool_sample())]
    injected = inject_positional_bullet_ids_into_pool(paths, IBM_REQUIRED)
    assert injected == 5
    parsed = paths[0].parsed
    assert isinstance(parsed, dict)
    bullets = parsed["bullets"]
    assigned_ids = [b["bullet_id"] for b in bullets]
    assert assigned_ids == list(IBM_REQUIRED)
    assert all(b["bullet_id_origin"] == "positional_pool_fallback" for b in bullets)


def test_injection_preserves_existing_bullet_ids() -> None:
    bullets = [
        {"bullet_id": "bul_ibm_001", "bullet_text": "Pre-assigned."},
        {"bullet_text": "Needs id assigned."},
    ]
    paths = [_path(0, bullets)]
    injected = inject_positional_bullet_ids_into_pool(paths, IBM_REQUIRED)
    assert injected == 1
    assert paths[0].parsed["bullets"][0]["bullet_id"] == "bul_ibm_001"
    assert "bullet_id_origin" not in paths[0].parsed["bullets"][0]
    assert paths[0].parsed["bullets"][1]["bullet_id"] == "bul_ibm_002"


def test_injection_skips_bullets_with_empty_text() -> None:
    bullets = [{"bullet_text": ""}, {"bullet_text": "Real bullet."}]
    paths = [_path(0, bullets)]
    injected = inject_positional_bullet_ids_into_pool(paths, IBM_REQUIRED)
    assert injected == 1
    assert "bullet_id" not in paths[0].parsed["bullets"][0]
    assert paths[0].parsed["bullets"][1]["bullet_id"] == "bul_ibm_002"


def test_injection_no_op_when_required_ids_empty() -> None:
    paths = [_path(0, _retired_provider_style_pool_sample())]
    injected = inject_positional_bullet_ids_into_pool(paths, None)
    assert injected == 0
    assert "bullet_id" not in paths[0].parsed["bullets"][0]
    injected2 = inject_positional_bullet_ids_into_pool(paths, ())
    assert injected2 == 0


def test_pool_text_renders_real_bullets_after_injection() -> None:
    """End-to-end: post-injection, _format_bullet_pool emits text instead of MISSING."""
    paths = [_path(0, _retired_provider_style_pool_sample())]
    pool_text_before = _format_bullet_pool(paths, IBM_REQUIRED)
    assert pool_text_before.count("MISSING") == 5
    inject_positional_bullet_ids_into_pool(paths, IBM_REQUIRED)
    pool_text_after = _format_bullet_pool(paths, IBM_REQUIRED)
    assert "MISSING" not in pool_text_after
    assert "Directed large-scale regulatory IT transformations" in pool_text_after
    assert "$10M in new ARR" in pool_text_after
    assert "30% cost optimization" in pool_text_after


def test_bullet_by_id_resolves_each_required_slot_after_injection() -> None:
    paths = [_path(0, _retired_provider_style_pool_sample())]
    inject_positional_bullet_ids_into_pool(paths, IBM_REQUIRED)
    parsed = paths[0].parsed
    for bid in IBM_REQUIRED:
        row = _bullet_by_id(parsed, bid)
        assert row is not None, f"slot {bid} unresolved after injection"
        assert row.get("bullet_text"), f"slot {bid} has empty text"
