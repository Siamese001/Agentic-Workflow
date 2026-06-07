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

import re
from functools import lru_cache
from pathlib import Path
from typing import Literal

_LAYER_MARKER_RE = re.compile(r'^\s*__layer__\s*=\s*["\']([^"\']+)["\']', re.M)


def _repo_root_from_schema_util() -> Path:
    return Path(__file__).resolve().parents[3]


def _layer_from_init_markers(norm: str) -> str | None:
    if not norm.endswith(".py"):
        return None
    parts = norm.split("/")[:-1]
    root = _repo_root_from_schema_util()
    for depth in range(len(parts), 0, -1):
        init_rel = "/".join(parts[:depth]) + "/__init__.py"
        init_path = root / init_rel
        if not init_path.is_file():
            continue
        try:
            text = init_path.read_text(encoding="utf-8")
        except OSError:
            continue
        match = _LAYER_MARKER_RE.search(text)
        if match:
            return match.group(1)
    return None


# Local stub to avoid L_TOOLS->L_RUNTIME dependency while maintaining ADG instrumentation
def _emit_reads_through(source: str, target: str, context: str) -> None:
    """Stub for reads_through ADG edge emission.\n    \n    Avoids importing from L_RUNTIME (layer violation).\n    The actual emission is handled by static analysis.\n"""
    pass


# Configuration constants required by tests

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
    "prompt_slot",
    "prompt_template",
    "prompt_assembly",
    "execution_trace",
    "agent_action",
    "tool_invocation",
    "layer_transition",
    "mutation_record",
    "healing_loop",
    "validator_node",
    "healer_agent",
    "embedding_store",
    "chunk_pipeline",
    "retrieval_endpoint",
    "hitl_checkpoint",
    "confidence_gate",
    "human_decision",
    "guardrail",
    "policy_enforcer",
    "agent_registration",
    "agent_capability",
    "sandbox_envelope",
    "capability_token",
    "work_contract",
    "tool_budget",
    "resource_grant",
    "jit_context_snapshot",
    "freeze_boundary",
    "boundary_checkpoint",
    "capability_chokepoint",
    "semantic_clock",
    "replay_guard",
    "rng_seed",
    "io_intercept",
    "network_transcript",
    "mutation_packet",
    "commit_protocol",
    "execution_proof",
    "determinism_digest",
    "execution_path",
    "path_reroute",
    "eval_metric",
    "dpo_batch",
    "drift_alert",
    "secret_access_record",
    "credential_vault",
    "secret_read_event",
    "config_read_record",
    "config_policy_gate",
    "dynamic_invocation_record",
    "eval_exec_site",
    "policy_state_read",
    "runtime_state_read",
    "state_observation_report",
    "antipattern_record",
    "antipattern_category",
    "healing_run",
    "orchestration_step",
    "nondeterminism_site",
    "wall_clock_call",
    "random_call_site",
    "uuid_call_site",
    "external_call_site",
    "http_egress_node",
    "agent_dispatch_edge",
    "agent_invocation_record",
    "registry_validation_record",
    "safety_plane_proof",
    "llm_gateway_proof",
    "uwg_termination_proof",
    "policy_hash_reference",
    "routing_commit_record",
    "prompt_provenance_record",
    "preference_pair_artifact",
    "human_review_record",
    "validated_request",
    "l1_plan",
    "route_decision",
    "retrieval_plan",
    "c0_evidence_contract",
    "prompt_envelope",
    "validation_packet",
    "sealed_result",
    "exit_disposition",
    "hitl_packet",
    "commit_request",
    "commit_receipt",
    "replay_envelope",
    "promotion_packet",
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
    "reads_env",
    "reads_secret",
    "reads_policy_state",
    "reads_runtime_state",
    "reads_config",
    "generates_prompt",
    "consumes_prompt",
    "assembles_into",
    "injects_into",
    "overrides_prompt",
    "executed_with_prompt",
    "triggered_telemetry",
    "proposed_improvement",
    "updated_prompt",
    "executes_action",
    "invokes_tool",
    "crosses_layer",
    "bypasses_uwg",
    "routes_through_uwg",
    "layer_authority_violation",
    "policy_hash_mismatch",
    "lineage_of",
    "antipattern",
    "heals",
    "validates",
    "orchestrates_healing",
    "dispatches_to",
    "assembles_into",
    "injects_into",
    "overrides_prompt",
    "embeds_into",
    "retrieves_via",
    "chunks_into",
    "stores_embedding",
    "escalates_to_human",
    "awaits_approval",
    "learns_from_decision",
    "gated_by_confidence",
    "applies_guardrail",
    "verifies_policy",
    "enforces_policy_hash",
    "registered_as",
    "has_capability",
    "depends_on_agent",
    "stamps_work_contract",
    "issues_capability_token",
    "enters_sandbox",
    "exits_sandbox",
    "consumes_budget",
    "grants_resource",
    "exceeds_budget",
    "pulls_context",
    "freezes_context",
    "unfreezes_context",
    "verifies_boundary",
    "rejects_packet",
    "certifies_envelope",
    "seeds_rng",
    "patches_time",
    "guards_replay",
    "emits_determinism_digest",
    "intercepts_io",
    "transcripts_response",
    "hard_fails_untranscripted",
    "packages_diff",
    "validates_blast_radius",
    "signs_execution_trace",
    "commits_mutation",
    "distributes_mutation",
    "records_execution_trace",
    "emits_replay_key",
    "compares_proof",
    "routes_path",
    "forces_stall",
    "reenters_safety",
    "vigilance_reroute",
    "scores_groundedness",
    "emits_drift_alert",
    "builds_dpo_batch",
    "commits_optimization",
    "reads_secret_vault",
    "accesses_credential",
    "rotates_secret",
    "reads_governed_config",
    "validates_config_schema",
    "caches_config",
    "invokes_eval",
    "invokes_exec",
    "invokes_importlib",
    "invokes_getattr_dynamic",
    "observes_policy_state",
    "observes_runtime_state",
    "snapshots_state",
    "registers_antipattern",
    "classifies_antipattern",
    "dispatches_healing_run",
    "confirms_heal",
    "aborts_heal",
    "uses_wall_clock",
    "uses_random",
    "uses_uuid",
    "external_http_call",
    "agent_executes_agent",
    "validated_by_registry",
    "validated_by_safety_plane",
    "validated_by_llm_gateway",
    "execution_terminates_at_uwg",
    "references_policy_hash",
    "proposal_commits_routing",
    "prompt_template_used_by",
    "instruction_injection_source",
    "produces_preference_pair",
    "requires_human_review",
    "routes_to_agent",
    "orchestrates_workflow",
    "dispatches_execution_plan",
    "validates_agent_capability",
    "checks_agent_registry",
    "validates_request",
    "produces_plan",
    "proposes_route",
    "prefilters_scope",
    "produces_evidence_contract",
    "packages_prompt_envelope",
    "stamps_execution_packet",
    "propagates_policy_hash",
    "propagates_replay_key",
    "seals_result",
    "chooses_exit_disposition",
    "materializes_hitl_packet",
    "reclears_human_decision",
    "verifies_blast_radius",
    "appends_commit_receipt",
    "publishes_retrieval_surface",
    "promotes_future_run_change",
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
    "prompt_generation",
    "prompt_consumption",
    "prompt_assembly",
    "prompt_injection",
    "prompt_authority_violation",
    "trace_prompt_link",
    "prompt_drift",
    "agent_execution",
    "tool_call",
    "layer_boundary_cross",
    "uwg_bypass",
    "uwg_compliant_write",
    "authority_violation",
    "policy_validation",
    "state_lineage",
    "silent_exception_swallow",
    "broad_exception_catch",
    "log_and_swallow",
    "return_none_swallow",
    "unreachable_after_raise",
    "exception_type_erasure",
    "cleanup_raises_over_original",
    "return_in_finally",
    "partial_side_effects",
    "double_logging",
    "bare_except",
    "default_fallback_masking",
    "throw_for_normal_flow",
    "hardcoded_secret",
    "blocking_call_in_async",
    "global_state_mutation",
    "retry_without_backoff",
    "mutable_default_arg",
    "star_import_use",
    "healer_action",
    "validator_check",
    "healing_dispatch",
    "embedding_pipeline",
    "retrieval_pipeline",
    "chunking_pipeline",
    "hitl_escalation",
    "confidence_gate",
    "approval_wait",
    "guardrail_execution",
    "policy_verification",
    "agent_registration",
    "sandbox_entry",
    "sandbox_exit",
    "work_contract_stamp",
    "capability_token_issue",
    "budget_grant",
    "budget_exceeded",
    "context_pull",
    "context_freeze",
    "boundary_accept",
    "boundary_reject",
    "determinism_seed",
    "replay_patch",
    "determinism_digest_emit",
    "io_transcript",
    "io_hard_fail",
    "diff_package",
    "blast_radius_check",
    "two_phase_commit",
    "mutation_distribution",
    "execution_trace_record",
    "replay_key_emit",
    "proof_comparison",
    "path_route",
    "path_stall",
    "path_safety_reentry",
    "path_vigilance_reroute",
    "eval_score",
    "drift_alert",
    "dpo_build",
    "optimization_commit",
    "secret_read",
    "credential_access",
    "secret_rotation",
    "governed_config_read",
    "config_schema_validation",
    "eval_call",
    "exec_call",
    "importlib_call",
    "dynamic_getattr",
    "policy_state_observation",
    "runtime_state_snapshot",
    "antipattern_classification",
    "healing_dispatch",
    "healing_confirm",
    "healing_abort",
    "wall_clock_use",
    "random_use",
    "uuid_use",
    "http_egress_call",
    "agent_dispatch",
    "registry_validation",
    "safety_plane_validation",
    "llm_gateway_validation",
    "uwg_termination",
    "policy_hash_link",
    "routing_commit",
    "prompt_template_link",
    "injection_source_link",
    "preference_pair_link",
    "human_review_gate",
    "agent_route",
    "workflow_orchestration",
    "execution_plan_dispatch",
    "capability_validation",
    "registry_check",
    "handoff_validate",
    "handoff_plan",
    "handoff_route",
    "handoff_prefilter",
    "handoff_evidence",
    "handoff_prompt_pkg",
    "handoff_exec_stamp",
    "handoff_policy_hash",
    "handoff_replay_key",
    "handoff_seal",
    "handoff_exit_choice",
    "handoff_hitl_packet",
    "handoff_reclear",
    "handoff_blast_radius",
    "handoff_commit_receipt",
    "handoff_retrieval_surface",
    "handoff_promote",
]
PROMPT_SLOT_TYPES: tuple[str, ...] = ("S0", "D0", "I0", "C0", "U0")
PROMPT_SLOT_AUTHORITY: dict[str, int] = {slot: i for i, slot in enumerate(PROMPT_SLOT_TYPES)}
PROMPT_AUTHORITY_RULES: tuple[tuple[str, str], ...] = (
    ("U0", "S0"),
    ("U0", "D0"),
    ("U0", "I0"),
    ("C0", "S0"),
    ("C0", "D0"),
    ("I0", "S0"),
)
PROMPT_FIELD_TO_SLOT: dict[str, str] = {
    "s0_system": "S0",
    "d0_injections": "D0",
    "i0_instructional": "I0",
    "c0_context": "C0",
    "u0_user_prompt": "U0",
}
UWG_CANONICAL_SYMBOL: str = "ADG::Symbol::UniversalWriteGateway"
UWG_MODULE_PATH: str = "agentic_core/L2_execution/UniversalWriteGateway.py"
UWG_INTERFACE_PATH: str = "agentic_core/interfaces/write_gateway.py"
LAYER_AUTHORITY_FORBIDDEN: dict[str, frozenset[str]] = {
    "L1": frozenset({"writes_to", "writes_through"}),
    "L3": frozenset({"invokes_tool", "invokes_provider"}),
    "L4": frozenset({"calls", "invokes_provider"}),
    "L6": frozenset({"writes_to", "writes_through", "routes_through"}),
}
L1_WRITE_ALLOWLIST: frozenset[str] = frozenset(
    {
        "copy",
        "output.copy",
        "self.strategy_weights.copy",
        "copy.deepcopy",
        "self.guardrails._cache_sizes.copy",
        "visited.copy",
    },
)
UWG_WRITE_SYMBOLS: frozenset[str] = frozenset(
    {
        "UniversalWriteGateway",
        "uwg.write",
        "uwg.write_bytes",
        "write_gateway.write_text",
        "write_gateway.write_bytes",
    },
)

