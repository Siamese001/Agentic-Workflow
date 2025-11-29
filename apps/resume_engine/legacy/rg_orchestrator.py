"""RG Orchestrator - Resume Generation L3 Orchestration Layer

Incorporated from historical agentic_workflow/l3/rg_orchestrator.py to coordinate
the complete 8-node resume generation pipeline with L1 planning and L3 orchestration.

This orchestrator coordinates:
L1 Planning (RGPlanner) → K1 Extract → K2 Clean → K3 Quantify → K4 Rewrite → K5 Skillmap → K6 Assemble → K7 Format → K8 Validate
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Import L1 planner
from .rg_planner import RGPlanner, ResumeProcessingPlan

# Import K-node executors - Now from agentic_core
from agentic_core.l2_execution.draft_execution.rg_k1_extract import RGK1Extract, ExtractionOutput
from agentic_core.l2_execution.draft_execution.rg_k2_clean import RGK2Clean, CleaningOutput
from agentic_core.l2_execution.draft_execution.rg_k3_quantify import RGK3Quantify, QuantificationOutput
from agentic_core.l2_execution.draft_execution.rg_k4_rewrite import RGK4Rewrite, RewritingOutput
from agentic_core.l2_execution.draft_execution.rg_k5_skillmap import RGK5Skillmap, SkillMappingOutput
from agentic_core.l2_execution.draft_execution.rg_k6_assemble import RGK6Assemble, AssemblyOutput
from agentic_core.l2_execution.draft_execution.rg_k7_format import RGK7Format, FormattingOutput
from agentic_core.l2_execution.draft_execution.rg_k8_validate import RGK8Validate, ValidationOutput

# Import LOW complexity utilities
from ..utils.rg_low_complexity_utils import LowComplexityUtils

logger = logging.getLogger(__name__)


@dataclass
class ResumeGenerationRequest:
    """Resume generation request with all inputs."""
    job_input: Dict[str, Any]
    resume_input: Dict[str, Any]
    processing_options: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResumeGenerationResult:
    """Complete resume generation result."""
    success: bool
    final_resume_content: str
    processing_plan: ResumeProcessingPlan
    k_node_outputs: Dict[str, Any]
    validation_result: Any
    processing_metrics: Dict[str, Any]
    error_message: str
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class OrchestratorMetrics:
    """Metrics from orchestrator execution."""
    total_processing_time_ms: int
    k_node_execution_times: Dict[str, int]
    planning_time_ms: int
    validation_time_ms: int
    pipeline_success_rate: float
    error_recovery_count: int


class RGOrchestrator:
    """Resume Generation Orchestrator - L3 orchestration layer.
    
    Coordinates the complete 8-node resume generation pipeline:
    - L1 planning with RGPlanner
    - Sequential K-node execution (K1-K8)
    - Error handling and recovery
    - Performance monitoring and telemetry
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize resume generation orchestrator."""
        self.config = config or {}
        self.telemetry_bus = telemetry_bus
        
        # Initialize L1 planner
        self.rg_planner = RGPlanner(
            config=self.config.get("planner_config", {}),
            telemetry_bus=self.telemetry_bus
        )
        
        # Initialize K-node executors
        self.k1_extract = RGK1Extract(
            extraction_plan=self.config.get("k1_config", {}),
            telemetry_bus=self.telemetry_bus
        )
        self.k2_clean = RGK2Clean(
            cleaning_plan=self.config.get("k2_config", {}),
            telemetry_bus=self.telemetry_bus
        )
        self.k3_quantify = RGK3Quantify(
            quantification_plan=self.config.get("k3_config", {}),
            telemetry_bus=self.telemetry_bus
        )
        self.k4_rewrite = RGK4Rewrite(
            rewriting_plan=self.config.get("k4_config", {}),
            telemetry_bus=self.telemetry_bus
        )
        self.k5_skillmap = RGK5Skillmap(
            mapping_plan=self.config.get("k5_config", {}),
            telemetry_bus=self.telemetry_bus
        )
        self.k6_assemble = RGK6Assemble(
            assembly_plan=self.config.get("k6_config", {}),
            telemetry_bus=self.telemetry_bus
        )
        self.k7_format = RGK7Format(
            formatting_plan=self.config.get("k7_config", {}),
            telemetry_bus=self.telemetry_bus
        )
        self.k8_validate = RGK8Validate(
            validation_plan=self.config.get("k8_config", {}),
            telemetry_bus=self.telemetry_bus
        )
        
        # Initialize LOW complexity utilities
        self.low_complexity_utils = LowComplexityUtils()
        
        # Pipeline configuration
        self.pipeline_config = {
            "enable_error_recovery": self.config.get("enable_error_recovery", True),
            "max_retry_attempts": self.config.get("max_retry_attempts", 2),
            "strict_validation": self.config.get("strict_validation", False),
            "performance_monitoring": self.config.get("performance_monitoring", True),
            "enable_low_complexity": self.config.get("enable_low_complexity", True)
        }
    
    def generate_resume(
        self,
        *,
        request: ResumeGenerationRequest
    ) -> ResumeGenerationResult:
        """Execute complete resume generation pipeline.
        
        Args:
            request: Resume generation request with job and resume inputs
            
        Returns:
            Complete resume generation result with final content and metrics
        """
        execution_trace = []
        start_time = datetime.now()
        
        try:
            # 1. L1 Planning Phase
            logger.info("Starting L1 resume generation planning")
            planning_start = datetime.now()
            
            processing_plan = self.rg_planner.plan_resume_processing(
                job_input=request.job_input,
                resume_input=request.resume_input,
                processing_options=request.processing_options or {}
            )
            
            planning_time = (datetime.now() - planning_start).total_seconds() * 1000
            execution_trace.append({
                "phase": "L1_Planning",
                "status": "success",
                "planning_time_ms": planning_time,
                "analysis_depth": processing_plan.analysis_plan.analysis_depth,
                "timestamp": datetime.now().isoformat()
            })
            
            # 2. LOW Complexity Preprocessing (if enabled)
            if self.pipeline_config.get("enable_low_complexity", True):
                current_input = self._apply_low_complexity_preprocessing(request.resume_input, request, processing_plan, execution_trace)
            else:
                current_input = request.resume_input
            
            # 3. K-Node Sequential Execution
            k_node_outputs = {}
            k_node_times = {}
            
            # Define K-node execution sequence
            k_nodes = [
                ("k1_extract", self.k1_extract, self._execute_k1_extract),
                ("k2_clean", self.k2_clean, self._execute_k2_clean),
                ("k3_quantify", self.k3_quantify, self._execute_k3_quantify),
                ("k4_rewrite", self.k4_rewrite, self._execute_k4_rewrite),
                ("k5_skillmap", self.k5_skillmap, self._execute_k5_skillmap),
                ("k6_assemble", self.k6_assemble, self._execute_k6_assemble),
                ("k7_format", self.k7_format, self._execute_k7_format),
                ("k8_validate", self.k8_validate, self._execute_k8_validate)
            ]
            
            # Execute K-nodes sequentially
            for node_name, node_executor, executor_func in k_nodes:
                node_start = datetime.now()
                
                try:
                    logger.info(f"Executing {node_name}")
                    node_output = executor_func(current_input, processing_plan, request)
                    
                    node_time = (datetime.now() - node_start).total_seconds() * 1000
                    k_node_times[node_name] = int(node_time)
                    k_node_outputs[node_name] = node_output
                    
                    # Update current_input for next node
                    current_input = node_output
                    
                    execution_trace.append({
                        "phase": node_name,
                        "status": "success",
                        "execution_time_ms": node_time,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    logger.info(f"Completed {node_name} in {node_time:.2f}ms")
                    
                except Exception as e:
                    logger.error(f"Failed to execute {node_name}: {e}")
                    
                    if self.pipeline_config["enable_error_recovery"]:
                        # Attempt error recovery
                        recovery_output = self._attempt_error_recovery(node_name, e, current_input)
                        if recovery_output:
                            k_node_outputs[node_name] = recovery_output
                            current_input = recovery_output
                            execution_trace.append({
                                "phase": node_name,
                                "status": "recovered",
                                "error": str(e),
                                "timestamp": datetime.now().isoformat()
                            })
                        else:
                            # Recovery failed, abort pipeline
                            error_result = ResumeGenerationResult(
                                success=False,
                                final_resume_content="",
                                processing_plan=processing_plan,
                                k_node_outputs=k_node_outputs,
                                validation_result=None,
                                processing_metrics={},
                                error_message=f"Pipeline failed at {node_name}: {str(e)}",
                                execution_trace=execution_trace
                            )
                            return error_result
                    else:
                        # No error recovery, abort immediately
                        error_result = ResumeGenerationResult(
                            success=False,
                            final_resume_content="",
                            processing_plan=processing_plan,
                            k_node_outputs=k_node_outputs,
                            validation_result=None,
                            processing_metrics={},
                            error_message=f"Pipeline failed at {node_name}: {str(e)}",
                            execution_trace=execution_trace
                        )
                        return error_result
            
            # 3. Extract final results
            validation_output = k_node_outputs.get("k8_validate")
            
            if not validation_output or not validation_output.success or not hasattr(validation_output, 'validated_content') or not validation_output.validated_content.strip():
                # Extract final content from K7 format output (handle both dict and object)
                k7_output = k_node_outputs.get("k7_format")
                if k7_output:
                    if hasattr(k7_output, 'formatted_content'):
                        # K7 returned a FormattingOutput object
                        final_content = k7_output.formatted_content
                    elif isinstance(k7_output, dict):
                        # K7 returned a dict
                        final_content = k7_output.get("formatted_content", "")
                    else:
                        final_content = str(k7_output)
                else:
                    final_content = ""
            else:
                final_content = validation_output.validated_content
            
            # 4. Calculate processing metrics
            total_time = (datetime.now() - start_time).total_seconds() * 1000
            processing_metrics = self._calculate_processing_metrics(
                total_time, planning_time, k_node_times, k_node_outputs
            )
            
            # 5. Build final result
            result = ResumeGenerationResult(
                success=True,
                final_resume_content=final_content,
                processing_plan=processing_plan,
                k_node_outputs=k_node_outputs,
                validation_result=validation_output.validation_result if validation_output else None,
                processing_metrics=processing_metrics,
                error_message="",
                execution_trace=execution_trace
            )
            
            # 6. Record telemetry (best-effort)
            self._safe_record_telemetry(result)
            
            logger.info(f"Resume generation completed successfully in {total_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Resume generation pipeline failed: {e}")
            
            total_time = (datetime.now() - start_time).total_seconds() * 1000
            
            error_result = ResumeGenerationResult(
                success=False,
                final_resume_content="",
                processing_plan=None,
                k_node_outputs=k_node_outputs if 'k_node_outputs' in locals() else {},
                validation_result=None,
                processing_metrics={"total_processing_time_ms": int(total_time)},
                error_message=str(e),
                execution_trace=execution_trace + [{
                    "phase": "pipeline_error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }]
            )
            
            return error_result
    
    def _execute_k1_extract(self, input_data: Dict[str, Any], plan: ResumeProcessingPlan, request: ResumeGenerationRequest) -> ExtractionOutput:
        """Execute K1 extraction phase with HyDE expansion."""
        # Update extraction params with job requirements
        extraction_params = plan.extraction_params.copy()
        extraction_params.update({
            "hyde_expansion": True  # Enable HyDE expansion for MEDIUM complexity
        })
        
        return self.k1_extract.extract_resume_content(
            resume_input=input_data,
            extraction_params=extraction_params
        )
    
    def _execute_k2_clean(self, input_data: ExtractionOutput, plan: ResumeProcessingPlan, request: ResumeGenerationRequest) -> CleaningOutput:
        """Execute K2 cleaning phase."""
        return self.k2_clean.clean_resume_content(
            extraction_output=input_data,
            cleaning_params=plan.cleaning_params
        )
    
    def _execute_k3_quantify(self, input_data: CleaningOutput, plan: ResumeProcessingPlan, request: ResumeGenerationRequest) -> QuantificationOutput:
        """Execute K3 quantification phase with evidence ranking."""
        # Update quantification params with job requirements
        quantification_params = plan.quantification_params.copy()
        quantification_params.update({
            "evidence_ranking": True  # Enable evidence ranking for MEDIUM complexity
        })
        
        return self.k3_quantify.quantify_resume_content(
            cleaning_output=input_data,
            job_requirements=request.job_input,  # Pass job requirements for evidence ranking
            quantification_params=quantification_params
        )
    
    def _execute_k4_rewrite(self, input_data: QuantificationOutput, plan: ResumeProcessingPlan, request: ResumeGenerationRequest) -> RewritingOutput:
        """Execute K4 rewriting phase with goal-alignment."""
        # Update rewriting params with job requirements
        rewriting_params = plan.rewriting_params.copy()
        rewriting_params.update({
            "target_role": request.job_input.get("title", ""),
            "target_industry": request.job_input.get("industry", "general"),
            "goal_alignment": True  # Enable goal-alignment for MEDIUM complexity
        })
        
        return self.k4_rewrite.rewrite_resume_content(
            quantification_output=input_data,
            job_requirements=request.job_input,  # Pass job requirements for goal alignment
            rewriting_params=rewriting_params
        )
    
    def _execute_k5_skillmap(self, input_data: RewritingOutput, plan: ResumeProcessingPlan, request: ResumeGenerationRequest) -> SkillMappingOutput:
        """Execute K5 skill mapping phase."""
        return self.k5_skillmap.map_resume_skills(
            rewriting_output=input_data,
            job_requirements=request.job_input,
            mapping_params=plan.skill_mapping_params
        )
    
    def _execute_k6_assemble(self, input_data: SkillMappingOutput, plan: ResumeProcessingPlan, request: ResumeGenerationRequest) -> AssemblyOutput:
        """Execute K6 assembly phase."""
        return self.k6_assemble.assemble_resume_sections(
            skill_mapping_output=input_data,
            job_requirements=request.job_input,
            assembly_params=plan.assembly_params
        )
    
    def _execute_k7_format(self, input_data: AssemblyOutput, plan: ResumeProcessingPlan, request: ResumeGenerationRequest) -> FormattingOutput:
        """Execute K7 formatting phase."""
        # Update formatting params with job requirements
        formatting_params = plan.formatting_params.copy()
        formatting_params.update({
            "target_role": request.job_input.get("title", ""),
            "target_industry": request.job_input.get("industry", "general")
        })
        
        return self.k7_format.format_resume_content(
            assembly_output=input_data,
            formatting_params=formatting_params
        )
    
    def _execute_k8_validate(self, input_data: FormattingOutput, plan: ResumeProcessingPlan, request: ResumeGenerationRequest) -> ValidationOutput:
        """Execute K8 validation phase."""
        return self.k8_validate.validate_resume_content(
            formatting_output=input_data,
            job_requirements=request.job_input,
            validation_params=plan.validation_params
        )
    
    def _attempt_error_recovery(self, node_name: str, error: Exception, input_data: Any) -> Optional[Any]:
        """Attempt error recovery for a failed K-node."""
        logger.info(f"Attempting error recovery for {node_name}")
        
        try:
            # Simple recovery strategy: create a minimal valid output
            if node_name == "k1_extract":
                # Create minimal extraction output
                from .rg_k1_extract import ExtractionOutput, ExtractionMetrics
                return ExtractionOutput(
                    extracted_sections=[],
                    raw_content=str(input_data),
                    normalized_content=str(input_data),
                    metrics=ExtractionMetrics(0, 0, 0.0, 0, {}, 0.0),
                    extraction_plan={"recovery": True},
                    success=True,
                    error_message="",
                    processing_trace=[{"step": "recovery", "error": str(error)}]
                )
            
            elif node_name == "k2_clean":
                # Create minimal cleaning output
                from .rg_k2_clean import CleaningOutput, CleaningMetrics
                return CleaningOutput(
                    cleaned_sections=[],
                    cleaning_operations=[],
                    cleaned_content=str(input_data),
                    metrics=CleaningMetrics(0, 0, 0, 0, 0.0, 0.0, 0),
                    cleaning_plan={"recovery": True},
                    success=True,
                    error_message="",
                    processing_trace=[{"step": "recovery", "error": str(error)}]
                )
            
            # Add recovery for other nodes as needed
            return None
            
        except Exception as recovery_error:
            logger.error(f"Error recovery failed for {node_name}: {recovery_error}")
            return None
    
    def _calculate_processing_metrics(
        self, 
        total_time: float, 
        planning_time: float, 
        k_node_times: Dict[str, int], 
        k_node_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate comprehensive processing metrics."""
        # Calculate success rate
        successful_nodes = sum(1 for output in k_node_outputs.values() if hasattr(output, 'success') and output.success)
        total_nodes = len(k_node_outputs)
        success_rate = successful_nodes / total_nodes if total_nodes > 0 else 0.0
        
        # Calculate validation score
        validation_output = k_node_outputs.get("k8_validate")
        validation_score = 0.0
        if validation_output and hasattr(validation_output, 'validation_result'):
            validation_result = validation_output.validation_result
            if validation_result:
                validation_score = (validation_result.quality_score + 
                                  validation_result.compliance_score + 
                                  validation_result.content_score + 
                                  validation_result.format_score) / 4
        
        return {
            "total_processing_time_ms": int(total_time),
            "planning_time_ms": int(planning_time),
            "k_node_execution_times": k_node_times,
            "pipeline_success_rate": success_rate,
            "validation_score": validation_score,
            "nodes_executed": total_nodes,
            "nodes_successful": successful_nodes,
            "error_recovery_count": 0  # Would be incremented during actual recovery
        }
    
    def _safe_record_telemetry(self, result: ResumeGenerationResult) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("rg_orchestrator_executed", {
                    "success": result.success,
                    "total_processing_time_ms": result.processing_metrics.get("total_processing_time_ms", 0),
                    "pipeline_success_rate": result.processing_metrics.get("pipeline_success_rate", 0),
                    "validation_score": result.processing_metrics.get("validation_score", 0)
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_orchestrator_summary(self, result: ResumeGenerationResult) -> Dict[str, Any]:
        """Get a summary of the orchestrator execution for debugging/telemetry."""
        return {
            "execution_id": "rg_orchestrator",
            "success": result.success,
            "total_processing_time_ms": result.processing_metrics.get("total_processing_time_ms", 0),
            "pipeline_success_rate": result.processing_metrics.get("pipeline_success_rate", 0),
            "validation_score": result.processing_metrics.get("validation_score", 0),
            "nodes_executed": result.processing_metrics.get("nodes_executed", 0),
            "error_message": result.error_message
        }
    
    def create_sample_request(self) -> ResumeGenerationRequest:
        """Create a sample resume generation request for testing."""
        return ResumeGenerationRequest(
            job_input={
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "industry": "technology",
                "description": "Senior software engineering position with focus on cloud technologies",
                "requirements": ["Python", "AWS", "Docker", "5+ years experience"],
                "skills": ["python", "aws", "docker", "kubernetes", "microservices"],
                "experience_years": 5
            },
            resume_input={
                "content": """
                John Doe
                Email: john@example.com | Phone: 555-1234 | LinkedIn: linkedin.com/in/johndoe
                
                Professional Summary
                Experienced software engineer with expertise in cloud technologies and distributed systems.
                
                Experience
                Senior Software Engineer at Tech Corp (2020-Present)
                • Developed scalable microservices using Python and AWS
                • Led team of 5 engineers on cloud migration project
                • Improved system performance by 40%
                
                Software Engineer StartupXYZ (2018-2020)
                • Built REST APIs and web applications
                • Worked with Docker and Kubernetes
                • Reduced deployment time by 60%
                
                Education
                BS Computer Science, University (2014-2018)
                
                Skills
                Python, AWS, Docker, Kubernetes, Microservices, REST APIs
                """,
                "sections": {
                    "contact_info": "John Doe\nEmail: john@example.com | Phone: 555-1234 | LinkedIn: linkedin.com/in/johndoe",
                    "summary": "Experienced software engineer with expertise in cloud technologies and distributed systems.",
                    "experience": "Senior Software Engineer at Tech Corp (2020-Present)\n• Developed scalable microservices using Python and AWS\n• Led team of 5 engineers on cloud migration project\n• Improved system performance by 40%",
                    "education": "BS Computer Science, University (2014-2018)",
                    "skills": "Python, AWS, Docker, Kubernetes, Microservices, REST APIs"
                }
            },
            processing_options={
                "analysis_depth": "comprehensive",
                "validation_level": "comprehensive",
                "formatting_standards": "ats_optimized"
            }
        )
    
    def _apply_low_complexity_preprocessing(
        self, 
        resume_input: Dict[str, Any], 
        request: ResumeGenerationRequest,
        plan: ResumeProcessingPlan,
        execution_trace: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply LOW complexity preprocessing features to resume content."""
        preprocessing_start = datetime.now()
        
        try:
            # Prepare context for LOW complexity processing
            processing_options = request.processing_options or {}
            low_complexity_context = {
                "scrub_pii": processing_options.get("scrub_pii", True),
                "audit_bias": processing_options.get("audit_bias", True),
                "inject_goals": processing_options.get("inject_goals", True),
                "hyde_expand": processing_options.get("hyde_expand", True),
                "reflect_improve": processing_options.get("reflect_improve", True),
                "goal_state": {
                    "primary_goal": request.job_input.get("title", "professional excellence"),
                    "target_role": request.job_input.get("title", ""),
                    "industry": request.job_input.get("industry", "general")
                },
                "skills": request.job_input.get("skills", []),
                "experience": resume_input.get("content", "")
            }
            
            # Process content with LOW complexity utilities
            original_content = resume_input.get("content", "")
            processing_results = self.low_complexity_utils.process_content(original_content, low_complexity_context)
            
            # Update resume input with processed content
            processed_input = resume_input.copy()
            processed_input["content"] = processing_results["processed_content"]
            
            # Add LOW complexity metadata
            processed_input["low_complexity_results"] = {
                "pii_scrubbed": processing_results["pii_result"] is not None,
                "bias_audited": processing_results["bias_result"] is not None,
                "goal_injected": processing_results["goal_injected"],
                "hyde_expanded": processing_results["hyde_expanded"],
                "reflection_applied": processing_results["reflection_result"] is not None
            }
            
            # Record preprocessing in execution trace
            preprocessing_time = (datetime.now() - preprocessing_start).total_seconds() * 1000
            execution_trace.append({
                "phase": "LOW_Complexity_Preprocessing",
                "status": "success",
                "preprocessing_time_ms": preprocessing_time,
                "features_applied": sum([
                    processing_results["pii_result"] is not None,
                    processing_results["bias_result"] is not None,
                    processing_results["goal_injected"],
                    processing_results["hyde_expanded"],
                    processing_results["reflection_result"] is not None
                ]),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"LOW complexity preprocessing completed in {preprocessing_time:.2f}ms")
            return processed_input
            
        except Exception as e:
            logger.error(f"LOW complexity preprocessing failed: {e}")
            
            # Record error in execution trace
            preprocessing_time = (datetime.now() - preprocessing_start).total_seconds() * 1000
            execution_trace.append({
                "phase": "LOW_Complexity_Preprocessing",
                "status": "error",
                "preprocessing_time_ms": preprocessing_time,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            # Return original input if preprocessing fails
            return resume_input
