# Healing Invocation Activation Strategy

## Current State: 24.9% Healing Invocation (Dormant)

### Problem: Insurance Policy Without Claims
Having self-healing capability means nothing if it's never invoked:
- **Capability exists** but is dormant
- **Healing methods defined** but not called
- **Self-repair logic** sits unused
- **System vulnerabilities** persist unfixed

### Insurance Analogy
Like having comprehensive insurance but never filing claims:
- Policy covers everything (capability: 100%)
- But claims filed rarely (invocation: 24.9%)
- Result: Damage goes unrepaired despite coverage

### Solution: Activate Healing Invocation
Add `super().heal_repository()` calls to trigger self-healing chain across all agent layers.

---

## Healing Invocation Architecture

### HealerMixin Base Class
```python
class HealerMixin:
    """Base healing capability for all agents."""
    
    def heal(self, violation: Dict[str, Any]) -> bool:
        """Autonomous repair with rollback verification."""
        # Diagnose issue
        # Apply fix
        # Verify rollback
        # Return success status
    
    async def heal_async(self, violation: Dict[str, Any]) -> bool:
        """Non-blocking heal for orchestrators."""
        return await asyncio.to_thread(self.heal, violation)
    
    def heal_repository(self, dry_run: bool = True, execute: bool = False, 
                       depth: int = 0, max_depth: int = 3) -> Dict[str, int]:
        """Repository-wide healing invocation."""
        # Scan for violations
        # Invoke healing for each
        # Return metrics
```

### Healing Invocation Chain
```
Agent.heal_repository()
  ↓
super().heal_repository()  ← MISSING IN 75% OF AGENTS
  ↓
HealerMixin.heal_repository()
  ↓
Invoke healing for violations
  ↓
Track metrics and results
```

---

## Agents Lacking super().heal_repository() Calls

### Identified Patterns

**Pattern 1: Methods with "CRITICAL FIRST" comment but no super() call**
- NamingLawHealerAgent.heal_repository()
- GlobalComplianceAggregatorAgent.heal_repository()
- DriftDetectorAgent.heal_repository()
- DeadCodeDetectorAgent.heal_repository()

**Pattern 2: Methods that initialize _call_path but don't invoke parent**
- FileManagerAgent.heal_repository()
- CheckpointManagerAgent.heal_repository()
- CognitiveContractManagerAgent.heal_repository()
- PromptGovernorAgent.heal_repository()

**Pattern 3: Methods with "invoke shared healing chain" comment but no call**
- TelemetryAgent.heal_repository()
- TracingAgent.heal_repository()
- CoordinateObservabilityOperationsAgent.heal_repository()

---

## Healing Invocation Fix Pattern

### Before: Dormant Healing
```python
@timeout(300)
def heal_repository(self, dry_run: bool = True, execute: bool = False, 
                   depth: int = 0, max_depth: int = 3, 
                   _call_path: Optional[set] = None) -> Dict[str, int]:
    """Agent healing - operational only."""
    if _call_path is None:
        _call_path = set()
    
    agent_name = self.__class__.__name__
    if agent_name in _call_path:
        return {"skipped": 1}
    
    _call_path.add(agent_name)
    try:
        # Agent-specific healing logic here
        return {"healed": 0}
    finally:
        _call_path.discard(agent_name)
```

### After: Active Healing with super() Invocation
```python
@timeout(300)
def heal_repository(self, dry_run: bool = True, execute: bool = False, 
                   depth: int = 0, max_depth: int = 3, 
                   _call_path: Optional[set] = None) -> Dict[str, int]:
    """Agent healing - invoke shared healing chain."""
    if _call_path is None:
        _call_path = set()
    
    agent_name = self.__class__.__name__
    if agent_name in _call_path:
        return {"skipped": 1}
    
    _call_path.add(agent_name)
    try:
        # CRITICAL FIRST: Invoke parent healing chain
        parent_result = super().heal_repository(
            dry_run=dry_run,
            execute=execute,
            depth=depth,
            max_depth=max_depth,
            _call_path=_call_path
        )
        
        # Agent-specific healing logic here
        agent_result = {"healed": 0}
        
        # Merge results
        return {
            **parent_result,
            **agent_result,
            "total": parent_result.get("total", 0) + agent_result.get("healed", 0)
        }
    finally:
        _call_path.discard(agent_name)
```

---

## Implementation Strategy

### Phase 1: Core Infrastructure (Week 1)
**Priority**: P0 - System-critical agents

Agents to fix:
1. NamingAgent.heal_repository()
2. NamingLawHealerAgent.heal_repository()
3. NamingNormalizationAgent.heal_repository()
4. GlobalComplianceAggregatorAgent.heal_repository()
5. DriftDetectorAgent.heal_repository()

**Action**: Add `super().heal_repository()` call as first action

