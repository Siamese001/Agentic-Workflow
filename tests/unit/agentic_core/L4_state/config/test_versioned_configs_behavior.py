"""Behavioral tests for ``agentic_core.L4_state.config.versioned_configs``.

Covers the L4 SSOT versioned config family — PolicyConfig, RoutingConfig,
ModelConfig, BudgetConfig, MLCacheConfig — plus the L4ActiveConfigs registry
and module-level singletons. Every config class publishes:
- canonical_bytes() — JSON-encoded, sort_keys, no whitespace
- config_hash — SHA-256 of canonical bytes
Both must be deterministic (reorder-invariant inputs where lists are sorted).
"""

from __future__ import annotations

import hashlib
import json

import pytest

from agentic_core.L4_state.config.versioned_configs import (
    BudgetConfig,
    L4ActiveConfigs,
    MLCacheConfig,
    ModelConfig,
    PolicyConfig,
    RoutingConfig,
    get_active_configs,
    get_ml_cache_config,
)


# ---- Shared invariants ------------------------------------------------

ALL_CONFIGS = [
    PolicyConfig(),
    RoutingConfig(),
    ModelConfig(),
    BudgetConfig(),
    MLCacheConfig(),
]


class TestCanonicalBytesInvariant:
    @pytest.mark.parametrize("cfg", ALL_CONFIGS)
    def test_canonical_bytes_is_bytes(self, cfg: object) -> None:
        assert isinstance(cfg.canonical_bytes(), bytes)

    @pytest.mark.parametrize("cfg", ALL_CONFIGS)
    def test_canonical_bytes_is_valid_json(self, cfg: object) -> None:
        payload = json.loads(cfg.canonical_bytes())
        assert "version" in payload

    @pytest.mark.parametrize("cfg", ALL_CONFIGS)
    def test_canonical_bytes_no_whitespace(self, cfg: object) -> None:
        # separators=(",", ":") produces no whitespace between tokens
        assert b", " not in cfg.canonical_bytes()
        assert b": " not in cfg.canonical_bytes()

    @pytest.mark.parametrize("cfg", ALL_CONFIGS)
    def test_config_hash_is_sha256(self, cfg: object) -> None:
        expected = hashlib.sha256(cfg.canonical_bytes()).hexdigest()
        assert cfg.config_hash == expected
        assert len(cfg.config_hash) == 64

    @pytest.mark.parametrize("cfg", ALL_CONFIGS)
    def test_config_hash_deterministic(self, cfg: object) -> None:
        assert cfg.config_hash == cfg.config_hash


# ---- PolicyConfig ---------------------------------------------------

class TestPolicyConfig:
    def test_defaults(self) -> None:
        p = PolicyConfig()
        assert p.version == "1.0.0"
        assert p.token_budget == 1_000_000
        assert "file_read" in p.tool_allowlist
        assert "llm_call" in p.tool_allowlist

    def test_tool_allowlist_sorted_in_canonical_bytes(self) -> None:
        shuffled = PolicyConfig(tool_allowlist=("llm_call", "ast_parse", "file_read"))
        sorted_version = PolicyConfig(tool_allowlist=("ast_parse", "file_read", "llm_call"))
        # Hash must be invariant to input order because canonical_bytes sorts
        assert shuffled.config_hash == sorted_version.config_hash

    def test_file_scope_sorted_in_canonical_bytes(self) -> None:
        a = PolicyConfig(file_scope_whitelist=("/b", "/a"))
        b = PolicyConfig(file_scope_whitelist=("/a", "/b"))
        assert a.config_hash == b.config_hash


# ---- RoutingConfig --------------------------------------------------

