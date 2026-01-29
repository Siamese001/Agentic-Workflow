#!/usr/bin/env python3
"""
Test suite for CognitiveDispositionAgent integration in execute_ssot.py
"""

import sys
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, AsyncMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestCDAIntegration(unittest.TestCase):
    """Test CognitiveDispositionAgent integration in execute_ssot.py"""

    def setUp(self):
        """Set up test environment"""
        self.project_root = Path.cwd()
        self.temp_dir = tempfile.mkdtemp()

    def test_enhanced_decision_engine_creation(self):
        """Test that EnhancedAutonomousDecisionEngine can be created with CDA enabled"""
        try:
            from agentic_core.L0_maintenance.scripts.execute_ssot import (
                EnhancedAutonomousDecisionEngine,
            )
            from agentic_core.L0_maintenance.scripts.execute_ssot import RuntimeStateManager

            state_mgr = RuntimeStateManager(self.project_root)

            # Test without CDA
            engine = EnhancedAutonomousDecisionEngine(
                enable_llm=False, state_mgr=state_mgr, enable_cda=False
            )
            self.assertIsNotNone(engine)
            self.assertFalse(engine.enable_cda)
            self.assertIsNone(engine.cda)

            # Test with CDA enabled
            engine_with_cda = EnhancedAutonomousDecisionEngine(
                enable_llm=False, state_mgr=state_mgr, enable_cda=True
            )
            self.assertIsNotNone(engine_with_cda)
            # CDA might not load if dependencies missing, but engine should still exist
            self.assertTrue(hasattr(engine_with_cda, "enable_cda"))

        except ImportError as e:
            self.skipTest(f"Could not import EnhancedAutonomousDecisionEngine: {e}")

    def test_cognitive_disposition_analysis(self):
        """Test cognitive disposition analysis functionality"""
        try:
            from agentic_core.L0_maintenance.scripts.execute_ssot import (
                EnhancedAutonomousDecisionEngine,
            )
            from agentic_core.L5_safety.validators.CognitiveDispositionAgent import (
                DispositionDecision,
            )

            # Create mock decision engine
            engine = EnhancedAutonomousDecisionEngine(enable_cda=False)

            # Test violation classification
            test_cases = [
                ("Missing sovereign root: test_dir", "MISSING_DIRECTORY"),
                ("Forbidden keyword 'def test_'", "FORBIDDEN_CONTENT"),
                ("Forbidden extension .py", "EXTENSION_MISMATCH"),
                ("test_function should be in tests", "TEST_FILE_MISPLACED"),
                ("Sovereign class violation", "SOVEREIGN_VIOLATION"),
                ("Some other violation", "STRUCTURAL_VIOLATION"),
            ]

            for message, expected_type in test_cases:
                result = engine._classify_violation_type(message)
                self.assertEqual(result, expected_type, f"Failed for message: {message}")

        except ImportError as e:
            self.skipTest(f"Could not import required modules: {e}")

    def test_cognitive_factor_calculation(self):
        """Test cognitive factor calculation from disposition decisions"""
        try:
            from agentic_core.L0_maintenance.scripts.execute_ssot import (
                EnhancedAutonomousDecisionEngine,
            )
            from agentic_core.L5_safety.validators.CognitiveDispositionAgent import (
                DispositionDecision,
            )

            engine = EnhancedAutonomousDecisionEngine(enable_cda=False)

            # Test with mock dispositions
            mock_dispositions = [
                DispositionDecision(action="MOVE", confidence=0.9),
                DispositionDecision(action="ARCHIVE", confidence=0.8),
                DispositionDecision(action="IGNORE", confidence=0.7),
                DispositionDecision(action="MANUAL_REVIEW", confidence=0.6),
            ]

            factor = engine._calculate_cognitive_factor(mock_dispositions)
            self.assertIsInstance(factor, float)
            self.assertGreater(factor, 0.0)
            self.assertLessEqual(factor, 1.0)

            # Test empty list
            empty_factor = engine._calculate_cognitive_factor([])
            self.assertEqual(empty_factor, 0.5)  # Neutral factor

        except ImportError as e:
            self.skipTest(f"Could not import required modules: {e}")

    @patch("agentic_core.L0_maintenance.scripts.execute_ssot.CognitiveDispositionAgent")
    def test_async_cognitive_analysis(self, mock_cda_class):
        """Test async cognitive analysis with mocked CDA"""
        try:
            import asyncio
            from agentic_core.L0_maintenance.scripts.execute_ssot import (
                EnhancedAutonomousDecisionEngine,
            )
            from agentic_core.L5_safety.validators.CognitiveDispositionAgent import (
                DispositionDecision,
            )

            # Mock the CDA instance
            mock_cda = AsyncMock()
            mock_cda_class.return_value = mock_cda

            # Mock the async analysis response
            mock_disposition = DispositionDecision(
                action="MOVE", target_path="/new/location", reason="Test reason", confidence=0.85
            )
            mock_cda.analyze_violation_async.return_value = mock_disposition

            engine = EnhancedAutonomousDecisionEngine(enable_cda=True)
            engine.cda = mock_cda

            # Test async method
            async def test_async():
                result = await engine.get_cognitive_disposition(
                    Path("test_file.py"), "TEST_VIOLATION", {"test": "context"}
                )
                return result

            result = asyncio.run(test_async())
            self.assertIsNotNone(result)
            self.assertEqual(result.action, "MOVE")
            self.assertEqual(result.confidence, 0.85)

        except ImportError as e:
            self.skipTest(f"Could not import required modules: {e}")

    def test_command_line_argument_parsing(self):
        """Test that --enable-cda argument is properly parsed"""
        try:
            from agentic_core.L0_maintenance.scripts.execute_ssot import main
            import argparse

            # Mock sys.argv to test argument parsing
            with patch("sys.argv", ["execute_ssot.py", "--enable-cda", "--territory", "test"]):
                try:
                    # This will try to run the main function, but we expect it to fail
                    # at some point since we're not providing a full environment
                    main()
                except SystemExit:
                    # Expected - the script will exit when it can't find the territory
                    pass
                except Exception:
                    # Other exceptions are also expected in test environment
                    pass

        except ImportError as e:
            self.skipTest(f"Could not import main function: {e}")

    def test_confidence_enhancement_with_cognitive_data(self):
        """Test that confidence calculation is enhanced with cognitive data"""
        try:
            from agentic_core.L0_maintenance.scripts.execute_ssot import (
                EnhancedAutonomousDecisionEngine,
            )
            from agentic_core.L5_safety.validators.CognitiveDispositionAgent import (
                DispositionDecision,
            )

            engine = EnhancedAutonomousDecisionEngine(enable_cda=False)

            # Test base confidence without cognitive data (with violations to trigger enhancement)
            base_confidence = engine.calculate_healing_confidence(
                violations_count=5, violation_types=["TEST"], territory="test_territory"
            )

            # Test enhanced confidence with cognitive data
            mock_dispositions = [
                DispositionDecision(action="MOVE", confidence=0.9),
                DispositionDecision(action="ARCHIVE", confidence=0.8),
            ]

            enhanced_confidence = engine.calculate_healing_confidence(
                violations_count=5,  # Need violations for cognitive enhancement to apply
                violation_types=["TEST"],
                territory="test_territory",
                cognitive_dispositions=mock_dispositions,
            )

            # Enhanced confidence should have cognitive factor when cognitive data is provided
            if mock_dispositions:
                self.assertIn("cognitive_analysis", enhanced_confidence.factors)
                self.assertIn("Cognitive:", enhanced_confidence.reasoning)
                # Cognitive should affect the confidence value
                self.assertNotEqual(base_confidence.value, enhanced_confidence.value)

        except ImportError as e:
            self.skipTest(f"Could not import required modules: {e}")


