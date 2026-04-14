"""apps_rfp Services Layer — lazy public exports only."""

from importlib import import_module
from typing import Any

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

_MODULE_MAP = {
    "CapabilityMapperService": "apps_rfp.services.capability_mapper_service",
    "ComplianceCheckerService": "apps_rfp.services.compliance_checker_service",
    "DifferentiationAnalyzerService": "apps_rfp.services.differentiation_analyzer_service",
    "ProposalArchitectService": "apps_rfp.services.proposal_architect_service",
    "RepoSignalService": "apps_rfp.services.repo_signal_service",
    "RequirementParserService": "apps_rfp.services.requirement_parser_service",
    "ResponseGeneratorService": "apps_rfp.services.response_generator_service",
    "RiskAssessorService": "apps_rfp.services.risk_assessor_service",
    "SubmissionValidatorService": "apps_rfp.services.submission_validator_service",
}


def __getattr__(name: str) -> Any:
    module_name = _MODULE_MAP.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(module_name)
    value = getattr(module, name)
    globals()[name] = value
    return value
