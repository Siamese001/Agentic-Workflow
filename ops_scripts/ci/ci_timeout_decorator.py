#!/usr/bin/env python3
"""
CI Timeout Decorator with RCA Generation

Provides timeout protection for all CI operations with automatic RCA generation
on failures. Prevents CI hangs and provides diagnostic context for debugging.

Usage:
    from ops_scripts.ci.ci_timeout_decorator import ci_timeout, generate_rca

    @ci_timeout(seconds=60, operation_name="Anti-Pattern Scan")
    def run_scanner():
        # CI operation code
        pass
"""

import _thread
import functools
import signal
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

# Project root for RCA storage
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RCA_DIR = PROJECT_ROOT / "docs" / "reports" / "plans"


class TimeoutError(Exception):
    """Raised when a CI operation times out."""

    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutError("CI operation exceeded timeout limit")


class _InterruptFallbackTimer:
    """Cross-platform fallback that interrupts the main thread after a deadline."""

    def __init__(self, seconds: int):
        self.seconds = seconds
        self.fired = False
        self._timer: threading.Timer | None = None

    def start(self) -> None:
        def _fire() -> None:
            self.fired = True
            _thread.interrupt_main()

        self._timer = threading.Timer(self.seconds, _fire)
        self._timer.daemon = True
        self._timer.start()

    def cancel(self) -> None:
        if self._timer is not None:
            self._timer.cancel()


def ci_timeout(seconds: int = 300, operation_name: str = "CI Operation"):
    """
    Decorator to add timeout protection to CI operations.

    Args:
        seconds: Timeout in seconds (default: 5 minutes)
        operation_name: Name of the operation for RCA reporting

    Returns:
        Decorated function with timeout protection
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.monotonic()
            old_handler = None
            fallback_timer: _InterruptFallbackTimer | None = None
            use_signal_timeout = (
                sys.platform != "win32" and threading.current_thread() is threading.main_thread()
            )
            use_interrupt_fallback = (
                not use_signal_timeout and threading.current_thread() is threading.main_thread()
            )

            # Set up timeout signal (Unix-like systems)
            if use_signal_timeout:
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(seconds)
            elif use_interrupt_fallback:
                fallback_timer = _InterruptFallbackTimer(seconds)
                fallback_timer.start()

            try:
                result = func(*args, **kwargs)
                elapsed = time.monotonic() - start_time
                print(f"✅ {operation_name} completed in {elapsed:.2f}s")
                return result

            except KeyboardInterrupt as e:
                if use_interrupt_fallback and fallback_timer is not None and fallback_timer.fired:
                    elapsed = time.monotonic() - start_time
                    rca_path = generate_rca(
                        operation_name=operation_name,
                        error_type="TIMEOUT",
                        error_message=f"Operation exceeded {seconds}s timeout limit",
                        elapsed_time=elapsed,
                        context={
                            "function": func.__name__,
                            "timeout_limit": seconds,
                            "timeout_backend": "interrupt_main_fallback",
                            "args": str(args)[:200],
                            "kwargs": str(kwargs)[:200],
                        },
                    )

                    print(f"❌ {operation_name} TIMEOUT after {elapsed:.2f}s")
                    print(f"📄 RCA generated: {rca_path}")
                    raise TimeoutError("CI operation exceeded timeout limit") from e
                raise

            except TimeoutError as e:  # guardian: TimeoutError should be handled with specific context
                elapsed = time.monotonic() - start_time

                # Generate RCA for timeout
                rca_path = generate_rca(
                    operation_name=operation_name,
                    error_type="TIMEOUT",
                    error_message=f"Operation exceeded {seconds}s timeout limit",
                    elapsed_time=elapsed,
                    context={
                        "function": func.__name__,
                        "timeout_limit": seconds,
                        "args": str(args)[:200],
                        "kwargs": str(kwargs)[:200],
                    },
                )

                print(f"❌ {operation_name} TIMEOUT after {elapsed:.2f}s")
                print(f"📄 RCA generated: {rca_path}")
                raise

            except Exception as e:  # guardian: allow-broad-exception -- timeout decorator must catch all exception types to generate RCA before re-raising; no shared catchable base exists across decorated functions
                elapsed = time.monotonic() - start_time

                # Generate RCA for error
                rca_path = generate_rca(
                    operation_name=operation_name,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    elapsed_time=elapsed,
                    traceback_info=traceback.format_exc(),
                    context={
                        "function": func.__name__,
                        "args": str(args)[:200],
                        "kwargs": str(kwargs)[:200],
                    },
                )

                print(f"❌ {operation_name} FAILED after {elapsed:.2f}s")
                print(f"📄 RCA generated: {rca_path}")
                raise
            finally:
                if fallback_timer is not None:
                    fallback_timer.cancel()
                if use_signal_timeout and old_handler is not None:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)

        return wrapper

    return decorator


def generate_rca(
    operation_name: str,
    error_type: str,
    error_message: str,
    elapsed_time: float,
    traceback_info: str | None = None,
    context: dict | None = None,
) -> Path:
    """
    Generate RCA (Root Cause Analysis) report for CI failures.

    Args:
        operation_name: Name of the failed operation
        error_type: Type of error (TIMEOUT, Exception name, etc.)
        error_message: Error message
        elapsed_time: Time elapsed before failure
        traceback_info: Full traceback if available
        context: Additional context information

    Returns:
        Path to generated RCA file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = operation_name.lower().replace(" ", "_").replace("/", "_")
    rca_filename = f"RCA_ci_{safe_name}_{error_type.lower()}_{timestamp}.md"
    rca_path = RCA_DIR / rca_filename

    # Ensure RCA directory exists
    RCA_DIR.mkdir(parents=True, exist_ok=True)

    # Generate RCA content
    rca_content = f"""# CI Failure RCA: {operation_name}

**Timestamp**: {datetime.now().isoformat()}
**Operation**: {operation_name}
**Error Type**: {error_type}
**Elapsed Time**: {elapsed_time:.2f}s

## Error Summary

{error_message}

## Context

"""

    if context:
        for key, value in context.items():
            rca_content += f"- **{key}**: {value}\n"

    if traceback_info:
        rca_content += f"""
## Full Traceback

```
{traceback_info}
```
"""

    rca_content += """
## Diagnostic Steps

1. **Review Operation Logs**: Check CI output for detailed error messages
2. **Check Resource Usage**: Verify system resources (CPU, memory, disk)
3. **Validate Inputs**: Ensure all input files and configurations are valid
4. **Test Locally**: Run the operation locally with verbose logging
5. **Check Dependencies**: Verify all required dependencies are available

## Recommended Actions

"""

    if error_type == "TIMEOUT":
        rca_content += """
### Timeout-Specific Actions

1. **Increase Timeout Limit**: If operation is legitimately slow, increase timeout
2. **Optimize Operation**: Profile and optimize the slow operation
3. **Add Progress Reporting**: Implement progress indicators to track execution
4. **Check for Infinite Loops**: Review code for potential infinite loops
5. **Verify File Limits**: Ensure file scanning has appropriate limits

### Prevention

- Add file count limits to scanning operations
- Implement progress reporting every N items
- Use early termination for large datasets
- Cache results where appropriate
"""
    else:
        rca_content += """
### Error-Specific Actions

1. **Fix Root Cause**: Address the specific error identified in traceback
2. **Add Error Handling**: Implement proper exception handling
3. **Validate Inputs**: Add input validation before processing
4. **Add Logging**: Increase logging verbosity for debugging
5. **Test Edge Cases**: Add tests for error conditions

### Prevention

- Add comprehensive error handling
- Validate all inputs before processing
- Implement graceful degradation
- Add unit tests for error paths
"""

    rca_content += """
## Related Documentation

- CI Guardrail Strategy: `docs/reports/plans/ci-guardrail-enforcement-strategies-9f4e1d.md`
- Timeout Recovery: `.windsurf/workflows/adg-timeout-recovery.md`
- Progress Enforcement: `.windsurf/workflows/timeout-progress-enforcement.md`

## Status

- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Tests added
- [ ] Documentation updated
- [ ] Verified in CI

---
*Auto-generated RCA by CI timeout decorator*
"""

    # Write RCA file
    rca_path.write_text(rca_content, encoding="utf-8")

    return rca_path


