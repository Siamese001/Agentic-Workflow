# Wave B — Migration and Rebuild Plan

**Version**: 1.0 · **Status**: Design-Final · **Phase**: B1 (no code)
**Precondition**: `wave_b_chromadb_topology.md` and `wave_b_metadata_contract.md` are finalized.
**Hard constraint**: No code changes occur in B1. B2 writes ingestion scripts. B3 executes rebuilds.

---

## 1. Chunking Strategy for `ext_authority` (External Target-State Lane)

### Section-Aware Chunking

- Use `chunk_by_headings()` pattern from `ingest_arch_docs.py` as the base implementation.
- Split at H1/H2/H3 heading boundaries. Build a `" > "`-delimited `heading_path` breadcrumb for every chunk.
- Never split across heading boundaries mid-paragraph. A new heading always starts a new chunk.
- Minimum chunk body: 80 chars. Skip sections shorter than this.
- Maximum chunk size: 2000 chars.
- Overlap: 200 chars (character-based, paragraph-break-preferring).

### Contextual Chunk Headers

- Every chunk body must be prefixed with its `heading_path` so the chunk is self-contained when retrieved out of context.
- Format: `[{heading_path}]\n\n{chunk_body}`
- This header is stored in the `document` field. It is included in embedding.

### Parent/Child Structure

- **Required** for `ext_authority`. Justified by precision retrieval need.
- H1 or H2 sections become parent chunks. H3 sub-sections become child chunks of their nearest H2 parent.
- Parent chunk: contains the full section text (up to 2000 chars). `parent_id = ""`. `child_ids = JSON list of child chunk IDs`.
- Child chunk: contains the H3 subsection text. `parent_id = parent_chunk_id`. `child_ids = "[]"`.
- If a document has no H2/H3 structure, every chunk is a root chunk with `parent_id = ""`.
- At retrieval time: when a child chunk is a top-K hit, expand to its parent for context.

### Table Handling

- A Markdown table encountered within a section is kept as one unit. Never split a table mid-row.
- If a table alone exceeds 2000 chars, it is its own chunk (no character-based re-split).
- Tables are prefixed with their heading context: `[{heading_path}]\n\n{table_markdown}`.

### Code vs Prose Separation

