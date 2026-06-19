# ADG Cleanup Queue and P2 Ratchet Trace

- **Generated:** 2026-06-19T16:01:12+00:00
- **Status:** degraded
- **Dead-code source:** `artifacts/adg/dead_code_zone_control_report_latest.json`
- **Published sqlite:** `artifacts/adg/adg_indexed_06192026_1144.sqlite`
- **P2 ratchet:** `missing`
- **Failed-run manifest:** `missing`

### BCG Cleanup Brief

- **North star:** Maintain SVP engineer-level repo standards: business-first decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Status:** NO_DELETIONS_APPROVED
- **Business read:** No deletions are approved in this run because ADG found 0 confirmed dead-code candidates; reduce uncertainty first, then deprecate noisy diagnostics.
- **Technical evidence:**
  - Dead code candidates: 0
  - Dead imports: 0
  - Unresolved imports: 588
  - First-party low-confidence ratio: 1.92%
  - Inferred-symbol ratio: 10.13%
  - Cleanup candidates surfaced: 0
- **Priority rule:** Confirmed dead code first, then unresolved imports, then low-confidence noise, then low-value diagnostics.
- **Column key:** Business reason = why the item matters to delivery or governance; Technical reason = the measured evidence; Why this order = why this item is ahead of the next row.

| Priority | Move | Scope | Business reason | Technical reason | Why this order | Decision |
|---------:|------|-------|----------------|-----------------|----------------|----------|
| 1 | Hold all deletion | whole codebase | The scan found no confirmed dead code, so deleting anything now would be speculative and could break working paths. | Dead-code candidates = 0 and dead imports = 0. | No proven target means the safest action is to pause deletion. | defer |
| 2 | Triage unresolved imports | ADG::Module::tests/ops_scripts/ci/test_adg_accelerator_compliance_gate.py | Unresolved imports are the biggest uncertainty and can hide real cleanup opportunities. | 588 unresolved imports; lead hotspot ADG::Module::tests/ops_scripts/ci/test_adg_accelerator_compliance_gate.py (62). | We need a cleaner signal before we can trust deletion decisions. | investigate |
| 3 | Reduce low-confidence noise | first-party nodes | Cleaner evidence makes later reviews faster and lowers the risk of deleting the wrong thing. | First-party low-confidence ratio = 1.92% and inferred-symbol ratio = 10.13%. | Noise reduction improves the quality of the next scan and makes future deletions safer. | stabilize |
| 4 | Deprecate low-value ADG signals | materialized views and unused artifacts | Remove empty or low-value diagnostics to cut review overhead once the evidence layer is stable. | 0 MV candidates and 0 unused artifacts surfaced by the report. | This is cheap cleanup, but it should follow the evidence cleanup work above. | deprecate |

Why this order:
- Confirmed dead code is the highest-confidence waste and should be removed first.
- Unresolved imports are the biggest uncertainty and can hide real cleanup work.
- Low-confidence and inferred-symbol noise should be reduced before taking more aggressive action.
- Low-value diagnostics are cheap to deprecate once the evidence layer is cleaner.

Next step: Deprecate first, then delete after the evidence stays clean.

## Cleanup Queue

The dead-code report found no confirmed deletions, so this queue prioritizes signal cleanup and unresolved-import noise reduction.

### Live unresolved-import queue

