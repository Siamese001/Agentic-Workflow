"""
Sovereign Healing Engine: Strategy Registry
Proactive repair strategies for L0 governance violations.

Phase 10: Sovereign Self-Correction (Dec 26, 2025)
"""
from typing import List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class HealingStrategy:
    """Base class for all healing strategies."""
    
    def __init__(self, name: str, priority: int):
        self.name = name
        self.priority = priority  # Lower = higher priority
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
        """
        Analyze issues and return actionable fixes.
        
        Args:
            issues: List of issue dictionaries from audit report
            
        Returns:
            List of fix dictionaries with action, target, reason, priority
        """
        return []
    
    async def apply(self, fix: Dict, ctx: Any) -> bool:
        """
        Apply a specific fix and return success status.
        
        Args:
            fix: Fix dictionary with action details
            ctx: Execution context
            
        Returns:
            True if fix was applied successfully, False otherwise
        """
        return False


class StructureHealing(HealingStrategy):
    """Heals structural violations (forbidden root folders, directory depth)."""
    
    def __init__(self):
        super().__init__("Structure", priority=1)
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
        """Diagnose structural issues and propose relocations."""
        fixes = []
        
        for issue in issues:
            description = issue.get("description", "").lower()
            
            # Forbidden root folder violations
            if "forbidden root" in description or "root folder" in description:
                source = Path(issue.get("file", ""))
                
                # Determine target directory based on file type
                if "legacy" in str(source) or "archive" in str(source):
                    target_dir = "agentic_core/L0_maintenance/scripts"
                elif "test" in str(source):
                    target_dir = "tests"
                else:
                    target_dir = "agentic_core/L0_maintenance/scripts"
                
                fixes.append({
                    "action": "move",
                    "source": str(source),
                    "target": str(Path(target_dir) / source.name),
                    "reason": "Forbidden root folder violation",
                    "priority": self.priority,
                    "strategy": self.name
                })
            
            # Directory depth violations
            elif "depth" in description and "invalid" in description:
                source = Path(issue.get("file", ""))
                # Suggest flattening or restructuring
                fixes.append({
                    "action": "restructure",
                    "source": str(source),
                    "reason": "Directory depth violation",
                    "priority": self.priority,
                    "strategy": self.name
                })
        
        return fixes


class UnderscoreFieldHealing(HealingStrategy):
    """Heals underscore-prefixed fields in SSOT models."""
    
    def __init__(self):
        super().__init__("UnderscoreFields", priority=2)
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
        """Diagnose underscore field violations and propose replacements."""
        fixes = []
        
        for issue in issues:
            description = issue.get("description", "").lower()
            
            if "underscore" in description or "_" in description:
                field_name = issue.get("field", "")
                if field_name.startswith("_"):
                    fixes.append({
                        "action": "replace",
                        "file": issue.get("file", ""),
                        "pattern": f"{field_name}:",
                        "replacement": f"{field_name.lstrip('_')}:",
                        "reason": "Underscore field in SSOT model",
                        "priority": self.priority,
                        "strategy": self.name,
                        "field": field_name
                    })
        
        return fixes


class DarkReasoningHealing(HealingStrategy):
    """Heals Dark Reasoning violations by injecting L6 logging."""
    
    def __init__(self):
        super().__init__("DarkReasoning", priority=3)
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
        """Diagnose Dark Reasoning violations and propose logging injections."""
        fixes = []
        
        for issue in issues:
            description = issue.get("description", "").lower()
            
            if "dark reasoning" in description or "l6 footprint" in description:
                # Extract line number from description
                line_num = None
                if "line" in description:
                    try:
                        parts = description.split("line")
                        if len(parts) > 1:
                            line_num = int(parts[1].strip().split(":")[0].strip())
                    except (ValueError, IndexError):
                        pass
                
                fixes.append({
                    "action": "inject_logging",
                    "file": issue.get("file", ""),
                    "line": line_num,
                    "reason": "Dark Reasoning - missing L6 observability footprint",
                    "priority": self.priority,
                    "strategy": self.name
                })
        
        return fixes


class DDDAlignmentHealing(HealingStrategy):
    """Heals DDD alignment violations by refactoring imports."""
    
    def __init__(self):
        super().__init__("DDDAlignment", priority=4)
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
        """Diagnose DDD violations and propose import refactoring."""
        fixes = []
        
        for issue in issues:
            description = issue.get("description", "").lower()
            
            if "context violation" in description or "importing" in description:
                # Extract module being imported
                if "importing" in description:
                    parts = description.split("importing")
                    if len(parts) > 1:
                        module_info = parts[1].strip()
                        
                        fixes.append({
                            "action": "refactor_import",
                            "file": issue.get("file", ""),
                            "module": module_info,
                            "reason": "DDD Context Violation - illegal cross-layer import",
                            "priority": self.priority,
                            "strategy": self.name
                        })
        
        return fixes


class ObservabilityHealing(HealingStrategy):
    """Heals observability footprint violations by injecting L6 logging."""
    
    def __init__(self):
        super().__init__("Observability", priority=3)
    
    async def diagnose(self, issues: List[Dict]) -> List[Dict]:
        """Diagnose observability violations and propose logging injections."""
        fixes = []
        
        for issue in issues:
            dimension = issue.get("dimension", "")
            description = issue.get("description", "").lower()
            
            # Check if this is an observability footprint issue
            if "observability footprint" in dimension.lower() or "observability" in description:
                # Extract function and line information if available
                function_name = None
                line_num = None
                
                # Try to parse from description
                if "function" in description:
                    try:
                        parts = description.split("function")
                        if len(parts) > 1:
                            function_name = parts[1].strip().split()[0]
                    except (ValueError, IndexError):
                        pass
                
                if "line" in description:
                    try:
                        parts = description.split("line")
                        if len(parts) > 1:
                            line_num = int(parts[1].strip().split(":")[0].strip())
                    except (ValueError, IndexError):
                        pass
                
                fixes.append({
                    "action": "inject_logging",
                    "file": issue.get("file", ""),
                    "line": line_num,
                    "function": function_name,
                    "reason": "Missing observability footprint in reasoning block",
                    "priority": self.priority,
                    "strategy": self.name,
                    "suggestion": f"Add logger.info('[REASONING START] {function_name}')" if function_name else "Add logging statement"
                })
        
        return fixes


# Registry of all available healing strategies
HEALING_STRATEGIES = [
    StructureHealing(),
    UnderscoreFieldHealing(),
    DarkReasoningHealing(),
    ObservabilityHealing(),
    DDDAlignmentHealing()
]


def get_strategy_by_name(name: str) -> HealingStrategy:
    """Get a healing strategy by name."""
    for strategy in HEALING_STRATEGIES:
        if strategy.name.lower() == name.lower():
            return strategy
    return None


def get_strategies_by_priority() -> List[HealingStrategy]:
    """Get all strategies sorted by priority (lower number = higher priority)."""
    return sorted(HEALING_STRATEGIES, key=lambda s: s.priority)
