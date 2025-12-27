"""
Sovereign Audit Engine – Phase 16H (Dec 27, 2025)
Scans for compliance with Phases 16A-16G.
Enforces exactly four levels of depth and uses approved utils/ path.
Enhanced in Phase 17 with autonomous healing integration.
"""
import os
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

BANNED_IMPORTS = {
    "Redis": [r'import\s+redis', r'from\s+redis'],
    "LLM SDKs": [r'import\s+openai', r'import\s+anthropic', r'google\.generativeai'],
    "Vector SDKs": [r'from\s+pinecone', r'Pinecone\s*\('],
    "HTTP Clients": [r'import\s+requests', r'import\s+httpx', r'urllib\.request'],
    "Filesystem": [r'open\(', r'\.read_text\(', r'\.write_text\('],
    "Git Operations": [
        r'subprocess\..*?git',  # Phase 17D: Strict Git subprocess lockdown
        r'os\.system\(.*?git',
        r'import\s+git\s',  # Block GitPython
        r'from\s+git\s+import'
    ],
}

REQUIRED_CLIENTS = [
    "SovereignRedisMCPClient",
    "SovereignLLMRouterMCPClient",
    "SovereignPineconeMCPClient",
    "SovereignFilesystemMCPClient",
    "SovereignFetchMCPClient",
    "SovereignGitKrakenMCPClient"
]


class SovereigntyAuditor:
    """
    Sovereignty Audit Engine for MCP compliance.
    
    Scans codebase for:
    - Direct SDK usage (Redis, LLM, Vector, HTTP, Filesystem, Git)
    - Path depth violations (max 4 levels)
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
        self.violations: List[Dict[str, Any]] = []
        self.stats = {
            "files_scanned": 0,
            "violations_found": 0,
            "depth_violations": 0,
            "import_violations": 0,
            "path_violations": 0
        }

    async def run_audit(self) -> bool:
        """
        Perform a full system sweep for constitutional purity.
        
        Returns:
            True if no violations found, False otherwise
        """
        logger.info(f"--- STARTING SOVEREIGNTY AUDIT: {self.root_dir} ---")
        
        for root, _, files in os.walk(self.root_dir):
            # Enforce 4-level depth check
            depth = self._calculate_depth(root)
            if depth > 4:
                self._add_violation(
                    "DEPTH_BREACH",
                    f"Path too deep (depth={depth}): {root}",
                    root
                )
                self.stats["depth_violations"] += 1

            for file in files:
                if file.endswith(".py") and file != "sovereignty_auditor.py":
                    file_path = os.path.join(root, file)
                    self._audit_file(file_path)
                    self.stats["files_scanned"] += 1
        
        audit_passed = self._report_results()
        
        # Phase 17: Trigger autonomous healing if violations found
        if self.violations:
            logger.warning("[L0 AUDIT] Violations found. Handing over to Healing Engine.")
            try:
                from agentic_core.L0_maintenance.healing.healing_engine import run_autonomous_healing
                healing_result = await run_autonomous_healing(self.violations)
                logger.info(f"[L0 AUDIT] Healing result: {healing_result.get('status', 'unknown')}")
            except Exception as e:
                logger.error(f"[L0 AUDIT] Healing engine failed: {e}")
        
        return audit_passed

    def _calculate_depth(self, path: str) -> int:
        """
        Calculate path depth from root.
        
        Args:
            path: Path to calculate depth for
            
        Returns:
            Depth level (0-indexed)
        """
        # Remove root_dir prefix and count remaining levels
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
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for banned imports
                for category, patterns in BANNED_IMPORTS.items():
                    for pattern in patterns:
                        if re.search(pattern, content):
                            # Exclude MCP client files themselves
                            if "mcp_client" not in file_path and "mcp_router" not in file_path:
                                self._add_violation(
                                    "IMPORT_BREACH",
                                    f"{category} direct usage detected",
                                    file_path
                                )
                                self.stats["import_violations"] += 1
                
                # Check for legacy path usage
                if re.search(r'agentic_core/tools/', content):
                    self._add_violation(
                        "PATH_BREACH",
                        "Legacy 'tools/' path usage detected",
                        file_path
                    )
                    self.stats["path_violations"] += 1
                    
        except Exception as e:
            logger.error(f"Error auditing {file_path}: {e}")

    def _add_violation(self, violation_type: str, message: str, file_path: str):
        """
        Add a violation to the list.
        
        Args:
            violation_type: Type of violation
            message: Violation message
            file_path: Path where violation occurred
        """
        self.violations.append({
            "type": violation_type,
            "message": message,
            "file": file_path
        })
        self.stats["violations_found"] += 1

    def _report_results(self) -> bool:
        """
        Report audit results.
        
        Returns:
            True if no violations, False otherwise
        """
        print(f"\n{'='*80}")
        print(f"SOVEREIGNTY AUDIT REPORT")
        print(f"{'='*80}")
        print(f"Root Directory: {self.root_dir}")
        print(f"Files Scanned: {self.stats['files_scanned']}")
        print(f"\nViolations Found: {self.stats['violations_found']}")
        print(f"  - Depth Violations: {self.stats['depth_violations']}")
        print(f"  - Import Violations: {self.stats['import_violations']}")
        print(f"  - Path Violations: {self.stats['path_violations']}")
        
        if self.violations:
            print(f"\n{'='*80}")
            print(f"VIOLATION DETAILS")
            print(f"{'='*80}")
            
            # Group by type
            by_type = {}
            for v in self.violations:
                vtype = v["type"]
                if vtype not in by_type:
                    by_type[vtype] = []
                by_type[vtype].append(v)
            
            for vtype, violations in by_type.items():
                print(f"\n[{vtype}] ({len(violations)} violations)")
                for v in violations[:10]:  # Limit to first 10 per type
                    print(f"  - {v['message']}")
                    print(f"    File: {v['file']}")
                if len(violations) > 10:
                    print(f"  ... and {len(violations) - 10} more")
        
        print(f"\n{'='*80}")
        if self.stats['violations_found'] == 0:
            print("✅ AUDIT PASSED - No violations found")
            print(f"{'='*80}\n")
            return True
        else:
            print("❌ AUDIT FAILED - Violations detected")
            print(f"{'='*80}\n")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get audit statistics."""
        return self.stats.copy()

    def get_violations(self) -> List[Dict[str, Any]]:
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
    auditor = SovereigntyAuditor(root_dir=root_dir)
    return await auditor.run_audit()


if __name__ == "__main__":
    import asyncio
    result = asyncio.run(run_sovereignty_audit())
    exit(0 if result else 1)
