"""Core-backed transport preflight wrapper tests."""

from __future__ import annotations

from apps_rg.runtime.judges.x1d_judge_transport_contract import (
    audit_json_output_lock_all_providers,
    audit_truncation_guard_all_providers,
)


def test_json_lock_preflight_passes() -> None:
    assert audit_json_output_lock_all_providers() == []


def test_truncation_preflight_passes() -> None:
    assert audit_truncation_guard_all_providers() == []
