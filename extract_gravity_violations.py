#!/usr/bin/env python3
"""
Extract detailed gravity violations from the codebase for materiality analysis.
Produces JSON with importer_file, imported_file, import_direction, and context.
"""
import ast
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_core.L4_state.utils.layer_gravity_util import (
    extract_layer_from_path,
    extract_layer_from_module,
    is_gravity_violation,
    LAYER_ORDER
)

def extract_gravity_violations(project_root: Path) -> List[Dict[str, Any]]:
    """Extract all gravity violations with detailed context."""
    violations = []
    
    # Get all Python files in agentic_core
    core_path = project_root / "agentic_core"
    
    for py_file in core_path.rglob("*.py"):
        if py_file.name == "__init__.py" or "legacy" in str(py_file):
            continue
            
        try:
            with open(py_file, encoding="utf-8") as f:
                tree = ast.parse(f.read())
            
            source_layer = extract_layer_from_path(py_file)
            if not source_layer:
                continue
                
            for node in ast.walk(tree):
                violation_info = None
                
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        target_layer = extract_layer_from_module(alias.name)
                        if target_layer and is_gravity_violation(source_layer, target_layer):
                            violation_info = {
                                "importer_file": str(py_file.relative_to(project_root)),
                                "importer_layer": source_layer,
                                "imported_module": alias.name,
                                "imported_layer": target_layer,
                                "import_direction": f"{source_layer} → {target_layer}",
                                "import_type": "direct",
                                "line_number": node.lineno,
                                "is_direct": True,
                                "is_transitive": False
                            }
                            
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        target_layer = extract_layer_from_module(node.module)
                        if target_layer and is_gravity_violation(source_layer, target_layer):
                            violation_info = {
                                "importer_file": str(py_file.relative_to(project_root)),
                                "importer_layer": source_layer,
                                "imported_module": node.module,
                                "imported_layer": target_layer,
                                "import_direction": f"{source_layer} → {target_layer}",
                                "import_type": "from_import",
                                "line_number": node.lineno,
                                "imported_names": [alias.name for alias in node.names] if node.names else [],
                                "is_direct": True,
                                "is_transitive": False
                            }
                
                if violation_info:
                    # Add materiality scoring factors
                    violation_info.update({
                        "authority_leak_score": _calculate_authority_leak(violation_info),
                        "runtime_coupling_score": _calculate_runtime_coupling(violation_info),
                        "blast_radius_score": _calculate_blast_radius(violation_info, project_root),
                        "materiality_score": 0  # Will be calculated below
                    })
                    
                    # Calculate total materiality score
                    violation_info["materiality_score"] = (
                        violation_info["authority_leak_score"] +
                        violation_info["runtime_coupling_score"] +
                        violation_info["blast_radius_score"]
                    )
                    
                    violations.append(violation_info)
                    
        except Exception as e:
            print(f"Error processing {py_file}: {e}")
    
    return violations

def _calculate_authority_leak(violation: Dict[str, Any]) -> int:
    """Score authority leak potential (0-5)."""
    source_layer = violation["importer_layer"]
    target_layer = violation["imported_layer"]
    
    # Higher authority leak when lower layers import from much higher layers
    layer_diff = LAYER_ORDER[target_layer] - LAYER_ORDER[source_layer]
    
    if layer_diff >= 4:  # L0 importing L4+
        return 5
    elif layer_diff >= 3:  # L0/L1 importing L3+
        return 4
    elif layer_diff >= 2:  # L0/L1/L2 importing L2+
        return 3
    elif layer_diff >= 1:
        return 2
    else:
        return 1

def _calculate_runtime_coupling(violation: Dict[str, Any]) -> int:
    """Score runtime coupling (0-3)."""
    imported_module = violation["imported_module"].lower()
    
    # Higher coupling for execution/runtime modules
    if any(keyword in imported_module for keyword in [
        "execution", "runtime", "orchestration", "factory", "engine"
    ]):
        return 3
    elif any(keyword in imported_module for keyword in [
        "reasoning", "agent", "healer", "validator"
    ]):
        return 2
    else:
        return 1

def _calculate_blast_radius(violation: Dict[str, Any], project_root: Path) -> int:
    """Score blast radius based on file usage (0-2)."""
    importer_file = violation["importer_file"]
    
    # Files in core locations have higher blast radius
    if any(keyword in importer_file for keyword in [
        "base_agents", "interfaces", "config", "utils"
    ]):
        return 2
    elif "reasoning" in importer_file or "engines" in importer_file:
        return 1
    else:
        return 0

def main():
    """Main extraction function."""
    project_root = Path("C:/Git/Agentic-Workflow")
    
    print("Extracting detailed gravity violations...")
    violations = extract_gravity_violations(project_root)
    
    # Sort by materiality score (highest first)
    violations.sort(key=lambda v: v["materiality_score"], reverse=True)
    
    # Create report
    report = {
        "meta": {
            "territory": "prompt_governance",
            "timestamp": "2026-02-22T15:45:00.000000",
            "status": "DETAILED_GRAVITY_VIOLATIONS",
            "total_violations": len(violations)
        },
        "summary": {
            "total_violations": len(violations),
            "high_materiality": len([v for v in violations if v["materiality_score"] >= 7]),
            "medium_materiality": len([v for v in violations if 4 <= v["materiality_score"] < 7]),
            "low_materiality": len([v for v in violations if v["materiality_score"] < 4]),
            "layer_violations": {}
        },
        "violations": violations
    }
    
    # Count violations by import direction
    for v in violations:
        direction = v["import_direction"]
        report["summary"]["layer_violations"][direction] = report["summary"]["layer_violations"].get(direction, 0) + 1
    
    # Save to file
    with open("gravity_violations_detailed.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Found {len(violations)} gravity violations")
    print(f"High materiality (≥7): {report['summary']['high_materiality']}")
    print(f"Medium materiality (4-6): {report['summary']['medium_materiality']}")
    print(f"Low materiality (<4): {report['summary']['low_materiality']}")
    print("Detailed report saved to: gravity_violations_detailed.json")
    
    return report

if __name__ == "__main__":
    main()
