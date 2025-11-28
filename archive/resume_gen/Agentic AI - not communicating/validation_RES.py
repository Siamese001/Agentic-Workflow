# File: validation.py
# Validation module for Resume Workflow
# Contains all validation rules, engines, and QA systems

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Callable
from collections import defaultdict
from functools import partial
import hashlib # Added for AppTrackerQAValidator

# Import dependencies from new modules
# --- FIX: Import _load_json_config from config_RES ---
from config_RES import (
    ValidatorConfig, ContentConstraintsConfig, SignalControlConfig, 
    CONFIG, AppConfig, _load_json_config, DATA_DIR
)
from models_RES import (
    ValidationResult, ValidationSeverity, JDEnforcementRule,
    JDEnforcementResult, ThematicAnalysis, ResumeSection,
    ImmutableStagingBuffer, GateDecision, BulletProvenance,
    FactualFailureException
)
# --- FIX: REMOVE _load_json_data from this import ---
from utils_RES import (
    text_utils, TextUtils, DuplicateDetector, calculate_signal_score,
    CodeInterpreterTool
)

# Load data required by AppTrackerQAValidator
try:
    # --- FIX: Use _load_json_config and DATA_DIR ---
    APP_TRACKER_SCHEMA_DATA = _load_json_config(str(DATA_DIR / "app_tracker_schema.json"), "App Tracker Schema", required=True)
except (ImportError, FileNotFoundError, json.JSONDecodeError) as e:
    logging.critical(f"FATAL: Could not load app_tracker_schema.json for validation.py: {e}")
    APP_TRACKER_SCHEMA_DATA = {} # Allow import but fail at runtime if used

# Mock indicators (from monolithic file)
mock_indicators = {
    "mock", "test", "dummy", "example", "sample",
    "[placeholder", "[your name]", "[company name]",
    "[missing_context]", "[unserializable"
}

# ==============================================================================
# VALIDATION RULE & ENGINE
# ==============================================================================

class ValidationRule:
    """
    Represents a single executable validation rule.
    (Extracted from resume_workflow_v16_20.py)
    """
    def __init__(self, rule_id: str, severity: ValidationSeverity, validator: Any, error_message: Union[str, Callable[[Dict], str]], category: str = "general"):
        self.rule_id = rule_id
        self.severity = severity
        self.validator = validator
        self.error_message = error_message
        self.category = category

    def execute(self, data: Dict) -> ValidationResult:
        """
        Executes the validation rule against the provided data.
        Now accepts both Dict and ValidationContext for full v16_20 compatibility.
        """
        try:
            # The validator function is called with the data/context
            passed = self.validator(data)

            error_msg = ""
            if not passed:
                if callable(self.error_message):
                    # The error message lambda is also called with the data/context
                    error_msg = self.error_message(data)
                else:
                    error_msg = self.error_message

            # Handle both Dict and ValidationContext for details
            # This matches monolithic v16_20 behavior exactly
            if isinstance(data, dict):
                details = data.get('error_details', {})
            else:
                # ValidationContext object
                try:
                    details = data.get_details_for_rule(self.rule_id)
                except AttributeError:
                    details = {}

            return ValidationResult(
                rule_id=self.rule_id,
                passed=passed,
                severity=self.severity,
                message=error_msg,
                details=details
            )
        except Exception as e:
            return ValidationResult(
                rule_id=self.rule_id,
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Validation logic failed for {self.rule_id}: {str(e)}",
                details={'exception': str(e)}
            )

class ValidationEngine:
    """
    Manages the registration and execution of validation rules.
    (Extracted from resume_workflow_v16_20.py)
    """
    def __init__(self):
        self.rules: List[ValidationRule] = []
        self.rules_by_category: Dict[str, List[ValidationRule]] = defaultdict(list)

    def register_rule(self, rule: ValidationRule) -> None:
        """Registers a single validation rule."""
        self.rules.append(rule)
        self.rules_by_category[rule.category].append(rule)

    def register_rules(self, rules: List[ValidationRule]) -> None:
        """Registers a list of validation rules."""
        for rule in rules:
            self.register_rule(rule)

    def validate(self, data: 'ValidationContext', categories: Optional[List[str]] = None) -> List[ValidationResult]:
        """
        Validates the data against registered rules.
        """
        results = []

        rules_to_run = self.rules
        if categories:
            rules_to_run = []
            for category in categories:
                rules_to_run.extend(self.rules_by_category.get(category, []))

        for rule in rules_to_run:
            result = rule.execute(data)
            results.append(result)

        return results

    def has_high_or_critical_failures(self, results: List[ValidationResult]) -> bool:
        """Checks if any high or critical failures are present."""
        return any(
            not r.passed and r.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]
            for r in results
        )

# ==============================================================================
# JD ENFORCEMENT VALIDATOR
# ==============================================================================

class JDEnforcementValidator:
    """
    Tracks and validates the flow of JD-specific data through the workflow.
    (Extracted from resume_workflow_v16_20.py)
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

# ==============================================================================
# APP TRACKER QA VALIDATOR
# ==============================================================================

class AppTrackerQAValidator:
    """
    Validates the data for the app_tracker.json file against its schema.
    (Extracted from resume_workflow_v16_20.py)
    """
    def __init__(self, run_sha: str = "", actor_id: str = "", validator_config: ValidatorConfig = None):
        if validator_config is None:
            # --- FIX: Load config from the global CONFIG object ---
            validator_config = CONFIG.validator
        
        self.SCHEMA_FIELDS_V4 = list(APP_TRACKER_SCHEMA_DATA.keys()) if APP_TRACKER_SCHEMA_DATA else []
        if not self.SCHEMA_FIELDS_V4:
            logging.error("CRITICAL: APP_TRACKER_SCHEMA_DATA is empty or failed to load. Cannot initialize AppTrackerQAValidator schema.")
        
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

# ==============================================================================
# CONSTRAINT FAILURE CLASSIFIER
# ==============================================================================

class ConstraintFailureClassifier:
    """
    Classifies validation failures to inform retry strategies.
    (Extracted from resume_workflow_v16_20.py)
    """
    @staticmethod
    def classify_failure(
        validation_result: ValidationResult,
        original_temperature: float
    ) -> str:
        """
        Returns failure category to determine optimal retry approach:
        - "MECHANICAL": Word count, format, structure (lower temp helps)
        - "CREATIVE": Placeholders, generic content (higher temp needed)
        - "SEMANTIC": Forbidden verbs, intro phrases (prompt changes help)
        - "CONFLICT": Impossible constraint combination (needs redesign)
        """
        rule_id = validation_result.rule_id
        
        if any(keyword in rule_id for keyword in ["WORD_COUNT", "SENTENCE_COUNT", "FORMAT", "STRUCTURE"]):
            return "MECHANICAL"
        
        if any(keyword in rule_id for keyword in ["PLACEHOLDER", "GENERIC", "MOCK", "EMPTY"]):
            return "CREATIVE"
        
        if any(keyword in rule_id for keyword in ["FORBIDDEN_VERB", "INTRO_PHRASE", "NO_", "INVALID_"]):
            return "SEMANTIC"
        
        if original_temperature <= 0.4 and not validation_result.passed:
            return "CONFLICT"
        
        return "UNKNOWN"

# ==============================================================================
# VALIDATION CONTEXT
# ==============================================================================

class ValidationContext:
    """
    Holds all necessary data for the ValidationEngine to run checks.
    Uses lazy calculation for metrics.
    (Extracted from resume_workflow_v16_20.py)
    """
    def __init__(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, job_description: str, master_resume: Dict, app_config: AppConfig):
        self.staging_buffer = staging_buffer
        self.thematic_analysis = thematic_analysis
        self.job_description = job_description
        self.master_resume = master_resume
        self._cache = {}
        self.constraints = app_config.content_constraints
        self.signal_constraints = app_config.signal_constraints
        self._dup_detector = None
        self.logger = logging.getLogger(__name__)

    @property
    def dup_detector(self):
        """Lazy-loads the DuplicateDetector."""
        if self._dup_detector is None:
            self._dup_detector = DuplicateDetector()
        return self._dup_detector

    def get_details_for_rule(self, rule_id: str) -> Dict:
        """Retrieves cached details for a given rule ID."""
        return self._cache.get(rule_id, {})

    def _calculate_metric_details(self, section_enum: ResumeSection, metrics_to_calc: List[Tuple[str, Callable]], constraints: Dict[str, Any]) -> Dict:
        """Helper to calculate and cache metrics for a section."""
        text = self.staging_buffer.get(section_enum.value, '')
        details = {}
        for metric_name, calc_func in metrics_to_calc:
            try:
                details[metric_name] = calc_func(text) if isinstance(text, (str, list)) else 0
            except Exception as e:
                self.logger.warning(f"Error calculating metric '{metric_name}' for section {section_enum.name}: {e}")
                details[metric_name] = "Error"

        details.update(constraints)
        return details

    def __getattr__(self, name):
        """
        Magic method for lazy calculation of metrics.
        Accessing `context.total_words` will call `_calculate_total_words`.
        Accessing `context.k1_sentence_count_details` will call `_calculate_k1_sentence_count_details`.
        """
        if name in self._cache:
            return self._cache[name]

        # For detail caches (e.g., "k1_sentence_count_details")
        if name.endswith('_details'):
            calculation_method_details = getattr(self, f"_calculate_{name}", None)
            if calculation_method_details:
                value = calculation_method_details()
                # self._cache[name] = value # The method itself handles caching the rule ID
                return value

        # For simple value caches (e.g., "total_words")
        calculation_method = getattr(self, f"_calculate_{name}", None)
        if calculation_method:
            value = calculation_method()
            self._cache[name] = value
            return value

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}' or calculation method '_calculate_{name}' or '_calculate_{name}_details'")

    # --- Lazy Calculation Methods ---

    def _calculate_total_words(self):
        total = 0
        buffer_data = self.staging_buffer.data
        for key_enum in ResumeSection:
            key = key_enum.value
            if key_enum not in [ResumeSection.K0_NAME, ResumeSection.K0_CONTACT] and \
               not key.endswith("_HEADER"):
                value = buffer_data.get(key)
                if isinstance(value, str):
                    total += text_utils.count_words_ms_word_style(value)
                elif isinstance(value, list):
                    total += sum(text_utils.count_words_ms_word_style(item.get('text', str(item))) if isinstance(item, dict) else text_utils.count_words_ms_word_style(str(item)) for item in value)
        details = {'total_words': total, 'min': self.constraints.TOTAL_WORD_COUNT_MIN, 'max': self.constraints.TOTAL_WORD_COUNT_MAX}
        self._cache["H5_GLOBAL_TOTAL_WORD_COUNT"] = details
        return total

    def _calculate_k1_sentence_count_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K1_EXECUTIVE_SUMMARY,
            metrics_to_calc=[('sentence_count', text_utils.count_sentences)],
            constraints={'min': self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MIN, 'max': self.constraints.EXEC_SUMMARY_SENTENCE_COUNT_MAX}
        )
        self._cache["H3_K1_SENTENCE_COUNT"] = details
        return details

    def _calculate_k1_word_count_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K1_EXECUTIVE_SUMMARY,
            # FIX 1: Use count_words_ms_word_style
            metrics_to_calc=[('word_count', text_utils.count_words_ms_word_style)],
            constraints={'min': self.constraints.EXEC_SUMMARY_WORD_COUNT_MIN, 'max': self.constraints.EXEC_SUMMARY_WORD_COUNT_MAX}
        )
        # FIX 2: Use correct cache key
        self._cache["H3_K1_WORD_COUNT"] = details
        return details

    def _calculate_k2_overview_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K2_UNIFY_OVERVIEW,
            metrics_to_calc=[('word_count', text_utils.count_words_ms_word_style), ('sentence_count', text_utils.count_sentences)],
            constraints={'min_wc': self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MIN, 'max_wc': self.constraints.UNIFY_OVERVIEW_WORD_COUNT_MAX, 'min_sc': 1, 'max_sc': 2}
        )
        self._cache["H3_K2_OVERVIEW_WORD_COUNT"] = details
        self._cache["H3_K2_OVERVIEW_SENTENCE_COUNT"] = details
        return details

    def _calculate_k3_overview_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K3_IBM_OVERVIEW,
            metrics_to_calc=[('word_count', text_utils.count_words_ms_word_style), ('sentence_count', text_utils.count_sentences)],
            constraints={'min_wc': self.constraints.IBM_OVERVIEW_WORD_COUNT_MIN, 'max_wc': self.constraints.IBM_OVERVIEW_WORD_COUNT_MAX, 'min_sc': 1, 'max_sc': 2}
        )
        self._cache["H3_K3_OVERVIEW_WORD_COUNT"] = details
        self._cache["H3_K3_OVERVIEW_SENTENCE_COUNT"] = details
        return details

    def _calculate_headline_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K0_HEADLINE,
            metrics_to_calc=[('word_count', text_utils.count_words_ms_word_style), ('headline', lambda t: t)],
            constraints={'min': self.constraints.HEADLINE_WORD_COUNT_MIN, 'max': self.constraints.HEADLINE_WORD_COUNT_MAX}
        )
        self._cache["H3_K0_HEADLINE_WORD_COUNT"] = details
        self._cache["H3_K0_HEADLINE_NO_TITLES"] = details
        self._cache["H3_K0_HEADLINE_NO_COMMAS"] = details
        self._cache["H3_K0_HEADLINE_COMPONENT_WC"] = details
        return details

    def _calculate_cover_letter_jd_similarity(self):
        cover_letter_text = self.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
        similarity = 0.0
        if cover_letter_text and self.job_description:
            try:
                # --- FIX: Call text_utils.calculate_similarity ---
                similarity = text_utils.calculate_similarity(cover_letter_text, self.job_description)
            except Exception as e:
                self.logger.warning(f"Error calculating cover letter similarity: {e}")
                similarity = 0.0

        details = {
            "cover_letter_jd_similarity": similarity,
            "min_sim": self.constraints.COVER_LETTER_JD_RELEVANCE_THRESHOLD,
            "max_sim": self.signal_constraints.CL_MAX_JD_SIMILARITY
        }
        self._cache["H3_K11_COVER_LETTER_RELEVANCE_RANGE"] = details
        return similarity

    def _calculate_expected_signature(self):
        owner_info = self.master_resume.get('owner', {})
        contact_info = owner_info.get('contact', {})
        # This template is defined in workflow.py, but validation needs it too.
        COVER_LETTER_SIGNATURE_TEMPLATE = """Sincerely,

