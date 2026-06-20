---
plan_id: codex-claude-mcp-access-parity-c6d4e2
plan_format: v2
plan_type: governance
status: Completed
ai_summary: "Give Codex Claude-equivalent callable MCP access from the repo .mcp.json SSOT without creating a parallel registry."
touches_governance_ci: true
touches_agentic_core: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
related_plans:
  - codex-mcp-transport-parity-4b9c7e
---

# Codex Claude MCP Access Parity

Give Codex the same practical MCP access as Claude Code for this repository: the root `.mcp.json` remains the single source of truth, Codex gets callable access to the same live server set where the host supports it, and any unavailable MCP has an explicit fallback with degraded-capability labeling.

> **plan_id discipline**: `plan_id` matches the filename stem `codex-claude-mcp-access-parity-c6d4e2`. Wave markers use `plan=codex-claude-mcp-access-parity-c6d4e2`.

## Context (SCQA)

- **Situation.** Claude Code reads the repo-root `.mcp.json` and exposes configured MCPs such as `GitKraken`, `adg_sqlite`, `memory`, `vector_db`, `notion`, `context7`, `playwright`, and `deepwiki`.
- **Complication.** Codex can inspect MCP config and local MCP processes, but it only receives tools that the Codex host exposes. A running Claude-owned stdio MCP process is not automatically callable by Codex after the fact.
- **Question.** How do we give Codex equivalent MCP access without creating a second MCP registry or drifting from Claude governance?
- **Answer.** Build a Codex access contract around the existing `.mcp.json`: inventory desired versus exposed tools, wire any host-supported MCP exposure from the same config, document explicit plugin or script fallbacks, and add verification that proves callable tools rather than merely live OS processes.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Inventory Claude MCP SSOT and Codex callable surfaces | ~20k | `.mcp.json` remains canonical | DONE | Matrix lists each configured MCP, expected Claude tool, Codex callable tool, and current gap |
| W2 | W2.1, W2.2 | Define Codex exposure path without a parallel registry | ~35k | Codex host may expose some MCPs through plugins/tools | DONE | Contract names the source config, exposure mechanism, fallback, and owner for every MCP |
| W3 | W3.1, W3.2 | Implement audit/verification helpers | ~45k | Existing `audit_codex_mcp_transports.py` is the starting point | DONE | Helper verifies callable MCP access where exposed and labels process-only visibility separately |
| W4 | W4.1, W4.2 | Prove parity and document operating procedure | ~30k | Some MCPs may remain host-gated | DONE | Verification report shows pass/degraded/blocked per MCP; docs explain how Codex gets same access as Claude |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Read `.mcp.json`, `.codex/mcp-notes.md`, and Codex tool inventory | DONE |
| W1.2 | Produce desired-vs-exposed MCP capability matrix | DONE |
| W2.1 | Select exposure mechanism per MCP: native Codex tool, plugin MCP, host-loaded MCP, or fallback | DONE |
| W2.2 | Define no-parallel-registry invariants and failure messages | DONE |
| W3.1 | Extend Codex MCP audit to distinguish callable tools from process presence | DONE |
| W3.2 | Add focused tests or fixtures for the audit classification | DONE |
| W4.1 | Run callable verification for each configured MCP | DONE |
| W4.2 | Update Codex primary adapter docs with the final access procedure | DONE |

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-06-11

> **W1 COMPLETE (2026-06-11).** Created the Codex/Claude MCP access inventory:
> `docs/reports/codex/codex_claude_mcp_access_inventory_c6d4e2.md` and
> `docs/reports/codex/codex_claude_mcp_access_inventory_c6d4e2.json`.
> W1 found eight live Claude MCPs in `.mcp.json`; Codex has no raw healthy
> parity route in this snapshot. `adg_sqlite` is exposed but blocked by a
> closed transport; `notion` is plugin-callable; `playwright` has a
> node/browser substitute; `memory`, `vector_db`, and `context7` are
> process-visible only; `GitKraken` and `deepwiki` are not exposed. W2 should
> choose host-level exposure versus accepted degraded/plugin routes.

