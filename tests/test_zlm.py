import logging

import os
from unittest.mock import MagicMock, mock_open, patch

import pytest
from canon_validator_engine import MAX_P6_ATTEMPTS, execute_dependency_refactor_zlm


@pytest.fixture

def mock_tools():

    """Mock tools dictionary for testing"""

    return {

        'issues_get_detail': MagicMock(),

        'search_records': MagicMock(),

        'edit_file': MagicMock(),

        'commit': MagicMock(),

        'string_set': MagicMock(),

        'add_observations': MagicMock()

    }



@pytest.fixture

def mock_logger():

    """Mock logger for testing"""

    logger = MagicMock()

    return logger



class TestZLMTC101:

    """TC-ZLM-101: Standard Successful Merge"""



    @patch('canon_validator_engine.register_process')

    @patch('canon_validator_engine.log_action')

    @patch('canon_validator_engine.execute_regression_suite')

    def test_zlm_success_first_attempt(self, mock_regression, mock_log_action, mock_register_process, mock_tools, mock_logger, monkeypatch):

        """Test ZLM succeeds on first attempt"""

        # Mock the underlying function to return success

        def mock_refactor(*args, **kwargs):

            return {"status": "SUCCESS", "reason": "PASSED"}



        # Mock regression to pass

        mock_regression.return_value = {"status": "SUCCESS"}



        monkeypatch.setattr("canon_validator_engine.execute_dependency_refactor", mock_refactor)



        result = execute_dependency_refactor_zlm(

            issue_id="TEST-001",

            target_file="test_file.py",

            tools=mock_tools,

            logger=mock_logger

        )



        assert result["status"] == "SUCCESS"

        assert mock_register_process.called

        assert mock_log_action.called

        assert mock_logger.info.call_count >= 2  # At least start and success messages

        mock_tools['add_observations'].assert_called_once()



class TestZLMTC201:

    """TC-ZLM-201: P2 Failure, P6 Single-Pass Fix"""



    @patch('canon_validator_engine.register_process')

    @patch('canon_validator_engine.log_action')

    @patch('canon_validator_engine.execute_regression_suite')

    @patch('builtins.open', new_callable=mock_open, read_data="# Original code")

    def test_zlm_success_after_single_retry(self, mock_file, mock_regression, mock_log_action, mock_register_process, mock_tools, mock_logger, monkeypatch):

        """Test ZLM succeeds after P6 self-correction on first retry"""

        call_count = 0



        def mock_refactor(*args, **kwargs):

            nonlocal call_count

            call_count += 1

            if call_count == 1:

                return {"status": "FAILED", "reason": "SANDBOX_VERIFICATION_FAILURE", "details": "Test failed"}

            return {"status": "SUCCESS", "reason": "PASSED"}



        def mock_propose_fix(*args, **kwargs):

            return {"status": "SUCCESS", "fixed_code": "# Fixed code"}



        # Mock regression to pass

        mock_regression.return_value = {"status": "SUCCESS"}



        monkeypatch.setattr("canon_validator_engine.execute_dependency_refactor", mock_refactor)

        monkeypatch.setattr("canon_validator_engine.jury.propose_fix", mock_propose_fix)



        result = execute_dependency_refactor_zlm(

            issue_id="TEST-002",

            target_file="test_file.py",

            tools=mock_tools,

            logger=mock_logger

        )



        assert result["status"] == "SUCCESS"

        assert call_count == 2  # Failed once, then succeeded

        assert mock_logger.warning.call_count >= 1  # Warning for P2 failure

        assert mock_logger.info.call_count >= 2  # P6 fix and success

        assert mock_tools['add_observations'].call_count >= 2  # Failure + success logs



