"""Analyze archives for files that should be restored to apps_* folders."""
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    ARCHIVES_DIR,
)

RESUME_KEYWORDS = {'resume', 'cv', 'ats', 'job', 'skill', 'experience', 'bullet', 'section'}
OUTREACH_KEYWORDS = {'outreach', 'linkedin', 'recipient', 'campaign', 'personalization', 'message', 'sender'}

def analyze_archive(archive_path: Path):
    """Analyze an archive folder for app-relevant files."""
    if not archive_path.exists():
        print(f'Error: Path {archive_path} does not exist.')
        return []
    results = []
    for f in sorted(archive_path.rglob('*.py')):
        if '__pycache__' in str(f):
            continue
        try:
            content = f.read_text(encoding='utf-8', errors='replace').lower()
            has_resume = any(kw in content for kw in RESUME_KEYWORDS)
            has_outreach = any(kw in content for kw in OUTREACH_KEYWORDS)
            if has_resume or has_outreach:
                tag = 'SHARED' if has_resume and has_outreach else 'RG' if has_resume else 'LIC'
                first_sig_line = ''
                with f.open('r', encoding='utf-8', errors='replace') as file:
                    for _ in range(50):
                        line = file.readline()
                        if not line:
                            break
                        clean_line = line.strip()
                        if clean_line.startswith(('class ', 'def ')):
                            first_sig_line = clean_line[:70]
                            break
                results.append({'path': str(f.relative_to(archive_path)), 'tag': tag, 'first_line': first_sig_line, 'has_resume': has_resume, 'has_outreach': has_outreach})
        # guardian: allow-silent-swallow
        except Exception:
            continue
    return results

def _discover_subfolders(archives_root: Path) -> list[tuple[str, str]]:
    """Dynamically discover all subfolders in the archives root."""
    if not archives_root.exists():
        return []
    return [(entry.name, f'Discovered subfolder: {entry.name}') for entry in sorted(archives_root.iterdir()) if entry.is_dir() and (not entry.name.startswith('.'))]

def main():
    archives_root = Path(ARCHIVES_DIR)
    known_archives: dict[str, str] = {'deprecated_2026_01_20': "Today's deprecated files", 'misplaced_tests_2026_01_20': "Today's misplaced tests", 'apps_lic': 'Previously archived LIC files', 'apps_rg': 'Previously archived RG files', 'apps_shared': 'Previously archived shared files', 'Reachout Engine Archive': 'Legacy outreach engine'}
    discovered = _discover_subfolders(archives_root)
    archives_to_check: list[tuple[str, str]] = list(known_archives.items())
    known_names = set(known_archives.keys())
    for name, desc in discovered:
        if name not in known_names:
            archives_to_check.append((name, desc))
    print('=' * 80)
    print('ARCHIVE ANALYSIS - FILES POTENTIALLY RELEVANT TO apps_* FOLDERS')
    print('=' * 80)
    all_restore_candidates = []
    for archive_name, description in archives_to_check:
        archive_path = archives_root / archive_name
        if not archive_path.exists():
            continue
        results = analyze_archive(archive_path)
        if results:
            print(f'\n## {archive_name} ({description})')
            print(f'   Found {len(results)} app-relevant files')
            print('-' * 60)
            for r in results[:15]:
                print(f"  [{r['tag']}] {r['path']}")
                if r['first_line']:
                    print(f"       -> {r['first_line']}")
            if len(results) > 15:
                print(f'  ... and {len(results) - 15} more files')
            all_restore_candidates.extend([{'archive': archive_name, **r} for r in results])
    print('\n' + '=' * 80)
    print('RESTORE RECOMMENDATIONS SUMMARY')
    print('=' * 80)
    rg_count = sum(1 for r in all_restore_candidates if r['tag'] == 'RG')
    lic_count = sum(1 for r in all_restore_candidates if r['tag'] == 'LIC')
    shared_count = sum(1 for r in all_restore_candidates if r['tag'] == 'SHARED')
    print(f'\nTotal app-relevant files in archives: {len(all_restore_candidates)}')
    print(f'  - Resume Engine (RG):     {rg_count} files')
    print(f'  - Outreach Engine (LIC):  {lic_count} files')
    print(f'  - Shared (both):          {shared_count} files')
    print('\n' + '=' * 80)
    print('JUSTIFICATION FOR RESTORE/KEEP DECISIONS')
    print('=' * 80)
    deprecated_today = [r for r in all_restore_candidates if r['archive'] == 'deprecated_2026_01_20']
    if deprecated_today:
        print("\n### deprecated_2026_01_20 (Today's archive)")
        for r in deprecated_today:
            print(f"\n  {r['path']}")
            if r['tag'] == 'RG':
                print('    DECISION: Consider restore to apps_rg/engines/')
                print('    REASON: Contains resume-related logic')
            elif r['tag'] == 'LIC':
                print('    DECISION: Consider restore to apps_lic/engines/')
                print('    REASON: Contains outreach-related logic')
            elif r['tag'] == 'SHARED':
                print('    DECISION: Consider restore to apps_shared/')
                print('    REASON: Contains both resume and outreach logic')
if __name__ == '__main__':
    main()
