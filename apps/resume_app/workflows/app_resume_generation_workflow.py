"""
resume_app/workflows – app_resume_generation_workflow.py

Apps layer workflow for end-to-end resume generation.
Orchestrates adapters and validators to generate enhanced resumes with LIC compliance.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

# Import apps layer components
from apps.resume_app.adapters.app_resume_engine_adapter import (
    ResumeEngineAdapter, ResumeGenerationRequest, ResumeGenerationResponse
)
from apps.resume_app.adapters.app_resume_memory_adapter import (
    ResumeMemoryAdapter, MemoryQueryRequest
)
from apps.resume_app.validators.app_resume_input_validator import (
    ResumeInputValidator, ValidationResult
)
from apps.resume_app.validators.app_resume_schema_validator import (
    ResumeSchemaValidator, SchemaValidationResult
)


@dataclass
class WorkflowStep:
    """Workflow step definition with status tracking"""
    step_name: str
    status: str = "pending"  # "pending", "running", "completed", "failed"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Complete workflow execution result"""
    success: bool = False
    resume_response: Optional[ResumeGenerationResponse] = None
    validation_results: List[ValidationResult] = field(default_factory=list)
    schema_results: List[SchemaValidationResult] = field(default_factory=list)
    steps_completed: List[WorkflowStep] = field(default_factory=list)
    total_time_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResumeGenerationWorkflow:
    """Apps layer resume generation workflow

    Orchestrates the complete resume generation process:
    1. Input validation (LIC compliance)
    2. Schema validation
    3. Memory query for relevant bullets
    4. Resume enhancement via engine adapter
    5. Output validation and compliance checking
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.engine_adapter = ResumeEngineAdapter(config)
        self.memory_adapter = ResumeMemoryAdapter(config)
        self.input_validator = ResumeInputValidator(config)
        self.schema_validator = ResumeSchemaValidator(config)

        # Workflow configuration
        self.enable_memory_query = self.config.get("enable_memory_query", True)
        self.enable_output_validation = self.config.get("enable_output_validation", True)
        self.max_retry_attempts = self.config.get("max_retry_attempts", 2)

    def execute_resume_generation(self, request_data: Dict[str, Any]) -> WorkflowResult:
        """Execute complete resume generation workflow"""
        workflow_start = datetime.now()
        result = WorkflowResult()

        try:
            self.logger.info("Starting resume generation workflow")

            # Step 1: Input validation
            step1 = self._execute_input_validation(request_data, result)
            if not step1.status == "completed":
                return result

            # Step 2: Schema validation
            step2 = self._execute_schema_validation(request_data, result)
            if not step2.status == "completed":
                return result

            # Step 3: Memory query (optional)
            step3 = self._execute_memory_query(request_data, result)
            if not step3.status == "completed":
                return result

            # Step 4: Resume generation
            step4 = self._execute_resume_generation(request_data, result)
            if not step4.status == "completed":
                return result

            # Step 5: Output validation (optional)
            if self.enable_output_validation and result.resume_response:
                step5 = self._execute_output_validation(result.resume_response, result)
                if not step5.status == "completed":
                    return result

            # Mark workflow as successful
            result.success = True
            self.logger.info("Resume generation workflow completed successfully")

        except Exception as e:
            self.logger.error(f"Workflow failed with error: {str(e)}")
            result.success = False
            result.metadata["workflow_error"] = str(e)

        finally:
            # Calculate total execution time
            workflow_end = datetime.now()
            result.total_time_seconds = (workflow_end - workflow_start).total_seconds()
            result.metadata["completed_at"] = workflow_end.isoformat()

        return result

    def _execute_input_validation(self, request_data: Dict[str, Any], result: WorkflowResult) -> WorkflowStep:
        """Execute input validation step"""
        step = WorkflowStep(step_name="input_validation")
        step.started_at = datetime.now().isoformat()
        step.status = "running"

        try:
            self.logger.info("Validating input with LIC compliance checks")

            # Validate overall resume request
            validation_result = self.input_validator.validate_resume_request(request_data)
            result.validation_results.append(validation_result)

            # Validate job targeting specifically
            target_role = request_data.get("target_role", "")
            experience_level = request_data.get("experience_level", "")
            job_description = request_data.get("job_description")

            targeting_result = self.input_validator.validate_job_targeting(
                target_role, experience_level, job_description
            )
            result.validation_results.append(targeting_result)

            # Check if validation passed
            if not validation_result.is_valid or not targeting_result.is_valid:
                step.status = "failed"
                step.error_message = "Input validation failed"
                result.metadata["validation_errors"] = (
                    validation_result.errors + targeting_result.errors
                )
            else:
                step.status = "completed"
                step.metadata["compliance_score"] = validation_result.compliance_score

        except Exception as e:
            step.status = "failed"
            step.error_message = str(e)
            self.logger.error(f"Input validation step failed: {str(e)}")

        finally:
            step.completed_at = datetime.now().isoformat()
            result.steps_completed.append(step)

        return step

    def _execute_schema_validation(self, request_data: Dict[str, Any], result: WorkflowResult) -> WorkflowStep:
        """Execute schema validation step"""
        step = WorkflowStep(step_name="schema_validation")
        step.started_at = datetime.now().isoformat()
        step.status = "running"

        try:
            self.logger.info("Validating request schema")

            schema_result = self.schema_validator.validate_resume_request_schema(request_data)
            result.schema_results.append(schema_result)

            if not schema_result.is_valid:
                step.status = "failed"
                step.error_message = "Schema validation failed"
                result.metadata["schema_errors"] = schema_result.errors
            else:
                step.status = "completed"
                step.metadata["schema_version"] = schema_result.schema_version

        except Exception as e:
            step.status = "failed"
            step.error_message = str(e)
            self.logger.error(f"Schema validation step failed: {str(e)}")

        finally:
            step.completed_at = datetime.now().isoformat()
            result.steps_completed.append(step)

        return step

    def _execute_memory_query(self, request_data: Dict[str, Any], result: WorkflowResult) -> WorkflowStep:
        """Execute memory query step"""
        step = WorkflowStep(step_name="memory_query")
        step.started_at = datetime.now().isoformat()
        step.status = "running"

        try:
            if not self.enable_memory_query:
                step.status = "completed"
                step.metadata["skipped"] = True
                return step

            self.logger.info("Querying memory for relevant resume data")

            # Query for relevant bullets
            target_role = request_data.get("target_role", "")
            target_company = request_data.get("target_company")

            memory_request = MemoryQueryRequest(
                query_type="bullets",
                target_role=target_role,
                company=target_company,
                min_relevance_score=0.5
            )

            memory_response = self.memory_adapter.query_memory(memory_request)

            if memory_response.success:
                step.status = "completed"
                step.metadata["bullets_found"] = len(memory_response.results)
                step.metadata["memory_stats"] = memory_response.query_stats

                # Store memory results in workflow metadata for later use
                result.metadata["memory_query_results"] = memory_response.results
            else:
                step.status = "completed"  # Don't fail workflow, just log warning
                step.metadata["query_failed"] = True
                step.metadata["error"] = memory_response.metadata.get("error", "Unknown error")
                self.logger.warning("Memory query failed, continuing without memory data")

        except Exception as e:
            step.status = "completed"  # Don't fail workflow, just log warning
            step.metadata["exception"] = str(e)
            self.logger.warning(f"Memory query step failed, continuing without memory data: {str(e)}")

        finally:
            step.completed_at = datetime.now().isoformat()
            result.steps_completed.append(step)

        return step

    def _execute_resume_generation(self, request_data: Dict[str, Any], result: WorkflowResult) -> WorkflowStep:
        """Execute resume generation step"""
        step = WorkflowStep(step_name="resume_generation")
        step.started_at = datetime.now().isoformat()
        step.status = "running"

        try:
            self.logger.info("Generating enhanced resume")

            # Build generation request
            generation_request = ResumeGenerationRequest(
                target_role=request_data.get("target_role", ""),
                experience_level=request_data.get("experience_level", ""),
                job_description=request_data.get("job_description"),
                master_resume_data=request_data.get("master_resume_data"),
                target_company=request_data.get("target_company"),
                optimization_focus=request_data.get("optimization_focus", ["impact", "keywords"]),
                linkedin_format=request_data.get("linkedin_format", True)
            )

            # Execute generation with retry logic
            resume_response = None

            for attempt in range(self.max_retry_attempts + 1):
                try:
                    resume_response = self.engine_adapter.generate_enhanced_resume(generation_request)
                    break
                except Exception as e:
                    if attempt < self.max_retry_attempts:
                        self.logger.warning(f"Generation attempt {attempt + 1} failed, retrying...")
                        continue
                    else:
                        raise e

            if resume_response:
                result.resume_response = resume_response
                step.status = "completed"
                step.metadata["bullets_generated"] = len(resume_response.enhanced_bullets)
                step.metadata["enhancement_confidence"] = resume_response.enhancement_confidence
                step.metadata["linkedin_compliance"] = resume_response.linkedin_compliance
            else:
                step.status = "failed"
                step.error_message = "Resume generation returned no response"

        except Exception as e:
            step.status = "failed"
            step.error_message = str(e)
            self.logger.error(f"Resume generation step failed: {str(e)}")

        finally:
            step.completed_at = datetime.now().isoformat()
            result.steps_completed.append(step)

        return step

    def _execute_output_validation(self, resume_response: ResumeGenerationResponse, result: WorkflowResult) -> WorkflowStep:
        """Execute output validation step"""
        step = WorkflowStep(step_name="output_validation")
        step.started_at = datetime.now().isoformat()
        step.status = "running"

        try:
            self.logger.info("Validating generated resume output")

            # Convert response to dict for schema validation
            response_dict = {
                "enhanced_bullets": resume_response.enhanced_bullets,
                "professional_summary": resume_response.professional_summary,
                "optimized_skills": resume_response.optimized_skills,
                "metadata": resume_response.metadata,
                "enhancement_confidence": resume_response.enhancement_confidence,
                "provenance_tracking": resume_response.provenance_tracking,
                "linkedin_compliance": resume_response.linkedin_compliance
            }

            # Validate response schema
            schema_result = self.schema_validator.validate_resume_response_schema(response_dict)
            result.schema_results.append(schema_result)

            # Validate bullet points specifically
            bullet_validation = self.input_validator.validate_bullet_points(resume_response.enhanced_bullets)
            result.validation_results.append(bullet_validation)

            # Check overall validation
            if not schema_result.is_valid or not bullet_validation.is_valid:
                step.status = "failed"
                step.error_message = "Output validation failed"
                result.metadata["output_validation_errors"] = (
                    schema_result.errors + bullet_validation.errors
                )
            else:
                step.status = "completed"
                step.metadata["output_compliance_score"] = bullet_validation.compliance_score

        except Exception as e:
            step.status = "failed"
            step.error_message = str(e)
            self.logger.error(f"Output validation step failed: {str(e)}")

        finally:
            step.completed_at = datetime.now().isoformat()
            result.steps_completed.append(step)

        return step

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get workflow system status"""
        return {
            "workflow_version": "1.0.0",
            "components_initialized": {
                "engine_adapter": bool(self.engine_adapter),
                "memory_adapter": bool(self.memory_adapter),
                "input_validator": bool(self.input_validator),
                "schema_validator": bool(self.schema_validator)
            },
            "configuration": {
                "enable_memory_query": self.enable_memory_query,
                "enable_output_validation": self.enable_output_validation,
                "max_retry_attempts": self.max_retry_attempts
            },
            "memory_stats": self.memory_adapter.get_memory_stats(),
            "validation_summary": self.input_validator.get_validation_summary(),
            "schema_definitions": self.schema_validator.get_schema_definitions()
        }

    def execute_quick_validation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute quick validation only (no generation)"""
        try:
            # Input validation
            input_result = self.input_validator.validate_resume_request(request_data)

            # Schema validation
            schema_result = self.schema_validator.validate_resume_request_schema(request_data)

            return {
                "valid": input_result.is_valid and schema_result.is_valid,
                "input_validation": {
                    "is_valid": input_result.is_valid,
                    "errors": input_result.errors,
                    "warnings": input_result.warnings,
                    "compliance_score": input_result.compliance_score
                },
                "schema_validation": {
                    "is_valid": schema_result.is_valid,
                    "errors": schema_result.errors,
                    "schema_version": schema_result.schema_version
                }
            }

        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }

