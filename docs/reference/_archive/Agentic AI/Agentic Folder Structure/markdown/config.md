config/
│
├── services/                                # Service-level config boundaries
│   ├── resume_engine/
│   │   ├── routing/
│   │   │   ├── model_routing.yaml
│   │   │   ├── safety_routing.yaml
│   │   │   └── cost_routing.yaml
│   │   ├── prompts/
│   │   │   ├── system_prompts.yaml
│   │   │   ├── planner_prompts.yaml
│   │   │   └── generator_prompts.yaml
│   │   ├── policies/
│   │   │   ├── safety_policies.yaml
│   │   │   ├── pii_policies.yaml
│   │   │   └── output_policies.yaml
│   │   ├── defaults/
│   │   │   ├── inference_defaults.yaml
│   │   │   ├── embeddings_defaults.yaml
│   │   │   └── retry_defaults.yaml
│   │   └── schemas/
│   │       ├── resume_plan.schema.json
│   │       ├── resume_message.schema.json
│   │       └── resume_strategy.schema.json
│   │
│   ├── outreach_engine/
│   │   ├── routing/
│   │   │   ├── outreach_model_routing.yaml
│   │   │   └── personalization_routing.yaml
│   │   ├── prompts/
│   │   │   ├── outreach_planner.yaml
│   │   │   ├── outreach_writer.yaml
│   │   │   └── outreach_style.yaml
│   │   ├── policies/
│   │   │   ├── linkedin_policies.yaml
│   │   │   └── compliance.yaml
│   │   ├── defaults/
│   │   │   ├── cadence_defaults.yaml
│   │   │   └── template_defaults.yaml
│   │   └── schemas/
│   │       ├── outreach_plan.schema.json
│   │       ├── outreach_message.schema.json
│   │       └── outreach_strategy.schema.json
│   │
│   └── shared/
│       ├── llm/
│       │   ├── model_profiles.yaml
│       │   ├── cost_profiles.yaml
│       │   └── api_settings.yaml
│       ├── telemetry/
│       │   ├── event_schema.yaml
│       │   ├── metric_counters.yaml
│       │   └── cost_tracking.yaml
│       ├── memory/
│       │   ├── cache_settings.yaml
│       │   ├── redis_settings.yaml
│       │   └── knowledge_profiles.yaml
│       └── tools/
│           ├── search.yaml
│           ├── browser.yaml
│           └── codeexec.yaml
│
├── environments/                            # Environment overlays (L5 policy-compliant)
│   ├── dev/
│   │   ├── settings.yaml
│   │   ├── routing_overrides.yaml
│   │   └── telemetry_overrides.yaml
│   ├── staging/
│   │   ├── settings.yaml
│   │   ├── safety_overrides.yaml
│   │   └── llm_overrides.yaml
│   └── prod/
│       ├── settings.yaml
│       ├── safety_overrides.yaml
│       └── cost_overrides.yaml
│
├── governance/                              # Prompt + safety + ACL governance
│   ├── prompt_registry.yaml
│   ├── version_map.yaml
│   ├── rollout_policies.yaml
│   └── fallback_policies.yaml
│
├── policies/                                # System-wide L5 policies
│   ├── pii.yaml
│   ├── data_retention.yaml
│   ├── safety.yaml
│   ├── agent_boundary.yaml
│   └── llm_governance.yaml
│
└── loaders/                                 # Config loaders for runtime
    ├── schema_loader.py
    ├── yaml_loader.py
    ├── policy_loader.py
    └── registry_loader.py


### Directory Structure

```plaintext
├── agentic_core.md
├── apps.md
├── config.md
├── data.md
├── observability.md
├── prompt_governance.md
├── runtime.md
├── schemas.md
├── scripts.md
├── tests.md
└── update_markdown_trees.py
```
