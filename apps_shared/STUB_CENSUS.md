# apps_shared Stub Census

**Generated:** 2026-05-02
**Source:** `python tools/analysis/audit_apps_shared_stubs.py`  
**Input:** `artifacts/analysis/apps_shared_stub_census.json`  
**Plan:** [`apps-shared-stub-audit-7dfe16`](../.codex/plans/apps-shared-stub-audit-7dfe16.md)

## Summary

- **Scanned files:** 207
- **Total stubs:** 64
- **Legitimate:** 64 (100.0%)
- **Real gaps:** 0

## Category counts

| Category | Count | Meaning |
|---|---:|---|
| `ABC` | 45 | explicit `abc.ABC` subclass or `@abstractmethod` method |
| `NullObject` | 7 | module-level function with descriptive docstring + no-op body — graceful-fallback pattern |
| `ImplicitABC` | 6 | class name suggests abstract (Base/Abstract/Client/Checker/Processor/Provider/Adapter) AND has `NotImplementedError` method — duck-typed abstract |
| `TemplateMethodHook` | 4 | private hook method (`_*`) on Base/Abstract/Executor/Invoker class — subclasses override |
| `ContextManagerStub` | 1 | dunder context-manager method (`__enter__`/`__aexit__`/etc.) with no-op body |
| `Protocol` | 1 | `typing.Protocol` subclass — interface declaration, no body |

## Stub-kind counts

| Kind | Count | AST shape |
|---|---:|---|
| `Pass` | 38 | `pass` after optional docstring |
| `Ellipsis` | 13 | `...` after optional docstring |
| `NotImpl` | 6 | `raise NotImplementedError` |
| `RetNone` | 5 | `return None` or bare `return` after optional docstring |
| `DocOnly` | 2 | docstring with no executable statements |

## Per-category details

### Protocol (1)

`typing.Protocol` subclass — interface declaration, no body

| File | Line | Symbol | Stub | Rationale |
|---|---:|---|---|---|
| `apps_shared/proof/runtime_drivers/__init__.py` | 35 | `AppRuntimeDriver.invoke` | Ellipsis | class AppRuntimeDriver inherits from Protocol |

### ABC (45)

explicit `abc.ABC` subclass or `@abstractmethod` method

