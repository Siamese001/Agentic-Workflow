---
slug: grep-pretooluse-adg-gate-a3f1c7
title: Grep PreToolUse ADG-First Gate (deterministic chokepoint)
status: Not Started
plan_type: governance_hook_change
tier: T2
created: 2026-06-07
owner: Amit
files_in_scope:
  - .claude/governance/scripts/pre_grep_gate.py        # NEW — gate logic
  - .claude/hooks/before_grep.py                        # NEW — thin PreToolUse hook
  - .claude/settings.json                               # EDIT — register Grep matcher
  - .claude/governance/scripts/pre_user_prompt_grep_for_deps_warning.py  # EDIT — drop intent breadcrumb
  - tests/unit/ops_scripts/hooks/cursor/test_pre_grep_gate.py            # NEW — unit tests
  - .claude/rules/constitutional.md                     # EDIT (1 line) — note §28 now has a pre-block
---

# Grep PreToolUse ADG-First Gate

## Context (SCQA)

- **Situation.** This repo already declares ADG-first for all dependency / import / consumer /
  reference / blast-radius / fan-in / fan-out queries (constitutional §5, §22, §23, §28, §34).
  Enforcement today is **advisory + post-hoc only**: a prompt-submit warning
  ([pre_user_prompt_grep_for_deps_warning.py](.claude/governance/scripts/pre_user_prompt_grep_for_deps_warning.py),
  explicitly "does NOT block"), always-on rule salience, and a Stop-hook audit that logs
  `DEGRADED_FALLBACK` after the fact ([after_agent_governance_dispatch.py](.claude/hooks/after_agent_governance_dispatch.py)).
- **Complication.** [.claude/settings.json](.claude/settings.json) registers `PreToolUse` matchers for
  `Bash`, `Read`, `mcp__.*` — **but not the native `Grep` tool**. So a structural grep cannot be
  blocked before it runs; the strongest acting control is a log line. This is architecturally the
  same advisory pattern that proved un-enforceable in the prior Cursor/Windsurf setup.
- **Question.** Can we add the one missing deterministic chokepoint — a `PreToolUse` hook on `Grep`
  that hard-blocks (exit 2) a structural query when ADG is healthy, and fails open (allowing grep,
  emitting the §28 `DEGRADED_FALLBACK` contract) when ADG is unusable?
