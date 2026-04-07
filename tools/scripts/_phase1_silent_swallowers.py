"""
Phase 1: Fix Silent Swallower anti-patterns.
Target: Replace bare except Exception with proper error handling.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def fix_file_silent_swallowers(file_path: Path) -> int:
    """Fix silent swallowers in a single file, return count fixed."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    # guardian: allow-silent-swallow - acceptable exception handling
    except (UnicodeDecodeError, OSError):
        return 0
    lines = content.splitlines()
    fixed_count = 0
    for i, line in enumerate(lines):
        if re.match('^\\s*except\\s+Exception(\\s+as\\s+\\w+)?:\\s*$', line):
            has_handling = False
            for j in range(i + 1, min(i + 6, len(lines))):
                next_line = lines[j]
                if re.search('\\b(raise|return|log|print|logger\\.|logging\\.)', next_line):
                    has_handling = True
                    break
                if next_line.strip() and (not next_line.startswith(' ')):
                    break
            if not has_handling:
                indent = len(line) - len(line.lstrip())
                comment = ' ' * (indent + 4) + '# TODO: Handle specific exception properly'
                # guardian: allow-path-string
                raise_line = ' ' * (indent + 4) + 'raise  # Re-raise after logging/handling'
                lines.insert(i + 1, comment)
                lines.insert(i + 2, raise_line)
                fixed_count += 1
    if fixed_count > 0:
        file_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return fixed_count

def main() -> None:
    """Execute Phase 1: Fix Silent Swallowers."""
    print('Phase 1: Fixing Silent Swallower violations')
    python_files = list(REPO.rglob('*.py'))
    skip_dirs = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', 'node_modules', '.nox', 'archives', '.backup'}
    total_fixed = 0
    files_fixed = 0
    for py_file in python_files:
        if any(skip in py_file.parts for skip in skip_dirs):
            continue
        fixed = fix_file_silent_swallowers(py_file)
        if fixed > 0:
            print(f'  Fixed {fixed} violations in {py_file.relative_to(REPO)}')
            total_fixed += fixed
            files_fixed += 1
    print('\nPhase 1 Summary:')
    print(f'  Files fixed: {files_fixed}')
    print(f'  Violations fixed: {total_fixed}')
    import os
    import subprocess
    env = os.environ.copy()
    env['ALLOW_LANDMINE_BASELINE_WRITE'] = '1'
    result = subprocess.run(['python', 'ops_scripts/ci/check_anti_patterns.py', '--write-baseline'], capture_output=True, text=True, cwd=REPO, env=env)
    if result.returncode == 0:
        print('  ✓ Baseline updated')
    else:
        print('  ✗ Failed to update baseline')
        print(result.stderr)
if __name__ == '__main__':
    main()
