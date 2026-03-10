"""Tests for SSOT Mutation Fence Hardening (Wave 2)."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    TESTS_DIR,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import (
    ProtectedRootPolicy,
    SourceMutationBlocked,
    enforce_protected_root,
    get_default_protected_root_policy,
)
from agentic_core.L2_execution.tools import write_gateway


@pytest.mark.unit_min_deps
class TestProtectedRootEnforcement:
    """Test protected-root enforcement primitives."""

    def test_enforce_protected_root_blocks_agentic_core(self):
        """Test that writes to agentic_core are blocked."""
        target_path = Path("agentic_core/test_file.py")
        with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
            enforce_protected_root(target_path, allow_override=False)

    def test_enforce_protected_root_allows_outside(self):
        """Test that writes outside protected roots are allowed."""
        target_path = Path("docs/evidence/test.md")
        # Should not raise
        enforce_protected_root(target_path, allow_override=False)
        assert True  # no-exception contract

    def test_enforce_protected_root_override_allows(self):
        """Test that override allows writes to protected roots."""
        target_path = Path("agentic_core/test_file.py")
        # Should not raise when override is enabled
        enforce_protected_root(target_path, allow_override=True)
        assert True  # no-exception contract

    def test_enforce_protected_root_blocks_tests(self):
        """Test that writes to tests directory are blocked (tests is a protected root)."""
        target_path = Path("tests/test_file.py")
        with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
            enforce_protected_root(target_path, allow_override=False)

    def test_enforce_protected_root_blocks_github(self):
        """Test that writes to .github directory are blocked."""
        target_path = Path(".github/workflows/test.yml")
        with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
            enforce_protected_root(target_path, allow_override=False)

    def test_exception_includes_matched_root_agentic_core(self):
        """Test that exception message includes the matched immutable root."""
        target_path = Path("agentic_core/test_file.py")
        with pytest.raises(SourceMutationBlocked, match="matched_root=agentic_core"):
            enforce_protected_root(target_path, allow_override=False)

    def test_exception_includes_matched_root_github(self):
        """Test that exception message includes matched root for .github directory."""
        target_path = Path(".github/workflows/test.yml")
        with pytest.raises(SourceMutationBlocked, match=r"matched_root=\.github"):
            enforce_protected_root(target_path, allow_override=False)


@pytest.mark.unit_min_deps
class TestWriteGatewayIntegration:
    """Test write gateway integration with protected-root enforcement."""

    @patch("pathlib.Path.write_text")
    def test_write_gateway_blocks_protected_root(self, mock_write):
        """Test that write_gateway blocks protected root writes."""
        target_path = Path("agentic_core/test_file.py")

        with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
            write_gateway.write_text(target_path, "test content")

        # Ensure no actual write occurred
        mock_write.assert_not_called()

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.read_bytes", return_value=b"test content")
    @patch("pathlib.Path.write_text")
    def test_write_gateway_allows_outside_protected_root(self, mock_write, mock_read, mock_mkdir):
        """Test that write_gateway allows writes outside protected roots."""
        target_path = Path("docs/evidence/test.md")

        # Should not raise
        write_gateway.write_text(target_path, "test content")

        # Verify write was attempted
        mock_write.assert_called_once_with("test content", encoding="utf-8")
        assert True  # no-exception contract

    @patch("pathlib.Path.write_bytes")
    def test_write_bytes_blocks_protected_root(self, mock_write):
        """Test that write_bytes blocks protected root writes."""
        target_path = Path("agentic_core/test_file.bin")

        with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
            write_gateway.write_bytes(target_path, b"test data")

        # Ensure no actual write occurred
        mock_write.assert_not_called()


@pytest.mark.unit_min_deps
class TestBlockEventEmission:
    """Test block event emission to JSONL log."""

    def test_block_emits_jsonl_event(self, tmp_path):
        """Test that a block attempt produces exactly one JSONL line with required fields."""
        target_path = Path("agentic_core/test_file.py")
        log_file = tmp_path / "blocks.jsonl"

        # Monkeypatch the log path
        with patch("agentic_core.L0_routing.enforcement.mutation_prohibition.Path") as mock_path_cls:
            # Make Path() constructor work normally for target_path
            mock_path_cls.side_effect = lambda x: (
                Path(x) if x != "logs/ssot_protected_root_blocks.jsonl" else log_file
            )

            # Also need to patch the open call to use our tmp_path
            original_open = open

            def patched_open(path, *args, **kwargs):
                if "logs/ssot_protected_root_blocks.jsonl" in str(path):
                    return original_open(log_file, *args, **kwargs)
                return original_open(path, *args, **kwargs)

            with patch("builtins.open", side_effect=patched_open):
                with pytest.raises(SourceMutationBlocked):
                    enforce_protected_root(target_path, allow_override=False)

        # Verify JSONL event was written
        assert log_file.exists()
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 1

        # Parse and verify event structure
        event = json.loads(lines[0])
        assert "ts_utc" in event
        assert "target" in event
        assert "matched_root" in event
        assert event["matched_root"] == AGENTIC_CORE_DIR
        assert "caller" in event
        assert event["caller"] == "mutation_prohibition:enforce_protected_root"

    def test_logging_failure_does_not_mask_exception(self):
        """Test that logging failures do not mask SourceMutationBlocked."""
        target_path = Path("agentic_core/test_file.py")

        # Monkeypatch open to raise an exception
        with patch("builtins.open", side_effect=PermissionError("Simulated logging failure")):
            # Should still raise SourceMutationBlocked, not PermissionError
            with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
                enforce_protected_root(target_path, allow_override=False)

    def test_exception_message_still_includes_diagnostics(self):
        """Test that exception message still includes target and matched_root after adding emission."""
        target_path = Path("agentic_core/test_file.py")

        with pytest.raises(SourceMutationBlocked) as exc_info:
            enforce_protected_root(target_path, allow_override=False)
        e = exc_info.value
        msg = str(e)
        assert "target=" in msg
        assert "matched_root=agentic_core" in msg


@pytest.mark.unit_min_deps
class TestPolicyContract:
    """Test protected-root policy contract and configurability."""

    def test_default_policy_immutable_roots(self):
        """Test that default policy has exactly the canonical immutable roots."""
        policy = get_default_protected_root_policy()
        assert policy.immutable_roots == (AGENTIC_CORE_DIR, TESTS_DIR, ".github", ".windsurfrules")

    def test_default_policy_log_path(self):
        """Test that default policy has the canonical log path."""
        policy = get_default_protected_root_policy()
        assert policy.log_path == "logs/ssot_protected_root_blocks.jsonl"

    def test_policy_override_log_path_writes_to_tmp(self, tmp_path):
        """Test that overriding policy.log_path writes JSONL to tmp_path (no writes to repo logs)."""
        target_path = Path("agentic_core/test_file.py")
        log_file = tmp_path / "test_blocks.jsonl"

        # Create custom policy with tmp_path log
        custom_policy = ProtectedRootPolicy(
            immutable_roots=(AGENTIC_CORE_DIR, TESTS_DIR, ".github"), log_path=str(log_file)
        )

        # Ensure tmp log doesn't exist before test
        assert not log_file.exists()

        # Attempt block with custom policy
        with pytest.raises(SourceMutationBlocked):
            enforce_protected_root(target_path, allow_override=False, policy=custom_policy)

        # Verify JSONL was written to tmp_path
        assert log_file.exists()

        # Verify event structure
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 1  # Exactly one event written
        event = json.loads(lines[0])
        assert event["matched_root"] == AGENTIC_CORE_DIR
        assert "target" in event
        assert "ts_utc" in event
        assert "caller" in event

    def test_policy_override_immutable_roots_changes_matched_root(self, tmp_path):
        """Test that changing policy.immutable_roots changes matched_root in exception and event."""
        target_path = Path("custom_protected/test_file.py")
        log_file = tmp_path / "test_blocks.jsonl"

        # Create custom policy with different immutable roots
        custom_policy = ProtectedRootPolicy(immutable_roots=("custom_protected",), log_path=str(log_file))

        # Attempt block with custom policy
        with pytest.raises(SourceMutationBlocked) as exc_info:
            enforce_protected_root(target_path, allow_override=False, policy=custom_policy)
        e = exc_info.value
        msg = str(e)
        assert "matched_root=custom_protected" in msg

        # Verify event has correct matched_root
        assert log_file.exists()
        lines = log_file.read_text().strip().split("\n")
        event = json.loads(lines[-1])
        assert event["matched_root"] == "custom_protected"

    def test_policy_none_uses_default(self):
        """Test that policy=None uses the default policy."""
        target_path = Path("agentic_core/test_file.py")

        # Should block with default policy
        with pytest.raises(SourceMutationBlocked, match="matched_root=agentic_core"):
            enforce_protected_root(target_path, allow_override=False, policy=None)


@pytest.mark.unit_min_deps
class TestEnvVarIsolation:
    """Test that env vars do not affect protected-root enforcement in SSOT path."""

    def test_env_allow_mutation_does_not_bypass_protected_root(self, monkeypatch):
        """Test that AGENTIC_ALLOW_MUTATION_FOR_TESTS does not bypass protected-root enforcement."""
        target_path = Path("agentic_core/test_file.py")

        # Set env var that should NOT affect protected-root behavior
        monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")

        # Should still block (env var should not affect protected-root enforcement)
        with pytest.raises(SourceMutationBlocked, match="matched_root=agentic_core"):
            enforce_protected_root(target_path, allow_override=False)

    def test_env_deny_mutation_does_not_change_protected_root(self, monkeypatch):
        """Test that AGENTIC_DENY_SOURCE_MUTATION does not change protected-root behavior."""
        target_path = Path("agentic_core/test_file.py")

        # Set env var that should NOT affect protected-root behavior
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        # Should still block (same behavior with or without env var)
        with pytest.raises(SourceMutationBlocked, match="matched_root=agentic_core"):
            enforce_protected_root(target_path, allow_override=False)

    def test_cli_override_works_regardless_of_env(self, monkeypatch):
        """Test that CLI override (allow_override=True) works regardless of env vars."""
        target_path = Path("agentic_core/test_file.py")

        # Set env vars that should NOT interfere
        monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "0")
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        # CLI override should allow bypass regardless of env vars
        enforce_protected_root(target_path, allow_override=True)  # Should not raise
        assert True  # no-exception contract

    def test_unset_env_vars_do_not_change_behavior(self, monkeypatch):
        """Test that unsetting env vars does not change protected-root behavior."""
        target_path = Path("agentic_core/test_file.py")

        # Ensure env vars are unset
        monkeypatch.delenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", raising=False)
        monkeypatch.delenv("AGENTIC_DENY_SOURCE_MUTATION", raising=False)

        # Should still block (default behavior)
        with pytest.raises(SourceMutationBlocked, match="matched_root=agentic_core"):
            enforce_protected_root(target_path, allow_override=False)


@pytest.mark.unit_min_deps
class TestFenceSelfCheck:
    """Test fence self-check mode validates policy + wiring."""

    def test_self_check_ok_path(self):
        """Test that self-check produces status ok JSON when all checks pass."""
        import json
        import subprocess

        result = subprocess.run(
            ["python", "-m", "agentic_core.L0_routing.scripts.execute_ssot_entrypoint", "--fence-self-check"],
            capture_output=True,
            text=True,
        )

        # Should exit 0
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}. stderr: {result.stderr}"

        # Should output valid JSON
        output = json.loads(result.stdout.strip())
        assert output["status"] == "ok"
        assert output["checks"] == 4

    def test_self_check_fails_with_bad_log_path(self, monkeypatch):
        """Test that self-check fails when log_path is under agentic_core."""
        from agentic_core.L0_routing.enforcement.mutation_prohibition import (
            ProtectedRootPolicy,
        )

        # Monkeypatch get_default_protected_root_policy to return bad log_path
        def bad_policy():
            return ProtectedRootPolicy(
                immutable_roots=(AGENTIC_CORE_DIR, TESTS_DIR, ".github"),
                log_path="agentic_core/bad_log.jsonl",  # Under protected root!
            )

        import agentic_core.L0_routing.scripts.execute_ssot as execute_ssot_module

        monkeypatch.setattr(
            "agentic_core.L0_routing.enforcement.mutation_prohibition.get_default_protected_root_policy",
            bad_policy,
        )

        # Run self-check
        with pytest.raises(SystemExit) as exc_info:
            execute_ssot_module.run_fence_self_check()

        # Should exit with nonzero
        assert exc_info.value.code != 0

    def test_self_check_validates_write_gateway_wiring(self):
        """Test that self-check validates write_gateway has enforce_protected_root calls."""
        import inspect

        from agentic_core.L2_execution.tools import write_gateway

        # Verify write_text has allow_override parameter
        sig = inspect.signature(write_gateway.write_text)
        assert "allow_override" in sig.parameters

        # Verify write_text source contains enforce_protected_root
        source = inspect.getsource(write_gateway.write_text)
        assert "enforce_protected_root" in source


@pytest.mark.unit_min_deps
class TestDeterministicReplay:
    """Test deterministic replay verification for protected-root fence behavior."""

    def test_replay_block_event_is_identical_under_fixed_clock(self, tmp_path, monkeypatch):
        """Test that blocked-write telemetry is identical across runs with fixed timestamp."""
        from agentic_core.L0_routing.enforcement.mutation_prohibition import (
            _emit_block_event,
        )

        target_path = Path("agentic_core/test_file.py").resolve()
        matched_root = AGENTIC_CORE_DIR
        fixed_ts = "2026-02-21T23:00:00+00:00"

        # Run 1: Emit event with fixed timestamp
        log_file_1 = tmp_path / "run1.jsonl"
        _emit_block_event(target_path, matched_root, str(log_file_1), ts_utc_override=fixed_ts)

        # Run 2: Emit event with same fixed timestamp
        log_file_2 = tmp_path / "run2.jsonl"
        _emit_block_event(target_path, matched_root, str(log_file_2), ts_utc_override=fixed_ts)

        # Verify JSONL lines are bitwise identical
        content_1 = log_file_1.read_text(encoding="utf-8")
        content_2 = log_file_2.read_text(encoding="utf-8")

        assert content_1 == content_2, "JSONL output should be identical under fixed clock"

        # Verify content is valid JSON with expected fields
        import json

        event = json.loads(content_1.strip())
        assert event["ts_utc"] == fixed_ts
        assert event["matched_root"] == matched_root
        assert "target" in event
        assert "caller" in event

    def test_self_check_output_is_bitwise_identical_across_runs(self):
        """Test that self-check JSON output is bitwise identical across multiple runs."""
        import json
        import subprocess

        # Run self-check twice
        result_1 = subprocess.run(
            ["python", "-m", "agentic_core.L0_routing.scripts.execute_ssot_entrypoint", "--fence-self-check"],
            capture_output=True,
            text=True,
        )

        result_2 = subprocess.run(
            ["python", "-m", "agentic_core.L0_routing.scripts.execute_ssot_entrypoint", "--fence-self-check"],
            capture_output=True,
            text=True,
        )

        # Both should succeed
        assert result_1.returncode == 0
        assert result_2.returncode == 0

        # Outputs should be bitwise identical
        assert result_1.stdout == result_2.stdout, "Self-check output should be deterministic"

        # Verify it's valid JSON
        output = json.loads(result_1.stdout.strip())
        assert output["status"] == "ok"
        assert output["checks"] == 4

    def test_block_event_without_override_uses_real_time(self, tmp_path):
        """Test that block events without override use real UTC time (not deterministic)."""
        import time

        from agentic_core.L0_routing.enforcement.mutation_prohibition import (
            _emit_block_event,
        )

        target_path = Path("agentic_core/test_file.py").resolve()
        matched_root = AGENTIC_CORE_DIR

        # Run 1
        log_file_1 = tmp_path / "run1.jsonl"
        _emit_block_event(target_path, matched_root, str(log_file_1))

        # Small delay to ensure different timestamp
        time.sleep(DEFAULT_SLEEP)

        # Run 2
        log_file_2 = tmp_path / "run2.jsonl"
        _emit_block_event(target_path, matched_root, str(log_file_2))

        # Verify timestamps are different (real time behavior)
        import json

        event_1 = json.loads(log_file_1.read_text().strip())
        event_2 = json.loads(log_file_2.read_text().strip())

        assert event_1["ts_utc"] != event_2["ts_utc"], "Real timestamps should differ across runs"
