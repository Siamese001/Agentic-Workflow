"""L5 Governance v4 — Replay Envelope Writer + Forensic Reconstruction Verifier.

Produces ``ReplayEnvelope`` artifacts after CERTIFY (G-18). Each envelope
captures everything an independent verifier needs to forensically
reconstruct the run.

Reference
---------
``docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md`` G-18.

KPI surface
-----------
``REPLAY_ENVELOPE_RECONSTRUCTION_SUCCESS_RATE`` — ratio of envelopes
that pass the deterministic reconstruction check.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Mapping

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReplayEnvelope:
    """Schema-versioned forensic envelope."""

    envelope_id: str
    schema_version: str
    trace_id: str
    run_id: str
    policy_hash: str
    prompt_hash: str
    context_hash: str
    capability_token_id: str
    sandbox_envelope_id: str
    standards_fingerprint: str
    canonical_payload_hash: str
    issued_at_epoch: float


def _stable_hash(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ReplayEnvelopeWriter:
    """Construct ``ReplayEnvelope`` artifacts."""

    SCHEMA_VERSION = "1.0"

    def write(
        self,
        *,
        trace_id: str,
        run_id: str,
        policy_hash: str,
        prompt_hash: str,
        context_hash: str,
        capability_token_id: str,
        sandbox_envelope_id: str,
        standards_fingerprint: str,
        canonical_payload: Mapping[str, Any],
        issued_at_epoch: float | None = None,
    ) -> ReplayEnvelope:
        ts = issued_at_epoch if issued_at_epoch is not None else time.time()
        canonical_hash = _stable_hash(canonical_payload)
        envelope_id_payload = {
            "schema_version": self.SCHEMA_VERSION,
            "trace_id": trace_id,
            "run_id": run_id,
            "policy_hash": policy_hash,
            "prompt_hash": prompt_hash,
            "context_hash": context_hash,
            "capability_token_id": capability_token_id,
            "sandbox_envelope_id": sandbox_envelope_id,
            "standards_fingerprint": standards_fingerprint,
            "canonical_payload_hash": canonical_hash,
        }
        envelope_id = _stable_hash(envelope_id_payload)
        return ReplayEnvelope(
            envelope_id=envelope_id,
            schema_version=self.SCHEMA_VERSION,
            trace_id=trace_id,
            run_id=run_id,
            policy_hash=policy_hash,
            prompt_hash=prompt_hash,
            context_hash=context_hash,
            capability_token_id=capability_token_id,
            sandbox_envelope_id=sandbox_envelope_id,
            standards_fingerprint=standards_fingerprint,
            canonical_payload_hash=canonical_hash,
            issued_at_epoch=ts,
        )


class ForensicReplayVerifier:
    """Verify a stored envelope can be deterministically reconstructed.

    Reconstruction success means: re-hashing the canonical payload yields
    the stored ``canonical_payload_hash``, and the envelope's
    ``envelope_id`` matches the deterministic recomputation.
    """

    def __init__(self) -> None:
        self._success: int = 0
        self._total: int = 0

    def verify(
        self,
        envelope: ReplayEnvelope,
        canonical_payload: Mapping[str, Any],
    ) -> tuple[bool, str]:
        self._total += 1
        recomputed_hash = _stable_hash(canonical_payload)
        if recomputed_hash != envelope.canonical_payload_hash:
            return False, "canonical payload hash mismatch"
        envelope_id_payload = {
            "schema_version": envelope.schema_version,
            "trace_id": envelope.trace_id,
            "run_id": envelope.run_id,
            "policy_hash": envelope.policy_hash,
            "prompt_hash": envelope.prompt_hash,
            "context_hash": envelope.context_hash,
            "capability_token_id": envelope.capability_token_id,
            "sandbox_envelope_id": envelope.sandbox_envelope_id,
            "standards_fingerprint": envelope.standards_fingerprint,
            "canonical_payload_hash": envelope.canonical_payload_hash,
        }
        if _stable_hash(envelope_id_payload) != envelope.envelope_id:
            return False, "envelope id mismatch"
        self._success += 1
        return True, "reconstructed"

    @property
    def counters(self) -> tuple[int, int]:
        return (self._success, self._total)

    def reset(self) -> None:
        self._success = 0
        self._total = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            from agentic_core.L6_system_learning.engines.v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )

            ratio = (
                self._success / self._total if self._total > 0 else 0.0
            )
            board.record(V7KPISample(
                name=V7KPIName.REPLAY_ENVELOPE_RECONSTRUCTION_SUCCESS_RATE,
                value=ratio,
                timestamp=time.time(),
                source="forensic_replay_verifier",
                metadata={"success": self._success, "total": self._total},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break verification
            logger.warning(
                "v7_kpi_replay_envelope_reconstruction_failed: %s", exc
            )


__all__ = [
    "ReplayEnvelope",
    "ReplayEnvelopeWriter",
    "ForensicReplayVerifier",
]