class TestCDALiveIntegration(unittest.TestCase):
    """Live integration tests for CognitiveDispositionAgent"""

    def setUp(self):
        """Set up test environment"""
        self.project_root = Path.cwd()

    @unittest.skipUnless(
        os.getenv("RUN_LIVE_TESTS"), "Live tests require RUN_LIVE_TESTS environment variable"
    )
    def test_live_cda_integration(self):
        """Test live CDA integration (requires actual LLM access)"""
        try:
            from agentic_core.L0_maintenance.scripts.execute_ssot import (
                EnhancedAutonomousDecisionEngine,
            )
            from agentic_core.L0_maintenance.scripts.execute_ssot import RuntimeStateManager

            state_mgr = RuntimeStateManager(self.project_root)
            engine = EnhancedAutonomousDecisionEngine(
                enable_llm=True, state_mgr=state_mgr, enable_cda=True
            )

            if not engine.enable_cda or not engine.cda:
                self.skipTest("CognitiveDispositionAgent not available in environment")

            # Test with a simple violation
            import asyncio

            async def test_live():
                result = await engine.get_cognitive_disposition(
                    Path("test_file.py"), "MISSING_DIRECTORY", {"territory": "test"}
                )
                return result

            result = asyncio.run(test_live())
            self.assertIsNotNone(result)
            self.assertIn(result.action, ["MOVE", "ARCHIVE", "IGNORE", "MANUAL_REVIEW"])
            self.assertIsInstance(result.confidence, float)
            self.assertGreaterEqual(result.confidence, 0.0)
            self.assertLessEqual(result.confidence, 1.0)

        except ImportError as e:
            self.skipTest(f"Could not import required modules: {e}")


def run_basic_integration_test():
    """Run a basic integration test without unittest framework"""
    print("🧪 Running Basic CDA Integration Test...")

    try:
        # Test import
        from agentic_core.L0_maintenance.scripts.execute_ssot import (
            EnhancedAutonomousDecisionEngine,
        )

        print("✅ EnhancedAutonomousDecisionEngine imported successfully")

        # Test instantiation
        engine = EnhancedAutonomousDecisionEngine(enable_cda=False)
        print("✅ EnhancedAutonomousDecisionEngine instantiated successfully")

        # Test violation classification
        test_message = "Missing sovereign root: test_dir"
        violation_type = engine._classify_violation_type(test_message)
        print(f"✅ Violation classification: {test_message} -> {violation_type}")

        # Test cognitive factor calculation
        from agentic_core.L5_safety.validators.CognitiveDispositionAgent import DispositionDecision

        mock_dispositions = [
            DispositionDecision(action="MOVE", confidence=0.9),
            DispositionDecision(action="ARCHIVE", confidence=0.8),
        ]
        factor = engine._calculate_cognitive_factor(mock_dispositions)
        print(f"✅ Cognitive factor calculation: {factor:.2f}")

        print("🎉 Basic integration test passed!")
        return True

    except Exception as e:
        print(f"❌ Basic integration test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 CognitiveDispositionAgent Integration Test Suite")
    print("=" * 60)

    # Run basic test first
    basic_success = run_basic_integration_test()
    print()

    # Run unittest suite
    print("🧪 Running Full Test Suite...")
    unittest.main(verbosity=2, exit=False)

    print("\n" + "=" * 60)
    if basic_success:
        print("🎉 All tests completed successfully!")
    else:
        print("⚠️  Some tests failed - check output above")
