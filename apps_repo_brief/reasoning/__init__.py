"""
apps_repo_brief.reasoning — Canonical orchestrator package (W5+).

W5 P5.4/P5.6: apps_exec archived. The W1-W4 re-export shim is retired.
ExecOrchestrator now resolves directly from this package.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P5.4
"""
from __future__ import annotations

from apps_repo_brief.reasoning.ExecOrchestrator import ExecOrchestrator  # noqa: F401

__all__ = ["ExecOrchestrator"]
