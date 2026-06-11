---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\chromadb-retrieval-remaining-gaps-b4e7c2.md'
original_relative_path: '_archive\\2026-05\\chromadb-retrieval-remaining-gaps-b4e7c2.md'
source_sha256: 0889769e474bb48c1bc7ed1cb646b0c35b6636c5baaa6d96478a7a4a921a2691
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: chromadb-retrieval-remaining-gaps-b4e7c2
plan_type: refactor
---

# ChromaDB Retrieval Hardening — Remaining Gaps

Addresses the unfixed gaps from the parent plan `chromadb-bge-retrieval-hardening-e9aa09` after code review against the current codebase (ADG snapshot `05032026_0713`).

---

## Context (SCQA)

- **Situation** — The parent plan (`chromadb-bge-retrieval-hardening-e9aa09`, Draft, zero waves executed) identified 16 gaps (G1–G16). Code review of the current workspace reveals that substantial work has already landed **outside** the parent plan's execution lifecycle — likely via related plans (anthropic-rag-gaps, c0-context-assembly, etc.). Many gaps are now fully or partially closed in code.

- **Complication** — The parent plan is stale: its status says TODO on all waves, but ~60% of the gaps it describes are already fixed in the codebase. The remaining ~40% are real, unfixed defects that degrade retrieval quality. The parent plan should be Retired and a focused successor plan should address only the true residual gaps.

- **Question** — What gaps from the original 16 remain open, and what is the minimal plan to close them?

- **Answer** — 6 of the original 16 gaps are still open (G5-partial, G8-partial, G9-partial, G11, G12, G15-partial). This plan closes them in 3 waves.

---

## Gap Analysis — Current State vs Parent Plan

### CLOSED (no further work needed)

| Gap | Description | Evidence of Closure |
|---|---|---|
| **G1** | Silent zero-vector embedding fallback | `ingest_docs.py:347-362` — raises `RuntimeError` on mismatch; no silent fallback. |
| **G2** | Split-brain persist_dir | `chroma_paths.py` SSOT module created at `agentic_core/L4_state/config/chroma_paths.py`; `ingest_code.py:579` and `ingest_docs.py:399` both call `canonical_persist_dir_str()`. |
| **G3** | Lying embedding metadata | `ingest_code.py:477-478` stamps `BGE_MODEL` / `BGE_QUERY_DIM`; `chroma_client.py:90-93` stamps collection-level metadata with same. |
| **G4** | Stale hardcoded ADG snapshot path | `ingest_code.py:587-589` uses `_adg_snapshot.latest_adg_snapshot()` runtime resolver. |
| **G6** | No unified metadata contract | `chunk_metadata.py` (`ChunkMetadataV1`) exists; both `ingest_code.py` and `ingest_docs.py` import and use `build_required`, `validate`, `build_canonical_digest`. |
| **G7** | Re-ingest produces duplicates | `ingest_docs.py:435` uses `canonical_digest` as chunk ID; `ingest_code.py:498` uses same — upsert semantics. |
| **G10** | Coverage hole: zero-arg functions / argless async / methodless classes | `ingest_code.py:290-292` comment confirms W3.2 fix — no longer skips these entities. |
| **G14** | BGE-M3 multi-vector (sparse + ColBERT) unused | Marked P3/optional in parent plan; `build_sparse_index.py` and `validate_sparse_index.py` exist under `tools/generate/ingestion/`. No action required — optional stretch goal. |
| **G16** | ADGNodeResolver ambiguous on duplicate basenames | P3 in parent plan; ADG resolver works adequately with runtime snapshot. Low priority. |

### PARTIALLY CLOSED

| Gap | Description | What's Done | What Remains |
|---|---|---|---|
| **G5** | `repo_adg_graph` collection corrupt | Pipeline comment (`pipeline.py:86-88`) says "stage removed W5.2" and references `tools/retrieval/drop_repo_adg_graph.py`. | **Verify** the collection is actually dropped from the canonical store. If it still exists on disk (corrupt), run the teardown script. |
| **G8** | No post-ingest validation in orchestrator | `pipeline.py:280-295` calls `_validate_stage` after each stage. | **Verify** `_validate_stage.py` validates metadata contract fields (not just row counts). If it only checks counts, add ChunkMetadataV1 field validation. |
| **G9** | Coverage: `apps_*` / `system_learning` / `tools` / `ops_scripts` uningested | `pipeline.py:68-80` adds 12 per-root code ingest stages covering all `apps_*`, `system_learning`, `infrastructure`, `tools`, `ops_scripts`. | **Verify** `ingest_docs.py` covers `AGENTS.md`, `.cursor/rules/*`, `.cursor/plans/*`, `.cursor/skills/*`, ADR bodies. Currently `--source-dir docs` only ingests `docs/`. Need additional doc ingest scope. |
| **G15** | Two parallel ingestion systems | `pipeline.py:112-131` adds `GENERATE_STAGES` under `--with-generate` flag, integrating `tools/generate/ingestion/*` scripts. | The two systems are unified at orchestrator level but the individual scripts still live in separate dirs. Archival of truly duplicated scripts not yet done. Low priority — functional parity achieved. |

