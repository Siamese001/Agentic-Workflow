"""
File System Utilities - Canonical implementations for common file operations.

This module provides pure, stateless utilities for file system operations
that are commonly duplicated across the codebase.
"""

import hashlib
import fnmatch
import os
from pathlib import Path
from typing import Generator, Iterator, Sequence

from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS
from tqdm import tqdm

SCAN_EXCLUDED_DIRS: frozenset[str] = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS
SCAN_EXCLUDED_PREFIXES: tuple[str, ...] = ("temp_", "tmp_", "_temp_", ".tmp_")
SCAN_EXCLUDED_SUFFIXES: tuple[str, ...] = (".egg-info",)


def _matches_scan_exclusion(
    part: str,
    *,
    exclude_dirs: frozenset[str] | set[str],
    exclude_prefixes: tuple[str, ...],
    exclude_suffixes: tuple[str, ...],
) -> bool:
    """Return True when a single path part should be excluded from scans."""
    lowered = part.lower()
    if part in exclude_dirs or lowered in exclude_dirs:
        return True
    if any(lowered.startswith(prefix.lower()) for prefix in exclude_prefixes):
        return True
    if any(lowered.endswith(suffix.lower()) for suffix in exclude_suffixes):
        return True
    return False


def _matches_scan_path(
    path: str | Path,
    *,
    exclude_dirs: frozenset[str] | set[str],
    exclude_prefixes: tuple[str, ...],
    exclude_suffixes: tuple[str, ...],
    exclude_path_prefixes: Sequence[str] | None,
) -> bool:
    candidate = Path(path)
    candidate_posix = candidate.as_posix().replace("\\", "/").lower()
    candidate_parts = tuple(part.lower() for part in candidate.parts)

    if exclude_path_prefixes:
        for prefix in exclude_path_prefixes:
            normalized_prefix = prefix.replace("\\", "/").lower().rstrip("/")
            if candidate_posix == normalized_prefix:
                return True
            if candidate_posix.startswith(f"{normalized_prefix}/"):
                return True

    for raw_dir in exclude_dirs:
        token = raw_dir.replace("\\", "/").lower()
        if "/" in token:
            normalized_token = token.rstrip("/")
            if candidate_posix == normalized_token or candidate_posix.startswith(f"{normalized_token}/"):
                return True
            if f"/{normalized_token}/" in candidate_posix:
                return True
        elif "*" in token or "?" in token:
            if fnmatch.fnmatch(candidate_posix, token) or any(fnmatch.fnmatch(part, token) for part in candidate_parts):
                return True
        elif token in candidate_parts:
            return True

    return any(
        _matches_scan_exclusion(
            part,
            exclude_dirs=exclude_dirs,
            exclude_prefixes=exclude_prefixes,
            exclude_suffixes=exclude_suffixes,
        )
        for part in candidate.parts
    )


def should_skip_scan_path(
    path: str | Path,
    *,
    exclude_dirs: frozenset[str] | set[str] | None = None,
    exclude_prefixes: Sequence[str] | None = None,
    exclude_suffixes: Sequence[str] | None = None,
    exclude_path_prefixes: Sequence[str] | None = None,
) -> bool:
    """Return True when a filesystem path belongs to a junk scan tree."""
    candidate = Path(path)
    dirs = SCAN_EXCLUDED_DIRS if exclude_dirs is None else exclude_dirs
    prefixes = tuple(SCAN_EXCLUDED_PREFIXES if exclude_prefixes is None else exclude_prefixes)
    suffixes = tuple(SCAN_EXCLUDED_SUFFIXES if exclude_suffixes is None else exclude_suffixes)
    return _matches_scan_path(
        candidate,
        exclude_dirs=dirs,
        exclude_prefixes=prefixes,
        exclude_suffixes=suffixes,
        exclude_path_prefixes=exclude_path_prefixes,
    )


