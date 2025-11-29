import json
import os

# ============================================================
# CONFIG
# ============================================================

TARGET_KEY_COUNT = 5000  # Ultra-aggressive spec: 5,000 keys

OUTPUT_PATH = (
    r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM "
    r"Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\scripts\windsurf_validation_keys.json"
)

# ============================================================
# CANONICAL DIRECTORY SCHEMA (ROOT → DEPTH 3 STRICT)
# Any directory not present in this schema is implicitly forbidden.
# ============================================================

ROOT_SCHEMA = {
    "agentic_core": {
        "l1_planning": {
            "planners": {},
            "schemas": {},
            "utils": {},
        },
        "l2_execution": {
            "executors": {},
            "schemas": {},
            "utils": {},
        },
        "l3_orchestration": {
            "engines": {},
            "framework": {},
            "utils": {},
        },
        "l4_memory": {
            "providers": {},
            "temporal": {},
            "mappings": {},
        },
        "l5_safety": {
            "filters": {},
            "policies": {},
            "validators": {},
        },
    },
    "apps": {
        "resume_engine": {
            "l1": {},
            "l2": {},
            "l3": {},
            "l4": {},
            "l5": {},
        },
        "outreach_engine": {
            "l1": {},
            "l2": {},
            "l3": {},
            "l4": {},
            "l5": {},
        },
    },
    "tests": {
        "l1": {
            "unit": {},
            "integration": {},
        },
        "l2": {
            "unit": {},
            "integration": {},
        },
        "l3": {
            "orchestration": {},
        },
        "l4": {
            "memory": {},
        },
        "l5": {
            "safety": {},
        },
        "e2e": {},
        "integration": {},
        "regression": {},
        "fixtures": {},
        "data": {},
    },
    "schemas": {},
    "runtime": {},
    "observability": {},
    "prompt_governance": {},
    "data": {},
    "docs": {},
    ".github": {
        "workflows": {},
    },
}

# ============================================================
# CANONICAL TEST FILES (STRICT)
# ============================================================

CANONICAL_TEST_FILES = {
    "tests/l1/unit": [
        "test_strategy_planner.py",
        "test_message_planner.py",
        "test_research_planner.py",
        "test_refinement_planner.py",
        "test_safety_planner.py",
    ],
    "tests/l1/integration": [
        "test_l1_planning_integration.py",
    ],
    "tests/l2/unit": [
        "test_company_research_executor.py",
        "test_contact_research_executor.py",
        "test_message_generation_executor.py",
    ],
    "tests/l2/integration": [
        "test_l2_execution_integration.py",
    ],
    "tests/l3/orchestration": [
        "test_resume_engine_dag.py",
        "test_outreach_engine_dag.py",
        "test_self_correction_loops.py",
    ],
    "tests/l4/memory": [
        "test_temporal_memory.py",
        "test_provider_registry.py",
        "test_memory_mappings.py",
    ],
    "tests/l5/safety": [
        "test_policy_engine.py",
        "test_filters.py",
        "test_validators.py",
        "test_prompt_injection_protection.py",
    ],
    "tests/e2e": [
        "test_e2e_resume_flow.py",
        "test_e2e_outreach_flow.py",
    ],
    "tests/integration": [
        "test_cross_layer_purity.py",
        "test_rag_pipeline_integration.py",
        "test_kg_pipeline_integration.py",
    ],
    "tests/regression": [
        "test_regression_resume_outputs.py",
        "test_regression_outreach_outputs.py",
        "test_regression_temporal_memory.py",
    ],
}

# ============================================================
# CANONICAL MODULE / TOOL LISTS
# ============================================================

L1_PLANNERS = [
    "strategy_planner",
    "message_planner",
    "research_planner",
    "refinement_planner",
    "safety_planner",
]

L2_EXECUTORS = [
    "company_research_executor",
    "contact_research_executor",
    "message_generation_executor",
]

L3_ENGINES = [
    "resume_engine_dag",
    "outreach_engine_dag",
]

SCHEMA_FILES = [
    "agentic_core/l1_planning/schemas/strategy_schema.json",
    "agentic_core/l1_planning/schemas/message_schema.json",
    "agentic_core/l2_execution/schemas/execution_schema.json",
    "agentic_core/l3_orchestration/schemas/dag_schema.json",
]

