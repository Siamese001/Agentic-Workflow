# File: validation/external.py
# External Validators Module - V18 Architecture
# Version: 18.00
# Contains validation classes that are external-facing or have side effects.
# Refactored from validator_RES_v2.py

import logging
import re
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from models_RES import JDEnforcementRule, JDEnforcementResult
from config_RES_v2 import CONFIG

# Mock indicators (from monolithic file)
mock_indicators = {
    "mock", "test", "dummy", "example", "sample",
    "[placeholder", "[your name]", "[company name]",
    "[missing_context]", "[unserializable"
}

class JDEnforcementValidator:
    """
    Tracks and validates the flow of JD-specific data through the workflow.
    This is not a simple validator; it's a separate, long-running agent that monitors 
    JD compliance across the entire workflow lifecycle.
    (Extracted from validation_RES_v2.py lines 152-523)
    """
    def __init__(self, job_description: str = '', logger = None):
        self.enforcement_results: List[JDEnforcementResult] = []
        self.jd_hash: Optional[str] = None
        self.jd_keywords: List[str] = []
        self.job_description = job_description
        self.logger = logger

    def _check_mock_data(self, data: Any, gate_id: str, rule: JDEnforcementRule) -> JDEnforcementResult:
        data_str = str(data).lower()
        has_mock = any(indicator in data_str for indicator in mock_indicators)
        return JDEnforcementResult(
            rule,
            not has_mock,
            f"No mock data indicators found in {rule.name}" if not has_mock else f"Mock data indicators found in {rule.name}",
            gate_id
        )

    def _check_jd_keywords(self, data: Any, gate_id: str, rule: JDEnforcementRule, min_count: int) -> JDEnforcementResult:
        if not self.jd_keywords:
            return JDEnforcementResult(rule, False, "JD keywords list is empty, cannot check", gate_id)
        
        data_str = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
        data_str = data_str.lower()
        keywords_found = [kw for kw in self.jd_keywords[:15] if kw.lower() in data_str]
        
        passed = len(keywords_found) >= min_count
        return JDEnforcementResult(
            rule,
            passed,
            f"Found {len(keywords_found)} JD keywords in {rule.name} (>= {min_count})" if passed else f"Found only {len(keywords_found)} JD keywords in {rule.name} (< {min_count})",
            gate_id
        )

    def validate_jd_input(self, job_description: str, gate_id: str) -> List[JDEnforcementResult]:
        results = []

        if len(job_description) >= 100:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E1_JD_MIN_LENGTH,
                True,
                f"JD length: {len(job_description)} chars",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E1_JD_MIN_LENGTH,
                False,
                f"JD too short: {len(job_description)} chars < 100 minimum",
                gate_id
            ))

        if job_description and job_description.strip():
            results.append(JDEnforcementResult(
                JDEnforcementRule.E2_JD_NON_NULL,
                True,
                "JD is non-null and non-empty",
                gate_id
            ))

            self.jd_hash = hashlib.sha256(job_description.encode()).hexdigest()[:16]
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E2_JD_NON_NULL,
                False,
                "JD is null or empty",
                gate_id
            ))

        results.append(JDEnforcementResult(
            JDEnforcementRule.E3_JD_PARSING_SUCCESS,
            True,
            "JD input is valid for parsing",
            gate_id
        ))

        self.enforcement_results.extend(results)
        return results

    def validate_jd_parsing(self, parsed_jd: Dict, gate_id: str) -> List[JDEnforcementResult]:
        results = []

        if parsed_jd and isinstance(parsed_jd, dict):
            results.append(JDEnforcementResult(
                JDEnforcementRule.E3_JD_PARSING_SUCCESS,
                True,
                f"JD parsed with {len(parsed_jd)} fields",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E3_JD_PARSING_SUCCESS,
                False,
                "JD parsing failed or returned non-dict",
                gate_id
            ))

        primary_theme = parsed_jd.get("primary_theme", "")
        secondary_themes = parsed_jd.get("secondary_themes", [])

        if primary_theme and secondary_themes:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E4_THEMES_EXTRACTED,
                True,
                f"Primary theme + {len(secondary_themes)} secondary themes",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E4_THEMES_EXTRACTED,
                False,
                f"Missing themes: primary={bool(primary_theme)}, secondary={len(secondary_themes)}",
                gate_id
            ))

        required_skills = parsed_jd.get("required_skills", [])
        if len(required_skills) >= 5:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E5_SKILLS_EXTRACTED,
                True,
                f"Extracted {len(required_skills)} skills",
                gate_id
            ))
            self.jd_keywords.extend(required_skills)
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E5_SKILLS_EXTRACTED,
                False,
                f"Insufficient skills: {len(required_skills)} < 5 minimum",
                gate_id
            ))

        self.enforcement_results.extend(results)
        return results

    def validate_thematic_analysis(self, thematic_analysis: Any, gate_id: str) -> List[JDEnforcementResult]:
        results = []

        if thematic_analysis and hasattr(thematic_analysis, 'primary_theme'):
            results.append(JDEnforcementResult(
                JDEnforcementRule.E6_JD_TO_THEMATIC,
                True,
                "ThematicAnalysis created from JD",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E6_JD_TO_THEMATIC,
                False,
                "ThematicAnalysis missing or invalid",
                gate_id
            ))

        if thematic_analysis:
            thematic_str = str(thematic_analysis).lower()
            has_mock = any(indicator in thematic_str for indicator in mock_indicators)

            if not has_mock:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E7_THEMATIC_USES_JD,
                    True,
                    "ThematicAnalysis contains no mock data indicators",
                    gate_id
                ))
            else:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E7_THEMATIC_USES_JD,
                    False,
                    "ThematicAnalysis may contain mock data",
                    gate_id
                ))

        self.enforcement_results.extend(results)
        return results

    def validate_enrichment(self, enriched_data: Dict, gate_id: str) -> List[JDEnforcementResult]:
        results = []
        if enriched_data and isinstance(enriched_data, dict):
            enriched_str = json.dumps(enriched_data).lower()
            keywords_found = [kw for kw in self.jd_keywords[:10] if kw.lower() in enriched_str]

            if keywords_found:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E10_ENRICHMENT_USES_JD,
                    True,
                    f"Found {len(keywords_found)} JD keywords in enriched data",
                    gate_id
                ))
            else:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E10_ENRICHMENT_USES_JD,
                    False,
                    "No JD keywords found in enriched data",
                    gate_id
                ))

        if enriched_data:
            enriched_str = str(enriched_data).lower()
            has_mock = any(indicator in enriched_str for indicator in mock_indicators)

            if not has_mock:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E14_NO_MOCK_DATA,
                    True,
                    "No mock data in enrichment",
                    gate_id
                ))
            else:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E14_NO_MOCK_DATA,
                    False,
                    "Mock data indicators found in enrichment",
                    gate_id
                ))

        self.enforcement_results.extend(results)
        return results

    def validate_artist_inputs(self, enriched_scaffold: Dict, thematic_analysis: Any, gate_id: str) -> List[JDEnforcementResult]:
        results = []

        if thematic_analysis:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E8_ARTIST_RECEIVES_JD,
                True,
                "Artist received JD-derived thematic_analysis",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E8_ARTIST_RECEIVES_JD,
                False,
                "Artist did not receive thematic_analysis",
                gate_id
            ))

        if enriched_scaffold and isinstance(enriched_scaffold, dict):
            enriched_str = json.dumps(enriched_scaffold).lower()
            keywords_found = [kw for kw in self.jd_keywords[:10] if kw.lower() in enriched_str]
            results.append(JDEnforcementResult(
                JDEnforcementRule.E10_ENRICHMENT_USES_JD, bool(keywords_found), f"Found {len(keywords_found)} JD keywords in enriched data provided to Artist", gate_id
            ))

        self.enforcement_results.extend(results)
        return results

    def validate_preflight(self, staging_buffer: Any, gate_id: str) -> List[JDEnforcementResult]:
        results = []
        if staging_buffer and hasattr(staging_buffer, '_data'):
            buffer_str = json.dumps(staging_buffer._data).lower()
            keywords_found = [kw for kw in self.jd_keywords[:15] if kw.lower() in buffer_str]

            if keywords_found:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E11_VALIDATION_CHECKS_JD,
                    True,
                    f"Validation found {len(keywords_found)} JD keywords",
                    gate_id
                ))
            else:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E11_VALIDATION_CHECKS_JD,
                    False,
                    "Validation found no JD keywords",
                    gate_id
                ))

        if staging_buffer and hasattr(staging_buffer, '_data'):
            buffer_str = json.dumps(staging_buffer._data).lower()
            keywords_found_final = [kw for kw in self.jd_keywords[:15] if kw.lower() in buffer_str]

            if len(keywords_found_final) >= 3:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E9_CONTENT_HAS_JD_KW,
                    True,
                    f"Pre-flight check found {len(keywords_found_final)} JD keywords in final buffer",
                    gate_id
                ))
            else:
                results.append(JDEnforcementResult(
                    JDEnforcementRule.E9_CONTENT_HAS_JD_KW,
                    False,
                    f"Pre-flight check found only {len(keywords_found_final)} JD keywords in final buffer",
                    gate_id
                ))

        if staging_buffer and hasattr(staging_buffer, '_data'):
            buffer_str = str(staging_buffer._data).lower()
            has_mock = any(indicator in buffer_str for indicator in mock_indicators)
            results.append(JDEnforcementResult(
                JDEnforcementRule.E14_NO_MOCK_DATA, not has_mock,
                "No mock data indicators found in final staging buffer" if not has_mock else "Mock data indicators found in final staging buffer",
                gate_id
            ))

        self.enforcement_results.extend(results)
        return results

    def validate_file_output(self, file_paths: Dict, gate_id: str) -> List[JDEnforcementResult]:
        results = []
        if file_paths:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E12_FILES_CONTAIN_JD,
                True,
                f"{len(file_paths)} files generated (assumed to contain JD content)",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E12_FILES_CONTAIN_JD,
                False,
                "No files generated",
                gate_id
            ))

        if file_paths:
            paths_str = "".join(file_paths.values()).lower()
            has_mock = any(indicator in paths_str for indicator in mock_indicators)
            results.append(JDEnforcementResult(
                JDEnforcementRule.E14_NO_MOCK_DATA,
                not has_mock,
                "No mock data indicators found in file paths" if not has_mock else "Mock data indicators found in file paths",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(JDEnforcementRule.E14_NO_MOCK_DATA, True, "No files to check for mock data", gate_id))

        self.enforcement_results.extend(results)
        return results

    def validate_qa_report(self, qa_report: Dict, gate_id: str) -> List[JDEnforcementResult]:
        results = []
        if qa_report:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E13_QA_VERIFIES_JD,
                True,
                "QA report generated",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E13_QA_VERIFIES_JD,
                False,
                "QA report missing",
                gate_id
            ))

        total_enforcements = len(self.enforcement_results)
        passed_enforcements = sum(1 for r in self.enforcement_results if r.passed)

        if total_enforcements >= 15:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E15_COMPLETE_AUDIT,
                True,
                f"Complete audit: {passed_enforcements}/{total_enforcements} enforcements passed",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E15_COMPLETE_AUDIT,
                False,
                f"Incomplete audit: {total_enforcements} checks < 15 enforcements",
                gate_id
            ))

        self.enforcement_results.extend(results)
        return results
