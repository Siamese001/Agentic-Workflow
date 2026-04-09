"""GraphDB Schema - Mapping from ADG canonical entities to graph projection.

This module defines the mapping between ADG entity/relation types and
graph projection node/edge types, along with property schemas.
"""

from __future__ import annotations

from typing import Dict, List, Literal

# ---------------------------------------------------------------------------
# Node Type Mapping
# ---------------------------------------------------------------------------

NODE_TYPE_MAPPING: Dict[str, str] = {
    # Core entities
    "module": "Module",
    "symbol": "Symbol",
    "layer": "Layer",
    "agent": "Agent",
    "tool": "Tool",
    "gateway": "Gateway",
    "provider": "Provider",
    "datastore": "DataStore",
    # Governance entities
    "policy": "PolicySurface",
    "decision": "DecisionPoint",
    "retrieval_component": "RetrievalComponent",
    "seam": "Seam",
    # Runtime entities
    "scan_run": "Snapshot",
    "commit": "Commit",
    "prompt_slot": "PromptSlot",
    "prompt_template": "PromptTemplate",
    # Extended entities (grouped by category)
    "validator_node": "Validator",
    "healer_agent": "Healer",
    "embedding_store": "Store",
    "chunk_pipeline": "Processor",
    "retrieval_endpoint": "Endpoint",
    "hitl_checkpoint": "Checkpoint",
    "confidence_gate": "Gate",
    "human_decision": "Human",
    "guardrail": "Guardrail",
    "policy_enforcer": "Enforcer",
    "antipattern_record": "AntiPattern",
    "test_suite": "TestSuite",
    "test_case": "TestCase",
    "invariant_family": "InvariantFamily",
    "healing_run": "HealingRun",
    "orchestration_step": "OrchestrationStep",
    "nondeterminism_site": "NondeterminismSite",
    "wall_clock_call": "WallClockCall",
    "random_call_site": "RandomCallSite",
    "uuid_call_site": "UUIDCallSite",
    "external_call_site": "ExternalCallSite",
    "http_egress_node": "HTTPEgressNode",
    "agent_dispatch_edge": "AgentDispatchEdge",
    "agent_invocation_record": "AgentInvocationRecord",
    "registry_validation_record": "RegistryValidationRecord",
    "safety_plane_proof": "SafetyPlaneProof",
    "llm_gateway_proof": "LLMGatewayProof",
    "uwg_termination_proof": "UWGTerminationProof",
    "policy_hash_reference": "PolicyHashReference",
    "routing_commit_record": "RoutingCommitRecord",
    "prompt_provenance_record": "PromptProvenanceRecord",
    "preference_pair_artifact": "PreferencePairArtifact",
    "human_review_record": "HumanReviewRecord",
}

# ---------------------------------------------------------------------------
# Edge Type Mapping
# ---------------------------------------------------------------------------

