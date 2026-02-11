"""Golden-trace harness for legacy execute_ssot equivalence testing.

Captures a deterministic golden snapshot of legacy pipeline behavior
that becomes the gating oracle for all future extraction waves.

Design decisions:
  - ``--legacy --plan`` mode is safe (pure introspection, no writes).
    This is used as the primary golden trace.
  - Full ``--legacy`` execution requires the live repo and writes to
    tracked files; it is marked xfail until a controlled fixture is
    available.
  - All snapshots use stable sorting and sha256 hashing.
  - stdout/stderr capped at 2000 chars for determinism.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# ── Constants ─────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DIR = Path(__file__).resolve().parent / "golden"
GOLDEN_SNAPSHOT_PATH = GOLDEN_DIR / "legacy_trace.json"
ENTRYPOINT_MODULE = "agentic_core.L0_maintenance.scripts.execute_ssot_entrypoint"
MAX_CAPTURE = 2000


# ── Helpers ───────────────────────────────────────────────────────


def _sha256(filepath: Path) -> str:
    """Compute hex SHA-256 of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _snapshot_tree(root: Path, rel_base: Path | None = None) -> list[dict]:
    """Return sorted list of {path, sha256} for all files under *root*.

    Paths are relative to *rel_base* (defaults to *root*).
    Directories, ``__pycache__``, and ``.git`` are excluded.
    """
    base = rel_base or root
    entries = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {"__pycache__", ".git", ".nox"}]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            rel = fpath.relative_to(base)
            entries.append(
                {
                    "path": str(rel).replace("\\", "/"),
                    "sha256": _sha256(fpath),
                },
            )
    entries.sort(key=lambda e: e["path"])
    return entries


def _run_legacy_subprocess(
    *extra_args: str,
    cwd: Path | None = None,
) -> dict:
    """Run the legacy entrypoint via subprocess and capture output."""
    cmd = [
        sys.executable,
        "-m",
        ENTRYPOINT_MODULE,
        "--legacy",
        *extra_args,
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd or REPO_ROOT),
        timeout=60,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return {
        "command": cmd,
        "returncode": result.returncode,
        "stdout_head": result.stdout[:MAX_CAPTURE],
        "stderr_head": result.stderr[:MAX_CAPTURE],
    }


def _build_golden_snapshot(
    run_result: dict,
    tree_before: list[dict],
    tree_after: list[dict],
    artifacts_after: list[dict],
) -> dict:
    """Assemble the canonical golden snapshot structure."""
    return {
        "legacy": {
            **run_result,
            "tree_before": tree_before,
            "tree_after": tree_after,
            "artifacts_after": artifacts_after,
        },
    }


def _write_golden(snapshot: dict) -> Path:
    """Write golden snapshot JSON to the canonical path."""
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    GOLDEN_SNAPSHOT_PATH.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return GOLDEN_SNAPSHOT_PATH


# ── Fixtures ──────────────────────────────────────────────────────


