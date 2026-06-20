# Codex MCP W5 Verification Closeout

Generated: 2026-06-10  
Plan: `codex-mcp-transport-parity-4b9c7e` W5  
Scope: Codex adapter documentation, Notion registration sync, and verification gates.

## W5 Result

W5 is complete out of order by explicit user request while W2.3 remains blocked.
The plan as a whole remains `IN_PROGRESS` because live ADG MCP still serves the
primary checkout without the eval-harness Redis decode fix.

## Adapter Documentation Updates

Updated thin Codex adapter pointers:

| File | Update |
|---|---|
| `docs/codex-primary-execution.md` | Added `.codex/mcp-notes.md`, MCP report evidence pointers, and the read-only transport audit helper. |
| `C:\Users\amita\.codex\skills\agentic-workflow-governance\SKILL.md` | Added `.codex/mcp-notes.md` as a canonical source and named the transport audit helper. |
| `C:\Users\amita\.codex\skills\agentic-workflow-verification\SKILL.md` | Added the transport audit helper and reiterated that report files are evidence snapshots, not routing SSOT. |

No Claude rule bodies were copied into Codex. Live MCP routing still comes from
`.mcp.json`; dormant/re-add routing still comes from `.codex/mcp-notes.md`;
procedure still comes from `mcp-integration`.

## Notion Registration

Existing Notion Plans row:

| Field | Value |
|---|---|
| URL | `https://app.notion.com/p/37b27693f55c8195864af01d07b7181a` |
| Slug | `codex-mcp-transport-parity-4b9c7e` |
| Status | `In Progress` |
| Exists On Disk | `__YES__` |
| Plan File Path | `plans/codex-mcp-transport-parity-4b9c7e.md` |

The original creation acceptance expected `Status=Not Started`. The row is now
correctly `In Progress` because W1, W2 partial, W3, W4, and W5 have been
executed. It should not be marked `Completed` while W2.3 remains blocked.

## Verification Gates

| Gate | Result |
|---|---|
| `python scripts/governance/verify_codex_primary.py` | PASS |
| `python scripts/governance/audit_codex_mcp_transports.py --json` | PASS |
| `python -m py_compile scripts/governance/audit_codex_mcp_transports.py scripts/governance/verify_codex_primary.py` | PASS |
| Focused pytest slice | PASS: `14 passed, 5 warnings` |

Focused pytest command:

```bash
python -m pytest -p pytest_timeout tests/unit/adg/test_path_resolver_sentinel_rejection.py tests/unit/tools/adg/test_adg_mcp_fixes.py::TestRedisUrlEnvOverride -q
```

## Residual Risk

- `W2.3` remains blocked by `ADG-LIVE-CODE-MISMATCH`.
- `W4-ADG-DUPLICATE-PROCESS` remains open: two `adg_sqlite` Python stdio
  server processes exist; `adg_runtime_info` reports PID `12236` as the live
  process.
- The eval worktree lacks `artifacts/adg`, while the live ADG MCP serves the
  primary checkout's ADG artifact directory.

## Closeout State

W1, W3, W4, and W5 are complete. W2 is partially complete and blocked. The main
wave cursor stays on W2 until the live ADG code/runtime mismatch is resolved.
