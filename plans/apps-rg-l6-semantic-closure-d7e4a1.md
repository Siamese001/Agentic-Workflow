# apps_rg L6 Semantic Closure

Plan ID: `apps-rg-l6-semantic-closure-d7e4a1`

## Status

| Wave | Scope | Status |
|---|---|---|
| W0 | Baseline and defect characterization | Complete |
| W1 | Exit → UWG → boundary → apps_eval/L6 authority order | Complete |
| W2 | Independent persisted-observation parity | Complete |
| W3 | Split observability closure from eval-binding closure | Complete |
| W4 | Harden section late binding and legacy downgrade | Complete |
| W5 | Trace integrity and bounded advisory trends | Complete |
| W6 | Distinct-run recurrence and inert proposals | Complete |
| W7 | Four-level eval-ladder claim enforcement | Complete |
| W8 | CI, tests, run receipt, and PR | In Progress |

## Objective

Close the semantic gaps left by the structural L6 observability implementation while preserving the v40 authority model:

```text
Exit → UWG → completed-run boundary → apps_eval/L6 observation
```

apps_eval and L6 may produce completed-run evidence and future-run proposals. They may not authorize, veto, rescue, or mutate the current run.

## Implemented invariants

1. `complete_apps_rg_post_x3()` closes the Exit-cleared UWG decision before invoking apps_eval or L6.
2. The authority-order receipt records that apps_eval/L6 did not influence the current UWG decision.
3. apps_eval-generated L6 rows are labelled projection consistency and cannot mint `APPS_EVAL_BOUND_PROOF`.
4. Independent proof binds immutable persisted apps_rg observations to apps_eval rows using the full compound grain key.
5. Duplicate keys, malformed keys, missing rows, source mismatches, verdict mismatches, bundle mismatches, and authority mismatches fail closed.
6. Section observability closure can pass with eval binding pending.
7. Eval-binding closure is additive and does not rewrite section packages.
8. Legacy L6 packages remain advisory and cannot become bound proof.
9. Trace availability and mismatch trends are advisory and preserve local receipts as proof authority.
10. Longitudinal recurrence requires distinct completed runs.
11. Deterministic fixtures cannot claim lane, suite, or meta eval completion.

## Verification

```bash
python scripts/governance/check_apps_rg_l6_semantic_closure.py --json
python -m py_compile \
  agentic_core/L6_observability/shadow_eval/independent_parity.py \
  agentic_core/L6_observability/shadow_eval/longitudinal_patterns.py \
  apps_rg/runtime/post_x3_completion.py \
  apps_rg/runtime/spine/l6_shadow_eval_runner.py \
  apps_rg/runtime/observability/trace_trend.py \
  apps_eval/l6_shadow_bridge.py \
  apps_eval/l6_eval_ladder.py
python -m pytest \
  tests/unit/agentic_core/L6_observability/shadow_eval/test_independent_parity.py \
  tests/unit/agentic_core/L6_observability/shadow_eval/test_longitudinal_patterns.py \
  tests/unit/apps_rg/runtime/observability/test_trace_trend.py \
  tests/unit/apps_rg/runtime/observability/test_trace_reconciliation.py \
  tests/unit/apps_rg/runtime/spine/test_l6_shadow_eval_runner.py \
  tests/apps_rg/test_l6_v40_shadow_eval_runner.py \
  tests/unit/apps_rg/test_post_x3_completion.py \
  tests/apps_eval/test_l6_shadow_bridge.py \
  tests/apps_eval/test_l6_shadow_bridge_projection.py \
  tests/apps_eval/test_l6_eval_ladder.py \
  tests/e2e/test_l6_v40_apps_rg_apps_eval.py \
  -q --tb=short
```

## Non-claims

- This change does not weaken X2, X1D, X3, Exit, or UWG.
- It does not grant L6 current-run or direct L4 authority.
- Deterministic CI fixtures are micro/E2E contract tests, not live lane, suite, or meta promotion evidence.
- Live provider and human-label runs remain separately governed operational evidence.
