---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\exec-summary-judge-display-override-parity-7c3e8a.md'
original_relative_path: 'exec-summary-judge-display-override-parity-7c3e8a.md'
source_sha256: a834de10357949ea4b5dc9f42c3f0bb43b90c6519d34b9cd1dd8b1b41dce6b4d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: exec-summary-judge-display-override-parity-7c3e8a
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Executive Summary — Judge-Packet Display-Override Parity

Make the X1D judge packet for `executive_summary` carry the same `FACT_C0_DISPLAY_OVERRIDES` text that the L2 (Qwen) generation prompt receives, eliminating the structural Claude soft-fail loop discovered in run `full_resume_3976479ef871` (Brown & Brown SVP).

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-28

---

## Context (SCQA)

- **Situation** — `apps_rg` executive_summary lane uses C0 `FACT_C0_DISPLAY_OVERRIDES` (defined in `apps_rg/runtime/sections/executive_summary_synthesis_contract.py`) to force Qwen to emit specific framing for `fact_quant_hpc_003` (FSA-chartered phrasing) and `fact_engineering_platform_002` (forward-modal dependency-graph phrasing). X2 gate `x2_exec_summary_display_override_compliance` makes the override mandatory. Memory entity `Bug:ExecSummaryJudgeDisplayOverrideInvisible` first identified the gap on 2026-05-28.
- **Complication** — `apps_rg/runtime/judges/executive_summary_judge_packet.py` builds the X1D `allowed_fact_packet` with raw `claim_text` only; the override is never attached. Anthropic Claude grades against the raw fact, flags the override phrases as "extending beyond fact scope," scores 3.6–3.8, never reaches the 4.0 threshold. Five regen cycles (verified in `regen_token_budget_receipt.json`) cannot break the loop because Qwen MUST emit the override (X2 enforces) and Claude MUST flag it (no override in packet).
- **Question** — How do we deliver the same C0 fact substrate to the judges that the generator receives, so Claude grades against the authorized text rather than the raw fact line?
- **Answer** — Attach `display_override_text` onto each `allowed_fact_packet` row when `FACT_C0_DISPLAY_OVERRIDES` is set, update the GRADE_ONLY rubric to grade against the union of `claim_text + display_override_text`, and add a new X2 parity gate that fails closed when the override is present in the gen prompt but absent from the judge packet (or vice versa).

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Attach `display_override_text` to judge packet rows + update rubric note | ~12K | `FACT_C0_DISPLAY_OVERRIDES` import is safe from the judges module (no circular dep) | 🔲 TODO | Claude judge raw response contains `display_override_text` in `allowed_fact_packet`; rubric explicitly authorizes grading against override union |
| W2 | W2.1, W2.2 | Add `x2_executive_summary_judge_packet_display_override_parity` X2 gate (fail-closed) | ~8K | New X2 gate slots into existing `executive_summary_judge_packet.build_deterministic_gate_summary` registry without breaking gate-closure map | 🔲 TODO | Gate emits `pass=true` when override is symmetric; `pass=false` decisive with reason when asymmetric; gate registered in `executive_summary_x2.py` |
| W3 | W3.1, W3.2 | Verification — Brown SVP rerun, unit test, integration smoke | ~6K | Qwen vLLM remains live on localhost:8000 | 🔲 TODO | Brown SVP rerun finishes with Claude score ≥ 4.0 on exec_summary AND all 7 lanes produce display text |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Extend `enrich_allowed_fact_packet_for_judges` with override attachment | 🔲 TODO |
| W1.2 | Patch GRADE_ONLY rubric + system prompt note to grade union | 🔲 TODO |
| W2.1 | Add parity validator function in `executive_summary_x2.py` | 🔲 TODO |
| W2.2 | Wire gate into `build_deterministic_gate_summary` + gate-closure map | 🔲 TODO |
| W3.1 | Re-run Brown SVP, capture artifacts, confirm Claude ≥ 4.0 | 🔲 TODO |
| W3.2 | Add unit test asserting override appears in packet; memory writeback | 🔲 TODO |

