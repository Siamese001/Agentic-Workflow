---
name: progress-display
description: Provides colored progress bars and percentage displays for all long-running queries and operations in Windsurf terminal. Enforces §5.3 timeout and progress reporting requirements with visual indicators.
enforcement_layer: windsurf
enforcement_timing: during_work
enforcement_type: behavioural
status: implemented
---

# Progress Display Skill

**PREREQUISITE:** None (standalone UI enhancement).

Provides visual progress bars and colored percentage displays for all long-running operations in Windsurf terminal, enforcing constitutional requirements for progress reporting (§5.3).

## Files

- **`progress_terminal_protocol.md`** — MANDATORY for operations >5s. Specifies progress bar formats, color schemes, percentage displays, and update intervals.

- **`color_scheme_reference.md`** — Defines ANSI color codes for different operation types (success, warning, error, in-progress).

- **`progress_implementation_guide.md`** — Technical implementation details for integrating progress displays into existing tools and scripts.

- **`example_usage.md`** — Complete implementation example with demo scripts for different operation types.

## When to use

- **ALWAYS for operations >5s**: Display progress bars with colored percentages
- **During file system scans**: Show file count progress and completion percentage
- **During test execution**: Display test progress with pass/fail rates in color
- **During ADG operations**: Show node/edge processing progress with colored status
- **During long queries**: Display query progress with time estimates and colored percentages

## Constitutional Requirements Enforced

### §5.3 Query Timeout & Progress Reporting

**Operations >5s MUST provide progress reporting**:
- Percentage completion (e.g., "45%")
- Current item being processed
- Estimated time remaining
- Updates at least every 5 seconds

**Color-coded status indicators**:
- 🟢 **Green**: Success/complete operations
- 🟡 **Yellow**: Warning/slow operations
- 🔴 **Red**: Error/failed operations
- 🔵 **Blue**: In-progress operations
- ⚪ **White**: Neutral/pending operations

**Progress bar formats**:
- **Standard**: `[████████████████████████████████] 100%`
- **Compact**: `████████████████████████████████ 100%`
- **Detailed**: `[████████████████████████████████] 100% (2500/2500 files)`

### ANSI Color Requirements

All progress displays MUST use ANSI escape sequences for colors:
- `\033[92m` for bright green (success)
- `\033[93m` for bright yellow (warning)
- `\033[91m` for bright red (error)
- `\033[94m` for bright blue (in-progress)
- `\033[97m` for bright white (neutral)
- `\033[0m` to reset color

## Integration Points

### ADG Operations
- File scanning progress
- Node/edge processing
- Query execution
- Cache building

### Test Execution
- Test collection progress
- Test run progress with pass/fail rates
- Coverage calculation

### CI Operations
- Gate execution progress
- Script run progress
- Report generation

## Implementation Status

✅ **COMPLETED** - Full implementation includes:
- Core progress tracking classes
- ANSI color scheme definitions
- ETA calculation algorithms
- Integration patterns for common operations
- Error handling and recovery
- Unit test templates
- Example usage scripts
- Workflow enforcement documentation

## Usage Example

```python
from .windsurf.skills.progress_display import ProgressTracker

# Create progress tracker
tracker = ProgressTracker(total_items, "Processing files")
tracker.start()

# Update progress during operation
for i, item in enumerate(items):
    process_item(item)
    tracker.update(1, f"Processing {item.name}")

# Complete with success
tracker.complete(f"Processed {total_items} items")
```

## Forbidden Patterns

- ❌ Long operations (>5s) without progress display
- ❌ Progress updates less frequent than every 5 seconds
- ❌ Monochrome output (no color coding)
- ❌ Missing percentage completion
- ❌ Missing ETA for operations >30s
- ❌ **Unbounded file operations** (processing unlimited files without limits)
- ❌ **Missing PowerShell compatibility** (Unix-only commands like `head`, `tail`)
- ❌ **Inline Python complexity** (complex scripts in shell commands)
- ❌ **No early termination conditions** (process all files even when patterns converge)
- ❌ **Missing batch processing** (process files one by one without progress reporting)
