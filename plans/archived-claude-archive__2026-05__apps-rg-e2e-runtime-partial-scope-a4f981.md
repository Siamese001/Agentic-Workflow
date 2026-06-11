---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-e2e-runtime-partial-scope-a4f981.md'
original_relative_path: '_archive\\2026-05\\apps-rg-e2e-runtime-partial-scope-a4f981.md'
source_sha256: 8a3dabcc2e23bfbe9501e646622e352e642a0d145e90000de3c0329a2f3a1ae0
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-e2e-runtime-partial-scope-a4f981
plan_type: tracker
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg E2E runtime — residual PARTIAL scope (post–competencies X2 GREEN)

Focused follow-up **after competencies deterministic X2 remediation is complete**. Baseline proven elsewhere: **`prove_apps_rg_e2e_runtime.py` exit 0**, competencies lane **deterministic X2 gates GREEN**, **`mock_pass=false`**, **`direct_bypass=false`**, **no `agentic_core` edits**. This plan covers only what still yields **`PARTIAL`** / **`X3B_REVIEW`** on the whole-run packet — **X1D judge execution/quality**, and **product R4 / C0_support / route note** review signals — without reopening competencies X2 weakening.

> **plan_id discipline**: markers use `plan=apps-rg-e2e-runtime-partial-scope-a4f981`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: TODO  
CURRENT_WAVE: W0  
LAST_COMPLETED_WAVE: NONE  
LAST_UPDATED: 2026-05-16  

---

## Context (SCQA)

- **Situation** — Competencies structured format / source_fact traceability is **green under real harness**; `artifacts/ci/apps_rg_e2e_runtime_proof.json` can remain **PARTIAL** while rollup **lifts blockers**.
- **Complication** — Whole-run **`x3_disposition`** trends **REVIEW** when **Gemini** rate-limit/blocked paths, **model-backed decisive/soft failures** on other judges, **`JUDGE_EXECUTION_PROVIDER_MISMATCH`**, **`PRODUCT_R4_BYPASS_PRELOADED_CONTEXT`** (or analogous route note), **C0 support WEAK**/review strings still appear on the packet/c0 summaries.
- **Question** — How do we converge the **remaining non-competencies** signals so the E2E proof **honestly** moves toward **full PASS claim level** where credentials and product stance allow — without mocking judges or weakening gates?
- **Answer** — Two-wave track: **(W1)** X1D provider health + quorum evidence + decisive vs soft remediation in **apps_rg harness/dispatch overlays only**; **(W2)** R4/route/C0-support narrative alignment and re-proof.

---

## Wave summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.P1–W1.P3 | X1D judge stack convergence (cred, retries, quorum semantics) | ~6K | `GEMINI`/`OPENAI`/`ANTHROPIC` keys configurable; no core edits | 🔲 TODO | Per-lane `x1d_llm_judge_outputs.json` shows expected modes; rollup failure breakdown clears **provider blocked** rows where infra allows |
| W2 | W2.P1–W2.P2 | R4 route note / C0 support review + harness artifact honesty | ~4K | C0 spine unchanged unless explicitly scoped | 🔲 TODO | `review_reasons` / `c0_summary` deltas documented OR explicit **NOT_CLAIMING** boundary preserved; reproducible `-- cmd --` in proof |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Credential + env matrix for harness | `README`/`docs`/operator notes, `.env.example` optional | Secrets in chat | ~1K | 🔲 TODO |
| W1.P2 | Judge adapters + bounded retries (lanes) | `apps_rg/runtime/judges/`, lane dispatches **if** app-local | Rate-limit classification drift | ~3K | 🔲 TODO |
| W1.P3 | Rollup diagnostics parity | `x1d_lane_judge_diagnostics` consumers, proof JSON fields | Double-count PASS | ~2K | 🔲 TODO |
| W2.P1 | R4 / route note reconciliation | routing notes in proof packet, AGENTS boundaries | Misleading PASS language | ~2K | 🔲 TODO |
| W2.P2 | C0_support WEAK remediation or explicit acceptance | `prove_apps_rg_c0_runtime`, chroma/evidence thresholds | infra dependency | ~2K | 🔲 TODO |

---

## Out of scope

- **Weakening or removing competencies deterministic X2 gates** (already remediated laneside).
- **Any `agentic_core` refactor** unless a separate **`platform_core_change`** plan and receipt exist.
- **Fabricated `bul_*` / FEC IDs** or satisfying deterministic gates via **X1D judge blobs**.

---

## Definition of Done

| ID | Acceptance | Verification | Done |
|----|-------------|--------------|------|
| DoD-1 | W1 completed with archived judge outputs for ≥1 full harness run under fixed env snapshot | Paths cited in wave note (`artifacts/apps_rg/runtime_proofs/*/real/*/x1d_llm_judge_outputs.json`) | 🔲 |
| DoD-2 | Whole-run packet shows **exactly_one_x3=true** and **block_reasons** either empty or justified as policy | `artifacts/ci/apps_rg_whole_run_exit_review_packet.json` | 🔲 |
| DoD-3 | `prove_apps_rg_e2e_runtime.py` exits **0** after W1/W2 deltas | CLI exit code 0 | 🔲 |
| DoD-4 | Contract pytest slice for judge/exit/hygiene still green | `python -m pytest tests/_apps_contract/test_apps_rg_x1d_* tests/_apps_contract/test_apps_rg_whole_run_exit.py -q -p pytest_timeout` (extend list as touched) exits 0 | 🔲 |
| DoD-5 | **NOT_CLAIMING** list updated vs actual proof (Knox/L5/production corpus/L6 calibration) — no silent upgrade | Narrative paragraph in wave complete note | 🔲 |

**Verification-vs-Deferral table**:

| Item | Why deferred | Tracked in |
|------|----------------|------------|
| Full **PASS** artifact if API quotas persist | External provider SLA; honesty over PASS theater | Deferred scope note on proof `decisive_reason` |
| Live R4 spine swap from bypass | Product/architecture gate outside this tracker | Separate ADR or product plan |

---

## Marker quick reference

```
WAVE_START: plan=apps-rg-e2e-runtime-partial-scope-a4f981 wave=1
WAVE_COMPLETE: plan=apps-rg-e2e-runtime-partial-scope-a4f981 wave=1 note="X1D quorum/cred matrix + judge artifacts archived"
WAVE_COMPLETE: plan=apps-rg-e2e-runtime-partial-scope-a4f981 wave=2 note="R4/C0_support narrative reconciled + harness re-proof"
```

---

## References

- Proof artifacts: `artifacts/ci/apps_rg_e2e_runtime_proof.json`, `artifacts/ci/apps_rg_whole_run_exit_review_packet.json`
- Harness: `ops_scripts/ci/prove_apps_rg_e2e_runtime.py`

