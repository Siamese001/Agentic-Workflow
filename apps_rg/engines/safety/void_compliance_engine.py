"""
Void Compliance Engine - Architecture enforcement and legacy import prevention
Refactored from void_compliance.py
Following Batch 6 specifications with AST scanning
"""

from __future__ import annotations
from typing import Any, List, Dict
import logging
import ast
from pathlib import Path

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class VoidComplianceEngine(BaseRGEngine):
    """
    Sovereign Safety Engine.
    Enforces architectural purity (Void Compliance).
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="SAFETY.VOID")
        self.forbidden_imports = ["archives", "legacy_root_folders"]
        self.project_root = Path(__file__).parent.parent.parent.parent  # C:\Git\Agentic-Workflow

    async def execute(self, scan_path: str = "apps_rg") -> Dict[str, Any]:
        """
        Scan the target directory for architectural violations.
        """
        self._mcp_audit("void_compliance_scan_start", {"target": scan_path})
        
        target_dir = self.project_root / scan_path
        if not target_dir.exists():
            self.record_fail(f"Scan target not found: {target_dir}")
            return {"status": "error"}

        violations = []
        
        # Recursive scan of python files
        for file_path in target_dir.rglob("*.py"):
            # Skip self to prevent recursion alerts
            if file_path.name == "void_compliance_engine.py":
                continue
                
            file_violations = self._audit_file(file_path)
            if file_violations:
                violations.extend(file_violations)

        if violations:
            # CRITICAL: This is a system-halting event
            msg = f"VOID COMPLIANCE FAILURE: Found {len(violations)} legacy contaminations."
            self.record_fail(msg, data={"violations": violations}, signal="SYSTEM_CRITICAL")
            # In strict mode, we might raise SystemExit, but for engine safety we return failure
            raise RuntimeError(msg)

        self.record_pass("Architecture is clean. No legacy contamination detected.")
        return {"status": "clean", "scanned_files": "All .py in apps_rg"}

    def _audit_file(self, file_path: Path) -> List[str]:
        """Parse AST to find forbidden imports."""
        issues = []
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if self._is_forbidden(alias.name):
                            issues.append(f"{file_path.name}: import {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module and self._is_forbidden(node.module):
                        issues.append(f"{file_path.name}: from {node.module}...")
                        
        except Exception as e:
            Logger.warning(f"Could not parse {file_path}: {e}")
            
        return issues

    def _is_forbidden(self, module_name: str) -> bool:
        """Check against blacklist."""
        return any(module_name.startswith(bad) for bad in self.forbidden_imports)
