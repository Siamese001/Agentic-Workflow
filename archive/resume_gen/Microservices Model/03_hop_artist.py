# hops/hop_3_artist.py
"""
Hop 3: Content Generation (Artist) - HIGH-SIGNAL OVERWRITE

This advanced Artist implements a "Select, then Synthesize" strategy.
1.  It uses vector embeddings from HOP-1 (via HOP-2 scaffold) and thematic
    targets from HOP-0 to perform multi-criteria semantic scoring and
    *selection* of the best bullets from the master pool.
2.  It then uses the LLM (Gemini) for its true strength: *synthesis* and
    *rewriting*, by feeding it the pre-selected content with high-signal
    prompts.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List, Set

# --- High-Signal Imports ---
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import necessary components
from helpers import (
    setup_workflow_logging, HopExecutionError, default_serializer,
    ValidationResult, ValidationSeverity, ThematicAnalysis, ResumeSection
)

# --- Mock Components (for high-signal orchestration) ---
# In a real system, these would be robust, shared clients.

class EmbeddingClient:
    """Mock EmbeddingClient to vectorize HOP-0 themes."""
    def __init__(self, config=None):
        logging.info("Initialized MOCK EmbeddingClient for HOP-3")
        self.dimension = 768 # Must match HOP-1's dimension
    
    def embed(self, text: str) -> List[float]:
        """Generates a mock, deterministic embedding."""
        if not text: return [0.0] * self.dimension
        hash_val = hash(text)
        np.random.seed(hash_val % (2**32 - 1))
        return np.random.rand(self.dimension).tolist()
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generates mock embeddings for a batch of texts."""
        return np.array([self.embed(text) for text in texts])

class MockGeminiClient:
    """Mock LLM client that tracks API calls and state."""
    def __init__(self, config=None):
        self.api_calls_made = 0
        logging.info("Initialized MOCK GeminiClient for HOP-3")

    def generate(self, prompt: str, temperature: float) -> str:
        """Simulates an LLM call."""
        self.api_calls_made += 1
        logging.info(f"Simulating LLM call (Temp: {temperature})...")
        time.sleep(0.05) # Simulate network latency
        
        if "RETRY:" in prompt:
             return f"Mock REWRITTEN content for prompt: {prompt[:50]}..."
        
        # Simulate different content types based on prompt
        if "executive summary" in prompt.lower():
            return "Mock Executive Summary: A high-impact leader..."
        if "rewrite these bullets" in prompt.lower():
            return "Mock Rewritten Bullets:\n- Drove 20% growth...\n- Led 5-person team..."
        
        return f"Mock generated content for prompt: {prompt[:50]}..."

class ArtistValidator:
    """
    Immediate post-generation validator. Runs *inside* HOP-3 to
    enable stateful retry logic.
    """
    def validate(self, section_enum: ResumeSection, text: str, target_keywords: Set[str]) -> List[ValidationResult]:
        """Runs simple, fast checks."""
        results = []
        if not text or len(text) < 20:
            results.append(ValidationResult(
                rule_id=f"{section_enum.value}_LEN_CHECK", passed=False,
                severity=ValidationSeverity.WARNING,
                message="Generated content is too short."
            ))
        
        # Example: Ensure summary mentions at least one target keyword
        if section_enum == ResumeSection.K1_EXECUTIVE_SUMMARY:
            if not any(kw.lower() in text.lower() for kw in target_keywords):
                results.append(ValidationResult(
                    rule_id="SUMMARY_KEYWORD_CHECK", passed=False,
                    severity=ValidationSeverity.WARNING,
                    message=f"Summary must mention a target keyword. (e.g., {list(target_keywords)[0]})"
                ))
        return results

# --- End Mock Components ---


