# Agentic-Workflow — Claude Code Operating Contract

> This is the always-on SSOT for Claude Code in this repo. It supersedes `AGENTS.md` (the prior
> Cursor-era contract, kept as legacy). Specialized guidance lives on demand in `.claude/rules/`,
> `.claude/skills/`, and subdirectory `CLAUDE.md` files — see the index at the bottom.

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

> ⛔ Sub-agents (Workflow fan-out, `Agent`, `Task`) cost **millions of tokens** — spin them up only
> when the work genuinely needs it, never because the effort tier is high. `max` / `ultracode` /
> `ultra` raise **rigor, not agent count**.

- **Default to inline.** Fan out only for: independent parallelizable subtasks · scale beyond one
  context · adversarial/independent verification · breadth sweeps where you only need the conclusion.
- **Do NOT** spawn agents to re-run discovery/inventory a **detailed plan or prior results already
  provide** — execute the plan and produce outputs; don't re-map a codebase you already understand.
- **`ultracode` is opt-in to quality, not to agent count** — scale to the task, not the budget; prefer
  the fewest agents that cover the work. Detail: [`agent-fanout-restraint.md`](.claude/rules/agent-fanout-restraint.md).
  Backstop: `.claude/hooks/pre_workflow_fanout_gate.py` (PreToolUse on `Workflow`). Bypass: `FANOUT_RESTRAINT_BYPASS=1`.


## Constitutional floor (always-on)

Full text: [`.claude/rules/constitutional.md`](.claude/rules/constitutional.md). Hard constraints:

- **Subprocess timeout always required** — `subprocess.run(argv, shell=False, timeout=30)`. PowerShell is allowed (primary Windows shell); the legacy Windsurf PowerShell ban is lifted.
- **No test skipping** — no `pytest.mark.skip`, no `xfail` without `strict=True`.
- **No editing while exploring** — all repair gates pass before any edit; mode separation (`analyze`/`plan`/`edit`/`verify`).
- **Precise exceptions** — no bare `except:` / `except Exception` without a guardian comment.
- **ADG before structural grep** — ingest `artifacts/adg/*.sqlite` before T2/T3 query/edit; grep only for literals/TODOs.
- **No app leakage into `agentic_core`** without a migration receipt; no imports from `archives/` in production.
- **Author-Gate for ambiguous decisions** (see below). **CI enforces all of this**: `python ops_scripts/ci/run_contract_gates.py`.
- **Memory lifecycle** — recall project memory at session start and write back significant decisions to native file memory (`memory/`); knowledge-graph MCP optional. (W3/ADR-095)

## Proof contract — PASS / PARTIAL / FAIL / BLOCKED

Detail: `.claude/rules/002-pass-blocked-proof-contract.md`.

- **PASS** only when: scoped seam patched/verified · exact command output shown · tests/gates ran and passed ·
  artifact paths listed · nothing mocked unless the user asked. **PASS is expensive.**
- **PARTIAL** — real progress, but a proof requirement is missing (name it).
- **FAIL** — a command/test/gate ran and failed (include the failing command + smallest safe next patch).
- **BLOCKED** — cannot proceed (missing key/service/file, permission boundary, ambiguous destructive target).
- Forbidden: PASS because a plan/marker was emitted; "should pass" language; burying failed gates as "pre-existing".
- Receipts: list every repo path in `FILES_CHANGED`/`ARTIFACTS`/`REPORTS_GENERATED` as `[basename](forward/slash/path)`.

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
| `notion` | Plans + Backlog DBs only | `API-query-data-source`, `API-post-page`, `API-patch-page` | [`notion`](.claude/skills/notion/SKILL.md) |
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
  `.claude/rules/plan-location.md`, skill [`plan-governance`](.claude/skills/plan-governance/SKILL.md).
- Memory: first tool call each session is `mem_recall_session_start`. Detail
  `.claude/rules/memory-management.md`, skill [`memory-mcp`](.claude/skills/memory-mcp/SKILL.md).

## apps_rg Operating Model — Standing Orders (2026-06-10)

> Adopted after the 145-plans/0-shipped review. Full rule: [`apps-rg-execution-bias`](.claude/rules/apps-rg-execution-bias.md).

- **North star (only success metric):** AIG resume, 11/11 lanes X3_ALLOW, assembled DOCX in hand.
- **Execute, don't plan** — NEW plan files are blocked by `pre_write_plan_mint_gate.py`; explicit
  user authorization in-turn (`PLAN_MINT_OK=1`) is the only mint path.
- **Findings → rows** in the single backlog (`plans/apps-rg-lane-aggregation-gap-closure-b8c3d1.md`
  Master Gap Inventory), never new plan documents.
- **WIP = 1 active plan, one owner session** — check Notion `In Progress` before apps_rg write-work.
- Discovery ≤20%, post-increment; subtraction before addition; weekly heartbeat E2E matrix is the
  only status artifact.

---

## Specialized rules — load when relevant

On-demand reference docs (the Cursor "agent-requested" layer). Read the file when a task matches.
A **Skill** column entry means a richer procedural skill covers the same area — prefer it.

