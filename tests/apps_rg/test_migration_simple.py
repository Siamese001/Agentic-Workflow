"""
Simplified Migration Test - Core functionality validation
"""

import pytest
import sys
from pathlib import Path

# Add apps_rg to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_knowledge_base_loads():
    """Test that knowledge base is accessible."""
    from apps_rg.domain.knowledge_base import FROZEN_SNAPSHOT
    
    assert FROZEN_SNAPSHOT.version == "v33.2"
    assert len(FROZEN_SNAPSHOT.nodes) == 12
    assert "K.9" in FROZEN_SNAPSHOT.nodes
    

def test_knowledge_base_prompts():
    """Test prompt retrieval."""
    from apps_rg.domain.knowledge_base import get_prompt
    
    # Test hyde generation prompt
    hyde = get_prompt("k1_hyde_generation")
    assert "{company_name}" in hyde
    assert "{job_title}" in hyde
    

def test_knowledge_base_node_configs():
    """Test node configuration retrieval."""
    from apps_rg.domain.knowledge_base import get_node_config
    
    k9 = get_node_config("K.9")
    assert k9.name == "Leadership Competencies"
    assert k9.config.qa_thresholds["count"] == "Exactly 6"
    

def test_base_engine_structure():
    """Test BaseRGEngine structure."""
    from apps_rg.engines.base.base_resume_agent import BaseRGEngine
    from pydantic import BaseModel
    
    class TestInput(BaseModel):
        data: str
        
    class TestOutput(BaseModel):
        result: str
    
    class TestEngine(BaseRGEngine):
        def execute(self, input_data: TestInput) -> TestOutput:
            return TestOutput(result=f"Processed: {input_data.data}")
    
    engine = TestEngine()
    assert hasattr(engine, 'execute')
    assert hasattr(engine, 'get_prompt')
    assert hasattr(engine, 'get_node_config')
    

def test_clerk_engine_structure():
    """Test ClerkExtractionEngine structure."""
    from apps_rg.engines.hops.hop1_clerk_engine import (
        ClerkExtractionEngine, ClerkInput, ClerkOutput
    )
    
    engine = ClerkExtractionEngine()
    
    # Test with sample data
    input_data = ClerkInput(
        master_resume={
            "experience": [
                {"company": "TestCo", "role": "Engineer", "duration": "2020-2023", "bullets": ["Built X"]}
            ],
            "skills": ["Python"],
            "education": {"degree": "BS CS"}
        }
    )
    
    output = engine.execute(input_data)
    
    assert isinstance(output, ClerkOutput)
    assert len(output.experience_sections) == 1
    assert output.experience_sections[0].company == "TestCo"
    

def test_enrichment_engine_structure():
    """Test EnrichmentEngine structure."""
    from apps_rg.engines.hops.hop2_enrichment_engine import (
        EnrichmentEngine, EnrichmentInput
    )
    from apps_rg.engines.hops.hop1_clerk_engine import ClerkOutput, ExperienceSection
    
    engine = EnrichmentEngine()
    
    # Create test clerk output
    clerk_output = ClerkOutput(
        experience_sections=[
            ExperienceSection(
                company="TestCo",
                role="Engineer", 
                duration="2020-2023",
                bullets=["Led team", "Built system", "Led team"]  # Duplicate
            )
        ]
    )
    
    input_data = EnrichmentInput(clerk_output=clerk_output)
    output = engine.execute(input_data)
    
    assert output.duplicates_removed == 1
    assert len(output.experience_sections[0].bullets) == 2
    

def test_void_compliance_structure():
    """Test VoidComplianceEngine structure."""
    from apps_rg.engines.safety.void_compliance_engine import (
        VoidComplianceEngine, ComplianceInput
    )
    
    engine = VoidComplianceEngine()
    
    # Test scanning for violations
    violations = engine.scan_file_content(
        "test.py",
        ComplianceInput()
    )
    
    # Should return empty list for non-existent file
    assert isinstance(violations, list)
    

def test_orchestrator_structure():
    """Test ResumeOrchestratorEngine structure."""
    from apps_rg.engines.orchestration.resume_orchestrator_engine import (
        ResumeOrchestratorEngine, OrchestratorInput, WorkflowState
    )
    
    engine = ResumeOrchestratorEngine()
    
    input_data = OrchestratorInput(
        job_description="Test JD",
        master_resume={"experience": []}
    )
    
    # Should handle empty resume gracefully
    output = engine.execute(input_data)
    
    assert output.workflow_state in [WorkflowState.COMPLETE, WorkflowState.ERROR]
    assert isinstance(output.metadata, dict)


def test_pydantic_validation():
    """Test that Pydantic models enforce validation."""
    from apps_rg.engines.hops.hop1_clerk_engine import ClerkInput
    from pydantic import ValidationError
    
    # Valid input
    valid = ClerkInput(master_resume={})
    assert valid.master_resume == {}
    
    # Invalid input should fail
    with pytest.raises(ValidationError):
        ClerkInput()  # Missing required field
        

def test_all_domains_exist():
    """Test that all domain directories exist."""
    from pathlib import Path
    
    base = Path("apps_rg/engines")
    domains = ["base", "hops", "orchestration", "generation", "refinement", "quality", "safety", "retrieval"]
    
    for domain in domains:
        path = base / domain
        assert path.exists(), f"Domain {domain} directory missing"
