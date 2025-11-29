"""
Resume Engine Failure Classifier Module

Corollary to outreach_engine/l5/lic_failure_classifier.py
Specialized for resume processing failure classification and analysis.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class FailureCategory(Enum):
    """Categories of resume processing failures."""
    INPUT_VALIDATION = "input_validation"
    EXTRACTION_FAILURE = "extraction_failure"
    CLEANING_FAILURE = "cleaning_failure"
    QUANTIFICATION_FAILURE = "quantification_failure"
    REWRITE_FAILURE = "rewrite_failure"
    SKILL_MAPPING_FAILURE = "skill_mapping_failure"
    ASSEMBLY_FAILURE = "assembly_failure"
    FORMATTING_FAILURE = "formatting_failure"
    VALIDATION_FAILURE = "validation_failure"
    SYSTEM_ERROR = "system_error"
    LLM_ERROR = "llm_error"
    TIMEOUT_ERROR = "timeout_error"
    MEMORY_ERROR = "memory_error"


class FailureSeverity(Enum):
    """Severity levels for processing failures."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FailureDetails:
    """Detailed information about a processing failure."""
    category: FailureCategory
    severity: FailureSeverity
    error_message: str
    step_name: str
    input_data_hash: str
    timestamp: datetime
    retry_count: int = 0
    context: Optional[Dict[str, Any]] = None
    recovery_suggestions: List[str] = None
    
    def __post_init__(self):
        if self.recovery_suggestions is None:
            self.recovery_suggestions = []


@dataclass
class ClassificationResult:
    """Result of failure classification analysis."""
    is_recoverable: bool
    should_retry: bool
    max_retries: int
    fallback_strategy: Optional[str]
    estimated_recovery_time: Optional[float]
    requires_manual_intervention: bool


