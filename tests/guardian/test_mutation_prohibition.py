"""G-12-1 — Mutation Prohibition Tests.

Negative tests proving FAIL-CLOSED behavior for L0/L4/L6 persistent writes.
Structural test verifying all write sites in L0/L4/L6 are guarded inline.
"""

from __future__ import annotations

import os
import pathlib
import re

import pytest

from agentic_core.L5_safety.enforcement.mutation_prohibition import (
    FORBIDDEN_WRITE_LAYERS,
    assert_no_persistent_write,
    safe_json_dump,
    safe_os_remove,
    safe_shutil_move,
    safe_write_text,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def _clear_override():
    """Ensure env override is NOT set by default."""
    old = os.environ.pop("AGENTIC_ALLOW_MUTATION_FOR_TESTS", None)
    yield
    if old is not None:
        os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = old
    else:
        os.environ.pop("AGENTIC_ALLOW_MUTATION_FOR_TESTS", None)


# =============================================================================
# NEGATIVE: L0 mutation attempt raises
# =============================================================================


class TestL0MutationBlocked:
    def test_write_text_raises(self, tmp_path):
        target = tmp_path / "test.txt"
        with pytest.raises(PermissionError, match="MUTATION_PROHIBITED.*layer=L0.*write_text"):
            safe_write_text(target, "content", layer="L0")

    def test_json_dump_raises(self, tmp_path):
        target = tmp_path / "test.json"
        with pytest.raises(PermissionError, match="MUTATION_PROHIBITED.*layer=L0.*json.dump"):
            safe_json_dump({"key": "val"}, target, layer="L0")

    def test_assert_raises(self):
        with pytest.raises(PermissionError, match="MUTATION_PROHIBITED.*layer=L0"):
            assert_no_persistent_write("L0", "write_text", "/some/path")

    def test_file_not_created(self, tmp_path):
        target = tmp_path / "should_not_exist.txt"
        try:
            safe_write_text(target, "content", layer="L0")
        except PermissionError:
            pass
        assert not target.exists()


# =============================================================================
# NEGATIVE: L4 mutation attempt raises
# =============================================================================


class TestL4MutationBlocked:
    def test_write_text_raises(self, tmp_path):
        target = tmp_path / "test.txt"
        with pytest.raises(PermissionError, match="MUTATION_PROHIBITED.*layer=L4"):
            safe_write_text(target, "content", layer="L4")

    def test_json_dump_raises(self, tmp_path):
        target = tmp_path / "test.json"
        with pytest.raises(PermissionError, match="MUTATION_PROHIBITED.*layer=L4"):
            safe_json_dump({"key": "val"}, target, layer="L4")

    def test_os_remove_raises(self, tmp_path):
        target = tmp_path / "test.txt"
        target.write_text("data")
        with pytest.raises(PermissionError, match="MUTATION_PROHIBITED.*layer=L4"):
            safe_os_remove(target, layer="L4")
        assert target.exists()


# =============================================================================
# NEGATIVE: L6 mutation attempt raises
# =============================================================================


class TestL6MutationBlocked:
    def test_write_text_raises(self, tmp_path):
        target = tmp_path / "test.txt"
        with pytest.raises(PermissionError, match="MUTATION_PROHIBITED.*layer=L6"):
            safe_write_text(target, "content", layer="L6")

    def test_shutil_move_raises(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("data")
        dst = tmp_path / "dst.txt"
        with pytest.raises(PermissionError, match="MUTATION_PROHIBITED.*layer=L6"):
            safe_shutil_move(src, dst, layer="L6")
        assert src.exists()
        assert not dst.exists()


# =============================================================================
# POSITIVE: L2 writes are permitted
# =============================================================================


class TestL2WritesPermitted:
    def test_write_text_allowed(self, tmp_path):
        target = tmp_path / "l2_ok.txt"
        safe_write_text(target, "L2 content", layer="L2")
        assert target.read_text() == "L2 content"

    def test_json_dump_allowed(self, tmp_path):
        import json

        target = tmp_path / "l2_ok.json"
        safe_json_dump({"ok": True}, target, layer="L2")
        assert json.loads(target.read_text()) == {"ok": True}

    def test_assert_passes_for_l2(self):
        assert_no_persistent_write("L2", "write_text", "/some/path")

    def test_assert_passes_for_l3(self):
        assert_no_persistent_write("L3", "write_text", "/some/path")


# =============================================================================
# ENV VAR OVERRIDE: test-only bypass
# =============================================================================


class TestEnvVarOverride:
    def test_override_allows_l0_write(self, tmp_path):
        os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = "1"
        target = tmp_path / "override_ok.txt"
        safe_write_text(target, "override content", layer="L0")
        assert target.read_text() == "override content"

    def test_default_is_fail_closed(self):
        """Prove that without the env var, guard blocks."""
        assert os.environ.get("AGENTIC_ALLOW_MUTATION_FOR_TESTS") != "1"
        with pytest.raises(PermissionError):
            assert_no_persistent_write("L0", "test_op")

    def test_wrong_value_does_not_override(self):
        os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = "yes"
        with pytest.raises(PermissionError):
            assert_no_persistent_write("L0", "test_op")


# =============================================================================
# DETERMINISTIC ERROR MESSAGE
# =============================================================================


class TestDeterministicMessage:
    def test_message_contains_layer(self):
        try:
            assert_no_persistent_write("L0", "write_text", "/foo/bar", "trace-123")
        except PermissionError as e:
            msg = str(e)
            assert "layer=L0" in msg
            assert "op=write_text" in msg
            assert "path=/foo/bar" in msg
            assert "trace_id=trace-123" in msg

    def test_message_without_optional_fields(self):
        try:
            assert_no_persistent_write("L4", "json.dump")
        except PermissionError as e:
            msg = str(e)
            assert "layer=L4" in msg
            assert "op=json.dump" in msg
            assert "path=" not in msg
            assert "trace_id=" not in msg


# =============================================================================
# STRUCTURAL: Single module + all writes guarded
# =============================================================================


class TestStructural:
    def test_single_mutation_prohibition_module(self):
        """Ensure only one mutation_prohibition module exists."""
        matches = list(pathlib.Path("agentic_core").rglob("mutation_prohibition.py"))
        assert len(matches) == 1, f"Expected 1 module, found {len(matches)}: {matches}"
        assert "L5_safety" in str(matches[0])

    def test_all_l0_l4_l6_writes_guarded(self):
        """Scan L0/L4/L6 for write primitives and verify each is guarded inline."""
        roots = [
            "agentic_core/L0_routing",
            "agentic_core/L4_state",
            "agentic_core/L6_observability",
        ]
        pats = [
            r"\.write_text\(",
            r"\.write_bytes\(",
            r"json\.dump\(",
            r"os\.(rename|remove|unlink)\(",
            r"shutil\.(move|rmtree)\(",
        ]
        unguarded = []

        for root in roots:
            for p in pathlib.Path(root).rglob("*.py"):
                lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    for pat in pats:
                        if re.search(pat, line):
                            # Check if the previous line (or same line) has a guard
                            guarded = False
                            # Check up to 3 lines above for the guard
                            for offset in range(1, 4):
                                if i - offset >= 0:
                                    prev = lines[i - offset].strip()
                                    if "assert_no_persistent_write" in prev:
                                        guarded = True
                                        break
                                    # Stop searching if we hit a non-comment, non-blank line
                                    # that isn't the guard
                                    if prev and not prev.startswith("#"):
                                        break
                            if not guarded:
                                unguarded.append(f"{p}:{i + 1}: {line.strip()}")
                            break

        assert len(unguarded) == 0, f"Found {len(unguarded)} unguarded write primitives:\n" + "\n".join(
            unguarded[:20]
        )

    def test_forbidden_layers_complete(self):
        """Verify FORBIDDEN_WRITE_LAYERS contains exactly L0, L4, L6."""
        assert FORBIDDEN_WRITE_LAYERS == frozenset({"L0", "L4", "L6"})
