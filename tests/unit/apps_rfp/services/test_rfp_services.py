"""Test apps_rfp services - comprehensive tests for key services."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRfpServices:
    """Comprehensive tests for apps_rfp services."""

    def test_capability_mapper_service_init(self):
        """Test CapabilityMapperService initialization."""
        from apps_rfp.services.capability_mapper_service import CapabilityMapperService

        service = CapabilityMapperService()
        assert service.config == {}

    def test_compliance_checker_service_init(self):
        """Test ComplianceCheckerService initialization."""
        from apps_rfp.services.compliance_checker_service import ComplianceCheckerService

        service = ComplianceCheckerService()
        assert service.config == {}

    def test_differentiation_analyzer_service_init(self):
        """Test DifferentiationAnalyzerService initialization."""
        from apps_rfp.services.differentiation_analyzer_service import DifferentiationAnalyzerService

        service = DifferentiationAnalyzerService()
        assert service.config == {}

    def test_proposal_architect_service_init(self):
        """Test ProposalArchitectService initialization."""
        from apps_rfp.services.proposal_architect_service import ProposalArchitectService

        service = ProposalArchitectService()
        assert service.config == {}

    @patch("apps_rfp.services.repo_signal_service.RepoSignalAdapter")
    def test_repo_signal_service_collect(self, mock_adapter):
        """Test RepoSignalService collect."""
        from apps_rfp.services.repo_signal_service import RepoSignalService

        mock_shared = MagicMock()
        mock_shared.captured_at = "2024-01-01"
        mock_shared.adg = {}
        mock_shared.tests = {}
        mock_shared.ci = {}
        mock_shared.governance = {}
        mock_shared.provenance = {}
        mock_shared.baseline = {}

        mock_adapter.return_value.collect.return_value = mock_shared

        service = RepoSignalService()
        snapshot = service.collect()
        assert snapshot.captured_at == "2024-01-01"

    def test_requirement_parser_service_init(self):
        """Test RequirementParserService initialization."""
        from apps_rfp.services.requirement_parser_service import RequirementParserService

        service = RequirementParserService()
        assert service.config == {}

    def test_response_generator_service_init(self):
        """Test ResponseGeneratorService initialization."""
        from apps_rfp.services.response_generator_service import ResponseGeneratorService

        service = ResponseGeneratorService()
        assert service.config == {}

    def test_risk_assessor_service_init(self):
        """Test RiskAssessorService initialization."""
        from apps_rfp.services.risk_assessor_service import RiskAssessorService

        service = RiskAssessorService()
        assert service.config == {}

    def test_submission_validator_service_init(self):
        """Test SubmissionValidatorService initialization."""
        from apps_rfp.services.submission_validator_service import SubmissionValidatorService

        service = SubmissionValidatorService()
        assert service.config == {}
