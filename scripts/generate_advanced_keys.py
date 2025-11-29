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
MAX_DEPTH = 8
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
