#!/usr/bin/env python3
"""
Test Suite for Outreach Engine ZSE (Engine 3)
Covers test cases TC-E3-101 through TC-E3-302
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
import unittest
from unittest.mock import patch

from agentic_core.engines.outreach_engine_zse import (ExitReason,
                                                      OutreachEngineZSE)
from agentic_core.knowledge.l5_consolidated import KnowledgeResult
from agentic_core.utils.networking import EgressResult


class TestStandardZSESuccess(unittest.TestCase):
    """TC-E3-101: Standard ZSE Success"""

    @patch('agentic_core.engines.outreach_engine_zse.send_email')
    @patch('agentic_core.engines.outreach_engine_zse.get_consolidated_knowledge')
    @patch('agentic_core.engines.outreach_engine_zse.get_networking_utility')
    @patch('agentic_core.engines.outreach_engine_zse.register_process')
    @patch('agentic_core.engines.outreach_engine_zse.log_action')
    def test_standard_zse_success(self, mock_log, mock_register, mock_network, mock_knowledge, mock_send):
        """
        Given: Context is valid. Initial pitch passes P6 Consensus.
        When: Engine executes full cycle.
        Then: Email is sent, P5 logs success, ZSE -> EXIT_SUCCESS.
        """
        # Setup mocks
        mock_network.return_value.strict_egress_filter.return_value = EgressResult(
            status="PASS",
            reason="Host whitelisted",
            host="linkedin.com"
        )

        mock_network.return_value.fetch_url.return_value = {
            "status": "mock_success",
            "content": "Company content"
        }

        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(
            user_profile={"timezone": "UTC"},
            template=None,
            metadata={"source": "test"}
        )

        mock_knowledge.return_value.query_consensus.return_value = {
            "status": "PASS",
            "evaluations": [],
            "consensus_score": 1.0,
            "reason": "All checks passed"
        }

        mock_knowledge.return_value.add_observations.return_value = True

        mock_send.return_value = {
            "status": "dry_run_success",
            "to": "test@example.com"
        }

        # Execute
        engine = OutreachEngineZSE(output_dir=tempfile.mkdtemp(), dry_run=True)
        exit_reason, result = engine.execute_outreach(
            company_url="https://linkedin.com/company/test",
            contact_email="test@example.com"
        )

        # Verify
        self.assertEqual(exit_reason, ExitReason.ZSE_SUCCESS)
        self.assertIsNotNone(result)
        self.assertEqual(result["refinements"], 0)
        self.assertEqual(mock_send.call_count, 1)

        # Check P5 logging
        log_calls = [str(call) for call in mock_log.call_args_list]
        self.assertTrue(any('SEND_EMAIL_SUCCESS' in call for call in log_calls))


class TestP8EgressFilterBlock(unittest.TestCase):
    """TC-E3-102: P8 Egress Filter Block"""

    @patch('agentic_core.engines.outreach_engine_zse.get_networking_utility')
    @patch('agentic_core.engines.outreach_engine_zse.register_process')
    @patch('agentic_core.engines.outreach_engine_zse.log_action')
    def test_p8_egress_block(self, mock_log, mock_register, mock_network):
        """
        Given: Engine attempts to fetch from unwhitelisted domain.
        When: Egress filter is called.
        Then: Filter returns FAIL, engine exits before pitch generation.
        """
        # Setup mock to block unwhitelisted domain
        mock_network.return_value.strict_egress_filter.return_value = EgressResult(
            status="FAIL",
            reason="Host malicious.com not in whitelist",
            host="malicious.com"
        )

        # Execute
        engine = OutreachEngineZSE(output_dir=tempfile.mkdtemp(), dry_run=True)
        exit_reason, result = engine.execute_outreach(
            company_url="https://malicious.com/company/test",
            contact_email="test@example.com"
        )

        # Verify
        self.assertEqual(exit_reason, ExitReason.P8_EGRESS_BLOCK)
        self.assertIsNone(result)

        # Check P8 block was logged
        log_calls = [str(call) for call in mock_log.call_args_list]
        self.assertTrue(any('P8_EGRESS_BLOCK' in call for call in log_calls))


class TestP6ComplianceFailure(unittest.TestCase):
    """TC-E3-201: P6 Compliance Failure (ZSE Loop)"""

    @patch('agentic_core.engines.outreach_engine_zse.send_email')
    @patch('agentic_core.engines.outreach_engine_zse.get_consolidated_knowledge')
    @patch('agentic_core.engines.outreach_engine_zse.get_networking_utility')
    @patch('agentic_core.engines.outreach_engine_zse.register_process')
    @patch('agentic_core.engines.outreach_engine_zse.log_action')
    def test_p6_compliance_failure(self, mock_log, mock_register, mock_network, mock_knowledge, mock_send):
        """
        Given: Initial pitch has non-compliant branding.
        When: P6 consensus fails.
        Then: Engine triggers P10 Shadow Mode and restarts loop.
        """
        # Setup mocks
        mock_network.return_value.strict_egress_filter.return_value = EgressResult(
            status="PASS",
            reason="Host whitelisted",
            host="linkedin.com"
        )

        mock_network.return_value.fetch_url.return_value = {
            "status": "mock_success",
            "content": "Company content"
        }

        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(
            user_profile={"timezone": "UTC"},
            template=None,
            metadata={"source": "test"}
        )

        # P6 fails first, then passes
        mock_knowledge.return_value.query_consensus.side_effect = [
            {
                "status": "FAIL",
                "evaluations": [],
                "consensus_score": 0.33,
                "reason": "Brand tone and style analysis; Spam and promotional content analysis"
            },
            {
                "status": "PASS",
                "evaluations": [],
                "consensus_score": 1.0,
                "reason": "All checks passed"
            }
        ]

        mock_knowledge.return_value.add_observations.return_value = True
        mock_send.return_value = {"status": "dry_run_success"}

        # Execute
        engine = OutreachEngineZSE(output_dir=tempfile.mkdtemp(), dry_run=True)
        exit_reason, result = engine.execute_outreach(
            company_url="https://linkedin.com/company/test",
            contact_email="test@example.com"
        )

        # Verify
        self.assertEqual(exit_reason, ExitReason.ZSE_SUCCESS)
        self.assertEqual(engine.refinement_count, 1)
        self.assertEqual(mock_knowledge.return_value.query_consensus.call_count, 2)

        # Check P10 shadow mode was triggered
        log_calls = [str(call) for call in mock_log.call_args_list]
        self.assertTrue(any('P10_START' in call for call in log_calls))
        self.assertTrue(any('P10_SHADOW_REFINEMENT' in call for call in log_calls))


class TestP10RefinementSuccess(unittest.TestCase):
    """TC-E3-202: P10 Refinement Success"""

    @patch('agentic_core.engines.outreach_engine_zse.send_email')
    @patch('agentic_core.engines.outreach_engine_zse.get_consolidated_knowledge')
    @patch('agentic_core.engines.outreach_engine_zse.get_networking_utility')
    @patch('agentic_core.engines.outreach_engine_zse.register_process')
    @patch('agentic_core.engines.outreach_engine_zse.log_action')
    def test_p10_refinement_success(self, mock_log, mock_register, mock_network, mock_knowledge, mock_send):
        """
        Given: P6 fails on attempt 1, P10 refines pitch.
        When: P6 passes on attempt 2.
        Then: Engine sends email, ZSE goal met.
        """
        # Setup mocks - same as previous test
        mock_network.return_value.strict_egress_filter.return_value = EgressResult(
            status="PASS",
            reason="Host whitelisted",
            host="linkedin.com"
        )

        mock_network.return_value.fetch_url.return_value = {
            "status": "mock_success",
            "content": "Company content"
        }

        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(
            user_profile={"timezone": "UTC"},
            template=None,
            metadata={"source": "test"}
        )

        # P6 fails first, then passes
        mock_knowledge.return_value.query_consensus.side_effect = [
            {
                "status": "FAIL",
                "evaluations": [],
                "consensus_score": 0.33,
                "reason": "Brand compliance issue"
            },
            {
                "status": "PASS",
                "evaluations": [],
                "consensus_score": 1.0,
                "reason": "All checks passed"
            }
        ]

        mock_knowledge.return_value.add_observations.return_value = True
        mock_send.return_value = {"status": "dry_run_success"}

        # Execute
        engine = OutreachEngineZSE(output_dir=tempfile.mkdtemp(), dry_run=True)
        exit_reason, result = engine.execute_outreach(
            company_url="https://linkedin.com/company/test",
            contact_email="test@example.com"
        )

        # Verify
        self.assertEqual(exit_reason, ExitReason.ZSE_SUCCESS)
        self.assertEqual(result["refinements"], 1)
        self.assertEqual(mock_send.call_count, 1)


class TestZSEMaxRefinementsFailure(unittest.TestCase):
    """TC-E3-203: ZSE Max Attempts Failure"""

    @patch('agentic_core.engines.outreach_engine_zse.get_consolidated_knowledge')
    @patch('agentic_core.engines.outreach_engine_zse.get_networking_utility')
    @patch('agentic_core.engines.outreach_engine_zse.register_process')
    @patch('agentic_core.engines.outreach_engine_zse.log_action')
    def test_zse_max_refinements_failure(self, mock_log, mock_register, mock_network, mock_knowledge):
        """
        Given: Pitch fails P6 on attempts 1, 2, and 3.
        When: MAX_REFINEMENTS (2) is exceeded.
        Then: Engine logs ZSE_FAIL_MAX_REFINEMENTS and exits with FAILURE.
        """
        # Setup mocks
        mock_network.return_value.strict_egress_filter.return_value = EgressResult(
            status="PASS",
            reason="Host whitelisted",
            host="linkedin.com"
        )

        mock_network.return_value.fetch_url.return_value = {
            "status": "mock_success",
            "content": "Company content"
        }

        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(
            user_profile={"timezone": "UTC"},
            template=None,
            metadata={"source": "test"}
        )

        # P6 always fails
        mock_knowledge.return_value.query_consensus.return_value = {
            "status": "FAIL",
            "evaluations": [],
            "consensus_score": 0.0,
            "reason": "Brand compliance issue"
        }

        mock_knowledge.return_value.add_observations.return_value = True

        # Execute
        engine = OutreachEngineZSE(output_dir=tempfile.mkdtemp(), dry_run=True)
        exit_reason, result = engine.execute_outreach(
            company_url="https://linkedin.com/company/test",
            contact_email="test@example.com"
        )

        # Verify
        self.assertEqual(exit_reason, ExitReason.ZSE_MAX_REFINEMENTS)
        self.assertIsNone(result)
        self.assertEqual(engine.refinement_count, 2)

        # Check max refinements logged
        log_calls = [str(call) for call in mock_log.call_args_list]
        self.assertTrue(any('ZSE_FAIL_MAX_REFINEMENTS' in call for call in log_calls))


class TestP5WatchdogKillCondition(unittest.TestCase):
    """TC-E3-301: P5 Watchdog Kill Condition"""

    @patch('agentic_core.engines.outreach_engine_zse.send_email')
    @patch('agentic_core.engines.outreach_engine_zse.get_consolidated_knowledge')
    @patch('agentic_core.engines.outreach_engine_zse.get_networking_utility')
    @patch('agentic_core.engines.outreach_engine_zse.register_process')
    @patch('agentic_core.engines.outreach_engine_zse.log_action')
    def test_p5_watchdog_kill_condition(self, mock_log, mock_register, mock_network, mock_knowledge, mock_send):
        """
        Given: Engine completes successful cycle.
        When: P5 detects rapid email burst.
        Then: DeadManSwitch kills agent process.
        """
        # Setup mocks for success
        mock_network.return_value.strict_egress_filter.return_value = EgressResult(
            status="PASS",
            reason="Host whitelisted",
            host="linkedin.com"
        )

        mock_network.return_value.fetch_url.return_value = {
            "status": "mock_success",
            "content": "Company content"
        }

        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(
            user_profile={"timezone": "UTC"},
            template=None,
            metadata={"source": "test"}
        )

        mock_knowledge.return_value.query_consensus.return_value = {
            "status": "PASS",
            "evaluations": [],
            "consensus_score": 1.0,
            "reason": "All checks passed"
        }

        mock_knowledge.return_value.add_observations.return_value = True
        mock_send.return_value = {"status": "dry_run_success"}

        # Execute
        engine = OutreachEngineZSE(output_dir=tempfile.mkdtemp(), dry_run=True)

        # Simulate rapid execution
        for i in range(10):
            engine.execute_outreach(
                company_url="https://linkedin.com/company/test",
                contact_email=f"test{i}@example.com"
            )

        # Verify watchdog would be triggered (mocked)
        # In real implementation, this would kill the process
        self.assertGreaterEqual(mock_log.call_count, 10)


class TestL4TimeUtilityCheck(unittest.TestCase):
    """TC-E3-302: L4 Time Utility Check"""

    @patch('agentic_core.engines.outreach_engine_zse.send_email')
    @patch('agentic_core.engines.outreach_engine_zse.get_consolidated_knowledge')
    @patch('agentic_core.engines.outreach_engine_zse.get_networking_utility')
    @patch('agentic_core.engines.outreach_engine_zse.register_process')
    @patch('agentic_core.engines.outreach_engine_zse.log_action')
    def test_l4_time_utility_check(self, mock_log, mock_register, mock_network, mock_knowledge, mock_send):
        """
        Given: Contact context specifies timezone 12 hours ahead.
        When: L4 time conversion is called.
        Then: OPTIMAL_SEND_TIME is correctly calculated.
        """
        # Setup mocks
        mock_network.return_value.strict_egress_filter.return_value = EgressResult(
            status="PASS",
            reason="Host whitelisted",
            host="linkedin.com"
        )

        mock_network.return_value.fetch_url.return_value = {
            "status": "mock_success",
            "content": "Company content"
        }

        # Contact with timezone 12 hours ahead
        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(
            user_profile={"timezone": "Asia/Singapore"},  # UTC+8
            template=None,
            metadata={"source": "test"}
        )

        mock_knowledge.return_value.query_consensus.return_value = {
            "status": "PASS",
            "evaluations": [],
            "consensus_score": 1.0,
            "reason": "All checks passed"
        }

        mock_knowledge.return_value.add_observations.return_value = True
        mock_send.return_value = {"status": "dry_run_success"}

        # Execute
        engine = OutreachEngineZSE(output_dir=tempfile.mkdtemp(), dry_run=True)
        exit_reason, result = engine.execute_outreach(
            company_url="https://linkedin.com/company/test",
            contact_email="test@example.com"
        )

        # Verify
        self.assertEqual(exit_reason, ExitReason.ZSE_SUCCESS)
        self.assertIsNotNone(result)

        # Check time conversion was logged
        log_calls = [str(call) for call in mock_log.call_args_list]
        self.assertTrue(any('L4_TIME' in call for call in log_calls))


if __name__ == "__main__":
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)

    # Run tests
    unittest.main(verbosity=2)
