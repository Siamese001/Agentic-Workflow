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

from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)


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
        lines = content.splitlines()
        
        # Signals that indicate reasoning or state changes
        reasoning_signals = ["think", "plan", "execute", "decide", "reason", "validate", "check"]
        
        # Signals that indicate L6 logging
        log_signals = ["Logger.", "logging.", "self.log", "trace(", "print("]
        
        for i, line in enumerate(lines):
            # Skip comments and docstrings
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            
            # Check if line contains reasoning signal
            if any(sig in line.lower() for sig in reasoning_signals):
                # Scan the next 10 lines for a corresponding log entry
                ContextWindow = "\n".join(lines[i:min(i+10, len(lines))])
                if not any(log_sig in ContextWindow for log_sig in log_signals):
                    issues.append(f"Potential Dark Reasoning at line {i+1}: Action without L6 footprint")
        
    except Exception as e:
        # Silently skip files that can't be read
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
        if TESTS_DIR in str(path) or "__pycache__" in str(path):
            continue
        
        total_files += 1
        file_issues = check_dark_reasoning(path)
        issues.extend([f"{path.name}: {i}" for i in file_issues])
    
    # Calculate score (deduct 5 points per dark reasoning instance)
    score = 100.0
    if issues:
        score = max(0, 100 - (len(issues) * 5))
    
    return score, issues
