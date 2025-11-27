"""
LIC Orchestrator Compatibility Layer for 10_12

Provides backward compatibility for regression tests expecting LICOrchestrator.
This is a thin wrapper around OutreachOrchestrator to maintain API compatibility.
"""

from typing import Dict, Any, Optional
from l3.outreach_orchestrator import OutreachOrchestrator


class LICOrchestrator:
    """
    Compatibility wrapper for legacy LIC orchestrator functionality.
    
    This class provides the same interface as the original LICOrchestrator
    but delegates to the new OutreachOrchestrator implementation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with OutreachOrchestrator backend."""
        self._orchestrator = OutreachOrchestrator(config or {})
    
    async def execute_outreach_workflow(self, mission_id: str, **kwargs) -> Dict[str, Any]:
        """
        Legacy compatibility method for outreach workflow execution.
        
        Delegates to OutreachOrchestrator's execute_outreach_workflow method.
        """
        return await self._orchestrator.execute_outreach_workflow(
            mission_id=mission_id,
            **kwargs
        )
    
    async def run_single_outreach_success(self, mission_id: str, **kwargs) -> Dict[str, Any]:
        """
        Legacy compatibility method for single outreach execution.
        
        Delegates to OutreachOrchestrator's execute_outreach_workflow method.
        """
        return await self._orchestrator.execute_outreach_workflow(
            mission_id=mission_id,
            **kwargs
        )
    
    async def resume_job_alignment_workflow(self, resume_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Legacy compatibility method for resume job alignment.
        
        Maps to OutreachOrchestrator's workflow execution.
        """
        return await self._orchestrator.execute_outreach_workflow(
            mission_id=resume_data.get("mission_id", "resume_alignment"),
            resume_data=resume_data,
            **kwargs
        )
    
    async def end_to_end_resume_pipeline_regression(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Legacy compatibility method for end-to-end pipeline testing.
        """
        return await self._orchestrator.execute_outreach_workflow(
            mission_id=input_data.get("mission_id", "e2e_test"),
            **input_data,
            **kwargs
        )
    
    async def backward_compatibility_existing_resume_workflows(self, workflow_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Legacy compatibility method for existing workflow compatibility.
        """
        return await self._orchestrator.execute_outreach_workflow(
            mission_id=workflow_data.get("mission_id", "compat_test"),
            **workflow_data,
            **kwargs
        )
    
    async def resume_pipeline_temporal_feature_flag(self, test_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Legacy compatibility method for temporal feature testing.
        """
        return await self._orchestrator.execute_outreach_workflow(
            mission_id=test_data.get("mission_id", "temporal_test"),
            **test_data,
            **kwargs
        )
    
    async def resume_pipeline_error_handling_preserved(self, error_scenario: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Legacy compatibility method for error handling testing.
        """
        return await self._orchestrator.execute_outreach_workflow(
            mission_id=error_scenario.get("mission_id", "error_test"),
            **error_scenario,
            **kwargs
        )
    
    async def resume_pipeline_performance_regression(self, perf_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Legacy compatibility method for performance regression testing.
        """
        return await self._orchestrator.execute_outreach_workflow(
            mission_id=perf_data.get("mission_id", "perf_test"),
            **perf_data,
            **kwargs
        )
    
    async def resume_pipeline_data_contract_consistency(self, contract_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Legacy compatibility method for data contract consistency testing.
        """
        return await self._orchestrator.execute_outreach_workflow(
            mission_id=contract_data.get("mission_id", "contract_test"),
            **contract_data,
            **kwargs
        )
    
    async def sequential_outreach_workflow_functional_equivalence(self, workflow_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Legacy compatibility method for sequential workflow testing.
        """
        return await self._orchestrator.execute_outreach_workflow(
            mission_id=workflow_data.get("mission_id", "sequential_test"),
            **workflow_data,
            **kwargs
        )
