"""Tests for W1 additive split-base classes (plan c8e4f1)."""

from __future__ import annotations

from typing import Any

import pytest

from agentic_core.base_agents.SovereignHealerBase import (
    HealerCannotValidateError,
    SnapshotBindingError,
    SovereignHealerBase,
)
from agentic_core.base_agents.SovereignValidatorBase import (
    SovereignValidatorBase,
    ValidatorCannotHealError,
)


class _ExampleValidator(SovereignValidatorBase):
    def validate(self, packet: Any) -> dict[str, Any]:
        return {"is_allowed": True, "reason": "ok", "evidence": {"packet": packet}}


class _ExampleHealer(SovereignHealerBase):
    def heal(self, heal_request: Any) -> dict[str, Any]:
        return {"outcome": "SUCCESS", "repair_count": 1}


class TestValidatorBase:
    def test_validator_instantiates_and_validates(self):
        v = _ExampleValidator()
        out = v.validate({"kind": "test"})
        assert out["is_allowed"] is True
        assert out["evidence"]["packet"]["kind"] == "test"

    def test_validator_cannot_heal(self):
        v = _ExampleValidator()
        with pytest.raises(ValidatorCannotHealError):
            v.heal({"violation": "x"})

    def test_validator_rejects_subclass_with_heal(self):
        with pytest.raises(TypeError, match="cannot define 'heal"):

            class _Bad(SovereignValidatorBase):  # noqa: N801
                def validate(self, packet: Any) -> dict[str, Any]:
                    return {"is_allowed": True}

                def heal(self, *args, **kwargs):  # guardian: allow-type-erasure
                    return {}

    def test_validator_rejects_subclass_with_heal_repository(self):
        with pytest.raises(TypeError, match="cannot define 'heal_repository"):

            class _Bad(SovereignValidatorBase):  # noqa: N801
                def validate(self, packet: Any) -> dict[str, Any]:
                    return {"is_allowed": True}

                def heal_repository(self, *args, **kwargs):  # guardian: allow-type-erasure
                    return {}

    def test_validator_rejects_subclass_with_repair(self):
        with pytest.raises(TypeError, match="cannot define 'repair"):

            class _Bad(SovereignValidatorBase):  # noqa: N801
                def validate(self, packet: Any) -> dict[str, Any]:
                    return {"is_allowed": True}

                def repair(self, *args, **kwargs):  # guardian: allow-type-erasure
                    return {}


class TestHealerBase:
    def test_healer_instantiates_and_heals(self):
        h = _ExampleHealer()
        out = h.heal({"kind": "test"})
        assert out["outcome"] == "SUCCESS"

    def test_healer_cannot_validate(self):
        h = _ExampleHealer()
        with pytest.raises(HealerCannotValidateError):
            h.validate({"packet": "x"})

    def test_healer_rejects_subclass_with_validate(self):
        with pytest.raises(TypeError, match="cannot define 'validate"):

            class _Bad(SovereignHealerBase):  # noqa: N801
                def heal(self, heal_request: Any) -> Any:
                    return {}

                def validate(self, *args, **kwargs):  # guardian: allow-type-erasure
                    return True

    def test_healer_rejects_subclass_with_check(self):
        with pytest.raises(TypeError, match="cannot define 'check"):

            class _Bad(SovereignHealerBase):  # noqa: N801
                def heal(self, heal_request: Any) -> Any:
                    return {}

                def check(self, *args, **kwargs):  # guardian: allow-type-erasure
                    return True


class TestSnapshotBinding:
    def test_matching_snapshots_no_raise(self):
        SovereignHealerBase.assert_snapshot_binding(
            heal_blueprint_hash="bp-1",
            heal_policy_hash="pol-1",
            parent_blueprint_hash="bp-1",
            parent_policy_hash="pol-1",
        )

    def test_blueprint_mismatch_raises(self):
        with pytest.raises(SnapshotBindingError, match="blueprint_hash mismatch"):
            SovereignHealerBase.assert_snapshot_binding(
                heal_blueprint_hash="bp-2",
                heal_policy_hash="pol-1",
                parent_blueprint_hash="bp-1",
                parent_policy_hash="pol-1",
            )

    def test_policy_mismatch_raises(self):
        with pytest.raises(SnapshotBindingError, match="policy_hash mismatch"):
            SovereignHealerBase.assert_snapshot_binding(
                heal_blueprint_hash="bp-1",
                heal_policy_hash="pol-2",
                parent_blueprint_hash="bp-1",
                parent_policy_hash="pol-1",
            )

    def test_max_repair_count_is_bounded(self):
        assert SovereignHealerBase.MAX_REPAIR_COUNT >= 1
        assert SovereignHealerBase.MAX_REPAIR_COUNT <= 10  # sanity bound
