"""Read-only L4 lookup APIs (00.1 §PHASE 2).

Implements the read-only resolver surface mandated by
``docs/reference/00_L4_State_and_UWG/00.1_L4_Policy_Blueprint_and_Registry_State_detailed.md``
§PHASE 2.

This is the **runtime read tier** that consumes the canonical records from
``records.py`` and returns them under tenant/ACL scope. Mutations remain
gated by UWG — these APIs never write.

Backing store
-------------
The default :class:`InMemoryL4Store` keeps records in a dict keyed by id.
Production deployments substitute a durable backend (SQLite/Postgres)
implementing the same :class:`L4ReadStore` protocol. Either way, lookups
behave identically:

- ``get_active_policy_manifest(tenant_id, route_id, risk_tier, snapshot_id)``
- ``get_policy_by_hash(policy_hash)``
- ``get_blueprint_by_hash(blueprint_hash)``
- ``get_registry_snapshot(registry_snapshot_id)``
- ``resolve_allowed_model_lane(model_id, provider_id, route_id, risk_tier, policy_hash)``
- ``resolve_allowed_tool(tool_id, route_id, capability_id, policy_hash)``
- ``resolve_schema(schema_id, schema_version, policy_hash)``

Failure modes (00.1 §PHASE 4)
-----------------------------
Every resolver fails closed on:
- unknown entry → raises :class:`UnknownEntryError`
- deprecated entry without explicit allow → :class:`DeprecatedEntryError`
- tenant overlay missing for tenant-specific request → :class:`TenantScopeError`
- alias points to non-existent record → :class:`AliasResolutionError`

OTel
----
Every successful read emits the canonical span name (``l4.read.*``) with all
required fields (``trace_id``, ``tenant_id``, ``policy_hash``, etc.).
"""

from __future__ import annotations

import threading
from typing import Dict, Optional, Tuple

from agentic_core.L4_state.contracts.records import (
    BlueprintRecord,
    CapabilityRegistryRecord,
    ModelRegistryRecord,
    PolicyManifest,
    RegistrySnapshot,
    SchemaRegistryRecord,
    ToolRegistryRecord,
)
from agentic_core.L4_state.otel.spans import emit_l4_span


class L4LookupError(RuntimeError):
    """Base class for L4 lookup failures (fail-closed contract)."""


class UnknownEntryError(L4LookupError):
    """Raised when a lookup id has no matching record."""


class DeprecatedEntryError(L4LookupError):
    """Raised when a record's ``deprecation_state`` blocks the lookup."""


class TenantScopeError(L4LookupError):
    """Raised when the requested tenant is not in the record's scope."""


class AliasResolutionError(L4LookupError):
    """Raised when an alias does not resolve to an immutable record."""


class StaleSnapshotError(L4LookupError):
    """Raised when the requested snapshot is older than the record's `valid_from`."""


