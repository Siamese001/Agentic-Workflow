# Project Memory — Agentic-Workflow (native file-memory SSOT)

> Constitutional §17 + ADR-095 (W3 `claude-native-supersession`): this file plus per-fact files under
> `memory/` are the canonical cross-session memory. **Recall at session start; write back significant
> decisions (15/3 rule).** The knowledge-graph MCP is optional, for genuine graph queries only.
>
> Structure: this index holds durable, high-signal facts. Large/episodic detail → `memory/<topic>.md`.
> Created 2026-06-14 by plan `enforcement-surface-consolidation-d8b3f6` (W1.1) to resolve the drift
> where §17 + `memory-management.md` + `memory-notion-writeback.md` cited this path before it existed.

## Architectural invariants

- The canonical product E2E spine is **function/stage based** (`run_integrated_single_action_spine`),
  NOT a `*Agent` class execution graph (ADR-088).
- `agentic_core` is **app-agnostic**; app behavior lives in `apps_*` via the U0
  `runtime_customization_package`. No app literals/branches in core without a migration receipt.
- **ADG SQLite** (`artifacts/adg/adg_indexed_*.sqlite`) is the structural-truth SSOT; Redis is a hot
  projection; MCP is the read-only gateway. ADG wins conflicts vs text-search/intuition.
- **Native features supersede ported emulation** (`claude-native-supersession-9d3f7a`): `AskUserQuestion`
  ← Author-Gate packet/marker/ledger; plan mode ← `SR_*` markers; `spawn_task` ← deferred/next-step
  capture; native file memory ← memory-MCP ritual; native parallel MCP ← serialization rule.

## Active governance state (2026-06-14)

- Enforcement surfaces: **67 rules, 34 skills, 14 hooks, 111 governance scripts, 408 CI gates
  (326 `check_*`)**.
- Active consolidation plan: **`plans/enforcement-surface-consolidation-d8b3f6.md`** — unified audit +
  7 waves; **supersedes `claude-native-supersession-9d3f7a`**; absorbs S1–S6 + the W0 coupling map and
  adds the CI-gate sweep, rule-stub collapse, skills archival, and this memory-drift fix.
- **Author-Gate emulation (S1) is RETIRED at the doctrine/wiring level** —
  `after_agent_governance_dispatch.py` removed the AG chain; 5 AG rules DEPRECATED; constitutional
  §30/§35 are RETIRED slots. W2 (2026-06-14) archived the 2 AG skills + 3 proven-orphan gates to
  `archives/enforcement_consolidation_2026-06-14/`. **KEPT:** `author_gate_ledger_integrity.py` — the
  active `refactor-decision-memory` skill imports it (`lookup_refactor_decisions.py`), so decouple
  that skill → native file memory BEFORE archiving the remaining ~15 AG scripts / ledger gates /
  `author-gate-gates.yml` workflow. Lesson: AG machinery has live consumers; verify imports before mv.
- "Uncalled by `run_contract_gates.py`" ≠ dead: pre-commit references 45 gates, workflows 33. Gate
  retirement (W4) is gated by `tools/governance/classify_gate_wiring.py`.

## Procedural patterns (this environment)

- New `plans/*.md` files are **mint-gated** (`pre_write_plan_mint_gate.py`) — create only with explicit
  user authorization in-turn. Editing existing plan files is unrestricted.
- Bash commands containing legacy execution tokens (`Windsurf`/`Cursor`) are **blocked** by
  `before_shell_execution.py`. Route large doc writes through the Write tool, then `mv`/`git mv` into place.
- **MCP sovereignty**: only servers whose key is in `.mcp.json` `mcpServers` pass `pre_mcp_gate`.
  Harness-injected servers (`github`, capital-`Notion`) are refused unless whitelisted; the project's
  sanctioned PR/Notion tools are `GitKraken`/lowercase-`notion` (may be disconnected in remote envs).
- v2 plans: `## Status Tables` (Wave Progress canonical columns + Phase Progress) before the first
  `## Wave N`; waves ascending; `## Definition of Done` ≥5 rows + smoke run.

## Project context

- Notion Plans DB `data_source_id`: `ac53d31b-3068-4039-9ebe-856c12caab32`. Registration helper:
  `tools/notion/plan_creation_helper.py` (needs `NOTION_TOKEN`).
- Local LLM: Docker container `local-qwen-vllm`, Qwen2.5-32B-AWQ, endpoint `http://localhost:8000/v1`
  (`docker-compose.qwen.yml`).
- Contract-gate entry point: `python ops_scripts/ci/run_contract_gates.py [--gate <ID>]`.
