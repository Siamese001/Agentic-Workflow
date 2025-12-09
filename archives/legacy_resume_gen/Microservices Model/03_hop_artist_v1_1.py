# hops/03_hop_artist.py
"""
Hop 3: Content Generation (Artist) with Configuration Integration

This Artist implements:
1. ReasoningConfig integration for section-specific generation parameters
2. ContentConstraintsConfig integration for word count boundaries
3. Enhanced system prompts with reasoning directives
4. Semantic bullet selection and synthesis
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List, Set

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import necessary components from helpers
from helpers import (
    setup_workflow_logging, HopExecutionError, default_serializer,
    ValidationResult, ValidationSeverity, ThematicAnalysis, ResumeSection,
    ReasoningConfig, ContentConstraintsConfig, enhance_system_prompt_with_reasoning
)

# Initialize module-level configuration instances
CONSTRAINTS = ContentConstraintsConfig()

# --- Mock Components ---

class EmbeddingClient:
    """Mock EmbeddingClient for vectorization"""
    def __init__(self, config=None):
        logging.info("Initialized MOCK EmbeddingClient for HOP-3")
        self.dimension = 768

    def embed(self, text: str) -> List[float]:
        """Generate mock embedding"""
        if not text:
            return [0.0] * self.dimension
        hash_val = hash(text)
        np.random.seed(hash_val % (2**32 - 1))
        return np.random.rand(self.dimension).tolist()

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for batch"""
        return np.array([self.embed(text) for text in texts])

class MockGeminiClient:
    """Mock LLM client with API call tracking"""
    def __init__(self, config=None):
        self.api_calls_made = 0
        self.logger = logging.getLogger(__name__)

    def generate(self, prompt: str, system_prompt: str, temperature: float, 
                 reasoning_config: ReasoningConfig = None) -> str:
        """Simulate LLM generation with reasoning config"""
        self.api_calls_made += 1
        self.logger.info(f"Simulating LLM call with reasoning config: {reasoning_config is not None}")
        time.sleep(0.05)

        # Simulate self-consistency runs if configured
        if reasoning_config and reasoning_config.self_consistency > 1:
            self.api_calls_made += (reasoning_config.self_consistency - 1)
            self.logger.info(f"Self-consistency: {reasoning_config.self_consistency} runs")

        if "executive summary" in prompt.lower():
            return "Strategic AI leader driving enterprise transformation through innovative machine learning platforms and data-driven decision frameworks. Proven track record architecting scalable AI solutions while managing cross-functional teams and establishing strategic partnerships that accelerate business outcomes."
        if "headline" in prompt.lower():
            return "AI Strategy & Innovation | Enterprise ML Architecture | Data Platform Leadership"
        if "rewrite" in prompt.lower():
            bullets = [
                "Architected enterprise AI platforms processing 10M+ daily transactions with 99.9% uptime",
                "Led cross-functional teams of 15+ engineers delivering $30M in measurable business value",
                "Established strategic partnerships with AWS and Google Cloud accelerating AI adoption by 40%"
            ]
            return "\n".join(bullets)

        return "Mock generated content"

# --- Artist Generator ---

