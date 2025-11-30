# RG Resume Strategy for L1 planning
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

@dataclass
class SchemaVersion:
    """Schema version information for compatibility"""
    version: str
    compatible: bool = True
    errors: List[str] = field(default_factory=list)

def validate_schema_version(schema: Dict[str, Any], expected_version: str = "v1", model_type: Any = None) -> SchemaVersion:
    """Validate schema version compatibility"""
    # Handle different object types
    if hasattr(schema, 'model_dump'):
        schema_dict = schema.model_dump()
    elif hasattr(schema, 'dict'):
        schema_dict = schema.dict()
    elif hasattr(schema, '__dataclass_fields__'):
        schema_dict = asdict(schema)
    else:
        schema_dict = schema

    schema_version = schema_dict.get("schema_version", "v1")

    # Check for version mismatch
    if schema_version != expected_version:
        return SchemaVersion(
            version=schema_version,
            compatible=False,
            errors=[f"Expected schema_version {expected_version}, got {schema_version}"]
        )

    return SchemaVersion(version=schema_version, compatible=True)

class ResumeSection(Enum):
    """Resume section identifiers"""
    K0_CONTACT = "K0_CONTACT"
    K1_HEADLINE = "K1_HEADLINE"
    K2_SUMMARY = "K2_SUMMARY"
    K3_EXPERIENCE = "K3_EXPERIENCE"
    K4_EDUCATION = "K4_EDUCATION"
    K5_SKILLS = "K5_SKILLS"
    K6_PROJECTS = "K6_PROJECTS"
    K7_CERTIFICATIONS = "K7_CERTIFICATIONS"
    K8_ADDITIONAL = "K8_ADDITIONAL"

@dataclass
class ThematicAnalysis:
    """Job description thematic analysis results"""
    themes: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    skills_required: List[str] = field(default_factory=list)
    experience_level: str = "mid"
    industry: Optional[str] = None
    company_intelligence: Dict = field(default_factory=dict)
    competitive_positioning: Dict = field(default_factory=dict)
    narrative_mining: Dict = field(default_factory=dict)
    signal_score: float = 0.0
    analysis_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    schema_version: str = "v1"

@dataclass
class ResumeStrategy:
    """Resume strategy definition with enhanced analysis"""
    strategy_id: str = ""
    target_role: str = ""
    optimization_focus: List[str] = None
    formatting_style: str = ""
    content_priorities: List[str] = None
    bullet_selection_strategy: str = ""
    thematic_analysis: Optional[ThematicAnalysis] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.optimization_focus is None:
            self.optimization_focus = []
        if self.content_priorities is None:
            self.content_priorities = []
        if self.metadata is None:
            self.metadata = {}

