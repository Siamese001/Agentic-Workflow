"""L4 read-only lookup API tests (00.1 §PHASE 2 + §PHASE 4).

Closes the previously-deferred §PHASE 2 row in the requirements traceability
matrix. Covers:

- ``get_active_policy_manifest`` (tenant/route/risk_tier scoped)
- ``get_policy_by_hash``
- ``get_blueprint_by_hash``
- ``get_registry_snapshot``
- ``resolve_allowed_model_lane``
- ``resolve_allowed_tool``
- ``resolve_schema``

Plus the §PHASE 4 fail-closed semantics for unknown / deprecated / tenant-out-of-scope.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.contracts import (
    AliasResolutionError,
    BlueprintRecord,
    CapabilityRegistryRecord,
    DeprecatedEntryError,
    InMemoryL4Store,
    ModelRegistryRecord,
    PolicyManifest,
    RegistrySnapshot,
    SchemaRegistryRecord,
    TenantScopeError,
    ToolRegistryRecord,
    UnknownEntryError,
)
from agentic_core.L4_state.contracts.records import stamp_digest
from agentic_core.L4_state.otel.spans import get_emitted_spans


def _seed_store() -> InMemoryL4Store:
    store = InMemoryL4Store()
    pm = stamp_digest(
        PolicyManifest(policy_manifest_id="pm:1", policy_version="v1", policy_hash="ph:1")
    )
    store.install_policy(pm, tenant_id="t:1", route_id="r:1", risk_tier="medium")
    store.install_blueprint(
        stamp_digest(
            BlueprintRecord(blueprint_id="bp:1", blueprint_hash="bh:1", blueprint_type="route")
        )
    )
    store.install_registry_snapshot(
        stamp_digest(
            RegistrySnapshot(
                registry_snapshot_id="rs:1",
                registry_digest="rd:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
            )
        )
    )
    store.install_model(
        stamp_digest(
            ModelRegistryRecord(
                model_id="m:1",
                provider_id="p:1",
                provider_lane="lane:fast",
                context_limit=8192,
                tool_calling_capability=True,
                structured_output_capability=True,
                egress_class="egress:none",
                data_retention_class="zero",
                deprecation_state="active",
                fallback_policy_ref="fp:1",
                allowed_task_classes=("answer",),
                allowed_risk_tiers=("low", "medium"),
            )
        )
    )
    store.install_model(
        stamp_digest(
            ModelRegistryRecord(
                model_id="m:dep",
                provider_id="p:1",
                provider_lane="lane:fast",
                context_limit=8192,
                tool_calling_capability=False,
                structured_output_capability=False,
                egress_class="egress:none",
                data_retention_class="zero",
                deprecation_state="deprecated",
                fallback_policy_ref="fp:1",
                allowed_risk_tiers=("low",),
            )
        )
    )
    store.install_tool(
        stamp_digest(
            ToolRegistryRecord(
                tool_id="tl:1",
                tool_version="1.0",
                tool_provider="prov:1",
                input_schema_ref="sch:in@1",
                output_schema_ref="sch:out@1",
                side_effect_class="read",
                sandbox_class_required="basic",
                credential_scope="none",
                network_scope="none",
                egress_policy_ref="egress:none",
                deprecation_state="active",
                allowed_route_ids=("r:1",),
            )
        )
    )
    store.install_capability(
        stamp_digest(
            CapabilityRegistryRecord(
                capability_id="cap:1",
                capability_class="read",
                side_effect_class="none",
                sandbox_required=False,
                egress_policy_ref="egress:none",
                deprecation_state="active",
                allowed_tools=("tl:1",),
                risk_tier_bounds=("low", "medium"),
            )
        )
    )
    store.install_schema(
        stamp_digest(
            SchemaRegistryRecord(
                schema_id="sch:answer",
                schema_version="1",
                schema_hash="schash:1",
                contract_type="output",
                owner_surface="L2",
                backward_compatibility="strict",
                deprecation_state="active",
            )
        )
    )
    return store


class TestActivePolicyManifest:
    def test_resolves_for_seeded_tenant(self) -> None:
        store = _seed_store()
        pm = store.get_active_policy_manifest(
            tenant_id="t:1", route_id="r:1", risk_tier="medium", trace_id="tr:1"
        )
        assert pm.policy_hash == "ph:1"
        # OTel span emitted with required fields
        spans = [s for s in get_emitted_spans() if s.name == "l4.read.policy_manifest"]
        assert spans
        assert spans[-1].attributes["tenant_id"] == "t:1"
        assert spans[-1].attributes["status"] == "OK"

    def test_unknown_tenant_fails_closed(self) -> None:
        store = _seed_store()
        with pytest.raises(TenantScopeError):
            store.get_active_policy_manifest(
                tenant_id="t:UNKNOWN", route_id="r:1", risk_tier="medium"
            )

    def test_alias_pointing_to_missing_record_fails_closed(self) -> None:
        store = _seed_store()
        # Surgically corrupt the alias target
        store._policies.clear()  # noqa: SLF001 — testing fail-closed path
        with pytest.raises(AliasResolutionError):
            store.get_active_policy_manifest(
                tenant_id="t:1", route_id="r:1", risk_tier="medium"
            )


class TestPolicyByHash:
    def test_resolves_known_hash(self) -> None:
        store = _seed_store()
        pm = store.get_policy_by_hash("ph:1", tenant_id="t:1", trace_id="tr:1")
        assert pm.policy_manifest_id == "pm:1"

    def test_unknown_hash_fails_closed(self) -> None:
        store = _seed_store()
        with pytest.raises(UnknownEntryError):
            store.get_policy_by_hash("ph:UNKNOWN")


class TestBlueprintByHash:
    def test_resolves_known(self) -> None:
        store = _seed_store()
        bp = store.get_blueprint_by_hash("bh:1")
        assert bp.blueprint_id == "bp:1"

    def test_unknown_fails_closed(self) -> None:
        store = _seed_store()
        with pytest.raises(UnknownEntryError):
            store.get_blueprint_by_hash("bh:UNKNOWN")


class TestRegistrySnapshot:
    def test_resolves_known(self) -> None:
        store = _seed_store()
        rs = store.get_registry_snapshot("rs:1")
        assert rs.registry_digest == "rd:1"

    def test_unknown_fails_closed(self) -> None:
        store = _seed_store()
        with pytest.raises(UnknownEntryError):
            store.get_registry_snapshot("rs:UNKNOWN")


class TestResolveAllowedModelLane:
    def test_active_model_resolves(self) -> None:
        store = _seed_store()
        m = store.resolve_allowed_model_lane(
            model_id="m:1",
            provider_id="p:1",
            route_id="r:1",
            risk_tier="medium",
            policy_hash="ph:1",
        )
        assert m.model_id == "m:1"

    def test_unknown_model_fails_closed(self) -> None:
        store = _seed_store()
        with pytest.raises(UnknownEntryError):
            store.resolve_allowed_model_lane(
                model_id="m:UNKNOWN",
                provider_id="p:1",
                route_id="r:1",
                risk_tier="medium",
                policy_hash="ph:1",
            )

    def test_deprecated_model_fails_closed(self) -> None:
        store = _seed_store()
        with pytest.raises(DeprecatedEntryError):
            store.resolve_allowed_model_lane(
                model_id="m:dep",
                provider_id="p:1",
                route_id="r:1",
                risk_tier="low",
                policy_hash="ph:1",
            )

    def test_provider_mismatch_fails_closed(self) -> None:
        store = _seed_store()
        with pytest.raises(UnknownEntryError):
            store.resolve_allowed_model_lane(
                model_id="m:1",
                provider_id="p:OTHER",
                route_id="r:1",
                risk_tier="medium",
                policy_hash="ph:1",
            )

    def test_risk_tier_out_of_range_fails_closed(self) -> None:
        store = _seed_store()
        with pytest.raises(UnknownEntryError):
            store.resolve_allowed_model_lane(
                model_id="m:1",
                provider_id="p:1",
                route_id="r:1",
                risk_tier="critical",  # not in allowed_risk_tiers
                policy_hash="ph:1",
            )


class TestResolveAllowedTool:
    def test_active_tool_under_capability(self) -> None:
        store = _seed_store()
        tool = store.resolve_allowed_tool(
            tool_id="tl:1", route_id="r:1", capability_id="cap:1", policy_hash="ph:1"
        )
        assert tool.tool_id == "tl:1"

    def test_unknown_tool_fails_closed(self) -> None:
        store = _seed_store()
        with pytest.raises(UnknownEntryError):
            store.resolve_allowed_tool(
                tool_id="tl:UNKNOWN",
                route_id="r:1",
                capability_id="cap:1",
                policy_hash="ph:1",
            )

    def test_route_mismatch_fails_closed(self) -> None:
        store = _seed_store()
        with pytest.raises(UnknownEntryError):
            store.resolve_allowed_tool(
                tool_id="tl:1",
                route_id="r:OTHER",
                capability_id="cap:1",
                policy_hash="ph:1",
            )


class TestResolveSchema:
    def test_active_schema_resolves(self) -> None:
        store = _seed_store()
        s = store.resolve_schema(
            schema_id="sch:answer", schema_version="1", policy_hash="ph:1"
        )
        assert s.schema_hash == "schash:1"

    def test_unknown_version_fails_closed(self) -> None:
        store = _seed_store()
        with pytest.raises(UnknownEntryError):
            store.resolve_schema(
                schema_id="sch:answer", schema_version="999", policy_hash="ph:1"
            )


class TestNoMutationOnRead:
    """Read APIs MUST NOT mutate cache/memory/audit state (00.1 §PHASE 2)."""

    def test_repeated_reads_yield_identical_records(self) -> None:
        store = _seed_store()
        a = store.get_active_policy_manifest(
            tenant_id="t:1", route_id="r:1", risk_tier="medium"
        )
        b = store.get_active_policy_manifest(
            tenant_id="t:1", route_id="r:1", risk_tier="medium"
        )
        assert a.deterministic_digest == b.deterministic_digest
        # Same Python object (frozen dataclass — value equality already implies digest equality)
        assert a == b