---

## Out Of Scope

- Changing the override text content (already finalized in plan `exec-summary-rc-structural-repair-f4a8c2`).
- Modifying the cascade-abort policy in `modular_resume_generation.py` (`product_fail_closed_runtime` flip is the alternative path the user explicitly rejected).
- Token-budget estimator recalibration (false-alarm; tracked under existing `exec-summary-context-limits-ssot-b7e4a1`).
- Notion writes — `aps_rg` runtime; this plan only edits judges + validators.

---

## Wave 1 — Judge-packet Override Attachment + Rubric Update

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Extend `enrich_allowed_fact_packet_for_judges` so each returned row carries `display_override_text` and `preferred_c0_display_text` when those fields are set in `FACT_C0_DISPLAY_OVERRIDES` or `preferred_c0_display_text` on the source row | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Update GRADE_ONLY system prompt + rubric note inside `executive_summary_judge_packet.py` to: "When `display_override_text` is set on an allowed fact row, grade the candidate sentence against the UNION of `claim_text` and `display_override_text`; neither is unsupported." Update `factual_support` rubric dimension to reference the union explicitly. | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- New Brown SVP judge_packet JSON shows `display_override_text` populated on `fact_quant_hpc_003` and `fact_engineering_platform_002` rows.
- Diff-based unit test asserts Claude rubric no longer references only raw `claim_text` for those rows.

---

## Wave 2 — Parity X2 Gate

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Add `check_judge_packet_display_override_parity` to `apps_rg/runtime/validators/executive_summary_x2.py`. Inputs: `judge_allowed_fact_packet`, the C0-side `FACT_C0_DISPLAY_OVERRIDES` mapping, and `cited_fact_ids`. Returns `(ok, detail)` with decisive failure when any cited fact_id has an override in C0 but no `display_override_text` on its packet row (or vice versa). | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Register gate id `x2_executive_summary_judge_packet_display_override_parity` in `executive_summary_judge_packet.build_deterministic_gate_summary` snapshot, in `executive_summary_x2.py` gate registry, and in `executive_summary_x1d_gate_closure_map.py` (gate-closure map version bump). Add to `DIMENSION_GATE_MAP` under `deterministic_alignment`. | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Gate emits in `x2_gate_outputs.json` for every exec_summary run.
- Synthetic regression test: tamper with the judge packet to remove the override text → gate fails closed with decisive reason.

---

## Wave 3 — Verification + Writeback

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Re-run `python -m apps_rg --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md`. Confirm: Claude X1D score ≥ 4.0 on exec_summary; X3 = `X3_ALLOW`; all 7 lanes produce `resume_display_text.txt`. | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Add unit test `tests/unit/apps_rg/runtime/judges/test_executive_summary_judge_packet_display_override.py` asserting override is attached for known fact ids. Memory writeback: flip `Bug:ExecSummaryJudgeDisplayOverrideInvisible` observation to closed-by-plan with this slug + run-id evidence. | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Brown SVP run exits 0; review_bundle.zip contains all 7 lane display files.
- New unit test passes; full apps_rg judges test slice green.
- Memory entity updated.

---

## Execution Details

### W1.1 — Extend judge-packet enricher

**Scope**: `apps_rg/runtime/judges/executive_summary_judge_packet.py` — modify `enrich_allowed_fact_packet_for_judges` (line 144).

**Commands**:
```bash
python -m pytest tests/unit/apps_rg/runtime/judges -k display_override -x -q
```

### W1.2 — Patch rubric note

**Scope**: Same file — update `GRAPH_ONLY_GRADE_ONLY_RUBRIC` block and the `system` prompt note above `factual_support` dimension.

**Commands**:
```bash
python -m apps_rg --section executive_summary --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

### W2.1 — Parity validator

**Scope**: `apps_rg/runtime/validators/executive_summary_x2.py` — add new function next to existing `_DISPLAY_OVERRIDE_REQUIRED_SUBSTRINGS` block (~line 130).

### W2.2 — Gate registration

**Scope**: `apps_rg/runtime/judges/executive_summary_judge_packet.py`, `apps_rg/runtime/validators/executive_summary_x2.py`, `apps_rg/runtime/judges/executive_summary_x1d_gate_closure_map.py`.

### W3.1 — Brown SVP rerun

**Commands**:
```bash
python -m apps_rg --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

