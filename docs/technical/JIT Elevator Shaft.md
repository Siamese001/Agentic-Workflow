# JIT Elevator Shaft

## Overview

The JIT Elevator Shaft is the just-in-time context assembly and execution dispatch system. It loads only the agent components, context chunks, and tool registrations required for the current task at the moment of execution — no pre-warming, no broad pre-loading. The "elevator shaft" metaphor reflects vertical traversal from L1 (Cognition) through L2 (Execution) to L3 (Orchestration) with dynamic agent loading at each stop.

---

## Architecture

```
MissionRequest
     │
     ▼
DecompositionOrchestrator (L3)
     │  breaks mission into AtomicTask list with dependency graph
     ▼
Orchestrator (L3) — dispatches per-task
     │  _validate_agent_import (JIT import check)
     │  run_agent(agent_name, context)
     ▼
ActionNode / ActionNodeCore (L2)
     │  _select_tools (JIT tool selection from tool_registry)
     │  _execute_tools
     ▼
ContextCurator (L3)
     │  add_chunk / pin_chunk / prune_by_relevance
     │  get_context_window → formatted LLM context
     ▼
CognitiveNode / CognitiveNodeRefactored (L1)
     │  _lazy_memory_prefetch (non-blocking JIT semantic prefetch)
     │  process_async
     ▼
SovereignLLMGateway (L2) — LLM call with provider health check
```

---

## L3 — Decomposition Orchestrator

**File:** `agentic_core/L3_orchestration/engines/decomposition_orchestrator.py`

`DecompositionOrchestrator` (dataclass) breaks a high-level mission prompt into an ordered `MissionPlan`.

`AtomicTask` dataclass:

| Field | Type | Description |
|---|---|---|
| `task_id` | `str` | Unique task identifier |
| `description` | `str` | Natural language task description |
| `target_agent` | `str` | Agent class name to execute this task |
| `agent_path` | `str` | Filesystem path to the agent module |
| `dependencies` | `list[str]` | `task_id`s that must complete first |
| `validation_gate` | `str` | Gate identifier to run post-execution |
| `priority` | `int` | Execution priority (lower = higher) |
| `estimated_complexity` | `str` | LOW / MEDIUM / HIGH |
| `status` | `str` | PENDING / RUNNING / DONE / FAILED |

`MissionPlan` dataclass:

| Field | Type | Description |
|---|---|---|
| `mission_id` | `str` | Unique mission identifier |
| `created_at` | `str` | ISO 8601 creation timestamp |
| `prompt` | `str` | Original mission prompt |
| `tasks` | `list[AtomicTask]` | Full task list |
| `execution_order` | `list[str]` | Topologically sorted `task_id` list |
| `validation_summary` | `dict[str, Any]` | Per-task gate results |

`DecompositionOrchestrator` fields:
- `_layer: str` — always `"L3"`
- `_agent_registry: dict[str, Any]` — available agent manifest
- `_capability_index: dict[str, list[str]]` — capability → agent name mapping for JIT selection

---

## L3 — Orchestrator (Mission Runner)

**File:** `agentic_core/L3_orchestration/engines/orchestrator_engine.py`

`Orchestrator(SovereignBaseAgent)` is the L3 dispatcher that resolves agent modules at call time.

| Method | Description |
|---|---|
| `dispatch(task)` | Routes an `AtomicTask` to the correct strategy |
| `run_mission(plan)` | Executes a full `MissionPlan` in dependency order |
| `run_agent(agent_name, context)` | JIT-loads and invokes a named agent |
| `_validate_agent_import(agent_name)` | Pre-flight import validation (AST-safe) |
| `_run_compliance_mode(task)` | Compliance-focused execution mode |
| `_run_healing_mode(task)` | Healing-focused execution mode |
| `_run_ssot_mode(task)` | SSOT validation mode |
| `_run_full_mode(task)` | Full agent mode (default) |
| `get_available_agents()` | Returns registered agent manifest |
| `validate_mission(plan)` | Pre-flight mission validation |
| `_v15_build_operation_manifest()` | Builds v1.5 operation manifest for evidence |
| `heal_repository(context)` / `heal(context)` | Healing entry points |

`L3OrchestrationStrategy(OrchestrationStrategy)`:
- `execute(task, agents)` — strategy-level execution
- `get_available_agents()` — returns agent capability map

