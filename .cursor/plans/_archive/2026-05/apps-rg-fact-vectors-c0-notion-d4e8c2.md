# apps_rg fact_vectors C0 — wave plan + evidence receipts

**Slug:** `apps-rg-fact-vectors-c0-notion-d4e8c2`  
**Scope:** apps_rg C0 dense lane, Chroma `fact_vectors`, readiness gate, contract tests — **no** `agentic_core` edits.

**Follow-on (Phase 2, separate plan):** `.cursor/plans/apps-rg-c0-sparse-exact-phase2-d2f8a1.md` — sparse / exact / merge / metrics; **not** part of this plan’s acceptance.

---

## Open vs done (read this first)

| Bucket | Status | What it means |
|--------|--------|----------------|
| **W1–W5 (core + CI determinism)** | **DONE** | Fixture, section profile, ingest path, proof tooling, hermetic pytest, Notion row, and **automated seed** before CHECK-RG-FACT-VECTORS in `run_contract_gates`. |
| **Operator-only** | **N/A** | Re-run `prove_fact_vectors_c0_runtime.py` when you want refreshed JSON under `artifacts/` (often gitignored). |

**Bottom line:** All planned waves are **closed**. Optional operator steps remain for local proof artifacts only.

**Correct status (dense C0 only):**

```text
Dense fact_vectors C0 objective: DONE
W1–W4 core delivery: DONE
W5 CI / clone determinism: DONE
Notion closeout: DONE
Phase 2 BM25 / exact-match / sparse merge: NOT IN THIS PLAN — separate next plan
```

---

## Acceptance

**ACCEPTED:** `apps_rg` **dense** `fact_vectors` C0 readiness plan is **fully closed** for the original objective (ingest → persist → retrieve via `c0_retrieve_apps_rg` → FEC + readiness gate + CI seed path).

**Evidence (operator / CI):**

```text
ops_scripts/ci/seed_apps_rg_fact_vectors_chroma.py -> exit 0 (skip or ingest)
ops_scripts/ci/check_apps_rg_fact_vectors_readiness.py -> exit 0 (when deps + store OK)
targeted C0/chroma pytest -> 36 passed (representative slice)
tools/notion/patch_apps_rg_fact_vectors_c0_plan_w5_notion.py -> exit 0
agentic_core -> no modification in this plan’s scope
```

---

## Out of scope — Phase 2 (new plan only)

This plan **does not** claim Phase 2. Track under a **separate** Cursor plan, e.g. *apps_rg C0 sparse / exact retrieval hardening*, including any of:

- BM25 and/or exact-match lane(s)
- Dense + sparse merge policy
- Sparse refs in FEC / receipts
- Stronger ACL, freshness, contradiction, weak-refinement receipts
- Expanded retrieval metric proof

Do **not** fold the above into this plan’s PASS; it would blur a clean dense-lane closure.

---

## Objective

Prove end-to-end that `apps_rg` can ingest deterministic fact-vector documents into persisted Chroma and retrieve them through `c0_retrieve_apps_rg`, with FEC maps (`citation_map`, `source_lineage_map`, `freshness_receipts`) and aggregate `support_status` aligned to bounded section retrieval.

---

## Wave structure

| Wave | Goal | Primary exit criteria | Status |
|------|------|------------------------|--------|
| **W1** | Fixture + section profile | Smoke ingest file committed; five C0 lanes in `section_retrieval_profile.yaml` with `max_k` / queries | DONE |
| **W2** | Operator ingest + readiness | `chroma_ingest_pipeline` succeeds; `check_apps_rg_fact_vectors_readiness.py` all checks OK at default path | DONE |
| **W3** | Proof tooling + artifacts | `prove_fact_vectors_c0_runtime.py` writes `ingestion_proof.json` + `c0_runtime_proof.json` | DONE |
| **W4** | Hermetic contract proof | `test_c0_fact_vectors_chroma_runtime.py` passes; targeted C0/chroma tests pass | DONE |
| **W5** | CI / clone determinism | `run_contract_gates` runs `seed_apps_rg_fact_vectors_chroma.py` before CHECK-RG-FV; idempotent; `--gate CHECK-RG-FACT-VECTORS` runs seed prelude | DONE |

### Wave detail — W1 (DONE)

- [x] Commit-friendly ingest input: `tests/fixtures/apps_rg/fact_vectors_c0_smoke.chroma_input` (not `*.jsonl` — repo gitignore).
- [x] Six documents: `id`, `text`, `metadata` with `BAAI/bge-m3`, `embedding_dim: 1024`, `company`, `role`, readiness-required metadata keys.
- [x] `apps_rg/config/domain_contract/section_retrieval_profile.yaml`: lanes `headline`, `executive_summary`, `competencies`, `unify_bullets`, `unify_narrative` with `max_k`, `dense_top_k`, `query_fields`, JD fallbacks.

