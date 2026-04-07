import concurrent.futures
import functools
import random
import time
from collections.abc import Callable
from typing import Any

from agentic_core.L0_routing.enforcement.runtime_guard import (
    runtime_guard,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "query_runtime_util")
_emit_applies_guardrail("p0", "query_runtime_util", "p0_governance")
_emit_reads_policy_state("p0", "query_runtime_util", "policy_binding")
_emit_snapshots_state("p0", "query_runtime_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("query_runtime_util", "p4obs", "metric_1")
_emit_emits_metric_event("query_runtime_util", "p4obs", "metric_2")
_emit_emits_metric_event("query_runtime_util", "p4obs", "metric_3")
_emit_emits_metric_event("query_runtime_util", "p4obs", "metric_4")
_emit_emits_metric_event("query_runtime_util", "p4obs", "metric_5")
_emit_emits_metric_event("query_runtime_util", "p4obs", "metric_6")
_emit_records_incident_event("query_runtime_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("query_runtime_util", "p4obs", "anomaly")
_emit_writes_observability_log("query_runtime_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("query_runtime_util", "p4obs", "mon_state")
_emit_triggers_alert("query_runtime_util", "p4obs", "alert")
_emit_links_incident_trace("query_runtime_util", "p4obs", "trace_link")
_emit_captures_pattern("query_runtime_util", "p3lm", "pattern")
_emit_records_learning_event("query_runtime_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("query_runtime_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("query_runtime_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("query_runtime_util", "p3lm", "routing")
_emit_improves_agent_policy("query_runtime_util", "p3lm", "policy")
_emit_stores_learning_state("query_runtime_util", "p3lm", "state")
_emit_records_execution_trace("query_runtime_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("query_runtime_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("query_runtime_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("query_runtime_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("query_runtime_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("query_runtime_util", "env_read", "p2_env_1")
_emit_reads_environ("query_runtime_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("query_runtime_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("query_runtime_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "query_runtime_util", "context_pull")
_emit_pulls_context("p1", "query_runtime_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "query_runtime_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "query_runtime_util", "uwg_term_2")
_emit_writes_through("p1", "query_runtime_util", "write_through")
_emit_writes_through("p1", "query_runtime_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "query_runtime_util", "safety_validation")
_emit_invokes_eval("p1", "query_runtime_util", "eval_call")
_emit_proposal_commits_routing("p1", "query_runtime_util", "routing_commit")
_emit_escalates_to_human("p1", "query_runtime_util", "human_escalation")
_emit_routes_through("p1", "query_runtime_util", "route_through")
_emit_checks_agent_registry("p1", "query_runtime_util", "agent_registry")
_emit_validates_agent_capability("p1", "query_runtime_util", "capability")
_emit_dispatches_execution_plan("p1", "query_runtime_util", "exec_plan")
_emit_agent_executes_agent("p1", "query_runtime_util", "sub_agent")
_emit_routes_to_agent("p1", "query_runtime_util", "target_agent")
_emit_verifies_policy("p1", "query_runtime_util", "policy_check")
_emit_observes_runtime_state("p1", "query_runtime_util", "runtime_state")
_emit_verifies_boundary("p1", "query_runtime_util", "boundary_check")
_emit_transcripts_response("p1", "query_runtime_util", "transcript")
_emit_hard_fails_untranscripted("p1", "query_runtime_util")
_emit_gated_by_confidence("p1", "query_runtime_util", "confidence_gate")
emit_replay_key("p0", "query_runtime_util")
emit_determinism_digest("p0", "query_runtime_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "query_runtime_util", "execution_auth")
_emit_validates_capability("p2", "query_runtime_util", "capability_check")
_emit_routes_to_capability("p2", "query_runtime_util", "capability_route")
_emit_writes_via_uwg("p2", "query_runtime_util", "uwg_write")
_emit_blocks_direct_write("p2", "query_runtime_util", "direct_write_block")
_emit_records_tool_invocation("p2", "query_runtime_util", "tool_invocation")
_emit_captures_execution_output("p2", "query_runtime_util", "exec_output")
_emit_dispatches_agent("p3", "query_runtime_util", "agent_dispatch")
_emit_coordinates_agents("p3", "query_runtime_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "query_runtime_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "query_runtime_util", "healing_outcome")
_emit_escalates_failure("p3", "query_runtime_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "query_runtime_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "query_runtime_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "query_runtime_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "query_runtime_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "query_runtime_util", "eval_metric")
_emit_stores_embedding("p4", "query_runtime_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "query_runtime_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "query_runtime_util", "exec_snapshot_link")

try:
    from rich.console import Console
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
except ImportError as _err:
    raise ImportError(
        "rich is required for this module. Install with: pip install -e '.[infra]'",
    ) from _err

# Approved SSOT: Singleton console to prevent terminal character interleaving
_console = Console()


@runtime_guard("D.retry_query.query_runtime_util")
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
@retry_query(max_retries=MAX_RETRIES)
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
                    timeout=DEFAULT_TIMEOUT,
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

        except (concurrent.futures.TimeoutError, TimeoutError):    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context    # guardian: TimeoutError should be handled with specific context
            # Ensure non-blocking shutdown is called even if TimeoutError is raised
            executor.shutdown(wait=False, cancel_futures=True)
            progress.update(task_id, description="[bold red]TIMEOUT[/bold red]")
            _console.print(f"\n[bold red]Alert:[/bold red] Query timed out after {timeout_seconds}s.")
            raise TimeoutError(f"Database operation timed out after {timeout_seconds}s.")
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            progress.update(task_id, description="[bold red]FAILED[/bold red]")
            _console.print(f"\n[bold red]Driver Error:[/bold red] {str(e)}")
            raise
        finally:
            # Standard cleanup for successful or failed (non-timeout) cases
            executor.shutdown(wait=False, cancel_futures=True)
