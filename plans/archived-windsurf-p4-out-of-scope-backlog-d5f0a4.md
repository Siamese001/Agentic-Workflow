---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\p4-out-of-scope-backlog-d5f0a4.md'
original_relative_path: 'p4-out-of-scope-backlog-d5f0a4.md'
source_sha256: e7bfc12f66cb1c0ed01d4198ba296b731ca90c63e9f267fc9dfc9d1a90d2d01e
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-07'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# P4 — Out-of-Scope Items Backlog

> Parent: deferred-scope-spine-refinement-5e3d1b
> Status: Captured, not implemented. Each item needs its own plan + ADR.

---

## Items (from parent plan's Out Of Scope section)

### 1. Changing the routing logic of X1–X3 gates
- Diagram labels were added (W1), but no logic changes.
- X1 has 10 sub-gates (X1A–X1J), X2 has 5, X3 has 5 dispositions.
- Any routing change needs blast-radius analysis via ADG.

### 2. Adding new guardrail rules to L5 safety
- L5 currently has policy_hash, blueprint_hash, and replay_key checks.
- New guardrails (e.g., content safety, PII redaction depth, rate limiting)
  need Author-Gate approval per constitutional §8.

### 3. Modifying C0 grounding retrieval strategy
- C0 currently uses fixture-backed retrieval in test mode.
- Production retrieval strategy (Tavily, vector DB, hybrid) needs design.
- Impacts all apps that use C0 (apps_rg, apps_qna, apps_research).

### 4. Retraining or swapping the BGE-M3 embedding model
- Current model: BGE-M3 via sentence-transformers.
- Swapping would require re-indexing all D2 cache entries.
- Retraining would need a labeled dataset of query-result pairs.

### 5. Any change to L6 runtime exhaust or learning ledger schema
- L6 exhaust bundle schema is stable but could be extended.
- Learning ledger (bandit feedback loop) is operational but not optimized.
- Changes here affect the closed-loop router (§29).

### 6. ADR authoring
- No ADRs were authored during the parent plan (observational only).
- At minimum, ADRs should cover: D2 default enable (P1), spine envelope
  pattern (P2/P3), sub-stage telemetry (W2).

### 7. Modifying apps_research internals
- The research_l3_adapter (W5) and spine envelope (P3) wrap the public
  interface only. Internal refactoring of apps_research (e.g., adding
  L0 routing, C0 grounding, Exit eval natively) is deferred.

### 8. Changing apps_lic → apps_research path
- Only apps_rg's path was addressed (W5). apps_lic still uses its own
  AppsResearchBridge pattern. Unifying the two paths would reduce
  duplication but requires apps_lic refactoring.

---

## Recommendation

None of these items block current functionality. They are architectural
improvements that should be prioritized in a future planning cycle.
Each item should get its own plan with ADR before implementation.

The deferred scope plan (`deferred-scope-spine-refinement-5e3d1b`) is now
fully captured: P1/P2/P3 implemented, P4 documented as backlog.
