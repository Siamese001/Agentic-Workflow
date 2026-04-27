---
name: pytest-mcp
description: Test discovery, execution, coverage analysis, and pytest configuration inspection via the in-house pytest_mcp server. Invoke when the user asks to run tests, find tests, check coverage, inspect pytest config, or verify a code change against the test suite. Distinguishes pytest_mcp (structured tool surface) from raw pytest CLI via run_command. See sibling skill testing-framework for test-rigor invariants and ADG-backed scope selection.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
---

# Pytest MCP Skill

In-house. Prefer over raw `pytest` CLI when the operation maps cleanly onto an MCP tool — the MCP returns structured results.

**Sibling skill:** `testing-framework` (test rigor, ADG-backed scope selection, skip discipline)

## When To Use This MCP

| User intent | Use pytest_mcp? |
|---|---|
| Discover tests in a path | ✅ Yes |
| Run a scoped test set | ✅ Yes |
| Coverage analysis | ✅ Yes |
| Inspect pytest config | ✅ Yes |
| Test details (parameters, fixtures) | ✅ Yes |
| Custom pytest plugin work | ❌ Maybe — fall back to `run_command` if MCP doesn't expose the flag |

## Tool Routing

| Goal | Tool |
|---|---|
| Health probe | `pytest_mcp_health` |
| Discover tests by pattern | `discover_tests` |
| Run tests (with markers/keywords/timeout) | `run_tests` |
| Get details for a specific test | `get_test_details` |
| Coverage report | `analyze_test_coverage` |
| Show pytest config | `list_pytest_config` |

## Hard Rules

1. **No `pytest.mark.skip` without `strict=True`.** Constitutional §1.
2. **No weakened assertions / `xfail` workarounds.** Constitutional §1.
3. **ADG-backed scope selection for T2/T3 changes.** Use `adg_sqlite` to compute blast radius, then run only affected tests. (See `testing-framework/SKILL.md`.)
4. **MCP serialization (§25):** One MCP call per response.
5. **Timeouts:** Always set `timeout` parameter for runs that may stall (default 60s).

## Common Workflows

**Run tests affected by a change:**
1. `adg_sqlite.adg_edge_fanin(...)` → blast radius
2. `pytest_mcp.run_tests(path='tests/<affected>', timeout=120, verbose=true)`

**Coverage check:**
1. `pytest_mcp.analyze_test_coverage(path='agentic_core', format='term-missing')`

**Find tests for a module:**
1. `pytest_mcp.discover_tests(path='tests/<module>', pattern='test_*.py')`

## Output Format Conventions

`run_tests` returns structured pass/fail counts plus stdout for failures. Prefer this over parsing raw `pytest -v` output from `run_command`.
