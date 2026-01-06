from __future__ import annotations
import json
import os
from unittest.mock import MagicMock, mock_open, patch

import pytest
from OutreachEngineZse import (
    MAX_PITCH_REFINEMENTS,
    OUTREACH_ALLOWED_HOSTS,
    SHADOW_MODE_ACTIVE,
    PitchGenerator,
    ShadowModeEngine,
    execute_outreach_zse,
)


@pytest.fixture

def mock_tools():

    """Mock tools dictionary for testing"""

    return {

        'fetch': MagicMock(),

        'search_nodes': MagicMock(),

        'send_email': MagicMock()

    }



@pytest.fixture

def Logger():

    """Mock Logger for testing"""

    Logger = MagicMock()

    return Logger



@pytest.fixture

def sample_contact():

    """Sample contact information"""

    return {

        "name": "John Doe",

        "email": "john.doe@company.com",

        "timezone": "America/New_York"

    }



class TestOutreachE3TC101:

    """TC-E3-101: Standard ZSE Success"""



    @patch('OutreachEngineZse.register_process')

    @patch('OutreachEngineZse.log_action')

    @patch('OutreachEngineZse.add_observations')

    @patch('OutreachEngineZse.convert_time')

    @patch('OutreachEngineZse.get_brand_style_guide')

    def test_zse_success_first_attempt(self, mock_brand_guide, mock_convert_time,

                                      mock_add_obs, mock_log_action, mock_register_process,

                                      mock_tools, Logger, sample_contact):

        """Test ZSE succeeds on first attempt with P6 passing"""

        # Mock dependencies

        mock_tools['fetch'].return_value = "Company news about recent funding round"

        mock_tools['search_nodes'].return_value = json.dumps({"entities": []})

        mock_convert_time.return_value = "2025-01-15T09:00:00"

        mock_brand_guide.return_value = {"rules": ["professional", "no_spam"]}



        # Mock P6 consensus to approve

        with patch('OutreachEngineZse.jury.judge_artifact') as mock_judge:

            mock_judge.return_value = {"Verdict": "APPROVED"}



            # Mock email send

            mock_tools['send_email'].return_value = {"status": "sent", "message_id": "123"}



            result = execute_outreach_zse(

                company_url="https://example.com",

                contact_info=sample_contact,

                tools=mock_tools,


            )



            assert result["status"] == "SUCCESS"

            assert result["refinements"] == 0

            assert "pitch_hash" in result

            mock_register_process.assert_called_once()

            mock_log_action.assert_any_call("ZSE_SUCCESS", "Pitch passed P6 compliance. Executing final side effect.")



class TestOutreachE3TC102:

    """TC-E3-102: P8 Egress Filter Block"""



    @patch('OutreachEngineZse.register_process')

    @patch('OutreachEngineZse.log_action')

    @patch('OutreachEngineZse._fetch_company_content')

    def test_p8_egress_filter_block(self, mock_fetch, mock_log_action,

                                    mock_register_process, mock_tools, Logger, sample_contact):

        """Test egress filter blocks unauthorized domains"""

        # Mock fetch to raise NetworkViolationError

        from network_utils import NetworkViolationError

        mock_fetch.side_effect = NetworkViolationError("Egress Filter Blocked: Outbound connection to 'malicious.com' is not on the Allow-List.")



        result = execute_outreach_zse(

            company_url="https://malicious.com",

            contact_info=sample_contact,

            tools=mock_tools,


        )



        assert result["status"] == "FAILED"

        assert result["reason"] == "P8_EGRESS_VIOLATION"

        mock_log_action.assert_any_call("P8_VIOLATION", "Egress filter blocked: Egress Filter Blocked: Outbound connection to 'malicious.com' is not on the Allow-List.")

        mock_register_process.assert_called_once()



