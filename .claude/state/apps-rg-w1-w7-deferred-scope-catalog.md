# apps_rg W1-W7 Deferred Scope Catalog

**Generated:** 2026-05-03
**Parent Plan:** `apps-rg-runtime-cert-hardening-a3f8c2` (Completed)
**Follow-Up Plan:** `apps-rg-deferred-activation-w8-a7f4d9` (Draft)

## Summary

This document catalogs all scope deferred during W1-W7 execution, with rationale for each deferral and activation criteria for the follow-up plan.

---

## 1. W6.P1 — Headline Ensemble SVP Inclusion

### What
Revert `SENIORITY_SKIP` hardcoded filter in `ats_coverage.py` and update `headline_ensemble.py` prompts so the LLM **organically includes seniority tokens** (SVP, EVP, VP, MD, CTO, etc.) in generated resume headlines, rather than filtering them out during coverage scoring.

### Current State (Deferred)
```python
# apps_rg/integrations/ats_coverage.py:167
_SENIORITY_SKIP = {"svp", "evp", "vp", "md", "gm", "cto", "ceo", "coo", "caio", "cdo", "ciso"}
title_tokens = [t for t in norm_t.split() if len(t) > 3 and t not in _SENIORITY_SKIP]
```

The `SENIORITY_SKIP` set explicitly removes seniority tokens from the ATS coverage check. This was originally added because:
1. Seniority tokens are "cheap" — they don't demonstrate domain expertise
2. The headline was getting prepend-bloat from `ensure_title_in_headline` post-processing
3. Coverage scoring focused on "hard" terms (domain keywords) vs "soft" terms (titles)

### Why Deferred

| Factor | Rationale |
|--------|-----------|
| **Live LLM Required** | Prompt engineering changes require actual LLM calls to verify output quality. Cannot unit-test prompt efficacy with mocks. |
| **Iteration Uncertainty** | May need 3-5 prompt variants to get "SVP Agentic Transformation" vs "Agentic Transformation Leader". Budget: ~6k tokens. |
| **Quality Verification** | Need human evaluation of 10-20 generated headlines to confirm seniority token placement feels natural, not forced. |
| **Blast Radius** | Changes to `headline_ensemble.py` affect all apps_rg resume generation; requires staged rollout. |
| **Dependency on W4** | W4 canonical entrypoint must be stable before iterating on output quality (chicken-egg: need live runs to tune). |

### Acceptance Criteria (from Plan)
- [ ] Headline contains seniority token organically (not via prepend-bloat)
- [ ] `ensure_title_in_headline` becomes no-op or is removed
- [ ] ATS coverage ≥0.85 maintained for other hard terms
- [ ] Zero regression on 8-app test matrix

### Activation Trigger
Picked up in **W9.P1** of follow-up plan. Requires:
1. AG-RG-011/012 decisions resolved (W8 complete)
2. Live `main_canonical()` runs emitting valid receipts (W10.1)
3. Headline quality corpus of 20+ samples for prompt iteration

---

## 2. AG-RG-011 — Post-Run Patch Policy

### What
Define policy for modifying `generated_resume.docx` after a run completes (e.g., manual edit, ATS optimizer pass).

### Options
| Option | Score | Description |
|--------|-------|-------------|
| **B (⭐ 0.86)** | **Re-seal helper** | `reseal_artifact()` recomputes sha256, updates `runtime_exhaust_bundle.json`, logs audit event |
| C (0.78) | Per-tool allowlist | Only specific approved tools may patch |
| A (0.71) | Forbid all patches | Any modification breaks cert bundle |
| D (0.34) | Auto-accept | No verification (rejected) |

### Skeleton Status
`apps_shared/spine_emission/reseal.py` implemented (142 LOC) with:
- `compute_sha256()` — deterministic hash
- `read_exhaust_bundle()` — fail-soft JSON load
- `reseal_artifact()` — updates `artifact_sha256_map` + appends `reseal_events` audit trail

### Why Deferred
Policy decision requires operator judgment on:
- Whether Fort Knox certification should tolerate any post-run modification
- Tradeoff between strict forbid (CI gate enforcement) vs operational flexibility (reseal helper)

### Activation Criteria
- [ ] User selects option A, B, or C
- [ ] If **B**: Activate `reseal_artifact()` policy, document in ADR
- [ ] If **A**: Add CI gate `FORBID_POST_RUN_PATCH` blocking any sha256 mismatch
- [ ] Update `certification/apps_e2e_requirements_source.json` with patch policy control

---

## 3. AG-RG-012 — HITL Blocking Behavior

### What
Define how `HITLApprovalGate.evaluate()` behaves when `run_report.status='HUMAN_REVIEW'`.

### Options
| Option | Score | Description |
|--------|-------|-------------|
| **B (⭐ 0.88)** | **Fail-closed** | Non-interactive; reject/deny if no prior HITL decision logged |
| A (0.75) | CLI stdin pause | Interactive prompt (requires TTY; blocks in background jobs) |
| C (0.69) | Async callback | Webhook or poll-based async approval (complex infrastructure) |
| D (0.42) | Advisory only | Log but don't block (W1.P1 legacy behavior) |

