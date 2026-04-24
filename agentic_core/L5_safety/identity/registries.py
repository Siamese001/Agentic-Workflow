"""Registry Contracts — L5 v4 Wave-C (G-12, G-13).

Expands the v3 single "Agent Registry" (Authorized Patron List) into four
sibling registries and adds the pre-L5 Data Authority Resolution hook.

- **G-12 Four Registries**:
    1. Agent Registry      — agent identity + scope ceilings (extended from v3)
    2. Tool Registry       — authorized tool identities + invocation envelopes
    3. Prompt Registry     — authorized prompt digests (system, policy, rubric)
    4. MCP Connector Reg   — authorized MCP servers + allowed_principals +
                             schema version pins
- **G-13 Data Authority Resolution**: pre-L5 hook that resolves RAG / KB /
  training-data sources to a deterministic digest. L5 trusts the digest
  but verifies it matches the current policy_set; drift = reject.

Both are minimum-viable record shapes + lookup helpers. Concrete storage
backends (SQLite / JSON / YAML) live in
`agentic_core/L5_safety/config/` and are wired in by separate follow-ups.

Reference:
  - docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md (Registries)
  - docs/contracts/identity_propagation.md §4 (Registry verification)
Parent plan: .windsurf/plans/l5-governance-best-practice-gap-4615ae.md
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping

from agentic_core.interfaces.principal_chain_types import (
    InvokingUserKind,
    PrincipalChain,
)


# --- G-12.1 Agent Registry ---------------------------------------------


@dataclass(frozen=True)
class AgentRegistryEntry:
    """Full agent registry entry (superset of Wave-B's minimal version)."""

    agent_id: str
    allowed_scope_ceiling: tuple[str, ...]
    allowed_inbound_handoff_scopes: tuple[str, ...]
    owner_principal: str  # invoking_user who registered the agent
    registered_at_tick: int
    deprecated: bool = False

    def __post_init__(self) -> None:
        if not self.agent_id:
            raise ValueError("AgentRegistryEntry: agent_id required")
        if not self.owner_principal:
            raise ValueError("AgentRegistryEntry: owner_principal required")
        # sorted for deterministic digest
        if list(self.allowed_scope_ceiling) != sorted(self.allowed_scope_ceiling):
            object.__setattr__(
                self,
                "allowed_scope_ceiling",
                tuple(sorted(self.allowed_scope_ceiling)),
            )
        if list(self.allowed_inbound_handoff_scopes) != sorted(
            self.allowed_inbound_handoff_scopes,
        ):
            object.__setattr__(
                self,
                "allowed_inbound_handoff_scopes",
                tuple(sorted(self.allowed_inbound_handoff_scopes)),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "allowed_inbound_handoff_scopes": list(
                self.allowed_inbound_handoff_scopes,
            ),
            "allowed_scope_ceiling": list(self.allowed_scope_ceiling),
            "deprecated": self.deprecated,
            "owner_principal": self.owner_principal,
            "registered_at_tick": self.registered_at_tick,
        }


# --- G-12.2 Tool Registry ----------------------------------------------


class ToolKind(str, Enum):
    READ = "read"
    WRITE = "write"
    COMPUTE = "compute"
    EGRESS = "egress"
    META = "meta"


@dataclass(frozen=True)
class ToolRegistryEntry:
    tool_id: str
    kind: ToolKind
    input_schema_digest: str
    output_schema_digest: str
    required_permissions: tuple[str, ...]  # e.g. ("TOOL:READ",) from PERMISSION_CODES
    owner_module: str
    deprecated: bool = False

    def __post_init__(self) -> None:
        if not self.tool_id:
            raise ValueError("ToolRegistryEntry: tool_id required")
        if not self.input_schema_digest or not self.output_schema_digest:
            raise ValueError("ToolRegistryEntry: schema digests required")
        if list(self.required_permissions) != sorted(self.required_permissions):
            object.__setattr__(
                self,
                "required_permissions",
                tuple(sorted(self.required_permissions)),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "deprecated": self.deprecated,
            "input_schema_digest": self.input_schema_digest,
            "kind": self.kind.value,
            "output_schema_digest": self.output_schema_digest,
            "owner_module": self.owner_module,
            "required_permissions": list(self.required_permissions),
            "tool_id": self.tool_id,
        }


# --- G-12.3 Prompt Registry --------------------------------------------


class PromptRole(str, Enum):
    SYSTEM = "system"
    POLICY = "policy"
    RUBRIC = "rubric"
    TEMPLATE = "template"


@dataclass(frozen=True)
class PromptRegistryEntry:
    prompt_id: str
    role: PromptRole
    content_digest: str  # SHA-256 of canonical prompt text
    policy_version: str
    deprecated: bool = False

    def __post_init__(self) -> None:
        if not self.prompt_id or not self.content_digest:
            raise ValueError("PromptRegistryEntry: prompt_id + content_digest required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "content_digest": self.content_digest,
            "deprecated": self.deprecated,
            "policy_version": self.policy_version,
            "prompt_id": self.prompt_id,
            "role": self.role.value,
        }


# --- G-12.4 MCP Connector Registry -------------------------------------


@dataclass(frozen=True)
class MCPConnectorRegistryEntry:
    connector_id: str
    server_endpoint_digest: str  # SHA-256 of server URI + protocol version
    schema_version: str
    allowed_principals: tuple[str, ...]  # empty = any authenticated principal
    allowed_invoking_user_kinds: tuple[InvokingUserKind, ...] = field(
        default_factory=tuple,
    )
    rate_limit_per_minute: int = 60
    deprecated: bool = False

    def __post_init__(self) -> None:
        if not self.connector_id:
            raise ValueError("MCPConnectorRegistryEntry: connector_id required")
        if not self.server_endpoint_digest:
            raise ValueError(
                "MCPConnectorRegistryEntry: server_endpoint_digest required",
            )
        if list(self.allowed_principals) != sorted(self.allowed_principals):
            object.__setattr__(
                self,
                "allowed_principals",
                tuple(sorted(self.allowed_principals)),
            )

    def principal_permitted(self, chain: PrincipalChain) -> bool:
        """True iff the invoking_user + invoking_user_kind are both allowed."""
        if self.allowed_principals and chain.invoking_user not in self.allowed_principals:
            return False
        if (
            self.allowed_invoking_user_kinds
            and chain.invoking_user_kind not in self.allowed_invoking_user_kinds
        ):
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed_invoking_user_kinds": sorted(
                k.value for k in self.allowed_invoking_user_kinds
            ),
            "allowed_principals": list(self.allowed_principals),
            "connector_id": self.connector_id,
            "deprecated": self.deprecated,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "schema_version": self.schema_version,
            "server_endpoint_digest": self.server_endpoint_digest,
        }


