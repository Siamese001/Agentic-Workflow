"""Unit tests for the ADG-first PDP (P6)."""

from __future__ import annotations

from tools.policy.decisions import (
    AdgFirstDecision,
    AdgFirstVerdict,
    classify_grep_for_deps,
)


def _call(**kwargs) -> AdgFirstDecision:
    """Helper with sensible defaults; override per test."""
    defaults = dict(
        grep_for_deps_present=False,
        adg_mcp_used=False,
        adg_health_checked=False,
        degraded_fallback_declared=False,
        sqlite_direct_used=False,
        adg_snapshot_present=False,
        bypass_set=False,
    )
    defaults.update(kwargs)
    return classify_grep_for_deps(**defaults)


def test_no_grep_is_compliant():
    d = _call(grep_for_deps_present=False)
    assert d.verdict is AdgFirstVerdict.COMPLIANT
    assert not d.is_blocking


def test_bypass_returns_info_not_blocking():
    d = _call(grep_for_deps_present=True, bypass_set=True, adg_snapshot_present=True)
    assert d.verdict is AdgFirstVerdict.INFO_BYPASS
    assert d.severity == "info"
    assert not d.is_blocking


def test_sqlite_direct_used_is_compliant():
    d = _call(grep_for_deps_present=True, sqlite_direct_used=True)
    assert d.verdict is AdgFirstVerdict.COMPLIANT
    assert not d.is_blocking


def test_mcp_used_is_warning_not_blocking():
    d = _call(grep_for_deps_present=True, adg_mcp_used=True)
    assert d.verdict is AdgFirstVerdict.WARNING
    assert d.severity == "warning"
    assert not d.is_blocking


def test_snapshot_reachable_grep_is_critical_blocking():
    """Constitutional §28: SQLite reachable but grep used → block."""
    d = _call(grep_for_deps_present=True, adg_snapshot_present=True)
    assert d.verdict is AdgFirstVerdict.CRITICAL_SKIP_SQLITE
    assert d.severity == "critical"
    assert d.is_blocking


def test_legacy_protocol_compliant():
    d = _call(
        grep_for_deps_present=True,
        adg_health_checked=True,
        degraded_fallback_declared=True,
    )
    assert d.verdict is AdgFirstVerdict.COMPLIANT
    assert not d.is_blocking


def test_partial_compliance_is_error():
    d = _call(grep_for_deps_present=True, adg_health_checked=True)
    assert d.verdict is AdgFirstVerdict.ERROR
    assert not d.is_blocking


def test_silent_fallback_is_critical_blocking():
    """No MCP, no snapshot, no health check, no reason code → silent fallback → block."""
    d = _call(grep_for_deps_present=True)
    assert d.verdict is AdgFirstVerdict.CRITICAL_SILENT
    assert d.severity == "critical"
    assert d.is_blocking


def test_decision_is_frozen():
    """AdgFirstDecision is a frozen dataclass — cannot mutate."""
    import dataclasses

    d = _call(grep_for_deps_present=False)
    assert dataclasses.is_dataclass(d)
    with __import__("pytest").raises(dataclasses.FrozenInstanceError):
        d.severity = "modified"  # type: ignore[misc]
