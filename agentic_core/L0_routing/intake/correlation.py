"""
01.5 — Trace / Replay / Correlation binding.

Public entrypoint: `bind_trace_and_replay`.

Builds:
- RequestCorrelationReceipt
- IngressReplaySeed
- NormalizedRequestHash
- IntakeManifestHash

INVARIANTS:
- replay_key_seed is NOT the L0 RouteContract replay_key.
- intake_manifest_hash MUST be deterministic across replays of the same
  logical input. Volatile fields (observed_at, random ids) are excluded.
- This stage NEVER emits route_digest, prompt_hash, or evidence_contract_hash.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

from agentic_core.L0_routing.intake.origin_labels import IngressOriginLabelManifest
from agentic_core.L0_routing.intake.receipts import (
    CallerScopeBaseline,
    IngressReplaySeed,
    IntakeManifestHash,
    NormalizedRequestHash,
    QuotaReceipt,
    RequestCorrelationReceipt,
    RequestSchemaValidationReceipt,
    TransportEnvelopeReceipt,
)


@dataclass(frozen=True)
class TraceReplayBindingResult:
    """Bundle returned by 01.5."""

    correlation_receipt: RequestCorrelationReceipt
    ingress_replay_seed: IngressReplaySeed
    normalized_request_hash: NormalizedRequestHash
    intake_manifest_hash: IntakeManifestHash


def bind_trace_and_replay(
    *,
    request_id: str,
    session_id: str,
    trace_root: str,
    raw_envelope_id: str,
    normalized_payload_id: Optional[str],
    transport_receipt: TransportEnvelopeReceipt,
    caller_scope_baseline: CallerScopeBaseline,
    quota_receipt: QuotaReceipt,
    schema_validation_receipt: RequestSchemaValidationReceipt,
    origin_label_manifest: IngressOriginLabelManifest,
    raw_payload_hash: str,
    normalized_payload_hash: str,
    schema_version: str,
    transport: str,
    intake_policy_ref: str = "policy:intake:default:v1",
    parent_trace_ref: Optional[str] = None,
    correlation_source: str = "intake_assigned",
    provisional_span_refs: tuple[str, ...] = (),
    entry_policy_refs: tuple[str, ...] = ("policy:intake:default:v1",),
) -> TraceReplayBindingResult:
    """Bind correlation, replay seed, and manifest hash for an Intake run.

    All hashes are deterministic over stable fields. Random IDs are used
    only for `receipt_id` / `replay_seed_id` / `manifest_hash_id` (the
    *envelope* identifiers), never inside the hash inputs.
    """
    tenant_id = caller_scope_baseline.tenant_id
    principal_id_hash = None  # explicit None — principal hash lives elsewhere

    correlation = RequestCorrelationReceipt(
        receipt_id=f"corr:{uuid.uuid4().hex}",
        request_id=request_id,
        session_id=session_id,
        trace_root=trace_root,
        tenant_id=tenant_id,
        principal_id_hash=principal_id_hash,
        raw_envelope_id=raw_envelope_id,
        normalized_payload_id=normalized_payload_id,
        correlation_source=correlation_source,
        parent_trace_ref=parent_trace_ref,
        provisional_span_refs=provisional_span_refs,
    ).with_hash()

    # Replay seed — exclude wall-clock; key is logical scope + payload identity.
    replay_seed_value = (
        f"{session_id}|{tenant_id or '-'}|{transport}|{raw_payload_hash}|"
        f"{normalized_payload_hash}|{schema_version}|{intake_policy_ref}"
    )
    replay_seed = IngressReplaySeed(
        replay_seed_id=f"seed:{uuid.uuid4().hex}",
        request_id=request_id,
        session_id=session_id,
        tenant_id=tenant_id,
        principal_id_hash=principal_id_hash,
        transport=transport,
        raw_payload_hash=raw_payload_hash,
        normalized_payload_hash=normalized_payload_hash,
        schema_version=schema_version,
        intake_policy_ref=intake_policy_ref,
        replay_key_seed=replay_seed_value,
    ).with_hash()

    normalized_request_hash = NormalizedRequestHash(
        hash_id=f"nrh:{uuid.uuid4().hex}",
        normalized_payload_hash=normalized_payload_hash,
        caller_scope_baseline_hash=caller_scope_baseline.baseline_hash,
        schema_version=schema_version,
        origin_label_manifest_hash=origin_label_manifest.manifest_hash,
        entry_policy_refs=entry_policy_refs,
    ).with_hash()

    manifest_hash = IntakeManifestHash(
        manifest_hash_id=f"mh:{uuid.uuid4().hex}",
        transport_receipt_hash=transport_receipt.deterministic_receipt_hash,
        caller_scope_baseline_hash=caller_scope_baseline.baseline_hash,
        quota_receipt_hash=quota_receipt.deterministic_receipt_hash,
        schema_validation_receipt_hash=schema_validation_receipt.deterministic_receipt_hash,
        origin_label_manifest_hash=origin_label_manifest.manifest_hash,
        normalized_request_hash=normalized_request_hash.normalized_request_hash,
        replay_seed_hash=replay_seed.replay_seed_hash,
    ).with_hash()

    return TraceReplayBindingResult(
        correlation_receipt=correlation,
        ingress_replay_seed=replay_seed,
        normalized_request_hash=normalized_request_hash,
        intake_manifest_hash=manifest_hash,
    )


__all__ = [
    "TraceReplayBindingResult",
    "bind_trace_and_replay",
]
