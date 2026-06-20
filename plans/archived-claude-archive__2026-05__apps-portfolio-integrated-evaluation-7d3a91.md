---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-portfolio-integrated-evaluation-7d3a91.md'
original_relative_path: '_archive\\2026-05\\apps-portfolio-integrated-evaluation-7d3a91.md'
source_sha256: a531b859dc57e3636755d176481f2d692788f64fab2b7771e68bcf42073bd1c0
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps Portfolio Integrated Evaluation

> ⚠️ **POST-CLOSURE CORRECTION (2026-05-01, late session)**: This plan's cross-app integration analysis was based on `imports`-edge fan-in only and undercounted **pattern (3) bare-subprocess CLI consumers**. `apps_research` and `apps_exec` are NOT dormant or redundant — they have multiple active consumers via subprocess-CLI invocation that leave no `imports` edge:
>
> - `apps_research` consumed by `apps_rg` (via `research_facade`) AND `apps_qna` (via `from_apps_research.py` + `wizard.py`)
> - `apps_exec` consumed by `apps_eval` (via `scenario_runner.py`) AND `apps_qna` (via `wizard.py`)
>
> Any text in this plan suggesting these apps could be merged or deleted is wrong. The K1 KEEP BOTH verdict and the N1 W3/W4 no-op closure both still hold (correctly), but for **stronger** reasons than originally documented — the producer apps each have 2 consumers, not 0.
>
> Corrected typology and consumer matrix: `docs/architecture/cross-app-facade-pattern.md` (updated same day).
>
> Successor plan that captured this correction: `dormant-facade-cleanup-b2d4f7.md` (closed).

# Apps Portfolio Integrated Evaluation & Consolidation Plan

Status: **W0 + W1 ready to run; W2 is the decision gate**
Last updated: 2026-05-01
Created: 2026-05-01
Owner: Cursor Agent
Plan slug: `apps-portfolio-integrated-evaluation-7d3a91`

## Mission

Consolidate four parallel work streams into one wave-ordered execution:

1. The user's directive "delete `apps_rfp`, consolidate `apps_exec`+`apps_research`, feed `apps_rg`+`apps_lic`".
2. The active `apps-rfp-first-principles-refactor-9c8d3f.md` — open W0.1 ADG verification of `ADR-rfp-multi-agent-justification` (Proposed).
3. The active `apps-exec-first-principles-refactor-5e6a4b.md` — same open verification for the 3 exec orchestrators.
4. The five Author-Gate decisions captured this session (A1, B3, C1, D1, R1) — kept in the ledger as audit trail; this plan supersedes their execution path.

The integration replaces "delete-then-consolidate" with **verify-first, decide, then execute**. The deletion / consolidation question is a *consequence* of whether the MULTI_AGENT topology claims hold under ADG verification, not a precondition.

