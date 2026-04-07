"""
apps_rfp Services Layer — AI Proposal/RFP Generator Capabilities.

Discrete service units for requirement parsing, compliance checking, and proposal assembly.
Aligned with apps_lic services/ pattern.
"""

from __future__ import annotations

from .capability_mapper_service import CapabilityMapperService
from .compliance_checker_service import ComplianceCheckerService
from .differentiation_analyzer_service import DifferentiationAnalyzerService
from .proposal_architect_service import ProposalArchitectService
from .repo_signal_service import RepoSignalService
from .requirement_parser_service import RequirementParserService
from .response_generator_service import ResponseGeneratorService
from .risk_assessor_service import RiskAssessorService
from .submission_validator_service import SubmissionValidatorService

__all__ = [
    "CapabilityMapperService",
    "ComplianceCheckerService",
    "DifferentiationAnalyzerService",
    "ProposalArchitectService",
    "RepoSignalService",
    "RequirementParserService",
    "ResponseGeneratorService",
    "RiskAssessorService",
    "SubmissionValidatorService",
]
