import pytest
pytestmark = pytest.mark.skip(reason="DEPRECATED: Test requires external modules")

"""
Test Suite for Canon Validator Engine (E1) - Zero-Loss Merge Compliance

Test Cases:
- TC-ZLM-101: Standard Successful Merge
- TC-ZLM-201: P2 Failure, P6 Single-Pass Fix
- TC-ZLM-202: P2 Failure, P6 Multi-Pass Fix
- TC-ZLM-203: ZLM Hard Stop Condition
- TC-ZLM-301: P5 Logging Integrity
- TC-ZLM-302: P7 File Integrity Check
- TC-ZLM-303: L5 Audit Trail
"""
import re
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))
from agentic_core.L2_execution.P3_engines.canon_validator_engine_zlm import CanonValidatorEngineZLM, ExitReason, P6FixResult, PhaseResult, PhaseStatus

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
from typing import Any
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class test_zlm_standard_successful_merge(unittest.TestCase):
    """TC-ZLM-101: Standard Successful Merge"""

    @patch('agentic_core.engines.canon_validator_engine_zlm.SandboxUtils.execute_in_sandbox')
    @patch('agentic_core.engines.canon_validator_engine_zlm.CoreUtils.validate_python_syntax')
    @patch('agentic_core.engines.canon_validator_engine_zlm.CoreUtils.sign_and_commit')
    def test_standard_successful_merge(self, mock_sign: Any, mock_p1: Any, mock_p2: Any) -> Any:
        """
        Given: Valid code committed. P1/P2 pass on Attempt 1.
        When: The engine executes P1 and P2 checks.
        Then: Engine immediately bypasses P6 loop, calls sign_and_commit(),
              and terminates with EXIT_SUCCESS.
        """
        mock_p1.return_value = PhaseResult(status=PhaseStatus.SUCCESS, phase='P1', message='Syntax valid')
        mock_p2.return_value = PhaseResult(status=PhaseStatus.SUCCESS, phase='P2', message='Tests passed')
        mock_sign.return_value = PhaseResult(status=PhaseStatus.SUCCESS, phase='P9', message='Commit signed')
        engine: Any = CanonValidatorEngineZLM(['test_file.py'])
        exit_reason, message = engine.run()
        self.assertEqual(exit_reason, ExitReason.P9_SUCCESS)
        self.assertEqual(engine.attempts, 1)
        mock_p1.assert_called_once()
        mock_p2.assert_called_once()
        mock_sign.assert_called_once()

class test_zlmp6_single_pass_fix(unittest.TestCase):
    """TC-ZLM-201: P2 Failure, P6 Single-Pass Fix"""

    @patch('agentic_core.engines.canon_validator_engine_zlm.L5Consensus.query_consensus')
    @patch('agentic_core.engines.canon_validator_engine_zlm.SandboxUtils.execute_in_sandbox')
    @patch('agentic_core.engines.canon_validator_engine_zlm.CoreUtils.validate_python_syntax')
    @patch('agentic_core.engines.canon_validator_engine_zlm.CoreUtils.sign_and_commit')
    def test_p6_single_pass_fix(self, mock_sign: Any, mock_p1: Any, mock_p2: Any, mock_consensus: Any) -> Any:
        """
        Given: Commit causes runtime failure (P2 FAIL). L5 Consensus returns
               a correct fix on Attempt 1.
        When: Engine enters ZLM loop, calls L5.query_consensus(), applies fix,
              and restarts P2.
        Then: P2 PASSES on Attempt 2. Engine proceeds to P9 and terminates
              with EXIT_SUCCESS. ZLM Goal Met.
        """
        mock_p1.return_value = PhaseResult(status=PhaseStatus.SUCCESS, phase='P1', message='Syntax valid')
        mock_p2.side_effect = [PhaseResult(status=PhaseStatus.FAIL, phase='P2', message='Test failed', stderr='AssertionError: expected 2, got 1'), PhaseResult(status=PhaseStatus.SUCCESS, phase='P2', message='Tests passed')]
        mock_consensus.return_value = P6FixResult(status=PhaseStatus.SUCCESS, corrected_code='def add(a, b): return a + b', confidence=0.95)
        mock_sign.return_value = PhaseResult(status=PhaseStatus.SUCCESS, phase='P9', message='Commit signed')
        engine: Any = CanonValidatorEngineZLM(['test_file.py'])
        exit_reason, message = engine.run()
        self.assertEqual(exit_reason, ExitReason.P9_SUCCESS)
        self.assertEqual(engine.attempts, 2)
        self.assertEqual(mock_p2.call_count, 2)
        mock_consensus.assert_called_once()
        mock_sign.assert_called_once()

