# hops/04_hop_staging.py
"""
Hop 4: Staging and Sanitization with Signal Score Calculation

This hop:
1. Cleans and sanitizes LLM output
2. Validates structural integrity
3. Calculates per-section signal scores using ThematicAnalysis
4. Creates ImmutableStagingBuffer
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Union

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import necessary components from helpers
from helpers import (
    setup_workflow_logging, HopExecutionError, default_serializer,
    ImmutableStagingBuffer, ResumeSection, ThematicAnalysis, calculate_signal_score
)

# --- Content Sanitizer with Signal Scoring ---

class ContentSanitizer:
    """
    Robust sanitizer that cleans LLM output and calculates signal quality scores
    """
    
    def __init__(self, artist_specs: Dict, thematic_analysis: ThematicAnalysis):
        self.logger = logging.getLogger(__name__)
        self.artist_specs = artist_specs
        self.thematic_analysis = thematic_analysis
        
        # Regex patterns for cleaning
        self.artifact_patterns = re.compile(
            r"^(Here's the generated content:|Here is the summary:|Certainly!|Here's the [a-zA-Z\s]+:)\s*",
            re.IGNORECASE | re.MULTILINE
        )
        
        self.markdown_patterns = re.compile(r"^(#+\s*|\*+\s*|-\s*)", re.MULTILINE)
        self.placeholder_pattern = re.compile(r"\[(INSERT|PLACEHOLDER|TODO|FILL IN).*?\]", re.IGNORECASE)

    def _clean_text_artifacts(self, text: str) -> str:
        """Remove conversational intros and markdown"""
        if not isinstance(text, str):
            return text
        text = self.artifact_patterns.sub("", text)
        text = self.markdown_patterns.sub("", text)
        return text.strip()

    def _find_placeholders(self, text: str) -> List[str]:
        """Find remaining placeholders"""
        if not isinstance(text, str):
            return []
        return self.placeholder_pattern.findall(text)

    def _unify_structure(self, section_key: str, content: Any) -> Union[str, List[str]]:
        """
        Ensure content structure matches spec
        """
        # Sections that should be lists
        list_sections = [
            ResumeSection.K2_UNIFY_BULLETS.value,
            ResumeSection.K3_IBM_BULLETS.value,
            "K.2_Unify_Bullets",
            "K.3_IBM_Bullets"
        ]
        
        if section_key in list_sections:
            if isinstance(content, list):
                return [self._clean_text_artifacts(item) for item in content if item.strip()]
            
            if isinstance(content, str):
                self.logger.warning(f"Structural mismatch for {section_key}: Expected List, got String. Splitting.")
                bullets = [
                    self._clean_text_artifacts(line)
                    for line in content.split('\n')
                    if line.strip() and not line.strip().startswith("-")
                ]
                return [b for b in bullets if b]
        
        # Default: string sections
        if isinstance(content, str):
            return self._clean_text_artifacts(content)
            
        return content

    def _calculate_section_signal_score(self, content: Any) -> float:
        """
        Calculate signal quality score for section content using ThematicAnalysis
        """
        if not content:
            return 0.0
        
        # Use calculate_signal_score from helpers
        score = calculate_signal_score(content, self.thematic_analysis)
        
        self.logger.debug(f"Section signal score: {score:.3f}")
        return score

    def sanitize_and_stage(self, artist_output: Dict) -> Tuple[ImmutableStagingBuffer, Dict]:
        """
        Sanitize content, calculate signal scores, and create staging buffer
        
        Returns:
            - ImmutableStagingBuffer with cleaned content
            - Metadata dict with section stats and signal scores
        """
        self.logger.info("Starting content sanitization and signal scoring...")
        staging_buffer = ImmutableStagingBuffer()
        
        output_metadata = {
            "sections_staged": 0,
            "placeholders_found": 0,
            "structural_corrections": 0,
            "signal_scores": {},
            "average_signal_score": 0.0
        }
        
        signal_scores = []
        
        for section_key, content in artist_output.items():
            if not content:
                self.logger.warning(f"Skipping empty content for section {section_key}")
                continue

            # 1. Unify structure
            original_type = type(content)
            clean_content = self._unify_structure(section_key, content)
            if original_type == str and isinstance(clean_content, list):
                output_metadata["structural_corrections"] += 1
                self.logger.info(f"Corrected structure for {section_key}: str -> list")

            # 2. Calculate signal score for this section
            section_signal_score = self._calculate_section_signal_score(clean_content)
            output_metadata["signal_scores"][section_key] = section_signal_score
            signal_scores.append(section_signal_score)

            # 3. Inject section metadata
            section_meta = {
                "signal_score": section_signal_score
            }
            
            placeholders = []
            
            if isinstance(clean_content, str):
                section_meta["word_count"] = len(clean_content.split())
                section_meta["char_count"] = len(clean_content)
                placeholders = self._find_placeholders(clean_content)
                
            elif isinstance(clean_content, list):
                section_meta["bullet_count"] = len(clean_content)
                for item in clean_content:
                    placeholders.extend(self._find_placeholders(item))

            if placeholders:
                self.logger.error(f"CRITICAL: Found placeholders in {section_key}: {placeholders}")
                output_metadata["placeholders_found"] += len(placeholders)
                section_meta["placeholders"] = placeholders

            # 4. Set data in buffer
            staging_buffer.set(section_key, clean_content)
            
            # Store metadata
            output_metadata[section_key] = section_meta
            output_metadata["sections_staged"] += 1

        # 5. Calculate average signal score
        if signal_scores:
            output_metadata["average_signal_score"] = sum(signal_scores) / len(signal_scores)
            self.logger.info(f"Average signal score across all sections: {output_metadata['average_signal_score']:.3f}")
        else:
            self.logger.warning("No signal scores calculated")

        # 6. Lock buffer
        staging_buffer.lock()
        self.logger.info(f"Staging buffer locked. Placeholders: {output_metadata['placeholders_found']}, "
                        f"Corrections: {output_metadata['structural_corrections']}, "
                        f"Avg Signal: {output_metadata['average_signal_score']:.3f}")
        
        output_metadata["locked"] = staging_buffer.is_locked()
        output_metadata["lock_timestamp"] = staging_buffer._lock_timestamp
        
        return staging_buffer, output_metadata

# --- Main Execution ---

def run_hop_4(args: argparse.Namespace):
    """Execute HOP-4 staging and sanitization with signal scoring"""
    logger, _ = setup_workflow_logging(args.workflow_id, log_file_dir=args.run_dir)
    logger.info("--- Starting HOP-4: Staging with Signal Scoring [v-HighSignal] ---")
    start_time = datetime.now()

    try:
        # Load artist output
        try:
            with open(args.input_path_artist_output, 'r', encoding='utf-8') as f:
                artist_data = json.load(f)
            artist_output = artist_data.get("artist_output", {})
            logger.info(f"Loaded artist output from {args.input_path_artist_output}")
        except Exception as e:
            raise HopExecutionError(f"Failed to load artist output: {e}") from e

        # Load thematic analysis for signal scoring
        try:
            with open(args.input_path_thematic_analysis, 'r', encoding='utf-8') as f:
                thematic_data = json.load(f)
            thematic_analysis = ThematicAnalysis.from_dict(thematic_data)
            logger.info(f"Loaded thematic analysis for signal scoring")
        except Exception as e:
            raise HopExecutionError(f"Failed to load thematic analysis: {e}") from e

        # Load artist specs
        try:
            with open(args.artist_specs_path, 'r', encoding='utf-8') as f:
                artist_specs = json.load(f)
            logger.info(f"Loaded artist specs from {args.artist_specs_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to load artist specs: {e}") from e

        # Create sanitizer with signal scoring capability
        sanitizer = ContentSanitizer(artist_specs, thematic_analysis)
        staging_buffer, staging_metadata = sanitizer.sanitize_and_stage(artist_output)
        
        # Check for critical failures
        if staging_metadata["placeholders_found"] > 0:
            logger.error("Sanitization failed: Placeholders were found in generated text")
        
        if staging_metadata["average_signal_score"] < 0.3:
            logger.warning(f"Low average signal score: {staging_metadata['average_signal_score']:.3f}")

        # Prepare output
        output_data = {
            "staging_buffer_data": staging_buffer.data,
            "staging_metadata": staging_metadata
        }

        # Write output
        try:
            output_path = Path(args.output_path_staging_buffer)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=default_serializer)
            logger.info(f"Successfully wrote staging buffer to {output_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to write output JSON: {e}") from e

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-4 Finished Successfully ({duration:.2f}s) ---")
        print("API Calls Made: 0")

    except HopExecutionError as he:
        logger.error(f"HOP-4 HALTED: {he}", exc_info=False)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-4 Finished with HALT ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        exit(1)
    except Exception as e:
        logger.error(f"HOP-4 FAILED with unexpected error: {e}", exc_info=True)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-4 Finished with FAILURE ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HOP-4: Staging with Signal Scoring [v-HighSignal]")
    parser.add_argument("--workflow-id", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--config-path", required=True)
    parser.add_argument("--artist-specs-path", required=True)
    parser.add_argument("--input-path-artist-output", required=True)
    parser.add_argument("--input-path-thematic-analysis", required=True)
    parser.add_argument("--output-path-staging-buffer", required=True)

    args = parser.parse_args()
    run_hop_4(args)
