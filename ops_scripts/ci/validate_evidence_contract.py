"""
Evidence Contract Validator (pre-commit)

Purpose:
  Fail commits that claim completion without including raw command outputs.

Behavior:
  - If NO evidence files are part of the commit, this hook exits 0.
  - If evidence files are present, each must include required command blocks.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


DEFAULT_EVIDENCE_GLOB = 'docs/reports/sub/**/*.md'
REQUIRED_MARKERS = ['pre-commit run --all-files', 'pytest -q', 'git show --name-only', 'git status --porcelain=v1']

def _read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace')

def _select_evidence_files(paths: list[str], evidence_glob: str) -> list[Path]:
    ev = []
    for p in paths:
        pp = Path(p)
        if pp.match(evidence_glob) and pp.is_file():
            ev.append(pp)
    return sorted(ev, key=lambda x: str(x))

def _missing_markers(text: str) -> list[str]:
    missing = []
    for m in REQUIRED_MARKERS:
        if m not in text:
            missing.append(m)
    return missing

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--evidence-glob', default=DEFAULT_EVIDENCE_GLOB)
    ap.add_argument('files', nargs='*')
    args = ap.parse_args(argv)
    evidence_files = _select_evidence_files(args.files, args.evidence_glob)
    if not evidence_files:
        return 0
    failed = False
    for ef in evidence_files:
        text = _read_text(ef)
        missing = _missing_markers(text)
        if missing:
            failed = True
            print(f'[FAIL] Evidence file missing required raw outputs: {ef}')
            for m in missing:
                print(f'  - missing marker: {m}')
            print('  Fix: paste verbatim command output blocks into the evidence file.')
            print('')
    return 1 if failed else 0
if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
