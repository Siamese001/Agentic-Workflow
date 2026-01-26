from __future__ import annotations

"""
Git Tools - Atomic Module
Extracted from action_registry.py via Atomic Fission Protocol
Tool ID Prefix: ACT-010
"""
import logging
from typing import Any

Logger: Any = logging.getLogger("ActionRegistry.GitTools")


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
        except Exception as e:
            return f"Status Error (Unexpected): {e}"


__all__ = ["GitTools"]
