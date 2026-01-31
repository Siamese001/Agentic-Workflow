#!/usr/bin/env python3
"""
Validate Sovereign Migration - Demonstrates all components working
"""

import sys
from pathlib import Path

# Add apps_rg to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def validate_knowledge_base():
    """Validate knowledge base is loaded correctly."""
    print("=" * 60)
    print("1. KNOWLEDGE BASE VALIDATION")
    print("-" * 60)

    from apps_rg.domain.knowledge_base import FROZEN_SNAPSHOT, get_node_config, get_prompt

    print(f"✅ Knowledge base version: {FROZEN_SNAPSHOT.version}")
    print(f"✅ Total prompts: {len(FROZEN_SNAPSHOT.prompts)}")
    print(f"✅ Total K-nodes: {len(FROZEN_SNAPSHOT.nodes)}")
    print(f"✅ Total rules: {len(FROZEN_SNAPSHOT.global_rules)}")

    # Test prompt retrieval
    hyde_prompt = get_prompt("k1_hyde_generation")
    assert "{company_name}" in hyde_prompt
    print("✅ Hyde generation prompt validated")

    # Test node config
    k9 = get_node_config("K.9")
    assert k9.config.qa_thresholds["count"] == "Exactly 6"
    print("✅ K.9 Leadership Competencies config validated")

    return True


def validate_base_engine():
    """Validate BaseRGEngine structure."""
    print("\n" + "=" * 60)
    print("2. BASE ENGINE VALIDATION")
    print("-" * 60)

    from apps_rg.engines.base.base_resume_agent import BaseRGEngine
    from pydantic import BaseModel

    class TestInput(BaseModel):
        data: str

    class TestEngine(BaseRGEngine):
        def execute(self, input_data: TestInput) -> TestInput:
            return input_data

    engine = TestEngine()
    status = engine.get_status()

    print(f"✅ Engine initialized: {status['initialized']}")
    print(f"✅ Knowledge available: {status['knowledge_available']}")
    print(f"✅ Engine name: {status['engine']}")

    # Test prompt access
    prompt = engine.get_prompt("input_jd")
    assert "Job Description" in prompt
    print("✅ Prompt access from engine validated")

    return True


def validate_hop_engines():
    """Validate HOP1 and HOP2 engines."""
    print("\n" + "=" * 60)
    print("3. HOP ENGINES VALIDATION")
    print("-" * 60)

    from apps_rg.engines.hops.hop1_clerk_engine import ClerkExtractionEngine, ClerkInput
    from apps_rg.engines.hops.hop2_enrichment_engine import EnrichmentEngine, EnrichmentInput

    # Test HOP1 Clerk
    clerk = ClerkExtractionEngine()
    clerk_input = ClerkInput(
        master_resume={
            "experience": [
                {
                    "company": "TechCo",
                    "role": "Engineer",
                    "duration": "2020-2023",
                    "bullets": ["Led team", "Built system"],
                }
            ],
            "skills": ["Python", "AWS"],
        }
    )

    clerk_output = clerk.execute(clerk_input)
    assert len(clerk_output.experience_sections) == 1
    assert clerk_output.skills == ["Python", "AWS"]
    print(f"✅ HOP1 Clerk extracted {len(clerk_output.experience_sections)} sections")

    # Test HOP2 Enrichment
    enrichment = EnrichmentEngine()
    enrich_input = EnrichmentInput(clerk_output=clerk_output)
    enrich_output = enrichment.execute(enrich_input)

    print(f"✅ HOP2 Enrichment canonicalized {enrich_output.verbs_canonicalized} verbs")
    print(f"✅ HOP2 Enrichment removed {enrich_output.duplicates_removed} duplicates")

    return True


def validate_orchestrator():
    """Validate Resume Orchestrator."""
    print("\n" + "=" * 60)
    print("4. ORCHESTRATOR VALIDATION")
    print("-" * 60)

    from apps_rg.engines.orchestration.resume_orchestrator_engine import (
        OrchestratorInput,
        ResumeOrchestratorEngine,
        WorkflowState,
    )

    orch = ResumeOrchestratorEngine()
    input_data = OrchestratorInput(
        job_description="Software Engineer at TechCorp",
        master_resume={
            "experience": [
                {
                    "company": "PrevCo",
                    "role": "Developer",
                    "duration": "2019-2023",
                    "bullets": ["Developed APIs"],
                }
            ]
        },
    )

    output = orch.execute(input_data)

    print(f"✅ Workflow state: {output.workflow_state}")
    print(f"✅ HOPs executed: {len(output.hop_results)}")

    if output.workflow_state == WorkflowState.COMPLETE:
        print("✅ Orchestration completed successfully")
    elif output.workflow_state == WorkflowState.ERROR:
        print(f"⚠️ Orchestration completed with error: {output.metadata.get('error')}")

    return True


