# File: workflow_RES_v3_8.py
# Resume Generation Workflow - V3.8 Architecture
# Version: 3.8.0 (Complete Migration)

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

# V3.8 Agent imports (Governor Module)
from governor_v3_8 import (
    PolicyAgent, CostRouter, ContextRelayLayer, 
    CritiqueTool, HIL_Interface, TraceRegistry,
    MAX_RETRIES_PER_NODE, DEFAULT_MODEL
)

# V3.8 Modular Tool imports
from clerk_RES_v3_8 import ClerkExtractor
from enricher_RES_v3_8 import DataEnricher
from artist_RES_v3_8 import ArtistGenerator
from renderer_RES_v3_8 import FileRenderer

# Import from modular components
from models_RES import (
    BulletProvenance, CircuitState, GateDecision, HopCheckpoint, HopStatus,
    ImmutableStagingBuffer, JDEnforcementResult, JDEnforcementRule,
    RAGState, RAGTelemetry, ResumeSection, ThematicAnalysis, FactualFailureException,
    ValidationResult, ValidationSeverity, HopExecutionError, StagingBufferError,
    CompetitiveIntelligence, RAGMission
)
from config_RES_v3_8 import (
    CONFIG, AppConfig, EnricherConfig, ContentConstraintsConfig,
    ReasoningConfig, DATA_DIR, OUTPUT_DIR, _load_json_config,
    COVER_LETTER_SIGNATURE_TEMPLATE, GEMINI_AVAILABLE, SKLEARN_AVAILABLE,
    DEFAULT_GENERATION_TEMPERATURE
)
from utils_RES_v3_8 import (
    text_utils, calculate_signal_score, setup_workflow_logging,
    create_directory_if_missing, sanitize_filename,
    WorkflowLogFilter, DuplicateDetector,
    reasoning_config_to_api_params, enhance_system_prompt_with_reasoning
)
from interpreter_RES_v3_8 import CodeInterpreterTool
from validator_RES_v3_8 import (
    PreFlightValidator, ConstraintFailureClassifier,
    JDEnforcementValidator, AppTrackerQAValidator
)
from qa_auditor_RES_v3_8 import QAReportGenerator
from rag_RES_v3_8 import EnhancedJobDescriptionAnalyzer
from state_manager_RES_v3_8 import ManifestManager

# Import ChromaDB if available
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("Warning: chromadb package not installed - RAG features may be limited")

# Constants
MAX_SLOW_LOOP_ITERATIONS = 3  # Maximum number of slow loop iterations before giving up

__version__ = "3.8.0"  # V3.8 Complete Migration