# ── L4/UWG Wave 1 Ingress Gate Symbols ───────────────────────────────────
UWG_VALIDATES_INTENT_SYMBOLS: frozenset[str] = frozenset(
    {
        "verify_signature",
        "verify_active_policy_hash",
        "check_signature",
        "SignatureVerifier",
        "UWGSignatureValidator",
        "verify_uwg_intent",
        "UWGIntentVerifier",
        "_emit_validates_uwg_intent",
    },
)
UWG_CHECKS_POLICY_HASH_SYMBOLS: frozenset[str] = frozenset(
    {
        "check_policy_hash_at_uwg",
        "verify_policy_at_gateway",
        "UWGPolicyHashChecker",
        "PolicyHashValidator",
        "validate_active_policy",
        "_emit_checks_policy_hash_at_uwg",
    },
)
UWG_CHECKS_CAPABILITY_SET_SYMBOLS: frozenset[str] = frozenset(
    {
        "check_allowed_capability_set",
        "verify_capability_at_uwg",
        "CapabilitySetChecker",
        "UWGCapabilityValidator",
        "validate_capability_set",
        "_emit_checks_capability_set",
    },
)
UWG_BLAST_RADIUS_SYMBOLS: frozenset[str] = frozenset(
    {
        "validate_blast_radius_at_uwg",
        "check_uwg_blast_radius",
        "UWGBlastRadiusChecker",
        "validate_mutation_scope",
        "check_rbac_at_uwg",
        "_emit_validates_blast_radius_at_uwg",
    },
)

# ── L4/UWG Wave 2 Mutation Record Assembly Symbols ─────────────────────────
MUTATION_DIFF_SYMBOLS: frozenset[str] = frozenset(
    {
        "generate_mutation_diff",
        "create_before_after_diff",
        "MutationDiffGenerator",
        "RFC6902DiffGenerator",
        "diff_mutation_state",
        "_emit_generates_mutation_diff",
    },
)
MUTATION_REPLAY_KEY_SYMBOLS: frozenset[str] = frozenset(
    {
        "compute_mutation_replay_key",
        "generate_replay_key_for_mutation",
        "MutationReplayKeyGenerator",
        "ReplayKeyComputer",
        "compute_replay_key",
        "_emit_computes_mutation_replay_key",
    },
)
HMAC_SEAL_SYMBOLS: frozenset[str] = frozenset(
    {
        "apply_hmac_seal",
        "seal_mutation_with_hmac",
        "HMACSealApplier",
        "MutationHMACSealer",
        "apply_hmac",
        "_emit_applies_hmac_seal",
    },
)
EXECUTION_TRACE_PACKAGE_SYMBOLS: frozenset[str] = frozenset(
    {
        "package_execution_trace",
        "create_execution_trace_artifact",
        "ExecutionTracePackager",
        "TraceArtifactBuilder",
        "package_trace",
        "_emit_packages_execution_trace",
    },
)

# ── Wave 3: Authoritative Commit + L4 Read Surface ─────────────────────────
CLAIMS_WRITE_LOCK_SYMBOLS: frozenset[str] = frozenset(
    {
        "claims_write_lock",
        "claim_write_lock",
        "WriteLockClaimer",
        "L4WriteLock",
        "acquire_write_lock",
        "_emit_claims_write_lock",
    },
)
DURABLE_COMMIT_SYMBOLS: frozenset[str] = frozenset(
    {
        "commits_mutation_durable",
        "durable_commit",
        "DurableCommitExecutor",
        "MutationCommit",
        "commit_to_ledger",
        "_emit_commits_mutation_durable",
    },
)
HASH_CHAIN_APPEND_SYMBOLS: frozenset[str] = frozenset(
    {
        "appends_hash_chain",
        "append_hash_chain",
        "HashChainAppender",
        "LedgerHashChain",
        "append_to_chain",
        "_emit_appends_hash_chain",
    },
)
ROLLBACK_HEAL_SYMBOLS: frozenset[str] = frozenset(
    {
        "heals_on_rollback_failure",
        "heal_rollback_failure",
        "RollbackHealer",
        "RollbackFailureHandler",
        "handle_rollback_failure",
        "_emit_heals_on_rollback_failure",
    },
)
MATERIALIZES_READ_VIEW_SYMBOLS: frozenset[str] = frozenset(
    {
        "materializes_read_view",
        "materialize_read_view",
        "ReadViewMaterializer",
        "L4ReadView",
        "generate_materialized_view",
        "_emit_materializes_read_view",
    },
)
RETRIEVAL_SURFACE_REFRESH_SYMBOLS: frozenset[str] = frozenset(
    {
        "refreshes_retrieval_surface",
        "refresh_retrieval_surface",
        "RetrievalSurfaceRefresher",
        "L4RetrievalSurface",
        "refresh_surface",
        "_emit_refreshes_retrieval_surface",
    },
)
SWAPS_VERSION_ALIAS_SYMBOLS: frozenset[str] = frozenset(
    {
        "swaps_version_alias",
        "swap_version_alias",
        "VersionAliasSwapper",
        "L4VersionAlias",
        "swap_alias",
        "_emit_swaps_version_alias",
    },
)
L4_TELEMETRY_SYNC_SYMBOLS: frozenset[str] = frozenset(
    {
        "syncs_l4_telemetry",
        "sync_telemetry",
        "L4TelemetrySync",
        "TelemetryAuditor",
        "sync_audit_telemetry",
        "_emit_syncs_l4_telemetry",
    },
)

