# G2 — Canonical Request Walk

The canonical request lifecycle, code-grounded. Each stage cites concrete modules from G1 `component_inventory.yaml`, the v1.4 atoms it embodies, and the observed ADG wiring between stages.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

## Walk: operator trigger → memory write-back

```
  ┌────────────────┐    ┌──────────────┐    ┌───────────────┐
  │  Operator /    │──▶ │   Admission  │──▶ │ Plan (L1)     │
  │  app_main()    │    │   (L5 at L0) │    │ F02.01        │
  └────────────────┘    │ F01.x F03.02 │    └───────┬───────┘
                        └──────┬───────┘            │
                               │                    ▼
                        ┌──────▼───────┐    ┌───────────────┐
                        │ Route (L0)   │◀───│ Context (L1)  │
                        │ F03.01       │    │ F04.x (ADR-7) │
                        └──────┬───────┘    └───────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │ Orchestrate (L3)                │
              │ F05.01 F05.04 (ADR-8 L3-I1/3)   │
              └───────────────┬─────────────────┘
                              │ dispatch
                              ▼
                   ┌──────────────────────┐
                   │ Execute (L2)         │
                   │ F06.x                │
                   └──────┬───────────────┘
                   fails? │ yes         │ ok
                          ▼             │
                   ┌─────────────┐      │
                   │ Heal (L2)   │      │
                   │ F07.01-04   │      │
                   │ (ADR-2/9)   │      │
                   └──────┬──────┘      │
                          │ unrecov.    │
                          ▼             │
                   ┌─────────────┐      │
                   │ Escalate    │      │
                   │ to L3       │      │
                   │ F07.03      │      │
                   └─────────────┘      │
                          ┌─────────────┘
                          │
                          ▼
               ┌─────────────────────┐
               │ Eval spine (L6/eval)│
               │ F08.01-05 (ADR-3)   │
               └──────────┬──────────┘
                          │ evaluate_sealed
                          ▼
              ┌──────────────────────────┐
              │ ExitControlGate (L5)     │
              │ F08.03-04 F09.05         │
              │ GovernedHandoffAgent     │
              └──────────┬───────────────┘
                         │ exit signal
                         ▼
                ┌────────────────────────┐
                │ UWG durable write      │
                │ F09.01 F09.02 F09.03   │
                │ L4_state (F10)         │
                └──────────┬─────────────┘
                           │
                           ▼
                ┌──────────────────────────┐
                │ L6 observe + record      │
                │ F12.01-08 (SRC-INT-004)  │
                │ memory write-back        │
                └──────────────────────────┘
```

## Per-stage grounding

### Stage 0 — Operator / app trigger

- **Entry points** (6 runtime apps): `apps_eval/__main__.py`, `apps_exec/__main__.py`, `apps_lic/__main__.py`, `apps_research/__main__.py`, `apps_rfp/__main__.py`, `apps_rg/__main__.py` + `apps_rg/bootstrap_runtime.py`.
- **Walk anchor**: `apps_rg/` (most entry points, heaviest cross-cutting coupling — per G1b).
- **Binding into core**: every app binds `agentic_core.runtime.contracts.lifecycle_trace_contract` (6 of 7 core apps) and `agentic_core.adg.runtime.behavioral_index` (7 of 7). Apps also reach `agentic_core.base_agents.SovereignBaseAgent` (2 apps directly; more through `apps_shared`).
- **v1.4 atoms**: no app-side atoms — apps are consumers.
- **ADG edge class**: `expected`.

### Stage 1 — Admission (L5 at L0 boundary)

- **Authority**: F01.x (admission) — embodied inside `agentic_core/L5_safety/enforcement/` and `agentic_core/L0_routing/enforcement/`.
- **Evidence of binding**: `mv_critical_path_segments` tags **L5 → L0 (368 imports, 101 files, both_on_spine=1)** — the only pair ADG marks as "both on spine". This is the admission seam.
- **Key modules (G1 layer L0 + L5)**:
  - `agentic_core/L0_routing/enforcement/safety_kernel_seam.py`
  - `agentic_core/L0_routing/enforcement/safety_enforcement_seam.py`
  - `agentic_core/L5_safety/enforcement/import_guard.py`
  - `agentic_core/L5_safety/enforcement/activation_gate.py`
- **v1.4 edges**: SRC-RULE-001 §1–§9 at admission.
- **ADG edge class**: `expected`.

### Stage 2 — Plan (L1)