# --- G-12 Aggregate Registry Snapshot ---------------------------------


@dataclass(frozen=True)
class RegistrySnapshot:
    """Snapshot of all four registries at a given policy_version.

    `registry_digest` is the SHA-256 of the canonical JSON across all four
    registries and is what gets pinned into every
    CapabilityTokenV4Artifact.registry_digest. Drift at verify time
    (stale snapshot on disk, mutated registry, etc.) yields a REGISTRY_DIGEST_MISMATCH
    failure from the L5 exit-control verifier.
    """

    policy_version: str
    agents: tuple[AgentRegistryEntry, ...]
    tools: tuple[ToolRegistryEntry, ...]
    prompts: tuple[PromptRegistryEntry, ...]
    connectors: tuple[MCPConnectorRegistryEntry, ...]
    registry_digest: str

    def __post_init__(self) -> None:
        if not self.policy_version:
            raise ValueError("RegistrySnapshot: policy_version required")
        if not self.registry_digest:
            raise ValueError("RegistrySnapshot: registry_digest required")

    @staticmethod
    def _canonical(
        policy_version: str,
        agents: Iterable[AgentRegistryEntry],
        tools: Iterable[ToolRegistryEntry],
        prompts: Iterable[PromptRegistryEntry],
        connectors: Iterable[MCPConnectorRegistryEntry],
    ) -> str:
        payload = {
            "agents": sorted(
                (a.to_dict() for a in agents), key=lambda d: d["agent_id"],
            ),
            "connectors": sorted(
                (c.to_dict() for c in connectors),
                key=lambda d: d["connector_id"],
            ),
            "policy_version": policy_version,
            "prompts": sorted(
                (p.to_dict() for p in prompts), key=lambda d: d["prompt_id"],
            ),
            "tools": sorted(
                (t.to_dict() for t in tools), key=lambda d: d["tool_id"],
            ),
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    def to_json(self) -> str:
        return RegistrySnapshot._canonical(
            self.policy_version, self.agents, self.tools, self.prompts, self.connectors,
        )


def build_registry_snapshot(
    *,
    policy_version: str,
    agents: Iterable[AgentRegistryEntry] = (),
    tools: Iterable[ToolRegistryEntry] = (),
    prompts: Iterable[PromptRegistryEntry] = (),
    connectors: Iterable[MCPConnectorRegistryEntry] = (),
) -> RegistrySnapshot:
    """Build a deterministic RegistrySnapshot with computed registry_digest."""
    agents_t = tuple(agents)
    tools_t = tuple(tools)
    prompts_t = tuple(prompts)
    connectors_t = tuple(connectors)
    canonical = RegistrySnapshot._canonical(
        policy_version, agents_t, tools_t, prompts_t, connectors_t,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return RegistrySnapshot(
        policy_version=policy_version,
        agents=agents_t,
        tools=tools_t,
        prompts=prompts_t,
        connectors=connectors_t,
        registry_digest=digest,
    )


# --- G-13 Data Authority Resolution -----------------------------------


class DataSourceKind(str, Enum):
    RAG_INDEX = "rag_index"
    KB_CORPUS = "kb_corpus"
    TRAINING_DATA = "training_data"
    POLICY_BUNDLE = "policy_bundle"
    RUBRIC_SET = "rubric_set"


@dataclass(frozen=True)
class DataAuthorityRecord:
    """One entry in the data-authority ledger.

    L5 trusts the `content_digest` but verifies it matches the
    `expected_digest` the policy_set has pinned. Drift = REJECT per
    SAIF Perimeter Principle (G-13).
    """

    source_id: str
    kind: DataSourceKind
    content_digest: str
    supply_chain_attestation: str  # e.g. SLSA provenance digest; "" if none
    expected_digest: str  # Digest pinned in the policy_set (authoritative)
    policy_version: str

    def __post_init__(self) -> None:
        if not self.source_id:
            raise ValueError("DataAuthorityRecord: source_id required")
        if not self.content_digest:
            raise ValueError("DataAuthorityRecord: content_digest required")
        if not self.expected_digest:
            raise ValueError("DataAuthorityRecord: expected_digest required")

    @property
    def matches_pin(self) -> bool:
        """True iff the current content digest matches the policy-pinned digest."""
        return self.content_digest == self.expected_digest

    def to_dict(self) -> dict[str, Any]:
        return {
            "content_digest": self.content_digest,
            "expected_digest": self.expected_digest,
            "kind": self.kind.value,
            "matches_pin": self.matches_pin,
            "policy_version": self.policy_version,
            "source_id": self.source_id,
            "supply_chain_attestation": self.supply_chain_attestation,
        }


@dataclass(frozen=True)
class DataAuthorityResolution:
    """Outcome of a pre-L5 Data Authority Resolution sweep."""

    records: tuple[DataAuthorityRecord, ...]
    all_match: bool
    drifts: tuple[str, ...]  # source_ids whose digest drifted

    def to_dict(self) -> dict[str, Any]:
        return {
            "all_match": self.all_match,
            "drifts": list(self.drifts),
            "records": [r.to_dict() for r in self.records],
        }


def resolve_data_authority(
    records: Iterable[DataAuthorityRecord],
) -> DataAuthorityResolution:
    """Run the data-authority sweep; produce a resolution outcome."""
    records_t = tuple(records)
    drifts = tuple(r.source_id for r in records_t if not r.matches_pin)
    return DataAuthorityResolution(
        records=records_t,
        all_match=not drifts,
        drifts=drifts,
    )


def verify_token_against_registry(
    *,
    token_registry_digest: str,
    current_snapshot: RegistrySnapshot,
) -> tuple[bool, str]:
    """Return (match, reason) comparing a token's pinned registry_digest to
    the current on-disk snapshot. Drift = upgrade path needs to re-issue
    the token at the new policy_version."""
    if not token_registry_digest:
        return False, "MISSING_REGISTRY_DIGEST"
    if token_registry_digest != current_snapshot.registry_digest:
        return (
            False,
            f"REGISTRY_DIGEST_MISMATCH:token={token_registry_digest[:16]}... "
            f"current={current_snapshot.registry_digest[:16]}...",
        )
    return True, "MATCH"


__all__ = [
    "AgentRegistryEntry",
    "DataAuthorityRecord",
    "DataAuthorityResolution",
    "DataSourceKind",
    "MCPConnectorRegistryEntry",
    "PromptRegistryEntry",
    "PromptRole",
    "RegistrySnapshot",
    "ToolKind",
    "ToolRegistryEntry",
    "build_registry_snapshot",
    "resolve_data_authority",
    "verify_token_against_registry",
]
