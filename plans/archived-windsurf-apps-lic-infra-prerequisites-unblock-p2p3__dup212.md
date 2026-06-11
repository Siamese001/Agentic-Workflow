---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-lic-infra-prerequisites-unblock-p2p3__dup212.md'
original_relative_path: 'apps-lic-infra-prerequisites-unblock-p2p3__dup212.md'
source_sha256: 342dd669923db8b9b97354e04baa300a119aa9ad9938191b9803bada40de72d0
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_lic Infrastructure Prerequisites Plan

**Plan ID:** apps-lic-infra-prerequisites-unblock-p2p3  
**Parent Plan:** apps-lic-p2p3-deferred-scope-collection (Waiting)  
**Status:** Not Started  
**Created:** 2026-05-05  
**Target:** Unblock P2/P3 deferred scope through infrastructure delivery

---

## 1. Executive Summary

This plan delivers the **infrastructure prerequisites** that block activation of `apps-lic-p2p3-deferred-scope-collection`. The deferred scope plan contains ~24k tokens of P2 integration work and P3 activation work that cannot proceed without foundational infrastructure.

**Infrastructure Gaps to Close:**
1. L4 touch state persistence (apps_lic_touch_state table + UWG integration)
2. Coordination fabric scheduled wake (multi-touch cadence timing)
3. L5 HITL re-engagement policy (resurfacing trigger sensitivity)
4. C0 FEC binding (apps_research → apps_lic competitive signals)
5. Cross-touch identity propagation (recipient tracking)

**Estimated Effort:** ~18k tokens across 6 waves  
**Success Criteria:** All 5 blocker categories resolved, deferred plan transitions Waiting → In Progress

---

## 2. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status |
|------|-----------|-------|-------------|-------------|--------|
| W1 | P1-P3 | L4 Touch State Infrastructure | 3k | UWG stable, no schema migrations needed | 🟡 Not Started |
| W2 | P1-P2 | Coordination Fabric Scheduled Wake | 2k | Redis coordination fabric healthy | 🟡 Not Started |
| W3 | P1-P3 | L5 Re-engagement HITL Policy | 3k | L5 eval spine stable | 🟡 Not Started |
| W4 | P1-P3 | C0 FEC Binding (Research Bridge) | 4k | apps_research spine-aligned | 🟡 Not Started |
| W5 | P1-P2 | Cross-touch Identity Propagation | 3k | Identity propagation contract stable | 🟡 Not Started |
| W6 | P1-P2 | Migration Scripts & E2E Tests | 3k | Prior waves complete | 🟡 Not Started |

---

## 3. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|---------------|-------------|--------|
| W1.P1 | Touch State Schema DDL | `schemas/apps_lic_touch_state.sql` | First app-specific state table pattern | 1k | 🟡 Not Started |
| W1.P2 | UWG Touch State Integration | `agentic_core/L4_state/uwg/touch_state_writer.py` | New write class severity determination | 1k | 🟡 Not Started |
| W1.P3 | Touch State Registration | `apps_lic/state/touch_state_registration.py` | App-domain UWG registration | 1k | 🟡 Not Started |
| W2.P1 | Scheduled Wake Schema | `agentic_core/cache/coordination_fabric_wake.py` | Redis wake key pattern design | 1k | 🟡 Not Started |
| W2.P2 | Wake Integration | `apps_lic/integrations/scheduled_wake_adapter.py` | Coordination fabric adapter | 1k | 🟡 Not Started |
| W3.P1 | Re-engagement Policy Schema | `apps_lic/config/reengagement_policy.yaml` | Policy DSL design | 1k | 🟡 Not Started |
| W3.P2 | L5 HITL Integration | `agentic_core/L5_safety/contracts/reengagement_hitl.py` | L5 eval spine integration | 1k | 🟡 Not Started |
| W3.P3 | Resurfacing Trigger Policy | `apps_lic/policy/resurfacing_trigger_policy.py` | Trigger matcher implementation | 1k | 🟡 Not Started |
| W4.P1 | Competitive Landscape C0 Schema | `apps_research/config/c0_competitive_landscape.yaml` | C0 retrieval profile extension | 1.5k | 🟡 Not Started |
| W4.P2 | Company Briefing Extension | `apps_research/engines/company_brief_engine.py` | Add competitive signals to briefing | 1.5k | 🟡 Not Started |
| W4.P3 | FEC Binding Registration | `apps_lic/cert/fec_research_bridge.py` | FEC producer for research sources | 1k | 🟡 Not Started |
| W5.P1 | Identity Propagation Contract | `apps_shared/contracts/cross_touch_identity.py` | Cross-app identity contract | 1.5k | 🟡 Not Started |
| W5.P2 | Touch State Identity Link | `apps_lic/state/touch_identity_link.py` | Identity → touch state binding | 1.5k | 🟡 Not Started |
| W6.P1 | State Migration Scripts | `tools/migration/apps_lic_touch_state_seed.py` | Migration scaffolding | 1.5k | 🟡 Not Started |
| W6.P2 | E2E Test Harness | `tests/_apps_contract/test_p3_touch_state_e2e.py` | End-to-end verification | 1.5k | 🟡 Not Started |

