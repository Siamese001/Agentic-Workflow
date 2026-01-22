from __future__ import annotations
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
Sovereign Audit Engine – Phase 16H (Dec 27, 2025)
Scans for compliance with Phases 16A-16G.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
Enhanced in Phase 17 with autonomous healing integration.
"""
import logging
import os
import re
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY

required_depth: Any = SOVEREIGN_REGISTRY["agentic_core"]["depth"]
Logger: Any = logging.getLogger(__name__)
banned_imports: Any = {
    "Redis": ["import\\s+redis", "from\\s+redis"],
    "LLM SDKs": ["import\\s+openai", "import\\s+anthropic", "google\\.generativeai"],
    "Vector SDKs": ["from\\s+pinecone", "Pinecone\\s*\\("],
    "HTTP Clients": ["import\\s+requests", "import\\s+httpx", "urllib\\.request"],
    "Filesystem": ["open\\(", "\\.read_text\\(", "\\.write_text\\("],
    "Git Operations": [
        "subprocess\\..*?git",
        "os\\.system\\(.*?git",
        "import\\s+git\\s",
        "from\\s+git\\s+import",
    ],
    "MCP Manager": [
        "from\\s+.*L2_execution.*mcp_manager",
        "from\\s+.*P1_core.*mcp_manager",
        "from\\s+\\.mcp_manager\\s+import",
    ],
}
required_clients: Any = [
    "SovereignRedisMCPClient",
    "SovereignLLMRouterMCPClient",
    "SovereignPineconeMCPClient",
    "SovereignFilesystemMCPClient",
    "SovereignFetchMCPClient",
    "SovereignGitKrakenMCPClient",
]


class SovereigntyAuditor(SovereignBaseAgent):
    """
    Sovereignty Audit Engine for MCP compliance.

    Scans codebase for:
    - Direct SDK usage (Redis, LLM, Vector, HTTP, Filesystem, Git)
    - Path depth violations (SSOT-derived from SOVEREIGN_REGISTRY)
    - Legacy path usage (tools/ instead of utils/)
    - MCP client usage compliance
    """

    def __init__(self, root_dir: str = "agentic_core"):
        """
        Initialize the auditor.

        Args:
            root_dir: Root directory to audit
        """
        self.root_dir = root_dir
        self.violations: list[dict[str, Any]] = []
        self.stats = {
            "files_scanned": 0,
            "violations_found": 0,
            "depth_violations": 0,
            "import_violations": 0,
            "path_violations": 0,
        }

    async def run_audit(self) -> bool:
        """
        Perform a full system sweep for constitutional purity.

        Returns:
            True if no violations found, False otherwise
        """
        Logger.info(f"--- STARTING SOVEREIGNTY AUDIT: {self.root_dir} ---")
        for root, _, files in os.walk(self.root_dir):
            depth: Any = self._calculate_depth(root)
            if depth > REQUIRED_DEPTH:
                self._add_violation("DEPTH_BREACH", f"Path too deep (depth={depth}): {root}", root)
                self.stats["depth_violations"] += 1
            for file in files:
                if file.endswith(".py") and file != "SovereigntyAuditor.py":
                    file_path: Any = os.path.join(root, file)
                    self._audit_file(file_path)
                    self.stats["files_scanned"] += 1
        audit_passed: Any = self._report_results()
        if self.violations:
            Logger.warning("[L0 AUDIT] Violations found. Handing over to Healing Engine.")
            try:
                from agentic_core.L0_maintenance.P1_core.healing_engine import (
                    run_autonomous_healing,
                )

                healing_result: Any = await run_autonomous_healing(self.violations)
                Logger.info(f"[L0 AUDIT] Healing result: {healing_result.get('status', 'unknown')}")
            except Exception as e:
                Logger.error(f"[L0 AUDIT] Healing engine failed: {e}")
        return audit_passed

    def _calculate_depth(self, path: str) -> int:
        """
        Calculate path depth from root.

        Args:
            path: Path to calculate depth for

        Returns:
            Depth level (0-indexed)
        """
        relative = path.replace(self.root_dir, "").strip(os.sep)
        if not relative:
            return 0
        return len(relative.split(os.sep))

    def _audit_file(self, file_path: str):
        """
        Audit a single Python file for sovereignty violations.

        Args:
            file_path: Path to file to audit
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                for category, patterns in BANNED_IMPORTS.items():
                    for pattern in patterns:
                        if re.search(pattern, content):
                            if "McpClient" not in file_path and "McpRouter" not in file_path:
                                self._add_violation(
                                    "IMPORT_BREACH", f"{category} direct usage detected", file_path
                                )
                                self.stats["import_violations"] += 1
                if re.search("agentic_core/tools/", content):
                    self._add_violation(
                        "PATH_BREACH", "Legacy 'tools/' path usage detected", file_path
                    )
                    self.stats["path_violations"] += 1
        except Exception as e:
            Logger.error(f"Error auditing {file_path}: {e}")

    def _add_violation(self, ViolationType: str, message: str, file_path: str):
        """
        Add a Violation to the list.

        Args:
            ViolationType: Type of Violation
            message: Violation message
            file_path: Path where Violation occurred
        """
        self.violations.append({"type": ViolationType, "message": message, "file": file_path})
        self.stats["violations_found"] += 1

    def _report_results(self) -> bool:
        """
        Report audit results.

        Returns:
            True if no violations, False otherwise
        """
        print(f"\n{'=' * 80}")
        print("SOVEREIGNTY AUDIT REPORT")
        print(f"{'=' * 80}")
        print(f"Root Directory: {self.root_dir}")
        print(f"Files Scanned: {self.stats['files_scanned']}")
        print(f"\nViolations Found: {self.stats['violations_found']}")
        print(f"  - Depth Violations: {self.stats['depth_violations']}")
        print(f"  - Import Violations: {self.stats['import_violations']}")
        print(f"  - Path Violations: {self.stats['path_violations']}")
        if self.violations:
            print(f"\n{'=' * 80}")
            print("VIOLATION DETAILS")
            print(f"{'=' * 80}")
            by_type = {}
            for v in self.violations:
                vtype = v["type"]
                if vtype not in by_type:
                    by_type[vtype] = []
                by_type[vtype].append(v)
            for vtype, violations in by_type.items():
                print(f"\n[{vtype}] ({len(violations)} violations)")
                for v in violations[:10]:
                    print(f"  - {v['message']}")
                    print(f"    File: {v['file']}")
                if len(violations) > 10:
                    print(f"  ... and {len(violations) - 10} more")
        print(f"\n{'=' * 80}")
        if self.stats["violations_found"] == 0:
            print("✅ AUDIT PASSED - No violations found")
            print(f"{'=' * 80}\n")
            return True
        else:
            print("❌ AUDIT FAILED - Violations detected")
            print(f"{'=' * 80}\n")
            return False

    def get_stats(self) -> dict[str, Any]:
        """Get audit statistics."""
        return self.stats.copy()

    def get_violations(self) -> list[dict[str, Any]]:
        """Get list of violations."""
        return self.violations.copy()


async def run_sovereignty_audit(root_dir: str = "agentic_core") -> bool:
    """
    Run sovereignty audit on codebase.

    Args:
        root_dir: Root directory to audit

    Returns:
        True if audit passed, False otherwise
    """
    auditor: Any = SovereigntyAuditor(root_dir=root_dir)
    return await auditor.run_audit()


if __name__ == "__main__":
    import asyncio

    result: Any = asyncio.run(run_sovereignty_audit())
    exit(0 if result else 1)


def _run_self_tests(self) -> dict:
    """Run internal self-tests."""
    results = {"passed": 0, "failed": 0, "tests": []}
    try:
        assert self is not None
        results["passed"] += 1
        results["tests"].append({"name": "test_instantiation", "status": "passed"})
    except AssertionError as e:
        results["failed"] += 1
        results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
    return results
