#!/usr/bin/env python3
"""
Experience Mappers
Section 16: RAG Optimization - Data mapping utilities for resume work experience
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class ExperienceMapper:
    """Mapper for resume work experience data transformation and normalization"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.company_mappings = self.config.get("company_mappings", {})
        self.role_mappings = self.config.get("role_mappings", {})
    
    def map_experience_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map raw work experience data to standardized format"""
        try:
            mapped_data = {}
            
            # Map basic experience fields
            mapped_data["company_name"] = raw_data.get("company", "").strip()
            mapped_data["job_title"] = raw_data.get("title", "").strip().title()
            mapped_data["start_date"] = self._normalize_date(raw_data.get("start_date", ""))
            mapped_data["end_date"] = self._normalize_date(raw_data.get("end_date", "present"))
            mapped_data["location"] = raw_data.get("location", "").strip()
            
            # Map job description
            if "description" in raw_data:
                mapped_data["job_description"] = raw_data["description"].strip()
            
            # Map responsibilities
            if "responsibilities" in raw_data:
                mapped_data["job_responsibilities"] = self._normalize_responsibilities(raw_data["responsibilities"])
            
            # Map achievements
            if "achievements" in raw_data:
                mapped_data["job_achievements"] = self._normalize_achievements(raw_data["achievements"])
            
            # Map skills used
            if "skills" in raw_data:
                mapped_data["skills_used"] = self._normalize_skills(raw_data["skills"])
            
            # Calculate experience metrics
            mapped_data["experience_metrics"] = self._calculate_experience_metrics(mapped_data)
            
            # Add processing metadata
            mapped_data["_metadata"] = {
                "mapped_at": self._get_timestamp(),
                "mapper_version": "1.0",
                "source_fields": list(raw_data.keys())
            }
            
            logger.info(f"Successfully mapped experience data: {mapped_data.get('job_title', 'Unknown')} at {mapped_data.get('company_name', 'Unknown')}")
            return mapped_data
            
        except Exception as e:
            logger.error(f"Experience mapping failed: {e}")
            return {"error": str(e), "original_data": raw_data}
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date format"""
        if not date_str or date_str.lower() == "present":
            return "Present"
        
        # Simple date normalization - in production would use proper date parsing
        date_str = date_str.strip()
        
        # Handle common date formats
        if len(date_str) == 4 and date_str.isdigit():
            return date_str  # Year only
        elif len(date_str) >= 6:
            return date_str  # Assume already in good format
        
        return date_str
    
    def _normalize_responsibilities(self, responsibilities: List[str]) -> List[str]:
        """Normalize job responsibilities"""
        normalized = []
        for resp in responsibilities:
            if isinstance(resp, str):
                # Clean up responsibility text
                cleaned = resp.strip()
                if cleaned and not cleaned.startswith("•"):
                    cleaned = f"• {cleaned}"
                normalized.append(cleaned)
        return normalized
    
    def _normalize_achievements(self, achievements: List[str]) -> List[Dict[str, str]]:
        """Normalize job achievements"""
        normalized = []
        for achievement in achievements:
            if isinstance(achievement, str):
                normalized.append({
                    "description": achievement.strip(),
                    "metric": self._extract_metric(achievement),
                    "impact": self._assess_impact(achievement)
                })
            elif isinstance(achievement, dict):
                normalized.append({
                    "description": achievement.get("description", "").strip(),
                    "metric": achievement.get("metric", ""),
                    "impact": achievement.get("impact", "")
                })
        return normalized
    
    def _normalize_skills(self, skills: List[str]) -> List[Dict[str, str]]:
        """Normalize skills used in experience"""
        normalized = []
        for skill in skills:
            if isinstance(skill, str):
                normalized.append({
                    "name": skill.strip().title(),
                    "category": self._categorize_skill(skill),
                    "proficiency": "Applied"  # Default for experience-based skills
                })
            elif isinstance(skill, dict):
                normalized.append({
                    "name": skill.get("name", "").strip().title(),
                    "category": skill.get("category", self._categorize_skill(skill.get("name", ""))),
                    "proficiency": skill.get("proficiency", "Applied")
                })
        return normalized
    
    def _extract_metric(self, achievement: str) -> str:
        """Extract quantitative metrics from achievement"""
        import re
        
        # Look for percentages, numbers, and metrics
        patterns = [
            r'\d+%',  # Percentage
            r'\$\d+',  # Dollar amount
            r'\d+x',  # Multiplier
            r'\d+',   # General number
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, achievement)
            if matches:
                return matches[0]
        
        return ""
    
    def _assess_impact(self, achievement: str) -> str:
        """Assess impact level of achievement"""
        achievement_lower = achievement.lower()
        
        high_impact_indicators = ["increased", "reduced", "improved", "saved", "generated", "achieved"]
        medium_impact_indicators = ["managed", "led", "coordinated", "developed", "implemented"]
        
        if any(indicator in achievement_lower for indicator in high_impact_indicators):
            return "High"
        elif any(indicator in achievement_lower for indicator in medium_impact_indicators):
            return "Medium"
        else:
            return "Standard"
    
    def _categorize_skill(self, skill: str) -> str:
        """Categorize skill based on name"""
        skill_lower = skill.lower()
        
        categories = {
            "Technical": ["python", "java", "javascript", "sql", "aws", "docker", "kubernetes"],
            "Leadership": ["led", "managed", "supervised", "coordinated", "mentored"],
            "Communication": ["presented", "wrote", "communicated", "negotiated"],
            "Analytical": ["analyzed", "researched", "investigated", "evaluated"],
            "Project Management": ["project", "timeline", "budget", "milestone", "deliverable"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in skill_lower for keyword in keywords):
                return category
        
        return "General"
    
    def _calculate_experience_metrics(self, experience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate experience-related metrics"""
        metrics = {
            "duration_months": self._calculate_duration(experience_data),
            "responsibility_count": len(experience_data.get("job_responsibilities", [])),
            "achievement_count": len(experience_data.get("job_achievements", [])),
            "skill_count": len(experience_data.get("skills_used", [])),
            "has_metrics": any(ach.get("metric") for ach in experience_data.get("job_achievements", [])),
            "seniority_level": self._assess_seniority_level(experience_data)
        }
        
        return metrics
    
    def _calculate_duration(self, experience_data: Dict[str, Any]) -> int:
        """Calculate duration in months"""
        start_date = experience_data.get("start_date", "")
        end_date = experience_data.get("end_date", "")
        
        if not start_date:
            return 0
        
        # Simple calculation - in production would use proper date arithmetic
        try:
            start_year = int(start_date.split()[-1]) if start_date.split()[-1].isdigit() else 0
            
            if end_date.lower() == "present":
                import datetime
                current_year = datetime.datetime.now().year
                duration_years = current_year - start_year
            else:
                end_year = int(end_date.split()[-1]) if end_date.split()[-1].isdigit() else start_year
                duration_years = max(0, end_year - start_year)
            
            return duration_years * 12  # Convert to months
        except Exception:
            return 0
    
    def _assess_seniority_level(self, experience_data: Dict[str, Any]) -> str:
        """Assess seniority level based on job title and experience"""
        title = experience_data.get("job_title", "").lower()
        duration = self._calculate_duration(experience_data)
        
        # Seniority by title
        senior_keywords = ["senior", "lead", "principal", "architect", "manager", "director"]
        junior_keywords = ["junior", "associate", "intern", "assistant"]
        
        if any(keyword in title for keyword in senior_keywords):
            return "Senior"
        elif any(keyword in title for keyword in junior_keywords):
            return "Junior"
        elif duration >= 60:  # 5+ years
            return "Senior"
        elif duration >= 24:  # 2+ years
            return "Mid-Level"
        else:
            return "Entry-Level"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import time
        return str(int(time.time()))
    
    def batch_map_experiences(self, experiences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map multiple work experiences in batch"""
        results = []
        for experience in experiences:
            mapped = self.map_experience_data(experience)
            results.append(mapped)
        
        logger.info(f"Batch mapped {len(experiences)} work experiences")
        return results
    
    def validate_mapped_experience(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mapped work experience data"""
        if "error" in mapped_data:
            return {"valid": False, "errors": [mapped_data["error"]]}
        
        required_fields = ["company_name", "job_title"]
        missing_fields = [field for field in required_fields if not mapped_data.get(field)]
        
        if missing_fields:
            return {"valid": False, "errors": [f"Missing required fields: {missing_fields}"]}
        
        # Validate dates
        start_date = mapped_data.get("start_date", "")
        end_date = mapped_data.get("end_date", "")
        
        if not start_date:
            return {"valid": False, "errors": ["Start date is required"]}
        
        return {"valid": True, "errors": []}

def map_experience_data(raw_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to map work experience data"""
    mapper = ExperienceMapper(config)
    return mapper.map_experience_data(raw_data)

# Re-export components
__all__ = [
    'ExperienceMapper', 'map_experience_data'
]