-e 
# ==============================================================================
# APP TRACKER VALIDATOR (MOVED FROM app_tracker_RES_v2.py)
# ==============================================================================
class AppTrackerQAValidator:
    """
    Validates the data for the app_tracker.json file against its schema.
    This is a specialized schema validation tool that should be separate 
    from resume content validation.
    (Extracted from validation_RES_v2.py lines 528-708)
    """
    def __init__(self, run_sha: str = "", actor_id: str = "", validator_config: Any = None):
        if validator_config is None:
            # --- FIX: Load config from the global CONFIG object ---
            validator_config = CONFIG.validator
        
        # Get app tracker schema from validator_config
        self.SCHEMA_FIELDS_V4 = list(validator_config.app_tracker_schema.keys()) if validator_config.app_tracker_schema else []
        if not self.SCHEMA_FIELDS_V4:
            logging.error("CRITICAL: app_tracker_schema is empty or failed to load. Cannot initialize AppTrackerQAValidator schema.")
        
        self.PIPELINE_STATUS_ENUM = validator_config.pipeline_status_enum
        
        self.errors = []
        self.run_sha = run_sha or self._generate_sha()
        self.actor_id = actor_id or "system"
        self.timestamp = datetime.now().isoformat()
        self.rule_pass_counts = {}
        self.rule_fail_counts = {}

    def _validate_string_field(self, idx: int, row: Dict, field: str, rule_id: str, error_name: str, min_length: int):
        value = row.get(field, "").strip()
        if not value:
            self._log_fail(rule_id, idx, field, f"{error_name} name cannot be empty.", f"Provide valid {error_name.lower()} name.")
        elif len(value) < min_length:
            self._log_fail(rule_id, idx, field, f"{error_name} name too short", f"Provide valid {error_name.lower()} name ({min_length}+ chars)")
        else:
            self._log_pass(rule_id)

    def _generate_sha(self) -> str:
        """Generates a simple SHA for the run."""
        return hashlib.sha256(f"{datetime.now().isoformat()}".encode()).hexdigest()[:12]

    def _log_pass(self, rule_id: str):
        """Logs a passed rule check."""
        self.rule_pass_counts[rule_id] = self.rule_pass_counts.get(rule_id, 0) + 1

    def _log_fail(self, rule_id: str, row_idx: int, field: str, message: str, fix: str = ""):
        """Logs a failed rule check."""
        self.rule_fail_counts[rule_id] = self.rule_fail_counts.get(rule_id, 0) + 1
        self.errors.append({
            "row_index": row_idx,
            "field": field,
            "RULE_ID": rule_id,
            "message": message,
            "suggested_fix": fix
        })

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parses a date string in MM/DD/YYYY format."""
        if not date_str or not date_str.strip():
            return None
        try:
            return datetime.strptime(date_str.strip(), "%m/%d/%Y")
        except ValueError:
            return None

    def _is_valid_url(self, url: str) -> bool:
        """Validates a URL format."""
        if not url or not url.strip():
            return True
        url_pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
        return bool(re.match(url_pattern, url.strip()))

    def validate_tracker_data(self, tracker_rows: List[Dict]) -> Dict:
        """Validates a list of app tracker rows."""
        for idx, row in enumerate(tracker_rows):
            if list(row.keys()) != self.SCHEMA_FIELDS_V4:
                self._log_fail("R1", idx, "schema",
                              f"Schema fields mismatch at row {idx}",
                              f"Ensure exactly {len(self.SCHEMA_FIELDS_V4)} fields in correct order")
            else:
                self._log_pass("R1S")

        for idx, row in enumerate(tracker_rows):
            self._validate_row(idx, row)

        logger = logging.getLogger(__name__)
        checked_rules = list(self.rule_pass_counts.keys()) + list(self.rule_fail_counts.keys())
        logger.info(f"AppTracker Validation: Checked rules for populated fields: {sorted(list(set(checked_rules)))}")

        if self.errors:
            return self._generate_blocked_outcome()
        else:
            return self._generate_passed_outcome(tracker_rows)

    def _validate_row(self, idx: int, row: Dict):
        """Validates a single row of app tracker data."""
        status = row.get("Pipeline Status", "").strip()
        if status and status not in self.PIPELINE_STATUS_ENUM:
            self._log_fail("R2", idx, "Pipeline Status",
                          f"Invalid status '{status}'",
                          f"Use one of: {', '.join(self.PIPELINE_STATUS_ENUM)}")
        elif not status:
             self._log_fail("R2", idx, "Pipeline Status", "Pipeline Status cannot be empty.", "Should be 'Applied'.")
        else:
            self._log_pass("R2")

        jd_url = row.get("JD URL", "").strip()
        app_date = row.get("Application Date", "").strip()

        if app_date:
            if not self._parse_date(app_date):
                 self._log_fail("R11", idx, "Application Date",
                               f"Invalid date format '{app_date}'",
                               "Use MM/DD/YYYY format")
            else:
                 self._log_pass("R11")
        else:
             self._log_fail("R11", idx, "Application Date", "Application Date cannot be empty.", "Use MM/DD/YYYY format.")

        if jd_url:
            if not app_date:
                self._log_fail("R10", idx, "Application Date",
                              "Application Date required when JD URL present",
                              "Add valid MM/DD/YYYY date")
            elif self._parse_date(app_date):
                self._log_pass("R10")

        if jd_url:
            if not self._is_valid_url(jd_url):
                self._log_fail("R17", idx, "JD URL",
                              f"Invalid URL format: '{jd_url}'",
                              "Provide valid HTTP/HTTPS URL")
            else:
                self._log_pass("R17")
        else:
            self._log_pass("R17")

        versioned_resume = row.get("Versioned Resume", "").strip()
        if versioned_resume:
            filename_pattern = r'^[A-Za-z0-9_\-]+(\.(md|pdf|docx|doc))?$'
            if not re.match(filename_pattern, versioned_resume):
                self._log_fail("R20", idx, "Versioned Resume",
                              f"Invalid filename format: '{versioned_resume}'",
                              "Use format: Name_Resume_Company_Title (alphanumeric, underscores, hyphens only)")
            else:
                self._log_pass("R20")
        else:
             self._validate_string_field(idx, row, "Versioned Resume", "R20", "Versioned Resume filename", min_length=1)

        self._validate_string_field(idx, row, "Company", "R21", "Company", min_length=2)
        self._validate_string_field(idx, row, "Job Title", "R22", "Job Title", min_length=3)

    def _generate_passed_outcome(self, tracker_rows: List[Dict]) -> Dict:
        """Generates the result dictionary for a successful validation."""
        status_counts = {}

        for row in tracker_rows:
            status = row.get("Pipeline Status", "").strip() or "Unknown"
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "result": "PASSED",
            "counts_by_rule": self.rule_pass_counts,
            "totals_by_status": status_counts,
            "run_sha": self.run_sha,
            "actor_id": self.actor_id,
            "timestamp": self.timestamp
        }

    def _generate_blocked_outcome(self) -> Dict:
        """Generates the result dictionary for a failed validation."""
        failure_histogram = {}
        for error in self.errors:
            rule_id = error["RULE_ID"]
            failure_histogram[rule_id] = failure_histogram.get(rule_id, 0) + 1

        return {
            "result": "BLOCKED",
            "errors": self.errors,
            "failure_histogram_by_rule": failure_histogram,
            "run_sha": self.run_sha,
            "actor_id": self.actor_id,
            "timestamp": self.timestamp
        }
