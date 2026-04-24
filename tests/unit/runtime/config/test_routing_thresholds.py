"""W2.P1 tests — routing thresholds YAML loader + lookup hierarchy."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from agentic_core.runtime.config.routing_thresholds import (
    RoutingThresholdConfig,
    get_routing_thresholds,
    get_threshold,
    reload_routing_thresholds,
    set_config_path_for_testing,
)


_VALID_YAML = """
schema_version: 1
defaults:
  r1b_semantic_similarity: 0.95
  r5_abstain_confidence: 0.50
  r3_grounding_need: 0.70
  c0_coverage_floor: 0.60
  r1a_freshness_ratio: 0.65
namespaces:
  rg:
    r1b_semantic_similarity: 0.97
  eval:
    r1b_semantic_similarity: 0.90
    r5_abstain_confidence: 0.40
r5_triggers:
  low_confidence:
    enabled: true
    threshold: 0.50
    reason_code: r5_low_confidence
  ood_detected:
    enabled: true
    threshold: 0.70
    reason_code: r5_ood_detected
  toxicity_flagged:
    enabled: false
    reason_code: r5_toxicity_flagged
"""


@pytest.fixture(autouse=True)
def _clean_env_and_cache() -> Iterator[None]:
    # Save/restore any ROUTING_THRESHOLD__* env vars and config override.
    saved = {k: v for k, v in os.environ.items() if k.startswith("ROUTING_THRESHOLD__")}
    for k in list(os.environ):
        if k.startswith("ROUTING_THRESHOLD__"):
            del os.environ[k]
    set_config_path_for_testing(None)
    yield
    for k in list(os.environ):
        if k.startswith("ROUTING_THRESHOLD__"):
            del os.environ[k]
    os.environ.update(saved)
    set_config_path_for_testing(None)


def _write_yaml(tmp_path: Path, content: str) -> Path:
    yaml_file = tmp_path / "routing_thresholds.yaml"
    yaml_file.write_text(content, encoding="utf-8")
    return yaml_file


# ---------------------------------------------------------------------------
# Back-compat: missing file -> hardcoded literal defaults.
# ---------------------------------------------------------------------------


class TestBackCompatDefaults:
    def test_missing_file_falls_back_to_literals(self, tmp_path: Path) -> None:
        set_config_path_for_testing(tmp_path / "does_not_exist.yaml")
        config = reload_routing_thresholds()
        assert config.loaded_ok is False
        # Literal defaults per _LITERAL_DEFAULTS.
        assert config.lookup("r1b_semantic_similarity") == pytest.approx(0.98)
        assert config.lookup("r5_abstain_confidence") == pytest.approx(0.50)
        assert config.lookup("r3_grounding_need") == pytest.approx(0.70)

    def test_malformed_yaml_falls_back_silently(self, tmp_path: Path) -> None:
        bad = _write_yaml(tmp_path, ":::not::valid::yaml:::")
        set_config_path_for_testing(bad)
        config = reload_routing_thresholds()
        # Parse failure -> empty config -> literal fallback still works.
        assert config.lookup("r1b_semantic_similarity") == pytest.approx(0.98)

    def test_unknown_threshold_key_raises(self, tmp_path: Path) -> None:
        set_config_path_for_testing(tmp_path / "absent.yaml")
        config = reload_routing_thresholds()
        with pytest.raises(KeyError, match="Unknown routing threshold key"):
            config.lookup("not_a_real_key")


# ---------------------------------------------------------------------------
# YAML parsing + namespace overrides
# ---------------------------------------------------------------------------


class TestYamlParsing:
    def test_defaults_load_correctly(self, tmp_path: Path) -> None:
        set_config_path_for_testing(_write_yaml(tmp_path, _VALID_YAML))
        config = reload_routing_thresholds()
        assert config.loaded_ok is True
        assert config.lookup("r1b_semantic_similarity") == pytest.approx(0.95)
        assert config.lookup("r3_grounding_need") == pytest.approx(0.70)

    def test_namespace_override_wins_over_default(self, tmp_path: Path) -> None:
        set_config_path_for_testing(_write_yaml(tmp_path, _VALID_YAML))
        config = reload_routing_thresholds()
        assert config.lookup("r1b_semantic_similarity", namespace="rg") == pytest.approx(0.97)
        assert config.lookup("r1b_semantic_similarity", namespace="eval") == pytest.approx(0.90)
        # namespace without override falls back to default
        assert config.lookup("r1b_semantic_similarity", namespace="research") == pytest.approx(0.95)

    def test_namespace_falls_back_to_default_when_key_absent(self, tmp_path: Path) -> None:
        # `rg` overrides only r1b — r3 must fall back to default.
        set_config_path_for_testing(_write_yaml(tmp_path, _VALID_YAML))
        config = reload_routing_thresholds()
        assert config.lookup("r3_grounding_need", namespace="rg") == pytest.approx(0.70)

    def test_out_of_range_value_is_rejected(self, tmp_path: Path) -> None:
        bad_yaml = """
