"""
Validation Pipeline Service
LEVEL 5 - Resume content validation and quality assurance
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import re

@dataclass
class ValidationResult:
    """Results of resume validation checks"""
    is_valid: bool
    validation_score: float
    issues_found: List[str]
    recommendations: List[str]
    quality_metrics: Dict[str, float]

class ValidationPipeline:
    """Validates resume content for quality, completeness, and ATS compliance"""

    def __init__(self):
        self.validation_rules = {
            "content": {
                "min_word_count": 150,
                "max_word_count": 600,
                "required_sections": ["experience", "education", "skills"],
                "max_bullet_points_per_section": 8
            },
            "formatting": {
                "max_line_length": 80,
                "consistent_tense": True,
                "action_verbs_required": True,
                "quantification_required": True
            },
            "ats_compliance": {
                "min_keyword_density": 0.5,
                "no_special_characters": True,
                "standard_section_headers": True
            },
            "professional_standards": {
                "no_typos": True,
                "professional_language": True,
                "contact_info_required": True
            }
        }

        self.quality_weights = {
            "content_quality": 0.3,
            "formatting": 0.2,
            "ats_compliance": 0.3,
            "professional_standards": 0.2
        }

    async def validate(
        self,
        resume_content: Dict[str, Any],
        job_description: Dict[str, Any] = None
    ) -> ValidationResult:
        """
        Perform comprehensive validation of resume content
        
        Args:
            resume_content: Resume structure to validate
            job_description: Optional job requirements for context validation
            
        Returns:
            Detailed validation results with recommendations
        """
        issues = []
        recommendations = []
        quality_metrics = {}

        # Content validation
        content_score, content_issues, content_recs = await self._validate_content(resume_content)
        issues.extend(content_issues)
        recommendations.extend(content_recs)
        quality_metrics["content_quality"] = content_score

        # Formatting validation
        format_score, format_issues, format_recs = await self._validate_formatting(resume_content)
        issues.extend(format_issues)
        recommendations.extend(format_recs)
        quality_metrics["formatting"] = format_score

        # ATS compliance validation
        ats_score, ats_issues, ats_recs = await self._validate_ats_compliance(resume_content, job_description)
        issues.extend(ats_issues)
        recommendations.extend(ats_recs)
        quality_metrics["ats_compliance"] = ats_score

        # Professional standards validation
        professional_score, prof_issues, prof_recs = await self._validate_professional_standards(resume_content)
        issues.extend(prof_issues)
        recommendations.extend(prof_recs)
        quality_metrics["professional_standards"] = professional_score

        # Calculate overall validation score
        overall_score = await self._calculate_overall_score(quality_metrics)

        # Determine if resume is valid
        is_valid = overall_score >= 0.7 and len([issue for issue in issues if "Critical" in issue]) == 0

        return ValidationResult(
            is_valid=is_valid,
            validation_score=overall_score,
            issues_found=issues,
            recommendations=recommendations[:10],  # Top 10 recommendations
            quality_metrics=quality_metrics
        )

    async def _validate_content(self, resume_content: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """Validate content structure and completeness"""
        issues = []
        recommendations = []

        # Check word count
        total_words = 0
        for section in resume_content.values():
            content = section.get("content", [])
            if isinstance(content, list):
                total_words += sum(len(item.split()) for item in content)
            else:
                total_words += len(str(content).split())

        if total_words < self.validation_rules["content"]["min_word_count"]:
            issues.append("Critical: Resume is too brief")
            recommendations.append("Expand content to meet minimum word count of 150 words")
        elif total_words > self.validation_rules["content"]["max_word_count"]:
            issues.append("Warning: Resume may be too long")
            recommendations.append("Consider condensing content for one-page format")

        # Check required sections
        existing_sections = list(resume_content.keys())
        required_sections = self.validation_rules["content"]["required_sections"]

        for required in required_sections:
            if not any(required.lower() in section.lower() for section in existing_sections):
                issues.append(f"Critical: Missing required section: {required}")
                recommendations.append(f"Add {required} section to complete resume")

        # Check bullet point counts
        for section_name, section in resume_content.items():
            content = section.get("content", [])
            if isinstance(content, list):
                bullet_count = len([item for item in content if item.strip().startswith("•")])
                max_bullets = self.validation_rules["content"]["max_bullet_points_per_section"]

                if bullet_count > max_bullets:
                    issues.append(f"Warning: Too many bullet points in {section_name}")
                    recommendations.append(f"Reduce bullet points in {section_name} to {max_bullets} or fewer")

        # Calculate content score
        content_score = 1.0
        if total_words < self.validation_rules["content"]["min_word_count"]:
            content_score -= 0.3
        if total_words > self.validation_rules["content"]["max_word_count"]:
            content_score -= 0.1

        missing_sections = len([
            req for req in required_sections
            if not any(req.lower() in section.lower() for section in existing_sections)
        ])
        content_score -= (missing_sections * 0.2)

        return max(content_score, 0.0), issues, recommendations

    async def _validate_formatting(self, resume_content: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """Validate formatting consistency and standards"""
        issues = []
        recommendations = []

        # Check line lengths
        max_length = self.validation_rules["formatting"]["max_line_length"]
        long_lines = []

        for section_name, section in resume_content.items():
            content = section.get("content", [])
            if isinstance(content, list):
                for i, line in enumerate(content):
                    if len(line) > max_length:
                        long_lines.append(f"{section_name}[{i}]: {len(line)} chars")

        if long_lines:
            issues.append("Warning: Some lines exceed maximum length")
            recommendations.append("Break long lines to improve readability")

        # Check for consistent tense
        tense_issues = await self._check_tense_consistency(resume_content)
        if tense_issues:
            issues.append("Warning: Inconsistent tense usage")
            recommendations.append("Ensure consistent past tense for experience descriptions")

        # Check for action verbs
        action_verbs = ["developed", "implemented", "managed", "led", "optimized", "created"]
        has_action_verbs = False

        for section in resume_content.values():
            content = section.get("content", [])
            if isinstance(content, list):
                content_text = " ".join(content).lower()
                if any(verb in content_text for verb in action_verbs):
                    has_action_verbs = True
                    break

        if not has_action_verbs:
            issues.append("Warning: Missing action verbs in experience descriptions")
            recommendations.append("Start bullet points with strong action verbs")

        # Calculate formatting score
        format_score = 1.0
        if long_lines:
            format_score -= 0.1
        if tense_issues:
            format_score -= 0.1
        if not has_action_verbs:
            format_score -= 0.2

        return max(format_score, 0.0), issues, recommendations

    async def _validate_ats_compliance(
        self,
        resume_content: Dict[str, Any],
        job_description: Dict[str, Any] = None
    ) -> Tuple[float, List[str], List[str]]:
        """Validate ATS compliance and keyword optimization"""
        issues = []
        recommendations = []

        # Extract all text from resume
        all_text = ""
        for section in resume_content.values():
            content = section.get("content", [])
            if isinstance(content, list):
                all_text += " ".join(content) + " "
            else:
                all_text += str(content) + " "

        all_text = all_text.lower()

        # Check for special characters that ATS systems may not parse well
        special_chars = ["★", "♦", "►", "•", "→", "✓"]
        found_special = [char for char in special_chars if char in all_text]

        if found_special:
            issues.append("Warning: Contains special characters that may confuse ATS")
            recommendations.append("Replace special characters with standard text")

        # Check section headers
        section_headers = list(resume_content.keys())
        non_standard_headers = [
            header for header in section_headers
            if header.lower() not in ["summary", "experience", "education", "skills", "projects", "certifications"]
        ]

        if non_standard_headers:
            issues.append("Warning: Non-standard section headers detected")
            recommendations.append("Use standard section headers for better ATS parsing")

        # Calculate keyword density if job description provided
        if job_description:
            job_requirements = job_description.get("requirements", [])
            job_text = " ".join(job_requirements).lower()

            # Extract keywords from job description
            job_keywords = re.findall(r'\b\w+\b', job_text)
            job_keywords = [kw for kw in job_keywords if len(kw) > 3]

            # Calculate keyword density
            resume_words = re.findall(r'\b\w+\b', all_text)
            total_words = len(resume_words)

            if total_words > 0:
                keyword_matches = sum(1 for kw in job_keywords if kw in all_text)
                keyword_density = keyword_matches / total_words

                min_density = self.validation_rules["ats_compliance"]["min_keyword_density"]
                if keyword_density < min_density:
                    issues.append("Warning: Low keyword density for target job")
                    recommendations.append("Include more relevant keywords from job description")

        # Calculate ATS compliance score
        ats_score = 1.0
        if found_special:
            ats_score -= 0.2
        if non_standard_headers:
            ats_score -= 0.1

        return max(ats_score, 0.0), issues, recommendations

    async def _validate_professional_standards(self, resume_content: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """Validate professional language and standards"""
        issues = []
        recommendations = []

        # Extract all text
        all_text = ""
        for section in resume_content.values():
            content = section.get("content", [])
            if isinstance(content, list):
                all_text += " ".join(content) + " "
            else:
                all_text += str(content) + " "

        # Check for common typos and errors
        common_errors = ["resposible", "managment", "succesful", "acheivement", "experiance"]
        found_errors = [error for error in common_errors if error in all_text.lower()]

        if found_errors:
            issues.append("Critical: Potential spelling errors detected")
            recommendations.append("Review and correct spelling errors")

        # Check for unprofessional language
        unprofessional_terms = ["awesome", "cool", "stuff", "things", "etc"]
        found_unprofessional = [term for term in unprofessional_terms if term in all_text.lower()]

        if found_unprofessional:
            issues.append("Warning: Contains informal language")
            recommendations.append("Replace informal terms with professional language")

        # Check for contact information (simplified check)
        has_email = "@" in all_text
        has_phone = any(char.isdigit() for char in all_text) and len(re.findall(r'\d+', all_text)) >= 10

        if not has_email:
            issues.append("Critical: Missing email contact information")
            recommendations.append("Add professional email address")

        if not has_phone:
            issues.append("Warning: Missing phone contact information")
            recommendations.append("Add phone number for contact")

        # Calculate professional standards score
        professional_score = 1.0
        if found_errors:
            professional_score -= 0.3
        if found_unprofessional:
            professional_score -= 0.1
        if not has_email:
            professional_score -= 0.2
        if not has_phone:
            professional_score -= 0.1

        return max(professional_score, 0.0), issues, recommendations

    async def _check_tense_consistency(self, resume_content: Dict[str, Any]) -> bool:
        """Check for consistent tense usage in experience descriptions"""
        # Simplified tense checking
        past_tense_indicators = ["ed ", "led ", "managed ", "developed ", "implemented "]
        present_tense_indicators = ["ing ", "manage ", "develop ", "implement "]

        for section_name, section in resume_content.items():
            if "experience" in section_name.lower():
                content = section.get("content", [])
                if isinstance(content, list):
                    for line in content:
                        line_lower = line.lower()
                        has_past = any(indicator in line_lower for indicator in past_tense_indicators)
                        has_present = any(indicator in line_lower for indicator in present_tense_indicators)

                        if has_present and not has_past:
                            return True  # Tense inconsistency found

        return False

    async def _calculate_overall_score(self, quality_metrics: Dict[str, float]) -> float:
        """Calculate weighted overall validation score"""
        total_score = 0
        total_weight = 0

        for metric, score in quality_metrics.items():
            weight = self.quality_weights.get(metric, 0.1)
            total_score += score * weight
            total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0

__all__ = ["ValidationPipeline", "ValidationResult"]
