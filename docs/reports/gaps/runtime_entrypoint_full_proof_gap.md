# GAP — runtime_entrypoint_full_proof_gap

- **Severity**: P0 architecture proof gap
- **Status**: OPEN
- **Owner**: TBD
- **Filed**: 2026-04-30
- **Related ADR**: TBD (likely ADR-NNN — Integrated runtime entry point)
- **Blocks**: INTEGRATED_RUNTIME_PROOF certification for L0 routing (R1A, R1B, R3, R4, R5, R3R4)

## Finding

No single production runtime entry point in this repository drives the full
governed sequence

```
U0 (intake) -> L1 (planning) -> L0 (routing/gates) -> RET or L2 -> Exit -> L6 (exhaust seal)
```

end-to-end while emitting the canonical proof artifacts at each stage.

The 9 named runtime contracts each have a real production producer:

| Contract | Producer module | Status |
|---|---|---|
| `ValidatedRequest` | `agentic_core/L0_routing/intake/validated_request.py` | exists |
| `L1PlanContract` | `agentic_core/L1_cognition/types/plan_contract_types.py` | exists |
| `L0RouteContract` | `agentic_core/L0_routing/reasoning/route_gates.py` | exists |
| `TerminalRetPacket` (R1A/R1B/R5) | `agentic_core/L0_routing/doctrine/...` (decisional types) | exists |
| `ExitReviewPacket` | `agentic_core/L3_orchestration/exit_eval/v6/preflight.py` | exists |
| `V6Disposition` (X3) | `agentic_core/L3_orchestration/exit_eval/v6/x2_matrix.py` | exists |
| `ExhaustManifest` (runtime exhaust seal) | `agentic_core/L3_orchestration/exit_eval/v6/return_payload.py` | exists |
| `ReplayKey` | `agentic_core/L0_routing/reasoning/route_gates.canonical_request_hash` | exists |
| `UWGCommitReceipt` (commit arms only) | `agentic_core/L4_state/utils/memory/uwg/...` | exists |

What does NOT exist is a single production callable — for example
`agentic_core.runtime.integrated_route_pipeline.run(validated_request) -> RuntimeResult` —
that, when invoked once with a `ValidatedRequest`, deterministically:

1. Validates and consumes the `ValidatedRequest`.
2. Drives L1 planning and emits an `L1PlanContract`.
3. Calls `check_route_gates` (or successor) and emits the `L0RouteContract`.
4. Branches on `execution_form`:
   - `terminal_return` (R1A / R1B / R5) — returns the cached or fallback payload, seals exhaust, no L2.
   - `single_step` (R3 / R4) — invokes one L2 step, seals exhaust.
   - `multi_step` (R3R4) — invokes L3 orchestration, then exit.
5. Hands off to `ExitEvalPipeline.run`.
6. Emits `ExhaustManifest` and (for commit arms) `UWGCommitReceipt`.

Today, every harness that claims to exercise this sequence — including
`scripts/proof/run_end_to_end_runtime_proof.py` and
`tests/e2e/proof/harness.py` — composes the steps from the test layer
rather than calling a production orchestrator. The contracts on the
boundary are real production types, but the orchestration is not.

## Why this matters (proof classification)

This repository now distinguishes three proof tiers:

| Tier | Meaning | Today's status |
|---|---|---|
| **COMPONENT_PRIMITIVE_PROOF** | A single production primitive works in isolation (e.g. `L1ExactCache.set/get`) | passing for cache primitives |
| **COMPOSITION_PROOF** | Real production components are exercised in sequence by a harness; each artifact carries provenance back to its production producer | achieved by `scripts/proof/run_l0_route_proof_v2.py` for R1A/R1B |
| **INTEGRATED_RUNTIME_PROOF** | A single production runtime entry point drives the full pipeline; the harness only feeds it a `ValidatedRequest` and observes emissions | **BLOCKED** by this gap |

Without an integrated runtime entry point, no proof harness — no matter
how strict — can certify INTEGRATED_RUNTIME_PROOF, because there is no
"runtime" to invoke; there are only well-typed components composed by
test code.

## Required next remediation

Implement or expose **one** production-layer callable that satisfies all
of the following (deterministically, in a single call):

1. **Single entry**: takes a `ValidatedRequest`, returns a structured
   `RuntimeResult` containing references (not duplicates) to every
   contract emitted along the way.
2. **Production-emitted contracts**: each emission happens INSIDE
   production code — the entry point composes the production layers, not
   the test harness. The harness's only job is to feed a
   `ValidatedRequest` and read the final `RuntimeResult`.
3. **Provenance chain**: every artifact's `upstream_artifact_ref` points
   to the digest of its predecessor. The chain is rebuildable by
   inspecting `RuntimeResult` only.
4. **OTEL parent-child**: route span, exit span, exhaust-seal span all
   share one trace and form a parent-child tree rooted at the entry
   span.
5. **Deterministic replay**: invoking the entry point twice with the
   same `ValidatedRequest`, `policy_hash`, and `blueprint_hash` produces
   identical `RuntimeResult.deterministic_digest`.
6. **No-bypass guarantees**: TERMINAL_RET arms cannot reach L2; SINGLE
   and MULTI cannot bypass `ExitEvalPipeline`; commit arms cannot
   bypass UWG.

Suggested home: `agentic_core/runtime/integrated_route_pipeline.py`.
Suggested ADR title: "Integrated runtime entry point for L0->Exit
governed routing (resolves runtime_entrypoint_full_proof_gap)".

## Acceptance for closing this gap

This gap can be closed when ALL of the following hold:

- [ ] A production callable exists at `agentic_core/runtime/<file>.py` matching the requirements above.
- [ ] `scripts/proof/run_l0_route_proof_v2.py` is updated so that, when invoked with `--integrated-entry-point`, it invokes that callable and emits `proof_classification = INTEGRATED_RUNTIME_PROOF` per scenario.
- [ ] `scripts/proof/assert_l0_route_proof.py` accepts `INTEGRATED_RUNTIME_PROOF` only when `bundle.integrated_runtime_entry_point_used == true` and the entry-point module path is under `agentic_core/`.
- [ ] R1A and R1B scenarios pass in BOTH modes: `composition` (today) and `integrated_runtime` (post-fix).
- [ ] An ADR documents the entry point's contract and its OTEL span parent-child shape.

Until all five items are checked, the L0 routing proof status is
**COMPOSITION_PROOF — PASS** for R1A/R1B and **INTEGRATED_RUNTIME_PROOF
— BLOCKED** workspace-wide.

## Related artifacts

- Composition proof harness: `scripts/proof/run_l0_route_proof_v2.py`
- Assertion script: `scripts/proof/assert_l0_route_proof.py`
- Deprecated primitive proof: `artifacts/proof/l0_route_proof.md` (downgraded to COMPONENT_PRIMITIVE_PROOF)
