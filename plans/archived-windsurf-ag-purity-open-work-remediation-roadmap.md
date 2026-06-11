---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\ag-purity-open-work-remediation-roadmap.md'
original_relative_path: 'ag-purity-open-work-remediation-roadmap.md'
source_sha256: c9899787e075b6caea4cbaed9e8b3292a492079aebfade6fa8ebcb457449c701
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-13'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
title: "AG-PURITY Open Work: Remediation + Strict-Mode Readiness"
slug: ag-purity-open-work-remediation-roadmap
tier: T2
status: Not Started
created: 2026-05-12
source_plan: adg-ci-agentic-core-purity-a7c3e9
dod_exempt: false
tags:
  - ag-purity
  - remediation
  - u0-runtime-package
  - strict-mode-readiness
  - agentic-core-purity
  - architecture-enforcement
---

# AG-PURITY Open Work: Remediation + Strict-Mode Readiness

## 1. Problem Statement

The AG-PURITY advisory CI gate (`ops_scripts/ci/adg_gates/gate_agentic_core_purity.py`) was fully constructed through W0–W4 of plan `adg-ci-agentic-core-purity-a7c3e9`. The gate is advisory, runs in CI, emits structured JSON artifacts, and captures a baseline of **969 active violations**.

**The remaining problem is not detection — it is remediation and readiness.**

Three blockers prevent strict-mode promotion:

1. **P1 violations too high** — 740 active P1 violations (threshold: <100 for strict readiness).
2. **U0 runtime packages missing** — 11 apps have no typed `runtime_customization_package` surface, so the gate cannot enforce the positive allowed-flow invariant for those apps.
3. **Architectural debt not clustered** — violation inventory is not yet organized into remediable clusters, so no engineering team can be assigned.

This plan owns all post-W4 open work: violation clustering, low-risk cleanup, architectural remediation by type, U0 package creation, and the strict-mode readiness review and activation sequence.

**What this plan does NOT do**: construct the gate (done), activate strict mode (gated on W12/W13 criteria), or auto-fix anything without explicit Author-Gate approval.

---

## 2. Current Baseline

Captured in `artifacts/ci/agentic_core_purity_baseline.json` (W4, commit `b8f365d7a9`).

### Violation Counts

| Leakage Type | Severity | Count |
|---|---|---|
| `CORE_APP_SPECIFIC_LITERAL` | P1 | 511 |
| `APP_BYPASSES_U0` | P1 | 211 |
| `APP_DIRECT_TO_CORE_LAYER` | P2 | 215 |
| `CORE_TO_APP_IMPORT` | P1 | 18 |
| `APP_RUNTIME_PACKAGE_MISSING` | P2 | 11 |
| `TEMPORARY_THIN_ADAPTER_UNRECEIPTED` | P2 | 3 |
| `CORE_TO_APP_CALL` | P1 | 0 |
| **Total Active** | | **969** |
| **P1 Active** | | **740** |
| Exempted | exempt | 5 |

### Apps Missing U0 Runtime Customization Package (11 of 11)

```
apps_architect
apps_eval
apps_exec
apps_lic
apps_qna
apps_repo_brief
apps_research
apps_rfp
apps_rg
apps_shared
apps_underwriting_ai
```

### Strict-Mode Blockers

| Blocker | Threshold | Current | Gap |
|---|---|---|---|
| P1 violation count | < 100 | 740 | −640 |
| U0 runtime packages missing | 0 | 11 apps | −11 apps |
| CORE_TO_APP_IMPORT | 0 or receipted | 18 | −18 |
| TEMPORARY_THIN_ADAPTER_UNRECEIPTED | 0 | 3 | −3 |
| Stability window (advisory) | 14 days clean | not yet complete | — |
| VP Engineering approval | documented | not yet obtained | — |
| False positive rate | < 5% | not yet measured | — |

---

## 3. Success Criteria

