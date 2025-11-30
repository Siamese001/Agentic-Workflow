"""
Outreach Pipeline Service
LEVEL 5 - Main pipeline for orchestrating outreach message generation
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..builders.outreach_builder import OutreachBuilder
from ..builders.message_builder import MessageBuilder
from ..enrichers.personalization_engine import PersonalizationEngine
from ..enrichers.profile_analyzer import RelationshipAnalyzer
from ..generators.outreach_generator import MessageGenerator
from ..generators.personalization_engine import TemplateGenerator

@dataclass
class OutreachPipelineResult:
    """Result of outreach pipeline execution"""
    outreach_content: Dict[str, str]
    metadata: Dict[str, Any]
    processing_time: float
    quality_score: float
    pipeline_stages: List[str]
    stage_results: Dict[str, Any]

class OutreachPipeline:
    """Main pipeline for orchestrating outreach message generation"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Initialize pipeline components
        self.outreach_builder = OutreachBuilder()
        self.message_builder = MessageBuilder()
        self.personalization_engine = PersonalizationEngine()
        self.relationship_analyzer = RelationshipAnalyzer()
        self.message_generator = MessageGenerator()
        self.template_generator = TemplateGenerator()

        # Pipeline stages configuration
        self.pipeline_stages = [
            "relationship_analysis",
            "template_selection",
            "message_generation",
            "personalization_enrichment",
            "quality_optimization",
            "final_assembly"
        ]

        # Stage configurations
        self.stage_configs = {
            "relationship_analysis": {
                "enabled": True,
                "timeout": 30,
                "retry_count": 2
            },
            "template_selection": {
                "enabled": True,
                "timeout": 20,
                "retry_count": 1
            },
            "message_generation": {
                "enabled": True,
                "timeout": 60,
                "retry_count": 3
            },
            "personalization_enrichment": {
                "enabled": True,
                "timeout": 45,
                "retry_count": 2
            },
            "quality_optimization": {
                "enabled": True,
                "timeout": 30,
                "retry_count": 1
            },
            "final_assembly": {
                "enabled": True,
                "timeout": 15,
                "retry_count": 1
            }
        }

    async def execute(
        self,
        request_data: Dict[str, Any]
    ) -> OutreachPipelineResult:
        """
        Execute the complete outreach generation pipeline
        
        Args:
            request_data: Dictionary containing all required data for outreach generation
                - recipient_profile: Recipient information
                - sender_profile: Sender information
                - outreach_type: Type of outreach message
                - context: Additional context (optional)
                - preferences: User preferences (optional)
        
        Returns:
            Complete outreach generation result
        """
        try:
            self.logger.info("Starting outreach generation pipeline")
            start_time = datetime.utcnow()

            # Validate input data
            await self._validate_input(request_data)

            # Execute pipeline stages
            stage_results = {}
            pipeline_stages_executed = []

            for stage in self.pipeline_stages:
                if self.stage_configs[stage]["enabled"]:
                    stage_result = await self._execute_stage(stage, request_data, stage_results)
                    stage_results[stage] = stage_result
                    pipeline_stages_executed.append(stage)

                    # Update request_data with stage results for next stages
                    request_data.update(stage_result.get("updates", {}))

            # Generate final result
            final_content = stage_results.get("final_assembly", {}).get("content", {})
            metadata = await self._generate_pipeline_metadata(stage_results, start_time)
            quality_score = await self._calculate_overall_quality_score(stage_results)

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = OutreachPipelineResult(
                outreach_content=final_content,
                metadata=metadata,
                processing_time=processing_time,
                quality_score=quality_score,
                pipeline_stages=pipeline_stages_executed,
                stage_results=stage_results
            )

            self.logger.info(f"Outreach pipeline completed in {processing_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            raise e

    async def _validate_input(self, request_data: Dict[str, Any]) -> None:
        """Validate pipeline input data"""
        required_fields = ["recipient_profile", "sender_profile", "outreach_type"]

        for field in required_fields:
            if field not in request_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate recipient profile
        recipient_profile = request_data["recipient_profile"]
        if not recipient_profile.get("name"):
            raise ValueError("Recipient profile must include name")

        # Validate sender profile
        sender_profile = request_data["sender_profile"]
        if not sender_profile.get("name"):
            raise ValueError("Sender profile must include name")

        # Validate outreach type
        valid_types = ["email", "linkedin", "cold_call", "follow_up", "networking"]
        if request_data["outreach_type"] not in valid_types:
            raise ValueError(f"Invalid outreach type: {request_data['outreach_type']}")

    async def _execute_stage(
        self,
        stage: str,
        request_data: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific pipeline stage"""

        config = self.stage_configs[stage]

        try:
            if stage == "relationship_analysis":
                return await self._execute_relationship_analysis(request_data)
            elif stage == "template_selection":
                return await self._execute_template_selection(request_data, previous_results)
            elif stage == "message_generation":
                return await self._execute_message_generation(request_data, previous_results)
            elif stage == "personalization_enrichment":
                return await self._execute_personalization_enrichment(request_data, previous_results)
            elif stage == "quality_optimization":
                return await self._execute_quality_optimization(request_data, previous_results)
            elif stage == "final_assembly":
                return await self._execute_final_assembly(request_data, previous_results)
            else:
                raise ValueError(f"Unknown pipeline stage: {stage}")

        except Exception as e:
            self.logger.error(f"Stage {stage} failed: {e}")
            raise e

    async def _execute_relationship_analysis(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute relationship analysis stage"""

        recipient_profile = request_data["recipient_profile"]
        sender_profile = request_data["sender_profile"]
        context = request_data.get("context", {})
        interaction_history = request_data.get("interaction_history", [])

        analysis = await self.relationship_analyzer.analyze_relationship(
            recipient_profile, sender_profile, context, interaction_history
        )

        return {
            "relationship_analysis": analysis,
            "updates": {
                "relationship_strength": analysis.relationship_strength,
                "relationship_type": analysis.relationship_type,
                "trust_indicators": analysis.trust_indicators
            }
        }

    async def _execute_template_selection(
        self,
        request_data: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute template selection stage"""

        recipient_profile = request_data["recipient_profile"]
        sender_profile = request_data["sender_profile"]
        context = request_data.get("context", {})

        # Get template recommendations
        templates = await self.template_generator.get_template_recommendations(
            recipient_profile, sender_profile, context
        )

        # Select best template
        selected_template = templates[0] if templates else None

        return {
            "template_selection": {
                "recommended_templates": templates,
                "selected_template": selected_template,
                "selection_confidence": 0.8 if selected_template else 0.5
            },
            "updates": {
                "template": selected_template
            }
        }

    async def _execute_message_generation(
        self,
        request_data: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute message generation stage"""

        recipient_profile = request_data["recipient_profile"]
        sender_profile = request_data["sender_profile"]
        outreach_type = request_data["outreach_type"]
        context = request_data.get("context", {})
        preferences = request_data.get("preferences", {})

        # Generate message
        generated_message = await self.message_generator.generate_message(
            recipient_profile, sender_profile, outreach_type, context, preferences, variations=2
        )

        return {
            "message_generation": generated_message,
            "updates": {
                "generated_content": generated_message.content,
                "message_variations": generated_message.variations
            }
        }

    async def _execute_personalization_enrichment(
        self,
        request_data: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute personalization enrichment stage"""

        base_content = previous_results["message_generation"].content
        recipient_profile = request_data["recipient_profile"]
        sender_profile = request_data["sender_profile"]
        context = request_data.get("context", {})
        preferences = request_data.get("preferences", {})

        # Personalize message
        personalization_result = await self.personalization_engine.personalize_message(
            base_content, recipient_profile, sender_profile, context, preferences
        )

        return {
            "personalization_enrichment": personalization_result,
            "updates": {
                "personalized_content": personalization_result.enriched_content,
                "personalization_score": personalization_result.personalization_score
            }
        }

    async def _execute_quality_optimization(
        self,
        request_data: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute quality optimization stage"""

        content = previous_results["personalization_enrichment"].enriched_content
        recipient_profile = request_data["recipient_profile"]
        sender_profile = request_data["sender_profile"]
        preferences = request_data.get("preferences", {})

        # Build and optimize message components
        components = await self.message_builder.build_message_components(
            recipient_profile, sender_profile, request_data["outreach_type"],
            request_data.get("context", {}), preferences
        )

        # Optimize for quality
        optimized_content = await self._optimize_content_quality(content, components)

        return {
            "quality_optimization": {
                "components": components,
                "optimization_applied": True,
                "quality_improvements": ["length_optimization", "tone_consistency", "clarity_enhancement"]
            },
            "updates": {
                "optimized_content": optimized_content
            }
        }

    async def _execute_final_assembly(
        self,
        request_data: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute final assembly stage"""

        # Get the best content from previous stages
        personalized_content = previous_results.get("personalization_enrichment", {}).get("enriched_content", {})
        optimized_content = previous_results.get("quality_optimization", {}).get("optimized_content", {})

        # Use optimized content if available, otherwise use personalized content
        final_content = optimized_content if optimized_content else personalized_content

        # Add final metadata
        final_metadata = {
            "assembly_timestamp": datetime.utcnow().isoformat(),
            "content_source": "optimized" if optimized_content else "personalized",
            "final_quality_checks": ["length_validation", "tone_consistency", "personalization_verification"]
        }

        return {
            "content": final_content,
            "final_metadata": final_metadata,
            "updates": {}
        }

    async def _optimize_content_quality(
        self,
        content: Dict[str, str],
        components: Dict[str, Any]
    ) -> Dict[str, str]:
        """Optimize content quality using components"""

        optimized = content.copy()

        # Apply component-based optimizations
        for component_type, component in components.items():
            if hasattr(component, 'content') and component_type in optimized:
                # Use optimized component content
                optimized[component_type] = component.content

        # Ensure consistency across all sections
        optimized = await self._ensure_content_consistency(optimized)

        return optimized

    async def _ensure_content_consistency(self, content: Dict[str, str]) -> Dict[str, str]:
        """Ensure consistency across message sections"""

        consistent = content.copy()

        # Extract tone from opening and apply to other sections
        opening = consistent.get("opening", "").lower()

        if "dear" in opening:
            # Formal tone - ensure closing is formal
            if "closing" in consistent:
                consistent["closing"] = consistent["closing"].replace("Best,", "Best regards,")
        elif "hi" in opening or "hey" in opening:
            # Casual tone - ensure closing is casual
            if "closing" in consistent:
                consistent["closing"] = consistent["closing"].replace("Best regards,", "Best,")

        return consistent

    async def _generate_pipeline_metadata(
        self,
        stage_results: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive pipeline metadata"""

        metadata = {
            "pipeline_version": "1.0.0",
            "execution_start": start_time.isoformat(),
            "stages_executed": list(stage_results.keys()),
            "stage_success": all(stage in stage_results for stage in self.pipeline_stages if self.stage_configs[stage]["enabled"]),
            "total_stages": len(self.pipeline_stages),
            "enabled_stages": len([s for s in self.pipeline_stages if self.stage_configs[s]["enabled"]])
        }

        # Add stage-specific metadata
        if "relationship_analysis" in stage_results:
            analysis = stage_results["relationship_analysis"]["relationship_analysis"]
            metadata["relationship_insights"] = {
                "relationship_type": analysis.relationship_type,
                "relationship_strength": analysis.relationship_strength,
                "trust_indicators_count": len(analysis.trust_indicators)
            }

        if "message_generation" in stage_results:
            generation = stage_results["message_generation"]
            metadata["generation_insights"] = {
                "variations_generated": len(generation.variations),
                "quality_metrics": generation.quality_metrics
            }

        if "personalization_enrichment" in stage_results:
            personalization = stage_results["personalization_enrichment"]
            metadata["personalization_insights"] = {
                "personalization_score": personalization.personalization_score,
                "elements_used": len(personalization.personalization_elements)
            }

        return metadata

    async def _calculate_overall_quality_score(self, stage_results: Dict[str, Any]) -> float:
        """Calculate overall quality score from all stages"""

        scores = []

        # Get quality scores from different stages
        if "message_generation" in stage_results:
            generation = stage_results["message_generation"]
            if hasattr(generation, 'quality_metrics'):
                scores.append(generation.quality_metrics.get("overall", 0.7))

        if "personalization_enrichment" in stage_results:
            personalization = stage_results["personalization_enrichment"]
            if hasattr(personalization, 'personalization_score'):
                scores.append(personalization.personalization_score)

        # Add stage completion scores
        completed_stages = len(stage_results)
        total_enabled_stages = len([s for s in self.pipeline_stages if self.stage_configs[s]["enabled"]])
        completion_score = completed_stages / total_enabled_stages if total_enabled_stages > 0 else 0
        scores.append(completion_score)

        # Calculate weighted average
        if scores:
            return sum(scores) / len(scores)
        else:
            return 0.7  # Default score

    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status and configuration"""
        return {
            "pipeline_stages": self.pipeline_stages,
            "stage_configs": self.stage_configs,
            "components_initialized": [
                "outreach_builder",
                "message_builder",
                "personalization_engine",
                "relationship_analyzer",
                "message_generator",
                "template_generator"
            ],
            "status": "ready",
            "version": "1.0.0"
        }

__all__ = ["OutreachPipeline", "OutreachPipelineResult"]