def ci_progress_reporter(total: int, operation_name: str = "Processing"):
    """
    Context manager for progress reporting in CI operations.

    Usage:
        with ci_progress_reporter(total=1000, operation_name="Scanning files") as reporter:
            for i, item in enumerate(items):
                reporter.update(i)
                # process item
    """

    class ProgressReporter:
        def __init__(self, total: int, operation_name: str):
            self.total = total
            self.operation_name = operation_name
            self.start_time = time.monotonic()
            self.last_report = 0

        def update(self, current: int):
            """Update progress and report every 10%."""
            if current == 0:
                return

            percent = (current / self.total) * 100

            # Report every 10%
            if percent >= self.last_report + 10:
                elapsed = time.monotonic() - self.start_time
                rate = current / elapsed if elapsed > 0 else 0
                eta = (self.total - current) / rate if rate > 0 else 0

                print(
                    f"📊 {self.operation_name}: {current}/{self.total} ({percent:.1f}%) - "
                    f"{rate:.1f} items/s - ETA: {eta:.1f}s"
                )

                self.last_report = int(percent / 10) * 10

        def __enter__(self):
            print(f"🚀 Starting {self.operation_name} ({self.total} items)")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            elapsed = time.monotonic() - self.start_time
            if exc_type is None:
                print(f"✅ {self.operation_name} completed in {elapsed:.2f}s")
            else:
                print(f"❌ {self.operation_name} failed after {elapsed:.2f}s")
            return False

    return ProgressReporter(total, operation_name)
