"""Golden-trace harness for legacy execute_ssot equivalence testing.

Captures a deterministic golden snapshot of legacy pipeline behavior
that becomes the gating oracle for all future extraction waves.

Design decisions:
  - ``--legacy --plan`` mode is safe (pure introspection, no writes).
    This is used as the primary golden trace.
  - Full ``--legacy --validate`` execution runs in an isolated sandbox
    repo (git worktree or local clone under tmp_path) so that any
    file mutations are confined to the sandbox.
  - L2 dispatcher dry-run is chained after guardian aggregation to
    capture CombinedHealResult without any repo mutations.
  - All snapshots use stable sorting and sha256 hashing.
  - stdout/stderr capped at 2000 chars for determinism.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pytest
from tests._helpers.robust_fs import robust_subprocess_run

from tests.ssot_equivalence._sandbox_repo import (
    create_sandbox,
    destroy_sandbox,
    run_legacy_in_sandbox,
)

# ── Constants ─────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DIR = Path(__file__).resolve().parent / "golden"
GOLDEN_SNAPSHOT_PATH = GOLDEN_DIR / "legacy_trace.json"
ENTRYPOINT_MODULE = "agentic_core.L0_routing.scripts.execute_ssot_entrypoint"
GUARDIAN_MODULE = "agentic_core.L0_routing.scripts.run_all_guardians"
DISPATCHER_MODULE = "agentic_core.L2_execution.scripts.remediation_dispatcher"
DISPATCHER_FIXED_UTC = "2000-01-01T00:00:00Z"
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
    result = robust_subprocess_run(
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


def _run_guardians_subprocess(
    output_dir: Path,
    cwd: Path | None = None,
) -> tuple[dict, Path | None]:
    """Run guardians via subprocess and capture aggregate JSON from stdout.

    Writes the captured JSON to *output_dir*/combined_guardian_result.json.
    Returns (capture_dict, path_to_combined_guardian_result_or_None).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        GUARDIAN_MODULE,
        "--format",
        "json",
        "--timestamp",
        DISPATCHER_FIXED_UTC,
        "--correlation-id",
        "ssot-equivalence-harness",
    ]
    result = robust_subprocess_run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd or REPO_ROOT),
        timeout=120,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "V15_TEST_SIGNING": "1"},
    )
    capture = {
        "command": cmd,
        "returncode": result.returncode,
        "stdout_head": result.stdout[:MAX_CAPTURE],
        "stderr_head": result.stderr[:MAX_CAPTURE],
    }
    # Write stdout JSON to file for dispatcher consumption
    agg_path = output_dir / "combined_guardian_result.json"
    if result.returncode in (0, 1) and result.stdout.strip():
        try:
            json.loads(result.stdout)
            agg_path.write_text(result.stdout, encoding="utf-8")
            return capture, agg_path
        except json.JSONDecodeError:
            pass
    return capture, None


