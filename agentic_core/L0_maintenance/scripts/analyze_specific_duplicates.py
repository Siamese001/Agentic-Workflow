"""
Focused analysis on specific duplicate files mentioned by user.
Analyzes CodeDeduplicationAgent and FilenameUniquenessGuardianAgent duplicates.
"""
import sys
from pathlib import Path
import hashlib
import difflib

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
    except Exception as e:
        return f"ERROR: {e}"


def analyze_functional_differences(file1: Path, file2: Path):
    """Analyze functional differences between two Python files."""
    content1 = read_file_content(file1)
    content2 = read_file_content(file2)
    
    if "ERROR" in content1 or "ERROR" in content2:
        return {"error": "Could not read files"}
    
    # Check if identical
    if content1 == content2:
        return {"identical": True, "diff_lines": 0}
    
    # Generate diff
    diff = list(difflib.unified_diff(
        content1.splitlines(keepends=True),
        content2.splitlines(keepends=True),
        fromfile=str(file1.name),
        tofile=str(file2.name),
        lineterm=''
    ))
    
    # Count significant differences (ignore whitespace-only)
    significant_diffs = [line for line in diff if line.startswith(('+', '-')) and not line.startswith(('+++', '---')) and line.strip() not in ('+', '-')]
    
    # Extract class names
    import re
    classes1 = set(re.findall(r'class\s+(\w+)', content1))
    classes2 = set(re.findall(r'class\s+(\w+)', content2))
    
    # Extract function names
    functions1 = set(re.findall(r'def\s+(\w+)', content1))
    functions2 = set(re.findall(r'def\s+(\w+)', content2))
    
    return {
        "identical": False,
        "diff_lines": len(significant_diffs),
        "classes1": classes1,
        "classes2": classes2,
        "functions1": functions1,
        "functions2": functions2,
        "diff_preview": diff[:50]  # First 50 lines of diff
    }


def main():
    print("=" * 120)
    print("FOCUSED DUPLICATE ANALYSIS - CodeDeduplicationAgent & FilenameUniquenessGuardianAgent")
    print("=" * 120)
    print()
    
    # Files to analyze
    files_to_check = [
        ("CodeDeduplicationAgent.py", [
            "agentic_core/L2_execution/ToolRegistry/CodeDeduplicationAgent.py",
            "agentic_core/L5_safety/guardrails/DuplicateCodeDetectorAgent.py"
        ]),
        ("FilenameUniquenessGuardianAgent.py", [
            "agentic_core/L5_safety/validators/FilenameUniquenessGuardianAgent.py",
            "agentic_core/config/blueprint_sovereign/FilenameUniquenessGuardianAgent.py"
        ])
    ]
    
    for filename, paths in files_to_check:
        print("=" * 120)
        print(f"ANALYZING: {filename}")
        print("=" * 120)
        print()
        
        # Convert to Path objects
        file_paths = [project_root / p.replace('/', '\\') for p in paths]
        
        # Check which files exist
        existing_files = [f for f in file_paths if f.exists()]
        
        if len(existing_files) < 2:
            print(f"⚠️  Only {len(existing_files)} of {len(file_paths)} files exist")
            for f in file_paths:
                status = "✓ EXISTS" if f.exists() else "✗ MISSING"
                print(f"   {status}: {f.relative_to(project_root)}")
            print()
            continue
        
        # Show file info
        print("FILES FOUND:")
        for i, f in enumerate(existing_files, 1):
            rel_path = f.relative_to(project_root)
            size = f.stat().st_size
            file_hash = compute_file_hash(f)
            
            # Classify location
            if 'config/blueprint_sovereign' in str(rel_path):
                location = "STALE (Blueprint)"
            elif 'L5_safety/validators' in str(rel_path):
                location = "CANONICAL (L5)"
            elif 'L2_execution/ToolRegistry' in str(rel_path):
                location = "CANONICAL (L2)"
            elif 'L5_safety/guardrails' in str(rel_path):
                location = "CANONICAL (L5 Guardrails)"
            else:
                location = "REVIEW"
            
            print(f"  [{i}] {rel_path}")
            print(f"      Location: {location}")
            print(f"      Size: {size:,} bytes")
            print(f"      Hash: {file_hash[:16]}...")
            print()
        
        # Compare files
        if len(existing_files) == 2:
            print("-" * 120)
            print("FUNCTIONAL ANALYSIS:")
            print("-" * 120)
            print()
            
            analysis = analyze_functional_differences(existing_files[0], existing_files[1])
            
            if analysis.get("identical"):
                print("✓ FILES ARE IDENTICAL")
                print()
                print("RECOMMENDATION:")
                print("  - Keep: Canonical location (L5_safety or L2_execution)")
                print("  - Delete: Blueprint/stale location")
                print("  - Action: Safe to delete duplicate")
                print()
            else:
                print("✗ FILES HAVE DIFFERENT CONTENT")
                print()
                print(f"Difference metrics:")
                print(f"  - Changed lines: {analysis['diff_lines']}")
                print(f"  - Classes in file 1: {', '.join(sorted(analysis['classes1'])) if analysis['classes1'] else 'None'}")
                print(f"  - Classes in file 2: {', '.join(sorted(analysis['classes2'])) if analysis['classes2'] else 'None'}")
                print(f"  - Functions in file 1: {len(analysis['functions1'])}")
                print(f"  - Functions in file 2: {len(analysis['functions2'])}")
                print()
                
                # Show class/function differences
                class_diff = analysis['classes1'].symmetric_difference(analysis['classes2'])
                func_diff = analysis['functions1'].symmetric_difference(analysis['functions2'])
                
                if class_diff:
                    print(f"Class differences: {', '.join(sorted(class_diff))}")
                if func_diff:
                    print(f"Function differences: {', '.join(sorted(list(func_diff)[:10]))}{'...' if len(func_diff) > 10 else ''}")
                print()
                
                print("DIFF PREVIEW (first 30 lines):")
                print("-" * 120)
                for line in analysis['diff_preview'][:30]:
                    print(line.rstrip())
                print("-" * 120)
                print()
                
                print("RECOMMENDATION:")
                print("  1. Review functional differences above")
                print("  2. If functions are truly different:")
                print("     - Use FilenameUniquenessGuardianAgent to suggest unique name")
                print("     - Rename the non-canonical copy")
                print("  3. If functions are similar but evolved:")
                print("     - Consolidate into canonical location")
                print("     - Delete stale copy")
                print("  4. If unsure:")
                print("     - Run CodeDeduplicationAgent for deeper analysis")
                print()
        
        print()
    
    # Summary
    print()
    print("=" * 120)
    print("SUMMARY & NEXT STEPS")
    print("=" * 120)
    print()
    print("Based on the analysis above:")
    print()
    print("1. For IDENTICAL files:")
    print("   - Safe to delete blueprint/stale copies")
    print("   - Keep canonical locations in L5_safety or L2_execution")
    print()
    print("2. For DIFFERENT files:")
    print("   - Review diff preview to understand changes")
    print("   - Use FilenameUniquenessGuardianAgent to suggest rename")
    print("   - Or consolidate if functions have evolved")
    print()
    print("3. Commands to run:")
    print("   - Delete identical: python scripts/delete_duplicates.py --execute")
    print("   - Analyze different: python -m agentic_core.L2_execution.ToolRegistry.CodeDeduplicationAgent")
    print("   - Suggest renames: python -m agentic_core.L5_safety.validators.FilenameUniquenessGuardianAgent")
    print()


if __name__ == "__main__":
    main()