- **Authority**: F02.01 ("L1 MUST own plan production"). 152 modules under `agentic_core/L1_cognition/`.
- **Key entry**: `agentic_core/L1_cognition/reasoning/context_assembler.py` (F04.01–F04.04, sole host).
- **Context grounding** (per SRC-ADR-007, OOS-003 superseded): L1 owns C0-equivalent responsibility in-process.
- **Binding**: L1 → L_RUNTIME (4,741 imports) = plan modules reference runtime contracts. L1 → L0 (17) = plan reads routing hints.
- **ADG edge class**: `expected`.

### Stage 3 — Route (L0)

- **Authority**: F03.01. 88 modules under `agentic_core/L0_routing/`.
- **Hotspot**: `agentic_core/L0_routing/config/path_constants.py` (blast radius 374, high_impact_hub) — every layer references L0 path constants.
- **v1.4 atoms**: F03.01, F03.02. Edge INT-F02.01-F01.05-01 (L0 admission → L1 plan) — NORMATIVE in v1.4.
- **ADG edge class**: `expected`.

### Stage 4 — Orchestrate (L3)

- **Authority**: F05.01, F05.04. 167 modules under `agentic_core/L3_orchestration/`.
- **Canonical dispatch**: `agentic_core/L3_orchestration/core/orchestrator_state_retry.py` (F05.04 — SRC-ADR-008 L3-I1 dispatch + SRC-ADR-002 retry).
- **Observed wiring**: L3 → L2 (30 imports) = dispatch direction. L3 → L_RUNTIME (5,677) = runtime contracts. L3 → L0 (54) = orchestrator reads routing.
- **v1.4 edges**: INT-F05.04-F06.01-01 (L3 dispatch to L2 — NORMATIVE in v1.4). INT-F07.03-F02.01-01 (L3→L1 escalation — NORMATIVE in v1.4, CONDITIONAL_ON).
- **ADG edge class**: `expected`.

### Stage 5 — Execute (L2)

- **Authority**: F06.01. 194 modules under `agentic_core/L2_execution/`.
- **Key sub-surfaces (from G1)**:
  - `L2_execution/healers/` (8 modules)
  - `L2_execution/determinism/` (6)
  - `L2_execution/capability/` (5)
  - Hotspot: `agentic_core/L2_execution/utils/write_gateway.py` (blast radius 80) — canonical L2 write path.
- **Observed wiring**: L2 → L_RUNTIME (9,485), L2 → L4 (37, state reads), L2 → L5 (19, policy check-ins), L2 → L0 (39 — possible back-reference to routing; unexpected).
- **ADG edge class**: mostly `expected`; L2 → L0 is `unexpected`.

### Stage 6 — Heal / retry (L2 healers)

- **Authority**: F07.01, F07.02, F07.04. Healers inside `agentic_core/L2_execution/healers/` (8 modules, role=other per G1 — deferred to G6 for role promotion to `healer`).
- **Retry config**: SRC-ADR-002 `RetryConfig`. Canonical holder: `agentic_core/L3_orchestration/core/orchestrator_state_retry.py` (F05.04).
- **Escalation**: when unrecoverable, escalate to L3 per F07.03.
  - `agentic_core/L0_routing/reasoning/escalation_router.py` (role=reasoner)
  - `agentic_core/L5_safety/enforcement/escalation/escalation_orchestrator.py` (role=policy)
- **v1.4 edge**: INT-F07.03-F02.01-01 (L3 emits re-plan to L1) — NORMATIVE, CONDITIONAL_ON.
- **ADG edge class**: `expected`.

### Stage 7 — Evaluation spine (eval + L6)

- **Authority**: F08.01–F08.05. Embodied across `agentic_core/evaluation/` (85 modules, CROSS_CUTTING) + `apps_eval/spine/`.
- **Key modules**:
  - `agentic_core/L2_execution/types/execution_trace_types.py` (F08.02)
  - `agentic_core/L3_orchestration/types/execution_trace_types.py` (F08.02 — duplicate; G6 candidate)
  - `agentic_core/L_CONTRACTS/execution_trace.py` (F08.02 — but **L_CONTRACTS fan-in is 1 from archived code only; effectively unused at runtime**; B7-G2-01)
- **Flow**: execute → trace → evaluate_sealed() → exit signal → UWG.
- **ADG edge class**: mostly `expected`; L_CONTRACTS zero-use is a B7 candidate.

### Stage 8 — Exit control gate (L5)

- **Authority**: F08.03, F08.04, F09.05. Sole hosts:
  - `agentic_core/L5_safety/enforcement/exit_control_gate.py`
  - `agentic_core/L5_safety/enforcement/exit_control_hitl.py`
- **v1.4 atoms**: F08.03 (spine records outcome), F08.04 (signals UWG), F09.05 (UWG rejects without exit signal).
- **v1.4 sources**: SRC-ADR-003.
- **v1.4 edges**: INT-F08.04-F09.01-01 and INT-F09.05-F08.04-01 — both NORMATIVE in v1.4 (upgraded from WEAK during F4).
- **ADG edge class**: `expected`.

