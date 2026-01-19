
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: guardrail
# This boosts alignment detection — review and integrate appropriately


# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations
"""
GravityLeakRepairAgent - Automated Gravity Violation Healer (Phase 2.3)
Territory: agentic_core/L5_safety/gravity/

RESPONSIBILITIES:
- Automatically fix upward imports detected by GravityEnforcerAgent
- Refactor code to eliminate gravity violations
- Suggest architectural improvements
- Generate import rewrite recommendations

HEALING STRATEGIES:
1. Move shared code to neutral utils/ layer
2. Create abstraction layers for cross-layer dependencies
3. Use dependency injection instead of direct imports
4. Refactor to respect layer hierarchy

Canon Key 51 Compliance: Includes heal_repository() method
"""
import ast
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass

from agentic_core.L5_safety.validators.healer_mixin import HealerMixin
from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin
from agentic_core.L3_orchestration.fission_logic.subatomic_testing_mixin import SubatomicTestingMixin

Logger = logging.getLogger(__name__)


@dataclass
class GravityFix:
    """Represents a gravity violation fix."""
    file_path: Path
    line_number: int
    old_import: str
    new_import: str
    fix_type: str  # 'RELOCATE', 'ABSTRACT', 'INJECT', 'REMOVE'
    rationale: str


