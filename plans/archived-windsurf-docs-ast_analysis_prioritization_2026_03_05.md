---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\ast_analysis_prioritization_2026_03_05.md'
original_relative_path: 'ast_analysis_prioritization_2026_03_05.md'
source_sha256: 11f4ec3c99e4c20b2d4cb528a90f588c7f1e8fce63310063c681d36fe54b6586
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# AST Analysis: Work Prioritization — 2026-03-05

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Methodology

Full AST scan of approved SSOT folders:
`agentic_core/`, `apps_lic/`, `apps_rg/`, `apps_shared/`, `system_learning/`, `tools/evidence/`, `ops_scripts/`

Scan scripts: `ops_scripts/general/ast_analysis_scan.py`, `ops_scripts/general/shim_classify_rg.py`

---

## Summary Counts

| Category | Count |
|---|---|
| Python files with Pinecone references (repo-wide) | 247 |
| Python files with Pinecone references (SSOT dirs only) | ~30 |
| Pure shims (imports + `__all__` only) | 85 |
| Shims missing `__all__` | 28 |
| Impure shims (no funcs/classes but has logic stmts: For/If/With/Try) | 35 |
| Total shim candidates in SSOT dirs | 148 |

---

## 1. Semantic Cache Layer

### Current State (AST-verified)

**Infrastructure exists — it is partially wired but not activated end-to-end.**

| File | Role | Status |
|---|---|---|
| `agentic_core/L4_state/memory/semantic_cache_manager.py` | SSOT singleton `SemanticCacheManager` — Redis L1 + in-memory BGE vector L2, thread-safe, PII sanitizer, promotion gate | **COMPLETE** |
| `agentic_core/L4_state/memory/sovereign_semantic_cache.py` | `SovereignSemanticCache(SovereignBaseAgent)` — mission-isolated Redis+Pinecone hybrid | **COMPLETE but has broken ref**: uses `mcp_authority` (undefined), `MAX_REDIS_ENTRY_SIZE`/`REDIS_CACHE_TTL` (undefined uppercase consts) |
| `agentic_core/mixins/semantic_cache_mixin.py` | Agent-level mixin: `semantic_recall`, `semantic_learn`, `semantic_promote` | **BROKEN**: imports `semantic_cache_manager_config` which **does not exist** anywhere in repo |
| `apps_shared/enforcement/GlobalcacheStrategy.py` | Standalone L1 LRU + L2 numpy cosine cache for RG/LIC engines | **COMPLETE** — 655 lines, fully functional, but isolated from `SemanticCacheManager` SSOT |
| `data/processed/semantic_cache/` | On-disk cache directory | Present |

### Gap Analysis

1. **`semantic_cache_mixin.py` is broken** — lazy-loads from `agentic_core.L4_state.memory.semantic_cache_manager_config` (file does not exist). Correct import is `agentic_core.L4_state.memory.semantic_cache_manager`. Zero agents actually inherit `SemanticCacheMixin` in production code.

2. **`GlobalcacheStrategy.py` is a parallel implementation** — fully functional but not wired to the SSOT `SemanticCacheManager`. Agents using it bypass the canonical singleton.

3. **`sovereign_semantic_cache.py` has 2 undefined references** — `mcp_authority` (line 50) and uppercase constant names `MAX_REDIS_ENTRY_SIZE` / `REDIS_CACHE_TTL` that shadow the lowercase module-level vars.

4. **No agent currently activates the mixin** — `SemanticCacheMixin` has zero real consumers in `apps_lic`, `apps_rg`, `apps_shared`, `agentic_core` production code.

5. **LLM call sites that are semantic cache candidates**: 261 files across SSOT dirs have `.encode()` / embedding calls. Key hot paths: `system_learning/pipelines/meta_learning_pipeline.py` (12+ encode calls), `system_learning/engines/` (80+ files), `apps_shared/enforcement/GlobalcacheStrategy.py`.

### Prioritization: **HIGH VALUE / LOW EFFORT**

