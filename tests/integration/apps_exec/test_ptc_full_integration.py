"""PTC Integration Tests

Comprehensive integration tests for Programmatic Tool Calling system.
Tests all components working together: orchestrator, safety gates, HITL, sandbox.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

import pytest

# Check if PTC modules are available
try:
    from agentic_core.L2_execution.utils.ptc_contract import (
        PTC_STDOUT_BYTE_CAP,
        PTCBytesCapExceeded,
        PTCContractEnforcer,
        PTCContractViolation,
        PTCUnsignedEnvelopeError,
        redact_output,
    )
    from agentic_core.L2_execution.types.ptc_tool_contracts_types import (
        ToolCall,
        ToolContractViolation,
        ToolResult,
    )
    from agentic_core.L2_execution.types.sandbox_envelope_types import SandboxEnvelope
    from agentic_core.L3_orchestration.reasoning.ptc.builtin_tools import expr_eval_handler, repo_rg_handler
    from agentic_core.L3_orchestration.reasoning.ptc.ptc_hitl_integration import (
        PTCHITLIntegration,
        PTCHumanDecision,
        PTCHumanReviewRecord,
        PTCSafetyAssessment,
        PTCSafetyGateResult,
        PTCScriptRiskLevel,
        assess_ptc_script_safety,
        generate_ptc_dpo_pair,
        get_ptc_hitl_integration,
        perform_ptc_l5_reclear,
        request_ptc_human_review,
        reset_ptc_hitl_integration,
    )
    from agentic_core.L3_orchestration.reasoning.ptc.ptc_orchestrator import (
        PTCExecutionResult,
        PTCOrchestrator,
        PTCSandboxContext,
        PTCSandboxExecutor,
        PTCScriptPlan,
        execute_in_ptc_sandbox,
        execute_ptc_batch,
        get_ptc_orchestrator,
        get_ptc_sandbox,
        parse_ptc_script,
        reset_ptc_orchestrator,
        reset_ptc_sandbox,
    )
    from agentic_core.L3_orchestration.reasoning.ptc.ptc_registry import (
        ToolRegistry,
        get_global_registry,
        register_tool,
    )
    from agentic_core.L3_orchestration.reasoning.ptc.ptc_safety_gates import (
        PTCConfidenceGate,
        PTCExecutionGate,
        PTCRoutingGate,
        PTCSafetyGateManager,
        PTCSafetyGateResult,
        PTCSafetyGateStatus,
        PTCSafetyGateType,
        PTCSafetyGateViolation,
        PTCValidationGate,
        check_ptc_safety_passed,
        evaluate_ptc_safety_gates,
        get_ptc_safety_gate_manager,
        reset_ptc_safety_gate_manager,
    )
    from agentic_core.L3_orchestration.reasoning.ptc.tool_call_store import (
        ToolCallStore,
        get_tool_call_store,
        record_tool_call,
    )
    from agentic_core.L3_orchestration.reasoning.ptc.tool_contract import (
        ToolArg,
        ToolCallResult,
        ToolSpec,
        canonical_json,
        generate_call_id,
        hash_result_data,
    )
    from agentic_core.L3_orchestration.reasoning.ptc.tool_contract import (
        ToolCall as PTCToolCall,
    )
    from agentic_core.L3_orchestration.reasoning.ptc.tool_invoker import ToolInvoker
    from agentic_core.L3_orchestration.types.human_decision_artifact_types import (
        HumanAction,
        create_approval_artifact,
        create_human_review_draft,
        create_rejection_artifact,
    )
    from agentic_core.L5_safety.hitl.hitl_escalation_activator import (
        EscalationPriority,
        EscalationRequest,
        HITLEscalationActivator,
        get_hitl_escalation_activator,
        reset_hitl_escalation_activator,
    )
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        LayerSegment,
        _emit_records_execution_trace,
        _emit_records_tool_invocation,
        emit_determinism_digest,
        emit_replay_key,
    )
    PTC_AVAILABLE = True
except ImportError:
    PTC_AVAILABLE = False


# PTC Core imports


# PTC Orchestration imports


# PTC New Components


# HITL imports


# Lifecycle trace imports


# Constants
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def reset_all_global_state():
    """Reset all global state before each test."""
    reset_ptc_orchestrator()
    reset_ptc_sandbox()
    reset_ptc_hitl_integration()
    reset_ptc_safety_gate_manager()
    reset_hitl_escalation_activator()
    yield


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide temporary directory."""
    return tmp_path