class ResumeFailureClassifier:
    """Classifies and analyzes resume processing failures."""
    
    def __init__(self):
        self.failure_patterns = self._init_failure_patterns()
        self.recovery_strategies = self._init_recovery_strategies()
    
    def _init_failure_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize failure pattern recognition rules."""
        return {
            # Input validation failures
            "input_validation": {
                "patterns": [
                    r"invalid.*format",
                    r"missing.*required.*field",
                    r"malformed.*input",
                    r"validation.*failed"
                ],
                "severity": FailureSeverity.HIGH,
                "recoverable": True,
                "max_retries": 2
            },
            # Extraction failures
            "extraction_failure": {
                "patterns": [
                    r"extraction.*failed",
                    r"cannot.*extract",
                    r"parsing.*error",
                    r"section.*not.*found"
                ],
                "severity": FailureSeverity.MEDIUM,
                "recoverable": True,
                "max_retries": 3
            },
            # Cleaning failures
            "cleaning_failure": {
                "patterns": [
                    r"cleaning.*failed",
                    r"cannot.*clean",
                    r"formatting.*error",
                    r"content.*corrupted"
                ],
                "severity": FailureSeverity.MEDIUM,
                "recoverable": True,
                "max_retries": 2
            },
            # Quantification failures
            "quantification_failure": {
                "patterns": [
                    r"quantification.*failed",
                    r"cannot.*quantify",
                    r"metric.*error",
                    r"calculation.*failed"
                ],
                "severity": FailureSeverity.MEDIUM,
                "recoverable": True,
                "max_retries": 3
            },
            # Rewrite failures
            "rewrite_failure": {
                "patterns": [
                    r"rewrite.*failed",
                    r"cannot.*rewrite",
                    r"content.*generation.*failed",
                    r"llm.*rewrite.*error"
                ],
                "severity": FailureSeverity.HIGH,
                "recoverable": True,
                "max_retries": 2
            },
            # Skill mapping failures
            "skill_mapping_failure": {
                "patterns": [
                    r"skill.*mapping.*failed",
                    r"cannot.*map.*skills",
                    r"taxonomy.*error",
                    r"skill.*classification.*failed"
                ],
                "severity": FailureSeverity.MEDIUM,
                "recoverable": True,
                "max_retries": 2
            },
            # Assembly failures
            "assembly_failure": {
                "patterns": [
                    r"assembly.*failed",
                    r"cannot.*assemble",
                    r"section.*assembly.*error",
                    r"structure.*failed"
                ],
                "severity": FailureSeverity.HIGH,
                "recoverable": True,
                "max_retries": 2
            },
            # Formatting failures
            "formatting_failure": {
                "patterns": [
                    r"formatting.*failed",
                    r"cannot.*format",
                    r"layout.*error",
                    r"template.*error"
                ],
                "severity": FailureSeverity.LOW,
                "recoverable": True,
                "max_retries": 1
            },
            # Validation failures
            "validation_failure": {
                "patterns": [
                    r"validation.*failed",
                    r"cannot.*validate",
                    r"quality.*check.*failed",
                    r"compliance.*error"
                ],
                "severity": FailureSeverity.MEDIUM,
                "recoverable": True,
                "max_retries": 1
            },
            # System errors
            "system_error": {
                "patterns": [
                    r"system.*error",
                    r"os.*error",
                    r"file.*system.*error",
                    r"permission.*denied"
                ],
                "severity": FailureSeverity.CRITICAL,
                "recoverable": False,
                "max_retries": 0
            },
            # LLM errors
            "llm_error": {
                "patterns": [
                    r"llm.*error",
                    r"model.*error",
                    r"api.*error",
                    r"rate.*limit.*exceeded"
                ],
                "severity": FailureSeverity.HIGH,
                "recoverable": True,
                "max_retries": 3
            },
            # Timeout errors
            "timeout_error": {
                "patterns": [
                    r"timeout",
                    r"timed.*out",
                    r"deadline.*exceeded",
                    r"operation.*timeout"
                ],
                "severity": FailureSeverity.MEDIUM,
                "recoverable": True,
                "max_retries": 1
            },
            # Memory errors
            "memory_error": {
                "patterns": [
                    r"memory.*error",
                    r"out.*of.*memory",
                    r"allocation.*failed",
                    r"buffer.*overflow"
                ],
                "severity": FailureSeverity.CRITICAL,
                "recoverable": False,
                "max_retries": 0
            }
        }
    
    def _init_recovery_strategies(self) -> Dict[str, List[str]]:
        """Initialize recovery strategies for different failure types."""
        return {
            "input_validation": [
                "Reformat input data",
                "Add missing required fields",
                "Validate against schema",
                "Use default values for optional fields"
            ],
            "extraction_failure": [
                "Try alternative parsing method",
                "Use different section detection",
                "Apply text preprocessing",
                "Use fallback extraction rules"
            ],
            "cleaning_failure": [
                "Apply gentler cleaning rules",
                "Preserve original formatting",
                "Use character-level cleaning",
                "Skip problematic sections"
            ],
            "quantification_failure": [
                "Use simplified quantification",
                "Apply conservative metrics",
                "Skip complex calculations",
                "Use default quantification rules"
            ],
            "rewrite_failure": [
                "Use simpler rewrite prompts",
                "Apply content preservation rules",
                "Use fallback rewrite templates",
                "Reduce rewrite complexity"
            ],
            "skill_mapping_failure": [
                "Use broader skill categories",
                "Apply manual skill mapping",
                "Use generic skill taxonomy",
                "Preserve original skill descriptions"
            ],
            "assembly_failure": [
                "Use simpler assembly logic",
                "Apply section-by-section assembly",
                "Use fallback assembly templates",
                "Preserve original structure"
            ],
            "formatting_failure": [
                "Use basic formatting",
                "Apply minimal styling",
                "Use plain text format",
                "Skip complex formatting"
            ],
            "validation_failure": [
                "Use relaxed validation rules",
                "Skip optional validations",
                "Apply basic quality checks",
                "Use manual validation override"
            ],
            "llm_error": [
                "Switch to backup model",
                "Apply exponential backoff",
                "Use cached responses",
                "Switch to rule-based processing"
            ],
            "timeout_error": [
                "Increase timeout limits",
                "Process in smaller chunks",
                "Use async processing",
                "Skip time-consuming operations"
            ]
        }
    
    def classify_failure(self, error_message: str, step_name: str, 
                         input_data_hash: str, context: Optional[Dict[str, Any]] = None) -> FailureDetails:
        """
        Classify a processing failure and provide detailed analysis.
        
        Args:
            error_message: The error message to classify
            step_name: Name of the processing step where failure occurred
            input_data_hash: Hash of input data for tracking
            context: Additional context about the failure
            
        Returns:
            FailureDetails with classification and recovery suggestions
        """
        error_message_lower = error_message.lower()
        
        # Find matching failure category
        detected_category = None
        
        for category, config in self.failure_patterns.items():
            for pattern in config["patterns"]:
                if re.search(pattern, error_message_lower):
                    detected_category = FailureCategory(category)
                    break
            if detected_category:
                break
        
        # Default to system error if no pattern matches
        if not detected_category:
            detected_category = FailureCategory.SYSTEM_ERROR
        
        # Get severity and recoverability
        category_key = detected_category.value
        severity = self.failure_patterns.get(category_key, {}).get("severity", FailureSeverity.MEDIUM)
        
        # Generate recovery suggestions
        recovery_suggestions = self.recovery_strategies.get(category_key, ["Contact support", "Review input data"])
        
        return FailureDetails(
            category=detected_category,
            severity=severity,
            error_message=error_message,
            step_name=step_name,
            input_data_hash=input_data_hash,
            timestamp=datetime.now(),
            context=context,
            recovery_suggestions=recovery_suggestions
        )
    
    def get_classification_result(self, failure_details: FailureDetails, 
                                  retry_count: int = 0) -> ClassificationResult:
        """
        Get classification result with recovery recommendations.
        
        Args:
            failure_details: Details of the failure
            retry_count: Current retry attempt
            
        Returns:
            ClassificationResult with recovery strategy
        """
        category_key = failure_details.category.value
        config = self.failure_patterns.get(category_key, {})
        
        is_recoverable = config.get("recoverable", False)
        max_retries = config.get("max_retries", 0)
        should_retry = is_recoverable and retry_count < max_retries
        
        # Determine fallback strategy
        fallback_strategy = None
        if not should_retry and is_recoverable:
            fallback_strategy = f"fallback_{category_key}"
        
        # Estimate recovery time (in seconds)
        recovery_time = None
        if is_recoverable:
            recovery_time = {
                FailureSeverity.LOW: 5,
                FailureSeverity.MEDIUM: 15,
                FailureSeverity.HIGH: 30,
                FailureSeverity.CRITICAL: 60
            }.get(failure_details.severity, 15)
        
        requires_manual_intervention = (
            failure_details.severity == FailureSeverity.CRITICAL or
            not is_recoverable or
            retry_count >= max_retries
        )
        
        return ClassificationResult(
            is_recoverable=is_recoverable,
            should_retry=should_retry,
            max_retries=max_retries,
            fallback_strategy=fallback_strategy,
            estimated_recovery_time=recovery_time,
            requires_manual_intervention=requires_manual_intervention
        )
    
    def batch_classify_failures(self, failures: List[Tuple[str, str, str, Optional[Dict[str, Any]]]]) -> List[FailureDetails]:
        """
        Classify multiple failures in batch.
        
        Args:
            failures: List of (error_message, step_name, input_data_hash, context) tuples
            
        Returns:
            List of FailureDetails for each failure
        """
        results = []
        
        for error_message, step_name, input_data_hash, context in failures:
            failure_details = self.classify_failure(error_message, step_name, input_data_hash, context)
            results.append(failure_details)
        
        return results
    
    def get_failure_statistics(self, failures: List[FailureDetails]) -> Dict[str, Any]:
        """
        Get statistics about classified failures.
        
        Args:
            failures: List of classified failures
            
        Returns:
            Dictionary with failure statistics
        """
        if not failures:
            return {"total_failures": 0}
        
        # Count by category
        category_counts = {}
        severity_counts = {}
        step_counts = {}
        
        for failure in failures:
            category = failure.category.value
            severity = failure.severity.value
            step = failure.step_name
            
            category_counts[category] = category_counts.get(category, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            step_counts[step] = step_counts.get(step, 0) + 1
        
        # Calculate recoverability
        recoverable_count = sum(1 for f in failures if self.get_classification_result(f).is_recoverable)
        
        return {
            "total_failures": len(failures),
            "by_category": category_counts,
            "by_severity": severity_counts,
            "by_step": step_counts,
            "recoverable_count": recoverable_count,
            "recoverable_percentage": (recoverable_count / len(failures)) * 100,
            "most_common_category": max(category_counts.items(), key=lambda x: x[1])[0],
            "most_severe_category": max(severity_counts.items(), key=lambda x: x[1])[0]
        }


# Convenience functions for backward compatibility
def classify_resume_failure(error_message: str, step_name: str, 
                           input_data_hash: str, context: Optional[Dict[str, Any]] = None) -> FailureDetails:
    """Convenience function to classify a resume processing failure."""
    classifier = ResumeFailureClassifier()
    return classifier.classify_failure(error_message, step_name, input_data_hash, context)


def get_recovery_strategy(failure_details: FailureDetails, retry_count: int = 0) -> ClassificationResult:
    """Convenience function to get recovery strategy for a failure."""
    classifier = ResumeFailureClassifier()
    return classifier.get_classification_result(failure_details, retry_count)
