# Authority Enforcement — Minimal Implementation Plan

**Version**: 1.0 · **Status**: Design · **Date**: 2026-07
**Companion docs**:
- `docs/requirements/agentic_source_authority_model.md`
- `docs/requirements/agentic_requirements_registry_spec.md`
**Audit basis**: Leakage RCA from 2026-07 session (4 confirmed vectors)

---

## 1. Implementation Phases — Ordered by Risk / Leverage

### Phase 0 — Metadata enrichment at ingest (requires collection rebuild)

**Files**: `ingest_arch_docs.py`, `ingest_curated_agent_docs.py`
**Size**: ~5 lines each
**Risk**: Low — metadata additions only; no logic change

| Field to add | arch_docs value | curated (web) | curated (local ADR) |
|---|---|---|---|
| `source_collection` | `"arch_docs"` | `"curated_agent_docs"` | `"curated_agent_docs"` |
| `authority_tier` | `"T4_implementation_evidence"` | derive from `topic_bucket` | `"T4_repo_canonical"` |
| `normative_scope` | `"evidence_only"` | `"external_authority"` | `"repo_internal"` |
| `invalid_for_normative_use` | `True` | `False` | `False` |

**Derivation for `authority_tier` in curated (web)**:
```python
_TOPIC_BUCKET_TO_TIER = {
    "tool_contracts":  "T2_standard",
    "rag_retrieval":   "T3_guidance",
    "orchestration":   "T3_guidance",
    "safety_eval":     "T3_guidance",
    "arch_standards":  "T3_guidance",
    "observability":   "T3_guidance",
}
# default: "T3_guidance"
```

**Collection rebuild required**: Yes for both `arch_docs` and `curated_agent_docs`.
Rebuild command:
```bash
python tools/generate/ingestion/ingest_arch_docs.py
python tools/generate/ingestion/ingest_curated_agent_docs.py
```
Both are idempotent (upsert). Run dry-run first.

---

### Phase 1 — Policy domain in query intent detector (no rebuild)

**Files**: `query_intent_detector.py`, `query_router.py`
**Size**: ~15 lines total (new pattern list + 2-line routing entry)
**Risk**: Low — additive only; existing domains unchanged

**`query_intent_detector.py` addition**:
```python
_policy_patterns = [
    r"\bconstitu(tion|tional)\b",
    r"\bsafety\s+(rule|constraint|policy|boundary|layer)\b",
    r"\bguardian\b",
    r"\binjection\s+control\b",
    r"\bhard\s+(rule|constraint|limit)\b",
    r"\btrust\s+boundary\b",
    r"\bpolicy\s+enforcement\b",
    r"\bagentic\s+(policy|rule|constraint)\b",
]
```

Add `"policy"` to `detect_topic_domain()` scoring dict — check BEFORE architecture (higher specificity).

**`query_router.py` addition**:
```python
# In _get_target_collection() or equivalent domain→collection map:
"policy": "curated_agent_docs",
```

No other routing changes. `collapse_group_dedup_max=2` already applies to `best_practice` and `tool_contracts`; add `"policy"` to that set.

**Test requirement**: Add parametrized cases to `TestDetectTopicDomain` covering:
- `"constitutional hard constraints"` → `"policy"`
- `"L5 safety trust boundary"` → `"policy"` (not `"architecture"`)
- `"guardian exemption gate"` → `"policy"`

---

### Phase 2 — Evidence-shaping normative gate (no rebuild)

**File**: `evidence_shaper.py`
**Size**: ~20 lines (new function + signal class)
**Risk**: Low — additive function; no change to existing functions

**Function to add**:
```python
def filter_normative_sources(
    results: list[_T],
    allowed_collections: tuple[str, ...] = ("curated_agent_docs",),
    allowed_tiers: tuple[str, ...] = (
        "T1_vendor", "T2_standard", "T3_guidance", "T4_repo_canonical"
    ),
) -> tuple[list[_T], list[_T]]:
    # Returns (accepted, rejected)
    # invalid_for_normative_use defaults to True (safe fail-closed)
```

**CitationAnchor provenance fix** (~3 lines):
Populate `CitationAnchor.collection` from `chunk.metadata.get("source_collection", "unknown")`
instead of from the routing-level `EvidenceBundle.collection`.

**Test requirement**: Add `TestFilterNormativeSources` class covering:
- arch_docs chunk → rejected
- curated web chunk → accepted
- curated local ADR chunk → accepted
- missing `source_collection` field → rejected (fail-closed default)
- empty input → empty accepted + empty rejected

---

### Phase 3 — Authority rerank tier-awareness (no rebuild)

**File**: `evidence_shaper.py` (`apply_authority_rerank`)
**Size**: ~10 lines (add `tier_discount` multiplier lookup)
**Risk**: Low — backward-compatible via default parameter

**Discount table** (new):
```python
_TIER_RERANK_DISCOUNT = {
    "T1_vendor":                    1.00,
    "T2_standard":                  1.00,
    "T3_guidance":                  0.85,
    "T4_repo_canonical":            0.50,
    "T4_implementation_evidence":   0.00,   # arch_docs: no bonus
}
```

**Call signature change** (backward-compatible):
```python
def apply_authority_rerank(
    results: list[_T],
    authority_bonus: float = 0.15,
    tier_aware: bool = False,          # opt-in; existing callers unaffected
) -> list[_T]:
```

