"""Tests for L5_safety/identity/registries.py."""

import pytest

from agentic_core.interfaces.principal_chain_types import InvokingUserKind, PrincipalChain
from agentic_core.L5_safety.identity.registries import (
    AgentRegistryEntry,
    DataAuthorityRecord,
    DataAuthorityResolution,
    DataSourceKind,
    MCPConnectorRegistryEntry,
    PromptRegistryEntry,
    PromptRole,
    RegistrySnapshot,
    ToolKind,
    ToolRegistryEntry,
    build_registry_snapshot,
    resolve_data_authority,
    verify_token_against_registry,
)


def test_resolve_data_authority_all_match(sample_data_authority_record):
    """Test resolve_data_authority when all records match their pins."""
    resolution = resolve_data_authority((sample_data_authority_record,))
    
    assert resolution.all_match is True
    assert len(resolution.records) == 1
    assert len(resolution.drifts) == 0


def test_resolve_data_authority_with_drift(sample_drifted_data_authority_record):
    """Test resolve_data_authority when records have drifted."""
    resolution = resolve_data_authority((sample_drifted_data_authority_record,))
    
    assert resolution.all_match is False
    assert len(resolution.records) == 1
    assert len(resolution.drifts) == 1
    assert resolution.drifts[0] == "test_rag_index"


def test_verify_token_against_registry_match(sample_registry_snapshot):
    """Test verify_token_against_registry when digests match."""
    match, reason = verify_token_against_registry(
        token_registry_digest=sample_registry_snapshot.registry_digest,
        current_snapshot=sample_registry_snapshot,
    )
    
    assert match is True
    assert reason == "MATCH"


def test_verify_token_against_registry_mismatch(sample_registry_snapshot):
    """Test verify_token_against_registry when digests mismatch."""
    match, reason = verify_token_against_registry(
        token_registry_digest="different_digest_abc123",
        current_snapshot=sample_registry_snapshot,
    )
    
    assert match is False
    assert "REGISTRY_DIGEST_MISMATCH" in reason


def test_verify_token_against_registry_missing_digest(sample_registry_snapshot):
    """Test verify_token_against_registry when token has no digest."""
    match, reason = verify_token_against_registry(
        token_registry_digest="",
        current_snapshot=sample_registry_snapshot,
    )
    
    assert match is False
    assert reason == "MISSING_REGISTRY_DIGEST"


def test_build_registry_snapshot(sample_agent_registry_entry, sample_tool_registry_entry):
    """Test build_registry_snapshot creates deterministic digest."""
    snapshot = build_registry_snapshot(
        policy_version="v4.0.0",
        agents=(sample_agent_registry_entry,),
        tools=(sample_tool_registry_entry,),
    )
    
    assert snapshot.policy_version == "v4.0.0"
    assert len(snapshot.agents) == 1
    assert len(snapshot.tools) == 1
    assert snapshot.registry_digest is not None
    assert len(snapshot.registry_digest) == 64  # SHA-256 hex string


def test_agent_registry_entry_validation_requires_agent_id():
    """Test AgentRegistryEntry requires agent_id."""
    with pytest.raises(ValueError, match="agent_id required"):
        AgentRegistryEntry(
            agent_id="",
            allowed_scope_ceiling=("read",),
            allowed_inbound_handoff_scopes=(),
            owner_principal="user@example.com",
            registered_at_tick=1000,
        )


def test_agent_registry_entry_validation_requires_owner_principal():
    """Test AgentRegistryEntry requires owner_principal."""
    with pytest.raises(ValueError, match="owner_principal required"):
        AgentRegistryEntry(
            agent_id="test_agent",
            allowed_scope_ceiling=("read",),
            allowed_inbound_handoff_scopes=(),
            owner_principal="",
            registered_at_tick=1000,
        )


def test_agent_registry_entry_sorts_scope_ceiling():
    """Test AgentRegistryEntry sorts allowed_scope_ceiling."""
    entry = AgentRegistryEntry(
        agent_id="test_agent",
        allowed_scope_ceiling=("write", "read"),  # Unsorted
        allowed_inbound_handoff_scopes=(),
        owner_principal="user@example.com",
        registered_at_tick=1000,
    )
    
    assert entry.allowed_scope_ceiling == ("read", "write")  # Sorted