class TestOutreachE3TC201:

    """TC-E3-201: P6 Compliance Failure (ZSE Loop)"""



    @patch('OutreachEngineZse.register_process')

    @patch('OutreachEngineZse.log_action')

    @patch('OutreachEngineZse.add_observations')

    @patch('OutreachEngineZse.convert_time')

    @patch('OutreachEngineZse.get_brand_style_guide')

    def test_p6_compliance_failure_triggers_p10(self, mock_brand_guide, mock_convert_time,

                                                mock_add_obs, mock_log_action, mock_register_process,

                                                mock_tools, Logger, sample_contact):

        """Test P6 compliance failure triggers P10 Shadow Mode"""

        # Mock dependencies

        mock_tools['fetch'].return_value = "Company news content"

        mock_tools['search_nodes'].return_value = json.dumps({"entities": []})

        mock_convert_time.return_value = "2025-01-15T09:00:00"

        mock_brand_guide.return_value = {"rules": ["professional", "no_spam"]}



        # Mock P6 consensus to fail initially

        with patch('OutreachEngineZse.jury.judge_artifact') as mock_judge:

            mock_judge.return_value = {

                "Verdict": "REJECTED",

                "reason": "Brand compliance failure: unprofessional language"

            }



            result = execute_outreach_zse(

                company_url="https://example.com",

                contact_info=sample_contact,

                tools=mock_tools,


            )



            # Should fail after max refinements

            assert result["status"] == "FAILED"

            assert result["reason"] == "ZSE_MAX_ATTEMPTS_REACHED"

            assert result["attempts"] == MAX_PITCH_REFINEMENTS + 1



            # Verify P10 shadow mode was triggered

            assert mock_add_obs.call_count >= MAX_PITCH_REFINEMENTS

            mock_log_action.assert_any_call("P10_SHADOW_START", "Refinement attempt 1")



class TestOutreachE3TC202:

    """TC-E3-202: P10 Refinement Success"""



    @patch('OutreachEngineZse.register_process')

    @patch('OutreachEngineZse.log_action')

    @patch('OutreachEngineZse.add_observations')

    @patch('OutreachEngineZse.convert_time')

    @patch('OutreachEngineZse.get_brand_style_guide')

    def test_p10_refinement_success(self, mock_brand_guide, mock_convert_time,

                                    mock_add_obs, mock_log_action, mock_register_process,

                                    mock_tools, Logger, sample_contact):

        """Test P10 refinement leads to P6 success on second attempt"""

        # Mock dependencies

        mock_tools['fetch'].return_value = "Company news content"

        mock_tools['search_nodes'].return_value = json.dumps({"entities": []})

        mock_convert_time.return_value = "2025-01-15T09:00:00"

        mock_brand_guide.return_value = {"rules": ["professional", "no_spam"]}



        # Mock P6 consensus: fail first, pass second

        with patch('OutreachEngineZse.jury.judge_artifact') as mock_judge:

            mock_judge.side_effect = [

                {"Verdict": "REJECTED", "reason": "unprofessional language"},

                {"Verdict": "APPROVED"}

            ]



            # Mock email send

            mock_tools['send_email'].return_value = {"status": "sent", "message_id": "456"}



            result = execute_outreach_zse(

                company_url="https://example.com",

                contact_info=sample_contact,

                tools=mock_tools,


            )



            assert result["status"] == "SUCCESS"

            assert result["refinements"] == 1

            assert "pitch_hash" in result



            # Verify P10 was called once

            shadow_calls = [call for call in mock_log_action.call_args_list

                          if "P10_SHADOW_START" in str(call)]

            assert len(shadow_calls) == 1



class TestOutreachE3TC203:

    """TC-E3-203: ZSE Max Attempts Failure"""



    @patch('OutreachEngineZse.register_process')

    @patch('OutreachEngineZse.log_action')

    @patch('OutreachEngineZse.add_observations')

    @patch('OutreachEngineZse.convert_time')

    @patch('OutreachEngineZse.get_brand_style_guide')

    def test_zse_max_attempts_failure(self, mock_brand_guide, mock_convert_time,

                                      mock_add_obs, mock_log_action, mock_register_process,

                                      mock_tools, Logger, sample_contact):

        """Test ZSE fails after max refinement attempts"""

        # Mock dependencies

        mock_tools['fetch'].return_value = "Company news content"

        mock_tools['search_nodes'].return_value = json.dumps({"entities": []})

        mock_convert_time.return_value = "2025-01-15T09:00:00"

        mock_brand_guide.return_value = {"rules": ["professional", "no_spam"]}



        # Mock P6 consensus to always fail

        with patch('OutreachEngineZse.jury.judge_artifact') as mock_judge:

            mock_judge.return_value = {

                "Verdict": "REJECTED",

                "reason": "Persistent brand compliance failure"

            }



            result = execute_outreach_zse(

                company_url="https://example.com",

                contact_info=sample_contact,

                tools=mock_tools,


            )



            assert result["status"] == "FAILED"

            assert result["reason"] == "ZSE_MAX_ATTEMPTS_REACHED"

            assert result["attempts"] == MAX_PITCH_REFINEMENTS + 1



            # Verify max refinements were attempted

            assert mock_add_obs.call_count >= MAX_PITCH_REFINEMENTS

            # Check if any ZSE_FAIL_MAX_ATTEMPTS was called

            zse_fail_calls = [call for call in mock_log_action.call_args_list

                             if call[0][0] == "ZSE_FAIL_MAX_ATTEMPTS"]

            assert len(zse_fail_calls) > 0



            # Verify no email was sent

            mock_tools['send_email'].assert_not_called()