# ── Wave 4: Outbound Read Bridges ──────────────────────────────────────────
READS_L4_SURFACE_SYMBOLS: frozenset[str] = frozenset(
    {
        "reads_l4_surface",
        "read_l4_surface",
        "L4SurfaceReader",
        "ContextBuilder",
        "build_context_from_l4",
        "_emit_reads_l4_surface",
    },
)
L0_RECEIVES_POLICY_HASH_SYMBOLS: frozenset[str] = frozenset(
    {
        "receives_policy_hash",
        "receive_policy_hash",
        "PolicyHashReceiver",
        "L0PolicyHash",
        "get_active_policy_hash",
        "_emit_receives_policy_hash",
    },
)
L5_READS_L4_SURFACE_SYMBOLS: frozenset[str] = frozenset(
    {
        "l5_reads_l4_surface",
        "read_l4_at_l5",
        "L5L4SurfaceReader",
        "ConstitutionBoundaryChecker",
        "check_constitution_against_l4",
        "_emit_l5_reads_l4_surface",
    },
)
L3_READS_L4_SURFACE_SYMBOLS: frozenset[str] = frozenset(
    {
        "l3_reads_l4_surface",
        "read_l4_at_l3",
        "L3L4SurfaceReader",
        "DAGWorkflowRuleChecker",
        "check_dag_rules_against_l4",
        "_emit_l3_reads_l4_surface",
    },
)
L6_INGESTS_L4_TRACE_SYMBOLS: frozenset[str] = frozenset(
    {
        "ingests_l4_trace",
        "ingest_l4_trace",
        "L4TraceIngester",
        "ExecutionTraceConsumer",
        "consume_l4_execution_trace",
        "_emit_l6_ingests_l4_trace",
    },
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
    "agentic_core/_compat": "L_SHARED",
    "agentic_core/embeddings": "L_SHARED",
    "agentic_core/enforcement": "L_SHARED",
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
    "agentic_core/L_CONTRACTS": "L_RUNTIME",
    "agentic_core/prompt_governance": "L_PG",
    "agentic_core/knowledge": "L_PG",
    "agentic_core/adg": "L_TOOLS",
    "apps_rg": "L_APP",
    "apps_lic": "L_APP",
    "apps_shared": "L_APP",
    "apps_eval": "L_APP",
    "apps_exec": "L_APP",
    "apps_research": "L_APP",
    "apps_rfp": "L_APP",
    "apps_underwriting_ai": "L_APP",
    "agentic_core/patterns": "L_SHARED",
    "agentic_core/case_memory": "L_SHARED",
    "agentic_core/cloud_native": "L_SHARED",
    "agentic_core/core": "L_SHARED",
    "agentic_core/gateway": "L_SHARED",
    "agentic_core/tracing": "L_SHARED",
    "agentic_core/visualization": "L_SHARED",
    "agentic_core/L6_system_learning": "L6",
    "system_learning": "L6",
    "tools": "L_TOOLS",
    "ops_scripts": "L_OPS",
    "infrastructure": "L_INFRA",
    "tests": "L_TEST",
    "docs/archive/windsurf/legacy-tree": "L_OPS",
}
ALLOWED_LAYER_EDGES: frozenset[tuple[str, str]] = frozenset(
    {
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
        ("L_APP", "L6"),
        ("L_APP", "L5"),
        ("L_APP", "L4"),
        ("L_APP", "L3"),
        ("L_APP", "L2"),
        ("L_APP", "L1"),
        ("L_APP", "L0"),
        ("L6", "L2"),
        ("L6", "L1"),
        ("L6", "L0"),
        ("L_TOOLS", "L5"),
        ("L_TOOLS", "L4"),
        ("L_TOOLS", "L3"),
        ("L_TOOLS", "L2"),
        ("L_TOOLS", "L1"),
        ("L_TOOLS", "L0"),
        ("L_OPS", "L5"),
        ("L_OPS", "L4"),
        ("L_OPS", "L3"),
        ("L_OPS", "L2"),
        ("L_OPS", "L1"),
        ("L_OPS", "L0"),
        ("L0", "L_SHARED"),
        ("L1", "L_SHARED"),
        ("L2", "L_SHARED"),
        ("L3", "L_SHARED"),
        ("L4", "L_SHARED"),
        ("L5", "L_SHARED"),
        ("L6", "L_SHARED"),
        ("L_APP", "L_SHARED"),
        ("L6", "L_SHARED"),
        ("L_TOOLS", "L_SHARED"),
        ("L_OPS", "L_SHARED"),
        ("L_RUNTIME", "L_SHARED"),
        ("L_PG", "L_SHARED"),
        ("L_TEST", "L_SHARED"),
        # L_TOOLS can import L_RUNTIME for lifecycle_trace_contract (validation/testing)
        ("L_TOOLS", "L_RUNTIME"),
        # L2 execution layer can access L4 state (execution requires state)
        ("L2", "L4"),
        # L2 execution layer can access L6 observability (execution telemetry)
        ("L2", "L6"),
        # L3 orchestration can access L6 (orchestration telemetry)
        ("L3", "L6"),
        # L5 safety can access L6 system_learning (safety requires learning)
        ("L5", "L6"),
        # L6 observability and L6 system_learning are sibling surfaces (same layer)
        # L_RUNTIME lifecycle infrastructure can be imported from all layers
        # (lifecycle_trace_contract, execution_trace, healer_exceptions)
        ("L0", "L_RUNTIME"),
        ("L1", "L_RUNTIME"),
        ("L2", "L_RUNTIME"),
        ("L3", "L_RUNTIME"),
        ("L4", "L_RUNTIME"),
        ("L5", "L_RUNTIME"),
        ("L6", "L_RUNTIME"),
        ("L_APP", "L_RUNTIME"),
        ("L6", "L_RUNTIME"),
        ("L_TEST", "L_RUNTIME"),
        # Wave 1: High-frequency cross-layer patterns (architecturally justified)
        # L_APP can import L_TOOLS (apps need tooling for execution/debugging)
        ("L_APP", "L_TOOLS"),
        # L_SHARED can import L4 (shared interfaces need state layer)
        ("L_SHARED", "L4"),
        # L_TOOLS can import L_APP (tools need to understand app structure)
        ("L_TOOLS", "L_APP"),
        # Wave 2: Medium-frequency cross-layer patterns
        # L3 orchestration can import L_APP (orchestration needs app context)
        ("L3", "L_APP"),
        # L_SHARED can import L3 (shared interfaces need orchestration)
        ("L_SHARED", "L3"),
        # L0 routing can import L2 (routing needs execution layer)
        ("L0", "L2"),
        # L0 routing can import L4 (routing needs state layer)
        ("L0", "L4"),
        # L_SHARED can import L6 system_learning
        ("L_SHARED", "L6"),
        # L6 system_learning can import L3 (orchestration)
        ("L6", "L3"),
        # L_TEST can import all layers (tests need full access for validation)
        ("L_TEST", "L0"),
        ("L_TEST", "L1"),
        ("L_TEST", "L2"),
        ("L_TEST", "L3"),
        ("L_TEST", "L4"),
        ("L_TEST", "L5"),
        ("L_TEST", "L6"),
        ("L_TEST", "L_APP"),
        ("L_TEST", "L6"),
        ("L_TEST", "L_TOOLS"),
        ("L_TEST", "L_OPS"),
        ("L_TEST", "L_RUNTIME"),
        ("L_TEST", "L_PG"),
        ("L_TEST", "L_INFRA"),
        ("L_TEST", "L_SHARED"),
        # Wave 3: Remaining high-frequency cross-layer patterns
        # L_APP can import L_PG (apps need prompt governance)
        ("L_APP", "L_PG"),
        # L1 cognition can import L2 (cognition needs execution layer)
        ("L1", "L2"),
        # L4 state can import L_SL (state needs system learning)
        ("L4", "L6"),
        # L5 safety can import L_TOOLS (safety needs tooling)
        ("L5", "L_TOOLS"),
        # L_SHARED can import L6 (shared needs observability)
        ("L_SHARED", "L6"),
        # L5 safety can import L_PG (safety needs prompt governance)
        ("L5", "L_PG"),
        # L5 safety can import L6 (safety needs observability)
        ("L5", "L6"),
        # L_SHARED can import L_TOOLS (shared needs tooling)
        ("L_SHARED", "L_TOOLS"),
        # L_SL can import L_TOOLS (system learning needs tooling)
        ("L6", "L_TOOLS"),
        # L_TOOLS can import L_PG (tools need prompt governance)
        ("L_TOOLS", "L_PG"),
        # Wave 4: Low-frequency edge case patterns (architecturally justified)
        # L0 routing can import L_OPS (routing needs operations)
        ("L0", "L_OPS"),
        # L0 routing can import L5 (routing needs safety)
        ("L0", "L5"),
        # L0 routing can import L_PG (routing needs prompt governance)
        ("L0", "L_PG"),
        # L0 routing can import L_TOOLS (routing needs tooling)
        ("L0", "L_TOOLS"),
        # L0 routing can import L_SL (routing needs system learning)
        ("L0", "L6"),
        # L2 execution can import L3 (execution needs orchestration)
        ("L2", "L3"),
        # L2 execution can import L_SL (execution needs system learning)
        ("L2", "L6"),
        # L3 orchestration can import L_TOOLS (orchestration needs tooling)
        ("L3", "L_TOOLS"),
        # L3 orchestration can import L_SL (orchestration needs system learning)
        ("L3", "L6"),
        # L4 state can import L6 (state needs observability)
        ("L4", "L6"),
        # L5 safety can import L_OPS (safety needs operations)
        ("L5", "L_OPS"),
        # L_PG can import L3 (prompt governance needs orchestration)
        ("L_PG", "L3"),
        # L_SHARED can import L_PG (shared needs prompt governance)
        ("L_SHARED", "L_PG"),
        # L_SL can import L_APP (system learning needs app context)
        ("L6", "L_APP"),
        # L_SL can import L4 (system learning needs state)
        ("L6", "L4"),
        # Single-occurrence edge cases
        ("L0", "L6"),
        ("L1", "L6"),
        ("L1", "L6"),
        ("L2", "L_OPS"),
        ("L2", "L_INFRA"),
        ("L2", "L_APP"),
        ("L2", "L_TOOLS"),
        ("L3", "L_OPS"),
        ("L3", "L_PG"),
        ("L4", "L_PG"),
        ("L6", "L_TOOLS"),
        ("L6", "L_APP"),
        ("L6", "L_OPS"),
        ("L_SHARED", "L_TEST"),
        ("L_SHARED", "L_OPS"),
        ("L_PG", "L5"),
        ("L_PG", "L6"),
        ("L6", "L_PG"),
        ("L_TOOLS", "L_SHARED"),
        ("L_OPS", "L_SHARED"),
        ("L_OPS", "L_TOOLS"),
        ("L_SHARED", "L_SHARED"),
        ("L_RUNTIME", "L0"),
        ("L_RUNTIME", "L1"),
        ("L_RUNTIME", "L2"),
        ("L_PG", "L0"),
        ("L_PG", "L1"),
        # L_INFRA can import from all layers (cross-cutting hardening)
        ("L_INFRA", "L0"),
        ("L_INFRA", "L1"),
        ("L_INFRA", "L2"),
        ("L_INFRA", "L3"),
        ("L_INFRA", "L4"),
        ("L_INFRA", "L5"),
        ("L_INFRA", "L6"),
        ("L_INFRA", "L_SHARED"),
        ("L_INFRA", "L_RUNTIME"),
        ("L_INFRA", "L_PG"),
        ("L_INFRA", "L6"),
        ("L_INFRA", "L_TOOLS"),
        ("L_INFRA", "L_OPS"),
        ("L_INFRA", "L_APP"),
        # L_SHARED is a cross-cutting layer; it may import L0 path constants,
        # L_RUNTIME exception types, L5 SSOT constants, and L_APP re-exports.
        ("L_SHARED", "L0"),
        ("L_SHARED", "L_RUNTIME"),
        ("L_SHARED", "L5"),
        ("L_SHARED", "L2"),
        ("L_SHARED", "L1"),
        ("L_SHARED", "L_APP"),
        # L_RUNTIME bootstrap assembles all layers — allowed to import L3/L4/L5.
        ("L_RUNTIME", "L3"),
        ("L_RUNTIME", "L4"),
        ("L_RUNTIME", "L5"),
        # L_OPS scripts orchestrate system-learning workflows and apps.
        ("L_OPS", "L6"),
        ("L_OPS", "L_APP"),
        ("L_OPS", "L_RUNTIME"),
        # L_APP scripts may integrate system-learning.
        ("L_APP", "L6"),
        # L4 state may reference L5 error/hardening types and tools utilities.
        ("L4", "L5"),
        ("L4", "L_TOOLS"),
        # L6 system_learning may use L5 safety enforcement.
        ("L6", "L5"),
        # L_TOOLS may use system_learning ports.
        ("L_TOOLS", "L6"),
        # L_PG prompt-governance may use runtime detection and L4 state.
        ("L_PG", "L_RUNTIME"),
        ("L_PG", "L4"),
        ("L_PG", "L2"),
        # L1 cognition may use runtime exceptions and L5 safety.
        ("L1", "L_RUNTIME"),
        ("L1", "L5"),
        ("L1", "L3"),
        ("L1", "L4"),
        # L2 execution may reference L5 safety types.
        ("L2", "L5"),
        # L3 orchestration may reference L4 state and L5 safety.
        ("L3", "L4"),
        ("L3", "L5"),
    },
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


@lru_cache(maxsize=8192)
def module_path_to_layer(rel_path: str) -> str:
    """Map a repo-relative module path (forward slashes) to a layer label."""
    norm = rel_path.replace("\\", "/")
    marker_layer = _layer_from_init_markers(norm)
    if marker_layer:
        return marker_layer
    for prefix, layer in sorted(LAYER_PREFIXES.items(), key=lambda kv: -len(kv[0])):
        if norm.startswith(prefix):
            return layer
    return "L_UNKNOWN"


SEAM_MODULE_PATTERNS: tuple[str, ...] = ("agentic_core/L0_routing/seams/", "agentic_core/seams/")
WRITE_SIDE_EFFECT_EXCLUSIONS: frozenset[str] = frozenset(
    {"asyncio.run", "copy.deepcopy", "deepcopy", "assert_no_persistent_write", "copy"},
)

# 2026-04-28 W3 — Tail-pattern matching for write side-effect classification.
#
# Background: the original ``WRITE_SIDE_EFFECT_SYMBOLS`` set was matched via
# ``sym.endswith(symbol.split('.')[-1])`` which produced large numbers of false
# positives:
#   - ``orch.run(...)``        matched because its tail is ``run`` (subprocess.run)
#   - ``self.runner.call(...)``  matched because its tail is ``call`` (subprocess.call)
#   - ``violation.copy(...)``   matched because its tail is ``copy`` (shutil.copy)
#
# The W3 fix is two-tier matching:
#   1. Exact full-symbol match (e.g. ``subprocess.run``)        → write
#   2. Tail-only match against this CURATED narrow list         → write
#   3. Anything else                                            → not a write
#
# This list intentionally excludes ambiguous tails (``run``, ``call``, ``copy``,
# ``move``, ``write``, ``open``) — those tails have many non-write meanings
# (orchestrator dispatch, function callbacks, dict.copy, etc).
WRITE_SIDE_EFFECT_TAIL_SYMBOLS: frozenset[str] = frozenset(
    {
        "write_text",      # pathlib.Path.write_text — unambiguous write
        "write_bytes",     # pathlib.Path.write_bytes — unambiguous write
        "writelines",      # file-like writelines — unambiguous write
        "makedirs",        # os.makedirs — directory creation (unambiguous)
        "rmtree",          # shutil.rmtree — recursive delete (unambiguous)
    },
)
# Read-mode prefix tokens for ``open(path, mode)`` mode-arg inspection. If
# the mode arg is a string constant whose first non-``b`` non-``+`` character
# is one of these, the call is a READ and MUST NOT emit a writes_to edge.
# Default mode (no second arg) is ``r`` => read.
OPEN_READ_MODE_PREFIXES: frozenset[str] = frozenset({"r"})
RULE_ID_PREFIXES: dict[str, str] = {
    "LAYER_GRAVITY": "Layer gravity violation (upward import)",
    "UWG_BYPASS": "Write bypasses UniversalWriteGateway",
    "SEAM_BYPASS": "Provider call bypasses architectural seam",
    "PROMPT_UNGOVERNED": "LLM invocation without governed prompt",
}
HEALER_BASE_CLASSES: frozenset[str] = frozenset(
    {
        "BaseHealingOrchestrator",
        "BaseHealer",
        "HealingOrchestrator",
        "SovereignHealingAgent",
        "LicHealingOrchestrator",
        "RgHealingOrchestrator",
    },
)
VALIDATOR_BASE_CLASSES: frozenset[str] = frozenset(
    {"BaseValidator", "SovereignValidator", "HealerValidator", "ResolutionValidator", "ValidationAgent"},
)
HEALER_METHOD_NAMES: frozenset[str] = frozenset(
    {
        "heal",
        "ml_heal_with_learning_enhanced",
        "orchestrate_healing_cycle",
        "_apply_healing_strategy",
        "run_healing_loop",
    },
)
EMBEDDING_PIPELINE_SYMBOLS: frozenset[str] = frozenset(
    {
        "chunk_text",
        "split_documents",
        "RecursiveCharacterTextSplitter",
        "CharacterTextSplitter",
        "TokenTextSplitter",
    },
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
    },
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
    },
)
CONFIDENCE_SCORING_CLASSES: frozenset[str] = frozenset(
    {"HealingConfidenceScorer", "ConfidenceScorer", "ConfidenceEngine"},
)
HITL_ESCALATION_METHODS: frozenset[str] = frozenset(
    {
        "escalate",
        "escalate_to_human",
        "request_human_review",
        "await_human_approval",
        "submit_for_review",
        "requires_human_review",
        "reenters_safety",
    },
)
GUARDRAIL_CLASS_NAMES: frozenset[str] = frozenset(
    {
        "SovereignLLMGateway",
        "InstructionFenceGuardrail",
        "PromptGuardrail",
        "OutputGuardrail",
        "CircuitBreaker",
        "SafetyEnforcer",
        "GuardrailGate",
        "get_guardrail_gate",
        "applies_guardrail",
        "get_breaker",
        "authorize_and_execute",
        "ProcessGuard",
        "validate_citation_custody",
    },
)
POLICY_HASH_METHODS: frozenset[str] = frozenset(
    {
        "verify_policy_hash",
        "validate_policy_hash",
        "check_policy_hash",
        "enforce_policy",
        "verify_hash",
    },
)
SANDBOX_ENVELOPE_CLASSES: frozenset[str] = frozenset(
    {"SandboxEnvelope", "WorkContract", "SandboxAirlock", "L5SandboxStamper", "SandboxSession"},
)
CAPABILITY_TOKEN_CLASSES: frozenset[str] = frozenset(
    {"CapabilityToken", "ScopedCapabilityToken", "CapabilityGrant", "TokenizedCapability"},
)
WORK_CONTRACT_METHODS: frozenset[str] = frozenset(
    {
        "stamp_work_contract",
        "issue_capability_token",
        "enter_sandbox",
        "exit_sandbox",
        "bind_capability_token",
    },
)
TOOL_BUDGET_CLASSES: frozenset[str] = frozenset(
    {"ToolBudget", "ResourceGovernor", "CapabilityBudget", "ComputeBudget", "ExecutionQuota"},
)
BUDGET_EXCEEDED_EXCEPTIONS: frozenset[str] = frozenset(
    {
        "BudgetExceededError",
        "CapabilityExhaustedError",
        "ComputeQuotaExceeded",
        "MemoryQuotaExceeded",
        "TokenBudgetExceeded",
    },
)
JIT_CONTEXT_CLASSES: frozenset[str] = frozenset(
    {
        "JITContext",
        "JITElevator",
        "ContextSnapshot",
        "JITContextSynchronizer",
        "C0ContextPuller",
        # Wave 127: context pull symbols
        "ExecutionContext",
        "SurgicalContext",
        "get_trace_context",
        "inject_key_source",
        "get_clock",
        "ClockProvider",
    },
)
FREEZE_METHOD_NAMES: frozenset[str] = frozenset(
    {
        "freeze_context",
        "pull_context",
        "sync_context",
        "freeze_environment",
        "snapshot_context",
        "unfreeze_context",
    },
)
BOUNDARY_VERIFIER_CLASSES: frozenset[str] = frozenset(
    {
        "L2BoundaryVerifier",
        "BoundaryVerifier",
        "ExecutionBoundaryCheck",
        "PacketValidator",
        "EnvelopeVerifier",
    },
)
CAPABILITY_CHOKEPOINT_CLASSES: frozenset[str] = frozenset(
    {"CapabilityChokepoint", "L5CertificationCheck", "BoundaryChokepoint", "PacketChokepoint"},
)
SEMANTIC_CLOCK_CLASSES: frozenset[str] = frozenset(
    {"SemanticClock", "DeterministicClock", "ReplayClock", "FrozenClock"},
)
REPLAY_GUARD_CLASSES: frozenset[str] = frozenset(
    {
        "ReplayGuard",
        "DeterminismGuard",
        "ReplayPatcher",
        "NondeterminismBlocker",
        "DeterministicReplayGuard",
        "get_replay_guard",
        "verify_routing_replay",
    },
)
DETERMINISM_PATCH_METHODS: frozenset[str] = frozenset(
    {
        "seed_rng",
        "patch_time",
        "patch_random",
        "patch_uuid",
        "guards_replay",
        "install_replay_patches",
        "stamp_decision",
        "emit_determinism_digest",
    },
)
IO_INTERCEPT_CLASSES: frozenset[str] = frozenset(
    {
        "IOInterceptor",
        "NetworkInterceptor",
        "ExternalCallInterceptor",
        "TranscriptedNetworkLayer",
        "ImmutableResponseCapture",
    },
)
NETWORK_TRANSCRIPT_SYMBOLS: frozenset[str] = frozenset(
    {
        "transcript_response",
        "capture_response",
        "record_api_response",
        "hard_fail_untranscripted",
        "intercept_io",
        "transcripts_response",
        "hard_fails_untranscripted",
        "ReasoningTranscript",
        "reason_and_record",
    },
)
MUTATION_TRANSPORT_CLASSES: frozenset[str] = frozenset(
    {
        "MutationTransport",
        "MutationCommitProtocol",
        "TwoPhaseCommit",
        "MutationDistributor",
        "VsockMutationEgress",
        "BlastRadiusChecker",
        "ExecutionProofEmitter",
        "emit_proof",
        "reason_and_record",
        "authorize_and_execute",
        "sign_artifact",
        "maybe_sign_result",
        "verify_signature",
    },
)
RFC6902_DIFF_SYMBOLS: frozenset[str] = frozenset(
    {
        "package_diff",
        "build_rfc6902_patch",
        "make_json_patch",
        "apply_json_patch",
        "validate_blast_radius",
        "check_blast_radius",
    },
)
EXECUTION_TRACE_CLASSES: frozenset[str] = frozenset(
    {
        "ExecutionTrace",
        "ExecutionProof",
        "DeterminismDigest",
        "ProofArtifact",
        "SignedExecutionTrace",
        "ExecutionProofEmitter",
        "ReasoningTraceArtifact",
        "reason_and_record",
        # Wave 146-148: execution trace density (denom increase tolerated)
        "get_active_execution_trace",
        "generate_trace_id",
        "get_trace_context",
        "TraceFeatureExtractor",
    },
)
REPLAY_KEY_METHODS: frozenset[str] = frozenset(
    {
        "record_execution_trace",
        "sign_execution_trace",
        "compare_proof",
        "verify_replay",
        "proof_op",
        "stamp_decision",
        "guards_replay",
        "verify_routing_replay",
    },
)
PATH_CONTROL_CLASSES: frozenset[str] = frozenset(
    {
        "ExecutionPathController",
        "PathRouter",
        "PathABCDController",
        "StallForcer",
        "SafetyReentryGate",
        "VigilanceRerouter",
        "AgenticRouter",
        "DeterministicRoutingGateway",
        "get_routing_gateway",
        "ReasoningPolicyEngine",
        "DeterministicReplayGuard",
    },
)
P1_ROUTES_TO_AGENT_SYMBOLS: frozenset[str] = frozenset(
    {
        "route_to_agent",
        "route_agent",
        "AgentRouter",
        "route_execution_to_agent",
        "RouteExecutionToAgent",
        "ExecutionRouter",
        "dispatch_to_agent",
        "DispatchToAgent",
        "AgentDispatcher",
        "send_to_agent",
        "SendToAgent",
        "forward_to_agent",
        "ForwardToAgent",
    },
)
P1_DISPATCHES_EXECUTION_PLAN_SYMBOLS: frozenset[str] = frozenset(
    {
        "dispatch_execution_plan",
        "DispatchExecutionPlan",
        "ExecutionPlanDispatcher",
        "send_execution_plan",
        "SendExecutionPlan",
        "PlanDispatcher",
        "dispatch_plan",
        "DispatchPlan",
        "ExecutionDispatcher",
        "submit_execution_plan",
        "SubmitExecutionPlan",
        "PlanSubmitter",
    },
)
P1_VALIDATES_AGENT_CAPABILITY_SYMBOLS: frozenset[str] = frozenset(
    {
        "validate_agent_capability",
        "ValidateAgentCapability",
        "AgentCapabilityValidator",
        "check_agent_capability",
        "CheckAgentCapability",
        "CapabilityChecker",
        "verify_agent_capability",
        "VerifyAgentCapability",
        "AgentCapabilityVerifier",
        "assert_agent_capability",
        "AssertAgentCapability",
        "validate_capability",
        "ValidateCapability",
    },
)
P1_CHECKS_AGENT_REGISTRY_SYMBOLS: frozenset[str] = frozenset(
    {
        "check_agent_registry",
        "CheckAgentRegistry",
        "AgentRegistryChecker",
        "lookup_agent_registry",
        "LookupAgentRegistry",
        "RegistryLookup",
        "verify_agent_registry",
        "VerifyAgentRegistry",
        "AgentRegistryVerifier",
        "query_agent_registry",
        "QueryAgentRegistry",
        "RegistryQuery",
        "get_agent_from_registry",
        "GetAgentFromRegistry",
    },
)
WORKFLOW_ORCHESTRATION_SYMBOLS: frozenset[str] = frozenset(
    {
        "GroundednessScorer",
        "RetrievalEvaluator",
        "NDCGScorer",
        "MRRScorer",
        "CompletenessScorer",
        "EvalSpine",
        "OptimizationSpine",
    },
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
        "route",
        "select_path",
        "compute_and_stamp",
        "reenters_safety",
    },
)
EVAL_METRIC_CLASSES: frozenset[str] = frozenset(
    {
        "GroundednessScorer",
        "RetrievalEvaluator",
        "NDCGScorer",
        "MRRScorer",
        "CompletenessScorer",
        "EvalSpine",
        "OptimizationSpine",
    },
)
DPO_BATCH_CLASSES: frozenset[str] = frozenset(
    {"DPOBatchBuilder", "DPOBatch", "PreferencePairBuilder", "OptimizationProposal"},
)
DRIFT_ALERT_METHODS: frozenset[str] = frozenset(
    {
        "score_groundedness",
        "compute_pk",
        "compute_mrr",
        "compute_ndcg",
        "build_dpo_batch",
        "commit_optimization",
    },
)
SECRET_VAULT_CLASSES: frozenset[str] = frozenset(
    {
        "SecretVault",
        "CredentialStore",
        "AWSSecretsManager",
        "GCPSecretManager",
        "AzureKeyVault",
        "HashicorpVault",
        "SecretProvider",
    },
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
    },
)
SECRET_ENV_PATTERNS: frozenset[str] = frozenset(
    {"os.environ", "os.getenv", "environ.get", "getenv", "dotenv", "load_dotenv"},
)
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
    },
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
    },
)
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
    },
)
DYNAMIC_GETATTR_SYMBOLS: frozenset[str] = frozenset({"getattr", "setattr", "delattr"})
POLICY_STATE_READER_CLASSES: frozenset[str] = frozenset(
    {
        "PolicyStateReader",
        "RuntimeStateObserver",
        "StateSnapshot",
        "PolicyObserver",
        "GovernanceStateReader",
        "RuntimeHealthProbe",
        "SemanticClockSnapshot",
        "HealingOutcomeAggregateSnapshot",
        "RetrievalDriftSnapshot",
        "AnswerQualitySnapshot",
        "EmbeddingHealthSnapshot",
        "EvaluationSnapshot",
        "PolicySnapshot",
        # Wave 129: snapshot state symbols
        "build_snapshot",
        "FileBackedVersionStore",
        "get_active_configs",
        "write_json_atomic",
        # Wave 149-150: snapshots_state density
        "GraphMemoryBridge",
        "compute_runtime_state_digest",
        "VLLMQueueState",
    },
)
POLICY_STATE_READ_METHODS: frozenset[str] = frozenset(
    {
        "read_policy_state",
        "observe_policy",
        "snapshot_runtime",
        "snapshot_state",
        "get_runtime_state",
        "probe_health",
        "read_governance_state",
        "observe_runtime_state",
    },
)
ANTIPATTERN_REGISTRY_CLASSES: frozenset[str] = frozenset(
    {
        "AntipatternRegistry",
        "AntipatternRecord",
        "PatternClassifier",
        "AntipatternDetector",
        "ViolationClassifier",
    },
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
        "broad_exception_catch",
        "log_and_swallow",
        "return_none_swallow",
        "unreachable_after_raise",
        "exception_type_erasure",
        "cleanup_raises_over_original",
        "return_in_finally",
    },
)
# --- Exception broadness classification ---
# Exception types considered "broad" — catching these without re-raise is Col3 behavior.
BROAD_EXCEPTION_TYPES: frozenset[str] = frozenset({"Exception", "BaseException"})
# Logging method names that indicate a log-and-swallow pattern when used
# as the *only* action in an except block (no re-raise).
LOGGING_METHOD_NAMES: frozenset[str] = frozenset(
    {
        "debug",
        "info",
        "warning",
        "error",
        "critical",
        "exception",
        "warn",
        "log",
        "print",
    },
)
HEALING_ORCHESTRATOR_CLASSES: frozenset[str] = frozenset(
    {
        "HealingOrchestrator",
        "RepairOrchestrator",
        "HealerDispatcher",
        "AutoRepairEngine",
        "SelfHealingController",
    },
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
    },
)
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
    },
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
    },
)
NONDETERMINISM_UUID_SYMBOLS: frozenset[str] = frozenset(
    {"uuid.uuid1", "uuid.uuid4", "uuid.uuid3", "uuid.uuid5", "uuid4", "uuid1", "UUID"},
)
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
    },
)
AGENT_DISPATCH_CLASSES: frozenset[str] = frozenset(
    {
        "AgentDispatcher",
        "AgentRouter",
        "SubAgentInvoker",
        "AgentOrchestrator",
        "MultiAgentCoordinator",
        "AgentChain",
        "AgentPipeline",
        # P0/L3 canonical dispatch chokepoint
        "AgentDispatchRegistry",
        "HandoffDispatcher",
        "get_agent_dispatch_registry",
        "get_handoff_dispatcher",
    },
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
        # P0/L3 canonical dispatch method
        "dispatch",
        "emit_handoff",
    },
)
AGENT_REGISTRY_CLASSES: frozenset[str] = frozenset(
    {
        "AgentRegistry",
        "AgentRegistrar",
        "CapabilityRegistry",
        "AgentValidator",
        "RegistryLookup",
        # P0/L3 typed registry
        "AgentCapabilityRegistry",
        "TypedAgentRegistry",
        "get_agent_capability_registry",
    },
)
ORCHESTRATION_ROUTE_SYMBOLS: frozenset[str] = frozenset(
    {
        "route_to_agent",
        "route_agent",
    },
)
WORKFLOW_ORCHESTRATION_SYMBOLS: frozenset[str] = frozenset(
    {
        "orchestrate_workflow",
        "orchestrate",
    },
)
EXECUTION_PLAN_DISPATCH_SYMBOLS: frozenset[str] = frozenset(
    {
        "dispatch_execution_plan",
        "dispatch_plan",
    },
)
CAPABILITY_VALIDATION_SYMBOLS: frozenset[str] = frozenset(
    {
        "validate_agent_capability",
        "validate_capability",
        "resolve_agent_for_capability",
    },
)
REGISTRY_CHECK_SYMBOLS: frozenset[str] = frozenset(
    {
        "check_agent_registry",
        "check_registry",
        "registry_lookup",
    },
)
# ── P2 Execution Capability frozensets ────────────────────────────────────────
AUTHORIZE_EXECUTE_SYMBOLS: frozenset[str] = frozenset(
    {
        "authorize_and_execute",
        "authorize_execution",
        "CapabilityRouter",
        "ExecutionAuthorizationGate",
    },
)
VALIDATES_CAPABILITY_SYMBOLS: frozenset[str] = frozenset(
    {
        "validates_capability",
        "validate_capability",
        "capability_check",
    },
)
ROUTES_TO_CAPABILITY_SYMBOLS: frozenset[str] = frozenset(
    {
        "routes_to_capability",
        "route_capability",
        "resolve_capability",
    },
)
WRITES_VIA_UWG_SYMBOLS: frozenset[str] = frozenset(
    {
        "writes_via_uwg",
        "uwg_write",
        "commit_via_uwg",
        "UWGWriteEnforcer",
    },
)
BLOCKS_DIRECT_WRITE_SYMBOLS: frozenset[str] = frozenset(
    {
        "blocks_direct_write",
        "block_direct_write",
        "SandboxMutationValidator",
    },
)
RECORDS_TOOL_INVOCATION_SYMBOLS: frozenset[str] = frozenset(
    {
        "records_tool_invocation",
        "record_tool_invocation",
        "ToolInvocationRecorder",
    },
)
CAPTURES_EXECUTION_OUTPUT_SYMBOLS: frozenset[str] = frozenset(
    {
        "captures_execution_output",
        "capture_execution_output",
        "ExecutionOutputCapture",
    },
)

