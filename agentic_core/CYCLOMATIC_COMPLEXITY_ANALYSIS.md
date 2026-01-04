# Cyclomatic Complexity Reduction Strategy

## Current State: CC 39.9 (High Risk)

### Problem: Spaghetti Code
High cyclomatic complexity means:
- **More branches** = more places for bugs to hide
- **Functions with CC>15** are 3x more likely to contain defects
- **Harder to test** - exponential test cases needed
- **Harder to maintain** - difficult to understand control flow
- **Higher bug density** - more edge cases to miss

### Target: CC <25 (Acceptable)

---

## High-CC Functions Identified

### 1. **SovereignRedisClient.execute()** (CC ~8-10)
**File**: `agentic_core/utils/core_extensions/redis.py:84-170`

**Complexity Sources**:
- 7 elif branches for different operations (set, get, delete, exists, keys, expire, ping)
- Nested if/else for client vs fallback logic
- Try/except block

**Refactoring Strategy**:
```python
# BEFORE: Single 87-line method with 7 elif branches
def execute(self, operation: str, **payload) -> Dict[str, Any]:
    if operation == 'set': ...
    elif operation == 'get': ...
    elif operation == 'delete': ...
    # ... 4 more elif branches

# AFTER: Dispatch pattern with helper methods
def execute(self, operation: str, **payload) -> Dict[str, Any]:
    handlers = {
        'set': self._handle_set,
        'get': self._handle_get,
        'delete': self._handle_delete,
        'exists': self._handle_exists,
        'keys': self._handle_keys,
        'expire': self._handle_expire,
        'ping': self._handle_ping,
    }
    handler = handlers.get(operation)
    if not handler:
        return {'success': False, 'error': f'Unsupported: {operation}'}
    return handler(**payload)

def _handle_set(self, key: str, value: str, ttl: Optional[int] = None) -> Dict:
    client = self._get_client()
    if client:
        if ttl:
            client.setex(key, ttl, value)
        else:
            client.set(key, value)
    else:
        self._fallback_set(key, value)
    return {'success': True}
```

**Expected CC Reduction**: 8-10 → 2-3 (70% reduction)

---

### 2. **SovereignGitClient.execute()** (CC ~9-11)
**File**: `agentic_core/utils/core_extensions/git.py:73-144`

**Complexity Sources**:
- 8 elif branches for different git operations
- Nested if/elif for branch actions
- Multiple conditional parameter handling

**Refactoring Strategy**:
```python
# BEFORE: Single 72-line method with 8 elif branches
def execute(self, operation: str, **payload) -> Dict[str, Any]:
    if operation == 'commit': ...
    elif operation == 'push': ...
    elif operation == 'pull': ...
    # ... 5 more elif branches

# AFTER: Dispatch pattern with operation handlers
def execute(self, operation: str, **payload) -> Dict[str, Any]:
    handlers = {
        'commit': self._handle_commit,
        'push': self._handle_push,
        'pull': self._handle_pull,
        'status': self._handle_status,
        'diff': self._handle_diff,
        'log': self._handle_log,
        'checkout': self._handle_checkout,
        'branch': self._handle_branch,
    }
    handler = handlers.get(operation)
    if not handler:
        return {'success': False, 'error': f'Unsupported: {operation}'}
    return handler(**payload)

def _handle_branch(self, action: str = 'list', **payload) -> Dict:
    if action == 'list':
        return self._run_git(['branch', '-a'])
    elif action == 'create':
        name = payload.get('name', '')
        if not name:
            return {'success': False, 'error': 'Branch name required'}
        return self._run_git(['branch', name])
    else:
        return {'success': False, 'error': f'Unknown action: {action}'}
```

**Expected CC Reduction**: 9-11 → 2-3 (75% reduction)

---

### 3. **NamingAgent.heal_naming_violations()** (CC ~12-15)
**File**: `agentic_core/utils/core_extensions/NamingAgent.py:1264-1304`

**Complexity Sources**:
- 6 elif branches for different status types
- Multiple conditional checks
- Complex summary tracking

