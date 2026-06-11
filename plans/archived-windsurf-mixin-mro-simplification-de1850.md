---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\mixin-mro-simplification-de1850.md'
original_relative_path: 'mixin-mro-simplification-de1850.md'
source_sha256: 0a32209ef283df8f7d0c66a126ea09212394d39902067a56b3a7220fec5cc209
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Mixin MRO Simplification — Wave Plan

**Plan ID**: `mixin-mro-simplification-de1850`
**Status**: Active (W0 done; W1 invalidated; **W3a/W3b done 2026-04-24** — see Correction Log)
**Tier**: T3 (cross-layer, >5 files, structural)
**ADG Snapshot**: `artifacts/adg/adg_indexed_04242026_1931.sqlite`
**ADG Provenance**: `backend=sqlite, snapshot=adg_indexed_04242026_1931.sqlite` *(MCP transport closed; SQLite is canonical truth per constitutional §22)*
**Evidence Artifact**: `docs/reports/plans/mixin_audit.json`

---

## Executive Summary

Static AST + ADG audit of the entire repo found:

| Metric | Value |
|---|---|
| Mixin classes defined (post AST scan) | **117** |
| Unique mixin **names** | **~50** |
| Mixin classes that are **try/except ImportError fallback stubs** | **~62** (53%) |
| Mixin classes that are **rename backward-compat shims** | **2** (`MCPHardenedMixin` → `MCPOperationMixin`; `HealerMixin` → `HealingPolicyMixin`) |
| Mixins **defined but never subclassed** (dead code) | **18** |
| Multi-member naming clusters (likely overlap) | **7** |
| Deepest MRO consumer | `SovereignBaseAgent` — **11 mixin bases** + transitive **9** via `InfrastructureMixin` ≈ effective **~20** |
| Mixin-as-aggregator antipattern (mixin whose bases are all mixins) | **`InfrastructureMixin`** (9 bases), **`L2SelfTestingMixin`** (2) |

**Headline**: ~62 of the 117 "mixin classes" are not real classes — they're either (a) defensive `try/except ImportError` fallback `pass` stubs in consumer files, or (b) rename-redirect shims. The actual unique mixin surface is **~50**, of which **~36% are unused**.

---

## ADG_HOTSPOT_REPORT

Hotspots ranked by `impact = subclassers × (1 + log10(1 + body_size)) × layer_multiplier` and intersected with the 5 ADG Surfaces. Layer multipliers per `adg-canonical-invariants.md` §6 (L0/L5=2.0, L3/L4=1.75, L1/L2=1.0, L6=0.75, mixins root=1.0).

| Rank | Hotspot | Archetype | Layer | Subclassers | Body Size | Surfaces Touched | Impact | Why Dangerous |
|---:|---|---|---|---:|---:|---|---:|---|
| 1 | `MCPHardenedMixin` family (canonical + 13 stubs) | **CENTRAL_DEPENDENCY** | core_mixins → L3/L5/apps_lic | 14 | 2 (canon), 1 (stubs) | Execution, Security | ~28 | Stub copies hide real type identity → MRO ordering depends on which copy "wins" at import time |
| 2 | `HealerMixin` family (canonical + 13 stubs) | **CENTRAL_DEPENDENCY** | core_mixins → L3/L5/apps_lic | 14 | 2 (canon), 1 (stubs) | Execution, State | ~28 | Same fragmentation; rename shim adds an extra MRO node |
| 3 | `InfrastructureMixin` (9-base aggregator) | **ORCHESTRATOR** | core_mixins | 1 (used only by `SovereignBaseAgent`) | aggregator | Execution, State, Observability | ~14 | Single inheritance hop hides 9 transitive mixins; explosion of MRO without explicit declaration |
| 4 | `SubatomicTestingMixin` family (1 + 9 stubs) | **CENTRAL_DEPENDENCY** | core_mixins → L2/L5/apps_lic | 10 | 1 | Execution | ~10 | Same stub-fallback fragmentation pattern |
| 5 | `EmbeddingMixin` family (1 + 4 app stubs) | **STATE_NODE** | core_mixins → apps_eval/exec/research/rfp/lic | 5 | 1 (stubs) | State | ~5 | Five-app stub fan-out = five places to break in lockstep |
| 6 | `SemanticCacheMixin` family (1 + 4 app stubs) | **STATE_NODE** | core_mixins → apps_* | 4 | 1 (stubs) | State | ~4 | Same as 5; co-located in same engines |
| 7 | `SovereignBaseAgent` MRO chain | **ORCHESTRATOR** | base_agents | n/a (consumer) | n/a | Execution, Write, State, Security, Observability — **all 5** | architectural | 11 declared + 9 transitive = ~20-deep MRO. Every diamond crosses all 5 surfaces |
| 8 | 18 unused mixins | **dead code** | mixed | 0 | small | None | 0 | Pure attack surface inflation; e.g. `ASTEnforcementMixin`, `HealingMixin`, `HealerAgentMixin`, `ReplayGuardMixin`, `SecretsManagementMixin`, `CognitiveRecoveryMixin` |
| 9 | `Healing*` cluster: `HealingMixin` + `HealingPolicyMixin` + `HealingStrategyMixin` | **STATE_NODE** | L5_safety mixins | 0/14/1 | mixed | Execution, Security | structural | Three names for one capability; `HealerMixin` is yet a fourth alias to `HealingPolicyMixin` |
| 10 | `MetaLearning*` cluster: `MetaLearningMixin` + `MetaLearningClientMixin` | **STATE_NODE** | core_mixins | 1/1 | small | State, Observability | structural | Two near-identical names; uses are split |

