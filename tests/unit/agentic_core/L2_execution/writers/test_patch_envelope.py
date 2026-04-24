"""Tests for ADR-048 apply-patch envelope (W14.b parser/validator + W14.c executor).

Coverage requirement (ADR-048): ≥10 tests covering parser happy path, validator
gates (size limits, anchor drift, path traversal, Agent.py deletion), executor
atomicity (mid-batch rollback), and idempotency.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L2_execution.writers import (
    AddFile,
    DeleteFile,
    Envelope,
    EnvelopeError,
    UpdateFile,
    apply_envelope,
    parse_envelope,
    validate_envelope,
)


# ---------------------------------------------------------------------------
# Fixtures.
# ---------------------------------------------------------------------------


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """Working tree with a couple of seed files."""
    (tmp_path / "foo.py").write_text(
        "def existing():\n    return 1\n",
        encoding="utf-8",
    )
    (tmp_path / "bar.py").write_text(
        "def bar():\n    return 'bar'\n",
        encoding="utf-8",
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Parser tests (W14.b).
# ---------------------------------------------------------------------------


def test_parse_happy_path_update_add_delete():
    text = (
        "*** Begin Patch\n"
        "*** Update File: foo.py\n"
        "@@ def existing():\n"
        " def existing():\n"
        "-    return 1\n"
        "+    return 2\n"
        "*** Add File: new.py\n"
        "+print('hi')\n"
        "*** Delete File: bar.py\n"
        "*** End Patch\n"
    )
    env = parse_envelope(text)
    assert env.file_count == 3
    assert env.hunk_count == 1
    kinds = [op.op_kind for op in env.operations]
    assert kinds == ["update", "add", "delete"]


def test_parse_missing_begin_marker_raises():
    text = "*** Update File: foo.py\n@@ x\n+y\n*** End Patch\n"
    with pytest.raises(EnvelopeError, match="Begin Patch"):
        parse_envelope(text)


def test_parse_missing_end_marker_raises():
    text = "*** Begin Patch\n*** Update File: foo.py\n@@ x\n+y\n"
    with pytest.raises(EnvelopeError, match="End Patch"):
        parse_envelope(text)


def test_parse_update_with_no_hunks_raises():
    text = "*** Begin Patch\n*** Update File: foo.py\n*** End Patch\n"
    with pytest.raises(EnvelopeError, match="no hunks"):
        parse_envelope(text)


def test_parse_preserves_agent_deletion_marker():
    text = (
        "*** Begin Patch\n"
        "*** AGENT-DELETION-AUTHORIZED: 2026-01-01\n"
        "*** Delete File: agentic_core/L5_safety/reasoning/FooAgent.py\n"
        "*** End Patch\n"
    )
    env = parse_envelope(text)
    assert len(env.preamble_markers) == 1
    assert env.preamble_markers[0].endswith("2026-01-01")


# ---------------------------------------------------------------------------
# Validator tests (W14.b).
# ---------------------------------------------------------------------------


def test_validate_happy_path_returns_no_errors(tree: Path):
    env = Envelope(
        operations=(
            AddFile(path="new.py", content="print('hi')\n"),
        ),
    )
    assert validate_envelope(env, tree) == []


def test_validate_size_limit_files(tree: Path):
    ops = tuple(
        AddFile(path=f"a{i}.py", content="x\n") for i in range(60)
    )
    env = Envelope(operations=ops)
    errors = validate_envelope(env, tree, max_files=50)
    codes = {e.code for e in errors}
    assert "ENVELOPE_TOO_LARGE_FILES" in codes


def test_validate_path_traversal_rejected(tree: Path):
    env = Envelope(operations=(AddFile(path="../escape.py", content="x"),))
    codes = {e.code for e in validate_envelope(env, tree)}
    assert "UNSAFE_PATH" in codes


def test_validate_absolute_path_rejected(tree: Path):
    env = Envelope(operations=(AddFile(path="/etc/passwd", content="x"),))
    codes = {e.code for e in validate_envelope(env, tree)}
    assert "UNSAFE_PATH" in codes


def test_validate_add_over_existing_rejected(tree: Path):
    env = Envelope(operations=(AddFile(path="foo.py", content="x"),))
    codes = {e.code for e in validate_envelope(env, tree)}
    assert "ADD_OVER_EXISTING" in codes


def test_validate_delete_missing_rejected(tree: Path):
    env = Envelope(operations=(DeleteFile(path="ghost.py"),))
    codes = {e.code for e in validate_envelope(env, tree)}
    assert "DELETE_MISSING" in codes


def test_validate_update_missing_rejected(tree: Path):
    from agentic_core.L2_execution.writers import Hunk

    env = Envelope(
        operations=(
            UpdateFile(
                path="ghost.py",
                hunks=(Hunk(anchor="x", lines=(" x",)),),
            ),
        ),
    )
    codes = {e.code for e in validate_envelope(env, tree)}
    assert "UPDATE_MISSING" in codes


def test_validate_anchor_mismatch_detected(tree: Path):
    """Per ADR-048 Q1, drifted anchors must abort the envelope."""
    from agentic_core.L2_execution.writers import Hunk

    env = Envelope(
        operations=(
            UpdateFile(
                path="foo.py",
                hunks=(
                    Hunk(
                        anchor="def nonexistent_function():",
                        lines=(" def nonexistent_function():",),
                    ),
                ),
            ),
        ),
    )
    codes = {e.code for e in validate_envelope(env, tree)}
    assert "ANCHOR_NOT_FOUND" in codes


def test_validate_agent_deletion_without_marker_rejected(tree: Path):
    """Per ADR-048 Q3, *Agent.py Delete File requires marker."""
    (tree / "FooAgent.py").write_text("class FooAgent: pass\n", encoding="utf-8")
    env = Envelope(operations=(DeleteFile(path="FooAgent.py"),))
    codes = {e.code for e in validate_envelope(env, tree)}
    assert "AGENT_DELETION_GATE" in codes


def test_validate_agent_deletion_with_marker_passes(tree: Path):
    (tree / "FooAgent.py").write_text("class FooAgent: pass\n", encoding="utf-8")
    env = Envelope(
        operations=(DeleteFile(path="FooAgent.py"),),
        preamble_markers=("*** AGENT-DELETION-AUTHORIZED: 2026-01-01",),
    )
    codes = {e.code for e in validate_envelope(env, tree)}
    assert "AGENT_DELETION_GATE" not in codes


# ---------------------------------------------------------------------------
# Executor tests (W14.c).
# ---------------------------------------------------------------------------


def test_apply_happy_path_update_add_delete(tree: Path):
    text = (
        "*** Begin Patch\n"
        "*** Update File: foo.py\n"
        "@@ def existing():\n"
        " def existing():\n"
        "-    return 1\n"
        "+    return 42\n"
        "*** Add File: new.py\n"
        "+print('hi')\n"
        "*** Delete File: bar.py\n"
        "*** End Patch\n"
    )
    env = parse_envelope(text)
    result = apply_envelope(env, tree)
    assert result.success, result.errors
    assert "return 42" in (tree / "foo.py").read_text(encoding="utf-8")
    assert (tree / "new.py").read_text(encoding="utf-8") == "print('hi')\n"
    assert not (tree / "bar.py").exists()


def test_apply_dry_run_makes_no_writes(tree: Path):
    before_foo = (tree / "foo.py").read_text(encoding="utf-8")
    env = parse_envelope(
        "*** Begin Patch\n"
        "*** Update File: foo.py\n"
        "@@ def existing():\n"
        " def existing():\n"
        "-    return 1\n"
        "+    return 99\n"
        "*** End Patch\n"
    )
    result = apply_envelope(env, tree, dry_run=True)
    assert result.success
    assert result.dry_run
    assert (tree / "foo.py").read_text(encoding="utf-8") == before_foo


def test_apply_validation_failure_writes_nothing(tree: Path):
    env = Envelope(
        operations=(
            AddFile(path="new.py", content="ok\n"),
            AddFile(path="../escape.py", content="bad\n"),
        ),
    )
    result = apply_envelope(env, tree)
    assert not result.success
    assert any(e.code == "UNSAFE_PATH" for e in result.errors)
    assert not (tree / "new.py").exists()


def test_apply_idempotent_replay_blocks_after_first_apply(tree: Path):
    """Replaying the same envelope after apply hits ADD_OVER_EXISTING."""
    env = parse_envelope(
        "*** Begin Patch\n*** Add File: new.py\n+x\n*** End Patch\n"
    )
    first = apply_envelope(env, tree)
    assert first.success
    second = apply_envelope(env, tree)
    assert not second.success
    assert any(e.code == "ADD_OVER_EXISTING" for e in second.errors)


def test_apply_mid_batch_failure_rolls_back(tree: Path, monkeypatch):
    """Force a failure mid-apply and assert all snapshots are restored."""
    original_foo = (tree / "foo.py").read_text(encoding="utf-8")

    # Validator-clean envelope: Update foo, Update bar.
    env = parse_envelope(
        "*** Begin Patch\n"
        "*** Update File: foo.py\n"
        "@@ def existing():\n"
        " def existing():\n"
        "-    return 1\n"
        "+    return 2\n"
        "*** Update File: bar.py\n"
        "@@ def bar():\n"
        " def bar():\n"
        "-    return 'bar'\n"
        "+    return 'BAR'\n"
        "*** End Patch\n"
    )

    # Patch write_gateway.write_text to fail on the SECOND call (bar.py).
    from agentic_core.L2_execution.utils import write_gateway as wg

    call_count = {"n": 0}
    real_write_text = wg.write_text

    def flaky_write_text(path, content, *args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 2:
            raise OSError("simulated mid-batch failure")
        return real_write_text(path, content, *args, **kwargs)

    monkeypatch.setattr(wg, "write_text", flaky_write_text)

    result = apply_envelope(env, tree)
    assert not result.success
    # foo.py was written then must be restored.
    assert (tree / "foo.py").read_text(encoding="utf-8") == original_foo
    # bar.py never touched.
    assert "return 'bar'" in (tree / "bar.py").read_text(encoding="utf-8")
