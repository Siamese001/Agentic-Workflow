"""Tests for IBlackboardLeaseVerifierProtocol phase hardening.

Phase: 7e4d24cdf7 harden(interfaces): remove import-time side effects, atomic writes, fail-fast proxies

Covers:
  G2  get_project_root() raises RuntimeError instead of returning Path.cwd()
  G3  validate_sandbox() rejects path traversal via ValueError->SandboxViolationError
  G4  validate_sandbox() rejects excluded directories
  G5  require_healing_lease deny/allow paths
"""

import pytest
from unittest.mock import MagicMock, patch

import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol as _mod
from agentic_core.interfaces.IBlackboardLeaseVerifierProtocol import (
    HealingLeaseError,
    PreservationViolationError,
    SandboxViolationError,
    create_directory,
    delete_file,
    get_project_root,
    list_files,
    move_file,
    read_file,
    require_healing_lease,
    validate_sandbox,
    write_file,
)
from agentic_core.L2_execution.types.tool_args_types import (
    CreateDirectoryArgs,
    DeleteFileArgs,
    ListFilesArgs,
    MoveFileArgs,
    ReadFileArgs,
    WriteFileArgs,
)


@pytest.mark.unit
class TestGetProjectRoot:
    def test_returns_path_with_git_or_agentic_core(self):
        """Happy: real repo has .git; get_project_root() returns a valid Path."""
        root = get_project_root()
        assert root.is_dir()
        assert (root / ".git").exists() or (root / "agentic_core").exists()

    def test_raises_runtime_error_at_filesystem_root(self):
        """Failure (G2): when parent==self (fs root), raises RuntimeError not Path.cwd()."""

        class _FsRoot:
            def __init__(self, *_args):
                pass

            def resolve(self):
                return self

            @property
            def parent(self):
                return self

            def __truediv__(self, _other):
                child = MagicMock()
                child.exists.return_value = False
                return child

            def __eq__(self, other):
                return other is self

            def __ne__(self, other):
                return other is not self

        with patch.object(_mod, "Path", _FsRoot):
            with pytest.raises(RuntimeError, match="Project root not found"):
                get_project_root()


@pytest.mark.unit
class TestValidateSandbox:
    def test_returns_resolved_path_for_valid_input(self, tmp_path, monkeypatch):
        """Happy: relative path inside root returns resolved absolute Path."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "safe").mkdir()
        result = validate_sandbox("safe")
        assert result == (tmp_path / "safe").resolve()

    def test_raises_for_path_traversal(self, tmp_path, monkeypatch):
        """Failure (G3): ../../ traversal raises SandboxViolationError."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        with pytest.raises(SandboxViolationError):
            validate_sandbox("../../outside_root")

    def test_raises_for_excluded_directory(self, tmp_path, monkeypatch):
        """Edge (G4): path component in EXCLUDED_DIRS raises SandboxViolationError."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        monkeypatch.setattr(_mod, "EXCLUDED_DIRS", frozenset(["__vault__"]))
        (tmp_path / "__vault__").mkdir()
        with pytest.raises(SandboxViolationError, match="Access denied"):
            validate_sandbox("__vault__")

    def test_raises_for_empty_path(self, monkeypatch, tmp_path):
        """Edge: empty string raises SandboxViolationError before root resolution."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        with pytest.raises(SandboxViolationError, match="Empty path"):
            validate_sandbox("")


@pytest.mark.unit
class TestRequireHealingLease:
    def test_raises_when_lease_denied(self):
        """Failure (G5): blackboard.verify_healing_lease returns False -> HealingLeaseError."""
        blackboard = MagicMock()
        blackboard.verify_healing_lease.return_value = False

        @require_healing_lease
        def _op(args, blackboard=None, agent_id=None):
            return "ok"

        with pytest.raises(HealingLeaseError, match="does not hold HealingLease"):
            _op(MagicMock(path="f.txt"), blackboard=blackboard, agent_id="bot1")

    def test_no_error_when_blackboard_absent(self):
        """Edge (G5): no blackboard -> lease check skipped, function returns normally."""

        @require_healing_lease
        def _op(args, blackboard=None, agent_id=None):
            return "ok"

        assert _op(MagicMock(path="f.txt")) == "ok"

    def test_no_path_attribute_on_args_skips_lease_check(self):
        """G2: getattr fallback returns None → file_path is None → lease check skipped even when blackboard denies."""
        blackboard = MagicMock()
        blackboard.verify_healing_lease.return_value = False

        @require_healing_lease
        def _op(args, blackboard=None, agent_id=None):
            return "executed"

        result = _op(MagicMock(spec=[]), blackboard=blackboard, agent_id="bot1")
        assert result == "executed"
        blackboard.verify_healing_lease.assert_not_called()

    def test_passes_when_lease_granted(self):
        """Happy (G5): blackboard grants lease -> function executes."""
        blackboard = MagicMock()
        blackboard.verify_healing_lease.return_value = True

        @require_healing_lease
        def _op(args, blackboard=None, agent_id=None):
            return "granted"

        assert _op(MagicMock(path="f.txt"), blackboard=blackboard, agent_id="a1") == "granted"


