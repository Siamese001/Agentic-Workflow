---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\TEST_HARDENING_PLAN.md'
original_relative_path: 'TEST_HARDENING_PLAN.md'
source_sha256: c7f54fbcb8ec410bf77b41c34eef37621a5ed5d62d29b25c6c9a7961cb61633f
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# TEST HARDENING PLAN
**Waves 1-4 Revalidation Audit Remediation**

Generated: 2026-03-26
Priority: CRITICAL - Immediate implementation required

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## 🎯 IMMEDIATE ACTIONS (Critical - Implement First)

### 1. Eliminate Silent Degradation Pattern

#### Current Problematic Pattern:
```python
# guardian: allow-silent-degradation - Optional <module>
try:
    import optional_module
except ImportError:
    pass  # Silent failure
```

#### Solution: Dependency Injection with Explicit Failures

**File**: `agentic_core/L4_state/enforcement/graph_memory_bridge.py`

**Before**:
```python
try:
    from agentic_core.adg.client.InMemoryStore import ADGMCPClient as _MCPFallbackClient
    _FALLBACK_AVAILABLE = True
except ImportError:
    _FALLBACK_AVAILABLE = False
```

**After**:
```python
class DependencyManager:
    def __init__(self):
        self._mcp_client = None
        self._sqlite_store = None
        
    def initialize_mcp_client(self):
        """Initialize MCP client with explicit failure handling."""
        try:
            from agentic_core.adg.client.InMemoryStore import ADGMCPClient
            self._mcp_client = ADGMCPClient()
            return True
        except ImportError as e:
            raise DependencyError(f"MCP client not available: {e}. Install agentic_core[adg] or implement fallback.")
    
    def get_mcp_client(self):
        if self._mcp_client is None:
            raise DependencyError("MCP client not initialized. Call initialize_mcp_client() first.")
        return self._mcp_client
```

### 2. Fix State Leaks in GraphMemoryBridge

#### Current Problem:
```python
class GraphMemoryBridge:
    _registered_entities = set()  # Class-level state leak
    _stats = {"entities_created": 0}  # Persistent across instances
```

#### Solution: Instance-Level State with Cleanup

**After**:
```python
class GraphMemoryBridge:
    def __init__(self):
        self._registered_entities = set()  # Instance-level
        self._stats = {"entities_created": 0}  # Instance-level
        self._cleanup_registered = False
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        
    def cleanup(self):
        """Explicit cleanup method for test isolation."""
        if not self._cleanup_registered:
            self._registered_entities.clear()
            self._stats = {"entities_created": 0}
            self._cleanup_registered = True
```

### 3. Strengthen Test Assertions

#### Current Weak Assertions:
```python
assert report.project_root == tmp_path
assert isinstance(summary, str)
assert len(violations) == 0
```

#### Solution: Behavioral Validation

**After**:
```python
def test_scan_report_behavioral_validation(self, tmp_path):
    """Test ScanReport with behavioral validation, not just property checks."""
    # Create test file with known violations
    test_file = tmp_path / "test.py"
    test_file.write_text("""
import sys
sys.path.append("/some/path")  # Global mutation violation
""")
    
    scanner = AntiPatternScanner(enforcement_level=EnforcementLevel.HARD_BLOCK)
    report = scanner.scan_file(test_file)
    
    # Behavioral assertions, not just property checks
    assert not report.passed, "Report should not pass with violations"
    assert report.total_violations == 1, f"Expected 1 violation, got {report.total_violations}"
    
    # Verify specific violation content
    violation = report.all_violations[0]
    assert violation.category == AntiPatternCategory.GLOBAL_MUTATION
    assert "sys.path" in violation.message
    assert violation.line_number == 3
    assert violation.file_path == test_file
```

---

## 🔧 MEDIUM-TERM IMPROVEMENTS (High Priority)

### 4. Expand Coverage to Error Paths

#### Add Malformed Exemption Tests:
```python
class TestExemptionEdgeCases:
    """Test edge cases in exemption recognition."""
    
    def test_malformed_exemption_no_reason(self, tmp_path):
        """Test exemption without reason fails validation."""
        code = """# guardian: allow-silent-degradation
try:
    import missing
except ImportError:
    pass
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)
        
        detector = SilentDegradationDetector()
        with pytest.raises(ExemptionFormatError, match="Exemption must include reason"):
            detector.scan_file(file_path)
    
    def test_exemption_out_of_range(self, tmp_path):
        """Test exemption too far from violation is ignored."""
        code = """# guardian: allow-silent-degradation - Too far

# Many lines between exemption and violation
# 1
# 2  
# 3
# 4
# 5
# 6
try:
    import missing
except ImportError:
    pass
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)
        
        detector = SilentDegradationDetector()
        result = detector.scan_file(file_path)
        assert len(result.violations) == 1, "Exemption out of range should not suppress"
```

### 5. Add Determinism Guarantees

#### Seed Control for Random Operations:
```python
class DeterministicScanner:
    """Scanner with deterministic behavior for testing."""
    
    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)
        self.time_provider = lambda: 1234567890  # Fixed timestamp
        
    def scan_with_deterministic_order(self, file_path: Path) -> ScanReport:
        """Scan files in deterministic order."""
        # Use deterministic file iteration
        files = sorted(file_path.rglob("*.py"))
        results = []
        
        for file_path in files:
            result = self._scan_single_file(file_path)
            results.append(result)
            
        return self._combine_results(results)
```

### 6. Implement Proper Test Isolation

