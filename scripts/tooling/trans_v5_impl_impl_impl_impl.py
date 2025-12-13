"""Implementation for trans_v5_impl_impl_impl."""

from typing import Any, Dict, List, Optional

def is_banned_name(name: str) -> bool:
    """Check if a folder/file name matches banned patterns."""
    for pattern in BANNED_PATTERNS:
        if re.match(pattern, name, re.IGNORECASE):
            return True
    return False

def get_new_filename(old_name: str) -> str:
    """Get the new filename based on rename mappings."""
    return RENAME_MAPPINGS.get(old_name, old_name)

def collect_py_files(directory: Path) -> List[Path]:
    """Recursively collect all .py files in a directory."""
    if not directory.exists():
        return []
    return list(directory.rglob('*.py'))

def ensure_init_py(directory: Path) -> None:
    """Ensure __init__.py exists in directory."""
    init_file = directory / '__init__.py'
    if not init_file.exists():
        init_file.write_text('"""Auto-generated __init__.py for subatomic canon 2025."""\n')

def move_file_with_rename(src: Path, dest_dir: Path, apply_rename: bool=True) -> Path:
    """Move a file to destination directory, optionally applying rename mappings."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    new_name = get_new_filename(src.name) if apply_rename else src.name
    dest_path = dest_dir / new_name
    if dest_path.exists() and dest_path != src:
        stem = dest_path.stem
        suffix = dest_path.suffix
        counter = 1
        while dest_path.exists():
            dest_path = dest_dir / f'{stem}_{counter}{suffix}'
            counter += 1
    if src != dest_path:
        shutil.move(str(src), str(dest_path))
    return dest_path

def flatten_layer(layer_path: Path, layer_name: str) -> Dict[str, List[str]]:
    """
    Flatten a layer by moving all files from P* subdirectories to the layer root.
    Returns a log of operations performed.
    """
    log = {'moved': [], 'deleted_dirs': [], 'renamed': []}
    if not layer_path.exists():
        return log
    phase_dirs = [d for d in layer_path.iterdir() if d.is_dir() and d.name.startswith('P')]
    for phase_dir in phase_dirs:
        py_files = collect_py_files(phase_dir)
        for py_file in py_files:
            if py_file.name == '__init__.py':
                continue
            new_path = move_file_with_rename(py_file, layer_path)
            log['moved'].append(f'{py_file} -> {new_path}')
            if py_file.name != new_path.name:
                log['renamed'].append(f'{py_file.name} -> {new_path.name}')
    try:
        shutil.rmtree(phase_dir)
        log['deleted_dirs'].append(str(phase_dir))
    except (ValueError, TypeError, KeyError) as e:
        log['errors'].append(f'Failed to delete {phase_dir}: {e}')
    ensure_init_py(layer_path)
    return log

def quarantine_l4_non_retrieve(l4_path: Path) -> Dict[str, List[str]]:
    """
    Quarantine L4_memory phases other than P1_retrieve.
    """
    log = {'quarantined': [], 'kept': []}
    if not l4_path.exists():
        return log
    quarantine_dir = l4_path / QUARANTINE_L4
    for item in l4_path.iterdir():
        if not item.is_dir():
            continue
        if item.name.startswith('P') and item.name not in L4_ALLOWED_PHASES:
            dest = quarantine_dir / item.name
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item), str(dest))
            log['quarantined'].append(f'{item.name} -> {dest}')
        elif item.name in L4_ALLOWED_PHASES:
            log['kept'].append(item.name)
    return log

def delete_banned_folders(root: Path) -> List[str]:
    """
    Delete all folders matching banned patterns.
    Promotes files up before deletion.
    """
    deleted = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        current_dir = Path(dirpath)
        for dirname in dirnames:
            if is_banned_name(dirname):
                banned_dir = current_dir / dirname
                for py_file in collect_py_files(banned_dir):
                    if py_file.name != '__init__.py':
                        move_file_with_rename(py_file, current_dir)
    try:
        shutil.rmtree(banned_dir)
        deleted.append(str(banned_dir))
    except (ValueError, TypeError, KeyError) as e:
        log['errors'].append(f'Failed to delete {banned_dir}: {e}')
    return deleted

def apply_file_renames(root: Path) -> List[str]:
    """
    Apply rename mappings to all .py files.
    """
    renamed = []
    for py_file in root.rglob('*.py'):
        if py_file.name in RENAME_MAPPINGS:
            new_name = RENAME_MAPPINGS[py_file.name]
            new_path = py_file.parent / new_name
            if not new_path.exists():
                py_file.rename(new_path)
                renamed.append(f'{py_file} -> {new_path}')
    return renamed

def update_meta_yaml(yaml_path: Path) -> None:
    """Update unified_structure_subatomic_meta.yaml with new cognitive_layer_phase_rules."""
    content = yaml_path.read_text(encoding='utf-8')
    new_rules = 'cognitive_layer_phase_rules:\n    L1_cognition:\n      allowed_phases: [P1_retrieve, P2_inspect, P3_aggregate, P4_safety]\n    L2_execution:\n      allowed_phases: []\n    L3_orchestration:\n      allowed_phases: []\n    L4_memory:\n      allowed_phases: [P1_retrieve]\n    L5_safety:\n      allowed_phases: []'
    content = re.sub('cognitive_layer_phase_rules:.*?L5_safety:\\s*\\n\\s*allowed_phases:.*?\\]', new_rules, content, flags=re.DOTALL)
    if 'subatomic_canon_2025:' not in content:
        canon_section = '\n# ---------------------------------------------------------------------\n# 11. SUBATOMIC CANON 2025 — FINAL\n# ---------------------------------------------------------------------\nsubatomic_canon_2025:\n  enforced: true\n  principles_applied:\n    - only_three_agents_have_L1_L5\n    - only_L1_has_phases\n    - L2_L3_L5_flat\n    - L4_retrieval_only\n    - imperative_verb_naming\n    - banned_low_signal_words\n    - natural_depth_no_padding\n    - self_teaching_names\n'
        content += canon_section
    yaml_path.write_text(content, encoding='utf-8')

def update_main_yaml(yaml_path: Path) -> None:
    """Update unified_structure_subatomic.yaml to reflect flat structure."""
    content = yaml_path.read_text(encoding='utf-8')
    content = content.replace('agentic_core', 'agentic_core')
    yaml_path.write_text(content, encoding='utf-8')

def fix_imports_in_file(file_path: Path, old_to_new: Dict[str, str]) -> bool:
    """Fix imports in a single Python file based on rename mappings."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        for old_name, new_name in old_to_new.items():
            old_module = old_name.replace('.py', '')
            new_module = new_name.replace('.py', '')
            content = re.sub(f'\\bfrom\\s+(\\S+\\.)?{re.escape(old_module)}\\b', f'from \\1{new_module}', content)
            content = re.sub(f'\\bimport\\s+(\\S+\\.)?{re.escape(old_module)}\\b', f'import \\1{new_module}', content)
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except (ValueError, TypeError, KeyError) as e:
        return False

