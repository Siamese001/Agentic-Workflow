# Agentic Source Authority Model

**Version**: 1.0 · **Status**: Design · **Date**: 2026-07
**Scope**: `curated_agent_docs`, `arch_docs`, retrieval pipeline, requirement-generation path
**Audit basis**: `docs/reports/retrieval_eval_curated_v4.md` + leakage RCA (2026-07)

---

## 1. Authority Tier Model

Every chunk stored in any ChromaDB collection MUST carry an `authority_tier` metadata field.
The tier determines whether the chunk may contribute to normative requirement artifacts.

| Tier | Label | Description | Normative? | Examples |
|------|-------|-------------|------------|---------|
| T1 | `T1_vendor` | Official vendor or first-party documentation | YES | Anthropic Claude docs, OpenAI platform docs, official MCP SDK README |
| T2 | `T2_standard` | Formal standards, specifications, protocols | YES | MCP Protocol specification, OpenAPI spec, W3C standards |
| T3 | `T3_guidance` | High-quality third-party technical guidance | YES (with scope) | LangGraph docs, AutoGen patterns, Anthropic agent pattern guides |
| T4c | `T4_repo_canonical` | Hand-curated internal repo docs (ADRs, process maps) | CONDITIONAL — repo scope only | Curated local ADRs, internal process mapping docs |
| T4e | `T4_implementation_evidence` | All other internal repo documents | NO — never | arch_docs, all internal markdown not in curated |

**Non-negotiable rule**: `T4_implementation_evidence` is **permanently excluded** from normative use.
`arch_docs` is entirely `T4_implementation_evidence`. No chunk from `arch_docs` may become a requirement.

---

## 2. Provenance Metadata Contract

The following five fields MUST be present in every chunk's stored metadata.
They are the enforceable contract for source authority.

| Field | Type | Values | Required |
|-------|------|--------|---------|
| `source_collection` | `str` | `"arch_docs"` \| `"curated_agent_docs"` \| `"ext_knowledge"` | Mandatory |
| `authority_tier` | `str` | `"T1_vendor"` \| `"T2_standard"` \| `"T3_guidance"` \| `"T4_repo_canonical"` \| `"T4_implementation_evidence"` | Mandatory |
| `normative_scope` | `str` | `"external_authority"` \| `"repo_internal"` \| `"evidence_only"` | Mandatory |
| `source_type` | `str` | `"web"` \| `"local"` \| `"markdown"` | Already exists — verify |
| `invalid_for_normative_use` | `bool` | `True` \| `False` | Mandatory |

### Derivation rules (at ingest time)

```
arch_docs:
  source_collection       = "arch_docs"
  authority_tier          = "T4_implementation_evidence"
  normative_scope         = "evidence_only"
  invalid_for_normative_use = True   # always, no exceptions

curated_agent_docs (source_type = "web"):
  source_collection       = "curated_agent_docs"
  authority_tier          = derive from topic_bucket:
      "tool_contracts"   -> "T2_standard"   (MCP spec, FastMCP)
      "rag_retrieval"    -> "T3_guidance"
      "orchestration"    -> "T3_guidance"
      "safety_eval"      -> "T3_guidance"
      "arch_standards"   -> "T3_guidance"
      "observability"    -> "T3_guidance"
  normative_scope         = "external_authority"
  invalid_for_normative_use = False

curated_agent_docs (source_type = "local"):
  source_collection       = "curated_agent_docs"
  authority_tier          = "T4_repo_canonical"
  normative_scope         = "repo_internal"
  invalid_for_normative_use = False   # normative for repo scope only
```

---

## 3. Source Collection Classes

| Class | Collections | Normative use | Repo-gap use | Implementation evidence |
|-------|------------|---------------|-------------|------------------------|
| **Approved normative** | `curated_agent_docs` (web sources) | YES | YES | YES |
| **Approved supporting** | `curated_agent_docs` (local ADRs) | REPO SCOPE ONLY | YES | YES |
| **Internal comparison-only** | `arch_docs`, `ext_knowledge` | **NO** | YES | YES |
| **Explicitly invalid** | `arch_docs` | **NEVER** | YES | YES |

`ext_knowledge` (raw web scrapes) is also **not approved normative** — it is unvetted and uncurated.
Only `curated_agent_docs` web sources that pass the curation rubric (`score ≥ 0.85`, `required = True`) qualify as normative.

---

## 4. Query Classes and Retrieval Policy

### Query class definitions

| Query class | Domain key | Description |
|-------------|-----------|-------------|
| `normative_req` | normative_requirements | Queries asking what agentic systems MUST/SHOULD do |
| `policy` | policy | Constitutional constraints, safety rules, guardian rules, injection controls |
| `best_practice` | best_practice | How-to, patterns, frameworks, agent design recipes |
| `tool_contracts` | tool_contracts | MCP, FastMCP, tool-call schemas, function tool specs |
| `architecture_pattern` | architecture | External agentic architecture patterns (NOT repo-internal) |
| `repo_gap` | repo_gap | Comparing repo current-state against external standards |
| `implementation` | implementation | Code-level details, module behavior, function contracts |
| `internal_arch` | internal_arch | Internal repo layer design, ADR lookup, current-state structure |

