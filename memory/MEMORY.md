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
- **Generate-full-ADG gate rationalization (2026-06-28):** ADG reporting must fail fast on mixed-run
  artifacts, `G_REACH` is core-layer L0 reachability only (`L_APP` excluded), and deleted
  `hierarchy_healer.py` behavior is routed through `StructureEnforcerAgent`. Detail:
  `memory/codex/generate_full_adg_gate_rationalization.md`.
- **ADG Redis hotcache query alignment (2026-06-29):** Redis query helpers must read the versioned
  `adg:v1:<snapshot_id>:` keys written by `adg_redis_ingest`; staleness checks compare commits to
  `adg:meta.sqlite_mtime` using Git `--after=@<epoch>` to avoid UTC/local drift, and the canonical generator is
  `tools/generate/generate_full_adg.py`. Detail: `memory/codex/adg_redis_hotcache_query_alignment.md`.
- **ADG scheduled retention contract (2026-07-01):** scheduled automation enters through
  `tools/adg/run_full_adg_audit.py`, so retention must be invoked there as a fail-soft sweep and must group
  UTC helper artifacts by their canonical `adg_indexed_<ts>.sqlite` metadata. Detail:
  `memory/codex/adg_scheduled_retention_contract.md`.
- **ADG C3 module-target side-effect ratchet (2026-07-05):** C3 silent-write counts must treat
  `emits_side_effect` edges that target the writer module as satisfying the same-surface side-effect
  requirement; otherwise module-level `writes_to` rows are overcounted. Detail:
  `memory/codex/adg_c3_module_target_side_effect_ratchet.md`.
- **ADG S2 write-sovereignty MV ratchet (2026-07-05):** S2 UWG-bypass counts must prefer
  `mv_write_sovereignty_paths WHERE is_uwg_routed = 0` over raw `writes_to` edges when the MV exists,
  because the MV carries durable-write scope, tooling/script exclusions, and routed-UWG symbol
  classification. Detail: `memory/codex/adg_s2_write_sovereignty_mv_ratchet.md`.
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
- **On-demand PR publisher dirty-worktree intake (2026-06-30):** `codex_publication_audit.py
  --require-pr-flow` must return WARN plus `recovery_required=["current_worktree_dirty"]` for
  dirty-but-recoverable intake, not FAIL; strict closeout with `--require-single-main-worktree`
  still fails until cleanup clears dirty state. Detail:
  `memory/codex/pr_publisher_dirty_worktree_recovery_contract.md`.
- **apps_research targeting briefs fail closed (2026-06-21):** fresh `python -m apps_research
  --target-company <company> --target-role <role> --jd <jd-path>` must print an `artifact=<...briefing.md>`
  before apps_rg may consume it. Missing grounded `company_brief_text` is a failure; do not substitute stale
  populated artifacts or dry-run output. Detail: `memory/codex/apps_research_targeting_brief_fail_closed.md`.
- **apps_research → apps_rg handoff envelope invariant (2026-07-04):** apps_research X3 authorization now
  requires an external_openai generation lane, a model-backed Gemini X2 receipt, and an envelope beside the
  delegated briefing; bridge confidence or deterministic semantics alone are not authorization. Detail:
  `memory/codex/apps_research_apps_rg_handoff_envelope_invariant.md`.
- **apps_rg competencies graph traversal receipts (2026-06-22):** bundle-mode competencies must prove
  graph traversal breadth/depth, rejected siblings, per-category granularity, JD-critical partnership axes,
  and decomposed confidence before certification. Detail:
  `memory/codex/apps_rg_competencies_graph_traversal_receipt.md`.
- **apps_rg competencies X1D self-judge guard (2026-06-30):** competencies primary generation is
  Claude-backed, so formal proof judging is OpenAI-required and `anthropic_claude` must be removed from
  competencies X1D CLI/env overrides. Detail:
  `memory/codex/apps_rg_competencies_x1d_self_judge_guard.md`.
- **L2 E4 repair authority modes (updated 2026-07-05):** package-driven L2 repair may mutate the retry
  CPA/prompt packet, but `apps_rg` v4 envelope E4 must keep prompt text and compilation hash stable,
  carry H0 repair context in the receipt, and link retries via `l2_e4_repair:<id>` audit refs.
  Detail: `memory/codex/l2_e4_real_healing_prompt_packet_repair.md`.
