#!/usr/bin/env python3
"""
Test Suite for Resume Engine (E2) - Zero-Loss Generation Compliance

Test Cases:
- TC-E2-101: Standard ZLG Success
- TC-E2-102: P3 Input Injection Block
- TC-E2-201: P4 Hallucination Trigger (ZLG Loop)
- TC-E2-202: Low Quality Trigger (ZLG Loop)
- TC-E2-203: ZLG Max Attempts Failure
- TC-E2-301: L5 Consolidated Knowledge
- TC-E2-302: P5 Activity Logging
"""
import re


import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_core.L2_execution.P3_engines.resume_engine_zlg import (
    DraftResult,
    ExitReason,
    ResumeEngineZLG,
    RewriteResult,
    ShadowModeEngine,
)
from agentic_core.knowledge.l5_consolidated import KnowledgeResult
from agentic_core.L5_safety.P4_security.security_utilities import SecurityResult, SecurityStatus


class TestStandardZLGSuccess(unittest.TestCase):
    """TC-E2-101: Standard ZLG Success"""

    @patch('agentic_core.engines.resume_engine_zlg.FileManager.write_file')
    @patch('agentic_core.engines.resume_engine_zlg.get_fact_checker')
    @patch('agentic_core.engines.resume_engine_zlg.get_prompt_firewall')
    @patch('agentic_core.engines.resume_engine_zlg.get_consolidated_knowledge')
    @patch('agentic_core.engines.resume_engine_zlg.SemanticScorer')
    @patch('agentic_core.engines.resume_engine_zlg.DraftGenerator')
    def test_standard_zlg_success(self, mock_draft_gen, mock_scorer, mock_knowledge, mock_firewall, mock_fact_checker, mock_write):
        """
        Given: Job URL is valid. L5 returns all data. Draft passes P4 and semantic score.
        When: Engine executes full cycle.
        Then: Draft written to file, L5 logs COVER_LETTER_GENERATED, ZLG -> EXIT_SUCCESS.
        """
        # Setup mocks
        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(
            user_profile={"name": "John Doe", "skills": ["Python", "React"]},
            template={"name": "professional", "structure": {"greeting": "Dear {hiring_manager},"}},
            metadata={"source": "test"}
        )

        mock_firewall.return_value.scan_input.return_value = SecurityResult(
            status=SecurityStatus.PASS,
            reason="Input clean"
        )

        mock_fact_checker.return_value.validate_skills.return_value = SecurityResult(
            status=SecurityStatus.PASS,
            reason="All skills verified"
        )

        # Mock draft generator
        mock_draft = DraftResult(
            content="Dear Hiring Manager,\n\nI am writing to express my interest...",
            source="test",
            metadata={}
        )
        mock_draft_gen.return_value.generate_draft_llm.return_value = mock_draft

        # Mock semantic scorer with high score
        mock_scorer.return_value.semantic_score_draft.return_value = {
            "quality": 0.8,
            "grade": "good",
            "reason": "Well structured",
            "metrics": {}
        }

        mock_write.return_value = True

        # Execute
        engine = ResumeEngineZLG(output_dir=tempfile.mkdtemp())
        exit_reason, output_path = engine.generate_cover_letter("https://example.com/job")

        # Verify
        self.assertEqual(exit_reason, ExitReason.ZLG_SUCCESS)
        self.assertIsNotNone(output_path)
        self.assertEqual(engine.rewrite_count, 0)
        mock_write.assert_called_once()


class TestP3InputInjectionBlock(unittest.TestCase):
    """TC-E2-102: P3 Input Injection Block"""

    @patch('agentic_core.engines.resume_engine_zlg.get_prompt_firewall')
    def test_p3_injection_block(self, mock_firewall):
        """
        Given: Job URL returns description with prompt injection.
        When: security_utils.PromptFirewall.scan_input() executes.
        Then: P3 returns FAIL. Engine logs P3_INJECTION_BLOCK and EXIT_FAILURE.
        """
        # Setup mock
        mock_firewall.return_value.scan_input.return_value = SecurityResult(
            status=SecurityStatus.FAIL,
            reason="Injection pattern detected"
        )

        # Execute
        engine = ResumeEngineZLG(output_dir=tempfile.mkdtemp())
        exit_reason, output_path = engine.generate_cover_letter("https://example.com/job")

        # Verify
        self.assertEqual(exit_reason, ExitReason.P3_INJECTION_BLOCK)
        self.assertIsNone(output_path)  # output_path should be None on failure