class TestZLMTC202:

    """TC-ZLM-202: P2 Failure, P6 Multi-Pass Fix"""



    @patch('canon_validator_engine.register_process')

    @patch('canon_validator_engine.log_action')

    @patch('canon_validator_engine.execute_regression_suite')

    @patch('builtins.open', new_callable=mock_open, read_data="# Original code")

    def test_zlm_success_after_multiple_retries(self, mock_file, mock_regression, mock_log_action, mock_register_process, mock_tools, mock_logger, monkeypatch):

        """Test ZLM succeeds after multiple P6 attempts"""

        call_count = 0

        fix_count = 0



        def mock_refactor(*args, **kwargs):

            nonlocal call_count

            call_count += 1

            if call_count <= 2:

                return {"status": "FAILED", "reason": "SANDBOX_VERIFICATION_FAILURE", "details": f"Test failed {call_count}"}

            return {"status": "SUCCESS", "reason": "PASSED"}



        def mock_propose_fix(*args, **kwargs):

            nonlocal fix_count

            fix_count += 1

            if fix_count == 1:

                return {"status": "FAILED"}  # First fix attempt fails

            elif fix_count == 2:

                return {"status": "SUCCESS", "fixed_code": "# Partially fixed code"}

            return {"status": "SUCCESS", "fixed_code": "# Fully fixed code"}



        # Mock regression to pass

        mock_regression.return_value = {"status": "SUCCESS"}



        monkeypatch.setattr("canon_validator_engine.execute_dependency_refactor", mock_refactor)

        monkeypatch.setattr("canon_validator_engine.jury.propose_fix", mock_propose_fix)



        result = execute_dependency_refactor_zlm(

            issue_id="TEST-003",

            target_file="test_file.py",

            tools=mock_tools,

            logger=mock_logger

        )



        assert result["status"] == "SUCCESS"

        assert call_count == 3  # 2 failures + 1 success

        assert mock_logger.warning.call_count >= 2  # 2 P2 failures

        assert mock_logger.info.call_count >= 2  # 2 P6 attempts



class TestZLMTC203:

    """TC-ZLM-203: ZLM Hard Stop Condition"""



    @patch('canon_validator_engine.register_process')

    @patch('canon_validator_engine.log_action')

    @patch('canon_validator_engine.execute_regression_suite')

    @patch('builtins.open', new_callable=mock_open, read_data="# Original code")

    def test_zlm_max_attempts_reached(self, mock_file, mock_regression, mock_log_action, mock_register_process, mock_tools, mock_logger, monkeypatch):

        """Test ZLM fails after max P6 attempts"""

        def mock_refactor(*args, **kwargs):

            return {"status": "FAILED", "reason": "SANDBOX_VERIFICATION_FAILURE", "details": "Test failed"}



        def mock_propose_fix(*args, **kwargs):

            return {"status": "FAILED"}  # P6 cannot fix



        # Mock regression to pass (but will never reach it due to P2 failures)

        mock_regression.return_value = {"status": "SUCCESS"}



        monkeypatch.setattr("canon_validator_engine.execute_dependency_refactor", mock_refactor)

        monkeypatch.setattr("canon_validator_engine.jury.propose_fix", mock_propose_fix)



        result = execute_dependency_refactor_zlm(

            issue_id="TEST-004",

            target_file="test_file.py",

            tools=mock_tools,

            logger=mock_logger

        )



        assert result["status"] == "FAILED"

        assert result["reason"] == "ZLM_MAX_ATTEMPTS_REACHED"

        assert result["attempts"] == MAX_P6_ATTEMPTS

        assert mock_logger.critical.call_count >= 1  # Critical log for max attempts



