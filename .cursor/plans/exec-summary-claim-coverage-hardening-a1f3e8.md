---
plan_id: exec-summary-claim-coverage-hardening-a1f3e8
plan_type: bugfix
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
dod_exempt: false
parent_rca_run: exec_summary_20260526_183905
---

# Executive summary — claim coverage hardening & X2 alignment

Close the Brown `exec_summary_20260526_183905` proof failures caused by **(A)** `build_sentence_claim_coverage` matching only `claim_text` (false UNSUPPORTED on paraphrased S5) and **(B)** no deterministic enforcement that six display sentences each have a ledger row (model left S6 uncovered; `self_check` honor-system only).

> **plan_id:** `exec-summary-claim-coverage-hardening-a1f3e8`  
> **RCA run:** [exec_summary_20260526_183905](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_183905)  
> **Related doc:** [executive_summary_24k_context_budget_rationalization_20260526.md](../../docs/reports/apps_rg/executive_summary_24k_context_budget_rationalization_20260526.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: COMPLETED  
CURRENT_WAVE: none  
LAST_COMPLETED_WAVE: W4  
LAST_UPDATED: 2026-05-26  

PLAN_CREATED: slug=exec-summary-claim-coverage-hardening-a1f3e8 path=.cursor/plans/exec-summary-claim-coverage-hardening-a1f3e8.md status=Not Started

---

## Context (SCQA)

| | |
|---|---|
| **Situation** | Exec summary runs at 24k with `dispatch_allowed: true`; Brown run `REAL_LLM` then **X3_BLOCK** on X2 (`x2_unsupported_claim_zero`, `x2_sentence_coverage_pass`, accounting gates). |
| **Complication** | One failure is a **checker bug** (S5 had `fact_quant_hpc_003` in ledger but coverage used `claim_text` tokens only). One is **model output** (6 sentences, 5 ledger rows; S6 forward prose). `self_check.every_material_claim_in_claim_ledger` is **not** enforced by X2. |
| **Question** | Harden coverage + add gates/tests so paraphrase+fact rows pass and display/ledger drift fails deterministically. |
| **Answer** | Fix matcher in `executive_summary_x2.py`; add narrow X2 gates; regression tests from Brown-shaped fixture; optional X3 label clarity (separate wave). |

---

## Status Tables

### Wave Progress

| Wave | Focus | Status |
|------|--------|--------|
| W0 | Coverage matcher fix (`claim` + `claim_text`) | Done |
| W1 | X2 gates: sentence↔ledger alignment + self_check cross-check | Done |
| W2 | X3 empty-judge mode label (no API-failure overclaim) | Done |
| W3 | Unit/contract tests + Brown fixture | Done |
| W4 | Live Brown re-run proof | Done |

### Root cause → seam map

| RCA item | Layer | Primary file |
|----------|--------|----------------|
| S5 false UNSUPPORTED (paraphrase + fact row) | Coverage → X2 | `apps_rg/runtime/validators/executive_summary_x2.py` `build_sentence_claim_coverage` |
| S6 no ledger row | L2 output (model) + missing gate | `executive_summary_lane.py`; new X2 gate |
| `self_check` lies | Prompt only today | new X2 gate reads `parsed_output.self_check` vs coverage |
| Misleading `x1d_evaluator_mode` | X3 aggregate | `apps_rg/runtime/exit/executive_summary_x3.py` |

---

## Scope

### In scope

- `apps_rg/runtime/validators/executive_summary_x2.py` — coverage matcher + new gates
- `apps_rg/runtime/exit/executive_summary_x3.py` — empty `x1d_judges` mode string (W2)
- `tests/_apps_contract/test_exec_summary_x2_product_gates.py` — extend + Brown regression
- `tests/unit/apps_rg/runtime/validators/` — focused unit tests if cleaner than contract-only
- Optional: short RCA addendum under `docs/reports/apps_rg/`

### Out of scope (defer)

- I0/U0 prompt rewrites to “fix” model S6 behavior (gates + regen messages only if W1 adds gate without prompt change)
- `agentic_core` judge panel / spine changes
- Weakening X2 thresholds or deleting accounting gates
- Running X1D before first X2 (lane order unchanged)

### Immutable constraints

- No edits under `agentic_core/`
- Do not weaken gates/fixtures to greenwash Brown output
- PASS on W4 requires live Qwen + unchanged 24k Docker/`VLLM_MAX_MODEL_LEN`

---

## SR_PLAN — Technical approach

### W0 — Coverage matcher (checker bug)

**Problem:** Matcher loops `claim_text` only; R0 allows `claim` (display line) + `claim_text` (fact line). Brown S5 matched zero rows.

**Change:** In `build_sentence_claim_coverage`:

1. For each ledger row, build match candidates from **both** `claim` and `claim_text` (non-empty), same token-overlap heuristic as today.
2. Prefer row where `claim` (normalized) equals / high-overlap with `sentence_text` when multiple rows hit (tie-break: row with `claim` field match wins).
3. When attaching `material_claims`, keep emitting fact `claim_text` + `source_fact_ids` for X2 orphan checks (unchanged consumer shape).
4. Document in function docstring: display↔ledger binding uses `claim` first, fact proof via `claim_text`.

**Acceptance:**

- Brown-shaped fixture: S5 display + ledger row with `fact_quant_hpc_003` → `sentence_pass: true`, `overall_pass: true` (other sentences satisfied).
- Existing `test_valid_synthesis_coverage_and_material_clauses` still passes.

---

### W1 — X2 enforcement gates

**Problem:** Model can emit 6 sentences and 5 ledger rows; `self_check.every_material_claim_in_claim_ledger: true` is never validated.

**Add gates** (names tentative; wire in `run_x2_gates` + `section_product_shape_ssot` if required):

| Gate ID | Rule |
|---------|------|
| `x2_claim_ledger_row_count_matches_sentence_count` | `len(split_sentences(resume_display_text)) == len(claim_ledger)` (strategy lane only if already gated elsewhere). |
| `x2_self_check_claim_ledger_consistent` | If `self_check.every_material_claim_in_claim_ledger is True` → require `text_claim_coverage.overall_pass`; else fail with explicit reason. |
| (optional) `x2_claim_field_maps_to_display_sentence` | Each ledger row with non-empty `claim` must `ledger_row_materialized_in_display(claim, resume)` (reuse existing helper). |

**Lane:** No change to X2-before-X1D order. Failed new gates still skip judge panel (by design).

**Synthesis regen:** If `retry_qwen_for_synthesis` reject reasons include ledger/sentence mismatch, add one reject reason in `_synthesis_shape_reject_reason` when row count ≠ sentence count (read after parse, before coverage) — only if W1 gate proves noisy without it.

---

### W2 — X3 label clarity (secondary)

**Problem:** `x1d_judges=[]` → `x1d_evaluator_mode=BLOCKED_PROVIDER_UNAVAILABLE` implies API down.

**Change:** In `aggregate_x3`, when `not x1d_judges`, set `x1d_evaluator_mode` to e.g. `NO_JUDGE_ROWS_EMITTED` (new enum string); keep `BLOCKED_PROVIDER_UNAVAILABLE` only when `_is_blocked_judge(j)` true.

**Tests:** `tests/unit/apps_rg/runtime/exit/test_executive_summary_x3.py` or extend existing x3 tests.

**Docs:** One line in [executive_summary_operator_guide.md](../../docs/apps_rg/executive_summary_operator_guide.md) field glossary.

---

### W3 — Tests

| Test | File | Asserts |
|------|------|---------|
| Brown S5 paraphrase regression | `tests/_apps_contract/test_exec_summary_x2_product_gates.py` | Fixture from `provider_response.json` S5/S6 pattern; after W0, S5 supported |
| S6 missing row | same | 6 sentences, 5 rows → `overall_pass false`; W1 gate fails |
| `claim` field match | new or same | Row with only `claim` matching display, unrelated `claim_text` |
| X3 empty judges | `tests/.../test_executive_summary_x3.py` | `[]` judges → `NO_JUDGE_ROWS_EMITTED`, not `BLOCKED_PROVIDER_UNAVAILABLE` |
| No regression | `test_exec_summary_x2_product_gates.py` full file | all existing green |

**Fixture source:** Copy minimal strings from [exec_summary_20260526_183905/parsed_output.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_183905/parsed_output.json) (no secrets).

---

### W4 — Live proof

**Pre:** Docker `local-qwen-vllm` @ 24576 + HF cache volume; `VLLM_MAX_MODEL_LEN=24576`.

```powershell
$env:VLLM_MAX_MODEL_LEN = '24576'
$env:APPS_RG_EXEC_SUMMARY_VERIFY_VLLM_CONTEXT_WINDOW = '1'

python -m apps_rg --section executive_summary `
  --target-company "Brown & Brown" `
  --target-role "SVP IT Strategy & Innovation" `
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd_exec.txt `
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md
```

**PASS criteria (this plan):**

| Artifact | Expectation after hardening |
|----------|----------------------------|
| `text_claim_coverage.json` | S5 not falsely UNSUPPORTED if ledger row present |
| `x2_gate_outputs.json` | No fail on `x2_unsupported_claim_zero` for S5-only bug |
| X2 overall | May still BLOCK on S6 / self_check / model quality — honest |
| `x1d_llm_judge_outputs.json` | Judges run **only if** first-pass X2 clean |

**PARTIAL acceptable:** X2 still blocks on real model gaps (S6), but S5 checker false negative gone + new gates fire with clear reasons.

---

## Verification commands (per wave)

```bash
# W0 + W3
python -m pytest tests/_apps_contract/test_exec_summary_x2_product_gates.py -q

# W1 (after gate registration)
python -m pytest tests/unit/apps_rg/runtime/validators/ -k executive_summary -q

# W2
python -m pytest tests/unit/apps_rg/runtime/exit/ -k x3 -q

# W4 (integration)
# command block above; inspect token_budget_receipt.json + text_claim_coverage.json
```

---

## Definition of Done (plan)

- [x] W0 merged; Brown S5 fixture passes coverage
- [x] W1 gates registered; tests for 6 vs 5 rows and self_check cross-check
- [x] W2 X3 label + test (or DEFERRED with marker if user defers)
- [x] All scoped pytest green with command output in receipt
- [x] W4 live run artifact path recorded; status PASS or PARTIAL with explicit remaining failures
- [x] Short report: [exec_summary_claim_coverage_hardening_receipt_20260526.md](../../docs/reports/apps_rg/exec_summary_claim_coverage_hardening_receipt_20260526.md)

---

## Risks

| Risk | Mitigation |
|------|------------|
| Dual-field match too loose → false SUPPORTED | Require valid `source_fact_ids` unchanged; add test with wrong fact id |
| Stricter row-count gate flakes on non-strategy lanes | Gate only when `is_strategy_executive_target_title` |
| X3 enum drift in downstream consumers | Grep `BLOCKED_PROVIDER_UNAVAILABLE` consumers; update tests only |

---

## Deferred (not in this plan)

```
DEFERRED_SCOPE: plan=exec-summary-claim-coverage-hardening-a1f3e8 wave=backlog gap="Invoke X1D on X2-fail for advisory-only panel" impact=product
```

Lane order change (judges despite X2 fail) is a **product decision**, not part of this bugfix plan.

---

PLAN_COMPLETE: plan=exec-summary-claim-coverage-hardening-a1f3e8 note="W0-W4 done; Brown RCA hardening; 83 pytest + live W4 exec_summary_20260526_191701; receipts exec_summary_claim_coverage_hardening_receipt_20260526.md + exec_summary_e2e_test_receipt_20260526.md"
