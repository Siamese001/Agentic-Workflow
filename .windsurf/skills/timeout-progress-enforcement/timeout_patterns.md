# Timeout Implementation Patterns

## Cross-Platform Timeout Patterns

### Pattern 1: subprocess with timeout (Recommended for commands)

```python
import subprocess

def run_command_with_timeout(cmd: list[str], timeout: int) -> subprocess.CompletedProcess:
    """Run command with timeout - works on all platforms."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace"
        )
        return result
    except subprocess.TimeoutExpired as e:
        raise TimeoutError(f"Command {' '.join(cmd)} exceeded {timeout}s timeout") from e
```

### Pattern 2: threading.Timer (Cross-platform)

```python
import threading
from typing import Callable, Any

class TimeoutGuard:
    """Cross-platform timeout guard using threading."""

    def __init__(self, seconds: int, operation: str):
        self.seconds = seconds
        self.operation = operation
        self.timer = None

    def __enter__(self):
        def timeout_handler():
            raise TimeoutError(f"{self.operation} exceeded {self.seconds}s timeout")

        self.timer = threading.Timer(self.seconds, timeout_handler)
        self.timer.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.timer:
            self.timer.cancel()
        return False

# Usage
with TimeoutGuard(30, "file processing"):
    process_large_file(path)
```

### Pattern 3: concurrent.futures (For parallel operations)

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Callable, Any

def execute_with_timeout(func: Callable, timeout: int, *args, **kwargs) -> Any:
    """Execute function with timeout using futures."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            future.cancel()
            raise TimeoutError(f"{func.__name__} exceeded {timeout}s timeout")
```

### Pattern 4: signal (Unix/Linux only - NOT for Windows)

```python
import signal
from contextlib import contextmanager

# WARNING: Only works on Unix/Linux, NOT Windows
@contextmanager
def timeout_guard_unix(seconds: int, operation: str):
    """Unix-only timeout guard using signals."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"{operation} exceeded {seconds}s timeout")

    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
```

## Timeout Ranges by Operation Type

### Fast Queries (5-30 seconds)

```python
# File reads
TIMEOUT_FILE_READ = 10

# Simple grep/search
TIMEOUT_GREP = 15

# Single file AST parse
TIMEOUT_AST_PARSE = 20

# JSON/YAML config load
TIMEOUT_CONFIG_LOAD = 5
```

### Medium Queries (30-120 seconds)

```python
# Dependency graph construction
TIMEOUT_DEP_GRAPH = 90

# Test collection
TIMEOUT_TEST_COLLECT = 60

# Multi-file AST analysis
TIMEOUT_MULTI_AST = 120

# Database queries
TIMEOUT_DB_QUERY = 45
```

### Heavy Queries (120-600 seconds)

```python
# Full repository analysis
TIMEOUT_FULL_REPO_ANALYSIS = 300

# Multi-file refactor planning
TIMEOUT_REFACTOR_PLAN = 180

# Large test suite execution
TIMEOUT_FULL_TEST_SUITE = 600

# Comprehensive dependency scan
TIMEOUT_FULL_DEP_SCAN = 240
```

### External API Calls (10-60 seconds)

```python
# HTTP requests
TIMEOUT_HTTP_REQUEST = 30

# API calls with retry
TIMEOUT_API_WITH_RETRY = 60

# File downloads
TIMEOUT_FILE_DOWNLOAD = 45

# External service health check
TIMEOUT_HEALTH_CHECK = 10
```

## Nested Timeout Pattern

```python
def analyze_repository_with_nested_timeouts(repo_path: str) -> dict:
    """Repository analysis with nested timeouts."""

    # Overall operation timeout
    OVERALL_TIMEOUT = 300

    with TimeoutGuard(OVERALL_TIMEOUT, "repository analysis"):
        results = {}

        # Each sub-operation has its own timeout
        with TimeoutGuard(60, "file discovery"):
            files = discover_files(repo_path)

        with TimeoutGuard(120, "AST parsing"):
            ast_data = parse_all_files(files)

        with TimeoutGuard(90, "dependency graph"):
            dep_graph = build_graph(ast_data)

        results["files"] = files
        results["ast"] = ast_data
        results["graph"] = dep_graph

        return results
```

## Timeout with Retry Pattern

```python
import time
from typing import Callable, Any

def execute_with_timeout_and_retry(
    func: Callable,
    timeout: int,
    max_retries: int = 3,
    backoff: float = 1.5,
    *args,
    **kwargs
) -> Any:
    """Execute with timeout and exponential backoff retry."""

    for attempt in range(max_retries):
        try:
            return execute_with_timeout(func, timeout, *args, **kwargs)
        except TimeoutError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = backoff ** attempt
            time.sleep(wait_time)

    raise TimeoutError(f"{func.__name__} failed after {max_retries} attempts")
```

## Timeout Configuration Class

```python
from dataclasses import dataclass
from enum import Enum

class OperationType(Enum):
    FAST_QUERY = "fast_query"
    MEDIUM_QUERY = "medium_query"
    HEAVY_QUERY = "heavy_query"
    EXTERNAL_API = "external_api"

@dataclass
class TimeoutConfig:
    """Centralized timeout configuration."""

    # Fast queries
    FILE_READ: int = 10
    GREP_SEARCH: int = 15
    AST_PARSE_SINGLE: int = 20
    CONFIG_LOAD: int = 5

    # Medium queries
    DEP_GRAPH: int = 90
    TEST_COLLECT: int = 60
    MULTI_AST: int = 120
    DB_QUERY: int = 45

    # Heavy queries
    FULL_REPO_ANALYSIS: int = 300
    REFACTOR_PLAN: int = 180
    FULL_TEST_SUITE: int = 600
    FULL_DEP_SCAN: int = 240

    # External API
    HTTP_REQUEST: int = 30
    API_WITH_RETRY: int = 60
    FILE_DOWNLOAD: int = 45
    HEALTH_CHECK: int = 10

    @classmethod
    def get_timeout(cls, operation_type: OperationType, operation_name: str) -> int:
        """Get timeout for specific operation."""
        config = cls()

        if operation_type == OperationType.FAST_QUERY:
            return getattr(config, operation_name.upper(), 15)
        elif operation_type == OperationType.MEDIUM_QUERY:
            return getattr(config, operation_name.upper(), 60)
        elif operation_type == OperationType.HEAVY_QUERY:
            return getattr(config, operation_name.upper(), 180)
        elif operation_type == OperationType.EXTERNAL_API:
            return getattr(config, operation_name.upper(), 30)

        return 60  # Default fallback

# Usage
timeout = TimeoutConfig.get_timeout(OperationType.MEDIUM_QUERY, "DEP_GRAPH")
with TimeoutGuard(timeout, "dependency graph"):
    build_graph()
```

## Evidence Documentation Pattern

```python
def document_timeout_in_evidence(
    operation: str,
    timeout: int,
    actual_duration: float,
    timeout_triggered: bool,
    total_items: int,
    completed_items: int
) -> str:
    """Generate timeout documentation for evidence files."""

    return f"""## TIMEOUT_CONFIGURATION

- Operation: {operation}
- Timeout: {timeout}s
- Timeout triggered: {"yes" if timeout_triggered else "no"}
- Progress reporting: enabled
- Total items: {total_items}
- Completed items: {completed_items}
- Duration: {actual_duration:.2f}s
- Completion rate: {(completed_items/total_items*100):.1f}%
"""
```

## References

- Constitutional Rule: `.windsurf/rules/.windsurfrules` §9.1
- Cross-platform compatibility: Use subprocess.run() or threading-based patterns
- Windows compatibility: Avoid signal-based timeouts
