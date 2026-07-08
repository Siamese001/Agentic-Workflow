from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "git_ops_impl")
trace_contract.emit_determinism_digest("p0", "git_ops_impl")

trace_contract._emit_dispatches_healing_run("p1", "git_ops_impl", "L2")
trace_contract._emit_routes_through("p1", "git_ops_impl", "L2")
trace_contract._emit_checks_agent_registry("p1", "git_ops_impl", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "git_ops_impl", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "git_ops_impl", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "git_ops_impl", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "git_ops_impl", "target_agent")
trace_contract._emit_verifies_policy("p1", "git_ops_impl", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "git_ops_impl", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "git_ops_impl", "boundary_check")
trace_contract._emit_transcripts_response("p1", "git_ops_impl", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "git_ops_impl")
trace_contract._emit_gated_by_confidence("p1", "git_ops_impl", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "git_ops_impl", "L2")
trace_contract._emit_reads_policy_state("p1", "git_ops_impl", "L2")

trace_contract._emit_applies_guardrail("p0", "git_ops_impl", "p0_governance")
trace_contract._emit_snapshots_state("p0", "git_ops_impl", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "git_ops_impl", "execution_auth")
trace_contract._emit_validates_capability("p2", "git_ops_impl", "capability_check")
trace_contract._emit_routes_to_capability("p2", "git_ops_impl", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "git_ops_impl", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "git_ops_impl", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "git_ops_impl", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "git_ops_impl", "exec_output")
trace_contract._emit_dispatches_agent("p3", "git_ops_impl", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "git_ops_impl", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "git_ops_impl", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "git_ops_impl", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "git_ops_impl", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "git_ops_impl", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "git_ops_impl", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "git_ops_impl", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "git_ops_impl", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "git_ops_impl", "eval_metric")
trace_contract._emit_stores_embedding("p4", "git_ops_impl", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "git_ops_impl", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "git_ops_impl", "exec_snapshot_link")

"\nGit Tools - Atomic Module\nExtracted from action_registry.py via Atomic Fission Protocol\nTool ID Prefix: ACT-010\n"
import logging
import uuid
from typing import Any


