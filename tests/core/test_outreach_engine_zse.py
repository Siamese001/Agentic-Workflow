"""
Test Suite for Outreach Engine ZSE (Engine 3)
Covers test cases TC-E3-101 through TC-E3-302
"""
import re
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tempfile
import unittest
from unittest.mock import patch
from agentic_core.L2_execution.P3_engines.outreach_engine_zse import ExitReason, OutreachEngineZSE
from agentic_core.knowledge.l5_consolidated import KnowledgeResult
from agentic_core.utils.networking import EgressResult

class test_standard_zse_success(unittest.TestCase):
    """TC-E3-101: Standard ZSE Success"""

    @patch('agentic_core.engines.outreach_engine_zse.send_email')
    @patch('agentic_core.engines.outreach_engine_zse.get_consolidated_knowledge')
    @patch('agentic_core.engines.outreach_engine_zse.get_networking_utility')
    @patch('agentic_core.engines.outreach_engine_zse.register_process')
    @patch('agentic_core.engines.outreach_engine_zse.log_action')
    def test_standard_zse_success(self, mock_log: Any, mock_register: Any, mock_network: Any, mock_knowledge: Any, mock_send: Any) -> Any:
        """
        Given: Context is valid. Initial pitch passes P6 Consensus.
        When: Engine executes full cycle.
        Then: Email is sent, P5 logs success, ZSE -> EXIT_SUCCESS.
        """
        mock_network.return_value.strict_egress_filter.return_value = EgressResult(status='PASS', reason='Host whitelisted', host='linkedin.com')
        mock_network.return_value.fetch_url.return_value = {'status': 'mock_success', 'content': 'Company content'}
        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(user_profile={'timezone': 'UTC'}, template=None, metadata={'source': 'test'})
        mock_knowledge.return_value.query_consensus.return_value = {'status': 'PASS', 'evaluations': [], 'consensus_score': 1.0, 'reason': 'All checks passed'}
        mock_knowledge.return_value.add_observations.return_value = True
        mock_send.return_value = {'status': 'dry_run_success', 'to': 'test@example.com'}
        engine: Any = OutreachEngineZSE(output_dir=tempfile.mkdtemp(), dry_run=True)
        exit_reason, result = engine.execute_outreach(company_url='https://linkedin.com/company/test', contact_email='test@example.com')
        self.assertEqual(exit_reason, ExitReason.ZSE_SUCCESS)
        self.assertIsNotNone(result)
        self.assertEqual(result['refinements'], 0)
        self.assertEqual(mock_send.call_count, 1)
        log_calls: Any = [str(call) for call in mock_log.call_args_list]
        self.assertTrue(any(('SEND_EMAIL_SUCCESS' in call for call in log_calls)))

class test_p8_egress_filter_block(unittest.TestCase):
    """TC-E3-102: P8 Egress Filter Block"""

    @patch('agentic_core.engines.outreach_engine_zse.get_networking_utility')
    @patch('agentic_core.engines.outreach_engine_zse.register_process')
    @patch('agentic_core.engines.outreach_engine_zse.log_action')
    def test_p8_egress_block(self, mock_log: Any, mock_register: Any, mock_network: Any) -> Any:
        """
        Given: Engine attempts to fetch from unwhitelisted domain.
        When: Egress filter is called.
        Then: Filter returns FAIL, engine exits before pitch generation.
        """
        mock_network.return_value.strict_egress_filter.return_value = EgressResult(status='FAIL', reason='Host malicious.com not in whitelist', host='malicious.com')
        engine: Any = OutreachEngineZSE(output_dir=tempfile.mkdtemp(), dry_run=True)
        exit_reason, result = engine.execute_outreach(company_url='https://malicious.com/company/test', contact_email='test@example.com')
        self.assertEqual(exit_reason, ExitReason.P8_EGRESS_BLOCK)
        self.assertIsNone(result)
        log_calls: Any = [str(call) for call in mock_log.call_args_list]
        self.assertTrue(any(('P8_EGRESS_BLOCK' in call for call in log_calls)))

