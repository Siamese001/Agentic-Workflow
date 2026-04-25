"""Tests for mutation_prohibition.py module."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import timezone

import pytest

from agentic_core.L0_routing.enforcement.mutation_prohibition import (
    FORBIDDEN_WRITE_LAYERS,
    SourceMutationBlocked,
    ProtectedRootBlockEvent,
    ProtectedRootPolicy,
    get_default_protected_root_policy,
    enforce_protected_root,
    assert_no_persistent_write,
    safe_write_text,
    safe_write_bytes,
    safe_json_dump,
    safe_shutil_move,
    safe_shutil_rmtree,
    safe_os_remove,
    safe_os_rename,
    safe_open_write,
    mutation_guard,
)


class TestConstants:
    """Tests for module constants."""

    def test_forbidden_write_layers(self):
        """Test FORBIDDEN_WRITE_LAYERS contains expected layers."""
        assert FORBIDDEN_WRITE_LAYERS == frozenset({"L0", "L4", "L6"})


class TestSourceMutationBlocked:
    """Tests for SourceMutationBlocked exception."""

    def test_source_mutation_blocked_creation(self):
        """Test SourceMutationBlocked can be raised and caught."""
        with pytest.raises(SourceMutationBlocked) as exc_info:
            raise SourceMutationBlocked("Test block")
        
        assert "Test block" in str(exc_info.value)


class TestProtectedRootBlockEvent:
    """Tests for ProtectedRootBlockEvent dataclass."""

    def test_protected_root_block_event_creation(self):
        """Test ProtectedRootBlockEvent dataclass initialization."""
        event = ProtectedRootBlockEvent(
            ts_utc="2024-01-01T00:00:00Z",
            target="/path/to/file",
            matched_root="agentic_core",
            caller="module:function",
        )
        
        assert event.ts_utc == "2024-01-01T00:00:00Z"
        assert event.target == "/path/to/file"
        assert event.matched_root == "agentic_core"
        assert event.caller == "module:function"


class TestProtectedRootPolicy:
    """Tests for ProtectedRootPolicy dataclass."""

    def test_protected_root_policy_creation(self):
        """Test ProtectedRootPolicy dataclass initialization."""
        policy = ProtectedRootPolicy(
            immutable_roots=("agentic_core", "tests"),
            log_path="logs/blocks.jsonl",
        )
        
        assert policy.immutable_roots == ("agentic_core", "tests")
        assert policy.log_path == "logs/blocks.jsonl"


class TestGetDefaultProtectedRootPolicy:
    """Tests for get_default_protected_root_policy function."""

    def test_get_default_protected_root_policy(self):
        """Test get_default_protected_root_policy returns expected policy."""
        policy = get_default_protected_root_policy()
        
        assert isinstance(policy, ProtectedRootPolicy)
        assert "agentic_core" in policy.immutable_roots
        assert "tests" in policy.immutable_roots
        assert ".github" in policy.immutable_roots
        assert policy.log_path == "logs/ssot_protected_root_blocks.jsonl"


class TestEnforceProtectedRoot:
    """Tests for enforce_protected_root function."""

    def test_enforce_protected_root_allowed_override(self):
        """Test enforce_protected_root allows writes when override is True."""
        from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
        
        # Should not raise when allow_override=True
        enforce_protected_root(
            Path(AGENTIC_CORE_DIR) / "test.py",
            allow_override=True,
        )

    def test_enforce_protected_root_blocked_no_override(self):
        """Test enforce_protected_root blocks writes to protected roots."""
        from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
        
        with pytest.raises(SourceMutationBlocked) as exc_info:
            enforce_protected_root(
                Path(AGENTIC_CORE_DIR) / "test.py",
                allow_override=False,
            )
        
        assert "Protected root mutation blocked" in str(exc_info.value)

    def test_enforce_protected_root_custom_policy(self):
        """Test enforce_protected_root with custom policy."""
        custom_policy = ProtectedRootPolicy(
            immutable_roots=("custom_root",),
            log_path="logs/custom.jsonl",
        )
        
        # Non-protected path should not raise
        from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
        enforce_protected_root(
            Path(AGENTIC_CORE_DIR) / "test.py",
            allow_override=False,
            policy=custom_policy,
        )

    def test_enforce_protected_root_unprotected_path(self):
        """Test enforce_protected_root allows writes to unprotected paths."""
        from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
        
        # Path outside protected roots should not raise
        enforce_protected_root(
            Path(AGENTIC_CORE_DIR).parent.parent / "outside.py",
            allow_override=False,
        )


class TestAssertNoPersistentWrite:
    """Tests for assert_no_persistent_write function."""

    def test_assert_no_persistent_write_allowed_layer(self):
        """Test assert_no_persistent_write allows non-forbidden layers."""
        # L1 is not in FORBIDDEN_WRITE_LAYERS
        assert_no_persistent_write("L1", "write_text", "/path/to/file")

    def test_assert_no_persistent_write_forbidden_layer(self):
        """Test assert_no_persistent_write blocks forbidden layers."""
        with pytest.raises(PermissionError) as exc_info:
            assert_no_persistent_write("L0", "write_text", "/path/to/file")
        
        assert "MUTATION_PROHIBITED" in str(exc_info.value)
        assert "layer=L0" in str(exc_info.value)

    def test_assert_no_persistent_write_with_override(self):
        """Test assert_no_persistent_write allows override when env var set."""
        with patch.dict(os.environ, {"AGENTIC_ALLOW_MUTATION_FOR_TESTS": "1"}):
            # Should not raise when override is active
            assert_no_persistent_write("L0", "write_text", "/path/to/file")

    def test_assert_no_persistent_write_with_trace_id(self):
        """Test assert_no_persistent_write includes trace_id in error."""
        with pytest.raises(PermissionError) as exc_info:
            assert_no_persistent_write(
                "L0",
                "write_text",
                "/path/to/file",
                trace_id="trace123",
            )
        
        assert "trace_id=trace123" in str(exc_info.value)


class TestSafeWriteText:
    """Tests for safe_write_text function."""

    def test_safe_write_text_forbidden_layer(self):
        """Test safe_write_text blocks writes from forbidden layers."""
        with pytest.raises(PermissionError):
            safe_write_text("/tmp/test.txt", "content", layer="L0")

    def test_safe_write_text_allowed_layer(self, tmp_path):
        """Test safe_write_text allows writes from allowed layers."""
        test_file = tmp_path / "test.txt"
        safe_write_text(test_file, "content", layer="L1")
        
        assert test_file.read_text() == "content"

    def test_safe_write_text_with_trace_id(self):
        """Test safe_write_text includes trace_id in error."""
        with pytest.raises(PermissionError) as exc_info:
            safe_write_text("/tmp/test.txt", "content", layer="L0", trace_id="trace123")
        
        assert "trace_id=trace123" in str(exc_info.value)


class TestSafeWriteBytes:
    """Tests for safe_write_bytes function."""

    def test_safe_write_bytes_forbidden_layer(self):
        """Test safe_write_bytes blocks writes from forbidden layers."""
        with pytest.raises(PermissionError):
            safe_write_bytes("/tmp/test.bin", b"data", layer="L0")

    def test_safe_write_bytes_allowed_layer(self, tmp_path):
        """Test safe_write_bytes allows writes from allowed layers."""
        test_file = tmp_path / "test.bin"
        safe_write_bytes(test_file, b"data", layer="L1")
        
        assert test_file.read_bytes() == b"data"


class TestSafeJsonDump:
    """Tests for safe_json_dump function."""

    def test_safe_json_dump_forbidden_layer(self):
        """Test safe_json_dump blocks writes from forbidden layers."""
        with pytest.raises(PermissionError):
            safe_json_dump({"key": "value"}, "/tmp/test.json", layer="L0")

    def test_safe_json_dump_allowed_layer(self, tmp_path):
        """Test safe_json_dump allows writes from allowed layers."""
        test_file = tmp_path / "test.json"
        safe_json_dump({"key": "value"}, test_file, layer="L1")
        
        assert json.loads(test_file.read_text()) == {"key": "value"}

    def test_safe_json_dump_with_indent(self, tmp_path):
        """Test safe_json_dump with custom indent."""
        test_file = tmp_path / "test.json"
        safe_json_dump({"key": "value"}, test_file, layer="L1", indent=4)
        
        content = test_file.read_text()
        assert "    " in content  # 4-space indent


class TestSafeShutilMove:
    """Tests for safe_shutil_move function."""

    def test_safe_shutil_move_forbidden_layer(self, tmp_path):
        """Test safe_shutil_move blocks moves from forbidden layers."""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("content")
        
        with pytest.raises(PermissionError):
            safe_shutil_move(src, dst, layer="L0")

    def test_safe_shutil_move_allowed_layer(self, tmp_path):
        """Test safe_shutil_move allows moves from allowed layers."""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("content")
        
        safe_shutil_move(src, dst, layer="L1")
        
        assert dst.read_text() == "content"


class TestSafeShutilRmtree:
    """Tests for safe_shutil_rmtree function."""

    def test_safe_shutil_rmtree_forbidden_layer(self, tmp_path):
        """Test safe_shutil_rmtree blocks removal from forbidden layers."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        
        with pytest.raises(PermissionError):
            safe_shutil_rmtree(test_dir, layer="L0")

    def test_safe_shutil_rmtree_allowed_layer(self, tmp_path):
        """Test safe_shutil_rmtree allows removal from allowed layers."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        
        safe_shutil_rmtree(test_dir, layer="L1")
        
        assert not test_dir.exists()


class TestSafeOsRemove:
    """Tests for safe_os_remove function."""

    def test_safe_os_remove_forbidden_layer(self, tmp_path):
        """Test safe_os_remove blocks removal from forbidden layers."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        with pytest.raises(PermissionError):
            safe_os_remove(test_file, layer="L0")

    def test_safe_os_remove_allowed_layer(self, tmp_path):
        """Test safe_os_remove allows removal from allowed layers."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        safe_os_remove(test_file, layer="L1")
        
        assert not test_file.exists()


class TestSafeOsRename:
    """Tests for safe_os_rename function."""

    def test_safe_os_rename_forbidden_layer(self, tmp_path):
        """Test safe_os_rename blocks rename from forbidden layers."""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("content")
        
        with pytest.raises(PermissionError):
            safe_os_rename(src, dst, layer="L0")

    def test_safe_os_rename_allowed_layer(self, tmp_path):
        """Test safe_os_rename allows rename from allowed layers."""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("content")
        
        safe_os_rename(src, dst, layer="L1")
        
        assert dst.read_text() == "content"


class TestSafeOpenWrite:
    """Tests for safe_open_write function."""

    def test_safe_open_write_forbidden_layer(self):
        """Test safe_open_write blocks writes from forbidden layers."""
        with pytest.raises(PermissionError):
            safe_open_write("/tmp/test.txt", "w", layer="L0")

    def test_safe_open_write_allowed_layer(self, tmp_path):
        """Test safe_open_write allows writes from allowed layers."""
        test_file = tmp_path / "test.txt"
        
        with safe_open_write(test_file, "w", layer="L1") as f:
            f.write("content")
        
        assert test_file.read_text() == "content"

    def test_safe_open_write_append_mode(self, tmp_path):
        """Test safe_open_write with append mode."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("existing")
        
        with safe_open_write(test_file, "a", layer="L1") as f:
            f.write(" more")
        
        assert test_file.read_text() == "existing more"


class TestMutationGuard:
    """Tests for mutation_guard context manager."""

    def test_mutation_guard_forbidden_layer(self):
        """Test mutation_guard blocks entry for forbidden layers."""
        with pytest.raises(PermissionError):
            with mutation_guard("L0"):
                pass

    def test_mutation_guard_allowed_layer(self):
        """Test mutation_guard allows entry for allowed layers."""
        # Should not raise
        with mutation_guard("L1"):
            pass

    def test_mutation_guard_execution(self, tmp_path):
        """Test mutation_guard allows execution after guard check."""
        test_file = tmp_path / "test.txt"
        
        with mutation_guard("L1"):
            test_file.write_text("content")
        
        assert test_file.read_text() == "content"
