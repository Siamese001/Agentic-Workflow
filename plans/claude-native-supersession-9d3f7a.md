---
slug: claude-native-supersession-9d3f7a
status: Not Started
plan_type: governance_refactor
dod_exempt: false
---

# Claude-Native Supersession — Retire Cursor/Windsurf Emulation Machinery

## Context (SCQA)

- **Situation:** The `.claude/` governance layer was migrated from Cursor/Windsurf. It carries
  **~95 active governance scripts**, **10 Pre/PostToolUse/Stop hooks**, a **~12-subprocess
  dispatch on every `Stop`** (`after_agent_governance_dispatch.py`), plus `_legacy_cursor/` and
  `_legacy_windsurf/` trees and **24 slash commands**.
- **Complication:** Much of this machinery *emulates* capabilities Claude Code now ships natively.
  The precedent is already proven: the ADG-first "grep-is-not-primary" enforcement no longer needs
  the heavy `pre_prompt_classifier` + `post_*_adg_audit` hook pair — the `graph-analysis` skill
  auto-loads and the `CLAUDE.md` operating contract carries the invariant. Cursor lacked
  auto-loading skills, a structured-choice tool, plan mode, file memory, and background-task chips,
  so the repo *built* them out of markers + hooks + audit scripts. Claude Code has them.
- **Question:** Where else can a native Claude Code feature supersede cumbersome ported machinery,
  and in what order should we cut it over without losing the underlying invariant?
- **Answer:** Six emulation surfaces, ranked by leverage. Apply the **proven ADG pattern** to each:
  keep the *invariant* as a thin always-on line in `CLAUDE.md`/a rule, move the *procedure* to a
  native feature (+ skill where procedural depth is needed), and **archive** (not delete) the heavy
  scripts. W0 maps CI-gate / constitutional-rule coupling first so no wave silently breaks a gate.

## Supersession Thesis (the six surfaces)

| # | Ported emulation (current burden) | Native Claude Code feature that supersedes it | Leverage |
|---|---|---|---|
| **S1** | **Author-Gate** packet-builder + ui-renderer skills, `_author_gate_queue`, marker grammar (`AUTHOR_GATE_PACKET`/`DECISION_CAPTURED`), 6-script AG audit chain, queue-seed/drain hooks, ledger-integrity + marker-validator | **`AskUserQuestion`** — renders clickable options with descriptions natively. Precedent kept in **file memory**, not a bespoke SQLite ledger + Notion mirror. | ★★★★★ |
| **S2** | **`SR_INTAKE/SR_PLAN/SR_APPROVAL/SR_EXECUTE/SR_VERIFY`** marker scheme + `pre_prompt_classifier.py` + `plan-first-enforcement.md` | **Plan mode** (`EnterPlanMode`/`ExitPlanMode`) — "no edits before approval" is the native contract the SR markers hand-rolled. | ★★★★☆ |
| **S3** | **Memory MCP ritual** — mandatory `mem_recall_session_start` first-call, `mem_cleanup_stale`, staleness/purge gates, `memory-notion-writeback` 15/3 discipline | **Native file-based memory** (`memory/MEMORY.md` + per-fact files) — already live this session; no purge gate needed (curated, not auto-grown). | ★★★★☆ |
| **S4** | **Deferred-scope / next-step** marker+hook pipeline — `DEFERRED_SCOPE:`/`NEXT_STEP:` markers, capture + miss-detector + scorer + recovery hooks, Notion Backlog posting | **`spawn_task`** background-task chips — one click spins out-of-scope work into its own session/worktree. | ★★★☆☆ |
| **S5** | **Wave-lifecycle markers** — `wave_execution_state.py`, `WAVE_COMPLETE`/`PHASE_COMPLETE`/`PLAN_COMPLETE`, `post_agent_wave_*` capture/audit | **`TodoWrite`** for in-session orchestration; Notion stays only as the explicit durable store. | ★★★☆☆ |
| **S6** | **Hook-spawn overhead + legacy trees + thin-alias commands + MCP-serialization rule** — 12 subprocesses/Stop; `_legacy_cursor/`+`_legacy_windsurf/`; ~10 `*.md` commands that only point at an existing skill; `mcp-serialization.md` one-call-per-block batching rule | Native parallel MCP calls; skills auto-load (commands redundant); in-process dispatch. | ★★★☆☆ |

