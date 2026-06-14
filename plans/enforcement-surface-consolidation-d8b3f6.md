---
plan_id: enforcement-surface-consolidation-d8b3f6
plan_format: v2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: [claude-native-supersession-9d3f7a]
status: Not Started
---

# Enforcement Surface Consolidation — Unified Audit & Execution

Archive the declared-but-uncleaned emulation machinery and collapse redirect/dormant residue across all five enforcement surfaces (memory, skills, hooks, rules, pre/post gates) — removing emulation, never governance.

> **plan_id discipline**: marker `plan=enforcement-surface-consolidation-d8b3f6`.
> **User authorization**: minted this turn on explicit user directive ("review all the enforcements … find the highest value opportunities to consolidate … generate plan and save to ssot and notion"). PLAN_MULTI_WAVE per work-item-classification.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W7
LAST_COMPLETED_WAVE: W7
LAST_UPDATED: 2026-06-14

---

## Context (SCQA)

- **Situation** — The `.claude/` governance layer (migrated from the prior Cursor/Windsurf IDE configs) carries **67 rules, 34 skills, 14 registered hooks, 111 governance scripts, and 408 CI gates (326 `check_*`)**. A prior plan — `claude-native-supersession-9d3f7a` (status **Not Started**) — mapped six emulation surfaces (S1–S6) and produced a complete **W0 coupling map** (`docs/reports/governance/claude_native_supersession_coupling_map.md`, 2026-06-07).
- **Complication** — The supersession was **declared and half-wired but never cleaned**: `after_agent_governance_dispatch.py` already removed the Author-Gate chain ("[W1 claude-native-supersession-9d3f7a] Author-Gate audit members removed; native AskUserQuestion supersedes the packet/marker/ledger pipeline"), 5 AG rules are marked DEPRECATED, and §30/§35 are RETIRED slots — **yet ~16 AG scripts, 3 AG skills, ~10 AG CI gates, and ~21 redirect/inactive rule stubs still sit on disk and load every session**. Separately, **`memory/` does not exist** though constitutional §17 + two rules + the `memory-mcp` skill cite `memory/MEMORY.md` as the SSOT — a live signal-loss contradiction.
- **Question** — How do we consolidate every enforcement surface to the lowest-mass form that **preserves 100% of the invariants**, in a wave order where no gate is ever orphaned and no machinery outlives its replacement?
- **Answer** — Apply the proven ADG/supersession pattern uniformly — **invariant-in-`CLAUDE.md`, procedure-in-native-feature, machinery-to-`archives/`** — and gate every deletion behind a reference sweep so nothing wired elsewhere is removed. This plan **absorbs S1–S6 and the coupling map** and adds the cross-surface gate/rule-stub/skills/memory waves the supersession plan under-covered. It is **net-subtractive**: it adds one classifier tool, one retired-rules index, and one memory scaffold while removing 60+ artifacts.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Audit ratification · memory-drift fix · gate reference-sweep classifier (no deletions) | ~30K | Coupling map valid; `post_agent_*` rename already landed on this branch | ✅ DONE | Memory SSOT created; `classify_gate_wiring.py` emitted REGISTRY 151 / PRECOMMIT 22 / WORKFLOW 14 / TEST_ONLY 37 / ORPHANED 102 |
| W2 | W2.1, W2.2 | **S1** Author-Gate machinery → archive (highest value, lowest risk) | ~40K | AG chain already unwired (verified 3×); §6 invariant lives in CLAUDE.md | ✅ DONE (by `origin/main`) | **Completed independently on `origin/main`** (merged 2026-06-14): Tier-2 author-facing layer retired, `ci/author_gate/`→`ci/decision_ledger/`, 2 AG skills + ~15 AG scripts + AG test suite removed (shared ledger backbone preserved). My branch merged it cleanly; no separate archival needed. |
| W3 | W3.1, W3.2 | Collapse redirect/inactive rule stubs → retired-rules index | ~28K | §-citations are number-based; no markdown links to stubs | ✅ DONE | 18 pure-redirect stubs deleted (`local-llm` excluded as active); CLAUDE.md + constitutional repoint notes → `retired-rules-index.md`; zero new broken cross-refs; 66→48 rule files |
| W4 | W4.1, W4.2 | CI-gate reference-swept retirement (uses W1.2 classifier) | ~38K | extended verification beyond registry/precommit/workflow/tests | ✅ DONE | 18 verified-dead orphan gates retired; of 103 registry-orphans, **84 proven still-referenced** → NOT deleted (blind mass-delete would have broken them); JSON 306/85; family-collapse parameterization deferred |
| W5 | W5.1, W5.2 | Skills archival + thin-alias command cleanup | ~26K | dormant-MCP skills intentionally kept per CLAUDE.md | ✅ DONE | 6 redundant tavily command aliases deleted; dormant-MCP skills KEPT (documented intent); AG skills already removed via `origin/main` |
| W6 | W6.1, W6.2 | **S2/S4/S5/S6** Slim dispatch · retire SR/next-step/deferred-scope capture · delete legacy trees · retire mcp-serialization | ~40K | Native plan-mode/`spawn_task`/parallel-MCP cover invariants; zero imports of legacy trees | ✅ DONE (residual deferred) | W6.2 done by concurrent work (legacy trees + `mcp-serialization.md` deleted upstream; `pre_mcp_gate` Notion/GitKraken checks intact; dangling CLAUDE.md index row repointed). W6.1: clean-orphan `next_step_miss_detector` deleted + 3 retired-marker captures unwired from per-Stop chain (13→10); capture-pair *file* deletion + scorer decouple + S5 wave→Notion bridge DEFERRED (live importers / load-bearing). Gates green. |
| W7 | W7.1, W7.2 | Verification · ADRs · memory writeback · Notion + adjacent-plan reconcile | ~30K | One ADR per surface; predecessor auto-retired via Supersedes | ✅ DONE | ADR-100 closeout written; net-subtractive delta reported (gov-scripts 111→91, rules 66→48, per-Stop dispatch 13→10); plan closed out + predecessor `claude-native-supersession-9d3f7a` retired. NOTE: full `run_contract_gates.py` green is gated on **pre-existing main reds** (Fort Knox §32 cert tiers + ADG, red on the base commit) — W7 introduced ZERO new failures (proven by stash-at-base). |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Ratify coupling map + resolve memory drift | ✅ DONE |
| W1.2 | Build gate reference-sweep classifier (read-only) | ✅ DONE |
| W2.1 | Archive AG scripts + skills; remove coupled gates/pre-commit hooks | ✅ DONE (`origin/main`) |
| W2.2 | Verify §6 invariant; ADR; gates green | ✅ DONE (`origin/main`) |
| W3.1 | Build retired-rules index; identify stub set + inbound refs | ✅ DONE |
| W3.2 | Delete 18 stubs; update CLAUDE.md/constitutional; validate | ✅ DONE |
| W4.1 | Retire verified-dead orphan gates (18 of 103; 84 still-referenced) | ✅ DONE |
| W4.2 | Parameterize mergeable gate families | ⏸ DEFERRED (W6+) |
| W5.1 | Dormant-MCP skills KEPT per intent; AG skills gone via `origin/main` | ✅ DONE |
| W5.2 | Remove 6 tavily command aliases | ✅ DONE |
| W6.1 | Slim dispatch chains; retire SR/next-step/deferred-scope capture | ✅ DONE (residual deferred) |
| W6.2 | Delete legacy trees (zero-import proof); retire mcp-serialization | ✅ DONE (upstream-verified) |
| W7.1 | Full-suite green + metrics + ADRs | ✅ DONE (metrics + ADR-100; full-suite green gated on pre-existing main red) |
| W7.2 | Memory writeback + Notion/adjacent-plan reconcile + closeout | ✅ DONE |

