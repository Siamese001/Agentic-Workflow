# Filesystem MCP - Operator Guide

**Server**: `@modelcontextprotocol/server-filesystem@2026.1.14`  
**Config SSOT**: `.windsurf/mcp_config.json` -> key `"filesystem"`  
**Global config**: `~/.codeium/windsurf/mcp_config.json` (auto-synced by `post_write_mcp_config_sync.py`)  
**Updated**: 2026-04-16

---

## Normal Start Path

Windsurf reads `~/.codeium/windsurf/mcp_config.json` at startup and spawns:

```
node  .windsurf/scripts/filesystem_mcp_launcher.js  C:/Git/Agentic-Workflow
```

The launcher (`filesystem_mcp_launcher.js`) runs at startup and:
1. Locates `npm-cli.js` co-located with the active `node.exe` (`process.execPath`).
2. Calls `node npm-cli.js prefix -g` to resolve the global npm prefix dynamically.
3. Constructs the path to `@modelcontextprotocol/server-filesystem/dist/index.js`.
4. Verifies the script exists and fails with a clear diagnostic if not.
5. Spawns the server using `process.execPath` with explicit stdio proxying, not bare `stdio: inherit`.
6. Waits for the filesystem server readiness banner on stderr:
   - `Secure MCP Filesystem Server running on stdio`
7. Enforces a 15 second startup watchdog and terminates the child if readiness never arrives.
8. Forwards stdout as MCP protocol traffic only and mirrors stderr for diagnostics.
9. Pins `cwd` to `C:/Git/Agentic-Workflow`.
10. Tears the child down on wrapper exit and common termination signals.

**Key properties:**
- No npm registry fetch - server runs from the globally-installed package.
- No version-pinned absolute path anywhere - survives fnm version upgrades without config edits.
- No `.ps1` / `.cmd` launcher ambiguity - `node` is resolved by fnm's PATH shim.
- `cwd` is pinned to `C:/Git/Agentic-Workflow`.
- Startup hangs fail fast instead of leaving a silent long-lived wrapper.

**Allowed directories**: `C:/Git/Agentic-Workflow` only - repo root is the sole permitted scope.

---

## Why the launcher uses a startup watchdog instead of a total runtime timeout

The filesystem server is a long-lived stdio MCP process. A blanket lifetime timeout would kill a healthy server during normal use. The bounded control point is startup, so the launcher watches for the server readiness banner and only times out initialization.

---

## Prerequisites

```powershell
# 1. node is in PATH (fnm activates this)
node --version

# 2. The filesystem server package is globally installed
npm list -g --depth=0 @modelcontextprotocol/server-filesystem

# 3. The launcher exists in the repo
Test-Path "C:\Git\Agentic-Workflow\.windsurf\scripts\filesystem_mcp_launcher.js"
```

---

## Health Verification

```powershell
# Manually test the full launcher path.
# Expected stderr banner includes:
#   Secure MCP Filesystem Server running on stdio
#   Allowed directories: [ 'C:\Git\Agentic-Workflow' ]
# Use Ctrl+C to exit after the banner appears.
node C:\Git\Agentic-Workflow\.windsurf\scripts\filesystem_mcp_launcher.js C:\Git\Agentic-Workflow

# Check the launcher's dynamic resolution directly
node -e "
  const {execFileSync}=require('child_process');
  const path=require('path');
  const nodeDir=path.dirname(process.execPath);
  const npmCli=path.join(nodeDir,'node_modules','npm','bin','npm-cli.js');
  const prefix=execFileSync(process.execPath,[npmCli,'prefix','-g'],{encoding:'utf8'}).trim();
  const script=path.join(prefix,'node_modules','@modelcontextprotocol','server-filesystem','dist','index.js');
  const fs=require('fs');
  console.log('prefix:', prefix);
  console.log('server script exists:', fs.existsSync(script));
"
```

The `pre_mcp_gate.py` hook (`pre_mcp_tool_use`) also probes `node --version` and launcher file
existence on every filesystem tool call, emitting a descriptive `BLOCKED` message to stderr if
either check fails.

