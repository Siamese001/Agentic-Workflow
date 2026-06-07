---
plan_id: exec-summary-regen-stuck-c0-split-a4f8e2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: artifacts/cursor/author_gate/complete_open_scope_spec.json
dod_exempt: false
---

# Executive Summary — Regen Stuck-Loop + C0 claim/proof Split

Fix the two defects exposed by Brown SVP run `exec_summary_20260526_230615`: (1) judge-regen burns all 10 cycles on the same `x2_claim_field_maps_to_display_sentence` failure because `regen_converged` only catches exact hash repetition; (2) two C0 facts carry `claim_text` that I0 bans in display while X2 requires verbatim materialization, creating a structural contradiction the regen loop cannot resolve.

> **plan_id discipline:** `exec-summary-regen-stuck-c0-split-a4f8e2`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: DONE
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-27  

NOTION_PAGE_ID: 36d27693-f55c-81d7-847a-c34cd7807849  
NOTION_PLAN_URL: https://www.notion.so/exec-summary-regen-stuck-c0-split-a4f8e2-36d27693f55c81d7847ac34cd7807849  
PLAN_CREATED: slug=exec-summary-regen-stuck-c0-split-a4f8e2 path=.cursor/plans/exec-summary-regen-stuck-c0-split-a4f8e2.md status=Not Started notion_page=36d27693-f55c-81d7-847a-c34cd7807849

---

## Context (SCQA)

