"""
resume_app/controllers – app_resume_controller.py

Apps layer controller for resume generation endpoints.
Orchestrates research and generation workflows with proper error handling
and LinkedIn compliance enforcement.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json

# Import apps layer components
from apps.resume_app.workflows.app_resume_generation_workflow import (
    ResumeGenerationWorkflow, WorkflowResult
)
from apps.resume_app.workflows.app_resume_research_workflow import (
    ResumeResearchWorkflow, ResearchResult
)
from apps.resume_app.validators.app_resume_input_validator import (
    ResumeInputValidator, ValidationResult
)
from apps.resume_app.validators.app_resume_schema_validator import (
    ResumeSchemaValidator, SchemaValidationResult
)


@dataclass
class ResumeRequest:
    """Resume generation request from API/controller"""
    target_role: str
    experience_level: str
    job_description: Optional[str] = None
    target_company: Optional[str] = None
    personal_info: Dict[str, Any] = field(default_factory=dict)
    professional_experience: List[Dict[str, Any]] = field(default_factory=list)
    skills: Dict[str, Any] = field(default_factory=dict)
    education: List[Dict[str, Any]] = field(default_factory=list)
    optimization_focus: List[str] = field(default_factory=lambda: ["impact", "keywords"])
    enable_research: bool = False
    linkedin_compliance: bool = True


@dataclass
class ResumeResponse:
    """Resume generation response for API/controller"""
    success: bool = False
    resume_data: Optional[Dict[str, Any]] = None
    research_results: Optional[ResearchResult] = None
    validation_results: List[ValidationResult] = field(default_factory=list)
    schema_results: List[SchemaValidationResult] = field(default_factory=list)
    workflow_result: Optional[WorkflowResult] = None
    linkedin_compliance_score: float = 0.0
    processing_time_seconds: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchRequest:
    """Job research request from API/controller"""
    job_description: str
    target_role: str
    company_info: Optional[str] = None
    include_thematic_analysis: bool = True
    max_keywords: int = 50


@dataclass
class ResearchResponse:
    """Job research response for API/controller"""
    success: bool = False
    research_result: Optional[ResearchResult] = None
    processing_time_seconds: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResumeController:
    """Apps layer controller for resume generation operations"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.generation_workflow = ResumeGenerationWorkflow(self.config)
        self.research_workflow = ResumeResearchWorkflow(self.config)
        self.input_validator = ResumeInputValidator(self.config)
        self.schema_validator = ResumeSchemaValidator(self.config)
        self.logger = logging.getLogger(__name__)
        
        # Controller configuration
        self.enable_research_by_default = self.config.get("enable_research_by_default", False)
        self.strict_linkedin_compliance = self.config.get("strict_linkedin_compliance", True)
        self.max_processing_time = self.config.get("max_processing_time", 300)  # 5 minutes
    
    def generate_resume(self, request: ResumeRequest) -> ResumeResponse:
        """Generate enhanced resume with optional research phase"""
        start_time = datetime.now()
        response = ResumeResponse()
        
        try:
            self.logger.info(f"Starting resume generation for {request.target_role}")
            
            # Step 1: Validate input request
            validation_result = self._validate_resume_request(request)
            response.validation_results.append(validation_result)
            
            # Enforce strict LinkedIn compliance if enabled
            if self.strict_linkedin_compliance and not validation_result.is_valid:
                response.success = False
                response.error_message = f"LinkedIn compliance validation failed: {', '.join(validation_result.errors)}"
                response.linkedin_compliance_score = validation_result.compliance_score
                return response
            
            if not validation_result.is_valid:
                response.success = False
                response.error_message = f"Input validation failed: {', '.join(validation_result.errors)}"
                response.linkedin_compliance_score = validation_result.compliance_score
                return response
            
            # Step 2: Perform research if enabled
            if request.enable_research or self.enable_research_by_default:
                research_result = self._perform_job_research(request)
                response.research_results = research_result
                
                if research_result and not research_result.success:
                    self.logger.warning("Research phase failed, continuing with generation")
            
            # Step 3: Execute generation workflow
            workflow_result = self._execute_generation_workflow(request, response.research_results)
            response.workflow_result = workflow_result
            
            if not workflow_result.success:
                response.success = False
                response.error_message = f"Generation workflow failed: {workflow_result.metadata.get('workflow_error', workflow_result.metadata.get('error', 'Unknown error'))}"
                return response
            
            # Step 4: Validate generated resume
            if workflow_result.resume_response:
                output_validation = self._validate_generated_resume(workflow_result.resume_response)
                response.validation_results.append(output_validation)
                
                if self.strict_linkedin_compliance and not output_validation.is_valid:
                    response.success = False
                    response.error_message = f"LinkedIn compliance validation failed: {', '.join(output_validation.errors)}"
                    response.linkedin_compliance_score = output_validation.compliance_score
                    return response
                
                response.linkedin_compliance_score = output_validation.compliance_score
                
                # Step 5: Format response data
                response.resume_data = self._format_resume_data(workflow_result.resume_response)
            
            response.success = True
            self.logger.info(f"Resume generation completed successfully for {request.target_role}")
            
        except Exception as e:
            self.logger.error(f"Resume generation failed: {str(e)}")
            response.success = False
            response.error_message = str(e)
        
        # Calculate processing time
        end_time = datetime.now()
        response.processing_time_seconds = (end_time - start_time).total_seconds()
        response.metadata["processed_at"] = end_time.isoformat()
        
        return response
    
    def research_job(self, request: ResearchRequest) -> ResearchResponse:
        """Perform job research and analysis"""
        start_time = datetime.now()
        response = ResearchResponse()
        
        try:
            self.logger.info(f"Starting job research for {request.target_role}")
            
            # Validate research request
            if not request.job_description or len(request.job_description.strip()) < 50:
                response.success = False
                response.error_message = "Job description must be at least 50 characters long"
                return response
            
            if not request.target_role or len(request.target_role.strip()) < 3:
                response.success = False
                response.error_message = "Target role must be at least 3 characters long"
                return response
            
            # Execute research workflow
            research_result = self.research_workflow.execute_job_research(
                job_description=request.job_description,
                target_role=request.target_role,
                company_info=request.company_info
            )
            
            response.research_result = research_result
            response.success = research_result.success
            
            if not research_result.success:
                response.error_message = research_result.metadata.get("error", "Research failed")
            
            self.logger.info(f"Job research completed for {request.target_role}")
            
        except Exception as e:
            self.logger.error(f"Job research failed: {str(e)}")
            response.success = False
            response.error_message = str(e)
        
        # Calculate processing time
        end_time = datetime.now()
        response.processing_time_seconds = (end_time - start_time).total_seconds()
        response.metadata["processed_at"] = end_time.isoformat()
        
        return response
    
    def validate_resume(self, resume_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate resume data against LinkedIn compliance"""
        results = []
        
        try:
            # Input validation
            input_result = self.input_validator.validate_resume_request(resume_data)
            results.append(input_result)
            
            # Schema validation
            schema_result = self.schema_validator.validate_resume_schema(resume_data)
            results.append(schema_result)
            
        except Exception as e:
            self.logger.error(f"Resume validation failed: {str(e)}")
            # Create error result
            error_result = ValidationResult()
            error_result.is_valid = False
            error_result.errors.append(f"Validation error: {str(e)}")
            results.append(error_result)
        
        return results
    
    def get_linkedin_compliance_report(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed LinkedIn compliance report"""
        try:
            validation_results = self.validate_resume(resume_data)
            
            report = {
                "overall_compliant": all(result.is_valid for result in validation_results),
                "compliance_score": sum(result.compliance_score for result in validation_results) / len(validation_results),
                "validation_details": [],
                "recommendations": []
            }
            
            for result in validation_results:
                detail = {
                    "validator_type": type(result).__name__,
                    "is_valid": result.is_valid,
                    "compliance_score": result.compliance_score,
                    "errors": result.errors,
                    "warnings": result.warnings
                }
                report["validation_details"].append(detail)
                
                # Add recommendations based on issues
                if result.errors:
                    report["recommendations"].extend([
                        f"Fix validation errors: {', '.join(result.errors)}"
                    ])
                if result.warnings:
                    report["recommendations"].extend([
                        f"Consider addressing warnings: {', '.join(result.warnings)}"
                    ])
            
            return report
            
        except Exception as e:
            self.logger.error(f"Compliance report generation failed: {str(e)}")
            return {
                "overall_compliant": False,
                "compliance_score": 0.0,
                "error": str(e),
                "validation_details": [],
                "recommendations": ["Fix validation system errors"]
            }
    
    def _validate_resume_request(self, request: ResumeRequest) -> ValidationResult:
        """Validate resume generation request"""
        request_data = {
            "target_role": request.target_role,
            "experience_level": request.experience_level,
            "personal_info": request.personal_info,
            "professional_experience": request.professional_experience,
            "skills": request.skills,
            "education": request.education
        }
        
        return self.input_validator.validate_resume_request(request_data)
    
    def _perform_job_research(self, request: ResumeRequest) -> Optional[ResearchResult]:
        """Perform job research as part of resume generation"""
        try:
            if not request.job_description:
                return None
            
            research_request = ResearchRequest(
                job_description=request.job_description,
                target_role=request.target_role,
                company_info=request.target_company,
                include_thematic_analysis=True
            )
            
            research_response = self.research_job(research_request)
            return research_response.research_result
            
        except Exception as e:
            self.logger.warning(f"Job research failed: {str(e)}")
            return None
    
    def _execute_generation_workflow(self, request: ResumeRequest, 
                                   research_result: Optional[ResearchResult]) -> WorkflowResult:
        # Execute resume generation workflow with research context"""
        # Prepare generation request data
        generation_data = {
            "target_role": request.target_role,
            "experience_level": request.experience_level,
            "job_description": request.job_description,
            "target_company": request.target_company,
            "personal_info": request.personal_info,
            "professional_experience": request.professional_experience,
            "skills": request.skills,
            "education": request.education,
            "optimization_focus": request.optimization_focus
        }
        
        # Add research insights if available
        if research_result and research_result.success:
            generation_data["research_insights"] = {
                "required_skills": research_result.job_analysis.required_skills if research_result.job_analysis else [],
                "keyword_rankings": research_result.keyword_rankings,
                "recommendations": research_result.recommendations,
                "thematic_insights": {
                    "primary_themes": research_result.thematic_analysis.primary_themes if research_result.thematic_analysis else [],
                    "skill_clusters": research_result.thematic_analysis.skill_clusters if research_result.thematic_analysis else []
                }
            }
        
        return self.generation_workflow.execute_resume_generation(generation_data)
    
    def _validate_generated_resume(self, resume_response) -> ValidationResult:
        """Validate generated resume for LinkedIn compliance"""
        if not resume_response:
            error_result = ValidationResult()
            error_result.is_valid = False
            error_result.errors.append("No resume response generated")
            return error_result
        
        # Validate output-specific LinkedIn compliance (bullet points, summary length)
        validation_result = ValidationResult()
        
        # Check professional summary length
        summary = getattr(resume_response, 'professional_summary', '')
        if len(summary) > 2000:
            validation_result.errors.append("Professional summary exceeds 2000 characters")
        elif len(summary) < 50:
            validation_result.warnings.append("Professional summary is quite short")
        
        # Check bullet points
        bullets = getattr(resume_response, 'enhanced_bullets', [])
        if len(bullets) > 5:
            validation_result.errors.append(f"Too many bullet points ({len(bullets)}). LinkedIn recommends max 5 per experience.")
        
        for i, bullet in enumerate(bullets):
            if len(bullet) > 600:
                validation_result.errors.append(f"Bullet {i+1} exceeds 600 characters")
            elif len(bullet) < 20:
                validation_result.warnings.append(f"Bullet {i+1} is quite short")
        
        validation_result.is_valid = len(validation_result.errors) == 0
        validation_result.compliance_score = max(0, 100 - (len(validation_result.errors) * 10) - (len(validation_result.warnings) * 5))
        
        return validation_result
    
    def _format_resume_data(self, resume_response) -> Dict[str, Any]:
        """Format resume response data for API output"""
        formatted_data = {
            "professional_summary": getattr(resume_response, 'professional_summary', ''),
            "enhanced_bullets": getattr(resume_response, 'enhanced_bullets', []),
            "skills_section": getattr(resume_response, 'optimized_skills', {}),
            "metadata": {
                "enhancement_confidence": getattr(resume_response, 'overall_confidence', 0.0),
                "provenance_tracking": getattr(resume_response, 'provenance_tracking', {}),
                "generated_at": datetime.now().isoformat()
            }
        }
        
        return formatted_data
    
    def get_controller_status(self) -> Dict[str, Any]:
        """Get controller status and configuration"""
        return {
            "controller": "ResumeController",
            "status": "active",
            "workflows": {
                "generation_workflow": self.generation_workflow.get_workflow_status(),
                "research_workflow": {
                    "initialized": True,
                    "memory_storage_enabled": self.research_workflow.enable_memory_storage,
                    "thematic_analysis_enabled": self.research_workflow.enable_thematic_analysis
                }
            },
            "validators": {
                "input_validator": True,
                "schema_validator": True
            },
            "configuration": {
                "enable_research_by_default": self.enable_research_by_default,
                "strict_linkedin_compliance": self.strict_linkedin_compliance,
                "max_processing_time": self.max_processing_time
            },
            "linkedin_compliance": {
                "enforced": self.strict_linkedin_compliance,
                "character_limits": {
                    "summary_max": 2000,
                    "bullet_max": 600,
                    "max_bullets_per_experience": 5
                }
            }
        }

