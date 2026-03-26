prompt_governance/
│
├── engines/
│   ├── outreach_engine/
│   │   ├── archetype.yaml
│   │   ├── messaging.yaml
│   │   ├── personalization.yaml
│   │   └── reflective_checks.yaml
│   │
│   └── resume_engine/
│       ├── rewriting.yaml
│       ├── scoring.yaml
│       ├── summarization.yaml
│       └── system_prompts.yaml
│
├── evaluations/
│   ├── eval_sets.yaml
│   ├── regression_tests.yaml
│   ├── rubric.yaml
│   └── style_checks.yaml
│
├── governance/
│   ├── approval_workflow.yaml
│   ├── change_history.yaml
│   ├── guard_base.py
│   ├── ownership.yaml
│   ├── policy_base.py
│   ├── semantic_versioning.yaml
│   │
│   └── schemas/
│       └── prompt_schema.json
│
├── injections/
│   ├── constraints.yaml
│   ├── context_engineering.yaml
│   ├── framing.yaml
│   ├── output_governance.yaml
│   ├── reasoning.yaml
│   ├── safety.yaml
│   ├── tool_use.yaml
│   │
│   └── layering/
│       └── injection_templates.py
│
├── registry/
│   ├── prompt_index.yaml
│   ├── prompt_manifest.yaml
│   ├── rollback_policies.yaml
│   ├── version_map.yaml
│   │
│   ├── prompts/
│   │   ├── analysis_prompt.json
│   │   └── draft_executor.json
│   │
│   └── version_map/
│       └── draft_executor.json
│
└── templates/
    ├── base.py
    ├── __init__.py
    │
    ├── outreach/
    │   ├── cold_outreach_template.md
    │   ├── connection_request.md
    │   └── followup_template.md
    │
    └── resume/
        ├── experience_template.md
        ├── skills_template.md
        └── summary_template.md


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
