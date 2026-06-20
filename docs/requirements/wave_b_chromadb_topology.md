# Wave B — ChromaDB Collection Topology

**Version**: 1.0 · **Status**: Design-Final · **Phase**: B1 (no code)
**Scope**: Full redesign of the ChromaDB data plane to enforce external-authority target-state isolation.
**Non-negotiable rule**: Only external-authority sources may define target-state agentic architecture and C0 best practices.

---

## 1. Ranked Design Decisions

| Rank | Decision | Rationale |
|------|----------|-----------|
| D1 | **Split `curated_agent_docs` along the `source_type` boundary** | The collection currently mixes external web sources (target-state authority) with local repo docs (current-state evidence) in the same collection. This is the root cause of the authority-contamination risk. The split is the non-negotiable prerequisite for all other decisions. |
| D2 | **Use 3 collections with 5 metadata-defined lanes** | 5 physical collections would create schema explosion and rebuild cost. Lane identity is enforced by the `source_band` field at the metadata-contract level. Physical separation is required only where the contamination risk is structural (external vs repo). |
| D3 | **Collapse `arch_docs` into `repo_evidence`** | `arch_docs` is `T4_implementation_evidence`. The 15 local sources from `curated_agent_docs` are `T4_repo_canonical`. Both are current-state-only. One collection with two `source_band` values is correct; two collections adds rebuild cost without retrieval benefit. |
| D4 | **Keep `ext_knowledge` as `ext_raw` (optional lane, justified)** | `ext_knowledge` contains domains not in `ext_authority` (NIST, HuggingFace, Paul Graham, LangChain raw, ChromaDB docs, on-disk playbooks). These domains have research value for gap analysis but are unvetted. Retention is justified. Rename enforces the unvetted status explicitly. |
| D5 | **Retire `ingest_agent_framework_docs.py`** | Its URL list is a subset of what `ext_authority` will ingest. Maintaining a second ingestion script for the same URLs with lower metadata quality is an anti-pattern. |
| D6 | **Add `source_band` as the lane discriminator field** | `authority_tier` distinguishes tiers but not lanes within a collection. `source_band` is a flat, queryable string that maps exactly to one of the 5 lanes. It is the enforcement field for `where=` filters at retrieval time. |
| D7 | **Section-aware parent/child chunking for `ext_authority`** | External authority docs require precision retrieval. Flat char-based chunks collapse multiple concepts and cause low-precision top-K. Parent/child chunking allows per-section retrieval while preserving context via `parent_id`. |

---

## 2. Final Collection Topology

### 3-Collection Design

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ext_authority                                                           │
│  May define target state. External sources only.                         │
│                                                                          │
│  Lane A: target_state_authority  authority_tier ∈ {T1_vendor, T2_standard} │
│  Lane B: supporting_guidance     authority_tier = T3_guidance            │
└──────────────────────────────────────────────────────────────────────────┘
                          ▲ ONLY COLLECTION ALLOWED for normative use

┌──────────────────────────────────────────────────────────────────────────┐
│  repo_evidence                                                           │
│  Current-state inspection only. Repo content only.                       │
│                                                                          │
│  Lane C: repo_canonical      authority_tier = T4_repo_canonical          │
│  Lane D: repo_implementation authority_tier = T4_implementation_evidence │
└──────────────────────────────────────────────────────────────────────────┘
                          ▲ NEVER used for target state

┌──────────────────────────────────────────────────────────────────────────┐
│  ext_raw         [OPTIONAL LANE — justified]                             │
│  Research use only. Unvetted web scrapes. Never normative.               │
│                                                                          │
│  Lane E: unvetted            authority_tier = T5_unvetted                │
└──────────────────────────────────────────────────────────────────────────┘
                          ▲ NEVER used for target state or current state