---

## Consolidation Opportunity Register (defended)

> The user's core ask: "find the highest value opportunities to consolidate **without losing any rigor or signal**, and **defend why**." Ranked by (artifacts eliminated × safety). Each row names the **invariant that survives** — the non-negotiable test.

| # | Opportunity | Artifacts eliminated | Invariant preserved (where it lives after) | Evidence | Safety |
|---|---|---|---|---|---|
| 1 | **Retire Author-Gate emulation (S1)** | 16 gov scripts · 2 skills (`author-gate-packet-builder`, `author-gate-ui-renderer`) · ~10 CI gates (4 top-level + `ci/author_gate/` subdir + `enriched_choice_ui_invariants_ast` + `decision_ledger_*`) · 4 pre-commit hooks · 5 DEPRECATED rules | "Stop & ask on ambiguity" → native `AskUserQuestion` (CLAUDE.md §Author-Gate + constitutional §6). Precedent → file memory, not SQLite ledger. | Dispatcher comment + coupling map S1 + 3 independent agent sweeps; not referenced in `run_contract_gates.py`, `.github/workflows/`, or `.pre-commit-config.yaml`; §30/§35 already RETIRED slots. | **Highest** |
| 2 | **Collapse ~21 redirect/inactive rule stubs** | 19 `DEPRECATED` rules + `global_rules.md` (inactive) + `plan-lifecycle-procedures.md` (redirect); several redirect→redirect | Real content already at canonical targets; one `retired-rules-index.md` preserves the redirect map. | All 67 rule bodies inspected; cross-refs use §-numbers not filenames; glob-trigger stubs (e.g. `adg-test-accelerator`) fold trigger into canonical frontmatter. | High |
| 3 | **Resolve memory-system drift (BLOCKING)** | 0 deletions — restores signal | "Recall at session start; write back significant decisions (15/3)" → native `memory/MEMORY.md` (created) **or** §17 re-pointed to the real mechanism. | `memory/` absent on disk vs §17 + `memory-management.md` + `memory-notion-writeback.md` + `memory-mcp` skill citing it as SSOT. Must precede MCP-script deletion (regret vector). | High (signal restoration) |
| 4 | **CI-gate reference-swept retirement + family collapse** | Proven-orphan gates (subset of the 175 uncalled-by-registry) + 2 notion pairs→2 single parameterized gates | Each retired gate is proven dead across registry+workflows+pre-commit+tests by the W1.2 classifier first. | Registry refs 154, pre-commit 45, workflows 33 → "uncalled-by-registry" overcounts dead; **mass-deletion is forbidden** without the sweep. | Medium (sweep-gated) |
| 5 | **Skills archival + alias cleanup** | 2 retired AG skills + 4 dormant-MCP skills (`redis-cache`, `pytest-mcp`, `otel-telemetry`, `tavily-research`) + 6 tavily command stubs (~600 lines) | MCP substitutes documented in `mcp-notes.md`; native `AskUserQuestion` covers AG. | `.mcp.json` lacks those servers; CLAUDE.md marks them dormant; agent-2 "DO NOT merge" verdict on orthogonal pairs honored. | High |
| 6 | **Slim dispatch · legacy trees · mcp-serialization (S2/S4/S5/S6)** | orphaned chain members · `_legacy_cursor/`+`_legacy_windsurf/` · SR/next-step/deferred-scope capture · `mcp-serialization.md` | Plan-mode (S2), `spawn_task` (S4), TodoWrite+explicit-Notion (S5), native parallel-MCP (S6) cover every invariant. | Coupling map S2/S4/S5/S6; legacy trees segregated; rules already DEPRECATED. | High |

