#!/usr/bin/env python3
"""
RecursiveSpanHealerAgent - L3 Orchestration Framework Agent
Detects and heals span-of-two violations (redundant single-child directories).
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple

logger = logging.getLogger(__name__)


class RecursiveSpanHealerAgent:
    """
    L3 Orchestration: Span-of-Two Violation Healer
    Identifies and flattens redundant directory tunnels.
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.violations = []
        
    def detect_span_violations(self, directory: Path) -> List[Tuple[Path, str]]:
        """Detect span-of-two violations in directory tree."""
        violations = []
        
        if not directory.is_dir():
            return violations
            
        for item in directory.rglob("*"):
            if not item.is_dir():
                continue
                
            try:
                children = list(item.iterdir())
                dirs = [c for c in children if c.is_dir()]
                files = [c for c in children if c.is_file()]
                
                # Span violation: single directory child, no files
                if len(dirs) == 1 and len(files) == 0:
                    violations.append((item, f"Redundant tunnel '{item.name}' → flatten"))
            except PermissionError:
                continue
                
        return violations
    
    def heal_violation(self, path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """Heal a span violation by flattening the structure."""
        if dry_run:
            return {'path': str(path), 'action': 'flatten', 'dry_run': True}
        
        # Implementation would move contents up one level
        logger.info("[L6_AUDIT] Action at line 53")
        return {'path': str(path), 'action': 'flatten', 'executed': False}
    
    def run_healing(self, target_dir: Path, dry_run: bool = True) -> Dict[str, Any]:
        """Run healing process on target directory."""
        violations = self.detect_span_violations(target_dir)
        
        logger.info("[L6_AUDIT] Action at line 60")
        healed = []
        for violation_path, reason in violations:
            result = self.heal_violation(violation_path, dry_run)
            healed.append(result)
        
        return {
            'total_violations': len(violations),
            'healed': len(healed),
            'dry_run': dry_run,
            'results': healed
        }