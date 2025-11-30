#!/usr/bin/env python3
"""
Structure Diff Analyzer for Agentic Workflow v10_11
Compares canonical markdown tree specs vs actual directory structure
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, Set, List, Tuple

def parse_markdown_tree(markdown_path: str) -> Dict[str, Set[str]]:
    """Parse markdown tree into sets of directories and files"""
    directories = set()
    files = set()
    
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
                
                if path_part and not path_part.startswith('###'):
                    # Determine if it's a file or directory
                    if '.' in path_part.split('/')[-1] or path_part.endswith('.gitkeep'):
                        files.add(path_part)
                    else:
                        directories.add(path_part)
    
    return {'directories': directories, 'files': files}

def get_actual_structure(root_path: str) -> Dict[str, Set[str]]:
    """Get actual directory and file structure"""
    directories = set()
    files = set()
    
    for root, dirs, filenames in os.walk(root_path):
        # Skip hidden and cache directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        rel_path = os.path.relpath(root, root_path)
        if rel_path != '.':
            directories.add(rel_path.replace('\\', '/'))
        
        for filename in filenames:
            if not filename.startswith('.') and not filename.endswith('.pyc'):
                rel_file = os.path.join(rel_path, filename).replace('\\', '/')
                if rel_file.startswith('./'):
                    rel_file = rel_file[2:]
                files.add(rel_file)
    
    return {'directories': directories, 'files': files}

def analyze_structure():
    """Main analysis function"""
    base_path = Path(__file__).parent
    markdown_dir = Path("C:/Users/amita/Documents/Work/AI Job Search/AI/ML/DL/GenAI/LLM 101/LLM Pipelines/Resume Gen/Git/Agentic Folder Structure")
    
    roots = [
        "agentic_core", "apps", "config", "data", 
        "observability", "prompt_governance", "runtime", 
        "schemas", "scripts", "tests"
    ]
    
    report = {
        "summary": {},
        "details": {}
    }
    
    total_missing = 0
    total_extra = 0
    
    for root in roots:
        print(f"\n=== Analyzing {root}/ ===")
        
        # Parse canonical structure
        markdown_file = markdown_dir / f"{root}.md"
        if markdown_file.exists():
            canonical = parse_markdown_tree(str(markdown_file))
        else:
            print(f"Warning: {markdown_file} not found")
            continue
        
        # Get actual structure
        actual_path = base_path / root
        if actual_path.exists():
            actual = get_actual_structure(str(actual_path))
        else:
            actual = {'directories': set(), 'files': set()}
        
        # Calculate differences
        missing_dirs = canonical['directories'] - actual['directories']
        missing_files = canonical['files'] - actual['files']
        extra_dirs = actual['directories'] - canonical['directories']
        extra_files = actual['files'] - canonical['files']
        
        missing_count = len(missing_dirs) + len(missing_files)
        extra_count = len(extra_dirs) + len(extra_files)
        
        total_missing += missing_count
        total_extra += extra_count
        
        report["details"][root] = {
            "missing_directories": sorted(list(missing_dirs)),
            "missing_files": sorted(list(missing_files)),
            "extra_directories": sorted(list(extra_dirs)),
            "extra_files": sorted(list(extra_files)),
            "missing_count": missing_count,
            "extra_count": extra_count
        }
        
        report["summary"][root] = {
            "missing_count": missing_count,
            "extra_count": extra_count,
            "status": "OK" if missing_count == 0 and extra_count == 0 else "NEEDS_WORK"
        }
        
        print(f"Missing: {missing_count} ({len(missing_dirs)} dirs, {len(missing_files)} files)")
        print(f"Extra: {extra_count} ({len(extra_dirs)} dirs, {len(extra_files)} files)")
        
        if missing_dirs:
            print(f"  Missing dirs: {missing_dirs}")
        if missing_files:
            print(f"  Missing files: {missing_files}")
        if extra_dirs:
            print(f"  Extra dirs: {extra_dirs}")
        if extra_files:
            print(f"  Extra files: {extra_files}")
    
    report["summary"]["total"] = {
        "total_missing": total_missing,
        "total_extra": total_extra,
        "overall_status": "OK" if total_missing == 0 and total_extra == 0 else "NEEDS_WORK"
    }
    
    print(f"\n=== SUMMARY ===")
    print(f"Total missing items: {total_missing}")
    print(f"Total extra items: {total_extra}")
    print(f"Overall status: {report['summary']['total']['overall_status']}")
    
    # Save detailed report
    report_file = base_path / "structure_diff_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_file}")
    return report

if __name__ == "__main__":
    analyze_structure()
