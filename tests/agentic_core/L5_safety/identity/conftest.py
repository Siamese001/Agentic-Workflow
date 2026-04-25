"""Shared fixtures for L5_safety/identity tests."""

import pytest

from agentic_core.interfaces.principal_chain_types import (
    InvokingUserKind,
    PrincipalChain,
)
from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L2_execution.types.capability_token_v4_types import (
    CapabilityTokenV4Artifact,
    issue_capability_token_v4,
)
from agentic_core.L5_safety.identity.guardrail_bank import (
    GuardrailFamily,
    GuardrailOutcome,
)
from agentic_core.L5_safety.identity.registries import (
    AgentRegistryEntry,
    DataAuthorityRecord,
    DataSourceKind,
    MCPConnectorRegistryEntry,
    PromptRegistryEntry,
    PromptRole,
    RegistrySnapshot,
    ToolKind,
    ToolRegistryEntry,
)


@pytest.fixture
def sample_semantic_clock() -> SemanticClockSnapshot:
    """Sample semantic clock for testing."""
    return SemanticClockSnapshot(
        tick=1000,
        vector_clock=(("L1", 10), ("L2", 5)),
    )


@pytest.fixture
def sample_principal_chain() -> PrincipalChain:
    """Sample principal chain for testing."""
    return PrincipalChain(
        agent_id="test_agent",
        invoking_user="user@example.com",
        invoking_user_kind=InvokingUserKind.HUMAN,
        auth_method="oauth2",
        scope_tag="default",
    )


@pytest.fixture
def sample_v4_token(
    sample_principal_chain: PrincipalChain,
    sample_semantic_clock: SemanticClockSnapshot,
) -> CapabilityTokenV4Artifact:
    """Sample v4 capability token for testing."""
    return issue_capability_token_v4(
        semantic_clock=sample_semantic_clock,
        principal_chain=sample_principal_chain,
        risk_tier_band="MODERATE",
        permission_ladder_entry="mutate",
        subject_kind="agent",
        subject_id="test_agent",
        issued_by="test_issuer",
        permissions=("read", "write"),
        allowed_paths=("read", "write"),
        max_tool_calls=100,
        ttl_seconds=900,
        single_use=False,
        expires_at_semantic_clock="tick:999999999",
        connector_allowlist=("claude_mcp",),
        tool_allowlist=("http_tool",),
        plan_digest="test_plan_digest_def456",
        grant_mode="sessioned",
        policy_version="v4.0.0",
        registry_digest="test_registry_digest_abc123",
    )


@pytest.fixture
def sample_guardrail_outcome() -> GuardrailOutcome:
    """Sample guardrail outcome for testing."""
    return GuardrailOutcome(
        family=GuardrailFamily.PII,
        layer="client_universal",
        stage="ingress",
        action="allow",
        score=0.0,
        evidence="no_pii_detected",
    )


@pytest.fixture
def sample_agent_registry_entry() -> AgentRegistryEntry:
    """Sample agent registry entry."""
    return AgentRegistryEntry(
        agent_id="test_agent",
        allowed_scope_ceiling=("read", "write"),
        allowed_inbound_handoff_scopes=("default",),
        owner_principal="user@example.com",
        registered_at_tick=1000,
    )


@pytest.fixture
def sample_tool_registry_entry() -> ToolRegistryEntry:
    """Sample tool registry entry."""
    return ToolRegistryEntry(
        tool_id="test_tool",
        kind=ToolKind.WRITE,
        input_schema_digest="input_sha256",
        output_schema_digest="output_sha256",
        required_permissions=("TOOL:WRITE",),
        owner_module="test_module",
    )


@pytest.fixture
def sample_prompt_registry_entry() -> PromptRegistryEntry:
    """Sample prompt registry entry."""
    return PromptRegistryEntry(
        prompt_id="system_prompt_v1",
        role=PromptRole.SYSTEM,
        content_digest="content_sha256",
        policy_version="v4.0.0",
    )


@pytest.fixture
def sample_mcp_connector_entry() -> MCPConnectorRegistryEntry:
    """Sample MCP connector registry entry."""
    return MCPConnectorRegistryEntry(
        connector_id="claude_mcp",
        server_endpoint_digest="endpoint_sha256",
        schema_version="1.0",
        allowed_principals=("user@example.com",),
    )


@pytest.fixture
def sample_registry_snapshot(
    sample_agent_registry_entry: AgentRegistryEntry,
    sample_tool_registry_entry: ToolRegistryEntry,
    sample_prompt_registry_entry: PromptRegistryEntry,
    sample_mcp_connector_entry: MCPConnectorRegistryEntry,
) -> RegistrySnapshot:
    """Sample registry snapshot with all four registries."""
    return RegistrySnapshot(
        policy_version="v4.0.0",
        agents=(sample_agent_registry_entry,),
        tools=(sample_tool_registry_entry,),
        prompts=(sample_prompt_registry_entry,),
        connectors=(sample_mcp_connector_entry,),
        registry_digest="test_digest_abc123",
    )


@pytest.fixture
def sample_data_authority_record() -> DataAuthorityRecord:
    """Sample data authority record."""
    return DataAuthorityRecord(
        source_id="test_rag_index",
        kind=DataSourceKind.RAG_INDEX,
        content_digest="content_sha256",
        supply_chain_attestation="slsa_provenance",
        expected_digest="content_sha256",  # Matching = no drift
        policy_version="v4.0.0",
    )


@pytest.fixture
def sample_drifted_data_authority_record() -> DataAuthorityRecord:
    """Sample data authority record with drift."""
    return DataAuthorityRecord(
        source_id="test_rag_index",
        kind=DataSourceKind.RAG_INDEX,
        content_digest="different_content_sha256",  # Drifted
        supply_chain_attestation="slsa_provenance",
        expected_digest="expected_sha256",
        policy_version="v4.0.0",
    )

