# apps_rg R1B semantic-cache persistence — W7

**Wave:** W7 only  
**Grain:** `ROLE_TARGET_RUN`  
**Status:** PASS (file-backed persistence; UWG durable write BLOCKED)

## Summary

W7 implements apps_rg R1B semantic cache at **role-target run** grain:

- **HistoricalIntentRecord** — primary lookup anchor (normalized intent digest + pseudo intent vector under `vectors/`).
- **HistoricalOutputChunk** — child records only (`chunks/<parent_intent_record_id>/`); never indexed as independent R1B keys (`independent_cache_identity: false` on serialize).

Lookup (`lookup_r1b_role_target_run`, `check_r1b_for_apps_rg`) scans **intent record vectors first**, then runs compatibility on metadata + child chunks. Inadmissible or sub-threshold candidates fall through to normal generation (returns `None` / miss).

## Persistence layout (file-backed SSOT)

Root: `artifacts/apps_rg/r1b_semantic_cache/`

| Path | Content |
|------|---------|
| `intents/<record_id>.json` | HistoricalIntentRecord |
| `vectors/<record_id>.json` | Intent vector payload (`subsystem=apps_rg_r1b_semantic_cache`, `not_c0_fact_vectors=true`) |
| `chunks/<record_id>/<chunk_id>.json` | HistoricalOutputChunk children |
| `index/by_digest/<digest>.json` | Digest → record_id index |

**UWG durable write:** `DURABLE_WRITE_VIA_UWG = "BLOCKED"` in `apps_rg/cache/r1b_constants.py`. No L4/UWG commit path added; governed durable persistence remains a future decision.

## Modules

| File | Role |
|------|------|
| `apps_rg/cache/r1b_constants.py` | Grain, chunk types, X3 admissibility, C0 separation |
| `apps_rg/cache/r1b_models.py` | HistoricalIntentRecord, HistoricalOutputChunk |
| `apps_rg/cache/r1b_intent_vector.py` | Intent text, digest, pseudo-vector, cosine similarity |
| `apps_rg/cache/r1b_store.py` | File-backed store |
| `apps_rg/cache/r1b_compatibility.py` | Admissibility + profile/digest match |
| `apps_rg/cache/r1b_retrieval.py` | Intent-first lookup + compatibility report |
| `apps_rg/cache/r1b_ingest.py` | Build/finalize records from run artifacts |
| `apps_rg/cache/r1b_adapter.py` | `check_r1b_for_apps_rg`, `AppsRgR1BCacheAdapter` |
| `tools/apps_rg/emit_r1b_w7_fixtures.py` | Proof fixtures emitter |

Whole-run post-success store hook: `apps_rg/__main__.py` (`store_intent_and_output` when R1B enabled and `generated_resume.json` exists).

## Chunk types implemented

`final_resume`, `headline_output`, `executive_summary_output`, `competencies_output`, `unify_narrative_output`, `unify_bullets_output`, `ibm_narrative_output`, `ibm_bullets_output`, `aggregation_summary`, `claim_ledger_entry`, `section_proof_summary`.

## Admissibility rules

`cache_admissible` only when:

- X3 disposition in finish-allowed set (`X3_ALLOW`, `X3C`, `X3D`, `EXIT_OK`, `EXIT_PARTIAL`)
- `proof_eligible=true`
- Runtime status not in `OFFLINE_CONTRACT_STUB`, `MOCKED`, `MOCK_ONLY`, etc.
- Required digests and profile hashes present
- Required child chunks: `final_resume`, `section_proof_summary`, ≥1 section output type
- On reuse query: optional `prompt_profile_hash` / `gate_profile_hash` match

## R1B vs C0

- R1B: `apps_rg_r1b_semantic_cache` subsystem, HistoricalIntentRecord vectors.
- C0: Chroma collection `fact_vectors` only for dense grounding on miss — not stored as R1B chunks or intent keys.

## Proof fixtures

`artifacts/apps_rg/r1b_semantic_cache/w7_fixtures/`:

- `historical_intent_record_admissible.json`
- `historical_output_chunks_admissible.json`
- `historical_intent_record_rejected_offline_stub.json`
- `historical_intent_record_rejected_not_proof_eligible.json`
- `historical_intent_record_rejected_digest_mismatch.json`
- `compatibility_report_w7.json` (accepted + rejected rows)

## Tests

- Unit: `tests/unit/apps_rg/test_r1b_historical_intent_persistence.py` (7 passed)
- Contract: `tests/_apps_contract/test_apps_rg_r1b_semantic_cache_w7.py`
- Quarantine-era contract tests updated for W7 active adapter

## agentic_core

`git diff HEAD -- agentic_core` → **empty** (no core edits).

## Commands (2026-05-18)

```text
python -m compileall apps_rg -q  → exit 0
python tools/apps_rg/emit_r1b_w7_fixtures.py → exit 0
pytest tests/unit/apps_rg/test_r1b_historical_intent_persistence.py -q → 7 passed
pytest tests/_apps_contract/test_apps_rg_r1b_semantic_cache_w7.py tests/_apps_contract/test_w1_core_r1b_cache_wiring.py tests/_apps_contract/test_w5_apps_rg_r1b_rca_decision.py -q → passed
git diff HEAD -- agentic_core → empty
```

Broad filter `pytest tests/_apps_contract -k "apps_rg and (r1b|...)"` still collects unrelated failing boundary tests (exit harness, missing review modules, core import renames) — not W7 regressions.
