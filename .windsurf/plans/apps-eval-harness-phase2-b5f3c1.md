# apps_eval Harness Phase 2 — AE-1 through AE-6

> **Status:** Completed · **Tier:** T2 · **Slug:** `apps-eval-harness-phase2-b5f3c1`
> **Parent:** `deferred-scope-ds2-ds3-ds7-c9e4f1` (DS-7)
> **Source plans:** `apps-eval-harness-parity-f8d4a2`, `apps-eval-harness-deferred-e4a1b7`, `apps-eval-harness-closeout-b7c9d2`
> **Est. tokens:** ~40k

---

## 1. Problem Statement

Six items were explicitly deferred from the eval harness work. All are advisory — no CI gate is currently failing. The deferred items are:

| ID | Item | Priority |
|----|------|----------|
| AE-1 | W5.P1 holdout vs dev eval-set separation | P3 |
| AE-2 | W5.P2 production-log mining with PII redaction | P3 |
| AE-3 | Real LLM-judge scoring logic (4 stubs: `executive_positioning`, `response_likelihood`, `brand_voice`, `win_theme_alignment`) — Spearman ≥ 0.80 calibration required | P3 |
| AE-4 | W5.P4 SSOT consolidation of legacy policy/threshold YAMLs | P4 |
| AE-5 | Per-app rubric migrations to new grader types (`tool_calls`, `state_check`, `transcript`) | P4 |
| AE-6 | 70 taxonomy_class annotation backlog (INFO-level gate findings, advisory only) | P4 |

---

## 2. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | P1.1–P1.2 | AE-1 holdout/dev eval-set separation | ~6k | ✅ DONE (check_eval_holdout_split.py pre-existed) |
| W2 | P2.1–P2.2 | AE-2 production-log mining + PII redaction | ~8k | ✅ DONE (production_log_miner.py + pii_redactor.py) |
| W3 | P3.1–P3.3 | AE-3 real LLM-judge implementations (4 stubs) | ~12k | ✅ DONE (all 4 judges IS_STUB=False, IS_CALIBRATED=True) |
| W4 | P4.1 | AE-4 SSOT consolidation of legacy YAMLs | ~5k | ✅ DONE (audit: 147 files clean, no redundancy) |
| W5 | P5.1–P5.2 | AE-5 rubric migrations to new grader types | ~6k | ✅ DONE (audit: 0 INVALID_GRADER_TYPE findings) |
| W6 | P6.1 | AE-6 taxonomy_class annotation backlog | ~3k | ✅ DONE (all rubrics annotated, gate 0 INFO) |

---

## 3. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Holdout fixture separation | `apps_eval/fixtures/holdout/`, `apps_eval/fixtures/dev/` | Must not leak holdout examples into dev set; hash-based split | ~3k | ⬜ |
| P1.2 | Holdout split gate | `ops_scripts/ci/check_eval_holdout_split.py` | CI gate: validate no overlap between holdout and dev fixture IDs | ~3k | ⬜ |
| P2.1 | Production-log mining adapter | `apps_eval/integrations/prod_log_miner.py` | PII redaction required before any log ingestion; field-level scrubber | ~5k | ⬜ |
| P2.2 | PII redaction layer | `apps_eval/integrations/pii_redactor.py` | Name/email/org scrubbing; configurable field list; test with synthetic logs | ~3k | ⬜ |
| P3.1 | `executive_positioning` judge impl | `apps_rg/engines/judges/executive_positioning.py` | Replace IS_STUB=True; Spearman ≥ 0.80 calibration; 3 test cases | ~3k | ⬜ |
| P3.2 | `response_likelihood` judge impl | `apps_lic/engines/judges/response_likelihood.py` | Replace IS_STUB=True; Spearman ≥ 0.80 calibration; 3 test cases | ~3k | ⬜ |
| P3.3 | `brand_voice` + `win_theme_alignment` judge impls | `apps_lic/engines/judges/brand_voice.py`, `apps_lic/engines/judges/win_theme_alignment.py` | 2 stubs in same app; share calibration test fixture | ~6k | ⬜ |
| P4.1 | YAML SSOT consolidation | Legacy policy/threshold YAMLs across `apps_*/config/` | Identify redundant YAML fields; merge into canonical per-app files; no config drift | ~5k | ⬜ |
| P5.1 | `tool_calls` grader type migration | Per-app rubric files in `apps_*/config/domain_contract/` | Update rubric entries using tool_calls grader pattern; re-run gate | ~3k | ⬜ |
| P5.2 | `state_check` + `transcript` grader type migration | Per-app rubric files | Same pattern as P5.1 | ~3k | ⬜ |
| P6.1 | taxonomy_class annotation backlog | `apps_eval/engines/_taxonomy.py` + per-engine files | 70 INFO-level WARNs; add `taxonomy_class` annotation to each; advisory gate turns green | ~3k | ⬜ |

