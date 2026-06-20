---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\gap-closure-test-impl-b77a11.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\gap-closure-test-impl-b77a11.md'
source_sha256: 3327a9a222877e7331c4c1728b2eed11f0e78659c7147a0fd65d1b14e042e241
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Gap-Closure Test Contract Implementation Plan

Status: Todo
Created: 2026-04-26
Related commit: a5df78f815 (April 2026 MECE gap closure pack)

## Purpose

Implement the 78 normative test contracts declared by the April 2026 gap-closure
pack in `docs/reference/`. Every test name listed in a `TEST REQUIREMENTS`
block of a gap-closure file must have a matching implementation under `tests/`
with a deterministic pass.

Without these tests, the requirements pack is doctrinal but unverifiable at
runtime — the architecture is asserted, not proven.

## Coverage gap (baseline)

| File | Tests declared | Tests on disk | Gap % |
|---|---:|---:|---:|
| `00A.8_L5_Runtime_Certification_Binding.md` | 6 | 0 | 100% |
| `00B.9_L4_Blueprint_Policy_Version_Migration.md` | 5 | 0 | 100% |
| `00C.9_RG_Layer_Integration_Invocation_Map.md` | 8 | 0 | 100% |
| `PA.8_Authority_RedTeam_Slot_Verification.md` | 6 | 0 | 100% |
| `03.9_L3_L2_Step_Handoff_Checkpoint_Resume.md` | 6 | 0 | 100% |
| `04.0_L2_Sequencer_Orchestrator_Contract_detailed.md` | 10 | 0 | 100% |
| `04.7_L2_Programmatic_Tool_Calling_PTC_Sandbox_detailed.md` | 7 | 0 | 100% |
| `04.9_L2_StateDiffCandidate_and_Mutation_Intent_detailed.md` | 8 | 0 | 100% |
| `04.10_L2_Verify_Then_Execute_Local_Critique_detailed.md` | 6 | 0 | 100% |
| `06.9_L6_Memory_Promotion_Interface.md` | 5 | 0 | 100% |
| `99.9_E2E_Mutation_Testing_Boundary_Faults.md` | 5 | 0 | 100% |
| `99.10_E2E_Fixtures_Replay_Harness_Commands.md` | 6 | 0 | 100% |
| **Total** | **78** | **0** | **100%** |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W1 | W1.1–W1.4 | Runtime certification + version migration (L5/L4) | 22000 | Existing L5/L4 modules accept evidence-ref injection | Todo | 11 tests passing in `tests/unit/agentic_core/L5_safety/` and `L4_state/` |
| W2 | W2.1–W2.2 | Runtime gate integration map + PA red-team (00C/PA) | 16000 | G01-G29 gate IDs already constants | Todo | 14 tests passing in `tests/unit/agentic_core/L5_safety/gates/` and `L1_cognition/prompt_assembly/` |
| W3 | W3.1–W3.4 | L2 sequencer + state-diff + verify-critique + L3-L2 handoff | 36000 | L2 sequencer module exists or can be stubbed | Todo | 30 tests passing in `tests/unit/agentic_core/L2_execution/` and `L3_orchestration/` |
| W4 | W4.1–W4.2 | PTC v2 sandbox hardening tests | 12000 | PTC sandbox exists; need property tests for offline/FS/seed | Todo | 7 tests passing in `tests/unit/agentic_core/L2_execution/ptc/` |
| W5 | W5.1 | L6 memory promotion interface | 8000 | UWG admission gateway exists | Todo | 5 tests passing in `tests/unit/agentic_core/L6_observability/memory_promotion/` |
| W6 | W6.1–W6.2 | E2E mutation/boundary + fixture replay harness | 18000 | Fixture loader infra exists or be stubbed minimally | Todo | 11 tests passing in `tests/e2e/` |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W1.1 | L5 binding + snapshot tests | `tests/unit/.../test_l5_runtime_certification_binding.py` | Need `L5RuntimeCertificationBinding` dataclass first | 6000 | Todo |
| W1.2 | L5 reclearance + UWG reject | same as W1.1 | Wire to existing UWG module | 4000 | Todo |
| W1.3 | Policy/blueprint version + alias swap | `tests/unit/.../test_l4_version_migration.py` | Need migration plan schema | 6000 | Todo |
| W1.4 | Deprecation window + replay mismatch | same as W1.3 | Time-bound test fixture | 6000 | Todo |
| W2.1 | G01-G29 invocation map coverage | `tests/unit/.../test_runtime_gate_invocation_map.py` | Inventory gate call sites first | 8000 | Todo |
| W2.2 | PA authority red-team | `tests/unit/.../test_pa_authority_redteam.py` | Need injection fixture corpus | 8000 | Todo |
| W3.1 | L2 sequencer ordering + ceilings | `tests/unit/.../test_l2_sequencer_contract.py` | Stub if E1-E5 modules absent | 10000 | Todo |
| W3.2 | proposed_state_diff inert | `tests/unit/.../test_l2_state_diff_candidate.py` | Wire to Exit/UWG mocks | 8000 | Todo |
| W3.3 | Verify-then-execute critique | `tests/unit/.../test_l2_local_critique.py` | Same-authority sandbox check | 6000 | Todo |
| W3.4 | L3 step handoff + checkpoint/resume | `tests/unit/.../test_l3_l2_step_handoff.py` | Workflow DAG fixture | 6000 | Todo |
| W4.1 | PTC offline/FS/quarantine | `tests/unit/.../test_ptc_v2_sandbox.py` | Need PTC sandbox harness | 6000 | Todo |
| W4.2 | PTC seed + import gate + cleanup | same as W4.1 | Deterministic seed fixture | 6000 | Todo |
| W5.1 | L6 memory promotion gauntlet | `tests/unit/.../test_l6_memory_promotion.py` | Mock gauntlet + UWG | 8000 | Todo |
| W6.1 | E2E mutation/boundary faults | `tests/e2e/test_boundary_faults.py` | Need 14 fault scenarios | 9000 | Todo |
| W6.2 | E2E fixtures + replay harness | `tests/e2e/test_replay_harness.py` | F1-F10 fixture corpus | 9000 | Todo |