class TestZLMTC301:

    """TC-ZLM-301: P5 Logging Integrity"""



    @patch('canon_validator_engine.register_process')

    @patch('canon_validator_engine.log_action')

    @patch('canon_validator_engine.execute_regression_suite')

    @patch('builtins.open', new_callable=mock_open, read_data="# Original code")

    def test_p5_logging_integrity(self, mock_file, mock_regression, mock_log_action, mock_register_process, mock_tools, mock_logger, monkeypatch):

        """Test P5 logs all major events"""

        call_count = 0



        def mock_refactor(*args, **kwargs):

            nonlocal call_count

            call_count += 1

            if call_count == 1:

                return {"status": "FAILED", "reason": "SANDBOX_VERIFICATION_FAILURE", "details": "Test failed"}

            return {"status": "SUCCESS", "reason": "PASSED"}



        def mock_propose_fix(*args, **kwargs):

            return {"status": "SUCCESS", "fixed_code": "# Fixed code"}



        # Mock regression to pass

        mock_regression.return_value = {"status": "SUCCESS"}



        monkeypatch.setattr("canon_validator_engine.execute_dependency_refactor", mock_refactor)

        monkeypatch.setattr("canon_validator_engine.jury.propose_fix", mock_propose_fix)



        result = execute_dependency_refactor_zlm(

            issue_id="TEST-005",

            target_file="test_file.py",

            tools=mock_tools,

            logger=mock_logger

        )



        # Verify P5 registration

        mock_register_process.assert_called_once()

        mock_log_action.assert_any_call("P5_PROCESS_REGISTERED", "CanonValidatorEngine ZLM started for TEST-005")



        # Verify all major events were logged

        assert mock_logger.info.call_count >= 4  # Start, P2 attempts, P6 fix, success

        assert mock_logger.warning.call_count >= 1  # P2 failure



class TestZLMTC302:

    """TC-ZLM-302: P7 File Integrity Check"""



    @patch('canon_validator_engine.register_process')

    @patch('canon_validator_engine.log_action')

    @patch('canon_validator_engine.execute_regression_suite')

    @patch('builtins.open', new_callable=mock_open, read_data="# Original code")

    def test_p7_file_integrity(self, mock_file, mock_regression, mock_log_action, mock_register_process, mock_tools, mock_logger, monkeypatch):

        """Test P6 fix only modifies target file, not canonical files"""

        call_count = 0



        def mock_refactor(*args, **kwargs):

            nonlocal call_count

            call_count += 1

            if call_count == 1:

                return {"status": "FAILED", "reason": "SANDBOX_VERIFICATION_FAILURE", "details": "Test failed"}

            return {"status": "SUCCESS", "reason": "PASSED"}



        def mock_propose_fix(*args, **kwargs):

            return {"status": "SUCCESS", "fixed_code": "# Fixed code"}



        # Mock regression to pass

        mock_regression.return_value = {"status": "SUCCESS"}



        monkeypatch.setattr("canon_validator_engine.execute_dependency_refactor", mock_refactor)

        monkeypatch.setattr("canon_validator_engine.jury.propose_fix", mock_propose_fix)



        result = execute_dependency_refactor_zlm(

            issue_id="TEST-006",

            target_file="test_file.py",

            tools=mock_tools,

            logger=mock_logger

        )



        # Verify only target file was opened for writing

        mock_file.assert_called_with("test_file.py", 'w', encoding='utf-8')



        # Ensure canonical files like core_utils.py were NOT modified

        all_open_calls = [call[0][0] for call in mock_file.call_args_list]

        assert "test_file.py" in all_open_calls

        assert "core_utils.py" not in all_open_calls



