import os

# Root config folder
ROOT = "config"

# Full Level-4 → Level-5 structure
STRUCTURE = {
    "core": [
        "system_defaults.yaml",
        "environment.yaml",
        "secrets_template.yaml",
        "feature_flags.yaml",
        "logging.yaml"
    ],
    "agentic_layers": {
        "l1_planning": [
            "strategy_planning.yaml",
            "research_planning.yaml",
            "message_planning.yaml",
            "safety_planning.yaml"
        ],
        "l2_execution": [
            "tool_registry.yaml",
            "execution_limits.yaml",
            "action_costing.yaml",
            "retry_policies.yaml"
        ],
        "l3_orchestration": [
            "workflow_graph.yaml",
            "orchestration_rules.yaml",
            "cost_budget_policies.yaml",
            "fallback_policies.yaml"
        ],
        "l4_state": [
            "memory_store.yaml",
            "recency_policies.yaml",
            "vector_cache.yaml",
            "persistence_policies.yaml"
        ],
        "l5_safety": [
            "safety_policies.yaml",
            "pii_filters.yaml",
            "guardrails.yaml",
            "redline_rules.yaml"
        ]
    },
    "model_routing": [
        "routing_policies.yaml",
        "model_profiles.yaml",
        "budget_bands.yaml",
        "recursion_depth_rules.yaml",
        "fallback_routing.yaml",
        "evaluation_weights.yaml"
    ],
    "engines": {
        "resume_engine": [
            "scoring_weights.yaml",
            "skill_taxonomy.yaml",
            "resume_style_defaults.yaml",
            "ats_rules.yaml",
            "optimizer_params.yaml"
        ],
        "outreach_engine": [
            "archetype_weights.yaml",
            "message_style.yaml",
            "outreach_pipeline.yaml",
            "cadence_rules.yaml",
            "personalization_params.yaml"
        ]
    },
    "runtime": [
        "inference.yaml",
        "batch_limits.yaml",
        "timeout_policies.yaml",
        "telemetry_controls.yaml",
        "tracing_config.yaml",
        "concurrency_rules.yaml"
    ],
    "validation": [
        "schema_registry.yaml",
        "test_matrix.yaml",
        "flow_hashes.yaml",
        "golden_trace_map.yaml",
        "l5_validation_keys.json"
    ]
}

# Stub placeholder content for YAML + JSON
YAML_STUB = "# Placeholder configuration file\n"
JSON_STUB = "{\n  \"placeholder\": true\n}\n"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def write_stub_file(path):
    # Determine stub type
    if path.endswith(".json"):
        content = JSON_STUB
    else:
        content = YAML_STUB

    # Write only if file does not exist
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

def populate():
    print(f"Populating `{ROOT}` folder structure...")

    ensure_dir(ROOT)

    for top, entries in STRUCTURE.items():
        top_path = os.path.join(ROOT, top)
        ensure_dir(top_path)

        # Nested folder (dict) e.g. agentic_layers, engines
        if isinstance(entries, dict):
            for subfolder, files in entries.items():
                sub_path = os.path.join(top_path, subfolder)
                ensure_dir(sub_path)
                for file in files:
                    file_path = os.path.join(sub_path, file)
                    write_stub_file(file_path)

        # Flat list of files
        elif isinstance(entries, list):
            for file in entries:
                file_path = os.path.join(top_path, file)
                write_stub_file(file_path)

    print("All folders and stub files created successfully.")

if __name__ == "__main__":
    populate()
