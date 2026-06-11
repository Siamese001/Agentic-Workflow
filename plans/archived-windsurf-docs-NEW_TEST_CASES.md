---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\NEW_TEST_CASES.md'
original_relative_path: 'NEW_TEST_CASES.md'
source_sha256: 96d6de1fe5b7724436009f32bae5ee361b9959b4778a78a1e6d5ce0b2ffd8c9e
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# NEW TEST CASES
**Waves 1-4 Revalidation Audit - Comprehensive Test Suite**

Generated: 2026-03-26
Purpose: Fill critical coverage gaps and eliminate hidden failures

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


## 🧪 CRITICAL TESTS (Must Add Immediately)

### 1. Silent Degradation Elimination Tests

#### Test: Missing Dependency Fails Fast
```python
# tests/unit/agentic_core/L5_safety/validators/test_dependency_management.py

import pytest
from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge, DependencyError

class TestDependencyManagement:
    """Test that missing dependencies cause explicit failures, not silent degradation."""
    
    def test_missing_mcp_client_raises_explicit_error(self):
        """Test that missing MCP client raises DependencyError, not silent failure."""
        bridge = GraphMemoryBridge()
        
        # Should not silently fall back - should raise explicit error
        with pytest.raises(DependencyError, match="MCP client not available"):
            bridge.get_mcp_client()
    
    def test_dependency_error_includes_helpful_message(self):
        """Test that DependencyError includes installation guidance."""
        bridge = GraphMemoryBridge()
        
        with pytest.raises(DependencyError) as exc_info:
            bridge.get_mcp_client()
        
        error_msg = str(exc_info.value)
        assert "Install agentic_core[adg]" in error_msg
        assert "implement fallback" in error_msg
    
    def test_explicit_initialization_required(self):
        """Test that dependencies must be explicitly initialized."""
        bridge = GraphMemoryBridge()
        
        # Should not auto-initialize silently
        with pytest.raises(DependencyError, match="not initialized"):
            bridge.initialize_mcp_client()
        
        # After explicit init, should work
        try:
            bridge.initialize_mcp_client()
            # If initialization succeeds, get should work
            client = bridge.get_mcp_client()
            assert client is not None
        except DependencyError:
            # If MCP not available, that's expected in test environment
            pass
```

### 2. State Isolation Tests

#### Test: GraphMemoryBridge State Isolation
```python
# tests/unit/agentic_core/L4_state/enforcement/test_graph_memory_bridge_isolation.py

import pytest
from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

class TestGraphMemoryBridgeIsolation:
    """Test that multiple bridge instances don't share state."""
    
    def test_multiple_instances_isolated_state(self):
        """Test that multiple instances have independent state."""
        bridge1 = GraphMemoryBridge()
        bridge2 = GraphMemoryBridge()
        
        # Create entity in bridge1
        success1 = bridge1.create_entity("test_entity_1", "test_type")
        assert success1 is True
        
        # Bridge2 should not see bridge1's entity
        assert "test_entity_1" not in bridge2._registered_entities
        assert bridge2.stats["entities_created"] == 0
        
        # Create entity in bridge2
        success2 = bridge2.create_entity("test_entity_2", "test_type")
        assert success2 is True
        
        # Each should only see its own entities
        assert bridge1.stats["entities_created"] == 1
        assert bridge2.stats["entities_created"] == 1
        assert len(bridge1._registered_entities) == 1
        assert len(bridge2._registered_entities) == 1
    
    def test_cleanup_resets_state_completely(self):
        """Test that cleanup method resets all state."""
        bridge = GraphMemoryBridge()
        
        # Create some state
        bridge.create_entity("test_entity_1", "test_type")
        bridge.create_entity("test_entity_2", "test_type")
        bridge.create_relation("test_entity_1", "test_entity_2", "test_relation")
        
        # Verify state exists
        assert len(bridge._registered_entities) == 2
        assert bridge.stats["entities_created"] == 2
        
        # Cleanup should reset everything
        bridge.cleanup()
        
        assert len(bridge._registered_entities) == 0
        assert bridge.stats["entities_created"] == 0
        assert bridge._cleanup_registered is True
    
    def test_context_manager_automatic_cleanup(self):
        """Test that context manager automatically cleans up."""
        initial_stats = None
        
        with GraphMemoryBridge() as bridge:
            bridge.create_entity("test_entity", "test_type")
            initial_stats = bridge.stats.copy()
            assert initial_stats["entities_created"] == 1
        
        # After context, state should be reset
        assert bridge.stats["entities_created"] == 0
        assert len(bridge._registered_entities) == 0
    
    def test_concurrent_instances_dont_interfere(self):
        """Test that concurrent instances don't share state."""
        import threading
        import time
        
        results = {}
        
        def create_entities_in_instance(instance_id):
            bridge = GraphMemoryBridge()
            entity_count = 0
            
            for i in range(5):
                entity_name = f"instance_{instance_id}_entity_{i}"
                if bridge.create_entity(entity_name, "test_type"):
                    entity_count += 1
            
            results[instance_id] = {
                'entity_count': entity_count,
                'stats': bridge.stats.copy(),
                'registered_count': len(bridge._registered_entities)
            }
        
        # Create multiple threads with different instances
        threads = []
        for instance_id in range(3):
            thread = threading.Thread(target=create_entities_in_instance, args=(instance_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify each instance had isolated state
        for instance_id, result in results.items():
            assert result['entity_count'] == 5
            assert result['stats']['entities_created'] == 5
            assert result['registered_count'] == 5
```

