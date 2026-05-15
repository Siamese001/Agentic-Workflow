---
slug: hop-engines-triage-a7e4b2
parent: apps-research-blend-baseline-c74787
type: investigation_memo
status: Completed
date: 2026-05-03
---

# `hop_*` Engines Triage — Investigation Memo (Plan §P1.5)

## Verdict

**ALIVE — dynamically loaded.** Do NOT delete.

## Evidence

`apps_research/config/hop_pipeline.py` defines a 3-stage `HopStageSpec`
pipeline that references the three `hop_*` engines by module string:

```python
HopStageSpec(stage_id=1, engine_module="apps_research.engines.hop_research_retrieval_engine",
             engine_class="HopResearchRetrievalEngine", ...)
HopStageSpec(stage_id=2, engine_module="apps_research.engines.hop_company_brief_engine",
             engine_class="HopCompanyBriefEngine", ...)
HopStageSpec(stage_id=3, engine_module="apps_research.engines.hop_research_assembly_engine",
             engine_class="HopResearchAssemblyEngine", ...)
```

The engines are loaded via `importlib.import_module(spec.engine_module)`
at pipeline execution time, which is invisible to static module-level
import-graph analysis. This explains the `fan_in(imports)=0` reading in
the ADG snapshot `adg_indexed_05022026_2217.sqlite` (GAP-R5) — the ADG
cannot cross the dynamic-import boundary.

## Why the ADG Fan-in Inventory Missed This

The ADG `imports` edge type records only static `import X` / `from X import Y`
statements. Dynamic imports via `importlib.import_module()` with a string
argument are correctly classified as `dynamic_exec` / unresolved edges
and do not count toward `fan_in(imports)`.

**Implication for GAP-R5 finding**: "fan_in=0 for all 6 engines" is
accurate as-stated but does NOT mean the engines are unreachable. Three
of them (`hop_*`) are reachable via the hop-pipeline spec dispatcher.
The other three (`company_brief_engine`, `research_assembly_engine`,
`research_retrieval_engine`) are reachable via `__main__.py` →
`run_research.py` which late-imports them inside function bodies
(documented in GAP-R7).

## Actionable Output

- ✅ No file deletions.
- ✅ No follow-on plan required — the `hop_*` engines are intentional
  dynamically-dispatched pipeline stages.
- ℹ️ Future ADG enhancement: treat `dynamic_exec` edges from recognized
  dispatcher patterns (`HopStageSpec`, `apps_shared.spine_emission`,
  `route_registry.yaml`) as synthetic `imports` edges for fan-in
  accuracy. Out of scope for this plan.

## Parent Plan Impact

`apps-research-blend-baseline-c74787` W1 P1.5 marked ✅ DONE with
verdict=ALIVE. No code produced. No deletions. Blend-baseline W1
advances to commit stage.
