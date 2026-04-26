"""Smoke + stress tests for ``agentic_core.L5_safety.contracts``.

Validates that:
- every entry in ``CONTRACT_REGISTRY`` is constructible with the common
  envelope fields,
- every contract is a frozen dataclass (mutation raises),
- every contract advertises a non-empty ``output_name``, ``source_doc``,
  and ``output_kind``,
- no contract class name overlaps with the L5-forbidden runtime
  disposition vocabulary.
"""

from __future__ import annotations

import dataclasses
from typing import Any

import pytest

from agentic_core.L5_safety.contracts import (
    ALL_OUTPUT_NAMES,
    CONTRACT_REGISTRY,
    FORBIDDEN_RUNTIME_DISPOSITIONS,
    L5CertificationStatus,
    L5OutputBase,
    L5ReasonCode,
    get_contract,
)

EXPECTED_CONTRACT_COUNT = 838  # 819 prior + 19 from 00A.8 runtime_binding doctrine
COMMON_KWARGS: dict[str, Any] = {
    "run_id": "smoke-run",
    "trace_id": "smoke-trace",
    "emitted_at_utc": "2026-04-26T00:00:00Z",
    "digest_sha256": "0" * 64,
}


def test_registry_is_complete() -> None:
    assert len(CONTRACT_REGISTRY) == EXPECTED_CONTRACT_COUNT
    assert ALL_OUTPUT_NAMES == frozenset(CONTRACT_REGISTRY.keys())


@pytest.mark.parametrize("name", sorted(CONTRACT_REGISTRY.keys()))
def test_every_contract_constructs_and_is_frozen(name: str) -> None:
    cls = get_contract(name)
    assert issubclass(cls, L5OutputBase)
    assert dataclasses.is_dataclass(cls)

    inst = cls(**COMMON_KWARGS)
    # ClassVars surface canonical doctrine identity. A class may carry
    # multiple doctrine names (e.g., ``ModelEgressReceipt`` /
    # ``model_egress_receipt``) — the registry indexes them all.
    assert name in cls.output_names, (name, cls.output_names)
    assert cls.output_name in cls.output_names
    assert cls.source_doc.startswith("00")
    assert cls.output_kind in {
        "packet",
        "receipt",
        "report",
        "manifest",
        "log",
        "diff",
        "envelope",
        "result",
        "map",
        "status",
        "ref",
        "context",
        "token",
        "output",
    }

    # Frozen: mutation must raise.
    with pytest.raises(dataclasses.FrozenInstanceError):
        inst.run_id = "tamper"  # type: ignore[misc]


def test_no_class_name_collides_with_forbidden_dispositions() -> None:
    bad = []
    for name, cls in CONTRACT_REGISTRY.items():
        if cls.__name__ in FORBIDDEN_RUNTIME_DISPOSITIONS:
            bad.append((name, cls.__name__))
        if name in FORBIDDEN_RUNTIME_DISPOSITIONS:
            bad.append((name, cls.__name__))
    assert bad == [], f"L5 contracts must not name themselves with runtime dispositions: {bad}"


def test_certification_status_round_trip() -> None:
    cls = get_contract("L5CertificationResult")
    inst = cls(
        **COMMON_KWARGS,
        certification_status=L5CertificationStatus.L5_CERTIFIED.value,
        reason_codes=(L5ReasonCode.DRIFT_EVIDENCE.value,),
        evidence_refs=("authority_context_evidence_ref",),
    )
    assert inst.certification_status == "L5_CERTIFIED"
    assert inst.reason_codes == ("drift_evidence",)
    assert inst.is_evidence_only() is True


def test_module_distribution_matches_doc_count() -> None:
    """All 8 doctrine docs are represented; counts sum to the registry size."""
    by_doc: dict[str, int] = {}
    for cls in CONTRACT_REGISTRY.values():
        by_doc[cls.source_doc] = by_doc.get(cls.source_doc, 0) + 1
    assert sum(by_doc.values()) == EXPECTED_CONTRACT_COUNT
    assert len(by_doc) == 9  # 00A.1–0A.7 + 00A umbrella + 00A.8 runtime_binding