@pytest.fixture
def ptc_orchestrator() -> PTCOrchestrator:
    """Provide fresh PTC orchestrator."""
    return PTCOrchestrator()


@pytest.fixture
def ptc_sandbox() -> PTCSandboxExecutor:
    """Provide fresh PTC sandbox."""
    return PTCSandboxExecutor()


@pytest.fixture
def ptc_hitl() -> PTCHITLIntegration:
    """Provide fresh PTC HITL integration."""
    return PTCHITLIntegration()


@pytest.fixture
def ptc_safety_manager() -> PTCSafetyGateManager:
    """Provide fresh PTC safety gate manager."""
    return PTCSafetyGateManager()


@pytest.fixture
def ptc_enforcer() -> PTCContractEnforcer:
    """Provide PTC contract enforcer with key source injected."""
    from agentic_core.L2_execution.enforcement.key_source import TestKeySource, inject_key_source
    inject_key_source(TestKeySource())
    return PTCContractEnforcer(secret=TestKeySource.TEST_SECRET)


@pytest.fixture
def tool_registry() -> ToolRegistry:
    """Provide fresh tool registry."""
    registry = ToolRegistry()
    registry._specs.clear()
    registry._handlers.clear()
    return registry


@pytest.fixture
def escalation_activator():
    """Provide fresh escalation activator."""
    reset_hitl_escalation_activator()
    return get_hitl_escalation_activator()


# =============================================================================
# Test Class: PTC End-to-End Integration
# =============================================================================

