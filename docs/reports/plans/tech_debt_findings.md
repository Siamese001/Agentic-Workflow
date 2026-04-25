# Repo-Wide Technical Debt Findings

**Generated**: 2026-04-24
**Scanner**: `tools/analysis/tech_debt_audit.py` (9 detection passes over 6,410 `.py` files)
**Raw data**: `docs/reports/plans/tech_debt_audit.json`
**Companion plan**: `.windsurf/plans/mixin-mro-simplification-de1850.md` (the W3 mixin work motivated this broader scan)

---

## Headline

| # | Pattern | Raw Count | Confidence | Estimated impact |
|---|---|---:|---|---|
| **P1** | Rename-compat shim files | 8 | high | Mostly resolved by mixin W3 (collapsed 2). 6 remain. |
| **P2** | `try/except ImportError: class X: pass` stubs | 66 | high | Same pattern as W3 mixin stubs, now seen across non-mixin classes too |
| **P3a** | **Truly dead imports** (file does not exist) | **663** | high | One-line typos / refactoring rot. Real bugs masked by silent fallbacks |
| P3b | Namespace-package imports (no `__init__.py`) | 4,650 | medium | Works at runtime but brittle; depends on `sys.path` fragility |
| **P4** | Duplicate file pairs (identical normalized body) | 13 | high | Pure cleanup |
| **P5** | Synthetic `_emit_*`-only files (>30% emit calls) | **589** | high | A massive auto-generated stub layer with no real implementations |
| **P6** | Zero-body classes/functions at module scope | 409 | medium | Many legit (Protocols, ABCs); needs filtering |
| **P7** | Stale `__all__` exports (declared name not present) | 121 | high | Each is a real import-time bug |
| **P8** | Empty `__init__.py` | 703 | medium | Most are legitimate package markers; suspicious are L*-deep nests |
| **P9** | Same name defined in 2–6 files | 1,209 | medium | Mostly stub fallbacks (P2 echo) + Protocol/Validator parallels |

**Eyes-on candidates**: P1, P2, P3a, P4, P5, P7 are immediately actionable.

---

## P1 — Remaining Rename-Compat Shim Files

W3 of the mixin plan deleted 2 of the 8. The remaining 6 (sample, full list in JSON):

| File | Classes | Lines | Likely target |
|---|---|---:|---|
| `agentic_core/utils/decorators_compat_util.py` | shim functions | small | merge into canonical `decorators_util.py` |
| `agentic_core/L5_safety/utils/healer_classification_compat.py` | wrapper | small | inline into one consumer |
| `apps_lic/utils/lic_agent_base_util.py` | "Legacy mixin - use LICAgentBase instead" | medium | trace usage of the legacy fallback class and delete |
| `apps_lic/reasoning/OutreachLearningAgent.py` | `class HealerMixin: """Legacy mixin - use LICAgentBase instead."""` | mid | same |
| `apps_lic/reasoning/OutreachValidationExecutorAgent.py` | same | mid | same |
| `apps_lic/validators/MessageDiversityValidator.py` | same | mid | same |

These are exactly the W3 pattern, scattered across `apps_lic/`. A single follow-on wave would clean all six.

---

## P2 — try/except ImportError stub pattern (the *real* "MCPHardenedMixin × 14" pattern)

66 stubs across 40 files — **outside** the mixin layer too:

| Stub class | Count | Notable Hosts |
|---|---:|---|
| `MCPOperationMixin` (renamed from `MCPHardenedMixin` in W3) | 14 | `dag_manager.py`, `placeholder_detector_agent_config.py`, `apps_lic/types/*` |
| `HealingPolicyMixin` (renamed from `HealerMixin` in W3) | 14 | same |
| `SubatomicTestingMixin` | 10 | L2/L5 reasoning files, apps_lic |
| `EmbeddingMixin` | 5 | apps_eval/exec/research/rfp/lic engines |
| `SemanticCacheMixin` | 4 | same engines |
| `RedisCacheMixin` | 1 | `EmbeddingSovereignAgent.py` |
| **non-mixin** stubs | ~18 | `_FallbackBus`, `_FallbackBusType`, `JudgeEvaluationResult`, `JudgeEvaluator`, etc. |

**Insight**: The `_FallbackBus` / `_FallbackBusType` pair in `agentic_core/L6_observability/utils/evaluation/governed_handoff.py` and the `JudgeEvaluationResult` / `JudgeEvaluator` pair in `apps_shared/types/golden_state_evaluator_types.py` show this pattern is **endemic**, not mixin-specific.

The W2 wave of the mixin plan should be **broadened** to "eliminate ImportError-fallback stubs across the codebase" — not just mixins.

---

## P3a — TRULY dead imports (file does not exist on disk)

**663 dead imports across the repo.** Each is silently masked by an outer `try/except ImportError` or by `_missing_dependency` shims, hiding real bugs.

