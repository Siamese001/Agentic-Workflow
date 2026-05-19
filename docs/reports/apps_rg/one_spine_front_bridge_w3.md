# One-spine front bridge (Wave 3)

Generated: 2026-05-19T15:15:01.701502+00:00
**STATUS: PASS**

Front-spine bridge enforced for product-visible proof_pool via load_section_proof_for_lane; kill switch enabled by default.

## Contracts added or emitted

- ValidatedRequest
- L1PlanContract
- RouteContract

## Kill switch

- Enabled: True
- Disable env: `APPS_RG_SECTION_FRONT_SPINE_KILL_SWITCH=0`

## Proof pool preconditions

- Required: ValidatedRequest, L1PlanContract, RouteContract

## Fixture / dev bypass

- non_product_certified=True or tests/_apps_contract conftest activate_fixture_dev_bypass

## Open gaps

- Wire spine C0 retrieve + FinalEvidenceContract before section PA for grounded lanes
- Map section X3 to spine ExitDispositionReceipt
- Bounded tests/_apps_contract triage (full suite still non-dispositive)
