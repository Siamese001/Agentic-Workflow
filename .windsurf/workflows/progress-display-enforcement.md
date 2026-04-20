---
description: Enforce progress display requirements for all long-running operations (>5s) with colored progress bars and percentage displays
---

> **Claude workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

# Progress Display Enforcement Workflow

This workflow enforces the constitutional requirement for progress displays on all operations exceeding 5 seconds, as specified in §5.3 of the Windsurf rules.

## When to Use

**MANDATORY** for any operation that:
- Takes longer than 5 seconds to complete
- Processes multiple items (files, tests, nodes, etc.)
- Performs batch operations
- Runs queries or searches
- Executes test suites
- Generates ADG artifacts
- Builds dependency graphs

## Enforcement Protocol

### 1. Operation Detection

Before starting any operation, estimate duration:
```python
# Check if operation will exceed 5 seconds
if estimated_duration > 5.0 or item_count > 10:
    # Progress display required
    invoke_progress_display()
```

### 2. Progress Display Implementation

Use the standardized progress display format:
```python
from tools.progress_display import ProgressTracker

# Create tracker
tracker = ProgressTracker(total_items, operation_name)
tracker.start()

# Update progress
for item in items:
    process_item(item)
    tracker.update(1, f"Processing {item.name}")

# Complete
tracker.complete("Operation complete")
```

### 3. Color Requirements

**Mandatory color scheme**:
- 🟢 **Green** (`\033[92m`): Success/complete (≥90%)
- 🔵 **Blue** (`\033[94m`): In-progress (70-89%)
- 🟡 **Yellow** (`\033[93m`): Warning/slow (40-69%)
- 🔴 **Red** (`\033[91m`): Error/slow (<40%)
- ⚪ **White** (`\033[97m`): Neutral/pending

### 4. Progress Bar Format

**Standard format** (40 characters):
```
[████████████████████████████████] 100% (2500/2500) - ETA: 0s
```

**Components**:
- 40-character progress bar using `█` and `░`
- Percentage completion (5 digits + %)
- Current/total count in parentheses
- ETA for operations >30s

### 5. Update Frequency

**Minimum**: Every 5 seconds
**Recommended**: Every 1-2 seconds
**Maximum**: No more frequent than every 0.5 seconds

## Integration Points

### ADG Operations
- **Module scanning**: Show progress through Python files
- **Edge building**: Display dependency graph construction
- **Validation**: Show ADG structure validation progress

### Test Execution
- **Test collection**: Progress through test discovery
- **Test running**: Display pass/fail counts in real-time
- **Coverage calculation**: Show coverage computation progress

### File System Operations
- **Repository scanning**: Progress through directory tree
- **File processing**: Display file-by-file progress
- **Batch operations**: Show batch completion status

### CI Operations
- **Gate execution**: Progress through CI gates
- **Script execution**: Display script run progress
- **Report generation**: Show report building progress

## Verification Checklist

Before completing any operation >5s, verify:

- [ ] **Progress bar displayed** with correct format
- [ ] **Colors applied** according to percentage thresholds
- [ ] **ETA calculated** for operations >30s
- [ ] **Updates frequent** enough (≤5s intervals)
- [ ] **Current item tracking** with descriptive messages
- [ ] **Final status** shown with appropriate color
- [ ] **Error handling** with colored error messages

## Common Implementation Patterns

### Pattern 1: File Processing
```python
def process_files_with_progress(file_paths):
    tracker = ProgressTracker(len(file_paths), "Processing files")
    tracker.start()
    
    try:
        for i, file_path in enumerate(file_paths):
            process_file(file_path)
            tracker.update(1, f"Processed {os.path.basename(file_path)}")
        
        tracker.complete(f"Processed {len(file_paths)} files")
    except Exception as e:
        tracker.fail(f"Failed: {e}")
        raise
```

