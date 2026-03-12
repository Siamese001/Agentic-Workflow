"""ADG schema: entity types, relation types, edge kinds, and naming conventions.

All ADG entities use the ADG:: namespace prefix to avoid collisions with other
Memory MCP uses.

Naming convention:
    ADG::Module::<forward/slash/path>
    ADG::Symbol::<qualified.symbol.name>
    ADG::Layer::L0 ... ADG::Layer::L6
    ADG::Commit::<40-hex-sha>
    ADG::Snapshot::<40-hex-sha>::<digest>
    ADG::Gateway::<ClassName>
    ADG::Policy::<POLICY_ID>
    ADG::Decision::<DecisionName>
    ADG::Retrieval::<ComponentName>
    ADG::Run::<run_id>
    ADG::Cycle::<hash_of_members>
"""

from __future__ import annotations

from typing import Literal

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

ADG_NS = "ADG"

EntityType = Literal[
    "module",
    "symbol",
    "layer",
    "seam",
    "agent",
    "tool",
    "gateway",
    "provider",
    "datastore",
    "side_effect_endpoint",
    "retrieval_component",
    "decision_point",
    "policy",
    "commit",
    "snapshot",
    "scan_run",
    # P6: Prompt governance
    "prompt_slot",
    "prompt_template",
    "prompt_assembly",
    # P7: Observability
    "execution_trace",
    # P3: Runtime graph
    "agent_action",
    "tool_invocation",
    "layer_transition",
    "mutation_record",
    # G1 (gap): Runtime behavior plane
    "healing_loop",
    "validator_node",
    "healer_agent",
    # G3 (gap): Embedding pipeline nodes
    "embedding_store",
    "chunk_pipeline",
    "retrieval_endpoint",
    # G4 (gap): HITL nodes
    "hitl_checkpoint",
    "confidence_gate",
    "human_decision",
    # G5 (gap): Safety enforcement nodes
    "guardrail",
    "policy_enforcer",
    # G6 (gap): Agent registry
    "agent_registration",
    "agent_capability",
    # G7 (gap): Sandbox airlock / work-contract
    "sandbox_envelope",
    "capability_token",
    "work_contract",
    # G8 (gap): Capability-token / tool-budget
    "tool_budget",
    "resource_grant",
    # G9 (gap): JIT context sync / freeze
    "jit_context_snapshot",
    "freeze_boundary",
    # G10 (gap): Boundary verification
    "boundary_checkpoint",
    "capability_chokepoint",
    # G11 (gap): Determinism control
    "semantic_clock",
    "replay_guard",
    "rng_seed",
    # G12 (gap): Network / I/O interception
    "io_intercept",
    "network_transcript",
    # G13 (gap): Mutation transport / commit
    "mutation_packet",
    "commit_protocol",
    # G14 (gap): Execution trace / proof
    "execution_proof",
    "determinism_digest",
    # G15 (gap): Path control
    "execution_path",
    "path_reroute",
    # G16 (gap): Evaluation / optimization spine
    "eval_metric",
    "dpo_batch",
    "drift_alert",
    # G17 (gap): Secret / credential access
    "secret_access_record",
    "credential_vault",
    "secret_read_event",
    # G18 (gap): Config governance
    "config_read_record",
    "config_policy_gate",
    # G19 (gap): Dynamic invocation
    "dynamic_invocation_record",
    "eval_exec_site",
    # G20 (gap): Policy state observation
    "policy_state_read",
    "runtime_state_read",
    "state_observation_report",
    # G21 (gap): Anti-pattern registry
    "antipattern_record",
    "antipattern_category",
    # G22 (gap): Healing orchestrator
    "healing_run",
    "orchestration_step",
    # G23 (gap): Non-determinism primitive detection
    "nondeterminism_site",
    "wall_clock_call",
    "random_call_site",
    "uuid_call_site",
    # G24 (gap): External HTTP / network call
    "external_call_site",
    "http_egress_node",
    # G25 (gap): Agent-to-agent dispatch
    "agent_dispatch_edge",
    "agent_invocation_record",
    # G26 (gap): L5 validation proof
    "registry_validation_record",
    "safety_plane_proof",
    "llm_gateway_proof",
    "uwg_termination_proof",
    "policy_hash_reference",
    # G27 (gap): Learning / prompt provenance
    "routing_commit_record",
    "prompt_provenance_record",
    "preference_pair_artifact",
    "human_review_record",
]

