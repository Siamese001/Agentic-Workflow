---
plan_id: adg-testing-hotspots-wave-plan-a7f3c1
plan_format: v2
plan_type: tracker
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# ADG Testing-Hotspots — Prioritized Test-Gap Wave Plan

Burn down the highest-blast-radius testing gaps across `agentic_core` and the `apps_*`
surfaces, ordered by ADG fan-in × layer-criticality, starting with the contract/spine
surface every app depends on.

> **plan_id**: `adg-testing-hotspots-wave-plan-a7f3c1` — wave markers use `plan=adg-testing-hotspots-wave-plan-a7f3c1`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-06-14

PLAN_CREATED: plan=adg-testing-hotspots-wave-plan-a7f3c1 slug=adg-testing-hotspots-wave-plan-a7f3c1 status="Not Started"

---

## Context (SCQA)

- **Situation** — The ADG testing-hotspots report (`docs/reports/test_hotspot_gaps_05252026.md`,
  snapshot `adg_indexed_05242026_2005.sqlite`) shows `agentic_core` at **1370/2372 modules (57%)**
  basename test coverage. The per-app ADG hotspot views (`docs/reports/adg/apps_*_hotspots_*.md`,
  snapshot `adg_indexed_05252026_0849.sqlite`) plus a basename scan show the `apps_*` surface at
  **225/1352 modules (16.6%)** — far worse.
- **Complication** — Coverage gaps are not uniform: **52 core P1 modules (fan-in ≥10)** and
  **100 core P2 modules (fan-in 5–9)** are untested *central dependencies* — a single break
  poisons every downstream consumer. On the app side, the highest-fan-out orchestrators
  (`apps_eval/engines/scenario_runner.py` fan-out 118, `apps_research/reasoning/ResearchOrchestrator.py`
  89, `apps_lic/runtime/bindings/exit_binding.py` fan-in 48) are **untested**, and `apps_eval`
  sits at **0%**. Flat "add tests everywhere" wastes budget on fan-in≤1 leaves (607 of them).
- **Question** — How do we sequence the testing-gap burn-down so the highest-blast surfaces
  (by ADG fan-in × layer-criticality multiplier) are covered first, across both core and apps?
- **Answer** — Six prioritized waves: core contract/spine surface → core safety+routing
  chokepoints (×2.0 layer multiplier) → core orchestration+state (×1.75) → apps canary surface
  (`apps_lic`/`apps_rg`) → apps cross-app/reference orchestrators → P2 backlog + a coverage
  ratchet gate that locks the gains.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Core P1 runtime-contract + Exit/X3 spine (fan-in ≥20) | ~140K | Contracts are pure data/pydantic — fast deterministic tests; ADG snapshot fresh | 🔲 TODO | All 13 W1 target modules have `test_<leaf>.py`; pytest green; P1 contract band ↓ |
| W2 | W2.1, W2.2 | Core P1 safety + routing chokepoints (L0/L5 ×2.0) | ~120K | L0/L5 modules carry the 2.0 criticality multiplier; intake/guardrail surfaces stable | 🔲 TODO | 11 L0/L5 P1 targets covered; no guardrail/intake regressions |
| W3 | W3.1, W3.2 | Core P1 orchestration + state (L3/L4 ×1.75) | ~130K | exit_eval + L4_state/UWG contracts are the durable-write + grading surface | 🔲 TODO | 13 L3/L4 P1 targets covered; UWG/exit_eval contract tests pass |
| W4 | W4.1, W4.2 | Apps canary: `apps_lic` + `apps_rg` high-blast gaps | ~150K | `apps_lic`=HIGH canary; `apps_rg`=largest app (440 gaps); linkage from MV/P-views | 🔲 TODO | Top-15 per app high-fan-in/out untested modules covered; app coverage ↑ |
| W5 | W5.1, W5.2 | Apps cross-app/reference orchestrators (`apps_eval`/`apps_research`/`apps_underwriting_ai`) | ~120K | These orchestrators are high-fan-out + 0–21% covered | 🔲 TODO | Named orchestrators/engines covered; `apps_eval` off 0% |
| W6 | W6.1, W6.2 | Core P2 backlog burn-down + coverage ratchet gate | ~110K | P1 cleared by W1–W3; gate prevents regression | 🔲 TODO | P2 band reduced ≥40%; ratchet CI gate live + green |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | runtime.contracts top surface (apps_rg_ingress, final_evidence, l1_plan, records, compiled_prompt) | 🔲 TODO |
| W1.2 | Exit/X3 spine (x3_disposition, x1_checkout_result, integrated_single_action_spine_run, exit_disposition) | 🔲 TODO |
| W2.1 | L0_routing intake chokepoints (envelope, validated_request, reason_codes, stages, final_contract) | 🔲 TODO |
| W2.2 | L5_safety enforcement + identity (ingress, contracts.verify, guardrail_bank, principal_verifier) | 🔲 TODO |
| W3.1 | L3_orchestration exit_eval (app_grader_registry, x2_matrix, x3_dispositions, consistency, dimension) | 🔲 TODO |
| W3.2 | L4_state contracts + UWG (records, app_domain, digests, durable_write_gateway, touch_state_writer, otel.spans) | 🔲 TODO |
| W4.1 | `apps_lic` canary (exit_binding, l3_binding, GovernanceShieldAgent, ab_variant_engine, signals.types) | 🔲 TODO |
| W4.2 | `apps_rg` high-blast engines/bindings (top fan-in/out untested) | 🔲 TODO |
| W5.1 | `apps_eval` + `apps_research` orchestrators (scenario_runner, EvalOrchestrator, regression_detector, ResearchOrchestrator, research_assembly_engine) | 🔲 TODO |
| W5.2 | `apps_underwriting_ai` reconnect-surface (decision_packet_assembler, runtime.bindings, profile_builder) | 🔲 TODO |
| W6.1 | Core P2 high-fan-in burn-down (top 40 of 100) | 🔲 TODO |
| W6.2 | Coverage ratchet CI gate (P1=0 invariant + monotonic coverage) | 🔲 TODO |