- **Answer.** Yes. A thin `before_grep.py` hook delegating to a `pre_grep_gate.py` gate, matched on
  `Grep` in `settings.json`. The gate is **high-precision** (block only when the user actually asked a
  deps question this turn *and/or* the pattern is unmistakably structural) and **health-aware**
  (fail-open when the latest ADG snapshot can't serve `nodes`). The same health probe would have
  caught today's broken-snapshot incident.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1.1, P1.2 | Build `pre_grep_gate.py`: intent classifier + ADG-health probe + allowlist + fail-open; unit tests | ~9k | Block contract = exit 2 (confirmed in `claude_hook_common.block`) | Not Started | All gate unit tests pass; structural→block, literal→allow, ADG-down→allow+marker |
| W2 | P2.1, P2.2 | Thin `before_grep.py` hook + register `Grep` matcher in `settings.json` + intent breadcrumb in prompt-submit hook | ~5k | Matcher `"Grep"` matches native tool; `type`+`command` only (§27) | Not Started | Hook wired; `python -m json.tool .claude/settings.json` clean; §27 schema gate passes |
| W3 | P3.1 | Verification: synthetic-payload smoke runs (3 cases), rule note, regression of existing hook tests | ~4k | Hooks fail-open on any error | Not Started | 3 smoke cases exit as expected; no existing hook test regresses |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Gate logic | `pre_grep_gate.py` | False-positive risk: inferring "deps query" from a grep pattern alone | ~6k | Not Started |
| P1.2 | Gate tests | `test_pre_grep_gate.py` | Cover block/allow/fail-open + bypass env | ~3k | Not Started |
| P2.1 | Thin hook | `before_grep.py` | Mirror `before_read_file.py` shape; receipt + fail-open | ~2k | Not Started |
| P2.2 | Wiring + breadcrumb | `settings.json`, `pre_user_prompt_grep_for_deps_warning.py` | §27 config purity; per-turn intent flag file | ~3k | Not Started |
| P3.1 | Verify + document | smoke runs, `constitutional.md` 1-line note | Don't wedge a turn; prove fail-open | ~4k | Not Started |

## Design

### Decision contract (`pre_grep_gate.py`)

Reads Claude Code event JSON from stdin (`tool_name`, `tool_input`). Returns **exit 2 (block)** only when
**all** hold; otherwise **exit 0 (allow)**:

1. `tool_name == "Grep"`.
2. **Structural intent present** — at least one of:
   - **Turn breadcrumb (primary, high-precision):** the prompt-submit hook detected a deps question
     this turn (regex already in `pre_user_prompt_grep_for_deps_warning.py`: "who uses / what depends on /
     fan-in / fan-out / blast radius / references to") and dropped a per-turn flag file
     `artifacts/cursor/_grep_deps_intent_turn.flag`. If the flag is present and fresh → structural.
   - **Pattern heuristic (secondary):** the `tool_input.pattern` is unmistakably structural —
     contains `import`, `from\s+\S+\s+import`, `extends`/`implements`, `def\s+\w+`, `class\s+\w+`, or a
     module-path token (`agentic_core\.`, `apps_\w+\.`). Bare-literal / TODO / FIXME / comment patterns
     never trip this.
3. **ADG is healthy** — see probe below.

Block message names the right tool by intent: fan-in → `adg_edge_fanin`; blast radius →
`adg_blast_radius`; consumers/who-uses → `adg_nodes_by_file` + `adg_edge_fanin`; layer → `adg_nodes_by_layer`.

### ADG-health probe (fail-open lever)

- Resolve newest `artifacts/adg/adg_indexed_*.sqlite` by mtime; open **read-only**; assert a `nodes`
  table exists and `SELECT count(*) FROM nodes > 0`. < 50 ms.
- **Healthy → enforce** (block per contract). **Unusable (missing file / no `nodes` / zero rows / any
  error) → fail-open allow**, and print the §28 line `DEGRADED_FALLBACK: reason=adg_snapshot_unusable`
  to stderr so the model emits the required marker.
- Bonus: this is exactly the signal that was wrong today (empty stub had no `nodes` table) — the gate
  would have self-diagnosed instead of silently mis-serving.

### Allowlist / escape hatches (never block)

- `tool_input.pattern` is a literal/TODO/comment search (no structural token, no turn-breadcrumb).
- Env bypass `ADG_GREP_GATE_BYPASS=1` (logged), consistent with `MCP_PREFLIGHT_BYPASS` / `GREP_BUDGET_BYPASS`.
- **Fail-open on any internal error** — a broken gate must never wedge a turn (house rule;
  mirrors `before_read_file.py` / `pre_mcp_gate.py`).

### Wiring (`settings.json`)

Add under `PreToolUse`:

```json
{ "matcher": "Grep",
  "hooks": [ { "type": "command",
    "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/before_grep.py\"" } ] }
```

`before_grep.py` mirrors `before_read_file.py`: `read_payload()` → call gate → `write_receipt(...)` →
`raise SystemExit(block(reason)|allow(...))`. Only `type`+`command` keys (constitutional §27).

## ADG_GRAPH_LAYER_EVIDENCE

This plan adds a **greenfield governance hook**; it does not refactor existing graph nodes.

- **Fan-in into changed files:** `pre_grep_gate.py` and `before_grep.py` are new — zero existing
  consumers (no `resolves_callsite` / `imports` edges point at them yet). `settings.json` is config,
  not an ADG node.
- **Blast radius:** confined to the hook surface; the only runtime coupling is the new per-turn flag
  file written by the existing prompt-submit hook (additive, fail-open).
- **MVs/semantic edges consulted:** N/A — no existing-module fan-in to rank; the change introduces a
  control, it does not move or re-layer code. Health probe reads the canonical
  `artifacts/adg/adg_indexed_*.sqlite` directly (SQLite = canonical truth, §23).

## Definition of Done

| # | Criterion | Verify / Defer |
|---|-----------|----------------|
| 1 | `pre_grep_gate.py` blocks (exit 2) a structural Grep when ADG healthy | Verify — unit test + smoke |
| 2 | Literal/TODO Grep allowed (exit 0) | Verify — unit test |
| 3 | ADG-unusable → allow (exit 0) + `DEGRADED_FALLBACK:` on stderr | Verify — unit test (temp empty snapshot) |
| 4 | `ADG_GREP_GATE_BYPASS=1` → allow + logged | Verify — unit test |
| 5 | Any gate exception → fail-open allow (turn never wedged) | Verify — unit test (malformed stdin) |
| 6 | **Smoke run:** `echo '<payload>' \| python .claude/hooks/before_grep.py` exits 2 / 0 / 0 for the three cases | Verify — P3.1 |
| 7 | `python -m json.tool .claude/settings.json` clean; §27 schema gate passes | Verify — P3.1 |
| 8 | No existing hook unit test regresses | Verify — P3.1 targeted pytest |

## Open Decisions (for review before execution)

1. **Match `Glob` too?** Default: **no** (filename matching ≠ deps). Easy to add later.
2. **Breadcrumb vs pattern-only.** Default: ship **both** (breadcrumb primary, pattern secondary) for
   precision. Could ship breadcrumb-only first if you want minimal false positives.
3. **Block vs warn for the pattern-heuristic tier.** Default: **block** only when breadcrumb present;
   pattern-heuristic alone → **warn** (exit 0 + stderr) to keep false-positives non-disruptive. (This is
   the conservative split; say the word to make pattern-heuristic also hard-block.)

## Notes

- Registration: per §36 a `PLAN_CREATED:` marker is emitted on creation; the Notion Plans-DB row
  (Status="Not Started") will be posted **before** any wave executes — not before your review.
- No code is edited until `SR_APPROVAL: APPROVED` after you review this plan.
