# ProceduralPattern:AppsRgL0CanonicalRouteContractInvariant

```json
{
  "entities": [{
    "name": "ProceduralPattern:AppsRgL0CanonicalRouteContractInvariant",
    "entityType": "ProceduralPattern",
    "observations": [
      "INVARIANT: apps_rg L0 RouteContract.route_id and route_family use canonical L0 branch vocabulary, while app-specific labels remain non-authority metadata.",
      "scope: apps_rg/runtime/bindings/l0_binding.py, apps_rg/runtime/bindings/l0_route_evidence.py, apps_rg/config/domain_contract/route_profiles.yaml",
      "enforcement: tests/_apps_contract/test_l0_routing_hardening.py plus tests/_apps_contract/test_l0_* L0-only suite",
      "violation_examples: using R4_MANAGED_DRAFT or R3_GENERATIVE as RouteContract.route_id/route_family; silently unsigned production route evidence; required gate UNKNOWN enabling allowed_next_stage",
      "canonical_pattern: route profiles declare canonical_route_id/app_route_id/production_enabled/test_only/required_activation_flags; L0 stamps route_digest, signing posture, gate block reason, replay_key, and snapshot_refs before downstream stages",
      "doctrine_ref: plans/apps-rg-l0-routing-only-a4c9e2.md; discovered: 2026-07-05, validated: 2026-07-05"
    ]
  }]
}
```
