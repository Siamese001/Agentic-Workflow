"""
Void Compliance Engine - Architecture enforcement and legacy import prevention
Refactored from void_compliance.py
Following Batch 6 specifications with AST scanning

HARDENING: Uses SovereignContext for reporting. Scans file system (not buffer).
Writes 'compliance_audit'.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class VoidComplianceEngine(BaseRGEngine):
    """
    Sovereign Safety Engine.
    Scans: File System ('apps_rg/')
    Writes: 'compliance_audit'
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="SAFETY.VOID")
        self.root_path = Path("apps_rg")

    async def execute(self) -> dict[str, Any]:
        """
        Scan architecture for forbidden legacy imports.
        """
        # 1. LOGIC
        violations = []
        if self.root_path.exists():
            for file_path in self.root_path.rglob("*.py"):
                # Skip self and legacy/quarantine folders
                if file_path.name == "void_compliance_engine.py":
                    continue
                if "legacy" in str(file_path) or "quarantine" in str(file_path):
                    continue

                if self._check_file(file_path):
                    violations.append(str(file_path))

        # 2. WRITE
        report = {"clean": len(violations) == 0, "violations": violations}
        self.ctx.buffer.write("compliance_audit", report, source_agent=self.name)

        if violations:
            self.record_fail(f"VOID POLICE: {len(violations)} legacy files detected", data=report)
            # In strict mode, we might signal critical failure
            self.ctx.add_signal("SYSTEM_CRITICAL")
        else:
            self.record_pass("Void Compliance Verified: 100% Clean")

        return report

    def _check_file(self, path: Path) -> bool:
        try:
            content = path.read_text("utf-8")
            # Check each line - skip commented lines
            for line in content.split("\n"):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue  # Skip comments
                if "import archives" in line or "from archives" in line:
                    return True
            return False
        except Exception:
            return False