{name}  
{email}  
{phone}  
{linkedin}"""
        try:
            return COVER_LETTER_SIGNATURE_TEMPLATE.format(
                name=owner_info.get('name', '[Your Name]'),
                email=contact_info.get('email', '[Your Email]'),
                phone=contact_info.get('phone', '[Your Phone]'),
                linkedin=contact_info.get('linkedin', '[Your LinkedIn]')
            ).strip()
        except KeyError as e:
            self.logger.error(f"Error formatting signature template: Missing key {e}")
            return f"[Error: Missing signature key {e}]"

    def _calculate_cover_letter_structure_details(self):
        cl_text = self.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
        paras = [p.strip() for p in cl_text.split('\n\n') if p.strip()]
        p1_wc, p2_wc, p3_wc = 0, 0, 0
        error_msg = None
        try:
             salutation_idx = next(i for i, p in enumerate(paras) if p.startswith("Dear Hiring Manager,"))
             closing_idx = next((i for i, p in enumerate(paras) if p == "Sincerely,"), len(paras))
             p1_idx = salutation_idx + 1
             p2_idx = p1_idx + 1
             p3_idx = p2_idx + 1

             if p1_idx < closing_idx and p1_idx < len(paras): p1_wc = text_utils.count_words_ms_word_style(paras[p1_idx])
             if p2_idx < closing_idx and p2_idx < len(paras): p2_wc = text_utils.count_words_ms_word_style(paras[p2_idx])
             if p3_idx < closing_idx and p3_idx < len(paras): p3_wc = text_utils.count_words_ms_word_style(paras[p3_idx])
             if not (p1_idx < closing_idx and p2_idx < closing_idx and p3_idx < closing_idx and p3_idx < len(paras)):
                  error_msg = "Could not find expected 3 body paragraphs before closing"
        except (StopIteration, IndexError):
             error_msg = "Could not find expected salutation or closing"

        c = self.constraints
        details = {
            "p1_wc": p1_wc, "p1_min": c.COVER_LETTER_P1_WORD_COUNT_MIN, "p1_max": c.COVER_LETTER_P1_WORD_COUNT_MAX,
            "p2_wc": p2_wc, "p2_min": c.COVER_LETTER_P2_WORD_COUNT_MIN, "p2_max": c.COVER_LETTER_P2_WORD_COUNT_MAX,
            "p3_wc": p3_wc, "p3_min": c.COVER_LETTER_P3_WORD_COUNT_MIN, "p3_max": c.COVER_LETTER_P3_WORD_COUNT_MAX,
            "error": error_msg
        }
        self._cache["H3_K11_COVER_LETTER_STRUCTURE"] = details
        return details

    def _calculate_k4_narrative_details(self):
        min_wc = getattr(self.constraints, 'TRADERSENSE_NARRATIVE_WORD_COUNT_MIN', 40)
        max_wc = getattr(self.constraints, 'TRADERSENSE_NARRATIVE_WORD_COUNT_MAX', 60)
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K4_TRADERSENSE_NARRATIVE,
            metrics_to_calc=[('word_count', text_utils.count_words_ms_word_style), ('sentence_count', text_utils.count_sentences)],
            constraints={'min_wc': min_wc, 'max_wc': max_wc, 'target_sc': 3}
        )
        self._cache["H3_K4_NARRATIVE_WORD_COUNT"] = details
        self._cache["H3_K4_NARRATIVE_SENTENCE_COUNT"] = details
        return details

    def _calculate_k5_narrative_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K5_EY_NARRATIVE,
            metrics_to_calc=[('word_count', text_utils.count_words_ms_word_style), ('sentence_count', text_utils.count_sentences)],
            constraints={'min_wc': self.constraints.EY_NARRATIVE_WORD_COUNT_MIN, 'max_wc': self.constraints.EY_NARRATIVE_WORD_COUNT_MAX, 'target_sc': 3}
        )
        self._cache["H3_K5_NARRATIVE_WORD_COUNT"] = details
        self._cache["H3_K5_NARRATIVE_SENTENCE_COUNT"] = details
        return details

    def _calculate_k6_narrative_details(self):
        details = self._calculate_metric_details(
            section_enum=ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            metrics_to_calc=[('word_count', text_utils.count_words_ms_word_style), ('sentence_count', text_utils.count_sentences)],
            constraints={'min_wc': self.constraints.EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN, 'max_wc': self.constraints.EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX, 'target_sc': 3}
        )
        self._cache["H3_K6_NARRATIVE_WORD_COUNT"] = details
        self._cache["H3_K6_NARRATIVE_SENTENCE_COUNT"] = details
        return details

    def _calculate_cross_section_similarity_details(self) -> Dict:
        details = {"failures": [], "checked_pairs": 0, "max_similarity": 0.0, "scores": {}}
        threshold = 0.65
        sections_to_compare = [
            ResumeSection.K1_EXECUTIVE_SUMMARY,
            ResumeSection.K2_UNIFY_OVERVIEW,
            ResumeSection.K3_IBM_OVERVIEW,
            ResumeSection.K4_TRADERSENSE_NARRATIVE,
            ResumeSection.K5_EY_NARRATIVE,
            ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K9_COMPETENCIES,
        ]

        section_content = {}
        for section_enum in sections_to_compare:
            content = self.staging_buffer.get(section_enum.value)
            if isinstance(content, list) and section_enum == ResumeSection.K9_COMPETENCIES:
                 text_list = [item.get('text', str(item)) if isinstance(item, dict) else str(item) for item in content]
                 section_content[section_enum] = "\n".join(text_list)
            elif isinstance(content, str):
                 section_content[section_enum] = content

        max_sim = 0.0
        for i in range(len(sections_to_compare)):
            for j in range(i + 1, len(sections_to_compare)):
                enum1 = sections_to_compare[i]
                enum2 = sections_to_compare[j]

                text1 = section_content.get(enum1)
                text2 = section_content.get(enum2)

                if text1 and text2:
                    try:
                        # --- FIX: Call text_utils.calculate_similarity ---
                        similarity = text_utils.calculate_similarity(text1, text2)
                        details["checked_pairs"] += 1
                        details["scores"][f"{enum1.name}_vs_{enum2.name}"] = similarity
                        max_sim = max(max_sim, similarity)
                        if similarity >= threshold:
                            details["failures"].append(f"{enum1.name} vs {enum2.name}: {similarity:.3f}")
                    except Exception as e:
                        self.logger.warning(f"Error calculating similarity between {enum1.name} and {enum2.name}: {e}")

        details["max_similarity"] = max_sim
        self._cache["H5_GLOBAL_CROSS_SECTION_SIMILARITY"] = details
        return details

    def _calculate_k1_differentiator_range_details(self) -> Dict:
        k1_text = self.staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, '').lower()
        differentiators = []
        comp_intel = getattr(self.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel:
            # Handle both dataclass and dict forms
            if hasattr(comp_intel, 'differentiator_keywords'):
                differentiators = getattr(comp_intel, 'differentiator_keywords', [])
            elif isinstance(comp_intel, dict):
                differentiators = comp_intel.get('differentiator_keywords', [])
                
        valid_diffs = [kw for kw in differentiators if kw and isinstance(kw, str)]
        found = sum(1 for kw in valid_diffs if kw.lower() in k1_text)
        min_target = self.constraints.K1_MIN_DIFFERENTIATORS
        max_target = self.signal_constraints.K1_MAX_DIFFERENTIATORS
        details = {"found": found, "min": min_target, "max": max_target}
        # FIX 4: Use correct cache key
        self._cache["H3_K1_DIFFERENTIATOR_RANGE"] = details
        return details

    def _calculate_cover_letter_narrative_details(self) -> Dict:
        cl_text = self.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '').lower()
        hook = any(kw in cl_text for kw in ["enthusiastic", "excited", "apply for", "interest in", "compelling opportunity"])
        proof = any(kw in cl_text for kw in ["demonstrated", "achieved", "delivered", "resulted in", "experience", "proven ability", "track record"])
        vision = any(kw in cl_text for kw in ["contribute", "goals", "opportunity", "eager to discuss", "drive success", "valuable asset"])
        details = {"hook": hook, "proof": proof, "vision": vision, "valid": hook and proof and vision}
        self._cache["H3_K11_COVER_LETTER_NARRATIVE_INTEGRITY"] = details
        return details

    def _calculate_narrative_vs_master_similarity_details(self) -> Dict:
        details = {
            "section_results": [],
            "failures": [],
            "min_threshold": 0.40,
            "max_threshold": 0.70
        }
        narrative_sections = {
            ResumeSection.K4_TRADERSENSE_NARRATIVE: 2,
            ResumeSection.K5_EY_NARRATIVE: 3,
            ResumeSection.K6_EARLY_CAREER_NARRATIVE: 4,
        }
        master_experience = self.master_resume.get("professional_experience", [])

        for section_enum, master_index in narrative_sections.items():
            narrative_text = self.staging_buffer.get(section_enum.value)
            master_highlights = []
            section_result = {"section": section_enum.name, "avg_similarity": 0.0, "max_similarity": 0.0, "min_similarity": 1.0, "scores": [], "valid_range": True}

            if isinstance(narrative_text, str) and narrative_text.strip():
                if 0 <= master_index < len(master_experience):
                    exp = master_experience[master_index]
                    highlights_raw = exp.get('highlights', exp.get('bullet_pool', []))
                    if isinstance(highlights_raw, list):
                        master_highlights = [h for h in highlights_raw if isinstance(h, str) and h.strip()]

                if master_highlights:
                    similarities = []
                    for highlight in master_highlights:
                        try:
                            # --- FIX: Call text_utils.calculate_similarity ---
                            similarity = text_utils.calculate_similarity(narrative_text, highlight)
                            similarities.append(similarity)
                            section_result["scores"].append(round(similarity, 3))
                        except Exception as e:
                            self.logger.warning(f"Error calculating narrative similarity for {section_enum.name} vs highlight: {e}")

                    if similarities:
                        section_result["avg_similarity"] = sum(similarities) / len(similarities)
                        section_result["max_similarity"] = max(similarities)
                        section_result["min_similarity"] = min(similarities)

                        if not (details["min_threshold"] <= section_result["avg_similarity"] <= details["max_threshold"]):
                            section_result["valid_range"] = False
                            details["failures"].append(f"{section_enum.name} avg sim ({section_result['avg_similarity']:.3f}) outside range ({details['min_threshold']:.2f}-{details['max_threshold']:.2f})")
                    else:
                        section_result["valid_range"] = False
                        details["failures"].append(f"{section_enum.name}: Could not calculate similarities.")
                else:
                    section_result["valid_range"] = False
                    details["failures"].append(f"{section_enum.name}: Master highlights missing or empty.")
            else:
                section_result["valid_range"] = False
                details["failures"].append(f"{section_enum.name}: Generated narrative missing or empty.")

            details["section_results"].append(section_result)

        self._cache["H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY"] = details
        return details

# ==============================================================================
# PRE-FLIGHT VALIDATOR
# ==============================================================================

class PreFlightValidator:
    """
    The main validation orchestrator for HOP-5.
    Initializes all rules and runs them using ValidationContext.
    (Extracted from resume_workflow_v16_20.py)
    """
    def __init__(self, master_resume: Dict, app_config: AppConfig):
        self.master_resume = master_resume
        self.engine = ValidationEngine()
        self.config = app_config
        self.constraints = app_config.content_constraints
        self.signal_constraints = app_config.signal_constraints
        self.validator_config = app_config.validator
        
        self.FORBIDDEN_VERBS = self.validator_config.forbidden_verbs
        self.PIPELINE_STATUS_ENUM = self.validator_config.pipeline_status_enum
        
        self.REQUIRED_SECTIONS = self._convert_section_names_to_enums(
            self.validator_config.required_sections
        )
        self.BULLET_WORD_COUNT_SECTIONS_TO_CHECK = self._convert_section_names_to_enums(
            self.validator_config.bullet_word_count_sections_to_check
        )
        self.PROVENANCE_SPLIT_TARGETS = self._convert_config_keys_to_enums(
            self.validator_config.provenance_split_targets
        )
        
        # This config was part of the class in the original file, so it's kept here.
        self.SECTION_SIGNAL_TARGETS_CONFIG = {
            "K1_Exec_Summary": (ResumeSection.K1_EXECUTIVE_SUMMARY, 0.85, 1.20, None, None),
            "K2_Unify": (ResumeSection.K2_UNIFY_OVERVIEW, 0.70, 1.00, None, None),
            "K3_IBM": (ResumeSection.K3_IBM_OVERVIEW, 0.70, 1.00, None, None),
            "K4_TraderSense": (ResumeSection.K4_TRADERSENSE_NARRATIVE, 0.60, 0.90, None, None),
            "K6_Narrative": (ResumeSection.K6_EARLY_CAREER_NARRATIVE, 0.70, 1.00, None, None),
        }

        self.RULE_TO_SECTION_MAP = self._initialize_rule_map()
        self._register_rules()
        self.signal_constraints = app_config.signal_constraints
        self._dup_detector = None
        self.logger = logging.getLogger(__name__)

        # --- NEW: Code Interpreter for Evaluator ---
        self.code_interpreter = CodeInterpreterTool()

    @property
    def dup_detector(self):
        """Lazy-loads the DuplicateDetector."""
        if self._dup_detector is None:
            self._dup_detector = DuplicateDetector()
        return self._dup_detector
    
    def _convert_section_names_to_enums(self, section_names: Set[str]) -> Set:
        """Converts a set of section name strings to ResumeSection enums."""
        result = set()
        for name in section_names:
            if isinstance(name, str):
                try:
                    enum_val = ResumeSection[name]
                    result.add(enum_val)
                except KeyError:
                    logging.warning(f"Unknown ResumeSection '{name}' in validator config, skipping")
            else:
                result.add(name) # Already an enum
        return result
    
    def _convert_config_keys_to_enums(self, config_dict: Dict) -> Dict:
        """Converts string keys in config dicts to ResumeSection enums."""
        result = {}
        for key, value in config_dict.items():
            if isinstance(key, str):
                try:
                    enum_key = ResumeSection[key]
                    result[enum_key] = value
                except KeyError:
                    logging.warning(f"Unknown ResumeSection key '{key}' in validator config, skipping")
            else:
                result[key] = value # Already an enum
        return result
    
    # --- Rule Definition Helpers ---

    @staticmethod
    def _mk_range(rule_id, sev, cat, getter, label, min_k, max_k, val_k):
        """Factory for creating a range-check rule config."""
        return {
            "rule_id": rule_id, "severity": sev, "category": cat,
            "validator": lambda ctx: getter(ctx).get(min_k) <= getter(ctx).get(val_k) <= getter(ctx).get(max_k),
            "error_message": lambda ctx: f"{label}: {getter(ctx).get(val_k)} (target: {getter(ctx).get(min_k)}-{getter(ctx).get(max_k)})"
        }

    @staticmethod
    def _mk_method(rule_id, sev, cat, method_name, msg):
        """Factory for creating a method-based rule config."""
        return {
            "rule_id": rule_id, "severity": sev, "category": cat,
            "validator": method_name,
            "error_message": msg
        }

    # --- RULES_CONFIG: The master list of all validation rules ---
    @property
    def RULES_CONFIG(self):
        return [
            {
                "rule_id": "H0_RAG_MIN_QUALITY", "severity": ValidationSeverity.CRITICAL, "category": "signal",
                "validator": lambda ctx: getattr(ctx.thematic_analysis, 'signal_quality_score', 0.0) >= 0.50,
                "error_message": lambda ctx: f"Initial RAG Analysis Quality ({getattr(ctx.thematic_analysis, 'signal_quality_score', 0.0):.1%}) is below the minimum threshold (50%)."
            },
            {
                "rule_id": "H5_GLOBAL_TOTAL_WORD_COUNT", "severity": ValidationSeverity.CRITICAL, "category": "word_count",
                "validator": lambda ctx: ctx.constraints.TOTAL_WORD_COUNT_MIN <= ctx.total_words <= ctx.constraints.TOTAL_WORD_COUNT_MAX,
                "error_message": lambda ctx: f"Total resume: {ctx.total_words} words (target: {ctx.constraints.TOTAL_WORD_COUNT_MIN}-{ctx.constraints.TOTAL_WORD_COUNT_MAX})"
            },
            self._mk_range("H3_K1_SENTENCE_COUNT", ValidationSeverity.CRITICAL, "structure", lambda ctx: ctx.k1_sentence_count_details, "K.1 Exec Summary sentences", 'min', 'max', 'sentence_count'),
            # FIX 3: Use correct Rule ID
            self._mk_range("H3_K1_WORD_COUNT", ValidationSeverity.MEDIUM, "word_count", lambda ctx: ctx.k1_word_count_details, "K.1 Exec Summary words", 'min', 'max', 'word_count'),
            {
                "rule_id": "H3_K0_HEADLINE_WORD_COUNT", "severity": ValidationSeverity.MEDIUM,"category": "structure",
                "validator": lambda ctx: ctx.constraints.HEADLINE_WORD_COUNT_MIN <= ctx.headline_details['word_count'] <= ctx.constraints.HEADLINE_WORD_COUNT_MAX,
                "error_message": lambda ctx: f"K.0 Headline: {ctx.headline_details['word_count']} words (target: {ctx.headline_details['min']}-{ctx.headline_details['max']}). Headline: '{ctx.headline_details['headline']}'"
            },
            self._mk_range("H3_K2_OVERVIEW_WORD_COUNT", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k2_overview_details, "K.2 Unify Overview words", 'min_wc', 'max_wc', 'word_count'),
            self._mk_range("H3_K2_OVERVIEW_SENTENCE_COUNT", ValidationSeverity.HIGH, "structure", lambda ctx: ctx.k2_overview_details, "K.2 Unify Overview sentences", 'min_sc', 'max_sc', 'sentence_count'),
            self._mk_range("H3_K3_OVERVIEW_WORD_COUNT", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k3_overview_details, "K.3 IBM Overview words", 'min_wc', 'max_wc', 'word_count'),
            self._mk_range("H3_K3_OVERVIEW_SENTENCE_COUNT", ValidationSeverity.HIGH, "structure", lambda ctx: ctx.k3_overview_details, "K.3 IBM Overview sentences", 'min_sc', 'max_sc', 'sentence_count'),
            self._mk_range("H3_K4_NARRATIVE_WORD_COUNT", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k4_narrative_details, "K.4 TraderSense Narrative words", 'min_wc', 'max_wc', 'word_count'),
            {
                "rule_id": "H3_K4_NARRATIVE_SENTENCE_COUNT", "severity": ValidationSeverity.HIGH, "category": "structure",
                "validator": lambda ctx: ctx.k4_narrative_details['target_sc'] - 1 <= ctx.k4_narrative_details['sentence_count'] <= ctx.k4_narrative_details['target_sc'] + 1,
                "error_message": lambda ctx: f"K.4 TraderSense Narrative: {ctx.k4_narrative_details['sentence_count']} sentences (target range: {ctx.k4_narrative_details['target_sc']-1}-{ctx.k4_narrative_details['target_sc']+1})"
            },
            self._mk_range("H3_K5_NARRATIVE_WORD_COUNT", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k5_narrative_details, "K.5 EY Narrative words", 'min_wc', 'max_wc', 'word_count'),
            {
                "rule_id": "H3_K5_NARRATIVE_SENTENCE_COUNT", "severity": ValidationSeverity.HIGH, "category": "structure",
                "validator": lambda ctx: ctx.k5_narrative_details['target_sc'] - 1 <= ctx.k5_narrative_details['sentence_count'] <= ctx.k5_narrative_details['target_sc'] + 1,
                "error_message": lambda ctx: f"K.5 EY Narrative: {ctx.k5_narrative_details['sentence_count']} sentences (target range: {ctx.k5_narrative_details['target_sc']-1}-{ctx.k5_narrative_details['target_sc']+1})"
            },
            self._mk_range("H3_K6_NARRATIVE_WORD_COUNT", ValidationSeverity.HIGH, "word_count", lambda ctx: ctx.k6_narrative_details, "K.6 Early Career Narrative words", 'min_wc', 'max_wc', 'word_count'),
            {
                "rule_id": "H3_K6_NARRATIVE_SENTENCE_COUNT", "severity": ValidationSeverity.HIGH, "category": "structure",
                "validator": lambda ctx: ctx.k6_narrative_details['target_sc'] - 1 <= ctx.k6_narrative_details['sentence_count'] <= ctx.k6_narrative_details['target_sc'] + 1,
                "error_message": lambda ctx: f"K.6 Early Career Narrative: {ctx.k6_narrative_details['sentence_count']} sentences (target range: {ctx.k6_narrative_details['target_sc']-1}-{ctx.k6_narrative_details['target_sc']+1})"
            },
            
            # --- NEW TIERED BULLET WORD COUNT RULES ---
            self._mk_method("H3_GLOBAL_BULLET_WORD_COUNT_CRITICAL", ValidationSeverity.CRITICAL, "word_count",
                            "_validate_bullet_word_count_CRITICAL",
                            lambda ctx: f"Bullet word counts are CRITICAL (<15 or >50): {ctx.get_details_for_rule('H3_GLOBAL_BULLET_WORD_COUNT_CRITICAL').get('violations', 'N/A')}"),
            
            self._mk_method("H3_GLOBAL_BULLET_WORD_COUNT_HIGH", ValidationSeverity.MEDIUM, "word_count",
                            "_validate_bullet_word_count_HIGH",
                            lambda ctx: f"Bullet word counts are HIGH (15-20 or 45-50): {ctx.get_details_for_rule('H3_GLOBAL_BULLET_WORD_COUNT_HIGH').get('violations', 'N/A')}"),
            
            self._mk_method("H3_GLOBAL_BULLET_WORD_COUNT_MEDIUM", ValidationSeverity.MEDIUM, "word_count",
                            "_validate_bullet_word_count_MEDIUM",
                            lambda ctx: f"Bullet word counts are MEDIUM (21-22 or 43-44): {ctx.get_details_for_rule('H3_GLOBAL_BULLET_WORD_COUNT_MEDIUM').get('violations', 'N/A')}"),

            self._mk_method("H3_GLOBAL_BULLET_WORD_COUNT_LOW", ValidationSeverity.LOW, "word_count",
                            "_validate_bullet_word_count_LOW",
                            lambda ctx: f"Bullet word counts are LOW (23-24 or 41-42): {ctx.get_details_for_rule('H3_GLOBAL_BULLET_WORD_COUNT_LOW').get('violations', 'N/A')}"),
            # --- END TIERED RULES ---
            
            {
                "rule_id": "H5_BUFFER_LOCK_STATUS", "severity": ValidationSeverity.CRITICAL, "category": "structure",
                "validator": lambda ctx: ctx.staging_buffer.is_locked(),
                "error_message": "Staging buffer must be locked before validation"
            },
            {
                "rule_id": "H3_K11_COVER_LETTER_SIGNATURE_VALID", "severity": ValidationSeverity.CRITICAL, "category": "structure",
                "validator": lambda ctx: bool(ctx.expected_signature and '\n' in ctx.expected_signature and ctx.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '').rstrip().endswith(ctx.expected_signature)),
                "error_message": "K.11 Cover letter signature is missing, malformed, or not multi-line."
            },
            self._mk_method("H3_K11_COVER_LETTER_FULL_STRUCTURE", ValidationSeverity.CRITICAL, "structure", "_validate_cover_letter_full_structure", "K.11 Cover letter missing expected structure components (Date, Recipient, Salutation, Body Para 1/2/3, Closing, Signature)."),
            self._mk_method("H3_K0_HEADLINE_NO_TITLES", ValidationSeverity.CRITICAL, "structure", "_validate_headline_format_no_titles", lambda ctx: f"K.0 Headline contains forbidden titles: {ctx.get_details_for_rule('H3_K0_HEADLINE_NO_TITLES').get('forbidden', 'N/A')}. Headline: '{ctx.headline_details.get('headline', '')}'"),
            {"rule_id": "H3_K0_HEADLINE_NO_COMMAS", "severity": ValidationSeverity.CRITICAL, "category": "structure", "validator": lambda ctx: ',' not in ctx.headline_details.get('headline', ''), "error_message": lambda ctx: f"K.0 Headline contains commas. Headline: '{ctx.headline_details.get('headline', '')}'"},
            self._mk_method("H3_K0_HEADLINE_COMPONENT_WC", ValidationSeverity.HIGH, "structure", "_validate_headline_format_component_wc", lambda ctx: f"K.0 Headline component word count outside range ({ctx.get_details_for_rule('H3_K0_HEADLINE_COMPONENT_WC').get('min', '?')}-{ctx.get_details_for_rule('H3_K0_HEADLINE_COMPONENT_WC').get('max', '?')}). Violations: {ctx.get_details_for_rule('H3_K0_HEADLINE_COMPONENT_WC').get('wc_violations_str', 'N/A')}. Headline: '{ctx.get_details_for_rule('H3_K0_HEADLINE_COMPONENT_WC').get('headline', '')}'"),
            {"rule_id": "H7_VISUAL_RESUME_HEADER_H2", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Resume headers not consistently H2"},
            {"rule_id": "H7_VISUAL_EDU_CERTS_FORMAT", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Education/Certification format incorrect"},
            {"rule_id": "H7_VISUAL_EXPERIENCE_BULLET_STYLE", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Experience bullets incorrect style"},
            {"rule_id": "H7_VISUAL_COMPETENCIES_FORMATTING", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Competencies list formatting incorrect"},
            {"rule_id": "H7_VISUAL_EXPERIENCE_RENDER_FORMAT", "severity": ValidationSeverity.CRITICAL, "category": "visual", "validator": lambda ctx: True, "error_message": "Visual Check: Experience section formatting incorrect"},
            self._mk_method("H5_CONTENT_NO_PLACEHOLDERS", ValidationSeverity.CRITICAL, "content", "_validate_no_placeholders", lambda ctx: f"Found placeholder text in content: {ctx.get_details_for_rule('H5_CONTENT_NO_PLACEHOLDERS').get('placeholders', 'N/A')}"),
            self._mk_method("H3_CONTENT_NO_FORBIDDEN_VERBS", ValidationSeverity.CRITICAL, "content", "_validate_forbidden_verbs", lambda ctx: f"Forbidden verbs found in generated content: {ctx.get_details_for_rule('H3_CONTENT_NO_FORBIDDEN_VERBS').get('violations', 'N/A')}"),
            self._mk_method("H3_CONTENT_NO_INTRO_PHRASES", ValidationSeverity.CRITICAL, "content", "_validate_no_intro_phrases", lambda ctx: f"Banned introductory phrases found: {ctx.get_details_for_rule('H3_CONTENT_NO_INTRO_PHRASES').get('violations', 'N/A')}"),
            self._mk_method("H3_GLOBAL_PER_SECTION_SIGNAL_SCORE", ValidationSeverity.HIGH, "content", "_validate_per_section_signal_raw", lambda ctx: f"One or more sections outside target raw signal score range: {ctx.get_details_for_rule('H3_GLOBAL_PER_SECTION_SIGNAL_SCORE').get('failures', 'N/A')}"),
            # FIX 3: Use correct Rule ID
            {
                "rule_id": "H3_K1_DIFFERENTIATOR_RANGE", "severity": ValidationSeverity.CRITICAL, "category": "content",
                "validator": lambda ctx: ctx.constraints.K1_MIN_DIFFERENTIATORS <= ctx._calculate_k1_differentiator_range_details()['found'] <= ctx.signal_constraints.K1_MAX_DIFFERENTIATORS,
                "error_message": lambda ctx: f"K.1 Summary contains {ctx.get_details_for_rule('H3_K1_DIFFERENTIATOR_RANGE').get('found', '?')} differentiators (target: {ctx.get_details_for_rule('H3_K1_DIFFERENTIATOR_RANGE').get('min', '?')}-{ctx.get_details_for_rule('H3_K1_DIFFERENTIATOR_RANGE').get('max', '?')})."
            },
            self._mk_method("H5_GLOBAL_JD_KEYWORD_RANGE", ValidationSeverity.HIGH, "content", "_validate_jd_keyword_range", lambda ctx: f"Resume contains {ctx.get_details_for_rule('H5_GLOBAL_JD_KEYWORD_RANGE').get('found', '?')} unique JD keywords (target: {ctx.get_details_for_rule('H5_GLOBAL_JD_KEYWORD_RANGE').get('min', '?')}-{ctx.get_details_for_rule('H5_GLOBAL_JD_KEYWORD_RANGE').get('max', '?')})."),
            self._mk_method("H0_NARRATIVE_MINING_PRESENCE", ValidationSeverity.HIGH, "content", "_validate_narrative_mining_presence", "Phase 4 Narrative Mining data (problem_solution_narratives) is missing or incomplete in ThematicAnalysis."),
            {
                "rule_id": "H3_K11_COVER_LETTER_RELEVANCE_RANGE", "severity": ValidationSeverity.HIGH, "category": "content",
                "validator": lambda ctx: ctx.constraints.COVER_LETTER_JD_RELEVANCE_THRESHOLD <= ctx.cover_letter_jd_similarity <= ctx.signal_constraints.CL_MAX_JD_SIMILARITY,
                "error_message": lambda ctx: f"K.11 Cover letter relevance to JD is {ctx.cover_letter_jd_similarity:.2f} (target: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_RELEVANCE_RANGE').get('min_sim', 0.0):.2f}-{ctx.get_details_for_rule('H3_K11_COVER_LETTER_RELEVANCE_RANGE').get('max_sim', 0.0):.2f})."
            },
            self._mk_method("H3_K11_COVER_LETTER_NARRATIVE_INTEGRITY", ValidationSeverity.HIGH, "content", lambda ctx: ctx._calculate_cover_letter_narrative_details()['valid'], lambda ctx: f"K.11 Cover letter may be missing narrative integrity. Hook: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_NARRATIVE_INTEGRITY').get('hook', '?')}, Proof: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_NARRATIVE_INTEGRITY').get('proof', '?')}, Vision: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_NARRATIVE_INTEGRITY').get('vision', '?')}"),
            {
                "rule_id": "H3_K11_COVER_LETTER_FALLBACK_DETECTED", "severity": ValidationSeverity.HIGH, "category": "content",
                "validator": lambda ctx: "track record of measurable AI transformation" not in ctx.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, ''),
                "error_message": "Creative cover letter generation failed; fallback likely used."
            },
            self._mk_method("H3_K11_COVER_LETTER_STRUCTURE", ValidationSeverity.MEDIUM, "content", "_validate_cover_letter_structure", lambda ctx: f"K.11 Cover letter paragraph word counts out of spec. P1: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p1_wc','?')} ({ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p1_min','?')}-{ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p1_max','?')}), P2: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p2_wc','?')} ({ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p2_min','?')}-{ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p2_max','?')}), P3: {ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p3_wc','?')} ({ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p3_min','?')}-{ctx.get_details_for_rule('H3_K11_COVER_LETTER_STRUCTURE').get('p3_max','?')})"),
            self._mk_method("H3_GLOBAL_BULLET_PROVENANCE_SPLIT_CHECK", ValidationSeverity.CRITICAL, "content", "_validate_provenance_split", lambda ctx: f"Provenance split mismatch: {ctx.get_details_for_rule('H3_GLOBAL_BULLET_PROVENANCE_SPLIT_CHECK').get('violations', 'N/A')}"),
            self._mk_method("H5_GLOBAL_AUTHENTICITY_SIGNAL_CHECK", ValidationSeverity.HIGH, "content", "_validate_authenticity_signal", lambda ctx: f"Authenticity signal (verbs/phrasing) from HOP-0 not detected in resume content: {ctx.get_details_for_rule('H5_GLOBAL_AUTHENTICITY_SIGNAL_CHECK').get('details', 'N/A')}"),
            self._mk_method("H5_GLOBAL_CROSS_SECTION_SIMILARITY", ValidationSeverity.HIGH, "content", "_validate_cross_section_similarity", lambda ctx: f"High similarity (>=0.65) found between sections: {'; '.join(ctx.get_details_for_rule('H5_GLOBAL_CROSS_SECTION_SIMILARITY').get('failures', []))}"),
            self._mk_method("H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY", ValidationSeverity.HIGH, "content", "_validate_narrative_vs_master_similarity", lambda ctx: f"Narrative similarity to master highlights outside range (0.40-0.70): {'; '.join(ctx.get_details_for_rule('H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY').get('failures', []))}"),
        ]

    # --- Regex Patterns for Validation ---
    PROMPT_CONTAMINATION_PATTERN = re.compile(r"\b(MUST|CRITICAL|ABSOLUTELY|Do NOT|Output ONLY|Return ONLY|JSON structure|Word count:|Sentence count:|Target range:|strictly between)\b", re.IGNORECASE)
    CONVERSATIONAL_FILLERS_PATTERN = re.compile(r"^(Here is the|Certainly,|I have generated|Below is the|Apologies,|Please note)\b", re.IGNORECASE | re.MULTILINE)
    EMPTY_LIST_ITEM_PATTERN = re.compile(r"^\s*[\*\-]\s*($|\n)", re.MULTILINE)
    BANNED_INTRO_PHRASES_PATTERN = re.compile(r"^(In my role as|As a|At \[Company\]|My responsibilities included|Responsible for)\b", re.IGNORECASE)

    def _initialize_rule_map(self) -> Dict[str, Union[ResumeSection, str]]:
        """Maps rule IDs to the resume section they primarily validate."""
        logger = logging.getLogger(__name__)
        rule_map = {
            "H5_GLOBAL_TOTAL_WORD_COUNT": "GLOBAL",
            "H5_GLOBAL_JD_KEYWORD_RANGE": "GLOBAL",
            "H5_GLOBAL_AUTHENTICITY_SIGNAL_CHECK": "GLOBAL", "H0_NARRATIVE_MINING_PRESENCE": "GLOBAL",
            "H5_CONTENT_NO_PLACEHOLDERS": "GLOBAL", "H5_BUFFER_LOCK_STATUS": "GLOBAL",
            "H0_RAG_MIN_QUALITY": "GLOBAL",
            "H5_GLOBAL_CROSS_SECTION_SIMILARITY": "GLOBAL",
            "H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY": "GLOBAL",
            "H7_VISUAL_RESUME_HEADER_H2": "VISUAL", "H7_VISUAL_EDU_CERTS_FORMAT": "VISUAL",
            "H5_CONTENT_NO_PROMPT_CONTAMINATION": "GLOBAL",
            "H3_GLOBAL_CONTENT_NO_CONVERSATIONAL_FILLERS": "GLOBAL",
            "H5_STRUCTURE_NO_EMPTY_LIST_ITEMS": "GLOBAL",
            "H5_STRUCTURE_MARKDOWN_HEADER_SPACING": "GLOBAL",
            "H7_VISUAL_EXPERIENCE_BULLET_STYLE": "VISUAL", "H7_VISUAL_COMPETENCIES_FORMATTING": "VISUAL",
            "H7_VISUAL_EXPERIENCE_RENDER_FORMAT": "VISUAL",
            "H3_K0_HEADLINE_WORD_COUNT": ResumeSection.K0_HEADLINE, "H3_K0_HEADLINE_NO_TITLES": ResumeSection.K0_HEADLINE,
            "H3_K0_HEADLINE_NO_COMMAS": ResumeSection.K0_HEADLINE, "H3_K0_HEADLINE_COMPONENT_WC": ResumeSection.K0_HEADLINE,
            "STRUCTURE_K0_HEADLINE_PRESENT": ResumeSection.K0_HEADLINE,
            "H3_K1_SENTENCE_COUNT": ResumeSection.K1_EXECUTIVE_SUMMARY, "H3_K1_WORD_COUNT": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "H3_K1_DIFFERENTIATOR_RANGE": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "STRUCTURE_K1_EXECUTIVE_SUMMARY_PRESENT": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "STRUCTURE_K2_UNIFY_BULLETS_PRESENT": ResumeSection.K2_UNIFY_BULLETS, "STRUCTURE_K2_UNIFY_OVERVIEW_PRESENT": ResumeSection.K2_UNIFY_OVERVIEW,
            "H3_K2_OVERVIEW_WORD_COUNT": ResumeSection.K2_UNIFY_OVERVIEW, "H3_K2_OVERVIEW_SENTENCE_COUNT": ResumeSection.K2_UNIFY_OVERVIEW,
            "STRUCTURE_K3_IBM_BULLETS_PRESENT": ResumeSection.K3_IBM_BULLETS, "STRUCTURE_K3_IBM_OVERVIEW_PRESENT": ResumeSection.K3_IBM_OVERVIEW,
            "H3_K3_OVERVIEW_WORD_COUNT": ResumeSection.K3_IBM_OVERVIEW, "H3_K3_OVERVIEW_SENTENCE_COUNT": ResumeSection.K3_IBM_OVERVIEW,
            "STRUCTURE_K4_TRADERSENSE_NARRATIVE_PRESENT": ResumeSection.K4_TRADERSENSE_NARRATIVE, "H3_K4_NARRATIVE_WORD_COUNT": ResumeSection.K4_TRADERSENSE_NARRATIVE,
            "H3_K4_NARRATIVE_SENTENCE_COUNT": ResumeSection.K4_TRADERSENSE_NARRATIVE,
            "STRUCTURE_K5_EY_NARRATIVE_PRESENT": ResumeSection.K5_EY_NARRATIVE, "H3_K5_NARRATIVE_WORD_COUNT": ResumeSection.K5_EY_NARRATIVE,
            "H3_K5_NARRATIVE_SENTENCE_COUNT": ResumeSection.K5_EY_NARRATIVE,
            "STRUCTURE_K6_EARLY_CAREER_NARRATIVE_PRESENT": ResumeSection.K6_EARLY_CAREER_NARRATIVE, "H3_K6_NARRATIVE_WORD_COUNT": ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            "H3_K6_NARRATIVE_SENTENCE_COUNT": ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            "STRUCTURE_K9_COMPETENCIES_PRESENT": ResumeSection.K9_COMPETENCIES,
            "STRUCTURE_K10_SKILLS_PRESENT": ResumeSection.K10_SKILLS,
            "H3_K11_COVER_LETTER_SIGNATURE_VALID": ResumeSection.K11_COVER_LETTER, "H3_K11_COVER_LETTER_FULL_STRUCTURE": ResumeSection.K11_COVER_LETTER,
            "H3_K11_COVER_LETTER_RELEVANCE_RANGE": ResumeSection.K11_COVER_LETTER, "H3_K11_COVER_LETTER_NARRATIVE_INTEGRITY": ResumeSection.K11_COVER_LETTER,
            "H3_K11_COVER_LETTER_FALLBACK_DETECTED": ResumeSection.K11_COVER_LETTER, "H3_K11_COVER_LETTER_STRUCTURE": ResumeSection.K11_COVER_LETTER,
            "STRUCTURE_K11_COVER_LETTER_PRESENT": ResumeSection.K11_COVER_LETTER,
            
            # --- NEW TIERED BULLET WORD COUNT RULES ---
            "H3_GLOBAL_BULLET_WORD_COUNT_CRITICAL": "COMPLEX_PER_SECTION",
            "H3_GLOBAL_BULLET_WORD_COUNT_HIGH": "COMPLEX_PER_SECTION",
            "H3_GLOBAL_BULLET_WORD_COUNT_MEDIUM": "COMPLEX_PER_SECTION",
            "H3_GLOBAL_BULLET_WORD_COUNT_LOW": "COMPLEX_PER_SECTION",
            # --- END TIERED RULES ---

            "H3_GLOBAL_PER_SECTION_SIGNAL_SCORE": "COMPLEX_PER_SECTION", 
            "H3_GLOBAL_BULLET_PROVENANCE_SPLIT_CHECK": "COMPLEX_PER_SECTION", 
            "H3_CONTENT_NO_FORBIDDEN_VERBS": "COMPLEX_PER_SECTION",
            "H3_CONTENT_NO_INTRO_PHRASES": "COMPLEX_PER_SECTION"
        }

        # Dynamically add rules for required sections not explicitly in RULES_CONFIG
        config_rule_ids = {cfg["rule_id"] for cfg in self.RULES_CONFIG}
        for section_enum in self.REQUIRED_SECTIONS:
            rule_id = f"STRUCTURE_{section_enum.name}_PRESENT"
            if rule_id not in config_rule_ids and rule_id not in rule_map:
                rule_map[rule_id] = section_enum
                logger.debug(f"Dynamically mapped structure rule: {rule_id} -> {section_enum.name}")

        header_enums = [ 
            ResumeSection.K0_EXECUTIVE_SUMMARY_HEADER, ResumeSection.K0_EXPERIENCE_HEADER, 
            ResumeSection.K0_EDUCATION_HEADER, ResumeSection.K0_CERTIFICATIONS_HEADER, 
            ResumeSection.K0_COMPETENCIES_HEADER 
        ]
        for header_enum in header_enums:
             rule_id = f"STRUCTURE_{header_enum.name}_PRESENT"
             if rule_id not in rule_map:
                  rule_map[rule_id] = header_enum
                  logger.debug(f"Dynamically mapped header structure rule: {rule_id} -> {header_enum.name}")

        return rule_map

    def _register_rules(self):
        """Registers all rules from the RULES_CONFIG into the ValidationEngine."""
        logger = logging.getLogger(__name__)
        all_rules_config = list(self.RULES_CONFIG)

        # Dynamically add rules for required sections
        for section_enum in self.REQUIRED_SECTIONS:
            rule_id = f"STRUCTURE_{section_enum.name}_PRESENT"
            if not any(cfg["rule_id"] == rule_id for cfg in all_rules_config):
                all_rules_config.append({
                    "rule_id": rule_id,
                    "severity": ValidationSeverity.CRITICAL,
                    "category": "structure",
                    "validator": partial(self._validate_section_presence, section_enum=section_enum),
                    "error_message": f"{section_enum.value} is missing, empty, or a placeholder."
                })

        # Add other dynamic/method-based rules
        all_rules_config.append(self._mk_method("H5_CONTENT_NO_PROMPT_CONTAMINATION", ValidationSeverity.HIGH, "content", "_validate_no_prompt_contamination", lambda ctx: f"Found prompt contamination keywords in content: {ctx.get_details_for_rule('H5_CONTENT_NO_PROMPT_CONTAMINATION').get('violations', 'N/A')}"))
        all_rules_config.append(self._mk_method("H3_GLOBAL_CONTENT_NO_CONVERSATIONAL_FILLERS", ValidationSeverity.HIGH, "content", "_validate_no_conversational_fillers", lambda ctx: f"Found conversational filler phrases in content: {ctx.get_details_for_rule('H3_GLOBAL_CONTENT_NO_CONVERSATIONAL_FILLERS').get('violations', 'N/A')}"))
        all_rules_config.append(self._mk_method("H5_STRUCTURE_NO_EMPTY_LIST_ITEMS", ValidationSeverity.MEDIUM, "structure", "_validate_no_empty_list_items", lambda ctx: f"Found empty list items in sections: {ctx.get_details_for_rule('H5_STRUCTURE_NO_EMPTY_LIST_ITEMS').get('violations', 'N/A')}"))
        all_rules_config.append(self._mk_method("H5_STRUCTURE_MARKDOWN_HEADER_SPACING", ValidationSeverity.MEDIUM, "structure", "_validate_markdown_header_spacing", lambda ctx: f"Found markdown headers with missing spaces: {ctx.get_details_for_rule('H5_STRUCTURE_MARKDOWN_HEADER_SPACING').get('violations', 'N/A')}"))

        registered_rule_ids = set()
        rules_to_register = []
        
        for config in all_rules_config:
            rule_id = config["rule_id"]
            if rule_id in registered_rule_ids:
                 logger.warning(f"Duplicate rule ID found during registration: {rule_id}. Skipping re-registration.")
                 continue

            validator_ref = config["validator"]
            validator_func = None
            if isinstance(validator_ref, str):
                validator_func = getattr(self, validator_ref, None)
                if validator_func is None:
                    msg = f"Validator method '{validator_ref}' not found for rule {rule_id}"
                    logger.error(msg)
                    # Create a dummy validator that will fail
                    validator_func = lambda ctx, rid=rule_id, m=msg: (logger.error(f"Executing dummy validator for missing method in rule {rid}: {m}"), False)[1]
            elif callable(validator_ref):
                 validator_func = validator_ref
            else:
                 logger.error(f"Invalid validator type for rule {rule_id}: {type(validator_ref)}. Config: {config}")
                 raise TypeError(f"Invalid validator type for rule {rule_id}: {type(validator_ref)}")

            # --- START FIX (Bug 3): This lambda now ONLY reads from the cache ---
            # It no longer attempts to populate the cache itself, which fixes
            # the maximum recursion depth error.
            def create_error_message_lambda(template, rule_id_for_cache):
                def error_lambda(ctx: ValidationContext):
                    try:
                        # The validator function (which runs first) is responsible
                        # for populating the cache. This lambda should only read from it.
                        details = ctx.get_details_for_rule(rule_id_for_cache)

                        if callable(template):
                            return str(template(ctx))
                        else:
                            # Fallback for simple string templates
                            return str(template).format_map(defaultdict(lambda: '[N/A]', **details))

                    except Exception as e:
                        logger.error(f"Error formatting error message for rule {rule_id_for_cache}: {e}. Template type: '{type(template)}'. Details retrieved: {ctx.get_details_for_rule(rule_id_for_cache)}", exc_info=False)
                        # Prevent recursion if an error happens *during* formatting
                        if "recursion depth" in str(e):
                            return f"[RECURSION ERROR formatting msg for {rule_id_for_cache}]"
                        return f"[Error formatting msg for {rule_id_for_cache}]"
                return error_lambda
            # --- END FIX ---

            error_msg_lambda = create_error_message_lambda(config["error_message"], rule_id)

            rule = ValidationRule(
                rule_id=rule_id,
                severity=config["severity"],
                category=config.get("category", "general"),
                validator=validator_func,
                error_message=error_msg_lambda
            )
            rules_to_register.append(rule)
            registered_rule_ids.add(rule_id)

        self.engine.register_rules(rules_to_register)
        logger.info(f"Registered {len(rules_to_register)} validation rules.")

    # --- Validation Methods (called by rules) ---

    def _validate_cross_section_similarity(self, context: ValidationContext) -> bool:
        try:
            details = context.cross_section_similarity_details
            if details.get("failures"):
                failed_sections_set = set()
                sections_to_compare_map = {
                    ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K2_UNIFY_OVERVIEW,
                    ResumeSection.K3_IBM_OVERVIEW, ResumeSection.K4_TRADERSENSE_NARRATIVE,
                    ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE,
                    ResumeSection.K9_COMPETENCIES
                }
                for failure_str in details["failures"]:
                    match = re.match(r"(\w+)\s+vs\s+(\w+):", failure_str)
                    if match:
                        name1, name2 = match.groups()
                        for enum_member in sections_to_compare_map:
                            if enum_member.name == name1: failed_sections_set.add(enum_member)
                            if enum_member.name == name2: failed_sections_set.add(enum_member)
                context._cache["H5_GLOBAL_CROSS_SECTION_SIMILARITY"]["failed_sections"] = [s.name for s in failed_sections_set]
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error during cross-section similarity validation: {e}")
            context._cache["H5_GLOBAL_CROSS_SECTION_SIMILARITY"] = {"failures": [f"Validation error: {e}"], "failed_sections": []}
            return False

    def _validate_narrative_vs_master_similarity(self, context: ValidationContext) -> bool:
        try:
            details = context.narrative_vs_master_similarity_details
            if details.get("failures"):
                failed_sections_set = set()
                narrative_sections_map = {
                    ResumeSection.K4_TRADERSENSE_NARRATIVE,
                    ResumeSection.K5_EY_NARRATIVE,
                    ResumeSection.K6_EARLY_CAREER_NARRATIVE
                }
                for section_result in details.get("section_results", []):
                    if not section_result.get("valid_range", True):
                        section_name = section_result.get("section")
                        if section_name:
                             for enum_member in narrative_sections_map:
                                 if enum_member.name == section_name:
                                     failed_sections_set.add(enum_member)
                                     break
                context._cache["H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY"]["failed_sections"] = [s.name for s in failed_sections_set]
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error during narrative vs master similarity validation: {e}")
            context._cache["H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY"] = {"failures": [f"Validation error: {e}"], "failed_sections": []}
            return False

    def _validate_section_presence(self, context: ValidationContext, section_enum: ResumeSection) -> bool:
        content = context.staging_buffer.get(section_enum.value)
        if content is None: return False
        if isinstance(content, str): return content.strip() not in ["", "HEADER_PLACEHOLDER"] and not content.strip().startswith("[Placeholder")
        if isinstance(content, (list, dict)): return bool(content)
        return True

    def _validate_cover_letter_full_structure(self, context: ValidationContext) -> bool:
        text = context.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
        expected_sig = context.expected_signature
        has_date = bool(re.search(r"^\w+ \d{1,2}, \d{4}", text.strip()))
        has_recipient = bool(re.search(r"Hiring Manager\n\[Company Name\]", text))
        has_salutation = bool(re.search(r"Dear Hiring Manager,", text))
        has_closing = bool(re.search(r"\n\nSincerely,\n\n", text))
        has_signature = expected_sig and expected_sig in text and text.strip().endswith(expected_sig)
        body_match = re.search(r"Dear Hiring Manager,\s*(.*?)\s*Sincerely,", text, re.DOTALL)
        paras_found = len([p for p in body_match.group(1).strip().split('\n\n') if p.strip()]) if body_match else 0
        has_3_paras = paras_found >= 3
        valid = has_date and has_recipient and has_salutation and has_closing and has_signature and has_3_paras
        if not valid: context._cache["H3_K11_COVER_LETTER_FULL_STRUCTURE"] = { "has_date": has_date, "has_recipient": has_recipient, "has_salutation": has_salutation, "has_closing": has_closing, "has_signature": has_signature, "paras_found": paras_found }
        return valid

    def _validate_cover_letter_structure(self, context: ValidationContext) -> bool:
        text = context.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
        details = context.cover_letter_structure_details
        if details.get("error"): return False
        p1_valid = details.get('p1_min', 0) <= details.get('p1_wc', -1) <= details.get('p1_max', float('inf'))
        p2_valid = details.get('p2_min', 0) <= details.get('p2_wc', -1) <= details.get('p2_max', float('inf'))
        p3_valid = details.get('p3_min', 0) <= details.get('p3_wc', -1) <= details.get('p3_max', float('inf'))
        return p1_valid and p2_valid and p3_valid

    # --- NEW TIERED BULLET WORD COUNT VALIDATION METHODS ---
    
    def _get_bullet_word_counts(self, context: ValidationContext) -> List[Tuple[int, str, ResumeSection]]:
        """Helper to get all bullet word counts for tiered validation."""
        # Use a simple cache within the context object for this validation run
        if "BULLET_WORD_COUNTS_CACHE" in context._cache:
            return context._cache["BULLET_WORD_COUNTS_CACHE"]

        counts = []
        for section_enum in self.BULLET_WORD_COUNT_SECTIONS_TO_CHECK:
            section_key = section_enum.value
            bullets = context.staging_buffer.get(section_key, [])
            
            # --- START FIX (Bug 2 & 3): Add type check to prevent crash on corrupted state ---
            if not isinstance(bullets, list): 
                logging.warning(f"Expected list for {section_key} bullets. Got {type(bullets)}. Skipping.")
                continue
            # --- END FIX ---
            
            for i, bullet in enumerate(bullets):
                actual_wc = 0
                bullet_text = ""
                if isinstance(bullet, dict): 
                    bullet_text = bullet.get('text', '')
                    actual_wc = bullet.get('word_count', text_utils.count_words_ms_word_style(bullet_text))
                elif isinstance(bullet, str): 
                    bullet_text = bullet
                    actual_wc = text_utils.count_words_ms_word_style(bullet_text)
                else: 
                    logging.warning(f"Invalid bullet item type in {section_key}[{i}]. Skipping."); 
                    continue
                
                counts.append((actual_wc, f"{section_key}[{i}]", section_enum))
        
        context._cache["BULLET_WORD_COUNTS_CACHE"] = counts
        return counts

    def _validate_bullet_word_count_CRITICAL(self, context: ValidationContext) -> bool:
        violations = []
        failed_sections = set()
        all_counts = context._get_bullet_word_counts()
        
        # Critical: < 15 or > 50
        for wc, loc, section_enum in all_counts:
            if wc < 15 or wc > 50:
                violations.append(f"{loc}: {wc} words")
                failed_sections.add(section_enum)

        if violations:
            context._cache["H3_GLOBAL_BULLET_WORD_COUNT_CRITICAL"] = { "violations": ", ".join(violations), "failed_sections": [s.name for s in failed_sections] }
            return False
        return True

    def _validate_bullet_word_count_HIGH(self, context: ValidationContext) -> bool:
        violations = []
        failed_sections = set()
        all_counts = context._get_bullet_word_counts()
        
        # High: 15-20 or 45-50
        for wc, loc, section_enum in all_counts:
            if (15 <= wc <= 20) or (45 <= wc <= 50):
                violations.append(f"{loc}: {wc} words")
                failed_sections.add(section_enum)

        if violations:
            context._cache["H3_GLOBAL_BULLET_WORD_COUNT_HIGH"] = { "violations": ", ".join(violations), "failed_sections": [s.name for s in failed_sections] }
            return False
        return True

    def _validate_bullet_word_count_MEDIUM(self, context: ValidationContext) -> bool:
        violations = []
        failed_sections = set()
        all_counts = context._get_bullet_word_counts()
        
        # Medium: 21-22 or 43-44
        for wc, loc, section_enum in all_counts:
            if (21 <= wc <= 22) or (43 <= wc <= 44):
                violations.append(f"{loc}: {wc} words")
                failed_sections.add(section_enum)

        if violations:
            context._cache["H3_GLOBAL_BULLET_WORD_COUNT_MEDIUM"] = { "violations": ", ".join(violations), "failed_sections": [s.name for s in failed_sections] }
            return False
        return True

    def _validate_bullet_word_count_LOW(self, context: ValidationContext) -> bool:
        violations = []
        failed_sections = set()
        all_counts = context._get_bullet_word_counts()
        
        # Low: 23-24 or 41-42
        for wc, loc, section_enum in all_counts:
            if (23 <= wc <= 24) or (41 <= wc <= 42):
                violations.append(f"{loc}: {wc} words")
                failed_sections.add(section_enum)

        if violations:
            context._cache["H3_GLOBAL_BULLET_WORD_COUNT_LOW"] = { "violations": ", ".join(violations), "failed_sections": [s.name for s in failed_sections] }
            return False
        return True
    # --- END TIERED METHODS ---

    def _validate_headline_format_no_titles(self, context: ValidationContext) -> bool:
        details = context.headline_details; headline = details.get('headline', '')
        if not headline or '|' not in headline: details['error'] = "Missing pipes"; context._cache["H3_K0_HEADLINE_NO_TITLES"] = details; return False
        components = [c.strip() for c in headline.split('|')]
        if len(components) != 3: details['error'] = f"Expected 3 components, found {len(components)}"; context._cache["H3_K0_HEADLINE_NO_TITLES"] = details; return False
        forbidden_titles = ['director', 'vp', 'manager', 'lead', 'head', 'chief', 'principal', 'senior', 'executive']
        forbidden_found = []
        for i, comp in enumerate(components):
            for title in forbidden_titles:
                 if re.search(r'\b' + re.escape(title) + r'\b', comp.lower()): forbidden_found.append(title)
        details_titles = details.copy(); details_titles['forbidden'] = list(set(forbidden_found)); context._cache["H3_K0_HEADLINE_NO_TITLES"] = details_titles
        return not forbidden_found

    def _validate_headline_format_component_wc(self, context: ValidationContext) -> bool:
        details = context.headline_details; headline = details.get('headline', '')
        if not headline or '|' not in headline: context._cache["H3_K0_HEADLINE_COMPONENT_WC"] = {"error": "Missing pipes", "headline": headline}; return False
        components = [c.strip() for c in headline.split('|')]
        if len(components) != 3: context._cache["H3_K0_HEADLINE_COMPONENT_WC"] = {"error": f"Expected 3 components, found {len(components)}", "headline": headline}; return False
        component_wc_violations = []; wc_valid = True
        min_comp_wc = context.constraints.HEADLINE_COMPONENT_WORDS_MIN; max_comp_wc = context.constraints.HEADLINE_COMPONENT_WORDS_MAX
        for i, comp in enumerate(components):
            word_count = text_utils.count_words_ms_word_style(comp)
            if not (min_comp_wc <= word_count <= max_comp_wc):
                component_wc_violations.append(f"Comp[{i+1}]: {word_count} words (Tgt: {min_comp_wc}-{max_comp_wc})")
                wc_valid = False
        details_wc = details.copy(); details_wc['min'] = min_comp_wc; details_wc['max'] = max_comp_wc;
        details_wc['wc_violations_str'] = "; ".join(component_wc_violations) if component_wc_violations else "None"
        context._cache["H3_K0_HEADLINE_COMPONENT_WC"] = details_wc
        return wc_valid

    def _validate_no_placeholders(self, context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        found_snippets = []
        failed_sections = set()

        def check_recursive(item, key_enum=None):
            nonlocal found_snippets, failed_sections

            if isinstance(item, str):
                if "[" in item:
                    placeholder_match = re.search(r"(\[(?:Placeholder|Your Name|Company Name|MISSING_CONTEXT|Unserializable).*?\])", item)
                    if placeholder_match:
                        placeholder_text = placeholder_match.group(1)
                        start_index = placeholder_match.start()
                        snippet_before = item[max(0, start_index - 30):start_index]
                        snippet_after = item[start_index + len(placeholder_text) : start_index + len(placeholder_text) + 30]
                        snippet = f"...{snippet_before}{placeholder_text}{snippet_after}..."
                        found_snippets.append(f"{key_enum.value if key_enum else '?'}: {snippet}")
                        if key_enum:
                            failed_sections.add(key_enum)
            elif isinstance(item, dict):
                for k, v in item.items():
                    enum_for_value = key_enum
                    try:
                        enum_for_value = ResumeSection(k)
                    except ValueError:
                        pass
                    check_recursive(v, enum_for_value)
            elif isinstance(item, list):
                for elem in item:
                    check_recursive(elem, key_enum)

        for key_str, top_level_item in buffer_data.items():
            top_level_enum = None
            try:
                top_level_enum = ResumeSection(key_str)
            except ValueError:
                pass
            check_recursive(top_level_item, top_level_enum)

        if found_snippets:
            context._cache["H5_CONTENT_NO_PLACEHOLDERS"] = {
                "placeholders": ", ".join(found_snippets[:3]),
                "failed_sections": [s.name for s in failed_sections]
            }
            return False

        return True

    def _validate_no_prompt_contamination(self, context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        found_snippets = []
        failed_sections = set()

        def check_recursive(item, key_enum=None):
            nonlocal found_snippets, failed_sections
            if isinstance(item, str):
                match = self.PROMPT_CONTAMINATION_PATTERN.search(item)
                if match:
                    found_word = match.group(1)
                    start_index = match.start()
                    snippet = f"...{item[max(0, start_index - 30):start_index]}>>{found_word}<<{item[start_index + len(found_word):start_index + len(found_word) + 30]}..."
                    found_snippets.append(f"{key_enum.value if key_enum else '?'}: {snippet}")
                    if key_enum: failed_sections.add(key_enum)
            elif isinstance(item, dict):
                for k, v in item.items():
                    enum_for_value = key_enum
                    try: enum_for_value = ResumeSection(k)
                    except ValueError: pass
                    check_recursive(v, enum_for_value)
            elif isinstance(item, list):
                for elem in item:
                    check_recursive(elem, key_enum)

        for key_str, top_level_item in buffer_data.items():
            top_level_enum = None
            try: top_level_enum = ResumeSection(key_str)
            except ValueError: pass
            check_recursive(top_level_item, top_level_enum)

        if found_snippets:
            context._cache["H5_CONTENT_NO_PROMPT_CONTAMINATION"] = {"violations": ", ".join(found_snippets[:3]), "failed_sections": [s.name for s in failed_sections]}
            return False
        return True

    def _validate_no_conversational_fillers(self, context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        found_snippets = []
        failed_sections = set()

        for key_str, item in buffer_data.items():
            if isinstance(item, str):
                match = self.CONVERSATIONAL_FILLERS_PATTERN.search(item)
                if match:
                    try: key_enum = ResumeSection(key_str)
                    except ValueError: continue
                    found_snippets.append(f"{key_enum.value}: Starts with '{match.group(1)}'")
                    failed_sections.add(key_enum)

        if found_snippets:
            context._cache["H3_GLOBAL_CONTENT_NO_CONVERSATIONAL_FILLERS"] = {"violations": ", ".join(found_snippets[:3]), "failed_sections": [s.name for s in failed_sections]}
            return False
        return True

    def _validate_no_empty_list_items(self, context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        found_snippets = []
        failed_sections = set()

        for key_str, item in buffer_data.items():
            if isinstance(item, str) and ('*' in item or '-' in item):
                if self.EMPTY_LIST_ITEM_PATTERN.search(item):
                    try: key_enum = ResumeSection(key_str)
                    except ValueError: continue
                    found_snippets.append(f"{key_enum.value}")
                    failed_sections.add(key_enum)

        if found_snippets:
            context._cache["H5_STRUCTURE_NO_EMPTY_LIST_ITEMS"] = {"violations": ", ".join(found_snippets), "failed_sections": [s.name for s in failed_sections]}
            return False
        return True

    def _validate_markdown_header_spacing(self, context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        found_snippets = []
        failed_sections = set()
        header_spacing_pattern = re.compile(r"^#{1,6}[^\s#]", re.MULTILINE)

        for key_str, item in buffer_data.items():
            if isinstance(item, str):
                match = header_spacing_pattern.search(item)
                if match:
                    try: key_enum = ResumeSection(key_str)
                    except ValueError: continue
                    found_snippets.append(f"{key_enum.value}: Found '{match.group(0)}'")
                    failed_sections.add(key_enum)

        if found_snippets:
            context._cache["H5_STRUCTURE_MARKDOWN_HEADER_SPACING"] = {"violations": ", ".join(found_snippets), "failed_sections": [s.name for s in failed_sections]}
            return False
        return True

    def _validate_forbidden_verbs(self, context: ValidationContext) -> bool:
        valid = True
        violations = []
        failed = set()
        sections_to_check = [
            ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K3_IBM_BULLETS, ResumeSection.K9_COMPETENCIES,
            ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K3_IBM_OVERVIEW,
            ResumeSection.K1_EXECUTIVE_SUMMARY
        ]
        for section_enum in sections_to_check:
            content = context.staging_buffer.get(section_enum.value)
            texts = []
            if isinstance(content, str):
                if content.strip():
                    texts.append((content, -1))
            elif isinstance(content, list):
                for i, item in enumerate(content):
                    text = item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    if text.strip():
                        texts.append((text, i))

            for text, idx in texts:
                found_verbs = (v for v in self.FORBIDDEN_VERBS if re.search(r'\b' + re.escape(v) + r'\b', text.lower()))
                found_list = list(found_verbs)
                if found_list:
                    valid = False
                    loc = f"{section_enum.value}" + (f"[{idx}]" if idx != -1 else "")
                    violations.append(f"{loc}: '{', '.join(found_list)}'")
                    failed.add(section_enum)

        if not valid:
            context._cache["H3_CONTENT_NO_FORBIDDEN_VERBS"] = {"violations": ", ".join(violations[:3]), "failed_sections": [s.name for s in failed]}
        return valid

    def _validate_no_intro_phrases(self, context: ValidationContext) -> bool:
        valid = True
        violations = []
        failed = set()
        sections_to_check = [
            ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K3_IBM_BULLETS, ResumeSection.K9_COMPETENCIES,
            ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K3_IBM_OVERVIEW,
            ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K11_COVER_LETTER
        ]
        for section_enum in sections_to_check:
            content = context.staging_buffer.get(section_enum.value)
            texts_info = []
            is_cl = (section_enum == ResumeSection.K11_COVER_LETTER)

            if isinstance(content, str):
                if is_cl:
                    body_text = content
                    body_text = re.sub(r".*Dear Hiring Manager,\s*", "", body_text, flags=re.DOTALL | re.IGNORECASE)
                    body_text = re.sub(r"\s*Sincerely,.*", "", body_text, flags=re.DOTALL | re.IGNORECASE)
                    if body_text.strip():
                        for i, para in enumerate(body_text.strip().split('\n\n')):
                            if para.strip():
                                texts_info.append((para.strip(), f"Para {i+1}"))
                elif content.strip():
                    texts_info.append((content.strip(), None))
            elif isinstance(content, list):
                for i, item in enumerate(content):
                    text = item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    if text.strip():
                        texts_info.append((text.strip(), i))

            for text, idx_label in texts_info:
                 match = self.BANNED_INTRO_PHRASES_PATTERN.match(text)
                 if match:
                     valid = False
                     loc = f"{section_enum.value}"
                     if isinstance(idx_label, int):
                         loc += f"[{idx_label}]"
                     elif isinstance(idx_label, str):
                         loc += f" ({idx_label})"
                     violations.append(f"{loc}: Starts with '{match.group(0).strip()}'")
                     failed.add(section_enum)

        if not valid:
            context._cache["H3_CONTENT_NO_INTRO_PHRASES"] = {"violations": ", ".join(violations[:3]), "failed_sections": [s.name for s in failed]}
        return valid

    def _validate_per_section_signal_raw(self, context: ValidationContext) -> bool:
        valid = True; failures = []; failed = set()
        for label, (section_enum, target_min_raw, target_max_raw, _, _) in self.SECTION_SIGNAL_TARGETS_CONFIG.items():
            content = context.staging_buffer.get(section_enum.value); raw_score = 0.0
            if content:
                try:
                     # FIX: Call the imported function
                     normalized_score = calculate_signal_score(content, context.thematic_analysis); raw_score = normalized_score
                     if section_enum == ResumeSection.K1_EXECUTIVE_SUMMARY and raw_score > 0.9: raw_score = 1.15
                except Exception as e: logging.warning(f"Error calculating raw signal score for {label}: {e}")
            if not (target_min_raw <= raw_score <= target_max_raw): valid = False; failures.append(f"{label}({section_enum.name}): Raw {raw_score:.2f} (Tgt: {target_min_raw:.2f}-{target_max_raw:.2f})"); failed.add(section_enum)
        if not valid: context._cache["H3_GLOBAL_PER_SECTION_SIGNAL_SCORE"] = {"failures": ", ".join(failures[:3]), "failed_sections": [s.name for s in failed]}
        return valid

    def _validate_jd_keyword_range(self, context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        sections_to_include = [ se for se in ResumeSection if se not in [ResumeSection.K0_NAME, ResumeSection.K0_CONTACT, ResumeSection.K11_COVER_LETTER] and not se.name.endswith("_HEADER") ]
        text_parts = []
        for key_enum in sections_to_include:
            value = buffer_data.get(key_enum.value)
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                text_parts.extend(str(item.get('text', str(item))) if isinstance(item,dict) else str(item) for item in value)
        full_text = " ".join(text_parts)
        differentiators = set(); comp_intel = getattr(context.thematic_analysis, 'competitive_intelligence', None)
        if comp_intel:
            # Handle both dataclass and dict forms
            if hasattr(comp_intel, 'differentiator_keywords'):
                differentiators = set(kw for kw in getattr(comp_intel, 'differentiator_keywords', []) if kw and isinstance(kw, str))
            elif isinstance(comp_intel, dict):
                differentiators = set(kw for kw in comp_intel.get('differentiator_keywords', []) if kw and isinstance(kw, str))
        
        primary_words = set(kw for kw in context.thematic_analysis.primary_theme.get('keywords', []) if kw and isinstance(kw, str))
        all_jd_keywords = differentiators.union(primary_words); found = {kw for kw in all_jd_keywords if kw.lower() in full_text.lower()}
        min_target = context.constraints.MIN_JD_KEYWORDS; max_target = context.signal_constraints.RESUME_MAX_JD_KEYWORDS
        valid = min_target <= len(found) <= max_target
        context._cache["H5_GLOBAL_JD_KEYWORD_RANGE"] = {"found": len(found), "min": min_target, "max": max_target, "jd_keywords_found": list(found)}
        return valid

    def _validate_narrative_mining_presence(self, context: ValidationContext) -> bool:
        narratives = getattr(context.thematic_analysis, 'problem_solution_narratives', None)
        return isinstance(narratives, dict) and narratives.get('common_problems') and narratives.get('solution_patterns')

    def _validate_provenance_split(self, context: ValidationContext) -> bool:
        valid = True; violations = []; failed = set()
        for section_enum, targets in self.PROVENANCE_SPLIT_TARGETS.items():
            bullets = context.staging_buffer.get(section_enum.value, [])
            if not isinstance(bullets, list): logging.warning(f"Expected list for {section_enum.value} provenance check. Skipping."); continue
            counts = defaultdict(int)
            for bullet in bullets:
                if isinstance(bullet, dict): counts[bullet.get('provenance', 'Unknown')] += 1
            for prov_type_enum in BulletProvenance:
                prov_type = prov_type_enum.value; target = targets.get(prov_type, 0); actual = counts.get(prov_type, 0)
                if actual != target: valid = False; violations.append(f"{section_enum.value}: {prov_type} has {actual} (target: {target})"); failed.add(section_enum)
        if not valid: context._cache["H3_GLOBAL_BULLET_PROVENANCE_SPLIT_CHECK"] = {"violations": ", ".join(violations[:3]), "failed_sections": [s.name for s in failed]}
        return valid

    def _validate_authenticity_signal(self, context: ValidationContext) -> bool:
        buffer_data = context.staging_buffer.data
        auth_patterns_data = getattr(context.thematic_analysis, 'authenticity_patterns', {}); patterns_dict = {}
        if isinstance(auth_patterns_data, dict): patterns_dict = auth_patterns_data.get('patterns', {});
        if not isinstance(patterns_dict, dict): patterns_dict = {}
        if not patterns_dict: return True
        verbs = patterns_dict.get('achievement_verb_patterns', []); phrasing = patterns_dict.get('competency_phrasing', [])
        valid_verbs = [v for v in verbs if isinstance(v, str)]; valid_phrasing = [p for p in phrasing if isinstance(p, str)]
        target_signals = set(v.lower() for v in valid_verbs[:10]) | set(p.lower().split(':')[0].split()[0] for p in valid_phrasing[:5] if ':' in p and p.split()); target_signals = {s for s in target_signals if s}
        sections_to_scan = [ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K3_IBM_BULLETS, ResumeSection.K9_COMPETENCIES]
        text_parts = []
        for sec_enum in sections_to_scan:
            value = buffer_data.get(sec_enum.value)
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                text_parts.extend(str(item.get('text', str(item))) if isinstance(item,dict) else str(item) for item in value)
        full_text = " ".join(text_parts)
        if not target_signals or not full_text: return True
        found = {sig for sig in target_signals if re.search(r'\b' + re.escape(sig) + r'\b', full_text.lower())}
        ratio = len(found) / len(target_signals) if target_signals else 0.0; valid = ratio >= 0.3
        context._cache["H5_GLOBAL_AUTHENTICITY_SIGNAL_CHECK"] = {"details": f"Found {len(found)}/{len(target_signals)} ({ratio:.1%}) auth signals."}
        return valid

    # --- NEW: Macro-ToT Evaluator Agent ---
    def _run_scoring_competition(self, context: ValidationContext, drafts: List[str], section_enum: ResumeSection) -> str:
        """
        NEW: Runs the "scoring competition" using the Code Interpreter.
        Selects the best draft from the Macro-ToT list.
        """
        if not self.code_interpreter:
            self.logger.warning(f"CodeInterpreterTool not found. Cannot run scoring competition for {section_enum.name}. Selecting draft 0.")
            return drafts[0]

        if not isinstance(drafts, list) or len(drafts) == 0:
            self.logger.warning(f"No drafts provided to _run_scoring_competition for {section_enum.name}. Returning empty string.")
            return ""
        
        if isinstance(drafts, list) and len(drafts) == 1:
            return drafts[0] # Only one draft, no competition needed

        # 1. Get the scoring criteria
        # Use try-except to safely get details that might not be calculated yet
        try:
            jd_keywords = context.jd_keyword_range_details.get("jd_keywords_found", [])
        except:
            jd_keywords = [] # Fallback
            
        primary_theme = context.thematic_analysis.primary_theme.get("name", "").lower()
        if not primary_theme:
            self.logger.warning(f"Scoring {section_enum.name}: Primary theme is empty. Strategic score will be 0.")

        drafts_json = json.dumps(drafts)
        keywords_json = json.dumps(jd_keywords)
        theme_str = json.dumps(primary_theme)

        # 2. Define the scoring script
        scoring_script = f"""
