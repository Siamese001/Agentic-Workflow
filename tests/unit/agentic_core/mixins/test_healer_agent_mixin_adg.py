"""ADG-driven tests for mixins/healer_agent_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.mixins.healer_agent_mixin import HealerAgentMixin


class TestHealerAgentMixin:
    def test_importable(self):
        assert callable(HealerAgentMixin)

    def test_heal_requires_dict(self):
        mixin = HealerAgentMixin()
        result = mixin.heal("not-a-dict")
        assert result["status"] == "failed"
        assert "dictionary" in result["errors"][0]

    def test_heal_delegates_to_heal_impl(self):
        class ConcreteHealer(HealerAgentMixin):
            def _heal_impl(self, v):
                return {"status": "success", "details": "ok", "artifacts": [], "errors": []}

        healer = ConcreteHealer()
        result = healer.heal({"file": "foo.py", "type": "test"})
        assert result["status"] == "success"

    def test_heal_impl_raises_not_implemented(self):
        mixin = HealerAgentMixin()
        result = mixin.heal({"file": "foo.py"})
        assert result["status"] == "failed"

    def test_has_normalize_result(self):
        assert hasattr(HealerAgentMixin, "_normalize_result")
