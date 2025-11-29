#!/usr/bin/env python3
"""
Skill Mappers
Section 16: RAG Optimization - Data mapping utilities for resume skills
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class SkillMapper:
    """Mapper for resume skill data transformation and normalization"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.skill_categories = self.config.get("skill_categories", {})
        self.proficiency_levels = self.config.get("proficiency_levels", {})
    
    def map_skill_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map raw skill data to standardized format"""
        try:
            mapped_data = {}
            
            # Map basic skill fields
            mapped_data["skill_name"] = raw_data.get("name", "").strip().title()
            mapped_data["skill_category"] = self._normalize_category(raw_data.get("category", ""))
            mapped_data["skill_level"] = self._normalize_proficiency(raw_data.get("level", ""))
            mapped_data["skill_years"] = self._normalize_years_experience(raw_data.get("years", ""))
            
            # Map skill details
            if "description" in raw_data:
                mapped_data["skill_description"] = raw_data["description"].strip()
            
            if "technologies" in raw_data:
                mapped_data["skill_technologies"] = self._normalize_technologies(raw_data["technologies"])
            
            if "certifications" in raw_data:
                mapped_data["skill_certifications"] = self._normalize_certifications(raw_data["certifications"])
            
            # Calculate skill metrics
            mapped_data["skill_metrics"] = self._calculate_skill_metrics(mapped_data)
            
            # Add processing metadata
            mapped_data["_metadata"] = {
                "mapped_at": self._get_timestamp(),
                "mapper_version": "1.0",
                "source_fields": list(raw_data.keys())
            }
            
            logger.info(f"Successfully mapped skill data: {mapped_data.get('skill_name', 'Unknown')}")
            return mapped_data
            
        except Exception as e:
            logger.error(f"Skill mapping failed: {e}")
            return {"error": str(e), "original_data": raw_data}
    
    def _normalize_category(self, category: str) -> str:
        """Normalize skill category classification"""
        category_lower = category.lower().strip()
        
        # Apply category mappings
        for key, mapped_value in self.skill_categories.items():
            if key.lower() in category_lower:
                return mapped_value
        
        # Default category normalization
        category_synonyms = {
            "programming": "Programming",
            "software": "Software Development",
            "development": "Software Development",
            "technical": "Technical Skills",
            "soft": "Soft Skills",
            "communication": "Communication",
            "leadership": "Leadership",
            "management": "Management",
            "analytical": "Analytical Skills",
            "design": "Design",
            "database": "Database",
            "cloud": "Cloud Computing",
            "security": "Security",
            "testing": "Testing",
            "devops": "DevOps"
        }
        
        for synonym, standard in category_synonyms.items():
            if synonym in category_lower:
                return standard
        
        return category.title()
    
    def _normalize_proficiency(self, level: str) -> str:
        """Normalize proficiency level"""
        level_lower = level.lower().strip()
        
        # Apply proficiency mappings
        for key, mapped_value in self.proficiency_levels.items():
            if key.lower() in level_lower:
                return mapped_value
        
        # Default proficiency normalization
        proficiency_synonyms = {
            "beginner": "Beginner",
            "novice": "Beginner",
            "junior": "Junior",
            "intermediate": "Intermediate",
            "mid": "Intermediate",
            "senior": "Senior",
            "advanced": "Advanced",
            "expert": "Expert",
            "master": "Expert"
        }
        
        for synonym, standard in proficiency_synonyms.items():
            if synonym in level_lower:
                return standard
        
        return level.title()
    
    def _normalize_years_experience(self, years: str) -> float:
        """Extract years of experience as float"""
        if isinstance(years, (int, float)):
            return float(years)
        
        if isinstance(years, str):
            # Extract numeric value from string
            import re
            numbers = re.findall(r'\d+\.?\d*', years)
            if numbers:
                return float(numbers[0])
        
        return 0.0
    
    def _normalize_technologies(self, technologies: List[str]) -> List[str]:
        """Normalize technology names"""
        normalized = []
        for tech in technologies:
            if isinstance(tech, str):
                normalized.append(tech.strip().title())
        return list(set(normalized))  # Remove duplicates
    
    def _normalize_certifications(self, certifications: List[str]) -> List[Dict[str, str]]:
        """Normalize certification information"""
        normalized = []
        for cert in certifications:
            if isinstance(cert, str):
                normalized.append({
                    "name": cert.strip(),
                    "issuer": "Unknown",  # Would need parsing logic
                    "date": "Unknown"
                })
            elif isinstance(cert, dict):
                normalized.append({
                    "name": cert.get("name", "").strip(),
                    "issuer": cert.get("issuer", "Unknown").strip(),
                    "date": cert.get("date", "Unknown").strip()
                })
        return normalized
    
    def _calculate_skill_metrics(self, skill_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate skill-related metrics"""
        metrics = {
            "category_confidence": self._calculate_category_confidence(skill_data),
            "level_confidence": self._calculate_level_confidence(skill_data),
            "experience_weight": self._calculate_experience_weight(skill_data),
            "technology_count": len(skill_data.get("skill_technologies", [])),
            "certification_count": len(skill_data.get("skill_certifications", []))
        }
        
        return metrics
    
    def _calculate_category_confidence(self, skill_data: Dict[str, Any]) -> float:
        """Calculate confidence score for skill categorization"""
        category = skill_data.get("skill_category", "")
        
        # High confidence for standard categories
        standard_categories = [
            "Programming", "Software Development", "Technical Skills",
            "Communication", "Leadership", "Management", "Analytical Skills"
        ]
        
        if category in standard_categories:
            return 0.9
        elif category:
            return 0.7
        else:
            return 0.3
    
    def _calculate_level_confidence(self, skill_data: Dict[str, Any]) -> float:
        """Calculate confidence score for proficiency level"""
        level = skill_data.get("skill_level", "")
        
        # High confidence for standard levels
        standard_levels = ["Beginner", "Junior", "Intermediate", "Senior", "Advanced", "Expert"]
        
        if level in standard_levels:
            return 0.9
        elif level:
            return 0.6
        else:
            return 0.2
    
    def _calculate_experience_weight(self, skill_data: Dict[str, Any]) -> float:
        """Calculate weight based on years of experience"""
        years = skill_data.get("skill_years", 0.0)
        
        # Simple weighting function
        if years >= 10:
            return 1.0
        elif years >= 5:
            return 0.8
        elif years >= 3:
            return 0.6
        elif years >= 1:
            return 0.4
        else:
            return 0.2
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import time
        return str(int(time.time()))
    
    def batch_map_skills(self, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map multiple skills in batch"""
        results = []
        for skill in skills:
            mapped = self.map_skill_data(skill)
            results.append(mapped)
        
        logger.info(f"Batch mapped {len(skills)} skills")
        return results
    
    def validate_mapped_skill(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mapped skill data"""
        if "error" in mapped_data:
            return {"valid": False, "errors": [mapped_data["error"]]}
        
        required_fields = ["skill_name"]
        missing_fields = [field for field in required_fields if not mapped_data.get(field)]
        
        if missing_fields:
            return {"valid": False, "errors": [f"Missing required fields: {missing_fields}"]}
        
        # Validate skill name length
        skill_name = mapped_data.get("skill_name", "")
        if len(skill_name) < 2:
            return {"valid": False, "errors": ["Skill name too short"]}
        elif len(skill_name) > 100:
            return {"valid": False, "errors": ["Skill name too long"]}
        
        return {"valid": True, "errors": []}

def map_skill_data(raw_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to map skill data"""
    mapper = SkillMapper(config)
    return mapper.map_skill_data(raw_data)

# Re-export components
__all__ = [
    'SkillMapper', 'map_skill_data'
]
