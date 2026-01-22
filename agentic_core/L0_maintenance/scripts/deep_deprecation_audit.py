"""Deep Deprecation Audit - Scan all *Agent.py files for legacy/deprecated markers."""
import re
import sys
sys.path.insert(0, '.')
DEPRECATION_PATTERNS = [('\\blegacy\\b', 'legacy'), ('\\bdeprecated\\b', 'deprecated'), ('\\bsuperseded\\b', 'superseded'), ('\\barchive\\b', 'archive'), ('use\\s+\\S+\\s+instead', 'use X instead'), ('\\bremoved\\b', 'removed'), ('\\bplaceholder\\b', 'placeholder'), ('\\bstub\\b', 'stub'), ('\\bobsolete\\b', 'obsolete'), ('\\bdo not use\\b', 'do not use'), ('\\bwill be removed\\b', 'will be removed'), ('\\bto be deleted\\b', 'to be deleted')]

def scan_file(filepath: Path) -> list[dict]:
    """Scan first 50 lines of a file for deprecation markers."""
from pathlib import Path
    findings = []
    try:
        content = filepath.read_text(encoding='utf-8')
        lines = content.splitlines()[:50]
        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()
            for pattern, keyword in DEPRECATION_PATTERNS:
                if re.search(pattern, line_lower):
                    text = line.strip()[:100]
                    if text:
                        findings.append({'file': filepath.name, 'path': str(filepath), 'line': line_num, 'keyword': keyword, 'text': text})
                        break
    except Exception as e:
        pass
    return findings

def main():
    """TODO: Add documentation for main."""
    project_root = Path('.')
    agent_files = []
    for search_dir in ['agentic_core', 'apps_rg', 'apps_lic', 'apps_shared']:
        search_path = project_root / search_dir
        if search_path.exists():
            for f in search_path.rglob('*Agent.py'):
                if 'archives' not in str(f) and '__pycache__' not in str(f):
                    agent_files.append(f)
    all_findings = []
    for filepath in sorted(agent_files):
        findings = scan_file(filepath)
        all_findings.extend(findings)
    seen_files = set()
    unique_findings = []
    for f in all_findings:
        if f['file'] not in seen_files:
            seen_files.add(f['file'])
            unique_findings.append(f)
    if unique_findings:
        for f in unique_findings:
            pass
        by_keyword = {}
        for f in unique_findings:
            kw = f['keyword']
            by_keyword[kw] = by_keyword.get(kw, []) + [f['file']]
        for kw, files in sorted(by_keyword.items(), key=lambda x: -len(x[1])):
            pass
    return unique_findings
if __name__ == '__main__':
    main()
