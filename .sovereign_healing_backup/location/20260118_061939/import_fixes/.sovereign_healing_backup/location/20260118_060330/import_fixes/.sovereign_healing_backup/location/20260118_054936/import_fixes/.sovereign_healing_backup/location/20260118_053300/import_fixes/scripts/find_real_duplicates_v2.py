#!/usr/bin/env python3
"""
Find REAL duplicate agent files by NAME (not content hash).
Shows files with same name in different locations.
"""
from pathlib import Path
from collections import defaultdict
from datetime import datetime

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
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


def is_agent_file(path: Path) -> bool:
    """Check if path is an actual agent file (not test)."""
    if not path.name.endswith("Agent.py"):
        return False
    path_str = str(path).lower()
    if "test" in path_str or "\\tests\\" in path_str or "/tests/" in path_str:
        return False
    if "__pycache__" in path_str or ".venv" in path_str:
        return False
    return True


def get_priority(path: Path, project_root: Path) -> int:
    """Get location priority (lower = better/canonical)."""
    rel_path = str(path.relative_to(project_root)).replace("\\", "/")
    
    if "blueprint_sovereign" in rel_path:
        return 10  # Blueprint templates (usually inferior)
    elif "L5_safety/validators" in rel_path:
        return 2  # Validators
    elif "L5_safety/agents" in rel_path:
        return 1  # Canonical agent location
    elif rel_path.startswith("agentic_core/"):
        return 3  # Other agentic_core locations
    else:
        return 5  # Other locations


def infer_rationale(canonical: Path, duplicate: Path, project_root: Path) -> str:
    """Infer rationale based on path patterns."""
    dup_str = str(duplicate.relative_to(project_root))
    can_str = str(canonical.relative_to(project_root))
    
    if "blueprint_sovereign" in dup_str:
        return "Leftover blueprint template — production version is canonical"
    
    if ("validators" in can_str and "agents" in dup_str) or \
       ("agents" in can_str and "validators" in dup_str):
        return "Location overlap: same agent in agents/ vs validators/ directories"
    
    if "runtime" in dup_str or "runtime" in can_str:
        return "Runtime duplicate — consolidate to primary location"
    
    return "Exact duplicate — likely copy-paste or migration artifact"


def main():
    project_root = Path.cwd()
    
    print(f"[SCAN] Searching for agent files in {project_root}...")
    
    # Find all agent files
    agent_files = [f for f in project_root.rglob("*Agent.py") if is_agent_file(f)]
    
    print(f"[SCAN] Found {len(agent_files)} agent files")
    
    # Group by filename
    name_to_files = defaultdict(list)
    for file_path in agent_files:
        name_to_files[file_path.name].append(file_path)
    
    # Filter to only groups with multiple files
    duplicates = {name: files for name, files in name_to_files.items() if len(files) > 1}
    
    print(f"[FOUND] {len(duplicates)} agent names with multiple locations")
    
    if not duplicates:
        print("\n✅ No duplicates found!")
        return 0
    
    # Generate report
    output_file = project_root / REPORTS_DIR / "real_duplicates_by_name.md"
    output_file.parent.mkdir(exist_ok=True)
    
    total_files_to_delete = sum(len(files) - 1 for files in duplicates.values())
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Real Duplicate Agents (By Name)\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Duplicate Agent Names:** {len(duplicates)}\n")
        f.write(f"**Files to Delete:** {total_files_to_delete}\n\n")
        
        f.write("| Agent Name | Canonical Path | Duplicate Path | Rationale |\n")
        f.write("| --- | --- | --- | --- |\n")
        
        for agent_name, files in sorted(duplicates.items()):
            # Sort by priority
            files_sorted = sorted(files, key=lambda f: (get_priority(f, project_root), str(f)))
            
            canonical = files_sorted[0]
            
            for duplicate in files_sorted[1:]:
                canonical_rel = canonical.relative_to(project_root)
                duplicate_rel = duplicate.relative_to(project_root)
                rationale = infer_rationale(canonical, duplicate, project_root)
                
                f.write(f"| {agent_name.replace('.py', '')} | `{canonical_rel}` | `{duplicate_rel}` | {rationale} |\n")
        
        f.write("\n---\n\n")
        f.write("## Delete Commands\n\n")
        f.write("**IMPORTANT:** Review each file before deleting. Use diff to compare:\n")
        f.write("```bash\n")
        f.write("code --diff \"canonical_path\" \"duplicate_path\"\n")
        f.write("```\n\n")
        
        f.write("### Delete Duplicates\n")
        f.write("```bash\n")
        
        for agent_name, files in sorted(duplicates.items()):
            files_sorted = sorted(files, key=lambda f: (get_priority(f, project_root), str(f)))
            
            for duplicate in files_sorted[1:]:
                duplicate_rel = duplicate.relative_to(project_root)
                f.write(f'git rm "{duplicate_rel}"\n')
        
        f.write("```\n")
    
    print(f"\n✅ Generated: {output_file}")
    print(f"   Duplicate agent names: {len(duplicates)}")
    print(f"   Files to delete: {total_files_to_delete}")
    
    # Print summary
    print("\n" + "="*80)
    print("REAL DUPLICATES FOUND (BY NAME)")
    print("="*80)
    
    for agent_name, files in sorted(duplicates.items()):
        files_sorted = sorted(files, key=lambda f: (get_priority(f, project_root), str(f)))
        
        canonical = files_sorted[0]
        
        print(f"\n[{agent_name.replace('.py', '')}]")
        print(f"  ✅ KEEP: {canonical.relative_to(project_root)}")
        for duplicate in files_sorted[1:]:
            print(f"  ❌ DELETE: {duplicate.relative_to(project_root)}")
    
    return 0


if __name__ == "__main__":
    exit(main())
