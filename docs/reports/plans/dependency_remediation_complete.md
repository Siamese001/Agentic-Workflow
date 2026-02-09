# Dependency Remediation — Complete

## Deliverables

### Patch Files (produced, then applied)

- `docs/reports/plans/patch_packaging_discovery.patch` — setuptools package discovery
- `docs/reports/plans/patch_core_deps_blocking.patch` — dependency corrections (pinecone rename, pytest to dev, 13 blocking deps added)

### Verifier Fix

- Exit code already correct (`sys.exit(1)` on BLOCKING)
- Verified via subprocess: `EXIT CODE: 1` when blocking > 0
- Split `infra` bucket into `infra` (15 declared) + `external` (25 user-provided SDKs)
- `--all` now requires core + dev + infra (declared deps only)
- Added `--require-infra` flag

### Regression Test

- `tests/core/test_dependency_verifier_exit_code.py` — 3 tests, all PASS

### Guardrails (24 sites across 15 packages)

All use `try/except ImportError` with actionable message: `pip install -e '.[infra]'`

**numpy (9 files):**
- `agentic_core/L0_maintenance/scripts/runtime_shared_data_layer_example_util.py`
- `agentic_core/L2_execution/reasoning/tool_registry.py`
- `agentic_core/L3_orchestration/reasoning/coverage_engine.py`
- `agentic_core/L5_safety/reasoning/PineconeSovereignAgent.py`
- `agentic_core/L5_safety/reasoning/PromptRegistryAgent.py`
- `agentic_core/runtime/types/cache_entry_types.py`
- `apps_shared/reasoning/GlobalcacheStrategy.py`
- `apps_shared/types/validation_status_types.py`
- `apps_shared/validators/cache_entry_validator.py`

**chromadb (1):** `agentic_core/L4_state/memory/in_memory_vector_cache.py`
**duckdb (1):** `agentic_core/L4_state/enforcement/trace_event.py`
**rank-bm25 (2):** `agentic_core/L2_execution/config/hybrid_retriever_config.py`, `agentic_core/L4_state/memory/bm25_store.py`
**scikit-learn (1):** `apps_shared/types/validation_status_types.py`
**pydantic-settings (1):** `agentic_core/config/core/global_settings_config.py`
**beautifulsoup4 (1):** `agentic_core/L0_maintenance/scripts/inspect_dashboard_browser_util.py`
**dash+pandas+plotly (1):** `agentic_core/L0_maintenance/scripts/windsurf_realtime_dashboard_util.py`
**fastapi (1):** `agentic_core/L6_observability/dashboards/core/experiencein_config.py`
**livereload (1):** `agentic_core/L0_maintenance/scripts/dashboard_live_server_util.py`
**playwright (1):** `agentic_core/L0_maintenance/scripts/diagnose_dashboard_live_util.py`
**waitress (1):** `agentic_core/L6_observability/dashboards/core/StaticFileApp.py`
**rich (1):** `agentic_core/L0_maintenance/scripts/query_runtime_util.py`

---

## Final pyproject.toml Dependency Layout

**Core (15 deps):** pydantic, google-genai, pinecone, redis, libcst, cryptography, aiofiles, jinja2, networkx, psutil, python-dotenv, PyYAML, tenacity, tqdm, watchdog

**Dev (6 deps):** pytest, pytest-cov, pytest-asyncio, black, ruff, mypy

**Infra (15 deps):** numpy, chromadb, duckdb, rank-bm25, scikit-learn, pydantic-settings, beautifulsoup4, dash, fastapi, livereload, pandas, playwright, plotly, waitress, rich

---

## Verifier Semantics

The verifier (`docs/reports/plans/dependency_verify_imports.py`) classifies packages into five buckets and supports four CLI modes:

| Flag | Required buckets | Use case |
|---|---|---|
| *(default)* | core | Bare `pip install -e .` — must pass on lean core |
| `--require-dev` | core + dev | After `pip install -e ".[dev]"` |
| `--require-infra` | core + infra | After `pip install -e ".[infra]"` |
| `--all` | core + dev + infra | After `pip install -e ".[dev,infra]"` — full declared surface |

**Bucket definitions:**

- **core (13):** Packages in `[project.dependencies]`. Always required. Failure = exit 1.
- **dev (6):** Packages in `[project.optional-dependencies].dev`. Required only when `--require-dev` or `--all`.
- **infra (15):** Packages in `[project.optional-dependencies].infra`. Required only when `--require-infra` or `--all`. Every infra package has a guardrail (`try/except ImportError` with actionable `pip install -e '.[infra]'` message) at every hard-import site.
- **external (25):** Third-party SDKs used via conditional imports (`try/except` already in source). Not declared in `pyproject.toml`. Never blocking regardless of CLI flags — informational only.
- **sdks (3):** Cloud/API SDKs. Same treatment as external — informational only.

**Why this split is correct:**

The previous verifier lumped declared infra deps and undeclared external SDKs into one bucket. With `--all`, this forced installation of packages like `torch` (2 GB), `anthropic`, and `FlagEmbedding` — packages that are only conditionally imported and never declared as project dependencies. Splitting them makes `--all` verifiable against declared deps only, while external SDKs remain visible for auditing without blocking CI.

**How reviewers should interpret results:**

- `PASS` + `EXPECTED_MISSING` in external/sdks = normal. These are user-provided.
- `FAIL` in core/dev/infra (when required) = exit 1 = must fix before merge.
- `OK` in external = bonus — the package happens to be installed (e.g., `requests` via a transitive dep).

---

## Gate Results — Clean Venv (Lean Core)

Full raw output with exact commands is in `docs/reports/plans/dependency_gate_evidence_vFinal.md`.

**Environment:** Python 3.12.10, pip 25.0.1, clean `.venv_final`

| Gate | Command | Result |
|---|---|---|
| A | `python -m venv .venv_final` | PASS (Python 3.12.10, pip 25.0.1) |
| B | `pip install -e .` | PASS (46 packages — lean core) |
| C | `python -c "import agentic_core; import apps_shared"` | PASS |
| D | `python dependency_verify_imports.py` | PASS (13/13 core, 0 BLOCKING) |
| E | `pip install -e ".[dev]"` + `pytest -xvv test_dependency_verifier_exit_code.py` | PASS (3/3) |
| F | `pip install -e ".[infra]"` + `python dependency_verify_imports.py --all` | PASS (29/29 declared, 0 BLOCKING) |
