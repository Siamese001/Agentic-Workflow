# Autonomy Gap Analysis: apps_lic & apps_rg vs Canon Validator

**Generated:** 2025-01-XX
**Baseline:** `scripts/canon_validator_agentic.py` (8864 lines)
**Targets:** `apps_lic/` (43 files) and `apps_rg/` (46 files)

---

## Executive Summary

| Capability | Canon Validator | apps_rg | apps_lic | Gap Severity |
|------------|-----------------|---------|----------|--------------|
| Convergence Loop | ✅ 10-cycle max | ⚠️ Single-pass | ⚠️ Single-pass | **CRITICAL** |
| Signal System | ✅ Full blackboard | ❌ None | ❌ None | **CRITICAL** |
| Human-in-the-Loop | ✅ FastAPI server | ❌ None | ❌ None | **HIGH** |
| Reflection/Self-Critique | ✅ ReflectionAgent | ❌ None | ❌ None | **HIGH** |
| Memory/Embeddings | ✅ Pinecone + traces | ⚠️ Partial | ⚠️ Partial | **MEDIUM** |
| Blast Radius | ✅ Dependency graph | ❌ None | ❌ None | **HIGH** |
| Rollback | ✅ GitAgent | ⚠️ Checkpoint only | ❌ None | **HIGH** |
| Few-Shot Injection | ✅ 5+ patterns | ❌ None | ❌ None | **MEDIUM** |
| Two-Pass Validation | ✅ Regex + AST | ⚠️ Single-pass | ⚠️ Single-pass | **MEDIUM** |
| Observability | ✅ Full audit trail | ⚠️ Logging only | ⚠️ Logging only | **LOW** |

**Overall Autonomy Score:**
- Canon Validator: **L5+ (Full Autonomy)**
- apps_rg: **L2-L3 (Execution with Checkpointing)**
- apps_lic: **L2 (Basic Execution)**

---

## Detailed Gap Analysis

### 1. Convergence Loop (CRITICAL)

**Canon Validator Pattern:**
```python
max_cycles = 10
for cycle in range(max_cycles):
    ctx.modified_files.clear()
    ctx.signals.clear()
    converged = await self._execute_all_phases()
    if converged:
        break
    if "CRITICAL_FAIL" in ctx.signals:
        break
```

**apps_rg Current State:**
- `HardenedWorkflowOrchestrator`: Single-pass execution with checkpointing
- `RecursivePlannerAgent`: Max depth limit (3) but no convergence loop
- No iterative self-healing capability

**apps_lic Current State:**
- No orchestrator with convergence loop
- Single-pass message generation

**Gap:** Neither engine can iteratively fix issues until convergence.

**Recommendation:**
```python
# Add to apps_rg/L3_orchestration/hardened_orchestrator.py
async def execute_with_convergence(self, workflow_id, context, max_cycles=5):
    for cycle in range(max_cycles):
        result = await self.execute_workflow_with_resilience(workflow_id, context)
        if result["status"] == "COMPLETED" and not self._has_quality_issues(result):
            break
        # Re-run with adjusted parameters
        context = self._adjust_for_retry(context, result)
    return result
```

---

### 2. Signal System (CRITICAL)

**Canon Validator Pattern:**
```python
ctx.signals = set()  # Blackboard pattern
ctx.signal_critical_failure(message)
ctx.signal_test_failure()
ctx.signal_convergence()

# Agents check signals
if "CRITICAL_FAIL" in ctx.signals:
    break
```

**apps_rg Current State:**
- No signal system
- Errors propagate via exceptions only
- No inter-agent communication

**apps_lic Current State:**
- No signal system
- No blackboard pattern

**Gap:** Agents cannot communicate state changes or trigger other agents.

**Recommendation:**
```python
# Create apps_shared/signal_bus.py
class SignalBus:
    def __init__(self):
        self.signals: Set[str] = set()
        self.listeners: Dict[str, List[Callable]] = {}
    
    def emit(self, signal: str, payload: Any = None):
        self.signals.add(signal)
        for listener in self.listeners.get(signal, []):
            listener(payload)
    
    def has(self, signal: str) -> bool:
        return signal in self.signals
    
    def clear(self):
        self.signals.clear()
```

---