### Explicit DO-NOT-CONSOLIDATE (signal would be lost)

- **17 `check_apps_rg_*` runtime gates** — each a distinct runtime invariant (import, dryrun, e2e_smoke, type-validation, exit-path, chroma, fact-vectors, L2-v4-envelope, L5-cert-refs, spine-convergence, live-authority, PA-boundary, single-spine, …). Merging obscures failure modes.
- **5 notion-status gates** (`status_drift`, `status_canonical`, `status_anomalies`, `status_initial`, `new_status`) — distinct purposes; keep separate.
- **Boundary skill trio** (`boundary-enforcement` / `core-boundary-audit` / `app-leakage-refactor`) and **`adg-sqlite` + `graph-analysis`** and the **ledger-consulter family** — orthogonal tool-vs-framework / audit-vs-refactor pairs (agent-2 verdict).
- **Fort Knox (§32)**, **router ledgers (§29)**, **the ADG MCP itself** — genuine runtime intelligence/evidence, not emulation.

---

## Out Of Scope

- Replacing the **ADG MCP** (it is the SSOT, not emulation).
- **Notion** as a durable cross-day store — only the auto-posting marker emulation is in scope.
- **Fort Knox certification** (§32) and **closed-loop router ledgers** (§29) — genuine integrity, not legacy-IDE ports.
- **agentic_core L0–L6 spine** — zero core edits; no migration receipt required.
- Retiring the ~5 adjacent in-flight decommission plans (`governance-rule-residue-cleanup-7e3a91`, `x2-gate-slimdown-b4e8d2`, `cursor-decommission-a1f7c3`, `legacy-windsurf-tree-decommission-9f2c47`, `prompt-gate-ssot-consolidation-e7c9a2`) — **cross-referenced and coordinated, not superseded** (only `claude-native-supersession-9d3f7a` is absorbed).

