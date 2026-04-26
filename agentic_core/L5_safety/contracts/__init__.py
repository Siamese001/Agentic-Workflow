"""L5 doctrine output contracts.

Every named output across the 8 ``docs/reference/00_L5_Policy_Plane``
docs is a frozen dataclass here. Use ``CONTRACT_REGISTRY`` to lookup
a contract by its canonical doctrine name.

Constitutional discipline: contracts are evidence-only. They never
encode runtime dispositions (ALLOW/DENY/REROUTE/etc.).

Sub-modules:

* ``_base`` — kind hierarchy (``L5Packet``, ``L5Receipt``, etc.)
* ``_vocab`` — controlled vocabularies (statuses, reason codes)
* ``parent`` — outputs from ``00_L5_Governance_Safety_detailed.md``
* ``enforcement`` — outputs from ``00.1`` Safety Enforcement Plane
* ``authority`` — outputs from ``00.2`` Authority Context & Registry
* ``origin`` — outputs from ``00.3`` Origin Trust & Content Boundary
* ``hitl`` — outputs from ``00.4`` HITL Reclearance
* ``egress`` — outputs from ``00.5`` Egress & Provider Governance
* ``replay`` — outputs from ``00.6`` Replay/Audit/Certification Evidence
* ``static`` — outputs from ``00.7`` Static Governance & Structure Drift
* ``registry`` — name lookup table
"""
from __future__ import annotations

from ._base import (
    L5OutputBase,
    L5Packet,
    L5Receipt,
    L5Report,
    L5Manifest,
    L5Log,
    L5Diff,
    L5Envelope,
    L5Result,
    L5Map,
    L5Status,
    L5Ref,
    L5Context,
    L5Token,
)
from ._vocab import (
    L5CertificationStatus,
    L5ReasonCode,
    L5EvidenceRefKind,
    FORBIDDEN_RUNTIME_DISPOSITIONS,
)
from .registry import (
    CONTRACT_REGISTRY,
    ALL_OUTPUT_NAMES,
    get_contract,
)
from ._status_enums import STATUS_ENUM_REGISTRY

__all__ = [
    "L5OutputBase",
    "L5Packet",
    "L5Receipt",
    "L5Report",
    "L5Manifest",
    "L5Log",
    "L5Diff",
    "L5Envelope",
    "L5Result",
    "L5Map",
    "L5Status",
    "L5Ref",
    "L5Context",
    "L5Token",
    "L5CertificationStatus",
    "L5ReasonCode",
    "L5EvidenceRefKind",
    "FORBIDDEN_RUNTIME_DISPOSITIONS",
    "CONTRACT_REGISTRY",
    "ALL_OUTPUT_NAMES",
    "get_contract",
    "STATUS_ENUM_REGISTRY",
]
