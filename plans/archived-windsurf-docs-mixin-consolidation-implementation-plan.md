---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\mixin-consolidation-implementation-plan.md'
original_relative_path: 'mixin-consolidation-implementation-plan.md'
source_sha256: d850483ab8bbc27282cc188fdcf637396214d82814f072c90205847f47385888
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-10'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Mixin Consolidation Implementation Plan

Consolidate `CachingMixin`, `BatchingMixin`, and `MetricsMixin` into `PerformanceMixin` as canonical owner, convert deprecated mixins to §26-compliant shims, fix `LightweightAgentBase` MRO, remove duplicate `SubatomicTestingMixin` base from `SovereignBaseAgent`, and add CI guardrails — all with backward compatibility preserved.

> **Execution model**: Proceed phase-by-phase; stop on first failing gate. No phase may advance until the current phase's gate tests are green.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Structural Invariant: No Deprecated Re-exports from `performance_mixin.py`

`performance_mixin.py` is the **canonical owner** of performance logic. It MUST NOT export deprecated alias names (`CachingMixin`, `MetricsMixin`, `BatchingMixin`, `CacheConfig`, `MetricsConfig`, `BatchingConfig`). Those names are owned exclusively by the §26 shim files (`caching_mixin.py`, `batching_mixin.py`, `metrics_mixin.py`).

**`performance_mixin.py` `__all__` is restricted to canonical names only:**
```python
__all__ = [
    "PerformanceMixin",
    "PerformanceConfig",
    "PerformanceMetrics",
    "CacheEntry",
]
```

Adding any deprecated alias to `performance_mixin.py` exports is a **HARD FAIL**.

**Gate test (enforced in Phase 9 regression suite):**
```python
def test_performance_mixin_no_deprecated_exports():
    """performance_mixin.py must not re-export deprecated alias names."""
    import ast
    from pathlib import Path
    path = Path("agentic_core/mixins/performance_mixin.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    BANNED = {"CachingMixin", "MetricsMixin", "BatchingMixin",
              "CacheConfig", "MetricsConfig", "BatchingConfig"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        exported = {
                            elt.value for elt in node.value.elts
                            if isinstance(elt, ast.Constant)
                        }
                        violations = exported & BANNED
                        assert not violations, (
                            f"performance_mixin.py exports banned names: {violations}"
                        )
```

---

## Config Aliasing Risk Mitigation

### Problem

`CacheConfig`, `MetricsConfig`, and `BatchingConfig` have **different field names** than `PerformanceConfig`. Aliasing `CacheConfig = PerformanceConfig` would cause `AttributeError` when consumers access legacy fields (e.g., `CacheConfig().enabled` vs `PerformanceConfig.cache_enabled`).

| Legacy dataclass | Legacy field | PerformanceConfig field |
|------------------|-------------|-------------------------|
| `CacheConfig` | `.enabled` | `.cache_enabled` |
| `CacheConfig` | `.max_size` | `.cache_max_size` |
| `CacheConfig` | `.default_ttl` | `.cache_default_ttl` |
| `MetricsConfig` | `.enabled` | `.metrics_enabled` |
| `MetricsConfig` | `.max_history` | `.metrics_max_history` |
| `BatchingConfig` | `.*` | `.*` (fields already match) |

### Mitigation: Dedicated `_config_compat.py` module

Create `agentic_core/mixins/_config_compat.py` containing the legacy config dataclasses with their original field names. This module is **not a shim** (§26 does not apply). The §26 shim files import from `_config_compat` for config types while aliasing mixin classes to `PerformanceMixin`.

**New file**: `agentic_core/mixins/_config_compat.py`
```python
"""
Legacy config dataclasses — backward compatibility only.

These preserve original field names for consumers that access
config attributes by name (e.g., CacheConfig().enabled).

Canonical config: PerformanceConfig in performance_mixin.py.
Do NOT add new fields here; extend PerformanceConfig instead.
"""

from dataclasses import dataclass


@dataclass
class CacheConfig:
    """Legacy caching config with original field names."""
    enabled: bool = True
    max_size: int = 1000
    default_ttl: float = 300.0


@dataclass
class MetricsConfig:
    """Legacy metrics config with original field names."""
    enabled: bool = True
    max_history: int = 100


@dataclass
class BatchingConfig:
    """Legacy batching config with original field names."""
    batch_size: int = 100
    async_pool_size: int = 10
    max_batch_queues: int = 50
    max_batch_queue_size: int = 10000
    lazy_init_enabled: bool = True
```

**Gate test (enforced in Phase 9 regression suite):**
```python
def test_legacy_cache_config_field_access():
    """CacheConfig from shim must support legacy field names."""
    from agentic_core.mixins.caching_mixin import CacheConfig
    cfg = CacheConfig()
    assert cfg.enabled is True
    assert cfg.max_size == 1000
    assert cfg.default_ttl == 300.0

def test_legacy_metrics_config_field_access():
    """MetricsConfig from shim must support legacy field names."""
    from agentic_core.mixins.metrics_mixin import MetricsConfig
    cfg = MetricsConfig()
    assert cfg.enabled is True
    assert cfg.max_history == 100

def test_legacy_batching_config_field_access():
    """BatchingConfig from shim must support legacy field names."""
    from agentic_core.mixins.batching_mixin import BatchingConfig
    cfg = BatchingConfig()
    assert cfg.batch_size == 100
    assert cfg.async_pool_size == 10
```

---

## Blast Radius Summary

| File | Action | Phase |
|------|--------|-------|
| `agentic_core/mixins/performance_mixin.py` | Add compat methods + batch_clear_all/execute_batch/batch_execute/get_batching_status | 1 |
| `agentic_core/mixins/_config_compat.py` | **NEW** — legacy config dataclasses | 2 |
| `agentic_core/mixins/caching_mixin.py` | Replace with §26 shim (imports from _config_compat + performance_mixin) | 3 |
| `agentic_core/mixins/batching_mixin.py` | Replace with §26 shim | 4 |
| `agentic_core/mixins/metrics_mixin.py` | Replace with §26 shim | 5 |
| `agentic_core/base_agents/LightweightBase.py` | Fix missing imports, replace CachingMixin+MetricsMixin with PerformanceMixin | 6 |
| `agentic_core/base_agents/SovereignBaseAgent.py` | Remove duplicate SubatomicTestingMixin from bases | 7 |
| `agentic_core/runtime/utils/trait_system_util.py` | Update CachingTrait/MetricsTrait imports to use PerformanceMixin types | 8 |
| `tests/_quarantine/integration/core_dir/test_mro_refactoring_integration.py` | Update test assertions for shim behavior | 9 |
| `tests/e2e/misc/test_mro_refactoring_e2e.py` | Update test assertions for shim behavior | 9 |
| `tests/agentic_core/mixins/test_mixin_consolidation_regression.py` | **NEW** — regression test suite | 10 |

