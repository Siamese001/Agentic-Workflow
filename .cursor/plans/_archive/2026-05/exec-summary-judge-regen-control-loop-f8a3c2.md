---
plan_id: exec-summary-judge-regen-control-loop-f8a3c2
plan_type: product
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Executive Summary — Judge Regen Control Loop (Monotonicity + Best-of Publish)

**North star:** Judge-directed regen is **closed-loop control**, not “call Qwen again.” A cycle is accepted only when it **improves or ties** the trigger judge(s) at the operator floor; the run **publishes the best candidate** in a pool (scratch + accepted regens), with receipts that never imply remediation success on `output_changed` alone.

**Evidence that motivated this plan:** Brown floor-matrix run `exec_summary_20260526_070105` (floor 4.2): judge regen cycle 1 **accepted** while Claude regressed **4.0 → 3.6**; regen introduced `claim_ledger` row-3 metric mismatch (10% vs 40% in `claim_text`); published paragraph kept the worse draft. Related: floor 4.4 reverted to scratch after regen (partial fix in lane: `final_publish_baseline`).

**Parent / related (do not re-open):**

- [exec-summary-failed-run-persistence-notion-e7c4b2.md](exec-summary-failed-run-persistence-notion-e7c4b2.md) — **apps_* receipt-bound candidate pool + Notion review index** (hardened 2026-05-26; **mirrors f8a3c2 publish only** — no parallel selector; LIVE vs BACKFILL `proof_class`)
- [exec-summary-judge-regen-loop-closure-d8f3a1.md](exec-summary-judge-regen-loop-closure-d8f3a1.md) — chassis + post-regen X2 green (COMPLETED)
- [exec-summary-x1d-dimension-verdicts-e8f4a2.md](exec-summary-x1d-dimension-verdicts-e8f4a2.md) — dimension deltas (if on disk)
- [exec-summary-qwen-regen-token-budget-c4e8a1.md](exec-summary-qwen-regen-token-budget-c4e8a1.md) — token budget (orthogonal)

> **plan_id discipline:** `exec-summary-judge-regen-control-loop-f8a3c2`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W5
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-26
PLAN_HARDENING: applied_2026-05-26 control_loop_v2_hardening
EXECUTION_APPROVED: true

NOTION_PAGE_ID: 36c27693-f55c-8132-8f36-d3ac156e1673
NOTION_PLAN_URL: https://www.notion.so/exec-summary-judge-regen-control-loop-f8a3c2-36c27693f55c81328f36d3ac156e1673
PLAN_CREATED: slug=exec-summary-judge-regen-control-loop-f8a3c2 path=.cursor/plans/exec-summary-judge-regen-control-loop-f8a3c2.md status=Not Started notion_page=36c27693-f55c-8132-8f36-d3ac156e1673

---

## Context (SCQA)

- **Situation** — Judge regen loop is operational: `SameAuthorityRegenRunner`, prescriptive `REGEN_DELTA_v1`, soft-failed-only rescore, `judge_remediation_cycles.json`. Acceptance today: `output_changed && parse_ok` ([executive_summary_judge_remediation.py](apps_rg/runtime/sections/executive_summary_judge_remediation.py)).
- **Complication** — Regen can change text and pass X2 while **lowering** the failing judge and corrupting ledger metrics; lane may publish last regen or revert to scratch inconsistently. Operators cannot trust “2 regen cycles” in metrics.
- **Question** — How do we make judge remediation **honest, monotonic, and best-of** without weakening X2 or moving rubric into core?
- **Answer** — Layered gates (G0–G5), trigger-judge monotonicity on accept, deterministic ledger metric sync, **candidate pool + argmax publish**, narrow delta classes, receipts that say `regressed` when scores drop.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.0–W0.1 | Plan + Notion registration + design lock | ~25K | This file approved for review | DONE | `PLAN_CREATED` + Notion row |
| W1 | W1.0–W1.2 | G3 trigger-judge monotonicity on cycle accept | ~55K | `rescore_judges_after_regen` receipts exist | DONE | Brown 4.2 regen regressed → cycle rejected |
| W2 | W2.0–W2.1 | G1 ledger metric sync (deterministic) | ~40K | Fact capsule metrics in C0 | DONE | 10%/40% mismatch auto-fixed or reject |
| W3 | W3.0–W3.4 | CandidateSnapshot + full-panel rank + artifact rebind | ~75K | W1 gate ids stable | DONE | `published_candidate_digest` match; no split-brain |
| W4 | W4.0–W4.3 | schema v2 + delta_class + negative tests | ~55K | W1–W3 merged | DONE | False PASS tests green |
| W5 | W5.0–W5.2 | Canonical CLI Brown proof + closeout | ~100K | vLLM + judges | DONE | CLI artifact checklist + no core diff |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.0 | Plan review on disk + Notion | DONE |
| W0.1 | Link parent plans + gap register | DONE |
| W1.0 | G3 deterministic evaluator | DONE |
| W1.1 | Wire G3 post soft-rescore | DONE |
| W1.2 | Negative tests: regression rejected | DONE |
| W2.0 | Ledger metric sync fail-closed | DONE |
| W2.1 | Candidate-local G1 + receipt | DONE |
| W3.0 | CandidateSnapshot frozen dataclass | DONE |
| W3.1 | Full-panel rescore per snapshot | DONE |
| W3.2 | Argmax + artifact rebind | DONE |
| W3.3 | candidate_pool_summary + integrity | DONE |
| W3.4 | Pool tests + 070105 fixture | DONE |
| W4.0 | judge_remediation_cycles v2 | DONE |
| W4.1 | delta_class + G5 scope | DONE |
| W4.2 | Negative false-PASS tests | DONE |
| W4.3 | stderr + matrix columns | DONE |
| W5.0 | Canonical CLI Brown 4.2 | DONE |
| W5.1 | Floor matrix aggregation | DEFERRED (optional) |
| W5.2 | Closeout + no core diff receipt | DONE |

