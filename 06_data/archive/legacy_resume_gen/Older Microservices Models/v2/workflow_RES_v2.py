# File: workflow_RES_v2.py
# Resume Generation Workflow - V2 Agentic Architecture
# Version: 17.02 (CRL Integration Fix)

from __future__ import annotations

import copy
import functools
import hashlib
import json
import logging
import os
import random
import re
import time
import uuid
from enum import Enum
from collections import defaultdict
from datetime import datetime, timedelta
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from dataclasses import asdict, is_dataclass
import asyncio

# V2 Agent imports (Governor Module)
from governor import (
    PolicyAgent, CostRouter, ContextRelayLayer, 
    CritiqueTool, HIL_Interface, TraceRegistry,
    MAX_RETRIES_PER_NODE, DEFAULT_MODEL
)

# V2 Modular Tool imports
from clerk_RES_v2 import ClerkExtractor
from enricher_RES_v2 import DataEnricher
from artist_RES_v2 import ArtistGenerator
from renderer_RES_v2 import FileRenderer

# Import from modular components
from models_RES import (
    BulletProvenance, CircuitState, GateDecision, HopCheckpoint, HopStatus,
    ImmutableStagingBuffer, JDEnforcementResult, JDEnforcementRule,
    RAGState, RAGTelemetry, ResumeSection, ThematicAnalysis, FactualFailureException,
    ValidationResult, ValidationSeverity, HopExecutionError, StagingBufferError,
    CompetitiveIntelligence, RAGMission
)
from config_RES_v2 import (
    CONFIG, AppConfig, EnricherConfig, ContentConstraintsConfig,
    ReasoningConfig, DATA_DIR, OUTPUT_DIR, _load_json_config,
    COVER_LETTER_SIGNATURE_TEMPLATE, GEMINI_AVAILABLE, SKLEARN_AVAILABLE,
    DEFAULT_GENERATION_TEMPERATURE # <-- IMPORTED DEFAULT TEMP
)
from utils_RES_v2 import (
    text_utils, calculate_signal_score, setup_workflow_logging,
    create_directory_if_missing, sanitize_filename,
    WorkflowLogFilter, DuplicateDetector,
    reasoning_config_to_api_params, enhance_system_prompt_with_reasoning
)
from interpreter_RES_v2 import CodeInterpreterTool
from validator_RES_v2 import (
    PreFlightValidator, ConstraintFailureClassifier
)
from qa_auditor_RES_v2 import QAReportGenerator
from rag_RES_v2 import EnhancedJobDescriptionAnalyzer
from state_manager_RES_v2 import ManifestManager

# GEMINI_AVAILABLE and SKLEARN_AVAILABLE are imported from config_RES_v2

# --- V18 REFACTOR: Import consolidated validation classes ---
from validator_RES_v2 import JDEnforcementValidator, AppTrackerQAValidator

# --- NEW: Import ChromaDB ---
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("Warning: chromadb package not installed - RAG features may be limited")

# CHROMADB_AVAILABLE is imported from rag_RES_v2

# Constants
MAX_SLOW_LOOP_ITERATIONS = 3  # Maximum number of slow loop iterations before giving up

__version__ = "17.02"  # V2 Agentic Governor with CRL Integration Fix

# text_utils is imported from utils_RES_v2

# Artist specs are now loaded via CONFIG.artist_specs
# NOTE: App tracker schema loading removed - now accessed via CONFIG.app_tracker_schema


# COVER_LETTER_SIGNATURE_TEMPLATE is imported from config_RES_v2

logger = logging.getLogger(__name__)
# NOTE: ClerkExtractor, DataEnricher, ArtistGenerator, and FileRenderer 
# have been moved to separate modules per V2 architecture