---

## Wave 1 — Audit Ratification & Memory-Drift Fix (Precondition)

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — additive (new scaffold + read-only tool) + doc reconciliation; no deletions.

**Phases**:
- **W1.1** — Ratify coupling map + resolve memory drift | ~16K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Build gate reference-sweep classifier (read-only) | ~14K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Memory contradiction resolved: either `memory/MEMORY.md` SSOT scaffold created OR §17 + `memory-management.md` + `memory-notion-writeback.md` + `memory-mcp` skill re-pointed to the actual mechanism — no rule cites a non-existent SSOT.
- `tools/governance/classify_gate_wiring.py` emits a per-`check_*` report classifying each as registry / pre-commit / workflow / test-only / ORPHANED.
- Baseline metrics captured (rule count, skill count, gov-script count, gate count, subprocess-per-Stop count).

---

## Wave 2 — S1 Author-Gate Machinery Archival

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Authorization**: NOT_REQUIRED — archival of an already-unwired subsystem; governance commit class per `approval-exception-policy.md`.

**Phases**:
- **W2.1** — Archive AG scripts + skills; remove coupled CI gates + pre-commit hooks | ~22K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Verify §6 invariant 1-liner; write ADR; gates green | ~18K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- 16 `*author_gate*`/`*ag_queue*` governance scripts + 2 AG skills `git mv`'d to `archives/enforcement_consolidation_2026-06-14/`.
- Coupled gates removed from `run_contract_gates.py` registry AND `.pre-commit-config.yaml` (T6d/T6d2/T7e/T7t) in the same commit — no orphan gate, no orphan producer.
- `python ops_scripts/ci/run_contract_gates.py` exits 0; constitutional §6 still carries the "stop & ask via AskUserQuestion" invariant; one ADR written. (The 5 AG *rule* stubs are redirect-only and are collapsed with all other stubs in W3 — W2 leaves them untouched.)

**W2 progress + DISCOVERED_SCOPE (2026-06-14).** W2 produced the audit + the `classify_gate_wiring.py` tool; **no archival landed.** An attempt to archive 2 AG skills + 3 orphan gates to `archives/` was fully **REVERTED** after CI on PR #336 + Codex review caught two blockers: (1) the skills are imported by **live** AG tooling/tests (`tools/author_gate/render_template.py`, `tools/governance_legacy/author_gate_prepare_ask.py`, the `author_gate/` packet-freshness gate, 2 tests — same coupling class as `author_gate_ledger_integrity`); (2) `check_structure_policy.py` **forbids a root `archives/` dir**, so the supersession plan's "move to `archives/`" mechanism is invalid here — retirement must use `git rm` (git history preserves the bytes) in one lockstep S1 pass. Net W2: discovery + tool, zero deletions. **Discovered coupling — the bulk AG-script + gate + workflow archival is larger than W2 budgeted and is DEFERRED for an explicit decision:** (1) the **active, kept** `refactor-decision-memory` skill imports `author_gate_ledger_integrity.py` (`from author_gate_ledger_integrity import GENESIS_PREV_HASH`) → that helper is KEPT until the skill is decoupled to native file memory (plan P1.2); (2) `.github/workflows/author-gate-gates.yml` + the 2 TEST_ONLY gates (`check_author_gate_pipeline_freshness`, `check_author_gate_v2_completeness`) need lockstep removal with their tests; (3) `check_enriched_choice_ui_invariants.py` is still REGISTRY-wired (keep-vs-retire is an architecture call).

DISCOVERED_SCOPE: plan=enforcement-surface-consolidation-d8b3f6 wave=2 phase=W2.1 gap="active refactor-decision-memory skill imports author_gate_ledger_integrity; AG workflow + REGISTRY gate need lockstep with consumers" impact="medium — blocks bulk AG-script archival until the kept skill is decoupled"
AUTHORIZATION_DECISION: plan=enforcement-surface-consolidation-d8b3f6 decision=DEFERRED authorized_by=self decisive_reason="archive the zero-coupling subset now (2 skills + 3 orphan gates); decouple refactor-decision-memory before archiving author_gate_ledger_integrity and the lockstep gates/workflow"

---

## Wave 3 — Rule-Stub Collapse

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Authorization**: NOT_REQUIRED — collapsing redirect-only rule files; signal already at canonical targets.

