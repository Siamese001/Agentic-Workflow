# Wave B — Final Metadata Contract

**Version**: 1.0 · **Status**: Design-Final · **Phase**: B1 (no code)
**Scope**: Every chunk stored in any Wave-B ChromaDB collection must satisfy this contract.
**Authority**: This document supersedes the per-collection schemas in individual ingestion scripts.

---

## 1. Mandatory Fields (ALL chunks, ALL collections)

Every chunk stored in `ext_authority`, `repo_evidence`, or `ext_raw` MUST carry every field in this table.
Missing fields are a fail-closed ingest error — the chunk must not be written.

| Field | Type | Allowed values | Description |
|-------|------|----------------|-------------|
| `source_collection` | `str` | `"ext_authority"` \| `"repo_evidence"` \| `"ext_raw"` | Physical collection name. Set at ingest time. Immutable. |
| `source_band` | `str` | `"target_state_authority"` \| `"supporting_guidance"` \| `"repo_canonical"` \| `"repo_implementation"` \| `"unvetted"` | Lane discriminator within collection. Used in `where=` filters. |
| `authority_tier` | `str` | `"T1_vendor"` \| `"T2_standard"` \| `"T3_guidance"` \| `"T4_repo_canonical"` \| `"T4_implementation_evidence"` \| `"T5_unvetted"` | Tier for rerank discount model. |
| `normative_scope` | `str` | `"external_authority"` \| `"repo_internal"` \| `"evidence_only"` \| `"unvetted"` | Determines normative eligibility. |
| `invalid_for_normative_use` | `bool` | `True` \| `False` | Gate field. If `True`, chunk is REJECTED from all normative bundles. |
| `source_type` | `str` | `"web"` \| `"local"` \| `"scraped"` | Origin of source material. |
| `topic_bucket` | `str` | `"arch_standards"` \| `"orchestration"` \| `"rag_retrieval"` \| `"safety_eval"` \| `"observability"` \| `"tool_contracts"` \| `"unclassified"` | Content topic for routing. |
| `doc_family` | `str` | `"adr"` \| `"architecture"` \| `"reference"` \| `"guide"` \| `"spec"` \| `"standard"` \| `"contract"` \| `"overview"` \| `"doc"` \| `"notebook"` \| `"web"` \| `"playbook"` | Document type taxonomy. |
| `source_url` | `str` | Non-empty. Full https:// URL or repo-relative path. | Canonical source locator. Used for dedup, provenance, and citation. |
| `heading_path` | `str` | Section breadcrumb or `"no-headings"` | `" > "`-delimited H1 > H2 > H3 path for precision retrieval. |
| `collapse_group` | `str` | Non-empty string | Dedup cluster key. Chunks sharing a `collapse_group` are capped by `collapse_group_dedup`. |
| `title` | `str` | Non-empty | Human-readable document title (max 200 chars). |
| `chunk_index` | `int` | ≥ 0 | Position of this chunk within its source document. |
| `canonical_digest` | `str` | 16-char hex | SHA-256[:16] of the source document text at ingest time. Used for freshness detection. |

---

## 2. Conditional Fields

Fields required only when the condition is met.

| Field | Type | Condition | Description |
|-------|------|-----------|-------------|
| `version_or_date` | `str` | When source carries a version string or date | e.g. `"v29"`, `"2026-04"`, `"main@abc1234"` for GitHub raw. Empty string if not available. |
| `parent_id` | `str` | When parent/child chunking is enabled (required for `ext_authority`) | ChromaDB document ID of the parent section chunk. Empty string for root-level chunks. |
| `child_ids` | `str` | When parent/child chunking is enabled (required for `ext_authority`) | JSON-encoded list of child chunk IDs. Empty string for leaf chunks. |
| `domain` | `str` | `source_type = "scraped"` | Origin domain for scraped content (e.g. `"docs.trychroma.com"`). |
| `file_path` | `str` | `source_type = "local"` | Repo-relative path (forward slashes). |

---

## 3. Per-Collection Derivation Rules

Derivation rules are authoritative. Ingestion scripts MUST follow these exactly.

### `ext_authority`

```
source_collection       = "ext_authority"
invalid_for_normative_use = False  # always for ext_authority

IF source_band = "target_state_authority":
    authority_tier ∈ {T1_vendor, T2_standard}
    normative_scope = "external_authority"

IF source_band = "supporting_guidance":
    authority_tier = T3_guidance
    normative_scope = "external_authority"

topic_bucket: use TOPIC_BUCKET_TO_TIER map from ingest_curated_agent_docs.py
source_type = "web"
source_url = full https:// URL (GitHub raw or official docs)
```