RelationType = Literal[
    "imports",
    "calls",
    "belongs_to_layer",
    "implements",
    "routes_through",
    "writes_through",
    "reads_from",
    "writes_to",
    "invokes_provider",
    "invokes_dynamic",
    "instantiates",
    "produces",
    "consumes",
    "influences",
    "decorated_by",
    "bypasses",
    "violates",
    "seam_bypass",
    "allows",
    "covers",
    "exports",
    "re_exports",
    "in_cycle",
    "dead_imports",
    # G6: Reads subtype relations (replaces coarse reads_from edge_kind)
    "reads_env",
    "reads_secret",
    "reads_policy_state",
    "reads_runtime_state",
    "reads_config",
    # P6: Prompt governance
    "generates_prompt",
    "consumes_prompt",
    "assembles_into",
    "injects_into",
    "overrides_prompt",
    # P7: Observability
    "executed_with_prompt",
    "triggered_telemetry",
    "proposed_improvement",
    "updated_prompt",
    # P3: Runtime graph / authority / mutation
    "executes_action",
    "invokes_tool",
    "crosses_layer",
    "bypasses_uwg",
    "routes_through_uwg",
    "layer_authority_violation",
    "policy_hash_mismatch",
    "lineage_of",
    # GA: Behavioral anti-pattern detection (AST-based)
    "antipattern",
    # G1 (gap): Runtime behavior plane — healer/validator loop
    "heals",
    "validates",
    "orchestrates_healing",
    "dispatches_to",
    # G2 (gap): Extended prompt governance
    "assembles_into",
    "injects_into",
    "overrides_prompt",
    # G3 (gap): Embedding / knowledge graph
    "embeds_into",
    "retrieves_via",
    "chunks_into",
    "stores_embedding",
    # G4 (gap): HITL / confidence-threshold gating
    "escalates_to_human",
    "awaits_approval",
    "learns_from_decision",
    "gated_by_confidence",
    # G5 (gap): Safety enforcement runtime
    "applies_guardrail",
    "verifies_policy",
    "enforces_policy_hash",
    # G6 (gap): Agent registry / capability graph
    "registered_as",
    "has_capability",
    "depends_on_agent",
    # G7 (gap): Sandbox airlock / work-contract
    "stamps_work_contract",
    "issues_capability_token",
    "enters_sandbox",
    "exits_sandbox",
    # G8 (gap): Capability-token / tool-budget
    "consumes_budget",
    "grants_resource",
    "exceeds_budget",
    # G9 (gap): JIT context sync / freeze
    "pulls_context",
    "freezes_context",
    "unfreezes_context",
    # G10 (gap): Boundary verification
    "verifies_boundary",
    "rejects_packet",
    "certifies_envelope",
    # G11 (gap): Determinism control
    "seeds_rng",
    "patches_time",
    "guards_replay",
    "emits_determinism_digest",
    # G12 (gap): Network / I/O interception
    "intercepts_io",
    "transcripts_response",
    "hard_fails_untranscripted",
    # G13 (gap): Mutation transport / commit
    "packages_diff",
    "validates_blast_radius",
    "signs_execution_trace",
    "commits_mutation",
    "distributes_mutation",
    # G14 (gap): Execution trace / proof
    "records_execution_trace",
    "emits_replay_key",
    "compares_proof",
    # G15 (gap): Path control
    "routes_path",
    "forces_stall",
    "reenters_safety",
    "vigilance_reroute",
    # G16 (gap): Evaluation / optimization spine
    "scores_groundedness",
    "emits_drift_alert",
    "builds_dpo_batch",
    "commits_optimization",
    # G17 (gap): Secret / credential access
    "reads_secret_vault",
    "accesses_credential",
    "rotates_secret",
    # G18 (gap): Config governance
    "reads_governed_config",
    "validates_config_schema",
    "caches_config",
    # G19 (gap): Dynamic invocation
    "invokes_eval",
    "invokes_exec",
    "invokes_importlib",
    "invokes_getattr_dynamic",
    # G20 (gap): Policy state observation
    "observes_policy_state",
    "observes_runtime_state",
    "snapshots_state",
    # G21 (gap): Anti-pattern registry
    "registers_antipattern",
    "classifies_antipattern",
    # G22 (gap): Healing orchestrator
    "dispatches_healing_run",
    "confirms_heal",
    "aborts_heal",
    # G23 (gap): Non-determinism primitive detection
    "uses_wall_clock",
    "uses_random",
    "uses_uuid",
    # G24 (gap): External HTTP / network egress
    "external_http_call",
    # G25 (gap): Agent-to-agent dispatch
    "agent_executes_agent",
    # G26 (gap): L5 validation proof edges
    "validated_by_registry",
    "validated_by_safety_plane",
    "validated_by_llm_gateway",
    "execution_terminates_at_uwg",
    "references_policy_hash",
    # G27 (gap): Learning / prompt provenance
    "proposal_commits_routing",
    "prompt_template_used_by",
    "instruction_injection_source",
    "produces_preference_pair",
    "requires_human_review",
]

EdgeKind = Literal[
    "import",
    "call",
    "write",
    "network",
    "embedding",
    "retrieval",
    "decision",
    "dead_import",
    "star_import",
    "cycle",
    "export",
    "re_export",
    "decorator",
    "type_checking_import",
    "optional_import",
    "version_guard_import",
    "type_annotation",
    # P6: Prompt governance
    "prompt_generation",
    "prompt_consumption",
    "prompt_assembly",
    "prompt_injection",
    "prompt_authority_violation",
    # P7: Observability
    "trace_prompt_link",
    "prompt_drift",
    # P3: Runtime graph / authority / mutation
    "agent_execution",
    "tool_call",
    "layer_boundary_cross",
    "uwg_bypass",
    "uwg_compliant_write",
    "authority_violation",
    "policy_validation",
    "state_lineage",
    # GA: Behavioral anti-pattern edge kinds
    "silent_exception_swallow",
    "blocking_call_in_async",
    "global_state_mutation",
    "retry_without_backoff",
    # G1 (gap): Healer/validator loop
    "healer_action",
    "validator_check",
    "healing_dispatch",
    # G3 (gap): Embedding pipeline
    "embedding_pipeline",
    "retrieval_pipeline",
    "chunking_pipeline",
    # G4 (gap): HITL
    "hitl_escalation",
    "confidence_gate",
    "approval_wait",
    # G5 (gap): Safety enforcement
    "guardrail_execution",
    "policy_verification",
    # G6 (gap): Agent registry
    "agent_registration",
    # G7 (gap): Sandbox airlock
    "sandbox_entry",
    "sandbox_exit",
    "work_contract_stamp",
    "capability_token_issue",
    # G8 (gap): Tool budget
    "budget_grant",
    "budget_exceeded",
    # G9 (gap): JIT freeze
    "context_pull",
    "context_freeze",
    # G10 (gap): Boundary verification
    "boundary_accept",
    "boundary_reject",
    # G11 (gap): Determinism
    "determinism_seed",
    "replay_patch",
    "determinism_digest_emit",
    # G12 (gap): IO interception
    "io_transcript",
    "io_hard_fail",
    # G13 (gap): Mutation transport
    "diff_package",
    "blast_radius_check",
    "two_phase_commit",
    "mutation_distribution",
    # G14 (gap): Execution proof
    "execution_trace_record",
    "replay_key_emit",
    "proof_comparison",
    # G15 (gap): Path control
    "path_route",
    "path_stall",
    "path_safety_reentry",
    "path_vigilance_reroute",
    # G16 (gap): Evaluation spine
    "eval_score",
    "drift_alert",
    "dpo_build",
    "optimization_commit",
    # G17 (gap): Secret / credential access
    "secret_read",
    "credential_access",
    "secret_rotation",
    # G18 (gap): Config governance
    "governed_config_read",
    "config_schema_validation",
    # G19 (gap): Dynamic invocation
    "eval_call",
    "exec_call",
    "importlib_call",
    "dynamic_getattr",
    # G20 (gap): Policy state observation
    "policy_state_observation",
    "runtime_state_snapshot",
    # G21 (gap): Anti-pattern registry
    "antipattern_classification",
    # G22 (gap): Healing orchestrator
    "healing_dispatch",
    "healing_confirm",
    "healing_abort",
    # G23 (gap): Non-determinism primitive detection
    "wall_clock_use",
    "random_use",
    "uuid_use",
    # G24 (gap): External HTTP
    "http_egress_call",
    # G25 (gap): Agent-to-agent dispatch
    "agent_dispatch",
    # G26 (gap): L5 validation proof
    "registry_validation",
    "safety_plane_validation",
    "llm_gateway_validation",
    "uwg_termination",
    "policy_hash_link",
    # G27 (gap): Learning / prompt provenance
    "routing_commit",
    "prompt_template_link",
    "injection_source_link",
    "preference_pair_link",
    "human_review_gate",
]


