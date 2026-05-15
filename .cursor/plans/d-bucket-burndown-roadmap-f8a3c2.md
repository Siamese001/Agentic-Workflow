# D-Bucket Burndown — Multi-Session Execution Roadmap

Generated: 2026-05-02  ·  Status: Live  ·  No-code deliverable  ·  Companion to `d-bucket-burndown-e4f2c9.md`

> **CORRECTION 2026-05-02 (post-ADG-verify pass)**: The "~48 sessions" estimate
> below is **naive per-row token math** that ignored ADG-informed scope sizing.
> Real estimate is **~10-15 focused sessions**, broken down:
>
> - Batch-scriptable single-row tracker work (lifecycle-pairs codemod,
>   test-harness smoke generation, write-sovereignty triage script): **~4 sessions**
> - Adoption propagation (e.g., `seal_step` autowrap recipe to 5 engines): **~2 sessions**
> - ADR + docs authorship batch (ADR-081 + audit reports): **~2 sessions**
> - `l6-gravity-hybrid` W2-W4 completion (verified by W1 demo this session): **~2 sessions**
> - Genuine P1/P2 architectural remainder: **~3-5 sessions**
>
> Why the original was wrong: many "P1" rows track batch work (e.g.,
> `142 lifecycle leaks` is 1 codemod, not 142 fixes). Several rows are
> already partially executed and only need ADG-regen verification + Evidence
> update + Status flip (proven by W1 today: `[P1] 17 cross-layer authority
> breaches` was actually ~2 sessions of remaining work, not 17).
>
> The W1 packet below remains accurate as the recommended starting point.
> The W2-W4 sizing tables overstate effort by ~3x. Treat them as a
> conservative ceiling.

## Purpose

Per-wave execution packets for the 114 D-bucket Notion backlog rows. Each wave is sized for cross-session pickup: **one human-ready entry criterion, concrete ordered steps, files in scope, exit criterion, row-closure list**. 

**Hard invariant**: a single Cursor Agent turn cannot execute a wave. Each wave spans N sessions. Use this roadmap to resume cleanly between sessions.

## Wave Structure (canonical from `d-bucket-burndown-e4f2c9`)

