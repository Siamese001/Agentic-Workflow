"""
Verification Script: Identify Intentional Variants vs True Duplicates

This script distinguishes between:
1. TRUE DUPLICATES: Same filename, identical content → Safe to delete
2. INTENTIONAL VARIANTS: Same filename, different content → Need renaming via NamingAgent

Purpose: Prevent accidental deletion of intentional variants that just need better names.
"""
import sys
from pathlib import Path
from collections import defaultdict
import hashlib
import re
from archives.location_violations.file_utils import safe_read_file, safe_write_file

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of file content."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return "ERROR"


def read_file_content(file_path: Path) -> str:
    """Read file content as string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""


def extract_key_identifiers(content: str, file_ext: str) -> dict:
    """Extract key identifiers from file content to determine if it's a variant."""
    identifiers = {
        'classes': set(),
        'functions': set(),
        'imports': set(),
        'constants': set(),
        'has_main': False
    }
    
    if file_ext == '.py':
        # Extract Python-specific identifiers
        identifiers['classes'] = set(re.findall(r'class\s+(\w+)', content))
        identifiers['functions'] = set(re.findall(r'def\s+(\w+)', content))
        identifiers['imports'] = set(re.findall(r'(?:from|import)\s+([\w.]+)', content))
        identifiers['constants'] = set(re.findall(r'^([A-Z_]{2,})\s*=', content, re.MULTILINE))
        identifiers['has_main'] = 'if __name__' in content
    
    return identifiers


def analyze_variant_likelihood(file1: Path, file2: Path) -> dict:
    """
    Analyze if two files with same name are intentional variants or true duplicates.
    
    Returns:
        dict with 'is_variant', 'confidence', 'reasons'
    """
    content1 = read_file_content(file1)
    content2 = read_file_content(file2)
    
    if not content1 or not content2:
        return {'is_variant': False, 'confidence': 'unknown', 'reasons': ['Cannot read files']}
    
    # Check if identical
    if content1 == content2:
        return {'is_variant': False, 'confidence': 'certain', 'reasons': ['Files are identical']}
    
    # Extract identifiers
    ext = file1.suffix
    ids1 = extract_key_identifiers(content1, ext)
    ids2 = extract_key_identifiers(content2, ext)
    
    reasons = []
    variant_score = 0
    
    # Check for different class names (strong indicator of variant)
    if ids1['classes'] and ids2['classes']:
        if ids1['classes'] != ids2['classes']:
            reasons.append(f"Different classes: {ids1['classes']} vs {ids2['classes']}")
            variant_score += 3
        else:
            reasons.append("Same class names (likely duplicate)")
            variant_score -= 2
    
    # Check for different function sets (moderate indicator)
    if ids1['functions'] and ids2['functions']:
        func_diff = ids1['functions'].symmetric_difference(ids2['functions'])
        if len(func_diff) > 3:
            reasons.append(f"Significantly different functions: {len(func_diff)} differences")
            variant_score += 2
        elif len(func_diff) > 0:
            reasons.append(f"Minor function differences: {len(func_diff)} differences")
            variant_score += 1
    
    # Check for different imports (weak indicator)
    if ids1['imports'] and ids2['imports']:
        import_diff = ids1['imports'].symmetric_difference(ids2['imports'])
        if len(import_diff) > 5:
            reasons.append(f"Different imports: {len(import_diff)} differences")
            variant_score += 1
    
    # Check location patterns (strong indicator)
    path1_str = str(file1)
    path2_str = str(file2)
    
    if 'config/blueprint_sovereign' in path1_str or 'config/blueprint_sovereign' in path2_str:
        reasons.append("One file in deprecated blueprint folder (likely stale copy)")
        variant_score -= 2
    
    if ('L5_safety' in path1_str and 'L2_execution' in path2_str) or \
       ('L2_execution' in path1_str and 'L5_safety' in path2_str):
        reasons.append("Files in different layers (L2 vs L5) - likely intentional variants")
        variant_score += 2
    
    # Calculate line difference percentage
    lines1 = len(content1.splitlines())
    lines2 = len(content2.splitlines())
    if lines1 > 0:
        line_diff_pct = abs(lines1 - lines2) / max(lines1, lines2) * 100
        if line_diff_pct > 30:
            reasons.append(f"Significant size difference: {line_diff_pct:.1f}% line count difference")
            variant_score += 1
    
    # Determine verdict
    if variant_score >= 3:
        return {'is_variant': True, 'confidence': 'high', 'reasons': reasons, 'score': variant_score}
    elif variant_score >= 1:
        return {'is_variant': True, 'confidence': 'medium', 'reasons': reasons, 'score': variant_score}
    elif variant_score <= -2:
        return {'is_variant': False, 'confidence': 'high', 'reasons': reasons, 'score': variant_score}
    else:
        return {'is_variant': False, 'confidence': 'low', 'reasons': reasons, 'score': variant_score}


def scan_for_duplicates():
    """Scan project for duplicate files."""
    file_hashes = defaultdict(list)
    extensions = {'.py', '.html', '.json', '.yaml', '.md', '.txt'}
    exclude_dirs = {'__pycache__', '.git', 'node_modules', 'venv', '.venv', 'archive'}
    
    for file_path in project_root.rglob('*'):
        if not file_path.is_file():
            continue
        if any(excluded in file_path.parts for excluded in exclude_dirs):
            continue
        if file_path.suffix not in extensions:
            continue
        
        file_hash = compute_file_hash(file_path)
        if file_hash != "ERROR":
            file_hashes[file_hash].append(file_path)
    
    return {h: paths for h, paths in file_hashes.items() if len(paths) > 1}


