#!/usr/bin/env python3
"""Comprehensive scan for all SOVEREIGN_TERRITORIES references in production code."""

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# Files that are part of the definition layer (allowed to use SOVEREIGN_TERRITORIES)
DEFINITION_FILES = {
    'ssot.py', '_constants.py', 'derived.py', 'territories.py',
    '__init__.py', '_verify.py', 'structure_blueprint_config.py',
    'blueprint_compiler.py', 'registry_config.py'
}

def scan_file(filepath: Path) -> dict:
    """Scan a single file for SOVEREIGN_TERRITORIES references."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')

        if 'SOVEREIGN_TERRITORIES' not in content:
            return None

        # Count different types of references
        import_matches = re.findall(r'(?:from|import).*SOVEREIGN_TERRITORIES', content)
        usage_matches = re.findall(r'SOVEREIGN_TERRITORIES(?:\.|\.get|\[|\.items|\.keys|\.values)', content)

        total_count = content.count('SOVEREIGN_TERRITORIES')
        import_count = len(import_matches)
        usage_count = len(usage_matches)
        comment_count = total_count - import_count - usage_count

        return {
            'imports': import_count,
            'usages': usage_count,
            'comments': comment_count,
            'total': total_count,
            'import_lines': import_matches[:3],  # Sample
            'usage_lines': usage_matches[:3]     # Sample
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    """Run comprehensive scan."""
    results = defaultdict(list)

    # Scan agentic_core production code
    for filepath in (ROOT / 'agentic_core').rglob('*.py'):
        if '__pycache__' in str(filepath):
            continue

        rel_path = str(filepath.relative_to(ROOT))

        # Categorize
        if any(df in filepath.name for df in DEFINITION_FILES):
            category = 'definition_layer'
        elif 'L5_safety/reasoning/' in rel_path or 'L5_safety/enforcement/' in rel_path:
            category = 'enforcement_reasoning'
        elif 'L0_routing/scripts/' in rel_path:
            category = 'l0_scripts'
        else:
            category = 'production_other'

        scan_result = scan_file(filepath)
        if scan_result:
            results[category].append((rel_path, scan_result))

    # Print results
    print("=" * 80)
    print("COMPREHENSIVE SOVEREIGN_TERRITORIES SCAN")
    print("=" * 80)

    for category in ['enforcement_reasoning', 'l0_scripts', 'production_other', 'definition_layer']:
        files = results.get(category, [])
        if not files:
            continue

        print(f"\n{category.upper().replace('_', ' ')}: {len(files)} files")
        print("-" * 80)

        # Show critical files (imports or usages)
        critical = [(f, r) for f, r in files if r.get('imports', 0) > 0 or r.get('usages', 0) > 0]

        if critical:
            print(f"  CRITICAL (has imports/usages): {len(critical)}")
            for filepath, result in sorted(critical):
                if 'error' in result:
                    print(f"    {filepath}: ERROR - {result['error']}")
                else:
                    print(f"    {filepath}")
                    print(f"      Imports: {result['imports']}, Usages: {result['usages']}, Comments: {result['comments']}")
                    if result.get('import_lines'):
                        print(f"      Sample import: {result['import_lines'][0][:80]}")

        # Show comment-only files
        comments_only = [(f, r) for f, r in files if r.get('imports', 0) == 0 and r.get('usages', 0) == 0]
        if comments_only:
            print(f"\n  COMMENTS ONLY: {len(comments_only)}")
            for filepath, _ in sorted(comments_only)[:5]:
                print(f"    {filepath}")
            if len(comments_only) > 5:
                print(f"    ... and {len(comments_only) - 5} more")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    all_critical = []
    for category, files in results.items():
        critical = [(f, r) for f, r in files if r.get('imports', 0) > 0 or r.get('usages', 0) > 0]
        all_critical.extend(critical)

    print(f"Total files with SOVEREIGN_TERRITORIES: {sum(len(files) for files in results.values())}")
    print(f"Critical files (imports/usages): {len(all_critical)}")
    print(f"Definition layer files: {len(results.get('definition_layer', []))}")

    # List all critical non-definition files
    non_def_critical = [(f, r) for f, r in all_critical
                        if not any(df in f for df in DEFINITION_FILES)]

    if non_def_critical:
        print(f"\n⚠️  NON-DEFINITION FILES WITH IMPORTS/USAGES: {len(non_def_critical)}")
        for filepath, result in sorted(non_def_critical):
            print(f"  ❌ {filepath}")
            print(f"     Imports: {result['imports']}, Usages: {result['usages']}")
    else:
        print("\n✅ All critical references are in definition layer only!")

if __name__ == '__main__':
    main()