| ID | Criterion | Wave |
|----|-----------|------|
| SC-1 | P1 reduced from 740 to below 600 after first remediation wave | W7 |
| SC-2 | P1 eventually below 100 for strict-mode readiness | W10–W11 |
| SC-3 | All 11 apps_* have typed U0 `runtime_customization_package` surfaces | W9 |
| SC-4 | `CORE_TO_APP_IMPORT` reduced to 0 or each formally receipted as a `TEMPORARY_THIN_ADAPTER` | W8 |
| SC-5 | `TEMPORARY_THIN_ADAPTER_UNRECEIPTED` reduced to 0 | W11 |
| SC-6 | AG-PURITY baseline artifact refreshed after each remediation wave | W7–W11 |
| SC-7 | Strict mode remains OFF until W12/W13 approval criteria explicitly met | W12–W13 |
| SC-8 | Violation clusters produced (W5) drive engineering assignment | W5 |
| SC-9 | False positive rate measured and documented below 5% before W12 | W12 |
| SC-10 | 14-day advisory stability window confirmed before W12 | W12 |

---

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W5 | P1–P3 | Remediation planning: load baseline, cluster violations, produce plan + cluster JSON | ~3k | Baseline artifact exists; ADG SQLite accessible | Not Started | SC-8; `ag_purity_w5_remediation_plan.md` + `ag_purity_w5_remediation_clusters.json` emitted |
| W6 | P1–P2 | False-positive cleanup and exemption improvement; no architectural rewiring | ~2k | W5 clusters complete | Not Started | Exemption count increases; active count decreases; baseline refreshed |
| W7 | P1–P4 | CORE_APP_SPECIFIC_LITERAL remediation: remove/replace app literals in `agentic_core`; move meaning to app-owned runtime packages or registries | ~6k | W5 clusters available; Author-Gate issued per change | Not Started | SC-1 (P1 below 600); baseline refreshed |
| W8 | P1–P3 | CORE_TO_APP_IMPORT removal: eliminate `agentic_core → apps_*` imports; use thin adapter receipts only where unavoidable | ~4k | W7 complete or concurrent | Not Started | SC-4 (18 → 0 or receipted) |
| W9 | P1–P3 | U0 Runtime Package creation: create typed `runtime_customization_package` for all 11 missing apps | ~5k | Apps spine manifests readable | Not Started | SC-3 (all 11 apps have U0 package) |
| W10 | P1–P4 | APP_BYPASSES_U0 remediation: replace direct `apps_*` imports into core L0/L1 internals with U0 package entry | ~6k | W9 complete (U0 packages exist to route through) | Not Started | APP_BYPASSES_U0 count materially reduced; P1 trajectory toward SC-2 |
| W11 | P1–P2 | Thin adapter receipt or removal: receipt or remove all unreceipted adapters; reduce TEMPORARY_THIN_ADAPTER_UNRECEIPTED to 0 | ~2k | W8 complete | Not Started | SC-5 (0 unreceipted adapters) |
| W12 | P1–P3 | Strict-mode readiness review: verify 14-day stability, <5% FP rate, P1 <100, owners assigned, VP Eng approval documented | ~3k | W7–W11 substantially complete | Not Started | SC-7 affirmed; explicit VP approval documented; strict mode still OFF |
| W13 | P1–P2 | Strict-mode activation: enable `AG_PURITY_FAIL_CLOSED=1`; validate fail-closed behavior; emit activation receipt | ~2k | W12 approval issued | Not Started | SC-7 (strict mode ON only after W12 approval); activation receipt at `artifacts/ci/ag_purity_strict_activation_receipt.md` |

---

## 5. Phase-Level Table