### Wave detail — W2 (DONE)

- [x] Ingest command (operator / local):

  ```bash
  python -m tools.ingestion.chroma_ingest_pipeline \
    --input tests/fixtures/apps_rg/fact_vectors_c0_smoke.chroma_input \
    --chromadb-path data/cache/chromadb \
    --collection fact_vectors \
    --execute
  ```

- [x] Readiness: `python ops_scripts/ci/check_apps_rg_fact_vectors_readiness.py` (advisory unless `APPS_RG_FACT_VECTORS_FAIL_CLOSED=1`).
- [x] Receipt: `artifacts/ci/apps_rg_fact_vectors_readiness_gate.json` (regenerate by re-running the gate).

### Wave detail — W3 (DONE)

- [x] `tools/apps_rg/prove_fact_vectors_c0_runtime.py` (repo root on `sys.path`; `--reset-collection`, `--skip-ingest`).
- [x] Artifacts: `artifacts/apps_rg/c0_embedding_gap/ingestion_proof.json`, `artifacts/apps_rg/c0_embedding_gap/c0_runtime_proof.json`.

### Wave detail — W4 (DONE)

- [x] `tests/_apps_contract/test_c0_fact_vectors_chroma_runtime.py` — `tmp_path` Chroma, real `run_ingestion` + query path, `c0_retrieve_apps_rg`, FEC + five lane anchors + `SUPPORT_STATUS_PASS` when both source classes hit.
- [x] **Pytest:** do not pass `-p pytest_timeout` if `pytest.ini` already loads `pytest_timeout` (duplicate plugin registration).

### Wave detail — W5 (DONE)

- [x] **SEED-RG-FV:** `ops_scripts/ci/seed_apps_rg_fact_vectors_chroma.py` — idempotent ingest from smoke fixture at `CHROMA_PERSIST_DIR` or `data/cache/chromadb`; `--force` to wipe + re-ingest; **bypass** `APPS_RG_SEED_FACT_VECTORS_BYPASS=1`.
- [x] **`run_contract_gates`:** SEED gate immediately before CHECK-RG-FACT-VECTORS; **900s** subprocess timeout for seed (model load). **Filtered** `--gate CHECK-RG-FACT-VECTORS` runs seed prelude once, then the readiness gate.
- [x] Readiness gate remains **advisory** by default (`APPS_RG_FACT_VECTORS_FAIL_CLOSED` still opt-in).

---

## Evidence receipts (filesystem SSOT)

| Receipt | Path |
|--------|------|
| Section retrieval profile | `apps_rg/config/domain_contract/section_retrieval_profile.yaml` |
| Smoke ingest fixture | `tests/fixtures/apps_rg/fact_vectors_c0_smoke.chroma_input` |
| Hermetic runtime test | `tests/_apps_contract/test_c0_fact_vectors_chroma_runtime.py` |
| Operator proof script | `tools/apps_rg/prove_fact_vectors_c0_runtime.py` |
| **W5 CI seed** | `ops_scripts/ci/seed_apps_rg_fact_vectors_chroma.py` |
| Contract gates wiring | `ops_scripts/ci/run_contract_gates.py` (SEED-RG-FV + timeout + `--gate` prelude) |
| Readiness gate script | `ops_scripts/ci/check_apps_rg_fact_vectors_readiness.py` |
| Readiness JSON (generated) | `artifacts/ci/apps_rg_fact_vectors_readiness_gate.json` |
| Ingestion proof JSON (generated) | `artifacts/apps_rg/c0_embedding_gap/ingestion_proof.json` |
| C0 runtime proof JSON (generated) | `artifacts/apps_rg/c0_embedding_gap/c0_runtime_proof.json` |
| Notion summary PATCH (operator) | `tools/notion/patch_apps_rg_fact_vectors_c0_plan_w5_notion.py` |

---

## Canonical environment

- **`CHROMA_PERSIST_DIR`:** unset → default `data/cache/chromadb` under repo (same as gate).
- **`EMBEDDING_ENABLED`:** `true` when Chroma path is set (C0 guard).
- **Collection:** `fact_vectors`; **dim:** 1024.

---

## Notion

- **Plans DB row:** `apps-rg-fact-vectors-c0-notion-d4e8c2`; Status **Completed** (retrospective + W5 closeout).
- **Patch summaries:** `python tools/notion/patch_apps_rg_fact_vectors_c0_plan_w5_notion.py` (requires `NOTION_TOKEN`).

---

## Risks

- `artifacts/*` is largely gitignored — proofs are local unless committed by exception.
- SEED-RG-FV skips (exit 0) when `chromadb` / `sentence-transformers` are missing; on those machines CHECK-RG-FV may still ERROR until deps are installed.
