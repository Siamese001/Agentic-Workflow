#!/usr/bin/env python3
"""
Resume Engine L5 - Validation Layer
Comprehensive validation infrastructure for resume generation
"""

from .validation_engine import (
    ValidationRule,
    ValidationEngine,
    JDEnforcementValidator,
    PreFlightValidator
)

from .rg_injection_detection import (
    InjectionType,
    InjectionResult,
    ResumeInjectionDetector,
    detect_resume_injection,
    validate_resume_sections
)

from .rg_failure_classifier import (
    FailureCategory,
    FailureSeverity,
    FailureDetails,
    ClassificationResult,
    ResumeFailureClassifier,
    classify_resume_failure,
    get_recovery_strategy
)

from .rg_validation_toolkit import (
    ValidationLevel,
    ValidationCategory,
    ValidationIssue,
    ValidationReport,
    ResumeValidationToolkit,
    validate_resume_content,
    get_validation_summary
)

# Safety validation - temporarily excluded due to missing RG_capabilities dependency
# from .rg_safety_validator import (
#     SafetyViolation,
#     SafetyReport,
#     ContentSafetyValidator
# )
# NOTE: rg_safety_validator requires RG_capabilities module - pre-existing technical debt

__all__ = [
    # Original validation engine
    'ValidationRule',
    'ValidationEngine',
    'JDEnforcementValidator',
    'PreFlightValidator',
    
    # Injection detection
    'InjectionType',
    'InjectionResult',
    'ResumeInjectionDetector',
    'detect_resume_injection',
    'validate_resume_sections',
    
    # Failure classification
    'FailureCategory',
    'FailureSeverity',
    'FailureDetails',
    'ClassificationResult',
    'ResumeFailureClassifier',
    'classify_resume_failure',
    'get_recovery_strategy',
    
    # Validation toolkit
    'ValidationLevel',
    'ValidationCategory',
    'ValidationIssue',
    'ValidationReport',
    'ResumeValidationToolkit',
    'validate_resume_content',
    'get_validation_summary',
    
    # Safety validation - temporarily excluded due to missing RG_capabilities dependency
    # 'SafetyViolation',
    # 'SafetyReport', 
    # 'ContentSafetyValidator'
]
