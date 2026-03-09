# Progress Reporting Implementation Patterns

## Core Progress Bar Patterns

### Pattern 1: Basic tqdm Progress Bar

```python
from tqdm import tqdm

def process_items_with_progress(items: list) -> list:
    """Process items with basic progress bar."""
    results = []

    with tqdm(total=len(items), desc="Processing", unit="item") as pbar:
        for item in items:
            result = process_single_item(item)
            results.append(result)
            pbar.update(1)

    return results
```

### Pattern 2: Progress Bar with ETA

```python
from tqdm import tqdm

def analyze_files_with_eta(file_paths: list[str]) -> dict:
    """Analyze files with progress and ETA."""
    results = {}

    pbar = tqdm(
        total=len(file_paths),
        desc="Analyzing files",
        unit="file",
        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
    )

    for file_path in file_paths:
        results[file_path] = analyze_file(file_path)
        pbar.update(1)

    pbar.close()
    return results
```

### Pattern 3: Nested Progress Bars

```python
from tqdm import tqdm

def process_batches_with_nested_progress(batches: list[list]) -> list:
    """Process batches with nested progress bars."""
    all_results = []

    # Outer progress bar for batches
    with tqdm(total=len(batches), desc="Batches", position=0) as pbar_batch:
        for batch in batches:
            batch_results = []

            # Inner progress bar for items in batch
            with tqdm(total=len(batch), desc="Items", position=1, leave=False) as pbar_item:
                for item in batch:
                    result = process_item(item)
                    batch_results.append(result)
                    pbar_item.update(1)

            all_results.extend(batch_results)
            pbar_batch.update(1)

    return all_results
```

### Pattern 4: Manual Progress Updates

```python
from tqdm import tqdm
import time

def long_running_operation_with_manual_progress(total_steps: int) -> None:
    """Long operation with manual progress tracking."""

    with tqdm(total=total_steps, desc="Operation", unit="step") as pbar:
        for step in range(total_steps):
            # Perform work
            perform_step(step)

            # Manual progress update
            pbar.set_postfix({
                'current': step,
                'status': get_status(step)
            })
            pbar.update(1)
```

## Progress Reporting Requirements

### Minimum Update Frequency

```python
import time
from tqdm import tqdm

def enforce_minimum_update_frequency(items: list, min_interval: float = 5.0) -> list:
    """Ensure progress updates at minimum frequency."""
    results = []
    last_update = time.time()

    with tqdm(total=len(items), desc="Processing", unit="item") as pbar:
        for i, item in enumerate(items):
            result = process_item(item)
            results.append(result)

            current_time = time.time()
            if current_time - last_update >= min_interval:
                pbar.update(i - pbar.n)  # Update to current position
                last_update = current_time

        pbar.update(len(items) - pbar.n)  # Final update to 100%

    return results
```

### Progress with Phase Transitions

```python
from tqdm import tqdm
from enum import Enum

class Phase(Enum):
    DISCOVERY = "Discovery"
    PARSING = "Parsing"
    ANALYSIS = "Analysis"
    VALIDATION = "Validation"

def multi_phase_operation_with_progress(data: dict) -> dict:
    """Multi-phase operation with phase transition progress."""

    phases = [Phase.DISCOVERY, Phase.PARSING, Phase.ANALYSIS, Phase.VALIDATION]
    total_work = sum(len(data.get(p.name.lower(), [])) for p in phases)

    results = {}

    with tqdm(total=total_work, desc="Overall", unit="item") as pbar:
        for phase in phases:
            phase_data = data.get(phase.name.lower(), [])
            pbar.set_description(f"{phase.value}")

            phase_results = []
            for item in phase_data:
                result = process_for_phase(item, phase)
                phase_results.append(result)
                pbar.update(1)

            results[phase.name] = phase_results

    return results
```

## Progress Format Requirements

### Standard Format (§9.2)

```python
from tqdm import tqdm

def standard_progress_format(items: list) -> list:
    """Progress bar with standard format per §9.2."""

    # Format: [████████░░░░░░░░░░░░] 40% | Processing: <item> | ETA: <time>

    results = []

    with tqdm(
        total=len(items),
        desc="Processing",
        unit="item",
        bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
    ) as pbar:
        for item in items:
            pbar.set_postfix_str(f"Current: {item}")
            result = process_item(item)
            results.append(result)
            pbar.update(1)

    return results
```

### Custom Progress Display

```python
from tqdm import tqdm

class ProgressReporter:
    """Custom progress reporter with percentage completion."""

    def __init__(self, total: int, description: str):
        self.total = total
        self.current = 0
        self.description = description
        self.pbar = tqdm(
            total=total,
            desc=description,
            unit="item",
            bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}'
        )

    def update(self, n: int = 1, current_item: str = None):
        """Update progress with optional current item description."""
        self.current += n

        if current_item:
            self.pbar.set_postfix_str(f"Processing: {current_item}")

        self.pbar.update(n)

    def set_phase(self, phase: str):
        """Update phase description."""
        self.pbar.set_description(f"{self.description} - {phase}")

    def complete(self):
        """Mark progress as complete."""
        remaining = self.total - self.current
        if remaining > 0:
            self.pbar.update(remaining)
        self.pbar.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.complete()
        return False

# Usage
with ProgressReporter(100, "Analysis") as progress:
    for i, item in enumerate(items):
        progress.update(1, current_item=f"item_{i}")
```

