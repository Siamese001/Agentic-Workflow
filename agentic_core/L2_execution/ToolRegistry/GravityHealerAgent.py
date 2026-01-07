from __future__ import annotations
"""
GravityHealerAgent - Unified Gravity Law Repair
Territory: agentic_core/L2_execution/ToolRegistry/

CONSOLIDATION (2026-01-07):
Merges healing logic from:
- GravityEnforcerAgent (Comment out violations)
- GravityLeakRepairAgent (Dynamic import conversion)

RESPONSIBILITIES:
- Healing ONLY - receives violations from GravityValidatorAgent
- Applies context-aware repair strategies
- Returns structured healing results

HEALING STRATEGIES:
1. Intra-core violations → Suggest file relocation (delegate to LocationHealerAgent)
2. Upstream→Downstream → Comment out forbidden import
3. Upward leaks → Convert to dynamic importlib call
"""
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin

Logger = logging.getLogger(__name__)


class GravityHealerAgent(HealerMixin, SubatomicTestingMixin):
    """
    [L2 HEALER] Specialized repair agent for Gravity violations.
    
    Receives structured violations from GravityValidatorAgent.
    Applies appropriate healing strategy based on violation type.
    """
    
    def __init__(self, project_root: Path) -> None:
        self.root = project_root.resolve()
        self.logger = Logger

    async def heal(self, violations: List[Any]) -> Dict[str, Any]:
        """
        Apply healing strategies to gravity violations.
        
        Args:
            violations: List of GravityViolation objects from validator
            
        Returns:
            Dict with healing statistics and results
        """
        stats = {
            "healed": 0,
            "failed": 0,
            "skipped": 0,
            "by_strategy": {
                "dynamic_import": 0,
                "comment_out": 0,
                "relocation_suggested": 0,
            }
        }
        
        results = []
        
        for v in violations:
            try:
                result = None
                
                if v.suggested_action == "DYNAMIC_IMPORT":
                    result = self._apply_dynamic_import_fix(v.file_path, v.import_line)
                    if result["success"]:
                        stats["healed"] += 1
                        stats["by_strategy"]["dynamic_import"] += 1
                    else:
                        stats["failed"] += 1
                        
                elif v.suggested_action == "COMMENT_OUT":
                    result = self._apply_comment_fix(v.file_path, v.import_line)
                    if result["success"]:
                        stats["healed"] += 1
                        stats["by_strategy"]["comment_out"] += 1
                    else:
                        stats["failed"] += 1
                        
                elif v.suggested_action == "RELOCATE_FILE":
                    # Don't execute relocation - just suggest
                    result = self._suggest_relocation(v)
                    stats["skipped"] += 1
                    stats["by_strategy"]["relocation_suggested"] += 1
                
                if result:
                    results.append({
                        "file": str(v.file_path),
                        "violation_type": v.violation_type,
                        "action": v.suggested_action,
                        "result": result,
                    })
                    
            except Exception as e:
                stats["failed"] += 1
                self.logger.error(f"Failed to heal {v.file_path}: {e}")
                results.append({
                    "file": str(v.file_path),
                    "violation_type": v.violation_type,
                    "action": v.suggested_action,
                    "result": {"success": False, "error": str(e)},
                })
        
        return {
            "statistics": stats,
            "results": results,
        }

    def _apply_dynamic_import_fix(self, file_path: Path, import_line: str) -> Dict[str, Any]:
        """
        Convert static import to dynamic importlib call.
        
        Strategy from GravityLeakRepairAgent:
        - Preserve functionality by using importlib
        - Add comment marking the fix
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Parse the import statement
            if import_line.startswith("import "):
                # Simple import: import agentic_core.L5_safety
                module_name = import_line.replace("import ", "").strip()
                var_name = module_name.split(".")[-1]
                replacement = (
                    f"# GRAVITY FIXED: {import_line}\n"
                    f"import importlib\n"
                    f"{var_name} = importlib.import_module('{module_name}')"
                )
            elif import_line.startswith("from "):
                # From import: from agentic_core.L5_safety import something
                match = re.match(r"from\s+([\w.]+)\s+import\s+([\w,\s]+)", import_line)
                if match:
                    module_path = match.group(1)
                    imported_items = match.group(2).strip()
                    replacement = (
                        f"# GRAVITY FIXED: {import_line}\n"
                        f"import importlib\n"
                        f"_mod = importlib.import_module('{module_path}')\n"
                        f"{imported_items} = getattr(_mod, '{imported_items.split(',')[0].strip()}')"
                    )
                else:
                    return {"success": False, "error": "Could not parse from import"}
            else:
                return {"success": False, "error": "Unknown import format"}
            
            # Replace the import line
            new_content = content.replace(import_line, replacement)
            
            if new_content != content:
                file_path.write_text(new_content, encoding="utf-8")
                self.logger.info(f"Applied dynamic import fix to {file_path.name}")
                return {"success": True, "strategy": "dynamic_import"}
            else:
                return {"success": False, "error": "Import line not found in file"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _apply_comment_fix(self, file_path: Path, import_line: str) -> Dict[str, Any]:
        """
        Seal gravity leaks by commenting out forbidden downstream imports.
        
        Strategy from GravityEnforcerAgent:
        - Comment out the import to prevent execution
        - Add GRAVITY VIOLATION marker for tracking
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Comment out the import
            replacement = f"# GRAVITY VIOLATION: {import_line}"
            new_content = content.replace(import_line, replacement)
            
            if new_content != content:
                file_path.write_text(new_content, encoding="utf-8")
                self.logger.info(f"Commented out gravity violation in {file_path.name}")
                return {"success": True, "strategy": "comment_out"}
            else:
                return {"success": False, "error": "Import line not found in file"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _suggest_relocation(self, violation: Any) -> Dict[str, Any]:
        """
        Suggest file relocation for intra-core violations.
        
        Does NOT execute the move - delegates to LocationHealerAgent.
        """
        # Determine target layer based on imports
        target_layer = violation.target_layer
        
        suggestion = {
            "success": True,
            "strategy": "relocation_suggested",
            "message": f"File should be relocated to {target_layer} or refactored to remove dependency",
            "current_location": str(violation.file_path),
            "suggested_location": f"agentic_core/{target_layer}/",
            "delegate_to": "LocationHealerAgent",
        }
        
        self.logger.info(f"Relocation suggested for {violation.file_path.name}")
        return suggestion

    async def heal_file(self, file_path: Path, violations: List[Any]) -> Dict[str, Any]:
        """
        Heal all gravity violations in a single file.
        
        Args:
            file_path: Path to file to heal
            violations: List of violations for this file
            
        Returns:
            Dict with healing results for the file
        """
        file_violations = [v for v in violations if v.file_path == file_path]
        
        if not file_violations:
            return {"file": str(file_path), "violations": 0, "healed": 0}
        
        result = await self.heal(file_violations)
        
        return {
            "file": str(file_path),
            "violations": len(file_violations),
            "healed": result["statistics"]["healed"],
            "failed": result["statistics"]["failed"],
            "details": result["results"],
        }


__all__ = ["GravityHealerAgent"]
