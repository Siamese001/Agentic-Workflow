"""Small deterministic I/O helpers for the offline human-eval packet."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import secrets
import stat
from typing import Any, Iterable, Mapping

import yaml


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record_with_digest(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    payload = dict(value)
    payload.pop(field, None)
    payload[field] = stable_digest(payload)
    return payload


def digest_matches(value: Mapping[str, Any], field: str) -> bool:
    expected = str(value.get(field) or "")
    payload = dict(value)
    payload.pop(field, None)
    return bool(expected) and expected == stable_digest(payload)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: expected JSON object")
        rows.append(value)
    return rows


def ensure_private_directory(path: Path) -> Path:
    """Create/verify one owner-only real directory without widening ancestors."""

    directory = Path(path)
    if directory.is_symlink():
        raise ValueError(f"private directory must not be a symlink: {directory}")
    if directory.exists():
        metadata = directory.stat()
        if not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"private directory path is not a directory: {directory}")
        if metadata.st_uid != os.getuid():
            raise ValueError(f"private directory must be owned by the current user: {directory}")
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            raise ValueError(f"private directory must be owner-only (0700): {directory}")
        return directory
    parent = directory.parent
    if parent != directory and not parent.exists():
        ensure_private_directory(parent)
    try:
        os.mkdir(directory, 0o700)
    except FileExistsError:
        return ensure_private_directory(directory)
    return directory


def private_path_error(path: Path, *, directory: bool) -> str | None:
    """Return why a sensitive controller path is not a real owner-only path."""

    candidate = Path(path)
    if candidate.is_symlink():
        return "must not be a symlink"
    try:
        metadata = candidate.stat()
    except OSError:
        return "is missing or inaccessible"
    expected_type = stat.S_ISDIR if directory else stat.S_ISREG
    if not expected_type(metadata.st_mode):
        return "must be a directory" if directory else "must be a regular file"
    if metadata.st_uid != os.getuid():
        return "must be owned by the current user"
    if stat.S_IMODE(metadata.st_mode) & 0o077:
        return "must be owner-only (0700)" if directory else "must be owner-only (0600)"
    return None


def path_has_symlink_component(path: Path) -> bool:
    """Return whether any existing path component is a symbolic link."""

    absolute = Path(path).absolute()
    return any(component.is_symlink() for component in (absolute, *absolute.parents))


def controlled_path_error(path: Path, *, repo_root: Path) -> str | None:
    """Reject controller artifacts inside checkout or through link aliases."""

    candidate = Path(path)
    if path_has_symlink_component(candidate):
        return "must not use a symlink alias"
    resolved = candidate.resolve(strict=False)
    repository = Path(repo_root).resolve()
    try:
        resolved.relative_to(repository)
    except ValueError:
        pass
    else:
        return "must be outside the git checkout"
    if candidate.exists() and candidate.is_file() and candidate.stat().st_nlink != 1:
        return "must not be a hardlink alias"
    return None


def paths_refer_same(left: Path, right: Path) -> bool:
    """Compare lexical/resolved identity and existing inode aliases."""

    left_path, right_path = Path(left), Path(right)
    if left_path.resolve(strict=False) == right_path.resolve(strict=False):
        return True
    if left_path.exists() and right_path.exists():
        try:
            return os.path.samefile(left_path, right_path)
        except OSError:
            return False
    return False


def path_within(path: Path, directory: Path) -> bool:
    try:
        Path(path).resolve(strict=False).relative_to(Path(directory).resolve())
    except ValueError:
        return False
    return True


def write_private_text(path: Path, text: str) -> None:
    """Atomically replace a sensitive file from a newly created 0600 inode."""

    destination = Path(path)
    ensure_private_directory(destination.parent)
    if destination.is_symlink():
        raise ValueError(f"private output must not replace a symlink: {destination}")
    if destination.exists() and not destination.is_file():
        raise ValueError(f"private output must be a regular file: {destination}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    temporary: Path | None = None
    descriptor = -1
    try:
        for _ in range(32):
            candidate = destination.parent / (
                f".{destination.name}.private-{secrets.token_hex(12)}.tmp"
            )
            try:
                descriptor = os.open(candidate, flags, 0o600)
                temporary = candidate
                break
            except FileExistsError:
                continue
        if temporary is None:
            raise FileExistsError(f"unable to allocate private temporary file for {destination}")
        encoded = text.encode("utf-8")
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
        temporary = None
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def copy_private_file(source: Path, destination: Path) -> None:
    write_private_text(destination, Path(source).read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    write_private_text(
        path,
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> int:
    materialized = [dict(row) for row in rows]
    text = "".join(canonical_json(row) + "\n" for row in materialized)
    write_private_text(path, text)
    return len(materialized)


def repo_root_from_module() -> Path:
    return Path(__file__).resolve().parents[3]


__all__ = [
    "canonical_json",
    "copy_private_file",
    "controlled_path_error",
    "digest_matches",
    "file_digest",
    "ensure_private_directory",
    "private_path_error",
    "path_has_symlink_component",
    "paths_refer_same",
    "path_within",
    "read_json",
    "read_jsonl",
    "read_yaml",
    "record_with_digest",
    "repo_root_from_module",
    "stable_digest",
    "write_json",
    "write_jsonl",
    "write_private_text",
]