`OrchestratorMode(str, Enum)` — `COMPLIANCE`, `HEALING`, `SSOT`, `FULL`.

---

## L3 — DAG Manager

**File:** `agentic_core/L3_orchestration/engines/dag_manager.py`

`DAGManager(HealerMixin, MCPHardenedMixin, L3SubatomicTestingMixin, RedisCacheMixin, PineconeVectorMixin)` — manages the directed acyclic graph of task dependencies, enabling parallel execution of non-dependent tasks.

| Method | Description |
|---|---|
| `register_function(fn)` | Registers a callable as a DAG node |
| `add_node(node_id, fn, deps)` | Adds a node with explicit dependencies |
| `request_mutation(node_id, change)` | Requests a structural change to the DAG |
| `create_mutation_request(node_id, change)` | Creates a typed mutation request artifact |
| `get_next_node()` | Returns the next node ready for execution |
| `pause_node(node_id)` / `resume_node(node_id)` | Execution suspension |
| `get_graph_stats()` | Returns node counts, edge counts, parallelism factor |
| `visualize_graph()` | Returns DOT-format string representation |
| `heal_repository(context)` | Self-healing for DAG integrity |

---

## L3 — Autonomous Execution Engine

**File:** `agentic_core/L3_orchestration/engines/autonomous_execution_engine.py`

`autonomous_execution_engine` — persistent, self-waking execution loop.

| Method | Description |
|---|---|
| `awaken()` | Starts the eternal execution cycle |
| `load_state()` / `save_state()` | Persists execution cursor to disk |
| `execute_validation_mission()` | Runs one validation mission cycle |
| `eternal_execution_cycle()` | Async infinite loop with circuit breaker |
| `get_execution_status()` | Returns current cycle state |
| `reset_circuit_breaker()` | Clears the circuit breaker on manual recovery |

---

## L2 — Action Node

**File:** `agentic_core/L2_execution/engines/action_node.py`

`ActionNode` — JIT tool selector and executor at the L2 boundary.

| Method | Description |
|---|---|
| `act(intent, context)` | Sync execution entry point |
| `act_async(intent, context)` | Async execution entry point |
| `act_simple(intent)` | Fast path for low-complexity intents |
| `_select_tools(intent)` | JIT tool selection via `tool_registry.find_tools_for_task` |
| `_execute_tools(tools, context)` | Executes selected tools with budget enforcement |
| `_format_output(results)` | Normalizes tool outputs |
| `get_statistics()` | Returns per-intent success/latency stats |

`ActionNodeCore` (`action_node_core.py`) provides the minimal execute loop used by non-LLM action paths:
- `execute_plan(steps)` — executes a pre-built step list
- `_execute_single_step(step)` — single-step execution with error isolation

---

## L2 — Tool Intent Executor

**File:** `agentic_core/L2_execution/engines/tool_intent_executor.py`

`ToolIntentExecutor` — context manager wrapping a single tool invocation with full audit trail.

- `__enter__` / `__exit__` — budget accounting and envelope sealing
- `execute(tool_name, args)` — invokes the tool and returns `ToolResult`

`ToolResult` dataclass:

| Field | Type | Description |
|---|---|---|
| `schema_version` | `int` | Result schema version |
| `tool_name` | `str` | Tool that was invoked |
| `args_hash` | `str` | SHA-256 of args dict |
| `success` | `bool` | Execution outcome |
| `output_summary` | `str` | Truncated output for logging |
| `anchor_ids` | `list[str]` | Retrieval anchors referenced during execution |
| `result_hash` | `str` | SHA-256 of full result payload |

---

## L2 — Tool Registry

**File:** `agentic_core/L2_execution/engines/tool_registry.py`

`tool_registry` — the JIT tool resolution authority. Tools are discovered at startup and matched to intents via embedding similarity.

| Method | Description |
|---|---|
| `register(fn, tags, category)` | Registers a callable with metadata |
| `find_tools_for_task(intent, top_k)` | Embedding-based JIT tool selection |
| `_ensure_embeddings()` | Lazy embedding computation for all registered tools |
| `_generate_match_reason(tool, intent)` | Human-readable match rationale |
| `get_tool_recommendations(intent, k)` | Returns `ToolMatch` list with scores |
| `get_tool(name)` | Direct lookup by name |
| `list_tools()` | Returns all `ToolDefinition` objects |
| `update_tool_stats(name, success)` | Updates usage count and success rate |
| `get_stats()` | Registry-level statistics |

