#!/usr/bin/env python3
"""
Enhanced L3 Orchestrator - Priority 1 & 2 Enhancements Design Reference

⚠️  DESIGN REFERENCE - NOT PRODUCTION READY ⚠️
This file demonstrates the architectural approach for integrating Priority 1 & 2 features.
The method signatures need to be aligned with actual L1-L5 module interfaces before production use.

For working demonstrations, see: enhanced_features_demo.py

Priority 1 Features (Demonstrated):
- Semantic caching (lic_cache_critique.py)
- Error recovery (lic_circuit_breaker.py, lic_fallback_tree.py)
- Enhanced documentation and usage examples

Priority 2 Features (Demonstrated):
- Self-correction (self_correction_injection.py, lic_meta_loop.py)
- Advanced prompt engineering (v6_prompt_integration.py, instructional_injection_v6.py)

Production Integration Status:
✅ All capabilities exist in L1-L5 layers and are accessible
✅ Working demonstrations prove functionality
⚠️  Method signature alignment needed for seamless integration
📋 Integration approach documented in this reference implementation
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Import base orchestrator
from archives.legacy_root_folders.orchestration.orchestrator import OutreachOrchestrator, OrchestratorOutput

# Import Priority 1 enhancements
from .l4.lic_cache_critique import LICCacheCritique, LICCacheCritiqueResult
from .l3.lic_circuit_breaker import LICCircuitBreaker
from .l3.lic_fallback_tree import LICFallbackTree

# Import Priority 2 enhancements  
from archives.legacy_resume_gen.Agentic_Workflow-10_10.l1.self_correction_injection import SelfCorrectionInjector
from .l3.lic_meta_loop import LICMetaLoop
from archives.legacy_resume_gen.Agentic_Workflow-10_10.l1.v6_prompt_integration import V6PromptIntegrator
from archives.legacy_resume_gen.Agentic_Workflow-10_10.l1.instructional_injection_v6 import InstructionalInjectorV6


@dataclass
class EnhancedOrchestratorConfig:
    """Configuration for enhanced orchestrator features."""
    enable_semantic_cache: bool = True
    enable_error_recovery: bool = True
    enable_self_correction: bool = True
    enable_advanced_prompts: bool = True
    cache_freshness_threshold_days: int = 30
    max_retry_attempts: int = 3
    circuit_breaker_threshold: int = 5
    self_correction_iterations: int = 2


class EnhancedOutreachOrchestrator:
    """Enhanced orchestrator with Priority 1 & 2 capabilities integrated."""
    
    def __init__(self, config: Optional[EnhancedOrchestratorConfig] = None):
        """Initialize enhanced orchestrator with all priority features."""
        self.config = config or EnhancedOrchestratorConfig()
        
        # Initialize base orchestrator
        self.base_orchestrator = OutreachOrchestrator()
        
        # Initialize Priority 1 enhancements
        if self.config.enable_semantic_cache:
            self.cache_critique = LICCacheCritique()
            
        if self.config.enable_error_recovery:
            self.circuit_breaker = LICCircuitBreaker(
                failure_threshold=self.config.circuit_breaker_threshold
            )
            self.fallback_tree = LICFallbackTree()
            
        # Initialize Priority 2 enhancements
        if self.config.enable_self_correction:
            self.self_correction_injector = SelfCorrectionInjector()
            self.meta_loop = LICMetaLoop(max_iterations=self.config.self_correction_iterations)
            
        if self.config.enable_advanced_prompts:
            self.v6_prompt_integrator = V6PromptIntegrator()
            self.instructional_injector = InstructionalInjectorV6()
    
    def generate_outreach_message(
        self,
        mission: Dict[str, object],
        sender_profile: Dict[str, object],
        recipient_context: Dict[str, object],
        existing_cache: Optional[Dict[str, object]] = None
    ) -> OrchestratorOutput:
        """Generate outreach message with all priority enhancements."""
        
        execution_trace = []
        start_time = time.time()
        
        try:
            # Priority 1: Semantic Caching - Check if existing cache is sufficient
            cache_result = None
            if self.config.enable_semantic_cache and existing_cache:
                cache_result = self._evaluate_cache_sufficiency(
                    existing_cache, mission, execution_trace
                )
                
                if cache_result.is_good_enough:
                    logger.info("Using existing cache - skipping research pipeline")
                    return self._create_cache_based_output(
                        cache_result, execution_trace, start_time
                    )
            
            # Priority 2: Advanced Prompt Engineering
            enhanced_mission = mission
            if self.config.enable_advanced_prompts:
                enhanced_mission = self._apply_advanced_prompt_engineering(
                    mission, sender_profile, recipient_context, execution_trace
                )
            
            # Execute base pipeline with error recovery
            pipeline_result = self._execute_with_error_recovery(
                enhanced_mission, sender_profile, recipient_context, execution_trace
            )
            
            # Priority 2: Self-Correction
            if self.config.enable_self_correction and pipeline_result.success:
                pipeline_result = self._apply_self_correction(
                    pipeline_result, mission, execution_trace
                )
            
            # Add enhancement metadata
            pipeline_result.metadata.update({
                "semantic_cache_used": cache_result.is_good_enough if cache_result else False,
                "cache_coverage_score": cache_result.coverage_score if cache_result else 0.0,
                "error_recovery_enabled": self.config.enable_error_recovery,
                "self_correction_enabled": self.config.enable_self_correction,
                "advanced_prompts_enabled": self.config.enable_advanced_prompts,
                "enhancement_version": "priority_1_2_integrated"
            })
            
            return pipeline_result
            
        except Exception as e:
            logger.error(f"Enhanced orchestrator failed: {e}")
            return OrchestratorOutput(
                final_message="",
                execution_trace=execution_trace,
                l1_plans={},
                k_node_outputs={},
                success=False,
                error_message=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                pipeline_confidence=0.0,
                delivery_format="failed",
                metadata={"error_phase": "enhanced_orchestration"}
            )
    
    def _evaluate_cache_sufficiency(
        self,
        existing_cache: Dict[str, object],
        mission: Dict[str, object],
        execution_trace: List[Dict[str, object]]
    ) -> LICCacheCritiqueResult:
        """Evaluate if existing cache is sufficient for current mission."""
        logger.info("Evaluating cache sufficiency")
        
        # Extract required targets from mission
        required_targets = set()
        if "research_targets" in mission:
            required_targets.update(mission["research_targets"])
        else:
            # Default targets for outreach missions
            required_targets = {"funding", "strategy", "product", "personnel", "market"}
        
        # Evaluate cache using correct method signature
        cache_result = self.cache_critique.evaluate(
            existing_signals=existing_cache,
            targets=list(required_targets)
        )
        
        execution_trace.append({
            "phase": "semantic_cache_evaluation",
            "status": "success" if cache_result.is_good_enough else "insufficient",
            "coverage_score": cache_result.coverage_score,
            "freshness_score": cache_result.freshness_score,
            "missing_targets": cache_result.missing_targets,
            "timestamp": datetime.now().isoformat()
        })
        
        return cache_result
    
    def _apply_advanced_prompt_engineering(
        self,
        mission: Dict[str, object],
        sender_profile: Dict[str, object],
        recipient_context: Dict[str, object],
        execution_trace: List[Dict[str, object]]
    ) -> Dict[str, object]:
        """Apply advanced prompt engineering to enhance mission."""
        logger.info("Applying advanced prompt engineering")
        
        # V6 prompt integration
        enhanced_mission = self.v6_prompt_integrator.integrate_prompts(
            mission=mission,
            context={"sender": sender_profile, "recipient": recipient_context}
        )
        
        # Instructional injection
        enhanced_mission = self.instructional_injector.inject_instructions(
            mission=enhanced_mission,
            persona=recipient_context.get("persona", "professional"),
            seniority=recipient_context.get("seniority", "mid")
        )
        
        execution_trace.append({
            "phase": "advanced_prompt_engineering",
            "status": "success",
            "v6_integration": True,
            "instructional_injection": True,
            "timestamp": datetime.now().isoformat()
        })
        
        return enhanced_mission
    
    def _execute_with_error_recovery(
        self,
        mission: Dict[str, object],
        sender_profile: Dict[str, object],
        recipient_context: Dict[str, object],
        execution_trace: List[Dict[str, object]]
    ) -> OrchestratorOutput:
        """Execute pipeline with error recovery mechanisms."""
        if not self.config.enable_error_recovery:
            return self.base_orchestrator.generate_outreach_message(
                mission, sender_profile, recipient_context
            )
        
        logger.info("Executing pipeline with error recovery")
        
        # Check circuit breaker
        if self.circuit_breaker.is_open():
            logger.warning("Circuit breaker is open - using fallback strategy")
            return self._execute_fallback_strategy(
                mission, sender_profile, recipient_context, execution_trace
            )
        
        # Execute with retry logic
        last_error = None
        for attempt in range(self.config.max_retry_attempts):
            try:
                result = self.base_orchestrator.generate_outreach_message(
                    mission, sender_profile, recipient_context
                )
                
                if result.success:
                    self.circuit_breaker.record_success()
                    execution_trace.append({
                        "phase": "error_recovery_execution",
                        "status": "success",
                        "attempt": attempt + 1,
                        "timestamp": datetime.now().isoformat()
                    })
                    return result
                else:
                    last_error = result.error_message
                    logger.warning(f"Pipeline attempt {attempt + 1} failed: {last_error}")
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Pipeline attempt {attempt + 1} exception: {last_error}")
        
        # All attempts failed - trigger circuit breaker and use fallback
        self.circuit_breaker.record_failure()
        return self._execute_fallback_strategy(
            mission, sender_profile, recipient_context, execution_trace
        )
    
    def _execute_fallback_strategy(
        self,
        mission: Dict[str, object],
        sender_profile: Dict[str, object],
        recipient_context: Dict[str, object],
        execution_trace: List[Dict[str, object]]
    ) -> OrchestratorOutput:
        """Execute fallback strategy when main pipeline fails."""
        logger.info("Executing fallback strategy")
        
        fallback_result = self.fallback_tree.execute_fallback(
            mission=mission,
            sender_profile=sender_profile,
            recipient_context=recipient_context
        )
        
        execution_trace.append({
            "phase": "fallback_execution",
            "status": "success" if fallback_result.get("success") else "failed",
            "fallback_level": fallback_result.get("level", "unknown"),
            "timestamp": datetime.now().isoformat()
        })
        
        return OrchestratorOutput(
            final_message=fallback_result.get("message", ""),
            execution_trace=execution_trace,
            l1_plans={"fallback": True},
            k_node_outputs={"fallback": fallback_result},
            success=fallback_result.get("success", False),
            error_message=fallback_result.get("error", "Fallback execution failed"),
            execution_time_ms=fallback_result.get("execution_time_ms", 0),
            pipeline_confidence=fallback_result.get("confidence", 0.3),
            delivery_format="fallback",
            metadata={"fallback_used": True}
        )
    
    def _apply_self_correction(
        self,
        pipeline_result: OrchestratorOutput,
        mission: Dict[str, object],
        execution_trace: List[Dict[str, object]]
    ) -> OrchestratorOutput:
        """Apply self-correction to improve pipeline result."""
        logger.info("Applying self-correction")
        
        corrected_result = self.meta_loop.execute_correction(
            current_result=pipeline_result,
            mission=mission,
            correction_injector=self.self_correction_injector
        )
        
        execution_trace.append({
            "phase": "self_correction",
            "status": "success" if corrected_result.success else "failed",
            "correction_iterations": corrected_result.metadata.get("correction_iterations", 0),
            "quality_improvement": corrected_result.metadata.get("quality_improvement", 0.0),
            "timestamp": datetime.now().isoformat()
        })
        
        return corrected_result
    
    def _create_cache_based_output(
        self,
        cache_result: LICCacheCritiqueResult,
        execution_trace: List[Dict[str, object]],
        start_time: float
    ) -> OrchestratorOutput:
        """Create output when using existing cache."""
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        return OrchestratorOutput(
            final_message=cache_result.metadata.get("cached_message", ""),
            execution_trace=execution_trace,
            l1_plans={"cache_based": True},
            k_node_outputs={"cache_used": True},
            success=cache_result.is_good_enough,
            error_message="" if cache_result.is_good_enough else "Cache insufficient",
            execution_time_ms=execution_time_ms,
            pipeline_confidence=cache_result.coverage_score,
            delivery_format="cache_optimized",
            metadata={
                "cache_based": True,
                "coverage_score": cache_result.coverage_score,
                "freshness_score": cache_result.freshness_score
            }
        )
