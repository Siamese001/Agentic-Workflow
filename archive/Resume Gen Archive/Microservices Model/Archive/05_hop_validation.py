# hops/hop_5_validation.py
"""
Hop 5: Comprehensive Validation - HIGH-SIGNAL OVERWRITE

This advanced validator uses the HOP-0 RAG analysis as a
ground-truth "answer key" to validate the final generated content
from the HOP-4 staging buffer.

It performs:
1.  Semantic Alignment Validation (Vector-based)
2.  Thematic & Keyword Coverage Checks
3.  Narrative Inclusion Checks
4.  Standard Linting & Placeholder Detection
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Set

# --- High-Signal Imports ---
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import necessary components
from helpers import (
    setup_workflow_logging, HopExecutionError, default_serializer,
    ValidationResult, ValidationSeverity, ThematicAnalysis, ImmutableStagingBuffer
)

# --- Mock Components (for high-signal orchestration) ---
class EmbeddingClient:
    """Mock EmbeddingClient to vectorize HOP-0 themes and HOP-4 content."""
    def __init__(self, config=None):
        logging.info("Initialized MOCK EmbeddingClient for HOP-5")
        self.dimension = 768 # Must match HOP-1/HOP-3 dimension
    
    def embed(self, text: str) -> List[float]:
        """Generates a mock, deterministic embedding."""
        if not text: return [0.0] * self.dimension
        hash_val = hash(text)
        np.random.seed(hash_val % (2**32 - 1))
        return np.random.rand(self.dimension).tolist()
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generates mock embeddings for a batch of texts."""
        return np.array([self.embed(text) for text in texts])

# --- End Mock Components ---