# P6: Prompt slot authority ordering (S0 highest authority → U0 lowest)
PROMPT_SLOT_TYPES: tuple[str, ...] = ("S0", "D0", "I0", "C0", "U0")
PROMPT_SLOT_AUTHORITY: dict[str, int] = {slot: i for i, slot in enumerate(PROMPT_SLOT_TYPES)}

# P6: Authority hierarchy — high-authority slots that low-authority slots must not override
PROMPT_AUTHORITY_RULES: tuple[tuple[str, str], ...] = (
    ("U0", "S0"),  # user must not mutate system
    ("U0", "D0"),  # user must not mutate injection fences
    ("U0", "I0"),  # user must not mutate instructional
    ("C0", "S0"),  # context must not mutate system
    ("C0", "D0"),  # context must not introduce injection fences
    ("I0", "S0"),  # instructional must not mutate system
)

# P6: Prompt slot field names in GovernedPayload → slot type mapping
PROMPT_FIELD_TO_SLOT: dict[str, str] = {
    "s0_system": "S0",
    "d0_injections": "D0",
    "i0_instructional": "I0",
    "c0_context": "C0",
    "u0_user_prompt": "U0",
}

# P3: UWG canonical symbol — all writes_through must target this
UWG_CANONICAL_SYMBOL: str = "ADG::Symbol::UniversalWriteGateway"
UWG_MODULE_PATH: str = "agentic_core/L2_execution/UniversalWriteGateway.py"
UWG_INTERFACE_PATH: str = "agentic_core/interfaces/write_gateway.py"

# P3: Layer authority rules — which relations are FORBIDDEN per layer
# Format: layer_prefix → frozenset of forbidden relation_types
LAYER_AUTHORITY_FORBIDDEN: dict[str, frozenset[str]] = {
    "L1": frozenset({"writes_to", "writes_through"}),  # L1 must not mutate state
    "L3": frozenset({"invokes_tool", "invokes_provider"}),  # L3 must not directly invoke tools
    "L4": frozenset({"calls", "invokes_provider"}),  # L4 must not contain business logic
    "L6": frozenset({"writes_to", "writes_through", "routes_through"}),  # L6 must not alter execution
}

# P3: L1 write symbols that are allowlisted (self-copies, not persistent mutations)
L1_WRITE_ALLOWLIST: frozenset[str] = frozenset(
    {
        "copy",
        "output.copy",
        "self.strategy_weights.copy",
        "copy.deepcopy",
        "self.guardrails._cache_sizes.copy",
        "visited.copy",
    }
)

# P3: UWG write symbols (compliant write targets)
UWG_WRITE_SYMBOLS: frozenset[str] = frozenset(
    {
        "UniversalWriteGateway",
        "uwg.write",
        "uwg.write_bytes",
        "write_gateway.write_text",
        "write_gateway.write_bytes",
    }
)


def canonical_name(entity_type: str, *parts: str) -> str:
    """Build a canonical ADG entity name.

    Examples:
        canonical_name("Module", "agentic_core/L0_routing/engines/path_router.py")
        canonical_name("Layer", "L0")
        canonical_name("Commit", "abcdef1234567890abcdef1234567890abcdef12")
        canonical_name("Snapshot", sha, digest)
    """
    safe_parts = [p.replace("\\", "/") for p in parts]
    return "::".join([ADG_NS, entity_type] + safe_parts)


LAYER_PREFIXES: dict[str, str] = {
    "agentic_core/L0_routing": "L0",
    "agentic_core/L1_cognition": "L1",
    "agentic_core/L2_execution": "L2",
    "agentic_core/L3_orchestration": "L3",
    "agentic_core/L4_state": "L4",
    "agentic_core/L5_safety": "L5",
    "agentic_core/L6_observability": "L6",
    # G11: previously L_UNKNOWN subdirs now mapped to L_SHARED
    "agentic_core/_compat": "L_SHARED",
    "agentic_core/embeddings": "L_SHARED",
    "agentic_core/enforcement": "L_SHARED",
    # H2: previously L_UNKNOWN subdirs now mapped to named labels
    "agentic_core/base_agents": "L_SHARED",
    "agentic_core/interfaces": "L_SHARED",
    "agentic_core/config": "L_SHARED",
    "agentic_core/mixins": "L_SHARED",
    "agentic_core/utils": "L_SHARED",
    "agentic_core/seams": "L_SHARED",
    "agentic_core/cache": "L_SHARED",
    "agentic_core/agents": "L_SHARED",
    "agentic_core/evaluation": "L_SHARED",
    "agentic_core/runtime": "L_RUNTIME",
    "agentic_core/prompt_governance": "L_PG",
    "agentic_core/knowledge": "L_PG",
    "agentic_core/adg": "L_TOOLS",
    # App and infra layers
    "apps_rg": "L_APP",
    "apps_lic": "L_APP",
    "apps_shared": "L_APP",
    "system_learning": "L_SL",
    "tools": "L_TOOLS",
    "ops_scripts": "L_OPS",
    "tests": "L_TEST",
}

