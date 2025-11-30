"""
Skill Expander Service
LEVEL 5 - Skill analysis, expansion, and enhancement
"""

from typing import Dict, List, Any
import re
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class SkillAnalysis:
    """Results of skill analysis and expansion"""
    expanded_skills: List[str]
    skill_categories: Dict[str, List[str]]
    proficiency_levels: Dict[str, str]
    recommended_additions: List[str]

class SkillExpander:
    """Analyzes and expands user skills based on job requirements and industry standards"""

    def __init__(self):
        self.skill_taxonomy = {
            "programming_languages": {
                "python": ["django", "flask", "fastapi", "pandas", "numpy", "scikit-learn"],
                "javascript": ["react", "vue", "angular", "node.js", "express", "typescript"],
                "java": ["spring", "hibernate", "maven", "junit", "jvm"],
                "sql": ["postgresql", "mysql", "oracle", "nosql", "mongodb", "redis"]
            },
            "cloud_platforms": {
                "aws": ["ec2", "s3", "lambda", "rds", "dynamodb", "cloudformation"],
                "azure": ["app_service", "blob_storage", "functions", "sql_database"],
                "gcp": ["compute_engine", "cloud_storage", "cloud_functions", "bigquery"]
            },
            "devops_tools": {
                "docker": ["kubernetes", "helm", "jenkins", "gitlab_ci", "github_actions"],
                "git": ["version_control", "branching_strategies", "merge_conflicts"],
                "ci_cd": ["continuous_integration", "continuous_deployment", "automation"]
            },
            "soft_skills": {
                "leadership": ["team_management", "mentoring", "decision_making", "strategic_planning"],
                "communication": ["presentations", "technical_writing", "stakeholder_management"],
                "problem_solving": ["analytical_thinking", "troubleshooting", "root_cause_analysis"]
            }
        }

        self.proficiency_levels = {
            "beginner": ["basic", "familiar", "learning"],
            "intermediate": ["proficient", "experienced", "competent"],
            "advanced": ["expert", "advanced", "specialized", "senior"]
        }

    async def expand_skills(
        self,
        user_skills: List[str],
        job_description: Dict[str, Any]
    ) -> SkillAnalysis:
        """
        Expand and categorize user skills based on job requirements
        
        Args:
            user_skills: List of user's current skills
            job_description: Target job requirements
            
        Returns:
            Skill analysis with expanded skills and recommendations
        """
        # Normalize and categorize user skills
        normalized_skills = await self._normalize_skills(user_skills)
        skill_categories = await self._categorize_skills(normalized_skills)

        # Extract job requirements
        job_requirements = await self._extract_skill_requirements(job_description)

        # Expand skills based on job requirements
        expanded_skills = await self._expand_based_on_requirements(normalized_skills, job_requirements)

        # Determine proficiency levels
        proficiency_levels = await self._estimate_proficiency_levels(expanded_skills)

        # Generate recommendations
        recommended_additions = await self._generate_skill_recommendations(
            expanded_skills, job_requirements
        )

        return SkillAnalysis(
            expanded_skills=expanded_skills,
            skill_categories=skill_categories,
            proficiency_levels=proficiency_levels,
            recommended_additions=recommended_additions
        )

    async def _normalize_skills(self, skills: List[str]) -> List[str]:
        """Normalize skill names to standard format"""
        normalized = []

        for skill in skills:
            # Convert to lowercase and remove special characters
            clean_skill = re.sub(r'[^\w\s]', '', skill.lower().strip())

            # Map common abbreviations
            skill_mapping = {
                "js": "javascript",
                "ts": "typescript",
                "py": "python",
                "db": "database",
                "ui": "user_interface",
                "ux": "user_experience",
                "ml": "machine_learning",
                "ai": "artificial_intelligence"
            }

            if clean_skill in skill_mapping:
                clean_skill = skill_mapping[clean_skill]

            if clean_skill and len(clean_skill) > 1:
                normalized.append(clean_skill)

        return list(set(normalized))  # Remove duplicates

    async def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into technical domains"""
        categories = defaultdict(list)

        for skill in skills:
            categorized = False

            for category, skill_map in self.skill_taxonomy.items():
                for base_skill, related_skills in skill_map.items():
                    if skill == base_skill or skill in related_skills:
                        categories[category].append(skill)
                        categorized = True
                        break

                if categorized:
                    break

            if not categorized:
                categories["other"].append(skill)

        return dict(categories)

    async def _extract_skill_requirements(self, job_description: Dict[str, Any]) -> List[str]:
        """Extract skill requirements from job description"""
        requirements = []

        # Extract from requirements section
        job_reqs = job_description.get("requirements", [])
        for req in job_reqs:
            # Find technical terms and skills
            words = re.findall(r'\b\w+\b', req.lower())
            requirements.extend([word for word in words if len(word) > 2])

        # Extract from responsibilities
        responsibilities = job_description.get("responsibilities", [])
        for resp in responsibilities:
            words = re.findall(r'\b\w+\b', resp.lower())
            requirements.extend([word for word in words if len(word) > 2])

        # Filter for common skill keywords
        skill_keywords = set()
        for category in self.skill_taxonomy.values():
            for base_skill, related_skills in category.items():
                skill_keywords.add(base_skill)
                skill_keywords.update(related_skills)

        filtered_requirements = [
            req for req in requirements
            if req in skill_keywords or any(req in skill for skill in skill_keywords)
        ]

        return list(set(filtered_requirements))

    async def _expand_based_on_requirements(
        self,
        user_skills: List[str],
        job_requirements: List[str]
    ) -> List[str]:
        """Expand user skills based on job requirements"""
        expanded = set(user_skills)

        # Find matching base skills
        for req_skill in job_requirements:
            for category, skill_map in self.skill_taxonomy.items():
                for base_skill, related_skills in skill_map.items():
                    if req_skill == base_skill or req_skill in related_skills:
                        # User has this skill or related skill
                        if base_skill in user_skills or any(related in user_skills for related in related_skills):
                            expanded.add(base_skill)
                            expanded.update(related_skills)

        return list(expanded)

    async def _estimate_proficiency_levels(self, skills: List[str]) -> Dict[str, str]:
        """Estimate proficiency levels based on skill context"""
        proficiency_map = {}

        for skill in skills:
            # Default to intermediate for most skills
            proficiency_map[skill] = "intermediate"

            # Advanced indicators
            if any(indicator in skill for indicator in ["senior", "lead", "architect", "expert"]):
                proficiency_map[skill] = "advanced"

            # Beginner indicators
            if any(indicator in skill for indicator in ["junior", "basic", "learning"]):
                proficiency_map[skill] = "beginner"

        return proficiency_map

    async def _generate_skill_recommendations(
        self,
        current_skills: List[str],
        job_requirements: List[str]
    ) -> List[str]:
        """Generate recommendations for missing or additional skills"""
        recommendations = []

        # Find missing required skills
        missing_skills = [
            req for req in job_requirements
            if req not in current_skills and req not in " ".join(current_skills)
        ]

        if missing_skills:
            recommendations.append(f"Consider adding these key skills: {', '.join(missing_skills[:5])}")

        # Suggest complementary skills
        for skill in current_skills:
            for category, skill_map in self.skill_taxonomy.items():
                if skill in skill_map:
                    base_skill = skill
                    related_skills = skill_map[base_skill]

                    # Suggest related skills not already present
                    missing_related = [
                        related for related in related_skills
                        if related not in current_skills
                    ]

                    if missing_related:
                        recommendations.append(
                            f"Complementary skills for {base_skill}: {', '.join(missing_related[:3])}"
                        )
                    break

        # Industry trend recommendations
        trending_skills = ["cloud_native", "microservices", "kubernetes", "machine_learning", "data_analytics"]
        missing_trending = [
            skill for skill in trending_skills
            if skill not in current_skills and skill not in " ".join(current_skills)
        ]

        if missing_trending:
            recommendations.append(f"Trending skills to consider: {', '.join(missing_trending[:3])}")

        return recommendations[:5]  # Limit to top 5 recommendations

__all__ = ["SkillExpander", "SkillAnalysis"]
