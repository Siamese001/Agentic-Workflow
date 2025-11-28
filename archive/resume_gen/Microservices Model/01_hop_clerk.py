# hops/hop_1_clerk.py
"""
Hop 1: Master Resume Pre-processing (Clerk).
Reads the master resume JSON, extracts all sections, and pre-processes
experience bullets by extracting action verbs, metrics, and generating
embeddings for future semantic analysis.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List

import numpy as np # Import numpy for embedding math

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import necessary components
from helpers import (
    setup_workflow_logging, HopExecutionError, default_serializer,
    ValidationResult, ValidationSeverity, BulletProvenance
)

# --- Placeholder Clients (to match stack in HOP-0) ---
# These are essential for a high-signal Clerk.
class EmbeddingClient:
    """Mock EmbeddingClient. In production, this uses a real model."""
    def __init__(self, config=None):
        logging.info("Initialized MOCK EmbeddingClient for HOP-1")
        self.dimension = 768 # Standard embedding dimension

    def embed(self, text: str) -> List[float]:
        """Generates a mock, deterministic embedding."""
        # Create a simple hash-based vector for mock stability
        if not text:
            return [0.0] * self.dimension
        hash_val = hash(text)
        np.random.seed(hash_val % (2**32 - 1))
        return np.random.rand(self.dimension).tolist()

class HallucinationDetector:
     def detect(self, bullets: List[Dict]) -> List[ValidationResult]:
         """
         MOCK Hallucination Detector.
         In a real system, this would validate bullets against
         the user's 'ground truth' or look for factual inconsistencies.
         """
         logging.warning("Using MOCK HallucinationDetector")
         # Example: Check for "placeholder" text
         results = []
         for i, bullet_data in enumerate(bullets):
             if "[INSERT METRIC]" in bullet_data.get("bullet_text", ""):
                 results.append(ValidationResult(
                     rule_id="PLACEHOLDER_METRIC",
                     passed=False,
                     severity=ValidationSeverity.WARNING,
                     message=f"Bullet {i} contains placeholder text.",
                     details={"bullet_text": bullet_data.get("bullet_text")}
                 ))
         return results

# --- End Placeholder Clients ---


class ClerkExtractor:
    """
    HOP-1: Pre-processes the master resume.
    - Extracts all sections (header, experience, education, etc.)
    - Extracts and structures competency map.
    - Enriches every experience bullet with:
        1. An Action Verb
        2. Extracted Metrics (%, $, etc.)
        3. Inferred Skills (cross-referenced with competencies)
        4. A Vector Embedding (for HOP-2 semantic scoring)
    """
    def __init__(self, master_resume: Dict):
        self.master_resume = master_resume
        self._validate_master_resume_structure()

        # Instantiate clients for enrichment
        self.embedding_client = EmbeddingClient()
        self.hallucination_detector = HallucinationDetector()

        # Pre-compile regex patterns for performance
        self.verb_pattern = re.compile(r"^(\w+ed|Built|Led|Managed|Developed|Created|Drove|Launched|Scaled|Achieved|Optimized|Architected)\b", re.IGNORECASE)
        self.metric_pattern = re.compile(r"(\d{1,3}%|\$\d+(\.\d+)?[kKmMbB]?|\d+ million|\d+x|(?<=[Oo]f )\d+)")

    def _validate_master_resume_structure(self):
        """Ensures the master resume has the expected top-level keys."""
        if not self.master_resume:
            raise ValueError("MASTER_RESUME_JSON is empty or not provided.")
        required_keys = [
            "owner", "professional_experience", "education",
            "certifications_and_credentials", "strategic_and_technical_competencies"
        ]
        missing_keys = [key for key in required_keys if key not in self.master_resume]
        if missing_keys:
            logging.warning(f"Master resume snapshot missing keys: {', '.join(missing_keys)}")

    def extract_and_preprocess(self) -> Tuple[Dict, List[ValidationResult]]:
        """Main execution method."""
        validation_results = []

        # 1. Build structured competency map
        competency_map = self._build_competency_map()
        
        # 2. Build enriched experience sections
        experience_sections, all_bullets_for_detection = self._build_experience_sections(competency_map)

        # 3. Run initial validation (e.g., hallucination/placeholder checks)
        hallucination_results = self.hallucination_detector.detect(all_bullets_for_detection)
        validation_results.extend(hallucination_results)

        # 4. Assemble final extracted data structure
        extracted_data = {
            "header": self.master_resume.get("header", {}),
            "education": self.master_resume.get("education", []),
            "certifications": self.master_resume.get("certifications_and_credentials", []),
            "competency_map": competency_map,
            "experience_sections": experience_sections
        }

        return extracted_data, validation_results

    def _build_competency_map(self) -> Dict[str, List[str]]:
        """Parses the competencies into a structured map."""
        competency_map = {}
        for category in self.master_resume.get("strategic_and_technical_competencies", []):
            category_name = category.get("category_name", "Uncategorized")
            skills = category.get("skills", [])
            if isinstance(skills, list):
                competency_map[category_name] = skills
        return competency_map

    def _build_experience_sections(self, competency_map: Dict[str, List[str]]) -> Tuple[List[Dict], List[Dict]]:
        """
        Builds structured experience, enriching each bullet with
        verbs, metrics, inferred skills, and an embedding.
        """
        experience_sections = []
        all_bullets_for_detection = [] # Flat list for validation
        
        all_skills = set(skill.lower() for skills in competency_map.values() for skill in skills)

        for exp in self.master_resume.get("professional_experience", []):
            enriched_bullets = []
            bullet_source = exp.get("bullet_pool", [])
            
            if isinstance(bullet_source, list):
                for i, bullet_text in enumerate(bullet_source):
                    if not isinstance(bullet_text, str) or not bullet_text.strip():
                        continue

                    # Generate all enrichments
                    action_verb = self._extract_action_verb(bullet_text)
                    metrics = self._extract_metrics(bullet_text)
                    inferred_skills = self._infer_skills_from_bullet(bullet_text, all_skills)
                    embedding = self.embedding_client.embed(bullet_text) # Key enhancement

                    bullet_data = {
                        "id": f"{exp.get('company', 'comp')[:5]}_{i}", # Unique ID
                        "bullet_text": bullet_text,
                        "provenance": BulletProvenance.Verbatim.value,
                        "action_verb": action_verb,
                        "metrics": metrics,
                        "inferred_skills": inferred_skills,
                        "embedding": embedding
                    }
                    enriched_bullets.append(bullet_data)
                    all_bullets_for_detection.append(bullet_data)

            experience_sections.append({
                "company": exp.get("company", ""),
                "title": exp.get("title", ""),
                "location": exp.get("location", ""),
                "start_date": exp.get("dates", {}).get("start", ""),
                "end_date": exp.get("dates", {}).get("end", ""),
                "overview": exp.get("overview", ""),
                "bullets": enriched_bullets
            })
        return experience_sections, all_bullets_for_detection

    def _extract_action_verb(self, text: str) -> str | None:
        """Extracts the first word if it's a common action verb."""
        match = self.verb_pattern.match(text)
        return match.group(1).capitalize() if match else None

    def _extract_metrics(self, text: str) -> List[str]:
        """Finds all instances of metrics (%, $, x) in the text."""
        return self.metric_pattern.findall(text)

    def _infer_skills_from_bullet(self, text: str, all_skills: set[str]) -> List[str]:
        """Cross-references bullet text with the master skill list."""
        text_lower = text.lower()
        # Use regex to find whole words to avoid matching "go" in "going"
        return [
            skill for skill in all_skills
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower, re.IGNORECASE)
        ]