EDGE_TYPE_MAPPING: Dict[str, str] = {
    # Structural edges
    "imports": "IMPORTS",
    "calls": "CALLS",
    "implements": "IMPLEMENTS",
    "belongs_to_layer": "BELONGS_TO_LAYER",
    "instantiates": "INSTANTIATES",
    "inherits": "INHERITS",
    # Data flow edges
    "reads_from": "READS_FROM",
    "writes_to": "WRITES_TO",
    "routes_through": "ROUTES_THROUGH",
    "writes_through": "WRITES_THROUGH",
    # Control flow edges
    "invokes_provider": "INVOKES_PROVIDER",
    "produces": "PRODUCES",
    "consumes": "CONSUMES",
    "influences": "INFLUENCES",
    "controls_flow": "CONTROLS_FLOW",
    "flows_to": "FLOWS_TO",
    # Context and retrieval edges
    "pulls_context": "PULLS_CONTEXT",
    "retrieves_via": "RETRIEVES_VIA",
    # Prompt edges
    "generates_prompt": "GENERATES_PROMPT",
    "consumes_prompt": "CONSUMES_PROMPT",
    "assembles_into": "ASSEMBLES_INTO",
    "injects_into": "INJECTS_INTO",
    "overrides_prompt": "OVERRIDES_PROMPT",
    "executed_with_prompt": "EXECUTED_WITH_PROMPT",
    # Governance edges
    "violates": "VIOLATES",
    "validates": "VALIDATES",
    "applies_guardrail": "APPLIES_GUARDRAIL",
    "verifies_policy": "VERIFIES",
    "escalates_to": "ESCALATES_TO",
    "heals": "HEALS",
    "orchestrates_healing": "ORCHESTRATES_HEALING",
    # Trace edges
    "emits_trace": "EMITS_TRACE",
    "lineage_of": "LINEAGE_OF",
    "antipattern": "ANTIPATTERN",
    "evaluates": "EVALUATES",
    # Additional edges from full ADG schema
    "invokes_dynamic": "INVOKES_DYNAMIC",
    "decorated_by": "DECORATED_BY",
    "bypasses": "BYPASSES",
    "seam_bypass": "SEAM_BYPASS",
    "allows": "ALLOWS",
    "covers": "COVERS",
    "exports": "EXPORTS",
    "re_exports": "RE_EXPORTS",
    "in_cycle": "IN_CYCLE",
    "dead_imports": "DEAD_IMPORTS",
    "reads_env": "READS_ENV",
    "reads_secret": "READS_SECRET",
    "reads_policy_state": "READS_POLICY_STATE",
    "reads_runtime_state": "READS_RUNTIME_STATE",
    "reads_config": "READS_CONFIG",
    "triggered_telemetry": "TRIGGERED_TELEMETRY",
    "proposed_improvement": "PROPOSED_IMPROVEMENT",
    "updated_prompt": "UPDATED_PROMPT",
    "executes_action": "EXECUTES_ACTION",
    "invokes_tool": "INVOKES_TOOL",
    "crosses_layer": "CROSSES_LAYER",
    "bypasses_uwg": "BYPASSES_UWG",
    "routes_through_uwg": "ROUTES_THROUGH_UWG",
    "layer_authority_violation": "LAYER_AUTHORITY_VIOLATION",
    "policy_hash_mismatch": "POLICY_HASH_MISMATCH",
    "dispatches_to": "DISPATCHES_TO",
    "embeds_into": "EMBEDS_INTO",
    "retrieves_from_store": "RETRIEVES_FROM_STORE",
    "enriches_chunk": "ENRICHES_CHUNK",
    "routes_retrieval": "ROUTES_RETRIEVAL",
    "applies_retrieval_guardrail": "APPLIES_RETRIEVAL_GUARDRAIL",
    "indexes_for_retrieval": "INDEXES_FOR_RETRIEVAL",
    "chunks_into": "CHUNKS_INTO",
    "stores_embedding": "STORES_EMBEDDING",
    "escalates_to_human": "ESCALATES_TO_HUMAN",
    "awaits_approval": "AWAITS_APPROVAL",
    "learns_from_decision": "LEARNS_FROM_DECISION",
    "gated_by_confidence": "GATED_BY_CONFIDENCE",
    "enforces_policy_hash": "ENFORCES_POLICY_HASH",
    "registered_as": "REGISTERED_AS",
    "has_capability": "HAS_CAPABILITY",
    "depends_on_agent": "DEPENDS_ON_AGENT",
    "stamps_work_contract": "STAMPS_WORK_CONTRACT",
    "issues_capability_token": "ISSUES_CAPABILITY_TOKEN",
}

# ---------------------------------------------------------------------------
# Node Properties Schema
# ---------------------------------------------------------------------------

NODE_PROPERTIES: Dict[str, List[str]] = {
    "Module": ["file_path", "layer", "is_test", "is_production", "line_count"],
    "Symbol": ["name", "symbol_type", "file_path", "line_number", "is_exported"],
    "Layer": ["name", "level", "description"],
    "Agent": ["name", "file_path", "class_name"],
    "Tool": ["name", "module_path"],
    "Gateway": ["name", "class_name", "file_path"],
    "Provider": ["name", "interface", "module_path"],
    "DataStore": ["name", "type", "connection_string"],
    "PolicySurface": ["policy_id", "description", "severity"],
    "DecisionPoint": ["name", "description", "outcome_type"],
    "RetrievalComponent": ["name", "type", "endpoint"],
    "Seam": ["name", "boundary_type", "enforcement_level"],
    "Snapshot": ["commit_sha", "timestamp", "run_id", "scanner_version"],
    "Commit": ["sha", "message", "author", "timestamp"],
    "PromptSlot": ["name", "type", "required"],
    "PromptTemplate": ["name", "version", "template_type"],
    "Validator": ["name", "validation_type", "rules"],
    "Healer": ["name", "healing_type", "capabilities"],
    "Store": ["name", "store_type", "endpoint"],
    "Processor": ["name", "processor_type", "config"],
    "Endpoint": ["name", "endpoint_type", "url"],
    "Checkpoint": ["name", "checkpoint_type", "conditions"],
    "Gate": ["name", "gate_type", "threshold"],
    "Human": ["name", "role", "decision_scope"],
    "Guardrail": ["name", "guard_type", "enforcement"],
    "Enforcer": ["name", "enforcement_type", "scope"],
    "AntiPattern": ["name", "category", "severity"],
    "TestSuite": ["name", "test_type", "coverage"],
    "TestCase": ["name", "test_method", "assertions"],
}

