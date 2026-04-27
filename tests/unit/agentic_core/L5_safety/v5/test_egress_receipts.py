"""Tests for `egress_receipts.py` (G5 — 00A.5 Egress Receipt Family)."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.v5 import (
    EgressCertificationReceipt,
    EgressCertificationRequest,
    HiddenEgressPathReport,
    NoSilentFallbackReceipt,
    SubstitutionReport,
    connector_substitution_report,
    model_substitution_report,
    provider_substitution_report,
    tool_substitution_report,
)
from agentic_core.L5_safety.v5.types import EgressKind


def test_egress_request_round_trip() -> None:
    req = EgressCertificationRequest(
        request_id="req",
        egress_kind=EgressKind.MODEL,
        target_id="anthropic:claude",
        requested_scope=("text-gen",),
        declared_payload_hash="h",
        declared_credential_scope=("api_key",),
        side_effect_class="MODEL_CALL",
        region="us-west-2",
    )
    d = req.to_dict()
    assert d["egress_kind"] == "MODEL"
    assert d["region"] == "us-west-2"


def test_egress_receipt_validates_status() -> None:
    with pytest.raises(ValueError, match="certification_status"):
        EgressCertificationReceipt(
            receipt_id="x",
            request_id="r",
            egress_kind=EgressKind.MODEL,
            certification_status="BOGUS",
            granted_scope=(),
            denied_scope=(),
            audit_ref="",
            replay_ref="",
        )


def test_substitution_substituted_requires_recertification() -> None:
    """Spec invariant 11 — provider/model/tool/connector change re-certifies."""

    with pytest.raises(ValueError, match="re_certification_required"):
        SubstitutionReport(
            report_id="x",
            kind="provider",
            declared_target="A",
            actual_target="B",
            substituted=True,
            silent_fallback=True,
            re_certification_required=False,  # forbidden
        )


def test_substitution_kind_validation() -> None:
    with pytest.raises(ValueError, match="kind"):
        SubstitutionReport(
            report_id="x",
            kind="bogus",
            declared_target="A",
            actual_target="A",
            substituted=False,
            silent_fallback=False,
            re_certification_required=False,
        )


def test_substitution_helpers_set_kind() -> None:
    common = dict(
        report_id="x",
        declared_target="A",
        actual_target="A",
        substituted=False,
        silent_fallback=False,
        re_certification_required=False,
    )
    assert provider_substitution_report(**common).kind == "provider"
    assert model_substitution_report(**common).kind == "model"
    assert tool_substitution_report(**common).kind == "tool"
    assert connector_substitution_report(**common).kind == "connector"


def test_hidden_egress_path_report_validates_severity() -> None:
    with pytest.raises(ValueError, match="severity"):
        HiddenEgressPathReport(
            report_id="x",
            detected_paths=("foo.py",),
            bypass_kind=("direct_sdk_import",),
            severity="bogus",
        )


def test_no_silent_fallback_receipt_inconsistency_guard() -> None:
    with pytest.raises(ValueError, match="silent_fallback_detected"):
        NoSilentFallbackReceipt(
            receipt_id="r",
            egress_kind=EgressKind.MODEL,
            declared_target="A",
            actual_target="A",  # same yet detected → inconsistent
            silent_fallback_detected=True,
        )