@pytest.mark.skipif(not PTC_AVAILABLE, reason="PTC modules not available")
class TestPTCEndToEndIntegration:
    """End-to-end integration tests for PTC system."""

    def test_ptc_full_workflow_approve(
        self,
        ptc_orchestrator: PTCOrchestrator,
        ptc_hitl: PTCHITLIntegration,
        ptc_safety_manager: PTCSafetyGateManager,
        tool_registry: ToolRegistry,
        escalation_activator,
    ) -> None:
        """Test complete PTC workflow with APPROVE decision."""
        script_id = f"ptc-e2e-approve-{uuid.uuid4().hex[:8]}"

        # Stage 1: Register tools
        query_spec = ToolSpec(
            tool_id="query_users",
            description="Query users table",
            side_effect_class="READONLY",
            args=(ToolArg("filter", "str", False, default=""),),
            output_kind="JSON",
            version=1,
        )

        def query_handler(args: dict[str, Any]) -> dict[str, Any]:
            return {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}], "count": 2}

        tool_registry.register(query_spec, query_handler)
        ptc_orchestrator.register_tool("query_users", query_handler)

        # Stage 2: Create and parse script
        code = """
users = query_users()
summary = {"count": users["count"], "names": [u["name"] for u in users["users"]]}
print(json.dumps(summary))
"""
        plan = ptc_orchestrator.parse_script(script_id, code)

        assert len(plan.tools) == 1
        assert "query_users" in plan.tools

        # Stage 3: Safety assessment
        assessment = ptc_hitl.assess_script_safety(
            script_id=script_id,
            code=code,
            tools=plan.tools,
        )

        assert assessment.risk_level == PTCScriptRiskLevel.LOW
        assert assessment.confidence_score > 0.7

        # Stage 4: Safety gates
        gate_results = ptc_safety_manager.evaluate_all_gates(
            script_id=script_id,
            confidence_score=assessment.confidence_score,
            risk_level=assessment.risk_level.value,
            policy_compliant=len(assessment.policy_violations) == 0,
            detected_patterns=list(assessment.detected_patterns),
            code=code,
            envelope_signed=True,
            envelope_valid=True,
        )

        assert ptc_safety_manager.check_all_passed(gate_results)
        assert not ptc_safety_manager.requires_human_review(gate_results)

        # Stage 5: Execute batch
        result = ptc_orchestrator.execute_batch(plan)

        assert result.success
        assert "count" in result.summary
        assert result.tokens_saved > 0

        # Stage 6: Verify in sandbox
        sandbox = PTCSandboxExecutor()
        ctx, output = sandbox.execute_in_sandbox(code, {"query_users": query_handler})

        assert ctx.isolated
        assert len(ctx.raw_results) == 1
        assert "count" in output

    def test_ptc_full_workflow_with_hitl_review(
        self,
        ptc_orchestrator: PTCOrchestrator,
        ptc_hitl: PTCHITLIntegration,
        ptc_safety_manager: PTCSafetyGateManager,
        escalation_activator,
    ) -> None:
        """Test PTC workflow requiring human review."""
        script_id = f"ptc-hitl-{uuid.uuid4().hex[:8]}"

        # Create high-risk script
        code = """
# High-risk: file write operation
with open("sensitive.txt", "w") as f:
    f.write("sensitive data")
result = {"status": "written"}
print(json.dumps(result))
"""

        # Parse and assess
        plan = ptc_orchestrator.parse_script(script_id, code)
        assessment = ptc_hitl.assess_script_safety(script_id, code, plan.tools)

        # Should detect high risk
        assert assessment.risk_level in (PTCScriptRiskLevel.HIGH, PTCScriptRiskLevel.CRITICAL)
        assert assessment.requires_human_review

        # Safety gates should require review
        gate_results = ptc_safety_manager.evaluate_all_gates(
            script_id=script_id,
            confidence_score=0.3,  # Low confidence
            risk_level=assessment.risk_level.value,
            policy_compliant=False,
            detected_patterns=list(assessment.detected_patterns),
            code=code,
            envelope_signed=True,
            envelope_valid=True,
        )

        assert ptc_safety_manager.requires_human_review(gate_results)

        # Request human review
        review = ptc_hitl.request_human_review(assessment)

        # For high-risk with file write, should be MODIFY_DIFF or REJECT
        assert review.decision in (PTCHumanDecision.MODIFY_DIFF, PTCHumanDecision.REJECT)

    def test_ptc_safety_gate_fail_closed(
        self,
        ptc_safety_manager: PTCSafetyGateManager,
    ) -> None:
        """Test PTC safety gate fail-closed behavior."""
        script_id = f"ptc-fail-{uuid.uuid4().hex[:8]}"

        execution_gate = PTCExecutionGate()

        # Unsigned envelope should fail-closed
        with pytest.raises(PTCSafetyGateViolation) as exc_info:
            execution_gate.evaluate_pre_execution(
                script_id=script_id,
                envelope_signed=False,
                envelope_valid=False,
            )
        assert "unsigned" in str(exc_info.value).lower()

        # Valid envelope should pass
        result = execution_gate.evaluate_pre_execution(
            script_id=script_id,
            envelope_signed=True,
            envelope_valid=True,
        )
        assert result.passed

    def test_ptc_token_savings_calculation(
        self,
        ptc_orchestrator: PTCOrchestrator,
    ) -> None:
        """Test PTC token savings calculation."""
        # Script with 5 tools
        code = """
result1 = tool_a()
result2 = tool_b()
result3 = tool_c()
result4 = tool_d()
result5 = tool_e()
print(json.dumps({"done": True}))
"""

        plan = ptc_orchestrator.parse_script("savings-test", code)

        # Should estimate savings
        assert plan.estimated_tokens > 0

        # With mock handlers
        handlers = {
            "tool_a": lambda _: {"result": "a"},
            "tool_b": lambda _: {"result": "b"},
            "tool_c": lambda _: {"result": "c"},
            "tool_d": lambda _: {"result": "d"},
            "tool_e": lambda _: {"result": "e"},
        }

        result = ptc_orchestrator.execute_batch(plan, handlers)

        # Should report token savings
        assert result.tokens_saved >= 0

        # 5 tools batched vs 5 separate inferences should save tokens
        assert result.tokens_saved > 0

    def test_ptc_context_isolation_integrity(
        self,
        ptc_sandbox: PTCSandboxExecutor,
    ) -> None:
        """Test PTC context isolation preserves raw results in sandbox."""
        code = "query_database('SELECT * FROM large_table')"

        def mock_query(_):
            return {"rows": [{"id": i, "data": "x" * 1000} for i in range(100)]}

        ctx, output = ptc_sandbox.execute_in_sandbox(
            code,
            {"query_database": mock_query}
        )

        # Raw results should be trapped
        assert len(ctx.raw_results) == 1
        raw_result = ctx.raw_results["query_database"]
        assert "rows" in raw_result
        assert len(raw_result["rows"]) == 100

        # Output should be small summary
        assert len(output) < 1000
        parsed = json.loads(output)
        assert "executed" in parsed

    def test_ptc_orchestrator_and_safety_integration(
        self,
        ptc_orchestrator: PTCOrchestrator,
        ptc_safety_manager: PTCSafetyGateManager,
    ) -> None:
        """Test PTC orchestrator integration with safety gates."""
        script_id = "integration-test"

        # Parse script
        code = "safe_query()"
        plan = ptc_orchestrator.parse_script(script_id, code)

        # Evaluate gates
        results = ptc_safety_manager.evaluate_all_gates(
            script_id=script_id,
            confidence_score=0.9,
            risk_level="low",
            policy_compliant=True,
            detected_patterns=[],
            code=code,
            envelope_signed=True,
            envelope_valid=True,
        )

        # If gates pass, execute
        if ptc_safety_manager.check_all_passed(results):
            result = ptc_orchestrator.execute_batch(plan, {
                "safe_query": lambda _: {"status": "ok"}
            })
            assert result.success

        # Check statistics
        stats = ptc_safety_manager.get_statistics()
        assert stats["total_evaluations"] == 4  # 4 gates

    def test_ptc_hitl_and_safety_integration(
        self,
        ptc_hitl: PTCHITLIntegration,
        ptc_safety_manager: PTCSafetyGateManager,
    ) -> None:
        """Test PTC HITL integration with safety gates."""
        script_id = "hitl-safety-test"
        code = "risky_operation()"

        # Assess safety
        assessment = ptc_hitl.assess_script_safety(
            script_id=script_id,
            code=code,
            tools=["risky_operation"],
        )

        # Evaluate gates with assessment
        results = ptc_safety_manager.evaluate_all_gates(
            script_id=script_id,
            confidence_score=assessment.confidence_score,
            risk_level=assessment.risk_level.value,
            policy_compliant=len(assessment.policy_violations) == 0,
            detected_patterns=list(assessment.detected_patterns),
            code=code,
            envelope_signed=True,
            envelope_valid=True,
        )

        # If review required, process through HITL
        if ptc_safety_manager.requires_human_review(results):
            review = ptc_hitl.request_human_review(assessment)

            # Generate DPO pair
            dpo_pair = ptc_hitl.generate_dpo_pair(assessment, review)

            assert "human_decision" in dpo_pair
            assert "example_id" in dpo_pair

    def test_ptc_complete_safety_workflow_reject(
        self,
        ptc_orchestrator: PTCOrchestrator,
        ptc_hitl: PTCHITLIntegration,
        ptc_safety_manager: PTCSafetyGateManager,
    ) -> None:
        """Test complete PTC workflow with REJECT decision."""
        script_id = "reject-test"

        # Code with critical violations
        code = "import os; os.system('rm -rf /')"

        # Parse
        plan = ptc_orchestrator.parse_script(script_id, code)

        # Assess
        assessment = ptc_hitl.assess_script_safety(script_id, code, plan.tools)

        # Should detect critical violations
        assert assessment.risk_level == PTCScriptRiskLevel.CRITICAL
        assert len(assessment.policy_violations) > 0

        # Human review should reject
        review = ptc_hitl.request_human_review(assessment)
        assert review.decision == PTCHumanDecision.REJECT

        # DPO pair should show rejection
        dpo_pair = ptc_hitl.generate_dpo_pair(assessment, review)
        assert dpo_pair["human_decision"] == "reject"

    def test_ptc_l5_reclear_workflow(
        self,
        ptc_hitl: PTCHITLIntegration,
    ) -> None:
        """Test PTC L5 re-clear workflow for MODIFY_DIFF."""
        script_id = "l5-reclear-test"
        code = "query_with_limit('SELECT * FROM users')"

        assessment = ptc_hitl.assess_script_safety(script_id, code, ["query_with_limit"])

        # Simulate MODIFY_DIFF decision
        review = PTCHumanReviewRecord(
            script_id=script_id,
            reviewer_id="human:reviewer",
            decision=PTCHumanDecision.MODIFY_DIFF,
            rationale="Added LIMIT clause for safety",
            modified_script="query_with_limit('SELECT * FROM users LIMIT 100')",
            timestamp="2024-01-01T00:00:00",
            trace_id="test-trace",
        )

        # Perform L5 re-clear
        reclear_passed = ptc_hitl.perform_l5_reclear(review, policy_hash="sha256:policy123")

        # Should validate modified script
        assert reclear_passed is True  # With placeholder validation