PROMPT_FILES = [
    "prompt_governance/prompt_system_v10_10.txt",
]

MCP_TOOLS = [
    "rag_retriever",
    "kg_resolver",
    "temporal_memory_inspector",
]

TEMPORAL_MEMORY_MODULE = "agentic_core/l4_memory/temporal"
SAFETY_POLICY_MODULE = "agentic_core/l5_safety/policies/policy_engine.py"

GOLDEN_DATASETS = [
    "data/golden/rag_queries.jsonl",
    "data/golden/kg_queries.jsonl",
    "data/golden/safety_queries.jsonl",
]

CI_WORKFLOW_DIR = ".github/workflows"

# DAG invariants (abstract specs)
DAG_SPECS = {
    "resume_engine_dag": {"node_count": 12},
    "outreach_engine_dag": {"node_count": 10},
}

# Zero-tolerance policy parameters
MAX_DEPTH = 9
FORBIDDEN_TEST_EXTENSIONS = [
    ".ipynb",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".log",
    ".tmp",
    ".bak",
]
FORBIDDEN_FILENAME_SUBSTRINGS = [
    "old",
    "backup",
    "copy",
    "tmp",
    "draft",
]

ALLOWED_HIDDEN_DIRS = [".github"]
ALLOWED_HIDDEN_FILES = [".gitignore"]

MAX_FILENAME_LENGTH = 80

# ============================================================
# HELPERS
# ============================================================

def collect_dir_paths(schema, prefix=""):
    paths = []
    for name, sub in schema.items():
        current = f"{prefix}/{name}" if prefix else name
        paths.append(current)
        if isinstance(sub, dict) and sub:
            paths.extend(collect_dir_paths(sub, current))
    return paths

# ============================================================
# KEY GENERATORS
# ============================================================

def gen_fs_structure_keys(dir_paths):
    keys = []
    for path in dir_paths:
        keys.append(f"fs.structure.presence.dir::{path}")
        keys.append(f"fs.structure.absence.unexpected_child_in::{path}")
    return keys


def gen_fs_filecount_keys():
    keys = []
    for dir_path, files in CANONICAL_TEST_FILES.items():
        count = len(files)
        keys.append(f"fs.structure.exact_filecount::{dir_path}::{count}")
    keys.append("fs.structure.exact_filecount::agentic_core/l1_planning/planners::5")
    keys.append("fs.structure.exact_filecount::agentic_core/l2_execution/executors::3")
    keys.append("fs.structure.exact_filecount::agentic_core/l3_orchestration/engines::2")
    return keys


def gen_fs_children_allowlist_keys():
    keys = []

    def traverse(schema, prefix=""):
        for name, sub in schema.items():
            current = f"{prefix}/{name}" if prefix else name
            children = list(sub.keys()) if isinstance(sub, dict) else []
            children_str = ",".join(sorted(children))
            keys.append(f"fs.structure.exact_children::{current}::[{children_str}]")
            if isinstance(sub, dict) and sub:
                traverse(sub, current)

    traverse(ROOT_SCHEMA)
    return keys


def gen_fs_depth_and_hidden_policy_keys():
    keys = []
    keys.append(f"fs.depth.max_depth::{MAX_DEPTH}")
    keys.append("fs.depth.zero_tolerance_for_excess::true")

    for d in ALLOWED_HIDDEN_DIRS:
        keys.append(f"fs.hidden.allowed_dir::{d}")
    for f in ALLOWED_HIDDEN_FILES:
        keys.append(f"fs.hidden.allowed_file::{f}")
    keys.append("fs.hidden.zero_tolerance_for_others::true")

    keys.append(f"fs.filename.max_length::{MAX_FILENAME_LENGTH}")
    for bad in FORBIDDEN_FILENAME_SUBSTRINGS:
        keys.append(f"fs.filename.forbidden_substring::{bad}")

    for ext in FORBIDDEN_TEST_EXTENSIONS:
        keys.append(f"fs.tests.forbidden_extension::{ext}")

    keys.append("fs.zero_tolerance.empty_directories::true")
    keys.append("fs.zero_tolerance.case_collisions::true")
    return keys


