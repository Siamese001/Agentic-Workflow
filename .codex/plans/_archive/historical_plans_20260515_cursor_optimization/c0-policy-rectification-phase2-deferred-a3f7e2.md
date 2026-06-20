# C0 Policy Rectification — Phase 2 (Deferred Scope)

> **Parent Plan**: `c0-policy-rectification-deferred-f7b2a9` (COMPLETED W1-W5)
> **This Plan**: Deferred items from parent plan §16 "Uncertainty Areas"
> **Status**: Not Started
> **Slug**: `c0-policy-rectification-phase2-deferred-a3f7e2`

## 1. Executive Summary

This plan captures the **deferred scope** from the completed C0 Policy Rectification
parent plan. While W1-W5 delivered the core C0 policy architecture, three significant
work items were intentionally deferred to a future phase:

1. **DS-5**: Eager migration strategy and tooling (not just lazy migration)
2. **DS-6**: PA4 and PA7 stages C0 policy awareness (only PA0 was updated)
3. **DS-7**: Production monitoring dashboard and alerting

These items represent **production hardening** and **observability completeness**
rather than core functionality. They should be implemented after the parent plan
has been stable in production for 30+ days.

## 2. Deferred Scope Items

### DS-5: Backward Compatibility / Migration Strategy (Full Implementation)

**Parent Plan Reference**: Section 16 "Uncertainty Areas"

**Description**:  
Existing `RouteContract` instances without `c0_policy` field need a **decided and
implemented** migration strategy. Parent plan implemented only lazy migration
(derive from legacy fields). This deferred scope completes the strategy.

**Options to Decide**:
1. ✅ **Lazy migration** (DONE in parent): Code checks for `None` and derives from legacy
2. 🔄 **Eager migration** (THIS PLAN): Background job rewrites existing contracts
3. 🔄 **Hard cutoff** (THIS PLAN): Require c0_policy after flag date with enforcement

**Work Required**:
- [ ] Decide on final migration strategy (lazy vs eager vs hard cutoff)
- [ ] If eager: Implement background migration job with progress tracking
- [ ] If hard cutoff: Add runtime enforcement gate with `C0_POLICY_REQUIRED_AFTER` date
- [ ] Set deprecation timeline with LTS (long-term support) commitment
- [ ] Document breaking changes in CHANGELOG
- [ ] Add CI gate to prevent new code without c0_policy

**Files to Create/Modify**:
- `tools/c0_migration/background_contract_updater.py` (eager migration job)
- `ops_scripts/ci/check_c0_policy_required.py` (hard cutoff gate)
- `docs/operations/C0_POLICY_MIGRATION.md` (update with final strategy)

---

### DS-6: Additional PA Stages (PA4, PA7) C0 Policy Enforcement

**Parent Plan Reference**: Section 7 "Fix Prompt Assembly boundary"

**Description**:  
Parent plan updated `pa0_boundary.py` (CHECK 0.4) to use frozen `RouteContract.c0_policy`.
Other PA stages (PA4 validation, PA7 dispatch) may need similar C0 policy awareness
for consistency and completeness.

**Files to Review and Potentially Update**:
- `agentic_core/prompt_governance/prompt_assembly/pa4_validation.py`
  - CHECK 4.x series for C0-related validation
  - Add c0_policy awareness if checking evidence contracts
- `agentic_core/prompt_governance/prompt_assembly/pa7_dispatch_states.py`
  - CHECK 7.x series for dispatch-time C0 validation
  - Ensure consistency with PA0 enforcement
- `agentic_core/prompt_governance/orchestrator.py`
  - Orchestrator-level C0 policy propagation

**Work Required**:
- [ ] Audit PA4 for C0-related validation logic
- [ ] Audit PA7 for C0-related dispatch logic
- [ ] Add c0_policy parameter to relevant functions (similar to PA0)
- [ ] Add OTEL span emission for PA4/PA7 C0 checks
- [ ] Add tests for PA4/PA7 C0 policy handling
- [ ] Ensure error messages reference C0 policy consistently

**Non-Goals**:
- Do NOT add new C0 modes (use existing C0Mode enum)
- Do NOT change RouteContract structure
- Do NOT modify C0 internals (retrieval, storage)

---

### DS-7: Production Rollout Monitoring

**Parent Plan Reference**: N/A - operational concern

**Description**:  
Operational monitoring for C0 policy enforcement in production. This is
**observability completeness** to ensure the C0 policy architecture is working
as expected in production.