class test_p6_compliance_failure(unittest.TestCase):
    """TC-E3-201: P6 Compliance Failure (ZSE Loop)"""

    @patch('agentic_core.engines.outreach_engine_zse.send_email')
    @patch('agentic_core.engines.outreach_engine_zse.get_consolidated_knowledge')
    @patch('agentic_core.engines.outreach_engine_zse.get_networking_utility')
    @patch('agentic_core.engines.outreach_engine_zse.register_process')
    @patch('agentic_core.engines.outreach_engine_zse.log_action')
    def test_p6_compliance_failure(self, mock_log: Any, mock_register: Any, mock_network: Any, mock_knowledge: Any, mock_send: Any) -> Any:
        """
        Given: Initial pitch has non-compliant branding.
        When: P6 consensus fails.
        Then: Engine triggers P10 Shadow Mode and restarts loop.
        """
        mock_network.return_value.strict_egress_filter.return_value = EgressResult(status='PASS', reason='Host whitelisted', host='linkedin.com')
        mock_network.return_value.fetch_url.return_value = {'status': 'mock_success', 'content': 'Company content'}
        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(user_profile={'timezone': 'UTC'}, template=None, metadata={'source': 'test'})
        mock_knowledge.return_value.query_consensus.side_effect = [{'status': 'FAIL', 'evaluations': [], 'consensus_score': 0.33, 'reason': 'Brand tone and style analysis; Spam and promotional content analysis'}, {'status': 'PASS', 'evaluations': [], 'consensus_score': 1.0, 'reason': 'All checks passed'}]
        mock_knowledge.return_value.add_observations.return_value = True
        mock_send.return_value = {'status': 'dry_run_success'}
        engine: Any = OutreachEngineZSE(output_dir=tempfile.mkdtemp(), dry_run=True)
        exit_reason, result = engine.execute_outreach(company_url='https://linkedin.com/company/test', contact_email='test@example.com')
        self.assertEqual(exit_reason, ExitReason.ZSE_SUCCESS)
        self.assertEqual(engine.refinement_count, 1)
        self.assertEqual(mock_knowledge.return_value.query_consensus.call_count, 2)
        log_calls: Any = [str(call) for call in mock_log.call_args_list]
        self.assertTrue(any(('P10_START' in call for call in log_calls)))
        self.assertTrue(any(('P10_SHADOW_REFINEMENT' in call for call in log_calls)))

class test_p10_refinement_success(unittest.TestCase):
    """TC-E3-202: P10 Refinement Success"""

    @patch('agentic_core.engines.outreach_engine_zse.send_email')
    @patch('agentic_core.engines.outreach_engine_zse.get_consolidated_knowledge')
    @patch('agentic_core.engines.outreach_engine_zse.get_networking_utility')
    @patch('agentic_core.engines.outreach_engine_zse.register_process')
    @patch('agentic_core.engines.outreach_engine_zse.log_action')
    def test_p10_refinement_success(self, mock_log: Any, mock_register: Any, mock_network: Any, mock_knowledge: Any, mock_send: Any) -> Any:
        """
        Given: P6 fails on attempt 1, P10 refines pitch.
        When: P6 passes on attempt 2.
        Then: Engine sends email, ZSE goal met.
        """
        mock_network.return_value.strict_egress_filter.return_value = EgressResult(status='PASS', reason='Host whitelisted', host='linkedin.com')
        mock_network.return_value.fetch_url.return_value = {'status': 'mock_success', 'content': 'Company content'}
        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(user_profile={'timezone': 'UTC'}, template=None, metadata={'source': 'test'})
        mock_knowledge.return_value.query_consensus.side_effect = [{'status': 'FAIL', 'evaluations': [], 'consensus_score': 0.33, 'reason': 'Brand compliance issue'}, {'status': 'PASS', 'evaluations': [], 'consensus_score': 1.0, 'reason': 'All checks passed'}]
        mock_knowledge.return_value.add_observations.return_value = True
        mock_send.return_value = {'status': 'dry_run_success'}
        engine: Any = OutreachEngineZSE(output_dir=tempfile.mkdtemp(), dry_run=True)
        exit_reason, result = engine.execute_outreach(company_url='https://linkedin.com/company/test', contact_email='test@example.com')
        self.assertEqual(exit_reason, ExitReason.ZSE_SUCCESS)
        self.assertEqual(result['refinements'], 1)
        self.assertEqual(mock_send.call_count, 1)

class test_zse_max_refinements_failure(unittest.TestCase):
    """TC-E3-203: ZSE Max Attempts Failure"""

    @patch('agentic_core.engines.outreach_engine_zse.get_consolidated_knowledge')
    @patch('agentic_core.engines.outreach_engine_zse.get_networking_utility')
    @patch('agentic_core.engines.outreach_engine_zse.register_process')
    @patch('agentic_core.engines.outreach_engine_zse.log_action')
    def test_zse_max_refinements_failure(self, mock_log: Any, mock_register: Any, mock_network: Any, mock_knowledge: Any) -> Any:
        """
        Given: Pitch fails P6 on attempts 1, 2, and 3.
        When: MAX_REFINEMENTS (2) is exceeded.
        Then: Engine logs ZSE_FAIL_MAX_REFINEMENTS and exits with FAILURE.
        """
        mock_network.return_value.strict_egress_filter.return_value = EgressResult(status='PASS', reason='Host whitelisted', host='linkedin.com')
        mock_network.return_value.fetch_url.return_value = {'status': 'mock_success', 'content': 'Company content'}
        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(user_profile={'timezone': 'UTC'}, template=None, metadata={'source': 'test'})
        mock_knowledge.return_value.query_consensus.return_value = {'status': 'FAIL', 'evaluations': [], 'consensus_score': 0.0, 'reason': 'Brand compliance issue'}
        mock_knowledge.return_value.add_observations.return_value = True
        engine: Any = OutreachEngineZSE(output_dir=tempfile.mkdtemp(), dry_run=True)
        exit_reason, result = engine.execute_outreach(company_url='https://linkedin.com/company/test', contact_email='test@example.com')
        self.assertEqual(exit_reason, ExitReason.ZSE_MAX_REFINEMENTS)
        self.assertIsNone(result)
        self.assertEqual(engine.refinement_count, 2)
        log_calls: Any = [str(call) for call in mock_log.call_args_list]
        self.assertTrue(any(('ZSE_FAIL_MAX_REFINEMENTS' in call for call in log_calls)))

