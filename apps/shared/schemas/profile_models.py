"""
Shared Profile Models
LEVEL 5 - Profile-related Pydantic models shared across engines
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import date
from enum import Enum
from .base_models import StandardModel

class ContactInfo(BaseModel):
    """Contact information model"""

    email: EmailStr = Field(..., description="Primary email address")
    phone: Optional[str] = Field(None, description="Phone number")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    website: Optional[str] = Field(None, description="Personal website URL")
    location: Optional[str] = Field(None, description="Physical location")
    address: Optional[str] = Field(None, description="Full address")

    @validator("phone")
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v is not None:
            import re
            phone_pattern = re.compile(r'^\+?1[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$')
            if not phone_pattern.match(v.strip()):
                raise ValueError("Invalid phone number format")
        return v.strip() if v else None

    @validator("linkedin", "github", "website")
    def validate_urls(cls, v):
        """Validate URL format"""
        if v is not None:
            import re
            url_pattern = re.compile(r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$')
            if not url_pattern.match(v.strip()):
                raise ValueError("Invalid URL format")
        return v.strip() if v else None

class SkillLevel(str, Enum):
    """Skill proficiency levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class SkillEntry(BaseModel):
    """Individual skill entry"""

    name: str = Field(..., description="Skill name")
    level: Optional[SkillLevel] = Field(SkillLevel.INTERMEDIATE, description="Proficiency level")
    years_experience: Optional[float] = Field(None, ge=0, description="Years of experience")
    last_used: Optional[date] = Field(None, description="When skill was last used")
    certifications: Optional[List[str]] = Field(default_factory=list, description="Related certifications")

    @validator("name")
    def validate_name(cls, v):
        """Validate skill name"""
        if not v or not v.strip():
            raise ValueError("Skill name cannot be empty")
        return v.strip().title()

    @validator("years_experience")
    def validate_experience(cls, v):
        """Validate years of experience"""
        if v is not None and v > 50:
            raise ValueError("Years of experience cannot exceed 50")
        return v

class SkillsByCategory(BaseModel):
    """Skills organized by category"""

    programming_languages: Optional[List[SkillEntry]] = Field(default_factory=list, description="Programming languages")
    frameworks: Optional[List[SkillEntry]] = Field(default_factory=list, description="Frameworks and libraries")
    databases: Optional[List[SkillEntry]] = Field(default_factory=list, description="Database systems")
    cloud_platforms: Optional[List[SkillEntry]] = Field(default_factory=list, description="Cloud platforms")
    devops_tools: Optional[List[SkillEntry]] = Field(default_factory=list, description="DevOps tools")
    methodologies: Optional[List[SkillEntry]] = Field(default_factory=list, description="Methodologies and practices")
    data_science: Optional[List[SkillEntry]] = Field(default_factory=list, description="Data science tools")
    other: Optional[List[SkillEntry]] = Field(default_factory=list, description="Other skills")

    def get_all_skills(self) -> List[SkillEntry]:
        """Get all skills as a flat list"""
        all_skills = []
        for category_skills in self.__dict__.values():
            if isinstance(category_skills, list):
                all_skills.extend(category_skills)
        return all_skills

    def get_skill_names(self) -> List[str]:
        """Get all skill names"""
        return [skill.name for skill in self.get_all_skills()]

    def add_skill(self, skill: SkillEntry, category: str):
        """Add a skill to a specific category"""
        if hasattr(self, category):
            category_skills = getattr(self, category)
            if category_skills is None:
                category_skills = []
                setattr(self, category, category_skills)

            # Avoid duplicates
            existing_names = [s.name for s in category_skills]
            if skill.name not in existing_names:
                category_skills.append(skill)