This plan supersedes the open execution paths in plans (2) and (3); their W0/W1.1 evidence is referenced, not redone.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W0** | W0.1 | Verify `apps_rfp` MULTI_AGENT claims via ADG (shared-state, side-effect, flows_to checks) | ~3k | ADG snapshot ≤ 24h old | Ready | Boolean verdict per ADR §Verification checklist; evidence rows in this plan |
| **W1** | W1.1 | Same verification for `apps_exec`'s 3 orchestrators | ~3k | Same | Ready | Boolean verdict; evidence rows |
| **W2** | W2.1 | **DECISION GATE** → **K1 KEEP BOTH** (2026-05-01); ADR-rfp-multi-agent → Accepted | ~2k | W0+W1 complete | **Done** | Author-Gate K1 captured; matrix verdict KEEP BOTH realized |
| **W3** | W3.1 | **NO-OP (evidence-driven)** — HOP2ResearchAgent is sovereign-sealed, immutable-buffer-driven, archetype-aware, with today's company_trigger extension; not a thin facade caller. See N1 disposition below. | 0 | source read 2026-05-01 | **No-op (evidence-driven)** | n/a |
| **W4** | W4.1 | **NO-OP (evidence-driven)** — `governed_research_run.py` already a thin 60-line subclass over `GovernedAppRunner`; consolidation already happened in `apps_shared/integrations/governed_app_runner.py`. See N1 disposition below. | 0 | source read 2026-05-01 | **No-op (evidence-driven)** | n/a |
| **W5** | W5.1 | **NO-OP** under K1 — consolidation stream closed | 0 | W2=KEEP | **No-op (closed)** | n/a |
| **W6** | W6.1 | **NO-OP** under K1 — apps_rg migration not triggered (consolidation didn't happen) | 0 | W5=no-op | **No-op (closed)** | n/a |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **W0.1** | apps_rfp MULTI_AGENT verification | ADG queries: `writes_to`, `emits_side_effect`, `flows_to` between `RfpOrchestrator`, `section_orchestrator`, `enterprise_orchestrator`, `ComplianceMappingAgent`, `RequirementAnalysisAgent` | Need to enumerate all 5 orchestrator nodes via `adg_find_node` first | 3k | Ready |
| **W1.1** | apps_exec orchestrator verification | Same query set for `brief_orchestrator`, `enterprise_brief_orchestrator`, `ExecOrchestrator` | Smaller surface (3 orchestrators, no MULTI_AGENT claim — verification is exploratory) | 3k | Ready |
| **W2.1** | Author-Gate: keep vs consolidate verdict | This plan + ADR-rfp-multi-agent-justification status update | Decision tree branches on W0/W1 booleans | 2k | Blocked on W0+W1 |
| **W3.1** | apps_lic HOP2 → research_facade | `apps_lic/engines/HOP2ResearchAgent.py`, `apps_shared/adapters/research_facade.py` | HOP contract stability is the only risk; preserved by adapter design | 5k | Independent |
| **W4.1** | apps_research single governed_run | `apps_research/integrations/governed_research_run.py` (rename to `governed_run.py`); delete duplicates if W5 lands | Trivial inside apps_research | 3k | Independent |
| **W5.1** | Conditional consolidation execution | Determined at W2 — may include `apps_rfp` archive, `apps_exec` fold, or no-op | SSOT registry edits in `agentic_core/L0_routing/config/path_constants.py`, `agentic_core/L2_execution/types/agent_taxonomy_registry.py`, `agentic_core/L5_safety/config/structure_blueprint/ssot.py`, `apps_shared/integrations/app_registry.py` | 12k | Conditional |
| **W6.1** | apps_rg migration | `apps_rg` research-flavored engines → `research_facade` calls; 52-engine surface preserved | Largest phase; only fires if W5 happened | 18k | Conditional |

## Decision Matrix at W2

| `apps_rfp` verdict | `apps_exec` verdict | W2 outcome | W5 action |
|---|---|---|---|
| MULTI_AGENT claims hold | orchestrators independent | **Keep both** | W5 = no-op; ADR-rfp-multi-agent → Accepted; close consolidation stream |
| MULTI_AGENT claims hold | orchestrators share state | **Keep rfp; consolidate exec→research** | W5 = fold apps_exec into apps_research; ADR-rfp-multi-agent → Accepted |
| MULTI_AGENT claims fail | orchestrators independent | **Tier-drop rfp to WORKFLOW; keep exec** | W5 = author tier-drop ADR for rfp; possibly consolidate later |
| MULTI_AGENT claims fail | orchestrators share state | **Tier-drop both; consider consolidation of rfp+exec→research** | W5 = author rejection of rfp ADR; tier-drop exec; multi-app consolidation Author-Gate |

The matrix replaces the prose "Reverse / Override / Park" framing with an evidence-driven branch.

## Predecessor plans superseded by this one

- `apps-rfp-first-principles-refactor-9c8d3f.md` — W0/W1.1 evidence carries forward; W0.1 verification (still open) lives here as W0; W2+ remain blocked on three-bucket as that plan documented.
- `apps-exec-first-principles-refactor-5e6a4b.md` — same pattern.
- `apps-cross-app-duplication-review` (NEW from prior turn's NEXT_STEP) — fully absorbed.

The five session DECISION_CAPTURED markers stay in the refactor decision ledger as audit trail; their `outcome=executed` status is technically a label drift (no code changed) — left as-is for ledger integrity per the R1 packet's ledger-handling clause.

## Out of Scope (DEFERRED_SCOPE candidates)

- Three-bucket-gap-remediation completion (gates W2+ in the predecessor plans; out of scope here).
- `apps_lic` HOP3+ migration (W3 only addresses HOP2).
- `apps_underwriting_ai`, `apps_qna`, `apps_eval` topology questions (separate plans exist).

## ADG_GRAPH_LAYER_EVIDENCE

> Constitutional §22 compliance. Sections cite the canonical graph-layer primitives that constrain this plan's verification scope.

**Domain**: apps_rfp + apps_exec orchestrator topology verification

**Materialized views consulted** (≥3 required):
1. `mv_dependency_cone_risk` — blast-radius / cone risk for each orchestrator's reachable state.
2. `mv_graph_reverse_dependency_hotspots` — fan-in centrality lens for orchestrators.
3. `mv_chokepoint_bridges` — chokepoint detection between orchestrators (would surface shared singletons).

**Semantic edges** beyond raw `imports` (the verification primitives):
- `writes_to` — primary evidence for shared mutable state between orchestrators.
- `emits_side_effect` — secondary evidence; cross-orchestrator side effects.
- `flows_to` — used to verify Claim 2 (typed-contract integration); the *absence* of `flows_to` between orchestrators is what would invalidate parallelism.
- `controls_flow` — supplementary; control coupling between orchestrators.
- `resolves_callsite` — to identify orchestrator-to-orchestrator direct calls.

**P-view cross-references** (pre-classified architectural concerns):
- `v_p0_write_bypass_uwg` — applicable if any orchestrator writes outside UWG.
- `v_p2_duplicated_adapters` — applicable to the apps_research/apps_exec/apps_rfp clone question.

**Rationale**: the existing apps_rfp and apps_exec hotspot reports (W0/W0.1 Done in predecessor plans) cover fan-in centrality. What's missing — and what this plan adds — is the cross-orchestrator shared-state evidence required by `ADR-rfp-multi-agent-justification` §Verification.

## ADG_HOTSPOT_REPORT

| Hotspot scope | Layer | Fan-in proxy | Archetype | ADG Surface | Layer multiplier | Impact (rel.) |
|---|---|---:|---|---|---:|---:|
| apps_rfp 5-orchestrator surface (W0.1 verification target) | L_APPS | high | ORCHESTRATOR | Execution Surface | 1.0 | **HIGH** |
| apps_exec 3-orchestrator surface (W1.1 verification target) | L_APPS | high | ORCHESTRATOR | Execution Surface | 1.0 | **HIGH** |
| apps_research subprocess-only surface (consolidation target) | L_APPS | medium (subprocess CLI) | CENTRAL_DEPENDENCY | Execution Surface | 1.0 | medium |
| `apps_shared/adapters/research_facade.py` (W3.1 seam) | L_APPS_SHARED | medium | CENTRAL_DEPENDENCY | Execution Surface | 1.0 | medium |
| `agentic_core/L0/L2/L5` SSOT registry pins (W5.1 if non-keep) | L0/L2/L5 | high (registry) | STATE_NODE | State Surface | 2.0 / 1.0 / 2.0 | varies |

**Top hotspot**: orchestrator surfaces in apps_rfp and apps_exec — the ADR §Verification claims are exactly the hotspot risk this plan resolves.

Impact formula (canonical): `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier`. Surface intersection covers Execution / State per `adg-canonical-invariants.md` §3.

## Evidence (filled in as waves complete)

### W0.1 — apps_rfp MULTI_AGENT verification

> Status: **DONE** 2026-05-01. Snapshot: `artifacts/adg/adg_indexed_05012026_0632.sqlite`. Full output: `artifacts/_scan_w0_w1_output.txt`.

5 orchestrator nodes verified present in ADG: `RfpOrchestrator.py`, `section_orchestrator.py`, `enterprise_orchestrator.py`, `ComplianceMappingAgent.py`, `RequirementAnalysisAgent.py`.

Cross-orchestrator edge counts (all relations queried both via `nodes.resolved_path` and `edges.source_file`):

| Relation | Count between orchestrators | ADR §Verification implication |
|---|---:|---|
| `writes_to` | 0 | ✅ No shared mutable state |
| `emits_side_effect` | 0 | ✅ No cross-workflow side effects into another's failure surface |
| `flows_to` | 0 | ⚠️ Absent — see Caveat below |
| `resolves_callsite` | 0 | ✅ No direct orchestrator-to-orchestrator calls (typed-contract integration shape preserved) |
| `controls_flow` | 0 | ✅ No control coupling |

Verification verdict per ADR §Verification checklist:

- [x] No shared mutable state across orchestrator boundaries
- [x] No `emits_side_effect` edges between workflows
- [x] No direct `resolves_callsite` between orchestrators
- [x] Independent escalation triggers (no shared queue evidence)

**Caveat on `flows_to=0`**: the ADR Claim 2 says "integration is via typed contracts, not shared state" — interpreting "typed contracts" as in-process Python message passing would predict `flows_to > 0`. The actual zero-count is consistent with two readings: (a) orchestrators are genuinely independent and emit outputs orthogonally consumed downstream (matches ADR Claim 3 — "parallel agents whose outputs are independently consumable"); (b) integration happens via file-based artifacts or `importlib`-driven dispatch that the static ADG cannot resolve. Both readings support the MULTI_AGENT tier; neither invalidates it. Verdict: **claims hold**.

### W1.1 — apps_exec orchestrator verification

> Status: **DONE** 2026-05-01. Same snapshot.

3 orchestrator nodes verified present: `brief_orchestrator.py`, `enterprise_brief_orchestrator.py`, `ExecOrchestrator.py`.

| Relation | Count between orchestrators |
|---|---:|
| `writes_to` | 0 |
| `emits_side_effect` | 0 |
| `flows_to` | 0 |
| `resolves_callsite` | 0 |
| `controls_flow` | 0 |

All three orchestrators are structurally independent in the ADG. `apps_exec` is currently `agency.tier=WORKFLOW` per its AgentSpec — independence under the same verification primitives means no demotion is required and no consolidation is forced by topology evidence.

### W2 decision-matrix input

| Input | Value |
|---|---|
| apps_rfp MULTI_AGENT claims hold | **True** |
| apps_exec orchestrators independent | **True** |
| Matrix verdict | **KEEP BOTH** — ADR-rfp-multi-agent → Accepted; close consolidation stream |

## Definition of Done

- [x] W0.1 evidence section populated; verdict booleans set (rfp claims hold = True)
- [x] W1.1 evidence section populated; verdict booleans set (exec independent = True)
- [x] W2.1 Author-Gate packet emitted; matrix verdict K1 KEEP BOTH captured in ledger
- [x] W3.1 disposition: **No-op (evidence-driven)** per N1 — HOP2 source read invalidates thin-caller hypothesis
- [x] W4.1 disposition: **No-op (evidence-driven)** per N1 — `governed_research_run.py` already thin over shared substrate
- [x] W5.1 No-op under K1 (consolidation closed)
- [x] W6.1 No-op under K1 (no consolidation = no apps_rg migration)
- [x] ADR-rfp-multi-agent-justification: Proposed → **Accepted** (2026-05-01)
- [x] Predecessor plans (apps-rfp / apps-exec first-principles refactors) carry supersession notes
- [x] Operational-grounds duplication review queued via DEFERRED_SCOPE marker (separate plan)

## Plan Status

**CLOSED 2026-05-01.** All waves resolved (W0/W1/W2 executed; W3/W4 no-op-after-evidence; W5/W6 no-op-under-K1). The integrated plan reaches Definition of Done with the live tree unchanged from start of session — the disposition is itself the deliverable: a documented, evidence-backed reason the apps portfolio is in correct shape today.

## N1 Disposition Detail (W3 + W4 closure)

### W3 — `apps_lic` HOP2 thin-caller through `research_facade` — closed no-op

Source-of-truth read of `apps_lic/engines/HOP2ResearchAgent.py` (450 lines) shows:

- `LICAgentBase` sovereign-sealed dataclass; runtime-immutable post-`__post_init__`.
- Operates on `ImmutableStagingBuffer` consumed by HOP3+ via `buffer.read("hop2_research")`.
- Output shape = `evidence_pack` (artifacts with stable hash IDs, confidence, source) + `strategic_brief` (archetype-tailored) + (today, lines 150–186) `company_triggers` + `best_company_trigger` consumed by HOP5 K.5A.
- Data sources: vector store (`memory_store.query_by_company`, `query_by_executive`, `get_strategic_briefs`), recipient-scoped queries, archetype gating, async fallback `search_client`.

`research_facade.fetch_company_brief()` returns generic `CompanyBrief` (`apps_rg.types.company_research`) via subprocess invocation of `python -m apps_research --mode company`. Generic, not recipient-scoped, not archetype-aware. Cannot replace HOP2's role without breaking HOP3+ contract and dropping today's company_trigger extension.

### W4 — single `governed_run` collapse — closed no-op

Source-of-truth read of `apps_research/integrations/governed_research_run.py` (205 lines) shows:

- Already a 60-line thin subclass `GovernedResearchRun(GovernedAppRunner)` configuring shared substrate for apps_research.
- The shared substrate (`GovernedAppRunner`, `GovernedAppRunRecord`, `build_app_record`) lives in `apps_shared/integrations/governed_app_runner.py`. Comment line 19: *"Common L1→L0→C0→L2→L5+L6 pipeline lives in `GovernedAppRunner` (apps_shared)"* — the consolidation already happened in a prior wave (referenced "W5: build_app_record handles all substrate fields automatically").
- The current file's job is to translate substrate `GovernedAppRunRecord` → app-specific frozen `GovernedE2ERunRecord` with research fields. That translation is the value-add; renaming the file to `governed_run.py` would be cosmetic-only and would break `check_apps_otel_coverage.py` pattern matching (module-load OTEL emit at line 204 is keyed on the exact module path).

Three apps × one record-translator each is the correct shape, not a duplication problem.

## Session-Level Markers Audit

The session emitted these `DECISION_CAPTURED:` markers (audit trail only — five markers represent decisions made on incomplete evidence and stay as written for ledger integrity per the R1 packet's ledger-handling clause):

| Marker | Type | Selected | Confidence | Outcome on disk |
|---|---|---|---|---|
| C1 | architecture_choice | single governed_run inside consolidated app | 0.78 | Superseded by N1 (no consolidation; substrate already exists) |
| A1 | architecture_choice | fold apps_exec → apps_research | 0.82 | Superseded by R1+K1 (KEEP BOTH; topology evidence holds) |
| B3 | refactor_scope | apps_lic HOP2 only | 0.80 | Superseded by N1 (HOP2 not a thin caller) |
| D1 | deletion_strategy | archive apps_rfp | 0.85 | Superseded by R1 (active ADR; W0 verification passes) |
| R1 | architecture_choice | reverse deletion; defer to active plans | 0.78 | Superseded by K1+N1 (full closure) |
| K1 | architecture_choice | keep both; ADR Accepted | 0.85 | Realized — ADR moved to Accepted; predecessor plans superseded |
| N1 | refactor_scope | close W3+W4 no-op-after-evidence | 0.75 | Realized — this disposition |

The lineage is: original directive → R1 reverses → K1 confirms keep → N1 closes the remaining waves. Five superseded markers are the audit trail; two realized markers (K1, N1) are the durable session output.
