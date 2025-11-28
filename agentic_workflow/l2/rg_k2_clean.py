#!/usr/bin/env python3
"""
L2 Execution Layer - K2 Clean
Atomic data cleaning and preprocessing
"""

from typing import Dict, Any, List, Optional
import sys
sys.path.append(r'C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\agentic_workflow\RG_capabilities')
from rg_atomic_spec import ATOMIC_RG_SPEC

class K2Cleaner:
    """K2 Clean - Atomic data cleaning and preprocessing"""
    
    def __init__(self):
        self.routing_rules = ATOMIC_RG_SPEC.get("routing", {})
        self.parameters = ATOMIC_RG_SPEC.get("parameters", {})
        self.formatting_rules = ATOMIC_RG_SPEC.get("formatting", {})
    
    def clean_resume_data(self, extracted_resume: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize extracted resume data
        
        Args:
            extracted_resume: Raw extracted resume data from K1
            
        Returns:
            Cleaned and normalized resume data
        """
        cleaned = {
            "contact_info": self._clean_contact_info(extracted_resume.get("contact_info", {})),
            "professional_experience": self._clean_experience(extracted_resume.get("professional_experience", [])),
            "education": self._clean_education(extracted_resume.get("education", [])),
            "skills": self._clean_skills(extracted_resume.get("skills", {})),
            "certifications": self._clean_certifications(extracted_resume.get("certifications", [])),
            "metadata": {
                "cleaning_timestamp": "2025-01-01T00:00:00Z",
                "cleaning_rules_applied": list(self.formatting_rules.keys())[:3],
                "data_quality_score": self._calculate_data_quality(extracted_resume)
            }
        }
        return cleaned
    
    def clean_job_data(self, extracted_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize extracted job data
        
        Args:
            extracted_job: Raw extracted job data from K1
            
        Returns:
            Cleaned and normalized job data
        """
        cleaned = {
            "required_skills": self._normalize_skills(extracted_job.get("required_skills", [])),
            "experience_level": self._normalize_experience_level(extracted_job.get("experience_level", "")),
            "key_responsibilities": self._clean_responsibilities(extracted_job.get("key_responsibilities", [])),
            "qualifications": self._normalize_qualifications(extracted_job.get("qualifications", [])),
            "metadata": {
                "cleaning_timestamp": "2025-01-01T00:00:00Z",
                "cleaning_rules_applied": list(self.formatting_rules.keys())[:3],
                "data_completeness_score": self._calculate_completeness(extracted_job)
            }
        }
        return cleaned
    
    def _clean_contact_info(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize contact information"""
        return {
            "name": contact.get("name", "").strip().title(),
            "email": contact.get("email", "").strip().lower(),
            "phone": self._clean_phone_number(contact.get("phone", "")),
            "location": contact.get("location", "").strip().title(),
            "linkedin": self._clean_linkedin_url(contact.get("linkedin", ""))
        }
    
    def _clean_experience(self, experience: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and normalize professional experience"""
        cleaned_experience = []
        
        for exp in experience:
            cleaned_exp = {
                "company": exp.get("company", "").strip().title(),
                "title": exp.get("title", "").strip().title(),
                "location": exp.get("location", "").strip().title(),
                "dates": exp.get("dates", "").strip(),
                "bullet_points": self._clean_bullet_points(exp.get("bullet_points", [])),
                "technologies": self._normalize_technologies(exp.get("technologies", []))
            }
            cleaned_experience.append(cleaned_exp)
        
        return cleaned_experience
    
    def _clean_education(self, education: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and normalize education information"""
        cleaned_education = []
        
        for edu in education:
            cleaned_edu = {
                "degree": edu.get("degree", "").strip().title(),
                "institution": edu.get("institution", "").strip().title(),
                "graduation_year": self._clean_year(edu.get("graduation_year", "")),
                "field_of_study": edu.get("field_of_study", "").strip().title()
            }
            cleaned_education.append(cleaned_edu)
        
        return cleaned_education
    
    def _clean_skills(self, skills: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Clean and normalize skills"""
        return {
            "technical_skills": self._normalize_skills(skills.get("technical_skills", [])),
            "soft_skills": self._normalize_skills(skills.get("soft_skills", [])),
            "domain_skills": self._normalize_skills(skills.get("domain_skills", []))
        }
    
    def _clean_certifications(self, certifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and normalize certifications"""
        cleaned_certs = []
        
        for cert in certifications:
            cleaned_cert = {
                "name": cert.get("name", "").strip().title(),
                "issuer": cert.get("issuer", "").strip().title(),
                "date_obtained": self._clean_date(cert.get("date_obtained", "")),
                "expiry_date": self._clean_date(cert.get("expiry_date", ""))
            }
            cleaned_certs.append(cleaned_cert)
        
        return cleaned_certs
    
    def _clean_phone_number(self, phone: str) -> str:
        """Clean and normalize phone number"""
        # Remove all non-digit characters
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Format as (XXX) XXX-XXXX if 10 digits
        if len(digits_only) == 10:
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        
        return phone.strip()
    
    def _clean_linkedin_url(self, linkedin: str) -> str:
        """Clean and normalize LinkedIn URL"""
        linkedin = linkedin.strip()
        if not linkedin:
            return ""
        
        # Add https:// if missing
        if not linkedin.startswith(("http://", "https://")):
            linkedin = "https://" + linkedin
        
        return linkedin
    
    def _clean_bullet_points(self, bullets: List[str]) -> List[str]:
        """Clean and normalize bullet points"""
        cleaned_bullets = []
        
        for bullet in bullets:
            # Remove leading bullet characters and clean whitespace
            cleaned = bullet.strip()
            cleaned = cleaned.lstrip("•-–—*")
            cleaned = cleaned.strip()
            
            # Capitalize first letter
            if cleaned:
                cleaned = cleaned[0].upper() + cleaned[1:]
                cleaned_bullets.append(cleaned)
        
        return cleaned_bullets
    
    def _normalize_technologies(self, technologies: List[str]) -> List[str]:
        """Normalize technology names"""
        normalized = []
        
        for tech in technologies:
            # Convert to lowercase and strip
            clean_tech = tech.strip().lower()
            if clean_tech:
                normalized.append(clean_tech)
        
        # Remove duplicates and sort
        return sorted(list(set(normalized)))
    
    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """Normalize skill names"""
        normalized = []
        
        for skill in skills:
            # Convert to title case and strip
            clean_skill = skill.strip().title()
            if clean_skill:
                normalized.append(clean_skill)
        
        # Remove duplicates and sort
        return sorted(list(set(normalized)))
    
    def _clean_year(self, year_str: str) -> str:
        """Clean and normalize year"""
        year_str = year_str.strip()
        
        # Extract 4-digit year
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', year_str)
        if year_match:
            return year_match.group()
        
        return year_str
    
    def _clean_date(self, date_str: str) -> str:
        """Clean and normalize date"""
        date_str = date_str.strip()
        if not date_str:
            return ""
        
        # Basic date format validation
        import re
        if re.match(r'\b(19|20)\d{2}\b', date_str):
            return date_str
        
        return date_str
    
    def _normalize_experience_level(self, level: str) -> str:
        """Normalize experience level"""
        level = level.strip().lower()
        
        if level in ["senior", "sr.", "sr", "lead", "principal"]:
            return "senior"
        elif level in ["junior", "jr.", "jr", "entry", "associate"]:
            return "junior"
        else:
            return "mid"
    
    def _clean_responsibilities(self, responsibilities: List[str]) -> List[str]:
        """Clean and normalize responsibilities"""
        cleaned = []
        
        for resp in responsibilities:
            # Remove leading/trailing whitespace and capitalize
            clean_resp = resp.strip()
            if clean_resp:
                clean_resp = clean_resp[0].upper() + clean_resp[1:]
                cleaned.append(clean_resp)
        
        return cleaned
    
    def _normalize_qualifications(self, qualifications: List[str]) -> List[str]:
        """Normalize qualifications"""
        normalized = []
        
        for qual in qualifications:
            # Convert to title case and strip
            clean_qual = qual.strip().title()
            if clean_qual:
                normalized.append(clean_qual)
        
        # Remove duplicates and sort
        return sorted(list(set(normalized)))
    
    def _calculate_data_quality(self, data: Dict[str, Any]) -> float:
        """Calculate data quality score"""
        score = 0.0
        total_checks = 0
        
        # Check contact info completeness
        contact = data.get("contact_info", {})
        if contact.get("name"):
            score += 1
        total_checks += 1
        
        if contact.get("email"):
            score += 1
        total_checks += 1
        
        # Check experience
        if data.get("professional_experience"):
            score += 1
        total_checks += 1
        
        # Check education
        if data.get("education"):
            score += 1
        total_checks += 1
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _calculate_completeness(self, data: Dict[str, Any]) -> float:
        """Calculate data completeness score"""
        score = 0.0
        total_checks = 0
        
        # Check required sections
        if data.get("required_skills"):
            score += 1
        total_checks += 1
        
        if data.get("experience_level"):
            score += 1
        total_checks += 1
        
        if data.get("key_responsibilities"):
            score += 1
        total_checks += 1
        
        if data.get("qualifications"):
            score += 1
        total_checks += 1
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def execute_cleaning(self, 
                        extracted_resume: Optional[Dict[str, Any]] = None,
                        extracted_job: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute complete K2 cleaning
        
        Args:
            extracted_resume: Raw extracted resume data from K1
            extracted_job: Raw extracted job data from K1
            
        Returns:
            Complete cleaning results
        """
        result = {
            "step": "K2_CLEAN",
            "status": "completed",
            "cleaned_data": {}
        }
        
        if extracted_resume:
            result["cleaned_data"]["resume"] = self.clean_resume_data(extracted_resume)
        
        if extracted_job:
            result["cleaned_data"]["job"] = self.clean_job_data(extracted_job)
        
        # Add metadata
        result["metadata"] = {
            "routing_rules_count": len(self.routing_rules),
            "parameters_count": len(self.parameters),
            "formatting_rules_count": len(self.formatting_rules),
            "cleaning_completeness": "full" if extracted_resume and extracted_job else "partial"
        }
        
        return result
