from __future__ import annotations
"""
GravityValidatorAgent - Unified Gravity Law Detection
Territory: agentic_core/L5_safety/validators/

CONSOLIDATION (2026-01-07):
Merges detection logic from:
- GravityComplianceValidatorAgent (Intra-core violations)
- GravityEnforcerAgent (Upstream→Downstream violations)
- GravityLeakRepairAgent (Upward leak detection)

RESPONSIBILITIES:
- Detection ONLY - no healing
- Returns structured GravityViolation objects
- Delegates healing to GravityHealerAgent (L2)

VIOLATION TYPES:
1. Intra-core: L1→L2/L3/L4/L5 (forbidden by LAYER_FORBIDDEN_IMPORTS)
2. Upstream→Downstream: agentic_core→apps_* (forbidden by GRAVITY_CONFIG)
3. Upward leaks: Any→L4/L5 (forbidden by layer authority)
"""
import re
import logging
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    CORE_SUBFOLDER_MAP,
    SOVEREIGN_REGISTRY,
    LAYER_FORBIDDEN_IMPORTS,
)

Logger = logging.getLogger(__name__)


@dataclass
class GravityViolation:
    """Structured violation for unified gravity detection."""
    file_path: Path
    import_line: str
    violation_type: str  # 'intra_core', 'upstream_downstream', 'upward_leak'
    source_layer: str
    target_layer: str
    severity: int
    suggested_action: str
    line_number: Optional[int] = None


class GravityValidatorAgent(SubatomicTestingMixin):
    """
    [L5 VALIDATOR] Unified detection for all gravity laws.
    
    Consolidates logic from:
    - GravityComplianceValidatorAgent (Intra-core)
    - GravityEnforcerAgent (Upstream→Downstream)
    - GravityLeakRepairAgent (Upward leaks to L4/L5)
    
    Detection only - delegates healing to GravityHealerAgent.
    """
    
    def __init__(self, project_root: Path) -> None:
        self.root = project_root.resolve()
        self.layers = list(CORE_SUBFOLDER_MAP.keys())
        self.logger = Logger

    def _get_layer_rank(self, path_str: str) -> int:
        """Return authority rank: lower index = higher authority."""
        for i, layer in enumerate(self.layers):
            if layer in path_str:
                return i
        return -1

    async def detect_violations(self, file_path: Path) -> List[GravityViolation]:
        """
        Unified detection for all gravity violation types.
        
        Returns:
            List of GravityViolation objects with severity and suggested healing
        """
        raw_violations = []
        
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            current_rank = self._get_layer_rank(str(file_path))
            in_docstring = False
            
            for line_num, line in enumerate(lines, 1):
                clean_line = line.strip()

                # MULTI-LINE DOCSTRING TRACKING
                if clean_line.count('"""') % 2 != 0 or clean_line.count("'''") % 2 != 0:
                    in_docstring = not in_docstring
                    continue
                
                # SKIPS: Ignore comments, empty lines, and docstring interiors
                if not clean_line or clean_line.startswith("#") or in_docstring:
                    continue
                
                # HARDENING: Ensure we are looking at an actual import statement, not a string
                if not (clean_line.startswith("import ") or clean_line.startswith("from ")):
                    # Exception: check if it's an inline import (rare but possible)
                    if "import agentic_core" not in clean_line:
                        continue

                # Pattern 1: Intra-core and Upward Leak Detection
                imports = re.findall(r"(?:from|import)\s+agentic_core\.(L\d+_\w+)", line)
                
                for imp_layer in imports:
                    imp_rank = self._get_layer_rank(imp_layer)
                    if imp_rank == -1:
                        continue

                    # 1. Intra-core violation (importing from lower-authority layer)
                    if current_rank != -1 and imp_rank > current_rank:
                        raw_violations.append(GravityViolation(
                            file_path=file_path,
                            import_line=line.strip(),
                            violation_type="intra_core",
                            source_layer=self.layers[current_rank],
                            target_layer=imp_layer,
                            severity=8,
                            suggested_action="RELOCATE_FILE",
                            line_number=line_num
                        ))
                    
                    # 2. Upward Leak (Low-layer importing L4/L5)
                    if imp_layer in ["L4_state", "L5_safety"] and current_rank < 3:
                        raw_violations.append(GravityViolation(
                            file_path=file_path,
                            import_line=line.strip(),
                            violation_type="upward_leak",
                            source_layer=self.layers[current_rank] if current_rank != -1 else "unknown",
                            target_layer=imp_layer,
                            severity=9,
                            suggested_action="DYNAMIC_IMPORT",
                            line_number=line_num
                        ))

                # 3. Upstream → Downstream (Core → Apps/Tests)
                if "agentic_core" in file_path.parts:
                    downstream_match = re.search(r"^(?:import|from)\s+(apps_\w+|tests)", clean_line)
                    if downstream_match:
                        raw_violations.append(GravityViolation(
                            file_path=file_path,
                            import_line=line.strip(),
                            violation_type="upstream_downstream",
                            source_layer="agentic_core",
                            target_layer=downstream_match.group(1),
                            severity=10,
                            suggested_action="COMMENT_OUT",
                            line_number=line_num
                        ))
                        
        except Exception as e:
            self.logger.error(f"Failed to scan {file_path}: {e}")

        # DEDUPLICATION: If multiple violations on one line, keep only the highest severity
        deduped = {}
        for v in raw_violations:
            key = (v.line_number, v.import_line)
            if key not in deduped or v.severity > deduped[key].severity:
                deduped[key] = v
            
        return list(deduped.values())

    async def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate a single file for gravity violations.
        
        Returns:
            Dict with violation count and details
        """
        violations = await self.detect_violations(file_path)
        
        return {
            "file": str(file_path.relative_to(self.root)),
            "violations_found": len(violations),
            "violations": [
                {
                    "type": v.violation_type,
                    "line": v.line_number,
                    "import": v.import_line,
                    "severity": v.severity,
                    "action": v.suggested_action,
                }
                for v in violations
            ]
        }

    async def validate_repository(self) -> Dict[str, Any]:
        """
        Scan entire repository for gravity violations.
        
        Returns:
            Dict with comprehensive violation report
        """
        all_violations = []
        files_scanned = 0
        
        for py_file in self.root.rglob("*.py"):
            # Skip excluded directories
            if any(skip in py_file.parts for skip in ["__pycache__", ".git", "archives", ".venv"]):
                continue
                
            files_scanned += 1
            violations = await self.detect_violations(py_file)
            all_violations.extend(violations)
        
        # Group by violation type
        by_type = {
            "intra_core": [v for v in all_violations if v.violation_type == "intra_core"],
            "upstream_downstream": [v for v in all_violations if v.violation_type == "upstream_downstream"],
            "upward_leak": [v for v in all_violations if v.violation_type == "upward_leak"],
        }
        
        return {
            "files_scanned": files_scanned,
            "total_violations": len(all_violations),
            "by_type": {
                "intra_core": len(by_type["intra_core"]),
                "upstream_downstream": len(by_type["upstream_downstream"]),
                "upward_leak": len(by_type["upward_leak"]),
            },
            "violations": all_violations,
        }


__all__ = ["GravityValidatorAgent", "GravityViolation"]
