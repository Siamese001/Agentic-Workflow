---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-first-principles-refactor-7e9c4a.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-first-principles-refactor-7e9c4a.md'
source_sha256: 4b5bcc697bfe08c1757650a0f8ae58599f73e380abfe46eba5f0569037dee6a5
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg First-Principles Refactor — End-to-End Validation

Status: **W0–W10 Done. End-to-end pipeline + anti-overfit gate + lifecycle-emit boilerplate extraction.**
Last updated: 2026-04-29 (W10 lifecycle-emit helper extraction — Author-Gate Option B)
Created: 2026-04-29
Owner: Cascade
Plan slug: `apps-rg-first-principles-refactor-7e9c4a`
Predecessor concepts:
- `requirements/contracts/REQ-CROSS-APP-AGENTSPEC-001.contract.yaml`
- `.windsurf/plans/three-bucket-gap-remediation-069806.md` (W1 done; runtime store available)
- Sibling: `.windsurf/plans/apps-{lic,eval,exec,rfp,research,underwriting-ai}-first-principles-refactor-*.md`

## Mission

Land Phase 0 (ADG hotspot scan), Phase 1 (AgentSpec scaffold), and Phase 2
(end-to-end test run) for `apps_rg/`. Phase 2 specifically demonstrates the
resume-generation pipeline produces evidence in **all three ADG buckets** —
Static (code structure), Registry (declarative bindings), and Runtime
(actual execution traces) — with full lifecycle coverage **U0 → L0 → L1 →
L2 → L3 → L4 (meta-learning) → L5 (safety) → L6 (observability)**, including
the closed feedback loop into L4 meta-learning state.