| Priority | Surface | Scope | Count | Business reason | Technical reason | Decision |
|---:|---|---|---:|---|---|---|
| 1 | live | ADG::Module::tests/ops_scripts/ci/test_adg_accelerator_compliance_gate.py | 62 | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 62 unresolved import(s) on this surface. | investigate |
| 2 | live | ADG::Module::ops_scripts/dev_tools/L0_routing_scripts/_ssot_meta_learning.py | 20 | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 20 unresolved import(s) on this surface. | investigate |
| 3 | live | ADG::Module::tests/_apps_contract/test_w2_hop4a_judging.py | 19 | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 19 unresolved import(s) on this surface. | investigate |
| 4 | live | ADG::Module::ops_scripts/dev_tools/L0_routing_scripts/colors.py | 14 | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 14 unresolved import(s) on this surface. | investigate |
| 5 | live | ADG::Module::agentic_core/L2_execution/types/healer_registry_types.py | 12 | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 12 unresolved import(s) on this surface. | investigate |
| 6 | live | ADG::Module::tests/apps_research/test_w4_c0_package_driven_grounding.py | 11 | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 11 unresolved import(s) on this surface. | investigate |
| 7 | live | ADG::Module::tests/_apps_contract/test_w_final_deferred.py | 10 | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 10 unresolved import(s) on this surface. | investigate |

### Archived or obsolete surfaces

| Priority | Surface | Scope | Count | Business reason | Technical reason | Decision |
|---:|---|---|---:|---|---|---|
| 8 | archived | ADG::Module::tests/_archived_obsolete/ops_scripts/ci/test_graphdb_gates.py | 24 | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 24 unresolved import(s) on this surface. | defer |
| 9 | archived | ADG::Module::tests/_archived_obsolete/unit_min_deps/test_inspector_mro_contracts.py | 12 | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 12 unresolved import(s) on this surface. | defer |
| 10 | archived | ADG::Module::tests/_archived_obsolete/ops_scripts/ci/test_pre_commit_summary_reporter.py | 11 | This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy. | 11 unresolved import(s) on this surface. | defer |

## P2 Ratchet Trace

This section explains the current MEDIUM hygiene count, the ceiling in `p2_ratchet.json`, and why the latest run is still blocked.

### BCG P2 Ratchet Brief

- **North star:** Maintain SVP engineer-level repo standards: business-first decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Status:** OVER_CEILING
- **Business read:** The published snapshot is still 20 over the P2 ceiling, so the ratchet remains blocked.
- **Technical evidence:**
  - Published sqlite snapshot: artifacts/adg/adg_indexed_06192026_1144.sqlite
  - P2 ceiling: 0
  - Current MEDIUM hygiene count: 20
  - Delta vs ceiling: +20
  - Baseline snapshot: missing
  - Latest failed run: missing
- **Priority rule:** Fix the largest live runtime hygiene hotspots first, then remove star imports, then re-baseline only if the debt is intentional.
- **Column key:** Business reason = why the item matters to delivery or governance; Technical reason = the measured evidence; Why this order = why this item is ahead of the next row.

| Priority | Move | Scope | Business reason | Technical reason | Why this order | Decision |
|---------:|------|-------|----------------|-----------------|----------------|----------|
| 1 | Reduce MEDIUM hygiene debt | apps_rg/runtime/c0/fact_vector_write_back.py | This is a live surface where removing hygiene debt improves trust in the next run. | 5 MEDIUM hygiene record(s) in the published snapshot. | Highest-count paths should be reduced first to move the ceiling fastest. | reduce |
| 2 | Reduce MEDIUM hygiene debt | apps_rg/runtime/bindings/u0_package_ingest.py | This is a live surface where removing hygiene debt improves trust in the next run. | 4 MEDIUM hygiene record(s) in the published snapshot. | Highest-count paths should be reduced first to move the ceiling fastest. | reduce |
| 3 | Reduce MEDIUM hygiene debt | apps_rg/runtime/section_graph_skills_proof_pool.py | This is a live surface where removing hygiene debt improves trust in the next run. | 2 MEDIUM hygiene record(s) in the published snapshot. | Highest-count paths should be reduced first to move the ceiling fastest. | reduce |
| 4 | Reduce MEDIUM hygiene debt | agentic_core/L6_learning/__init__.py | This is a live surface where removing hygiene debt improves trust in the next run. | 1 MEDIUM hygiene record(s) in the published snapshot. | Highest-count paths should be reduced first to move the ceiling fastest. | reduce |
| 5 | Remove star imports | agentic_core/L6_learning/__init__.py; apps_rg/runtime/sections/executive_summary_qwen_regen_dispatch.py | Star imports hide dependencies and make deprecation decisions harder to defend. | 2 MEDIUM hygiene record(s) are explicit star imports. | Easy wins should follow the largest live runtime hotspots. | deprecate |
| 6 | Re-run ADG and keep the ceiling honest | p2_ratchet.json | Do not change the ceiling until the underlying hygiene debt is actually reduced or explicitly accepted. | Current count=20; ceiling=0; delta=20. | Re-baselining before cleanup only hides the blocker. | rebaseline_if_intentional |

