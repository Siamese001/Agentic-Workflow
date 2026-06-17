# Agentic-Workflow — Claude Code Compatibility Contract

> Legacy compatibility contract for Claude Code in this repo. The active Codex execution contract
> lives in `AGENTS.md` and `docs/codex-primary-execution.md`; specialized guidance lives on demand in
> `.claude/rules/`, `.claude/skills/`, and subdirectory `CLAUDE.md` files for compatibility — see the
> index at the bottom.

## Plan First. Execute Second.

- **T2/T3** (2+ files, cross-layer, architecture, multi-file debug): enter **plan mode**
  (`EnterPlanMode`) and present the plan via `ExitPlanMode` for approval before any edit. The
  [`structured-reasoning`](.claude/skills/structured-reasoning/SKILL.md) skill still offers retrieval
  discipline for dense decomposition. See `.claude/rules/plan-first-enforcement.md`.
- **T0/T1**: single file ≤20 lines or questions — answer/edit directly.
- **Layer separation:** Reasoning / Routing / Execution / Verification — no edits before plan approval.

> Superseded W2 (`claude-native-supersession-9d3f7a`, ADR-094): the `SR_INTAKE`…`SR_VERIFY` /
> `SR_APPROVAL` marker scheme is retired — native plan mode is the "no edits before approval" contract.


## Agent fan-out restraint (always-on)

> ✅ **Multiple workflows / agents are welcome.** Parallel fan-out is a tool; effort tier
> (`max` / `ultracode` / `ultra`) raises **rigor, not a ceiling on agent count** — spin up as many
> as the work genuinely benefits from. ⛔ The **one** restraint: don't spend that fan-out
> **re-running discovery a plan (or prior results) already provides**.

- **Fan out freely for** independent parallelizable subtasks · scale beyond one context ·
  adversarial/independent verification · breadth sweeps where you only need the conclusion.
- **The one thing to avoid:** spawning agents to re-run discovery/inventory a **detailed plan or
  prior results already provide** — execute the plan and produce outputs; don't re-map a codebase
  you already understand. (Agent count itself is never the problem; redundant rediscovery is.)
- **`ultracode` is opt-in to quality, not a quota of agents** — use as many as the task benefits
  from; with a plan in hand, spend them on execution + verification, not rediscovery.
  Detail: [`agent-fanout-restraint.md`](.claude/rules/agent-fanout-restraint.md).
  Backstop: `.claude/hooks/pre_workflow_fanout_gate.py` (PreToolUse on `Workflow`) — confirms only
  on the pure-rediscovery shape, decoupled from count. Bypass: `FANOUT_RESTRAINT_BYPASS=1`.


## Constitutional floor (always-on)

Full text: [`.claude/rules/constitutional.md`](.claude/rules/constitutional.md). Hard constraints:

- **Subprocess timeout always required** — `subprocess.run(argv, shell=False, timeout=30)`. PowerShell is allowed (primary Windows shell); the legacy Windsurf PowerShell ban is lifted.
- **No test skipping** — no `pytest.mark.skip`, no `xfail` without `strict=True`.
- **No editing while exploring** — all repair gates pass before any edit; mode separation (`analyze`/`plan`/`edit`/`verify`).
- **Precise exceptions** — no bare `except:` / `except Exception` without a guardian comment.
- **ADG before structural grep** — ingest `artifacts/adg/*.sqlite` before T2/T3 query/edit; grep only for literals/TODOs.
- **No app leakage into `agentic_core`** without a migration receipt; no imports from `archives/` in production.
- **Author-Gate for ambiguous decisions** (see below). **CI enforces all of this**: `python ops_scripts/ci/run_contract_gates.py`.
- **Memory lifecycle** — recall project memory at session start and write back significant decisions to native file memory (`memory/`); knowledge-graph MCP optional. Codex-specific Agentic Workflow memory lives under `memory/codex/`, while `C:\Users\amita\.codex\memories` remains global/user memory. (W3/ADR-095)