class ArtistGenerator:
    """
    High-signal content generator with configuration integration
    """
    def __init__(self, master_resume: Dict, enriched_scaffold: Dict, job_description: str,
                 thematic_analysis: ThematicAnalysis, artist_specs: Dict):
        self.master_resume = master_resume
        self.enriched_scaffold = enriched_scaffold
        self.job_description = job_description
        self.thematic_analysis = thematic_analysis
        self.artist_specs = artist_specs

        self.logger = logging.getLogger(__name__)

        # Initialize clients
        self.embedding_client = EmbeddingClient()
        self.llm_client = MockGeminiClient()

        # Internal state
        self.target_embeddings: np.ndarray | None = None
        self.target_keywords: Set[str] = set()
        self.selected_bullets_map: Dict[str, List[Dict]] = {}
        self.generated_content: Dict[str, Any] = {}
        self.api_calls_made = 0

    def _get_reasoning_config(self, section_key: str) -> ReasoningConfig:
        """
        Get reasoning configuration for a specific section.
        Maps section keys to pre-configured ReasoningConfig instances.
        """
        section_config_map = {
            "K.0_Headline": ReasoningConfig.K0_HEADLINE_CONFIG,
            "K.1_Executive_Summary": ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG,
            "K.2_Unify_Bullets": ReasoningConfig.K2_UNIFY_BULLETS_CONFIG,
            "K.2_Unify_Overview": ReasoningConfig.K2_UNIFY_OVERVIEW_CONFIG,
            "K.3_IBM_Bullets": ReasoningConfig.K3_IBM_BULLETS_CONFIG,
            "K.3_IBM_Overview": ReasoningConfig.K3_IBM_OVERVIEW_CONFIG,
            "K.4_TraderSense_Narrative": ReasoningConfig.K4_TRADERSENSE_NARRATIVE_CONFIG,
            "K.5_EY_Narrative": ReasoningConfig.K5_EY_NARRATIVE_CONFIG,
            "K.6_Early_Career_Narrative": ReasoningConfig.K6_EARLY_CAREER_NARRATIVE_CONFIG,
            "K.9_Competencies": ReasoningConfig.K9_COMPETENCIES_CONFIG,
            "K.10_Skills": ReasoningConfig.K10_SKILLS_CONFIG,
            "K.11_Cover_Letter": ReasoningConfig.K11_COVER_LETTER_CONFIG
        }

        config = section_config_map.get(section_key, ReasoningConfig.DEFAULT)
        self.logger.debug(f"Using reasoning config for {section_key}: CoT={config.cot_min_paths}, "
                         f"SC={config.self_consistency}, Reflexion={config.reflexion}")
        return config

    def _get_constraints_for_section(self, section_key: str) -> Dict[str, int]:
        """
        Get word count constraints for a specific section.
        Returns dict with min_wc, max_wc, and other relevant constraints.
        """
        constraints_map = {
            "K.0_Headline": {
                "min_wc": CONSTRAINTS.HEADLINE_WORD_COUNT_MIN,
                "max_wc": CONSTRAINTS.HEADLINE_WORD_COUNT_MAX,
                "comp_min_wc": CONSTRAINTS.HEADLINE_COMPONENT_WORDS_MIN,
                "comp_max_wc": CONSTRAINTS.HEADLINE_COMPONENT_WORDS_MAX
            },
            "K.1_Executive_Summary": {
                "min_wc": CONSTRAINTS.EXEC_SUMMARY_WORD_COUNT_MIN,
                "max_wc": CONSTRAINTS.EXEC_SUMMARY_WORD_COUNT_MAX,
                "min_sc": CONSTRAINTS.EXEC_SUMMARY_SENTENCE_COUNT_MIN,
                "max_sc": CONSTRAINTS.EXEC_SUMMARY_SENTENCE_COUNT_MAX,
                "min_diff": CONSTRAINTS.K1_MIN_DIFFERENTIATORS
            },
            "K.2_Unify_Overview": {
                "min_wc": CONSTRAINTS.UNIFY_OVERVIEW_WORD_COUNT_MIN,
                "max_wc": CONSTRAINTS.UNIFY_OVERVIEW_WORD_COUNT_MAX
            },
            "K.3_IBM_Overview": {
                "min_wc": CONSTRAINTS.IBM_OVERVIEW_WORD_COUNT_MIN,
                "max_wc": CONSTRAINTS.IBM_OVERVIEW_WORD_COUNT_MAX
            },
            "K.4_TraderSense_Narrative": {
                "min_wc": CONSTRAINTS.TRADERSENSE_NARRATIVE_WORD_COUNT_MIN,
                "max_wc": CONSTRAINTS.TRADERSENSE_NARRATIVE_WORD_COUNT_MAX
            },
            "K.5_EY_Narrative": {
                "min_wc": CONSTRAINTS.EY_NARRATIVE_WORD_COUNT_MIN,
                "max_wc": CONSTRAINTS.EY_NARRATIVE_WORD_COUNT_MAX
            },
            "K.6_Early_Career_Narrative": {
                "min_wc": CONSTRAINTS.EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN,
                "max_wc": CONSTRAINTS.EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX
            }
        }

        return constraints_map.get(section_key, {"min_wc": 50, "max_wc": 100})

    def _get_target_vectors(self):
        """Generate target embeddings from HOP-0 thematic analysis"""
        self.logger.info("Vectorizing HOP-0 thematic targets...")

        targets = []

        # Primary theme
        if self.thematic_analysis.primary_theme:
            targets.append(self.thematic_analysis.primary_theme.get("name", ""))
            targets.extend(self.thematic_analysis.primary_theme.get("keywords", []))
            self.target_keywords.update(self.thematic_analysis.primary_theme.get("keywords", []))

        # Competitive intelligence differentiators
        if hasattr(self.thematic_analysis, 'competitive_intelligence') and self.thematic_analysis.competitive_intelligence:
            diff_keywords = getattr(self.thematic_analysis.competitive_intelligence, 'differentiator_keywords', [])
            if diff_keywords:
                targets.extend(diff_keywords)
                self.target_keywords.update(diff_keywords)

        targets = [t for t in targets if t]
        if not targets:
            self.logger.warning("No thematic targets found. Using fallback.")
            return np.array([[0.0] * 768])

        self.target_embeddings = self.embedding_client.embed_batch(targets)
        self.logger.info(f"Target vectors generated: {len(targets)} keywords")

    def _select_top_bullets(self, company_name: str, top_k: int = 8) -> List[Dict]:
        """
        Select top-k bullets from a company using semantic similarity
        """
        self.logger.info(f"Selecting top {top_k} bullets for {company_name}...")

        # Find matching company in enriched scaffold
        all_bullets = []
        for section in self.enriched_scaffold.get("experience_sections", []):
            if section.get("company", "").lower() == company_name.lower():
                all_bullets = section.get("bullets", [])
                break

        if not all_bullets:
            self.logger.warning(f"No bullets found for {company_name}")
            return []

        # Calculate semantic scores
        bullet_embeddings = np.array([b.get("embedding", [0.0] * 768) for b in all_bullets])
        
        if self.target_embeddings is None or bullet_embeddings.size == 0:
            self.logger.warning("Missing embeddings for semantic scoring")
            return all_bullets[:top_k]

        # Compute similarities
        similarities = cosine_similarity(bullet_embeddings, self.target_embeddings)
        avg_similarities = similarities.mean(axis=1)

        # Rank and select
        ranked_indices = np.argsort(avg_similarities)[::-1]
        selected = [all_bullets[i] for i in ranked_indices[:top_k]]

        self.logger.info(f"Selected {len(selected)} bullets with avg similarity: {avg_similarities[ranked_indices[0]]:.3f}")
        return selected

    def _generate_section_with_retry(self, section_key: str, max_retries: int = 2) -> str:
        """
        Generate content for a section with reasoning config and retry logic
        """
        self.logger.info(f"Generating {section_key}...")

        # Get reasoning config and constraints
        reasoning_config = self._get_reasoning_config(section_key)
        constraints = self._get_constraints_for_section(section_key)

        # Build prompt with constraints
        prompt = self._build_section_prompt(section_key, constraints)
        
        # Build system prompt
        base_system_prompt = f"You are an expert resume writer specializing in {section_key}."
        
        # Enhance system prompt with reasoning directives
        enhanced_system_prompt = enhance_system_prompt_with_reasoning(
            base_system_prompt,
            reasoning_config,
            section_id=section_key
        )

        # Generate with retry
        for attempt in range(max_retries + 1):
            content = self.llm_client.generate(
                prompt=prompt,
                system_prompt=enhanced_system_prompt,
                temperature=0.9,
                reasoning_config=reasoning_config
            )

            # Simple validation
            word_count = len(content.split())
            if constraints.get("min_wc", 0) <= word_count <= constraints.get("max_wc", 1000):
                self.logger.info(f"{section_key} generated successfully ({word_count} words)")
                return content
            else:
                self.logger.warning(f"{section_key} word count {word_count} outside range "
                                  f"[{constraints.get('min_wc')}, {constraints.get('max_wc')}]. "
                                  f"Retry {attempt + 1}/{max_retries}")

        self.logger.error(f"Failed to generate {section_key} within constraints after {max_retries} retries")
        return content  # Return last attempt

    def _build_section_prompt(self, section_key: str, constraints: Dict[str, int]) -> str:
        """Build prompt with constraints and thematic context"""
        primary_theme = self.thematic_analysis.primary_theme.get("name", "Unknown")
        keywords = ", ".join(list(self.target_keywords)[:5])

        if "Headline" in section_key:
            return (f"Create a professional resume headline for {primary_theme} expertise. "
                   f"Include keywords: {keywords}. "
                   f"Total words: {constraints['min_wc']}-{constraints['max_wc']}. "
                   f"Format: Component A | Component B | Component C")

        if "Executive_Summary" in section_key:
            return (f"Write an executive summary for a {primary_theme} leader. "
                   f"Emphasize: {keywords}. "
                   f"Requirements: {constraints['min_wc']}-{constraints['max_wc']} words, "
                   f"{constraints.get('min_sc', 6)}-{constraints.get('max_sc', 7)} sentences. "
                   f"Include {constraints.get('min_diff', 4)}+ differentiating keywords.")

        if "Bullets" in section_key:
            # Get selected bullets for context
            company = section_key.split("_")[1] if "_" in section_key else "Unknown"
            selected_bullets = self._select_top_bullets(company, top_k=6)
            bullets_text = "\n".join([b.get("bullet_text", "") for b in selected_bullets[:3]])
            
            return (f"Rewrite these achievement bullets for {primary_theme} focus:\n{bullets_text}\n\n"
                   f"Target keywords: {keywords}\n"
                   f"Output 3-5 rewritten bullets emphasizing measurable impact.")

        if "Overview" in section_key:
            return (f"Write a brief role overview ({constraints['min_wc']}-{constraints['max_wc']} words) "
                   f"for experience relevant to {primary_theme}. Keywords: {keywords}")

        if "Narrative" in section_key:
            return (f"Write a narrative paragraph ({constraints['min_wc']}-{constraints['max_wc']} words) "
                   f"bridging past experience to {primary_theme}. Keywords: {keywords}")

        return f"Generate content for {section_key} targeting {primary_theme}."

    def generate_all_sections(self) -> Tuple[Dict[str, Any], int]:
        """
        Main generation orchestrator
        """
        self.logger.info("=== Starting Artist Content Generation ===")
        
        # Initialize target vectors
        self._get_target_vectors()

        # Generate each section defined in artist specs
        sections_to_generate = [
            "K.0_Headline",
            "K.1_Executive_Summary",
            "K.2_Unify_Bullets",
            "K.2_Unify_Overview",
            "K.3_IBM_Bullets",
            "K.3_IBM_Overview"
        ]

        for section_key in sections_to_generate:
            try:
                content = self._generate_section_with_retry(section_key)
                self.generated_content[section_key] = content
            except Exception as e:
                self.logger.error(f"Failed to generate {section_key}: {e}")
                self.generated_content[section_key] = f"[GENERATION ERROR: {str(e)}]"

        # Track API calls
        self.api_calls_made = self.llm_client.api_calls_made

        # Build metadata
        metadata = {
            "sections_generated": list(self.generated_content.keys()),
            "api_calls": self.api_calls_made,
            "selected_bullet_map_keys": list(self.selected_bullets_map.keys()),
            "target_keywords_count": len(self.target_keywords)
        }

        self.logger.info(f"=== Generation complete: {len(self.generated_content)} sections, "
                        f"{self.api_calls_made} API calls ===")

        return self.generated_content, metadata

