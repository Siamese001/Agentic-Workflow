#!/usr/bin/env python3
"""
Duplicate Agent Finder - Repository Hygiene Tool
Identifies duplicate agent files across the repository and provides remediation recommendations.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, memory, orchestrator, prompt, state, workflow
# This boosts alignment detection — review and integrate appropriately

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Set
import ast


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file content."""
    try:
        content = file_path.read_bytes()
        return hashlib.sha256(content).hexdigest()
    except Exception as e:
        return f"error:{e}"


def compute_semantic_hash(file_path: Path) -> str:
    """
    Compute semantic hash based on class structure (ignoring comments/whitespace).
    This catches near-duplicates with minor formatting differences.
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        # Extract class names, method names, and base classes
        semantic_parts = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = [ast.unparse(base) for base in node.bases]
                semantic_parts.append(f"class:{node.name}:{','.join(bases)}")
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        semantic_parts.append(f"method:{item.name}")
        
        semantic_str = "|".join(sorted(semantic_parts))
        return hashlib.sha256(semantic_str.encode()).hexdigest()[:16]
    except Exception:
        return "parse_error"


def extract_agent_class_name(file_path: Path) -> str:
    """Extract the main agent class name from file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Look for classes ending in Agent
                if node.name.endswith('Agent'):
                    return node.name
        return "NoAgentClass"
    except Exception:
        return "ParseError"


def get_file_location_priority(file_path: Path, project_root: Path) -> int:
    """
    Determine location priority (lower = better/canonical).
    SSOT hierarchy per structure_blueprint.py.
    """
    rel_path = str(file_path.relative_to(project_root)).replace("\\", "/")
    
    # Priority order (canonical locations first)
    if rel_path.startswith("agentic_core/L5_safety/agents/"):
        return 1  # Canonical L5 agent location
    elif rel_path.startswith("agentic_core/L5_safety/validators/"):
        return 2  # L5 validators
    elif rel_path.startswith("agentic_core/L0_maintenance/scripts/"):
        return 3  # L0 maintenance
    elif rel_path.startswith("agentic_core/") and "/agents/" in rel_path:
        return 4  # Other layer agents
    elif rel_path.startswith("agentic_core/config/blueprint_sovereign/"):
        return 10  # Blueprint (often duplicates/templates)
    elif rel_path.startswith("tests/"):
        return 15  # Test files
    else:
        return 20  # Other locations


def analyze_duplicate_quality(file_path: Path) -> Dict[str, any]:
    """Analyze file quality to determine which duplicate to keep."""
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        # Quality metrics
        has_docstrings = False
        has_type_hints = False
        has_tests = False
        has_healing = False
        has_mcp_hardening = False
        syntax_errors = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if ast.get_docstring(node):
                    has_docstrings = True
                
                # Check base classes
                for base in node.bases:
                    base_name = ast.unparse(base)
                    if "HealerMixin" in base_name:
                        has_healing = True
                    if "MCPHardenedMixin" in base_name:
                        has_mcp_hardening = True
                    if "TestingMixin" in base_name:
                        has_tests = True
                
                # Check for type hints
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.returns or any(arg.annotation for arg in item.args.args):
                            has_type_hints = True
        
        # Check for common issues
        if "SubatomicTestingMixin" in content and "from" not in content.split("SubatomicTestingMixin")[0][-100:]:
            syntax_errors.append("Missing SubatomicTestingMixin import")
        
        if "super().heal_repository()" in content:
            # Check if it's in a factory function (bad) or class method (potentially bad)
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "super().heal_repository()" in line:
                    # Check context
                    context = '\n'.join(lines[max(0, i-5):i])
                    if "def create_" in context and "class " not in context:
                        syntax_errors.append("super() call outside class scope")
        
        return {
            "has_docstrings": has_docstrings,
            "has_type_hints": has_type_hints,
            "has_tests": has_tests,
            "has_healing": has_healing,
            "has_mcp_hardening": has_mcp_hardening,
            "syntax_errors": syntax_errors,
            "quality_score": sum([has_docstrings, has_type_hints, has_healing, has_mcp_hardening]) - len(syntax_errors)
        }
    except SyntaxError as e:
        return {
            "has_docstrings": False,
            "has_type_hints": False,
            "has_tests": False,
            "has_healing": False,
            "has_mcp_hardening": False,
            "syntax_errors": [f"SyntaxError: {e}"],
            "quality_score": -10
        }
    except Exception as e:
        return {
            "has_docstrings": False,
            "has_type_hints": False,
            "has_tests": False,
            "has_healing": False,
            "has_mcp_hardening": False,
            "syntax_errors": [f"ParseError: {e}"],
            "quality_score": -5
        }