class TestRoutingConfig:
    def test_defaults(self) -> None:
        r = RoutingConfig()
        assert r.depth_breaker == 10
        assert r.escalation_threshold == 0.85
        assert r.fallback_mode == "safe"
        assert r.escalation_mode == "normal"
        assert r.escalation_violation_code_denylist == ()

    def test_denylist_order_invariant(self) -> None:
        a = RoutingConfig(escalation_violation_code_denylist=("z", "a"))
        b = RoutingConfig(escalation_violation_code_denylist=("a", "z"))
        assert a.config_hash == b.config_hash

    def test_hash_changes_with_threshold(self) -> None:
        a = RoutingConfig(escalation_threshold=0.5)
        b = RoutingConfig(escalation_threshold=0.9)
        assert a.config_hash != b.config_hash


# ---- ModelConfig ----------------------------------------------------

class TestModelConfig:
    def test_defaults(self) -> None:
        m = ModelConfig()
        assert m.cognition_model == "gpt-4o"
        assert m.embedding_model == "text-embedding-3-small"
        assert m.embedding_dimensions == 1536

    def test_hash_changes_with_model_name(self) -> None:
        a = ModelConfig(cognition_model="gpt-4o")
        b = ModelConfig(cognition_model="gpt-4.1")
        assert a.config_hash != b.config_hash


# ---- BudgetConfig ---------------------------------------------------

class TestBudgetConfig:
    def test_defaults(self) -> None:
        b = BudgetConfig()
        assert b.token_budget == 1_000_000
        assert b.max_k == 10
        assert b.max_retries == 3
        assert b.backoff_base_seconds == 1.0

    def test_hash_changes_with_budget(self) -> None:
        a = BudgetConfig(token_budget=1000)
        b = BudgetConfig(token_budget=2000)
        assert a.config_hash != b.config_hash


# ---- MLCacheConfig --------------------------------------------------

class TestMLCacheConfig:
    def test_defaults(self) -> None:
        m = MLCacheConfig()
        assert m.default_ttl_seconds == 3600
        assert m.max_entries == 1000
        assert m.eviction_mode == "lru"

    def test_hash_changes_with_eviction_mode(self) -> None:
        a = MLCacheConfig(eviction_mode="lru")
        b = MLCacheConfig(eviction_mode="fifo")
        assert a.config_hash != b.config_hash


# ---- L4ActiveConfigs ------------------------------------------------

class TestL4ActiveConfigs:
    def test_defaults_populated(self) -> None:
        c = L4ActiveConfigs()
        assert isinstance(c.policy, PolicyConfig)
        assert isinstance(c.routing, RoutingConfig)
        assert isinstance(c.model, ModelConfig)
        assert isinstance(c.budget, BudgetConfig)

    def test_hashes_returns_four_keys(self) -> None:
        c = L4ActiveConfigs()
        h = c.hashes()
        assert set(h.keys()) == {"policy_hash", "routing_hash", "model_hash", "budget_hash"}

    def test_hashes_match_individual(self) -> None:
        c = L4ActiveConfigs()
        h = c.hashes()
        assert h["policy_hash"] == c.policy.config_hash
        assert h["routing_hash"] == c.routing.config_hash
        assert h["model_hash"] == c.model.config_hash
        assert h["budget_hash"] == c.budget.config_hash

    def test_hashes_all_sha256_hex(self) -> None:
        c = L4ActiveConfigs()
        for value in c.hashes().values():
            assert len(value) == 64
            int(value, 16)  # must parse as hex


# ---- Module-level singletons ---------------------------------------

class TestModuleLevelSingletons:
    def test_get_active_configs_returns_l4_active(self) -> None:
        assert isinstance(get_active_configs(), L4ActiveConfigs)

    def test_get_active_configs_returns_same_instance(self) -> None:
        assert get_active_configs() is get_active_configs()

    def test_get_ml_cache_config_returns_ml_cache(self) -> None:
        assert isinstance(get_ml_cache_config(), MLCacheConfig)

    def test_get_ml_cache_config_returns_same_instance(self) -> None:
        assert get_ml_cache_config() is get_ml_cache_config()