### Phase 2: Utility & Runtime Agents (Week 2)
**Priority**: P1 - Support infrastructure

Agents to fix:
1. FileManagerAgent.heal_repository()
2. DeadCodeDetectorAgent.heal_repository()
3. CheckpointManagerAgent.heal_repository()
4. CognitiveContractManagerAgent.heal_repository()
5. PromptGovernorAgent.heal_repository()

### Phase 3: Observability Agents (Week 3)
**Priority**: P2 - Monitoring and telemetry

Agents to fix:
1. TelemetryAgent.heal_repository()
2. TracingAgent.heal_repository()
3. CoordinateObservabilityOperationsAgent.heal_repository()
4. All other observability agents

### Phase 4: Layer-Specific Agents (Week 4)
**Priority**: P3 - Layer orchestration

Agents to fix:
1. All L1 Cognition healing methods
2. All L2 Execution healing methods
3. All L3 Orchestration healing methods
4. All L4 State healing methods
5. All L5 Safety healing methods

### Phase 5: Validation & Testing (Week 5)
**Priority**: Verification

Actions:
1. Audit all heal_repository() methods
2. Verify super() calls are present
3. Test healing invocation chain
4. Measure healing metrics
5. Validate invocation percentage increase

---

## Expected Improvements

### Current State (24.9% Invocation)
- Healing capability exists but dormant
- 75% of agents don't invoke parent healing
- Violations go unrepaired
- System vulnerabilities persist

### Target State (85-90% Invocation)
- Active healing across all layers
- Healing chain properly invoked
- Violations detected and repaired
- System self-heals automatically

### Metrics

| Metric | Current | Target | Method |
|--------|---------|--------|--------|
| Healing Invocation | 24.9% | 85-90% | Agent audit |
| Agents with super() | ~25% | 100% | Code review |
| Healing Chain Active | Partial | Complete | Integration test |
| Violations Repaired | Low | High | Metrics tracking |
| System Stability | Degraded | Improved | Uptime monitoring |

---

## Healing Invocation Checklist

### Phase 1: Core Infrastructure
- [ ] NamingAgent - Add super().heal_repository()
- [ ] NamingLawHealerAgent - Add super().heal_repository()
- [ ] NamingNormalizationAgent - Add super().heal_repository()
- [ ] GlobalComplianceAggregatorAgent - Add super().heal_repository()
- [ ] DriftDetectorAgent - Add super().heal_repository()
- [ ] Test Phase 1 agents

### Phase 2: Utility & Runtime
- [ ] FileManagerAgent - Add super().heal_repository()
- [ ] DeadCodeDetectorAgent - Add super().heal_repository()
- [ ] CheckpointManagerAgent - Add super().heal_repository()
- [ ] CognitiveContractManagerAgent - Add super().heal_repository()
- [ ] PromptGovernorAgent - Add super().heal_repository()
- [ ] Test Phase 2 agents

### Phase 3: Observability
- [ ] TelemetryAgent - Add super().heal_repository()
- [ ] TracingAgent - Add super().heal_repository()
- [ ] CoordinateObservabilityOperationsAgent - Add super().heal_repository()
- [ ] All other observability agents
- [ ] Test Phase 3 agents

### Phase 4: Layer-Specific
- [ ] L1 Cognition agents - Add super().heal_repository()
- [ ] L2 Execution agents - Add super().heal_repository()
- [ ] L3 Orchestration agents - Add super().heal_repository()
- [ ] L4 State agents - Add super().heal_repository()
- [ ] L5 Safety agents - Add super().heal_repository()
- [ ] Test Phase 4 agents

### Phase 5: Validation
- [ ] Audit all heal_repository() methods
- [ ] Verify super() calls present
- [ ] Test healing invocation chain
- [ ] Measure healing metrics
- [ ] Validate invocation percentage

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Healing Invocation | 85-90% |
| Agents with super() | 100% |
| Healing Chain Active | Complete |
| Violations Repaired | >80% |
| System Stability | Improved |

---

## Why This Matters

### Insurance Claim Analogy
- **Having insurance** = Having healing capability (100%)
- **Filing claims** = Invoking healing methods (24.9%)
- **Getting repairs** = Violations fixed (low)

**Current problem**: Insurance exists but claims never filed
**Solution**: File claims (invoke healing) to get repairs

### System Impact
- **Without invocation**: Violations accumulate, system degrades
- **With invocation**: Violations detected and fixed, system self-heals
- **Result**: Improved stability, reduced manual intervention

---

## Next Steps

1. **Audit**: Identify all heal_repository() methods lacking super() calls
2. **Prioritize**: Focus on critical infrastructure first
3. **Implement**: Add super().heal_repository() calls systematically
4. **Test**: Verify healing chain activation
5. **Monitor**: Track healing metrics and system stability
