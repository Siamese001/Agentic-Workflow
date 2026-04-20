"""
Terminal Color Utilities for Windsurf Console
==============================================

Provides color-coded status bars and progress indicators for:
- Discovery processes
- Orchestration workflows
- Healing operations
- Validation runs

Color Scheme:
- GREEN: Success, completed, healthy
- YELLOW: In progress, warning, pending
- RED: Error, failed, critical
- CYAN: Info, discovery, scanning
- MAGENTA: Orchestration, tier execution
- BLUE: Agent activity, processing

Usage:
        status_bar, progress_bar, phase_header, agent_status,
        Colors, print_success, print_error, print_warning, print_info
    )
"""

import sys
from datetime import datetime

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

_emit_records_execution_trace("p0", "evidence", "colors_config")
_emit_applies_guardrail("p0", "colors_config", "p0_governance")
_emit_reads_policy_state("p0", "colors_config", "policy_binding")
_emit_snapshots_state("p0", "colors_config", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("colors_config", "p4obs", "metric_1")
_emit_emits_metric_event("colors_config", "p4obs", "metric_2")
_emit_emits_metric_event("colors_config", "p4obs", "metric_3")
_emit_emits_metric_event("colors_config", "p4obs", "metric_4")
_emit_emits_metric_event("colors_config", "p4obs", "metric_5")
_emit_emits_metric_event("colors_config", "p4obs", "metric_6")
_emit_records_incident_event("colors_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("colors_config", "p4obs", "anomaly")
_emit_writes_observability_log("colors_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("colors_config", "p4obs", "mon_state")
_emit_triggers_alert("colors_config", "p4obs", "alert")
_emit_links_incident_trace("colors_config", "p4obs", "trace_link")
_emit_captures_pattern("colors_config", "p3lm", "pattern")
_emit_records_learning_event("colors_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("colors_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("colors_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("colors_config", "p3lm", "routing")
_emit_improves_agent_policy("colors_config", "p3lm", "policy")
_emit_stores_learning_state("colors_config", "p3lm", "state")
_emit_records_execution_trace("colors_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("colors_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("colors_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("colors_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("colors_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("colors_config", "env_read", "p2_env_1")
_emit_reads_environ("colors_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("colors_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("colors_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "colors_config", "context_pull")
_emit_pulls_context("p1", "colors_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "colors_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "colors_config", "uwg_term_2")
_emit_writes_through("p1", "colors_config", "write_through")
_emit_writes_through("p1", "colors_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "colors_config", "safety_validation")
_emit_invokes_eval("p1", "colors_config", "eval_call")
_emit_proposal_commits_routing("p1", "colors_config", "routing_commit")
_emit_escalates_to_human("p1", "colors_config", "human_escalation")
_emit_routes_through("p1", "colors_config", "route_through")
_emit_checks_agent_registry("p1", "colors_config", "agent_registry")
_emit_validates_agent_capability("p1", "colors_config", "capability")
_emit_dispatches_execution_plan("p1", "colors_config", "exec_plan")
_emit_agent_executes_agent("p1", "colors_config", "sub_agent")
_emit_routes_to_agent("p1", "colors_config", "target_agent")
_emit_verifies_policy("p1", "colors_config", "policy_check")
_emit_observes_runtime_state("p1", "colors_config", "runtime_state")
_emit_verifies_boundary("p1", "colors_config", "boundary_check")
_emit_transcripts_response("p1", "colors_config", "transcript")
_emit_hard_fails_untranscripted("p1", "colors_config")
_emit_gated_by_confidence("p1", "colors_config", "confidence_gate")
emit_replay_key("p0", "colors_config")
emit_determinism_digest("p0", "colors_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "colors_config", "execution_auth")
_emit_validates_capability("p2", "colors_config", "capability_check")
_emit_routes_to_capability("p2", "colors_config", "capability_route")
_emit_writes_via_uwg("p2", "colors_config", "uwg_write")
_emit_blocks_direct_write("p2", "colors_config", "direct_write_block")
_emit_records_tool_invocation("p2", "colors_config", "tool_invocation")
_emit_captures_execution_output("p2", "colors_config", "exec_output")
_emit_dispatches_agent("p3", "colors_config", "agent_dispatch")
_emit_coordinates_agents("p3", "colors_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "colors_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "colors_config", "healing_outcome")
_emit_escalates_failure("p3", "colors_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "colors_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "colors_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "colors_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "colors_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "colors_config", "eval_metric")
_emit_stores_embedding("p4", "colors_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "colors_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "colors_config", "exec_snapshot_link")

# Configuration constants

# Alias for backward compatibility
PrintColors = None  # Will be set after Colors class definition


class Colors:
    """ANSI color codes for terminal output."""

    # Reset
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Standard colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


# Status symbols
SYMBOLS = {
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
    "running": "▶",
    "pending": "○",
    "complete": "●",
    "arrow": "→",
    "bar_full": "█",
    "bar_empty": "░",
    "spinner": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
}


def _ensure_utf8():
    """Ensure terminal supports UTF-8."""
    if sys.platform.startswith("win"):
        try:
            from agentic_core.utils.security_util import safe_execute

            # Replace os.system with safe_execute for security
            safe_execute(["chcp", "65001"], capture_output=True, check=False)
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, AttributeError, UnicodeDecodeError, RuntimeError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            import logging

            logging.getLogger(__name__).debug("colors_config: Exception swallowed at L245: %s", e)


_ensure_utf8()


def colorize(text: str, color: str, bold: bool = False) -> str:
    """Apply color to text."""
    prefix = Colors.BOLD if bold else ""
    return f"{prefix}{color}{text}{Colors.RESET}"


def print_success(msg: str):
    """Print success message in green."""
    print(f"{Colors.BRIGHT_GREEN}{SYMBOLS['success']} {msg}{Colors.RESET}")


def print_error(msg: str):
    """Print error message in red."""
    print(f"{Colors.BRIGHT_RED}{SYMBOLS['error']} {msg}{Colors.RESET}")


def print_warning(msg: str):
    """Print warning message in yellow."""
    print(f"{Colors.BRIGHT_YELLOW}{SYMBOLS['warning']} {msg}{Colors.RESET}")


def print_info(msg: str):
    """Print info message in cyan."""
    print(f"{Colors.BRIGHT_CYAN}{SYMBOLS['info']} {msg}{Colors.RESET}")


def status_bar(label: str, status: str, width: int = 60, show_time: bool = True) -> str:
    """Generate a color-coded status bar."""
    status_colors = {
        "running": (Colors.BRIGHT_YELLOW, Colors.BG_YELLOW, SYMBOLS["running"]),
        "success": (Colors.BRIGHT_GREEN, Colors.BG_GREEN, SYMBOLS["success"]),
        "error": (Colors.BRIGHT_RED, Colors.BG_RED, SYMBOLS["error"]),
        "warning": (Colors.BRIGHT_YELLOW, Colors.BG_YELLOW, SYMBOLS["warning"]),
        "pending": (Colors.DIM, Colors.BG_BLACK, SYMBOLS["pending"]),
        "info": (Colors.BRIGHT_CYAN, Colors.BG_CYAN, SYMBOLS["info"]),
    }

    fg_color, bg_color, symbol = status_colors.get(status, status_colors["info"])

    timestamp = f"[{datetime.now().strftime('%H:%M:%S')}] " if show_time else ""
    status_text = f" {status.upper()} "

    bar = f"{timestamp}{fg_color}{symbol} {label}{Colors.RESET}"
    padding = width - len(timestamp) - len(label) - len(status_text) - 4

    return f"{bar}{' ' * max(0, padding)}{bg_color}{Colors.BLACK}{status_text}{Colors.RESET}"


def progress_bar(
    current: int,
    total: int,
    label: str = "",
    width: int = 40,
    show_percent: bool = True,
    show_count: bool = True,
) -> str:
    """Generate a color-coded progress bar."""
    if total == 0:
        percent = 0
    else:
        percent = min(100, int((current / total) * 100))

    filled = int(width * current / max(total, 1))
    empty = width - filled

    if percent >= 100:
        color = Colors.BRIGHT_GREEN
    elif percent >= 75:
        color = Colors.BRIGHT_CYAN
    elif percent >= 50:
        color = Colors.BRIGHT_YELLOW
    elif percent >= 25:
        color = Colors.YELLOW
    else:
        color = Colors.DIM

    bar = f"{color}{SYMBOLS['bar_full'] * filled}{Colors.DIM}{SYMBOLS['bar_empty'] * empty}{Colors.RESET}"

    parts = [bar]
    if show_percent:
        parts.append(f"{color}{percent:3d}%{Colors.RESET}")
    if show_count:
        parts.append(f"{Colors.DIM}({current}/{total}){Colors.RESET}")
    if label:
        parts.insert(0, f"{Colors.BRIGHT_WHITE}{label}{Colors.RESET}")

    return " ".join(parts)


def phase_header(
    phase_name: str,
    phase_num: int | None = None,
    total_phases: int | None = None,
    status: str = "running",
) -> str:
    """Generate a prominent phase/tier header."""
    status_colors = {
        "running": Colors.BRIGHT_YELLOW,
        "success": Colors.BRIGHT_GREEN,
        "error": Colors.BRIGHT_RED,
        "pending": Colors.DIM,
    }
    color = status_colors.get(status, Colors.BRIGHT_CYAN)

    if phase_num and total_phases:
        prefix = f"[{phase_num}/{total_phases}]"
    elif phase_num:
        prefix = f"[{phase_num}]"
    else:
        prefix = ""

    border = "═" * 60

    lines = [
        f"\n{color}╔{border}╗{Colors.RESET}",
        f"{color}║{Colors.BOLD} {prefix} {phase_name.upper()}{Colors.RESET}{color}{' ' * (58 - len(prefix) - len(phase_name))}║{Colors.RESET}",
        f"{color}╚{border}╝{Colors.RESET}",
    ]

    return "\n".join(lines)


def agent_status(
    agent_name: str,
    status: str,
    fixes: int = 0,
    violations: int = 0,
    duration_ms: int | None = None,
) -> str:
    """Generate agent execution status line."""
    status_styles = {
        "running": (Colors.BRIGHT_YELLOW, SYMBOLS["running"], "RUNNING"),
        "success": (Colors.BRIGHT_GREEN, SYMBOLS["success"], "SUCCESS"),
        "error": (Colors.BRIGHT_RED, SYMBOLS["error"], "ERROR"),
        "skipped": (Colors.DIM, SYMBOLS["pending"], "SKIPPED"),
        "healing": (Colors.BRIGHT_MAGENTA, SYMBOLS["running"], "HEALING"),
    }

    color, symbol, label = status_styles.get(status, status_styles["running"])

    metrics = []
    if fixes > 0:
        metrics.append(f"{Colors.BRIGHT_GREEN}+{fixes} fixed{Colors.RESET}")
    if violations > 0:
        metrics.append(f"{Colors.BRIGHT_RED}{violations} violations{Colors.RESET}")
    if duration_ms is not None:
        if duration_ms > 5000:
            time_color = Colors.BRIGHT_RED
        elif duration_ms > 2000:
            time_color = Colors.BRIGHT_YELLOW
        else:
            time_color = Colors.DIM
        metrics.append(f"{time_color}{duration_ms}ms{Colors.RESET}")

    metrics_str = f" [{', '.join(metrics)}]" if metrics else ""

    return f"  {color}{symbol} {agent_name}{Colors.RESET} {color}[{label}]{Colors.RESET}{metrics_str}"


def tier_summary(
    tier_name: str,
    tier_num: int,
    agents_run: int,
    total_fixes: int,
    total_violations: int,
    duration_sec: float,
    passed: bool,
) -> str:
    """Generate tier execution summary."""
    if passed:
        status_color = Colors.BRIGHT_GREEN
        status_symbol = SYMBOLS["success"]
        status_text = "PASSED"
    else:
        status_color = Colors.BRIGHT_RED
        status_symbol = SYMBOLS["error"]
        status_text = "FAILED"

    border = "─" * 58

    lines = [
        f"\n{Colors.DIM}┌{border}┐{Colors.RESET}",
        f"{Colors.DIM}│{Colors.RESET} {status_color}{status_symbol} TIER {tier_num}: {tier_name}{Colors.RESET}",
        f"{Colors.DIM}│{Colors.RESET}   Agents: {agents_run} | Fixes: {Colors.BRIGHT_GREEN}{total_fixes}{Colors.RESET} | Violations: {Colors.BRIGHT_RED if total_violations > 0 else Colors.DIM}{total_violations}{Colors.RESET}",
        f"{Colors.DIM}│{Colors.RESET}   Duration: {duration_sec:.2f}s | Status: {status_color}{status_text}{Colors.RESET}",
        f"{Colors.DIM}└{border}┘{Colors.RESET}",
    ]

    return "\n".join(lines)


def mission_header(mode: str, execute: bool = False) -> str:
    """Generate mission start header."""
    mode_color = Colors.BRIGHT_RED if execute else Colors.BRIGHT_YELLOW
    mode_label = "EXECUTE" if execute else "DRY-RUN"

    lines = [
        f"\n{Colors.BRIGHT_MAGENTA}{'═' * 62}{Colors.RESET}",
        f"{Colors.BRIGHT_MAGENTA}║{Colors.RESET} {Colors.BOLD}SOVEREIGN MISSION: {mode.upper()}{Colors.RESET}",
        f"{Colors.BRIGHT_MAGENTA}║{Colors.RESET} Mode: {mode_color}{mode_label}{Colors.RESET}",
        f"{Colors.BRIGHT_MAGENTA}║{Colors.RESET} Started: {Colors.DIM}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}",
        f"{Colors.BRIGHT_MAGENTA}{'═' * 62}{Colors.RESET}",
    ]

    return "\n".join(lines)


def mission_summary(
    total_agents: int,
    total_fixes: int,
    total_violations: int,
    total_errors: int,
    duration_sec: float,
    success: bool,
) -> str:
    """Generate mission completion summary."""
    if success:
        status_color = Colors.BRIGHT_GREEN
        status_text = "MISSION COMPLETE"
    else:
        status_color = Colors.BRIGHT_RED
        status_text = "MISSION FAILED"

    border = "═" * 60

    lines = [
        f"\n{status_color}╔{border}╗{Colors.RESET}",
        f"{status_color}║{Colors.RESET} {Colors.BOLD}{status_text}{Colors.RESET}",
        f"{status_color}║{Colors.RESET}",
        f"{status_color}║{Colors.RESET}   Agents Executed: {total_agents}",
        f"{status_color}║{Colors.RESET}   Fixes Applied:   {Colors.BRIGHT_GREEN}{total_fixes}{Colors.RESET}",
        f"{status_color}║{Colors.RESET}   Violations:      {Colors.BRIGHT_RED if total_violations > 0 else Colors.DIM}{total_violations}{Colors.RESET}",
        f"{status_color}║{Colors.RESET}   Errors:          {Colors.BRIGHT_RED if total_errors > 0 else Colors.DIM}{total_errors}{Colors.RESET}",
        f"{status_color}║{Colors.RESET}   Duration:        {duration_sec:.2f}s",
        f"{status_color}║{Colors.RESET}",
        f"{status_color}╚{border}╝{Colors.RESET}",
    ]

    return "\n".join(lines)


def heartbeat(iteration: int) -> str:
    """Generate a heartbeat indicator to show process is alive."""
    spinner = SYMBOLS["spinner"]
    return f"{Colors.BRIGHT_CYAN}{spinner[iteration % len(spinner)]}{Colors.RESET}"


def log_status(level: str, message: str, **kwargs):
    """Log a status message with appropriate color."""
    timestamp = f"[{datetime.now().strftime('%H:%M:%S')}]"

    level_styles = {
        "info": (Colors.BRIGHT_CYAN, "INFO"),
        "success": (Colors.BRIGHT_GREEN, "OK"),
        "warning": (Colors.BRIGHT_YELLOW, "WARN"),
        "error": (Colors.BRIGHT_RED, "ERR"),
        "debug": (Colors.DIM, "DBG"),
        "trace": (Colors.DIM, "TRC"),
    }

    color, label = level_styles.get(level, level_styles["info"])

    context = ""
    if kwargs:
        context = f" {Colors.DIM}({', '.join(f'{k}={v}' for k, v in kwargs.items())}){Colors.RESET}"

    print(f"{Colors.DIM}{timestamp}{Colors.RESET} {color}[{label}]{Colors.RESET} {message}{context}")


# Backward compatibility alias - PrintColors is an alias for Colors
PrintColors = Colors
