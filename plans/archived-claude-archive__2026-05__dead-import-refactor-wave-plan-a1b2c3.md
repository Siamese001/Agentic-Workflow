---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\dead-import-refactor-wave-plan-a1b2c3.md'
original_relative_path: '_archive\\2026-05\\dead-import-refactor-wave-plan-a1b2c3.md'
source_sha256: cc576106605e3f07b8459e683f3d9c8e1ad7eb92c768a01a81adfd76733667cd
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Dead Import & Structural Refactor — Full Wave Plan

Eliminate 845 dead/unused import issues and 47 root violations across 14,359 files in 19 directories using 3 top-level waves, each subdivided into micro-waves.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| Wave 1 | W1-A through W1-F | Bulk path_constants + MAX_RETRIES injection strip (~230 files) | UNRESOLVED | Single mechanical pattern; no logic change | ⬜ PENDING | 0 path_constants dead imports remain |
| Wave 2 | W2-A through W2-H | Dead `__init__.py` re-exports + stale shims + pytest/typing cleanup (~200 files) | UNRESOLVED | Re-exports confirmed zero-consumer via ADG | ⬜ PENDING | 0 dead __init__ re-exports remain |
| Wave 3 | W3-A through W3-C | Root violations: .md moves, lifecycle_trace_contract.py relocation, config/ cleanup (47 items) | UNRESOLVED | All references to moved files must be updated | ⬜ PENDING | 0 root violations remain |

**Total: UNRESOLVED tokens — token_estimator.py not found**

---

## Gap Register

**GAP-1: Token estimator unavailable**
- `agentic_core/planning/token_estimator.py` does not exist at that path
- Impact: Cannot produce token budget estimates; all budgets marked UNRESOLVED

**GAP-2: `logs/` directory not scanned**
- Logs were listed by user but tool returned no Python files in that directory
- Impact: If .py files exist in logs/, they are not in the report