# ---------------------------------------------------------------------------
# Edge Properties Schema
# ---------------------------------------------------------------------------

EDGE_PROPERTIES: Dict[str, List[str]] = {
    "IMPORTS": ["line_number", "is_dynamic", "is_conditional"],
    "CALLS": ["line_number", "is_async", "call_type"],
    "IMPLEMENTS": ["line_number", "implementation_type"],
    "BELONGS_TO_LAYER": ["layer_level", "assignment_type"],
    "INSTANTIATES": ["line_number", "instantiation_type"],
    "INHERITS": ["line_number", "inheritance_type"],
    "READS_FROM": ["line_number", "read_type", "is_conditional"],
    "WRITES_TO": ["line_number", "write_type", "is_atomic"],
    "ROUTES_THROUGH": ["gateway_type", "checkpoint_id"],
    "WRITES_THROUGH": ["gateway_type", "bypass_type"],
    "INVOKES_PROVIDER": ["provider_type", "call_context"],
    "PRODUCES": ["production_type", "cardinality"],
    "CONSUMES": ["consumption_type", "dependency_type"],
    "INFLUENCES": ["influence_type", "strength"],
    "CONTROLS_FLOW": ["control_type", "conditionality"],
    "FLOWS_TO": ["flow_type", "medium"],
    "PULLS_CONTEXT": ["context_type", "scope"],
    "RETRIEVES_VIA": ["retrieval_method", "endpoint"],
    "GENERATES_PROMPT": ["prompt_type", "template_id"],
    "CONSUMES_PROMPT": ["prompt_type", "template_id"],
    "VIOLATES": ["policy_id", "severity", "description"],
    "VALIDATES": ["validation_type", "rules"],
    "APPLIES_GUARDRAIL": ["guardrail_type", "enforcement"],
    "VERIFIES": ["verification_type", "conditions"],
    "ESCALATES_TO": ["escalation_type", "severity"],
    "HEALS": ["healing_type", "strategy"],
    "ORCHESTRATES_HEALING": ["orchestration_type", "scope"],
    "EMITS_TRACE": ["trace_type", "trace_id"],
    "LINEAGE_OF": ["lineage_type", "generation"],
    "ANTIPATTERN": ["antipattern_type", "category"],
    "EVALUATES": ["evaluation_type", "metric"],
}

# ---------------------------------------------------------------------------
# Type Aliases
# ---------------------------------------------------------------------------

GraphNodeType = Literal[tuple(NODE_TYPE_MAPPING.values())]
GraphEdgeType = Literal[tuple(EDGE_TYPE_MAPPING.values())]

# ---------------------------------------------------------------------------
# Validation Functions
# ---------------------------------------------------------------------------


def validate_node_type(node_type: str) -> str:
    """Validate and normalize node type."""
    if node_type not in NODE_TYPE_MAPPING:
        raise ValueError(f"Unknown node type: {node_type}")
    return NODE_TYPE_MAPPING[node_type]


def validate_edge_type(edge_type: str) -> str:
    """Validate and normalize edge type."""
    if edge_type not in EDGE_TYPE_MAPPING:
        raise ValueError(f"Unknown edge type: {edge_type}")
    return EDGE_TYPE_MAPPING[edge_type]


def get_node_properties(node_type: str) -> List[str]:
    """Get property schema for a node type."""
    graph_type = validate_node_type(node_type)
    return NODE_PROPERTIES.get(graph_type, [])


def get_edge_properties(edge_type: str) -> List[str]:
    """Get property schema for an edge type."""
    graph_type = validate_edge_type(edge_type)
    return EDGE_PROPERTIES.get(graph_type, [])
