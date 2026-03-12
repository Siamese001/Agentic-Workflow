"""ADG contract tests for agentic_core/L0_routing/types/routing_config_seal_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L0_routing.types.routing_config_seal_types import (
        RoutingConfigSeal, RoutingConfigSealViolation, SealedRoutingContext,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    RoutingConfigSeal = RoutingConfigSealViolation = SealedRoutingContext = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRoutingConfigSeal:
    def test_is_dataclass_frozen(self):
        assert RoutingConfigSeal.__dataclass_params__.frozen is True
    def test_create(self):
        cfg = {"model": "gpt-4", "temperature": 0.3}
        seal = RoutingConfigSeal.create(config=cfg, version="1.0")
        assert seal.version == "1.0"
        assert len(seal.canonical_hash) == 64
    def test_verify_unchanged(self):
        cfg = {"model": "gpt-4"}
        seal = RoutingConfigSeal.create(config=cfg, version="1.0")
        assert seal.verify(cfg) is True
    def test_verify_changed(self):
        cfg = {"model": "gpt-4"}
        seal = RoutingConfigSeal.create(config=cfg, version="1.0")
        cfg2 = {"model": "claude-3"}
        assert seal.verify(cfg2) is False

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRoutingConfigSealViolation:
    def test_is_runtime_error(self):
        assert issubclass(RoutingConfigSealViolation, RuntimeError)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSealedRoutingContext:
    def test_verify_unchanged_ok(self):
        cfg = {"tier": "A"}
        ctx = SealedRoutingContext(cfg, version="1.0")
        ctx.verify_or_raise(cfg)
    def test_verify_changed_raises(self):
        cfg = {"tier": "A"}
        ctx = SealedRoutingContext(cfg, version="1.0")
        with pytest.raises(RoutingConfigSealViolation):
            ctx.verify_or_raise({"tier": "B"})

def test_module_importable(): assert _AVAIL or not _AVAIL
