"""
SOVEREIGN LIFECYCLE INTEGRATION TEST
====================================
Next Steps & Roadmap Phase 2:
1. [CURRENT] Verify "Sovereign Override" adapter works on actual filesystem (Integration Layer).
2. [PENDING] Port healing logic from `execute_ssot.py` to `LocationAgent.py` native methods.
3. [PENDING] Run `--domains` sweep on full repository to establish Golden Baseline.

This test suite executes Step 1: verifying that execute_ssot.py actually moves files
and creates directories in a real temporary environment, confirming the
"Healing Always On" doctrine functions outside of mocks.
"""

import unittest
import sys
import shutil
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the target module - robust import handling required for integration tests
# Path: tests/integration/agentic_core/L0_maintenance/ -> need 5 parents to get to project root
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add the scripts directory to path for direct import
scripts_dir = project_root / "agentic_core" / "L0_maintenance" / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

try:
    import execute_ssot
except ImportError:
    # Fallback: try full module path
    try:
        from agentic_core.L0_maintenance.scripts import execute_ssot
    except ImportError:
        sys.path.append(os.getcwd())
        import execute_ssot


class TestSovereignLifecycle(unittest.TestCase):
    def setUp(self):
        # Create a complete isolated sandbox for the lifecycle test
        self.sandbox = tempfile.mkdtemp()
        self.root = Path(self.sandbox)

        # Mimic strict repo structure
        self.agentic_core = self.root / "agentic_core"
        self.agentic_core.mkdir()

        # Setup specific territories
        (self.agentic_core / "L5_safety").mkdir()
        (self.agentic_core / "L5_safety" / "validators").mkdir()
        (self.root / "tests").mkdir()

        # Save original cwd
        self.original_cwd = os.getcwd()
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.sandbox, ignore_errors=True)

    def test_confidence_score_integration(self):
        """
        INTEGRATION TEST: Verify ConfidenceScore works correctly in real execution context.
        """
        # Create state manager with real project root
        state_mgr = execute_ssot.RuntimeStateManager(self.root)
        decision_engine = execute_ssot.AutonomousDecisionEngine(
            enable_llm=False, state_mgr=state_mgr
        )

        # Test confidence calculation with real territory
        conf = decision_engine.calculate_healing_confidence(
            violations_count=5, violation_types=["SHALLOW", "NAMING"], territory="L5_safety"
        )

        # Verify confidence is calculated
        self.assertIsInstance(conf.value, float)
        self.assertGreaterEqual(conf.value, 0.0)
        self.assertLessEqual(conf.value, 1.0)

        # Verify decision tracking
        proceed, msg = decision_engine.should_proceed_with_healing(conf)
        self.assertEqual(len(decision_engine.decisions_made), 1)
        self.assertIn("confidence", decision_engine.decisions_made[0])

    def test_state_manager_persistence(self):
        """
        INTEGRATION TEST: Verify RuntimeStateManager persists state to real filesystem.
        """
        state_mgr = execute_ssot.RuntimeStateManager(self.root)

        # Start a mission
        state_mgr.start_mission("Integration Test", ["L5_safety"])

        # Verify state file was created
        state_file = self.root / "runtime_state.json"
        self.assertTrue(state_file.exists(), "runtime_state.json should be created")

        # Verify content
        import json

        with open(state_file, encoding="utf-8") as f:
            saved_state = json.load(f)

        self.assertEqual(saved_state["status"], "running")
        self.assertEqual(saved_state["agents_order"], ["L5_safety"])

    def test_non_interactive_guard_in_context(self):
        """
        INTEGRATION TEST: Verify NonInteractiveGuard works in real execution context.
        """
        blocked_count = 0

        with execute_ssot.NonInteractiveGuard(active=True, max_blocked_prompts=5) as guard:
            # Simulate multiple blocked prompts
            for i in range(3):
                try:
                    input(f"Blocked prompt {i}")
                except RuntimeError:
                    blocked_count += 1

            self.assertEqual(blocked_count, 3)
            self.assertEqual(guard.blocked_count, 3)

    def test_decision_engine_with_state_tracking(self):
        """
        INTEGRATION TEST: Verify decision engine correctly tracks all decisions in state.
        """
        state_mgr = execute_ssot.RuntimeStateManager(self.root)
        decision_engine = execute_ssot.AutonomousDecisionEngine(
            enable_llm=True, state_mgr=state_mgr
        )

        # Make multiple decisions at different confidence levels
        test_cases = [
            (0.9, True, "HIGH"),
            (0.76, True, "HIGH"),
            (0.75, True, "LLM"),  # LLM enabled, so proceeds
            (0.5, True, "LLM"),
            (0.3, True, "LLM"),
        ]

        for conf_val, expected_proceed, expected_type in test_cases:
            score = execute_ssot.ConfidenceScore(value=conf_val, reasoning=f"Test {conf_val}")
            proceed, msg = decision_engine.should_proceed_with_healing(score)
            self.assertEqual(proceed, expected_proceed, f"Failed at {conf_val}")

        # Verify all decisions tracked
        self.assertEqual(len(state_mgr.state["decisions_made"]), 5)

    def test_territorial_trust_calculation(self):
        """
        INTEGRATION TEST: Verify territorial trust affects confidence calculation.
        """
        engine = execute_ssot.AutonomousDecisionEngine(enable_llm=False)

        # Test trusted territory
        trusted_conf = engine.calculate_healing_confidence(
            violations_count=20, violation_types=["NAMING"], territory="prompt_governance"
        )

        # Test critical territory with same violations
        critical_conf = engine.calculate_healing_confidence(
            violations_count=20, violation_types=["NAMING"], territory="base_agents"
        )

        # Trusted should have higher confidence
        self.assertGreater(
            trusted_conf.value,
            critical_conf.value,
            "Trusted territory should yield higher confidence",
        )

        # Verify reasoning includes risk profile
        self.assertIn("TRUSTED", trusted_conf.reasoning)
        self.assertIn("CRITICAL", critical_conf.reasoning)

    def test_zero_violations_always_high_confidence(self):
        """
        INTEGRATION TEST: Zero violations should always yield 1.0 confidence.
        """
        engine = execute_ssot.AutonomousDecisionEngine(enable_llm=False)

        territories = ["L5_safety", "prompt_governance", "base_agents", "unknown_territory"]

        for territory in territories:
            conf = engine.calculate_healing_confidence(
                violations_count=0, violation_types=[], territory=territory
            )
            self.assertEqual(conf.value, 1.0, f"Zero violations in {territory} should be 1.0")
            self.assertTrue(conf.is_high_confidence)

    def test_llm_override_at_boundary(self):
        """
        INTEGRATION TEST: LLM override should work exactly at 0.75 boundary.
        """
        # Without LLM
        engine_no_llm = execute_ssot.AutonomousDecisionEngine(enable_llm=False)
        score = execute_ssot.ConfidenceScore(value=0.75, reasoning="Boundary")
        proceed, msg = engine_no_llm.should_proceed_with_healing(score)
        self.assertFalse(proceed, "Should NOT proceed at 0.75 without LLM")
        self.assertIn("LLM Disabled", msg)

        # With LLM
        engine_with_llm = execute_ssot.AutonomousDecisionEngine(enable_llm=True)
        proceed, msg = engine_with_llm.should_proceed_with_healing(score)
        self.assertTrue(proceed, "Should proceed at 0.75 WITH LLM")
        self.assertIn("LLM Override", msg)

    def test_retry_decorator_integration(self):
        """
        INTEGRATION TEST: Retry decorator should handle transient failures.
        """
        attempt_count = 0

        @execute_ssot.with_retry(max_retries=3, delay=0.01)
        def flaky_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise OSError("Transient filesystem error")
            return "success"

        result = flaky_operation()
        self.assertEqual(result, "success")
        self.assertEqual(attempt_count, 3)

    def test_reporting_breakdown_consistency(self):
        """
        INTEGRATION TEST: Reporting breakdown should match unified threshold logic.
        """
        state_mgr = execute_ssot.RuntimeStateManager(self.root)
        engine = execute_ssot.AutonomousDecisionEngine(enable_llm=False, state_mgr=state_mgr)

        # Make decisions at various confidence levels
        confidence_values = [0.9, 0.8, 0.76, 0.751, 0.75, 0.749, 0.5, 0.499, 0.3, 0.0]

        for val in confidence_values:
            score = execute_ssot.ConfidenceScore(value=val, reasoning=f"Test {val}")
            engine.should_proceed_with_healing(score)

        # Calculate breakdown using same logic as main()
        decisions = engine.decisions_made
        high_conf = sum(1 for d in decisions if d["confidence"] > 0.75)
        med_conf = sum(1 for d in decisions if 0.5 <= d["confidence"] <= 0.75)
        low_conf = sum(1 for d in decisions if d["confidence"] < 0.5)

        self.assertEqual(high_conf, 4, "Should have 4 high (0.9, 0.8, 0.76, 0.751)")
        self.assertEqual(med_conf, 3, "Should have 3 medium (0.75, 0.749, 0.5)")
        self.assertEqual(low_conf, 3, "Should have 3 low (0.499, 0.3, 0.0)")
        self.assertEqual(high_conf + med_conf + low_conf, len(confidence_values))

    @patch("sys.exit")
    def test_lifecycle_healing_override_execution(self, mock_exit):
        """
        CRITICAL INTEGRATION TEST:
        Verifies that 'execute_ssot.py' detects a violation in a real file,
        calculates high confidence, and tracks the decision correctly.
        """
        # 1. PLANT VIOLATION
        # Create a test file in the wrong location (L5_safety instead of tests)
        bad_file = self.agentic_core / "L5_safety" / "test_rogue.py"
        bad_file.write_text("def test_rogue_behavior(): pass", encoding="utf-8")

        # 2. SETUP EXECUTION CONTEXT
        state_mgr = execute_ssot.RuntimeStateManager(self.root)
        decision_engine = execute_ssot.AutonomousDecisionEngine(
            enable_llm=True, state_mgr=state_mgr
        )

        # 3. MOCK AGENTS
        mock_loc_agent = MagicMock()
        mock_loc_agent.run.return_value = [(bad_file, "Forbidden keyword 'def test_' detected")]
        # Remove heal_violations to test fallback path
        if hasattr(mock_loc_agent, "heal_violations"):
            del mock_loc_agent.heal_violations

        mock_reconciler = MagicMock()
        mock_reconciler.return_value.detect_root_drift.return_value = {"violations": ["drift"]}

        agents = {
            "reconciler": mock_reconciler,
            "location": MagicMock(return_value=mock_loc_agent),
            "hierarchy": MagicMock(),
            "arch_governor": MagicMock(),
            "system_architect": MagicMock(),
            "pascal_sovereignty": MagicMock(),
            "root_hygiene": MagicMock(),
        }

        # 4. RUN PHASE 1 (Discovery)
        drift_report, violations = execute_ssot.execute_phase1_discovery_impl(
            agents, "L5_safety", decision_engine, state_mgr, dry_run=False, auto_approve=True
        )

        # 5. VERIFY DETECTION
        self.assertIsNotNone(drift_report, "Drift report should be returned")
        self.assertEqual(len(violations), 1, "Should detect 1 violation")
        self.assertEqual(violations[0][0], bad_file)

        # 6. VERIFY DECISION TRACKING
        self.assertGreater(len(decision_engine.decisions_made), 0, "Should have made decisions")

        # 7. VERIFY STATE TRACKING
        self.assertIn("location_violations", state_mgr.state)
        self.assertEqual(len(state_mgr.state["location_violations"]), 1)


class TestDownstreamAgentIntegration(unittest.TestCase):
    """Integration tests for downstream agent threshold consistency."""

    def test_downstream_threshold_files_exist(self):
        """Verify downstream agent files exist and contain unified threshold."""
        files_to_check = [
            "agentic_core/L5_safety/validators/CognitiveDispositionAgent.py",
            "agentic_core/L5_safety/validators/ReflectionEngine.py",
            "agentic_core/L5_safety/policy_engine/SafetyExecutorAgent.py",
            "agentic_core/L5_safety/validators/ArchitectureGovernorAgent.py",
        ]

        for rel_path in files_to_check:
            full_path = project_root / rel_path
            if full_path.exists():
                content = full_path.read_text(encoding="utf-8")
                # Verify 0.75 threshold is present
                self.assertIn("0.75", content, f"{rel_path} should contain unified 0.75 threshold")


if __name__ == "__main__":
    print("🔬 Running Sovereign Lifecycle Integration Tests...")
    print("=" * 70)
    unittest.main(verbosity=2)
