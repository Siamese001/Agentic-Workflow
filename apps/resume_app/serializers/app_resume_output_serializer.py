"""
resume_app/serializers – app_resume_output_serializer.py

Apps layer serializer for resume output formatting.
Handles conversion of internal resume data to various output formats
with LinkedIn compliance validation and provenance tracking.
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

# Import apps layer components
from apps.resume_app.controllers.app_resume_controller import (
    ResumeResponse, ResearchResponse
)
from apps.resume_app.workflows.app_resume_generation_workflow import (
    WorkflowResult, ResumeGenerationResponse
)
from apps.resume_app.workflows.app_resume_research_workflow import (
    ResearchResult, JobAnalysisResult, ThematicAnalysisResult
)
from apps.resume_app.validators.app_resume_input_validator import (
    ValidationResult
)


@dataclass
class ResumeOutputFormat:
    """Resume output format specification"""
    format_type: str = "json"  # "json", "markdown", "html", "pdf"
    include_metadata: bool = True
    include_provenance: bool = False
    linkedin_optimized: bool = True
    sections: List[str] = field(default_factory=lambda: [
        "header", "summary", "experience", "skills", "education"
    ])


@dataclass
class SerializedResume:
    """Serialized resume output"""
    format_type: str
    content: Union[str, Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)
    linkedin_compliance: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ResumeOutputSerializer:
    """Apps layer serializer for resume output formatting"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Serialization configuration
        self.default_format = self.config.get("default_format", "json")
        self.include_debug_info = self.config.get("include_debug_info", False)
        self.validate_on_serialize = self.config.get("validate_on_serialize", True)
    
    def serialize_resume_response(self, response: ResumeResponse, 
                                output_format: Optional[ResumeOutputFormat] = None) -> SerializedResume:
        """Serialize resume response to specified output format"""
        if not output_format:
            output_format = ResumeOutputFormat(
                format_type=self.default_format,
                linkedin_optimized=True
            )
        
        try:
            # Prepare base resume data
            resume_data = self._prepare_resume_data(response)
            
            # Validate if required
            if self.validate_on_serialize:
                validation_result = self._validate_resume_data(resume_data)
                if not validation_result.is_valid:
                    self.logger.warning(f"Resume data validation failed: {validation_result.errors}")
            
            # Serialize based on format type
            if output_format.format_type == "json":
                content = self._serialize_to_json(resume_data, output_format)
            elif output_format.format_type == "markdown":
                content = self._serialize_to_markdown(resume_data, output_format)
            elif output_format.format_type == "html":
                content = self._serialize_to_html(resume_data, output_format)
            else:
                raise ValueError(f"Unsupported format type: {output_format.format_type}")
            
            # Prepare metadata
            metadata = self._prepare_metadata(response, output_format)
            
            # Prepare provenance if requested
            provenance = self._prepare_provenance(response) if output_format.include_provenance else {}
            
            # Prepare LinkedIn compliance info
            linkedin_compliance = self._prepare_linkedin_compliance(response)
            
            return SerializedResume(
                format_type=output_format.format_type,
                content=content,
                metadata=metadata,
                provenance=provenance,
                linkedin_compliance=linkedin_compliance,
                generated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Resume serialization failed: {str(e)}")
            # Return error response
            return SerializedResume(
                format_type=output_format.format_type,
                content={"error": str(e)},
                metadata={"serialization_failed": True},
                provenance={},
                linkedin_compliance={"valid": False, "error": str(e)},
                generated_at=datetime.now().isoformat()
            )
    
    def serialize_research_response(self, response: ResearchResponse, 
                                  output_format: Optional[ResumeOutputFormat] = None) -> SerializedResume:
        """Serialize research response to specified output format"""
        if not output_format:
            output_format = ResumeOutputFormat(format_type="json")
        
        try:
            # Prepare research data
            research_data = self._prepare_research_data(response)
            
            # Serialize based on format type
            if output_format.format_type == "json":
                content = self._serialize_to_json(research_data, output_format)
            elif output_format.format_type == "markdown":
                content = self._serialize_research_to_markdown(research_data, output_format)
            else:
                content = self._serialize_to_json(research_data, output_format)
            
            # Prepare metadata
            metadata = {
                "response_type": "research",
                "success": response.success,
                "processing_time_seconds": response.processing_time_seconds,
                "error_message": response.error_message,
                "generated_at": datetime.now().isoformat()
            }
            
            return SerializedResume(
                format_type=output_format.format_type,
                content=content,
                metadata=metadata,
                provenance={},
                linkedin_compliance={},
                generated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Research serialization failed: {str(e)}")
            return SerializedResume(
                format_type=output_format.format_type,
                content={"error": str(e)},
                metadata={"serialization_failed": True},
                provenance={},
                linkedin_compliance={},
                generated_at=datetime.now().isoformat()
            )
    
    def _prepare_resume_data(self, response: ResumeResponse) -> Dict[str, Any]:
        """Prepare resume data for serialization"""
        if not response.resume_data:
            return {"error": "No resume data available"}
        
        resume_data = response.resume_data.copy()
        
        # Add validation results if available
        if response.validation_results:
            resume_data["validation_results"] = [
                {
                    "is_valid": result.is_valid,
                    "compliance_score": result.compliance_score,
                    "errors": result.errors,
                    "warnings": result.warnings
                }
                for result in response.validation_results
            ]
        
        # Add workflow metadata if available
        if response.workflow_result:
            resume_data["workflow_metadata"] = {
                "success": response.workflow_result.success,
                "steps_completed": len(response.workflow_result.steps_completed),
                "total_time_seconds": response.workflow_result.total_time_seconds
            }
        
        return resume_data
    
    def _prepare_research_data(self, response: ResearchResponse) -> Dict[str, Any]:
        """Prepare research data for serialization"""
        if not response.research_result:
            return {"error": "No research data available"}
        
        research = response.research_result
        
        research_data = {
            "success": research.success,
            "keyword_rankings": research.keyword_rankings,
            "competitive_insights": research.competitive_insights,
            "recommendations": research.recommendations,
            "total_time_seconds": research.total_time_seconds,
            "metadata": research.metadata
        }
        
        # Add job analysis if available
        if research.job_analysis:
            research_data["job_analysis"] = {
                "target_role": research.job_analysis.target_role,
                "required_skills": research.job_analysis.required_skills,
                "preferred_skills": research.job_analysis.preferred_skills,
                "experience_level": research.job_analysis.experience_level,
                "key_responsibilities": research.job_analysis.key_responsibilities,
                "company_context": research.job_analysis.company_context,
                "industry_keywords": research.job_analysis.industry_keywords
            }
        
        # Add thematic analysis if available
        if research.thematic_analysis:
            research_data["thematic_analysis"] = {
                "primary_themes": research.thematic_analysis.primary_themes,
                "secondary_themes": research.thematic_analysis.secondary_themes,
                "skill_clusters": research.thematic_analysis.skill_clusters,
                "achievement_indicators": research.thematic_analysis.achievement_indicators,
                "culture_fit_keywords": research.thematic_analysis.culture_fit_keywords
            }
        
        return research_data
    
    def _serialize_to_json(self, data: Dict[str, Any], 
                          output_format: ResumeOutputFormat) -> str:
        """Serialize data to JSON format"""
        json_data = data.copy()
        
        # Filter sections if specified
        if output_format.sections and "sections" in json_data:
            filtered_sections = {}
            for section in output_format.sections:
                if section in json_data["sections"]:
                    filtered_sections[section] = json_data["sections"][section]
            json_data["sections"] = filtered_sections
        
        # Remove metadata if not requested
        if not output_format.include_metadata:
            json_data.pop("metadata", None)
            json_data.pop("validation_results", None)
            json_data.pop("workflow_metadata", None)
        
        return json.dumps(json_data, indent=2, ensure_ascii=False)
    
    def _serialize_to_markdown(self, data: Dict[str, Any], 
                             output_format: ResumeOutputFormat) -> str:
        """Serialize resume data to Markdown format"""
        markdown_lines = []
        
        # Header section
        if "professional_summary" in data:
            markdown_lines.append("# Professional Summary")
            markdown_lines.append(data["professional_summary"])
            markdown_lines.append("")
        
        # Experience section
        if "enhanced_bullets" in data:
            markdown_lines.append("# Professional Experience")
            for bullet in data["enhanced_bullets"]:
                markdown_lines.append(f"• {bullet}")
            markdown_lines.append("")
        
        # Skills section
        if "skills_section" in data:
            markdown_lines.append("# Skills")
            skills = data["skills_section"]
            if isinstance(skills, dict):
                for category, skill_list in skills.items():
                    markdown_lines.append(f"## {category.title()}")
                    if isinstance(skill_list, list):
                        for skill in skill_list:
                            markdown_lines.append(f"• {skill}")
                    markdown_lines.append("")
        
        # Metadata section
        if output_format.include_metadata and "metadata" in data:
            markdown_lines.append("# Metadata")
            metadata = data["metadata"]
            markdown_lines.append(f"- Generated: {metadata.get('generated_at', 'Unknown')}")
            markdown_lines.append(f"- Enhancement Confidence: {metadata.get('enhancement_confidence', 0.0):.2f}")
            markdown_lines.append("")
        
        return "\n".join(markdown_lines)
    
    def _serialize_to_html(self, data: Dict[str, Any], 
                          output_format: ResumeOutputFormat) -> str:
        """Serialize resume data to HTML format"""
        html_lines = ["<html>", "<head>", "<title>Resume</title>", "</head>", "<body>"]
        
        # Header section
        if "professional_summary" in data:
            html_lines.append("<h1>Professional Summary</h1>")
            html_lines.append(f"<p>{data['professional_summary']}</p>")
        
        # Experience section
        if "enhanced_bullets" in data:
            html_lines.append("<h2>Professional Experience</h2>")
            html_lines.append("<ul>")
            for bullet in data["enhanced_bullets"]:
                html_lines.append(f"<li>{bullet}</li>")
            html_lines.append("</ul>")
        
        # Skills section
        if "skills_section" in data:
            html_lines.append("<h2>Skills</h2>")
            skills = data["skills_section"]
            if isinstance(skills, dict):
                for category, skill_list in skills.items():
                    html_lines.append(f"<h3>{category.title()}</h3>")
                    html_lines.append("<ul>")
                    if isinstance(skill_list, list):
                        for skill in skill_list:
                            html_lines.append(f"<li>{skill}</li>")
                    html_lines.append("</ul>")
        
        html_lines.extend(["</body>", "</html>"])
        return "\n".join(html_lines)
    
    def _serialize_research_to_markdown(self, data: Dict[str, Any], 
                                      output_format: ResumeOutputFormat) -> str:
        """Serialize research data to Markdown format"""
        markdown_lines = ["# Job Research Analysis", ""]
        
        # Job Analysis
        if "job_analysis" in data:
            analysis = data["job_analysis"]
            markdown_lines.append("## Job Analysis")
            markdown_lines.append(f"**Target Role:** {analysis.get('target_role', 'Unknown')}")
            markdown_lines.append(f"**Experience Level:** {analysis.get('experience_level', 'Unknown')}")
            markdown_lines.append("")
            
            if analysis.get("required_skills"):
                markdown_lines.append("### Required Skills")
                for skill in analysis["required_skills"]:
                    markdown_lines.append(f"- {skill}")
                markdown_lines.append("")
        
        # Keyword Rankings
        if "keyword_rankings" in data:
            markdown_lines.append("## Keyword Rankings")
            rankings = data["keyword_rankings"]
            for keyword, score in list(rankings.items())[:10]:  # Top 10
                markdown_lines.append(f"- **{keyword}**: {score:.2f}")
            markdown_lines.append("")
        
        # Recommendations
        if "recommendations" in data:
            markdown_lines.append("## Recommendations")
            for recommendation in data["recommendations"]:
                markdown_lines.append(f"- {recommendation}")
            markdown_lines.append("")
        
        return "\n".join(markdown_lines)
    
    def _prepare_metadata(self, response: ResumeResponse, 
                         output_format: ResumeOutputFormat) -> Dict[str, Any]:
        """Prepare metadata for serialized output"""
        metadata = {
            "format_type": output_format.format_type,
            "linkedin_optimized": output_format.linkedin_optimized,
            "serialization_timestamp": datetime.now().isoformat(),
            "processing_time_seconds": response.processing_time_seconds,
            "success": response.success
        }
        
        if self.include_debug_info:
            metadata.update({
                "validation_count": len(response.validation_results),
                "has_research_data": response.research_results is not None,
                "workflow_steps": len(response.workflow_result.steps_completed) if response.workflow_result else 0
            })
        
        return metadata
    
    def _prepare_provenance(self, response: ResumeResponse) -> Dict[str, Any]:
        """Prepare provenance tracking information"""
        provenance = {
            "generated_by": "ResumeOutputSerializer",
            "source_components": [
                "ResumeController",
                "ResumeGenerationWorkflow", 
                "ResumeInputValidator"
            ]
        }
        
        if response.workflow_result and response.workflow_result.resume_response:
            resume_response = response.workflow_result.resume_response
            if hasattr(resume_response, 'provenance_tracking'):
                provenance["bullet_provenance"] = resume_response.provenance_tracking
        
        return provenance
    
    def _prepare_linkedin_compliance(self, response: ResumeResponse) -> Dict[str, Any]:
        """Prepare LinkedIn compliance information"""
        compliance = {
            "compliance_score": response.linkedin_compliance_score,
            "validation_passed": all(result.is_valid for result in response.validation_results),
            "character_limits": {
                "summary_max": 2000,
                "bullet_max": 600,
                "max_bullets_per_experience": 5
            }
        }
        
        # Add specific validation issues
        issues = []
        for result in response.validation_results:
            issues.extend(result.errors)
            issues.extend(result.warnings)
        
        if issues:
            compliance["issues"] = issues
        
        return compliance
    
    def _validate_resume_data(self, resume_data: Dict[str, Any]) -> ValidationResult:
        """Basic validation of resume data before serialization"""
        result = ValidationResult()
        
        # Check required fields
        if not resume_data.get("professional_summary"):
            result.errors.append("Missing professional summary")
        
        if not resume_data.get("enhanced_bullets"):
            result.errors.append("Missing enhanced bullets")
        
        # Check LinkedIn compliance
        summary = resume_data.get("professional_summary", "")
        if len(summary) > 2000:
            result.errors.append("Professional summary exceeds 2000 characters")
        
        bullets = resume_data.get("enhanced_bullets", [])
        if len(bullets) > 5:
            result.errors.append("Too many bullet points (max 5 per experience)")
        
        for i, bullet in enumerate(bullets):
            if len(bullet) > 600:
                result.errors.append(f"Bullet {i+1} exceeds 600 characters")
        
        result.is_valid = len(result.errors) == 0
        result.compliance_score = max(0, 100 - (len(result.errors) * 10) - (len(result.warnings) * 5))
        
        return result
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported output formats"""
        return ["json", "markdown", "html"]
    
    def get_serializer_status(self) -> Dict[str, Any]:
        """Get serializer status and configuration"""
        return {
            "serializer": "ResumeOutputSerializer",
            "status": "active",
            "supported_formats": self.get_supported_formats(),
            "default_format": self.default_format,
            "configuration": {
                "include_debug_info": self.include_debug_info,
                "validate_on_serialize": self.validate_on_serialize
            },
            "linkedin_compliance": {
                "enforced": True,
                "character_limits": {
                    "summary_max": 2000,
                    "bullet_max": 600,
                    "max_bullets_per_experience": 5
                }
            }
        }

