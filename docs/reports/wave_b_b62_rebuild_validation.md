# Wave B6.2 — Rebuild and Targeted Validation Report

**Date:** 2026-04-16  
**Scope:** ext_authority only — targeted at F25  
**Collection after rebuild:** `ext_authority` — 592 docs  
**Embedding model:** `BAAI/bge-m3` (1024-dim, CUDA)  
**ChromaDB path:** `data/cache/chromadb`

---

## 1. Dry-Run Results

| Field | Value |
|-------|-------|
| Command | `python tools/generate/ingestion/ingest_ext_authority.py --dry-run` |
| Exit code | `0` |
| Total sources | 30 |
| Chunks projected | **585** |
| `required_ok` | 5 |
| `required_fail` | 0 |
| `optional_fail` | 0 |
| P13 URL resolved | **YES** (HTTP 200) |
| Dry-run delta vs B6.1 (579) | **+6 chunks from P13** |

**Pre-existing optional failures (not introduced by B6.2):**
- `openai-agents-python/main/docs/models.md` — HTTP 404 (pre-existing since B6)
- `anthropics/anthropic-cookbook/main/patterns/agents/subagent.ipynb` — HTTP 404 (pre-existing since B6)

No new blockers introduced. No metadata contract errors. Exit code 0.

---

## 2. Rebuild Results

| Field | Value |
|-------|-------|
| Command | `python tools/generate/ingestion/ingest_ext_authority.py` |
| Exit code | `0` |
| Elapsed | `6.8s` |
| Collection | `ext_authority` |
| Doc count before B6.2 | 586 (post-B6.1) |
| Doc count after B6.2 | **592** |
| **Net B6.2 additions** | **+6 chunks from P13** |
| Rebuild target | `ext_authority` only ✅ |
| `repo_evidence` modified | No ✅ |
| `ext_raw` modified | No ✅ |

---

## 3. Per-Source Chunk Counts (B6.2 addition only)

| Source | Domain | Chunks added | Notes |
|--------|--------|-------------|-------|
| P13 — LangGraph libs/langgraph README | `langchain-ai/langgraph` (libs) | **6** | Library-level README; covers durable execution + human-in-the-loop; distinct from existing repo-level README |

*Exact count confirmed from collection delta: 586 → 592 = +6.*

---

## 4. Metadata Validation

All new B6.2 chunks validated via ingestion pipeline output:

| Check | Result |
|-------|--------|
| `invalid_for_normative_use=False` on all new chunks | ✅ |
| `source_collection=ext_authority` on all new chunks | ✅ |
| `source_url` starts with `https://raw.githubusercontent.com/` | ✅ |
| `authority_tier=T3_guidance` on all new chunks | ✅ |
| `collapse_group=langgraph_core` populated | ✅ |
| `doc_family=reference` populated | ✅ |
| `topic_bucket=orchestration` populated | ✅ |
| No duplicate `source_url` values introduced | ✅ |
| No local file paths in `source_url` | ✅ |
| Metadata contract fields unchanged | ✅ |
| P13 URL distinct from existing `langchain-ai/langgraph/main/README.md` | ✅ |

---

## 5. Targeted Validation — F25 Only

Validation script: `tools/diag/b62_f25_validation.py`  
Raw results: `artifacts/b62_f25_validation_raw.json`  
Embedding model: `BAAI/bge-m3` (CUDA, fp16 applied)  
Collection size at query time: 592 docs

### F25 — Tiered Healing / Escalation

**Query:** "How do agentic systems implement confidence-scored tiered healing dispatch routing failures through local rules, model retry, and human escalation?"

| Metric | B6.1 Baseline | B6.2 Result |
|--------|---------------|-------------|
| `dist@1` | 0.5043 | **0.5043** |
| `delta` | — | 0.0000 |
| `n_rel<0.50` | 0 | 0 |
| P13 (`langgraph_core`) in top-5 | — | **no** |
| P12 (Temporal) in top-5 | — | no |
| Live grade | WEAK | **WEAK** |
| Improved vs B6.1 | — | **no** |

