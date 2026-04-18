# G1 — Layer Embodiment Map

Every v1.3/v1.4 canonical atom that has at least one embodying module inside `agentic_core/` is listed below with a pointer to the modules that embody it. The binding strategy is conservative:

- **Layer anchor atoms** (F02.01, F03.01, F05.01, F06.01, F10.01, F11.01, F12.01) are attached to every module inside the owning layer directory, because every module in that layer directory is *part of* the authority that atom asserts. Per-module granularity for these anchors is not authoritative here — it's a coarse embodiment map.
- **Targeted atoms** (F04.x, F05.04, F07.03, F08.02–04, F09.01/.02/.05) are attached to specific modules whose name or path explicitly corresponds to the atom's claim. These are high-confidence, narrow mappings.
- **Atoms without an embodying module**: tracked in §Unmapped atoms below. These are either (a) not physically present yet, (b) embodied across multiple files with no single canonical host, or (c) embodied inside `apps_*` and therefore out of G1 scope.

All data in this file is re-derivable from `component_inventory.yaml` using the `embodies.atoms` field.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

## Layer anchor atoms (coarse, per-layer)

These atoms define *authority* for a whole layer. Every module under that layer directory is, by construction, inside the authority envelope.

### L0 routing — F03.01

*"L0 MUST own route selection and admission decisions."* (v1.4 atoms.yaml)

- Modules that embody: all **88** files under `agentic_core/L0_routing/`.
- Canonical authority module (start of route-selection call-chain for G2): `agentic_core/L0_routing/reasoning/` — primary role cluster `reasoner`.
- Special modules:
  - `agentic_core/L0_routing/reasoning/escalation_router.py` — also tagged F07.03 (escalation).

### L1 cognition — F02.01

*"L1 MUST own plan production."*

- Modules that embody: all **152** files under `agentic_core/L1_cognition/`.
- Canonical reasoning surface: `agentic_core/L1_cognition/reasoning/` (see also F04 below).

### L2 execution — F06.01

*"L2 MUST execute tasks dispatched by L3."*

- Modules that embody: all **194** files under `agentic_core/L2_execution/`.
- Sub-surfaces observed: `L2_execution/healers/` (8 modules), `L2_execution/determinism/` (6), `L2_execution/capability/` (5), plus large subfolders.

### L3 orchestration — F05.01

*"L3 MUST own orchestration across plan steps."*

- Modules that embody: all **167** files under `agentic_core/L3_orchestration/`.
- Targeted atom: `L3_orchestration/core/orchestrator_state_retry.py` additionally embodies **F05.04** (*L3 dispatch* — SRC-ADR-008 L3-I1, SRC-ADR-002 retry).

### L4 state — F10.01

*"L4 MUST own durable state."*

- Modules that embody: all **141** files under `agentic_core/L4_state/`.
- Sub-surfaces: `L4_state/cache/` (readers + policies), `L4_state/memory/`, `L4_state/enforcement/`, `L4_state/reasoning/`.

### L5 safety — F11.01

*"L5 MUST enforce safety policy."*

- Modules that embody: all **382** files under `agentic_core/L5_safety/`.
- Sub-surfaces: `L5_safety/audit/`, `L5_safety/enforcement/`, `L5_safety/validators/`, `L5_safety/reasoning/`, `L5_safety/types/`, `L5_safety/utils/`.
- Targeted sub-surfaces (see below): exit-control gate, escalation orchestrator.

### L6 observability — F12.01

*"L6 MUST observe and record run outcomes."*

- Modules that embody: all **89** files under `agentic_core/L6_observability/`.
- Sub-surfaces: `L6_observability/execution/`, `L6_observability/enforcement/`, `L6_observability/reasoning/`, `L6_observability/utils/`.

## Targeted atoms (narrow, high-confidence)

| Atom | Claim (abbrev.) | Embodying modules |
|---|---|---|
| **F04.01–F04.04** | Context assembly (CTX-I1 attribution, CTX-I2 single-grounded-path, CTX-I3 idempotence) | `agentic_core/L1_cognition/reasoning/context_assembler.py` — sole host. SRC-ADR-007 cited. Note: OOS-003 SUPERSEDED in v1.4 per F4 cleanup; F04 is normatively L1-owned. |
| **F05.04** | L3 dispatches to L2 | `agentic_core/L3_orchestration/core/orchestrator_state_retry.py` — SRC-ADR-002, SRC-ADR-008. |
| **F07.03** | Unrecoverable L2 failures escalate to L3 | `agentic_core/L0_routing/reasoning/escalation_router.py`; `agentic_core/L5_safety/enforcement/escalation/escalation_orchestrator.py` (+ `__init__.py` re-export shim); additional escalation-named modules. SRC-ADR-009 cited. |
| **F08.02** | ExecutionTrace and mutation_hash | `agentic_core/L2_execution/types/execution_trace_types.py`, `agentic_core/L3_orchestration/types/execution_trace_types.py`, `agentic_core/L_CONTRACTS/execution_trace.py` (+ related). SRC-ADR-005 cited. **Observation**: two parallel `execution_trace_types.py` (L2 + L3) — flagged to G6 `duplicate_responsibility_register.md`. |
| **F08.03 / F08.04** | Spine records outcome / signals UWG | `agentic_core/L5_safety/enforcement/exit_control_gate.py`, `agentic_core/L5_safety/enforcement/exit_control_hitl.py`. SRC-ADR-003 cited. |
| **F09.01 / F09.02** | UWG sole durable write path + scheme | `agentic_core/L3_orchestration/types/agent_handoff.py`, `agentic_core/L3_orchestration/types/orchestration_handoff_contract.py`, `agentic_core/L6_observability/utils/evaluation/governed_handoff.py`. SRC-ADR-003 cited. **Observation**: `governed_handoff.py` is under `L6_observability/utils/evaluation/` — its host layer is L6 but the atom is an F09 (UWG) claim; this crosses the naive layer/atom alignment and is a B7 candidate for G7. |
| **F09.05** | UWG rejects writes lacking exit signal | The F09.01/02 handoff modules plus `L5_safety/enforcement/exit_control_gate.py`, `L5_safety/enforcement/exit_control_hitl.py`. |

