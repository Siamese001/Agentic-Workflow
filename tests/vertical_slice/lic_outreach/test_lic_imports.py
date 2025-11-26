"""
LIC Import Chain Smoke Test

Minimal test to verify the entire LIC structural hardening import chain works.
This ensures all components integrate properly without breaking existing functionality.
"""

import pytest


def test_lic_workflow_entry_imports():
    """Test that the main LIC workflow entry point imports successfully."""
    try:
        from apps.lic_outreach.lic_workflow_entry import run_single_outreach, run_batch
        assert callable(run_single_outreach)
        assert callable(run_batch)
    except ImportError as e:
        pytest.fail(f"LIC workflow entry import failed: {e}")


def test_lic_orchestrator_imports():
    """Test that the LIC orchestrator imports successfully."""
    try:
        from l3.lic_orchestrator import LICOrchestrator, RecipientProfile, LICPipelineResult
        assert LICOrchestrator is not None
        assert RecipientProfile is not None
        assert LICPipelineResult is not None
    except ImportError as e:
        pytest.fail(f"LIC orchestrator import failed: {e}")


def test_lic_rag_engine_imports():
    """Test that the LIC RAG engine imports successfully."""
    try:
        from l4.rag.rag_engine import RAGEngine
        from l4.rag.lic_rag_policies import get_rag_policy
        assert RAGEngine is not None
        assert callable(get_rag_policy)
    except ImportError as e:
        pytest.fail(f"LIC RAG engine import failed: {e}")


def test_lic_outreach_shims_import():
    """Test that the L2 outreach shims import successfully."""
    try:
        from l2.outreach.company_research_executor import CompanyResearchExecutor
        from l2.outreach.contact_research_executor import ContactResearchExecutor
        from l2.outreach.message_generation_executor import MessageGenerationExecutor
        from l2.outreach.outreach_batch_executor import OutreachBatchExecutor
        assert CompanyResearchExecutor is not None
        assert ContactResearchExecutor is not None
        assert MessageGenerationExecutor is not None
        assert OutreachBatchExecutor is not None
    except ImportError as e:
        pytest.fail(f"LIC outreach shims import failed: {e}")


def test_lic_config_imports():
    """Test that the LIC configuration imports successfully."""
    try:
        from config.LIC.lic_profile import get_lic_profile, DEFAULT_LIC_PROFILE
        from apps.lic_outreach.pipeline_config import get_lic_pipeline_config
        assert get_lic_profile is not None
        assert DEFAULT_LIC_PROFILE is not None
        assert callable(get_lic_pipeline_config)
    except ImportError as e:
        pytest.fail(f"LIC config import failed: {e}")


def test_lic_end_to_end_import_chain():
    """Test the complete end-to-end import chain from apps to L1-L5."""
    try:
        # This should import the entire stack without errors
        from apps.lic_outreach.lic_workflow_entry import (
            run_single_outreach,
            run_batch,
            run_single_outreach_production,
            run_batch_high_volume
        )
        
        # Verify all functions are callable
        assert callable(run_single_outreach)
        assert callable(run_batch)
        assert callable(run_single_outreach_production)
        assert callable(run_batch_high_volume)
        
        # Verify we can create basic objects
        from l1.outreach_archetype_planning import RecipientProfile
        from l1.outreach_dataclasses import OutreachMission
        
        recipient = RecipientProfile(
            name="Test",
            title="Software Engineer", 
            company="Test Corp",
            industry="Technology",
            seniority="Mid",
            department="Engineering",
            skills=["Python", "Testing"],
            recent_activity=["Recent project"],
            metadata={}
        )
        mission = OutreachMission(objective="Test mission", target_role="Engineer")
        
        assert recipient.name == "Test"
        assert recipient.company == "Test Corp"
        assert mission.objective == "Test mission"
        
    except ImportError as e:
        pytest.fail(f"End-to-end import chain failed: {e}")
    except Exception as e:
        pytest.fail(f"Object creation failed: {e}")


if __name__ == "__main__":
    # Quick manual test
    test_lic_workflow_entry_imports()
    test_lic_orchestrator_imports()
    test_lic_rag_engine_imports()
    test_lic_outreach_shims_import()
    test_lic_config_imports()
    test_lic_end_to_end_import_chain()
    print("✅ All LIC import chain tests passed")
