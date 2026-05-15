# apps_qna Spine Integration — T3 Architecture Plan

**Plan ID**: `apps-qna-spine-integration-e8f3a1`
**Tier**: T3 (architecture decision, cross-layer, multi-wave, irreversible boundary changes)
**Decision class**: `architecture_choice` (per author-gate-enforcement.md)
**Status**: Drafted — pending Author-Gate per Wave entry
**Owner**: Cursor Agent (drafted) → Amit (approver)
**Created**: 2026-04-30
**Persona**: SVP Engineering (per constitutional §9 — operational simplicity, dependency hygiene, archival over deletion, ADRs, zero-regression)

---

## 1. Problem Statement

**`apps_qna` is the only `apps_*` package that does not route through the `agentic_core` spine.** AST scan via `tools/analysis/apps_spine_coverage.py`:

| App | Files | Non-stdlib edges | `agentic_core` edges | Spine % | Status |
|---|---:|---:|---:|---:|---|
| `apps_eval` | 59 | 184 | 55 | 29.9% | ✅ ON_SPINE |
| `apps_exec` | 54 | 131 | 63 | 48.1% | ✅ ON_SPINE |
| `apps_lic` | 90 | 226 | 137 | 60.6% | ✅ ON_SPINE |
| **`apps_qna`** | **30** | **70** | **0** | **0.0%** | **🔴 OFF_SPINE** |
| `apps_research` | 54 | 120 | 53 | 44.2% | ✅ ON_SPINE |
| `apps_rfp` | 53 | 117 | 31 | 26.5% | ✅ ON_SPINE |
| `apps_rg` | 171 | 586 | 338 | 57.7% | ✅ ON_SPINE |
| `apps_shared` | 194 | 505 | 273 | 54.1% | ✅ ON_SPINE |
| `apps_underwriting_ai` | 68 | 166 | 35 | 21.1% | ✅ ON_SPINE |

**Off-spine consequences** (re-derived from upstream best practices — OpenAI BNY Eliza case study, Anthropic Claude Agent SDK, Rakesh Gohel "constraint-first / governance spine" pattern):

1. **Shadow workflow** — duplicates capabilities the spine already provides (validation, observability, retrieval, governance).
2. **Audit gap** — direct `Path.write_text` writes bypass UWG anti-bypass (constitutional §3 violation).
3. **Learning floor** — no system_learning hookup means each interview pack starts from zero; no cross-interview transfer.
4. **TCO inflation** — multi-framework analysis: custom side-system + spine = 3-5× year-1 cost vs. shared platform.
5. **Governance drift** — source-register / regulated-claim policing is local lint, not safety-plane gate.

**Decision** (architecture_choice): Refactor `apps_qna` onto the spine in 5 sequential waves. Off-spine remediation, not greenfield.

`DECISION_CAPTURED: type=architecture_choice, repo_area=apps_qna, selected=spine_integration_5_waves, outcome=executed, principle=every_apps_must_leverage_spine, precedent=none`

---

## ADG_HOTSPOT_REPORT

**Snapshot**: `artifacts/adg/adg_indexed_04302026_0604.sqlite` (544 MB, mtime 04/30 06:58)

**Method**: Reverse-dependency hotspot ranking via `mv_graph_reverse_dependency_hotspots`, filtered to spine modules `apps_qna` will integrate with. Layer multipliers per constitutional §23 (L0=2.0, L5=2.0, L3=1.75, L4=1.75, L1=1.0, L2=1.0, L6=0.75). Note: this ADG snapshot uses an L_RUNTIME / L_SHARED / L_APP virtual-layer overlay in addition to L0..L6.

