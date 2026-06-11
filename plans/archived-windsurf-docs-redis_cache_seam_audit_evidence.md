---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\redis_cache_seam_audit_evidence.md'
original_relative_path: 'redis_cache_seam_audit_evidence.md'
source_sha256: fe54d8713a88bde0a9ca521ccd4492a07a68bdf45bcacb9efb12738e0cfc45dc
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Redis Cache Seam Audit — G1/G2/G3/G4 Full Remediation

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Scope

Remediate 4 gaps in Redis cache architecture:
- G1: Wire cache seams to actual callers via `get_or_fetch()` read-through helpers
- G2: Audit and tombstone shadow Redis clients in L4
- G3: Restore SHA-256 hash validation with env-var escape hatch
- G4: Write architecture invariant tests (happy + non-happy paths)

Files modified:
- agentic_core/cache/cache_key_builders.py
- agentic_core/L0_routing/seams/redis_decision_cache.py
- agentic_core/L1_cognition/engines/prompt_artifact_cache.py
- agentic_core/L3_orchestration/engines/orchestration_plan_cache.py
- agentic_core/L5_safety/enforcement/safety_eval_cache.py
- agentic_core/L4_state/caching/__init__.py
- agentic_core/L4_state/caching/redis_mcp_client.py
- agentic_core/L4_state/memory/blob_storage_provider.py
- agentic_core/L4_state/memory/sovereign_semantic_cache.py
- agentic_core/L4_state/reasoning/CachedStateLedger.py
- tests/architecture/test_redis_cache_wiring_invariants.py (new)

## CODE_COMMIT

befb4fa9491db80863dcdcc915e3621414efbec3

## EVIDENCE_COMMIT

a3ae05c2b28709cf6b474b42fa6947d6ea878705

## FILES_CHANGED_CODE

agentic_core/L0_routing/seams/redis_decision_cache.py
agentic_core/L1_cognition/engines/prompt_artifact_cache.py
agentic_core/L3_orchestration/engines/orchestration_plan_cache.py
agentic_core/L4_state/caching/__init__.py
agentic_core/L4_state/caching/redis_mcp_client.py
agentic_core/L4_state/memory/blob_storage_provider.py
agentic_core/L4_state/memory/sovereign_semantic_cache.py
agentic_core/L4_state/reasoning/CachedStateLedger.py
agentic_core/L5_safety/enforcement/safety_eval_cache.py
agentic_core/cache/cache_key_builders.py
tests/architecture/test_redis_cache_wiring_invariants.py

## FILES_CHANGED_EVIDENCE

agentic_core/L1_cognition/engines/prompt_artifact_cache.py
agentic_core/L3_orchestration/engines/orchestration_plan_cache.py
tests/architecture/test_redis_cache_wiring_invariants.py

## INSPECTED_FILES

agentic_core/cache/redis_cache_client.py
agentic_core/L0_routing/seams/redis_decision_cache.py
agentic_core/L1_cognition/engines/prompt_artifact_cache.py
agentic_core/L2_execution/coordination/lease_coordinator.py
agentic_core/L3_orchestration/engines/orchestration_plan_cache.py
agentic_core/L5_safety/enforcement/safety_eval_cache.py
agentic_core/L4_state/memory/blob_storage_provider.py
agentic_core/L4_state/caching/redis_mcp_client.py
agentic_core/L4_state/memory/sovereign_semantic_cache.py
agentic_core/L4_state/reasoning/CachedStateLedger.py
agentic_core/L4_state/memory/semantic_cache_manager.py
tests/architecture/test_redis_cache_non_authoritative.py

## Architecture Invariant Tests (Initial Run)

$ python -m pytest tests/architecture/test_redis_cache_wiring_invariants.py -q --color=no
28 passed in 0.24s

## Non-Happy-Path Tests (Gap Discovery)

$ python -m pytest tests/architecture/test_redis_cache_wiring_invariants.py::test_orch_plan_cache_replay_mode_does_not_write_to_cache -q --color=no --tb=short
FAILED tests/architecture/test_redis_cache_wiring_invariants.py::test_orch_plan_cache_replay_mode_does_not_write_to_cache
AssertionError: Expected set_json to not have been called. Called 1 times.

EXIT CODE: 1

## Gap Remediation

Gap found: L1 CompiledPromptCache, L1 TemplateRenderCache, and L3 OrchestrationPlanCache were writing to cache during replay mode, violating replay determinism contract.

Fixed by adding `if not replay_mode:` guards around both `self.get()` and `self.set()` calls in all three `get_or_fetch()` implementations.

## Architecture Invariant Tests (Final Run)

$ python -m pytest tests/architecture/test_redis_cache_wiring_invariants.py -q --color=no
44 passed in 0.13s

## Full Test Suite

$ python -m pytest -q --color=no --tb=line
8 failed, 6725 passed, 83 skipped, 7 xfailed, 623 warnings in 100.59s

Pre-existing failures (unrelated to this work):
- 5 semantic_cache_activation tests (expect no Redis, local Redis running)
- 3 shadow_embedder_w4b tests (dimension mismatch)

## Summary

**G1 — Seam Wiring**: Added `get_or_fetch()` to 6 seam classes (L0: RouteDecisionCache, RoutingRuleSurfaceCache, CapabilityRegistryCache; L1: CompiledPromptCache, TemplateRenderCache; L3: OrchestrationPlanCache; L5: SafetyEvalCache). All implementations skip cache entirely when `replay_mode=True`.

**G2 — Shadow Tombstones**: Tombstoned SovereignRedisMCPClient, RedisDistributedLock, RedisHotCache, HotBrainCache. Removed re-exports from L4_state/caching/__init__.py. Moved top-level `import redis` in CachedStateLedger.py into guarded __init__ try block. Redirected sovereign_semantic_cache.py to canonical get_hot_cache().

**G3 — Hash Validation**: Restored SHA-256 strictness in _require_hash_segment with REDIS_CACHE_STRICT_HASH_VALIDATION=0 escape hatch for tests.

**G4 — Invariant Tests**: Created tests/architecture/test_redis_cache_wiring_invariants.py with 44 tests covering:
- Seam wiring contract (get_or_fetch presence and behavior)
- No module-level Redis imports in L4
- Tombstone enforcement (all arg patterns)
- Hash validation strictness (uppercase, mixed case, non-hex, boundary lengths)
- Error handling (exception propagation, non-callable fetch, cache failures)
- Replay mode write verification

**Gap discovered via non-happy-path tests**: L1/L3 `get_or_fetch()` were writing to cache during replay mode. Fixed by adding replay mode guards.

**Test coverage**: 44/44 architecture invariant tests passing. Full suite: 6725 passed, 8 pre-existing failures unrelated to this work.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

