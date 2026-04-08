# Sequential Thinking MCP — Retirement & Replacement

**Status**: RETIRED (2026-04-07)
**Replacement**: Native Cascade reasoning + compositional MCP pattern
**Workflow**: `/structured-reasoning`
**Skill**: `.windsurf/skills/structured-reasoning/SKILL.md`
**Rule**: `.windsurf/rules/sequential-thinking-enforcement.md`

---

## Why Sequential Thinking Was Retired

### Root Cause Assessment

**Confirmed findings:**

1. **stdio transport fragility on Windows** — The Sequential Thinking MCP used `@modelcontextprotocol/server-sequential-thinking` via Node.js stdio transport. On Windows, `npx` without `.cmd` extension fails to resolve in subprocess context. The backup config (`mcp_config_backup.json`) shows the server was launched with a hardcoded absolute path to `node.exe` — a fragile workaround for this exact problem.

2. **Zombie node.exe processes** — When the MCP hung, it left orphaned `node.exe` processes that blocked subsequent starts. Recovery required `taskkill /f /im node.exe`, which kills all Node processes in the system.

3. **The `mcp_config_enhanced.json` shows attempted over-configuration** — The file contains 7 custom environment variables (`SEQUENTIAL_THINKING_KIMI_MODE`, `SEQUENTIAL_THINKING_AUTO_TRIGGER`, `SEQUENTIAL_THINKING_INTEGRATION_MODE`, etc.) that are not part of the published MCP protocol. These are cargo-cult knobs — they have no effect on the actual server but indicate increasingly desperate tuning attempts.

4. **`DISABLE_THOUGHT_LOGGING=true` was set** — This suppresses the only diagnostic output the server emits, making hang diagnosis impossible. The fix for "it's noisy" created "it's silent when broken."

5. **Capability negotiation mismatch** — The server expects to be invoked repeatedly as a "reasoning loop" tool. In practice, Windsurf's Cascade model drives the reasoning natively; the MCP was being used as a meta-layer on top of an already-reasoning model, creating a redundant abstraction with no performance guarantee.

**Likely findings (not fully confirmed):**

6. **Bad invocation pattern** — Cascade was expected to call `mcp7_sequentialthinking` as a blocking reasoning primitive, then act on its output. This created a synchronous dependency on a process that could hang indefinitely. No timeout was configured at the Windsurf layer.

7. **Oversized tool surface** — The server exposed a single tool (`sequentialthinking`) with open-ended parameters. This made parameter validation impossible and created an opaque black box that violated the compositional principle.

**Unknowns:**

- Whether the server would have been stable on a Unix host (stdio is more reliable there)
- The exact hang trigger (network call? file system? node module resolution?)
- Whether the ADG-awareness env vars were ever parsed by any code

**Operationally irrelevant:**

Even if the root cause is fully resolved, the architectural case for a dedicated "reasoning MCP" is weak. Cascade's native reasoning is more capable, observable, and reliable than a tool-server abstraction that adds latency and failure modes without adding capability.

---

## Replacement Architecture

The replacement reproduces all Sequential Thinking behaviors using current healthy MCPs and native Windsurf features.

### What Sequential Thinking Was Supposed to Provide

| Capability | Old approach | Replacement |
|------------|-------------|-------------|
| Task decomposition | `sequentialthinking` tool call | `mcp13_create_task` + `mcp13_decompose_task` + native Cascade |
| Ordered reasoning | MCP thought chain | SR_PLAN numbered steps (explicit, inspectable) |
| Revision / self-correction | MCP internal state | SR_PLAN_v2 with explicit revision reason |
| Branching under uncertainty | MCP branch parameter | BRANCH POINT blocks + HITL via `ask_user_question` |
| Explicit tool selection | MCP output | "Tools needed:" section in SR_PLAN |
| Controlled execution after plan validation | MCP gate | SR_APPROVAL gate (APPROVED / REVISED / CLARIFY / ABSTAIN) |

### Five-Phase Pattern

```
A: Intake        → normalize goal, constraints, assumptions
B: Decompose     → numbered plan, branch points, tool selection
C: Evidence pull → read-only — ADG, files, session context
D: Approval gate → APPROVED / REVISED / CLARIFY / ABSTAIN
E: Execute       → step by step, named tools, result check before next step
F: Verify        → SR_SUMMARY — what changed, what verified, what uncertain
```

**Key invariant**: Phases A–D produce no edits. Phase E only runs if D emits APPROVED.

---

## MCP Role Mapping

Each MCP has exactly one functional role. No single MCP is an opaque reasoning black box.

| MCP | Prefix | Role | Reliability |
|-----|--------|------|-------------|
| ADG SQLite | `mcp1` | Context / evidence — primary structural truth | High (Python, local SQLite) |
| Memory | `mcp9` | Memory / checkpointing — session context | Medium (SQLite, depends on memory server) |
| Task Manager | `mcp13` | Plan tracking / decomposition | Medium (npx-based, can degrade) |
| Filesystem | `mcp7` | Context / evidence — file reads | High (npx, but `read_file` native fallback always available) |
| Pytest MCP | `mcp11` | Validation / verification | Medium (Python, depends on pytest server) |
| GitKraken | `mcp0` | Validation / version control | High (gk.exe, binary) |
| Brave Search | `mcp2` | External lookup | Medium (requires API key, network) |
| Enhanced HTTP | `mcp4` | External lookup — HTTP requests | Medium (Python, local) |
| DeepWiki | `mcp3` | External lookup — repo docs | Low (remote URL, network dependent) |
| Redis MCP | `mcp12` | Cache / state inspection | Medium (depends on Redis server running) |
| Playwright | `mcp10` | External lookup / browser automation | Low (heavy, use only when needed) |
| Figma | mcp6 | External lookup — design assets | Low (requires API key, use only when needed) |

