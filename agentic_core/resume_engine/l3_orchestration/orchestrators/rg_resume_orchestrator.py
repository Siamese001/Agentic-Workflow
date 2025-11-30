# Resume Orchestration Framework - L3 Orchestration Layer
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

# Import L1 planning components
from ..l1_planning.inputs.rg_resume_inputs import RGResumeInputs, ResumeInput
from ..l1_planning.planners.rg_resume_planner import RGResumePlanner
from ..l1_planning.strategies.rg_resume_strategy import RGResumeStrategy

# Import L2 execution components
from ..l2_execution.adapters.rg_llm_adapter import RGLLMAdapter, LLMRequest

# Import L4 memory for provenance tracking
from ..l4_memory_state.memory.rg_memory import RGMemory, BulletProvenance

class OrchestrationStatus(Enum):
    """Orchestration execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class OrchestrationContext:
    """Enhanced orchestration context with comprehensive parameters"""
    request_id: str = ""
    target_role: str = ""
    experience_level: str = "mid"
    job_description: Optional[str] = None
    master_resume_data: Optional[Dict[str, Any]] = None
    target_company: Optional[str] = None
    optimization_focus: List[str] = None
    compliance_requirements: Dict[str, Any] = None
    execution_config: Dict[str, Any] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.optimization_focus is None:
            self.optimization_focus = ["impact", "readability", "keywords"]
        if self.compliance_requirements is None:
            self.compliance_requirements = {"linkedin": True, "ats_friendly": True}
        if self.execution_config is None:
            self.execution_config = {"parallel_execution": True, "timeout_seconds": 300}
        if self.metadata is None:
            self.metadata = {}

@dataclass
class OrchestrationResult:
    """Comprehensive orchestration result with full execution details"""
    request_id: str = ""
    status: OrchestrationStatus = OrchestrationStatus.PENDING
    enhanced_bullets: List[str] = field(default_factory=list)
    professional_summary: str = ""
    optimized_skills: Dict[str, List[str]] = field(default_factory=dict)
    planning_metadata: Dict[str, Any] = field(default_factory=dict)
    execution_metadata: Dict[str, Any] = field(default_factory=dict)
    provenance_tracking: Dict[str, BulletProvenance] = field(default_factory=dict)
    compliance_results: Dict[str, bool] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time_ms: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

class RGResumeOrchestrator:
    """Comprehensive resume orchestration framework coordinating L1-L2 components"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Initialize L1 planning components
        self.inputs_processor = RGResumeInputs(config)
        self.planner = RGResumePlanner(config)
        self.strategist = RGResumeStrategy(config)

        # Initialize L2 execution components
        self.llm_adapter = RGLLMAdapter(config)

        # Initialize L4 memory for provenance
        self.memory = RGMemory(config)

        # Orchestration state
        self.active_orchestrations = {}
        self.orchestration_history = []

        # Performance tracking
        self.performance_metrics = {
            "total_orchestrations": 0,
            "successful_orchestrations": 0,
            "average_execution_time_ms": 0.0,
            "compliance_rate": 0.0
        }

    async def orchestrate_resume_generation(self, context: OrchestrationContext) -> OrchestrationResult:
        """Orchestrate complete resume generation using L1→L2 coordination"""
        start_time = datetime.now()

        result = OrchestrationResult(
            request_id=context.request_id,
            status=OrchestrationStatus.RUNNING
        )

        try:
            self.logger.info(f"Starting orchestration for request {context.request_id}")

            # Phase 1: L1 Planning - Process inputs and create strategic plan
            planning_result = await self._execute_planning_phase(context)
            result.planning_metadata = planning_result

            # Phase 2: L2 Execution - Generate enhanced content using plan
            execution_result = await self._execute_execution_phase(context, planning_result)
            result.enhanced_bullets = execution_result.get("enhanced_bullets", [])
            result.professional_summary = execution_result.get("professional_summary", "")
            result.optimized_skills = execution_result.get("optimized_skills", {})
            result.execution_metadata = execution_result.get("metadata", {})

            # Phase 3: Compliance validation and provenance tracking
            compliance_result = await self._execute_compliance_phase(result, context)
            result.compliance_results = compliance_result

            # Phase 4: Performance metrics calculation
            performance_result = self._calculate_performance_metrics(result, start_time)
            result.performance_metrics = performance_result

            # Update status and completion time
            result.status = OrchestrationStatus.COMPLETED
            result.completed_at = datetime.now().isoformat()
            result.execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Update orchestrator metrics
            self._update_performance_metrics(result)

            self.logger.info(f"Orchestration completed successfully for request {context.request_id}")

        except Exception as e:
            self.logger.error(f"Orchestration failed for request {context.request_id}: {str(e)}")
            result.status = OrchestrationStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.now().isoformat()
            result.execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        # Store in history
        self.orchestration_history.append({
            "request_id": result.request_id,
            "status": result.status.value,
            "execution_time_ms": result.execution_time_ms,
            "created_at": result.created_at,
            "completed_at": result.completed_at
        })

        return result

    async def _execute_planning_phase(self, context: OrchestrationContext) -> Dict[str, Any]:
        """Execute L1 planning phase with comprehensive business logic"""

        # Step 1: Process and validate inputs
        resume_input = ResumeInput(
            target_role=context.target_role,
            experience_level=context.experience_level,
            job_description=context.job_description,
            personal_info=context.master_resume_data.get("personal_info", {}) if context.master_resume_data else {},
            skills=context.master_resume_data.get("skills", []) if context.master_resume_data else [],
            education=context.master_resume_data.get("education", []) if context.master_resume_data else [],
            preferences={"optimization_focus": context.optimization_focus},
            metadata={"target_company": context.target_company} if context.target_company else {}
        )

        processed_input = self.inputs_processor.process_input(resume_input)

        # Step 2: Create strategic plan
        resume_plan = self.planner.create_plan(processed_input)

        # Step 3: Generate optimization strategy
        strategy = self.strategist.create_strategy(
            context.target_role,
            context.experience_level,
            context.job_description
        )

        return {
            "processed_input": processed_input.__dict__,
            "resume_plan": resume_plan.__dict__,
            "strategy": strategy.__dict__,
            "validation_results": processed_input.validation_results,
            "market_analysis": processed_input.market_data,
            "skill_gap_analysis": processed_input.skill_gap_analysis
        }

    async def _execute_execution_phase(self, context: OrchestrationContext,
                                     planning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute L2 generation phase using strategic planning"""

        execution_metadata = {}

        # Extract bullets from master resume data
        bullets = self._extract_bullets_from_master(context.master_resume_data)

        # Step 1: Enhance bullets using L2 adapter with strategic guidance
        enhanced_bullets = []
        bullet_confidence_scores = []

        for bullet in bullets:
            if not bullet or not bullet.strip():
                continue

            llm_request = LLMRequest(
                prompt=bullet,
                context={
                    "target_role": context.target_role,
                    "experience_level": context.experience_level,
                    "job_description": context.job_description,
                    "optimization_focus": context.optimization_focus,
                    "strategy": planning_result.get("strategy", {})
                },
                task_type="bullet_enhancement"
            )

            enhanced_response = self.llm_adapter._enhance_bullet(llm_request)
            enhanced_bullets.append(enhanced_response.content)

            # Track confidence scores
            confidence = enhanced_response.metadata.get("confidence_score", 0.0)
            bullet_confidence_scores.append(confidence)

        execution_metadata["bullet_enhancement"] = {
            "original_count": len(bullets),
            "enhanced_count": len(enhanced_bullets),
            "average_confidence": sum(bullet_confidence_scores) / len(bullet_confidence_scores) if bullet_confidence_scores else 0.0
        }

        # Step 2: Generate professional summary
        strategy = planning_result.get("strategy", {})
        key_areas = strategy.get("metadata", {}).get("key_areas", [])
        key_achievements = strategy.get("metadata", {}).get("key_achievements", [])

        summary_request = LLMRequest(
            prompt="Generate professional summary",
            context={
                "target_role": context.target_role,
                "experience_level": context.experience_level,
                "years_experience": self._extract_years_experience(context.master_resume_data),
                "key_areas": key_areas,
                "key_achievements": key_achievements,
                "specialties": context.optimization_focus
            },
            task_type="summary"
        )

        summary_response = self.llm_adapter._generate_professional_summary(summary_request)
        professional_summary = summary_response.content

        execution_metadata["summary_generation"] = {
            "confidence_score": summary_response.metadata.get("confidence_score", 0.0),
            "quality_metrics": summary_response.metadata.get("quality_metrics", {})
        }

        # Step 3: Optimize skills section
        skills_data = context.master_resume_data.get("skills", {}) if context.master_resume_data else {}
        skills_request = LLMRequest(
            prompt="Optimize skills section",
            context={
                "target_role": context.target_role,
                "experience_level": context.experience_level,
                "technical_skills": skills_data.get("technical", []),
                "soft_skills": skills_data.get("soft", []),
                "tools": skills_data.get("tools", [])
            },
            task_type="skills_optimization"
        )

        skills_response = self.llm_adapter._optimize_skills(skills_request)
        optimized_skills = self._parse_skills_response(skills_response.content)

        execution_metadata["skills_optimization"] = {
            "confidence_score": skills_response.metadata.get("confidence_score", 0.0),
            "skills_processed": skills_response.metadata.get("skills_processed", {})
        }

        return {
            "enhanced_bullets": enhanced_bullets,
            "professional_summary": professional_summary,
            "optimized_skills": optimized_skills,
            "metadata": execution_metadata
        }

    async def _execute_compliance_phase(self, result: OrchestrationResult,
                                      context: OrchestrationContext) -> Dict[str, bool]:
        """Execute compliance validation phase"""

        compliance_results = {}

        # LinkedIn compliance checks
        if context.compliance_requirements.get("linkedin", True):
            compliance_results["linkedin_summary_length"] = len(result.professional_summary) <= 2000
            compliance_results["linkedin_bullet_length"] = all(len(bullet) <= 600 for bullet in result.enhanced_bullets)
            compliance_results["linkedin_bullets_per_experience"] = len(result.enhanced_bullets) <= 5

        # ATS compliance checks
        if context.compliance_requirements.get("ats_friendly", True):
            compliance_results["ats_readable"] = self._check_ats_readability(result)
            compliance_results["ats_format"] = self._check_ats_format(result)

        # General compliance
        compliance_results["has_professional_summary"] = bool(result.professional_summary.strip())
        compliance_results["has_enhanced_bullets"] = len(result.enhanced_bullets) > 0
        compliance_results["has_optimized_skills"] = len(result.optimized_skills) > 0

        return compliance_results

    def _calculate_performance_metrics(self, result: OrchestrationResult,
                                     start_time: datetime) -> Dict[str, float]:
        """Calculate comprehensive performance metrics"""

        metrics = {
            "execution_time_ms": result.execution_time_ms,
            "bullets_per_second": len(result.enhanced_bullets) / (result.execution_time_ms / 1000) if result.execution_time_ms > 0 else 0,
            "compliance_score": sum(result.compliance_results.values()) / len(result.compliance_results) if result.compliance_results else 0.0,
            "content_quality_score": self._calculate_content_quality(result),
            "strategic_alignment_score": self._calculate_strategic_alignment(result)
        }

        return metrics

    def _update_performance_metrics(self, result: OrchestrationResult):
        """Update orchestrator performance metrics"""
        self.performance_metrics["total_orchestrations"] += 1

        if result.status == OrchestrationStatus.COMPLETED:
            self.performance_metrics["successful_orchestrations"] += 1

        # Update average execution time
        total_time = self.performance_metrics["average_execution_time_ms"] * (self.performance_metrics["total_orchestrations"] - 1)
        self.performance_metrics["average_execution_time_ms"] = (total_time + result.execution_time_ms) / self.performance_metrics["total_orchestrations"]

        # Update compliance rate
        if result.compliance_results:
            compliance_rate = sum(result.compliance_results.values()) / len(result.compliance_results)
            total_compliance = self.performance_metrics["compliance_rate"] * (self.performance_metrics["total_orchestrations"] - 1)
            self.performance_metrics["compliance_rate"] = (total_compliance + compliance_rate) / self.performance_metrics["total_orchestrations"]

    def _extract_bullets_from_master(self, master_resume_data: Optional[Dict[str, Any]]) -> List[str]:
        """Extract bullet points from master resume data"""
        if not master_resume_data:
            return []

        bullets = []
        experience = master_resume_data.get("experience", [])

        for exp in experience:
            exp_bullets = exp.get("bullets", [])
            bullets.extend(exp_bullets)

        return bullets

    def _extract_years_experience(self, master_resume_data: Optional[Dict[str, Any]]) -> str:
        """Extract years of experience from master resume data"""
        if not master_resume_data:
            return "5"

        # Simple extraction - in production would be more sophisticated
        return master_resume_data.get("years_experience", "5")

    def _parse_skills_response(self, skills_content: str) -> Dict[str, List[str]]:
        """Parse skills response into structured format"""
        skills = {"technical": [], "soft": [], "tools": []}

        lines = skills_content.split('\n')
        for line in lines:
            line = line.strip()
            if "Technical Skills:" in line:
                skills["technical"] = [s.strip() for s in line.replace("Technical Skills:", "").split(',')]
            elif "Leadership Skills:" in line or "Soft Skills:" in line:
                skills["soft"] = [s.strip() for s in line.split("Skills:")[1].split(',')]
            elif "Tools" in line:
                skills["tools"] = [s.strip() for s in line.split("Tools:")[1].split(',')]

        return skills

    def _check_ats_readability(self, result: OrchestrationResult) -> bool:
        """Check ATS readability compliance"""
        # Simple readability check - in production would use more sophisticated metrics
        all_text = result.professional_summary + " ".join(result.enhanced_bullets)
        words = all_text.split()
        return len(words) > 50  # Minimum content threshold

    def _check_ats_format(self, result: OrchestrationResult) -> bool:
        """Check ATS format compliance"""
        # Check for ATS-unfriendly characters
        ats_unfriendly = ["@", "#", "$", "%", "^", "&", "*"]
        all_text = result.professional_summary + " ".join(result.enhanced_bullets)
        return not any(char in all_text for char in ats_unfriendly)

    def _calculate_content_quality(self, result: OrchestrationResult) -> float:
        """Calculate overall content quality score"""
        quality_score = 0.0

        # Summary quality
        if result.professional_summary:
            summary_words = result.professional_summary.split()
            if 50 <= len(summary_words) <= 150:  # Good length range
                quality_score += 0.3

        # Bullet quality
        if result.enhanced_bullets:
            quality_score += 0.3

            # Check for quantification in bullets
            quantified_bullets = sum(1 for bullet in result.enhanced_bullets
                                   if any(char.isdigit() for char in bullet))
            bullet_quality = quantified_bullets / len(result.enhanced_bullets)
            quality_score += bullet_quality * 0.2

        # Skills quality
        if result.optimized_skills:
            total_skills = sum(len(skills) for skills in result.optimized_skills.values())
            if total_skills >= 5:  # Minimum skills threshold
                quality_score += 0.2

        return min(quality_score, 1.0)

    def _calculate_strategic_alignment(self, result: OrchestrationResult) -> float:
        """Calculate strategic alignment score"""
        # Simple alignment check - in production would use more sophisticated analysis
        alignment_score = 0.5  # Base score

        # Check if content includes optimization focus areas
        all_text = result.professional_summary + " ".join(result.enhanced_bullets)

        if "impact" in result.execution_metadata.get("optimization_focus", []):
            if any(word in all_text.lower() for word in ["improved", "increased", "reduced", "achieved"]):
                alignment_score += 0.2

        if "keywords" in result.execution_metadata.get("optimization_focus", []):
            # Simple keyword density check
            words = all_text.split()
            if len(words) > 0:
                keyword_density = len(set(words)) / len(words)  # Unique word ratio
                alignment_score += min(keyword_density, 0.3)

        return min(alignment_score, 1.0)

    def get_orchestration_status(self, request_id: str) -> Optional[OrchestrationResult]:
        """Get status of specific orchestration"""
        return self.active_orchestrations.get(request_id)

    def get_orchestration_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get orchestration history"""
        return self.orchestration_history[-limit:]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get orchestrator performance metrics"""
        return self.performance_metrics.copy()

    def cancel_orchestration(self, request_id: str) -> bool:
        """Cancel active orchestration"""
        if request_id in self.active_orchestrations:
            orchestration = self.active_orchestrations[request_id]
            orchestration.status = OrchestrationStatus.CANCELLED
            orchestration.completed_at = datetime.now().isoformat()
            return True
        return False

    def create_orchestration_context(self, request_data: Dict[str, Any]) -> OrchestrationContext:
        """Create orchestration context from request data"""
        return OrchestrationContext(
            request_id=request_data.get("request_id", f"req_{datetime.now().timestamp()}"),
            target_role=request_data.get("target_role", ""),
            experience_level=request_data.get("experience_level", "mid"),
            job_description=request_data.get("job_description"),
            master_resume_data=request_data.get("master_resume_data"),
            target_company=request_data.get("target_company"),
            optimization_focus=request_data.get("optimization_focus", ["impact", "readability"]),
            compliance_requirements=request_data.get("compliance_requirements", {"linkedin": True, "ats_friendly": True}),
            execution_config=request_data.get("execution_config", {"parallel_execution": True, "timeout_seconds": 300}),
            metadata=request_data.get("metadata", {})
        )

# Factory function for easy instantiation
def create_resume_orchestrator(config: Optional[Dict[str, Any]] = None) -> RGResumeOrchestrator:
    """Create resume orchestrator with default configuration"""
    return RGResumeOrchestrator(config)