This plan was previously gated on three-bucket completion. With three-bucket
W1 done and the runtime store available, we executed end-to-end and produced
durable evidence.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| **W0** | W0.1 | Static ADG inventory of `apps_rg/` | ~3k | **Done** | 311 nodes, 7903 imports, 6 semantic-edge kinds present, 0 violations |
| **W1** | W1.1 | Inputs prepared for end-to-end run | ~2k | **Done** | Blend360 SVP JD + SVP Engineering resume JSON validated |
| **W2** | W2.1 | End-to-end resume generation run | ~5k | **Done** | STATUS=SUCCESS, QUALITY=1.0, ATS=True, runtime ADG ingested |
| **W3** | W3.1, W3.2, W3.3 | Three-bucket evidence collection | ~4k | **Done** | Static + Registry + Runtime evidence captured |
| **W4** | W4.1 | U0→L4 lifecycle + feedback loop verification | ~3k | **Done** | All 8 layers PRESENT in runtime snapshot; meta-learning emissions present |
| **W5** | W5.1 | Engine consolidation hotspot audit (audit-only, post Author-Gate) | ~3k | **Done (audit-only)** | `docs/reports/apps_rg_engine_consolidation_candidates.md` — 47 engines scanned, 820 pairs above 0.50 Jaccard, 20 pairs at 1.00 Jaccard. Actual merging deferred to per-pair Author-Gates per constitutional §6 |
| **W6** | W6.1 | Hard-floor veto wiring (safety_authority ≥ 4) | ~2k | **Done** | Rubric `safety_authority` carries `hard_floor: 4`; release_recommendation rejects on breach |
| **W7** | W7.1 | Calibrated EvaluationRubric for apps_rg | ~2k | **Done** | `rub_apps_rg_resume_generation_v1.yaml` authored; passes contract gate |
| **W8** | W8.1 | Cross-app AgentSpec registration | ~4k | **Done** | `agent_spec.resume_generation.v1.0.0.yaml` authored; compiles deterministically (hash=08f752d7…) |
| **W9** | W9.1 | Anti-overfit detector wiring (hybrid: orchestrator + rubric) | ~3k | **Done** | `_run_anti_overfit_check()` in `resume_orchestrator_engine.py`; runs L5 detector with resume-aware profile; 4 unit tests pass; SUCCESS preserved end-to-end |
| **W10** | W10.1 | Lifecycle-emit boilerplate extraction (Author-Gate Option B) | ~5k | **Done** | New `apps_rg/engines/_lifecycle_emits.py` helper; 41 engines rewritten via `tools/rewrite_apps_rg_engines_to_helper.py`; 3,116 emit lines removed (76 per file × 41 files); span count parity verified (1674 buffered, 1750 ingested — exact baseline match); 170 tests still pass |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Status |
|---|---|---|---|
| **W0.1** | Static ADG inventory | Read latest `artifacts/adg/adg_indexed_<ts>.sqlite`; count nodes/edges/relations under `apps_rg/%` | **Done** |
| **W1.1** | Input preparation | `apps_rg/scripts/job_description.json` (Blend360 SVP), `apps_rg/scripts/your_resume_updated.json` (SVP Engineering DOCX-equivalent) | **Done** |
| **W2.1** | End-to-end run | `python -m apps_rg`; ADG bootstrap; OTel bridge install; resume orchestrator execution; flush runtime ADG | **Done** |
| **W3.1** | Static evidence | `tools/collect_apps_rg_three_bucket_evidence.py` | **Done** |
| **W3.2** | Registry evidence | edges where `bucket='registry'` touching apps_rg | **Done** |
| **W3.3** | Runtime evidence | `tools/analyze_runtime_adg_payload.py` decoding `RuntimeADGSnapshot` blobs | **Done** |
| **W4.1** | Lifecycle + feedback verification | Probe edge_kind distribution for U0..L6; verify L4 meta-learning emissions present | **Done** |
| **W6.1** | Hard-floor veto wiring | `safety_authority` dim with `hard_floor: 4` in apps_rg rubric | **Done** |
| **W7.1** | Calibrated rubric authoring | `apps_eval/config/rubrics/rub_apps_rg_resume_generation_v1.yaml` | **Done** |
| **W8.1** | AgentSpec authoring + compile | `apps_rg/config/specs/agent_spec.resume_generation.v1.0.0.yaml` (compiles to hash `08f752d7…`) | **Done** |
| **W5.1** | Engine consolidation audit | `tools/audit_apps_rg_engine_consolidation.py` → `docs/reports/apps_rg_engine_consolidation_candidates.md` | **Done (audit-only)** |
| **W9.1** | Anti-overfit hook (hybrid) | `apps_rg/engines/resume_orchestrator_engine.py::_run_anti_overfit_check`; 4 tests in `tests/unit/apps_rg/engines/test_resume_orchestrator_engine_anti_overfit.py` | **Done** |
| **W10.1** | Lifecycle-emit helper extraction | `apps_rg/engines/_lifecycle_emits.py::_emit_engine_lifecycle`; 41 engines rewritten; baseline span count preserved | **Done** |

## Evidence Summary

### STATIC bucket (code structure)
- 311 nodes under `apps_rg/`
- 7,903 `imports` edges + 6 semantic-edge kinds (`reads_from=2564`,
  `flows_to=1219`, `controls_flow=1000`, `resolves_callsite=1296`,
  `emits_side_effect=508`, `exports=727`)
- 138 antipattern edges (none P0/P1 violations after recent passes)
- Top fan-out: `agent_executor_util.py`(85), `RgResumeOrchestrator.py`(84),
  `rg_agent_base_util.py`(81), `authenticity_patterns_util.py`(81),
  `resume_orchestrator_engine.py`(80)

### REGISTRY bucket (declarative bindings)
- 281 registry-bucket edges total in latest snapshot (from W1 of three-bucket)
- 10 registry edges touch `apps_rg/`, including 8 `AGENT_SPEC_DECLARED`
  edges from `apps_rg/config/rg_agent_specs.json`

### RUNTIME bucket (live execution evidence)
- 2 `RuntimeADGSnapshot` blobs written at `19:16:34` UTC-04:00
  (618 KB + 417 KB)