| Wave | Phase ID | Title | Scope | Output Artifact | Risk | Status |
|------|----------|-------|-------|-----------------|------|--------|
| W5 | W5.P1 | Load and parse W4 baseline | `artifacts/ci/agentic_core_purity_baseline.json` + gate run | Refreshed violation list | Low | Not Started |
| W5 | W5.P2 | Cluster by leakage type and source path | Violation data | Cluster groupings (in-memory) | Low | Not Started |
| W5 | W5.P3 | Produce remediation cluster JSON | `artifacts/ci/` | `ag_purity_w5_remediation_clusters.json` | Low | Not Started |
| W6 | W6.P0 | Resolve P2 ratchet ceiling blocker: update `artifacts/adg/p2_ratchet.json` ceiling to ≥139 (with justification) OR run with `ADG_P2_RATCHET_BYPASS=1`; verify `generate_full_adg.py` exits 0 and produces a fresh snapshot | `artifacts/adg/p2_ratchet.json` | Updated ratchet ceiling; fresh ADG sqlite | Medium | Not Started |
| W6 | W6.P1 | Audit current exemptions for false positives | `gate_agentic_core_purity.py` + exemption patterns | False positive list | Low | Not Started |
| W6 | W6.P2 | Expand/correct exemption patterns where safe | `gate_agentic_core_purity.py` | Updated gate; refreshed baseline | Low | Not Started |
| W7 | W7.P1 | Identify top-N literal clusters from W5 output | W5 cluster JSON | Targeted literal list | Low | Not Started |
| W7 | W7.P2 | Remove or replace app literals in `agentic_core` (Author-Gate per batch) | `agentic_core/**/*.py` | Modified core files; Author-Gate receipts | Medium | Not Started |
| W7 | W7.P3 | Move app-specific meaning to app-owned runtime packages or registries | `apps_*/config/` or new registry files | New app-owned config files | Medium | Not Started |
| W7 | W7.P4 | Refresh AG-PURITY baseline | Gate run | Updated `agentic_core_purity_baseline.json` | Low | Not Started |
| W8 | W8.P1 | Enumerate all 18 CORE_TO_APP_IMPORT violations from W5 clusters | Cluster JSON | Annotated import list | Low | Not Started |
| W8 | W8.P2 | Remove core-to-app imports (move config/gates to app-owned location or U0) | `agentic_core/**/*.py` | Modified imports; Author-Gate receipts | High | Not Started |
| W8 | W8.P3 | Create thin adapter receipts for unavoidable cases | `artifacts/governance/migration_receipts/` | TEMPORARY_THIN_ADAPTER receipt files | Low | Not Started |
| W9 | W9.P1 | Author typed U0 `runtime_customization_package` for each of 11 apps | `apps_*/runtime/entry/runtime_customization_package.py` (×11) | 11 new U0 package files | Medium | Not Started |
| W9 | W9.P2 | Validate each package satisfies U0 type contract | Gate re-run | Reduced `APP_RUNTIME_PACKAGE_MISSING` count | Low | Not Started |
| W10 | W10.P1 | Enumerate APP_BYPASSES_U0 violations by app from W5 clusters | Cluster JSON | Per-app bypass list | Low | Not Started |
| W10 | W10.P2 | Replace direct L0/L1 imports with U0 entry point (Author-Gate per app) | `apps_*/**/*.py` | Modified app files; Author-Gate receipts | High | Not Started |
| W10 | W10.P3 | Preserve allowed entrypoints and approved adapters | `agentic_core/runtime/entry/` | No-op or gate allowlist update | Low | Not Started |
| W10 | W10.P4 | Refresh AG-PURITY baseline | Gate run | Updated `agentic_core_purity_baseline.json` | Low | Not Started |
| W11 | W11.P1 | Enumerate 3 TEMPORARY_THIN_ADAPTER_UNRECEIPTED instances | Cluster JSON | Annotated adapter list | Low | Not Started |
| W11 | W11.P2 | For each: create approved receipt OR remove adapter | `artifacts/governance/migration_receipts/` or code | Receipt files or removals | Medium | Not Started |
| W12 | W12.P1 | Verify 14-day advisory stability window has elapsed | Gate run history | Stability attestation | Low | Not Started |
| W12 | W12.P2 | Compute and document false positive rate (manual sampling) | Violation artifacts | FP rate report | Medium | Not Started |
| W12 | W12.P3 | Verify P1 count below 100 | Gate run | P1 count confirmation | Low | Not Started |
| W12 | W12.P4 | Assign engineering owners for remaining violations | Owner roster | Assignment doc | Low | Not Started |
| W12 | W12.P5 | Obtain and document VP Engineering approval | Approval channel | Signed approval artifact | Low | Not Started |
| W13 | W13.P1 | Enable `AG_PURITY_FAIL_CLOSED=1` in CI configuration | CI config | Config change | Medium | Not Started |
| W13 | W13.P2 | Validate fail-closed behavior on known violation | Gate run with synthetic violation | Pass/fail evidence | Low | Not Started |
| W13 | W13.P3 | Emit strict activation receipt | `artifacts/ci/` | `ag_purity_strict_activation_receipt.md` | Low | Not Started |

