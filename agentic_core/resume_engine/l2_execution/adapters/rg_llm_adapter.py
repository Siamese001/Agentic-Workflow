# RG LLM Adapter for L2 execution
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import comprehensive message generation executor as implementation engine
from ..executors.rg_message_generation_executor import (
    MessageGenerationExecutor, GenerationContext
)

@dataclass
class LLMRequest:
    """LLM request structure"""
    prompt: str = ""
    context: Dict[str, Any] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    task_type: str = "generation"

    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class LLMResponse:
    """LLM response structure"""
    content: str = ""
    token_usage: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class RGLLMAdapter:
    """LLM adapter for resume execution - thin interface layer using comprehensive executor"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.model_name = self.config.get("model", "resume-optimization-v1")
        # Use comprehensive message generation executor as implementation engine
        self.executor = MessageGenerationExecutor(config)

    def generate_professional_summary(self, target_role: str, experience_level: str,
                                    years_experience: str, key_areas: List[str],
                                    key_achievements: List[str], specialties: List[str],
                                    impact_type: str = "business impact",
                                    company_type: str = "innovative organizations") -> LLMResponse:
        """Generate professional summary using comprehensive executor"""

        # Create prompt from parameters
        prompt = (
            f"Generate professional summary for {target_role} with {years_experience} years "
            f"experience in {', '.join(key_areas)}. Key achievements: {', '.join(key_achievements)}. "
            f"Specialties: {', '.join(specialties)}."
        )

        # Create enhanced context
        context = GenerationContext(
            prompt=prompt,
            task_type="professional_summary",
            target_role=target_role,
            experience_level=experience_level,
            optimization_focus=["impact", "keywords", "readability"],
            parameters={
                "key_areas": key_areas,
                "key_achievements": key_achievements,
                "specialties": specialties,
                "impact_type": impact_type,
                "company_type": company_type
            }
        )

        # Execute using comprehensive executor
        result = self.executor.execute(context)

        return LLMResponse(
            content=result.content,
            token_usage=result.token_usage,
            metadata={
                "confidence_score": result.confidence_score,
                "quality_metrics": result.quality_metrics,
                "compliance_check": result.compliance_check,
                "enhancements_applied": result.enhancement_applied,
                "model_name": self.model_name
            }
        )

    def enhance_bullets(self, bullets: List[str], target_role: str,
                       optimization_focus: List[str] = None) -> List[LLMResponse]:
        """Enhance bullets using comprehensive executor"""
        if optimization_focus is None:
            optimization_focus = ["impact", "keywords"]

        enhanced_responses = []

        for bullet in bullets:
            context = GenerationContext(
                prompt=bullet,
                task_type="bullet_enhancement",
                target_role=target_role,
                optimization_focus=optimization_focus,
                compliance_rules={"linkedin": True, "ats_friendly": True}
            )

            result = self.executor.execute(context)

            enhanced_responses.append(LLMResponse(
                content=result.content,
                token_usage=result.token_usage,
                metadata={
                    "confidence_score": result.confidence_score,
                    "quality_metrics": result.quality_metrics,
                    "compliance_check": result.compliance_check,
                    "enhancements_applied": result.enhancement_applied,
                    "original_bullet": bullet,
                    "model_name": self.model_name
                }
            ))

        return enhanced_responses

    def optimize_skills_section(self, technical_skills: List[str],
                              soft_skills: List[str], tools: List[str],
                              target_role: str, experience_level: str = "mid") -> LLMResponse:
        """Optimize skills section using comprehensive executor"""

        context = GenerationContext(
            prompt="Optimize skills section",
            task_type="skills_optimization",
            target_role=target_role,
            experience_level=experience_level,
            optimization_focus=["keywords", "readability"],
            parameters={
                "technical_skills": technical_skills,
                "leadership_skills": soft_skills,
                "tools": tools
            }
        )

        result = self.executor.execute(context)

        return LLMResponse(
            content=result.content,
            token_usage=result.token_usage,
            metadata={
                "confidence_score": result.confidence_score,
                "quality_metrics": result.quality_metrics,
                "compliance_check": result.compliance_check,
                "enhancements_applied": result.enhancement_applied,
                "skills_processed": {
                    "technical_count": len(technical_skills),
                    "soft_count": len(soft_skills),
                    "tools_count": len(tools)
                },
                "model_name": self.model_name
            }
        )

    def process(self, request: LLMRequest) -> LLMResponse:
        """Process LLM request using comprehensive executor"""

        # Map task types to executor task types
        task_mapping = {
            "generation": "general",
            "summary": "professional_summary",
            "bullet_enhancement": "bullet_enhancement",
            "skills_optimization": "skills_optimization"
        }

        executor_task_type = task_mapping.get(request.task_type, "general")

        context = GenerationContext(
            prompt=request.prompt,
            task_type=executor_task_type,
            parameters=request.context,
            compliance_rules={"linkedin": True, "ats_friendly": True}
        )

        result = self.executor.execute(context)

        return LLMResponse(
            content=result.content,
            token_usage=result.token_usage,
            metadata={
                "confidence_score": result.confidence_score,
                "quality_metrics": result.quality_metrics,
                "compliance_check": result.compliance_check,
                "enhancements_applied": result.enhancement_applied,
                "model_name": self.model_name,
                "original_task_type": request.task_type
            }
        )

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "executor_version": "comprehensive_v2",
            "capabilities": [
                "professional_summary_generation",
                "bullet_enhancement",
                "skills_optimization",
                "compliance_checking",
                "quality_metrics"
            ],
            "supported_task_types": [
                "generation", "summary", "bullet_enhancement", "skills_optimization"
            ]
        }

    def get_generation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get generation history from executor"""
        return self.executor.get_generation_history(limit)

    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance using executor analytics"""
        return self.executor.analyze_generation_patterns()

    # Private methods for backward compatibility with resume_app
    def _enhance_bullet(self, request: LLMRequest) -> LLMResponse:
        """Enhance bullet - private method for resume_app compatibility"""
        bullets = [request.prompt]
        enhanced_responses = self.enhance_bullets(
            bullets,
            request.context.get("target_role", "Professional"),
            request.context.get("optimization_focus", ["impact", "keywords"])
        )
        return enhanced_responses[0] if enhanced_responses else LLMResponse()

    def _generate_professional_summary(self, request: LLMRequest) -> LLMResponse:
        """Generate professional summary - private method for resume_app compatibility"""
        context = request.context or {}
        return self.generate_professional_summary(
            target_role=context.get("target_role", "Professional"),
            experience_level=context.get("experience_level", "mid"),
            years_experience=context.get("years_experience", "5"),
            key_areas=context.get("key_areas", []),
            key_achievements=context.get("key_achievements", []),
            specialties=context.get("specialties", []),
            impact_type=context.get("impact_type", "business impact"),
            company_type=context.get("company_type", "innovative organizations")
        )

    def _optimize_skills(self, request: LLMRequest) -> LLMResponse:
        """Optimize skills - private method for resume_app compatibility"""
        context = request.context or {}
        return self.optimize_skills_section(
            technical_skills=context.get("technical_skills", []),
            soft_skills=context.get("soft_skills", []),
            tools=context.get("tools", []),
            target_role=context.get("target_role", "Professional"),
            experience_level=context.get("experience_level", "mid")
        )
