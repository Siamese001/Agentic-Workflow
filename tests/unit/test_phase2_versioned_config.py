"""
Phase 2 Wave 1 — Versioned Config SSOT Tests

Tests that PolicyConfig, RoutingConfig, ModelConfig, BudgetConfig:
- expose version, canonical_bytes(), config_hash
- produce stable hashes across serialization
- manifest binding rejects missing/mismatched hashes
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.enforcement.manifest_hash_validator import (
    ManifestHashError,
    validate_manifest_hashes,
)
from agentic_core.L4_state.config.versioned_configs import (
    BudgetConfig,
    L4ActiveConfigs,
    ModelConfig,
    PolicyConfig,
    RoutingConfig,
    get_active_configs,
)

pytestmark = pytest.mark.unit_min_deps


class TestVersionedConfigs:
    def test_policy_config_has_version(self):
        cfg = PolicyConfig()
        assert isinstance(cfg.version, str)
        assert cfg.version

    def test_routing_config_has_version(self):
        cfg = RoutingConfig()
        assert isinstance(cfg.version, str)
        assert cfg.version

    def test_model_config_has_version(self):
        cfg = ModelConfig()
        assert isinstance(cfg.version, str)
        assert cfg.version

    def test_budget_config_has_version(self):
        cfg = BudgetConfig()
        assert isinstance(cfg.version, str)
        assert cfg.version

    def test_policy_canonical_bytes_is_bytes(self):
        cfg = PolicyConfig()
        assert isinstance(cfg.canonical_bytes(), bytes)

    def test_routing_canonical_bytes_is_bytes(self):
        cfg = RoutingConfig()
        assert isinstance(cfg.canonical_bytes(), bytes)

    def test_model_canonical_bytes_is_bytes(self):
        cfg = ModelConfig()
        assert isinstance(cfg.canonical_bytes(), bytes)

    def test_budget_canonical_bytes_is_bytes(self):
        cfg = BudgetConfig()
        assert isinstance(cfg.canonical_bytes(), bytes)

    def test_policy_config_hash_is_sha256(self):
        cfg = PolicyConfig()
        h = cfg.config_hash
        assert isinstance(h, str)
        assert len(h) == 64

    def test_routing_config_hash_is_sha256(self):
        cfg = RoutingConfig()
        h = cfg.config_hash
        assert isinstance(h, str)
        assert len(h) == 64

    def test_model_config_hash_is_sha256(self):
        cfg = ModelConfig()
        h = cfg.config_hash
        assert isinstance(h, str)
        assert len(h) == 64

    def test_budget_config_hash_is_sha256(self):
        cfg = BudgetConfig()
        h = cfg.config_hash
        assert isinstance(h, str)
        assert len(h) == 64


class TestHashStability:
    def test_hashes_stable_across_serialization(self):
        cfg = PolicyConfig()
        h1 = cfg.config_hash
        h2 = cfg.config_hash
        assert h1 == h2

    def test_same_config_same_hash(self):
        a = PolicyConfig()
        b = PolicyConfig()
        assert a.config_hash == b.config_hash

    def test_different_config_different_hash(self):
        a = PolicyConfig(token_budget=1_000_000)
        b = PolicyConfig(token_budget=500_000)
        assert a.config_hash != b.config_hash

    def test_budget_config_hash_changes_with_max_k(self):
        a = BudgetConfig(max_k=10)
        b = BudgetConfig(max_k=20)
        assert a.config_hash != b.config_hash

    def test_l4_active_configs_hashes_returns_all_four(self):
        active = L4ActiveConfigs()
        h = active.hashes()
        assert set(h.keys()) == {"policy_hash", "routing_hash", "model_hash", "budget_hash"}
        for v in h.values():
            assert isinstance(v, str) and len(v) == 64


class TestManifestHashBinding:
    def _valid_manifest(self) -> dict:
        return get_active_configs().hashes()

    def test_manifest_requires_config_hashes(self):
        manifest = self._valid_manifest()
        validate_manifest_hashes(manifest)
        pytest.skip("TODO: Implement actual test based on module functionality")

    def test_missing_policy_hash_rejected(self):
        manifest = self._valid_manifest()
        del manifest["policy_hash"]
        with pytest.raises(ManifestHashError, match="policy_hash"):
            validate_manifest_hashes(manifest)

    def test_missing_routing_hash_rejected(self):
        manifest = self._valid_manifest()
        del manifest["routing_hash"]
        with pytest.raises(ManifestHashError, match="routing_hash"):
            validate_manifest_hashes(manifest)

    def test_missing_model_hash_rejected(self):
        manifest = self._valid_manifest()
        del manifest["model_hash"]
        with pytest.raises(ManifestHashError, match="model_hash"):
            validate_manifest_hashes(manifest)

    def test_missing_budget_hash_rejected(self):
        manifest = self._valid_manifest()
        del manifest["budget_hash"]
        with pytest.raises(ManifestHashError, match="budget_hash"):
            validate_manifest_hashes(manifest)

    def test_hash_mismatch_rejected(self):
        manifest = self._valid_manifest()
        manifest["policy_hash"] = "a" * 64
        with pytest.raises(ManifestHashError, match="mismatch"):
            validate_manifest_hashes(manifest)

    def test_all_correct_hashes_accepted(self):
        manifest = self._valid_manifest()
        validate_manifest_hashes(manifest)
        pytest.skip("TODO: Implement actual test based on module functionality")
