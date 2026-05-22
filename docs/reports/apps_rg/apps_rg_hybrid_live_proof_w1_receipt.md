# apps_rg Hybrid Live Proof — W1 Receipt

Plan: [apps-rg-hybrid-live-jd-selection-f8e2b3](../../.cursor/plans/apps-rg-hybrid-live-jd-selection-f8e2b3.md)

## STATUS

**PASS** — `LIVE_RUNTIME_PROOF` (H1 artifact table satisfied)

## PROOF_CLASSIFICATION

| Class | Result |
|-------|--------|
| LIVE_RUNTIME_PROOF | **PASS** |
| CONTRACT_TEST_PROOF | PASS (W0b, separate receipt) |
| RELEASE_ELIGIBLE_PROOF | **Not claimed** |

## Preconditions (operator, outside section CLI)

| Step | Command | Result |
|------|---------|--------|
| fact_vectors readiness | `python ops_scripts/ci/check_apps_rg_fact_vectors_readiness.py` | 4 OK (25 docs, dim 1024) |
| BM25 sparse sidecar | `python tools/generate/ingestion/build_sparse_index.py --collection fact_vectors` | `fact_vectors.db` (25 docs) |

## COMMANDS_RUN

```text
CHROMA_PERSIST_DIR=c:\Git\Agentic-Workflow-FRESH\data\cache\chromadb
EMBEDDING_ENABLED=1
python -m apps_rg --section executive_summary \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md \
  --provider qwen_vllm \
  --allow-non-allow-exit-zero \
  --artifact-dir artifacts/apps_rg/runtime_proofs/executive_summary/real/hybrid_live_20260522_110117
```

**Exit code:** 1 (X2 aggregate FAIL on non-H6 gates; C0 hybrid lanes **completed** before generation)

## PRODUCT_HYBRID_RECEIPT_FIELDS (H1)

Artifact dir: [hybrid_live_20260522_110117](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/hybrid_live_20260522_110117)

| File | Required fields | Observed |
|------|-----------------|----------|
| [c02_vector_query.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/hybrid_live_20260522_110117/c02_vector_query.json) | `product_hybrid: true` | ✅ true |
| Same | `attempted: true` | ✅ true |
| Same | `reason: product_hybrid_bounded_section_retrieval` | ✅ exact |
| Same | `c0_retrieval_mode: ledger_plus_hybrid_retrieval` | ✅ exact |
| Same | `lanes.dense/sparse/metadata` = `completed` | ✅ all completed |
| [c0_evidence_room_receipt.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/hybrid_live_20260522_110117/c0_evidence_room_receipt.json) | `product_hybrid_required: true` | ✅ true |
| Product path | no `spine_chroma_enrich_disabled` as hybrid miss | ✅ absent |

## NOTES

- First attempt [hybrid_live_20260522_110047](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/hybrid_live_20260522_110047) also produced valid H1 `c02_vector_query.json` but failed pre-PA on `graph_pa` UnboundLocalError (fixed in [executive_summary_evidence_capsule.py](../../apps_rg/runtime/sections/executive_summary_evidence_capsule.py)).
- W1 claims **hybrid ran**, not full X3 ALLOW.
