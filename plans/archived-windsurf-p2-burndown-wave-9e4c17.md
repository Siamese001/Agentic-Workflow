---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\p2-burndown-wave-9e4c17.md'
original_relative_path: 'p2-burndown-wave-9e4c17.md'
source_sha256: fd60e680dcf285b1951e034a16f3ef4d78096cdaa0f170b85e70dbc3cc0b4d6f
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-21'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
> SUPERSEDED 2026-05-02 - Notion status flipped to Superseded. Burndown/backlog/followup/deferred framing retired in favor of ratcheting CI gates (where applicable) or absorption into successor plans. Daily-drift counts are stale by design and not plan-tracked. Kept on disk for archive only.

# P2 Burndown + Cross-Band Re-Severity Wave Plan

**Plan ID:** `p2-burndown-wave-9e4c17`
**Status:** DRAFT (awaiting SR_APPROVAL)
**Tier:** T3 (multi-layer, >5 files, cross-band severity changes)
**ADG Snapshot:** `adg_indexed_04212026_0433.sqlite` (node_count=76399, edge_count=552113)
**Redis hot cache:** healthy | **ADG MCP:** green | **Graph projection:** fresh, not stale

---

## ADG Provenance

```
ADG Provenance: backend=sqlite+mv_views, snapshot=adg_indexed_04212026_0433.sqlite
MV views consulted: mv_debt_concentration_hotspots, mv_hotspot_centrality,
                    mv_graph_reverse_dependency_hotspots (implied), v_p0_write_bypass_uwg,
                    v_p2_mixed_usage, v_p3_isolated_experimental
Semantic edges relied on: imports (fan-in/fan-out), antipattern (severity bands)
```

---

## 1. Baseline (current canonical burndown)

From `artifacts/adg/adg_burndown_table.json` (schema 2.2):

| Band | Net | Guardian | Gross | Classes |
|------|----:|---------:|------:|---------|
| **P0** | **55** | 1 | 56 | 1 hygiene (chokepoint_bypass) + **54 structural_conformance SC-1** |
| **P1** | **6**  | 875 | 881 | 6 hallucinated_tool_name (2 prod) |
| **P2** | **60** | 194 | 254 | see §2 |
| **P3** | **4210** | 0 | 4210 | see §5 |

Observations:
- **P0 is dominated by SC-1 structural_conformance (54)** — pre-existing structural wall, noted in prior waves (see memory entries H8/H9). Not part of antipattern burndown; must be split off.
- **P1 is near-clean** (6 net). Budget is intact.
- **P2 net 60** distributes across 46 distinct files (only 3 files carry ≥3).
- **P3 net 4210** — global_state_mutation (2793, 66%) dominates; rest is exception-handling residue.

---

## 2. P2 Net Breakdown (60 items, by kind)

| Kind | Net | Prod | Guard | Share | Archetype | ADG Surface |
|------|---:|----:|-----:|------:|-----------|-------------|
| `double_logging` | 30 | 21 | 0 | 50.0% | OBSERVABILITY | Observability |
| `default_fallback_masking` | 7 | 7 | 0 | 11.7% | STATE_NODE | State / Write |
| `broad_exception_catch` | 6 | 0 | 128 | 10.0% | varies | varies |
| `silent_exception_swallow` | 5 | 0 | 47 | 8.3% | varies | Execution |
| `log_and_swallow` | 5 | 0 | 9 | 8.3% | varies | Execution |
| `retry_without_backoff` | 4 | 4 | 0 | 6.7% | ORCHESTRATOR | Execution / Write |
| `partial_side_effects` | 2 | 2 | 0 | 3.3% | STATE_NODE | **Write** |
| `return_none_swallow` | 1 | 0 | 10 | 1.7% | varies | Execution |

Cross-referenced against **mv_debt_concentration_hotspots** and **mv_hotspot_centrality**:

| File | P2 | Layer | Fan-In | Archetype | Surfaces Hit |
|------|---:|:-----:|------:|-----------|--------------|
| `apps_lic/reasoning/OutreachLearningAgent.py` | 5 | apps | low | ORCHESTRATOR | Execution |
| `apps_rg/reasoning/RgReflectionAgent.py` | 4 | apps | low | ORCHESTRATOR | Execution |
| `system_learning/ml_integration/training_pipeline.py` | 3 | SL | low | STATE_NODE | Write/State |
| `agentic_core/L5_safety/enforcement/process_guardrail.py` | 1 | **L5** | med | **SAFETY_GATEKEEPER** | **Security** |
| `agentic_core/L5_safety/enforcement/tool_safety_contract.py` | 1 | **L5** | med | **SAFETY_GATEKEEPER** | **Security** |
| `agentic_core/L5_safety/validators/static_checks/write_gateway_enforcer.py` | 1 | **L5** | med | **SAFETY_GATEKEEPER** | **Write/Security** |
| `agentic_core/L4_state/enforcement/authority/memory_authority.py` | 1 | **L4** | med | **STATE_NODE** | **Write/State** |
| `agentic_core/L4_state/utils/versioning/commit_versioned_state_transition.py` | 1 | **L4** | med | **STATE_NODE** | **Write/State** |
| `agentic_core/L3_orchestration/reasoning/engines/sovereign_mcp_router.py` | 1 | L3 | high | ORCHESTRATOR | Execution |
| `agentic_core/L0_routing/reasoning/execution_orchestrator.py` | 1 | **L0** | high | ORCHESTRATOR | **Execution** |
| ...36 other files at 1 each |  |  |  |  |  |

**Impact-weighted ordering** (layer-multiplier × (1 + log10(1+fan_in)) × count):
L0/L5 hits outrank apps hits despite lower raw counts — the three L5 SAFETY_GATEKEEPER rows and two L4 STATE_NODE rows must lead W1.

---

## 3. Cross-Band Re-Severity Proposal (budget increase)

The user directive "increase P0/P1/P3 budget if needed" is executed as **re-classification, not ceiling dilation**. Rationale: widening a band without a rule change is drift; promoting items surfaces the real risk and then we burn them down at the correct severity.

### Proposed promotions (all require ADR entry + Author-Gate approval)

| From → To | Category | Count | Justification |
|-----------|----------|------:|---------------|
| **P2 → P1** | `partial_side_effects` | 2 | 100% prod, ADG Surface = **Write**. Doctrine §3 rule 4 (STATE_NODE). |
| **P2 → P1** | `default_fallback_masking` | 7 | 100% prod, silent state drift across L3/L4. |
| **P2 → P1** | `retry_without_backoff` (prod only) | 4 | Retry storm → outbound side-effect amplification. |
| **P3 → P2** | `global_state_mutation` on L0/L5 critical-path nodes | ~30 est. | Fan-in ≥100 on `path_constants.py` (982), `SovereignBaseAgent.py` (136), `structure_blueprint/__init__.py` (122), `static_scanner.py` (180). |
| **P3 → P2** | `broad_exception_catch` in L5 safety/validators | ~25 est. | SAFETY_GATEKEEPER surface. |
| **P3 → P1** | `silent_exception_swallow` + `log_and_swallow` in L0/L5 | ~15 est. | Constitutional §23(f) — swallowed safety/routing failures. |
| **P0 (new)** | Keep existing 1 `chokepoint_bypass` | 1 | No change. |
| **P0 (carve-out)** | SC-1 structural_conformance | 54 | **Split into separate structural_wall plan** — not an antipattern burndown target. |

### Revised post-promotion targets

| Band | Pre | After promotions | Burndown target |
|------|---:|----:|----:|
| P0 (antipattern) | 1 | 1 | 0 |
| P1 | 6 | ~34 | 0 |
| P2 | 60 | ~102 (demoted items flow in) | 0 |
| P3 | 4210 | ~4140 | ratchet lock + 30%/wave burn |

The post-promotion P2 is **larger**, not smaller — this is intentional. We burn the higher-severity items first.

---

## 4. Wave / Microwave Structure

| Wave | Phases | Focus | Est. Tokens | Status | Success Criteria |
|------|--------|-------|------------:|:------:|------------------|
| **W0** | P0a, P0b | Freeze + provenance | 8k | 🟢 | Plan approved, snapshot pinned |
| **W1** | P1a–P1e | L0/L4/L5 safety-surface P2 | 45k | 🟡 | 0 P2 remaining in L0/L4/L5 |
| **W2** | P2a–P2d | Promotions (re-severity) | 30k | 🟡 | ADR + band manifest updated, CI green |
| **W3** | P3a–P3e | `double_logging` 30 → 0 | 55k | 🟡 | 0 double_logging P2 |
| **W4** | P4a–P4d | `broad/silent/log_and_swallow/return_none` P2 → 0 | 40k | 🟡 | 0 P2 exception-handling net |
| **W5** | P5a–P5c | `partial_side_effects`, `retry_without_backoff`, `default_fallback_masking` promoted items | 35k | 🟡 | 0 P1 promoted items |
| **W6** | P6a–P6g | P3 critical-path cluster (global_state_mutation) | 90k | 🔴 | Top 10 fan-in P3 files → 0 global_state_mutation |
| **W7** | P7a–P7c | P3 long-tail ratchet + lock | 40k | 🟡 | P3 ratchet ceiling = net count, no regressions 4 weeks |
| **W8** | P8 | SC-1 structural_conformance (split plan) | N/A | ⏭️ | Forwarded to separate plan `sc1-wall-*.md` |