# =============================================================================
# Test Class: PTC Contract Enforcement Integration
# =============================================================================

@pytest.mark.skipif(not PTC_AVAILABLE, reason="PTC modules not available")
class TestPTCContractEnforcementIntegration:
    """Integration tests for PTC contract enforcement."""

    def test_ptc_enforcer_with_sandbox(self, ptc_enforcer: PTCContractEnforcer) -> None:
        """Test PTC enforcer integration with sandbox execution."""
        # Create valid envelope (auto-signs with injected key)
        envelope = SandboxEnvelope(
            envelope_id="test-env-001",
            tool_name="test_tool",
            tool_args={"output": "hello world"},
            instruction_packet_id="test-packet",
        )

        # Pre-execute validation
        ptc_enforcer.pre_execute(envelope)

        # Simulate sandbox output
        raw_output = "API_KEY: secret123\nhello world\nPassword: pass456"

        # Post-execute with redaction
        safe_output = ptc_enforcer.post_execute(raw_output)

        # Secrets should be redacted
        assert "[REDACTED]" in safe_output
        assert "secret123" not in safe_output
        assert "pass456" not in safe_output
        assert "hello world" in safe_output

    def test_ptc_enforcer_byte_cap_fail_closed(
        self, ptc_enforcer: PTCContractEnforcer
    ) -> None:
        """Test PTC enforcer byte cap fail-closed."""
        envelope = SandboxEnvelope(
            envelope_id="test-env-002",
            tool_name="test_tool",
            tool_args={},
            instruction_packet_id="test-packet",
        )

        ptc_enforcer.pre_execute(envelope)

        # Output exceeding cap
        huge_output = "x" * (PTC_STDOUT_BYTE_CAP + 1000)

        with pytest.raises(PTCBytesCapExceeded):
            ptc_enforcer.post_execute(huge_output)