logger = logging.getLogger(__name__)


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
        
        # V3.8 In-Memory State
        self.drafts: Dict[ResumeSection, Any] = {}
        self.failures: Dict[ResumeSection, int] = defaultdict(int)
        self.thematic_analysis: Optional[ThematicAnalysis] = None
        self.enriched_scaffold: Optional[Dict] = None
        self.all_validation_results: List[ValidationResult] = []
        
        self.rendered_output = None
        
        # Use OUTPUT_DIR constant
        self.base_output_dir = str(OUTPUT_DIR)
        
        if run_id:
            # RESUME RUN MODE
            self.run_id = run_id
            self.run_path = os.path.join(self.base_output_dir, self.run_id)
            
            if not os.path.exists(self.run_path):
                raise FileNotFoundError(f"Cannot resume: Run directory not found for ID {self.run_id} at {self.run_path}")
            
            # Load manifest
            self.manifest_manager = ManifestManager(self.run_path)
            manifest = self.manifest_manager.load_manifest()
            
            self.job_input = manifest['job_input']
            self.hop_checkpoints = self.manifest_manager.get_checkpoints()
                
        elif job_input:
            # NEW RUN MODE
            self.run_id = str(uuid.uuid4())[:8]
            self.run_path = os.path.join(self.base_output_dir, self.run_id)
            os.makedirs(self.run_path, exist_ok=True)
            
            self.job_input = job_input
            
            # Use ManifestManager
            self.manifest_manager = ManifestManager(self.run_path)
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
        
        # V3.8 TraceRegistry for structured audit logging
        self.trace_registry = TraceRegistry(run_id=self.run_id)
        
        self.constraints = config.constraints
        
        # Initialize JD enforcer
        self.jd_enforcer = JDEnforcementValidator(
            job_description=self.job_input.get('job_description', ''),
            logger=self.logger
        )
        
        self.code_interpreter = CodeInterpreterTool()  # Always available
        self.slow_loop_iteration = 0  # Track Slow Loop iterations
        
        # V3.8 AGENTS
        self.policy_agent = PolicyAgent(logger=self.logger)
        self.cost_router = CostRouter(config=config, logger=self.logger)
        self.crl = ContextRelayLayer(logger=self.logger)
        self.critique_tool = CritiqueTool(logger=self.logger)
        self.hil = HIL_Interface(trace_registry=self.trace_registry)
        
        # Initialize modules
        self.clerk = ClerkExtractor(master_resume=self.master_resume)
        self.enricher = DataEnricher()
        self.artist = None  # Lazy init
        self.file_renderer = None  # Lazy init
        self.qa_report_generator = QAReportGenerator()
        self.pre_flight_validator = PreFlightValidator()
        self.constraint_classifier = ConstraintFailureClassifier()

    def _get_hop_status(self, hop_name: str) -> Optional[HopStatus]:
        """Get status of a specific hop from checkpoints."""
        if not hasattr(self, 'hop_checkpoints'):
            self.hop_checkpoints = self.manifest_manager.get_checkpoints()
        
        for checkpoint in self.hop_checkpoints:
            if checkpoint.hop_name == hop_name:
                return checkpoint.status
        return None

    def _checkpoint_hop(self, hop_name: str, status: HopStatus, data: Dict):
        """Save hop checkpoint to manifest."""
        checkpoint = HopCheckpoint(
            hop_name=hop_name,
            status=status,
            timestamp=datetime.utcnow().isoformat() + "Z",
            data=data
        )
        
        self.manifest_manager.update_checkpoint(hop_name, data)
        
        # Update in-memory list
        if not hasattr(self, 'hop_checkpoints'):
            self.hop_checkpoints = []
        
        # Replace or append checkpoint
        for i, cp in enumerate(self.hop_checkpoints):
            if cp.hop_name == hop_name:
                self.hop_checkpoints[i] = checkpoint
                return
        self.hop_checkpoints.append(checkpoint)

    def _get_hop_data(self, hop_name: str) -> Optional[Dict]:
        """Retrieve saved data for a hop from checkpoints."""
        if not hasattr(self, 'hop_checkpoints'):
            self.hop_checkpoints = self.manifest_manager.get_checkpoints()
        
        for checkpoint in self.hop_checkpoints:
            if checkpoint.hop_name == hop_name:
                return checkpoint.data
        return None

    def _hop_needs_execution(self, hop_name: str) -> bool:
        """Check if a hop needs to be executed."""
        status = self._get_hop_status(hop_name)
        return status != HopStatus.COMPLETED

    async def execute(self) -> Dict:
        """
        Execute the complete workflow with resumability support.
        Returns execution result dictionary.
        """
        try:
            workflow_start = datetime.now()
            self.trace_registry.log("INFO", f"Starting workflow execution for run_id: {self.run_id}")
            
            # PHASE 1: JD Analysis (HOP-0)
            if self._hop_needs_execution("HOP-0_JD_Analysis"):
                self.trace_registry.log("INFO", "Executing JD Analysis (HOP-0)...")
                
                jd_analyzer = self._create_jd_analyzer()
                thematic_analysis = await jd_analyzer.analyze(
                    job_description=self.job_input.get('job_description', ''),
                    company_name=self.job_input.get('company_name', 'Unknown'),
                    job_title=self.job_input.get('job_title', 'Unknown'),
                    master_resume=self.master_resume
                )
                
                self.thematic_analysis = thematic_analysis
                
                # Save checkpoint
                self._checkpoint_hop("HOP-0_JD_Analysis", HopStatus.COMPLETED, {
                    "primary_theme": thematic_analysis.primary_theme if thematic_analysis.primary_theme else None,
                    "secondary_themes": thematic_analysis.secondary_themes,
                    "signal_quality_score": thematic_analysis.signal_quality_score
                })
                
                self.trace_registry.log("SUCCESS", "JD Analysis Complete", {
                    "signal_quality": thematic_analysis.signal_quality_score
                })
            else:
                # Load from checkpoint
                hop_data = self._get_hop_data("HOP-0_JD_Analysis")
                self.thematic_analysis = ThematicAnalysis(
                    primary_theme=hop_data.get('primary_theme'),
                    secondary_themes=hop_data.get('secondary_themes', []),
                    signal_quality_score=hop_data.get('signal_quality_score', 0.0)
                )
                self.trace_registry.log("INFO", "Skipping HOP-0 (already completed)")
            
            # GATE-1: Signal Quality Check
            signal_score = self.thematic_analysis.signal_quality_score
            
            if signal_score < self.config.constraints.minimum_signal_score:
                self.trace_registry.log("WARNING", 
                    f"Signal quality {signal_score:.2f} below threshold {self.config.constraints.minimum_signal_score}")
                
                gate_decision = self.policy_agent.evaluate_gate(
                    gate_name="GATE-1_Signal_Quality",
                    metrics={"signal_score": signal_score},
                    threshold=self.config.constraints.minimum_signal_score
                )
                
                if gate_decision == GateDecision.HALT:
                    return self._handle_workflow_termination(
                        "Signal quality too low",
                        workflow_start,
                        "LOW_SIGNAL_QUALITY"
                    )
            
            # PHASE 2: Pre-Flight Validation
            if self._hop_needs_execution("HOP-1_PreFlight"):
                self.trace_registry.log("INFO", "Executing Pre-Flight Validation...")
                
                pre_flight_results = self.pre_flight_validator.validate(
                    master_resume=self.master_resume,
                    job_input=self.job_input,
                    config=self.config
                )
                
                if not pre_flight_results['is_valid']:
                    return self._handle_workflow_termination(
                        f"Pre-flight validation failed: {pre_flight_results['errors']}",
                        workflow_start,
                        "PREFLIGHT_FAILURE"
                    )
                
                self._checkpoint_hop("HOP-1_PreFlight", HopStatus.COMPLETED, pre_flight_results)
            
            # PHASE 3: Content Generation
            self.trace_registry.log("INFO", "Starting Content Generation Phase...")
            
            # Create enriched scaffold
            if self._hop_needs_execution("HOP-2_Enrichment"):
                enriched_scaffold = self.enricher.enrich(
                    extracted_data=self.clerk.extract(self.job_input),
                    thematic_analysis=self.thematic_analysis,
                    master_resume=self.master_resume
                )
                self.enriched_scaffold = enriched_scaffold
                self._checkpoint_hop("HOP-2_Enrichment", HopStatus.COMPLETED, enriched_scaffold)
            else:
                self.enriched_scaffold = self._get_hop_data("HOP-2_Enrichment")
            
            # Generate resume content
            if self._hop_needs_execution("HOP-3_Generation"):
                if self.artist is None:
                    self.artist = ArtistGenerator(
                        config=self.config,
                        master_resume=self.master_resume,
                        job_input=self.job_input,
                        run_path=self.run_path
                    )
                
                staging_buffer = await self.artist.generate(
                    enriched_scaffold=self.enriched_scaffold,
                    thematic_analysis=self.thematic_analysis
                )
                
                self._checkpoint_hop("HOP-3_Generation", HopStatus.COMPLETED, 
                                   staging_buffer.to_dict())
            else:
                buffer_data = self._get_hop_data("HOP-3_Generation")
                staging_buffer = ImmutableStagingBuffer(buffer_data)
            
            # Validation Phase
            validation_results = []
            
            # Run JD enforcement
            if self._hop_needs_execution("HOP-4_JD_Enforcement"):
                jd_results = self.jd_enforcer.validate_staging_buffer(staging_buffer)
                validation_results.extend(jd_results)
                self.all_validation_results.extend(jd_results)
                
                critical_failures = [r for r in jd_results if r.severity == ValidationSeverity.CRITICAL]
                if critical_failures:
                    self.slow_loop_iteration += 1
                    if self.slow_loop_iteration >= MAX_SLOW_LOOP_ITERATIONS:
                        return self._handle_workflow_termination(
                            f"Max slow loop iterations reached: {critical_failures}",
                            workflow_start,
                            "MAX_ITERATIONS_EXCEEDED"
                        )
                    
                    # Request HIL intervention
                    hil_result = await self.hil.request_human_intervention(
                        issue_type="CRITICAL_VALIDATION_FAILURE",
                        context={"failures": critical_failures},
                        staging_buffer=staging_buffer
                    )
                    
                    if hil_result.get('action') == 'ABORT':
                        return self._handle_workflow_termination(
                            "Human-in-loop requested abort",
                            workflow_start,
                            "HIL_ABORT"
                        )
                
                self._checkpoint_hop("HOP-4_JD_Enforcement", HopStatus.COMPLETED, 
                                   {"results": [asdict(r) if is_dataclass(r) else r for r in jd_results]})
            
            # Final buffer for rendering
            final_buffer = staging_buffer
            
            # PHASE 4: File Rendering
            if self._hop_needs_execution("HOP-5_Rendering"):
                self.trace_registry.log("INFO", "Executing File Rendering...")
                
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
                
                self._checkpoint_hop("HOP-5_Rendering", HopStatus.COMPLETED, self.rendered_output)
                
                self.trace_registry.log("INFO", "Final Rendering Complete", {
                    "files_generated": len(file_paths)
                })
            else:
                self.rendered_output = self._get_hop_data("HOP-5_Rendering")
                file_paths = self.rendered_output.get("file_paths", [])
            
            # PHASE 5: Final Auditing
            if self._hop_needs_execution("HOP-6_Auditing"):
                self.trace_registry.log("INFO", "Executing Final Auditing...")
                
                qa_results, qa_report_text = self.qa_report_generator.generate(
                    staging_buffer=final_buffer,
                    thematic_analysis=self.thematic_analysis,
                    validation_results=self.all_validation_results,
                    file_contents=self.rendered_output.get('file_contents', {}),
                    job_description=self.job_input.get('job_description', '')
                )
                
                # Save QA report to file
                qa_report_path = os.path.join(
                    self.run_path, 
                    f"{self.run_id}_QA_Report.md"
                )
                with open(qa_report_path, 'w', encoding='utf-8') as f:
                    f.write(qa_report_text)
                
                self._checkpoint_hop("HOP-6_Auditing", HopStatus.COMPLETED, {
                    "qa_report_path": qa_report_path,
                    "qa_results": qa_results
                })
                
                self.trace_registry.log("INFO", "Final Auditing Complete")
            else:
                audit_data = self._get_hop_data("HOP-6_Auditing")
                qa_report_path = audit_data.get("qa_report_path")
            
            # Build Final Result
            workflow_end = datetime.now()
            
            # Build CoC ledger
            coc_ledger = {
                "status": "SUCCESS",
                "run_id": self.run_id,
                "engine_version": __version__,
                "total_duration_seconds": (workflow_end - workflow_start).total_seconds(),
                "primary_theme": self.thematic_analysis.primary_theme.get('name') if self.thematic_analysis and self.thematic_analysis.primary_theme else 'N/A',
                "signal_quality": self.thematic_analysis.signal_quality_score if self.thematic_analysis else 0.0
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
            return self._handle_workflow_termination(
                str(e), 
                workflow_start, 
                "UNCAUGHT_EXCEPTION"
            )

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

    def _create_jd_analyzer(self):
        """Create JD analyzer instance."""
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
        
        return validation_results

    def _setup_logging(self) -> Tuple[logging.Logger, str]:
        """Setup logging for this workflow run."""
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
    try:
        from config_RES_v3_8 import _load_json_config, DATA_DIR
        path_to_try = DATA_DIR / "master_resume.json"
        data = _load_json_config(str(path_to_try), "Master Resume", required=True)
        return data
    except ImportError:
        logging.critical("FATAL: Could not import config_RES_v3_8 to load master_resume.json")
        return {}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.critical(f"FATAL: Failed to load master_resume.json: {e}")
        return {}
    except Exception as e:
        logging.critical(f"FATAL: Unexpected error loading master_resume.json: {e}")
        return {}
