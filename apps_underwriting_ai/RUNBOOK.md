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

## §6 Evidence Sufficiency Gate Triage

**Scope:** the C0 Submitted-Document Evidence Sufficiency Gate
(`integrations/underwriting_c0_adapter.py`, emits `FinalEvidenceContract`).
Case study: `docs/EVIDENCE_SUFFICIENCY_GATE_CASE_STUDY.md`.

> Reproduce locally by instantiating the gate directly and inspecting the contract:
> `UnderwritingC0Adapter().run(submitted_documents, demo_policy_hash=...)`, then
> read `fec.to_dict()`. The gate is deterministic and writes nothing, so triage is safe.

| Symptom | Likely cause | Triage steps | Likely files |
|---|---|---|---|
| **Unexpected `PASS`** | All required classes AND required fields were present, no contradiction fired, and score ≥ 0.80 — confirm that's actually correct. A false PASS usually means a contradiction rule didn't fire (one field missing) or an alias mis-classified a document. | Confirm `fec.missing_evidence_flags == []` (no `MISSING_DOC:`/`MISSING_FIELD:`); inspect `fec.document_coverage_map`; confirm `fec.contradiction_flags == []` is correct; recompute `support_score` from `_compute_support_score_breakdown`. | `underwriting_c0_adapter.py` (`_classify_document`, `_detect_contradictions`, `_required_fields_for_class`, `_compute_support_score_breakdown`) |
| **Unexpected `FAIL`/`WEAK`** | A required class is missing/unclassifiable (`MISSING_DOC:`), or a required field of a present class was not extracted (`MISSING_FIELD:<CLASS>.<field>`) — note PASS now requires required *fields*, not just required document *classes*. | Inspect `fec.missing_evidence_flags` for `MISSING_DOC:`/`MISSING_FIELD:` entries; check each submitted doc has a recognized `document_class`; check the required fields per class in `_DOCUMENT_FIELD_SCHEMA` are actually present (remember `0`/`False` count as present). | `underwriting_c0_adapter.py` (`_classify_document`, `_extract_spans`, `_get_submitted_field_value`) |
| **Contradiction flags present** | Cross-document inconsistency — by design. Confirm it's real, not a unit/scale bug (e.g. monthly vs annual income). | Read `fec.contradiction_flags`; for each flag, pull the two cited fields from `fec.extracted_span_map` and re-apply the threshold by hand (see §7 of the case study). | `underwriting_c0_adapter.py` (`_CONTRADICTION_RULES`, `_detect_contradictions`) |
| **LLM rationale cites missing evidence** | The firewall fell open, or a caller bypassed it. The served rationale should never contain an `ev-…` evidence ID absent from `fec.evidence_ids` — the deterministic citation allowlist rejects those with `failure_reason="unsupported_evidence_id"`. | Check `firewall_result.firewall_passed` / `deterministic_fallback_used` / `failure_reason`; confirm the firewall received the real `FinalEvidenceContract` dict as `c0_bundle` (or, on the legacy path, a no-evidence fallback bundle) and not a raw `feature_summary`; confirm `APPS_UW_FIREWALL_DISABLED` is unset; confirm the rationale went through `DecisionPacketAssembler.run_pa_firewall`/`assemble(c0_bundle=...)` and not a raw LLM call. | `underwriting_llm_firewall.py` (`_validate_c0_bundle`, `_rationale_cites_unknown_evidence`), `engines/decision_packet_assembler.py`, `prompt_assembly/underwriting_pa_compiler.py` |
| **`support_score` changed between runs** | Non-determinism leaked in — dict ordering, an unstable field value, time, or randomness in the input payload. | Run the determinism test (`test_same_input_produces_same_ids_across_runs`); diff `fec.to_dict()` across two runs; confirm the input documents are byte-identical (the score is a pure function of coverage + spans). | `underwriting_c0_adapter.py` (`_compute_support_score_breakdown`, `_compute_contract_id`, `_compute_evidence_id`) |

**Invariants that must always hold (escalate if violated):**
- `fec.open_web_blocked is True` on every contract, in every state.
- Malformed input returns a `FAIL` contract — it must never raise.
- A contradiction flag or a missing required class makes `PASS` unreachable.
- `fec.extracted_span_map` contains only fields that were actually submitted (no inferred fields).

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
