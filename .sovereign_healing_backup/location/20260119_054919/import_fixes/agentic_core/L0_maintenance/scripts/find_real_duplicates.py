#!/usr/bin/env python3
"""
Find REAL duplicate agent files (different paths, same or similar content).
Excludes phantom duplicates where the same path appears twice.
"""
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime

from agentic_core.L5_safety.validators.structure_blueprint import (
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
from agentic_core.utils.sovereign_index import SovereignIndex
from archives.location_violations.file_utils import safe_read_file, safe_write_file


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file content."""
    try:
        return hashlib.sha256(file_path.read_bytes()).hexdigest()
    except Exception:
        return None


def is_agent_file(path: Path) -> bool:
    """Check if path is an actual agent file (not test)."""
    if not path.name.endswith("Agent.py"):
        return False
    path_str = str(path).lower()
    if "test" in path_str or "\\tests\\" in path_str or "/tests/" in path_str:
        return False
    return True


def find_real_duplicates(project_root: Path):
    """Find real duplicate files (different paths, same content)."""
    print(f"[SCAN] Searching for agent files in {project_root}...")
    
    # Find all agent files
    agent_files = [f for f in project_root.rglob("*Agent.py") if is_agent_file(f)]
    
    # Exclude certain directories
    excluded_dirs = {".venv", "venv", "__pycache__", ".git", "node_modules", "coverage_html"}
    agent_files = [
        f for f in agent_files 
        if not any(excluded in f.parts for excluded in excluded_dirs)
    ]
    
    print(f"[SCAN] Found {len(agent_files)} agent files")
    
    # Group by hash
    hash_to_files = defaultdict(list)
    for file_path in agent_files:
        file_hash = compute_file_hash(file_path)
        if file_hash:
            hash_to_files[file_hash].append(file_path)
    
    # Filter to only groups with DIFFERENT paths
    real_duplicates = []
    for file_hash, files in hash_to_files.items():
        if len(files) > 1:
            # Check if paths are actually different
            unique_paths = set(str(f.relative_to(project_root)) for f in files)
            if len(unique_paths) > 1:
                real_duplicates.append((file_hash, files))
    
    print(f"[FOUND] {len(real_duplicates)} real duplicate groups (different paths, same content)")
    
    return real_duplicates


def infer_rationale(canonical: Path, duplicate: Path, project_root: Path) -> str:
    """Infer rationale based on path patterns."""
    dup_str = str(duplicate.relative_to(project_root))
    can_str = str(canonical.relative_to(project_root))
    
    if "blueprint_sovereign" in dup_str:
        return "Leftover blueprint template — production version is canonical"
    
    if ("validators" in can_str and "agents" in dup_str) or \
       ("agents" in can_str and "validators" in dup_str):
        return "Location overlap: same agent in agents/ vs validators/ directories"
    
    return "Exact duplicate — likely copy-paste or migration artifact"


def main():
    project_root = Path.cwd()
    
    duplicates = find_real_duplicates(project_root)
    
    if not duplicates:
        print("\n✅ No real duplicates found!")
        print("   (The 195 'duplicates' in the previous report were phantom duplicates)")
        return 0
    
    # Generate report
    output_file = project_root / REPORTS_DIR / "real_duplicates_table.md"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Real Duplicate Agents (Different Paths)\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Real Duplicates:** {len(duplicates)}\n\n")
        
        f.write("| Agent Name | Canonical Path | Duplicate Path | Rationale |\n")
        f.write("| --- | --- | --- | --- |\n")
        
        for file_hash, files in duplicates:
            # Sort by path priority (production > blueprint)
            files_sorted = sorted(files, key=lambda f: (
                0 if "blueprint_sovereign" not in str(f) else 1,
                str(f)
            ))
            
            canonical = files_sorted[0]
            agent_name = canonical.stem
            
            for duplicate in files_sorted[1:]:
                canonical_rel = canonical.relative_to(project_root)
                duplicate_rel = duplicate.relative_to(project_root)
                rationale = infer_rationale(canonical, duplicate, project_root)
                
                f.write(f"| {agent_name} | `{canonical_rel}` | `{duplicate_rel}` | {rationale} |\n")
        
        f.write("\n---\n\n")
        f.write("## Delete Commands\n")
        f.write("```bash\n")
        
        for file_hash, files in duplicates:
            files_sorted = sorted(files, key=lambda f: (
                0 if "blueprint_sovereign" not in str(f) else 1,
                str(f)
            ))
            
            for duplicate in files_sorted[1:]:
                duplicate_rel = duplicate.relative_to(project_root)
                f.write(f'git rm "{duplicate_rel}"\n')
        
        f.write("```\n")
    
    print(f"\n✅ Generated: {output_file}")
    print(f"   Real duplicate groups: {len(duplicates)}")
    
    # Print summary
    print("\n" + "="*80)
    print("REAL DUPLICATES FOUND")
    print("="*80)
    
    for file_hash, files in duplicates:
        files_sorted = sorted(files, key=lambda f: (
            0 if "blueprint_sovereign" not in str(f) else 1,
            str(f)
        ))
        
        canonical = files_sorted[0]
        agent_name = canonical.stem
        
        print(f"\n[{agent_name}]")
        print(f"  ✅ KEEP: {canonical.relative_to(project_root)}")
        for duplicate in files_sorted[1:]:
            print(f"  ❌ DELETE: {duplicate.relative_to(project_root)}")
    
    return 0


if __name__ == "__main__":
    exit(main())
