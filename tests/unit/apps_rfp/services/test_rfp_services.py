"""Test consolidated services for apps_rfp."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRfpServices:
    """Test apps_rfp services."""

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

    def test_services_init_unknown_name_raises(self):
        """G2: services.__getattr__ raises AttributeError for names not in _MODULE_MAP."""
        import apps_rfp.services as svc

        with pytest.raises(AttributeError):
            _ = svc.NonExistentService

    @patch("apps_rfp.services.repo_signal_service.RepoSignalAdapter")
    def test_repo_signal_service_collect_delivery_proof(self, mock_adapter):
        """G5: collect() always populates governance['delivery_proof'] with requirement_confidence."""
        from apps_rfp.services.repo_signal_service import RepoSignalService

        mock_shared = MagicMock()
        mock_shared.captured_at = "2024-06-01"
        mock_shared.adg = {}
        mock_shared.tests = {}
        mock_shared.ci = {}
        mock_shared.governance = {}
        mock_shared.provenance = {}
        mock_shared.baseline = {}
        mock_adapter.return_value.collect.return_value = mock_shared

        service = RepoSignalService()
        snapshot = service.collect()

        assert "delivery_proof" in snapshot.governance
        proof = snapshot.governance["delivery_proof"]
        assert "requirement_confidence" in proof
        assert isinstance(proof["requirement_confidence"], float)
        assert 0.0 <= proof["requirement_confidence"] <= 1.0


@pytest.mark.unit
class TestRfpIntegrations:
    """G3: Test apps_rfp integrations (ExecutionAdapter)."""

    def test_execution_adapter_submit_happy_path(self):
        """ExecutionAdapter.submit() returns receipt with receipt_id and gate_passed=True."""
        from apps_rfp.integrations.execution_adapter import ExecutionAdapter
        from apps_rfp.types.rfp_types import RfpRequest, RfpResult

        adapter = ExecutionAdapter()
        request = RfpRequest(
            problem_statement="We need to modernize our cloud infrastructure for scale",
            trace_id="test-trace-001",
        )
        result = RfpResult(trace_id="test-trace-001", status="complete", quality_score=0.9)

        receipt = adapter.submit(request, result)

        assert receipt["receipt_id"] == "RFP-test-trace-001"
        assert receipt["status"] == "submitted"
        assert receipt["provenance"]["gate_passed"] is True
        assert receipt["app"] == "apps_rfp"

    def test_execution_adapter_submit_failed_gate(self):
        """ExecutionAdapter.submit() with gate violations sets gate_passed=False in provenance."""
        from apps_rfp.integrations.execution_adapter import ExecutionAdapter
        from apps_rfp.types.rfp_types import RfpRequest, RfpResult

        adapter = ExecutionAdapter()
        request = RfpRequest(
            problem_statement="We need to modernize our cloud infrastructure for scale",
            trace_id="fail-trace-001",
        )
        result = RfpResult(
            trace_id="fail-trace-001",
            status="failed",
            gate_violations=["missing required section"],
        )

        receipt = adapter.submit(request, result)

        assert receipt["status"] == "submitted"
        assert receipt["provenance"]["gate_passed"] is False
        assert len(adapter.get_execution_log()) == 1

    def test_execution_adapter_get_execution_log_empty(self):
        """ExecutionAdapter.get_execution_log() returns empty list before any submissions."""
        from apps_rfp.integrations.execution_adapter import ExecutionAdapter

        adapter = ExecutionAdapter()
        assert adapter.get_execution_log() == []
