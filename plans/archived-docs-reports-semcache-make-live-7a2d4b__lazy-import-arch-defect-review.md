---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\semcache-make-live-7a2d4b\\lazy-import-arch-defect-review.md'
original_relative_path: 'semcache-make-live-7a2d4b\\lazy-import-arch-defect-review.md'
source_sha256: a7edea6bf3c720bdf9d178161e66facb803f906e59a9b18eb17b2ccce0037661
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Lazy-Import Architecture Defect Review

> ⚠️ **CORRECTION 2026-04-22 (P1 wave)** — the framing below is partially wrong.
> Empirical verification (`tools/diag/_verify_fanin.py`) shows the ADG DOES
> capture lazy `ImportFrom` inside function bodies. Every module labeled
> "orphan" in this review actually has 1–10 `imports` fan-in edges. The
> scan script (`tools/diag/scan_lazy_import_gaps.py`) used a stricter
> top-level-only filter than the ADG extractor, producing artifacts.
>
> The expected-wiring assertions added in commit `3ccb8e5bf8` are still
> valuable — they assert **positive call-site presence**, which
> `v_p1_zero_caller_infra` does NOT check. But the narrative below overstates
> ADG blind spots. See RCA RC2 retraction for full empirical evidence.

- **Related RCA**: `rca-adg-ci-missed-gaps.md` (RC2 RETRACTED — lazy imports are captured)
- **Scan tool**: `tools/diag/scan_lazy_import_gaps.py` + `scan_lazy_import_gaps_summary.py` (known false-positive rate — see correction)
- **Date**: 2026-04-22
- **Question answered**: *Are other lazy imports hiding architectural defects today?*

## Executive answer (CORRECTED)

**The scan reported 188 "orphans". Most were false positives.** The ADG extractor
walks function bodies and captures lazy imports. Verified sample (9 out of 188):
every one has 1–10 `imports` fan-in edges. The review's severity tiers listed
below describe where the SCAN SCRIPT's filter disagrees with the ADG's filter,
not where the ADG is blind. Still, the expected-wiring P0 assertions are
retained because they provide a **positive** signal that complements the
ADG's **negative** (zero-caller) signal.

## Original (uncorrected) framing below — retained for audit

**Yes — the semantic cache was not unique.** 188 production modules are "lazy-only orphans" — zero top-level static callers, one or more callers via lazy imports inside function bodies. Every one of them is invisible to `adg_edge_fanin(relation_type="imports")`. Three severity tiers matter:

| Tier | Pattern | Count | Risk |
|---|---|---|---|
| **T-CRIT** | Enrolled in `_APPROVED_ADAPTER_PATHS` but lazy-only | **3** | Exact semcache bug class. Without the 2026-04-22 process-boundary exemption, `v_p1_zero_caller_infra` would either (a) emit a false positive or (b) as today, silently pass without checking. |
| **T-HIGH** | On L0 or L5 (×2.0 criticality), lazy-only | **~42** | Safety plane and routing. A structural defect here is maximum-blast, and ADG sees zero fan-in. |
| **T-MED** | L4 state/memory/storage modules, lazy-only | **11** | Same signature as semcache (persistence adapters reached only via lazy imports inside methods). |

## T-CRIT — Approved adapters with lazy-only callers

These are the direct siblings of the semcache failure. If enrolled today with no process-boundary exemption they would fail zero-caller. If NOT enrolled they could go orphan silently (the original semcache failure).

| Adapter | Lazy callers | Status |
|---|---|---|
| `agentic_core/L4_state/utils/memory/semantic_cache_manager.py` | 6 | FIXED today — enrolled + process-boundary-exempt + expected-wiring assertion |
| `agentic_core/L4_state/utils/memory/sovereign_semantic_cache.py` | 2 | FIXED today — same treatment |
| `agentic_core/embeddings/embedding_factory.py` | 1 | **NOT FIXED** — enrolled in `_APPROVED_ADAPTER_PATHS` as `agentic_core/embeddings/embedding_factory.py` but the sole caller (`EmbeddingSovereignAgent.py`) imports it lazily. If that one lazy import is removed, the adapter goes orphan and no gate flags it. |

**Recommended action**: add an `expected_wiring.yaml` row for `embedding_factory.EmbeddingFactory` being reachable from at least one L2 agent. Alternative: add to `_PROCESS_BOUNDARY_ADAPTERS` with a comment and queue `lazy_imports` edge kind (RCA §C2) as the real fix.

## T-HIGH — L0 and L5 orphans (safety/routing plane)

The safety plane (L5) and routing plane (L0) carry a ×2.0 criticality multiplier per canonical invariants §6. These are the modules whose silent orphaning would be most damaging. Spot-checks from the scan:

### L5 Safety (selected)

