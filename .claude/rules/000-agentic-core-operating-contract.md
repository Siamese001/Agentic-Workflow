
# Agentic Core Operating Contract for Claude Code

## Non-negotiable spine laws

- Deterministic workflow first: keep one live product path, one bounded agent, and one replayable artifact. Multi-agent and control-plane expansion comes later, after contracts, gates, replay, and state authority.
- L2 proposes. Exit clears. UWG commits. L4 stores. L6 learns only after the current-run boundary.
- Runtime gates decide live proceed/stop evidence. They do not emit final X3.
- X1D judges may assess semantic quality. X2 deterministic gates enforce hard correctness. X3 aggregates exactly one disposition.
- UNKNOWN is never PASS. Mocked, skipped, blocked, dry-run, or unavailable provider paths are not runtime ALLOW.
- No direct durable write path from L2, L3, tools, Exit, or L6.

## Repo boundary laws

- Do not edit `agentic_core` unless the user explicitly authorizes generic, app-agnostic spine work.
- Keep app-specific behavior inside `apps_*` overlays, app-owned runtime packages, fixtures, gates, judges, prompts, and manifests.
- For `apps_rg`, locked deterministic content stays deterministic: company names, titles, locations, dates, education, certifications, InsurTech, EY, and early career sections.
- Do not weaken a gate, schema, rubric, fixture, or test to make a bad output pass.

## ADG-first code understanding (structural queries)

For imports, consumers, references, blast radius, layers, or who-uses-X:

1. `adg_sqlite` MCP (`adg_health` first, then `adg_nodes_by_file` / `adg_edge_fanin` / `adg_edge_fanout`).
2. Direct `sqlite3` on latest `artifacts/adg/adg_indexed_<ts>.sqlite` if MCP is unavailable.
3. `Grep` / `grep_search` only after both fail — emit `DEGRADED_FALLBACK: reason=<mcp_err>+<sqlite_err>`.

`Grep` for TODOs, literals, comments, and non-structural text is allowed. Decision tree: `.claude/skills/graph-analysis/tool_routing_decision_tree.md`.

## Proof law

- Implementation claims require changed files, exact commands, command output, tests/gates, artifact paths, and honest status.
- Plans, prompts, receipts, dashboards, and manifests are support evidence only; they do not certify runtime until the live trace consumes them.
- PASS requires completed command output and passing tests/gates for the scoped seam.
- PARTIAL requires useful completed work plus explicit unfinished proof.
- FAIL requires exact failing command/output and smallest safe next patch.
- BLOCKED requires the missing dependency, unavailable provider, permission issue, or policy stop condition.