def fix_all_imports(root: Path) -> int:
    """Fix imports across the entire repository."""
    fixed_count = 0
    for py_file in root.rglob('*.py'):
        if fix_imports_in_file(py_file, RENAME_MAPPINGS):
            fixed_count += 1
    return fixed_count

def main() -> None:
    """Main entry point for subatomic canon 2025 transform."""
    all_logs = {'flattened_layers': {}, 'quarantined_l4': {}, 'deleted_banned': [], 'renamed_files': [], 'fixed_imports': 0}
    for root in COGNITIVE_ROOTS:
        for layer in FLAT_LAYERS:
            layer_path = root / layer
            if layer_path.exists():
                log = flatten_layer(layer_path, layer)
                key = f'{root.name}/{layer}'
                all_logs['flattened_layers'][key] = log
    for root in COGNITIVE_ROOTS:
        l4_path = root / 'L4_memory'
        if l4_path.exists():
            log = quarantine_l4_non_retrieve(l4_path)
            key = f'{root.name}/L4_memory'
            all_logs['quarantined_l4'][key] = log
    for root in COGNITIVE_ROOTS:
        deleted = delete_banned_folders(root)
        all_logs['deleted_banned'].extend(deleted)
    for root in COGNITIVE_ROOTS:
        renamed = apply_file_renames(root)
        all_logs['renamed_files'].extend(renamed)
    meta_yaml = REPO_ROOT / 'unified_structure_subatomic_meta.yaml'
    main_yaml = REPO_ROOT / 'unified_structure_subatomic.yaml'
    if meta_yaml.exists():
        update_meta_yaml(meta_yaml)
    if main_yaml.exists():
        update_main_yaml(main_yaml)
    fixed = fix_all_imports(REPO_ROOT)
    all_logs['fixed_imports'] = fixed
    log_path = REPO_ROOT / 'subatomic_canon_2025_transform_log.json'
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(all_logs, f, indent=2, default=str)