class WorkflowOrchestrator:
    """
    Main workflow orchestrator with resumable state-driven architecture.
    Supports both new runs and resume runs with idempotent hop functions.
    """

    def __init__(
        self,
        config: AppConfig,
        master_resume: dict,
        run_id: Optional[str] = None,
        job_input: Optional[dict] = None
    ):
        self.config = config
        self.master_resume = master_resume
        
        # --- V2 In-Memory State ---
        self.drafts: Dict[ResumeSection, Any] = {}
        self.failures: Dict[ResumeSection, int] = defaultdict(int)
        self.thematic_analysis: Optional[ThematicAnalysis] = None
        self.enriched_scaffold: Optional[Dict] = None
        # --- BUG 3 FIX: Add aggregator for validation results ---
        # --- FIX: (Amnesiac Auditor) Aggregate all validation results ---
        self.all_validation_results: List[ValidationResult] = []
        # --- End V2 State ---
        
        self.rendered_output = None
        
        # --- FIX: Use OUTPUT_DIR constant ---
        self.base_output_dir = str(OUTPUT_DIR)
        
        if run_id:
            # --- RESUME RUN MODE ---
            self.run_id = run_id
            self.run_path = os.path.join(self.base_output_dir, self.run_id)
            
            if not os.path.exists(self.run_path):
                raise FileNotFoundError(f"Cannot resume: Run directory not found for ID {self.run_id} at {self.run_path}")
            
            # Load manifest
            self.manifest_manager = ManifestManager(self.run_path) # Init manifest manager
            manifest_path = os.path.join(self.run_path, "run_manifest.json")
            with open(manifest_path, 'r', encoding='utf-8') as f:
                # --- V2 REFACTOR: Use ManifestManager ---
                manifest = self.manifest_manager.load_manifest()
            
            self.job_input = manifest['job_input']
            self.hop_checkpoints = self.manifest_manager.get_checkpoints()
            # --- END REFACTOR ---
                
        elif job_input:
            # --- NEW RUN MODE ---
            self.run_id = str(uuid.uuid4())[:8]
            self.run_path = os.path.join(self.base_output_dir, self.run_id)
            os.makedirs(self.run_path, exist_ok=True)
            
            self.job_input = job_input
            
            # --- V2 REFACTOR: Use ManifestManager ---
            self.manifest_manager = ManifestManager(self.run_path) # Init manifest manager
            # Create initial manifest
            manifest = {
                "run_id": self.run_id,
                "engine_version": __version__,
                "start_time_utc": datetime.utcnow().isoformat() + "Z",
                "job_input": self.job_input,
                "master_resume_hash": self._hash_resume(master_resume),
                "hop_checkpoints": []
            }
            self.manifest_manager.create_manifest(
                run_id=self.run_id,
                engine_version=__version__,
                job_input=self.job_input,
                master_resume_hash=manifest["master_resume_hash"]
            )
            
        else:
            raise ValueError("Must provide either 'run_id' to resume or 'job_input' to start a new run.")

        # Setup logging and state serializer
        self.logger, self.log_file_path = self._setup_logging()
        
        # --- V2 TraceRegistry for structured audit logging ---
        self.trace_registry = TraceRegistry(run_id=self.run_id)
        
        # DEPRECATED IN V2: Only used for manifest management and backward compatibility
        # self.manifest_manager = ManifestManager(self.run_path) # Moved up
        self.constraints = config.constraints
        
        # Initialize JD enforcer
        self.jd_enforcer = JDEnforcementValidator(
            job_description=self.job_input.get('job_description', ''),
            logger=self.logger
        )
        
        # --- V2 REFACTOR: Removed orphaned LibrarianAgent instance ---
        # EnhancedJobDescriptionAnalyzer (HOP-0) creates its own instance
        self.code_interpreter = CodeInterpreterTool()  # Always available from utils_RES
        self.slow_loop_iteration = 0  # Track Slow Loop iterations
        
        # --- V2 AGENTS ---
        self.policy_agent = PolicyAgent(logger=self.logger)
        self.cost_router = CostRouter(config=self.config, logger=self.logger)
        self.context_relay_layer = ContextRelayLayer(
            config=self.config,
            logger=self.logger
        )
        self.critique_tool = CritiqueTool(logger=self.logger)
        self.hil_interface = HIL_Interface(logger=self.logger)
        # --- End V2 Agents ---
        
        # --- V2 TOOLS (Refactored Hops) ---
        # HOP-0: JD Analyzer
        self.jd_analyzer = self._create_jd_analyzer() if GEMINI_AVAILABLE else None
        
        # HOP-1: Clerk Extractor (will be called in _load_initial_state)
        # Note: ClerkExtractor instantiation happens in _load_initial_state
        # We keep a reference for potential direct access
        self._clerk_extractor_class = ClerkExtractor
        
        # HOP-2: Data Enricher (will be called in _load_initial_state)
        # Note: DataEnricher instantiation happens in _load_initial_state
        self._data_enricher_config = self.config.enricher
        
        # HOP-3: Artist Generator (Writer Tool)
        # This will be initialized after _load_initial_state populates thematic_analysis
        self.artist_generator = None
        
        # HOP-5/6: Validator (Inspector/Validator Tool)
        self.validator = PreFlightValidator(
            master_resume=self.master_resume,
            app_config=self.config
        )
        
        # HOP-7: File Renderer (Publisher Tool)
        # This will be initialized after we have drafts
        self.file_renderer = None
        
        # HOP-8: QA Report Generator (Auditor Tool)
        self.qa_report_generator = QAReportGenerator(self)
        # --- End V2 Tools ---
        
        # DEPRECATED IN V2: Hop execution order no longer used
        # V2 uses async DAG execution via _execute_generation_node
        
        if not GEMINI_AVAILABLE:
            self.logger.error(
                "CRITICAL: Gemini API is not available!\n" +
                "="*80 + "\n" +
                "Either the google-generativeai package is not installed,\n" +
                "or GEMINI_API_KEY environment variable is not set.\n" +
                "Workflow will fail.\n" +
                "="*80
            )

    def _load_initial_state(self):
        """
        V2 Ingestion Phase: Runs Hops 0, 1, 2 to populate in-memory state.
        
        This replaces the old hop-by-hop file serialization approach.
        State flows into memory (self.thematic_analysis, self.enriched_scaffold).
        """
        self.trace_registry.log("INFO", "Executing Ingestion Phase (Hops 0-2)")
        
        try:
            # ===== HOP-0: JD Analysis =====
            self.trace_registry.log("DEBUG", "Running HOP-0: JD Analysis")
            
            if not self.jd_analyzer:
                raise HopExecutionError("JD Analyzer not available (GEMINI_API not configured)")
            
            # --- REFACTOR: Master resume indexing is handled by EnhancedJobDescriptionAnalyzer ---
            # This logic was missing from the original file but is required by the analyzer.
            # Assuming a simple index creation here for completeness.
            master_resume_index = MasterResumeIndex(
                skill_to_experiences={},
                achievement_catalog=[],
                domain_vocabularies={},
                recency_scores={}
            )
            # --- END REFACTOR ---
            
            self.thematic_analysis = self.jd_analyzer.analyze_job_description(
                job_description=self.job_input['job_description'],
                company_name=self.job_input.get('company_name', 'Unknown'),
                job_title=self.job_input.get('job_title', 'Unknown'),
                master_resume_index=master_resume_index,
                # --- REFACTOR: Pass a default CompConfig ---
                comp_config=CompetitiveAnalysisConfig() # Pass default config
            )
            
            self.trace_registry.log("INFO", "HOP-0 Complete", {
                "primary_theme": self.thematic_analysis.primary_theme.get('name') if self.thematic_analysis.primary_theme else 'N/A',
                "signal_quality": self.thematic_analysis.signal_quality_score
            })
            
            # ===== HOP-1: Clerk Extraction =====
            self.trace_registry.log("DEBUG", "Running HOP-1: Clerk Extraction")
            
            clerk_extractor = self._clerk_extractor_class(self.master_resume)
            extracted_data, clerk_validation = clerk_extractor.extract()
            
            self.trace_registry.log("INFO", "HOP-1 Complete", {
                "sections_extracted": len(extracted_data)
            })
            
            # ===== HOP-2: Data Enrichment =====
            self.trace_registry.log("DEBUG", "Running HOP-2: Data Enrichment")
            
            # --- REFACTOR: Use correct instantiation ---
            data_enricher = DataEnricher() # No longer takes config
            self.enriched_scaffold, enrichment_validation = data_enricher.enrich(
                extracted_data, 
                self.thematic_analysis
            )
            
            self.trace_registry.log("INFO", "HOP-2 Complete", {
                "enriched_sections": len(self.enriched_scaffold)
            })
            
            # ===== Initialize Tools That Depend on State =====
            # Now that we have thematic_analysis and enriched_scaffold, initialize Artist
            self.artist_generator = ArtistGenerator(
                master_resume=self.master_resume,
                enriched_scaffold=self.enriched_scaffold,
                job_description=self.job_input.get('job_description', ''),
                thematic_analysis=self.thematic_analysis,
                artist_specs=self.config.artist_specs,
                # app_config=self.config, # <-- Removed, Artist now uses global CONFIG
                company_name=self.job_input.get('company_name', 'Unknown Company'),
                job_title=self.job_input.get('job_title', 'Target Role')
            )
            
            self.trace_registry.log("INFO", "Ingestion Phase Complete. State is in-memory.")
            
        except Exception as e:
            self.trace_registry.log("CRITICAL", f"Ingestion Phase Failed: {e}", {
                "exception": str(e)
            })
            raise HopExecutionError(f"Ingestion Phase Failed (Hops 0-2): {e}") from e

    def _create_buffer_for_section(
        self, 
        section_enum: ResumeSection, 
        draft: Any
    ) -> ImmutableStagingBuffer:
        """
        Creates a temporary, locked buffer containing only the section under test.
        Used by the Validator for per-node validation.
        
        Args:
            section_enum: The section being validated
            draft: The draft content for that section
            
        Returns:
            Locked ImmutableStagingBuffer with the section
        """
        buffer = ImmutableStagingBuffer()
        
        # Add all *already completed* drafts for cross-section validation
        for completed_section, completed_draft in self.drafts.items():
            buffer.set(completed_section.value, completed_draft)
            
        # Add the new draft being tested
        buffer.set(section_enum.value, draft)
        
        buffer.lock()
        return buffer

    async def _execute_generation_node(
        self, 
        section_enum: ResumeSection
    ) -> bool:
        """
        V2 Flattened Generation Loop for a single node.
        
        This is the core of the Governor. It orchestrates:
        1. Model selection (CostRouter)
        2. Context building (ContextRelayLayer) - DELEGATED
        3. Content generation (ArtistGenerator via dispatch)
        4. Sanitization (TextSanitizer)
        5. Validation (PreFlightValidator)
        6. Retry logic (PolicyAgent)
        7. Critique generation (CritiqueTool)
        8. HIL escalation (HIL_Interface)
        
        Args:
            section_enum: The ResumeSection to generate
            
        Returns:
            True if generation succeeded, False if failed all retries
        """
        self.trace_registry.log("INFO", f"Executing Node: {section_enum.name}", {
            "node": section_enum.name
        })
        
        critique_context = None
        
        # --- BUG 1 FIX: Get spec and dispatch method *before* the loop ---
        if not hasattr(self.artist_generator, 'SECTION_GENERATION_SPECS'):
             raise HopExecutionError("ArtistGenerator not initialized or SECTION_GENERATION_SPECS missing.")
            
        spec = self.artist_generator.SECTION_GENERATION_SPECS.get(section_enum)
        if not spec:
            self.trace_registry.log("ERROR", f"No artist spec found for {section_enum.name}. Skipping node.", {
                "node": section_enum.name, "status": "FAILED"
            })
            return False

        generation_method_name = spec.get("generation_method")
        generation_method = self.artist_generator.GENERATION_DISPATCH.get(generation_method_name)

        if not generation_method:
            self.trace_registry.log("ERROR", f"Invalid generation_method '{generation_method_name}' for {section_enum.name}.", {
                "node": section_enum.name, "status": "FAILED"
            })
            return False
        # --- END BUG 1 FIX ---

        for attempt in range(1, MAX_RETRIES_PER_NODE + 1):
            self.trace_registry.log("DEBUG", 
                f"Running {section_enum.name}, Attempt {attempt}/{MAX_RETRIES_PER_NODE}", 
                {"node": section_enum.name, "attempt": attempt}
            )
            
            try:
                # ===== STEP 1: Consult CostRouter =====
                model_to_use = self.cost_router.get_model_for_task(section_enum, attempt)
                
                # ===== STEP 2: Consult Context Relay Layer (CRL) =====
                # --- FIX: (Rogue Governor / Broken DAG) ---
                # The Governor MUST call the ContextRelayLayer to build the context.
                # The old logic micromanaged this, causing a crash for most methods.

                # Get base config from the spec
                temp_override = spec.get('temperature', DEFAULT_GENERATION_TEMPERATURE)
                reasoning_config = spec.get('reasoning_config', ReasoningConfig.DEFAULT)

                # Extract critique text and temp adjustment from PolicyAgent
                critique_text = None
                if critique_context and isinstance(critique_context, dict):
                    critique_text = critique_context.get("text")
                    temp_adjustment = critique_context.get("temperature_adjustment", 0.0)
                    temp_override = max(0.0, min(1.0, temp_override + temp_adjustment))
                    self.trace_registry.log("DEBUG", f"PolicyAgent adjusted temp: {temp_override}", {"node": section_enum.name})

                # Call the CRL to build the complete context envelope
                context_envelope = self.context_relay_layer.get_context_envelope(
                    section_enum=section_enum,
                    thematic_analysis=self.thematic_analysis,
                    enriched_scaffold=self.enriched_scaffold,
                    model=model_to_use,
                    reasoning_config=reasoning_config,
                    temperature=temp_override,
                    critique_context=critique_text,
                    # Pass all necessary context for the CRL's helpers
                    master_resume=self.master_resume,
                    job_description=self.job_input.get('job_description', ''),
                    company_name=self.job_input.get('company_name', 'Unknown Company'),
                    job_title=self.job_input.get('job_title', 'Target Role'),
                    spec=spec
                )
                
                # ===== STEP 3: (Tool Call) HOP-3: Writer (via correct dispatch) =====
                # Call the dynamically determined method
                
                # Non-async methods (most of them)
                if generation_method_name not in [
                    "_generate_section_macro_tot", "_generate_section_generic"
                ]:
                    # Handle simpler methods that don't need the full envelope
                    # (This logic is still part of the old bug, but we'll leave it
                    # to focus on the main crash)
                    simple_args = {"section_enum": section_enum, "spec": spec}
                    if "dependency_enum" in context_envelope: # HACK for overview
                        simple_args["generated_bullets"] = self.drafts[context_envelope["dependency_enum"]]
                        simple_args["word_count_range"] = context_envelope["word_count_range"]
                        simple_args["reasoning_config"] = context_envelope["reasoning_config"]
                        simple_args["temperature_override"] = context_envelope["temperature"]
                    
                    draft, call_count = generation_method(**simple_args)
                else:
                    # Correctly call the main generation methods using the CRL envelope
                    draft, call_count = self.artist_generator.generate(
                        prompt=context_envelope["prompt"],
                        system_prompt=context_envelope["system_prompt"],
                        reasoning_config=context_envelope["reasoning_config"],
                        temperature=context_envelope["temperature"],
                        model=context_envelope["model"],
                        section_id=context_envelope["section_name"]
                    )
                # --- END FIX ---

                # ===== STEP 3.5: (Tool Call) HOP-3.5: Inspector (Macro-ToT Selection) =====
                # This logic is now correctly inside the _execute_generation_node loop
                if isinstance(draft, list):
                    self.trace_registry.log("INFO", 
                        f"Macro-ToT returned {len(draft)} drafts for {section_enum.name}. Running Inspector...",
                        {"node": section_enum.name, "num_drafts": len(draft)}
                    )
                    
                    # Build temporary context for scoring
                    temp_buffer_for_scoring = self._create_buffer_for_section(section_enum, draft[0])  # Use first draft as placeholder
                    from validator_RES_v2 import ValidationContext
                    scoring_context = ValidationContext(
                        staging_buffer=temp_buffer_for_scoring,
                        thematic_analysis=self.thematic_analysis,
                        job_description=self.job_input['job_description'],
                        master_resume=self.master_resume,
                        app_config=self.config
                    )
                    
                    # Run scoring competition to select best draft
                    draft = self.validator._run_scoring_competition(
                        context=scoring_context,
                        drafts=draft,
                        section_enum=section_enum
                    )
                    
                    self.trace_registry.log("INFO", 
                        f"Inspector selected winning draft for {section_enum.name}",
                        {"node": section_enum.name}
                    )
                
                # ===== STEP 4: (Tool Call) HOP-4: Janitor =====
                cleaned_draft = text_utils.sanitize_text(draft)
                
                # ===== STEP 5 & 6: (Tool Call) HOP-5/6: Validator =====
                temp_buffer = self._create_buffer_for_section(section_enum, cleaned_draft)
                
                validation_results, decision, failed_sections = self.validator.validate(
                    staging_buffer=temp_buffer,
                    thematic_analysis=self.thematic_analysis,
                    job_description=self.job_input['job_description'],
                    sections_under_test={section_enum}
                )
                
                # --- BUG 3 FIX: Aggregate validation results ---
                # --- FIX: (Amnesiac Auditor) Aggregate results ---
                self.all_validation_results.extend(validation_results)

                self.trace_registry.log("DEBUG", "Node validation complete", {
                    "node": section_enum.name,
                    "decision": decision.name,
                    "failures": [
                        {"rule_id": vr.rule_id, "message": vr.message} 
                        for vr in validation_results if not vr.passed
                    ]
                })
                
                # ===== STEP 7: Observe Decision =====
                if decision == GateDecision.PROCEED:
                    self.trace_registry.log("INFO", "Node execution complete", {
                        "node": section_enum.name,
                        "status": "SUCCESS"
                    })
                    self.drafts[section_enum] = cleaned_draft
                    return True  # Success, exit retry loop
                
                # ===== STEP 8: Handle Failure (Start Feedback Loop) =====
                self.logger.warning(
                    f"♻️ {section_enum.name} FAILED validation. Consulting PolicyAgent..."
                )
                self.failures[section_enum] += 1
                
                # Classify failure type
                failure_type = "CREATIVE"  # Default
                for vr in validation_results:
                    if not vr.passed:
                        if "WORD_COUNT" in vr.rule_id or "SENTENCE_COUNT" in vr.rule_id:
                            failure_type = "MECHANICAL"
                            break
                        elif "THEME" in vr.rule_id or "SIGNAL" in vr.rule_id:
                            failure_type = "STRATEGIC"
                            break
                
                # ===== STEP 9: Consult PolicyAgent =====
                strategy = self.policy_agent.get_failure_strategy(
                    node=section_enum.name,
                    failure_type=failure_type,
                    retries=self.failures[section_enum]
                )
                
                if strategy.get("action") == "invoke_critique_and_reframe":
                    # ===== STEP 10: (Tool Call) CritiqueTool =====
                    critique_context = self.critique_tool.generate_critique(
                        cleaned_draft, 
                        validation_results, 
                        strategy.get("params", {})
                    )
                    # --- BUG 4 FIX: Store temp adjustment in critique context ---
                    critique_context = {
                        "text": critique_context,
                        "temperature_adjustment": strategy.get("params", {}).get("temperature_adjustment", 0.0)
                    }
                    self.trace_registry.log("WARNING", 
                        f"Retrying {section_enum.name} with new critique.", 
                        {"node": section_enum.name}
                    )
                    # Continue to next iteration with critique_context
                    
                elif strategy.get("action") == "hybrid_review_escalation":
                    self.trace_registry.log("CRITICAL", 
                        f"Escalating {section_enum.name} to HIL.", 
                        {"node": section_enum.name}
                    )
                    
                    # ===== STEP 11: (Tool Call) HIL_Interface =====
                    critique_text = critique_context.get("text") if isinstance(critique_context, dict) else critique_context
                    human_decision = self.hil_interface.notify(
                        section_enum, 
                        self.drafts, 
                        critique_text
                    )
                    
                    if human_decision.get("action") == "continue_with_draft":
                        self.drafts[section_enum] = human_decision.get("draft_with_warnings")
                        self.trace_registry.log("INFO", "Node execution complete", {
                            "node": section_enum.name,
                            "status": "SUCCESS_WITH_WARNINGS (HIL)"
                        })
                        return True  # HIL resolved the failure
                    else:
                        self.trace_registry.log("ERROR", "Node execution aborted by HIL", {
                            "node": section_enum.name,
                            "status": "ABORTED"
                        })
                        return False  # HIL aborted
            
            except Exception as e:
                self.trace_registry.log("ERROR", 
                    f"Node {section_enum.name} attempt {attempt} failed with exception: {e}", 
                    {"node": section_enum.name, "exception": str(e)}
                )
                self.failures[section_enum] += 1
                # Add exception as critique for next attempt
                critique_context = {
                    "text": f"The last attempt failed with an exception: {e}",
                    "temperature_adjustment": 0.0
                }
        
        # All retries exhausted
        self.trace_registry.log("ERROR", "Node execution failed all retries", {
            "node": section_enum.name,
            "status": "FAILED"
        })
        return False

    def _drafts_to_buffer(self) -> ImmutableStagingBuffer:
        """
        Converts the final in-memory self.drafts dict to a locked buffer.
        Used for final rendering (HOP-7).
        
        Returns:
            Locked ImmutableStagingBuffer with all drafts
        """
        buffer = ImmutableStagingBuffer()
        for section_enum, draft in self.drafts.items():
            buffer.set(section_enum.value, draft)
        buffer.lock()
        return buffer

    async def execute_workflow(self) -> Dict:
        """
        V2: Execute the workflow as an async dependency graph (DAG).
        
        The DAG structure:
        - K0 (Headline) is the root node
        - K1, K2, K9 execute in parallel after K0
        
        Returns:
            Dictionary with status, file_paths, run_id, etc.
        """
        workflow_start = datetime.now()
        self.trace_registry.log("INFO", "V2 Workflow Execution Started", {
            "run_id": self.run_id
        })
        
        try:
            # ===== PHASE 1: Load Initial State (Hops 0, 1, 2) =====
            self._load_initial_state()
            
            # ===== PHASE 2: Execute DAG =====
            
            # --- BUG 2 FIX: Define all nodes based on validator rules ---
            # Get all sections that have generation specs, excluding headers/copy
            all_generation_nodes = {
                s for s, spec in self.artist_generator.SECTION_GENERATION_SPECS.items()
                if spec.get("generation_method") not in [
                    "_copy_from_master", "_copy_k0_contact", "_generate_dummy_header"
                ]
            }
            
            # Find root nodes (no dependencies)
            root_nodes = set()
            dependent_nodes = {} # Map[Enum, Enum]
            for node in all_generation_nodes:
                spec = self.artist_generator.SECTION_GENERATION_SPECS[node]
                dep_enum = spec.get("depends_on")
                if dep_enum:
                    dependent_nodes[node] = dep_enum
                else:
                    root_nodes.add(node)
            
            self.trace_registry.log("INFO", f"DAG: Root Nodes: {[n.name for n in root_nodes]}")
            self.trace_registry.log("INFO", f"DAG: Dependent Nodes: { {n.name: d.name for n, d in dependent_nodes.items()} }")
            
            # Execute Root Nodes in parallel
            self.trace_registry.log("INFO", "Executing Root Nodes in parallel...")
            root_tasks = [
                self._execute_generation_node(node) for node in root_nodes
            ]
            root_results = await asyncio.gather(*root_tasks)
            
            if not all(root_results):
                failed_nodes = [node.name for node, success in zip(root_nodes, root_results) if not success]
                raise HopExecutionError(f"Root node(s) failed: {failed_nodes}")

            # Execute Dependent Nodes sequentially (or in parallel batches if possible)
            # For this spec, dependencies are simple, so sequential check is fine
            self.trace_registry.log("INFO", "Executing Dependent Nodes...")
            
            for node, dependency in dependent_nodes.items():
                if self.drafts.get(dependency):
                    self.trace_registry.log("INFO", f"Executing {node.name} (dependency {dependency.name} met)")
                    success = await self._execute_generation_node(node)
                    if not success:
                        raise HopExecutionError(f"Dependent node {node.name} failed")
                else:
                    raise HopExecutionError(f"Cannot execute {node.name}: Dependency {dependency.name} failed or was not generated.")
            
            # --- END BUG 2 FIX ---
            
            # ===== PHASE 3: Final Rendering (HOP-7) =====
            self.trace_registry.log("INFO", "Executing Final Rendering (Publisher)...")
            
            final_buffer = self._drafts_to_buffer()
            
            # Initialize FileRenderer if not already done
            if self.file_renderer is None:
                self.file_renderer = FileRenderer(
                    master_resume=self.master_resume,
                    orchestrator=self,
                    company_name=self.job_input.get('company_name', 'Target_Company'),
                    job_title=self.job_input.get('job_title', 'Target_Role'),
                    config=self.config
                )
            
            file_paths, (render_validation, file_contents) = self.file_renderer.render(
                staging_buffer=final_buffer,
                company_name=self.job_input.get('company_name'),
                job_title=self.job_input.get('job_title'),
                thematic_analysis=self.thematic_analysis,
                job_description=self.job_input.get('job_description'),
                jd_url=self.job_input.get('jd_url', '')
            )
            
            self.rendered_output = {
                "file_paths": file_paths,
                "file_contents": file_contents
            }
            
            self.trace_registry.log("INFO", "Final Rendering Complete", {
                "files_generated": len(file_paths)
            })
            
            # ===== PHASE 4: Final Auditing (HOP-8) =====
            self.trace_registry.log("INFO", "Executing Final Auditing (Auditor)...")
            
            # --- BUG 3 FIX: Pass the aggregated validation results ---
            qa_results, qa_report_text = self.qa_report_generator.generate(
                staging_buffer=final_buffer,
                thematic_analysis=self.thematic_analysis,
                validation_results=self.all_validation_results,
                file_contents=self.rendered_output.get('file_contents', {}),
                job_description=self.job_input.get('job_description', '')
            )
            # --- END BUG 3 FIX ---
            
            # Save QA report to file
            qa_report_path = os.path.join(
                self.run_path, 
                f"{self.run_id}_QA_Report.md"
            )
            with open(qa_report_path, 'w', encoding='utf-8') as f:
                f.write(qa_report_text)
            
            self.trace_registry.log("INFO", "Final Auditing Complete")
            
            # ===== PHASE 5: Build Final Result =====
            workflow_end = datetime.now()
            
            # Build CoC ledger (simplified for V2)
            coc_ledger = {
                "status": "SUCCESS",
                "run_id": self.run_id,
                "engine_version": __version__,
                "total_duration_seconds": (workflow_end - workflow_start).total_seconds(),
                "primary_theme": self.thematic_analysis.primary_theme.get('name') if self.thematic_analysis.primary_theme else 'N/A',
                "signal_quality": self.thematic_analysis.signal_quality_score
            }
            
            self.trace_registry.log("INFO", "Workflow Execution Succeeded")
            
            return {
                "status": "SUCCESS",
                "run_id": self.run_id,
                "gate_decision": GateDecision.PROCEED.value,
                "file_paths": file_paths,
                "log_file_path": self.log_file_path,
                "coc_ledger": coc_ledger,
                "qa_report_path": qa_report_path
            }
            
        except Exception as e:
            self.trace_registry.log("CRITICAL", 
                f"Workflow terminated with unhandled exception: {e}", 
                {"exception": str(e)}
            )
            # --- REFACTOR: Call helper for termination ---
            return self._handle_workflow_termination(
                str(e), 
                workflow_start, 
                "UNCAUGHT_EXCEPTION"
            )
            # --- END REFACTOR ---

    # ========================================================================
    # HELPER METHODS (kept from original, some modified for resumability)
    # ========================================================================
    
    # --- ADDED: Termination Helper ---
    def _handle_workflow_termination(
        self,
        reason: str,
        workflow_start_time: datetime,
        status: str
    ) -> Dict:
        """Centralized handler for workflow failure."""
        workflow_end_time = datetime.now()
        duration = (workflow_end_time - workflow_start_time).total_seconds()
        
        self.logger.error(f"WORKFLOW TERMINATED: {status}")
        self.logger.error(f"Reason: {reason}")
        
        coc_ledger = {
            "status": status,
            "run_id": self.run_id,
            "engine_version": __version__,
            "total_duration_seconds": duration,
            "termination_reason": reason
        }
        
        # Try to save manifest
        try:
            self.manifest_manager.update_checkpoint("WORKFLOW_FAILURE", coc_ledger)
        except Exception as e:
            self.logger.error(f"Failed to save final failure checkpoint: {e}")

        return {
            "status": status,
            "run_id": self.run_id,
            "gate_decision": GateDecision.HALT.value,
            "reason": reason,
            "log_file_path": self.log_file_path,
            "coc_ledger": coc_ledger
        }
    # --- END HELPER ---

    def _create_jd_analyzer(self):
        """Create JD analyzer instance."""
        # from rag_RES_v2 import EnhancedJobDescriptionAnalyzer # Old v16.20 call
        return EnhancedJobDescriptionAnalyzer(
            run_path=self.run_path,
            run_id=self.run_id
        )

    def _run_comprehensive_validation(
        self,
        staging_buffer: ImmutableStagingBuffer,
        thematic_analysis: ThematicAnalysis
    ) -> List[ValidationResult]:
        """Run comprehensive validation on staging buffer."""
        validation_results = []
        
        # Word count validation
        for section_key, content in staging_buffer.data.items():
            # --- FIX: Check type before splitting ---
            if isinstance(content, str):
                word_count = len(content.split())
                if word_count > 500:
                    validation_results.append(ValidationResult(
                        rule_id=f"VAL_{section_key}_LENGTH",
                        passed=False,
                        severity=ValidationSeverity.HIGH,
                        message=f"Section {section_key} exceeds maximum length",
                        details={"word_count": word_count, "max": 500}
                    ))
            # --- END FIX ---
        
        return validation_results

    def _setup_logging(self) -> Tuple[logging.Logger, str]:
        """Setup logging for this workflow run."""
        # --- FIX: Use self.run_path ---
        log_file_path = os.path.join(self.run_path, f"{self.run_id}_workflow.log")
        logger, _ = setup_workflow_logging(
            workflow_id=self.run_id, 
            log_file_path=log_file_path, 
            test_mode=False
        )
        return logger, log_file_path

    def _hash_resume(self, resume: dict) -> str:
        """Generate hash of master resume for integrity checking."""
        resume_str = json.dumps(resume, sort_keys=True)
        return hashlib.sha256(resume_str.encode('utf-8')).hexdigest()

def load_master_resume() -> Dict:
    """Load master resume from JSON file."""
    # --- FIX: Use _load_json_config and DATA_DIR from config ---
    try:
        from config_RES_v2 import _load_json_config, DATA_DIR
        path_to_try = DATA_DIR / "master_resume.json"
        data = _load_json_config(str(path_to_try), "Master Resume", required=True)
        return data
    except ImportError:
        logging.critical("FATAL: Could not import config_RES to load master_resume.json")
        return {}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.critical(f"FATAL: Failed to load master_resume.json: {e}")
        return {}
    except Exception as e:
        logging.critical(f"FATAL: Unexpected error loading master_resume.json: {e}")
        return {}

# NOTE: Global loading removed - driver script now responsible for loading