### 3. Concurrent Access Tests

#### Test: Thread Safety of GraphMemoryBridge
```python
# tests/unit/agentic_core/L4_state/enforcement/test_graph_memory_bridge_concurrent.py

import pytest
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

class TestGraphMemoryBridgeConcurrent:
    """Test thread safety of GraphMemoryBridge operations."""
    
    def test_concurrent_entity_creation(self):
        """Test concurrent entity creation doesn't cause race conditions."""
        bridge = GraphMemoryBridge()
        created_entities = []
        errors = []
        
        def create_entity(entity_id):
            try:
                entity_name = f"concurrent_entity_{entity_id}"
                success = bridge.create_entity(entity_name, "test_type")
                created_entities.append((entity_id, success))
            except Exception as e:
                errors.append((entity_id, str(e)))
        
        # Create 50 entities concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_entity, i) for i in range(50)]
            for future in as_completed(futures):
                future.result()  # Wait for completion
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Errors in concurrent execution: {errors}"
        
        # Verify all entities were created
        assert len(created_entities) == 50
        assert all(success for _, success in created_entities)
        
        # Verify no duplicates
        assert len(bridge._registered_entities) == 50
    
    def test_concurrent_relation_creation(self):
        """Test concurrent relation creation maintains consistency."""
        bridge = GraphMemoryBridge()
        
        # First create entities
        for i in range(10):
            bridge.create_entity(f"entity_{i}", "test_type")
        
        created_relations = []
        errors = []
        
        def create_relation(relation_id):
            try:
                from_entity = f"entity_{relation_id % 10}"
                to_entity = f"entity_{(relation_id + 1) % 10}"
                relation_type = f"relation_{relation_id}"
                
                success = bridge.create_relation(from_entity, to_entity, relation_type)
                created_relations.append((relation_id, success))
            except Exception as e:
                errors.append((relation_id, str(e)))
        
        # Create 100 relations concurrently
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_relation, i) for i in range(100)]
            for future in as_completed(futures):
                future.result()
        
        # Verify no errors
        assert len(errors) == 0, f"Errors in concurrent relation creation: {errors}"
        
        # Verify stats consistency
        assert bridge.stats["relations_created"] >= 90  # Some might fail due to missing entities
    
    def test_concurrent_observation_addition(self):
        """Test concurrent observation addition maintains data integrity."""
        bridge = GraphMemoryBridge()
        
        # Create test entity
        bridge.create_entity("test_entity", "test_type")
        
        observations = []
        errors = []
        
        def add_observation(obs_id):
            try:
                entity_name = "test_entity"
                observation = f"Observation {obs_id} at {time.time()}"
                success = bridge.add_observation(entity_name, observation)
                observations.append((obs_id, success))
            except Exception as e:
                errors.append((obs_id, str(e)))
        
        # Add 200 observations concurrently
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(add_observation, i) for i in range(200)]
            for future in as_completed(futures):
                future.result()
        
        # Verify no errors
        assert len(errors) == 0, f"Errors in concurrent observation addition: {errors}"
        
        # Verify most observations were added
        successful_obs = [obs for _, success in observations if success]
        assert len(successful_obs) >= 190  # Allow for some race condition failures
```

