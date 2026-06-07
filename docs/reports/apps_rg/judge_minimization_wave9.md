# apps_rg Judge Minimization Wave 9

## Scope

Wave 9 makes X1D judge defaults explicit and token-efficient without weakening proof gates:

- judges evaluate compact `GRADE_ONLY` packets;
- judges do not repair or rewrite candidate output;
- advisory and bullet lanes default to one judge;
- lanes whose X2 gates still require all judge providers keep the full panel;
- explicit CLI and `APPS_RG_E2E_X1D_JUDGES` overrides remain available for diagnostics.

## Default Policy

| Section | Default judges | Reason |
|---|---:|---|
| `competencies` | 1 | advisory taxonomy judge; not required for proof |
| `unify_bullets` | 1 | single composite bullet judge; optional adjudicator escalation |
| `ibm_bullets` | 1 | single composite bullet judge; optional adjudicator escalation |
| `headline` | 3 | X2 required-judge gate still expects full panel |
| `unify_narrative` | 3 | X2 required-judge gate still expects full panel |
| `ibm_narrative` | 3 | X2 required-judge gate still expects full panel |
| `executive_summary` | 3 | X2 required-judge gate still expects full panel |
| `final_aggregate_resume` | 3 | final proof policy remains enhanced/full-panel |

## Acceptance Evidence

- `apps_rg.runtime.section_cli_defaults.summarize_section_x1d_minimization_policy()` exports the canonical policy.
- `tests/unit/apps_rg/test_judge_minimization_wave9.py` verifies minimized defaults, override precedence, and compact non-repairing judge packet boundaries.
- `tests/unit/apps_rg/test_section_orchestration_dependency_order.py` verifies per-lane judge resolver threading through whole-run lane execution context.

## Follow-Up

Full-panel defaults can only shrink further after the related X2 `x2_x1d_required_judges_present` gates are revised with replacement proof authority.
