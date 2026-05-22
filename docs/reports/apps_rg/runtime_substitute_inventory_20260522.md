# apps_rg Runtime Substitute Inventory (W0.1)

Plan: [apps-rg-runtime-substitute-burndown-c4e8f1.md](../../.cursor/plans/apps-rg-runtime-substitute-burndown-c4e8f1.md)

## S1 — Chroma DefaultEmbeddingFunction (MiniLM 384d)

| Field | Value |
|-------|-------|
| Authority replaced | BGE-M3 1024d |
| Guard | `apps_rg/runtime/chroma_precomputed_collection.py` |
| Env | `APPS_RG_FORBID_CHROMA_DEFAULT_EF`, `CHROMA_DISABLE_DEFAULT_EMBEDDING` |
| CI | `ops_scripts/ci/check_apps_rg_chroma_collection_ef.py` |

## S2 — pseudo_digest_fallback (32d)

| Field | Value |
|-------|-------|
| Trigger | BGE load fail when not fail-closed |
| Code | `apps_rg/cache/r1b_bge_embedding.py` |
| W5 guard | `r1b_chroma_read_surface_projection._assert_bge_vector_for_chroma_upsert` |

## S3 — Ledger/graph slice masquerading as retrieval

| Field | Value |
|-------|-------|
| Code | `apps_rg/runtime/c0/c02_evidence_fetch.py` |
| Receipt | `c0_authority_mode=ledger_graph_primary` in `c02_chroma_query` |

## S4 — Skipped C0.2 hybrid retrieval lane

| Field | Value |
|-------|-------|
| Prior symptom | `spine_c0_retrieve_skipped:bounded_section_path` in `c05_fec_packet.py` |
| W4 fix | Product fail-closed raises `C0EvidenceGapError` |

## S5 — C0 retrieve fail-soft

| Field | Value |
|-------|-------|
| Code | `apps_rg/runtime/bindings/c0_binding.py` (~396) |
| W4 fix | Re-raise on `product_fail_closed_runtime()` |

## S6 — C0.2 lane maybe_upsert (same-run write)

| Field | Value |
|-------|-------|
| Code | `c02_fact_vector_ingest.maybe_upsert_c02_fact_vectors`, `evidence_room.py` |
| W2 fix | `product_section_skip_lane_upsert()` → `c02_chroma_write.status=skipped_not_required` |
| Env | `APPS_RG_ALLOW_C02_CHROMA_INDEX_REFRESH=1` + `APPS_RG_INDEX_MAINTENANCE_ENTRYPOINT=1` |

## S7 — Product shortcuts

| Field | Value |
|-------|-------|
| Env opt-out | `APPS_RG_ALLOW_PRODUCT_SHORTCUTS=1` |
| W1 default | `product_fail_closed_runtime()` true for all `python -m apps_rg` |

## S8 — Qwen offline stub

| Field | Value |
|-------|-------|
| Guard | `apps_rg/runtime/qwen_live_only_guard.py` |
| Stub | `qwen_offline_contract_stub.py` (disabled on product) |

## S9 — Mock judges

| Field | Value |
|-------|-------|
| Policy | `assert_production_runtime` in `__main__.py` |
| Tests | `tests/_apps_contract/test_apps_rg_section_mock_provider_policy.py` |

## S10 — Assembly structural-only

| Field | Value |
|-------|-------|
| Env | `APPS_RG_ASSEMBLY_STRUCTURAL_ONLY` |

## S11 — phase0_synthetic lanes

| Field | Value |
|-------|-------|
| Bar | `lane_run_dir_meets_product_bar` rejects `phase0_synthetic` path |

## S12 — X1D cloud judges (non-Qwen)

| Field | Value |
|-------|-------|
| Note | Documented alternate providers; distinct from MOCKED |

## Cross-cutting invariant (W2+W4)

Product PASS may depend on `c02_chroma_query` + ledger authority receipts, **never** on same-run `c02_chroma_write` unless bound pre-run `index_build_receipt.json` exists.

## Operator symptoms

| Symptom | Likely substitute |
|---------|-------------------|
| BGE loaded but briefing not embedded | Lane upsert vs query confusion (S6) |
| PASS with only ledger atoms | Skipped hybrid retrieve (S4/S5) |
| 384d Chroma hits | Legacy DefaultEmbeddingFunction collection (S1) |

## Example artifacts

`artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260522_121758/`