### OPEN (requires new work)

| Gap | Description | Current State | Required Work |
|---|---|---|---|
| **G11** | `traces` and `agentic_best_practices` empty | Pipeline skips `traces` when corpus file missing (`pipeline.py:93`). `agentic_best_practices` likely still empty (web stage requires seed URLs). | W1: Verify corpus file exists; if missing, generate from healing contexts. For `agentic_best_practices`, decide: populate or drop. |
| **G12** | BM25 parity — only `code_chunks` has sparse index | `build_sparse_index.py` exists but is not wired into the main pipeline for all collections. | W2: Wire BM25 sidecar build into pipeline for all primary collections; validate via `validate_sparse_index.py`. |
| **G9-docs** | Doc ingest covers only `docs/` | `ingest_docs.py` default `--source-dir docs`; pipeline only invokes with this default. | W1: Add pipeline stages for `AGENTS.md`, `.cursor/rules/`, `.cursor/skills/`, `docs/architecture/adr/`. |
| **G5-verify** | `repo_adg_graph` may still be corrupt on disk | Teardown script exists but may not have been run. | W1: Verify and clean up. |
| **G8-meta** | `_validate_stage` depth unknown | May only validate counts, not contract fields. | W1: Verify and enhance if needed. |
| **NEW-1** | `SovereignChromaClient.__init__` default is hardcoded string | `chroma_client.py:56` uses `"data/cache/chromadb"` literal instead of `canonical_persist_dir_str()`. Callers override, but the default should use the SSOT. | W1: Point default at SSOT function. |

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| Parent plan `chromadb-bge-retrieval-hardening-e9aa09` | Gap definitions G1–G16 | ✅ Reviewed |
| `tools/ingestion/ingest_code.py` | Code ingest defect assessment | ✅ Read lines 1-30, 200-340, 440-610 |
| `tools/ingestion/ingest_docs.py` | Doc ingest defect assessment | ✅ Read full (676 lines) |
| `tools/ingestion/pipeline.py` | Orchestrator assessment | ✅ Read full (366 lines) |
| `agentic_core/L4_state/config/chroma_paths.py` | SSOT persist_dir | ✅ Read full (86 lines) |
| `agentic_core/L4_state/utils/chunk_metadata.py` | Metadata contract | ✅ Read lines 1-80 |
| `agentic_core/L4_state/utils/client/chroma_client.py` | Client assessment | ✅ Read full (310 lines) |
| ADG MCP snapshot `05032026_0713` | Fan-in, blast radius, node verification | ✅ Queried |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|:---:|---|
| **W1** | W1.1–W1.5 | Verify & fix residuals: client default, validate_stage depth, repo_adg_graph cleanup, doc-scope expansion, traces corpus | ~15k | ADG healthy, ChromaDB accessible | ✅ DONE | All 5 verification items confirmed or fixed; doc ingest covers AGENTS.md + rules + ADRs |
| **W2** | W2.1–W2.2 | BM25 parity: wire sparse index build into pipeline for all collections; validate | ~12k | W1 complete; `build_sparse_index.py` working | ✅ DONE | Every primary collection has BM25 sidecar; `validate_sparse_index.py` passes |
| **W3** | W3.1 | Parent plan retirement + cleanup: retire `chromadb-bge-retrieval-hardening-e9aa09` to Retired status; update Notion | ~3k | W1–W2 green | ✅ DONE | Parent plan Status=Retired in Notion; this plan Status=Completed |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|:---:|
| W1.1 | Fix `SovereignChromaClient` default | `chroma_client.py` | Import cycle risk — verify no circular import from `chroma_paths` | ~2k | ✅ DONE |
| W1.2 | Verify `_validate_stage` depth | `tools/ingestion/_validate_stage.py` | Already validates ChunkMetadataV1 fields, embedding dim/model, and builds BM25 sidecars | ~3k | ✅ DONE (already adequate) |
| W1.3 | Verify/clean `repo_adg_graph` | Run `tools/retrieval/drop_repo_adg_graph.py` if collection still exists | Compactor error may block deletion | ~2k | ✅ DONE (already clean — not in either store) |
| W1.4 | Expand doc ingest scope | `pipeline.py` (add stages for AGENTS.md, rules, skills, ADRs) | Need to verify `ingest_docs.py` handles non-`docs/` roots | ~5k | ✅ DONE (3 new stages added + validator entries) |
| W1.5 | Traces corpus verification | `data/corpus/healing_contexts_corpus.jsonl`; `agentic_best_practices` decision | Corpus may be empty or missing | ~3k | ✅ DONE (correct by design — gated on data availability) |
| W2.1 | Wire BM25 into pipeline | `pipeline.py` (add sparse index build after each dense stage) | Already wired in `_validate_stage.py:193-194`; cleaned stale `TARGET_COLLECTIONS` | ~8k | ✅ DONE (already wired) |
| W2.2 | Validate sparse indexes | Run `validate_sparse_index.py` across all collections | Updated `TARGET_COLLECTIONS` for full pipeline parity | ~4k | ✅ DONE |
| W3.1 | Parent plan retirement | Notion status update; this plan completion | None | ~3k | ✅ DONE |

