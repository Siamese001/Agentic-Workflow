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


def has_real_code(path: Path) -> bool:
    """Check if file has real implementation beyond stubs."""
    try:
        content = path.read_text(encoding='utf-8', errors='ignore')
                if 'DO NOT implement logic here' in content:
            return False
        if 'AUTO-GENERATED ZERO-LOSS' in content and 'Phase 3 hydration' in content:
            return False
        if 'PENDING[HUMAN_OWNER]' in content and 'Unmapped legacy' in content:
            return False
        # Check for actual class/function definitions with bodies
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                # Check if next non-empty line is pass/...
                for j in range(i+1, min(i+5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and next_line not in ('pass', '...', '"""', "'''"):
                        if not next_line.startswith('#') and not next_line.startswith('"'):
                            return True
        return False
    except (ValueError, TypeError, KeyError):
        return False


def main():
    # Build index of approved files
    print("Building index of approved files...")
    approved_by_name = {}

    for folder in APPROVED_FOLDERS:
        folder_path = REPO / folder
        if not folder_path.exists():
            continue
        for f in folder_path.rglob('*.py'):
            if 'review_pending' in str(f) or '__pycache__' in str(f):
                continue
            approved_by_name.setdefault(f.name, []).append(f)

    # Scan review_pending
    print(f"Scanning {REVIEW_PENDING}...")

    pending_files = [f for f in REVIEW_PENDING.rglob('*.py') if '__pycache__' not in str(f)]

    # Categorize
    pending_has_more_code = []
    pending_is_stub = []
    pending_same_or_less = []
    pending_unique_with_code = []
    pending_unique_stub = []

    for f in pending_files:
        pending_real = count_real_lines(f)
        pending_has_code = has_real_code(f)

        if f.name in approved_by_name:
            approved_files = approved_by_name[f.name]
            max_approved_real = max(count_real_lines(a) for a in approved_files)

            if pending_real > max_approved_real and pending_has_code:
                pending_has_more_code.append((f, pending_real, max_approved_real))
            elif not pending_has_code:
                pending_is_stub.append(f)
            else:
                pending_same_or_less.append(f)
        else:
            if pending_has_code:
                pending_unique_with_code.append((f, pending_real))
            else:
                pending_unique_stub.append(f)

    # Report
    print("\n" + "=" * 80)
    print("DEEP ANALYSIS RESULTS")
    print("=" * 80)

    print(f"\nPENDING HAS MORE CODE THAN APPROVED: {len(pending_has_more_code)}")
    for f, pending_lines, approved_lines in pending_has_more_code[:20]:
        print(f"  {f.name}: pending={pending_lines} vs approved={approved_lines}")

    print(f"\nPENDING IS STUB (name match exists): {len(pending_is_stub)}")

    print(f"\nPENDING SAME OR LESS CODE: {len(pending_same_or_less)}")

    print(f"\nUNIQUE WITH REAL CODE: {len(pending_unique_with_code)}")
    for f, lines in pending_unique_with_code[:20]:
        print(f"  {f.relative_to(REVIEW_PENDING)}: {lines} real lines")

    print(f"\nUNIQUE STUBS: {len(pending_unique_stub)}")

    # Final recommendation
    print("\n" + "=" * 80)
    print("FINAL RECOMMENDATION")
    print("=" * 80)

    total_files = len(pending_files)
    safe_to_archive = len(pending_is_stub) + len(pending_same_or_less) + len(pending_unique_stub)
    needs_review = len(pending_has_more_code) + len(pending_unique_with_code)

    print(f"  Total files: {total_files}")
    print(f"  Safe to archive (stubs/duplicates): {safe_to_archive}")
    print(f"  Needs manual review: {needs_review}")

    if needs_review == 0:
        print("\n  ✓ ALL FILES ARE STUBS OR DUPLICATES - SAFE TO MOVE TO 06_data/deprecated/")
    else:
        print(f"\n  ⚠ {needs_review} files need content review before archival")


if __name__ == '__main__':
    main()
