#!/usr/bin/env python3
"""
Migration Mapper for Agentic Workflow v10_11
Maps existing files to canonical locations based on content analysis
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

def analyze_file_content(file_path: str) -> Dict[str, str]:
    """Analyze file content to determine its purpose and suggested location"""
    if not os.path.exists(file_path):
        return {"purpose": "missing", "suggested_location": None}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return {"purpose": "binary", "suggested_location": None}
    
    # Analyze imports and content patterns
    imports = re.findall(r'from\s+([^\s]+)\s+import|import\s+([^\s]+)', content)
    imports = [imp[0] or imp[1] for imp in imports]
    
    # Look for key patterns
    patterns = {
        "planning": ["plan", "strategy", "goal", "decomposition", "refinement"],
        "execution": ["execute", "tool", "api", "browser", "file_ops"],
        "orchestration": ["dag", "react", "controller", "loop"],
        "memory": ["memory", "buffer", "store", "embeddings", "state"],
        "safety": ["safety", "filter", "pii", "toxicity", "guardrail"],
        "rag": ["rag", "retrieval", "query", "fusion", "vector"],
        "qa": ["question", "answer", "understanding", "classification"],
        "utils": ["util", "helper", "common", "shared"]
    }
    
    content_lower = content.lower()
    purpose_scores = {}
    
    for purpose, keywords in patterns.items():
        score = sum(1 for kw in keywords if kw in content_lower)
        if score > 0:
            purpose_scores[purpose] = score
    
    if purpose_scores:
        primary_purpose = max(purpose_scores, key=purpose_scores.get)
    else:
        primary_purpose = "unknown"
    
    return {
        "purpose": primary_purpose,
        "imports": imports[:10],  # Limit imports for readability
        "suggested_location": None  # Will be filled by mapping logic
    }

def create_migration_plan():
    """Create migration plan for all existing files"""
    base_path = Path(__file__).parent
    
    # Load existing structure from diff report
    with open(base_path / "structure_diff_report.json", 'r') as f:
        diff_report = json.load(f)
    
    migration_plan = {
        "migrations": {},
        "unmappable": [],
        "summary": {}
    }
    
    for root, details in diff_report["details"].items():
        print(f"\n=== Mapping {root}/ ===")
        
        root_path = base_path / root
        if not root_path.exists():
            continue
            
        migration_plan["migrations"][root] = {}
        
        # Map extra files
        for file_path in details["extra_files"]:
            full_path = root_path / file_path
            analysis = analyze_file_content(str(full_path))
            
            # Determine suggested canonical location based on purpose and filename
            suggested = suggest_canonical_location(root, file_path, analysis)
            analysis["suggested_location"] = suggested
            
            if suggested:
                migration_plan["migrations"][root][file_path] = {
                    "current": str(full_path),
                    "suggested": suggested,
                    "purpose": analysis["purpose"],
                    "action": "move"
                }
            else:
                migration_plan["unmappable"].append({
                    "file": str(full_path),
                    "reason": "no_clear_mapping"
                })
        
        # Map extra directories
        for dir_path in details["extra_directories"]:
            suggested = suggest_canonical_directory(root, dir_path)
            if suggested:
                migration_plan["migrations"][root][dir_path] = {
                    "current": str(root_path / dir_path),
                    "suggested": suggested,
                    "action": "move_directory"
                }
            else:
                migration_plan["unmappable"].append({
                    "directory": str(root_path / dir_path),
                    "reason": "no_clear_mapping"
                })
    
    # Save migration plan
    plan_file = base_path / "migration_plan.json"
    with open(plan_file, 'w') as f:
        json.dump(migration_plan, f, indent=2)
    
    print(f"\nMigration plan saved to: {plan_file}")
    return migration_plan

def suggest_canonical_location(root: str, file_path: str, analysis: Dict) -> str:
    """Suggest canonical location based on file analysis"""
    
    # Mapping logic based on markdown specs
    if root == "agentic_core":
        purpose = analysis["purpose"]
        filename = file_path.split('/')[-1]
        
        if purpose == "planning":
            if "strategy" in filename.lower() or "goal" in filename.lower():
                return f"agentic_core/l1_planning/strategy_planning/blueprint/goals/{filename}"
            elif "signal" in filename.lower():
                return f"agentic_core/l1_planning/strategy_planning/blueprint/signals/{filename}"
            elif "task" in filename.lower():
                return f"agentic_core/l1_planning/strategy_planning/decomposition/{filename}"
            elif "validator" in filename.lower() or "scoring" in filename.lower():
                return f"agentic_core/l1_planning/strategy_planning/refinement/{filename}"
            else:
                return f"agentic_core/l1_planning/utils/{filename}"
                
        elif purpose == "execution":
            if "tool" in filename.lower() or "browser" in filename.lower():
                return f"agentic_core/l2_execution/tools/browser/{filename}"
            elif "api" in filename.lower() or "client" in filename.lower():
                return f"agentic_core/l2_execution/tools/api/{filename}"
            elif "file" in filename.lower():
                return f"agentic_core/l2_execution/tools/file_ops/{filename}"
            else:
                return f"agentic_core/l2_execution/utils/{filename}"
                
        elif purpose == "orchestration":
            if "dag" in filename.lower() or "graph" in filename.lower():
                return f"agentic_core/l3_orchestration/dag/{filename}"
            elif "react" in filename.lower():
                return f"agentic_core/l3_orchestration/react/{filename}"
            else:
                return f"agentic_core/l3_orchestration/controllers/{filename}"
                
        elif purpose == "memory":
            if "buffer" in filename.lower() or "short" in filename.lower():
                return f"agentic_core/l4_memory/short_term/{filename}"
            elif "embeddings" in filename.lower() or "index" in filename.lower():
                return f"agentic_core/l4_memory/long_term/{filename}"
            else:
                return f"agentic_core/l4_memory/state/{filename}"
                
        elif purpose == "safety":
            if "filter" in filename.lower():
                return f"agentic_core/l5_safety/filters/{filename}"
            elif "guardrail" in filename.lower() or "enforcement" in filename.lower():
                return f"agentic_core/l5_safety/guardrails/{filename}"
            else:
                return f"agentic_core/l5_safety/audit/{filename}"
    
    # Default: no clear mapping
    return None

def suggest_canonical_directory(root: str, dir_path: str) -> str:
    """Suggest canonical location for directories"""
    # Simplified directory mapping
    if root == "agentic_core":
        if "planning" in dir_path.lower():
            return f"agentic_core/l1_planning/{dir_path}"
        elif "execution" in dir_path.lower():
            return f"agentic_core/l2_execution/{dir_path}"
        elif "orchestration" in dir_path.lower():
            return f"agentic_core/l3_orchestration/{dir_path}"
        elif "memory" in dir_path.lower():
            return f"agentic_core/l4_memory/{dir_path}"
        elif "safety" in dir_path.lower():
            return f"agentic_core/l5_safety/{dir_path}"
    
    return None

if __name__ == "__main__":
    create_migration_plan()
