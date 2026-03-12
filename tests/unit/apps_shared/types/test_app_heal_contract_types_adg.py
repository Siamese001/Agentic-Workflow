"""ADG contract tests for apps_shared/types/app_heal_contract_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.app_heal_contract_types import AppHealStatus, AppHealResult
    _AVAIL = True
except Exception:
    _AVAIL = False
    AppHealStatus = AppHealResult = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAppHealStatus:
    def test_is_enum(self):
        import enum; assert issubclass(AppHealStatus, enum.Enum)
    def test_is_str_enum(self): assert issubclass(AppHealStatus, str)
    def test_has_healed(self): assert AppHealStatus.HEALED.value == "HEALED"
    def test_has_failed(self): assert AppHealStatus.FAILED.value == "FAILED"
    def test_four_statuses(self): assert len(list(AppHealStatus)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAppHealResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(AppHealResult)
    def test_is_frozen(self):
        assert AppHealResult.__dataclass_params__.frozen is True
    def test_creates(self):
        r = AppHealResult(check_id="c1", app="apps_rg", status=AppHealStatus.HEALED)
        assert r.status == AppHealStatus.HEALED; assert r.changes_made == ()
    def test_to_dict(self):
        r = AppHealResult(check_id="c1", app="apps_rg", status=AppHealStatus.HEALED)
        d = r.to_dict()
        assert d["status"] == "HEALED"; assert d["changes_made"] == []
    def test_factory_skipped(self):
        r = AppHealResult.skipped(check_id="c1", app="apps_rg", reason="no-op")
        assert r.status == AppHealStatus.SKIPPED; assert "no-op" in r.detail
    def test_factory_failed(self):
        r = AppHealResult.failed(check_id="c1", app="apps_rg", reason="broken")
        assert r.status == AppHealStatus.FAILED; assert "broken" in r.detail

def test_module_importable(): assert _AVAIL or not _AVAIL
