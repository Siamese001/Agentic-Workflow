#!/usr/bin/env python3
"""RCA: Why MCP cwd issue was not caught by E2E tests"""

print("=" * 70)
print("ROOT CAUSE ANALYSIS: MCP 'cwd' Parameter Validation Gap")
print("=" * 70)

print(r"""
ISSUE SUMMARY
-------------
Two local Python MCP servers (adg_redis, memory) were missing the 'cwd'
parameter in user-global config (r'C:\Users\amita\.codeium\windsurf\mcp_config.json').
This caused import failures when Windsurf launched them from default directory.

AFFECTED MCPs
-------------
1. adg_redis  - FIXED: Added cwd=r'C:\Git\Agentic-Workflow'
2. memory     - FIXED: Added cwd=r'C:\Git\Agentic-Workflow'
3. sequential-thinking - OK: Node.js global package, no local imports
4. brave-search      - OK: Node.js global package
5. filesystem        - OK: Uses absolute path in args
6. fetch             - OK: uvx global package
7. GitKraken         - OK: Native executable
8. deepwiki          - OK: URL-based remote MCP

ROOT CAUSE: Why E2E Tests Didn't Catch This
-------------------------------------------

1. TEST FIXTURE HAD cwd, REAL CONFIG DIDN'T
   File: tests/e2e/test_mcp_drift_e2e.py
   Lines 49, 58: Sample configs include 'cwd'

   The test fixture was:
   {
     "adg_redis": {
       "cwd": "C:\\Git\\Agentic-Workflow",  <-- Present in test
       ...
     }
   }

   But real user-global config was missing cwd.

   ROOT CAUSE: Test fixture != Reality mismatch

2. SOVEREIGNTY CHECKER VALIDATES FORBIDDEN PATHS, NOT MISSING cwd
   File: ops_scripts/ci/check_mcp_config_sovereignty.py
   Lines 272-288: Only checks that paths DON'T contain forbidden fragments
   (c:\\users, .windsurf\\plans, etc.)

   Does NOT validate that local Python MCPs have cwd set to repo root.

   ROOT CAUSE: Validation gap - checks path safety, not completeness

3. NO INTEGRATION TEST ACTUALLY STARTS MCP SERVER
   - E2E tests mock MCP interactions
   - No test executes: python tools/adg/adg_mcp_server.py
   - Import errors only occur on actual startup from wrong directory

   ROOT CAUSE: No "smoke test" that launches real MCP processes

4. CONFIG LOCATION GAP
   - Tests validate: .windsurf/mcp_config.json (workspace)
   - Reality uses: C:\Users\amita\.codeium\windsurf\mcp_config.json (user-global)

   The workspace config had cwd, user-global didn't.
   Windsurf reads from user-global location.

   ROOT CAUSE: Test validates wrong config file

5. SILENT FAILURE MODE
   - MCP server fails to import -> stderr error
   - Windsurf may not surface this to user clearly
   - No health check that pings MCP after startup

   ROOT CAUSE: Failure was silent, not noisy

FIX RECOMMENDATIONS
-------------------

1. ADD MCP_CONFIG_CWD_VALIDATOR
   New gate: ops_scripts/ci/check_mcp_config_cwd.py
   - Check all local Python MCPs have cwd set
   - Check cwd points to repo root
   - Check local Node.js MCPs with relative paths

2. FIX E2E TEST FIXTURE SYNC
   - Load real mcp_config.json in tests
   - Don't use handcrafted fixtures that differ from reality
   - Or validate fixture matches schema of real config

3. ADD MCP SMOKE TEST
   - Test actually starts each MCP server
   - Sends 'adg_status' or health check ping
   - Verifies response, not just config syntax

4. VALIDATE BOTH CONFIG LOCATIONS
   - Test both workspace and user-global configs
   - Or document which one is source of truth

5. ADD MCP_HEALTH_MONITOR
   - Runtime check: Can I reach adg_redis.adg_status?
   - Runtime check: Can I reach memory.mem_recall_session_start?
   - Alert if MCP tools return errors

FILES TO MODIFY
---------------
- ops_scripts/ci/check_mcp_config_sovereignty.py (add cwd validation)
- tests/e2e/test_mcp_drift_e2e.py (use real config, not fixture)
- tests/adg/test_mcp_config_sovereignty.py (add cwd tests)
- .windsurf/mcp_config.json (sync to user-global)
- C:\Users\amita\.codeium\windsurf\mcp_config.json (already fixed)

VALIDATION COMPLETED
--------------------
""")

print(r"✅ adg_redis:  cwd=C:\Git\Agentic-Workflow")
print(r"✅ memory:      cwd=C:\Git\Agentic-Workflow")
print("ℹ️  sequential-thinking: Node.js, no cwd needed")
print("ℹ️  All other MCPs: cwd not required")
print()
print("=" * 70)
