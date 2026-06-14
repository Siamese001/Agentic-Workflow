"""Unit tests for agentic_core.L0_routing.intake.envelope.

W2 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 L0 routing chokepoint (x2.0).
``envelope`` (fan_in=22) is the pre-intake request shell. INVARIANT: purely
descriptive; predicates are SHAPE-only and never interpret intent.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L0_routing.intake.envelope import (
    AttachmentManifestEntry,
    AttachmentManifestShell,
    ModalityManifest,
    RawIngressEnvelope,
)


class TestAttachmentManifest:
    def test_entry_default_modality(self) -> None:
        e = AttachmentManifestEntry(filename="r.pdf", mime_type="application/pdf", size_bytes=10, ref="blob:1")
        assert e.declared_modality == "unknown"

    def test_shell_count(self) -> None:
        shell = AttachmentManifestShell(
            entries=(
                AttachmentManifestEntry("a", "text/plain", 1, "r1"),
                AttachmentManifestEntry("b", "text/plain", 2, "r2"),
            ),
        )
        assert shell.count == 2

    def test_empty_shell_count_zero(self) -> None:
        assert AttachmentManifestShell().count == 0

    def test_modality_manifest_defaults(self) -> None:
        m = ModalityManifest()
        assert m.declared == () and m.observed == ()


class TestRawIngressEnvelope:
    def test_required_transport(self) -> None:
        assert RawIngressEnvelope(transport="api").transport == "api"

    def test_defaults(self) -> None:
        env = RawIngressEnvelope(transport="chat")
        assert env.method == ""
        assert env.claimed_tenant_id is None
        assert env.body_text is None
        assert env.body_parser_failed is False
        assert env.auth_credential == {}
        assert env.declared_modalities == ()
        assert env.attachments.count == 0

    def test_has_payload_empty_is_false(self) -> None:
        assert RawIngressEnvelope(transport="chat").has_payload() is False

    def test_has_payload_whitespace_body_is_false(self) -> None:
        assert RawIngressEnvelope(transport="chat", body_text="   ").has_payload() is False

    def test_has_payload_with_body_text(self) -> None:
        assert RawIngressEnvelope(transport="chat", body_text="hi").has_payload() is True

    def test_has_payload_with_body_json(self) -> None:
        assert RawIngressEnvelope(transport="api", body_json={"k": "v"}).has_payload() is True

    def test_has_payload_with_attachment(self) -> None:
        shell = AttachmentManifestShell(entries=(AttachmentManifestEntry("a", "text/plain", 1, "r"),))
        assert RawIngressEnvelope(transport="api", attachments=shell).has_payload() is True

    def test_has_credential(self) -> None:
        assert RawIngressEnvelope(transport="api").has_credential() is False
        assert RawIngressEnvelope(transport="api", auth_credential={"kind": "api_key"}).has_credential() is True

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            RawIngressEnvelope(transport="api").transport = "chat"  # type: ignore[misc]
