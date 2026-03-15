from __future__ import annotations

"\nProactive Fission Scanner - L3 Orchestration\n\nScans L4 State for structural patterns matching known 'Critical Bloat' profiles.\nIdentifies files likely to cause Key 41/42 violations before they fail.\n\nStrategy:\n- Scan repository for high-gravity files (>600 lines)\n- Use Brave Search for modular design patterns\n- Use Pinecone to find structural twins\n- Create pre-emptive refactor proposals\n- Enable proactive architectural governance\n"
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger: Any = logging.getLogger(__name__)


class ProactiveFissionScanner:
    """
    L3 Orchestrator: Scans the L4 State for structural patterns
    matching known 'Critical Bloat' profiles.

    Process:
    1. Scan repository for files exceeding line threshold
    2. Query Brave Search for modular design patterns
    3. Use Pinecone to find structural twins
    4. Generate pre-emptive fission strategies
    5. Create GitKraken refactor proposal branches
    """

    # guardian: allow-magic-config
    def __init__(self, McpRouterAgent, line_threshold: int = 600):
        """
        Initialize Proactive Fission Scanner.

        Args:
            McpRouterAgent: MCPRouter instance for MCP calls
            line_threshold: Line count threshold for bloat detection
        """
        self.router = McpRouterAgent
        self.threshold = line_threshold
        Logger.info(f"[OK] Proactive Scanner initialized (threshold: {line_threshold} lines)")

    def get_line_count(self, file_path: str) -> int:
        """
        Get line count for a file.

        Args:
            file_path: Path to file

        Returns:
            Number of lines in file
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                return len(f.readlines())
        except Exception as e:
            Logger.warning(f"   [!]  Could not read {file_path}: {e}")
            return 0

    async def scan_repository(self, target_dir: str) -> list[dict[str, any]]:
        """
        Identifies files that meet the 'Atomic Criticality' criteria.

        Args:
            target_dir: Directory to scan

        Returns:
            List of candidate files with metadata
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ProactiveFissionScanner.scan_repository")

        Logger.info(f"[SCAN] Scanning repository: {target_dir}")
        candidates: Any = []
        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for file in files:
                if file.endswith(".py"):
                    path: Any = Path(root) / file
                    line_count: Any = self.get_line_count(path)
                    if line_count > self.threshold:
                        candidates.append(
                            {
                                "path": path,
                                "line_count": line_count,
                                "Severity": self._calculate_severity(line_count),
                                "relative_path": os.path.relpath(path, target_dir),
                            }
                        )
                        Logger.info(f"   [ALERT] Bloat detected: {file} ({line_count} lines)")
        Logger.info(f"   [OK] Scan complete: {len(candidates)} candidates found")
        return candidates

    def _calculate_severity(self, line_count: int) -> str:
        """
        Calculate Severity level based on line count.

        Args:
            line_count: Number of lines

        Returns:
            Severity level (LOW, MEDIUM, HIGH, CRITICAL)
        """
        if line_count < 700:
            return "LOW"
        elif line_count < 850:
            return "MEDIUM"
        elif line_count < 1000:
            return "HIGH"
        else:
            return "CRITICAL"

    async def generate_pre_emptive_strategy(self, file_path: str) -> dict[str, any]:
        """
        Uses Brave Search to find the best modular split for the specific file type.

        Args:
            file_path: Path to file

        Returns:
            Strategy dictionary with design patterns
        """
        file_name: Any = Path(file_path).name
        Logger.info(f"🧠 Generating strategy for {file_name}")
        try:
            query: Any = f"best modular architecture for python {file_name}"
            design_patterns: Any = await self.router.call_mcp(
                "brave_search", {"query": query, "purpose": "Find modular design patterns"}
            )
            structural_twins: Any = await self.router.call_mcp(
                "pinecone",
                {
                    "query": f"similar structure to {file_name}",
                    "top_k": 3,
                    "purpose": "Find files with similar structure",
                },
            )
            strategy: Any = {
                "file_path": file_path,
                "design_patterns": design_patterns,
                "structural_twins": structural_twins,
                "recommended_split": self._recommend_split(file_path),
            }
            Logger.info("   [OK] Strategy generated")
            return strategy
        except Exception as e:
            Logger.error(f"   [X] Strategy generation failed: {e}")
            return {"file_path": file_path, "error": str(e)}

    def _recommend_split(self, file_path: str) -> dict[str, str]:
        """
        Recommend split pattern based on file name and content.

        Args:
            file_path: Path to file

        Returns:
            Dictionary of recommended file splits
        """
        base_name = Path(file_path).stem
        parent_dir = Path(file_path).parent
        return {
            "core": f"{parent_dir}/{base_name}_core.py",
            "signals": f"{parent_dir}/{base_name}_signals.py",
            "utils": f"{parent_dir}/{base_name}_utils.py",
            "facade": file_path,
        }

    async def create_refactor_proposal(self, candidates: list[dict[str, any]]) -> str:
        """
        Creates a GitKraken refactor proposal branch.

        Args:
            candidates: List of bloat candidates

        Returns:
            Branch name created
        """
        if not candidates:
            Logger.info("   ℹ️  No candidates for refactor proposal")
            return None
        timestamp: Any = datetime.now().strftime("%Y%m%d_%H%M%S")
        branch_name: Any = f"proactive-refactor-{timestamp}"
        Logger.info(f"🌿 Creating refactor proposal branch: {branch_name}")
        try:
            await self.router.call_mcp("gitkraken", {"action": "create_branch", "name": branch_name})
            await self.router.call_mcp(
                "redis",
                {"action": "set", "key": f"refactor_proposal:{branch_name}", "value": str(len(candidates))},
            )
            Logger.info(f"   [OK] Refactor proposal created: {len(candidates)} files")
            return branch_name
        except Exception as e:
            Logger.error(f"   [X] Failed to create refactor proposal: {e}")
            return None

    async def generate_audit_report(self, candidates: list[dict[str, any]]) -> dict[str, any]:
        """
        Generate comprehensive audit report.

        Args:
            candidates: List of bloat candidates

        Returns:
            Audit report dictionary
        """
        Logger.info("[STATS] Generating audit report")
        severity_counts: Any = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        total_lines: Any = 0
        for candidate in candidates:
            severity_counts[candidate["Severity"]] += 1
            total_lines += candidate["line_count"]
        report: Any = {
            "total_candidates": len(candidates),
            "severity_breakdown": severity_counts,
            "total_lines": total_lines,
            "average_lines": total_lines // len(candidates) if candidates else 0,
            "candidates": candidates,
        }
        Logger.info(f"   [OK] Report generated: {len(candidates)} candidates")
        Logger.info(f"      CRITICAL: {severity_counts['CRITICAL']}")
        Logger.info(f"      HIGH: {severity_counts['HIGH']}")
        Logger.info(f"      MEDIUM: {severity_counts['MEDIUM']}")
        Logger.info(f"      LOW: {severity_counts['LOW']}")
        return report


