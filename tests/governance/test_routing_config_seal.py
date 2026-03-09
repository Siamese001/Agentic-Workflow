"""Wave 5.3: Immutable routing config seal tests.

Validates:
- RoutingConfigSeal is frozen
- Seal hash is deterministic
- Unchanged config passes verification
- Mutated config fails verification
- SealedRoutingContext raises on mutation
- sealed_at timestamp is set
"""

import pytest

from agentic_core.L0_routing.types.routing_config_seal_types import (
    RoutingConfigSeal,
    RoutingConfigSealViolation,
    SealedRoutingContext,
)

pytestmark = pytest.mark.governance

SAMPLE_CONFIG = {
    "model": "gpt-4",
    "temperature": 0.0,
    "routes": {"a": "agent-1", "b": "agent-2"},
}


class TestSealImmutability:
    """RoutingConfigSeal must be frozen."""

    def test_seal_is_frozen(self):
        seal = RoutingConfigSeal.create(config=SAMPLE_CONFIG, version="1.0")
        with pytest.raises(AttributeError):
            seal.canonical_hash = "tampered"  # type: ignore[misc]

    def test_sealed_at_is_set(self):
        seal = RoutingConfigSeal.create(config=SAMPLE_CONFIG, version="1.0")
        assert seal.sealed_at is not None
        assert len(seal.sealed_at) > 0


class TestSealDeterminism:
    """Same config must produce same hash."""

    def test_same_config_same_hash(self):
        a = RoutingConfigSeal.create(config=SAMPLE_CONFIG, version="1.0")
        b = RoutingConfigSeal.create(config=SAMPLE_CONFIG, version="1.0")
        assert a.canonical_hash == b.canonical_hash

    def test_different_config_different_hash(self):
        a = RoutingConfigSeal.create(config=SAMPLE_CONFIG, version="1.0")
        b = RoutingConfigSeal.create(
            config={"model": "gpt-3.5"},
            version="1.0",
        )
        assert a.canonical_hash != b.canonical_hash


class TestSealVerification:
    """Seal must detect config changes."""

    def test_unchanged_config_passes(self):
        config = dict(SAMPLE_CONFIG)
        seal = RoutingConfigSeal.create(config=config, version="1.0")
        assert seal.verify(config) is True

    def test_mutated_config_fails(self):
        config = dict(SAMPLE_CONFIG)
        seal = RoutingConfigSeal.create(config=config, version="1.0")
        config["new_key"] = "injected"
        assert seal.verify(config) is False

    def test_removed_key_fails(self):
        config = dict(SAMPLE_CONFIG)
        seal = RoutingConfigSeal.create(config=config, version="1.0")
        del config["model"]
        assert seal.verify(config) is False


class TestSealedRoutingContext:
    """Context must raise on mid-run mutation."""

    def test_no_mutation_passes(self):
        config = dict(SAMPLE_CONFIG)
        ctx = SealedRoutingContext(config, version="1.0")
        ctx.verify_or_raise(config)
        assert True  # no-exception contract

    def test_mutation_raises(self):
        config = dict(SAMPLE_CONFIG)
        ctx = SealedRoutingContext(config, version="1.0")
        config["temperature"] = 1.0
        with pytest.raises(RoutingConfigSealViolation):
            ctx.verify_or_raise(config)

    def test_seal_accessible(self):
        config = dict(SAMPLE_CONFIG)
        ctx = SealedRoutingContext(config, version="1.0")
        assert ctx.seal.version == "1.0"
        assert len(ctx.seal.canonical_hash) == 64