# =============================================================================
# Test Class: PTC Built-in Tools Integration
# =============================================================================

@pytest.mark.skipif(not PTC_AVAILABLE, reason="PTC modules not available")
class TestPTCBuiltinToolsIntegration:
    """Integration tests for PTC built-in tools."""

    def test_ptc_repo_rg_integration(self, temp_dir: Path) -> None:
        """Test repo_rg tool integration."""
        # Create test files
        (temp_dir / "test1.py").write_text("def hello(): pass")
        (temp_dir / "test2.py").write_text("def world(): pass")

        # Search using repo_rg
        result = repo_rg_handler({
            "pattern": r"def \w+",
            "root": str(temp_dir),
        })

        data = json.loads(result)
        assert len(data["results"]) == 2

        # Results should be sorted
        files = [r["file"] for r in data["results"]]
        assert files == sorted(files)

    def test_ptc_expr_eval_integration(self) -> None:
        """Test expr_eval tool integration."""
        # Safe expressions
        test_cases = [
            ({"expr": "2 + 2"}, "4"),
            ({"expr": "10 * 5"}, "50"),
            ({"expr": "100 / 4"}, "25.0"),
            ({"expr": "2 ** 8"}, "256"),
            ({"expr": "max(1, 5, 3)"}, "5"),
        ]

        for args, expected in test_cases:
            result = expr_eval_handler(args)
            assert result == expected

    def test_ptc_expr_eval_safety_rejection(self) -> None:
        """Test expr_eval rejects unsafe expressions."""
        unsafe_cases = [
            {"expr": "__import__('os')"},
            {"expr": "import sys"},
            {"expr": "open('file.txt')"},
            {"expr": "eval('1+1')"},
        ]

        for args in unsafe_cases:
            with pytest.raises(ValueError) as exc_info:
                expr_eval_handler(args)
            assert "unsafe" in str(exc_info.value).lower()