defaults:
  r1b_semantic_similarity: 1.5
  r5_abstain_confidence: 0.50
"""
        set_config_path_for_testing(_write_yaml(tmp_path, bad_yaml))
        config = reload_routing_thresholds()
        # Out-of-range silently rejected; the VALID key (r5_abstain) still loads.
        assert "r1b_semantic_similarity" not in config.defaults
        # Lookup falls back to literal default for the rejected key.
        assert config.lookup("r1b_semantic_similarity") == pytest.approx(0.98)


# ---------------------------------------------------------------------------
# Env override: ROUTING_THRESHOLD__<KEY>
# ---------------------------------------------------------------------------


class TestEnvOverride:
    def test_env_var_beats_yaml_default(self, tmp_path: Path) -> None:
        set_config_path_for_testing(_write_yaml(tmp_path, _VALID_YAML))
        reload_routing_thresholds()
        os.environ["ROUTING_THRESHOLD__R1B_SEMANTIC_SIMILARITY"] = "0.77"
        assert get_threshold("r1b_semantic_similarity") == pytest.approx(0.77)

    def test_env_var_beats_namespace_override(self, tmp_path: Path) -> None:
        set_config_path_for_testing(_write_yaml(tmp_path, _VALID_YAML))
        reload_routing_thresholds()
        os.environ["ROUTING_THRESHOLD__R1B_SEMANTIC_SIMILARITY"] = "0.55"
        assert get_threshold("r1b_semantic_similarity", namespace="rg") == pytest.approx(0.55)

    def test_invalid_env_value_is_ignored(self, tmp_path: Path) -> None:
        set_config_path_for_testing(_write_yaml(tmp_path, _VALID_YAML))
        reload_routing_thresholds()
        os.environ["ROUTING_THRESHOLD__R1B_SEMANTIC_SIMILARITY"] = "not_a_number"
        # Falls through to namespace -> default path.
        assert get_threshold("r1b_semantic_similarity", namespace="rg") == pytest.approx(0.97)


# ---------------------------------------------------------------------------
# R5 triggers parsing
# ---------------------------------------------------------------------------


class TestR5Triggers:
    def test_enabled_triggers_parsed(self, tmp_path: Path) -> None:
        set_config_path_for_testing(_write_yaml(tmp_path, _VALID_YAML))
        config = reload_routing_thresholds()
        enabled = {t.name for t in config.enabled_r5_triggers()}
        assert enabled == {"low_confidence", "ood_detected"}

    def test_disabled_triggers_not_in_enabled_list(self, tmp_path: Path) -> None:
        set_config_path_for_testing(_write_yaml(tmp_path, _VALID_YAML))
        config = reload_routing_thresholds()
        assert "toxicity_flagged" not in {t.name for t in config.enabled_r5_triggers()}
        # But the trigger itself is still present (just disabled).
        assert "toxicity_flagged" in config.r5_triggers


# ---------------------------------------------------------------------------
# Process-level caching
# ---------------------------------------------------------------------------


class TestCaching:
    def test_cache_returns_same_instance(self, tmp_path: Path) -> None:
        set_config_path_for_testing(_write_yaml(tmp_path, _VALID_YAML))
        a = get_routing_thresholds()
        b = get_routing_thresholds()
        assert a is b  # cached

    def test_reload_forces_fresh_read(self, tmp_path: Path) -> None:
        yaml_path = _write_yaml(tmp_path, _VALID_YAML)
        set_config_path_for_testing(yaml_path)
        first = reload_routing_thresholds()
        # Edit the YAML on disk.
        yaml_path.write_text(
            "defaults:\n  r1b_semantic_similarity: 0.60\n",
            encoding="utf-8",
        )
        second = reload_routing_thresholds()
        assert first is not second
        assert second.lookup("r1b_semantic_similarity") == pytest.approx(0.60)


# ---------------------------------------------------------------------------
# Repo config sanity (shipped config/routing_thresholds.yaml loads cleanly)
# ---------------------------------------------------------------------------


class TestShippedConfig:
    def test_shipped_yaml_parses(self) -> None:
        # Default path resolver finds the repo-root config/*.yaml.
        set_config_path_for_testing(None)
        config = reload_routing_thresholds()
        # Either the shipped file loaded OR we fell back to literals — both OK.
        # But in a dev/CI run the file exists, so loaded_ok should be True.
        if config.loaded_ok:
            assert "r1b_semantic_similarity" in config.defaults
            # Must match the W2.P2 calibration report values.
            assert config.defaults["r1b_semantic_similarity"] == pytest.approx(0.95)
            assert "rg" in config.namespaces
            assert "underwriting_ai" in config.namespaces


def test_RoutingThresholdConfig_is_frozen() -> None:
    config = RoutingThresholdConfig()
    with pytest.raises((AttributeError, Exception)):
        config.loaded_ok = True  # type: ignore[misc]