| File | Line | Symbol | Stub | Rationale |
|---|---:|---|---|---|
| `apps_shared/scripts/update_observability_usage_safety_type.py` | 273 | `UpdateObservabilityUsageSafetySafety.apply_safety` | Pass | class UpdateObservabilityUsageSafetySafety inherits from ABC |
| `apps_shared/scripts/update_observability_usage_safety_type.py` | 278 | `UpdateObservabilityUsageSafetySafety.validate_safety` | Pass | class UpdateObservabilityUsageSafetySafety inherits from ABC |
| `apps_shared/types/checkpoint_manager_types.py` | 284 | `CheckpointStorageBackend.save` | Pass | class CheckpointStorageBackend inherits from ABC |
| `apps_shared/types/checkpoint_manager_types.py` | 296 | `CheckpointStorageBackend.load` | Pass | class CheckpointStorageBackend inherits from ABC |
| `apps_shared/types/checkpoint_manager_types.py` | 308 | `CheckpointStorageBackend.delete` | Pass | class CheckpointStorageBackend inherits from ABC |
| `apps_shared/types/checkpoint_manager_types.py` | 321 | `CheckpointStorageBackend.list_checkpoints` | Pass | class CheckpointStorageBackend inherits from ABC |
| `apps_shared/types/checkpoint_manager_types.py` | 333 | `CheckpointStorageBackend.cleanup` | Pass | class CheckpointStorageBackend inherits from ABC |
| `apps_shared/types/coordinate_observability_operations_orchestrator_type.py` | 234 | `CoordinateObservabilityOperationsOrchestratorProcessor.process` | Ellipsis | class CoordinateObservabilityOperationsOrchestratorProcessor inherits from ABC |
| `apps_shared/types/coordinate_observability_operations_orchestrator_type.py` | 239 | `CoordinateObservabilityOperationsOrchestratorProcessor.validate_safety` | Ellipsis | class CoordinateObservabilityOperationsOrchestratorProcessor inherits from ABC |
| `apps_shared/types/dead_letter_queue_types.py` | 341 | `DeadLetterStorage.add` | Pass | class DeadLetterStorage inherits from ABC |
| `apps_shared/types/dead_letter_queue_types.py` | 353 | `DeadLetterStorage.get` | Pass | class DeadLetterStorage inherits from ABC |
| `apps_shared/types/dead_letter_queue_types.py` | 366 | `DeadLetterStorage.list` | Pass | class DeadLetterStorage inherits from ABC |
| `apps_shared/types/dead_letter_queue_types.py` | 379 | `DeadLetterStorage.update_status` | Pass | class DeadLetterStorage inherits from ABC |
| `apps_shared/types/dead_letter_queue_types.py` | 393 | `DeadLetterStorage.delete` | Pass | class DeadLetterStorage inherits from ABC |
| `apps_shared/types/dead_letter_queue_types.py` | 405 | `DeadLetterStorage.cleanup` | Pass | class DeadLetterStorage inherits from ABC |
| `apps_shared/types/engine_type_types.py` | 355 | `DomainValidator.validate_domain_content` | Pass | class DomainValidator inherits from ABC |
| `apps_shared/types/engine_type_types.py` | 368 | `DomainValidator.extract_domain_metrics` | Pass | class DomainValidator inherits from ABC |
| `apps_shared/types/event_bus_types.py` | 342 | `EventBus.connect` | Pass | class EventBus inherits from ABC |
| `apps_shared/types/event_bus_types.py` | 347 | `EventBus.publish` | Pass | class EventBus inherits from ABC |
| `apps_shared/types/event_bus_types.py` | 357 | `EventBus.subscribe` | Pass | class EventBus inherits from ABC |
| `apps_shared/types/event_bus_types.py` | 367 | `EventBus.unsubscribe` | Pass | class EventBus inherits from ABC |
| `apps_shared/types/event_bus_types.py` | 376 | `EventBus.close` | Pass | class EventBus inherits from ABC |
| `apps_shared/types/event_bus_types.py` | 381 | `EventBus.health_check` | Pass | class EventBus inherits from ABC |
| `apps_shared/types/health_status_types.py` | 222 | `HealthChecker.check_health` | Pass | class HealthChecker inherits from ABC |
| `apps_shared/types/health_status_types.py` | 232 | `HealthChecker.component_name` | Pass | class HealthChecker inherits from ABC |
| `apps_shared/types/health_status_types.py` | 238 | `HealthChecker.component_type` | Pass | class HealthChecker inherits from ABC |
| `apps_shared/types/json_exporter_types.py` | 30 | `BaseExporter.export` | Ellipsis | class BaseExporter inherits from ABC |
| `apps_shared/types/orchestrate_observability_planning_orchestrator_type.py` | 222 | `OrchestrateObservabilityPlanningOrchestratorProcessor.process` | Ellipsis | class OrchestrateObservabilityPlanningOrchestratorProcessor inherits from ABC |
| `apps_shared/types/orchestrate_observability_planning_orchestrator_type.py` | 227 | `OrchestrateObservabilityPlanningOrchestratorProcessor.validate_safety` | Ellipsis | class OrchestrateObservabilityPlanningOrchestratorProcessor inherits from ABC |
| `apps_shared/types/otlp_exporter_types.py` | 30 | `BaseExporter.export` | Ellipsis | class BaseExporter inherits from ABC |
| `apps_shared/types/rate_limiter_types.py` | 318 | `RateLimiter.is_allowed` | Pass | class RateLimiter inherits from ABC |
| `apps_shared/types/rate_limiter_types.py` | 330 | `RateLimiter.check_limit` | Pass | class RateLimiter inherits from ABC |
| `apps_shared/types/rate_limiter_types.py` | 342 | `RateLimiter.get_stats` | Pass | class RateLimiter inherits from ABC |
| `apps_shared/types/self_healing_formatter_types.py` | 260 | `FormatRepair.repair` | Pass | class FormatRepair inherits from ABC |
| `apps_shared/types/self_healing_formatter_types.py` | 280 | `FormatRepair.strategy_name` | Pass | class FormatRepair inherits from ABC |
| `apps_shared/types/unified_formatter_types.py` | 288 | `FormatterStrategy.format` | Pass | class FormatterStrategy inherits from ABC |
| `apps_shared/types/unified_formatter_types.py` | 302 | `FormatterStrategy.format_name` | Pass | class FormatterStrategy inherits from ABC |
| `apps_shared/utils/format_observability_context_plan_type_util.py` | 201 | `FormatObservabilityContextPlanProcessor.process` | Ellipsis | class FormatObservabilityContextPlanProcessor inherits from ABC |
| `apps_shared/utils/format_observability_context_plan_type_util.py` | 206 | `FormatObservabilityContextPlanProcessor.validate_safety` | Ellipsis | class FormatObservabilityContextPlanProcessor inherits from ABC |
| `apps_shared/utils/metric_type_util.py` | 749 | `OrchestrateObservabilityPlanningOrchestratorProcessor.process` | Ellipsis | class OrchestrateObservabilityPlanningOrchestratorProcessor inherits from ABC |
| `apps_shared/utils/metric_type_util.py` | 754 | `OrchestrateObservabilityPlanningOrchestratorProcessor.validate_safety` | Ellipsis | class OrchestrateObservabilityPlanningOrchestratorProcessor inherits from ABC |
| `apps_shared/utils/optimize_observability_order_plan_type_util.py` | 201 | `OptimizeObservabilityOrderPlanProcessor.process` | Pass | class OptimizeObservabilityOrderPlanProcessor inherits from ABC |
| `apps_shared/utils/optimize_observability_order_plan_type_util.py` | 206 | `OptimizeObservabilityOrderPlanProcessor.validate_safety` | Pass | class OptimizeObservabilityOrderPlanProcessor inherits from ABC |
| `apps_shared/utils/rank_data_components_plan_type_util.py` | 195 | `RankDataComponentsPlanProcessor.process` | Ellipsis | class RankDataComponentsPlanProcessor inherits from ABC |
| `apps_shared/utils/rank_data_components_plan_type_util.py` | 200 | `RankDataComponentsPlanProcessor.validate_safety` | Ellipsis | class RankDataComponentsPlanProcessor inherits from ABC |