- **Situation** — Judge regen control-loop ([f8a3c2](_archive/2026-05/exec-summary-judge-regen-control-loop-f8a3c2.md), COMPLETE) hardened G0–G5 monotonicity + best-of publish. Convergence guard ([e7c4b2](exec-summary-failed-run-persistence-notion-e7c4b2.md) W5.2) ships as `REGEN_STOPPED_REASON_CONVERGED = "regen_converged"` at [executive_summary_regen_observability.py:92](../../apps_rg/runtime/sections/executive_summary_regen_observability.py).
- **Complication** — Brown run `exec_summary_20260526_230615` burned all 10 regen cycles on the **same** `x2_claim_field_maps_to_display_sentence` failure (rows 1+5). At Qwen `T=0.45`, each cycle's `regen_output_hash` differs slightly so `regen_converged` never fires; G3 monotonicity never engages because the X2 stop-gate fails first. Separately, two C0 facts (`fact_engineering_platform_001` mechanism inventory; `fact_quant_hpc_003` employer + FSA credential stack) carry `claim_text` that I0 (`credential_policy_v1` + `neg_mechanism_inventory_001`) explicitly bans in display — X2 verbatim-display matching cannot succeed regardless of regen quality.
- **Question** — How do we make the regen loop fail-fast on truly stuck X2 failures **and** make the fact ledger structurally compatible with the I0 / X2 contract — without weakening any gate or reopening f8a3c2?
- **Answer** — (W1) Add a `x2_stuck_same_failure` early-exit when `failing_gate_ids` + row indexes repeat ≥ N=2 cycles, recorded as `stopped_reason` in the cycles receipt and surfaced in `regen_lane_stats`. (W2) Split the fact schema into `claim_text` (display-allowed paraphrase, what X2 matches) and `proof_text` (full body, source binding only); migrate the two offending facts. (W3) Re-run Brown canonical CLI; compare to `230615` baseline; assert non-regression on all f8a3c2 W1–W4 gates. (W4) Closeout receipt + Notion writeback.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1–W0.2 | Plan + Notion registration; backlog link; design lock | ~10K | Backlog rows from c9e4a1 W2 still live | ✅ DONE | [w0_receipt](../../docs/reports/apps_rg/exec_summary_regen_stuck_c0_split_w0_receipt.md) |
| W1 | W1.1–W1.3 | G2 stuck-same-failure early-exit | ~40K | f8a3c2 G3 wiring intact | ✅ DONE | [w1_receipt](../../docs/reports/apps_rg/exec_summary_regen_stuck_c0_split_w1_receipt.md) |
| W2 | W2.1–W2.4 | C0 fact schema split + migration | ~70K | X2 already reads `claim_text` | ✅ DONE | [w2_receipt](../../docs/reports/apps_rg/exec_summary_regen_stuck_c0_split_w2_receipt.md) |
| W3 | W3.1 | Brown canonical CLI re-proof | ~25K | vLLM + Qwen + judges available | ✅ DONE | [w3_receipt](../../docs/reports/apps_rg/exec_summary_regen_stuck_c0_split_w3_receipt.md) |
| W4 | W4.1 | Closeout: receipt, Notion, link-back | ~5K | W3 evidence on disk | ✅ DONE | [closeout_20260527](../../docs/reports/apps_rg/exec_summary_regen_stuck_c0_split_closeout_20260527.md) |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Disk + Notion plan registration | ✅ DONE |
| W0.2 | Link backlog rows + parent traceability | ✅ DONE |
| W1.1 | Failure-signature equality helper + tests | ✅ DONE |
| W1.2 | Wire `x2_stuck_same_failure` into cycles receipt + lane stats | ✅ DONE |
| W1.3 | Negative tests: same gate IDs + rows repeat → early-exit; different rows → no exit | ✅ DONE |
| W2.1 | Ledger schema v2: add `proof_text`; preserve `claim_text` semantics | ✅ DONE |
| W2.2 | Migrate `fact_engineering_platform_001` + `fact_quant_hpc_003` | ✅ DONE |
| W2.3 | Audit script: every fact has `claim_text` + `proof_text`; all I0 negs satisfied by `claim_text` | ✅ DONE |
| W2.4 | X2 contract test: `claim_text` is the only field X2 matches; `proof_text` reachable from source binding | ✅ DONE |
| W3.1 | Brown canonical CLI run + compare to `230615` | ✅ DONE |
| W4.1 | Closeout receipt + Notion writeback + backlog link-up | ✅ DONE |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Failure-signature equality | `apps_rg/runtime/sections/executive_summary_regen_observability.py` (helper) + new tests | Defining "same failure" without false negatives across cycles | ~12K | ✅ DONE |
| W1.2 | Cycles receipt wiring | `executive_summary_regen_observability.py`, `executive_summary_lane.py` (regen lane stats) | Cycles receipt schema additions must stay backward-compatible | ~14K | ✅ DONE |
| W1.3 | Stuck-loop tests | `tests/unit/apps_rg/test_executive_summary_regen_cycle_observability.py` | Brown-shaped fixture rows 1+5 | ~14K | ✅ DONE |
| W2.1 | Ledger schema v2 | `apps_rg/fact_inventory/master_skills_arsenal_ledger.json`, design doc | 38k-line ledger; per-fact migration must be deterministic | ~25K | ✅ DONE |
| W2.2 | Offending fact migration | candidate ledger + SRFS active (2 fact rows) | I0 negative-mechanism + credential policy must be satisfied by new `claim_text` | ~15K | ✅ DONE |
| W2.3 | Ledger audit script | `tools/apps_rg/audit_fact_ledger_claim_proof_split.py` (new) | Must be CI-callable; fail-closed | ~15K | ✅ DONE |
| W2.4 | X2 contract test | `tests/unit/apps_rg/runtime/validators/test_executive_summary_x2_claim_proof_split.py` | Confirms X2 reads `claim_text` only (already the case at lines 310/329/497) | ~15K | ✅ DONE |
| W3.1 | Brown re-proof | Brown & Brown SVP CLI + `compare_exec_summary_w3_brown.py` | Token + GPU cost; baseline comparison rigor | ~25K | ✅ DONE |
| W4.1 | Closeout | `docs/reports/apps_rg/exec_summary_regen_stuck_c0_split_closeout_20260527.md` | Notion linkage to backlog rows | ~5K | ✅ DONE |

---

## Parent / Related