### Skeleton Status
`apps_rg/integrations/hitl_bridge.py` implemented (120 LOC) with:
- `read_run_report()` — parses `run_report.json`
- `build_hitl_context()` — constructs `GateContext.hitl` dict
- `evaluate_hitl()` — calls `HITLApprovalGate.evaluate(ctx)`, returns `GateDecision`

### Why Deferred
Operator environment decision:
- Background job runners (CI, scheduled tasks) cannot use stdin pause
- Async callback requires infrastructure not yet deployed
- Fail-closed is safest but may reject valid runs awaiting human review

### Activation Criteria
- [ ] User selects option A, B, or C
- [ ] Wire selected behavior into `apps_rg/__main__.py` post-run logic
- [ ] If **B**: Ensure `stop_condition_violated=True` on reject per §32 Fort Knox
- [ ] Add environment detection (TTY check) to auto-select mode if option A

---

## 4. W10 — Live Integration Run & Proof Verification

### What
Execute `main_canonical()` against real inputs and verify all 8 canonical receipts emitted.

### Prerequisites
1. AG-RG-011/012 resolved (policy/behavior defined)
2. W9.P1 headline ensemble stable (optional, can use legacy for W10)
3. `python -m apps_rg --target-company "TestCorp"` via `main_canonical()`

### Expected Receipts
| Receipt | File | Claim |
|---------|------|-------|
| Route Contract | `route_contract.json` | APPS-REQ-RG-001 (V15 binding) |
| L2 Execution | `l2_execution_receipt.json` | APPS-REQ-RG-002 (E1-E5 sealed) |
| Exit Review | `exit_review_packet.json` | APPS-REQ-RG-003 (X1-X3 canonical) |
| Gate Verdicts | `gate_verdicts.json` | APPS-REQ-RG-004 (G01/G24/G26/G28) |
| Spine Proof | `spine_proof_bundle.json` | APPS-REQ-RG-005 (no-bypass) |
| Replay | `replay_comparison.json` | APPS-REQ-RG-006 (determinism) |
| ATS Coverage | `ats_coverage_report.json` | APPS-REQ-RG-007 (≥0.73 baseline) |
| Provenance | `provenance_report.json` | APPS-REQ-RG-008 (master binding) |

### Why Deferred
Requires all upstream wiring to be stable:
- W4 adapter must emit canonical receipts (not just legacy JSON)
- W5 proof producer needs actual artifacts to hash
- AG decisions affect whether HITL blocks the run

### Activation Criteria
- [ ] `python -m apps_rg` via `main_canonical()` completes without error
- [ ] All 8 receipt files present in `artifacts/apps_rg/runs/<timestamp>/`
- [ ] `tools/cert/apps_e2e/apps_rg_proof_producer.py` reports ≥6/8 PASS
- [ ] `scripts/compile_apps_e2e_signoff.py` includes apps_rg evidence

---

## Deferred Scope by Wave (Follow-Up Plan)

| Wave | Phase | Scope | Blocker |
|------|-------|-------|---------|
| **W8** | P8.1 | Execute AG-RG-011 (reseal policy) | User decision |
| **W8** | P8.2 | Execute AG-RG-012 (HITL blocking) | User decision |
| **W9** | P9.1 | W6.P1 headline SVP inclusion | Live LLM iteration |
| **W10** | P10.1 | Live `main_canonical()` run | W8 + W9 (optional) |
| **W10** | P10.2 | Proof producer ≥6/8 PASS | W10.1 receipts |

---

## Files Affected (Deferred Activation)

| File | Current Status | Activation Trigger |
|------|---------------|-------------------|
| `apps_rg/integrations/hops/headline_ensemble.py` | Uses `SENIORITY_SKIP` | W9.P1 prompt iteration |
| `apps_rg/integrations/ats_coverage.py` | Filters seniority tokens | W9.P1 remove `_SENIORITY_SKIP` |
| `apps_shared/spine_emission/reseal.py` | Skeleton (policy unactivated) | W8.P1 AG-RG-011 decision |
| `apps_rg/integrations/hitl_bridge.py` | Skeleton (behavior unwired) | W8.P2 AG-RG-012 decision |
| `apps_rg/__main__.py` | `main_canonical()` exists, HITL unwired | W8.P2 wire `evaluate_hitl()` |

---

## Decision Dependencies

```
AG-RG-011 (reseal policy)
    └── enables W8.P1
        └── enables W10 (live run with defined patch policy)

AG-RG-012 (HITL blocking)
    └── enables W8.P2
        └── enables W10 (live run with defined HITL behavior)

W9.P1 (headline SVP)
    └── can parallel W8 (no dependency)
    └── ideally completes before W10 (quality gate)
```

---

## Risk: Long Deferral

If W8-W10 are delayed >14 days:
- Skeletons may drift from `agentic_core` API changes
- `SpineRuntimeAdapter` contract may need re-verification
- Author-Gate queue may accumulate additional pending decisions

**Mitigation:** Weekly CI run of `test_w{3,4,5,6}_*.py` to catch regressions.
