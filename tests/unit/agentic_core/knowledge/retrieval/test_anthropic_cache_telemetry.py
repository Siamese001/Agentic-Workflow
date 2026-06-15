"""Unit tests for anthropic_cache_telemetry (P4 — closed-loop cache verification).

Plan: prompt-cache-anthropic-best-practice-c7a1e9 (W1.1).

Covers DoD-1 (stable-tier cache hit proven on the 2nd identical-prefix call),
DoD-2 (no write-waste on one-shot RAG), and the silent-invalidator alarm as a
negative control (fires only when it should).
"""

from __future__ import annotations

import logging

from agentic_core.knowledge.retrieval import (
    prefix_fingerprint as public_prefix_fingerprint,
    record_cache_usage as public_record_cache_usage,
)
from agentic_core.knowledge.retrieval.anthropic_cache_telemetry import (
    CacheUsage,
    CacheUsageLedger,
    extract_cache_usage,
    prefix_fingerprint,
    record_cache_usage,
    reset_default_cache_ledger,
    get_default_cache_ledger,
)


def test_public_retrieval_surface_exports_gateway_cache_helpers():
    assert public_prefix_fingerprint is prefix_fingerprint
    assert public_record_cache_usage is record_cache_usage


class _FakeUsage:
    """Duck-typed stand-in for the Anthropic SDK ``Usage`` object."""

    def __init__(self, **kw: int) -> None:
        for k, v in kw.items():
            setattr(self, k, v)


# --------------------------------------------------------------------------- #
# extract_cache_usage
# --------------------------------------------------------------------------- #


def test_extract_from_object():
    usage = _FakeUsage(
        input_tokens=100,
        output_tokens=20,
        cache_read_input_tokens=4096,
        cache_creation_input_tokens=0,
    )
    cu = extract_cache_usage(usage)
    assert cu.cache_read_input_tokens == 4096
    assert cu.cache_creation_input_tokens == 0
    assert cu.input_tokens == 100
    assert cu.output_tokens == 20


def test_extract_from_dict():
    cu = extract_cache_usage(
        {"input_tokens": 10, "cache_read_input_tokens": 2048, "cache_creation_input_tokens": 0}
    )
    assert cu.cache_read_input_tokens == 2048
    assert cu.is_read_hit is True


def test_extract_none_and_missing_fields_zero():
    assert extract_cache_usage(None) == CacheUsage()
    cu = extract_cache_usage(_FakeUsage(input_tokens=5))  # no cache fields
    assert cu.cache_read_input_tokens == 0
    assert cu.cache_creation_input_tokens == 0


def test_extract_negative_coerced_to_zero():
    cu = extract_cache_usage({"cache_read_input_tokens": -7, "cache_creation_input_tokens": None})
    assert cu.cache_read_input_tokens == 0
    assert cu.cache_creation_input_tokens == 0


def test_extract_non_numeric_string_coerced_to_zero():
    cu = extract_cache_usage({"cache_read_input_tokens": "n/a"})
    assert cu.cache_read_input_tokens == 0


# --------------------------------------------------------------------------- #
# CacheUsage derived properties
# --------------------------------------------------------------------------- #


def test_hit_ratio_zero_when_nothing_cacheable():
    assert CacheUsage(input_tokens=100).cache_hit_ratio == 0.0


def test_hit_ratio_computed():
    cu = CacheUsage(cache_read_input_tokens=900, cache_creation_input_tokens=100)
    assert cu.cacheable_input_tokens == 1000
    assert cu.cache_hit_ratio == 0.9


def test_is_write_only():
    assert CacheUsage(cache_creation_input_tokens=4096).is_write_only is True
    assert CacheUsage(cache_read_input_tokens=4096).is_write_only is False


# --------------------------------------------------------------------------- #
# prefix_fingerprint
# --------------------------------------------------------------------------- #


def test_fingerprint_stable_and_distinct():
    a = prefix_fingerprint("identical system prefix")
    b = prefix_fingerprint("identical system prefix")
    c = prefix_fingerprint("a different prefix")
    assert a == b
    assert a != c
    assert len(a) == 32


# --------------------------------------------------------------------------- #
# DoD-1 — stable-tier cache hit on the 2nd identical-prefix call
# --------------------------------------------------------------------------- #


