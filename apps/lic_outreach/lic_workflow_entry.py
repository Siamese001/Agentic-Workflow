"""
LIC Workflow Entry Point

Entrypoint for LIC vertical slice. Absolutely NO business logic inside this file.
"""

from typing import List, Optional
import logging

from l3.lic_orchestrator import LICOrchestrator, LICOrchestrationConfig, LICPipelineResult, RecipientProfile
from apps.lic_outreach.pipeline_config import get_lic_pipeline_config
from l1.outreach_dataclasses import OutreachMission

logger = logging.getLogger(__name__)


def run_single_outreach(
    mission: OutreachMission, 
    recipient: RecipientProfile,
    config_preset: Optional[str] = None
) -> LICPipelineResult:
    """
    Run single outreach mission through LIC pipeline.
    
    Args:
        mission: Outreach mission details
        recipient: Target recipient profile
        config_preset: Optional configuration preset name
        
    Returns:
        Complete pipeline result
    """
    logger.info(f"Starting single outreach via workflow entry: {recipient.name} at {recipient.company}")
    
    # Get configuration
    pipeline_config = get_lic_pipeline_config(config_preset)
    
    # Create orchestrator configuration
    orch_config = LICOrchestrationConfig(
        enable_company_research=pipeline_config.enable_company_research,
        enable_contact_research=pipeline_config.enable_contact_research,
        enable_message_generation=pipeline_config.enable_message_generation,
        enable_safety_validation=True,
        enable_rag_enrichment=pipeline_config.enable_rag_enrichment,
        parallel_execution=pipeline_config.concurrency.mode.value in ["parallel", "batch"],
        profile_name=config_preset
    )
    
    # Initialize orchestrator
    orchestrator = LICOrchestrator(orch_config)
    
    # Execute pipeline
    return orchestrator.run_single_outreach(mission, recipient)


def run_batch(
    missions: List[OutreachMission], 
    recipients: List[RecipientProfile],
    config_preset: Optional[str] = None
) -> List[LICPipelineResult]:
    """
    Run batch outreach missions through LIC pipeline.
    
    Args:
        missions: List of outreach missions
        recipients: List of target recipients
        config_preset: Optional configuration preset name
        
    Returns:
        List of pipeline results
    """
    logger.info(f"Starting batch outreach via workflow entry: {len(recipients)} recipients")
    
    # Get configuration
    pipeline_config = get_lic_pipeline_config(config_preset)
    
    # Create orchestrator configuration
    orch_config = LICOrchestrationConfig(
        enable_company_research=pipeline_config.enable_company_research,
        enable_contact_research=pipeline_config.enable_contact_research,
        enable_message_generation=pipeline_config.enable_message_generation,
        enable_safety_validation=True,
        enable_rag_enrichment=pipeline_config.enable_rag_enrichment,
        parallel_execution=pipeline_config.concurrency.mode.value in ["parallel", "batch"],
        profile_name=config_preset
    )
    
    # Initialize orchestrator
    orchestrator = LICOrchestrator(orch_config)
    
    # Execute batch
    return orchestrator.run_batch(missions, recipients)


# Convenience functions for common presets
def run_single_outreach_development(mission: OutreachMission, recipient: RecipientProfile) -> LICPipelineResult:
    """Run single outreach with development preset."""
    return run_single_outreach(mission, recipient, "development")


def run_single_outreach_production(mission: OutreachMission, recipient: RecipientProfile) -> LICPipelineResult:
    """Run single outreach with production preset."""
    return run_single_outreach(mission, recipient, "production")


def run_single_outreach_research(mission: OutreachMission, recipient: RecipientProfile) -> LICPipelineResult:
    """Run single outreach with research preset."""
    return run_single_outreach(mission, recipient, "research")


def run_batch_production(missions: List[OutreachMission], recipients: List[RecipientProfile]) -> List[LICPipelineResult]:
    """Run batch with production preset."""
    return run_batch(missions, recipients, "production")


def run_batch_high_volume(missions: List[OutreachMission], recipients: List[RecipientProfile]) -> List[LICPipelineResult]:
    """Run batch with high-volume preset."""
    return run_batch(missions, recipients, "high_volume")


# Export main functions
__all__ = [
    'run_single_outreach',
    'run_batch',
    'run_single_outreach_development',
    'run_single_outreach_production', 
    'run_single_outreach_research',
    'run_batch_production',
    'run_batch_high_volume'
]
