# hops/05_hop_validation.py
"""
Hop 5: Comprehensive Validation with 12+ Rules

This validator includes:
1. Global word count validation
2. Keyword coverage checks  
3. Section-specific constraint validation
4. Thematic alignment scoring
5. Input signal quality tracking
6. Placeholder detection
7. Narrative proportion validation
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import necessary components from helpers
from helpers import (
    setup_workflow_logging, HopExecutionError, default_serializer,
    ValidationResult, ValidationSeverity, ThematicAnalysis, 
    ImmutableStagingBuffer, ContentConstraintsConfig
)

# Initialize constraints
CONSTRAINTS = ContentConstraintsConfig()

# --- Mock Embedding Client ---

class EmbeddingClient:
    """Mock EmbeddingClient for semantic validation"""
    def __init__(self, config=None):
        logging.info("Initialized MOCK EmbeddingClient for HOP-5")
        self.dimension = 768

    def embed(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimension
        hash_val = hash(text)
        np.random.seed(hash_val % (2**32 - 1))
        return np.random.rand(self.dimension).tolist()

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        return np.array([self.embed(text) for text in texts])

# --- Validation Engine ---

class ValidationEngine:
    """
    Comprehensive validation engine with 12+ rules
    """
    
    def __init__(self, constraints: Dict, thematic_analysis: ThematicAnalysis, job_description: str):
        self.constraints = constraints or {}
        self.thematic_analysis = thematic_analysis
        self.job_description = job_description
        self.logger = logging.getLogger(__name__)
        
        self.embedding_client = EmbeddingClient()
        
        # Pre-calculate target vectors
        self.target_theme_embeddings, self.target_keywords = self._get_target_vectors()

    def _get_target_vectors(self) -> Tuple[np.ndarray, Set[str]]:
        """Generate embeddings for HOP-0 themes"""
        self.logger.info("Vectorizing HOP-0 thematic targets for validation...")
        targets = []
        keywords = set()
        
        if self.thematic_analysis.primary_theme:
            targets.append(self.thematic_analysis.primary_theme.get("name", ""))
            targets.extend(self.thematic_analysis.primary_theme.get("keywords", []))
            keywords.update(self.thematic_analysis.primary_theme.get("keywords", []))
        
        if hasattr(self.thematic_analysis, 'competitive_intelligence') and self.thematic_analysis.competitive_intelligence:
            diff_keywords = getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])
            if diff_keywords:
                keywords.update(diff_keywords[:5])
        
        targets = [t for t in targets if t]
        if not targets:
            self.logger.warning("No thematic targets found. Semantic validation will be limited.")
            return np.array([]), set()
            
        return self.embedding_client.embed_batch(targets), keywords

    def _extract_all_text(self, staging_buffer: ImmutableStagingBuffer) -> str:
        """Concatenate all text from buffer"""
        all_text = []
        for key, content in staging_buffer.data.items():
            if isinstance(content, str):
                all_text.append(content)
            elif isinstance(content, list):
                all_text.extend([str(item) for item in content])
        return " ".join(all_text)

    def validate_all(self, staging_buffer: ImmutableStagingBuffer) -> List[ValidationResult]:
        """Run all validation rules"""
        self.logger.info("--- Starting Comprehensive Validation (12+ Rules) ---")
        
        # Discover all check_ methods
        all_rules = [
            getattr(self, func) for func in dir(self)
            if callable(getattr(self, func)) and func.startswith('check_')
        ]
        
        all_generated_text = self._extract_all_text(staging_buffer)
        
        results = []
        for rule in all_rules:
            try:
                result = rule(staging_buffer, all_generated_text)
                results.append(result)
                status = "âœ" PASSED" if result.passed else "âŒ FAILED"
                self.logger.info(f"  {status} - {result.rule_id}")
            except Exception as e:
                self.logger.error(f"Validation rule {rule.__name__} failed: {e}")
                results.append(ValidationResult(
                    rule_id=f"ENGINE_FAILURE_{rule.__name__}",
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Rule execution error: {e}"
                ))
        
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        self.logger.info(f"--- Validation Complete: {passed} passed, {failed} failed ({len(results)} total) ---")
        
        return results

    # --- VALIDATION RULES (12+ Required) ---

    def check_global_word_count(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        Rule 1: GLOBAL_WORD_COUNT
        Validates total word count is within acceptable range
        """
        word_count = len(all_text.split())
        min_wc = CONSTRAINTS.TOTAL_WORD_COUNT_MIN
        max_wc = CONSTRAINTS.TOTAL_WORD_COUNT_MAX
        
        passed = min_wc <= word_count <= max_wc
        severity = ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO
        
        return ValidationResult(
            rule_id="GLOBAL_WORD_COUNT",
            passed=passed,
            severity=severity,
            message=f"Total word count: {word_count} (target: {min_wc}-{max_wc})",
            details={"word_count": word_count, "min": min_wc, "max": max_wc}
        )

    def check_keyword_coverage(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        Rule 2: KEYWORD_COVERAGE
        Validates that minimum JD keywords appear in resume
        """
        text_lower = all_text.lower()
        found_keywords = [kw for kw in self.target_keywords if kw.lower() in text_lower]
        missing_keywords = list(self.target_keywords - set(found_keywords))
        
        min_keywords = CONSTRAINTS.MIN_JD_KEYWORDS
        passed = len(found_keywords) >= min_keywords
        severity = ValidationSeverity.HIGH if not passed else ValidationSeverity.INFO
        
        return ValidationResult(
            rule_id="KEYWORD_COVERAGE",
            passed=passed,
            severity=severity,
            message=f"Found {len(found_keywords)}/{len(self.target_keywords)} keywords (min: {min_keywords})",
            details={"found": found_keywords, "missing": missing_keywords, "required": min_keywords}
        )

    def check_headline_constraints(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        Rule 3: HEADLINE_CONSTRAINTS
        Validates headline structure and word count
        """
        headline = buffer.get("K.0_Headline") or buffer.get("K0_HEADLINE") or ""
        
        if not headline:
            return ValidationResult(
                rule_id="HEADLINE_CONSTRAINTS",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Headline is missing",
                details={}
            )
        
        word_count = len(headline.split())
        pipe_count = headline.count("|")
        
        min_wc = CONSTRAINTS.HEADLINE_WORD_COUNT_MIN
        max_wc = CONSTRAINTS.HEADLINE_WORD_COUNT_MAX
        
        wc_ok = min_wc <= word_count <= max_wc
        structure_ok = pipe_count == 2
        
        passed = wc_ok and structure_ok
        severity = ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO
        
        return ValidationResult(
            rule_id="HEADLINE_CONSTRAINTS",
            passed=passed,
            severity=severity,
            message=f"Headline: {word_count} words, {pipe_count} pipes (need: {min_wc}-{max_wc} words, 2 pipes)",
            details={
                "word_count": word_count,
                "pipe_count": pipe_count,
                "word_count_ok": wc_ok,
                "structure_ok": structure_ok
            }
        )

    def check_exec_summary_constraints(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        Rule 4: EXEC_SUMMARY_CONSTRAINTS
        Validates executive summary word and sentence counts
        """
        summary = buffer.get("K.1_Executive_Summary") or buffer.get("K1_EXECUTIVE_SUMMARY") or ""
        
        if not summary:
            return ValidationResult(
                rule_id="EXEC_SUMMARY_CONSTRAINTS",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Executive summary is missing"
            )
        
        word_count = len(summary.split())
        sentence_count = len(re.findall(r'[.!?]+', summary))
        
        min_wc = CONSTRAINTS.EXEC_SUMMARY_WORD_COUNT_MIN
        max_wc = CONSTRAINTS.EXEC_SUMMARY_WORD_COUNT_MAX
        min_sc = CONSTRAINTS.EXEC_SUMMARY_SENTENCE_COUNT_MIN
        max_sc = CONSTRAINTS.EXEC_SUMMARY_SENTENCE_COUNT_MAX
        
        wc_ok = min_wc <= word_count <= max_wc
        sc_ok = min_sc <= sentence_count <= max_sc
        
        passed = wc_ok and sc_ok
        severity = ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO
        
        return ValidationResult(
            rule_id="EXEC_SUMMARY_CONSTRAINTS",
            passed=passed,
            severity=severity,
            message=f"Summary: {word_count} words, {sentence_count} sentences (target: {min_wc}-{max_wc} words, {min_sc}-{max_sc} sentences)",
            details={
                "word_count": word_count,
                "sentence_count": sentence_count,
                "word_count_ok": wc_ok,
                "sentence_count_ok": sc_ok
            }
        )

    def check_input_signal_quality(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        Rule 5: INPUT_SIGNAL_QUALITY
        Reports the HOP-0 RAG signal quality (not a failure, just info)
        """
        signal_quality = self.thematic_analysis.signal_quality_score
        
        # This is informational - always passes but reports quality
        passed = True
        severity = ValidationSeverity.INFO
        
        if signal_quality < 0.6:
            severity = ValidationSeverity.LOW
        
        return ValidationResult(
            rule_id="INPUT_SIGNAL_QUALITY",
            passed=passed,
            severity=severity,
            message=f"HOP-0 RAG signal quality: {signal_quality:.2%}",
            details={"signal_quality": signal_quality}
        )

    def check_thematic_alignment_summary(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        Rule 6: THEMATIC_ALIGNMENT_SUMMARY
        Validates semantic alignment between summary and primary theme
        """
        if self.target_theme_embeddings.size == 0:
            return ValidationResult(
                rule_id="THEMATIC_ALIGNMENT_SUMMARY",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="Skipped (no theme embeddings)"
            )
        
        summary = buffer.get("K.1_Executive_Summary") or buffer.get("K1_EXECUTIVE_SUMMARY") or ""
        if not summary:
            return ValidationResult(
                rule_id="THEMATIC_ALIGNMENT_SUMMARY",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Cannot validate alignment: summary missing"
            )
        
        summary_embedding = np.array([self.embedding_client.embed(summary)])
        similarity = cosine_similarity(summary_embedding, self.target_theme_embeddings).mean()
        
        threshold = 0.60
        passed = similarity >= threshold
        severity = ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO
        
        return ValidationResult(
            rule_id="THEMATIC_ALIGNMENT_SUMMARY",
            passed=passed,
            severity=severity,
            message=f"Summary-theme alignment: {similarity:.2%} (threshold: {threshold:.0%})",
            details={"actual_similarity": similarity, "threshold": threshold}
        )

    def check_placeholder_detected(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        Rule 7: PLACEHOLDER_DETECTED
        Detects any placeholder text that wasn't sanitized
        """
        placeholder_pattern = re.compile(r"\[(INSERT|PLACEHOLDER|TODO|FILL IN|COMPANY|ROLE).*?\]", re.IGNORECASE)
        placeholders = placeholder_pattern.findall(all_text)
        
        passed = len(placeholders) == 0
        severity = ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO
        
        return ValidationResult(
            rule_id="PLACEHOLDER_DETECTED",
            passed=passed,
            severity=severity,
            message=f"Found {len(placeholders)} placeholder(s)" if not passed else "No placeholders found",
            details={"placeholders": placeholders}
        )

    def check_unify_overview_constraints(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        Rule 8: UNIFY_OVERVIEW_CONSTRAINTS
        Validates Unify overview section word count
        """
        overview = buffer.get("K.2_Unify_Overview") or buffer.get("K2_UNIFY_OVERVIEW") or ""
        
        if not overview:
            return ValidationResult(
                rule_id="UNIFY_OVERVIEW_CONSTRAINTS",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="Unify overview not present (optional)"
            )
        
        word_count = len(overview.split())
        min_wc = CONSTRAINTS.UNIFY_OVERVIEW_WORD_COUNT_MIN
        max_wc = CONSTRAINTS.UNIFY_OVERVIEW_WORD_COUNT_MAX
        
        passed = min_wc <= word_count <= max_wc
        severity = ValidationSeverity.LOW if not passed else ValidationSeverity.INFO
        
        return ValidationResult(
            rule_id="UNIFY_OVERVIEW_CONSTRAINTS",
            passed=passed,
            severity=severity,
            message=f"Unify overview: {word_count} words (target: {min_wc}-{max_wc})",
            details={"word_count": word_count, "min": min_wc, "max": max_wc}
        )

    def check_ibm_overview_constraints(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        Rule 9: IBM_OVERVIEW_CONSTRAINTS
        Validates IBM overview section word count
        """
        overview = buffer.get("K.3_IBM_Overview") or buffer.get("K3_IBM_OVERVIEW") or ""
        
        if not overview:
            return ValidationResult(
                rule_id="IBM_OVERVIEW_CONSTRAINTS",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="IBM overview not present (optional)"
            )
        
        word_count = len(overview.split())
        min_wc = CONSTRAINTS.IBM_OVERVIEW_WORD_COUNT_MIN
        max_wc = CONSTRAINTS.IBM_OVERVIEW_WORD_COUNT_MAX
        
        passed = min_wc <= word_count <= max_wc
        severity = ValidationSeverity.LOW if not passed else ValidationSeverity.INFO
        
        return ValidationResult(
            rule_id="IBM_OVERVIEW_CONSTRAINTS",
            passed=passed,
            severity=severity,
            message=f"IBM overview: {word_count} words (target: {min_wc}-{max_wc})",
            details={"word_count": word_count, "min": min_wc, "max": max_wc}
        )

    def check_bullet_count_validity(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        Rule 10: BULLET_COUNT_VALIDITY
        Validates that bullet sections have reasonable counts
        """
        bullet_sections = {
            "K.2_Unify_Bullets": buffer.get("K.2_Unify_Bullets") or buffer.get("K2_UNIFY_BULLETS"),
            "K.3_IBM_Bullets": buffer.get("K.3_IBM_Bullets") or buffer.get("K3_IBM_BULLETS")
        }
        
        issues = []
        for section_key, bullets in bullet_sections.items():
            if bullets and isinstance(bullets, list):
                count = len(bullets)
                if count < 2:
                    issues.append(f"{section_key} has only {count} bullet(s)")
                elif count > 10:
                    issues.append(f"{section_key} has too many bullets ({count})")
        
        passed = len(issues) == 0
        severity = ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO
        
        return ValidationResult(
            rule_id="BULLET_COUNT_VALIDITY",
            passed=passed,
            severity=severity,
            message="All bullet counts valid" if passed else f"Issues: {'; '.join(issues)}",
            details={"issues": issues}
        )

    def check_narrative_proportion(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        Rule 11: NARRATIVE_PROPORTION
        Validates that narrative sections exist and are proportional
        """
        narratives = {
            "TraderSense": buffer.get("K.4_TraderSense_Narrative"),
            "EY": buffer.get("K.5_EY_Narrative"),
            "Early_Career": buffer.get("K.6_Early_Career_Narrative")
        }
        
        narrative_word_counts = {
            k: len(v.split()) if v else 0
            for k, v in narratives.items()
        }
        
        total_narrative_words = sum(narrative_word_counts.values())
        total_words = len(all_text.split())
        
        if total_words == 0:
            return ValidationResult(
                rule_id="NARRATIVE_PROPORTION",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="No content to validate"
            )
        
        narrative_proportion = total_narrative_words / total_words
        
        # Narratives should be 5-15% of total content
        passed = 0.05 <= narrative_proportion <= 0.15
        severity = ValidationSeverity.LOW if not passed else ValidationSeverity.INFO
        
        return ValidationResult(
            rule_id="NARRATIVE_PROPORTION",
            passed=passed,
            severity=severity,
            message=f"Narrative proportion: {narrative_proportion:.1%} of total (target: 5-15%)",
            details={
                "narrative_words": total_narrative_words,
                "total_words": total_words,
                "proportion": narrative_proportion,
                "counts": narrative_word_counts
            }
        )

    def check_ascii_only(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        Rule 12: ASCII_ONLY
        Validates that content uses only ASCII characters (no smart quotes, etc.)
        """
        non_ascii_chars = [c for c in all_text if ord(c) > 127]
        
        passed = len(non_ascii_chars) == 0
        severity = ValidationSeverity.LOW if not passed else ValidationSeverity.INFO
        
        unique_non_ascii = list(set(non_ascii_chars))[:10]  # Show first 10 unique
        
        return ValidationResult(
            rule_id="ASCII_ONLY",
            passed=passed,
            severity=severity,
            message=f"Found {len(non_ascii_chars)} non-ASCII character(s)" if not passed else "All ASCII",
            details={"non_ascii_count": len(non_ascii_chars), "examples": unique_non_ascii}
        )

    def check_section_completeness(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        Rule 13: SECTION_COMPLETENESS
        Validates that critical sections are present
        """
        required_sections = [
            "K.0_Headline",
            "K.1_Executive_Summary"
        ]
        
        missing = []
        for section in required_sections:
            content = buffer.get(section)
            if not content or (isinstance(content, str) and len(content.strip()) < 10):
                missing.append(section)
        
        passed = len(missing) == 0
        severity = ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO
        
        return ValidationResult(
            rule_id="SECTION_COMPLETENESS",
            passed=passed,
            severity=severity,
            message="All required sections present" if passed else f"Missing: {', '.join(missing)}",
            details={"missing_sections": missing}
        )

# --- Main Execution ---

def run_hop_5(args: argparse.Namespace):
    """Execute HOP-5 comprehensive validation"""
    logger, _ = setup_workflow_logging(args.workflow_id, log_file_dir=args.run_dir)
    logger.info("--- Starting HOP-5: Comprehensive Validation [13 Rules] ---")
    start_time = datetime.now()

    try:
        # Load staging buffer
        try:
            with open(args.input_path_staging_buffer, 'r', encoding='utf-8') as f:
                staging_data = json.load(f)
            staging_buffer = ImmutableStagingBuffer.from_dict(
                staging_data.get("staging_buffer_data", {}), locked=True
            )
            logger.info(f"Loaded staging buffer from {args.input_path_staging_buffer}")
        except Exception as e:
            raise HopExecutionError(f"Failed to load staging buffer: {e}") from e

        # Load thematic analysis
        try:
            with open(args.input_path_thematic_analysis, 'r', encoding='utf-8') as f:
                thematic_data = json.load(f)
            thematic_analysis = ThematicAnalysis.from_dict(thematic_data)
            logger.info(f"Loaded thematic analysis")
        except Exception as e:
            raise HopExecutionError(f"Failed to load thematic analysis: {e}") from e

        # Load job description
        try:
            with open(args.jd, 'r', encoding='utf-8') as f:
                job_description = f.read()
            logger.info(f"Loaded job description")
        except Exception as e:
            raise HopExecutionError(f"Failed to load job description: {e}") from e

        # Create validation engine
        constraints = {}  # Could load from config
        validator = ValidationEngine(constraints, thematic_analysis, job_description)

        # Run all validations
        validation_results = validator.validate_all(staging_buffer)

        # Generate summary
        passed = sum(1 for r in validation_results if r.passed)
        failed = len(validation_results) - passed
        critical_failures = sum(1 for r in validation_results 
                               if not r.passed and r.severity == ValidationSeverity.CRITICAL)

        summary = {
            "total": len(validation_results),
            "passed": passed,
            "failed": failed,
            "critical_failures": critical_failures
        }

        logger.info(f"Validation summary: {passed}/{len(validation_results)} passed, "
                   f"{critical_failures} critical failures")

        # Prepare output
        output_data = {
            "validation_results": [default_serializer(vr) for vr in validation_results],
            "summary": summary
        }

        # Write output
        try:
            output_path = Path(args.output_path_validation_results)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=default_serializer)
            logger.info(f"Successfully wrote validation results to {output_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to write output: {e}") from e

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-5 Finished Successfully ({duration:.2f}s) ---")
        print("API Calls Made: 0")

    except HopExecutionError as he:
        logger.error(f"HOP-5 HALTED: {he}", exc_info=False)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-5 Finished with HALT ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        exit(1)
    except Exception as e:
        logger.error(f"HOP-5 FAILED with unexpected error: {e}", exc_info=True)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-5 Finished with FAILURE ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HOP-5: Comprehensive Validation [13 Rules]")
    parser.add_argument("--workflow-id", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--config-path", required=True)
    parser.add_argument("--input-path-staging-buffer", required=True)
    parser.add_argument("--input-path-thematic-analysis", required=True)
    parser.add_argument("--jd", required=True)
    parser.add_argument("--output-path-validation-results", required=True)

    args = parser.parse_args()
    run_hop_5(args)
