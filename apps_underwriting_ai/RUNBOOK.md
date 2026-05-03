# RUNBOOK — apps_underwriting_ai

> **When to use this:** an underwriting decision is wrong, missing, or malformed.
> **Companion docs:** `SLO.md` · `SVP_ENGINEERING_REVIEW.md` · `README.md`
> **Owner:** see `CODEOWNERS`
> **Maturity:** skeleton — many "real-domain" runbook entries are placeholders pending feature-complete logic.

## On-Call Decision Tree

```
An underwriting run is misbehaving
├── Did the verdict come back as INSUFFICIENT_EVIDENCE unexpectedly?
│   ├── YES → §1 Insufficient Evidence
│   └── NO  → continue
├── Did the verdict come back as REFER unexpectedly?
│   ├── YES → §2 Unresolved Reconciliation
│   └── NO  → continue
├── Did one of the 5 pipeline stages raise?
│   ├── YES → §3 Stage Exception
│   └── NO  → continue
├── Did the run complete but emit no artifacts?
│   ├── YES → §4 Artifact Emission Failure
│   └── NO  → §5 Generic Investigation
```

## §1 Insufficient Evidence

**Symptom:** `decision.verdict == INSUFFICIENT_EVIDENCE` but the request had documents.

**Likely cause:** stage 4 (`collect_evidence`) failed to append records, OR stage 3 (`derive_features`) emitted an empty feature vector AND the request had no documents.

**Triage:**
1. Inspect `result.register.records` — should have ≥1 record per `collect_*_evidence` call.
2. Inspect `result.features.feature_vector` — should reflect document count from stage 2.

**Mitigation:**
- If skeleton, this is expected for empty-document requests; verify the input.
- If feature-complete, audit the collection adapter for the missing dimension.

## §2 Unresolved Reconciliation

**Symptom:** `decision.verdict == REFER` because `reconciliation.unresolved_count > 0`.

**Triage:** read `reconciliation.notes` — surfaces which documents could not be reconciled.

**Mitigation:**
- For human-resolvable mismatches, route to manual underwriting queue.
- For systemic OCR/parser failures, freeze `DocumentReconciliationEngine` and root-cause.

## §3 Stage Exception

**Symptom:** the 5-stage pipeline raises mid-run.

**Triage:**
1. Identify which stage raised — observability adapter emits `stage.start` / `stage.complete` events.
2. Re-run the offending stage in isolation: instantiate the engine directly with the same context.

**Mitigation:**
- For deterministic bugs, fix and re-run.
- For provider-side failures (downstream LLM, vector store), retry with backoff.

## §4 Artifact Emission Failure

**Symptom:** run completes but no `decision_<id>.md` / `run_summary_<id>.json` appears under `--artifact-dir`.

**Triage:**
1. Verify `--artifact-dir` was passed.
2. Verify directory permissions.

**Mitigation:**
- Re-run with explicit `--artifact-dir`.
- Check `EnterpriseUnderwritingRenderer.render_to_disk` for path-creation errors.

## §5 Generic Investigation

1. Run `python -m apps_underwriting_ai --demo` to verify the pipeline is healthy in isolation.
2. Bisect against last 24h commits to `apps_underwriting_ai/engines/`.
3. Check observability events for the failing run.

## Rollback Procedure

apps_underwriting_ai produces decisions as artifacts. Rollback affects only future decisions.

1. `git revert <commit>`.
2. `python -m apps_underwriting_ai --demo` smoke test.

## Top-3 Failure Modes

1. **Insufficient evidence on a real applicant** → §1 (skeleton-stage frequent; feature-complete should be rare)
2. **REFER cascade from document mismatch** → §2 (operational reality once parsers land)
3. **Stage exception during feature derivation** → §3 (most likely site of real-domain bugs)

## Key Files

- `engines/underwriting_engine.py` — imperative driver
- `engines/decision_packet_assembler.py` — verdict heuristic (replace for real-domain logic)
- `engines/feature_derivation_engine.py` — risk feature stage (replace for real-domain logic)
- `integrations/execution_adapter.py` — runtime handoff
- `outputs/decision_renderer.py` — text/JSON output

## Escalation Contacts

- **Primary on-call:** see `CODEOWNERS`
- **Underwriting domain SME:** TBD
- **L3 orchestration owner:** see `agentic_core/L3_orchestration/CODEOWNERS`

## Eval Harness (apps-eval-harness-closeout-b7c9d2 W3.P1)

The app-specific evaluation rubric and threshold profile live under
`apps_underwriting_ai/config/domain_contract/` and are authoritative via the L4
`AppEvalRubricRecord` + `AppThresholdProfileRecord` registered through
UWG.

**Rubric**: `apps_underwriting_ai/config/domain_contract/eval_rubrics.yaml`
**Threshold profile**: `apps_underwriting_ai/config/domain_contract/threshold_profiles.yaml`
**Grader roster**: `apps_underwriting_ai/config/domain_contract/grader_roster.yaml`

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