### Microwave detail

#### W1 — L0/L4/L5 safety-surface P2 (must lead)

| µWave | File | Kind (evidence) | Action |
|-------|------|-----------------|--------|
| W1.1 | `L5/enforcement/process_guardrail.py:327` | `try_body_side_effects=2` | Extract idempotent commit; add compensating rollback |
| W1.2 | `L5/enforcement/tool_safety_contract.py:514` | `ValueError` broad-catch | Narrow to `ValidationError, ContractError` |
| W1.3 | `L5/validators/static_checks/write_gateway_enforcer.py` | (TBD from evidence) | Narrow + emit guardian telemetry |
| W1.4 | `L5/validators/static_checks/ptc_invariants.py` | (TBD) | Same pattern |
| W1.5 | `L5/reasoning/SafetyInspectorAgent.py` | (TBD) | Same pattern |
| W1.6 | `L5/reasoning/DuplicateCodeDetectorAgent.py:426` | `for_retry` | Replace with bounded retry + backoff |
| W1.7 | `L4/enforcement/authority/memory_authority.py:349` | `ValueError` broad-catch | Narrow to `AuthorityError` |
| W1.8 | `L4/utils/versioning/commit_versioned_state_transition.py:325` | `StateVersionMissingError` — **keep** but promote swallow to raise |
| W1.9 | `L4/reasoning/CheckpointManager.py:457` | `AttributeError` — narrow to `CheckpointStateError` |
| W1.10 | `L4/utils/memory/graph_knowledge_store.py:64` | `Exception` — narrow to specific |
| W1.11 | `L4/enforcement/activation_flags.py:100` | `try_body_side_effects=2` | Wrap in atomic write |
| W1.12 | `L0/reasoning/execution_orchestrator.py:141` | `AttributeError` broad-catch | Narrow to router-specific |
| W1.13 | `L1/reasoning/semantic_retriever.py:190` | `AttributeError` | Narrow |
| **Checkpoint** | — | — | **ADG regen, confirm L0/L4/L5 P2 = 0** |

#### W2 — Cross-band promotions (ADR-gated)

| µWave | Action |
|-------|--------|
| W2.1 | Author ADR `ADR-NNN-p2-p1-reseverity-writeplane.md` listing `partial_side_effects` + `default_fallback_masking` + `retry_without_backoff` (prod) promotions |
| W2.2 | Update `agentic_core/adg/severity_bands.py` band manifest; add migration test |
| W2.3 | Update `tools/generate/validation/gates.py` P1 ratchet ceiling from current → +~13 (matches promoted count) |
| W2.4 | Regenerate ADG; confirm rebalanced counts match prediction ±2 |

#### W3 — `double_logging` 30 → 0

30 P2 rows, 21 prod. Microwave by layer:
- W3.1 L6 observability (`reasoning_streamer.py`, `enhanced_observability.py`, `analytics_dashboard.py`) — 3 files
- W3.2 L3 orchestration apps (4–6 files)
- W3.3 L2 execution (2–3 files)
- W3.4 apps_* reasoning (remaining, batch with OutreachLearningAgent cluster from §2)
- W3.5 Ratchet lock: `double_logging` ceiling = 0 in gates.py

#### W4 — Exception-handling P2 (broad/silent/log_and_swallow/return_none): 17 → 0

Grouped by file, 1–2 files per µWave, ADG regen every 5 files.

#### W5 — P1-promoted items: ~13 → 0

All items from W2 carry forward at P1 severity. Higher-rigor review, guardian exemption allowed only on Author-Gate approval.

#### W6 — P3 critical-path global_state_mutation (the big lever)

ADG centrality evidence (mv_hotspot_centrality):

