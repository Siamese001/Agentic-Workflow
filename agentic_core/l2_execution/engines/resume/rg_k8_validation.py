#!/usr/bin/env python3
"""
L2 Execution Layer - K8 Validation
Atomic validation and quality assurance
"""

from typing import Dict, Any, List, Optional, Tuple
# RG_capabilities is now at root level - no sys.path manipulation needed
from RG_capabilities.rg_atomic_spec import ATOMIC_RG_SPEC

class K8Validator:
    """K8 Validation - Atomic validation and quality assurance"""
    
    def __init__(self):
        self.validators = ATOMIC_RG_SPEC.get("validators", {})
        self.constraints = ATOMIC_RG_SPEC.get("constraints", {})
        self.ats_rules = ATOMIC_RG_SPEC.get("ats", {})
        self.routing_rules = ATOMIC_RG_SPEC.get("routing", {})
    
    def validate_resume_quality(self, 
                               formatted_resume: Dict[str, Any],
                               job_requirements: Dict[str, Any],
                               quant_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate resume quality and completeness
        
        Args:
            formatted_resume: Formatted resume from K7
            job_requirements: Job requirements from K2
            quant_results: Quantification results from K3
            
        Returns:
            Validation results with scores and recommendations
        """
        validation_results = {
            "quality_score": 0.0,
            "validation_checks": {},
            "issues_found": [],
            "recommendations": [],
            "metadata": {
                "validators_applied": list(self.validators.keys())[:5],
                "constraints_checked": list(self.constraints.keys())[:3],
                "validation_timestamp": "2025-01-01T00:00:00Z"
            }
        }
        
        # Perform validation checks
        validation_results["validation_checks"] = {
            "content_completeness": self._validate_content_completeness(formatted_resume),
            "format_consistency": self._validate_format_consistency(formatted_resume),
            "job_alignment": self._validate_job_alignment(formatted_resume, job_requirements),
            "ats_compliance": self._validate_ats_compliance(formatted_resume),
            "constraint_adherence": self._validate_constraint_adherence(formatted_resume)
        }
        
        # Calculate overall quality score
        scores = list(validation_results["validation_checks"].values())
        validation_results["quality_score"] = sum(scores) / len(scores) if scores else 0.0
        
        # Generate issues and recommendations
        validation_results["issues_found"] = self._identify_validation_issues(
            validation_results["validation_checks"]
        )
        validation_results["recommendations"] = self._generate_recommendations(
            validation_results["validation_checks"]
        )
        
        return validation_results
    
    def validate_ats_compliance(self, resume_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate ATS compliance specifically
        
        Args:
            resume_content: Resume content to validate
            
        Returns:
            ATS compliance validation results
        """
        ats_validation = {
            "compliant": True,
            "score": 0.0,
            "issues": [],
            "optimizations": []
        }
        
        # Check for ATS-friendly formatting
        content_text = self._extract_text_content(resume_content)
        
        # ATS checks
        if len(content_text) > 10000:  # Too long for ATS
            ats_validation["issues"].append("Resume too long for ATS parsing")
            ats_validation["compliant"] = False
        
        if not self._has_proper_headings(resume_content):
            ats_validation["issues"].append("Missing proper section headings")
            ats_validation["compliant"] = False
        
        if not self._has_standard_format(resume_content):
            ats_validation["issues"].append("Non-standard formatting detected")
        
        # Calculate ATS score
        ats_validation["score"] = 0.9 if ats_validation["compliant"] else 0.6
        
        return ats_validation
    
    def validate_content_truthfulness(self, resume_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate content truthfulness and detect potential issues
        
        Args:
            resume_content: Resume content to validate
            
        Returns:
            Truthfulness validation results
        """
        truthfulness = {
            "score": 0.0,
            "warnings": [],
            "flagged_content": []
        }
        
        # Check for common truthfulness issues
        content_text = self._extract_text_content(resume_content)
        
        # Look for potentially exaggerated claims
        exaggerated_patterns = [
            "world's best", "revolutionized", "single-handedly",
            "perfect", "never failed", "always successful"
        ]
        
        for pattern in exaggerated_patterns:
            if pattern in content_text.lower():
                truthfulness["warnings"].append(f"Potentially exaggerated language: {pattern}")
                truthfulness["flagged_content"].append(pattern)
        
        # Calculate truthfulness score
        truthfulness["score"] = max(0.0, 1.0 - (len(truthfulness["warnings"]) * 0.1))
        
        return truthfulness
    
    def _validate_content_completeness(self, resume: Dict[str, Any]) -> float:
        """Validate resume content completeness"""
        required_sections = ["contact_info", "professional_experience", "education", "skills"]
        present_sections = 0
        
        document = resume.get("document", {})
        for section in required_sections:
            if document.get(section):
                present_sections += 1
        
        return present_sections / len(required_sections)
    
    def _validate_format_consistency(self, resume: Dict[str, Any]) -> float:
        """Validate format consistency"""
        document = resume.get("document", {})
        consistency_score = 0.8  # Base score
        
        # Check for consistent formatting across sections
        fonts_used = set()
        for section_data in document.values():
            if isinstance(section_data, dict) and "formatting" in section_data:
                font = section_data["formatting"].get("font_size", "12pt")
                fonts_used.add(font)
        
        # Deduct points for inconsistent fonts
        if len(fonts_used) > 3:
            consistency_score -= 0.2
        
        return max(0.0, consistency_score)
    
    def _validate_job_alignment(self, resume: Dict[str, Any], job_requirements: Dict[str, Any]) -> float:
        """Validate job alignment"""
        # Simple alignment check based on skills
        resume_skills = self._extract_skills_from_resume(resume)
        required_skills = job_requirements.get("required_skills", [])
        
        if not required_skills:
            return 0.5  # Default score
        
        matches = 0
        for skill in required_skills:
            if any(skill.lower() in resume_skill.lower() for resume_skill in resume_skills):
                matches += 1
        
        return matches / len(required_skills) if required_skills else 0.0
    
    def _validate_ats_compliance(self, resume: Dict[str, Any]) -> float:
        """Validate ATS compliance"""
        ats_score = 0.9  # Base score
        
        # Check for ATS-friendly elements
        content_text = self._extract_text_content(resume)
        
        if len(content_text) > 10000:
            ats_score -= 0.3
        
        if not self._has_proper_headings(resume):
            ats_score -= 0.2
        
        return max(0.0, ats_score)
    
    def _validate_constraint_adherence(self, resume: Dict[str, Any]) -> float:
        """Validate constraint adherence"""
        constraint_score = 0.8  # Base score
        
        # Check length constraints
        content_text = self._extract_text_content(resume)
        max_length = self.constraints.get("max_resume_length", 1000)
        
        if len(content_text.split()) > max_length:
            constraint_score -= 0.2
        
        return max(0.0, constraint_score)
    
    def _identify_validation_issues(self, validation_checks: Dict[str, float]) -> List[str]:
        """Identify validation issues from check results"""
        issues = []
        
        for check_name, score in validation_checks.items():
            if score < 0.7:
                issues.append(f"Low score in {check_name}: {score:.2f}")
        
        return issues
    
    def _generate_recommendations(self, validation_checks: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        for check_name, score in validation_checks.items():
            if score < 0.7:
                if check_name == "content_completeness":
                    recommendations.append("Add missing sections to improve completeness")
                elif check_name == "format_consistency":
                    recommendations.append("Standardize formatting across all sections")
                elif check_name == "job_alignment":
                    recommendations.append("Better align skills and experience with job requirements")
                elif check_name == "ats_compliance":
                    recommendations.append("Improve ATS-friendly formatting")
                elif check_name == "constraint_adherence":
                    recommendations.append("Reduce content length to meet constraints")
        
        return recommendations
    
    def _extract_text_content(self, content: Any) -> str:
        """Extract text content from resume data"""
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            # Extract text from document structure
            document = content.get("document", {})
            text_parts = []
            
            for section_data in document.values():
                if isinstance(section_data, dict):
                    section_content = section_data.get("content", "")
                    if isinstance(section_content, str):
                        text_parts.append(section_content)
                    elif isinstance(section_content, list):
                        text_parts.extend(str(item) for item in section_content)
            
            return " ".join(text_parts)
        
        return str(content)
    
    def _extract_skills_from_resume(self, resume: Dict[str, Any]) -> List[str]:
        """Extract skills from resume data"""
        document = resume.get("document", {})
        skills_section = document.get("skills", {})
        
        if isinstance(skills_section, dict):
            content = skills_section.get("content", {})
            if isinstance(content, dict):
                # Extract from skills categories
                all_skills = []
                for skill_list in content.values():
                    if isinstance(skill_list, list):
                        all_skills.extend(skill_list)
                return all_skills
        
        return []
    
    def _has_proper_headings(self, resume: Dict[str, Any]) -> bool:
        """Check if resume has proper section headings"""
        document = resume.get("document", {})
        expected_headings = ["contact_info", "professional_experience", "education", "skills"]
        
        return any(heading in document for heading in expected_headings)
    
    def _has_standard_format(self, resume: Dict[str, Any]) -> bool:
        """Check if resume uses standard formatting"""
        # Simple check for standard formatting elements
        document = resume.get("document", {})
        
        for section_data in document.values():
            if isinstance(section_data, dict) and "formatting" in section_data:
                formatting = section_data["formatting"]
                if formatting.get("font_size") and formatting.get("spacing"):
                    return True
        
        return True
    
    def execute_validation(self, 
                          formatted_resume: Optional[Dict[str, Any]] = None,
                          job_requirements: Optional[Dict[str, Any]] = None,
                          quant_results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute complete K8 validation
        
        Args:
            formatted_resume: Formatted resume from K7
            job_requirements: Job requirements from K2
            quant_results: Quantification results from K3
            
        Returns:
            Complete validation results
        """
        result = {
            "step": "K8_VALIDATION",
            "status": "completed",
            "validation_results": {}
        }
        
        if formatted_resume and job_requirements and quant_results:
            result["validation_results"] = self.validate_resume_quality(
                formatted_resume, job_requirements, quant_results
            )
        
        # Add additional validation checks
        if formatted_resume:
            result["validation_results"]["ats_compliance"] = self.validate_ats_compliance(formatted_resume)
            result["validation_results"]["truthfulness"] = self.validate_content_truthfulness(formatted_resume)
        
        # Add metadata
        result["metadata"] = {
            "validators_count": len(self.validators),
            "constraints_count": len(self.constraints),
            "ats_rules_count": len(self.ats_rules),
            "routing_rules_count": len(self.routing_rules),
            "validation_completeness": "full" if formatted_resume and job_requirements and quant_results else "partial"
        }
        
        return result





