# Section quality benchmark (scaffold)

Offline evaluation harness for **generated** resume sections. **No scores are vendored in-repo.**

## Scope (initial)

Lanes with JSON schema stubs in this directory:

- `headline`
- `executive_summary`
- `competencies`
- `unify_bullets`
- `ibm_bullets`

Add `unify_narrative` / `ibm_narrative` when you extend the benchmark runner.

## Row model

Each evaluation row is **section-specific** (see `*.schema.json`). Common optional fields:

- `run_id`, `section_id`, `prompt_hash`, `section_contract_id`, `model_label`
- `human_notes` / `labeler_id` (empty in scaffold)
- **No** `overall_score` or judge outputs required for the scaffold

## Rules

- **X1D** outputs are **not** runtime release approvals.
- **Human labels** calibrate judges **offline** only.
- **L6** is future-run learning; **no current-run L6 mutation** in benchmark design.

See `docs/reports/apps_rg_prompt_authority/W14_quality_benchmark.md`.