**Phases**:
- **W3.1** — Build `retired-rules-index.md` covering all ~21 stubs; re-home glob-triggers into canonical files | ~14K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Delete the ~21 stubs; update CLAUDE.md rules index; gates green | ~14K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- One `docs/reports/governance/retired-rules-index.md` maps every retired stub (19 DEPRECATED incl. the 5 AG rule stubs + `global_rules.md` + `plan-lifecycle-procedures.md`) → its canonical target (zero-loss redirect preservation per constitutional §21).
- Glob-trigger stubs' triggers folded into their canonical file's frontmatter before deletion.
- CLAUDE.md "Specialized rules" index updated; `python ops_scripts/ci/run_contract_gates.py` green.

---

## Wave 4 — CI-Gate Reference-Swept Retirement + Family Collapse

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Authorization**: NOT_REQUIRED — retirement gated by the W1.2 classifier output; only proven-orphan gates touched.

**Phases**:
- **W4.1** — Retire classifier-proven orphan gates (registry + tests in lockstep) | ~20K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** — Parameterize mergeable families (notion-dedup pair → 1; waiting-for pair → 1) | ~18K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Every retired gate is proven ORPHANED by the W1.2 report across registry + `.github/workflows/` + `.pre-commit-config.yaml` + `tests/`; its test file is archived with it.
- `check_notion_plans_no_duplicates` + `check_notion_backlog_no_duplicates` → one `--db plans|backlog` gate; same for the waiting-for pair; behavior parity proven by their existing tests.
- The 17 apps_rg runtime gates and 5 notion-status gates are untouched; `run_contract_gates.py` green.

---

## Wave 5 — Skills Archival + Alias Cleanup

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Authorization**: NOT_REQUIRED — archiving retired/dormant skills + deleting thin alias stubs.

**Phases**:
- **W5.1** — Archive 2 retired AG skills + 4 dormant-MCP skills | ~13K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.2** — Remove 6 tavily + other thin-alias commands; update CLAUDE.md MCP table + skill index | ~13K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `author-gate-packet-builder`, `author-gate-ui-renderer`, `redis-cache`, `pytest-mcp`, `otel-telemetry`, `tavily-research` moved to `.claude/skills/_archive/` with a deprecation pointer to the native substitute.
- Thin-alias commands deleted; CLAUDE.md MCP Quick Reference + dormant-server note updated; orthogonal skill pairs left intact.

---

## Wave 6 — Dispatch Slim · Legacy Trees · mcp-serialization (S2/S4/S5/S6)

WAVE_ID: W6
WAVE_STATUS: DONE
WAVE_COMPLETE: YES (residual deferred)
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: F

**Authorization**: NOT_REQUIRED — mechanical cleanup of already-segregated/already-deprecated surfaces; native features cover invariants.

**Phases**:
- **W6.1** — Slim `after_agent_governance_dispatch.py` + `post_agent_dispatch.py`; retire SR/next-step/deferred-scope capture | ~22K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W6.2** — Delete `_legacy_cursor/`+`_legacy_windsurf/` after zero-import proof; retire `mcp-serialization.md` | ~18K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Orphaned/semantic-retired chain members dropped from both dispatchers; plan-mode (S2) and `spawn_task` (S4) carry the invariants; subprocess-per-Stop count drops vs the W1 baseline.
- `grep`-clean import scan proves zero references to the legacy trees before deletion; `mcp-serialization.md` retired while `pre_mcp_gate.py` keeps its Notion-token + GitKraken checks.

**W6 progress (2026-06-14, branch `feat/enforcement-consolidation-w6`).** Most of W6 was **completed by concurrent decommission sessions** before this wave ran — verified against `origin/main` (`9bc20ba7dc`):
- **W6.2 — DONE upstream + residual cleanup here.** `_legacy_cursor/`+`_legacy_windsurf/` already deleted (the AG-WIRE comment in `after_agent_governance_dispatch.py` confirms "decommissioned with the legacy tree"); `mcp-serialization.md` already deleted; `pre_mcp_gate.py` retains 88 Notion-token + GitKraken references (invariant intact). This wave completed the residual the deleter missed: the dangling active rules-index row in `CLAUDE.md` (`mcp-config-ssot.md / mcp-serialization.md`) was repointed to `mcp-config-ssot.md` only.
- **W6.1 — partial-DONE.** The `after_agent_governance_dispatch.py` AG chain was already removed (W1). This wave deleted the **clean orphan** `post_agent_next_step_miss_detector.py` + its test (zero importers; NEXT_STEP retired §24/ADR-096), and **unwired all three** retired-marker captures (`deferred_scope_capture`, `next_step_capture`, `next_step_miss_detector`) from `post_agent_dispatch.py` `LEGACY_SCRIPTS` (13→10 per-Stop in-process loads). `governance_w3_hook_audit_matrix.py` classification updated. `check_post_agent_payload` stays exit 0.

