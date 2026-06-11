---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-qna-spine-deferred-e9c5b3.md'
original_relative_path: '_archive\\2026-05\\apps-qna-spine-deferred-e9c5b3.md'
source_sha256: aedd2971bbae86c4b45c2992176c5d28de02afd6268a2f542df5a9c30154a179
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-qna-spine-deferred-e9c5b3
plan_type: deferred_scope
parent_plan: apps-qna-spine-integration-e9c5b3
---

# apps_qna Spine Integration — Deferred Scope

Deferred scope items from the completed `apps-qna-spine-integration-e9c5b3` plan (5 waves, 86 tests). These items were explicitly scoped out and should be addressed in future work.

**Parent Plan**: `.windsurf/plans/apps-qna-spine-integration-e9c5b3.md` (Completed)  
**Created**: 2026-05-05

---

## Wave Structure

| Wave | Focus | Est. Tokens | Status |
|------|-------|-------------|--------|
| D1 | C0 retrieval implementation + real LLM-judge | ~40K | ✅ DONE |
| D2 | UWG/L4 durable write + canonical Prompt Assembly | ~35K | ✅ DONE |
| D3 | Production readiness: log mining, holdout, rubric migration | ~30K | ✅ DONE |
| D4 | Cross-app alignment + SSOT consolidation | ~25K | ✅ DONE |

---

## Deferred Items

### D1: C0 Retrieval + Real LLM-Judge (~40K)

**D1.1: Canonical C0 retrieval implementation**
- Current: `c0_adapter.py` returns stub `FinalEvidenceContract`
- Needed: Call canonical `agentic_core` C0 retrieval endpoint
- Impact: Enables real evidence-backed card rendering
- Files: `c0_adapter.py`, `agentic_core` C0 integration

**D1.2: Real LLM-judge implementations**
- Current: Stub judges only
- Needed: Production-grade LLM judges for card quality evaluation
- Impact: Enables automated quality scoring
- Files: `apps_qna/engines/judges/`

### D2: UWG/L4 + Canonical Prompt Assembly (~35K)

**D2.1: UWG/L4 durable write path**
- Current: Local filesystem output only (`reports/qna/<slug>/`)
- Needed: Optional UWG/L4 durable write for committed state
- Impact: Enables persistent, auditable pack storage
- Files: `exit_wiring.py`, UWG integration

**D2.2: Canonical Prompt Assembly integration**
- Current: Domain card context assembly only (not canonical PA)
- Needed: Integration with canonical Prompt Assembly for model execution
- Impact: Enables model-level prompt construction
- Files: `card_context/`, canonical PA adapter

### D3: Production Readiness (~30K)

**D3.1: Production-log mining with PII redaction**
- Current: Not implemented
- Needed: Log analysis pipeline with PII protection
- Impact: Enables production monitoring and debugging

**D3.2: Holdout vs dev eval-set separation**
- Current: Not separated
- Needed: Proper train/dev/holdout split for evaluation
- Impact: Prevents data leakage in evaluation

**D3.3: Per-app rubric migrations**
- Current: Legacy rubric types
- Needed: Migration to new grader types
- Impact: Standardized evaluation across apps

### D4: Cross-App + SSOT (~25K)

**D4.1: SSOT consolidation of legacy YAMLs**
- Current: Multiple YAML configs across apps
- Needed: Consolidated, canonical configuration
- Impact: Reduced config drift

**D4.2: Provider SDK integration**
- Current: apps_qna does not call providers
- Needed: Optional provider SDK for model execution
- Impact: Enables direct model calls when needed

**D4.3: Cross-app alignment**
- Current: apps_rg, apps_lic, apps_research have own plans
- Needed: Aligned spine patterns across all apps
- Impact: Consistent architecture

---

## Success Criteria

- [ ] C0 adapter calls real canonical C0 (not stub)
- [ ] LLM judges produce real quality scores
- [ ] UWG/L4 write path available (optional, not default)
- [ ] Canonical Prompt Assembly integrated
- [ ] Production logging with PII redaction
- [ ] Holdout separation implemented
- [ ] Rubric migrations complete
- [ ] Legacy YAMLs consolidated
- [ ] Provider SDK integration (optional)

---

PLAN_CREATED: slug=apps-qna-spine-deferred-e9c5b3 path=.windsurf/plans/apps-qna-spine-deferred-e9c5b3.md waves=4 phases=9 tokens=130K
