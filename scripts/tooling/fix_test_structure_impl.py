"""Implementation for fix_test_structure."""

from typing import Any, Dict, List, Optional

def flatten_unit_tests() -> List[str]:
    """
    Flatten unit tests by removing L/P folder nesting.
    Move all tests from unit/domain/L*/P*/ to unit/domain/
    """
    moved = []
    unit_dir = TESTS_ROOT / 'unit'
    if not unit_dir.exists():
        return moved
    for domain_dir in unit_dir.iterdir():
        if not domain_dir.is_dir():
            continue
        for test_file in domain_dir.rglob('test_*.py'):
            rel_to_domain = test_file.relative_to(domain_dir)
            has_lp = any((p in str(rel_to_domain) for p in FORBIDDEN_PATTERNS))
            if has_lp:
                dest = domain_dir / test_file.name
                if dest.exists() and dest != test_file:
                    stem = dest.stem
                    suffix = dest.suffix
                    counter = 1
                    while dest.exists():
                        dest = domain_dir / f'{stem}_{counter}{suffix}'
                        counter += 1
                if test_file != dest:
                    shutil.move(str(test_file), str(dest))
                    moved.append(f'{test_file.relative_to(TESTS_ROOT)} -> {dest.relative_to(TESTS_ROOT)}')
    return moved

def _remove_lp_dirs_in_domain(domain_dir: Path) -> List[str]:
    """Remove L/P pattern directories in a single domain."""
    removed = []
    for lp_pattern in FORBIDDEN_PATTERNS:
        for lp_dir in domain_dir.rglob(lp_pattern):
            if lp_dir.is_dir():
                try:
                    contents = list(lp_dir.iterdir())
                    if not contents or all((f.name == '__init__.py' for f in contents)):
                        shutil.rmtree(lp_dir)
                        removed.append(str(lp_dir.relative_to(TESTS_ROOT)))
                except (ValueError, TypeError, KeyError) as e:
                    print(f'Error removing {lp_dir}: {e}')
    return removed

def _clean_empty_dirs(unit_dir: Path) -> List[str]:
    """Clean empty directories after removing L/P patterns."""
    removed = []
    for dirpath, dirnames, filenames in os.walk(unit_dir, topdown=False):
        current = Path(dirpath)
        if current == unit_dir:
            continue
        rel_path = str(current.relative_to(unit_dir))
        if any((pattern in rel_path for pattern in FORBIDDEN_PATTERNS)):
            try:
                contents = list(current.iterdir())
                if not contents or all((f.name == '__init__.py' for f in contents)):
                    shutil.rmtree(current)
                    removed.append(str(current.relative_to(TESTS_ROOT)))
            except (ValueError, TypeError, KeyError) as e:
                print(f'Error removing {current}: {e}')
    return removed

def remove_empty_lp_dirs() -> List[str]:
    """Remove empty L/P directories after flattening."""
    removed = []
    unit_dir = TESTS_ROOT / 'unit'
    if not unit_dir.exists():
        return removed
    for domain_dir in unit_dir.iterdir():
        if not domain_dir.is_dir():
            continue
        removed.extend(_remove_lp_dirs_in_domain(domain_dir))
    removed.extend(_clean_empty_dirs(unit_dir))
    return removed

def move_logic_tests() -> List[str]:
    """Move tests from logic/ to appropriate categories."""
    moved = []
    logic_dir = TESTS_ROOT / 'logic'
    if not logic_dir.exists():
        return moved
    for test_file in logic_dir.glob('test_*.py'):
        if test_file.name in LOGIC_REMAP:
            category, subcategory = LOGIC_REMAP[test_file.name]
            dest_dir = TESTS_ROOT / category / subcategory
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / test_file.name
            if not dest.exists():
                shutil.move(str(test_file), str(dest))
                moved.append(f'logic/{test_file.name} -> {category}/{subcategory}/{test_file.name}')
        else:
            dest_dir = TESTS_ROOT / 'unit' / 'agentic_core'
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / test_file.name
            if not dest.exists():
                shutil.move(str(test_file), str(dest))
                moved.append(f'logic/{test_file.name} -> unit/agentic_core/{test_file.name}')
        if logic_dir.exists():
            remaining = [f for f in logic_dir.iterdir() if f.name not in ['__init__.py', '__pycache__']]
            if not remaining:
                shutil.rmtree(logic_dir)
                moved.append('Removed empty logic/ folder')
    return moved

def ensure_init_files() -> int:
    """Ensure all test directories have __init__.py."""
    created = 0
    for dirpath, dirnames, filenames in os.walk(TESTS_ROOT):
        current = Path(dirpath)
        init_file = current / '__init__.py'
        if not init_file.exists():
            init_file.write_text('"""Test package."""\n')
            created += 1
    return created

def main() -> None:
    """Main entry point for test structure fixing."""
    log = {'flattened': [], 'removed_dirs': [], 'moved_logic': [], 'init_files_created': 0}
    log['flattened'] = flatten_unit_tests()
    for item in log['flattened'][:5]:
        print(f'  - {item}')
    if len(log['flattened']) > 5:
        print(f"  ... and {len(log['flattened']) - 5} more")
    log['removed_dirs'] = remove_empty_lp_dirs()
    log['moved_logic'] = move_logic_tests()
    for item in log['moved_logic']:
        print(f'  - {item}')
    log['init_files_created'] = ensure_init_files()
    log_path = REPO_ROOT / 'fix_test_structure_log.json'
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2)

