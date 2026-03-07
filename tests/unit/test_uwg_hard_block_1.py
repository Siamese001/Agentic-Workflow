"""Tests for UniversalWriteGateway hard-blocking behavior.

Phase 3: UWG Runtime Blocking — L2 [UWG], Guarantee #6.
Verifies that write_file/append_file/delete_file/rename_file raise ToolNotAllowedError
on blocked paths/extensions (live mode) and return SimulationResult in replay_mode.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.UniversalWriteGateway import (
    MutationRecord,
    SimulationResult,
    ToolNotAllowedError,
    UniversalWriteGateway,
)


class TestWriteFileHardBlock:
    def test_blocked_extension_raises(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            gw.write_file("some/path/module.py", b"print('hello')")

    def test_blocked_js_extension_raises(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            gw.write_file("src/app.js", b"console.log('hi')")

    def test_blocked_path_not_in_allowed_set_raises(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            gw.write_file("secret/config.json", b"{}")

    def test_allowed_path_succeeds(self):
        gw = UniversalWriteGateway(replay_mode=False)
        result = gw.write_file("artifacts/output.json", b'{"key": "value"}')
        assert isinstance(result, MutationRecord)
        assert result.permitted is True
        assert result.operation == "write"

    def test_replay_mode_returns_simulation_result(self):
        gw = UniversalWriteGateway(replay_mode=True)
        result = gw.write_file("some/path/module.py", b"print('hello')")
        assert isinstance(result, SimulationResult)
        assert result.replay_mode is True
        assert result.operation == "write"

    def test_blocked_write_recorded_in_ledger(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError):
            gw.write_file("src/evil.py", b"pass")
        ledger = gw.get_mutation_ledger()
        assert len(ledger) == 1
        assert ledger[0].permitted is False
        assert ledger[0].operation == "write"


class TestAppendFileHardBlock:
    def test_blocked_extension_raises(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            gw.append_file("core/engine.py", b"# extra")

    def test_allowed_path_succeeds(self):
        gw = UniversalWriteGateway(replay_mode=False)
        result = gw.append_file("logs/run.log", b"line\n")
        assert isinstance(result, MutationRecord)
        assert result.permitted is True

    def test_replay_mode_returns_simulation_result(self):
        gw = UniversalWriteGateway(replay_mode=True)
        result = gw.append_file("core/engine.py", b"# extra")
        assert isinstance(result, SimulationResult)
        assert result.operation == "append"


class TestDeleteFileHardBlock:
    def test_blocked_path_raises(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            gw.delete_file("ops_scripts/ci/scanner.py")

    def test_allowed_path_succeeds(self):
        gw = UniversalWriteGateway(replay_mode=False)
        result = gw.delete_file("artifacts/old_report.json")
        assert isinstance(result, MutationRecord)
        assert result.permitted is True
        assert result.operation == "delete"

    def test_replay_mode_returns_simulation_result(self):
        gw = UniversalWriteGateway(replay_mode=True)
        result = gw.delete_file("ops_scripts/ci/scanner.py")
        assert isinstance(result, SimulationResult)
        assert result.operation == "delete"


class TestRenameFileHardBlock:
    def test_blocked_src_raises(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            gw.rename_file("src/bad.py", "artifacts/moved.py")

    def test_blocked_dst_raises(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            gw.rename_file("artifacts/ok.json", "src/bad.py")

    def test_replay_mode_returns_simulation_result(self):
        gw = UniversalWriteGateway(replay_mode=True)
        result = gw.rename_file("src/bad.py", "artifacts/moved.json")
        assert isinstance(result, SimulationResult)
        assert result.operation == "rename"