```

### Per-Collection Specification

| Field | `ext_authority` | `repo_evidence` | `ext_raw` |
|-------|----------------|-----------------|-----------|
| Replaces | `curated_agent_docs[web]` | `arch_docs` + `curated_agent_docs[local]` | `ext_knowledge` |
| Source origin | External URLs only | Repo files only | Scraped URLs + disk playbooks |
| Lanes | A, B | C, D | E |
| `invalid_for_normative_use` | `False` (Lane A/B) | `True` (always) | `True` (always) |
| Normative use | YES | NEVER | NEVER |
| hnsw:space | cosine | cosine | cosine |
| Embedding model | BAAI/bge-m3 | BAAI/bge-m3 | BAAI/bge-m3 |
| Embedding dim | 1024 | 1024 | 1024 |

### Lane Definitions

| Lane | ID | Collection | `authority_tier` | `source_band` | May define target state | May define current state |
|------|-----|-----------|------------------|---------------|------------------------|------------------------|
| A | target_state_authority | ext_authority | T1_vendor, T2_standard | `target_state_authority` | **YES** | YES |
| B | supporting_guidance | ext_authority | T3_guidance | `supporting_guidance` | YES (with scope) | YES |
| C | repo_canonical | repo_evidence | T4_repo_canonical | `repo_canonical` | **NEVER** | YES |
| D | repo_implementation | repo_evidence | T4_implementation_evidence | `repo_implementation` | **NEVER** | YES |
| E | unvetted | ext_raw | T5_unvetted | `unvetted` | **NEVER** | NEVER |

### Anti-Contamination Constraints

- `ext_authority` MUST NOT contain any chunk whose `source_url` resolves to a local file path.
- `repo_evidence` MUST NOT contain any chunk whose `invalid_for_normative_use = False`.
- `ext_raw` MUST NOT contain any chunk whose `source_url` is already indexed in `ext_authority`.
- `semantic_search(collections=None)` is **BANNED** on normative-path queries. Callers MUST pass `collections=["ext_authority"]`.

---

## 3. Current-to-Future Collection Mapping

### `curated_agent_docs` (32 sources, 579 chunks) → RETIRE

| Sub-population | Criterion | Destination | Destination lane |
|---------------|-----------|-------------|-----------------|
| 17 external web sources | `source_type = "web"` | `ext_authority` | A or B based on `authority_tier` derivation |
| 15 local repo sources | `source_type = "local"` | `repo_evidence` | C (`repo_canonical`) |
| Collection itself | — | DELETE after migration validates | — |

**Explicit source routing:**

*To `ext_authority` (Lane A — T2_standard):*
- `modelcontextprotocol/python-sdk README.md` (MCP SDK — formal protocol spec)

*To `ext_authority` (Lane B — T3_guidance):*
- All `openai/openai-agents-python` docs (8 sources)
- All `anthropics/anthropic-cookbook` pattern notebooks (4 sources)
- `langchain-ai/langgraph README.md`
- `microsoft/autogen README.md`

*To `repo_evidence` (Lane C — T4_repo_canonical):*
- All 5 ADR docs (`adr-0043`, `adr-002`, `adr-0042`, `ADR-018`, `ADR-019`)
- `agentic_process_mapping_exec.md`, `agentic_process_mapping_v29.md`
- `governed-app-contract.md`, `eval_pipeline_acceptance.md`
- `Retrieval_System_SVP.md`, `Technical_Implementation_Guide.md`
- `.codex/rules/constitutional.md`, `.codex/rules/global_rules.md`
- `docs/STANDARDS.md`, `docs/architecture/adg-graph-projection.md`
- `AGENTS.md`

### `arch_docs` (~8840 chunks) → `repo_evidence`

- FULL REBUILD into `repo_evidence` as Lane D (`repo_implementation`, `T4_implementation_evidence`)
- All metadata: `source_band=repo_implementation`, `authority_tier=T4_implementation_evidence`, `invalid_for_normative_use=True`
- The 15 local sources from `curated_agent_docs` are added to the same collection as Lane C.
- Rename enforces the usage boundary. `arch_docs` collection is deleted.

### `ext_knowledge` → `ext_raw`

- INCREMENTAL: add missing authority metadata fields to existing chunks
- DEDUP: remove any chunk whose `source_url` matches a URL in `ext_authority`
- RENAME collection from `ext_knowledge` to `ext_raw`
- `ingest_agent_framework_docs.py` is RETIRED — its URLs are a subset of `ext_authority`

### `ingest_agent_framework_docs.py` → RETIRE

- All its URLs are already covered by the `ext_authority` curated source list
- Duplicate content at lower metadata quality adds noise and maintenance cost
- No replacement needed

### Do repo-local curated ADRs need to split from external curated sources?

**YES — hard yes.** The 15 local sources in `curated_agent_docs` must move to `repo_evidence` (Lane C). They may never co-exist in a target-state collection because their `normative_scope=repo_internal` — they describe what this repo has decided, not what agentic systems universally must do. Any query asking "what should agentic systems do?" must be answered exclusively from `ext_authority`.

---

## 4. Anti-Drift Operating Rule

```
RULE: Anti-drift collection gate

IF query_intent IS IN {normative_requirement, policy, best_practice, tool_contracts, architecture_pattern}:
    MUST query:  ext_authority  (collections=["ext_authority"])
    MUST NOT query: repo_evidence, ext_raw
    MUST NOT return: any chunk where invalid_for_normative_use = True

IF query_intent IS IN {repo_gap, current_state_inspection}:
    MUST query: repo_evidence  (WHERE source_band IN ["repo_canonical", "repo_implementation"])
    MAY query:  ext_authority  (as external baseline)
    MUST NOT use ext_authority results to define "what the repo should do"

IF query_intent IS IN {implementation, code_lookup}:
    MUST query: repo_evidence (WHERE source_band = "repo_implementation")
    MUST NOT query: ext_authority

IF query_intent IS IN {research, broad_background}:
    MAY query: ext_raw (with explicit acknowledgment of unvetted status)
    MUST NOT surface ext_raw results as normative evidence
```

**Enforcement point**: `evidence_shaper.py` must gate on `invalid_for_normative_use` before constructing any requirement bundle. Return `LOW_NORMATIVE_COVERAGE` if `ext_authority` returns empty for a normative query. Do not fall back to `repo_evidence`.