> **W2 COMPLETE (2026-06-11).** Created the Codex/Claude MCP access contract:
> `docs/reports/codex/codex_claude_mcp_access_contract_c6d4e2.md` and
> `docs/reports/codex/codex_claude_mcp_access_contract_c6d4e2.json`.
> W2 selected a route for each configured MCP without creating a parallel
> registry: `memory`, `adg_sqlite`, `GitKraken`, `deepwiki`, `vector_db`, and
> `context7` require host-level MCP exposure for parity or explicit degraded
> fallback; `notion` is accepted through the Codex Notion plugin for this plan;
> `playwright` is accepted through node/browser substitutes unless raw
> Playwright MCP parity is explicitly required. W2 also defined standard
> failure messages for raw-unavailable, process-only, closed-transport,
> plugin-substitute, and no-substitute states.

> **W3 COMPLETE (2026-06-11).** Implemented W3 audit classification support
> in `scripts/governance/audit_codex_mcp_transports.py` and added focused
> tests in `tests/unit/scripts/governance/test_audit_codex_mcp_transports.py`.
> Created W3 verification artifacts:
> `docs/reports/codex/codex_claude_mcp_access_w3_verification_c6d4e2.md` and
> `docs/reports/codex/codex_claude_mcp_access_w3_verification_c6d4e2.json`.
> The audit now emits `route_evidence` from the W2 contract, including
> `EXPOSED_BLOCKED`, `PROCESS_ONLY`, `PLUGIN_SUBSTITUTE`,
> `SUBSTITUTE_CALLABLE`, and `DEGRADED_FALLBACK` classifications. Focused
> pytest passed with 7 tests.

> **W4 COMPLETE / PLAN COMPLETE (2026-06-11).** Created W4 closeout artifacts:
> `docs/reports/codex/codex_claude_mcp_access_w4_proof_c6d4e2.md` and
> `docs/reports/codex/codex_claude_mcp_access_w4_proof_c6d4e2.json`.
> Updated `docs/codex-primary-execution.md` with the final route-evidence
> operating procedure. W4 proof results: `notion` is a callable plugin
> substitute; `playwright` is a callable node/browser substitute; `adg_sqlite`
> is exposed but blocked by closed transport; `memory`, `vector_db`, and
> `context7` are process-only; `GitKraken` and `deepwiki` remain degraded
> fallback routes until the Codex host exposes raw MCP tools.

> **POST-COMPLETION E2E LIVE PROOF (2026-06-11).** Created live E2E proof
> artifacts:
> `docs/reports/codex/codex_claude_mcp_access_e2e_live_proof_c6d4e2.md` and
> `docs/reports/codex/codex_claude_mcp_access_e2e_live_proof_c6d4e2.json`.
> Live tests proved `adg_sqlite` as `CALLABLE` via successful `adg_health`,
> `notion` as `PLUGIN_SUBSTITUTE` via plan-page fetch, and `playwright` as
> `SUBSTITUTE_CALLABLE` via `node_repl.js`. The final audit passed with
> counts: `CALLABLE=1`, `PLUGIN_SUBSTITUTE=1`, `SUBSTITUTE_CALLABLE=1`,
> `PROCESS_ONLY=3`, and `DEGRADED_FALLBACK=2`. Focused pytest, plan-format
> validation, py_compile, git/rg fallback checks, and Codex backup verification
> all passed. Duplicate process cohorts remain hygiene debt and are not treated
> as callable proof.

> **POST-COMPLETION MCP COHORT CLEANUP (2026-06-11).** Fixed the duplicate
> MCP process cohorts caused by two Claude agent parents each owning a full MCP
> launch tree. Terminated 16 duplicate MCP child processes from the older
> Claude parent while preserving the newer cohort. Added guarded dry-run-first
> helper `scripts/governance/cleanup_duplicate_mcp_cohorts.py` and patched
> `scripts/governance/audit_codex_mcp_transports.py` to detect the live
> `tools.mcp.launch_adg_sqlite_mcp` launcher. Final audit shows
> `adg_sqlite`, `memory`, and `vector_db` as `single`, and `notion`,
> `context7`, and `playwright` as `single_launch_tree`. Cleanup proof artifacts:
> `docs/reports/codex/codex_mcp_process_cohort_cleanup_c6d4e2.md` and
> `docs/reports/codex/codex_mcp_process_cohort_cleanup_c6d4e2.json`.