def _run_dispatcher_dry_run(
    guardian_result_path: Path,
    write_artifacts_dir: Path,
    cwd: Path | None = None,
) -> dict:
    """Run remediation_dispatcher in dry-run mode (no --apply).

    Returns capture dict with keys: command, returncode, stdout_head, stderr_head.
    """
    write_artifacts_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        DISPATCHER_MODULE,
        "--guardian-result",
        str(guardian_result_path),
        "--write-artifacts",
        str(write_artifacts_dir),
        "--created-utc",
        DISPATCHER_FIXED_UTC,
    ]
    result = robust_subprocess_run(
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
    *,
    dispatcher_dry_run: dict | None = None,
) -> dict:
    """Assemble the canonical golden snapshot structure."""
    snapshot: dict = {
        "legacy": {
            **run_result,
            "tree_before": tree_before,
            "tree_after": tree_after,
            "artifacts_after": artifacts_after,
        },
    }
    if dispatcher_dry_run is not None:
        snapshot["dispatcher_dry_run"] = dispatcher_dry_run
    return snapshot


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
        porcelain_before = robust_subprocess_run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        ).stdout

        _run_legacy_subprocess("--plan")

        porcelain_after = robust_subprocess_run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        ).stdout

        assert porcelain_before == porcelain_after, (
            "Legacy --plan mode mutated tracked files!\n"
            f"Before:\n{porcelain_before}\nAfter:\n{porcelain_after}"
        )

    def test_plan_mode_golden_snapshot_written(self, tmp_path: Path) -> None:
        """Generate and write the golden snapshot for --plan mode + dispatcher dry-run."""
        # Snapshot a stable subset: the scripts directory only
        scripts_dir = REPO_ROOT / "agentic_core" / "L0_routing" / "scripts"
        tree_before = _snapshot_tree(scripts_dir, rel_base=REPO_ROOT)

        result = _run_legacy_subprocess("--plan")

        tree_after = _snapshot_tree(scripts_dir, rel_base=REPO_ROOT)

        # Chain: run guardians -> dispatcher dry-run
        guardian_dir = tmp_path / "guardian_artifacts"
        _, agg_path = _run_guardians_subprocess(guardian_dir)

        dispatcher_section: dict | None = None
        if agg_path is not None:
            dispatcher_dir = tmp_path / "dispatcher_artifacts"
            disp_result = _run_dispatcher_dry_run(agg_path, dispatcher_dir)
            heal_path = dispatcher_dir / "combined_heal_result.json"
            dispatcher_section = {
                **disp_result,
                "combined_heal_result": {
                    "exists": heal_path.is_file(),
                    "sha256": _sha256(heal_path) if heal_path.is_file() else None,
                },
                "created_utc": DISPATCHER_FIXED_UTC,
            }

        snapshot = _build_golden_snapshot(
            result,
            tree_before=tree_before,
            tree_after=tree_after,
            artifacts_after=[],
            dispatcher_dry_run=dispatcher_section,
        )

        out = _write_golden(snapshot)
        assert out.exists()

        # Validate written JSON is parseable and schema-valid
        loaded = json.loads(out.read_text(encoding="utf-8"))
        assert "legacy" in loaded
        assert loaded["legacy"]["returncode"] == 0
        assert loaded["legacy"]["tree_before"] == loaded["legacy"]["tree_after"]
        if dispatcher_section is not None:
            assert "dispatcher_dry_run" in loaded


# ── Test: full legacy execution in sandbox ─────────────────────────