class EmploymentType(str, Enum):
    """Employment type options"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"
    VOLUNTEER = "volunteer"

class ExperienceEntry(StandardModel):
    """Work experience entry"""

    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    employment_type: Optional[EmploymentType] = Field(EmploymentType.FULL_TIME, description="Employment type")
    start_date: date = Field(..., description="Start date")
    end_date: Optional[date] = Field(None, description="End date (None for current)")
    current: bool = Field(False, description="Whether this is current employment")
    description: Optional[str] = Field(None, description="Job description")
    achievements: Optional[List[str]] = Field(default_factory=list, description="Key achievements")
    skills_used: Optional[List[str]] = Field(default_factory=list, description="Skills used in this role")
    responsibilities: Optional[List[str]] = Field(default_factory=list, description="Key responsibilities")

    @validator("company", "title")
    def validate_name_fields(cls, v):
        """Validate company and title fields"""
        if not v or not v.strip():
            raise ValueError("Company and title cannot be empty")
        return v.strip()

    @validator("end_date")
    def validate_dates(cls, v, values):
        """Validate date consistency"""
        if v is not None:
            start_date = values.get("start_date")
            if start_date and v < start_date:
                raise ValueError("End date cannot be before start date")
        return v

    @validator("current")
    def validate_current_employment(cls, v, values):
        """Validate current employment flag"""
        if v:
            # If current, end_date should be None
            if values.get("end_date") is not None:
                raise ValueError("Current employment cannot have an end date")
        return v

    def get_duration_months(self) -> Optional[int]:
        """Calculate duration in months"""
        end = self.end_date or date.today()
        start = self.start_date

        months = (end.year - start.year) * 12 + (end.month - start.month)
        return max(0, months)

    def get_duration_years(self) -> float:
        """Calculate duration in years"""
        months = self.get_duration_months()
        return round(months / 12.0, 1) if months else 0.0

class EducationLevel(str, Enum):
    """Education level options"""
    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    POSTDOCTORAL = "postdoctoral"
    CERTIFICATE = "certificate"
    BOOTCAMP = "bootcamp"

class EducationEntry(StandardModel):
    """Education entry"""

    institution: str = Field(..., description="Educational institution name")
    degree: str = Field(..., description="Degree or program name")
    level: Optional[EducationLevel] = Field(None, description="Education level")
    field_of_study: Optional[str] = Field(None, description="Field of study")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    current: bool = Field(False, description="Whether currently enrolled")
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="Grade point average")
    honors: Optional[List[str]] = Field(default_factory=list, description="Honors and awards")
    coursework: Optional[List[str]] = Field(default_factory=list, description="Relevant coursework")
    activities: Optional[List[str]] = Field(default_factory=list, description="Extracurricular activities")

    @validator("institution", "degree")
    def validate_required_fields(cls, v):
        """Validate required fields"""
        if not v or not v.strip():
            raise ValueError("Institution and degree cannot be empty")
        return v.strip()

    @validator("end_date")
    def validate_dates(cls, v, values):
        """Validate date consistency"""
        if v is not None:
            start_date = values.get("start_date")
            if start_date and v < start_date:
                raise ValueError("End date cannot be before start date")
        return v

    def get_duration_years(self) -> Optional[float]:
        """Calculate duration in years"""
        if not self.start_date:
            return None

        end = self.end_date or date.today()
        years = (end.year - self.start_date.year) + ((end.month - self.start_date.month) / 12.0)
        return max(0.0, round(years, 1))

class ProjectType(str, Enum):
    """Project type options"""
    PERSONAL = "personal"
    PROFESSIONAL = "professional"
    ACADEMIC = "academic"
    OPEN_SOURCE = "open_source"

class ProjectEntry(StandardModel):
    """Project entry"""

    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    type: Optional[ProjectType] = Field(ProjectType.PERSONAL, description="Project type")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    current: bool = Field(False, description="Whether project is ongoing")
    url: Optional[str] = Field(None, description="Project URL")
    github_url: Optional[str] = Field(None, description="GitHub repository URL")
    technologies: Optional[List[str]] = Field(default_factory=list, description="Technologies used")
    achievements: Optional[List[str]] = Field(default_factory=list, description="Key achievements")
    role: Optional[str] = Field(None, description="Role in the project")
    team_size: Optional[int] = Field(None, ge=1, description="Team size")

    @validator("name", "description")
    def validate_required_fields(cls, v):
        """Validate required fields"""
        if not v or not v.strip():
            raise ValueError("Project name and description cannot be empty")
        return v.strip()

    @validator("url", "github_url")
    def validate_urls(cls, v):
        """Validate URLs"""
        if v is not None:
            import re
            url_pattern = re.compile(r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$')
            if not url_pattern.match(v.strip()):
                raise ValueError("Invalid URL format")
        return v.strip() if v else None

class CertificationEntry(StandardModel):
    """Certification entry"""

    name: str = Field(..., description="Certification name")
    issuer: str = Field(..., description="Issuing organization")
    issue_date: Optional[date] = Field(None, description="Issue date")
    expiry_date: Optional[date] = Field(None, description="Expiry date")
    credential_id: Optional[str] = Field(None, description="Credential ID")
    credential_url: Optional[str] = Field(None, description="Credential verification URL")

    @validator("name", "issuer")
    def validate_required_fields(cls, v):
        """Validate required fields"""
        if not v or not v.strip():
            raise ValueError("Certification name and issuer cannot be empty")
        return v.strip()

    @validator("expiry_date")
    def validate_dates(cls, v, values):
        """Validate date consistency"""
        if v is not None:
            issue_date = values.get("issue_date")
            if issue_date and v < issue_date:
                raise ValueError("Expiry date cannot be before issue date")
        return v

    def is_expired(self) -> bool:
        """Check if certification is expired"""
        if self.expiry_date is None:
            return False
        return date.today() > self.expiry_date

    def is_valid(self) -> bool:
        """Check if certification is currently valid"""
        if self.issue_date is None:
            return False
        if self.expiry_date is None:
            return True
        return not self.is_expired()

class UserProfile(StandardModel):
    """Comprehensive user profile"""

    name: str = Field(..., description="Full name")
    contact: ContactInfo = Field(..., description="Contact information")
    summary: Optional[str] = Field(None, description="Professional summary")
    experience: Optional[List[ExperienceEntry]] = Field(default_factory=list, description="Work experience")
    education: Optional[List[EducationEntry]] = Field(default_factory=list, description="Education history")
    skills: Optional[SkillsByCategory] = Field(default_factory=SkillsByCategory, description="Skills by category")
    projects: Optional[List[ProjectEntry]] = Field(default_factory=list, description="Projects")
    certifications: Optional[List[CertificationEntry]] = Field(default_factory=list, description="Certifications")
    languages: Optional[List[Dict[str, Union[str, int]]]] = Field(default_factory=list, description="Languages spoken")
    interests: Optional[List[str]] = Field(default_factory=list, description="Professional interests")
    availability: Optional[str] = Field(None, description="Availability status")
    salary_expectations: Optional[Dict[str, Any]] = Field(None, description="Salary expectations")
    preferred_locations: Optional[List[str]] = Field(default_factory=list, description="Preferred work locations")
    work_preferences: Optional[Dict[str, Any]] = Field(None, description="Work preferences")

    @validator("name")
    def validate_name(cls, v):
        """Validate name"""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        if len(v.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")
        return v.strip()

    @validator("summary")
    def validate_summary(cls, v):
        """Validate summary length"""
        if v is not None:
            if len(v.strip()) < 50:
                raise ValueError("Summary should be at least 50 characters")
            if len(v) > 500:
                raise ValueError("Summary should not exceed 500 characters")
        return v.strip() if v else None

    def get_total_experience_years(self) -> float:
        """Calculate total years of experience"""
        if not self.experience:
            return 0.0

        total_months = sum(exp.get_duration_months() or 0 for exp in self.experience)
        return round(total_months / 12.0, 1)

    def get_current_position(self) -> Optional[str]:
        """Get current position title"""
        if not self.experience:
            return None

        current_exp = [exp for exp in self.experience if exp.current]
        return current_exp[0].title if current_exp else None

    def get_current_company(self) -> Optional[str]:
        """Get current company"""
        if not self.experience:
            return None

        current_exp = [exp for exp in self.experience if exp.current]
        return current_exp[0].company if current_exp else None

    def get_education_level(self) -> Optional[EducationLevel]:
        """Get highest education level"""
        if not self.education:
            return None

        level_order = {
            EducationLevel.HIGH_SCHOOL: 0,
            EducationLevel.ASSOCIATE: 1,
            EducationLevel.BACHELOR: 2,
            EducationLevel.MASTER: 3,
            EducationLevel.PHD: 4,
            EducationLevel.POSTDOCTORAL: 5
        }

        highest_level = None
        highest_score = -1

        for edu in self.education:
            if edu.level and level_order.get(edu.level, -1) > highest_score:
                highest_level = edu.level
                highest_score = level_order[edu.level]

        return highest_level

    def get_skill_count(self) -> int:
        """Get total number of skills"""
        if not self.skills:
            return 0
        return len(self.skills.get_all_skills())

    def is_complete_profile(self) -> bool:
        """Check if profile is reasonably complete"""
        required_fields = [
            self.name,
            self.contact.email,
            self.summary,
            len(self.experience or []) > 0,
            len(self.education or []) > 0,
            self.get_skill_count() > 5
        ]

        return all(required_fields)

    def get_completion_percentage(self) -> float:
        """Get profile completion percentage"""
        total_weight = 100
        earned_weight = 0

        # Basic info (30%)
        if self.name and len(self.name) > 2:
            earned_weight += 10
        if self.contact.email:
            earned_weight += 10
        if self.summary and len(self.summary) >= 50:
            earned_weight += 10

        # Experience (25%)
        if self.experience:
            exp_weight = min(25, len(self.experience) * 5)
            earned_weight += exp_weight

        # Education (15%)
        if self.education:
            edu_weight = min(15, len(self.education) * 5)
            earned_weight += edu_weight

        # Skills (20%)
        skill_count = self.get_skill_count()
        if skill_count > 0:
            skill_weight = min(20, skill_count * 2)
            earned_weight += skill_weight

        # Additional info (10%)
        if self.projects:
            earned_weight += 5
        if self.certifications:
            earned_weight += 5

        return round(earned_weight, 1)