### ImplicitABC (6)

class name suggests abstract (Base/Abstract/Client/Checker/Processor/Provider/Adapter) AND has `NotImplementedError` method — duck-typed abstract

| File | Line | Symbol | Stub | Rationale |
|---|---:|---|---|---|
| `apps_shared/reasoning/health_check.py` | 40 | `HealthChecker.check_health` | NotImpl | class HealthChecker matches implicit-ABC naming (duck-typed abstract pattern with NotImpl method) |
| `apps_shared/reasoning/health_check.py` | 45 | `HealthChecker.component_name` | NotImpl | class HealthChecker matches implicit-ABC naming (duck-typed abstract pattern with NotImpl method) |
| `apps_shared/reasoning/health_check.py` | 50 | `HealthChecker.component_type` | NotImpl | class HealthChecker matches implicit-ABC naming (duck-typed abstract pattern with NotImpl method) |
| `apps_shared/types/model_router_types.py` | 612 | `LLMClient.generate` | NotImpl | class LLMClient matches implicit-ABC naming (duck-typed abstract pattern with NotImpl method) |
| `apps_shared/utils/request_type_util.py` | 341 | `LoadDataPlanningPlanProcessor.process` | NotImpl | class LoadDataPlanningPlanProcessor matches implicit-ABC naming (duck-typed abstract pattern with NotImpl method) |
| `apps_shared/utils/request_type_util.py` | 344 | `LoadDataPlanningPlanProcessor.validate_safety` | NotImpl | class LoadDataPlanningPlanProcessor matches implicit-ABC naming (duck-typed abstract pattern with NotImpl method) |

### TemplateMethodHook (4)

private hook method (`_*`) on Base/Abstract/Executor/Invoker class — subclasses override