**Fallback chain for evidence failure:**
1. ADG MCP fails → `/mcp-failure-rca` → do NOT grep
2. Memory MCP fails → proceed without session context, note `[MEMORY UNAVAILABLE]`
3. All file MCPs fail → use `read_file` Windsurf native (always present)

---

## Invocation Examples

### Example 1 — T2 Scoped Refactor

```
/structured-reasoning

## SR_INTAKE
Objective: Move RedisClient instantiation in L3 orchestration to use the shared connection pool
Constraints:
  - Must not break existing L3 integration tests
  - L3→L4 layer direction must be preserved
Assumptions:
  - Shared pool is at agentic_core/L4_memory/redis_pool.py (to confirm)
Tier: T2
Complexity: medium

## SR_PLAN
1. mcp1_adg_health — confirm ADG healthy
2. mcp9_mem_recall_session_start — load session context
3. mcp1_adg_nodes_by_file on L3 orchestration files — find RedisClient nodes
4. mcp1_adg_edge_fanout — find what depends on current Redis usage
5. Read agentic_core/L4_memory/redis_pool.py
6. Edit L3 file to use pool
7. pytest tests/unit/agentic_core/L3_orchestration/ -q
```

### Example 2 — T3 Architecture Decision

```
/structured-reasoning

## SR_INTAKE
Objective: Introduce a new L2 execution engine for async task dispatch
Constraints:
  - Must fit L2 layer; cannot import from L3+
  - Must have unit tests before any integration wiring
Assumptions:
  - No existing async dispatch engine (to confirm via ADG dedup check)
Tier: T3
Complexity: complex

BRANCH POINT — Step 3:
  Plan A: Extend base_exec_engine.py — use if async interface already abstract
  Plan B: Create new async_exec_engine.py — use if base class is sync-only
  Selecting after reading base_exec_engine.py
```

### Example 3 — MCP Failure Mid-Execution

```
## EXECUTING Step 4 — ADG fanout query
mcp1_adg_edge_fanout called → HANG (no response after 10s)

## SR_STEP_FAILURE
Failed step: 4
Error: mcp1_adg_edge_fanout hung indefinitely
Recovery: OPTION A — Run /mcp-failure-rca before continuing
[MCP UNAVAILABLE — ADG SQLite — running /mcp-failure-rca]
```

---

## Failure Handling

### If ADG MCP is down
→ Run `/mcp-failure-rca`. Do NOT grep. Work is blocked until MCP is healthy.

### If Task Manager is down
→ Use `todo_list` native Windsurf tool. Note `[TASK MANAGER UNAVAILABLE]`.

### If Memory MCP is down
→ Proceed without session context. Note `[MEMORY UNAVAILABLE]`. Do not block on this.

### If plan evidence is too weak
→ Emit `SR_APPROVAL: ABSTAIN`. Explain what's missing. Ask user to provide missing information.

### If execution partially completes then fails
→ Emit `SR_STEP_FAILURE` block. Select recovery option. Do not silently continue.

---

## Operator Guidance

### Daily use
- T0/T1 tasks: skip this workflow entirely — answer directly or edit directly
- T2/T3 tasks: invoke `/structured-reasoning` or apply the skill naturally
- The plan block does not need to be verbose — 5–8 steps is enough for most T2 tasks

### When the plan changes mid-execution
- Stop. Emit `SR_PLAN_v2`. Re-validate before continuing.
- Do not silently carry forward stale assumptions.

### When to ABSTAIN
- Evidence contradicts the plan and you cannot resolve it
- A required MCP is down and its data is critical to the plan
- The blast radius is larger than estimated and the user needs to decide scope

### Maintaining this replacement
- **Skill**: `.windsurf/skills/structured-reasoning/SKILL.md`
- **Workflow**: `.windsurf/workflows/structured-reasoning.md`
- **Rule**: `.windsurf/rules/sequential-thinking-enforcement.md`
- **This doc**: `docs/mcp/sequential-thinking-replacement.md`

If the Task Manager MCP (`mcp13`) becomes unreliable, replace its role with the `todo_list` native tool — the pattern does not depend on it.

---

## What Was NOT Replaced

The Sequential Thinking MCP was never used for:
- File reads (that's Filesystem MCP / native `read_file`)
- Code execution (that's `run_command`)
- Test running (that's Pytest MCP / `run_command`)
- Git operations (that's GitKraken MCP / `run_command`)

It was used only for "structured thinking about what to do." That capability is now provided by:
1. Cascade's native reasoning (the model itself)
2. The explicit SR_INTAKE + SR_PLAN + SR_APPROVAL protocol (the behavioral rule)
3. Task Manager MCP for durable step tracking

This is simpler, more observable, and more reliable than the MCP it replaces.
