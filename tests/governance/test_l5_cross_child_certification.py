"""GAP-010 / 00A.8a — cross-child L5 digest coherence (governance).

Proves ``L5PacketProducer`` binds every child certifier that carries an
``evidence_digest`` to the same canonical governance-context digest; digest
mismatch fails closed with ``L5DigestMismatchError``.
"""
from __future__ import annotations

import pytest

from agentic_core.L5_safety.certification.l5_packet_producer import L5PacketProducer
from agentic_core.L5_safety.contracts.l5_certification_contracts import (
    ChildCertifierReceipt,
)
from agentic_core.L5_safety.exceptions import L5DigestMismatchError

_PRODUCER = L5PacketProducer()

_COMMON_REFS = dict(
    certified_object_ref="urn:obj:cross-child:v1",
    policy_ref="urn:policy:cross-child:v1",
    blueprint_ref="urn:blueprint:cross-child:v1",
    registry_ref="urn:registry:cross-child:v1",
    authority_ref="urn:authority:cross-child:v1",
    replay_ref="urn:replay:cross-child:v1",
    audit_ref="urn:audit:cross-child:v1",
    static_ref="urn:static:cross-child:v1",
    runtime_ref="urn:runtime:cross-child:v1",
    producer_ref="l5_packet_producer:cross_child_test:v1",
    certifier_version="0.0.1",
)

_DOMAINS_REQUIRED = (
    "safety_enforcement",
    "authority_context_registry_binding",
    "origin_trust_content_boundary",
    "replay_audit_certification_evidence",
    "static_governance_structure_drift",
    "runtime_certification_binding",
)


def _child(domain: str, *, digest: str = "") -> ChildCertifierReceipt:
    return ChildCertifierReceipt(
        domain=domain,
        applicability="REQUIRED",
        certified=True,
        evidence_digest=digest,
    )


class TestCrossChildDigestCoherence:
    """00A.8a — all applicable children share the same evidence_digest (or all omit it)."""

    def test_all_children_empty_digest_certified(self) -> None:
        children = [_child(d, digest="") for d in _DOMAINS_REQUIRED]
        packet = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_CERTIFIED"
        assert all(r.evidence_digest == "" for r in packet.child_receipts)

    def test_single_non_empty_digest_mismatch_raises(self) -> None:
        """Any non-empty child digest must equal the computed governance-context digest."""

        tampered = [
            _child("safety_enforcement", digest="0" * 64),
            *[_child(d, digest="") for d in _DOMAINS_REQUIRED if d != "safety_enforcement"],
        ]
        with pytest.raises(L5DigestMismatchError, match="safety_enforcement"):
            _PRODUCER.produce_packet(
                child_receipts=tampered,
                egress_receipts=[],
                **_COMMON_REFS,
            )

    def test_mismatched_two_nonempty_child_digests_raises(self) -> None:
        gov = "a" * 64
        other = "b" * 64
        mixed = [
            _child("safety_enforcement", digest=gov),
            _child("authority_context_registry_binding", digest=other),
            *[
                _child(d, digest="")
                for d in _DOMAINS_REQUIRED
                if d
                not in (
                    "safety_enforcement",
                    "authority_context_registry_binding",
                )
            ],
        ]
        with pytest.raises(L5DigestMismatchError):
            _PRODUCER.produce_packet(
                child_receipts=mixed,
                egress_receipts=[],
                **_COMMON_REFS,
            )

    def test_l5_not_certified_missing_child_without_digest_failure(self) -> None:
        # Missing required category → L5_NOT_CERTIFIED (omit evidence_digest so
        # producer does not fail-closed on digest before coverage checks).
        partial = [_child(_DOMAINS_REQUIRED[0], digest="")]
        packet = _PRODUCER.produce_packet(
            child_receipts=partial,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_NOT_CERTIFIED"
        assert packet.reason_codes


class TestRequestEnvelopeReplayThreading:
    def test_apps_rg_parse_sets_replay_key_from_payload(self) -> None:
        from apps_rg.runtime.dispatch.apps_rg_dispatch import apps_rg_parse

        env = apps_rg_parse(
            {
                "target_company": "Acme",
                "target_role": "Engineer",
                "source_resume_text": "x",
                "job_description_text": "y",
                "replay_key": "rk-test-001",
            }
        )
        assert env.replay_key == "rk-test-001"

    def test_u0_prefers_envelope_replay_key_over_idempotency_derivation(self) -> None:
        from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
            AppsRgIngressPayload,
            RequestEnvelope,
        )

        from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg

        payload = AppsRgIngressPayload(
            target_company="Acme",
            target_role="Eng",
            source_resume_text="body",
            job_description_text="jd",
            idempotency_key="from-payload",
            l5_certification_ref="test:valid:w6",
        )
        env = RequestEnvelope(
            payload=payload,
            replay_key="envelope-override-xyz",
        )
        vr = u0_validate_apps_rg(env)
        assert vr.replay_key == "envelope-override-xyz"
