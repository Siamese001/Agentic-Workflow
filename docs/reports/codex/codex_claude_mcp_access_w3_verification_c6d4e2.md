# Codex Claude MCP Access W3 Verification

Generated: 2026-06-11  
Plan: `codex-claude-mcp-access-parity-c6d4e2` W3  
Scope: implement audit/verification helper support for Codex MCP access route classifications.

## W3 Result

W3 is complete.

- **W3.1 complete:** `scripts/governance/audit_codex_mcp_transports.py` now emits a `route_evidence` section derived from the W2 route contract.
- **W3.2 complete:** added fixture-backed unit tests for blocked transport, process-only, plugin substitute, substitute callable, degraded fallback, and missing-contract states.

## Implementation

Updated:

- `scripts/governance/audit_codex_mcp_transports.py`
- `tests/unit/scripts/governance/test_audit_codex_mcp_transports.py`

The audit helper now:

- Finds the latest `docs/reports/codex/codex_claude_mcp_access_contract_*.json` file, or uses `CODEX_MCP_ROUTE_CONTRACT` / `--route-contract`.
- Loads the W2 route contract as evidence, not as a second MCP registry.
- Combines that route contract with live process visibility.
- Emits route classifications in `route_evidence.servers`.
- Supports optional callable evidence through `CODEX_MCP_CALLABLE_<SERVER_ID>` values:
  - `healthy`
  - `closed_transport`
  - `plugin_callable`
  - `substitute_callable`
  - `absent`

## Supported Classifications

| Classification | Meaning |
|---|---|
| `CALLABLE` | Codex has healthy callable proof for the route. |
| `EXPOSED_BLOCKED` | A tool namespace or route is exposed, but the transport is closed or blocked. |
| `PLUGIN_SUBSTITUTE` | Codex uses a plugin route with a different API shape. |
| `SUBSTITUTE_CALLABLE` | Codex has a callable adjacent substitute, such as node/browser automation. |
| `PROCESS_ONLY` | A process is visible, but Codex cannot call the MCP tools. |
| `HOST_MCP_REQUIRED` | The route requires host-level MCP exposure before parity can be claimed. |
| `DEGRADED_FALLBACK` | Codex must use an explicitly degraded fallback. |
| `NOT_EXPOSED` | No configured, visible, or accepted route was found. |

## Live Audit Snapshot

`python scripts/governance/audit_codex_mcp_transports.py --json` emitted `route_evidence` with:

| Classification | Count |
|---|---:|
| `DEGRADED_FALLBACK` | 2 |
| `EXPOSED_BLOCKED` | 1 |
| `PLUGIN_SUBSTITUTE` | 1 |
| `PROCESS_ONLY` | 3 |
| `SUBSTITUTE_CALLABLE` | 1 |

Per-server result:

| MCP | Route Classification |
|---|---|
| `GitKraken` | `DEGRADED_FALLBACK` |
| `adg_sqlite` | `EXPOSED_BLOCKED` |
| `deepwiki` | `DEGRADED_FALLBACK` |
| `memory` | `PROCESS_ONLY` |
| `vector_db` | `PROCESS_ONLY` |
| `notion` | `PLUGIN_SUBSTITUTE` |
| `context7` | `PROCESS_ONLY` |
| `playwright` | `SUBSTITUTE_CALLABLE` |

## Verification

| Command | Result |
|---|---|
| `python -m pytest tests/unit/scripts/governance/test_audit_codex_mcp_transports.py -q` | `7 passed, 3 warnings` |
| `python scripts/governance/audit_codex_mcp_transports.py --json` | Exit 0; emitted `route_evidence` from W2 contract |

## W4 Inputs

W4 should run callable proof calls where Codex tools are exposed, record blocked/degraded proof rows for absent or closed routes, and update the Codex backup adapter documentation with the final access procedure.
