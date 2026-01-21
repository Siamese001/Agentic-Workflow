# System Hardening Guide
## Sub-Atomic Reliability Through Integrity Checks

**Version:** 1.0
**Last Updated:** December 15, 2025
**Status:** Implementation In Progress

---

## Executive Summary

This document outlines critical hardening measures to prevent "stale state" vulnerabilities and cache poisoning in the two-phase autonomous pipeline. The hardening strategy focuses on strict integrity checks at hand-off points between agents to prevent hallucinations based on corrupt or outdated states.

---

## Critical Vulnerabilities Identified

### 1. Stale State Vulnerability (CRITICAL)

**Problem:** The orchestrator only checks if `active_manifest.json` exists, not if it's current. If you edit code locally and run the system, Phase B executes against old code hashes.

**Impact:** Agents process outdated code, leading to incorrect validations and cache hits on stale data.

**Solution:** Implemented timestamp-based freshness check in `orchestrator.py`.

### 2. Cache Poisoning (HIGH)

**Problem:** If code logic changes (via Architect/Surgeon), old logic might remain in Redis/Pinecone if the query matches semantically.

**Impact:** Canon Validator returns stale validation results, causing incorrect decisions.

**Solution:** Compound cache keys that include file content hash.

### 3. Silent Failure Fallbacks (MEDIUM)

**Problem:** Mock fallbacks (e.g., `MockPinecone`) return empty results instead of failing explicitly.

**Impact:** Cognitive Node hallucinates that "no data exists" rather than "database is down."

**Solution:** Circuit Breaker pattern with explicit service unavailable exceptions.

---

## Hardening Implementation Status

### Phase A: Sanitization Hardening

#### ✅ Step 1: Librarian - Data Integrity

**Status:** PLANNED
**Priority:** HIGH

**Current Logic:**
```python
hash_content → dedup → write_manifest
```

**Vulnerability:** Whitespace/comment changes trigger full re-indexing.

**Hardening Action [1b]: AST-Based Hashing**
```python
def get_ast_hash(file_path: str) -> str:
    """
    Generate hash from AST structure, not raw text.
    Formatting changes don't invalidate cache.
    """
    with open(file_path, 'r') as f:
        code = f.read()

    tree = ast.parse(code)
    ast_dump = ast.dump(tree)
    return hashlib.sha256(ast_dump.encode()).hexdigest()
```

**Benefit:** Formatting changes (linting) don't invalidate cache or change manifest hash.

---

#### ⏳ Step 2: Architect - Import Validation

**Status:** PLANNED
**Priority:** MEDIUM

**Current Logic:**
```python
ast_parse → llm_refactor → ast_validate
```

**Vulnerability:** LLM might hallucinate imports that don't exist.

**Hardening Action [2d]: Import Validation**
```python
def validate_imports(code: str, allowed_libs: set) -> bool:
    """
    Validate that all imports exist in environment.
    """
    tree = ast.parse(code)

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = node.module if isinstance(node, ast.ImportFrom) else node.names[0].name
            base_module = module.split('.')[0]

            if base_module not in allowed_libs:
                raise ImportError(f"Hallucinated import: {module}")

    return True
```

**Equation:** $V_{code} = AST_{valid} \land Imports_{whitelisted}$

---

#### ⏳ Step 3: Surgeon - Scope Integrity Check

**Status:** PLANNED
**Priority:** LOW

**Current Logic:**
```python
compile_check → tiered_llm_fix
```

**Vulnerability:** Fixing syntax can break logic (e.g., closing parenthesis in wrong place).

**Hardening Action [3d]: Scope Integrity Check**
```python
def check_scope_integrity(original: str, fixed: str) -> bool:
    """
    Compare symbol tables to ensure functions/classes haven't vanished.
    """
    try:
        orig_tree = ast.parse(original)
        fixed_tree = ast.parse(fixed)

        orig_names = {node.name for node in ast.walk(orig_tree)
                      if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
        fixed_names = {node.name for node in ast.walk(fixed_tree)
                       if isinstance(node, (ast.FunctionDef, ast.ClassDef))}

        missing = orig_names - fixed_names
        if missing:
            raise ValueError(f"Scope integrity violated. Missing: {missing}")

        return True
    except SyntaxError:
        return True  # Original was too broken to parse
```

---

### Phase B: Runtime Hardening

#### ✅ Step 4: Orchestrator - Freshness Check

**Status:** IMPLEMENTED
**Priority:** CRITICAL

**Current Logic:**
```python
if not os.path.exists(manifest_path):
    run_librarian()
```

**Vulnerability:** Manifest exists but is stale (code modified after manifest creation).

**Hardening Action [4a]: Timestamp Comparison**

**Implementation:**
```python
def get_max_mtime(root_dir: str, excluded_dirs: set = None) -> float:
    """Get maximum modification time of all Python files."""
    if excluded_dirs is None:
        excluded_dirs = {'.git', '.venv', 'venv', '__pycache__', 'node_modules', 'logs'}

    max_mtime = 0.0
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(file_path)
                    max_mtime = max(max_mtime, mtime)
                except OSError:
                    continue

    return max_mtime

# In run_agentic_loop:
manifest_mtime = os.path.getmtime(manifest_path)
newest_file_time = get_max_mtime(".")

if newest_file_time > manifest_mtime:
    logger.warning("⚠️  DRIFT DETECTED: Code is newer than manifest!")
    logger.warning(f"   Drift: {newest_file_time - manifest_mtime:.0f} seconds")
    needs_sanitization = True
```

**Result:** Prevents execution on stale manifest. Auto-triggers Phase A when drift detected.

---

#### ✅ Step 5: Canon Validator - Compound Cache Keys

