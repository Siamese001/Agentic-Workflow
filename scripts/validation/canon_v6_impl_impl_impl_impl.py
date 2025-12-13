"""Implementation for canon_v6_impl_impl_impl."""

from typing import Any, Dict, List, Optional

def clean_debug_statements(file_path: str) -> None:
    """Remove print, pdb, and breakpoint statements from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        original_lines = content.count('\n')
        content = re.sub('^\\s*print\\(.*\\)\\s*$', '', content, flags=re.MULTILINE)
        content = re.sub('^\\s*pdb\\.\\w+.*$', '', content, flags=re.MULTILINE)
        content = re.sub('^\\s*breakpoint\\(\\)\\s*$', '', content, flags=re.MULTILINE)
        content = re.sub('\\n\\s*\\n\\s*\\n', '\n\n', content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        cleaned_lines = content.count('\n')
        return original_lines - cleaned_lines
    except Exception as e:
        return 0

def get_file_hash(file_path: str) -> str:
    """Get SHA256 hash of file"""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def analyze_file_complexity(file_path: str) -> Dict[str, int]:
    """Get simple complexity metrics"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        code_lines = sum((1 for line in lines if line.strip() and (not line.strip().startswith('#'))))
        file_size = os.path.getsize(file_path)
        return {'lines': code_lines, 'size': file_size, 'hash': get_file_hash(file_path)}
    except (OSError, IOError, UnicodeDecodeError):
        return {'lines': 0, 'size': 0, 'hash': ''}

def canonicalize_filename(encoded_name: str) -> str:
    """Convert path-encoded filename back to clean name"""
    prefixes = ['agentic_core_', 'apps_shared_', 'apps_rg_', 'apps_lic_', 'schemas_', 'config_', 'docs_', 'observability_', 'data_']
    clean_name = encoded_name
    for prefix in prefixes:
        if clean_name.startswith(prefix):
            clean_name = clean_name[len(prefix):]
            break
    return clean_name

def _find_encoded_files(base_dir: Path) -> list:
    """Find all path-encoded files."""
    encoded_files = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'archive_code', 'archives']]
        for file in files:
            if file.endswith('.py') or file.endswith('.json') or file.endswith('.md'):
                if '_' in file and file.count('_') >= 2:
                    full_path = Path(root) / file
                    encoded_files.append(full_path)
    return encoded_files

def _group_by_canonical_target(encoded_files: list) -> dict:
    """Group files by their canonical target."""
    target_groups = defaultdict(list)
    for file_path in encoded_files:
        canonical_name = canonicalize_filename(file_path.name)
        target_path = file_path.parent / canonical_name
        target_groups[str(target_path)].append(file_path)
    return target_groups

def _process_duplicates(target_groups: dict) -> int:
    """Process duplicate files and return count of deleted duplicates."""
    deleted_duplicates = 0
    for target_path, candidates in target_groups.items():
        if len(candidates) > 1:
            analyses = []
            for candidate in candidates:
                analysis = analyze_file_complexity(candidate)
                analyses.append((candidate, analysis))
            best = max(analyses, key=lambda x: (x[1]['lines'], x[1]['size']))
            for candidate, analysis in analyses:
                if candidate != best[0]:
                    candidate.unlink()
                    deleted_duplicates += 1
    return deleted_duplicates

def _find_dirty_files(base_dir: Path) -> list:
    """Find files with debug statements."""
    dirty_files = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'archive_code', 'archives']]
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'print(' in content or 'pdb.' in content or 'breakpoint()' in content:
                        dirty_files.append(file_path)
    return dirty_files

def _clean_files(dirty_files: list) -> int:
    """Clean debug statements from files and return count of cleaned files."""
    cleaned_files = 0
    for file_path in dirty_files:
        lines_removed = clean_debug_statements(file_path)
        if lines_removed > 0:
            cleaned_files += 1
    return cleaned_files

def _rename_to_canonical(base_dir: Path) -> int:
    """Rename files to canonical names and return count of renamed files."""
    renamed_files = 0
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'archive_code', 'archives']]
        for file in files:
            if file.endswith('.py') or file.endswith('.json') or file.endswith('.md'):
                file_path = Path(root) / file
                if '_' in file and file.count('_') >= 2:
                    canonical_name = canonicalize_filename(file)
                    target_path = file_path.parent / canonical_name
                    if file_path != target_path and (not target_path.exists()):
                        file_path.rename(target_path)
                        renamed_files += 1
    return renamed_files

def main() -> None:
    """Main function to canonicalize filenames by removing banned prefixes."""
    base_dir = Path('.')
    encoded_files = _find_encoded_files(base_dir)
    target_groups = _group_by_canonical_target(encoded_files)
    deleted_duplicates = _process_duplicates(target_groups)
    dirty_files = _find_dirty_files(base_dir)
    cleaned_files = _clean_files(dirty_files)
    renamed_files = _rename_to_canonical(base_dir)
    apps_rg_count = len(list(Path('apps_rg').rglob('*.py'))) if Path('apps_rg').exists() else 0