### Top-5 Results

| Rank | dist | collapse_group | heading |
|------|------|---------------|---------|
| 1 | 0.5043 | `openai_agents_raw_github` | Running agents > MCP > Agent-level MCP configuration |
| 2 | 0.5125 | `openai_swarm` | Examples |
| 3 | 0.5190 | `openai_agents_raw_github` | Running agents > **Durable execution integrations and human-in-the-loop** |
| 4 | 0.5200 | `openai_swarm` | Swarm (experimental, educational) > Usage |
| 5 | 0.5206 | `openai_agents_raw_github` | Tools > Hosted tools > Hosted container shell + skills |

**Contamination:** 0 — all results from `ext_authority` only. ✅

### Assessment

P13 was successfully ingested and indexed but did not surface in the top-5 for the F25 query. The `libs/langgraph/README.md` is a concise ~6KB library introduction; while it uses "durable execution" and "human-in-the-loop", these appear as short bullet points rather than dense explanatory prose. The embedding distance remains identical to the B6.1 baseline.

**Encouraging signal from rank 3:** `running_agents.md` "Durable execution integrations and human-in-the-loop" (dist=0.5190) confirms that LangGraph-flavored vocabulary is being retrieved, but just outside the relevance threshold.

**Root cause of persistent gap:** The F25 query contains the phrase "confidence-scored tiered healing dispatch" — a compound AI-specific concept that does not appear verbatim or in close paraphrase in any currently ingested source. All top-5 results sit in the 0.50–0.52 range, indicating the concept space is being approached but no source provides sufficiently dense coverage.

**F25 remains the single open Wave B blocker.** F12, F14, and F17 are ADEQUATE and ready for B7.

---

## 6. Blockers Fixed in B6.2

No ingestion blockers encountered. P13 URL resolved on first attempt (HTTP 200). Dry-run exit 0.

| Blocker | Fix | Status |
|---------|-----|--------|
| None | — | — |

---

## 7. B6.2 Final Status by Family

| Family | Pre-B6.2 | Post-B6.2 | Ready for B7? |
|--------|----------|-----------|--------------|
| F12 | ADEQUATE (marginal) | ADEQUATE (marginal) | Yes |
| F14 | ADEQUATE | ADEQUATE | Yes |
| F17 | ADEQUATE (marginal) | ADEQUATE (marginal) | Yes |
| F25 | WEAK | **WEAK** | **No — one source needed** |

---

## 8. B7 Recommendation for F25

F25 requires a source with **dense prose** covering the following vocabulary cluster:  
`confidence-scored` + `tiered` + `healing` + `dispatch` + `escalation` + `agentic`.

Candidates not yet attempted:

| Candidate | Why likely better | URL status |
|-----------|------------------|-----------|
| AutoGen core documentation on error handling or termination conditions | AutoGen core has explicit discussion of failure conditions and agent termination/handoff | Not verified |
| A dedicated multi-agent failure-escalation tutorial (e.g., AutoGen notebook) | Notebook format provides denser prose than README | Not verified |
| An AI-native healing framework paper or guide (e.g., SWE-agent, AutoCodeRover) | Would contain precise "healing dispatch" vocabulary | Not verified |

**B7 extended audit** should attempt one of these before freeze-gate rerun.

---

## 9. Anti-Drift Compliance

| Constraint | Status |
|-----------|--------|
| Only `ext_authority` changed | ✅ |
| Only F25 targeted | ✅ |
| `query_router.py` not modified | ✅ |
| `evidence_shaper.py` not modified | ✅ |
| `retrieval_eval_curated.py` not modified | ✅ |
| `repo_evidence` ingestion not modified | ✅ |
| `ext_raw` ingestion not modified | ✅ |
| Metadata contract not changed | ✅ |
| `wave_b_closeout.md` not modified | ✅ |
| `wave_c_handoff_contract.md` not modified | ✅ |
| No F12/F14/F17/F21/F22/F28 sources added | ✅ |
| No Wave C scope | ✅ |
| Full B7 audit/freeze gates not run | ✅ |
