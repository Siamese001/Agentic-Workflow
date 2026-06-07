# Agentic-Workflow — Claude Code Operating Contract

> This is the always-on SSOT for Claude Code in this repo. It supersedes `AGENTS.md` (the prior
> Cursor-era contract, kept as legacy). Specialized guidance lives on demand in `.claude/rules/`,
> `.claude/skills/`, and subdirectory `CLAUDE.md` files — see the index at the bottom.

## Plan First. Execute Second.

- **T2/T3** (2+ files, cross-layer, architecture, multi-file debug): first output = a plan; invoke
  the [`structured-reasoning`](.claude/skills/structured-reasoning/SKILL.md) skill →
  `SR_INTAKE` … `SR_VERIFY`. See `.claude/rules/sequential-thinking-enforcement.md`.
- **T0/T1**: single file ≤20 lines or questions — answer/edit directly.
- **Layer separation:** Reasoning / Routing / Execution / Verification — no edits before `SR_APPROVAL`.

## Constitutional floor (always-on)

Full text: [`.claude/rules/constitutional.md`](.claude/rules/constitutional.md). Hard constraints:

- **No PowerShell for repo automation** — `subprocess.run(argv, shell=False, timeout=30)`. Subprocess timeout always required.
- **No test skipping** — no `pytest.mark.skip`, no `xfail` without `strict=True`.
- **No editing while exploring** — all repair gates pass before any edit; mode separation (`analyze`/`plan`/`edit`/`verify`).
- **Precise exceptions** — no bare `except:` / `except Exception` without a guardian comment.
- **ADG before structural grep** — ingest `artifacts/adg/*.sqlite` before T2/T3 query/edit; grep only for literals/TODOs.
- **No app leakage into `agentic_core`** without a migration receipt; no imports from `archives/` in production.
- **Author-Gate for ambiguous decisions** (see below). **CI enforces all of this**: `python ops_scripts/ci/run_contract_gates.py`.
- **Memory lifecycle** — call `mem_recall_session_start` at session start; write back significant decisions.

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

Detail: `.claude/rules/003-cursor-author-gate-hitl.md` · triggers `.claude/rules/author-gate-decision-points.md` ·
scoring `.claude/rules/author-gate-enforcement.md`. Skills:
[`author-gate-packet-builder`](.claude/skills/author-gate-packet-builder/SKILL.md),
[`author-gate-ui-renderer`](.claude/skills/author-gate-ui-renderer/SKILL.md).

Stop and ask (via `AskUserQuestion`) before edits when the decision is `architecture_choice`,
`refactor_scope`, `anti_pattern`, `deletion_strategy`, `dependency_addition`, `test_strategy`, or
`error_handling` — i.e. two+ plausible approaches with different blast radius and no unambiguous user
directive. Pipeline (same response): precedent lookup (`refactor-decision-memory`) → emit packet →
render options → ask → capture `DECISION_CAPTURED:`. Do **not** fire for typos, single-path fixes, or
explicit instructions.

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
`.claude/hooks/`. They reuse the existing governance engine under `.cursor/scripts/**` as a backend
(the one live dependency on the legacy tree). Block signal = exit code 2 + reason on stderr.

## Pytest

`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` — load plugins via `-p` in `pytest.ini` `addopts`. Prefer the
`pytest_mcp` server over the bare CLI.

## Core vs apps

Apps customize inputs; core enforces contracts. No app-specific behavior in `agentic_core` without a
migration receipt. Detail: `.claude/rules/agentic-core-static.md`, `.claude/rules/apps-customization.md`,
[`agentic_core/AGENTS.md`](agentic_core/AGENTS.md).

## Plans & memory

- Plans SSOT remains `.cursor/plans/<slug>-<6hex>.md` (plan data not migrated). See
  `.claude/rules/plan-location.md`, skill [`plan-governance`](.claude/skills/plan-governance/SKILL.md).
- Memory: first tool call each session is `mem_recall_session_start`. Detail
  `.claude/rules/memory-management.md`, skill [`memory-mcp`](.claude/skills/memory-mcp/SKILL.md).

---

## Specialized rules — load when relevant

On-demand reference docs (the Cursor "agent-requested" layer). Read the file when a task matches.
A **Skill** column entry means a richer procedural skill covers the same area — prefer it.

### Governance / process
| Rule | Topic | Skill |
|---|---|---|
| `scope-containment.md` | No gold-plating; one task at a time | [`scope-containment`](.claude/skills/scope-containment/SKILL.md) |
| `approval-exception-policy.md` | When approval/exceptions apply | — |
| `deferred-scope-capture.md` | Capturing out-of-scope work | — |
| `next-step-capture.md` | Recording the next step | — |
| `refactor-decision-memory.md` | Pre-Author-Gate precedent check | [`refactor-decision-memory`](.claude/skills/refactor-decision-memory/SKILL.md) |
| `author-gate-decision-points.md` / `author-gate-enforcement.md` / `author-gate-queue-drain.md` / `author-gate-svp-calibration.md` | Author-Gate doctrine, scoring, queue | [`author-gate-packet-builder`](.claude/skills/author-gate-packet-builder/SKILL.md) |
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

### Eval / judges / fortknox
| Rule | Topic | Skill |
|---|---|---|
| `evaluation-promotion-gate.md` | Regression-pass required to promote | [`operational-gates`](.claude/skills/operational-gates/SKILL.md) |
| `judge-calibration-cadence.md` | Judge calibration cadence | — |
| `fortknox-certification-discipline.md` | Fort Knox certification | [`fortknox-evidence`](.claude/skills/fortknox-evidence/SKILL.md) |
| `intelligence-ledger-family.md` | Ledger writer/consulter invariants | [`ledger-consulter`](.claude/skills/ledger-consulter/SKILL.md) |

### MCP / infra / runtime
| Rule | Topic | Skill |
|---|---|---|
| `mcp-config-ssot.md` / `mcp-serialization.md` | MCP config SSOT + serialization | [`mcp-integration`](.claude/skills/mcp-integration/SKILL.md) |
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

> Deprecated rules (kept for reference, not active): `adg-graph-layer-enforcement`, `adg-hotspot-enforcement`,
> `adg-p7-analyst-artifacts`, `adg-repair-discipline`, `adg-test-accelerator-enforcement`,
> `anti-pattern-author-gate`, `notion-backlog-plan-linkage`, `notion-plan-identity-verification`,
> `plan-registration-enforcement`, `wave-completion-discipline`.
