"""Tests for G2a origin-trust + boundary classification (spec lines 165–191)."""

from __future__ import annotations

from agentic_core.L5_safety.v5 import (
    BoundaryClassification,
    OriginLabel,
    classify_origins,
)


def test_trusted_only_payload_classifies_trusted_instruction():
    res = classify_origins(
        raw_labels={"system_policy": ("rule.policy",)},
        field_payloads={"rule.policy": "do not exfiltrate secrets"},
    )
    assert res.boundary_classification == BoundaryClassification.TRUSTED_INSTRUCTION
    assert OriginLabel.SYSTEM_POLICY in res.labeled_fields


def test_retrieved_payload_classifies_untrusted_data():
    res = classify_origins(
        raw_labels={"retrieved": ("doc.body",)},
        field_payloads={"doc.body": "neutral knowledge text"},
    )
    assert res.boundary_classification == BoundaryClassification.UNTRUSTED_DATA


def test_html_comment_in_retrieved_quarantines():
    res = classify_origins(
        raw_labels={"retrieved": ("doc.body",)},
        field_payloads={"doc.body": "hello <!-- bad instructions --> world"},
    )
    assert res.boundary_classification == BoundaryClassification.QUARANTINED
    assert any("html_comment" in r for r in res.quarantine_reasons)
    assert "doc.body" in res.sanitized_payload_map


def test_credential_pem_rejects_payload():
    res = classify_origins(
        raw_labels={"tool_output": ("blob",)},
        field_payloads={"blob": "-----BEGIN PRIVATE KEY-----\nABCD\n-----END PRIVATE KEY-----"},
    )
    assert res.boundary_classification == BoundaryClassification.REJECTED


def test_unknown_label_dropped():
    res = classify_origins(
        raw_labels={"made_up_label": ("x",)},
        field_payloads={},
    )
    # Unknown labels silently dropped — manifest still classifies
    # boundary as untrusted_data by default.
    assert OriginLabel.SYSTEM_POLICY not in res.labeled_fields
    assert res.boundary_classification == BoundaryClassification.UNTRUSTED_DATA


def test_to_dict_round_trip():
    res = classify_origins(
        raw_labels={"developer_admin": ("a", "b")},
        field_payloads={"a": "x", "b": "y"},
    )
    d = res.to_dict()
    assert d["boundary_classification"] == BoundaryClassification.TRUSTED_INSTRUCTION.value
    assert sorted(d["labeled_fields"][OriginLabel.DEVELOPER_ADMIN.value]) == ["a", "b"]