---

## Out Of Scope

- Editing `agentic_core/**` or `apps_*/**` **source** logic. This plan adds **tests only**
  (under `tests/unit/<pkg>/` and `tests/<app>/` per the 3-surface taxonomy). Source bugs found
  while testing → `spawn_task` / Backlog Item, not in-plan edits.
- P4 (fan-in=1, 541 modules) and P5 (fan-in=0, 66 likely-dead modules) core gaps — deferred;
  P5 modules need a dead-code verdict before any test investment.
- Behavioral/coverage-% rubric beyond basename presence (handled by `hotspot_coverage_report.py`).
- Re-running / regenerating the ADG snapshot (consume the committed reports as SSOT).

---

## ADG_HOTSPOT_REPORT

Snapshot: `adg_indexed_05242026_2005.sqlite` (core gaps) + `adg_indexed_05252026_0849.sqlite` (apps views)
P0 open: N/A (test-gap plan, not violation burn-down) · P1 core test-gaps: 52 · P2: 100

Impact = `untested × (1 + log10(1 + fan_in)) × layer_multiplier`. Top hotspots (impact-ranked):

| rank | module | layer | fan_in | multiplier | archetype | surfaces |
|------|--------|-------|-------:|-----------:|-----------|----------|
| 1 | `runtime.contracts.apps_rg_ingress_payload` | runtime | 79 | ×1.0 | CENTRAL_DEPENDENCY | Execution |
| 2 | `runtime.contracts.final_evidence_contract` | runtime | 74 | ×1.0 | CENTRAL_DEPENDENCY | Observability |
| 3 | `L3_orchestration.exit_eval.v6.app_grader_registry` | L3 | 40 | ×1.75 | ORCHESTRATOR | Execution/Security |
| 4 | `runtime.contracts.l1_plan_contract` | runtime | 40 | ×1.0 | CENTRAL_DEPENDENCY | Execution |
| 5 | `L4_state.contracts.records` | L4 | 32 | ×1.75 | STATE_NODE | Write/State |
| 6 | `L4_state.uwg.durable_write_gateway` | L4 | 27 | ×1.75 | SAFETY_GATEKEEPER | Write |
| 7 | `L0_routing.intake.envelope` | L0 | 22 | ×2.0 | CENTRAL_DEPENDENCY | Execution |
| 8 | `L0_routing.intake.validated_request` | L0 | 20 | ×2.0 | CENTRAL_DEPENDENCY | Execution/Security |
| 9 | `L5_safety.enforcement.ingress` | L5 | 16 | ×2.0 | SAFETY_GATEKEEPER | Security |
| 10 | `L5_safety.identity.guardrail_bank` | L5 | 14 | ×2.0 | SAFETY_GATEKEEPER | Security |
| 11 (apps) | `apps_lic/runtime/bindings/exit_binding.py` | L_APP | 48 | canary HIGH | SAFETY_GATEKEEPER | Write/Security |
| 12 (apps) | `apps_eval/engines/scenario_runner.py` | L_APP | fan-out 118 | MEDIUM | ORCHESTRATOR | Execution |

