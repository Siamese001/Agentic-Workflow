
<!-- Converted from `.claude/rules/mcp-pytest-enforcement.md`. Original Cursor trigger: `glob`. -->

> See `.cursor/RULES_INDEX.md#always-on-discipline` for shared retrieval / enforcement guidance.

# MCP PyTest Enforcement Rule

> **Scope clarification:** This rule governs **testing the MCP servers themselves** (e.g., `tools/mcp/vector_db_server.py`). For **using `pytest_mcp`** to discover/run tests, see `.claude/skills/pytest-mcp/SKILL.md`. The two are not the same concern.

## Constitutional Rule

**All MCP server code changes MUST pass PyTest validation before commit.**

## Scope

This rule applies to:
- All MCP server implementations in `tools/adg/mcp/` (ADG SQLite MCP) and `tools/mcp/` (pytest, otel, redis, memory servers)
- MCP client code in `agentic_core/`
- MCP-related test files in `tests/integration/`, `tests/unit/`

> **Note:** `tools/redis_mcp/`, `tools/memory_mcp/`, and `tools/filesystem_mcp/` do not exist as standalone directories. The filesystem MCP is npx-based (no local source). Redis and memory servers live under `tools/mcp/`.

## Mandatory Test Requirements

### 1. MCP Server Tests

Every MCP server MUST have:
- **Unit tests**: Test individual tool functions in isolation
- **Integration tests**: Test MCP protocol communication
- **Health check tests**: Verify health probe functionality
- **Error handling tests**: Test timeout, connection failure, invalid input

**Required test coverage:**
- All tools with `@mcp.tool` decorator must have tests
- All MCP startup/shutdown sequences must be tested
- All error paths must have test coverage

### 2. Hung Process Detection

**CRITICAL**: All MCP servers MUST handle hung process scenarios:

| Scenario | Required Behavior | Test Coverage |
|----------|-------------------|---------------|
| Tool call timeout | Return error, don't hang | Test with timeout decorator |
| Connection failure | Graceful degradation, retry | Test with mock failures |
| Process spawn failure | Surface error immediately | Test with invalid paths |
| Stderr overflow | Capture and report | Test with large stderr |
| Zombie process | Cleanup on exit | Test process lifecycle |

**CI Enforcement:**
- Gate: `ops_scripts/ci/run_contract_gates.py` (canonical entry point)
- Hung process detection: `ops_scripts/ci/mcp_hung_process_detector.py` — *verify script exists before invoking*

### 3. MCP Redis Specific Tests

**ADG Redis MCP** (`tools/adg/mcp/`) MUST have:
- Redis connection pool tests
- Cache hit/miss tests
- Concurrent access tests
- Timeout and retry tests
- Reconnection logic tests

**Test Commands:**
```bash
# Unit tests
pytest tests/unit/tools/adg/mcp/ -v

# Integration tests (requires Redis running)
pytest tests/integration/tools/adg/mcp/ -v --mcp-integration

# Hung process simulation
pytest tests/integration/tools/adg/mcp/test_hung_process.py -v
```

### 4. MCP Memory Specific Tests

**Memory MCP** (server: `memory`, source in `tools/mcp/`) MUST have:
- Memory graph CRUD tests
- Entity relationship tests
- Search and query tests
- Bulk operation tests

### 5. MCP Filesystem Specific Tests

**Filesystem MCP** (server: `filesystem`, npx-based — no local source directory) MUST have:
- Path validation tests (mock the MCP call)
- Permission tests (mocked)
- File operation tests
- Directory traversal tests

## Failure Modes

| Check | Failure Action |
|-------|----------------|
| Missing test coverage | Block commit, require tests |
| Hung process test missing | Block commit, add hung process tests |
| Timeout handling missing | Block commit, add timeout decorator |
| Health check missing | Block commit, add health probe |
| Integration test missing | Block commit, add integration test |

## CI Integration

When MCP code changes:
1. Run unit tests: `pytest tests/unit/tools/*/mcp/ -v`
2. Run integration tests: `pytest tests/integration/tools/*/mcp/ -v --mcp-integration`
3. Run hung process detector: `python ops_scripts/ci/mcp_hung_process_detector.py`
4. CI gate enforces all checks before merge

Pre-commit hook triggers on any file in `tools/*/mcp/` or `agentic_core/*/mcp/`.

## Enforcement

All MCP PyTest checks are enforced via:
- Pre-commit hooks (`.pre-commit-config.yaml`)
- CI gates (`python ops_scripts/ci/run_contract_gates.py`)
- Manual review for MCP architecture changes

**No bypass exceptions.** MCP test violations must be fixed before commit.

## Related Rules

- `.claude/rules/mcp-config-ssot.md` — MCP configuration management
- `.claude/rules/security-hardening.md` — Security checks for MCP code
- `.claude/rules/constitutional.md` §11 — Terminal process lifecycle management