---

## Product Contract (one sentence)

> **Trigger on judge failure; accept only on measured improvement (or tie with strict dimension wins); publish the best evidence-backed candidate; never certify a regressed draft.**

---

## Architecture Invariants

| ID | Invariant |
|----|-----------|
| INV-1 | Apps own trigger, floors, X2 re-check, judge rescore, publish policy, X3 inputs — no rubric/X2 definitions in core |
| INV-2 | `SameAuthorityRegenRunner` unchanged; apps pass narrower deltas only |
| INV-3 | No gate weakening to make bad regen pass |
| INV-4 | `UNKNOWN` / regressed regen ≠ remediation success; `CERTIFIED` only when all model-backed judges ≥ operator floor on **published** text |
| INV-5 | X2 pass alone is insufficient for regen accept (executive_signal / synthesis_quality are X1D) |
| INV-6 | Live Brown re-proof required for plan PASS (not unit tests alone) |
| INV-7 | **Publish reads frozen `CandidateSnapshot` only** — never reconstruct from mutable lane state |
| INV-8 | **CERTIFIED** requires fresh full-panel X1D on published text; `carried_forward` scores cannot certify |

---

## Plan Hardening Register (2026-05-26)

| ID | Hardening | Wave |
|----|-----------|------|
| H-1 | Immutable `CandidateSnapshot` + `candidate_digest` before publish | W3 |
| H-2 | Deterministic G3 tie semantics (no vague “tie”) | W1 |
| H-3 | Full-panel rescore for publish ranking (soft-only for G3 accept) | W3 |
| H-4 | G1 ledger sync fail-closed + candidate-local | W2 |
| H-5 | Negative tests for false PASS receipts | W1, W4 |
| H-6 | Final artifacts rebound from selected snapshot only | W3 |
| H-7 | W5 canonical `python -m apps_rg` artifact checklist | W5 |
| H-8 | `judge_remediation_cycles` schema_version=2 | W4 |
| H-9 | Closeout: no `agentic_core` diff receipt | W5 |
| H-10 | G4 mandatory for CERTIFIED when text changed materially | W3, W5 |

---

## CandidateSnapshot (immutable — H-1)

Every pool entry (`scratch`, `regen_cycle_k`) MUST be frozen as an **immutable** `CandidateSnapshot` at the moment it becomes publish-eligible. Publish and final artifact writes MUST read **only** from the selected snapshot — never from live lane variables.

### Required fields