**GAP-3: Root-level repo files not scanned**
- Files directly in `C:\Git\Agentic-Workflow\` root (conftest.py, pyproject.toml, etc.) not covered by the 19-directory sweep
- Impact: Any dead imports in root-level .py files are undetected

---

## Execution Plan

---

### WAVE 1 — Bulk path_constants + MAX_RETRIES Strip

**Root cause**: ~230 files had `BATCH_SIZE`, `BUFFER_SIZE`, `DEFAULT_SLEEP`, `DEFAULT_TIMEOUT`, `MAX_DEPTH`, `MAX_RETRIES`, `THRESHOLD` systematically injected from `agentic_core.L0_routing.config.path_constants` and `apps_shared.config.pipeline_constants_config` but never used.

**Strategy**: Write one automated script (`tools/fix/strip_dead_constants_imports.py`) that:
1. Reads all JSON reports to collect exact (file, line, symbol) tuples for path_constants-pattern imports
2. For each file: parses the import line, removes only the dead symbols, rewrites the file
3. If the entire import statement becomes empty after stripping, removes the whole line
4. Logs every change to `docs/reports/plans/wave1_strip_log.json`

---

#### W1-A — Strip `ops_scripts/ci/` (149 files, 149 issues)

**Scope**: All `path_constants` dead imports in `ops_scripts/ci/*.py`

**Commands**:
```bash
python tools/fix/strip_dead_constants_imports.py \
  --report docs/reports/plans/deep_analysis_ops_scripts.json \
  --subdir ops_scripts/ci \
  --symbols BATCH_SIZE,BUFFER_SIZE,DEFAULT_SLEEP,DEFAULT_TIMEOUT,MAX_DEPTH,MAX_FILES,MAX_RETRIES,THRESHOLD \
  --dry-run
```
Then remove `--dry-run` to apply.

**Acceptance**: `python tools/analysis/recursive_deep_analysis.py ops_scripts/ci artifacts/adg/adg_indexed_04062026_0952.sqlite /tmp/verify_w1a.json` shows 0 path_constants issues. `pytest tests/ -x -q` green.

---

#### W1-B — Strip `ops_scripts/dev_tools/l0_scripts/` (72 files)

**Scope**: All path_constants dead imports in `ops_scripts/dev_tools/l0_scripts/`

**Commands**:
```bash
python tools/fix/strip_dead_constants_imports.py \
  --report docs/reports/plans/deep_analysis_ops_scripts.json \
  --subdir ops_scripts/dev_tools/l0_scripts \
  --symbols BATCH_SIZE,BUFFER_SIZE,DEFAULT_SLEEP,DEFAULT_TIMEOUT,MAX_DEPTH,MAX_FILES,MAX_RETRIES,THRESHOLD \
  --dry-run
```

**Acceptance**: 0 path_constants issues in that subdir. Tests green.

---

#### W1-C — Strip `ops_scripts/general/`, `ops_scripts/root_scripts/`, `ops_scripts/security/`, `ops_scripts/review/` (~60 files)

**Scope**: Remaining ops_scripts subdirs with path_constants injection

**Commands**:
```bash
python tools/fix/strip_dead_constants_imports.py \
  --report docs/reports/plans/deep_analysis_ops_scripts.json \
  --subdir ops_scripts/general,ops_scripts/root_scripts,ops_scripts/security,ops_scripts/review \
  --symbols BATCH_SIZE,BUFFER_SIZE,DEFAULT_SLEEP,DEFAULT_TIMEOUT,MAX_DEPTH,MAX_FILES,MAX_RETRIES,THRESHOLD \
  --dry-run
```

**Acceptance**: 0 path_constants issues in those subdirs. Tests green.

---

#### W1-D — Strip `agentic_core/` path_constants injection (~50 files)

**Scope**: `agentic_core/runtime/config/`, `agentic_core/utils/workflow_engines/completeness.py`, and all other agentic_core files with the path_constants pattern

**Commands**:
```bash
python tools/fix/strip_dead_constants_imports.py \
  --report docs/reports/plans/deep_analysis_agentic_core.json \
  --subdir agentic_core \
  --symbols BATCH_SIZE,BUFFER_SIZE,DEFAULT_SLEEP,DEFAULT_TIMEOUT,MAX_DEPTH,MAX_FILES,MAX_RETRIES,THRESHOLD \
  --dry-run
```

**Acceptance**: 0 path_constants issues in agentic_core. Tests green.

---

#### W1-E — Strip `apps_shared/` + `apps_rg/` + `apps_lic/` MAX_RETRIES injection (~20 files)

**Scope**: `apps_shared/config/`, `apps_shared/utils/`, `apps_shared/types/`, `apps_rg/config/`, `apps_lic/config/` files with `MAX_RETRIES` from `pipeline_constants_config`

**Commands**:
```bash
python tools/fix/strip_dead_constants_imports.py \
  --report docs/reports/plans/deep_analysis_apps_shared.json \
  --subdir apps_shared \
  --symbols MAX_RETRIES \
  --source apps_shared.config.pipeline_constants_config \
  --dry-run

python tools/fix/strip_dead_constants_imports.py \
  --report docs/reports/plans/deep_analysis_apps_rg.json \
  --subdir apps_rg \
  --symbols MAX_RETRIES \
  --dry-run

python tools/fix/strip_dead_constants_imports.py \
  --report docs/reports/plans/deep_analysis_apps_lic.json \
  --subdir apps_lic \
  --symbols MAX_RETRIES \
  --dry-run
```

**Acceptance**: 0 MAX_RETRIES dead imports in those apps. Tests green.

---

#### W1-F — Strip `tests/` path_constants injection (3 files)

**Scope**: `tests/unit/apps_shared/enforcement/test_HardenedeventbusStrategy.py`, `test_ProvenancetrackerStrategy.py`, `tests/unit/apps_shared/reasoning/test_InfrastructureOrchestrator.py`, `tests/unit/agentic_core/runtime/config/test_model_tier_config_adg.py`

**Commands**:
```bash
python tools/fix/strip_dead_constants_imports.py \
  --report docs/reports/plans/deep_analysis_tests.json \
  --subdir tests/unit/apps_shared,tests/unit/agentic_core/runtime/config \
  --symbols DEFAULT_SLEEP,MAX_RETRIES,THRESHOLD,MAX_DEPTH \
  --dry-run
```

**Acceptance**: 0 path_constants dead imports in those test files. Full pytest green.

**Wave 1 Gate**: Run `pytest tests/ -x -q --tb=short` — must pass 100%. Then regenerate ADG: `python tools/generate_full_adg.py`.

---

### WAVE 2 — Dead Re-exports, Stale Shims, pytest/typing Cleanup

**Root cause**: ~200 files with:
- (a) `__init__.py` re-exporting symbols with zero ADG consumers
- (b) `apps_shared/reasoning/` shim files forwarding to `enforcement/` with no consumers
- (c) `pytest` imported but not called in test files
- (d) Obsolete `typing.List`, `typing.Dict`, `typing.Tuple`, `typing.Set` (Python 3.9+)
- (e) Misc genuine dead imports (`AppsQwenPromptConfig`, `AgentOutputContract`, `PolicyHashViolation`, etc.)

---

#### W2-A — `apps_eval/` dead `__init__.py` re-exports (5 files)

**Files**:
- `apps_eval/config/__init__.py` — 2 dead re-exports
- `apps_eval/integrations/__init__.py` — 2 dead re-exports
- `apps_eval/outputs/__init__.py` — 2 dead re-exports
- `apps_eval/services/__init__.py` — 9 dead re-exports
- `apps_eval/types/__init__.py` — 11 dead re-exports
- `apps_eval/validators/__init__.py` — 2 dead re-exports

**Action**: For each `__init__.py`, remove only the lines that re-export symbols confirmed zero-consumer in ADG. If the entire `__init__.py` becomes empty, replace with a single `# Package` comment.

**Acceptance**: `python tools/analysis/recursive_deep_analysis.py apps_eval ...` shows 0 dead __init__ imports. Tests green.

---

#### W2-B — `apps_exec/` dead `__init__.py` re-exports + `config/knowledge_base.py` (6 files)

**Files**:
- `apps_exec/config/__init__.py` — 2 dead
- `apps_exec/config/knowledge_base.py` — 12 unused (ExecBriefGlobalRule, ExecBriefNodeEntry, etc.)
- `apps_exec/engines/__init__.py` — 1 dead
- `apps_exec/engines/base_exec_engine.py` — 1 dead (pydantic.BaseModel)
- `apps_exec/integrations/__init__.py` — 2 dead
- `apps_exec/outputs/__init__.py` — 3 dead, `brief_renderer.py` — 1 dead
- `apps_exec/types/__init__.py` — 11 dead
- `apps_exec/reasoning/ExecOrchestrator.py` — 1 unused (AppsQwenPromptConfig)

**Acceptance**: Tests green.

---

#### W2-C — `apps_lic/` dead re-exports + mixin dead imports (5 files)

**Files**:
- `apps_lic/config/knowledge_base.py` — 12 unused
- `apps_lic/engines/__init__.py` — 9 dead
- `apps_lic/integrations/__init__.py` — 2 dead
- `apps_lic/outputs/__init__.py` — 4 dead, `campaign_renderer.py` — 1 dead
- `apps_lic/types/__init__.py` — 13 dead
- `apps_lic/utils/lic_agent_base_util.py` — 3 unused (MetaLearningMixin, SemanticCacheMixin, EmbeddingMixin)
- `apps_lic/utils/mixins_util.py` — 3 dead (HealerMixin, MCPHardenedMixin, SubatomicTestingMixin)
- `apps_lic/reasoning/GovernanceShieldAgent.py` — 1 unused

**Acceptance**: Tests green.

---

#### W2-D — `apps_research/`, `apps_rfp/` dead re-exports (4 files each, same pattern)

**Files** (same structural pattern in both):
- `config/__init__.py`, `config/knowledge_base.py`, `engines/__init__.py`
- `integrations/__init__.py`, `outputs/__init__.py`, `outputs/*_renderer.py`
- `services/__init__.py`, `types/__init__.py`
- `reasoning/*Orchestrator.py` — 1 unused AppsQwenPromptConfig each

**Acceptance**: Tests green.

---

#### W2-E — `apps_rg/` dead re-exports + mixin dead imports (5 files)

**Files**:
- `apps_rg/engines/__init__.py` — 1 dead
- `apps_rg/engines/sovereign_context.py` — 1 dead
- `apps_rg/integrations/__init__.py` — 2 dead
- `apps_rg/outputs/__init__.py` — 3 dead, `resume_renderer.py` — 1 dead
- `apps_rg/reasoning/DispatchResumeToolsAgent.py` — 2 dead (titanium_rag_pipeline)
- `apps_rg/reasoning/RgResumeOrchestrator.py` — 2 unused (AppsQwenConfig, AppsQwenPromptConfig)
- `apps_rg/types/__init__.py` — 11 dead
- `apps_rg/utils/rg_core_mixins.py` — 1 dead (MCPHardenedMixin)
- `apps_rg/utils/rg_core_mixins_util.py` — 3 dead (HealerMixin, MCPHardenedMixin, SubatomicTestingMixin)

**Acceptance**: Tests green.

---

#### W2-F — `apps_shared/` dead re-exports + stale shims (15 files)

**Stale shim files** (confirm zero consumers via ADG, then remove the dead import lines):
- `apps_shared/reasoning/bulkhead_manager.py` — 3 dead re-exports from `enforcement/`
- `apps_shared/reasoning/circuit_breaker.py` — 3 dead
- `apps_shared/reasoning/dead_letter_queue.py` — 3 dead
- `apps_shared/reasoning/event_bus_integration.py` — 7 unused
- `apps_shared/reasoning/core/event_bus.py` — 4 dead
- `apps_shared/reasoning/core/provenance_tracker.py` — 7 dead

**Dead re-exports in __init__.py files**:
- `apps_shared/config/__init__.py` — 10 dead
- `apps_shared/data_adapters/__init__.py` — 2 dead
- `apps_shared/scripts/__init__.py` — 6 dead
- `apps_shared/services/__init__.py` — 3 dead
- `apps_shared/types/__init__.py` — 1 dead
- `apps_shared/validators/__init__.py` — 7 dead

**Misc unused**:
- `apps_shared/scripts/fix_all_indentation_errors.py` — 3 unused (fix_all_indentation, fix_all_files, main)
- `apps_shared/scripts/meta_learning_bridge.py` — 3 dead
- `apps_shared/scripts/meta_learning_operator.py` — 2 dead
- `apps_shared/enforcement/FewshotregistryStrategy.py` — 1 unused
- `apps_shared/mixins/apps_tracing_mixin.py` — 1 unused (TracingMixin)
- `apps_shared/types/hardened_gemini_executor_types.py` — 1 unused (SourceDocument)
- `apps_shared/utils/late_interaction_reranker_util.py` — 1 unused (torch)
- `apps_shared/utils/vllm_advanced_features.py` — 3 unused (AppsQwenInferenceWorker, AppsQwenModelConfig, AppsQwenPromptConfig)
- `apps_shared/utils/vllm_shared_utils.py` — 1 unused (AppsQwenPromptConfig)
- `apps_shared/validators/resume_prompts_validator.py` — 4 unused

**Acceptance**: Tests green. ADG confirms no new violations.

---

#### W2-G — `agentic_core/` genuine dead imports (~80 files)

**Scope**: All agentic_core files with non-path_constants dead/unused imports:
- `utils/workflow_engines/apps_engines_aliases.py` — 14 unused aliases
- `utils/workflow_engines/sealed_interface_check_enforcer.py` — 3 dead (self-import via L5_safety shim)
- `seams/contracts/` — 2 files, dead re-exports
- `utils/` — 12 files with dead/unused imports (details from deep_analysis_agentic_core.json)
- `L5_safety/`, `L4_state/`, `L3_orchestration/`, `L2_execution/`, `L1_cognition/`, `L0_routing/` — spread across layers

**Process**: Read `deep_analysis_agentic_core.json`, iterate all files with issues that are NOT path_constants-pattern, apply targeted removals.

**Acceptance**: `recursive_deep_analysis.py agentic_core ...` shows 0 non-path_constants issues. Tests green.

---

#### W2-H — `tools/` + `infrastructure/` + `system_learning/` genuine dead imports (60 files)

**Scope**:
- `tools/adg/` — 9 files (FileMatch, Node, Any, os, re, subprocess)
- `tools/fix/` — 14 files (ast, os, re, sys, subprocess, gzip, shutil)
- `tools/mcp/` — 4 files (CallToolRequest, ListToolsRequest, HTTPAdapter, Retry, np)
- `tools/testing/` — 3 files (sqlite3, statistics, time, trace, sns, px)
- `tools/waves/` — 4 files (re unused)
- `tools/analysis/`, `tools/otel/`, `tools/profiling/`, `tools/scripts/`, `tools/migrate/`, `tools/utils/` — misc
- `infrastructure/sdks_mcps/client_wrappers.py` — 9 dead (AnthropicClient, OpenAIClient, VertexClient, etc.)
- `system_learning/` — 9 files (arbitration, correlation, fingerprinting, meta_learning, ml_integration, config, engines, types)

**Acceptance**: `recursive_deep_analysis.py` on each shows 0 issues. Tests green.

**Wave 2 Gate**: Full `pytest tests/ -x -q --tb=short`. Regenerate ADG. ADG issue count must drop by ≥200.

---

#### W2-I — `tests/` genuine dead imports (40 files)

**Scope**:
- 10x `tests/unit/apps_underwriting_ai/` — remove `import pytest` (unused in each)
- `tests/integration/apps_exec/test_ptc_full_integration.py` — 45 unused (PTCContractViolation, redact_output, ToolCall, etc.)
- `tests/e2e/retrieval_layers/test_graphrag_hardened.py` — 12 unused (InMemoryChunkRegistry, ADGQueryClient, etc.)
- `tests/e2e/retrieval_layers/validate_graphrag_integration.py` — 10 unused
- `tests/governance/test_determinism_validation.py` — 1 unused (pathlib)
- `tests/governance/test_error_path_coverage.py` — 3 unused
- `tests/unit/agentic_core/L3_orchestration/inference/qwen_vllm/` — 5 test files with pytest + mock unused imports
- `tests/unit/agentic_core/L4_state/utils/memory/test_graph_knowledge_store.py` — 3 unused
- `tests/unit/agentic_core/L5_safety/` — 3 test files, misc unused
- `tests/unit/agentic_core/L6_observability/` — 2 unused
- Remaining misc test files

**Note**: Do NOT remove `import pytest` if `pytest.mark.*`, `pytest.raises`, `@pytest.fixture`, or `pytest.param` appear in the file. Verify before removing.

**Acceptance**: All tests still pass (removing unused imports from test files must not break tests). 0 pytest/typing dead imports remain.

---

### WAVE 3 — Root Violations: File Moves

**Root cause**: 47 items at wrong structural level.

---

#### W3-A — `apps_eval/`, `apps_exec/`, `apps_research/`, `apps_rfp/` root .md files (32 violations, 8 each)

**Files to handle** (same pattern in each of the 4 apps):
- `README.md` — keep at root (standard practice, not a true violation)
- `PRODUCT_SPEC.md`, `CLI_SPEC.md`, `OUTPUT_CONTRACTS.md` — move to `docs/<app>/`

**Decision required**: The recursive_deep_analysis tool flagged all .md files as root violations. However:
- `README.md` is universally expected at package root → **keep**
- `PRODUCT_SPEC.md`, `CLI_SPEC.md`, `OUTPUT_CONTRACTS.md` → assess if any tool/CI script references them by path before moving

**Commands**:
```bash
# For each of apps_eval, apps_exec, apps_research, apps_rfp:
git mv apps_eval/PRODUCT_SPEC.md docs/apps_eval/PRODUCT_SPEC.md
git mv apps_eval/CLI_SPEC.md docs/apps_eval/CLI_SPEC.md
git mv apps_eval/OUTPUT_CONTRACTS.md docs/apps_eval/OUTPUT_CONTRACTS.md
# (repeat for apps_exec, apps_research, apps_rfp)
```

**Pre-condition**: `grep -r "apps_eval/PRODUCT_SPEC.md" --include="*.py" --include="*.yaml" --include="*.json" .` returns nothing.

**Acceptance**: No broken references. Tests green.

---

#### W3-B — `apps_rg/`, `apps_lic/`, `apps_underwriting_ai/` root violations (3 violations: __main__.py or SVP review files)

**Files**: `apps_rg/__main__.py` (root violation per tool — but `__main__.py` IS valid at package root), `apps_underwriting_ai/SVP_ENGINEERING_REVIEW.md`, `apps_lic/__main__.py`

**Decision**: `__main__.py` at package root is correct Python convention — **keep**. `SVP_ENGINEERING_REVIEW.md` → move to `docs/apps_underwriting_ai/`.

**Commands**:
```bash
git mv apps_underwriting_ai/SVP_ENGINEERING_REVIEW.md docs/apps_underwriting_ai/SVP_ENGINEERING_REVIEW.md
```

**Acceptance**: Tests green. No broken doc references.

---

#### W3-C — `agentic_core/runtime/lifecycle_trace_contract.py` relocation (1 file, 76KB, 113 functions)

**Decision**: Move to `agentic_core/runtime/contracts/lifecycle_trace_contract.py` (create `contracts/` subdir if not exists).

**Pre-condition**: ADG fan-in query to find all importers of `lifecycle_trace_contract`. Update all import paths.

**Commands**:
```bash
# 1. Query importers
python -c "..."  # ADG fan-in on lifecycle_trace_contract

# 2. Move file
git mv agentic_core/runtime/lifecycle_trace_contract.py \
       agentic_core/runtime/contracts/lifecycle_trace_contract.py

# 3. Update all import references (sed or custom script)
python tools/fix/update_import_paths.py \
  --old "agentic_core.runtime.lifecycle_trace_contract" \
  --new "agentic_core.runtime.contracts.lifecycle_trace_contract"
```

**Acceptance**: All importers updated. `pytest tests/ -x -q` green. ADG regenerated.

---

#### W3-D — `docs/` and `config/` root violations (5 items)

**Files**: 2 `.md` files directly at `docs/` root and 3 yaml/json files directly at `config/` root flagged by tool.

**Note**: `config/` root YAML files (excluded_paths.yaml, mcp_servers.yaml, token_budget.yaml) and `docs/` root .md files are architecturally correct at root for config and docs directories. These are **false positives** from the tool — the no-root-files rule applies to Python source packages, not config/docs directories.

**Action**: Confirm false positives, no moves needed. Update tool exclusion list for non-Python root file checks.

**Acceptance**: Document decision. No code changes needed.

---

**Wave 3 Gate**: Full `pytest tests/ -x -q --tb=short`. ADG regenerated. `python ops_scripts/ci/run_contract_gates.py` green.

---

## Pre-Execution Checklist

- [ ] `git status` clean before each wave
- [ ] ADG snapshot taken before Wave 1 starts: `python tools/generate_full_adg.py`
- [ ] Rollback point: `git stash` before each micro-wave
- [ ] Each micro-wave ends with `pytest tests/ -x -q` before proceeding to next

---

## Rollback Strategy

Each micro-wave is a separate commit. If any wave breaks tests:
1. `git revert HEAD` on the failing commit
2. Investigate the specific file via ADG fan-in to check if the import was actually used by a runtime path not captured in ADG
3. Re-apply with the problematic file excluded
4. Re-run tests

---

## Success Criteria

| Metric | Target | Verification |
|--------|--------|--------------|
| path_constants dead imports | 0 | `recursive_deep_analysis.py` all dirs |
| Total dead/unused imports | ≤ 50 (genuine optional deps excluded) | ADG query |
| Root violations | ≤ 5 (false positives excluded) | `recursive_deep_analysis.py` all dirs |
| Test suite | 100% pass | `pytest tests/ -q` |
| ADG issues after | < 100 (from 845) | ADG snapshot diff |
| CI contract gates | All green | `python ops_scripts/ci/run_contract_gates.py` |

---

## Dependency Order

```
W1-A → W1-B → W1-C → W1-D → W1-E → W1-F
  └── [Wave 1 Gate: pytest + ADG regen]
W2-A → W2-B → W2-C → W2-D → W2-E → W2-F → W2-G → W2-H → W2-I
  └── [Wave 2 Gate: pytest + ADG regen]
W3-A → W3-B → W3-C → W3-D
  └── [Wave 3 Gate: pytest + ADG regen + CI gates]
```