class ValidationEngine:
    """
    High-Signal Validation Engine.
    Validates generated content (HOP-4) against RAG analysis (HOP-0).
    """
    def __init__(self, constraints: Dict, thematic_analysis: ThematicAnalysis, job_description: str):
        self.constraints = constraints or {}
        self.thematic_analysis = thematic_analysis
        self.job_description = job_description
        self.logger = logging.getLogger(__name__)
        
        self.embedding_client = EmbeddingClient()
        
        # Pre-calculate target vectors from HOP-0
        self.target_theme_embeddings, self.target_keywords = self._get_target_vectors()

    def _get_target_vectors(self) -> Tuple[np.ndarray, Set[str]]:
        """Generates vector embeddings for the key themes from HOP-0."""
        self.logger.info("Vectorizing HOP-0 thematic targets for validation...")
        targets = []
        keywords = set()
        
        if self.thematic_analysis.primary_theme:
            targets.append(self.thematic_analysis.primary_theme.get("name", ""))
            targets.extend(self.thematic_analysis.primary_theme.get("keywords", []))
            keywords.update(self.thematic_analysis.primary_theme.get("keywords", []))
        
        # Add secondary themes
        # (Assuming 'secondary_themes' is a field in ThematicAnalysis)
        if hasattr(self.thematic_analysis, 'secondary_themes'):
            for theme in self.thematic_analysis.secondary_themes:
                 targets.append(theme.get("name", ""))
                 keywords.update(theme.get("keywords", []))

        targets = [t for t in targets if t]
        if not targets:
            self.logger.warning("No thematic targets found in HOP-0. Semantic validation will be skipped.")
            return np.array([]), set()
            
        return self.embedding_client.embed_batch(targets), keywords

    def _extract_all_text(self, staging_buffer: ImmutableStagingBuffer) -> str:
        """Concatenates all generated text pieces into a single string."""
        all_text = []
        for key, content in staging_buffer.data.items():
            if isinstance(content, str):
                all_text.append(content)
            elif isinstance(content, list):
                all_text.extend([str(item) for item in content])
        return " ".join(all_text)

    def validate_all(self, staging_buffer: ImmutableStagingBuffer) -> List[ValidationResult]:
        """Runs all validation rules."""
        self.logger.info("--- Starting High-Signal Validation Engine ---")
        
        # Discover all rule methods (methods starting with 'check_')
        all_rules = [
            getattr(self, func) for func in dir(self)
            if callable(getattr(self, func)) and func.startswith('check_')
        ]
        
        # Get a single blob of text for rules that need it
        all_generated_text = self._extract_all_text(staging_buffer)
        
        results = []
        for rule in all_rules:
            try:
                results.append(rule(staging_buffer, all_generated_text))
            except Exception as e:
                self.logger.error(f"Validation rule {rule.__name__} failed to execute: {e}")
                results.append(ValidationResult(
                    rule_id=f"ENGINE_FAILURE_{rule.__name__}",
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Rule execution error: {e}"
                ))
        
        self.logger.info(f"--- Validation Complete: {len(results)} rules executed ---")
        return results

    # --- VALIDATION RULES ---
    
    def check_thematic_alignment(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        [HIGH-SIGNAL] Checks if the K.1 Summary is semantically
        aligned with the HOP-0 primary theme.
        """
        rule_id = "THEMATIC_ALIGNMENT_SUMMARY"
        
        if self.target_theme_embeddings.size == 0:
            return ValidationResult(rule_id, True, ValidationSeverity.INFO, "Skipped (No HOP-0 themes)")
        
        summary_text = buffer.data.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value, "")
        if not summary_text:
            return ValidationResult(rule_id, False, ValidationSeverity.HIGH, "K.1 Executive Summary is missing.")
            
        summary_embedding = self.embedding_client.embed(summary_text)
        
        similarity_matrix = cosine_similarity([summary_embedding], self.target_theme_embeddings)
        max_similarity = similarity_matrix.max()
        
        threshold = self.constraints.get("min_theme_similarity", 0.60)
        passed = max_similarity >= threshold
        
        return ValidationResult(
            rule_id=rule_id,
            passed=passed,
            severity=ValidationSeverity.HIGH if not passed else ValidationSeverity.INFO,
            message=f"Summary semantic alignment to HOP-0 themes: {max_similarity:.2f} (Threshold: {threshold})",
            details={"actual_similarity": max_similarity, "threshold": threshold}
        )

    def check_keyword_coverage(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        [HIGH-SIGNAL] Checks what percentage of HOP-0 keywords
        are present in the final generated text.
        """
        rule_id = "KEYWORD_COVERAGE"
        
        if not self.target_keywords:
            return ValidationResult(rule_id, True, ValidationSeverity.INFO, "Skipped (No HOP-0 keywords)")
            
        text_lower = all_text.lower()
        found_keywords = {kw for kw in self.target_keywords if kw.lower() in text_lower}
        
        coverage = len(found_keywords) / len(self.target_keywords)
        threshold = self.constraints.get("min_keyword_coverage", 0.75)
        passed = coverage >= threshold

        return ValidationResult(
            rule_id=rule_id,
            passed=passed,
            severity=ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO,
            message=f"Found {len(found_keywords)}/{len(self.target_keywords)} target keywords. Coverage: {coverage:.1%}",
            details={"found": list(found_keywords), "missing": list(self.target_keywords - found_keywords)}
        )
        
    def check_narrative_inclusion(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        [HIGH-SIGNAL] Checks if problem/solution narratives from HOP-0
        are reflected in the text. (Simple keyword check)
        """
        rule_id = "NARRATIVE_INCLUSION"
        narratives = getattr(self.thematic_analysis, 'problem_solution_narratives', [])
        if not narratives:
            return ValidationResult(rule_id, True, ValidationSeverity.INFO, "Skipped (No HOP-0 narratives)")
        
        # Simple check: look for keywords from the first narrative
        narrative_keywords = narratives[0].get("problem_keywords", []) + narratives[0].get("solution_keywords", [])
        if not narrative_keywords:
             return ValidationResult(rule_id, True, ValidationSeverity.INFO, "Skipped (Narrative has no keywords)")
        
        text_lower = all_text.lower()
        found = any(kw.lower() in text_lower for kw in narrative_keywords)
        
        return ValidationResult(
            rule_id=rule_id,
            passed=found,
            severity=ValidationSeverity.MEDIUM,
            message="Generated text does not appear to reference the core problem/solution narrative." if not found else "Generated text includes core narrative elements."
        )

    def check_input_signal_quality(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """
        [HIGH-SIGNAL] Logs the input signal quality from HOP-0 as an
        informational check for the final QA report.
        """
        score = self.thematic_analysis.signal_quality_score
        severity = ValidationSeverity.INFO
        if score < 0.5:
            severity = ValidationSeverity.WARNING # Flag for manual review
            
        return ValidationResult(
            rule_id="INPUT_SIGNAL_QUALITY",
            passed=True,
            severity=severity,
            message=f"Source HOP-0 RAG signal quality was {score:.2f}. Low signal may impact output quality.",
            details={"signal_quality": score}
        )

    def check_word_count(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """[STANDARD] Checks total document word count."""
        rule_id = "WORD_COUNT_TOTAL"
        count = len(all_text.split())
        
        min_wc = self.constraints.get("min_word_count", 800)
        max_wc = self.constraints.get("max_word_count", 1100)
        passed = min_wc <= count <= max_wc

        return ValidationResult(
            rule_id=rule_id,
            passed=passed,
            severity=ValidationSeverity.HIGH,
            message=f"Total word count: {count} (Target: {min_wc}-{max_wc})",
            details={"actual": count, "min": min_wc, "max": max_wc}
        )
        
    def check_placeholder_detection(self, buffer: ImmutableStagingBuffer, all_text: str) -> ValidationResult:
        """[STANDARD] Scans for mock or placeholder text."""
        rule_id = "PLACEHOLDER_DETECTED"
        
        # Regex to find [INSERT...], MOCK, or ERROR:
        matches = re.findall(r"\[INSERT.*\]|MOCK|ERROR:|Failed to generate", all_text, re.IGNORECASE)
        passed = not matches
        
        return ValidationResult(
            rule_id=rule_id,
            passed=passed,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            message=f"Found {len(matches)} placeholder/error strings in final text." if not passed else "No placeholders found.",
            details={"matches": matches}
        )

# --- End ValidationEngine ---

def run_hop_5(args: argparse.Namespace):
    """Executes the HOP-5 validation logic."""
    logger, _ = setup_workflow_logging(args.workflow_id, log_file_dir=args.run_dir)
    logger.info("--- Starting HOP-5: Comprehensive Validation [v-HighSignal] ---")
    start_time = datetime.now()

    try:
        # Load inputs (All inputs are required for this advanced model)
        try:
            with open(args.input_path_staging_buffer, 'r', encoding='utf-8') as f:
                buffer_data = json.load(f)
            staging_buffer = ImmutableStagingBuffer.from_dict(
                buffer_data.get("staging_buffer_data", {}),
                locked=True
            )
            logger.info(f"Loaded staging buffer from {args.input_path_staging_buffer}")
            
            with open(args.input_path_thematic_analysis, 'r', encoding='utf-8') as f:
                thematic_analysis = ThematicAnalysis.from_dict(json.load(f))
            logger.info(f"Loaded thematic analysis from {args.input_path_thematic_analysis}")
            
            jd_path = Path(args.input_path_jd)
            job_description = jd_path.read_text(encoding='utf-8')
            logger.info(f"Loaded job description from {jd_path}")
            
            # Load constraints from config (mocked as empty dict for now)
            constraints = {}
            logger.info("Mocked validation constraints. (Load from config in prod)")
            
        except Exception as e:
            raise HopExecutionError(f"Failed to load input files: {e}") from e

        # Instantiate the High-Signal Validation Engine
        validator = ValidationEngine(constraints, thematic_analysis, job_description)

        # Execute validation
        validation_results = validator.validate_all(staging_buffer)

        # Analyze results
        total_checks = len(validation_results)
        failed_checks = [vr for vr in validation_results if not vr.passed]
        critical_failures = [vr for vr in failed_checks if vr.severity == ValidationSeverity.CRITICAL]
        
        logger.info(f"Validation complete. Total checks: {total_checks}")
        logger.info(f"Failed checks: {len(failed_checks)}")
        logger.info(f"Critical failures: {len(critical_failures)}")

        # Prepare output
        output_data = {
            "validation_results": [default_serializer(vr) for vr in validation_results],
            "summary": {
                "total_checks": total_checks,
                "failed_checks": len(failed_checks),
                "critical_failures": len(critical_failures),
                "passed_checks": total_checks - len(failed_checks)
            }
        }

        # Write output
        try:
            output_path = Path(args.output_path_validation_results)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=default_serializer)
            logger.info(f"Successfully wrote validation results to {output_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to write output JSON: {e}") from e

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-5 Finished Successfully ({duration:.2f}s) ---")
        print("API Calls Made: 0")  # Validation makes no API calls

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
    parser = argparse.ArgumentParser(description="HOP-5: Comprehensive Validation [v-HighSignal]")
    parser.add_argument("--workflow-id", required=True, help="Unique ID for the workflow run")
    parser.add_argument("--run-dir", required=True, help="Directory for the workflow run artifacts")
    parser.add_argument("--config-path", required=True, help="Path to the config file snapshot")
    parser.add_argument("--input-path-staging-buffer", required=True, help="Path to the staging buffer JSON")
    parser.add_argument("--input-path-thematic-analysis", required=True, help="Path to the thematic analysis JSON")
    parser.add_argument("--input-path-jd", required=True, help="Path to the job description text file")
    parser.add_argument("--output-path-validation-results", required=True, help="Path to write the validation results JSON")

    args = parser.parse_args()
    run_hop_5(args)