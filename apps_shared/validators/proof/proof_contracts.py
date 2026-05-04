"""Runtime evidence contracts for apps_* proof harness.

Defines :class:`AppRunEvidencePacket` and supporting record types. All hashes
are SHA-256 of a canonical JSON serialization (sorted keys, no whitespace) so
that a manually edited proof JSON will fail :func:`verify_packet_hash`.

This module is intentionally dependency-light — it only imports from the
standard library — so the proof harness can run before any apps_*
runtime is bootstrapped.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


PROOF_STATUS_PASS = "PASS"
PROOF_STATUS_FAIL = "FAIL"

CLASSIFICATION_SANDBOX_OUTPUT = "SANDBOX_OUTPUT"
CLASSIFICATION_UWG_DURABLE = "UWG_DURABLE"
CLASSIFICATION_PROOF_ARTIFACT = "PROOF_ARTIFACT"


def _utcnow_iso() -> str:
    """ISO-8601 UTC timestamp with ``Z`` suffix."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_json(obj: Any) -> str:
    """Deterministic JSON: sorted keys, no whitespace, default=str."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def sha256_of(obj: Any) -> str:
    """SHA-256 of canonical JSON of ``obj``."""
    return hashlib.sha256(_canonical_json(obj).encode("utf-8")).hexdigest()


def sha256_of_file(path: Path | str) -> str:
    """SHA-256 of the file at ``path``. Raises ``FileNotFoundError`` if absent."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"sha256_of_file: missing {p}")
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Span / contract / gate / artifact records
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SpanRecord:
    """Single OTEL-style span record carried by the proof harness.

    Frozen so callers cannot retroactively re-stamp timestamps or attrs.
    """

    trace_id: str
    span_id: str
    parent_span_id: str | None
    layer: str
    name: str
    started_at: str
    ended_at: str | None
    status: str
    request_id: str | None = None
    run_id: str | None = None
    app_id: str | None = None
    scenario_id: str | None = None
    route_id: str | None = None
    step_id: str | None = None
    gate_id: str | None = None
    policy_hash: str | None = None
    blueprint_hash: str | None = None
    replay_key: str | None = None
    contract_digest: str | None = None
    reason_codes: tuple[str, ...] = ()
    latency_ms: float | None = None
    artifact_refs: tuple[str, ...] = ()
    attrs: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class ContractRecord:
    """A runtime contract emitted during a span (e.g. RouteContract)."""

    contract_kind: str
    digest: str
    emitted_by_span_id: str
    payload_path: str
    schema_version: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class GateVerdictRecord:
    """A gate verdict emitted by Exit / L5 / capability / egress / HITL."""

    gate_id: str
    verdict: str  # ALLOW_FINISH | BLOCK | CAVEAT | ESCALATE | NOT_APPLICABLE
    emitted_by_span_id: str
    reason_codes: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class ArtifactRecord:
    """Sandbox or UWG-durable artifact emitted during a run."""

    artifact_id: str
    app_id: str
    run_id: str
    trace_id: str
    producing_span_id: str
    classification: str  # SANDBOX_OUTPUT | UWG_DURABLE | PROOF_ARTIFACT
    durable: bool
    path: str
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


# ---------------------------------------------------------------------------
# AppRunEvidencePacket
# ---------------------------------------------------------------------------


