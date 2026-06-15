from __future__ import annotations

from apps_rg.runtime import offline_contract_status as status


def test_offline_contract_stub_is_permanently_disabled_with_stable_marker() -> None:
    assert status.OFFLINE_CONTRACT_STUB_RUNTIME_STATUS == "OFFLINE_CONTRACT_STUB"
    assert status.offline_contract_stub_enabled() is False
    assert status.effective_offline_contract_stub_enabled() is False
    assert set(status.__all__) == {
        "OFFLINE_CONTRACT_STUB_RUNTIME_STATUS",
        "effective_offline_contract_stub_enabled",
        "offline_contract_stub_enabled",
    }
