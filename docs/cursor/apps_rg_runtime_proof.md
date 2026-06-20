# apps_rg Runtime Proof — Operator Checklist (W8.2)

Plan: [apps-rg-runtime-substitute-burndown-c4e8f1.md](../../.codex/plans/apps-rg-runtime-substitute-burndown-c4e8f1.md) · Env cleanup: [apps-rg-env-kill-switch-cleanup-f8e2a3.md](../../.codex/plans/apps-rg-env-kill-switch-cleanup-f8e2a3.md)

## Proof classification (closeout 2026-05-22)

The substitute-burndown implementation closeout is **PARTIAL**:

| Class | Status |
|-------|--------|
| CONTRACT_TEST_PROOF | Delivered (pytest) |
| IMPLEMENTATION_RECEIPT | Delivered (code + this doc) |
| LIVE_RUNTIME_PROOF | **Not yet** — requires live section/integrated run |
| RELEASE_ELIGIBLE_PROOF | **Not claimed** |

Receipt: [runtime_substitute_burndown_w0_w8_receipt.md](../../artifacts/apps_rg/plans/runtime_substitute_burndown_w0_w8_receipt.md)

## Brown & Brown executive_summary (strict product)

Child plan (live hybrid + W2B): [apps-rg-hybrid-live-jd-selection-f8e2b3](../../.codex/plans/apps-rg-hybrid-live-jd-selection-f8e2b3.md) · W1 receipt: [apps_rg_hybrid_live_proof_w1_receipt.md](../reports/apps_rg/apps_rg_hybrid_live_proof_w1_receipt.md)

### Pre-run (index write — not product PASS)

```bash
set CHROMA_PERSIST_DIR=c:\Git\Agentic-Workflow-FRESH\data\cache\chromadb
set EMBEDDING_ENABLED=1
python tools/ingestion/chroma_ingest_pipeline.py --collection fact_vectors --execute
python tools/generate/ingestion/build_sparse_index.py --collection fact_vectors
```

**W1 blocker taxonomy** (if hybrid lanes do not complete): `sparse_bm25_index_missing`, `fact_vectors_collection_missing`, `dense_index_unavailable`, `embedding_config_missing`, `provider_failure`. Status must be **BLOCKED**, not PARTIAL/PASS on miss.

Optional dedicated index maintenance (emits `index_build_receipt.json`, `product_eligible=false`):

```bash
set APPS_RG_ALLOW_C02_CHROMA_INDEX_REFRESH=1
set APPS_RG_INDEX_MAINTENANCE_ENTRYPOINT=1
```

### Product section run (read-only index default)

`python -m apps_rg` bootstraps `CHROMA_PERSIST_DIR` and `EMBEDDING_ENABLED` automatically from the repo root (via `bootstrap_apps_rg_embedding_env`). Manual env is only needed to **override** or **opt out** (`EMBEDDING_ENABLED=false`).

```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
REM Do NOT set APPS_RG_ALLOW_C02_CHROMA_INDEX_REFRESH on --section product runs
python -m apps_rg --section executive_summary ^
  --target-company "Brown & Brown" ^
  --target-role "SVP IT Strategy & Innovation" ^
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt ^
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

### Expected receipts

| Receipt field | Expected |
|---------------|----------|
| `product_fail_closed` | `true` |
| `proof_class` | `PRODUCT_STRICT` |
| `c02_chroma_write.status` | `skipped_not_required` |
| `c02_chroma_query.dense/sparse/metadata` | `required` → `completed` or `failed_BLOCKED` |
| `c02_chroma_query.c0_retrieval_mode` | `ledger_plus_hybrid_retrieval` when hybrid ran |
| `c02_chroma_query.reason` | `product_hybrid_bounded_section_retrieval` (not `spine_chroma_enrich_disabled`) |
| `c0_authority_mode` | `ledger_graph_primary` |

`APPS_RG_SPINE_CHROMA_ENRICH` does **not** enable product hybrid; profile-driven `perform_product_hybrid_retrieval` does.

### Forbidden on canonical product runs (`python -m apps_rg --section`)

| Env / lever | Effect if set | Product behavior |
|-------------|---------------|------------------|
| `APPS_RG_ALLOW_PRODUCT_SHORTCUTS=1` | Disables fail-closed | **Forbidden** on release proof |
| `APPS_RG_C0_EVIDENCE_ROOM=0` | Skips C0 room + hybrid | **Runtime error** (unless `APPS_RG_TEST_HARNESS=1`) |
| `APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH=0` | Raw proof_pool to PA | **Runtime error** (unless test harness) |
| `APPS_RG_SPINE_CHROMA_ENRICH` | *(removed)* | No longer read — use profile hybrid only |
| `APPS_RG_ALLOW_C02_CHROMA_INDEX_REFRESH=1` | Same-run index write | **Forbidden** on section product PASS |
| `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1` | Stub L2 | **Forbidden** |

### Positive `c02_vector_query` truth fields (required)

`retrieval_profile_ref`, `product_hybrid_required`, `product_hybrid_attempted`, `dense_attempted`, `sparse_attempted`, `bm25_available`, `failure_reason`, `proof_classification`. Legacy `spine_chroma_enrich_disabled` must not appear.

### Other forbidden

- Same-run upsert + query claiming product PASS

### Verification

```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest tests/unit/apps_rg/test_c02_chroma_lifecycle_product_pass.py tests/unit/apps_rg/test_product_output_policy.py -q
python ops_scripts/ci/check_apps_rg_chroma_collection_ef.py
```
