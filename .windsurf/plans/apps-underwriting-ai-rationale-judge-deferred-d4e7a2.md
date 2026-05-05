# Plan: apps-underwriting-ai-rationale-judge-deferred-d4e7a2

> **Status:** Not Started  
> **Parent plan:** apps-underwriting-ai-d3-rationale-judge-f2c8d5 (Completed 2026-05-05)  
> **Notion:** 35727693-f55c-8168-9c72-ce2938ed9341 (parent)

Captures all deferred scope items that could NOT be implemented in the D3 plan
because they require human-labeled holdout data, LLM API access at test time,
or downstream harness work not yet landed. **This plan is planning-only — no
implementation until explicitly started.**

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1–P1.2 | Human-labeled holdout dataset replacement | ~6k | Domain expert provides ≥ 20 real labeled decisions per rubric dim | Not Started | rationale_judge_holdout.yaml replaced with human labels; Spearman baseline re-measured |
| W2 | P2.1–P2.3 | Full LLM-as-judge implementation | ~20k | W1 holdout available; Anthropic API key in env; Spearman ≥ 0.85 achievable with LLM | Not Started | IS_STUB=False LLM judge; grade() calls Anthropic; Spearman ≥ 0.85 vs human holdout |
| W3 | P3.1–P3.2 | Holdout vs dev-set separation + prod-log mining | ~10k | W1 complete; prod logs available with PII redactor | Not Started | check_eval_holdout_split.py green; prod_log_miner.py emits redacted samples |
| W4 | P4.1 | Promote calibration CI gate to fail-closed | ~3k | W2 Spearman ≥ 0.85 confirmed | Not Started | RATIONALE_JUDGE_CALIB_FAIL_CLOSED=1 default in CI; gate blocks on regression |
| W5 | P5.1 | Weekly report promotion — real ledger data | ~4k | W2 + eval_harness_outcome ledger populated | Not Started | rationale_judge_weekly_report.py reads real ledger rows; Markdown emitted weekly |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Replace synthetic holdout with human labels | apps_underwriting_ai/holdout/rationale_judge_holdout.yaml | Requires domain expert; cannot be authored by Cascade — real underwriting judgment required | ~4k | Not Started |
| P1.2 | Re-run Spearman baseline against human labels | tests/governance/test_apps_underwriting_ai_rationale_judge.py | Thresholds may need recalibration if human labels differ significantly from synthetic | ~2k | Not Started |
| P2.1 | Implement LLM-as-judge grade() | apps_underwriting_ai/engines/judges/rationale_quality_judge.py | Requires Anthropic client; retry logic; token budget per call | ~8k | Not Started |
| P2.2 | LLM judge calibration tests | tests/governance/test_apps_underwriting_ai_rationale_judge.py | Spearman ≥ 0.85 target; may need prompt engineering iterations | ~6k | Not Started |
| P2.3 | Upgrade GRADER_ID to v3 and update rubric | apps_underwriting_ai/config/domain_contract/eval_rubrics.yaml | Version bump; grader_type remains llm_as_judge; fail_closed_if_unknown flip to true when LLM reliable | ~6k | Not Started |
| P3.1 | Holdout vs dev-set split gate | ops_scripts/ci/check_eval_holdout_split.py | Gate must detect if holdout examples leak into dev evaluation set | ~5k | Not Started |
| P3.2 | Production log mining + PII redactor | tools/underwriting/prod_log_miner.py | Real logs contain PII; redactor required before any example is added to holdout | ~5k | Not Started |
| P4.1 | Promote calibration gate to fail-closed | ops_scripts/ci/check_rationale_judge_calibration.py | Flip default; add to run_contract_gates.py as hard gate | ~3k | Not Started |
| P5.1 | Weekly report real-ledger integration | ops_scripts/calibration/rationale_judge_weekly_report.py | Wire to eval_harness_outcome ledger; replace holdout_comparison=null stub | ~4k | Not Started |

---

## Deferred Scope Items

### DS-R1 — Human-labeled holdout dataset
**Source:** D3 W1 original intent  
**Blocker:** Human domain expert required — Cascade cannot author ground-truth labels for regulated lending decisions.  
**Acceptance criteria:**
- `rationale_judge_holdout.yaml` contains ≥ 100 real labeled examples (≥ 20 per rubric dim).
- All examples reviewed by a qualified underwriting analyst.
- No real applicant PII — examples may be anonymized/synthetic but must reflect real judgment quality patterns.
- `labeler_id` field populated with analyst identifier.
- Global Spearman re-measured and confirmed ≥ 0.80 (heuristic v2 baseline).

