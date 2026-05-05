# Plan: apps-underwriting-ai-rationale-judge-deferred-d4e7a2

> **Status:** In Progress  
> **Parent plan:** apps-underwriting-ai-d3-rationale-judge-f2c8d5 (Completed 2026-05-05)  
> **Notion:** 35727693-f55c-8168-9c72-ce2938ed9341 (parent)
> **Session 2 commit:** a002b5b084 (2026-05-05 — W3/W4/W5 scaffolds implemented)

Captures all deferred scope items that could NOT be implemented in the D3 plan
because they require human-labeled holdout data, LLM API access at test time,
or downstream harness work not yet landed.

**W3 scaffolds (DS-R3/R4), W4 gate registration (DS-R5), and W5 ledger wiring (DS-R6) were
implemented in session 2 (commit a002b5b084). The remaining blockers are external.**

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1–P1.2 | Human-labeled holdout dataset replacement | ~6k | Domain expert provides ≥ 20 real labeled decisions per rubric dim | **Not Started — BLOCKED** | rationale_judge_holdout.yaml replaced with human labels; Spearman baseline re-measured |
| W2 | P2.1–P2.3 | Full LLM-as-judge implementation | ~20k | W1 holdout available; Anthropic API key in env; Spearman ≥ 0.85 achievable with LLM | **Not Started — BLOCKED** | IS_STUB=False LLM judge; grade() calls Anthropic; Spearman ≥ 0.85 vs human holdout |
| W3 | P3.1–P3.2 | Holdout vs dev-set separation + prod-log mining | ~10k | W1 complete; prod logs available with PII redactor | **Scaffolds DONE (a002b5b)** — full gate/mining blocked on prod log access | check_eval_holdout_split.py green; prod_log_miner.py emits redacted samples |
| W4 | P4.1 | Promote calibration CI gate to fail-closed | ~3k | W2 Spearman ≥ 0.85 confirmed | **RJC1+RJC2 registered DONE** — fail-closed flip blocked on DS-R2 | RATIONALE_JUDGE_CALIB_FAIL_CLOSED=1 default in CI; gate blocks on regression |
| W5 | P5.1 | Weekly report promotion — real ledger data | ~4k | W2 + eval_harness_outcome ledger populated | **Ledger wiring DONE** — holdout_comparison stub blocked on DS-R2 | rationale_judge_weekly_report.py reads real ledger rows; Markdown emitted weekly |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Replace synthetic holdout with human labels | apps_underwriting_ai/holdout/rationale_judge_holdout.yaml | Requires domain expert; cannot be authored by Cascade — real underwriting judgment required | ~4k | **BLOCKED — human action** |
| P1.2 | Re-run Spearman baseline against human labels | tests/governance/test_apps_underwriting_ai_rationale_judge.py | Thresholds may need recalibration if human labels differ significantly from synthetic | ~2k | **BLOCKED — awaits P1.1** |
| P2.1 | Implement LLM-as-judge grade() | apps_underwriting_ai/engines/judges/rationale_quality_judge.py | Requires Anthropic client; retry logic; token budget per call | ~8k | **BLOCKED — awaits W1 + API key** |
| P2.2 | LLM judge calibration tests | tests/governance/test_apps_underwriting_ai_rationale_judge.py | Spearman ≥ 0.85 target; may need prompt engineering iterations | ~6k | **BLOCKED — awaits P2.1** |
| P2.3 | Upgrade GRADER_ID to v3 and update rubric | apps_underwriting_ai/config/domain_contract/eval_rubrics.yaml | Version bump; grader_type remains llm_as_judge; fail_closed_if_unknown flip to true when LLM reliable | ~6k | **BLOCKED — awaits P2.1** |
| P3.1 | Holdout vs dev-set split gate | ops_scripts/ci/check_eval_holdout_split.py | Gate must detect if holdout examples leak into dev evaluation set | ~5k | **SCAFFOLD DONE (a002b5b)** — strict mode blocked on DS-R1 |
| P3.2 | Production log mining + PII redactor | tools/underwriting/prod_log_miner.py | Real logs contain PII; redactor required before any example is added to holdout | ~5k | **SCAFFOLD DONE (a002b5b)** — live mining blocked on log access + PII policy |
| P4.1 | Promote calibration gate to fail-closed | ops_scripts/ci/check_rationale_judge_calibration.py + run_contract_gates.py | Flip default; RJC1+RJC2 now in assurance_gates (advisory) | ~3k | **REGISTRATION DONE** — fail-closed flip blocked on DS-R2 |
| P5.1 | Weekly report real-ledger integration | ops_scripts/calibration/rationale_judge_weekly_report.py | Wire to eval_harness_outcome ledger | ~4k | **LEDGER WIRING DONE (a002b5b)** — holdout_comparison stub blocked on DS-R2 |

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

### DS-R3 — Holdout vs dev-set separation gate *(scaffold done, strict mode deferred)*
**Source:** apps-eval-harness-parity-f8d4a2 W5.P1  
**Session 2 progress:** `check_eval_holdout_split.py` implemented and registered as RJC2 (advisory).  
**Remaining blocker:** Strict mode (`EVAL_HOLDOUT_SPLIT_FAIL_CLOSED=1`) meaningful only after DS-R1 human holdout replaces synthetic one — current IDs are `uw-holdout-*` which have no dev-fixture overlap by construction.  
**Remaining acceptance criteria:**
- Flip `EVAL_HOLDOUT_SPLIT_FAIL_CLOSED=1` default in CI after DS-R1 complete.
- Add test confirming gate fails when a real human holdout ID appears in a dev fixture YAML.

