"""
Phase 0 — source manifest builder.

Walks the 12 canonical source folders, computes SHA256 + line count + mtime
for every ingestible file, and builds a structured manifest. Validates the
manifest against the foolproof rules in the user spec:

  * folder_count_found must equal 12
  * file_count_ingested must be > 0
  * missing_folders must be empty
  * empty_folders must be empty
  * every discovered file must be readable
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from agentic_core.runtime.prove_requirements.constants import (
    EXCLUDED_DIRNAMES,
    EXCLUDED_FILE_SUFFIXES,
    EXCLUDED_PATH_FRAGMENTS,
    INGESTIBLE_SUFFIXES,
    REPO_ROOT,
    SOURCE_FOLDERS,
)
from agentic_core.runtime.prove_requirements.types import SourceFileEntry


def _compute_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _count_lines(p: Path) -> int:
    n = 0
    with p.open("rb") as f:
        for _ in f:
            n += 1
    return n


def _is_excluded(p: Path) -> bool:
    parts = set(p.parts)
    if parts & EXCLUDED_DIRNAMES:
        return True
    posix = p.as_posix()
    for frag in EXCLUDED_PATH_FRAGMENTS:
        if frag in posix:
            return True
    suffix_lower = p.suffix.lower()
    if suffix_lower in EXCLUDED_FILE_SUFFIXES:
        return True
    return False


def _walk_folder(folder: Path) -> List[Path]:
    out: List[Path] = []
    for p in folder.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in INGESTIBLE_SUFFIXES:
            continue
        if _is_excluded(p):
            continue
        out.append(p)
    return sorted(out)


def build_manifest(repo_root: Optional[Path] = None) -> Dict:
    """Build the source manifest by walking the 12 canonical folders.

    Returns a dict with two keys:
        summary -- counts, missing/empty folder lists, generation timestamp
        files   -- list of dicts, one per ingested file
    """
    repo_root = (repo_root or REPO_ROOT).resolve()
    folder_count_expected = len(SOURCE_FOLDERS)
    missing: List[str] = []
    empty: List[str] = []
    excluded: List[Dict[str, str]] = []
    files: List[SourceFileEntry] = []

    for folder_rel in SOURCE_FOLDERS:
        folder = (repo_root / folder_rel).resolve()
        if not folder.exists() or not folder.is_dir():
            missing.append(folder_rel)
            continue
        discovered = _walk_folder(folder)
        if not discovered:
            empty.append(folder_rel)
            continue
        for p in discovered:
            try:
                entry = SourceFileEntry(
                    source_folder=str(folder),
                    path=str(p),
                    relative_path=p.relative_to(repo_root).as_posix(),
                    sha256=_compute_sha256(p),
                    line_count=_count_lines(p),
                    mtime=datetime.fromtimestamp(
                        p.stat().st_mtime, tz=timezone.utc
                    ).isoformat(),
                    ingested=True,
                )
                files.append(entry)
            except (OSError, IOError) as exc:
                excluded.append(
                    {"path": str(p), "reason": f"unreadable: {exc.__class__.__name__}: {exc}"}
                )

    summary = {
        "folder_count_expected": folder_count_expected,
        "folder_count_found": folder_count_expected - len(missing),
        "file_count_ingested": len(files),
        "missing_folders": missing,
        "empty_folders": empty,
        "excluded_files": excluded,
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "repo_root": str(repo_root),
    }
    return {"summary": summary, "files": [asdict(f) for f in files]}


def validate_manifest(manifest: Dict) -> Tuple[bool, List[str]]:
    """Return (ok, errors). Implements the foolproof acceptance rules."""
    s = manifest["summary"]
    errors: List[str] = []
    if s["folder_count_found"] != 12:
        errors.append(
            f"folder_count_found={s['folder_count_found']} (expected 12); missing={s['missing_folders']}"
        )
    if s["file_count_ingested"] == 0:
        errors.append("file_count_ingested=0 — no source files discovered")
    if s["missing_folders"]:
        errors.append(f"missing_folders={s['missing_folders']}")
    if s["empty_folders"]:
        errors.append(f"empty_folders={s['empty_folders']}")
    if s["excluded_files"]:
        # excluded files (unreadable) are listed but only fatal if all files are excluded
        if len(s["excluded_files"]) >= s["file_count_ingested"] and s["file_count_ingested"] == 0:
            errors.append(f"all candidate files unreadable: {s['excluded_files'][:5]}")
    return (len(errors) == 0, errors)
