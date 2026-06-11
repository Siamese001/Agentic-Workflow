---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\RCA_four_questions_20260311.md'
original_relative_path: 'RCA_four_questions_20260311.md'
source_sha256: 6d7382288b81e0d5ca025789616a264465585b83c1f05b9f64b2f01669ae028a
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Four Questions — 2026-03-11

## ADG Evidence Basis
- **Graph:** `artifacts/adg/adg_full_20260311T100549Z.json`
- **Modules:** 3,261 | **Edges:** 51,400
- **Scan roots confirmed:** `agentic_core`, `apps_rg`, `apps_lic`, `apps_shared`, `system_learning`, `tools`, `tests`, `ops_scripts`

---

## RCA Q1 — Are the 10 agents running? Where are the 3 mandatory outputs and executive summary?

### Verdict: All 10 agents DO run. All 3 mandatory outputs exist. Executive summary has 4 structural bugs causing LOW_SIGNAL.

### The 10 agents confirmed running (coverage_ratio = 1.0, proof_complete = true):

| Agent | Territories | Type |
|-------|-------------|------|
| `FilesystemSSOTHealerAgent` | All 12 | Healer |
| `LocationHealerAgent` | All 12 | Healer |
| `HierarchyHealerAgent` | All 12 | Healer |
| `FileClassificationHealerAgent` | All 12 | Healer |
| `ArchitectureGovernorAgent` | All 12 | Validator |
| `GravityValidatorAgent` | All 12 | Validator |
| `GravityLeakHealerAgent` | All 12 | Healer |
| `RootHygieneAgent` | All 12 | Healer |
| `ObservabilityProbeExecutorAgent` | All 12 | Probe |
| `CognitiveDispositionAgent` | All 12 | Analytics |

67 total action records across 12 territories.

### 3 Mandatory output files — all present:

| File | Top-level keys |
|------|---------------|
| `logs/compliance_reports/heal_run_complete.json` | meta, coverage, routing, learning, healing_actions, blockers, **executive_summary** |
| `logs/compliance_reports/heal_run_output.json` | meta, semantic_cache, meta_learning_pipeline, healing_heatmap, meta_learning, healing_actions, routing_decisions |
| `logs/compliance_reports/failure_forensics.json` | meta, summary, failed_agents, blocked_agents, misrouted_agents |

### Why VERDICT = LOW_SIGNAL (only 2/12 gate criteria pass):

**B1 — `Healing Effectiveness Rate`: N/A (REGEX PARSE FAILURE)** ← **ROOT CAUSE**
- `HierarchyHealerAgent.fix_summary` = `"Healed 3256 of 1 hierarchy violation(s)"` — parser rejects
  because `fixed(3256) > found(1)` is detected as impossible
- **Actual bug:** `execute_ssot.py:L3752` reads `heal_result.get("violations_fixed", heal_result.get("healed", 0))`
  but `HierarchyHealerAgent.heal_repository()` returns `{"fixed": N, "violations": N}` — key is `"fixed"`, not `"violations_fixed"`
- The `@standard_heal` decorator's normalized `violations_fixed` key gets `3256` from the parent result's
  `total_actions_taken` counter (cumulative across all territories in the `HealerMixin` base class)
- **Fix applied:** `execute_ssot.py:L3752` now reads `heal_result.get("fixed", heal_result.get("violations_fixed", heal_result.get("healed", 0)))`

**B2 — `Zero-Fix Healer Penalty`: N/A** — downstream of B1, resolves when B1 is fixed

**B3 — `LLM Call Execution Rate`: VACUOUS PASS** — expected: this run had zero violations requiring LLM routing.
All 67 actions resolved deterministically. Not a bug, not actionable.

**B4 — `Meta-Learning Improvement`: N/A (NO BASELINE)** — first recorded run.
Self-resolves on run 2. Not a bug.

**Net:** 10 gates were N/A or VACUOUS. Only 2 had real data (Agent Coverage = PASS, Meta-Learning Records = PASS).
After B1 fix, `Healing Effectiveness Rate` and `Zero-Fix Healer Penalty` will evaluate on next run.

---

## RCA Q2 — Why were SovereignBaseAgent and key mixins deleted?

### Four deletion commits identified:

### Commit `bbb1b6de4` — 2026-01-18 — `"cv"` (author: Siamese001)
**340 `agentic_core/` files deleted.** This is the most damaging commit.

- **Intent:** Mass cleanup / reorganization from `L0_maintenance/` legacy scripts
- **Collateral damage:** `SovereignBaseAgent.py` and 60+ non-maintenance production files were deleted
  alongside the intended legacy maintenance artifacts
- **Critical files lost in this commit:**
  - `agentic_core/base_agents/SovereignBaseAgent.py`
  - `agentic_core/L2_execution/ToolRegistry/` (8 files)
  - `agentic_core/L3_orchestration/coordinators/recovery_coordinator.py`
  - `agentic_core/L3_orchestration/coordinators/rl_coordinator.py`
  - `agentic_core/L6_observability/api/runtime_api.py`
  - `agentic_core/infrastructure/SemanticKnowledgeClient.py`
  - `agentic_core/knowledge/rag/SovereignRAGManagerAgent.py`
  - `agentic_core/utils/mixins/subatomic_testing_mixin.py`
  - `agentic_core/config/blueprint_sovereign/` (14 manifest/config files)
- **Root cause:** No blast-radius check before `git rm`; no ADG was consulted.
  The commit message `"cv"` (two characters) indicates no review process.

### Commit `d22b10898` — 2026-03-01 — `"feat: simplify healing invocation (top 6 changes)"` (author: Siamese001)
**24 `agentic_core/` files deleted.**

- **Intent:** Remove `--legacy` gate, simplify entrypoint, add missing modules
- **Collateral damage:** Deleted production files while simplifying:
  - `agentic_core/embeddings/embedding_factory.py`
  - `agentic_core/embeddings/embedding_input_guard.py`
  - `agentic_core/embeddings/tokenization_adapter.py`
  - `agentic_core/architecture/architectural_invariants.py`
  - `agentic_core/architecture/embedding_allowlist.py`
  - `agentic_core/architecture/layer_import_allowlist.py`
  - `agentic_core/determinism/digest_authority.py`
  - `agentic_core/L5_safety/config/structure_blueprint/enforcement/` (8 files)
  - `agentic_core/__init__.py`
- **Root cause:** Files removed as "simplification" without checking import consumers in ADG.
  `embedding_factory.py` was imported by `EmbeddingSovereignAgent.py` (L2_execution).

### Commit `df4441bb8` — 2026-02-05 — `"feat: Enforce branch purity and root folder compliance"` (author: Windsurf Cascade)
**1,016 files migrated, 2 `agentic_core/` files deleted outright.**

- **Intent:** Move files from branch nodes to leaf nodes (enforce `STRUCTURAL_INVARIANT`)
- **Collateral damage:** Moved `agentic_core/L5_safety/validators/` files to `validators/core/`
  but some (`chaos_healing_integration_types.py`, `dependency_healing_integration_types.py`)
  were deleted rather than moved
- **Root cause:** The rename/move script deleted originals without verifying all consumers
  were updated to the new import path.

### Commit `de0b164db` — 2026-03-10 — `"feat(adg): merge governance_hardening branch"` (author: Siamese001)
**0 `agentic_core/` deletions** — despite being listed as the last-known commit for `atomic_execution_mixin`
and `audit_trail_mixin`. These were already deleted in an earlier commit not captured in the 4-day window.

### Pattern: **Three systemic failure modes**

1. **Mass cleanup without ADG blast-radius check** (`bbb1b6de4`) — production files caught in
   maintenance cleanup sweeps
2. **Simplification deletes without import-consumer verification** (`d22b10898`) — files removed
   as "dead" without checking who imports them
3. **Structural migration without redirect verification** (`df4441bb8`) — originals deleted before
   all callers updated to new paths

---

## RCA Q3 — All critical source files deleted in last 

### Legitimate deletions (renames/shims — callers already updated):

