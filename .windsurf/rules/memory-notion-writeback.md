---
trigger: always_on
---

# Memory ↔ Notion Writeback Discipline

> ⛔ When non-trivial work completes, the knowledge MUST be written back to the correct store. Memory for Cascade's next-session recall, Notion for human audit, both for cross-cutting decisions.

## The 15/3 Rule

If solving a problem took more than **15 minutes** of real work, spend up to **3 minutes** writing it back. Non-negotiable for work classified T2/T3 per constitutional Tier Classification.

## Decision Table — Where Does It Go?

| Signal in current session | Memory MCP (`memory`) | Notion MCP (`notion`) | Neither |
|---|:---:|:---:|:---:|
| Non-obvious bug fix / RCA with recurring pattern | ✅ `ProceduralPattern:*` | ⚠️ only if user-audit needed | — |
| Architectural decision / ADR | ⚠️ short invariant entity | ✅ ADR Registry row | — |
| Wave/phase status change on a plan | ✅ `Project:*` observation | ✅ Wave/Phase Convergence row | — |
| HITL / Author-Gate decision resolved | — | ✅ HITL Decision Ledger row | — |
| MCP config or gate behavior change | — | ✅ MCP Registry patch | — |
| New SC/AP violations emitted by ADG | — | ✅ SC/AP Violation Backlog row(s) | — |
| New anti-pattern suppression baseline | — | ✅ Anti-Pattern Burndown row | — |
| Regenerated full ADG / new snapshot | — | — | ✅ (auto-logged in artifact) |
| Full topology / rationale / diagrams | — | — | ✅ lives on disk (`docs/architecture/*.md`) |
| Fix that recurs across ≥2 sessions | ✅ `ProceduralPattern:*` | — | — |
| Project blocker the user must resolve | ✅ `Project:*` observation | ✅ Wave/Phase row with status=blocked | — |

**Rule of thumb**: If Cascade will need it in the **first 5 minutes of the next session**, write to **Memory**. If a **human** will audit it across days/weeks, write to **Notion**. If both, write a compact Memory entity with a Notion URL in its observations.

## Memory MCP — Entity Types (canonical)

Write to `memory` MCP via `create_entities` / `add_observations`. Durable entity types (survive `mem_cleanup_stale`):

| Type | Use |
|---|---|
| `ProceduralPattern` | Fix recipes, tool-usage patterns, debugging playbooks |
| `ProjectContext` | Project status, next-action, active blockers |
| `ArchitecturalInvariant` | Rules about code topology that must not be violated |
| `EpisodicEvent` | Important one-time occurrences (rare — prefer ProceduralPattern) |

General-typed entities (without these protected types) are purged at 30 days — do **not** use `"entityType": "general"` for anything you want to persist.

SSOT path: `@c:/Git/Agentic-Workflow/artifacts/memory/knowledge_graph.sqlite`

## Notion MCP — Database Routing (canonical)

Full workspace map lives in `@c:/Git/Agentic-Workflow/AGENTS.md` (Notion Workspace Map block, auto-synced). Writes use `API-post-page` with `parent: {type: "database_id", database_id: <write-id>}` — **not** data_source_id (that 404s).

The 8 canonical databases and their triggers are listed in AGENTS.md. Never invent a new database without first proposing it; never duplicate narrative from disk into Notion — Notion holds the searchable row, disk holds the full artifact.

## Writeback Triggers (fire these automatically)

Cascade MUST write back without waiting for a prompt when any of these happen in the current response:

1. **New `docs/architecture/adr/ADR-*.md`** → Notion ADR Registry row (`API-post-page`)
2. **Modified `.windsurf/mcp_config.json`** → Notion MCP Registry patch/post
3. **Gate behavior changed in `.windsurf/scripts/*_gate.py`** → Notion MCP Registry Notes field update
4. **Resolved scored `ask_user_question`** → Notion HITL Decision Ledger row
5. **`generate_full_adg.py` produced NEW SC/AP defects** → Notion SC/AP Violation Backlog row per new violation
6. **Created/modified `.windsurf/plans/*-<6hex>.md`** → Memory `Project:<plan-slug>` observation with current status + blocker
7. **Diagnosed a recurring bug or anti-pattern** → Memory `ProceduralPattern:*` entity with diagnosis + fix recipe

## Stale-Source Sniff Test (MANDATORY before writing Project:* or Wave rows)

Plan files go stale when work completes but the header is not updated. Before writing a `Project:*` Memory entity or a Wave/Phase Notion row using a plan file's stated Status, run this 3-step check:

1. **Grep the plan for `Status:`** — read the claimed status
2. **Run `git log --grep="<plan-slug>"`** — look for a commit containing `complete`, `done`, or the final-wave label
3. **Verify referenced paths** — files the plan says to **retire** should NOT exist; files it says to **create** SHOULD exist

If (2) or (3) contradicts (1), the plan is stale. Write the ACTUAL status (with a `CORRECTION: plan header was stale` observation) and update the plan header in the same response.

Failure precedent: 2026-04-22 routing-unification-qwen false-blocked writeback. Captured as `ProceduralPattern:WritebackStaleSourceSniffTest`.

## Forbidden Patterns

- ❌ Write Notion narrative that duplicates disk content — row should link to the file, not repeat it.
- ❌ Use `entityType: "general"` for anything intended to persist (gets purged at 30 days).
- ❌ Create entities with observations containing only generic strings (e.g., "fixed the bug"). Observations must be recall-actionable in the next session.
- ❌ Write to Notion without also updating Memory if Cascade will need to recall it next session.
- ❌ Skip the writeback because "it's small" — if the 15/3 rule triggered, the writeback is required.

## Escape Hatch

Set `WRITEBACK_AUDIT_BYPASS=1` only for: scripted batch runs, tests, or acknowledged one-off exploratory sessions. Each bypass is logged in `@c:/Git/Agentic-Workflow/artifacts/windsurf/writeback_violations.jsonl` with reason=bypass.

## Enforcement

This rule is the **advisory tier**. The deterministic tier is the post-response hook:
- `@c:/Git/Agentic-Workflow/.windsurf/scripts/post_cascade_writeback_audit.py` (runs on every response)
- Violations log: `@c:/Git/Agentic-Workflow/artifacts/windsurf/writeback_violations.jsonl`

See the `writeback-discipline` skill for entity/row templates to copy.