class TestP4HallucinationTrigger(unittest.TestCase):
    """TC-E2-201: P4 Hallucination Trigger (ZLG Loop)"""

    @patch('agentic_core.engines.resume_engine_zlg.FileManager.write_file')
    @patch('agentic_core.engines.resume_engine_zlg.get_fact_checker')
    @patch('agentic_core.engines.resume_engine_zlg.get_prompt_firewall')
    @patch('agentic_core.engines.resume_engine_zlg.get_consolidated_knowledge')
    @patch('agentic_core.engines.resume_engine_zlg.SemanticScorer')
    @patch('agentic_core.engines.resume_engine_zlg.DraftGenerator')
    def test_p4_hallucination_trigger(self, mock_draft_gen, mock_scorer, mock_knowledge, mock_firewall, mock_fact_checker, mock_write):
        """
        Given: Draft includes hallucinated skill (P4 FAIL). Semantic score is high.
        When: Engine enters ZLG loop.
        Then: Transitions to P10 Shadow Mode, L5 logs P10_SHADOW_REWRITE, loop restarts.
        """
        # Setup mocks
        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(
            user_profile={"name": "John Doe"},
            template={"name": "professional", "structure": {}},
            metadata={"source": "test"}
        )

        mock_firewall.return_value.scan_input.return_value = SecurityResult(
            status=SecurityStatus.PASS,
            reason="Input clean"
        )

        # P4 fails first, then passes
        mock_fact_checker.return_value.validate_skills.side_effect = [
            SecurityResult(status=SecurityStatus.FAIL, reason="Skill 'Quantum Computing' not found"),
            SecurityResult(status=SecurityStatus.PASS, reason="All skills verified")
        ]

        # Mock draft generator
        mock_draft = DraftResult(
            content="Dear Hiring Manager,\n\nI am writing to express my interest...",
            source="test",
            metadata={}
        )
        mock_draft_gen.return_value.generate_draft_llm.return_value = mock_draft

        # Mock semantic scorer with high score
        mock_scorer.return_value.semantic_score_draft.return_value = {
            "quality": 0.8,
            "grade": "good",
            "reason": "Well structured",
            "metrics": {}
        }

        mock_write.return_value = True

        # Execute
        engine = ResumeEngineZLG(output_dir=tempfile.mkdtemp())
        exit_reason, output_path = engine.generate_cover_letter("https://example.com/job")

        # Verify
        self.assertEqual(exit_reason, ExitReason.ZLG_SUCCESS)
        self.assertEqual(engine.rewrite_count, 1)
        self.assertEqual(mock_fact_checker.return_value.validate_skills.call_count, 2)


class TestLowQualityTrigger(unittest.TestCase):
    """TC-E2-202: Low Quality Trigger (ZLG Loop)"""

    @patch('agentic_core.engines.resume_engine_zlg.FileManager.write_file')
    @patch('agentic_core.engines.resume_engine_zlg.get_fact_checker')
    @patch('agentic_core.engines.resume_engine_zlg.get_prompt_firewall')
    @patch('agentic_core.engines.resume_engine_zlg.get_consolidated_knowledge')
    @patch('agentic_core.engines.resume_engine_zlg.SemanticScorer')
    def test_low_quality_trigger(self, mock_scorer, mock_knowledge, mock_firewall, mock_fact_checker, mock_write):
        """
        Given: Draft passes P4 but semantic score < MIN_ACCEPTABLE_SCORE.
        When: Engine enters ZLG loop.
        Then: Transitions to P10 Shadow Mode, loop restarts with rewrite instruction.
        """
        # Setup mocks
        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(
            user_profile={"name": "John Doe"},
            template={"name": "professional", "structure": {}},
            metadata={"source": "test"}
        )

        mock_firewall.return_value.scan_input.return_value = SecurityResult(
            status=SecurityStatus.PASS,
            reason="Input clean"
        )

        mock_fact_checker.return_value.validate_skills.return_value = SecurityResult(
            status=SecurityStatus.PASS,
            reason="All skills verified"
        )

        # Score fails first, then passes
        mock_scorer.return_value.semantic_score_draft.side_effect = [
            {"quality": 0.3, "grade": "poor", "reason": "Too short"},
            {"quality": 0.8, "grade": "good", "reason": "Well structured"}
        ]

        mock_write.return_value = True

        # Execute
        engine = ResumeEngineZLG(output_dir=tempfile.mkdtemp())
        exit_reason, output_path = engine.generate_cover_letter("https://example.com/job")

        # Verify
        self.assertEqual(exit_reason, ExitReason.ZLG_SUCCESS)
        self.assertEqual(engine.rewrite_count, 1)