ALLOWED_LAYER_EDGES: frozenset[tuple[str, str]] = frozenset(
    {
        # Core downward edges
        ("L6", "L5"),
        ("L6", "L4"),
        ("L6", "L3"),
        ("L6", "L2"),
        ("L6", "L1"),
        ("L6", "L0"),
        ("L5", "L4"),
        ("L5", "L3"),
        ("L5", "L2"),
        ("L5", "L1"),
        ("L5", "L0"),
        ("L4", "L3"),
        ("L4", "L2"),
        ("L4", "L1"),
        ("L4", "L0"),
        ("L3", "L2"),
        ("L3", "L1"),
        ("L3", "L0"),
        ("L2", "L1"),
        ("L2", "L0"),
        ("L1", "L0"),
        # App layer
        ("L_APP", "L6"),
        ("L_APP", "L5"),
        ("L_APP", "L4"),
        ("L_APP", "L3"),
        ("L_APP", "L2"),
        ("L_APP", "L1"),
        ("L_APP", "L0"),
        # System learning
        ("L_SL", "L2"),
        ("L_SL", "L1"),
        ("L_SL", "L0"),
        # Tools
        ("L_TOOLS", "L5"),
        ("L_TOOLS", "L4"),
        ("L_TOOLS", "L3"),
        ("L_TOOLS", "L2"),
        ("L_TOOLS", "L1"),
        ("L_TOOLS", "L0"),
        # Ops
        ("L_OPS", "L5"),
        ("L_OPS", "L4"),
        ("L_OPS", "L3"),
        ("L_OPS", "L2"),
        ("L_OPS", "L1"),
        ("L_OPS", "L0"),
        # H2: L_SHARED importable from all named layers (it's a shared utility layer)
        ("L0", "L_SHARED"),
        ("L1", "L_SHARED"),
        ("L2", "L_SHARED"),
        ("L3", "L_SHARED"),
        ("L4", "L_SHARED"),
        ("L5", "L_SHARED"),
        ("L6", "L_SHARED"),
        ("L_APP", "L_SHARED"),
        ("L_SL", "L_SHARED"),
        ("L_TOOLS", "L_SHARED"),
        ("L_OPS", "L_SHARED"),
        ("L_RUNTIME", "L_SHARED"),
        ("L_PG", "L_SHARED"),
        ("L_TEST", "L_SHARED"),
        # H2: L_RUNTIME importable from L3+
        ("L3", "L_RUNTIME"),
        ("L4", "L_RUNTIME"),
        ("L5", "L_RUNTIME"),
        ("L6", "L_RUNTIME"),
        ("L_APP", "L_RUNTIME"),
        # H2: L_PG importable from L1+
        ("L1", "L_PG"),
        ("L2", "L_PG"),
        ("L3", "L_PG"),
        ("L4", "L_PG"),
        ("L5", "L_PG"),
        ("L6", "L_PG"),
        ("L_APP", "L_PG"),
        # L_TEST can import anything (test files are unrestricted consumers)
        ("L_TEST", "L0"),
        ("L_TEST", "L1"),
        ("L_TEST", "L2"),
        ("L_TEST", "L3"),
        ("L_TEST", "L4"),
        ("L_TEST", "L5"),
        ("L_TEST", "L6"),
        ("L_TEST", "L_APP"),
        ("L_TEST", "L_SL"),
        ("L_TEST", "L_TOOLS"),
        ("L_TEST", "L_OPS"),
        ("L_TEST", "L_RUNTIME"),
        ("L_TEST", "L_PG"),
        # L_TOOLS can import L_SHARED
        ("L_TOOLS", "L_SHARED"),
        # L_OPS can import L_SHARED + L_TOOLS
        ("L_OPS", "L_SHARED"),
        ("L_OPS", "L_TOOLS"),
        # L_SHARED internal cross-imports allowed
        ("L_SHARED", "L_SHARED"),
        # L_RUNTIME can import L0-L2
        ("L_RUNTIME", "L0"),
        ("L_RUNTIME", "L1"),
        ("L_RUNTIME", "L2"),
        # L_PG can import L0-L1
        ("L_PG", "L0"),
        ("L_PG", "L1"),
    }
)


def verify_layer_graph_consistency(module_layer_map: dict[str, str]) -> list[str]:
    """S4: Verify every module has exactly one layer label (no L_UNKNOWN remaining).

    Returns list of error strings; empty list means consistent.
    """
    errors: list[str] = []
    for module, layer in sorted(module_layer_map.items()):
        if layer == "L_UNKNOWN":
            errors.append(f"L_UNKNOWN module (unmapped): {module}")
    return errors


def module_path_to_layer(rel_path: str) -> str:
    """Map a repo-relative module path (forward slashes) to a layer label."""
    norm = rel_path.replace("\\", "/")
    for prefix, layer in sorted(LAYER_PREFIXES.items(), key=lambda kv: -len(kv[0])):
        if norm.startswith(prefix):
            return layer
    return "L_UNKNOWN"


# G9: Path patterns that identify architectural seam modules
SEAM_MODULE_PATTERNS: tuple[str, ...] = (
    "agentic_core/L0_routing/seams/",
    "agentic_core/seams/",
)

# G3: Write side effect exclusions — symbols that match WRITE_SIDE_EFFECT_SYMBOLS
# by suffix but are NOT persistent writes and must not produce writes_to edges.
WRITE_SIDE_EFFECT_EXCLUSIONS: frozenset[str] = frozenset(
    {
        "asyncio.run",
        "copy.deepcopy",
        "deepcopy",
        "assert_no_persistent_write",
        "copy",
    }
)

# G16: Structured rule_id prefixes for violation/bypass edges
RULE_ID_PREFIXES: dict[str, str] = {
    "LAYER_GRAVITY": "Layer gravity violation (upward import)",
    "UWG_BYPASS": "Write bypasses UniversalWriteGateway",
    "SEAM_BYPASS": "Provider call bypasses architectural seam",
    "PROMPT_UNGOVERNED": "LLM invocation without governed prompt",
}

# G1 (gap): Healer/validator base class names for static inheritance detection
HEALER_BASE_CLASSES: frozenset[str] = frozenset(
    {
        "BaseHealingOrchestrator",
        "BaseHealer",
        "HealingOrchestrator",
        "SovereignHealingAgent",
        "LicHealingOrchestrator",
        "RgHealingOrchestrator",
    }
)

VALIDATOR_BASE_CLASSES: frozenset[str] = frozenset(
    {
        "BaseValidator",
        "SovereignValidator",
        "HealerValidator",
        "ResolutionValidator",
        "ValidationAgent",
    }
)

HEALER_METHOD_NAMES: frozenset[str] = frozenset(
    {
        "heal",
        "ml_heal_with_learning_enhanced",
        "orchestrate_healing_cycle",
        "_apply_healing_strategy",
        "run_healing_loop",
    }
)

# G3 (gap): Embedding pipeline symbols for AST detection
EMBEDDING_PIPELINE_SYMBOLS: frozenset[str] = frozenset(
    {
        "chunk_text",
        "split_documents",
        "RecursiveCharacterTextSplitter",
        "CharacterTextSplitter",
        "TokenTextSplitter",
    }
)

