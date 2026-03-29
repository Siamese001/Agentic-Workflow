"""
apps_rfp Services Layer — AI Proposal/RFP Generator Capabilities.

Discrete service units for requirement parsing, compliance checking, and proposal assembly.
Aligned with apps_lic services/ pattern.
"""

from apps_rfp.services.capability_mapper_service import CapabilityMapperService
from apps_rfp.services.compliance_checker_service import ComplianceCheckerService
from apps_rfp.services.differentiation_analyzer_service import DifferentiationAnalyzerService
from apps_rfp.services.proposal_architect_service import ProposalArchitectService
from apps_rfp.services.repo_signal_service import RepoSignalService
from apps_rfp.services.requirement_parser_service import RequirementParserService
from apps_rfp.services.response_generator_service import ResponseGeneratorService
from apps_rfp.services.risk_assessor_service import RiskAssessorService
from apps_rfp.services.submission_validator_service import SubmissionValidatorService

__all__ = [
    "RequirementParserService",
    "ComplianceCheckerService",
    "CapabilityMapperService",
    "ProposalArchitectService",
    "ResponseGeneratorService",
    "DifferentiationAnalyzerService",
    "RiskAssessorService",
    "SubmissionValidatorService",
    "RepoSignalService",
]
