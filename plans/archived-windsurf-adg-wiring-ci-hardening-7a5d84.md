---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\adg-wiring-ci-hardening-7a5d84.md'
original_relative_path: 'adg-wiring-ci-hardening-7a5d84.md'
source_sha256: 7dd4480c6982ba40746d647b1c321cae39a4abca8e836a6d60a93dfe97f9d09b
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Wiring-CI Hardening — Holistic Early-Warning Framework

Status: Todo (plan authored 2026-04-23)
Owner: architecture
Tier: T3 (cross-layer, >5 files, CI plane change)
Plan SSOT: `.windsurf/plans/adg-wiring-ci-hardening-7a5d84.md`

## Problem Statement

Existing ADG CI only asks "is there a *bad* edge?" (anti-patterns, forbidden imports, SC-1). It does **not** ask "is the graph shaped correctly?" — absence-of-good-edge, trace-theater stubs, layer drift, taint flow, and churn hotspots are all invisible today. The C0 Context Engine failure (every stage has fan-in=0; trace-only stub `agentic_core/L1_cognition/utils/c0_context_retriever.py` masquerades as the retriever; docs claim L0 but code is L_PG) proves this gap in production.

## Goal

Ship a holistic ADG wiring-CI framework — ~34 gates across 17 anomaly dimensions — that provides **fail-closed per-commit early warning** on structural anomalies, not just anti-pattern counts. Model follows Thoughtworks architecture fitness functions, augmented with Anthropic/OpenAI agentic-safety patterns and Augment COD policy shape.

## External Research Grounding

| Source | Adopted pattern |
|---|---|
| Thoughtworks / L. Niessen — *Architecture Fitness Functions* | Per-commit, objective, block/warn tiering; layer-dep rules; cycle detection; code-metric gates; naming conventions |
| Augment Code — *COD Model, Phase 5* | `cod-policy.yml` block/warn split; `maxNewOrphans: N` ratchet; churn × complexity hotspot; duplicate-helper detection; CVE matching |
| Neo4j — *deps.dev, KeyLines dependency hell* | Transitive CVE propagation; undirected cycle detection; version-link cycles |
| TigerGraph — *graph-algorithms glossary* | Community detection for shadow SSOTs; centrality scoring |
| Anthropic — *Building Effective Agents* | Programmatic gate checks at every chain step; evaluator-optimizer separation; "ground truth at each step" = tool-call/observability parity |
| OpenAI — *Agent-Builder Safety + Agentic Governance Cookbook* | Untrusted data must not drive decisions; structured-field extraction boundary; built-in + workflow guardrails; ZDR trace processors |
| CodeScene — *change-coupling research* | `hotspot_score = change_frequency × cyclomatic_complexity` |

## Hardened Anomaly Taxonomy (50 signals, 17 dimensions)

Dimensions A–J from prior analysis plus K–Q (new from research):

- **A** Topology shape (orphans, cycles, dead symbols, leaves, chokepoints)
- **B** Layer / gravity (reverse, skip, L_PG drift, doc-binding, misclassification)
- **C** Semantic edges (UWG bypass, L5 bypass, silent write, policy-without-audit, unresolved callsite, orphan side-effect, read-without-gate)
- **D** Role / duplication (role dedup with orphans, shadow SSOT, protocol without impl, parallel inheritance)
- **E** Trace theater (stub modules, import-time emits, emit-to-impl ratio, emit-without-receipt)
- **F** Contract / interface (untyped seam, broken-contract consumer, missing adapter)
- **G** Test ↔ prod (prod imports test, seam-test coherence, test-only prod consumer, symbol without test)
- **H** Drift / time-series (new orphans, fan-in collapse, AP velocity, MV staleness, trace-theater growth)
- **I** Observability binding (L5 without L6, evidence-built-not-consumed, write without OTEL adapter)
- **J** Doctrinal SSOT (canonical pipeline binding, ADR↔ADG, rule-cited-gate-orphan)
- **K** *(new)* Churn × complexity hotspot
- **L** *(new)* Supply-chain / CVE propagation
- **M** *(new)* Taint flow — untrusted source reaches decision node
- **N** *(new)* Guardrail/evaluator co-location
- **O** *(new)* Tool-call ground-truth parity
- **P** *(new)* Structured-field extraction boundary
- **Q** *(new)* Simple metric fitness functions (LOC, cyclomatic, method count)

