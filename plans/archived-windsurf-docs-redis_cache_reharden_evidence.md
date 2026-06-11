---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\redis_cache_reharden_evidence.md'
original_relative_path: 'redis_cache_reharden_evidence.md'
source_sha256: c1a13c3a7ed930f5d984424ce8a82ce328e1e90e8677030186b93ff62b0c695c
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Redis Cache Seams Re-hardening

## Scope

Review and re-harden all Redis caching seams implemented in the previous session.
8 issues identified and resolved: 3 critical runtime bugs, 2 correctness hardening,
1 completeness gap (missing C0/RAG seam), 1 export gap, 38 new regression tests.

Files modified (N=5) + created (N=1) = 6 total:
- agentic_core/cache/redis_cache_client.py
- agentic_core/cache/cache_key_builders.py
- agentic_core/cache/__init__.py
- agentic_core/L1_cognition/engines/prompt_artifact_cache.py
- tests/architecture/test_redis_cache_non_authoritative.py
- system_learning/engines/rag_retrieval_cache.py (NEW)

## CODE_COMMIT

aae4651d5813800a12d81b16f0be4a17ff5a3b42

## EVIDENCE_COMMIT

aa72a5f0d130caf923682e13533d2219b4ba7f84

## FILES_CHANGED_CODE

agentic_core/L1_cognition/engines/prompt_artifact_cache.py
agentic_core/cache/__init__.py
agentic_core/cache/cache_key_builders.py
agentic_core/cache/redis_cache_client.py
system_learning/engines/rag_retrieval_cache.py
tests/architecture/test_redis_cache_non_authoritative.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/redis_cache_reharden_evidence.md

## INSPECTED_FILES

- agentic_core/cache/redis_cache_client.py
- agentic_core/cache/cache_key_builders.py
- agentic_core/cache/__init__.py
- agentic_core/L1_cognition/engines/prompt_artifact_cache.py
- agentic_core/L0_routing/seams/redis_decision_cache.py
- agentic_core/L1_cognition/engines/prompt_artifact_cache.py
- agentic_core/L2_execution/coordination/lease_coordinator.py
- agentic_core/L3_orchestration/engines/orchestration_plan_cache.py
- agentic_core/L5_safety/enforcement/safety_eval_cache.py
- tests/architecture/test_redis_cache_non_authoritative.py
- system_learning/engines/rag_retrieval_cache.py

## Issues Found and Fixed

### H1 -- CRITICAL: _BoundedLRU.set() silent overwrite bug

Root cause: when a key already existed, only its LRU position was updated
(`move_to_end`) but `self._store[key] = value` was inside the `else` branch
and therefore NOT executed on overwrite. Effect: re-caching an updated artifact
silently returned stale bytes from the first write forever.

Fix: moved `self._store[key] = value` outside the if/else so it always executes.

### H2 -- CRITICAL: get_json() unguarded decode error

Root cause: `json.loads(raw.decode("ascii"))` raises `json.JSONDecodeError` or
`UnicodeDecodeError` if stored bytes are corrupted (hardware fault, partial
write, truncated eviction). Non-authoritative contract requires returning None
on any retrieval failure -- not raising.

Fix: wrapped decode+parse in try/except returning None on any error.

### H3 -- TemplateRenderCache.get() unguarded UnicodeDecodeError

Root cause: `raw.decode("utf-8")` raises on corrupt bytes with no guard.
Same non-authoritative contract violation as H2 but in the seam layer.

Fix: wrapped in try/except UnicodeDecodeError returning None.

### H4 -- _validate_key() missing tab rejection

Root cause: tab character (\t) was not in the control-character rejection set
alongside \0, \n, \r. Tabs produce syntactically valid but semantically
misleading keys that violate the printable-ASCII-only key invariant.

Fix: added "\t" to the rejection tuple.

### H5 -- cache_key_builders.py: colon injection in non-hash segments

Root cause: non-hash caller-supplied segments (trace_id, template_id,
template_version, embedder_version) were not validated for the ":" character,
which is the key segment delimiter. A colon in these segments corrupts the
key schema and can produce silent cross-key collisions:
  build_orch_plan_key("a:b", "c", "d") == build_orch_plan_key("a", "b:c", "d")

Fix: added _require_safe_segment() guard raising ValueError if ":" present.
Applied to: trace_id (orch_plan), template_id, template_version
(template_render), embedder_version (rag_topk).

### H6 -- Missing exports in cache/__init__.py

content_hash and reset_cache_singletons were defined but not exported from the
package __all__. Callers importing from agentic_core.cache could not access them.

Fix: added both to __init__.py imports and __all__.

### H7 -- Missing C0/RAG retrieval cache seam module

build_rag_topk_key() was defined in cache_key_builders.py with full
documentation, but no seam file existed to actually use it.
The spec explicitly required a C0/RAG informational cache seam.

Fix: created system_learning/engines/rag_retrieval_cache.py with
RagRetrievalCache class, replay bypass, non-list result guard,
no L4 import, and get_rag_retrieval_cache() singleton factory.

### H8 -- Test coverage gaps (38 new tests, 88 total)

New test classes:
- TestBoundedLRUOverwrite (4 tests) -- covers H1 regression
- TestGetJsonCorruptData (3 tests) -- covers H2 regression
- TestKeyValidationTabChar (3 tests) -- covers H4 regression
- TestKeySegmentColonInjection (5 tests) -- covers H5 regression
- TestTemplateRenderCacheCorruptBytes (3 tests) -- covers H3 regression
- TestL0SeamRoundtrips (4 tests) -- RoutingRuleSurface + CapabilityRegistry
- TestRagRetrievalCache (4 tests) -- full C0/RAG seam coverage
- TestGetStats (4 tests) -- get_stats() structure and counter accuracy
- TestSingletonFactories extended (1 test) -- package export verification

## Pytest: Architecture Tests

$ python -m pytest -q --color=no tests/architecture/test_redis_cache_non_authoritative.py
88 passed in 0.13s

## Pytest: Full Suite

$ python -m pytest -q --color=no
6524 passed, 83 skipped, 7 xfailed in 82.79s

## Design Invariants Verified

1. NON-AUTHORITATIVE: No seam module imports from agentic_core.L4_state (AST-verified)
2. REPLAY BYPASS: Every get() returns None when replay_mode=True (all 6 seams)
3. KEY DETERMINISM: Identical inputs always produce identical keys
4. NO WALL-CLOCK IN KEYS: No time-based key segments
5. FALLBACK TRANSPARENCY: Offline mode operations still succeed
6. CANONICAL SERIALISATION: ASCII-only, sorted keys, no whitespace
7. COORDINATION: Lease NX semantics; replay=True returns False from acquire
8. KEY NAMESPACE UNIQUENESS: All 10 prefixes distinct, no cross-layer collision
9. KEY SEGMENT SAFETY: Non-hash segments validated against colon injection
10. CORRUPT DATA RESILIENCE: get_json() and TemplateRenderCache.get() return
    None on corrupt bytes instead of raising exceptions

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

