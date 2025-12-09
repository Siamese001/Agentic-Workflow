# hops/00_hop_rag_v1_3.py
"""
Hop 0: Job Description Analysis & RAG (v1.3 - Merged)
Combines v1.1 Agentic Orchestrator with v1.2 Circuit Breaker Integration
Reads job description text, performs agentic, multi-phase RAG analysis,
and writes the resulting ThematicAnalysis object as JSON.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List

# Imports for enhancements
import networkx as nx
import numpy as np

# Add project root to path to allow importing shared modules
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import necessary components from helpers
from helpers import (
    setup_workflow_logging, _load_json_data, HopExecutionError, default_serializer,
    CircuitState
)

# --- Define Classes needed specifically for HOP-0 ---

# v1.1: Added/Updated dataclasses for State Management (#1, #13)
@dataclass
class ThematicAnalysis:
    """Represents the final output of the RAG analysis."""
    primary_theme: Dict = field(default_factory=dict)
    signal_quality_score: float = 0.0
    retrieval_method: str = "MOCK"
    # v1.1: evidence_log added to track agentic steps (#13)
    evidence_log: List[Dict] = field(default_factory=list) 
    # Additional fields
    competitive_intelligence: Any = None
    
    @staticmethod
    def from_dict(data):
        """Mock static method for reconstruction"""
        return ThematicAnalysis(
            primary_theme=data.get("primary_theme", {}),
            signal_quality_score=data.get("signal_quality_score", 0.0),
            retrieval_method=data.get("retrieval_method", "MOCK_FROM_DICT"),
            evidence_log=data.get("evidence_log", []),
            competitive_intelligence=data.get("competitive_intelligence")
        )

@dataclass
class RAGCritique:
    """Output of the LLM-powered critique step."""
    is_sufficient: bool = False
    confidence_score: float = 0.0
    critique_text: str = ""
    # v1.1 / #7: Active Learning - tasks suggested by LLM
    refinement_tasks: List[str] = field(default_factory=list)

@dataclass
class RAGState:
    """Manages the state of the agentic RAG loop."""
    mission: RAGMission
    job_description: str
    current_analysis: ThematicAnalysis
    critique_history: List[RAGCritique] = field(default_factory=list)
    
    def get_latest_evidence(self) -> str:
        """Helper to format evidence for the next prompt."""
        if not self.current_analysis.evidence_log:
            return "No evidence gathered yet. This is the first step."
        # Return a summary of the last 5 evidence pieces
        evidence_summary = [
            f"Phase: {entry.get('phase')}, Summary: {entry.get('result_snippet')}"
            for entry in self.current_analysis.evidence_log[-5:]
        ]
        return "LATEST EVIDENCE:\n" + json.dumps(evidence_summary, indent=2)

@dataclass
class RAGConfig:
    """Configuration for RAG operations with circuit breaker settings"""
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
    semantic_cache_threshold: float = 0.92
    semantic_cache_dir: str = "./semantic_cache"
    telemetry_enabled: bool = False
    telemetry_log_dir: str = "./rag_telemetry"
    source_weights: Dict = field(default_factory=lambda: {"blogs.company.com": 1.5, "github.com": 1.4, "generic-jobs.com": 0.8})
    max_refinement_loops: int = 3

@dataclass
class RAGMission:
    """Mission context extracted from pre-RAG analysis"""
    target_company_name: str = "Default Co"
    precise_role_title: str = "Default Role"
    key_technologies: List = field(default_factory=list) 
    core_responsibilities: List = field(default_factory=list)
    signal_gap_keywords: List = field(default_factory=list)
    signal_overlap_keywords: List = field(default_factory=list)

# --- Circuit Breaker Implementation (v1.3 Enhanced) ---

class CircuitBreaker:
    """
    v1.3: Full circuit breaker implementation for resilient RAG operations.
    Tracks failures and transitions between CLOSED, OPEN, and HALF_OPEN states.
    """
    def __init__(self, config: RAGConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        self.logger = logging.getLogger(__name__)

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.logger.info("Circuit breaker transitioning to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
            else:
                raise HopExecutionError(
                    f"Circuit breaker is OPEN. Too many failures ({self.failure_count}). "
                    f"Wait {self.config.circuit_breaker_timeout}s before retry."
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful operation"""
        if self.state == CircuitState.HALF_OPEN:
            self.logger.info("Circuit breaker recovering: HALF_OPEN -> CLOSED")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.circuit_breaker_threshold:
            self.logger.error(
                f"Circuit breaker opening: {self.failure_count} failures reached threshold"
            )
            self.state = CircuitState.OPEN
        
        self.logger.warning(
            f"Circuit breaker failure {self.failure_count}/{self.config.circuit_breaker_threshold}. "
            f"State: {self.state.value}"
        )

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if not self.last_failure_time:
            return False
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.config.circuit_breaker_timeout

