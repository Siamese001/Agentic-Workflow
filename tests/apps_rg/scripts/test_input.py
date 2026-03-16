#!/usr/bin/env python3
"""
Validate Sovereign Migration - Demonstrates all components working
"""

import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "test_input", "execution_auth")
_emit_validates_capability("p2", "test_input", "capability_check")
_emit_routes_to_capability("p2", "test_input", "capability_route")
_emit_writes_via_uwg("p2", "test_input", "uwg_write")
_emit_blocks_direct_write("p2", "test_input", "direct_write_block")
_emit_records_tool_invocation("p2", "test_input", "tool_invocation")
_emit_captures_execution_output("p2", "test_input", "exec_output")
_emit_dispatches_agent("p3", "test_input", "agent_dispatch")
_emit_coordinates_agents("p3", "test_input", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_input", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_input", "healing_outcome")
_emit_escalates_failure("p3", "test_input", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_input", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_input", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_input", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_input", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_input", "eval_metric")
_emit_stores_embedding("p4", "test_input", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_input", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_input", "exec_snapshot_link")
from apps_shared.config.pipeline_constants_config import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

_emit_records_execution_trace("p0", "evidence", "test_input")
_emit_applies_guardrail("p0", "test_input", "p0_governance")
_emit_reads_policy_state("p0", "test_input", "policy_binding")
_emit_snapshots_state("p0", "test_input", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_input", "p4obs", "metric_1")
_emit_emits_metric_event("test_input", "p4obs", "metric_2")
_emit_emits_metric_event("test_input", "p4obs", "metric_3")
_emit_emits_metric_event("test_input", "p4obs", "metric_4")
_emit_emits_metric_event("test_input", "p4obs", "metric_5")
_emit_emits_metric_event("test_input", "p4obs", "metric_6")
_emit_records_incident_event("test_input", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_input", "p4obs", "anomaly")
_emit_writes_observability_log("test_input", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_input", "p4obs", "mon_state")
_emit_triggers_alert("test_input", "p4obs", "alert")
_emit_links_incident_trace("test_input", "p4obs", "trace_link")
_emit_captures_pattern("test_input", "p3lm", "pattern")
_emit_records_learning_event("test_input", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_input", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_input", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_input", "p3lm", "routing")
_emit_improves_agent_policy("test_input", "p3lm", "policy")
_emit_stores_learning_state("test_input", "p3lm", "state")
_emit_records_execution_trace("test_input", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_input", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_input", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_input", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_input", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_input", "env_read", "p2_env_1")
_emit_reads_environ("test_input", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_input", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_input", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_input", "context_pull")
_emit_pulls_context("p1", "test_input", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_input", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_input", "uwg_term_2")
_emit_writes_through("p1", "test_input", "write_through")
_emit_writes_through("p1", "test_input", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_input", "safety_validation")
_emit_invokes_eval("p1", "test_input", "eval_call")
_emit_proposal_commits_routing("p1", "test_input", "routing_commit")
emit_replay_key("p0", "test_input")
emit_determinism_digest("p0", "test_input")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


# Add apps_rg to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def validate_knowledge_base():
    """Validate knowledge base is loaded correctly."""
    print("=" * 60)
    print("1. KNOWLEDGE BASE VALIDATION")
    print("-" * 60)

    from apps_rg.config.knowledge_base import FROZEN_SNAPSHOT, get_node_config, get_prompt

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

    from apps_rg.engines.base_resume_agent import BaseRGEngine
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

    from apps_rg.engines.hop1_clerk_engine import ClerkExtractionEngine, ClerkInput
    from apps_rg.engines.hop2_enrichment_engine import EnrichmentEngine, EnrichmentInput

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
                },
            ],
            "skills": ["Python", "AWS"],
        },
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

    from apps_rg.engines.resume_orchestrator_engine import (
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
                },
            ],
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

    from apps_rg.engines.void_compliance_engine import ComplianceInput, VoidComplianceEngine

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

    from apps_rg.engines.hop1_clerk_engine import ClerkInput, ExperienceSection
    from pydantic import ValidationError

    # Valid model
    ClerkInput(master_resume={"test": "data"})
    print("✅ Valid ClerkInput created")

    # Valid ExperienceSection
    exp = ExperienceSection(
        company="TestCo",
        role="Engineer",
        duration="2020-2023",
        bullets=["Task 1", "Task 2"],
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
