"""
resume_app/adapters – app_resume_engine_adapter.py

Apps layer adapter that wraps agentic_core L2 resume engine logic.
Provides clean interface for resume generation workflows with bullet enhancement,
professional summaries, and skills optimization.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

# Import from agentic_core L2 execution layer
from agentic_core.resume_engine.l2_execution.adapters.rg_llm_adapter import (
    RGLLMAdapter, LLMRequest
)
# Import from agentic_core L4 memory state layer for provenance tracking
from agentic_core.resume_engine.l4_memory_state.memory.rg_memory import (
    BulletProvenance
)


@dataclass
class ResumeGenerationRequest:
    """Apps layer resume generation request"""
    target_role: str
    experience_level: str
    job_description: Optional[str] = None
    master_resume_data: Optional[Dict[str, Any]] = None
    target_company: Optional[str] = None
    optimization_focus: List[str] = field(default_factory=lambda: ["impact", "keywords"])
    linkedin_format: bool = True  # LIC compliance flag


@dataclass
class ResumeGenerationResponse:
    """Apps layer resume generation response"""
    enhanced_bullets: List[str] = field(default_factory=list)
    professional_summary: str = ""
    optimized_skills: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    enhancement_confidence: float = 0.0
    provenance_tracking: Dict[str, BulletProvenance] = field(default_factory=dict)
    linkedin_compliance: Dict[str, bool] = field(default_factory=dict)


class ResumeEngineAdapter:
    """Apps layer adapter for resume generation engine

    Wraps agentic_core L2 RGLLMAdapter to provide clean interface
    for resume generation workflows with LIC compliance.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        # Initialize agentic core L2 adapter
        self.core_adapter = RGLLMAdapter(config)
        self.linkedin_limits = {
            "summary_max_chars": 2000,
            "bullet_max_chars": 600,
            "title_max_chars": 100,
            "max_bullets_per_experience": 5
        }

    def generate_enhanced_resume(self, request: ResumeGenerationRequest) -> ResumeGenerationResponse:
        """Generate enhanced resume with bullet enhancement and optimization"""
        response = ResumeGenerationResponse()

        # Ensure master_resume_data is not None to avoid attribute errors
        if not request.master_resume_data:
            request.master_resume_data = {}

        # Extract bullets from master resume data
        bullets = self._extract_bullets_from_master(request.master_resume_data)

        # Enhance bullets using agentic core L2 logic
        enhanced_bullets = []
        total_confidence = 0.0

        for i, bullet in enumerate(bullets):
            if not bullet or not bullet.strip():
                continue
            llm_request = LLMRequest(
                prompt=bullet,
                context={
                    "target_role": request.target_role,
                    "experience_level": request.experience_level,
                    "job_description": request.job_description,
                    "target_company": request.target_company,
                    "optimization_focus": request.optimization_focus
                },
                task_type="bullet_enhancement"
            )

            try:
                llm_response = self.core_adapter._enhance_bullet(llm_request)
                enhanced_bullets.append(llm_response.content)

                # Track confidence and provenance
                total_confidence += getattr(llm_response, 'overall_confidence', 0.0)
                if hasattr(llm_response, 'provenance'):
                    response.provenance_tracking[bullet] = llm_response.provenance
                    
            except Exception:
                # Use original bullet if enhancement fails
                enhanced_bullets.append(bullet)
                total_confidence += 0.5  # Default confidence for fallback

        # Generate professional summary
        summary_request = LLMRequest(
                prompt="",
                context={
                    "target_role": request.target_role,
                    "experience_level": request.experience_level,
                    "job_description": request.job_description,
                    "optimization_focus": request.optimization_focus
                },
                task_type="professional_summary"
            )
        summary_response = self.core_adapter._generate_professional_summary(summary_request)

        # Optimize skills section
        skills_request = LLMRequest(
            prompt="",
            context={
                "target_role": request.target_role,
                "technical_skills": request.master_resume_data.get("technical_skills", []),
                "soft_skills": request.master_resume_data.get("soft_skills", []),
                "tools": request.master_resume_data.get("tools", []),
                "certifications": request.master_resume_data.get("certifications", [])
            },
            task_type="skills_optimization"
        )
        skills_response = self.core_adapter._optimize_skills(skills_request)

        # Build response
        response.enhanced_bullets = enhanced_bullets
        response.professional_summary = summary_response.content
        response.optimized_skills = self._parse_skills_response(skills_response.content)
        response.enhancement_confidence = total_confidence / len(bullets) if bullets else 0.0
        response.metadata = {
            "model": self.core_adapter.model_name,
            "target_role": request.target_role,
            "experience_level": request.experience_level,
            "bullets_processed": len(bullets),
            "generated_at": datetime.now().isoformat()
        }

        # Apply LIC compliance if requested
        if request.linkedin_format:
            response.linkedin_compliance = self._validate_linkedin_compliance(response)
            response = self._apply_linkedin_formatting(response)

        return response

    def _extract_bullets_from_master(self, master_data: Optional[Dict[str, Any]]) -> List[str]:
        """Extract bullet points from master resume data"""
        if not master_data:
            return []

        bullets = []
        for exp in master_data.get("professional_experience", []):
            exp_bullets = exp.get("bullet_pool", exp.get("highlights", []))
            bullets.extend(exp_bullets)

        return bullets

    def _parse_skills_response(self, skills_content: str) -> Dict[str, List[str]]:
        """Parse skills response into structured format"""
        # Simple parsing - in real implementation would be more sophisticated
        lines = [line.strip() for line in skills_content.split('\n') if line.strip()]

        skills = {
            "technical": [],
            "soft": [],
            "tools": [],
            "certifications": []
        }

        current_category = "technical"
        for line in lines:
            if "technical skills" in line.lower():
                current_category = "technical"
            elif "soft skills" in line.lower():
                current_category = "soft"
            elif "tools" in line.lower():
                current_category = "tools"
            elif "certifications" in line.lower():
                current_category = "certifications"
            elif line.startswith('-') or line.startswith('•'):
                skill = line.lstrip('-•').strip()
                skills[current_category].append(skill)

        return skills

    def _validate_linkedin_compliance(self, response: ResumeGenerationResponse) -> Dict[str, bool]:
        """Validate LinkedIn (LIC) compliance"""
        compliance = {
            "summary_length_ok": len(response.professional_summary) <= self.linkedin_limits["summary_max_chars"],
            "bullets_length_ok": all(len(bullet) <= self.linkedin_limits["bullet_max_chars"] for bullet in response.enhanced_bullets),
            "bullet_count_ok": len(response.enhanced_bullets) <= self.linkedin_limits["max_bullets_per_experience"]
        }
        return compliance

    def _apply_linkedin_formatting(self, response: ResumeGenerationResponse) -> ResumeGenerationResponse:
        """Apply LinkedIn-specific formatting"""
        # Truncate summary if too long
        if len(response.professional_summary) > self.linkedin_limits["summary_max_chars"]:
            response.professional_summary = response.professional_summary[:self.linkedin_limits["summary_max_chars"]-3] + "..."

        # Truncate bullets if too long
        formatted_bullets = []
        for bullet in response.enhanced_bullets:
            if len(bullet) > self.linkedin_limits["bullet_max_chars"]:
                bullet = bullet[:self.linkedin_limits["bullet_max_chars"]-3] + "..."
            formatted_bullets.append(bullet)
        response.enhanced_bullets = formatted_bullets

        return response

