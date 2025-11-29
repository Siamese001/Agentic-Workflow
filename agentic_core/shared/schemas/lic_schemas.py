#!/usr/bin/env python3
"""
Outreach Engine Schemas - Lift & Shift + Enhanced from LIC
Message schemas and data structures
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from ..models import (
    Route, Archetype, ValidationResult, ValidationSeverity
)


@dataclass
class SenderProfile:
    """Sender profile schema - Enhanced from LIC"""
    name: str
    title: str
    company: str
    experience: List[Dict[str, Any]] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    education: List[Dict[str, Any]] = field(default_factory=list)
    current_company: str = ""
    domain: str = ""
    linkedin_url: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    certifications: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    projects: List[Dict[str, Any]] = field(default_factory=list)
    publications: List[Dict[str, Any]] = field(default_factory=list)
    honors: List[str] = field(default_factory=list)
    
    def get_current_role(self) -> Optional[Dict[str, Any]]:
        """Get current role from experience"""
        for exp in self.experience:
            if exp.get("current", False) or not exp.get("end_date"):
                return exp
        return self.experience[0] if self.experience else None
    
    def get_years_experience(self) -> int:
        """Calculate total years of experience"""
        total_years = 0
        for exp in self.experience:
            start_date = exp.get("start_date")
            end_date = exp.get("end_date")
            
            if start_date:
                try:
                    start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    if end_date:
                        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    else:
                        end = datetime.now()
                    
                    years = (end - start).days / 365.25
                    total_years += years
                except:
                    continue
        
        return int(total_years)
    
    def validate_profile(self) -> List[ValidationResult]:
        """Validate sender profile completeness"""
        validation_results = []
        
        if not self.name:
            validation_results.append(ValidationResult(
                rule_id="MISSING_SENDER_NAME",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="Sender name is required",
                details={}
            ))
        
        if not self.title:
            validation_results.append(ValidationResult(
                rule_id="MISSING_SENDER_TITLE",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Sender title is required",
                details={}
            ))
        
        if not self.company and not self.current_company:
            validation_results.append(ValidationResult(
                rule_id="MISSING_SENDER_COMPANY",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Sender company is required",
                details={}
            ))
        
        return validation_results


@dataclass
class RecipientProfile:
    """Recipient profile schema - Enhanced from LIC"""
    name: str
    title: str
    company: str
    department: str = ""
    linkedin_url: str = ""
    email: str = ""
    location: str = ""
    about: str = ""
    experience: List[Dict[str, Any]] = field(default_factory=list)
    education: List[Dict[str, Any]] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    connection_status: str = "not_connected"  # connected, not_connected, pending
    mutual_connections: List[Dict[str, Any]] = field(default_factory=list)
    recent_activity: List[Dict[str, Any]] = field(default_factory=list)
    company_size: str = ""
    industry: str = ""
    domain: str = ""
    seniority_level: str = ""
    profile_completeness: float = 0.0
    
    def get_profile_score(self) -> float:
        """Calculate profile completeness score"""
        score = 0.0
        max_score = 10.0
        
        if self.name: score += 1.0
        if self.title: score += 1.0
        if self.company: score += 1.0
        if self.about: score += 1.0
        if self.experience: score += 1.0
        if self.skills: score += 1.0
        if self.education: score += 1.0
        if self.location: score += 1.0
        if self.industry: score += 1.0
        if self.domain: score += 1.0
        
        return score / max_score
    
    def is_connected(self) -> bool:
        """Check if connected to recipient"""
        return self.connection_status == "connected"
    
    def get_mutual_connection_count(self) -> int:
        """Get number of mutual connections"""
        return len(self.mutual_connections)
    
    def validate_profile(self) -> List[ValidationResult]:
        """Validate recipient profile completeness"""
        validation_results = []
        
        if not self.name:
            validation_results.append(ValidationResult(
                rule_id="MISSING_RECIPIENT_NAME",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="Recipient name is required",
                details={}
            ))
        
        if not self.title:
            validation_results.append(ValidationResult(
                rule_id="MISSING_RECIPIENT_TITLE",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Recipient title is required for proper classification",
                details={}
            ))
        
        if not self.company:
            validation_results.append(ValidationResult(
                rule_id="MISSING_RECIPIENT_COMPANY",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Recipient company is required for personalization",
                details={}
            ))
        
        return validation_results


@dataclass
class JobDescription:
    """Job description schema - Enhanced from LIC"""
    title: str
    company: str
    location: str = ""
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    qualifications: List[str] = field(default_factory=list)
    skills_required: List[str] = field(default_factory=list)
    experience_level: str = ""
    salary_range: str = ""
    job_type: str = ""  # full-time, contract, etc.
    remote_policy: str = ""
    posted_date: str = ""
    application_deadline: str = ""
    department: str = ""
    industry: str = ""
    company_size: str = ""
    
    def get_key_requirements(self) -> List[str]:
        """Get most important requirements"""
        return self.requirements[:5] if self.requirements else []
    
    def get_required_skills(self) -> List[str]:
        """Get required skills"""
        return self.skills_required[:10] if self.skills_required else []
    
    def get_experience_years(self) -> str:
        """Extract experience years from requirements"""
        for req in self.requirements:
            if "year" in req.lower():
                return req
        return ""
    
    def validate_job_description(self) -> List[ValidationResult]:
        """Validate job description completeness"""
        validation_results = []
        
        if not self.title:
            validation_results.append(ValidationResult(
                rule_id="MISSING_JOB_TITLE",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Job title is required",
                details={}
            ))
        
        if not self.company:
            validation_results.append(ValidationResult(
                rule_id="MISSING_JOB_COMPANY",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Job company is required",
                details={}
            ))
        
        if not self.description:
            validation_results.append(ValidationResult(
                rule_id="MISSING_JOB_DESCRIPTION",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="Job description is recommended for better personalization",
                details={}
            ))
        
        return validation_results


@dataclass
class MessageSchema:
    """Complete message schema - Enhanced from LIC"""
    message_id: str = field(default_factory=lambda: f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    sender_profile: Optional[SenderProfile] = None
    recipient_profile: Optional[RecipientProfile] = None
    job_description: Optional[JobDescription] = None
    route: Optional[Route] = None
    archetype: Optional[Archetype] = None
    k1_greeting: str = ""
    k2_subject_line: Optional[str] = None
    k3_message_body: str = ""
    k4_cta: str = ""
    k5_signature: str = ""
    formatted_message: str = ""
    generation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    validation_results: List[ValidationResult] = field(default_factory=list)
    rag_evidence: List[Dict[str, Any]] = field(default_factory=list)
    processing_metrics: Dict[str, Any] = field(default_factory=dict)
    delivery_status: str = "draft"  # draft, sent, delivered, opened, responded
    response_received: bool = False
    response_timestamp: Optional[str] = None
    
    def get_word_count(self) -> int:
        """Get total word count of message"""
        return len(self.formatted_message.split())
    
    def get_character_count(self) -> int:
        """Get total character count of message"""
        return len(self.formatted_message)
    
    def has_critical_validations(self) -> bool:
        """Check if message has critical validation failures"""
        return any(v.severity == ValidationSeverity.CRITICAL and not v.passed for v in self.validation_results)
    
    def is_ready_for_delivery(self) -> bool:
        """Check if message is ready for delivery"""
        # Must have all components
        if not all([self.k1_greeting, self.k3_message_body, self.k4_cta, self.k5_signature]):
            return False
        
        # Must have route and archetype
        if not self.route or not self.archetype:
            return False
        
        # Must not have critical validation failures
        if self.has_critical_validations():
            return False
        
        return True
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation results"""
        total = len(self.validation_results)
        passed = sum(1 for v in self.validation_results if v.passed)
        failed = total - passed
        
        severity_counts = {}
        for result in self.validation_results:
            severity = result.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_validations": total,
            "passed": passed,
            "failed": failed,
            "severity_breakdown": severity_counts,
            "ready_for_delivery": self.is_ready_for_delivery()
        }
    
    def validate_message_schema(self) -> List[ValidationResult]:
        """Validate complete message schema"""
        validation_results = []
        
        # Validate required components
        if not self.sender_profile:
            validation_results.append(ValidationResult(
                rule_id="MISSING_SENDER_PROFILE",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="Sender profile is required",
                details={}
            ))
        
        if not self.recipient_profile:
            validation_results.append(ValidationResult(
                rule_id="MISSING_RECIPIENT_PROFILE",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="Recipient profile is required",
                details={}
            ))
        
        # Validate message components
        if not self.k1_greeting:
            validation_results.append(ValidationResult(
                rule_id="MISSING_GREETING_COMPONENT",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="K1 greeting component is missing",
                details={}
            ))
        
        if not self.k3_message_body:
            validation_results.append(ValidationResult(
                rule_id="MISSING_MESSAGE_BODY_COMPONENT",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="K3 message body component is missing",
                details={}
            ))
        
        if not self.k4_cta:
            validation_results.append(ValidationResult(
                rule_id="MISSING_CTA_COMPONENT",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="K4 CTA component is missing",
                details={}
            ))
        
        if not self.k5_signature:
            validation_results.append(ValidationResult(
                rule_id="MISSING_SIGNATURE_COMPONENT",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="K5 signature component is missing",
                details={}
            ))
        
        return validation_results