---

## ADG_GRAPH_LAYER_EVIDENCE

The MCP `mv_*` materialized views are unavailable in the current snapshot's table list (the snapshot exposes only `nodes`, `edges`, `violations`, `meta`, `mv_critical_path_segments`, `t_infra_importers`, `sqlite_sequence`). Evidence is therefore drawn from the relational tables and corroborating AST passes.

1. **`edges` (relation_type='imports')** — every consumer file that defines a `try/except ImportError: class XMixin: pass` block represents a **conditional import dependency** on `agentic_core.mixins.X`. Counted: 62 such fallback blocks across 36 files. These are all **L3/L5/apps → core_mixins** edges that the import graph already represents; the fallback stubs are pure noise.
2. **`mv_critical_path_segments`** — `SovereignBaseAgent` sits on the critical path; any mixin in its 11-deep declared MRO (`InfrastructureMixin, AtomicExecutionMixin, ConfigMixin, LLMProviderMixin, EmbeddingMixin, ValidatorMixin, AuditTrailMixin, MetaLearningClientMixin, GoldenContextMixin, RuntimeSafetyMixin, ADGBehavioralMixin`) inherits that criticality.
3. **`t_infra_importers`** — `InfrastructureMixin` is imported by exactly one site (`SovereignBaseAgent`); collapsing it to explicit MRO declaration removes one indirection edge with zero loss of behavior.
4. **`nodes.resolved_path` × AST class scan** — the 18 unused mixins each have ≥1 module node but **0** subclass-edge in the AST class graph. They are orphans relative to the MRO graph.

> **Note**: When the ADG MCP transport recovers, re-run with `mv_dependency_cone_risk` and `mv_hotspot_centrality` to refine the impact ranking on Wave 2's exact deletion list. This is a refinement, not a blocker, because the AST-level evidence is canonical for **class-level** mixin topology — the ADG graph layer specializes in **module-level** flow.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| **W0** | W0.1 | Baseline + audit artifact | done | ADG SQLite snapshot present | ✅ Done | `mixin_audit.json` written; report numbers above |
| **W1** | W1.1, W1.2 | Delete the 18 unused mixins (zero subclassers) | 4000 | Each unused mixin has 0 subclass edges (verified by audit) | Todo | All 18 mixins removed; `mixin_audit.py` reruns with `unused_mixins=0`; full pytest collection clean |
| **W2** | W2.1, W2.2, W2.3 | Eliminate the 62 try/except ImportError fallback stubs | 12000 | Cross-layer imports are stable now that L0–L6 paths are canonical (per constitutional §12) | Todo | No file outside `agentic_core/mixins/` defines `class *Mixin: pass`; mixin classes only authored under canonical mixin modules; ADG `imports` edges become unconditional |
| **W3** | W3.1, W3.2 | Collapse rename shims (`MCPHardenedMixin`, `HealerMixin`) to canonical names | 6000 | grep + ADG show all 89+12 import sites can be rewritten | Todo | `mcp_hardened_mixin.py` and `healer_mixin.py` deleted; all imports point at `MCPOperationMixin`/`HealingPolicyMixin` directly |
| **W4** | W4.1, W4.2 | Merge naming clusters: `Healing*` → 1, `MetaLearning*` → 1, `Context*Mixin` → 1, `State*Mixin` → 1 | 10000 | Each cluster's members truly cover the same capability (verify per-cluster in W4.0) | Todo | One canonical name per stem; merged mixin retains union of methods; no behavior drift in tests |
| **W5** | W5.1, W5.2 | Detonate `InfrastructureMixin` aggregator — inline its 9 bases into `SovereignBaseAgent`'s explicit MRO | 6000 | `InfrastructureMixin` adds no methods of its own beyond aggregation (verify in W5.0) | Todo | `SovereignBaseAgent` declares its real bases explicitly; `infrastructure_mixin.py` deleted; MRO depth printed before/after as evidence |
| **W6** | W6.1 | Convert deepest MRO chains to composition where MRO adds no real polymorphism | 8000 | Some "mixins" are just method bags with no `super()` cooperation (verify with `super_chain_audit.py` — to author in W6.0) | Todo | At least 3 mixins converted to plain helper classes injected via `__init__`; tests still green |

