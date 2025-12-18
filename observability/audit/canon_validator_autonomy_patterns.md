# Canon Validator Autonomy Patterns - Baseline Reference

**Generated:** 2025-01-XX
**Source:** `scripts/canon_validator_agentic.py` (8864 lines)

---

## Executive Summary

The Canon Validator implements a **Level 5+ Autonomous Self-Healing System** with the following core capabilities:
- Multi-phase orchestration with convergence loops
- Human-in-the-loop intervention gates
- Self-critique and reflection
- Dynamic tool creation (ToolsmithAgent)
- Semantic memory with embeddings
- Git-based checkpointing and rollback

---

## 1. Orchestration Architecture

### SwarmScheduler (Central Orchestrator)
```
Location: Lines 4900-5190
Role: Manages 10 execution phases with convergence detection
```

**10 Named Phases:**
| Phase | Name | Execution Mode | Purpose |
|-------|------|----------------|---------|
| 1 | integrity_seq | Sequential (Hard Gate) | AST validation, syntax checks |
| 2 | curation_seq | Sequential | Import cleanup, hygiene |
| 3 | test_seq | Sequential + Scheduler | pytest, property-based testing |
| 4 | memory_parallel | Parallel | Historian, embeddings |
| 5 | resilience_parallel | Parallel | Concurrency, safety |
| 6 | resource_safety_parallel | Parallel | Memory leaks, deadlocks |
| 7 | engineering_parallel | Parallel | Structure, patterns |
| 8 | refinement_parallel | Parallel | Naming, docs, types |
| 9 | benchmarking_seq | Sequential | Performance regression |
| 10 | optimization_conditional | Conditional | Only if converged |

**Convergence Loop:**
```python
max_cycles = 10
for cycle in range(max_cycles):
    # Reset cycle state
    ctx.modified_files.clear()
    ctx.signals.clear()
    
    # Execute all phases
    converged = await self._execute_all_phases()
    
    # Human-in-the-loop check
    if await self._check_intervention_required():
        if "VETOED" in ctx.signals:
            break
    
    # Convergence check
    if converged:
        break
    
    # Critical failure check
    if "CRITICAL_FAIL" in ctx.signals:
        break
```

---

## 2. Signal-Based Communication (Blackboard Pattern)

### Signal Types
| Signal | Meaning | Triggered By |
|--------|---------|--------------|
| `CRITICAL_FAIL` | Abort mission | Integrity agents |
| `TEST_FAILURE` | Tests failed | TestPilot |
| `HIGH_RISK` | Needs human approval | Multiple agents |
| `VETOED` | Human rejected | Intervention server |
| `SECURE_REBOOT` | Critical secrets found | SecurityEnforcer |
| `PERFORMANCE_REGRESSION` | Benchmarks degraded | BenchmarkingAgent |
| `NEEDS_HUMAN_REVIEW` | Escalation needed | ReflectionAgent |

### Context Signals API
```python
ctx.signal_critical_failure(message)
ctx.signal_ast_valid()
ctx.signal_deps_valid()
ctx.signal_secure()
ctx.signal_healing_cycle(cycle_num)
ctx.signal_llm_failure(error)
ctx.signal_convergence()
```

---

## 3. Human-in-the-Loop (L5)

### Intervention Triggers
```python
high_risk = "HIGH_RISK" in ctx.signals
many_modifications = len(ctx.modified_files) > 3
strategic_plan = getattr(ctx, 'strategic_plan', None)

if high_risk or (many_modifications and strategic_plan):
    # Start intervention server
    start_intervention_server(ctx)
    # Wait for human approval
    await approval_event.wait()
```

### Telepathy Interface
```python
# Dynamic instruction loading from file
instruction_file = Path("observability/human_instructions.md")
if instruction_file.exists():
    instructions = instruction_file.read_text().strip()
    if "stop" in instructions.lower():
        sys.exit(0)
    if "test" in instructions.lower():
        ctx.signals.add("TEST_FAILURE")
```

---

## 4. Reflection & Self-Critique

### ReflectionAgent (Lines 7001-7071)
```python
reflection_prompt = f"""
<self_critique_guidance>
You are reflecting on healing cycle {cycle}.
Ask:
1. Did modifications reduce signals? (Goal: zero)
2. Did any new signals appear? → regression?
3. Are files still subatomic and at correct depth?
4. What strategy failed/succeeded?
5. What should change next cycle?
</self_critique_guidance>

Respond with one keyword only:
CONVERGE_AND_COMMIT | MARK_FLAPPING_SKIP_FILE | 
ROLLBACK_LAST_CHANGE_AND_RETRY | ESCALATE_TO_HUMAN_WITH_REPORT
"""
```