**Refactoring Strategy**:
```python
# BEFORE: Single method with 6 elif branches
def heal_naming_violations(self, violations, actual_execute=False):
    for file_path, reason in violations:
        if 'AGENT FILE NAMING VIOLATION' not in reason:
            summary['skipped'] += 1
            continue
        
        proposal = self.auto_rename_proposal(file_path, dry_run=not actual_execute)
        status = proposal.get('status', 'unknown')
        
        if status == 'renamed': ...
        elif status == 'proposed': ...
        elif status == 'collision': ...
        # ... 3 more elif branches

# AFTER: Dispatch pattern with status handlers
def heal_naming_violations(self, violations, actual_execute=False):
    summary = self._initialize_summary()
    
    for file_path, reason in violations:
        if not self._is_agent_naming_violation(reason):
            summary['skipped'] += 1
            continue
        
        proposal = self.auto_rename_proposal(file_path, dry_run=not actual_execute)
        self._process_healing_status(proposal, file_path, summary)
    
    self._print_healing_summary(summary)
    return summary

def _process_healing_status(self, proposal: Dict, file_path: Path, summary: Dict) -> None:
    status_handlers = {
        'renamed': self._handle_renamed,
        'proposed': self._handle_proposed,
        'collision': self._handle_collision,
        'multi_agent_needs_split': self._handle_multi_agent,
        'compliant': self._handle_compliant,
    }
    
    status = proposal.get('status', 'unknown')
    handler = status_handlers.get(status, self._handle_error)
    handler(proposal, file_path, summary)
```

**Expected CC Reduction**: 12-15 → 3-4 (70% reduction)

---

### 4. **NamingAgent.determine_placement_confidence()** (CC ~6-8)
**File**: `agentic_core/utils/core_extensions/NamingAgent.py:430-450`

**Complexity Sources**:
- 4 elif branches for confidence levels
- Nested conditional logic
- Multiple calculations

**Refactoring Strategy**:
```python
# BEFORE: Nested if/elif for confidence levels
if confidence >= PLACEMENT_CONFIDENCE["HIGH"]:
    ConfidenceLevel = "HIGH"
elif confidence >= PLACEMENT_CONFIDENCE["MEDIUM"]:
    ConfidenceLevel = "MEDIUM"
elif confidence >= PLACEMENT_CONFIDENCE["LOW"]:
    ConfidenceLevel = "LOW"
else:
    ConfidenceLevel = "REJECT"

# AFTER: Lookup table pattern
def _determine_confidence_level(self, confidence: float) -> str:
    confidence_thresholds = [
        (PLACEMENT_CONFIDENCE["HIGH"], "HIGH"),
        (PLACEMENT_CONFIDENCE["MEDIUM"], "MEDIUM"),
        (PLACEMENT_CONFIDENCE["LOW"], "LOW"),
    ]
    
    for threshold, level in confidence_thresholds:
        if confidence >= threshold:
            return level
    return "REJECT"
```

**Expected CC Reduction**: 6-8 → 1-2 (85% reduction)

---

## Refactoring Patterns

### Pattern 1: Dispatch Pattern (for if/elif chains)
**Use when**: Multiple elif branches with similar structure

```python
# BEFORE: if/elif chain
if operation == 'set':
    result = handle_set()
elif operation == 'get':
    result = handle_get()
elif operation == 'delete':
    result = handle_delete()

# AFTER: Dispatch dictionary
handlers = {
    'set': self._handle_set,
    'get': self._handle_get,
    'delete': self._handle_delete,
}
handler = handlers.get(operation)
result = handler() if handler else error_result()
```

**CC Reduction**: if/elif chain (CC=N) → dispatch (CC=2)

---

### Pattern 2: Lookup Table (for conditional assignments)
**Use when**: Multiple if/elif branches assigning values

```python
# BEFORE: if/elif assignment
if confidence >= HIGH:
    level = "HIGH"
elif confidence >= MEDIUM:
    level = "MEDIUM"
else:
    level = "LOW"

# AFTER: Lookup table
levels = [(HIGH, "HIGH"), (MEDIUM, "MEDIUM")]
level = next((l for t, l in levels if confidence >= t), "LOW")
```

**CC Reduction**: if/elif chain (CC=N) → lookup (CC=1)

---

### Pattern 3: Strategy Pattern (for complex branching)
**Use when**: Multiple branches with different algorithms

```python
# BEFORE: Complex if/elif with different logic
if strategy == 'aggressive':
    # 10 lines of aggressive logic
elif strategy == 'conservative':
    # 10 lines of conservative logic
elif strategy == 'balanced':
    # 10 lines of balanced logic

# AFTER: Strategy classes
strategies = {
    'aggressive': AggressiveStrategy(),
    'conservative': ConservativeStrategy(),
    'balanced': BalancedStrategy(),
}
strategy = strategies[strategy_name]
result = strategy.execute()
```

