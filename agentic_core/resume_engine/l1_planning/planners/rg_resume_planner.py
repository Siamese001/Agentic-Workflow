# RG Resume Planner for L1 planning
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import re

from ..inputs.rg_resume_inputs import ResumeInput

@dataclass
class ResumePlan:
    """Comprehensive resume plan structure with detailed planning metadata"""
    plan_id: str = ""
    target_role: str = ""
    experience_level: str = "mid"
    target_company: Optional[str] = None
    sections: List[str] = None
    content_strategy: Dict[str, Any] = None
    section_priorities: Dict[str, int] = None
    timeline: Dict[str, Any] = None
    optimization_focus: List[str] = None
    keyword_strategy: Dict[str, Any] = None
    formatting_specifications: Dict[str, Any] = None
    compliance_requirements: Dict[str, Any] = None
    success_metrics: Dict[str, Any] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.sections is None:
            self.sections = ["professional_summary", "experience", "skills", "education"]
        if self.content_strategy is None:
            self.content_strategy = {}
        if self.section_priorities is None:
            self.section_priorities = {}
        if self.timeline is None:
            self.timeline = {}
        if self.optimization_focus is None:
            self.optimization_focus = ["impact", "keywords", "readability"]
        if self.keyword_strategy is None:
            self.keyword_strategy = {}
        if self.formatting_specifications is None:
            self.formatting_specifications = {}
        if self.compliance_requirements is None:
            self.compliance_requirements = {}
        if self.success_metrics is None:
            self.success_metrics = {}
        if self.metadata is None:
            self.metadata = {}