#### Test Isolation Framework:
```python
class IsolatedTest:
    """Base class for tests requiring complete isolation."""
    
    def setup_method(self):
        """Setup isolated test environment."""
        self.original_cwd = Path.cwd()
        self.original_env = os.environ.copy()
        self.original_path = sys.path[:]
        
        # Create isolated temp directory
        self.temp_dir = Path(tempfile.mkdtemp())
        os.chdir(self.temp_dir)
        
        # Reset any global state
        reset_global_state()
        
    def teardown_method(self):
        """Cleanup isolated test environment."""
        os.chdir(self.original_cwd)
        os.environ.clear()
        os.environ.update(self.original_env)
        sys.path[:] = self.original_path
        
        # Clean up temp directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
```

---

## 📋 COVERAGE EXPANSION (Medium Priority)

### 7. Edge Case Test Suite

#### Empty File Handling:
```python
def test_scan_empty_file(self, tmp_path):
    """Test scanner behavior on completely empty files."""
    empty_file = tmp_path / "empty.py"
    empty_file.touch()
    
    scanner = AntiPatternScanner()
    report = scanner.scan_file(empty_file)
    
    assert report.passed is True
    assert report.total_files_scanned == 1
    assert report.total_violations == 0
```

#### Invalid Syntax Handling:
```python
def test_scan_invalid_syntax(self, tmp_path):
    """Test scanner behavior on files with invalid Python syntax."""
    invalid_file = tmp_path / "invalid.py"
    invalid_file.write_text("def invalid_syntax(\n    # Missing closing parenthesis")
    
    scanner = AntiPatternScanner()
    report = scanner.scan_file(invalid_file)
    
    # Should handle syntax errors gracefully
    assert len(report.errors) == 1
    assert "SyntaxError" in report.errors[0]
```

### 8. Concurrent Access Testing

#### Thread Safety Tests:
```python
def test_concurrent_entity_creation(self):
    """Test GraphMemoryBridge under concurrent access."""
    import threading
    import time
    
    bridge = GraphMemoryBridge()
    results = []
    errors = []
    
    def create_entities(thread_id):
        try:
            for i in range(10):
                entity_name = f"thread_{thread_id}_entity_{i}"
                success = bridge.create_entity(entity_name, "test_type")
                results.append((thread_id, i, success))
        except Exception as e:
            errors.append((thread_id, str(e)))
    
    # Create multiple threads
    threads = []
    for thread_id in range(5):
        thread = threading.Thread(target=create_entities, args=(thread_id,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify no race conditions
    assert len(errors) == 0, f"Errors in concurrent execution: {errors}"
    assert len(results) == 50, f"Expected 50 operations, got {len(results)}"
    
    # Verify all entities were created uniquely
    entity_names = {r[2] for r in results if r[2]}  # Successful creations
    assert len(entity_names) == 50, "Some entities were not created due to race conditions"
```

---

## 🔄 IMPLEMENTATION SEQUENCE

### Week 1: Critical Fixes
1. [ ] Eliminate silent degradation patterns (39 files)
2. [ ] Fix GraphMemoryBridge state leaks
3. [ ] Strengthen core test assertions

### Week 2: Coverage Expansion  
1. [ ] Add error path tests
2. [ ] Add edge case tests
3. [ ] Implement test isolation framework

### Week 3: Advanced Features
1. [ ] Add deterministic behavior
2. [ ] Add concurrent access tests
3. [ ] Performance and load testing

### Week 4: Validation
1. [ ] Re-run comprehensive audit
2. [ ] Fix any remaining issues
3. [ ] Final validation and sign-off

---

## 🎯 SUCCESS CRITERIA

### Must Achieve:
- [ ] **Zero silent degradation patterns** in production code
- [ ] **Complete test isolation** - no state leaks between tests
- [ ] **Behavioral test validation** - no trivial assertions
- [ ] **Error path coverage** - all failure modes tested
- [ ] **Deterministic behavior** - consistent results across runs

### Should Achieve:
- [ ] **95%+ code coverage** on critical components
- [ ] **Concurrent access testing** for all shared state
- [ ] **Performance benchmarking** for regression detection
- [ ] **Documentation completeness** for all test patterns

### Could Achieve:
- [ ] **Property-based testing** for edge case discovery
- [ ] **Mutation testing** for test quality validation
- [ ] **Contract testing** for interface compliance
- [ ] **Chaos engineering** for resilience validation

---

## 🚨 RISK MITIGATION

### During Implementation:
1. **Branch Strategy**: Work in feature branches, merge via PR
2. **Backward Compatibility**: Ensure existing functionality preserved
3. **Incremental Deployment**: Roll out changes gradually
4. **Monitoring**: Add observability for failure detection

### Validation Strategy:
1. **Automated Testing**: CI/CD pipeline with comprehensive tests
2. **Manual Review**: Code review for all critical changes
3. **Integration Testing**: Full system validation
4. **Performance Testing**: Ensure no regressions

---

## 📊 METRICS AND TRACKING

### Quality Metrics:
- **Test Coverage**: Target 95%+ for critical components
- **Defect Density**: < 1 defect per 1000 lines of code
- **Test Flakiness**: < 1% flaky test rate
- **Performance**: < 10% regression in test execution time

### Progress Tracking:
- **Weekly Status Reports**: Progress against implementation plan
- **Defect Trend Analysis**: Track defect discovery and resolution
- **Coverage Reports**: Weekly coverage improvement tracking
- **Risk Assessment**: Ongoing risk evaluation and mitigation

---

**Implementation Priority**: 🚨 **CRITICAL** - Start immediately
**Expected Timeline**: 
**Success Probability**: 85% with proper execution

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