### 3. Human-in-the-Loop (HIGH)

**Canon Validator Pattern:**
```python
if high_risk or (many_modifications and strategic_plan):
    start_intervention_server(ctx)
    await approval_event.wait()
    if "VETOED" in ctx.signals:
        break
```

**apps_rg Current State:**
- No intervention mechanism
- All decisions are automatic

**apps_lic Current State:**
- No intervention mechanism

**Gap:** No ability to pause for human review on high-risk operations.

**Recommendation:**
```python
# Add to apps_rg/L3_orchestration/hardened_orchestrator.py
async def _check_intervention_required(self, context: Dict) -> bool:
    high_risk_indicators = [
        context.get("quality_score", 1.0) < 0.7,
        len(context.get("validation_failures", [])) > 3,
        context.get("contains_pii", False),
    ]
    if any(high_risk_indicators):
        # Emit signal and wait for approval
        self.signal_bus.emit("NEEDS_HUMAN_REVIEW", context)
        return await self._wait_for_approval()
    return True
```

---

### 4. Reflection/Self-Critique (HIGH)

**Canon Validator Pattern:**
```python
class ReflectionAgent(SubAtomicAgent):
    async def execute(self):
        reflection_prompt = f"""
        Ask:
        1. Did modifications reduce signals?
        2. Did any new signals appear?
        3. What strategy failed/succeeded?
        """
        advice = await ctx.resilient_mutation(self.name, reflection_prompt)
        if "escalat" in advice.lower():
            ctx.signals.add("NEEDS_HUMAN_REVIEW")
```

**apps_rg Current State:**
- `QualityCritic` role exists but no self-reflection
- No learning from failures

**apps_lic Current State:**
- No reflection mechanism

**Gap:** Engines don't learn from their own execution patterns.

**Recommendation:**
```python
# Create apps_shared/reflection_agent.py
class ReflectionAgent:
    async def reflect_on_execution(self, execution_log: List[Dict]) -> Dict:
        prompt = f"""
        Analyze this execution:
        {json.dumps(execution_log[-5:])}
        
        Questions:
        1. Did quality improve across iterations?
        2. What patterns led to failures?
        3. Recommend: CONTINUE | ADJUST_STRATEGY | ESCALATE
        """
        return await self.llm.generate(prompt)
```

---

### 5. Blast Radius Analysis (HIGH)

**Canon Validator Pattern:**
```python
if ctx.modified_files:
    all_impacted = set()
    for f in ctx.modified_files:
        deps = ctx.code_graph.get_impact_radius(f)
        all_impacted.update(deps)
    ctx.impact_zone = all_impacted
```

**apps_rg Current State:**
- No dependency tracking between resume sections
- Changes to one section don't trigger re-validation of dependent sections

**apps_lic Current State:**
- No dependency tracking between message components

**Gap:** Changes don't propagate to dependent components.

**Recommendation:**
```python
# Add to apps_rg/L3_orchestration/hardened_orchestrator.py
def _calculate_blast_radius(self, modified_sections: Set[str]) -> Set[str]:
    dependency_map = {
        "executive_summary": {"headline", "skills"},
        "experience_bullets": {"executive_summary", "skills"},
        "skills": {"experience_bullets"},
    }
    impacted = set(modified_sections)
    for section in modified_sections:
        impacted.update(dependency_map.get(section, set()))
    return impacted
```

---

### 6. Rollback Capability (HIGH)

**Canon Validator Pattern:**
```python
class GitAgent(SubAtomicAgent):
    async def execute(self):
        if "CRITICAL_FAILURE" in ctx.signals:
            repo.git.reset('--hard', 'HEAD')
            ctx.signals.discard("CRITICAL_FAILURE")
```

**apps_rg Current State:**
- `AtomicStateManager` provides checkpointing
- Can resume from checkpoint but no rollback to previous good state

**apps_lic Current State:**
- No rollback capability

**Gap:** Cannot revert to last known good state on failure.