---

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| MCP panel shows red / tools unavailable | `node` not in PATH - fnm not activated | Run `fnm use <version>` in the shell that launches Windsurf, or set fnm default version |
| MCP panel shows red / tools unavailable | `server-filesystem` not globally installed | `npm install -g @modelcontextprotocol/server-filesystem@2026.1.14` |
| `[pre_mcp_gate] BLOCKED: Filesystem MCP cannot start` | Gate detected node or launcher missing | Follow the check named in stderr |
| `[filesystem_mcp_launcher] FATAL: server-filesystem not found` | Package uninstalled or wrong Node version active | Re-install under active node version; see Package Upgrade |
| `[filesystem_mcp_launcher] Startup timeout after 15000 ms ...` | Child process hung before readiness banner or stdout/stderr wiring is broken | Run the manual launcher test; inspect stderr; verify the active Node install and global package |
| `write_file` / `edit_file` / `move_file` blocked | Correct behavior - gate enforces native write tools | Use `write_to_file`, `edit`, or `multi_edit` native Cursor Agent tools instead |
| All filesystem reads fail after Windsurf update | Windsurf may have changed MCP spawn mechanism | Check Windsurf changelog; verify `node` resolves correctly; re-run manual launcher test |

---

## Exact Restart Procedure

```
1. Close Windsurf.
2. Verify prerequisites (see Prerequisites section above).
3. Open Windsurf - MCP starts automatically from global config.
4. If MCP panel still shows red: click the refresh/reconnect button in the MCP panel.
5. If still red: check Windsurf's MCP log output for the launcher FATAL or startup-timeout message.
```

---

## Node Version Upgrade Procedure

When upgrading Node.js via fnm (for example v24 -> v26):

```
1. Install and activate the new Node version:
   fnm install <new-version>
   fnm use <new-version>                    # or set as default: fnm default <new-version>

2. Re-install the filesystem server under the new version:
   npm install -g @modelcontextprotocol/server-filesystem@2026.1.14

3. Verify: npm list -g --depth=0 @modelcontextprotocol/server-filesystem

4. No changes needed to mcp_config.json or pre_mcp_gate.py - the launcher resolves
   the server path dynamically from the active Node version's npm prefix.

5. Restart Windsurf.
```

---

## Filesystem MCP Package Upgrade Procedure

When upgrading to a newer `@modelcontextprotocol/server-filesystem` release:

```
1. npm install -g @modelcontextprotocol/server-filesystem@<new-version>

2. Verify: npm list -g --depth=0 @modelcontextprotocol/server-filesystem

3. No changes needed to mcp_config.json or pre_mcp_gate.py - the launcher resolves
   the server script from the global prefix dynamically.

4. Update the version reference in the _startup comment in .windsurf/mcp_config.json
   if needed, then save.
   The post_write_mcp_config_sync.py hook auto-syncs to global.

5. Restart Windsurf.

6. Gate validation:
   echo '{"tool_info":{"mcp_server_name":"filesystem","mcp_tool_name":"read_text_file"}}' |
     python .windsurf/scripts/pre_mcp_gate.py
   # Expected: exit 0, no BLOCKED output
```

---

## Write Gate Policy

The `pre_mcp_tool_use` hook blocks these filesystem MCP tools - they bypass the constitutional
write gates that Cursor Agent's native tools enforce:

| Tool | Status | Reason |
|------|--------|--------|
| `write_file` | **BLOCKED** | Bypasses `pre_write_code` constitutional gates |
| `edit_file` | **BLOCKED** | Bypasses `pre_write_code` constitutional gates |
| `move_file` | **BLOCKED** | Mutates filesystem (rename/relocate); bypasses gates |
| All others | Allowed | Read-only or non-mutating operations |

**Correct alternatives**: Use Cursor Agent's native `write_to_file`, `edit`, or `multi_edit` tools -
these fire `pre_write_code` -> `pre_write_gate.py` -> constitutional anti-pattern and syntax checks.

---

## Allowed Directory Scope

The server is started with exactly one allowed directory: `C:/Git/Agentic-Workflow`.

- The server enforces this scope internally - any path outside the repo root is rejected by the
  server process itself, not just by the gate.
- Do NOT add additional directories to `args` without HITL approval (Constitutional Rule #0).
- Do NOT add `C:\Users\...` paths.

---

## References

- Config SSOT: `.windsurf/mcp_config.json` -> key `"filesystem"`
- Write gate: `.windsurf/scripts/pre_mcp_gate.py` -> `FILESYSTEM_WRITE_TOOLS`, `check_filesystem_startup_gate`, `check_filesystem_write_gate`
- Gate tests: `tests/unit/ops_scripts/hooks/windsurf/test_pre_mcp_gate.py`
- Write-gate RCA: `docs/reports/rca/filesystem_mcp_write_gate_bypass_rca.md`
- MCP Registry: `docs/guides/MCP_Registry.md`
- ADR-021: `docs/architecture/adr/ADR-021-hooks-mcp-recovery-limitations.md`
- Config version policy: `docs/guides/MCP_Config_Version_Policy.md`
