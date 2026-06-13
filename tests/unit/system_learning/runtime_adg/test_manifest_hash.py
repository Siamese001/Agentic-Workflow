"""Tests for the manifest_hash helper (Phase B.3).

Pins the ``sha256-raw-bytes`` convention: any change to the manifest's
raw bytes (including comments, whitespace, line endings) must produce
a different hash. No YAML parse, no canonicalization.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from agentic_core.L6_system_learning.manifest_hash import (
    MANIFEST_FILENAME,
    MANIFEST_HASH_ALGORITHM,
    compute_manifest_hash,
    compute_manifest_hash_for_app,
)


_HEX_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


# ---------------------------------------------------------------------------
# compute_manifest_hash — pure bytes-in / hex-out
# ---------------------------------------------------------------------------


def test_same_bytes_produce_same_hash(tmp_path: Path) -> None:
    p1 = tmp_path / "a.yaml"
    p2 = tmp_path / "b.yaml"
    payload = b"claimed_routes: [R3_grounded_read]\n"
    p1.write_bytes(payload)
    p2.write_bytes(payload)
    assert compute_manifest_hash(p1) == compute_manifest_hash(p2)


def test_changing_one_byte_changes_hash(tmp_path: Path) -> None:
    p1 = tmp_path / "a.yaml"
    p2 = tmp_path / "b.yaml"
    p1.write_bytes(b"claimed_routes: [R3_grounded_read]\n")
    p2.write_bytes(b"claimed_routes: [R3_grounded_read] \n")  # single extra space
    assert compute_manifest_hash(p1) != compute_manifest_hash(p2)


def test_comments_affect_hash(tmp_path: Path) -> None:
    """Raw-bytes SHA-256 means comments are hash-relevant. This is the
    explicit design choice from design matrix v2 §12 Q6."""
    without_comment = tmp_path / "without.yaml"
    with_comment = tmp_path / "with.yaml"
    without_comment.write_bytes(b"claimed_routes: [R3_grounded_read]\n")
    with_comment.write_bytes(
        b"# CC-EVAL-01 applies\nclaimed_routes: [R3_grounded_read]\n"
    )
    assert compute_manifest_hash(without_comment) != compute_manifest_hash(with_comment)


def test_line_endings_affect_hash(tmp_path: Path) -> None:
    lf = tmp_path / "lf.yaml"
    crlf = tmp_path / "crlf.yaml"
    lf.write_bytes(b"a: 1\nb: 2\n")
    crlf.write_bytes(b"a: 1\r\nb: 2\r\n")
    assert compute_manifest_hash(lf) != compute_manifest_hash(crlf)


def test_whitespace_only_difference_changes_hash(tmp_path: Path) -> None:
    p1 = tmp_path / "no_trail.yaml"
    p2 = tmp_path / "trail.yaml"
    p1.write_bytes(b"claimed_routes: [R3_grounded_read]")
    p2.write_bytes(b"claimed_routes: [R3_grounded_read]\n")
    assert compute_manifest_hash(p1) != compute_manifest_hash(p2)


def test_returned_hash_is_64_lowercase_hex(tmp_path: Path) -> None:
    p = tmp_path / "m.yaml"
    p.write_bytes(b"anything: at all\n")
    h = compute_manifest_hash(p)
    assert _HEX_SHA256_RE.match(h) is not None, (
        f"expected 64 lowercase hex chars; got {h!r}"
    )
    assert len(h) == 64
    assert h == h.lower()


def test_matches_openssl_sha256(tmp_path: Path) -> None:
    """Verify against an independent hashlib call \u2014 pins the
    raw-bytes, no-canonicalization contract."""
    import hashlib

    p = tmp_path / "m.yaml"
    payload = b"claimed_routes:\n  - R3_grounded_read\n# CC-EVAL-01\n"
    p.write_bytes(payload)
    assert compute_manifest_hash(p) == hashlib.sha256(payload).hexdigest()


def test_accepts_string_path(tmp_path: Path) -> None:
    p = tmp_path / "m.yaml"
    p.write_bytes(b"x: 1\n")
    h_from_path = compute_manifest_hash(p)
    h_from_str = compute_manifest_hash(str(p))
    assert h_from_path == h_from_str


# ---------------------------------------------------------------------------
# Error paths
# ---------------------------------------------------------------------------


def test_missing_file_raises_FileNotFoundError(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="manifest not found"):
        compute_manifest_hash(tmp_path / "does_not_exist.yaml")


def test_directory_path_raises_IsADirectoryError(tmp_path: Path) -> None:
    with pytest.raises(IsADirectoryError, match="is a directory"):
        compute_manifest_hash(tmp_path)


def test_empty_path_raises_ValueError() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        compute_manifest_hash("")


def test_whitespace_path_raises_ValueError() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        compute_manifest_hash("   ")


def test_none_path_raises_ValueError() -> None:
    with pytest.raises(ValueError, match="must not be None"):
        compute_manifest_hash(None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# compute_manifest_hash_for_app
# ---------------------------------------------------------------------------


def test_compute_manifest_hash_for_app_works_against_tmp_repo(tmp_path: Path) -> None:
    app_dir = tmp_path / "apps_demo"
    app_dir.mkdir()
    manifest = app_dir / MANIFEST_FILENAME
    payload = b"claimed_routes:\n  - R3_grounded_read\n"
    manifest.write_bytes(payload)

    h = compute_manifest_hash_for_app("apps_demo", repo_root=tmp_path)
    assert _HEX_SHA256_RE.match(h) is not None
    # Same hash as the direct call.
    assert h == compute_manifest_hash(manifest)


def test_compute_manifest_hash_for_app_rejects_non_apps_name() -> None:
    with pytest.raises(ValueError, match="must start with 'apps_'"):
        compute_manifest_hash_for_app("agentic_core")


def test_compute_manifest_hash_for_app_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="must be a non-empty string"):
        compute_manifest_hash_for_app("")


def test_compute_manifest_hash_for_app_rejects_whitespace_name() -> None:
    with pytest.raises(ValueError, match="must be a non-empty string"):
        compute_manifest_hash_for_app("   ")


def test_compute_manifest_hash_for_app_missing_manifest(tmp_path: Path) -> None:
    (tmp_path / "apps_ghost").mkdir()  # dir exists but no manifest
    with pytest.raises(FileNotFoundError, match="manifest not found"):
        compute_manifest_hash_for_app("apps_ghost", repo_root=tmp_path)


def test_compute_manifest_hash_for_app_infers_repo_root() -> None:
    """With ``repo_root=None``, the helper must find the real repo's
    manifests for active apps in this checkout."""
    h = compute_manifest_hash_for_app("apps_rg")
    assert _HEX_SHA256_RE.match(h) is not None


def test_compute_manifest_hash_for_app_multiple_apps_differ() -> None:
    """Two distinct apps must produce distinct manifest_hash values
    (unless by astronomical coincidence their manifests are byte-equal)."""
    h_research = compute_manifest_hash_for_app("apps_research")
    h_rg = compute_manifest_hash_for_app("apps_rg")
    assert h_research != h_rg


# ---------------------------------------------------------------------------
# Module-level invariants
# ---------------------------------------------------------------------------


def test_algorithm_identifier_is_stable() -> None:
    assert MANIFEST_HASH_ALGORITHM == "sha256-raw-bytes"


def test_manifest_filename_is_stable() -> None:
    assert MANIFEST_FILENAME == "spine_manifest.yaml"
