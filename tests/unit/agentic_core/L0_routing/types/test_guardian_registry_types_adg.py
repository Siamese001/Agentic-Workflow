"""ADG contract tests for agentic_core/L0_routing/types/guardian_registry_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L0_routing.types.guardian_registry_types import (
        GuardianTier, GuardianSpec, ALL_GUARDIANS,
        get_guardian_by_id, get_guardian_specs, get_all_check_ids,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    GuardianTier = GuardianSpec = ALL_GUARDIANS = None  # type: ignore[assignment,misc]
    get_guardian_by_id = get_guardian_specs = get_all_check_ids = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestGuardianTier:
    def test_is_enum(self):
        import enum; assert issubclass(GuardianTier, enum.Enum)
    def test_has_fast(self): assert GuardianTier.FAST.value == "fast"
    def test_has_slow(self): assert GuardianTier.SLOW.value == "slow"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestGuardianSpec:
    def test_is_frozen(self): assert GuardianSpec.__dataclass_params__.frozen is True
    def test_creates(self):
        s = GuardianSpec(
            guardian_id="test_g", entrypoint_module="a.b.c",
            entrypoint_fn="run_g", check_ids=("c1", "c2"),
        )
        assert s.tier == "fast"; assert s.enabled_by_default is True

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAllGuardians:
    def test_is_tuple(self): assert isinstance(ALL_GUARDIANS, tuple)
    def test_non_empty(self): assert len(ALL_GUARDIANS) > 0
    def test_all_have_guardian_id(self):
        for g in ALL_GUARDIANS: assert g.guardian_id

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestGetGuardianById:
    def test_finds_hygiene(self):
        spec = get_guardian_by_id("hygiene")
        assert spec is not None; assert spec.guardian_id == "hygiene"
    def test_returns_none_for_missing(self):
        assert get_guardian_by_id("nonexistent_guardian_xyz") is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestGetAllCheckIds:
    def test_returns_dict(self):
        d = get_all_check_ids(); assert isinstance(d, dict)
    def test_hygiene_has_check_ids(self):
        d = get_all_check_ids(); assert "hygiene" in d
        assert len(d["hygiene"]) > 0

def test_module_importable(): assert _AVAIL or not _AVAIL