## Proof contract — PASS / PARTIAL / FAIL / BLOCKED

Detail: `.claude/rules/002-pass-blocked-proof-contract.md`.

- **PASS** only when: scoped seam patched/verified · exact command output shown · tests/gates ran and passed ·
  artifact paths listed · nothing mocked unless the user asked. **PASS is expensive.**
- **PARTIAL** — real progress, but a proof requirement is missing (name it).
- **FAIL** — a command/test/gate ran and failed (include the failing command + smallest safe next patch).
- **BLOCKED** — cannot proceed (missing key/service/file, permission boundary, ambiguous destructive target).
- Forbidden: PASS because a plan/marker was emitted; "should pass" language; burying failed gates as "pre-existing".
- Receipts: list every repo path in `FILES_CHANGED`/`ARTIFACTS`/`REPORTS_GENERATED` as `[basename](forward/slash/path)`.
- Receipt block: emit it as its own separated block — after a `---` rule + a `### ⬛ Turn Receipt` heading, **unfenced** (a code fence would kill the clickable links). SSOT: `.claude/rules/001-runtime-seam-execution.md` § Response floor.

## Explanation style — business-first, technical kept (always-on)

Every explanation / summary / RCA / status *narrative* leads with the **outcome and what's at
stake in plain business English**, then the technical detail. Keep precise terms — but **each
jargon term, acronym, or internal code-name earns a short plain-language gloss on first use**, and
the **opening line carries no undefined acronym or code-name**. This is the general form of the
apps_rg "layman-lead" standard ([`apps-rg-executive-summary-response.md`](.claude/rules/apps-rg-executive-summary-response.md),
the stricter 3-sentence instance) — it now applies to **all** explanatory prose, not just apps_rg.

**Carve-out:** the post-turn **`STATUS` floor / `### ⬛ Turn Receipt`** and the proof-contract
structured fields stay in their exact contract shape — they are evidence, never business-simplified.
This is the "how the prose reads" layer on the floor, not a replacement (precedence:
`001-runtime-seam-execution.md` § Canonical post-turn output). No new template or hook — this is
doctrine, model-applied.

## Author-Gate (HITL before edits)

Stop and ask via the native **`AskUserQuestion`** tool before edits when the decision is
`architecture_choice`, `refactor_scope`, `anti_pattern`, `deletion_strategy`, `dependency_addition`,
`test_strategy`, or `error_handling` — i.e. two+ plausible approaches with different blast radius and
no unambiguous user directive. Present each option with a one-line trade-off and mark the recommended
one. Do **not** fire for typos, single-path fixes, or explicit instructions; when one path clearly
dominates, say so and proceed.

> Superseded W1 (`claude-native-supersession-9d3f7a`, ADR-093): the bespoke packet-builder /
> ui-renderer / `AUTHOR_GATE_PACKET:` / `DECISION_CAPTURED:` marker + SQLite-ledger + queue pipeline is
> retired — `AskUserQuestion` renders clickable options natively. Precedent, if useful, lives in file
> memory.


## MCP Quick Reference

> Tool ids in Claude Code are `mcp__<server>__<tool>` (stable, from the server key in
> [`.mcp.json`](.mcp.json)). Auth/setup notes: [`.claude/mcp-notes.md`](.claude/mcp-notes.md).