| Field | Purpose |
|-------|---------|
| `candidate_id` | `scratch` \| `regen_cycle_N` |
| `resume_display_text` | Frozen display prose |
| `parsed_json` | Full parsed L2 object at freeze time |
| `claim_ledger` | Frozen ledger rows |
| `x2_gate_outputs` | X2 gates evaluated on **this** text |
| `model_backed_scores_snapshot` | Per-provider holistic scores used for ranking |
| `dimension_verdicts_snapshot` | Per-provider dimension verdicts when available |
| `source_fact_ids_digest` | SHA256 of sorted allowlist |
| `allowed_fact_ids_digest` | SHA256 of sorted allowed IDs |
| `prompt_hash` | Frozen compile ref |
| `provider_lane` / `model_name` | Generation metadata |
| `run_refs` | `provider_request` / `provider_response` refs for this candidate |
| `candidate_digest` | SHA256 over canonical JSON of fields above (excl. self) |
| `scores_freshness` | `full_panel` \| `soft_failed_only` \| `carried_forward` (see H-3) |

### Rules

- Snapshots are **append-only** in `candidate_pool_summary.json` (or embedded in `judge_remediation_cycles.json` v2).
- Argmax publish compares `candidate_digest` values — lane working copy changes after freeze MUST NOT affect ranking.
- `publish_selected_snapshot_id` + `published_candidate_digest` written before any artifact rebind (H-6).

---

## Layered Acceptance Gates (regen cycle)

| Gate | Check | Fail action |
|------|--------|-------------|
| **G0** | Valid JSON, 6 sentences, third person | `reject_gate=parse` |
| **G1** | Ledger metric sync (candidate-local, fail-closed) — § G1 | `reject_gate=ledger_metric_sync_ambiguous` |
| **G2** | X2 on regen text | One bounded shape repair → else `reject_gate=post_regen_x2_failed` |
| **G3** | Trigger-judge monotonicity (deterministic) — § G3 | `reject_gate=trigger_judge_regression` \| `trigger_judge_unknown` |
| **G4** | Optional for **cycle accept**; **mandatory for CERTIFIED** if published text ≠ scratch digest — § G4 | Block cert / require full panel |
| **G5** | Delta scope matches `delta_class` | `reject_gate=delta_scope_violation` |

**Acceptance ≠ publish.** Accept = snapshot frozen + pool entry. Publish = argmax over snapshots with **full-panel** scores (H-3).

### G1 — Ledger metric sync (fail-closed, H-4)

Deterministic sync runs **on the candidate being evaluated** (not lane globals).

| Rule | Behavior |
|------|----------|
| Single source | Repair allowed only when **exactly one** allowed `source_fact_id` supplies the metric replacement |
| Ambiguity | Multiple conflicting facts, no fact contains metric, or candidate metric not in allowed facts → `reject_gate=ledger_metric_sync_ambiguous` |
| Consistency | Must update `claim_text`, display prose, and `claim_ledger` together or reject |
| Receipt per row | `row_id`, `before_metric`, `after_metric`, `source_fact_id`, `repair_reason` |

No hidden metric rewrite path.

### G3 — Trigger-judge monotonicity (deterministic, H-2)

Evaluated per **soft-failed** trigger judge after soft-failed-only rescore (cost control for accept only).

For each trigger judge `j`:

| Condition | G3 result |
|-----------|-----------|
| `score_after` missing / UNKNOWN / rescore failed | **REJECT** — `reject_gate=trigger_judge_unknown` |
| `score_after > score_before` | **PASS** |
| `score_after < score_before` | **REJECT** — `reject_gate=trigger_judge_regression` |
| `score_after == score_before` AND `major_dimension_fail_count_after < major_dimension_fail_count_before` | **PASS** |
| `score_after == score_before` AND counts equal AND dimension verdicts missing | **REJECT** — `reject_gate=trigger_judge_unknown` |
| `score_after == score_before` AND counts equal AND verdicts unchanged | **REJECT** — `reject_gate=trigger_judge_regression` (tie is not improvement) |

`major_dimension_fail_count` = count of dimensions with `pass=false` AND `severity=major` in `dimension_verdicts_snapshot`.

### G4 — Non-trigger stability (H-10)

- **Cycle accept:** G4 optional (defer full panel unless needed).
- **CERTIFIED:** If `published_candidate_digest != scratch_digest` (material text change), **all** model-backed judges MUST have `scores_freshness=full_panel` on published snapshot; any `carried_forward` score → CERTIFIED blocked (`cert_block_reason=stale_non_trigger_scores`).

---

## Delta Classes (one per cycle)

