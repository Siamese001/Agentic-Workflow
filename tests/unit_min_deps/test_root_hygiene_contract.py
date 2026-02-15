"""
Structural invariant: project root must only contain approved files and directories.

Deterministic filesystem scan against root_manifest.json.
Guardian hard gate — fails on any drift.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "artifacts" / "structure" / "root_manifest.json"


def _load_manifest() -> dict:
    """Load the approved root manifest."""
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _scan_root_drift() -> tuple[list[str], list[str]]:
    """Compare filesystem root against manifest. Return (extra_files, extra_dirs)."""
    manifest = _load_manifest()
    approved_files = set(manifest["approved_files"])
    approved_dirs = set(manifest["approved_directories"])

    extra_files: list[str] = []
    extra_dirs: list[str] = []

    for entry in ROOT.iterdir():
        name = entry.name
        if entry.is_file():
            if name not in approved_files:
                extra_files.append(name)
        elif entry.is_dir():
            if name not in approved_dirs:
                extra_dirs.append(name)

    return sorted(extra_files), sorted(extra_dirs)


class TestRootHygiene:
    """Hard gate: root directory must match approved manifest."""

    def test_manifest_exists(self) -> None:
        assert MANIFEST_PATH.exists(), f"Root manifest not found at {MANIFEST_PATH.relative_to(ROOT)}"

    def test_no_unapproved_root_files(self) -> None:
        extra_files, _ = _scan_root_drift()
        assert not extra_files, (
            f"Found {len(extra_files)} unapproved file(s) at project root:\n"
            + "\n".join(f"  {f}" for f in extra_files)
            + "\nAdd to artifacts/structure/root_manifest.json or move to correct folder."
        )

    def test_no_unapproved_root_directories(self) -> None:
        _, extra_dirs = _scan_root_drift()
        assert not extra_dirs, (
            f"Found {len(extra_dirs)} unapproved directory(ies) at project root:\n"
            + "\n".join(f"  {d}/" for d in extra_dirs)
            + "\nAdd to artifacts/structure/root_manifest.json or move to correct folder."
        )

    def test_synthetic_root_file_detected(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Negative test: prove scanner catches a synthetic unapproved file."""
        # Create a fake root with manifest + extra file
        fake_root = tmp_path / "fake_root"
        fake_root.mkdir()
        manifest_dir = fake_root / "artifacts" / "structure"
        manifest_dir.mkdir(parents=True)
        manifest = {
            "approved_files": ["README.md"],
            "approved_directories": [],
        }
        (manifest_dir / "root_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (fake_root / "README.md").write_text("ok", encoding="utf-8")
        (fake_root / "rogue_script.py").write_text("bad", encoding="utf-8")

        # Scan the fake root
        extra_files = []
        approved = set(manifest["approved_files"])
        for entry in fake_root.iterdir():
            if entry.is_file() and entry.name not in approved:
                extra_files.append(entry.name)

        assert "rogue_script.py" in extra_files, "Scanner failed to detect synthetic unapproved root file"
