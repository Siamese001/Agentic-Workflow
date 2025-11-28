# hops/hop_0_rag.py
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
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple

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
# from shared.rag import RAGConfig, GeminiWebSearchClient, WebSearchRAG, RAGMission, JDCacheManager, TelemetryLogger, PhaseExecutor, CircuitBreaker, CompetitiveAnalysisConfig
# --- Start Placeholder Definitions ---
@dataclass
class RAGConfig: # Placeholder
    model: str = "gemini-1.5-flash-latest" # Example
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
    telemetry_enabled: bool = False
    telemetry_log_dir: str = "./rag_telemetry"
    source_weights: Dict = field(default_factory=dict)

class CircuitBreaker: # Placeholder
    def __init__(self, config): pass
    def call(self, func, *args, **kwargs): return func(*args, **kwargs) # Passthrough

class PhaseExecutor: # Placeholder
     def __init__(self, config): pass
     def execute_with_retry(self, func, name): return func() # No retry

class GeminiWebSearchClient: # Placeholder
    def __init__(self, config): self.api_calls_made = 0; self.circuit_breaker = CircuitBreaker(config) # Add circuit breaker attribute
    def search_and_analyze(self, prompt, phase_name) -> Tuple[Dict, int]:
        logging.warning(f"Using MOCK GeminiWebSearchClient for {phase_name}")
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
        return {}, 1 # Default mock

class WebSearchRAG: # Placeholder
    def __init__(self, client, config): self.client = client
    def phase1_thematic_research(self, jd, mission): return self.client.search_and_analyze("mock p1", "Phase 1")
    def phase2_authenticity_patterns(self, jd, mission): return self.client.search_and_analyze("mock p2", "Phase 2")
    def phase3_competitive_positioning(self, jd, mission): return self.client.search_and_analyze("mock p3", "Phase 3")
    def phase4_narrative_mining(self, mission): return self.client.search_and_analyze("mock p4", "Phase 4")

@dataclass
class RAGMission: # Placeholder
    target_company_name: str = "Default Co"
    precise_role_title: str = "Default Role"
    key_technologies: List = field(default_factory=list)
    core_responsibilities: List = field(default_factory=list)
    signal_gap_keywords: List = field(default_factory=list)
    signal_overlap_keywords: List = field(default_factory=list)

class JDCacheManager: # Placeholder
    def __init__(self, dir, ttl): pass
    def get(self, jd): return None
    def set(self, jd, analysis): pass

class TelemetryLogger: # Placeholder
     def __init__(self, log_dir): pass
     def log(self, telemetry): pass

@dataclass
class CompetitiveAnalysisConfig: # Placeholder
     pass

class EnhancedJobDescriptionAnalyzer:
    # --- Simplified Analyzer ---
    # This needs the full implementation moved here or imported
    def __init__(self, master_resume, enable_web_search=True, config=None):
        self.master_resume = master_resume
        self.config = config or RAGConfig()
        # In real version, these would be properly initialized based on config/DI
        self.gemini_client = GeminiWebSearchClient(self.config)
        self.web_rag = WebSearchRAG(self.gemini_client, self.config)
        self.cache_manager = JDCacheManager(self.config.cache_dir, self.config.cache_ttl_days)
        self.telemetry_logger = None # Disabled for simplicity
        self.total_api_calls_hop0 = 0
        self.rag_mission = None

    def _execute_pre_rag_analysis(self, job_description: str) -> RAGMission:
        """Simplified mock pre-rag"""
        logger = logging.getLogger(__name__)
        logger.info("Executing MOCK HOP -0.5: Pre-RAG Differential Analysis...")
        # Simulate API call
        analysis_json, pre_rag_calls = self.gemini_client.search_and_analyze("mock pre-rag", "Pre-RAG Analysis")
        self.total_api_calls_hop0 += pre_rag_calls
        # Use mock data, ensure keys exist
        mission = RAGMission(
            target_company_name=analysis_json.get("jd_entities", {}).get("target_company_name", "Unknown"),
            precise_role_title=analysis_json.get("jd_entities", {}).get("precise_role_title", "Unknown"),
            key_technologies=analysis_json.get("jd_entities", {}).get("key_technologies", []),
            core_responsibilities=analysis_json.get("jd_entities", {}).get("core_responsibilities", []),
            signal_gap_keywords=analysis_json.get("differential_analysis", {}).get("signal_gap_keywords", []),
            signal_overlap_keywords=analysis_json.get("differential_analysis", {}).get("signal_overlap_keywords", [])
        )
        logger.info(f"  ✓ Mock RAG Mission defined.")
        return mission

    def _analyze_with_resilient_web_search(self, job_description) -> Tuple[ThematicAnalysis, int]:
         """Simplified mock web search"""
         logger = logging.getLogger(__name__)
         total_calls = 0
         # Simulate calling RAG phases
         try:
             _, calls_p1 = self.web_rag.phase1_thematic_research(job_description, self.rag_mission)
             total_calls += calls_p1
             _, calls_p2 = self.web_rag.phase2_authenticity_patterns(job_description, self.rag_mission)
             total_calls += calls_p2
             _, calls_p3 = self.web_rag.phase3_competitive_positioning(job_description, self.rag_mission)
             total_calls += calls_p3
             _, calls_p4 = self.web_rag.phase4_narrative_mining(self.rag_mission)
             total_calls += calls_p4
         except Exception as e:
              logger.error(f"Mock RAG phase failed: {e}")
              raise HopExecutionError(f"Mock RAG failed: {e}")

         # Return a basic ThematicAnalysis object
         mock_analysis = ThematicAnalysis(
             primary_theme={"name": "Mock Primary Theme"},
             signal_quality_score=0.75,
             retrieval_method="MOCK_RAG"
         )
         logger.info(f"Mock RAG analysis complete. API Calls: {total_calls}")
         return mock_analysis, total_calls

    def analyze(self, job_description) -> Tuple[ThematicAnalysis, int]:
         """Simplified analyze method"""
         self.total_api_calls_hop0 = 0
         self.rag_mission = self._execute_pre_rag_analysis(job_description)
         analysis, calls_rag = self._analyze_with_resilient_web_search(job_description)
         self.total_api_calls_hop0 += calls_rag
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
        # Pass loaded config object
        analyzer = EnhancedJobDescriptionAnalyzer(master_resume, enable_web_search=True, config=config_rag)

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