Tiering: **B** = blocking fail-closed; **R** = ratchet (today's value is ceiling); **W** = warn/investigate; **K** = KPI trend only.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W1 | W1.1–W1.4 | Scaffold, manifest, first gate | 🟢 18k | ADG MCP healthy; snapshot ≤ 24h old | Todo | Harness importable; pipeline manifest schema validates; gate J1 fails red on C0 |
| W2 | W2.1–W2.5 | Topology blockers | 🟢 22k | W1 merged | Todo | Orphan count ratcheted; cycles fail PR; trace-stub `c0_context_retriever.py` flagged; seam-test coherence fails red |
| W3 | W3.1–W3.6 | Layer & doc-binding + cheap metrics | 🟢 20k | W1 merged; pipeline manifest has ≥2 entries | Todo | L_PG drift ratcheted; 3 rerankers collapsed; LOC/cyclomatic gates live |
| W4 | W4.1–W4.9 | Semantic-edge wiring | 🟡 28k | W1 merged; P-views populated (`v_p0_write_bypass_uwg`, etc.) | Todo | UWG bypass, L5 bypass, tool-call parity, guardrail co-location all fail red on any regression |
| W5 | W5.1–W5.6 | Dataflow + supply chain | 🟡 24k | W4 merged; OSV/deps.dev client available | Todo | Taint-flow gate live; structured-field boundary enforced; CVE propagation gate live |
| W6 | W6.1–W6.6 | Temporal + KPI dashboard | 🟢 18k | W1 merged; ≥3 snapshots in rolling window | Todo | Snapshot-diff gate live; churn×complexity dashboard published; MV staleness fails red |

**Total**: ~130k tokens, ~5,150 LOC, 6 PRs. GREEN bands (W1, W2, W3, W6) = well within per-wave 32k budget. YELLOW (W4, W5) = approach 28k/24k; split mid-wave if growth.

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|
| W1.1 | Base harness `_adg_wiring_gate_base.py` | 1 py + 1 unit test | Design block/warn/ratchet shared class | 5k | Todo |
| W1.2 | Pipeline manifest schema + YAML | `config/canonical_pipelines.yaml`, `config/schemas/canonical_pipeline.schema.json` | Seed C0 only; schema tight enough to reject typos | 4k | Todo |
| W1.3 | Gate J1 — canonical pipeline wiring | `ops_scripts/ci/check_canonical_pipeline_wiring.py` + test | First real gate; must fail red on C0 | 6k | Todo |
| W1.4 | Violation JSONL sink + waiver format | `artifacts/windsurf/wiring_gate_violations.jsonl` pattern + `config/wiring_gate_waivers.yaml` | Shared by all future gates | 3k | Todo |
| W2.1 | Gate A1 — orphan module ratchet | `check_orphan_module_ratchet.py` + baseline JSON | Lock today's count; Augment COD `maxNewOrphans: 3` delta | 5k | Todo |
| W2.2 | Gate A6 — import cycle (directed + undirected) | `check_import_cycles.py` | SCC on `imports` + Neo4j-style undirected 4-cycle check | 5k | Todo |
| W2.3 | Gate A3 — dead symbol detector | `check_dead_symbols.py` | Symbol `fan_in=0` in module with `fan_in>0` | 4k | Todo |
| W2.4 | Gate E1 — trace-stub detector | `check_trace_stub_modules.py` | Catches `c0_context_retriever.py` pattern | 4k | Todo |
| W2.5 | Gate G2 — seam-test export coherence | `check_seam_test_export_coherence.py` | AST parse tests + `__init__.py` symbols | 4k | Todo |
| W3.1 | Gate B2 — layer-skip path check | `check_layer_skip.py` | Path query on `imports` across layer ordinals | 4k | Todo |
| W3.2 | Gate B3 — L_PG drift ratchet | `check_lpg_drift.py` | L_PG with `fan_in>0` from L0–L6 | 3k | Todo |
| W3.3 | Gate B4 — doc↔layer binding | `check_doc_layer_binding.py` | Reads pipeline manifest, verifies layer match | 4k | Todo |
| W3.4 | Gate D1 — role dedup with orphans | `check_role_dedup.py` | Regex role clusters; flag >1 orphan in cluster | 3k | Todo |
| W3.5 | Gate Q.1 — file LOC ceiling (Thoughtworks) | `check_file_loc_ceiling.py` | ≤500 LOC default, overrideable per-file | 3k | Todo |
| W3.6 | Gate Q.2 — cyclomatic complexity ceiling | `check_cyclomatic_ceiling.py` | `radon` or AST-based | 3k | Todo |
| W4.1 | Gate C1 — UWG write-path bypass | `check_uwg_bypass.py` | Consumes `v_p0_write_bypass_uwg` | 4k | Todo |
| W4.2 | Gate C2 — L5 guardrail bypass | `check_l5_bypass.py` | `flows_to` path without L5 intersection | 4k | Todo |
| W4.3 | Gate C3 — silent write (no side-effect emit) | `check_silent_writes.py` | `writes_to` without sibling `emits_side_effect` | 3k | Todo |
| W4.4 | Gate C4 — policy decision without audit | `check_policy_without_audit.py` | `controls_flow` without L6 emit | 3k | Todo |
| W4.5 | Gate C5 — unresolved callsite ratchet | `check_unresolved_callsites.py` | `resolves_callsite.target_id IS NULL` | 3k | Todo |
| W4.6 | Gate I1 — L5 without L6 audit | `check_l5_audit_parity.py` | Path from L5 enforcement node to L6 required | 3k | Todo |
| W4.7 | Gate I2 — evidence contract unconsumed | `check_evidence_consumption.py` | `EvidenceContract*` symbol `fan_in=0` | 2k | Todo |
| W4.8 | Gate O — tool-call ground-truth parity (Anthropic) | `check_tool_call_receipt.py` | Every tool-call edge pairs with observability emit | 3k | Todo |
| W4.9 | Gate N — guardrail/evaluator co-location (Anthropic) | `check_guardrail_evaluator_separation.py` | Screen node must not share `writes_to` with core-response node | 3k | Todo |
| W5.1 | Gate M — taint flow (OpenAI) | `check_taint_flow.py` | External `reads_from` → validator → decision path | 6k | Todo |
| W5.2 | Gate P — structured-field extraction boundary (OpenAI) | `check_structured_extraction_boundary.py` | External read must hit `type_surface != ""` node first | 4k | Todo |
| W5.3 | Gate L — CVE propagation (Neo4j/deps.dev) | `check_cve_propagation.py` + OSV client | Transitive closure × OSV DB match | 6k | Todo |
| W5.4 | Gate F1 — untyped cross-layer seam | `check_untyped_seams.py` | Ratchet on `type_surface=""` across L→L edges | 3k | Todo |
| W5.5 | Gate F2 — broken-contract consumer | `check_broken_contract.py` | Symbol import resolves to nothing exported | 3k | Todo |
| W5.6 | Gate F3 — missing adapter for declared Protocol | `check_missing_adapter.py` | `Protocol` classes without concrete-class edge | 2k | Todo |
| W6.1 | Gate H1 — new-orphan delta (snapshot diff) | `check_new_orphans_delta.py` | Compare last 2 snapshots; any new orphan fails | 4k | Todo |
| W6.2 | Gate H2 — fan-in collapse on high-centrality nodes | `check_fanin_collapse.py` | >30% drop on `mv_hotspot_centrality` top-50 | 4k | Todo |
| W6.3 | KPI K — churn × complexity dashboard | `reports/churn_complexity_heatmap.py` + Notion row | CodeScene formula; weekly run | 3k | Todo |
| W6.4 | KPI E3 — trace-theater growth per layer | `reports/trace_theater_kpi.py` | `_emit_*` count / real-impl import count | 2k | Todo |
| W6.5 | KPI H3 — anti-pattern velocity per 1k LOC | `reports/ap_velocity.py` | Time-series, Notion writeback | 2k | Todo |
| W6.6 | Gate H4 — MV staleness | `check_mv_staleness.py` | Edge count delta >5% since last MV refresh | 3k | Todo |

## ADG_HOTSPOT_REPORT — Seed Evidence (C0 orphan cluster)

| Module | ADG id | Layer | Fan-in (imports) | Archetype | Surface | Impact Score |
|---|---:|---|---:|---|---|---:|
| `agentic_core/L1_cognition/utils/c0_context_retriever.py` | 259 | L1 | 0 | ORPHAN (trace-stub) | None | 0 |
| `agentic_core/L3_orchestration/reasoning/engines/omni_context_engine.py` | 553 | L3 | 0 | ORPHAN | None | 0 |
| `agentic_core/knowledge/retrieval/hybrid_recall_stage.py` | 1829 | L_PG | 0 | ORPHAN (C0.2) | State | 0 |
| `agentic_core/knowledge/retrieval/retrieval_plan.py` | 1832 | L_PG | 0 | ORPHAN (C0.1) | Security | 0 |
| `agentic_core/knowledge/retrieval/senior_librarian_reranker.py` | 1833 | L_PG | 0 | ORPHAN (C0.4) | None | 0 |
| `agentic_core/knowledge/retrieval/evidence_contract_builder.py` | 1828 | L_PG | 0 | ORPHAN (C0.5) | State | 0 |
| `agentic_core/knowledge/gates/preretrieval_gate.py` | 1797 | L_PG | 0 | SAFETY_GATEKEEPER (orphan) | Security | 0 |

All seven have impact_score = 0 because current formula (`violations × (1 + log10(1+fan_in)) × layer_mult`) collapses on zero fan-in. **This plan's W1.3 gate J1 catches exactly this class of zero-score orphan that the current hotspot formula masks.**

## ADG_GRAPH_LAYER_EVIDENCE

Gates consume these graph-layer primitives (materialized views + pre-built P-views + semantic edges):

- `mv_hotspot_centrality` — W6.2 (fan-in collapse), W3.4 (role dedup shadow candidates)
- `mv_graph_chokepoint_bridges` — W4.x (semantic bypass impact scoring)
- `mv_graph_critical_path_blast_radius` — W6.2 (fan-in collapse ranking)
- `mv_dependency_cone_risk` — W4.2 (L5 bypass blast-radius)
- `mv_exemptions_near_critical_paths` — W4.1 (UWG bypass exemption review)
- `mv_debt_concentration_hotspots` — W6.3 (churn × complexity overlay)
- `v_p0_write_bypass_uwg` — W4.1 (direct consumer)
- `v_p0_apps_direct_infra` — W3.1 (layer-skip baseline)
- `v_p1_mis_layered_infra` — W3.2 (L_PG drift)
- `v_p1_zero_caller_infra` — W2.1 (orphan ratchet baseline)
- `v_p2_duplicated_adapters` — W3.4 (role dedup)
- `v_p3_isolated_experimental` — W2.1 orphan allowlist (experimental exempted)

Semantic edges used: `imports`, `flows_to`, `reads_from`, `writes_to`, `emits_side_effect`, `controls_flow`, `resolves_callsite`. Precision tables (`precision_call_resolution`, `precision_side_effects`) consumed by W4.5, W4.8, W5.1.

## Gap Register

| Gap | Mitigation | Wave |
|---|---|---|
| No shared wiring-gate harness exists | W1.1 | W1 |
| No canonical pipeline manifest concept | W1.2 | W1 |
| `precision_call_resolution` may be sparse → C5 false negatives | W4.5 ratchet on populated subset only; alert if table shrinks | W4 |
| OSV client not yet in `enhanced_http` allowlist | W5.3 adds ADR for external dep | W5 |
| MV refresh cadence currently ad hoc | W6.6 adds explicit staleness gate | W6 |
| Test-scope regex may misidentify `tests/**/fixtures/` as prod | W2.5 allowlist | W2 |

## Rollback Checkpoints

- After W1: harness + J1 gate — revert by deleting `ops_scripts/ci/_adg_wiring_gate_base.py`, `ops_scripts/ci/check_canonical_pipeline_wiring.py`, `config/canonical_pipelines.yaml`. No schema / state changes.
- After W2: revert baselines under `ops_scripts/ci/baselines/wiring_*.json`. Gates read baselines, so deletion auto-disables.
- After W4: all semantic-edge gates read-only against ADG; no rollback action needed beyond git revert of the gate scripts.
- After W5: if OSV client problematic, gate L has feature flag `CVE_PROPAGATION_BYPASS=1`.
- After W6: KPI reports are Notion-writeback-only; no prod CI impact from disabling.

## Token Budget Per Wave

| Wave | Estimate | Band | Note |
|---|---:|:---:|---|
| W1 | 18k | 🟢 GREEN | Well within 32k per-wave ceiling |
| W2 | 22k | 🟢 GREEN | 5 gates, ~5k each |
| W3 | 20k | 🟢 GREEN | 6 gates, cheap AST + metric queries |
| W4 | 28k | 🟡 YELLOW | 9 gates; split at phase W4.5 if any gate exceeds 4k |
| W5 | 24k | 🟡 YELLOW | Includes OSV client + taint-flow graph query (most complex) |
| W6 | 18k | 🟢 GREEN | KPI-heavy; lightweight queries |

Grand total: **130k tokens across 6 PRs**. No single PR > 28k.

## CI Wiring

Each gate is registered in two places:
1. `.pre-commit-config.yaml` (local per-file invocation where feasible)
2. `ops_scripts/ci/run_contract_gates.py` (full-repo PR-level invocation)

New gates inherit `WiringGate` base class — one SQL + one fail predicate + tier. Baselines live under `ops_scripts/ci/baselines/wiring_<gate>.json`. Waivers under `config/wiring_gate_waivers.yaml` with required fields `{gate, scope, reason, owner, expires_on}`.

## Exit Criteria

Plan is DONE when:
- All 34 gates are merged and green on main
- `artifacts/windsurf/wiring_gate_violations.jsonl` appends on every CI run
- C0 orphans flagged by gate J1 are either wired (preferred) or explicitly waived with 90-day expiry
- Notion MCP Registry entry added: "Wiring-CI gate plane v1" with the 34 gate names and their tiers
- ADR written: `docs/architecture/adr/ADR-NNN-adg-wiring-ci-framework.md` citing research sources
- Memory entity `ArchitecturalInvariant:ADGWiringCIFramework` created with dim A–Q summary