Why this order:
- The highest-count live runtime surfaces move the ceiling fastest.
- Star imports are low-ambiguity cleanup once the larger exception paths are underway.
- Re-baselining too early hides the blocker instead of paying it down.

Next step: Burn down the top runtime hotspots, then rerun ADG and confirm the count stays under the ceiling.

### Trace Summary

- **Current MEDIUM hygiene count:** 20
- **Ceiling:** 0
- **Delta:** +20
- **Baseline snapshot:** missing
- **Published snapshot:** artifacts/adg/adg_indexed_06192026_1144.sqlite

### Evidence Buckets

| Evidence | Count | Interpretation |
|---|---:|---|
| Exception | 9 | Broad exception catch or swallow on a live hygiene path. |
| OSError | 5 | Filesystem / IO error handling needs to be narrowed. |
| FileNotFoundError | 2 | Hygiene debt on the current published snapshot. |
| from agentic_core.L6_system_learning.future_run_promotion import * | 1 | Star import hides dependencies and makes review harder. |
| ImportError | 1 | Import fallback logic should be explicit and local. |
| ValueError | 1 | Parsing or validation guard should be tightened. |
| from apps_rg.runtime.sections.executive_summary_regen_dispatch import * | 1 | Star import hides dependencies and makes review harder. |

### File Hotspots

| Priority | Surface | Scope | Count | Business reason | Technical reason | Decision |
|---:|---|---|---:|---|---|---|
| 1 | live runtime | apps_rg/runtime/c0/fact_vector_write_back.py | 5 | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 5 MEDIUM hygiene record(s) in the published snapshot. | reduce |
| 2 | live runtime | apps_rg/runtime/bindings/u0_package_ingest.py | 4 | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 4 MEDIUM hygiene record(s) in the published snapshot. | reduce |
| 3 | live runtime | apps_rg/runtime/section_graph_skills_proof_pool.py | 2 | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 2 MEDIUM hygiene record(s) in the published snapshot. | reduce |
| 4 | core | agentic_core/L6_learning/__init__.py | 1 | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 1 MEDIUM hygiene record(s) in the published snapshot. | reduce |
| 5 | apps | apps_research/prompt_assembly/consumer_briefs.py | 1 | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 1 MEDIUM hygiene record(s) in the published snapshot. | reduce |
| 6 | live runtime | apps_rg/runtime/c0/c02_semantic_cache_payload.py | 1 | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 1 MEDIUM hygiene record(s) in the published snapshot. | reduce |
| 7 | live runtime | apps_rg/runtime/orchestration/patch_run.py | 1 | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 1 MEDIUM hygiene record(s) in the published snapshot. | reduce |
| 8 | live runtime | apps_rg/runtime/orchestration/r3r4_whole_run_orchestration.py | 1 | This path concentrates MEDIUM hygiene debt on a visible runtime or core surface. | 1 MEDIUM hygiene record(s) in the published snapshot. | reduce |

### What This Means

- There are no confirmed dead-code deletions in the latest dead-code report, so deletion stays deferred.
- The published snapshot still carries MEDIUM hygiene debt against the P2 ceiling, so the ratchet remains open.
- Reduce the live runtime hotspots first, then rerun ADG and confirm the ceiling stays honest.