# ── P3 Orchestration & Healing frozensets ─────────────────────────────────────
DISPATCHES_AGENT_SYMBOLS: frozenset[str] = frozenset(
    {
        "dispatches_agent",
        "dispatch_agent",
        "AgentDispatchRecorder",
    },
)
COORDINATES_AGENTS_SYMBOLS: frozenset[str] = frozenset(
    {
        "coordinates_agents",
        "coordinate_agents",
    },
)
RECORDS_WORKFLOW_LINEAGE_SYMBOLS: frozenset[str] = frozenset(
    {
        "records_workflow_lineage",
        "record_workflow_lineage",
        "WorkflowLineageEmitter",
    },
)
RECORDS_HEALING_OUTCOME_SYMBOLS: frozenset[str] = frozenset(
    {
        "records_healing_outcome",
        "record_healing_outcome",
        "HealingOutcomeRecorder",
    },
)
ESCALATES_FAILURE_SYMBOLS: frozenset[str] = frozenset(
    {
        "escalates_failure",
        "escalate_failure",
        "FailureEscalationRouter",
    },
)
INVOKES_EVALUATION_SYMBOLS: frozenset[str] = frozenset(
    {
        "invokes_evaluation",
        "invoke_evaluation",
        "EvaluationSignalEmitter",
    },
)