def gen_tests_presence_absence_keys():
    keys = []
    for dir_path, files in CANONICAL_TEST_FILES.items():
        keys.append(f"tests.presence.dir::{dir_path}")
        keys.append(f"tests.absence.unexpected_file_in::{dir_path}")
        for fname in files:
            full = f"{dir_path}/{fname}"
            keys.append(f"tests.presence.file::{full}")
            keys.append(f"tests.naming.must_start_with_test::{full}")
            keys.append(f"tests.naming.snake_case_required::{full}")
    return keys


def gen_tests_coverage_keys():
    keys = []
    for planner in L1_PLANNERS:
        keys.append(f"coverage.l1.planning.has_unit_test::{planner}")
        keys.append(f"coverage.l1.planning.has_integration_test::{planner}")
        keys.append(f"coverage.l1.planning.negative_cases_present::{planner}")
    for executor in L2_EXECUTORS:
        keys.append(f"coverage.l2.execution.has_unit_test::{executor}")
        keys.append(f"coverage.l2.execution.error_paths_tested::{executor}")
        keys.append(f"coverage.l2.execution.timeout_paths_tested::{executor}")
    for engine in L3_ENGINES:
        keys.append(f"coverage.l3.orchestration.dag_nodes_tested::{engine}")
        keys.append(f"coverage.l3.orchestration.self_correction_tested::{engine}")
        keys.append(f"coverage.l3.orchestration.schema_enforced_in_tests::{engine}")
    keys.append("coverage.e2e.resume_flow_happy_path_tested::tests/e2e/test_e2e_resume_flow.py")
    keys.append("coverage.e2e.outreach_flow_happy_path_tested::tests/e2e/test_e2e_outreach_flow.py")
    keys.append("coverage.e2e.outreach_flow_failure_modes_tested::tests/e2e/test_e2e_outreach_flow.py")
    keys.append("coverage.regression.resume_outputs_hash_stable::tests/regression/test_regression_resume_outputs.py")
    keys.append("coverage.regression.outreach_outputs_hash_stable::tests/regression/test_regression_outreach_outputs.py")
    return keys


def gen_negative_test_keys():
    keys = []
    keys.append("tests.negative.l1.strategy_planner_invalid_input::tests/l1/unit/test_strategy_planner.py")
    keys.append("tests.negative.l2.executor_timeout_case::tests/l2/unit/test_company_research_executor.py")
    keys.append("tests.negative.l3.orchestration_cycle_detection::tests/l3/orchestration/test_resume_engine_dag.py")
    keys.append("tests.negative.l4.read_expired_state::tests/l4/memory/test_temporal_memory.py")
    keys.append("tests.negative.l5.policy_blocks_unsafe_output::tests/l5/safety/test_policy_engine.py")
    # extra edge-case negatives
    keys.append("tests.negative.rag.off_topic_results_detected::tests/integration/test_rag_pipeline_integration.py")
    keys.append("tests.negative.kg.invalid_relation_detected::tests/integration/test_kg_pipeline_integration.py")
    return keys


def gen_orphan_and_untested_policy_keys():
    keys = []
    keys.append("tests.policy.zero_orphan_tests_allowed::true")
    keys.append("tests.policy.zero_untested_known_modules_allowed::true")
    for mod in L1_PLANNERS + L2_EXECUTORS + L3_ENGINES:
        keys.append(f"tests.mapping.module_has_test_mapping::{mod}")
    return keys


