---
slug: governance-rule-residue-cleanup-7e3a91
plan_type: governance_cleanup
status: Completed
created: 2026-06-07
owner: Claude Code
supersedes: []
relates_to:
  - cursor-naming-rename-w5-b4f1a9                    # live-wiring rename (owns A–C,F–H); this plan owns the residue it does NOT cover
  - cursor-windsurf-codeium-decommission-dec0de       # parent decommission (prose rebrand + relocation)
---

# Governance-Rule Residue Cleanup — the Doc/Staleness Debt No Decommission Wave Owns

> Captures the constitutional-floor and rule-pointer debt surfaced in the 2026-06-07 review that falls
> **outside** both decommission plans. The `cursor-naming-rename-w5` plan owns the IDE *live-wiring* rename
> (`post_cursor_agent_*`, `artifacts/cursor/`, `.cursor/state/`, `tools/windsurf/`). The parent dec0de plan
> delivered the *prose rebrand*. Neither plan claims: floor numbering hygiene, deprecated-stub repointing,
> retired-MCP references, or the stray `ask_user_question` tool-name. This plan does.

## Context (SCQA)

- **Situation.** A review of `.claude/rules/constitutional.md` + its always-on rules found a residue of
  non-IDE staleness: a duplicated/dead constitutional slot, a missing slot number, several `§` pointers into
  **deprecated stub** rule files, references to **MCP servers already trimmed from `.mcp.json`**, and the
  Cursor-era lowercase `ask_user_question` tool-name (real tool is `AskUserQuestion`).
- **Complication.** These were never in scope for the decommission effort: the IDE plans rename *wiring*
  named after Cursor/Windsurf, not general doc hygiene or ADG-consolidation/​MCP-trim follow-through. So the
  residue was unowned. Two hazards realized during execution: (a) constitutional `§` numbers are
  cross-referenced across rules — blind renumbering breaks citations; (b) `ask_user_question` is **not pure
  prose** — a live capture hook keys on the lowercase string, and the `cursor-naming-rename-w5` rename was
  already mid-flight on that exact token.
- **Question.** How to clear the residue without breaking `§`-citation links, the always-on token-budget gate
  (§33), or any live capture/audit pipeline?
- **Answer.** One deferral-eligible wave per residue class, **doc-only and lowest-blast first**. Keep `§`
  numbering **stable** (annotate, never renumber). Hand the wiring-adjacent `ask_user_question` token to the
  in-flight `cursor-naming-rename-w5` rename rather than sweep it in parallel.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | R1.1–R1.2 | Constitutional floor hygiene — §0≡§14 dup + missing §25 (annotate, no renumber) | ~5k | `§14`/`§25` cited elsewhere → numbering must stay stable | ✅ Done (2026-06-07) | §14 now explicit alias-of-§0; §25 reserved-note added; citation map proved §14 cited by 2 rules (no renumber); token-budget gate EXIT 0 |
| W2 | R2.1–R2.2 | Repoint deprecated-stub pointers (§22 + Extended-Doctrine list) | ~6k | Live targets exist in `adg-analysis-procedures.md` / `adg-canonical-invariants.md` | ✅ Done (2026-06-07) | §22 → `adg-analysis-procedures.md` §3; Extended-Doctrine list collapsed 5 deprecated stubs + dropped inactive `global_rules.md`. **§5 had no stub pointer — review over-flagged; left intact.** |
| W3 | R3.1–R3.2 | Correct retired-MCP references | ~6k | Native substitutes per `CLAUDE.md` "Not in `.mcp.json`" table | ✅ Done (2026-06-07) | `sequential-thinking-enforcement.md` "Task Manager MCP" → `structured-reasoning`. **§13 verified script-based (`adg_redis_ingest.py` exists) + §17 uses live memory MCP — both non-stale, left intact (review over-flagged).** |
| W4 | R4.1–R4.2 | `ask_user_question` → `AskUserQuestion` | ~8k | Token load-bearing + W5-rename in flight | ✅ Done — handed off (2026-06-07) | Blast-radius confirmed the functional token is owned by the in-flight `cursor-naming-rename-w5` rename (already renaming `post_*_ask_user_question_packet_audit.py`). Parallel prose sweep would collide → **deferred to that plan by design**; no edit here. |
| W5 | R5.1 | Verify + close | ~3k | All prior waves green | ✅ Done (2026-06-07) | token-budget gate EXIT 0; all 4 governance markers confirmed on `origin/main`; plan artifact committed + FF to main |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| R1.1 | Grep `§14`/`§0`/`§25` citation map | `.claude/rules/**` | Must know who cites the slots before touching them | ~2k | ✅ |
| R1.2 | Annotate §0≡§14 + reserve §25 | `.claude/rules/constitutional.md` | Keep numbering stable | ~3k | ✅ |
| R2.1 | Confirm live targets + map | `adg-analysis-procedures.md`, `adg-canonical-invariants.md` | Stubs redirect; cite the real § | ~2k | ✅ |
| R2.2 | Repoint §22 + Extended-Doctrine list | `constitutional.md` | `global_rules.md` inactive — dropped | ~4k | ✅ |
| R3.1 | Map retired servers → substitutes | `CLAUDE.md`, `.mcp.json` | Verify `adg_redis_ingest.py` still exists (it does) | ~3k | ✅ |
| R3.2 | Correct sequential-thinking Task-Manager ref | `sequential-thinking-enforcement.md` | §13/§17 verified non-stale, left intact | ~3k | ✅ |
| R4.1 | Blast-radius: `ask_user_question` token | hooks, governance scripts, markers | Token load-bearing + live rename in flight | ~4k | ✅ |
| R4.2 | Handoff to `cursor-naming-rename-w5` | — | No parallel sweep; avoid collision | ~4k | ✅ (handed off) |
| R5.1 | Verify + close | whole repo, Notion | Distinguish intentional history from residue | ~3k | ✅ |