class TestLegacyFullExecution:
    """Run full legacy pipeline inside an isolated sandbox repo.

    The sandbox is created via ``git worktree add --detach`` (or local
    clone as fallback) under ``tmp_path``.  All file mutations happen
    inside the sandbox; the primary working tree is verified unchanged.
    """

    @pytest.fixture()
    def sandbox(self, tmp_path: Path):
        """Create and yield a sandbox repo, then destroy it."""
        from tests.ssot_equivalence._sandbox_repo import _git_available

        if not _git_available(REPO_ROOT):
            pytest.skip("git not available")
        sandbox_path = create_sandbox(REPO_ROOT, tmp_path)
        yield sandbox_path
        destroy_sandbox(REPO_ROOT, sandbox_path)

    @staticmethod
    def _primary_porcelain() -> str:
        return robust_subprocess_run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        ).stdout

    def test_sandbox_created(self, sandbox: Path) -> None:
        """Sandbox exists and contains agentic_core."""
        assert sandbox.exists()
        assert (sandbox / "agentic_core").is_dir()

    def test_full_legacy_validate_captures_output(self, sandbox: Path) -> None:
        """Run --legacy --validate in sandbox and capture trace."""
        porcelain_before = self._primary_porcelain()

        # Snapshot sandbox before
        scripts_dir = sandbox / "agentic_core" / "L0_routing" / "scripts"
        tree_before = _snapshot_tree(scripts_dir, rel_base=sandbox)

        # Run legacy in validate mode (dry-run, no healing writes)
        result = run_legacy_in_sandbox(sandbox, extra_args=["--validate"], timeout=120)

        # Snapshot sandbox after
        tree_after = _snapshot_tree(scripts_dir, rel_base=sandbox)

        # Collect any artifacts written by legacy
        artifacts_dir = sandbox / "logs" / "compliance_reports"
        if artifacts_dir.is_dir():
            artifacts_after = _snapshot_tree(artifacts_dir, rel_base=sandbox)
        else:
            artifacts_after = []

        # Schema validity
        assert isinstance(result["command"], list)
        assert isinstance(result["returncode"], int)
        assert isinstance(result["stdout_head"], str)
        assert isinstance(result["stderr_head"], str)
        assert len(result["stdout_head"]) <= MAX_CAPTURE
        assert len(result["stderr_head"]) <= MAX_CAPTURE

        # Trees are sorted and hashes are valid
        for tree in (tree_before, tree_after, artifacts_after):
            paths = [e["path"] for e in tree]
            assert paths == sorted(paths)
            for entry in tree:
                assert len(entry["sha256"]) == 64
                assert all(c in "0123456789abcdef" for c in entry["sha256"])

        # Primary repo unchanged
        porcelain_after = self._primary_porcelain()
        assert porcelain_before == porcelain_after, (
            "Sandboxed legacy run mutated primary working tree!\n"
            f"Before:\n{porcelain_before}\nAfter:\n{porcelain_after}"
        )

    def test_primary_repo_no_new_untracked(self, sandbox: Path) -> None:
        """After sandbox run, no new untracked files in primary repo."""
        porcelain_before = self._primary_porcelain()

        run_legacy_in_sandbox(sandbox, extra_args=["--validate"], timeout=120)

        porcelain_after = self._primary_porcelain()
        assert porcelain_before == porcelain_after


# ── Test: dispatcher dry-run trace (chained after guardians) ──────


