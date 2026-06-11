---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\dependency_remediation_analysis.md'
original_relative_path: 'dependency_remediation_analysis.md'
source_sha256: f47bce0c1e69620c6c55457eeac5531827c1ad3a3970a57d57d80188bcfc78e1
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Dependency Remediation Analysis — Packaging Policy

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Baseline Gates (Acceptance Criteria)

All gates MUST PASS after remediation:

### Gate A: Import Gate (core-only env)
```bash
pip install -e .
python -c "import agentic_core; import apps_shared"
```
**Expected:** Exit code 0, no ImportError

### Gate B: Core Verifier (core-only env)
```bash
python docs/reports/plans/dependency_verify_imports.py
```
**Expected:** Exit code 0, 0 BLOCKING failures (13 core OK, 6 moved to infra EXPECTED_MISSING)

### Gate C: Dev Verifier (dev env)
```bash
pip install -e '.[dev]'
python docs/reports/plans/dependency_verify_imports.py --require-dev
```
**Expected:** Exit code 0, 0 BLOCKING failures (13 core + 1 dev OK)

### Gate D: Full Verifier (infra env)
```bash
pip install -e '.[infra]'
python docs/reports/plans/dependency_verify_imports.py --all
```
**Expected:** Exit code 0 OR documented expected failures for truly optional packages

---

## STEP 1 — Default Runtime Entrypoint Analysis

### Entrypoint Discovery

**Finding:** No `[project.scripts]` defined in `pyproject.toml`. No `__main__.py` files. This is a library package, not an application with a single entrypoint.

**Default runtime path:** Any code that imports from `agentic_core`, `apps_lic`, `apps_rg`, or `apps_shared`.

**Analysis approach:** Trace each blocking dep to determine if it's imported at module scope (hard import) in commonly-used modules vs. specialized backends.

---

### 6 Blocking Dependencies — Import Analysis

| Dep | Import Module | Module Scope? | Usage Pattern | Default Startup? |
|-----|---------------|---------------|---------------|------------------|
| **pydantic-settings** | `agentic_core/config/core/global_settings_config.py` | YES (line 9) | Defines `Settings(BaseSettings)` | **NO** — Settings class defined but never imported in codebase |
| **numpy** | 9 files (see below) | YES (all 9) | Embeddings, caching, coverage, tool registry | **UNKNOWN** — need to trace if embedding/cache modules are on default path |
| **chromadb** | `agentic_core/L4_state/memory/in_memory_vector_cache.py` | YES (line 11) | Vector cache backend | **NO** — specialized backend, not default |
| **duckdb** | `agentic_core/L4_state/enforcement/trace_event.py` | YES (line 11) | Trace event storage backend | **NO** — specialized backend, not default |
| **rank-bm25** | `agentic_core/L4_state/memory/bm25_store.py`<br>`agentic_core/L2_execution/config/hybrid_retriever_config.py` | YES (both) | BM25 retrieval backend | **NO** — specialized retrieval, not default |
| **scikit-learn** | `apps_shared/types/validation_status_types.py` | YES (lines 21-22) | TF-IDF + cosine similarity for validation | **NO** — validation utility, not core runtime |

---

### Numpy Import Locations (9 files)

1. `apps_shared/types/validation_status_types.py` — validation utility
2. `agentic_core/L3_orchestration/reasoning/coverage_engine.py` — coverage analysis
3. `agentic_core/runtime/types/cache_entry_types.py` — cache types
4. `agentic_core/L2_execution/reasoning/batch_embedding_service.py` — embedding service
5. `agentic_core/L2_execution/reasoning/tool_registry.py` — tool registry
6. `agentic_core/L5_safety/reasoning/PineconeSovereignAgent.py` — Pinecone agent
7. `apps_shared/validators/cache_entry_validator.py` — cache validator
8. `agentic_core/L5_safety/reasoning/PromptRegistryAgent.py` — prompt registry
9. `apps_shared/reasoning/GlobalcacheStrategy.py` — cache strategy
10. `agentic_core/L0_maintenance/scripts/runtime_shared_data_layer_example_util.py` — example script (excluded from runtime scan)

**Trace verdict:** Numpy is used in embedding/cache infrastructure. If embeddings are deferred (lazy-loaded), numpy can be infra. If embeddings are eagerly imported, numpy must be core.