| Class | Scope | When |
|-------|--------|------|
| `S6_forward_synthesis` | S6 + touching ledger rows | Thin S6 / forward synthesis fail |
| `connective_S2_S5` | Reword openers S2–S5, same facts/metrics | Mechanical connectives |
| `ledger_metric_sync` | **Deterministic, no LLM** | Display vs `claim_text` metric mismatch |
| `dimension_executive_signal` | ≤3 sentences from dimension verdicts | executive_signal major fail |

**Forbidden in production default:** “rewrite S2–S6” without `APPS_RG_EXEC_SUMMARY_EXPLORATORY_FULL_PARAGRAPH_REGEN=1`.

---

## Publish Policy — Best-of Pool (frozen snapshots)

| Candidate ID | Enter pool when |
|--------------|-----------------|
| `scratch` | After first X2 pass → `CandidateSnapshot` frozen |
| `regen_cycle_k` | G0–G3 pass → snapshot frozen with `publish_eligible=true` |

### Full-panel scoring for ranking (H-3)

**Soft-failed-only rescore is allowed for G3 cycle accept only.**

Before argmax publish, **every publish-eligible snapshot** MUST receive a **fresh full-panel** X1D rescore on that snapshot’s frozen text. Set `scores_freshness=full_panel` on the snapshot used for ranking.

| Mode | When | May used for publish rank? | May used for CERTIFIED? |
|------|------|---------------------------|-------------------------|
| `soft_failed_only` | G3 accept gate | No | No |
| `full_panel` | Pre-publish rank + cert | Yes | Yes |
| `carried_forward` | Copied from prior candidate | No | No |

**Publish score:** `min(model_backed_holistic_scores)` from **full_panel** snapshot fields only.

**Tie-break:** higher sum of full-panel scores → fewer major dimension fails → prefer `scratch` on tie.

**Receipt fields:** `final_publish_baseline`, `publish_reason`, `candidate_pool_summary[]`, `publish_selected_snapshot_id`, `published_candidate_digest`.

Replaces ambiguous “revert to `_pre_resume`” vs “last regen” behavior.

---

## Artifact Rebind (H-6 — no split-brain)

After argmax selects `CandidateSnapshot` `S*`, **rebind or regenerate** all final outputs from `S*` only:

| Artifact | Source |
|----------|--------|
| `resume_display_text.txt` | `S*.resume_display_text` |
| `l2_output.json` / parsed JSON | `S*.parsed_json` |
| `claim_ledger.json` | `S*.claim_ledger` |
| `x2_gate_outputs.json` | `S*.x2_gate_outputs` |
| `x1d_llm_judge_outputs.json` | Full-panel rescore on `S*` (must match snapshot scores) |
| `x3_disposition.json` | Aggregated from rebound X2 + X1D |
| `section_metric_receipt.json` | Published candidate metrics |

**Integrity receipt (required):**

```json
{
  "published_candidate_digest": "<S*.candidate_digest>",
  "final_artifact_digest_source": "<same>",
  "publish_selected_snapshot_id": "scratch|regen_cycle_k",
  "artifact_rebind_complete": true
}
```

`published_candidate_digest` MUST equal `final_artifact_digest_source` or run fails closed (`publish_integrity_failed`).

Lane mutable state after publish is **non-authoritative** for exit artifacts.

---

## Rescore & Receipts

- **G3 accept:** soft-failed-only rescore (cost control).
- **Publish rank / CERTIFIED:** full-panel rescore per publish-eligible `CandidateSnapshot`.
- **Cycle receipt (`schema_version=2`):** `scores_before`, `scores_after`, `score_deltas` (rescored keys only), `reject_gate`, `publish_eligible`, `delta_class`, `candidate_digest`, `g3_verdict_per_trigger_judge[]`.
- **Run receipt:** `operator_judge_pass_floor`, `regen_outcome`: `improved` \| `no_acceptable_candidate` \| `floor_not_met` (never `improved` if `final_publish_baseline=scratch` and no accepted regen beat scratch on full-panel min score).
- **stderr one-liner:** e.g. `Judge regen cycle 1 rejected: Claude 4.0→3.6 (floor 4.2). Published scratch (min 4.0).`

### Schema versioning (H-8)

- `judge_remediation_cycles.json`: `schema_version: 2`, `schema: executive_summary_judge_remediation_cycles_v2`.
- Parsers MUST NOT treat v1 receipts as monotonic-control proof.
- v1 → v2 migration: read-only; new runs emit v2 only.

---

## Certification Boundary

