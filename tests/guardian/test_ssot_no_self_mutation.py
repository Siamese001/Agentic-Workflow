"""
Tests: SSOT heal runner source root fence — blocks writes to tracked source directories.

Verifies that _deny_writes_into_source_roots() raises RuntimeError when
AGENTIC_DENY_SOURCE_MUTATION=1 and target is under agentic_core/.
"""

from pathlib import Path

import pytest

pytestmark = pytest.mark.guardian


class TestSourceRootFence:
    def test_blocks_write_to_agentic_core(self, monkeypatch, tmp_path):
        """Write to agentic_core/... is blocked when fence is active."""
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        from agentic_core.L2_execution.tools import write_gateway

        # Reset cached repo root to use a fake one
        monkeypatch.setattr(write_gateway, "_REPO_ROOT", tmp_path)

        # Create fake agentic_core directory
        fake_source = tmp_path / "agentic_core" / "L0_routing" / "scripts"
        fake_source.mkdir(parents=True)
        target = fake_source / "execute_ssot.py"

        with pytest.raises(RuntimeError, match="SOURCE_MUTATION_BLOCKED"):
            write_gateway.write_text(target, "corrupted content")

    def test_allows_write_to_docs_evidence(self, monkeypatch, tmp_path):
        """Write to docs/evidence/... is allowed (safe output)."""
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        from agentic_core.L2_execution.tools import write_gateway

        monkeypatch.setattr(write_gateway, "_REPO_ROOT", tmp_path)

        safe_output = tmp_path / "docs" / "evidence"
        safe_output.mkdir(parents=True)
        target = safe_output / "test_output.txt"

        # Should NOT raise
        result = write_gateway.write_text(target, "safe content")
        assert Path(result).exists()
        assert Path(result).read_text() == "safe content"

    def test_allows_write_when_fence_disabled(self, monkeypatch, tmp_path):
        """Write to agentic_core/... is allowed when fence is disabled."""
        monkeypatch.delenv("AGENTIC_DENY_SOURCE_MUTATION", raising=False)

        from agentic_core.L2_execution.tools import write_gateway

        monkeypatch.setattr(write_gateway, "_REPO_ROOT", tmp_path)

        fake_source = tmp_path / "agentic_core" / "test"
        fake_source.mkdir(parents=True)
        target = fake_source / "allowed.py"

        # Should NOT raise when fence is disabled
        result = write_gateway.write_text(target, "allowed content")
        assert Path(result).exists()

    def test_blocks_move_to_agentic_core(self, monkeypatch, tmp_path):
        """move_path to agentic_core/... is blocked when fence is active."""
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        from agentic_core.L2_execution.tools import write_gateway

        monkeypatch.setattr(write_gateway, "_REPO_ROOT", tmp_path)

        # Create source file outside protected area
        src = tmp_path / "temp_file.txt"
        src.write_text("content")

        # Target inside protected area
        fake_source = tmp_path / "agentic_core" / "test"
        fake_source.mkdir(parents=True)
        dst = fake_source / "moved.py"

        with pytest.raises(RuntimeError, match="SOURCE_MUTATION_BLOCKED"):
            write_gateway.move_path(src, dst)

    def test_blocks_copy_to_tests(self, monkeypatch, tmp_path):
        """copy_file to tests/... is blocked when fence is active."""
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        from agentic_core.L2_execution.tools import write_gateway

        monkeypatch.setattr(write_gateway, "_REPO_ROOT", tmp_path)

        src = tmp_path / "temp_file.txt"
        src.write_text("content")

        fake_tests = tmp_path / "tests" / "guardian"
        fake_tests.mkdir(parents=True)
        dst = fake_tests / "copied.py"

        with pytest.raises(RuntimeError, match="SOURCE_MUTATION_BLOCKED"):
            write_gateway.copy_file(src, dst)

    def test_blocks_remove_file_in_agentic_core(self, monkeypatch, tmp_path):
        """remove_file under agentic_core/ is blocked when fence is active."""
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        from agentic_core.L2_execution.tools import write_gateway

        monkeypatch.setattr(write_gateway, "_REPO_ROOT", tmp_path)

        target = tmp_path / "agentic_core" / "some_file.py"
        target.parent.mkdir(parents=True)
        target.write_text("x")

        with pytest.raises(RuntimeError, match="SOURCE_MUTATION_BLOCKED.*delete"):
            write_gateway.remove_file(target)

    def test_blocks_remove_tree_in_tests(self, monkeypatch, tmp_path):
        """remove_tree under tests/ is blocked when fence is active."""
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        from agentic_core.L2_execution.tools import write_gateway

        monkeypatch.setattr(write_gateway, "_REPO_ROOT", tmp_path)

        target = tmp_path / "tests" / "subdir"
        target.mkdir(parents=True)

        with pytest.raises(RuntimeError, match="SOURCE_MUTATION_BLOCKED.*delete"):
            write_gateway.remove_tree(target)

    def test_blocks_touch_in_ops_scripts(self, monkeypatch, tmp_path):
        """touch_file under ops_scripts/ is blocked when fence is active."""
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        from agentic_core.L2_execution.tools import write_gateway

        monkeypatch.setattr(write_gateway, "_REPO_ROOT", tmp_path)

        target = tmp_path / "ops_scripts" / "new.py"
        target.parent.mkdir(parents=True)

        with pytest.raises(RuntimeError, match="SOURCE_MUTATION_BLOCKED.*touch"):
            write_gateway.touch_file(target)

    def test_blocks_copy_tree_into_prompt_governance(self, monkeypatch, tmp_path):
        """copy_tree into prompt_governance/ is blocked when fence is active."""
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        from agentic_core.L2_execution.tools import write_gateway

        monkeypatch.setattr(write_gateway, "_REPO_ROOT", tmp_path)

        src = tmp_path / "safe_src"
        src.mkdir()
        (src / "a.txt").write_text("a")

        dst = tmp_path / "prompt_governance" / "copied"

        with pytest.raises(RuntimeError, match="SOURCE_MUTATION_BLOCKED.*copy"):
            write_gateway.copy_tree(src, dst)

    def test_blocks_write_json_atomic_in_apps_shared(self, monkeypatch, tmp_path):
        """write_json_atomic into apps_shared/ is blocked when fence is active."""
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        from agentic_core.L2_execution.tools import write_gateway

        monkeypatch.setattr(write_gateway, "_REPO_ROOT", tmp_path)

        target = tmp_path / "apps_shared" / "data.json"
        target.parent.mkdir(parents=True)

        with pytest.raises(RuntimeError, match="SOURCE_MUTATION_BLOCKED.*write"):
            write_gateway.write_json_atomic(target, {"key": "val"})

    def test_verb_appears_in_error_message(self, monkeypatch, tmp_path):
        """The verb (move/copy/delete/etc.) appears in the RuntimeError message."""
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        from agentic_core.L2_execution.tools import write_gateway

        monkeypatch.setattr(write_gateway, "_REPO_ROOT", tmp_path)

        src = tmp_path / "temp.txt"
        src.write_text("x")
        dst = tmp_path / "agentic_core" / "moved.py"
        dst.parent.mkdir(parents=True)

        with pytest.raises(RuntimeError, match="move"):
            write_gateway.move_path(src, dst)

    def test_allows_runtime_state_json(self, monkeypatch, tmp_path):
        """runtime_state.json at repo root is allowed."""
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        from agentic_core.L2_execution.tools import write_gateway

        monkeypatch.setattr(write_gateway, "_REPO_ROOT", tmp_path)

        target = tmp_path / "runtime_state.json"
        result = write_gateway.write_text(target, '{"ok": true}')
        assert Path(result).exists()