class GravityLeakRepairAgent(SubatomicTestingMixin, MCPHardenedMixin, HealerMixin):
    """
    [L5 HEALER] Automated gravity violation repair agent.
    
    Works in tandem with GravityEnforcerAgent to automatically fix
    upward imports and architectural violations.
    
    Healing Strategies:
    1. RELOCATE: Move shared code to utils/ or appropriate layer
    2. ABSTRACT: Create abstraction layer for cross-layer dependencies
    3. INJECT: Use dependency injection instead of direct imports
    4. REMOVE: Remove unnecessary imports
    """
    
    # Layer hierarchy - lower index = higher authority
    LAYER_ORDER = {
        'L0': 0,
        'L1': 1,
        'L2': 2,
        'L3': 3,
        'L4': 4,
        'L5': 5,
        'L6': 6
    }
    
    def __init__(self, project_root: Path = None) -> None:
        """Initialize the gravity leak repair agent."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.logger = Logger
        super().__init__()
    
    def analyze_violation(
        self,
        file_path: Path,
        import_statement: str,
        file_layer: str,
        import_layer: str
    ) -> GravityFix:
        """
        Analyze a gravity violation and recommend a fix.
        
        Args:
            file_path: File with the violation
            import_statement: The problematic import
            file_layer: Layer of the file
            import_layer: Layer being imported
            
        Returns:
            GravityFix with recommended solution
        """
        # Determine fix strategy based on violation pattern
        
        # Strategy 1: If importing from L0, likely a shared utility
        if import_layer == 'L0':
            return GravityFix(
                file_path=file_path,
                line_number=0,
                old_import=import_statement,
                new_import=self._suggest_utils_import(import_statement),
                fix_type='RELOCATE',
                rationale=f"Move shared L0 code to utils/ to avoid upward import from {file_layer}"
            )
        
        # Strategy 2: Cross-layer dependency - suggest abstraction
        else:
            return GravityFix(
                file_path=file_path,
                line_number=0,
                old_import=import_statement,
                new_import="# TODO: Create abstraction layer",
                fix_type='ABSTRACT',
                rationale=f"Create abstraction layer to decouple {file_layer} from {import_layer}"
            )
    
    def _suggest_utils_import(self, import_statement: str) -> str:
        """
        Suggest a utils/ import path for relocated code.
        
        Args:
            import_statement: Original import statement
            
        Returns:
            Suggested new import path
        """
        # Extract module name from import
        if 'from' in import_statement:
            # from agentic_core.L0_maintenance.mixins import X
            parts = import_statement.split()
            if len(parts) >= 4:
                module_path = parts[1]
                imported_items = ' '.join(parts[3:])
                
                # Suggest utils path
                if 'mixins' in module_path:
                    return f"from agentic_core.utils.core_extensions.subatomic_testing_mixin import {imported_items}"
                else:
                    return f"from agentic_core.utils import {imported_items}"
        
        return import_statement
    
    def generate_fix_report(self, violations: List[Dict[str, Any]]) -> List[GravityFix]:
        """
        Generate fix recommendations for all violations.
        
        Args:
            violations: List of gravity violations from GravityEnforcerAgent
            
        Returns:
            List of GravityFix recommendations
        """
        fixes = []
        
        for violation in violations:
            fix = self.analyze_violation(
                file_path=violation.get('file_path'),
                import_statement=violation.get('import_statement', ''),
                file_layer=violation.get('file_layer', ''),
                import_layer=violation.get('import_layer', '')
            )
            fixes.append(fix)
        
        return fixes
    
    def apply_fix(
        self,
        fix: GravityFix,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Apply a gravity fix to a file.
        
        Args:
            fix: GravityFix to apply
            dry_run: If True, only simulate the fix
            
        Returns:
            Dict with fix results
        """
        try:
            if dry_run:
                self.logger.info(f"[DRY RUN] Would fix {fix.file_path.name}:")
                self.logger.info(f"  OLD: {fix.old_import}")
                self.logger.info(f"  NEW: {fix.new_import}")
                self.logger.info(f"  TYPE: {fix.fix_type}")
                self.logger.info(f"  REASON: {fix.rationale}")
                return {"status": "simulated", "fix_type": fix.fix_type}
            else:
                # Read file
                content = fix.file_path.read_text(encoding='utf-8')
                
                # Replace import
                new_content = content.replace(fix.old_import, fix.new_import)
                
                # Write back
                if new_content != content:
                    fix.file_path.write_text(new_content, encoding='utf-8')
                    self.logger.info(f"[FIXED] {fix.file_path.name}: {fix.fix_type}")
                    return {"status": "fixed", "fix_type": fix.fix_type}
                else:
                    self.logger.warning(f"[NO CHANGE] {fix.file_path.name}: Import not found")
                    return {"status": "no_change", "fix_type": fix.fix_type}
                    
        except Exception as e:
            self.logger.error(f"Error applying fix to {fix.file_path}: {e}")
            return {"status": "error", "error": str(e)}
    
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Canon Key 51 compliance: Detect and fix gravity violations.
        
        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, attempt to fix violations
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Internal call path tracking
            
        Returns:
            Dictionary with healing summary
        """
        super().heal_repository()

        if _call_path is None:
            _call_path = []
        
        self.logger.info(f"[GravityLeakRepairAgent] Starting gravity leak repair (dry_run={dry_run})")
        
        # Get violations from GravityEnforcerAgent
        try:
            from agentic_core.L5_safety.validators.GravityEnforcerAgent import GravityEnforcerAgent
            enforcer = GravityEnforcerAgent(project_root=self.project_root)
            results = enforcer.validate_repository()
            violations = results.get('violations', [])
        except Exception as e:
            self.logger.error(f"Failed to get violations from GravityEnforcerAgent: {e}")
            return {
                "agent": "GravityLeakRepairAgent",
                "status": "ERROR",
                "error": str(e),
                "violations_found": 0,
                "violations_fixed": 0
            }
        
        if not violations:
            self.logger.info("No gravity violations found - nothing to repair!")
            return {
                "agent": "GravityLeakRepairAgent",
                "status": "PASS",
                "violations_found": 0,
                "violations_fixed": 0,
                "summary": "No gravity violations to repair"
            }
        
        # Generate fix recommendations
        self.logger.info(f"Analyzing {len(violations)} gravity violations...")
        
        # Group violations by fix type
        fix_summary = {
            'RELOCATE': 0,
            'ABSTRACT': 0,
            'INJECT': 0,
            'REMOVE': 0
        }
        
        fixes_applied = 0
        
        for v in violations[:10]:  # Limit to first 10 for safety
            fix = self.analyze_violation(
                file_path=v.file_path,
                import_statement=v.import_statement,
                file_layer=v.file_layer,
                import_layer=v.import_layer
            )
            
            fix_summary[fix.fix_type] += 1
            
            # Apply fix if execute=True
            if execute and not dry_run:
                result = self.apply_fix(fix, dry_run=False)
                if result.get('status') == 'fixed':
                    fixes_applied += 1
            else:
                # Just report
                self.apply_fix(fix, dry_run=True)
        
        # Report summary
        self.logger.info(f"\nGravity Leak Repair Summary:")
        self.logger.info(f"  Total violations: {len(violations)}")
        self.logger.info(f"  Analyzed: {min(10, len(violations))}")
        self.logger.info(f"  Fix types:")
        for fix_type, count in fix_summary.items():
            if count > 0:
                self.logger.info(f"    {fix_type}: {count}")
        self.logger.info(f"  Fixes applied: {fixes_applied}")
        
        return {
            "agent": "GravityLeakRepairAgent",
            "violations_found": len(violations),
            "violations_fixed": fixes_applied,
            "fix_summary": fix_summary,
            "status": "PASS" if fixes_applied == len(violations) else "PARTIAL",
            "dry_run": dry_run,
            "execute": execute,
            "summary": f"Analyzed {len(violations)} violations, applied {fixes_applied} fixes"
        }


def get_gravity_leak_repair_agent(project_root: Path = None) -> GravityLeakRepairAgent:
    """Factory function for GravityLeakRepairAgent."""
    return GravityLeakRepairAgent(project_root=project_root)