| Wave | Row Count | Max Impact | Estimated Sessions | Parent Plans |
|---|---:|---:|---:|---|
| W1 | 1 | 677 | ~1.0 sessions (@ 2-4 hr each) | l6-gravity-hybrid-7c4e2a.md |
| W2 | 17 | 444 | ~11.0 sessions (@ 2-4 hr each) | gap-closure-test-impl-b77a11.md, adg-architectural-p0-violations-cleanup-, phase-b-blocker-burndown-a8c4f1.md |
| W3 | 19 | 361 | ~10.5 sessions (@ 2-4 hr each) | audit-uncovered-gates-and-remediation-62, repo-tech-debt-wave1-b3c8d1.md, l0-routing-calibration-gap-audit-b3c9d4.... |
| W4 | 77 | 229 | ~26.0 sessions (@ 2-4 hr each) | anthropic-rag-gaps-7f3c2a.md, windsurf-maintenance-2026-q2-0f3564.md, prompt-assembly-best-practices-gap-b4e1c... |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W1.l6-gravity-hybrid-7c4e2a.md | 1-row sub-wave | l6-gravity-hybrid-7c4e2a.md (parent plan exists) | bands={'P1': 1}, max impact 677 | 3000 | Draft |
| W2.gap-closure-test-impl-b77a11.m | 12-row sub-wave | gap-closure-test-impl-b77a11.md (parent plan exists) | bands={'P1': 2, 'P2': 9, 'P3': 1}, max impact 444 | 36000 | Draft |
| W2.adg-architectural-p0-violation | 2-row sub-wave | adg-architectural-p0-violations-cleanup-bced9c.md (parent plan exists) | bands={'P1': 1, 'P3': 1}, max impact 390 | 6000 | Draft |
| W2.phase-b-blocker-burndown-a8c4f | 3-row sub-wave | phase-b-blocker-burndown-a8c4f1.md (parent plan exists) | bands={'P1': 3}, max impact 384 | 9000 | Draft |
| W3.audit-uncovered-gates-and-reme | 2-row sub-wave | audit-uncovered-gates-and-remediation-627368.md (parent plan exists) | bands={'P1': 1, 'P2': 1}, max impact 361 | 6000 | Draft |
| W3.repo-tech-debt-wave1-b3c8d1.md | 6-row sub-wave | repo-tech-debt-wave1-b3c8d1.md (parent plan exists) | bands={'P1': 2, 'P2': 2, 'P3': 2}, max impact 352 | 18000 | Draft |
| W3.l0-routing-calibration-gap-aud | 5-row sub-wave | l0-routing-calibration-gap-audit-b3c9d4.md (parent plan exists) | bands={'P1': 1, 'P2': 2, 'P3': 2}, max impact 336 | 15000 | Draft |
| W3.runtime-adg-coverage-audit-4f7 | 1-row sub-wave | runtime-adg-coverage-audit-4f7a21.md (audit) | NEW:runtime-adg-trace-binding-remediation (remediation — not yet drafted) (parent plan MISSING ON DISK) | bands={'P2': 1}, max impact 297 | 3000 | Draft |
| W3.c0-context-assembly-best-pract | 2-row sub-wave | c0-context-assembly-best-practices-b7c3a1.md (parent plan exists) | bands={'P2': 2}, max impact 254 | 6000 | Draft |
| W3.NEW:adg-mcp-reopen-hardening ( | 3-row sub-wave | NEW:adg-mcp-reopen-hardening (to be created) (parent plan MISSING ON DISK) | bands={'P2': 3}, max impact 254 | 9000 | Draft |
| W4.anthropic-rag-gaps-7f3c2a.md | 2-row sub-wave | anthropic-rag-gaps-7f3c2a.md (parent plan exists) | bands={'P2': 1, 'P3': 1}, max impact 229 | 6000 | Draft |
| W4.windsurf-maintenance-2026-q2-0 | 1-row sub-wave | windsurf-maintenance-2026-q2-0f3564.md (parent plan exists) | bands={'P2': 1}, max impact 220 | 3000 | Draft |
| W4.prompt-assembly-best-practices | 14-row sub-wave | prompt-assembly-best-practices-gap-b4e1c2.md (parent plan exists) | bands={'P2': 3, 'P3': 1, '--': 10}, max impact 204 | 42000 | Draft |
| W4.adg-three-bucket-unified-c4f8e | 5-row sub-wave | adg-three-bucket-unified-c4f8e2.md (parent plan exists) | bands={'P3': 4, 'P5': 1}, max impact 148 | 15000 | Draft |
| W4.sc1-audit-to-enforce-promotion | 1-row sub-wave | sc1-audit-to-enforce-promotion-b4e9d7.md (parent plan exists) | bands={'P3': 1}, max impact 144 | 3000 | Draft |
| W4.notion-schema-refactor-cleanup | 8-row sub-wave | notion-schema-refactor-cleanup-9f2e4a.md (parent plan exists) | bands={'P3': 2, 'P5': 1, '--': 5}, max impact 130 | 24000 | Draft |
| W4.scorer-otel-autosource-layer-b | 4-row sub-wave | scorer-otel-autosource-layer-b-c5e4d1.md (parent plan exists) | bands={'P3': 3, 'P4': 1}, max impact 106 | 12000 | Draft |
| W4.chromadb-bge-retrieval-hardeni | 1-row sub-wave | chromadb-bge-retrieval-hardening-e9aa09.md (parent plan exists) | bands={'P3': 1}, max impact 100 | 3000 | Draft |
| W4.fortknox-100pct-static-runtime | 1-row sub-wave | fortknox-100pct-static-runtime-gap-9a3d4f.md (parent plan exists) | bands={'P5': 1}, max impact 50 | 3000 | Draft |
| W4.decision-router-policy-tables- | 1-row sub-wave | decision-router-policy-tables-b3a4d2.md (parent plan exists) | bands={'--': 1}, max impact 0 | 3000 | Draft |
| W4.adg-truth-expansion-r5w1-a8f3c | 1-row sub-wave | adg-truth-expansion-r5w1-a8f3c2 (parent plan MISSING ON DISK) | bands={'--': 1}, max impact 0 | 3000 | Draft |
| W4.notion-backlog-schema-refactor | 1-row sub-wave | notion-backlog-schema-refactor-7c3d9e (parent plan MISSING ON DISK) | bands={'--': 1}, max impact 0 | 3000 | Draft |
| W4.next-step-gate-ci-workflow-873 | 1-row sub-wave | next-step-gate-ci-workflow-8733a6 (parent plan MISSING ON DISK) | bands={'--': 1}, max impact 0 | 3000 | Draft |
| W4.adg-tree-sitter-parser-explora | 1-row sub-wave | adg-tree-sitter-parser-exploration-b1c517.md (parent plan exists) | bands={'P4': 1}, max impact 0 | 3000 | Draft |
| W4.mcp-serial-defense-l2l5-7d4f1a | 1-row sub-wave | mcp-serial-defense-l2l5-7d4f1a.md (parent plan exists) | bands={'--': 1}, max impact 0 | 3000 | Draft |
| W4.adg-cascading-ratchet-defer-ex | 1-row sub-wave | adg-cascading-ratchet-defer-exit-a41828.md (parent plan exists) | bands={'P4': 1}, max impact 0 | 3000 | Draft |
| W4.notion-backlog-human-scoring-e | 5-row sub-wave | notion-backlog-human-scoring-e7a941.md (parent plan exists) | bands={'P3': 5}, max impact 0 | 15000 | Draft |
| W4.shadow-learning-bestpractice-g | 2-row sub-wave | shadow-learning-bestpractice-gap-7b3e4c.md (parent plan exists) | bands={'--': 2}, max impact 0 | 6000 | Draft |
| W4.runtime-adg-tier3-broader-adop | 1-row sub-wave | runtime-adg-tier3-broader-adoption-8f2d1c.md (parent plan exists) | bands={'P5': 1}, max impact 0 | 3000 | Draft |
| W4.adg-wiring-ci-dispatcher-harde | 5-row sub-wave | adg-wiring-ci-dispatcher-hardening-b2f4a1.md (parent plan exists) | bands={'P1': 1, 'P2': 2, 'P3': 2}, max impact 0 | 15000 | Draft |
| W4.judge-surface-harmonization-b9 | 1-row sub-wave | judge-surface-harmonization-b9d3a7.md (parent plan exists) | bands={'P2': 1}, max impact 0 | 3000 | Draft |
| W4.llm-judge-hardening-followups- | 1-row sub-wave | llm-judge-hardening-followups-f2c8e1.md (parent plan exists) | bands={'P1': 1}, max impact 0 | 3000 | Draft |
| W4.llm-as-judge-hardening-anthrop | 1-row sub-wave | llm-as-judge-hardening-anthropic-e7b1a4.md (parent plan exists) | bands={'P1': 1}, max impact 0 | 3000 | Draft |
| W4.moe-agentic-architecture-d4e9a | 1-row sub-wave | moe-agentic-architecture-d4e9a2.md (parent plan exists) | bands={'P1': 1}, max impact 0 | 3000 | Draft |
| W4.prompt-assembly-few-shot-exemp | 1-row sub-wave | prompt-assembly-few-shot-exemplars-9c4e2b.md (parent plan exists) | bands={'P2': 1}, max impact 0 | 3000 | Draft |
| W4.prompt-categories-coverage-aud | 1-row sub-wave | prompt-categories-coverage-audit-b8f5d3.md (parent plan exists) | bands={'P1': 1}, max impact 0 | 3000 | Draft |
| W4.cot-reflexion-self-consistency | 1-row sub-wave | cot-reflexion-self-consistency-config-7a3f1c.md (parent plan exists) | bands={'P1': 1}, max impact 0 | 3000 | Draft |
| W4.hybrid-search-adg-seed-rerank- | 1-row sub-wave | hybrid-search-adg-seed-rerank-c58e21.md (parent plan exists) | bands={'P3': 1}, max impact 0 | 3000 | Draft |
| W4.ssot-violations-sweep-29caf4.m | 2-row sub-wave | ssot-violations-sweep-29caf4.md (parent plan exists) | bands={'P3': 1, 'UNSCORED': 1}, max impact 0 | 6000 | Draft |
| W4.p2-burndown-wave-9e4c17.md | 2-row sub-wave | p2-burndown-wave-9e4c17.md (parent plan exists) | bands={'P3': 2}, max impact 0 | 6000 | Draft |
| W4.ssot-consolidation-cleanup-b7f | 8-row sub-wave | ssot-consolidation-cleanup-b7f3a1.md (parent plan exists) | bands={'P3': 8}, max impact 0 | 24000 | Draft |

## Global Entry Checklist (applies to every wave)

Before starting ANY wave, verify:

- [ ] `adg_health` returns green (per §13 MCP green light)
- [ ] Latest ADG snapshot present under `artifacts/adg/adg_indexed_*.sqlite` (regenerate if >24h old)
- [ ] No uncommitted work on another wave's scope (`git status` clean OR scoped)
- [ ] Parent plan for the sub-wave exists on disk (if MISSING: either recreate or flip row → Retired before starting)
- [ ] `post_cursor_agent_adg_audit.py` violations log is empty OR acknowledged

## Global Exit Checklist (applies to every wave)

Before declaring a wave complete:

- [ ] All sub-wave rows flipped to `Completed` with Evidence field pointing at commit SHA or PR
- [ ] ADG regenerated; no new P0/P1 violations introduced (see `adg_violations` diff)
- [ ] Tests pass at the tier of the change (scoped pytest for T2, full-suite signal for T3)
- [ ] `post_cursor_agent_adg_audit.py` clean run
- [ ] Parent plan's wave status table updated (if plan still Live)


## W1 Execution Packet (1 rows, max impact 677, ~1.0 sessions (@ 2-4 hr each))

**Intent**: Close the single highest-impact remaining row in one focused session.

### W1.1 — `l6-gravity-hybrid-7c4e2a.md` (✓ exists, 1 rows, bands={'P1': 1})

**Entry**: parent plan `l6-gravity-hybrid-7c4e2a.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/l6-gravity-hybrid-7c4e2a.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `35027693-f55` | P1 | 677 | [P1] 2_authority_boundary P0 17 cross-layer authority breach | PARTIAL EXECUTION 2026-05-01: W1.P1 DONE (agentic_core/_shared/ namespace + infe |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.


## W2 Execution Packet (17 rows, max impact 444, ~11.0 sessions (@ 2-4 hr each))

**Intent**: Three related plans — runtime-cert thread (`gap-closure-test-impl`), architectural P0 burndown, phase-b blockers. Do NOT begin until Phase D.5 closeout is confirmed per stored memory (runtime-cert rows are explicitly gated on it).

### W2.1 — `gap-closure-test-impl-b77a11.md` (✓ exists, 12 rows, bands={'P1': 2, 'P2': 9, 'P3': 1})

**Entry**: parent plan `gap-closure-test-impl-b77a11.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/gap-closure-test-impl-b77a11.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34e27693-f55` | P1 | 444 | [P1] L4 blueprint policy version migration tests (00B.9) | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-26 — Cursor Agent to fill o |
| `34e27693-f55` | P1 | 405 | [P1] L3-L2 step handoff checkpoint resume tests (03.9) | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-26 — Cursor Agent to fill o |
| `34e27693-f55` | P2 | 287 | L2 sequencer orchestrator contract tests (04.0) | RESOLVED 2026-04-26: L2 sequencer orchestrator contracts (spec 04.0) implemented |
| `34e27693-f55` | P2 | 286 | [P2] L2 StateDiffCandidate mutation intent tests (04.9) | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-26 — Cursor Agent to fill o |
| `34e27693-f55` | P2 | 277 | [P2] PA authority red-team slot verification tests (PA.8) | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-26 — Cursor Agent to fill o |
| `34e27693-f55` | P2 | 254 | [P2] PTC v2 sandbox hardening tests (04.7) | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-26 — Cursor Agent to fill o |
| `34e27693-f55` | P2 | 240 | [P2] L2 verify-then-execute local critique tests (04.10) | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-26 — Cursor Agent to fill o |
| `35027693-f55` | P2 | 185 | [P2] G2_seam_test_export_coherence P1 6 test export coherenc | [REROUTE 2026-04-30] Re-routed from orphan slug `adg-seam-test-coherence-cleanup |
| `34e27693-f55` | P2 | 161 | [P2] E2E fixtures replay harness commands tests (99.10) | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-26 — Cursor Agent to fill o |
| `34e27693-f55` | P2 | 161 | [P2] E2E mutation testing boundary faults tests (99.9) | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-26 — Cursor Agent to fill o |
| `34e27693-f55` | P2 | 160 | [P2] L6 memory promotion interface tests (06.9) | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-26 — Cursor Agent to fill o |
| `34b27693-f55` | P3 | 124 | [P3] W1 W1.1 — replace deleted test_pytest_server with tests | [REROUTE 2026-04-30] Re-routed from orphan slug `pytest-server-functional-tests` |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W2.2 — `adg-architectural-p0-violations-cleanup-bced9c.md` (✓ exists, 2 rows, bands={'P1': 1, 'P3': 1})

**Entry**: parent plan `adg-architectural-p0-violations-cleanup-bced9c.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/adg-architectural-p0-violations-cleanup-bced9c.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `35027693-f55` | P1 | 390 | [P1] C2_l5_bypass_pview P0 L5 safety plane bypass | [REROUTE 2026-04-30] Re-routed from orphan slug `adg-l5-bypass-cleanup` (no plan |
| `34c27693-f55` | P3 | 0 | [P3] Remediate the 3 SC-1 + 2 P0 architectural violations su | Success: TBD — Cursor Agent suggested follow-up; fill on execution start. \| Blocking |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W2.3 — `phase-b-blocker-burndown-a8c4f1.md` (✓ exists, 3 rows, bands={'P1': 3})

**Entry**: parent plan `phase-b-blocker-burndown-a8c4f1.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/phase-b-blocker-burndown-a8c4f1.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `35027693-f55` | P1 | 384 | [P1] 4_capability_egress P0 outbound calls bypass capability | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-28 — Cursor Agent to fill o |
| `35027693-f55` | P1 | 319 | [P1] v_p0_write_bypass_uwg P0 state write does not flow thro | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-28 — Cursor Agent to fill o |
| `35027693-f55` | P1 | 319 | [P1] C1_uwg_bypass_pview P0 single row UWG bypass pview | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-28 — Cursor Agent to fill o |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.


## W3 Execution Packet (19 rows, max impact 361, ~10.5 sessions (@ 2-4 hr each))

**Intent**: Mid-impact cluster spanning audit, tech-debt, routing calibration, C0 assembly, runtime ADG coverage, and a to-be-created ADG-MCP hardening plan. Start with the smallest sub-wave (fewest rows + plan exists on disk).

### W3.1 — `audit-uncovered-gates-and-remediation-627368.md` (✓ exists, 2 rows, bands={'P1': 1, 'P2': 1})

**Entry**: parent plan `audit-uncovered-gates-and-remediation-627368.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/audit-uncovered-gates-and-remediation-627368.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34b27693-f55` | P1 | 361 | [P1] W7 W7.4 — D7 gate over-flags subsystems dispatched via  | [REROUTE 2026-04-30] Re-routed from orphan slug `d7-anchor-tuning` (no plan on d |
| `35027693-f55` | P2 | 240 | [P2] J1_canonical_pipeline_wiring P0 6 manifest violations o | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-28 — Cursor Agent to fill o |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W3.2 — `repo-tech-debt-wave1-b3c8d1.md` (✓ exists, 6 rows, bands={'P1': 2, 'P2': 2, 'P3': 2})

**Entry**: parent plan `repo-tech-debt-wave1-b3c8d1.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/repo-tech-debt-wave1-b3c8d1.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34c27693-f55` | P1 | 352 | [P1] W-LATER SSOT-HARDCODING-W2 — DEFERRED top 10 hardcoded  | DEFERRED top 10 hardcoded path literals to migrate to path_constants imports req |
| `34c27693-f55` | P1 | 309 | [P1] W-LATER SSOT-HARDCODING-W2-CODEMOD — codemod migration  | codemod migration of 123 hardcoded path literals in 100 files to use new W5.4 SS |
| `34c27693-f55` | P2 | 244 | [P2] W-LATER GUARDIAN-TOKEN-SSOT — PARTIAL W5.1 expanded can | PARTIAL CLOSURE 2026-04-24 (W17.a + W17.b high-volume).  W17.a lint-only baselin |
| `34c27693-f55` | P2 | 192 | [P2] W-LATER SCANNER-EDGEKIND-MISCLASSIFY — PARTIAL W5.1 acc | PARTIAL W5.1 accepts allow-log-and-swallow as return_none_swallow alias as paper |
| `34c27693-f55` | P3 | 130 | [P3] W-LATER SC1-STRUCTURAL-BLOCK — OUT OF SCOPE pre existin | OUT OF SCOPE pre existing SC-1 structural conformance 54 violations halts full a |
| `34c27693-f55` | P3 | 85 | [P3] W-LATER TIER-B-ANNOTATIONS — DEFERRED top 4 critical pa | DEFERRED top 4 critical path exemption files retrieval_benchmark _ssot_meta_lear |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W3.3 — `l0-routing-calibration-gap-audit-b3c9d4.md` (✓ exists, 5 rows, bands={'P1': 1, 'P2': 2, 'P3': 2})

**Entry**: parent plan `l0-routing-calibration-gap-audit-b3c9d4.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/l0-routing-calibration-gap-audit-b3c9d4.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34c27693-f55` | P1 | 336 | [P1] W2 W2.P1 — move similarity_threshold and abstain thresh | move similarity_threshold and abstain threshold literals to config YAML. Layer=L |
| `34c27693-f55` | P2 | 299 | [P2] W1 W1.P3 — emit routing feature vector on decision trac | emit routing feature vector on decision trace. Layer=L0, fan_in=4, surface=Obser |
| `34c27693-f55` | P2 | 269 | [P2] W1b W1b.P1 — close reason_codes enum and C0 coverage_sc | close reason_codes enum and C0 coverage_score field. Layer=L0, fan_in=2, surface |
| `34c27693-f55` | P3 | 132 | [P3] W5 W5.P5 — call sites for routing_calibration_metrics e | call sites for routing_calibration_metrics emitters at each gate decision point. |
| `34c27693-f55` | P3 | 132 | [P3] W4 W4.P1 — OTEL metrics for routing decisions and cache | OTEL metrics for routing decisions and cache hit ratios. Layer=L6, fan_in=3, sur |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W3.4 — `runtime-adg-coverage-audit-4f7a21.md (audit) | NEW:runtime-adg-trace-binding-remediation (remediation — not yet drafted)` (✗ MISSING, 1 rows, bands={'P2': 1})

**BLOCKER**: Parent plan `runtime-adg-coverage-audit-4f7a21.md (audit) | NEW:runtime-adg-trace-binding-remediation (remediation — not yet drafted)` not on disk. Options:

1. Recreate the plan file (check git log for last known version)
2. Flip all 1 rows → Retired with reason 'parent plan deleted'

Do NOT start execution until this is resolved.

Row IDs (for bulk retire if that's the chosen path):

- `34c27693-f55c-8157-90ef-c140194caf92` — [P2] [P2] RT1 P1 — Runtime ADG trace-binding remediation (98.9% snapshots unbound)

### W3.5 — `c0-context-assembly-best-practices-b7c3a1.md` (✓ exists, 2 rows, bands={'P2': 2})

**Entry**: parent plan `c0-context-assembly-best-practices-b7c3a1.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/c0-context-assembly-best-practices-b7c3a1.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34c27693-f55` | P2 | 254 | [P2] W1 W1.2 — Gateway-enabled recall A/B: Qwen local vLLM v | PATH CLARIFIED 2026-04-24. Acceptance gate from ADR-045 unchanged: Recall@20 ≥ h |
| `34c27693-f55` | P2 | 254 | [P2] W1 W1.1 — Heuristic-only retrieval baseline capture on  | ENV-BLOCKED 2026-04-24. Cannot execute in-session. Blockers: (1) ChromaDB collec |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W3.6 — `NEW:adg-mcp-reopen-hardening (to be created)` (✗ MISSING, 3 rows, bands={'P2': 3})

**Entry**: parent plan `NEW:adg-mcp-reopen-hardening (to be created)` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/NEW:adg-mcp-reopen-hardening (to be created)` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34b27693-f55` | P2 | 254 | [P2] W2 W2.2 — F4 make adg_reopen_connections truly idempote | F4 make adg_reopen_connections truly idempotent. Layer=L_TOOLS, fan_in=8, surfac |
| `34b27693-f55` | P2 | 254 | [P2] W1 W1.2 — F2 bounded-timeout wrapper around service.reo | F2 wrap service.reopen in bounded timeout executor. Layer=L_TOOLS, fan_in=8, sur |
| `34b27693-f55` | P2 | 215 | [P2] W1 W1.1 — F1 fix logging.basicConfig override (ADG MCP  | F1 fix logging.basicConfig override so adg_mcp_server.log captures runtime activ |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.


## W4 Execution Packet (77 rows, max impact 229, ~26.0 sessions (@ 2-4 hr each))

**Intent**: Long tail. Do NOT execute W4 linearly — instead, before any W4 session, run a THIRD triage pass that decomposes this wave by effort-rank: within W4, which sub-waves are in-progress vs. idle? Promote the most-advanced to a dedicated wave and demote the rest to further review.

### W4.1 — `anthropic-rag-gaps-7f3c2a.md` (✓ exists, 2 rows, bands={'P2': 1, 'P3': 1})

**Entry**: parent plan `anthropic-rag-gaps-7f3c2a.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/anthropic-rag-gaps-7f3c2a.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34a27693-f55` | P2 | 229 | [P2] W5 W5.1 — hardening_mixin execute_hardened NameError on | hardening_mixin execute_hardened NameError on CircuitBreakerOpenError blocks rea |
| `34a27693-f55` | P3 | 148 | [P3] W6 W6.2 — ingest_docs.py missing --contextualize flag m | ingest_docs.py missing --contextualize flag mirror of P1.1b. Layer=L_TOOLS, fan_ |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.2 — `windsurf-maintenance-2026-q2-0f3564.md` (✓ exists, 1 rows, bands={'P2': 1})

**Entry**: parent plan `windsurf-maintenance-2026-q2-0f3564.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/windsurf-maintenance-2026-q2-0f3564.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34c27693-f55` | P2 | 220 | [P2] W11 W11.1 — truly-independent watchdog fallback cron or | [REROUTE 2026-04-30] Re-routed from orphan slug `post-cursor-agent-watchdog-hardening |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.3 — `prompt-assembly-best-practices-gap-b4e1c2.md` (✓ exists, 14 rows, bands={'P2': 3, 'P3': 1, '--': 10})

**Entry**: parent plan `prompt-assembly-best-practices-gap-b4e1c2.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/prompt-assembly-best-practices-gap-b4e1c2.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34c27693-f55` | P2 | 204 | [P2] EQ-15 EQ-15.1 — Synthesis slot Y0 producer consumer wir | Synthesis slot Y0 producer consumer wiring. Layer=L_PG, fan_in=4, surface=State, |
| `34c27693-f55` | P2 | 195 | [P2] EQ-16 EQ-16.1 — Anti-pattern lint gate forbidding assis | Anti-pattern lint gate forbidding assistant prefill usage. Layer=L_PG, fan_in=1, |
| `34c27693-f55` | P2 | 192 | [P2] EQ-8b EQ-8b.1 — LLM-based conversation summarizer optio | LLM-based conversation summarizer optional upgrade. Layer=L_PG, fan_in=3, surfac |
| `34c27693-f55` | P3 | 122 | [P3] EQ-11b EQ-11b.1 — Cross-provider thinking-token billing | Cross-provider thinking-token billing reconciliation. Layer=L6, fan_in=2, surfac |
| `34c27693-f55` | -- | 0 | EQ-17 Y0 slot producer/consumer wiring | Author-Gate: adds a new dispatch path. Rollback via AgentSpec.y0_enabled default |
| `34c27693-f55` | -- | 0 | EQ-16 Thinking-token billing reconciliation | No Author-Gate. Observability-only; never raises. Risk: missing provider field h |
| `34c27693-f55` | -- | 0 | EQ-15 LLM-based convo summarizer (feature-flagged) | Author-Gate: introduces a non-determinism entry point in the dispatch path. Roll |
| `34c27693-f55` | -- | 0 | EQ-14 Final doc + registry sync | No Author-Gate. Admin-only; no code behavior change. |
| `34c27693-f55` | -- | 0 | EQ-13 Gemini adapter polish (long-context + thinking config) | Author-Gate: extends a provider surface. Risk: Gemini thinking_config API drift  |
| `34c27693-f55` | -- | 0 | EQ-12 Apply-patch validator + R0 response-shape fence | No Author-Gate. R0 is opt-in per AgentSpec. Risk: validator too strict rejects v |
| `34c27693-f55` | -- | 0 | EQ-11 Routing-meta + AgentSpec fields | No Author-Gate. All fields default to None/False so legacy behavior preserved. R |
| `34c27693-f55` | -- | 0 | EQ-10 I0 mixin bank (agentic_persistence, tool_first, plan_t | No Author-Gate. Mixins are opt-in per AgentSpec; default-off preserves legacy be |
| `34c27693-f55` | -- | 0 | EQ-9 Cache-prefix stability CI gate | No Author-Gate. Additive-only: gate is off-by-default until wired into .pre-comm |
| `34c27693-f55` | -- | 0 | EQ-8 History compressor + deterministic eviction | Author-Gate: this adds a new component in the dispatch path. Rollback via featur |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.4 — `adg-three-bucket-unified-c4f8e2.md` (✓ exists, 5 rows, bands={'P3': 4, 'P5': 1})

**Entry**: parent plan `adg-three-bucket-unified-c4f8e2.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/adg-three-bucket-unified-c4f8e2.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `35127693-f55` | P3 | 148 | [P3] Prompt-slot registry resolver pending canonical declara | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-29 — Cursor Agent to fill o |
| `35127693-f55` | P5 | 0 | [P4] Schema graduation to column-level NOT NULL after 4-week | Success: Auto-captured from DEFERRED_SCOPE marker 2026-04-29 — Cursor Agent to fill o |
| `34a27693-f55` | P3 | 0 | [P3] Rewrite weak gates to use graph-layer primitives (MVs + | Depends on 1.3 precision audit. Replace name-match/flat-relational queries with  |
| `34a27693-f55` | P3 | 0 | [P3] Burn down test-harness coverage baseline (1051 uncovere | Largest debt surface. 1051/1250 production modules have ZERO test-harness import |
| `34a27693-f55` | P3 | 0 | [P3] Burn down lifecycle-pair baseline (142 legacy leaks) | 142 leaks across sqlite3.connect (error), open (error), redis.Redis (warn), chro |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.5 — `sc1-audit-to-enforce-promotion-b4e9d7.md` (✓ exists, 1 rows, bands={'P3': 1})

**Entry**: parent plan `sc1-audit-to-enforce-promotion-b4e9d7.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/sc1-audit-to-enforce-promotion-b4e9d7.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34b27693-f55` | P3 | 144 | [P3] W8 W8.1 — SC1 54 violation audit mode backlog promote t | SC1 54 violation audit mode backlog promote to enforce. Layer=L_TOOLS, fan_in=3, |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.6 — `notion-schema-refactor-cleanup-9f2e4a.md` (✓ exists, 8 rows, bands={'P3': 2, 'P5': 1, '--': 5})

**Entry**: parent plan `notion-schema-refactor-cleanup-9f2e4a.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/notion-schema-refactor-cleanup-9f2e4a.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34b27693-f55` | P3 | 130 | [P3] C7 C7.1 — Deduplicate LJH1.3 Enforce JSON schema parsin | Deduplicate LJH1.3 Enforce JSON schema parsing entries in Wave Phase Convergence |
| `34b27693-f55` | P3 | 130 | [P3] C6 C6.1 — Patch post_cursor_agent_deferred_scope_capture hoo | Patch post_cursor_agent_deferred_scope_capture hook to write W1 typed fields directly |
| `34b27693-f55` | P5 | 1 | [P5] W6 W6.smoke — W6 smoke test verifying Priority removal  | W6 smoke test verifying Priority removal and Backlog Items rename. Layer=L_OPS,  |
| `34b27693-f55` | -- | 0 | [P3] C5 C5.1 — Archive 3 garbage slugs in Plans DS and relin | Archive 3 garbage slugs in Plans DS and relink backlog rows. Layer=L_OPS, fan_in |
| `34b27693-f55` | -- | 0 | [P3] C4 C4.1 — Promote query-progress-bar-backlog to real pl | Promote query-progress-bar-backlog to real plan file. Layer=L_TOOLS, fan_in=0, s |
| `34b27693-f55` | -- | 0 | [P2] C3 C3.1 — Promote hybrid-search-adg-seed-impl to real p | Promote hybrid-search-adg-seed-impl to real plan file (E.F1.1 P1 row depends on  |
| `34b27693-f55` | -- | 0 | [P2] C2 C2.1 — Promote anthropic-alignment-followups to real | Promote anthropic-alignment-followups to real plan file. Layer=L3, fan_in=1, sur |
| `34b27693-f55` | -- | 0 | [P2] C1 C1.1 — Promote adg-mcp-reopen-hardening to real plan | Promote adg-mcp-reopen-hardening to real plan file (4 P2 backlog rows depend on  |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.7 — `scorer-otel-autosource-layer-b-c5e4d1.md` (✓ exists, 4 rows, bands={'P3': 3, 'P4': 1})

**Entry**: parent plan `scorer-otel-autosource-layer-b-c5e4d1.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/scorer-otel-autosource-layer-b-c5e4d1.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34b27693-f55` | P3 | 106 | [P3] B2 B2.1 — rolling-window otel query fabric | rolling-window otel query fabric. Layer=L6, fan_in=3, surface=Observability, cov |
| `34b27693-f55` | P3 | 100 | [P3] B3 B3.1 — reversibility inference from adg semantic edg | reversibility inference from adg semantic edges. Layer=L_TOOLS, fan_in=0, surfac |
| `34b27693-f55` | P3 | 80 | [P3] B1 B1.1 — plan-slug agent-class resolver new module | plan-slug agent-class resolver new module. Layer=L_TOOLS, fan_in=0, surface=None |
| `34b27693-f55` | P4 | 66 | [P4] B5 B5.1 — priority calibration ab report | priority calibration ab report. Layer=L6, fan_in=0, surface=Observability, cover |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.8 — `chromadb-bge-retrieval-hardening-e9aa09.md` (✓ exists, 1 rows, bands={'P3': 1})

**Entry**: parent plan `chromadb-bge-retrieval-hardening-e9aa09.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/chromadb-bge-retrieval-hardening-e9aa09.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34c27693-f55` | P3 | 100 | [P3] W5 W5.1b — ingest_code hangs post-BGE-load on large sou | ingest_code hangs post-BGE-load on large source dirs. Layer=L_TOOLS, fan_in=0, s |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.9 — `fortknox-100pct-static-runtime-gap-9a3d4f.md` (✓ exists, 1 rows, bands={'P5': 1})

**Entry**: parent plan `fortknox-100pct-static-runtime-gap-9a3d4f.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/fortknox-100pct-static-runtime-gap-9a3d4f.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `35427693-f55` | P5 | 50 | [P5] FINAL — FINAL_SIGNED_CERTIFICATION via cosign keyless ( | Promotion from SIGNED_PROOF (Ed25519 repo signer, fortknox-release-signer-v1) to |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.10 — `decision-router-policy-tables-b3a4d2.md` (✓ exists, 1 rows, bands={'--': 1})

**Entry**: parent plan `decision-router-policy-tables-b3a4d2.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/decision-router-policy-tables-b3a4d2.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `35427693-f55` | -- | 0 | [P3] W3 — HOP1 archetype_classifier.yaml + classifier-chain  | Layer=L_APP, fan_in=1 (low blast radius). Coverage_gap_pct=N/A (golden-file pari |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.11 — `adg-truth-expansion-r5w1-a8f3c2` (✗ MISSING, 1 rows, bands={'--': 1})

**BLOCKER**: Parent plan `adg-truth-expansion-r5w1-a8f3c2` not on disk. Options:

1. Recreate the plan file (check git log for last known version)
2. Flip all 1 rows → Retired with reason 'parent plan deleted'

Do NOT start execution until this is resolved.

Row IDs (for bulk retire if that's the chosen path):

- `35227693-f55c-8110-8a59-dfd9d899d89e` — [--] [P3] ADG Truth Expansion R5 Wave 1 — A8 + A6 + A12

### W4.12 — `notion-backlog-schema-refactor-7c3d9e` (✗ MISSING, 1 rows, bands={'--': 1})

**BLOCKER**: Parent plan `notion-backlog-schema-refactor-7c3d9e` not on disk. Options:

1. Recreate the plan file (check git log for last known version)
2. Flip all 1 rows → Retired with reason 'parent plan deleted'

Do NOT start execution until this is resolved.

Row IDs (for bulk retire if that's the chosen path):

- `35227693-f55c-811a-91e8-efd59cc1d467` — [--] [P3] Notion Backlog Schema Refactor — typed fields + projection pattern

### W4.13 — `next-step-gate-ci-workflow-8733a6` (✗ MISSING, 1 rows, bands={'--': 1})

**BLOCKER**: Parent plan `next-step-gate-ci-workflow-8733a6` not on disk. Options:

1. Recreate the plan file (check git log for last known version)
2. Flip all 1 rows → Retired with reason 'parent plan deleted'

Do NOT start execution until this is resolved.

Row IDs (for bulk retire if that's the chosen path):

- `35227693-f55c-8157-b943-dc465901be37` — [--] [P3] next-step-gate-ci-workflow — run notion-plan-file-drift nightly

### W4.14 — `adg-tree-sitter-parser-exploration-b1c517.md` (✓ exists, 1 rows, bands={'P4': 1})

**Entry**: parent plan `adg-tree-sitter-parser-exploration-b1c517.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/adg-tree-sitter-parser-exploration-b1c517.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34f27693-f55` | P4 | 0 | [P4] Explore tree-sitter as ADG parser pass | Success: TBD — Cursor Agent suggested follow-up; fill on execution start. \| Blocking |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.15 — `mcp-serial-defense-l2l5-7d4f1a.md` (✓ exists, 1 rows, bands={'--': 1})

**Entry**: parent plan `mcp-serial-defense-l2l5-7d4f1a.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/mcp-serial-defense-l2l5-7d4f1a.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34d27693-f55` | -- | 0 | [P3] MCP Serial Defense L2–L5 — plan only, not implemented | NOT IMPLEMENTED — plan only per user instruction. Implementation order: W1→W2→W3 |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.16 — `adg-cascading-ratchet-defer-exit-a41828.md` (✓ exists, 1 rows, bands={'P4': 1})

**Entry**: parent plan `adg-cascading-ratchet-defer-exit-a41828.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/adg-cascading-ratchet-defer-exit-a41828.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34c27693-f55` | P4 | 0 | [P4] Extend defer-exit pattern to SC-1 / agentic-antipattern | Success: TBD — Cursor Agent suggested follow-up; fill on execution start. \| Blocking |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.17 — `notion-backlog-human-scoring-e7a941.md` (✓ exists, 5 rows, bands={'P3': 5})

**Entry**: parent plan `notion-backlog-human-scoring-e7a941.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/notion-backlog-human-scoring-e7a941.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34c27693-f55` | P3 | 0 | [SCORING] Wave 5 — Apply filled worksheet to Notion | Cursor Agent runs tools/debug/_apply_human_scoring.py once human finishes waves 1-4.  |
| `34c27693-f55` | P3 | 0 | [SCORING] Wave 4 — Score 22 singleton rows (H/B/EQ/ENH/misc) | Human reviews remaining H-series (H3/H6-H10 not in prior Wave D), B-series (B1-B |
| `34c27693-f55` | P3 | 0 | [SCORING] Wave 3 — Score 8 baseline-burndown rows (GAP/W1-P0 | Human spot-checks baseline counts (153 env flags, 142 legacy leaks, 1051 uncover |
| `34c27693-f55` | P3 | 0 | [SCORING] Wave 2 — Score 22 governance rows (W1.x / W2.x / W | Human audits each governance row against .cursor/rules/ and .windsurf/hooks.js |
| `34c27693-f55` | P3 | 0 | [SCORING] Wave 1 — Score 4 graph-edge rows (W9/W11/W12/W13) | Human reviews W9 (OTel span->ADG edge), W11 (watchdog + secret telemetry), W12 ( |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.18 — `shadow-learning-bestpractice-gap-7b3e4c.md` (✓ exists, 2 rows, bands={'--': 2})

**Entry**: parent plan `shadow-learning-bestpractice-gap-7b3e4c.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/shadow-learning-bestpractice-gap-7b3e4c.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34c27693-f55` | -- | 0 | [P4] F3 F3.1 — Dueling-LLM synth gateway-injected (Sovereign | Closed. Mock mode generates deterministic turns with prior-context threading; re |
| `34c27693-f55` | -- | 0 | [P4] F2 F2.1 — Wire transcript sampler to runtime ADG / L6 s | Closed. Verified end-to-end: synthetic index with 4 entries correctly loaded 3 w |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.19 — `runtime-adg-tier3-broader-adoption-8f2d1c.md` (✓ exists, 1 rows, bands={'P5': 1})

**Entry**: parent plan `runtime-adg-tier3-broader-adoption-8f2d1c.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/runtime-adg-tier3-broader-adoption-8f2d1c.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34c27693-f55` | P5 | 0 | [P5] RT3 P2 — Runtime ADG Tier 3 broader seal_step adoption  | None. Pure adoption backlog. Pattern proven, recipe is 3 lines, fail-open. Each  |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.20 — `adg-wiring-ci-dispatcher-hardening-b2f4a1.md` (✓ exists, 5 rows, bands={'P1': 1, 'P2': 2, 'P3': 2})

**Entry**: parent plan `adg-wiring-ci-dispatcher-hardening-b2f4a1.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/adg-wiring-ci-dispatcher-hardening-b2f4a1.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34b27693-f55` | P1 | 0 | [P1] H10 H10.1 — CVE OSV client unblocks W5.3 Gate L supply  | BAND-EXTRACTED 2026-04-24 (Wave D of notion-backlog-residual-cleanup-c3d8f2): ba |
| `34b27693-f55` | P2 | 0 | [P2] H9 H9.1 — Waiver expiry enforcement with populated waiv | BAND-EXTRACTED 2026-04-24 (Wave D of notion-backlog-residual-cleanup-c3d8f2): ba |
| `34b27693-f55` | P3 | 0 | [P3] H8 H8.1 — GitHub Actions matrix split per owner paralle | BAND-EXTRACTED 2026-04-24 (Wave D of notion-backlog-residual-cleanup-c3d8f2): ba |
| `34b27693-f55` | P3 | 0 | [P3] H7 H7.1 — Dispatcher owner band tier filter flags | BAND-EXTRACTED 2026-04-24 (Wave D of notion-backlog-residual-cleanup-c3d8f2): ba |
| `34b27693-f55` | P2 | 0 | [P2] H6 H6.1 — Shared SQLite ro connection pool cuts fleet w | BAND-EXTRACTED 2026-04-24 (Wave D of notion-backlog-residual-cleanup-c3d8f2): ba |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.21 — `judge-surface-harmonization-b9d3a7.md` (✓ exists, 1 rows, bands={'P2': 1})

**Entry**: parent plan `judge-surface-harmonization-b9d3a7.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/judge-surface-harmonization-b9d3a7.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34b27693-f55` | P2 | 0 | [P2] ENH6 ENH6.1 — Judge surface harmonization (legacy RAG v | Backlog architectural follow-up. Layer=L5, fan_in=12, surface=None, coverage_gap |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.22 — `llm-judge-hardening-followups-f2c8e1.md` (✓ exists, 1 rows, bands={'P1': 1})

**Entry**: parent plan `llm-judge-hardening-followups-f2c8e1.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/llm-judge-hardening-followups-f2c8e1.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34b27693-f55` | P1 | 0 | [P1] ENH5 ENH5.7 — LLM-as-Judge hardening follow-ups (gold s | Backlog follow-up. Layer=L5 (safety/evaluation), fan_in=15, surface=Security, co |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.23 — `llm-as-judge-hardening-anthropic-e7b1a4.md` (✓ exists, 1 rows, bands={'P1': 1})

**Entry**: parent plan `llm-as-judge-hardening-anthropic-e7b1a4.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/llm-as-judge-hardening-anthropic-e7b1a4.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34b27693-f55` | P1 | 0 | [P1] ENH5 ENH5.1 — LLM-as-Judge hardening to Anthropic best  | Backlog enhancement. Layer=L5 (safety/evaluation), fan_in=15, surface=Security,  |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.24 — `moe-agentic-architecture-d4e9a2.md` (✓ exists, 1 rows, bands={'P1': 1})

**Entry**: parent plan `moe-agentic-architecture-d4e9a2.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/moe-agentic-architecture-d4e9a2.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34b27693-f55` | P1 | 0 | [P1] ENH4 ENH4.1 — Mixture-of-Experts (MoE) control plane fo | Backlog enhancement. Layer=L0, fan_in=25, surface=Execution, coverage_gap_pct=75 |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.25 — `prompt-assembly-few-shot-exemplars-9c4e2b.md` (✓ exists, 1 rows, bands={'P2': 1})

**Entry**: parent plan `prompt-assembly-few-shot-exemplars-9c4e2b.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/prompt-assembly-few-shot-exemplars-9c4e2b.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34b27693-f55` | P2 | 0 | [P2] ENH2 ENH2.1 — Prompt assembly: one-shot many-example EX | Backlog enhancement. Layer=L4, fan_in=10, surface=None, coverage_gap_pct=80.0. P |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.26 — `prompt-categories-coverage-audit-b8f5d3.md` (✓ exists, 1 rows, bands={'P1': 1})

**Entry**: parent plan `prompt-categories-coverage-audit-b8f5d3.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/prompt-categories-coverage-audit-b8f5d3.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34b27693-f55` | P1 | 0 | [P1] ENH3 ENH3.1 — Prompt category coverage audit and enforc | Backlog enhancement. Layer=L0, fan_in=15, surface=Execution, coverage_gap_pct=60 |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.27 — `cot-reflexion-self-consistency-config-7a3f1c.md` (✓ exists, 1 rows, bands={'P1': 1})

**Entry**: parent plan `cot-reflexion-self-consistency-config-7a3f1c.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/cot-reflexion-self-consistency-config-7a3f1c.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34b27693-f55` | P1 | 0 | [P1] ENH1 ENH1.1 — CoT/ToT/Reflexion + self-consistency conf | Backlog enhancement. Layer=L3, fan_in=20, surface=Execution, coverage_gap_pct=70 |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.28 — `hybrid-search-adg-seed-rerank-c58e21.md` (✓ exists, 1 rows, bands={'P3': 1})

**Entry**: parent plan `hybrid-search-adg-seed-rerank-c58e21.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/hybrid-search-adg-seed-rerank-c58e21.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34b27693-f55` | P3 | 0 | [P3] E E.F1 — Hybrid search engine ADG seed + rerank wiring | Hybrid search engine ADG seed and rerank wiring. Layer=L3, fan_in=0, surface=Exe |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.29 — `ssot-violations-sweep-29caf4.md` (✓ exists, 2 rows, bands={'P3': 1, 'UNSCORED': 1})

**Entry**: parent plan `ssot-violations-sweep-29caf4.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/ssot-violations-sweep-29caf4.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34a27693-f55` | P3 | 0 | [P3] ssot-sweep: _validate_baseline_integrity test coverage  | VALIDATION 2026-04-22: grep for _validate_baseline_integrity in agentic_core/ re |
| `34a27693-f55` | UNSCORED | 0 | ssot-sweep: 34 grandfathered hardcoded-exclusion sites (long | BASELINE VERIFICATION 2026-04-24: python ops_scripts/ci/check_hardcoded_exclusio |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.30 — `p2-burndown-wave-9e4c17.md` (✓ exists, 2 rows, bands={'P3': 2})

**Entry**: parent plan `p2-burndown-wave-9e4c17.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/p2-burndown-wave-9e4c17.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `34927693-f55` | P3 | 0 | [P3] W7 — P3 long-tail (style) antipattern burndown | Primary kinds: global_state_mutation (~373 on L0/L4/L5), throw_for_normal_flow ( |
| `34927693-f55` | P3 | 0 | [P3] W5 — Post-W4 resnapshot to refresh ADR-024 Part B promo | INVESTIGATED 2026-04-24 (Wave B): row is an action ('Post-W4 resnapshot'), not f |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.

### W4.31 — `ssot-consolidation-cleanup-b7f3a1.md` (✓ exists, 8 rows, bands={'P3': 8})

**Entry**: parent plan `ssot-consolidation-cleanup-b7f3a1.md` available; global entry checklist passes.

**Ordered steps**:

1. Read parent plan `.cursor/plans/ssot-consolidation-cleanup-b7f3a1.md` to understand current wave status + any in-progress Phase ID
2. For each row below (in impact-descending order), fetch the Notion row and inspect Evidence for prior partial execution
3. Determine smallest complete sub-slice executable in current session (may be 1 row, rarely more than 3 for P1)
4. Execute per the usual Cursor Agent T2/T3 loop: analyze → plan → edit → verify → evidence
5. For each row completed: PATCH Notion Status=Completed, Evidence=commit SHA + delta summary, Last Updated=today
6. Update parent plan's wave status table

**Rows in this sub-wave** (in impact-descending order):

| Row ID | Band | Impact | Title | BI snippet |
|---|---|---:|---|---|
| `33f27693-f55` | P3 | 0 | [P3] Delete lifecycle trace emit block (import-time side eff | _empty_ |
| `33f27693-f55` | P3 | 0 | [P3] Remove LCD subfolder builder pipeline (_build_lcd_subfo | _empty_ |
| `33f27693-f55` | P3 | 0 | [P3] Remove all *_subfolders keys from LAYER_OVERRIDES | _empty_ |
| `33f27693-f55` | P3 | 0 | [P3] Clean init.py re-exports (remove re-exports of removed  | INVESTIGATED 2026-04-24 (Wave B): naive scorer matched literal 'init.py' token.  |
| `33f27693-f55` | P3 | 0 | [P3] Update 2 test files consuming build_sovereign_territori | _empty_ |
| `33f27693-f55` | P3 | 0 | [P3] Run tests, pre-commit, regenerate ADG — full verificati | _empty_ |
| `33f27693-f55` | P3 | 0 | [P3] Clean structure_blueprint_config.py shim (remove delete | _empty_ |
| `33f27693-f55` | P3 | 0 | [P3] Delete build_sovereign_territories() + all private help | _empty_ |

**Exit**: all rows above flipped Completed; parent plan regen-verified; no new P0/P1 ADG violations.


## ADG_GRAPH_LAYER_EVIDENCE

Not applicable — this is a governance / execution-roadmap document. Each child wave produces its own ADG evidence at execution time. The parent plans listed above are where wave-specific §22 evidence belongs.

## ADG_HOTSPOT_REPORT

Not applicable — see above. Hotspot analysis is done at execution time on the parent plan's scope, not at roadmap authoring time.

## Supersedes

None. This extends `d-bucket-burndown-e4f2c9.md` with per-wave execution detail.