def gen_layer_purity_keys():
    keys = []
    l1_rules = [
        "no_import_l2",
        "no_import_l3",
        "no_import_l4",
        "no_import_l5",
        "no_direct_tool_calls",
        "no_state_mutation",
        "no_inline_prompts",
        "planners_are_pure",
    ]
    for rule in l1_rules:
        keys.append(f"l1.planning.purity.{rule}::agentic_core/l1_planning")

    l2_rules = [
        "no_import_l3",
        "no_import_l4",
        "no_import_l5",
        "no_planning_logic",
        "no_inline_prompts",
        "tools_declare_timeouts",
        "tools_declare_failure_modes",
        "tools_have_circuit_breakers",
    ]
    for rule in l2_rules:
        keys.append(f"l2.execution.purity.{rule}::agentic_core/l2_execution")

    l3_rules = [
        "no_import_l4",
        "no_import_l5",
        "no_direct_tool_calls",
        "no_business_logic",
        "dag_nodes_have_input_schema",
        "dag_nodes_have_output_schema",
        "self_correction_deterministic",
    ]
    for rule in l3_rules:
        keys.append(f"l3.orchestration.purity.{rule}::agentic_core/l3_orchestration")

    l4_rules = [
        "no_import_l1",
        "no_import_l2",
        "no_import_l3",
        "no_inline_prompts",
        "apis_are_memory_only",
        "temporal_validity_fields_present",
    ]
    for rule in l4_rules:
        keys.append(f"l4.memory.purity.{rule}::agentic_core/l4_memory")

    l5_rules = [
        "no_import_l1",
        "no_import_l2",
        "no_import_l3",
        "no_import_l4",
        "no_business_logic",
        "no_inline_prompts",
        "filters_present",
        "policies_present",
        "validators_present",
    ]
    for rule in l5_rules:
        keys.append(f"l5.safety.purity.{rule}::agentic_core/l5_safety")

    return keys


def gen_schema_binding_keys():
    keys = []
    for schema_path in SCHEMA_FILES:
        base = schema_path.split("/")[-1].replace(".json", "")
        keys.append(f"schema.binding.has_unit_test::{schema_path}")
        keys.append(f"schema.binding.has_integration_test::{schema_path}")
        keys.append(f"schema.binding.has_regression_test::{schema_path}")
        keys.append(f"schema.hash.must_match_committed_value::{base}")
    return keys


def gen_runtime_binding_keys():
    keys = []
    for executor in L2_EXECUTORS:
        keys.append(f"coverage.runtime.observed_call.l2_executor::{executor}")
    for planner in L1_PLANNERS:
        keys.append(f"coverage.runtime.observed_call.l1_planner::{planner}")
    for engine in L3_ENGINES:
        keys.append(f"coverage.runtime.observed_call.l3_dag::{engine}")
    keys.append("coverage.runtime.observed_memory_call::temporal_store")
    return keys


def gen_dag_invariant_keys():
    keys = []
    for dag_name, spec in DAG_SPECS.items():
        keys.append(f"l3.dag.hash_matches_manifest::{dag_name}")
        keys.append(f"l3.dag.node_count::{dag_name}::{spec['node_count']}")
        keys.append(f"l3.dag.has_no_cycles::{dag_name}")
        keys.append(f"l3.dag.schema_round_trip_valid::{dag_name}")
    return keys


def gen_prompt_governance_keys():
    keys = []
    for p in PROMPT_FILES:
        keys.append(f"prompt.governance.exists::{p}")
        keys.append(f"prompt.governance.contains_injection.header::{p}")
        keys.append(f"prompt.governance.contains_injection.context::{p}")
        keys.append(f"prompt.governance.contains_injection.reasoning::{p}")
        keys.append(f"prompt.governance.contains_injection.safety::{p}")
    keys.append("prompt.governance.strict_version::v10_10")
    keys.append("prompt.governance.no_shadow_prompts_present::prompt_governance")
    keys.append("prompt.governance.zero_tolerance_for_rogue_prompts::true")
    return keys


def gen_mcp_contract_keys():
    keys = []
    for tool in MCP_TOOLS:
        keys.append(f"mcp.contract.required_fields_present::{tool}")
        keys.append(f"mcp.contract.output_schema_has_examples::{tool}")
        keys.append(f"mcp.contract.has_error_codes::{tool}")
        keys.append(f"mcp.contract.timeout_present::{tool}")
        keys.append(f"mcp.contract.retry_policy_present::{tool}")
        keys.append(f"mcp.contract.security_policies_present::{tool}")
        keys.append(f"mcp.contract.zero_tolerance_for_untyped_params::{tool}")
    return keys


def gen_temporal_memory_keys():
    keys = []
    keys.append(f"temporal.memory.event_requires_valid_at::{TEMPORAL_MEMORY_MODULE}")
    keys.append(f"temporal.memory.event_requires_invalid_at_or_none::{TEMPORAL_MEMORY_MODULE}")
    keys.append(f"temporal.memory.no_overlapping_intervals_for_same_entity::{TEMPORAL_MEMORY_MODULE}")
    keys.append(f"temporal.memory.survives_round_trip::{TEMPORAL_MEMORY_MODULE}")
    keys.append(f"temporal.memory.sort_order_correct::{TEMPORAL_MEMORY_MODULE}")
    keys.append(f"temporal.memory.zero_tolerance_for_time_travel_bugs::{TEMPORAL_MEMORY_MODULE}")
    return keys