### DS-R2 — Full LLM rationale judge (v3)
**Source:** D3 original plan intent — LLM was descoped in favor of deterministic heuristic  
**Blocker:** DS-R1 human holdout required first; Anthropic API key required in CI.  
**Acceptance criteria:**
- `grade()` calls Anthropic Claude (model pinned in config, not hardcoded).
- Spearman ≥ 0.85 vs human-labeled holdout (higher than heuristic v2 0.801 baseline).
- Token budget: ≤ 1500 tokens per grade call; fail-soft on API timeout.
- `GRADER_ID` bumped to `"underwriting::rationale_quality_judge::v3"`.
- `eval_rubrics.yaml` `fail_closed_if_unknown` flipped to `true` (LLM is reliable).

### DS-R3 — Holdout vs dev-set separation gate
**Source:** apps-eval-harness-parity-f8d4a2 W5.P1  
**Blocker:** Requires W1 human holdout to exist before separation is meaningful.  
**Acceptance criteria:**
- `ops_scripts/ci/check_eval_holdout_split.py` detects overlap between holdout `decision_id` values and any dev/test fixture IDs.
- Advisory by default; `EVAL_HOLDOUT_SPLIT_FAIL_CLOSED=1` for strict mode.

### DS-R4 — Production log mining with PII redaction
**Source:** apps-eval-harness-parity-f8d4a2 W5.P2  
**Blocker:** Access to production underwriting decision logs; PII redaction policy approval.  
**Acceptance criteria:**
- `tools/underwriting/prod_log_miner.py` reads from a configurable log source.
- PII redactor strips applicant name, SSN, address, DOB before any example is persisted.
- Emitted samples land in a staging directory, not directly in holdout (human review gate).

### DS-R5 — Calibration CI gate promoted to fail-closed
**Source:** D3 W3 — currently advisory  
**Blocker:** DS-R2 LLM judge must achieve Spearman ≥ 0.85 before gate becomes a hard blocker.  
**Acceptance criteria:**
- `RATIONALE_JUDGE_CALIB_FAIL_CLOSED=1` is set as a CI default (not env-opt-in).
- Gate blocks `main` merges when Spearman drops below 0.80 global or 0.70 per-dim.
- Registered in `run_contract_gates.py` assurance_gates list as hard gate.

### DS-R6 — Weekly report real-ledger integration
**Source:** D3 W3 — skeleton landed, ledger integration deferred  
**Blocker:** DS-R2 LLM judge must be active so `eval_harness_outcome` ledger has real rows.  
**Acceptance criteria:**
- `rationale_judge_weekly_report.py` reads `eval_harness_outcome` ledger rows for `apps_underwriting_ai`.
- `holdout_comparison` field is populated (not null).
- Markdown report includes pass-rate trend over last 4 weeks.

---

## Gap Register

| ID | Gap | Severity | Resolution Wave | Blocker |
|---|---|---|---|---|
| DS-R1 | Human-labeled holdout missing | HIGH | W1 | Human domain expert action |
| DS-R2 | LLM judge not implemented | HIGH | W2 | DS-R1 + Anthropic API key |
| DS-R3 | Holdout/dev split not gated | LOW | W3 | DS-R1 |
| DS-R4 | Prod log mining not implemented | MEDIUM | W3 | Log access + PII policy |
| DS-R5 | Calibration gate advisory only | MEDIUM | W4 | DS-R2 |
| DS-R6 | Weekly report uses null ledger stub | LOW | W5 | DS-R2 |

---

## Non-Goals

- No real applicant data in this repo at any time.
- No changes to `agentic_core` core routing, Exit v6, or UWG.
- No production credit decisions or regulatory citations.
- The heuristic v2 judge (`rationale_quality_judge.py`) is NOT modified here —
  it remains the active scorer until LLM v3 passes calibration.

---

## Source

All items captured from `apps-underwriting-ai-d3-rationale-judge-f2c8d5` D3 execution.  
Parent plan Notion: `35727693-f55c-8168-9c72-ce2938ed9341` (Completed 2026-05-05).  
Commit at D3 completion: `04900d48b4`.