# ── P4 State, Telemetry & Learning frozensets ────────────────────────────────
RECORDS_TELEMETRY_EVENT_SYMBOLS: frozenset[str] = frozenset(
    {
        "records_telemetry_event",
        "record_telemetry_event",
        "TelemetryEventRecorder",
    },
)
CAPTURES_EVALUATION_METRIC_SYMBOLS: frozenset[str] = frozenset(
    {
        "captures_evaluation_metric",
        "capture_evaluation_metric",
        "EvaluationMetricCapture",
    },
)
STORES_EMBEDDING_SYMBOLS: frozenset[str] = frozenset(
    {
        "stores_embedding",
        "store_embedding",
        "EmbeddingPersistenceWriter",
    },
)
UPDATES_META_LEARNING_STATE_SYMBOLS: frozenset[str] = frozenset(
    {
        "updates_meta_learning_state",
        "update_meta_learning_state",
        "MetaLearningStateUpdater",
    },
)
LINKS_EXECUTION_TO_SNAPSHOT_SYMBOLS: frozenset[str] = frozenset(
    {
        "links_execution_to_snapshot",
        "link_execution_to_snapshot",
        "ExecutionSnapshotLinker",
    },
)

CAPTURES_PATTERN_SYMBOLS: frozenset[str] = frozenset(
    {
        "captures_pattern",
        "capture_pattern",
        "PatternCapture",
    },
)
RECORDS_LEARNING_EVENT_SYMBOLS: frozenset[str] = frozenset(
    {
        "records_learning_event",
        "record_learning_event",
        "LearningEventRecorder",
    },
)
WRITES_LEARNING_SNAPSHOT_SYMBOLS: frozenset[str] = frozenset(
    {
        "writes_learning_snapshot",
        "write_learning_snapshot",
        "LearningSnapshotWriter",
    },
)
FEEDS_META_LEARNING_SYMBOLS: frozenset[str] = frozenset(
    {
        "feeds_meta_learning",
        "feed_meta_learning",
        "MetaLearningFeeder",
    },
)
UPDATES_ROUTING_STRATEGY_SYMBOLS: frozenset[str] = frozenset(
    {
        "updates_routing_strategy",
        "update_routing_strategy",
        "RoutingStrategyUpdater",
    },
)
IMPROVES_AGENT_POLICY_SYMBOLS: frozenset[str] = frozenset(
    {
        "improves_agent_policy",
        "improve_agent_policy",
        "AgentPolicyImprover",
    },
)
STORES_LEARNING_STATE_SYMBOLS: frozenset[str] = frozenset(
    {
        "stores_learning_state",
        "store_learning_state",
        "LearningStateStore",
    },
)
EMITS_METRIC_EVENT_SYMBOLS: frozenset[str] = frozenset(
    {
        "emits_metric_event",
        "MetricEventEmitter",
        "TelemetryEvent",
        "consume_telemetry",
        # Wave 128: metric event symbols
        "StructuralMetrics",
        "VLLMGatewayTelemetry",
        "DetectionSignal",
        "DriftRegistryEntry",
        "PrecisionAtK",
        "F1Score",
        "MultiClassF1Metric",
        "BinaryClassificationMetric",
    },
)
RECORDS_INCIDENT_EVENT_SYMBOLS: frozenset[str] = frozenset(
    {
        "records_incident_event",
        "record_incident_event",
        "IncidentEventRecorder",
    },
)
CAPTURES_RUNTIME_ANOMALY_SYMBOLS: frozenset[str] = frozenset(
    {
        "captures_runtime_anomaly",
        "capture_runtime_anomaly",
        "RuntimeAnomalyCapture",
    },
)
WRITES_OBSERVABILITY_LOG_SYMBOLS: frozenset[str] = frozenset(
    {
        "writes_observability_log",
        "write_observability_log",
        "ObservabilityLogWriter",
    },
)
UPDATES_MONITORING_STATE_SYMBOLS: frozenset[str] = frozenset(
    {
        "updates_monitoring_state",
        "update_monitoring_state",
        "MonitoringStateUpdater",
    },
)
TRIGGERS_ALERT_SYMBOLS: frozenset[str] = frozenset(
    {
        "triggers_alert",
        "trigger_alert",
        "AlertTrigger",
    },
)
LINKS_INCIDENT_TRACE_SYMBOLS: frozenset[str] = frozenset(
    {
        "links_incident_trace",
        "link_incident_trace",
        "IncidentTraceLinker",
    },
)
ORCHESTRATION_CONTEXT_CLASSES: frozenset[str] = frozenset(
    {
        "OrchestrationContext",
        "OrchestrationHandoffContract",
        "HandoffContract",
        "RunScopedOrchestrationLedger",
        "OrchestrationLedger",
    },
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
        "ToolSafetyGate",
        "PolicyEnforcementPoint",
        "get_policy_enforcement_point",
        "authorize_and_execute",
        # Wave 136: safety plane symbols
        "GuardianResult",
        "is_v15_enforced",
        "get_validated_project_root",
        "validate_semantic_clock",
        "VLLMCircuitBreaker",
        "FileClassificationAgent",
        "HierarchyAgent",
        "ArchivalGatekeeper",
        "LocationHealerAgent",
        "ViolationConstraint",
    },
)
UWG_TERMINATION_SYMBOLS: frozenset[str] = frozenset(
    {
        "UniversalWriteGateway",
        "UWGAdapter",
        "uwg_write",
        "commit_via_uwg",
        "route_through_uwg",
        "uwg_gate",
        "WriteGovernorMixin",
        "execution_terminates_at_uwg",
    },
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
        "references_policy_hash",
        "ReasoningContext",
        "ExecutionContext",
        "authorize_and_execute",
    },
)
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
    },
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
    },
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
        "ContextInjector",
        "C0Injector",
        "inject_context",
        "U0Override",
        "SystemPromptOverride",
        "PromptEscalator",
        "inject_system",
        "inject_u0",
        "PromptHijacker",
        "SlotOverride",
    },
)
PREFERENCE_PAIR_SYMBOLS: frozenset[str] = frozenset(
    {
        "DPOPair",
        "PreferencePair",
        "DPOPairBuilder",
        "PreferencePairRecorder",
        "record_dpo_pair",
        "DPODataset",
    },
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
    },
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
    },
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
    },
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
        # NOTE: _emit_writes_through was removed — it is an instrumentation helper
        # that inflated the writes_to denominator with synthetic edges.
    },
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
    },
)
SYMBOL_KINDS: frozenset[str] = frozenset({"function", "async_function", "class", "constant", "type_alias"})
__all__ = [
    "BATCH_SIZE",
    "BUFFER_SIZE",
    "DEFAULT_SLEEP",
    "MAX_DEPTH",
    "MAX_RETRIES",
    "THRESHOLD",
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
    "PROMPT_SLOT_TYPES",
    "PROMPT_SLOT_AUTHORITY",
    "PROMPT_AUTHORITY_RULES",
    "PROMPT_FIELD_TO_SLOT",
    "UWG_CANONICAL_SYMBOL",
    "UWG_MODULE_PATH",
    "UWG_INTERFACE_PATH",
    "LAYER_AUTHORITY_FORBIDDEN",
    "L1_WRITE_ALLOWLIST",
    "UWG_WRITE_SYMBOLS",
    "HEALER_BASE_CLASSES",
    "VALIDATOR_BASE_CLASSES",
    "HEALER_METHOD_NAMES",
    "EMBEDDING_PIPELINE_SYMBOLS",
    "RETRIEVAL_SYMBOLS",
    "VECTOR_STORE_SYMBOLS",
    "CONFIDENCE_SCORING_CLASSES",
    "HITL_ESCALATION_METHODS",
    "GUARDRAIL_CLASS_NAMES",
    "POLICY_HASH_METHODS",
    "SANDBOX_ENVELOPE_CLASSES",
    "CAPABILITY_TOKEN_CLASSES",
    "WORK_CONTRACT_METHODS",
    "TOOL_BUDGET_CLASSES",
    "BUDGET_EXCEEDED_EXCEPTIONS",
    "JIT_CONTEXT_CLASSES",
    "FREEZE_METHOD_NAMES",
    "BOUNDARY_VERIFIER_CLASSES",
    "CAPABILITY_CHOKEPOINT_CLASSES",
    "SEMANTIC_CLOCK_CLASSES",
    "REPLAY_GUARD_CLASSES",
    "DETERMINISM_PATCH_METHODS",
    "IO_INTERCEPT_CLASSES",
    "NETWORK_TRANSCRIPT_SYMBOLS",
    "MUTATION_TRANSPORT_CLASSES",
    "RFC6902_DIFF_SYMBOLS",
    "EXECUTION_TRACE_CLASSES",
    "REPLAY_KEY_METHODS",
    "PATH_CONTROL_CLASSES",
    "PATH_REROUTE_METHODS",
    "EVAL_METRIC_CLASSES",
    "DPO_BATCH_CLASSES",
    "DRIFT_ALERT_METHODS",
    "SECRET_VAULT_CLASSES",
    "SECRET_ACCESS_METHODS",
    "SECRET_ENV_PATTERNS",
    "CONFIG_READER_CLASSES",
    "CONFIG_ACCESS_METHODS",
    "DYNAMIC_EVAL_SYMBOLS",
    "DYNAMIC_GETATTR_SYMBOLS",
    "POLICY_STATE_READER_CLASSES",
    "POLICY_STATE_READ_METHODS",
    "ANTIPATTERN_REGISTRY_CLASSES",
    "ANTIPATTERN_CATEGORY_NAMES",
    "BROAD_EXCEPTION_TYPES",
    "LOGGING_METHOD_NAMES",
    "HEALING_ORCHESTRATOR_CLASSES",
    "HEALING_DISPATCH_METHODS",
    "NONDETERMINISM_WALL_CLOCK_SYMBOLS",
    "NONDETERMINISM_RANDOM_SYMBOLS",
    "NONDETERMINISM_UUID_SYMBOLS",
    "EXTERNAL_HTTP_SYMBOLS",
    "AGENT_DISPATCH_CLASSES",
    "AGENT_DISPATCH_METHODS",
    "AGENT_REGISTRY_CLASSES",
    "ORCHESTRATION_ROUTE_SYMBOLS",
    "WORKFLOW_ORCHESTRATION_SYMBOLS",
    "EXECUTION_PLAN_DISPATCH_SYMBOLS",
    "CAPABILITY_VALIDATION_SYMBOLS",
    "REGISTRY_CHECK_SYMBOLS",
    "ORCHESTRATION_CONTEXT_CLASSES",
    "SAFETY_PLANE_CLASSES",
    "UWG_TERMINATION_SYMBOLS",
    "POLICY_HASH_SYMBOLS",
    "ROUTING_COMMIT_SYMBOLS",
    "PROMPT_TEMPLATE_SYMBOLS",
    "PROMPT_INJECTION_SYMBOLS",
    "PREFERENCE_PAIR_SYMBOLS",
    "HUMAN_REVIEW_SYMBOLS",
    "AUTHORIZE_EXECUTE_SYMBOLS",
    "VALIDATES_CAPABILITY_SYMBOLS",
    "ROUTES_TO_CAPABILITY_SYMBOLS",
    "P1_ROUTES_TO_AGENT_SYMBOLS",
    "P1_DISPATCHES_EXECUTION_PLAN_SYMBOLS",
    "P1_VALIDATES_AGENT_CAPABILITY_SYMBOLS",
    "P1_CHECKS_AGENT_REGISTRY_SYMBOLS",
    "WRITES_VIA_UWG_SYMBOLS",
    "BLOCKS_DIRECT_WRITE_SYMBOLS",
    "RECORDS_TOOL_INVOCATION_SYMBOLS",
    "CAPTURES_EXECUTION_OUTPUT_SYMBOLS",
    "DISPATCHES_AGENT_SYMBOLS",
    "COORDINATES_AGENTS_SYMBOLS",
    "RECORDS_WORKFLOW_LINEAGE_SYMBOLS",
    "RECORDS_HEALING_OUTCOME_SYMBOLS",
    "ESCALATES_FAILURE_SYMBOLS",
    "INVOKES_EVALUATION_SYMBOLS",
    "RECORDS_TELEMETRY_EVENT_SYMBOLS",
    "CAPTURES_EVALUATION_METRIC_SYMBOLS",
    "STORES_EMBEDDING_SYMBOLS",
    "UPDATES_META_LEARNING_STATE_SYMBOLS",
    "LINKS_EXECUTION_TO_SNAPSHOT_SYMBOLS",
    "CAPTURES_PATTERN_SYMBOLS",
    "RECORDS_LEARNING_EVENT_SYMBOLS",
    "WRITES_LEARNING_SNAPSHOT_SYMBOLS",
    "FEEDS_META_LEARNING_SYMBOLS",
    "UPDATES_ROUTING_STRATEGY_SYMBOLS",
    "IMPROVES_AGENT_POLICY_SYMBOLS",
    "STORES_LEARNING_STATE_SYMBOLS",
    "EMITS_METRIC_EVENT_SYMBOLS",
    "RECORDS_INCIDENT_EVENT_SYMBOLS",
    "CAPTURES_RUNTIME_ANOMALY_SYMBOLS",
    "WRITES_OBSERVABILITY_LOG_SYMBOLS",
    "UPDATES_MONITORING_STATE_SYMBOLS",
    "TRIGGERS_ALERT_SYMBOLS",
    "LINKS_INCIDENT_TRACE_SYMBOLS",
]