@pytest.mark.unit
class TestReadFile:
    def test_returns_file_content(self, tmp_path, monkeypatch):
        """Happy (G6): existing file returns UTF-8 content."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "hello.txt").write_text("world", encoding="utf-8")
        assert read_file(ReadFileArgs(path="hello.txt")) == "world"

    def test_raises_file_not_found(self, tmp_path, monkeypatch):
        """Failure (G6): missing file raises FileNotFoundError."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        with pytest.raises(FileNotFoundError):
            read_file(ReadFileArgs(path="ghost.txt"))

    def test_raises_for_directory_path(self, tmp_path, monkeypatch):
        """Edge (G6): directory path raises ValueError (not a file)."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "adir").mkdir()
        with pytest.raises(ValueError, match="Not a file"):
            read_file(ReadFileArgs(path="adir"))


@pytest.mark.unit
class TestWriteFile:
    def test_creates_new_file_atomically(self, tmp_path, monkeypatch):
        """Happy (G10): write_file creates file with correct content via temp+replace."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        write_file(WriteFileArgs(path="out.txt", content="atomic content"))
        assert (tmp_path / "out.txt").read_text(encoding="utf-8") == "atomic content"

    def test_preservation_violation_raises(self, tmp_path, monkeypatch):
        """Failure (G7): shrinking file >10% raises PreservationViolationError."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        big = "\n".join(f"line{i}" for i in range(100))
        (tmp_path / "big.txt").write_text(big, encoding="utf-8")
        with pytest.raises(PreservationViolationError):
            write_file(WriteFileArgs(path="big.txt", content="just one line"))

    def test_override_preservation_bypasses_check(self, tmp_path, monkeypatch):
        """Edge (G8): override_preservation=True skips preservation check and writes."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        big = "\n".join(f"line{i}" for i in range(100))
        (tmp_path / "big2.txt").write_text(big, encoding="utf-8")
        write_file(
            WriteFileArgs(path="big2.txt", content="tiny"),
            override_preservation=True,
        )
        assert (tmp_path / "big2.txt").read_text(encoding="utf-8") == "tiny"

    def test_log_security_event_called_before_preservation_error(self, tmp_path, monkeypatch):
        """Edge (G9): blackboard.log_security_event is called with PRESERVATION_VIOLATION before raise."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        big = "\n".join(f"line{i}" for i in range(100))
        (tmp_path / "big3.txt").write_text(big, encoding="utf-8")
        blackboard = MagicMock()
        blackboard.verify_healing_lease.return_value = True
        with pytest.raises(PreservationViolationError):
            write_file(
                WriteFileArgs(path="big3.txt", content="line1"),
                blackboard=blackboard,
                agent_id="agent1",
            )
        blackboard.log_security_event.assert_called_once()
        kwargs = blackboard.log_security_event.call_args.kwargs
        assert kwargs["event_type"] == "PRESERVATION_VIOLATION"
        assert kwargs["file_path"] == "big3.txt"
        details = kwargs["details"]
        assert details["original_lines"] == 100
        assert details["new_lines"] == 1
        assert details["threshold"] == 90
        assert details["deletion_percentage"] == 99.0

    def test_log_security_event_exception_does_not_mask_preservation_error(self, tmp_path, monkeypatch):
        """G1: if log_security_event raises, PreservationViolationError still propagates."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        big = "\n".join(f"line{i}" for i in range(100))
        (tmp_path / "big4.txt").write_text(big, encoding="utf-8")
        blackboard = MagicMock()
        blackboard.verify_healing_lease.return_value = True
        blackboard.log_security_event.side_effect = RuntimeError("log backend down")
        with pytest.raises(PreservationViolationError):
            write_file(
                WriteFileArgs(path="big4.txt", content="line1"),
                blackboard=blackboard,
                agent_id="agent1",
            )
        blackboard.log_security_event.assert_called_once()

    def test_oserror_during_preservation_check_write_still_proceeds(self, tmp_path, monkeypatch):
        """G2: OSError on read_text() during preservation pre-check is silently skipped; write proceeds."""
        import pathlib

        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "locked.txt").write_text("x\n" * 100, encoding="utf-8")
        _call = [0]
        _orig = pathlib.Path.read_text

        def _raise_first(self, *a, **kw):
            _call[0] += 1
            if _call[0] == 1:
                raise PermissionError("simulated read error")
            return _orig(self, *a, **kw)

        monkeypatch.setattr(pathlib.Path, "read_text", _raise_first)
        write_file(WriteFileArgs(path="locked.txt", content="replaced"))
        assert (tmp_path / "locked.txt").read_text(encoding="utf-8") == "replaced"

    def test_write_exactly_90pct_passes(self, tmp_path, monkeypatch):
        """G3 boundary-pass: exactly 90/100 lines does NOT raise (strict < not <=)."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        original = "\n".join(f"line{i}" for i in range(100))
        (tmp_path / "ninety.txt").write_text(original, encoding="utf-8")
        content_90 = "\n".join(f"line{i}" for i in range(90))
        write_file(WriteFileArgs(path="ninety.txt", content=content_90))
        assert (tmp_path / "ninety.txt").read_text(encoding="utf-8") == content_90

    def test_write_to_empty_original_passes(self, tmp_path, monkeypatch):
        """G1 boundary: empty original file (0 lines) → min_lines=0 → any content accepted."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "empty.txt").write_text("", encoding="utf-8")
        write_file(WriteFileArgs(path="empty.txt", content="new content"))
        assert (tmp_path / "empty.txt").read_text(encoding="utf-8") == "new content"

    def test_write_89pct_raises(self, tmp_path, monkeypatch):
        """G3 boundary-fail: 89/100 lines raises PreservationViolationError."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        original = "\n".join(f"line{i}" for i in range(100))
        (tmp_path / "eighty9.txt").write_text(original, encoding="utf-8")
        content_89 = "\n".join(f"line{i}" for i in range(89))
        with pytest.raises(PreservationViolationError):
            write_file(WriteFileArgs(path="eighty9.txt", content=content_89))

    def test_single_line_original_requires_at_least_one_line(self, tmp_path, monkeypatch):
        """G2 boundary: 1-line file → min_lines=max(1,int(0.9))=1 → writing 0 lines raises."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "one.txt").write_text("only line\n", encoding="utf-8")
        with pytest.raises(PreservationViolationError):
            write_file(WriteFileArgs(path="one.txt", content=""))