**Total files modified**: 9 existing + 2 new files

---

## Phase 1: Augment PerformanceMixin with Compatibility API

### Rationale

`PerformanceMixin` already implements the core logic for caching, batching, and metrics. However, the split mixins expose some public methods that `PerformanceMixin` lacks or names differently. Before we can shim the split mixins, `PerformanceMixin` must expose the full union API.

### Sub-phase 1.1: Add CachingMixin-compat methods

**File**: `agentic_core/mixins/performance_mixin.py`

`CachingMixin` has `configure_cache()` — `PerformanceMixin` has `configure_performance()`. Add a compat wrapper.

```diff
--- a/agentic_core/mixins/performance_mixin.py
+++ b/agentic_core/mixins/performance_mixin.py
@@ -232,6 +232,27 @@

         Logger.info(f"[PERF] Configuration updated: {self._perf_config}")

+    # =========================================================================
+    # Compatibility API — CachingMixin surface
+    # =========================================================================
+
+    def configure_cache(
+        self,
+        enabled: bool | None = None,
+        max_size: int | None = None,
+        default_ttl: float | None = None,
+    ) -> None:
+        """Configure caching settings (CachingMixin-compat)."""
+        self.configure_performance(
+            cache_enabled=enabled,
+            cache_max_size=max_size,
+            cache_default_ttl=default_ttl,
+        )
+
     # =========================================================================
     # Caching
     # =========================================================================
```

### Sub-phase 1.2: Add MetricsMixin-compat methods

`MetricsMixin` exposes `record_timing()`, `record_cache_hit()`, `record_cache_miss()` as **public** methods. `PerformanceMixin` has them as `_record_timing()`, `_record_cache_hit()`, `_record_cache_miss()` (private). Also `get_metrics()` vs `get_performance_metrics()` and `configure_metrics()`.

```diff
--- a/agentic_core/mixins/performance_mixin.py
+++ b/agentic_core/mixins/performance_mixin.py
@@ after the CachingMixin compat block @@
+    # =========================================================================
+    # Compatibility API — MetricsMixin surface
+    # =========================================================================
+
+    def configure_metrics(self, enabled: bool | None = None) -> None:
+        """Configure metrics settings (MetricsMixin-compat)."""
+        self.configure_performance(metrics_enabled=enabled)
+
+    def record_timing(self, operation_name: str, duration_ms: float, error: bool = False) -> None:
+        """Record timing for an operation (MetricsMixin-compat public wrapper)."""
+        self._record_timing(operation_name, duration_ms, error)
+
+    def record_cache_hit(self, operation_name: str) -> None:
+        """Record cache hit (MetricsMixin-compat public wrapper)."""
+        self._record_cache_hit(operation_name)
+
+    def record_cache_miss(self, operation_name: str) -> None:
+        """Record cache miss (MetricsMixin-compat public wrapper)."""
+        self._record_cache_miss(operation_name)
+
+    def get_metrics(self, operation_name: str | None = None) -> dict[str, Any]:
+        """Get performance metrics (MetricsMixin-compat alias)."""
+        return self.get_performance_metrics(operation_name)
```

### Sub-phase 1.3: Add BatchingMixin-compat methods

`BatchingMixin` has `batch_clear_all()`, `execute_batch()`, `batch_execute()`, `get_batching_status()`, `configure_batching()` which are **absent** from `PerformanceMixin`. These must be added.

```diff
--- a/agentic_core/mixins/performance_mixin.py
+++ b/agentic_core/mixins/performance_mixin.py
@@ after should_flush_batch @@
+    def batch_clear_all(self) -> int:
+        """Clear all batch queues. Returns count of queues cleared."""
+        with self._perf_lock:
+            count = len(self._batch_queues)
+            self._batch_queues.clear()
+            return count
+
+    # =========================================================================
+    # Parallel Batch Execution (from BatchingMixin consolidation)
+    # =========================================================================
+
+    async def execute_batch(
+        self,
+        tasks: Iterable[Awaitable[T]],
+        *,
+        concurrency: int = 10,
+        timeout: float | None = None,
+        return_exceptions: bool = False,
+    ) -> list[T]:
+        """Execute awaitables with bounded concurrency via asyncio.TaskGroup.
+
+        Args:
+            tasks: Iterable of awaitables to execute.
+            concurrency: Max concurrent tasks (semaphore limit).
+            timeout: Overall timeout in seconds (None = no limit).
+            return_exceptions: If True, exceptions are returned in the
+                result list instead of being raised.
+
+        Returns:
+            Ordered list of results matching the input task order.
+        """
+        task_list = list(tasks)
+        if not task_list:
+            return []
+
+        semaphore = asyncio.Semaphore(concurrency)
+        results: list[Any] = [None] * len(task_list)
+
+        async def _run(index: int, awaitable) -> None:
+            async with semaphore:
+                results[index] = await awaitable
+
+        async def _run_safe(index: int, awaitable) -> None:
+            async with semaphore:
+                try:
+                    results[index] = await awaitable
+                except Exception as exc:
+                    results[index] = exc
+
+        runner = _run_safe if return_exceptions else _run
+
+        async def _execute() -> None:
+            async with asyncio.TaskGroup() as tg:
+                for i, aw in enumerate(task_list):
+                    tg.create_task(runner(i, aw))
+
+        if timeout is not None:
+            await asyncio.wait_for(_execute(), timeout=timeout)
+        else:
+            await _execute()
+
+        return results
+
+    async def batch_execute(
+        self,
+        tasks: list,
+        max_workers: int = 5,
+        sequential: bool = False,
+    ) -> list[Any]:
+        """Backwards-compat alias for legacy batch_operation_mixin callers."""
+        if sequential:
+            results = []
+            for task in tasks:
+                try:
+                    results.append(await task)
+                except Exception as e:
+                    results.append(e)
+            return results
+
+        return await self.execute_batch(
+            tasks,
+            concurrency=max_workers,
+            timeout=120.0,
+            return_exceptions=True,
+        )
+
+    def get_batching_status(self) -> dict[str, Any]:
+        """Get batching status (BatchingMixin-compat)."""
+        with self._perf_lock:
+            return {
+                "batch_queues": {name: len(items) for name, items in self._batch_queues.items()},
+                "lazy_registered": len(self._lazy_registry),
+                "lazy_initialized": len(self._lazy_initialized),
+                "config": {
+                    "batch_size": self._perf_config.batch_size,
+                    "async_pool_size": self._perf_config.async_pool_size,
+                    "max_batch_queues": self._perf_config.max_batch_queues,
+                },
+            }
+
+    def configure_batching(
+        self,
+        batch_size: int | None = None,
+        async_pool_size: int | None = None,
+        max_batch_queues: int | None = None,
+        max_batch_queue_size: int | None = None,
+        lazy_init_enabled: bool | None = None,
+    ) -> None:
+        """Configure batching settings (BatchingMixin-compat)."""
+        self.configure_performance(
+            batch_size=batch_size,
+            async_pool_size=async_pool_size,
+            max_batch_queues=max_batch_queues,
+            max_batch_queue_size=max_batch_queue_size,
+            lazy_init_enabled=lazy_init_enabled,
+        )
```