RETRIEVAL_SYMBOLS: frozenset[str] = frozenset(
    {
        "similarity_search",
        "as_retriever",
        "max_marginal_relevance_search",
        "get_relevant_documents",
        "retrieve",
        "vector_store.query",
        "vectorstore.query",
    }
)

VECTOR_STORE_SYMBOLS: frozenset[str] = frozenset(
    {
        "FAISS",
        "Chroma",
        "Pinecone",
        "Weaviate",
        "Qdrant",
        "PGVector",
        "ElasticsearchStore",
        "add_documents",
        "add_texts",
        "upsert",
    }
)

# G4 (gap): Confidence threshold / HITL gating symbols
CONFIDENCE_SCORING_CLASSES: frozenset[str] = frozenset(
    {
        "HealingConfidenceScorer",
        "ConfidenceScorer",
        "ConfidenceEngine",
    }
)

HITL_ESCALATION_METHODS: frozenset[str] = frozenset(
    {
        "escalate",
        "escalate_to_human",
        "request_human_review",
        "await_human_approval",
        "submit_for_review",
    }
)

# G5 (gap): Safety / guardrail enforcement symbols
GUARDRAIL_CLASS_NAMES: frozenset[str] = frozenset(
    {
        "SovereignLLMGateway",
        "InstructionFenceGuardrail",
        "PromptGuardrail",
        "OutputGuardrail",
        "CircuitBreaker",
        "SafetyEnforcer",
    }
)

POLICY_HASH_METHODS: frozenset[str] = frozenset(
    {
        "verify_policy_hash",
        "validate_policy_hash",
        "check_policy_hash",
        "enforce_policy",
        "verify_hash",
    }
)


# G7 (gap): Sandbox airlock / work-contract symbols
SANDBOX_ENVELOPE_CLASSES: frozenset[str] = frozenset(
    {
        "SandboxEnvelope",
        "WorkContract",
        "SandboxAirlock",
        "L5SandboxStamper",
        "SandboxSession",
    }
)

CAPABILITY_TOKEN_CLASSES: frozenset[str] = frozenset(
    {
        "CapabilityToken",
        "ScopedCapabilityToken",
        "CapabilityGrant",
        "TokenizedCapability",
    }
)

WORK_CONTRACT_METHODS: frozenset[str] = frozenset(
    {
        "stamp_work_contract",
        "issue_capability_token",
        "enter_sandbox",
        "exit_sandbox",
        "bind_capability_token",
    }
)

# G8 (gap): Tool-budget / resource governance symbols
TOOL_BUDGET_CLASSES: frozenset[str] = frozenset(
    {
        "ToolBudget",
        "ResourceGovernor",
        "CapabilityBudget",
        "ComputeBudget",
        "ExecutionQuota",
    }
)

BUDGET_EXCEEDED_EXCEPTIONS: frozenset[str] = frozenset(
    {
        "BudgetExceededError",
        "CapabilityExhaustedError",
        "ComputeQuotaExceeded",
        "MemoryQuotaExceeded",
        "TokenBudgetExceeded",
    }
)

# G9 (gap): JIT context sync / freeze symbols
JIT_CONTEXT_CLASSES: frozenset[str] = frozenset(
    {
        "JITContext",
        "JITElevator",
        "ContextSnapshot",
        "JITContextSynchronizer",
        "C0ContextPuller",
    }
)

FREEZE_METHOD_NAMES: frozenset[str] = frozenset(
    {
        "freeze_context",
        "pull_context",
        "sync_context",
        "freeze_environment",
        "snapshot_context",
        "unfreeze_context",
    }
)

# G10 (gap): Boundary verification symbols
BOUNDARY_VERIFIER_CLASSES: frozenset[str] = frozenset(
    {
        "L2BoundaryVerifier",
        "BoundaryVerifier",
        "ExecutionBoundaryCheck",
        "PacketValidator",
        "EnvelopeVerifier",
    }
)

CAPABILITY_CHOKEPOINT_CLASSES: frozenset[str] = frozenset(
    {
        "CapabilityChokepoint",
        "L5CertificationCheck",
        "BoundaryChokepoint",
        "PacketChokepoint",
    }
)

# G11 (gap): Determinism control symbols
SEMANTIC_CLOCK_CLASSES: frozenset[str] = frozenset(
    {
        "SemanticClock",
        "DeterministicClock",
        "ReplayClock",
        "FrozenClock",
    }
)

REPLAY_GUARD_CLASSES: frozenset[str] = frozenset(
    {
        "ReplayGuard",
        "DeterminismGuard",
        "ReplayPatcher",
        "NondeterminismBlocker",
    }
)

DETERMINISM_PATCH_METHODS: frozenset[str] = frozenset(
    {
        "seed_rng",
        "patch_time",
        "patch_random",
        "patch_uuid",
        "emit_determinism_digest",
        "guards_replay",
        "install_replay_patches",
    }
)

# G12 (gap): Network / I/O interception symbols
IO_INTERCEPT_CLASSES: frozenset[str] = frozenset(
    {
        "IOInterceptor",
        "NetworkInterceptor",
        "ExternalCallInterceptor",
        "TranscriptedNetworkLayer",
        "ImmutableResponseCapture",
    }
)

NETWORK_TRANSCRIPT_SYMBOLS: frozenset[str] = frozenset(
    {
        "transcript_response",
        "capture_response",
        "record_api_response",
        "hard_fail_untranscripted",
        "intercept_io",
    }
)

# G13 (gap): Mutation transport / commit symbols
MUTATION_TRANSPORT_CLASSES: frozenset[str] = frozenset(
    {
        "MutationTransport",
        "MutationCommitProtocol",
        "TwoPhaseCommit",
        "MutationDistributor",
        "VsockMutationEgress",
        "BlastRadiusChecker",
    }
)

RFC6902_DIFF_SYMBOLS: frozenset[str] = frozenset(
    {
        "package_diff",
        "build_rfc6902_patch",
        "make_json_patch",
        "apply_json_patch",
        "validate_blast_radius",
        "check_blast_radius",
    }
)

# G14 (gap): Execution trace / proof symbols
EXECUTION_TRACE_CLASSES: frozenset[str] = frozenset(
    {
        "ExecutionTrace",
        "ExecutionProof",
        "DeterminismDigest",
        "ProofArtifact",
        "SignedExecutionTrace",
    }
)