# =============================================================================
# Test Class: PTC Tool Registry Integration
# =============================================================================

@pytest.mark.skipif(not PTC_AVAILABLE, reason="PTC modules not available")
class TestPTCToolRegistryIntegration:
    """Integration tests for PTC tool registry."""

    def test_ptc_registry_integration_with_invoker(self) -> None:
        """Test tool registry integration with invoker."""
        registry = ToolRegistry()
        invoker = ToolInvoker()

        # Register tool
        spec = ToolSpec(
            tool_id="integrated_tool",
            description="Test integration",
            side_effect_class="PURE",
            args=(ToolArg("value", "int", True),),
            output_kind="TEXT",
            version=1,
        )

        def handler(args: dict[str, Any]) -> str:
            return str(args["value"] * 2)

        registry.register(spec, handler)

        # Invoke via invoker
        call = PTCToolCall(
            call_id="int-test-001",
            tool_id="integrated_tool",
            args={"value": 21},
        )

        result = invoker.invoke(call, registry)

        assert result.exit_code == 0
        assert "42" in result.stdout

    def test_ptc_registry_deterministic_ordering(self) -> None:
        """Test tool registry returns tools in deterministic order."""
        registry = ToolRegistry()

        # Register in random order
        for i in [5, 2, 8, 1, 9]:
            spec = ToolSpec(
                tool_id=f"tool_{i:03d}",
                description=f"Tool {i}",
                side_effect_class="PURE",
                args=(),
                output_kind="TEXT",
                version=1,
            )
            try:
                registry.register(spec, lambda x: x)
            except ValueError:
                pass

        # Should be sorted
        tools = registry.list()
        ids = [t.tool_id for t in tools]
        assert ids == sorted(ids)


# =============================================================================
# Test Class: PTC Performance Integration
# =============================================================================

@pytest.mark.skipif(not PTC_AVAILABLE, reason="PTC modules not available")
class TestPTCPerformanceIntegration:
    """Performance integration tests for PTC."""

    def test_ptc_batch_vs_sequential_performance(self) -> None:
        """Test PTC batch execution vs sequential."""
        orchestrator = PTCOrchestrator()

        # Register tools
        for i in range(5):
            orchestrator.register_tool(f"tool_{i}", lambda _: {"result": "ok"})

        # Script with 5 tools
        code = "; ".join([f"tool_{i}()" for i in range(5)])
        plan = orchestrator.parse_script("perf-test", code)

        # Time batch execution
        start = time.time()
        result = orchestrator.execute_batch(plan)
        batch_time = time.time() - start

        assert result.success
        assert batch_time < 1.0  # Should be fast

        # Verify token savings
        assert result.tokens_saved > 0

    def test_ptc_sandbox_isolation_performance(self) -> None:
        """Test PTC sandbox isolation overhead."""
        sandbox = PTCSandboxExecutor()

        def fast_tool(_):
            return {"data": "x" * 1000}

        # Execute multiple times
        times = []
        for _ in range(10):
            start = time.time()
            _, output = sandbox.execute_in_sandbox("fast_tool()", {"fast_tool": fast_tool})
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        assert avg_time < 0.1  # Should be fast

        # Verify isolation still works
        assert len(output) < len("x" * 1000)


# =============================================================================
# Lifecycle Trace Contract Compliance
# =============================================================================

emit_replay_key("p0", "test_ptc_integration")
emit_determinism_digest("p0", "test_ptc_integration")

_emit_records_execution_trace("ptc_integration", LayerSegment.L3_ORCHESTRATION, "PTCIntegrationTestSuite")
_emit_records_tool_invocation("ptc_integration", "integration_test", "test_suite")