Also need to add the missing import for `Iterable` and `Awaitable`:

```diff
--- a/agentic_core/mixins/performance_mixin.py
+++ b/agentic_core/mixins/performance_mixin.py
@@ -28,7 +28,7 @@
 from collections import OrderedDict
-from collections.abc import Callable
+from collections.abc import Awaitable, Callable, Iterable
 from dataclasses import dataclass, field
```

### Sub-phase 1.4: Verify `__all__` contains canonical names only

`__all__` MUST remain:
```python
__all__ = [
    "PerformanceMixin",
    "PerformanceConfig",
    "PerformanceMetrics",
    "CacheEntry",
]
```

No deprecated alias names (`CachingMixin`, `MetricsMixin`, `BatchingMixin`, `CacheConfig`, `MetricsConfig`, `BatchingConfig`) may be added. Violation is a **HARD FAIL**.

### Phase 1 Gate

```
pytest tests/agentic_core/mixins/test_performance_mixin.py -xvs
python -c "import ast; ast.parse(open('agentic_core/mixins/performance_mixin.py').read())"
```

Must PASS before proceeding to Phase 2.

### Phase 1 Test Plan

| Test ID | Description | Command |
|---------|-------------|---------|
| P1-T1 | `PerformanceMixin.configure_cache()` delegates correctly | `pytest tests/agentic_core/mixins/test_mixin_consolidation_regression.py::test_configure_cache_compat -xvs` |
| P1-T2 | `PerformanceMixin.record_timing()` public wrapper works | same file `::test_record_timing_public` |
| P1-T3 | `PerformanceMixin.get_metrics()` alias works | same file `::test_get_metrics_alias` |
| P1-T4 | `PerformanceMixin.batch_clear_all()` clears queues | same file `::test_batch_clear_all` |
| P1-T5 | `PerformanceMixin.execute_batch()` runs tasks | same file `::test_execute_batch` |
| P1-T6 | `PerformanceMixin.batch_execute()` legacy compat | same file `::test_batch_execute_compat` |
| P1-T7 | Existing `test_performance_mixin.py` still passes | `pytest tests/agentic_core/mixins/test_performance_mixin.py -xvs` |
| P1-T8 | AST parse check — no syntax errors | `python -c "import ast; ast.parse(open('agentic_core/mixins/performance_mixin.py').read())"` |
| P1-T9 | `__all__` contains no banned deprecated names | regression test `::test_performance_mixin_no_deprecated_exports` |

### Phase 1 Invariant

```python
assert hasattr(PerformanceMixin, 'configure_cache')
assert hasattr(PerformanceMixin, 'configure_metrics')
assert hasattr(PerformanceMixin, 'configure_batching')
assert hasattr(PerformanceMixin, 'record_timing')
assert hasattr(PerformanceMixin, 'record_cache_hit')
assert hasattr(PerformanceMixin, 'record_cache_miss')
assert hasattr(PerformanceMixin, 'get_metrics')
assert hasattr(PerformanceMixin, 'batch_clear_all')
assert hasattr(PerformanceMixin, 'execute_batch')
assert hasattr(PerformanceMixin, 'batch_execute')
assert hasattr(PerformanceMixin, 'get_batching_status')
assert hasattr(PerformanceMixin, 'configure_batching')
```

---

## Phase 2: Create `_config_compat.py` Legacy Config Module

### Rationale

§26 prohibits `ClassDef` in shim files. Legacy config dataclasses (`CacheConfig`, `MetricsConfig`, `BatchingConfig`) have field names that differ from `PerformanceConfig` (e.g., `.enabled` vs `.cache_enabled`). Aliasing `CacheConfig = PerformanceConfig` would cause `AttributeError` for any consumer accessing legacy fields. A dedicated compat module preserves legacy field names without violating §26.

### Sub-phase 2.1: Create new file

**File**: `agentic_core/mixins/_config_compat.py` (**NEW**)

```python
"""
Legacy config dataclasses — backward compatibility only.

These preserve original field names for consumers that access
config attributes by name (e.g., CacheConfig().enabled).

Canonical config: PerformanceConfig in performance_mixin.py.
Do NOT add new fields here; extend PerformanceConfig instead.
"""

from dataclasses import dataclass


@dataclass
class CacheConfig:
    """Legacy caching config with original field names."""
    enabled: bool = True
    max_size: int = 1000
    default_ttl: float = 300.0


@dataclass
class MetricsConfig:
    """Legacy metrics config with original field names."""
    enabled: bool = True
    max_history: int = 100


@dataclass
class BatchingConfig:
    """Legacy batching config with original field names."""
    batch_size: int = 100
    async_pool_size: int = 10
    max_batch_queues: int = 50
    max_batch_queue_size: int = 10000
    lazy_init_enabled: bool = True
```

### Phase 2 Gate

```
python -c "from agentic_core.mixins._config_compat import CacheConfig, MetricsConfig, BatchingConfig; print('OK')"
```

### Phase 2 Test Plan

| Test ID | Description | Command |
|---------|-------------|---------|
| P2-T1 | Module imports cleanly | gate command above |
| P2-T2 | `CacheConfig().enabled` returns True | regression test `::test_legacy_cache_config_field_access` |
| P2-T3 | `MetricsConfig().enabled` returns True | regression test `::test_legacy_metrics_config_field_access` |
| P2-T4 | `BatchingConfig().batch_size` returns 100 | regression test `::test_legacy_batching_config_field_access` |

---

## Phase 3: Convert `CachingMixin` to §26 Shim

### Sub-phase 3.1: Replace file content

**File**: `agentic_core/mixins/caching_mixin.py`

Full file replacement (§26: imports + `__all__` + docstring only):

```python
"""
CachingMixin — §26-compliant backward-compatibility shim.

DEPRECATED: CachingMixin is now an alias for PerformanceMixin.
All caching functionality is canonically owned by PerformanceMixin.
This shim preserves import paths for existing consumers.

Migration: Replace `from agentic_core.mixins.caching_mixin import CachingMixin`
           with    `from agentic_core.mixins.performance_mixin import PerformanceMixin`
"""

from agentic_core.mixins._config_compat import CacheConfig
from agentic_core.mixins.performance_mixin import (
    CacheEntry,
    PerformanceMixin as CachingMixin,
)

__all__ = ["CachingMixin", "CacheConfig", "CacheEntry"]
```