| Module | Lazy callers | Worst-case consequence of orphaning |
|---|---|---|
| `L5_safety/reasoning/CodeHealerAgent.py` | 6 | Auto-healing pipeline detached without detection |
| `L5_safety/reasoning/LocationHealerAgent.py` | 6 | Misplaced-file healing offline |
| `L5_safety/reasoning/ArchitectureGovernorAgent.py` | 6 | Architecture governance agent unreachable |
| `L5_safety/reasoning/CodeEnforcerAgent.py` | 4 | Code-quality enforcement offline |
| `L5_safety/enforcement/conf_calib_gate.py` | 1 (sole) | Confidence calibration gate dormant — **safety-critical** |
| `L5_safety/enforcement/d0_injection_engine_enforcer.py` | 1 (sole) | D0 injection guard dormant — **safety-critical** |
| `L5_safety/enforcement/mcp_sovereign_authority_enforcer.py` | 1 (sole) | MCP authority enforcer unreachable — **safety-critical** |
| `L5_safety/enforcement/credential_guard.py` | 1 (sole) | Credential scan enforcement dormant — **safety-critical** |
| `L5_safety/enforcement/security/injection_regression_gate.py` | 1 (sole) | Prompt-injection regression gate dormant — **safety-critical** |
| `L5_safety/reasoning/guardian_decision.py` | 1 (sole) | Guardian decision path from `execution_gateway.py` invisible to ADG |
| `L5_safety/enforcement/activation_gate.py` | 1 (sole) | Activation gate invisible to ADG |

Each of these is a single-lazy-caller fingerprint: one `from ... import` inside a function body. Remove the call, and ADG still says "everything fine." Today nothing forces one to be present at all.

### L0 Routing (selected)

| Module | Lazy callers | Consequence |
|---|---|---|
| `L0_routing/enforcement/policy_hash_enforcer.py` | 3 | Policy-hash routing guard |
| `L0_routing/reasoning/RootCustomsAgent.py` | 3 | Root customs check in routing |
| `L0_routing/utils/subprocess_runner_util.py` | 3 | Subprocess dispatch util |
| `L0_routing/reasoning/prompt_bom_builder.py` | 1 | Prompt BOM construction for L0 |
| `L0_routing/enforcement/safety_enforcement_seam.py` | 1 | Safety seam between L0 and L5 |

## T-MED — L4 state/memory orphans (semcache archetype)

The exact structural pattern that hid the semantic cache — an L4 persistence module reached only through lazy imports — recurs in at least 11 modules:

| Module | Lazy callers | Store type |
|---|---|---|
| `L4_state/utils/storage/persistent_store.py` | 7 | Generic persistent KV |
| `L4_state/utils/memory/bm25_store.py` | 5 | BM25 sparse index |
| `L4_state/utils/memory/graph_store_factory.py` | 5 | Graph store factory |
| `L4_state/utils/memory/template_registry.py` | 4 | Prompt template registry |
| `L4_state/utils/memory/prompt_version_store.py` | 2 | Prompt version store |
| `L4_state/enforcement/violation_event_store.py` | 1 (sole) | Violation event ledger |
| `L4_state/utils/memory/retrieval_eval_registry.py` | 1 (sole) | Retrieval eval registry |
| `L4_state/utils/storage/filesystem_store.py` | 1 (sole) | Filesystem-backed store |
| `L4_state/utils/memory/in_memory_vector_store.py` | 1 (sole) | In-memory vector cache |
| `L4_state/utils/memory/runtime_state_guard.py` | 1 (sole) | Runtime state invariant guard |
| `L4_state/types/detection_signal_store_types.py` | 1 (sole) | Detection signal types |

The sole-caller ones (1 lazy caller) are the most dangerous — one line away from a silent orphan.

## Why static fan-in fails here (recap from RCA)

All production code in this repo follows a **required** pattern: infrastructure-heavy imports are lazy (inside try/except inside method bodies) to keep module import cheap and to isolate optional deps. This pattern is necessary AND defeats ADG's `ImportFrom` top-level extraction. The result: layers that follow the required pattern most rigorously (L0, L5 — the ones we care about most) are the ones most invisible to the ADG fan-in view.

Cumulative scan result:
- 188 orphan targets
- 42+ at L0/L5 (×2.0 criticality)
- 11 at L4 state (same class as semcache bug)
- 3 approved adapters (T-CRIT)

## Recommendations

### Immediate (P0 — within this plan family)

1. **Enroll `embedding_factory.py` with expected-wiring assertion** (T-CRIT gap still open).
2. **Add expected-wiring assertions for the 12 single-lazy-caller L5 safety enforcers** — these are the highest-risk. One YAML row per enforcer. Cost: ~60 lines.
3. **Add expected-wiring assertions for the 11 L4 state stores** that carry persistence.

### Medium-term (P1)

4. **Implement `lazy_imports` edge kind** (RCA §C2). This eliminates the entire class of problems globally, not per-module. Extract `ast.ImportFrom` inside `FunctionDef`/`AsyncFunctionDef` bodies and emit as `relation_type="lazy_imports"`. Add a derived view `v_p1_true_orphan` = `static_callers == 0 AND lazy_callers == 0`. Once this lands, the process-boundary exemptions we added today can be removed.

### Long-term (P2)

5. **Runtime↔static delta gate** (RCA §C5). If a module is lazy-only AND has zero runtime spans in any test, it is effectively dead code. Cross-reference `otel_mcp` span sources against the static + lazy caller set.

## Bounded interpretation

This scan shows **structural blindness**, not proof of rot. A lazy-only orphan is a module whose structural reachability cannot be proven by ADG — not proof it is unreachable at runtime. Existing integration tests may still cover many of these via runtime dispatch. The point is the gate layer: today, CI has no way to distinguish "structurally reachable via required pattern" from "silently dead". Without a declaration layer (expected_wiring) or a lazy-aware edge kind (C2), any of these 188 modules can be removed/broken silently.

The semantic cache incident showed one of these failing in practice. Nothing structural prevents the next one.