### 4. Error Path Tests

#### Test: Exemption Recognition Edge Cases
```python
# tests/guardian/test_exemption_edge_cases.py

import pytest
from agentic_core.L5_safety.validators.silent_degradation_validator import (
    SilentDegradationDetector,
    ExemptionFormatError
)

class TestExemptionEdgeCases:
    """Test edge cases in exemption recognition."""
    
    def test_malformed_exemption_no_reason(self, tmp_path):
        """Test exemption without reason fails validation."""
        code = """# guardian: allow-silent-degradation
try:
    import missing_module
except ImportError:
    pass
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)
        
        detector = SilentDegradationDetector()
        with pytest.raises(ExemptionFormatError, match="Exemption must include reason"):
            detector.scan_file(file_path)
    
    def test_malformed_exemption_invalid_format(self, tmp_path):
        """Test exemption with invalid format fails validation."""
        code = """# guardian: invalid-format - Some reason
try:
    import missing_module
except ImportError:
    pass
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)
        
        detector = SilentDegradationDetector()
        with pytest.raises(ExemptionFormatError, match="Invalid exemption format"):
            detector.scan_file(file_path)
    
    def test_exemption_out_of_range_ignored(self, tmp_path):
        """Test exemption too far from violation is ignored."""
        code = """# guardian: allow-silent-degradation - Too far away

# Line 2
# Line 3
# Line 4
# Line 5
# Line 6
# Line 7
# Line 8
try:
    import missing_module
except ImportError:
    pass
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)
        
        detector = SilentDegradationDetector()
        result = detector.scan_file(file_path)
        
        # Exemption out of range should not suppress violation
        assert len(result.violations) == 1
        assert result.violations[0].suppressed is False
    
    def test_multiple_exemptions_conflict_resolution(self, tmp_path):
        """Test how conflicting exemptions are resolved."""
        code = """# guardian: allow-silent-degradation - First reason
# guardian: allow-silent-degradation - Second reason
try:
    import missing_module
except ImportError:
    pass
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)
        
        detector = SilentDegradationDetector()
        result = detector.scan_file(file_path)
        
        # Should use the first valid exemption
        assert len(result.violations) == 1
        assert result.violations[0].suppressed is True
        assert result.violations[0].exemption_reason == "First reason"
    
    def test_exemption_with_special_characters(self, tmp_path):
        """Test exemption with special characters in reason."""
        code = """# guardian: allow-silent-degradation - Optional dependency (requires: pip install package-name)
try:
    import missing_module
except ImportError:
    pass
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)
        
        detector = SilentDegradationDetector()
        result = detector.scan_file(file_path)
        
        # Should handle special characters correctly
        assert len(result.violations) == 1
        assert result.violations[0].suppressed is True
        assert "pip install package-name" in result.violations[0].exemption_reason
```

---

## 📋 COVERAGE TESTS (Should Add)

### 5. Edge Case Test Suite

#### Test: Empty File Handling
```python
# tests/unit/agentic_core/L5_safety/validators/test_scanner_edge_cases.py

class TestScannerEdgeCases:
    """Test scanner behavior on edge cases."""
    
    def test_scan_empty_file(self, tmp_path):
        """Test scanner behavior on completely empty files."""
        empty_file = tmp_path / "empty.py"
        empty_file.touch()
        
        scanner = AntiPatternScanner()
        report = scanner.scan_file(empty_file)
        
        assert report.passed is True
        assert report.total_files_scanned == 1
        assert report.total_violations == 0
        assert report.errors == []
    
    def test_scan_whitespace_only_file(self, tmp_path):
        """Test scanner behavior on files with only whitespace."""
        ws_file = tmp_path / "whitespace.py"
        ws_file.write_text("   \n  \t\n   \n")
        
        scanner = AntiPatternScanner()
        report = scanner.scan_file(ws_file)
        
        assert report.passed is True
        assert report.total_violations == 0
    
    def test_scan_comments_only_file(self, tmp_path):
        """Test scanner behavior on files with only comments."""
        comment_file = tmp_path / "comments.py"
        comment_file.write_text("""
# This is a comment
# Another comment
""")
        
        scanner = AntiPatternScanner()
        report = scanner.scan_file(comment_file)
        
        assert report.passed is True
        assert report.total_violations == 0
```