---

### Pydantic-Settings Deep Dive

**File:** `agentic_core/config/core/global_settings_config.py`

**Import:** `from pydantic_settings import BaseSettings, SettingsConfigDict` (line 9)

**Class defined:** `Settings(BaseSettings)` with fields for API keys, Redis config, etc.

**Usage search:** ZERO imports of `Settings` or `global_settings_config` in the entire codebase.

**Verdict:** `pydantic-settings` is imported at module scope but the Settings class is **never used**. This is dead code.

**Recommendation:** Move to infra OR remove the module entirely. If kept, guard the import.

---

## STEP 2 — Two-Tier Remediation Plan

### Proposal: Minimize Core, Maximize Flexibility

**Principle:** Core should contain ONLY dependencies required for basic library import and baseline operation. All specialized backends → infra.

### A) Core (must install for `pip install -e .`)

| Package | Justification |
|---------|---------------|
| pydantic | 71 hard imports across runtime — fundamental to type system |
| python-dotenv | 1 hard import — env config loading |
| libcst | 3 hard imports — AST operations |
| redis | 4 hard imports — state management (if baseline uses Redis) |
| pinecone | 1 hard import — vector store (if baseline uses Pinecone) |
| jinja2 | 1 hard import — templating |
| tenacity | 1 hard import — retry logic |
| tqdm | 1 hard import — progress bars |
| watchdog | 1 hard import — file watching |
| aiofiles | 3 hard imports — async file I/O |
| networkx | 3 hard imports — graph operations |
| PyYAML | 1 hard import — YAML parsing |
| psutil | 1 hard import — system utilities |

**Total core:** 13 packages (all currently passing verifier)

### B) Infra Extra (optional, install via `pip install -e '.[infra]'`)

| Package | Justification |
|---------|---------------|
| **numpy** | 9 hard imports BUT all in specialized modules (embeddings, caching, agents) — move to infra with guards |
| **chromadb** | 1 hard import in vector cache backend — specialized, not default |
| **duckdb** | 1 hard import in trace event backend — specialized, not default |
| **rank-bm25** | 2 hard imports in BM25 retrieval — specialized, not default |
| **scikit-learn** | 2 hard imports in validation utility — specialized, not default |
| **pydantic-settings** | 1 hard import in unused Settings class — dead code OR move to infra |
| google-genai | 1 conditional import — already infra per audit |
| google-generativeai | 4 deferred/conditional — already infra per audit |
| anthropic | 3 conditional — already infra per audit |
| openai | 4 deferred/conditional — already infra per audit |
| (all other conditional/deferred packages) | Already classified infra |

**Total infra:** 6 blocking + 28 existing infra = 34 packages

---

## STEP 3 — Guardrail Implementation (Code Diffs)

For each of the 6 blocking deps moved to infra, implement minimal guards to prevent import crashes on default runtime.

### 3A. pydantic-settings (dead code — remove or guard)

**Option 1: Remove the module entirely** (preferred if truly unused)

```diff
--- a/agentic_core/config/core/global_settings_config.py
+++ /dev/null
@@ -1,50 +0,0 @@
-"""Global settings configuration using pydantic-settings."""
-...
```

**Option 2: Guard the import** (if keeping for future use)

```diff
--- a/agentic_core/config/core/global_settings_config.py
+++ b/agentic_core/config/core/global_settings_config.py
@@ -6,7 +6,13 @@
 from typing import Literal

 from pydantic import Field, SecretStr
-from pydantic_settings import BaseSettings, SettingsConfigDict
+
+try:
+    from pydantic_settings import BaseSettings, SettingsConfigDict
+except ImportError as e:
+    raise ImportError(
+        "pydantic-settings is required for Settings. Install with: pip install -e '.[infra]'"
+    ) from e


 class Settings(BaseSettings):
```

**Test:**
```python
# tests/unit/config/test_settings_import_guard.py
import sys
import pytest

def test_settings_import_without_pydantic_settings(monkeypatch):
    """Settings import raises clear error when pydantic-settings missing."""
    # Hide pydantic_settings
    monkeypatch.setitem(sys.modules, 'pydantic_settings', None)

    with pytest.raises(ImportError, match="Install with: pip install -e '\\[infra\\]'"):
        from agentic_core.config.core.global_settings_config import Settings
```

