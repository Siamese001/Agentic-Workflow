# Config Surface Disposition Report

- **Generated:** 2026-06-17T16:13:16Z
- **ADG snapshot:** `artifacts/adg/adg_indexed_06152026_1043.sqlite`
- **Scope:** config folders only; tests, artifacts, and archived trees are treated as non-runtime unless proven otherwise.

## Decision

- **Keep**: live SSOT and runtime config surfaces.
- **Keep but clean**: compatibility shims that still have callers.
- **Archive / delete**: historical trees, generated outputs, and zero-fan-in legacy leaves that only exist as compatibility baggage.

## What Is Really Needed Where

| Surface | Disposition | Why |
|---|---|---|
| `config/` | Keep | Global config SSOT. Not runtime-only, but it is authoritative for repo-wide settings and YAML-backed inputs. |
| `agentic_core/config/` | Mixed | Contains live loaders and registries, but also several legacy helpers and salvage-only modules. |
| `agentic_core/L0_routing/config/` | Keep | Load-bearing routing config; this is one of the hottest config packages in the repo. |
| `agentic_core/L5_safety/config/structure_blueprint/` | Keep | Active structure SSOT package. |
| `apps_shared/config/` | Mixed | Shared config and compatibility helpers live here; some files are core, some are migration scaffolding. |
| `apps_exec/config/` | Archive / compat | App-contract surface with no clear active top-level runtime owner. |
| `apps_*/config/` | Keep | App-owned config for active app packages. |
| `tests/**/config` | Test-only | Fixture and import-shape coverage, not runtime SSOT. |
| `tests/_archived_obsolete/**/config` | Archive | Obsolete test-only trees. |
| `artifacts/**/config` | Generated | Derived outputs, not source of truth. |

## Live Surfaces To Keep

These are the config files that ADG and code search show as real runtime or SSOT dependencies:

- `agentic_core/L0_routing/config/path_constants.py`
- `agentic_core/L0_routing/config/__init__.py`
- `agentic_core/L0_routing/config/model_registry.py`
- `agentic_core/L0_routing/config/routing_thresholds.py`
- `agentic_core/config/model_catalog.py`
- `agentic_core/config/google_ai_env.py`
- `agentic_core/config/constants_config.py`
- `agentic_core/config/sovereign_config.py`
- `agentic_core/config/registry_config.py`
- `agentic_core/config/injection_layer_config.py`
- `agentic_core/config/hygiene_registry_config.py`
- `agentic_core/config/env_loader.py`
- `agentic_core/L5_safety/config/structure_blueprint/ssot.py`
- `agentic_core/L5_safety/config/structure_blueprint/_constants.py`
- `agentic_core/L5_safety/config/structure_enforcement_util.py`
- `agentic_core/runtime/config/routing_thresholds.py`
- `agentic_core/runtime/config/shared_infrastructure_config.py`
- `agentic_core/runtime/config/signal_quality_config.py`
- `apps_shared/config/pipeline_constants_config.py`
- `apps_shared/config/prompt_reception_spec.py`
- `apps_shared/config/operational_config.py`
- `apps_shared/config/app_guardian_registry.py`
- app-owned config under `apps_lic/config/`, `apps_qna/config/`, `apps_research/config/`, `apps_underwriting_ai/config/`, `apps_architect/config/`, and active `apps_rg/config/`

## Legacy Or Compatibility Surfaces

These files or directories are not primary runtime SSOT. They should stay only while callers or migration windows remain open:

- `agentic_core/L5_safety/config/structure_blueprint_config.py`
- `agentic_core/L5_safety/config/structure_blueprint/territories_loader.py`
- `apps_shared/config/legacy_yaml_deprecation.py`
- `apps_shared/config/environment_config.py`
- `agentic_core/config/token_budget_loader.py`
- `agentic_core/config/mcp_loader.py`
- `agentic_core/config/legacy_artifacts_config.py`
- `agentic_core/config/colors_config.py`
- `agentic_core/config/complexity_metrics_config.py`
- `agentic_core/config/config_loader.py`
- `agentic_core/config/domain_constitution_config.py`
- `agentic_core/config/gateway_config.py`
- `agentic_core/config/global_settings_config.py`
- `agentic_core/config/non_conforming_agent_finder_config.py`
- `agentic_core/config/rag_config.py`
- `agentic_core/config/reflection_config.py`
- `apps_exec/config/agent_spec_config.py`
- `agentic_core/L0_routing/_archive/v12/config/`

## High-Confidence Cleanup Queue

These are the best first-wave cleanup candidates because they are legacy, zero-fan-in, archive-only, or otherwise non-authoritative:

1. `agentic_core/L5_safety/config/structure_blueprint/territories_loader.py`
   - Zero runtime fan-in.
   - Explicitly described as a deprecated replacement helper.

2. `agentic_core/config/token_budget_loader.py`
   - Only archived-test references were found in the repo scan.
   - Candidate for relocation to a tooling-only surface or removal after caller proof.

3. `agentic_core/config/mcp_loader.py`
   - No runtime callers surfaced in the scan.
   - Root `.mcp.json` is the real SSOT; this loader is tooling support, not core runtime config.

4. `agentic_core/config/legacy_artifacts_config.py`
   - Salvage/archive registry, not a live config source.
   - Reads like historical artifact recovery, not current runtime behavior.

5. `apps_shared/config/legacy_yaml_deprecation.py`
   - Keep only while legacy YAML loaders still need migration warnings.
   - After the last caller migrates, retire it.

6. `apps_exec/config/`
   - Archived contract surface, not a live top-level execution package.
   - Keep only until all consumers are moved to the canonical app surfaces.

7. `agentic_core/L0_routing/_archive/v12/config/`
   - Pure archive.

8. `tests/_archived_obsolete/**/config` and `artifacts/**/config`
   - Test-only or generated; do not treat as source SSOT.

## Important Exceptions

- `agentic_core/config/model_catalog.py` stays. The ADG snapshot did not index it cleanly, but code search shows broad runtime use.
- `agentic_core/L5_safety/config/structure_blueprint_config.py` is still consumed by many callers. It is legacy, but not deletable yet.
- `apps_shared/config/environment_config.py` is compatibility-heavy and still has test coverage, so it is not a deletion candidate until caller ownership is verified.

## Recommended Next Wave

1. Freeze the live SSOT files listed above.
2. Confirm callers for the cleanup queue.
3. Delete or archive only the zero-fan-in legacy leaves first.
4. Rerun ADG to verify fan-in moved to the live surfaces.
5. Only then remove the remaining compatibility shims.

## Physical Cleanup Executed

- Deleted `agentic_core/config/token_budget_loader.py`
- Deleted `agentic_core/config/mcp_loader.py`
- Deleted `agentic_core/config/legacy_artifacts_config.py`
- Deleted `agentic_core/L5_safety/config/structure_blueprint/territories_loader.py`

These were the highest-confidence zero-fan-in legacy leaves. Remaining compatibility surfaces stay in place until their callers are proven gone.

## Verification

- Fresh ADG snapshot from the detached clean worktree: `C:\Git\Agentic-Workflow-FRESH-adgverify\artifacts\adg\adg_indexed_06172026_1244.sqlite`
- The four deleted files are `MISSING` in that snapshot.
- Live replacement surfaces remain present in the snapshot, including `agentic_core/L0_routing/config/path_constants.py`, `agentic_core/L5_safety/config/structure_blueprint/ssot.py`, and `agentic_core/config/model_catalog.py`.
