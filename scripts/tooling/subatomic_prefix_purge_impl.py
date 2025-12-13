"""Implementation for subatomic_prefix_purge."""

from typing import Any, Dict, List, Optional

def rename_top_level_folders() -> List[str]:
    """Rename all numbered folders to their clean names."""
    renamed = []
    for old_name, new_name in FOLDER_RENAMES.items():
        old_path = REPO_ROOT / old_name
        new_path = REPO_ROOT / new_name
        if old_path.exists() and (not new_path.exists()):
            shutil.move(str(old_path), str(new_path))
            renamed.append(f'{old_name} -> {new_name}')
        elif old_path.exists() and new_path.exists():
            for item in old_path.iterdir():
                dest = new_path / item.name
                if not dest.exists():
                    shutil.move(str(item), str(dest))
            shutil.rmtree(old_path)
            renamed.append(f'{old_name} -> {new_name} (merged)')
    return renamed

def _promote_app(apps_dir: Path, app_name: str) -> Optional[str]:
    """Promote a single app from 09_apps/ to top-level."""
    src = apps_dir / app_name
    dst = REPO_ROOT / app_name
    if src.exists() and (not dst.exists()):
        shutil.move(str(src), str(dst))
        return f'09_apps/{app_name} -> {app_name}'
    return None

def _cleanup_remaining_apps_dir(apps_dir: Path, log: Dict[str, List[str]]) -> None:
    """Clean up remaining items in apps directory after promotion."""
    remaining = list(apps_dir.iterdir())
    if len(remaining) == 0:
        apps_dir.rmdir()
    else:
        for item in remaining:
            if item.name == 'shared':
                dest = REPO_ROOT / 'apps_shared'
                if not dest.exists():
                    shutil.move(str(item), str(dest))
            else:
                dest = REPO_ROOT / item.name
                if not dest.exists():
                    shutil.move(str(item), str(dest))
        try:
            shutil.rmtree(apps_dir)
            log['deleted_dirs'].append(str(apps_dir))
        except (ValueError, TypeError, KeyError) as e:
            log['errors'].append(f'Failed to delete {apps_dir}: {e}')

def promote_apps_to_top_level() -> List[str]:
    """Promote apps_lic and apps_rg from 09_apps/ to top-level."""
    promoted = []
    apps_dir = REPO_ROOT / '09_apps'
    if not apps_dir.exists():
        return promoted
    result = _promote_app(apps_dir, 'apps_lic')
    if result:
        promoted.append(result)
    result = _promote_app(apps_dir, 'apps_rg')
    if result:
        promoted.append(result)
        promoted.append('09_apps/apps_rg -> apps_rg')
        if apps_dir.exists():
            _cleanup_remaining_apps_dir(apps_dir, log)
    return promoted

