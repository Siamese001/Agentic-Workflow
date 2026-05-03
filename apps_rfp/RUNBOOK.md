# RUNBOOK — apps_rfp

> **When to use this:** a proposal is wrong, late, or financially out-of-bounds.
> **Companion docs:** `SLO.md` · `SVP_ENGINEERING_REVIEW.md` · `TECHNICAL_SPEC.md`
> **Owner:** see `CODEOWNERS`

## On-Call Decision Tree

```
A proposal run is misbehaving
├── Did pricing exceed the bound?
│   ├── YES → §1 Pricing Violation (CRITICAL)
│   └── NO  → continue
├── Did the proposal omit a required section?
│   ├── YES → §2 Section Completeness Failure
│   └── NO  → continue
├── Did win-rate regression detector flag a >0.15 drop?
│   ├── YES → §3 Win-Rate Regression
│   └── NO  → continue
├── Is assembly stalled >20min?
│   ├── YES → §4 Assembly Stall
│   └── NO  → §5 Generic
```

## §1 Pricing Violation (CRITICAL)

**Symptom:** `gate_violations=["PRICING_OUT_OF_BOUNDS"]` — the rendered proposal contains a price outside the configured envelope.

**This is the most critical failure type.** Pricing errors directly create financial / contractual exposure.

**Triage:**
1. **DO NOT submit the proposal.** The gate already blocked render but verify nothing leaked downstream.
2. Inspect the offending line items: `python -m apps_rfp --inspect --run-id=<id> --filter=pricing`.
3. Identify whether the LLM produced an out-of-bound price (assembly bug) or the bound is misconfigured (config bug).

**Mitigation:**
- If assembly bug → freeze the assembly engine; manually correct the proposal; root-cause the prompt.
- If config bug → immediately update bound (Author-Gate the change); re-run.
- **Never relax the bound** to make the gate pass.

**Audit:** every pricing violation is logged to an immutable audit trail; weekly review.

## §2 Section Completeness Failure

**Symptom:** `gate_violations=["MISSING_SECTION:<name>"]`.

**Triage:**
1. Compare RFP scope (`apps_rfp/data/sample_rfps/...`) against the rendered output.
2. The rendered output WILL contain a `[MISSING SECTION]` placeholder — surface to user, do not silently omit.

**Mitigation:**
- Re-run the missing section explicitly: `python -m apps_rfp --rerender-section <name> --run-id=<id>`.
- If the section keeps failing, the RFP-ingestion engine likely failed to capture the requirement upstream.

## §3 Win-Rate Regression (>0.15 drop)

**Symptom:** the regression detector emits `verdict=REGRESSION` against the historical win-rate baseline.

**Triage:**
1. Check baseline timestamp — is the comparison stale?
2. Check for concurrent changes: prompt template, assembly engine, retrieval source.
3. Spot-check 5 recent proposals for quality drop visible to a human reviewer.

**Mitigation:**
- Halt promotion of the assembly engine.
- Roll back the most recent assembly change.
- Re-run a known-good fixture; compare.

## §4 Assembly Stall (>20min)

**Symptom:** proposal run exceeds the 20-min hard ceiling.

**Triage:**
1. Check Qwen health.
2. Check section count — proposals with >12 sections may legitimately need more time; review hard ceiling for that scope class.
3. Check retrieval cold-start latency.

**Mitigation:**
- Cancel the run.
- For deadline-sensitive work, render a partial proposal with explicit `[INCOMPLETE]` markers.

## §5 Generic Investigation

1. `python -m apps_rfp --trace --replay --run-id=<id>`.
2. Bisect against last 24h commits.
3. Check `apps_rfp/data/sample_rfps/` for fixture drift.

## Rollback Procedure

apps_rfp produces proposals as artifacts. Rollback affects only future proposals. Past rendered proposals are **immutable** and retained for audit.

1. `git revert <commit>`.
2. `python -m apps_rfp --demo` smoke test.
3. Re-arm pricing-bound + win-rate gates.

## Top-3 Failure Modes

1. **Pricing violation** → §1 (CRITICAL — financial)
2. **Section completeness failure** → §2 (audit-critical)
3. **Assembly stall near deadline** → §4 (operational reality)

## Key Files

- `engines/proposal_assembly_engine.py` — main composer (25KB)
- `engines/rfp_ingestion_engine.py` — scope extraction (14KB)
- `engines/proposal_retrieval_engine.py` — past-bid retrieval
- `validators/proposal_gate_validator.py` — final gate
- `outputs/enterprise_rfp_renderer.py` — render

## Escalation Contacts

- **Primary on-call:** see `CODEOWNERS`
- **Pricing approval authority:** TBD (any pricing change requires this contact)
- **L3 inference owner:** see `agentic_core/L3_orchestration/inference/CODEOWNERS`

## Eval Harness (apps-eval-harness-closeout-b7c9d2 W3.P1)

The app-specific evaluation rubric and threshold profile live under
`apps_rfp/config/domain_contract/` and are authoritative via the L4
`AppEvalRubricRecord` + `AppThresholdProfileRecord` registered through
UWG.

**Rubric**: `apps_rfp/config/domain_contract/eval_rubrics.yaml`
**Threshold profile**: `apps_rfp/config/domain_contract/threshold_profiles.yaml`
**Grader roster**: `apps_rfp/config/domain_contract/grader_roster.yaml`

**HITL policy**: see `threshold_profiles.yaml` `hitl_policy` field
(`none` | `required_on_low` | `required_always`). Soft below-threshold
failures escalate when `required_on_low`; hard guardrail failures always
DENY regardless of policy.

**Run the advisory CI gate**:

`ash
python ops_scripts/ci/check_app_domain_harness_parity.py
`

Exit 0 with JSON report at `artifacts/ci/app_domain_harness_parity.json`.
Fail-closed mode via `APP_DOMAIN_HARNESS_PARITY_FAIL_CLOSED=1`.

**Ledger**: per-run outcomes land in
`artifacts/ledgers/eval_harness_outcome.sqlite` (fail-soft — Exit pipeline
is never blocked by ledger errors). Weekly rollup:

`ash
python ops_scripts/calibration/eval_harness_weekly_report.py
`

Emits JSON + Markdown under `docs/reports/eval_harness/<YYYY-Www>.md`.
