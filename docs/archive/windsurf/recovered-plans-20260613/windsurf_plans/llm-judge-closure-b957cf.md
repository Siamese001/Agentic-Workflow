# LLM-as-Judge Closure Plan — Last 30%

- **Plan slug**: `llm-judge-closure-b957cf`
- **Parent plan**: `@.windsurf/plans/llm-judge-hardening-b5e319.md` (code-complete)
- **Tier**: T2 (scoped — 3 phases, additive)
- **Status**: In progress
- **Created**: 2026-04-23

## Parent Plan Summary

The LLM-as-Judge hardening plan reached 100% **code closure** (14 phases
shipped on `origin/main`) but 3 phases remained scaffolded with no
operational teeth: LJH4.1 golden dataset only had 1 seed item, LJH4.3
CI gate was not wired into `run_contract_gates.py`, and LJH5.2
capability/regression suites had READMEs but no items or markers.
This plan closes those three gaps in three small waves.

## Wave Plan

| Wave | Phases | Focus | Est Tokens | Status |
|---|---|---|---:|---|
| **LJHC1** | LJHC1.1 | Seed golden dataset with synthetic bootstrap items (≥10 per rubric × 4 RAG rubrics) | 1,500 | Todo |
| **LJHC2** | LJHC2.1 | Wire `check_judge_calibration.py` into `run_contract_gates.py` | 800 | Todo |
| **LJHC3** | LJHC3.1 – LJHC3.2 | Register `eval_capability`/`eval_regression` pytest markers + 1 seed test per suite | 1,200 | Todo |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est Tokens | Status |
|---|---|---|---|---:|---|
| LJHC1.1 | Golden dataset bootstrap | `data/eval/golden/rag/{faithfulness,answer_relevancy,context_precision,groundedness}/*.json` — 10 synthetic items per rubric | Real labeling is out of scope for Cascade; synthetic items labeled `synthetic_seed` let the calibration machinery exercise end-to-end and fail loud when humans haven't supplied real items. | 1,500 | Todo |
| LJHC2.1 | CI gate wiring | `ops_scripts/ci/run_contract_gates.py` — add `check_judge_calibration.py` invocation; pre-commit hook registration | Gate exists but is invisible to CI; no enforcement path. | 800 | Todo |
| LJHC3.1 | Pytest markers | `pytest.ini` — register `eval_capability` and `eval_regression` markers | Marker registration required for pytest strict-markers mode (if enabled). | 400 | Todo |
| LJHC3.2 | Seed eval tests | `tests/eval/capability/test_seed_capability.py`, `tests/eval/regression/test_seed_regression.py` | Empty dirs would not be collected by pytest; need at least one test per suite. | 800 | Todo |

## Acceptance

1. `python ops_scripts/ci/check_judge_calibration.py` executed standalone **and** via `run_contract_gates.py`; both exit 0 on current state and fail on synthetic-corruption test.
2. `python -m pytest tests/eval/capability tests/eval/regression -v` collects ≥ 1 test per suite, all pass.
3. `python -m pytest tests/unit/agentic_core/evaluation/` still at 37/37 green — no regressions.
4. All changes committed + pushed to `origin/main`.