---

## 6. Gap Register

| ID | Gap | Risk | Resolution Wave |
|----|-----|------|-----------------|
| G1 | P1 remediation inventory not clustered; no engineering assignment possible | High | W5 |
| G2 | U0 runtime packages missing for 11 apps; positive allowed-flow cannot be enforced for those apps | High | W9 |
| G3 | 511 app-specific literals remain in `agentic_core`; violates "core owns mechanisms, apps own meaning" | High | W7 |
| G4 | 18 `agentic_core → apps_*` imports remain; reverse flow is an architectural violation | High | W8 |
| G5 | 211 apps directly importing core L0/L1 internals; bypasses U0 contract | High | W10 |
| G6 | 3 thin adapter instances have no migration receipt; unaudited bypass surface | Medium | W11 |
| G7 | Strict mode blocked by P1 count (740 vs threshold 100) and 14-day stability window not complete | High | W12–W13 |
| G8 | P2 ratchet ceiling (23) vs current MEDIUM antipattern count (139) blocks `generate_full_adg.py`; ADG snapshot is 2+ days stale (latest: `adg_indexed_05102026_1319.sqlite`); baseline `adg_db_path` in `agentic_core_purity_baseline.json` references a non-existent file | High | Pre-W6 (must resolve before any wave refreshes ADG snapshot) |

---

## 7. Definition of Done

| Wave | ID | Criterion | Verification Method | Status |
|------|----|-----------|---------------------|--------|
| W5 | DoD-W5-1 | `artifacts/ci/ag_purity_w5_remediation_plan.md` exists | File existence check | Not Started |
| W5 | DoD-W5-2 | `artifacts/ci/ag_purity_w5_remediation_clusters.json` exists and is valid JSON | `python -c "import json; json.load(open('artifacts/ci/ag_purity_w5_remediation_clusters.json'))"` | Not Started |
| W5 | DoD-W5-3 | Clusters cover enough P1 violations to target reducing from 740 to below 600 in W7 | Cluster JSON sum of P1 covered violations | Not Started |
| W5 | DoD-W5-4 | No production code modified | `git diff HEAD --name-only` contains no `agentic_core/` or `apps_*/` Python files | Not Started |
| W6 | DoD-W6-1 | Active violation count decreases or stays flat (no regressions from exemption cleanup) | Gate re-run baseline comparison | Not Started |
| W6 | DoD-W6-2 | Baseline artifact refreshed | `artifacts/ci/agentic_core_purity_baseline.json` `last_updated` field updated | Not Started |
| W7 | DoD-W7-1 | P1 active violation count below 600 | Gate run output; `counts_by_leakage_type.CORE_APP_SPECIFIC_LITERAL` reduced | Not Started |
| W7 | DoD-W7-2 | Author-Gate receipt issued for each batch of literal removals | `DECISION_CAPTURED:` markers in session log | Not Started |
| W7 | DoD-W7-3 | Baseline artifact refreshed | File timestamp and count updated | Not Started |
| W8 | DoD-W8-1 | `CORE_TO_APP_IMPORT` count is 0 or each remaining instance has a `TEMPORARY_THIN_ADAPTER` receipt | Gate run + receipt file listing | Not Started |
| W9 | DoD-W9-1 | All 11 apps have `runtime_customization_package.py` at canonical U0 path | Gate run; `APP_RUNTIME_PACKAGE_MISSING` count = 0 | Not Started |
| W9 | DoD-W9-2 | Each U0 package satisfies type annotation contract | Gate run; `APP_RUNTIME_PACKAGE_UNTYPED` count = 0 | Not Started |
| W10 | DoD-W10-1 | `APP_BYPASSES_U0` count materially reduced; P1 total on trajectory toward <100 | Gate run baseline comparison | Not Started |
| W11 | DoD-W11-1 | `TEMPORARY_THIN_ADAPTER_UNRECEIPTED` count = 0 | Gate run | Not Started |
| W12 | DoD-W12-1 | 14-day advisory stability window attested | Timestamped gate run history | Not Started |
| W12 | DoD-W12-2 | False positive rate documented below 5% | FP rate report artifact | Not Started |
| W12 | DoD-W12-3 | P1 count confirmed below 100 | Gate run output | Not Started |
| W12 | DoD-W12-4 | VP Engineering approval documented | Signed approval artifact or documented approval | Not Started |
| W12 | DoD-W12-5 | Strict mode still OFF at W12 exit | `AG_PURITY_FAIL_CLOSED` env var NOT set in CI | Not Started |
| W13 | DoD-W13-1 | `AG_PURITY_FAIL_CLOSED=1` set in CI config | CI config diff | Not Started |
| W13 | DoD-W13-2 | Fail-closed behavior validated with synthetic violation | Gate run log shows non-zero exit on known violation | Not Started |
| W13 | DoD-W13-3 | `artifacts/ci/ag_purity_strict_activation_receipt.md` exists | File existence check | Not Started |