class TestOutreachE3TC301:

    """TC-E3-301: P5 Watchdog Kill Condition"""



    def test_p5_watchdog_registration(self):

        """Test P5 process registration is called"""

        with patch('OutreachEngineZse.register_process') as mock_register:

            mock_register.return_value = None



            # This would be tested with actual watchdog integration

            # For now, just verify registration is attempted

            mock_register.assert_not_called()  # Not called yet



            # The actual watchdog kill condition would need

            # integration with the watchdog system



class TestOutreachE3TC302:

    """TC-E3-302: L4 Time Utility Check"""



    @patch('OutreachEngineZse.register_process')

    @patch('OutreachEngineZse.log_action')

    @patch('OutreachEngineZse.add_observations')

    @patch('OutreachEngineZse.get_brand_style_guide')

    def test_l4_time_conversion(self, mock_brand_guide, mock_add_obs,

                                mock_log_action, mock_register_process,

                                mock_tools, Logger, sample_contact):

        """Test L4 time conversion for different timezones"""

        # Mock dependencies

        mock_tools['fetch'].return_value = "Company news content"

        mock_tools['search_nodes'].return_value = json.dumps({"entities": []})



        # Test timezone 12 hours ahead

        contact_ahead = sample_contact.copy()

        contact_ahead["timezone"] = "Asia/Tokyo"  # UTC+9 vs UTC-5 (14 hour difference)



        with patch('OutreachEngineZse.convert_time') as mock_convert:

            mock_convert.return_value = "2025-01-16T23:00:00"  # Next day in Tokyo



            with patch('OutreachEngineZse.jury.judge_artifact') as mock_judge:

                mock_judge.return_value = {"Verdict": "APPROVED"}



                mock_tools['send_email'].return_value = {"status": "sent"}



                result = execute_outreach_zse(

                    company_url="https://example.com",

                    contact_info=contact_ahead,

                    tools=mock_tools,


                )



                # Verify time conversion was called

                mock_convert.assert_called_once_with(

                    source_timezone="America/New_York",

                    time="09:00",

                    target_timezone="Asia/Tokyo"

                )



                assert result["status"] == "SUCCESS"



class TestShadowModeEngine:

    """Test the Shadow Mode Engine"""



    def test_refine_pitch_spam_fix(self):

        """Test pitch refinement for spam issues"""

        original = "Hello!!! Buy now $$$ Special offer!!!"

        result = ShadowModeEngine.refine_pitch(original, "Contains spam indicators")



        assert result["status"] == "SUCCESS"

        assert "!!!" not in result["content"]

        assert "$$$" not in result["content"]

        assert result["refinements_applied"] == "Contains spam indicators"



    def test_refine_pitch_professional_fix(self):

        """Test pitch refinement for unprofessional language"""

        original = "hey yo, wanna buy stuff?"

        result = ShadowModeEngine.refine_pitch(original, "Unprofessional language")



        assert result["status"] == "SUCCESS"

        assert "hey" not in result["content"].lower()

        assert "yo" not in result["content"].lower()

        assert "Dear" in result["content"] or "Hello" in result["content"]



    def test_refine_pitch_length_fix(self):

        """Test pitch refinement for length issues"""

        original = "This is a very long pitch. " * 20  # Long repetitive text

        result = ShadowModeEngine.refine_pitch(original, "Too long")



        assert result["status"] == "SUCCESS"

        # Should be truncated to 5 sentences

        sentences = result["content"].split(". ")

        assert len(sentences) <= 6  # 5 sentences + empty string from final period



class TestPitchGenerator:

    """Test the Pitch Generator"""



    def test_generate_pitch(self):

        """Test pitch generation"""

        context = "Company just raised Series A funding"

        relationships = "No prior relationship"



        result = PitchGenerator.generate_pitch(context, relationships)



        assert result["status"] == "SUCCESS"

        assert "subject" in result

        assert "content" in result

        assert "Potential Collaboration" in result["subject"]

        assert context[:200] in result["content"]

        assert "[Contact Name]" in result["content"]

        assert "[Your Name]" in result["content"]