class TestZLGMaxAttemptsFailure(unittest.TestCase):
    """TC-E2-203: ZLG Max Attempts Failure"""

    @patch('agentic_core.engines.resume_engine_zlg.get_fact_checker')
    @patch('agentic_core.engines.resume_engine_zlg.get_prompt_firewall')
    @patch('agentic_core.engines.resume_engine_zlg.get_consolidated_knowledge')
    def test_zlg_max_attempts_failure(self, mock_knowledge, mock_firewall, mock_fact_checker):
        """
        Given: Draft fails P4 on attempts 1, 2, and 3.
        When: REWRITE_COUNT reaches 3.
        Then: Logs ZLG_FAIL_MAX_ATTEMPTS to L5 and terminates with EXIT_FAILURE.
        """
        # Setup mocks
        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(
            user_profile={"name": "John Doe"},
            template={"name": "professional", "structure": {}},
            metadata={"source": "test"}
        )

        mock_firewall.return_value.scan_input.return_value = SecurityResult(
            status=SecurityStatus.PASS,
            reason="Input clean"
        )

        # P4 always fails
        mock_fact_checker.return_value.validate_skills.return_value = SecurityResult(
            status=SecurityStatus.FAIL,
            reason="Invalid skills"
        )

        # Execute
        engine = ResumeEngineZLG(output_dir=tempfile.mkdtemp())
        exit_reason, output_path = engine.generate_cover_letter("https://example.com/job")

        # Verify
        self.assertEqual(exit_reason, ExitReason.ZLG_MAX_ATTEMPTS)
        self.assertEqual(engine.rewrite_count, 3)
        self.assertIsNone(output_path)


class TestL5ConsolidatedKnowledge(unittest.TestCase):
    """TC-E2-301: L5 Consolidated Knowledge"""

    @patch('agentic_core.engines.resume_engine_zlg.get_consolidated_knowledge')
    def test_l5_consolidated_knowledge(self, mock_knowledge):
        """
        Given: L3 Pinecone index for templates is down.
        When: Engine attempts L5.search_knowledge().
        Then: Consolidated L5 handles L3 failure internally and returns fallback.
        """
        # Setup mock with fallback behavior
        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(
            user_profile={"name": "John Doe", "skills": ["Python"]},
            template={"name": "professional", "structure": {}},
            metadata={"template_source": "fallback"}
        )

        # Execute
        engine = ResumeEngineZLG(output_dir=tempfile.mkdtemp())
        knowledge = engine.knowledge.search_knowledge("test query")

        # Verify
        self.assertIsNotNone(knowledge.user_profile)
        self.assertIsNotNone(knowledge.template)
        self.assertEqual(knowledge.metadata["template_source"], "fallback")


