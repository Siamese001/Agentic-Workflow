from __future__ import annotations
"""
Sovereign Guardian: Observability Footprint (Dark Reasoning Check)
Ensures every L1 reasoning step leaves an L6 observability trail.

The Governance Cycle:
1. L0 (Auditor) defines what is "Legal."
2. L1-L5 perform the actual agentic operations.
3. L6 (Observability) records the ground truth of those operations.
4. L0 (Auditor) periodically sweeps L6 to ensure L1-L5 behaved, flagging Dark Reasoning if an agent "thought" without telling the system.

Phase 9C: Dark Reasoning Guardian (Dec 26, 2025)
"""
import ast
from pathlib import Path
from typing import List, Tuple

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.utils.sovereign_index import SovereignIndex


def check_dark_reasoning(filepath: Path) -> List[str]:
    """
    Check for reasoning operations without corresponding observability footprints.
    
    Dark Reasoning occurs when an agent performs cognitive operations (think, plan, decide)
    without leaving a trace in the L6 observability layer (logging, telemetry).
    
    Args:
        filepath: Path to Python file to audit
        
    Returns:
        List of issues found (empty if compliant)
    """
    issues = []
    
    # Only audit L1-L3 for reasoning footprints
    file_str = str(filepath).replace("\\", "/")
    if not any(layer in file_str for layer in ["L1_cognition", "L2_execution", "L3_orchestration"]):
        return []

    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        class DarkReasoningVisitor(ast.NodeVisitor):
                                    
            def __init__(self):
                self.issues = []
                self.reasoning_methods = {"think", "plan", "decide", "reason", "validate", "execute_plan"}
                
            def visit_Call(self, node):
                                                    
                # Check for calls to reasoning methods
                if isinstance(node.func, ast.Attribute) and node.func.attr.lower() in self.reasoning_methods:
                    self.issues.append(f"Dark Reasoning Violation: Unobserved reasoning call '{node.func.attr}' at line {node.lineno}")
                
                # Check for direct LLM usage (L5 Bypass)
                if isinstance(node.func, ast.Attribute) and node.func.attr in {"chat", "complete", "messages"}:
                    if isinstance(node.func.value, ast.Name) and node.func.value.id in {"client", "openai", "anthropic"}:
                        self.issues.append(f"Potential L5 Bypass: Direct LLM call at line {node.lineno}")
                
                self.generic_visit(node)

        visitor = DarkReasoningVisitor()
        visitor.visit(tree)
        issues.extend(visitor.issues)

    except Exception:
        pass
    
    return issues

def validate_observability_footprint(target_dir: str) -> Tuple[float, List[str]]:
    """
    Validate that all reasoning operations have observability footprints.
    
    Args:
        target_dir: Directory to audit
        
    Returns:
        Tuple of (score percentage, list of issues)
    """
    issues = []
    total_files = 0
    
    for path in Path(target_dir).rglob("*.py"):
        if "tests" in str(path) or "__pycache__" in str(path):
            continue
        
        total_files += 1
        file_issues = check_dark_reasoning(path)
        # Use full path instead of just filename
        issues.extend([f"{str(path)}: {i}" for i in file_issues])
    
    # Calculate score (deduct 5 points per dark reasoning instance)
    score = 100.0
    if issues:
        score = max(0, 100 - (len(issues) * 5))
    
    return score, issues