**Total estimated tokens**: ~46k (within 1M-window era; sized for scope clarity, not budget).

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W0.1 | Audit baseline | `tools/analysis/mixin_audit.py`, `docs/reports/plans/mixin_audit.json` | None | 0 | ✅ Done |
| W1.1 | Tag the 18 dead mixins for deletion | All 18 paths from `mixins_unused_as_base` | Some are "just-in-case" hooks the team may want to keep | 1000 | Todo |
| W1.2 | Delete + run full tests | Same 18 files (some are partial-file deletions) | Imports of these names from elsewhere must be re-grepped to confirm zero refs | 3000 | Todo |
| W2.1 | Inventory all `try/except ImportError: class *Mixin: pass` blocks | 36 consumer files | Some fallbacks may legitimately handle optional deps (e.g. apps_exec `_optional_agentic_core.py`) | 2000 | Todo |
| W2.2 | Replace conditional imports with unconditional ones in core/L*/apps_lic | ~30 files (excludes `apps_exec/_optional_agentic_core.py` which is the documented optional path) | Possible circular imports — must run repo-wide import smoke test after each batch | 6000 | Todo |
| W2.3 | Verify ADG snapshot regen still passes; rerun audit | `tools/generate_full_adg.py` + audit | ADG SQLite write lock if MCP servers running | 4000 | Todo |
| W3.1 | Rewrite imports of `MCPHardenedMixin` → `MCPOperationMixin` (89 sites) | 89 files (per shim docstring) | Some sites may import via `from agentic_core.mixins import MCPHardenedMixin` style | 4000 | Todo |
| W3.2 | Rewrite imports of `HealerMixin` → `HealingPolicyMixin`, delete shims | 12 files + 2 shim files | Same as W3.1; downstream verification via test run | 2000 | Todo |
| W4.1 | Per-cluster diff (Healing*, MetaLearning*, Context*, State*) | 8 mixin files | Need to confirm methods don't conflict before merge | 4000 | Todo |
| W4.2 | Execute merges; rename to canonical (`HealingMixin`, `MetaLearningMixin`, `ContextMixin`, `StateMixin`) | 8 mixin files + every consumer | Risk of method-resolution conflict if mixins had same-named methods with different signatures | 6000 | Todo |
| W5.1 | Confirm `InfrastructureMixin` is purely aggregation (read its body) | 1 file | If it has methods of its own, demote to composition rather than inline | 1000 | Todo |
| W5.2 | Inline its 9 bases into `SovereignBaseAgent`; delete file | 2 files | MRO order must be preserved exactly | 5000 | Todo |
| W6.1 | Identify "method bag" mixins (no `super()` calls, no `__init_subclass__`, no class-level state) | All remaining ~30 mixins | Some method bags are intentionally mixins for reuse across unrelated agents | 4000 | Todo |
| W6.2 | Convert top 3 method bags to composition (helper class injected via `__init__`) | ~6 files | Test changes likely needed where tests instantiate via mixin | 4000 | Todo |

---

## Gap Register

| Gap | Why it matters | Resolution |
|---|---|---|
| ADG MCP transport closed during audit | Cannot use `mv_hotspot_centrality` / `mv_dependency_cone_risk` for refined ranking | Re-rank W2 deletion order once MCP recovers; AST-level evidence is sufficient for W1 (zero subclassers is unambiguous) |
| `mv_*` views beyond `mv_critical_path_segments` not in this snapshot | Deferred mixin → snapshot may have shipped without full graph layer | Force-regenerate via `python tools/generate_full_adg.py` before W2 begins |
| `apps_exec/_optional_agentic_core.py` is the documented optional-deps path | W2 must NOT touch this file | Add it to W2 exclude list |
| `MCPHardenedMixin` / `HealerMixin` shim docstrings claim "89+" / "12+" import sites | Counts may be stale | Re-grep at W3.0 entry |