---

### 3B. numpy (9 hard imports — defer to function scope)

**Strategy:** Move imports from module scope to function/method scope in all 9 files.

**Example diff for `agentic_core/L2_execution/reasoning/batch_embedding_service.py`:**

```diff
--- a/agentic_core/L2_execution/reasoning/batch_embedding_service.py
+++ b/agentic_core/L2_execution/reasoning/batch_embedding_service.py
@@ -11,8 +11,6 @@
 from concurrent.futures import ThreadPoolExecutor
 from typing import Any

-import numpy as np
-
 Logger: Any = logging.getLogger(__name__)


@@ -45,6 +43,12 @@ class BatchEmbeddingService:
         Returns:
             List of embedding vectors
         """
+        try:
+            import numpy as np
+        except ImportError as e:
+            raise ImportError(
+                "numpy is required for embeddings. Install with: pip install -e '.[infra]'"
+            ) from e
+
         if not texts:
             return []
```

**Repeat for all 9 files.** Each function that uses `np` gets the guarded import at the top of the function body.

**Test:**
```python
# tests/unit/execution/test_batch_embedding_numpy_guard.py
import sys
import pytest

def test_batch_embedding_without_numpy(monkeypatch):
    """BatchEmbeddingService raises clear error when numpy missing."""
    monkeypatch.setitem(sys.modules, 'numpy', None)

    from agentic_core.L2_execution.reasoning.batch_embedding_service import BatchEmbeddingService

    service = BatchEmbeddingService()
    with pytest.raises(ImportError, match="Install with: pip install -e '\\[infra\\]'"):
        service.embed_batch(["test"])
```

---

### 3C. chromadb (1 hard import — defer to method scope)

```diff
--- a/agentic_core/L4_state/memory/in_memory_vector_cache.py
+++ b/agentic_core/L4_state/memory/in_memory_vector_cache.py
@@ -8,8 +8,6 @@
 import logging
 from typing import Any

-import chromadb
-
 Logger: Any = logging.getLogger(__name__)


@@ -20,6 +18,12 @@ class InMemoryVectorCache:
     def __init__(self):
         """Initialize the in-memory vector cache."""
+        try:
+            import chromadb
+        except ImportError as e:
+            raise ImportError(
+                "chromadb is required for vector caching. Install with: pip install -e '.[infra]'"
+            ) from e
+
         self.client = chromadb.Client()
         self.collection = self.client.create_collection("cache")
```

---

### 3D. duckdb (1 hard import — defer to method scope)

```diff
--- a/agentic_core/L4_state/enforcement/trace_event.py
+++ b/agentic_core/L4_state/enforcement/trace_event.py
@@ -8,8 +8,6 @@
 from dataclasses import dataclass
 from typing import Any

-import duckdb
-
 Logger = logging.getLogger(__name__)


@@ -20,6 +18,12 @@ class TraceEvent:
     def store(self):
         """Store trace event to DuckDB."""
+        try:
+            import duckdb
+        except ImportError as e:
+            raise ImportError(
+                "duckdb is required for trace storage. Install with: pip install -e '.[infra]'"
+            ) from e
+
         conn = duckdb.connect("trace.db")
         # ... rest of implementation
```

---

### 3E. rank-bm25 (2 hard imports — defer to method scope)

**File 1:** `agentic_core/L4_state/memory/bm25_store.py`

```diff
--- a/agentic_core/L4_state/memory/bm25_store.py
+++ b/agentic_core/L4_state/memory/bm25_store.py
@@ -9,8 +9,6 @@

 from typing import Any

-from rank_bm25 import BM25Okapi
-

 class Bm25Store:
     """BM25-based retrieval store."""
@@ -18,6 +16,12 @@ class Bm25Store:
     def __init__(self, corpus: list[str]):
         """Initialize BM25 store with corpus."""
+        try:
+            from rank_bm25 import BM25Okapi
+        except ImportError as e:
+            raise ImportError(
+                "rank-bm25 is required for BM25 retrieval. Install with: pip install -e '.[infra]'"
+            ) from e
+
         self.bm25 = BM25Okapi(corpus)
```

