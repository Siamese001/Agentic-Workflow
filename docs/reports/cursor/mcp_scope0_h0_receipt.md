# MCP Scope 0 — H0 remediation receipt

**Wave:** H0 (restore automated Rule #0 enforcement)  
**Generated:** 2026-05-19

## STATUS: PASS

## Summary

Restored `ops_scripts/ci/check_mcp_config_sovereignty.py` to enforce Constitutional **Rule #0** on both editor MCP configs:

- [`.cursor/mcp.json`](../../.cursor/mcp.json) — Cursor project SSOT
- [`.windsurf/mcp_config.json`](../../.windsurf/mcp_config.json) — Windsurf mirror

The gate validates structural filesystem scope (launcher + `${env:AGENTIC_REPO_ROOT}` only), scans **operational** fields for forbidden out-of-repo path fragments, and allows `filesystem.disabled: true` (shadow-disable policy).

## FILES_CHANGED

- [check_mcp_config_sovereignty.py](../../ops_scripts/ci/check_mcp_config_sovereignty.py) — new gate (stdlib-only, dual-profile)
- [test_check_mcp_config_sovereignty.py](../../tests/unit/ops_scripts/ci/test_check_mcp_config_sovereignty.py) — unit tests
- [run_contract_gates.py](../../ops_scripts/ci/run_contract_gates.py) — early + advisory wiring
- [.pre-commit-config.yaml](../../.pre-commit-config.yaml) — hook `mcp-config-sovereignty` (T11)

## COMMANDS_RUN

| Command | Exit |
|---------|-----:|
| `python ops_scripts/ci/check_mcp_config_sovereignty.py` | 0 |
| `pytest tests/unit/ops_scripts/ci/test_check_mcp_config_sovereignty.py -q` | 0 (8 passed) |

## ARTIFACTS

- [mcp_config_sovereignty.json](../../artifacts/ci/mcp_config_sovereignty.json)
- [mcp_scope0_h0_receipt.md](mcp_scope0_h0_receipt.md)

## Gate behavior

| Check | Enforced |
|-------|----------|
| `filesystem` present | Yes |
| `args` length = 2 | Yes |
| Launcher path matches editor (`.cursor/` vs `.windsurf/`) | Yes |
| Second arg = `${env:AGENTIC_REPO_ROOT}` | Yes |
| Forbidden fragments in `command`/`args`/`env`/`cwd`/`url` | Yes |
| `_comment` prose documenting forbidden paths | Allowed (not scanned) |
| `disabled: true` on filesystem | Allowed |

**Bypass:** `MCP_CONFIG_SOVEREIGNTY_BYPASS=1`

## Notion

- Backlog row: [P2 MCP H0 — Scope 0 CI gate (Rule #0)](https://www.notion.so/P2-MCP-H0-Scope-0-CI-gate-Rule-0-36527693f55c81b59103ca869fe780fd) (`36527693-f55c-81b5-9103-ca869fe780fd`)
- Closeout: [mcp_scope0_closeout_receipt.md](mcp_scope0_closeout_receipt.md) (H0 + H1 combined)

## Deferred (not in H0)

- ~~AGENTS.md archived MCP Registry SSOT line update~~ → done in [H1](mcp_scope0_h1_receipt.md)
- Tavily/Playwright version pin parity (H2)
- Operator smoke with filesystem re-enabled (H3)
