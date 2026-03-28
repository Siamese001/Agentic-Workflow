runtime/
├── cache/
│   ├── __init__.py
│   ├── .cache/
│   │   └── .gitkeep
│   └── .mypy_cache/
│       └── 3.13/
│           └── <*.data.json / *.meta.json artifacts>
│
├── config/
│   ├── .keep
│   ├── agent_profile.py
│   ├── budget_profile.py
│   ├── config_profiles_v10_10.py
│   ├── context_profile.py
│   ├── lic_assembly.py
│   ├── lic_cta.py
│   ├── lic_routing.py
│   ├── lic_seniority.py
│   ├── lic_tone.py
│   ├── lic_validation.py
│   ├── llm_profile.py
│   ├── meta_profile.py
│   ├── retrieval_profile.py
│   ├── rg_config.py
│   ├── safety_profile.py
│   └── __init__.py
│
├── core/
│   ├── routing.py
│   ├── __init__.py
│   └── models/
│       ├── models.py
│       ├── __init__.py
│       └── __pycache__/
│
├── cost/
│   ├── cost_tracking.json
│   └── __init__.py
│
├── data/
│   └── .gitkeep
│
├── environment/
│   └── __init__.py
│
├── eval/
│   ├── __init__.py
│   ├── golden_state/
│   │   ├── datasets.py
│   │   ├── evaluator.py
│   │   ├── gating.py
│   │   ├── judge.py
│   │   ├── models.py
│   │   ├── runner.py
│   │   ├── scorer.py
│   │   └── __pycache__/
│   ├── simulation/
│   │   └── models.py
│   └── __pycache__/
│
├── inference/
│   ├── context_manager.py
│   ├── execution_budget_manager.py
│   ├── executor.py
│   ├── runtime_utils.py
│   ├── __init__.py
│   └── __pycache__/
│
├── infra/
│   ├── __init__.py
│   ├── model_routing/
│   │   ├── policies.py
│   │   ├── __init__.py
│   │   └── __pycache__/
│   └── sandbox/
│       ├── fs_template.py
│       ├── microvm.py
│       ├── models.py
│       ├── networking.py
│       ├── sandbox_errors.py
│       ├── vm_manager.py
│       ├── __init__.py
│       └── __pycache__/
│
├── logs/
│   └── __init__.py
│
├── meta/
│   ├── schema_validation.py
│   ├── __init__.py
│   ├── metacognition/
│   │   ├── evaluator.py
│   │   ├── hypothesis.py
│   │   ├── models.py
│   │   ├── refinement.py
│   │   ├── uncertainty.py
│   │   ├── __init__.py
│   │   └── __pycache__/
│   ├── ranking/
│   │   ├── scoring.py
│   │   ├── __init__.py
│   │   └── __pycache__/
│   └── retrieval/
│       ├── hybrid_ranker.py
│       ├── orchestrate.py
│       ├── __init__.py
│       └── __pycache__/
│
├── ops/
│   ├── cost_tracker.py
│   ├── golden_datasets.py
│   ├── llm_judge.py
│   ├── reliability_scorer.py
│   ├── rest_interface.py
│   ├── session_manager.py
│   └── __init__.py
│
├── orchestration/
│   ├── policy_engine.py
│   ├── tool_registry.py
│   ├── __init__.py
│   └── __pycache__/
│
├── router/
│   └── __init__.py
│
├── telemetry/
│   ├── metrics.json
│   ├── metrics.py
│   ├── telemetry.py
│   ├── __init__.py
│   └── __pycache__/
│
├── utils/
│   ├── observability.py
│   ├── __init__.py
│   └── __pycache__/
│
├── tmp/
│   └── .gitkeep
│
└── __pycache__/
    ├── execution_budget_manager.*.pyc
    ├── runtime_utils.*.pyc
    ├── telemetry.*.pyc
    └── __init__.*.pyc


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