The infrastructure is ~85% built. The blocking items are small fixes:

| Phase | Action | Effort | Value |
|---|---|---|---|
| S1 | Fix broken import in `semantic_cache_mixin.py`: `semantic_cache_manager_config` → `semantic_cache_manager` | 1 line | Unblocks entire mixin |
| S2 | Fix `sovereign_semantic_cache.py`: define/import `mcp_authority`, normalize const names | ~5 lines | Eliminates runtime crash |
| S3 | Wire `GlobalcacheStrategy.py` to delegate to `SemanticCacheManager.get_instance()` for L2 vector ops, keeping its L1 LRU intact | ~30 lines | Unifies the two implementations |
| S4 | Add `SemanticCacheMixin` to 3-5 high-frequency reasoning agents (e.g. `LicHealingOrchestrator`, `RgHealingOrchestrator`, `meta_learning_pipeline`) | ~10 lines each | Activates cache hit path |
| S5 | Add invariant test: assert `semantic_cache_manager_config` does not exist; assert `SemanticCacheMixin` import resolves | 1 test file | Prevents regression |

**Score: Value=9/10, Effort=2/10 → Ratio = 4.5 (highest)**

---

## 2. Pinecone Deprecation

### Current State (AST-verified)

**247 Python files reference Pinecone. However, the actual runtime Pinecone usage is concentrated in ~8 files.**

#### Tier 1 — Runtime Pinecone (must replace or route through MCP)

| File | Role | Lines |
|---|---|---|
| `agentic_core/L2_execution/reasoning/PineconeSovereignAgent.py` | Primary Pinecone agent — upsert/query/heal | Core |
| `agentic_core/L4_state/memory/sovereign_semantic_cache.py` | Uses `pinecone_agent` parameter + Pinecone index | ~141 lines |
| `agentic_core/L4_state/memory/semantic_cache_manager.py` | `promote_to_long_term()` docstring says Pinecone but body uses `_vector_store` (in-memory) — **already migrated away** | Nominal only |
| `agentic_core/mixins/meta_learning_client_mixin.py` | References `_initialize_pinecone` | Mixin |
| `agentic_core/utils/meta_learning_storage_util.py` | "SemanticCacheManager (Pinecone)" comment | Comment only |
| `ops_scripts/dev_tools/l0_scripts/pinecone_assistant_util.py` | Dev script for Pinecone population | Deprecated tooling |
| `tests/support/l2_execution/SovereignPineconeMcpClientAgent.py` | 44-hit support file — MCP client shim | Test support |
| `tests/support/l1_cognition/RgReflectionAgent.py` | References Pinecone for long-term memory | Test support |

#### Tier 2 — Test references (assert Pinecone names, test integration, env vars)

~80 test files reference `PineconeSovereignAgent`, `PineconeVectorMixin`, `PINECONE_API_KEY`, `pinecone_upsert` as tool names. These are **governance tests that enforce Pinecone still exists** — they will need updating post-deprecation.

#### Tier 3 — Nominal / docstring / string literal (~160 files)

Config attribute paths (`PINECONE_API_KEY`), dashboard JSON keys, architecture docs, comments — no runtime impact.

### Key Finding

`SemanticCacheManager.promote_to_long_term()` already uses `_vector_store` (in-memory BGE). The Pinecone reference in the docstring is stale. The actual L2 store is already Pinecone-free. **The real Pinecone dependency is in `PineconeSovereignAgent` + `sovereign_semantic_cache.py` only.**

### Deprecation Path

| Phase | Action | Effort | Blockers |
|---|---|---|---|
| P1 | Audit `PineconeSovereignAgent` — identify which callers actually invoke it at runtime vs which are test/governance references | Low | None |
| P2 | Replace `sovereign_semantic_cache.py` Pinecone parameter with `_vector_store` from `SemanticCacheManager` | Medium | S3 (semantic cache unification must come first) |
| P3 | Delete/archive `ops_scripts/dev_tools/l0_scripts/pinecone_assistant_util.py` + `pinecone_populator.py` | Low | None |
| P4 | Update Tier 2 tests: replace `PineconeSovereignAgent` references with new L4 vector store agent name | High (80+ files) | P1, P2 must be complete |
| P5 | Remove `PINECONE_API_KEY` from environment config | Low | P4 complete |