### Pattern 2: Test Execution
```python
def run_tests_with_progress(test_nodes):
    tracker = ProgressTracker(len(test_nodes), "Running tests")
    passed = failed = 0
    tracker.start()
    
    try:
        for test_id in test_nodes:
            result = run_test(test_id)
            if result.passed:
                passed += 1
            else:
                failed += 1
            
            status = f"✅ {passed} ❌ {failed}"
            tracker.update(1, status)
        
        tracker.complete(f"Results: {passed} passed, {failed} failed")
    except Exception as e:
        tracker.fail(f"Test execution failed: {e}")
        raise
```

### Pattern 3: ADG Operations
```python
def build_adg_with_progress():
    # Module scanning
    modules = discover_modules()
    module_tracker = ProgressTracker(len(modules), "ADG Module Scan")
    module_tracker.start()
    
    for module in modules:
        scan_module(module)
        module_tracker.update(1, f"Scanning {module}")
    
    module_tracker.complete(f"Scanned {len(modules)} modules")
    
    # Edge building
    edges = discover_edges()
    edge_tracker = ProgressTracker(len(edges), "ADG Edge Building")
    edge_tracker.start()
    
    for edge in edges:
        build_edge(edge)
        edge_tracker.update(1)
    
    edge_tracker.complete(f"Built {len(edges)} edges")
```

## Error Handling

### Progress Interruption
```python
try:
    for item in long_operation():
        tracker.update(1, f"Processing {item}")
except KeyboardInterrupt:
    tracker.fail("Operation interrupted by user")
    raise
except Exception as e:
    tracker.fail(f"Operation failed: {e}")
    raise
```

### Recovery Mode
```python
def resume_with_progress(checkpoint_file, total_items):
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file) as f:
            completed = int(f.read())
        print(f"{COLORS['warning']}🔄 Resuming from checkpoint: {completed}/{total_items}{COLORS['reset']}")
        return completed
    return 0
```

## Testing Progress Display

### Unit Test Template
```python
def test_progress_display():
    """Test progress display functionality"""
    import io
    import sys
    from unittest.mock import patch
    
    # Capture output
    captured_output = io.StringIO()
    
    with patch('sys.stdout', captured_output):
        tracker = ProgressTracker(10, "Test operation")
        tracker.start()
        
        for i in range(10):
            tracker.update(1, f"Item {i+1}")
            time.sleep(0.01)
        
        tracker.complete("Test complete")
    
    output = captured_output.getvalue()
    
    # Verify requirements
    assert "[████" in output  # Progress bar present
    assert "100%" in output   # Percentage displayed
    assert "\033[92m" in output  # Success color used
    assert "Test complete" in output  # Completion message
```

## Enforcement Violations

### Forbidden Patterns
- ❌ Operations >5s without progress display
- ❌ Missing color coding (monochrome output)
- ❌ Progress updates less frequent than every 5s
- ❌ Missing ETA for operations >30s
- ❌ Non-standard progress bar formats
- ❌ Missing final status display

### Corrective Actions
When violations are detected:
1. **Stop the operation** immediately
2. **Add progress tracking** using ProgressTracker
3. **Apply standard colors** from color scheme
4. **Test display** before continuing
5. **Document fix** in operation logs

## Tools and Resources

### Integration Scripts
- `tools/progress_display.py` - Core implementation (verify exists before use)
- `tools/progress_utils.py` - Utility functions (verify exists before use)
- `tests/test_progress_display.py` - Test suite (verify exists before use)

> **Skill directory note:** The `progress-display` skill directory is not present in the current `.windsurf/skills/` layout (7 canonical skills as of 2026-04-14). Progress display guidance is covered by the `artifact-management` skill (`SKILL.md` and `progress_display_protocol.md`). References to `.windsurf/skills/progress-display/` are stale and should not be used.

## References

- **Constitutional Rule**: §5.3 Query Timeout & Progress Reporting
- **Skill Definition**: `.windsurf/skills/artifact-management/SKILL.md` (progress display is in `progress_display_protocol.md`)

---

**Remember**: Progress display is not optional - it's a constitutional requirement for any operation exceeding 5 seconds. All long-running operations MUST provide colored progress bars, percentage displays, and ETA calculations.
