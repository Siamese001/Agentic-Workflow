#!/usr/bin/env python3
"""
L2 Execution Layer - K1 Extract
Atomic extraction of resume data and job requirements
"""

from typing import Dict, Any, Optional, List
# RG_capabilities is now at root level - no sys.path manipulation needed
from RG_capabilities.rg_atomic_spec import ATOMIC_RG_SPEC

class K1Extractor:
    """K1 Extract - Atomic data extraction from master resume and job description"""
    
    def __init__(self):
        self.routing_rules = ATOMIC_RG_SPEC.get("routing", {})
        self.job_workflow_rules = ATOMIC_RG_SPEC.get("job_workflow", {})
        self.parameters = ATOMIC_RG_SPEC.get("parameters", {})
    
    def extract_master_resume_data(self, master_resume: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from master resume
        
        Args:
            master_resume: Raw master resume data
            
        Returns:
            Structured extracted data
        """
        extracted = {
            "contact_info": self._extract_contact_info(master_resume),
            "professional_experience": self._extract_experience(master_resume),
            "education": self._extract_education(master_resume),
            "skills": self._extract_skills(master_resume),
            "certifications": self._extract_certifications(master_resume),
            "metadata": {
                "extraction_timestamp": "2025-01-01T00:00:00Z",
                "source_format": "json",
                "extraction_rules_applied": list(self.routing_rules.keys())[:5]
            }
        }
        return extracted
    
    def extract_job_requirements(self, job_description: str) -> Dict[str, Any]:
        """
        Extract structured requirements from job description
        
        Args:
            job_description: Raw job description text
            
        Returns:
            Structured job requirements
        """
        requirements = {
            "required_skills": self._extract_required_skills(job_description),
            "experience_level": self._extract_experience_level(job_description),
            "key_responsibilities": self._extract_responsibilities(job_description),
            "qualifications": self._extract_qualifications(job_description),
            "metadata": {
                "extraction_timestamp": "2025-01-01T00:00:00Z",
                "job_description_length": len(job_description),
                "extraction_rules_applied": list(self.job_workflow_rules.keys())[:5]
            }
        }
        return requirements
    
    def _extract_contact_info(self, resume: Dict[str, Any]) -> Dict[str, Any]:
        """Extract contact information from resume"""
        contact = resume.get("contact", {})
        return {
            "name": contact.get("name", ""),
            "email": contact.get("email", ""),
            "phone": contact.get("phone", ""),
            "location": contact.get("location", ""),
            "linkedin": contact.get("linkedin", "")
        }
    
    def _extract_experience(self, resume: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract professional experience from resume"""
        experience = resume.get("professional_experience", [])
        extracted_experience = []
        
        for exp in experience:
            extracted_exp = {
                "company": exp.get("company", ""),
                "title": exp.get("title", ""),
                "location": exp.get("location", ""),
                "dates": exp.get("dates", ""),
                "bullet_points": exp.get("bullet_pool", [])[:10],  # Limit bullets
                "technologies": exp.get("technologies", [])
            }
            extracted_experience.append(extracted_exp)
        
        return extracted_experience
    
    def _extract_education(self, resume: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract education information from resume"""
        education = resume.get("education", [])
        extracted_education = []
        
        for edu in education:
            extracted_edu = {
                "degree": edu.get("degree", ""),
                "institution": edu.get("institution", ""),
                "graduation_year": edu.get("graduation_year", ""),
                "field_of_study": edu.get("field_of_study", "")
            }
            extracted_education.append(extracted_edu)
        
        return extracted_education
    
    def _extract_skills(self, resume: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract skills from resume"""
        skills = resume.get("strategic_and_technical_competencies", {})
        return {
            "technical_skills": skills.get("technical", []),
            "soft_skills": skills.get("soft", []),
            "domain_skills": skills.get("domain", [])
        }
    
    def _extract_certifications(self, resume: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract certifications from resume"""
        certifications = resume.get("certifications_and_credentials", [])
        extracted_certs = []
        
        for cert in certifications:
            extracted_cert = {
                "name": cert.get("name", ""),
                "issuer": cert.get("issuer", ""),
                "date_obtained": cert.get("date_obtained", ""),
                "expiry_date": cert.get("expiry_date", "")
            }
            extracted_certs.append(extracted_cert)
        
        return extracted_certs
    
    def _extract_required_skills(self, job_description: str) -> List[str]:
        """Extract required skills from job description"""
        # Simple keyword extraction - in real implementation would use NLP
        skill_keywords = ["python", "java", "javascript", "sql", "aws", "docker", "kubernetes"]
        found_skills = []
        
        for skill in skill_keywords:
            if skill.lower() in job_description.lower():
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_experience_level(self, job_description: str) -> str:
        """Extract experience level from job description"""
        job_desc_lower = job_description.lower()
        
        if any(term in job_desc_lower for term in ["senior", "sr.", "lead", "principal"]):
            return "senior"
        elif any(term in job_desc_lower for term in ["junior", "jr.", "entry", "associate"]):
            return "junior"
        else:
            return "mid"
    
    def _extract_responsibilities(self, job_description: str) -> List[str]:
        """Extract key responsibilities from job description"""
        # Simple sentence extraction - in real implementation would be more sophisticated
        sentences = job_description.split('.')
        responsibilities = []
        
        for sentence in sentences[:10]:  # Limit to first 10 sentences
            sentence = sentence.strip()
            if len(sentence) > 20 and any(keyword in sentence.lower() for keyword in ["responsible", "develop", "design", "implement", "manage"]):
                responsibilities.append(sentence)
        
        return responsibilities
    
    def _extract_qualifications(self, job_description: str) -> List[str]:
        """Extract qualifications from job description"""
        qualifications = []
        job_desc_lower = job_description.lower()
        
        qualification_keywords = ["bachelor", "master", "phd", "degree", "certified", "license"]
        for keyword in qualification_keywords:
            if keyword in job_desc_lower:
                qualifications.append(keyword)
        
        return qualifications
    
    def execute_extraction(self, 
                          master_resume: Optional[Dict[str, Any]] = None,
                          job_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute complete K1 extraction
        
        Args:
            master_resume: Source master resume
            job_description: Target job description
            
        Returns:
            Complete extraction results
        """
        result: Dict[str, Any] = {
            "step": "K1_EXTRACT",
            "status": "completed",
            "extracted_data": {}
        }
        
        if master_resume:
            result["extracted_data"]["resume"] = self.extract_master_resume_data(master_resume)
        
        if job_description:
            result["extracted_data"]["job"] = self.extract_job_requirements(job_description)
        
        # Add metadata
        result["metadata"] = {
            "routing_rules_count": len(self.routing_rules),
            "job_workflow_rules_count": len(self.job_workflow_rules),
            "parameters_count": len(self.parameters),
            "extraction_completeness": "full" if master_resume and job_description else "partial"
        }
        
        return result
