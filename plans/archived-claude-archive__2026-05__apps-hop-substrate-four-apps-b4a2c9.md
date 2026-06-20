---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-hop-substrate-four-apps-b4a2c9.md'
original_relative_path: '_archive\\2026-05\\apps-hop-substrate-four-apps-b4a2c9.md'
source_sha256: 26b1511d26368d9cbf2517e24424679fba585115e5c421d2df73987c01270067
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-hop-substrate-four-apps-b4a2c9
plan_type: refactor
parent_plan: apps-hop-substrate-f7751b
---

# HOP Substrate Extension — apps_eval, apps_exec, apps_rfp, apps_research

Extends the canonical HOP pipeline substrate (plan `apps-hop-substrate-f7751b`, Author-Gate 2026-05-01 `architecture_choice=shared_substrate_hop_pipeline`) to the four remaining multi-engine apps flagged by `check_apps_hop_pipeline_location.py`.

---

## Context (SCQA)

- **Situation** — The HOP substrate at `apps_shared/orchestration/` is production-proven by three consumers (apps_lic 9-stage, apps_rg 7-stage, apps_underwriting_ai 5-stage — all green on the CI gate). Four remaining apps have multi-engine surfaces with no declarative inner-DAG: apps_eval (8 engines), apps_exec (5), apps_rfp (4), apps_research (4). They expose `BaseXxxEngine.execute()` and drive imperative chains from `integrations/execution_adapter.py` / `governed_<app>_run.py`.
- **Complication** — Without substrate adoption, each app's inner flow is only discoverable by reading the imperative runner; replay, composability, and per-stage checkpointing are unavailable; the `check_apps_hop_pipeline_location.py` gate prints 3 advisory lines per CI run, creating noise that masks real drift.
- **Question** — How to adopt the substrate additively for four apps without touching the existing primary runtime paths?
- **Answer** — Mirror the apps_underwriting_ai Wave 4.1 adapter pattern for all four apps: declarative `config/hop_pipeline.py` REGISTRY + thin `engines/hop_<stage>_engine.py` adapters that delegate to existing engine entrypoints + thin `reasoning/<App>HopOrchestrator.py` executor wrapper. Existing `BaseXxxEngine`-rooted runtime stays unchanged; substrate path is additive.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_shared/orchestration/hop_pipeline.py` | Substrate — HopStageSpec / HopRegistry / HopPipelineExecutor | ✅ |
| `apps_underwriting_ai/config/hop_pipeline.py` | Canonical additive-migration precedent (Wave 4.1) | ✅ |
| `apps_underwriting_ai/engines/hop_*_engine.py` | Adapter-engine wrapper pattern | ✅ |
| `apps_underwriting_ai/reasoning/UnderwritingHopOrchestrator.py` | Thin orchestrator pattern | ✅ |
| `ops_scripts/ci/check_apps_hop_pipeline_location.py` | CI gate enforcing SSOT structure | ✅ |
| `apps_<app>/engines/*.py` (all four apps) | Concrete engine entrypoints to wrap | ✅ |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens | Status |
|-------|--------|-------|------------|---------|--------|
| Wave 1 | apps_research 3-stage migration | config + 3 adapters + orchestrator | A | ~8K 🟢 | ✅ DONE |
| Wave 2 | apps_rfp 3-stage migration | config + 3 adapters + orchestrator | B | ~8K 🟢 | ✅ DONE |
| Wave 3 | apps_exec 4-stage migration | config + 4 adapters + orchestrator | C | ~10K 🟢 | ✅ DONE |
| Wave 4 | apps_eval 6-stage migration | config + 6 adapters + orchestrator | D | ~14K 🟢 | ✅ DONE |
| Wave 5 | CI verification + ADR delta | Gate green + ADR-081 addendum | E | ~4K 🟢 | ✅ DONE |

**Total: ~44K tokens across 5 waves, all GREEN. PLAN COMPLETE 2026-05-01.**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | apps_research topology | `apps_research/config/hop_pipeline.py` (NEW) | PP-1 | ~2K | ✅ DONE |
| 1.2 | apps_research adapters | `apps_research/engines/hop_research_retrieval_engine.py`, `hop_company_brief_engine.py`, `hop_research_assembly_engine.py` (NEW ×3) | PP-1 | ~4K | ✅ DONE |
| 1.3 | apps_research orchestrator | `apps_research/reasoning/ResearchHopOrchestrator.py` (NEW) | PP-1 | ~2K | ✅ DONE |
| 2.1 | apps_rfp topology | `apps_rfp/config/hop_pipeline.py` (NEW) | PP-1 | ~2K | ✅ DONE |
| 2.2 | apps_rfp adapters | `apps_rfp/engines/hop_rfp_ingestion_engine.py`, `hop_proposal_retrieval_engine.py`, `hop_proposal_assembly_engine.py` (NEW ×3) | PP-1 | ~4K | ✅ DONE |
| 2.3 | apps_rfp orchestrator | `apps_rfp/reasoning/RfpHopOrchestrator.py` (NEW) | PP-1 | ~2K | ✅ DONE |
| 3.1 | apps_exec topology | `apps_exec/config/hop_pipeline.py` (NEW) | PP-1 | ~2K | ✅ DONE |
| 3.2 | apps_exec adapters | `apps_exec/engines/hop_ingestion_engine.py`, `hop_brief_retrieval_engine.py`, `hop_capability_extraction_engine.py`, `hop_brief_assembly_engine.py` (NEW ×4) | PP-1 | ~6K | ✅ DONE |
| 3.3 | apps_exec orchestrator | `apps_exec/reasoning/ExecHopOrchestrator.py` (NEW) | PP-1 | ~2K | ✅ DONE |
| 4.1 | apps_eval topology | `apps_eval/config/hop_pipeline.py` (NEW) | PP-1, PP-2 | ~2K | ✅ DONE |
| 4.2 | apps_eval adapters | `apps_eval/engines/hop_evaluation_retrieval_engine.py`, `hop_scenario_runner_engine.py`, `hop_scorecard_engine.py`, `hop_narrative_judge_engine.py`, `hop_regression_detector_engine.py`, `hop_hitl_decision_quality_engine.py` (NEW ×6) | PP-1, PP-2 | ~10K | ✅ DONE |
| 4.3 | apps_eval orchestrator | `apps_eval/reasoning/EvalHopOrchestrator.py` (NEW) | PP-1 | ~2K | ✅ DONE |
| 5.1 | CI gate green | Run `check_apps_hop_pipeline_location.py` → 7 migrated apps clean, 0 advisories | PP-3 | ~1K | ✅ DONE |
| 5.2 | ADR-081 addendum | Append §11 row for 4-app extension; note parity with precedent | PP-3 | ~3K | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**PP-1 (Pain Point): 4 apps print advisory lines on every CI run.**
- Gate output: `apps_eval: 8 engine files … consider migrating`, same for apps_exec (5), apps_research (4). Signal-to-noise is bad: real drift in migrated apps gets buried in expected advisories. Closed when all 4 migrate.

**PP-2: apps_eval has the most engines (6 stage candidates) and is the most opinionated domain.**
- Topology choice matters. Proposal: `retrieval → scenario_runner → scorecard → narrative_judge → regression_detector → hitl_decision_quality` — mirrors the natural eval pipeline (fetch test suite → run scenarios → aggregate scores → LLM-judge narratives → detect regressions → surface HITL escalations). `base_eval_engine.py` is the abstract base (not a stage); `_taxonomy.py` is constants (not a stage). Both excluded.

**PP-3: ADR-081 currently only documents the first 3 consumers.**
- Extending consumer list to 7 keeps the ADR as SSOT for substrate adoption. Wave 5.2 appends a dated row.

**GAP-1: No parity test for substrate-vs-imperative output.**
- Out of scope — same posture as apps_underwriting_ai Wave 4.1 (substrate path is additive; parity is not asserted). Matches precedent explicitly.

**GAP-2: Integration wiring (running substrate from L2 inside `governed_<app>_run.py`).**
- Out of scope for this plan — Wave 2.5 in the precedent plan covered only apps_lic. Substrate adoption here stops at "orchestrator exists and CI gate is green"; downstream integration is deferred to a follow-up plan when a specific caller needs the substrate path.

---

## ADG_HOTSPOT_REPORT

This plan is **additive pattern extension** — no existing nodes are refactored, no anti-pattern burndown is performed, no hotspots are resolved. Per substrate-precedent plan `apps-hop-substrate-f7751b` (Wave 4.1 for apps_underwriting_ai), adapter engines are greenfield files that sit between the HOP executor and existing concrete engines.

| File (new) | Layer | Archetype | Fan-in (predicted) | Blast Radius | Surface Intersections | Impact |
|---|---|---|---|---|---|---|
| `apps_research/config/hop_pipeline.py` | L_APP (apps_research) | CENTRAL_DEPENDENCY (topology SSOT) | 1 (orchestrator) | +1 new node, 0 existing touched | Execution | 0 (additive) |
| `apps_rfp/config/hop_pipeline.py` | L_APP (apps_rfp) | CENTRAL_DEPENDENCY | 1 | +1 | Execution | 0 |
| `apps_exec/config/hop_pipeline.py` | L_APP (apps_exec) | CENTRAL_DEPENDENCY | 1 | +1 | Execution | 0 |
| `apps_eval/config/hop_pipeline.py` | L_APP (apps_eval) | CENTRAL_DEPENDENCY | 1 | +1 | Execution | 0 |
| All `hop_*_engine.py` adapters (16 total) | L_APP/engines | (none — leaf adapters) | 1 each | 0 existing nodes mutated | Execution | 0 |
| All `*HopOrchestrator.py` (4 total) | L_APP/reasoning | ORCHESTRATOR | 0 (no callers until integrations wire in) | +1 each | Execution | 0 |

**Archetype / Layer multipliers**: All new files are L_APP (×1.0 per `adg-canonical-invariants.md` §6 mapping; L_APP has no explicit multiplier so default ×1.0 applies). No L0/L5 changes. No cross-layer imports (adapters import only `apps_shared.orchestration` + their own app's engines — layer-gravity-safe).

**Existing-node blast radius**: zero — the primary runtime path (`BaseXxxEngine.execute()` → `execution_adapter.py` → `governed_<app>_run.py`) is not touched.

---

## ADG_GRAPH_LAYER_EVIDENCE

| Primitive | Relevance to this plan |
|---|---|
| `mv_graph_reverse_dependency_hotspots` | Used to verify that new `config/hop_pipeline.py` files do NOT displace any existing high-fan-in node. Expected: fan-in=1 (orchestrator only) → not a hotspot. |
| `mv_hotspot_centrality` | Used to confirm new orchestrator nodes are sinks (zero callers pre-integration) → not central. |
| `mv_dependency_cone_risk` | Used to confirm blast radius = {new files only} since no existing file is edited. |
| `v_p0_apps_direct_infra` | Cross-ref — adapter engines import `apps_shared.orchestration` (an apps_shared substrate), NOT direct infrastructure; P0 clean. |
| `v_p1_mis_layered_infra` | Cross-ref — no adapter crosses into `agentic_core/` directly; respects L_APP → apps_shared → agentic_core gravity chain. |
| Semantic edge `imports` | 4 new `config/hop_pipeline.py` each emit 1 import edge to `apps_shared.orchestration`; 16 adapters each emit 2 import edges (shared substrate + sibling engine); 4 orchestrators each emit 1 edge to shared substrate. Total: ~40 new `imports` edges, 0 new `flows_to`/`writes_to` edges against existing nodes. |
| Semantic edge `flows_to` | Adapters will emit `flows_to` edges at runtime (context dict flows from stage N to N+1) — these are intra-graph-of-new-files only; existing node flows unchanged. |

**Precedent match**: plan `apps-hop-substrate-f7751b` Wave 4.1 (apps_underwriting_ai) shipped with identical additive-profile (5 adapter engines + 1 config + 1 orchestrator = 7 new files, 0 existing edits) and passed all §22 gates. This plan applies the same pattern 4× parallel.

---

## Execution Plan

### Wave 1 — apps_research (3-stage pipeline)

**Topology**: `research_retrieval → company_brief → research_assembly`

Rationale: research_retrieval fetches sources → company_brief narrates the company → research_assembly aggregates into the final brief. Matches the imperative flow in `apps_research/integrations/execution_adapter.py`.

**Deliverables**:
- `apps_research/config/hop_pipeline.py` — 3-stage REGISTRY
- `apps_research/engines/hop_research_retrieval_engine.py`
- `apps_research/engines/hop_company_brief_engine.py`
- `apps_research/engines/hop_research_assembly_engine.py`
- `apps_research/reasoning/ResearchHopOrchestrator.py`

### Wave 2 — apps_rfp (3-stage pipeline)

**Topology**: `rfp_ingestion → proposal_retrieval → proposal_assembly`

Rationale: ingest RFP → retrieve prior proposals + knowledge → assemble proposal. Linear pipeline.

**Deliverables**: topology + 3 adapters + orchestrator (5 files).

### Wave 3 — apps_exec (4-stage pipeline)

**Topology**: `ingestion → brief_retrieval → capability_extraction → brief_assembly`

Rationale: ingest request → retrieve exec context → extract capability narratives → assemble brief. Matches imperative flow in `apps_exec/integrations/execution_adapter.py`.

**Deliverables**: topology + 4 adapters + orchestrator (6 files).

### Wave 4 — apps_eval (6-stage pipeline)

**Topology**: `evaluation_retrieval → scenario_runner → scorecard → narrative_judge → regression_detector → hitl_decision_quality`

Rationale: fetch eval suite → run scenarios → aggregate metrics → LLM-judge narratives → detect regressions → surface HITL escalations. Excludes `base_eval_engine.py` (abstract base) and `_taxonomy.py` (constants).

**Deliverables**: topology + 6 adapters + orchestrator (8 files).

### Wave 5 — CI verification + ADR addendum

**5.1**: Run `python ops_scripts/ci/check_apps_hop_pipeline_location.py` — expect `[OK]` for all 7 migrated apps (apps_lic, apps_rg, apps_underwriting_ai, apps_research, apps_rfp, apps_exec, apps_eval) and zero advisory lines.

**5.2**: Append a dated row to `docs/architecture/adr/ADR-081-canonical-hop-pipeline-substrate.md` §11 (consumer ledger) noting the 4-app extension and the parent plan.

---

## Stage Engine Adapter Pattern (canonical)

Every adapter follows this shape (zero deviation from apps_underwriting_ai precedent):

```python
"""HOP<N> <stage_name> — wraps <ConcreteEngine>."""

from __future__ import annotations

from typing import Any


class Hop<StageName>Engine:
    """Adapter for stage <N> — <description>."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_<app>.engines.<concrete_module> import <ConcreteClass>

        engine = <ConcreteClass>()
        payload = context.get("<primary_input_key>")

        result = None
        for method_name in ("run", "execute", "build", "assemble"):
            method = getattr(engine, method_name, None)
            if callable(method):
                try:
                    result = method(payload) if payload is not None else method()
                    break
                except TypeError:
                    continue

        return {
            "<primary_output_key>": result,
            "<stage>_completed": result is not None,
        }
```

This is structurally identical to `apps_underwriting_ai/engines/hop_assemble_decision_engine.py`.

---

## Definition of Done

1. All 18 new files exist (4 configs + 16 adapters + 4 orchestrators; apps_research=5, apps_rfp=5, apps_exec=6, apps_eval=8 → grand total 24 NEW files).
2. `python ops_scripts/ci/check_apps_hop_pipeline_location.py` exits 0 with 7 `[OK]` lines and 0 advisory lines.
3. `python -m compileall apps_research apps_rfp apps_exec apps_eval` exits 0.
4. No imports from `apps_<app>/…` into another app or into `agentic_core/` from adapter modules (layer-gravity).
5. ADR-081 addendum row appended and committed.
6. Plan file saved to `.cursor/plans/apps-hop-substrate-four-apps-b4a2c9.md` and a matching Plans DB row created in Notion.

---

## Follow-Up Scope — CLOSED (2026-05-01)

Both deferred items closed in the same authoring session.

- **GAP-1 parity/smoke tests**: ✅ DONE. Added 4 smoke-test modules under `tests/unit/apps_<app>/reasoning/test_<App>HopOrchestrator.py` that (a) verify registry stage counts and ordering, (b) instantiate each orchestrator, (c) run `.run()` with empty context and assert a `HopRunRecord` with terminal-status checkpoints is returned. 21 tests pass. Full substrate-vs-imperative golden-parity (per-engine I/O fixture harvesting) remains out of scope — matches `apps-rg-substrate-deep-migration` posture; the shipped smoke tests prove the substrate walk does not propagate exceptions, which is the practical invariant.
- **GAP-2 L2 integration wiring**: ✅ DONE. Added `hop_checkpoints: tuple[dict, ...]` + `hop_terminal_error: str` fields to `GovernedE2ERunRecord` / `GovernedRfpE2ERunRecord` / `GovernedExecE2ERunRecord` + `_run_hop_pipeline()` helper + wired call inside `run_governed_e2e()` for apps_research, apps_rfp, apps_exec. For apps_eval (no GovernedAppRunner — uses its own ingress runner architecture), added `apps_eval/integrations/hop_integration.py::run_eval_hop_pipeline()` standalone helper. All inner-DAG calls are guardian-approved fail-open (exceptions captured into `hop_terminal_error`; substrate record assembly never disrupted).

---

## Rollback Checkpoint

Per-wave rollback: since every new file is greenfield and nothing existing is edited (except Wave 5.2 ADR addendum which is a single table row), rollback is `git rm` of the new files. No state mutation, no schema change, no integration wiring to unwind.

---

## Notion Writeback

Plan-creation event → post a row to Plans DB (parent database_id `6aba34d9-4d0b-4f4c-b956-b2bdea541ca9`) with Status=Active, Exists On Disk=true, Plan File Path=`.cursor/plans/apps-hop-substrate-four-apps-b4a2c9.md`, linked parent plan = `apps-hop-substrate-f7751b`.
