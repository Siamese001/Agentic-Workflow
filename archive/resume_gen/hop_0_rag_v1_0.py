# hops/hop_0_rag_v1.0.py
"""
Hop 0: Job Description Analysis & RAG.
Reads job description text, performs RAG analysis using multiple phases,
and writes the resulting ThematicAnalysis object as JSON.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List

# Imports for new enhancements
import networkx as nx
import numpy as np

# Add project root to path to allow importing shared modules
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import necessary components from helpers or the original module if not moved yet
from helpers import (
    ThematicAnalysis, # Assuming moved to helpers
    setup_workflow_logging, _load_json_data, HopExecutionError, default_serializer
)

# --- Define Classes needed specifically for HOP-0 ---
# These would ideally be in shared modules (e.g., rag_components.py)
# For now, include simplified versions or assume they exist.

# Placeholder imports/definitions - REPLACE with actual imports from shared modules
# from shared.rag import RAGConfig, GeminiWebSearchClient, WebSearchRAG, RAGMission, SimpleFileCacheManager, TelemetryLogger, PhaseExecutor, CircuitBreaker, CompetitiveAnalysisConfig
# --- Start Placeholder Definitions ---
@dataclass
class RAGConfig: # Placeholder
    # Enhancement 1: Multi-Model Consensus
    models: List[str] = field(default_factory=lambda: ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest"])
    max_tokens: int = 8000
    temperature: float = 0.7
    api_max_retries: int = 3
    api_initial_backoff_seconds: float = 1.0
    api_max_backoff_seconds: float = 8.0
    api_backoff_multiplier: float = 2.0
    api_backoff_jitter: float = 0.1
    phase_max_retries: int = 2
    phase_timeout_seconds: int = 120
    circuit_breaker_threshold: int = 3
    circuit_breaker_timeout: int = 30
    cache_dir: str = "./rag_cache"
    cache_ttl_days: int = 7
    # Enhancement 8: Semantic Cache
    semantic_cache_threshold: float = 0.92
    semantic_cache_dir: str = "./semantic_cache"
    telemetry_enabled: bool = False
    telemetry_log_dir: str = "./rag_telemetry"
    # Enhancement 5: Source Authority Weighting
    source_weights: Dict = field(default_factory=lambda: {"blogs.company.com": 1.5, "github.com": 1.4, "generic-jobs.com": 0.8})
    # Enhancement 3: Active Learning Loop
    max_refinement_loops: int = 3

class CircuitBreaker: # Placeholder
    def __init__(self, config): pass
    def call(self, func, *args, **kwargs): return func(*args, **kwargs) # Passthrough

class PhaseExecutor: # Placeholder
     def __init__(self, config): pass
     def execute_with_retry(self, func, name): return func() # No retry

class GeminiWebSearchClient: # Placeholder
    def __init__(self, config, model_name: str):
        self.model_name = model_name
        self.api_calls_made = 0
        self.circuit_breaker = CircuitBreaker(config) # Add circuit breaker attribute
    def search_and_analyze(self, prompt, phase_name) -> Tuple[Dict, int]:
        logging.warning(f"Using MOCK GeminiWebSearchClient ({self.model_name}) for {phase_name}")
        self.api_calls_made += 1
        # Return mock data structure based on phase_name
        if "Pre-RAG" in phase_name:
             return {
                 "jd_entities": {"target_company_name": "Mock Co", "precise_role_title": "Mock Role", "key_technologies": ["mock", "test"], "core_responsibilities": ["mocking"]},
                 "resume_entities": {"candidate_skills": ["mock", "dev"]},
                 "differential_analysis": {"signal_gap_keywords": ["test"], "signal_overlap_keywords": ["mock"]}
             }, 1
        # Add mock returns for phase1, phase2 etc. matching expected JSON structure
        elif "Phase 1" in phase_name:
             return {"search_summary": {}, "thematic_analysis": {"primary_theme": {"name": "Mock Theme", "keywords": ["mock", "test"]}}}, 1
        elif "Phase 2" in phase_name:
             return {"search_summary": {}, "authenticity_patterns": {}}, 1
        elif "Phase 3" in phase_name:
             return {"search_summary": {}, "competitive_analysis": {}}, 1
        elif "Phase 4" in phase_name:
            return {"search_summary": {}, "problem_solution_narratives": {}}, 1
        # Enhancement 2: Adversarial Self-Play
        elif "Phase 5 (Adversary)" in phase_name:
            return {"search_summary": {}, "adversarial_findings": {"refuted_themes": ["Mock Primary Theme"]}}, 1
        return {}, 1 # Default mock

class WebSearchRAG: # Placeholder
    def __init__(self, clients: Dict[str, GeminiWebSearchClient], config): self.clients = clients
    def _get_client(self, model_name): return self.clients[model_name]
    def phase1_thematic_research(self, jd, mission, model_name): return self._get_client(model_name).search_and_analyze("mock p1", "Phase 1")
    def phase2_authenticity_patterns(self, jd, mission, model_name): return self._get_client(model_name).search_and_analyze("mock p2", "Phase 2") # Enhancement 4 (Fingerprinting) logic implied here
    def phase3_competitive_positioning(self, jd, mission, model_name): return self._get_client(model_name).search_and_analyze("mock p3", "Phase 3")
    def phase4_narrative_mining(self, mission, model_name): return self._get_client(model_name).search_and_analyze("mock p4", "Phase 4")
    def phase5_adversarial_check(self, analysis, mission, model_name): return self._get_client(model_name).search_and_analyze("mock p5 adversary", "Phase 5 (Adversary)") # Enhancement 2
    def run_refinement_step(self, weak_areas, mission, model_name): return self._get_client(model_name).search_and_analyze(f"mock refinement: {weak_areas}", "Refinement") # Enhancement 3

@dataclass
class RAGMission: # Placeholder
    target_company_name: str = "Default Co"
    precise_role_title: str = "Default Role"
    key_technologies: List = field(default_factory=list) # Enhancement 4 (Fingerprinting) uses this
    core_responsibilities: List = field(default_factory=list)
    signal_gap_keywords: List = field(default_factory=list)
    signal_overlap_keywords: List = field(default_factory=list)

class SimpleFileCacheManager: # Placeholder
    def __init__(self, dir, ttl): pass
    def get(self, jd): return None
    def set(self, jd, analysis): pass

# --- Start New Placeholder Definitions for Enhancements ---
class EmbeddingClient: # Placeholder for Enhancement 8
    def __init__(self, config): pass
    def embed(self, text: str) -> np.ndarray:
        logging.warning("Using MOCK EmbeddingClient")
        return np.random.rand(768) # Return mock embedding

class SemanticCacheManager: # Placeholder for Enhancement 8
    def __init__(self, config): self.config = config
    def get(self, embedding: np.ndarray) -> Tuple[ThematicAnalysis, float] | None:
        logging.warning("Using MOCK SemanticCacheManager.get")
        # Simulate cache miss
        return None
    def set(self, embedding: np.ndarray, analysis: ThematicAnalysis):
        logging.warning("Using MOCK SemanticCacheManager.set")
        pass
    def _verify_cache(self, analysis: ThematicAnalysis) -> bool:
        # "A quick check ensures the cached analysis is still relevant now."
        logging.warning("Using MOCK SemanticCacheManager._verify_cache")
        return True
# --- End New Placeholder Definitions ---

class TelemetryLogger: # Placeholder
     def __init__(self, log_dir): pass
     def log(self, telemetry): pass

@dataclass
class CompetitiveAnalysisConfig: # Placeholder
     pass

class EnhancedJobDescriptionAnalyzer:
    # --- Simplified Analyzer ---
    def __init__(self, master_resume, config: RAGConfig, embedding_client: EmbeddingClient, semantic_cache: SemanticCacheManager, enable_web_search=True):
        self.master_resume = master_resume
        self.config = config or RAGConfig()

        # Enhancement 1: Init multi-model clients
        self.model_clients = {
            model: GeminiWebSearchClient(self.config, model)
            for model in self.config.models
        }
        self.web_rag = WebSearchRAG(self.model_clients, self.config)
        self.primary_client = self.model_clients[self.config.models[0]] # For pre-rag

        self.cache_manager = SimpleFileCacheManager(self.config.cache_dir, self.config.cache_ttl_days)
        # Enhancement 8: Init semantic cache
        self.embedding_client = embedding_client
        self.semantic_cache = semantic_cache

        self.telemetry_logger = None # Disabled for simplicity
        self.total_api_calls_hop0 = 0

    def _execute_pre_rag_analysis(self, job_description: str) -> RAGMission:
        """Simplified mock pre-rag"""
        logger = logging.getLogger(__name__)
        logger.info("Executing MOCK HOP -0.5: Pre-RAG Differential Analysis...")
        # Simulate API call
        analysis_json, pre_rag_calls = self.primary_client.search_and_analyze("mock pre-rag", "Pre-RAG Analysis")
        self.total_api_calls_hop0 += pre_rag_calls
        # Use mock data, ensure keys exist
        mission = RAGMission(
            target_company_name=analysis_json.get("jd_entities", {}).get("target_company_name", "Unknown"),
            precise_role_title=analysis_json.get("jd_entities", {}).get("precise_role_title", "Unknown"),
            key_technologies=analysis_json.get("jd_entities", {}).get("key_technologies", []), # Used by Enhancement 4
            core_responsibilities=analysis_json.get("jd_entities", {}).get("core_responsibilities", []),
            signal_gap_keywords=analysis_json.get("differential_analysis", {}).get("signal_gap_keywords", []),
            signal_overlap_keywords=analysis_json.get("differential_analysis", {}).get("signal_overlap_keywords", [])
        )
        logger.info(f"  ✓ Mock RAG Mission defined for {mission.target_company_name}.")
        return mission

    # Enhancement 3: Active Learning & Uncertainty-Guided Refinement
    def _run_agentic_rag_loop(self, job_description: str, mission: RAGMission) -> ThematicAnalysis:
        """Replaces simple pipeline with an agentic loop."""
        logger = logging.getLogger(__name__)
        logger.info("Starting HOP-0 Agentic RAG Loop...")
        
        current_analysis = ThematicAnalysis(
             primary_theme={"name": "Mock Primary Theme"},
             signal_quality_score=0.0, # Start score low
             retrieval_method="MOCK_AGENTIC_RAG"
         )

        phases_to_run = [
            (self.web_rag.phase1_thematic_research, "P1 Thematic"),
            (self.web_rag.phase2_authenticity_patterns, "P2 Authenticity"), # Enhancement 4 logic is inside
            (self.web_rag.phase3_competitive_positioning, "P3 Competitive"),
            (self.web_rag.phase4_narrative_mining, "P4 Narrative"),
        ]

        for i in range(self.config.max_refinement_loops):
            logger.info(f"Agentic Loop: Iteration {i+1}/{self.config.max_refinement_loops}")
            
            # Run phases in consensus
            for phase_func, phase_name in phases_to_run:
                # Enhancement 1: Multi-Model Consensus
                consensus_result, calls = self._execute_phase_with_consensus(phase_func, job_description, mission, phase_name)
                self.total_api_calls_hop0 += calls
                # ... logic to merge consensus_result into current_analysis ...

            # Enhancement 3: Critique
            weak_areas = self._critique_analysis(current_analysis)
            if not weak_areas:
                logger.info("Critique PASSED. Exiting refinement loop.")
                break
            
            logger.warning(f"Critique identified weak areas: {weak_areas}. Starting refinement step.")
            # Enhancement 3: Re-plan / Refine
            refinement_result, calls = self._execute_phase_with_consensus(
                self.web_rag.run_refinement_step, weak_areas, mission, "Refinement"
            )
            self.total_api_calls_hop0 += calls
            # ... logic to merge refinement_result into current_analysis ...
            phases_to_run = [] # Don't re-run all phases, only refine (example logic)

        # Enhancement 2: Adversarial Self-Play
        logger.info("Executing Adversarial Self-Play Verification...")
        adversarial_result, calls = self._execute_phase_with_consensus(
            self.web_rag.phase5_adversarial_check, current_analysis, mission, "Adversarial"
        )
        self.total_api_calls_hop0 += calls
        # ... logic to merge adversarial_result into current_analysis (e.g., flag themes) ...

        # Enhancement 5: Source Authority Weighting
        final_analysis = self._synthesize_analysis(current_analysis)
        
        return final_analysis

    # Enhancement 1: Multi-Model Consensus
    def _execute_phase_with_consensus(self, phase_func: callable, *args) -> Tuple[Dict, int]:
        """Runs a phase function across multiple models and finds consensus."""
        logger = logging.getLogger(__name__)
        all_results = []
        total_calls = 0
        for model in self.config.models:
            try:
                result_json, calls = phase_func(*args, model_name=model)
                all_results.append(result_json)
                total_calls += calls
            except Exception as e:
                logger.error(f"Failed to run phase {phase_func.__name__} with model {model}: {e}")
        
        consensus_data = self._find_consensus(all_results)
        return consensus_data, total_calls

    def _find_consensus(self, results: List[Dict]) -> Dict:
        """Placeholder logic to merge results from multiple models."""
        logger = logging.getLogger(__name__)
        if not results: return {}
        logger.info(f"Finding consensus from {len(results)} model outputs.")
        # Mock logic: just return the first result
        return results[0]

    # Enhancement 3: Active Learning
    def _critique_analysis(self, analysis: ThematicAnalysis) -> List[str]:
        """Placeholder logic for internal critique."""
        logger = logging.getLogger(__name__)
        logger.info("Critiquing analysis...")
        # Mock logic: assume it always needs refinement on the first pass
        if analysis.signal_quality_score < 0.5:
             analysis.signal_quality_score = 0.6 # Show improvement
             return ["role_archetype", "authenticity_patterns"]
        return [] # Empty list means PASS

    # Enhancement 5: Source Authority Weighting
    def _synthesize_analysis(self, analysis: ThematicAnalysis) -> ThematicAnalysis:
        """Placeholder for synthesis and source weighting."""
        logger = logging.getLogger(__name__)
        logger.info("Synthesizing final analysis with source authority weighting...")
        # Mock logic: just boost score
        analysis.signal_quality_score = 0.85
        return analysis

    # Enhancement 7: Graph-RAG Synthesis
    def _build_and_analyze_graph(self, analysis: ThematicAnalysis) -> ThematicAnalysis:
        """Placeholder for Graph-RAG synthesis."""
        logger = logging.getLogger(__name__)
        logger.info("Building and analyzing knowledge graph (Graph-RAG)...")
        G = nx.Graph()
        # Mock logic: add nodes and edges from analysis.evidence_log (which is not in placeholder)
        G.add_edge("Python", "Data Pipelines")
        G.add_edge("AWS", "Data Pipelines")
        centrality = nx.degree_centrality(G)
        logger.info(f"Graph centrality (mock): {centrality}")
        # ... logic to update analysis themes/keywords based on centrality ...
        analysis.primary_theme["centrality_score"] = centrality.get("Data Pipelines", 0)
        return analysis

    # Enhancement 6: Constitutional RAG Constraints
    def _apply_constitutional_constraints(self, analysis: ThematicAnalysis) -> ThematicAnalysis:
        """Placeholder for applying hard-coded safety filters."""
        logger = logging.getLogger(__name__)
        logger.info("Applying Constitutional RAG Constraints...")
        # Mock logic
        if "Director" in analysis.primary_theme.get("keywords", []):
            logger.warning("Constraint VIOLATION: Removed 'Director' from keywords.")
            # ... logic to filter 'Director' from skills/keywords ...
        return analysis

    def analyze(self, job_description) -> Tuple[ThematicAnalysis, int]:
         """Main analysis pipeline incorporating all enhancements."""
         logger = logging.getLogger(__name__)
         self.total_api_calls_hop0 = 0

         # Enhancement 8: Semantic Cache Check
         try:
             jd_embedding = self.embedding_client.embed(job_description)
             cached_result = self.semantic_cache.get(jd_embedding)
             if cached_result:
                 cached_analysis, similarity = cached_result
                 if self.semantic_cache._verify_cache(cached_analysis): # Verify freshness
                     logger.info(f"SEMANTIC CACHE HIT (Similarity: {similarity:.4f}). Skipping HOP-0 execution.")
                     return cached_analysis, 0 # Return cached result, 0 new API calls
         except Exception as e:
             logger.error(f"Semantic cache check failed: {e}")

         logger.info("Semantic cache miss or invalid. Executing full HOP-0 workflow.")

         # Pre-RAG (Step -0.5)
         mission = self._execute_pre_rag_analysis(job_description)

         # Main Agentic Loop (Enhancements 1, 2, 3, 4, 5)
         analysis = self._run_agentic_rag_loop(job_description, mission)

         # Post-processing (Enhancements 7)
         analysis = self._build_and_analyze_graph(analysis)

         # Final Filtering (Enhancement 6)
         analysis = self._apply_constitutional_constraints(analysis)

         # Save to semantic cache
         try:
             self.semantic_cache.set(jd_embedding, analysis)
         except Exception as e:
             logger.error(f"Failed to write to semantic cache: {e}")

         return analysis, self.total_api_calls_hop0

    def _dict_to_thematic_analysis(self, data: Dict) -> ThematicAnalysis:
         # Placeholder for reconstruction if needed from cache
         return ThematicAnalysis.from_dict(data)

# --- End Placeholder Definitions ---

def run_hop_0(args: argparse.Namespace):
    """Executes the HOP-0 RAG analysis logic."""
    # Use workflow_id and run_dir passed from orchestrator for consistent logging
    logger, _ = setup_workflow_logging(args.workflow_id, log_file_dir=args.run_dir)
    logger.info("--- Starting HOP-0: Job Description Analysis & RAG ---")
    start_time = datetime.now()
    api_calls = 0
    analyzer = None # Define analyzer in outer scope for finally block

    try:
        # Load config (assuming a function or method exists based on Rec #4)
        # config = load_config(args.config_path) # Example
        config_rag = RAGConfig() # Using placeholder default

        # Load Master Resume (passed via path)
        try:
            with open(args.master_resume_path, 'r', encoding='utf-8') as f:
                master_resume = json.load(f)
            logger.info(f"Loaded master resume from {args.master_resume_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to load master resume snapshot: {e}") from e

        # Load Job Description
        try:
            jd_path = Path(args.input_path_jd)
            job_description = jd_path.read_text(encoding='utf-8')
            logger.info(f"Loaded job description from {jd_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to load job description input: {e}") from e

        # Instantiate necessary components (DI would be better here)
        # Enhancement 8: Instantiate new clients
        embedding_client = EmbeddingClient(config_rag)
        semantic_cache = SemanticCacheManager(config_rag)

        # Pass all dependencies to the analyzer
        analyzer = EnhancedJobDescriptionAnalyzer(master_resume, config=config_rag, embedding_client=embedding_client, semantic_cache=semantic_cache, enable_web_search=True)
        
        # Execute the core analysis logic
        thematic_analysis, api_calls = analyzer.analyze(job_description)

        # Serialize the output ThematicAnalysis object
        # Ensure complex types within ThematicAnalysis are handled by default_serializer
        output_data = default_serializer(thematic_analysis) # Use serializer directly

        # Write the output JSON file
        try:
            output_path = Path(args.output_path_thematic_analysis)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=default_serializer) # Use helper serializer again just in case
            logger.info(f"Successfully wrote Thematic Analysis to {output_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to write output JSON: {e}") from e

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-0 Finished Successfully ({duration:.2f}s) ---")
        # Report API calls for orchestrator via stdout
        print(f"API Calls Made: {api_calls}")
        # Exit code 0 is implicit on successful completion

    except HopExecutionError as he:
        logger.error(f"HOP-0 HALTED: {he}", exc_info=False)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-0 Finished with HALT ({duration:.2f}s) ---")
        # Report calls even on failure if possible
        calls_on_fail = getattr(analyzer, 'total_api_calls_hop0', api_calls) if analyzer else api_calls
        print(f"API Calls Made: {calls_on_fail}")
        exit(1) # Exit with non-zero code

    except Exception as e:
        logger.error(f"HOP-0 FAILED with unexpected error: {e}", exc_info=True)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-0 Finished with FAILURE ({duration:.2f}s) ---")
        calls_on_fail = getattr(analyzer, 'total_api_calls_hop0', api_calls) if analyzer else api_calls
        print(f"API Calls Made: {calls_on_fail}")
        exit(1) # Exit with non-zero code

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HOP-0: Job Description Analysis & RAG")
    parser.add_argument("--workflow-id", required=True, help="Unique ID for the workflow run")
    parser.add_argument("--run-dir", required=True, help="Directory for the workflow run artifacts")
    parser.add_argument("--config-path", required=True, help="Path to the config file snapshot")
    parser.add_argument("--master-resume-path", required=True, help="Path to the master resume JSON snapshot")
    parser.add_argument("--input-path-jd", required=True, help="Path to the input job description text file")
    parser.add_argument("--output-path-thematic-analysis", required=True, help="Path to write the output ThematicAnalysis JSON")

    args = parser.parse_args()

    # Basic check for API key before running - enhance as needed
    if not os.environ.get("GEMINI_API_KEY"):
         logging.error("CRITICAL: GEMINI_API_KEY not found in environment. HOP-0 cannot run.")
         print("API Calls Made: 0") # Report 0 calls
         exit(1) # Fail early

    run_hop_0(args)