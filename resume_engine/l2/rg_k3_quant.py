#!/usr/bin/env python3
"""
L2 Execution Layer - K3 Quant
Atomic quantitative scoring and metrics analysis
"""

from typing import Dict, Any, List, Optional
# RG_capabilities is now at root level - no sys.path manipulation needed
from RG_capabilities.rg_atomic_spec import ATOMIC_RG_SPEC

class K3Quantifier:
    """K3 Quant - Atomic quantitative scoring and metrics analysis"""
    
    def __init__(self):
        self.quant_rules = ATOMIC_RG_SPEC.get("quant", {})
        self.routing_rules = ATOMIC_RG_SPEC.get("routing", {})
        self.parameters = ATOMIC_RG_SPEC.get("parameters", {})
    
    def calculate_job_alignment_score(self, 
                                     cleaned_resume: Dict[str, Any],
                                     cleaned_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate job alignment scores between resume and job
        
        Args:
            cleaned_resume: Cleaned resume data from K2
            cleaned_job: Cleaned job data from K2
            
        Returns:
            Quantitative alignment scores
        """
        scores = {
            "skill_alignment": self._calculate_skill_alignment(
                cleaned_resume.get("skills", {}),
                cleaned_job.get("required_skills", [])
            ),
            "experience_alignment": self._calculate_experience_alignment(
                cleaned_resume.get("professional_experience", []),
                cleaned_job.get("experience_level", "")
            ),
            "qualification_alignment": self._calculate_qualification_alignment(
                cleaned_resume.get("education", []),
                cleaned_job.get("qualifications", [])
            ),
            "overall_alignment": 0.0,
            "metadata": {
                "scoring_rules_applied": list(self.quant_rules.keys())[:5],
                "scoring_timestamp": "2025-01-01T00:00:00Z"
            }
        }
        
        # Calculate weighted overall score
        weights = self.parameters.get("scoring_weights", {
            "skill_alignment": 0.4,
            "experience_alignment": 0.3,
            "qualification_alignment": 0.3
        })
        
        scores["overall_alignment"] = (
            scores["skill_alignment"] * weights.get("skill_alignment", 0.4) +
            scores["experience_alignment"] * weights.get("experience_alignment", 0.3) +
            scores["qualification_alignment"] * weights.get("qualification_alignment", 0.3)
        )
        
        return scores
    
    def calculate_resume_quality_metrics(self, cleaned_resume: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate resume quality metrics
        
        Args:
            cleaned_resume: Cleaned resume data from K2
            
        Returns:
            Resume quality metrics
        """
        metrics = {
            "content_completeness": self._calculate_completeness_score(cleaned_resume),
            "bullet_quality": self._calculate_bullet_quality(cleaned_resume.get("professional_experience", [])),
            "skill_diversity": self._calculate_skill_diversity(cleaned_resume.get("skills", {})),
            "experience_progression": self._calculate_experience_progression(cleaned_resume.get("professional_experience", [])),
            "overall_quality": 0.0,
            "metadata": {
                "metric_rules_applied": list(self.quant_rules.keys())[:3],
                "calculation_timestamp": "2025-01-01T00:00:00Z"
            }
        }
        
        # Calculate overall quality score
        metrics["overall_quality"] = (
            metrics["content_completeness"] * 0.3 +
            metrics["bullet_quality"] * 0.3 +
            metrics["skill_diversity"] * 0.2 +
            metrics["experience_progression"] * 0.2
        )
        
        return metrics
    
    def _calculate_skill_alignment(self, resume_skills: Dict[str, List[str]], 
                                 job_skills: List[str]) -> float:
        """Calculate skill alignment score"""
        if not job_skills:
            return 0.0
        
        # Flatten all resume skills
        all_resume_skills = []
        for skill_category in resume_skills.values():
            all_resume_skills.extend([skill.lower() for skill in skill_category])
        
        # Calculate matches
        matches = 0
        for job_skill in job_skills:
            if any(job_skill.lower() in resume_skill for resume_skill in all_resume_skills):
                matches += 1
        
        return matches / len(job_skills) if job_skills else 0.0
    
    def _calculate_experience_alignment(self, experience: List[Dict[str, Any]], 
                                       required_level: str) -> float:
        """Calculate experience alignment score"""
        if not experience or not required_level:
            return 0.0
        
        # Extract years of experience from most recent positions
        total_years = 0
        for exp in experience[-3:]:  # Consider last 3 positions
            dates = exp.get("dates", "")
            if dates:
                years = self._extract_years_from_dates(dates)
                total_years += years
        
        # Score based on required level
        if required_level == "junior":
            return min(total_years / 2, 1.0)  # 2+ years ideal
        elif required_level == "mid":
            return min(total_years / 5, 1.0)  # 5+ years ideal
        elif required_level == "senior":
            return min(total_years / 8, 1.0)  # 8+ years ideal
        
        return 0.5  # Default score
    
    def _calculate_qualification_alignment(self, education: List[Dict[str, Any]], 
                                          required_quals: List[str]) -> float:
        """Calculate qualification alignment score"""
        if not required_quals:
            return 0.0
        
        matches = 0
        education_text = " ".join([
            edu.get("degree", "") + " " + edu.get("field_of_study", "")
            for edu in education
        ]).lower()
        
        for qual in required_quals:
            if qual.lower() in education_text:
                matches += 1
        
        return matches / len(required_quals) if required_quals else 0.0
    
    def _calculate_completeness_score(self, resume: Dict[str, Any]) -> float:
        """Calculate resume completeness score"""
        required_sections = ["contact_info", "professional_experience", "education", "skills"]
        present_sections = 0
        
        for section in required_sections:
            if resume.get(section):
                present_sections += 1
        
        return present_sections / len(required_sections)
    
    def _calculate_bullet_quality(self, experience: List[Dict[str, Any]]) -> float:
        """Calculate bullet point quality score"""
        if not experience:
            return 0.0
        
        total_bullets = 0
        quality_bullets = 0
        
        for exp in experience:
            bullets = exp.get("bullet_points", [])
            total_bullets += len(bullets)
            
            for bullet in bullets:
                # Quality criteria: length, contains action verb, contains metric
                if (len(bullet) > 20 and 
                    self._has_action_verb(bullet) and 
                    self._has_metric(bullet)):
                    quality_bullets += 1
        
        return quality_bullets / total_bullets if total_bullets > 0 else 0.0
    
    def _calculate_skill_diversity(self, skills: Dict[str, List[str]]) -> float:
        """Calculate skill diversity score"""
        total_skills = sum(len(skill_list) for skill_list in skills.values())
        unique_categories = sum(1 for skill_list in skills.values() if skill_list)
        
        # Score based on having skills across multiple categories
        if total_skills == 0:
            return 0.0
        
        diversity_score = unique_categories / 3  # Max 3 categories
        volume_score = min(total_skills / 20, 1.0)  # 20+ skills ideal
        
        return (diversity_score + volume_score) / 2
    
    def _calculate_experience_progression(self, experience: List[Dict[str, Any]]) -> float:
        """Calculate career progression score"""
        if len(experience) < 2:
            return 0.0
        
        progression_score = 0.0
        for i in range(1, len(experience)):
            current = experience[i]
            previous = experience[i-1]
            
            # Check for title progression
            if self._is_title_promotion(previous.get("title", ""), current.get("title", "")):
                progression_score += 0.5
            
            # Check for responsibility increase
            if len(current.get("bullet_points", [])) > len(previous.get("bullet_points", [])):
                progression_score += 0.5
        
        return min(progression_score / (len(experience) - 1), 1.0)
    
    def _extract_years_from_dates(self, dates: str) -> float:
        """Extract years of experience from date string"""
        import re
        
        # Look for year patterns
        year_matches = re.findall(r'\b(19|20)\d{2}\b', dates)
        if len(year_matches) >= 2:
            try:
                start_year = int(year_matches[0])
                end_year = int(year_matches[1])
                return end_year - start_year
            except ValueError:
                pass
        
        return 1.0  # Default to 1 year if can't parse
    
    def _has_action_verb(self, bullet: str) -> bool:
        """Check if bullet contains action verb"""
        action_verbs = [
            "developed", "implemented", "designed", "managed", "led",
            "created", "built", "optimized", "improved", "increased",
            "reduced", "achieved", "delivered", "launched", "coordinated"
        ]
        
        bullet_lower = bullet.lower()
        return any(verb in bullet_lower for verb in action_verbs)
    
    def _has_metric(self, bullet: str) -> bool:
        """Check if bullet contains metric"""
        import re
        
        # Look for percentages, dollar amounts, or numbers
        metric_patterns = [
            r'\d+%', r'\$\d+', r'\d+x', r'\d+%', r'\d+%',
            r'decreased by \d+', r'increased by \d+', r'reduced by \d+'
        ]
        
        return any(re.search(pattern, bullet.lower()) for pattern in metric_patterns)
    
    def _is_title_promotion(self, previous_title: str, current_title: str) -> bool:
        """Check if current title represents a promotion"""
        seniority_levels = {
            "junior": 1, "associate": 2, "mid": 3, "senior": 4,
            "lead": 5, "principal": 6, "director": 7, "vp": 8
        }
        
        prev_level = self._get_title_level(previous_title, seniority_levels)
        curr_level = self._get_title_level(current_title, seniority_levels)
        
        return curr_level > prev_level
    
    def _get_title_level(self, title: str, levels: Dict[str, int]) -> int:
        """Get seniority level from title"""
        title_lower = title.lower()
        
        for level_name, level_value in levels.items():
            if level_name in title_lower:
                return level_value
        
        return 3  # Default to mid-level
    
    def execute_quantification(self, 
                              cleaned_resume: Optional[Dict[str, Any]] = None,
                              cleaned_job: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute complete K3 quantification
        
        Args:
            cleaned_resume: Cleaned resume data from K2
            cleaned_job: Cleaned job data from K2
            
        Returns:
            Complete quantification results
        """
        result = {
            "step": "K3_QUANT",
            "status": "completed",
            "quantification_results": {}
        }
        
        if cleaned_resume and cleaned_job:
            result["quantification_results"]["job_alignment"] = self.calculate_job_alignment_score(
                cleaned_resume, cleaned_job
            )
        
        if cleaned_resume:
            result["quantification_results"]["resume_quality"] = self.calculate_resume_quality_metrics(
                cleaned_resume
            )
        
        # Add metadata
        result["metadata"] = {
            "quant_rules_count": len(self.quant_rules),
            "routing_rules_count": len(self.routing_rules),
            "parameters_count": len(self.parameters),
            "quantification_completeness": "full" if cleaned_resume and cleaned_job else "partial"
        }
        
        return result