### Governance / process
| Rule | Topic | Skill |
|---|---|---|
| `scope-containment.md` | No gold-plating; one task at a time | [`scope-containment`](.claude/skills/scope-containment/SKILL.md) |
| `agent-fanout-restraint.md` | Spawn agents only when needed; effort tier ≠ agent count | — |
| `approval-exception-policy.md` | When approval/exceptions apply | — |
| `deferred-scope-capture.md` | Capturing out-of-scope work | — |
| `next-step-capture.md` | Recording the next step | — |
| `author-gate-decision-points.md` / `author-gate-enforcement.md` / `author-gate-queue-drain.md` / `author-gate-svp-calibration.md` | Author-Gate (retired → native `AskUserQuestion`); rules are deprecation stubs | [`ask-user-question-recommendation`](.claude/skills/ask-user-question-recommendation/SKILL.md) |
| `security-hardening.md` | Security hardening | — |
| `python-dash-c-quote-hazard.md` | `python -c "..."` quote-hazard ban | — |
| `query-progress-bar.md` | Progress bar for long operations | — |

### Architecture / boundaries
| Rule | Topic | Skill |
|---|---|---|
| `agentic-core-static.md` / `agentic-core-glob-lock.md` | Core static law + editing guard | [`boundary-enforcement`](.claude/skills/boundary-enforcement/SKILL.md) |
| `boundary-audit-required.md` | When a boundary audit is required | [`core-boundary-audit`](.claude/skills/core-boundary-audit/SKILL.md) |
| `apps-customization.md` / `apps-folder-taxonomy.md` / `apps-test-surface-taxonomy.md` | Apps overlay rules & taxonomy | [`u0-app-customization`](.claude/skills/u0-app-customization/SKILL.md) |
| `agent-taxonomy-spine-truth.md` | Agent taxonomy / product spine | — |
| `ssot-folder-enforcement.md` | New files land in canonical folders | [`artifact-management`](.claude/skills/artifact-management/SKILL.md) |
| `artifact-provenance-discipline.md` | Never present a wrong-run artifact | [`artifact-management`](.claude/skills/artifact-management/SKILL.md) |
| `closed-loop-router-enforcement.md` | Closed-loop router invariants | — |

### ADG / graph
| Rule | Topic | Skill |
|---|---|---|
| `adg-analysis-procedures.md` / `adg-canonical-invariants.md` | ADG analysis + invariants | [`graph-analysis`](.claude/skills/graph-analysis/SKILL.md), [`adg-sqlite`](.claude/skills/adg-sqlite/SKILL.md) |
| `adg-p-band-burn-down-discipline.md` / `adg-post-run-burndown.md` | P-Band burndown + post-run dispatch | — |

### Eval / judges
| Rule | Topic | Skill |
|---|---|---|
| `evaluation-promotion-gate.md` | Regression-pass required to promote | [`operational-gates`](.claude/skills/operational-gates/SKILL.md) |
| `judge-calibration-cadence.md` | Judge calibration cadence | — |
| `intelligence-ledger-family.md` | Ledger writer/consulter invariants | [`ledger-consulter`](.claude/skills/ledger-consulter/SKILL.md) |

### MCP / infra / runtime
| Rule | Topic | Skill |
|---|---|---|
| `mcp-config-ssot.md` | MCP config SSOT | [`mcp-integration`](.claude/skills/mcp-integration/SKILL.md) |
| `mcp-pytest-enforcement.md` | Prefer pytest MCP | [`pytest-mcp`](.claude/skills/pytest-mcp/SKILL.md), [`testing-framework`](.claude/skills/testing-framework/SKILL.md) |
| `local-llm-wsl2-gpu.md` | Local LLM runtime (WSL2/Docker) | — |
| `claude-config-lookup.md` | Where Claude Code config lives | — |

### Plans / Notion
| Rule | Topic | Skill |
|---|---|---|
| `plan-location.md` / `plan-update-enforcement.md` / `plan-lifecycle-procedures.md` | Plan location, updates, lifecycle | [`plan-governance`](.claude/skills/plan-governance/SKILL.md) |
| `notion-plans-taxonomy.md` / `notion-plan-wave-deferral.md` / `notion-archived-databases.md` | Notion status taxonomy, deferral, archived DBs | [`notion`](.claude/skills/notion/SKILL.md) |
| `memory-management.md` / `memory-notion-writeback.md` | Memory lifecycle + writeback | [`memory-mcp`](.claude/skills/memory-mcp/SKILL.md), [`writeback-discipline`](.claude/skills/writeback-discipline/SKILL.md) |

### apps_rg (also see `apps_rg/CLAUDE.md`, auto-loaded under that subtree)
| Rule | Topic |
|---|---|
| `apps-rg-executive-summary-response.md` | Executive-summary default response shape |
| `apps-rg-interactive-discipline.md` | apps_rg interactive discipline |
| `apps-rg-post-run-summary.md` | Mandatory inline post-run summary |

> Retired redirect rules (deleted W3, plan `enforcement-surface-consolidation-d8b3f6`): 18 pure-redirect
> stubs (Author-Gate, ADG-consolidation, deferred-scope/next-step, notion/plan, mcp-serialization) were
> removed. Their signal already lived at canonical targets (constitutional §-citations are number-based
> and survive); the full redirect map is preserved in
> [retired-rules-index.md](docs/reports/governance/retired-rules-index.md).