---

## 4. Wave Details

### W1: L4 Touch State Infrastructure (3k tokens)

**Objective:** Create durable state persistence for multi-touch sequences.

**P1: Touch State Schema DDL**
- Create `agentic_core/L4_state/schemas/apps_lic_touch_state.sql`
- Schema fields: touch_id, recipient_hash, campaign_id, touch_sequence, touch_state, next_scheduled_wake, context_carry_forward, created_at, updated_at
- Index on recipient_hash + campaign_id for fast lookup
- Index on next_scheduled_wake for wake queries

**P2: UWG Touch State Integration**
- Create `agentic_core/L4_state/uwg/touch_state_writer.py`
- Define write class severity for touch state (likely `durable`)
- Implement TouchStateWriteRequest, TouchStateCommitReceipt
- Add touch state to UWG catalog

**P3: Touch State Registration**
- Create `apps_lic/state/touch_state_registration.py`
- Implement `register_touch_state_contract()` for app-domain registration
- Wire into apps_lic spine initialization

**Exit Criteria:**
- [ ] DDL deploys cleanly to SQLite backend
- [ ] UWG integration passes write/read round-trip test
- [ ] Registration succeeds at apps_lic startup

---

### W2: Coordination Fabric Scheduled Wake (2k tokens)

**Objective:** Enable timing/cadence for multi-touch sequences.

**P1: Scheduled Wake Schema**
- Extend `agentic_core/cache/core/redis_coordination_fabric.py`
- Add wake registration: `register_wake(wake_id, wake_at, payload)`
- Add wake polling: `poll_due_wakes(before_time)`
- Add wake cancellation: `cancel_wake(wake_id)`

**P2: Wake Integration**
- Create `apps_lic/integrations/scheduled_wake_adapter.py`
- Implement `schedule_next_touch(touch_state, cadence_policy)`
- Implement `reschedule_touch(touch_id, new_wake_time)`
- Integrate with coordination fabric

**Exit Criteria:**
- [ ] Wake registration persists to Redis
- [ ] Poll returns due wakes correctly
- [ ] Integration test: schedule → poll → process → cancel

---

### W3: L5 Re-engagement HITL Policy (3k tokens)

**Objective:** Define HITL gates for sensitive resurfacing triggers.

**P1: Re-engagement Policy Schema**
- Create `apps_lic/config/reengagement_policy.yaml`
- Define policy levels: `auto`, `review_on_sensitive`, `review_all`
- Define sensitive trigger patterns: competitor_mention, negative_signal, etc.
- Define reviewer routing by trigger type

**P2: L5 HITL Integration**
- Create `agentic_core/L5_safety/contracts/reengagement_hitl.py`
- Implement `ReengagementHitlPolicy` contract
- Wire into L5 eval spine
- Add hitl_policy to apps_lic eval_rubrics

**P3: Resurfacing Trigger Policy**
- Create `apps_lic/policy/resurfacing_trigger_policy.py`
- Implement `should_trigger_resurfacing(signal, history)`
- Implement `classify_trigger_sensitivity(trigger)`
- Return HITL routing decision

**Exit Criteria:**
- [ ] Policy YAML parses and validates
- [ ] L5 integration surfaces HITL decisions
- [ ] Trigger classification returns correct routing

---

### W4: C0 FEC Binding - Research Bridge (4k tokens)

**Objective:** Connect apps_research competitive signals to apps_lic.

**P1: Competitive Landscape C0 Schema**
- Create `apps_research/config/c0_competitive_landscape.yaml`
- Define retrieval profile for competitive signals
- Add to `apps_research/config/domain_contract/retrieval_profiles.yaml`

**P2: Company Briefing Extension**
- Extend `apps_research/engines/company_brief_engine.py`
- Add `competitive_landscape` section to briefing output
- Include: differentiators, source_refs, competitor_mentions, confidence scores
- Ensure source_refs trace to C0 retrieval

**P3: FEC Binding Registration**
- Create `apps_lic/cert/fec_research_bridge.py`
- Implement `produce_research_fec(run_context)`
- Extract competitive signals from briefing
- Return FEC with `grounded=True` when research-sourced
- Register in `apps_lic/cert/__init__.py`

