# hops/hop_4_staging.py
"""
Hop 4: Staging and Sanitization - HIGH-SIGNAL OVERWRITE

This hop is a deterministic "data integrity" layer. It cleans, validates,
and finalizes the creative output from HOP-3 before it can be validated
or rendered.

Its responsibilities are:
1.  Remove all AI/LLM generation artifacts (e.g., "Certainly!", markdown).
2.  Perform structural unification (e.g., split string-based lists into List[str]).
3.  Sanitize any remaining placeholders (e.g., "[Insert Metric]").
4.  Inject per-section metadata (word counts, bullet counts) for granular
    validation in HOP-5.
5.  Create and lock the final ImmutableStagingBuffer.
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

# Import necessary components
from helpers import (
    setup_workflow_logging, HopExecutionError, default_serializer,
    ImmutableStagingBuffer, ResumeSection
)

# --- High-Signal Sanitizer ---

class ContentSanitizer:
    """
    A robust, rule-based sanitizer to clean LLM output.
    This is deterministic and does not use AI.
    """
    
    def __init__(self, artist_specs: Dict):
        self.logger = logging.getLogger(__name__)
        self.artist_specs = artist_specs # Specs define expected structure
        
        # Regex to find and remove common LLM conversational artifacts
        self.artifact_patterns = re.compile(
            r"^(Here's the generated content:|Here is the summary:|Certainly!|Here's the [a-zA-Z\s]+:)\s*",
            re.IGNORECASE | re.MULTILINE
        )
        
        # Regex to remove markdown that shouldn't be in the final data
        self.markdown_patterns = re.compile(r"^(#+\s*|\*+\s*|-\s*)", re.MULTILINE)
        
        # Regex to find remaining placeholders
        self.placeholder_pattern = re.compile(r"\[(INSERT|PLACEHOLDER|TODO|FILL IN).*?\]", re.IGNORECASE)

    def _clean_text_artifacts(self, text: str) -> str:
        """Removes conversational intros and markdown."""
        if not isinstance(text, str):
            return text
        text = self.artifact_patterns.sub("", text)
        text = self.markdown_patterns.sub("", text)
        return text.strip()

    def _find_placeholders(self, text: str) -> List[str]:
        """Finds, but does not remove, placeholders."""
        if not isinstance(text, str):
            return []
        return self.placeholder_pattern.findall(text)

    def _unify_structure(self, section_key: str, content: Any) -> Union[str, List[str]]:
        """
        Ensures content structure matches spec.
        If spec expects a list (e.g., bullets) but LLM gave a single
        string with newlines, this splits it.
        """
        
        # This is a mock; a real impl would look up the section spec
        # e.g., if self.artist_specs.get(section_key, {}).get("type") == "list":
        if section_key in [ResumeSection.K2_UNIFY_BULLETS.value, ResumeSection.K3_UNIFY_BULLETS.value]:
            
            # Case 1: Already a list. Sanitize each item.
            if isinstance(content, list):
                return [self._clean_text_artifacts(item) for item in content if item.strip()]

            # Case 2: A single string that needs to be split
            if isinstance(content, str):
                self.logger.warning(f"Structural mismatch for {section_key}: "
                                    f"Expected List, got String. Attempting to split.")
                # Split by newline, then clean artifacts from each line
                bullets = [
                    self._clean_text_artifacts(line) 
                    for line in content.split('\n') 
                    if line.strip() and not line.strip().startswith("-") # Avoid empty/marker lines
                ]
                return [b for b in bullets if b] # Filter empty strings
        
        # Default case: It's a string (e.g., Summary). Just clean it.
        if isinstance(content, str):
            return self._clean_text_artifacts(content)
            
        return content # Return as-is if type is unknown

    def sanitize_and_stage(self, artist_output: Dict) -> Tuple[ImmutableStagingBuffer, Dict]:
        """
        Iterates over all artist content, sanitizes, validates structure,
        and injects metadata.
        
        Returns:
            - The locked ImmutableStagingBuffer.
            - A metadata dictionary for the final output file.
        """
        self.logger.info("Starting content sanitization and staging...")
        staging_buffer = ImmutableStagingBuffer()
        output_metadata = {
            "sections_staged": 0,
            "placeholders_found": 0,
            "structural_corrections": 0
        }
        
        for section_key, content in artist_output.items():
            if not content:
                self.logger.warning(f"Skipping empty content for section {section_key}")
                continue

            # 1. Unify Structure (e.g., str -> list)
            original_type = type(content)
            clean_content = self._unify_structure(section_key, content)
            if original_type == str and isinstance(clean_content, list):
                output_metadata["structural_corrections"] += 1

            # 2. Inject Metadata and Find Placeholders
            section_meta = {}
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
                # Add to metadata for HOP-5 to see
                section_meta["placeholders"] = placeholders

            # 3. Set data in the buffer
            # The buffer stores the content itself.
            staging_buffer.set(section_key, clean_content)
            
            # We store the *metadata about* the content in our own dict.
            output_metadata[section_key] = section_meta
            output_metadata["sections_staged"] += 1

        # 4. Lock the buffer
        staging_buffer.lock()
        self.logger.info(f"Staging buffer locked. "
                         f"Placeholders: {output_metadata['placeholders_found']}, "
                         f"Corrections: {output_metadata['structural_corrections']}")
        
        output_metadata["locked"] = staging_buffer.is_locked()
        output_metadata["lock_timestamp"] = staging_buffer._lock_timestamp
        
        return staging_buffer, output_metadata

# --- End Sanitizer ---

def run_hop_4(args: argparse.Namespace):
    """Executes the HOP-4 staging and sanitization logic."""
    logger, _ = setup_workflow_logging(args.workflow_id, log_file_dir=args.run_dir)
    logger.info("--- Starting HOP-4: Staging and Sanitization [v-HighSignal] ---")
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

        # Load artist specs (needed by sanitizer to know structure)
        try:
            with open(args.artist_specs_path, 'r', encoding='utf-8') as f:
                artist_specs = json.load(f)
            logger.info(f"Loaded artist specs from {args.artist_specs_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to load artist specs: {e}") from e

        # Instantiate and run the sanitizer
        # This is the core logic
        sanitizer = ContentSanitizer(artist_specs)
        staging_buffer, staging_metadata = sanitizer.sanitize_and_stage(artist_output)
        
        # Check for critical failures
        if staging_metadata["placeholders_found"] > 0:
            logger.error("Sanitization failed: Placeholders were found in the generated text.")
            # We still write the file so HOP-5 can explicitly fail on this
            # but we log it as a critical error.

        # Prepare output - serialize the buffer data and the new metadata
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
    parser = argparse.ArgumentParser(description="HOP-4: Staging and Sanitization [v-HighSignal]")
    parser.add_argument("--workflow-id", required=True, help="Unique ID for the workflow run")
    parser.add_argument("--run-dir", required=True, help="Directory for the workflow run artifacts")
    parser.add_argument("--config-path", required=True, help="Path to the config file snapshot")
    parser.add_argument("--artist-specs-path", required=True, help="Path to the artist specs JSON (for structural rules)")
    parser.add_argument("--input-path-artist-output", required=True, help="Path to the artist output JSON")
    parser.add_argument("--output-path-staging-buffer", required=True, help="Path to write the staging buffer JSON")

    args = parser.parse_args()
    run_hop_4(args)