**Key decisions**:
- `CacheConfig` imported from `_config_compat` — preserves `.enabled`, `.max_size`, `.default_ttl` field names.
- `CacheEntry` re-exported from `performance_mixin.py` where the canonical copy lives.
- `CachingMixin = PerformanceMixin` — full API compat because Phase 1 added `configure_cache()`.
- No `ClassDef`, `FunctionDef`, or logic → passes §26 AST lock.

### Phase 3 Gate

```
pytest tests/agentic_core/mixins/test_caching_mixin.py -xvs
```

### Phase 3 Test Plan

| Test ID | Description | Command |
|---------|-------------|---------|
| P3-T1 | `from agentic_core.mixins.caching_mixin import CachingMixin` succeeds | `pytest tests/agentic_core/mixins/test_caching_mixin.py -xvs` |
| P3-T2 | `CachingMixin is PerformanceMixin` | regression test |
| P3-T3 | `isinstance(PerformanceMixin(), CachingMixin)` is True | regression test |
| P3-T4 | `CacheEntry` import from shim resolves | regression test |
| P3-T5 | §26 AST lock: no ClassDef or FunctionDef in shim | regression test |
| P3-T6 | `CacheConfig().enabled` returns True (legacy field access) | regression test `::test_legacy_cache_config_field_access` |
| P3-T7 | Existing `test_caching_mixin.py` passes | gate command |

### Phase 3 Invariant

```python
from agentic_core.mixins.caching_mixin import CachingMixin, CacheConfig, CacheEntry
from agentic_core.mixins.performance_mixin import PerformanceMixin
assert CachingMixin is PerformanceMixin
assert CacheConfig().enabled is True  # legacy field name works
```

---

## Phase 4: Convert `BatchingMixin` to §26 Shim

### Sub-phase 4.1: Replace file content

**File**: `agentic_core/mixins/batching_mixin.py`

```python
"""
BatchingMixin — §26-compliant backward-compatibility shim.

DEPRECATED: BatchingMixin is now an alias for PerformanceMixin.
All batching functionality is canonically owned by PerformanceMixin.
This shim preserves import paths for existing consumers.

Migration: Replace `from agentic_core.mixins.batching_mixin import BatchingMixin`
           with    `from agentic_core.mixins.performance_mixin import PerformanceMixin`
"""

from agentic_core.mixins._config_compat import BatchingConfig
from agentic_core.mixins.performance_mixin import PerformanceMixin as BatchingMixin

__all__ = ["BatchingMixin", "BatchingConfig"]
```

**Key decisions**:
- `BatchingConfig` imported from `_config_compat` — field names already match `PerformanceConfig` but the type is preserved for `isinstance` checks.
- Phase 1 added `batch_clear_all`, `execute_batch`, `batch_execute`, `get_batching_status`, `configure_batching` to `PerformanceMixin`, so full API compat.
- No consumers inherit `BatchingMixin` directly in production agent classes (only tests).

### Phase 4 Gate

```
pytest tests/agentic_core/mixins/test_batching_mixin.py -xvs
```

### Phase 4 Test Plan

| Test ID | Description | Command |
|---------|-------------|---------|
| P4-T1 | `from agentic_core.mixins.batching_mixin import BatchingMixin` succeeds | gate command |
| P4-T2 | `BatchingMixin is PerformanceMixin` | regression test |
| P4-T3 | §26 AST lock: no ClassDef or FunctionDef in shim | regression test |
| P4-T4 | `BatchingConfig().batch_size` returns 100 (legacy field access) | regression test `::test_legacy_batching_config_field_access` |
| P4-T5 | Existing `test_batching_mixin.py` passes | gate command |

### Phase 4 Invariant

```python
from agentic_core.mixins.batching_mixin import BatchingMixin, BatchingConfig
from agentic_core.mixins.performance_mixin import PerformanceMixin
assert BatchingMixin is PerformanceMixin
assert BatchingConfig().batch_size == 100
```

---

## Phase 5: Convert `MetricsMixin` to §26 Shim

### Sub-phase 5.1: Replace file content

**File**: `agentic_core/mixins/metrics_mixin.py`

```python
"""
MetricsMixin — §26-compliant backward-compatibility shim.

DEPRECATED: MetricsMixin is now an alias for PerformanceMixin.
All metrics functionality is canonically owned by PerformanceMixin.
This shim preserves import paths for existing consumers.

Migration: Replace `from agentic_core.mixins.metrics_mixin import MetricsMixin`
           with    `from agentic_core.mixins.performance_mixin import PerformanceMixin`
"""

from agentic_core.mixins._config_compat import MetricsConfig
from agentic_core.mixins.performance_mixin import (
    PerformanceMetrics,
    PerformanceMixin as MetricsMixin,
)

__all__ = ["MetricsMixin", "MetricsConfig", "PerformanceMetrics"]
```

**Key decisions**:
- `PerformanceMetrics` re-exported (canonical copy in `performance_mixin.py`). Eliminates EXACT-duplicate dataclass.
- `MetricsConfig` imported from `_config_compat` — preserves `.enabled` and `.max_history` field names.
- Phase 1 added `record_timing`, `record_cache_hit`, `record_cache_miss`, `get_metrics`, `configure_metrics` as public methods to `PerformanceMixin`.

### Phase 5 Gate

```
pytest tests/agentic_core/mixins/test_metrics_mixin.py -xvs
```

### Phase 5 Test Plan

| Test ID | Description | Command |
|---------|-------------|---------|
| P5-T1 | `from agentic_core.mixins.metrics_mixin import MetricsMixin` succeeds | gate command |
| P5-T2 | `MetricsMixin is PerformanceMixin` | regression test |
| P5-T3 | `from agentic_core.mixins.metrics_mixin import PerformanceMetrics` succeeds | regression test |
| P5-T4 | §26 AST lock: no ClassDef or FunctionDef in shim | regression test |
| P5-T5 | `MetricsConfig().enabled` returns True (legacy field access) | regression test `::test_legacy_metrics_config_field_access` |
| P5-T6 | Existing `test_metrics_mixin.py` passes | gate command |

### Phase 5 Invariant

```python
from agentic_core.mixins.metrics_mixin import MetricsMixin, MetricsConfig, PerformanceMetrics
from agentic_core.mixins.performance_mixin import PerformanceMixin
from agentic_core.mixins.performance_mixin import PerformanceMetrics as PM2
assert MetricsMixin is PerformanceMixin
assert PerformanceMetrics is PM2  # same class object, not a copy
assert MetricsConfig().enabled is True  # legacy field name works
```

---

## Phase 6: Update `LightweightAgentBase` MRO

### Pre-existing Bug

