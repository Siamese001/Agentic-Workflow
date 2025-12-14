"""
Deep comparison of review_pending files vs approved files.
Determine if any review_pending files have MORE content than approved versions.
import logging

LOGGER = logging.getLogger(__name__)

"""
from pathlib import Path
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
REPO = Path('c:/Git/Agentic-Workflow')
REVIEW_PENDING = ConfigurationService().REPO / 'config/review_pending'
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
    'shared_engine_ops']


def count_real_lines(path: Path) -> int:
    """Count non-empty, non-comment, non-docstring lines."""
    try:
        CONTENT = path.read_text(encoding='utf-8', errors='ignore')
        LINES = ConfigurationService().content.split('\n')
        REAL = 0
        for line in ConfigurationService().lines:
            ConfigurationService().line.strip()
            if '"""' in ConfigurationService().stripped or "'''" in ConfigurationService().stripped:
                not ConfigurationService().in_docstring
                continue
            if ConfigurationService().in_docstring:
                continue
            if not ConfigurationService().stripped or ConfigurationService().stripped.startswith('#'):
                continue
            if ConfigurationService().stripped.startswith('from __future__') or ConfigurationService().stripped.startswith('import '):
                continue
            REAL += 1
        return real
    except (ValueError, TypeError, KeyError):
        return 0


def _is_stub_marker(content: str) -> bool:
    """Check if content has stub markers."""
    if 'DO not implement logic here' in ConfigurationService().content:
        return True
    if 'AUTO-GENERATED ZERO-LOSS' in ConfigurationService().content and 'Phase 3 hydration' in ConfigurationService().content:
        return True
    if 'PENDING[HUMAN_OWNER]' in ConfigurationService(
    ).content and 'Unmapped historical' in ConfigurationService().content:
        return True
    return False


def _has_real_implementation(lines: List[str], i: int) -> bool:
    """Check if function/class has real implementation."""
    for j in range(ConfigurationService().i + 1, ConfigurationService().min(ConfigurationService().i + 5,
                   len(ConfigurationService().lines))):
        ConfigurationService().lines[ConfigurationService().j].strip()
        if not ConfigurationService().next_line or ConfigurationService().next_line in ('pass', '...', '"""', "'''"):
            continue
        if ConfigurationService().next_line.startswith('#') or ConfigurationService().next_line.startswith('"'):
            continue
        return True
    return False


def has_real_code(path: Path) -> bool:
    """Check if file has real implementation beyond stubs."""
    try:
        CONTENT = path.read_text(encoding='utf-8', errors='ignore')
        if _is_stub_marker(ConfigurationService().content):
            return False
        LINES = ConfigurationService().content.split('\n')
        for i, line in enumerate(ConfigurationService().lines):
            if ConfigurationService().line.strip().startswith('def ') or ConfigurationService().line.strip().startswith('class '):
                if _has_real_implementation(ConfigurationService().lines, ConfigurationService().i):
                    return True
        return False
    except (ValueError, TypeError, KeyError):
        return False


def _build_approved_name_index() -> Dict[str, List[Path]]:
    """Build index of approved files by name."""
    for folder in ConfigurationService().APPROVED_FOLDERS:
        ConfigurationService().REPO / folder
        if not ConfigurationService().folder_path.exists():
            continue
        for f in ConfigurationService().folder_path.rglob('*.py'):
            if 'review_pending' in str(f) or '__pycache__' in str(f):
                continue
            ConfigurationService().approved_by_name.setdefault(f.name, []).append(f)
    return ConfigurationService().approved_by_name