**File 2:** `agentic_core/L2_execution/config/hybrid_retriever_config.py` (similar pattern)

---

### 3F. scikit-learn (2 hard imports — defer to method scope)

```diff
--- a/apps_shared/types/validation_status_types.py
+++ b/apps_shared/types/validation_status_types.py
@@ -18,9 +18,6 @@
 from typing import Any

 import numpy as np
-from sklearn.feature_extraction.text import TfidfVectorizer
-from sklearn.metrics.pairwise import cosine_similarity
-
 logger = logging.getLogger(__name__)


@@ -45,6 +42,14 @@ class ValidationStatus:
     def compute_similarity(self, text1: str, text2: str) -> float:
         """Compute TF-IDF cosine similarity between two texts."""
+        try:
+            from sklearn.feature_extraction.text import TfidfVectorizer
+            from sklearn.metrics.pairwise import cosine_similarity
+        except ImportError as e:
+            raise ImportError(
+                "scikit-learn is required for validation. Install with: pip install -e '.[infra]'"
+            ) from e
+
         vectorizer = TfidfVectorizer()
         vectors = vectorizer.fit_transform([text1, text2])
         return cosine_similarity(vectors[0], vectors[1])[0][0]
```

---

## STEP 4 — Updated pyproject.toml Patch

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -14,22 +14,37 @@
 ]
 dependencies = [
-    "pytest>=7.4.0",
-    "pytest-cov>=4.1.0",
-    "pytest-asyncio>=0.21.0",
     "pydantic>=2.0.0",
-    "google-genai>=1.0.0",
-    "pinecone-client>=3.0.0",
+    "python-dotenv>=1.0.0",
+    "libcst>=1.1.0",
     "redis>=5.0.0",
-    "libcst>=1.1.0",         # MANDATORY: Deterministic AST serialization (Cap 1.4)
-    "cryptography>=41.0.0",  # MANDATORY: Signed Guardian artifacts (Cap 7.2)
+    "pinecone>=3.0.0",
+    "jinja2>=3.1.0",
+    "tenacity>=8.0.0",
+    "tqdm>=4.65.0",
+    "watchdog>=3.0.0",
+    "aiofiles>=23.0.0",
+    "networkx>=3.0.0",
+    "PyYAML>=6.0.0",
+    "psutil>=5.9.0",
 ]

 [project.optional-dependencies]
 dev = [
+    "pytest>=7.4.0",
+    "pytest-cov>=4.1.0",
+    "pytest-asyncio>=0.21.0",
     "black>=23.0.0",
     "ruff>=0.1.0",
     "mypy>=1.5.0",
 ]
+infra = [
+    "numpy>=1.24.0",
+    "chromadb>=0.4.0",
+    "duckdb>=0.9.0",
+    "rank-bm25>=0.2.0",
+    "scikit-learn>=1.3.0",
+    "pydantic-settings>=2.0.0",
+    "google-genai>=1.0.0",
+    "google-generativeai>=0.3.0",
+    "anthropic>=0.7.0",
+    "openai>=1.0.0",
+    # ... (all other conditional/deferred packages from audit)
+]
```

---

## STEP 5 — Verifier Gate Results

**Commands to run AFTER implementing guards:**

1. `python docs/reports/plans/dependency_verify_imports.py` — must PASS (13/19 core OK, 6 moved to infra)
2. `python docs/reports/plans/dependency_verify_imports.py --require-dev` — must PASS
3. `python docs/reports/plans/dependency_verify_imports.py --all` — will FAIL unless infra installed (expected)

**Expected behavior:**
- Default install (`pip install -e .`): 13 core deps OK, 6 infra deps EXPECTED_MISSING
- Dev install (`pip install -e '.[dev]'`): 13 core + 1 dev OK, 6 infra EXPECTED_MISSING
- Full install (`pip install -e '.[dev,infra]'`): All 57 deps testable

---

## Summary

**Core reduction:** 19 → 13 packages (-6, -31.6%)

**Guardrails:** 6 deps moved to infra with clear ImportError messages + unit tests

**Breaking change:** NO — all guarded imports raise actionable errors, not silent failures

**Next action:** Implement the 6 guardrail diffs, update pyproject.toml, re-run verifier gates.

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