When `tier_aware=True`: `effective_bonus = authority_bonus * authority_level * tier_discount`.
When `tier_aware=False` (default): existing behavior unchanged.

---

### Phase 4 — Eval harness source tracking (no rebuild)

**File**: `retrieval_eval_curated.py`
**Size**: ~10 lines
**Risk**: Low — metrics addition only

**Add to per-chunk metrics**: `source_collection` field recorded alongside `dist_at_1`.
**Add to per-query report**: `arch_docs_contamination` counter — number of arch_docs chunks in top-5 for normative query classes.
**Threshold check**: `arch_docs_contamination = 0` for `policy`, `best_practice`, `tool_contracts` queries → report PASS/FAIL.

---

## 2. Files — Change / No-Change Matrix

### Files that MUST change

| File | Phase | Change |
|------|-------|--------|
| `tools/generate/ingestion/ingest_arch_docs.py` | 0 | Add 4 metadata fields |
| `tools/generate/ingestion/ingest_curated_agent_docs.py` | 0 | Add 4 metadata fields + derivation logic |
| `agentic_core/L3_orchestration/reasoning/engines/query_intent_detector.py` | 1 | Add `_policy_patterns` + `"policy"` domain |
| `agentic_core/L3_orchestration/reasoning/engines/query_router.py` | 1 | Map `"policy"` → `curated_agent_docs` |
| `agentic_core/L3_orchestration/reasoning/engines/evidence_shaper.py` | 2 + 3 | Add `filter_normative_sources()` + tier-aware rerank |
| `tools/eval/retrieval_eval_curated.py` | 4 | Add `source_collection` tracking + contamination metric |

### Files that MUST NOT change

| File | Reason |
|------|--------|
| `hybrid_search_engine.py` | Enforcement belongs at router + shaper layer, not the engine. The engine is correctly collection-agnostic. |
| `docs/operations/curated_collection_runbook.md` | Update pass thresholds only AFTER Phase 4 eval confirms metrics. |
| `tests/unit/*/test_query_routing.py` | Existing tests MUST NOT be modified — only add new test classes. |

---

## 3. RCA Closure Mapping

| Audit RCA | Phase that closes it | Mechanism |
|-----------|---------------------|-----------|
| RCA-1: policy queries route to arch_docs | Phase 1 | New `"policy"` domain + routing |
| RCA-2: no `source_collection` in metadata | Phase 0 | Explicit field at ingest |
| RCA-3: authority_rerank is collection-blind | Phase 3 | Tier-aware discount in reranker |
| RCA-4: CitationAnchor.collection from routing context | Phase 2 | Read from chunk metadata |
| RCA-5: no normative gate in evidence_shaper | Phase 2 | `filter_normative_sources()` gate |
| RCA-6: curated local ADRs have no scope marker | Phase 0 | `normative_scope="repo_internal"` |

---

## 4. Collection Rebuild Sequence

Phases 1–4 do NOT require a collection rebuild. Only Phase 0 does.

Rebuild sequence:
```
1. python tools/generate/ingestion/ingest_curated_agent_docs.py --dry-run
2. python tools/generate/ingestion/ingest_curated_agent_docs.py
3. python tools/generate/ingestion/ingest_arch_docs.py --dry-run (if dry-run supported)
4. python tools/generate/ingestion/ingest_arch_docs.py
5. python tools/eval/retrieval_eval_curated.py --k 5 --live-path --out docs/reports/retrieval_eval_curated_v5.md
```

**Regression gate**: v5 eval MUST meet or exceed v4 thresholds:
- curated overall win rate ≥ 95%
- canonical_hit_rate = 1.000
- tooling_contamination = 0.000
- `arch_docs_contamination = 0` for all policy/best_practice/tool_contracts queries (new metric)

---

## 5. Success Criteria

| Criterion | Verification method |
|-----------|-------------------|
| arch_docs cannot serve as normative source | Rule V-1 in validity gate rejects all arch_docs chunks |
| policy queries do not reach arch_docs | `TestDetectTopicDomain` + routing integration test |
| `source_collection` present in all chunks | Metadata audit query post-rebuild |
| `invalid_for_normative_use=True` in all arch_docs chunks | Metadata audit query post-rebuild |
| `filter_normative_sources()` rejects arch_docs | `TestFilterNormativeSources` unit tests |
| Tier-aware rerank gives arch_docs 0 bonus | `TestApplyAuthorityRerank` tier-aware tests |
| v5 eval: arch_docs_contamination = 0 for normative queries | `retrieval_eval_curated.py` Phase 4 output |
| Overall retrieval quality unchanged or better | v5 win rate ≥ 95% |

---

## 6. Artifacts to Create (implementation phase)

| Artifact | Type | When |
|----------|------|------|
| `docs/requirements/registry/policy/AGEN-0001.yaml` | Requirement | After Phase 2 |
| `docs/requirements/registry/policy/AGEN-0002.yaml` | Requirement | After Phase 2 |
| `docs/requirements/registry/best_practice/AGEN-0050.yaml` | Requirement | After Phase 2 |
| `docs/reports/retrieval_eval_curated_v5.md` | Eval report | After Phase 4 |

Requirement YAML files are created manually (human-authored), not generated from arch_docs.