#### Test: Invalid Syntax Handling
```python
    def test_scan_invalid_syntax(self, tmp_path):
        """Test scanner behavior on files with invalid Python syntax."""
        invalid_file = tmp_path / "invalid.py"
        invalid_file.write_text("""
def invalid_function(
    # Missing closing parenthesis
    pass
""")
        
        scanner = AntiPatternScanner()
        report = scanner.scan_file(invalid_file)
        
        # Should handle syntax errors gracefully
        assert len(report.errors) == 1
        assert "SyntaxError" in report.errors[0]
        assert report.passed is False  # Syntax errors should cause failure
    
    def test_scan_mixed_encoding(self, tmp_path):
        """Test scanner behavior on files with mixed encoding."""
        mixed_file = tmp_path / "mixed.py"
        
        # Write file with UTF-8 BOM then regular content
        with open(mixed_file, 'w', encoding='utf-8-sig') as f:
            f.write('import sys\n')
            f.write('sys.path.append("test")\n')
        
        scanner = AntiPatternScanner()
        report = scanner.scan_file(mixed_file)
        
        # Should handle encoding gracefully
        assert report.total_violations == 1  # Should detect sys.path mutation
```

### 6. Determinism Tests

#### Test: Same-Process Repeated Execution
```python
# tests/system/test_deterministic_behavior.py

class TestDeterministicBehavior:
    """Test deterministic behavior across multiple executions."""
    
    def test_scanner_deterministic_same_process(self, tmp_path):
        """Test scanner produces same results in same process."""
        # Create test file with deterministic violations
        test_file = tmp_path / "deterministic.py"
        test_file.write_text("""
import sys
sys.path.append("/test/path")
import os
os.environ["TEST_VAR"] = "value"
""")
        
        scanner = AntiPatternScanner(enforcement_level=EnforcementLevel.WARNING)
        
        # Run scan multiple times
        results = []
        for i in range(5):
            report = scanner.scan_file(test_file)
            results.append({
                'violations': len(report.all_violations),
                'categories': sorted([v.category.name for v in report.all_violations]),
                'line_numbers': sorted([v.line_number for v in report.all_violations])
            })
        
        # All results should be identical
        first_result = results[0]
        for i, result in enumerate(results[1:], 1):
            assert result == first_result, f"Result {i} differs from first result"
    
    def test_scanner_deterministic_across_processes(self, tmp_path):
        """Test scanner produces same results across different processes."""
        import subprocess
        import json
        import tempfile
        
        # Create test file
        test_file = tmp_path / "cross_process.py"
        test_file.write_text("""
try:
    import missing_module
except ImportError:
    pass
""")
        
        # Create scanner script
        scanner_script = tmp_path / "scanner_script.py"
        scanner_script.write_text(f"""
import sys
import json
from pathlib import Path

sys.path.insert(0, '{Path(__file__).parent.parent}')

from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import AntiPatternScanner
from agentic_core.L5_safety.validators.base_detector_validator import EnforcementLevel

scanner = AntiPatternScanner(enforcement_level=EnforcementLevel.WARNING)
report = scanner.scan_file(Path('{test_file}'))

result = {{
    'violations': len(report.all_violations),
    'categories': sorted([v.category.name for v in report.all_violations]),
    'line_numbers': sorted([v.line_number for v in report.all_violations]),
    'messages': [v.message for v in report.all_violations]
}}

print(json.dumps(result))
""")
        
        # Run scanner in multiple processes
        results = []
        for i in range(3):
            result = subprocess.run(
                [sys.executable, str(scanner_script)],
                capture_output=True,
                text=True,
                cwd=tmp_path
            )
            
            assert result.returncode == 0, f"Process {i} failed: {result.stderr}"
            
            process_result = json.loads(result.stdout.strip())
            results.append(process_result)
        
        # All results should be identical
        first_result = results[0]
        for i, result in enumerate(results[1:], 1):
            assert result == first_result, f"Process {i} result differs from first process"
```