## Integration with Timeout

### Combined Timeout + Progress Pattern

```python
from tqdm import tqdm
import subprocess
from contextlib import contextmanager

@contextmanager
def timeout_with_progress(timeout: int, total_items: int, operation: str):
    """Combined timeout guard and progress reporting."""

    class TimeoutProgress:
        def __init__(self):
            self.pbar = tqdm(
                total=total_items,
                desc=operation,
                unit="item",
                bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [Timeout: {postfix}]'
            )
            self.pbar.set_postfix_str(f"{timeout}s")

        def update(self, n: int = 1):
            self.pbar.update(n)

        def close(self):
            self.pbar.close()

    progress = TimeoutProgress()

    try:
        yield progress
    finally:
        progress.close()

# Usage
with timeout_with_progress(120, len(files), "Processing files") as progress:
    for file in files:
        with subprocess.Popen(..., timeout=120) as proc:
            process_file(file)
            progress.update(1)
```

## AST Dependency Graph Progress (§0, §3.4)

```python
from tqdm import tqdm

def build_dependency_graph_with_progress(file_paths: list[str]) -> dict:
    """Build AST dependency graph with detailed progress."""

    graph = {"nodes": {}, "edges": []}

    # Phase 1: File discovery
    with tqdm(total=len(file_paths), desc="Discovering files", unit="file") as pbar:
        discovered = []
        for path in file_paths:
            if is_python_file(path):
                discovered.append(path)
            pbar.update(1)

    # Phase 2: AST parsing
    with tqdm(total=len(discovered), desc="Parsing AST", unit="file") as pbar:
        for path in discovered:
            ast_data = parse_ast(path)
            graph["nodes"][path] = ast_data
            pbar.update(1)

    # Phase 3: Edge extraction
    total_edges = len(discovered) * len(discovered)  # Worst case
    with tqdm(total=len(discovered), desc="Extracting edges", unit="file") as pbar:
        for source in discovered:
            edges = extract_edges(source, graph["nodes"])
            graph["edges"].extend(edges)
            pbar.update(1)

    return graph
```

## Test Collection Progress (§1, §5.2)

```python
from tqdm import tqdm

def collect_tests_with_progress(test_dirs: list[str]) -> dict:
    """Collect tests with progress reporting."""

    collected = {"total": 0, "by_dir": {}}

    with tqdm(total=len(test_dirs), desc="Collecting tests", unit="dir") as pbar:
        for test_dir in test_dirs:
            pbar.set_postfix_str(f"Current: {test_dir}")

            tests = discover_tests_in_dir(test_dir)
            collected["by_dir"][test_dir] = tests
            collected["total"] += len(tests)

            pbar.update(1)

    return collected
```

## Evidence Generation Progress (§2)

```python
from tqdm import tqdm
import subprocess

def generate_evidence_with_progress(commands: list[str]) -> list[str]:
    """Generate evidence with command execution progress."""

    evidence_lines = []

    with tqdm(total=len(commands), desc="Executing commands", unit="cmd") as pbar:
        for i, cmd in enumerate(commands):
            pbar.set_postfix_str(f"Command {i+1}/{len(commands)}")

            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=30,
                encoding="utf-8",
                errors="replace"
            )

            evidence_lines.append(f"## Command: {cmd}")
            evidence_lines.append(result.stdout)

            pbar.update(1)

    return evidence_lines
```

## Progress Logging Pattern

```python
from tqdm import tqdm
import logging

def process_with_progress_and_logging(items: list) -> list:
    """Process items with both progress bar and logging."""

    logger = logging.getLogger(__name__)
    results = []

    with tqdm(total=len(items), desc="Processing", unit="item") as pbar:
        for i, item in enumerate(items):
            try:
                result = process_item(item)
                results.append(result)
                logger.debug(f"Processed item {i+1}/{len(items)}: {item}")
            except Exception as e:
                logger.error(f"Failed to process item {i+1}: {e}")
                pbar.set_postfix_str(f"ERROR: {str(e)[:30]}")
            finally:
                pbar.update(1)

    return results
```

## Progress Documentation for Evidence

```python
def document_progress_in_evidence(
    operation: str,
    total_items: int,
    completed_items: int,
    duration: float,
    phases: list[str] = None
) -> str:
    """Generate progress documentation for evidence files."""

    completion_pct = (completed_items / total_items * 100) if total_items > 0 else 0

    doc = f"""## PROGRESS_REPORTING

- Operation: {operation}
- Total items: {total_items}
- Completed items: {completed_items}
- Completion: {completion_pct:.1f}%
- Duration: {duration:.2f}s
- Rate: {completed_items/duration:.2f} items/sec
"""

    if phases:
        doc += "\n### Phases\n"
        for phase in phases:
            doc += f"- {phase}\n"

    return doc
```

## References

- Constitutional Rule: `.windsurf/rules/.windsurfrules` §9.2
- Progress format requirement: `[████████░░░░░░░░░░░░] 40% | Processing: <item> | ETA: <time>`
- Update frequency: Every 5s for ops >30s, every 10s for ops >120s