| Rank | Module | Layer | Fan-in | Layer Mult | Impact = fan-in × (1+log10(1+fan-in)) × mult | Archetype | Surface(s) |
|---:|---|---|---:|---:|---:|---|---|
| 1 | `agentic_core/runtime/contracts/lifecycle_trace_contract.py` | L_RUNTIME | 1954 | 2.0 | ~13,200 | CENTRAL_DEPENDENCY | Execution, Observability |
| 2 | `agentic_core/L0_routing/config/path_constants.py` | L0 | 390 | 2.0 | ~2,200 | CENTRAL_DEPENDENCY | State |
| 3 | `agentic_core/base_agents/SovereignBaseAgent.py` | L_SHARED | 150 | 2.0 | ~700 | ORCHESTRATOR | Execution, Write, Security |
| 4 | `agentic_core/L0_routing/config/__init__.py` | L0 | 119 | 2.0 | ~530 | CENTRAL_DEPENDENCY | State |
| 5 | **`agentic_core/L2_execution/utils/write_gateway.py`** | **L2** | **81** | **1.0** | **~190** | **STATE_NODE** | **Write, Security, Observability** |
| 6 | `agentic_core/L5_safety/runtime_gates/types.py` | L5 | 53 | 2.0 | ~210 | SAFETY_GATEKEEPER | Security, State |
| 7 | `agentic_core/L0_routing/enforcement/mutation_prohibition.py` | L0 | 51 | 2.0 | ~200 | SAFETY_GATEKEEPER | Write, Security |
| 8 | `apps_rg/engines/base_rg_engine.py` | L_APP | 48 | 1.0 | ~110 | ORCHESTRATOR | Execution |
| 9 | `agentic_core/L2_execution/utils/providers.py` | L2 | 47 | 1.0 | ~110 | CENTRAL_DEPENDENCY | Execution |
| 10 | `agentic_core/L0_routing/config/model_registry.py` | L0 | 45 | 2.0 | ~170 | CENTRAL_DEPENDENCY | Execution, State |

**Key finding**: The Write/Security/Observability surfaces converge at `L2_execution/utils/write_gateway.py` (the UWG, despite living in L2 not L4 as architectural diagrams suggest — the path is canonical). `apps_qna` would join 81 existing reverse-deps as a STATE_NODE consumer.

**Zero-Loss Propagation Pipeline check** (per constitutional §23 — every refactoring target must trace this chain):

```
[ apps_qna/builder/card_pack_builder.py — direct Path.write_text ]
       ↓ (current, off-spine)
[ NO antipattern edge in the ADG — apps_qna isn't even in the snapshot yet ]
       ↓ (would be: write_bypass_uwg if scanned)
[ Module: apps_qna → owning Layer: L_APP (none registered) ]
       ↓
   Pattern severity: HIGH (write without UWG audit trail)
   Layer: L_APP (multiplier 1.0)
   Fan-in: 0 (apps_qna is leaf)
   Fan-out: 0 outbound to spine (the violation)
   Surfaces crossed: Write (no UWG), Observability (no OTEL), State (direct file write)
       ↓
[ HOTSPOT: apps_qna/builder/card_pack_builder.py — high pattern severity, low blast radius, 3-surface intersection ]
```

**Hotspot archetype for apps_qna itself**: `STATE_NODE` (writes pack files; would normally be ORCHESTRATOR if it routed through spine).

**Surface intersections** per constitutional §23 (5 ADG Surfaces): the integration crosses the **Write Surface** (UWG-bypassed file writes today), the **Observability Surface** (no OTEL spans on build today), the **State Surface** (direct file mutations untracked), and post-W3 the **Security Surface** (source-register policy gate at L5) and **Execution Surface** (L2 synthesis callsites for STAR/RCA/architecture content). All 5 surfaces are touched by the time W3 lands — the highest-priority remediation profile per §23 §3.

---

## ADG_GRAPH_LAYER_EVIDENCE

Per constitutional §22, this section MUST cite ≥3 materialized views + semantic edges + cross-references against P-views. CI gate: `ops_scripts/ci/check_graph_layer_evidence.py`.

### 3.1 Materialized Views Consulted

