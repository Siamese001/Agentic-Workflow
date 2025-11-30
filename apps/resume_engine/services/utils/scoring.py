"""
Resume Scoring Utilities
LEVEL 5 - Resume quality scoring and evaluation algorithms
"""

from typing import Dict, List, Any, Optional, Tuple
import re
from dataclasses import dataclass
from enum import Enum

class ScoreType(Enum):
    """Types of resume scores"""
    ATS_SCORE = "ats_score"
    CONTENT_QUALITY = "content_quality"
    JOB_ALIGNMENT = "job_alignment"
    READABILITY = "readability"
    COMPLETENESS = "completeness"

@dataclass
class ScoreResult:
    """Individual scoring result"""
    score_type: ScoreType
    score: float
    max_score: float
    details: Dict[str, Any]
    recommendations: List[str]

class ResumeScorer:
    """Calculates various types of resume scores for quality assessment"""
    
    def __init__(self):
        self.scoring_weights = {
            ScoreType.ATS_SCORE: 0.3,
            ScoreType.CONTENT_QUALITY: 0.25,
            ScoreType.JOB_ALIGNMENT: 0.25,
            ScoreType.READABILITY: 0.1,
            ScoreType.COMPLETENESS: 0.1
        }
        
        self.ats_keywords = {
            "technical": ["python", "java", "javascript", "sql", "aws", "docker", "kubernetes"],
            "soft_skills": ["leadership", "communication", "teamwork", "problem-solving"],
            "action_verbs": ["developed", "implemented", "managed", "led", "optimized", "achieved"]
        }
    
    async def calculate_comprehensive_score(
        self,
        resume_content: Dict[str, Any],
        job_description: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive resume score across multiple dimensions
        
        Args:
            resume_content: Resume structure to score
            job_description: Optional job requirements for alignment scoring
            
        Returns:
            Comprehensive scoring results with breakdown
        """
        scores = {}
        
        # Calculate individual scores
        ats_result = await self._calculate_ats_score(resume_content)
        scores[ScoreType.ATS_SCORE.value] = ats_result
        
        content_result = await self._calculate_content_quality_score(resume_content)
        scores[ScoreType.CONTENT_QUALITY.value] = content_result
        
        if job_description:
            alignment_result = await self._calculate_job_alignment_score(resume_content, job_description)
            scores[ScoreType.JOB_ALIGNMENT.value] = alignment_result
        else:
            scores[ScoreType.JOB_ALIGNMENT.value] = ScoreResult(
                score_type=ScoreType.JOB_ALIGNMENT,
                score=0.7,  # Default neutral score
                max_score=1.0,
                details={"note": "No job description provided"},
                recommendations=[]
            )
        
        readability_result = await self._calculate_readability_score(resume_content)
        scores[ScoreType.READABILITY.value] = readability_result
        
        completeness_result = await self._calculate_completeness_score(resume_content)
        scores[ScoreType.COMPLETENESS.value] = completeness_result
        
        # Calculate weighted overall score
        overall_score = await self._calculate_weighted_score(scores)
        
        # Generate overall recommendations
        overall_recommendations = await self._generate_overall_recommendations(scores)
        
        return {
            "overall_score": overall_score,
            "individual_scores": scores,
            "grade": await self._get_grade(overall_score),
            "recommendations": overall_recommendations,
            "strengths": await self._identify_strengths(scores),
            "improvement_areas": await self._identify_improvement_areas(scores)
        }
    
    async def _calculate_ats_score(self, resume_content: Dict[str, Any]) -> ScoreResult:
        """Calculate ATS optimization score"""
        score = 0.0
        details = {}
        recommendations = []
        
        # Extract all text from resume
        all_text = ""
        for section in resume_content.values():
            content = section.get("content", [])
            if isinstance(content, list):
                all_text += " ".join(content) + " "
        
        all_text = all_text.lower()
        
        # Check keyword density
        keyword_matches = 0
        total_keywords = 0
        
        for category, keywords in self.ats_keywords.items():
            total_keywords += len(keywords)
            for keyword in keywords:
                if keyword in all_text:
                    keyword_matches += 1
        
        keyword_density = keyword_matches / total_keywords if total_keywords > 0 else 0
        score += keyword_density * 0.4
        details["keyword_density"] = keyword_density
        
        if keyword_density < 0.3:
            recommendations.append("Include more relevant keywords for better ATS optimization")
        
        # Check formatting compliance
        formatting_issues = 0
        
        # Check for special characters
        special_chars = ["★", "♦", "►"]
        for char in special_chars:
            if char in all_text:
                formatting_issues += 1
        
        # Check section headers
        section_headers = list(resume_content.keys())
        standard_headers = ["summary", "experience", "education", "skills"]
        non_standard = len([
            header for header in section_headers
            if header.lower() not in standard_headers
        ])
        
        formatting_issues += non_standard
        
        format_score = max(0, 1.0 - (formatting_issues * 0.1))
        score += format_score * 0.3
        details["formatting_score"] = format_score
        
        if formatting_issues > 0:
            recommendations.append("Use standard section headers and avoid special characters")
        
        # Check action verb usage
        action_verbs_found = sum(1 for verb in self.ats_keywords["action_verbs"] if verb in all_text)
        action_verb_score = action_verbs_found / len(self.ats_keywords["action_verbs"])
        score += action_verb_score * 0.3
        details["action_verb_score"] = action_verb_score
        
        if action_verb_score < 0.5:
            recommendations.append("Start bullet points with strong action verbs")
        
        return ScoreResult(
            score_type=ScoreType.ATS_SCORE,
            score=min(score, 1.0),
            max_score=1.0,
            details=details,
            recommendations=recommendations
        )
    
    async def _calculate_content_quality_score(self, resume_content: Dict[str, Any]) -> ScoreResult:
        """Calculate content quality score"""
        score = 0.8  # Base score
        details = {}
        recommendations = []
        
        # Check word count
        total_words = 0
        for section in resume_content.values():
            content = section.get("content", [])
            if isinstance(content, list):
                total_words += sum(len(item.split()) for item in content)
        
        details["word_count"] = total_words
        
        if total_words < 150:
            score -= 0.3
            recommendations.append("Resume is too brief - expand content")
        elif total_words > 600:
            score -= 0.1
            recommendations.append("Consider condensing for one-page format")
        
        # Check section balance
        section_word_counts = {}
        for section_name, section in resume_content.items():
            content = section.get("content", [])
            if isinstance(content, list):
                section_word_counts[section_name] = sum(len(item.split()) for item in content)
        
        details["section_word_counts"] = section_word_counts
        
        # Check for quantifiable achievements
        all_text = " ".join([
            " ".join(section.get("content", [])) if isinstance(section.get("content"), list)
            else str(section.get("content", ""))
            for section in resume_content.values()
        ]).lower()
        
        has_metrics = any(indicator in all_text for indicator in ["%", "increased", "decreased", "saved", "generated"])
        if has_metrics:
            score += 0.1
        else:
            recommendations.append("Add quantifiable achievements with metrics")
        
        details["has_quantifiable_achievements"] = has_metrics
        
        return ScoreResult(
            score_type=ScoreType.CONTENT_QUALITY,
            score=max(min(score, 1.0), 0.0),
            max_score=1.0,
            details=details,
            recommendations=recommendations
        )
    
    async def _calculate_job_alignment_score(
        self,
        resume_content: Dict[str, Any],
        job_description: Dict[str, Any]
    ) -> ScoreResult:
        """Calculate job alignment score"""
        score = 0.0
        details = {}
        recommendations = []
        
        # Extract job requirements
        job_requirements = job_description.get("requirements", [])
        job_text = " ".join(job_requirements).lower()
        
        # Extract resume text
        resume_text = ""
        for section in resume_content.values():
            content = section.get("content", [])
            if isinstance(content, list):
                resume_text += " ".join(content) + " "
        
        resume_text = resume_text.lower()
        
        # Calculate keyword matching
        job_keywords = re.findall(r'\b\w+\b', job_text)
        job_keywords = [kw for kw in job_keywords if len(kw) > 3]
        
        matched_keywords = sum(1 for kw in job_keywords if kw in resume_text)
        alignment_score = matched_keywords / len(job_keywords) if job_keywords else 0
        
        score += alignment_score * 0.6
        details["keyword_alignment"] = alignment_score
        
        if alignment_score < 0.5:
            recommendations.append("Include more keywords from job requirements")
        
        # Check skills alignment
        user_skills = []
        for section in resume_content.values():
            if "skill" in str(section).lower():
                content = section.get("content", [])
                if isinstance(content, list):
                    user_skills.extend([item.lower().replace("• ", "").strip() for item in content])
        
        required_skills = [req.lower() for req in job_requirements if len(req.split()) <= 3]
        skills_match = sum(1 for skill in user_skills for req in required_skills if req in skill)
        skills_alignment = skills_match / len(required_skills) if required_skills else 0
        
        score += skills_alignment * 0.4
        details["skills_alignment"] = skills_alignment
        
        if skills_alignment < 0.6:
            recommendations.append("Highlight skills that match job requirements")
        
        return ScoreResult(
            score_type=ScoreType.JOB_ALIGNMENT,
            score=min(score, 1.0),
            max_score=1.0,
            details=details,
            recommendations=recommendations
        )
    
    async def _calculate_readability_score(self, resume_content: Dict[str, Any]) -> ScoreResult:
        """Calculate readability score"""
        score = 0.8  # Base score
        details = {}
        recommendations = []
        
        # Check sentence length
        all_sentences = []
        for section in resume_content.values():
            content = section.get("content", [])
            if isinstance(content, list):
                for item in content:
                    sentences = re.split(r'[.!?]+', item)
                    all_sentences.extend([s.strip() for s in sentences if s.strip()])
        
        if all_sentences:
            avg_sentence_length = sum(len(s.split()) for s in all_sentences) / len(all_sentences)
            details["avg_sentence_length"] = avg_sentence_length
            
            if avg_sentence_length > 20:
                score -= 0.2
                recommendations.append("Use shorter sentences for better readability")
            elif avg_sentence_length < 8:
                score -= 0.1
                recommendations.append("Consider using more complete sentences")
        
        # Check bullet point consistency
        bullet_points = []
        for section in resume_content.values():
            content = section.get("content", [])
            if isinstance(content, list):
                bullet_points.extend([item for item in content if item.strip().startswith("•")])
        
        if bullet_points:
            avg_bullet_length = sum(len(bp.split()) for bp in bullet_points) / len(bullet_points)
            details["avg_bullet_length"] = avg_bullet_length
            
            if avg_bullet_length > 15:
                score -= 0.1
                recommendations.append("Keep bullet points concise")
        
        return ScoreResult(
            score_type=ScoreType.READABILITY,
            score=max(min(score, 1.0), 0.0),
            max_score=1.0,
            details=details,
            recommendations=recommendations
        )
    
    async def _calculate_completeness_score(self, resume_content: Dict[str, Any]) -> ScoreResult:
        """Calculate completeness score"""
        score = 0.0
        details = {}
        recommendations = []
        
        required_sections = ["experience", "education", "skills"]
        existing_sections = [section.lower() for section in resume_content.keys()]
        
        sections_present = sum(1 for req in required_sections if req in existing_sections)
        completeness_score = sections_present / len(required_sections)
        
        score += completeness_score * 0.5
        details["sections_present"] = sections_present
        details["required_sections"] = len(required_sections)
        
        missing_sections = [req for req in required_sections if req not in existing_sections]
        if missing_sections:
            recommendations.append(f"Add missing sections: {', '.join(missing_sections)}")
        
        # Check for contact information
        all_text = ""
        for section in resume_content.values():
            content = section.get("content", [])
            if isinstance(content, list):
                all_text += " ".join(content) + " "
        
        has_email = "@" in all_text
        has_phone = len(re.findall(r'\d+', all_text)) >= 10
        
        contact_score = 0.5
        if has_email:
            contact_score += 0.25
        if has_phone:
            contact_score += 0.25
        
        score += contact_score * 0.5
        details["has_email"] = has_email
        details["has_phone"] = has_phone
        
        if not has_email:
            recommendations.append("Add email address")
        if not has_phone:
            recommendations.append("Add phone number")
        
        return ScoreResult(
            score_type=ScoreType.COMPLETENESS,
            score=min(score, 1.0),
            max_score=1.0,
            details=details,
            recommendations=recommendations
        )
    
    async def _calculate_weighted_score(self, scores: Dict[str, ScoreResult]) -> float:
        """Calculate weighted overall score"""
        total_score = 0.0
        total_weight = 0.0
        
        for score_result in scores.values():
            weight = self.scoring_weights.get(score_result.score_type, 0.1)
            total_score += score_result.score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    async def _get_grade(self, score: float) -> str:
        """Get letter grade for score"""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
    
    async def _generate_overall_recommendations(self, scores: Dict[str, ScoreResult]) -> List[str]:
        """Generate overall recommendations based on all scores"""
        all_recommendations = []
        
        for score_result in scores.values():
            all_recommendations.extend(score_result.recommendations)
        
        # Remove duplicates and prioritize
        unique_recommendations = list(set(all_recommendations))
        return unique_recommendations[:5]  # Top 5 recommendations
    
    async def _identify_strengths(self, scores: Dict[str, ScoreResult]) -> List[str]:
        """Identify areas of strength"""
        strengths = []
        
        for score_result in scores.values():
            if score_result.score >= 0.8:
                strengths.append(f"Strong {score_result.score_type.value.replace('_', ' ')}")
        
        return strengths
    
    async def _identify_improvement_areas(self, scores: Dict[str, ScoreResult]) -> List[str]:
        """Identify areas needing improvement"""
        improvements = []
        
        for score_result in scores.values():
            if score_result.score < 0.7:
                improvements.append(f"Improve {score_result.score_type.value.replace('_', ' ')}")
        
        return improvements

__all__ = ["ResumeScorer", "ScoreResult", "ScoreType"]
