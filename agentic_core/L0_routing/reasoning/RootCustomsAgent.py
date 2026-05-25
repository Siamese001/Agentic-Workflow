"""ROOT CUSTOMS AGENT - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L0_routing.utils.root_customs_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W4.2 of agent-deprecation-migration-d7a3f2)
Authorization date: 2026-04-24
W2 archive (2026-05-25): legacy orphan body in archives/agents/2026-05-25/ (90-day cooling = consumer migration window)
Category: deprecated-delegating-shim-with-constants
Canonical replacement: agentic_core.L0_routing.utils.root_customs_util
Consumers at authorization (1):
  - agentic_core/L0_routing/utils/root_customs_util.py (imports ARTIFACT_ROUTING_MAP, TEST_TYPE_SIGNALS, LEGACY_AST_SIGNALS constants FROM the agent - constants must be moved into util before archive)

Policy interpretation (pragmatic constitutional \u00a73): This agent is
self-documented DEPRECATED with an explicit canonical replacement. The 90-day
cooling period serves as the formal consumer migration window. W6 archive
sweep on or after 2026-07-23 will verify zero live consumers via regex grep
BEFORE physical archive. If consumers remain, W6 blocks the archive and
schedules per-consumer follow-up; authorization is NOT revoked but the
archive action is deferred.

Target archive path on or after eligibility date:
  archives/agents/2026-07-23/agentic_core__L0_routing__reasoning__RootCustomsAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/w_final_RootCustomsAgent.json
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.config import get_validated_project_root
from agentic_core.L0_routing.utils.root_customs_util import (
    ASTAnalyzer,
    RoutingDecision,
    analyze_content_signatures,
    determine_routing,
    execute_routing,
    scan_root_directory,
)
from agentic_core.L0_routing.utils.root_customs_util import (
    run_inspection as _run_inspection,
)


class RootCustomsAgent(SovereignBaseAgent):
    """
    DEPRECATED: Enhanced "Customs Agent" - now delegates to root_customs_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L0_routing.utils.root_customs_util directly.
    """

    def __init__(self, project_root: Path | None = None, dry_run: bool = True):
        """Initialize RootCustomsAgent (deprecated, use root_customs_util instead)."""
        resolved_root = project_root or get_validated_project_root()
        super().__init__(project_root=resolved_root)

        warnings.warn(
            "RootCustomsAgent is deprecated. Use agentic_core.L0_routing.utils.root_customs_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.project_root = resolved_root
        self.dry_run = dry_run
        self.routing_decisions: list[RoutingDecision] = []
        self.ast_analyzer = ASTAnalyzer()

    def scan_root_directory(self) -> list[Path]:
        """Scan the project root for files to analyze."""
        return scan_root_directory(self.project_root)

    def check_allowed_patterns(self, file_path: Path) -> bool:
        """Check if file matches any allowed root patterns."""
        from agentic_core.L0_routing.utils.root_customs_util import check_allowed_patterns

        return check_allowed_patterns(file_path)

    def analyze_content_signatures(self, file_path: Path) -> dict[str, Any]:
        """Analyze file content for routing signatures."""
        return analyze_content_signatures(file_path)

    def analyze_ast_signals(self, file_path: Path) -> dict[str, Any]:
        """Analyze Python files for AST-based routing signals."""
        return self.ast_analyzer.analyze_file(file_path)

    def determine_routing(
        self,
        file_path: Path,
        content_matches: dict[str, Any],
        ast_matches: dict[str, Any],
    ) -> RoutingDecision:
        """Determine where a file should be routed using enhanced analysis."""
        return determine_routing(file_path, content_matches, ast_matches)

    def execute_routing(self, decision: RoutingDecision) -> bool:
        """Execute a routing decision."""
        return execute_routing(decision, self.project_root, self.dry_run)

    def run_inspection(self) -> dict[str, Any]:
        """Run complete enhanced root inspection and routing."""
        return _run_inspection(self.project_root, self.dry_run)

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by RootCustomsAgent.

        DEPRECATED: Use root_customs_util.run_inspection instead.
        """
        warnings.warn(
            "RootCustomsAgent.heal() is deprecated. Use root_customs_util.run_inspection instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        file_path = violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")

        try:
            if file_path and violation_type == "file_misplaced":
                _run_inspection(self.project_root, dry_run=False)
                return {
                    "status": "success",
                    "details": f"RootCustomsAgent routed {file_path}",
                    "artifacts": [file_path],
                    "errors": [],
                }
            else:
                return {
                    "status": "skipped",
                    "details": f"RootCustomsAgent heal() not implemented for {violation_type}",
                    "artifacts": [],
                    "errors": [],
                }
        except (ValueError, TypeError, RuntimeError) as e:
            return {
                "status": "failed",
                "details": f"RootCustomsAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }

    def heal_repository(self, *args, **kwargs) -> dict:
        """heal_repository() not implemented for RootCustomsAgent."""
        raise NotImplementedError("heal_repository() not implemented for RootCustomsAgent")


def main():
    """Main entry point - delegates to utility."""
    from agentic_core.L0_routing.utils.root_customs_util import main as _main

    return _main()


if __name__ == "__main__":
    main()

    file_path: Path