### Memory Consolidation
```python
for trace in ctx.successful_traces:
    await ctx.upsert_embedding(
        key=f"trace_{hash(trace['task'])}",
        text=trace['task'] + "\n" + trace['code_before'],
        metadata=trace
    )
ctx.successful_traces.clear()  # Reset short-term memory
```

---

## 5. Strategic Planning

### StrategicPlanner (Lines 6913-6999)
- **Dependency Graph Analysis**: Calculates blast radius for modified files
- **Signal-Based Agenda**: Maps signals to appropriate agents
- **Plan Generation**: Uses LLM with few-shot examples

```python
# Blast Radius Calculation
if ctx.modified_files:
    all_impacted = set()
    for f in ctx.modified_files:
        deps = ctx.code_graph.get_impact_radius(f)
        all_impacted.update(deps)
    ctx.impact_zone = all_impacted
```

---

## 6. LLM Integration Patterns

### Mutation Request API
```python
# Single-file mutation
await ctx.request_mutation(
    agent_name, 
    prompt, 
    content, 
    reasoning_mode=True
)

# Multi-turn collective repair
await ctx.conversational_repair(
    structured_traceback,
    primary_file=primary,
    dependent_files=list(files_content.keys())
)

# Resilient mutation with retry
await ctx.resilient_mutation(
    agent_name, 
    prompt, 
    max_attempts=2
)
```

### Few-Shot Injection Patterns
```python
ctx.FEW_SHOT_SHERLOCK      # Root cause analysis examples
ctx.FEW_SHOT_GITOPS        # Branch/commit naming examples
ctx.FEW_SHOT_STRATEGIC     # Strategic planning examples
ctx.FEW_SHOT_REFLECTION_STRATEGY  # Self-critique examples
ctx.FEW_SHOT_GLOBAL_REFACTOR      # Cross-file refactoring
```

---

## 7. Specialized Agent Patterns

### TestPilot (Testing + Auto-Repair)
- Auto-install missing dependencies via pip
- Trigger Sherlock on test failures
- Property-based testing with Hypothesis
- Collective repair for complex failures

### Sherlock (Root Cause Analysis)
- Cross-file dependency tracing
- Structured traceback analysis
- Collective intelligence repair

### ToolsmithAgent (Dynamic Agency)
- Creates diagnostic scripts when standard fixes fail
- Forges Python tools using LLM
- Outputs findings in JSON format

### GitAgent (Version Control)
- Auto-commit to healing branches
- Remote push capability
- Intelligent branch/commit naming via LLM
- Rollback on critical failure

### TheCartographer (Semantic Mapping)
- Generates embeddings for changed files
- Maintains Pinecone index for semantic retrieval
- Generates summaries for file metadata

---

## 8. Watchman (L5 Daemon Mode)

### File System Monitoring
```python
class WatchmanHandler:
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.py'):
            return
        # Debounce and trigger surgical mission
        task = asyncio.run_coroutine_threadsafe(
            self._debounced_trigger(file_path), 
            self.loop
        )
    
    async def trigger_mission(self, file_path: str):
        scheduler = SwarmScheduler()
        await scheduler.run_mission(target_scope=file_path)
```

---

## 9. Safety & Compliance Patterns

### Two-Pass Scanning
1. **Fast Regex Pass**: Quick pattern detection
2. **AST Context Pass**: Semantic analysis for false positive reduction

### Severity Prioritization
```python
prioritized = {
    'critical': [],  # Auto-fix immediately
    'high': [],      # Auto-fix with caution
    'medium': []     # Log for review
}
```

### Compliance Governor
```python
ctx.write_compliant_file(file_path, content)
# Validates against:
# - Max depth rules
# - Atomicity constraints
# - Zero-loss merge policy
```

---

## 10. Key Autonomy Metrics

| Metric | Value | Purpose |
|--------|-------|---------|
| Max Cycles | 10 | Convergence loop limit |
| Debounce Delay | 1.0s | Watchman trigger delay |
| High-Risk Threshold | >3 files | Human intervention trigger |
| Regression Threshold | 10% | Performance regression detection |
| Max Recursion Depth | 3 | RecursivePlannerAgent limit |

---

## Gap Analysis Checklist

When comparing apps_lic/apps_rg to Canon Validator, check for:

- [ ] **Convergence Loop**: Does the engine have iterative self-healing?
- [ ] **Signal System**: Are signals emitted and consumed?
- [ ] **Human-in-the-Loop**: Is there an intervention mechanism?
- [ ] **Reflection**: Does the engine self-critique?
- [ ] **Memory**: Are successful patterns stored for recall?
- [ ] **Blast Radius**: Is dependency impact calculated?
- [ ] **Rollback**: Can the engine revert on failure?
- [ ] **Few-Shot Injection**: Are LLM prompts enhanced with examples?
- [ ] **Two-Pass Validation**: Is there fast+deep scanning?
- [ ] **Observability**: Are audit reports generated?
