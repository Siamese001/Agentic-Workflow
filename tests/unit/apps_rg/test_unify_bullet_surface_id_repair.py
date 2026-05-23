"""Unify bullet surface id typo repair (bul_unify_.003 -> bul_unify_003)."""

from __future__ import annotations

from apps_rg.runtime.validators.fact_id_typo_repair import repair_unify_bullet_surface_id


def test_repair_unify_bullet_surface_id_dot_typo() -> None:
    allowed = {"bul_unify_003", "bul_unify_003_metric_abc12345"}
    assert repair_unify_bullet_surface_id("bul_unify_.003", allowed) == "bul_unify_003"
    assert (
        repair_unify_bullet_surface_id("bul_unify_.003_metric_abc12345", allowed)
        == "bul_unify_003_metric_abc12345"
    )


def test_repair_unify_bullet_surface_id_without_allowlist() -> None:
    assert repair_unify_bullet_surface_id("bul_unify_.001", None) == "bul_unify_001"