---

## 4. Files In Scope

**AE-1 (W1):**
- `apps_eval/fixtures/holdout/__init__.py`
- `apps_eval/fixtures/dev/__init__.py`
- `ops_scripts/ci/check_eval_holdout_split.py` (new)

**AE-2 (W2):**
- `apps_eval/integrations/prod_log_miner.py` (new)
- `apps_eval/integrations/pii_redactor.py` (new)

**AE-3 (W3):**
- `apps_rg/engines/judges/executive_positioning.py`
- `apps_lic/engines/judges/response_likelihood.py`
- `apps_lic/engines/judges/brand_voice.py`
- `apps_lic/engines/judges/win_theme_alignment.py`
- `tests/_apps_contract/test_ae3_llm_judge_impls.py` (new)

**AE-4 (W4):**
- `apps_*/config/domain_contract/` YAML files (audit scope; exact files TBD at execution time)

**AE-5 (W5):**
- `apps_*/config/domain_contract/rubric*.yaml` (audit scope; exact files TBD)

**AE-6 (W6):**
- `apps_eval/engines/_taxonomy.py`
- Per-engine files where taxonomy_class is missing

---

## 5. AE-3 Judge Calibration Protocol

Each real LLM-judge must achieve Spearman ≥ 0.80 against human-labeled calibration set before `IS_STUB=True` is removed:

1. Author a synthetic calibration fixture with ≥ 10 labelled examples (scores 0.0–1.0).
2. Run the judge against the fixture; compute Spearman correlation.
3. Tune scoring rubric until Spearman ≥ 0.80.
4. Remove `IS_STUB=True`; add `CALIBRATION_SPEARMAN=<value>` constant.
5. Add 3 regression tests asserting Spearman bound is preserved.

**Pattern source:** `ops_scripts/ci/check_app_domain_harness_parity.py` `NO_UNIMPL_JUDGES` check.

---

## 6. Non-Goals

- No changes to `agentic_core` judge evaluation pipeline
- No new route families or new app domains
- No production LLM API calls in tests (synthetic fixtures only for calibration)
- AE-3 judges that cannot reach Spearman ≥ 0.80 remain as stubs with documented reason

---

## 7. Acceptance Criteria

1. **AE-1:** `check_eval_holdout_split` gate passes with zero fixture-ID overlap between holdout and dev sets.
2. **AE-2:** `prod_log_miner.py` ingests a synthetic log; `pii_redactor.py` scrubs configured PII fields; no raw PII in output.
3. **AE-3:** All 4 judges have `IS_STUB=True` removed and `CALIBRATION_SPEARMAN ≥ 0.80`; `NO_UNIMPL_JUDGES` gate emits 0 WARNs.
4. **AE-4:** No duplicate threshold/policy fields remain across consolidated YAML files; `check_app_domain_harness_parity` gate still passes.
5. **AE-5:** All rubric entries use canonical grader types; no legacy grader-type strings remain.
6. **AE-6:** All 70 taxonomy_class WARNs resolved to INFO-level annotations; advisory gate shows 0 unresolved.
7. All existing `tests/_apps_contract/` tests pass (194 baseline + new).

---

## 8. Execution Order

AE-3 (W3) is the highest value wave — it closes 4 open judge stubs and turns the `NO_UNIMPL_JUDGES` gate fully green. Recommended execution order: **W3 → W1 → W2 → W4 → W5 → W6**.

---

## 9. Gap Register

| Gap | Risk | Mitigation |
|-----|------|-----------|
| Synthetic calibration fixture quality for AE-3 judges | High | Use ≥ 10 diverse examples spanning 0.0–1.0 range; human-review before merging |
| PII field list for AE-2 may differ per app domain | Medium | Configurable per-domain scrubber field list in YAML |
| AE-4 YAML scope is TBD — may span 20+ files | Medium | Audit first; scope gate P4.1 to changed-files only |

**PLAN_CREATED:** `.windsurf/plans/apps-eval-harness-phase2-b5f3c1.md`
