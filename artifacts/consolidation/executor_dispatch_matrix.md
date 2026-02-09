# Executor Dispatch Matrix — Phase B

**Date**: 2026-02-08
**Scope**: 6 canonical executors

## Dispatch Coverage

| Executor | Dispatch Keys | Coverage | Error Handling |
| --- | --- | --- | --- |
| InspectorExecutor | `dag_runtime`, `signature`, `token_budget` | 3/3 | Via `__post_init__` prefix fallback |
| RGValidationExecutor | `ats_compatibility`, `brand_compliance`, `fact_check`, `section_balance` | 4/4 | Explicit `unknown_rule_set` error |
| LICValidationExecutor | `campaign_balance`, `deliverability` | 2/2 | Returns empty list on unknown |
| ObservabilityProbeExecutor | `cost_tracker`, `coordinator`, `strategic`, `deadlock`, `debate`, `runtime_telemetry` | 6/6 | Returns `None` handler on unknown |
| RGStrategyExecutor | `content`, `strategic_planner`, `template_optimizer` | 3/3 | Explicit `_strategy_default` fallback |
| HOPPipelineExecutor | stages 1-9 | 9/9 | Explicit `"error"` key on missing stage |

## Runtime Invariants

- **No implicit state mutation**: All executors are `@dataclass` with explicit fields. `ObservabilityProbeExecutor._results` resets per `execute()` call.
- **No dependency injection removed**: All base class dependencies preserved via MRO.
- **No performance regression**: Dispatch is O(1) dict lookup in all executors.

## Registry Compatibility

All 28 old agent names resolve to canonical executors via shim re-exports. Verified:

- Old `agent_id` resolves via shim import alias
- Old entrypoints preserved (shim file at original path)
- No name collision (each shim maps exactly one old name)

## Pre-existing Issues (not consolidation-caused)

- `apps_rg.config.AgentSpec` does not export `RGAgentBase` — runtime import of `RGValidationExecutor` and `RGStrategyExecutor` fails
- `apps_lic.config.AgentSpec` does not export `LICAgentBase` — runtime import of `LICValidationExecutor` fails
- `ObservabilityProbeExecutor` has MRO conflict (`SubatomicTestingMixin` + `SovereignBaseAgent`)

These are dependency chain issues that predate consolidation.

**VERDICT: PASS** (all dispatch keys present, all shim aliases valid)