`ToolDefinition` dataclass fields: `name`, `description`, `function`, `parameters`, `tags`, `category`, `embedding`, `usage_count`, `success_rate`.

`ToolMatch` dataclass: `tool: ToolDefinition`, `relevance_score: float`, `reason: str`.

---

## L1 — Cognitive Engine (JIT Memory Prefetch)

**File:** `agentic_core/L1_cognition/engines/cognitive_engine.py`

`CognitiveNodeRefactored` implements lazy, non-blocking semantic memory prefetch for JIT context assembly.

- `_is_simple_intent(input)` — fast-path detection that skips expensive memory retrieval
- `_lazy_memory_prefetch(query)` — fires a background `asyncio.Task` to warm semantic memory without blocking the main execution path
- `_make_cache_key(input)` — deterministic key for `CompiledPromptCache` / `TemplateRenderCache`

---

## L1 — Prompt Artifact Cache

**File:** `agentic_core/L1_cognition/engines/prompt_artifact_cache.py`

Two independent caches support JIT prompt assembly without redundant compilation:

- `CompiledPromptCache` — caches fully assembled, governance-governed prompts by key hash
- `TemplateRenderCache` — caches template renders before governance wrapping

Both expose `get(key)`, `set(key, value)`, `invalidate(key)`.

---

## L3 — Context Curator (JIT Window Management)

**File:** `agentic_core/L3_orchestration/engines/context_curator_engine.py`

`ContextCurator(SovereignBaseAgent)` manages the bounded context window for each in-flight task. Eviction is driven by relevance scores, not FIFO.

| Method | Description |
|---|---|
| `add_chunk(chunk)` | Adds chunk; calls `_make_space` if over budget |
| `pin_chunk(chunk_id)` | Eviction-immune marking |
| `update_relevance(chunk_id, score)` | Dynamic relevance update |
| `prune_by_relevance(threshold)` | Batch evict below threshold |
| `get_context_window()` | Current non-evicted chunks |
| `get_formatted_context()` | LLM-ready string (respects token budget) |
| `_calculate_total_tokens()` | Token budget accounting |
| `_make_space(needed_tokens)` | Eviction strategy: evict lowest-relevance unpinned chunks |

---

## L2 — Sovereign LLM Gateway (Provider Health Check)

**File:** `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`

`SovereignLLMGateway` is the L2 LLM invocation gateway. It consolidates provider selection, retry, and health monitoring for the JIT execution path.

`ProviderHealthState` (frozen dataclass):

| Field | Type | Description |
|---|---|---|
| `provider` | `Literal["openai","anthropic","google"]` | Provider identifier |
| `is_healthy` | `bool` | Current health status |
| `error_rate` | `float` | Recent 0.0–1.0 error rate |
| `last_check` | `int` | Unix timestamp of last check |
| `degraded_until` | `int` | Timestamp until degraded mode ends |
| `consecutive_failures` | `int` | Streak counter |

- `is_degraded(current_time)` — checks if provider is currently in degraded mode
- `should_degrade(error_threshold, failure_threshold)` — degradation decision

`SovereigntyViolation` — raised when an agent's `ExecutionMode` does not permit LLM calls (e.g., DETERMINISTIC agents that bypass the healing tier router).

Supported providers: `openai` (GPT-4, GPT-4o, o1), `anthropic` (Claude 3.5), `google` (Gemini). All audit entries are written to `HashChainAuditLog` with FIFO rotation.

---

## Sandbox Envelope — JIT Budget Enforcement

**File:** `agentic_core/L2_execution/types/sandbox_envelope_types.py`

Every JIT tool invocation is wrapped in a `SandboxEnvelope` that declares and enforces its budget before execution begins.

`SandboxEnvelope` dataclass:

| Field | Type | Description |
|---|---|---|
| `envelope_id` | `str` | Unique envelope identifier |
| `tool_name` | `str` | Tool being invoked |
| `tool_args` | `dict[str, Any]` | Tool arguments |
| `instruction_packet_id` | `str` | Parent instruction packet |
| `invocation_metadata` | `dict[str, Any]` | Execution context metadata |
| `budget` | `ToolBudget` | Max calls, tokens, time |
| `signature` | `str` | L5 signature over envelope contents |

`ToolBudget.__post_init__` validates all budget fields are non-negative at construction time. Exceeding any budget dimension raises `WriteSetViolation`.
