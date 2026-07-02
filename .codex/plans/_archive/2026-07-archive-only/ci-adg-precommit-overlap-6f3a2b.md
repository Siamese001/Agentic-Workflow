---
slug: ci-adg-precommit-overlap-6f3a2b
status: Completed
plan_type: platform_core_change
tier: T2
created: 2026-06-07
owner: Codex
notion_registration: completed
notion_page_id: 37827693-f55c-8107-bfd5-e5a7c6551700
notion_url: https://app.notion.com/p/37827693f55c8107bfd5e5a7c6551700
---

# CI / ADG / Pre-Commit Overlap Cleanup

## Context

- **Situation.** GitHub Actions, ADG CI, and pre-commit are intentionally layered: local hooks catch cheap scoped regressions, while CI runs authoritative full-repo sweeps.
- **Complication.** The overlap review found stale `.mcp.json` references after the completed `.cursor` -> `.codex` migration. Helper code already treats root `.mcp.json` as the live MCP SSOT, but local hook triggers and docs still name the deleted `.mcp.json`, making pre-commit blind to `.mcp.json` edits.
- **Question.** How do we remove harmful redundancy without weakening deliberate two-lane coverage?
- **Answer.** Keep deliberate pre-commit/CI mirrors, repair the stale MCP SSOT paths, and path-scope ADG PR execution so heavy ADG gates run when ADG-relevant surfaces change.

## Status Tables

### Wave Progress

| Wave | Focus | Status | Success Criteria |
|---|---|---|---|
| W1 | MCP SSOT drift between pre-commit, docs, and CI helper prose | Done | `.mcp.json` edits trigger local hooks; docs/user-facing messages name root `.mcp.json` |
| W2 | ADG PR trigger redundancy | Done | `adg-ci-gates.yml` PR trigger is path-scoped like push, with workflow/config self-triggers |
| W3 | Verification and closeout | Done | Targeted governance checks pass or failures are documented with exact blockers |

### Wave Detail

| Wave | Implementation |
|---|---|
| W1 | Update `.pre-commit-config.yaml`, `AGENTS.md`, `.codex/governance/scripts/sync_mcp_config.py`, MCP CI gate docstrings/messages, and ADG gate manifest path references from `.mcp.json` to `.mcp.json` where the live code already resolves root `.mcp.json`. |
| W2 | Add PR path filters to `.github/workflows/adg-ci-gates.yml` matching the existing push paths plus the workflow and root MCP config, reducing doc/config-only ADG runs while preserving ADG coverage. |
| W3 | Run targeted MCP sync/schema/coverage checks, pre-commit hook-level checks where practical, YAML parsing for workflows, and `python scripts/governance/verify_codex_primary.py` if Codex backup docs or skills changed. |

## Registration Note

Notion plan registration completed from Codex after lazy-loading the Notion write tools:

- Page ID: `37827693-f55c-8107-bfd5-e5a7c6551700`
- URL: <https://app.notion.com/p/37827693f55c8107bfd5e5a7c6551700>
- Data source: `collection://ac53d31b-3068-4039-9ebe-856c12caab32`

## Closeout

- W1 aligned the active MCP enforcement surface to root `.mcp.json`: pre-commit hook triggers, root guidance, sync generator prose, MCP CI gate docstrings/messages, and the ADG gate manifest now name the live SSOT.
- W1 also retired obsolete local pre-commit hooks for legacy editor-era MCP schema/parity/sovereignty assumptions; the active root MCP contract is covered by sync integrity, AGENTS coverage, and autogen-block sync.
- W2 scoped `adg-ci-gates.yml` PR execution to ADG-relevant paths, matching push behavior while adding `config/**`, `.mcp.json`, and workflow/setup self-triggers.
- W3 updated the Codex primary adapter verifier/doc and the personal Codex governance skill to point at `.codex`, `.mcp.json`, and `.codex/hooks.json`.
- W3 verification was run from Codex with available local tooling; see the Codex turn summary for pass/fail details and any environment-limited checks.
