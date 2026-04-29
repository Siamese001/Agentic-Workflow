# `tests/e2e/` — End-to-End Runtime Proof SSOT

This directory is the **single source of truth** for the end-to-end runtime proof harness, validators, and acceptance test suites declared in `docs/reference/99_End_to_End_Runtime_Proof_and_Acceptance/`.

## Layout

```
tests/e2e/
├── __init__.py
├── conftest.py                 # shared fixtures
├── README.md                   # this file
├── scripts                     # legacy script entrypoint (file)
│
├── harnesses/                  # CLI runners that emit proof bundles
│   ├── run_agentic_runtime_proof.py
│   └── run_route_coverage_proof.py
│
├── validators/                 # per-axis bundle validators (consume bundles)
│   ├── _validate_common.py     # shared loader/parser
│   ├── validate_grounded_output.py
│   ├── validate_no_bypass.py
│   ├── validate_replay.py
│   └── validate_trace_tree.py
│
├── suites/                     # pytest test modules
│   ├── test_boundary_fault_matrix.py
│   ├── test_fixture_families.py
│   ├── test_requirements_traceability.py
│   └── test_runtime_proof_harness.py
│
├── proof/                      # core proof primitives (contracts, harness, runner, scenarios, validators, bundle)
├── agentic_core/               # agentic_core-specific E2E
├── retrieval_layers/           # retrieval-layer E2E
├── meta_learning_e2e/          # meta-learning E2E
└── data/                       # fixtures
```

## Acceptance Commands (per spec 99.8)

```bash
# Full E2E proof suite
python -m tests.e2e.harnesses.run_agentic_runtime_proof --scenario-set all \
    --emit-proof-bundle artifacts/e2e/latest

# Golden path only
python -m tests.e2e.harnesses.run_agentic_runtime_proof --scenario GP-001 \
    --emit-proof-bundle artifacts/e2e/gp_001

# Route coverage
python -m tests.e2e.harnesses.run_route_coverage_proof --all-routes \
    --emit-proof-bundle artifacts/e2e/routes

# Per-axis validators (consume an existing bundle)
python -m tests.e2e.validators.validate_trace_tree     --proof-bundle artifacts/e2e/latest --strict
python -m tests.e2e.validators.validate_replay         --proof-bundle artifacts/e2e/latest --strict
python -m tests.e2e.validators.validate_no_bypass      --proof-bundle artifacts/e2e/latest --strict
python -m tests.e2e.validators.validate_grounded_output --proof-bundle artifacts/e2e/latest --strict
```

## Pytest

```bash
python -m pytest tests/e2e/suites -v
```

## Reorganization Note (2026-04-28)

Files were grouped into `harnesses/`, `validators/`, and `suites/` subfolders to declare this directory as the canonical E2E SSOT. Prior flat layout module paths have been migrated:

| Old import path | New import path |
|---|---|
| `tests.e2e.run_agentic_runtime_proof` | `tests.e2e.harnesses.run_agentic_runtime_proof` |
| `tests.e2e.run_route_coverage_proof` | `tests.e2e.harnesses.run_route_coverage_proof` |
| `tests.e2e._validate_common` | `tests.e2e.validators._validate_common` |
| `tests.e2e.validate_grounded_output` | `tests.e2e.validators.validate_grounded_output` |
| `tests.e2e.validate_no_bypass` | `tests.e2e.validators.validate_no_bypass` |
| `tests.e2e.validate_replay` | `tests.e2e.validators.validate_replay` |
| `tests.e2e.validate_trace_tree` | `tests.e2e.validators.validate_trace_tree` |
| `tests.e2e.test_boundary_fault_matrix` | `tests.e2e.suites.test_boundary_fault_matrix` |
| `tests.e2e.test_fixture_families` | `tests.e2e.suites.test_fixture_families` |
| `tests.e2e.test_requirements_traceability` | `tests.e2e.suites.test_requirements_traceability` |
| `tests.e2e.test_runtime_proof_harness` | `tests.e2e.suites.test_runtime_proof_harness` |

Files under `proof/`, `agentic_core/`, `retrieval_layers/`, `meta_learning_e2e/`, `data/` and `conftest.py` were not moved.
