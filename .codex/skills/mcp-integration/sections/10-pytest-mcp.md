## §10 — Pytest MCP

**In-house.** Prefer over raw `pytest` CLI when operation maps cleanly.

### When To Use

| Intent | Use? |
|--------|------|
| Discover tests | ✅ Yes |
| Run scoped test set | ✅ Yes |
| Coverage analysis | ✅ Yes |
| Inspect pytest config | ✅ Yes |
| Custom plugin work | ❌ Maybe — fall back to `run_command` |

### Tool Routing

| Goal | Tool |
|------|------|
| Health probe | `pytest_mcp_health` |
| Discover tests | `discover_tests` |
| Run tests | `run_tests` |
| Test details | `get_test_details` |
| Coverage | `analyze_test_coverage` |
| Show config | `list_pytest_config` |

### Hard Rules
1. **No `pytest.mark.skip`** without `strict=True` — constitutional §1
2. **No weakened assertions** — constitutional §1
3. **ADG-backed scope selection** — use `adg_sqlite` for blast radius
5. **Timeouts** — always set `timeout` for runs that may stall

---
