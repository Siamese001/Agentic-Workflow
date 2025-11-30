# RG Resume Inputs for L1 planning
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class ResumeInput:
    """Resume input data structure with comprehensive fields"""
    resume_id: str = ""
    target_role: str = ""
    experience_level: str = "mid"  # junior, mid, senior, executive
    target_company: Optional[str] = None
    job_description: Optional[str] = None
    personal_info: Dict[str, Any] = None
    professional_experience: List[Dict[str, Any]] = None
    skills: Dict[str, List[str]] = None
    education: List[Dict[str, Any]] = None
    preferences: Dict[str, Any] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.personal_info is None:
            self.personal_info = {}
        if self.professional_experience is None:
            self.professional_experience = []
        if self.skills is None:
            self.skills = {"technical": [], "soft": [], "tools": [], "certifications": []}
        if self.education is None:
            self.education = []
        if self.preferences is None:
            self.preferences = {"format": "modern", "length": "one_page", "style": "professional"}
        if self.metadata is None:
            self.metadata = {}

class RGResumeInputs:
    """Resume inputs processor for planning with comprehensive validation and enrichment"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.validation_rules = self._initialize_validation_rules()
        self.market_data_cache = {}
        self.role_templates = self._load_role_templates()

    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize comprehensive validation rules"""
        return {
            "required_fields": ["resume_id", "target_role", "personal_info"],
            "experience_levels": ["junior", "mid", "senior", "executive"],
            "max_bullets_per_experience": 5,
            "max_chars_per_bullet": 600,
            "max_summary_chars": 2000,
            "required_personal_fields": ["name", "email", "phone"],
            "valid_email_pattern": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "valid_phone_pattern": r'^[\d\s\-\+\(\)]{10,}$'
        }

    def _load_role_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load role-specific templates and requirements"""
        return {
            "ai_engineer": {
                "required_skills": ["Python", "Machine Learning", "Deep Learning"],
                "preferred_skills": ["TensorFlow", "PyTorch", "AWS", "Docker"],
                "experience_keywords": ["AI", "ML", "algorithms", "models", "deployment"],
                "summary_template": "AI Engineer with {years} years of experience in {key_areas}"
            },
            "technical_lead": {
                "required_skills": ["System Design", "Leadership", "Architecture"],
                "preferred_skills": ["Cloud Computing", "DevOps", "Agile", "Team Management"],
                "experience_keywords": ["led", "architected", "managed", "scaled"],
                "summary_template": "Technical Lead with {years} years of experience in {key_areas}"
            },
            "data_scientist": {
                "required_skills": ["Python", "Statistics", "Machine Learning"],
                "preferred_skills": ["R", "SQL", "Tableau", "A/B Testing"],
                "experience_keywords": ["data", "analytics", "models", "insights", "statistical"],
                "summary_template": "Data Scientist with {years} years of experience in {key_areas}"
            },
            "executive": {
                "required_skills": ["Leadership", "Strategy", "Business Development"],
                "preferred_skills": ["P&L Management", "Stakeholder Relations", "Transformation"],
                "experience_keywords": ["strategic", "leadership", "revenue", "transformation"],
                "summary_template": "Executive leader with {years} years of experience in {key_areas}"
            }
        }

    def validate_inputs(self, inputs: ResumeInput) -> Dict[str, Any]:
        """Comprehensive validation of resume inputs"""
        errors = []
        warnings = []

        # Validate required fields
        for field in self.validation_rules["required_fields"]:
            if not getattr(inputs, field, None):
                errors.append(f"Missing required field: {field}")

        # Validate experience level
        if inputs.experience_level not in self.validation_rules["experience_levels"]:
            errors.append(f"Invalid experience level: {inputs.experience_level}")

        # Validate personal info
        if inputs.personal_info:
            for req_field in self.validation_rules["required_personal_fields"]:
                if req_field not in inputs.personal_info:
                    errors.append(f"Missing required personal field: {req_field}")

            # Validate email format
            email = inputs.personal_info.get("email", "")
            if email and not re.match(self.validation_rules["valid_email_pattern"], email):
                errors.append("Invalid email format")

            # Validate phone format
            phone = inputs.personal_info.get("phone", "")
            if phone and not re.match(self.validation_rules["valid_phone_pattern"], phone):
                warnings.append("Phone number format may need review")

        # Validate professional experience
        if inputs.professional_experience:
            for i, exp in enumerate(inputs.professional_experience):
                bullets = exp.get("bullet_pool", exp.get("highlights", []))
                if len(bullets) > self.validation_rules["max_bullets_per_experience"]:
                    warnings.append(f"Experience {i+1} has {len(bullets)} bullets (max: {self.validation_rules['max_bullets_per_experience']})")

                for j, bullet in enumerate(bullets):
                    if len(bullet) > self.validation_rules["max_chars_per_bullet"]:
                        warnings.append(f"Experience {i+1}, bullet {j+1} exceeds {self.validation_rules['max_chars_per_bullet']} characters")

        # Validate skills
        if inputs.skills:
            if len(inputs.skills.get("technical", [])) < 3:
                warnings.append("Consider adding more technical skills")
            if len(inputs.skills.get("soft", [])) < 2:
                warnings.append("Consider adding more soft skills")

        # Role-specific validation
        role_template = self.role_templates.get(inputs.target_role.lower().replace(" ", "_"))
        if role_template:
            missing_skills = []
            for req_skill in role_template["required_skills"]:
                if req_skill not in inputs.skills.get("technical", []):
                    missing_skills.append(req_skill)
            if missing_skills:
                warnings.append(f"Missing key skills for {inputs.target_role}: {missing_skills}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "metadata": {
                "validated_at": datetime.now().isoformat(),
                "validation_score": max(0, 100 - (len(errors) * 20) - (len(warnings) * 5))
            }
        }

    def enrich_inputs(self, inputs: ResumeInput, market_data: Dict[str, Any] = None) -> ResumeInput:
        """Enrich inputs with market data and role insights"""
        market_data = market_data or self._get_market_data(inputs.target_role)

        # Add market insights to metadata
        inputs.metadata["enriched"] = True
        inputs.metadata["market_data"] = market_data
        inputs.metadata["enrichment_timestamp"] = datetime.now().isoformat()

        # Add role-specific keywords
        role_template = self.role_templates.get(inputs.target_role.lower().replace(" ", "_"))
        if role_template:
            inputs.metadata["role_keywords"] = role_template["experience_keywords"]
            inputs.metadata["required_skills"] = role_template["required_skills"]
            inputs.metadata["preferred_skills"] = role_template["preferred_skills"]

        # Add experience level insights
        inputs.metadata["experience_insights"] = self._get_experience_insights(inputs.experience_level)

        # Add skill gap analysis
        if inputs.skills and role_template:
            skill_gap = self._analyze_skill_gap(inputs.skills, role_template)
            inputs.metadata["skill_gap_analysis"] = skill_gap

        return inputs

    def _get_market_data(self, target_role: str) -> Dict[str, Any]:
        """Get market data for target role"""
        if target_role in self.market_data_cache:
            return self.market_data_cache[target_role]

        # Simulate market data retrieval
        market_data = {
            "demand_level": "high" if "engineer" in target_role.lower() else "medium",
            "average_salary": self._estimate_salary(target_role),
            "top_companies": self._get_top_companies(target_role),
            "growth_trends": self._get_growth_trends(target_role),
            "required_certifications": self._get_required_certifications(target_role)
        }

        self.market_data_cache[target_role] = market_data
        return market_data

    def _estimate_salary(self, target_role: str) -> Dict[str, int]:
        """Estimate salary ranges by experience level"""
        base_salaries = {
            "ai_engineer": {"junior": 120000, "mid": 150000, "senior": 180000, "executive": 250000},
            "technical_lead": {"junior": 100000, "mid": 130000, "senior": 160000, "executive": 220000},
            "data_scientist": {"junior": 110000, "mid": 140000, "senior": 170000, "executive": 230000},
            "executive": {"junior": 80000, "mid": 120000, "senior": 180000, "executive": 300000}
        }
        return base_salaries.get(target_role.lower().replace(" ", "_"), {"mid": 100000})

    def _get_top_companies(self, target_role: str) -> List[str]:
        """Get top companies for target role"""
        company_data = {
            "ai_engineer": ["Google", "Microsoft", "Amazon", "OpenAI", "Meta"],
            "technical_lead": ["Microsoft", "Amazon", "Google", "Apple", "Netflix"],
            "data_scientist": ["Google", "Meta", "Amazon", "Netflix", "Apple"],
            "executive": ["Fortune 500 companies", "Tech startups", "Consulting firms"]
        }
        return company_data.get(target_role.lower().replace(" ", "_"), ["Tech companies"])

    def _get_growth_trends(self, target_role: str) -> List[str]:
        """Get growth trends for target role"""
        trends = {
            "ai_engineer": ["Machine Learning Ops", "LLM Engineering", "AI Ethics", "Edge AI"],
            "technical_lead": ["Cloud Architecture", "DevOps", "Microservices", "Kubernetes"],
            "data_scientist": ["Big Data", "AI/ML Integration", "Real-time Analytics", "Data Engineering"],
            "executive": ["Digital Transformation", "AI Strategy", "Remote Leadership", "Sustainability"]
        }
        return trends.get(target_role.lower().replace(" ", "_"), ["Technology trends"])

    def _get_required_certifications(self, target_role: str) -> List[str]:
        """Get required certifications for target role"""
        certs = {
            "ai_engineer": ["AWS Machine Learning", "Google Cloud AI", "Microsoft Azure AI"],
            "technical_lead": ["AWS Solutions Architect", "PMP", "Scrum Master"],
            "data_scientist": ["Google Data Analytics", "IBM Data Science", "Microsoft Data Science"],
            "executive": ["MBA", "Executive Leadership", "Digital Strategy"]
        }
        return certs.get(target_role.lower().replace(" ", "_"), ["Industry certifications"])

    def _get_experience_insights(self, experience_level: str) -> Dict[str, Any]:
        """Get insights based on experience level"""
        insights = {
            "junior": {
                "focus_areas": ["learning", "skill development", "team collaboration"],
                "expected_impact": ["supporting projects", "learning technologies", "contributing to codebase"],
                "career_progression": "2-3 years to mid-level"
            },
            "mid": {
                "focus_areas": ["independent work", "project ownership", "mentoring"],
                "expected_impact": ["leading small projects", "improving processes", "technical contributions"],
                "career_progression": "3-5 years to senior-level"
            },
            "senior": {
                "focus_areas": ["technical leadership", "architecture", "team mentoring"],
                "expected_impact": ["system design", "technical strategy", "team development"],
                "career_progression": "5+ years to executive or principal"
            },
            "executive": {
                "focus_areas": ["business strategy", "organizational leadership", "stakeholder management"],
                "expected_impact": ["business growth", "team scaling", "strategic direction"],
                "career_progression": "C-level trajectory"
            }
        }
        return insights.get(experience_level, insights["mid"])

    def _analyze_skill_gap(self, current_skills: Dict[str, List[str]], role_template: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze skill gaps for target role"""
        required_skills = role_template["required_skills"]
        preferred_skills = role_template["preferred_skills"]
        current_tech = current_skills.get("technical", [])

        missing_required = [skill for skill in required_skills if skill not in current_tech]
        missing_preferred = [skill for skill in preferred_skills if skill not in current_tech]

        skill_score = max(0, 100 - (len(missing_required) * 30) - (len(missing_preferred) * 10))

        return {
            "missing_required": missing_required,
            "missing_preferred": missing_preferred,
            "skill_match_score": skill_score,
            "recommendations": self._generate_skill_recommendations(missing_required, missing_preferred)
        }

    def _generate_skill_recommendations(self, missing_required: List[str], missing_preferred: List[str]) -> List[str]:
        """Generate skill development recommendations"""
        recommendations = []

        if missing_required:
            recommendations.append(f"Priority: Learn required skills - {', '.join(missing_required)}")

        if missing_preferred:
            recommendations.append(f"Consider: Add preferred skills - {', '.join(missing_preferred[:3])}")

        recommendations.extend([
            "Focus on hands-on projects to demonstrate skills",
            "Consider certifications for missing technical skills",
            "Highlight transferable skills from existing experience"
        ])

        return recommendations

    def create_input_template(self, role_category: str, experience_level: str = "mid") -> ResumeInput:
        """Create comprehensive input template for role category"""
        role_template = self.role_templates.get(role_category.lower(), {})

        return ResumeInput(
            resume_id=f"template_{role_category}_{experience_level}_{datetime.now().strftime('%Y%m%d')}",
            target_role=role_category.replace("_", " ").title(),
            experience_level=experience_level,
            personal_info={
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "(555) 123-4567",
                "linkedin": "linkedin.com/in/johndoe",
                "location": "San Francisco, CA"
            },
            professional_experience=[
                {
                    "company": "Tech Company",
                    "title": f"{role_category.replace('_', ' ').title()}",
                    "dates": {"start": "2020", "end": "2024"},
                    "location": "San Francisco, CA",
                    "bullet_pool": [
                        "Developed innovative solutions using cutting-edge technologies",
                        "Collaborated with cross-functional teams to deliver projects",
                        "Improved system performance and efficiency"
                    ]
                }
            ],
            skills={
                "technical": role_template.get("required_skills", ["Python", "Problem Solving"]),
                "soft": ["Communication", "Teamwork", "Problem Solving"],
                "tools": ["Git", "VS Code", "Docker"],
                "certifications": role_template.get("preferred_skills", [])[:2]
            },
            education=[
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "institution": "University Name",
                    "year": "2020"
                }
            ],
            preferences={
                "format": "modern",
                "length": "one_page" if experience_level in ["junior", "mid"] else "two_pages",
                "style": "professional",
                "sections": ["summary", "experience", "skills", "education"]
            },
            metadata={
                "template_category": role_category,
                "template_version": "1.0",
                "created_at": datetime.now().isoformat(),
                "auto_generated": True
            }
        )
