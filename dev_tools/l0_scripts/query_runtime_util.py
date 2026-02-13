import concurrent.futures
import functools
import random
import time
from collections.abc import Callable
from typing import Any

from agentic_core.L0_routing.enforcement.v15_runtime_guard import (
    v15_runtime_guard,
)

try:
    from rich.console import Console
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
except ImportError as _err:
    raise ImportError(
        "rich is required for this module. Install with: pip install -e '.[infra]'",
    ) from _err

# Approved SSOT: Singleton console to prevent terminal character interleaving
_console = Console()


@v15_runtime_guard("D.retry_query.query_runtime_util")
# guardian: allow-magic-config
def retry_query(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator to provide exponential backoff with jitter for database queries.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                # guardian: allow-silent-swallow
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        # Exponential backoff with jitter
                        delay = (base_delay * 2**attempt) + random.uniform(0, 1)
                        _console.print(
                            f"[yellow]Retrying query (Attempt {attempt + 1}/{max_retries}) in {delay:.2f}s...[/yellow]",
                        )
                        time.sleep(delay)
            raise last_exception

        return wrapper

    return decorator


# guardian: allow-magic-config
@retry_query(max_retries=3)
def execute_sql(sql: str) -> Any:
    """
    Placeholder database execution function.
    In production, this should be replaced with actual database driver calls.
    """
    # This is a stub implementation - replace with actual database logic
    raise NotImplementedError("execute_sql must be implemented with actual database driver")


# guardian: allow-magic-config
def run_hardened_query(
    query_string: str,
    timeout_seconds: int = 300,
) -> Any:
    """
    Executes a database query with a decoupled animation thread.

    This implementation solves the 'Terminal Hang' problem where the UI stops
    responding during blocking I/O. By utilizing a ThreadPoolExecutor, the
    Rich progress bar remains active (pulsing) even if the database driver
    is waiting on a high-latency network socket.
    """
    with Progress(
        SpinnerColumn(spinner_name="dots", style="bold cyan"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, pulse_style="bright_yellow"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=_console,
        transient=True,  # Auto-clears the bar on completion
    ) as progress:
        task_id = progress.add_task(
            description=f"[bold white]Querying:[/bold white] [blue]{query_string[:35]}...[/blue]",
            total=None,  # Indeterminate mode for SQL
        )

        # CRITICAL FIX: Avoid 'with' context manager to prevent __exit__ blocking on infinite worker loops.
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            future = executor.submit(execute_sql, query_string)
            start_time = time.time()

            while True:
                # Polling wait with 20Hz refresh to keep Rich UI responsive
                # guardian: allow-magic-config
                done, _ = concurrent.futures.wait(
                    [future],
                    timeout=0.05,
                    return_when=concurrent.futures.FIRST_COMPLETED,
                )

                if done:
                    break

                # HARDENING: Explicit timeout check inside polling loop
                if time.time() - start_time > timeout_seconds:
                    future.cancel()
                    # Force non-blocking shutdown: orphan zombie worker to free main thread
                    executor.shutdown(wait=False, cancel_futures=True)
                    raise concurrent.futures.TimeoutError(f"Query timed out after {timeout_seconds}s.")

            result = future.result()
            progress.update(task_id, completed=100, description="[bold green]COMPLETED[/bold green]")
            return result

        except (concurrent.futures.TimeoutError, TimeoutError):
            # Ensure non-blocking shutdown is called even if TimeoutError is raised
            executor.shutdown(wait=False, cancel_futures=True)
            progress.update(task_id, description="[bold red]TIMEOUT[/bold red]")
            _console.print(f"\n[bold red]Alert:[/bold red] Query timed out after {timeout_seconds}s.")
            raise TimeoutError(f"Database operation timed out after {timeout_seconds}s.")
        except Exception as e:
            progress.update(task_id, description="[bold red]FAILED[/bold red]")
            _console.print(f"\n[bold red]Driver Error:[/bold red] {str(e)}")
            raise
        finally:
            # Standard cleanup for successful or failed (non-timeout) cases
            executor.shutdown(wait=False, cancel_futures=True)
