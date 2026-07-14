#!/usr/bin/env python3
"""Seal or validate reviewer-return JSONL records without sealed packet data."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import stat
from typing import Any, Mapping, Sequence


def canonical_record_digest(record: Mapping[str, Any]) -> str:
    """Match the packet's canonical SHA-256 record-digest contract."""

    payload = {
        key: value for key, value in record.items() if key != "record_digest"
    }
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: record must be an object")
        rows.append(value)
    return rows


def _bind_identity_hashes(record: dict[str, Any]) -> None:
    """Fill or verify hashes bound to exact UTF-8 human identity references."""

    for reference_field, hash_field in (
        ("reviewer_identity_ref", "reviewer_id_hash"),
        ("adjudicator_identity_ref", "adjudicator_id_hash"),
    ):
        if reference_field not in record:
            continue
        reference = str(record.get(reference_field) or "")
        if not reference:
            raise ValueError(f"{reference_field} cannot be empty")
        expected = hashlib.sha256(reference.encode("utf-8")).hexdigest()
        observed = str(record.get(hash_field) or "")
        if observed and observed != expected:
            raise ValueError(f"{hash_field} does not match SHA-256({reference_field})")
        record[hash_field] = expected


def _private_directory(path: Path) -> None:
    if path.is_symlink():
        raise ValueError(f"return directory must not be a symlink: {path}")
    if path.exists():
        metadata = path.stat()
        if not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"return directory is not a directory: {path}")
        if metadata.st_uid != os.getuid() or stat.S_IMODE(metadata.st_mode) & 0o077:
            raise ValueError(f"return directory must be current-user owner-only (0700): {path}")
        return
    if not path.parent.exists():
        _private_directory(path.parent)
    os.mkdir(path, 0o700)


def _write_private(path: Path, text: str) -> None:
    _private_directory(path.parent)
    if path.is_symlink():
        raise ValueError(f"return file must not be a symlink: {path}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    temporary: Path | None = None
    descriptor = -1
    try:
        for _ in range(32):
            candidate = path.parent / f".{path.name}.private-{secrets.token_hex(12)}.tmp"
            try:
                descriptor = os.open(candidate, flags, 0o600)
                temporary = candidate
                break
            except FileExistsError:
                continue
        if temporary is None:
            raise FileExistsError(f"unable to allocate private output for {path}")
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            descriptor = -1
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def seal_file(source: Path, destination: Path) -> int:
    rows = _read_jsonl(source)
    output: list[str] = []
    for row in rows:
        sealed = {key: value for key, value in row.items() if key != "record_digest"}
        _bind_identity_hashes(sealed)
        sealed["record_digest"] = canonical_record_digest(sealed)
        output.append(
            json.dumps(
                sealed,
                allow_nan=False,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        )
    _write_private(destination, "".join(output))
    return len(rows)


def validate_file(path: Path) -> int:
    rows = _read_jsonl(path)
    for line_number, row in enumerate(rows, 1):
        _bind_identity_hashes(row)
        observed = row.get("record_digest")
        expected = canonical_record_digest(row)
        if observed != expected:
            raise ValueError(f"{path}:{line_number}: record_digest mismatch")
    return len(rows)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    seal = subcommands.add_parser("seal", help="write canonical record_digest values")
    seal.add_argument("source", type=Path)
    seal.add_argument("--out", type=Path, required=True)
    validate = subcommands.add_parser("validate", help="verify canonical record_digest values")
    validate.add_argument("path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "seal":
            count = seal_file(args.source, args.out)
        else:
            count = validate_file(args.path)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print(f"PASS: {count} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["canonical_record_digest", "main", "seal_file", "validate_file"]
