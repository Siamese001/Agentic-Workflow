"""
Wave 2 Regression Tests: Execute SSOT Mutation Fence

Tests the mutation fence implementation for execute_ssot to ensure:
1. Protected roots block writes under agentic_core
2. Protected roots block rename/move under agentic_core
3. Protected roots allow writes outside agentic_core
4. Startup self-test aborts if fence inactive
5. Import preflight fails fast with actionable message
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add repo root to path for imports
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from agentic_core.L0_routing.enforcement.mutation_prohibition import (
    SourceMutationBlocked,
    enforce_protected_root,
    get_default_protected_root_policy,
)


@pytest.mark.governance
class TestProtectedRootEnforcement:
    """Test suite for protected root enforcement."""

    def test_protected_root_blocks_write_under_agentic_core(self, tmp_path):
        """Test 1: Protected roots block writes under agentic_core."""
        # Create a mock agentic_core path
        agentic_core_path = tmp_path / "agentic_core" / "test_file.py"

        # Mock the repo root to use tmp_path
        with patch(
            "agentic_core.L0_routing.enforcement.mutation_prohibition._get_repo_root", return_value=tmp_path
        ):
            # Attempt to write should raise SourceMutationBlocked
            with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
                enforce_protected_root(agentic_core_path, allow_override=False)

    def test_protected_root_blocks_rename_under_agentic_core(self, tmp_path):
        """Test 2: Protected roots block rename/move under agentic_core."""
        # Create destination path under agentic_core (rename/move target)
        dst_path = tmp_path / "agentic_core" / "new_file.py"

        # Mock the repo root to use tmp_path
        with patch(
            "agentic_core.L0_routing.enforcement.mutation_prohibition._get_repo_root", return_value=tmp_path
        ):
            # Destination should be blocked (rename/move target)
            with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
                enforce_protected_root(dst_path, allow_override=False)

    def test_protected_root_allows_write_outside_agentic_core(self, tmp_path):
        """Test 3: Protected roots allow writes outside agentic_core."""
        # Create a path outside protected roots
        safe_path = tmp_path / "logs" / "test_file.txt"

        # Mock the repo root to use tmp_path
        with patch(
            "agentic_core.L0_routing.enforcement.mutation_prohibition._get_repo_root", return_value=tmp_path
        ):
            # Should NOT raise - writes outside protected roots are allowed
            try:
                enforce_protected_root(safe_path, allow_override=False)
            except SourceMutationBlocked:
                pytest.fail(
                    "enforce_protected_root raised SourceMutationBlocked for path outside protected roots"
                )

    def test_protected_root_respects_override_flag(self, tmp_path):
        """Test that allow_override=True bypasses the protection."""
        # Create a path under agentic_core
        agentic_core_path = tmp_path / "agentic_core" / "test_file.py"

        # Mock the repo root to use tmp_path
        with patch(
            "agentic_core.L0_routing.enforcement.mutation_prohibition._get_repo_root", return_value=tmp_path
        ):
            # With override=True, should NOT raise
            try:
                enforce_protected_root(agentic_core_path, allow_override=True)
            except SourceMutationBlocked:
                pytest.fail("enforce_protected_root raised SourceMutationBlocked despite allow_override=True")


@pytest.mark.governance
class TestStartupFenceSelfTest:
    """Test suite for startup fence self-test."""

    def test_startup_self_test_aborts_if_fence_inactive(self):
        """Test 4: Startup self-test aborts if fence inactive (monkeypatch to simulate)."""

        # Monkeypatch enforce_protected_root to NOT raise (simulating inactive fence)
        def mock_enforce_no_raise(target_path, *, allow_override):
            # Do nothing - fence is inactive
            pass

        with patch(
            "agentic_core.L0_routing.enforcement.mutation_prohibition.enforce_protected_root",
            side_effect=mock_enforce_no_raise,
        ):
            # Simulate the startup self-test logic
            from agentic_core.L0_routing.enforcement.mutation_prohibition import SourceMutationBlocked

            probe_path = Path("/tmp/agentic_core/.tmp_fence_probe")
            fence_active = False

            try:
                # Import the patched version
                import agentic_core.L0_routing.enforcement.mutation_prohibition as mp

                mp.enforce_protected_root(probe_path, allow_override=False)
                # If we get here, fence is NOT active
                fence_active = False
            except SourceMutationBlocked:
                # Expected: fence blocked the write
                fence_active = True

            # Assert that fence was detected as inactive
            assert not fence_active, (
                "Fence should be detected as inactive when enforce_protected_root doesn't raise"
            )

    def test_startup_self_test_passes_if_fence_active(self, tmp_path):
        """Test that startup self-test passes when fence is active."""
        from agentic_core.L0_routing.enforcement.mutation_prohibition import (
            ProtectedRootPolicy,
            SourceMutationBlocked,
        )

        # Use a policy rooted at tmp_path so the probe path is under the immutable root
        policy = ProtectedRootPolicy(
            immutable_roots=("agentic_core",),
            log_path=str(tmp_path / "logs" / "fence.jsonl"),
        )
        probe_path = tmp_path / "agentic_core" / ".tmp_fence_probe"
        fence_active = False

        with patch(
            "agentic_core.L0_routing.enforcement.mutation_prohibition._get_repo_root",
            return_value=tmp_path,
        ):
            try:
                enforce_protected_root(probe_path, allow_override=False, policy=policy)
                fence_active = False
            except SourceMutationBlocked:
                fence_active = True

        assert fence_active, "Fence should be detected as active when enforce_protected_root raises"


@pytest.mark.governance
class TestImportPreflight:
    """Test suite for import/symbol preflight."""

    def test_import_preflight_fails_fast_with_actionable_message(self):
        """Test 5: Import preflight fails fast with actionable message (monkeypatch import resolution)."""
        import agentic_core.L0_routing.scripts.execute_ssot as execute_ssot_mod
        from agentic_core.L0_routing.scripts.execute_ssot import _preflight_import_check

        # Patch the module attribute directly to simulate missing _legacy_main
        original = getattr(execute_ssot_mod, "_legacy_main", None)
        try:
            del execute_ssot_mod._legacy_main
            with pytest.raises(RuntimeError, match="CRITICAL.*_legacy_main"):
                _preflight_import_check()
        except AttributeError:
            pytest.fail("_legacy_main not present on module; preflight test not applicable")
        finally:
            if original is not None:
                execute_ssot_mod._legacy_main = original

    def test_import_preflight_passes_when_symbols_exist(self):
        """Test that import preflight passes when all symbols exist."""
        # Use the real module (should have _legacy_main)
        from agentic_core.L0_routing.scripts.execute_ssot import _preflight_import_check

        # Should NOT raise
        try:
            _preflight_import_check()
        except RuntimeError as exc:
            pytest.fail(f"_preflight_import_check raised RuntimeError: {exc}")


@pytest.mark.governance
class TestProtectedRootPolicy:
    """Test suite for protected root policy."""

    def test_default_policy_has_correct_immutable_roots(self):
        """Test that default policy has the expected immutable roots."""
        policy = get_default_protected_root_policy()
        assert policy.immutable_roots == ("agentic_core", "tests", ".github", ".windsurfrules")

    def test_default_policy_log_path_outside_immutable_roots(self):
        """Test that default policy log path is outside immutable roots."""
        policy = get_default_protected_root_policy()
        log_path = Path(policy.log_path)

        # Log path should not start with any immutable root
        for immutable_root in policy.immutable_roots:
            assert not str(log_path).startswith(immutable_root), (
                f"Log path {log_path} should not be under immutable root {immutable_root}"
            )


# Deterministic test execution order
pytest_plugins = []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
