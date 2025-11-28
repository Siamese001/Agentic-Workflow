# File: clerk_RES_v3_8.py
# ClerkExtractor class - extracts data from master resume
# Version: 3.8.0 - V3.8 Migration

import logging
from typing import Dict, List, Tuple

from models_RES import BulletProvenance, ValidationResult, ValidationSeverity

logger = logging.getLogger(__name__)


class ClerkExtractor:
    """
    Data extraction service that processes master resume into structured format.
    V3.8 version with enhanced extraction capabilities.
    """

    def __init__(self, master_resume: Dict):
        """
        Initialize the ClerkExtractor.
        
        Args:
            master_resume: Master resume dictionary
        """
        self.master_resume = master_resume
        self._validate_master_resume_structure()

    def extract(self, job_input: Dict = None) -> Tuple[Dict, List[ValidationResult]]:
        """
        Extract structured data from master resume.
        
        Args:
            job_input: Optional job input for context-aware extraction
            
        Returns:
            Tuple of (extracted_data, validation_results)
        """
        validation_results = []

        # Build experience sections
        experience_sections = self._build_experience_sections()

        # Extract all bullets for analysis
        all_bullets = []
        for section in experience_sections:
            all_bullets.extend([bullet['bullet_text'] for bullet in section.get('bullets', [])])

        # Build comprehensive extracted data
        extracted_data = {
            "experience_sections": experience_sections,
            "header": self._extract_header(),
            "education": self._extract_education(),
            "certifications": self._extract_certifications(),
            "skills": self._extract_skills(),
            "achievements": self._extract_achievements(),
            "metadata": {
                "total_experiences": len(experience_sections),
                "total_bullets": len(all_bullets),
                "extraction_timestamp": self._get_timestamp()
            }
        }

        # Validate extraction completeness
        validation_results.extend(self._validate_extraction(extracted_data))

        return extracted_data, validation_results

    def _validate_master_resume_structure(self):
        """Validate that master resume has all required keys."""
        required_keys = [
            "owner", 
            "professional_experience", 
            "education", 
            "certifications_and_credentials", 
            "strategic_and_technical_competencies"
        ]
        
        if not self.master_resume:
            raise ValueError("MASTER_RESUME_JSON is empty or not provided.")

        missing_keys = [key for key in required_keys if key not in self.master_resume]
        if missing_keys:
            raise ValueError(f"MASTER_RESUME_JSON is missing required keys: {', '.join(missing_keys)}")
        
        logger.info("✔ Master resume structure validated.")

    def _build_experience_sections(self) -> List[Dict]:
        """Build experience sections from professional experience data."""
        experience_sections = []

        for exp in self.master_resume.get("professional_experience", []):
            bullets = []
            bullet_source = exp.get("bullet_pool", exp.get("highlights", []))

            for bullet_text in bullet_source:
                bullets.append({
                    "bullet_text": bullet_text,
                    "canonical_verbs": [],  # Will be enriched later
                    "provenance": BulletProvenance.VERBATIM.value,
                    "source_role": exp.get("title", ""),
                    "source_company": exp.get("company", "")
                })

            experience_sections.append({
                "company": exp.get("company", ""),
                "title": exp.get("title", ""),
                "location": exp.get("location", ""),
                "start_date": exp.get("dates", {}).get("start", ""),
                "end_date": exp.get("dates", {}).get("end", ""),
                "overview": exp.get("overview", ""),
                "bullets": bullets,
                "highlights": [bullet['bullet_text'] for bullet in bullets],
                "technologies": exp.get("technologies", []),
                "achievements": exp.get("achievements", [])
            })

        return experience_sections

    def _extract_header(self) -> Dict:
        """Extract header information from master resume."""
        owner = self.master_resume.get("owner", {})
        
        return {
            "name": owner.get("name", ""),
            "title": owner.get("current_title", ""),
            "email": owner.get("email", ""),
            "phone": owner.get("phone", ""),
            "location": owner.get("location", ""),
            "linkedin": owner.get("linkedin", ""),
            "github": owner.get("github", ""),
            "website": owner.get("website", ""),
            "summary": owner.get("summary", ""),
            "headline": owner.get("headline", "")
        }

    def _extract_education(self) -> List[Dict]:
        """Extract education information."""
        education_list = []
        
        for edu in self.master_resume.get("education", []):
            education_list.append({
                "institution": edu.get("institution", ""),
                "degree": edu.get("degree", ""),
                "field": edu.get("field", ""),
                "graduation_date": edu.get("graduation_date", ""),
                "gpa": edu.get("gpa", ""),
                "honors": edu.get("honors", []),
                "relevant_coursework": edu.get("relevant_coursework", [])
            })
        
        return education_list

    def _extract_certifications(self) -> List[Dict]:
        """Extract certifications and credentials."""
        cert_list = []
        certs = self.master_resume.get("certifications_and_credentials", [])
        
        if isinstance(certs, list):
            for cert in certs:
                if isinstance(cert, dict):
                    cert_list.append({
                        "name": cert.get("name", ""),
                        "issuer": cert.get("issuer", ""),
                        "date": cert.get("date", ""),
                        "expires": cert.get("expires", ""),
                        "credential_id": cert.get("credential_id", "")
                    })
                elif isinstance(cert, str):
                    # Handle simple string certifications
                    cert_list.append({
                        "name": cert,
                        "issuer": "",
                        "date": "",
                        "expires": "",
                        "credential_id": ""
                    })
        
        return cert_list

    def _extract_skills(self) -> Dict[str, List[str]]:
        """Extract skills by category."""
        skills = {}
        skills_data = self.master_resume.get("strategic_and_technical_competencies", {})
        
        for category, skill_list in skills_data.items():
            if isinstance(skill_list, list):
                skills[category] = skill_list
            elif isinstance(skill_list, str):
                # Handle string skills as single-item list
                skills[category] = [skill_list]
        
        return skills

    def _extract_achievements(self) -> List[str]:
        """Extract notable achievements from across the resume."""
        achievements = []
        
        # Extract from dedicated achievements section if exists
        if "achievements" in self.master_resume:
            achv = self.master_resume["achievements"]
            if isinstance(achv, list):
                achievements.extend(achv)
        
        # Extract from experience sections
        for exp in self.master_resume.get("professional_experience", []):
            if "achievements" in exp:
                exp_achv = exp["achievements"]
                if isinstance(exp_achv, list):
                    achievements.extend(exp_achv)
        
        # Deduplicate
        achievements = list(set(achievements))
        
        return achievements

    def _validate_extraction(self, extracted_data: Dict) -> List[ValidationResult]:
        """Validate the completeness of extraction."""
        validation_results = []
        
        # Check experience sections
        exp_sections = extracted_data.get("experience_sections", [])
        if not exp_sections:
            validation_results.append(ValidationResult(
                rule_id="EXTRACTION_NO_EXPERIENCE",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="No experience sections extracted"
            ))
        else:
            validation_results.append(ValidationResult(
                rule_id="EXTRACTION_EXPERIENCE_COUNT",
                passed=True,
                severity=ValidationSeverity.INFO,
                message=f"Successfully extracted {len(exp_sections)} experience sections"
            ))
        
        # Check header completeness
        header = extracted_data.get("header", {})
        required_header_fields = ["name", "email"]
        missing_fields = [f for f in required_header_fields if not header.get(f)]
        
        if missing_fields:
            validation_results.append(ValidationResult(
                rule_id="EXTRACTION_HEADER_INCOMPLETE",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Missing required header fields: {missing_fields}",
                details={"missing_fields": missing_fields}
            ))
        
        # Check education
        education = extracted_data.get("education", [])
        if not education:
            validation_results.append(ValidationResult(
                rule_id="EXTRACTION_NO_EDUCATION",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="No education information extracted"
            ))
        
        # Check skills
        skills = extracted_data.get("skills", {})
        if not skills:
            validation_results.append(ValidationResult(
                rule_id="EXTRACTION_NO_SKILLS",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message="No skills extracted"
            ))
        else:
            total_skills = sum(len(s) for s in skills.values() if isinstance(s, list))
            validation_results.append(ValidationResult(
                rule_id="EXTRACTION_SKILLS_COUNT",
                passed=True,
                severity=ValidationSeverity.INFO,
                message=f"Extracted {total_skills} skills across {len(skills)} categories"
            ))
        
        return validation_results

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


# Backwards compatibility
DataExtractor = ClerkExtractor

__all__ = ['ClerkExtractor', 'DataExtractor']