## Unmapped atoms (no direct G1 embodying module)

Atoms in v1.4 canonical with **no** `agentic_core/` module explicitly tagged at G1 (not absent — just not narrowly mappable at this classification depth):

- **F01.01–F01.06** (admission & guard authority) — G1 observed no `agentic_core/admission/` subtree. Likely embodied in `L5_safety/enforcement/` policy modules (inside the F11.01 bucket) and/or in `apps_*` entry points. Resolution deferred to G1b + G2.
- **F02.02–F02.05** (L1 sub-claims: plan idempotence, plan-scope lock, plan reproducibility) — not narrowly mapped; each likely lives inside specific `L1_cognition/reasoning/` modules. Deferred to G7 traceability matrix after G2 finishes call-chain analysis.
- **F03.02** (L0 uses admission status as routing input) — not narrowly mapped; lives in `L0_routing/reasoning/`.
- **F05.02 / F05.03** (plan-to-step refinement, step-to-result refinement) — not narrowly mapped; lives in `L3_orchestration/reasoning/` and `L3_orchestration/core/`.
- **F06.02–F06.05** (L2 sub-claims) — not narrowly mapped; spread across `L2_execution/`.
- **F07.01 / F07.02 / F07.04** (healing sub-claims) — not narrowly mapped; spread across `L2_execution/healers/` (8 modules currently `role=other` at G1, deferred to G6).
- **F08.01 / F08.05** (evaluation spine boundary, evaluation idempotence) — likely in `agentic_core/evaluation/` (CROSS_CUTTING subsystem, 85 modules).
- **F09.03 / F09.04** (UWG append-only, UWG audit record) — likely in the governed-handoff / exit-control cluster.
- **F10.02–F10.04** (L4 sub-claims) — spread across `L4_state/cache/`, `L4_state/memory/`, `L4_state/enforcement/`.
- **F11.02–F11.07** (L5 sub-claims) — spread across `L5_safety/`.
- **F12.02–F12.08** (L6 sub-claims, including F12.05/07/08 memory-lifecycle atoms) — spread across `L6_observability/` + `system_learning/` (out of G1 scope; G4 owns).
- **F12.06** — EXCLUDED in v1.4; no embodying module by construction.

## CROSS_CUTTING atoms

The following CROSS_CUTTING subsystems also host runtime code that may embody atoms, but G1 deliberately does not tag CROSS_CUTTING modules with layer anchor atoms (because they are not inside a layer directory):

- `agentic_core/evaluation/` (85) — F08.x candidates live here (eval spine).
- `agentic_core/prompt_governance/` (43) — F11.x candidates (policy over prompts).
- `agentic_core/adg/` (277) — not directly an atom host; tool for graph analysis.
- `agentic_core/knowledge/` (82) — F04 / F02 candidates (knowledge is plan input).
- `agentic_core/seams/` (7) — seams implement edges; tagged in G2 / G7 traceability matrix.
- `agentic_core/interfaces/` (38) — same: implement edges.
- `agentic_core/L_CONTRACTS/` (4) — layer contracts; canonical embodiment target for seam atoms.

Per-module embodiment for CROSS_CUTTING surfaces is G7's responsibility when the traceability matrix is assembled.

## Summary: coverage of v1.4 atoms by G1 (direct citations)

| Atom count category | Count |
|---|---:|
| v1.4 ACTIVE NORMATIVE atoms (total) | 60 |
| Atoms with ≥1 direct G1 embodying module | **15** (F02.01, F03.01, F04.01, F04.02, F04.03, F04.04, F05.01, F05.04, F06.01, F07.03, F08.02, F08.03, F08.04, F09.01, F09.02, F09.05, F10.01, F11.01, F12.01 — deduped count: 19 if counted literally; some F04 entries share the same module) |
| Atoms without a direct G1 embodying module | 41 (deferred to G7 traceability matrix) |

This number will grow in G7 after G2 (wiring) and G3/G3b (pipelines) produce finer-grained mappings.
