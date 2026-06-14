"""Unit tests for anthropic_cache_determinism (P5 — Tier-1 determinism guard).

Plan: prompt-cache-anthropic-best-practice-c7a1e9 (W1.2).

Covers DoD-4: the determinism guard stays quiet for a frozen prefix and FIRES
when a non-deterministic value (e.g. an injected ``datetime.now()``) leaks into
the cacheable Tier-1 block.
"""

from __future__ import annotations

import logging

from agentic_core.knowledge.retrieval.anthropic_cache_determinism import (
    DeterminismGuard,
    find_nondeterministic_tokens,
    get_default_determinism_guard,
    reset_default_determinism_guard,
)

_FROZEN_TIER1 = (
    "You are a precise assistant. Quote sources before answering.\n"
    "<tools>search, fetch</tools>"
)


# --------------------------------------------------------------------------- #
# DoD-4 positive — frozen prefix stays quiet
# --------------------------------------------------------------------------- #


def test_guard_stable_for_identical_prefix(caplog):
    guard = DeterminismGuard()
    with caplog.at_level(logging.WARNING, logger="agentic_core.knowledge.retrieval.anthropic_cache_determinism"):
        assert guard.check("apps_rg:exec_summary", _FROZEN_TIER1) is True
        assert guard.check("apps_rg:exec_summary", _FROZEN_TIER1) is True
        assert guard.check("apps_rg:exec_summary", _FROZEN_TIER1) is True
    assert "TIER1_PREFIX_DRIFT" not in caplog.text


# --------------------------------------------------------------------------- #
# DoD-4 negative — injected datetime.now() leak trips the alarm
# --------------------------------------------------------------------------- #


def test_guard_detects_datetime_leak(caplog):
    guard = DeterminismGuard()
    # Simulate a `datetime.now()` leak: the SAME logical input renders a prefix
    # whose only difference is a live timestamp.
    leaked_a = _FROZEN_TIER1 + "\nGenerated at: 2026-06-14T16:05:01"
    leaked_b = _FROZEN_TIER1 + "\nGenerated at: 2026-06-14T16:05:02"

    with caplog.at_level(logging.WARNING, logger="agentic_core.knowledge.retrieval.anthropic_cache_determinism"):
        assert guard.check("apps_rg:exec_summary", leaked_a) is True   # first sighting
        drifted = guard.check("apps_rg:exec_summary", leaked_b)        # same key, new hash

    assert drifted is False
    assert "TIER1_PREFIX_DRIFT" in caplog.text
    # the volatile token is named in the alarm for legibility
    assert "iso_timestamp" in caplog.text


def test_guard_independent_per_logical_key():
    guard = DeterminismGuard()
    assert guard.check("key_a", _FROZEN_TIER1) is True
    assert guard.check("key_b", _FROZEN_TIER1 + " variant") is True  # different key, no drift
    # key_a remains stable on its own prefix
    assert guard.check("key_a", _FROZEN_TIER1) is True


# --------------------------------------------------------------------------- #
# static volatile-token scanner
# --------------------------------------------------------------------------- #


def test_find_nondeterministic_tokens_clean_is_empty():
    assert find_nondeterministic_tokens(_FROZEN_TIER1) == []


def test_find_nondeterministic_tokens_detects_each_class():
    assert "iso_timestamp" in find_nondeterministic_tokens("at 2026-06-14T16:05:01 today")
    assert "uuid" in find_nondeterministic_tokens(
        "session 1b9c2f3a-0000-4aaa-bbbb-ccccddddeeee active"
    )
    assert "session_id" in find_nondeterministic_tokens("session_id=abc")
    assert "epoch_seconds" in find_nondeterministic_tokens("ts=1718380000 now")


def test_find_nondeterministic_tokens_empty_text():
    assert find_nondeterministic_tokens("") == []


# --------------------------------------------------------------------------- #
# default guard lifecycle
# --------------------------------------------------------------------------- #


def test_default_guard_reset():
    reset_default_determinism_guard()
    guard = get_default_determinism_guard()
    assert guard.check("k", _FROZEN_TIER1) is True
    assert guard.fingerprint_for("k") is not None
    reset_default_determinism_guard()
    assert get_default_determinism_guard().fingerprint_for("k") is None