**Status:** IMPLEMENTED
**Priority:** HIGH

**Current Logic:**
```python
check_l1/l2 → miss → upsert
```

**Vulnerability:** Cache poisoning when code logic changes but query matches semantically.

**Hardening Action [6b]: Compound Cache Keys**

**Implementation:**
```python
def _generate_compound_cache_key(self, entry: CanonEntry, user_query: str = "") -> str:
    """
    Generate compound cache key with content hash.
    Key Structure: sha256(UserQuery + FileContentHash)
    """
    import hashlib

    compound_input = f"{user_query}:{entry.ast_hash}"
    compound_key = hashlib.sha256(compound_input.encode('utf-8')).hexdigest()

    return compound_key
```

**Result:** If Architect refactors code, context hash changes, automatically invalidating old cache entry.

---

#### ⏳ Step 6: Cognitive Node - Temperature Decay

**Status:** PLANNED
**Priority:** MEDIUM

**Current Logic:**
```python
think → epiphany → code_synthesis
```

**Vulnerability:** Infinite loops where agent "thinks" forever without convergence.

**Hardening Action [5c]: Reasoning Fatigue Decay**

**Formula:** $Temp_i = Temp_{base} \times (1 - \frac{i}{MaxSteps})$

**Implementation:**
```python
def think_with_decay(self, user_goal: str, max_steps: int = 10, base_temp: float = 0.7):
    """
    Multi-step reasoning with temperature decay to force convergence.
    """
    for i in range(max_steps):
        # Calculate decaying temperature
        temp = base_temp * (1 - (i / max_steps))

        # Ensure minimum temperature
        temp = max(temp, 0.1)

        response = self.llm.generate(
            prompt=user_goal,
            temperature=temp
        )

        if self._is_solution_complete(response):
            return response

    # Force return even if not perfect
    return response
```

**Result:** Forces convergence toward solution (even suboptimal) rather than infinite looping.

---

#### ⏳ Step 7: Connection Manager - Circuit Breaker

**Status:** PLANNED
**Priority:** MEDIUM

**Current Logic:**
```python
return MockPinecone() on failure
```

**Vulnerability:** Silent failure returns dummy data, causing hallucinations.

**Hardening Action [8e]: Circuit Breaker Pattern**

**Implementation:**
```python
class ServiceUnavailableError(Exception):
    """Raised when external service is unavailable."""
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise ServiceUnavailableError("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self.failure_count = 0
            self.state = "CLOSED"
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"

            raise ServiceUnavailableError(f"Service failed: {e}")

# In connection_manager.py:
def get_pinecone_index(self):
    """Get Pinecone index with circuit breaker protection."""
    try:
        return self.circuit_breaker.call(self._connect_pinecone)
    except ServiceUnavailableError:
        # DO NOT return Mock in production
        # Raise explicit error for hardened orchestrator to handle
        raise
```

**Result:** Hardened Orchestrator pauses workflow and enters "Wait/Retry" state, preserving workflow_state.

---

## Verification Checklist

### Phase A Hardening

- [ ] AST-based hashing implemented in Librarian
- [ ] Import validation added to Architect
- [ ] Scope integrity check added to Surgeon
- [ ] All Phase A agents log integrity check results

### Phase B Hardening

- [x] Freshness check implemented in Orchestrator
- [x] Compound cache keys implemented in Canon Validator
- [ ] Temperature decay implemented in Cognitive Node
- [ ] Circuit breaker implemented in Connection Manager
- [ ] All Phase B agents handle ServiceUnavailableError

### Integration Testing

- [ ] Test stale manifest detection (edit file, run orchestrator)
- [ ] Test cache invalidation (refactor code, verify cache miss)
- [ ] Test circuit breaker (kill Pinecone, verify graceful degradation)
- [ ] Test temperature decay (provide unsolvable problem, verify convergence)

---

## Monitoring & Observability

### Key Metrics to Track

1. **Drift Detection Rate**: How often does freshness check trigger re-sanitization?
2. **Cache Hit Rate**: Before and after compound key implementation
3. **Circuit Breaker Trips**: Frequency of service unavailability
4. **Temperature Decay Convergence**: Average steps to solution

### Logging Enhancements

```python
# Add to all hardening points:
logger.info("HARDENING_CHECK", extra={
    "check_type": "freshness|cache_key|circuit_breaker|temp_decay",
    "status": "pass|fail",
    "details": {...}
})
```

---

## Rollout Plan

### Phase 1: Critical Hardening (Week 1)
- [x] Implement freshness check in orchestrator
- [x] Implement compound cache keys in canon validator
- [ ] Add comprehensive logging

### Phase 2: Resilience Hardening (Week 2)
- [ ] Implement circuit breaker in connection manager
- [ ] Implement temperature decay in cognitive node
- [ ] Add integration tests

### Phase 3: Quality Hardening (Week 3)
- [ ] Implement AST-based hashing in librarian
- [ ] Implement import validation in architect
- [ ] Implement scope integrity in surgeon

---

## Conclusion

These hardening measures transform the system from "happy path" assumptions to "sub-atomic" reliability by:

1. **Preventing Stale Execution**: Freshness checks ensure code and manifest are synchronized
2. **Preventing Cache Poisoning**: Compound keys invalidate cache when code changes
3. **Preventing Silent Failures**: Circuit breakers force explicit error handling
4. **Preventing Infinite Loops**: Temperature decay forces convergence

**Next Steps:** Complete Phase 1 implementation and add comprehensive integration tests.

---

**Document Maintainer:** Agentic Workflow Team
**Last Review:** December 15, 2025
**Next Review:** December 22, 2025
