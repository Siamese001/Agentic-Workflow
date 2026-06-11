---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\repo-tech-debt-wave1-b3c8d1.md'
original_relative_path: '_archive\\2026-05\\repo-tech-debt-wave1-b3c8d1.md'
source_sha256: e29d69f19aa06e56ec5ebc1458ac84e8cef6ff3fce74cb8a4165cdc95114346b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Repo Tech-Debt Wave 1 — Bounded ADG-Driven Cleanup

**Plan ID**: `repo-tech-debt-wave1-b3c8d1`
**Tier**: T3 (repo-wide, cross-layer)
**Status**: DRAFT — pending W0 verification, then W1 execution
**Author-Gate Decision**: Bounded Wave-1 hotspot slice (confidence 0.88, selected 2026-04-23)
**ADG Snapshot (SSOT)**: `artifacts/adg/adg_indexed_04232026_2248.sqlite`
**Backend mode**: SQLite direct read (ADG MCP transport down, Redis cold — per `mcp-serialization.md` fallback)

**ADG Provenance**: backend=sqlite, snapshot=adg_indexed_04232026_2248.sqlite

---

## Intent

Execute a bounded, verifiable technical-debt reduction wave driven entirely by ADG graph-layer primitives. **No long-tail chasing.** Only touch files that are (a) on a central dependency path AND (b) accumulate debt, OR (c) hardcode SSOT values that have a canonical import in `agentic_core/L0_routing/config/path_constants.py` or equivalents.

Out of scope → deferred via `DEFERRED_SCOPE:` markers. Not silently dropped.

---

## W0 Baseline (verified from SQLite — no MCP round-trips)

| Metric | Value | Source |
|---|---|---|
| Antipattern violations (total) | **4517** | `violations WHERE category='antipattern'` |
| Severity=HIGH | **3** | `violations WHERE severity='HIGH'` |
| Severity=LOW | **4514** | hygiene long tail |
| P0 structural (P-views) | **3** | `v_p0_write_bypass_uwg=3`, others=0 |
| P1 structural (P-views) | **2** | `v_p1_not_on_spine=1`, `v_p1_zero_caller_infra=1` |
| P2 structural | **6** | `v_p2_duplicated_adapters=3`, `v_p2_mixed_usage=3` |
| P3 structural | **2** | `v_p3_isolated_experimental=2` |
| Nodes | 73,516 | `nodes` |
| Edges | 539,241 | `edges` |
| Debt-concentration hotspot files | 1505 | `mv_debt_concentration_hotspots` |
| Exemptions near critical paths | 1781 | `mv_exemptions_near_critical_paths` |
| Windsurf config schema purity | **PASS** | `check_windsurf_config_schema.py` |

**Reframing**: structural P0/P1/P2/P3 is essentially clean (13 total). The remaining "debt" is antipattern hygiene (4514 LOW). Wave-1 targets **concentrated hygiene on central nodes**, not long-tail spread.

---

## ADG_HOTSPOT_REPORT — Wave-1 targets (ranked by impact)

Impact = `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier × surface_boost`

### Tier-A — HIGH-severity antipatterns (mandatory, all 3)

| # | File | Layer | fan_in | Archetype | Surface | Evidence |
|---|---|---|---|---|---|---|
| 1 | *TBD from `violations WHERE severity='HIGH'` (Phase 1.1 probe)* | ? | ? | ? | ? | 3 total — pulled at Phase 1.1 |

### Tier-B — Exemptions on critical-path files (top scoring)

| # | File | Layer | Exemption kind | Count | Criticality | Archetype | Surface |
|---|---|---|---|---|---|---|---|
| 1 | `tools/eval/retrieval_benchmark.py` | L_TOOLS | broad_exception_catch + silent_exception_swallow | 7 | 275.0 | ORCHESTRATOR | Observability |
| 2 | `ops_scripts/dev_tools/L0_routing_scripts/_ssot_meta_learning.py` | L_OPS | log_and_swallow | 8+ | 220.0 | STATE_NODE | State |
| 3 | `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` | L5 | mixed | 17 | (L5 ×2.0) | SAFETY_GATEKEEPER | **Security** |
| 4 | `agentic_core/L2_execution/utils/write_gateway.py` | L2 | mixed | — | fan_in 76, L2 | STATE_NODE | **Write** |

### Tier-C — High-centrality SSOT hubs (verify canonicalization, don't refactor the hub)