class TestDispatcherDryRunTrace:
    """Run guardians then dispatcher in dry-run mode.

    Proves:
    - combined_heal_result.json exists and validates
    - all statuses are SKIPPED in dry-run
    - created_utc matches fixed harness value
    - tool_id is correct
    - primary repo unchanged
    """

    @pytest.fixture()
    def dispatcher_artifacts(self, tmp_path: Path) -> tuple[Path, dict]:
        """Run guardians + dispatcher, return (heal_result_path, capture_dict)."""
        guardian_dir = tmp_path / "guardian_artifacts"
        _, agg_path = _run_guardians_subprocess(guardian_dir)
        assert agg_path is not None, "Guardians did not produce combined_guardian_result.json"

        dispatcher_dir = tmp_path / "dispatcher_artifacts"
        capture = _run_dispatcher_dry_run(agg_path, dispatcher_dir)
        heal_path = dispatcher_dir / "combined_heal_result.json"
        return heal_path, capture

    def test_dispatcher_returns_zero(self, dispatcher_artifacts: tuple[Path, dict]) -> None:
        _, capture = dispatcher_artifacts
        assert capture["returncode"] == 0, (
            f"Dispatcher failed (rc={capture['returncode']}):\nstderr: {capture['stderr_head']}"
        )

    def test_combined_heal_result_exists(self, dispatcher_artifacts: tuple[Path, dict]) -> None:
        heal_path, _ = dispatcher_artifacts
        assert heal_path.is_file(), "combined_heal_result.json not produced"

    def test_combined_heal_result_valid_json(self, dispatcher_artifacts: tuple[Path, dict]) -> None:
        heal_path, _ = dispatcher_artifacts
        assert heal_path.is_file()
        data = json.loads(heal_path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_tool_id(self, dispatcher_artifacts: tuple[Path, dict]) -> None:
        heal_path, _ = dispatcher_artifacts
        data = json.loads(heal_path.read_text(encoding="utf-8"))
        assert data["tool_id"] == "remediation_dispatcher"

    def test_created_utc_matches_fixed_value(self, dispatcher_artifacts: tuple[Path, dict]) -> None:
        heal_path, _ = dispatcher_artifacts
        data = json.loads(heal_path.read_text(encoding="utf-8"))
        assert data["created_utc"] == DISPATCHER_FIXED_UTC

    def test_all_statuses_skipped_in_dry_run(self, dispatcher_artifacts: tuple[Path, dict]) -> None:
        heal_path, _ = dispatcher_artifacts
        data = json.loads(heal_path.read_text(encoding="utf-8"))
        for result in data.get("results", []):
            assert result["status"] == "SKIPPED", (
                f"Expected SKIPPED in dry-run but got {result['status']} "
                f"for check_id={result.get('check_id')}"
            )

    def test_schema_validates_via_contract(
        self,
        dispatcher_artifacts: tuple[Path, dict],
    ) -> None:
        heal_path, _ = dispatcher_artifacts
        from agentic_core.L2_execution.types.heal_contract import (
            check_schema_compatibility,
        )

        data = json.loads(heal_path.read_text(encoding="utf-8"))
        errors = check_schema_compatibility(data)
        assert not errors, f"CombinedHealResult schema errors: {errors}"

    def test_primary_repo_unchanged(self, tmp_path: Path) -> None:
        porcelain_before = robust_subprocess_run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        ).stdout

        guardian_dir = tmp_path / "guardian_artifacts"
        _, agg_path = _run_guardians_subprocess(guardian_dir)
        if agg_path is not None:
            dispatcher_dir = tmp_path / "dispatcher_artifacts"
            _run_dispatcher_dry_run(agg_path, dispatcher_dir)

        porcelain_after = robust_subprocess_run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        ).stdout
        assert porcelain_before == porcelain_after, (
            "Dispatcher dry-run mutated primary repo!\n"
            f"Before:\n{porcelain_before}\nAfter:\n{porcelain_after}"
        )


# ── Test: sub-check healer reachability via full subprocess path ──