**Score: Value=7/10, Effort=7/10 → Ratio = 1.0 (lowest — depends on S3 from semantic cache)**

**Dependency**: Pinecone deprecation is BLOCKED on semantic cache unification (work item 1, phase S3).

---

## 3. Shim Classification

### Current State (AST-verified, SSOT dirs only)

Total shim candidates: **148** across SSOT dirs.

#### Category A — Pure Shims (intentional re-exports): 85 files

These are **correct by design** per §26 constitutional rule. They have:
- Only `import`/`from X import Y` statements
- Exactly one `__all__` assignment
- Optional docstring

**Key clusters:**

| Directory | Count | Pattern |
|---|---|---|
| `apps_rg/reasoning/` | 7 | All re-export from `apps_rg.engines.RGValidationExecutor` or `RGStrategyExecutor` — agent class shims |
| `system_learning/*/` `__init__.py` | 6+ | Re-export from sibling `engine.py` / `types.py` |
| `apps_shared/config/__init__.py`, `apps_shared/scripts/__init__.py`, etc. | 4 | Package-level re-exports |
| `agentic_core/L5_safety/config/structure_blueprint/territories.py` | 1 | Re-exports `build_sovereign_territories` + constants |
| `apps_lic/utils/mixins_util.py` | 1 | Re-exports `CoreMixins` |
| `apps_rg/utils/rg_core_mixins_util.py` | 1 | Re-exports 4 mixin classes |

**Verdict: Leave as-is. These are intentional. §26 compliant.**

#### Category B — Shims Missing `__all__`: 28 files

These import from other modules but have no `__all__`. Violation of §26 which requires exactly one `__all__`.

**High-priority examples:**

| File | Imports | Issue |
|---|---|---|
| `agentic_core/L0_routing/enforcement/boot_sequence_enforcer.py` | `from boot_sequence import *` | Star import + no `__all__`, ambiguous |
| `agentic_core/L1_cognition/utils/execution_util.py` | `from execution_types import *` | Star import, no `__all__` |
| `agentic_core/prompt_governance/core/__init__.py` | 3x star imports from non-qualified modules | Unclear what is exported |
| `agentic_core/runtime/config/__init__.py` | `from shared_infrastructure_config import *` | Star import |
| `agentic_core/runtime/types/__init__.py` | 4x star imports | No `__all__` |
| `agentic_core/L1_cognition/utils/consensus_util.py` | `from supreme_court import *` | Non-existent module name |
| `agentic_core/L0_routing/scripts/cache_init_util.py` | `from __future__ import annotations` + stdlib only | Not a true shim — should be reclassified as script |

#### Category C — Impure Shims (no func/class but has logic): 35 files

These violate §26 structurally. They have `For`/`If`/`With`/`Try` at module level.

**Sub-categories:**

| Sub-type | Count | Examples | Verdict |
|---|---|---|---|
| `agentic_core/interfaces/*.py` — `Try` blocks only | 7 | `execution_contracts.py`, `mixins.py` — try/except import fallback | **Intentional compatibility shims** — acceptable pattern for optional imports |
| `agentic_core/L0_routing/scripts/*_util.py` — `For`/`With`/`If` | 27 | `add_subatomic_testing_to_agents_util.py` etc. | **These are scripts, not shims** — misclassified by our heuristic. They have no `def` but run imperative logic at module level |
| `agentic_core/L2_execution/determinism/__init__.py` — `If` | 1 | Conditional import based on `TYPE_CHECKING` | **Intentional** |
| `agentic_core/L2_execution/enforcement/filesystem_mcp.py` — `Try` | 1 | Optional MCP import guard | **Intentional** |

