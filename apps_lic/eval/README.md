# apps_lic eval harness (non-product)

These paths are **not** reachable from `python -m apps_lic` / `apps_lic.__main__`.

Product runtime is **only**:

`apps_lic.runtime.dispatch.canonical_dispatch.run_canonical_apps_lic_spine`

## Eval-only surfaces

- `tools/eval/retrieval_benchmark.py` — `run_lic_pilot_proof()` is retired (GovernedLicRun deleted)

## Removed (hard-delete)

- `GovernedLicRun` / `governed_lic_run.py`
- `spine_handoff.py` / `run_lic_via_spine`
- `integrated_r4_lic_pipeline_run` (agentic_core entrypoint)
- YAML L2 recipes (`lic_l2_recipe_registry`, static/managed DAG YAML)
- `--apps-e2e-live` symbolic cert branch
