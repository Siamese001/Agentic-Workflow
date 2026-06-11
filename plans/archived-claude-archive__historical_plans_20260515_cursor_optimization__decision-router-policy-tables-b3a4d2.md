---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\decision-router-policy-tables-b3a4d2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\decision-router-policy-tables-b3a4d2.md'
source_sha256: 8a1f033afdac10e3ccec6586a4e32593d4ebaadda58e3d41ae4f3543f5e37b30
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Decision-Tree HOPs → Policy Tables (DecisionRouter primitive)

**Slug**: `decision-router-policy-tables-b3a4d2`
**Status**: In-progress (W1 + W2 landing this session; W3-W4 deferred with markers)
**Tier**: T3 (cross-layer refactor, multi-file, architecture decision)
**Created**: 2026-05-01

## Goal

Promote LIC HOPs that are **decision-tree leaves** out of class hierarchy into
declarative YAML policies consumed by a single generic `DecisionRouter`
primitive. HOP4 (Routing) and HOP7 (GateDecision) are pure lookup tables today
— they pay full Sovereign-dataclass overhead for what is fundamentally a
config dispatch. Imperative branches inside HOP1 (CXO precedence chain) and
HOP5 (`if archetype == "C_LEVEL": n_candidates = ...`) are the same pattern.