def prune_walk_dirs(
    dirs: list[str],
    *,
    root: str | Path | None = None,
    exclude_dirs: frozenset[str] | set[str] | None = None,
    exclude_prefixes: Sequence[str] | None = None,
    exclude_suffixes: Sequence[str] | None = None,
) -> None:
    """Prune junk directories from an ``os.walk`` directory list in place."""
    root_path = Path(root) if root is not None else None
    dirs[:] = [
        d
        for d in dirs
        if not _matches_scan_path(
            (root_path / d) if root_path is not None else d,
            exclude_dirs=SCAN_EXCLUDED_DIRS if exclude_dirs is None else exclude_dirs,
            exclude_prefixes=tuple(SCAN_EXCLUDED_PREFIXES if exclude_prefixes is None else exclude_prefixes),
            exclude_suffixes=tuple(SCAN_EXCLUDED_SUFFIXES if exclude_suffixes is None else exclude_suffixes),
            exclude_path_prefixes=None,
        )
    ]


def iter_scanned_files(
    root_dir: str | Path,
    *,
    suffixes: Sequence[str] | None = None,
    exclude_dirs: frozenset[str] | set[str] | None = None,
    exclude_prefixes: Sequence[str] | None = None,
    exclude_suffixes: Sequence[str] | None = None,
    exclude_path_prefixes: Sequence[str] | None = None,
) -> Iterator[Path]:
    """Yield files from a rooted walk while pruning junk directories."""
    wanted_suffixes = None
    if suffixes is not None:
        wanted_suffixes = {
            suffix.lower() if suffix.startswith(".") else f".{suffix.lower()}"
            for suffix in suffixes
        }
    for root, dirs, files in os.walk(root_dir):
        prune_walk_dirs(
            dirs,
            root=root,
            exclude_dirs=exclude_dirs,
            exclude_prefixes=exclude_prefixes,
            exclude_suffixes=exclude_suffixes,
        )
        for file_name in files:
            file_path = Path(root) / file_name
            if wanted_suffixes is not None and file_path.suffix.lower() not in wanted_suffixes:
                continue
            if should_skip_scan_path(
                file_path,
                exclude_dirs=exclude_dirs,
                exclude_prefixes=exclude_prefixes,
                exclude_suffixes=exclude_suffixes,
                exclude_path_prefixes=exclude_path_prefixes,
            ):
                continue
            yield file_path


def get_python_files_fast(
    root_dir: Path,
    exclude_dirs: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
) -> Generator[Path, None, None]:
    """
    Fast Python file discovery with configurable filtering.

    Args:
        root_dir: Root directory to search
        exclude_dirs: Directory names to exclude (default: ['__pycache__', '.git', 'venv', 'env'])
        exclude_patterns: File patterns to exclude (default: ['*.pyc', '*.pyo'])

    Yields:
        Path objects for Python files found
    """
    if exclude_patterns is None:
        exclude_patterns = ["*.pyc", "*.pyo", "*.pyd"]

    for file_path in tqdm(
        iter_scanned_files(root_dir, suffixes=(".py",), exclude_dirs=exclude_dirs),
        desc="Processing",
        unit="item",
    ):
        if not any(file_path.match(pattern) for pattern in exclude_patterns):
            yield file_path


def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """
    Calculate hash of file content.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (default: 'sha256')

    Returns:
        Hexadecimal hash string
    """
    hash_obj = hashlib.new(algorithm)

    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except OSError:  # guardian: allow-silent-swallow -- acceptable exception handling
        return ""


def get_canonical_path(path: Path) -> Path:
    """
    Get canonical path with forward slashes and resolved components.

    Args:
        path: Path to normalize

    Returns:
        Canonical Path object
    """
    # Resolve to absolute path, then convert to forward slashes
    resolved = path.resolve()
    return Path(str(resolved).replace("\\", "/"))


def remove_duplicate_suffix_path(
    duplicate_path: Path,
    problematic_suffixes: list[str],
) -> tuple[Path, str | None]:
    """
    Get the canonical path by removing duplicate suffix.

    Args:
        duplicate_path: Path with potential duplicate suffix
        problematic_suffixes: List of suffixes to remove

    Returns:
        Tuple of (canonical_path, matched_suffix)
    """
    stem = duplicate_path.stem
    for suffix in problematic_suffixes:
        if stem.endswith(suffix):
            canonical_stem = stem[: -len(suffix)]
            canonical_path = duplicate_path.parent / f"{canonical_stem}.py"
            return (canonical_path, suffix)
    return (duplicate_path, None)
