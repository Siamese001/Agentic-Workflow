import unittest
import json
import os
import sys
import tempfile
import asyncio
from unittest.mock import MagicMock, patch

# Add project directories to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '03_runtime'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '03_runtime', 'shared'))

# --- Import your actual modules ---
# Adjust these imports if your folder structure is nested (e.g. apps_rg.orchestrator)
try:
    from orchestrator import validate_manifest_integrity, ensure_manifest_freshness
    from agent_logic_connectivity import CanonValidator
    from apps_rg.L3_orchestration.hardened_orchestrator import HardenedOrchestrator, TERMINAL_ERRORS
    from connection_manager import InfrastructureError
except ImportError as e:
    pass
pass
# print(f"❌ Setup Error: Could not import project modules. {e}")  # [Security Fix]
    # print("Ensure this script is in the root directory and your PYTHONPATH is set.")  # [Security Fix]
    sys.exit(1)

class TestSystemHardening(unittest.TestCase):

    # =========================================================================
    # TEST 1: THE SABOTAGE TEST (Integrity Gate)
    # Goal: Verify the Orchestrator refuses to load a corrupt manifest.
    # =========================================================================
    def test_integrity_gate_catches_corruption(self):
        # print("\n🛡️  Running Test 1: Integrity Gate (Sabotage)...")  # [Security Fix]

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            # Write broken JSON (simulating a bad write or merge conflict)
            tmp.write('{"files": { "broken_entry": [ }')
            tmp_path = tmp.name

        try:
            # Should return False or raise Exception
            result = validate_manifest_integrity(tmp_path)
            self.assertFalse(result, "❌ Security Flaw: Orchestrator accepted corrupt JSON!")
            # print("   ✅ Orchestrator successfully rejected corrupt manifest.")  # [Security Fix]
        finally:
            os.remove(tmp_path)

    # =========================================================================
    # TEST 2: THE AMNESIA TEST (Memory Ghosting)
    # Goal: Verify queries strictly filter by the 'content_hash'.
    # =========================================================================
    @patch('agent_logic_connectivity.Pinecone')
    @patch('agent_logic_connectivity.Redis')
    def test_memory_uses_version_shield(self, mock_redis, mock_pinecone):
        # print("🛡️  Running Test 2: Memory Ghost Shield...")  # [Security Fix]

        # Setup
        validator = CanonValidator(manifest_path="active_manifest.json")
        validator.pinecone_index = MagicMock()
        validator.embedding_fn = lambda x: [0.1, 0.2] # Mock embedding

        # Mock the manifest lookup to return a specific hash
        validator._get_file_hash = MagicMock(return_value="HASH_V2_NEW")

        # Action: Query memory
        validator.query_semantic_memory("login logic", context_file="auth.py")

        # Verification: Did we send the filter?
        call_args = validator.pinecone_index.query.call_args
        _, kwargs = call_args

        actual_filter = kwargs.get('filter', {})
        expected_filter = {"file_path": "auth.py", "content_hash": "HASH_V2_NEW"}

        self.assertEqual(actual_filter, expected_filter,
            f"❌ Security Flaw: Filter missing! Expected {expected_filter}, got {actual_filter}")

        # print(f"   ✅ Query included strict hash filter: {actual_filter}")  # [Security Fix]

    # =========================================================================
    # TEST 3: THE ZOMBIE TEST (Error Classification)
    # Goal: Verify Terminal errors KILL the workflow, Infra errors PAUSE it.
    # =========================================================================
    async def run_resilience_check(self, error_to_raise, expected_status):
        # Setup
        orchestrator = HardenedOrchestrator()
        orchestrator.router = MagicMock()
        orchestrator.state_manager = MagicMock()
        orchestrator.workflow_state = MagicMock()

        # Mock router to throw the specific error
        orchestrator.router.execute_with_fallback = MagicMock(side_effect=error_to_raise)

        # Mock sys.exit so test doesn't actually quit
        with patch('sys.exit') as mock_exit:
            await orchestrator.execute_hop_with_hardening(MagicMock(name="TestHop"), {})

        return orchestrator.workflow_state, mock_exit

    def test_resilience_error_classification(self):
        # print("🛡️  Running Test 3: Zombie Prevention...")  # [Security Fix]
        loop = asyncio.new_event_loop()

        # Scenario A: SyntaxError (Terminal) -> Should FAILED
        state_fail, mock_exit_fail = loop.run_until_complete(
            self.run_resilience_check(SyntaxError("Bad Code"), "FAILED")
        )
        state_fail.mark_failed.assert_called()
        # print("   ✅ SyntaxError correctly triggered 'mark_failed'.")  # [Security Fix]

        # Scenario B: InfrastructureError (Transient) -> Should PAUSED
        state_pause, mock_exit_pause = loop.run_until_complete(
            self.run_resilience_check(InfrastructureError("Redis down"), "PAUSED")
        )
        state_pause.mark_paused.assert_called()
        # print("   ✅ InfrastructureError correctly triggered 'mark_paused'.")  # [Security Fix]

        loop.close()

if __name__ == '__main__':
    unittest.main(verbosity=0)

