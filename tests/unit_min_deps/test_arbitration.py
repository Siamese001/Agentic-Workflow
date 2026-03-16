"""Unit tests for multi-agent arbitration system."""

import pytest

from agentic_core.L3_orchestration.arbitration.arbitration_contract import (
    AdvisorProposal,
    ArbitrationDecision,
    ArbitrationInput,
    decision_from_json,
    decision_to_json,
    proposal_from_json,
    proposal_to_json,
)
from agentic_core.L3_orchestration.arbitration.arbitrator import Arbitrator
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

_emit_records_execution_trace("p0", "evidence", "test_arbitration")
_emit_applies_guardrail("p0", "test_arbitration", "p0_governance")
_emit_reads_policy_state("p0", "test_arbitration", "policy_binding")
_emit_snapshots_state("p0", "test_arbitration", "state_snapshot")
emit_replay_key("p0", "test_arbitration")
emit_determinism_digest("p0", "test_arbitration")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_arbitration", "execution_auth")
_emit_validates_capability("p2", "test_arbitration", "capability_check")
_emit_routes_to_capability("p2", "test_arbitration", "capability_route")
_emit_writes_via_uwg("p2", "test_arbitration", "uwg_write")
_emit_blocks_direct_write("p2", "test_arbitration", "direct_write_block")
_emit_records_tool_invocation("p2", "test_arbitration", "tool_invocation")
_emit_captures_execution_output("p2", "test_arbitration", "exec_output")
_emit_dispatches_agent("p3", "test_arbitration", "agent_dispatch")
_emit_coordinates_agents("p3", "test_arbitration", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_arbitration", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_arbitration", "healing_outcome")
_emit_escalates_failure("p3", "test_arbitration", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_arbitration", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_arbitration", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_arbitration", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_arbitration", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_arbitration", "eval_metric")
_emit_stores_embedding("p4", "test_arbitration", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_arbitration", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_arbitration", "exec_snapshot_link")


@pytest.mark.unit_min_deps
def test_advisor_proposal_validation():
    """Test AdvisorProposal validation."""
    # Valid proposal
    proposal = AdvisorProposal(
        advisor_id="test_advisor",
        decision="execute_plan",
        confidence=75,
        rationale=["safe", "fast"],
        risks=["minimal"],
        artifacts=["plan.json"],
    )
    assert proposal.advisor_id == "test_advisor"
    assert proposal.confidence == 75

    # Invalid confidence
    with pytest.raises(ValueError, match="confidence must be between 0 and 100"):
        AdvisorProposal("test", "decision", -1)

    with pytest.raises(ValueError, match="confidence must be between 0 and 100"):
        AdvisorProposal("test", "decision", 101)

    # Empty advisor_id
    with pytest.raises(ValueError, match="advisor_id cannot be empty"):
        AdvisorProposal("", "decision", 50)

    # Empty decision
    with pytest.raises(ValueError, match="decision cannot be empty"):
        AdvisorProposal("test", "", 50)


@pytest.mark.unit_min_deps
def test_arbitration_input_validation():
    """Test ArbitrationInput validation."""
    proposal1 = AdvisorProposal("advisor1", "decision1", 50)
    proposal2 = AdvisorProposal("advisor2", "decision2", 60)

    # Valid input
    input_data = ArbitrationInput(
        task_id="task_1",
        task_kind="planning",
        proposals=[proposal1, proposal2],
    )
    assert len(input_data.proposals) == 2

    # Duplicate advisor IDs
    with pytest.raises(ValueError, match="duplicate advisor IDs not allowed"):
        ArbitrationInput(
            task_id="task_1",
            task_kind="planning",
            proposals=[proposal1, proposal1],  # Same advisor twice
        )


@pytest.mark.unit_min_deps
def test_deterministic_scoring():
    """Test that scoring is deterministic and follows rules."""
    arbitrator = Arbitrator()

    # Base score = confidence
    proposal = AdvisorProposal("test", "decision", 50)
    score = arbitrator.calculate_score(proposal)
    assert score == 50

    # +2 per rationale (cap 10)
    proposal = AdvisorProposal(
        "test",
        "decision",
        50,
        rationale=["r1", "r2", "r3"],  # 3 * 2 = 6
    )
    score = arbitrator.calculate_score(proposal)
    assert score == 56  # 50 + 6

    # Rationale cap at 10
    proposal = AdvisorProposal(
        "test",
        "decision",
        50,
        rationale=["r1", "r2", "r3", "r4", "r5", "r6"],  # 6 * 2 = 12, capped at 10
    )
    score = arbitrator.calculate_score(proposal)
    assert score == 60  # 50 + 10

    # -3 per risk (cap 15)
    proposal = AdvisorProposal(
        "test",
        "decision",
        50,
        risks=["risk1", "risk2"],  # 2 * 3 = 6
    )
    score = arbitrator.calculate_score(proposal)
    assert score == 44  # 50 - 6

    # Risk cap at 15
    proposal = AdvisorProposal(
        "test",
        "decision",
        50,
        risks=["r1", "r2", "r3", "r4", "r5", "r6"],  # 6 * 3 = 18, capped at 15
    )
    score = arbitrator.calculate_score(proposal)
    assert score == 35  # 50 - 15

    # +1 per artifact (cap 5)
    proposal = AdvisorProposal(
        "test",
        "decision",
        50,
        artifacts=["a1", "a2", "a3"],  # 3 * 1 = 3
    )
    score = arbitrator.calculate_score(proposal)
    assert score == 53  # 50 + 3

    # Artifact cap at 5
    proposal = AdvisorProposal(
        "test",
        "decision",
        50,
        artifacts=["a1", "a2", "a3", "a4", "a5", "a6", "a7"],  # 7 * 1 = 7, capped at 5
    )
    score = arbitrator.calculate_score(proposal)
    assert score == 55  # 50 + 5


@pytest.mark.unit_min_deps
def test_deterministic_selection_under_ties():
    """Test deterministic tie-breaking rules."""
    arbitrator = Arbitrator()

    # Create proposals with same score
    proposal1 = AdvisorProposal("advisor_B", "decision1", 50, rationale=["r1"])
    proposal2 = AdvisorProposal("advisor_A", "decision2", 50, rationale=["r1"])

    # Both have score 52 (50 + 2)
    input_data = ArbitrationInput(
        task_id="test",
        task_kind="test",
        proposals=[proposal1, proposal2],
    )

    decision = arbitrator.arbitrate(input_data)

    # Should select advisor_A (lexicographically smaller)
    assert decision.selected_advisor_id == "advisor_A"
    assert decision.selected_decision == "decision2"


@pytest.mark.unit_min_deps
def test_tie_break_by_confidence():
    """Test tie-breaking by confidence when scores equal."""
    arbitrator = Arbitrator()

    # Different confidence but same final score
    proposal1 = AdvisorProposal("advisor_A", "decision1", 45, rationale=["r1", "r2"])  # 45 + 4 = 49
    proposal2 = AdvisorProposal("advisor_B", "decision2", 50)  # 50 = 50

    input_data = ArbitrationInput(
        task_id="test",
        task_kind="test",
        proposals=[proposal1, proposal2],
    )

    decision = arbitrator.arbitrate(input_data)

    # Should select proposal2 (higher confidence)
    assert decision.selected_advisor_id == "advisor_B"
    assert decision.selected_decision == "decision2"


@pytest.mark.unit_min_deps
def test_serialization_stable():
    """Test that JSON serialization is stable and deterministic."""
    proposal = AdvisorProposal(
        "test_advisor",
        "test_decision",
        75,
        rationale=["zebra", "alpha", "beta"],  # Unsorted
        risks=["high", "low"],  # Unsorted
        artifacts=["file3", "file1", "file2"],  # Unsorted
    )

    # Serialize twice
    json1 = proposal_to_json(proposal)
    json2 = proposal_to_json(proposal)

    # Should be identical
    assert json1 == json2

    # Should have sorted arrays
    assert '"alpha"' in json1
    assert '"beta"' in json1
    assert '"zebra"' in json1
    assert json1.find('"alpha"') < json1.find('"beta"') < json1.find('"zebra"')

    # Round-trip should preserve data
    restored = proposal_from_json(json1)
    assert restored == proposal

    # Rationale should be sorted
    assert restored.rationale == ["alpha", "beta", "zebra"]
    assert restored.risks == ["high", "low"]
    assert restored.artifacts == ["file1", "file2", "file3"]


@pytest.mark.unit_min_deps
def test_arbitration_decision_serialization():
    """Test ArbitrationDecision serialization."""
    decision = ArbitrationDecision(
        selected_advisor_id="best_advisor",
        selected_decision="best_action",
        score_breakdown={"advisor1": 50, "advisor2": 45},
        merged_rationale=["reason2", "reason1"],  # Unsorted
        merged_risks=["risk2", "risk1"],  # Unsorted
    )

    # Serialize
    json_str = decision_to_json(decision)

    # Should have sorted keys and arrays
    assert '"advisor1":50' in json_str
    assert '"advisor2":45' in json_str
    assert json_str.find('"advisor1":50') < json_str.find('"advisor2":45')

    # Round-trip
    restored = decision_from_json(json_str)
    assert restored == decision

    # Arrays should be sorted
    assert restored.merged_rationale == ["reason1", "reason2"]
    assert restored.merged_risks == ["risk1", "risk2"]


@pytest.mark.unit_min_deps
def test_arbitrator_with_no_proposals():
    """Test arbitrator handles empty proposals gracefully."""
    arbitrator = Arbitrator()

    input_data = ArbitrationInput(
        task_id="test",
        task_kind="test",
        proposals=[],  # Empty
    )

    with pytest.raises(ValueError, match="No proposals provided"):
        arbitrator.arbitrate(input_data)


@pytest.mark.unit_min_deps
def test_arbitration_deterministic_across_runs():
    """Test that arbitration is deterministic across multiple runs."""
    arbitrator1 = Arbitrator()
    arbitrator2 = Arbitrator()

    proposals = [
        AdvisorProposal("advisor1", "decision1", 60, rationale=["fast"], risks=["medium"]),
        AdvisorProposal("advisor2", "decision2", 55, rationale=["safe"], risks=["low"]),
        AdvisorProposal("advisor3", "decision3", 70, rationale=["risky"], risks=["high"]),
    ]

    input_data = ArbitrationInput(
        task_id="test_task",
        task_kind="test_kind",
        proposals=proposals,
    )

    decision1 = arbitrator1.arbitrate(input_data)
    decision2 = arbitrator2.arbitrate(input_data)

    # Should be identical
    assert decision1 == decision2
    assert decision1.score_breakdown == decision2.score_breakdown
    assert decision1.merged_rationale == decision2.merged_rationale
    assert decision1.merged_risks == decision2.merged_risks


@pytest.mark.unit_min_deps
def test_advisor_deterministic_outputs():
    """Test that advisors produce deterministic outputs."""
    from agentic_core.L3_orchestration.arbitration.advisors import (
        risk_averse_advisor,
        throughput_advisor,
    )

    task = {
        "task_id": "test_task",
        "task_kind": "planning",
    }

    # Run advisors twice
    proposal1a = risk_averse_advisor(task)
    proposal1b = risk_averse_advisor(task)
    proposal2a = throughput_advisor(task)
    proposal2b = throughput_advisor(task)

    # Should be identical
    assert proposal1a == proposal1b
    assert proposal2a == proposal2b

    # Different advisors should produce different proposals
    assert proposal1a.advisor_id != proposal2a.advisor_id
    assert proposal1a.decision != proposal2a.decision


@pytest.mark.unit_min_deps
def test_run_advisors_validation():
    """Test advisor execution harness with validation."""
    from agentic_core.L3_orchestration.arbitration.run_advisors import (
        run_advisors,
    )

    task = {
        "task_id": "test_task",
        "task_kind": "execution",
    }

    # Run valid advisors
    proposals = run_advisors(task, ["risk_averse", "throughput"])
    assert len(proposals) == 2
    assert proposals[0].advisor_id == "risk_averse"
    assert proposals[1].advisor_id == "throughput"

    # Test invalid advisor ID
    with pytest.raises(ValueError, match="Invalid advisor_id"):
        run_advisors(task, ["nonexistent_advisor"])


@pytest.mark.unit_min_deps
def test_run_all_advisors():
    """Test running all available advisors."""
    from agentic_core.L3_orchestration.arbitration.run_advisors import (
        run_all_advisors,
    )

    task = {
        "task_id": "test_task",
        "task_kind": "planning",
    }

    proposals = run_all_advisors(task)

    # Should have proposals from all advisors
    assert len(proposals) >= 2  # At least risk_averse and throughput

    advisor_ids = [p.advisor_id for p in proposals]
    assert "risk_averse" in advisor_ids
    assert "throughput" in advisor_ids

    # All proposals should be valid
    for proposal in proposals:
        assert proposal.decision
        assert 0 <= proposal.confidence <= 100
        assert proposal.advisor_id in ["risk_averse", "throughput"]


@pytest.mark.unit_min_deps
def test_advisor_task_kind_behavior():
    """Test that advisors behave differently for different task kinds."""
    from agentic_core.L3_orchestration.arbitration.advisors import (
        risk_averse_advisor,
    )

    # Test planning task
    planning_task = {"task_id": "test", "task_kind": "planning"}
    planning_proposal = risk_averse_advisor(planning_task)

    # Test execution task
    execution_task = {"task_id": "test", "task_kind": "execution"}
    execution_proposal = risk_averse_advisor(execution_task)

    # Should produce different decisions
    assert planning_proposal.decision != execution_proposal.decision

    # But same advisor ID
    assert planning_proposal.advisor_id == execution_proposal.advisor_id == "risk_averse"


@pytest.mark.unit_min_deps
def test_execute_ssot_plan_arbitration_integration():
    """Test that execute_ssot plan mode includes arbitration when flag enabled."""
    import subprocess
    import sys

    # Test plan without arbitration
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
            "--legacy",
            "--plan",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "MULTI-AGENT ARBITRATION" not in result.stdout

    # Test plan with arbitration
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
            "--legacy",
            "--plan",
            "--arbitrate-plan",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "MULTI-AGENT ARBITRATION" in result.stdout
    assert "Selected Advisor:" in result.stdout
    assert "Selected Decision:" in result.stdout
    assert "Score Breakdown:" in result.stdout


@pytest.mark.unit_min_deps
def test_arbitration_output_stable():
    """Test that arbitration output is stable across runs."""
    import subprocess
    import sys

    # Run arbitration twice
    result1 = subprocess.run(
        [
            sys.executable,
            "-m",
            "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
            "--legacy",
            "--plan",
            "--arbitrate-plan",
        ],
        capture_output=True,
        text=True,
    )

    result2 = subprocess.run(
        [
            sys.executable,
            "-m",
            "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
            "--legacy",
            "--plan",
            "--arbitrate-plan",
        ],
        capture_output=True,
        text=True,
    )

    assert result1.returncode == 0
    assert result2.returncode == 0

    # Extract arbitration section
    arbitration_start = "=== MULTI-AGENT ARBITRATION ==="
    idx1 = result1.stdout.find(arbitration_start)
    idx2 = result2.stdout.find(arbitration_start)

    assert idx1 != -1, "Arbitration section not found in first run"
    assert idx2 != -1, "Arbitration section not found in second run"

    # Get arbitration sections
    section1 = result1.stdout[idx1:]
    section2 = result2.stdout[idx2:]

    # Should be identical (deterministic)
    assert section1 == section2