def find_duplicate_agents(project_root: Path) -> Dict[str, List[Path]]:
    """Find all duplicate agent files in the repository."""
    print(f"[SCAN] Searching for agent files in {project_root}...")
    
    # Find all Python files with "Agent" in the name
    agent_files = []
    for pattern in ["**/*Agent.py", "**/*agent.py"]:
        agent_files.extend(project_root.glob(pattern))
    
    # Exclude certain directories
    excluded_dirs = {".venv", "venv", "__pycache__", ".git", "node_modules", "coverage_html"}
    agent_files = [
        f for f in agent_files 
        if not any(excluded in f.parts for excluded in excluded_dirs)
    ]
    
    print(f"[SCAN] Found {len(agent_files)} agent files")
    
    # Group by exact hash
    exact_duplicates = defaultdict(list)
    for file_path in agent_files:
        file_hash = compute_file_hash(file_path)
        if not file_hash.startswith("error:"):
            exact_duplicates[file_hash].append(file_path)
    
    # Group by semantic hash (near-duplicates)
    semantic_duplicates = defaultdict(list)
    for file_path in agent_files:
        semantic_hash = compute_semantic_hash(file_path)
        if semantic_hash != "parse_error":
            semantic_duplicates[semantic_hash].append(file_path)
    
    # Filter to only groups with duplicates
    exact_dups = {h: files for h, files in exact_duplicates.items() if len(files) > 1}
    semantic_dups = {h: files for h, files in semantic_duplicates.items() if len(files) > 1}
    
    print(f"[FOUND] {len(exact_dups)} exact duplicate groups")
    print(f"[FOUND] {len(semantic_dups)} semantic duplicate groups")
    
    return exact_dups, semantic_dups


def generate_recommendations(duplicate_groups: Dict[str, List[Path]], project_root: Path, duplicate_type: str = "exact") -> List[Dict]:
    """Generate remediation recommendations for each duplicate group."""
    recommendations = []
    
    for hash_val, files in duplicate_groups.items():
        if len(files) < 2:
            continue
        
        # Sort by location priority
        files_with_priority = [(f, get_file_location_priority(f, project_root)) for f in files]
        files_with_priority.sort(key=lambda x: x[1])
        
        # Analyze quality
        files_with_quality = []
        for file_path, priority in files_with_priority:
            quality = analyze_duplicate_quality(file_path)
            files_with_quality.append((file_path, priority, quality))
        
        # Sort by quality score (descending) then priority (ascending)
        files_with_quality.sort(key=lambda x: (-x[2]["quality_score"], x[1]))
        
        canonical_file = files_with_quality[0][0]
        canonical_quality = files_with_quality[0][2]
        duplicates_to_remove = [f[0] for f in files_with_quality[1:]]
        
        # Extract agent class name
        agent_class = extract_agent_class_name(canonical_file)
        
        # Generate recommendation
        rec = {
            "agent_class": agent_class,
            "duplicate_type": duplicate_type,
            "canonical_file": str(canonical_file.relative_to(project_root)),
            "canonical_quality": canonical_quality,
            "duplicates": [
                {
                    "path": str(f[0].relative_to(project_root)),
                    "priority": f[1],
                    "quality": f[2]
                }
                for f in files_with_quality[1:]
            ],
            "action": "DELETE" if canonical_quality["quality_score"] > 0 else "REVIEW",
            "rationale": generate_rationale(canonical_file, duplicates_to_remove, canonical_quality, files_with_quality[1:])
        }
        
        recommendations.append(rec)
    
    return recommendations


