#!/usr/bin/env python3
"""
Enhanced Migration Mapper for Agentic Workflow v10_11
Parses full canonical structure and maps files to most specific locations
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set

def parse_detailed_canonical_structure(markdown_path: str) -> Dict[str, List[str]]:
    """Parse markdown tree into detailed canonical directory structure"""
    directories = []
    
    with open(markdown_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    for line in lines:
        if '│' in line or '├──' in line or '└──' in line:
            # Extract the path part
            match = re.search(r'├──|└──', line)
            if match:
                after_symbol = line[match.end():].strip()
                # Remove comments and level indicators
                path_part = re.sub(r'#.*$', '', after_symbol).strip()
                # Remove trailing / for directories
                if path_part.endswith('/'):
                    path_part = path_part[:-1]
                
                if path_part and not path_part.startswith('###') and 'LEVEL' not in path_part:
                    directories.append(path_part)
    
    return directories

def analyze_file_for_detailed_mapping(file_path: str) -> Dict[str, str]:
    """Detailed analysis of file content for precise canonical mapping"""
    if not os.path.exists(file_path):
        return {"purpose": "missing", "keywords": [], "suggested_paths": []}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return {"purpose": "binary", "keywords": [], "suggested_paths": []}
    
    # Extract keywords and patterns
    content_lower = content.lower()
    filename = os.path.basename(file_path).lower()
    
    # Detailed keyword mapping for canonical structure
    keyword_mappings = {
        # L1 Planning - Strategy Planning
        "agentic_core/l1_planning/strategy_planning/blueprint/goals/": {
            "keywords": ["goal", "objective", "target", "aim"],
            "filename_patterns": ["goal", "objective", "target"]
        },
        "agentic_core/l1_planning/strategy_planning/blueprint/signals/": {
            "keywords": ["signal", "extract", "weight", "type"],
            "filename_patterns": ["signal", "extract", "weight"]
        },
        "agentic_core/l1_planning/strategy_planning/blueprint/orchestration/": {
            "keywords": ["plan", "orchestrat", "optim", "safety", "schema"],
            "filename_patterns": ["plan", "orchestrat", "optim", "safety"]
        },
        "agentic_core/l1_planning/strategy_planning/decomposition/": {
            "keywords": ["task", "segment", "graph", "normal"],
            "filename_patterns": ["task", "segment", "graph", "normal"]
        },
        "agentic_core/l1_planning/strategy_planning/refinement/": {
            "keywords": ["valid", "prune", "score", "refine"],
            "filename_patterns": ["valid", "prune", "score", "refine"]
        },
        
        # L1 Planning - QA Planning
        "agentic_core/l1_planning/qa_planning/question_understanding/": {
            "keywords": ["question", "classif", "intent", "disambigu"],
            "filename_patterns": ["question", "classif", "intent", "disambigu"]
        },
        "agentic_core/l1_planning/qa_planning/retrieval_plans/": {
            "keywords": ["rag", "blueprint", "rank", "fallback"],
            "filename_patterns": ["rag", "blueprint", "rank", "fallback"]
        },
        "agentic_core/l1_planning/qa_planning/answer_blueprints/": {
            "keywords": ["answer", "format", "template", "verif"],
            "filename_patterns": ["answer", "format", "template", "verif"]
        },
        
        # L1 Planning - RAG Planning
        "agentic_core/l1_planning/rag_planning/query_generation/": {
            "keywords": ["query", "hyde", "rewrit", "signal"],
            "filename_patterns": ["query", "hyde", "rewrit", "signal"]
        },
        "agentic_core/l1_planning/rag_planning/fusion/": {
            "keywords": ["fusion", "rrf", "hybrid", "scor"],
            "filename_patterns": ["fusion", "rrf", "hybrid", "scor"]
        },
        "agentic_core/l1_planning/rag_planning/routing/": {
            "keywords": ["vector", "rout", "balanc", "budget"],
            "filename_patterns": ["vector", "rout", "balanc", "budget"]
        },
        
        # L1 Planning - Safety Planning
        "agentic_core/l1_planning/safety_planning/detectors/": {
            "keywords": ["pii", "toxic", "jailbreak", "detect"],
            "filename_patterns": ["pii", "toxic", "jailbreak", "detect"]
        },
        "agentic_core/l1_planning/safety_planning/policies/": {
            "keywords": ["policy", "rule", "severity"],
            "filename_patterns": ["policy", "rule", "severity"]
        },
        "agentic_core/l1_planning/safety_planning/mitigation/": {
            "keywords": ["redact", "rephrase", "block"],
            "filename_patterns": ["redact", "rephrase", "block"]
        },
        
        # L2 Execution - Tools
        "agentic_core/l2_execution/tools/browser/": {
            "keywords": ["browser", "search", "scrape", "extract"],
            "filename_patterns": ["browser", "search", "scrape", "extract"]
        },
        "agentic_core/l2_execution/tools/file_ops/": {
            "keywords": ["file", "load", "find", "summar"],
            "filename_patterns": ["file", "load", "find", "summar"]
        },
        "agentic_core/l2_execution/tools/api/": {
            "keywords": ["api", "client", "openai", "anthropic"],
            "filename_patterns": ["api", "client", "openai", "anthropic"]
        },
        
        # L2 Execution - Execution Engines
        "agentic_core/l2_execution/execution_engines/": {
            "keywords": ["tool", "invoc", "execut", "valid", "error"],
            "filename_patterns": ["tool", "invoc", "execut", "valid", "error"]
        },
        
        # L3 Orchestration - DAG
        "agentic_core/l3_orchestration/dag/node_types/": {
            "keywords": ["node", "plan", "act", "observe"],
            "filename_patterns": ["node", "plan", "act", "observe"]
        },
        "agentic_core/l3_orchestration/dag/": {
            "keywords": ["graph", "build", "optim", "valid"],
            "filename_patterns": ["graph", "build", "optim", "valid"]
        },
        
        # L3 Orchestration - ReAct
        "agentic_core/l3_orchestration/react/": {
            "keywords": ["think", "act", "observe", "react"],
            "filename_patterns": ["think", "act", "observe", "react"]
        },
        
        # L3 Orchestration - Controllers
        "agentic_core/l3_orchestration/controllers/": {
            "keywords": ["control", "loop", "retry", "escal"],
            "filename_patterns": ["control", "loop", "retry", "escal"]
        },
        
        # L4 Memory
        "agentic_core/l4_memory/short_term/": {
            "keywords": ["buffer", "short", "summar", "evict"],
            "filename_patterns": ["buffer", "short", "summar", "evict"]
        },
        "agentic_core/l4_memory/long_term/": {
            "keywords": ["embed", "index", "version", "long"],
            "filename_patterns": ["embed", "index", "version", "long"]
        },
        "agentic_core/l4_memory/state/": {
            "keywords": ["context", "thread", "persist", "state"],
            "filename_patterns": ["context", "thread", "persist", "state"]
        },
        
        # L5 Safety
        "agentic_core/l5_safety/filters/": {
            "keywords": ["filter", "pii", "violence", "policy"],
            "filename_patterns": ["filter", "pii", "violence", "policy"]
        },
        "agentic_core/l5_safety/guardrails/": {
            "keywords": ["guardrail", "enforce", "safety", "block"],
            "filename_patterns": ["guardrail", "enforce", "safety", "block"]
        },
        "agentic_core/l5_safety/audit/": {
            "keywords": ["audit", "log", "trace", "report"],
            "filename_patterns": ["audit", "log", "trace", "report"]
        }
    }
    
    # Score each canonical path
    scored_paths = []
    found_keywords = []
    
    for canonical_path, mapping in keyword_mappings.items():
        score = 0
        
        # Check content keywords
        for keyword in mapping["keywords"]:
            if keyword in content_lower:
                score += 2
                found_keywords.append(keyword)
        
        # Check filename patterns
        for pattern in mapping["filename_patterns"]:
            if pattern in filename:
                score += 3
                found_keywords.append(pattern)
        
        if score > 0:
            scored_paths.append((canonical_path, score, found_keywords))
    
    # Sort by score (highest first)
    scored_paths.sort(key=lambda x: x[1], reverse=True)
    
    suggested_paths = [path for path, score, _ in scored_paths[:3]]  # Top 3 suggestions
    
    return {
        "purpose": "mapped",
        "keywords": found_keywords[:10],  # Limit for readability
        "suggested_paths": suggested_paths,
        "top_suggestion": suggested_paths[0] if suggested_paths else None
    }

def create_enhanced_migration_plan():
    """Create enhanced migration plan with detailed canonical mapping"""
    base_path = Path(__file__).parent
    markdown_dir = Path("C:/Users/amita/Documents/Work/AI Job Search/AI/ML/DL/GenAI/LLM 101/LLM Pipelines/Resume Gen/Git/Agentic Folder Structure")
    
    # Load existing structure from diff report
    with open(base_path / "structure_diff_report.json", 'r') as f:
        diff_report = json.load(f)
    
    migration_plan = {
        "migrations": {},
        "unmappable": [],
        "canonical_structure": {},
        "summary": {}
    }
    
    # First, build the full canonical structure
    roots = ["agentic_core", "apps", "config", "data", "observability", "prompt_governance", "runtime", "schemas", "scripts", "tests"]
    
    for root in roots:
        print(f"\n=== Building canonical structure for {root}/ ===")
        
        markdown_file = markdown_dir / f"{root}.md"
        if markdown_file.exists():
            canonical_dirs = parse_detailed_canonical_structure(str(markdown_file))
            migration_plan["canonical_structure"][root] = canonical_dirs
            print(f"  Found {len(canonical_dirs)} canonical directories")
        else:
            print(f"  Warning: {markdown_file} not found")
    
    # Now map existing files to canonical locations
    for root, details in diff_report["details"].items():
        print(f"\n=== Enhanced mapping for {root}/ ===")
        
        root_path = base_path / root
        if not root_path.exists():
            continue
            
        migration_plan["migrations"][root] = {}
        
        # Map extra files with detailed analysis
        for file_path in details["extra_files"]:
            full_path = root_path / file_path
            analysis = analyze_file_for_detailed_mapping(str(full_path))
            
            if analysis["top_suggestion"]:
                # Use the top suggested canonical path + filename
                filename = os.path.basename(file_path)
                suggested_location = f"{analysis['top_suggestion']}{filename}"
                
                migration_plan["migrations"][root][file_path] = {
                    "current": str(full_path),
                    "suggested": suggested_location,
                    "purpose": analysis["purpose"],
                    "keywords": analysis["keywords"],
                    "confidence": "high" if len(analysis["keywords"]) >= 3 else "medium",
                    "action": "move"
                }
            else:
                # Fallback to simple mapping
                migration_plan["unmappable"].append({
                    "file": str(full_path),
                    "reason": "no_detailed_mapping_available"
                })
    
    # Save enhanced migration plan
    plan_file = base_path / "enhanced_migration_plan.json"
    with open(plan_file, 'w') as f:
        json.dump(migration_plan, f, indent=2)
    
    print(f"\nEnhanced migration plan saved to: {plan_file}")
    return migration_plan

if __name__ == "__main__":
    create_enhanced_migration_plan()