# guardian: allow-magic-config
def get_proactive_scanner(McpRouterAgent: Any, line_threshold: int = 600) -> ProactiveFissionScanner:
    """
    Factory function to create ProactiveFissionScanner instance.

    Args:
        McpRouterAgent: MCPRouter instance
        line_threshold: Line count threshold

    Returns:
        ProactiveFissionScanner instance
    """
    return ProactiveFissionScanner(McpRouterAgent=McpRouterAgent, line_threshold=line_threshold)


'\nfrom agentic_core.core.proactive_audit import ProactiveFissionScanner\nfrom agentic_core.infra.McpRouterAgent import MCPRouter\nfrom agentic_core.infra.tui_dashboard import AgenticTUI\n\n# Initialize components\nmcp_router = MCPRouter(tui_handle=tui)\nscanner = ProactiveFissionScanner(McpRouterAgent=McpRouterAgent, line_threshold=THRESHOLD)\n\n# Run proactive scan\ncandidates = await scanner.scan_repository("agentic_core/")\n\n# Generate strategies for each candidate\nfor candidate in candidates:\n    strategy = await scanner.generate_pre_emptive_strategy(candidate["path"])\n    print(f"Strategy for {candidate[\'path\']}: {strategy}")\n\n# Create refactor proposal branch\nbranch_name = await scanner.create_refactor_proposal(candidates)\n\n# Generate audit report\nreport = await scanner.generate_audit_report(candidates)\nprint(f"Audit Report: {report}")\n'