---

## 8. Non-Goals

- ❌ No strict mode activation before W12/W13 approval criteria are met
- ❌ No hidden auto-fix or automated migration of violations
- ❌ No app-specific logic moved into `agentic_core` (that is the inverse of the goal)
- ❌ No weakening of AG-PURITY detection logic to artificially reduce violation counts
- ❌ No direct L4/UWG/runtime mutation changes as part of this roadmap
- ❌ No reconstruction of the gate (W0–W4 complete; `gate_agentic_core_purity.py` is the SSOT)
- ❌ No remediation executed in W5 (W5 is planning and clustering only)

---

## 9. Next Action

**The next executable step is W5 only.**

W5 produces the violation cluster inventory and remediation plan that unlocks all downstream waves. No production code changes occur in W5.

---

## W5 Execution Prompt

```
Execute AG-PURITY W5 remediation planning only.

Scope:
- Do not modify production code.
- Do not auto-fix violations.
- Do not activate strict mode.
- Load the W4 baseline and latest AG-PURITY artifact.
- Cluster active P1 violations by leakage_type, source_path, target_path, app name, core layer, and remediation pattern.
- Produce:
  artifacts/ci/ag_purity_w5_remediation_plan.md
  artifacts/ci/ag_purity_w5_remediation_clusters.json
- Target enough clusters to reduce P1 from 740 to below 600 in follow-on remediation.
- Preserve the rule:
  core owns mechanisms, apps own meaning, apps enter through U0 runtime_customization_package.

Acceptance:
- New plan file exists.
- It contains only post-W4 open work.
- It clearly itemizes W5-W13.
- It does not duplicate completed W0-W4 details beyond baseline context.
- No production code changes.
- No strict mode activation.
```

---

## References

- Source plan (W0–W4 implementation): `.windsurf/plans/adg-ci-agentic-core-purity-a7c3e9.md`
- Gate implementation: `ops_scripts/ci/adg_gates/gate_agentic_core_purity.py`
- Baseline artifact: `artifacts/ci/agentic_core_purity_baseline.json`
- Promotion criteria: `docs/adr/gate-promotion/AG-PURITY-advisory-to-strict.md`
- Thin adapter receipts: `artifacts/governance/migration_receipts/`
- Constitutional rule: `.windsurf/rules/agentic-core-static.md`
- Constitutional rule: `.windsurf/rules/adg-canonical-invariants.md`

---

Plan Version: 1.0 (W5–W13 open work; W0–W4 complete in source plan)
Created: 2026-05-12