1. **`mv_graph_reverse_dependency_hotspots`** — drove the hotspot table in §2. Confirms that integration points (UWG, L0 path_constants, L2 providers, L5 runtime_gates, L6 promotion_gates) are all high-fan-in CENTRAL_DEPENDENCY / SAFETY_GATEKEEPER nodes — apps_qna joining their fan-in is structurally consistent with how every other apps_* already consumes them.

2. **`mv_graph_chokepoint_bridges`** — to be queried at Wave 1 entry to verify that the integration adapter we add (`apps_qna/integrations/spine_adapter.py`) does not create a NEW chokepoint. Expectation: it will appear as a low-rank bridge (apps_qna leaf → spine), not a true bottleneck.

3. **`mv_graph_critical_path_blast_radius`** — to be re-queried after each wave. Wave 1 (UWG integration) should add apps_qna to the critical-path blast radius of `L2_execution/utils/write_gateway.py`. This is intentional — putting apps_qna under the same blast radius as every other write-emitting app is the explicit goal of spine integration.

4. **`mv_hotspot_centrality`** — apps_qna currently absent from the centrality ranking (snapshot was generated before apps_qna was authored today). Post-integration, expected centrality for apps_qna leaf modules: ≤ rank 50 (low — leaf characteristic preserved).

### 3.2 Semantic Edge Coverage

| Semantic edge | Current apps_qna | Post-integration target |
|---|---|---|
| `imports` | 70 outbound (zero into agentic_core) | ~25–40 into agentic_core (mirroring `apps_shared` distribution: L0 dominant, L3/L5/L2 secondary) |
| `flows_to` | None (no agent dispatch) | apps_qna L_APP → L2 execution → UWG L2 → L6 ledger |
| `writes_to` | Direct Path.write_text (uninstrumented) | Routes through `DurableWriteGateway` — every card write emits a `writes_to` edge to UWG |
| `emits_side_effect` | Untracked filesystem mutations | Captured at UWG boundary |
| `controls_flow` | Local Jinja2 render | L3 orchestration controls the build pipeline |
| `reads_from` | YAML + JSON via Path.read_text | L1 retrieval-router for research-brief sectioning (Wave 2); raw reads remain for typed schemas (YAML stays the contract) |
| `resolves_callsite` | All internal | Wave 3 introduces L2 callsites for STAR/RCA synthesis |

### 3.3 P-View Cross-Reference

