# ADR-100 — Enforcement Surface Consolidation (closeout)

- **Status:** Accepted
- **Date:** 2026-06-14
- **Plan:** [enforcement-surface-consolidation-d8b3f6.md](../../../plans/enforcement-surface-consolidation-d8b3f6.md)
- **Absorbs:** `claude-native-supersession-9d3f7a` (its S1–S6 framework + W0 coupling map) → retired via the Supersedes mechanism.
- **Related:** ADR-093 (Author-Gate → AskUserQuestion), ADR-094 (SR markers → plan mode), ADR-095 (memory ritual → file memory), ADR-096 (deferred-scope/next-step → spawn_task), ADR-097 (mcp-serialization retirement + cleanup).

## Context

The `.claude/` governance layer — ported from the prior Cursor/Windsurf IDE configs — accumulated
**emulation machinery** that native Claude Code features now supersede: an Author-Gate
packet/marker/ledger pipeline (native `AskUserQuestion`), `SR_*` plan markers (native plan mode),
a mandatory memory-MCP ritual (native file memory), `DEFERRED_SCOPE:`/`NEXT_STEP:` marker → hook →
Notion capture (native `spawn_task`), an `mcp-serialization` batching rule (native parallel MCP), and
two legacy trees. Much of it was *declared* superseded (rules marked DEPRECATED, constitutional slots
RETIRED) but **never cleaned** — ~16 AG scripts, ~21 redirect rule stubs, dead CI gates, and the S4
capture hooks still loaded every session.

## Decision

Apply the proven ADG/supersession pattern uniformly — **invariant-in-`CLAUDE.md`,
procedure-in-native-feature, machinery-removed** — gating every deletion behind a reference sweep so
nothing wired elsewhere is removed. Net-subtractive, zero governance lost.

| Wave | Surface | Outcome | Invariant now lives at |
|---|---|---|---|
| W1 | Audit + memory drift | `memory/` SSOT scaffold; `classify_gate_wiring.py` reference-sweep tool | §17 / `memory/MEMORY.md` |
| W2 | S1 Author-Gate | AG author-facing layer + ~15 scripts + 2 skills + AG tests removed (shared ledger backbone kept) | `AskUserQuestion` + constitutional §6 |
| W3 | Rule stubs | 18 pure-redirect rule stubs deleted (66→48 rule files); `retired-rules-index.md` preserves the redirect map | canonical rule targets + §-citations |
| W4 | CI gates | 19 classifier-proven-dead orphan gates retired (of 103 registry-orphans, **84 proven still-referenced → kept**) | `gate_wiring_classification.json` |
| W5 | Skills/aliases | 6 redundant tavily command aliases removed; dormant-MCP skills KEPT per documented intent | `mcp-notes.md` |
| W6 | S6 legacy/serialization | legacy trees + `mcp-serialization.md` deleted (concurrent); dangling `CLAUDE.md` index row repointed; 3 retired-marker captures unwired from the per-Stop chain | native parallel MCP; `pre_mcp_gate` keeps Notion/GitKraken checks |
| W7 | S4 capture + closeout | S4 capture hooks (`post_agent_deferred_scope_capture`, `post_agent_next_step_capture`) + `_deferred_scope_plan_scaffold` + `next_step_miss_detector` deleted after decoupling `backfill_backlog_plan_relation` and emptying the MECE gate's writer list | native `spawn_task` + constitutional §24 |

### Kept (explicitly NOT retired — signal would be lost)

- **`tools/priority/deferred_scope_scorer`** subsystem — live P-Band backlog scoring with many
  consumers (`backfill_backlog_scores`, `batch_rescore_notion`, `batch_triage_enricher`,
  `infer_and_score_unscored`, `recover_deferred_scope_pendings`); ADR-031.
- **S5 wave-lifecycle** (`post_agent_wave_lifecycle_capture`, `post_agent_wave_completion_audit`) —
  the live `WAVE_COMPLETE`/`PLAN_COMPLETE` → Notion bridge used by multi-wave plan governance, §36,
  and `check_plan_notion_wave_freshness`. The supersession "S5 → TodoWrite" mapping does not hold
  while Notion plan governance is active.
- **17 `check_apps_rg_*` runtime gates, 5 notion-status gates, Fort Knox (§32), router ledgers (§29),
  the ADG MCP** — genuine runtime intelligence/evidence, not emulation.

## Consequences

- **Net-subtractive**: governance scripts 111 → 91 (−20); rule files 66 → 48 (−18); per-Stop
  dispatch in-process loads 13 → 10; thousands of lines removed across the plan with one classifier
  tool + one retired-rules index + a memory scaffold added.
- **Reversibility**: deletions preserved in git history (`check_structure_policy.py` forbids a root
  `archives/` dir, so retirement uses `git rm`, not move-to-archives).
- **Reference-swept safety**: every gate/hook retirement was proven dead across registry +
  pre-commit + workflows + tests before removal — the W4 sweep found only 19 of 103 registry-orphans
  truly dead (a blind mass-delete would have broken 84).
- **No `agentic_core` edits**; no migration receipt required.