`LightweightBase.py` lines 44-49 reference `CostGuardrailMixin`, `ContextManagementMixin`, `TracingMixin`, `CachingMixin`, `MetricsMixin` as class bases but **never imports them**. The `__post_init__` manually initializes state. This phase fixes the bug AND updates the MRO.

### Sub-phase 6.1: Full file diff

**File**: `agentic_core/base_agents/LightweightBase.py`

```diff
--- a/agentic_core/base_agents/LightweightBase.py
+++ b/agentic_core/base_agents/LightweightBase.py
@@ -1,12 +1,11 @@
 """
 LightweightAgentBase - Minimal Infrastructure for Simple Agents

-Phase 4 MRO Refactoring: Alternative to full SovereignBaseAgent.
+Phase 4+P0 MRO Refactoring: Alternative to full SovereignBaseAgent.

 Provides only essential infrastructure:
 - CostGuardrailMixin (budget control)
 - ContextManagementMixin (context window management)
 - TracingMixin (observability)
-- CachingMixin (performance - from Phase 3 split)
-- MetricsMixin (performance - from Phase 3 split)
+- PerformanceMixin (caching + metrics + batching - canonical owner)

 Does NOT include:
@@ -18,7 +17,7 @@
 - SubatomicTestingMixin (self-testing - optional)

-MRO Depth: ~8 classes (vs ~20+ for full SovereignBaseAgent)
+MRO Depth: ~6 classes (vs ~20+ for full SovereignBaseAgent)

 Usage:
     class SimpleAgent(LightweightAgentBase):
@@ -33,7 +32,11 @@

 from __future__ import annotations

 import logging
 from dataclasses import dataclass
 from typing import Any

+from agentic_core.mixins.context_management_mixin import ContextManagementMixin
+from agentic_core.mixins.cost_mixin import CostGuardrailMixin
+from agentic_core.mixins.performance_mixin import PerformanceMixin
+from agentic_core.mixins.tracing_mixin import TracingMixin
+
 Logger = logging.getLogger(__name__)


 @dataclass
 class LightweightAgentBase(
     CostGuardrailMixin,
     ContextManagementMixin,
     TracingMixin,
-    CachingMixin,
-    MetricsMixin,
+    PerformanceMixin,
 ):
     """
     Lightweight base agent with minimal infrastructure.

-    Phase 4 MRO Refactoring: Reduced MRO depth for simple agents.
+    Phase 4+P0 MRO Refactoring: Reduced MRO depth for simple agents.

     Includes:
     - Cost control and budget enforcement
     - Context window management
     - Distributed tracing
-    - LRU caching with TTL
-    - Performance metrics collection
+    - LRU caching with TTL (via PerformanceMixin)
+    - Performance metrics collection (via PerformanceMixin)
+    - Batch operations (via PerformanceMixin)

     For additional capabilities, inherit from the relevant mixins:
     - HealerMixin: For autonomous healing
     - HITLMixin: For human-in-the-loop workflows
-    - BatchingMixin: For batch operations
     - MCPHardenedMixin: For MCP protocol safety
     """

     def __post_init__(self) -> None:
         """Initialize lightweight infrastructure."""
-        # Initialize all parent mixins
-        # Note: dataclass doesn't call __init__ automatically for mixins
-        # so we need to initialize them here
-
-        # Initialize CachingMixin
-        import threading
-        from collections import OrderedDict
-
-        from agentic_core.mixins.caching_mixin import CacheConfig
-
-        self._cache_config = CacheConfig()
-        self._cache_store = OrderedDict()
-        self._cache_lock = threading.RLock()
-        self._caching_initialized = True
-
-        # Initialize MetricsMixin
-        from agentic_core.mixins.metrics_mixin import MetricsConfig
-
-        self._metrics_config = MetricsConfig()
-        self._metrics_store = {}
-        self._metrics_lock = threading.RLock()
-        self._metrics_initialized = True
+        # PerformanceMixin.__init__ handles caching, metrics, batching state
+        try:
+            super().__post_init__()
+        except AttributeError:
+            pass

         self._lightweight_initialized = True

@@ in get_lightweight_status @@
             "capabilities": [
                 "cost_control",
                 "context_management",
                 "tracing",
                 "caching",
                 "metrics",
+                "batching",
             ],
```

### Phase 6 Gate

```
python -c "from agentic_core.base_agents.LightweightBase import LightweightAgentBase; print('OK')"
pytest tests/e2e/misc/test_mro_refactoring_e2e.py::TestPhase4E2E -xvs
```

### Phase 6 Test Plan

| Test ID | Description | Command |
|---------|-------------|---------|
| P6-T1 | `from agentic_core.base_agents.LightweightBase import LightweightAgentBase` succeeds | gate command |
| P6-T2 | `LightweightAgentBase` subclass has `cache_get`, `cache_set` | regression test |
| P6-T3 | `LightweightAgentBase` subclass has `record_timing`, `get_metrics` | regression test |
| P6-T4 | `LightweightAgentBase` subclass has `batch_add`, `batch_flush` | regression test |
| P6-T5 | MRO depth < 10 (was ~8, now ~6) | regression test |
| P6-T6 | `verify_lightweight_state()` returns True | regression test |
| P6-T7 | E2E test `test_lightweight_base_is_functional` passes | gate command |

### Phase 6 Invariant

```python
from agentic_core.base_agents.LightweightBase import LightweightAgentBase
agent = LightweightAgentBase()
agent.cache_set("k", "v")
assert agent.cache_get("k") == (True, "v")
agent.record_timing("op", 50.0)
assert agent.get_metrics("op")["call_count"] == 1
assert len(LightweightAgentBase.__mro__) < 10
```

---

## Phase 7: Remove Duplicate `SubatomicTestingMixin` from `SovereignBaseAgent`

### Sub-phase 7.1: Remove duplicate base

`SubatomicTestingMixin` appears BOTH in `infrastructure_mixin` (line 58) AND directly on `SovereignBaseAgent` (line 75). Python C3 resolves this, but it's architectural drift.

**File**: `agentic_core/base_agents/SovereignBaseAgent.py`

```diff
--- a/agentic_core/base_agents/SovereignBaseAgent.py
+++ b/agentic_core/base_agents/SovereignBaseAgent.py
@@ -60,7 +60,6 @@
 from agentic_core.mixins.infrastructure_mixin import infrastructure_mixin
 from agentic_core.mixins.llm_provider_mixin import LLMProviderMixin
 from agentic_core.mixins.meta_learning_client_mixin import MetaLearningClientMixin
 from agentic_core.mixins.runtime_safety_mixin import RuntimeSafetyMixin
-from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
 from agentic_core.mixins.validator_mixin import ValidatorMixin
 from agentic_core.runtime.exceptions.healer_exceptions import ConfigurationError
 from agentic_core.runtime.exceptions.sovereign_errors import SovereignError
@@ -73,7 +72,6 @@
 @dataclass
 class SovereignBaseAgent(
     infrastructure_mixin,
-    SubatomicTestingMixin,
     ConfigMixin,
     LLMProviderMixin,
     EmbeddingMixin,
```