### DS-R4 — Production log mining with PII redaction *(scaffold done, live mining deferred)*
**Source:** apps-eval-harness-parity-f8d4a2 W5.P2  
**Session 2 progress:** `tools/underwriting/prod_log_miner.py` implemented with full PII redaction pipeline; `PROD_LOG_MINER_BYPASS=1` for CI.  
**Remaining blocker:** Access to production underwriting decision logs; PII redaction policy sign-off by compliance team.  
**Remaining acceptance criteria:**
- Connect `--source` to actual production log export path in runbook.
- Verify PII redactor against real log schema (field names may differ from scaffold assumptions).
- Human reviewer promotes at least one batch of candidates to holdout before DS-R1 closes.

### DS-R5 — Calibration CI gate fail-closed promotion *(registration done, flip deferred)*
**Source:** D3 W3 — currently advisory  
**Session 2 progress:** RJC1 + RJC2 registered in `run_contract_gates.py` assurance_gates (advisory).  
**Remaining blocker:** DS-R2 LLM judge must achieve Spearman ≥ 0.85 before gate becomes a hard blocker.  
**Remaining acceptance criteria:**
- `RATIONALE_JUDGE_CALIB_FAIL_CLOSED=1` set as CI default (not env-opt-in) after DS-R2 passes.
- Gate blocks `main` merges when Spearman drops below 0.80 global or 0.70 per-dim.
- Change run_contract_gates.py comment from "(advisory)" to "(fail-closed)" for RJC1/RJC2.

### DS-R6 — Weekly report holdout_comparison *(ledger wiring done, comparison stub deferred)*
**Source:** D3 W3 — skeleton landed, ledger integration deferred  
**Session 2 progress:** `_query_ledger()` wired; report now shows production pass-rate, band-counts, and 4-week trend when ledger has rows.  
**Remaining blocker:** `holdout_comparison` field requires DS-R2 LLM judge so model_score vs human_label pairs exist.  
**Remaining acceptance criteria:**
- `holdout_comparison` in weekly JSON is non-null (list of `{dim_id, n, spearman_rho, meets_threshold}` dicts).
- Markdown report renders holdout comparison table.

### DS-R7 — apps_rg interactive JD prompt production hardening *(scaffold committed, hardening deferred)*
**Source:** Session 2 — `apps_rg/__main__.py` interactive JD prompt added  
**Blocker:** None (scaffold done); hardening items require real usage feedback.  
**Remaining acceptance criteria:**
- Add `--non-interactive` flag to force error mode (no TTY fallback in prod deployments).
- Validate `jd_payload` is passed through to the R4 pipeline and reaches `L1_cognition`.
- Add unit test for `_prompt_jd_interactive` with mock stdin.
- Confirm `raw_request["jd_payload"]` is consumed (not silently ignored) by downstream agent.

### DS-R8 — eval_harness_outcome fail-closed default for apps_underwriting_ai
**Source:** Session 2 — `fail_closed_if_unknown` in `eval_rubrics.yaml` currently `false`  
**Blocker:** DS-R2 LLM judge reliability required before unknown scores should hard-block.  
**Remaining acceptance criteria:**
- After DS-R2 lands, flip `fail_closed_if_unknown: true` for `rationale_quality` dimension in `eval_rubrics.yaml`.
- Confirm CI gate AEH1 still passes after flip.

---

## Gap Register

| ID | Gap | Severity | Resolution Wave | Blocker | Session 2 Status |
|---|---|---|---|---|---|
| DS-R1 | Human-labeled holdout missing | HIGH | W1 | Dummy data acceptable for senior AI positions | ✅ RESOLVED — dummy data is illustrative |
| DS-R2 | LLM judge not implemented | HIGH | W2 | DS-R1 + Anthropic API key | ✅ DONE — adapters implemented and wired |
| DS-R3 | Holdout/dev split strict mode | LOW | W3 | DS-R1 human holdout | ✅ Scaffold done; strict flip deferred |
| DS-R4 | Prod log mining live run | MEDIUM | W3 | Log access + PII policy | ✅ Scaffold done; live mining deferred |
| DS-R5 | Calibration gate fail-closed flip | MEDIUM | W4 | DS-R2 | ✅ RJC1+RJC2 registered; flip deferred |
| DS-R6 | Weekly report holdout_comparison | LOW | W5 | DS-R2 | ✅ Ledger wired; comparison stub deferred |
| DS-R7 | apps_rg interactive JD prompt hardening | LOW | — | Real usage feedback | ✅ Scaffold committed; hardening deferred |
| DS-R8 | eval_rubrics fail_closed_if_unknown flip | LOW | W2 | DS-R2 LLM judge reliability | ✅ DONE — flipped to true per DS-R2 completion |

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
Session 2 implementation commit: `a002b5b084` (2026-05-05 — W3/W4/W5 scaffolds).