The 9 HOPs collapse to 6 once decision-tree leaves move to YAML; no genuine
pipeline stage (LLM synthesis, file I/O, vector retrieval, multi-rule scoring,
multi-artifact aggregation) is touched.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| **W1** | W1-P1, W1-P2, W1-P3 | Build `DecisionRouter` primitive + 2 YAML policies + unit tests | 18000 | YAML drives dispatch; first-match semantics; ROUTER_DECISION marker emission | **Done** | DecisionRouter passes table-driven tests for both policies; ROUTER_DECISION marker emitted per resolve |
| **W2** | W2-P1, W2-P2 | Wire HOP5 (PreFlightPolicy) and HOP6 (ExitPolicy); HOP4/HOP7 stay alive but become pass-through shims | 9000 | HOP4/HOP7 deletion deferred 90 days per constitutional §3 | **Done** | HOP5._process opens with route_constraints from policy; HOP6 attaches x3_disposition row to validation_results; tests green |
| **W3** | W3-P1, W3-P2 | Refactor HOP1 imperative classifier chain into `archetype_classifier.yaml` with golden-file parity; preserve LLM-fallback branch | 12000 | Classifier tree (CXO precedence, heuristic) is pure decision; LLM low-confidence path stays imperative | **Deferred** | DEFERRED_SCOPE marker (P3) |
| **W4** | W4-P1, W4-P2, W4-P3 | After 90-day deprecation: delete HOP4RoutingAgent.py + HOP7GateDecisionAgent.py; remove from hop_stage_registry; update apps_lic spine_manifest | 8000 | Constitutional §3 90-day deprecation window honored; zero non-shim references via ADG fan-in audit | **Deferred** | DEFERRED_SCOPE marker (P2) |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W1-P1 | DecisionRouter primitive | `apps_lic/policy/__init__.py`, `apps_lic/policy/decision_router.py` | First-match vs scored-match tradeoff; YAML schema validation at load | 7000 | Done |
| W1-P2 | Policy YAML files | `apps_lic/policy/exit_policy.yaml`, `apps_lic/policy/pre_flight_policy.yaml` | Capturing today's HOP4/HOP7 logic 1:1 with no behavior drift | 5000 | Done |
| W1-P3 | DecisionRouter unit tests | `tests/unit/apps/apps_lic/policy/test_decision_router.py` | Parametrized over policy rows × edge-case states; verifies ROUTER_DECISION emission | 6000 | Done |
| W2-P1 | HOP5 PreFlightPolicy wiring | `apps_lic/engines/HOP5GenerationAgent.py` | Inline `route_constraints = PreFlightRouter.resolve(hop1, mission_input)` at top of `_process`; emit ROUTE_RESOLVED trace; HOP4 still callable for back-compat | 5000 | Done |
| W2-P2 | HOP6 ExitPolicy wiring | `apps_lic/engines/HOP6ValidationAgent.py` | Attach `x3_disposition` (ALLOW/REVISE/DENY/HITL/ABSTAIN) to each validation row via ExitRouter; HOP7 reads disposition directly instead of severity remap | 4000 | Done |
| W3-P1 | archetype_classifier.yaml | `apps_lic/policy/archetype_classifier.yaml` | Encoding CXO precedence regex + heuristic keywords as policy rows | 7000 | **Deferred** |
| W3-P2 | HOP1 classifier refactor | `apps_lic/engines/HOP1ProfileAnalysisAgent.py` | Replace imperative chain; preserve LLM-fallback branch as code (it's synthesis, not lookup) | 5000 | **Deferred** |
| W4-P1 | Add 90-day deprecation banner | `HOP4RoutingAgent.py`, `HOP7GateDecisionAgent.py` | Emit DEPRECATED log, schedule deletion date | 1000 | **Deferred** |
| W4-P2 | Delete HOP4 + HOP7 source | `HOP4RoutingAgent.py`, `HOP7GateDecisionAgent.py` | Constitutional §3: AGENT-DELETION-AUTHORIZED marker required at deletion time | 4000 | **Deferred** |
| W4-P3 | Remove from hop_stage_registry + spine | `apps_lic/engines/hop_stage_registry.py`, `apps_lic/spine_manifest.yaml` | Update wiring; verify ADG fan-in zero post-deletion | 3000 | **Deferred** |

## ADG_HOTSPOT_REPORT

Hotspot analysis from `artifacts/adg/adg_indexed_05012026_0632.sqlite`:

| File | Layer | fan_in | fan_out | Archetype | Surface | Multiplier | Impact | Notes |
|---|---|---:|---:|---|---|:---:|---:|---|
| `apps_lic/engines/HOP4RoutingAgent.py` | L_APP | 0 | (n/a) | CENTRAL_DEPENDENCY → DEMOTE | None | ×1.0 | n/a | Zero direct module fan-in; consumed only via spine `hop_stage_registry.py`. Safe to demote to YAML. |
| `apps_lic/engines/HOP7GateDecisionAgent.py` | L_APP | 0 | (n/a) | CENTRAL_DEPENDENCY → DEMOTE | None | ×1.0 | n/a | Same shape as HOP4. Pure severity→action lookup. Safe to demote. |
| `apps_lic/engines/hop_stage_registry.py` | L_APP | 1 | 4 | ORCHESTRATOR | Execution | ×1.0 | medium | Spine that wires all 9 HOPs. Will need 1-line edit per deletion in W4. Updates are additive in W2 (new modules registered alongside old). |
| `apps_lic/engines/HOP5GenerationAgent.py` | L_APP | 1 | 11 | ORCHESTRATOR | Execution | ×1.0 | medium | Highest fan-out in apps_lic/engines. W2-P1 adds one new import + one helper call. No structural risk. |
| `apps_lic/engines/HOP6ValidationAgent.py` | L_APP | 1 | (n/a) | SAFETY_GATEKEEPER | Security | ×1.0 | medium | Last deterministic checkpoint. W2-P2 attaches x3_disposition rows; existing validation rules untouched. |
| `apps_lic/engines/HOP1ProfileAnalysisAgent.py` | L_APP | 1 | (n/a) | CENTRAL_DEPENDENCY | None | ×1.0 | low | W3 (deferred) restructures imperative classifier chain only; LLM fallback stays. |

Provenance: backend=sqlite_direct, snapshot=adg_indexed_05012026_0632.sqlite

## ADG_GRAPH_LAYER_EVIDENCE

**Materialized views consulted** (≥3 required):

1. `mv_hotspot_centrality` — confirmed `hop_stage_registry.py` fan_in=1 (the registry is the spine; everything else is a downstream consumer of the spine, not of the HOPs directly). All other HOP files show 0 module-level fan_in.
2. `mv_l2_phase_coverage` — apps_lic/engines is L_APP (not L2); not on the L2 phase critical path. Refactor blast-radius bounded to apps_lic/.
3. `mv_authority_boundary_breaches` — none on apps_lic/engines/HOP4 or HOP7. Safe to demote.

**Semantic edges relied on**: `imports` (none from outside apps_lic/engines into HOP4/HOP7); `flows_to` (HOP4 output → HOP5 only; HOP7 output → HOP8 only — single-consumer confirms decision-tree-leaf shape).

**P-view cross-references**:
- `v_p0_apps_direct_infra` — empty for HOP4/HOP7 (no infra coupling to fix).
- `v_p2_duplicated_adapters` — clean (no duplicate routing logic elsewhere).
- `v_p3_isolated_experimental` — HOP4/HOP7 do NOT appear (they are mainline, but that's why we're moving the policy out, not deleting outright in W2).

**Conclusion**: HOP4 and HOP7 are decision-tree leaves with zero direct module fan-in beyond the spine. Demoting their logic to YAML in W2 is structurally safe; deletion in W4 (post-90-day deprecation) only requires the 1-line spine edits enumerated in W4-P3.

## Out of Scope

- HOP1 classifier refactor (W3) — deferred; requires golden-file parity test design.
- HOP4/HOP7 source deletion (W4) — constitutional §3 mandates 90-day deprecation; cannot delete in same session as introduction of replacement.
- HOP9 dispatch policy refactor — HOP9 is a transformer, not a decision tree.
- Closed-loop router enforcement (§29) wiring of `DecisionRouter` into the 10-router ledger family — separate plan; this plan establishes the primitive.

## Bypass / Author-Gate

Per `author-gate-enforcement.md` "explicit unambiguous directive" bypass — user said "plan and implement above and mark complete in notion." Silent `DECISION_CAPTURED` marker emitted in the executing response.
