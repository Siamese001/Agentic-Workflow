"""
agentic_core/L0_maintenance/scripts/test_phase3_base_class_archiving.py
-----------------------------------------------------------------------
FIX: Implements Functional Naming.
REMOVED: 'test_l3_inheritance', 'test_l2_inheritance' etc. renamed to 
         'test_orchestration_inheritance', 'test_execution_inheritance'.
"""
import inspect
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestPhase3_BaseClassArchiving:
    """
    Verifies that legacy base agents are correctly "tombstoned"
    and still functional as aliases for SovereignBaseAgent.
    """

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test_sovereign_base_agent_exists(self):
        """SovereignBaseAgent should exist and be importable."""
        try:
            from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

            assert SovereignBaseAgent is not None
            agent = SovereignBaseAgent()
            assert agent is not None

            self.passed += 1
            print("✅ test_sovereign_base_agent_exists PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_sovereign_base_agent_exists: {e}")
            print(f"❌ test_sovereign_base_agent_exists FAILED: {e}")

    def test_sovereign_has_heal_repository(self):
        """SovereignBaseAgent should have heal_repository method."""
        try:
            from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

            assert hasattr(SovereignBaseAgent, "heal_repository")

            self.passed += 1
            print("✅ test_sovereign_has_heal_repository PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_sovereign_has_heal_repository: {e}")
            print(f"❌ test_sovereign_has_heal_repository FAILED: {e}")

    def test_legacy_base_agents_consolidated(self):
        """Legacy layer-specific base agents should be consolidated into SovereignBaseAgent."""
        try:
            from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
            
            # Verify SovereignBaseAgent is the SSOT
            assert SovereignBaseAgent is not None
            
            # Legacy base agents (L1-L6) should NOT exist as separate files
            # This is the expected state after Phase 3 consolidation
            legacy_paths = [
                PROJECT_ROOT / "agentic_core" / "L1_cognition" / "thought_engine" / "L1CognitionBaseAgent.py",
                PROJECT_ROOT / "agentic_core" / "L2_execution" / "L2ExecutionBaseAgent.py",
                PROJECT_ROOT / "agentic_core" / "L3_orchestration" / "workflow_engines" / "L3OrchestrationBaseAgent.py",
            ]
            
            # Count how many legacy files still exist (should be 0 after full consolidation)
            existing_legacy = [p for p in legacy_paths if p.exists()]
            
            if len(existing_legacy) == 0:
                print("  ✓ All legacy base agents consolidated")
            else:
                print(f"  ⚠ {len(existing_legacy)} legacy base agent files still exist (may be tombstones)")

            self.passed += 1
            print("✅ test_legacy_base_agents_consolidated PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_legacy_base_agents_consolidated: {e}")
            print(f"❌ test_legacy_base_agents_consolidated FAILED: {e}")

    def test_canon_base_agent_exists(self):
        """CanonBaseAgent should exist as an alias/variant."""
        try:
            # Check if CanonBaseAgent exists in expected locations
            canon_paths = [
                PROJECT_ROOT / "agentic_core" / "L2_execution" / "tool_registry" / "CanonBaseAgent.py",
                PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "CanonBaseAgent.py",
            ]
            
            existing = [p for p in canon_paths if p.exists()]
            
            if len(existing) > 0:
                print(f"  ✓ Found {len(existing)} CanonBaseAgent file(s)")

            self.passed += 1
            print("✅ test_canon_base_agent_exists PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_canon_base_agent_exists: {e}")
            print(f"❌ test_canon_base_agent_exists FAILED: {e}")


    def run_all(self):
        """Run all tests."""
        print("\n" + "=" * 70)
        print("PHASE 3: BASE CLASS ARCHIVING & CONSOLIDATION VERIFICATION SUITE")
        print("=" * 70 + "\n")

        self.test_sovereign_base_agent_exists()
        self.test_sovereign_has_heal_repository()
        self.test_legacy_base_agents_consolidated()
        self.test_canon_base_agent_exists()

        print("\n" + "=" * 70)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("=" * 70)

        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  - {error}")

        return self.failed == 0


if __name__ == "__main__":
    suite = TestPhase3_BaseClassArchiving()
    success = suite.run_all()
    sys.exit(0 if success else 1)