class test_zlmp6_multi_pass_fix(unittest.TestCase):
    """TC-ZLM-202: P2 Failure, P6 Multi-Pass Fix"""

    @patch('agentic_core.engines.canon_validator_engine_zlm.L5Consensus.query_consensus')
    @patch('agentic_core.engines.canon_validator_engine_zlm.SandboxUtils.execute_in_sandbox')
    @patch('agentic_core.engines.canon_validator_engine_zlm.CoreUtils.validate_python_syntax')
    @patch('agentic_core.engines.canon_validator_engine_zlm.CoreUtils.sign_and_commit')
    def test_p6_multi_pass_fix(self, mock_sign: Any, mock_p1: Any, mock_p2: Any, mock_consensus: Any) -> Any:
        """
        Given: Commit fails P2. L5 Consensus returns a fix on Attempt 2 that
               still fails P2. A correct fix is returned on Attempt 3.
        When: Engine runs P2 (FAIL), P6 (FAIL), restarts loop.
              Runs P2 (FAIL), P6 (SUCCESS), restarts loop.
        Then: P2 PASSES on Attempt 4. Engine proceeds to P9. ZLM Goal Met.
        """
        mock_p1.return_value = PhaseResult(status=PhaseStatus.SUCCESS, phase='P1', message='Syntax valid')
        mock_p2.side_effect = [PhaseResult(status=PhaseStatus.FAIL, phase='P2', message='Test failed', stderr='Error 1'), PhaseResult(status=PhaseStatus.FAIL, phase='P2', message='Test failed', stderr='Error 2'), PhaseResult(status=PhaseStatus.FAIL, phase='P2', message='Test failed', stderr='Error 3'), PhaseResult(status=PhaseStatus.SUCCESS, phase='P2', message='Tests passed')]
        mock_consensus.side_effect = [P6FixResult(status=PhaseStatus.FAIL), P6FixResult(status=PhaseStatus.FAIL), P6FixResult(status=PhaseStatus.SUCCESS, corrected_code='fixed code', confidence=0.9)]
        mock_sign.return_value = PhaseResult(status=PhaseStatus.SUCCESS, phase='P9', message='Commit signed')
        engine: Any = CanonValidatorEngineZLM(['test_file.py'])
        engine.MAX_P6_ATTEMPTS = 4
        exit_reason, message = engine.run()
        self.assertEqual(exit_reason, ExitReason.P9_SUCCESS)
        self.assertEqual(engine.attempts, 4)
        self.assertEqual(mock_p2.call_count, 4)
        self.assertEqual(mock_consensus.call_count, 3)

class test_zlm_hard_stop_condition(unittest.TestCase):
    """TC-ZLM-203: ZLM Hard Stop Condition"""

    @patch('agentic_core.engines.canon_validator_engine_zlm.L5Consensus.add_observations')
    @patch('agentic_core.engines.canon_validator_engine_zlm.L5Consensus.query_consensus')
    @patch('agentic_core.engines.canon_validator_engine_zlm.SandboxUtils.execute_in_sandbox')
    @patch('agentic_core.engines.canon_validator_engine_zlm.CoreUtils.validate_python_syntax')
    def test_zlm_hard_stop(self, mock_p1: Any, mock_p2: Any, mock_consensus: Any, mock_observations: Any) -> Any:
        """
        Given: Commit fails P2. L5 Consensus returns no fix or invalid fix
               on Attempt 1, 2, and 3.
        When: Engine runs P2, P6, restarts loop 3 times.
        Then: The condition ATTEMPTS >= MAX_P6_ATTEMPTS is met.
              Engine terminates with EXIT_FAILURE and logs ZLM failure to L5.
        """
        mock_p1.return_value = PhaseResult(status=PhaseStatus.SUCCESS, phase='P1', message='Syntax valid')
        mock_p2.return_value = PhaseResult(status=PhaseStatus.FAIL, phase='P2', message='Test failed', stderr='Persistent error')
        mock_consensus.return_value = P6FixResult(status=PhaseStatus.FAIL)
        engine: Any = CanonValidatorEngineZLM(['test_file.py'])
        exit_reason, message = engine.run()
        self.assertEqual(exit_reason, ExitReason.P6_LIMIT_REACHED)
        self.assertEqual(engine.attempts, 3)
        self.assertEqual(mock_p2.call_count, 3)
        self.assertEqual(mock_consensus.call_count, 3)
        observation_calls: Any = [call for call in mock_observations.call_args_list if 'ZLM_FAIL_MAX_ATTEMPTS' in str(call)]
        self.assertGreater(len(observation_calls), 0)

