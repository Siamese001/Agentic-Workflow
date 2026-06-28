# apps_rg runtime proof — runbook (canonical CLI only)

There is **no** `python -m apps_rg.runtime.*` product or section CLI. Runtime proof enters only through `apps_rg/__main__.py`.

| Goal | Command |
|------|---------|
| **Product / integrated spine proof** | `python -m apps_rg --target-company <co> --target-role <role> [--jd …] [--manual-brief …]` |
| **Single-lane dev proof** | `python -m apps_rg --section <lane> --target-company <co> --target-role <role> --jd … --manual-brief …` |
| **Read-only integrated product proof check** | `python -m apps_rg.runtime.integrated_product_proof_gate <run_dir> [--json]` |

Offline batch helpers (`run_orchestration`, rollup, assembly, package disposition) are **library-only** under `apps_rg.runtime.*` — not module CLIs.

Outputs from non-canonical historical runs must not be claimed as product, L7, or Fort Knox proof.

---

## Required services (live lanes)

| Dependency | Purpose |
|------------|---------|
| **external model PROVIDER_MODEL** | Section lanes with `external_model` (or contract stub in CI) |
| **X1D judge backends** | Per-lane judge configuration when not using test mocks |

Run from repository root.

---

## Product whole-run

```bash
python -m apps_rg \
  --target-company "Contoso Labs" \
  --target-role "Principal Engineer" \
  --jd artifacts/apps_rg/runtime_inputs/example_jd.txt \
  --manual-brief artifacts/apps_rg/runtime_inputs/example_briefing.txt
```

Dry-run (no lane runtime):

```bash
python -m apps_rg --section executive_summary --dry-run \
  --target-company "Contoso Labs" \
  --target-role "Principal Engineer" \
  --jd path/to/jd.txt \
  --manual-brief path/to/briefing.txt
```

---

## Single-lane dev

```bash
python -m apps_rg --section executive_summary \
  --target-company "Contoso Labs" \
  --target-role "Principal Engineer" \
  --jd artifacts/apps_rg/runtime_inputs/example_jd.txt \
  --manual-brief artifacts/apps_rg/runtime_inputs/example_briefing.txt \
  --provider external_model \
  --allow-non-allow-exit-zero
```

---

## JD + briefing validation (no generation)

```bash
python -m apps_rg.runtime.prepare_orchestrator_inputs \
  --job-description path/to/jd.txt \
  --briefing path/to/briefing.txt
```

Prints a suggested **canonical** `python -m apps_rg` command. Does not read or write base resume.

---

## CI lane-dev harness (retired direct script)

`ops_scripts/ci/prove_apps_rg_e2e_runtime.py` remains importable for unit tests only. Do not run it as a product proof entrypoint. Lane-dev proof uses `python -m apps_rg --section <lane>` per lane.

---

## Maintainer boundaries

Generated lane behavior, X1D/X2/X3, L6, DOCX internals, registry, and `agentic_core` are out of scope for this runbook. This document covers **how to invoke canonical entrypoints only**.