### Phase 7 Gate

```
python -c "from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent; print('OK')"
```

### Phase 7 Test Plan

| Test ID | Description | Command |
|---------|-------------|---------|
| P7-T1 | `SovereignBaseAgent.__mro__` contains `SubatomicTestingMixin` exactly once | regression test |
| P7-T2 | `from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent` succeeds | gate command |
| P7-T3 | `hasattr(SovereignBaseAgent, 'run_subatomic_tests')` still True (inherited from infrastructure_mixin) | regression test |

### Phase 7 Invariant

```python
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
assert SubatomicTestingMixin in SovereignBaseAgent.__mro__
assert SovereignBaseAgent.__mro__.count(SubatomicTestingMixin) == 1
```

---

## Phase 8: Update `trait_system_util.py` Imports

### Sub-phase 8.1: Update CachingTrait and MetricsTrait imports

`CachingTrait` imports `CacheConfig`, `CacheEntry` from `caching_mixin.py`. `MetricsTrait` imports `MetricsConfig`, `PerformanceMetrics` from `metrics_mixin.py`. Update to canonical imports from `performance_mixin.py` and `_config_compat.py`.

**File**: `agentic_core/runtime/utils/trait_system_util.py`

```diff
--- a/agentic_core/runtime/utils/trait_system_util.py
+++ b/agentic_core/runtime/utils/trait_system_util.py
@@ -72,7 +72,10 @@
         import threading
         from collections import OrderedDict

-        from agentic_core.mixins.caching_mixin import CacheConfig, CacheEntry
+        from agentic_core.mixins._config_compat import CacheConfig
+        from agentic_core.mixins.performance_mixin import CacheEntry

@@ -144,7 +147,7 @@
         import threading

-        from agentic_core.mixins.metrics_mixin import (
-            MetricsConfig,
-            PerformanceMetrics,
-        )
+        from agentic_core.mixins._config_compat import MetricsConfig
+        from agentic_core.mixins.performance_mixin import PerformanceMetrics
```

### Phase 8 Gate

```
python -c "from agentic_core.runtime.utils.trait_system_util import CachingTrait, MetricsTrait; print('OK')"
```

### Phase 8 Test Plan

| Test ID | Description | Command |
|---------|-------------|---------|
| P8-T1 | `from agentic_core.runtime.utils.trait_system_util import CachingTrait` succeeds | gate command |
| P8-T2 | `CachingTrait.apply(TestClass)` produces class with `cache_get` | regression test |
| P8-T3 | `MetricsTrait.apply(TestClass)` produces class with `record_timing` | regression test |

---

## Phase 9: Update Integration and E2E Tests

### Sub-phase 9.1: Quarantined integration test

**File**: `tests/_quarantine/integration/core_dir/test_mro_refactoring_integration.py`

The `TestSplitMixinsCombined` tests create `class TestAgent(CachingMixin, MetricsMixin, BatchingMixin)`. Post-shimming, all three are `PerformanceMixin`, so this becomes `class TestAgent(PerformanceMixin, PerformanceMixin, PerformanceMixin)` which Python deduplicates. The test still passes because the methods exist. However, `test_split_mixins_no_conflicts` checks for `_cache_config`, `_metrics_config`, `_batching_config` — these attribute names differ from `PerformanceMixin`'s `_perf_config`.

```diff
--- a/tests/_quarantine/integration/core_dir/test_mro_refactoring_integration.py
+++ b/tests/_quarantine/integration/core_dir/test_mro_refactoring_integration.py
@@ -180,13 +180,12 @@
     def test_split_mixins_no_conflicts(self):
-        """Split mixins should have no attribute conflicts."""
-        from agentic_core.mixins.batching_mixin import BatchingMixin
-        from agentic_core.mixins.caching_mixin import CachingMixin
-        from agentic_core.mixins.metrics_mixin import MetricsMixin
+        """Post-consolidation: all shims resolve to PerformanceMixin."""
+        from agentic_core.mixins.performance_mixin import PerformanceMixin

-        class TestAgent(CachingMixin, MetricsMixin, BatchingMixin):
+        class TestAgent(PerformanceMixin):
             pass

         agent = TestAgent()

-        # Each mixin has its own state
-        assert hasattr(agent, "_cache_config")
-        assert hasattr(agent, "_metrics_config")
-        assert hasattr(agent, "_batching_config")
+        # Single unified config
+        assert hasattr(agent, "_perf_config")
+        assert hasattr(agent, "cache_get")
+        assert hasattr(agent, "record_timing")
+        assert hasattr(agent, "batch_add")
```

### Sub-phase 9.2: E2E test

**File**: `tests/e2e/misc/test_mro_refactoring_e2e.py`

`TestPhase3E2E.test_split_mixins_work_independently` creates standalone `CacheOnlyAgent(CachingMixin)`, etc. Post-shimming these become `CacheOnlyAgent(PerformanceMixin)` which is fine — they'll have more methods but the tested methods still work.

The only change needed is `TestAllPhasesIntegrated.test_all_new_files_exist` which checks for files at wrong paths:

```diff
--- a/tests/e2e/misc/test_mro_refactoring_e2e.py
+++ b/tests/e2e/misc/test_mro_refactoring_e2e.py
@@ -256,13 +256,13 @@
         new_files = [
             # Phase 2
             PROJECT_ROOT / "agentic_core" / "L2_execution" / "gateway_factory.py",
-            # Phase 3
-            PROJECT_ROOT / "agentic_core" / "base_agents" / "caching_mixin.py",
-            PROJECT_ROOT / "agentic_core" / "base_agents" / "metrics_mixin.py",
-            PROJECT_ROOT / "agentic_core" / "base_agents" / "batching_mixin.py",
+            # Phase 3 (now shims in mixins/)
+            PROJECT_ROOT / "agentic_core" / "mixins" / "caching_mixin.py",
+            PROJECT_ROOT / "agentic_core" / "mixins" / "metrics_mixin.py",
+            PROJECT_ROOT / "agentic_core" / "mixins" / "batching_mixin.py",
             # Phase 4
-            PROJECT_ROOT / "agentic_core" / "base_agents" / "lightweight_agent_base.py",
+            PROJECT_ROOT / "agentic_core" / "base_agents" / "LightweightBase.py",
             # Phase 5
             PROJECT_ROOT / "agentic_core" / "base_agents" / "trait_system.py",
         ]
```

Same fix for `test_all_new_files_are_valid_python`.