REPLAY_KEY_METHODS: frozenset[str] = frozenset(
    {
        "emit_replay_key",
        "record_execution_trace",
        "sign_execution_trace",
        "compare_proof",
        "emit_singleton_digest",
        "verify_replay",
    }
)

# G15 (gap): Path control symbols
PATH_CONTROL_CLASSES: frozenset[str] = frozenset(
    {
        "ExecutionPathController",
        "PathRouter",
        "PathABCDController",
        "StallForcer",
        "SafetyReentryGate",
        "VigilanceRerouter",
    }
)

PATH_REROUTE_METHODS: frozenset[str] = frozenset(
    {
        "route_path",
        "force_stall",
        "force_path_d",
        "reenter_safety",
        "vigilance_reroute",
        "reroute_to_l0",
        "reroute_to_l1",
    }
)

# G16 (gap): Evaluation / optimization spine symbols
EVAL_METRIC_CLASSES: frozenset[str] = frozenset(
    {
        "GroundednessScorer",
        "RetrievalEvaluator",
        "NDCGScorer",
        "MRRScorer",
        "CompletenessScorer",
        "EvalSpine",
        "OptimizationSpine",
    }
)

DPO_BATCH_CLASSES: frozenset[str] = frozenset(
    {
        "DPOBatchBuilder",
        "DPOBatch",
        "PreferencePairBuilder",
        "OptimizationProposal",
    }
)

DRIFT_ALERT_METHODS: frozenset[str] = frozenset(
    {
        "emit_drift_alert",
        "score_groundedness",
        "compute_pk",
        "compute_mrr",
        "compute_ndcg",
        "build_dpo_batch",
        "commit_optimization",
    }
)


# G17 (gap): Secret / credential access symbols
SECRET_VAULT_CLASSES: frozenset[str] = frozenset(
    {
        "SecretVault",
        "CredentialStore",
        "AWSSecretsManager",
        "GCPSecretManager",
        "AzureKeyVault",
        "HashicorpVault",
        "SecretProvider",
    }
)

SECRET_ACCESS_METHODS: frozenset[str] = frozenset(
    {
        "get_secret",
        "read_secret",
        "fetch_secret",
        "load_secret",
        "access_credential",
        "rotate_secret",
        "get_password",
        "get_api_key",
    }
)

SECRET_ENV_PATTERNS: frozenset[str] = frozenset(
    {
        "os.environ",
        "os.getenv",
        "environ.get",
        "getenv",
        "dotenv",
        "load_dotenv",
    }
)

# G18 (gap): Config governance symbols
CONFIG_READER_CLASSES: frozenset[str] = frozenset(
    {
        "ConfigReader",
        "GovernedConfig",
        "ConfigLoader",
        "PolicyConfig",
        "StructuredConfig",
        "HydraConfig",
        "PydanticSettings",
        "BaseSettings",
    }
)

CONFIG_ACCESS_METHODS: frozenset[str] = frozenset(
    {
        "load_config",
        "read_config",
        "get_config",
        "validate_config",
        "cache_config",
        "refresh_config",
        "resolve_config",
    }
)

# G19 (gap): Dynamic invocation symbols
DYNAMIC_EVAL_SYMBOLS: frozenset[str] = frozenset(
    {
        "eval",
        "exec",
        "compile",
        "__import__",
        "importlib.import_module",
        "importlib.util.spec_from_file_location",
        "importlib.util.module_from_spec",
        "runpy.run_module",
        "runpy.run_path",
    }
)

DYNAMIC_GETATTR_SYMBOLS: frozenset[str] = frozenset(
    {
        "getattr",
        "setattr",
        "delattr",
        "hasattr",
        "vars",
        "type",
    }
)

# G20 (gap): Policy state observation symbols
POLICY_STATE_READER_CLASSES: frozenset[str] = frozenset(
    {
        "PolicyStateReader",
        "RuntimeStateObserver",
        "StateSnapshot",
        "PolicyObserver",
        "GovernanceStateReader",
        "RuntimeHealthProbe",
    }
)

POLICY_STATE_READ_METHODS: frozenset[str] = frozenset(
    {
        "read_policy_state",
        "observe_policy",
        "snapshot_runtime",
        "get_runtime_state",
        "probe_health",
        "read_governance_state",
        "observe_runtime_state",
    }
)

# G21 (gap): Anti-pattern registry symbols
ANTIPATTERN_REGISTRY_CLASSES: frozenset[str] = frozenset(
    {
        "AntipatternRegistry",
        "AntipatternRecord",
        "PatternClassifier",
        "AntipatternDetector",
        "ViolationClassifier",
    }
)

ANTIPATTERN_CATEGORY_NAMES: frozenset[str] = frozenset(
    {
        "silent_exception_swallow",
        "blocking_call_in_async",
        "global_state_mutation",
        "retry_without_backoff",
        "bare_except",
        "mutable_default_arg",
        "star_import_use",
        "hardcoded_secret",
    }
)

# G22 (gap): Healing orchestrator symbols
HEALING_ORCHESTRATOR_CLASSES: frozenset[str] = frozenset(
    {
        "HealingOrchestrator",
        "RepairOrchestrator",
        "HealerDispatcher",
        "AutoRepairEngine",
        "SelfHealingController",
    }
)

HEALING_DISPATCH_METHODS: frozenset[str] = frozenset(
    {
        "dispatch_healing",
        "orchestrate_healing",
        "run_healer",
        "confirm_heal",
        "abort_heal",
        "schedule_repair",
        "trigger_healing",
    }
)


# G23 (gap): Non-determinism primitive symbols
NONDETERMINISM_WALL_CLOCK_SYMBOLS: frozenset[str] = frozenset(
    {
        "datetime.datetime.now",
        "datetime.datetime.utcnow",
        "datetime.date.today",
        "time.time",
        "time.monotonic",
        "time.perf_counter",
        "time.process_time",
        "time.localtime",
        "time.gmtime",
        "time.strftime",
    }
)

NONDETERMINISM_RANDOM_SYMBOLS: frozenset[str] = frozenset(
    {
        "random.random",
        "random.randint",
        "random.choice",
        "random.choices",
        "random.shuffle",
        "random.sample",
        "random.uniform",
        "random.gauss",
        "random.seed",
        "numpy.random",
        "np.random",
        "secrets.token_hex",
        "secrets.token_bytes",
        "secrets.token_urlsafe",
        "secrets.choice",
        "secrets.randbelow",
    }
)