class ArtistGenerator:
    """
    High-Signal Artist Generator.
    """
    def __init__(self, master_resume, enriched_scaffold, job_description, thematic_analysis, artist_specs):
        self.master_resume = master_resume
        self.enriched_scaffold = enriched_scaffold
        self.job_description = job_description
        self.thematic_analysis = thematic_analysis
        self.artist_specs = artist_specs
        
        self.logger = logging.getLogger(__name__)
        
        # Instantiate clients
        self.embedding_client = EmbeddingClient()
        self.llm_client = MockGeminiClient()
        self.validator = ArtistValidator()
        
        # Internal state
        self.target_embeddings: np.ndarray | None = None
        self.target_keywords: Set[str] = set()
        self.selected_bullets_map: Dict[str, List[Dict]] = {}
        self.generated_content: Dict[str, Any] = {}
        self.validation_results: List[ValidationResult] = []
        self.api_calls_made = 0

    def _get_target_vectors(self):
        """
        Generates vector embeddings for the key themes from HOP-0.
        This is the "target" for our semantic search.
        """
        self.logger.info("Vectorizing HOP-0 thematic targets...")
        
        targets = []
        
        # 1. Primary Theme
        if self.thematic_analysis.primary_theme:
            targets.append(self.thematic_analysis.primary_theme.get("name", ""))
            targets.extend(self.thematic_analysis.primary_theme.get("keywords", []))
            self.target_keywords.update(self.thematic_analysis.primary_theme.get("keywords", []))
        
        # 2. Problem/Solution Narratives
        # (Assuming 'problem_solution_narratives' is a field in ThematicAnalysis)
        if hasattr(self.thematic_analysis, 'problem_solution_narratives'):
            for narrative in self.thematic_analysis.problem_solution_narratives:
                targets.append(narrative.get("problem_statement", ""))
                targets.append(narrative.get("solution_statement", ""))
        
        # 3. Signal Gaps
        # (Assuming 'signal_gap_keywords' is a field in ThematicAnalysis)
        if hasattr(self.thematic_analysis, 'signal_gap_keywords'):
             targets.extend(self.thematic_analysis.signal_gap_keywords)

        targets = [t for t in targets if t] # Filter empty strings
        if not targets:
            raise HopExecutionError("No thematic targets found in HOP-0 analysis. Cannot proceed.")
            
        self.target_embeddings = self.embedding_client.embed_batch(targets)
        self.logger.info(f"Generated {len(self.target_embeddings)} target vectors.")

    def _score_and_select_bullets(self):
        """
        The core of the "Select" phase. Scores all bullets in the scaffold
        against the target vectors and selects the best N.
        """
        self.logger.info("Scoring and selecting bullets from scaffold...")
        
        # Weights for Multi-Criteria Decision Making
        score_weights = self.artist_specs.get("score_weights", {
            "semantic_similarity": 1.0,
            "has_metrics": 1.5,
            "has_strong_verb": 1.2
        })
        
        for section in self.enriched_scaffold.get("experience_sections", []):
            section_id = f"{section.get('company', 'comp')}_{section.get('title', 'title')}"
            bullets = section.get("bullets", [])
            
            if not bullets:
                continue
            
            # 1. Get pre-computed bullet embeddings from HOP-1/HOP-2
            try:
                bullet_embeddings = np.array([b['embedding'] for b in bullets])
                if bullet_embeddings.shape[1] != self.target_embeddings.shape[1]:
                     raise ValueError("Embedding dimension mismatch!")
            except (KeyError, ValueError) as e:
                self.logger.error(f"Failed to extract embeddings for section {section_id}: {e}. Skipping.")
                continue

            # 2. Calculate Semantic Score (Cosine Similarity)
            # Shape: (n_bullets, n_targets)
            similarity_matrix = cosine_similarity(bullet_embeddings, self.target_embeddings)
            # Take the *max* similarity for each bullet (how well it matches *any* target)
            semantic_scores = similarity_matrix.max(axis=1)

            # 3. Apply Multi-Criteria Scoring
            scored_bullets = []
            for i, bullet_data in enumerate(bullets):
                base_score = semantic_scores[i]
                
                # Apply weights
                if bullet_data.get("metrics"):
                    base_score *= score_weights["has_metrics"]
                if bullet_data.get("action_verb"):
                    base_score *= score_weights["has_strong_verb"]
                
                scored_bullets.append({
                    "score": base_score,
                    **bullet_data
                })
            
            # 4. Select Top N
            num_to_select = self.artist_specs.get("bullets_per_role", 4)
            top_bullets = sorted(scored_bullets, key=lambda x: x['score'], reverse=True)[:num_to_select]
            
            self.selected_bullets_map[section_id] = top_bullets
            self.logger.info(f"Selected {len(top_bullets)} bullets for {section_id} (Top score: {top_bullets[0]['score']:.2f})")

    def _build_prompt_for_section(self, section_enum: ResumeSection) -> str:
        """Builds a high-signal prompt based on pre-selected data."""
        
        # K.1 Summary: Synthesize themes from HOP-0
        if section_enum == ResumeSection.K1_EXECUTIVE_SUMMARY:
            prompt = f"""
            Generate a 4-line executive summary for a technical leader.
            It must be aligned with this job's primary theme:
            {json.dumps(self.thematic_analysis.primary_theme)}
            
            Weave in these problem/solution narratives found from RAG analysis:
            {json.dumps(getattr(self.thematic_analysis, 'problem_solution_narratives', 'N/A'))}
            
            Ensure you mention these keywords: {list(self.target_keywords)}
            """
            return prompt.strip()
        
        # K.2 Bullets: Rewrite *selected* bullets
        # This assumes K2_UNIFY_BULLETS maps to the first experience section
        # A real impl would map specs to sections
        if section_enum == ResumeSection.K2_UNIFY_BULLETS:
            section_key = next(iter(self.selected_bullets_map.keys()), None)
            if not section_key: return "No bullets selected." # Failsafe
            
            bullets_to_rewrite = [b['bullet_text'] for b in self.selected_bullets_map[section_key]]
            
            prompt = f"""
            Rewrite these {len(bullets_to_rewrite)} bullets into a single, cohesive narrative.
            Focus on the achievements and impact.
            
            Target Themes: {json.dumps(self.thematic_analysis.primary_theme.get("keywords"))}
            
            Bullets to rewrite:
            {json.dumps(bullets_to_rewrite, indent=2)}
            """
            return prompt.strip()

        # Fallback for other sections
        return f"Generate content for section: {section_enum.value}"

    def _generate_section_with_retry(self, section_enum: ResumeSection):
        """Generates one section with immediate validation and retry."""
        
        prompt = self._build_prompt_for_section(section_enum)
        base_temp = self.artist_specs.get("temperature", 0.7)
        max_retries = self.artist_specs.get("max_retries", 2)
        
        for i in range(max_retries):
            temperature = base_temp + (i * 0.1) # Increase temp on retry
            
            generated_text = self.llm_client.generate(prompt, temperature)
            
            # Run immediate validation
            validation_issues = self.validator.validate(section_enum, generated_text, self.target_keywords)
            
            if not validation_issues:
                # SUCCESS
                self.generated_content[section_enum.value] = generated_text
                self.logger.info(f"Successfully generated section {section_enum.value}")
                return
            
            # FAILURE - Prep for retry
            self.logger.warning(f"Validation failed for {section_enum.value} (Attempt {i+1}). Retrying...")
            self.validation_results.extend(validation_issues)
            
            # Append retry instructions to the prompt
            retry_prompt = "\n\nRETRY: The previous generation failed. "
            retry_prompt += "Fix this issue: " + validation_issues[0].message
            prompt += retry_prompt
        
        # If loop finishes, all retries failed
        self.logger.error(f"Failed to generate {section_enum.value} after {max_retries} attempts.")
        self.generated_content[section_enum.value] = f"ERROR: Failed to generate content. Last attempt: {generated_text}"
        self.validation_results.append(ValidationResult(
            rule_id=f"{section_enum.value}_GEN_FAILED", passed=False,
            severity=ValidationSeverity.CRITICAL,
            message=f"All {max_retries} generation attempts failed."
        ))

    def run_generation_pipeline(self) -> Tuple[Dict, List[ValidationResult], int]:
        """Main orchestration method for HOP-3."""
        
        self.logger.info("--- Starting High-Signal Artist Pipeline ---")
        
        # --- PHASE 1: PREPARATION (Vectorize Targets) ---
        self._get_target_vectors()
        
        # --- PHASE 2: SELECTION (Score and Pick Bullets) ---
        # This is the "Mise en Place" - 0 LLM calls
        self._score_and_select_bullets()
        
        # --- PHASE 3: SYNTHESIS (Generate Content with LLM) ---
        self.logger.info("Starting LLM Synthesis phase...")
        
        # Define generation plan (simplified, a real one comes from artist_specs)
        generation_plan = [
            ResumeSection.K1_EXECUTIVE_SUMMARY,
            ResumeSection.K2_UNIFY_BULLETS,
            # ... other sections
        ]
        
        for section in generation_plan:
            self._generate_section_with_retry(section)

        self.api_calls_made = self.llm_client.api_calls_made
        self.logger.info(f"--- Artist Pipeline Finished. Total API Calls: {self.api_calls_made} ---")
        
        return self.generated_content, self.validation_results, self.api_calls_made


