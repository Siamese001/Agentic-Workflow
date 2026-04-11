---
trigger: always_on
---
# HITL Core Pipeline

When facing a decision point, run this pipeline — no exceptions.

## Pipeline

1. **STOP** before taking action
2. **Generate candidates** — all plausible approaches
3. **Score** each — `confidence_score` in [0.00, 1.00]
4. **Filter** — suppress below `surface_threshold = 0.72`
5. **Dominance rule** — if top scores ≥ 0.85 AND gap to next ≥ 0.12, surface only the top option
6. **Material-distinctness** — collapse cosmetic variants; surface only options that differ on execution path, risk, reversibility, outcome, dependencies, time/cost, or governance
7. **Surface 1–N options** via `ask_user_question` — ALL analysis INSIDE description field, never in chat prose
8. **Wait** for explicit user selection
9. **Execute** only the chosen option — before executing, emit on its own line in the response:
   `DECISION_CAPTURED: type=<type>, repo_area=<area>, selected=<chosen_label>, outcome=executed`
   `type` = §HITL-1 class (`refactor_scope`, `architecture_choice`, `deletion_strategy`, `anti_pattern`, `dependency_addition`, `test_strategy`, `error_handling`). `repo_area` = most specific module/file path for the current task. `selected` = exact chosen option label (no commas).

If no candidate clears 0.72: emit `LOW_CONFIDENCE_AMBIGUITY`. Route to clarify/replan/abstain. Do not fabricate options.

## Continuous Execution

Execute continuously WITHOUT stopping UNLESS a genuine HITL decision point is reached.

FORBIDDEN: stopping after tool calls to check in; asking permission for deterministic actions; presenting options when there is one correct path; breaking work into artificial phase-breaks; summarizing while work is incomplete.

REQUIRED: chain all deterministic tool calls; stop only when genuine decision ambiguity exists after scoring; put ALL analysis inside the ask_user_question description field.

## ask_user_question Format

question field MUST include this header packet:

    Recommended: <option_title>
    Why it wins: <one sentence, case-specific, not generic>
    What you are optimizing for: <the actual goal this decision serves>
    What is being traded off: <the precise cost of the winning path>
    Candidates evaluated: N | Surfaced: M | Suppressed (low confidence): X | Suppressed (non-distinct): Y

Each option description uses the HITL-10 shape. See hitl-decision-points.md.

FORBIDDEN: bare ask_user_question after analysis prose. FORBIDDEN: padding options to a minimum count. FORBIDDEN: generic pros/cons without architecture-specific justification.

## Bypass Conditions

HITL skipped ONLY when: fixing typos/whitespace/formatting; single correct solution exists (syntax error, import error); user gave explicit unambiguous directive; emergency rollback; auto-fixable lint violations.

## Thresholds (SSOT)

| Parameter | Value |
|-----------|-------|
| surface_threshold | 0.72 |
| high_confidence_band | 0.85 |
| dominance_score_threshold | 0.85 |
| dominance_delta | 0.12 |
| max_surface_options | 4 |

## Extended Doctrine

Full decision-point triggers, option shape contract (HITL-10), scoring guidance, and telemetry format:
- hitl-decision-points.md (model_decision trigger)