# --- Main Execution ---

def run_hop_3(args: argparse.Namespace):
    """Execute HOP-3 Artist generation with configuration integration"""
    logger, _ = setup_workflow_logging(args.workflow_id, log_file_dir=args.run_dir)
    logger.info("--- Starting HOP-3: Artist Content Generation [Config-Integrated] ---")
    start_time = datetime.now()

    try:
        # Load inputs
        try:
            with open(args.input_path_enriched_scaffold, 'r', encoding='utf-8') as f:
                enriched_data = json.load(f)
            enriched_scaffold = enriched_data.get("enriched_scaffold", {})
            
            with open(args.input_path_thematic_analysis, 'r', encoding='utf-8') as f:
                thematic_data = json.load(f)
            thematic_analysis = ThematicAnalysis.from_dict(thematic_data)
            
            with open(args.jd, 'r', encoding='utf-8') as f:
                job_description = f.read()
            
            with open(args.master_resume_path, 'r', encoding='utf-8') as f:
                master_resume = json.load(f)
            
            with open(args.artist_specs_path, 'r', encoding='utf-8') as f:
                artist_specs = json.load(f)
                
            logger.info("All inputs loaded successfully")
        except Exception as e:
            raise HopExecutionError(f"Failed to load inputs: {e}") from e

        # Create artist generator
        artist = ArtistGenerator(
            master_resume=master_resume,
            enriched_scaffold=enriched_scaffold,
            job_description=job_description,
            thematic_analysis=thematic_analysis,
            artist_specs=artist_specs
        )

        # Generate content
        artist_output, metadata = artist.generate_all_sections()

        logger.info(f"Generated {len(artist_output)} sections with {metadata['api_calls']} API calls")

        # Prepare output
        output_data = {
            "artist_output": artist_output,
            "metadata": metadata
        }

        # Write output
        try:
            output_path = Path(args.output_path_artist_output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=default_serializer)
            logger.info(f"Successfully wrote artist output to {output_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to write output: {e}") from e

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-3 Finished Successfully ({duration:.2f}s) ---")
        print(f"API Calls Made: {metadata['api_calls']}")

    except HopExecutionError as he:
        logger.error(f"HOP-3 HALTED: {he}", exc_info=False)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-3 Finished with HALT ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        exit(1)
    except Exception as e:
        logger.error(f"HOP-3 FAILED with unexpected error: {e}", exc_info=True)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-3 Finished with FAILURE ({duration:.2f}s) ---")
        print("API Calls Made: 0")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HOP-3: Artist Content Generation [Config-Integrated]")
    parser.add_argument("--workflow-id", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--config-path", required=True)
    parser.add_argument("--input-path-enriched-scaffold", required=True)
    parser.add_argument("--input-path-thematic-analysis", required=True)
    parser.add_argument("--jd", required=True)
    parser.add_argument("--master-resume-path", required=True)
    parser.add_argument("--artist-specs-path", required=True)
    parser.add_argument("--output-path-artist-output", required=True)

    args = parser.parse_args()
    run_hop_3(args)
