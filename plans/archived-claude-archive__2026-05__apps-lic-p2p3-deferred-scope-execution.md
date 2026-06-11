---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-lic-p2p3-deferred-scope-execution.md'
original_relative_path: '_archive\\2026-05\\apps-lic-p2p3-deferred-scope-execution.md'
source_sha256: add88105988df8a878cffb120da7090ff776020e0c3391bc11ff518e0ba62691
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_lic P2/P3 Deferred Scope Execution Plan

> **Status**: `Not Started` in Notion (created 2026-05-05)
> **Unblocked by**: [apps-lic-infra-prerequisites-unblock-p2p3](https://www.notion.so/apps-lic-infra-prerequisites-unblock-p2p3-35727693f55c81e5b930fbde92aad535) — W1-W6 COMPLETE
> **Notion Page**: [apps-lic-p2p3-deferred-scope-execution](https://www.notion.so/apps-lic-p2p3-deferred-scope-execution-35727693f55c81a9be6af8fffbf989d4)

---

## 1. Executive Summary

This plan executes the deferred P2/P3 scope for apps_lic that was blocked pending infrastructure completion. All 5 infrastructure blockers have been resolved:

| Blocker | Status | Infrastructure Delivered |
|---------|--------|--------------------------|
| #1 L4 Touch State Persistence | ✅ | `apps_lic_touch_state.sql`, `TouchStateUWGAdapter`, registration |
| #2 Coordination Fabric Scheduled Wake | ✅ | `TouchScheduler`, `WakeHandler`, cadence calculator |
| #3 L5 HITL Re-engagement Policy | ✅ | `ReengagementHITLPolicy` with 6 rules, evaluator, escalation |
| #4 C0 FEC Binding (Research Bridge) | ✅ | `produce_fec()` with forward-compat for C0 retrieval |
| #5 Cross-Touch Identity Propagation | ✅ | `IdentityPropagationService`, `ContextCarryForwardBridge` |

**Execution is now unblocked.**

---

## 2. Goals

### Primary Goal
Execute all deferred P2/P3 scope items to enable full apps_lic multi-touch functionality.

### Secondary Goals
- Verify all infrastructure components integrate correctly
- Complete E2E test coverage
- Execute migration scripts for existing campaigns
- Enable research bridge integration

---

## 3. Non-Goals

- Infrastructure development (W1-W6 complete)
- New blockers or scope expansion
- Breaking changes to existing functionality
- Production deployment (separate release plan)

---

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W1 | P1-P3 | P2 Integration Completion | ~3k | ⏳ Not Started | P2 features active, tests pass |
| W2 | P1-P4 | P3 Multi-Touch Sequences | ~5k | ⏳ Not Started | 3+ touch sequences working |
| W3 | P1-P3 | Resurfacing Logic | ~4k | ⏳ Not Started | Signal-based wake triggers active |
| W4 | P1-P2 | Research Bridge Integration | ~3k | ⏳ Not Started | C0 retrieval → apps_lic flow working |
| W5 | P1-P3 | Migration Execution | ~2k | ⏳ Not Started | Existing campaigns migrated |
| W6 | P1-P2 | E2E Verification | ~1k | ⏳ Not Started | 100% test coverage, all green |

---

## 5. Phase-Level Summary

### W1: P2 Integration Completion

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | P2 Context Slot Integration | `apps_lic/prompt_assembly/` | Slot binding, validation | ~1k | ⏳ |
| W1.P2 | P2 Eval Rubric Dimensions | `apps_lic/config/domain_contract/` | Dimension scoring, thresholds | ~1k | ⏳ |
| W1.P3 | P2 Feature Activation | Spine wiring | Feature flags, activation | ~1k | ⏳ |

### W2: P3 Multi-Touch Sequences

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W2.P1 | 3-Touch Sequence Definition | `apps_lic/sequences/` | Cadence rules, content variation | ~1.5k | ⏳ |
| W2.P2 | Touch N → N+1 Propagation | `apps_lic/coordination/` | Context carry-forward | ~1.5k | ⏳ |
| W2.P3 | Sequence State Machine | `apps_lic/state/` | State transitions, timeouts | ~1k | ⏳ |
| W2.P4 | Sequence Testing | `tests/integration/apps_lic/` | Full sequence E2E | ~1k | ⏳ |

### W3: Resurfacing Logic

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W3.P1 | Signal Detection Integration | `apps_lic/signals/` | Hiring, funding, competitive signals | ~1.5k | ⏳ |
| W3.P2 | Trigger → Wake Mapping | `apps_lic/coordination/` | Signal confidence, cadence boost | ~1.5k | ⏳ |
| W3.P3 | Resurfacing Test Suite | `tests/` | Signal simulation, wake verification | ~1k | ⏳ |

### W4: Research Bridge Integration

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W4.P1 | apps_research → apps_lic Flow | `apps_research/`, `apps_lic/` | Snippet routing, context assembly | ~1.5k | ⏳ |
| W4.P2 | C0 Retrieval Wiring | `agentic_core/L1_cognition/` | C0 → FEC producer integration | ~1.5k | ⏳ |

### W5: Migration Execution

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W5.P1 | Existing Campaign Inventory | `apps_lic/migrations/` | Data audit, compatibility check | ~500 | ⏳ |
| W5.P2 | Migration Script Execution | `apps_lic/migrations/` | Dry-run, execute, verify | ~1k | ⏳ |
| W5.P3 | Rollback Procedures | `docs/runbooks/` | Recovery, validation | ~500 | ⏳ |

### W6: E2E Verification

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W6.P1 | Full Pipeline E2E Tests | `tests/e2e/apps_lic/` | Complete flow validation | ~500 | ⏳ |
| W6.P2 | Performance & Load Testing | `tests/performance/` | Scale validation, latency | ~500 | ⏳ |

---

## 6. Gap Register

| ID | Gap | Impact | Owner | Resolution Target |
|----|-----|--------|-------|-------------------|
| G1 | C0 retrieval sources not yet populated | FEC stays template-only | C0 team | W4 completion |
| G2 | Redis coordination fabric requires production config | Scheduling may fail | Infra team | W5 completion |
| G3 | Identity service L4 storage needs schema migration | Context loss on restart | L4 team | W5 completion |

---

## 7. Dependencies & Blockers

### External Dependencies
- C0 retrieval service availability (for W4)
- Redis production configuration (for W2-W3)
- HITL approval workflow configuration (for W1-W2)

### Internal Dependencies
- W1 must complete before W2 (P2 features enable P3 sequences)
- W5 migration depends on W2-W4 being stable
- W6 verification depends on all prior waves

---

## 8. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| C0 retrieval delays | Medium | High | Template-only path is functional fallback |
| Migration data loss | Low | Critical | Full backup, dry-run, rollback procedures |
| Performance degradation | Medium | Medium | Load testing in W6, feature flags for rollback |

---

## 9. Success Criteria

### Functional
- [ ] All P2 integration features active and tested
- [ ] 3+ touch sequences execute end-to-end
- [ ] Resurfacing triggers fire on signal detection
- [ ] Research bridge flows C0 retrieval → apps_lic
- [ ] Existing campaigns migrated without data loss

### Quality
- [ ] 100% test coverage for new code
- [ ] All E2E tests passing
- [ ] Performance within 10% of baseline
- [ ] Zero critical or high security findings

### Operational
- [ ] Migration runbook documented
- [ ] Rollback procedures tested
- [ ] Monitoring dashboards active
- [ ] On-call runbook updated

---

## 10. Key Files (Infrastructure - W1-W6)

### Created
- `agentic_core/L4_state/schemas/apps_lic_touch_state.sql`
- `agentic_core/L4_state/uwg/touch_state_writer.py`
- `apps_lic/state/touch_state_registration.py`
- `apps_lic/coordination/touch_scheduler.py`
- `apps_lic/coordination/wake_handler.py`
- `apps_lic/coordination/touch_state_integration.py`
- `agentic_core/L5_safety/policy/apps_lic_reengagement.py`
- `agentic_core/L5_safety/evaluators/apps_lic_reengagement.py`
- `apps_lic/coordination/hitl_escalation.py`
- `apps_lic/cert/fec_producer.py`
- `apps_lic/identity/propagation.py`
- `apps_lic/identity/carry_forward.py`
- `apps_lic/identity/integration.py`
- `apps_lic/migrations/w6_migration.py`
- `apps_lic/spine_wiring.py`
- `tests/integration/apps_lic/test_w6_e2e.py`

### Modified
- `apps_lic/__main__.py` (FEC integration)
- `apps_lic/cert/__init__.py` (side-effect registration)

---

## 11. Related Plans

- **Parent Plan**: [apps-lic-p2p3-deferred-scope-collection](https://www.notion.so/apps-lic-p2p3-deferred-scope-collection-35527693f55c81d8b8f5c0fd77e597e3) (Status: `Waiting` → will transition to `In Progress` when this plan executes)
- **Infrastructure Plan**: [apps-lic-infra-prerequisites-unblock-p2p3](https://www.notion.so/apps-lic-infra-prerequisites-unblock-p2p3-35727693f55c81e5b930fbde92aad535) (Status: `Completed`)

---

## 12. Appendix: Infrastructure Verification

Run spine wiring verification:
```bash
python apps_lic/spine_wiring.py --initialize
```

Run migration dry-run:
```bash
python apps_lic/migrations/w6_migration.py --dry-run
```

Run E2E tests:
```bash
pytest tests/integration/apps_lic/test_w6_e2e.py -v
```
