"""Tests for routing-calibration YAML SSOT loader.

Plan: ``l0-routing-calibration-gap-audit-b3c9d4.md`` phase W2.P1.
Covers env-override > YAML > hardcoded-fallback precedence, namespace
per-override placeholder, malformed-input defensive behavior, and
``lru_cache`` reset semantics for tests that mutate the YAML.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path

import pytest

from agentic_core.L0_routing.config import routing_calibration


@pytest.fixture(autouse=True)
def _clear_cache_between_tests() -> Iterator[None]:
    """Every test starts with a cold YAML cache."""
    routing_calibration.reset_cache()
    yield
    routing_calibration.reset_cache()


def test_abstain_threshold_matches_yaml_ssot() -> None:
    """W2.P1: import-time threshold resolves to the YAML value (0.50)."""
    assert routing_calibration.get_abstain_threshold() == 0.50


def test_similarity_threshold_matches_yaml_ssot() -> None:
    """W2.P1: semantic-cache threshold resolves to the YAML value (0.98)."""
    assert routing_calibration.get_similarity_threshold() == 0.98


def test_env_override_wins_for_abstain(monkeypatch: pytest.MonkeyPatch) -> None:
    """W2.P1: ``AGENTIC_ABSTAIN_THRESHOLD`` overrides YAML."""
    monkeypatch.setenv("AGENTIC_ABSTAIN_THRESHOLD", "0.33")
    assert routing_calibration.get_abstain_threshold() == 0.33


def test_env_override_wins_for_similarity(monkeypatch: pytest.MonkeyPatch) -> None:
    """W2.P1: ``AGENTIC_SIMILARITY_THRESHOLD`` overrides YAML."""
    monkeypatch.setenv("AGENTIC_SIMILARITY_THRESHOLD", "0.80")
    assert routing_calibration.get_similarity_threshold() == 0.80


def test_malformed_env_falls_back_to_yaml(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """W2.P1: a non-numeric env override falls back to the hardcoded
    default (0.50) rather than crashing the router."""
    monkeypatch.setenv("AGENTIC_ABSTAIN_THRESHOLD", "not-a-number")
    assert routing_calibration.get_abstain_threshold() == 0.50


def test_out_of_range_env_value_falls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """W2.P1: values outside [0.0, 1.0] are rejected and fall back."""
    monkeypatch.setenv("AGENTIC_ABSTAIN_THRESHOLD", "2.5")
    assert routing_calibration.get_abstain_threshold() == 0.50


def test_namespace_lookup_falls_back_to_global_when_absent() -> None:
    """W2.P1: asking for a namespace not in the per-namespace map returns
    the global similarity_threshold (prepares for W3.P3 landing)."""
    assert routing_calibration.get_similarity_threshold(namespace="nonexistent_ns") == 0.98


def test_missing_yaml_uses_hardcoded_fallbacks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """W2.P1: if the YAML SSOT is absent, the loader must fall back to
    hardcoded defaults (0.50 / 0.98) — never raise."""
    monkeypatch.setattr(routing_calibration, "_YAML_PATH", tmp_path / "nope.yaml")
    routing_calibration.reset_cache()
    assert routing_calibration.get_abstain_threshold() == 0.50
    assert routing_calibration.get_similarity_threshold() == 0.98


def test_custom_yaml_values_are_honored(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """W2.P1: editing the YAML SSOT (and calling reset_cache) changes
    observable thresholds without any code change."""
    custom = tmp_path / "rc.yaml"
    custom.write_text(
        """
version: 1
abstain:
  default_threshold: 0.42
semantic_cache:
  similarity_threshold: 0.85
  per_namespace_thresholds:
    tenant_alpha: 0.92
""".strip(),
        encoding="utf-8",
    )
    logging.info("C3 write receipt: routing calibration override written")
    monkeypatch.setattr(routing_calibration, "_YAML_PATH", custom)
    routing_calibration.reset_cache()
    assert routing_calibration.get_abstain_threshold() == 0.42
    assert routing_calibration.get_similarity_threshold() == 0.85
    # Per-namespace map (W3.P3 placeholder) honored end-to-end.
    assert routing_calibration.get_similarity_threshold(namespace="tenant_alpha") == 0.92
    # Unknown namespace falls back to global.
    assert routing_calibration.get_similarity_threshold(namespace="tenant_omega") == 0.85


def test_abstain_contract_import_uses_yaml_value() -> None:
    """W2.P1: ``abstain_contract.DEFAULT_ABSTAIN_THRESHOLD`` must reflect
    the YAML SSOT, proving the loader is actually wired in."""
    from agentic_core.runtime.contracts.abstain_contract import (
        DEFAULT_ABSTAIN_THRESHOLD,
    )

    assert DEFAULT_ABSTAIN_THRESHOLD == 0.50
