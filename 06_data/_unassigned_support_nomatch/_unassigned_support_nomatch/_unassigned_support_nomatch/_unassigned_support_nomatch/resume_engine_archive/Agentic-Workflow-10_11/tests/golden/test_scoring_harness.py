"""
Scoring Harness for Quality Evaluation

Deterministic quantitative metrics for resume analysis, job matching, and skill extraction.
Focuses on structural completeness, content coverage, and format validation without LLM dependencies.
"""

import pytest
import re
from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import time

# Mark all tests as golden evaluation tests
pytestmark = [pytest.mark.golden, pytest.mark.integration]


class ScoreLevel(Enum):
    """Quality score levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass(frozen=True)
class QualityScore:
    """Individual quality score component."""
    metric_name: str
    score: float  # 0.0 to 1.0
    weight: float
    level: ScoreLevel
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScoringResult:
    """Complete scoring result for evaluation."""
    domain: str
    overall_score: float  # 0.0 to 1.0
    overall_level: ScoreLevel
    component_scores: List[QualityScore]
    evaluation_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResumeAnalysisScorer:
    """Scoring harness for resume analysis quality."""
    
    def __init__(self):
        self.scoring_weights = {
            "structural_completeness": 0.25,
            "skill_coverage": 0.30,
            "experience_detail": 0.25,
            "format_consistency": 0.20
        }
        self.required_sections = [
            "contact_info", "summary", "experience", "education", "skills"
        ]
        self.skill_categories = [
            "technical", "soft", "leadership", "communication", "analytical"
        ]
    
    def score_resume_analysis(self, resume_data: Dict[str, Any], 
                             expected_skills: List[str]) -> ScoringResult:
        """Score resume analysis quality."""
        start_time = time.time()
        component_scores = []
        
        # 1. Structural Completeness
        structural_score = self._score_structural_completeness(resume_data)
        component_scores.append(structural_score)
        
        # 2. Skill Coverage
        skill_score = self._score_skill_coverage(resume_data, expected_skills)
        component_scores.append(skill_score)
        
        # 3. Experience Detail
        experience_score = self._score_experience_detail(resume_data)
        component_scores.append(experience_score)
        
        # 4. Format Consistency
        format_score = self._score_format_consistency(resume_data)
        component_scores.append(format_score)
        
        # Calculate overall score
        overall_score = sum(
            score.score * score.weight for score in component_scores
        )
        overall_level = self._determine_score_level(overall_score)
        
        evaluation_time = time.time() - start_time
        
        return ScoringResult(
            domain="resume_analysis",
            overall_score=overall_score,
            overall_level=overall_level,
            component_scores=component_scores,
            evaluation_time=evaluation_time,
            metadata={
                "total_sections": len(resume_data.get("sections", {})),
                "expected_skills_count": len(expected_skills),
                "scoring_weights": self.scoring_weights
            }
        )
    
    def _score_structural_completeness(self, resume_data: Dict[str, Any]) -> QualityScore:
        """Score structural completeness of resume."""
        sections = resume_data.get("sections", {})
        present_sections = set(sections.keys())
        required_set = set(self.required_sections)
        
        missing_sections = required_set - present_sections
        present_count = len(present_sections & required_set)
        total_required = len(required_set)
        
        completeness_score = present_count / total_required if total_required > 0 else 0.0
        
        # Additional scoring for optional sections
        optional_sections = {"projects", "certifications", "awards", "publications"}
        optional_present = len(present_sections & optional_sections)
        optional_bonus = min(optional_present * 0.05, 0.15)  # Max 15% bonus
        
        final_score = min(completeness_score + optional_bonus, 1.0)
        level = self._determine_score_level(final_score)
        
        return QualityScore(
            metric_name="structural_completeness",
            score=final_score,
            weight=self.scoring_weights["structural_completeness"],
            level=level,
            details={
                "present_sections": list(present_sections),
                "missing_sections": list(missing_sections),
                "optional_present": optional_present,
                "completeness_ratio": completeness_score
            }
        )
    
    def _score_skill_coverage(self, resume_data: Dict[str, Any], 
                             expected_skills: List[str]) -> QualityScore:
        """Score skill coverage against expected skills."""
        skills_section = resume_data.get("sections", {}).get("skills", {})
        extracted_skills = skills_section.get("technical_skills", [])
        
        if isinstance(extracted_skills, str):
            extracted_skills = [extracted_skills]
        
        # Normalize skills for comparison
        extracted_normalized = {skill.lower().strip() for skill in extracted_skills}
        expected_normalized = {skill.lower().strip() for skill in expected_skills}
        
        matched_skills = extracted_normalized & expected_normalized
        coverage_ratio = len(matched_skills) / len(expected_normalized) if expected_normalized else 1.0
        
        # Bonus for category diversity
        categories_present = set()
        for category in self.skill_categories:
            category_skills = skills_section.get(f"{category}_skills", [])
            if category_skills:
                categories_present.add(category)
        
        category_bonus = len(categories_present) / len(self.skill_categories) * 0.1
        final_score = min(coverage_ratio + category_bonus, 1.0)
        
        level = self._determine_score_level(final_score)
        
        return QualityScore(
            metric_name="skill_coverage",
            score=final_score,
            weight=self.scoring_weights["skill_coverage"],
            level=level,
            details={
                "extracted_skills_count": len(extracted_skills),
                "expected_skills_count": len(expected_skills),
                "matched_skills": list(matched_skills),
                "coverage_ratio": coverage_ratio,
                "categories_present": list(categories_present)
            }
        )
    
    def _score_experience_detail(self, resume_data: Dict[str, Any]) -> QualityScore:
        """Score detail level in experience section."""
        experience_section = resume_data.get("sections", {}).get("experience", [])
        
        if not experience_section:
            return QualityScore(
                metric_name="experience_detail",
                score=0.0,
                weight=self.scoring_weights["experience_detail"],
                level=ScoreLevel.CRITICAL,
                details={"error": "No experience section found"}
            )
        
        detail_scores = []
        for exp in experience_section:
            score = 0.0
            
            # Check for required fields
            if exp.get("title") and exp.get("company") and exp.get("duration"):
                score += 0.4
            
            # Check for detailed descriptions
            description = exp.get("description", "")
            if len(description) > 50:  # Substantial description
                score += 0.3
            
            # Check for achievements/impact
            achievements = exp.get("achievements", [])
            if achievements and len(achievements) > 0:
                score += 0.3
            
            detail_scores.append(score)
        
        avg_detail_score = sum(detail_scores) / len(detail_scores) if detail_scores else 0.0
        level = self._determine_score_level(avg_detail_score)
        
        return QualityScore(
            metric_name="experience_detail",
            score=avg_detail_score,
            weight=self.scoring_weights["experience_detail"],
            level=level,
            details={
                "experience_entries": len(experience_section),
                "average_detail_score": avg_detail_score,
                "detail_scores": detail_scores
            }
        )
    
    def _score_format_consistency(self, resume_data: Dict[str, Any]) -> QualityScore:
        """Score format consistency across resume."""
        sections = resume_data.get("sections", {})
        # Check date format consistency
        date_patterns = []
        for section_name, section_data in sections.items():
            if isinstance(section_data, list):
                for item in section_data:
                    if "duration" in item:
                        duration = str(item["duration"])
                        if re.match(r'\d{4}-\d{4}', duration):
                            date_patterns.append("YYYY-YYYY")
                        elif re.match(r'\d{1,2}/\d{4} - \d{1,2}/\d{4}', duration):
                            date_patterns.append("MM/YYYY - MM/YYYY")
                        else:
                            date_patterns.append("other")
        
        date_consistency = len(set(date_patterns)) <= 1 if date_patterns else 1.0
        
        # Check section ordering
        section_order = list(sections.keys())
        
        order_score = 0.0
        if len(section_order) >= 3:
            # Check if key sections are in reasonable order
            if "experience" in section_order and "education" in section_order:
                exp_index = section_order.index("experience")
                edu_index = section_order.index("education")
                if exp_index < edu_index:  # Experience should come before education
                    order_score = 1.0
                else:
                    order_score = 0.5
            else:
                order_score = 0.8  # Partial credit if sections exist
        
        # Check for consistent formatting
        format_score = (date_consistency + order_score) / 2.0
        level = self._determine_score_level(format_score)
        
        return QualityScore(
            metric_name="format_consistency",
            score=format_score,
            weight=self.scoring_weights["format_consistency"],
            level=level,
            details={
                "date_patterns": date_patterns,
                "date_consistency": date_consistency,
                "order_score": order_score,
                "section_order": section_order
            }
        )
    
    def _determine_score_level(self, score: float) -> ScoreLevel:
        """Determine score level from numeric score."""
        if score >= 0.9:
            return ScoreLevel.EXCELLENT
        elif score >= 0.75:
            return ScoreLevel.GOOD
        elif score >= 0.6:
            return ScoreLevel.ACCEPTABLE
        elif score >= 0.4:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.CRITICAL


class JobMatchingScorer:
    """Scoring harness for job matching quality."""
    
    def __init__(self):
        self.scoring_weights = {
            "requirement_coverage": 0.35,
            "skill_alignment": 0.30,
            "experience_match": 0.25,
            "qualification_assessment": 0.10
        }
    
    def score_job_matching(self, resume_data: Dict[str, Any], 
                          job_data: Dict[str, Any]) -> ScoringResult:
        """Score job matching quality."""
        start_time = time.time()
        component_scores = []
        
        # 1. Requirement Coverage
        requirement_score = self._score_requirement_coverage(resume_data, job_data)
        component_scores.append(requirement_score)
        
        # 2. Skill Alignment
        alignment_score = self._score_skill_alignment(resume_data, job_data)
        component_scores.append(alignment_score)
        
        # 3. Experience Match
        experience_score = self._score_experience_match(resume_data, job_data)
        component_scores.append(experience_score)
        
        # 4. Qualification Assessment
        qualification_score = self._score_qualification_assessment(resume_data, job_data)
        component_scores.append(qualification_score)
        
        # Calculate overall score
        overall_score = sum(
            score.score * score.weight for score in component_scores
        )
        overall_level = self._determine_score_level(overall_score)
        
        evaluation_time = time.time() - start_time
        
        return ScoringResult(
            domain="job_matching",
            overall_score=overall_score,
            overall_level=overall_level,
            component_scores=component_scores,
            evaluation_time=evaluation_time,
            metadata={
                "job_title": job_data.get("title", "Unknown"),
                "resume_sections": len(resume_data.get("sections", {})),
                "scoring_weights": self.scoring_weights
            }
        )
    
    def _score_requirement_coverage(self, resume_data: Dict[str, Any], 
                                   job_data: Dict[str, Any]) -> QualityScore:
        """Score coverage of job requirements."""
        job_requirements = job_data.get("requirements", [])
        resume_skills = resume_data.get("sections", {}).get("skills", {}).get("technical_skills", [])
        
        if isinstance(resume_skills, str):
            resume_skills = [resume_skills]
        
        # Normalize for comparison
        resume_skill_set = {skill.lower().strip() for skill in resume_skills}
        requirement_set = {req.lower().strip() for req in job_requirements}
        
        # Direct matches
        direct_matches = resume_skill_set & requirement_set
        
        # Partial matches (contains)
        partial_matches = set()
        for req in requirement_set:
            for skill in resume_skill_set:
                if req in skill or skill in req:
                    partial_matches.add(req)
        
        total_matches = len(direct_matches) + len(partial_matches - direct_matches)
        coverage_ratio = total_matches / len(requirement_set) if requirement_set else 1.0
        
        level = self._determine_score_level(coverage_ratio)
        
        return QualityScore(
            metric_name="requirement_coverage",
            score=coverage_ratio,
            weight=self.scoring_weights["requirement_coverage"],
            level=level,
            details={
                "job_requirements_count": len(job_requirements),
                "resume_skills_count": len(resume_skills),
                "direct_matches": list(direct_matches),
                "partial_matches": list(partial_matches - direct_matches),
                "coverage_ratio": coverage_ratio
            }
        )
    
    def _score_skill_alignment(self, resume_data: Dict[str, Any], 
                              job_data: Dict[str, Any]) -> QualityScore:
        """Score skill alignment with job requirements."""
        required_skills = job_data.get("required_skills", [])
        preferred_skills = job_data.get("preferred_skills", [])
        
        resume_section = resume_data.get("sections", {}).get("skills", {})
        resume_skills = resume_section.get("technical_skills", [])
        
        if isinstance(resume_skills, str):
            resume_skills = [resume_skills]
        
        resume_skill_set = {skill.lower().strip() for skill in resume_skills}
        required_set = {skill.lower().strip() for skill in required_skills}
        preferred_set = {skill.lower().strip() for skill in preferred_skills}
        
        # Score required skills (higher weight)
        required_matches = len(resume_skill_set & required_set)
        required_score = required_matches / len(required_set) if required_set else 1.0
        
        # Score preferred skills (lower weight)
        preferred_matches = len(resume_skill_set & preferred_set)
        preferred_score = preferred_matches / len(preferred_set) if preferred_set else 1.0
        
        # Weighted combination
        alignment_score = (required_score * 0.7) + (preferred_score * 0.3)
        level = self._determine_score_level(alignment_score)
        
        return QualityScore(
            metric_name="skill_alignment",
            score=alignment_score,
            weight=self.scoring_weights["skill_alignment"],
            level=level,
            details={
                "required_matches": required_matches,
                "preferred_matches": preferred_matches,
                "required_score": required_score,
                "preferred_score": preferred_score,
                "alignment_score": alignment_score
            }
        )
    
    def _score_experience_match(self, resume_data: Dict[str, Any], 
                               job_data: Dict[str, Any]) -> QualityScore:
        """Score experience level matching."""
        job_requirements = job_data.get("experience_requirements", {})
        required_years = job_requirements.get("minimum_years", 0)
        required_level = job_requirements.get("level", "entry").lower()
        
        resume_experience = resume_data.get("sections", {}).get("experience", [])
        
        # Calculate total years of experience
        total_years = 0.0
        relevant_experience = 0.0
        
        for exp in resume_experience:
            duration_str = exp.get("duration", "")
            # Extract years from duration string
            years_match = re.search(r'(\d+(?:\.\d+)?)\s*years?', duration_str.lower())
            if years_match:
                years = float(years_match.group(1))
                total_years += years
                
                # Check if experience is relevant
                title = exp.get("title", "").lower()
                if any(keyword in title for keyword in ["software", "developer", "engineer", "analyst"]):
                    relevant_experience += years
        
        # Score based on years requirement
        years_score = min(total_years / max(required_years, 1), 1.0)
        
        # Score based on level requirement
        level_score = 0.0
        if required_level == "entry":
            level_score = 1.0 if total_years >= 0 else 0.5
        elif required_level == "mid":
            level_score = 1.0 if total_years >= 3 else 0.7 if total_years >= 2 else 0.3
        elif required_level == "senior":
            level_score = 1.0 if total_years >= 5 else 0.7 if total_years >= 3 else 0.3
        elif required_level == "lead":
            level_score = 1.0 if total_years >= 7 else 0.6 if total_years >= 5 else 0.2
        
        experience_score = (years_score * 0.6) + (level_score * 0.4)
        level = self._determine_score_level(experience_score)
        
        return QualityScore(
            metric_name="experience_match",
            score=experience_score,
            weight=self.scoring_weights["experience_match"],
            level=level,
            details={
                "total_years": total_years,
                "relevant_years": relevant_experience,
                "required_years": required_years,
                "required_level": required_level,
                "years_score": years_score,
                "level_score": level_score
            }
        )
    
    def _score_qualification_assessment(self, resume_data: Dict[str, Any], 
                                       job_data: Dict[str, Any]) -> QualityScore:
        """Score overall qualification assessment."""
        education_requirements = job_data.get("education_requirements", {})
        required_degree = education_requirements.get("degree", "").lower()
        required_field = education_requirements.get("field", "").lower()
        
        education_section = resume_data.get("sections", {}).get("education", [])
        
        degree_score = 0.0
        field_score = 0.0
        
        for edu in education_section:
            degree = edu.get("degree", "").lower()
            field = edu.get("field", "").lower()
            
            # Check degree match
            if required_degree:
                if required_degree in degree or degree in required_degree:
                    degree_score = 1.0
                elif "bachelor" in degree and "bachelor" in required_degree:
                    degree_score = 0.8
                elif "master" in degree and "master" in required_degree:
                    degree_score = 0.8
            
            # Check field match
            if required_field:
                if required_field in field or field in required_field:
                    field_score = 1.0
                elif any(keyword in field for keyword in required_field.split()):
                    field_score = 0.7
        
        qualification_score = (degree_score * 0.6) + (field_score * 0.4)
        level = self._determine_score_level(qualification_score)
        
        return QualityScore(
            metric_name="qualification_assessment",
            score=qualification_score,
            weight=self.scoring_weights["qualification_assessment"],
            level=level,
            details={
                "required_degree": required_degree,
                "required_field": required_field,
                "degree_score": degree_score,
                "field_score": field_score,
                "education_entries": len(education_section)
            }
        )
    
    def _determine_score_level(self, score: float) -> ScoreLevel:
        """Determine score level from numeric score."""
        if score >= 0.9:
            return ScoreLevel.EXCELLENT
        elif score >= 0.75:
            return ScoreLevel.GOOD
        elif score >= 0.6:
            return ScoreLevel.ACCEPTABLE
        elif score >= 0.4:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.CRITICAL


class SkillExtractionScorer:
    """Scoring harness for skill extraction quality."""
    
    def __init__(self):
        self.scoring_weights = {
            "extraction_completeness": 0.35,
            "categorization_accuracy": 0.30,
            "relevance_precision": 0.25,
            "format_standardization": 0.10
        }
        self.skill_categories = {
            "technical": ["python", "java", "javascript", "react", "node", "angular", "vue", "sql", "nosql", "mongodb", "postgresql", "mysql", "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "ci/cd", "api", "rest", "graphql", "microservices", "programming", "software", "database", "framework", "tool"],
            "soft": ["communication", "leadership", "teamwork", "problem-solving", "analytical", "collaboration", "mentoring", "project management", "time management", "critical thinking", "adaptability", "creativity", "interpersonal", "presentation"],
            "domain": ["finance", "healthcare", "education", "retail", "manufacturing", "ecommerce", "banking", "insurance", "telecommunications", "government", "consulting", "startup", "enterprise"]
        }
    
    def score_skill_extraction(self, source_text: str, 
                              extracted_skills: Dict[str, List[str]]) -> ScoringResult:
        """Score skill extraction quality."""
        start_time = time.time()
        component_scores = []
        
        # 1. Extraction Completeness
        completeness_score = self._score_extraction_completeness(source_text, extracted_skills)
        component_scores.append(completeness_score)
        
        # 2. Categorization Accuracy
        categorization_score = self._score_categorization_accuracy(extracted_skills)
        component_scores.append(categorization_score)
        
        # 3. Relevance Precision
        relevance_score = self._score_relevance_precision(source_text, extracted_skills)
        component_scores.append(relevance_score)
        
        # 4. Format Standardization
        format_score = self._score_format_standardization(extracted_skills)
        component_scores.append(format_score)
        
        # Calculate overall score
        overall_score = sum(
            score.score * score.weight for score in component_scores
        )
        overall_level = self._determine_score_level(overall_score)
        
        evaluation_time = time.time() - start_time
        
        return ScoringResult(
            domain="skill_extraction",
            overall_score=overall_score,
            overall_level=overall_level,
            component_scores=component_scores,
            evaluation_time=evaluation_time,
            metadata={
                "source_text_length": len(source_text),
                "total_extracted_skills": sum(len(skills) for skills in extracted_skills.values()),
                "categories_found": list(extracted_skills.keys())
            }
        )
    
    def _score_extraction_completeness(self, source_text: str, 
                                      extracted_skills: Dict[str, List[str]]) -> QualityScore:
        """Score completeness of skill extraction."""
        # Count expected skill indicators in source text
        skill_indicators = [
            "python", "java", "javascript", "sql", "react", "node.js", "aws", "docker",
            "leadership", "communication", "project management", "analytical", "problem-solving"
        ]
        
        found_indicators = set()
        for indicator in skill_indicators:
            if indicator.lower() in source_text.lower():
                found_indicators.add(indicator)
        
        # Count extracted skills
        all_extracted = []
        for category, skills in extracted_skills.items():
            if isinstance(skills, list):
                all_extracted.extend(skills)
            elif isinstance(skills, str):
                all_extracted.append(skills)
        
        extracted_set = {skill.lower().strip() for skill in all_extracted}
        
        # Calculate completeness
        matched_indicators = found_indicators & extracted_set
        completeness_ratio = len(matched_indicators) / len(found_indicators) if found_indicators else 1.0
        
        # Bonus for extracting additional relevant skills
        additional_skills = len(extracted_set) - len(matched_indicators)
        additional_bonus = min(additional_skills * 0.02, 0.1)  # Max 10% bonus
        
        final_score = min(completeness_ratio + additional_bonus, 1.0)
        level = self._determine_score_level(final_score)
        
        return QualityScore(
            metric_name="extraction_completeness",
            score=final_score,
            weight=self.scoring_weights["extraction_completeness"],
            level=level,
            details={
                "indicators_in_text": len(found_indicators),
                "skills_extracted": len(extracted_set),
                "matched_indicators": len(matched_indicators),
                "completeness_ratio": completeness_ratio,
                "additional_bonus": additional_bonus
            }
        )
    
    def _score_categorization_accuracy(self, extracted_skills: Dict[str, List[str]]) -> QualityScore:
        """Score accuracy of skill categorization."""
        total_skills = 0
        correctly_categorized = 0
        
        for category, skills in extracted_skills.items():
            if isinstance(skills, list):
                total_skills += len(skills)
                for skill in skills:
                    if self._is_correct_category(skill.lower(), category):
                        correctly_categorized += 1
            elif isinstance(skills, str):
                total_skills += 1
                if self._is_correct_category(skills.lower(), category):
                    correctly_categorized += 1
        
        categorization_ratio = correctly_categorized / total_skills if total_skills > 0 else 1.0
        
        # Bonus for having multiple categories
        category_diversity = len([cat for cat, skills in extracted_skills.items() if skills])
        diversity_bonus = min(category_diversity * 0.05, 0.15)  # Max 15% bonus
        
        final_score = min(categorization_ratio + diversity_bonus, 1.0)
        level = self._determine_score_level(final_score)
        
        return QualityScore(
            metric_name="categorization_accuracy",
            score=final_score,
            weight=self.scoring_weights["categorization_accuracy"],
            level=level,
            details={
                "total_skills": total_skills,
                "correctly_categorized": correctly_categorized,
                "categorization_ratio": categorization_ratio,
                "category_diversity": category_diversity,
                "diversity_bonus": diversity_bonus
            }
        )
    
    def _score_relevance_precision(self, source_text: str, 
                                  extracted_skills: Dict[str, List[str]]) -> QualityScore:
        """Score relevance precision of extracted skills."""
        # Define irrelevant indicators
        irrelevant_patterns = [
            r'\b(excellent|good|great|strong|solid)\s+(skill|experience|background)\b',
            r'\b(team\s+player|hard\s+worker|fast\s+learner)\b',
            r'\b(ability|capability|capacity)\s+to\b'
        ]
        
        total_extracted = 0
        relevant_skills = 0
        
        for category, skills in extracted_skills.items():
            if isinstance(skills, list):
                for skill in skills:
                    total_extracted += 1
                    if not self._is_irrelevant_skill(skill, irrelevant_patterns):
                        relevant_skills += 1
            elif isinstance(skills, str):
                total_extracted += 1
                if not self._is_irrelevant_skill(skills, irrelevant_patterns):
                    relevant_skills += 1
        
        precision_ratio = relevant_skills / total_extracted if total_extracted > 0 else 1.0
        level = self._determine_score_level(precision_ratio)
        
        return QualityScore(
            metric_name="relevance_precision",
            score=precision_ratio,
            weight=self.scoring_weights["relevance_precision"],
            level=level,
            details={
                "total_extracted": total_extracted,
                "relevant_skills": relevant_skills,
                "precision_ratio": precision_ratio
            }
        )
    
    def _score_format_standardization(self, extracted_skills: Dict[str, List[str]]) -> QualityScore:
        """Score format standardization of extracted skills."""
        format_issues = []
        total_skills = 0
        
        for category, skills in extracted_skills.items():
            if isinstance(skills, list):
                for skill in skills:
                    total_skills += 1
                    # Check for common format issues
                    if skill != skill.strip():
                        format_issues.append("leading/trailing_whitespace")
                    if skill != skill.lower() and skill != skill.title():
                        format_issues.append("inconsistent_case")
                    if len(skill) < 3:
                        format_issues.append("too_short")
                    if skill.count(' ') > 5:  # Too many words
                        format_issues.append("too_long")
            elif isinstance(skills, str):
                total_skills += 1
                if skills != skills.strip():
                    format_issues.append("leading/trailing_whitespace")
        
        # Calculate format score
        unique_issues = set(format_issues)
        format_penalty = len(unique_issues) * 0.1  # 10% penalty per issue type
        format_score = max(0.0, 1.0 - format_penalty)
        
        level = self._determine_score_level(format_score)
        
        return QualityScore(
            metric_name="format_standardization",
            score=format_score,
            weight=self.scoring_weights["format_standardization"],
            level=level,
            details={
                "total_skills": total_skills,
                "format_issues": list(unique_issues),
                "format_penalty": format_penalty,
                "format_score": format_score
            }
        )
    
    def _is_correct_category(self, skill: str, category: str) -> bool:
        """Check if skill is correctly categorized."""
        category_keywords = self.skill_categories.get(category, [])
        return any(keyword in skill for keyword in category_keywords)
    
    def _is_irrelevant_skill(self, skill: str, irrelevant_patterns: List[str]) -> bool:
        """Check if skill matches irrelevant patterns."""
        skill_lower = skill.lower()
        return any(re.search(pattern, skill_lower) for pattern in irrelevant_patterns)
    
    def _determine_score_level(self, score: float) -> ScoreLevel:
        """Determine score level from numeric score."""
        if score >= 0.9:
            return ScoreLevel.EXCELLENT
        elif score >= 0.75:
            return ScoreLevel.GOOD
        elif score >= 0.6:
            return ScoreLevel.ACCEPTABLE
        elif score >= 0.4:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.CRITICAL


class TestScoringHarness:
    """Test the scoring harness functionality."""
    
    def test_resume_analysis_scoring(self):
        """Test resume analysis scoring functionality."""
        scorer = ResumeAnalysisScorer()
        
        # Test resume data
        resume_data = {
            "sections": {
                "contact_info": {"email": "test@example.com", "phone": "555-1234"},
                "summary": "Experienced software developer with 5 years of expertise",
                "experience": [
                    {
                        "title": "Senior Software Engineer",
                        "company": "Tech Corp",
                        "duration": "2019-2024",
                        "description": "Developed and maintained web applications using modern frameworks. Led a team of 3 developers and implemented CI/CD pipelines.",
                        "achievements": ["Increased performance by 40%", "Reduced bugs by 60%"]
                    }
                ],
                "education": [
                    {
                        "degree": "Bachelor of Science",
                        "field": "Computer Science",
                        "duration": "2015-2019"
                    }
                ],
                "skills": {
                    "technical_skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
                    "soft_skills": ["Leadership", "Communication", "Problem-solving"],
                    "leadership_skills": ["Team management", "Project coordination"]
                },
                "projects": ["E-commerce platform", "API development"]
            }
        }
        
        expected_skills = ["Python", "JavaScript", "React", "Node.js", "SQL", "AWS", "Docker"]
        
        # Score resume analysis
        result = scorer.score_resume_analysis(resume_data, expected_skills)
        
        # Validate result structure
        assert result.domain == "resume_analysis"
        assert 0.0 <= result.overall_score <= 1.0
        assert isinstance(result.overall_level, ScoreLevel)
        assert len(result.component_scores) == 4
        assert result.evaluation_time >= 0.0  # Allow ultra-fast execution
        
        # Validate component scores
        component_names = [score.metric_name for score in result.component_scores]
        expected_components = ["structural_completeness", "skill_coverage", "experience_detail", "format_consistency"]
        assert set(component_names) == set(expected_components)
        
        # Validate scoring logic
        structural_score = next(s for s in result.component_scores if s.metric_name == "structural_completeness")
        assert structural_score.score > 0.8  # Should have most required sections plus optional
        
        skill_score = next(s for s in result.component_scores if s.metric_name == "skill_coverage")
        assert skill_score.score > 0.5  # Should match several expected skills
    
    def test_job_matching_scoring(self):
        """Test job matching scoring functionality."""
        scorer = JobMatchingScorer()
        
        # Test data
        resume_data = {
            "sections": {
                "skills": {
                    "technical_skills": ["Python", "JavaScript", "React", "AWS", "Docker"]
                },
                "experience": [
                    {
                        "title": "Software Engineer",
                        "company": "Tech Corp",
                        "duration": "4 years"
                    }
                ]
            }
        }
        
        job_data = {
            "title": "Senior Software Engineer",
            "requirements": ["Python", "React", "AWS"],
            "required_skills": ["Python", "JavaScript", "React"],
            "preferred_skills": ["AWS", "Docker", "Kubernetes"],
            "experience_requirements": {
                "minimum_years": 3,
                "level": "mid"
            },
            "education_requirements": {
                "degree": "Bachelor",
                "field": "Computer Science"
            }
        }
        
        # Score job matching
        result = scorer.score_job_matching(resume_data, job_data)
        
        # Validate result structure
        assert result.domain == "job_matching"
        assert 0.0 <= result.overall_score <= 1.0
        assert len(result.component_scores) == 4
        
        # Validate component scores
        component_names = [score.metric_name for score in result.component_scores]
        expected_components = ["requirement_coverage", "skill_alignment", "experience_match", "qualification_assessment"]
        assert set(component_names) == set(expected_components)
        
        # Validate scoring logic
        requirement_score = next(s for s in result.component_scores if s.metric_name == "requirement_coverage")
        assert requirement_score.score > 0.5  # Should match several requirements
        
        skill_score = next(s for s in result.component_scores if s.metric_name == "skill_alignment")
        assert skill_score.score > 0.6  # Should have good skill alignment
    
    def test_skill_extraction_scoring(self):
        """Test skill extraction scoring functionality."""
        scorer = SkillExtractionScorer()
        
        # Test data
        source_text = """
        Experienced software developer with expertise in Python, JavaScript, and React.
        Proficient in AWS cloud services and Docker containerization. Strong leadership 
        and communication skills with experience in project management and analytical thinking.
        """
        
        extracted_skills = {
            "technical": ["Python", "JavaScript", "React", "AWS", "Docker"],
            "soft": ["Leadership", "Communication", "Project management", "Analytical thinking"],
            "domain": ["Software development"]
        }
        
        # Score skill extraction
        result = scorer.score_skill_extraction(source_text, extracted_skills)
        
        # Validate result structure
        assert result.domain == "skill_extraction"
        assert 0.0 <= result.overall_score <= 1.0
        assert len(result.component_scores) == 4
        
        # Validate component scores
        component_names = [score.metric_name for score in result.component_scores]
        expected_components = ["extraction_completeness", "categorization_accuracy", "relevance_precision", "format_standardization"]
        assert set(component_names) == set(expected_components)
        
        # Validate scoring logic
        completeness_score = next(s for s in result.component_scores if s.metric_name == "extraction_completeness")
        assert completeness_score.score > 0.7  # Should extract most skills from text
        
        categorization_score = next(s for s in result.component_scores if s.metric_name == "categorization_accuracy")
        assert categorization_score.score > 0.8  # Should categorize skills correctly
    
    def test_scoring_harness_integration(self):
        """Test integration of all scoring harnesses."""
        resume_scorer = ResumeAnalysisScorer()
        job_scorer = JobMatchingScorer()
        skill_scorer = SkillExtractionScorer()
        
        # Comprehensive test data
        resume_data = {
            "sections": {
                "contact_info": {"email": "candidate@example.com"},
                "summary": "Senior software developer with full-stack experience",
                "experience": [
                    {
                        "title": "Senior Software Engineer",
                        "company": "Tech Company",
                        "duration": "2018-2023",
                        "description": "Led development of enterprise applications",
                        "achievements": ["Improved system performance", "Mentored junior developers"]
                    }
                ],
                "education": [{"degree": "BS Computer Science", "field": "Computer Science"}],
                "skills": {
                    "technical_skills": ["Python", "JavaScript", "React", "Node.js", "AWS"],
                    "soft_skills": ["Leadership", "Communication"]
                }
            }
        }
        
        job_data = {
            "title": "Senior Full Stack Developer",
            "requirements": ["Python", "React", "AWS"],
            "required_skills": ["Python", "JavaScript"],
            "preferred_skills": ["React", "AWS", "Docker"],
            "experience_requirements": {"minimum_years": 5, "level": "senior"}
        }
        
        source_text = "Senior software developer skilled in Python, JavaScript, React, and AWS cloud services."
        extracted_skills = {
            "technical": ["Python", "JavaScript", "React", "AWS"],
            "soft": ["Software development"]
        }
        
        # Run all scorers
        resume_result = resume_scorer.score_resume_analysis(resume_data, ["Python", "React", "AWS"])
        job_result = job_scorer.score_job_matching(resume_data, job_data)
        skill_result = skill_scorer.score_skill_extraction(source_text, extracted_skills)
        
        # Validate all results
        for result in [resume_result, job_result, skill_result]:
            assert 0.0 <= result.overall_score <= 1.0
            assert result.evaluation_time >= 0.0  # Allow ultra-fast execution
            assert len(result.component_scores) > 0
            assert all(0.0 <= score.score <= 1.0 for score in result.component_scores)
        
        # Validate domain-specific results
        assert resume_result.domain == "resume_analysis"
        assert job_result.domain == "job_matching"
        assert skill_result.domain == "skill_extraction"
        
        # Overall quality should be good for this test data
        assert resume_result.overall_score > 0.7
        assert job_result.overall_score > 0.6
        assert skill_result.overall_score > 0.7
    
    def test_scoring_error_handling(self):
        """Test scoring harness error handling."""
        scorer = ResumeAnalysisScorer()
        
        # Test with empty resume data
        empty_resume = {"sections": {}}
        result = scorer.score_resume_analysis(empty_resume, [])
        
        # Should handle gracefully with low scores
        assert result.overall_score < 0.5
        assert result.overall_level in [ScoreLevel.POOR, ScoreLevel.CRITICAL]
        
        # Test with None values
        try:
            scorer.score_resume_analysis(None, [])
            assert False, "Should raise exception for None input"
        except (AttributeError, TypeError):
            pass  # Expected behavior
        
        # Test job matching scorer with invalid data
        job_scorer = JobMatchingScorer()
        invalid_job = {"title": "Test Job"}  # Missing required fields
        result = job_scorer.score_job_matching(empty_resume, invalid_job)
        
        # Should handle gracefully
        assert 0.0 <= result.overall_score <= 1.0
        assert result.domain == "job_matching"