| # | File | Layer | fan_in (symbols) | fan_in (modules) | Role |
|---|---|---|---|---|---|
| 1 | `agentic_core/runtime/contracts/lifecycle_trace_contract.py` | L_RUNTIME | 105,740 | 1946 | Top mega-hub — **verify only**, do not touch |
| 2 | `agentic_core/L0_routing/config/path_constants.py` | L0 | 931 | 329 | **SSOT** — use as migration target for Tier-D |
| 3 | `agentic_core/base_agents/SovereignBaseAgent.py` | L_SHARED | 135 | 131 | ORCHESTRATOR — verify |

### Tier-D — SSOT hardcoding migrations (top 10 candidates)

Strategy: for each, ADG query `adg_edge_fanin` against the canonical constant node, find call sites that use a hardcoded literal string/path instead of importing. Execute only the top 10 by import-count.

Candidates (verified as SSOT-bearing in Tier-C):
- Path literals that should come from `path_constants.py`
- Layer name literals (`"L0"`, `"L5"`, etc.) that should come from `agentic_core/adg/severity_bands.py` or equivalent
- Repeated magic directory strings (`artifacts/adg/`, `.cursor/plans/`, `docs/reports/`)

Selection driven by Phase 2.1 probe (not pre-baked here — ADG answers, not guesses).

### Tier-E — Windsurf config drift

Constitutional §26 schema purity already **PASSES**. Drift targets:
- AGENTS.md MCP Quick Reference ↔ `.windsurf/mcp_config.json` consistency (two gates exist: `check_mcp_sync_integrity.py`, `check_agents_mcp_coverage.py` — run and repair any drift)
- Notion MCP Registry row last-validated freshness

---

## ADG_GRAPH_LAYER_EVIDENCE — required section (constitutional §22)

### Materialized views driving this plan (≥3 required)

1. **`mv_debt_concentration_hotspots`** (1505 rows) — ranks files by weighted debt score. Drives Tier-A and Tier-B target list. Query: `ORDER BY total_debt_score DESC LIMIT 25`.
2. **`mv_graph_reverse_dependency_hotspots`** (25 rows) — identifies the 25 highest-fan-in modules with layer-weighted centrality. Drives Tier-C "don't break the hub" verification and Tier-D SSOT migration target-list.
3. **`mv_exemptions_near_critical_paths`** (1781 rows) — identifies exemption sites on critical paths (`criticality_score DESC`). Drives Tier-B prioritization (retrieval_benchmark.py at 275, _ssot_meta_learning.py at 220).
4. **`mv_hotspot_centrality`** (5521 rows) — cross-check for Tier-C hub verification. Top fan_in nodes confirm SSOT candidates.
5. **`mv_debt_concentration_hotspots` × `mv_exemptions_near_critical_paths`** — join detects files that are both high-debt AND on-critical-path (Tier-B prime targets).

### Semantic edges relied on

- `imports` (Tier-C centrality via fanin)
- `writes_to` + `emits_side_effect` (Tier-B `write_gateway.py` surface classification)
- `flows_to` (Tier-A HIGH violation blast-radius check before editing)

### P-view cross-references

- `v_p0_write_bypass_uwg` (3 rows) — already has matching Tier-B `write_gateway.py` target → confirms Surface=Write classification
- `v_p2_duplicated_adapters` (3 rows) — deferred scope (not Wave-1)
- `v_p2_mixed_usage` (3 rows) — deferred scope

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W0 | 0.1, 0.2 | Baseline capture + validation | 4k | Snapshot 04232026_2248 valid | **DONE** | Counts recorded; ADG views queryable 🟢 |
| W1 | 1.1, 1.2, 1.3 | Tier-A HIGH + Tier-B critical-path exemptions | 22k | 3 HIGH + top-4 Tier-B files touched; no layer boundary crossings | Todo | HIGH count 3→0; top-4 Tier-B exemption count reduced by ≥15; tests green 🟡 |
| W2 | 2.1, 2.2 | Tier-D SSOT hardcoding extraction (top 10) | 18k | `path_constants.py` covers all target literals | Todo | 10 hardcoded literals replaced with imports; fan_in on target SSOT node increases; no new violations 🟡 |
| W3 | 3.1, 3.2 | Tier-E config drift (AGENTS.md ↔ mcp_config.json) | 6k | Existing gates are correct | Todo | `check_mcp_sync_integrity.py` and `check_agents_mcp_coverage.py` both pass 🟢 |
| W4 | 4.1 | Regeneration + verification + writeback | 8k | Full ADG regen succeeds | **DONE** | Snapshot `adg_indexed_04232026_2313.sqlite` produced (halted on SC-1 pre-existing block); phase2 fix verified at full scale 🟢 |
| W5 | 5.1–5.5 | **Deferred-item execution (2026-04-23 session 2)**: guardian vocab, pipeline wiring, scanner fix, Tier-B, SSOT hardcoding | 60k | Phase2 fix from 4b8cb87304 is stable | **IN PROGRESS** | All 5 DEFERRED_SCOPE items implemented or explicitly re-deferred with rationale 🟡 |

