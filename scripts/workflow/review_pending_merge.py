#!/usr/bin/env python3
"""
Deep comparison of review_pending files vs approved files.
Determine if any review_pending files have MORE content than approved versions.
"""

from pathlib import Path

REPO = Path('c:/Git/Agentic-Workflow')
REVIEW_PENDING = REPO / 'config/review_pending'

APPROVED_FOLDERS = [
    'agentic_core',
    'schemas',
    'runtime',
    'prompt_governance',
    'config',
    'observability',
    'scripts',
    '09_apps',
    'shared',
    'shared_engine_ops',
]

def count_real_lines(path: Path) -> int:
    """Count non-empty, non-comment, non-docstring lines."""
    try:
        content = path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        real = 0
        in_docstring = False
        for line in lines:
            stripped = line.strip()
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
                continue
            if in_docstring:
                continue
            if not stripped or stripped.startswith('#'):
                continue
            if stripped.startswith('from __future__') or stripped.startswith('import '):
                continue
            real += 1
        return real
    except (ValueError, TypeError, KeyError):
        return 0

def _is_stub_marker(content: str) -> bool:
    """Check if content has stub markers."""
    if 'DO NOT implement logic here' in content:
        return True
    if 'AUTO-GENERATED ZERO-LOSS' in content and 'Phase 3 hydration' in content:
        return True
    if 'PENDING[HUMAN_OWNER]' in content and 'Unmapped historical' in content:
        return True
    return False

def _has_real_implementation(lines: List[str], i: int) -> bool:
    """Check if function/class has real implementation."""
    for j in range(i+1, min(i+5, len(lines))):
        next_line = lines[j].strip()
        if not next_line or next_line in ('pass', '...', '"""', "'''"):
            continue
        if next_line.startswith('#') or next_line.startswith('"'):
            continue
        return True
    return False

def has_real_code(path: Path) -> bool:
    """Check if file has real implementation beyond stubs."""
    try:
        content = path.read_text(encoding='utf-8', errors='ignore')
        if _is_stub_marker(content):
            return False
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                if _has_real_implementation(lines, i):
                    return True
        return False
    except (ValueError, TypeError, KeyError):
        return False

def _build_approved_name_index() -> Dict[str, List[Path]]:
    """Build index of approved files by name."""
    approved_by_name = {}
    
    for folder in APPROVED_FOLDERS:
        folder_path = REPO / folder
        if not folder_path.exists():
            continue
        for f in folder_path.rglob('*.py'):
            if 'review_pending' in str(f) or '__pycache__' in str(f):
                continue
            approved_by_name.setdefault(f.name, []).append(f)
    
    return approved_by_name

def _categorize_pending_file(f: Path, approved_by_name: Dict[str, List[Path]]) -> Dict[str, Any]:
    """Categorize a pending file based on comparison with approved versions."""
    pending_real = count_real_lines(f)
    pending_has_code = has_real_code(f)
    
    result = {
        "file": f,
        "pending_real": pending_real,
        "pending_has_code": pending_has_code,
        "category": None
    }
    
    if f.name in approved_by_name:
        # Compare with approved versions
        for approved in approved_by_name[f.name]:
            approved_real = count_real_lines(approved)
            approved_has_code = has_real_code(approved)
            
            if pending_real > approved_real and pending_has_code:
                result["category"] = "has_more_code"
                break
            elif pending_has_code and not approved_has_code:
                result["category"] = "has_code_vs_stub"
                break
            elif pending_real <= approved_real:
                result["category"] = "same_or_less"
                break
    else:
        # Unique file
        if pending_has_code:
            result["category"] = "unique_with_code"
        else:
            result["category"] = "unique_stub"
    
    return result

def _categorize_files(pending_files: List[Path], approved_by_name: Dict[str, List[Path]]) -> Dict[str, List[Path]]:
    """Categorize pending files into different buckets."""
    categories = {
        "has_more_code": [],
        "has_code_vs_stub": [],
        "same_or_less": [],
        "unique_with_code": [],
        "unique_stub": []
    }
    
    for f in pending_files:
        category_info = _categorize_pending_file(f, approved_by_name)
        category = category_info["category"]
        if category in categories:
            categories[category].append(f)
    
    return categories

def main() -> None:
    """Main entry point for review pending merge."""
    approved_by_name = _build_approved_name_index()
    pending_files = [f for f in REVIEW_PENDING.rglob('*.py') if '__pycache__' not in str(f)]
    
    categories = _categorize_files(pending_files, approved_by_name)
    pending_has_more_code = categories["has_more_code"]
    pending_is_stub = categories["has_code_vs_stub"]
    pending_same_or_less = categories["same_or_less"]
    pending_unique_with_code = categories["unique_with_code"]
    pending_unique_stub = categories["unique_stub"]

    # Report results
    print(f"\nFiles with more code than approved versions ({len(pending_has_more_code)}):")
    for f in pending_has_more_code[:20]:
        print(f"  - {f.relative_to(REVIEW_PENDING)}")
    
    print(f"\nStubs replacing real code ({len(pending_is_stub)}):")
    for f in pending_is_stub[:20]:
        print(f"  - {f.relative_to(REVIEW_PENDING)}")
    
    print(f"\nUnique files with real code ({len(pending_unique_with_code)}):")
    for f in pending_unique_with_code[:20]:
        print(f"  - {f.relative_to(REVIEW_PENDING)}")
    
    print(f"\nUnique stub files ({len(pending_unique_stub)}):")
    for f in pending_unique_stub[:20]:
        print(f"  - {f.relative_to(REVIEW_PENDING)}")

    # Final recommendation

    total_files = len(pending_files)
    safe_to_archive = len(pending_is_stub) + len(pending_same_or_less) + len(pending_unique_stub)
    needs_review = len(pending_has_more_code) + len(pending_unique_with_code)

    if needs_review == 0:
        print("\n✓ All files can be safely archived!")
    else:
        print(f"\n⚠ {needs_review} files need review before archiving")

if __name__ == '__main__':
    main()
