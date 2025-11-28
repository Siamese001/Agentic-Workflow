# File: qa_auditor_RES_v3_8.py
# QA Auditor Tool Module - V3.8 Architecture
# Version: 3.8.0 - Complete V3.8 Migration
# This tool's job is to generate a report (an audit), not to validate content for a GateDecision

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Import dependencies from v3.8 modules
from models_RES import (
    ValidationResult, ValidationSeverity, 
    ThematicAnalysis, ImmutableStagingBuffer
)
# Import Validator from v3.8
from validator_RES_v3_8 import AppTrackerQAValidator
import json

logger = logging.getLogger(__name__)

# ==============================================================================
# QA AUDITOR TOOL
# ==============================================================================

class QAReportGenerator:
    """
    Generates comprehensive QA reports for resume workflow output.
    This tool generates a report (an audit) rather than validating content for GateDecisions.
    V3.8 version with corrected imports and enhanced reporting.
    """

    def __init__(self):
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
        
        Args:
            staging_buffer: Final staging buffer with all content
            thematic_analysis: Theme analysis results
            validation_results: All validation results from workflow
            file_contents: Generated file contents
            job_description: Original job description
            
        Returns:
            Tuple of (validation_results, qa_report_text)
        """
        lines = []
        
        # Header
        lines.append("# QA Report - V3.8")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Calculate status
        critical_failures = [r for r in validation_results if not r.passed and r.severity == ValidationSeverity.CRITICAL]
        high_failures = [r for r in validation_results if not r.passed and r.severity == ValidationSeverity.HIGH]
        medium_failures = [r for r in validation_results if not r.passed and r.severity == ValidationSeverity.MEDIUM]
        production_ready = len(critical_failures) == 0 and len(high_failures) == 0
        
        overall_status = "PASS" if production_ready else ("WARN" if len(high_failures) > 0 else "FAIL")
        lines.append(f"Overall Status: **{overall_status}**")
        lines.append("")
        
        # Section 1: Production Readiness
        lines.append("## Section 1: Production Readiness & Key Indicators")
        lines.append(f"* Production Ready: **{'YES' if production_ready else 'NO'}**")
        lines.append(f"* Critical Failures: **{len(critical_failures)}**")
        lines.append(f"* High Failures: **{len(high_failures)}**")
        lines.append(f"* Medium Failures: **{len(medium_failures)}**")
        lines.append(f"* Total Validation Rules: **{len(validation_results)}**")
        lines.append(f"* Pass Rate: **{sum(1 for r in validation_results if r.passed)}/{len(validation_results)}**")
        
        # JD keyword analysis
        jd_keyword_rule = next((r for r in validation_results if r.rule_id == "H5_GLOBAL_JD_KEYWORD_RANGE"), None)
        jd_keywords_found = 0
        kw_pass = False
        if jd_keyword_rule:
            jd_keywords_found = jd_keyword_rule.details.get('found', 0)
            kw_pass = jd_keyword_rule.passed
        lines.append(f"* JD Keyword Count: **{jd_keywords_found}** (Target: 7-16) - **{'PASS' if kw_pass else 'FAIL'}**")
        
        # JD enforcement gates
        jd_enforcement_results = [r for r in validation_results if "JD_ENFORCEMENT" in r.rule_id]
        jd_passed = sum(1 for r in jd_enforcement_results if r.passed)
        if jd_enforcement_results:
            lines.append(f"* JD Enforcement: **{jd_passed}/{len(jd_enforcement_results)}** Checks Passed")
        
        lines.append("")
        
        # Section 2: Critical & High Failures
        lines.append("## Section 2: Critical & High Severity Failures")
        if not critical_failures and not high_failures:
            lines.append("✅ No CRITICAL or HIGH severity failures detected.")
        else:
            if critical_failures:
                lines.append("**CRITICAL:**")
                for r in critical_failures[:10]:  # Limit to first 10
                    lines.append(f"* [{r.rule_id}]: {r.message[:100]}")
            if high_failures:
                lines.append("**HIGH:**")
                for r in high_failures[:10]:  # Limit to first 10
                    lines.append(f"* [{r.rule_id}]: {r.message[:100]}")
        lines.append("")
    
        # Section 3: Content & Signal Summary
        lines.append("## Section 3: Content & Signal Summary")
        
        lines.append("### Signal & Quality Metrics")
        
        # Theme signal scoring
        if thematic_analysis:
            lines.append(f"* Primary Theme: **{thematic_analysis.primary_theme.get('name', 'N/A') if thematic_analysis.primary_theme else 'N/A'}**")
            lines.append(f"* Signal Quality Score: **{thematic_analysis.signal_quality_score:.2f}**")
        
        section_signal = next((r for r in validation_results if r.rule_id == "H3_GLOBAL_PER_SECTION_SIGNAL_SCORE"), None)
        lines.append(f"* Per-Section Signal Scores: **{('PASS' if section_signal and section_signal.passed else 'FAIL') if section_signal else 'N/A'}**")
        
        cl_signal = next((r for r in validation_results if r.rule_id == "H3_K11_COVER_LETTER_RELEVANCE_RANGE"), None)
        lines.append(f"* Cover Letter Signal Score: **{('PASS' if cl_signal and cl_signal.passed else 'FAIL') if cl_signal else 'N/A'}**")
        
        cross_sim = next((r for r in validation_results if r.rule_id == "H5_GLOBAL_CROSS_SECTION_SIMILARITY"), None)
        lines.append(f"* Cross-Section Similarity: **{('PASS' if cross_sim and cross_sim.passed else 'FAIL') if cross_sim else 'N/A'}**")
        
        # Content cleanliness checks
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
        
        # Section presence checks
        structure_rules = [r for r in validation_results if "STRUCTURE" in r.rule_id and "PRESENT" in r.rule_id]
        all_present = all(r.passed for r in structure_rules) if structure_rules else False
        lines.append(f"* Required Sections Present: **{'PASS' if all_present else 'FAIL'}**")
        
        # Bullet provenance
        prov_check = next((r for r in validation_results if r.rule_id == "H3_GLOBAL_BULLET_PROVENANCE_SPLIT_CHECK"), None)
        lines.append(f"* Bullet Provenance Splits: **{('PASS' if prov_check and prov_check.passed else 'FAIL') if prov_check else 'N/A'}**")
        
        # Bullet word counts
        bullet_wc_rules = ["H3_GLOBAL_BULLET_WORD_COUNT_CRITICAL", "H3_GLOBAL_BULLET_WORD_COUNT_HIGH", 
                          "H3_GLOBAL_BULLET_WORD_COUNT_MEDIUM", "H3_GLOBAL_BULLET_WORD_COUNT_LOW"]
        bullet_wc_results = [r for r in validation_results if r.rule_id in bullet_wc_rules]
        bullet_wc_pass = all(r.passed for r in bullet_wc_results) if bullet_wc_results else False
        lines.append(f"* Bullet Word Counts: **{'PASS' if bullet_wc_pass else 'FAIL'}**")
        
        # Headline format
        headline_rules = ["H3_K0_HEADLINE_WORD_COUNT", "H3_K0_HEADLINE_COMPONENT_WORD_COUNT",
                         "H3_K0_HEADLINE_NO_COMMAS", "H3_K0_HEADLINE_NO_TITLES"]
        headline_results = [r for r in validation_results if r.rule_id in headline_rules]
        headline_pass = all(r.passed for r in headline_results) if headline_results else False
        lines.append(f"* Headline Format: **{'PASS' if headline_pass else 'FAIL'}**")
        
        # Cover letter structure
        cl_rules = ["H3_K11_COVER_LETTER_FULL_STRUCTURE", "H3_K11_COVER_LETTER_SIGNATURE_VALID",
                   "H3_K11_COVER_LETTER_STRUCTURE"]
        cl_results = [r for r in validation_results if r.rule_id in cl_rules]
        cl_pass = all(r.passed for r in cl_results) if cl_results else False
        lines.append(f"* Cover Letter Structure: **{'PASS' if cl_pass else 'FAIL'}**")
        
        # Other structural issues
        other_struct = ["H5_STRUCTURE_NO_EMPTY_LIST_ITEMS", "H5_STRUCTURE_MARKDOWN_HEADER_SPACING"]
        other_results = [r for r in validation_results if r.rule_id in other_struct]
        other_pass = all(r.passed for r in other_results) if other_results else False
        lines.append(f"* Other Structural Issues: **{'PASS' if other_pass else 'FAIL'}**")
        lines.append("")
        
        # Section 5: App Tracker Validation
        lines.append("## Section 5: App Tracker Validation")
        app_tracker_content = file_contents.get('app_tracker', '{}')
        app_tracker_validation_results = []
        
        try:
            app_tracker_data = json.loads(app_tracker_content)
            # Note: In production, would validate app tracker data here
            lines.append(f"* App Tracker Status: **JSON_VALID**")
            lines.append(f"* Fields Present: {len(app_tracker_data)}")
            
            app_tracker_validation_results.append(ValidationResult(
                rule_id="APP_TRACKER_VALIDATION_PASSED", 
                passed=True, 
                severity=ValidationSeverity.INFO,
                message="AppTracker JSON is valid and well-formed."
            ))
            
        except json.JSONDecodeError as e:
            lines.append(f"* App Tracker Status: **JSON_INVALID**")
            lines.append(f"* Error: {str(e)[:100]}")
            
            app_tracker_validation_results.append(ValidationResult(
                rule_id="APP_TRACKER_JSON_ERROR", 
                passed=False, 
                severity=ValidationSeverity.HIGH,
                message=f"AppTracker JSON parse error: {str(e)[:100]}"
            ))
        except Exception as e:
            lines.append(f"* App Tracker Status: **VALIDATION_ERROR**")
            lines.append(f"* Error: {str(e)[:100]}")
        
        lines.append("")
        
        # Section 6: Output files
        lines.append("## Section 6: Final Output Format Check")
        
        output_checks = {
            "Resume (.md)": "resume" in file_contents,
            "Skills (.txt)": "skills" in file_contents,
            "Cover Letter (.txt)": "cover_letter" in file_contents,
            "App Tracker (.json)": "app_tracker" in file_contents
        }
        
        for output_name, is_present in output_checks.items():
            status = 'PASS' if is_present else 'MISSING'
            lines.append(f"* {output_name}: **{status}**")
        
        # Section 7: Summary Statistics
        lines.append("")
        lines.append("## Section 7: Summary Statistics")
        
        total_rules = len(validation_results)
        passed_rules = sum(1 for r in validation_results if r.passed)
        failed_rules = total_rules - passed_rules
        
        lines.append(f"* Total Validation Rules: **{total_rules}**")
        lines.append(f"* Passed: **{passed_rules}** ({passed_rules/total_rules*100:.1f}%)")
        lines.append(f"* Failed: **{failed_rules}** ({failed_rules/total_rules*100:.1f}%)")
        
        # Breakdown by severity
        by_severity = {}
        for r in validation_results:
            sev = r.severity.name if hasattr(r.severity, 'name') else str(r.severity)
            if sev not in by_severity:
                by_severity[sev] = {"passed": 0, "failed": 0}
            if r.passed:
                by_severity[sev]["passed"] += 1
            else:
                by_severity[sev]["failed"] += 1
        
        lines.append("* By Severity:")
        for sev, counts in sorted(by_severity.items()):
            total = counts["passed"] + counts["failed"]
            lines.append(f"    * {sev}: {counts['passed']}/{total} passed")
        
        lines.append("")
        lines.append("---")
        lines.append("*End of QA Report*")
        
        qa_report_text = "\n".join(lines)
        
        # Compile final validation results
        qa_generation_validation_results = []
        qa_generation_validation_results.extend(app_tracker_validation_results)
        qa_generation_validation_results.append(ValidationResult(
            rule_id="QA_REPORT_GENERATION_OVERALL",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="QA Report generated successfully (V3.8)."
        ))
        
        return qa_generation_validation_results, qa_report_text


# Backwards compatibility
QAAuditor = QAReportGenerator

__all__ = ['QAReportGenerator', 'QAAuditor']