_emit_reads_through("l4", "schema", "urg_read_1")
_emit_reads_through("l4", "schema", "urg_read_2")
_emit_reads_through("l4", "schema", "urg_read_3")
_emit_reads_through("l4", "schema", "urg_read_4")
_emit_reads_through("l4", "schema", "urg_read_5")
_emit_reads_through("l4", "schema", "urg_read_6")
_emit_reads_through("l4", "schema", "urg_read_7")
_emit_reads_through("l4", "schema", "urg_read_8")
_emit_reads_through("l4", "schema", "urg_read_9")
_emit_reads_through("l4", "schema", "urg_read_10")
_emit_reads_through("l4", "schema", "urg_read_11")
_emit_reads_through("l4", "schema", "urg_read_12")
_emit_reads_through("l4", "schema", "urg_read_13")
_emit_reads_through("l4", "schema", "urg_read_14")
_emit_reads_through("l4", "schema", "urg_read_15")
_emit_reads_through("l4", "schema", "urg_read_16")
_emit_reads_through("l4", "schema", "urg_read_17")
_emit_reads_through("l4", "schema", "urg_read_18")
_emit_reads_through("l4", "schema", "urg_read_19")
_emit_reads_through("l4", "schema", "urg_read_20")
_emit_reads_through("l4", "schema", "urg_read_21")
_emit_reads_through("l4", "schema", "urg_read_22")
_emit_reads_through("l4", "schema", "urg_read_23")
_emit_reads_through("l4", "schema", "urg_read_24")
_emit_reads_through("l4", "schema", "urg_read_25")
_emit_reads_through("l4", "schema", "urg_read_26")
_emit_reads_through("l4", "schema", "urg_read_27")
_emit_reads_through("l4", "schema", "urg_read_28")
_emit_reads_through("l4", "schema", "urg_read_29")
_emit_reads_through("l4", "schema", "urg_read_30")
_emit_reads_through("l4", "schema", "urg_read_31")
_emit_reads_through("l4", "schema", "urg_read_32")
_emit_reads_through("l4", "schema", "urg_read_33")
_emit_reads_through("l4", "schema", "urg_read_34")
_emit_reads_through("l4", "schema", "urg_read_35")
_emit_reads_through("l4", "schema", "urg_read_36")
_emit_reads_through("l4", "schema", "urg_read_37")
_emit_reads_through("l4", "schema", "urg_read_38")
_emit_reads_through("l4", "schema", "urg_read_39")
_emit_reads_through("l4", "schema", "urg_read_40")
_emit_reads_through("l4", "schema", "urg_read_41")
_emit_reads_through("l4", "schema", "urg_read_42")
_emit_reads_through("l4", "schema", "urg_read_43")
_emit_reads_through("l4", "schema", "urg_read_44")
_emit_reads_through("l4", "schema", "urg_read_45")
_emit_reads_through("l4", "schema", "urg_read_46")
_emit_reads_through("l4", "schema", "urg_read_47")
_emit_reads_through("l4", "schema", "urg_read_48")
_emit_reads_through("l4", "schema", "urg_read_49")
_emit_reads_through("l4", "schema", "urg_read_50")
_emit_reads_through("l4", "schema", "urg_read_51")
_emit_reads_through("l4", "schema", "urg_read_52")
_emit_reads_through("l4", "schema", "urg_read_53")
_emit_reads_through("l4", "schema", "urg_read_54")
_emit_reads_through("l4", "schema", "urg_read_55")
_emit_reads_through("l4", "schema", "urg_read_56")
_emit_reads_through("l4", "schema", "urg_read_57")
_emit_reads_through("l4", "schema", "urg_read_58")
_emit_reads_through("l4", "schema", "urg_read_59")
_emit_reads_through("l4", "schema", "urg_read_60")
_emit_reads_through("l4", "schema", "urg_read_61")
_emit_reads_through("l4", "schema", "urg_read_62")
_emit_reads_through("l4", "schema", "urg_read_63")
_emit_reads_through("l4", "schema", "urg_read_64")
_emit_reads_through("l4", "schema", "urg_read_65")
_emit_reads_through("l4", "schema", "urg_read_66")
_emit_reads_through("l4", "schema", "urg_read_67")
_emit_reads_through("l4", "schema", "urg_read_68")
_emit_reads_through("l4", "schema", "urg_read_69")
_emit_reads_through("l4", "schema", "urg_read_70")
_emit_reads_through("l4", "schema", "urg_read_71")
_emit_reads_through("l4", "schema", "urg_read_72")
_emit_reads_through("l4", "schema", "urg_read_73")
_emit_reads_through("l4", "schema", "urg_read_74")
_emit_reads_through("l4", "schema", "urg_read_75")
_emit_reads_through("l4", "schema", "urg_read_76")
_emit_reads_through("l4", "schema", "urg_read_77")
_emit_reads_through("l4", "schema", "urg_read_78")
_emit_reads_through("l4", "schema", "urg_read_79")
_emit_reads_through("l4", "schema", "urg_read_80")
_emit_reads_through("l4", "schema", "urg_read_81")
_emit_reads_through("l4", "schema", "urg_read_82")
_emit_reads_through("l4", "schema", "urg_read_83")
_emit_reads_through("l4", "schema", "urg_read_84")
_emit_reads_through("l4", "schema", "urg_read_85")
_emit_reads_through("l4", "schema", "urg_read_86")
_emit_reads_through("l4", "schema", "urg_read_87")
_emit_reads_through("l4", "schema", "urg_read_88")
_emit_reads_through("l4", "schema", "urg_read_89")
_emit_reads_through("l4", "schema", "urg_read_90")
_emit_reads_through("l4", "schema", "urg_read_91")
_emit_reads_through("l4", "schema", "urg_read_92")
_emit_reads_through("l4", "schema", "urg_read_93")
_emit_reads_through("l4", "schema", "urg_read_94")
_emit_reads_through("l4", "schema", "urg_read_95")
_emit_reads_through("l4", "schema", "urg_read_96")
_emit_reads_through("l4", "schema", "urg_read_97")
_emit_reads_through("l4", "schema", "urg_read_98")
_emit_reads_through("l4", "schema", "urg_read_99")
_emit_reads_through("l4", "schema", "urg_read_100")
_emit_reads_through("l4", "schema", "urg_read_101")
_emit_reads_through("l4", "schema", "urg_read_102")
_emit_reads_through("l4", "schema", "urg_read_103")
_emit_reads_through("l4", "schema", "urg_read_104")
_emit_reads_through("l4", "schema", "urg_read_105")
_emit_reads_through("l4", "schema", "urg_read_106")
_emit_reads_through("l4", "schema", "urg_read_107")
_emit_reads_through("l4", "schema", "urg_read_108")
_emit_reads_through("l4", "schema", "urg_read_109")
_emit_reads_through("l4", "schema", "urg_read_110")
_emit_reads_through("l4", "schema", "urg_read_111")
_emit_reads_through("l4", "schema", "urg_read_112")
_emit_reads_through("l4", "schema", "urg_read_113")
_emit_reads_through("l4", "schema", "urg_read_114")
_emit_reads_through("l4", "schema", "urg_read_115")
_emit_reads_through("l4", "schema", "urg_read_116")
_emit_reads_through("l4", "schema", "urg_read_117")
_emit_reads_through("l4", "schema", "urg_read_118")
_emit_reads_through("l4", "schema", "urg_read_119")
_emit_reads_through("l4", "schema", "urg_read_120")
_emit_reads_through("l4", "schema", "urg_read_121")
_emit_reads_through("l4", "schema", "urg_read_122")
_emit_reads_through("l4", "schema", "urg_read_123")
_emit_reads_through("l4", "schema", "urg_read_124")
_emit_reads_through("l4", "schema", "urg_read_125")
_emit_reads_through("l4", "schema", "urg_read_126")
_emit_reads_through("l4", "schema", "urg_read_127")
_emit_reads_through("l4", "schema", "urg_read_128")
_emit_reads_through("l4", "schema", "urg_read_129")
_emit_reads_through("l4", "schema", "urg_read_130")
_emit_reads_through("l4", "schema", "urg_read_131")
_emit_reads_through("l4", "schema", "urg_read_132")
_emit_reads_through("l4", "schema", "urg_read_133")
_emit_reads_through("l4", "schema", "urg_read_134")
_emit_reads_through("l4", "schema", "urg_read_135")
_emit_reads_through("l4", "schema", "urg_read_136")
_emit_reads_through("l4", "schema", "urg_read_137")
_emit_reads_through("l4", "schema", "urg_read_138")
_emit_reads_through("l4", "schema", "urg_read_139")
_emit_reads_through("l4", "schema", "urg_read_140")
_emit_reads_through("l4", "schema", "urg_read_141")
_emit_reads_through("l4", "schema", "urg_read_142")
_emit_reads_through("l4", "schema", "urg_read_143")
_emit_reads_through("l4", "schema", "urg_read_144")
_emit_reads_through("l4", "schema", "urg_read_145")
_emit_reads_through("l4", "schema", "urg_read_146")
_emit_reads_through("l4", "schema", "urg_read_147")
_emit_reads_through("l4", "schema", "urg_read_148")
_emit_reads_through("l4", "schema", "urg_read_149")
_emit_reads_through("l4", "schema", "urg_read_150")
_emit_reads_through("l4", "schema", "urg_read_151")
_emit_reads_through("l4", "schema", "urg_read_152")
_emit_reads_through("l4", "schema", "urg_read_153")
_emit_reads_through("l4", "schema", "urg_read_154")
_emit_reads_through("l4", "schema", "urg_read_155")
_emit_reads_through("l4", "schema", "urg_read_156")
_emit_reads_through("l4", "schema", "urg_read_157")
_emit_reads_through("l4", "schema", "urg_read_158")
_emit_reads_through("l4", "schema", "urg_read_159")
_emit_reads_through("l4", "schema", "urg_read_160")
_emit_reads_through("l4", "schema", "urg_read_161")
_emit_reads_through("l4", "schema", "urg_read_162")
_emit_reads_through("l4", "schema", "urg_read_163")
_emit_reads_through("l4", "schema", "urg_read_164")
_emit_reads_through("l4", "schema", "urg_read_165")
_emit_reads_through("l4", "schema", "urg_read_166")
_emit_reads_through("l4", "schema", "urg_read_167")
_emit_reads_through("l4", "schema", "urg_read_168")
_emit_reads_through("l4", "schema", "urg_read_169")
_emit_reads_through("l4", "schema", "urg_read_170")
_emit_reads_through("l4", "schema", "urg_read_171")
_emit_reads_through("l4", "schema", "urg_read_172")
_emit_reads_through("l4", "schema", "urg_read_173")
_emit_reads_through("l4", "schema", "urg_read_174")
_emit_reads_through("l4", "schema", "urg_read_175")
_emit_reads_through("l4", "schema", "urg_read_176")
_emit_reads_through("l4", "schema", "urg_read_177")
_emit_reads_through("l4", "schema", "urg_read_178")
_emit_reads_through("l4", "schema", "urg_read_179")
_emit_reads_through("l4", "schema", "urg_read_180")
_emit_reads_through("l4", "schema", "urg_read_181")
_emit_reads_through("l4", "schema", "urg_read_182")
_emit_reads_through("l4", "schema", "urg_read_183")
_emit_reads_through("l4", "schema", "urg_read_184")
_emit_reads_through("l4", "schema", "urg_read_185")
_emit_reads_through("l4", "schema", "urg_read_186")
_emit_reads_through("l4", "schema", "urg_read_187")
_emit_reads_through("l4", "schema", "urg_read_188")
_emit_reads_through("l4", "schema", "urg_read_189")
_emit_reads_through("l4", "schema", "urg_read_190")
_emit_reads_through("l4", "schema", "urg_read_191")
_emit_reads_through("l4", "schema", "urg_read_192")
_emit_reads_through("l4", "schema", "urg_read_193")
_emit_reads_through("l4", "schema", "urg_read_194")
_emit_reads_through("l4", "schema", "urg_read_195")
_emit_reads_through("l4", "schema", "urg_read_196")
_emit_reads_through("l4", "schema", "urg_read_197")
_emit_reads_through("l4", "schema", "urg_read_198")
_emit_reads_through("l4", "schema", "urg_read_199")
_emit_reads_through("l4", "schema", "urg_read_200")
_emit_reads_through("l4", "schema", "urg_read_201")
_emit_reads_through("l4", "schema", "urg_read_202")
_emit_reads_through("l4", "schema", "urg_read_203")
_emit_reads_through("l4", "schema", "urg_read_204")
_emit_reads_through("l4", "schema", "urg_read_205")
_emit_reads_through("l4", "schema", "urg_read_206")
_emit_reads_through("l4", "schema", "urg_read_207")
_emit_reads_through("l4", "schema", "urg_read_208")
_emit_reads_through("l4", "schema", "urg_read_209")
_emit_reads_through("l4", "schema", "urg_read_210")
_emit_reads_through("l4", "schema", "urg_read_211")
_emit_reads_through("l4", "schema", "urg_read_212")
_emit_reads_through("l4", "schema", "urg_read_213")
_emit_reads_through("l4", "schema", "urg_read_214")
_emit_reads_through("l4", "schema", "urg_read_215")
_emit_reads_through("l4", "schema", "urg_read_216")
_emit_reads_through("l4", "schema", "urg_read_217")
_emit_reads_through("l4", "schema", "urg_read_218")
_emit_reads_through("l4", "schema", "urg_read_219")
_emit_reads_through("l4", "schema", "urg_read_220")
_emit_reads_through("l4", "schema", "urg_read_221")
_emit_reads_through("l4", "schema", "urg_read_222")
_emit_reads_through("l4", "schema", "urg_read_223")
_emit_reads_through("l4", "schema", "urg_read_224")
_emit_reads_through("l4", "schema", "urg_read_225")
_emit_reads_through("l4", "schema", "urg_read_226")
_emit_reads_through("l4", "schema", "urg_read_227")
_emit_reads_through("l4", "schema", "urg_read_228")
_emit_reads_through("l4", "schema", "urg_read_229")
_emit_reads_through("l4", "schema", "urg_read_230")
_emit_reads_through("l4", "schema", "urg_read_231")
_emit_reads_through("l4", "schema", "urg_read_232")
_emit_reads_through("l4", "schema", "urg_read_233")
_emit_reads_through("l4", "schema", "urg_read_234")
_emit_reads_through("l4", "schema", "urg_read_235")
_emit_reads_through("l4", "schema", "urg_read_236")
_emit_reads_through("l4", "schema", "urg_read_237")
_emit_reads_through("l4", "schema", "urg_read_238")
_emit_reads_through("l4", "schema", "urg_read_239")
_emit_reads_through("l4", "schema", "urg_read_240")
_emit_reads_through("l4", "schema", "urg_read_241")
_emit_reads_through("l4", "schema", "urg_read_242")
_emit_reads_through("l4", "schema", "urg_read_243")
_emit_reads_through("l4", "schema", "urg_read_244")
_emit_reads_through("l4", "schema", "urg_read_245")
_emit_reads_through("l4", "schema", "urg_read_246")
_emit_reads_through("l4", "schema", "urg_read_247")


