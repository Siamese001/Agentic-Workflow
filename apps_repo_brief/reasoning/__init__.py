"""
apps_repo_brief.reasoning — Compatibility re-export shim (W1 transition).

Re-exports the legacy apps_exec orchestrator symbols under the new package
namespace so that apps_eval (the one allowed hard-import consumer) can
reference either path during the transition window.

IMPORTANT: This module is a SHIM. The canonical runtime path does NOT invoke
ExecOrchestrator directly — it goes through the agentic_core canonical runner.
apps_eval lazy-imports ExecOrchestrator for dry-run eval scenarios only; those
will be updated to apps_repo_brief scenarios in W1/P1.9.

Shim lifetime: W1 through W4. Retired in W5 once zero-hard-refs gate passes.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P1.2
"""
from __future__ import annotations

# Re-export under the new name so apps_repo_brief.reasoning.ExecOrchestrator
# resolves. apps_eval already has an allowlisted lazy import of the
# apps_exec path; this shim provides the parallel new-namespace path.
from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator  # noqa: F401

__all__ = ["ExecOrchestrator"]
