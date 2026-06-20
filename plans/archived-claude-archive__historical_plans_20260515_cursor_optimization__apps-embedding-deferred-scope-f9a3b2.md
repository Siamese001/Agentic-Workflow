---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-embedding-deferred-scope-f9a3b2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-embedding-deferred-scope-f9a3b2.md'
source_sha256: c54703c434cdd6e1622f7657b5b701ea87d7623366cc61d3f29d17d9ff1bf4a9
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
description: Deferred scope from apps-embedding-gap-analysis-8f7d2e - manual reviews and non-critical remediation
tags: [deferred-scope, embedding, chromadb, gap-analysis, P1, P2]
status: Not Started
created: 2026-05-10
dependent_on: apps-embedding-gap-analysis-8f7d2e
---

# Apps Embedding Gap Analysis — Deferred Scope Plan

**Source Plan:** apps-embedding-gap-analysis-8f7d2e  
**Created:** 2026-05-10  
**Status:** Not Started  
**Priority:** P1/P2 (post-critical remediation)

---

## Deferred Scope Summary

This plan captures all **non-P0 deferred work** from the completed `apps-embedding-gap-analysis-8f7d2e`. These items were classified as P1 or P2 because they:
- Need deeper manual investigation
- Are not runtime-critical
- Can be addressed after the P0 ChromaDB initialization

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| D-W1 | D-P1.1-D-P1.6 | Manual review of 6 UNKNOWN apps | ~8,000 | Not Started | Each app has embedding requirements documented |
| D-W2 | D-P2.1-D-P2.4 | P1 remediation (post-P0) | ~12,000 | Not Started | 3 P1 gaps closed |
| D-W3 | D-P3.1-D-P3.3 | P2 cleanup and hardening | ~6,000 | Not Started | All P2 gaps addressed |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| D-P1.1 | apps_rfp embedding review | apps_rfp/engines/, config/ | Proposal retrieval may need semantic search | ~1,500 | Not Started |
| D-P1.2 | apps_underwriting_ai review | apps_underwriting_ai/engines/ | Underwriting may use structured data only | ~1,500 | Not Started |
| D-P1.3 | apps_lic embedding review | apps_lic/types/, L1_cognition/ | Vector memory types defined but unused | ~1,500 | Not Started |
| D-P1.4 | apps_exec embedding review | apps_exec/ | Minimal skeleton, likely no embeddings | ~1,000 | Not Started |
| D-P1.5 | apps_repo_brief review | apps_repo_brief/L2/, c0/ | May use code analysis not semantic | ~1,500 | Not Started |
| D-P1.6 | apps_architect review | apps_architect/cli/, L6/ | CLI-focused, likely no embeddings | ~1,000 | Not Started |
| D-P2.1 | Migrate C0 to ChromaDB | apps_qna/c0_adapter.py, L4_state/ | Move from flat JSON to governed ChromaDB | ~4,000 | Not Started |
| D-P2.2 | Real embeddings for research | apps_research/engines/ | Replace mock with BGE-M3 | ~4,000 | Not Started |
| D-P2.3 | Add embedding refs to contracts | agentic_core/runtime/contracts/ | Add query_vec_ref, fact_vec_ref fields | ~3,000 | Not Started |
| D-P2.4 | R1B schema completion | agentic_core/runtime/prove_requirements/ | Add cache embedding refs to R1B | ~1,000 | Not Started |
| D-P3.1 | Refresh healing_contexts | system_learning/config/, adapters/ | Re-ingest 2-month-old index | ~2,000 | Not Started |
| D-P3.2 | Persist L1 classification cache | apps_qna/integrations/, L4_state/ | Convert in-memory to ChromaDB | ~2,000 | Not Started |
| D-P3.3 | Contract metadata gaps | agentic_core/L4_state/contracts/ | Add dimension validation to VectorCacheLayout | ~2,000 | Not Started |

---

## Gap Register (from Source Plan)

### UNKNOWN_NEEDS_MANUAL_REVIEW (6 apps)

| App | Current Evidence | Deferred Investigation |
|-----|------------------|------------------------|
| apps_rfp | grep found no embedding matches | Inspect proposal_retrieval_engine.py for semantic search needs |
| apps_underwriting_ai | No embedding code found | Check if underwriting uses structured data or needs retrieval |
| apps_lic | lic_vector_memory_types.py exists | Determine if vector types are planned but not implemented |
| apps_exec | Minimal skeleton | Confirm no embedding requirements expected |
| apps_repo_brief | No embedding evidence | Verify code analysis vs semantic retrieval approach |
| apps_architect | CLI tooling focus | Confirm no semantic retrieval needs |