def run_hop_3(args: argparse.Namespace):
    """Executes the HOP-3 Artist generation logic."""
    logger, _ = setup_workflow_logging(args.workflow_id, log_file_dir=args.run_dir)
    logger.info("--- Starting HOP-3: Content Generation (Artist) [v-HighSignal] ---")
    start_time = datetime.now()
    total_api_calls = 0
    generator = None

    try:
        # Load inputs (All inputs are required for this advanced model)
        try:
            with open(args.input_path_enriched_scaffold, 'r', encoding='utf-8') as f:
                enriched_scaffold = json.load(f).get("enriched_scaffold", {})
            logger.info(f"Loaded enriched scaffold from {args.input_path_enriched_scaffold}")
            
            with open(args.input_path_thematic_analysis, 'r', encoding='utf-8') as f:
                thematic_analysis = ThematicAnalysis.from_dict(json.load(f))
            logger.info(f"Loaded thematic analysis from {args.input_path_thematic_analysis}")
            
            jd_path = Path(args.input_path_jd)
            job_description = jd_path.read_text(encoding='utf-8')
            logger.info(f"Loaded job description from {jd_path}")
            
            with open(args.master_resume_path, 'r', encoding='utf-8') as f:
                master_resume = json.load(f)
            logger.info(f"Loaded master resume from {args.master_resume_path}")
            
            with open(args.artist_specs_path, 'r', encoding='utf-8') as f:
                artist_specs = json.load(f)
            logger.info(f"Loaded artist specs from {args.artist_specs_path}")
            
        except Exception as e:
            raise HopExecutionError(f"Failed to load input files: {e}") from e

        if not os.environ.get("GEMINI_API_KEY"):
            raise HopExecutionError("GEMINI_API_KEY not found in environment")

        # Instantiate the High-Signal Artist
        generator = ArtistGenerator(
            master_resume=master_resume,
            enriched_scaffold=enriched_scaffold,
            job_description=job_description,
            thematic_analysis=thematic_analysis,
            artist_specs=artist_specs
        )

        # Execute the full pipeline
        generated_content, validation_results, total_api_calls = generator.run_generation_pipeline()
        
        logger.info(f"Artist generation complete. Sections generated: {len(generated_content)}")
        logger.info(f"API calls made: {total_api_calls}")

        # Prepare output
        output_data = {
            "artist_output": generated_content,
            "artist_validation_results": [default_serializer(vr) for vr in validation_results],
            "metadata": {
                "api_calls": total_api_calls,
                "sections_generated": list(generated_content.keys()),
                "selected_bullet_map_keys": list(generator.selected_bullets_map.keys())
            }
        }

        # Write output
        try:
            output_path = Path(args.output_path_artist_output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=default_serializer)
            logger.info(f"Successfully wrote artist output to {output_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to write output JSON: {e}") from e

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-3 Finished Successfully ({duration:.2f}s) ---")
        print(f"API Calls Made: {total_api_calls}")

    except HopExecutionError as he:
        logger.error(f"HOP-3 HALTED: {he}", exc_info=False)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-3 Finished with HALT ({duration:.2f}s) ---")
        if generator: total_api_calls = generator.api_calls_made
        print(f"API Calls Made: {total_api_calls}")
        exit(1)
    except Exception as e:
        logger.error(f"HOP-3 FAILED with unexpected error: {e}", exc_info=True)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-3 Finished with FAILURE ({duration:.2f}s) ---")
        if generator: total_api_calls = generator.api_calls_made
        print(f"API Calls Made: {total_api_calls}")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HOP-3: Content Generation (Artist) [v-HighSignal]")
    parser.add_argument("--workflow-id", required=True, help="Unique ID for the workflow run")
    parser.add_argument("--run-dir", required=True, help="Directory for the workflow run artifacts")
    parser.add_argument("--config-path", required=True, help="Path to the config file snapshot")
    parser.add_argument("--master-resume-path", required=True, help="Path to the master resume JSON snapshot")
    parser.add_argument("--artist-specs-path", required=True, help="Path to the artist specs JSON")
    parser.add_argument("--input-path-enriched-scaffold", required=True, help="Path to the enriched scaffold JSON")
    parser.add_ idyllic-path-thematic-analysis", required=True, help="Path to the thematic analysis JSON")
    parser.add_argument("--input-path-jd", required=True, help="Path to the input job description text file")
    parser.add_argument("--output-path-artist-output", required=True, help="Path to write the artist output JSON")

    args = parser.parse_args()
    run_hop_3(args)