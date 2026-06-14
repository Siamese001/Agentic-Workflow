"""Unit tests for agentic_core.prompt_governance.pa_package_driven_binding.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core module.
``pa_package_driven_binding`` is the app-agnostic Package-Driven Prompt Assembly
binding. The top-level ``pa_assemble_prompt_package_driven`` needs live YAML
profiles + Jinja templates + filesystem IO, so it is out of scope here. This file
covers the pure/deterministic surface: the frozen receipt/manifest dataclasses,
the canonical slot order, the exception hierarchy, and the ``_compute_hash``
SHA256 helper (16-hex truncation + determinism).
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.prompt_governance.pa_package_driven_binding import (
    CANONICAL_SLOT_ORDER,
    AssemblySecurityReceipt,
    PromptAssemblyError,
    PromptBoundaryReceipt,
    PromptEnvelope,
    ProviderRenderManifest,
    ReplayManifest,
    SchemaNotBoundError,
    SlotContent,
    SlotLineageMap,
    TemplateNotFoundError,
    _compute_hash,
)


class TestCanonicalSlotOrder:
    def test_order_and_membership(self) -> None:
        assert CANONICAL_SLOT_ORDER == [
            "S0_system",
            "D0_fences",
            "I0_instructions",
            "E0_approved_examples",
            "C0_verified_evidence",
            "M0_provider_controls",
            "U0_neutralized_user_task",
            "H0_bounded_repair",
            "R0_response_schema",
        ]

    def test_nine_slots(self) -> None:
        assert len(CANONICAL_SLOT_ORDER) == 9


class TestComputeHash:
    def test_returns_16_hex(self) -> None:
        h = _compute_hash("hello")
        assert len(h) == 16
        assert all(c in "0123456789abcdef" for c in h)

    def test_deterministic(self) -> None:
        assert _compute_hash("abc") == _compute_hash("abc")

    def test_distinct_inputs_distinct_hash(self) -> None:
        assert _compute_hash("abc") != _compute_hash("abd")

    def test_known_vector(self) -> None:
        # sha256("")[:16]
        assert _compute_hash("") == "e3b0c44298fc1c14"


class TestExceptionHierarchy:
    def test_template_not_found_is_pa_error(self) -> None:
        assert issubclass(TemplateNotFoundError, PromptAssemblyError)

    def test_schema_not_bound_is_pa_error(self) -> None:
        assert issubclass(SchemaNotBoundError, PromptAssemblyError)

    def test_pa_error_is_exception(self) -> None:
        assert issubclass(PromptAssemblyError, Exception)


class TestSlotContent:
    def test_required_and_defaults(self) -> None:
        s = SlotContent(
            slot_id="S0_system",
            content="body",
            content_hash="abc",
            source_ref="ref",
        )
        assert s.template_ref == ""
        assert s.authority_level == ""
        assert s.data_boundary_label is None

    def test_frozen(self) -> None:
        s = SlotContent("s", "c", "h", "r")
        with pytest.raises(dataclasses.FrozenInstanceError):
            s.content = "x"  # type: ignore[misc]


class TestManifests:
    def test_provider_render_manifest(self) -> None:
        m = ProviderRenderManifest(
            format="chat_completions_api",
            message_roles=("system", "user"),
            response_format="json_object",
            slot_order=("S0", "U0"),
        )
        assert m.format == "chat_completions_api"
        assert m.message_roles == ("system", "user")

    def test_replay_manifest(self) -> None:
        r = ReplayManifest(
            template_refs=["t1"],
            evidence_digest="dig",
            output_schema_ref="schema",
            slot_ids_used=["S0"],
        )
        assert r.evidence_digest == "dig"
        assert r.slot_ids_used == ["S0"]

    def test_prompt_envelope_frozen(self) -> None:
        e = PromptEnvelope(
            system_content="s",
            user_content="u",
            evidence_context="e",
            response_schema="r",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            e.user_content = "x"  # type: ignore[misc]


class TestReceipts:
    def test_prompt_boundary_receipt(self) -> None:
        r = PromptBoundaryReceipt(
            receipt_id="pbr-1",
            evidence_data_only_verified=True,
            uploaded_briefing_data_only_verified=True,
            cached_substrate_data_only_verified=True,
            instruction_data_airlock_sealed=True,
            timestamp="2026-01-01T00:00:00Z",
        )
        assert r.receipt_id == "pbr-1"
        assert r.instruction_data_airlock_sealed is True

    def test_assembly_security_receipt_frozen(self) -> None:
        r = AssemblySecurityReceipt(
            receipt_id="psr-1",
            authority_order_valid=True,
            slot_injection_scan_passed=True,
            user_task_neutralized=True,
            timestamp="2026-01-01T00:00:00Z",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.authority_order_valid = False  # type: ignore[misc]

    def test_slot_lineage_map(self) -> None:
        m = SlotLineageMap(
            slot_id="S0_system",
            source_ref="ref",
            source_hash="h",
            assembly_timestamp="2026-01-01T00:00:00Z",
            authority_level="highest",
        )
        assert m.authority_level == "highest"
