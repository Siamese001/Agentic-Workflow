# Agentic Source Authority Model

**Version**: 2.0 · **Status**: Active (Wave B2) · **Date**: 2026-07
**Scope**: `ext_authority`, `repo_evidence`, `ext_raw`, retrieval pipeline, requirement-generation path
**Audit basis**: `docs/reports/retrieval_eval_curated_v4.md` + leakage RCA (2026-07) + Wave B2 topology refactor

> **Wave B2 note**: Collections `curated_agent_docs`, `arch_docs`, and `ext_knowledge` are **RETIRED**.
> They are superseded by `ext_authority` (Lane A/B), `repo_evidence` (Lane C/D), and `ext_raw` (Lane E).

---

## 1. Authority Tier Model

Every chunk stored in any ChromaDB collection MUST carry an `authority_tier` metadata field.
The tier determines whether the chunk may contribute to normative requirement artifacts.

| Tier | Label | Description | Normative? | Examples |
|------|-------|-------------|------------|---------|
| T1 | `T1_vendor` | Official vendor or first-party documentation | YES | Anthropic Claude docs, OpenAI platform docs, official MCP SDK README |
| T2 | `T2_standard` | Formal standards, specifications, protocols | YES | MCP Protocol specification, OpenAPI spec, W3C standards |
| T3 | `T3_guidance` | High-quality third-party technical guidance | YES (with scope) | LangGraph docs, AutoGen patterns, Anthropic agent pattern guides |
| T4c | `T4_repo_canonical` | Hand-curated internal repo docs (ADRs, process maps) | NO — evidence only (Wave B2) | Curated local ADRs, internal process mapping docs |
| T4e | `T4_implementation_evidence` | All other internal repo documents | NO — never | repo_evidence Lane D, all internal markdown |
| T5 | `T5_unvetted` | Unvetted scraped web content, not curated | NO — never | ext_raw (Lane E), raw web scrapes |

**Non-negotiable rules**:
- `T4_implementation_evidence` is **permanently excluded** from normative use. No chunk from `repo_evidence` Lane D may become a requirement.
- `T4_repo_canonical` is also excluded from normative use in Wave B2. All repo content is evidence only.
- `T5_unvetted` is **permanently excluded** from all normative and retrieval augmentation paths.

---

## 2. Provenance Metadata Contract

The following five fields MUST be present in every chunk's stored metadata.
They are the enforceable contract for source authority.

| Field | Type | Values | Required |
|-------|------|--------|---------|
| `source_collection` | `str` | `"ext_authority"` \| `"repo_evidence"` \| `"ext_raw"` | Mandatory |
| `source_band` | `str` | `"target_state_authority"` \| `"supporting_guidance"` \| `"repo_canonical"` \| `"repo_implementation"` \| `"unvetted"` | Mandatory (Wave B2) |
| `authority_tier` | `str` | `"T2_standard"` \| `"T3_guidance"` \| `"T4_repo_canonical"` \| `"T4_implementation_evidence"` \| `"T5_unvetted"` | Mandatory |
| `normative_scope` | `str` | `"external_authority"` \| `"repo_internal"` \| `"unvetted"` | Mandatory |
| `source_type` | `str` | `"web"` \| `"local"` \| `"scraped"` | Mandatory |
| `invalid_for_normative_use` | `bool` | `True` \| `False` | Mandatory |

### Derivation rules (at ingest time — Wave B2)

```
ext_authority (Lane A — source_band = "target_state_authority"):
  source_collection       = "ext_authority"
  source_band             = "target_state_authority"
  authority_tier          = "T2_standard"
  normative_scope         = "external_authority"
  invalid_for_normative_use = False

ext_authority (Lane B — source_band = "supporting_guidance"):
  source_collection       = "ext_authority"
  source_band             = "supporting_guidance"
  authority_tier          = "T3_guidance"
  normative_scope         = "external_authority"
  invalid_for_normative_use = False

repo_evidence (Lane C — source_band = "repo_canonical"):
  source_collection       = "repo_evidence"
  source_band             = "repo_canonical"
  authority_tier          = "T4_repo_canonical"
  normative_scope         = "repo_internal"
  invalid_for_normative_use = True   # evidence only in Wave B2

repo_evidence (Lane D — source_band = "repo_implementation"):
  source_collection       = "repo_evidence"
  source_band             = "repo_implementation"
  authority_tier          = "T4_implementation_evidence"
  normative_scope         = "repo_internal"
  invalid_for_normative_use = True   # always

ext_raw (Lane E — source_band = "unvetted"):
  source_collection       = "ext_raw"
  source_band             = "unvetted"
  authority_tier          = "T5_unvetted"
  normative_scope         = "unvetted"
  invalid_for_normative_use = True   # always
```

---

## 3. Source Collection Classes

| Class | Collections (Wave B2) | source_band | Normative use | Repo-gap use | Implementation evidence |
|-------|----------------------|-------------|---------------|-------------|------------------------|
| **Approved normative (canonical spec)** | `ext_authority` Lane A | `target_state_authority` | YES | YES | YES |
| **Approved normative (guidance)** | `ext_authority` Lane B | `supporting_guidance` | YES (with scope) | YES | YES |
| **Internal evidence — repo canonical** | `repo_evidence` Lane C | `repo_canonical` | **NO** (Wave B2) | YES | YES |
| **Internal evidence — implementation** | `repo_evidence` Lane D | `repo_implementation` | **NEVER** | YES | YES |
| **Explicitly invalid — unvetted** | `ext_raw` Lane E | `unvetted` | **NEVER** | **NO** | **NO** |

`ext_raw` (Lane E) is **not approved normative** — it is unvetted and uncurated. Only `ext_authority` sources (Lane A/B) with `invalid_for_normative_use=False` qualify as normative.

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

| Query class | `ext_authority` | `repo_evidence` | `ext_raw` | `code_chunks` |
|-------------|----------------|-----------------|-----------|---------------|
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

**Routing**: `"policy"` → `ext_authority` (same path as `best_practice` and `tool_contracts`).
`repo_evidence` and `ext_raw` are never valid targets for `policy` class queries.

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
| `repo_evidence` (Lane D) | `True` | REJECT — implementation evidence only |
| `repo_evidence` (Lane C) | `True` (Wave B2) | REJECT — evidence only, not normative |
| `ext_raw` (Lane E) | `True` | REJECT — unvetted scraped content |
| Any chunk with `authority_tier = "T4_implementation_evidence"` | `True` | REJECT |
| Any chunk with `authority_tier = "T5_unvetted"` | `True` | REJECT — hardest block |

### Hard allowlist (normative requirement generation)

| Collection | Condition | `normative_scope` | Allowed use |
|------------|-----------|------------------|------------|
| `ext_authority` Lane A | `invalid_for_normative_use = False`, `source_band = "target_state_authority"` | `external_authority` | Universal requirements |
| `ext_authority` Lane B | `invalid_for_normative_use = False`, `source_band = "supporting_guidance"` | `external_authority` | Requirements with guidance scope |

### Fallback rule

If `filter_normative_sources()` returns an empty set: **do not fall back to repo_evidence or ext_raw**. Return empty evidence and surface a `LOW_NORMATIVE_COVERAGE` signal to the caller. A requirement MUST NOT be emitted from an empty or repo-evidence-only bundle.