| Server | Use for | Example tools | Skill |
|---|---|---|---|
| `GitKraken` | Git, PRs, issues | `git_status`, `git_add_or_commit`, `pull_request_create` | [`gitkraken`](.claude/skills/gitkraken/SKILL.md) |
| `adg_sqlite` | Dependency graph, blast radius, layer analysis | `adg_health`, `adg_edge_fanin`, `adg_nodes_by_file`, `adg_violations` | [`adg-sqlite`](.claude/skills/adg-sqlite/SKILL.md) |
| `memory` | Cross-session knowledge graph | `mem_recall_session_start`, `create_entities`, `search_nodes` | [`memory-mcp`](.claude/skills/memory-mcp/SKILL.md) |
| `vector_db` | Semantic search / embeddings | `semantic_search`, `query_collection`, `vector_stats` | [`vector-db`](.claude/skills/vector-db/SKILL.md) |
| `notion` | Manual page/DB read+write (no plan-status enforcement) | `API-query-data-source`, `API-post-page`, `API-patch-page` | [`mcp-integration`](.claude/skills/mcp-integration/SKILL.md) |
| `deepwiki` | External GitHub repo docs Q&A | `read_wiki_contents`, `ask_question` | [`deepwiki`](.claude/skills/deepwiki/SKILL.md) |
| `context7` | Versioned external library docs | `resolve-library-id`, `get-library-docs` | [`context7`](.claude/skills/context7/SKILL.md) |
| `playwright` | Browser automation / E2E | `browser_navigate`, `browser_snapshot`, `browser_click` | [`playwright`](.claude/skills/playwright/SKILL.md) |

Procedural MCP SSOT: [`mcp-integration`](.claude/skills/mcp-integration/SKILL.md) §1–§13.

**Not in `.mcp.json` (use the native substitute; re-add from [`.claude/mcp-notes.md`](.claude/mcp-notes.md) if needed):**
`pytest_mcp` → `python -m pytest` via Bash · `redis` → `redis-cli` via Bash · `tavily` → native WebSearch/WebFetch ·
`otel_mcp` → on-demand (runtime trace debugging) · `filesystem`/`task_manager` → native file tools / `structured-reasoning`.
Their skills (`pytest-mcp`, `redis-cache`, `tavily-research`, `otel-telemetry`) remain as dormant reference until you re-add the server.

## Hooks

Governance hooks are registered in [`.claude/settings.json`](.claude/settings.json) and implemented in
`.claude/hooks/`. They reuse the existing governance engine under `.claude/governance/scripts/**` as a backend
(the one live dependency on the legacy tree). Block signal = exit code 2 + reason on stderr.

## Pytest