@dataclass
class OutreachCampaign:
    """Outreach campaign schema - Enhanced from LIC"""
    campaign_id: str = field(default_factory=lambda: f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    name: str = ""
    description: str = ""
    sender_profile: Optional[SenderProfile] = None
    target_recipients: List[RecipientProfile] = field(default_factory=list)
    job_context: Optional[JobDescription] = None
    campaign_settings: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    scheduled_send_date: Optional[str] = None
    messages: List[MessageSchema] = field(default_factory=list)
    campaign_status: str = "draft"  # draft, scheduled, active, completed, paused
    
    def get_recipient_count(self) -> int:
        """Get number of target recipients"""
        return len(self.target_recipients)
    
    def get_generated_message_count(self) -> int:
        """Get number of generated messages"""
        return len(self.messages)
    
    def get_completion_rate(self) -> float:
        """Get campaign completion rate"""
        if not self.target_recipients:
            return 0.0
        return len(self.messages) / len(self.target_recipients)
    
    def validate_campaign_schema(self) -> List[ValidationResult]:
        """Validate campaign schema"""
        validation_results = []
        
        if not self.name:
            validation_results.append(ValidationResult(
                rule_id="MISSING_CAMPAIGN_NAME",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="Campaign name is required",
                details={}
            ))
        
        if not self.sender_profile:
            validation_results.append(ValidationResult(
                rule_id="MISSING_CAMPAIGN_SENDER",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="Sender profile is required for campaign",
                details={}
            ))
        
        if not self.target_recipients:
            validation_results.append(ValidationResult(
                rule_id="NO_TARGET_RECIPIENTS",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Campaign must have target recipients",
                details={}
            ))
        
        return validation_results
