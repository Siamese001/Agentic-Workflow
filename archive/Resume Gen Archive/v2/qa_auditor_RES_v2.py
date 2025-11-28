# File: qa_auditor_RES_v2.py
# QA Auditor Tool Module - V17 Architecture
# Version: 17.00 (Extracted from validation_RES_v2.py)
# This tool's job is to generate a report (an audit), not to validate content for a GateDecision

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Import dependencies from new modules
from models_RES import (
    ValidationResult, ValidationSeverity, 
    ThematicAnalysis, ImmutableStagingBuffer
)
# --- FIX: (Role Confusion) Import Validator ---
from validator_RES_v2 import AppTrackerQAValidator
import json
# --- END FIX ---

# ==============================================================================
# QA AUDITOR TOOL
# ==============================================================================

class QAReportGenerator:
    """
    Generates comprehensive QA reports for resume workflow output.
    This tool generates a report (an audit) rather than validating content for GateDecisions.
    It is correctly called at the end of the workflow, confirming it's a separate step.
    (Extracted from validation_RES_v2.py lines 2233-2415)
    """

    def __init__(self, orchestrator: 'WorkflowOrchestrator'):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(__name__)

    def generate(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        validation_results: List[ValidationResult],
        file_contents: Dict[str, str],
        job_description: str = ""
    ) -> Tuple[List[ValidationResult], str]:
        """
        Generate QA report from validation results and staging buffer.
        
        Returns:
            Tuple of (validation_results, qa_report_text)
        """
        lines = []
        
        # Header
        lines.append("# QA Report (Simplified)")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Calculate status
        critical_failures = [r for r in validation_results if not r.passed and r.severity == ValidationSeverity.CRITICAL]
        high_failures = [r for r in validation_results if not r.passed and r.severity == ValidationSeverity.HIGH]
        production_ready = len(critical_failures) == 0 and len(high_failures) == 0
        
        overall_status = "PASS" if production_ready else ("WARN" if len(high_failures) > 0 else "FAIL")
        lines.append(f"Overall Status: **{overall_status}**")
        lines.append("")
        
        # Section 1: Production Readiness
        lines.append("## Section 1: Production Readiness & Key Indicators")
        lines.append(f"* Production Ready: **{'YES' if production_ready else 'NO'}**")
        lines.append(f"* Critical Failures: **{len(critical_failures)}**")
        lines.append(f"* High Failures: **{len(high_failures)}**")
        
        # Section 1: Production Readiness (continued)
        jd_keyword_rule = next((r for r in validation_results if r.rule_id == "H5_GLOBAL_JD_KEYWORD_RANGE"), None)
        jd_keywords_found = 0
        kw_pass = False
        if jd_keyword_rule:
            jd_keywords_found = jd_keyword_rule.details.get('found', 0)
            kw_pass = jd_keyword_rule.passed
        lines.append(f"* JD Keyword Count: **{jd_keywords_found}** (Tgt: 7-16) - **{'PASS' if kw_pass else 'FAIL'}** *(Ref: H5_GLOBAL_JD_KEYWORD_RANGE)*")
        
        # JD enforcement gates
        jd_enforcement_results = self.orchestrator.jd_enforcer.enforcement_results if hasattr(self.orchestrator, 'jd_enforcer') else []
        jd_passed = sum(1 for r in jd_enforcement_results if r.passed)
        lines.append(f"* JD Enforcement: **{jd_passed}/{len(jd_enforcement_results)}** Checks Passed")
        
        # API calls
        total_api_calls = sum(c.metadata.get('gemini_api_calls', 0) for c in self.orchestrator.hop_checkpoints)
        lines.append(f"* Total API Calls: **{total_api_calls}**")
        lines.append("")
        
        # Section 2: Critical & High Failures
        lines.append("## Section 2: Critical & High Severity Failures")
        if not critical_failures and not high_failures:
            lines.append("No CRITICAL or HIGH severity failures detected. ✅")
        else:
            if critical_failures:
                lines.append("**CRITICAL:**")
                for r in critical_failures:
                    lines.append(f"* [{r.rule_id}]: {r.message[:100]}")
            if high_failures:
                lines.append("**HIGH:**")
                for r in high_failures:
                    lines.append(f"* [{r.rule_id}]: {r.message[:100]}")
        lines.append("")
    
        # Section 3: Content & Signal Summary
        lines.append("## Section 3: Content & Signal Summary")
        
        lines.append("### Final Generation Temperatures")
        hop3_checkpoint = next((c for c in self.orchestrator.hop_checkpoints if c.hop_id == "HOP-3"), None)
        if hop3_checkpoint and hop3_checkpoint.metadata.get('final_temperatures'):
            temps = hop3_checkpoint.metadata['final_temperatures']
            attempts = hop3_checkpoint.metadata.get('attempts_made', 1)
            lines.append(f"* Generation Attempts: **{attempts}**")
            lines.append("* Section Temperatures:")
            for section_name, temp in sorted(temps.items()):
                lines.append(f"    * {section_name}: **{temp:.1f}**")
            avg_temp = sum(temps.values()) / len(temps) if temps else 0.0
            lines.append(f"* Average Temperature: **{avg_temp:.2f}**")
        else:
            lines.append("* Temperature data not available")
        lines.append("")
        
        lines.append("### Signal & Quality Metrics")
        
        section_signal = next((r for r in validation_results if r.rule_id == "H3_GLOBAL_PER_SECTION_SIGNAL_SCORE"), None)
        lines.append(f"* Per-Section Signal Scores: **{('PASS' if section_signal and section_signal.passed else 'FAIL') if section_signal else 'N/A'}** *(Ref: H3_GLOBAL_PER_SECTION_SIGNAL_SCORE)*")
        
        cl_signal = next((r for r in validation_results if r.rule_id == "H3_K11_COVER_LETTER_RELEVANCE_RANGE"), None)
        lines.append(f"* Cover Letter Signal Score: **{('PASS' if cl_signal and cl_signal.passed else 'FAIL') if cl_signal else 'N/A'}** *(Ref: H3_K11_COVER_LETTER_RELEVANCE_RANGE)*")
        
        cross_sim = next((r for r in validation_results if r.rule_id == "H5_GLOBAL_CROSS_SECTION_SIMILARITY"), None)
        lines.append(f"* Cross-Section Similarity: **{('PASS' if cross_sim and cross_sim.passed else 'FAIL') if cross_sim else 'N/A'}** *(Ref: H5_GLOBAL_CROSS_SECTION_SIMILARITY)*")
        
        cleanliness_rules = ["H5_CONTENT_NO_PLACEHOLDERS", "H5_CONTENT_NO_PROMPT_CONTAMINATION",
                           "H3_GLOBAL_CONTENT_NO_CONVERSATIONAL_FILLERS", "H3_CONTENT_NO_FORBIDDEN_VERBS",
                           "H3_CONTENT_NO_INTRO_PHRASES"]
        cleanliness_results = [r for r in validation_results if r.rule_id in cleanliness_rules]
        all_clean = all(r.passed for r in cleanliness_results) if cleanliness_results else False
        lines.append(f"* Content Cleanliness: **{'PASS' if all_clean else 'FAIL'}**")
        if not all_clean and cleanliness_results:
            failed_types = [r.rule_id.split("_")[-1] for r in cleanliness_results if not r.passed]
            lines.append(f"    * Issues: {', '.join(failed_types)}")
        lines.append("")
        
        # Section 4: Structural & Provenance
        lines.append("## Section 4: Structural & Provenance Summary")
        
        structure_rules = [r for r in validation_results if "STRUCTURE" in r.rule_id and "PRESENT" in r.rule_id]
        all_present = all(r.passed for r in structure_rules) if structure_rules else False
        lines.append(f"* Required Sections Present: **{'PASS' if all_present else 'FAIL'}** *(Ref: H3_KX_STRUCTURE_SECTION_PRESENT)*")
        
        prov_check = next((r for r in validation_results if r.rule_id == "H3_GLOBAL_BULLET_PROVENANCE_SPLIT_CHECK"), None)
        lines.append(f"* Bullet Provenance Splits: **{('PASS' if prov_check and prov_check.passed else 'FAIL') if prov_check else 'N/A'}** *(Ref: H3_GLOBAL_BULLET_PROVENANCE_SPLIT_CHECK)*")
        
        bullet_wc_rules = ["H3_GLOBAL_BULLET_WORD_COUNT_CRITICAL", "H3_GLOBAL_BULLET_WORD_COUNT_HIGH", "H3_GLOBAL_BULLET_WORD_COUNT_MEDIUM", "H3_GLOBAL_BULLET_WORD_COUNT_LOW"]
        bullet_wc_results = [r for r in validation_results if r.rule_id in bullet_wc_rules]
        bullet_wc_pass = all(r.passed for r in bullet_wc_results) if bullet_wc_results else False
        lines.append(f"* Bullet Word Counts: **{'PASS' if bullet_wc_pass else 'FAIL'}** *(Ref: H3_GLOBAL_BULLET_WORD_COUNT_...)*")
        
        headline_rules = ["H3_K0_HEADLINE_WORD_COUNT", "H3_K0_HEADLINE_COMPONENT_WORD_COUNT",
                         "H3_K0_HEADLINE_NO_COMMAS", "H3_K0_HEADLINE_NO_TITLES"]
        headline_results = [r for r in validation_results if r.rule_id in headline_rules]
        headline_pass = all(r.passed for r in headline_results) if headline_results else False
        lines.append(f"* Headline Format: **{'PASS' if headline_pass else 'FAIL'}**")
        
        cl_rules = ["H3_K11_COVER_LETTER_FULL_STRUCTURE", "H3_K11_COVER_LETTER_SIGNATURE_VALID",
                   "H3_K11_COVER_LETTER_STRUCTURE"]
        cl_results = [r for r in validation_results if r.rule_id in cl_rules]
        cl_pass = all(r.passed for r in cl_results) if cl_results else False
        lines.append(f"* Cover Letter Structure: **{'PASS' if cl_pass else 'FAIL'}**")
        
        other_struct = ["H5_STRUCTURE_NO_EMPTY_LIST_ITEMS", "H5_STRUCTURE_MARKDOWN_HEADER_SPACING"]
        other_results = [r for r in validation_results if r.rule_id in other_struct]
        other_pass = all(r.passed for r in other_results) if other_results else False
        lines.append(f"* Other Structural Issues: **{'PASS' if other_pass else 'FAIL'}**")
        lines.append("")
        
        # --- FIX: (Role Confusion) Run App Tracker Validation Here ---
        lines.append("## Section 5: App Tracker Validation")
        app_tracker_content = file_contents.get('app_tracker', '{}')
        app_tracker_validation_results = []
        try:
            app_tracker_data = json.loads(app_tracker_content)
            validator = AppTrackerQAValidator(validator_config=self.orchestrator.config.validator)
            validation_result_dict = validator.validate_tracker_data([app_tracker_data])
            
            if "BLOCKED" in validation_result_dict.get("result", ""):
                errors = validation_result_dict.get('errors', [])
                for error in errors:
                    app_tracker_validation_results.append(ValidationResult(
                        rule_id=f"APP_TRACKER_{error.get('RULE_ID', 'UNKNOWN')}", passed=False,
                        severity=ValidationSeverity.HIGH,
                        message=f"AppTracker Error (Field '{error.get('field')}'): {error.get('message')}",
                        details=error
                    ))
            else:
                app_tracker_validation_results.append(ValidationResult(
                    rule_id="APP_TRACKER_VALIDATION_PASSED", passed=True, severity=ValidationSeverity.INFO,
                    message="AppTracker JSON passed validation rules."
                ))
            
            lines.append(f"* App Tracker Status: **{validation_result_dict.get('result', 'UNKNOWN')}**")
            if errors:
                lines.append(f"* Errors Found: {len(errors)}")
        except Exception as e:
            lines.append(f"* App Tracker Status: **VALIDATION_CRASH**")
            lines.append(f"* Error: {e}")
        lines.append("")
        # --- END FIX ---
        
        # Section 6: Output files
        lines.append("## Section 6: Final Output Format Check (High Level)")
        
        output_checks = {
            "Resume (.md)": "RENDER_RESUME_MD",
            "Skills (.txt)": "RENDER_SKILLS",
            "Cover Letter (.txt)": "RENDER_COVER_LETTER",
            "QA Report (.md)": "QA_REPORT_GENERATION_OVERALL",
            "App Tracker (.json)": "RENDER_APP_TRACKER"
        }
        
        for output_name, rule_id in output_checks.items():
            # Check if the RENDER step passed
            result = next((r for r in validation_results if r.rule_id == rule_id), None)
            if rule_id == "QA_REPORT_GENERATION_OVERALL": # Special check for QA report
                status = 'PASS' # If we got this far, the report *text* exists
            else:
                status = ('PASS' if result and result.passed else 'FAIL') if result else 'N/A'
            lines.append(f"* {output_name}: **{status}**")
        
        qa_report_text = "\n".join(lines)
        
        # Return validation result
        qa_generation_validation_results = []
        qa_generation_validation_results.extend(app_tracker_validation_results) # Add AppTracker results
        qa_generation_validation_results.append(ValidationResult(
            rule_id="QA_REPORT_GENERATION_OVERALL",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Simplified QA Report generated successfully."
        ))
        
        return qa_generation_validation_results, qa_report_text