| Plan / Item | Role |
|-------------|------|
| [complete-open-scope-closeout-c9e4a1](complete-open-scope-closeout-c9e4a1.md) | **Source closeout** — captured both defects as Backlog Items (W2 of c9e4a1) |
| [exec-summary-judge-regen-control-loop-f8a3c2](_archive/2026-05/exec-summary-judge-regen-control-loop-f8a3c2.md) | **Subject (COMPLETE — DO NOT REOPEN)** — owns G0–G5 wiring this plan extends with G2 stuck-loop |
| [exec-summary-failed-run-persistence-notion-e7c4b2](exec-summary-failed-run-persistence-notion-e7c4b2.md) | Convergence guard W5.2; this plan widens its semantics |
| [exec-summary-judge-regen-loop-closure-d8f3a1](exec-summary-judge-regen-loop-closure-d8f3a1.md) | Grandparent chassis (COMPLETE) — anti-pattern: parents stay Completed |
| Backlog: [G2 stuck-loop](https://www.notion.so/Exec-summary-regen-G2-stuck-loop-early-exit-same-X2-row-fails-N-times-36c27693f55c81d4b75ef9ac99509a07) | Owner of W1 acceptance |
| Backlog: [C0 claim/proof split](https://www.notion.so/Exec-summary-C0-fact-split-claim_text-display-allowed-vs-proof_text-full-body-36c27693f55c81b7916dc2a65edde07f) | Owner of W2 acceptance |

---

## Out Of Scope

- Reopening or appending waves to [f8a3c2](_archive/2026-05/exec-summary-judge-regen-control-loop-f8a3c2.md) (Completed parent — anti-pattern enforced by d8f3a1).
- Changing the X2 verbatim-display contract or any X1D rubric.
- Generic refactor of `master_skills_arsenal_ledger.json` beyond the 2 offending facts + the schema-additive change.
- New regen budget or temperature tuning.
- Anything in `agentic_core/` (this plan is `apps_rg`-only).
- Lowering N below 2 cycles for the stuck-loop early-exit (would risk false positives on legitimate retries).

---

## Gap Register

**GAP-1: Stuck-loop signature stability across cycles**  
- "Same failure" must be defined as `(failing_gate_ids tuple, row_indexes tuple)` after sort + dedup; otherwise rotating row indexes could mask a true stuck condition.

**GAP-2: I0 negs vs `claim_text` paraphrase**  
- W2.2 paraphrases must be checked against I0 `credential_policy_v1` and `neg_mechanism_inventory_001` deterministically — the audit script (W2.3) must reject any `claim_text` containing banned tokens.

**GAP-3: `proof_text` source binding**  
- X2 source-binding gates must continue to anchor against full provenance; this plan must not weaken them. W2.4 test asserts X2 reads `claim_text` while `proof_text` is reachable from `source_fact_ids`.

**GAP-4: Brown re-proof vLLM availability**  
- W3.1 requires the Qwen vLLM + judges; if unavailable, BLOCKED with a deferred-scope marker rather than mocking.

---

## Design Lock (W0 — approved)

SSOT: [exec_summary_regen_stuck_c0_split_design_lock.json](../../artifacts/apps_rg/exec_summary_regen_stuck_c0_split_design_lock.json)

| Constant | Value | Wave |
|----------|-------|------|
| `STUCK_LOOP_N_CYCLES` | `2` | W1 |
| `REGEN_STOPPED_REASON_X2_STUCK` | `x2_stuck_same_failure` | W1 |
| `REGEN_STOPPED_REASON_CONVERGED` | `regen_converged` (existing) | W1 (precedence: stuck before hash) |
| Failure signature | `(failing_gate_ids, row_indexes)` sorted/deduped | W1 |
| `claim_text` / `proof_text` split | display-allowed vs full-body | W2 |

Brown baseline: `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_230615/`

---

## Wave 0 — Plan + Notion registration + design lock

WAVE_ID: W0  
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: A

**Phases:**
- **W0.1** — Disk plan write + Notion registration via `tools/notion/plan_creation_helper.py` | ~5K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W0.2** — Link backlog rows + parent traceability (Related table) | ~5K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance:**
- `PLAN_CREATED` marker emitted; Notion Plans DB row **In Progress**
- Both backlog rows linked via `Plan` relation (PATCH OK)
- Design lock JSON on disk; constants approved for W1/W2

---

## Wave 1 — G2 stuck-same-failure early-exit

WAVE_ID: W1  
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: B

**Phases:**
- **W1.1** — Failure-signature equality helper in `executive_summary_regen_observability.py` | ~12K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Wire `REGEN_STOPPED_REASON_X2_STUCK` into cycles receipt + `regen_lane_stats` | ~14K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** — Stuck-loop tests (Brown rows 1+5 fixture) | ~14K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance:**
- `judge_remediation_cycles.json` for a Brown-shaped fixture stops at cycle 2 with `stopped_reason=x2_stuck_same_failure` when `failing_gate_ids` + row idx repeat
- All existing f8a3c2 G3 monotonicity tests still PASS (no regression)
- `regen_lane_stats` exposes `stuck_loop_detected: true` + `stuck_signature` for Notion review index

---

## Wave 2 — C0 claim/proof split + migration

WAVE_ID: W2  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: C

**Phases:**
- **W2.1** — Ledger schema v2: add optional `proof_text`; `claim_text` becomes display-allowed paraphrase; design doc update | ~25K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** — Migrate `fact_engineering_platform_001` + `fact_quant_hpc_003`: extract banned mechanism / credential prose into `proof_text`; rewrite `claim_text` to satisfy I0 | ~15K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.3** — `tools/apps_rg/audit_fact_ledger_claim_proof_split.py`: every fact has `claim_text`; if `proof_text` present, `claim_text ∩ I0_neg_tokens = ∅` | ~15K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.4** — X2 contract test: `claim_text` is the matching field; `proof_text` is read only for source binding (no X2 path matches it) | ~15K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance:**
- `master_skills_arsenal_ledger.json` v2 schema documented in `docs/reports/apps_rg/master_skills_arsenal_ledger_design.json`
- Audit script PASS over the full ledger
- X2 contract test PASS; no other X2 test regression
- Two offending facts: `claim_text` passes I0 deterministic neg-list; `proof_text` retains full body

---

## Wave 3 — Brown canonical CLI re-proof

WAVE_ID: W3  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: D

**Phases:**
- **W3.1** — Brown canonical CLI (parity JD/briefing/temperature with `230615`) — compare via `tools/apps_rg/compare_exec_summary_w3_brown.py` | ~25K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance:**
- New run reaches DRAFT_READY or X3=ALLOW (row 1+5 X2 PASS)
- Stuck-loop early-exit not triggered (or, if triggered, on a different signature than `230615`)
- f8a3c2 W4 schema_v2 stderr matrix unchanged

---

## Wave 4 — Closeout

WAVE_ID: W4  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: E

**Phases:**
- **W4.1** — Closeout report + Notion `Completed` + backlog link-up + `PLAN_COMPLETE` marker | ~5K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance:**
- `docs/reports/apps_rg/exec_summary_regen_stuck_c0_split_closeout_<ts>.md` on disk
- Both backlog rows updated with closure note + plan link
- Notion Plans status=Completed via `wave_execution_state.py complete`

---

## Definition of Done

| DoD | Criterion | Evidence | Verification |
|-----|-----------|----------|--------------|
| DoD-1 | Stuck-loop early-exit fires on Brown-signature fixture | New unit test + fixture | `pytest tests/unit/apps_rg/runtime/sections/test_executive_summary_regen_observability.py -k stuck` PASS |
| DoD-2 | C0 ledger split passes audit | Audit script | `python tools/apps_rg/audit_fact_ledger_claim_proof_split.py` exit 0 |
| DoD-3 | X2 contract preserved | X2 contract test | `pytest tests/unit/apps_rg/runtime/validators/test_executive_summary_x2_claim_proof_split.py` PASS |
| DoD-4 | No regression on f8a3c2 G3 monotonicity gates | Existing test suite | `pytest tests/unit/apps_rg/runtime/sections -k regen` PASS |
| DoD-5 | Brown canonical CLI smoke run produces artifact dir | CLI exit 0 + artifact_dir on disk | `python -m apps_rg --section executive_summary --candidate brown` exit 0 |
| DoD-6 | Plan registered on disk + Notion; backlog rows linked | Notion URLs + plan markers | `check_plan_registration_freshness.py --refresh` OK |
| DoD-7 | Closeout report + `PLAN_COMPLETE` marker emitted | Report path + marker | Grep for marker in plan file |

---

## Verification vs Deferral

| Item | Wave | If blocked |
|------|------|------------|
| vLLM + Qwen unavailable | W3 | BLOCKED — emit `DEFERRED_SCOPE` with reason `vllm_unavailable`; W1+W2 still merge |
| I0 paraphrase ambiguous | W2.2 | Author-Gate sub-decision (paraphrase candidates) — do not invent; pull from existing source binding |
| Audit script catches additional offending facts | W2.3 | SCOPE_EXPANSION decision: ACCEPTED if ≤5; SPLIT_TO_NEW_PLAN if >5 |
| Stuck-loop fires on legitimate divergent failures | W1.3 | Increase `STUCK_LOOP_N_CYCLES` to 3; document in plan; re-test |
| Notion token missing | W0/W4 | Disk SSOT valid; emit `PLAN_REGISTRATION_BYPASS=1`; complete Notion when token returns |

---

## Related artifacts

| Artifact | Path |
|----------|------|
| Source closeout (this plan's parent) | [complete-open-scope-closeout-c9e4a1.md](complete-open-scope-closeout-c9e4a1.md) |
| Closeout report (governance) | [complete_open_scope_closeout_20260526.md](../../docs/reports/cursor/complete_open_scope_closeout_20260526.md) |
| Author-Gate spec (origin) | [complete_open_scope_spec.json](../../artifacts/cursor/author_gate/complete_open_scope_spec.json) |
| Brown failure run | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_230615/` |
| Convergence guard (existing) | [executive_summary_regen_observability.py](../../apps_rg/runtime/sections/executive_summary_regen_observability.py) |
| X2 validator (existing claim_text matcher) | [executive_summary_x2.py](../../apps_rg/runtime/validators/executive_summary_x2.py) |
| Fact ledger (W2 target) | [master_skills_arsenal_ledger.json](../../apps_rg/fact_inventory/master_skills_arsenal_ledger.json) |
| Ledger design doc | [master_skills_arsenal_ledger_design.json](../../docs/reports/apps_rg/master_skills_arsenal_ledger_design.json) |
| f8a3c2 control-loop plan (archived parent) | [_archive/2026-05/exec-summary-judge-regen-control-loop-f8a3c2.md](_archive/2026-05/exec-summary-judge-regen-control-loop-f8a3c2.md) |
| W0 receipt | [exec_summary_regen_stuck_c0_split_w0_receipt.md](../../docs/reports/apps_rg/exec_summary_regen_stuck_c0_split_w0_receipt.md) |
| W1 receipt | [exec_summary_regen_stuck_c0_split_w1_receipt.md](../../docs/reports/apps_rg/exec_summary_regen_stuck_c0_split_w1_receipt.md) |
| Design lock (W0) | [exec_summary_regen_stuck_c0_split_design_lock.json](../../artifacts/apps_rg/exec_summary_regen_stuck_c0_split_design_lock.json) |

---

## Emitted markers

```
WAVE_COMPLETE: plan=exec-summary-regen-stuck-c0-split-a4f8e2 wave=0 note="design lock json, backlog Plan relation x2, w0 receipt"
WAVE_COMPLETE: plan=exec-summary-regen-stuck-c0-split-a4f8e2 wave=1 note="+6 stuck-loop tests, regen_observability, regen_lane_stats"
WAVE_COMPLETE: plan=exec-summary-regen-stuck-c0-split-a4f8e2 wave=2 note="claim/proof split, 2 facts migrated, audit+contract tests PASS"
WAVE_COMPLETE: plan=exec-summary-regen-stuck-c0-split-a4f8e2 wave=3 note="Brown exec_summary_20260527_025447_w3 claim_gate 0/10 regen fails vs baseline 10/10"
WAVE_COMPLETE: plan=exec-summary-regen-stuck-c0-split-a4f8e2 wave=4 note="closeout_20260527, notion Completed, backlog Done x2"
PLAN_COMPLETE: plan=exec-summary-regen-stuck-c0-split-a4f8e2 waves=W0-W4 status=DONE notion_page=36d27693-f55c-81d7-847a-c34cd7807849
```