def gen_safety_envelope_keys():
    keys = []
    keys.append(f"safety.policy_has_negative_cases::{SAFETY_POLICY_MODULE}")
    keys.append(f"safety.policy_has_positive_cases::{SAFETY_POLICY_MODULE}")
    keys.append("safety.policy_has_shadow_prompts_blocked::agentic_core/l5_safety")
    keys.append("safety.policy_has_input_normalization::agentic_core/l5_safety")
    keys.append("safety.policy_has_output_normalization::agentic_core/l5_safety")
    keys.append("safety.policy_has_no_rogue_regex::agentic_core/l5_safety")
    keys.append("safety.policy_has_no_custom_exceptions::agentic_core/l5_safety")
    keys.append("safety.zero_tolerance_for_blanket_allow_rules::agentic_core/l5_safety")
    return keys


def gen_rag_kg_runtime_security_keys():
    keys = []

    rag_rules = [
        "hybrid_retriever_configured",
        "dense_and_sparse_retrievers_valid",
        "rrf_reranker_deterministic",
        "golden_queries_present",
        "golden_queries_pass",
        "source_attribution_required",
        "retrieval_latency_within_bounds",
    ]
    for rule in rag_rules:
        keys.append(f"rag.pipeline.{rule}::agentic_core/l2_execution")

    kg_rules = [
        "graph_schema_valid",
        "nodes_have_ids",
        "edges_have_types",
        "temporal_annotations_valid",
        "lookup_latency_within_bounds",
    ]
    for rule in kg_rules:
        keys.append(f"kg.pipeline.{rule}::agentic_core/l4_memory")

    runtime_rules = [
        "startup_checks_pass",
        "shutdown_checks_pass",
        "health_checks_defined",
        "state_manager_ready",
        "tool_registry_ready",
        "mcp_registry_ready",
        "prompt_registry_ready",
        "safety_engine_ready",
        "observability_ready",
        "performance_thresholds_met",
    ]
    for rule in runtime_rules:
        keys.append(f"runtime.health.{rule}::runtime")

    security_rules = [
        "input_validation_present",
        "output_validation_present",
        "tool_parameter_validation_present",
        "no_prompt_injection_allowed",
        "no_code_execution_allowed",
        "no_filesystem_access_outside_sandbox",
        "no_network_access_outside_mcp",
        "user_roles_validated",
        "context_constrained",
        "sandbox_enforced",
    ]
    for rule in security_rules:
        keys.append(f"security.enforcement.{rule}::agentic_core/l5_safety")

    keys.append("security.zero_tolerance_for_direct_secrets_in_repo::true")
    keys.append("security.zero_tolerance_for_unknown_env_vars::true")

    return keys


def gen_observability_keys():
    keys = []
    obs_rules = [
        "traces_cover_all_tool_calls",
        "traces_cover_all_memory_writes",
        "traces_cover_all_policy_decisions",
        "logs_capture_state_transitions",
        "metrics_capture_latency",
        "metrics_capture_cost",
        "metrics_capture_error_rates",
        "metrics_capture_retries",
    ]
    for rule in obs_rules:
        keys.append(f"observability.requirement.{rule}::observability")
    keys.append("observability.zero_tolerance_for_missing_traces::true")
    keys.append("observability.zero_tolerance_for_missing_metrics::true")
    keys.append("observability.zero_tolerance_for_missing_logs::true")
    return keys


def gen_ci_cd_keys():
    keys = []
    cicd_rules = [
        "tests_run_on_every_commit",
        "schema_regression_runs_on_every_commit",
        "prompt_regression_runs_on_every_commit",
        "safety_regression_runs_on_every_commit",
        "rag_regression_runs_on_every_commit",
        "kg_regression_runs_on_every_commit",
        "blocks_merge_on_failures",
        "blocks_merge_on_missing_tests",
        "blocks_merge_on_purity_violation",
        "enforces_linting",
        "enforces_mypy",
        "enforces_security_scan",
    ]
    for rule in cicd_rules:
        keys.append(f"ci_cd.pipeline.{rule}::{CI_WORKFLOW_DIR}")

    keys.append("ci_cd.mutation_test.must_be_enabled::tests")
    keys.append("ci_cd.mutation_test.score_above_threshold::0.85")
    keys.append("ci_cd.mutation_test.covers_all_layers::l1_l2_l3_l4_l5")
    keys.append("ci_cd.zero_tolerance_for_silent_failures::true")

    return keys


