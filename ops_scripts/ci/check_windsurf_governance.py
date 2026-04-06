#!/usr/bin/env python3
"""
Windsurf Governance Health Check

Validates:
1. Cross-references resolve (no broken links to archived files)
2. RULES_INDEX.md accuracy matches actual files
3. No duplicate content across rules/skills/workflows
"""

import re
import sys
from pathlib import Path

WINDSURF_DIR = Path('.windsurf')
ARCHIVE_DIR = Path('tools/archive/.windsurf')


def check_cross_references():
    """Check for references to archived files"""
    issues = []
    
    if not ARCHIVE_DIR.exists():
        print("  ⚠️  Archive directory not found, skipping cross-reference check")
        return issues
    
    archived_files = {f.name for f in ARCHIVE_DIR.rglob('*.md')}
    
    if not archived_files:
        print("  ⚠️  No archived files found, skipping cross-reference check")
        return issues
    
    for md_file in WINDSURF_DIR.rglob('*.md'):
        # Skip skills and workflows directories - they legitimately reference archived files (consolidation docs)
        if 'skills' in str(md_file) or 'workflows' in str(md_file):
            continue
            
        content = md_file.read_text(encoding='utf-8')
        
        # Check for references to archived files
        for archived_name in archived_files:
            if archived_name in content:
                # Allow references in deprecation headers
                if "DEPRECATED" in content or "archived" in content.lower():
                    continue
                issues.append(f"{md_file}: references archived {archived_name}")
    
    return issues


def validate_rules_index():
    """Check RULES_INDEX.md against actual files"""
    index_file = WINDSURF_DIR / 'RULES_INDEX.md'
    
    if not index_file.exists():
        return ["RULES_INDEX.md not found"]
    
    content = index_file.read_text(encoding='utf-8')
    issues = []
    
    # Extract file paths from index (matches `.windsurf/...` patterns, excluding globs)
    referenced_files = re.findall(r'`\.windsurf/[^*`]+\.md`', content)
    
    for ref in referenced_files:
        ref = ref.strip('`')
        ref_path = Path(ref)
        
        if not ref_path.exists():
            # Check if it's in archive (allow references to archived files in index)
            archive_path = ARCHIVE_DIR / ref_path.name
            if not archive_path.exists():
                issues.append(f"RULES_INDEX references non-existent: {ref}")
    
    return issues


def check_duplicate_content():
    """Check for duplicate sections across files within same category"""
    issues = []
    
    # Only check within categories (rules, workflows, skills) to avoid false positives
    # Plans and templates are excluded since they use standard headers
    categories = {
        'rules': WINDSURF_DIR / 'rules',
        'workflows': WINDSURF_DIR / 'workflows',
        'skills': WINDSURF_DIR / 'skills',
    }
    
    # Common template headers to exclude from duplicate check
    common_headers = {
        'Files', 'When to use', 'When to Use',
        'Constitutional Requirements Enforced',
        'Enforcement Scripts',
        'Forbidden Patterns',
        'Evidence Requirements',
        'References',
        'Quick Commands',
        'CI Integration',
    }
    
    for _, category_dir in categories.items():
        if not category_dir.exists():
            continue
        
        # Check for duplicate ## headers within category
        rule_headers = {}
        for md_file in category_dir.rglob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            # Find all ## headers (but skip ### subheaders)
            headers = re.findall(r'^##\s+([^#].+)$', content, re.MULTILINE)
            for header in headers:
                # Skip common template headers
                if header in common_headers:
                    continue
                    
                if header in rule_headers and rule_headers[header] != md_file:
                    issues.append(
                        f"Duplicate header '{header}' in {md_file} "
                        f"and {rule_headers[header]}"
                    )
                else:
                    rule_headers[header] = md_file
    
    return issues


def main():
    print("Windsurf Governance Health Check")
    print("=" * 50)
    
    if not WINDSURF_DIR.exists():
        print("❌ .windsurf directory not found")
        sys.exit(1)
    
    all_issues = []
    
    print("\n1. Cross-reference check...")
    issues = check_cross_references()
    if issues:
        all_issues.extend(issues)
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print("  ✅ No broken references to archived files")
    
    print("\n2. RULES_INDEX validation...")
    issues = validate_rules_index()
    if issues:
        all_issues.extend(issues)
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print("  ✅ RULES_INDEX accurate")
    
    print("\n3. Duplicate content check...")
    issues = check_duplicate_content()
    if issues:
        all_issues.extend(issues)
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print("  ✅ No duplicate headers found")
    
    if all_issues:
        print(f"\n❌ {len(all_issues)} issues found")
        sys.exit(1)
    else:
        print("\n✅ All checks passed")
        sys.exit(0)


if __name__ == '__main__':
    main()
