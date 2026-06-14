"""Wave 4.2 — unit tests for fact_id_typo_repair.

Covers deterministic candidate fact-id typo repair against an allowlist:
double-underscore collapse, legacy bullet id fixes, interior-whitespace strip,
fingerprint allowlist mapping, and bul_unify surface-id repair.
"""

from __future__ import annotations

import pytest

from apps_rg.runtime.validators.fact_id_typo_repair import (
    repair_fact_id_against_allowlist,
    repair_unify_bullet_surface_id,
)


class TestRepairWithoutAllowlist:
    def test_collapse_double_underscores_in_fact_id(self) -> None:
        assert (
            repair_fact_id_against_allowlist("fact_engineering_platform__005")
            == "fact_engineering_platform_005"
        )

    def test_non_fact_prefix_double_underscore_left_alone(self) -> None:
        # collapse only applies to fact_* ids
        assert repair_fact_id_against_allowlist("other__id") == "other__id"

    def test_legacy_bul_ibm_double_underscore(self) -> None:
        assert repair_fact_id_against_allowlist("bul_ibm__003") == "bul_ibm_003"

    def test_legacy_bul_ib_to_bul_ibm(self) -> None:
        assert repair_fact_id_against_allowlist("bul_ib_007") == "bul_ibm_007"

    def test_interior_whitespace_stripped(self) -> None:
        assert repair_fact_id_against_allowlist("fact_foo_ 003") == "fact_foo_003"

    def test_idempotent_clean_id(self) -> None:
        assert repair_fact_id_against_allowlist("fact_foo_003") == "fact_foo_003"


class TestRepairWithAllowlist:
    def test_exact_match_passthrough(self) -> None:
        allow = {"fact_foo_001"}
        assert repair_fact_id_against_allowlist("fact_foo_001", allow) == "fact_foo_001"

    def test_fingerprint_unique_match_maps(self) -> None:
        # "fact_foo_1" fingerprints same as the padded allowlist member.
        allow = {"fact_foo_001"}
        assert repair_fact_id_against_allowlist("fact_foo_1", allow) == "fact_foo_001"

    def test_zero_pad_match(self) -> None:
        allow = {"fact_bar_005"}
        assert repair_fact_id_against_allowlist("fact_bar_5", allow) == "fact_bar_005"

    def test_ambiguous_fingerprint_not_mapped(self) -> None:
        # two members share the same fingerprint -> no unique mapping, returns cleaned input
        allow = {"fact_foo_001", "fact_foo_002"}
        # fingerprint of cleaned "fact_foo_1" base collides with both -> ambiguous
        out = repair_fact_id_against_allowlist("fact_foo_xyz", allow)
        assert out == "fact_foo_xyz"

    def test_metric_tail_preserved_on_pad_match(self) -> None:
        allow = {"fact_bar_005"}
        out = repair_fact_id_against_allowlist("fact_bar_5_metric_ab", allow)
        assert out == "fact_bar_005_metric_ab"


class TestRepairUnifyBulletSurfaceId:
    def test_dot_prefixed_number_repaired(self) -> None:
        assert repair_unify_bullet_surface_id("bul_unify_.003") == "bul_unify_003"

    def test_zero_padded(self) -> None:
        assert repair_unify_bullet_surface_id("bul_unify_3") == "bul_unify_003"

    def test_allowlist_gate_metric_tail(self) -> None:
        allow = {"bul_unify_003_metric_ff"}
        out = repair_unify_bullet_surface_id("bul_unify_.003_metric_ff", allow)
        assert out == "bul_unify_003_metric_ff"

    def test_base_rejected_when_not_in_allowlist_falls_through(self) -> None:
        # base not in allowlist -> falls through to generic repair (which returns cleaned)
        allow = {"bul_unify_999"}
        out = repair_unify_bullet_surface_id("bul_unify_.003", allow)
        assert out == "bul_unify_.003"

    def test_non_unify_delegates_to_generic(self) -> None:
        assert repair_unify_bullet_surface_id("fact_x__001") == "fact_x_001"

    @pytest.mark.parametrize("raw", ["bul_unify_003", "bul_unify_.45"])
    def test_no_allowlist_accepts_surface(self, raw: str) -> None:
        out = repair_unify_bullet_surface_id(raw)
        assert out.startswith("bul_unify_")
        assert out.split("_")[-1].isdigit()
