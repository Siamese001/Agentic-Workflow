# Unit Test Layout

This directory is split into canonical `agentic_core` layer suites, app suites, and a small set of wrapper or smoke roots.

Generated artifacts such as `__pycache__` and `.pytest_cache` are intentionally omitted from the tree below and should not be committed.

## Live Tree

```text
tests/unit/
├── agentic_core/
│   ├── L0_routing/
│   ├── L1_cognition/
│   ├── L2_execution/
│   ├── L3_orchestration/
│   ├── L4_state/
│   │   └── cache/
│   ├── L5_safety/
│   ├── L6_observability/
│   │   └── shadow_eval/
│   ├── L6_learning/
│   ├── L6_system_learning/
│   ├── adg/
│   ├── agents/
│   ├── base_agents/
│   ├── cache/
│   ├── config/
│   ├── core/
│   ├── embeddings/
│   ├── evaluation/
│   ├── governance/
│   ├── interfaces/
│   ├── knowledge/
│   ├── mixins/
│   ├── prompt_governance/
│   ├── runtime/
│   ├── runtime_gates/
│   ├── seams/
│   ├── tracing/
│   └── utils/
├── apps/
│   └── apps_lic/
├── apps_lic/
│   ├── config/
│   ├── engines/
│   ├── reasoning/
│   ├── runtime/
│   ├── sequences/
│   ├── signals/
│   ├── tools/
│   ├── types/
│   └── utils/
├── apps_rg/
│   ├── cache/
│   ├── claim_ledger/
│   ├── config/
│   ├── enforcement/
│   ├── engines/
│   ├── fact_inventory/
│   ├── integrations/
│   ├── l2_recipe/
│   ├── prompt_assembly/
│   ├── runtime/
│   ├── scripts/
│   ├── section_rigor/
│   ├── shared/
│   ├── types/
│   ├── utils/
│   └── validators/
├── apps_shared/
│   ├── adapters/
│   ├── cli/
│   ├── config/
│   ├── contracts/
│   ├── data/
│   ├── data_adapters/
│   ├── enforcement/
│   ├── integrations/
│   ├── mixins/
│   ├── prompts/
│   ├── proof/
│   ├── reasoning/
│   ├── scripts/
│   ├── services/
│   ├── spine/
│   ├── spine_emission/
│   ├── tests/
│   ├── types/
│   ├── utils/
│   └── validators/
├── apps_e2e/
├── apps_eval/
├── apps_exec/
├── apps_qna/
├── apps_research/
├── apps_rfp/
├── apps_underwriting_ai/
├── L0_routing/
├── L1_cognition/
├── L3_orchestration/
├── L4_state/
│   └── cache/
├── L6_observability/
│   └── shadow_eval/
├── adg/
├── calibration/
├── cost_telemetry/
├── docs/
│   └── wave_h/
├── embedders/
├── governance/
├── governance_hooks/
├── governance_scripts/
├── infrastructure/
├── ledgers/
├── ops_scripts/
├── prompt_assembly/
├── runtime/
├── runtime_contracts/
├── scripts/
├── system_learning/
├── tools/
├── tools_adg/
├── tools_analysis/
└── tools_notion/
```

The top-level `L2` and `L5` roots are intentionally absent. Their live suites live under `tests/unit/agentic_core/L2_execution` and `tests/unit/agentic_core/L5_safety`.

## Organization Notes

- `tests/unit/agentic_core` is the canonical home for layer tests.
- Top-level `tests/unit/L0_routing`, `tests/unit/L1_cognition`, `tests/unit/L3_orchestration`, `tests/unit/L4_state`, and `tests/unit/L6_observability` are small wrapper or smoke roots, not the main layer homes.
- `tests/unit/apps_lic` and `tests/unit/apps/apps_lic` are both kept for now because the repo has a legacy flat path and a current nested path.
- `tests/unit/apps` currently only wraps `apps_lic`. Keep it only while it continues to serve as a real umbrella or compatibility root.
- Legacy `tests/unit/author_gate*` and `tests/unit/windsurf*` roots were removed. Do not recreate them without a new SSOT decision.
- `__pycache__` and `.pytest_cache` are generated artifacts. They should be deleted locally and never committed.
- This README is a live layout guide, not an exhaustive inventory of every test file.

## Keep vs Delete

Keep:

- Canonical layer roots under `tests/unit/agentic_core`
- App suites under `tests/unit/apps_rg`, `tests/unit/apps_shared`, `tests/unit/apps_lic`, and `tests/unit/apps`
- Small wrapper or smoke roots only if they are intentionally used by CI or path-based collection

Delete:

- `__pycache__` directories under `tests/unit`
- `.pytest_cache` directories under `tests/unit`

## Useful Examples

```bash
python -m pytest tests/unit/agentic_core/L2_execution/enforcement/test_key_source.py -v
python -m pytest tests/unit/agentic_core/L5_safety/validators/test_global_mutation_validator.py -v
python -m pytest tests/unit/L6_observability/shadow_eval -v
```