**CC Reduction**: Complex branching (CC=10+) → strategy dispatch (CC=2)

---

## Implementation Roadmap

### Phase 1: High-Impact Refactoring (Week 1)
**Target**: Reduce CC by 50%

1. **SovereignRedisClient.execute()** → Dispatch pattern
   - Extract 7 operation handlers
   - Expected: CC 8-10 → 2-3

2. **SovereignGitClient.execute()** → Dispatch pattern
   - Extract 8 operation handlers
   - Expected: CC 9-11 → 2-3

3. **NamingAgent.heal_naming_violations()** → Dispatch pattern
   - Extract 6 status handlers
   - Expected: CC 12-15 → 3-4

### Phase 2: Medium-Impact Refactoring (Week 2)
**Target**: Reduce CC by additional 25%

1. **NamingAgent.determine_placement_confidence()** → Lookup table
   - Expected: CC 6-8 → 1-2

2. **Identify additional high-CC functions** in:
   - L1 Cognition layer (inference_engine.py, cognitive_node.py)
   - L3 Orchestration layer (mission_controller_engine.py, nervous_system_agent.py)
   - L5 Safety layer (governance.py, healer_agent.py)

### Phase 3: Testing & Validation (Week 3)
**Target**: Verify improvements and ensure correctness

1. Unit tests for extracted helper methods
2. Integration tests for dispatch patterns
3. CC measurement and comparison
4. Performance benchmarking

---

## Expected Improvements

### Current State
- **Overall CC**: 39.9 (high risk)
- **High-CC functions**: 4+ identified
- **Bug risk**: 3x higher than acceptable
- **Test coverage**: Exponential complexity

### Target State (After Refactoring)
- **Overall CC**: <25 (acceptable)
- **High-CC functions**: 0 (all <15)
- **Bug risk**: Baseline
- **Test coverage**: Linear complexity

### Metrics

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Overall CC | 39.9 | <25 | -37% |
| Max Function CC | 15+ | <10 | -33% |
| Functions CC>15 | 4+ | 0 | 100% |
| Test Cases Needed | Exponential | Linear | -90% |
| Maintainability | Low | High | +50% |

---

## Refactoring Checklist

### SovereignRedisClient.execute()
- [ ] Create dispatch dictionary for operations
- [ ] Extract _handle_set() method
- [ ] Extract _handle_get() method
- [ ] Extract _handle_delete() method
- [ ] Extract _handle_exists() method
- [ ] Extract _handle_keys() method
- [ ] Extract _handle_expire() method
- [ ] Extract _handle_ping() method
- [ ] Update error handling
- [ ] Test all operations
- [ ] Verify CC reduction

### SovereignGitClient.execute()
- [ ] Create dispatch dictionary for operations
- [ ] Extract _handle_commit() method
- [ ] Extract _handle_push() method
- [ ] Extract _handle_pull() method
- [ ] Extract _handle_status() method
- [ ] Extract _handle_diff() method
- [ ] Extract _handle_log() method
- [ ] Extract _handle_checkout() method
- [ ] Extract _handle_branch() method
- [ ] Test all operations
- [ ] Verify CC reduction

### NamingAgent.heal_naming_violations()
- [ ] Extract _initialize_summary() method
- [ ] Extract _is_agent_naming_violation() method
- [ ] Extract _process_healing_status() method
- [ ] Extract status handlers (_handle_renamed, etc.)
- [ ] Extract _print_healing_summary() method
- [ ] Test healing workflow
- [ ] Verify CC reduction

### NamingAgent.determine_placement_confidence()
- [ ] Extract _determine_confidence_level() method
- [ ] Replace if/elif with lookup table
- [ ] Test confidence calculation
- [ ] Verify CC reduction

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Overall CC | <25 | Radon/pylint |
| Max Function CC | <10 | Radon/pylint |
| Functions CC>15 | 0 | Code review |
| Test Coverage | >90% | pytest coverage |
| Code Duplication | <5% | pylint |

---

## Next Steps

1. **Measure baseline CC** using radon or pylint
2. **Implement Phase 1 refactoring** (dispatch patterns)
3. **Write unit tests** for extracted methods
4. **Measure improved CC** and compare
5. **Implement Phase 2 refactoring** (lookup tables, etc.)
6. **Final validation** and performance testing
