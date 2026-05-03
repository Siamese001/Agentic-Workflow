# ADR-096 — L6 Observability Is Universally Importable (Leaf-Observer Doctrine)

Status: **Accepted** · 2026-05-03 · Tier: T2 governance · Layer: L6

## Context

ADR-095 ("L6 Observability Dependency Hygiene") codified the policy for L6 *importing from* lower layers (L6 is a leaf observer — imports should flow *into* it, not out). It does NOT address the symmetric question: **may lower layers (L_RUNTIME, L_OPS, L_TOOLS, L1..L5) import *from* L6?**

The ADG layer-gravity scanner currently flags 9 such edges as CRITICAL `violates` on snapshot `adg_indexed_05032026_0645.sqlite`:

| # | Source file | Line | Direction |
|---|---|---|---|
| 1 | `agentic_core/runtime/entrypoints/integrated_managed_workflow_run.py` | 68 | L_RUNTIME → L6 |
| 2 | `agentic_core/runtime/entrypoints/integrated_safe_reuse_run.py` | 76 | L_RUNTIME → L_TOOLS (veto_orchestrator) |
| 3 | `agentic_core/runtime/entrypoints/integrated_safe_reuse_run.py` | 119 | L_RUNTIME → L6 |
| 4 | `ops_scripts/ci/check_otel_genai_semconv_coverage.py` | 59 | L_OPS → L6 |
| 5 | `ops_scripts/ci/check_synthetic_trace_flag.py` | 33 | L_OPS → L6 |
| 6 | `ops_scripts/reports/desk_d_governed_board.py` | 29 | L_OPS → L6 |
| 7 | `ops_scripts/reports/governed_handoff.py` | 45 | L_OPS → L6 |
| 8 | `tools/maintenance/backfill_adg_graph_layer_sections.py` | 261 | L_TOOLS → L_OPS |
| 9 | `tools/otel/exercise_real_otel_pipeline.py` | 221 | L_TOOLS → L6 |
| 10 | `tools/proof/composition_proof_provenance_chain.py` | 61 | L_TOOLS → L6 |

(Probe script: `tools/analysis/_probe_p1p2_items.py`.)

Every one of these is **by design**:

- Runtime entrypoints (`integrated_managed_workflow_run`, `integrated_safe_reuse_run`) need L6 telemetry (`synthetic_trace_detector`, `runtime_exhaust_bundle`) to emit their structured runtime trace — that is the entrypoint's whole job.
- CI gates (`check_otel_genai_semconv_coverage`, `check_synthetic_trace_flag`) validate L6 semconv alignment — they must read L6 semconv constants to verify coverage.
- Reports (`desk_d_governed_board`, `governed_handoff`) are downstream-artifact emitters (the canonical home per ADR-095 §1) that consume L6 observability primitives.
- Tooling (`exercise_real_otel_pipeline`, `composition_proof_provenance_chain`) exercise / verify the OTEL pipeline — L6 is the subject under test.
- `tools/maintenance/backfill_adg_graph_layer_sections.py:261` → `ops_scripts/*`: a maintenance tool invokes an ops utility, not a gravity violation in spirit.

## Decision

**L6 observability is universally importable. All layers (L0..L5, L_RUNTIME, L_OPS, L_TOOLS, L_APP, L_APP_SHARED, L_SHARED) MAY import from `agentic_core/L6_observability/*` without layer-gravity penalty.**

This mirrors the L0-universal-import doctrine (`agentic_core/L5_safety/config/structure_blueprint/_constants.py`: "L0 is allowed for all layers"). The symmetry is deliberate:

- **L0 is the foundation** — constants, types, path primitives. Everyone depends on it.
- **L6 is the roof** — the observability surface. Everyone emits into it.

Both are universally importable because both sit at the boundary of the vertical architecture and act as broadcast channels rather than hubs.

### Enforcement

Per ADR-095 §1, the existing `# guardian: allow-layer-violation -- <reason>` inline comment mechanism (recognized by `tools/adg/core/guardian_filter.is_layer_violation_exempted` within 5 lines of the import) remains the single-source-of-truth marker. **Starting with this ADR, every L_X → L6 import carrying a `guardian: allow-layer-violation -- ADR-096` comment is formally approved.** CI enforcement does NOT need a new allowlist file; the guardian-comment scanner already honors the reason field.

For the 10 sites enumerated above, guardian comments land as part of this ADR's rollout (commit immediately following this ADR).

### Scope

- **In scope**: imports FROM L6 into any other layer.
- **Out of scope**: imports FROM L6 into lower layers (that is ADR-095's domain — L6 MUST stay a leaf observer, not import others except via the three categories ADR-095 whitelists).

### Exception: `L_RUNTIME → L_TOOLS` (site #2)

`integrated_safe_reuse_run.py:76` imports `tools.certification.safety.veto_orchestrator`. This is NOT an L6 crossing but still flagged CRITICAL because the runtime boundary imports *downward* into tooling. Documented exception per the existing W1p5 wiring — the runtime entrypoint is the only instantiator of `VetoOrchestrator`, avoiding double-registration. Guardian comment on that line references this ADR §"Exception" and preserves the W1p5 invariant.

### Exception: `L_TOOLS → L_OPS` (site #8)

`tools/maintenance/backfill_adg_graph_layer_sections.py:261` imports from `ops_scripts/*`. Maintenance tools consuming ops utilities is conventional; the boundary exists for historical reasons only. Guardian comment references this ADR §"Exception".

## Consequences

### Positive

- **Runtime entrypoints become legally expressible** — they can emit canonical telemetry without guardian-comment sprawl needing ad-hoc rationales.
- **CI gates / reporters become legally expressible** — they can read L6 semconv / primitives without every new gate reinventing a justification.
- **Symmetry with L0** — the architecture is now describable as "L0 and L6 are broadcast-boundary layers; L1..L5 flow between them with gravity."
- **Zero code-path impact** — no behavior changes, no new tests, no regression risk.

### Negative

- **Nothing enforced by gravity on L6 imports** — a new rule "do not import L6 from a test fixture" would require separate gating. Unlikely in practice; reporters and fixtures already have good instincts.
- **Guardian-comment sprawl** — every L_X → L6 edge now needs an inline comment. Acceptable because the comment also documents intent; future authors know to copy the pattern.

### Neutral / deferred

- **CI enforcement of guardian-comment presence on ALL L_X → L6 imports** — optional future gate. Current honor-system via `tools/adg/core/guardian_filter.is_layer_violation_exempted` is adequate because the fail-closed path (no comment → CRITICAL violation) already catches omissions at regen time.

## Cross-References

- ADR-095 — L6 Observability Dependency Hygiene (symmetric: L6 imports FROM lower)
- `adg-canonical-invariants.md` §6 — Layer Criticality Multipliers (L0 = ×0.75 at bottom, L6 = ×0.75 at top — both boundaries)
- `tools/adg/core/guardian_filter.py` — `is_layer_violation_exempted()` is the SSOT for exemption recognition
- Parent plan: `.windsurf/plans/p1p2-burndown-followup-a2e4c7.md` W2-01