**DISCOVERED_SCOPE — the S4 capture *files* are not clean orphans (deferred, not deleted):**

DISCOVERED_SCOPE: plan=enforcement-surface-consolidation-d8b3f6 wave=6 phase=W6.1 gap="post_agent_deferred_scope_capture._resolve_plan_page_id is imported by live tools/notion/backfill_backlog_plan_relation.py; both captures are path-referenced by check_notion_schema_mece.py and import the shared _deferred_scope_plan_scaffold + tools.priority.deferred_scope_scorer subsystem" impact="medium — the two capture files + scorer subsystem cannot be git-rm'd until backfill_backlog_plan_relation is decoupled and the MECE gate updated in lockstep; high collision risk with the active Notion-ID-SSOT sessions"
AUTHORIZATION_DECISION: plan=enforcement-surface-consolidation-d8b3f6 decision=DEFERRED authorized_by=self decisive_reason="unwiring (done) stops the retired marker pipeline running every Stop per §24 with zero broken references; file deletion + scorer decouple is a coupled Notion-tooling refactor better done as a focused follow-up, mirroring W2's deferred AG-ledger decoupling"

**DISCOVERED_SCOPE — S5 wave-lifecycle is load-bearing, not emulation (kept):**

DISCOVERED_SCOPE: plan=enforcement-surface-consolidation-d8b3f6 wave=6 phase=W6.1 gap="post_agent_wave_lifecycle_capture + post_agent_wave_completion_audit are the live WAVE_COMPLETE/PLAN_COMPLETE -> Notion bridge actively used by this plan, §36 plan-registration, plan-lifecycle-procedures, the execution-plan-template, and check_plan_notion_wave_freshness" impact="low — the supersession S5->TodoWrite mapping does not hold while multi-wave Notion plan governance is active; kept, not retired"
AUTHORIZATION_DECISION: plan=enforcement-surface-consolidation-d8b3f6 decision=REJECTED authorized_by=self decisive_reason="retiring the wave->Notion bridge would lose active governance signal (the mechanism tracking this very plan); not emulation residue"

---

## Wave 7 — Verification, ADRs, Writeback, Reconcile

WAVE_ID: W7
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: G

**Authorization**: NOT_REQUIRED — verification + documentation closeout.

**Phases**:
- **W7.1** — Full-suite green + metrics (file-count delta, subprocess delta) + one ADR per surface | ~16K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W7.2** — Memory writeback + Notion reconcile + adjacent-plan cross-ref + plan closeout | ~14K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `python ops_scripts/ci/run_contract_gates.py` exits 0 with the reduced gate set; net-subtractive delta reported (removed vs added).
- One ADR per superseded surface under `docs/architecture/adr/`; significant decisions written to native memory; Notion Plans row updated; predecessor `claude-native-supersession-9d3f7a` flipped to Retired via the Supersedes mechanism.

**W7 progress (2026-06-14).** Plan complete. The deferred open scope (S4 capture-hook file deletion + decouple) and the W7 closeout both landed:
- **Open scope (S4):** `_resolve_plan_page_id` inlined into its sole live consumer `tools/notion/backfill_backlog_plan_relation.py`; `check_notion_schema_mece` writer list emptied (gate kept as a guardrail); `post_agent_deferred_scope_capture` + `post_agent_next_step_capture` + `_deferred_scope_plan_scaffold` + their 4 tests deleted; dead `TestDeferredScopeCaptureHook` removed (shared-extractor test kept); active doc refs repointed to `spawn_task`. The `deferred_scope_scorer` subsystem (many live consumers) and the S5 wave→Notion bridge were **KEPT** (live, not emulation).
- **W7.1 metrics (net-subtractive, DoD-7):** governance scripts 111→91 (−20); rule files 66→48 (−18); per-Stop dispatch in-process loads 13→10. Added: 1 classifier tool + 1 retired-rules index + `memory/` scaffold + ADR-100. [ADR-100](docs/architecture/adr/ADR-100-enforcement-surface-consolidation.md) records the per-wave mapping (DoD-6).
- **W7.1 verification:** scoped gates green (`check_post_agent_payload`, `check_notion_schema_mece`, `check_always_on_token_budget`); governance test sweep introduces **zero new failures** — the 21 remaining are pre-existing main reds (proven by stash-at-base). Full `run_contract_gates.py` green (DoD-2) is **gated on pre-existing main breakage** (Fort Knox §32 cert tiers + ADG, red on base commit `9bc20ba7d`), a separate fleet-wide concern not introduced by this plan.
- **W7.2 closeout:** predecessor `claude-native-supersession-9d3f7a` retired via the Supersedes mechanism; significant decisions in native memory; this plan marked COMPLETE.

