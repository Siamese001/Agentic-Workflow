# apps_rg R1B post-Exit ingestion eligibility — W8

**Wave:** W8 only  
**Builds on:** W7 `ROLE_TARGET_RUN` file-backed R1B storage  
**Status:** PASS

## Summary

W8 hardens R1B ingestion so **only post-Exit, proof-eligible, non-mock** role-target runs can produce `cache_admissible=true` records. Ingestion is blocked during L2 generation paths unless `post_exit_ingestion=True` and Exit artifacts are present.

## Ingestion eligibility rules (fail-closed)

| Check | Requirement |
|-------|-------------|
| `exit_metadata_present` | `x3_disposition.json` exists with `x3_code` |
| `x3_allows_finish` | X3 in finish-allowed set (`X3_ALLOW`, `X3C`, `X3D`, `EXIT_OK`, `EXIT_PARTIAL`) |
| `proof_eligible_explicit` | `proof_eligible` explicitly true in Exit/manifest (missing → reject) |
| `proof_eligible` | Record + Exit agree proof-eligible |
| `runtime_status_present` | `runtime_generation_status` non-empty |
| `not_mock_runtime` | Not `OFFLINE_CONTRACT_STUB`, `MOCKED`, `MOCK_ONLY`, etc. |
| `exit_proceed_to_runtime` | `proceed_to_runtime` not false when present |
| Digest / profile | `jd_digest`, `base_resume_digest`, prompt/gate hashes present |
| Output chunks | `final_resume`, `section_proof_summary`, ≥1 section output |
| Parent linkage | All chunks `parent_intent_record_id == record_id`, `independent_cache_identity: false` |
| C0 separation | No `fact_vectors` chunk types |

When any check fails: `cache_admissible=false` with decisive `non_admissible_reason` (or `missing_exit_x3_disposition` when Exit artifact absent).

## Modules

| File | Role |
|------|------|
| `apps_rg/cache/r1b_post_exit_eligibility.py` | Exit metadata load + `assess_post_exit_ingestion_eligibility` |
| `apps_rg/cache/r1b_post_exit_ingest.py` | `evaluate_post_exit_ingestion`, `ingest_post_exit_from_run_dir`, `ingest_post_exit_after_run` |
| `apps_rg/cache/r1b_adapter.py` | `store_intent_and_output` requires `post_exit_ingestion=True` |
| `apps_rg/cache/r1b_ingest.py` | `ingest_run_artifact_dir` delegates to post-Exit ingest |
| `apps_rg/__main__.py` | Post-pipeline hook calls `ingest_post_exit_after_run` (after Exit bundle exists) |

## Post-Exit proof

- `ingest_post_exit_from_run_dir` returns `None` immediately when `x3_disposition.json` is missing.
- CLI shim ingests only after `run_integrated_r4_deterministic_pipeline` completes and artifact dir contains Exit outputs.
- `AppsRgR1BCacheAdapter.store_intent_and_output` returns `None` without `post_exit_ingestion=True` (no L2-time writes).

## Fixtures

`artifacts/apps_rg/r1b_semantic_cache/w8_fixtures/`:

- `accepted_post_exit_ingestion.json`
- `rejected_mock_runtime_ingestion.json` → `not_mock_runtime`
- `rejected_missing_x3_ingestion.json` → `missing_exit_x3_disposition`
- `rejected_missing_proof_chunks_ingestion.json` → missing output/proof chunks
- `rejected_missing_required_digest_ingestion.json` → `jd_digest_present` / `base_resume_digest_present`

Regenerate: `python tools/apps_rg/emit_r1b_w8_fixtures.py`

## UWG / durable persistence

**Not solved.** `DURABLE_WRITE_VIA_UWG` remains `BLOCKED`; W8 only gates file-backed writes.

## Commands (2026-05-18)

```text
python -m compileall apps_rg -q  → exit 0
python tools/apps_rg/emit_r1b_w8_fixtures.py → exit 0
pytest tests/unit/apps_rg -k "r1b and (ingest or eligibility or admissible or post_exit)" -q → 9 passed
pytest tests/_apps_contract -k "apps_rg and r1b and (ingest or eligibility or admissible or post_exit)" -q → 10 passed
git diff HEAD -- agentic_core → empty
```

## agentic_core

No edits (`git diff HEAD -- agentic_core` empty).
