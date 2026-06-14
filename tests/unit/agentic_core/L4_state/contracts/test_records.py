"""Unit tests for agentic_core.L4_state.contracts.records.

W1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 state-contract surface.
``records`` (fan_in=32, L4_STATE) holds the durable UWG-owned record dataclasses
(policy / registry / memory / learning). Frozen value contracts — coverage of the
representative records' required fields, safe defaults, and immutability.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L4_state.contracts.records import (
    L4_CONTRACT_SCHEMA_VERSION,
    CapabilityRegistryRecord,
    MemoryRecord,
    ModelRegistryRecord,
    PolicyManifest,
    RegistrySnapshot,
)


class TestPolicyManifest:
    def test_required_fields(self) -> None:
        m = PolicyManifest(policy_manifest_id="pm-1", policy_version="1", policy_hash="h")
        assert m.policy_manifest_id == "pm-1"
        assert m.policy_version == "1"

    def test_defaults(self) -> None:
        m = PolicyManifest(policy_manifest_id="pm-1", policy_version="1", policy_hash="h")
        assert m.schema_version == L4_CONTRACT_SCHEMA_VERSION
        assert m.deterministic_digest == ""
        assert m.tenant_overlays == ()
        assert m.active_alias_state == "active"
        assert m.created_by_surface == "UWG"
        assert m.previous_alias_ref is None

    def test_frozen(self) -> None:
        m = PolicyManifest(policy_manifest_id="pm-1", policy_version="1", policy_hash="h")
        with pytest.raises(dataclasses.FrozenInstanceError):
            m.policy_version = "2"  # type: ignore[misc]


class TestRegistrySnapshot:
    def test_required_and_defaults(self) -> None:
        s = RegistrySnapshot(
            registry_snapshot_id="rs-1", registry_digest="d",
            policy_hash="ph", blueprint_hash="bh",
        )
        assert s.registry_snapshot_id == "rs-1"
        assert s.schema_version == L4_CONTRACT_SCHEMA_VERSION
        assert s.model_registry_refs == ()
        assert s.deprecation_manifest_ref is None

    def test_frozen(self) -> None:
        s = RegistrySnapshot(
            registry_snapshot_id="rs-1", registry_digest="d",
            policy_hash="ph", blueprint_hash="bh",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            s.registry_digest = "x"  # type: ignore[misc]


class TestCapabilityRegistryRecord:
    def test_construction_preserves_flags(self) -> None:
        c = CapabilityRegistryRecord(
            capability_id="cap-1", capability_class="read",
            side_effect_class="none", sandbox_required=True,
            egress_policy_ref="ep", deprecation_state="active",
        )
        assert c.sandbox_required is True
        assert c.side_effect_class == "none"
        assert c.allowed_tools == ()
        assert c.schema_version == L4_CONTRACT_SCHEMA_VERSION

    def test_frozen(self) -> None:
        c = CapabilityRegistryRecord(
            capability_id="cap-1", capability_class="read",
            side_effect_class="none", sandbox_required=False,
            egress_policy_ref="ep", deprecation_state="active",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            c.sandbox_required = True  # type: ignore[misc]


class TestModelRegistryRecord:
    def test_construction(self) -> None:
        m = ModelRegistryRecord(
            model_id="qwen", provider_id="vllm", provider_lane="local",
            context_limit=24576, tool_calling_capability=False,
            structured_output_capability=True, egress_class="internal",
            data_retention_class="none", deprecation_state="active",
            fallback_policy_ref="fp",
        )
        assert m.context_limit == 24576
        assert m.structured_output_capability is True
        assert m.allowed_task_classes == ()
        assert m.schema_version == L4_CONTRACT_SCHEMA_VERSION


class TestMemoryRecord:
    def test_construction_and_defaults(self) -> None:
        r = MemoryRecord(
            memory_id="mem-1", memory_type="procedural",
            memory_text_or_payload_ref="ref", scope="project",
            tenant_id="t1", validity_window="P30D",
            confidence_band="high", policy_hash="ph",
            blueprint_hash="bh", created_at="2026-01-01",
        )
        assert r.scope == "project"
        assert r.created_by_surface == "UWG"
        assert r.subject_refs == ()
        assert r.source_learning_promotion_ref is None
        assert r.schema_version == L4_CONTRACT_SCHEMA_VERSION

    def test_frozen(self) -> None:
        r = MemoryRecord(
            memory_id="mem-1", memory_type="procedural",
            memory_text_or_payload_ref="ref", scope="project",
            tenant_id="t1", validity_window="P30D",
            confidence_band="high", policy_hash="ph",
            blueprint_hash="bh", created_at="2026-01-01",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.scope = "tenant"  # type: ignore[misc]