| File | Line | Symbol | Stub | Rationale |
|---|---:|---|---|---|
| `apps_shared/reasoning/BaseDispatchAgent.py` | 308 | `BaseDispatchAgent._heal_domain_config` | DocOnly | private hook _heal_domain_config on BaseDispatchAgent (subclasses override) |
| `apps_shared/reasoning/BaseReflectionAgent.py` | 201 | `BaseReflectionAgent._post_reflect` | DocOnly | private hook _post_reflect on BaseReflectionAgent (subclasses override) |
| `apps_shared/types/kx_execution_context_types.py` | 445 | `KXNodeExecutor._extract_reasoning_trace` | RetNone | private hook _extract_reasoning_trace on KXNodeExecutor (subclasses override) |
| `apps_shared/types/tool_category_types.py` | 673 | `ObservabilityToolInvoker._record_invocation_metrics` | Pass | private hook _record_invocation_metrics on ObservabilityToolInvoker (subclasses override) |

### ContextManagerStub (1)

dunder context-manager method (`__enter__`/`__aexit__`/etc.) with no-op body

| File | Line | Symbol | Stub | Rationale |
|---|---:|---|---|---|
| `apps_shared/enforcement/ProvenancetrackerStrategy.py` | 692 | `ProvenanceContext.__aexit__` | Pass | context-manager protocol method __aexit__ with no-op body |

### NullObject (7)

module-level function with descriptive docstring + no-op body — graceful-fallback pattern

| File | Line | Symbol | Stub | Rationale |
|---|---:|---|---|---|
| `apps_shared/reasoning/health_check.py` | 88 | `initialize_system_health_checks` | Pass | module-level initialize_system_health_checks with descriptive docstring and Pass body (graceful-fallback null-object) |
| `apps_shared/utils/observability_clients_util.py` | 17 | `create_span` | RetNone | module-level create_span with descriptive docstring and RetNone body (graceful-fallback null-object) |
| `apps_shared/utils/observability_clients_util.py` | 30 | `record_exception` | Pass | module-level record_exception with descriptive docstring and Pass body (graceful-fallback null-object) |
| `apps_shared/utils/observability_clients_util.py` | 40 | `set_span_attribute` | Pass | module-level set_span_attribute with descriptive docstring and Pass body (graceful-fallback null-object) |
| `apps_shared/utils/provider_util.py` | 31 | `get_client` | RetNone | module-level get_client with descriptive docstring and RetNone body (graceful-fallback null-object) |
| `apps_shared/utils/provider_util.py` | 44 | `get_instructor_client` | RetNone | module-level get_instructor_client with descriptive docstring and RetNone body (graceful-fallback null-object) |
| `apps_shared/utils/provider_util.py` | 57 | `get_litellm_completion` | RetNone | module-level get_litellm_completion with descriptive docstring and RetNone body (graceful-fallback null-object) |

## Regenerating

```bash
python tools/analysis/audit_apps_shared_stubs.py
python tools/analysis/_emit_stub_census_md.py
```

## Consumer notes

The `tools/analysis/_apps_completeness_review2.py` scanner consumes the census JSON (W4 of plan `apps-shared-stub-audit-7dfe16`) and emits a `RealGaps` column distinguishing legitimate Protocol/ABC pattern stubs from real gaps. Without the census, that column falls back to the total stub count.

## Adding a new stub?

If your new function/method genuinely needs a stub body, prefer one of these legitimate patterns (in order of preference):

1. Inherit from `abc.ABC` + `@abstractmethod` — most explicit, static type checkers + CI gates understand it.
2. Inherit from `typing.Protocol` — structural typing; no runtime cost; best when the class describes an interface rather than a base implementation.
3. Structured no-op dict (see `apps_lic/RUNBOOK.md` `#heal-method-notimpl-convention`) — for legitimately-stateless adapters where `raise NotImplementedError` would force every caller into exception handling.
4. Null-object module-level function with descriptive docstring — for graceful-fallback observability/provider wiring.

Avoid bare `pass` bodies on script-level (`scripts/`) files — the audit treats those as RealGap.