- **Codex repo-local memory placement (2026-06-16):** Agentic Workflow-specific Codex memory artifacts
  belong under `memory/codex/`, not only under the global user-profile path
  `C:\Users\amita\.codex\memories`. The repo-local mirror contains `MEMORY.md`, `memory_summary.md`,
  `raw_memories.md`, rollout summaries, and repo-specific Codex skills. Keep global/user preferences
  outside the repo; keep project-governance and project-run memory in this repo-owned `memory/` tree.
- **Codex native/global memory boundary (2026-06-28):** Codex product memories and
  `C:\Users\amita\.codex\memories` are ambient user/cross-workflow recall only. Agentic Workflow
  project facts, governance decisions, and run history resolve to repo-local `memory/`; if Codex native
  memories are ever enabled, use `memories.disable_on_external_context = true` and do not let generated
  memories override checked-in project guidance.
- **ADG transport-open per-turn gate (2026-07-01):** ordinary T2/T3 prompts require both ADG SQLite
  SSOT health and active-session ADG MCP transport proof; heartbeat/process evidence or direct SQLite
  fallback cannot substitute for a closed Codex MCP route. Detail:
  `memory/codex/adg_transport_open_per_turn_gate.md`.
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
- **apps_rg C0.3 graphDB overwrite validation repairs (2026-06-26):** apply graphDB/graph-skill overwrite
  packages through materializers, open SQLite writable for schema hardening, and validate the broader
  master-ledger shape after granularity hardening. Detail:
  `memory/codex/apps_rg_c03_graphdb_overwrite_validation_repairs.md`.
- **L6 / apps_eval microstep alignment (2026-06-27):** L6 shadow observability uses the same
  `microstep_id` join key as `apps_eval` for apps_rg, but remains post-run, read-only, and
  future-run-only. Detail: `memory/codex/l6_apps_eval_microstep_alignment_invariant.md`.
- **apps_rg L7 provider attempt spans (2026-06-28):** provider RCA timing now has a normalized
  `provider_attempt_spans` surface on provider responses, fallback receipts, and section L7 binding
  manifests. Detail: `memory/codex/apps_rg_l7_provider_attempt_spans.md`.
- **apps_rg single-spine section scope invariant (2026-07-01):** apps_rg section execution must attach
  app-owned U0 runtime package fields and enter `agentic_core`'s integrated single-action spine; the
  app-owned section lane is selected only as a scoped L2 recipe body, while L7 remains core-owned.
  Detail: `memory/codex/apps_rg_single_spine_section_scope_invariant.md`.
- **apps_rg OTel trace reconciliation consumer (2026-06-28):** OTel is consumed post-run through
  `trace_reconciliation.json`; apps_eval grades it as optional observability evidence and L6 turns gaps
  into future-run-only recommendations. Detail:
  `memory/codex/apps_rg_otel_trace_reconciliation_consumer.md`.
- **apps_rg L6 shadow observability closure invariant (2026-07-05):** L6 evidence classes now
  distinguish contract-only advisory, apps_eval-bound proof, and failure-terminal advisory; trace
  reconciliation/summary precede microstep observations, closure receipts follow v40 packages, and
  post-X3 section bindings are additive only. Detail:
  `memory/codex/apps_rg_l6_shadow_observability_closure_invariant.md`.
- **apps_rg mandatory BCG/run-ledger outputs (2026-06-28):** every apps_rg run must emit
  `BCG_EXECUTIVE_OUTPUT.md`, `APPS_RG_MANDATORY_RUN_OUTPUT.md`, and
  `APPS_RG_MANDATORY_RUN_OUTPUT.json`; failed runs still need RCA, section/judge ledger, and
  3-5 bullet root-cause implementation plans plus causal allocation with concrete
  root-cause-linked rows, not symptom-only remediation or generic buckets. Causal-control
  fixtures live in `tests/unit/apps_rg/test_causal_rca_regression_fixtures.py`. Detail:
  `memory/codex/apps_rg_mandatory_bcg_run_outputs.md`.
- **apps_rg Anthropic section blockers (2026-07-05):** InsurTech bullet empty-selection after real
  Anthropic SC paths with truncated JSON is a role-episode output-token-budget bug, while headline
  partner/alliance/channel repetition must fail deterministic segment quality before X1D. Detail:
  `memory/codex/apps_rg_anthropic_section_blockers.md`.

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