def fix_imports_in_file(file_path: Path) -> bool:
    """Fix imports in a single Python file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        for old_path, new_path in IMPORT_RENAMES.items():
            if not old_path:
                continue
            if new_path:
                content = re.sub(f'\\bfrom\\s+{re.escape(old_path)}\\.(\\S+)', f'from {new_path}.\\1', content)
                content = re.sub(f'\\bfrom\\s+{re.escape(old_path)}\\b', f'from {new_path}', content)
                content = re.sub(f'\\bimport\\s+{re.escape(old_path)}\\.(\\S+)', f'import {new_path}.\\1', content)
                content = re.sub(f'\\bimport\\s+{re.escape(old_path)}\\b', f'import {new_path}', content)
            else:
                content = re.sub(f'\\bfrom\\s+{re.escape(old_path)}\\.(\\S+)', 'from \\1', content)
                content = re.sub(f'\\bimport\\s+{re.escape(old_path)}\\.(\\S+)', 'import \\1', content)
        for old_path, new_path in IMPORT_RENAMES.items():
            if old_path and new_path:
                content = content.replace(f'"{old_path}/', f'"{new_path}/')
                content = content.replace(f"'{old_path}/", f"'{new_path}/")
                content = content.replace(f'"{old_path}"', f'"{new_path}"')
                content = content.replace(f"'{old_path}'", f"'{new_path}'")
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except (ValueError, TypeError, KeyError) as e:
        return False

def fix_all_imports() -> int:
    """Fix imports across the entire repository."""
    fixed_count = 0
    for py_file in REPO_ROOT.rglob('*.py'):
        if any((part.startswith('.') or part == '__pycache__' for part in py_file.parts)):
            continue
        if fix_imports_in_file(py_file):
            fixed_count += 1
    return fixed_count

def update_yaml_files() -> None:
    """Update both YAML SSoT files with new folder names."""
    main_yaml = REPO_ROOT / 'unified_structure_subatomic.yaml'
    if main_yaml.exists():
        content = main_yaml.read_text(encoding='utf-8')
        for old_name, new_name in FOLDER_RENAMES.items():
            content = content.replace(old_name, new_name)
        content = content.replace('09_apps/apps_lic', 'apps_lic')
        content = content.replace('09_apps/apps_rg', 'apps_rg')
        content = content.replace('09_apps.', '')
        content = content.replace('09_apps:', '# 09_apps removed - apps_lic and apps_rg are now top-level')
        main_yaml.write_text(content, encoding='utf-8')
    meta_yaml = REPO_ROOT / 'unified_structure_subatomic_meta.yaml'
    if meta_yaml.exists():
        content = meta_yaml.read_text(encoding='utf-8')
        for old_name, new_name in FOLDER_RENAMES.items():
            content = content.replace(old_name, new_name)
        content = content.replace('09_apps/apps_lic', 'apps_lic')
        content = content.replace('09_apps/apps_rg', 'apps_rg')
        content = content.replace('09_apps.', '')
        if 'numbered_folder_exception:' not in content:
            exception_section = '\n# ---------------------------------------------------------------------\n# 12. NUMBERED FOLDER EXCEPTION — ETERNAL LAW\n# ---------------------------------------------------------------------\nnumbered_folder_exception:\n  "06_data":\n    reason: "Pure curated knowledge plane — never imported as code"\n    permanent: true\n'
            content += exception_section
        meta_yaml.write_text(content, encoding='utf-8')

def update_workspace_file() -> None:
    """Update the VS Code workspace file."""
    workspace_file = REPO_ROOT / 'Agentic.code-workspace'
    if workspace_file.exists():
        content = workspace_file.read_text(encoding='utf-8')
        for old_name, new_name in FOLDER_RENAMES.items():
            content = content.replace(old_name, new_name)
        content = content.replace('09_apps', 'apps_lic')
        workspace_file.write_text(content, encoding='utf-8')

def update_ssot_validator() -> None:
    """Update the SSOT validator script."""
    validator = REPO_ROOT / 'SSOT_validator.py'
    if validator.exists():
        content = validator.read_text(encoding='utf-8')
        for old_name, new_name in FOLDER_RENAMES.items():
            content = content.replace(f'"{old_name}"', f'"{new_name}"')
            content = content.replace(f"'{old_name}'", f"'{new_name}'")
            content = content.replace(f'"{old_name}/', f'"{new_name}/')
            content = content.replace(f"'{old_name}/", f"'{new_name}/")
        content = content.replace('"09_apps"', '"apps_lic", "apps_rg"')
        validator.write_text(content, encoding='utf-8')

def main() -> None:
    """Main entry point for subatomic prefix purge."""
    log = {'renamed_folders': [], 'promoted_apps': [], 'fixed_imports': 0, 'yaml_updated': True}
    log['renamed_folders'] = rename_top_level_folders()
    log['promoted_apps'] = promote_apps_to_top_level()
    log['fixed_imports'] = fix_all_imports()
    update_yaml_files()
    update_workspace_file()
    update_ssot_validator()
    log_path = REPO_ROOT / 'subatomic_prefix_purge_log.json'
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, default=str)