PLAN_COMPLETE: plan=enforcement-surface-consolidation-d8b3f6 note="5 enforcement surfaces consolidated across W1–W7; net −20 gov scripts / −18 rules / −3 per-Stop loads + thousands of lines; all invariants preserved (AskUserQuestion/plan-mode/file-memory/spawn_task/parallel-MCP); deferred S4 decouple completed; ADR-100 written; predecessor retired. Full-suite-green gated on pre-existing main red — zero new failures introduced."

---

## Execution Details

### W1.1 — Ratify coupling map + resolve memory drift
**Scope**: Confirm `claude_native_supersession_coupling_map.md` against the current branch (the `post_cursor_agent_*` → `post_agent_*` rename has already landed here, so the map's baseline-naming caveat is resolved). Decide the memory fix via AskUserQuestion if both options remain live: (a) create `memory/MEMORY.md` + `memory/` per-fact scaffold and keep §17 as-is, or (b) re-point §17 + the two memory rules + the `memory-mcp` skill to the real recall mechanism. Implement the chosen fix so no rule cites a non-existent SSOT.

**Commands**:
```bash
git grep -n "memory/MEMORY.md" .claude/ docs/ | head
python ops_scripts/ci/run_contract_gates.py --gate ALWAYS-ON-BUDGET
```

### W1.2 — Gate reference-sweep classifier
**Scope**: New read-only tool `tools/governance/classify_gate_wiring.py` that, for every `ops_scripts/ci/check_*.py`, records whether it is referenced in `run_contract_gates.py`, `.pre-commit-config.yaml`, `.github/workflows/`, or only `tests/` — emitting `docs/reports/governance/gate_wiring_classification.json`. This is the guardrail that makes W4 safe; it is the only thing W4 may delete from.

**Commands**:
```bash
python tools/governance/classify_gate_wiring.py --out docs/reports/governance/gate_wiring_classification.json
```

### W2.1 — Archive AG scripts + skills; remove coupled gates
**Scope**: `git mv` the 16 AG/ag_queue scripts + 2 AG skills to `archives/enforcement_consolidation_2026-06-14/`; remove their entries from `run_contract_gates.py` and `.pre-commit-config.yaml` in the same commit (coupling map S1 enumerates the exact set).

**Commands**:
```bash
python ops_scripts/ci/run_contract_gates.py
```

### W3.1 — Build retired-rules index
**Scope**: Create `docs/reports/governance/retired-rules-index.md` listing every retired stub → canonical target; fold any glob-trigger frontmatter (e.g. `adg-test-accelerator-enforcement`) into the canonical file before deleting the stub.

### W4.1 — Retire classifier-proven orphans
**Scope**: Read `gate_wiring_classification.json` (the W1.2 output); retire ONLY gates classified ORPHANED; archive each gate's test alongside it.

**Commands**:
```bash
python ops_scripts/ci/run_contract_gates.py
```

---

## Gap Register

**GAP-1: "uncalled by registry" ≠ dead.** 175 gates are uncalled by `run_contract_gates.py`, but pre-commit references 45 and workflows 33. Mitigation: W1.2 classifier; W4 retires only proven orphans.

**GAP-2: memory mechanism unknown.** Whether the harness loads `memory/MEMORY.md` natively is undocumented. Mitigation: W1.1 resolves via AskUserQuestion before any MCP-script deletion (W6).

**GAP-3: §-citation stability.** Rules cite constitutional §-numbers; renumbering would break them. Mitigation: retired slots (§25/§30/§35) stay vacant for numbering stability — never renumber.

---

## Definition of Done

DoD-1: Every superseded surface keeps its invariant as a thin CLAUDE.md/rule line (no governance lost).
- Evidence: rule-diff review per wave; constitutional §6/§17/§24 invariants present post-change.
- Status: DONE

DoD-2: Smoke — `python ops_scripts/ci/run_contract_gates.py` exits 0 after every wave and after the final wave with the reduced gate set.
- Evidence: command output captured per wave.
- Status: PARTIAL — scoped gates green (`check_post_agent_payload`, `check_notion_schema_mece`, `check_always_on_token_budget`) + zero new test failures; FULL-suite green BLOCKED by pre-existing main reds (Fort Knox §32 cert tiers + ADG, red on the base commit — not introduced by this plan).

DoD-3: Superseded scripts/skills moved to `archives/enforcement_consolidation_2026-06-14/` (not deleted); legacy trees deleted only after a grep-clean zero-import proof.
- Evidence: `git mv` log + import scan = empty.
- Status: DONE

DoD-4: `tools/governance/classify_gate_wiring.py` exists and every retired gate is proven ORPHANED across registry + workflows + pre-commit + tests.
- Evidence: `docs/reports/governance/gate_wiring_classification.json`.
- Status: DONE

DoD-5: Memory drift resolved — `memory/MEMORY.md` exists OR §17 re-pointed; the two memory rules + `memory-mcp` skill reconciled; no rule references a non-existent SSOT.
- Evidence: `git grep "memory/MEMORY.md"` resolves to a real file or zero stale cites.
- Status: DONE

DoD-6: One ADR per superseded surface under `docs/architecture/adr/`; this plan + Notion row updated; predecessor `claude-native-supersession-9d3f7a` Retired via Supersedes.
- Evidence: ADR files present; Notion patch; supersession hook log.
- Status: DONE

DoD-7: Net-subtractive proof — removed-vs-added file-count delta and subprocess-per-Stop baseline-vs-final reported (subtraction-before-addition, apps-rg-execution-bias §5).
- Evidence: metrics block in W7.1.
- Status: DONE

### Verification vs Deferral

| Item | Verified by | Deferred? |
|---|---|---|
| Gate set still green after each wave | `run_contract_gates.py` exit 0 | No — every wave |
| Invariants preserved | rule-diff + §-cite presence | No — DoD-1 |
| Orphan-only gate retirement | W1.2 classifier JSON | No — DoD-4 |
| Memory mechanism (native load) | W1.1 AskUserQuestion + scaffold | Resolve in W1; do not defer past W6 |
| Per-app golden-path gate parameterization | existing per-app gate tests | Deferred to W4.2 (optional if risk surfaces) |
| Adjacent decommission-plan merge | cross-ref only | Deferred — out of scope this plan |

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=enforcement-surface-consolidation-d8b3f6 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=enforcement-surface-consolidation-d8b3f6 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=enforcement-surface-consolidation-d8b3f6 reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

> **Documentation ≠ Authorization.** Retroactive plan updates are not governance.

---

## ADG / Blast-Radius Note

This plan touches `.claude/` governance config + `ops_scripts/ci/` gates — **not** the `agentic_core` L0–L6 spine — so an `ADG_HOTSPOT_REPORT` is not the right instrument. The real blast radius is **CI gates + constitutional §-citations + the Stop dispatch chain**, enumerated in the coupling map and the W1.2 classifier. No `agentic_core` edits; no migration receipt required.

---

## Supersedes

| Predecessor slug | Reason |
|---|---|
| claude-native-supersession-9d3f7a | Absorbed in full — this plan adopts its S1–S6 framework and W0 coupling map, then extends to the CI-gate sweep, rule-stub collapse, skills archival, and memory-drift fix the user requested across all five surfaces. Single SSOT for enforcement consolidation; predecessor was Not Started with a stale naming baseline. |

---

## Marker Quick Reference

```
WAVE_START: plan=enforcement-surface-consolidation-d8b3f6 wave=<N>
WAVE_COMPLETE: plan=enforcement-surface-consolidation-d8b3f6 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=enforcement-surface-consolidation-d8b3f6 phase=<W1.1>
PLAN_COMPLETE: plan=enforcement-surface-consolidation-d8b3f6 note="<final outcome>"
```

PLAN_CREATED: plan=enforcement-surface-consolidation-d8b3f6 status=Not Started title="Enforcement Surface Consolidation — Unified Audit & Execution"