| Disposition | When |
|-------------|------|
| **CERTIFIED** | Published snapshot: all model-backed judges ≥ floor, X2 pass, `scores_freshness=full_panel` on published snapshot, G4 satisfied if text ≠ scratch |
| **DRAFT_READY** | Publishable best-of, floor not met OR stale/carried_forward scores on published text |
| **Never** | Certify because regen ran, hash changed, or copied non-trigger scores on changed paragraph |

---

## Out Of Scope

- Changing X1D rubric definitions or judge panel membership
- Core `JudgeDirectedRegenOrchestrator` rewrite (ADR-086 apps orchestration stands)
- `max_semantic_regen_attempts` > 1 product default (defer until W4 PASS)
- CERTIFIED 3/3 at floor 4.4+ (operator ship / separate matrix plans)
- `agentic_core` edits unless Author-Gate `platform_core_change` opened

---

## Execution Waves

> Consolidated wave + phase status: [Status Tables](#status-tables) (auto-updated by wave lifecycle hooks).

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.0 | Plan review on disk + Notion | This plan, Plans DB | Registration | ~10K | DONE |
| W0.1 | Link parent plans + gap register | `.cursor/plans/` cross-refs | Traceability | ~15K | DONE |
| W1.0 | G3 deterministic evaluator (`evaluate_g3_trigger_judge`) | `executive_summary_judge_remediation.py` | vague tie | ~25K | DONE |
| W1.1 | Wire G3 post soft-rescore; `trigger_judge_unknown` | lane + remediation | UNKNOWN accept | ~15K | DONE |
| W1.2 | Negative tests: regression → `accepted=false` | `test_*judge*` | false PASS | ~15K | DONE |
| W2.0 | `sync_claim_ledger_metrics_from_facts()` fail-closed | `executive_summary_judge_regen_loop.py` | ambiguous repair | ~25K | DONE |
| W2.1 | Candidate-local G1 + per-row receipt | prepare + lane | lane globals | ~15K | DONE |
| W3.0 | `CandidateSnapshot` frozen dataclass + digest | `executive_summary_lane.py` | mutable lane | ~25K | DONE |
| W3.1 | Full-panel rescore per publish-eligible snapshot | remediation + lane | carried_forward rank | ~20K | DONE |
| W3.2 | Argmax + artifact rebind from snapshot only | lane finalize path | split-brain | ~20K | DONE |
| W3.3 | `candidate_pool_summary.json` + integrity receipt | artifact writers | — | ~10K | DONE |
| W3.4 | Pool tests + 070105 fixture replay | unit | Brown 4.2 | ~15K | DONE |
| W4.0 | `judge_remediation_cycles` schema_version=2 | lane receipts | v1 misread | ~15K | 🔲 TODO |
| W4.1 | `delta_class` + G5 scope | `collect_judge_remediation_delta_lines` | rewrite S2–S6 | ~20K | 🔲 TODO |
| W4.2 | Negative tests: X2-only / output_changed cannot pool | tests | false PASS | ~15K | 🔲 TODO |
| W4.3 | stderr + matrix columns (`reject_gate`, digests) | floor matrix helper | UX | ~10K | 🔲 TODO |
| W5.0 | Canonical CLI Brown run (single floor 4.2 proof) | `python -m apps_rg` | helper-only PASS | ~50K | 🔲 TODO |
| W5.1 | Floor matrix aggregation (optional index) | `run_exec_summary_floor_matrix.py` | — | ~40K | 🔲 TODO |
| W5.2 | Closeout + `no_agentic_core_diff` receipt | `docs/reports/cursor/` | core drift | ~25K | 🔲 TODO |

---

## Wave 0 — Plan Lock + Traceability

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: Z

**Phases:**

- **W0.0** — Plan on disk; Notion Plans row verified (`Exists On Disk=true`, slug/path match) | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W0.1** — Parent/sibling plan cross-refs + gap register + Brown fixture anchor | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance:**

- `PLAN_CREATED` marker present; Notion page `36c27693-f55c-8132-8f36-d3ac156e1673` Status=`In Progress`
- Receipt: [exec_summary_judge_regen_control_loop_w0_receipt.md](docs/reports/cursor/exec_summary_judge_regen_control_loop_w0_receipt.md)

---

## Wave 1 — Trigger-Judge Monotonicity

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases:**

- **W1.0** — Implement deterministic G3 table (§ G3); emit `g3_verdict_per_trigger_judge[]` | ~25K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.1** — UNKNOWN/missing rescore → `trigger_judge_unknown`; equal score + unchanged verdicts → reject | ~15K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Negative: `output_changed=true` + regression → `accepted=false`, `publish_eligible=false` | ~15K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance:**

- Re-running logic on `exec_summary_20260526_070105` artifacts: cycle 1 would be **`publish_eligible: false`**
- Unit tests PASS

---

## Wave 2 — Ledger Metric Integrity (G1)

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases:**

- **W2.0** — Single-source-only repair; ambiguous → `ledger_metric_sync_ambiguous` | ~25K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.1** — Sync `claim_text` + display + ledger; per-row `before_metric`/`after_metric` receipt | ~15K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance:**

- Fixture: row with 10% in `claim_text` and 40% in fact → repaired to 40% before X2
- Claude finding `claim_ledger_row_3_metric_mismatch` not introduced by regen

---

## Wave 3 — Best-of Publish

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases:**

- **W3.0** — `CandidateSnapshot` freeze at pool entry; `candidate_digest` | ~25K | PHASE_STATUS: DONE
- **W3.1** — Full-panel rescore each publish-eligible snapshot before rank | ~20K | PHASE_STATUS: DONE
- **W3.2** — Argmax on full-panel min score; rebind all final artifacts (§ Artifact Rebind) | ~20K | PHASE_STATUS: DONE
- **W3.3** — `candidate_pool_summary.json` + `published_candidate_digest == final_artifact_digest_source` | ~10K | PHASE_STATUS: DONE
- **W3.4** — Tests: all regens regress → publish scratch; cert blocked on `carried_forward` | ~15K | PHASE_STATUS: DONE

**Acceptance:**

- Floor 4.2 Brown replay: when regen regresses Claude, **published = scratch** (not 3.6 draft)
- Floor 4.4: when regen improves min score vs scratch, published = best regen (≠ scratch)

---

## Wave 4 — Receipts + Narrow Deltas

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases:**

- **W4.0** — Map dimension failures → `delta_class`; ban default full-paragraph rewrite | ~20K | PHASE_STATUS: DONE
- **W4.1** — G5: count sentence-level edits vs prior; reject if over budget | ~15K | PHASE_STATUS: DONE
- **W4.2** — Operator stderr + floor matrix columns: `reject_gate`, `publish_baseline` | ~10K | PHASE_STATUS: DONE

---

## Wave 5 — Live Proof (canonical CLI — H-7)

WAVE_ID: W5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

### W5.0 — Canonical section CLI (PASS authority)

**Primary proof command** (Brown, floor 4.2, judge regen on):

```bash
set APPS_RG_EXEC_SUMMARY_JUDGE_PASS_FLOOR=4.2
set APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1
set APPS_RG_EXEC_SUMMARY_CORE_SAME_AUTHORITY_REGEN=1
set VLLM_MAX_MODEL_LEN=32768
python -m apps_rg --section executive_summary --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --provider qwen_vllm --allow-non-allow-exit-zero --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

**Required artifacts under run dir** (plan PASS fails closed if any missing):

| Artifact | Purpose |
|----------|---------|
| `run_manifest.json` | Run identity |
| `compiled_prompt_artifact.json` | Frozen compile proof |
| `provider_request.json` | Scratch generation |
| `provider_response.json` | Scratch generation |
| `judge_remediation_cycles.json` | `schema_version: 2` cycles |
| `candidate_pool_summary.json` | Frozen snapshots + digests (or embedded in cycles v2) |
| `x2_gate_outputs.json` | Matches published snapshot |
| `x1d_llm_judge_outputs.json` | Full-panel on published text |
| `x3_disposition.json` | Honest disposition |
| `section_metric_receipt.json` | Operator metrics |
| `publish_integrity_receipt.json` | `published_candidate_digest == final_artifact_digest_source` |

### W5.1 — Floor matrix (aggregation only)

```bash
python tools/cursor/run_exec_summary_floor_matrix.py
```

- Helper MAY aggregate floors 4.0 / 4.2 / 4.4 into `floor_matrix_latest.json`
- **PASS for plan does NOT rely on helper alone** — W5.0 canonical CLI artifacts are authoritative

### W5.2 — Closeout (H-9)

- `docs/reports/cursor/exec_summary_judge_regen_control_loop_closeout_20260526.md`
- **`no_agentic_core_diff_receipt.json`**: `git diff --name-only` (or file manifest) proving **zero** `agentic_core/` changes in this plan’s commits
- List only `apps_rg/`, `tests/`, `tools/cursor/`, docs

---

## Gap Register

### Parent / Sibling Plan Traceability (W0.1)

| Plan | Role | Status | Handoff to f8a3c2 |
|------|------|--------|-------------------|
| [exec-summary-judge-regen-loop-closure-d8f3a1.md](exec-summary-judge-regen-loop-closure-d8f3a1.md) | **Parent (COMPLETED)** | DONE | Chassis + post-regen X2 green; **does not** enforce G3 monotonicity or best-of publish |
| [exec-summary-failed-run-persistence-notion-e7c4b2.md](exec-summary-failed-run-persistence-notion-e7c4b2.md) | **Sibling** | IN_PROGRESS (W1) | Persists receipt-bound pool + Notion index; **mirrors** f8a3c2 publish selection only |
| [exec-summary-x1d-dimension-verdicts-e8f4a2.md](exec-summary-x1d-dimension-verdicts-e8f4a2.md) | Orthogonal | COMPLETED | `dimension_verdicts_snapshot` inputs for G3 tie-break |
| [exec-summary-qwen-regen-token-budget-c4e8a1.md](exec-summary-qwen-regen-token-budget-c4e8a1.md) | Orthogonal | COMPLETE | Token budget; no accept/publish policy |

**Brown fixture anchor (W5 replay):** `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_070105` — floor 4.2; cycle 1 must become `publish_eligible: false` after W1–W3.

---

**GAP-1: ChatGPT score 4.6→4.5 in cycle receipt without rescore**

- Likely snapshot artifact; W1.1 fixes delta reporting.

**GAP-2: Partial `final_publish_baseline` landed without monotonicity**

- W3 subsumes; do not rely on last_regen publish alone.

**GAP-3: exploratory_full_paragraph_regen flag**

- Defer env wiring to W4; default off.

**GAP-4: Split-brain publish (partial fix on branch)**

- W3 artifact rebind + digest integrity supersedes `final_publish_baseline` without rebind.

---

## Negative Test Matrix (H-5 — required)

| Test | Assert |
|------|--------|
| `test_regen_output_changed_trigger_regression_rejected` | `output_changed=true`, Claude 4.0→3.6 → `accepted=false`, `publish_eligible=false`, `reject_gate=trigger_judge_regression` |
| `test_parse_ok_x2_pass_alone_not_pool_eligible` | parse + X2 pass without G3 → not added to pool |
| `test_regen_outcome_not_improved_when_scratch_wins` | all regens regress → `regen_outcome=no_acceptable_candidate` or `floor_not_met`, NOT `improved`; `final_publish_baseline=scratch` |
| `test_certified_blocked_without_full_panel_scores` | published regen + `carried_forward` scores → CERTIFIED impossible |
| `test_certified_blocked_any_judge_below_floor` | full panel below floor → not CERTIFIED |
| `test_publish_integrity_digest_mismatch_fails` | `published_candidate_digest != final_artifact_digest_source` → fail closed |
| `test_g1_ambiguous_metric_rejects` | two facts conflict → `ledger_metric_sync_ambiguous` |
| `test_g3_unknown_rescore_rejects` | UNKNOWN trigger rescore → `trigger_judge_unknown` |

---

## Definition of Done

DoD-1: G3 deterministic semantics + `trigger_judge_unknown` (unit)

- Evidence: `pytest tests/unit/apps_rg/test_executive_summary_judge_remediation.py -q` includes negative matrix (20 passed 2026-05-26)
- Status: DONE

DoD-2: G1 fail-closed sync with per-row receipt

- Evidence: `pytest tests/unit/apps_rg/test_executive_summary_g1_ledger_metric_sync.py -q` (3 passed 2026-05-26)
- Status: DONE

DoD-3: `CandidateSnapshot` + full-panel rank + scratch wins when all regens regress

- Evidence: unit + `candidate_pool_summary.json` from fixture replay
- Status: DONE

DoD-4: Artifact rebind — `published_candidate_digest == final_artifact_digest_source`

- Evidence: [publish_integrity_receipt.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_080609/publish_integrity_receipt.json)
- Status: DONE

DoD-5: **Canonical CLI** Brown run @ floor 4.2 — all § W5.0 artifacts present

- Evidence: [exec_summary_20260526_080609](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_080609); verifier PASS
- Status: DONE

DoD-6: `judge_remediation_cycles.json` schema_version=2; v1 not interpreted as control proof

- Evidence: live run `schema_version: 2` + unit verifier test
- Status: DONE

DoD-7: Closeout + `no_agentic_core_diff_receipt.json` (zero agentic_core files)

- Evidence: [exec_summary_judge_regen_control_loop_closeout_20260526.md](../../docs/reports/cursor/exec_summary_judge_regen_control_loop_closeout_20260526.md)
- Status: DONE

DoD-8: Parent regen loop tests still PASS

- Evidence: `pytest tests/unit/apps_rg/test_executive_summary_judge_regen_loop.py -q` → 8 passed
- Status: DONE

DoD-9: Floor matrix helper output (optional index only)

- Evidence: deferred (W5.1 optional); helper columns updated
- Status: DEFERRED

### Verification vs Deferral

| Item | In scope | Deferred |
|------|----------|----------|
| H-1–H-10 hardenings | ✅ W1–W5 | — |
| G4 optional on cycle accept | ✅ | — |
| G4 mandatory for CERTIFIED | ✅ W3 | — |
| Core runner changes | — | `touches_agentic_core=false` |
| CERTIFIED at floor 4.4 matrix | — | Operator ship |
| `max_semantic_regen_attempts` > 1 | — | After W5 PASS |

---

## Key Seam Files

| File | Change |
|------|--------|
| [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py) | `CandidateSnapshot`, pool, G3, full-panel rank, artifact rebind |
| [executive_summary_judge_remediation.py](apps_rg/runtime/sections/executive_summary_judge_remediation.py) | G3 evaluator, delta_class, soft vs full rescore |
| [executive_summary_judge_regen_loop.py](apps_rg/runtime/sections/executive_summary_judge_regen_loop.py) | G1 fail-closed sync, snapshot freeze helpers |
| `apps_rg/runtime/sections/executive_summary_candidate_pool.py` (new) | Immutable snapshot + digest (if split from lane) |
| [executive_summary_repair_policy.py](apps_rg/runtime/sections/executive_summary_repair_policy.py) | Env: exploratory full paragraph (default off) |
| [run_exec_summary_floor_matrix.py](tools/cursor/run_exec_summary_floor_matrix.py) | Matrix columns for review |

---

## Marker Quick Reference

```
PLAN_CREATED: slug=exec-summary-judge-regen-control-loop-f8a3c2 path=.cursor/plans/exec-summary-judge-regen-control-loop-f8a3c2.md status=Not Started
WAVE_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 wave=0 note="Notion verified In Progress, parent traceability, Brown fixture ref, w0 receipt"
WAVE_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 wave=1 note="+4 g3 tests, 3 files, scope=G3-monotonicity; 070105 Claude 4.0→3.6 rejected"
WAVE_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 wave=2 note="+3 g1 tests, 2 files, scope=G1-ledger-metric-sync; 070105 row3 10%→40%"
WAVE_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 wave=3 note="+candidate_pool, lane publish argmax, 7 pool tests; 070105 rank→scratch"
WAVE_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 wave=4 note="+delta_policy G5 schema_v2 stderr matrix; 11 W4 tests"
WAVE_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 wave=5 note="canonical CLI exec_summary_20260526_080609 verifier PASS; closeout; no core diff"
PLAN_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 note="W0–W5 DONE; W5.1 floor matrix optional deferred"
```

**Emitted (W0):** `WAVE_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 wave=0 note="Notion verified In Progress, parent traceability, Brown fixture ref, w0 receipt"`

**Emitted (W1):** `WAVE_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 wave=1 note="+4 g3 tests, 3 files, scope=G3-monotonicity; 070105 Claude 4.0→3.6 rejected"`

**Emitted (W2):** `WAVE_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 wave=2 note="+3 g1 tests, 2 files, scope=G1-ledger-metric-sync; 070105 row3 10%→40%"`

**Emitted (W3):** `WAVE_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 wave=3 note="+candidate_pool, lane publish argmax, 7 pool tests; 070105 rank→scratch"`

**Emitted (W4):** `WAVE_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 wave=4 note="+delta_policy G5 schema_v2 stderr matrix; 11 W4 tests"`

**Emitted (W5):** `WAVE_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 wave=5 note="canonical CLI exec_summary_20260526_080609 verifier PASS; closeout; no core diff"`