### Phase 9 Gate

```
pytest tests/_quarantine/integration/core_dir/test_mro_refactoring_integration.py -xvs
pytest tests/e2e/misc/test_mro_refactoring_e2e.py -xvs
```

---

## Phase 10: Create Consolidation Regression Test Suite

### Sub-phase 10.1: New test file

**File**: `tests/agentic_core/mixins/test_mixin_consolidation_regression.py` (**NEW**)

```python
"""
Mixin Consolidation Regression Tests
=====================================
Verifies P0 consolidation invariants:
1. Shims are §26-compliant (no ClassDef/FunctionDef)
2. Shims resolve to PerformanceMixin
3. PerformanceMixin exposes full union API
4. performance_mixin.py does not re-export deprecated names
5. Legacy config dataclasses preserve original field names
6. LightweightAgentBase MRO is correct
7. SovereignBaseAgent MRO has no duplicate bases
"""

import ast
import importlib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]

pytestmark = [pytest.mark.unit, pytest.mark.guardian]


# ── Structural Invariant: No deprecated re-exports ────────────────────

def test_performance_mixin_no_deprecated_exports():
    """performance_mixin.py must not re-export deprecated alias names."""
    path = PROJECT_ROOT / "agentic_core" / "mixins" / "performance_mixin.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    BANNED = {"CachingMixin", "MetricsMixin", "BatchingMixin",
              "CacheConfig", "MetricsConfig", "BatchingConfig"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        exported = {
                            elt.value for elt in node.value.elts
                            if isinstance(elt, ast.Constant)
                        }
                        violations = exported & BANNED
                        assert not violations, (
                            f"performance_mixin.py exports banned names: {violations}"
                        )


# ── §26 Shim Structural Lock ──────────────────────────────────────────

SHIM_FILES = [
    "agentic_core/mixins/caching_mixin.py",
    "agentic_core/mixins/batching_mixin.py",
    "agentic_core/mixins/metrics_mixin.py",
]


@pytest.mark.parametrize("rel_path", SHIM_FILES)
def test_shim_no_classdef(rel_path):
    """§26: Shim files must not contain ClassDef."""
    path = PROJECT_ROOT / rel_path
    tree = ast.parse(path.read_text(encoding="utf-8"))
    class_defs = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    assert class_defs == [], f"{rel_path} contains ClassDef: {[c.name for c in class_defs]}"


@pytest.mark.parametrize("rel_path", SHIM_FILES)
def test_shim_no_functiondef(rel_path):
    """§26: Shim files must not contain FunctionDef."""
    path = PROJECT_ROOT / rel_path
    tree = ast.parse(path.read_text(encoding="utf-8"))
    func_defs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    assert func_defs == [], f"{rel_path} contains FunctionDef: {[f.name for f in func_defs]}"


@pytest.mark.parametrize("rel_path", SHIM_FILES)
def test_shim_has_all(rel_path):
    """§26: Shim files must have __all__."""
    path = PROJECT_ROOT / rel_path
    tree = ast.parse(path.read_text(encoding="utf-8"))
    has_all = any(
        isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "__all__" for t in n.targets)
        for n in ast.walk(tree)
    )
    assert has_all, f"{rel_path} missing __all__"


@pytest.mark.parametrize("rel_path", SHIM_FILES)
def test_shim_under_30_loc(rel_path):
    """§26: Shim files should be < 30 LOC."""
    path = PROJECT_ROOT / rel_path
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip() and not l.strip().startswith("#")]
    assert len(lines) < 30, f"{rel_path} has {len(lines)} non-blank/non-comment lines (limit: 30)"


# ── Shim Identity ─────────────────────────────────────────────────────

def test_caching_mixin_is_performance_mixin():
    from agentic_core.mixins.caching_mixin import CachingMixin
    from agentic_core.mixins.performance_mixin import PerformanceMixin
    assert CachingMixin is PerformanceMixin


def test_batching_mixin_is_performance_mixin():
    from agentic_core.mixins.batching_mixin import BatchingMixin
    from agentic_core.mixins.performance_mixin import PerformanceMixin
    assert BatchingMixin is PerformanceMixin


def test_metrics_mixin_is_performance_mixin():
    from agentic_core.mixins.metrics_mixin import MetricsMixin
    from agentic_core.mixins.performance_mixin import PerformanceMixin
    assert MetricsMixin is PerformanceMixin


def test_performance_metrics_ssot():
    """PerformanceMetrics must exist in exactly one canonical location."""
    from agentic_core.mixins.metrics_mixin import PerformanceMetrics as PM1
    from agentic_core.mixins.performance_mixin import PerformanceMetrics as PM2
    assert PM1 is PM2


# ── Legacy Config Field Access (config aliasing risk gate) ────────────

def test_legacy_cache_config_field_access():
    """CacheConfig from shim must support legacy field names."""
    from agentic_core.mixins.caching_mixin import CacheConfig
    cfg = CacheConfig()
    assert cfg.enabled is True
    assert cfg.max_size == 1000
    assert cfg.default_ttl == 300.0


def test_legacy_metrics_config_field_access():
    """MetricsConfig from shim must support legacy field names."""
    from agentic_core.mixins.metrics_mixin import MetricsConfig
    cfg = MetricsConfig()
    assert cfg.enabled is True
    assert cfg.max_history == 100


def test_legacy_batching_config_field_access():
    """BatchingConfig from shim must support legacy field names."""
    from agentic_core.mixins.batching_mixin import BatchingConfig
    cfg = BatchingConfig()
    assert cfg.batch_size == 100
    assert cfg.async_pool_size == 10


# ── PerformanceMixin Union API ─────────────────────────────────────────

UNION_API = [
    # CachingMixin surface
    "cache_get", "cache_set", "cache_invalidate", "cache_clear",
    "cache_stats", "cached", "configure_cache",
    # MetricsMixin surface
    "record_timing", "record_cache_hit", "record_cache_miss",
    "get_metrics", "reset_metrics", "timed", "configure_metrics",
    # BatchingMixin surface
    "batch_add", "batch_flush", "batch_size", "should_flush_batch",
    "batch_clear_all", "register_lazy", "get_lazy", "is_lazy_initialized",
    "get_async_semaphore", "run_pooled", "execute_batch", "batch_execute",
    "get_batching_status", "configure_batching",
    # PerformanceMixin canonical
    "configure_performance", "get_performance_metrics", "get_performance_status",
]


@pytest.mark.parametrize("method_name", UNION_API)
def test_performance_mixin_has_method(method_name):
    from agentic_core.mixins.performance_mixin import PerformanceMixin
    assert hasattr(PerformanceMixin, method_name), f"PerformanceMixin missing: {method_name}"


# ── PerformanceMixin Functional ────────────────────────────────────────

def test_configure_cache_compat():
    from agentic_core.mixins.performance_mixin import PerformanceMixin
    agent = PerformanceMixin()
    agent.configure_cache(enabled=False)
    assert agent._perf_config.cache_enabled is False


def test_record_timing_public():
    from agentic_core.mixins.performance_mixin import PerformanceMixin
    agent = PerformanceMixin()
    agent.record_timing("op", 42.0)
    metrics = agent.get_metrics("op")
    assert metrics["call_count"] == 1
    assert metrics["total_time_ms"] == 42.0


def test_get_metrics_alias():
    from agentic_core.mixins.performance_mixin import PerformanceMixin
    agent = PerformanceMixin()
    agent.record_timing("op", 10.0)
    assert agent.get_metrics("op") == agent.get_performance_metrics("op")


def test_batch_clear_all():
    from agentic_core.mixins.performance_mixin import PerformanceMixin
    agent = PerformanceMixin()
    agent.batch_add("q1", "a")
    agent.batch_add("q2", "b")
    count = agent.batch_clear_all()
    assert count == 2
    assert agent.batch_size("q1") == 0


def test_configure_batching_compat():
    from agentic_core.mixins.performance_mixin import PerformanceMixin
    agent = PerformanceMixin()
    agent.configure_batching(batch_size=50)
    assert agent._perf_config.batch_size == 50


def test_configure_metrics_compat():
    from agentic_core.mixins.performance_mixin import PerformanceMixin
    agent = PerformanceMixin()
    agent.configure_metrics(enabled=False)
    assert agent._perf_config.metrics_enabled is False


# ── LightweightAgentBase MRO ──────────────────────────────────────────

def test_lightweight_mro_depth():
    from agentic_core.base_agents.LightweightBase import LightweightAgentBase
    mro_depth = len(LightweightAgentBase.__mro__)
    assert mro_depth < 10, f"MRO depth {mro_depth} should be < 10"


def test_lightweight_has_caching():
    from agentic_core.base_agents.LightweightBase import LightweightAgentBase
    assert hasattr(LightweightAgentBase, "cache_get")
    assert hasattr(LightweightAgentBase, "cache_set")


def test_lightweight_has_metrics():
    from agentic_core.base_agents.LightweightBase import LightweightAgentBase
    assert hasattr(LightweightAgentBase, "record_timing")
    assert hasattr(LightweightAgentBase, "get_metrics")


def test_lightweight_has_batching():
    from agentic_core.base_agents.LightweightBase import LightweightAgentBase
    assert hasattr(LightweightAgentBase, "batch_add")


# ── SovereignBaseAgent MRO ─────────────────────────────────────────────

def test_sovereign_no_duplicate_subatomic():
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
    count = SovereignBaseAgent.__mro__.count(SubatomicTestingMixin)
    assert count == 1, f"SubatomicTestingMixin appears {count}x in MRO (expected 1)"


def test_sovereign_still_has_subatomic():
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
    assert SubatomicTestingMixin in SovereignBaseAgent.__mro__
```