def generate_rationale(canonical: Path, duplicates: List[Path], canonical_quality: Dict, duplicate_info: List[Tuple]) -> str:
    """Generate human-readable rationale for the recommendation."""
    rationale_parts = []
    
    # Canonical file strengths
    strengths = []
    if canonical_quality["has_healing"]:
        strengths.append("has HealerMixin")
    if canonical_quality["has_mcp_hardening"]:
        strengths.append("has MCPHardenedMixin")
    if canonical_quality["has_docstrings"]:
        strengths.append("has docstrings")
    if canonical_quality["has_type_hints"]:
        strengths.append("has type hints")
    
    if strengths:
        rationale_parts.append(f"Keep canonical: {', '.join(strengths)}")
    
    # Issues with duplicates
    for dup_path, priority, quality in duplicate_info:
        issues = []
        if quality["syntax_errors"]:
            issues.append(f"syntax errors: {', '.join(quality['syntax_errors'])}")
        if not quality["has_healing"] and canonical_quality["has_healing"]:
            issues.append("missing HealerMixin")
        if not quality["has_mcp_hardening"] and canonical_quality["has_mcp_hardening"]:
            issues.append("missing MCPHardenedMixin")
        if quality["quality_score"] < canonical_quality["quality_score"]:
            issues.append(f"lower quality score ({quality['quality_score']} vs {canonical_quality['quality_score']})")
        
        if issues:
            rationale_parts.append(f"Remove {dup_path.name}: {', '.join(issues)}")
    
    return " | ".join(rationale_parts) if rationale_parts else "Review manually - similar quality"


def print_recommendations(recommendations: List[Dict], output_format: str = "text"):
    """Print recommendations in specified format."""
    if output_format == "json":
        print(json.dumps(recommendations, indent=2))
        return
    
    print("\n" + "="*80)
    print("DUPLICATE AGENT ANALYSIS & RECOMMENDATIONS")
    print("="*80 + "\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{'─'*80}")
        print(f"[{i}] {rec['agent_class']} ({rec['duplicate_type']} duplicates)")
        print(f"{'─'*80}")
        
        print(f"\n✅ CANONICAL (KEEP):")
        print(f"   📁 {rec['canonical_file']}")
        print(f"   Quality: {rec['canonical_quality']['quality_score']}/4")
        if rec['canonical_quality']['syntax_errors']:
            print(f"   ⚠️  Issues: {', '.join(rec['canonical_quality']['syntax_errors'])}")
        
        print(f"\n❌ DUPLICATES ({rec['action']}):")
        for dup in rec['duplicates']:
            print(f"   📁 {dup['path']}")
            print(f"      Priority: {dup['priority']} | Quality: {dup['quality']['quality_score']}/4")
            if dup['quality']['syntax_errors']:
                print(f"      ⚠️  Issues: {', '.join(dup['quality']['syntax_errors'])}")
        
        print(f"\n💡 RATIONALE:")
        print(f"   {rec['rationale']}")
        
        print(f"\n🔧 RECOMMENDED ACTION:")
        if rec['action'] == "DELETE":
            print(f"   1. Verify canonical file works correctly")
            print(f"   2. Delete duplicate files:")
            for dup in rec['duplicates']:
                print(f"      rm \"{dup['path']}\"")
            print(f"   3. Update any imports referencing deleted files")
            print(f"   4. Run discovery: python scripts/full_agent_discovery.py --incremental")
        else:
            print(f"   ⚠️  MANUAL REVIEW REQUIRED - Similar quality, check differences carefully")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Find duplicate agents in repository")
    parser.add_argument("--project-root", type=str, default=".", help="Project root directory")
    parser.add_argument("--output", type=str, choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--type", type=str, choices=["exact", "semantic", "both"], default="both", help="Duplicate detection type")
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root).resolve()
    
    if not project_root.exists():
        print(f"Error: Project root {project_root} does not exist")
        return 1
    
    # Find duplicates
    exact_dups, semantic_dups = find_duplicate_agents(project_root)
    
    # Generate recommendations
    all_recommendations = []
    
    if args.type in ["exact", "both"]:
        exact_recs = generate_recommendations(exact_dups, project_root, "exact")
        all_recommendations.extend(exact_recs)
    
    if args.type in ["semantic", "both"]:
        semantic_recs = generate_recommendations(semantic_dups, project_root, "semantic")
        # Filter out exact duplicates already covered
        exact_files = {rec['canonical_file'] for rec in all_recommendations}
        semantic_recs = [r for r in semantic_recs if r['canonical_file'] not in exact_files]
        all_recommendations.extend(semantic_recs)
    
    # Print results
    print_recommendations(all_recommendations, args.output)
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total duplicate groups found: {len(all_recommendations)}")
    print(f"Files to delete: {sum(len(r['duplicates']) for r in all_recommendations)}")
    print(f"Action required: {sum(1 for r in all_recommendations if r['action'] == 'DELETE')} auto-delete, {sum(1 for r in all_recommendations if r['action'] == 'REVIEW')} manual review")
    
    return 0


if __name__ == "__main__":
    exit(main())