class TestSubCheckReachabilityGolden:
    """Prove sub-check healer is reachable through guardian→dispatcher subprocess.

    Takes real guardian output, enriches one roll-up check with sub-check
    evidence (simulating what run_all_guardians will produce once wired),
    then runs dispatcher dry-run via subprocess and asserts sub-check ids
    appear in the combined_heal_result.
    """

    @pytest.fixture()
    def enriched_heal_result(self, tmp_path: Path) -> tuple[Path, dict]:
        """Run guardians, enrich aggregate with sub-checks, run dispatcher."""
        guardian_dir = tmp_path / "guardian_artifacts"
        _, agg_path = _run_guardians_subprocess(guardian_dir)
        assert agg_path is not None, "Guardians did not produce aggregate"

        # Enrich: inject sub-check evidence into classification_compliance
        agg_data = json.loads(agg_path.read_text(encoding="utf-8"))
        for check in agg_data.get("checks", []):
            if check.get("check_id") == "guardian_classification_compliance":
                check["evidence"] = {
                    "guardian_id": "classification_compliance",
                    "status": check.get("status", "FAIL"),
                    "checks": [
                        {
                            "check_id": "naming_compliance",
                            "status": "FAIL",
                            "details": "golden-trace synthetic sub-check",
                            "evidence": {
                                "violation_count": 1,
                                "violations": [
                                    {"path": "fake_agent_types.py", "suffixes": ["agent", "types"]},
                                ],
                            },
                        },
                        {
                            "check_id": "territory_compliance",
                            "status": "PASS",
                            "details": "golden-trace synthetic sub-check",
                            "evidence": {"violation_count": 0, "violations": []},
                        },
                    ],
                }
                break
        else:
            pytest.skip("guardian_classification_compliance not in aggregate")

        enriched_path = tmp_path / "enriched_aggregate.json"
        enriched_path.write_text(
            json.dumps(agg_data, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        dispatcher_dir = tmp_path / "dispatcher_artifacts"
        capture = _run_dispatcher_dry_run(enriched_path, dispatcher_dir)
        heal_path = dispatcher_dir / "combined_heal_result.json"
        return heal_path, capture

    def test_dispatcher_returns_zero(
        self,
        enriched_heal_result: tuple[Path, dict],
    ) -> None:
        _, capture = enriched_heal_result
        assert capture["returncode"] == 0, f"Dispatcher rc={capture['returncode']}:\n{capture['stderr_head']}"

    def test_naming_compliance_present(
        self,
        enriched_heal_result: tuple[Path, dict],
    ) -> None:
        heal_path, _ = enriched_heal_result
        assert heal_path.is_file()
        data = json.loads(heal_path.read_text(encoding="utf-8"))
        check_ids = [r["check_id"] for r in data.get("results", [])]
        assert "naming_compliance" in check_ids, f"naming_compliance not in results: {check_ids}"

    def test_territory_compliance_present(
        self,
        enriched_heal_result: tuple[Path, dict],
    ) -> None:
        heal_path, _ = enriched_heal_result
        data = json.loads(heal_path.read_text(encoding="utf-8"))
        check_ids = [r["check_id"] for r in data.get("results", [])]
        assert "territory_compliance" in check_ids, f"territory_compliance not in results: {check_ids}"

    def test_sub_checks_skipped_in_dry_run(
        self,
        enriched_heal_result: tuple[Path, dict],
    ) -> None:
        heal_path, _ = enriched_heal_result
        data = json.loads(heal_path.read_text(encoding="utf-8"))
        for result in data.get("results", []):
            if result["check_id"] in ("naming_compliance", "territory_compliance"):
                assert result["status"] == "SKIPPED", (
                    f"{result['check_id']} status={result['status']}, expected SKIPPED"
                )

    def test_no_repo_mutation(self, tmp_path: Path) -> None:
        porcelain_before = robust_subprocess_run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        ).stdout

        guardian_dir = tmp_path / "guardian_artifacts"
        _, agg_path = _run_guardians_subprocess(guardian_dir)
        if agg_path is not None:
            agg_data = json.loads(agg_path.read_text(encoding="utf-8"))
            for check in agg_data.get("checks", []):
                if check.get("check_id") == "guardian_classification_compliance":
                    check["evidence"] = {
                        "checks": [
                            {
                                "check_id": "naming_compliance",
                                "status": "FAIL",
                                "details": "test",
                                "evidence": {},
                            },
                        ],
                    }
                    break
            enriched = tmp_path / "enriched.json"
            enriched.write_text(json.dumps(agg_data), encoding="utf-8")
            _run_dispatcher_dry_run(enriched, tmp_path / "disp_out")

        porcelain_after = robust_subprocess_run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        ).stdout
        assert porcelain_before == porcelain_after


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

    def test_golden_dispatcher_dry_run_section_exists(self) -> None:
        data = json.loads(GOLDEN_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        assert "dispatcher_dry_run" in data, "Golden snapshot missing dispatcher_dry_run section"

    def test_golden_dispatcher_returncode_zero(self) -> None:
        data = json.loads(GOLDEN_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        disp = data.get("dispatcher_dry_run", {})
        assert disp.get("returncode") == 0

    def test_golden_dispatcher_created_utc(self) -> None:
        data = json.loads(GOLDEN_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        disp = data.get("dispatcher_dry_run", {})
        assert disp.get("created_utc") == DISPATCHER_FIXED_UTC

    def test_golden_dispatcher_heal_result_has_sha256(self) -> None:
        data = json.loads(GOLDEN_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        disp = data.get("dispatcher_dry_run", {})
        hr = disp.get("combined_heal_result", {})
        assert hr.get("exists") is True
        h = hr.get("sha256", "")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)