### Retrieval policy matrix

| Query class | `curated_agent_docs` | `arch_docs` | `ext_knowledge` | `code_chunks` |
|-------------|---------------------|-------------|----------------|--------------|
| `normative_req` | ✅ REQUIRED | ❌ EXCLUDED | ❌ EXCLUDED | ❌ |
| `policy` | ✅ REQUIRED | ❌ EXCLUDED | ❌ EXCLUDED | ❌ |
| `best_practice` | ✅ REQUIRED | ❌ EXCLUDED | ❌ EXCLUDED | ❌ |
| `tool_contracts` | ✅ REQUIRED | ❌ EXCLUDED | ❌ EXCLUDED | ❌ |
| `architecture_pattern` | ✅ DEFAULT | ❌ EXCLUDED | ❌ | ❌ |
| `repo_gap` | ✅ (external baseline) | ✅ ALLOWED | ❌ | ❌ |
| `implementation` | ❌ | ✅ ALLOWED | ❌ | ✅ ALLOWED |
| `internal_arch` | ❌ | ✅ ALLOWED | ❌ | ❌ |

**The policy column is the primary fix for audit RCA-1**: policy/constitutional queries MUST NOT reach arch_docs.

---

## 5. Policy Query Domain — Explicit Answer

**YES** — constitutional/safety/guardian/injection/policy terms MUST be separated from generic architecture terms.

**Rationale**: The audit proved that `detect_topic_domain()` currently routes `\bconstitu(tion|tional)\b`, `\bstandard\b`, `\bprinciple\b` → `architecture` domain → `arch_docs`. This means "constitutional hard constraints for agents" goes to the internal repo collection rather than curated external authority.

**New domain**: `"policy"`

**Trigger patterns** (additions to `query_intent_detector.py`):
```
\bconstitu(tion|tional)\b
\bsafety\s+(rule|constraint|policy|boundary|layer)\b
\bguardian\b
\binjection\s+control\b
\bhard\s+(rule|constraint|limit)\b
\btrust\s+boundary\b
\bpolicy\s+enforcement\b
\binvariant\b  (when not paired with structural/code context)
\bagentic\s+(policy|rule|constraint)\b
```

**Routing**: `"policy"` → `curated_agent_docs` (same path as `best_practice` and `tool_contracts`).
`arch_docs` is never a valid target for `policy` class queries.

---

## 6. Authority Rerank — Tier-Aware Discount Model

**Current problem (RCA-3)**: `apply_authority_rerank()` reads `authority_level` from metadata with no collection awareness. arch_docs chunks with `authority_level=0.9` receive the same `+0.135` bonus as curated chunks.

**Fix**: Introduce a `collection_discount` multiplier keyed on `authority_tier` or `source_collection`.

```
collection_discount(chunk):
  if chunk.metadata["authority_tier"] == "T4_implementation_evidence":
      return 0.0       # no rerank bonus for arch_docs — ever
  if chunk.metadata["authority_tier"] == "T4_repo_canonical":
      return 0.5       # half bonus — normative for repo scope only
  if chunk.metadata["authority_tier"] in ("T2_standard", "T1_vendor"):
      return 1.0       # full bonus
  if chunk.metadata["authority_tier"] == "T3_guidance":
      return 0.85      # slight discount vs formal standards
  return 0.0           # default safe: unknown tier → no bonus
```

**Implementation**: Add `tier_discount` parameter to `apply_authority_rerank()`. Default behavior (existing callers) is unchanged by setting `tier_discount=None` (backward-compatible). Normative-path callers pass `tier_discount=True`.

---

## 7. Source Allowlist / Denylist

### Hard denylist (enforced at evidence-shaping gate)

| Collection | `invalid_for_normative_use` | Gate behavior |
|------------|----------------------------|--------------|
| `arch_docs` | `True` | REJECT — strip from normative bundle |
| `ext_knowledge` | `True` | REJECT — unvetted web scrapes |
| Any chunk with `authority_tier = "T4_implementation_evidence"` | `True` | REJECT |

### Hard allowlist (normative requirement generation)

| Collection | Condition | `normative_scope` | Allowed use |
|------------|-----------|------------------|------------|
| `curated_agent_docs` (web) | `invalid_for_normative_use = False` | `external_authority` | Universal requirements |
| `curated_agent_docs` (local ADR) | `invalid_for_normative_use = False` | `repo_internal` | Repo-scoped requirements only |

### Fallback rule

If `filter_normative_sources()` returns an empty set: **do not fall back to arch_docs**. Return empty evidence and surface a `LOW_NORMATIVE_COVERAGE` signal to the caller. A requirement MUST NOT be emitted from an empty or arch_docs-only bundle.