def test_agent_registry_entry_to_dict():
    """Test AgentRegistryEntry.to_dict serialization."""
    entry = AgentRegistryEntry(
        agent_id="test_agent",
        allowed_scope_ceiling=("read", "write"),
        allowed_inbound_handoff_scopes=("default",),
        owner_principal="user@example.com",
        registered_at_tick=1000,
        deprecated=True,
    )
    
    d = entry.to_dict()
    assert d["agent_id"] == "test_agent"
    assert d["allowed_scope_ceiling"] == ["read", "write"]
    assert d["allowed_inbound_handoff_scopes"] == ["default"]
    assert d["owner_principal"] == "user@example.com"
    assert d["registered_at_tick"] == 1000
    assert d["deprecated"] is True


def test_tool_kind_enum_values():
    """Test ToolKind enum has expected values."""
    assert ToolKind.READ.value == "read"
    assert ToolKind.WRITE.value == "write"
    assert ToolKind.COMPUTE.value == "compute"
    assert ToolKind.EGRESS.value == "egress"
    assert ToolKind.META.value == "meta"


def test_tool_registry_entry_validation_requires_tool_id():
    """Test ToolRegistryEntry requires tool_id."""
    with pytest.raises(ValueError, match="tool_id required"):
        ToolRegistryEntry(
            tool_id="",
            kind=ToolKind.READ,
            input_schema_digest="digest1",
            output_schema_digest="digest2",
            required_permissions=(),
            owner_module="test_module",
        )


def test_tool_registry_entry_validation_requires_schema_digests():
    """Test ToolRegistryEntry requires both schema digests."""
    with pytest.raises(ValueError, match="schema digests required"):
        ToolRegistryEntry(
            tool_id="test_tool",
            kind=ToolKind.READ,
            input_schema_digest="",
            output_schema_digest="digest2",
            required_permissions=(),
            owner_module="test_module",
        )


def test_tool_registry_entry_sorts_permissions():
    """Test ToolRegistryEntry sorts required_permissions."""
    entry = ToolRegistryEntry(
        tool_id="test_tool",
        kind=ToolKind.READ,
        input_schema_digest="digest1",
        output_schema_digest="digest2",
        required_permissions=("TOOL:WRITE", "TOOL:READ"),  # Unsorted
        owner_module="test_module",
    )
    
    assert entry.required_permissions == ("TOOL:READ", "TOOL:WRITE")  # Sorted


def test_tool_registry_entry_to_dict():
    """Test ToolRegistryEntry.to_dict serialization."""
    entry = ToolRegistryEntry(
        tool_id="test_tool",
        kind=ToolKind.WRITE,
        input_schema_digest="input_sha256",
        output_schema_digest="output_sha256",
        required_permissions=("TOOL:WRITE",),
        owner_module="test_module",
        deprecated=True,
    )
    
    d = entry.to_dict()
    assert d["tool_id"] == "test_tool"
    assert d["kind"] == "write"
    assert d["input_schema_digest"] == "input_sha256"
    assert d["output_schema_digest"] == "output_sha256"
    assert d["required_permissions"] == ["TOOL:WRITE"]
    assert d["owner_module"] == "test_module"
    assert d["deprecated"] is True


def test_prompt_role_enum_values():
    """Test PromptRole enum has expected values."""
    assert PromptRole.SYSTEM.value == "system"
    assert PromptRole.POLICY.value == "policy"
    assert PromptRole.RUBRIC.value == "rubric"
    assert PromptRole.TEMPLATE.value == "template"


def test_prompt_registry_entry_validation_requires_prompt_id():
    """Test PromptRegistryEntry requires prompt_id."""
    with pytest.raises(ValueError, match="prompt_id.*content_digest required"):
        PromptRegistryEntry(
            prompt_id="",
            role=PromptRole.SYSTEM,
            content_digest="digest1",
            policy_version="v4.0.0",
        )


def test_prompt_registry_entry_validation_requires_content_digest():
    """Test PromptRegistryEntry requires content_digest."""
    with pytest.raises(ValueError, match="prompt_id.*content_digest required"):
        PromptRegistryEntry(
            prompt_id="system_prompt",
            role=PromptRole.SYSTEM,
            content_digest="",
            policy_version="v4.0.0",
        )


def test_prompt_registry_entry_to_dict():
    """Test PromptRegistryEntry.to_dict serialization."""
    entry = PromptRegistryEntry(
        prompt_id="system_prompt",
        role=PromptRole.POLICY,
        content_digest="content_sha256",
        policy_version="v4.0.0",
        deprecated=True,
    )
    
    d = entry.to_dict()
    assert d["prompt_id"] == "system_prompt"
    assert d["role"] == "policy"
    assert d["content_digest"] == "content_sha256"
    assert d["policy_version"] == "v4.0.0"
    assert d["deprecated"] is True