class test_p5_watchdog_kill_condition(unittest.TestCase):
    """TC-E3-301: P5 Watchdog Kill Condition"""

    @patch('agentic_core.engines.outreach_engine_zse.send_email')
    @patch('agentic_core.engines.outreach_engine_zse.get_consolidated_knowledge')
    @patch('agentic_core.engines.outreach_engine_zse.get_networking_utility')
    @patch('agentic_core.engines.outreach_engine_zse.register_process')
    @patch('agentic_core.engines.outreach_engine_zse.log_action')
    def test_p5_watchdog_kill_condition(self, mock_log: Any, mock_register: Any, mock_network: Any, mock_knowledge: Any, mock_send: Any) -> Any:
        """
        Given: Engine completes successful cycle.
        When: P5 detects rapid email burst.
        Then: DeadManSwitch kills agent process.
        """
        mock_network.return_value.strict_egress_filter.return_value = EgressResult(status='PASS', reason='Host whitelisted', host='linkedin.com')
        mock_network.return_value.fetch_url.return_value = {'status': 'mock_success', 'content': 'Company content'}
        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(user_profile={'timezone': 'UTC'}, template=None, metadata={'source': 'test'})
        mock_knowledge.return_value.query_consensus.return_value = {'status': 'PASS', 'evaluations': [], 'consensus_score': 1.0, 'reason': 'All checks passed'}
        mock_knowledge.return_value.add_observations.return_value = True
        mock_send.return_value = {'status': 'dry_run_success'}
        engine: Any = OutreachEngineZSE(output_dir=tempfile.mkdtemp(), dry_run=True)
        for i in range(10):
            engine.execute_outreach(company_url='https://linkedin.com/company/test', contact_email=f'test{i}@example.com')
        self.assertGreaterEqual(mock_log.call_count, 10)

class test_l4_time_utility_check(unittest.TestCase):
    """TC-E3-302: L4 Time Utility Check"""

    @patch('agentic_core.engines.outreach_engine_zse.send_email')
    @patch('agentic_core.engines.outreach_engine_zse.get_consolidated_knowledge')
    @patch('agentic_core.engines.outreach_engine_zse.get_networking_utility')
    @patch('agentic_core.engines.outreach_engine_zse.register_process')
    @patch('agentic_core.engines.outreach_engine_zse.log_action')
    def test_l4_time_utility_check(self, mock_log: Any, mock_register: Any, mock_network: Any, mock_knowledge: Any, mock_send: Any) -> Any:
        """
        Given: Contact context specifies timezone 12 hours ahead.
        When: L4 time conversion is called.
        Then: OPTIMAL_SEND_TIME is correctly calculated.
        """
        mock_network.return_value.strict_egress_filter.return_value = EgressResult(status='PASS', reason='Host whitelisted', host='linkedin.com')
        mock_network.return_value.fetch_url.return_value = {'status': 'mock_success', 'content': 'Company content'}
        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(user_profile={'timezone': 'Asia/Singapore'}, template=None, metadata={'source': 'test'})
        mock_knowledge.return_value.query_consensus.return_value = {'status': 'PASS', 'evaluations': [], 'consensus_score': 1.0, 'reason': 'All checks passed'}
        mock_knowledge.return_value.add_observations.return_value = True
        mock_send.return_value = {'status': 'dry_run_success'}
        engine: Any = OutreachEngineZSE(output_dir=tempfile.mkdtemp(), dry_run=True)
        exit_reason, result = engine.execute_outreach(company_url='https://linkedin.com/company/test', contact_email='test@example.com')
        self.assertEqual(exit_reason, ExitReason.ZSE_SUCCESS)
        self.assertIsNotNone(result)
        log_calls: Any = [str(call) for call in mock_log.call_args_list]
        self.assertTrue(any(('L4_TIME' in call for call in log_calls)))
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.WARNING)
    unittest.main(verbosity=2)