**Recommendation:**
```python
# Enhance apps_rg/L3_orchestration/hardened_orchestrator.py
async def execute_with_rollback(self, workflow_id, context):
    # Save pre-execution state
    pre_state = self.state_manager.snapshot(workflow_id)
    
    try:
        result = await self.execute_workflow_with_resilience(workflow_id, context)
        if result["status"] == "FAILED":
            # Rollback to pre-execution state
            self.state_manager.restore(workflow_id, pre_state)
            self.signal_bus.emit("ROLLBACK_EXECUTED")
        return result
    except Exception as e:
        self.state_manager.restore(workflow_id, pre_state)
        raise
```

---

### 7. Few-Shot Injection (MEDIUM)

**Canon Validator Pattern:**
```python
ctx.FEW_SHOT_SHERLOCK = """
Example 1: ImportError in test_utils.py
Root cause: Missing __init__.py in parent directory
Fix: Added __init__.py with proper exports
...
"""
prompt = f"{ctx.FEW_SHOT_SHERLOCK}\n{actual_task}"
```

**apps_rg Current State:**
- Static prompts without few-shot examples
- No dynamic example injection

**apps_lic Current State:**
- Static prompts without few-shot examples

**Gap:** LLM prompts lack contextual examples for better performance.

**Recommendation:**
```python
# Create apps_shared/few_shot_library.py
FEW_SHOT_RESUME_BULLETS = """
Example 1: Weak bullet
Input: "Managed team"
Output: "Led cross-functional team of 12 engineers, delivering $2.3M project 15% under budget"

Example 2: Missing metrics
Input: "Improved sales"
Output: "Increased quarterly sales by 34% ($1.2M) through strategic account management"
"""

# Usage in prompts
prompt = f"{FEW_SHOT_RESUME_BULLETS}\n\nNow improve this bullet: {user_bullet}"
```

---

### 8. Two-Pass Validation (MEDIUM)

**Canon Validator Pattern:**
```python
# Pass 1: Fast regex
detected_risks = self._detect_risks(content)  # Regex patterns

# Pass 2: AST context
if detected_risks:
    risk_context = self._analyze_risk_context(content, detected_risks)  # AST analysis
```

**apps_rg Current State:**
- `IntegrityGateExecutor` does single-pass validation
- No fast pre-filter before expensive checks

**apps_lic Current State:**
- Single-pass validation

**Gap:** All validations run at full cost, no fast-fail optimization.

**Recommendation:**
```python
# Enhance apps_rg/L2_execution/integrity_gate_executor.py
def execute_gates_optimized(self, content: str) -> List[ValidationResult]:
    # Pass 1: Fast regex checks
    fast_failures = self._run_fast_checks(content)
    if fast_failures:
        return fast_failures  # Fail fast
    
    # Pass 2: Expensive LLM-based checks
    return self._run_deep_checks(content)
```

---

## Implementation Priority

### Phase 1: Critical Gaps (Week 1-2)
1. **Signal System** - Create `apps_shared/signal_bus.py`
2. **Convergence Loop** - Add to `HardenedWorkflowOrchestrator`

### Phase 2: High Gaps (Week 3-4)
3. **Reflection Agent** - Create `apps_shared/reflection_agent.py`
4. **Human-in-the-Loop** - Add intervention server
5. **Rollback** - Enhance state manager
6. **Blast Radius** - Add dependency tracking

### Phase 3: Medium Gaps (Week 5-6)
7. **Few-Shot Library** - Create `apps_shared/few_shot_library.py`
8. **Two-Pass Validation** - Optimize gate executor
9. **Observability** - Add audit trail generation

---

## Files to Create/Modify

### New Files
- `apps_shared/signal_bus.py` - Signal/blackboard system
- `apps_shared/reflection_agent.py` - Self-critique agent
- `apps_shared/few_shot_library.py` - Few-shot examples
- `apps_shared/intervention_server.py` - Human-in-the-loop server

### Modified Files
- `apps_rg/L3_orchestration/hardened_orchestrator.py` - Add convergence loop, rollback
- `apps_rg/L2_execution/integrity_gate_executor.py` - Two-pass validation
- `apps_lic/L3_orchestration/` - Add orchestrator with convergence

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Autonomy Level | L2-L3 | L4-L5 |
| Self-Healing Cycles | 0 | 5 max |
| Signal Types | 0 | 10+ |
| Rollback Capability | Partial | Full |
| Human Intervention Points | 0 | 3+ |
| Few-Shot Patterns | 0 | 5+ |