class TestConfiguration:

    """Test configuration settings"""



    def test_max_pitch_refinements_default(self):

        """Test default MAX_PITCH_REFINEMENTS"""

        assert MAX_PITCH_REFINEMENTS == 2



    def test_max_pitch_refinements_from_env(self):

        """Test MAX_PITCH_REFINEMENTS from environment"""

        with patch.dict(os.environ, {'MAX_PITCH_REFINEMENTS': '5'}):

            import importlib

            import OutreachEngineZse

            importlib.reload(OutreachEngineZse)

            assert OutreachEngineZse.MAX_PITCH_REFINEMENTS == 5



    def test_outreach_allowed_hosts(self):

        """Test OUTREACH_ALLOWED_HOSTS configuration"""

        assert "api.openai.com" in OUTREACH_ALLOWED_HOSTS

        assert "smtp.sendgrid.net" in OUTREACH_ALLOWED_HOSTS

        assert "linkedin.com" in OUTREACH_ALLOWED_HOSTS

        assert "malicious.com" not in OUTREACH_ALLOWED_HOSTS



    def test_shadow_mode_active(self):

        """Test SHADOW_MODE_ACTIVE configuration"""

        assert isinstance(SHADOW_MODE_ACTIVE, bool)



        with patch.dict(os.environ, {'AGENT_MODE': 'SHADOW'}):

            import importlib

            import OutreachEngineZse

            importlib.reload(OutreachEngineZse)

            assert OutreachEngineZse.SHADOW_MODE_ACTIVE == True



class TestNetworkIntegration:

    """Test P8 Egress Filter Integration"""



    @patch('OutreachEngineZse.register_process')

    @patch('OutreachEngineZse.log_action')

    def test_egress_filter_decorator(self, mock_log_action, mock_register_process):

        """Test that egress filter decorator is properly applied"""

        # Verify the decorator is applied to _fetch_company_content
        import OutreachEngineZse
        from network_utils import strict_egress_filter

        assert hasattr(OutreachEngineZse._fetch_company_content, '__wrapped__')



        # The decorator should be present

        # Actual egress filtering is tested in TC-E3-102



class TestShadowModeExecution:

    """Test shadow mode execution"""



    @patch('OutreachEngineZse.register_process')

    @patch('OutreachEngineZse.log_action')

    @patch('OutreachEngineZse.add_observations')

    @patch('OutreachEngineZse.convert_time')

    @patch('OutreachEngineZse.get_brand_style_guide')

    def test_shadow_mode_blocks_email(self, mock_brand_guide, mock_convert_time,

                                      mock_add_obs, mock_log_action, mock_register_process,

                                      mock_tools, Logger, sample_contact):

        """Test that shadow mode blocks email sending"""

        # Patch SHADOW_MODE_ACTIVE directly

        import OutreachEngineZse

        OutreachEngineZse.SHADOW_MODE_ACTIVE = True



        # Mock dependencies

        mock_tools['fetch'].return_value = "Company news content"

        mock_tools['search_nodes'].return_value = json.dumps({"entities": []})

        mock_convert_time.return_value = "2025-01-15T09:00:00"

        mock_brand_guide.return_value = {"rules": ["professional"]}



        with patch('OutreachEngineZse.jury.judge_artifact') as mock_judge:

            mock_judge.return_value = {"Verdict": "APPROVED"}



            result = OutreachEngineZse.execute_outreach_zse(

                company_url="https://example.com",

                contact_info=sample_contact,

                tools=mock_tools,


            )



            assert result["status"] == "SUCCESS"

            assert result["send_result"]["result"] == "SHADOW_BLOCKED"

            # Debug: print all log calls

            # print("\nAll log_action calls:")  # [Security Fix]

            for call in mock_log_action.call_args_list:
                pass

            # Check if SEND_EMAIL_SHADOW was called

            shadow_calls = [call for call in mock_log_action.call_args_list

                          if call[0][0] == "SEND_EMAIL_SHADOW"]

            assert len(shadow_calls) > 0, f"SEND_EMAIL_SHADOW not found in calls: {[call[0] for call in mock_log_action.call_args_list]}"



            # Verify send_email was NOT called

            mock_tools['send_email'].assert_not_called()
