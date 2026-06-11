---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\centrality_recompute_post_hardening.md'
original_relative_path: 'centrality_recompute_post_hardening.md'
source_sha256: 54b6fdab99df26fc442d14b9f3c5840ea375b5b14b9a1463c9cae769973b8247
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Centrality Recompute — Post-Hardening

**Date**: 2026-02-09
**Scope**: All Python files under `agentic_core/`, `apps_lic/`, `apps_rg/`, `apps_shared/`
**Metric**: In-degree centrality (count of modules importing a given module)
**Gate**: `ops_scripts/ci/centrality_gate.py`

## Top 10 Gravity Nodes

| Rank | Module | Importers | Ceiling | Status |
| ---- | ------ | --------- | ------- | ------ |
| 1 | `agentic_core.base_agents.SovereignBaseAgent` | 164 | 200 | OK |
| 2 | `agentic_core.L5_safety.config.structure_blueprint_config` | 140 | 200 | OK |
| 3 | `agentic_core.base_agents.decorators` | 94 | 120 | OK |
| 4 | `agentic_core.base_agents.timeout_decorator` | 65 | 80 | OK |
| 5 | `agentic_core.mixins.subatomic_testing_mixin` | 41 | 60 | OK |
| 6 | `agentic_core.mixins.atomic_execution_mixin` | 28 | 40 | OK |
| 7 | `agentic_core.L5_safety.reasoning.HierarchyAgent` | 10 | 20 | OK |
| 8 | `agentic_core.L5_safety.enforcement.archival_gatekeeper` | 10 | 20 | OK |
| 9 | `apps_rg.utils.RGAgentBase` | 9 | 20 | OK |
| 10 | `apps_lic.engines.HOPPipelineExecutor` | 9 | 15 | OK |

## Executor Centrality

| Executor | Importers | Ceiling | Status |
| -------- | --------- | ------- | ------ |
| `InspectorExecutor` | 3 | 10 | OK |
| `ObservabilityProbeExecutor` | 6 | 10 | OK |
| `HOPPipelineExecutor` | 9 | 12 | OK |
| `LICValidationExecutor` | 2 | 10 | OK |
| `RGStrategyExecutor` | 4 | 10 | OK |
| `RGValidationExecutor` | 4 | 10 | OK |

## Allowlist

The following modules are allowlisted above the general ceiling of 15:

- `SovereignBaseAgent` (200) — universal base class
- `structure_blueprint_config` (200) — SSOT configuration
- `decorators` (120) — shared decorator module
- `timeout_decorator` (80) — shared timeout utility
- `subatomic_testing_mixin` (60) — universal testing mixin
- `atomic_execution_mixin` (40) — execution mixin
- All other infrastructure modules at ceiling 20

## Verdict

All modules within ceilings. No new gravity nodes from consolidation hardening.

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

