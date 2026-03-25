# Progress Terminal Protocol

**MANDATORY** for all operations exceeding 5 seconds duration per §5.3 constitutional requirements.

## Core Requirements

### 1. Progress Bar Format

**Standard Format**:
```
[████████████████████████████████] 100% (2500/2500 files) - ETA: 0s
```

**Components**:
- **Bar**: 40 characters wide, using `█` for complete, `░` for remaining
- **Percentage**: Right-aligned, 2 digits + % symbol
- **Count**: Current/Total in parentheses
- **ETA**: Estimated time remaining, formatted as "Xs", "Xm", or "Xh"

### 2. Color Scheme

| Status | ANSI Code | Example | Use Case |
|--------|-----------|---------|----------|
| **Success** | `\033[92m` (Bright Green) | `✅ Complete` | Operation finished successfully |
| **Warning** | `\033[93m` (Bright Yellow) | `⚠️ Slow progress` | Operation slower than expected |
| **Error** | `\033[91m` (Bright Red) | `❌ Failed` | Operation failed or hit error |
| **In-Progress** | `\033[94m` (Bright Blue) | `🔄 Processing` | Currently running |
| **Neutral** | `\033[97m` (Bright White) | `⏸ Queued` | Pending/queued state |

**Color Reset**: Always use `\033[0m` after colored text

### 3. Update Frequency

**Minimum**: Every 5 seconds for operations >5s
**Recommended**: Every 1-2 seconds for better UX
**Maximum**: No more frequent than every 0.5 seconds (avoid flicker)

### 4. Progress Calculation

```python
def format_progress_bar(current, total, width=40):
    """Generate standardized progress bar with colors"""
    percentage = (current / total) * 100
    filled = int(width * current // total)
    bar = '█' * filled + '░' * (width - filled)
    
    # Color based on percentage
    if percentage >= 90:
        color = '\033[92m'  # Green
    elif percentage >= 50:
        color = '\033[94m'  # Blue
    elif percentage >= 25:
        color = '\033[93m'  # Yellow
    else:
        color = '\033[91m'  # Red
    
    return f"{color}[{bar}]\033[0m {percentage:5.1f}% ({current}/{total})"
```

## Implementation Templates

### File System Operations
```python
def scan_with_progress(file_list):
    total = len(file_list)
    for i, file_path in enumerate(file_list, 1):
        # Process file
        process_file(file_path)
        
        # Update progress every 10 files or on last file
        if i % 10 == 0 or i == total:
            progress = format_progress_bar(i, total)
            print(f"\r\033[K{progress}", end='', flush=True)
    print()  # New line when complete
```

### Test Execution
```python
def run_tests_with_progress(test_nodes):
    total = len(test_nodes)
    passed = failed = 0
    
    for i, test_id in enumerate(test_nodes, 1):
        result = run_single_test(test_id)
        if result.passed:
            passed += 1
        else:
            failed += 1
        
        if i % 5 == 0 or i == total:
            progress = format_progress_bar(i, total)
            status = f"✅ {passed} ❌ {failed}"
            print(f"\r\033[K{progress} {status}", end='', flush=True)
    
    final_color = '\033[92m' if failed == 0 else '\033[91m'
    print(f"\n{final_color}Complete: {passed} passed, {failed} failed\033[0m")
```

### ADG Operations
```python
def adg_scan_with_progress(scanner):
    print("🔍 Scanning repository for ADG generation...")
    
    # Module scanning
    modules = scanner.get_module_list()
    total_modules = len(modules)
    
    for i, module in enumerate(modules, 1):
        scanner.scan_module(module)
        
        if i % 50 == 0 or i == total_modules:
            progress = format_progress_bar(i, total_modules)
            print(f"\r\033[K{progress} modules scanned", end='', flush=True)
    
    print("\n🔗 Building dependency graph...")
    # Similar progress for edge building
```

## ETA Calculation

```python
import time

class ETACalculator:
    def __init__(self):
        self.start_time = time.time()
        self.last_update = self.start_time
        self.last_progress = 0
    
    def get_eta(self, current, total):
        now = time.time()
        elapsed = now - self.start_time
        
        if current == 0:
            return "∞"
        
        # Simple linear extrapolation
        rate = current / elapsed
        remaining = total - current
        eta_seconds = remaining / rate if rate > 0 else float('inf')
        
        if eta_seconds < 60:
            return f"{eta_seconds:.0f}s"
        elif eta_seconds < 3600:
            return f"{eta_seconds/60:.1f}m"
        else:
            return f"{eta_seconds/3600:.1f}h"
```

## Error Handling

### Progress Interruption
```python
try:
    for item in long_operation():
        update_progress(item)
except KeyboardInterrupt:
    print(f"\n\033[91m❌ Operation interrupted by user\033[0m")
    raise
except Exception as e:
    print(f"\n\033[91m❌ Operation failed: {e}\033[0m")
    raise
```

### Recovery Mode
```python
def resume_progress(checkpoint_file, total):
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file) as f:
            completed = int(f.read())
        print(f"\033[93m🔄 Resuming from checkpoint: {completed}/{total}\033[0m")
        return completed
    return 0
```

## Integration Requirements

### All Long-Running Operations Must:
1. **Detect duration** >5s before showing progress
2. **Use standard format** with all components
3. **Apply colors** based on operation status
4. **Update frequently** (every 1-5s)
5. **Handle interruption** gracefully
6. **Show final status** with appropriate color

### Forbidden:
- ❌ Silent operations >5s without progress
- ❌ Monochrome output (no colors)
- ❌ Missing ETA for operations >30s
- ❌ Progress updates less frequent than every 5s
- ❌ Inconsistent formats across operations