# --- Phase Executor (v1.3 Enhanced) ---

class PhaseExecutor:
    """v1.3: Phase execution with retry logic"""
    def __init__(self, config: RAGConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def execute_with_retry(self, func, name):
        """Execute phase with retry logic"""
        for attempt in range(self.config.phase_max_retries):
            try:
                return func()
            except Exception as e:
                self.logger.warning(f"Phase {name} attempt {attempt + 1} failed: {e}")
                if attempt == self.config.phase_max_retries - 1:
                    raise
                time.sleep(self.config.api_initial_backoff_seconds * (attempt + 1))
        return func()

# --- Mock RAG Components ---

class GeminiWebSearchClient:
    """Mock Gemini client with circuit breaker (v1.3 enhanced)"""
    def __init__(self, config: RAGConfig, model_name: str):
        self.model_name = model_name
        self.api_calls_made = 0
        self.circuit_breaker = CircuitBreaker(config)
        self.logger = logging.getLogger(__name__)

    def search_and_analyze(self, prompt: str, phase_name: str) -> Tuple[Dict, int]:
        """Execute search with circuit breaker protection"""
        def _execute():
            self.logger.warning(f"Using MOCK GeminiWebSearchClient ({self.model_name}) for {phase_name}")
            self.api_calls_made += 1
            time.sleep(0.05)  # Simulate latency
            
            # Return mock data structure based on phase_name
            if "Pre-RAG" in phase_name:
                return {
                    "jd_entities": {"target_company_name": "Mock Co", "precise_role_title": "Mock Role", "key_technologies": ["mock", "test"], "core_responsibilities": ["mocking"]},
                    "resume_entities": {"candidate_skills": ["mock", "dev"]},
                    "differential_analysis": {"signal_gap_keywords": ["test"], "signal_overlap_keywords": ["mock"]}
                }, 1
            elif "Phase 1" in phase_name:
                return {"search_summary": {"source": "mock.com"}, "thematic_analysis": {"primary_theme": {"name": "Mock P1 Theme", "keywords": ["mock", "test"]}}}, 1
            elif "Phase 2" in phase_name:
                return {"search_summary": {"source": "github.com"}, "authenticity_patterns": {"employee_count": 5}}, 1
            elif "Phase 3" in phase_name:
                return {"search_summary": {"source": "blogs.company.com"}, "competitive_analysis": {"key_rival": "Test Inc"}}, 1
            elif "Phase 4" in phase_name:
                return {"search_summary": {"source": "generic-jobs.com"}, "problem_solution_narratives": {"found": 1}}, 1
            elif "Phase 5 (Adversary)" in phase_name:
                return {"search_summary": {}, "adversarial_findings": {"refuted_themes": ["Mock P1 Theme"]}}, 1
            elif "Critique" in phase_name:
                # Mock critique response
                if "0.5" in prompt or "0.1" in prompt:  # Check if score is low
                    return {"is_sufficient": False, "confidence_score": 0.6, "critique_text": "Mock Critique: P1 theme weak. Need P2 fingerprinting.", "refinement_tasks": ["run_P2", "refine_P1_themes"]}, 1
                else:
                    return {"is_sufficient": True, "confidence_score": 0.9, "critique_text": "Mock Critique: Analysis looks solid.", "refinement_tasks": []}, 1
            elif "Refinement" in phase_name:
                return {"search_summary": {"source": "refined.com"}, "thematic_analysis": {"primary_theme": {"name": "Refined Mock P1 Theme"}}}, 1
            return {}, 1
        
        return self.circuit_breaker.call(_execute)

class WebSearchRAG:
    """
    v1.1: This class is now a "dumb" executor. It just runs the LLM calls.
    The orchestration logic is in EnhancedJobDescriptionAnalyzer.
    """
    def __init__(self, clients: Dict[str, GeminiWebSearchClient], config: RAGConfig): 
        self.clients = clients
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def _get_client(self, model_name: str): 
        return self.clients[model_name]

    # v1.1: All phases now accept 'evidence' (#2)
    def phase1_thematic_research(self, jd: str, mission: RAGMission, evidence: str, model_name: str) -> Tuple[Dict, int]: 
        prompt = f"P1: Find primary themes for role. JD: {jd[:100]}... Mission: {mission.precise_role_title}. Evidence: {evidence}"
        return self._get_client(model_name).search_and_analyze(prompt, "Phase 1")
    
    # v1.1: Added evidence arg and (mock) fingerprinting prompt (#8)
    def phase2_authenticity_patterns(self, jd: str, mission: RAGMission, evidence: str, model_name: str) -> Tuple[Dict, int]: 
        prompt = f"P2: Authenticate role. Search for employee profiles at {mission.target_company_name} matching tech: {mission.key_technologies}. Evidence: {evidence}"
        return self._get_client(model_name).search_and_analyze(prompt, "Phase 2")
    
    def phase3_competitive_positioning(self, jd: str, mission: RAGMission, evidence: str, model_name: str) -> Tuple[Dict, int]: 
        prompt = f"P3: Find competitive positioning for {mission.target_company_name}. Evidence: {evidence}"
        return self._get_client(model_name).search_and_analyze(prompt, "Phase 3")
    
    # v1.1: P4 signature changed to add evidence
    def phase4_narrative_mining(self, mission: RAGMission, evidence: str, model_name: str) -> Tuple[Dict, int]: 
        prompt = f"P4: Find problem/solution narratives for {mission.target_company_name}. Evidence: {evidence}"
        return self._get_client(model_name).search_and_analyze(prompt, "Phase 4")

    # v1.1: Renamed from phase5_... (#6) and added evidence
    def adversarial_verification_step(self, analysis: ThematicAnalysis, mission: RAGMission, evidence: str, model_name: str) -> Tuple[Dict, int]: 
        prompt = f"P5 (Adversary): Refute the themes in this analysis: {json.dumps(asdict(analysis))}. Evidence: {evidence}"
        return self._get_client(model_name).search_and_analyze(prompt, "Phase 5 (Adversary)")

    # v1.1: Added critique step (#3, #7)
    def critique_step_output(self, analysis: ThematicAnalysis, mission: RAGMission, evidence: str, model_name: str) -> Tuple[Dict, int]:
        prompt = f"""
        Critique the following analysis based on the evidence.
        Analysis: {json.dumps(asdict(analysis))}
        Evidence: {evidence}
        Mission: {json.dumps(asdict(mission))}
        
        Respond ONLY in JSON with fields:
        - is_sufficient (bool): Is the analysis complete and high-confidence?
        - confidence_score (float): 0.0-1.0
        - critique_text (str): Your reasoning.
        - refinement_tasks (List[str]): List of tasks to improve. 
          (Valid tasks: 'run_P1', 'run_P2', 'run_P3', 'run_P4', 'refine_P1_themes', 'run_P5_adversarial')
        """
        # This calls the MOCK critique response from GeminiWebSearchClient
        return self._get_client(model_name).search_and_analyze(prompt, "Critique")

    # v1.1: Added targeted refinement step (#4)
    def run_refinement_step(self, task: str, analysis: ThematicAnalysis, mission: RAGMission, evidence: str, model_name: str) -> Tuple[Dict, int]:
        prompt = f"Execute refinement task: {task}. Current Analysis: {json.dumps(asdict(analysis))}. Evidence: {evidence}"
        return self._get_client(model_name).search_and_analyze(prompt, f"Refinement ({task})")

class EmbeddingClient:
    """Mock EmbeddingClient for semantic analysis"""
    def __init__(self, config=None):
        logging.info("Initialized MOCK EmbeddingClient")
        self.dimension = 768

    def embed(self, text: str) -> np.ndarray:
        """Generate mock embedding"""
        if not text:
            return np.zeros(self.dimension)
        hash_val = hash(text)
        np.random.seed(hash_val % (2**32 - 1))
        return np.random.rand(self.dimension)

class SemanticCacheManager:
    """Mock semantic cache manager"""
    def __init__(self, config: RAGConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get(self, embedding: np.ndarray) -> Tuple[ThematicAnalysis, float] | None:
        self.logger.warning("Using MOCK SemanticCacheManager.get")
        return None  # Simulate cache miss

    def set(self, embedding: np.ndarray, analysis: ThematicAnalysis):
        self.logger.warning("Using MOCK SemanticCacheManager.set")
        pass

    def _verify_cache(self, analysis: ThematicAnalysis) -> bool:
        self.logger.warning("Using MOCK SemanticCacheManager._verify_cache")
        return True

class TelemetryLogger:
    """Placeholder for telemetry logging"""
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
    
    def log(self, telemetry: Dict):
        pass

class EnhancedJobDescriptionAnalyzer:
    """
    v1.1/v1.3: Agentic Orchestrator with Circuit Breaker Integration.
    Manages the RAGState and executes the Execute-Critique-Replan loop.
    """
    def __init__(self, master_resume, config: RAGConfig, embedding_client: EmbeddingClient, 
                 semantic_cache: SemanticCacheManager, enable_web_search=True):
        self.master_resume = master_resume
        self.config = config or RAGConfig()

        self.model_clients = {
            model: GeminiWebSearchClient(self.config, model)
            for model in self.config.models
        }
        self.web_rag = WebSearchRAG(self.model_clients, self.config)
        self.primary_client = self.model_clients[self.config.models[0]]

        # v1.1: Use Semantic Cache (#12)
        self.embedding_client = embedding_client
        self.semantic_cache = semantic_cache
        self.telemetry_logger = None
        self.total_api_calls_hop0 = 0
        self.logger = logging.getLogger(__name__)

    def analyze(self, job_description: str) -> Tuple[ThematicAnalysis, int]:
        """v1.1/v1.3: Main orchestration entry point with circuit breaker protection."""
        self.total_api_calls_hop0 = 0

        # 1. Semantic Cache Check (#12)
        try:
            jd_embedding = self.embedding_client.embed(job_description)
            cached_result = self.semantic_cache.get(jd_embedding)
            if cached_result:
                cached_analysis, similarity = cached_result
                if self.semantic_cache._verify_cache(cached_analysis): 
                    self.logger.info(f"SEMANTIC CACHE HIT (Similarity: {similarity:.4f}). Skipping HOP-0 execution.")
                    return cached_analysis, 0 
        except Exception as e:
            self.logger.error(f"Semantic cache check failed: {e}")

        self.logger.info("Semantic cache miss or invalid. Executing full HOP-0 workflow.")

        # 2. Pre-RAG (Step -0.5)
        mission = self._execute_pre_rag_analysis(job_description)

        # 3. Agentic RAG Loop (v1.1) (#1)
        analysis = self._analyze_with_agentic_orchestration(job_description, mission)

        # 4. Post-processing & Synthesis (#9, #10, #11)
        analysis = self._synthesize_final_analysis(analysis)

        # 5. Save to semantic cache
        try:
            self.semantic_cache.set(jd_embedding, analysis)
        except Exception as e:
            self.logger.error(f"Failed to write to semantic cache: {e}")

        return analysis, self.total_api_calls_hop0

    def _execute_pre_rag_analysis(self, job_description: str) -> RAGMission:
        """Simplified mock pre-rag (from v1.0)."""
        self.logger.info("Executing MOCK HOP -0.5: Pre-RAG Differential Analysis...")
        analysis_json, pre_rag_calls = self.primary_client.search_and_analyze("mock pre-rag", "Pre-RAG Analysis")
        self.total_api_calls_hop0 += pre_rag_calls
        mission = RAGMission(
            target_company_name=analysis_json.get("jd_entities", {}).get("target_company_name", "Unknown"),
            precise_role_title=analysis_json.get("jd_entities", {}).get("precise_role_title", "Unknown"),
            key_technologies=analysis_json.get("jd_entities", {}).get("key_technologies", []), 
            core_responsibilities=analysis_json.get("jd_entities", {}).get("core_responsibilities", []),
            signal_gap_keywords=analysis_json.get("differential_analysis", {}).get("signal_gap_keywords", []),
            signal_overlap_keywords=analysis_json.get("differential_analysis", {}).get("signal_overlap_keywords", [])
        )
        self.logger.info(f"  ✓ Mock RAG Mission defined for {mission.target_company_name}.")
        return mission

    # v1.1: New Agentic Loop (#1)
    def _analyze_with_agentic_orchestration(self, job_description: str, mission: RAGMission) -> ThematicAnalysis:
        """v1.1: Implements the Execute -> Store -> Critique -> Re-plan loop."""
        self.logger.info("Starting HOP-0 Agentic RAG Orchestration (v1.3)...")
        
        state = RAGState(
            mission=mission,
            job_description=job_description,
            current_analysis=ThematicAnalysis(
                primary_theme={"name": "Initial Stub Theme"},
                signal_quality_score=0.1,  # Start score low
                retrieval_method="AGENTIC_ORCHESTRATOR_V1.3"
            )
        )

        # v1.1: Initial plan is a list of task strings
        current_plan: List[str] = ["run_P1", "run_P2", "run_P3", "run_P4"]
        
        for i in range(self.config.max_refinement_loops):
            self.logger.info(f"Agentic Loop: Iteration {i+1}/{self.config.max_refinement_loops}")
            evidence = state.get_latest_evidence()

            # 1. EXECUTE current plan
            if current_plan:
                self.logger.info(f"Executing plan: {current_plan}")
                for task in current_plan:
                    consensus_result, calls = {}, 0
                    task_name = task  # Default task name
                    
                    # Orchestrator maps task string to function call
                    if task == "run_P1":
                        consensus_result, calls = self._execute_phase_with_consensus(
                            self.web_rag.phase1_thematic_research, "P1 Thematic", 
                            [state.job_description, state.mission, evidence]
                        )
                    elif task == "run_P2":
                        consensus_result, calls = self._execute_phase_with_consensus(
                            self.web_rag.phase2_authenticity_patterns, "P2 Authenticity", 
                            [state.job_description, state.mission, evidence]
                        )
                    elif task == "run_P3":
                        consensus_result, calls = self._execute_phase_with_consensus(
                            self.web_rag.phase3_competitive_positioning, "P3 Competitive", 
                            [state.job_description, state.mission, evidence]
                        )
                    elif task == "run_P4":
                        consensus_result, calls = self._execute_phase_with_consensus(
                            self.web_rag.phase4_narrative_mining, "P4 Narrative", 
                            [state.mission, evidence]  # Note: Different args
                        )
                    elif task.startswith("refine_"):  # (#4)
                        consensus_result, calls = self._execute_phase_with_consensus(
                            self.web_rag.run_refinement_step, f"Refinement ({task})",
                            [task, state.current_analysis, state.mission, evidence]
                        )
                    else:
                        self.logger.warning(f"Unknown task in plan: {task}. Skipping.")
                        continue
                    
                    self.total_api_calls_hop0 += calls
                    # 2. STORE EVIDENCE
                    self._store_evidence(state, task_name, consensus_result)
            
            # 3. CRITIQUE (#3, #7)
            self.logger.info("Critiquing current analysis...")
            evidence = state.get_latest_evidence()
            # Critique runs on the primary (most powerful) model
            critique_json, calls = self.web_rag.critique_step_output(
                state.current_analysis, state.mission, evidence, self.config.models[0]
            )
            self.total_api_calls_hop0 += calls
            critique = RAGCritique(**critique_json)
            state.critique_history.append(critique)

            if critique.is_sufficient:
                self.logger.info(f"Critique PASSED (Confidence: {critique.confidence_score}). Exiting refinement loop.")
                break
            
            # 4. RE-PLAN
            self.logger.warning(f"Critique FAILED. Re-planning based on tasks: {critique.refinement_tasks}")
            current_plan = critique.refinement_tasks  # New plan comes from LLM
            
            if not current_plan:
                self.logger.error("Critique failed but no refinement plan was generated. Breaking.")
                break

        # After loop, run final adversarial check (#6)
        self.logger.info("Executing Adversarial Self-Play Verification...")
        evidence = state.get_latest_evidence()
        adversarial_result, calls = self._execute_phase_with_consensus(
            self.web_rag.adversarial_verification_step, "P5 Adversarial",
            [state.current_analysis, state.mission, evidence] 
        )
        self.total_api_calls_hop0 += calls
        self._store_evidence(state, "run_P5_adversarial", adversarial_result)
        
        return state.current_analysis

    # v1.1: New helper for agentic loop
    def _store_evidence(self, state: RAGState, phase_name: str, result: Dict):
        """Helper to store phase results in the evidence log and update analysis."""
        if not result:
            self.logger.warning(f"No result to store for phase {phase_name}")
            return
            
        # Store a snippet in the log
        state.current_analysis.evidence_log.append({
            "timestamp": datetime.now().isoformat(),
            "phase": phase_name,
            "result_snippet": result.get("search_summary", {"source": "N/A"}),
            "full_result_keys": list(result.keys())  # For debug
        })
        
        # In a real app, this would deeply merge 'result' into 'state.current_analysis'
        # Mock merge:
        if "thematic_analysis" in result and "primary_theme" in result["thematic_analysis"]:
            state.current_analysis.primary_theme = result["thematic_analysis"]["primary_theme"]
            self.logger.info(f"Stored evidence and updated primary theme from {phase_name}.")
        
        # Hacky score update for mock loop
        if state.current_analysis.signal_quality_score < 0.8:
            state.current_analysis.signal_quality_score += 0.4  # Big jump for mock
        else:
            state.current_analysis.signal_quality_score = 0.9

    # v1.1: Updated to fix v1.0 bug and support agentic loop
    def _execute_phase_with_consensus(self, phase_func: callable, phase_name: str, model_args: List) -> Tuple[Dict, int]:
        """
        v1.1/v1.3: Runs a phase function across multiple models and finds consensus.
        'model_args' is the list of args *before* model_name.
        """
        all_results = []
        total_calls = 0
        
        # v1.1 / #5: Placeholder for Multi-Model Consensus
        # In a real implementation, these calls would be parallelized
        for model in self.config.models:
            try:
                # Pass all args, plus the model_name
                result_json, calls = phase_func(*model_args, model_name=model)
                all_results.append(result_json)
                total_calls += calls
            except Exception as e:
                self.logger.error(f"Failed to run phase {phase_name} with model {model}: {e}", exc_info=True)
        
        self.logger.info(f"Consensus: Executed {phase_name} on {len(all_results)} models.")
        consensus_data = self._find_consensus(all_results)
        return consensus_data, total_calls

    def _find_consensus(self, results: List[Dict]) -> Dict:
        """Placeholder logic to merge results from multiple models."""
        if not results:
            return {}
        # v1.1 / #5: Mock logic: just return the first valid result
        valid_results = [r for r in results if r]
        if not valid_results:
            return {}
        
        # In a real app:
        # 1. Vote on key fields (e.g., primary_theme name)
        # 2. Merge/union lists (e.g., keywords)
        # 3. Average scores
        self.logger.info(f"Finding consensus from {len(valid_results)} model outputs (Mock: returning first).")
        return valid_results[0]

    # v1.1: New helper to consolidate post-processing
    def _synthesize_final_analysis(self, analysis: ThematicAnalysis) -> ThematicAnalysis:
        """
        v1.1: Consolidates all post-processing and synthesis steps.
        """
        # Enhancement 5: Source Authority Weighting (#9)
        # Placeholder: This is where we'd analyze analysis.evidence_log,
        # find source URLs, and re-score themes based on self.config.source_weights.
        self.logger.info("v1.3 Placeholder: Applying Source Authority Weighting...")
        # score = self._apply_source_weighting(analysis.evidence_log)
        # analysis.signal_quality_score = max(analysis.signal_quality_score, score)
        
        # Enhancement 7: Graph-RAG Synthesis (#11)
        self.logger.info("v1.3 Placeholder: Applying Graph-RAG Synthesis...")
        analysis = self._build_and_analyze_graph(analysis)
        
        # Enhancement 6: Constitutional RAG Constraints (#10)
        self.logger.info("v1.3 Placeholder: Applying Constitutional RAG Constraints...")
        analysis = self._apply_constitutional_constraints(analysis)

        self.logger.info("Synthesizing final analysis...")
        analysis.signal_quality_score = max(analysis.signal_quality_score, 0.95)  # Final mock boost
        analysis.retrieval_method = "AGENTIC_ORCHESTRATOR_V1.3_CB"

        return analysis

    # --- (Placeholder methods from v1.0, now called by _synthesize_final_analysis) ---

    def _build_and_analyze_graph(self, analysis: ThematicAnalysis) -> ThematicAnalysis:
        """Placeholder for Graph-RAG synthesis."""
        self.logger.info("Building and analyzing knowledge graph (Graph-RAG)...")
        G = nx.Graph()
        # Mock logic
        G.add_edge("Python", "Data Pipelines")
        G.add_edge("AWS", "Data Pipelines")
        if analysis.primary_theme.get("keywords"):
            for kw in analysis.primary_theme["keywords"]:
                G.add_edge(kw, "Primary Theme")
        centrality = nx.degree_centrality(G)
        self.logger.info(f"Graph centrality (mock): {centrality}")
        analysis.primary_theme["centrality_score"] = centrality.get("Data Pipelines", 0)
        return analysis

    def _apply_constitutional_constraints(self, analysis: ThematicAnalysis) -> ThematicAnalysis:
        """Placeholder for applying hard-coded safety filters."""
        self.logger.info("Applying Constitutional RAG Constraints...")
        # Mock logic
        if "Director" in analysis.primary_theme.get("keywords", []):
            self.logger.warning("Constraint VIOLATION: Removed 'Director' from keywords.")
            # ... logic to filter 'Director' ...
        return analysis

    def _dict_to_thematic_analysis(self, data: Dict) -> ThematicAnalysis:
        # v1.1: Use the static method on the placeholder class
        return ThematicAnalysis.from_dict(data)

# --- End Placeholder Definitions ---

def run_hop_0(args: argparse.Namespace):
    """Executes the HOP-0 RAG analysis logic with circuit breaker."""
    logger, _ = setup_workflow_logging(args.workflow_id, log_file_dir=args.run_dir)
    logger.info("--- Starting HOP-0: Job Description Analysis & RAG (v1.3 Merged) ---")
    start_time = datetime.now()
    api_calls = 0
    analyzer = None 

    try:
        config_rag = RAGConfig()  # Using placeholder default

        # Load Master Resume
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

        # Instantiate necessary components
        embedding_client = EmbeddingClient(config_rag)
        semantic_cache = SemanticCacheManager(config_rag)

        # Pass all dependencies to the analyzer
        analyzer = EnhancedJobDescriptionAnalyzer(
            master_resume, config=config_rag, embedding_client=embedding_client, 
            semantic_cache=semantic_cache, enable_web_search=True
        )
        
        # Execute the core analysis logic
        thematic_analysis, api_calls = analyzer.analyze(job_description)

        # Serialize the output ThematicAnalysis object
        output_data = default_serializer(thematic_analysis) 

        # Write the output JSON file
        try:
            output_path = Path(args.output_path_thematic_analysis)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=default_serializer)
            logger.info(f"Successfully wrote Thematic Analysis to {output_path}")
        except Exception as e:
            raise HopExecutionError(f"Failed to write output JSON: {e}") from e

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-0 Finished Successfully ({duration:.2f}s) ---")
        print(f"API Calls Made: {api_calls}")

    except HopExecutionError as he:
        logger.error(f"HOP-0 HALTED: {he}", exc_info=False)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-0 Finished with HALT ({duration:.2f}s) ---")
        calls_on_fail = getattr(analyzer, 'total_api_calls_hop0', api_calls) if analyzer else api_calls
        print(f"API Calls Made: {calls_on_fail}")
        exit(1) 

    except Exception as e:
        logger.error(f"HOP-0 FAILED with unexpected error: {e}", exc_info=True)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"--- HOP-0 Finished with FAILURE ({duration:.2f}s) ---")
        calls_on_fail = getattr(analyzer, 'total_api_calls_hop0', api_calls) if analyzer else api_calls
        print(f"API Calls Made: {calls_on_fail}")
        exit(1) 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HOP-0: Job Description Analysis & RAG (v1.3 Merged)")
    parser.add_argument("--workflow-id", required=True, help="Unique ID for the workflow run")
    parser.add_argument("--run-dir", required=True, help="Directory for the workflow run artifacts")
    parser.add_argument("--config-path", required=True, help="Path to the config file snapshot")
    parser.add_argument("--master-resume-path", required=True, help="Path to the master resume JSON snapshot")
    parser.add_argument("--input-path-jd", required=True, help="Path to the input job description text file")
    parser.add_argument("--output-path-thematic-analysis", required=True, help="Path to write the output ThematicAnalysis JSON")

    args = parser.parse_args()

    if not os.environ.get("GEMINI_API_KEY"):
        logging.error("CRITICAL: GEMINI_API_KEY not found in environment. HOP-0 cannot run.")
        print("API Calls Made: 0")
        exit(1) 

    run_hop_0(args)
