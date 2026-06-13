# L0/L3 Doctrine Contracts Implementation — Plan b8c2a4

**Status:** In Progress
**Created:** 2026-04-26
**ADG Snapshot:** `04252026_0843` (84,920 nodes, 593,555 edges, healthy)
**Doctrine source:** `docs/reference/03_L0_Routing/03*.md` (10 files, fully ingested)

## Goal

Implement the formal data-class contracts and pure-function pipeline mandated by the
03.x L0 Routing + L3 Orchestration doctrine. Existing repo already covers parts of
03.5 (`V15RouteContract` in `agentic_core/L0_routing/types/route_contract_v15.py`)
and has a `v15_route_selector.py` reasoner. Missing: the formal named contract types
for L0.1 preflight, L0.2 deterministic selection, L0.3 terminal route decisions,
L0.4 single-step handoffs, L0.5 telemetry + replay manifest, L3.6 workflow eligibility,
L3.7 state ledger + step contract, L3.8 concurrency/quality/fallback/completion.

## Scope (DIRECTLY OBSERVED gaps from grep)

| Doctrine surface | Existing | Missing |
|---|---|---|
| 03.1 RouteDecisionInput etc. | none | RouteDecisionInput, RoutePreflightStatus, RouteDiscriminatorFrame, SourceAvailabilitySnapshot, RouteCandidateFrame, RouteInputAuditReceipt, `run_l0_preflight()` |
| 03.2 Deterministic selector | partial (v15_route_selector.py — different surface) | RouteScoreVector, FixedDecisionOrderReceipt, RouteSelectionReceipt, `select_route()` |
| 03.3 Terminal routes | partial (`SafeResponseType` in route_contract_v15.py) | ExactCacheRouteDecision, SemanticCacheRouteDecision, FallbackRouteDecision, HITLPostureAnnotation |
| 03.4 Handoffs | none | R3GroundedReadHandoff, R4SingleActionHandoff, R3R4ArgumentGroundingHandoff, DownstreamLayerRequirementMap |
| 03.5 RouteContract + telemetry + replay | partial (`V15RouteContract`) | RouteTelemetryEvent, RouteReplayManifest |
| 03.6 Workflow eligibility | none | L3WorkflowInput, ExecutionShapeClassification, WorkflowNode, WorkflowEdge, ManagedWorkflowBlueprint, `build_l3_workflow()` |
| 03.7 State ledger + step contract | none | L3StateLedger, NodeReadinessDecision, L3ContextBus, L3StepContract, StepResultIngest, `select_next_ready_node()`, `emit_step_contract()`, `ingest_step_result()` |
| 03.8 Concurrency/quality/completion | none | ConcurrencyPlan, QualityLoopPlan, FallbackCascadeState, WorkflowCompletionTest, SealedWorkflowPackage, governors |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.1, W1.2, W1.3 | L0.1 + L0.2 contracts + pipeline | ~12000 | New module `L0_routing/doctrine/`, no edits to existing v15 files | done | All W1 contracts validate, py_compile clean, unit tests pass |
| W2 | W2.1, W2.2, W2.3 | L0.3 + L0.4 + L0.5 telemetry/replay | ~10000 | Builds on W1 | done | All W2 contracts validate, telemetry digest deterministic |
| W3 | W3.1, W3.2, W3.3 | L3.6 + L3.7 + L3.8 contracts | ~16000 | New module `L3_orchestration/doctrine/` | done | DAG forward-only, completion test, sealed package validates |
| W4 | W4.1, W4.2 | Integration tests + harden | ~6000 | Builds on W1+W2+W3 | done | pytest green, py_compile clean across all new files |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | L0.1 preflight contracts | `L0_routing/doctrine/__init__.py`, `contracts_l0_1.py` | Frozen dataclasses, validation, hash digest | 4000 | done |
| W1.2 | L0.1 preflight pipeline | `L0_routing/doctrine/preflight.py` | Pure function, hard-fail conditions | 3000 | done |
| W1.3 | L0.2 selector | `L0_routing/doctrine/selector.py`, `contracts_l0_2.py` | Fixed decision order, deterministic | 5000 | done |
| W2.1 | L0.3 terminal routes | `L0_routing/doctrine/terminal_routes.py` | R1A/R1B/R5 + HITL posture | 3000 | done |
| W2.2 | L0.4 handoffs | `L0_routing/doctrine/handoffs.py` | R3/R4/R3R4 single-step | 3000 | done |
| W2.3 | L0.5 telemetry + replay | `L0_routing/doctrine/telemetry.py`, `replay.py` | Deterministic digest, no entropy | 4000 | done |
| W3.1 | L3.6 eligibility + DAG | `L3_orchestration/doctrine/__init__.py`, `eligibility.py` | Forward-only, no backward edges | 6000 | done |
| W3.2 | L3.7 state ledger + step contract | `L3_orchestration/doctrine/state.py` | Node readiness, context bus | 6000 | done |
| W3.3 | L3.8 concurrency/quality/completion | `L3_orchestration/doctrine/governance.py`, `completion.py` | Sealed workflow package | 4000 | done |
| W4.1 | Tests | `tests/agentic_core/L0_routing/doctrine/`, `tests/agentic_core/L3_orchestration/doctrine/` | Unit + integration coverage | 5000 | done |
| W4.2 | Harden + commit | repo-wide py_compile + pytest | Lint clean, no ADG regression | 1000 | done |

## ADG_GRAPH_LAYER_EVIDENCE

ADG snapshot `04252026_0843` healthy. New code lands in:

- **L0 layer** (`agentic_core/L0_routing/doctrine/*`) — graph-layer placement: layer=L0, fan_in expected=0 initially (new surface)
- **L3 layer** (`agentic_core/L3_orchestration/doctrine/*`) — graph-layer placement: layer=L3, fan_in expected=0 initially

Materialized views relevant to gravity check:
- `mv_graph_reverse_dependency_hotspots` — confirms no upward-direction imports
- `mv_dependency_cone_risk` — new modules expected to be leaves until consumed
- `v_p0_apps_direct_infra` — new doctrine modules MUST NOT import apps_*

Semantic edges expected on these new modules:
- `imports` — only stdlib + sibling doctrine modules
- `flows_to`, `controls_flow` — emergent once integrated
- `reads_from`, `writes_to` — pure data, no I/O

## ADG_HOTSPOT_REPORT

This is **new implementation, not refactoring**. No anti-pattern hotspots are
introduced because the contracts use:
- Specific exception type `DoctrineContractError(ValueError)` per contract module
- No `except Exception:` (constitutional §15)
- No `subprocess` calls (constitutional §14 N/A)
- No PowerShell (constitutional §0 N/A)

Risk surface intersection:
- **Execution surface**: contracts only declare; no execution
- **Write surface**: `write_authority=NONE_UNTIL_UWG` enforced
- **Security surface**: HMAC over canonical JSON; closed-vocab enums
- **State surface**: pure data; no mutation
- **Observability surface**: telemetry events emit `route_digest`/`event_hash`

Layer criticality multiplier: L0 ×2.0, L3 ×1.75. New modules add no current
violations; positive impact when other layers begin consuming them.

## Doctrine Compliance Checklist (per file)

Every doctrine file MUST:
1. Be `frozen=True` dataclasses
2. Validate in `__post_init__` with specific `DoctrineContractError`
3. Provide `canonical_payload()` and content hash (`sha256` of canonical JSON)
4. Honor "GLOBAL NO-OVERLAP LOCK" — no execution, no retrieval, no write
5. Use closed-vocabulary `Enum` for every taxonomic field
6. py_compile clean
7. Have at least one unit test asserting hard-fail validation