# --- End ClerkExtractor Definition ---


def run_hop_1(args: argparse.Namespace):
    """Executes the HOP-1 Clerk pre-processing logic."""
    logger, _ = setup_workflow_logging(args.workflow_id, log_file_dir=args.run_dir)
    logger.info("--- Starting HOP-1: Master Resume Pre-processing (Clerk) ---")
    start_time = datetime.now()

    try:
        # Load Master Resume
        try:
            resume_path = Path(args.master_resume_path)
            with open(resume_path, 'r', encoding='utf-8') as f:
                master_resume = json.load(f)
            logger.info(f"Loaded master resume from {resume_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to load master resume snapshot: {e}") from e

        # Instantiate and run the extractor
        clerk = ClerkExtractor(master_resume)
        extracted_data, validation_results = clerk.extract_and_preprocess()

        # Serialize results
        serializable_validation_results = [default_serializer(vr) for vr in validation_results]
        logger.info(f"Pre-processing complete. Found {len(serializable_validation_results)} initial validation issues.")

        output_data = {
            "extracted_content": extracted_data,
            "initial_validation_results": serializable_validation_results
        }

        # Write output
        try:
            output_path = Path(args.output_path_clerk_output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=default_serializer)
            logger.info(f"Successfully wrote Clerk pre-processed output to {output_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to write output JSON: {e}") from e

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-1 Finished Successfully ({duration:.2f}s) ---")
        print("API Calls Made: 0") # Still 0 LLM calls, but embedding model was used (local/assumed)

    except (HopExecutionError, ValueError) as he:
        logger.error(f"HOP-1 HALTED: {he}", exc_info=False)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-1 Finished with HALT ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        exit(1)
    except Exception as e:
        logger.error(f"HOP-1 FAILED with unexpected error: {e}", exc_info=True)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-1 Finished with FAILURE ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HOP-1: Master Resume Pre-processing (Clerk)")
    parser.add_argument("--workflow-id", required=True, help="Unique ID for the workflow run")
    parser.add_argument("--run-dir", required=True, help="Directory for the workflow run artifacts")
    parser.add_argument("--config-path", required=True, help="Path to the config file snapshot")
    parser.add_argument("--master-resume-path", required=True, help="Path to the master resume JSON snapshot")
    parser.add_argument("--output-path-clerk-output", required=True, help="Path to write the extracted Clerk data JSON")

    args = parser.parse_args()
    run_hop_1(args)