#!/usr/bin/env python3
"""
Safety Schemas
Section 10: Schema Layer - Schemas for L5 safety/policy operations
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

from .base_schemas import BaseRequest, BaseResponse, ProcessingStatus

class SafetyLevel(str, Enum):
    """Safety level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PolicyType(str, Enum):
    """Policy type enumeration"""
    CONTENT = "content"
    PRIVACY = "privacy"
    SECURITY = "security"
    ETHICAL = "ethical"
    COMPLIANCE = "compliance"

class ValidationType(str, Enum):
    """Validation type enumeration"""
    INPUT = "input"
    OUTPUT = "output"
    PROCESS = "process"
    CONTEXT = "context"

class SafetyRequest(BaseRequest):
    """Request schema for safety operations"""
    safety_level: SafetyLevel = Field(..., description="Required safety level")
    policy_types: List[PolicyType] = Field(..., description="Policy types to apply")
    validation_type: ValidationType = Field(..., description="Type of validation to perform")
    content: Dict[str, Any] = Field(..., description="Content to validate")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Validation context")
    strict_mode: bool = Field(False, description="Enable strict validation mode")

class SafetyResponse(BaseResponse):
    """Response schema for safety operations"""
    validation_id: str = Field(..., description="Validation identifier")
    safety_level: SafetyLevel = Field(..., description="Safety level applied")
    validation_results: Dict[str, Any] = Field(..., description="Validation results")
    policy_violations: List[Dict[str, Any]] = Field(default_factory=list, description="Policy violations found")
    risk_score: float = Field(..., description="Overall risk score")
    recommendations: List[str] = Field(default_factory=list, description="Safety recommendations")

class PolicyConfig(BaseModel):
    """Policy configuration schema"""
    policy_id: str = Field(..., description="Policy identifier")
    policy_type: PolicyType = Field(..., description="Policy type")
    policy_name: str = Field(..., description="Policy name")
    rules: List[Dict[str, Any]] = Field(..., description="Policy rules")
    enabled: bool = Field(True, description="Whether policy is enabled")
    severity: SafetyLevel = Field(SafetyLevel.MEDIUM, description="Policy severity")
    exceptions: Optional[List[str]] = Field(default_factory=list, description="Policy exceptions")

class ContentFilter(BaseModel):
    """Content filter schema"""
    filter_id: str = Field(..., description="Filter identifier")
    filter_type: str = Field(..., description="Filter type")
    patterns: List[str] = Field(..., description="Filter patterns")
    action: str = Field("block", description="Action to take on match")
    severity: SafetyLevel = Field(SafetyLevel.MEDIUM, description="Filter severity")

class PrivacyPolicy(BaseModel):
    """Privacy policy schema"""
    policy_id: str = Field(..., description="Privacy policy identifier")
    data_types: List[str] = Field(..., description="Protected data types")
    retention_rules: Dict[str, Any] = Field(..., description="Data retention rules")
    access_controls: List[str] = Field(..., description="Access control rules")
    encryption_required: bool = Field(True, description="Whether encryption is required")

class SecurityPolicy(BaseModel):
    """Security policy schema"""
    policy_id: str = Field(..., description="Security policy identifier")
    threat_level: SafetyLevel = Field(..., description="Threat level")
    protection_rules: List[Dict[str, Any]] = Field(..., description="Protection rules")
    monitoring_required: bool = Field(True, description="Whether monitoring is required")
    incident_response: Dict[str, Any] = Field(default_factory=dict, description="Incident response procedures")

class EthicalGuideline(BaseModel):
    """Ethical guideline schema"""
    guideline_id: str = Field(..., description="Guideline identifier")
    principle: str = Field(..., description="Ethical principle")
    application: str = Field(..., description="How to apply this guideline")
    examples: List[str] = Field(default_factory=list, description="Application examples")
    exceptions: Optional[List[str]] = Field(default_factory=list, description="Allowed exceptions")

class ComplianceRule(BaseModel):
    """Compliance rule schema"""
    rule_id: str = Field(..., description="Compliance rule identifier")
    regulation: str = Field(..., description="Applicable regulation")
    requirements: List[str] = Field(..., description="Compliance requirements")
    audit_procedures: List[str] = Field(default_factory=list, description="Audit procedures")
    documentation_required: List[str] = Field(default_factory=list, description="Required documentation")

class SafetyAudit(BaseModel):
    """Safety audit schema"""
    audit_id: str = Field(..., description="Audit identifier")
    audit_type: str = Field(..., description="Type of audit")
    scope: List[str] = Field(..., description="Audit scope")
    findings: List[Dict[str, Any]] = Field(default_factory=list, description="Audit findings")
    recommendations: List[str] = Field(default_factory=list, description="Audit recommendations")
    audit_date: datetime = Field(default_factory=datetime.now, description="Audit date")

# Re-export safety schemas
__all__ = [
    'SafetyRequest', 'SafetyResponse', 'PolicyConfig', 'ContentFilter',
    'PrivacyPolicy', 'SecurityPolicy', 'EthicalGuideline', 'ComplianceRule',
    'SafetyAudit', 'SafetyLevel', 'PolicyType', 'ValidationType'
]