## Gap Register

- Many target modules (L5RuntimeCertificationBinding, etc.) likely do not yet
  exist as Python classes; this plan implements TESTS first per the
  doctrine, surfacing missing modules as `pytest.fail("module not yet implemented: <X>")`.
- Each wave should regenerate ADG after module scaffolding so
  fan-in/fan-out signals stabilize.
- Constitutional §1 forbids `pytest.mark.skip` — for unimplemented modules,
  use `pytest.fail` with a clear message instead.

## ADG_HOTSPOT_REPORT

Constitutional §22 ranked hotspot report. Targets are the **modules under test**
(not the test files themselves). Layer multipliers per `adg-canonical-invariants.md`.

| Rank | Target Module / Surface | Layer | Mult | fan_in (est.) | Archetype | Surface | Impact | Wave |
|---:|---|:---:|:---:|---:|---|---|---:|:---:|
| 1 | Runtime Gate dispatch (G01-G29) | L5 | ×2.0 | 15 | SAFETY_GATEKEEPER | Security Surface | 1000+ | W2 |
| 2 | L5 Certification Binding emission | L5 | ×2.0 | 10 | SAFETY_GATEKEEPER | Security Surface | 800 | W1 |
| 3 | L4 policy/blueprint version aliases | L4 | ×1.75 | 12 | STATE_NODE | State Surface | 700 | W1 |
| 4 | L2 Sequencer (E1→E5) | L2 | ×1.0 | 15 | ORCHESTRATOR | Execution Surface | 500 | W3 |
| 5 | L3 → L2 Step Handoff contract | L3 | ×1.75 | 5 | ORCHESTRATOR | Execution Surface | 300 | W3 |
| 6 | L2 StateDiffCandidate emission | L2 | ×1.0 | 10 | CENTRAL_DEPENDENCY | Write Surface | 280 | W3 |
| 7 | PTC v2 sandbox executor | L2 | ×1.0 | 8 | CENTRAL_DEPENDENCY | Execution Surface | 250 | W4 |
| 8 | L6 Memory Promotion candidate gate | L6 | ×0.75 | 5 | STATE_NODE | State Surface | 160 | W5 |
| 9 | E2E boundary-fault matrix | (cross) | ×1.0 | 8 | CENTRAL_DEPENDENCY | Observability Surface | 161 | W6 |
| 10 | E2E replay harness | (cross) | ×1.0 | 8 | CENTRAL_DEPENDENCY | Observability Surface | 161 | W6 |

## ADG_GRAPH_LAYER_EVIDENCE

Per constitutional §22, this plan cites the ADG graph-layer primitives that
shape its wave ordering. The plan implements the test layer for a
requirements pack; the analysis below verifies that test scope correctly
intersects high-impact graph regions.

**Materialized views consulted:**
- `mv_hotspot_centrality` — selects top-impact modules where new tests
  must apply first; drives Wave 1/2 ordering (L5 + L4 modules dominate by
  centrality and layer multiplier).
- `mv_dependency_cone_risk` — verifies boundary-fault scenarios in 99.9
  cover the dependency cone of UWG and Exit, the canonical state-mutation
  chokepoints. Used to validate Wave 6 scope completeness.
- `mv_chokepoint_bridges` — confirms `00C.9_RG_Layer_Integration_Invocation_Map`
  tests cover the RG dispatch chokepoint between layers (G27 in particular,
  which guards direct-write attempts).
- `mv_path_criticality_rollup` — used to rank E2E fixture families F1-F10
  by criticality (F10 failure-path > F3 simple grounded > F1/F2 cache).

**Semantic edges relied on:**
- `flows_to` — traces RouteContract → C0 → PA → L2 → Exit handoff; each
  handoff has a paired test contract in this plan.
- `writes_to` — flags every test that asserts `write_auth=NONE` inside
  L2 (04.9, 04.10). UWG remains the only `writes_to` egress target.
- `emits_side_effect` — validates PTC sandbox tests (04.7) cover all
  side-effect kinds: filesystem, network, subprocess, stdout/stderr.

**P-views cross-referenced:**
- `v_p0_write_bypass_uwg` — Wave 6.1 boundary-fault tests must include any
  current rows here as fault scenarios; baseline must equal zero post-fix.
- `v_p1_mis_layered_infra` — verify no test fixture creates new mis-layered
  imports while scaffolding modules for tests under W1/W3.
- `v_p2_duplicated_adapters` — avoid scaffolding duplicate adapter helpers
  when implementing fixture loaders for W6.

**Provenance:**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_<latest>.sqlite

## Sequencing Note

Waves W1, W2 can proceed in parallel. W3 depends on W1.1 (state diff
references L5 binding). W4 is independent. W5 depends on W2 (gate IDs).
W6 depends on W1-W5 because E2E proof packets reference all earlier contracts.
