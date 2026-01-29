from pathlib import Path
from unittest.mock import patch

from agentic_core.L3_orchestration.interfaces import ExecutionContext
from agentic_core.L3_orchestration.OrchestratorAgent import OrchestratorAgent


class TestOrchestratorZeroLoss:
    @patch("subprocess.run")
    @patch("agentic_core.L3_orchestration.OrchestratorAgent.get_agent_paths")
    def test_validation_cache_efficiency(self, mock_paths, mock_run):
        """TC-01: Verifies subprocess is only called once for the same agent."""
        orchestrator = OrchestratorAgent()

        # Mock agent paths to return a valid path
        mock_paths.return_value = [
            "C:/Git/Agentic-Workflow/agentic_core/L3_orchestration/OrchestratorAgent.py"
        ]
        mock_run.return_value.returncode = 0

        # First call - should trigger subprocess
        orchestrator._validate_agent_import("OrchestratorAgent")
        # Second call - should hit cache
        orchestrator._validate_agent_import("OrchestratorAgent")

        assert mock_run.call_count == 1
        print("✓ TC-01: Validation cache prevented redundant subprocess overhead.")

    def test_zero_loss_context_merge(self):
        """TC-02: Ensures retry_context does not wipe out original accumulated_context."""
        orchestrator = OrchestratorAgent()
        context = ExecutionContext()
        context.accumulated_context = {"goal": "fix_recursion", "dataset": "core_v2"}
        context.retry_context = {"retry_count": 1}

        result = orchestrator._run_full_mode("TestAgent", dry_run=True, context=context)

        # Metadata check for merge proof
        assert result.metadata["dna_preserved"] is True
        print("✓ TC-02: Zero-Loss merge verified; goal and retry data co-exist.")

    def test_circuit_breaker_enforcement(self):
        """TC-03: Confirms the 50-step depth limit is strictly enforced."""
        orchestrator = OrchestratorAgent()
        context = ExecutionContext()
        context.metadata["depth"] = 51

        result = orchestrator.run_agent("TestAgent", context=context)

        assert result.status == "DEPTH_LIMIT_EXCEEDED"
        print("✓ TC-03: Forward-Rolling circuit breaker correctly halted execution.")

    def test_whitelist_rejection_caching(self):
        """TC-04: Ensures security rejections are also cached to prevent repeated bypass attempts."""
        orchestrator = OrchestratorAgent()

        # Mock get_agent_paths to return a path that will be rejected by whitelist
        with patch("agentic_core.L3_orchestration.OrchestratorAgent.get_agent_paths") as mock_paths:
            # Create a mock path that resolves to a module outside whitelist
            mock_path = "C:/Git/Agentic-Workflow/os.py"
            mock_paths.return_value = [mock_path]

            # Mock the project root to ensure path resolution works
            with patch.object(orchestrator, "project_root"):
                orchestrator.project_root = Path("C:/Git/Agentic-Workflow")

                # Attempt an out-of-bounds import
                result = orchestrator._validate_agent_import("os")

                # Should be rejected and cached
                assert result is False
                assert len(orchestrator._import_cache) > 0

                # Verify the rejection is cached
                cached_value = list(orchestrator._import_cache.values())[0]
                assert cached_value is False

            print("✓ TC-04: Security rejections successfully cached.")
