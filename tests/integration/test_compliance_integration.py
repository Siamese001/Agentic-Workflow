"""
Test Suite for Compliance Integration

Integration tests ensuring the UnifiedOrchestrator correctly invokes
the CredentialScannerAgent when running in COMPLIANCE mode.

Risk 4: Hardcoded Credential Detection Integration
"""

from unittest.mock import patch

from agentic_core.L3_orchestration.OrchestratorAgent import OrchestratorAgent


class test_compliance_integration:
    """
    Integration tests ensuring the UnifiedOrchestrator correctly invokes
    the CredentialScannerAgent when running in COMPLIANCE mode.
    """

    def test_orchestrator_compliance_mode_calls_scanner(self):
        """
        Verify that running the orchestrator in COMPLIANCE mode instantiates
        and calls the CredentialScannerAgent.
        """
        with patch(
            "agentic_core.L5_safety.validators.CredentialScannerAgent.CredentialScannerAgent"
        ) as MockScanner:
            # Setup Mock Scanner instance
            mock_scanner_instance = MockScanner.return_value
            mock_scanner_instance.scan_for_credentials.return_value = {
                "status": "success",
                "total_matches": 0,
                "matches": [],
                "summary": {"by_severity": {"high": 0, "medium": 0, "low": 0}},
                "recommendations": ["✅ No high-priority credential leaks detected"],
            }

            orch = OrchestratorAgent(mode="compliance")

            # Execute in Compliance Mode
            result = orch.run_agent("TestAgent", dry_run=True)

            # Verify Scanner was initialized and called
            MockScanner.assert_called()
            mock_scanner_instance.scan_for_credentials.assert_called_once()

            # Verify result metadata
            assert result.metadata.get("credential_scan") == "complete"

    def test_high_severity_credentials_fail_compliance(self):
        """
        Verify that if CredentialScanner finds high severity secrets,
        the Orchestrator reports a failure status.
        """
        with patch(
            "agentic_core.L5_safety.validators.CredentialScannerAgent.CredentialScannerAgent"
        ) as MockScanner:
            # Setup Mock Scanner to find a secret
            mock_scanner_instance = MockScanner.return_value
            mock_scanner_instance.scan_for_credentials.return_value = {
                "status": "success",
                "total_matches": 3,
                "matches": [
                    {"type": "aws_access_key", "severity": "high"},
                    {"type": "github_token", "severity": "high"},
                    {"type": "generic_secret", "severity": "medium"},
                ],
                "summary": {"by_severity": {"high": 2, "medium": 1, "low": 0}},
                "recommendations": ["🚨 HIGH PRIORITY: Remove all hardcoded credentials"],
            }

            orch = OrchestratorAgent(mode="compliance")
            result = orch.run_agent("TestAgent", dry_run=True)

            # Result should reflect the findings
            assert result.status == "FAIL"
            assert result.violations_found == 3
            assert result.metadata.get("high_severity_count") == 2

    def test_zero_credentials_pass_compliance(self):
        """
        Verify that zero credentials results in PASS status.
        """
        with patch(
            "agentic_core.L5_safety.validators.CredentialScannerAgent.CredentialScannerAgent"
        ) as MockScanner:
            mock_scanner_instance = MockScanner.return_value
            mock_scanner_instance.scan_for_credentials.return_value = {
                "status": "success",
                "total_matches": 0,
                "matches": [],
                "summary": {"by_severity": {"high": 0, "medium": 0, "low": 0}},
                "recommendations": ["✅ No high-priority credential leaks detected"],
            }

            orch = OrchestratorAgent(mode="compliance")
            result = orch.run_agent("TestAgent", dry_run=True)

            assert result.status == "PASS"
            assert result.violations_found == 0
            assert result.success is True

    def test_medium_severity_warns_compliance(self):
        """
        Verify that medium severity credentials result in WARN status.
        """
        with patch(
            "agentic_core.L5_safety.validators.CredentialScannerAgent.CredentialScannerAgent"
        ) as MockScanner:
            mock_scanner_instance = MockScanner.return_value
            mock_scanner_instance.scan_for_credentials.return_value = {
                "status": "success",
                "total_matches": 2,
                "matches": [
                    {"type": "generic_secret", "severity": "medium"},
                    {"type": "jwt_token", "severity": "medium"},
                ],
                "summary": {"by_severity": {"high": 0, "medium": 2, "low": 0}},
                "recommendations": ["Use environment variables for secrets"],
            }

            orch = OrchestratorAgent(mode="compliance")
            result = orch.run_agent("TestAgent", dry_run=True)

            assert result.status == "WARN"
            assert result.violations_found == 2
            assert result.success is True  # WARN still counts as success

    def test_credential_count_in_agent_result(self):
        """
        Verify the credential count is included in AgentResult metadata.
        """
        with patch(
            "agentic_core.L5_safety.validators.CredentialScannerAgent.CredentialScannerAgent"
        ) as MockScanner:
            mock_scanner_instance = MockScanner.return_value
            mock_scanner_instance.scan_for_credentials.return_value = {
                "status": "success",
                "total_matches": 5,
                "matches": [],
                "summary": {"by_severity": {"high": 1, "medium": 2, "low": 2}},
                "recommendations": [],
            }

            orch = OrchestratorAgent(mode="compliance")
            result = orch.run_agent("TestAgent", dry_run=True)

            assert result.metadata.get("total_credentials") == 5
            assert result.metadata.get("high_severity_count") == 1

    def test_scanner_error_handling(self):
        """
        Verify that scanner errors are handled gracefully.
        """
        with patch(
            "agentic_core.L5_safety.validators.CredentialScannerAgent.CredentialScannerAgent"
        ) as MockScanner:
            mock_scanner_instance = MockScanner.return_value
            mock_scanner_instance.scan_for_credentials.side_effect = Exception("Scanner failed")

            orch = OrchestratorAgent(mode="compliance")
            result = orch.run_agent("TestAgent", dry_run=True)

            assert result.status == "ERROR"
            assert result.errors == 1
            assert "Credential scan error" in result.message