**Exit Criteria:**
- [ ] apps_research briefing includes competitive_landscape
- [ ] Source refs traceable to C0 retrieval
- [ ] apps_lic FEC resolver returns research-sourced evidence
- [ ] P2c engine confidence boost when research-sourced

---

### W5: Cross-touch Identity Propagation (3k tokens)

**Objective:** Enable recipient tracking across touch sequences.

**P1: Identity Propagation Contract**
- Create `apps_shared/contracts/cross_touch_identity.py`
- Define `CrossTouchIdentity` contract
- Fields: identity_hash, touch_sequence_ids, last_touch_at, identity_confidence
- Define propagation rules (consent, retention)

**P2: Touch State Identity Link**
- Create `apps_lic/state/touch_identity_link.py`
- Implement `link_touch_to_identity(touch_id, identity_hash)`
- Implement `get_identity_touch_history(identity_hash)`
- Ensure GDPR-compliant identity handling

**Exit Criteria:**
- [ ] Contract defines clear identity fields
- [ ] Touch state links to identity correctly
- [ ] History retrieval works across touch sequence
- [ ] Consent/retention rules enforced

---

### W6: Migration Scripts & E2E Tests (3k tokens)

**Objective:** Ensure safe rollout and verify end-to-end behavior.

**P1: State Migration Scripts**
- Create `tools/migration/apps_lic_touch_state_seed.py`
- Implement idempotent touch state table creation
- Add rollback script for emergency use
- Document migration procedure

**P2: E2E Test Harness**
- Create `tests/_apps_contract/test_p3_touch_state_e2e.py`
- Test: schedule touch → wake → state advance → reschedule
- Test: trigger detection → HITL routing → decision → resume
- Test: research briefing → FEC resolution → P2c consumption
- Verify no spine violations

**Exit Criteria:**
- [ ] Migration script runs idempotently
- [ ] E2E tests pass (target: 12+ tests)
- [ ] Rollback script tested in staging
- [ ] Documentation complete

---

## 5. Success Criteria

- [ ] **W1:** `apps_lic_touch_state` table operational with UWG integration
- [ ] **W2:** Coordination fabric scheduled wake functional
- [ ] **W3:** L5 re-engagement HITL policy active
- [ ] **W4:** Research bridge (C0 FEC binding) operational
- [ ] **W5:** Cross-touch identity propagation functional
- [ ] **W6:** Migration scripts + E2E tests passing (12+ tests)
- [ ] **Activation Gate:** Parent deferred plan transitions Waiting → In Progress

---

## 6. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| UWG schema migration complexity | Medium | High | Phased rollout with validation gates |
| Coordination fabric wake reliability | Medium | High | Redundant wake polling + dead letter queue |
| L5 policy performance overhead | Low | Medium | Async HITL classification |
| apps_research briefing API change | Medium | High | Versioned contract with backward compatibility |
| Identity propagation GDPR issues | Low | High | Privacy-by-design review at W5.P1 |

---

## 7. Non-Goals

- Template governance approval (external process, not infrastructure)
- LLM judge prompt authoring (content creation, not infrastructure)
- Real Spearman-calibrated judges (deferred to future eval work)
- Production holdout dataset separation (eval harness deferred scope)
- PII-redacted production-log mining (observability deferred scope)

---

## 8. Related Plans

| Plan | Relationship | Current Status |
|------|--------------|----------------|
| apps-lic-p2p3-deferred-scope-collection | **Parent to unblock** | Waiting |
| apps-lic-p3-multi-touch-resurfacing-readiness | Child (Notion: 35727693-f55c-81ff-ab29-df287dc5945a) | Waiting |
| apps-lic-signal-enhancements-p2p3-spine-aligned | Ancestor | Completed |

---

## 9. Dependencies

**Inbound (must be ready before this plan starts):**
- UWG infrastructure operational (confirmed: `agentic_core/L4_state/uwg/` exists)
- Coordination fabric healthy (confirmed: `redis_coordination_fabric.py` exists)
- L5 eval spine stable (confirmed: `agentic_core/L5_safety/eval_spine/` exists)
- apps_research spine-aligned (confirmed: `apps_research/` with spine integration)

**Outbound (this plan must complete before):**
- apps-lic-p2p3-deferred-scope-collection activation
- P2.1 Prompt template P2 slots
- P2.2 Exit rubric dimensions
- P3a Multi-touch cadence
- P3b Resurfacing triggers

---

**Plan Status:** `Not Started` — Ready to begin Wave 1 when prioritized

**Next Action:** W1.P1 — Create touch state schema DDL