def test_mcp_connector_registry_entry_validation_requires_connector_id():
    """Test MCPConnectorRegistryEntry requires connector_id."""
    with pytest.raises(ValueError, match="connector_id required"):
        MCPConnectorRegistryEntry(
            connector_id="",
            server_endpoint_digest="endpoint_sha256",
            schema_version="1.0",
            allowed_principals=(),
        )


def test_mcp_connector_registry_entry_validation_requires_endpoint_digest():
    """Test MCPConnectorRegistryEntry requires server_endpoint_digest."""
    with pytest.raises(ValueError, match="server_endpoint_digest required"):
        MCPConnectorRegistryEntry(
            connector_id="claude_mcp",
            server_endpoint_digest="",
            schema_version="1.0",
            allowed_principals=(),
        )


def test_mcp_connector_registry_entry_sorts_allowed_principals():
    """Test MCPConnectorRegistryEntry sorts allowed_principals."""
    entry = MCPConnectorRegistryEntry(
        connector_id="claude_mcp",
        server_endpoint_digest="endpoint_sha256",
        schema_version="1.0",
        allowed_principals=("user2@example.com", "user1@example.com"),  # Unsorted
    )
    
    assert entry.allowed_principals == ("user1@example.com", "user2@example.com")  # Sorted


def test_mcp_connector_principal_permitted(sample_principal_chain):
    """Test MCPConnectorRegistryEntry.principal_permitted method."""
    # Empty allowed_principals = any principal permitted
    entry = MCPConnectorRegistryEntry(
        connector_id="claude_mcp",
        server_endpoint_digest="endpoint_sha256",
        schema_version="1.0",
        allowed_principals=(),  # Empty = any
    )
    
    assert entry.principal_permitted(sample_principal_chain) is True
    
    # Specific principal allowed
    entry2 = MCPConnectorRegistryEntry(
        connector_id="claude_mcp",
        server_endpoint_digest="endpoint_sha256",
        schema_version="1.0",
        allowed_principals=("user@example.com",),
    )
    
    assert entry2.principal_permitted(sample_principal_chain) is True
    
    # Different principal not allowed
    other_chain = PrincipalChain(
        agent_id="other_agent",
        invoking_user="other@example.com",
        invoking_user_kind=InvokingUserKind.HUMAN,
        auth_method="oauth2",
        scope_tag="default",
    )
    
    assert entry2.principal_permitted(other_chain) is False


def test_mcp_connector_principal_permitted_user_kind_restriction(sample_principal_chain):
    """Test principal_permitted respects allowed_invoking_user_kinds."""
    entry = MCPConnectorRegistryEntry(
        connector_id="claude_mcp",
        server_endpoint_digest="endpoint_sha256",
        schema_version="1.0",
        allowed_principals=(),
        allowed_invoking_user_kinds=(InvokingUserKind.HUMAN,),
    )
    
    assert entry.principal_permitted(sample_principal_chain) is True
    
    # Automation user not allowed
    automation_chain = PrincipalChain(
        agent_id="automation_agent",
        invoking_user="automation@example.com",
        invoking_user_kind=InvokingUserKind.AUTOMATION,
        auth_method="oauth2",
        scope_tag="default",
    )
    
    assert entry.principal_permitted(automation_chain) is False


def test_mcp_connector_registry_entry_to_dict():
    """Test MCPConnectorRegistryEntry.to_dict serialization."""
    entry = MCPConnectorRegistryEntry(
        connector_id="claude_mcp",
        server_endpoint_digest="endpoint_sha256",
        schema_version="1.0",
        allowed_principals=("user@example.com",),
        allowed_invoking_user_kinds=(InvokingUserKind.HUMAN,),
        rate_limit_per_minute=120,
        deprecated=True,
    )
    
    d = entry.to_dict()
    assert d["connector_id"] == "claude_mcp"
    assert d["server_endpoint_digest"] == "endpoint_sha256"
    assert d["schema_version"] == "1.0"
    assert d["allowed_principals"] == ["user@example.com"]
    assert d["allowed_invoking_user_kinds"] == ["human"]
    assert d["rate_limit_per_minute"] == 120
    assert d["deprecated"] is True


def test_data_source_kind_enum_values():
    """Test DataSourceKind enum has expected values."""
    assert DataSourceKind.RAG_INDEX.value == "rag_index"
    assert DataSourceKind.KB_CORPUS.value == "kb_corpus"
    assert DataSourceKind.TRAINING_DATA.value == "training_data"
    assert DataSourceKind.POLICY_BUNDLE.value == "policy_bundle"
    assert DataSourceKind.RUBRIC_SET.value == "rubric_set"


