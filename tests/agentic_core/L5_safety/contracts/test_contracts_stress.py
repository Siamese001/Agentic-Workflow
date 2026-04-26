"""Stress + resilience tests for the L5 contracts package.

Covers:
- mass instantiation of every contract,
- hashability + equality semantics for frozen dataclasses,
- ``dataclasses.asdict`` round-trip on a representative sample,
- thread-concurrent registry lookup (no shared mutable state).
"""

from __future__ import annotations

import concurrent.futures
import dataclasses
import threading

from agentic_core.L5_safety.contracts import (
    CONTRACT_REGISTRY,
    L5OutputBase,
    get_contract,
)

COMMON = dict(
    run_id="stress",
    trace_id="stress",
    emitted_at_utc="2026-04-26T00:00:00Z",
    digest_sha256="0" * 64,
)


def test_every_contract_is_hashable_and_equal() -> None:
    seen: set[L5OutputBase] = set()
    for cls in CONTRACT_REGISTRY.values():
        a = cls(**COMMON)
        b = cls(**COMMON)
        assert a == b
        assert hash(a) == hash(b)
        seen.add(a)
    # Every distinct dataclass type should map to its own hash bucket.
    assert len(seen) >= len(set(CONTRACT_REGISTRY.values()))


def test_concurrent_registry_lookup_is_threadsafe() -> None:
    names = list(CONTRACT_REGISTRY.keys())
    barrier = threading.Barrier(8)

    def worker(slice_start: int) -> int:
        barrier.wait()
        count = 0
        for name in names[slice_start::8]:
            cls = get_contract(name)
            inst = cls(**COMMON)
            assert isinstance(inst, L5OutputBase)
            count += 1
        return count

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        totals = list(pool.map(worker, range(8)))
    assert sum(totals) == len(names)


def test_asdict_roundtrip_on_representative_classes() -> None:
    sample_names = [
        "L5CertificationResult",
        "L5CertificationPacket",
        "OriginTrustManifest",
        "HITLFreezePacket",
        "ModelEgressReceipt",
        "StaticGovernanceReviewPacket",
        "agent_registry_validation_report",
        "classification_report",
    ]
    for name in sample_names:
        cls = get_contract(name)
        inst = cls(**COMMON)
        d = dataclasses.asdict(inst)
        assert d["run_id"] == "stress"
        assert d["digest_sha256"] == "0" * 64
