#!/usr/bin/env python3
"""
Prompt Governance Schemas
Section 10: Schema Layer - Schemas for prompt governance operations
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from ..core.base_schemas import BaseRequest, BaseResponse

class AccessLevel(str, Enum):
    """Access levels for governance."""
    READ_ONLY = "read_only"
    OPERATIONAL = "operational"
    MANAGEMENT = "management"
    EXECUTIVE = "executive"
    CONSULTATION = "consultation"
    QUALITY = "quality"
    COMPLIANCE = "compliance"
    BUSINESS = "business"
    TECHNICAL = "technical"

class RoleType(str, Enum):
    """Role types in governance framework."""
    GOVERNANCE_COMMITTEE = "governance_committee"
    PROMPT_GOVERNANCE_MANAGER = "prompt_governance_manager"
    TECHNICAL_LEAD = "technical_lead"
    PROMPT_ENGINEER = "prompt_engineer"
    QUALITY_ASSURANCE_LEAD = "quality_assurance_lead"
    COMPLIANCE_OFFICER = "compliance_officer"
    SUBJECT_MATTER_EXPERT = "subject_matter_expert"
    PRODUCT_MANAGER = "product_manager"
    AUDITOR = "auditor"
    VIEWER = "viewer"

class PermissionType(str, Enum):
    """Permission types."""
    APPROVE_MAJOR_CHANGES = "approve_major_changes"
    SET_GOVERNANCE_POLICIES = "set_governance_policies"
    OVERRIDE_APPROVALS = "override_approvals"
    EMERGENCY_AUTHORIZATION = "emergency_authorization"
    MANAGE_APPROVAL_WORKFLOWS = "manage_approval_workflows"
    CREATE_PROMPTS = "create_prompts"
    MODIFY_PROMPTS = "modify_prompts"
    DEPLOY_PROMPTS = "deploy_prompts"
    AUDIT_ACCESS = "audit_access"
    VIEW_APPROVED_CONTENT = "view_approved_content"

class DataClassification(str, Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class RegulatoryStandard(str, Enum):
    """Regulatory standards."""
    GDPR = "gdpr"
    SOC2 = "soc2"
    HIPAA = "hipaa"
    ISO27001 = "iso27001"
    NIST_CSF = "nist_csf"

class Role(BaseModel):
    """Role definition in governance framework."""
    role_name: RoleType = Field(..., description="Role type")
    description: str = Field(..., description="Role description")
    permissions: List[PermissionType] = Field(..., description="Role permissions")
    access_level: AccessLevel = Field(..., description="Access level")
    created_at: datetime = Field(default_factory=datetime.now, description="Role creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Role update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional role metadata")

class User(BaseModel):
    """User in governance system."""
    user_id: str = Field(..., description="User identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    roles: List[RoleType] = Field(..., description="Assigned roles")
    access_level: AccessLevel = Field(..., description="User access level")
    active: bool = Field(True, description="User active status")
    created_at: datetime = Field(default_factory=datetime.now, description="User creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional user metadata")

class Permission(BaseModel):
    """Permission definition."""
    permission_name: PermissionType = Field(..., description="Permission type")
    description: str = Field(..., description="Permission description")
    resource_type: str = Field(..., description="Resource type this permission applies to")
    access_level: AccessLevel = Field(..., description="Required access level")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Permission conditions")

class PermissionMatrix(BaseModel):
    """Permission matrix for resource access."""
    resource_name: str = Field(..., description="Resource name")
    resource_type: str = Field(..., description="Resource type")
    access_rules: Dict[str, List[RoleType]] = Field(..., description="Access rules by operation")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Access conditions")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class AccessPolicy(BaseModel):
    """Access control policy."""
    policy_id: str = Field(..., description="Policy identifier")
    policy_name: str = Field(..., description="Policy name")
    policy_type: str = Field(..., description="Policy type")
    description: str = Field(..., description="Policy description")
    rules: List[Dict[str, Any]] = Field(..., description="Policy rules")
    enabled: bool = Field(True, description="Policy enabled status")
    priority: int = Field(1, description="Policy priority")
    created_at: datetime = Field(default_factory=datetime.now, description="Policy creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Policy update timestamp")

class DataAccessControl(BaseModel):
    """Data access control configuration."""
    data_type: str = Field(..., description="Data type")
    classification: DataClassification = Field(..., description="Data classification")
    access_roles: List[RoleType] = Field(..., description="Roles with access")
    encryption_required: bool = Field(..., description="Encryption required")
    audit_access: bool = Field(True, description="Audit access enabled")
    retention_policy: str = Field(..., description="Data retention policy")
    restrictions: List[str] = Field(default_factory=list, description="Access restrictions")

class APIAccessControl(BaseModel):
    """API access control configuration."""
    endpoint: str = Field(..., description="API endpoint")
    authentication_required: bool = Field(True, description="Authentication required")
    required_permissions: List[PermissionType] = Field(default_factory=list, description="Required permissions")
    rate_limit: Optional[Dict[str, int]] = Field(None, description="Rate limiting configuration")
    ip_whitelist: Optional[List[str]] = Field(None, description="IP whitelist")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional API metadata")

class AuditEvent(BaseModel):
    """Audit event record."""
    event_id: str = Field(..., description="Event identifier")
    event_type: str = Field(..., description="Event type")
    user_id: str = Field(..., description="User identifier")
    resource: str = Field(..., description="Resource accessed")
    action: str = Field(..., description="Action performed")
    timestamp: datetime = Field(..., description="Event timestamp")
    ip_address: str = Field(..., description="IP address")
    user_agent: str = Field(..., description="User agent")
    success: bool = Field(True, description="Action success status")
    details: Dict[str, Any] = Field(default_factory=dict, description="Event details")

class ComplianceRequirement(BaseModel):
    """Compliance requirement configuration."""
    standard: RegulatoryStandard = Field(..., description="Regulatory standard")
    requirement_type: str = Field(..., description="Requirement type")
    description: str = Field(..., description="Requirement description")
    implementation_status: str = Field(..., description="Implementation status")
    last_audit: Optional[datetime] = Field(None, description="Last audit date")
    next_audit: Optional[datetime] = Field(None, description="Next audit date")
    compliance_score: float = Field(..., description="Compliance score")
    evidence: List[str] = Field(default_factory=list, description="Compliance evidence")

class EmergencyAccess(BaseModel):
    """Emergency access configuration."""
    scenario_type: str = Field(..., description="Emergency scenario type")
    description: str = Field(..., description="Scenario description")
    authorized_roles: List[RoleType] = Field(..., description="Authorized roles")
    approval_process: str = Field(..., description="Approval process")
    duration_hours: int = Field(..., description="Access duration in hours")
    documentation_required: str = Field(..., description="Required documentation")
    automatic_expiration: bool = Field(True, description="Automatic expiration enabled")

class GovernanceRequest(BaseRequest):
    """Request schema for governance operations."""
    operation: str = Field(..., description="Governance operation")
    resource_type: str = Field(..., description="Resource type")
    resource_id: Optional[str] = Field(None, description="Resource identifier")
    user_id: str = Field(..., description="User identifier")
    justification: str = Field(..., description="Operation justification")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class GovernanceResponse(BaseResponse):
    """Response schema for governance operations."""
    governance_id: str = Field(..., description="Governance operation identifier")
    operation: str = Field(..., description="Operation performed")
    approval_status: str = Field(..., description="Approval status")
    approved_by: Optional[str] = Field(None, description="Approver identifier")
    approval_timestamp: Optional[datetime] = Field(None, description="Approval timestamp")
    conditions: List[str] = Field(default_factory=list, description="Approval conditions")

class RoleAssignmentRequest(BaseRequest):
    """Request schema for role assignment operations."""
    user_id: str = Field(..., description="User identifier")
    role: RoleType = Field(..., description="Role to assign")
    justification: str = Field(..., description="Assignment justification")
    duration_days: Optional[int] = Field(None, description="Assignment duration in days")
    approver_id: Optional[str] = Field(None, description="Approver identifier")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Assignment conditions")

class RoleAssignmentResponse(BaseResponse):
    """Response schema for role assignment operations."""
    assignment_id: str = Field(..., description="Assignment identifier")
    user_id: str = Field(..., description="User identifier")
    role: RoleType = Field(..., description="Assigned role")
    assigned_at: datetime = Field(..., description="Assignment timestamp")
    expires_at: Optional[datetime] = Field(None, description="Assignment expiration")
    assigned_by: str = Field(..., description="Assigner identifier")

class AuditLogRequest(BaseRequest):
    """Request schema for audit log operations."""
    event_type: Optional[str] = Field(None, description="Event type filter")
    user_id: Optional[str] = Field(None, description="User identifier filter")
    resource: Optional[str] = Field(None, description="Resource filter")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
    page_size: int = Field(100, description="Page size")
    page_number: int = Field(1, description="Page number")

class AuditLogResponse(BaseResponse):
    """Response schema for audit log operations."""
    events: List[AuditEvent] = Field(..., description="Audit events")
    total_count: int = Field(..., description="Total event count")
    page_number: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    filtered_by: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")

class ComplianceReport(BaseModel):
    """Compliance report data."""
    report_id: str = Field(..., description="Report identifier")
    standard: RegulatoryStandard = Field(..., description="Regulatory standard")
    report_date: datetime = Field(..., description="Report date")
    overall_score: float = Field(..., description="Overall compliance score")
    requirements: List[ComplianceRequirement] = Field(..., description="Compliance requirements")
    findings: List[str] = Field(default_factory=list, description="Compliance findings")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    generated_by: str = Field(..., description="Report generator")

class ComplianceReportRequest(BaseRequest):
    """Request schema for compliance report operations."""
    standard: RegulatoryStandard = Field(..., description="Regulatory standard")
    report_type: str = Field(..., description="Report type")
    include_findings: bool = Field(True, description="Include findings")
    include_recommendations: bool = Field(True, description="Include recommendations")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range for report")

class ComplianceReportResponse(BaseResponse):
    """Response schema for compliance report operations."""
    report: ComplianceReport = Field(..., description="Compliance report data")
    report_url: str = Field(..., description="Report download URL")
    expires_at: datetime = Field(..., description="Report expiration timestamp")