`v_p0_write_bypass_uwg` (currently 0 rows in snapshot — apps_qna isn't in the snapshot yet). Post-Wave-0 ADG regen, **apps_qna is expected to appear in this view**. Wave 1 explicitly retires those rows by routing all writes through UWG. CI ratchet: `v_p0_write_bypass_uwg` count must monotonically decrease at every wave commit.

`v_p1_not_on_spine` — to be queried at Wave 1 entry. Expected to enumerate apps_qna modules. Each wave reduces the count.

`v_p0_apps_direct_infra` — currently 0 rows (good). Wave 0 (ADG regen) MUST keep this at 0; if apps_qna spine integration accidentally introduces direct-infra imports (e.g., `import sqlite3` instead of going through L4/UWG), those would surface here.

### 3.4 Provenance Stamp

**ADG Provenance**: `backend=sqlite, snapshot=adg_indexed_04302026_0604.sqlite`

---

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W1 | 1.1, 1.2, 1.3, 1.4 | Foundation: writes through UWG, OTEL spans on build, L6 ledger writeback | 18,000 | UWG L2 path stable; apps_shared adapters reusable | Todo | All 22-card pack writes route through `DurableWriteGateway`; `v_p0_write_bypass_uwg` count for apps_qna = 0; build emits OTEL trace. |
| W2 | 2.1, 2.2, 2.3 | Retrieval: L1 retrieval-router replaces regex section-split for research brief PDFs | 22,000 | `agentic_core/L1_cognition/reasoning/retrieval_router.py` exposes a callable interface; chunking primitives stable | Todo | Searce research PDF (47k chars) sections cleanly into ≥6 typed sections via retrieval-router; existing tests still 94/94. |
| W3 | 3.1, 3.2, 3.3, 3.4 | Synthesis: L2 execution for STAR/RCA/cross-exam authoring; L5 source-register policy gate | 35,000 | L2 provider routing available; ExperiencePoint → STAR mapping is deterministic enough to test | Todo | Hand-authored content blocks become L2-synthesized + Author-Gate approved; source-register citations enforced at safety plane. |
| W4 | 4.1, 4.2, 4.3 | Selection: L0 NamespaceBandit for likely-question route selection; bandit over card paste-set per interviewer signal | 20,000 | NamespaceBandit ledger writeable; Wilson CI promotion gates available | Todo | Likely-questions trim from 9 → top-N empirically; paste-set selection is bandit-driven, not hand-curated. |
| W5 | 5.1, 5.2, 5.3 | Learning: system_learning episodic capture per interview; flywheel promoter wires to next-pack defaults | 25,000 | system_learning episodic store accepts new EpisodicEvent type; flywheel promoter accepts new namespace | Todo | Pack v_n+1 starts smarter than v_n on cross-interview transfer; system_learning EpisodicEvent rows for `qna_pack_outcome:*` populate. |

**Total estimate**: ~120,000 tokens across 5 waves. Sized for a 1M context window per plan-location.md.

---

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| 1.1 | Add `apps_qna/integrations/spine_adapter.py` | New file (~120 lines) | Defines the `apps_qna` → `agentic_core` boundary cleanly. Follows `apps_shared` template (L0+L3+L5+L2+L6). | 4,000 | Todo |
| 1.2 | Route all card writes through UWG | `apps_qna/builder/card_pack_builder.py`, `apps_qna/builder/render.py` | Replace `Path.write_text` with `DurableWriteGateway.commit()`. Atomicity, audit trail, anti-bypass. | 5,000 | Todo |
| 1.3 | OTEL span instrumentation on build pipeline | `apps_qna/scripts/run_qna.py`, `apps_qna/builder/card_pack_builder.py` | Trace ingest → validation → render → write → manifest. Tags: slug, interviewer, route_count. | 4,000 | Todo |
| 1.4 | Wire lint output + self-eval to L6 ledger | `apps_qna/scripts/run_qna.py` (lint, self-eval subcmds), new `apps_qna/integrations/ledger_adapter.py` | Lint failures + self-eval drift → L6 evidence rows. ROUTER_DECISION-style markers. | 5,000 | Todo |
| 2.1 | Replace regex section-split with L1 retrieval-router for PDFs | `apps_qna/integrations/from_research_brief.py` | Searce-PDF-as-one-blob bug we hit today. Real chunking + reranker. | 9,000 | Todo |
| 2.2 | Glossary auto-extraction via L1 retrieval | `apps_qna/integrations/from_research_brief.py` | Currently hand-authored. Extract candidate terms via NER + retrieval scoring. | 7,000 | Todo |
| 2.3 | Likely-question generation seeded from interviewer hot-buttons | `apps_qna/integrations/wizard.py`, `apps_qna/integrations/from_research_brief.py` | Currently hand-authored 6+ questions per route. L1 retrieval over hot-buttons + role keywords. | 6,000 | Todo |
| 3.1 | STAR/RCA story drafting from ExperiencePoints | `apps_qna/integrations/from_apps_shared.py`, new `apps_qna/integrations/star_synthesis.py` | TBD content gap we hit today. L2 execution call grounded by master_resume_svp.json + JD. Author-Gate on variants. | 12,000 | Todo |
| 3.2 | Cross-exam depth anchor synthesis | `apps_qna/builder/render.py`, new `apps_qna/integrations/depth_anchor_synth.py` | Currently hand-authored via YAML extra_context. L2 with multi-ExperiencePoint synthesis. | 8,000 | Todo |
| 3.3 | Architecture content block authoring from repo's actual ADG | `apps_qna/integrations/architecture_synth.py` (new) | Currently hand-authored. L2 query against repo's own ADG → synthesized blocks. | 9,000 | Todo |
| 3.4 | L5 source-register policy gate | `apps_qna/integrations/spine_adapter.py`, validation extension | Block claims without source-register entries at safety plane. Currently LINT-2 (advisory); should be safety gate. | 6,000 | Todo |
| 4.1 | L0 NamespaceBandit for route selection | new `apps_qna/router/route_bandit.py` | Replace hand-ordered likely_questions with bandit over (interviewer_signal × route_id). Wilson CI gates. | 7,000 | Todo |
| 4.2 | Card paste-set selection bandit | `apps_qna/builder/card_pack_builder.py`, `apps_qna/router/paste_bandit.py` (new) | Currently hard-coded paste-set ordering. Bandit over (interviewer_signal × paste_budget). | 8,000 | Todo |
| 4.3 | Wilson CI + z + uplift gates on promotion of route/card defaults | `apps_qna/router/route_bandit.py` consumer | L6/promo router pattern — promote new defaults only with statistical evidence. | 5,000 | Todo |
| 5.1 | system_learning EpisodicEvent capture per interview | new `apps_qna/integrations/learning_adapter.py` | Post-interview feedback ("which questions actually got asked, which cards landed") → EpisodicEvent. | 8,000 | Todo |
| 5.2 | Flywheel promoter wires to next-pack defaults | `apps_qna/integrations/learning_adapter.py`, `apps_qna/router/*` | Cross-interview transfer (Searce/Vrinda → next consulting-VP role). | 9,000 | Todo |
| 5.3 | Cross-interview ProceduralPattern memory writeback | `apps_qna/integrations/learning_adapter.py` | "Hiring manager personas always probe X" → ProceduralPattern. Survives via mem_cleanup_stale protected types. | 8,000 | Todo |

---

## 6. Gap Register

| Gap | Severity | Resolution Phase |
|---|---|---|
| `apps_qna` not in latest ADG snapshot (created today, snapshot is from 06:58) | Medium | Wave 0: regen ADG before W1 entry |
| ADG snapshot uses `L_RUNTIME` / `L_SHARED` / `L_APP` virtual layers in addition to L0..L6 | Low | Documentation only — does not block any wave |
| `v_p0_write_bypass_uwg` schema needs apps_qna's writes to be ADG-detected as `writes_to` edges | Medium | Wave 1.2 introduces UWG calls; Wave 0 ADG regen will surface them |
| No existing precedent for "apps_qna-style document compiler on the spine" — apps_eval is closest analogue | Medium | Wave 1.1 spine_adapter.py mirrors apps_shared template; deviation justified per phase |
| `apps_underwriting_ai` only touches L5 + agentic_core_other (21.1% — borderline ON_SPINE) | Low | Out of scope; flag for separate audit |
| `tools/intake/extract_pdf_to_text.py` (authored today) is also off-spine | Trivial | Tools don't have to be on the spine; constitutional §31 governs SSOT folder routing only |

---

## 7. Author-Gate Entry Points

Per author-gate-enforcement.md, each Wave entry is an Author-Gate decision (`refactor_scope`):

- **W1 entry**: Confirm UWG path + OTEL instrumentation approach. Surface options if `DurableWriteGateway` API doesn't fit cleanly (alternative: lower-level `writes_to` adapter).
- **W2 entry**: Confirm L1 retrieval-router signature compatibility. Surface options if PDF chunking doesn't fit `RetrievalRouter` SLO budgets.
- **W3 entry**: Confirm L2 provider routing tier (deterministic vs. qwen vs. gemini_flash). Architecture decision worth surfacing.
- **W4 entry**: Confirm bandit cold-start strategy (uniform prior vs. seeded from existing hand-curated ordering).
- **W5 entry**: Confirm system_learning EpisodicEvent schema extension (new entity type vs. reusing existing).

Each entry emits `DECISION_CAPTURED:` per silent-marker invariant.

---

## 8. Verification Plan

| Gate | Command | Threshold |
|---|---|---|
| Spine coverage rises | `python -m tools.analysis.apps_spine_coverage --app apps_qna` | After W1: ≥10%. After W3: ≥30%. After W5: ≥40% (mirrors apps_shared profile). |
| Test suite | `python -m pytest apps_qna/tests -p no:xdist` | 94/94 pre-W1; ≥94 at every wave commit; new tests added for each new integration. |
| Lint invariants | `python -m apps_qna lint reports/qna/searce-applied-ai` | 6/6 clean across all waves. |
| ADG hotspot stability | `python tools/generate_full_adg.py` then re-query | New apps_qna nodes appear; no NEW P0/P1 violations introduced. |
| `v_p0_write_bypass_uwg` for apps_qna | direct SQLite query | After W1: 0 rows for `writer_file LIKE 'apps_qna/%'`. |
| `v_p1_not_on_spine` for apps_qna | direct SQLite query | After W3: ≤30% of apps_qna modules. After W5: ≤10%. |
| OTEL trace integrity | end-to-end smoke build with OTEL exporter on | Single trace covers ingest → render → write → lint with no orphan spans. |
| L6 promotion gate firing | run W4-onwards bandits in shadow mode | No promotion verdict without `wilson_lower≥0.60, z≥1.96, uplift>0, n≥30`. |

---

## 9. Rollback Strategy

Each wave is independently revertible:

- **W1 rollback**: `apps_qna/integrations/spine_adapter.py` becomes a no-op shim that calls `Path.write_text` directly. Builder still consumes the adapter; observable behavior unchanged.
- **W2 rollback**: `from_research_brief.py` retains the regex fallback under a feature flag `USE_L1_RETRIEVAL=false`.
- **W3 rollback**: STAR/RCA synthesizers default to TBD content (current state) when L2 unavailable.
- **W4 rollback**: Bandits default to deterministic hand-ordered selection (current state) when no calibration data exists.
- **W5 rollback**: system_learning hooks emit but do not consume — disabling consumption returns to W4 baseline.

No wave hard-couples to subsequent waves; each is independently shippable.

---

## 10. Out of Scope

- **Other apps_*** spine-coverage adjustments: `apps_underwriting_ai` is borderline (21.1%) — flag for separate audit, do not bundle.
- **`tools/intake/`**: not an apps_* surface; SSOT folder routing per §31 governs, not spine integration.
- **Master resume schema changes**: keep `apps_shared/data/master_resume_svp.json` shape; only the consumption path changes.
- **Pack output format changes**: Markdown card output stays identical at every wave; only the production pipeline changes.
- **Multi-interviewer panel mode**: existing feature, not enhanced by this plan.

---

## 11. References

- Upstream guidance: OpenAI BNY Eliza case study, Anthropic Claude Agent SDK, Rakesh Gohel "constraint-first / governance spine" (Tavily search 2026-04-30)
- Constitutional rules: §3 (no edits while exploring — informs wave entry gates), §22 (graph-layer primary driver — this plan's evidence section), §23 (canonical invariants — hotspot archetypes + 5 surfaces + layer multipliers), §29 (closed-loop router evidence — informs W4 bandit + W5 promotion)
- Sibling rules: `adg-graph-layer-enforcement.md`, `author-gate-enforcement.md`, `closed-loop-router-enforcement.md`, `memory-notion-writeback.md`
- Tooling: `tools/analysis/apps_spine_coverage.py` (this plan's scorecard), `tools/generate_full_adg.py` (regen between waves), `ops_scripts/ci/check_graph_layer_evidence.py` (validates this plan)
- Sibling apps as integration templates: `apps_shared/` (the canonical pattern — 54.1% spine coverage, all 7 layers touched, UWG + meta-learning), `apps_eval/` (closest analogue — also a build/eval-time tool, 29.9% spine coverage)
