"""
Pydantic schemas for workflow node validation.

Defines strict models for each K-node to enforce structure
and prevent LLM output drift.
"""

from pydantic import BaseModel, Field, validator, constr
from typing import List, Optional, Dict, Any
from datetime import datetime


# K.1: Company and Job Title Extraction
class K1CompanyJobTitle(BaseModel):
    """Schema for K.1 node - Company and job title extraction."""
    company_name: str = Field(..., description="Exact company name from the job posting")
    job_title: str = Field(..., description="Exact job title from the posting")
    location: Optional[str] = Field(None, description="Job location if specified")
    
    @validator('company_name')
    def validate_company(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Company name too short")
        return v.strip()
    
    @validator('job_title')
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Job title too short")
        return v.strip()


# K.2: Skills Analysis
class K2SkillsAnalysis(BaseModel):
    """Schema for K.2 node - Skills extraction and categorization."""
    required_skills: List[str] = Field(
        ...,
        min_items=5,
        max_items=15,
        description="Required technical and soft skills"
    )
    preferred_skills: List[str] = Field(
        ...,
        min_items=3,
        max_items=10,
        description="Preferred but not required skills"
    )
    skill_categories: Dict[str, List[str]] = Field(
        ...,
        description="Skills grouped by category (technical, soft, tools, etc.)"
    )
    
    @validator('required_skills')
    def validate_required_skills(cls, v):
        cleaned = [skill.strip() for skill in v if skill.strip()]
        if len(cleaned) < 5:
            raise ValueError("At least 5 required skills needed")
        return cleaned


# K.3: Experience Requirements
class K3ExperienceRequirements(BaseModel):
    """Schema for K.3 node - Experience level and requirements."""
    years_experience_required: Dict[str, Any] = Field(
        ...,
        description="Experience requirements with minimum/preferred years"
    )
    seniority_level: str = Field(
        ...,
        description="Seniority level (Entry, Mid, Senior, Lead, Principal)"
    )
    industry_experience: List[str] = Field(
        ...,
        description="Required industry experience"
    )
    
    @validator('seniority_level')
    def validate_seniority(cls, v):
        valid_levels = ["Entry", "Mid", "Senior", "Lead", "Principal", "Executive"]
        if v not in valid_levels:
            raise ValueError(f"Invalid seniority level. Must be one of: {valid_levels}")
        return v


# K.4: Responsibilities Analysis
class K4Responsibilities(BaseModel):
    """Schema for K.4 node - Job responsibilities breakdown."""
    primary_responsibilities: List[str] = Field(
        ...,
        min_items=5,
        max_items=8,
        description="Primary job responsibilities"
    )
    secondary_responsibilities: List[str] = Field(
        ...,
        min_items=3,
        max_items=6,
        description="Secondary or occasional responsibilities"
    )
    leadership_scope: Optional[str] = Field(
        None,
        description="Leadership or management scope if applicable"
    )
    
    @validator('primary_responsibilities')
    def validate_primary(cls, v):
        for resp in v:
            if len(resp.strip()) < 10:
                raise ValueError("Responsibility descriptions too short")
        return v


# K.5: Executive Summary
class K5ExecutiveSummary(BaseModel):
    """Schema for K.5 node - Executive summary generation."""
    summary_text: constr(
        min_length=100,
        max_length=300
    ) = Field(..., description="Executive summary in paragraph form")
    key_highlights: List[str] = Field(
        ...,
        min_items=3,
        max_items=5,
        description="3-5 key highlights from the analysis"
    )
    value_proposition: str = Field(
        ...,
        description="Clear value proposition statement"
    )
    
    @validator('summary_text')
    def validate_no_markdown(cls, v):
        if '#' in v or '*' in v or '`' in v:
            raise ValueError("Summary should not contain markdown formatting")
        return v.strip()


# K.6: Most Recent Experience
class K6MostRecentExperience(BaseModel):
    """Schema for K.6 node - Most recent experience bullets."""
    intro_sentence: constr(
        min_length=20,
        max_length=100
    ) = Field(..., description="Context-setting introduction")
    bullets: List[str] = Field(
        ...,
        min_items=7,
        max_items=7,
        description="Exactly 7 achievement bullets, 25-35 words each"
    )
    
    @validator('bullets')
    def validate_bullets(cls, v):
        for i, bullet in enumerate(v):
            word_count = len(bullet.split())
            if word_count < 25 or word_count > 35:
                raise ValueError(f"Bullet {i+1} must be 25-35 words (got {word_count})")
            if not bullet.endswith('.'):
                raise ValueError(f"Bullet {i+1} must end with a period")
        return v
    
    @validator('intro_sentence')
    def validate_intro(cls, v):
        if not v[0].isupper():
            raise ValueError("Intro sentence must start with capital letter")
        return v.strip()


# K.7: Technical Skills Section
class K7TechnicalSkills(BaseModel):
    """Schema for K.7 node - Technical skills categorization."""
    programming_languages: List[str] = Field(
        ...,
        min_items=3,
        description="Programming languages and proficiency"
    )
    frameworks_tools: List[str] = Field(
        ...,
        min_items=3,
        description="Frameworks and tools"
    )
    databases: List[str] = Field(
        ...,
        min_items=2,
        description="Database technologies"
    )
    cloud_platforms: List[str] = Field(
        ...,
        min_items=1,
        description="Cloud platforms experience"
    )
    
    @validator('programming_languages')
    def validate_languages(cls, v):
        # Remove duplicates and empty entries
        cleaned = list(set([lang.strip() for lang in v if lang.strip()]))
        if len(cleaned) < 3:
            raise ValueError("At least 3 programming languages required")
        return cleaned


# K.8: Project Experience
class K8ProjectExperience(BaseModel):
    """Schema for K.8 node - Key project highlights."""
    project_name: str = Field(..., description="Project name")
    duration: str = Field(..., description="Project duration (e.g., '6 months')")
    role: str = Field(..., description="Role in the project")
    achievements: List[str] = Field(
        ...,
        min_items=3,
        max_items=5,
        description="Key achievements in the project"
    )
    technologies_used: List[str] = Field(
        ...,
        min_items=3,
        description="Technologies used in the project"
    )
    
    @validator('achievements')
    def validate_achievements(cls, v):
        for achievement in v:
            if len(achievement.strip()) < 15:
                raise ValueError("Achievement descriptions too short")
        return v


# K.9: Education and Certifications
class K9EducationCertifications(BaseModel):
    """Schema for K.9 node - Education and certifications."""
    highest_degree: str = Field(..., description="Highest degree obtained")
    institution: str = Field(..., description="Institution name")
    graduation_year: Optional[int] = Field(
        None,
        ge=1950,
        le=2030,
        description="Graduation year"
    )
    certifications: List[str] = Field(
        ...,
        max_items=10,
        description="Professional certifications"
    )
    
    @validator('institution')
    def validate_institution(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Institution name too short")
        return v.strip()


# K.10: Additional Information
class K10AdditionalInfo(BaseModel):
    """Schema for K.10 node - Additional relevant information."""
    languages: List[str] = Field(
        ...,
        max_items=5,
        description="Languages spoken"
    )
    volunteer_experience: Optional[str] = Field(
        None,
        max_length=200,
        description="Brief volunteer experience"
    )
    interests: List[str] = Field(
        ...,
        max_items=5,
        description="Professional interests"
    )
    availability: Optional[str] = Field(
        None,
        max_length=100,
        description="Availability information"
    )


# Registry function to get all schemas
def get_schema_registry() -> Dict[str, type]:
    """Get a registry of all available schemas.
    
    Returns:
        Dictionary mapping schema names to Pydantic model classes
    """
    return {
        "K1CompanyJobTitle": K1CompanyJobTitle,
        "K2SkillsAnalysis": K2SkillsAnalysis,
        "K3ExperienceRequirements": K3ExperienceRequirements,
        "K4Responsibilities": K4Responsibilities,
        "K5ExecutiveSummary": K5ExecutiveSummary,
        "K6MostRecentExperience": K6MostRecentExperience,
        "K7TechnicalSkills": K7TechnicalSkills,
        "K8ProjectExperience": K8ProjectExperience,
        "K9EducationCertifications": K9EducationCertifications,
        "K10AdditionalInfo": K10AdditionalInfo
    }