@pytest.fixture()
def synthetic_tree(tmp_path: Path) -> Path:
    """Create a minimal synthetic file tree for snapshot infrastructure tests."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# module a\n", encoding="utf-8")
    (tmp_path / "src" / "b.py").write_text("# module b\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# readme\n", encoding="utf-8")
    return tmp_path


# ── Test: snapshot infrastructure (hermetic, no legacy import) ────


class TestSnapshotInfrastructure:
    """Verify snapshot helpers are deterministic and schema-valid."""

    def test_sha256_deterministic(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello\n", encoding="utf-8")
        h1 = _sha256(f)
        h2 = _sha256(f)
        assert h1 == h2
        assert len(h1) == 64
        assert all(c in "0123456789abcdef" for c in h1)

    def test_snapshot_tree_sorted(self, synthetic_tree: Path) -> None:
        tree = _snapshot_tree(synthetic_tree)
        paths = [e["path"] for e in tree]
        assert paths == sorted(paths)

    def test_snapshot_tree_hashes_are_64hex(self, synthetic_tree: Path) -> None:
        tree = _snapshot_tree(synthetic_tree)
        assert len(tree) >= 3
        for entry in tree:
            assert len(entry["sha256"]) == 64
            assert all(c in "0123456789abcdef" for c in entry["sha256"])

    def test_snapshot_tree_paths_use_forward_slashes(self, synthetic_tree: Path) -> None:
        tree = _snapshot_tree(synthetic_tree)
        for entry in tree:
            assert "\\" not in entry["path"]

    def test_snapshot_tree_excludes_pycache(self, synthetic_tree: Path) -> None:
        pc = synthetic_tree / "__pycache__"
        pc.mkdir()
        (pc / "cached.pyc").write_bytes(b"\x00")
        tree = _snapshot_tree(synthetic_tree)
        assert all("__pycache__" not in e["path"] for e in tree)

    def test_golden_snapshot_schema(self, synthetic_tree: Path) -> None:
        run_result = {
            "command": ["python", "-m", "test"],
            "returncode": 0,
            "stdout_head": "ok",
            "stderr_head": "",
        }
        tree = _snapshot_tree(synthetic_tree)
        snapshot = _build_golden_snapshot(run_result, tree, tree, [])

        # Schema keys
        assert "legacy" in snapshot
        legacy = snapshot["legacy"]
        required_keys = {
            "command",
            "returncode",
            "stdout_head",
            "stderr_head",
            "tree_before",
            "tree_after",
            "artifacts_after",
        }
        assert required_keys <= set(legacy.keys())

        # Types
        assert isinstance(legacy["command"], list)
        assert isinstance(legacy["returncode"], int)
        assert isinstance(legacy["stdout_head"], str)
        assert isinstance(legacy["stderr_head"], str)
        assert isinstance(legacy["tree_before"], list)
        assert isinstance(legacy["tree_after"], list)
        assert isinstance(legacy["artifacts_after"], list)


# ── Test: legacy --plan mode golden trace (safe, deterministic) ───


class TestLegacyPlanModeTrace:
    """Run legacy entrypoint in --plan mode (pure introspection, no writes).

    This is the primary golden trace: it exercises the real entrypoint import
    chain and execution plan resolution without modifying any repo files.
    """

    def test_plan_mode_returns_zero(self) -> None:
        result = _run_legacy_subprocess("--plan")
        assert result["returncode"] == 0, (
            f"--plan mode failed (rc={result['returncode']}):\nstderr: {result['stderr_head']}"
        )

    def test_plan_mode_stdout_nonempty(self) -> None:
        result = _run_legacy_subprocess("--plan")
        assert len(result["stdout_head"].strip()) > 0

    def test_plan_mode_no_repo_mutations(self) -> None:
        """Verify --plan mode does not create tracked diffs."""
        porcelain_before = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        ).stdout

        _run_legacy_subprocess("--plan")

        porcelain_after = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        ).stdout

        assert porcelain_before == porcelain_after, (
            "Legacy --plan mode mutated tracked files!\n"
            f"Before:\n{porcelain_before}\nAfter:\n{porcelain_after}"
        )

    def test_plan_mode_golden_snapshot_written(self) -> None:
        """Generate and write the golden snapshot for --plan mode."""
        # Snapshot a stable subset: the scripts directory only
        scripts_dir = REPO_ROOT / "agentic_core" / "L0_maintenance" / "scripts"
        tree_before = _snapshot_tree(scripts_dir, rel_base=REPO_ROOT)

        result = _run_legacy_subprocess("--plan")

        tree_after = _snapshot_tree(scripts_dir, rel_base=REPO_ROOT)

        snapshot = _build_golden_snapshot(
            result,
            tree_before=tree_before,
            tree_after=tree_after,
            artifacts_after=[],
        )

        out = _write_golden(snapshot)
        assert out.exists()

        # Validate written JSON is parseable and schema-valid
        loaded = json.loads(out.read_text(encoding="utf-8"))
        assert "legacy" in loaded
        assert loaded["legacy"]["returncode"] == 0
        assert loaded["legacy"]["tree_before"] == loaded["legacy"]["tree_after"]


# ── Test: full legacy execution (requires controlled fixture) ─────


class TestLegacyFullExecution:
    """Full --legacy execution requires the live repo and writes to tracked
    files during healing phases.  Until a sandboxed fixture is available,
    these tests are marked xfail.
    """

    @pytest.mark.xfail(
        reason=(
            "Full legacy execution requires live repo context with all agent "
            "imports resolvable, writes to tracked files during L2 healing "
            "phases, and cannot be safely isolated in a tmp_path fixture. "
            "Prerequisite: sandboxed repo clone fixture with mock agent "
            "registry (Phase 2 Wave 2.3+)."
        ),
        strict=False,
    )
    def test_full_legacy_run_captures_artifacts(self) -> None:
        """Placeholder: run full legacy pipeline and capture artifacts."""
        # This will be implemented when a controlled fixture exists.
        # For now, assert False to trigger xfail.
        msg = "Not yet implemented — awaiting sandboxed fixture"
        raise NotImplementedError(msg)


# ── Test: golden snapshot file deterministic assertions ───────────


class TestGoldenSnapshotDeterminism:
    """Validate the golden snapshot file if it exists on disk."""

    @pytest.fixture(autouse=True)
    def _require_golden(self) -> None:
        if not GOLDEN_SNAPSHOT_PATH.exists():
            pytest.skip("Golden snapshot not yet generated")

    def test_golden_file_is_valid_json(self) -> None:
        data = json.loads(GOLDEN_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_golden_schema_keys(self) -> None:
        data = json.loads(GOLDEN_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        legacy = data["legacy"]
        required = {
            "command",
            "returncode",
            "stdout_head",
            "stderr_head",
            "tree_before",
            "tree_after",
            "artifacts_after",
        }
        assert required <= set(legacy.keys())

    def test_golden_trees_sorted(self) -> None:
        data = json.loads(GOLDEN_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        legacy = data["legacy"]
        for key in ("tree_before", "tree_after", "artifacts_after"):
            paths = [e["path"] for e in legacy[key]]
            assert paths == sorted(paths), f"{key} is not sorted"

    def test_golden_hashes_are_64hex(self) -> None:
        data = json.loads(GOLDEN_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        legacy = data["legacy"]
        for key in ("tree_before", "tree_after", "artifacts_after"):
            for entry in legacy[key]:
                h = entry["sha256"]
                assert len(h) == 64, f"Bad hash length in {key}: {h}"
                assert all(c in "0123456789abcdef" for c in h), f"Non-hex char in {key}: {h}"

    def test_golden_stdout_under_capture_limit(self) -> None:
        data = json.loads(GOLDEN_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        assert len(data["legacy"]["stdout_head"]) <= MAX_CAPTURE

    def test_golden_stderr_under_capture_limit(self) -> None:
        data = json.loads(GOLDEN_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        assert len(data["legacy"]["stderr_head"]) <= MAX_CAPTURE