> **Non-negotiable for every wave:** the *invariant* survives even when the *machinery* is archived.
> S1 still requires "stop and ask before ambiguous edits" — it just becomes a direct `AskUserQuestion`
> instead of a packet→render→marker→audit→ledger pipeline. We are removing emulation, not governance.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W0** | P0.1–P0.3 | Supersession audit & coupling map (no edits) | ~25k | CI gates + constitutional §-cites are the real blast radius | Not Started | Decision matrix: each Sn → native feature → coupled gates/rules/hooks → reversibility |
| **W1** | P1.1–P1.4 | **S1** Author-Gate → native `AskUserQuestion` | ~60k | `AskUserQuestion` already in use; precedent value is low-volume | Not Started | AG packet/render/queue/audit chain archived; invariant 1-liner in CLAUDE.md; gates green |
| **W2** | P2.1–P2.3 | **S2** SR markers → native plan mode | ~35k | Plan mode honored by harness for T2/T3 | Not Started | `pre_prompt_classifier` SR-enforcement retired; rule rewritten to plan-mode contract |
| **W3** | P3.1–P3.3 | **S3** Memory MCP ritual → native file memory | ~40k | Native memory persists per-project | Not Started | Session-start recall + writeback on native memory; purge/staleness gates retired |
| **W4** | P4.1–P4.2 | **S4** Deferred-scope/next-step → `spawn_task` | ~30k | spawn_task chips acceptable substitute for Notion auto-post | Not Started | Marker+hook capture pipeline archived; agent-suggestion path uses spawn_task |
| **W5** | P5.1–P5.4 | **S5/S6** Lifecycle + cleanup (hooks, legacy, commands, mcp-serialization) | ~45k | Nothing imports legacy trees | Not Started | Dispatch slimmed; legacy trees deleted; alias commands removed; serialization rule retired |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P0.1 | Coupling inventory | `ops_scripts/ci/check_*`, `.claude/rules/*`, `.claude/settings.json` | Marker grammar is cited by many gates | ~10k | Not Started |
| P0.2 | Native-feature fit test | each Sn | Confirm native feature covers the *invariant*, not just the happy path | ~8k | Not Started |
| P0.3 | Reversibility + cutover order | this plan | Some gates are constitutional §-numbered (load-bearing) | ~7k | Not Started |
| P1.1 | CLAUDE.md AG invariant rewrite | `CLAUDE.md`, `003-cursor-author-gate-hitl.md` | Keep "stop & ask" trigger doctrine | ~12k | Not Started |
| P1.2 | Decision precedent → file memory | `memory/`, `refactor-decision-memory` skill | Replace SQLite ledger lookups | ~14k | Not Started |
| P1.3 | Archive AG scripts + skills | `_author_gate_*`, AG chain, packet-builder/ui-renderer skills | 8+ scripts + 2 skills + queue | ~20k | Not Started |
| P1.4 | Retire AG CI gates / §30,§35 markers | `ops_scripts/ci/check_*ag*`, `check_decision_ledger_*` | §30/§35 are constitutional | ~14k | Not Started |
| P2.1 | Rewrite SR rule → plan-mode contract | `plan-first-enforcement.md`, `CLAUDE.md` | Preserve T2/T3 gating threshold | ~12k | Not Started |
| P2.2 | Retire `pre_prompt_classifier` SR path | `pre_prompt_classifier.py` | Also hosts ADG step-0 classify | ~13k | Not Started |
| P2.3 | structured-reasoning skill → plan-mode notes | `structured-reasoning` skill | Keep retrieval-discipline content | ~10k | Not Started |
| P3.1 | Session-start recall → native memory | `memory-management.md`, §17 | First-call mandate is constitutional | ~14k | Not Started |
| P3.2 | Writeback discipline → native memory files | `memory-notion-writeback.md`, `writeback-discipline` skill | 15/3 rule keeps, target changes | ~14k | Not Started |
| P3.3 | Retire purge/staleness gates | `mem_cleanup_stale`, `check_memory_health.py`, `purge_sync.py` | Keep MCP only for graph queries actually used | ~12k | Not Started |
| P4.1 | Agent-suggestion path → spawn_task | `next-step-capture.md`, `deferred-scope-capture.md` | Keep §24 scored-wave-deferral path | ~16k | Not Started |
| P4.2 | Archive capture/miss/scorer hooks | `post_agent_deferred_scope_capture.py`, `post_agent_next_step_*` | Notion auto-post removal | ~14k | Not Started |
| P5.1 | Slim Stop dispatch | `after_agent_governance_dispatch.py` | Drop superseded chain members | ~12k | Not Started |
| P5.2 | Delete legacy trees | `_legacy_cursor/`, `_legacy_windsurf/` | Confirm zero imports first | ~10k | Not Started |
| P5.3 | Remove thin-alias commands | `.claude/commands/*.md` aliases | Keep skills as SSOT | ~10k | Not Started |
| P5.4 | Retire MCP-serialization rule | `mcp-serialization.md`, `pre_mcp_gate.py` batching | Keep Notion-token + GitKraken checks | ~13k | Not Started |

