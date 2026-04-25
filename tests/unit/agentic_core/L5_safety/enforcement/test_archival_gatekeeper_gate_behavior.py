"""Behavioral tests for ``agentic_core.L5_safety.enforcement.archival_gatekeeper_gate``.

Covers ArchivalGatekeeper — the singleton service for destructive file operations:
- ArchivalOperation enum values.
- ArchivalResult.to_dict serialization.
- Singleton: get_instance requires project_root on first call; reset_instance clears it.
- _get_archive_path: YYYY-MM-DD date folder + relative path; out-of-root paths accepted.
- _validate_path: missing source, within-archive, protected dir all rejected.
- safe_move: missing source error; approval gate; destination-exists without overwrite;
  overwrite=True replaces; success moves file.
- safe_archive: success moves to archive; collision appends timestamp suffix; missing source error.
- safe_delete: soft-delete moves file to archive (file removed from source).
- restore_from_archive: restores under project_root; out-of-archive rejected.
- Batch mode: ARCHIVE_BATCH_ACCEPT=1 auto-approves; SOVEREIGN_AUTO_APPROVE=1 auto-approves.
- set_require_approval(False) skips prompts.
- set_input_function integration; user denial path.
- L4 ledger hook: register, notify, hook raises → exception propagates.
- get_audit_log: returns entries most-recent-first, within limit.
- get_operation_count increments only on success.
"""

from __future__ import annotations

import json
import os
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import (
    ArchivalGatekeeper,
    ArchivalOperation,
    ArchivalResult,
)


