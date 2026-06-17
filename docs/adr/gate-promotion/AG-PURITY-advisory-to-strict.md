# AG-PURITY Gate Promotion Criteria: Advisory to Strict

**Status**: Accepted promotion criteria; gate remains advisory
**Gate ID**: AG-PURITY  
**Current Mode**: Advisory (warn, exit 0)  
**Target Mode**: Strict (fail, exit non-zero)  
**Document Version**: W4  
**Date**: 2026-05-12  

---

## Executive Summary

This document defines the criteria for promoting the AG-PURITY gate from **advisory mode** to **strict mode**. Strict mode activation is explicitly deferred beyond W4; this document establishes the promotion path.

**Explicit Statement**: **Strict mode is NOT activated in W4.** The gate remains advisory.

---

## Current Advisory Baseline (W4)

| Metric | Value |
|--------|-------|
| **Active Violations** | 969 |
| **Exempted Violations** | 5 |
| **Gate Mode** | advisory |
| **CI Effect** | warn |
| **Exit Code** | 0 |
| **Gate Version** | W4-ci-registration |

### Violation Breakdown by Leakage Type

| Leakage Type | Severity | Count |
|--------------|----------|-------|
| CORE_APP_SPECIFIC_LITERAL | P1 | 511 |
| APP_BYPASSES_U0 | P1 | 211 |
| APP_DIRECT_TO_CORE_LAYER | P2 | 215 |
| CORE_TO_APP_IMPORT | P1 | 18 |
| APP_RUNTIME_PACKAGE_MISSING | P2 | 11 |
| TEMPORARY_THIN_ADAPTER_UNRECEIPTED | P2 | 3 |
| CORE_TO_APP_CALL | P1 | 0 |

---

## What Strict Mode Means

| Aspect | Advisory (Current) | Strict (Target) |
|--------|-------------------|-----------------|
| **Exit Code** | 0 (always) | Non-zero if violations > baseline |
| **CI Blocking** | No | Yes |
| **Merge Blocking** | No | Yes |
| **New Violations** | Logged only | Logged + block merge |
| **Remediation Required** | Recommended | Mandatory |

### Strict Mode Activation Thresholds

When strict mode is activated:
- Any **new P1 violation** introduced in a PR → CI FAIL
- Any **new P2 violation** introduced in a PR → CI WARN (unless cumulative > threshold)
- **Existing baseline violations** → CI PASS with warnings (ratchet model)
- **Baseline exceedance** (>969 active) → CI FAIL

---

## Required Stability Window

### Duration
**Minimum 14 days** of advisory operation before strict mode consideration.

### Stability Metrics Required
| Metric | Target | Measurement |
|----------|--------|-------------|
| False Positive Rate | < 5% | Daily gate runs vs. manual audit |
| Flapping Incidents | 0 | No unexplained violation count swings |
| ADG Snapshot Success | 100% | All runs have valid ADG data |
| Baseline Variance | ±2% | Active violation count stable week-over-week |

### Evidence Collection
- Run gate daily for 14 days
- Log all results to `artifacts/ci/ag_purity_baseline.json`
- Track variance and document any anomalies

---

## False Positive Threshold

### Definition
A false positive is a violation flagged by AG-PURITY that, upon human review, is:
1. An allowed architectural pattern (e.g., legitimate U0 entry)
2. In an exempted path (test/doc/receipt/generated/migration) not caught by exemption classifier
3. A spurious match (e.g., "apps_rg" in a docstring, not code)

### Thresholds
| Gate Phase | Max Acceptable FP Rate |
|------------|------------------------|
| W4-W5 (now) | < 10% |
| Strict Promotion | < 5% |
| Post-Strict | < 2% |

### Calculation
```
FP Rate = (Manual Audits Flagging Error) / (Total Active Violations Sampled)
```

Sample minimum: 100 violations reviewed per week.

---

## Required P1 Remediation Threshold

### Current P1 Count
511 (CORE_APP_SPECIFIC_LITERAL) + 211 (APP_BYPASSES_U0) + 18 (CORE_TO_APP_IMPORT) = **740 P1 violations**

### Remediation Path
| Phase | Target P1 Count | Action |
|-------|-----------------|--------|
| W4 (now) | 740 | Baseline established |
| W5 | < 600 | Begin systematic remediation |
| W6 | < 400 | Priority apps_lic, apps_rg clean |
| W7 | < 200 | Core literals eliminated |
| Strict Promotion | < 100 | Remaining allowed thin adapters only |

### Remediation Priorities
1. **apps_lic** - highest business priority
2. **apps_rg** - second priority  
3. **apps_qna** - third priority
4. **apps_shared** - cross-cutting impact

---

## Owner Assignment Requirement

### Required Owners
Before strict mode activation, assign explicit owners for:

| Area | Owner Role | Responsibility |
|------|------------|----------------|
| Agentic Core | Core Platform Team | Resolve CORE_* violations |
| apps_lic | Lic Engineering | Resolve APP_* violations in apps_lic |
| apps_rg | RG Engineering | Resolve APP_* violations in apps_rg |
| apps_qna | QnA Engineering | Resolve APP_* violations in apps_qna |
| apps_shared | Shared Infra | Resolve apps_shared violations |
| Exemption Appeals | Architecture Board | Review exemption requests |

### Owner Sign-off Required
Each owner must:
1. Acknowledge their area's violation count
2. Commit to remediation timeline
3. Sign off on strict mode readiness

---

## Approval/Sign-off Requirement

### Required Approvals
| Role | Approval Required | Check |
|------|-------------------|-------|
| VP Engineering | Yes | Final strict mode authorization |
| Core Platform Lead | Yes | Technical readiness |
| CI/CD Lead | Yes | CI integration validated |
| Apps Engineering Leads | Yes | Per-app remediation commitment |

### Sign-off Document
Create `artifacts/ci/ag_purity_strict_mode_signoff.md` with:
- Approval signatures (name, role, date)
- Violation baseline at promotion time
- Remediation commitment table
- Rollback criteria

---

## Rollback Procedure

### Automatic Rollback Triggers
| Condition | Action |
|-----------|--------|
| FP Rate > 10% for 3 consecutive days | Auto-revert to advisory |
| CI failure rate > 5% for 2 days | Auto-revert to advisory |
| Emergency incident linked to AG-PURITY | Immediate manual revert |

### Rollback Steps
1. Set `AG_PURITY_FAIL_CLOSED=0` (env var)
2. Update gate metadata: `"gate_mode": "advisory"`
3. Notify #engineering-alerts channel
4. Schedule post-mortem within 24 hours
5. Create remediation ticket for re-promotion

### Rollback Evidence
Log rollback to:
- `artifacts/ci/ag_purity_rollback_log.jsonl`
- Notion incident page
- CI pipeline logs

---

## Environment/Config Switch for Strict Activation

### Env Var Control
```bash
# Advisory mode (default)
AG_PURITY_FAIL_CLOSED=0   # or unset

# Strict mode  
AG_PURITY_FAIL_CLOSED=1
```

### Activation Steps
1. Verify all promotion criteria met
2. Obtain all required sign-offs
3. Set `AG_PURITY_FAIL_CLOSED=1` in CI environment
4. Update baseline artifact with `mode: strict`
5. Announce in #engineering-announcements
6. Monitor for 48 hours closely

### Deactivation Steps
1. Set `AG_PURITY_FAIL_CLOSED=0`
2. Update baseline artifact with `mode: advisory`
3. Document reason for deactivation
4. Notify stakeholders

---

## Explicit Statement: Strict Mode NOT Activated in W4

> **⛔ STRICT MODE IS NOT ACTIVATED IN W4.**
>
> W4 scope is limited to:
> - CI registration ✅
> - Synthetic tests ✅
> - Baseline artifact ✅
> - Promotion criteria documentation ✅
>
> Strict mode activation requires:
> - All promotion criteria above met
> - VP Engineering approval
> - 14-day stability window
> - < 5% FP rate
> - < 100 P1 violations
>
> **Estimated earliest strict mode date: 2026-05-26**

---

## Appendix: Promotion Checklist

| # | Criterion | Status | Date |
|---|-----------|--------|------|
| 1 | 14-day stability window | ⏳ | TBD |
| 2 | FP Rate < 5% | ⏳ | TBD |
| 3 | P1 Violations < 100 | ⏳ | TBD |
| 4 | Owner assignments complete | ⏳ | TBD |
| 5 | VP Eng approval obtained | ⏳ | TBD |
| 6 | Sign-off document created | ⏳ | TBD |
| 7 | Rollback procedure tested | ⏳ | TBD |
| 8 | `AG_PURITY_FAIL_CLOSED` env var ready | ✅ | 2026-05-12 |

---

## References

- Plan: `.claude/plans/adg-ci-agentic-core-purity-a7c3e9.md`
- Gate: `ops_scripts/ci/adg_gates/gate_agentic_core_purity.py`
- Baseline: `artifacts/ci/agentic_core_purity_baseline.json`
- W0 Receipt: `artifacts/ci/ag_purity_w0_schema_discovery_receipt.md`
- W1 Receipt: `artifacts/ci/ag_purity_w1_gate_skeleton_receipt.md`
- W2 Receipt: `artifacts/ci/ag_purity_w2_leakage_refinement_receipt.md`
- W3 Receipt: `artifacts/ci/ag_purity_w3_runtime_package_receipt.md`
- W4 Receipt: `artifacts/ci/ag_purity_w4_ci_registration_tests_baseline_receipt.md`

---

*Document created: 2026-05-12*
*Version: W4*
*Next review: 2026-05-26 (post-stability window)*