**Lane A assignment rule** (`target_state_authority` / T2_standard):
- Source is a formal protocol specification, SDK README, or official API reference
- Currently: `modelcontextprotocol/python-sdk README.md`

**Lane B assignment rule** (`supporting_guidance` / T3_guidance):
- Source is high-quality third-party technical guidance (framework docs, pattern libraries)
- Currently: all OpenAI agents, Anthropic cookbook, LangGraph, AutoGen sources

### `repo_evidence`

```
source_collection       = "repo_evidence"
invalid_for_normative_use = True  # always for repo_evidence
source_type = "local"
source_url = repo-relative path (forward slashes)
file_path = same as source_url

IF source_band = "repo_canonical":
    authority_tier = "T4_repo_canonical"
    normative_scope = "repo_internal"
    # Sources: the 15 hand-curated local docs from curated_agent_docs

IF source_band = "repo_implementation":
    authority_tier = "T4_implementation_evidence"
    normative_scope = "evidence_only"
    # Sources: all remaining repo markdown (former arch_docs coverage)
```

### `ext_raw`

```
source_collection       = "ext_raw"
source_band             = "unvetted"
authority_tier          = "T5_unvetted"
normative_scope         = "unvetted"
invalid_for_normative_use = True  # always for ext_raw
source_type = "scraped"
```

---

## 4. Authority Tier Rerank Discount

The `collection_discount` multiplier from `agentic_source_authority_model.md` is extended:

```python
TIER_DISCOUNT: dict[str, float] = {
    "T1_vendor":                    1.00,
    "T2_standard":                  1.00,
    "T3_guidance":                  0.85,
    "T4_repo_canonical":            0.50,   # normative for repo scope only
    "T4_implementation_evidence":   0.00,   # no rerank bonus — ever
    "T5_unvetted":                  0.00,   # no rerank bonus — ever
}
```

---

## 5. Field Consistency Constraints

These constraints are enforced at ingest time (fail-closed) and at validation time (regression harness).

| Constraint | Rule |
|-----------|------|
| C1 | `source_collection` must match the physical collection being written |
| C2 | `ext_authority` chunks must have `invalid_for_normative_use = False` |
| C3 | `repo_evidence` and `ext_raw` chunks must have `invalid_for_normative_use = True` |
| C4 | `ext_authority` chunks must have `source_url` starting with `https://` |
| C5 | `repo_evidence` chunks must NOT have `source_url` starting with `https://` |
| C6 | `source_band` must be consistent with `authority_tier` per derivation rules above |
| C7 | `normative_scope = "external_authority"` implies `invalid_for_normative_use = False` |
| C8 | `authority_tier in {T4_*, T5_*}` implies `invalid_for_normative_use = True` |
| C9 | `ext_raw` chunk `source_url` must NOT appear in `ext_authority.source_url` set |
| C10 | `heading_path` must be non-empty (use `"no-headings"` if no sections found) |
| C11 | `collapse_group` must be non-empty |
| C12 | `chunk_index` must be sequential per `(source_url, parent_id)` pair |

---

## 6. Validation Queries

Run after each collection build to verify contract compliance.

```python
# C2 / C3 check
ext_auth_bad = [m for m in ext_authority.get()['metadatas']
                if m.get('invalid_for_normative_use') != False]

repo_ev_bad = [m for m in repo_evidence.get()['metadatas']
               if m.get('invalid_for_normative_use') != True]

# C4 check
ext_auth_local = [m for m in ext_authority.get()['metadatas']
                  if not m.get('source_url', '').startswith('https://')]

# C5 check
repo_ev_web = [m for m in repo_evidence.get()['metadatas']
               if m.get('source_url', '').startswith('https://')]

# C9 check
ext_auth_urls = {m['source_url'] for m in ext_authority.get()['metadatas']}
ext_raw_contaminated = [m for m in ext_raw.get()['metadatas']
                        if m.get('source_url') in ext_auth_urls]

# Missing fields check
REQUIRED = {'source_collection', 'source_band', 'authority_tier', 'normative_scope',
            'invalid_for_normative_use', 'source_type', 'topic_bucket', 'doc_family',
            'source_url', 'heading_path', 'collapse_group', 'title',
            'chunk_index', 'canonical_digest'}
for col_name, col in [('ext_authority', ext_authority), ('repo_evidence', repo_evidence)]:
    missing = [m for m in col.get()['metadatas'] if not REQUIRED.issubset(m.keys())]
    print(f"{col_name}: {len(missing)} chunks missing required fields")

# All counts should be 0 for a compliant build.
```