### P1 Gaps (Deferred until P0 Complete)

| Gap | Severity | Deferred Rationale |
|-----|----------|-------------------|
| apps_qna C0 outside canonical path | P1 | Works functionally; migrate after P0 ChromaDB ready |
| apps_research mock embeddings | P1 | Non-critical path; implement real BGE-M3 after core fix |
| FinalEvidenceContract missing embedding refs | P1 | Contract enhancement; not blocking current runtime |
| R1B schema missing cache refs | P1 | Certification schema; enhance after core functionality |

### P2 Gaps (Cleanup/Hardening)

| Gap | Severity | Deferred Rationale |
|-----|----------|-------------------|
| healing_contexts stale (2mo) | P2 | system_learning pipeline; not production-critical |
| L1 in-memory only | P2 | Process restart cost acceptable; persist later |
| SealedL2Artifact opaque evidence | P2 | Observability gap; enhance contracts later |
| ExitReviewPacket missing cache fields | P2 | Validation gap; add after cache working |

---

## Definition of Done

### D-W1: Manual App Reviews
- [ ] D-DoD-1: Each of 6 UNKNOWN apps has determined embedding requirements
- [ ] D-DoD-2: Requirements documented in apps_embedding_requirements_from_adg_v2.json
- [ ] D-DoD-3: New gaps classified (PRESENT/MISSING/NOT_APPLICABLE)

### D-W2: P1 Remediation
- [ ] D-DoD-4: apps_qna C0 index migrated to ChromaDB canonical path
- [ ] D-DoD-5: apps_research uses real BGE-M3 embeddings (not mock)
- [ ] D-DoD-6: FinalEvidenceContract has query_vec_ref and fact_vec_ref fields
- [ ] D-DoD-7: R1B schema has request_intent_embedding_ref and cache_embedding_ref

### D-W3: P2 Cleanup
- [ ] D-DoD-8: healing_contexts index refreshed with current BGE-M3
- [ ] D-DoD-9: L1 topic classification cache persisted to ChromaDB
- [ ] D-DoD-10: VectorCacheLayout validates BGE-M3 dimension (1024)

---

## Dependencies

**Hard Dependency:**
- apps-embedding-gap-analysis-8f7d2e must be Completed (P0 gap identified)
- P0 remediation (ChromaDB initialization for apps_qna L4) should be Complete

**Soft Dependencies:**
- BGE-M3 embedder available in agentic_core.embeddings.bge_runtime
- ChromaDB persistent client functional at canonical paths

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Manual review finds new P0 gaps | Medium | High | Weekly check-ins; escalate if found |
| P0 fix changes architecture | Low | Medium | Re-assess this plan if P0 pivots |
| 6 UNKNOWN apps all need embeddings | Low | High | Scope D-W1 tightly; time-box reviews |

---

## Success Criteria (Overall)

1. All 6 UNKNOWN apps have documented embedding requirements
2. No remaining UNKNOWN classifications in gap matrix
3. 4 P1 gaps closed
4. 4 P2 gaps addressed
5. All changes follow ChromaDB canonical path governance
6. Contracts have explicit embedding vector reference fields

---

## Execution Commands

```bash
# D-W1: Manual reviews
python tools/apps_proof/generate_compact_app_contracts.py --app apps_rfp
python tools/apps_proof/generate_compact_app_contracts.py --app apps_underwriting_ai
# ... etc for each UNKNOWN app

# D-W2: P1 remediation
python tools/adg/migrate_flat_index_to_chromadb.py \
  --source C:/AgenticEmbeddings/indexes/apps_qna_interview_cards \
  --target data/cache/chromadb/apps_qna_interview_cards

# D-W3: P2 cleanup
python tools/indexing/refresh_healing_contexts.py --force
```

---

## Rollback Strategy

- Flat JSON indexes preserved as backup during migration
- In-memory caches remain functional if ChromaDB migration fails
- Contract changes are additive (new fields optional)

---

## Notes

**DO NOT IMPLEMENT NOW** — This plan is for post-critical remediation.

Start this plan only after:
1. P0: apps_qna L4 ChromaDB cache is initialized and functional
2. Core team confirms P0 is stable

AG_QUEUE_SEED: plan=apps-embedding-deferred-scope-f9a3b2 id=deferred-scope-start depends_on=apps-embedding-gap-analysis-8f7d2e title="Begin deferred scope after P0 completion"