class InMemoryL4Store:
    """Thread-safe in-memory store backing the read-only lookup APIs.

    Production deployments swap this for a durable backend; the doctrinal
    contract is the **read shape**, not the persistence mechanism.
    """

    def __init__(self) -> None:
        self._policies: Dict[str, PolicyManifest] = {}
        self._policy_by_hash: Dict[str, PolicyManifest] = {}
        self._blueprints_by_hash: Dict[str, BlueprintRecord] = {}
        self._registries: Dict[str, RegistrySnapshot] = {}
        self._models: Dict[str, ModelRegistryRecord] = {}
        self._tools: Dict[str, ToolRegistryRecord] = {}
        self._capabilities: Dict[str, CapabilityRegistryRecord] = {}
        self._schemas: Dict[Tuple[str, str], SchemaRegistryRecord] = {}
        self._active_alias: Dict[Tuple[str, str, str], str] = {}
        # active_alias key: (tenant_id, route_id, risk_tier) -> policy_manifest_id
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Population (UWG-only path; tests use it directly to seed the store)
    # ------------------------------------------------------------------
    def install_policy(
        self,
        manifest: PolicyManifest,
        *,
        tenant_id: str,
        route_id: str,
        risk_tier: str,
        active: bool = True,
    ) -> None:
        with self._lock:
            self._policies[manifest.policy_manifest_id] = manifest
            self._policy_by_hash[manifest.policy_hash] = manifest
            if active:
                self._active_alias[(tenant_id, route_id, risk_tier)] = manifest.policy_manifest_id

    def install_blueprint(self, blueprint: BlueprintRecord) -> None:
        with self._lock:
            self._blueprints_by_hash[blueprint.blueprint_hash] = blueprint

    def install_registry_snapshot(self, snapshot: RegistrySnapshot) -> None:
        with self._lock:
            self._registries[snapshot.registry_snapshot_id] = snapshot

    def install_model(self, model: ModelRegistryRecord) -> None:
        with self._lock:
            self._models[model.model_id] = model

    def install_tool(self, tool: ToolRegistryRecord) -> None:
        with self._lock:
            self._tools[tool.tool_id] = tool

    def install_capability(self, capability: CapabilityRegistryRecord) -> None:
        with self._lock:
            self._capabilities[capability.capability_id] = capability

    def install_schema(self, schema: SchemaRegistryRecord) -> None:
        with self._lock:
            self._schemas[(schema.schema_id, schema.schema_version)] = schema

    # ------------------------------------------------------------------
    # Read APIs (00.1 §PHASE 2)
    # ------------------------------------------------------------------
    def get_active_policy_manifest(
        self,
        *,
        tenant_id: str,
        route_id: str,
        risk_tier: str,
        snapshot_id: str = "",
        trace_id: str = "",
    ) -> PolicyManifest:
        with self._lock:
            key = (tenant_id, route_id, risk_tier)
            policy_id = self._active_alias.get(key)
            if policy_id is None:
                # Fail closed per 00.1 §PHASE 4: tenant overlay missing
                emit_l4_span(
                    "l4.read.policy_manifest",
                    trace_id=trace_id,
                    tenant_id=tenant_id,
                    snapshot_id=snapshot_id,
                    state_surface="policy",
                    operation_type="read",
                    status="UNKNOWN",
                    reason_codes=("tenant_scope_missing",),
                )
                raise TenantScopeError(
                    f"no active policy alias for tenant={tenant_id} route={route_id} tier={risk_tier}"
                )
            manifest = self._policies.get(policy_id)
            if manifest is None:
                emit_l4_span(
                    "l4.read.policy_manifest",
                    trace_id=trace_id,
                    tenant_id=tenant_id,
                    snapshot_id=snapshot_id,
                    state_surface="policy",
                    operation_type="read",
                    status="ALIAS_BROKEN",
                    reason_codes=("alias_resolution_failure",),
                )
                raise AliasResolutionError(
                    f"active alias {key} points to missing policy_manifest_id={policy_id}"
                )
            emit_l4_span(
                "l4.read.policy_manifest",
                trace_id=trace_id,
                tenant_id=tenant_id,
                policy_hash=manifest.policy_hash,
                snapshot_id=snapshot_id,
                state_surface="policy",
                operation_type="read",
                status="OK",
            )
            return manifest

    def get_policy_by_hash(
        self, policy_hash: str, *, tenant_id: str = "", trace_id: str = ""
    ) -> PolicyManifest:
        with self._lock:
            manifest = self._policy_by_hash.get(policy_hash)
            if manifest is None:
                emit_l4_span(
                    "l4.read.policy_version",
                    trace_id=trace_id,
                    tenant_id=tenant_id or "-",
                    state_surface="policy",
                    operation_type="read",
                    status="UNKNOWN",
                    reason_codes=("unknown_policy_hash",),
                )
                raise UnknownEntryError(f"unknown policy_hash={policy_hash}")
            emit_l4_span(
                "l4.read.policy_version",
                trace_id=trace_id,
                tenant_id=tenant_id or "-",
                policy_hash=policy_hash,
                state_surface="policy",
                operation_type="read",
                status="OK",
            )
            return manifest

    def get_blueprint_by_hash(
        self, blueprint_hash: str, *, tenant_id: str = "", trace_id: str = ""
    ) -> BlueprintRecord:
        with self._lock:
            bp = self._blueprints_by_hash.get(blueprint_hash)
            if bp is None:
                emit_l4_span(
                    "l4.read.blueprint_record",
                    trace_id=trace_id,
                    tenant_id=tenant_id or "-",
                    state_surface="blueprint",
                    operation_type="read",
                    status="UNKNOWN",
                    reason_codes=("unknown_blueprint_hash",),
                )
                raise UnknownEntryError(f"unknown blueprint_hash={blueprint_hash}")
            emit_l4_span(
                "l4.read.blueprint_record",
                trace_id=trace_id,
                tenant_id=tenant_id or "-",
                blueprint_hash=blueprint_hash,
                state_surface="blueprint",
                operation_type="read",
                status="OK",
            )
            return bp

    def get_registry_snapshot(
        self,
        registry_snapshot_id: str,
        *,
        tenant_id: str = "",
        trace_id: str = "",
    ) -> RegistrySnapshot:
        with self._lock:
            snap = self._registries.get(registry_snapshot_id)
            if snap is None:
                emit_l4_span(
                    "l4.read.registry_snapshot",
                    trace_id=trace_id,
                    tenant_id=tenant_id or "-",
                    state_surface="registry",
                    operation_type="read",
                    status="UNKNOWN",
                    reason_codes=("unknown_registry_snapshot_id",),
                )
                raise UnknownEntryError(
                    f"unknown registry_snapshot_id={registry_snapshot_id}"
                )
            emit_l4_span(
                "l4.read.registry_snapshot",
                trace_id=trace_id,
                tenant_id=tenant_id or "-",
                policy_hash=snap.policy_hash,
                blueprint_hash=snap.blueprint_hash,
                snapshot_id=registry_snapshot_id,
                state_surface="registry",
                operation_type="read",
                status="OK",
            )
            return snap

    def resolve_allowed_model_lane(
        self,
        *,
        model_id: str,
        provider_id: str,
        route_id: str,
        risk_tier: str,
        policy_hash: str,
        tenant_id: str = "",
        trace_id: str = "",
    ) -> ModelRegistryRecord:
        with self._lock:
            model = self._models.get(model_id)
            if model is None:
                emit_l4_span(
                    "l4.read.registry_record",
                    trace_id=trace_id,
                    tenant_id=tenant_id or "-",
                    policy_hash=policy_hash,
                    state_surface="model",
                    operation_type="read",
                    status="UNKNOWN",
                    reason_codes=("unknown_model_id",),
                )
                raise UnknownEntryError(f"unknown model_id={model_id}")
            if model.provider_id != provider_id:
                raise UnknownEntryError(
                    f"model_id={model_id} not registered under provider_id={provider_id} "
                    f"(actual provider_id={model.provider_id})"
                )
            if model.deprecation_state == "deprecated":
                emit_l4_span(
                    "l4.read.registry_record",
                    trace_id=trace_id,
                    tenant_id=tenant_id or "-",
                    policy_hash=policy_hash,
                    state_surface="model",
                    operation_type="read",
                    status="DEPRECATED",
                    reason_codes=("deprecated_model",),
                )
                raise DeprecatedEntryError(f"model_id={model_id} is deprecated")
            if risk_tier not in model.allowed_risk_tiers:
                raise UnknownEntryError(
                    f"model_id={model_id} not allowed for risk_tier={risk_tier} "
                    f"(allowed={list(model.allowed_risk_tiers)})"
                )
            emit_l4_span(
                "l4.read.registry_record",
                trace_id=trace_id,
                tenant_id=tenant_id or "-",
                policy_hash=policy_hash,
                state_surface="model",
                operation_type="read",
                status="OK",
            )
            return model

    def resolve_allowed_tool(
        self,
        *,
        tool_id: str,
        route_id: str,
        capability_id: str,
        policy_hash: str,
        tenant_id: str = "",
        trace_id: str = "",
    ) -> ToolRegistryRecord:
        with self._lock:
            tool = self._tools.get(tool_id)
            if tool is None:
                emit_l4_span(
                    "l4.read.registry_record",
                    trace_id=trace_id,
                    tenant_id=tenant_id or "-",
                    policy_hash=policy_hash,
                    state_surface="tool",
                    operation_type="read",
                    status="UNKNOWN",
                    reason_codes=("unknown_tool_id",),
                )
                raise UnknownEntryError(f"unknown tool_id={tool_id}")
            if tool.deprecation_state == "deprecated":
                raise DeprecatedEntryError(f"tool_id={tool_id} is deprecated")
            if tool.allowed_route_ids and route_id not in tool.allowed_route_ids:
                raise UnknownEntryError(
                    f"tool_id={tool_id} not allowed for route_id={route_id}"
                )
            cap = self._capabilities.get(capability_id)
            if cap is not None and tool_id not in cap.allowed_tools:
                raise UnknownEntryError(
                    f"tool_id={tool_id} not in capability_id={capability_id} allowed_tools"
                )
            emit_l4_span(
                "l4.read.registry_record",
                trace_id=trace_id,
                tenant_id=tenant_id or "-",
                policy_hash=policy_hash,
                state_surface="tool",
                operation_type="read",
                status="OK",
            )
            return tool

    def resolve_schema(
        self,
        *,
        schema_id: str,
        schema_version: str,
        policy_hash: str,
        tenant_id: str = "",
        trace_id: str = "",
    ) -> SchemaRegistryRecord:
        with self._lock:
            schema = self._schemas.get((schema_id, schema_version))
            if schema is None:
                emit_l4_span(
                    "l4.read.registry_record",
                    trace_id=trace_id,
                    tenant_id=tenant_id or "-",
                    policy_hash=policy_hash,
                    state_surface="schema",
                    operation_type="read",
                    status="UNKNOWN",
                    reason_codes=("unknown_schema",),
                )
                raise UnknownEntryError(
                    f"unknown schema_id={schema_id} schema_version={schema_version}"
                )
            if schema.deprecation_state == "deprecated":
                raise DeprecatedEntryError(
                    f"schema_id={schema_id} schema_version={schema_version} is deprecated"
                )
            emit_l4_span(
                "l4.read.registry_record",
                trace_id=trace_id,
                tenant_id=tenant_id or "-",
                policy_hash=policy_hash,
                state_surface="schema",
                operation_type="read",
                status="OK",
            )
            return schema


# Default singleton ----------------------------------------------------------

_DEFAULT_STORE: Optional[InMemoryL4Store] = None
_DEFAULT_LOCK = threading.Lock()


def get_default_store() -> InMemoryL4Store:
    global _DEFAULT_STORE  # noqa: PLW0603
    with _DEFAULT_LOCK:
        if _DEFAULT_STORE is None:
            _DEFAULT_STORE = InMemoryL4Store()
        return _DEFAULT_STORE


def reset_default_store() -> None:
    global _DEFAULT_STORE  # noqa: PLW0603
    with _DEFAULT_LOCK:
        _DEFAULT_STORE = InMemoryL4Store()


__all__ = [
    "AliasResolutionError",
    "DeprecatedEntryError",
    "InMemoryL4Store",
    "L4LookupError",
    "StaleSnapshotError",
    "TenantScopeError",
    "UnknownEntryError",
    "get_default_store",
    "reset_default_store",
]