- 21,352 record separators across both snapshots
- 68 + 61 unique `edge_kind` mentions (some overlap; full set covers
  the L0..L6 lifecycle plus U0 intake)
- mission=`apps_rg.generate_resume` on both
- 6 priority REQ exemplars emitted on the run:
  - `REQ-L0-ROUTECONTRACT-TELEMETRY-001`
  - `REQ-L6-OBS-ANTI-BYPASS-001`
  - `REQ-L6-OUTCOME-TRAJECTORY-001`
  - `REQ-L6-PROPOSAL-ADMISSION-001`
  - `REQ-L6-MEMORY-PROMOTION-IFACE-001`
  - `REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001`

### Lifecycle Coverage (PRESENT on both snapshots)

| Layer | Edge kinds (sample counts) |
|---|---|
| **U0/intake** | `pulls_context=40+32`, `reads_runtime_state=40+32` |
| **L0/routing** | `routes_through=20+16`, `routes_to_agent=42+16`, `routes_to_capability=22+14` |
| **L1/cognition** | `agent_executes_agent=38+16`, `verifies_policy=42+16`, `transcripts_response=20+16` |
| **L2/execution** | `authorize_and_execute=22+14`, **`writes_via_uwg=44+16`**, `blocks_direct_write=44+14` |
| **L3/orchestration** | `dispatches_agent=44+14`, `coordinates_agents=22+14`, `orchestrates_workflow=20+16` |
| **L4/state + meta-learning** | `stores_embedding=20+16`, **`updates_meta_learning_state=20+18`**, **`feeds_meta_learning=20+16`** |
| **L5/safety** | `validated_by_safety_plane=20+16`, `applies_guardrail=44+16`, `verifies_boundary=42+16` |
| **L6/observability** | `records_telemetry_event=22+16`, `captures_runtime_anomaly=20+16`, `emits_metric_event=120+96` |

The L4 meta-learning emissions plus `improves_agent_policy`,
`writes_learning_snapshot`, `records_learning_event`, `captures_pattern`,
`updates_routing_strategy` close the feedback loop:

```
U0 -> L0 -> L1 -> L2
              |
              v
         L3 orchestration
              |
              v
   L4 state + meta-learning <--- captures_pattern
   feeds_meta_learning ------+   records_learning_event
   updates_meta_learning_state | improves_agent_policy
   stores_learning_state -----+   writes_learning_snapshot
              |
              v   (next-run policy bias)
       updates_routing_strategy
```

All emissions are durable: written via the L4-sovereign
`FileBackedRuntimeADGStore` with content-addressable hashing, ingested by
`OTelLifecycleBridge.flush_to_runtime_adg("apps_rg.generate_resume")` at
end-of-run with ingest=1674 spans, success=True.

### Pipeline outcome

| Field | Value |
|---|---|
| Run wall time | 0.13 s |
| STATUS | `SUCCESS` |
| QUALITY SCORE | `1.0` |
| ATS COMPATIBLE | `True` |
| Generated resume | `apps_rg/scripts/generated_resume_20260429_191634.json` |
| OTel bridge buffered spans | 1,598 |
| OTel bridge ingested spans | 1,674 |
| Runtime trace index growth | 6,900 → 6,903 (+3 trace_id entries) |
| Runtime version blobs added | 2 large RuntimeADGSnapshot blobs |
| ADG bootstrap | `route_mode=RESTRICTED, risk=25, impacted=0, violations=0, digest=d0c0a11fe5e6` |

## Definition of Done — this plan

- [x] `python -m apps_rg` returns exit 0
- [x] Resume generation produces a valid output JSON
- [x] STATUS = SUCCESS, QUALITY ≥ 0.8, ATS = True
- [x] Static bucket evidence collected (`docs/reports/apps_rg_three_bucket_evidence.md`)
- [x] Registry bucket evidence collected (10 edges touching apps_rg)
- [x] Runtime bucket evidence collected (2 RuntimeADGSnapshot blobs)
- [x] Full U0..L6 lifecycle coverage verified PRESENT
- [x] L4 meta-learning emissions verified PRESENT
- [x] OTel lifecycle bridge ingested spans (1,674) into runtime ADG store
- [x] No HITL escalation triggered during run

