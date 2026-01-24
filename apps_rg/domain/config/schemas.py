"""
RG Configuration Schemas - LIC-Aligned Sovereign Architecture.

Defines the Pydantic models for type-safe configuration loading.
Aligned with LIC schemas.py pattern.

HARDENING: Defines strict Pydantic models for the system topology.
This prevents "Schema Drift" where JSON files get out of sync with code expectations.
"""

from __future__ import annotations

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator


# =============================================================================
# TOPOLOGY SCHEMAS (Phase 2 Hardening)
# =============================================================================

class AgentSpec(BaseModel):
    """Configuration for a single Sovereign Agent."""
    name: str = Field(..., description="Unique agent identifier (e.g., HOP1_CLERK)")
    module_path: str = Field(..., description="Python path to the engine class")
    inputs: List[str] = Field(default_factory=list, description="Keys required from Buffer")
    outputs: List[str] = Field(default_factory=list, description="Keys written to Buffer")
    timeout_sec: int = Field(default=30, ge=1)
    criticality: str = Field(default="required", pattern="^(required|optional|best_effort)$")


class OrchestrationTopology(BaseModel):
    """Defines the execution graph."""
    version: str = "2.5.0"
    phases: Dict[str, List[str]] = Field(
        ..., 
        description="Map of Phase Name -> List of Agent Names in execution order"
    )
    agents: Dict[str, AgentSpec] = Field(..., description="Registry of all agents")

    @model_validator(mode="after")
    def validate_agents_exist(self) -> "OrchestrationTopology":
        """Ensure all agents listed in phases exist in the agent registry."""
        known_agents = set(self.agents.keys())
        for phase, agent_list in self.phases.items():
            for agent in agent_list:
                if agent not in known_agents:
                    raise ValueError(f"Phase '{phase}' references unknown agent: '{agent}'")
        return self


# =============================================================================
# LEGACY HOP CONFIG SCHEMAS (Preserved for backward compatibility)
# =============================================================================

class ClerkExtractionConfig(BaseModel):
    """Settings for HOP1 Clerk Extraction Agent."""
    
    metrics_patterns: list[str] = Field(
        default_factory=lambda: [
            r"\$\d+\.?\d*[MBK]\+?",
            r"\d+\.?\d*%",
            r"\d{1,3}(?:,\d{3})+"
        ]
    )
    min_bullets_per_section: int = Field(default=3)
    max_bullets_per_section: int = Field(default=8)


class EnrichmentConfig(BaseModel):
    """Settings for HOP2 Enrichment Agent."""
    
    forbidden_phrases: list[str] = Field(
        default_factory=lambda: [
            "responsible for",
            "duties included",
            "helped with",
            "assisted with",
            "worked on"
        ]
    )
    duplicate_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    power_verbs: list[str] = Field(
        default_factory=lambda: [
            "achieved", "delivered", "led", "drove", "established",
            "transformed", "accelerated", "optimized", "pioneered", "spearheaded"
        ]
    )


class GenerationConfig(BaseModel):
    """Settings for HOP3 Generation Agent."""
    
    base_temperatures: dict[str, float] = Field(
        default_factory=lambda: {
            "summary": 0.7,
            "experience": 0.5,
            "skills": 0.3
        }
    )
    max_section_words: dict[str, int] = Field(
        default_factory=lambda: {
            "summary": 100,
            "experience_bullet": 30,
            "skills": 50
        }
    )
    n_candidates: int = Field(default=3)


class ValidationConfig(BaseModel):
    """Settings for HOP4 Validation Agent."""
    
    severity_threshold: str = Field(default="WARNING")
    rule_categories: list[str] = Field(
        default_factory=lambda: [
            "grammar",
            "formatting",
            "content_quality",
            "ats_compatibility"
        ]
    )
    min_quality_score: float = Field(default=0.7, ge=0.0, le=1.0)


class GateConfig(BaseModel):
    """Settings for HOP5 Gate Decision Agent."""
    
    factual_failure_rules: list[str] = Field(
        default_factory=lambda: [
            "hallucination_detected",
            "source_mismatch",
            "date_inconsistency"
        ]
    )
    max_factual_loops: int = Field(default=3)
    max_creative_retries: int = Field(default=5)
    pass_threshold: float = Field(default=0.8, ge=0.0, le=1.0)


class RefinementConfig(BaseModel):
    """Settings for HOP6 Refinement Agent."""
    
    optimization_targets: list[str] = Field(
        default_factory=lambda: [
            "keyword_density",
            "action_verb_strength",
            "quantification_rate"
        ]
    )
    max_iterations: int = Field(default=3)


class QAReportConfig(BaseModel):
    """Settings for HOP7 QA Report Agent."""
    
    report_sections: list[str] = Field(
        default_factory=lambda: [
            "executive_summary",
            "quality_metrics",
            "validation_results",
            "recommendations"
        ]
    )
    output_directory: str = Field(default="logs/rg_reports")
    scoring_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "content_quality": 0.3,
            "ats_compatibility": 0.25,
            "keyword_match": 0.25,
            "formatting": 0.2
        }
    )


class OrchestratorConfig(BaseModel):
    """Settings for the RG Orchestrator."""
    
    global_step_limit: int = Field(default=20)
    max_retry_iterations: int = Field(default=5)
    checkpoint_enabled: bool = Field(default=True)
    trace_persistence: bool = Field(default=True)


class RGAgentSpecs(BaseModel):
    """Root configuration object for all RG Agent Specifications."""
    
    clerk_extraction: ClerkExtractionConfig = Field(default_factory=ClerkExtractionConfig)
    enrichment: EnrichmentConfig = Field(default_factory=EnrichmentConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    gate_decision: GateConfig = Field(default_factory=GateConfig)
    refinement: RefinementConfig = Field(default_factory=RefinementConfig)
    qa_report: QAReportConfig = Field(default_factory=QAReportConfig)
    orchestrator: OrchestratorConfig = Field(default_factory=OrchestratorConfig)