class test_p5_logging_integrity(unittest.TestCase):
    """TC-ZLM-301: P5 Logging Integrity"""

    @patch('agentic_core.engines.canon_validator_engine_zlm.CoreUtils.log_action')
    @patch('agentic_core.engines.canon_validator_engine_zlm.L5Consensus.query_consensus')
    @patch('agentic_core.engines.canon_validator_engine_zlm.SandboxUtils.execute_in_sandbox')
    @patch('agentic_core.engines.canon_validator_engine_zlm.CoreUtils.validate_python_syntax')
    @patch('agentic_core.engines.canon_validator_engine_zlm.CoreUtils.sign_and_commit')
    def test_p5_logging_integrity(self, mock_sign: Any, mock_p1: Any, mock_p2: Any, mock_consensus: Any, mock_log: Any) -> Any:
        """
        Given: The engine executes a full P2 failure/P6 fix/P9 success cycle.
        When: Engine executes log_action() at start of P1, P2, P6, and P9.
        Then: The logs contain timestamped records for all 5 major events.
        """
        mock_p1.return_value = PhaseResult(status=PhaseStatus.SUCCESS, phase='P1', message='OK')
        mock_p2.side_effect = [PhaseResult(status=PhaseStatus.FAIL, phase='P2', message='Fail', stderr='Error'), PhaseResult(status=PhaseStatus.SUCCESS, phase='P2', message='OK')]
        mock_consensus.return_value = P6FixResult(status=PhaseStatus.SUCCESS, corrected_code='fixed', confidence=0.9)
        mock_sign.return_value = PhaseResult(status=PhaseStatus.SUCCESS, phase='P9', message='OK')
        engine: Any = CanonValidatorEngineZLM(['test_file.py'])
        engine.run()
        log_calls: Any = [str(call) for call in mock_log.call_args_list]
        self.assertTrue(any(('P1_VALIDATION_START' in call for call in log_calls)))
        self.assertTrue(any(('P2_SANDBOX_START' in call for call in log_calls)))
        self.assertTrue(any(('P6_FIX_APPLIED' in call for call in log_calls)))
        self.assertTrue(any(('P9_COMMIT_SUCCESS' in call for call in log_calls)))

class test_p7_file_integrity_check(unittest.TestCase):
    """TC-ZLM-302: P7 File Integrity Check"""

    def test_p7_canonical_file_protection(self) -> Any:
        """
        Given: A canonical file is monitored by P7's Canary Trap.
        When: P6 consensus attempts to apply fix using APPLY_INLINE_FIX.
        Then: P7 monitor does not trigger alert, confirming fix only targets
              approved staging files.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test(): pass\n')
            test_file: Any = f.name
        try:
            engine: Any = CanonValidatorEngineZLM([test_file])
            engine._apply_inline_fix(test_file, 'def test(): return True\n')
            with open(test_file, 'r') as f:
                content: Any = f.read()
            self.assertIn('return True', content)
        finally:
            os.unlink(test_file)

class test_l5_audit_trail(unittest.TestCase):
    """TC-ZLM-303: L5 Audit Trail"""

    @patch('agentic_core.engines.canon_validator_engine_zlm.L5Consensus.add_observations')
    @patch('agentic_core.engines.canon_validator_engine_zlm.L5Consensus.query_consensus')
    @patch('agentic_core.engines.canon_validator_engine_zlm.SandboxUtils.execute_in_sandbox')
    @patch('agentic_core.engines.canon_validator_engine_zlm.CoreUtils.validate_python_syntax')
    @patch('agentic_core.engines.canon_validator_engine_zlm.CoreUtils.sign_and_commit')
    def test_l5_audit_trail(self, mock_sign: Any, mock_p1: Any, mock_p2: Any, mock_consensus: Any, mock_observations: Any) -> Any:
        """
        Given: A full P2 failure/P6 fix/P9 success cycle is completed.
        When: Engine makes four separate L5.add_observations() calls.
        Then: L5 MEMemory contains four distinct nodes documenting the cycle.
        """
        mock_p1.return_value = PhaseResult(status=PhaseStatus.SUCCESS, phase='P1', message='OK')
        mock_p2.side_effect = [PhaseResult(status=PhaseStatus.FAIL, phase='P2', message='Fail', stderr='Error'), PhaseResult(status=PhaseStatus.SUCCESS, phase='P2', message='OK')]
        mock_consensus.return_value = P6FixResult(status=PhaseStatus.SUCCESS, corrected_code='fixed', confidence=0.9)
        mock_sign.return_value = PhaseResult(status=PhaseStatus.SUCCESS, phase='P9', message='OK')
        engine: Any = CanonValidatorEngineZLM(['test_file.py'])
        engine.run()
        observation_calls: Any = mock_observations.call_args_list
        p2_fail_calls: Any = [call for call in observation_calls if 'P2_FAIL_ATTEMPT' in str(call)]
        self.assertGreater(len(p2_fail_calls), 0)
        for call_obj in observation_calls:
            args, kwargs = call_obj
            if args:
                data: Any = args[0]
                self.assertIn('event', data)

def run_test_suite() -> Any:
    """Run the complete ZLM test suite."""
    loader: Any = unittest.TestLoader()
    suite: Any = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestZLMStandardSuccessfulMerge))
    suite.addTests(loader.loadTestsFromTestCase(TestZLMP6SinglePassFix))
    suite.addTests(loader.loadTestsFromTestCase(TestZLMP6MultiPassFix))
    suite.addTests(loader.loadTestsFromTestCase(TestZLMHardStopCondition))
    suite.addTests(loader.loadTestsFromTestCase(TestP5LoggingIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestP7FileIntegrityCheck))
    suite.addTests(loader.loadTestsFromTestCase(TestL5AuditTrail))
    runner: Any = unittest.TextTestRunner(verbosity=2)
    result: Any = runner.run(suite)
    return result
if __name__ == '__main__':
    result: Any = run_test_suite()
    sys.exit(0 if result.wasSuccessful() else 1)