### 7. Performance and Load Tests

#### Test: Large File Performance
```python
# tests/performance/test_scanner_performance.py

class TestScannerPerformance:
    """Test scanner performance under various conditions."""
    
    def test_scan_large_file_performance(self, tmp_path):
        """Test scanner performance on large files."""
        import time
        
        # Create large file with many violations
        large_file = tmp_path / "large.py"
        
        with open(large_file, 'w') as f:
            for i in range(1000):
                f.write(f"""
# Function {i}
def function_{i}():
    import sys
    sys.path.append("/path/{i}")
    
    try:
        import missing_module_{i}
    except ImportError:
        pass
    
    return None
""")
        
        scanner = AntiPatternScanner()
        
        # Measure scan time
        start_time = time.time()
        report = scanner.scan_file(large_file)
        end_time = time.time()
        
        scan_time = end_time - start_time
        
        # Performance assertions
        assert scan_time < 5.0, f"Scan took too long: {scan_time:.2f}s"
        assert report.total_violations == 2000, f"Expected 2000 violations, got {report.total_violations}"
        assert len(report.errors) == 0, f"Unexpected errors: {report.errors}"
    
    def test_scan_many_small_files_performance(self, tmp_path):
        """Test scanner performance on many small files."""
        import time
        
        # Create many small files
        files = []
        for i in range(100):
            file_path = tmp_path / f"small_{i}.py"
            file_path.write_text(f"""
import sys
sys.path.append("/path/{i}")
""")
            files.append(file_path)
        
        scanner = AntiPatternScanner()
        
        # Measure scan time
        start_time = time.time()
        reports = [scanner.scan_file(f) for f in files]
        end_time = time.time()
        
        scan_time = end_time - start_time
        
        # Performance assertions
        assert scan_time < 3.0, f"Scanning {len(files)} files took too long: {scan_time:.2f}s"
        
        # Verify all files were scanned correctly
        total_violations = sum(r.total_violations for r in reports)
        assert total_violations == 100, f"Expected 100 total violations, got {total_violations}"
```

---

## 🔄 IMPLEMENTATION NOTES

### Test Organization
- Place critical tests in appropriate test directories
- Use descriptive test class and method names
- Include comprehensive docstrings explaining test purpose
- Add markers for test categories: `@pytest.mark.critical`, `@pytest.mark.coverage`

### Test Data Management
- Use pytest fixtures for test data setup
- Clean up test artifacts in teardown
- Use temporary directories for file-based tests
- Mock external dependencies appropriately

### Assertion Strategy
- Use specific assertions with clear error messages
- Test both positive and negative cases
- Verify exact values, not just types or existence
- Include edge case boundaries in assertions

### CI/CD Integration
- Ensure all tests pass in CI environment
- Add performance regression detection
- Include coverage reporting
- Add flaky test detection and reporting

---

## 📊 SUCCESS METRICS

### Coverage Targets
- **Critical Tests**: 100% implementation
- **Coverage Tests**: 95% implementation
- **Overall Coverage**: 90%+ for critical components

### Quality Targets
- **Test Pass Rate**: 100% in CI
- **Performance**: No regression > 10%
- **Flaky Test Rate**: < 1%
- **Execution Time**: <  for full suite

### Risk Mitigation
- **Critical Issues**: 0 remaining
- **High Issues**: < 5 remaining
- **Medium Issues**: < 10 remaining
- **Test Isolation**: 100% achieved

---

**Implementation Priority**: 🚨 **CRITICAL** - Start with critical tests immediately
**Expected Timeline**:  for critical tests, 2 additional weeks for coverage tests
**Success Probability**: 90% with proper execution and resource allocation

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