def main():
    print("=" * 120)
    print("INTENTIONAL VARIANTS VERIFICATION")
    print("Distinguishing between true duplicates and intentional variants needing rename")
    print("=" * 120)
    print()
    
    # Scan for duplicates
    print("[1/3] Scanning for duplicate files...")
    duplicates = scan_for_duplicates()
    print(f"   Found {len(duplicates)} duplicate sets")
    print()
    
    # Group by filename
    print("[2/3] Grouping by filename...")
    by_filename = defaultdict(list)
    for file_hash, paths in duplicates.items():
        for path in paths:
            by_filename[path.name].append({'path': path, 'hash': file_hash})
    
    filename_groups = {name: files for name, files in by_filename.items() if len(files) > 1}
    print(f"   Found {len(filename_groups)} filename groups with duplicates")
    print()
    
    # Analyze each group
    print("[3/3] Analyzing for intentional variants...")
    print()
    
    true_duplicates = []
    intentional_variants = []
    needs_review = []
    
    for filename, file_info in sorted(filename_groups.items()):
        # Check if all hashes are the same (identical content)
        hashes = set(f['hash'] for f in file_info)
        
        if len(hashes) == 1:
            # All identical - true duplicates
            true_duplicates.append((filename, file_info))
        else:
            # Different content - analyze if intentional variant
            paths = [f['path'] for f in file_info]
            
            # Analyze pairwise
            max_variant_score = 0
            max_analysis = None
            
            for i in range(len(paths)):
                for j in range(i + 1, len(paths)):
                    analysis = analyze_variant_likelihood(paths[i], paths[j])
                    score = analysis.get('score', 0)
                    if score > max_variant_score:
                        max_variant_score = score
                        max_analysis = analysis
            
            if max_analysis and max_analysis.get('is_variant') and max_analysis.get('confidence') in ['high', 'medium']:
                intentional_variants.append((filename, file_info, max_analysis))
            else:
                needs_review.append((filename, file_info, max_analysis))
    
    print()
    print("=" * 120)
    print("ANALYSIS RESULTS")
    print("=" * 120)
    print()
    
    # Summary
    print(f"SUMMARY:")
    print(f"  ✓ True Duplicates (safe to delete): {len(true_duplicates)}")
    print(f"  ⚠ Intentional Variants (need rename): {len(intentional_variants)}")
    print(f"  ? Needs Manual Review: {len(needs_review)}")
    print()
    
    # Show intentional variants
    if intentional_variants:
        print("=" * 120)
        print("INTENTIONAL VARIANTS - REQUIRE RENAMING VIA NamingAgent")
        print("=" * 120)
        print()
        
        for idx, (filename, file_info, analysis) in enumerate(intentional_variants, 1):
            print(f"[{idx}] {filename}")
            print(f"    Copies: {len(file_info)}")
            print(f"    Variant Confidence: {analysis['confidence'].upper()}")
            print(f"    Variant Score: {analysis['score']}")
            print()
            print(f"    Reasons:")
            for reason in analysis['reasons']:
                print(f"      - {reason}")
            print()
            print(f"    Locations:")
            for f in file_info:
                rel_path = f['path'].relative_to(project_root)
                print(f"      {rel_path}")
            print()
            print(f"    ⚠️  ACTION REQUIRED:")
            print(f"       DO NOT DELETE - These files have different functionality")
            print(f"       Use NamingAgent to suggest unique names for each variant")
            print(f"       Command: python -m agentic_core.utils.core_extensions.NamingAgent --file {file_info[0]['path']}")
            print()
            print("-" * 120)
            print()
    
    # Show needs review
    if needs_review:
        print("=" * 120)
        print("NEEDS MANUAL REVIEW - Unclear if variant or duplicate")
        print("=" * 120)
        print()
        
        for idx, (filename, file_info, analysis) in enumerate(needs_review, 1):
            print(f"[{idx}] {filename}")
            print(f"    Copies: {len(file_info)}")
            if analysis:
                print(f"    Analysis Score: {analysis['score']}")
                print(f"    Reasons: {', '.join(analysis['reasons'][:2])}")
            print(f"    Locations: {len(file_info)} files")
            print()
    
    # Show true duplicates summary
    print("=" * 120)
    print("TRUE DUPLICATES - SAFE TO DELETE")
    print("=" * 120)
    print()
    print(f"Found {len(true_duplicates)} filename groups with identical content")
    print(f"Total files to delete: {sum(len(files) - 1 for _, files in true_duplicates)}")
    print()
    print("These files have identical content and can be safely deleted via:")
    print("  python scripts/delete_duplicates.py --execute")
    print()
    
    # Final recommendations
    print()
    print("=" * 120)
    print("NEXT STEPS")
    print("=" * 120)
    print()
    print("1. INTENTIONAL VARIANTS (DO NOT DELETE):")
    print(f"   - {len(intentional_variants)} filename groups need renaming")
    print("   - Use NamingAgent to suggest unique names")
    print("   - Rename files to reflect their different purposes")
    print()
    print("2. TRUE DUPLICATES (SAFE TO DELETE):")
    print(f"   - {len(true_duplicates)} filename groups are identical")
    print("   - Run: python scripts/delete_duplicates.py --execute")
    print()
    print("3. NEEDS REVIEW:")
    print(f"   - {len(needs_review)} filename groups need manual inspection")
    print("   - Review diff and decide: rename or delete")
    print()
    
    # Save results
    output_file = project_root / "variant_analysis_results.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("INTENTIONAL VARIANTS - DO NOT DELETE\n")
        f.write("=" * 80 + "\n\n")
        for filename, file_info, analysis in intentional_variants:
            f.write(f"{filename}\n")
            for fi in file_info:
                f.write(f"  {fi['path'].relative_to(project_root)}\n")
            f.write("\n")
    
    print(f"Detailed results saved to: {output_file}")
    print()


if __name__ == "__main__":
    main()