Pytest runs with plugin **autoload ON** (CI default). `addopts` carries `--timeout=180` (and `-n 24`
in `pyproject.toml`) but **no** `-p pytest_timeout` / `-p xdist` — so **do NOT** set
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` for ad-hoc runs: it strips those plugins and pytest aborts with
`error: unrecognized arguments: --timeout`. (Harnesses under `tools/` / `ops_scripts/` that set the
flag pass the matching `-p` flags on their own command line.) Prefer the `pytest_mcp` server over the bare CLI.

## Core vs apps

Apps customize inputs; core enforces contracts. No app-specific behavior in `agentic_core` without a
migration receipt. Detail: `.claude/rules/agentic-core-static.md`, `.claude/rules/apps-customization.md`,
[`agentic_core/AGENTS.md`](agentic_core/AGENTS.md).

## Plans & memory

- Plans SSOT is `plans/<slug>-<6hex>.md` at repo root (relocated out of `.claude/` to escape the Claude Code edit-guard; legacy `.claude/plans/` still valid — forward-only). See
  `.claude/rules/plan-location.md`. Plans are **disk-only** — no Notion registration (the
  windsurf/cursor-era Notion plan-status / registration / wave-lifecycle enforcement was removed;
  the disk-side plan-format lint stays). Multi-wave plan *format* is still validated by the disk
  gates (`check_plan_format_compliance`, `check_plan_wave_summary_top`, `check_plan_definition_of_done`).
- Memory: first tool call each session is `mem_recall_session_start`. Detail
  `.claude/rules/memory-management.md`, skill [`memory-mcp`](.claude/skills/memory-mcp/SKILL.md).

## apps_rg Operating Model — Standing Orders (2026-06-10)

> Adopted after the 145-plans/0-shipped review. Full rule: [`apps-rg-execution-bias`](.claude/rules/apps-rg-execution-bias.md).

- **North star (only success metric):** AIG resume, 11/11 lanes X3_ALLOW, assembled DOCX in hand.
- **Execute, don't plan** — NEW plan files are blocked by `pre_write_plan_mint_gate.py`; explicit
  user authorization in-turn (`PLAN_MINT_OK=1`) is the only mint path.
- **Findings → rows** in the single backlog (`plans/apps-rg-lane-aggregation-gap-closure-b8c3d1.md`
  Master Gap Inventory), never new plan documents.
- **WIP = 1 active plan, one owner session** — one owner per active apps_rg write-work stream.
- Discovery ≤20%, post-increment; subtraction before addition; weekly heartbeat E2E matrix is the
  only status artifact.

---

## Specialized rules — load on demand

Most `.claude/rules/*.md` are now **thin pointer stubs** (plan `always-on-rule-surface-cut-c7f3a1`):
each names its invariant + the skill/hook that enforces it. Open the rule for the pointer, or jump
straight to the skill. Topic → primary skill:

| Area | Rules (stubs unless noted) | Primary skill(s) |
|---|---|---|
| Scope / process | `scope-containment`*, `agent-fanout-restraint`*, `approval-exception-policy`, `query-progress-bar`, `python-dash-c-quote-hazard`, `security-hardening` (*=still full) | [`scope-containment`](.claude/skills/scope-containment/SKILL.md), [`security-hardening`](.claude/skills/security-hardening/SKILL.md), [`progress-display-enforcement`](.claude/skills/progress-display-enforcement/SKILL.md) |
| Core / apps boundary | `agentic-core-static`, `agentic-core-glob-lock`, `boundary-audit-required`, `apps-customization`, `apps-folder-taxonomy`, `apps-test-surface-taxonomy`, `agent-taxonomy-spine-truth`, `ssot-folder-enforcement`, `artifact-provenance-discipline` | [`boundary-enforcement`](.claude/skills/boundary-enforcement/SKILL.md), [`core-boundary-audit`](.claude/skills/core-boundary-audit/SKILL.md), [`u0-app-customization`](.claude/skills/u0-app-customization/SKILL.md) |
| ADG / graph | `adg-analysis-procedures`, `adg-canonical-invariants`*, `adg-p-band-burn-down-discipline`, `adg-post-run-burndown`, `closed-loop-router-enforcement` | [`graph-analysis`](.claude/skills/graph-analysis/SKILL.md), [`adg-sqlite`](.claude/skills/adg-sqlite/SKILL.md) |
| Eval / judges / ledgers | `evaluation-promotion-gate`, `judge-calibration-cadence`, `intelligence-ledger-family` | [`operational-gates`](.claude/skills/operational-gates/SKILL.md), [`ledger-consulter`](.claude/skills/ledger-consulter/SKILL.md) |
| MCP / infra / runtime | `mcp-config-ssot`, `mcp-pytest-enforcement`, `local-llm-wsl2-gpu`, `claude-config-lookup` | [`mcp-integration`](.claude/skills/mcp-integration/SKILL.md), [`pytest-mcp`](.claude/skills/pytest-mcp/SKILL.md) |
| Plans / memory | `plan-location`, `memory-management` | [`memory-mcp`](.claude/skills/memory-mcp/SKILL.md), [`writeback-discipline`](.claude/skills/writeback-discipline/SKILL.md) |
| Chat isolation | `git-branch-per-chat` | [`worktree-per-chat`](.claude/skills/worktree-per-chat/SKILL.md) |
| apps_rg (also `apps_rg/CLAUDE.md`) | `apps-rg-execution-bias`, `apps-rg-executive-summary-response`, `apps-rg-interactive-discipline`, `apps-rg-post-run-summary` | [`apps-rg-runtime`](.claude/skills/apps-rg-runtime/SKILL.md) |

> Author-Gate is retired → native `AskUserQuestion` ([`ask-user-question-recommendation`](.claude/skills/ask-user-question-recommendation/SKILL.md)); deferred scope → `spawn_task` (§24). Notion plan enforcement removed (plans disk-only). Full retired-rule map: [retired-rules-index.md](docs/reports/governance/retired-rules-index.md).
