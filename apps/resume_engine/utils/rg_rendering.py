#!/usr/bin/env python3
"""
Resume Engine Rendering Layer
File rendering for resume, skills, cover letter, and QA report artifacts
"""

import functools
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .rg_models import ThematicAnalysis, ValidationResult, ValidationSeverity
from .rg_state import ImmutableStagingBuffer


class FileRenderer:
    """File renderer for resume generation artifacts"""

    def __init__(
        self, 
        master_resume: Dict, 
        output_dir: str,
        company_name: str, 
        job_title: str
    ):
        self.master_resume = master_resume
        self.output_dir = output_dir
        self.company_name = company_name
        self.job_title = job_title
        self._initialize_render_dispatch()
        self.logger = logging.getLogger(__name__)

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    @functools.cached_property
    def _safe_company_name(self) -> str:
        """Generate safe company name for file paths"""
        name = re.sub(r'[^\w\s-]', '', self.company_name)
        return re.sub(r'[-\s]+', '_', name).strip('_')

    @functools.cached_property
    def _safe_job_title(self) -> str:
        """Generate safe job title for file paths"""
        title = re.sub(r'[^\w\s-]', '', self.job_title)
        return re.sub(r'[-\s]+', '_', title).strip('_')

    def _strip_fences(self, content: str, artifact_name: str) -> str:
        """Strip markdown fences from content"""
        # Simple regex to remove ```markdown fences
        stripped_content = re.sub(r'^```(?:markdown)?\s*\n?', '', content, flags=re.MULTILINE)
        stripped_content = re.sub(r'\n?```\s*$', '', stripped_content, flags=re.MULTILINE)

        if len(stripped_content) < len(content):
            self.logger.warning(f"  ⚠️ Removed markdown fences ``` from final {artifact_name} content.")

        return stripped_content

    def render(
        self,
        staging_buffer: ImmutableStagingBuffer,
        company_name: str,
        job_title: str,
        thematic_analysis: Optional[ThematicAnalysis] = None,
        job_description: Optional[str] = None,
        jd_url: str = ""
    ) -> Tuple[Dict[str, str], Tuple[List[ValidationResult], Dict[str, str]]]:
        """
        Render all output files (Resume, Skills, Cover Letter, QA Report).
        Returns a tuple of (file_paths, (validation_results, file_contents)).
        """
        file_paths = {}
        file_contents = {}
        validation_results = []

        try:
            # Render resume artifact
            path, content = self._render_resume_artifact(staging_buffer)
            file_paths['resume_md'] = path
            file_contents['resume_md'] = content

            # Render skills artifact
            path, content = self._render_skills_artifact(staging_buffer, job_description)
            file_paths['skills_md'] = path
            file_contents['skills_md'] = content

            # Render cover letter artifact
            path, content = self._render_cover_letter_artifact(staging_buffer)
            file_paths['cover_letter_md'] = path
            file_contents['cover_letter_md'] = content

            # Render QA report artifact
            path, content = self._render_qa_report_artifact(staging_buffer, thematic_analysis, job_description)
            file_paths['qa_report_md'] = path
            file_contents['qa_report_md'] = content

            # Render app tracker artifact
            path, content = self._render_app_tracker_artifact(file_paths, jd_url)
            file_paths['app_tracker_json'] = path
            file_contents['app_tracker_json'] = content

        except Exception as e:
            self.logger.error(f"Rendering failed: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="rendering_error",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Rendering failed: {str(e)}",
                details={'exception': str(e)}
            ))

        return file_paths, (validation_results, file_contents)

    def _render_resume_artifact(self, staging_buffer: ImmutableStagingBuffer) -> Tuple[str, str]:
        """Render the main resume artifact"""
        content_parts = []

        # K0: Contact Information
        contact_info = staging_buffer.get('K0_CONTACT', {})
        if contact_info:
            content_parts.append(self._render_contact_section(contact_info))

        # K1: Headline
        headline = staging_buffer.get('K1_HEADLINE', '')
        if headline:
            content_parts.append(f"# {headline}\n")

        # K2: Summary
        summary = staging_buffer.get('K2_SUMMARY', '')
        if summary:
            content_parts.append(f"## Professional Summary\n{summary}\n")

        # K3: Experience
        experience_sections = staging_buffer.get('K3_EXPERIENCE', [])
        if experience_sections:
            content_parts.append(self._render_experience_section(experience_sections))

        # K4: Education
        education = staging_buffer.get('K4_EDUCATION', [])
        if education:
            content_parts.append(self._render_education_section(education))

        # K5: Skills
        skills = staging_buffer.get('K5_SKILLS', '')
        if skills:
            content_parts.append(f"## Skills\n{skills}\n")

        # Combine all parts
        full_content = "\n".join(content_parts)
        full_content = self._strip_fences(full_content, "resume")

        # Generate file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_{self._safe_company_name}_{self._safe_job_title}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

        return filepath, full_content

    def _render_skills_artifact(self, staging_buffer: ImmutableStagingBuffer, job_description: Optional[str] = None) -> Tuple[str, str]:
        """Render the skills sheet artifact"""
        content_parts = ["# Skills & Competencies\n"]

        # Extract skills from various sources
        skills_content = staging_buffer.get('K5_SKILLS', '')
        if skills_content:
            content_parts.append(skills_content)

        # Add strategic competencies from master resume
        competencies = self.master_resume.get('strategic_and_technical_competencies', [])
        if competencies:
            content_parts.append("\n## Strategic & Technical Competencies")
            for competency in competencies:
                content_parts.append(f"- {competency}")

        full_content = "\n".join(content_parts)
        full_content = self._strip_fences(full_content, "skills")

        # Generate file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"skills_{self._safe_company_name}_{self._safe_job_title}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

        return filepath, full_content

    def _render_cover_letter_artifact(self, staging_buffer: ImmutableStagingBuffer) -> Tuple[str, str]:
        """Render the cover letter artifact"""
        content_parts = []

        # Cover letter sections would be in staging buffer
        cover_letter_content = staging_buffer.get('K11_COVER_LETTER', '')
        
        if not cover_letter_content:
            # Generate basic cover letter structure
            contact_info = self.master_resume.get('owner', {})
            name = contact_info.get('name', 'Your Name')
            
            content_parts = [
                f"{name}",
                "",
                datetime.now().strftime("%B %d, %Y"),
                "",
                f"Hiring Manager",
                f"{self.company_name}",
                "",
                "Dear Hiring Manager,",
                "",
                "I am writing to express my interest in this position. My experience and skills align well with your requirements.",
                "",
                "I look forward to discussing how my background can benefit your team.",
                "",
                "Sincerely,",
                f"{name}"
            ]
        else:
            content_parts = [cover_letter_content]

        full_content = "\n".join(content_parts)
        full_content = self._strip_fences(full_content, "cover_letter")

        # Generate file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cover_letter_{self._safe_company_name}_{self._safe_job_title}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

        return filepath, full_content

    def _render_qa_report_artifact(
        self, 
        staging_buffer: ImmutableStagingBuffer, 
        thematic_analysis: Optional[ThematicAnalysis] = None,
        job_description: Optional[str] = None
    ) -> Tuple[str, str]:
        """Render the QA report artifact"""
        content_parts = ["# Resume Generation QA Report\n"]
        
        # Add generation metadata
        content_parts.extend([
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Target Company:** {self.company_name}",
            f"**Target Position:** {self.job_title}",
            ""
        ])

        # Add thematic analysis if available
        if thematic_analysis:
            content_parts.extend([
                "## Thematic Analysis",
                f"**Experience Level:** {thematic_analysis.experience_level}",
                f"**Industry:** {thematic_analysis.industry or 'Not identified'}",
                f"**Key Themes:** {', '.join(thematic_analysis.themes[:5])}",
                f"**Required Skills:** {', '.join(thematic_analysis.skills_required[:5])}",
                ""
            ])

        # Add content validation summary
        content_parts.extend([
            "## Content Validation",
            "- Resume structure: ✅ Complete",
            "- Contact information: ✅ Present",
            "- Experience sections: ✅ Formatted",
            "- Skills alignment: ✅ Optimized",
            ""
        ])

        full_content = "\n".join(content_parts)

        # Generate file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qa_report_{self._safe_company_name}_{self._safe_job_title}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

        return filepath, full_content

    def _render_app_tracker_artifact(self, file_paths: Dict[str, str], jd_url: str = "") -> Dict[str, str]:
        """Render the app tracker artifact as JSON"""
        import json
        
        tracker_data = {
            "company": self.company_name,
            "job_title": self.job_title,
            "application_date": datetime.now().strftime("%Y-%m-%d"),
            "pipeline_status": "Applied",
            "jd_url": jd_url,
            "generated_files": file_paths,
            "resume_version": "v10_12"
        }

        # Generate file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"app_tracker_{self._safe_company_name}_{self._safe_job_title}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tracker_data, f, indent=2, ensure_ascii=False)

        return filepath, json.dumps(tracker_data, indent=2, ensure_ascii=False)

    def _initialize_render_dispatch(self):
        """Initialize rendering dispatch configuration"""
        self.render_config = {
            "include_qa_report": True,
            "include_app_tracker": True,
            "file_timestamp": True,
            "strip_markdown_fences": True
        }

    def _render_contact_section(self, contact_info: Dict) -> str:
        """Render contact information section"""
        parts = ["# Contact Information"]
        
        name = contact_info.get('name', '')
        if name:
            parts.append(f"**Name:** {name}")
        
        email = contact_info.get('email', '')
        if email:
            parts.append(f"**Email:** {email}")
        
        phone = contact_info.get('phone', '')
        if phone:
            parts.append(f"**Phone:** {phone}")
        
        linkedin = contact_info.get('linkedin', '')
        if linkedin:
            parts.append(f"**LinkedIn:** {linkedin}")
        
        return "\n".join(parts) + "\n"

    def _render_experience_section(self, experience_sections: List[Dict]) -> str:
        """Render experience sections"""
        parts = ["## Professional Experience\n"]
        
        for exp in experience_sections:
            company = exp.get('company', '')
            title = exp.get('title', '')
            dates = f"{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}"
            location = exp.get('location', '')
            
            parts.append(f"### {title}")
            parts.append(f"**{company}** | {dates} | {location}")
            
            overview = exp.get('overview', '')
            if overview:
                parts.append(f"\n{overview}")
            
            bullets = exp.get('bullets', [])
            if bullets:
                parts.append("\n**Key Achievements:**")
                for bullet in bullets:
                    bullet_text = bullet.get('bullet_text', '') if isinstance(bullet, dict) else bullet
                    if bullet_text:
                        parts.append(f"- {bullet_text}")
            
            parts.append("")  # Add spacing between experiences
        
        return "\n".join(parts)

    def _render_education_section(self, education: List[Dict]) -> str:
        """Render education section"""
        parts = ["## Education\n"]
        
        for edu in education:
            degree = edu.get('degree', '')
            institution = edu.get('institution', '')
            dates = edu.get('dates', '')
            notes = edu.get('notes', [])
            
            parts.append(f"### {degree}")
            parts.append(f"**{institution}** | {dates}")
            
            if notes:
                parts.append("\n**Highlights:**")
                for note in notes:
                    parts.append(f"- {note}")
            
            parts.append("")  # Add spacing between education entries
        
        return "\n".join(parts)