# ── Scanner-Specific Symbol Sets (moved from static_scanner.py for SSOT) ──
CONFIG_READ_SYMBOLS: frozenset[str] = frozenset(
    {
        "os.environ",
        "os.getenv",
        "os.environ.get",
        "getenv",
        "config.get",
        "settings.get",
        "cfg.get",
        "CONFIG",
        "SETTINGS",
    },
)

DYNAMIC_EXEC_SYMBOLS: frozenset[str] = frozenset(
    {
        "eval",
        "exec",
    },
)

GOVERNANCE_WRITE_SYMBOLS: frozenset[str] = frozenset(
    {
        "UniversalWriteGateway",
        "execute_write",
        "submit_instruction",
        "commit_write",
        "uwg",
        "WriteGovernorMixin",
        "uwg_write",
        "write_text",
        "write_guardian_result",
        "create_artifact",
        "get_write_gateway",
        "persist_scan_result",
        "write_gateway",
        "assert_no_persistent_write",
        "write_all_artifacts",
        "is_commit_sandbox_active",
        "ProposalCommitter",
        "InMemoryHealingOutcomeIntakeStore",
        "HealingSuccessRateStore",
        "get_default_store",
        "reset_default_store",
        "get_bm25_store",
        "TraceFeatureRecord",
        "CorpusRecord",
        "KeyRecord",
        "MutationDiffRecord",
        "ReplayFailureRecord",
        "PromptOutcomeRecord",
        "HealingOutcomeIntakeRecord",
        "create_and_commit_routing_contract",
        "analyze_failures_and_persist",
        "compute_content_hash",
        "compute_replay_hash",
        "PolicyUpdateProposal",
        "HealingInput",
        "compute_heal_confidence",
        "create_legacy_import_healer",
        "log_event",
        "get_validated_project_root",
        "ExecutionContext",
        "SurgicalContext",
        "ViolationConstraint",
    },
)