### W3.2 — Unit test + writeback

**Scope**: New test file under `tests/unit/apps_rg/runtime/judges/`. Memory MCP `add_observations` to `Bug:ExecSummaryJudgeDisplayOverrideInvisible`.

---

## Gap Register

**GAP-1: Token-budget estimator over-counts ~70% (judge_regen headroom shows -25% but calls succeed)**
- Tracked by separate plan `exec-summary-context-limits-ssot-b7e4a1`. Not blocking this fix.

**GAP-2: ToT / reflexion / self-consistency disabled (singleton_call_no_vote_or_branch_loop)**
- Architectural; out of scope. Multi-shot would not help here anyway since all judges share the broken packet.

**GAP-3: Six lanes cascade-abort on one lane soft-fail (`product_fail_closed_runtime` defaults True)**
- User explicitly chose this fix over the cascade-policy flip. If the proper fix lands and Claude passes, the cascade no longer triggers and other lanes will render naturally.

---

## Definition of Done

DoD-1: Brown SVP rerun produces Claude X1D score ≥ 4.0 and X3 = `X3_ALLOW` on executive_summary.
- Evidence: `artifacts/apps_rg/runtime_proofs/full_resume_<run_id>/lanes/executive_summary/x3_disposition.json` shows `x3_code: X3_ALLOW`.
- Status: TODO

DoD-2: All 7 generated lanes (headline, executive_summary, unify_bullets, unify_narrative, ibm_bullets, ibm_narrative, competencies) produce `resume_display_text.txt`.
- Evidence: `find artifacts/apps_rg/runtime_proofs/full_resume_<run_id>/lanes -name resume_display_text.txt | wc -l` ≥ 7.
- Status: TODO

DoD-3: Smoke-run executable surface — `python -m apps_rg --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd ... --manual-brief ...` exits 0.
- Evidence: command exit code captured in terminal log.
- Status: TODO

DoD-4: Unit test + judges-slice test green.
- Evidence: `python -m pytest tests/unit/apps_rg/runtime/judges -q` shows N pass, 0 fail.
- Status: TODO

DoD-5: New X2 parity gate is enforced; tampered packet fails closed.
- Evidence: Synthetic test asserts gate emits `pass=false` with decisive reason on tampered input.
- Status: TODO

DoD-6: Memory writeback to `Bug:ExecSummaryJudgeDisplayOverrideInvisible`.
- Evidence: `mem://Bug:ExecSummaryJudgeDisplayOverrideInvisible` updated with closing observation + plan slug + run-id.
- Status: TODO

### Verification vs Deferral

| Item | Verified by | Deferred to |
|---|---|---|
| Claude raw response no longer flags override phrases | DoD-1 evidence | — |
| All 7 lanes ship | DoD-2 evidence | — |
| Cascade-abort policy change | — | Not in scope (user choice) |
| Token-budget estimator recalibration | — | `exec-summary-context-limits-ssot-b7e4a1` |
| ToT/reflexion loops | — | Outside apps_rg scope |

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=exec-summary-judge-display-override-parity-7c3e8a wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=exec-summary-judge-display-override-parity-7c3e8a decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=exec-summary-judge-display-override-parity-7c3e8a reason="<summary>" added="<waves/phases>" authorized="yes"
```

---

## Marker Quick Reference

```
WAVE_START: plan=exec-summary-judge-display-override-parity-7c3e8a wave=<N>
WAVE_COMPLETE: plan=exec-summary-judge-display-override-parity-7c3e8a wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=exec-summary-judge-display-override-parity-7c3e8a phase=<W1.1>
PLAN_COMPLETE: plan=exec-summary-judge-display-override-parity-7c3e8a note="Brown SVP rerun ALLOW with all 7 lanes"
```
