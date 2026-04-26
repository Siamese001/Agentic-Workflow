"""Base dataclasses for L5 doctrine output contracts.

Every named L5 output (packet / receipt / report / manifest / log / diff /
envelope / result / map / status / ref / context / token) defined in the
8 doctrine documents under ``docs/reference/00_L5_Policy_Plane`` is
implemented as a frozen dataclass that inherits from one of the bases
below.

L5 doctrine forbids these contracts from carrying runtime dispositions
(ALLOW / DENY / REROUTE / etc.). They carry **evidence** only. Downstream
consumers (Runtime Gates, Exit Eval, UWG, L6) decide live outcomes.

Generated and re-runnable. Do not hand-edit individual contract modules
(parent.py, enforcement.py, ..., static.py) — re-run
``python tools/l5_contracts/generate_contracts.py`` instead.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Mapping

# Empty mapping default — produced fresh per instance via default_factory.
# ``dict`` is mutable, but doctrine treats payload contents as
# read-after-emission. Callers must not mutate after construction.


@dataclass(frozen=True, slots=True)
class L5OutputBase:
    """Doctrine-level common envelope for every L5 output.

    Carries evidence only — never runtime disposition.
    """

    run_id: str = ""
    trace_id: str = ""
    emitted_at_utc: str = ""
    digest_sha256: str = ""

    output_name: ClassVar[str] = ""
    source_doc: ClassVar[str] = ""
    output_kind: ClassVar[str] = "output"

    def is_evidence_only(self) -> bool:
        """L5 contracts are evidence-only by doctrine."""
        return True


@dataclass(frozen=True, slots=True)
class L5Packet(L5OutputBase):
    """Bundle of evidence fields for a single L5 concern."""

    payload: Mapping[str, Any] = field(default_factory=dict, hash=False)
    output_kind: ClassVar[str] = "packet"


@dataclass(frozen=True, slots=True)
class L5Receipt(L5OutputBase):
    """Confirmation that an L5 step executed and produced bound evidence."""

    receipt_status: str = ""
    evidence_refs: tuple[str, ...] = ()
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class L5Report(L5OutputBase):
    """Findings from an L5 scan or evaluation. Severity-graded."""

    severity: str = "info"
    findings: tuple[Mapping[str, Any], ...] = ()
    output_kind: ClassVar[str] = "report"


@dataclass(frozen=True, slots=True)
class L5Manifest(L5OutputBase):
    """Enumerated set of items bound under one L5 evidence header."""

    entries: tuple[Mapping[str, Any], ...] = ()
    output_kind: ClassVar[str] = "manifest"


@dataclass(frozen=True, slots=True)
class L5Log(L5OutputBase):
    """Hash-chained sequence of L5 events. ``prev_hash`` chains entries."""

    prev_hash: str = ""
    entries: tuple[Mapping[str, Any], ...] = ()
    output_kind: ClassVar[str] = "log"


@dataclass(frozen=True, slots=True)
class L5Diff(L5OutputBase):
    """Before/after delta evidence between two L5 snapshots or artifacts."""

    before_ref: str = ""
    after_ref: str = ""
    diff_entries: tuple[Mapping[str, Any], ...] = ()
    output_kind: ClassVar[str] = "diff"


@dataclass(frozen=True, slots=True)
class L5Envelope(L5OutputBase):
    """Sealed wrapper around evidence contents with a hash seal."""

    contents_ref: str = ""
    seal_hash: str = ""
    output_kind: ClassVar[str] = "envelope"


@dataclass(frozen=True, slots=True)
class L5Result(L5OutputBase):
    """L5 certification outcome. Status + reason_codes + evidence_refs."""

    certification_status: str = ""
    reason_codes: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    output_kind: ClassVar[str] = "result"


@dataclass(frozen=True, slots=True)
class L5Map(L5OutputBase):
    """Key→value evidence index (e.g., affected consumer surfaces)."""

    entries: Mapping[str, Any] = field(default_factory=dict, hash=False)
    output_kind: ClassVar[str] = "map"


@dataclass(frozen=True, slots=True)
class L5Status(L5OutputBase):
    """Single-state evidence marker (e.g., readiness status)."""

    status_value: str = ""
    output_kind: ClassVar[str] = "status"


@dataclass(frozen=True, slots=True)
class L5Ref(L5OutputBase):
    """Pointer-style reference to externally stored evidence."""

    ref_uri: str = ""
    ref_kind: str = ""
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class L5Context(L5OutputBase):
    """Bound governance context object (e.g., GovernedValidationContext)."""

    payload: Mapping[str, Any] = field(default_factory=dict, hash=False)
    output_kind: ClassVar[str] = "context"


@dataclass(frozen=True, slots=True)
class L5Token(L5OutputBase):
    """Capability-style scoped token evidence (issuance shape only)."""

    token_value: str = ""
    scope: tuple[str, ...] = ()
    expires_at_utc: str = ""
    output_kind: ClassVar[str] = "token"


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
]