> The ×2.0 layer multiplier is why W2 (L0/L5, fan-in 12–22) precedes W3 (L3/L4, fan-in up to 40):
> a swallowed routing/guardrail contract poisons every route and disables safety controls
> (`adg-canonical-invariants.md` §4).

## ADG_GRAPH_LAYER_EVIDENCE

### Materialized Views Consulted
- `mv_hotspot_centrality` — per-module centrality within each app (apps hotspot reports §`mv_hotspot_centrality`).
- `mv_debt_concentration_hotspots` — deterministic linkage source for `apps_lic` actionable hotspots
  (`exit_binding.py`, `l3_binding.py`, `ab_variant_engine.py` flagged `linkage_source=MV`).
- `mv_graph_reverse_dependency_hotspots` — fan-in ranking that produced the P1 band (≥10) in the core report.

### Semantic Edges Used
- `resolves_callsite` / fan-in (`edges.relation_type='imports'`, dst-joined): ranked the 52 P1 core
  modules and the apps Top-Fan-In tables — "who calls this contract?" → blast radius if untested.
- `flows_to` / fan-out: ranked apps orchestrators (`scenario_runner` 118, `ResearchOrchestrator` 89)
  — "what does this orchestrator reach?" → cascade surface a broken orchestrator hides.

### Pre-Built P-Views Cross-Referenced
- `v_p0_*` / `v_p1_*`: apps actionable-hotspot linkage cites `violations:*:hygiene:LOW` from the
  P-view join; no P0 write-bypass intersections in the test-gap set (test-only plan).

### Graph-Layer-Derived Priority
Targets are ranked by fan-in × layer-multiplier (above), NOT raw gap counts — which is why
607 fan-in≤1 leaves are explicitly out of scope despite being the bulk of the 1002 core gaps.

---

## Wave 1 — Core P1 Runtime-Contract + Exit/X3 Spine

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — adds test files only; no shared-surface source edits.

**Phases**:
- **W1.1** — runtime.contracts top surface | ~70K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Exit/X3 spine | ~70K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Targets (fan-in ≥20, the contract surface every app depends on):**
`apps_rg_ingress_payload`(79), `final_evidence_contract`(74), `l1_plan_contract`(40),
`records`(32), `compiled_prompt_artifact`(30), `durable_write_gateway`(27), `x3_disposition`(23),
`x1_checkout_result`(15), `integrated_single_action_spine_run`(15), `exit_disposition`(15),
`sealed_workflow_types`(16), `origin`(16), `posture`(20).

**Acceptance**:
- Every target has `tests/unit/agentic_core/.../test_<leaf>.py` (schema validity, required-field, round-trip).
- `pytest tests/unit/agentic_core/runtime -q` green; zero regressions vs baseline.

---

## Wave 2 — Core P1 Safety + Routing Chokepoints (×2.0)

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — L0_routing intake chokepoints | ~60K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — L5_safety enforcement + identity | ~60K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Targets (L0/L5, ×2.0 multiplier):** L0 `intake.envelope`(22), `intake.validated_request`(20),
`intake.reason_codes`(19), `intake.stages`(13), `c0_retrieval.final_contract`(14),
`c0_retrieval.candidate_pool`(13), `types.route_contract_v15`(11); L5 `enforcement.ingress`(16),
`contracts.verify`(15), `identity.guardrail_bank`(14), `identity.principal_verifier`(12).

**Acceptance**:
- All 11 targets covered; guardrail/principal/intake behavior pinned (accept + reject paths).
- `pytest tests/unit/agentic_core/L0_routing tests/unit/agentic_core/L5_safety -q` green.

---

## Wave 3 — Core P1 Orchestration + State (×1.75)

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — L3_orchestration exit_eval | ~65K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — L4_state contracts + UWG | ~65K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Targets (L3/L4, ×1.75):** L3 `exit_eval.v6.app_grader_registry`(40), `exit_eval.dimension`(21),
`exit_eval.v6.x2_matrix`(19), `exit_eval.consistency`(15), `exit_eval.v6.x3_dispositions`(15);
L4 `contracts.records`(32)†, `uwg.durable_write_gateway`(27)†, `contracts.app_domain`(15),
`contracts.digests`(11), `uwg.touch_state_writer`(10), `otel.spans`(13).
(† if not already landed in W1; dedupe on basename.)

**Acceptance**:
- exit_eval grading surface + UWG durable-write contracts covered (admit + reject).
- `pytest tests/unit/agentic_core/L3_orchestration tests/unit/agentic_core/L4_state -q` green.