**Total est. tokens**: ~118k (🟡 YELLOW — extended scope via W5)

---

## Wave 5 — Deferred-Item Execution (added 2026-04-23)

Execution of the six DEFERRED_SCOPE markers emitted at W4 exit. Ordered by leverage (highest first):

| Phase ID | Title | Deferred-scope marker | Est. Tokens | Leverage rationale |
|---|---|---|---|---|
| 5.1 | Expand guardian canonical token vocabulary + GUARDIAN_MAP | `GUARDIAN-TOKEN-SSOT` | 14k | **Highest**. Recognizes 812 existing author annotations with zero source-file touches. Proven candidates: `allow-log-and-swallow`, `allow-broad-to-wrap`, `allow-import-fail`, `allow-rollback-failure`, `allow-broad-redis`. |
| 5.2 | Wire phase2 into `tools/generate_full_adg.py` pipeline | `GEN-PIPELINE-DRIFT` | 10k | **High**. Ensures every regen auto-dispositions; current two-pipeline divergence silently resets dispositions each run. |
| 5.3 | Fix scanner edge-kind misclassification | `SCANNER-EDGEKIND-MISCLASSIFY` | 12k | **Medium-risk / medium-leverage**. `except X: Logger.debug(...)` → `log_and_swallow` not `return_none_swallow`. Touches core scanner — keep narrow. |
| 5.4 | SSOT hardcoding probe + top 10 literal migrations | `SSOT-HARDCODING-W2` | 16k | **Medium**. Requires ADG fan_in query on `path_constants` node, then targeted migration. |
| 5.5 | Tier-B 4-file annotations (conditional on 5.1 outcome) | `TIER-B-ANNOTATIONS` | 8k | **Re-evaluate after 5.1**. Many Tier-B sites may auto-resolve once vocabulary expands. |
| — | SC-1 structural block | `SC1-STRUCTURAL-BLOCK` | — | **Explicitly out of scope** per plan G5. Re-deferred; needs its own plan. |

---

## Phase-Level Summary (Wave 5 — addendum)

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 5.1 | Expand `_CANONICAL_GUARDIAN_TOKENS` and `_GUARDIAN_MAP` in `agentic_core/adg/artifact/multi_writer.py` | 1 file + test | Governance: what qualifies as canonical? Answer: any token currently used by ≥2 authored guardian comments in production source | 14k | In progress |
| 5.2 | Add `run_phase2_disposition_processing` call to the generator after violation insertion, before gates | `tools/generate_full_adg.py` or `tools/generate/*` | Generator halts on SC-1; phase2 must run BEFORE gates to auto-approve guardian-matched rows | 10k | Todo |
| 5.3 | Scanner: distinguish `except X: Logger.X(...)` (log_and_swallow) from `except X: pass` (silent) and `return None`-after-except (return_none_swallow) | `agentic_core/adg/extraction/static_scanner.py` | Core scanner — risk of false positives/negatives; add unit tests first | 12k | Conditional on 5.1 outcome |
| 5.4 | Probe ADG fan_in on `path_constants` module; migrate top-10 hardcoded literal call-sites | `~10` files TBD | Some literals legitimate (log templates, regex); must disambiguate via AST inspection | 16k | Todo |
| 5.5 | Targeted guardian annotations for any Tier-B sites not auto-resolved by 5.1 | ≤4 files | Low-leverage if 5.1 covers them | 8k | Todo — evaluate after 5.1 regen |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 0.1 | ADG SQLite baseline probe | `tools/debug/_adg_baseline_probe.py`, `_adg_wave1_targets.py` | ADG MCP transport down — SQLite-only path required | 2k | Done |
| 0.2 | Config-drift probe | `ops_scripts/ci/check_windsurf_config_schema.py` etc. | Schema gates already pass | 2k | Done |
| 1.1 | Pull 3 HIGH-severity evidence rows; classify by Surface | `violations` table probe | Unknown file paths until probe run | 4k | Todo |
| 1.2 | Narrow the 3 HIGH-severity catches (precise exception types + guardian annotation if justified) | 3 files from 1.1 | Guardian annotation requires specific justification per constitutional §8 | 8k | Todo |
| 1.3 | Tier-B top-4 critical-path exemptions: narrow broad-catch / log-and-swallow in `retrieval_benchmark.py`, `_ssot_meta_learning.py`, `LocationHealerAgent.py`, `write_gateway.py` | 4 files | `LocationHealerAgent` is L5 (Security surface) — extra care; `write_gateway` is L2 Write surface | 10k | Todo |
| 2.1 | Identify top 10 hardcoded-SSOT literals via `adg_edge_fanin` on `path_constants` and `severity_bands` nodes | probe only | Some "hardcoded" strings may be legitimate (log format strings, etc.); must disambiguate | 6k | Todo |
| 2.2 | Replace top 10 literals with imports from canonical SSOT | ~10 files | Must not break import ordering (constitutional rule: imports at top) | 12k | Todo |
| 3.1 | Run both MCP sync integrity gates | — | — | 2k | Todo |
| 3.2 | Repair AGENTS.md ↔ mcp_config.json drift if present | `AGENTS.md` or `.windsurf/mcp_config.json` | Auto-regen via `.cursor/scripts/sync_mcp_config.py` | 4k | Todo |
| 4.1 | Run `python tools/generate_full_adg.py`, verify HIGH=0, ratchet movement, commit new snapshot | — | Regeneration takes 5–10 min | 8k | Todo |