class TestZLMTC303:

    """TC-ZLM-303: L5 Audit Trail"""



    @patch('canon_validator_engine.register_process')

    @patch('canon_validator_engine.log_action')

    @patch('canon_validator_engine.execute_regression_suite')

    @patch('builtins.open', new_callable=mock_open, read_data="# Original code")

    def test_l5_audit_trail(self, mock_file, mock_regression, mock_log_action, mock_register_process, mock_tools, mock_logger, monkeypatch):

        """Test L5 maintains complete audit trail"""

        call_count = 0



        def mock_refactor(*args, **kwargs):

            nonlocal call_count

            call_count += 1

            if call_count == 1:

                return {"status": "FAILED", "reason": "SANDBOX_VERIFICATION_FAILURE", "details": "Test failed"}

            return {"status": "SUCCESS", "reason": "PASSED"}



        def mock_propose_fix(*args, **kwargs):

            return {"status": "SUCCESS", "fixed_code": "# Fixed code"}



        # Mock regression: fail first, then pass

        mock_regression.side_effect = [

            {"status": "FAILED", "reason": "REGRESSION_TEST_FAILURE", "stderr": "Test failed"},

            {"status": "SUCCESS"}

        ]



        monkeypatch.setattr("canon_validator_engine.execute_dependency_refactor", mock_refactor)

        monkeypatch.setattr("canon_validator_engine.jury.propose_fix", mock_propose_fix)



        result = execute_dependency_refactor_zlm(

            issue_id="TEST-007",

            target_file="test_file.py",

            tools=mock_tools,

            logger=mock_logger

        )



        # Verify L5 observations were added

        assert mock_tools['add_observations'].call_count >= 2



        # Check the observation entities and content

        observation_calls = mock_tools['add_observations'].call_args_list



        # First call should log the failure - add_observations is called with a list as the first arg

        first_call_list = observation_calls[0][0][0]

        assert first_call_list[0]["entityName"] == "ZLM_TEST-007"

        assert "P2_FAIL_ATTEMPT_1" in first_call_list[0]["observations"]



        # Second call should log the fix application

        second_call_list = observation_calls[1][0][0]

        assert second_call_list[0]["entityName"] == "ZLM_TEST-007"

        assert "P6_FIX_APPLIED" in second_call_list[0]["observations"][0]



        # Third call should log the regression failure (on attempt 2)

        if len(observation_calls) > 2:

            third_call_list = observation_calls[2][0][0]

            assert third_call_list[0]["entityName"] == "ZLM_TEST-007"

            assert "REGRESSION_FAIL_ATTEMPT_2" in third_call_list[0]["observations"][0]



        # Fourth call should log the final fix application

        if len(observation_calls) > 3:

            fourth_call_list = observation_calls[3][0][0]

            assert fourth_call_list[0]["entityName"] == "ZLM_TEST-007"

            assert "P6_FIX_APPLIED" in fourth_call_list[0]["observations"][0]



        # Fifth call should log the success

        if len(observation_calls) > 4:

            fifth_call_list = observation_calls[4][0][0]

            assert fifth_call_list[0]["entityName"] == "ZLM_TEST-007"

            assert "ZLM_SUCCESS" in fifth_call_list[0]["observations"][0]



class TestZLMNonRecoverable:

    """Test non-recoverable failures"""



    @patch('canon_validator_engine.register_process')

    @patch('canon_validator_engine.log_action')

    def test_zlm_non_recoverable_failure(self, mock_log_action, mock_register_process, mock_tools, mock_logger, monkeypatch):

        """Test ZLM fails immediately for non-recoverable errors (P1, GPG)"""

        def mock_refactor(*args, **kwargs):

            return {"status": "FAILED", "reason": "AST_VALIDATION_FAILURE", "details": "Syntax error"}



        monkeypatch.setattr("canon_validator_engine.execute_dependency_refactor", mock_refactor)



        result = execute_dependency_refactor_zlm(

            issue_id="TEST-008",

            target_file="test_file.py",

            tools=mock_tools,

            logger=mock_logger

        )



        assert result["status"] == "FAILED"

        assert result["reason"] == "AST_VALIDATION_FAILURE"

        assert mock_logger.error.call_count >= 1

        mock_tools['add_observations'].assert_called_once()



class TestZLMTC204:

    """TC-ZLM-204: Regression Failure Trigger"""



    @patch('canon_validator_engine.register_process')

    @patch('canon_validator_engine.log_action')

    @patch('canon_validator_engine.execute_regression_suite')

    def test_regression_failure_triggers_p6(self, mock_regression, mock_log_action, mock_register_process, mock_tools, mock_logger, monkeypatch):

        """Test that regression failure triggers P6 self-correction"""

        call_count = 0



        def mock_refactor(*args, **kwargs):

            nonlocal call_count

            call_count += 1

            # P2 passes on first attempt

            return {"status": "SUCCESS", "reason": "PASSED"}



        def mock_propose_fix(*args, **kwargs):

            return {"status": "SUCCESS", "fixed_code": "# Fixed regression issue"}



        # Regression fails on first attempt, passes on second

        mock_regression.side_effect = [

            {"status": "FAILED", "reason": "REGRESSION_TEST_FAILURE", "stderr": "Test failure"},

            {"status": "SUCCESS"}

        ]



        monkeypatch.setattr("canon_validator_engine.execute_dependency_refactor", mock_refactor)

        monkeypatch.setattr("canon_validator_engine.jury.propose_fix", mock_propose_fix)



        result = execute_dependency_refactor_zlm(

            issue_id="TEST-204",

            target_file="test_file.py",

            tools=mock_tools,

            logger=mock_logger

        )



        assert result["status"] == "SUCCESS"

        assert mock_regression.call_count == 2  # Called twice, fails first then passes

        assert mock_logger.warning.call_count >= 1  # Warning for regression failure

        assert mock_logger.info.call_count >= 1  # Info for P6 fix application