---

## Wave 4 — Apps Canary: `apps_lic` + `apps_rg`

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — `apps_lic` canary surface | ~75K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** — `apps_rg` high-blast engines/bindings | ~75K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**`apps_lic` targets (HIGH canary; MV/P-view linkage):** `runtime/bindings/exit_binding.py`(fan-in 48),
`runtime/bindings/l3_binding.py`(39), `sequences/touch_sequence_definitions.py`(30),
`engines/ab_variant_engine.py`(30), `signals/types.py`(24),
`integrations/managed_workflow_dispatcher.py`(24), `cert/fec_producer.py`(22),
`reasoning/GovernanceShieldAgent.py`(fan-out 83), `engines/control_plane.py`(fan-out 80).

**`apps_rg` targets (largest app, 440 gaps / 17.6%):** select top-15 untested by fan-in/out from the
`apps_rg` graph view (regenerate `apps_rg` hotspot view first — it is absent from `docs/reports/adg/`;
fall back to `tools/analysis/test_hotspot_gaps_report.py`-style basename scan filtered to `apps_rg/`).

**Acceptance**:
- Top-15 high-blast untested modules per app covered under `tests/unit/apps_lic/` and `tests/unit/apps_rg/`.
- `apps_lic` coverage ↑ from 18.6%; `apps_rg` ↑ from 17.6% (report a delta).

---

## Wave 5 — Apps Cross-App / Reference Orchestrators

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** — `apps_eval` + `apps_research` orchestrators | ~65K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.2** — `apps_underwriting_ai` reconnect-surface | ~55K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Targets (high fan-out, 0–21% covered):** `apps_eval/engines/scenario_runner.py`(fan-out 118),
`apps_eval/reasoning/EvalOrchestrator.py`(90), `apps_eval/engines/regression_detector.py`(84),
`apps_eval/engines/scorecard_engine.py`(76), `apps_eval/validators/eval_gate_validator.py`(72);
`apps_research/reasoning/ResearchOrchestrator.py`(89), `apps_research/engines/research_assembly_engine.py`(77),
`apps_research/engines/company_brief_engine.py`(39);
`apps_underwriting_ai/engines/decision_packet_assembler.py`(23),
`apps_underwriting_ai/runtime/profile_builder.py`(15), `apps_underwriting_ai/runtime/bindings/c0_binding.py`(13).

**Acceptance**:
- `apps_eval` off **0%**; each named orchestrator/engine has a `test_<leaf>.py` exercising its public entrypoint.
- `pytest tests/unit/apps_eval tests/unit/apps_research tests/unit/apps_underwriting_ai -q` green.

---

## Wave 6 — Core P2 Backlog Burn-Down + Coverage Ratchet Gate

WAVE_ID: W6
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: F

**Authorization**: REQUIRED — W6.2 adds a CI gate (`touches_governance_ci` surface); confirm gate
mode (advisory vs fail-closed) via `AskUserQuestion` before landing.

**Phases**:
- **W6.1** — Core P2 high-fan-in burn-down (top 40 of 100) | ~60K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W6.2** — Coverage ratchet CI gate | ~50K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- P2 band reduced ≥40% (≥40 of 100 covered), prioritizing fan-in 7–9 first.
- Ratchet gate (`ops_scripts/ci/check_test_hotspot_coverage_ratchet.py`) asserts **P1 core test-gap
  count = 0** and **coverage is monotonic** (regenerates the report, compares to a committed baseline).

---

## Execution Details

### Per-phase loop (applies to W1–W5)
**Scope**: For each target module, author a `test_<leaf>.py` in the canonical surface
(`tests/unit/<pkg>/` mirroring package path; integration → `tests/<app>/`).

**Commands**:
```bash
# 1. Confirm the gap still exists (basename scan / report renderer)
python tools/analysis/test_hotspot_gaps_report.py            # regenerates core report
# 2. ADG-scoped test selection for the target (no full-suite during loop)
python tools/adg/adg_test_accelerator.py scope --changed <test_file> --format pytest
# 3. Run scoped tests only
python -m pytest tests/unit/<pkg>/test_<leaf>.py -q
```

### W6.2 — Coverage ratchet gate
**Scope**: New CI gate at `ops_scripts/ci/check_test_hotspot_coverage_ratchet.py` (canonical SSOT
folder per §31). Reads the report, fails if P1 core test-gap count > 0 or coverage < committed baseline.

```bash
python ops_scripts/ci/check_test_hotspot_coverage_ratchet.py
python ops_scripts/ci/run_contract_gates.py
```