class RGResumeStrategy:
    """Resume strategy planner with real business logic"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.role_strategies = self._initialize_role_strategies()

    def _initialize_role_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize role-specific strategies based on real resume data"""
        return {
            "ai_engineer": {
                "optimization_focus": ["technical_skills", "project_impact", "innovation"],
                "formatting_style": "technical_clean",
                "content_priorities": ["ai_projects", "ml_models", "technical_leadership"],
                "bullet_selection_strategy": "technical_achievement",
                "keywords": ["machine learning", "ai", "llm", "models", "algorithms", "architecture"]
            },
            "technical_lead": {
                "optimization_focus": ["leadership", "architecture", "team_impact"],
                "formatting_style": "leadership_focused",
                "content_priorities": ["leadership", "architecture", "business_impact"],
                "bullet_selection_strategy": "leadership_quantified",
                "keywords": ["led", "architected", "built", "designed", "managed", "scaled"]
            },
            "executive": {
                "optimization_focus": ["business_impact", "strategic_leadership", "revenue"],
                "formatting_style": "executive_summary",
                "content_priorities": ["strategic_impact", "partnerships", "transformation"],
                "bullet_selection_strategy": "business_outcomes",
                "keywords": ["strategic", "leadership", "partnership", "transformation", "revenue", "growth"]
            },
            "data_scientist": {
                "optimization_focus": ["analytics", "modeling", "insights"],
                "formatting_style": "analytical_detailed",
                "content_priorities": ["data_analysis", "statistical_modeling", "business_insights"],
                "bullet_selection_strategy": "quantified_insights",
                "keywords": ["data", "analytics", "models", "statistical", "analysis", "insights"]
            }
        }

    def create_strategy(self, target_role: str, experience_level: str,
                        job_description: Optional[str] = None) -> ResumeStrategy:
        """Create enhanced resume strategy with thematic analysis and validation"""

        # Get base strategy
        base_strategy = self.role_strategies.get(target_role.lower(),
            self.role_strategies["ai_engineer"])

        # Create thematic analysis if job description provided
        thematic = None
        if job_description:
            thematic = self._analyze_job_themes(job_description, target_role)
            # Validate schema version
            version_check = validate_schema_version(thematic, expected_version="v1")
            if not version_check.compatible:
                # Log version mismatch but continue with default analysis
                print(f"Warning: ThematicAnalysis schema version mismatch: {version_check.errors}")

        # Enhanced strategy with thematic insights
        strategy = ResumeStrategy(
            strategy_id=f"strategy_{target_role}_{experience_level}",
            target_role=target_role,
            optimization_focus=base_strategy["optimization_focus"],
            formatting_style=base_strategy["formatting_style"],
            content_priorities=base_strategy["content_priorities"],
            bullet_selection_strategy=base_strategy["bullet_selection_strategy"],
            thematic_analysis=thematic,
            metadata={
                "experience_level": experience_level,
                "has_thematic_analysis": thematic is not None,
                "created_at": datetime.now().isoformat(),
                "schema_version": "v1"
            }
        )

        return strategy

    def _analyze_job_themes(self, job_description: str, target_role: str) -> ThematicAnalysis:
        """Analyze job description for themes and competitive intelligence"""

        # Extract keywords from job description
        jd_keywords = self._extract_keywords(job_description)

        # Role-specific theme analysis
        role_themes = {
            "ai_engineer": ["machine learning", "deep learning", "production systems", "model deployment"],
            "technical_lead": ["architecture", "scalability", "team leadership", "technical strategy"],
            "executive": ["business strategy", "leadership", "revenue growth", "digital transformation"],
            "data_scientist": ["analytics", "data modeling", "insights", "statistical analysis"]
        }

        # Calculate signal score based on keyword overlap
        themes = role_themes.get(target_role.lower(), [])
        matched_themes = [theme for theme in themes if theme.lower() in job_description.lower()]
        signal_score = len(matched_themes) / len(themes) if themes else 0.0

        # Industry detection
        industry_indicators = {
            "financial_services": ["banking", "finance", "trading", "risk", "compliance"],
            "healthcare": ["medical", "health", "clinical", "pharmaceutical", "healthcare"],
            "technology": ["software", "technology", "saas", "platform", "digital"],
            "retail": ["retail", "ecommerce", "consumer", "merchandise", "sales"]
        }

        detected_industry = None
        for industry, indicators in industry_indicators.items():
            if any(indicator in job_description.lower() for indicator in indicators):
                detected_industry = industry
                break

        return ThematicAnalysis(
            themes=matched_themes,
            keywords=jd_keywords,
            skills_required=self._extract_skills(job_description),
            experience_level=self._infer_experience_level(job_description),
            industry=detected_industry,
            company_intelligence={"size": "unknown", "type": "unknown"},
            competitive_positioning={"differentiation_opportunities": matched_themes},
            narrative_mining={"key_phrases": jd_keywords[:5]},
            signal_score=signal_score
        )

    def optimize_strategy(self, strategy: ResumeStrategy, feedback_data: Dict[str, Any]) -> ResumeStrategy:
        """Optimize strategy based on feedback with real business logic"""
        # Add industry-specific optimizations
        industry = feedback_data.get("industry", "technology")

        if industry == "financial_services":
            strategy.optimization_focus.extend(["regulatory_compliance", "risk_management"])
            strategy.metadata["industry_focus"] = "financial_services"
        elif industry == "healthcare":
            strategy.optimization_focus.extend(["healthcare_tech", "compliance"])
            strategy.metadata["industry_focus"] = "healthcare"

        # Add seniority-based adjustments
        seniority = feedback_data.get("seniority", "mid")
        if seniority in ["senior", "executive"]:
            strategy.content_priorities.insert(0, "strategic_impact")
            strategy.metadata["seniority_adjustment"] = True

        strategy.metadata["optimized"] = True
        return strategy

    def get_section_recommendations(self, target_role: str) -> List[str]:
        """Get section recommendations for target role with real business logic"""
        base_sections = [
            "Professional Summary",
            "Technical Skills",
            "Work Experience",
            "Education",
            "Certifications"
        ]

        role_specific_sections = {
            "ai_engineer": ["AI/ML Projects", "Research & Publications"],
            "technical_lead": ["Leadership Experience", "Technical Architecture"],
            "executive": ["Executive Summary", "Strategic Initiatives", "Board Experience"],
            "data_scientist": ["Analytics Projects", "Technical Publications"]
        }

        additional = role_specific_sections.get(target_role.lower(), [])
        return base_sections + additional

    def get_bullet_selection_criteria(self, strategy: ResumeStrategy) -> Dict[str, Any]:
        """Get bullet selection criteria based on strategy"""
        criteria_map = {
            "technical_achievement": {
                "must_contain": ["built", "developed", "implemented", "architected"],
                "should_contain": ["% improvement", "reduced", "increased", "optimized"],
                "priority_keywords": ["machine learning", "ai", "models", "algorithms"]
            },
            "leadership_quantified": {
                "must_contain": ["led", "managed", "directed", "oversaw"],
                "should_contain": ["team", "revenue", "cost", "efficiency"],
                "priority_keywords": ["leadership", "strategy", "transformation"]
            },
            "business_outcomes": {
                "must_contain": ["drove", "achieved", "delivered", "generated"],
                "should_contain": ["$", "%", "growth", "revenue"],
                "priority_keywords": ["strategic", "partnership", "transformation"]
            },
            "quantified_insights": {
                "must_contain": ["analyzed", "modeled", "predicted", "identified"],
                "should_contain": ["%", "accuracy", "insights", "patterns"],
                "priority_keywords": ["data", "analytics", "statistical", "insights"]
            }
        }

        return criteria_map.get(strategy.bullet_selection_strategy, criteria_map["technical_achievement"])

    def estimate_resume_strength(self, strategy: ResumeStrategy, candidate_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate resume strength based on strategy and profile"""
        years_experience = candidate_profile.get("years_experience", 0)
        relevant_skills = candidate_profile.get("skills", [])
        target_keywords = strategy.metadata.get("keywords", [])

        # Calculate keyword match percentage
        skill_matches = sum(1 for skill in relevant_skills if any(keyword in skill.lower() for keyword in target_keywords))
        keyword_match_pct = (skill_matches / len(target_keywords)) * 100 if target_keywords else 0

        # Calculate experience fit
        experience_fit = min(100, (years_experience / 10) * 100)  # 10 years = 100%

        # Overall strength
        overall_strength = (keyword_match_pct * 0.6) + (experience_fit * 0.4)

        return {
            "overall_strength": round(overall_strength, 1),
            "keyword_match_pct": round(keyword_match_pct, 1),
            "experience_fit": round(experience_fit, 1),
            "recommendations": self._get_strength_recommendations(overall_strength, keyword_match_pct)
        }

    def _get_strength_recommendations(self, overall_strength: float, keyword_match: float) -> List[str]:
        """Get recommendations based on strength analysis"""
        recommendations = []

        if overall_strength < 60:
            recommendations.append("Consider adding more quantified achievements")
            recommendations.append("Highlight relevant technical skills more prominently")
        elif overall_strength < 80:
            recommendations.append("Add specific metrics and business impact")
            recommendations.append("Consider expanding project descriptions")

        if keyword_match < 50:
            recommendations.append("Align skills more closely with target role keywords")

        return recommendations

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction based on common resume terms
        keyword_patterns = [
            "python", "java", "javascript", "aws", "azure", "docker", "kubernetes",
            "machine learning", "ai", "deep learning", "data science", "analytics",
            "leadership", "management", "strategy", "architecture", "development",
            "engineering", "software", "technology", "cloud", "devops", "agile"
        ]

        found_keywords = []
        text_lower = text.lower()
        for pattern in keyword_patterns:
            if pattern in text_lower:
                found_keywords.append(pattern)

        return found_keywords

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from job description"""
        skills = []

        # Technical skills indicators
        tech_indicators = ["experience with", "proficient in", "skilled in", "knowledge of"]

        for indicator in tech_indicators:
            if indicator in text.lower():
                # Simple extraction - in real implementation would use NLP
                words = text.lower().split(indicator)
                if len(words) > 1:
                    potential_skills = words[1].split()[:3]  # Take next 3 words
                    skills.extend([skill.strip().strip(',') for skill in potential_skills if len(skill) > 2])

        return list(set(skills))  # Remove duplicates

    def _infer_experience_level(self, text: str) -> str:
        """Infer experience level from job description"""
        text_lower = text.lower()

        if any(term in text_lower for term in ["entry level", "junior", "0-2 years", "recent graduate"]):
            return "entry"
        elif any(term in text_lower for term in ["mid level", "3-5 years", "intermediate"]):
            return "mid"
        elif any(term in text_lower for term in ["senior", "5+ years", "lead", "principal"]):
            return "senior"
        elif any(term in text_lower for term in ["executive", "director", "vp", "c-level", "10+ years"]):
            return "executive"

        return "mid"  # Default