---

## Risk & Rollback

- **W1**: Trivial rollback — `git revert` of 18 file deletions. Only risk: hidden re-export from `__init__.py`. Mitigation: `mixins/__init__.py` re-grep before deletion.
- **W2**: Higher risk. Removing fallback stubs makes optional imports hard. Mitigation: (a) batch by 5 files; (b) full `pytest --collect-only` after each batch; (c) keep `apps_exec/_optional_agentic_core.py` excluded.
- **W3**: Mechanical rename. Mitigation: scripted sed across 89 files, single commit, full test run.
- **W4**: Highest risk. Method-resolution conflicts can break agents silently. Mitigation: before merge, write per-cluster diff showing method signatures side-by-side.
- **W5**: Medium risk. MRO order changes can subtly alter `super()` resolution. Mitigation: print `SovereignBaseAgent.__mro__` before/after, diff must be empty for non-`InfrastructureMixin` entries.
- **W6**: Composition refactor — touches test instantiation patterns. Each conversion gated by full test pass.

---

## Verification Commands

```powershell
# After each wave:
python tools/generate_full_adg.py                    # regen snapshot
python tools/analysis/mixin_audit.py                 # rerun audit
python -m pytest tests/ -x --tb=short                # full test pass
python tools/analysis/_mixin_print.py                # human-readable diff vs prior
```

Expected metric trajectory:

| Metric | W0 baseline | After W1 | After W2 | After W3 | After W4 | After W5 | After W6 target |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mixin class defs (AST) | 117 | 99 | 55 | 53 | 49 | 48 | 45 |
| Unique mixin names | 50 | 32 | 32 | 30 | 26 | 25 | 22 |
| Unused mixins | 18 | 0 | 0 | 0 | 0 | 0 | 0 |
| Deepest MRO (declared+transitive) | 11+9 | 11+9 | 11+9 | 11+9 | 11+9 | 11 | 8 |
| Try/except ImportError stubs | 62 | 62 | 0 | 0 | 0 | 0 | 0 |

---

## Correction Log

### 2026-04-24 — W1 invalidated

The audit metric `subclassers == 0` (used as a proxy for "unused mixin") proved
**too narrow**. Per-name verification (`tools/analysis/_mixin_verify_unused.py`,
output: `docs/reports/plans/mixin_unused_verification.json`) shows that of the
18 candidates:

| Bucket | Count | Names |
|---|---:|---|
| Truly unused (0 external refs) | **0** | — |
| Test-only (delete test + def together) | 1 | `ReplayGuardMixin` |
| Imported but no class-base (composition / direct instantiation) | 2 | `AppsTracingMixin`, `StateAnalysisMixin` |
| Re-exported in `__init__.py` (audit needed) | 2 | `HealerAgentMixin`, `SafetyAnalysisMixin` |
| Other references (docs, isinstance, dynamic) | 13 | rest |

**Conclusion**: There is no zero-risk wave. Every candidate needs per-mixin review.

W1 is replaced by:

- **W1a**: Investigate the 1 test-only mixin (`ReplayGuardMixin`) and decide
  delete vs keep. Lowest risk (~500 tokens).
- **W1b**: Audit the 2 `__init__.py` re-exports (`HealerAgentMixin`,
  `SafetyAnalysisMixin`) — find their consumers and decide whether the
  re-export is load-bearing.
- **W1c** (replacing original W1.2): No bulk deletion. Each mixin requires
  per-name evaluation.

W2 (try/except ImportError stub elimination) and W3 (rename-shim collapse)
are unaffected by this correction — both were independently sourced.

### 2026-04-24 — W3 (rename-shim collapse) executed

**Scope**: rename two backward-compat shim classes to their canonical names
and delete the shim modules.

| Old name (shim) | Canonical name | Old module | Canonical module |
|---|---|---|---|
| `MCPHardenedMixin` | `MCPOperationMixin` | `agentic_core/mixins/mcp_hardened_mixin.py` | `agentic_core/mixins/mcp_operation_mixin.py` |
| `HealerMixin` | `HealingPolicyMixin` | `agentic_core/mixins/healer_mixin.py` | `agentic_core/mixins/healing_policy_mixin.py` |