---

## Gap Register

**GAP-1: `apps_rg` hotspot graph view is missing from `docs/reports/adg/`.**
- Other apps have `apps_<x>_hotspots_*.md`; `apps_rg` (the largest app, 440 gaps) does not.
- Impact: W4.2 must regenerate it (or fall back to basename scan filtered to `apps_rg/`) before ranking.

**GAP-2: Basename match overcounts coverage.**
- A `test_types.py` can match multiple `types.py` across layers (report W2 note). Treat W-level
  coverage deltas as directional; verify per-target that the test actually imports the target module.

**GAP-3: `apps_eval` at 0% but split across `apps_eval` (8 mods) and `apps_eval_legacy` (67 mods).**
- Confirm which is the live surface before investing; legacy may be deletion-bound, not test-bound.

---

## Definition of Done

DoD-1: Core P1 test-gap band (fan-in ≥10) reduced from 52 to 0 across W1–W3.
- Evidence: `python tools/analysis/test_hotspot_gaps_report.py` shows P1 band count = 0.
- Status: TODO

DoD-2: Report renderer smoke-run succeeds (executable surface this plan drives).
- Evidence: `python tools/analysis/test_hotspot_gaps_report.py` exits 0, writes `docs/reports/test_hotspot_gaps_<date>.md`.
- Status: TODO

DoD-3: Net-new tests pass with zero regressions.
- Evidence: `python -m pytest tests/unit/agentic_core tests/unit/apps_lic tests/unit/apps_rg tests/unit/apps_eval tests/unit/apps_research tests/unit/apps_underwriting_ai -q` → N pass, 0 fail.
- Status: TODO

DoD-4: Contract gates green; no new violations introduced by added tests.
- Evidence: `python ops_scripts/ci/run_contract_gates.py` exits 0.
- Status: TODO

DoD-5: Coverage ratchet gate live and green (P1=0 invariant + monotonic coverage).
- Evidence: `python ops_scripts/ci/check_test_hotspot_coverage_ratchet.py` exits 0; gate registered in `run_contract_gates.py`.
- Status: TODO

DoD-6: Apps coverage uplift recorded.
- Evidence: basename scan shows `apps_*` aggregate coverage ↑ from 16.6% baseline; `apps_eval` > 0%.
- Status: TODO

### Verification vs Deferral

| Item | Verified by | Deferred? |
|---|---|---|
| Core P1 band → 0 | report renderer | No |
| Apps canary top-15 covered | scoped pytest | No |
| P4/P5 core leaves (607+66) | — | Yes — out of scope |
| Behavioral coverage-% rubric | `hotspot_coverage_report.py` | Yes — future plan |

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=adg-testing-hotspots-wave-plan-a7f3c1 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=adg-testing-hotspots-wave-plan-a7f3c1 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=adg-testing-hotspots-wave-plan-a7f3c1 reason="<summary>" added="<waves/phases>" authorized="yes"
```

> Source bugs found while writing tests are **out of scope** — capture via `spawn_task` / Backlog Item,
> do not fix in-plan (this is a test-authoring plan, not a refactor plan).

---

## Supersedes

| Predecessor slug | Reason |
|---|---|

_None — net-new plan._

---

## Marker Quick Reference

```
WAVE_START: plan=adg-testing-hotspots-wave-plan-a7f3c1 wave=<N>
WAVE_COMPLETE: plan=adg-testing-hotspots-wave-plan-a7f3c1 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=adg-testing-hotspots-wave-plan-a7f3c1 phase=<W1.1>
PLAN_COMPLETE: plan=adg-testing-hotspots-wave-plan-a7f3c1 note="<final outcome>"
```

---

## Provenance

ADG Provenance: backend=sqlite, snapshot=adg_indexed_05242026_2005.sqlite (core gaps) +
adg_indexed_05252026_0849.sqlite (apps hotspot views). Sources:
[test_hotspot_gaps_05252026.md](docs/reports/test_hotspot_gaps_05252026.md),
[apps_lic_hotspots_20260525T132938Z.md](docs/reports/adg/apps_lic_hotspots_20260525T132938Z.md),
[apps_eval_hotspots_20260525T132938Z.md](docs/reports/adg/apps_eval_hotspots_20260525T132938Z.md),
[apps_research_hotspots_20260525T132938Z.md](docs/reports/adg/apps_research_hotspots_20260525T132938Z.md),
[apps_underwriting_ai_hotspots_20260525T132938Z.md](docs/reports/adg/apps_underwriting_ai_hotspots_20260525T132938Z.md).
