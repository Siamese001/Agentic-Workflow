# Agent Deduplication — Validation Report

**Generated**: Phase 4 post-consolidation validation
**Discovery baseline**: 190 active agents
**Discovery post-consolidation**: 190 active agents (shims preserve backward compat)

---

## Phase 0–2 Summary: Analysis Pipeline

| Metric | Value |
|--------|-------|
| Agents in scope | 190 |
| Pairwise comparisons | 17,955 |
| Code similarity pairs ≥ 0.75 | 8 |
| Prompt similarity pairs ≥ 0.80 | 1 |
| Responsibility overlap pairs ≥ 0.60 | 19 |
| Composite clusters (≥ 0.70) | 7 |

### Artifacts Produced

| Artifact | Path |
|----------|------|
| Active agents index | `artifacts/dedup/active_agents_index.json` |
| Code similarity (JSON) | `artifacts/dedup/similarity/code_similarity.json` |
| Code similarity (MD) | `artifacts/dedup/similarity/code_similarity.md` |
| Prompt similarity (JSON) | `artifacts/dedup/similarity/prompt_similarity.json` |
| Prompt similarity (MD) | `artifacts/dedup/similarity/prompt_similarity.md` |
| Consolidation plan | `docs/reports/plans/dedup_consolidation_plan.md` |
| Stop-sprawl policy | `docs/reports/plans/dedup_stop_sprawl_policy.md` |
| Analysis pipeline | `artifacts/dedup/run_dedup_analysis.py` |

---

## Phase 3 Summary: Consolidations Implemented

### Cluster 6: CodeFormatterAgent + UnusedCleanupAgent (code_sim=0.771)

**Action**: SPLIT shared core into library + thin wrappers

- Created `agentic_core/L5_safety/reasoning/code_tool_runner_core.py`
  - `CodeToolRunnerMixin(SovereignBaseAgent)` provides shared `__init__`, `heal_repository` (cycle-detection + depth-limiting), and `heal` methods
- Refactored `CodeFormatterAgent` → extends `CodeToolRunnerMixin`, retains only `execute()` override (Black + Ruff)
- Refactored `UnusedCleanupAgent` → extends `CodeToolRunnerMixin`, retains only `execute()` override (autoflake)
- **Lines eliminated**: ~120 lines of duplicated boilerplate removed across both agents
- **Backward compatibility**: All existing imports, MRO, and method signatures preserved
- **Risk**: LOW — no behavioral change, only inheritance restructuring

### Cluster 7: ContentStrategyAgent → RgStrategicPlannerAgent (responsibility_overlap=1.0)

**Action**: RETIRE redundant agent with deprecation shim

- Converted `apps_rg/reasoning/ContentStrategyAgent.py` to deprecation shim
  - Emits `DeprecationWarning` on instantiation
  - Preserves `analyze_topic()` method for backward compat
  - Docstring directs to `RgStrategicPlannerAgent` as canonical replacement
- Created `apps_rg/engines/ContentStrategyAgent.py` re-export shim
  - **Fixes pre-existing broken import** in `apps_rg/engines/__init__.py`
- **Backward compatibility**: All existing imports and test assertions preserved
- **Risk**: LOW — behavior unchanged, deprecation warning added

### Clusters Not Consolidated (Deferred)

| Cluster | Members | Reason |
|---------|---------|--------|
| 1 (13 agents) | CoordinateObservabilityOperationsAgent + 12 | HIGH risk, median_sim=0.384 — RE-SCOPE needed |
| 2 (4 agents) | ATSCompatibility + Brand + Fact + Section | MEDIUM risk, different business domains |
| 3 (4 agents) | DynamicSeal + HOP6 + Historian + LicS2 | MEDIUM risk, different layers |
| 4 (3 agents) | HOP4 + HOP7 + HOP9 | LOW risk but distinct pipeline stages — candidate for shared HOP base class |
| 5 (2 agents) | CampaignBalance + Deliverability | LOW risk but different business logic — candidate for shared LIC validation base |

---

## Phase 4: Validation

### AST Parse Verification

| File | Status |
|------|--------|
| `code_tool_runner_core.py` | ✅ PASS |
| `CodeFormatterAgent.py` | ✅ PASS |
| `UnusedCleanupAgent.py` | ✅ PASS |
| `apps_rg/reasoning/ContentStrategyAgent.py` | ✅ PASS |
| `apps_rg/engines/ContentStrategyAgent.py` | ✅ PASS |

### AST Structure Verification

| Class | Base | Methods (own) |
|-------|------|---------------|
| CodeToolRunnerMixin | SovereignBaseAgent | `__init__`, `execute`, `heal_repository`, `heal` |
| CodeFormatterAgent | CodeToolRunnerMixin | `execute` |
| UnusedCleanupAgent | CodeToolRunnerMixin | `execute` |
| ContentStrategyAgent | RGAgentBase | `__post_init__`, `analyze_topic` |

### Discovery Re-run

```
Verified Active Agents: 190
Stubs/Exempt: 0
Invalid/Ghosts: 0
Compliance: All checks passed
```

### Regression Test Suite

- **File**: `tests/unit/dedup/test_consolidation_regression.py`
- **Tests**: 22 total
  - 14 for Cluster 6 (CodeToolRunnerMixin extraction)
  - 8 for Cluster 7 (ContentStrategyAgent retirement)
- **Status**: All pass or skip (skip due to missing runtime deps — same as all existing agent tests)

---

## Agent Count Table

| Category | Count |
|----------|-------|
| Pre-consolidation active agents | 190 |
| Post-consolidation active agents | 190 |
| Agents converted to shims | 1 (ContentStrategyAgent) |
| Shared core modules created | 1 (CodeToolRunnerMixin) |
| Agents refactored to use shared core | 2 (CodeFormatterAgent, UnusedCleanupAgent) |
| Broken imports fixed | 1 (apps_rg/engines/ContentStrategyAgent.py) |
| Net new files | 4 |
| Duplicated lines eliminated | ~120 |

---

## CI Gate Invocation

```bash
# Full validation pipeline
python -m agentic_core.L0_maintenance.scripts.full_agent_discovery
python artifacts/dedup/run_dedup_analysis.py
python -m pytest tests/unit/dedup/test_consolidation_regression.py -xvv
```

---

## Next Steps (Deferred Consolidations)

1. **Cluster 4 (HOP agents)**: Extract shared `HOPAgentBase` with buffer/registry plumbing → 3 agents become thin wrappers
2. **Cluster 5 (CampaignBalance + Deliverability)**: Extract shared LIC validation heal boilerplate
3. **Cluster 2 (RG compliance agents)**: Investigate shared compliance checking pattern across ATS/Brand/Fact/Section agents
4. **Cluster 1**: Requires manual review — 13 agents with low median similarity but some high outlier pairs