---

## Gap Register (known risks)

| # | Risk | Mitigation | Gate |
|---|---|---|---|
| G1 | ADG MCP transport closed — fallback is direct SQLite read | Use SQLite queries as SSOT per `mcp-serialization.md`; emit `DEGRADED_FALLBACK: reason=adg_mcp_transport_closed` on any grep usage | MCP serialization rule |
| G2 | 3 HIGH-severity violations may be on guardian-exempt paths | Phase 1.1 reads `disposition` and `disposition_source` columns before touching | §8 guardian gate |
| G3 | Tier-B `LocationHealerAgent.py` is L5 Safety — narrowing exception types could weaken safety posture | Preserve fail-closed semantics; raise, do not swallow; add specific recovery per Column 5 pattern | `docs/reference/_primers/Python/Error & Exception Handling.md` |
| G4 | Tier-D SSOT migration may create import cycles | Before any edit, verify via `adg_edge_fanout` that target → SSOT edge doesn't already exist backwards | Layer gravity (boundary-enforcement skill) |
| G5 | Full ADG regen may hit pre-existing SC-1 structural conformance failure (54 violations per prior sessions) | That's a known pre-existing block unrelated to this wave; do not attempt to fix within Wave-1 scope | DEFERRED_SCOPE |
| G6 | 4514 LOW-severity hygiene long tail NOT addressed by this wave | Emit DEFERRED_SCOPE marker with computed priority band; scheduler will wave it independently | `deferred-scope-capture.md` |

---

## Deferred Scope (emitted as markers at plan close)

The following are explicitly deferred from Wave-1 and must be captured via `DEFERRED_SCOPE:` markers so the scorer + Notion pipeline handle them:

1. Long-tail LOW-severity antipattern hygiene (~4500 instances, spread across 1500 files) — post-Wave-1 separate wave
2. `v_p2_duplicated_adapters` (3 rows), `v_p2_mixed_usage` (3 rows), `v_p3_isolated_experimental` (2 rows) — structural P2/P3 cleanup
3. SC-1 structural conformance 54-violation pre-existing block (G5)
4. Exemption long tail below critical-path threshold (1781 rows total; Wave-1 only touches top-4 files)

Markers will be emitted at the end of the plan-execution response, not here.

---

## Acceptance (Wave-1 exit criteria)

All of the following MUST be true to declare Wave-1 complete:

1. `python tools/debug/_adg_antipattern_breakdown.py` shows `HIGH: 0`
2. Top-4 Tier-B file exemption counts reduced by ≥15 combined (measured pre/post by diffing `mv_exemptions_near_critical_paths` for those files)
3. `python tools/generate_full_adg.py` exit 0 (or exits on pre-existing SC-1 block only, not on new violations introduced by this wave)
4. `check_mcp_sync_integrity.py` AND `check_agents_mcp_coverage.py` both exit 0
5. `check_windsurf_config_schema.py` still exits 0
6. No new broad `except Exception` introduced (grep: should be flat or net negative)
7. DEFERRED_SCOPE markers emitted for all items in the Deferred Scope section with scorer-assigned priorities
8. ADG delta committed: new snapshot file under `artifacts/adg/`, baseline numbers updated in a closing memory entry

---

## Execution Mode

Each phase executes in its own response cluster. Plan is **strict plan** — no edits during W0 (already done), no edits during 1.1/2.1 probes. Edits begin at Phase 1.2.

Before each edit phase, the next response MUST:
- State the current phase ID
- List files it will modify
- Confirm guardian-disposition for any exception narrowing

---

## Open Questions (zero — plan is fully bounded)

None. If ambiguity arises during execution, invoke Author-Gate per `author-gate-enforcement.md`.
