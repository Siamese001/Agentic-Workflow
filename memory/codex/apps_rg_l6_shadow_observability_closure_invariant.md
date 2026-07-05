# apps_rg L6 shadow observability closure invariant

```json
{
  "entities": [{
    "name": "ProceduralPattern:AppsRgL6ShadowObservabilityClosureInvariant",
    "entityType": "ProceduralPattern",
    "observations": [
      "INVARIANT: Keep apps_rg L6 shadow observability post-run, read-only, evidence-classed, and future-run-only; apps_eval-bound proof is additive and never rewrites section runtime packages.",
      "scope: apps_rg/runtime/spine/l6_shadow_eval_runner.py, apps_rg/runtime/post_x3_completion.py, apps_rg/runtime/observability/trace_reconciliation.py, apps_eval/l6_shadow_bridge.py, agentic_core/L6_observability/shadow_eval/*",
      "enforcement: python scripts/governance/check_apps_rg_l6_observability_contract.py --json plus targeted L6/apps_eval pytest set",
      "violation_examples: writing microstep observations before trace_reconciliation.json exists; treating contract-only pseudo rows as proof; mutating l6_v40_shadow_eval_package.json after post-X3 apps_eval; using L6 proposals to alter current X3/Exit/L4",
      "canonical_pattern: emit trace reconciliation and l6_trace_observability_summary before microstep observations, write l6_v40_shadow_eval_package.json before l6_observability_closure_receipt.json, and use l6_section_apps_eval_bindings.json for post-X3 late binding",
      "doctrine_ref: plans/apps-rg-l6-shadow-observability-improvement-waves.md"
    ]
  }]
}
```

Discovered: 2026-07-05. Validated: targeted L6/apps_eval pytest set, contract verifier, receipt validator.
