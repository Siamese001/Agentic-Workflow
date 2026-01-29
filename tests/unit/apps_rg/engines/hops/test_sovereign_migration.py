"""
Sovereign Migration Test Suite
Validates the 51-file migration to Sovereign V2.5 Architecture
"""

from unittest.mock import mock_open, patch

import pytest
from apps_rg.domain.knowledge_base import FROZEN_SNAPSHOT
from apps_rg.engines.hops.hop1_clerk_engine import ClerkExtractionEngine, ClerkInput

# Import engines to test
from apps_rg.engines.orchestration.resume_orchestrator_engine import (
    OrchestratorInput,
    ResumeOrchestratorEngine,
    WorkflowState,
)
from apps_rg.engines.safety.void_compliance_engine import ComplianceInput, VoidComplianceEngine


def test_void_compliance_police():
    """CRITICAL: Ensure the Void Compliance engine correctly flags legacy imports."""
    engine = VoidComplianceEngine()

    # Mock a dirty file with legacy import
    dirty_content = "from archives.legacy_code import OldEngine\nimport archives.old_stuff"

    with patch("builtins.open", mock_open(read_data=dirty_content)):
        violations = engine.scan_file_content("test_dirty.py", ComplianceInput())

    assert len(violations) > 0, "Void Police failed to catch legacy import!"
    assert violations[0].violation_type == "LEGACY_IMPORT"
    assert violations[0].severity == "CRITICAL"

    # Test that it finds multiple violations
    assert len(violations) >= 2, "Should find both import statements"


def test_orchestrator_hop_flow():
    """Verify Orchestrator executes HOPs in sequence (0 -> 1 -> 2)."""
    orch = ResumeOrchestratorEngine()

    # Mock input
    input_data = OrchestratorInput(
        job_description="Software Engineer at TechCorp",
        master_resume={
            "experience": [
                {
                    "company": "Previous Corp",
                    "role": "Senior Developer",
                    "duration": "2020-2023",
                    "bullets": ["Led team of 5", "Built microservices"],
                }
            ],
            "skills": ["Python", "Docker", "Kubernetes"],
            "education": {"degree": "BS Computer Science", "school": "Tech University"},
        },
    )

    with patch.object(orch, "_execute_k_nodes", return_value={"K.1": {"executed": True}}):
        with patch.object(orch, "_generate_output", return_value="Generated Resume"):
            output = orch.execute(input_data)

    # Verify HOP execution sequence
    assert output.workflow_state == WorkflowState.COMPLETE
    assert "hop1" in output.hop_results, "HOP-1 should be executed"
    assert "hop2" in output.hop_results, "HOP-2 should be executed"

    # Verify HOP-1 extracted data
    hop1_result = output.hop_results["hop1"]
    assert len(hop1_result["experience_sections"]) > 0
    assert hop1_result["skills"] == ["Python", "Docker", "Kubernetes"]


def test_knowledge_base_integrity():
    """Ensure K-Node configs are accessible."""
    # Test K.9 configuration
    k9_config = FROZEN_SNAPSHOT.nodes["K.9"]
    assert k9_config.config.qa_thresholds["count"] == "Exactly 6"
    assert k9_config.name == "Leadership Competencies"

    # Test K.10 configuration
    k10_config = FROZEN_SNAPSHOT.nodes["K.10"]
    assert ">=3 company-specific details" in k10_config.config.qa_thresholds.values()

    # Test all nodes present
    expected_nodes = ["K.1", "K.2", "K.3", "K.4", "K.5", "K.6", "K.7", "K.8", "K.9", "K.10", "K.11"]
    for node_id in expected_nodes:
        assert node_id in FROZEN_SNAPSHOT.nodes, f"Missing node: {node_id}"


def test_clerk_extraction_schema():
    """Verify Clerk Engine returns sovereign Pydantic models."""
    clerk = ClerkExtractionEngine()

    mock_resume = {
        "experience": [
            {
                "company": "TechCorp",
                "role": "Software Engineer",
                "duration": "2022-2024",
                "bullets": ["Developed APIs", "Improved performance by 50%"],
            }
        ],
        "skills": ["Python", "FastAPI"],
        "education": {"degree": "BS CS"},
    }

    input_data = ClerkInput(master_resume=mock_resume)
    result = clerk.execute(input_data)

    # Verify returns typed object
    assert hasattr(result, "experience_sections"), "Clerk must return typed object"
    assert hasattr(result, "skills")
    assert hasattr(result, "metadata")

    # Verify data extracted correctly
    assert len(result.experience_sections) == 1
    assert result.experience_sections[0].company == "TechCorp"
    assert len(result.experience_sections[0].bullets) == 2
    assert result.skills == ["Python", "FastAPI"]