## Scope

### In Scope

- Treat `C:\Git\Agentic-Workflow-FRESH\.mcp.json` as the only MCP server registry.
- Compare Claude-configured MCPs against the Codex tools actually exposed in-session.
- Define and verify callable access for:
  - `GitKraken`
  - `adg_sqlite`
  - `deepwiki`
  - `memory`
  - `vector_db`
  - `notion`
  - `context7`
  - `playwright`
- Extend or supplement `scripts/governance/audit_codex_mcp_transports.py` so it reports three separate states: configured, process-visible, and callable.
- Document precise degraded fallbacks when a Claude MCP cannot be exposed to Codex.

### Out of Scope

- Duplicating `.mcp.json` into a Codex-only registry.
- Copying Claude governance rule bodies into Codex skills.
- Manually launching detached stdio MCPs and treating them as equivalent to host-owned callable tools.
- Changing credentials or secrets.

## Design

### Access Contract

Codex MCP access is valid only when all four conditions hold:

1. The server is declared in root `.mcp.json`.
2. Required environment variables are present and do not contain unresolved placeholders.
3. The Codex host exposes a callable tool surface for that server, or the plan explicitly labels the route as degraded fallback.
4. Verification calls the tool surface successfully; process presence alone is not proof.

### Verification Matrix

| MCP | Desired callable proof | Fallback if unavailable |
|-----|------------------------|-------------------------|
| `GitKraken` | repository status/log tool succeeds | `git` CLI with GitKraken-unavailable note |
| `adg_sqlite` | `adg_health` succeeds | direct SQLite/read-only repo scripts with MCP-unavailable note |
| `deepwiki` | wiki structure or question call succeeds | web/repo docs search with degraded external-docs note |
| `memory` | `mem_recall_session_start` succeeds | local note in final response; no persistent-memory claim |
| `vector_db` | collection stats/list call succeeds | local Chroma inspection where safe |
| `notion` | Plans data source fetch/query/create succeeds | report Notion write blocked; do not fake registration |
| `context7` | library resolution succeeds | official docs/web search with citation |
| `playwright` | browser/session call succeeds | CLI Playwright only if interactive verification is still possible |

## Wave Details

### Wave 1 - Inventory

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

- W1.1: Read root `.mcp.json`, `.codex/mcp-notes.md`, and active Codex tool inventory.
- W1.2: Generate a table that separates configured, process-visible, and callable states.

### Wave 2 - Contract

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

- W2.1: Decide the exposure route for each MCP using the existing host/plugin capabilities.
- W2.2: Document fallback wording and the rule that fallback is not parity.

### Wave 3 - Implementation

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

- W3.1: Extend the Codex transport audit helper to include callable-tool evidence.
- W3.2: Add focused tests for classification and placeholder/env handling.

### Wave 4 - Verification and Docs

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

- W4.1: Run one proof call per MCP or record a blocked/degraded result.
- W4.2: Update Codex primary adapter documentation with the access procedure and verification command.

## Definition of Done

| # | Criterion | Verification |
|---|-----------|--------------|
| 1 | `.mcp.json` remains the only server registry | Diff review shows no copied registry |
| 2 | Capability matrix distinguishes configured/process/callable states | Generated report reviewed |
| 3 | Every configured MCP has a proof call or explicit degraded fallback | Verification report reviewed |
| 4 | Codex docs explain same-access procedure and limits | Doc diff reviewed |
| 5 | Codex primary adapter still verifies | `python scripts/governance/verify_codex_primary.py` |

## Risks

- Codex host may not support loading arbitrary repo MCPs directly.
- Some MCPs may be available through plugins with different tool names than Claude Code.
- Process cleanup can make a server healthy at the OS level while still not callable from Codex.

## Notion Registration

Expected Plans DB row:

- Slug: `codex-claude-mcp-access-parity-c6d4e2`
- Notion Status: `Not Started`
- Exists On Disk: yes
- Plan File Path: `plans/codex-claude-mcp-access-parity-c6d4e2.md`
- Summary: `Give Codex Claude-equivalent callable MCP access from the repo .mcp.json SSOT without creating a parallel registry.`
