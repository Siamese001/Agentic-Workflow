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
- **apps_rg C0.3 graph skills** use `master_skills_arsenal_ledger.json` as canonical source and generated
  SQLite only as runtime/query projection; detail: `memory/codex/apps_rg_graph_skills_sqlite_runtime_invariant.md`.
- **apps_rg SQLite graph index** preserves edge rationale and materializes generated path/neighborhood/sibling
  runtime views/tables for C0.3; detail: `memory/codex/apps_rg_graph_sqlite_path_index_runtime.md`.
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
  §30/§35 are RETIRED slots. **S1 author-gate retirement was COMPLETED on `origin/main`** (merged into
  this branch 2026-06-14): Tier-2 author-facing layer retired, `ci/author_gate/`→`ci/decision_ledger/`,
  the 2 AG skills + ~15 AG scripts + the AG test suite removed (shared ledger backbone preserved).
  Remaining consolidation = **W3** (19 redirect rule stubs), **W4** (103 orphan gates per refreshed
  `classify_gate_wiring.py`), **W5** (dormant-MCP skills + thin-alias commands).
  **CI lessons (PR #336):** root `archives/` is FORBIDDEN (`check_structure_policy`) — retire via `git rm`,
  not move-to-archives; verify a name is not a *live import* before any mv; `memory/` is whitelisted in
  `config/structure_blueprint/structure_policy.yaml`; rule files are validated by
  `check_rule_frontmatter_schema`/`check_rules_index_freshness`/`check_rule_cross_references` (W3 must
  repoint inbound refs + keep AGENTS.md's index fresh in lockstep).
- "Uncalled by `run_contract_gates.py`" ≠ dead: pre-commit references 45 gates, workflows 33. Gate
  retirement (W4) is gated by `tools/governance/classify_gate_wiring.py`.

## Procedural patterns (this environment)

- **ADR liveness hygiene (2026-06-22):** ADRs are provenance/rationale, not executable policy.
  Use `python ops_scripts/ci/inventory_adr_liveness.py --json` for live-binding classification and
  `python ops_scripts/ci/check_adr_hygiene.py --advisory` for namespace drift; details:
  `memory/codex/adr_liveness_hygiene.md`.
- **apps_research targeting briefs fail closed (2026-06-21):** fresh `python -m apps_research
  --target-company <company> --target-role <role> --jd <jd-path>` must print an `artifact=<...briefing.md>`
  before apps_rg may consume it. Missing grounded `company_brief_text` is a failure; do not substitute stale
  populated artifacts or dry-run output. Detail: `memory/codex/apps_research_targeting_brief_fail_closed.md`.
- **apps_rg competencies graph traversal receipts (2026-06-22):** bundle-mode competencies must prove
  graph traversal breadth/depth, rejected siblings, per-category granularity, JD-critical partnership axes,
  and decomposed confidence before certification. Detail:
  `memory/codex/apps_rg_competencies_graph_traversal_receipt.md`.
- **Codex repo-local memory placement (2026-06-16):** Agentic Workflow-specific Codex memory artifacts
  belong under `memory/codex/`, not only under the global user-profile path
  `C:\Users\amita\.codex\memories`. The repo-local mirror contains `MEMORY.md`, `memory_summary.md`,
  `raw_memories.md`, rollout summaries, and repo-specific Codex skills. Keep global/user preferences
  outside the repo; keep project-governance and project-run memory in this repo-owned `memory/` tree.
- New `plans/*.md` files are **mint-gated** (`pre_write_plan_mint_gate.py`) — create only with explicit
  user authorization in-turn. Editing existing plan files is unrestricted.
- Bash commands containing legacy execution tokens (`Windsurf`/`Cursor`) are **blocked** by
  `before_shell_execution.py`. Route large doc writes through the Write tool, then `mv`/`git mv` into place.
- **MCP sovereignty**: only servers whose key is in `.mcp.json` `mcpServers` pass `pre_mcp_gate`.
  Harness-injected servers (`github`, capital-`Notion`) are refused unless whitelisted; the project's
  sanctioned PR/Notion tools are `GitKraken`/lowercase-`notion` (may be disconnected in remote envs).
- v2 plans: `## Status Tables` (Wave Progress canonical columns + Phase Progress) before the first
  `## Wave N`; waves ascending; `## Definition of Done` ≥5 rows + smoke run.
- **PR merge method (operator directive 2026-06-15):** merge PRs with **`merge` or `rebase`, NEVER
  `squash`**. Squash collapses the branch into a new commit, so the branch is not an ancestor of `main`
  (`rev-list trunk..branch ≠ 0`) and the worktree auto-reaper (`prune_merged_chat_worktrees.py`) reads it
  as *unmerged* and SKIPS cleanup. `merge`/`rebase` keep the branch a true ancestor → its worktree +
  local branch are auto-deleted cleanly, which is the desired lifecycle (deleting the merged worktree +
  local branch IS the correct behavior).
- **apps_rg graph SQLite path-index runtime (2026-06-26):** C0.3 graph traversal keeps JSON canonical and
  uses generated SQLite objects for reverse paths, siblings, budgets, metric usage, and rejection receipts.
  Validate with `python apps_rg/fact_inventory/validate_graph_sqlite_path_index.py` plus
  `python -m pytest tests/unit/apps_rg/fact_inventory/test_graph_sqlite_path_index.py -q`. Detail:
  `memory/codex/apps_rg_graph_sqlite_path_index_runtime.md`.

- 2026-06-20: Branch publication closeout now means **exact ancestry on `origin/main`**, not
  patch-equivalence. `git cherry -v` is diagnostic only: `-` rows can justify an explicit
  `git merge -s ours --no-ff <branch>` to record a superseded/transplanted branch, but local
  branch/worktree cleanup must wait for `git merge-base --is-ancestor <branch> origin/main`.

## Project context

- Notion Plans DB `data_source_id`: `ac53d31b-3068-4039-9ebe-856c12caab32`. Registration helper:
  `tools/notion/plan_creation_helper.py` (needs `NOTION_TOKEN`).
- Local LLM: Docker container `local-qwen-vllm`, Qwen2.5-32B-AWQ, endpoint `http://localhost:8000/v1`
  (`docker-compose.qwen.yml`).
- Contract-gate entry point: `python ops_scripts/ci/run_contract_gates.py [--gate <ID>]`.