def test_base_engine_mixins():
    """Verify BaseRGEngine properly inherits from mixins."""
    from apps_rg.engines.base.base_resume_agent import BaseRGEngine

    # Create a test implementation
    class TestEngine(BaseRGEngine):
        def execute(self, input_data):
            return input_data

    engine = TestEngine()

    # Verify mixin methods available
    assert hasattr(engine, "heal_repository"), "HealerMixin methods should be available"
    assert hasattr(engine, "get_prompt"), "Knowledge base integration should be available"
    assert hasattr(engine, "get_node_config"), "Node config access should be available"

    # Test get_status
    status = engine.get_status()
    assert "engine" in status
    assert "initialized" in status
    assert status["initialized"] == True


def test_enrichment_canonicalization():
    """Verify HOP2 enrichment engine canonicalizes verbs and removes duplicates."""
    from apps_rg.engines.hops.hop1_clerk_engine import ClerkOutput, ExperienceSection
    from apps_rg.engines.hops.hop2_enrichment_engine import EnrichmentEngine, EnrichmentInput

    engine = EnrichmentEngine()

    # Create test data with duplicates and verbs to canonicalize
    clerk_output = ClerkOutput(
        experience_sections=[
            ExperienceSection(
                company="Corp A",
                role="Engineer",
                duration="2020-2022",
                bullets=[
                    "Led team of 10 engineers",
                    "Managed cloud infrastructure",
                    "led team of 10 engineers",  # Duplicate
                    "Built microservices architecture",
                ],
            )
        ],
        skills=["Python", "AWS"],
        education={},
    )

    input_data = EnrichmentInput(
        clerk_output=clerk_output,
        canonical_verbs={"Led": "Directed", "Managed": "Directed", "Built": "Established"},
    )

    result = engine.execute(input_data)

    # Verify canonicalization
    bullets = result.experience_sections[0].bullets
    assert bullets[0].startswith("Directed"), "Led should be canonicalized to Directed"
    assert bullets[1].startswith("Directed"), "Managed should be canonicalized to Directed"
    assert any("Established" in b for b in bullets), "Built should be canonicalized"

    # Verify duplicate removal
    assert len(bullets) == 3, "Duplicate bullet should be removed"
    assert result.duplicates_removed > 0
    assert result.verbs_canonicalized > 0


def test_void_compliance_magic_strings():
    """Verify Void Compliance catches magic strings."""
    engine = VoidComplianceEngine()

    # File with magic strings
    magic_content = """
def generate():
    prompt = "Please provide the job description"
    temperature = 0.7
    max_tokens = 500
    return prompt
"""

    with patch("builtins.open", mock_open(read_data=magic_content)):
        violations = engine.scan_file_content("test_magic.py", ComplianceInput())

    # Should find magic string violations
    magic_violations = [v for v in violations if v.violation_type == "MAGIC_STRING"]
    assert len(magic_violations) >= 2, "Should find temperature and prompt magic strings"


def test_orchestrator_error_handling():
    """Verify orchestrator handles errors gracefully."""
    orch = ResumeOrchestratorEngine()

    # Invalid input (missing JD)
    input_data = OrchestratorInput(
        job_description="",  # Empty JD should cause error
        master_resume={},
    )

    output = orch.execute(input_data)

    # Should handle error and set error state
    assert output.workflow_state == WorkflowState.ERROR
    assert "error" in output.metadata


def test_knowledge_base_prompt_access():
    """Verify prompts are accessible from knowledge base."""
    from apps_rg.domain.knowledge_base import get_prompt

    # Test accessing prompts
    hyde_prompt = get_prompt("hyde_gen")
    assert "{company_name}" in hyde_prompt
    assert "{job_title}" in hyde_prompt

    # Test shorthand mapping
    jd_prompt = get_prompt("input_jd")
    assert "Job Description" in jd_prompt

    # Test error on invalid prompt
    with pytest.raises(KeyError):
        get_prompt("INVALID_PROMPT_ID")


def test_pydantic_model_validation():
    """Verify Pydantic models enforce type safety."""
    from apps_rg.engines.hops.hop1_clerk_engine import ClerkInput

    # Valid input
    valid_input = ClerkInput(master_resume={"experience": []}, job_description="Test JD")
    assert valid_input.master_resume is not None

    # Invalid input should raise validation error
    with pytest.raises(Exception):  # Pydantic will raise validation error
        ClerkInput(
            master_resume="not a dict",  # Wrong type
            job_description=123,  # Wrong type
        )


def test_architecture_scan():
    """Verify scan_architecture method works and can trigger SystemExit."""
    engine = VoidComplianceEngine()

    # Mock clean architecture
    with patch.object(engine, "execute") as mock_execute:
        mock_execute.return_value.critical_violations = 0
        mock_execute.return_value.model_dump.return_value = {"violations": []}

        result = engine.scan_architecture()
        assert isinstance(result, dict)

    # Mock dirty architecture with critical violations
    with patch.object(engine, "execute") as mock_execute:
        mock_execute.return_value.critical_violations = 5

        with pytest.raises(SystemExit) as exc_info:
            engine.scan_architecture()

        assert "VOID COMPLIANCE FAILED" in str(exc_info.value)
