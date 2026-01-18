#!/usr/bin/env python3
"""
Scan entire repository for hardcoded paths and identify SSOT candidates.
"""
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent

# Directories to exclude from scanning
EXCLUDED_DIRS = {
    '__pycache__', '.pytest_cache', 'build', 'dist', '.eggs', '*.egg-info',
    '.git', '.svn', '.hg',
    '.venv', 'venv', 'env', '.env', 'node_modules',
    'coverage_html', 'htmlcov', '.coverage',
    'archives', '.sovereign_healing_backup', 'reports',
    'legacy', 'deprecated', 'test_data',
}

# Files to exclude
EXCLUDED_FILES = {
    'structure_blueprint.py',  # SSOT definition file
    'scan_hardcoded_paths.py',  # This file
    'validate_dashboard_ssot.py',
    'fix_dashboard_hardcoding.py',
}

# Path patterns to search for (ordered by specificity)
PATH_PATTERNS = [
    # Absolute Windows paths
    (r'["\']C:/Git/Agentic-Workflow/([^"\']+)["\']', 'absolute_windows'),
    (r'["\']C:\\\\Git\\\\Agentic-Workflow\\\\([^"\']+)["\']', 'absolute_windows_escaped'),
    
    # Common file paths
    (r'["\']agent_discovery_full\.json["\']', 'agent_discovery'),
    (r'["\']agent_discovery_full\.manifest\.json["\']', 'agent_discovery_manifest'),
    
    # Directory paths (quoted strings)
    (r'["\']agentic_core/L[0-6]_[a-z_]+["\']', 'layer_dir'),
    (r'["\']agentic_core/([^"\']+)["\']', 'agentic_core_path'),
    (r'["\']scripts/([^"\']+)["\']', 'scripts_path'),
    (r'["\']apps_[a-z]+/([^"\']+)["\']', 'apps_path'),
    (r'["\']tests/([^"\']+)["\']', 'tests_path'),
    
    # Path() constructor patterns
    (r'Path\(["\']([^"\']+)["\']', 'path_constructor'),
    
    # os.path.join patterns
    (r'os\.path\.join\([^)]*["\']([^"\']+)["\'][^)]*\)', 'os_path_join'),
]

def should_exclude_path(path: Path) -> bool:
    """Check if path should be excluded from scanning."""
    parts_lower = {p.lower() for p in path.parts}
    if parts_lower & {d.lower() for d in EXCLUDED_DIRS}:
        return True
    if path.name in EXCLUDED_FILES:
        return True
    return False

def categorize_path(path_str: str) -> str:
    """Categorize a path into SSOT candidate types."""
    path_lower = path_str.lower()
    
    # Agent discovery files
    if 'agent_discovery_full.json' in path_lower:
        return 'agent_discovery_json'
    if 'agent_discovery_full.manifest.json' in path_lower:
        return 'agent_discovery_manifest_json'
    
    # Layer directories
    if any(f'l{i}_' in path_lower for i in range(7)):
        return 'layer_directory'
    
    # Common directories
    if path_lower.startswith('agentic_core/'):
        return 'agentic_core_subdir'
    if path_lower.startswith('scripts/'):
        return 'scripts_subdir'
    if path_lower.startswith('tests/'):
        return 'tests_subdir'
    if path_lower.startswith('apps_'):
        return 'apps_subdir'
    
    # Specific known paths
    if 'dashboard' in path_lower:
        return 'dashboard_related'
    if 'blueprint_sovereign' in path_lower:
        return 'blueprint_sovereign'
    
    return 'other'

def scan_file(file_path: Path) -> Dict[str, List[Tuple[int, str, str]]]:
    """Scan a single file for hardcoded paths.
    
    Returns:
        Dict mapping category -> list of (line_num, matched_text, full_line)
    """
    findings = defaultdict(list)
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip import lines that use structure_blueprint
            if 'from agentic_core.L5_safety.validators.structure_blueprint_1 import' in line:
                continue
            if 'structure_blueprint' in line and 'import' in line:
                continue
            
            # Check each pattern
            for pattern, pattern_type in PATH_PATTERNS:
                matches = re.finditer(pattern, line)
                for match in matches:
                    matched_text = match.group(0)
                    # Extract the path part
                    if match.groups():
                        path_part = match.group(1)
                    else:
                        path_part = matched_text.strip('"\'')
                    
                    category = categorize_path(path_part)
                    findings[category].append((line_num, matched_text, line.strip()))
    
    except Exception as e:
        pass
    
    return findings