def test_data_authority_record_validation_requires_source_id():
    """Test DataAuthorityRecord requires source_id."""
    with pytest.raises(ValueError, match="source_id required"):
        DataAuthorityRecord(
            source_id="",
            kind=DataSourceKind.RAG_INDEX,
            content_digest="content_sha256",
            supply_chain_attestation="attestation",
            expected_digest="expected_sha256",
            policy_version="v4.0.0",
        )


def test_data_authority_record_validation_requires_content_digest():
    """Test DataAuthorityRecord requires content_digest."""
    with pytest.raises(ValueError, match="content_digest required"):
        DataAuthorityRecord(
            source_id="test_source",
            kind=DataSourceKind.RAG_INDEX,
            content_digest="",
            supply_chain_attestation="attestation",
            expected_digest="expected_sha256",
            policy_version="v4.0.0",
        )


def test_data_authority_record_validation_requires_expected_digest():
    """Test DataAuthorityRecord requires expected_digest."""
    with pytest.raises(ValueError, match="expected_digest required"):
        DataAuthorityRecord(
            source_id="test_source",
            kind=DataSourceKind.RAG_INDEX,
            content_digest="content_sha256",
            supply_chain_attestation="attestation",
            expected_digest="",
            policy_version="v4.0.0",
        )


def test_data_authority_record_matches_pin():
    """Test DataAuthorityRecord.matches_pin property."""
    # Matching digests
    match_record = DataAuthorityRecord(
        source_id="test_source",
        kind=DataSourceKind.RAG_INDEX,
        content_digest="sha256",
        supply_chain_attestation="attestation",
        expected_digest="sha256",
        policy_version="v4.0.0",
    )
    
    assert match_record.matches_pin is True
    
    # Mismatched digests
    drift_record = DataAuthorityRecord(
        source_id="test_source",
        kind=DataSourceKind.RAG_INDEX,
        content_digest="different_sha256",
        supply_chain_attestation="attestation",
        expected_digest="sha256",
        policy_version="v4.0.0",
    )
    
    assert drift_record.matches_pin is False


def test_data_authority_record_to_dict():
    """Test DataAuthorityRecord.to_dict serialization."""
    record = DataAuthorityRecord(
        source_id="test_rag_index",
        kind=DataSourceKind.RAG_INDEX,
        content_digest="content_sha256",
        supply_chain_attestation="slsa_provenance",
        expected_digest="expected_sha256",
        policy_version="v4.0.0",
    )
    
    d = record.to_dict()
    assert d["source_id"] == "test_rag_index"
    assert d["kind"] == "rag_index"
    assert d["content_digest"] == "content_sha256"
    assert d["expected_digest"] == "expected_sha256"
    assert d["policy_version"] == "v4.0.0"
    assert d["matches_pin"] is False
    assert d["supply_chain_attestation"] == "slsa_provenance"


def test_data_authority_resolution_to_dict():
    """Test DataAuthorityResolution.to_dict serialization."""
    resolution = DataAuthorityResolution(
        records=(),
        all_match=True,
        drifts=(),
    )
    
    d = resolution.to_dict()
    assert d["all_match"] is True
    assert d["records"] == []
    assert d["drifts"] == []


def test_registry_snapshot_validation_requires_policy_version(sample_agent_registry_entry):
    """Test RegistrySnapshot requires policy_version."""
    with pytest.raises(ValueError, match="policy_version required"):
        RegistrySnapshot(
            policy_version="",
            agents=(sample_agent_registry_entry,),
            tools=(),
            prompts=(),
            connectors=(),
            registry_digest="digest",
        )


def test_registry_snapshot_validation_requires_registry_digest(sample_agent_registry_entry):
    """Test RegistrySnapshot requires registry_digest."""
    with pytest.raises(ValueError, match="registry_digest required"):
        RegistrySnapshot(
            policy_version="v4.0.0",
            agents=(sample_agent_registry_entry,),
            tools=(),
            prompts=(),
            connectors=(),
            registry_digest="",
        )


def test_registry_snapshot_to_json(sample_registry_snapshot):
    """Test RegistrySnapshot.to_json returns canonical JSON."""
    json_str = sample_registry_snapshot.to_json()
    
    assert isinstance(json_str, str)
    assert "policy_version" in json_str
    assert "agents" in json_str
    assert "tools" in json_str
    assert "prompts" in json_str
    assert "connectors" in json_str