- Fenced code blocks (` ``` ` delimited) are never split mid-block.
- If a code block exceeds 2000 chars, it is its own chunk with heading context.
- A minimum 50-char text buffer is required before any split point adjacent to a code fence.
- Short code blocks (< 200 chars) are absorbed into the surrounding prose chunk.

### Whether Existing Chunks Must Be Rebuilt

**YES — full rebuild required for `ext_authority`.**

- `curated_agent_docs` chunks were built without `source_band`, without parent/child IDs, and without contextual chunk headers.
- The `source_collection` field value will change from `"curated_agent_docs"` to `"ext_authority"`.
- No incremental path exists. All 17 web sources must be re-fetched and re-ingested into a new collection.

**For `repo_evidence`:**

- The 15 local sources migrating from `curated_agent_docs` require a rebuild with new metadata fields.
- The `arch_docs` population requires adding `source_band=repo_implementation` and renaming `source_collection`.
- If `arch_docs` already has `T4_implementation_evidence` and `invalid_for_normative_use=True` (it does), the metadata delta can be applied as an upsert rather than a full delete+rebuild. However a clean rebuild is preferred for schema consistency.

**For `ext_raw`:**

- Incremental. Add missing authority metadata (`source_band`, `authority_tier`, `normative_scope`) via upsert.
- Identify and delete any chunk whose `source_url` appears in `ext_authority`.

---

## 2. Migration and Rebuild Sequence

### Phase B2 — Write Ingestion Scripts (Code Phase, Future)

| Task | File to create or modify | Notes |
|------|--------------------------|-------|
| B2-1 | `tools/generate/ingestion/ingest_ext_authority.py` (NEW) | New ingestion script for `ext_authority` collection. Splits web sources from curated list. Section-aware + parent/child chunking. Full metadata contract. |
| B2-2 | `tools/generate/ingestion/ingest_repo_evidence.py` (NEW) | New ingestion script for `repo_evidence`. Ingests 15 local sources (Lane C) + scans repo docs (Lane D, formerly arch_docs). |
| B2-3 | `tools/generate/ingestion/ingest_ext_knowledge.py` (MODIFY) | Rename target collection to `ext_raw`. Add authority metadata. Add URL dedup against `ext_authority`. Remove `ingest_agent_framework_docs.py` references. |
| B2-4 | `tools/generate/ingestion/ingest_agent_framework_docs.py` (RETIRE) | Mark RETIRED. Add top-level docstring: "RETIRED — replaced by ingest_ext_authority.py". Do not delete immediately; archive after B3 validates. |
| B2-5 | `docs/requirements/agentic_source_authority_model.md` (MODIFY) | Add T5_unvetted tier. Add `source_band` field to provenance contract. Update collection class table to reflect new names. |
| B2-6 | `docs/operations/curated_collection_runbook.md` (MODIFY) | Update to reflect 3-collection topology. Replace `curated_agent_docs` rebuild instructions with `ext_authority` + `repo_evidence`. |

### Phase B3 — Execute Rebuilds (In Order)

**Step 1: Build `ext_authority` (new collection, no dependencies)**

```
Prerequisite:  ext_authority does NOT exist
Action:        python tools/generate/ingestion/ingest_ext_authority.py
Expected:      ~17 sources, ~400-600 chunks
Validation:    Run contract validation queries from wave_b_metadata_contract.md
               All ext_auth_bad, ext_auth_local = 0
               Regression harness: curated_win_rate ≥ 95%, arch_docs_contamination = 0
               Manual: verify source_url set = expected 17 URLs, no local paths
```

**Step 2: Build `repo_evidence` (replaces arch_docs)**

```
Prerequisite:  ext_authority passes validation
Action:        python tools/generate/ingestion/ingest_repo_evidence.py
Expected:      ~9000+ chunks (8840 arch_docs population + 15 local sources)
Validation:    Run contract validation queries
               All repo_ev_bad, repo_ev_web = 0
               source_band=repo_canonical count = expected 15 sources worth of chunks
               source_band=repo_implementation count ≈ former arch_docs count
```

**Step 3: Validate and update `ext_raw`**

```
Prerequisite:  ext_authority source_url set is confirmed (needed for dedup)
Action:        python tools/generate/ingestion/ingest_ext_knowledge.py --add-metadata --dedup
Expected:      Existing chunks updated with authority fields; URL duplicates removed
Validation:    ext_raw_contaminated = 0 (no overlap with ext_authority URLs)
               All chunks have source_band=unvetted, invalid_for_normative_use=True
```

**Step 4: Retire `curated_agent_docs`**

```
Prerequisite:  ext_authority and repo_evidence both pass validation
Action:        Delete curated_agent_docs collection
               chromadb_client.delete_collection("curated_agent_docs")
Validation:    client.list_collections() does not contain "curated_agent_docs"
               Regression harness re-run: no regressions (routing points to ext_authority)
```

**Step 5: Retire `arch_docs`**

```
Prerequisite:  repo_evidence passes validation
Action:        Delete arch_docs collection
               chromadb_client.delete_collection("arch_docs")
Validation:    client.list_collections() does not contain "arch_docs"
               Query routing updated to use repo_evidence instead of arch_docs
```

### Rollback Plan

| Step | Rollback action |
|------|----------------|
| Step 1 fails validation | Delete `ext_authority`, fix ingest script, re-run Step 1. `curated_agent_docs` still live. |
| Step 2 fails validation | Delete `repo_evidence`, fix ingest script, re-run Step 2. `arch_docs` still live. |
| Step 3 fails | Revert `ext_knowledge` upsert by rebuilding from source. No other collection affected. |
| Step 4 premature | Do NOT delete `curated_agent_docs` until Steps 1+2 have passed validation AND routing has been updated. |

---

## 3. What Rebuilds First / What Is Incremental

| Collection | Rebuild type | Reason |
|-----------|-------------|--------|
| `ext_authority` | **Full rebuild** (new collection) | New collection. New chunking strategy. No prior chunks to carry. |
| `repo_evidence` | **Full rebuild** (rename from arch_docs + delta) | Preferred for schema consistency. Incremental possible for arch_docs population only. |
| `ext_raw` | **Incremental** (upsert + dedup) | Existing chunks retain value; only metadata fields and URL dedup need updating. |
| `curated_agent_docs` | **Delete** after migration | Not rebuilt. Retired. |
| `arch_docs` | **Delete** after repo_evidence validates | Not rebuilt. Replaced by repo_evidence. |

---

## 4. Validation Required After Rebuild

### Per-Collection Validation (run after each step)

```
1. Contract constraint checks — all counts = 0:
   ext_auth_bad, ext_auth_local, repo_ev_bad, repo_ev_web, ext_raw_contaminated, missing_fields

2. Lane population counts:
   ext_authority[source_band=target_state_authority] ≥ 1 (MCP SDK at minimum)
   ext_authority[source_band=supporting_guidance] ≥ 10 (OpenAI + Anthropic sources)
   repo_evidence[source_band=repo_canonical] ≥ 50 chunks (15 local sources)
   repo_evidence[source_band=repo_implementation] ≥ 5000 chunks (broad repo coverage)

3. Regression harness (tools/eval/retrieval_eval_curated.py, updated for new collection names):
   ext_authority overall win rate ≥ 95%
   arch_docs_contamination = 0 for normative query classes
   canonical_hit_rate (ext_authority) = 1.000
   policy class → ext_authority only (0 results from repo_evidence)
```

### System-Level Validation (run after Steps 4+5)

```
4. No references to curated_agent_docs or arch_docs in:
   - query_router.py collection targets
   - evidence_shaper.py collection allowlists
   - Regression harness collection lists

5. semantic_search("what should agentic systems do") → results ONLY from ext_authority

6. semantic_search("what does this repo's constitutional.md say") → results from repo_evidence only
```

### Contamination Prevention During Migration

- Do NOT point any normative-path query routing at `ext_authority` until Step 1 validation passes.
- Do NOT delete `curated_agent_docs` until routing has been confirmed pointing to `ext_authority`.
- Keep `arch_docs` live during repo_evidence build. Flip routing atomically after repo_evidence validation.
- `ext_raw` can be updated at any time — it is never a normative source.

---

## 5. Files to Change in B2/B3

| File | Action | Reason |
|------|--------|--------|
| `tools/generate/ingestion/ingest_ext_authority.py` | **CREATE** | New ingestion for target-state collection |
| `tools/generate/ingestion/ingest_repo_evidence.py` | **CREATE** | New ingestion for repo current-state collection |
| `tools/generate/ingestion/ingest_ext_knowledge.py` | **MODIFY** | Add authority metadata, URL dedup, rename target collection |
| `tools/generate/ingestion/ingest_agent_framework_docs.py` | **RETIRE** | URL list duplicated in ext_authority |
| `tools/generate/ingestion/ingest_curated_agent_docs.py` | **RETIRE** | Replaced by ingest_ext_authority.py + ingest_repo_evidence.py |
| `tools/generate/ingestion/ingest_arch_docs.py` | **RETIRE** | Replaced by ingest_repo_evidence.py |
| `docs/requirements/agentic_source_authority_model.md` | **MODIFY** | Add T5_unvetted tier, source_band field, updated collection classes |
| `docs/operations/curated_collection_runbook.md` | **MODIFY** | Update for 3-collection topology |
| Any file referencing `arch_docs` collection name in query routing or evidence shaping | **MODIFY** | Update to `repo_evidence` |
| Any file referencing `curated_agent_docs` collection name in query routing or evidence shaping | **MODIFY** | Update to `ext_authority` |

---

## 6. Files NOT to Change

| File | Reason |
|------|--------|
| `tools/mcp/vector_db_server.py` | Collection-agnostic MCP server. All collection names passed as parameters by callers. |
| All files in `agentic_core/` | No ChromaDB at the production layer. |
| `tools/generate/archiving/archiver.py` | SQLite archiving only; no ChromaDB references. |
| `tools/generate/utils/file_utils.py` | SQLite locking utilities; no ChromaDB references. |
| All `docs/architecture/adr/` files | Design-only artifacts; not ingestion code. |
| `tools/eval/retrieval_eval_curated.py` | Will need updates for new collection names, but that is a B3 validation task, not a B2 code task. Flag as B3 dependency. |
| `docs/requirements/wave_b_chromadb_topology.md` | SSOT for topology — this document. |
| `docs/requirements/wave_b_metadata_contract.md` | SSOT for metadata — the sibling document. |

---

## 7. Single Final Recommendation

**3-collection topology with metadata-defined lanes is the correct answer.**

The root cause of target-state contamination is not `arch_docs` leaking into normative queries — that path is already blocked by `invalid_for_normative_use=True`. The root cause is that `curated_agent_docs` mixes external authority (can define target state) with local repo docs (cannot define target state) in one collection, making the boundary enforced only by metadata filtering rather than physical separation.

Physical collection separation between `ext_authority` and `repo_evidence` makes this boundary structural and impossible to bypass silently. A retrieval call to `ext_authority` cannot return a local ADR. A call to `repo_evidence` cannot return an OpenAI SDK page. The contamination vector is eliminated at the collection boundary, not at the application layer.

The five lanes (target_state_authority, supporting_guidance, repo_canonical, repo_implementation, unvetted) are implemented via `source_band` metadata within 3 collections, giving full lane granularity without schema explosion.

**Build order**: `ext_authority` first (it is the normative-path source and must be validated before routing changes), then `repo_evidence`, then `ext_raw` incrementally, then delete the retired collections atomically after routing is confirmed.

**Stop condition**: This design is precise enough to implement without ambiguity. No design decisions remain open. B2 may begin writing code.