---

## Out of Scope

- **Replacing BGE-M3 with a larger model** (parent plan §10)
- **Moving off ChromaDB** (ADR-018 stands)
- **Reranker model training** (parent plan W4.2 ships hook only; that hook may already exist)
- **BGE-M3 multi-vector** (P3, optional, sparse + ColBERT)
- **ADGNodeResolver duplicate-basename fix** (P3, working adequately)
- **Archiving duplicate scripts** (functional parity achieved at orchestrator level; archival is cosmetic)
- **Online/streaming ingest**

---

## ADG_GRAPH_LAYER_EVIDENCE

### Materialized-view citations

- **`mv_hotspot_centrality`** — `chroma_client.py` (node 1015) not in top-20 global hotspots; confirms bounded blast radius for W1.1 default fix.
- **`mv_graph_reverse_dependency_hotspots`** — used to verify `SovereignChromaClient` symbol fan-in (18 edges) is manageable.
- **`mv_dependency_cone_risk`** — cone risk from `pipeline.py` (node 9147) into consumers is zero (script, not library); confirms orchestrator changes are safe.

### Semantic edges used

- `imports` — `SovereignChromaClient` fan-in (18 consumers across L_TOOLS, L_APP, L_TEST, L1).
- `reads_from` / `writes_to` — persist_dir write sites (ingest scripts) confirmed using SSOT.

### P-view cross-references

- **`v_p0_apps_direct_infra`** — `apps_lic/types/lic_vector_memory_types.py` imports `SovereignChromaClient` directly (acceptable: typed reference, not bypass).
- **`v_p1_mis_layered_infra`** — no tools/ingestion script imports L1/L2/L3 reasoning modules (clean).

---

## ADG_HOTSPOT_REPORT

| Rank | Node / File | Layer | Archetype | Fan-in | Impact |
|---|---|---|---|---:|---|
| 1 | `chroma_client.py` (SovereignChromaClient symbol) | L4 | STATE_NODE | 18 | P2 — default fix is safe; all callers override persist_dir |
| 2 | `pipeline.py` | L_TOOLS | ORCHESTRATOR | 0 | P3 — script, not library; changes have no downstream blast |
| 3 | `ingest_docs.py` | L_TOOLS | ORCHESTRATOR | 0 | P3 — script; doc-scope expansion is additive |

---

## Rollback / Checkpoint

- W1 changes are individually revertible via `git revert`.
- W2 BM25 sidecar build is additive — no existing data modified.
- No deletion of existing data in any wave.

---

## References

- Parent plan: `.cursor/plans/chromadb-bge-retrieval-hardening-e9aa09.md`
- `agentic_core/L4_state/config/chroma_paths.py` — SSOT persist_dir
- `agentic_core/L4_state/utils/chunk_metadata.py` — ChunkMetadataV1 contract
- `tools/ingestion/pipeline.py` — unified orchestrator
- `tools/ingestion/_validate_stage.py` — post-stage validator
- `tools/generate/ingestion/build_sparse_index.py` — BM25 builder
- ADG snapshot `05032026_0713` (133,045 nodes / 822,438 edges)
