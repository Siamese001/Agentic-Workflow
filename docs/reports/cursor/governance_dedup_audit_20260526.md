# Governance deduplication audit — 2026-05-26

**Scope:** `AGENTS.md`, `.cursor/rules/`, `.cursor/skills/`, `.cursor/hooks.json`, pre/post Cursor hooks.  
**Goal:** Eliminate redundancies, inconsistencies, and stale SSOT references without weakening invariants.

## Executive summary

| Area | Finding | Action taken |
|------|---------|--------------|
| Always-on rule count | `.cursor/README.md` said **3** rules; repo policy is **4** (`003` Author-Gate) | README corrected |
| `RULES_INDEX.md` | Missing on disk; 19+ rules linked broken `#always-on-discipline` anchor | Generator fixed (`.mdc` scan); index regenerated |
| Post-agent hooks | Two chains: `after_agent_governance_dispatch` (wired) vs `after_agent_author_gate_audits` (unwired duplicate) | Legacy hook documented; CI wiring points to dispatch only |
| Author-Gate prose | Full pipeline duplicated in `pre_user_prompt_author_gate_reminder.py` and `003` rule | Reminder shortened to pointer + replay path |
| Obsolete scripts | `post_cursor_agent_author_gate_audit.py`, `author_gate_suite` not in chain | Marked obsolete in script headers; matrix already lists them |
| MCP skills | AGENTS table links to redirect stubs; bodies duplicate `mcp-integration` | AGENTS note added; stubs kept for backward compat |
| Rules generator | Scanned `*.md` only → **0 rules** in index | Now scans `*.mdc`, maps `alwaysApply` |

## Tier model (canonical)

```text
Tier-1 (always injected):  AGENTS.md + 000–003 .mdc (alwaysApply: true)
Tier-2 (on demand):       other .cursor/rules/*.mdc
Tier-3 (progressive):      .cursor/skills — mcp-integration sections > redirect stubs
Hooks (deterministic):     .cursor/hooks.json → hooks/*.py → scripts/post_cursor_agent_*.py
```

Inventory: [`governance_tier_inventory.json`](governance_tier_inventory.json) (~4.6k tokens Tier-1, PASS).

## Findings detail

### 1. Documentation drift

- **`.cursor/README.md`** listed three always-on rules; `governance_tier_inventory.json` and `check_cursor_optimized_config.py` expect four.
- **`.cursor/RULES_INDEX.md`** did not exist; many `.mdc` files referenced `.cursor/RULES_INDEX.md#always-on-discipline`.

### 2. Hook chain duplication

**Wired (SSOT):** `hooks.json` → `after_agent_governance_dispatch.py` → ADG audit → AG script chain → Notion auditor → `post_cursor_agent_dispatch.py`.

**Unwired legacy:** `after_agent_author_gate_audits.py` duplicates the AG subset of governance dispatch. Not in `hooks.json`; risks double-runs if re-wired.

**Obsolete (manual/CI only):** `post_cursor_agent_author_gate_audit.py`, `post_cursor_agent_author_gate_suite.py` per [`governance_w3_hook_audit_matrix.md`](governance_w3_hook_audit_matrix.md).

### 3. Author-Gate triple SSOT

| Surface | Role |
|---------|------|
| `003-cursor-author-gate-hitl.mdc` | Always-on invariant + pipeline |
| `author-gate-enforcement.mdc` | Scoring, triggers, examples (on demand) |
| `pre_user_prompt_author_gate_reminder.py` | Violation replay + keyword nudge (must not restate full pipeline) |

### 4. Skills vs AGENTS.md MCP table

W4 consolidated per-server skills into `mcp-integration` §1–§13. Thirteen redirect stubs remain (`metadata.deprecated: true`). AGENTS.md still links stub paths in the Skill column — acceptable for discovery, but agents should load **`mcp-integration`** sections for procedure.

### 5. Windsurf mirror — **CLOSED (W4)**

13× `always_on` demoted to `model_decision` (2026-05-26). Map: [windsurf_always_on_demotion_map_20260526.md](windsurf_always_on_demotion_map_20260526.md). Gate reports **0 B** windsurf always_on. `.windsurf/` tree not deleted (intentional).

### 6. Deferred items — **CLOSED (closeout plan COMPLETED)**

**Follow-up plan:** [governance-dedup-closeout-e8a4c2.md](../../.cursor/plans/governance-dedup-closeout-e8a4c2.md) — **COMPLETED 2026-05-26**.

**Closeout manifest:** [governance_dedup_closeout_receipt.md](governance_dedup_closeout_receipt.md) · [governance_dedup_closeout_receipt.json](governance_dedup_closeout_receipt.json)

| Item | Wave | Status |
|------|------|--------|
| Obsolete hook scripts | W1 | PASS |
| Native config legacy refs | W2 | PASS |
| Plan sprawl (86 → 11) | W3 | PASS |
| Windsurf always_on demotion | W4 | PASS |
| MCP stub Skill column autogen | — | DEFERRED P4 (mitigated) |

## Verification

```bash
python ops_scripts/ci/check_ag_hook_wiring.py          # AG-WIRE-1..4
python ops_scripts/ci/check_agents_md_sync.py          # autogen blocks
python .cursor/scripts/check_cursor_optimized_config.py
python .cursor/scripts/generate_rules_index.py --check
```

## Files changed (this pass)

- [`AGENTS.md`](../../AGENTS.md) — governance map, MCP stub note, dedup audit link
- [`.cursor/README.md`](../../.cursor/README.md) — four rules, hooks table
- [`.cursor/RULES_INDEX.md`](../../.cursor/RULES_INDEX.md) — regenerated
- [`.cursor/scripts/generate_rules_index.py`](../../.cursor/scripts/generate_rules_index.py) — `.mdc` + SSOT sections
- [`.cursor/rules/author-gate-enforcement.mdc`](../../.cursor/rules/author-gate-enforcement.mdc) — hook integration path
- [`.cursor/hooks/after_agent_author_gate_audits.py`](../../.cursor/hooks/after_agent_author_gate_audits.py) — legacy banner
- [`.cursor/scripts/pre_user_prompt_author_gate_reminder.py`](../../.cursor/scripts/pre_user_prompt_author_gate_reminder.py) — shortened reminder
- [`.cursor/scripts/post_cursor_agent_author_gate_audit.py`](../../.cursor/scripts/post_cursor_agent_author_gate_audit.py) — obsolete banner
- [`ops_scripts/ci/check_ag_hook_wiring.py`](../../ops_scripts/ci/check_ag_hook_wiring.py) — dispatch-only chain SSOT