@dataclass
class AppRunEvidencePacket:
    """The single source of truth for whether an apps_* run is provably real.

    Fields mirror the prompt's "App Runtime Evidence Contract" section.
    The ``packet_hash`` field is computed by :meth:`finalize` and binds the
    entire packet content; tampering with the JSON on disk after writing
    will be detected by :func:`verify_packet_hash`.
    """

    # Process / environment identity
    app_id: str
    scenario_id: str
    command: str
    cwd: str
    process_id: int
    python_executable: str
    git_commit_or_snapshot_ref: str | None
    adg_snapshot_ref: str

    # Run identity
    request_id: str
    session_id: str
    run_id: str
    trace_root: str
    trace_id: str

    # Decision/policy/contract digests
    policy_hash: str | None = None
    blueprint_hash: str | None = None
    replay_key: str | None = None
    input_hash: str | None = None
    route_digest: str | None = None
    prompt_hash: str | None = None
    evidence_contract_hash: str | None = None
    sealed_artifact_hash: str | None = None

    # Boundary timestamps
    runtime_boundary_timestamp: str | None = None
    l6_start_timestamp: str | None = None

    # Disposition + outcome
    exit_disposition: str | None = None
    proof_status: str = PROOF_STATUS_FAIL
    fail_reasons: list[str] = field(default_factory=list)

    # Inventories (paths to JSON sidecar files, all relative to export root)
    artifact_inventory: list[str] = field(default_factory=list)
    contract_inventory: list[str] = field(default_factory=list)
    gate_verdict_inventory: list[str] = field(default_factory=list)
    span_inventory: list[str] = field(default_factory=list)

    # Cross-validator outputs
    span_tree_ref: str | None = None
    replay_report_ref: str | None = None
    adg_bypass_report_ref: str | None = None
    write_sovereignty_report_ref: str | None = None
    negative_control_report_ref: str | None = None

    # Bookkeeping
    created_at: str = field(default_factory=_utcnow_iso)
    packet_hash: str | None = None

    # ------------------------------------------------------------------ helpers
    def add_fail_reason(self, code: str, detail: str = "") -> None:
        msg = code if not detail else f"{code}: {detail}"
        if msg not in self.fail_reasons:
            self.fail_reasons.append(msg)
        self.proof_status = PROOF_STATUS_FAIL

    def mark_pass_if_clean(self) -> None:
        if not self.fail_reasons:
            self.proof_status = PROOF_STATUS_PASS

    def to_dict(self, *, include_hash: bool = True) -> dict[str, Any]:
        d = dataclasses.asdict(self)
        if not include_hash:
            d.pop("packet_hash", None)
        return d

    def finalize(self) -> str:
        """Compute and stamp ``packet_hash`` over the hash-free packet body.

        Returns the hash. Idempotent only if no other field was mutated
        between calls.
        """
        body = self.to_dict(include_hash=False)
        digest = sha256_of(body)
        self.packet_hash = digest
        return digest


def verify_packet_hash(packet_path: Path | str) -> tuple[bool, str]:
    """Recompute ``packet_hash`` from JSON on disk and compare.

    Returns ``(ok, message)``. ``ok=False`` means the JSON was edited after
    finalize() — exactly the manual-tampering case the negative controls test.
    """
    p = Path(packet_path)
    if not p.exists():
        return False, f"missing: {p}"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"invalid json: {exc}"
    # BUG-FIX (2026-04-26 audit pass 2 / #7): json.loads can return a list,
    # string, number, or null. data.pop("packet_hash", None) raises
    # AttributeError on non-dict types. Validate shape before popping.
    if not isinstance(data, dict):
        return False, f"packet root is not an object: got {type(data).__name__}"
    stored = data.pop("packet_hash", None)
    if stored is None:
        return False, "no packet_hash field"
    recomputed = sha256_of(data)
    if stored != recomputed:
        return False, f"hash mismatch: stored={stored} recomputed={recomputed}"
    return True, "ok"


def write_packet(packet: AppRunEvidencePacket, dest: Path | str) -> Path:
    """Finalize and write ``packet`` to ``dest`` as canonical JSON."""
    packet.finalize()
    p = Path(dest)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(packet.to_dict(), sort_keys=True, indent=2, default=str),
        encoding="utf-8",
    )
    return p


def write_records(records: Sequence[Any], dest: Path | str) -> str:
    """Write a list of dataclass records to ``dest`` as JSON, return content hash."""
    payload = [r.to_dict() if hasattr(r, "to_dict") else r for r in records]
    p = Path(dest)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(payload, sort_keys=True, indent=2, default=str),
        encoding="utf-8",
    )
    return sha256_of(payload)


__all__ = [
    "PROOF_STATUS_PASS",
    "PROOF_STATUS_FAIL",
    "CLASSIFICATION_SANDBOX_OUTPUT",
    "CLASSIFICATION_UWG_DURABLE",
    "CLASSIFICATION_PROOF_ARTIFACT",
    "SpanRecord",
    "ContractRecord",
    "GateVerdictRecord",
    "ArtifactRecord",
    "AppRunEvidencePacket",
    "sha256_of",
    "sha256_of_file",
    "verify_packet_hash",
    "write_packet",
    "write_records",
]