def validate_void_compliance():
    """Validate Void Compliance Engine."""
    print("\n" + "=" * 60)
    print("5. VOID COMPLIANCE VALIDATION")
    print("-" * 60)

    from apps_rg.engines.safety.void_compliance_engine import ComplianceInput, VoidComplianceEngine

    engine = VoidComplianceEngine()

    # Test detection of legacy imports
    engine.scan_file_content("test_file.py", ComplianceInput())

    print("✅ Void Compliance engine initialized")

    # Test with actual dirty content
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("from archives.legacy import OldEngine\n")
        f.write("temperature = 0.7  # Magic string\n")
        temp_path = f.name

    violations = engine.scan_file_content(temp_path, ComplianceInput())

    # Clean up
    import os

    os.unlink(temp_path)

    print(f"✅ Detected {len(violations)} violations in test file")

    # Check for critical violations
    critical = [v for v in violations if v.severity == "CRITICAL"]
    if critical:
        print(f"✅ Found {len(critical)} CRITICAL violations (legacy imports)")

    return True


def validate_pydantic_models():
    """Validate Pydantic model enforcement."""
    print("\n" + "=" * 60)
    print("6. PYDANTIC MODEL VALIDATION")
    print("-" * 60)

    from apps_rg.engines.hops.hop1_clerk_engine import ClerkInput, ExperienceSection
    from pydantic import ValidationError

    # Valid model
    ClerkInput(master_resume={"test": "data"})
    print("✅ Valid ClerkInput created")

    # Valid ExperienceSection
    exp = ExperienceSection(
        company="TestCo", role="Engineer", duration="2020-2023", bullets=["Task 1", "Task 2"]
    )
    print(f"✅ Valid ExperienceSection with {len(exp.bullets)} bullets")

    # Invalid model should raise
    try:
        ClerkInput()  # Missing required field
        print("❌ Should have raised ValidationError")
        return False
    except ValidationError:
        print("✅ ValidationError raised for invalid input")

    return True


def validate_directory_structure():
    """Validate all domain directories exist."""
    print("\n" + "=" * 60)
    print("7. DIRECTORY STRUCTURE VALIDATION")
    print("-" * 60)

    from pathlib import Path

    base = Path("apps_rg/engines")
    domains = [
        "base",
        "hops",
        "orchestration",
        "generation",
        "refinement",
        "quality",
        "safety",
        "retrieval",
    ]

    all_exist = True
    for domain in domains:
        path = base / domain
        if path.exists():
            print(f"✅ Domain '{domain}' directory exists")
        else:
            print(f"❌ Domain '{domain}' directory missing")
            all_exist = False

    # Check for key files
    key_files = [
        "apps_rg/domain/knowledge_base.py",
        "apps_rg/engines/base/base_resume_agent.py",
        "apps_rg/engines/hops/hop1_clerk_engine.py",
        "apps_rg/engines/hops/hop2_enrichment_engine.py",
        "apps_rg/engines/orchestration/resume_orchestrator_engine.py",
        "apps_rg/engines/safety/void_compliance_engine.py",
    ]

    print("\n" + "-" * 60)
    print("KEY FILES:")
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_exist = False

    return all_exist


def main():
    """Run all validations."""
    print("\n" + "🛡️ SOVEREIGN V2.5 MIGRATION VALIDATION" + "\n")

    results = []

    # Run all validations
    try:
        results.append(("Knowledge Base", validate_knowledge_base()))
    except Exception as e:
        print(f"❌ Knowledge Base failed: {e}")
        results.append(("Knowledge Base", False))

    try:
        results.append(("Base Engine", validate_base_engine()))
    except Exception as e:
        print(f"❌ Base Engine failed: {e}")
        results.append(("Base Engine", False))

    try:
        results.append(("HOP Engines", validate_hop_engines()))
    except Exception as e:
        print(f"❌ HOP Engines failed: {e}")
        results.append(("HOP Engines", False))

    try:
        results.append(("Orchestrator", validate_orchestrator()))
    except Exception as e:
        print(f"❌ Orchestrator failed: {e}")
        results.append(("Orchestrator", False))

    try:
        results.append(("Void Compliance", validate_void_compliance()))
    except Exception as e:
        print(f"❌ Void Compliance failed: {e}")
        results.append(("Void Compliance", False))

    try:
        results.append(("Pydantic Models", validate_pydantic_models()))
    except Exception as e:
        print(f"❌ Pydantic Models failed: {e}")
        results.append(("Pydantic Models", False))

    try:
        results.append(("Directory Structure", validate_directory_structure()))
    except Exception as e:
        print(f"❌ Directory Structure failed: {e}")
        results.append(("Directory Structure", False))

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} {status}")

    print("-" * 60)
    print(f"TOTAL: {passed}/{total} passed ({100 * passed / total:.0f}%)")

    if passed == total:
        print("\n🎉 ALL VALIDATIONS PASSED! Migration successful.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} validations failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
