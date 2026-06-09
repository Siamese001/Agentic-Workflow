# apps_lic X1D Qwen Feedback Regeneration

Status: In Progress
Created: 2026-06-09
Worktree: `C:\Git\Agentic-Workflow-apps_lic`

## Objective

Add a bounded judge-feedback regeneration loop so live Claude X1D review failures can drive one controlled Qwen repair pass before final apps_lic Exit.

## Constraints

- Qwen/vLLM remains the generator.
- Claude remains the independent LLM-as-judge.
- `validation_exit.py` remains deterministic and provider-free.
- Missing, unavailable, fake, or non-live X1D judge results must fail closed and must not trigger regeneration.
- Repaired drafts must rerun X2 before any second X1D pass.
- Repaired drafts may only use claim IDs already present in the C0.3 sender proof packet.
- No automatic send or durable external write is permitted.
- Default bound is one repair pass; hard cap is two.

## Design

1. Keep W4 as the immutable original Qwen candidate batch.
2. Run the current W5 validation path once against the W4 selected candidate.
3. If W5 clears, stop.
4. If W5 is blocked because X1D is missing, unavailable, non-live, non-independent, wrong provider, or wrong model, stop.
5. If W5 is review-required due to judge score/fail, build a repair prompt from:
   - original selected draft,
   - failed judge IDs,
   - scores and thresholds,
   - judge issues,
   - judge required repairs,
   - recipient class/archetype,
   - message type,
   - target context and JD fields,
   - allowed C0.3 sender proof claim IDs.
6. Call live Qwen/vLLM in repair mode with repair temperature and one repair candidate.
7. Materialize a repaired candidate batch overlay that contains the original candidates plus a selected repair candidate.
8. Rerun X2 against the repair overlay.
9. If X2 passes, rerun live Claude X1D against the repaired candidate.
10. Stop with clear draft, review-required, or blocked. Never loop beyond the configured bound.

## Receipt Contract

W5 should expose:

- `x1d_regeneration_attempted`
- `x1d_regeneration_iteration_count`
- `x1d_regeneration_stop_reason`
- `x1d_regeneration_attempts`
- `parent_candidate_id`
- `repaired_candidate_id`
- `failed_judge_ids`
- `required_repairs`
- `pre_repair_scores`
- `post_repair_scores`
- Qwen repair model/provider/receipt

## Stop Conditions

- `already_clear`
- `repair_budget_exhausted`
- `x1d_not_review_required`
- `x1d_blocked_no_regeneration`
- `x2_failed_before_judge_feedback`
- `no_selected_candidate`
- `qwen_repair_unavailable`
- `qwen_repair_unparseable`
- `repair_same_as_parent`
- `repair_candidate_x2_failed`
- `repair_candidate_x1d_blocked`
- `repair_candidate_review_required`
- `repair_candidate_clear`

## Verification

- Unit test: review-required live X1D result triggers one Qwen repair and clears when repaired judge passes.
- Unit test: blocked X1D result does not trigger repair.
- Unit test: same-text repair fails closed as review-required with no second judge run.
- Unit test: repaired candidate reruns X2 and blocks if shape/claim gates fail.
- Regression tests: W5 wire-up, W7 validation, W4 candidate batch, W6 whole-message generation.
- Live harness: post-W7 12-contact run remains all clear with live Qwen and live Claude X1D.

## ADG Note

`adg_health` returned `Transport closed` in this Codex session. Direct code inspection was used as the fallback for impact assessment.