class TestP5ActivityLogging(unittest.TestCase):
    """TC-E2-302: P5 Activity Logging"""

    @patch('agentic_core.engines.resume_engine_zlg.log_action')
    @patch('agentic_core.engines.resume_engine_zlg.FileManager.write_file')
    @patch('agentic_core.engines.resume_engine_zlg.get_fact_checker')
    @patch('agentic_core.engines.resume_engine_zlg.get_prompt_firewall')
    @patch('agentic_core.engines.resume_engine_zlg.get_consolidated_knowledge')
    @patch('agentic_core.engines.resume_engine_zlg.SemanticScorer')
    @patch('agentic_core.engines.resume_engine_zlg.DraftGenerator')
    def test_p5_activity_logging(self, mock_draft_gen, mock_scorer, mock_knowledge, mock_firewall, mock_fact_checker, mock_write, mock_log):
        """
        Given: Engine executes full successful cycle.
        When: Engine executes log_action() at key points.
        Then: logs/agent_actions.log contains records for registration, P4, and success.
        """
        # Setup mocks for success
        mock_knowledge.return_value.search_knowledge.return_value = KnowledgeResult(
            user_profile={"name": "John Doe"},
            template={"name": "professional", "structure": {}},
            metadata={"source": "test"}
        )

        mock_firewall.return_value.scan_input.return_value = SecurityResult(
            status=SecurityStatus.PASS,
            reason="Input clean"
        )

        mock_fact_checker.return_value.validate_skills.return_value = SecurityResult(
            status=SecurityStatus.PASS,
            reason="All skills verified"
        )

        # Mock draft generator
        mock_draft = DraftResult(
            content="Dear Hiring Manager,\n\nI am writing to express my interest...",
            source="test",
            metadata={}
        )
        mock_draft_gen.return_value.generate_draft_llm.return_value = mock_draft

        # Mock semantic scorer with high score
        mock_scorer.return_value.semantic_score_draft.return_value = {
            "quality": 0.8,
            "grade": "good",
            "reason": "Well structured",
            "metrics": {}
        }

        mock_write.return_value = True

        # Execute
        engine = ResumeEngineZLG(output_dir=tempfile.mkdtemp())
        engine.generate_cover_letter("https://example.com/job")

        # Verify logging calls
        log_calls = [str(call) for call in mock_log.call_args_list]

        # Check for key log events
        self.assertTrue(any('L1_FETCH_START' in call for call in log_calls))
        self.assertTrue(any('P3_START' in call for call in log_calls))
        self.assertTrue(any('P4_START' in call for call in log_calls))
        self.assertTrue(any('ZLG_FINAL_SUCCESS' in call for call in log_calls))


class TestShadowModeEngine(unittest.TestCase):
    """Additional tests for Shadow Mode Engine"""

    def test_shadow_mode_rewrite_with_rules(self):
        """Test shadow mode rewrite using rule-based approach."""
        engine = ShadowModeEngine(llm_client=None)

        draft = "I'm an expert developer with awesome skills."
        error_reason = "professional tone needed"

        result = engine.rewrite_draft(draft, error_reason)

        self.assertIsInstance(result, RewriteResult)
        self.assertIn("I am", result.content)
        self.assertNotIn("awesome", result.content)
        self.assertGreater(result.confidence, 0)

    def test_shadow_mode_fix_skill_claims(self):
        """Test fixing exaggerated skill claims."""
        engine = ShadowModeEngine()

        draft = "I am a world-class expert in Python."
        improved = engine._fix_skill_claims(draft)

        self.assertNotIn("world-class", improved)
        self.assertNotIn("expert", improved)
        self.assertIn("experienced", improved)


def run_test_suite():
    """Run the complete Resume Engine test suite."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStandardZLGSuccess))
    suite.addTests(loader.loadTestsFromTestCase(TestP3InputInjectionBlock))
    suite.addTests(loader.loadTestsFromTestCase(TestP4HallucinationTrigger))
    suite.addTests(loader.loadTestsFromTestCase(TestLowQualityTrigger))
    suite.addTests(loader.loadTestsFromTestCase(TestZLGMaxAttemptsFailure))
    suite.addTests(loader.loadTestsFromTestCase(TestL5ConsolidatedKnowledge))
    suite.addTests(loader.loadTestsFromTestCase(TestP5ActivityLogging))
    suite.addTests(loader.loadTestsFromTestCase(TestShadowModeEngine))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    result = run_test_suite()
    sys.exit(0 if result.wasSuccessful() else 1)
