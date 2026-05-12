---
title: W2 Hook Consolidation — B6B Shadow Mode Unblock
slug: windsurf-governance-w2-deferred-b6b-unblock-a8d4e2
created: 2026-05-12
last_updated: 2026-05-12 16:27 UTC-04
author: Cascade
tier: T3
status: Not Started
dod_exempt: false
---

# W2 Hook Consolidation — B6B Shadow Mode Unblock

> **CURRENT STATUS**: W2 BLOCKED ⛔ on B6B (shadow mode) | Parent plan W5 COMPLETE ✅ | Unblock requires 14+ days shadow data + harness fix

> **DEPENDENCY**: This plan is gated by B6B shadow mode completion. Cannot start until B6A validation harness issues resolved AND 14+ days of production shadow data collected.

## 1. Problem Statement

W2 Hook Consolidation was **intentionally blocked** in parent plan `windsurf-governance-consolidation-a7c3e9` due to unresolved B6B blocker.

**B6A Status**: Integration harness complete but 23/24 hooks failed (harness bugs, not hook bugs). 35 hooks marked SHADOW_REQUIRED.

**B6B Requirement**: Production shadow mode validation for 35 hooks requiring real-world context to verify PASS/FAIL/BYPASS behavior.

**OP-1 Status**: ✅ CLOSED — Loader priority proven via physical reordering in W1B.P3.

## 2. Goals & Success Criteria

### P1: Unblock W2 (Primary)
- [ ] B6B shadow mode completes 14+ days data collection
- [ ] 35 SHADOW_REQUIRED hooks validated in production
- [ ] Golden receipts match for all 35 hooks
- [ ] W2.P0 re-authorized with GO status

### P2: Execute W2 Consolidation
- [ ] 59→~20 hooks consolidated (target: 70% reduction)
- [ ] 29→8 post_cascade hooks (functional consolidation)
- [ ] Zero enforcement loss proven
- [ ] All replacement_for[] mappings valid

### P3: Closeout
- [ ] W2 FINAL closeout receipt
- [ ] No orphaned hooks verified
- [ ] CI gates still pass (43 gates)

## 3. Non-Goals (Out-of-Scope)

1. **NO new hook creation** — consolidation only
2. **NO rule changes** — W3 already complete
3. **NO skill changes** — W4 already complete
4. **NO index automation changes** — W5 already complete
5. **NO constitutional changes** — §0-§36 remain untouched

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Blockers |
|------|-----------|-------|-------------|--------|----------|
| **W0** | P1-P2 | **B6B Shadow Mode Execution** | ~4K | 🔲 NOT STARTED | Requires 14+ days runtime |
| **W0.P1** | P1 | Shadow mode activation | ~2K | 🔲 NOT STARTED | Harness fix required |
| **W0.P2** | P2 | 14-day data collection | ~2K | 🔲 NOT STARTED | Time-gated |
| **W1** | P1-P5 | **W2 Consolidation Re-execution** | ~10K | 🔲 NOT STARTED | W0 completion |
| **W1.P0** | P0 | Readiness re-verification | ~0.5K | 🔲 NOT STARTED | W0.GO required |
| **W1.P1** | P1 | Notion hook consolidation | ~3K | 🔲 NOT STARTED | — |
| **W1.P2** | P2 | Author-Gate hook merge | ~2K | 🔲 NOT STARTED | — |
| **W1.P3** | P3 | Plan lifecycle hook merge | ~2K | 🔲 NOT STARTED | — |
| **W1.P4** | P4 | Resource budget hook merge | ~1.5K | 🔲 NOT STARTED | — |
| **W1.P5** | P5 | MCP hygiene hook merge | ~1.5K | 🔲 NOT STARTED | — |
| **W1.FINAL** | — | W2 closeout | ~1K | 🔲 NOT STARTED | All P1-P5 done |

## 5. Definition of Done

| DoD ID | Criterion | Verification |
|--------|-----------|--------------|
| DoD-1 | B6B shadow mode 14+ days data | `artifacts/b6b/shadow_data_14d.json` |
| DoD-2 | 35 hooks validated | `b6b_validation_manifest.md` |
| DoD-3 | W2.P0 GO status | `w2p0_go_no_go.md` |
| DoD-4 | 59→~20 hooks consolidated | `w2_final_hook_count_report.md` |
| DoD-5 | Zero enforcement loss | `w2_final_no_enforcement_loss_receipt.json` |
| DoD-6 | No orphaned hooks | `w2a_no_orphaned_lookup_receipt.md` |
| DoD-7 | All 43 CI gates pass | `python ops_scripts/ci/run_contract_gates.py` |
| DoD-8 | W2 FINAL receipt | `w2_final_receipt.json` |

## 6. Blocker Register

| Blocker ID | Description | Resolution | Status |
|------------|-------------|------------|--------|
| **B6B** | Shadow mode 14+ days required | Wait + data collection | 🔲 OPEN |
| **B6A-HF** | Harness bug fixes | Repair 23 harness failures | 🔲 OPEN |

## 7. Related Plans & Dependencies

| Plan | Slug | Relation |
|------|------|----------|
| Parent Governance Plan | windsurf-governance-consolidation-a7c3e9 | Deferred from W2 |
| Author-Gate Pipeline | author-gate-pipeline-hardening-d7e3f9 | W1.P2 dependency |

## 8. Verification-vs-Deferral

| Item | Verify Now | Defer | Rationale |
|------|------------|-------|-----------|
| B6B shadow activation | — | ✅ | Requires harness fix first |
| 14-day data collection | — | ✅ | Time-gated, cannot accelerate |
| W2 consolidation logic | ✅ | — | Already proven in W2A-R2 |

## 9. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| B6A harness fix takes >1 week | Medium | High | Parallel track: fix harness while W5 completed |
| Shadow data shows hook bugs | Low | High | Fail-soft receipts already in place |
| 14-day delay pushes to next sprint | High | Low | This plan captures the deferral explicitly |

---

**PLAN_CREATED**: windsurf-governance-w2-deferred-b6b-unblock-a8d4e2  
**STATUS**: Not Started — GATED on B6B  
**PARENT_PLAN**: windsurf-governance-consolidation-a7c3e9 (W5 COMPLETE)  
**UNBLOCK_REQUIRES**: B6B shadow mode (14+ days) + B6A harness fix  
**ESTIMATED_TOKENS**: ~14K  
**TARGET_START**: After B6B data collection complete