class TestZLMTC205:

    """TC-ZLM-205: P6 Fix introduces Regression"""



    @patch('canon_validator_engine.register_process')

    @patch('canon_validator_engine.log_action')

    @patch('canon_validator_engine.execute_regression_suite')

    @patch('builtins.open', new_callable=mock_open, read_data="# Original code")

    def test_p6_fix_introduces_regression(self, mock_file, mock_regression, mock_log_action, mock_register_process, mock_tools, mock_logger, monkeypatch):

        """Test that P6 fix causing regression triggers another P6 attempt"""

        call_count = 0



        def mock_refactor(*args, **kwargs):

            nonlocal call_count

            call_count += 1

            if call_count == 1:

                return {"status": "FAILED", "reason": "SANDBOX_VERIFICATION_FAILURE", "details": "Initial error"}

            elif call_count == 2:

                # After P6 fix, P2 passes but regression will fail

                return {"status": "SUCCESS", "reason": "PASSED"}

            else:

                return {"status": "SUCCESS", "reason": "PASSED"}



        def mock_propose_fix(*args, **kwargs):

            return {"status": "SUCCESS", "fixed_code": "# Fixed code with regression"}



        # Regression sequence: fails (after P6 fix), passes (after second P6 fix)

        mock_regression.side_effect = [

            {"status": "FAILED", "reason": "REGRESSION_TEST_FAILURE", "stderr": "Regression introduced"},

            {"status": "SUCCESS"}

        ]



        monkeypatch.setattr("canon_validator_engine.execute_dependency_refactor", mock_refactor)

        monkeypatch.setattr("canon_validator_engine.jury.propose_fix", mock_propose_fix)



        result = execute_dependency_refactor_zlm(

            issue_id="TEST-205",

            target_file="test_file.py",

            tools=mock_tools,

            logger=mock_logger

        )



        assert result["status"] == "SUCCESS"

        assert call_count == 3  # Initial fail + 2 retries

        assert mock_regression.call_count == 2  # 2 regression checks (on attempts 2 and 3)

        assert mock_logger.warning.call_count >= 2  # 2 warnings (P2 fail + regression fail)



class TestZLMTC206:

    """TC-ZLM-206: P6 Max Attempts Failure"""



    @patch('canon_validator_engine.register_process')

    @patch('canon_validator_engine.log_action')

    @patch('canon_validator_engine.execute_regression_suite')

    @patch('builtins.open', new_callable=mock_open, read_data="# Original code")

    def test_max_attempts_with_regression_failures(self, mock_file, mock_regression, mock_log_action, mock_register_process, mock_tools, mock_logger, monkeypatch):

        """Test max attempts reached when P6 fixes keep failing regression"""

        call_count = 0



        def mock_refactor(*args, **kwargs):

            nonlocal call_count

            call_count += 1

            if call_count == 1:

                return {"status": "FAILED", "reason": "SANDBOX_VERIFICATION_FAILURE", "details": "Initial error"}

            else:

                return {"status": "SUCCESS", "reason": "PASSED"}  # P2 passes after fixes



        def mock_propose_fix(*args, **kwargs):

            return {"status": "SUCCESS", "fixed_code": "# Fixed code that breaks regression"}



        # Regression always fails

        mock_regression.return_value = {"status": "FAILED", "reason": "REGRESSION_TEST_FAILURE", "stderr": "Persistent regression"}



        monkeypatch.setattr("canon_validator_engine.execute_dependency_refactor", mock_refactor)

        monkeypatch.setattr("canon_validator_engine.jury.propose_fix", mock_propose_fix)



        result = execute_dependency_refactor_zlm(

            issue_id="TEST-206",

            target_file="test_file.py",

            tools=mock_tools,

            logger=mock_logger

        )



        assert result["status"] == "FAILED"

        assert result["reason"] == "ZLM_MAX_ATTEMPTS_REACHED"

        assert result["attempts"] == MAX_P6_ATTEMPTS

        assert mock_logger.critical.call_count >= 1  # Critical log for max attempts



