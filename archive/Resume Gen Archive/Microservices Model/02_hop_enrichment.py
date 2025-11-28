# hops/hop_2_enrichment.py
"""
Hop 2: Data Enrichment.
Reads extracted clerk data and thematic analysis, enriches with canonical verbs
and duplicate detection, writes enriched scaffold as JSON.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import necessary components
from helpers import (
    setup_workflow_logging, HopExecutionError, default_serializer,
    ValidationResult, ValidationSeverity, ThematicAnalysis
)

# --- DataEnricher and Dependencies (Placeholder - Move to shared module) ---
class DuplicateDetector:
    """Placeholder duplicate detector"""
    def detect(self, bullets: List[str]) -> List[ValidationResult]:
        logging.warning("Using MOCK DuplicateDetector")
        return []

class DataEnricher:
    """HOP-2: Enrich bullet pool with canonical verbs, deduplication, etc."""
    
    CANONICAL_VERBS = {
        "led": ["led", "lead", "leading"], "built": ["built", "build", "building"],
        "drove": ["drove", "drive", "driving"], "launched": ["launched", "launch", "launching"],
        "scaled": ["scaled", "scale", "scaling"], "delivered": ["delivered", "deliver", "delivering"],
        "achieved": ["achieved", "achieve", "achieving"], "established": ["established", "establish", "establishing"],
        "managed": ["managed", "manage", "managing"], "developed": ["developed", "develop", "developing"]
    }

    def __init__(self):
        self.duplicate_detector = DuplicateDetector()

    def _canonicalize_verbs(self, text: str) -> List[str]:
        """Extract and canonicalize verbs from text."""
        text_lower = text.lower()
        return [
            canonical_form for canonical_form, variants in self.CANONICAL_VERBS.items()
            if any(variant in text_lower for variant in variants)
        ]

    def enrich(self, extracted_data: Dict, thematic_analysis: ThematicAnalysis) -> Tuple[Dict, List[ValidationResult]]:
        """
        Enrich extracted data with additional metadata.
        Returns: (enriched_data, validation_results)
        """
        validation_results = []
        
        # Enrich experience sections
        experience_sections = extracted_data.get("experience_sections", [])
        
        for section in experience_sections:
            for bullet in section.get("bullets", []):
                bullet_text = bullet.get("bullet_text", "")
                # Add canonical verbs
                bullet["canonical_verbs"] = self._canonicalize_verbs(bullet_text)
        
        # Collect all bullets for duplicate detection
        all_bullets = []
        for section in experience_sections:
            all_bullets.extend([b.get("bullet_text", "") for b in section.get("bullets", [])])
        
        # Run duplicate detection
        dup_results = self.duplicate_detector.detect(all_bullets)
        validation_results.extend(dup_results)
        
        # Construct enriched scaffold
        enriched_scaffold = {
            "experience_sections": experience_sections,
            "header": extracted_data.get("header", {}),
            "education": extracted_data.get("education", []),
            "certifications": extracted_data.get("certifications", [])
        }
        
        return enriched_scaffold, validation_results

# --- End DataEnricher ---

def run_hop_2(args: argparse.Namespace):
    """Executes the HOP-2 enrichment logic."""
    logger, _ = setup_workflow_logging(args.workflow_id, log_file_dir=args.run_dir)
    logger.info("--- Starting HOP-2: Data Enrichment ---")
    start_time = datetime.now()

    try:
        # Load inputs
        try:
            # Load clerk output
            with open(args.input_path_clerk_output, 'r', encoding='utf-8') as f:
                clerk_data = json.load(f)
            extracted_data = clerk_data.get("extracted_content", {})
            logger.info(f"Loaded clerk output from {args.input_path_clerk_output}")
            
            # Load thematic analysis
            with open(args.input_path_thematic_analysis, 'r', encoding='utf-8') as f:
                thematic_data = json.load(f)
            thematic_analysis = ThematicAnalysis.from_dict(thematic_data)
            logger.info(f"Loaded thematic analysis from {args.input_path_thematic_analysis}")
            
        except Exception as e:
            raise HopExecutionError(f"Failed to load input files: {e}") from e

        # Instantiate enricher
        enricher = DataEnricher()

        # Execute enrichment
        enriched_scaffold, validation_results = enricher.enrich(extracted_data, thematic_analysis)

        # Log results
        dup_issues = [vr for vr in validation_results if 'DUPLICATE' in vr.rule_id and not vr.passed]
        logger.info(f"Enrichment complete. Duplicate issues: {len(dup_issues)}")
        logger.info(f"Experience sections enriched: {len(enriched_scaffold.get('experience_sections', []))}")

        # Prepare output
        output_data = {
            "enriched_scaffold": enriched_scaffold,
            "enrichment_validation_results": [default_serializer(vr) for vr in validation_results]
        }

        # Write output
        try:
            output_path = Path(args.output_path_enriched_scaffold)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=default_serializer)
            logger.info(f"Successfully wrote enriched scaffold to {output_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to write output JSON: {e}") from e

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-2 Finished Successfully ({duration:.2f}s) ---")
        print("API Calls Made: 0")  # Enrichment makes no API calls

    except HopExecutionError as he:
        logger.error(f"HOP-2 HALTED: {he}", exc_info=False)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-2 Finished with HALT ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        exit(1)
    except Exception as e:
        logger.error(f"HOP-2 FAILED with unexpected error: {e}", exc_info=True)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-2 Finished with FAILURE ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HOP-2: Data Enrichment")
    parser.add_argument("--workflow-id", required=True, help="Unique ID for the workflow run")
    parser.add_argument("--run-dir", required=True, help="Directory for the workflow run artifacts")
    parser.add_argument("--config-path", required=True, help="Path to the config file snapshot")
    parser.add_argument("--input-path-clerk-output", required=True, help="Path to the clerk output JSON")
    parser.add_argument("--input-path-thematic-analysis", required=True, help="Path to the thematic analysis JSON")
    parser.add_argument("--output-path-enriched-scaffold", required=True, help="Path to write the enriched scaffold JSON")

    args = parser.parse_args()
    run_hop_2(args)