NONDETERMINISM_UUID_SYMBOLS: frozenset[str] = frozenset(
    {
        "uuid.uuid1",
        "uuid.uuid4",
        "uuid.uuid3",
        "uuid.uuid5",
        "uuid4",
        "uuid1",
        "UUID",
    }
)

# G24 (gap): External HTTP / network egress symbols
EXTERNAL_HTTP_SYMBOLS: frozenset[str] = frozenset(
    {
        "requests.get",
        "requests.post",
        "requests.put",
        "requests.delete",
        "requests.patch",
        "requests.head",
        "requests.request",
        "requests.Session",
        "httpx.get",
        "httpx.post",
        "httpx.put",
        "httpx.delete",
        "httpx.Client",
        "httpx.AsyncClient",
        "aiohttp.ClientSession",
        "urllib.request.urlopen",
        "urllib.request.urlretrieve",
        "urllib.request.Request",
    }
)

# G25 (gap): Agent-to-agent dispatch symbols
AGENT_DISPATCH_CLASSES: frozenset[str] = frozenset(
    {
        "AgentDispatcher",
        "AgentRouter",
        "SubAgentInvoker",
        "AgentOrchestrator",
        "MultiAgentCoordinator",
        "AgentChain",
        "AgentPipeline",
    }
)

AGENT_DISPATCH_METHODS: frozenset[str] = frozenset(
    {
        "invoke_agent",
        "dispatch_agent",
        "call_agent",
        "run_agent",
        "execute_agent",
        "delegate_to",
        "handoff_to",
        "forward_to_agent",
    }
)

# G26 (gap): L5 validation proof symbols
AGENT_REGISTRY_CLASSES: frozenset[str] = frozenset(
    {
        "AgentRegistry",
        "AgentRegistrar",
        "CapabilityRegistry",
        "AgentValidator",
        "RegistryLookup",
    }
)

SAFETY_PLANE_CLASSES: frozenset[str] = frozenset(
    {
        "SafetyPlane",
        "SafetyEnforcer",
        "L5SafetyGate",
        "ClassificationKernel",
        "StructureBlueprint",
        "SovereignLLMGateway",
        "SovereignMCPGatewayAgent",
    }
)

UWG_TERMINATION_SYMBOLS: frozenset[str] = frozenset(
    {
        "UniversalWriteGateway",
        "UWGAdapter",
        "uwg_write",
        "commit_via_uwg",
        "route_through_uwg",
        "uwg_gate",
    }
)

POLICY_HASH_SYMBOLS: frozenset[str] = frozenset(
    {
        "policy_hash",
        "PolicyHash",
        "PolicyHashGuard",
        "PolicyConfigGuard",
        "policy_hash_mismatch",
        "verify_policy_hash",
        "check_policy_hash",
        "PolicyHashChain",
    }
)

# G27 (gap): Learning / prompt provenance symbols
ROUTING_COMMIT_SYMBOLS: frozenset[str] = frozenset(
    {
        "MetaLearningProposalArtifact",
        "build_meta_learning_proposal",
        "build_meta_learning_decision",
        "build_meta_learning_change_package",
        "MetaLearningDecisionArtifact",
        "MetaLearningChangePackageArtifact",
        "MetaLearningProposal",
        "RoutingProposal",
        "ProposalCommitter",
        "commit_routing_update",
        "apply_routing_proposal",
        "LearningPipelineCommitter",
        "commit_proposal",
    }
)

PROMPT_TEMPLATE_SYMBOLS: frozenset[str] = frozenset(
    {
        "PromptTemplate",
        "SystemPromptTemplate",
        "PromptRegistry",
        "PromptLoader",
        "load_prompt_template",
        "get_prompt_template",
        "PromptBuilder",
    }
)

PROMPT_INJECTION_SYMBOLS: frozenset[str] = frozenset(
    {
        "InstructionInjector",
        "PromptInjector",
        "D0Injector",
        "inject_instruction",
        "inject_d0",
        "PromptAugmentor",
        "InstructionOverride",
    }
)

PREFERENCE_PAIR_SYMBOLS: frozenset[str] = frozenset(
    {
        "DPOPair",
        "PreferencePair",
        "DPOPairBuilder",
        "PreferencePairRecorder",
        "emit_preference_pair",
        "record_dpo_pair",
        "DPODataset",
    }
)

HUMAN_REVIEW_SYMBOLS: frozenset[str] = frozenset(
    {
        "HumanReviewGate",
        "HumanApprovalRequired",
        "requires_human_review",
        "requires_human_approval",
        "await_human_approval",
        "HumanInTheLoop",
        "HITLGate",
        "EscalateToHuman",
        "request_human_review",
        "load_human_review_adapter",
        "human_review_adapter",
        "human_review",
    }
)


GATEWAY_ALLOWLIST: dict[str, str] = {
    "SovereignLLMGateway": "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
    "UniversalWriteGateway": "agentic_core/L2_execution/UniversalWriteGateway.py",
    "EmbeddingSovereignAgent": "agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
}

PROVIDER_SDK_SYMBOLS: frozenset[str] = frozenset(
    {
        "openai",
        "anthropic",
        "google.generativeai",
        "google.cloud.aiplatform",
        "vertexai",
        "requests",
        "httpx",
        "aiohttp",
        "boto3",
        "botocore",
    }
)

EMBEDDING_SYMBOLS: frozenset[str] = frozenset(
    {
        "OpenAIEmbeddings",
        "VertexAIEmbeddings",
        "GoogleGenerativeAIEmbeddings",
        "HuggingFaceEmbeddings",
        "FakeEmbeddings",
        "SentenceTransformerEmbeddings",
        "EmbeddingSovereignAgent",
        "bmg_embed_text",
        "create_vertex_client",
    }
)

WRITE_SIDE_EFFECT_SYMBOLS: frozenset[str] = frozenset(
    {
        "open",
        "write",
        "os.remove",
        "os.rename",
        "os.makedirs",
        "os.mkdir",
        "shutil.copy",
        "shutil.move",
        "shutil.rmtree",
        "pathlib.Path.write_text",
        "pathlib.Path.write_bytes",
        "subprocess.run",
        "subprocess.Popen",
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
    }
)

