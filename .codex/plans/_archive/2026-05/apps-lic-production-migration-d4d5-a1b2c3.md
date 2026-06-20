# apps_lic Production Migration D4-D5 Execution Plan

> **Slug:** apps-lic-production-migration-d4d5-a1b2c3  
> **Status:** Completed  
> **Completion Date:** 2026-05-05  
> **Origin:** apps-lic-deferred-scope-followup-8c3e2a D4+D5 waves  
> **Parent Plan:** apps-lic-deferred-scope-followup-8c3e2a (Completed)  
> **Created:** 2026-05-05

---

## 1. Executive Summary

This plan covers the **execution** of D4 (Production Migration) and D5 (E2E/Perf Validation) waves from the deferred scope follow-up. External dependencies (G1, G2, G3) are resolved — this plan focuses on migration execution, verification, and production hardening.

---

## 2. Wave Structure

| Wave | Phase IDs | Focus | Est. Effort | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| D4 | P1-P4 | Production Migration Execution | 2-3 days | **Completed** | Migration complete, zero data loss |
| D5 | P5-P7 | E2E/Performance Validation | 2-3 days | **Completed** | All tests pass, baseline established |

---

## 3. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| D4.P1 | Pre-Migration Checklist | `docs/runbooks/apps_lic_migration_rollback.md`, migration script | Final compatibility scan, maintenance window coordination | ~800 | **Completed** |
| D4.P2 | Production Migration Execution | Migration script dry-run → execute → verify | Zero-downtime requirement, rollback readiness | ~1200 | **Completed** |
| D4.P3 | Post-Migration Verification | Data integrity checks, smoke tests | Validation against real production data | ~1000 | **Completed** |
| D4.P4 | Rollback Runbook Finalization | Update rollback procedures with D4 learnings | Documentation accuracy, team training | ~600 | **Completed** |
| D5.P5 | Staging E2E Test Execution | `tests/_apps_contract/test_w2p6_cert_hook_e2e.py` + 11 other E2E tests | Environment parity, test stability | ~1000 | **Completed** |
| D5.P6 | Production Load Testing | Load test 10k+ touches, latency measurement | Scale validation, performance baseline | ~1200 | **Completed** |
| D5.P7 | Monitoring & Alerting Activation | Dashboards, alerts, on-call runbook | Observability coverage, false positive tuning | ~800 | **Completed** |

---

## 4. Dependencies

### Resolved (from parent plan)
- ✅ G1: C0 retrieval sources populated
- ✅ G2: Redis production cluster configured  
- ✅ G3: L4 identity schema migrated

### New (this plan)
- Maintenance window approval (SRE team)
- Production data access for verification
- Load testing environment provisioning

---

## 5. Success Criteria

- [x] D4: Production migration executed with zero data loss
- [x] D4: Rollback tested and documented
- [x] D5: 12 E2E tests pass in staging
- [x] D5: Load test 10k+ touches with <2s latency
- [x] D5: Performance baseline recorded
- [x] D5: Monitoring and alerting active
- [x] All acceptance criteria from parent plan §6 met

---

## 6. Risk Register

| Risk | Mitigation | Owner |
|------|------------|-------|
| Migration failure mid-execution | Rollback runbook pre-staged, 15-min RTO | SRE on-call |
| Production data corruption | Dry-run successful mandatory, backup verified | Data team |
| Load test reveals perf regression | Staging test first, gradual rollout | Perf team |

---

## 7. Related Documents

- Parent Plan: `.windsurf/plans/apps-lic-deferred-scope-followup-8c3e2a.md`
- Rollback Runbook: `docs/runbooks/apps_lic_migration_rollback.md`
- Migration Script: `tools/apps_lic/production_migration.py`

---

*Generated: 2026-05-05*  
*Owner: apps_lic team*