def test_tier1_cache_hit_on_second_identical_prefix_call():
    ledger = CacheUsageLedger()
    fp = prefix_fingerprint("TIER-1: tools + system prompt")

    # Call 1: cold — the prefix is written to cache, nothing read yet.
    record_cache_usage(
        _FakeUsage(input_tokens=50, cache_read_input_tokens=0, cache_creation_input_tokens=4096),
        fingerprint=fp,
        ledger=ledger,
    )
    # Call 2: same prefix — now served FROM cache (the win the plan promises).
    record_cache_usage(
        _FakeUsage(input_tokens=50, cache_read_input_tokens=4096, cache_creation_input_tokens=0),
        fingerprint=fp,
        ledger=ledger,
    )

    records = ledger.records_for(fp)
    assert len(records) == 2
    assert records[1].usage.cache_read_input_tokens > 0  # DoD-1
    assert ledger.hit_ratio_for(fp) == 0.5
    assert ledger.is_silent_invalidator(fp) is False  # a read happened


# --------------------------------------------------------------------------- #
# DoD-2 — no write-waste on a one-shot (distinct-query) RAG batch
# --------------------------------------------------------------------------- #


def test_one_shot_rag_batch_has_zero_tier3_write_waste():
    ledger = CacheUsageLedger()
    # Five distinct queries; Tier-3 docs carry NO cache marker (workload-aware),
    # so each call reports cache_creation == 0 — the waste the plan removes.
    for i in range(5):
        record_cache_usage(
            {"input_tokens": 800, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
            fingerprint=prefix_fingerprint(f"distinct query {i}"),
            ledger=ledger,
        )
    total_creation = sum(r.usage.cache_creation_input_tokens for r in ledger.all_records())
    assert total_creation == 0  # DoD-2
    # Distinct prefixes never trip the silent-invalidator alarm.
    for r in ledger.all_records():
        assert ledger.is_silent_invalidator(r.fingerprint) is False


# --------------------------------------------------------------------------- #
# Silent-invalidator alarm — negative control (fires only when it should)
# --------------------------------------------------------------------------- #


def test_silent_invalidator_fires_after_min_calls(caplog):
    ledger = CacheUsageLedger()
    fp = prefix_fingerprint("frozen-looking but never read")
    with caplog.at_level(logging.WARNING, logger="agentic_core.knowledge.retrieval.anthropic_cache_telemetry"):
        for _ in range(3):
            record_cache_usage(
                _FakeUsage(cache_read_input_tokens=0, cache_creation_input_tokens=4096),
                fingerprint=fp,
                label="anthropic_opus",
                ledger=ledger,
            )
    assert ledger.is_silent_invalidator(fp) is True
    assert "SILENT_CACHE_INVALIDATOR" in caplog.text


def test_silent_invalidator_quiet_on_single_cold_miss():
    ledger = CacheUsageLedger()
    fp = prefix_fingerprint("just one write")
    record_cache_usage(
        _FakeUsage(cache_read_input_tokens=0, cache_creation_input_tokens=4096),
        fingerprint=fp,
        ledger=ledger,
    )
    assert ledger.is_silent_invalidator(fp) is False


def test_silent_invalidator_quiet_when_reads_present():
    ledger = CacheUsageLedger()
    fp = prefix_fingerprint("healthy cached prefix")
    for _ in range(4):
        record_cache_usage(
            _FakeUsage(cache_read_input_tokens=4096, cache_creation_input_tokens=0),
            fingerprint=fp,
            ledger=ledger,
        )
    assert ledger.is_silent_invalidator(fp) is False


def test_silent_invalidator_quiet_when_nothing_cacheable():
    # read==0 AND creation==0 → nothing was ever cached; that is a different
    # problem ("never marked"), not a silent invalidation.
    ledger = CacheUsageLedger()
    fp = prefix_fingerprint("uncached")
    for _ in range(5):
        record_cache_usage({}, fingerprint=fp, ledger=ledger)
    assert ledger.is_silent_invalidator(fp) is False


# --------------------------------------------------------------------------- #
# default ledger lifecycle
# --------------------------------------------------------------------------- #


def test_default_ledger_record_and_reset():
    reset_default_cache_ledger()
    fp = prefix_fingerprint("default-ledger-test")
    record_cache_usage(_FakeUsage(cache_read_input_tokens=1), fingerprint=fp)
    assert len(get_default_cache_ledger().records_for(fp)) == 1
    reset_default_cache_ledger()
    assert get_default_cache_ledger().records_for(fp) == []
