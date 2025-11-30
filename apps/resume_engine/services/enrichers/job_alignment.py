"""
Job Alignment Service
LEVEL 5 - Job requirement analysis and resume-job alignment optimization
"""

from typing import Dict, List, Any, Tuple
import re
from dataclasses import dataclass

@dataclass
class AlignmentResult:
    """Results of job-resume alignment analysis"""
    alignment_score: float
    matched_requirements: List[str]
    missing_requirements: List[str]
    strength_areas: List[str]
    improvement_areas: List[str]
    optimization_suggestions: List[str]

class JobAligner:
    """Analyzes job requirements and optimizes resume alignment"""

    def __init__(self):
        self.requirement_categories = {
            "technical_skills": ["python", "java", "javascript", "sql", "aws", "docker", "kubernetes"],
            "experience_level": ["senior", "junior", "lead", "manager", "entry", "mid"],
            "education": ["bachelor", "master", "phd", "degree", "certification"],
            "industry": ["healthcare", "finance", "technology", "retail", "manufacturing"],
            "responsibilities": ["develop", "manage", "lead", "design", "implement", "optimize"]
        }

        self.alignment_weights = {
            "technical_skills": 0.35,
            "experience_level": 0.20,
            "education": 0.15,
            "industry": 0.15,
            "responsibilities": 0.15
        }

    async def analyze_alignment(
        self,
        resume_content: Dict[str, Any],
        job_description: Dict[str, Any]
    ) -> AlignmentResult:
        """
        Analyze how well the resume aligns with job requirements
        
        Args:
            resume_content: Current resume structure
            job_description: Target job information
            
        Returns:
            Detailed alignment analysis with recommendations
        """
        # Extract requirements from job description
        job_requirements = await self._extract_requirements(job_description)

        # Extract skills and experience from resume
        resume_profile = await self._extract_resume_profile(resume_content)

        # Calculate alignment for each category
        category_scores = {}
        matched_requirements = []
        missing_requirements = []

        for category, requirements in job_requirements.items():
            category_alignment, matched, missing = await self._calculate_category_alignment(
                category, requirements, resume_profile
            )
            category_scores[category] = category_alignment
            matched_requirements.extend(matched)
            missing_requirements.extend(missing)

        # Calculate overall alignment score
        overall_score = await self._calculate_overall_score(category_scores)

        # Identify strength and improvement areas
        strength_areas = await self._identify_strength_areas(category_scores)
        improvement_areas = await self._identify_improvement_areas(category_scores)

        # Generate optimization suggestions
        optimization_suggestions = await self._generate_optimization_suggestions(
            category_scores, missing_requirements, resume_profile
        )

        return AlignmentResult(
            alignment_score=overall_score,
            matched_requirements=matched_requirements,
            missing_requirements=missing_requirements,
            strength_areas=strength_areas,
            improvement_areas=improvement_areas,
            optimization_suggestions=optimization_suggestions
        )

    async def _extract_requirements(self, job_description: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract and categorize job requirements"""
        requirements = {category: [] for category in self.requirement_categories}

        # Extract from requirements section
        job_reqs = job_description.get("requirements", [])
        for req in job_reqs:
            req_lower = req.lower()

            # Categorize requirements
            for category, keywords in self.requirement_categories.items():
                if any(keyword in req_lower for keyword in keywords):
                    requirements[category].append(req)
                    break
            else:
                # Add to responsibilities if no specific category matches
                requirements["responsibilities"].append(req)

        # Extract from responsibilities
        responsibilities = job_description.get("responsibilities", [])
        for resp in responsibilities:
            resp_lower = resp.lower()

            for category, keywords in self.requirement_categories.items():
                if category == "responsibilities" or any(keyword in resp_lower for keyword in keywords):
                    requirements[category].append(resp)
                    break

        return requirements

    async def _extract_resume_profile(self, resume_content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key information from resume content"""
        profile = {
            "skills": set(),
            "experience": [],
            "education": [],
            "achievements": [],
            "responsibilities": []
        }

        # Extract from all sections
        for section_name, section in resume_content.items():
            content = section.get("content", [])
            if isinstance(content, list):
                text_content = " ".join(content).lower()
            else:
                text_content = str(content).lower()

            # Extract skills
            if "skill" in section_name.lower():
                words = re.findall(r'\b\w+\b', text_content)
                profile["skills"].update([word for word in words if len(word) > 2])

            # Extract experience
            if "experience" in section_name.lower():
                profile["experience"].extend(content)

                # Look for achievement indicators
                for line in content:
                    if any(indicator in line.lower() for indicator in ["increased", "decreased", "improved", "achieved"]):
                        profile["achievements"].append(line)

            # Extract education
            if "education" in section_name.lower():
                profile["education"].extend(content)

            # Extract responsibilities
            profile["responsibilities"].extend(content)

        return profile

    async def _calculate_category_alignment(
        self,
        category: str,
        requirements: List[str],
        resume_profile: Dict[str, Any]
    ) -> Tuple[float, List[str], List[str]]:
        """Calculate alignment score for a specific category"""
        if not requirements:
            return 1.0, [], []  # Perfect alignment if no requirements

        matched = []
        missing = []

        resume_text = " ".join([
            " ".join(resume_profile.get("skills", set())),
            " ".join(resume_profile.get("experience", [])),
            " ".join(resume_profile.get("education", [])),
            " ".join(resume_profile.get("responsibilities", []))
        ]).lower()

        for requirement in requirements:
            req_lower = requirement.lower()

            # Check for direct matches
            if any(word in resume_text for word in req_lower.split() if len(word) > 2):
                matched.append(requirement)
            else:
                missing.append(requirement)

        # Calculate alignment score
        alignment = len(matched) / len(requirements) if requirements else 1.0

        return alignment, matched, missing

    async def _calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """Calculate weighted overall alignment score"""
        total_score = 0
        total_weight = 0

        for category, score in category_scores.items():
            weight = self.alignment_weights.get(category, 0.1)
            total_score += score * weight
            total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0

    async def _identify_strength_areas(self, category_scores: Dict[str, float]) -> List[str]:
        """Identify areas where the resume aligns well"""
        strengths = []

        for category, score in category_scores.items():
            if score >= 0.8:  # 80% or higher alignment
                category_name = category.replace("_", " ").title()
                strengths.append(f"{category_name}: {score:.1%} alignment")

        return strengths

    async def _identify_improvement_areas(self, category_scores: Dict[str, float]) -> List[str]:
        """Identify areas needing improvement"""
        improvements = []

        for category, score in category_scores.items():
            if score < 0.6:  # Less than 60% alignment
                category_name = category.replace("_", " ").title()
                improvements.append(f"{category_name}: {score:.1%} alignment")

        return improvements

    async def _generate_optimization_suggestions(
        self,
        category_scores: Dict[str, float],
        missing_requirements: List[str],
        resume_profile: Dict[str, Any]
    ) -> List[str]:
        """Generate specific optimization suggestions"""
        suggestions = []

        # Address missing requirements
        if missing_requirements:
            suggestions.append(f"Address these key requirements: {', '.join(missing_requirements[:3])}")

        # Category-specific suggestions
        if category_scores.get("technical_skills", 0) < 0.7:
            suggestions.append("Highlight more technical skills and technologies")

        if category_scores.get("experience_level", 0) < 0.7:
            suggestions.append("Emphasize relevant experience level and achievements")

        if category_scores.get("education", 0) < 0.7:
            suggestions.append("Showcase relevant education and certifications")

        if category_scores.get("responsibilities", 0) < 0.7:
            suggestions.append("Include more quantifiable achievements and responsibilities")

        # General optimization tips
        if not resume_profile.get("achievements"):
            suggestions.append("Add quantifiable achievements with metrics (e.g., 'increased efficiency by 25%')")

        skill_count = len(resume_profile.get("skills", set()))
        if skill_count < 10:
            suggestions.append("Expand skills section to include more relevant technical and soft skills")

        return suggestions[:5]  # Limit to top 5 suggestions

__all__ = ["JobAligner", "AlignmentResult"]