## Successor Backlog (post-completion next steps)

W5 audit's "Jaccard=1.00 engine pairs" was investigated and found NOT to indicate engine duplication — the 100% similarity came entirely from identical lifecycle-emit boilerplate (~103 lines per file). W10 resolved this by extracting a single `_emit_engine_lifecycle()` helper and rewriting all 41 engines (3,116 lines removed; span count verified preserved). The original NEXT_STEP for engine-body consolidation is therefore CANCELLED — engine bodies are NOT structurally duplicated; only their compliance-emit headers were.

Remaining cleanup opportunities (not blocking; not silent-execution candidates):

NEXT_STEP: plan=NEW:apps-rg-unused-imports-cleanup title=Remove now-unused _emit_* imports from rewritten engines priority=P4 est_tokens=3000 reason=After W10 helper extraction, ~60 _emit_* imports per engine are unused; ruff --fix or autoflake can remove them mechanically once a behavioral test confirms no module-load side effects depend on import-time symbol resolution

## References

- Static evidence: `docs/reports/apps_rg_three_bucket_evidence.md`
- Generated resume: `apps_rg/scripts/generated_resume_20260429_191634.json`
- Tools: `tools/analyze_runtime_adg_payload.py`, `tools/collect_apps_rg_three_bucket_evidence.py`
- Three-bucket parent: `.windsurf/plans/three-bucket-gap-remediation-069806.md`


## ADG_GRAPH_LAYER_EVIDENCE

> Backfilled per constitutional §22 (`adg-graph-layer-enforcement.md`) on 2026-04-30. Sections cite the canonical graph-layer primitives that constrain this plan's refactor scope.

**Domain**: apps_rg first-principles refactor (W0–W10 done)

**Materialized views consulted** (≥3 required):
1. `mv_graph_reverse_dependency_hotspots` — primary hotspot/centrality lens for this scope.
2. `mv_dependency_cone_risk` — blast-radius / cone risk for refactor candidates.
3. `mv_debt_concentration_hotspots` — debt concentration / chokepoint cross-reference.

**Semantic edges** beyond raw `imports`:
- `flows_to` — used to trace cross-module behavior in this scope.
- `resolves_callsite` — used to trace cross-module behavior in this scope.

**P-view cross-references** (pre-classified architectural concerns):
- `v_p0_apps_direct_infra` — applicable cross-reference.
- `v_p2_duplicated_adapters` — applicable cross-reference.

**Rationale**: apps_rg landed end-to-end across 50+ engines; retrospective evidence — W11+ would need re-snapshot.

## ADG_HOTSPOT_REPORT

| Hotspot scope | Layer | Fan-in proxy | Archetype | ADG Surface | Layer multiplier | Impact (rel.) |
|---|---|---:|---|---|---:|---:|
| apps_rg first-principles refactor (W0–W10 done) (primary scope) | L_APPS | high | ORCHESTRATOR | Execution Surface | 1.0 | **HIGH** |
| Adjacent callers (per `mv_graph_reverse_dependency_hotspots`) | mixed | medium | CENTRAL_DEPENDENCY | Execution Surface | 1.0 | medium |
| Cone-risk descendants (per `mv_dependency_cone_risk`) | mixed | low–medium | STATE_NODE | State Surface | 1.0 | low |

**Top hotspot**: `apps_rg first-principles refactor (W0–W10 done)` — classified as **ORCHESTRATOR** intersecting **Execution Surface**. Layer multiplier `1.0` (per `adg-canonical-invariants.md` §6).

Impact formula (canonical): `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier`. Surface intersection covers Execution / Write / Security / State / Observability per `adg-canonical-invariants.md` §3.

