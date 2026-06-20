"""Behavioral tests for agentic_core.L0_routing.enforcement.mutation_prohibition.

Covers the runtime contract surfaces that existing smoke tests do not:
  - `assert_no_persistent_write` layer gating and env-var override
  - `enforce_protected_root` block / allow / event-emission paths
  - All `safe_*` write wrappers (fail closed vs execute-through)
  - `mutation_guard` context manager behavior
  - `_emit_block_event` JSONL structure

L0 is a ×2.0 criticality layer (adg-canonical-invariants.md §6). These tests
exist because Stage 1 of the risk-weighted gap report
(`ops_scripts/verification/report_risk_weighted_test_gaps.py`) ranked this
module #1 by gap score (fan-in=51). Existing tests in this directory are
`pytest.importorskip` smoke tests that exercise none of the module's
decision logic.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.unit


# --------------------------------------------------------------------------- #
# Module under test                                                           #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def mp():
    """Import the module under test (skip if L0 package cannot be imported)."""
    return pytest.importorskip("agentic_core.L0_routing.enforcement.mutation_prohibition")


@pytest.fixture(autouse=True)
def _scrub_override_env(monkeypatch):
    """Ensure AGENTIC_ALLOW_MUTATION_FOR_TESTS is unset unless a test opts in."""
    monkeypatch.delenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", raising=False)


# --------------------------------------------------------------------------- #
# Constants / public surface                                                  #
# --------------------------------------------------------------------------- #


class TestPublicSurface:
    def test_forbidden_layers_are_exactly_L0_L4_L6(self, mp):
        assert mp.FORBIDDEN_WRITE_LAYERS == frozenset({"L0", "L4", "L6"})

    def test_forbidden_layers_is_frozenset(self, mp):
        assert isinstance(mp.FORBIDDEN_WRITE_LAYERS, frozenset)

    def test_exports_include_all_safe_wrappers(self, mp):
        for name in (
            "assert_no_persistent_write",
            "mutation_guard",
            "safe_json_dump",
            "safe_open_write",
            "safe_os_remove",
            "safe_os_rename",
            "safe_shutil_move",
            "safe_shutil_rmtree",
            "safe_write_bytes",
            "safe_write_text",
        ):
            assert name in mp.__all__, f"missing export: {name}"


# --------------------------------------------------------------------------- #
# assert_no_persistent_write                                                  #
# --------------------------------------------------------------------------- #


class TestAssertNoPersistentWrite:
    @pytest.mark.parametrize("layer", ["L0", "L4", "L6"])
    def test_forbidden_layer_raises_permission_error(self, mp, layer):
        with pytest.raises(PermissionError) as exc_info:
            mp.assert_no_persistent_write(layer, "write_text", path="/tmp/x")
        assert f"layer={layer}" in str(exc_info.value)
        assert "op=write_text" in str(exc_info.value)

    @pytest.mark.parametrize("layer", ["L1", "L2", "L3", "L5", "L_APP", ""])
    def test_allowed_layer_passes_silently(self, mp, layer):
        # No exception for non-forbidden layers
        mp.assert_no_persistent_write(layer, "write_text", path="/tmp/x")

    def test_override_env_var_bypasses_check(self, mp, monkeypatch):
        monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")
        # Would raise without override
        mp.assert_no_persistent_write("L0", "write_text", path="/tmp/x")

    @pytest.mark.parametrize("val", ["0", "true", "yes", "", "TRUE"])
    def test_override_env_var_only_accepts_literal_1(self, mp, monkeypatch, val):
        monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", val)
        with pytest.raises(PermissionError):
            mp.assert_no_persistent_write("L0", "write_text")

    def test_message_format_includes_path_and_trace_id_when_given(self, mp):
        with pytest.raises(PermissionError) as exc_info:
            mp.assert_no_persistent_write("L4", "json.dump", path="/var/x.json", trace_id="trace-123")
        msg = str(exc_info.value)
        assert "path=/var/x.json" in msg
        assert "trace_id=trace-123" in msg
        assert msg.startswith("MUTATION_PROHIBITED:layer=L4")

    def test_message_omits_path_and_trace_id_when_absent(self, mp):
        with pytest.raises(PermissionError) as exc_info:
            mp.assert_no_persistent_write("L0", "mutation_guard_enter")
        msg = str(exc_info.value)
        assert "path=" not in msg
        assert "trace_id=" not in msg


# --------------------------------------------------------------------------- #
# safe_* wrappers — fail-closed vs execute-through                            #
# --------------------------------------------------------------------------- #


class TestSafeWrappersFailClosed:
    @pytest.mark.parametrize("layer", ["L0", "L4", "L6"])
    def test_safe_write_text_blocks_forbidden_layer(self, mp, layer, tmp_path):
        target = tmp_path / "x.txt"
        with pytest.raises(PermissionError):
            mp.safe_write_text(target, "hello", layer=layer)
        assert not target.exists(), "file must not be created on block"

    @pytest.mark.parametrize("layer", ["L0", "L4", "L6"])
    def test_safe_write_bytes_blocks_forbidden_layer(self, mp, layer, tmp_path):
        target = tmp_path / "x.bin"
        with pytest.raises(PermissionError):
            mp.safe_write_bytes(target, b"\x00\x01", layer=layer)
        assert not target.exists()

    @pytest.mark.parametrize("layer", ["L0", "L4", "L6"])
    def test_safe_json_dump_blocks_forbidden_layer(self, mp, layer, tmp_path):
        target = tmp_path / "x.json"
        with pytest.raises(PermissionError):
            mp.safe_json_dump({"k": "v"}, target, layer=layer)
        assert not target.exists()

    @pytest.mark.parametrize("layer", ["L0", "L4", "L6"])
    def test_safe_os_remove_blocks_forbidden_layer(self, mp, layer, tmp_path):
        target = tmp_path / "x.txt"
        target.write_text("data", encoding="utf-8")
        with pytest.raises(PermissionError):
            mp.safe_os_remove(target, layer=layer)
        assert target.exists(), "file must still exist after blocked remove"

    @pytest.mark.parametrize("layer", ["L0", "L4", "L6"])
    def test_safe_os_rename_blocks_forbidden_layer(self, mp, layer, tmp_path):
        src = tmp_path / "a.txt"
        dst = tmp_path / "b.txt"
        src.write_text("data", encoding="utf-8")
        with pytest.raises(PermissionError):
            mp.safe_os_rename(src, dst, layer=layer)
        assert src.exists() and not dst.exists()

    @pytest.mark.parametrize("layer", ["L0", "L4", "L6"])
    def test_safe_shutil_move_blocks_forbidden_layer(self, mp, layer, tmp_path):
        src = tmp_path / "a.txt"
        dst = tmp_path / "b.txt"
        src.write_text("data", encoding="utf-8")
        with pytest.raises(PermissionError):
            mp.safe_shutil_move(src, dst, layer=layer)
        assert src.exists() and not dst.exists()

    @pytest.mark.parametrize("layer", ["L0", "L4", "L6"])
    def test_safe_shutil_rmtree_blocks_forbidden_layer(self, mp, layer, tmp_path):
        target = tmp_path / "dir"
        target.mkdir()
        (target / "inner.txt").write_text("x", encoding="utf-8")
        with pytest.raises(PermissionError):
            mp.safe_shutil_rmtree(target, layer=layer)
        assert target.exists() and (target / "inner.txt").exists()

    @pytest.mark.parametrize("layer", ["L0", "L4", "L6"])
    def test_safe_open_write_blocks_forbidden_layer(self, mp, layer, tmp_path):
        target = tmp_path / "x.txt"
        with pytest.raises(PermissionError):
            mp.safe_open_write(target, "w", layer=layer)
        assert not target.exists()


class TestSafeWrappersExecuteThrough:
    def test_safe_write_text_writes_content_when_allowed(self, mp, tmp_path):
        target = tmp_path / "x.txt"
        mp.safe_write_text(target, "hello", layer="L2")
        assert target.read_text(encoding="utf-8") == "hello"

    def test_safe_write_bytes_writes_content_when_allowed(self, mp, tmp_path):
        target = tmp_path / "x.bin"
        mp.safe_write_bytes(target, b"\x01\x02", layer="L3")
        assert target.read_bytes() == b"\x01\x02"

    def test_safe_json_dump_writes_valid_json_when_allowed(self, mp, tmp_path):
        target = tmp_path / "x.json"
        mp.safe_json_dump({"b": 2, "a": 1}, target, layer="L2")
        loaded = json.loads(target.read_text(encoding="utf-8"))
        assert loaded == {"a": 1, "b": 2}

    def test_safe_os_remove_deletes_when_allowed(self, mp, tmp_path):
        target = tmp_path / "x.txt"
        target.write_text("data", encoding="utf-8")
        mp.safe_os_remove(target, layer="L2")
        assert not target.exists()

    def test_safe_os_rename_moves_when_allowed(self, mp, tmp_path):
        src = tmp_path / "a.txt"
        dst = tmp_path / "b.txt"
        src.write_text("data", encoding="utf-8")
        mp.safe_os_rename(src, dst, layer="L2")
        assert not src.exists()
        assert dst.read_text(encoding="utf-8") == "data"

    def test_safe_shutil_move_moves_when_allowed(self, mp, tmp_path):
        src = tmp_path / "a.txt"
        dst = tmp_path / "b.txt"
        src.write_text("data", encoding="utf-8")
        mp.safe_shutil_move(src, dst, layer="L2")
        assert not src.exists()
        assert dst.read_text(encoding="utf-8") == "data"

    def test_safe_shutil_rmtree_removes_when_allowed(self, mp, tmp_path):
        target = tmp_path / "dir"
        target.mkdir()
        (target / "inner.txt").write_text("x", encoding="utf-8")
        mp.safe_shutil_rmtree(target, layer="L2")
        assert not target.exists()

    def test_safe_open_write_returns_writable_handle_when_allowed(self, mp, tmp_path):
        target = tmp_path / "x.txt"
        handle = mp.safe_open_write(target, "w", layer="L2")
        try:
            handle.write("hello")
        finally:
            handle.close()
        assert target.read_text(encoding="utf-8") == "hello"

    def test_override_env_lets_forbidden_layer_write(self, mp, monkeypatch, tmp_path):
        monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")
        target = tmp_path / "x.txt"
        mp.safe_write_text(target, "override-ok", layer="L0")
        assert target.read_text(encoding="utf-8") == "override-ok"


# --------------------------------------------------------------------------- #
# mutation_guard context manager                                              #
# --------------------------------------------------------------------------- #


class TestMutationGuardContextManager:
    @pytest.mark.parametrize("layer", ["L0", "L4", "L6"])
    def test_forbidden_layer_raises_on_enter(self, mp, layer):
        with pytest.raises(PermissionError):
            with mp.mutation_guard(layer):
                pass

    @pytest.mark.parametrize("layer", ["L1", "L2", "L3", "L5"])
    def test_allowed_layer_yields_cleanly(self, mp, layer):
        sentinel = []
        with mp.mutation_guard(layer):
            sentinel.append(1)
        assert sentinel == [1]

    def test_override_bypasses_guard_on_forbidden_layer(self, mp, monkeypatch):
        monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")
        sentinel = []
        with mp.mutation_guard("L0"):
            sentinel.append(1)
        assert sentinel == [1]


# --------------------------------------------------------------------------- #
# Protected-root enforcement                                                  #
# --------------------------------------------------------------------------- #


class TestEnforceProtectedRoot:
    def test_allow_override_short_circuits(self, mp, tmp_path):
        # Even a nominally protected target is allowed under override
        target = Path(mp._get_repo_root()) / "agentic_core" / "fake.py"
        mp.enforce_protected_root(target, allow_override=True)  # must not raise

    def test_path_outside_protected_roots_passes(self, mp, tmp_path):
        target = tmp_path / "somewhere_outside.txt"
        mp.enforce_protected_root(target, allow_override=False)  # must not raise

    def test_path_under_protected_root_raises(self, mp, tmp_path):
        policy = mp.ProtectedRootPolicy(
            immutable_roots=(tmp_path.name,),
            log_path=str(tmp_path / "block_log.jsonl"),
        )
        # Place tmp_path under repo_root namespace via monkeypatching _get_repo_root
        with patch.object(mp, "_get_repo_root", return_value=tmp_path.parent):
            target = tmp_path / "child.txt"
            with pytest.raises(mp.SourceMutationBlocked) as exc_info:
                mp.enforce_protected_root(target, allow_override=False, policy=policy)
            assert "Protected root mutation blocked" in str(exc_info.value)
            assert tmp_path.name in str(exc_info.value)

    def test_block_emits_jsonl_event(self, mp, tmp_path):
        log_file = tmp_path / "blocks.jsonl"
        policy = mp.ProtectedRootPolicy(
            immutable_roots=(tmp_path.name,),
            log_path="blocks.jsonl",
        )
        with patch.object(mp, "_get_repo_root", return_value=tmp_path.parent):
            with pytest.raises(mp.SourceMutationBlocked):
                mp.enforce_protected_root(
                    tmp_path / "nested" / "file.txt",
                    allow_override=False,
                    policy=policy,
                )
        # Event should land in <repo_root>/<policy.log_path>
        emitted = tmp_path.parent / "blocks.jsonl"
        assert emitted.exists(), "block event log must exist"
        lines = [ln for ln in emitted.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert set(record.keys()) == {"ts_utc", "target", "matched_root", "caller"}
        assert record["matched_root"] == tmp_path.name
        assert record["caller"] == "mutation_prohibition:enforce_protected_root"


class TestDefaultProtectedRootPolicy:
    def test_returns_policy_with_expected_roots(self, mp):
        policy = mp.get_default_protected_root_policy()
        assert isinstance(policy, mp.ProtectedRootPolicy)
        # Must include the canonical immutable roots
        assert ".github" in policy.immutable_roots
        assert ".codex/rules" in policy.immutable_roots
        # log_path is a string (JSONL destination)
        assert isinstance(policy.log_path, str) and policy.log_path

    def test_is_pure_returns_equal_values(self, mp):
        a = mp.get_default_protected_root_policy()
        b = mp.get_default_protected_root_policy()
        assert a.immutable_roots == b.immutable_roots
        assert a.log_path == b.log_path


# --------------------------------------------------------------------------- #
# _emit_block_event internals                                                 #
# --------------------------------------------------------------------------- #


class TestEmitBlockEvent:
    def test_writes_deterministic_jsonl_line(self, mp, tmp_path):
        log_rel = "custom/block.jsonl"
        with patch.object(mp, "_get_repo_root", return_value=tmp_path):
            mp._emit_block_event(
                target=Path("/some/blocked/path.txt"),
                matched_root="agentic_core",
                log_path=log_rel,
                ts_utc_override="2026-01-01T00:00:00+00:00",
            )
        emitted = tmp_path / log_rel
        assert emitted.exists()
        line = emitted.read_text(encoding="utf-8").splitlines()[0]
        record = json.loads(line)
        assert record == {
            "ts_utc": "2026-01-01T00:00:00+00:00",
            "target": str(Path("/some/blocked/path.txt")),
            "matched_root": "agentic_core",
            "caller": "mutation_prohibition:enforce_protected_root",
        }

    def test_append_mode_accumulates_events(self, mp, tmp_path):
        log_rel = "custom/block.jsonl"
        with patch.object(mp, "_get_repo_root", return_value=tmp_path):
            for i in range(3):
                mp._emit_block_event(
                    target=Path(f"/x/{i}.txt"),
                    matched_root="tests",
                    log_path=log_rel,
                    ts_utc_override=f"2026-01-01T00:00:0{i}+00:00",
                )
        emitted = tmp_path / log_rel
        lines = [ln for ln in emitted.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(lines) == 3
        # Each line parses as JSON
        for ln in lines:
            json.loads(ln)


# --------------------------------------------------------------------------- #
# _is_override_active                                                         #
# --------------------------------------------------------------------------- #


class TestOverrideFlag:
    def test_unset_env_var_means_inactive(self, mp, monkeypatch):
        monkeypatch.delenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", raising=False)
        assert mp._is_override_active() is False

    def test_literal_1_means_active(self, mp, monkeypatch):
        monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")
        assert mp._is_override_active() is True

    @pytest.mark.parametrize("val", ["", "0", "true", "yes", "2", "TRUE"])
    def test_other_values_mean_inactive(self, mp, monkeypatch, val):
        monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", val)
        assert mp._is_override_active() is False
