# apps_rg C0 ownership split — scope (completed)

**Status:** Completed (2026-05-22)  
**Receipt:** [apps_rg_c0_ownership_split_closeout_receipt.md](apps_rg_c0_ownership_split_closeout_receipt.md)  
**Tests:** [test_apps_rg_c0_ownership_split.py](../../tests/_apps_contract/test_apps_rg_c0_ownership_split.py)

## Principle

apps_rg binds to agentic_core **contracts and law**, not to generic core C0 builders on section lanes.

| Layer | Owns |
|-------|------|
| **agentic_core** | `FinalEvidenceContract` shape, `EvidenceItem`, GateVerdict / 00C semantics, L5/Exit/X2 law, sparse/hybrid primitives |
| **apps_rg** | Section evidence room C0.1–C0.7, ledger/SRFS/skills graph proof, `allowed_fact_ids` SSOT, section FEC builder, PA handoff |

## Delivered

1. **C0.5 default:** `spine_chroma_enrich=false`; no default `c0_retrieve_apps_rg` merge.
2. **Explicit enrich:** `APPS_RG_SPINE_CHROMA_ENRICH=1` or `spine_chroma_enrich=True`; enrichment marked non-authoritative.
3. **C0.3 rename:** `c03_skills_graph_v1`; `canonical_c0_3_claimed=false` unless core GraphRAG runs.
4. **C0.2 split artifacts:** `c01_retrieval_plan.json`, `c02_atoms.json`, `c02_vector_query.json`.
5. **Chroma policy:** write in C0.2 OR query in C0.5 enrich — not both by default.
6. **C0.6:** fake receipt-only refine removed from room orchestration.
7. **C0.7:** handoff audit with `allowed_fact_ids` preservation.
8. **Metrics:** `SupportTarget` = proof prefixes only (`fact:`, `ledger:`, `proof_pool:`, `srfs:`).
9. **Authority:** `c0_authority_mode=ledger_graph_primary` on bridge.

## Out of scope (explicit)

- Core GraphRAG on section room path
- Default spine Chroma merge
- JD/resume/briefing as proof in metrics targets
- agentic_core product logic changes

## Verification

- Contract tests: `pytest tests/_apps_contract/test_apps_rg_c0_ownership_split.py`
- Canonical CLI: `python -m apps_rg --section headline` (artifacts under `artifacts/apps_rg/runtime_proofs/headline/c0_ownership_split_proof/`)