**Pre-flight discoveries**:

1. The "second" `HealerMixin` (apparently defined in
   `agentic_core/L5_safety/validators/healing_mixin.py` per
   `agentic_core/interfaces/mixins.py`) **does not exist on disk**. The
   `try: from … import HealerMixin / except ImportError` path was permanently
   in the `_missing_dependency` fallback. Same observation for the
   `MetaLearningMixin` re-export, whose declared source path
   (`agentic_core/L1_cognition/reasoning/meta_learning_mixin.py`) also did
   not exist; the canonical path is `agentic_core/mixins/meta_learning_mixin.py`.
   Both bugs were silently masked by the fail-fast stub.
2. The 14 "duplicate" `class MCPHardenedMixin: pass` definitions were
   `try/except ImportError` fallback shadows in consumer files. They were
   renamed to `class MCPOperationMixin: pass` together with their `try` import
   targets so each consumer file remains internally consistent.

**Execution**:

- Mechanical rewrite via `tools/analysis/_w3_shim_rewrite.py --apply`
  (`whole-word \b` regex on names + module paths; rules legend in the script).
- 91 files changed: 20 module-path imports for `mcp_hardened_mixin`, 14 for
  `healer_mixin`, 128 class-name occurrences of `MCPHardenedMixin`, 150 of
  `HealerMixin`. Total 312 substitutions.
- Repaired `agentic_core/interfaces/mixins.py` to import from the canonical
  paths (and added a `HealerMixin = HealingPolicyMixin` alias for any
  call site we may have missed).
- Deleted 3 files: `agentic_core/mixins/mcp_hardened_mixin.py`,
  `agentic_core/mixins/healer_mixin.py`, and the now-orphan stub test
  `tests/unit/agentic_core/mixins/test_healer_mixin.py`.

**Verification**:

- All four critical modules import cleanly:
  `agentic_core.mixins.mcp_operation_mixin`,
  `agentic_core.mixins.healing_policy_mixin`,
  `agentic_core.interfaces.mixins`,
  `agentic_core.mixins`.
- `agentic_core.interfaces.mixins.HealerMixin is HealingPolicyMixin` → True
  (alias preserved).
- 7 of 8 high-fan-in consumer modules import cleanly. The 1 failure
  (`agentic_core/L3_orchestration/reasoning/engines/dag_manager.py`) is a
  **pre-existing** bug — its class declaration references
  `RedisCacheMixin` and `PineconeVectorMixin` which are never imported in
  the file. The W3 dry-run table for this file shows only `rule_1/2/3`
  matches; the missing imports are unrelated.
- `pytest --collect-only`: `tests/unit/agentic_core/` collected **6352
  tests** with 11 errors, **none** mentioning the renamed names or deleted
  modules. Sampled error: `ModuleNotFoundError: agentic_core.react_determinism`
  — pre-existing.
- `tests/unit/apps_lic + apps_shared` collected **381 tests, 0 errors, 0
  references** to the deleted shim names.

**Metric impact**:

| Metric | W0 baseline | After W3 |
|---|---:|---:|
| Mixin class defs (AST) | 117 | **115** (−2 shims) |
| Consumers (≥1 mixin base) | 59 | **57** |
| Naming clusters (multi-member) | 7 | **6** (`healer:` cluster eliminated) |
| Unused mixins | 18 | 18 (W1 still pending per-name review) |

**W2 (try/except ImportError stub elimination) and W4–W6** remain Todo.

### Revised metric definition

For future waves, "unused mixin" requires ALL of:

1. `subclassers == 0` (no class extends it)
2. No external `import X` of the name
3. No `isinstance(_, X)` / `issubclass(_, X)` reference
4. No direct `X(...)` instantiation
5. No re-export in any `__init__.py`
6. No dedicated unit test file

This is implemented in `tools/analysis/_mixin_verify_unused.py`.

---

## References

- Audit script: `tools/analysis/mixin_audit.py`
- Verification script: `tools/analysis/_mixin_verify_unused.py`
- Verification artifact: `docs/reports/plans/mixin_unused_verification.json`
- Audit JSON: `docs/reports/plans/mixin_audit.json`
- Constitutional §22 (graph-layer primary), §23 (canonical invariants): `.windsurf/rules/constitutional.md`
- ADG snapshot: `artifacts/adg/adg_indexed_04242026_1931.sqlite`
- Shim files (W3 targets): `agentic_core/mixins/mcp_hardened_mixin.py`, `agentic_core/mixins/healer_mixin.py`
