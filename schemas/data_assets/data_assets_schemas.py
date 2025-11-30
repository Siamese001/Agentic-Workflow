#!/usr/bin/env python3
"""
Data Assets Schemas
Section 10: Schema Layer - Schemas for data assets operations
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from ..core.base_schemas import BaseRequest, BaseResponse, ProcessingStatus

class AssetType(str, Enum):
    """Types of data assets."""
    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"
    OUTREACH_TARGET = "outreach_target"
    USER_PROFILE = "user_profile"
    DATASET = "dataset"
    GOLDEN_SET = "golden_set"
    LOOKUP = "lookup"
    TEMPLATE = "template"

class DataFormat(str, Enum):
    """Data format types."""
    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    PDF = "pdf"
    DOCX = "docx"
    XML = "xml"

class DataAsset(BaseModel):
    """Base data asset schema."""
    asset_id: str = Field(..., description="Asset identifier")
    asset_name: str = Field(..., description="Asset name")
    asset_type: AssetType = Field(..., description="Asset type")
    format: DataFormat = Field(..., description="Data format")
    file_path: str = Field(..., description="File path")
    file_size: int = Field(..., description="File size in bytes")
    checksum: str = Field(..., description="File checksum")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Update timestamp")
    version: str = Field("1.0", description="Asset version")
    status: ProcessingStatus = Field(ProcessingStatus.PENDING, description="Processing status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Asset metadata")

class ResumeAsset(DataAsset):
    """Resume-specific data asset."""
    asset_type: AssetType = Field(AssetType.RESUME, description="Asset type")
    candidate_name: str = Field(..., description="Candidate name")
    experience_years: int = Field(..., description="Years of experience")
    skills: List[str] = Field(default_factory=list, description="Candidate skills")
    education: List[Dict[str, str]] = Field(default_factory=list, description="Education background")
    work_history: List[Dict[str, Any]] = Field(default_factory=list, description="Work history")
    certifications: List[str] = Field(default_factory=list, description="Certifications")
    target_roles: List[str] = Field(default_factory=list, description="Target job roles")
    industries: List[str] = Field(default_factory=list, description="Industries worked in")
    resume_type: str = Field("chronological", description="Resume format type")

class JobDescriptionAsset(DataAsset):
    """Job description-specific data asset."""
    asset_type: AssetType = Field(AssetType.JOB_DESCRIPTION, description="Asset type")
    job_title: str = Field(..., description="Job title")
    company_name: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    remote_option: str = Field(..., description="Remote work option")
    salary_range: Optional[str] = Field(None, description="Salary range")
    required_skills: List[str] = Field(default_factory=list, description="Required skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills")
    experience_level: str = Field(..., description="Required experience level")
    education_requirements: List[str] = Field(default_factory=list, description="Education requirements")
    responsibilities: List[str] = Field(default_factory=list, description="Job responsibilities")
    qualifications: List[str] = Field(default_factory=list, description="Job qualifications")
    industry: str = Field(..., description="Industry")
    employment_type: str = Field(..., description="Employment type")

class OutreachTargetAsset(DataAsset):
    """Outreach target-specific data asset."""
    asset_type: AssetType = Field(AssetType.OUTREACH_TARGET, description="Asset type")
    contact_name: str = Field(..., description="Contact name")
    contact_title: str = Field(..., description="Contact title")
    company_name: str = Field(..., description="Company name")
    company_size: str = Field(..., description="Company size")
    industry: str = Field(..., description="Industry")
    location: str = Field(..., description="Location")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile")
    outreach_status: str = Field("new", description="Outreach status")
    last_contacted: Optional[datetime] = Field(None, description="Last contact date")
    notes: Optional[str] = Field(None, description="Contact notes")
    tags: List[str] = Field(default_factory=list, description="Contact tags")

class UserProfileAsset(DataAsset):
    """User profile-specific data asset."""
    asset_type: AssetType = Field(AssetType.USER_PROFILE, description="Asset type")
    user_id: str = Field(..., description="User identifier")
    persona_type: str = Field(..., description="Persona type")
    communication_style: str = Field(..., description="Communication style")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="User constraints")
    goals: List[str] = Field(default_factory=list, description="User goals")
    target_companies: List[str] = Field(default_factory=list, description="Target companies")
    target_locations: List[str] = Field(default_factory=list, description="Target locations")
    salary_expectations: Optional[str] = Field(None, description="Salary expectations")
    availability: str = Field(..., description="Availability status")
    work_preferences: Dict[str, Any] = Field(default_factory=dict, description="Work preferences")

class DatasetAsset(DataAsset):
    """Dataset-specific data asset."""
    asset_type: AssetType = Field(AssetType.DATASET, description="Asset type")
    dataset_name: str = Field(..., description="Dataset name")
    dataset_type: str = Field(..., description="Dataset type")
    record_count: int = Field(..., description="Number of records")
    schema_definition: Dict[str, Any] = Field(..., description="Dataset schema")
    data_quality_score: float = Field(..., description="Data quality score")
    last_validated: Optional[datetime] = Field(None, description="Last validation date")
    validation_results: Dict[str, Any] = Field(default_factory=dict, description="Validation results")
    refresh_frequency: str = Field(..., description="Data refresh frequency")
    source_system: str = Field(..., description="Source system")
    retention_policy: str = Field(..., description="Data retention policy")

class GoldenSetAsset(DataAsset):
    """Golden set-specific data asset for testing and validation."""
    asset_type: AssetType = Field(AssetType.GOLDEN_SET, description="Asset type")
    test_scenario: str = Field(..., description="Test scenario description")
    expected_outcome: Dict[str, Any] = Field(..., description="Expected test outcome")
    input_data: Dict[str, Any] = Field(..., description="Test input data")
    validation_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Validation rules")
    test_type: str = Field(..., description="Test type")
    priority: str = Field("medium", description="Test priority")
    tags: List[str] = Field(default_factory=list, description="Test tags")
    dependencies: List[str] = Field(default_factory=list, description="Test dependencies")

class LookupAsset(DataAsset):
    """Lookup table-specific data asset."""
    asset_type: AssetType = Field(AssetType.LOOKUP, description="Asset type")
    lookup_type: str = Field(..., description="Lookup table type")
    key_field: str = Field(..., description="Primary key field")
    value_fields: List[str] = Field(..., description="Value fields")
    record_count: int = Field(..., description="Number of lookup records")
    last_updated: datetime = Field(..., description="Last update timestamp")
    update_frequency: str = Field(..., description="Update frequency")
    source: str = Field(..., description="Data source")
    usage_count: int = Field(0, description="Usage count")

class DataAssetRequest(BaseRequest):
    """Request schema for data asset operations."""
    asset_type: AssetType = Field(..., description="Asset type to process")
    operation: str = Field(..., description="Operation to perform")
    asset_name: str = Field(..., description="Asset name")
    file_path: str = Field(..., description="Asset file path")
    format: DataFormat = Field(..., description="Asset format")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Asset metadata")
    processing_options: Optional[Dict[str, Any]] = Field(None, description="Processing options")

class DataAssetResponse(BaseResponse):
    """Response schema for data asset operations."""
    asset_id: str = Field(..., description="Processed asset identifier")
    asset_type: AssetType = Field(..., description="Asset type")
    operation: str = Field(..., description="Operation performed")
    status: ProcessingStatus = Field(..., description="Processing status")
    file_size: int = Field(..., description="Processed file size")
    checksum: str = Field(..., description="File checksum")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    validation_results: Optional[Dict[str, Any]] = Field(None, description="Validation results")

class DataAssetSearchRequest(BaseRequest):
    """Request schema for data asset search operations."""
    search_query: str = Field(..., description="Search query")
    asset_types: Optional[List[AssetType]] = Field(None, description="Asset type filters")
    formats: Optional[List[DataFormat]] = Field(None, description="Format filters")
    status_filter: Optional[ProcessingStatus] = Field(None, description="Status filter")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")
    metadata_filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    page_size: int = Field(20, description="Page size")
    page_number: int = Field(1, description="Page number")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", description="Sort order")

class DataAssetSearchResponse(BaseResponse):
    """Response schema for data asset search operations."""
    assets: List[DataAsset] = Field(..., description="Found assets")
    total_count: int = Field(..., description="Total matching assets")
    page_number: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    search_time_ms: int = Field(..., description="Search time in milliseconds")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")

class DataAssetValidationRequest(BaseRequest):
    """Request schema for data asset validation operations."""
    asset_id: str = Field(..., description="Asset identifier")
    validation_rules: List[Dict[str, Any]] = Field(..., description="Validation rules to apply")
    strict_mode: bool = Field(False, description="Enable strict validation")
    auto_fix: bool = Field(False, description="Auto-fix detected issues")

class DataAssetValidationResponse(BaseResponse):
    """Response schema for data asset validation operations."""
    asset_id: str = Field(..., description="Validated asset identifier")
    validation_status: str = Field(..., description="Validation status")
    issues_found: List[Dict[str, Any]] = Field(default_factory=list, description="Issues found")
    issues_fixed: List[Dict[str, Any]] = Field(default_factory=list, description="Issues auto-fixed")
    quality_score: float = Field(..., description="Data quality score")
    validation_time_ms: int = Field(..., description="Validation time in milliseconds")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")

class DataAssetMetrics(BaseModel):
    """Data asset usage and performance metrics."""
    asset_id: str = Field(..., description="Asset identifier")
    asset_type: AssetType = Field(..., description="Asset type")
    access_count: int = Field(..., description="Number of times accessed")
    download_count: int = Field(..., description="Number of times downloaded")
    last_accessed: datetime = Field(..., description="Last access timestamp")
    average_processing_time_ms: float = Field(..., description="Average processing time")
    error_rate: float = Field(..., description="Error rate")
    user_ratings: List[int] = Field(default_factory=list, description="User ratings")
    usage_by_date: Dict[str, int] = Field(default_factory=dict, description="Usage by date")
    popular_queries: List[str] = Field(default_factory=list, description="Popular search queries")

class DataAssetMetricsRequest(BaseRequest):
    """Request schema for data asset metrics operations."""
    asset_id: Optional[str] = Field(None, description="Specific asset identifier")
    asset_types: Optional[List[AssetType]] = Field(None, description="Asset type filters")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range for metrics")
    include_usage: bool = Field(True, description="Include usage metrics")
    include_performance: bool = Field(True, description="Include performance metrics")

class DataAssetMetricsResponse(BaseResponse):
    """Response schema for data asset metrics operations."""
    metrics: List[DataAssetMetrics] = Field(..., description="Asset metrics data")
    summary: Dict[str, Any] = Field(..., description="Metrics summary")
    time_range: Dict[str, datetime] = Field(..., description="Time range covered")
    total_assets: int = Field(..., description="Total assets in metrics")
    generated_at: datetime = Field(default_factory=datetime.now, description="Metrics generation timestamp")