@pytest.mark.unit
class TestListFiles:
    def test_returns_sorted_files(self, tmp_path, monkeypatch):
        """Happy (G2): existing directory returns sorted relative file paths."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "b.txt").write_text("b", encoding="utf-8")
        (tmp_path / "a.txt").write_text("a", encoding="utf-8")
        result = list_files(ListFilesArgs(directory="."))
        assert result == sorted(result)
        assert any("a.txt" in p for p in result)
        assert any("b.txt" in p for p in result)

    def test_raises_for_missing_directory(self, tmp_path, monkeypatch):
        """Failure (G2): non-existent directory raises FileNotFoundError."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        with pytest.raises(FileNotFoundError):
            list_files(ListFilesArgs(directory="does_not_exist"))

    def test_raises_for_file_as_directory(self, tmp_path, monkeypatch):
        """Edge (G2): path resolving to a file raises NotADirectoryError."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "notadir.txt").write_text("x", encoding="utf-8")
        with pytest.raises(NotADirectoryError):
            list_files(ListFilesArgs(directory="notadir.txt"))


@pytest.mark.unit
class TestCreateDirectory:
    def test_creates_nested_directory(self, tmp_path, monkeypatch):
        """Happy (G3): create_directory makes nested dirs under sandbox root."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        create_directory(CreateDirectoryArgs(path="newdir/subdir"))
        assert (tmp_path / "newdir" / "subdir").is_dir()

    def test_idempotent_on_existing_directory(self, tmp_path, monkeypatch):
        """Edge (G3): create_directory on existing dir does not raise."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "existing").mkdir()
        create_directory(CreateDirectoryArgs(path="existing"))
        assert (tmp_path / "existing").is_dir()


@pytest.mark.unit
class TestMoveFile:
    def test_raises_file_not_found_for_missing_source(self, tmp_path, monkeypatch):
        """Failure (G1): move_file raises FileNotFoundError when source does not exist."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        with pytest.raises(FileNotFoundError):
            move_file(MoveFileArgs(source="no_src.txt", destination="dst.txt"))

    def test_emits_deprecation_warning(self, tmp_path, monkeypatch):
        """Failure (G1): move_file emits DeprecationWarning before raising FileNotFoundError."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        with pytest.warns(DeprecationWarning, match="deprecated"):
            with pytest.raises(FileNotFoundError):
                move_file(MoveFileArgs(source="no_src.txt", destination="dst.txt"))

    def test_raises_file_exists_error_when_dest_exists(self, tmp_path, monkeypatch):
        """Edge (G1): move_file raises FileExistsError when destination already exists."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        (tmp_path / "src.txt").write_text("content", encoding="utf-8")
        (tmp_path / "dst.txt").write_text("content", encoding="utf-8")
        with pytest.raises(FileExistsError):
            move_file(MoveFileArgs(source="src.txt", destination="dst.txt"))


@pytest.mark.unit
class TestDeleteFile:
    def test_raises_file_not_found_for_missing_file(self, tmp_path, monkeypatch):
        """Failure (G2): delete_file raises FileNotFoundError when file does not exist."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        with pytest.raises(FileNotFoundError):
            delete_file(DeleteFileArgs(path="no_file.txt"))

    def test_emits_deprecation_warning(self, tmp_path, monkeypatch):
        """Failure (G2): delete_file emits DeprecationWarning before raising FileNotFoundError."""
        monkeypatch.setattr(_mod, "get_project_root", lambda: tmp_path)
        with pytest.warns(DeprecationWarning, match="deprecated"):
            with pytest.raises(FileNotFoundError):
                delete_file(DeleteFileArgs(path="no_file.txt"))