### Phase 10 Gate (FINAL)

```
pytest tests/agentic_core/mixins/test_mixin_consolidation_regression.py -xvs
pytest tests/agentic_core/mixins/test_caching_mixin.py -xvs
pytest tests/agentic_core/mixins/test_batching_mixin.py -xvs
pytest tests/agentic_core/mixins/test_metrics_mixin.py -xvs
pytest tests/agentic_core/mixins/test_performance_mixin.py -xvs
```

---

## Execution Order and Gate Conditions

```
Phase 1 ─→ Phase 2 ─→ Phase 3 ─→ Phase 4 ─→ Phase 5 ─→ Phase 6 ─→ Phase 7 ─→ Phase 8 ─→ Phase 9 ─→ Phase 10
  │           │           │           │           │           │           │           │           │           │
  │ GATE:     │ GATE:     │ GATE:     │ GATE:     │ GATE:     │ GATE:     │ GATE:     │ GATE:     │ GATE:     │ FINAL:
  │ perf test │ import    │ caching   │ batching  │ metrics   │ import    │ import    │ import    │ integ+e2e │ full
  │ + AST     │ compat    │ test      │ test      │ test      │ Lweight   │ Sovereign │ trait     │ tests     │ regress
```

Proceed phase-by-phase; stop on first failing gate. If any gate fails → root-cause, fix, re-run same phase. Do not advance until the current phase is green.

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Config field name mismatch** (`CacheConfig.enabled` vs `PerformanceConfig.cache_enabled`) | **HIGH** | Legacy config dataclasses retained in `_config_compat.py` with original field names. Shims import from `_config_compat` for config types. Gate tests: `test_legacy_cache_config_field_access`, `test_legacy_metrics_config_field_access`, `test_legacy_batching_config_field_access`. Failure of any gate test blocks the phase. |
| Deprecated names re-exported from `performance_mixin.py` | **HIGH** | Structural invariant + AST-based gate test `test_performance_mixin_no_deprecated_exports` enforced in Phase 10. Adding any banned name to `__all__` is a HARD FAIL. |
| Thread-safety regression | MEDIUM | `PerformanceMixin` uses `_perf_lock` for all operations — same pattern as split mixins. No regression. |
| `isinstance` checks in decorators | LOW | `CachingMixin.cached` checks `isinstance(self, CachingMixin)`. Post-shim, `CachingMixin IS PerformanceMixin`, so any `PerformanceMixin` instance passes. This is **correct** — wider acceptance, no false negatives. |
| E2E test checks file paths that don't exist | LOW | Fixed in Phase 9 — paths updated to actual locations. |
| `trait_system_util.py` accesses `.enabled` on what it thinks is `CacheConfig` | **HIGH** | Phase 8 updates trait imports to use `CacheConfig` from `_config_compat` (which has `.enabled`). Gate test: `CachingTrait.apply(TestClass)` must produce working class. |

---

## Metrics (Expected Post-Implementation)

| Metric | Before | After |
|--------|--------|-------|
| Canonical mixin classes | 54 | 51 (-3: CachingMixin, BatchingMixin, MetricsMixin become shims) |
| EXACT M↔M clusters | 12 | 0 |
| NEAR M↔M clusters (caching/batching/metrics) | 8 | 0 |
| `SovereignBaseAgent` direct bases | 12 | 11 (-SubatomicTestingMixin duplicate) |
| `LightweightAgentBase` direct bases | 5 | 4 (PerformanceMixin replaces CachingMixin+MetricsMixin) |
| `LightweightAgentBase` MRO depth | ~8 | ~6 |
| `PerformanceMetrics` definitions | 2 (duplicate) | 1 (canonical in performance_mixin.py) |
| New files | 0 | 2 (`_config_compat.py`, `test_mixin_consolidation_regression.py`) |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