### Stage 9 — UWG durable write (L4 state)

- **Authority**: F09.01, F09.02, F09.03, F09.04. Sole-writer seam.
- **Key modules**:
  - `agentic_core/L3_orchestration/types/agent_handoff.py` (F09.01/.02)
  - `agentic_core/L3_orchestration/types/orchestration_handoff_contract.py` (F09.01/.02)
  - `agentic_core/L6_observability/utils/evaluation/governed_handoff.py` (F09.01/.02) — **layer mismatch**: the GovernedHandoffAgent is hosted under L6_observability, but the atom is F09 (UWG). Flagged in G1 layer_embodiment_map; G7 will decide.
  - `agentic_core/L2_execution/utils/write_gateway.py` (canonical L2 write path, blast radius 80)
- **v1.4 sources**: SRC-ADR-003.
- **v1.4 edge**: INT-F10.03-F09.01-01 (L4 durable state uses UWG as sole writer).
- **Known write-sovereignty bypasses** (per `mv_write_sovereignty_paths`): **1,821 total, 56 critical**:
  - L_TOOLS: 25 critical (expected — tools write artefacts outside UWG)
  - L_UNKNOWN: 24 critical (investigate — unclassified modules writing to infra)
  - L4: **7 critical** (concerning — L4 modules writing directly: `gptcache_client.py mkdir`, `retrieval_layers.py persist_dir.mkdir`, `chunk_manifest_registry.py parent.mkdir`, etc.)
  - L_INFRA: 4 critical
  - L2: 1 critical (`RedisSovereignAgent.py`)
  - L_SHARED: 1 critical
- **ADG edge class**: `expected` for UWG-routed writes; `violation` for critical bypasses.

### Stage 10 — L4 durable state persist

- **Authority**: F10.01–F10.04. 141 modules under `agentic_core/L4_state/`.
- **Sub-surfaces**: `L4_state/cache/`, `L4_state/memory/`, `L4_state/enforcement/`, `L4_state/reasoning/`.
- **Downstream from UWG**: only durable-state writes that pass exit gate reach L4 (per F09.05).
- **ADG edge class**: `expected`.

### Stage 11 — L6 observe + record + memory write-back

- **Authority**: F12.01–F12.08. 89 modules under `agentic_core/L6_observability/`.
- **Memory lifecycle atoms**: F12.05/.07/.08 (SRC-INT-004). F12.06 EXCLUDED (per OOS-001 in v1.4 exclusions).
- **Writes**: observation writes go through L4 or straight to `system_learning/` (CROSS_CUTTING, out-of-scope for G1; G4 owns). F12.05 routes memory back for next-run F02.01 (L1) consumption.
- **Observed violations**: L6 → L0 (23) — L6_observability/__init__.py imports L0_routing/config/path_constants repeatedly. Flagged as `L6_downstream_mutation` breach — B7-G2-03.
- **ADG edge class**: mostly `expected`; L6 → L0 is `violation`.

## Spine reconstruction

`mv_runtime_spine_gaps` reports 100% of L0–L6, L_APP, L_SHARED modules as "gap" (not connected to runtime spine) — but this metric uses a narrow spine definition. The observed `mv_critical_path_segments.both_on_spine=1` line is only the L5→L0 admission pair. G2 interprets this as:

- The ADG-defined "runtime spine" is narrowly the admission gate (L5→L0).
- The full operational spine visible in the code is the 12-stage walk above.
- G3 pipelines should adopt the 12-stage walk as the spine pipeline and expand per-stage sub-pipelines.

## Canonical request walk summary

- **Modules named**: ~30 named modules cited, every one present in G1 `component_inventory.yaml`.
- **v1.4 atoms referenced**: F01, F02.01, F03.01/02, F04.01–04, F05.01/04, F06.01, F07.01–04, F08.01–05, F09.01–05, F10.01–04, F11.01, F12.01–08. Coverage: 15 of 60 ACTIVE atoms directly named in the walk; remaining 45 are covered transitively via layer authority.
- **v1.4 edges referenced**: INT-F02.01-F01.05-01, INT-F05.04-F06.01-01, INT-F07.03-F02.01-01, INT-F07.03-F05.01-01, INT-F08.04-F09.01-01, INT-F09.05-F08.04-01, INT-F10.03-F09.01-01. Coverage: 7 of 26 NORMATIVE edges directly named.
- **Unnamed atoms/edges** are not missing — they are covered by layer-authority atoms (F02.01 covers all L1 sub-claims, etc.). G7 traceability matrix produces the full atom-to-module mapping.