**Metrics to Track**:
- `c0_policy_none_rate`: Rate of `c0_policy=None` fallback (should decrease over time)
- `c0_bypass_reason_distribution`: Typed vs legacy bypass reasons
- `pa_boundary_rejection_rate_by_reason`: PA rejection breakdown
- `c0_preflight_eligibility_rate_by_c0_mode`: Eligibility by mode
- `l0_l1_c0_disagreement_rate`: How often L0 and L1 disagree (should be low)

**Dashboard Queries to Create**:
- Grafana/prometheus queries for C0 policy metrics
- Notion dashboards for weekly executive summary
- ADG query templates for C0 policy provenance tracing

**Alerting Rules**:
- WARN: `c0_policy_none_rate` > 5% (migration incomplete)
- CRIT: `c0_bypass_reason_distribution.legacy_ratio` > 10% (typed adoption lag)
- WARN: `pa_boundary_rejection_rate` spike (>2x baseline)
- CRIT: `l0_l1_c0_disagreement_rate` > 1% (L0 authority not respected)

**Work Required**:
- [ ] Add dashboard queries to monitoring system
- [ ] Set up alerts for unexpected bypass rates
- [ ] Create weekly report on C0 policy adoption
- [ ] Build self-service C0 policy provenance lookup tool
- [ ] Add C0 policy section to incident runbook

**Files to Create**:
- `ops_scripts/monitoring/c0_policy_dashboard.py`
- `ops_scripts/monitoring/c0_policy_weekly_report.py`
- `docs/runbooks/C0_POLICY_INCIDENT_RESPONSE.md`

---

## 3. Wave Structure

| Wave | Scope | Focus | Est. Tokens | Status | Dependencies |
|------|-------|-------|-------------|--------|--------------|
| W1 | DS-5 Migration Strategy | Decide + implement migration | ~3k | **Completed** | Parent plan stable 30d |
| W2 | DS-6 PA4 C0 Awareness | PA4 validation C0 policy | ~2k | **Completed** | W1 complete |
| W3 | DS-6 PA7 C0 Awareness | PA7 dispatch C0 policy | ~2k | **Completed** | W2 complete |
| W4 | DS-7 Monitoring | Dashboards + alerts | ~3k | **Completed** | W1 complete |
| W5 | DS-7 Weekly Reports | Automation + runbooks | ~2k | **Completed** | W4 complete |

## 4. Dependencies

- **Parent plan stable in production**: 30+ days without C0 policy incidents
- **DS-5 decision made**: Migration strategy must be selected before W1 start
- **Monitoring infrastructure**: Grafana/prometheus access for W4
- **No urgent production issues**: This is hardening work, not fire-fighting

## 5. Success Criteria

- [ ] DS-5: Migration strategy implemented and documented
- [ ] DS-5: <1% of RouteContracts have `c0_policy=None` (or documented exception)
- [ ] DS-6: PA4 and PA7 have C0 policy awareness matching PA0
- [ ] DS-6: OTEL spans emitted from PA4/PA7 with C0 fields
- [ ] DS-7: Dashboards show C0 policy metrics in real-time
- [ ] DS-7: Weekly reports auto-generated and reviewed
- [ ] DS-7: Alerting rules fire correctly on anomaly

## 6. Non-Goals

- **No new C0 modes**: Use existing `C0Mode` enum values only
- **No RouteContract changes**: Structure is frozen by parent plan
- **No C0 internals changes**: Retrieval, storage, caching untouched
- **No L3 orchestration changes**: Step-level policy is done (W1)
- **No entrypoint changes**: R4-like entrypoints are done (W3)

## 7. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Parent plan instability found | Low | High | Delay Phase 2 until root cause fixed |
| Monitoring infra unavailable | Med | Med | Use logs + manual queries initially |
| PA4/PA7 C0 changes break edge case | Low | High | Extensive testing, feature flags |
| Migration strategy debate blocks W1 | Med | Low | SVP Engineering decision authority |

## 8. Notes

- This plan is **information gathering only** - no implementation yet
- Implementation should begin after parent plan has 30-day production stability
- DS-5, DS-6, DS-7 can be worked in parallel once W1 decision is made
- Consider splitting this plan into 3 separate plans if scope grows

---

## Plan Metadata

- **Created**: 2026-05-08
- **Author**: Cascade (AI Assistant)
- **Source**: `.windsurf/plans/c0-policy-rectification-deferred-f7b2a9.md` §16
- **Notion Page**: [To be created]