## Recommended Approach (SVP lens)

Apply the **ADG precedent** uniformly — **invariant-in-CLAUDE.md, procedure-in-native-feature,
machinery-to-`archives/`**:

1. **Operational simplicity** — every archived script is one fewer subprocess/marker/gate to keep green.
2. **Archival over deletion** — move superseded scripts to `archives/claude_native_supersession_<date>/`
   (W1–W4); only delete the already-segregated `_legacy_*` trees in W5 after a zero-import proof.
3. **Zero-regression** — each wave ends with `python ops_scripts/ci/run_contract_gates.py` green; a gate
   that *only* validated the retired marker is retired *with* its machinery in the same wave (no orphan gates).
4. **Documentation discipline** — one ADR per superseded surface recording the native-feature mapping.

**Cutover order rationale:** W1 (Author-Gate) first = largest burden + cleanest native fit
(`AskUserQuestion` is already how decisions surface). Memory (W3) and SR/plan-mode (W2) are high-value
but touch constitutional §17/§-numbered slots, so they follow the W0 coupling map. W4–W5 are cleanup
with the smallest blast radius.

## ADG / Blast-Radius Note

This plan touches `.claude/` governance config + `ops_scripts/ci/` gates — **not** the `agentic_core`
L0–L6 spine — so an `ADG_HOTSPOT_REPORT` is not the right instrument. The real blast radius is
**CI gates + constitutional §-citations + the Stop dispatch chain**, enumerated in **W0/P0.1**. No
`agentic_core` edits; no migration receipt required.

## Definition of Done

| # | Criterion | Verify / Defer |
|---|---|---|
| 1 | W0 decision matrix exists mapping each S1–S6 → native feature → coupled gates/rules → reversibility | Verify: matrix artifact in `docs/reports/` |
| 2 | Every superseded surface keeps its **invariant** as a thin CLAUDE.md/rule line (no governance lost) | Verify: rule diff review |
| 3 | Superseded scripts moved to `archives/` (W1–W4) or deleted with zero-import proof (W5 legacy trees) | Verify: `grep`-clean import scan + `adg_health` |
| 4 | Each wave ends with `python ops_scripts/ci/run_contract_gates.py` → exit 0 (no orphan gates) | Verify: command output per wave |
| 5 | One ADR per superseded surface under `docs/architecture/adr/` | Verify: ADR files present |
| 6 | Smoke: `python ops_scripts/ci/run_contract_gates.py` exits 0 after final wave with reduced gate set | Verify: command output |
| 7 | Stop-dispatch subprocess count measurably reduced (baseline vs final) | Verify: count in `after_agent_governance_dispatch.py` |

## Out of Scope / Deferred

- Replacing the **ADG MCP** itself (it is the SSOT, not emulation — keep it).
- **Notion** as a durable cross-day store (real external system; only the *auto-posting markers* are emulation).
- **Fort Knox certification** machinery (§32) — genuine evidence integrity, not a Cursor port.
- Closed-loop **router ledgers** (§29) — runtime intelligence, not harness emulation.

PLAN_CREATED: plan=claude-native-supersession-9d3f7a status=Not Started title="Claude-Native Supersession — retire Cursor/Windsurf emulation machinery"
