#!/usr/bin/env python3
"""
Education Mappers
Section 16: RAG Optimization - Data mapping utilities for resume education
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class EducationMapper:
    """Mapper for resume education data transformation and normalization"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.institution_mappings = self.config.get("institution_mappings", {})
        self.degree_mappings = self.config.get("degree_mappings", {})
    
    def map_education_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map raw education data to standardized format"""
        try:
            mapped_data = {}
            
            # Map basic education fields
            mapped_data["institution_name"] = raw_data.get("institution", "").strip()
            mapped_data["degree_type"] = self._normalize_degree_type(raw_data.get("degree", ""))
            mapped_data["field_of_study"] = raw_data.get("field", "").strip().title()
            mapped_data["start_date"] = self._normalize_date(raw_data.get("start_date", ""))
            mapped_data["end_date"] = self._normalize_date(raw_data.get("end_date", ""))
            mapped_data["location"] = raw_data.get("location", "").strip()
            
            # Map GPA and academic achievements
            if "gpa" in raw_data:
                mapped_data["gpa"] = self._normalize_gpa(raw_data["gpa"])
            
            if "honors" in raw_data:
                mapped_data["academic_honors"] = self._normalize_honors(raw_data["honors"])
            
            # Map coursework
            if "coursework" in raw_data:
                mapped_data["relevant_coursework"] = self._normalize_coursework(raw_data["coursework"])
            
            # Map activities
            if "activities" in raw_data:
                mapped_data["extracurricular_activities"] = self._normalize_activities(raw_data["activities"])
            
            # Calculate education metrics
            mapped_data["education_metrics"] = self._calculate_education_metrics(mapped_data)
            
            # Add processing metadata
            mapped_data["_metadata"] = {
                "mapped_at": self._get_timestamp(),
                "mapper_version": "1.0",
                "source_fields": list(raw_data.keys())
            }
            
            logger.info(f"Successfully mapped education data: {mapped_data.get('degree_type', 'Unknown')} in {mapped_data.get('field_of_study', 'Unknown')}")
            return mapped_data
            
        except Exception as e:
            logger.error(f"Education mapping failed: {e}")
            return {"error": str(e), "original_data": raw_data}
    
    def _normalize_degree_type(self, degree: str) -> str:
        """Normalize degree type classification"""
        degree_lower = degree.lower().strip()
        
        # Apply degree mappings
        for key, mapped_value in self.degree_mappings.items():
            if key.lower() in degree_lower:
                return mapped_value
        
        # Default degree normalization
        degree_synonyms = {
            "bachelor": "Bachelor's Degree",
            "b.s.": "Bachelor of Science",
            "b.a.": "Bachelor of Arts",
            "master": "Master's Degree",
            "m.s.": "Master of Science",
            "m.a.": "Master of Arts",
            "mba": "Master of Business Administration",
            "phd": "Doctor of Philosophy",
            "ph.d.": "Doctor of Philosophy",
            "doctorate": "Doctorate",
            "associate": "Associate's Degree",
            "certificate": "Certificate",
            "diploma": "Diploma"
        }
        
        for synonym, standard in degree_synonyms.items():
            if synonym in degree_lower:
                return standard
        
        return degree.title()
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date format"""
        if not date_str:
            return ""
        
        date_str = date_str.strip()
        
        # Handle common date formats
        if len(date_str) == 4 and date_str.isdigit():
            return date_str  # Year only
        elif len(date_str) >= 6:
            return date_str  # Assume already in good format
        
        return date_str
    
    def _normalize_gpa(self, gpa: str) -> Dict[str, Any]:
        """Normalize GPA information"""
        if isinstance(gpa, (int, float)):
            return {
                "value": float(gpa),
                "scale": "4.0",
                "formatted": f"{gpa:.2f}/4.0"
            }
        
        if isinstance(gpa, str):
            # Extract numeric value
            import re
            numbers = re.findall(r'\d+\.?\d*', gpa)
            if numbers:
                value = float(numbers[0])
                # Determine scale
                if value > 4.0:
                    scale = "5.0"
                else:
                    scale = "4.0"
                
                return {
                    "value": value,
                    "scale": scale,
                    "formatted": f"{value:.2f}/{scale}"
                }
        
        return {"value": 0.0, "scale": "4.0", "formatted": "N/A"}
    
    def _normalize_honors(self, honors: List[str]) -> List[Dict[str, str]]:
        """Normalize academic honors"""
        normalized = []
        for honor in honors:
            if isinstance(honor, str):
                normalized.append({
                    "name": honor.strip(),
                    "type": self._categorize_honor(honor),
                    "year": self._extract_honor_year(honor)
                })
            elif isinstance(honor, dict):
                normalized.append({
                    "name": honor.get("name", "").strip(),
                    "type": honor.get("type", self._categorize_honor(honor.get("name", ""))),
                    "year": honor.get("year", self._extract_honor_year(honor.get("name", "")))
                })
        return normalized
    
    def _normalize_coursework(self, coursework: List[str]) -> List[Dict[str, str]]:
        """Normalize relevant coursework"""
        normalized = []
        for course in coursework:
            if isinstance(course, str):
                normalized.append({
                    "name": course.strip().title(),
                    "category": self._categorize_course(course),
                    "level": self._assess_course_level(course)
                })
            elif isinstance(course, dict):
                normalized.append({
                    "name": course.get("name", "").strip().title(),
                    "category": course.get("category", self._categorize_course(course.get("name", ""))),
                    "level": course.get("level", self._assess_course_level(course.get("name", "")))
                })
        return normalized
    
    def _normalize_activities(self, activities: List[str]) -> List[Dict[str, str]]:
        """Normalize extracurricular activities"""
        normalized = []
        for activity in activities:
            if isinstance(activity, str):
                normalized.append({
                    "name": activity.strip(),
                    "type": self._categorize_activity(activity),
                    "role": self._extract_role(activity)
                })
            elif isinstance(activity, dict):
                normalized.append({
                    "name": activity.get("name", "").strip(),
                    "type": activity.get("type", self._categorize_activity(activity.get("name", ""))),
                    "role": activity.get("role", self._extract_role(activity.get("name", "")))
                })
        return normalized
    
    def _categorize_honor(self, honor: str) -> str:
        """Categorize academic honor"""
        honor_lower = honor.lower()
        
        if "dean" in honor_lower:
            return "Dean's List"
        elif "president" in honor_lower:
            return "President's List"
        elif "scholarship" in honor_lower:
            return "Scholarship"
        elif "award" in honor_lower:
            return "Award"
        elif "honor" in honor_lower:
            return "Honor Society"
        else:
            return "Academic Recognition"
    
    def _extract_honor_year(self, honor: str) -> str:
        """Extract year from honor"""
        import re
        years = re.findall(r'\b(19|20)\d{2}\b', honor)
        return years[0] if years else ""
    
    def _categorize_course(self, course: str) -> str:
        """Categorize course by subject area"""
        course_lower = course.lower()
        
        categories = {
            "Computer Science": ["computer", "programming", "algorithm", "data structure", "software"],
            "Mathematics": ["math", "calculus", "statistics", "linear", "algebra"],
            "Business": ["business", "finance", "accounting", "marketing", "management"],
            "Science": ["physics", "chemistry", "biology", "science"],
            "Engineering": ["engineering", "mechanical", "electrical", "civil"],
            "Liberal Arts": ["literature", "history", "philosophy", "writing"],
            "Social Sciences": ["psychology", "sociology", "economics", "political"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in course_lower for keyword in keywords):
                return category
        
        return "General"
    
    def _assess_course_level(self, course: str) -> str:
        """Assess course level"""
        course_lower = course.lower()
        
        if any(indicator in course_lower for indicator in ["intro", "basic", "fundamental", "101"]):
            return "Introductory"
        elif any(indicator in course_lower for indicator in ["advanced", "graduate", "500", "600"]):
            return "Advanced"
        else:
            return "Intermediate"
    
    def _categorize_activity(self, activity: str) -> str:
        """Categorize extracurricular activity"""
        activity_lower = activity.lower()
        
        if "club" in activity_lower:
            return "Student Club"
        elif "sport" in activity_lower or "team" in activity_lower:
            return "Sports"
        elif "volunteer" in activity_lower:
            return "Volunteer Work"
        elif "leadership" in activity_lower or "president" in activity_lower or "treasurer" in activity_lower:
            return "Leadership"
        else:
            return "Student Organization"
    
    def _extract_role(self, activity: str) -> str:
        """Extract role from activity description"""
        activity_lower = activity.lower()
        
        roles = ["president", "vice president", "treasurer", "secretary", "captain", "leader", "member"]
        
        for role in roles:
            if role in activity_lower:
                return role.title()
        
        return "Member"
    
    def _calculate_education_metrics(self, education_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate education-related metrics"""
        metrics = {
            "duration_years": self._calculate_duration(education_data),
            "honor_count": len(education_data.get("academic_honors", [])),
            "course_count": len(education_data.get("relevant_coursework", [])),
            "activity_count": len(education_data.get("extracurricular_activities", [])),
            "has_gpa": bool(education_data.get("gpa", {}).get("value", 0)),
            "education_level": self._assess_education_level(education_data)
        }
        
        return metrics
    
    def _calculate_duration(self, education_data: Dict[str, Any]) -> int:
        """Calculate education duration in years"""
        start_date = education_data.get("start_date", "")
        end_date = education_data.get("end_date", "")
        
        if not start_date:
            return 0
        
        try:
            start_year = int(start_date.split()[-1]) if start_date.split()[-1].isdigit() else 0
            
            if end_date:
                end_year = int(end_date.split()[-1]) if end_date.split()[-1].isdigit() else start_year
            else:
                import datetime
                end_year = datetime.datetime.now().year
            
            return max(0, end_year - start_year)
        except Exception:
            return 0
    
    def _assess_education_level(self, education_data: Dict[str, Any]) -> str:
        """Assess education level"""
        degree_type = education_data.get("degree_type", "").lower()
        
        if "doctor" in degree_type or "phd" in degree_type:
            return "Doctoral"
        elif "master" in degree_type or "mba" in degree_type:
            return "Graduate"
        elif "bachelor" in degree_type:
            return "Undergraduate"
        elif "associate" in degree_type:
            return "Associate"
        else:
            return "Other"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import time
        return str(int(time.time()))
    
    def batch_map_education(self, education_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map multiple education entries in batch"""
        results = []
        for education in education_list:
            mapped = self.map_education_data(education)
            results.append(mapped)
        
        logger.info(f"Batch mapped {len(education_list)} education entries")
        return results
    
    def validate_mapped_education(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mapped education data"""
        if "error" in mapped_data:
            return {"valid": False, "errors": [mapped_data["error"]]}
        
        required_fields = ["institution_name", "degree_type"]
        missing_fields = [field for field in required_fields if not mapped_data.get(field)]
        
        if missing_fields:
            return {"valid": False, "errors": [f"Missing required fields: {missing_fields}"]}
        
        return {"valid": True, "errors": []}

def map_education_data(raw_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to map education data"""
    mapper = EducationMapper(config)
    return mapper.map_education_data(raw_data)

# Re-export components
__all__ = [
    'EducationMapper', 'map_education_data'
]