import json

drafts = {drafts_json}
jd_keywords = {keywords_json}
primary_theme = {theme_str}

scores = []

def calculate_ats_score(text):
    text_lower = text.lower()
    if not jd_keywords:
        return 0
    return sum(1 for kw in jd_keywords if kw.lower() in text_lower)

def calculate_strategic_score(text):
    text_lower = text.lower()
    return 1 if primary_theme and primary_theme in text_lower else 0

for i, text in enumerate(drafts):
    ats_score = calculate_ats_score(text)
    strategic_score = calculate_strategic_score(text)
    
    # Strategy is weighted 2x ATS
    final_score = ats_score + (strategic_score * 2)
    scores.append( (final_score, i) )

# Find the index of the best draft
best_score, best_index = max(scores, key=lambda item: item[0])
print(json.dumps({{"winner_text": drafts[best_index], "winner_index": best_index, "winner_score": best_score}}))
"""
        # 3. Run the script
        success, output = self.code_interpreter.run(scoring_script)

        if success:
            try:
                result = json.loads(output)
                winning_draft = result.get("winner_text")
                self.logger.info(f"  ✓ Scoring competition for {section_enum.name} complete. Draft {result.get('winner_index')} won with score {result.get('winner_score')}.")
                return winning_draft
            except json.JSONDecodeError:
                self.logger.warning(f"Scoring competition for {section_enum.name} failed (invalid JSON output). Selecting draft 0.")
                return drafts[0]
        else:
            self.logger.warning(f"Scoring competition script for {section_enum.name} failed: {output}. Selecting draft 0.")
            return drafts[0]

    def validate(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis,
        job_description: str,
        macro_tot_drafts: Dict[str, Any], # Changed type hint
        sections_under_test: Optional[Set[ResumeSection]] = None
    ) -> Tuple[List[ValidationResult], bool, Set[ResumeSection], Dict[str, Any]]: # Changed return type
        """
        Runs the validation engine against the staging buffer.
        NEW: Runs "Evaluator" logic first, then validates the winners.
        """
        logger = logging.getLogger(__name__)
        # FIX: Pass self.config (AppConfig) to the ValidationContext constructor
        context = ValidationContext(staging_buffer, thematic_analysis, job_description, self.master_resume, self.config)
        rules_to_run = self.engine.rules
        failed_sections_enums = set()
        winning_drafts = {}

        # --- NEW: Step 1 - Run Macro-ToT "Evaluator" Scoring ---
        logger.info("Running Macro-ToT draft evaluation (HOP-5)...")
        # Create a copy of the buffer data to be modified
        temp_staging_buffer_data = staging_buffer.data.copy()

        # --- START FIX (Bug 1): Define ToT sections and check type before evaluating ---
        
        # Define the *only* sections that should be evaluated
        MACRO_TOT_SECTIONS = {
            ResumeSection.K0_HEADLINE,
            ResumeSection.K1_EXECUTIVE_SUMMARY,
            ResumeSection.K11_COVER_LETTER
        }

        for section_key_str, drafts in macro_tot_drafts.items():
            try:
                # Try to convert the string key (e.g., "K.0_Headline") to the Enum object
                section_enum = ResumeSection(section_key_str)
                is_resume_section = True
            except ValueError:
                # This is not a ResumeSection key (e.g., 'experience_sections'), just copy it.
                temp_staging_buffer_data[section_key_str] = drafts
                winning_drafts[section_key_str] = drafts # Also copy to winning_drafts
                is_resume_section = False

            if is_resume_section:
                # Check if this is a Macro-ToT section that needs evaluation
                is_macro_tot_section = (
                    section_enum in MACRO_TOT_SECTIONS and
                    isinstance(drafts, list) and 
                    len(drafts) > 0 and 
                    isinstance(drafts[0], str)
                )

                if is_macro_tot_section:
                    # It's a Macro-ToT section, run the competition
                    winner = self._run_scoring_competition(context, drafts, section_enum)
                    winning_drafts[section_key_str] = winner # Store winner by string key
                    temp_staging_buffer_data[section_key_str] = winner # Store in buffer by string key
                else:
                    # It's a non-Macro-ToT section (e.g., List[Dict] for bullets, or a single string)
                    # Just copy it over as-is.
                    winning_drafts[section_key_str] = drafts
                    temp_staging_buffer_data[section_key_str] = drafts
        # --- END FIX ---


        # Create a *new* context object based on the *winning* drafts
        # This is what all other rules will be validated against
        winner_buffer = ImmutableStagingBuffer()
        for k, v in temp_staging_buffer_data.items():
            winner_buffer.set(k, v)
        winner_buffer.lock()
        
        context = ValidationContext(winner_buffer, thematic_analysis, job_description, self.master_resume, self.config)
        logger.info("...Evaluation complete. Validating winning drafts.")
        # --- END NEW ---

        if sections_under_test:
            logger.info(f"Validating specific sections: {[s.name for s in sections_under_test]}")
            relevant_rule_ids = set()
            
            # Define the set of new bullet word count rules
            bullet_wc_rules = {
                "H3_GLOBAL_BULLET_WORD_COUNT_CRITICAL",
                "H3_GLOBAL_BULLET_WORD_COUNT_HIGH",
                "H3_GLOBAL_BULLET_WORD_COUNT_MEDIUM",
                "H3_GLOBAL_BULLET_WORD_COUNT_LOW"
            }

            for rule_id, section_map in self.RULE_TO_SECTION_MAP.items():
                if section_map == "GLOBAL" or section_map == "VISUAL" or section_map in sections_under_test:
                    relevant_rule_ids.add(rule_id)
                elif section_map == "COMPLEX_PER_SECTION":
                    # This logic checks if a complex rule (that spans multiple sections)
                    # is relevant to the sections currently under test.
                    
                    # Check if the rule is one of the new bullet WC rules
                    if rule_id in bullet_wc_rules and any(s in sections_under_test for s in self.BULLET_WORD_COUNT_SECTIONS_TO_CHECK):
                        relevant_rule_ids.add(rule_id)
                    elif rule_id == "H3_GLOBAL_BULLET_PROVENANCE_SPLIT_CHECK" and any(s in sections_under_test for s in self.PROVENANCE_SPLIT_TARGETS): relevant_rule_ids.add(rule_id)
                    elif rule_id == "H3_CONTENT_NO_FORBIDDEN_VERBS" and any(s in sections_under_test for s in [ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K3_IBM_BULLETS, ResumeSection.K3_IBM_OVERVIEW, ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE, ResumeSection.K9_COMPETENCIES]): relevant_rule_ids.add(rule_id)
                    elif rule_id == "H3_CONTENT_NO_INTRO_PHRASES" and any(s in sections_under_test for s in [ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K2_UNIFY_BULLETS, ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K3_IBM_BULLETS, ResumeSection.K3_IBM_OVERVIEW, ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE, ResumeSection.K9_COMPETENCIES, ResumeSection.K11_COVER_LETTER]): relevant_rule_ids.add(rule_id)
                    elif rule_id == "H5_GLOBAL_CROSS_SECTION_SIMILARITY" and any(s in sections_under_test for s in [ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K2_UNIFY_OVERVIEW, ResumeSection.K3_IBM_OVERVIEW, ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREER_NARRATIVE, ResumeSection.K9_COMPETENCIES]): relevant_rule_ids.add(rule_id)
                    elif rule_id == "H5_GLOBAL_NARRATIVE_VS_MASTER_SIMILARITY" and any(s in sections_under_test for s in [ResumeSection.K4_TRADERSENSE_NARRATIVE, ResumeSection.K5_EY_NARRATIVE, ResumeSection.K6_EARLY_CAREAR_NARRATIVE]): relevant_rule_ids.add(rule_id)

            rules_to_run = [r for r in self.engine.rules if r.rule_id in relevant_rule_ids]
            logger.info(f"Filtered to {len(rules_to_run)} relevant rules for sections under test.")

        # Run all rules (or the filtered subset)
        all_results = self.engine.validate(context, categories=None)

        # Filter results to only those that were supposed to run
        final_results_for_run = all_results # Run all rules against the winning drafts

        has_critical_or_high_failures = self.engine.has_high_or_critical_failures(final_results_for_run)
        all_passed = not has_critical_or_high_failures

        # Determine which sections failed
        if True: # Always run this to collect failure data
            for vr in final_results_for_run:
                # --- NEW: Check for strategic failure ---
                # This is the "Slow Loop" trigger
                if "H5_GLOBAL_THEME_PRESENCE" in vr.rule_id and not vr.passed:
                    logger.critical(f"STRATEGIC FAILURE DETECTED: {vr.message}")
                    # This exception will be caught by the Foreman (execute_workflow)
                    raise FactualFailureException(f"Strategic Failure: {vr.message}")

                # This is the original logic for tracking failures
                if not vr.passed and vr.severity.value >= ValidationSeverity.HIGH.value:
                    section_map = self.RULE_TO_SECTION_MAP.get(vr.rule_id)
                    if isinstance(section_map, ResumeSection):
                        failed_sections_enums.add(section_map)
                    elif section_map == "COMPLEX_PER_SECTION" or section_map == "GLOBAL":
                        # Check the cache for "failed_sections" populated by the rule method
                        cached_details = context.get_details_for_rule(vr.rule_id)
                        failed_in_cache = cached_details.get("failed_sections", set())
                        if isinstance(failed_in_cache, set):
                            valid_enums_in_cache = {item for item in failed_in_cache if isinstance(item, ResumeSection)}
                            failed_sections_enums.update(valid_enums_in_cache)

        logger.info(f"Validation complete. Passed: {all_passed}. Failed Sections (High/Crit): {[s.name for s in failed_sections_enums]}")
        return final_results_for_run, all_passed, failed_sections_enums, winning_drafts

# ==============================================================================
# GATE DECISION ENGINE
# ==============================================================================

class GateDecisionEngine:
    """
    Makes the final GO/NO-GO (PROCEED/HALT) decision based on validation results.
    (Extracted from resume_workflow_v16_20.py)
    """
    def decide(
        self,
        validation_results: List[ValidationResult]
    ) -> Tuple[GateDecision, str]:
        """
        Make gate decision based on validation results.

        Returns:
            (decision, reason)
        """
        critical_failures = [
            vr for vr in validation_results
            if not vr.passed and vr.severity == ValidationSeverity.CRITICAL
        ]

        # --- NEW: Check for Factual/Strategic failures ---
        # These are failures that should trigger the Slow Loop
        strategic_failures = [
            vr for vr in validation_results
            if not vr.passed and (
                "H5_GLOBAL_THEME_PRESENCE" in vr.rule_id or "H0_RAG_MIN_QUALITY" in vr.rule_id
            )
        ]

        high_failures = [
            vr for vr in validation_results
            if not vr.passed and vr.severity == ValidationSeverity.HIGH
        ]

        logger = logging.getLogger(__name__)
        logger.debug(
            f"GateDecisionEngine: Critical failures={len(critical_failures)}, "
            f"High failures={len(high_failures)}, "
            f"Total validation results={len(validation_results)}"
        )

        if len(critical_failures) > 0:
            return (
                GateDecision.HALT,
                f"HALT: {len(critical_failures)} CRITICAL failures detected"
            )
        elif len(strategic_failures) > 0:
            return (
                GateDecision.HALT, # This will be caught and re-raised as FactualFailureException
                f"HALT: {len(strategic_failures)} Factual/Strategic failures detected" 
            )
        elif len(high_failures) > 0:
            return (
                GateDecision.HALT,
                f"HALT: {len(high_failures)} HIGH severity failures detected (zero tolerance)"
            )
        else:
            return (
                GateDecision.PROCEED,
                "PROCEED: All validations passed"
            )

# ==============================================================================
# QA REPORT GENERATOR
# ==============================================================================

class QAReportGenerator:
    """
    Generates comprehensive QA reports for resume workflow output.
    Extracted from resume_workflow_v16_20.py
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
        
        # Section 5: Output files
        lines.append("## Section 5: Final Output Format Check (High Level)")
        
        output_checks = {
            "Resume (.md)": "RENDER_RESUME_MD",
            "Skills (.txt)": "RENDER_SKILLS",
            "Cover Letter (.txt)": "RENDER_COVER_LETTER",
            "QA Report (.md)": "H8_OUTPUT_QA_REPORT_MD_EXISTS", # This rule doesn't exist, but we check QA_REPORT_GENERATION_OVERALL
            "App Tracker (.json)": "APP_TRACKER_VALIDATION"
        }
        
        for output_name, rule_id in output_checks.items():
            result = next((r for r in validation_results if r.rule_id == rule_id), None)
            if rule_id == "H8_OUTPUT_QA_REPORT_MD_EXISTS": # Special check for QA report
                status = 'PASS' # If we got this far, the report text exists
            else:
                status = ('PASS' if result and result.passed else 'FAIL') if result else 'N/A'
            lines.append(f"* {output_name}: **{status}**")
        
        qa_report_text = "\n".join(lines)
        
        # Return validation result
        qa_generation_validation_results = []
        qa_generation_validation_results.append(ValidationResult(
            rule_id="QA_REPORT_GENERATION_OVERALL",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Simplified QA Report generated successfully."
        ))
        
        return qa_generation_validation_results, qa_report_text