## Wave Detail

### W1 — Constitutional floor hygiene ✅
- **R1.1** Citation map: `git grep` proved `§14` is cited as "the subprocess-timeout rule" by `query-progress-bar.md` + `python-dash-c-quote-hazard.md`, and `§25` has **zero** citers → renumbering forbidden; annotate only.
- **R1.2** §14 made an explicit reserved-alias-of-§0 with a do-not-renumber note; §25 given a reserved-slot note. No slot renumbered.

### W2 — Deprecated-stub repointing ✅
- §22 repointed `adg-graph-layer-enforcement.md` → `adg-analysis-procedures.md` §3 (live merged location).
- Extended-Doctrine list collapsed the 5 deprecated ADG/anti-pattern stubs into `adg-analysis-procedures.md` + `adg-canonical-invariants.md` and dropped inactive `global_rules.md`; added a repoint provenance note.
- **Correction:** §5 had no stub pointer (review over-flagged) — left intact.

### W3 — Retired-MCP reference correction ✅
- `sequential-thinking-enforcement.md` "Use Task Manager MCP" → `structured-reasoning` (native), with retired-MCP note.
- **Correction:** §13 is script-based (`tools/adg/adg_redis_ingest.py` confirmed present) and §17 uses the **live** memory MCP — both non-stale; the green-light gate semantics were NOT touched (review over-flagged both).

### W4 — `ask_user_question` → handed off ✅
- Blast-radius confirmed the lowercase token is load-bearing in the live capture pipeline and that `cursor-naming-rename-w5` was already mid-rename of `post_*_ask_user_question_packet_audit.py`. A parallel prose sweep here would collide with that uncommitted rename → **deferred to `cursor-naming-rename-w5` by the plan's pre-declared escape hatch.** No edit made under this plan.

### W5 — Verify + close ✅
- token-budget gate (`check_always_on_token_budget.py`) EXIT 0.
- All four governance markers confirmed present on `origin/main` (the W1–W3 edits rode to main with the decommission squash `#247`).
- This plan artifact committed on `chore/gov-residue-main-7e3a91` (off `origin/main`) and fast-forwarded to main.

## Definition of Done

| # | Criterion | Verify / Defer | Result |
|---|-----------|----------------|--------|
| 1 | `§14`/`§25` citation map captured before any constitutional edit | grep output in R1.1 | ✅ §14 cited by 2 rules; §25 zero citers |
| 2 | §0≡§14 annotated and §25 gap documented, **without renumbering** | read `constitutional.md` diff | ✅ |
| 3 | Every constitutional `§` pointer resolves to a live, non-stub, non-inactive rule | each link target checked | ✅ |
| 4 | No retired MCP (`redis`/`pytest_mcp`/`task_manager`) named as a live dependency; §13 gate not weakened | grep + read §13 | ✅ |
| 5 | `ask_user_question` prose handled or explicitly handed to `cursor-naming-rename-w5` | R4.1 classification | ✅ handed off |
| 6 | `check_always_on_token_budget.py` exits 0 | command output | ✅ EXIT 0 |
| 7 | Wave edits present on `origin/main`; plan artifact committed + FF to main | git show / push | ✅ |

**Verification vs Deferral:** W1–W3 were committed doc-only, low-risk core. W4 was deferral-eligible and was
correctly handed off to `cursor-naming-rename-w5` (the functional `ask_user_question` rename). No
`agentic_core/` edits in this plan.

## Risk / blast-radius notes
- **Stable numbering (W1):** constitutional `§` numbers are cited across rules + CI gate messages → annotated, never renumbered.
- **§13 is a gate, not just prose (W3):** only the named backend was assessed; the green-light semantics + `adg_health` fallback were preserved (no edit needed — verified non-stale).
- **W4 overlap (D):** the lowercase `ask_user_question` token is the same class as `cursor-naming-rename-w5`'s `post_cursor_agent_*` rename → routed there to avoid double-ownership.

## Execution Log (2026-06-07)
- Registered in Notion Plans DB (page `37827693-f55c-81d1-9b99-d74f24c802af`, Status Not Started at creation).
- W1–W3 edits applied to `constitutional.md` + `sequential-thinking-enforcement.md`; carried (via a concurrent
  decommission orchestration on shared worktrees) into the `w5-b4f1a9` decommission squash and landed on
  `origin/main` (PR `#247`). Confirmed present on `origin/main`.
- W4 handed off to `cursor-naming-rename-w5`. W5 verification gate green.
- This artifact created on a fresh branch off `origin/main` and fast-forwarded to main to close the plan.
- RCA captured this session: the `.claude/` edit-guard is pierced only by scoped `Edit/Write(.claude/<sub>/**)`
  allow rules, NOT by `bypassPermissions` — memory `claude-folder-relocatability` corrected accordingly.