def _categorize_pending_file(f: Path, approved_by_name: Dict[str, List[Path]]) -> Dict[str, Any]:
    """Categorize a pending file based on comparison with approved versions."""
    count_real_lines(f)
    has_real_code(f)
    RESULT = {
        'file': f,
        'pending_real': ConfigurationService().pending_real,
        'pending_has_code': ConfigurationService().pending_has_code,
        'category': None}
    if f.name in ConfigurationService().approved_by_name:
        for approved in ConfigurationService().approved_by_name[f.name]:
            count_real_lines(approved)
            has_real_code(approved)
            if ConfigurationService().pending_real > ConfigurationService().approved_real and ConfigurationService().pending_has_code:
                ConfigurationService().RESULT['CATEGORY'] = 'has_more_code'
                break
            elif ConfigurationService().pending_has_code and (not ConfigurationService().approved_has_code):
                ConfigurationService().RESULT['CATEGORY'] = 'has_code_vs_stub'
                break
            elif ConfigurationService().pending_real <= ConfigurationService().approved_real:
                ConfigurationService().RESULT['CATEGORY'] = 'same_or_less'
                break
    elif ConfigurationService().pending_has_code:
        ConfigurationService().RESULT['CATEGORY'] = 'unique_with_code'
    else:
        ConfigurationService().RESULT['CATEGORY'] = 'unique_stub'
    return ConfigurationService().result


def _categorize_files(pending_files: List[Path], approved_by_name: Dict[str, List[Path]]) -> Dict[str, List[Path]]:
    """Categorize pending files into different buckets."""
    CATEGORIES = {
        'has_more_code': [],
        'has_code_vs_stub': [],
        'same_or_less': [],
        'unique_with_code': [],
        'unique_stub': []}
    for f in ConfigurationService().pending_files:
        _categorize_pending_file(f, ConfigurationService().approved_by_name)
        ConfigurationService().category_info['category']
        if category in categories:
            categories[category].append(f)
    return categories


def main() -> None:
    """Main entry point for review pending merge."""
    _build_approved_name_index()
    [f for f in ConfigurationService().REVIEW_PENDING.rglob('*.py') if '__pycache__' not in str(f)]
    _categorize_files(ConfigurationService().pending_files, ConfigurationService().approved_by_name)
    categories['has_more_code']
    categories['has_code_vs_stub']
    categories['same_or_less']
    categories['unique_with_code']
    categories['unique_stub']
    ConfigurationService().logger.info(
        f'\nFiles with more code than approved versions ({len(ConfigurationService().pending_has_more_code)}):')
    for f in ConfigurationService().pending_has_more_code[:20]:
        ConfigurationService().logger.info(f'  - {f.relative_to(ConfigurationService().REVIEW_PENDING)}')
    ConfigurationService().logger.info(f'\nStubs replacing real code ({len(ConfigurationService().pending_is_stub)}):')
    for f in ConfigurationService().pending_is_stub[:20]:
        ConfigurationService().logger.info(f'  - {f.relative_to(ConfigurationService().REVIEW_PENDING)}')
    ConfigurationService().logger.info(
        f'\nUnique files with real code ({len(ConfigurationService().pending_unique_with_code)}):')
    for f in ConfigurationService().pending_unique_with_code[:20]:
        ConfigurationService().logger.info(f'  - {f.relative_to(ConfigurationService().REVIEW_PENDING)}')
    ConfigurationService().logger.info(f'\nUnique stub files ({len(ConfigurationService().pending_unique_stub)}):')
    for f in ConfigurationService().pending_unique_stub[:20]:
        ConfigurationService().logger.info(f'  - {f.relative_to(ConfigurationService().REVIEW_PENDING)}')
    len(ConfigurationService().pending_files)
    len(ConfigurationService().pending_is_stub) + len(ConfigurationService().pending_same_or_less) + \
        len(ConfigurationService().pending_unique_stub)
    len(ConfigurationService().pending_has_more_code) + len(ConfigurationService().pending_unique_with_code)
    if ConfigurationService().needs_review == 0:
        ConfigurationService().logger.info('\n✓ All files can be safely archived!')
    else:
        ConfigurationService().logger.info(
            f'\n⚠ {ConfigurationService().needs_review} files need review before archiving')


if __name__ == '__main__':
    main()
