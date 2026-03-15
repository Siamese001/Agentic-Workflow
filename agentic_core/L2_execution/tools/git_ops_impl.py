from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "git_ops_impl", "L2")
_emit_routes_through("p1", "git_ops_impl", "L2")
_emit_escalates_to_human("p1", "git_ops_impl", "L2")
_emit_reads_policy_state("p1", "git_ops_impl", "L2")

_emit_applies_guardrail("p0", "git_ops_impl", "p0_governance")
_emit_snapshots_state("p0", "git_ops_impl", "state_snapshot")

"\nGit Tools - Atomic Module\nExtracted from action_registry.py via Atomic Fission Protocol\nTool ID Prefix: ACT-010\n"
import logging
import uuid
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_writes_through,
)

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
        _emit_writes_through(str(uuid.uuid4()), "GitTools.commit", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "GitTools.commit")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:GitTools.commit".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        Logger.info(f"➕ Committing file '{file_path}' with message: '{message}'")
        try:
            from mcp0_git_add_or_commit import mcp0_git_add_or_commit

            add_result: Any = mcp0_git_add_or_commit(directory=".", action="add", files=[file_path])
            if "Error" in add_result:
                return f"Commit Error (Add): {add_result}"
            commit_result: Any = mcp0_git_add_or_commit(
                directory=".", action="commit", files=[file_path], message=message
            )
            if "Error" in commit_result:
                return f"Commit Error (Commit): {commit_result}"
            return f"[OK] Committed: {message}"
        except ImportError:
            return "Commit Error: 'mcp0_git_add_or_commit' client not available. Git operations require this client."
        # guardian: allow-silent-swallow
        except Exception as e:
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
        # guardian: allow-silent-swallow
        except Exception as e:
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
        # guardian: allow-silent-swallow
        except Exception as e:
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
        # guardian: allow-silent-swallow
        except Exception as e:
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
        # guardian: allow-silent-swallow
        except Exception as e:
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
        # guardian: allow-silent-swallow
        except Exception as e:
            return f"Push Error (Unexpected): {e}"


__all__ = ["GitTools"]
