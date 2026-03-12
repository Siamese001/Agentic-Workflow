from agentic_core.L2_execution.tools import write_gateway as _wg
'\nDocumentation Structure Guard\n\nDeterministic read-only scanner for docs/ directory governance.\nEnforces structural invariants without modifying any files.\n'
from pathlib import Path
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def is_valid_extension(file_path: Path) -> bool:
    """Check if file has a valid documentation extension."""
    return file_path.suffix.lower() in {'.md', '.yaml', '.yml', '.json', '.txt'}

def has_backup_suffix(filename: str) -> bool:
    """Check if filename has backup suffix."""
    return any((filename.endswith(suffix) for suffix in ['.bak.md', '.old.md', '.backup.md']))

def has_h1_heading(file_path: Path) -> bool:
    """Check if markdown file contains at least one H1 heading."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
            return '# ' in content
    except (UnicodeDecodeError, PermissionError):
        return False

def scan_docs_directory(docs_path: Path) -> dict[str, Any]:
    """Scan docs directory for structural violations."""
    violations = []
    files_scanned = 0
    filenames_seen = set()
    all_files = sorted(docs_path.rglob('*'))
    for file_path in all_files:
        if file_path.is_dir():
            continue
        if not is_valid_extension(file_path):
            continue
        files_scanned += 1
        relative_path = file_path.relative_to(docs_path)
        filename = file_path.name
        if has_backup_suffix(filename):
            violations.append({'file': str(relative_path), 'type': 'backup_suffix', 'detail': f'File has backup suffix: {filename}'})
        filename_lower = filename.lower()
        if filename_lower in filenames_seen:
            violations.append({'file': str(relative_path), 'type': 'duplicate_filename', 'detail': f'Duplicate filename (case-insensitive): {filename}'})
        filenames_seen.add(filename_lower)
        if file_path.suffix.lower() == '.md' and file_path.stat().st_size == 0:
            violations.append({'file': str(relative_path), 'type': 'empty_markdown', 'detail': 'Empty markdown file'})
        depth = len(relative_path.parts) - 1
        if depth > 6:
            violations.append({'file': str(relative_path), 'type': 'depth_exceeded', 'detail': f'File depth {depth} exceeds maximum of 6 levels'})
        if file_path.suffix.lower() == '.md' and (not has_h1_heading(file_path)):
            violations.append({'file': str(relative_path), 'type': 'missing_h1', 'detail': 'Markdown file missing H1 heading (# )'})
    return {'files_scanned': files_scanned, 'violations': violations}

def main():
    """Main scanner execution."""
    root_path = Path(__file__).parent.parent.parent
    docs_path = root_path / 'docs'
    if not docs_path.exists():
        print(f'Error: docs directory not found at {docs_path}')
        return 1
    print(f'Scanning docs directory: {docs_path}')
    result = scan_docs_directory(docs_path)
    output_dir = root_path / 'artifacts' / 'governance'
    _wg.ensure_dir(output_dir)
    report_path = output_dir / 'docs_structure_report.json'
    _wg.write_json(report_path, result, indent=2)
    print(f'Scan complete. Report written to: {report_path}')
    print(f"Files scanned: {result['files_scanned']}")
    print(f"Violations found: {len(result['violations'])}")
    if result['violations']:
        print('DOCS STRUCTURE VIOLATIONS DETECTED:')
        for violation in result['violations']:
            print(f"  {violation['file']}: {violation['type']} - {violation['detail']}")
        return 1
    else:
        print('No docs structure violations found.')
        return 0
if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