def scan_repository() -> Dict[str, Dict[str, List]]:
    """Scan entire repository for hardcoded paths.
    
    Returns:
        Dict mapping category -> files -> list of findings
    """
    print("=" * 80)
    print("HARDCODED PATH SCANNER")
    print("=" * 80)
    print(f"\n📂 Scanning: {PROJECT_ROOT}")
    print(f"🚫 Excluding: {', '.join(sorted(EXCLUDED_DIRS)[:5])}...\n")
    
    all_findings = defaultdict(lambda: defaultdict(list))
    files_scanned = 0
    
    # Scan all Python files
    for py_file in PROJECT_ROOT.rglob('*.py'):
        if should_exclude_path(py_file):
            continue
        
        files_scanned += 1
        findings = scan_file(py_file)
        
        for category, issues in findings.items():
            if issues:
                rel_path = py_file.relative_to(PROJECT_ROOT)
                all_findings[category][str(rel_path)].extend(issues)
    
    print(f"✅ Scanned {files_scanned} Python files\n")
    return all_findings

def generate_report(findings: Dict[str, Dict[str, List]]) -> None:
    """Generate detailed report of findings."""
    print("=" * 80)
    print("HARDCODED PATH REPORT")
    print("=" * 80)
    print()
    
    # Summary by category
    category_counts = {cat: sum(len(issues) for issues in files.values()) 
                       for cat, files in findings.items()}
    
    if not category_counts:
        print("✅ No hardcoded paths found!")
        return
    
    print("📊 SUMMARY BY CATEGORY")
    print("-" * 80)
    for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        file_count = len(findings[category])
        print(f"   {category:30} {count:4} occurrences in {file_count:3} files")
    print()
    
    # Detailed findings
    print("=" * 80)
    print("DETAILED FINDINGS")
    print("=" * 80)
    print()
    
    for category in sorted(findings.keys()):
        files_dict = findings[category]
        total_count = sum(len(issues) for issues in files_dict.values())
        
        print(f"\n{'=' * 80}")
        print(f"CATEGORY: {category.upper()}")
        print(f"Total: {total_count} occurrences in {len(files_dict)} files")
        print(f"{'=' * 80}\n")
        
        # Show top 10 files with most occurrences
        sorted_files = sorted(files_dict.items(), key=lambda x: -len(x[1]))
        for file_path, issues in sorted_files[:10]:
            print(f"\n📄 {file_path}")
            print(f"   {len(issues)} occurrence(s):")
            for line_num, matched, full_line in issues[:3]:  # Show first 3
                print(f"      Line {line_num}: {matched}")
            if len(issues) > 3:
                print(f"      ... and {len(issues) - 3} more")
    
    # SSOT Recommendations
    print("\n\n" + "=" * 80)
    print("SSOT RECOMMENDATIONS")
    print("=" * 80)
    print()
    print("Suggested constants to add to structure_blueprint.py:")
    print()
    
    recommendations = []
    
    if 'agent_discovery_json' in findings:
        recommendations.append('AGENT_DISCOVERY_JSON = "agent_discovery_full.json"')
    if 'agent_discovery_manifest_json' in findings:
        recommendations.append('AGENT_DISCOVERY_MANIFEST_JSON = "agent_discovery_full.manifest.json"')
    if 'scripts_subdir' in findings:
        recommendations.append('SCRIPTS_DIR = "scripts"')
    if 'tests_subdir' in findings:
        recommendations.append('TESTS_DIR = "tests"')
    
    for rec in recommendations:
        print(f"   {rec}")
    
    if not recommendations:
        print("   (Review detailed findings to determine appropriate SSOT constants)")

def main():
    findings = scan_repository()
    generate_report(findings)
    
    # Save detailed report to file
    report_path = PROJECT_ROOT / "hardcoded_paths_report.json"
    import json
    with open(report_path, 'w', encoding='utf-8') as f:
        # Convert defaultdict to regular dict for JSON
        json_data = {cat: dict(files) for cat, files in findings.items()}
        json.dump(json_data, f, indent=2)
    
    print(f"\n\n💾 Detailed report saved to: {report_path}")

if __name__ == "__main__":
    main()