class TestZLMTC304:

    """TC-ZLM-304: P5 Logging of Regression Failure"""



    @patch('canon_validator_engine.register_process')

    @patch('canon_validator_engine.log_action')

    @patch('canon_validator_engine.execute_regression_suite')

    def test_p5_logging_regression_cycle(self, mock_regression, mock_log_action, mock_register_process, mock_tools, mock_logger, monkeypatch):

        """Test P5 logs all regression cycle events"""

        call_count = 0



        def mock_refactor(*args, **kwargs):

            nonlocal call_count

            call_count += 1

            if call_count == 1:

                return {"status": "SUCCESS", "reason": "PASSED"}  # P2 passes

            return {"status": "SUCCESS", "reason": "PASSED"}



        def mock_propose_fix(*args, **kwargs):

            return {"status": "SUCCESS", "fixed_code": "# Fixed regression"}



        # Regression sequence: fails, then passes

        mock_regression.side_effect = [

            {"status": "FAILED", "reason": "REGRESSION_TEST_FAILURE", "stderr": "Test broke"},

            {"status": "SUCCESS"}

        ]



        monkeypatch.setattr("canon_validator_engine.execute_dependency_refactor", mock_refactor)

        monkeypatch.setattr("canon_validator_engine.jury.propose_fix", mock_propose_fix)



        result = execute_dependency_refactor_zlm(

            issue_id="TEST-304",

            target_file="test_file.py",

            tools=mock_tools,

            logger=mock_logger

        )



        assert result["status"] == "SUCCESS"



        # Verify all major events were logged

        assert mock_logger.info.call_count >= 3  # P2 pass, P6 fix, final success

        assert mock_logger.warning.call_count >= 1  # Regression failure



        # Verify P5 registration

        mock_register_process.assert_called_once()

        mock_log_action.assert_called_with("P5_PROCESS_REGISTERED", "CanonValidatorEngine ZLM started for TEST-304")



class TestZLMConfiguration:

    """Test ZLM configuration"""



    def test_max_p6_attempts_default(self):

        """Test MAX_P6_ATTEMPTS has correct default"""

        assert MAX_P6_ATTEMPTS == 3



    @patch.dict(os.environ, {'MAX_P6_ATTEMPTS': '5'})

    def test_max_p6_attempts_from_env(self):

        """Test MAX_P6_ATTEMPTS can be configured via environment"""

        # Reload the module to pick up env var

        import importlib

        import canon_validator_engine

        importlib.reload(canon_validator_engine)

        assert canon_validator_engine.MAX_P6_ATTEMPTS == 5



    def test_regression_suite_path_default(self):

        """Test REGRESSION_SUITE_PATH has correct default"""

        from canon_validator_engine import REGRESSION_SUITE_PATH

        assert REGRESSION_SUITE_PATH == "tests/"



    @patch.dict(os.environ, {'REGRESSION_SUITE_PATH': 'custom/tests/'})

    def test_regression_suite_path_from_env(self):

        """Test REGRESSION_SUITE_PATH can be configured via environment"""

        import importlib

        import canon_validator_engine

        importlib.reload(canon_validator_engine)

        assert canon_validator_engine.REGRESSION_SUITE_PATH == "custom/tests/"

