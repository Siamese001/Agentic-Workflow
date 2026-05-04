"""apps_lic calibration-holdout W1 — config file completions sentinel tests.

Plan: .windsurf/plans/apps-lic-calibration-holdout-e8f1c4.md W1
Covers DS6-P1 (resurfacing_policy.yaml), DS7-P1 (arc_policy.yaml +
archetype_tone_policy.yaml), DS9-P1 (briefing_quality_policy.yaml per-class
recency).

Tests verify:
  - All 4 config files exist and parse without error.
  - Required keys present in each YAML.
  - NarrativeArcEngine loads arc_policy.yaml and returns source="config".
  - ArchetypeToneSelector loads archetype_tone_policy.yaml and returns source="config".
  - ResurfacingDetector loads resurfacing_policy.yaml and uses cool_off_days from it.
  - briefing_quality_policy.yaml v1.1 schema: per_class keys present for CTO,
    C_LEVEL, VP_ENG, HIRING_MANAGER, RECRUITER, SENIOR_TA.
  - Per-class thresholds are stricter (≤) than their bucket defaults.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

_CONFIG_DIR = Path(__file__).parent.parent.parent / "apps_lic" / "config"


# ===========================================================================
# Helpers
# ===========================================================================

def _load(name: str) -> dict:
    with open(_CONFIG_DIR / name, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


# ===========================================================================
# DS6-P1: resurfacing_policy.yaml
# ===========================================================================

class TestResurfacingPolicyYaml:
    def test_file_exists(self):
        assert (_CONFIG_DIR / "resurfacing_policy.yaml").exists()

    def test_parses_without_error(self):
        cfg = _load("resurfacing_policy.yaml")
        assert isinstance(cfg, dict)

    def test_has_cool_off_days(self):
        cfg = _load("resurfacing_policy.yaml")
        assert "cool_off_days" in cfg
        assert isinstance(cfg["cool_off_days"], (int, float))

    def test_has_warm_resurface_days(self):
        cfg = _load("resurfacing_policy.yaml")
        assert "warm_resurface_days" in cfg
        assert cfg["warm_resurface_days"] >= cfg["cool_off_days"]

    def test_cool_off_by_distance_present(self):
        cfg = _load("resurfacing_policy.yaml")
        assert "cool_off_by_distance" in cfg
        cbd = cfg["cool_off_by_distance"]
        for dist in ("cold", "warm", "referral", "known"):
            assert dist in cbd, f"missing distance key: {dist}"

    def test_cold_cooloff_greater_than_warm(self):
        cfg = _load("resurfacing_policy.yaml")
        cbd = cfg["cool_off_by_distance"]
        assert cbd["cold"] > cbd["warm"]

    def test_schema_version_present(self):
        cfg = _load("resurfacing_policy.yaml")
        assert "schema_version" in cfg

    def test_engine_loads_config_value(self, monkeypatch):
        monkeypatch.setenv("RESURFACING_ENABLED", "1")
        from apps_lic.engines.resurfacing_detector import ResurfacingDetector
        cfg = _load("resurfacing_policy.yaml")
        engine = ResurfacingDetector(config=cfg)
        assert engine._cool_off_days() == float(cfg["cool_off_days"])

    def test_blocked_below_cooloff(self, monkeypatch):
        monkeypatch.setenv("RESURFACING_ENABLED", "1")
        from apps_lic.engines.resurfacing_detector import ResurfacingDetector
        cfg = _load("resurfacing_policy.yaml")
        engine = ResurfacingDetector(config=cfg)
        cool_off = cfg["cool_off_days"]
        result = engine.detect(
            days_since_last_contact=cool_off - 1,
            relationship_distance="warm",
        )
        assert result.recommendation == "blocked"


# ===========================================================================
# DS7-P1: arc_policy.yaml
# ===========================================================================

class TestArcPolicyYaml:
    def test_file_exists(self):
        assert (_CONFIG_DIR / "arc_policy.yaml").exists()

    def test_parses_without_error(self):
        cfg = _load("arc_policy.yaml")
        assert isinstance(cfg, dict)

    def test_has_arc_matrix(self):
        cfg = _load("arc_policy.yaml")
        assert "arc_matrix" in cfg

    def test_all_recipient_buckets_present(self):
        cfg = _load("arc_policy.yaml")
        matrix = cfg["arc_matrix"]
        for bucket in ("exec", "hiring", "recruiter", "default"):
            assert bucket in matrix, f"missing bucket: {bucket}"

    def test_all_distance_buckets_present(self):
        cfg = _load("arc_policy.yaml")
        matrix = cfg["arc_matrix"]
        for bucket in ("exec", "hiring", "recruiter", "default"):
            for dist in ("cold", "warm", "referral", "known"):
                assert dist in matrix[bucket], f"missing {bucket}/{dist}"

    def test_all_arc_values_are_valid(self):
        cfg = _load("arc_policy.yaml")
        valid = set(cfg.get("valid_arcs", []))
        matrix = cfg["arc_matrix"]
        for bucket, dists in matrix.items():
            for dist, arc in dists.items():
                assert arc in valid, f"unknown arc '{arc}' at {bucket}/{dist}"

    def test_engine_uses_config_source(self, monkeypatch):
        monkeypatch.setenv("ARC_ENGINE_ENABLED", "1")
        from apps_lic.engines.narrative_arc_engine import NarrativeArcEngine
        cfg = _load("arc_policy.yaml")
        engine = NarrativeArcEngine(config=cfg)
        result = engine.select(recipient_class="CTO", relationship_distance="cold")
        assert result.source == "config"
        assert result.enabled is True

    def test_engine_returns_config_arc_value(self, monkeypatch):
        monkeypatch.setenv("ARC_ENGINE_ENABLED", "1")
        from apps_lic.engines.narrative_arc_engine import NarrativeArcEngine
        cfg = _load("arc_policy.yaml")
        engine = NarrativeArcEngine(config=cfg)
        # CTO → exec bucket, cold distance
        result = engine.select(recipient_class="CTO", relationship_distance="cold")
        expected = cfg["arc_matrix"]["exec"]["cold"]
        assert result.arc_name == expected

    def test_schema_version_present(self):
        cfg = _load("arc_policy.yaml")
        assert "schema_version" in cfg


# ===========================================================================
# DS7-P1: archetype_tone_policy.yaml
# ===========================================================================

class TestArchetypeTonePolicyYaml:
    def test_file_exists(self):
        assert (_CONFIG_DIR / "archetype_tone_policy.yaml").exists()

    def test_parses_without_error(self):
        cfg = _load("archetype_tone_policy.yaml")
        assert isinstance(cfg, dict)

    def test_has_tone_matrix(self):
        cfg = _load("archetype_tone_policy.yaml")
        assert "tone_matrix" in cfg

    def test_all_recipient_buckets_present(self):
        cfg = _load("archetype_tone_policy.yaml")
        matrix = cfg["tone_matrix"]
        for bucket in ("exec", "hiring", "recruiter", "default"):
            assert bucket in matrix, f"missing bucket: {bucket}"

    def test_all_distance_buckets_present(self):
        cfg = _load("archetype_tone_policy.yaml")
        matrix = cfg["tone_matrix"]
        for bucket in ("exec", "hiring", "recruiter", "default"):
            for dist in ("cold", "warm", "referral", "known"):
                assert dist in matrix[bucket], f"missing {bucket}/{dist}"

    def test_all_tone_values_are_valid(self):
        cfg = _load("archetype_tone_policy.yaml")
        valid = set(cfg.get("valid_archetypes", []))
        matrix = cfg["tone_matrix"]
        for bucket, dists in matrix.items():
            for dist, tone in dists.items():
                assert tone in valid, f"unknown archetype '{tone}' at {bucket}/{dist}"

    def test_engine_uses_config_source(self, monkeypatch):
        monkeypatch.setenv("ARCHETYPE_TONE_ENABLED", "1")
        from apps_lic.engines.archetype_tone_selector import ArchetypeToneSelector
        cfg = _load("archetype_tone_policy.yaml")
        engine = ArchetypeToneSelector(config=cfg)
        result = engine.select(recipient_class="CTO", relationship_distance="warm")
        assert result.source == "config"
        assert result.enabled is True

    def test_engine_returns_config_tone_value(self, monkeypatch):
        monkeypatch.setenv("ARCHETYPE_TONE_ENABLED", "1")
        from apps_lic.engines.archetype_tone_selector import ArchetypeToneSelector
        cfg = _load("archetype_tone_policy.yaml")
        engine = ArchetypeToneSelector(config=cfg)
        # CTO → exec bucket, warm distance
        result = engine.select(recipient_class="CTO", relationship_distance="warm")
        expected = cfg["tone_matrix"]["exec"]["warm"]
        assert result.archetype == expected

    def test_schema_version_present(self):
        cfg = _load("archetype_tone_policy.yaml")
        assert "schema_version" in cfg


# ===========================================================================
# DS9-P1: briefing_quality_policy.yaml per-class recency
# ===========================================================================

class TestBriefingQualityPolicyPerClass:
    def test_schema_version_is_1_1(self):
        cfg = _load("briefing_quality_policy.yaml")
        assert cfg["schema_version"] == "1.1"

    def test_per_class_key_present(self):
        cfg = _load("briefing_quality_policy.yaml")
        assert "per_class" in cfg["recency"]

    def test_required_per_class_keys_present(self):
        per_class = _load("briefing_quality_policy.yaml")["recency"]["per_class"]
        for rc in ("CTO", "C_LEVEL", "VP_ENG", "HIRING_MANAGER", "RECRUITER", "SENIOR_TA"):
            assert rc in per_class, f"missing per_class entry: {rc}"

    def test_per_class_entries_have_fail_and_marginal_days(self):
        per_class = _load("briefing_quality_policy.yaml")["recency"]["per_class"]
        for rc, thresholds in per_class.items():
            assert "fail_days" in thresholds, f"{rc} missing fail_days"
            assert "marginal_days" in thresholds, f"{rc} missing marginal_days"
            assert thresholds["fail_days"] < thresholds["marginal_days"], (
                f"{rc}: fail_days must be < marginal_days"
            )

    def test_cto_stricter_than_default_bucket(self):
        cfg = _load("briefing_quality_policy.yaml")["recency"]
        cto = cfg["per_class"]["CTO"]
        default = cfg["default"]
        assert cto["fail_days"] <= default["fail_days"]
        assert cto["marginal_days"] <= default["marginal_days"]

    def test_c_level_as_strict_as_executive_bucket(self):
        cfg = _load("briefing_quality_policy.yaml")["recency"]
        c_level = cfg["per_class"]["C_LEVEL"]
        exec_bucket = cfg["executive"]
        assert c_level["fail_days"] <= exec_bucket["fail_days"]

    def test_recruiter_more_lenient_than_exec(self):
        cfg = _load("briefing_quality_policy.yaml")["recency"]
        recruiter = cfg["per_class"]["RECRUITER"]
        exec_bucket = cfg["executive"]
        assert recruiter["fail_days"] > exec_bucket["fail_days"]

    def test_senior_ta_stricter_than_recruiter(self):
        cfg = _load("briefing_quality_policy.yaml")["recency"]
        senior_ta = cfg["per_class"]["SENIOR_TA"]
        recruiter = cfg["per_class"]["RECRUITER"]
        assert senior_ta["fail_days"] <= recruiter["fail_days"]

    def test_bucket_defaults_still_present(self):
        recency = _load("briefing_quality_policy.yaml")["recency"]
        for bucket in ("executive", "recruiter", "default"):
            assert bucket in recency, f"missing bucket: {bucket}"
            assert "fail_days" in recency[bucket]
            assert "marginal_days" in recency[bucket]