Top 10 victims by frequency:

| # | Missing module | Hits | Likely cause |
|---|---|---:|---|
| 1 | `agentic_core.L5_safety.config.structure_blueprint` | 50 | Refactored away; canonical lives elsewhere |
| 2 | `agentic_core.L5_safety.config.structure_blueprint.ssot` | 38 | child of #1 |
| 3 | `config.feature_schemas` | 27 | Top-level `config/` reorganization |
| 4 | `ops_scripts.ci.adg_accelerator_compliance_gate` | 26 | Renamed/deleted gate |
| 5 | `agentic_core.adg.schema` | 19 | Now lives at `agentic_core.adg.contracts.schema` |
| 6 | `config.model_registry` | 18 | same as #3 |
| 7 | `agentic_core.L3_orchestration.healers.bmg_embedding_similarity` | 17 | Healer reorganization |
| 8 | `tools.change_impact_engine` | 9 | Tooling rename |
| 9 | `agentic_core.runtime.trace_context` | 7 | Moved to `runtime.utils.trace_emitter`? |
| 10 | `apps_shared.spine.base_spine_adapter` | 7 | spine/ package moved |

**Fix shape**: each entry is one of (a) deleted reference, (b) `from X import` → updated dotted path, (c) deferred to W2-style fallback removal.

---

## P3b — Namespace-package imports (4,650)

Files exist on disk but at least one intermediate folder lacks `__init__.py`. These work at runtime in Cascade's environment because `sys.path` is augmented at startup — but they're brittle. Examples:

- `tools.generate.validation.gates` (147 hits)
- `tools.generate.adg_graph_watchlist_builder` (57 hits)
- `agentic_core.L6_observability.utils.evaluation.async_eval_packet` (29 hits)
- `tools.generate.generate_full_adg` (29 hits)
- `ops_scripts.ci.adg_gates.gate_policy` (31 hits)
- `ops_scripts.ci.adg_gates.gate_base` (27 hits)

**Fix shape**: add `__init__.py` to each intermediate folder. Single PR, mechanical.

---

## P4 — Duplicate file pairs (identical normalized body)

13 hash-identical pairs. The five most operationally significant:

| Hash | Files |
|---|---|
| `b263da5883e3` | `agentic_core/interfaces/IOrchestratorProtocol.py` + `tools/archive/interfaces_dead_code_20260405/IOrchestratorProtocol.py` (archive shouldn't be importable) |
| `17217a044de8` | `agentic_core/L_CONTRACTS/healer_exceptions.py` + `agentic_core/runtime/exceptions/healer_exceptions.py` (**two canonical paths for the same exceptions**) |
| `3743018c926a` | `agentic_core/adg/analysis/EdgeConfidence.py` + `agentic_core/adg/analysis/confidence.py` (rename in flight, both kept) |
| `bb62696f696c` | `agentic_core/adg/analysis/protocol_coverage.py` + `agentic_core/adg/analysis/protocol_coverage_validator.py` (suffix `_validator` duplicate) |
| `951ecbcfeb4d` | `agentic_core/prompt_governance/security/assembly_injection_neutralizer.py` + `agentic_core/prompt_governance/security/detectors/assembly_injection_neutralizer.py` (file moved to subfolder, original not deleted) |

Plus 2 hash-buckets where 24+ different `__init__.py` files share the same boilerplate body — these are stubbed-init duplications, low-priority cleanup.

---

## P5 — Synthetic `_emit_*`-only files

**589 files** are >30% `_emit_*(...)` no-op calls. The worst offenders:

| Emit calls | Ratio | Total stmts | File |
|---:|---:|---:|---|
| 247 | high | ~ | `agentic_core/adg/contracts/schema.py` |
| 247 | high | ~ | `agentic_core/adg/contracts/schema_util.py` (same content as the one above per P4 hash check) |
| 232 | high | ~ | `agentic_core/runtime/contracts/lifecycle_trace_contract.py` |
| 230 | high | ~ | `agentic_core/L3_orchestration/reasoning/engines/rl_coordinator_orchestrator.py` |
| 221 | high | ~ | `agentic_core/L0_routing/types/guardian_contract_types.py` |
| 215 | high | ~ | `agentic_core/L_CONTRACTS/lifecycle_trace_contract.py` (P4 dup of #3) |
| 205 | high | ~ | `agentic_core/L3_orchestration/reasoning/DagEngineAgent.py` |

**Verified shape (corrected after sampling)**: the `_emit_*` functions are NOT no-ops — they write `DEBUG`-level records via Python `logging` (e.g. `_EMITS_METRIC_EVENT_LOG.debug(...)` inside `agentic_core/runtime/contracts/lifecycle_trace_contract.py`). However, **these calls live at module top level**, so they fire at import time, not when the corresponding domain event actually occurs. The semantic claim in each call (e.g. "this module emitted a `writes_through` edge") is a structural annotation about the module's identity, not a runtime trace event.

**75,645 such calls across 1,203 files.** This is debt of a different kind: misuse of the trace API for static metadata. Likely emitted by a past code-gen pass to satisfy ADG annotation requirements. Two possible cleanup paths:

1. **If the goal was static annotation**: replace the runtime calls with module-level `__adg_traces__ = ["writes_through", "authorize_and_execute", ...]` constants. Same expressiveness, ~60–70% line reduction, no debug-log noise.
2. **If the goal was real telemetry**: move the calls into the actual code paths that perform the action they claim to trace.

This is the **largest-line-count debt** in the repo (75k+ lines). It needs an architectural decision before any sweep, but the leverage is enormous.

---

## P6 — Zero-body classes/functions

409 module-scope `class X: pass` / `def f(): pass`. Many are legitimate (Protocol classes, ABC stubs). Top hosts that look suspicious:

- Various `*_types.py` files (likely intentional — sentinel types)
- Various `*Validator.py` files with empty `validate()` stubs
- Files in `apps_lic/reasoning/` with `class HealerMixin: pass`-style (overlap with P2)

Needs per-file judgment; don't bulk-delete.

---

## P7 — Stale `__all__` (121 files)

Each is a real bug: `__all__` lists names that aren't actually defined or imported in the module. `from module import *` would fail. Sample:

(extracted from the JSON; first 20)

**Fix shape**: regenerate each `__all__` from the module's actual public symbols, or remove the stale entries.

---

## P8 — Empty `__init__.py` (703)

Most are legitimate package markers. Suspicious cases (from P4 cluster):
- 24 of them share identical empty content — these are package markers with no docstring, no `__all__`, no re-export.
- The deeper L*/L*/L*/L*/`__init__.py` cases hint that some packages are over-nested.

Low-priority cleanup.

---

## P9 — Name collisions (1,209)

A name defined in 2–6 distinct files (excluding `Test*` / `_*`). Top 25 by collision count showed nearly all are echo of P2:
- `MCPOperationMixin`, `HealingPolicyMixin`, `SubatomicTestingMixin`, `EmbeddingMixin`, `SemanticCacheMixin` → already known stub-fallback pattern
- Also: validator class names (`Validator`, `Strategy`, etc.) which are intentional protocol pattern, **not** debt.

**De-duplicating P9 against P2 → ~50 unique non-mixin name collisions deserving review.**

---

## Recommended Wave Sequence (next session)

A single overarching plan called e.g. `repo-tech-debt-burndown-<hex>.md` with:

| Wave | Target | Risk | Token Estimate |
|---|---|---|---:|
| **TD-W1** | P3a — fix the 663 truly-dead imports (10 top modules account for 247 hits) | medium — touches many files but each fix is mechanical | 12000 |
| **TD-W2** | P4 — collapse the 13 duplicate file pairs (esp. the 2 `lifecycle_trace_contract.py`, the 2 `healer_exceptions.py`) | low | 4000 |
| **TD-W3** | Generalize mixin W2: eliminate all 66 try/except ImportError stubs | medium — likely surfaces real circular-import problems | 14000 |
| **TD-W4** | P3b — add missing `__init__.py` to namespace packages (4,650 hits collapse to ~50 directories) | low | 3000 |
| **TD-W5** | P5 — investigate `_emit_*` stub function bodies; if confirmed no-ops, sweep removal | high (potential 70k+ line deletion across 1,200 files) | 20000 |
| **TD-W6** | P7 — fix 121 stale `__all__` entries | low | 5000 |
| **TD-W7** | P1 — collapse remaining 6 rename shims (apps_lic-heavy) | low | 4000 |

**TD-W1, TD-W2, TD-W4, TD-W6, TD-W7** are mechanical and low-risk. **TD-W3 and TD-W5** carry the most risk but the most leverage.

---

## Caveats

1. **P3 numbers reported in the headline distinguish "missing" (663) from "namespace_pkg" (4,650).** The first run of the audit conflated these into a single 5,278 number; the refined audit splits them.
2. **P5 ratio threshold** (30% emit calls + ≥20 emit calls) is a heuristic. Verifying that `_emit_*` functions are no-ops requires reading their definitions — should be the first action of TD-W5.
3. **P9 needs de-duplication against P2** before the 1,209 number is operationally useful.
4. **No code edits were made by this scan.** Scripts: `tools/analysis/tech_debt_audit.py`, `tools/analysis/_tech_debt_report.py`, `tools/analysis/_p3_validate.py`.

---

## See Also

- Audit JSON: `docs/reports/plans/tech_debt_audit.json`
- Mixin audit (subset): `docs/reports/plans/mixin_audit.json`
- Mixin plan: `.windsurf/plans/mixin-mro-simplification-de1850.md`