def gen_golden_dataset_keys():
    keys = []
    for path in GOLDEN_DATASETS:
        keys.append(f"golden.dataset.required::{path}")
        keys.append(f"golden.dataset.has_positive_cases::{path}")
        keys.append(f"golden.dataset.has_negative_cases::{path}")
        keys.append(f"golden.dataset.no_duplicates::{path}")
        keys.append(f"golden.dataset.schema_valid::{path}")
    keys.append("golden.dataset.total_minimum_cases::500")
    keys.append("golden.dataset.zero_tolerance_for_missing_golden_data::true")
    return keys


def gen_documentation_keys():
    keys = []
    docs_rules = [
        "readme_present",
        "api_docs_present",
        "prompt_docs_present",
        "safety_docs_present",
        "schema_docs_present",
        "observability_docs_present",
        "memory_docs_present",
        "agent_cards_present",
        "rag_docs_present",
        "kg_docs_present",
        "ci_cd_docs_present",
    ]
    for rule in docs_rules:
        keys.append(f"documentation.structure.{rule}::docs")
    keys.append("documentation.zero_tolerance_for_missing_readme::true")
    return keys


def gen_meta_keys(start_index, count):
    keys = []
    for i in range(start_index, start_index + count):
        keys.append(f"meta.validation_slot.{i:04d}::reserved")
    return keys

# ============================================================
# MAIN
# ============================================================

def main():
    keys = []

    # 1) Filesystem structure + zero-tolerance policies
    dir_paths = collect_dir_paths(ROOT_SCHEMA)
    keys.extend(gen_fs_structure_keys(dir_paths))
    keys.extend(gen_fs_filecount_keys())
    keys.extend(gen_fs_children_allowlist_keys())
    keys.extend(gen_fs_depth_and_hidden_policy_keys())

    # 2) Tests (presence, absence, naming, coverage, negative cases, orphan policy)
    keys.extend(gen_tests_presence_absence_keys())
    keys.extend(gen_tests_coverage_keys())
    keys.extend(gen_negative_test_keys())
    keys.extend(gen_orphan_and_untested_policy_keys())

    # 3) Layer purity
    keys.extend(gen_layer_purity_keys())

    # 4) Schema↔test↔hash + runtime bindings
    keys.extend(gen_schema_binding_keys())
    keys.extend(gen_runtime_binding_keys())

    # 5) DAG invariants
    keys.extend(gen_dag_invariant_keys())

    # 6) Prompt governance
    keys.extend(gen_prompt_governance_keys())

    # 7) MCP contracts
    keys.extend(gen_mcp_contract_keys())

    # 8) Temporal memory invariants
    keys.extend(gen_temporal_memory_keys())

    # 9) Safety envelope
    keys.extend(gen_safety_envelope_keys())

    # 10) RAG / KG / runtime / security
    keys.extend(gen_rag_kg_runtime_security_keys())

    # 11) Observability
    keys.extend(gen_observability_keys())

    # 12) CI/CD (incl. mutation testing)
    keys.extend(gen_ci_cd_keys())

    # 13) Golden datasets
    keys.extend(gen_golden_dataset_keys())

    # 14) Documentation
    keys.extend(gen_documentation_keys())

    # De-duplicate while preserving order
    seen = set()
    deduped = []
    for k in keys:
        if k not in seen:
            seen.add(k)
            deduped.append(k)
    keys = deduped

    # Fill or trim to exactly TARGET_KEY_COUNT
    if len(keys) < TARGET_KEY_COUNT:
        remaining = TARGET_KEY_COUNT - len(keys)
        keys.extend(gen_meta_keys(start_index=0, count=remaining))
    elif len(keys) > TARGET_KEY_COUNT:
        keys = keys[:TARGET_KEY_COUNT]

    output = {k: "" for k in keys}

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Generated {len(output)} keys → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