# ---- fixtures -----------------------------------------------------------


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Isolated project root for each test."""
    return tmp_path


@pytest.fixture
def gk(
    project_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[ArchivalGatekeeper, None, None]:
    """ArchivalGatekeeper with approval auto-disabled for write-through tests."""
    ArchivalGatekeeper.reset_instance()
    # Default: no interactive prompts.
    monkeypatch.delenv("ARCHIVE_BATCH_ACCEPT", raising=False)
    monkeypatch.delenv("SOVEREIGN_AUTO_APPROVE", raising=False)
    instance = ArchivalGatekeeper.get_instance(project_root)
    instance.set_require_approval(False)
    yield instance
    ArchivalGatekeeper.reset_instance()


def _mkfile(root: Path, rel: str, content: str = "data") -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


# ---- Enum + Result ------------------------------------------------------


class TestArchivalOperation:
    def test_values(self) -> None:
        assert ArchivalOperation.MOVE.value == "MOVE"
        assert ArchivalOperation.ARCHIVE.value == "ARCHIVE"
        assert ArchivalOperation.DELETE.value == "DELETE"


class TestArchivalResult:
    def test_to_dict_serialization(self, tmp_path: Path) -> None:
        r = ArchivalResult(
            success=True,
            operation=ArchivalOperation.MOVE,
            source_path=tmp_path / "src",
            destination_path=tmp_path / "dst",
            requester_agent="MyAgent",
            reason="because",
        )
        d = r.to_dict()
        assert d["success"] is True
        assert d["operation"] == "MOVE"
        assert d["requester_agent"] == "MyAgent"
        assert d["reason"] == "because"
        assert d["source_path"].endswith("src")
        assert d["destination_path"].endswith("dst")

    def test_to_dict_none_destination(self, tmp_path: Path) -> None:
        r = ArchivalResult(
            success=False,
            operation=ArchivalOperation.DELETE,
            source_path=tmp_path / "x",
        )
        assert r.to_dict()["destination_path"] is None

    def test_default_timestamp_and_status(self, tmp_path: Path) -> None:
        r = ArchivalResult(
            success=True,
            operation=ArchivalOperation.MOVE,
            source_path=tmp_path / "x",
        )
        assert r.approval_status == "PENDING"
        # timestamp is a valid ISO string
        datetime.fromisoformat(r.timestamp)


# ---- Singleton ---------------------------------------------------------


class TestSingleton:
    def test_first_call_requires_project_root(self) -> None:
        ArchivalGatekeeper.reset_instance()
        with pytest.raises(ValueError, match="project_root"):
            ArchivalGatekeeper.get_instance()

    def test_same_instance_returned(self, project_root: Path) -> None:
        ArchivalGatekeeper.reset_instance()
        i1 = ArchivalGatekeeper.get_instance(project_root)
        i2 = ArchivalGatekeeper.get_instance()  # no project_root needed after first
        assert i1 is i2
        ArchivalGatekeeper.reset_instance()

    def test_reset_instance_clears(self, project_root: Path) -> None:
        ArchivalGatekeeper.reset_instance()
        i1 = ArchivalGatekeeper.get_instance(project_root)
        ArchivalGatekeeper.reset_instance()
        i2 = ArchivalGatekeeper.get_instance(project_root)
        assert i1 is not i2
        ArchivalGatekeeper.reset_instance()


# ---- _get_archive_path -------------------------------------------------


class TestGetArchivePath:
    def test_uses_date_folder(self, gk: ArchivalGatekeeper, project_root: Path) -> None:
        src = project_root / "sub" / "foo.py"
        ap = gk._get_archive_path(src)
        date = datetime.now().strftime("%Y-%m-%d")
        assert date in ap.parts
        assert ap.name == "foo.py"

    def test_relative_to_project_root(self, gk: ArchivalGatekeeper, project_root: Path) -> None:
        src = project_root / "x" / "y.py"
        ap = gk._get_archive_path(src)
        # Archive path must live under the gatekeeper's archive_root
        assert gk.archive_root in ap.parents

    def test_out_of_root_source_handled(
        self,
        gk: ArchivalGatekeeper,
        tmp_path_factory: pytest.TempPathFactory,
    ) -> None:
        # A file outside project_root → source.relative_to raises ValueError,
        # and _get_archive_path falls back to an escaped name.
        other = tmp_path_factory.mktemp("outside") / "y.py"
        ap = gk._get_archive_path(other)
        assert gk.archive_root in ap.parents
        assert "y.py" in ap.name or ap.name == "y.py"


# ---- _validate_path ----------------------------------------------------


class TestValidatePath:
    def test_missing_source_error(self, gk: ArchivalGatekeeper, project_root: Path) -> None:
        err = gk._validate_path(project_root / "ghost", "move")
        assert err is not None
        assert "does not exist" in err

    def test_within_archive_rejected(self, gk: ArchivalGatekeeper) -> None:
        # Put a file inside the archive_root and attempt to operate on it
        inside = gk.archive_root / "inside.txt"
        inside.parent.mkdir(parents=True, exist_ok=True)
        inside.write_text("x")
        err = gk._validate_path(inside, "move")
        assert err is not None
        assert "archive directory" in err

    def test_allow_archive_bypasses_archive_check(self, gk: ArchivalGatekeeper) -> None:
        # allow_archive=True skips the "inside archive" rejection but the
        # archive-dir check message ("archive directory") no longer appears —
        # the other validators (e.g. protected-dir) may still reject.
        inside = gk.archive_root / "inside.txt"
        inside.parent.mkdir(parents=True, exist_ok=True)
        inside.write_text("x")
        err = gk._validate_path(inside, "restore", allow_archive=True)
        assert err is None or "archive directory" not in err

    def test_protected_dir_rejected(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        # Pick a known-protected name — GLOBAL_EXCLUDED_DIRS contains __pycache__
        protected = project_root / "pkg" / "__pycache__" / "m.pyc"
        protected.parent.mkdir(parents=True, exist_ok=True)
        protected.write_text("x")
        err = gk._validate_path(protected, "delete")
        assert err is not None
        assert "protected" in err


# ---- safe_move ---------------------------------------------------------


class TestSafeMove:
    def test_missing_source_errors(self, gk: ArchivalGatekeeper, project_root: Path) -> None:
        r = gk.safe_move(
            project_root / "no-such",
            project_root / "dst",
            "Agent",
            "reason",
        )
        assert r.success is False
        assert "does not exist" in (r.error or "")

    def test_success_moves_file(self, gk: ArchivalGatekeeper, project_root: Path) -> None:
        src = _mkfile(project_root, "a/b.py", "hi")
        dst = project_root / "moved" / "b.py"
        r = gk.safe_move(src, dst, "Agent", "relocation")
        assert r.success is True
        assert dst.exists()
        assert not src.exists()
        assert r.operation == ArchivalOperation.MOVE

    def test_destination_exists_no_overwrite(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        src = _mkfile(project_root, "src.py")
        dst = _mkfile(project_root, "dst.py", "existing")
        r = gk.safe_move(src, dst, "Agent", "r", overwrite=False)
        assert r.success is False
        assert "already exists" in (r.error or "")
        # Both source and destination preserved
        assert src.exists()
        assert dst.read_text() == "existing"

    def test_overwrite_replaces_file(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        src = _mkfile(project_root, "src.py", "NEW")
        dst = _mkfile(project_root, "dst.py", "OLD")
        r = gk.safe_move(src, dst, "Agent", "r", overwrite=True)
        assert r.success is True
        assert dst.read_text() == "NEW"
        assert not src.exists()

    def test_denial_returns_failed_result(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        gk.set_require_approval(True)
        gk.set_input_function(lambda _prompt: "n")
        src = _mkfile(project_root, "src.py")
        dst = project_root / "dst.py"
        r = gk.safe_move(src, dst, "Agent", "r")
        assert r.success is False
        assert "User denied" in (r.error or "")
        # Source untouched, destination never created
        assert src.exists()
        assert not dst.exists()


# ---- safe_archive ------------------------------------------------------


class TestSafeArchive:
    def test_success_moves_to_archive(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        src = _mkfile(project_root, "to_archive.py", "content")
        r = gk.safe_archive(src, "Agent", "violation")
        assert r.success is True
        assert r.destination_path is not None
        assert r.destination_path.exists()
        assert not src.exists()
        assert gk.archive_root in r.destination_path.parents

    def test_missing_source_errors(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        r = gk.safe_archive(project_root / "ghost.py", "Agent", "r")
        assert r.success is False
        assert "does not exist" in (r.error or "")

    def test_collision_suffixes_with_time(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        # First archive succeeds; re-create source and archive again to force collision
        src1 = _mkfile(project_root, "dup.py", "v1")
        r1 = gk.safe_archive(src1, "Agent", "first")
        assert r1.success is True

        src2 = _mkfile(project_root, "dup.py", "v2")
        r2 = gk.safe_archive(src2, "Agent", "second")
        assert r2.success is True
        # Two different destination paths
        assert r1.destination_path != r2.destination_path
        assert r1.destination_path.exists()
        assert r2.destination_path.exists()


# ---- safe_delete (soft) ------------------------------------------------


class TestSafeDelete:
    def test_soft_delete_moves_to_archive(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        src = _mkfile(project_root, "delete_me.py", "x")
        r = gk.safe_delete(src, "Agent", "cleanup")
        assert r.success is True
        assert r.operation == ArchivalOperation.DELETE
        assert not src.exists()
        assert r.destination_path is not None
        assert r.destination_path.exists()
        assert "SOFT DELETE" in r.reason

    def test_missing_source_errors(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        r = gk.safe_delete(project_root / "ghost.py", "Agent", "r")
        assert r.success is False


# ---- restore_from_archive ---------------------------------------------


class TestRestoreFromArchive:
    def test_out_of_archive_rejected(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        outside = _mkfile(project_root, "outside.py")
        r = gk.restore_from_archive(outside, "Agent", "r")
        assert r.success is False
        assert "not in archive" in (r.error or "")

    def test_success_restores_to_original_location(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        src = _mkfile(project_root, "pkg/mod.py", "content")
        arch = gk.safe_archive(src, "Agent", "first")
        assert arch.success is True
        # Now restore
        r = gk.restore_from_archive(arch.destination_path, "Agent", "undo")
        assert r.success is True
        assert (project_root / "pkg" / "mod.py").exists()


# ---- Batch / approval modes --------------------------------------------


class TestApprovalModes:
    def test_batch_accept_env(
        self,
        project_root: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ArchivalGatekeeper.reset_instance()
        monkeypatch.setenv("ARCHIVE_BATCH_ACCEPT", "1")
        gk = ArchivalGatekeeper.get_instance(project_root)
        # Keep approval required — batch env should auto-approve
        gk.set_require_approval(True)
        src = _mkfile(project_root, "a.py")
        r = gk.safe_archive(src, "Agent", "r")
        assert r.success is True
        assert "BATCH_APPROVED" in r.approval_status
        ArchivalGatekeeper.reset_instance()

    def test_sovereign_auto_approve(
        self,
        project_root: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ArchivalGatekeeper.reset_instance()
        monkeypatch.setenv("SOVEREIGN_AUTO_APPROVE", "1")
        gk = ArchivalGatekeeper.get_instance(project_root)
        gk.set_require_approval(True)
        src = _mkfile(project_root, "b.py")
        r = gk.safe_archive(src, "Agent", "r")
        assert r.success is True
        assert "SOVEREIGN_AUTO_APPROVE" in r.approval_status
        ArchivalGatekeeper.reset_instance()

    def test_require_approval_false_bypasses_prompt(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        gk.set_require_approval(False)

        def _boom(_prompt: str) -> str:
            raise AssertionError("input must not be called")

        gk.set_input_function(_boom)
        src = _mkfile(project_root, "c.py")
        r = gk.safe_archive(src, "Agent", "r")
        assert r.success is True
        assert r.approval_status == "APPROVED"


# ---- L4 ledger hook ----------------------------------------------------


class TestL4LedgerHook:
    def test_hook_called_on_success(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        hook = MagicMock()
        gk.set_l4_ledger_hook(hook)
        src = _mkfile(project_root, "x.py")
        gk.safe_archive(src, "Agent", "r")
        hook.assert_called_once()
        passed = hook.call_args.args[0]
        assert passed.success is True
        assert passed.operation == ArchivalOperation.ARCHIVE

    def test_hook_exception_propagates(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        def bad_hook(_r: ArchivalResult) -> None:
            raise RuntimeError("ledger-failed")

        gk.set_l4_ledger_hook(bad_hook)
        src = _mkfile(project_root, "y.py")
        with pytest.raises(RuntimeError, match="ledger-failed"):
            gk.safe_archive(src, "Agent", "r")


# ---- Audit log + counters ----------------------------------------------


class TestAuditLog:
    def test_get_audit_log_empty(self, gk: ArchivalGatekeeper) -> None:
        assert gk.get_audit_log() == []

    def test_get_audit_log_returns_recent_first(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        gk.safe_archive(_mkfile(project_root, "a.py"), "A", "first")
        gk.safe_archive(_mkfile(project_root, "b.py"), "A", "second")
        entries = gk.get_audit_log()
        assert len(entries) >= 2
        # Most recent first
        assert entries[0]["reason"] == "second"
        assert entries[1]["reason"] == "first"

    def test_get_audit_log_respects_limit(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        for i in range(5):
            gk.safe_archive(_mkfile(project_root, f"f{i}.py"), "A", f"n{i}")
        entries = gk.get_audit_log(limit=3)
        assert len(entries) == 3

    def test_audit_log_jsonl_parseable(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        gk.safe_archive(_mkfile(project_root, "parse.py"), "A", "r")
        raw = gk.audit_log_path.read_text(encoding="utf-8").splitlines()
        for line in raw:
            json.loads(line)


class TestOperationCounter:
    def test_counter_increments_on_success(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        start = gk.get_operation_count()
        gk.safe_archive(_mkfile(project_root, "a.py"), "A", "r")
        gk.safe_archive(_mkfile(project_root, "b.py"), "A", "r")
        assert gk.get_operation_count() == start + 2

    def test_counter_skips_failed(
        self,
        gk: ArchivalGatekeeper,
        project_root: Path,
    ) -> None:
        start = gk.get_operation_count()
        gk.safe_archive(project_root / "ghost.py", "A", "r")  # missing source
        assert gk.get_operation_count() == start