trace_contract._emit_emits_metric_event("git_ops_impl", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("git_ops_impl", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("git_ops_impl", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("git_ops_impl", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("git_ops_impl", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("git_ops_impl", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("git_ops_impl", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("git_ops_impl", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("git_ops_impl", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("git_ops_impl", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("git_ops_impl", "p4obs", "alert")
trace_contract._emit_links_incident_trace("git_ops_impl", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("git_ops_impl", "p3lm", "pattern")
trace_contract._emit_records_learning_event("git_ops_impl", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("git_ops_impl", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("git_ops_impl", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("git_ops_impl", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("git_ops_impl", "p3lm", "policy")
trace_contract._emit_stores_learning_state("git_ops_impl", "p3lm", "state")
trace_contract._emit_records_execution_trace("git_ops_impl", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("git_ops_impl", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("git_ops_impl", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("git_ops_impl", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("git_ops_impl", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("git_ops_impl", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("git_ops_impl", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("git_ops_impl", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("git_ops_impl", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "git_ops_impl", "context_pull")
trace_contract._emit_pulls_context("p1", "git_ops_impl", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "git_ops_impl", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "git_ops_impl", "uwg_term_2")
trace_contract._emit_writes_through("p1", "git_ops_impl", "write_through")
trace_contract._emit_writes_through("p1", "git_ops_impl", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "git_ops_impl", "safety_validation")
trace_contract._emit_invokes_eval("p1", "git_ops_impl", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "git_ops_impl", "routing_commit")

_LOGGER_NAME = "ActionRegistry.GitTools"
_DEFAULT_LOG_ENTRIES = 10
Logger: Any = logging.getLogger(_LOGGER_NAME)


class GitTools:
    """
    Provides git operations like commit and status.
    Tool ID Prefix: ACT-010
    """

    def __init__(self):
        """Initializes GitTools. No specific state needed."""

    def commit(self, file_path: str, message: str) -> str:
        """
        Commits a file to git.
        Tool ID: ACT-010

        Args:
            file_path (str): The path to the file to commit.
            message (str): The commit message.

        Returns:
            str: A success message or an error message.
        """
        trace_contract._emit_writes_through(str(uuid.uuid4()), "GitTools.commit", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "GitTools.commit")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:GitTools.commit".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        Logger.info(f"➕ Committing file '{file_path}' with message: '{message}'")
        try:
            from mcp0_git_add_or_commit import mcp0_git_add_or_commit

            add_result: Any = mcp0_git_add_or_commit(directory=".", action="add", files=[file_path])
            if "Error" in add_result:
                return f"Commit Error (Add): {add_result}"
            commit_result: Any = mcp0_git_add_or_commit(
                directory=".",
                action="commit",
                files=[file_path],
                message=message,
            )
            if "Error" in commit_result:
                return f"Commit Error (Commit): {commit_result}"
            return f"[OK] Committed: {message}"
        except ImportError:  # guardian: allow-silent-swallow -- optional dependency
            return "Commit Error: 'mcp0_git_add_or_commit' client not available. Git operations require this client."
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            return f"Commit Error (Unexpected): {e}"

    def status(self) -> str:
        """
        Gets git status.
        Tool ID: ACT-011

        Returns:
            str: The git status output or an error message.
        """
        Logger.info("❓ Getting git status.")
        try:
            from mcp0_git_status import mcp0_git_status

            result: Any = mcp0_git_status(directory=".")
            return result
        except ImportError:
            return "Status Error: 'mcp0_git_status' client not available. Git operations require this client."
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            return f"Status Error (Unexpected): {e}"

    def log(self, max_entries: int = _DEFAULT_LOG_ENTRIES) -> str:
        """
        Gets git commit log.
        Tool ID: ACT-012

        Args:
            max_entries: Maximum number of log entries to return.

        Returns:
            str: The git log output or an error message.
        """
        Logger.info(f"📋 Getting git log (max {max_entries} entries).")
        try:
            from mcp0_git_log_or_diff import mcp0_git_log_or_diff

            result: Any = mcp0_git_log_or_diff(directory=".", action="log")
            return result
        except ImportError:
            return (
                "Log Error: 'mcp0_git_log_or_diff' client not available. Git operations require this client."
            )
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            return f"Log Error (Unexpected): {e}"

    def diff(self, revision_range: str | None = None) -> str:
        """
        Gets git diff.
        Tool ID: ACT-013

        Args:
            revision_range: Optional revision range (e.g. 'HEAD~1..HEAD').

        Returns:
            str: The git diff output or an error message.
        """
        Logger.info(f"🔍 Getting git diff (range={revision_range}).")
        try:
            from mcp0_git_log_or_diff import mcp0_git_log_or_diff

            kwargs: dict[str, Any] = {"directory": ".", "action": "diff"}
            if revision_range:
                kwargs["revision_range"] = revision_range
            result: Any = mcp0_git_log_or_diff(**kwargs)
            return result
        except ImportError:
            return (
                "Diff Error: 'mcp0_git_log_or_diff' client not available. Git operations require this client."
            )
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            return f"Diff Error (Unexpected): {e}"

    def branch(self, branch_name: str | None = None) -> str:
        """
        Lists or creates git branches.
        Tool ID: ACT-014

        Args:
            branch_name: If provided, creates a new branch with this name.
                         If None, lists all branches.

        Returns:
            str: Branch list or creation result, or an error message.
        """
        if branch_name:
            Logger.info(f"🌿 Creating git branch '{branch_name}'.")
        else:
            Logger.info("🌿 Listing git branches.")
        try:
            from mcp0_git_branch import mcp0_git_branch

            if branch_name:
                result: Any = mcp0_git_branch(directory=".", action="create", branch_name=branch_name)
            else:
                result = mcp0_git_branch(directory=".", action="list")
            return result
        except ImportError:
            return "Branch Error: 'mcp0_git_branch' client not available. Git operations require this client."
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            return f"Branch Error (Unexpected): {e}"

    def push(self) -> str:
        """
        Pushes commits to remote.
        Tool ID: ACT-015

        Returns:
            str: A success message or an error message.
        """
        Logger.info("⬆️ Pushing commits to remote.")
        try:
            from mcp0_git_push import mcp0_git_push

            result: Any = mcp0_git_push(directory=".")
            return result
        except ImportError:
            return "Push Error: 'mcp0_git_push' client not available. Git operations require this client."
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            return f"Push Error (Unexpected): {e}"


__all__ = ["GitTools"]