NETWORK_SYMBOLS: frozenset[str] = frozenset(
    {
        "requests.get",
        "requests.post",
        "requests.put",
        "requests.delete",
        "requests.patch",
        "requests.head",
        "requests.options",
        "httpx.get",
        "httpx.post",
        "httpx.Client",
        "httpx.AsyncClient",
        "aiohttp.ClientSession",
        "urllib.request.urlopen",
        "urllib.request.urlretrieve",
    }
)

SYMBOL_KINDS: frozenset[str] = frozenset(
    {
        "function",
        "async_function",
        "class",
        "constant",
        "type_alias",
    }
)


__all__ = [
    "ADG_NS",
    "EntityType",
    "RelationType",
    "EdgeKind",
    "canonical_name",
    "module_path_to_layer",
    "verify_layer_graph_consistency",
    "LAYER_PREFIXES",
    "ALLOWED_LAYER_EDGES",
    "GATEWAY_ALLOWLIST",
    "PROVIDER_SDK_SYMBOLS",
    "EMBEDDING_SYMBOLS",
    "WRITE_SIDE_EFFECT_SYMBOLS",
    "WRITE_SIDE_EFFECT_EXCLUSIONS",
    "NETWORK_SYMBOLS",
    "SYMBOL_KINDS",
    "SEAM_MODULE_PATTERNS",
    "RULE_ID_PREFIXES",
    # P6
    "PROMPT_SLOT_TYPES",
    "PROMPT_SLOT_AUTHORITY",
    "PROMPT_AUTHORITY_RULES",
    "PROMPT_FIELD_TO_SLOT",
    # P3
    "UWG_CANONICAL_SYMBOL",
    "UWG_MODULE_PATH",
    "UWG_INTERFACE_PATH",
    "LAYER_AUTHORITY_FORBIDDEN",
    "L1_WRITE_ALLOWLIST",
    "UWG_WRITE_SYMBOLS",
    # G1 (gap): Runtime behavior / healer-validator
    "HEALER_BASE_CLASSES",
    "VALIDATOR_BASE_CLASSES",
    "HEALER_METHOD_NAMES",
    # G3 (gap): Embedding pipeline
    "EMBEDDING_PIPELINE_SYMBOLS",
    "RETRIEVAL_SYMBOLS",
    "VECTOR_STORE_SYMBOLS",
    # G4 (gap): HITL / confidence
    "CONFIDENCE_SCORING_CLASSES",
    "HITL_ESCALATION_METHODS",
    # G5 (gap): Safety enforcement
    "GUARDRAIL_CLASS_NAMES",
    "POLICY_HASH_METHODS",
    # G7 (gap): Sandbox airlock
    "SANDBOX_ENVELOPE_CLASSES",
    "CAPABILITY_TOKEN_CLASSES",
    "WORK_CONTRACT_METHODS",
    # G8 (gap): Tool budget
    "TOOL_BUDGET_CLASSES",
    "BUDGET_EXCEEDED_EXCEPTIONS",
    # G9 (gap): JIT context
    "JIT_CONTEXT_CLASSES",
    "FREEZE_METHOD_NAMES",
    # G10 (gap): Boundary verification
    "BOUNDARY_VERIFIER_CLASSES",
    "CAPABILITY_CHOKEPOINT_CLASSES",
    # G11 (gap): Determinism
    "SEMANTIC_CLOCK_CLASSES",
    "REPLAY_GUARD_CLASSES",
    "DETERMINISM_PATCH_METHODS",
    # G12 (gap): IO interception
    "IO_INTERCEPT_CLASSES",
    "NETWORK_TRANSCRIPT_SYMBOLS",
    # G13 (gap): Mutation transport
    "MUTATION_TRANSPORT_CLASSES",
    "RFC6902_DIFF_SYMBOLS",
    # G14 (gap): Execution proof
    "EXECUTION_TRACE_CLASSES",
    "REPLAY_KEY_METHODS",
    # G15 (gap): Path control
    "PATH_CONTROL_CLASSES",
    "PATH_REROUTE_METHODS",
    # G16 (gap): Evaluation spine
    "EVAL_METRIC_CLASSES",
    "DPO_BATCH_CLASSES",
    "DRIFT_ALERT_METHODS",
    # G17 (gap): Secret / credential access
    "SECRET_VAULT_CLASSES",
    "SECRET_ACCESS_METHODS",
    "SECRET_ENV_PATTERNS",
    # G18 (gap): Config governance
    "CONFIG_READER_CLASSES",
    "CONFIG_ACCESS_METHODS",
    # G19 (gap): Dynamic invocation
    "DYNAMIC_EVAL_SYMBOLS",
    "DYNAMIC_GETATTR_SYMBOLS",
    # G20 (gap): Policy state observation
    "POLICY_STATE_READER_CLASSES",
    "POLICY_STATE_READ_METHODS",
    # G21 (gap): Anti-pattern registry
    "ANTIPATTERN_REGISTRY_CLASSES",
    "ANTIPATTERN_CATEGORY_NAMES",
    # G22 (gap): Healing orchestrator
    "HEALING_ORCHESTRATOR_CLASSES",
    "HEALING_DISPATCH_METHODS",
    # G23 (gap): Non-determinism primitive detection
    "NONDETERMINISM_WALL_CLOCK_SYMBOLS",
    "NONDETERMINISM_RANDOM_SYMBOLS",
    "NONDETERMINISM_UUID_SYMBOLS",
    # G24 (gap): External HTTP / network egress
    "EXTERNAL_HTTP_SYMBOLS",
    # G25 (gap): Agent-to-agent dispatch
    "AGENT_DISPATCH_CLASSES",
    "AGENT_DISPATCH_METHODS",
    # G26 (gap): L5 validation proof
    "AGENT_REGISTRY_CLASSES",
    "SAFETY_PLANE_CLASSES",
    "UWG_TERMINATION_SYMBOLS",
    "POLICY_HASH_SYMBOLS",
    # G27 (gap): Learning / prompt provenance
    "ROUTING_COMMIT_SYMBOLS",
    "PROMPT_TEMPLATE_SYMBOLS",
    "PROMPT_INJECTION_SYMBOLS",
    "PREFERENCE_PAIR_SYMBOLS",
    "HUMAN_REVIEW_SYMBOLS",
]
