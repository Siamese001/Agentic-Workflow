# File: renderer_RES_v2.py
# FileRenderer class - renders final resume artifacts to files
# Version: 17.01 (Patched)

import copy
import functools
import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, TYPE_CHECKING

from models_RES import ResumeSection, ImmutableStagingBuffer, ThematicAnalysis, ValidationResult, ValidationSeverity
from config_RES_v2 import AppConfig, DATA_DIR, CONFIG
from utils_RES_v2 import text_utils, sanitize_filename
# --- V18 REFACTOR: Import consolidated validator ---
from validator_RES_v2 import AppTrackerQAValidator
# --- END V18 REFACTOR ---

if TYPE_CHECKING:
    from workflow_RES_v2 import WorkflowOrchestrator

logger = logging.getLogger(__name__)
# text_utils is imported from utils_RES_v2


class FileRenderer:

    def __init__(self, master_resume: Dict, orchestrator: 'WorkflowOrchestrator', company_name: str, job_title: str, config: AppConfig):
        self.master_resume = master_resume
        self.orchestrator = orchestrator
        self.company_name = company_name
        self.job_title = job_title
        self.config = config
        self._initialize_render_dispatch()
        self.logger = logging.getLogger(__name__)

    @functools.cached_property
    def _safe_company_name(self) -> str:
        name = re.sub(r'[^\w\s-]', '', self.company_name)
        return re.sub(r'[-\s]+', '_', name).strip('_')

    @functools.cached_property
    def _safe_job_title(self) -> str:
        title = re.sub(r'[^\w\s-]', '', self.job_title)
        return re.sub(r'[-\s]+', '_', title).strip('_')

    def _strip_fences(self, content: str, artifact_name: str) -> str:
        stripped_content = text_utils.strip_markdown_fences(content)

        if len(stripped_content) < len(content):
            self.logger.warning(f"  ⚠️ Removed markdown fences ``` from final {artifact_name} content.")

        return stripped_content

    def render(
        self,
        staging_buffer: ImmutableStagingBuffer,
        company_name: str,
        job_title: str,
        thematic_analysis: ThematicAnalysis,
        job_description: Optional[str] = None,
        jd_url: str = ""
    ) -> Tuple[Dict[str, str], Tuple[List[ValidationResult], Dict[str, str]]]:
        """
        Render all output files (Resume, Skills, Cover Letter, QA Report, App Tracker).
        Uses K0-K11 Enum scheme. Includes fence stripping for relevant artifacts.
        Returns a tuple of (file_paths, (validation_results, file_contents)).
        """
        file_paths = {}
        file_contents = {}
        validation_results = []

        try:
            path, content = self._render_resume_artifact(staging_buffer)
            file_paths['resume_md'] = path
            file_contents['resume_md'] = content
            validation_results.append(ValidationResult(
                rule_id="RENDER_RESUME_MD", passed=True, severity=ValidationSeverity.INFO,
                message="Resume MD rendered successfully."
            ))
        except Exception as e:
            self.logger.error(f"Error rendering Resume MD: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_RESUME_MD", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render Resume MD: {e}"
            ))
            file_contents['resume_md'] = f"[ERROR: Resume Rendering Failed: {e}]"

        try:
            path, content = self._render_skills_artifact(staging_buffer, job_description)
            file_paths['skills'] = path
            file_contents['skills'] = content
            validation_results.append(ValidationResult(
                rule_id="RENDER_SKILLS", passed=True, severity=ValidationSeverity.INFO,
                message="Skills TXT rendered successfully."
            ))
        except Exception as e:
            self.logger.error(f"Error rendering Skills TXT: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_SKILLS", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render Skills TXT: {e}"
            ))
            file_contents['skills'] = f"[ERROR: Skills Rendering Failed: {e}]"

        try:
            path, content = self._render_cover_letter_artifact(staging_buffer)
            file_paths['cover_letter'] = path
            file_contents['cover_letter'] = content
            validation_results.append(ValidationResult(
                rule_id="RENDER_COVER_LETTER", passed=True, severity=ValidationSeverity.INFO,
                message="Cover Letter TXT rendered successfully."
            ))
        except Exception as e:
            self.logger.error(f"Error rendering Cover Letter TXT: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_COVER_LETTER", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render Cover Letter TXT: {e}"
            ))
            file_contents['cover_letter'] = f"[ERROR: Cover Letter Rendering Failed: {e}]"

        try:
            path, content_placeholder = self._render_qa_report_artifact()
            file_paths['qa_report'] = path
            file_contents['qa_report'] = content_placeholder
            validation_results.append(ValidationResult(
                rule_id="RENDER_QA_PATH", passed=True, severity=ValidationSeverity.INFO,
                message="QA Report path generated."
            ))
        except Exception as e:
            self.logger.error(f"Error generating QA Report path: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_QA_PATH", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to generate QA Report path: {e}"
            ))

        try:
            # --- FIX: (Role Confusion) Removed validation results from return tuple ---
            path, content = self._render_app_tracker_artifact(file_paths, jd_url=jd_url)
            file_paths['app_tracker'] = path
            file_contents['app_tracker'] = content
            # --- END FIX ---
            validation_results.append(ValidationResult(
                rule_id="RENDER_APP_TRACKER",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="App Tracker JSON rendered successfully (validation moved to QA_Auditor)."
            ))
        except Exception as e:
            self.logger.error(f"Error rendering App Tracker JSON: {e}", exc_info=True)
            validation_results.append(ValidationResult(
                rule_id="RENDER_APP_TRACKER", passed=False, severity=ValidationSeverity.CRITICAL,
                message=f"Failed to render App Tracker JSON: {e}"
            ))
            file_contents['app_tracker'] = f"[ERROR: App Tracker Rendering Failed: {e}]"

        return file_paths, (validation_results, file_contents)

    def _render_resume_artifact(self, staging_buffer: ImmutableStagingBuffer) -> Tuple[str, str]:
        raw_content = self._render_resume_markdown(staging_buffer)
        final_content = self._strip_fences(raw_content, "Resume MD")

        candidate_name = self.master_resume.get("owner", {}).get("name", "Candidate").replace(" ", "_")
        base_filename = f"{candidate_name}_Resume_{self._safe_company_name}_{self._safe_job_title}"
        path = f"{base_filename}.md"

        return path, final_content

    def _render_skills_artifact(self, staging_buffer: ImmutableStagingBuffer, job_description: Optional[str] = None) -> Tuple[str, str]:
        raw_content = self._render_skills(staging_buffer, job_description)
        final_content = self._strip_fences(raw_content, "Skills TXT")
        path = f"Skills_{self._safe_company_name}_{self._safe_job_title}.txt"
        return path, final_content

    def _render_cover_letter_artifact(self, staging_buffer: ImmutableStagingBuffer) -> Tuple[str, str]:
        raw_content = staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
        final_content = self._strip_fences(raw_content, "Cover Letter TXT")
        path = f"CoverLetter_{self._safe_company_name}_{self._safe_job_title}.txt"
        return path, final_content

    def _render_qa_report_artifact(self) -> Tuple[str, str]:
        path = f"QA_Report_{self._safe_company_name}_{self._safe_job_title}.md"
        return path, "[QA Report Content Placeholder - Generated in HOP-8]"

    def _render_app_tracker_artifact(self, file_paths: Dict[str, str], jd_url: str = "") -> Tuple[str, str]:
        # --- FIX: (Role Confusion) This method now *only* renders the file. ---
        # Validation logic has been removed.
        app_tracker_data = self._render_app_tracker(file_paths, jd_url=jd_url)
        content = json.dumps(app_tracker_data, indent=2)
        path = f"AppTracker_{self._safe_company_name}_{self._safe_job_title}.json"
        return path, content
        # --- END FIX ---

    RESUME_RENDER_CONFIG = [
        {"type": "simple", "source": ResumeSection.K0_NAME, "render_method": "_render_name"},
        {"type": "simple", "source": ResumeSection.K0_HEADLINE, "render_method": "_render_headline"},
        {"type": "simple", "source": ResumeSection.K0_CONTACT, "render_method": "_render_contact"},
        {"type": "header", "text": "## EXECUTIVE SUMMARY"},
        {"type": "simple", "source": ResumeSection.K1_EXECUTIVE_SUMMARY, "render_method": "_render_paragraph"},
        {"type": "header", "text": "## PROFESSIONAL EXPERIENCE"},
        {"type": "experience", "master_index": 0, "overview_source": ResumeSection.K2_UNIFY_OVERVIEW, "bullets_source": ResumeSection.K2_UNIFY_BULLETS},
        {"type": "experience", "master_index": 1, "overview_source": ResumeSection.K3_IBM_OVERVIEW, "bullets_source": ResumeSection.K3_IBM_BULLETS},
        {"type": "experience_narrative", "master_index": 2, "narrative_source": ResumeSection.K4_TRADERSENSE_NARRATIVE},
        {"type": "experience_narrative", "master_index": 3, "narrative_source": ResumeSection.K5_EY_NARRATIVE},
        {"type": "experience_narrative", "master_index": 4, "narrative_source": ResumeSection.K6_EARLY_CAREER_NARRATIVE},
        {"type": "header", "text": "## EDUCATION"},
        {"type": "education", "source": ResumeSection.K7_EDUCATION},
        {"type": "header", "text": "## CERTIFICATIONS & CREDENTIALS"},
        {"type": "certifications", "source": ResumeSection.K8_CERTIFICATIONS},
        {"type": "header", "text": "## STRATEGIC & TECHNICAL COMPETENCIES"},
        {"type": "competencies", "source": ResumeSection.K9_COMPETENCIES},
    ]

    def _initialize_render_dispatch(self):
        self._RENDER_DISPATCH = {
            "header": self._handle_render_header,
            "simple": self._handle_render_simple,
            "experience": self._handle_render_experience,
            "experience_narrative": self._handle_render_experience_narrative,
            "education": self._handle_render_list,
            "certifications": self._handle_render_list,
            "competencies": self._handle_render_list,
            "list": self._handle_render_list,
        }

    def _handle_render_header(self, config: Dict, staging_buffer: ImmutableStagingBuffer) -> str:
        return config.get("text", "")

    def _handle_render_simple(self, config: Dict, staging_buffer: ImmutableStagingBuffer) -> str:
        content = staging_buffer.get(config["source"].value)
        if content:
            render_method = getattr(self, config["render_method"])
            return render_method(content)
        return ""

    def _handle_render_experience(self, config: Dict, staging_buffer: ImmutableStagingBuffer) -> str:
        master_experience = self.master_resume.get("professional_experience", [])
        master_index = config["master_index"]
        if 0 <= master_index < len(master_experience):
            master_exp = master_experience[master_index]
            overview = staging_buffer.get(config["overview_source"].value)
            bullets = staging_buffer.get(config["bullets_source"].value)
            return self._render_experience_section_std(master_exp, overview, bullets)
        else:
            self.logger.warning(f"Master experience index {master_index} out of bounds. Max index: {len(master_experience)-1}.")
            return ""

    def _handle_render_experience_narrative(self, config: Dict, staging_buffer: ImmutableStagingBuffer) -> str:
        master_experience = self.master_resume.get("professional_experience", [])
        master_index = config["master_index"]
        if 0 <= master_index < len(master_experience):
            master_exp = master_experience[master_index]
            narrative = staging_buffer.get(config["narrative_source"].value)
            return self._render_experience_section_narrative(master_exp, narrative)
        else:
            self.logger.warning(f"Master experience index {master_index} out of bounds. Max index: {len(master_experience)-1}.")
            return ""

    def _handle_render_list(self, config: Dict, staging_buffer: ImmutableStagingBuffer) -> str:
        content = staging_buffer.get(config["source"].value)
        if content and isinstance(content, list):
            item_prefix = "* "
            if config["source"] == ResumeSection.K7_EDUCATION:
                return self._render_list_section(content, item_prefix="")
            elif config["source"] == ResumeSection.K8_CERTIFICATIONS:
                return self._render_list_section(content, item_prefix="* ")
            elif config["source"] == ResumeSection.K9_COMPETENCIES:
                return self._render_list_section(content, item_prefix="")
            else:
                return self._render_list_section(content, item_prefix=config.get("item_prefix", "* "))
        elif not content:
             self.logger.warning(f"Content for list section {config['source'].name} is missing or empty.")
             return ""
        else:
             self.logger.warning(f"Expected list content for section {config['source'].name}, got {type(content)}. Rendering as string.")
             return str(content) + "\n"

    def _render_name(self, content: str) -> str: return f"# {content.strip()}\n"
    def _render_headline(self, content: str) -> str: return f"{content.strip()}\n"
    def _render_contact(self, content: str) -> str: return f"{content.strip()}\n"
    def _render_paragraph(self, content: str) -> str: return f"{content.strip()}\n"
    def _render_experience_section_std(self, master_exp: Dict, overview: Optional[str], bullets: Optional[List[Union[str, Dict]]]) -> str:
        lines = self._render_experience_header(master_exp)
        if overview and isinstance(overview, str) and overview.strip(): lines.append(f"\n{overview.strip()}")
        bullet_lines = []
        bullets_list = bullets if isinstance(bullets, list) else []
        for bullet in bullets_list:
            text = ""
            if isinstance(bullet, dict): text = bullet.get('text', '').strip()
            elif isinstance(bullet, str): text = bullet.strip()
            if text: bullet_lines.append(f"* {text}")
        if bullet_lines: lines.append("\n" + "\n".join(bullet_lines))
        return "\n".join(lines) + "\n"

    def _render_experience_section_narrative(self, master_exp: Dict, narrative: Optional[str]) -> str:
        lines = self._render_experience_header(master_exp)
        if narrative and isinstance(narrative, str) and narrative.strip(): lines.append(f"\n{narrative.strip()}")
        master_highlights = master_exp.get('highlights', [])
        highlight_lines = []
        if master_highlights and isinstance(master_highlights, list):
             for hl in master_highlights:
                  if isinstance(hl, str) and hl.strip(): highlight_lines.append(f"* {hl.strip()}")
        if highlight_lines:
             prefix = "\n" if (narrative and narrative.strip()) else ""; lines.append(prefix + "\n".join(highlight_lines))
        return "\n".join(lines) + "\n"

    def _render_experience_header(self, master_exp: Dict) -> List[str]:
        header_lines = []; company = master_exp.get('company', '').strip(); location = master_exp.get('location', '').strip()
        line1_parts = [part for part in [company, location] if part]; title = master_exp.get('title', '').strip()
        start = master_exp.get('dates', {}).get('start', '').strip(); end = master_exp.get('dates', {}).get('end', '').strip()
        date_str = " – ".join(filter(None, [start, end])); line2_parts = [part for part in [title, date_str] if part]
        if line1_parts: header_lines.append(f"**{' | '.join(line1_parts)}**")
        if line2_parts: header_lines.append(f"**{' | '.join(line2_parts)}**")
        return header_lines

    def _render_list_section(self, content_list: List[Union[str, Dict]], item_prefix: str = "") -> str:
        lines = []
        if not isinstance(content_list, list): return ""
        for item in content_list:
            text_to_render = ""
            if isinstance(item, str): text_to_render = item.strip()
            elif isinstance(item, dict):
                if 'degree' in item and 'institution' in item:
                    degree = item.get('degree', '').strip()
                    institution = item.get('institution', '').strip()
                    parts = [p for p in [degree, institution] if p]
                    text_to_render = ", ".join(parts)
                    notes = item.get('notes', '').strip()
                    if notes: text_to_render += f" ({notes})"
                else: text_to_render = item.get('text', str(item)).strip()

            if text_to_render:
                if text_to_render.startswith("*") or text_to_render.startswith("**"):
                    lines.append(text_to_render)
                else:
                    lines.append(f"{item_prefix}{text_to_render}")

        return "\n".join(lines) + "\n" if lines else ""

    def _render_skills(self, staging_buffer: ImmutableStagingBuffer, job_description: Optional[str] = None) -> str:
        skills_list = staging_buffer.get(ResumeSection.K10_SKILLS.value)
        output_lines = []; valid_skills = []; malformed = []
        if not isinstance(skills_list, list) or not skills_list: return "• Error: K.10_Skills list not found or invalid."
        if isinstance(skills_list[0], str) and skills_list[0].startswith("Error:"): return "\n\n".join(skills_list)
        for skill in skills_list:
            if isinstance(skill, str):
                cleaned = skill.strip(); wc = text_utils.count_words_ms_word_style(cleaned)
                if 1 <= wc <= 3: valid_skills.append(f"• {cleaned}")
                else: malformed.append(f"• {cleaned} [Warning: Malformed - {wc} words (expected 1-3)]")
            else: malformed.append(f"• {str(skill).strip()} [Warning: Non-string skill item found]")
        output_lines.extend(valid_skills); output_lines.extend(malformed)
        return "\n\n".join(output_lines)

    def _render_resume_markdown(self, staging_buffer: ImmutableStagingBuffer) -> str:
        """
        Renders the resume to markdown format using the K0-K11 schema.
        Uses the RESUME_RENDER_CONFIG to determine the order and type of sections.
        """
        sections = []
        for section_config in self.RESUME_RENDER_CONFIG:
            section_type = section_config.get("type")
            render_handler = self._RENDER_DISPATCH.get(section_type)
            if render_handler:
                section_content = render_handler(section_config, staging_buffer)
                if section_content and section_content.strip():
                    sections.append(section_content)
            else:
                self.logger.warning(f"Unknown section type: {section_type}")

        return "\n".join(sections)

    def _render_app_tracker(self, file_paths: Dict[str, str], jd_url: str = "") -> Dict:
        # --- PATCH: Access constraints, not artist_config ---
        app_tracker_schema = self.config.validator.app_tracker_schema
        if not app_tracker_schema:
             self.logger.error("App tracker schema not found in config.constraints.app_tracker_schema")
             app_tracker_schema = {} # Fallback
        
        tracker = copy.deepcopy(app_tracker_schema)
        # --- END PATCH ---
        
        candidate_name = self.master_resume.get("owner", {}).get("name", "Candidate").replace(" ", "_")
        tracker['Company'] = self.company_name; tracker['Job Title'] = self.job_title
        tracker['JD URL'] = jd_url; tracker['Application Date'] = datetime.now().strftime("%m/%d/%Y")
        tracker['Base Resume'] = ""; versioned_resume_filename = f"{candidate_name}_Resume_{self._safe_company_name}_{self._safe_job_title}"
        tracker['Versioned Resume'] = versioned_resume_filename; tracker['Pipeline Status'] = 'Applied'
        
        # --- PATCH: Use app_tracker_schema variable ---
        if app_tracker_schema:
             for key in app_tracker_schema.keys():
                  if key not in tracker: tracker[key] = ""
        # --- END PATCH ---
        return tracker