class RGResumePlanner:
    """Comprehensive resume planner engine with strategic planning capabilities"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.role_planning_templates = self._load_role_planning_templates()
        self.section_templates = self._load_section_templates()
        self.compliance_rules = self._load_compliance_rules()
        self.planning_history = []

    def _load_role_planning_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load role-specific planning templates"""
        return {
            "ai_engineer": {
                "section_priorities": {"skills": 1, "experience": 2, "summary": 3, "education": 4},
                "content_strategy": {
                    "focus": "technical_achievements",
                    "tone": "innovative",
                    "emphasis": ["ml_models", "algorithms", "deployment", "impact"]
                },
                "keyword_categories": ["technical_ml", "frameworks", "cloud", "algorithms"],
                "success_metrics": {
                    "technical_depth": 0.4,
                    "business_impact": 0.3,
                    "innovation": 0.3
                }
            },
            "technical_lead": {
                "section_priorities": {"experience": 1, "skills": 2, "summary": 3, "education": 4},
                "content_strategy": {
                    "focus": "leadership_achievements",
                    "tone": "authoritative",
                    "emphasis": ["architecture", "team_leadership", "scalability", "mentoring"]
                },
                "keyword_categories": ["leadership", "architecture", "process", "business"],
                "success_metrics": {
                    "leadership_demonstration": 0.4,
                    "technical_acumen": 0.3,
                    "business_impact": 0.3
                }
            },
            "data_scientist": {
                "section_priorities": {"experience": 1, "skills": 2, "summary": 3, "education": 4},
                "content_strategy": {
                    "focus": "analytical_achievements",
                    "tone": "analytical",
                    "emphasis": ["insights", "models", "statistics", "business_value"]
                },
                "keyword_categories": ["analytics", "statistics", "ml", "business"],
                "success_metrics": {
                    "analytical_depth": 0.4,
                    "business_insights": 0.3,
                    "technical_skills": 0.3
                }
            },
            "executive": {
                "section_priorities": {"summary": 1, "experience": 2, "education": 3, "skills": 4},
                "content_strategy": {
                    "focus": "strategic_impact",
                    "tone": "executive",
                    "emphasis": ["strategy", "leadership", "growth", "transformation"]
                },
                "keyword_categories": ["leadership", "strategy", "business", "finance"],
                "success_metrics": {
                    "strategic_impact": 0.5,
                    "leadership_demonstration": 0.3,
                    "business_growth": 0.2
                }
            }
        }

    def _load_section_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load section-specific planning templates"""
        return {
            "professional_summary": {
                "target_length": {"junior": 50, "mid": 100, "senior": 150, "executive": 200},
                "content_elements": ["years_experience", "key_expertise", "major_achievements", "career_objective"],
                "tone_guidelines": {
                    "junior": "eager_and_capable",
                    "mid": "confident_and_accomplished",
                    "senior": "expert_and_strategic",
                    "executive": "visionary_and_results_driven"
                }
            },
            "experience": {
                "max_bullets_per_role": 5,
                "bullet_length_range": {"min": 20, "max": 600},
                "required_elements": ["action_verb", "quantifiable_impact", "technical_skills", "business_context"],
                "chronological_order": True
            },
            "skills": {
                "categories": ["technical", "leadership", "tools", "certifications"],
                "max_skills_per_category": 10,
                "prioritization_method": "relevance_and_proficiency"
            },
            "education": {
                "include_gpa": True,
                "relevant_coursework_limit": 5,
                "honors_and_awards": True,
                "continuing_education": True
            }
        }

    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load platform-specific compliance rules"""
        return {
            "linkedin": {
                "max_bullets_per_experience": 5,
                "max_chars_per_bullet": 600,
                "max_summary_chars": 2000,
                "required_sections": ["experience", "education"],
                "recommended_sections": ["summary", "skills"]
            },
            "indeed": {
                "max_bullets_per_experience": 8,
                "max_chars_per_bullet": 800,
                "max_summary_chars": 3000,
                "format_preference": "chronological"
            },
            "ats_friendly": {
                "standard_section_names": True,
                "avoid_special_characters": True,
                "keyword_density_min": 0.02,
                "readability_score_min": 60
            }
        }

    def create_resume_plan(self, resume_input: ResumeInput) -> ResumePlan:
        """Create comprehensive resume plan based on input analysis"""
        plan_id = f"plan_{resume_input.target_role}_{resume_input.experience_level}_{datetime.now().strftime('%Y%m%d_%H%M')}"

        # Get role-specific template
        role_template = self.role_planning_templates.get(
            resume_input.target_role.lower().replace(" ", "_"),
            self.role_planning_templates["technical_lead"]
        )

        # Analyze input for planning decisions
        input_analysis = self._analyze_resume_input(resume_input)

        # Create comprehensive plan
        plan = ResumePlan(
            plan_id=plan_id,
            target_role=resume_input.target_role,
            experience_level=resume_input.experience_level,
            target_company=resume_input.target_company,
            sections=self._determine_sections(resume_input, input_analysis),
            content_strategy=self._create_content_strategy(resume_input, role_template, input_analysis),
            section_priorities=role_template["section_priorities"],
            timeline=self._create_timeline(resume_input, input_analysis),
            optimization_focus=self._determine_optimization_focus(resume_input, input_analysis),
            keyword_strategy=self._create_keyword_strategy(resume_input, role_template),
            formatting_specifications=self._create_formatting_specifications(resume_input),
            compliance_requirements=self._determine_compliance_requirements(resume_input),
            success_metrics=role_template["success_metrics"],
            metadata={
                "created_at": datetime.now().isoformat(),
                "input_analysis": input_analysis,
                "planning_confidence": self._calculate_planning_confidence(resume_input, input_analysis),
                "estimated_completion_date": self._estimate_completion_date(resume_input),
                "quality_targets": self._set_quality_targets(resume_input)
            }
        )

        # Store planning history
        self.planning_history.append({
            "plan_id": plan_id,
            "created_at": datetime.now().isoformat(),
            "input_summary": self._create_input_summary(resume_input),
            "planning_decisions": self._document_planning_decisions(plan, input_analysis)
        })

        return plan

    def _analyze_resume_input(self, resume_input: ResumeInput) -> Dict[str, Any]:
        """Comprehensive analysis of resume input for planning"""
        analysis = {
            "complexity_score": 0,
            "content_gaps": [],
            "strengths": [],
            "improvement_opportunities": [],
            "target_market_analysis": {},
            "competitive_positioning": {}
        }

        # Analyze experience complexity
        if resume_input.professional_experience:
            total_bullets = sum(len(exp.get("bullet_pool", exp.get("highlights", [])))
                              for exp in resume_input.professional_experience)
            analysis["complexity_score"] += min(total_bullets * 2, 40)

            # Analyze experience progression
            if len(resume_input.professional_experience) > 1:
                analysis["strengths"].append("career_progression")
            else:
                analysis["improvement_opportunities"].append("diversify_experience")

        # Analyze skills coverage
        if resume_input.skills:
            tech_skills = len(resume_input.skills.get("technical", []))
            soft_skills = len(resume_input.skills.get("soft", []))
            analysis["complexity_score"] += min((tech_skills + soft_skills) * 3, 30)

            if tech_skills >= 5:
                analysis["strengths"].append("strong_technical_skills")
            else:
                analysis["content_gaps"].append("more_technical_skills")

            if soft_skills >= 3:
                analysis["strengths"].append("well_rounded_skills")
            else:
                analysis["content_gaps"].append("more_soft_skills")

        # Analyze education
        if resume_input.education:
            analysis["complexity_score"] += min(len(resume_input.education) * 5, 20)
            has_advanced_degree = any(edu.get("degree", "").lower() in ["master", "phd", "mba"]
                                     for edu in resume_input.education)
            if has_advanced_degree:
                analysis["strengths"].append("advanced_education")

        # Analyze target market
        analysis["target_market_analysis"] = self._analyze_target_market(resume_input)

        # Competitive positioning
        analysis["competitive_positioning"] = self._analyze_competitive_positioning(resume_input)

        return analysis

    def _analyze_target_market(self, resume_input: ResumeInput) -> Dict[str, Any]:
        """Analyze target market for the role"""
        market_analysis = {
            "demand_level": "medium",
            "salary_range": {},
            "key_requirements": [],
            "growth_trends": [],
            "competition_level": "medium"
        }

        # Role-specific market analysis
        role_lower = resume_input.target_role.lower()
        if "engineer" in role_lower or "ai" in role_lower:
            market_analysis["demand_level"] = "high"
            market_analysis["key_requirements"] = ["technical_skills", "problem_solving", "innovation"]
            market_analysis["growth_trends"] = ["ai_ml", "cloud_computing", "automation"]
        elif "lead" in role_lower or "manager" in role_lower:
            market_analysis["demand_level"] = "high"
            market_analysis["key_requirements"] = ["leadership", "communication", "technical_acumen"]
            market_analysis["growth_trends"] = ["remote_leadership", "digital_transformation", "team_scaling"]
        elif "executive" in role_lower:
            market_analysis["demand_level"] = "medium"
            market_analysis["key_requirements"] = ["strategy", "business_acumen", "stakeholder_management"]
            market_analysis["growth_trends"] = ["digital_strategy", "sustainability", "global_leadership"]

        # Experience-level salary estimates
        salary_ranges = {
            "junior": {"min": 80000, "max": 120000},
            "mid": {"min": 120000, "max": 180000},
            "senior": {"min": 180000, "max": 250000},
            "executive": {"min": 250000, "max": 500000}
        }
        market_analysis["salary_range"] = salary_ranges.get(resume_input.experience_level, salary_ranges["mid"])

        return market_analysis

    def _analyze_competitive_positioning(self, resume_input: ResumeInput) -> Dict[str, Any]:
        """Analyze competitive positioning"""
        positioning = {
            "competitive_score": 0,
            "key_differentiators": [],
            "areas_to_improve": [],
            "market_fit": "good"
        }

        # Calculate competitive score
        score = 50  # Base score

        # Experience scoring
        if resume_input.professional_experience:
            years_experience = sum(
                self._estimate_years_experience(exp) for exp in resume_input.professional_experience
            )
            if resume_input.experience_level == "junior" and years_experience >= 3:
                score += 15
            elif resume_input.experience_level == "mid" and years_experience >= 5:
                score += 15
            elif resume_input.experience_level == "senior" and years_experience >= 8:
                score += 15
            elif resume_input.experience_level == "executive" and years_experience >= 12:
                score += 15

        # Skills scoring
        if resume_input.skills:
            tech_count = len(resume_input.skills.get("technical", []))
            if tech_count >= 8:
                score += 20
            elif tech_count >= 5:
                score += 10

        # Education scoring
        if resume_input.education:
            has_degree = any(edu.get("degree", "") for edu in resume_input.education)
            if has_degree:
                score += 10
            has_advanced = any(edu.get("degree", "").lower() in ["master", "phd", "mba"]
                              for edu in resume_input.education)
            if has_advanced:
                score += 5

        positioning["competitive_score"] = min(score, 100)

        # Determine market fit
        if positioning["competitive_score"] >= 80:
            positioning["market_fit"] = "excellent"
        elif positioning["competitive_score"] >= 60:
            positioning["market_fit"] = "good"
        else:
            positioning["market_fit"] = "needs_improvement"

        return positioning

    def _estimate_years_experience(self, experience: Dict[str, Any]) -> int:
        """Estimate years of experience from experience entry"""
        dates = experience.get("dates", {})
        if isinstance(dates, dict):
            start_year = dates.get("start", "")
            end_year = dates.get("end", "present")

            if start_year and isinstance(start_year, str):
                try:
                    start = int(start_year)
                    if end_year == "present":
                        end = datetime.now().year
                    else:
                        end = int(end_year) if end_year else datetime.now().year
                    return max(0, end - start)
                except ValueError:
                    return 2  # Default estimate
        return 2

    def _determine_sections(self, resume_input: ResumeInput, input_analysis: Dict[str, Any]) -> List[str]:
        """Determine optimal sections based on input analysis"""
        base_sections = ["professional_summary", "experience", "skills", "education"]

        # Add sections based on experience level and content
        if resume_input.experience_level in ["senior", "executive"]:
            base_sections.insert(-1, "leadership")

        if resume_input.experience_level == "executive":
            base_sections.insert(1, "executive_summary")
            base_sections.insert(-2, "board_experience")

        # Add projects section for technical roles
        if "engineer" in resume_input.target_role.lower() or "developer" in resume_input.target_role.lower():
            base_sections.insert(-2, "projects")

        # Add certifications if present
        if resume_input.skills and resume_input.skills.get("certifications"):
            base_sections.insert(-1, "certifications")

        # Add awards/honors if competitive position is strong
        if input_analysis["competitive_positioning"]["competitive_score"] >= 70:
            base_sections.insert(-1, "awards_honors")

        return base_sections

    def _create_content_strategy(self, resume_input: ResumeInput, role_template: Dict[str, Any],
                                input_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive content strategy"""
        strategy = role_template["content_strategy"].copy()

        # Customize based on input analysis
        if "strong_technical_skills" in input_analysis["strengths"]:
            strategy["technical_emphasis"] = "deep"

        if "career_progression" in input_analysis["strengths"]:
            strategy["narrative_approach"] = "growth_story"

        if input_analysis["competitive_positioning"]["market_fit"] == "excellent":
            strategy["confidence_level"] = "high"
        else:
            strategy["confidence_level"] = "moderate"

        # Add company-specific customization
        if resume_input.target_company:
            strategy["company_research"] = "required"
            strategy["customization_level"] = "high"

        return strategy

    def _create_timeline(self, resume_input: ResumeInput, input_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create realistic timeline for resume completion"""
        base_days = 7  # Base timeline

        # Adjust for complexity
        complexity_multiplier = 1 + (input_analysis["complexity_score"] / 100)

        # Adjust for experience level
        experience_multipliers = {
            "junior": 0.8,
            "mid": 1.0,
            "senior": 1.2,
            "executive": 1.5
        }

        total_days = int(base_days * complexity_multiplier * experience_multipliers[resume_input.experience_level])

        return {
            "total_days": total_days,
            "phases": {
                "research_and_analysis": max(1, int(total_days * 0.2)),
                "content_development": max(2, int(total_days * 0.5)),
                "formatting_and_refinement": max(1, int(total_days * 0.2)),
                "final_review": max(1, int(total_days * 0.1))
            },
            "milestones": self._create_milestones(total_days),
            "buffer_time": max(1, int(total_days * 0.1))
        }

    def _create_milestones(self, total_days: int) -> List[Dict[str, Any]]:
        """Create project milestones"""
        return [
            {"day": max(1, int(total_days * 0.2)), "milestone": "Research_complete", "deliverable": "Market_analysis_and_role_requirements"},
            {"day": max(3, int(total_days * 0.5)), "milestone": "First_draft_complete", "deliverable": "Complete_resume_draft"},
            {"day": max(5, int(total_days * 0.8)), "milestone": "Refinement_complete", "deliverable": "Polished_resume_with_optimizations"},
            {"day": total_days, "milestone": "Final_delivery", "deliverable": "Production_ready_resume"}
        ]

    def _determine_optimization_focus(self, resume_input: ResumeInput, input_analysis: Dict[str, Any]) -> List[str]:
        """Determine optimization focus areas"""
        base_focus = ["impact", "keywords", "readability"]

        # Add focus based on gaps
        if "more_technical_skills" in input_analysis["content_gaps"]:
            base_focus.append("skills_optimization")

        if "diversify_experience" in input_analysis["improvement_opportunities"]:
            base_focus.append("experience_highlighting")

        # Add focus based on target role
        if "executive" in resume_input.target_role.lower():
            base_focus.extend(["strategic_impact", "leadership_demonstration"])

        if "engineer" in resume_input.target_role.lower():
            base_focus.extend(["technical_depth", "innovation_showcase"])

        return list(set(base_focus))  # Remove duplicates

    def _create_keyword_strategy(self, resume_input: ResumeInput, role_template: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive keyword strategy"""
        return {
            "primary_keywords": self._extract_primary_keywords(resume_input),
            "secondary_keywords": self._extract_secondary_keywords(resume_input),
            "keyword_categories": role_template["keyword_categories"],
            "density_targets": {
                "primary": 0.015,  # 1.5% of total text
                "secondary": 0.025,  # 2.5% of total text
                "total": 0.04       # 4% total keyword density
            },
            "placement_strategy": {
                "summary": "high_priority_primary",
                "experience": "contextual_integration",
                "skills": "comprehensive_coverage"
            },
            "competitive_keywords": self._identify_competitive_keywords(resume_input)
        }

    def _extract_primary_keywords(self, resume_input: ResumeInput) -> List[str]:
        """Extract primary keywords from input"""
        keywords = []

        # From target role
        role_keywords = resume_input.target_role.lower().replace(" ", "_").split("_")
        keywords.extend(role_keywords)

        # From skills
        if resume_input.skills:
            keywords.extend(resume_input.skills.get("technical", [])[:5])

        # From job description if available
        if resume_input.job_description:
            keywords.extend(self._extract_keywords_from_text(resume_input.job_description, 10))

        return list(set(keywords))

    def _extract_secondary_keywords(self, resume_input: ResumeInput) -> List[str]:
        """Extract secondary keywords from input"""
        keywords = []

        # Additional technical skills
        if resume_input.skills:
            keywords.extend(resume_input.skills.get("technical", [])[5:10])
            keywords.extend(resume_input.skills.get("tools", [])[:5])

        # Soft skills
        if resume_input.skills:
            keywords.extend(resume_input.skills.get("soft", [])[:5])

        return list(set(keywords))

    def _extract_keywords_from_text(self, text: str, limit: int = 10) -> List[str]:
        """Extract keywords from text using simple heuristics"""
        # Simple keyword extraction - in production would use NLP
        words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:limit]]

    def _identify_competitive_keywords(self, resume_input: ResumeInput) -> List[str]:
        """Identify keywords that provide competitive advantage"""
        competitive_keywords = []

        # High-value technical keywords
        high_value_tech = ["machine learning", "artificial intelligence", "cloud architecture",
                          "devops", "microservices", "kubernetes", "aws", "azure", "tensorflow", "pytorch"]

        # Leadership keywords for senior roles
        if resume_input.experience_level in ["senior", "executive"]:
            high_value_tech.extend(["strategic planning", "team leadership", "p&l management",
                                   "digital transformation", "stakeholder management"])

        # Check which keywords are present in skills
        if resume_input.skills:
            all_skills = " ".join(resume_input.skills.get("technical", []) +
                                resume_input.skills.get("soft", []) +
                                resume_input.skills.get("tools", []))

            for keyword in high_value_tech:
                if keyword.lower() in all_skills.lower():
                    competitive_keywords.append(keyword)

        return competitive_keywords

    def _create_formatting_specifications(self, resume_input: ResumeInput) -> Dict[str, Any]:
        """Create detailed formatting specifications"""
        return {
            "page_length": "one_page" if resume_input.experience_level in ["junior", "mid"] else "two_pages",
            "font_preferences": {
                "professional": ["Calibri", "Arial", "Georgia"],
                "modern": ["Helvetica", "Open Sans", "Lato"],
                "creative": ["Garamond", "Cambria", "Book Antiqua"]
            },
            "layout_style": "chronological",
            "margin_settings": {"top": "0.5", "bottom": "0.5", "left": "0.75", "right": "0.75"},
            "section_spacing": {"before": "6pt", "after": "6pt"},
            "bullet_style": "consistent_round",
            "header_hierarchy": {
                "name": "16pt_bold",
                "section_titles": "14pt_bold",
                "company_titles": "12pt_bold_italic",
                "body_text": "11pt_regular"
            }
        }

    def _determine_compliance_requirements(self, resume_input: ResumeInput) -> Dict[str, Any]:
        """Determine compliance requirements based on target platforms"""
        compliance = {
            "primary_platform": "linkedin",
            "ats_optimization": True,
            "platform_specific_rules": {}
        }

        # LinkedIn compliance
        compliance["platform_specific_rules"]["linkedin"] = self.compliance_rules["linkedin"]

        # ATS compliance
        compliance["platform_specific_rules"]["ats"] = self.compliance_rules["ats_friendly"]

        # Company-specific requirements if target company specified
        if resume_input.target_company:
            compliance["custom_requirements"] = self._get_company_requirements(resume_input.target_company)

        return compliance

    def _get_company_requirements(self, company: str) -> Dict[str, Any]:
        """Get company-specific resume requirements"""
        # Simulated company requirements database
        company_requirements = {
            "google": {
                "emphasis": "technical_innovation",
                "preferred_format": "pdf",
                "additional_sections": ["projects", "publications"]
            },
            "microsoft": {
                "emphasis": "collaboration_impact",
                "preferred_format": "word",
                "specific_keywords": ["cloud", "azure", "enterprise"]
            },
            "amazon": {
                "emphasis": "customer_impact",
                "preferred_format": "pdf",
                "leadership_principles": True
            }
        }

        return company_requirements.get(company.lower(), {})

    def _calculate_planning_confidence(self, resume_input: ResumeInput, input_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for the planning"""
        base_confidence = 0.7

        # Increase confidence based on input completeness
        if resume_input.personal_info and resume_input.professional_experience and resume_input.skills:
            base_confidence += 0.1

        # Adjust based on competitive positioning
        competitive_score = input_analysis["competitive_positioning"]["competitive_score"]
        base_confidence += (competitive_score - 50) * 0.006  # Scale 0-50 to 0-0.3

        return min(max(base_confidence, 0.0), 1.0)

    def _estimate_completion_date(self, resume_input: ResumeInput) -> str:
        """Estimate completion date for the resume"""
        timeline = self._create_timeline(resume_input, self._analyze_resume_input(resume_input))
        completion_date = datetime.now() + timedelta(days=timeline["total_days"])
        return completion_date.isoformat()

    def _set_quality_targets(self, resume_input: ResumeInput) -> Dict[str, Any]:
        """Set quality targets for the resume"""
        return {
            "ats_compatibility_score": 0.85,
            "readability_score": 70,
            "keyword_density": 0.04,
            "impact_score": 0.8,
            "compliance_score": 0.95
        }

    def _create_input_summary(self, resume_input: ResumeInput) -> Dict[str, Any]:
        """Create summary of input for planning history"""
        return {
            "target_role": resume_input.target_role,
            "experience_level": resume_input.experience_level,
            "experience_count": len(resume_input.professional_experience or []),
            "technical_skills_count": len(resume_input.skills.get("technical", []) if resume_input.skills else []),
            "has_education": len(resume_input.education or []) > 0,
            "target_company": resume_input.target_company
        }

    def _document_planning_decisions(self, plan: ResumePlan, input_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Document key planning decisions for audit trail"""
        return {
            "section_selection_rationale": f"Selected {len(plan.sections)} sections based on experience level and role requirements",
            "content_strategy_rationale": f"Emphasis on {plan.content_strategy.get('focus', 'impact')} based on market analysis",
            "timeline_rationale": f"{plan.timeline['total_days']} days timeline based on complexity score {input_analysis['complexity_score']}",
            "optimization_focus_rationale": f"Focus areas: {', '.join(plan.optimization_focus)} based on input analysis"
        }

    def update_plan(self, plan: ResumePlan, updates: Dict[str, Any]) -> ResumePlan:
        """Update existing plan with change tracking"""
        original_sections = plan.sections.copy()
        original_strategy = plan.content_strategy.copy()

        # Apply updates
        if "sections" in updates:
            plan.sections = updates["sections"]
        if "content_strategy" in updates:
            plan.content_strategy.update(updates["content_strategy"])
        if "optimization_focus" in updates:
            plan.optimization_focus = updates["optimization_focus"]
        if "timeline" in updates:
            plan.timeline.update(updates["timeline"])

        # Track changes
        plan.metadata["updated"] = True
        plan.metadata["last_updated"] = datetime.now().isoformat()
        plan.metadata["change_history"] = plan.metadata.get("change_history", [])
        plan.metadata["change_history"].append({
            "timestamp": datetime.now().isoformat(),
            "changes": {
                "sections_added": list(set(plan.sections) - set(original_sections)),
                "sections_removed": list(set(original_sections) - set(plan.sections)),
                "strategy_changes": self._identify_strategy_changes(original_strategy, plan.content_strategy)
            }
        })

        return plan

    def _identify_strategy_changes(self, original: Dict[str, Any], updated: Dict[str, Any]) -> List[str]:
        """Identify changes in content strategy"""
        changes = []
        for key, value in updated.items():
            if key not in original or original[key] != value:
                changes.append(f"{key}_updated")
        return changes

    def estimate_completion_time(self, plan: ResumePlan) -> Dict[str, Any]:
        """Estimate plan completion time with detailed breakdown"""
        base_time = plan.timeline.get("total_days", 7)

        # Calculate complexity factors
        section_complexity = len(plan.sections) * 1.5
        optimization_complexity = len(plan.optimization_focus) * 0.5

        total_complexity = base_time + section_complexity + optimization_complexity

        return {
            "estimated_days": int(total_complexity),
            "complexity": "low" if total_complexity <= 5 else "medium" if total_complexity <= 10 else "high",
            "confidence": plan.metadata.get("planning_confidence", 0.8),
            "breakdown": plan.timeline.get("phases", {}),
            "risk_factors": self._identify_risk_factors(plan),
            "success_probability": self._calculate_success_probability(plan)
        }

    def _identify_risk_factors(self, plan: ResumePlan) -> List[str]:
        """Identify potential risk factors for plan completion"""
        risks = []

        if plan.timeline.get("total_days", 0) > 14:
            risks.append("extended_timeline_risk")

        if len(plan.optimization_focus) > 5:
            risks.append("scope_creep_risk")

        if plan.content_strategy.get("company_research") == "required" and not plan.target_company:
            risks.append("insufficient_input_risk")

        return risks

    def _calculate_success_probability(self, plan: ResumePlan) -> float:
        """Calculate probability of successful plan completion"""
        base_probability = 0.8

        # Adjust based on planning confidence
        planning_confidence = plan.metadata.get("planning_confidence", 0.7)
        base_probability += (planning_confidence - 0.7) * 0.5

        # Adjust based on complexity
        if plan.timeline.get("total_days", 0) > 10:
            base_probability -= 0.1

        # Adjust based on risk factors
        risk_count = len(self._identify_risk_factors(plan))
        base_probability -= risk_count * 0.05

        return min(max(base_probability, 0.0), 1.0)

    def get_planning_history(self, plan_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get planning history for specific plan or all plans"""
        if plan_id:
            return [entry for entry in self.planning_history if entry["plan_id"] == plan_id]
        return self.planning_history

    def validate_plan(self, plan: ResumePlan) -> Dict[str, Any]:
        """Validate plan completeness and consistency"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }

        # Check required fields
        if not plan.plan_id:
            validation_result["errors"].append("Missing plan ID")
            validation_result["is_valid"] = False

        if not plan.target_role:
            validation_result["errors"].append("Missing target role")
            validation_result["is_valid"] = False

        # Check sections
        if len(plan.sections) < 3:
            validation_result["warnings"].append("Plan has fewer than 3 sections")

        # Check timeline
        if plan.timeline.get("total_days", 0) < 3:
            validation_result["warnings"].append("Timeline seems too short for quality work")

        # Recommendations
        if not plan.target_company and plan.content_strategy.get("company_research") == "required":
            validation_result["recommendations"].append("Consider specifying target company for better customization")

        if len(plan.optimization_focus) < 3:
            validation_result["recommendations"].append("Consider adding more optimization focus areas")

        return validation_result