### Shim Action Plan

| Phase | Action | Effort | Value |
|---|---|---|---|
| SH1 | Add `__all__` to the 28 Category B shims — use AST to infer correct export list from what is imported | Low (~1-2 lines each) | §26 compliance |
| SH2 | Fix the 7 `agentic_core/interfaces/*.py` Try-block shims — consolidate `try/except ImportError` into a single compatibility guard per file | Low | Cleaner, still §26-compliant |
| SH3 | Reclassify the 27 `L0_routing/scripts/*_util.py` impure shims — they are scripts, not shims. Add a `main()` function and `if __name__ == '__main__': main()` guard. Then they stop being shim candidates | Medium | Correct structural classification |
| SH4 | Add AST invariant test: assert all files in `apps_rg/reasoning/`, `system_learning/*/`, `apps_shared/config/` that are pure re-exports have `__all__` | 1 test file | Prevents §26 regression |

**Score: Value=6/10, Effort=4/10 → Ratio = 1.5 (medium)**

---

## Prioritized Execution Order

```
Priority 1 (do first, unblocks everything):
  S1 — Fix semantic_cache_mixin.py import         [1 line,  immediate]
  S2 — Fix sovereign_semantic_cache.py refs        [5 lines, immediate]
  P3 — Delete pinecone_assistant_util.py + populator [safe now]

Priority 2 (high value, medium effort):
  S3 — Wire GlobalcacheStrategy to SemanticCacheManager  [30 lines]
  S4 — Add SemanticCacheMixin to 3 hot-path agents       [30 lines]
  SH1 — Add __all__ to 28 Category B shims               [28 edits]

Priority 3 (medium value, medium effort):
  S5 — Semantic cache invariant test                      [1 file]
  SH2 — Fix 7 interface Try-block shims                  [7 files]
  SH4 — AST invariant test for shim __all__               [1 file]

Priority 4 (high effort, deferred — needs P1-P3 first):
  P1 — Audit PineconeSovereignAgent runtime callers       [analysis]
  P2 — Replace sovereign_semantic_cache Pinecone param    [medium]
  SH3 — Reclassify 27 L0 scripts                         [medium]

Priority 5 (last — massive test churn):
  P4 — Update 80+ test files for Pinecone deprecation    [high effort]
  P5 — Remove PINECONE_API_KEY from env config           [low effort]
```

---

## Value/Effort Matrix

```
High Value
    |
  9 |  [S1-S4 Semantic Cache]
    |
  7 |  [P1-P3 Pinecone Tier1+Dev]
    |
  6 |  [SH1 Add __all__]
    |
  4 |  [P4 Test updates]
    |
  2 |  [SH3 Script reclassify]
    +----+----+----+----+----+----
         1    2    3    5    7    9
         Low effort          High effort
```

**Recommendation**: Start with semantic cache fixes (S1+S2) — they are 1-5 line fixes that unblock the entire L4 memory activation. Then SH1 shim `__all__` additions (pure mechanical, no logic change). Pinecone deprecation should be planned as a separate phase after semantic cache unification is complete.

---

## Files Needing Immediate Attention

| File | Issue | Fix |
|---|---|---|
| `agentic_core/mixins/semantic_cache_mixin.py:33` | Imports non-existent `semantic_cache_manager_config` | Change to `semantic_cache_manager` |
| `agentic_core/L4_state/memory/sovereign_semantic_cache.py:50` | `mcp_authority` undefined | Import or remove |
| `agentic_core/L4_state/memory/sovereign_semantic_cache.py:108-109` | `MAX_REDIS_ENTRY_SIZE`/`REDIS_CACHE_TTL` uppercase undefined | Use lowercase module vars |
| `agentic_core/L1_cognition/utils/consensus_util.py` | `from supreme_court import *` — module does not exist | Investigate/remove |
| `agentic_core/prompt_governance/core/__init__.py` | 3x star imports from unqualified names | Qualify or add `__all__` |

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