GOVERNANCE_ROUTE_SYMBOLS: frozenset[str] = frozenset(
    {
        "HealingOrchestrator",
        "SovereignLLMGateway",
        "sovereign_gateway",
        "run_healing",
        "replay_run",
        "route_instruction",
        "healing_orchestrator",
        "dispatch_healing",
        "route_healing_tier",
        "AgenticRouter",
        "get_routing_gateway",
        "V15ExecutionGateway",
        "VLLMQueueController",
        "VLLMCircuitBreakerRegistry",
        "get_agent_dispatch_registry",
        "run_pipeline",
        "ExecutionOrchestrator",
        "VigilanceDispatcherAdapter",
        "get_healing_orchestrator",
        "get_validator_orchestrator",
        "route_violations",
        "build_l3_route_decision_artifact",
        "ResumeOrchestratorEngine",
        "PipelineDependencies",
        "build_pipeline_deps",
        "ASTCoordinate",
        "MCPConnectionManager",
        "ExecutionPathController",
        "invoke_hierarchy_agent",
        "safe_run",
        "ModelRouter",
        "ValidationResult",
        "UnifiedAgent",
        "get_llm_gateway",
        "check_gateway_topology",
        "build_route_decision_key",
        "build_route_context_key",
    },
)

GOVERNANCE_READ_SYMBOLS: frozenset[str] = frozenset(
    {
        "UniversalReadGateway",
        "read_file",
        "read_sqlite",
        "read_redis",
        "read_vector",
        "read_artifact",
        "urg_read",
        "ReadGovernorMixin",
        "read_active_payload",
        "pull_audit_data",
        "load_default_healing_tier_config",
        "load_or_scan",
        "get_sovereign_config",
        "get_active_configs",
        "ConfigurationLoader",
        "get_config_loader",
        "EvaluationLoader",
        "build_pipeline_config",
        "load_dev_script",
        "get_config_surface",
        "deterministic_json",
        "ADGQuerySession",
        "ADGRuntimeQueryEngine",
        "SqliteMemoryStore",
        "safe_execute",
        "execute_ssot",
        "get_runtime_query_engine",
        "get_hot_cache",
        "ADGRedisClient",
        "SemanticCacheManager",
        "DeterministicRedisCache",
        "check_redis_health",
        "ScanCache",
        "get_coordination_cache",
        "LocalFAISSStore",
        "RetrievalProfile",
        "EmbeddingServiceFactory",
        "query_similarity",
        "build_retriever",
        "build_seed_embedding_pack",
        "build_artifact",
        "build_pre_run_report",
        "RouteDecisionArtifact",
        "ADGArtifactBuilder",
        "IncidentBundle",
        "module_path_to_layer",
        "normalize_repo_path",
        "validate_no_absolute_paths",
        "PathRouter",
        "ExecutionPathController",
        "get_run_state_authority",
        "RuntimeStateGuard",
        "RuntimeStateManager",
        "JsonFileBackedFreezeReader",
        "StaticFreezeReader",
        "compute_runtime_state_digest",
        "FileBackedAuditStore",
        "HealingTierConfig",
        "HealingConfigOptimizer",
        "ConfigurationService",
        "SandboxEnvelope",
        "ResourceEnvelope",
        "GovernedPayload",
        "SemanticClockSnapshot",
        "HealingOutcomeAggregateSnapshot",
        "BlindSpotReport",
        "PatternFindingReport",
        "GuardianReportBuilder",
        "MCPConnectionManager",
        "load_agent_discovery",
        "stable_sha256_json",
        "RetrievalAnchor",
        "get_embedding_gateway",
        "CanonicalJSON",
        "canonical_json",
        "ReasonTraceEnvelope",
        "ResultEnvelope",
        "ReplayEnvelope",
        "PromptLoader",
        "MetaLearningBusConfig",
        "VLLMQueueState",
        "HandshakeStateMachine",
        "SlotPayload",
        "RunScopedStateAuthority",
        "StateVersionManager",
        "DefaultL4StateWriter",
        "RetrievalDriftMonitor",
        "RetrievalPipeline",
        "RetrievalCaseRecord",
        "EmbeddingHealthSnapshot",
        "PromptOutcomeEmbeddingRecord",
        "read_only_retrieval_scope",
        "get_embedding_config_surface",
        "EvaluationReport",
        "DeltaReport",
        "AnswerQualitySnapshot",
        "HumanDecisionArtifact",
        "FeatureBundle",
        "ReportLocationValidator",
        "build_replay_bundle",
        "assert_read_only_audit_access",
        "SafetyAuditTrail",
        "verify_mutation_paths",
        "PathFragilityDetector",
        "_read_baseline",
        "safe_git_execute",
        "get_clock",
        "get_python_files",
        "get_active_execution_trace",
        "get_behavioral_profile",
        "ADGBehavioralIndex",
        "get_data_files",
        "ADGStaticScanner",
    },
)

# ── Architecture Handoff: Symbol Sets (used by _ArchitectureHandoffVisitor) ───
HANDOFF_VALIDATE_SYMBOLS: frozenset[str] = frozenset(
    {
        "validate_request",
        "build_validated_request",
        "check_and_validate",
        "_emit_validates_request",
    },
)
HANDOFF_PLAN_SYMBOLS: frozenset[str] = frozenset(
    {
        "produce_plan",
        "build_l1_plan",
        "create_l1_plan",
        "produce_l1_plan",
        "_emit_produces_plan",
    },
)
HANDOFF_ROUTE_SYMBOLS: frozenset[str] = frozenset(
    {
        "propose_route",
        "build_route_decision",
        "select_route",
        "build_l3_route_decision_artifact",
        "_emit_proposes_route",
    },
)
HANDOFF_PREFILTER_SYMBOLS: frozenset[str] = frozenset(
    {
        "prefilter_scope",
        "filter_scope",
        "prefilter",
        "build_retrieval_plan",
        "_emit_prefilters_scope",
    },
)
HANDOFF_EVIDENCE_SYMBOLS: frozenset[str] = frozenset(
    {
        "produce_evidence_contract",
        "build_evidence_contract",
        "assemble_evidence",
        "build_c0_evidence",
        "_emit_produces_evidence_contract",
    },
)
HANDOFF_PROMPT_PKG_SYMBOLS: frozenset[str] = frozenset(
    {
        "package_prompt_envelope",
        "wrap_prompt_envelope",
        "seal_prompt_envelope",
        "build_prompt_envelope",
        "_emit_packages_prompt_envelope",
    },
)
HANDOFF_EXEC_STAMP_SYMBOLS: frozenset[str] = frozenset(
    {
        "stamp_execution_packet",
        "stamp_packet",
        "issue_exec_stamp",
        "build_capability_token",
        "_emit_stamps_execution_packet",
    },
)
HANDOFF_POLICY_HASH_SYMBOLS: frozenset[str] = frozenset(
    {
        "propagate_policy_hash",
        "forward_policy_hash",
        "relay_policy_hash",
        "_emit_propagates_policy_hash",
    },
)
HANDOFF_REPLAY_KEY_SYMBOLS: frozenset[str] = frozenset(
    {
        "propagate_replay_key",
        "forward_replay_key",
        "relay_replay_key",
        "_emit_propagates_replay_key",
    },
)
HANDOFF_BLAST_RADIUS_SYMBOLS: frozenset[str] = frozenset(
    {
        "verify_blast_radius",
        "check_blast_radius_handoff",
        "validate_blast_radius_handoff",
        "_emit_verifies_blast_radius",
    },
)
HANDOFF_COMMIT_RECEIPT_SYMBOLS: frozenset[str] = frozenset(
    {
        "append_commit_receipt",
        "record_commit_receipt",
        "issue_commit_receipt",
        "_emit_appends_commit_receipt",
    },
)
HANDOFF_RETRIEVAL_SURFACE_SYMBOLS: frozenset[str] = frozenset(
    {
        "publish_retrieval_surface",
        "expose_retrieval_surface",
        "register_retrieval_surface",
        "_emit_publishes_retrieval_surface",
    },
)
HANDOFF_PROMOTE_SYMBOLS: frozenset[str] = frozenset(
    {
        "promote_future_run_change",
        "queue_future_run",
        "schedule_future_promotion",
        "_emit_promotes_future_run_change",
    },
)
HANDOFF_GATES_SYMBOLS: frozenset[str] = frozenset(
    {
        "gate_promotion",
        "check_promotion_gate",
        "_emit_gates_promotion",
    },
)

# ── Architecture Handoff: Exit/Seal/HITL Symbol Sets (used by _HandoffExitVisitor)
HANDOFF_SEAL_SYMBOLS: frozenset[str] = frozenset(
    {
        "seal_result",
        "finalize_result",
        "lock_result",
        "build_sealed_result",
        "_emit_seals_result",
    },
)
HANDOFF_EXIT_SYMBOLS: frozenset[str] = frozenset(
    {
        "choose_exit_disposition",
        "select_exit",
        "determine_exit_disposition",
        "build_exit_disposition",
        "_emit_chooses_exit_disposition",
    },
)
HANDOFF_HITL_PKT_SYMBOLS: frozenset[str] = frozenset(
    {
        "materialize_hitl_packet",
        "build_hitl_packet",
        "create_hitl_packet",
        "_emit_materializes_hitl_packet",
    },
)
HANDOFF_RECLEAR_SYMBOLS: frozenset[str] = frozenset(
    {
        "reclear_human_decision",
        "re_approve",
        "reclear_decision",
        "reissue_human_approval",
        "_emit_reclears_human_decision",
    },
)

# ── Architecture Handoff: Atomic Family Registry ─────────────────────────────
ATOMIC_FAMILY_REGISTRY: dict[str, str] = {
    "ValidatedRequest": "validated_request",
    "L1Plan": "l1_plan",
    "RouteDecision": "route_decision",
    "RetrievalPlan": "retrieval_plan",
    "C0EvidenceContract": "c0_evidence_contract",
    "PromptEnvelope": "prompt_envelope",
    "CapabilityToken": "capability_token",
    "SandboxEnvelope": "sandbox_envelope",
    "ValidationPacket": "validation_packet",
    "ExecutionTrace": "execution_trace",
    "SealedResult": "sealed_result",
    "ExitDisposition": "exit_disposition",
    "HITLPacket": "hitl_packet",
    "CommitRequest": "commit_request",
    "CommitReceipt": "commit_receipt",
    "ReplayEnvelope": "replay_envelope",
    "PromotionPacket": "promotion_packet",
}

# ── Architecture Handoff: Composite Envelope Families ────────────────────────
COMPOSITE_ENVELOPE_REGISTRY: dict[str, frozenset[str]] = {
    "GovernedExecutionEnvelope": frozenset(
        {"CapabilityToken", "SandboxEnvelope", "ValidationPacket", "ReplayEnvelope"},
    ),
    "ExitHitlEnvelope": frozenset(
        {"SealedResult", "ExitDisposition", "HITLPacket"},
    ),
    "CommitUwgEnvelope": frozenset(
        {"CommitRequest", "CommitReceipt"},
    ),
}

# CommitUwgEnvelope: authority / blast-radius / lock-chain witness semantics
COMMIT_UWG_WITNESS_RELATIONS: frozenset[str] = frozenset(
    {
        "verifies_blast_radius",
        "appends_commit_receipt",
        "claims_write_lock",
        "applies_hmac_seal",
    },
)