| File | fan_in | Action |
|------|-------:|--------|
| `agentic_core/L0_routing/config/path_constants.py` | 982 | Convert module-level state → `@lru_cache` readers or frozen dataclass |
| `agentic_core/base_agents/SovereignBaseAgent.py` | 136 | Class-level → per-instance or context-manager scoped |
| `agentic_core/adg/extraction/static_scanner.py` | 180 | Module singleton → factory |
| `agentic_core/L5_safety/config/structure_blueprint/__init__.py` | 122 | Freeze; constitutional §7 alignment |
| `agentic_core/adg/contracts/schema_util.py` | 228 | Freeze constants |
| `agentic_core/__init__.py` | 1027 | Audit mutation sites; retain only registration hooks |
| `tools/generate/validation/gates.py` | 253 | Extract mutable parts behind accessor |
| `tools/eval/retrieval_benchmark.py` | low | Bulk — lowest risk, highest density (46 P3) |

One file per µWave. ADG regen after each.

#### W7 — P3 long-tail ratchet lock

- W7.1 Freeze `ops_scripts/dev_tools/L0_routing_scripts/_ssot_*.py` cluster (153 P3, isolated per `v_p3_isolated_experimental`). Confirm via fan-in that they are indeed zero-consumer outside ops_scripts.
- W7.2 Batch-burn tests/** (lowest risk).
- W7.3 Lock ratchet ceilings to post-wave count.

---

## 5. P3 Landscape (informational, drives W6/W7)

From burndown (net counts):

| P3 kind | Net | Prod | Surface | W6/W7 wave |
|---------|---:|----:|---------|:-:|
| `global_state_mutation` | 2793 | 769 | State | W6 |
| `broad_exception_catch` | 415 | 0 | varies | W7 (after W4) |
| `throw_for_normal_flow` | 267 | 215 | Execution | W7 |
| `log_and_swallow` | 197 | 0 | Execution | W7 |
| `silent_exception_swallow` | 180 | 0 | Execution | W7 |
| `return_none_swallow` | 108 | 0 | Execution | W7 |
| `double_logging` | 97 | 36 | Obs | W3 tail |
| `hardcoded_path` | 90 | 5 | State | W7 |
| other | 63 | — | — | W7 |

---

## 6. Phase-Level Summary

| Phase | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|-------|-------|--------------|-------------|------------:|:------:|
| P0a | Plan + snapshot pin | 1 plan | — | 4k | 🟢 |
| P0b | SR_APPROVAL gate | — | User must approve before W1 | 4k | 🟡 |
| P1a | L5 safety P2 (W1.1–W1.6) | 6 files | Guardrail surface, no regressions | 15k | 🟡 |
| P1b | L4 state P2 (W1.7–W1.11) | 5 files | Write-plane integrity | 12k | 🟡 |
| P1c | L0/L1 P2 (W1.12–W1.13) | 2 files | Fan-in 982 on path_constants | 8k | 🟡 |
| P1d | L3 engines P2 | 4 files | Orchestrator surface | 10k | 🟡 |
| P1e | W1 checkpoint + ADG regen | — | Regenerate + Redis reload | 3k | 🟢 |
| P2a | ADR authoring (re-severity) | 1 doc | — | 6k | 🟡 |
| P2b | severity_bands.py update | 2 files | Migration test | 6k | 🟡 |
| P2c | gates.py ratchet update | 1 file | — | 4k | 🟡 |
| P2d | ADG regen + verify | — | ±2 count tolerance | 4k | 🟢 |
| P3a–P3e | double_logging 30 → 0 | ~15 files | Obs fidelity | 55k | 🟡 |
| P4a–P4d | exception-handling P2 → 0 | ~17 files | Narrow catches | 40k | 🟡 |
| P5a–P5c | P1-promoted burn | ~13 files | Write-plane fixes | 35k | 🟡 |
| P6a–P6g | Critical-path P3 | 8 files | fan_in ≥100 each | 90k | 🔴 |
| P7a–P7c | P3 long-tail + lock | ~40 files | Low-risk batch | 40k | 🟡 |
| P8 | SC-1 structural wall | deferred | **Split plan** | — | ⏭️ |

---

## 7. Gate / Checkpoint Sequence

1. **After W1:** `python tools/generate_full_adg.py` → confirm L0/L4/L5 P2 = 0.
2. **After W2:** Re-severity verified; band manifest migration test passes.
3. **After each W3–W5 µwave:** py_compile + scoped pytest (owner-file tests).
4. **After W3/W4/W5:** full ADG regen + Redis reload.
5. **After W6 each file:** ADG regen + fan-in recount (did we break any imports?).
6. **After W7:** Ratchet ceilings locked; CI gate enforces no regressions.

---

## 8. Risks & Rollback

| Risk | Mitigation |
|------|------------|
| Narrowing an exception breaks a caller | ADG fan-in check before edit; scoped pytest on fan-in set |
| Global-state removal breaks singleton invariants | Keep accessor shim for 1 snapshot; delete only after zero-caller proof |
| Promotion inflates P1 ceiling past CI gate | W2.3 raises ceiling **in same commit** as W2.1 ADR |
| ADG snapshot drift mid-wave | Snapshot pinned in plan header; reload only at phase boundaries |
| SC-1 structural wall conflates with antipattern progress | Explicit split — W8 deferred to separate plan |

Rollback: each µwave is a single commit. Revert per file. Ratchet ceilings in `gates.py` are the single source of truth and block regressions.

---

## 9. ADG_HOTSPOT_REPORT (constitutional §22)

| Rank | File | Layer | fan_in | P2 | P3 | Archetype | Surfaces | Impact |
|-----:|------|:-----:|------:|---:|---:|-----------|----------|-------:|
| 1 | `agentic_core/L0_routing/config/path_constants.py` | L0 | 982 | 0 | ~10 | CENTRAL_DEPENDENCY+STATE_NODE | State, Routing | 60.0 (×2.0) |
| 2 | `agentic_core/adg/extraction/static_scanner.py` | L_TOOLS | 180 | 0 | ~8 | CENTRAL_DEPENDENCY | State | 18.4 |
| 3 | `agentic_core/base_agents/SovereignBaseAgent.py` | L_SHARED | 136 | 0 | ~7 | ORCHESTRATOR | Write, Execution | 15.4 |
| 4 | `agentic_core/L5_safety/enforcement/process_guardrail.py` | L5 | med | 1 | ? | **SAFETY_GATEKEEPER** | **Security** | 8.0 (×2.0) |
| 5 | `agentic_core/L5_safety/enforcement/tool_safety_contract.py` | L5 | med | 1 | ? | **SAFETY_GATEKEEPER** | **Security** | 8.0 (×2.0) |
| 6 | `agentic_core/L4_state/enforcement/authority/memory_authority.py` | L4 | med | 1 | ? | STATE_NODE | **Write/State** | 5.25 (×1.75) |
| 7 | `agentic_core/L4_state/utils/versioning/commit_versioned_state_transition.py` | L4 | med | 1 | ? | STATE_NODE | **Write/State** | 5.25 |
| 8 | `agentic_core/L3_orchestration/reasoning/engines/sovereign_mcp_router.py` | L3 | high | 1 | ? | ORCHESTRATOR | Execution | 4.4 (×1.75) |
| 9 | `apps_lic/reasoning/OutreachLearningAgent.py` | apps | low | 5 | ? | ORCHESTRATOR | Execution | 3.5 |
| 10 | `apps_rg/reasoning/RgReflectionAgent.py` | apps | low | 4 | ? | ORCHESTRATOR | Execution | 2.8 |

Impact = `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier`. L0/L5 get ×2.0.

---

## 10. ADG_GRAPH_LAYER_EVIDENCE (constitutional §22)

Materialized views consulted:
1. **mv_debt_concentration_hotspots** — drives W6/W7 target selection (top 15 P3 files by debt score).
2. **mv_hotspot_centrality** — drives critical-path weighting for W6 (path_constants 982, static_scanner 180, SovereignBaseAgent 136).
3. **mv_graph_reverse_dependency_hotspots** — (implicit via edge_fanin) — used per-file in W1/W6 to validate blast radius before edit.

Semantic edges relied on:
- `imports` (fan-in for central-dependency ranking)
- `antipattern` (the sole relation_type carrying severity bands)

P-views cross-referenced:
- `v_p3_isolated_experimental` — confirms `ops_scripts/dev_tools/L0_routing_scripts/_ssot_*.py` cluster is safe for bulk burn in W7.1.
- `v_p2_mixed_usage` — will be re-checked after W2 promotions to confirm no dangling mixed-usage classifications.
- `v_p0_write_bypass_uwg` — used to validate that L4 write-plane fixes (W1.7–W1.8) do not introduce UWG bypasses.

Precision tables: not populated in this snapshot — fall back to AST-based analysis only.

---

## 11. Token Budget (per-wave)

| Wave | Est. tokens | Status | Rationale |
|------|------------:|:------:|-----------|
| W0 | 8k | 🟢 | Plan-only |
| W1 | 45k | 🟡 | 13 files, high-touch surfaces |
| W2 | 30k | 🟡 | ADR + 3 code files + tests |
| W3 | 55k | 🟡 | 15 files, scattered |
| W4 | 40k | 🟡 | 17 files, mostly narrowing |
| W5 | 35k | 🟡 | 13 files, write-plane |
| W6 | 90k | 🔴 | High blast radius, regen per file |
| W7 | 40k | 🟡 | Batch-burn tail |

`W6 is 🔴` — recommend splitting into W6a/W6b (one critical file per µwave) if execution shows token pressure.

---

## 12. Exit Criteria

1. **P0 (hygiene):** 0.
2. **P1:** 0 after W5 completes.
3. **P2:** 0 after W4 completes.
4. **P3:** Ratchet locked; critical-path files (fan_in ≥100) cleared of global_state_mutation.
5. **Ratchet ceilings in `tools/generate/validation/gates.py`:** locked to match post-wave counts; CI blocks regressions.
6. **ADR** published covering all re-severity promotions.
7. **SC-1 (54 structural_conformance P0)** forwarded to separate plan; not blocked by this one.

---

## ADG_HOTSPOT_REPORT

Hotspot rank driving wave sequencing (sourced from `mv_debt_concentration_hotspots`,
`mv_hotspot_centrality`, and band-severity cross-reference):

| Rank | Node / Class | Layer | Fan-in | Archetype | Surfaces | Wave |
|------|--------------|-------|:------:|-----------|----------|------|
| 1 | structural_conformance SC-1 (54 P0) | L0/L1 | high | SAFETY_GATEKEEPER | Security Surface, State Surface | W0 (separate plan) |
| 2 | hallucinated_tool_name (P1, 2 prod) | L2/L3 | medium | CENTRAL_DEPENDENCY | Execution Surface | W1 |
| 3 | global_state_mutation (P1→P2 re-severity) | L2/L4 | high | STATE_NODE | State Surface, Write Surface | W5–W6 |
| 4 | chokepoint_bypass (P0 hygiene, 1) | L4 | low | SAFETY_GATEKEEPER | Security Surface | W2 |
| 5 | v_p0_write_bypass_uwg rows | L4 | medium | STATE_NODE | Write Surface, State Surface | W3 |
| 6 | v_p2_mixed_usage rows | mixed | medium | CENTRAL_DEPENDENCY | Execution Surface | W4 |
| 7 | v_p3_isolated_experimental rows | mixed | low | ORPHAN | none | W4 (candidates for archival) |

## ADG_GRAPH_LAYER_EVIDENCE

Materialized views + semantic edges consulted (see §ADG Provenance above):

| Primitive | Use in this plan |
|---|---|
| `mv_debt_concentration_hotspots` | Ranked structural debt density by file/module for W1 ordering |
| `mv_hotspot_centrality` | Identified high-fan-in nodes for cross-band re-severity priority |
| `mv_graph_reverse_dependency_hotspots` | Consumer blast-radius estimation for each proposed promotion |
| `v_p0_write_bypass_uwg` | W3 gate rows — unauthorized write seams |
| `v_p2_mixed_usage` | W4 candidates for mixed-responsibility refactor |
| `v_p3_isolated_experimental` | W4 orphan archival candidates |
| semantic edge `imports` | fan-in/fan-out computations supporting all above |
| semantic edge `antipattern` (band-tagged) | drives re-severity promotion decisions |
| semantic edge `flows_to` | Traces P1→P2 global_state_mutation propagation |
| semantic edge `writes_to` | Confirms v_p0_write_bypass_uwg classification |

## 13. Open Questions for SR_APPROVAL

1. Is the **re-severity approach** (§3) preferred over a **band-ceiling expansion** approach? (Re-severity is the cleaner answer but requires ADR + migration test.)
2. Should **W6 global_state_mutation** begin before W5 completes (parallel track) or strictly after?
3. Should the **SC-1 structural_wall plan** be authored now as a sibling plan or deferred until this plan's W4?
4. Any L5 guardian exemptions on W1 rows we should surface for explicit Author-Gate approval up front rather than per-file?