| Commit | File | Reason |
|--------|------|--------|
| `5272c105c` 2026-03-07 | `agentic_core/L5_safety/reasoning/FileClassificationHealerAgent.py` | Shim deleted, callers redirected |
| `5272c105c` 2026-03-07 | `agentic_core/L5_safety/reasoning/FilesystemSSOTHealerAgent.py` | Shim deleted |
| `5272c105c` 2026-03-07 | `agentic_core/L5_safety/reasoning/HierarchyHealerAgent.py` | Shim deleted |
| `5272c105c` 2026-03-07 | `agentic_core/L5_safety/reasoning/HierarchyValidatorAgent.py` | Shim deleted |
| `ce2fce74d` 2026-03-07 | `agentic_core/L5_safety/reasoning/LocationAgent.py` | Shim deleted |
| `66ce7957d` 2026-03-07 | `agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py` | Renamed |
| `66ce7957d` 2026-03-07 | `agentic_core/L5_safety/reasoning/FilesystemSSOTValidatorAgent.py` | Renamed |
| `7a23cf780` 2026-03-07 | `agentic_core/L5_safety/reasoning/LocationValidatorAgent.py` | Renamed |
| `23e7150eb` 2026-03-07 | `agentic_core/L6_observability/reasoning/ObservabilityProbeExecutorAgent.py` | Renamed |

### Accidental / incomplete deletions (callers NOT updated — currently missing from disk):

| Commit | File | Status |
|--------|------|--------|
| `421a1f377` 2026-03-08 | `agentic_core/enforcement/__init__.py` | `__init__` — low impact |
| `421a1f377` 2026-03-08 | `agentic_core/evaluation/chunking/__init__.py` | `__init__` — low impact |
| `421a1f377` 2026-03-08 | `agentic_core/evaluation/feedback/__init__.py` | `__init__` — low impact |
| `421a1f377` 2026-03-08 | `agentic_core/evaluation/monitoring/__init__.py` | `__init__` — low impact |
| `421a1f377` 2026-03-08 | `agentic_core/evaluation/runners/__init__.py` | `__init__` — low impact |
| `421a1f377` 2026-03-08 | `agentic_core/evaluation/schemas/__init__.py` | `__init__` — low impact |

All 4-day deletions outside `L5_safety/reasoning/` are either `__init__.py` stubs or test/docs files.
**No critical production source files were newly deleted in the last .**

The critical deletions (`SovereignBaseAgent`, `embedding_factory`, mixins) all pre-date the 4-day window.

---

## RCA Q4 — Are apps_* included in the ADG scan?

### Verdict: YES — apps_* are already in `_SCAN_ROOTS`. No change needed.

**`static_scanner.py:L52-61`:**
```python
_SCAN_ROOTS: tuple[str, ...] = (
    AGENTIC_CORE_DIR,      # "agentic_core"
    APPS_RG_DIR,           # "apps_rg"     ← included
    APPS_LIC_DIR,          # "apps_lic"    ← included
    APPS_SHARED_DIR,       # "apps_shared" ← included
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
    TESTS_DIR,
    OPS_SCRIPTS_DIR,
)
```

**Cross-module edge classification (`static_scanner.py:L289`):**
```python
if any(base_name.startswith(r) for r in (AGENTIC_CORE_DIR, "apps_")):
    edge_kind = "resolved_internal"
```
`apps_*` imports are classified as `resolved_internal` — full dependency tracking.

**`generate_full_adg.py` uses `ADGStaticScanner` directly** with no overrides, so it inherits
the same `_SCAN_ROOTS`. apps_* are scanned by both the lightweight `scan_result_cache.json`
path and the full `adg_full_*.json` path.

**Confirmed from last heal run:** `apps_lic`, `apps_rg`, `apps_shared` all appear in
`heal_run_complete.json` `healing_actions` with agent results — they are full scan+heal territories.

---

## Fixes Applied This Session

| Fix | File | Change |
|-----|------|--------|
| B1 fix_summary key | `execute_ssot.py:L3752` | Read `"fixed"` key first (hierarchy_healer's canonical key), falling back to `"violations_fixed"` then `"healed"` |
| Golden seal | `core_integrity golden seal` | Updated to `38a5833f...` |

## Pending Remediation (not in scope of this session)

1. **ADG-backed import sweep** — scan all files that import from paths deleted in `bbb1b6de4` and `d22b10898`
   to find remaining broken importers not yet surfaced
2. **`__init__.py` stubs** — restore 6 deleted `agentic_core/evaluation/*/` `__init__.py` files from `421a1f377`
3. **`STRUCTURAL_INVARIANT` guardrail** — add pre-commit check: any `git rm` on `agentic_core/` must
   pass an ADG blast-radius check (zero importers) before deletion is permitted

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

