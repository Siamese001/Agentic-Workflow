"""
ATS Optimizer Service
LEVEL 5 - Applicant Tracking System optimization and compliance
"""

from typing import Dict, List, Any
import re
from dataclasses import dataclass
from collections import Counter

@dataclass
class ATSOptimizationResult:
    """Results of ATS optimization analysis"""
    score: float
    recommendations: List[str]
    keyword_density: Dict[str, float]
    format_issues: List[str]
    compliance_score: float

class ATSOptimizer:
    """Optimizes resume content for ATS systems and job matching"""

    def __init__(self):
        self.ats_keywords = {
            "technical": ["python", "java", "javascript", "sql", "aws", "docker", "kubernetes", "git", "ci/cd"],
            "soft_skills": ["leadership", "communication", "teamwork", "problem-solving", "analytical", "project management"],
            "action_verbs": ["developed", "implemented", "managed", "led", "optimized", "designed", "coordinated", "achieved"],
            "metrics": ["increased", "decreased", "reduced", "improved", "enhanced", "streamlined", "automated"]
        }

        self.formatting_rules = {
            "max_bullet_points": 8,
            "max_line_length": 80,
            "required_sections": ["experience", "education", "skills"],
            "avoid_keywords": ["responsible for", "duties included", "worked on"]
        }

    async def optimize_resume(
        self,
        resume_content: Dict[str, Any],
        job_description: Dict[str, Any]
    ) -> ATSOptimizationResult:
        """
        Optimize resume content for ATS compatibility and job matching
        
        Args:
            resume_content: Current resume structure
            job_description: Target job requirements
            
        Returns:
            ATS optimization results with recommendations
        """
        # Extract job keywords
        job_keywords = await self._extract_job_keywords(job_description)

        # Analyze keyword density
        keyword_analysis = await self._analyze_keyword_density(resume_content, job_keywords)

        # Check formatting compliance
        format_issues = await self._check_formatting(resume_content)

        # Generate optimization recommendations
        recommendations = await self._generate_recommendations(
            resume_content, job_keywords, keyword_analysis, format_issues
        )

        # Calculate overall scores
        ats_score = await self._calculate_ats_score(keyword_analysis, format_issues)
        compliance_score = await self._calculate_compliance_score(format_issues)

        return ATSOptimizationResult(
            score=ats_score,
            recommendations=recommendations,
            keyword_density=keyword_analysis,
            format_issues=format_issues,
            compliance_score=compliance_score
        )

    async def _extract_job_keywords(self, job_description: Dict[str, Any]) -> List[str]:
        """Extract and prioritize keywords from job description"""
        keywords = []

        # Extract from requirements
        requirements = job_description.get("requirements", [])
        for req in requirements:
            # Clean and split requirements into individual keywords
            cleaned = re.sub(r'[^\w\s]', ' ', req.lower())
            words = cleaned.split()
            keywords.extend([word for word in words if len(word) > 2])

        # Extract from responsibilities
        responsibilities = job_description.get("responsibilities", [])
        for resp in responsibilities:
            cleaned = re.sub(r'[^\w\s]', ' ', resp.lower())
            words = cleaned.split()
            keywords.extend([word for word in words if len(word) > 2])

        # Add job title and field-specific terms
        job_title = job_description.get("title", "").lower()
        keywords.extend(job_title.split())

        # Remove duplicates and prioritize
        keyword_counts = Counter(keywords)
        prioritized_keywords = [kw for kw, count in keyword_counts.most_common(20)]

        return prioritized_keywords

    async def _analyze_keyword_density(
        self,
        resume_content: Dict[str, Any],
        job_keywords: List[str]
    ) -> Dict[str, float]:
        """Analyze keyword density in resume content"""
        all_text = ""

        # Extract all text from resume sections
        for section in resume_content.values():
            if isinstance(section.get("content"), list):
                all_text += " ".join(section["content"]).lower()
            elif isinstance(section.get("content"), str):
                all_text += section["content"].lower()

        # Calculate keyword density
        total_words = len(all_text.split())
        keyword_density = {}

        for keyword in job_keywords:
            keyword_count = all_text.count(keyword)
            density = (keyword_count / total_words * 100) if total_words > 0 else 0
            keyword_density[keyword] = density

        return keyword_density

    async def _check_formatting(self, resume_content: Dict[str, Any]) -> List[str]:
        """Check resume formatting for ATS compliance"""
        issues = []

        # Check required sections
        existing_sections = list(resume_content.keys())
        for required_section in self.formatting_rules["required_sections"]:
            if not any(required_section in section.lower() for section in existing_sections):
                issues.append(f"Missing required section: {required_section}")

        # Check bullet point counts
        for section_name, section in resume_content.items():
            content = section.get("content", [])
            if isinstance(content, list):
                bullet_count = len([item for item in content if item.strip().startswith("•")])
                if bullet_count > self.formatting_rules["max_bullet_points"]:
                    issues.append(f"Too many bullet points in {section_name}: {bullet_count}")

        # Check line lengths
        for section_name, section in resume_content.items():
            content = section.get("content", [])
            if isinstance(content, list):
                for line in content:
                    if len(line) > self.formatting_rules["max_line_length"]:
                        issues.append(f"Line too long in {section_name}: {len(line)} characters")

        # Check for problematic phrases
        all_text = " ".join([
            " ".join(section.get("content", [])) if isinstance(section.get("content"), list)
            else section.get("content", "")
            for section in resume_content.values()
        ]).lower()

        for avoid_phrase in self.formatting_rules["avoid_keywords"]:
            if avoid_phrase in all_text:
                issues.append(f"Contains problematic phrase: '{avoid_phrase}'")

        return issues

    async def _generate_recommendations(
        self,
        resume_content: Dict[str, Any],
        job_keywords: List[str],
        keyword_analysis: Dict[str, float],
        format_issues: List[str]
    ) -> List[str]:
        """Generate specific optimization recommendations"""
        recommendations = []

        # Keyword recommendations
        low_density_keywords = [
            kw for kw, density in keyword_analysis.items()
            if density < 0.5 and kw in job_keywords[:10]
        ]

        if low_density_keywords:
            recommendations.append(
                f"Add these important keywords: {', '.join(low_density_keywords[:5])}"
            )

        # Action verb recommendations
        all_text = " ".join([
            " ".join(section.get("content", [])) if isinstance(section.get("content"), list)
            else section.get("content", "")
            for section in resume_content.values()
        ]).lower()

        missing_action_verbs = [
            verb for verb in self.ats_keywords["action_verbs"]
            if verb not in all_text
        ]

        if missing_action_verbs:
            recommendations.append(
                f"Incorporate action verbs: {', '.join(missing_action_verbs[:3])}"
            )

        # Format recommendations
        if format_issues:
            recommendations.extend(format_issues[:3])

        # Section-specific recommendations
        for section_name, section in resume_content.items():
            content = section.get("content", [])
            if isinstance(content, list):
                # Check for quantifiable achievements
                has_metrics = any(
                    any(metric in item.lower() for metric in self.ats_keywords["metrics"])
                    for item in content
                )

                if not has_metrics and "experience" in section_name.lower():
                    recommendations.append(
                        f"Add quantifiable metrics to {section_name} (e.g., 'increased by 25%', 'reduced costs by $10k')"
                    )

        return recommendations

    async def _calculate_ats_score(
        self,
        keyword_analysis: Dict[str, float],
        format_issues: List[str]
    ) -> float:
        """Calculate overall ATS compatibility score"""
        # Keyword score (60% weight)
        keyword_score = 0
        if keyword_analysis:
            avg_density = sum(keyword_analysis.values()) / len(keyword_analysis)
            keyword_score = min(avg_density * 10, 60)  # Cap at 60

        # Format score (40% weight)
        format_score = max(0, 40 - len(format_issues) * 5)

        return keyword_score + format_score

    async def _calculate_compliance_score(self, format_issues: List[str]) -> float:
        """Calculate ATS compliance score"""
        total_possible_issues = 20  # Estimated maximum issues
        compliance_score = max(0, 100 - (len(format_issues) * 5))
        return compliance_score

__all__ = ["ATSOptimizer", "ATSOptimizationResult"]
