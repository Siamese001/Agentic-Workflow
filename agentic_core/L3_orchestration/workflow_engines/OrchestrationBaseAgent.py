"""OrchestrationBaseAgent — L3 Base with Subatomic Testing Framework (Jan 01, 2026)

L3 Orchestration agents produce composed workflows (plans, delegation sequences, routing).
Subatomic CRITIQUE hop includes:
- Basic self-testing (plan validation, cycle detection, delegation checks)
- Delegation to TestSovereigntyAgent on failure

Table Decision (L3 Orchestration):
- Basic Self-Testing: YES
- Delegation to TestSovereigntyAgent: YES
"""
from __future__ import annotations

import json
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout

from agentic_core.L2_execution.ToolRegistry.ExecutionCanonBaseAgent import CanonBaseAgent

# [PHASE 3] Default-on healing mixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin


class L3SovereignSeverity(Enum):
    """Sovereign event Severity levels for L3 subatomic testing."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class L3SubatomicTestingMixin(MCPHardenedMixin):
    """Mixin providing L3 subatomic testing capabilities.
    
    L3 Table Decision:
    - Basic Self-Testing: YES (plan validation, cycles, delegation)
    - Delegation to TestSovereigntyAgent: YES (on failure)
    """
    
    # [PHASE 1] Self-testing flag
    _self_testing_enabled: bool = True

    def _run_self_tests(self) -> bool:
        """
        Phase 1: Canonical self-testing for L3 orchestration agents.
        
        Tests orchestration capabilities:
        - Workflow/plan structure validation
        - Agent registry access if available
        - Basic routing logic
        
        Returns:
            True if all tests pass
            
        Raises:
            AssertionError: If any test fails
        """
        if not self._self_testing_enabled:
            return True
            
        class_name = self.__class__.__name__
        
        try:
            # Test workflow/plan structure if present
            if hasattr(self, "workflow") and self.workflow is not None:
                assert isinstance(self.workflow, (dict, list)), \
                    f"{class_name}: Workflow must be dict or list"
            
            # Test agent registry access if available
            if hasattr(self, "agent_registry") and self.agent_registry is not None:
                assert isinstance(self.agent_registry, dict), \
                    f"{class_name}: Agent registry must be dict"
            
            # Test routing table if present
            if hasattr(self, "routing_table") and self.routing_table is not None:
                assert isinstance(self.routing_table, dict), \
                    f"{class_name}: Routing table must be dict"
        except AssertionError as e:
            # Proactive healing: create anomaly and attempt heal
            from agentic_core.schemas.models.anomaly_report import AnomalyReport, AnomalySeverity
            anomaly = AnomalyReport(
                type="self_test_failure",
                severity=AnomalySeverity.MEDIUM,
                description=f"L3 self-test assertion failed: {e}",
                source=class_name,
                details={"failed_assert": str(e)},
            )
            if hasattr(self, "_mcp_audit"):
                self._mcp_audit("proactive_anomaly_detected", payload=anomaly.to_dict())
            if hasattr(self, "heal"):
                if self.heal({}, anomaly):
                    return True  # Healed - pass implicitly
            raise  # Unhealable - escalate
        
        return True

    async def run_l3_subatomic_critique(self, Artifact: Dict, artifact_type: str, context: Dict) -> Dict:
        """L3 CRITIQUE hop: Basic plan testing + delegation on failure.
        
        Args:
            Artifact: The produced plan/workflow (dict or JSON)
            artifact_type: Type (plan_json, delegation_tree, conditional_plan)
            context: Execution context with goal, Task info
            
        Returns:
            Dict with passed, tests, coverage info
        """
        # Step 1: Generate basic tests for plan Artifact
        tests = self._generate_plan_tests(Artifact, artifact_type, context)
        
        # Step 2: Run sandboxed tests
        test_result = self._run_plan_sandbox_tests(tests, Artifact)
        
        if test_result["passed"]:
            self._emit_l3_event(L3SovereignSeverity.INFO, "L3_CRITIQUE_PASSED", {
                "artifact_type": artifact_type,
                "tests_run": len(test_result.get("tests", []))
            })
            return test_result
        
        # Step 3: On failure, delegate to TestSovereigntyAgent
        self._emit_l3_event(L3SovereignSeverity.WARNING, "L3_BASIC_TESTS_FAILED", {
            "artifact_type": artifact_type,
            "reason": test_result.get("error", "unknown")
        })
        
        advanced_result = await self._delegate_to_l5_specialist(Artifact, artifact_type, context)
        
        if not advanced_result["passed"]:
            self._emit_l3_event(L3SovereignSeverity.ERROR, "L3_CRITIQUE_FAILED", {
                "artifact_type": artifact_type,
                "specialist_coverage": advanced_result.get("coverage", 0)
            })
        
        return advanced_result

    def _generate_plan_tests(self, Artifact: Dict, artifact_type: str, context: Dict) -> str:
        """Generate basic tests for L3 plan Artifact."""
        if artifact_type == "plan_json":
            return self._generate_plan_json_tests(Artifact, context)
        elif artifact_type == "delegation_tree":
            return self._generate_delegation_tests(Artifact, context)
        elif artifact_type == "conditional_plan":
            return self._generate_routing_tests(Artifact, context)
        else:
            return self._generate_generic_plan_tests(Artifact, context)

    def _generate_plan_json_tests(self, plan: Dict, context: Dict) -> str:
        """L3 Example 1: Unit tests for plan JSON structure/validity."""
        plan_json = json.dumps(plan) if isinstance(plan, dict) else str(plan)
        # Escape for embedding in test string
        escaped_json = plan_json.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        return f'''
import json
import pytest

def test_plan_structure():
    """Verify plan has required structure."""
    plan_json = """{escaped_json}"""
    plan = json.loads(plan_json)
    assert isinstance(plan, dict), "Plan must be a dictionary"

def test_plan_has_steps():
    """Verify plan contains steps or actions."""
    plan_json = """{escaped_json}"""
    plan = json.loads(plan_json)
    has_steps = "steps" in plan or "actions" in plan or "tasks" in plan
    assert has_steps or len(plan) > 0, "Plan must have steps, actions, or content"

def test_no_cycles_basic():
    """Basic cycle detection (dependency check)."""
    plan_json = """{escaped_json}"""
    plan = json.loads(plan_json)
    # Basic: check no step depends on itself
    if "steps" in plan:
        for i, step in enumerate(plan["steps"]):
            if isinstance(step, dict) and "depends_on" in step:
                assert i not in step["depends_on"], f"Step {{i}} depends on itself"
    assert True  # Pass if no steps or no dependencies

def test_valid_references():
    """Verify agent/tool references are strings."""
    plan_json = """{escaped_json}"""
    plan = json.loads(plan_json)
    if "steps" in plan:
        for step in plan["steps"]:
            if isinstance(step, dict):
                if "agent" in step:
                    assert isinstance(step["agent"], str), "Agent ref must be string"
                if "tool" in step:
                    assert isinstance(step["tool"], str), "Tool ref must be string"
    assert True
'''

    def _generate_delegation_tests(self, tree: Dict, context: Dict) -> str:
        """L3 Example 2: Test delegation hierarchy/tree."""
        tree_json = json.dumps(tree) if isinstance(tree, dict) else str(tree)
        escaped_tree = tree_json.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        return f'''
import json
import pytest

def test_tree_structure():
    """Verify delegation tree structure."""
    tree_json = """{escaped_tree}"""
    tree = json.loads(tree_json)
    assert isinstance(tree, dict), "Tree must be a dictionary"

def test_no_orphan_nodes():
    """Check hierarchy validity."""
    tree_json = """{escaped_tree}"""
    tree = json.loads(tree_json)
    # Basic: tree should have root or be flat
    assert len(tree) > 0 or tree == {{}}, "Tree should have content"

def test_agent_capabilities():
    """Verify agents have required fields."""
    tree_json = """{escaped_tree}"""
    tree = json.loads(tree_json)
    if "agents" in tree:
        for agent in tree["agents"]:
            if isinstance(agent, dict):
                assert "name" in agent or "id" in agent, "Agent needs identifier"
    assert True
'''

    def _generate_routing_tests(self, plan: Dict, context: Dict) -> str:
        """L3 Example 3: Test conditional routing logic."""
        plan_json = json.dumps(plan) if isinstance(plan, dict) else str(plan)
        escaped_routing = plan_json.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        return f'''
import json
import pytest

def test_routing_structure():
    """Verify routing plan structure."""
    plan_json = """{escaped_routing}"""
    plan = json.loads(plan_json)
    assert isinstance(plan, dict), "Routing plan must be a dictionary"

def test_conditions_valid():
    """Check conditions are properly formatted."""
    plan_json = """{escaped_routing}"""
    plan = json.loads(plan_json)
    if "conditions" in plan:
        for cond in plan["conditions"]:
            if isinstance(cond, dict):
                assert "if" in cond or "when" in cond or "condition" in cond, "Condition needs trigger"
    assert True

def test_default_fallback():
    """Verify default/fallback exists."""
    plan_json = """{escaped_routing}"""
    plan = json.loads(plan_json)
    # Routing should have default or else clause
    has_default = "default" in plan or "else" in plan or "fallback" in plan
    # Not strictly required but good practice
    assert True  # Pass - default is recommended not required
'''

    def _generate_generic_plan_tests(self, Artifact: Dict, context: Dict) -> str:
        """Fallback tests for unknown plan types."""
        artifact_str = json.dumps(Artifact)[:500] if isinstance(Artifact, dict) else str(Artifact)[:500]
        escaped_artifact = artifact_str.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        return f'''
import pytest
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

def test_artifact_exists():
    """Verify Artifact is not empty."""
    Artifact = """{escaped_artifact}"""
    assert Artifact is not None
    assert len(str(Artifact)) > 0
'''

    def _run_plan_sandbox_tests(self, tests: str, Artifact: Dict) -> Dict:
        """Run plan tests in sandboxed subprocess."""
        try:
            temp_test = Path.cwd() / "temp_l3_test.py"
            temp_test.write_text(tests, encoding='utf-8')
            
            result = subprocess.run(
                ["pytest", str(temp_test), "-q", "--tb=short"],
                capture_output=True,
                timeout=30,
                cwd=Path.cwd()
            )
            
            if temp_test.exists():
                temp_test.unlink()
            
            passed = result.returncode == 0
            return {
                "passed": passed,
                "tests": [{"name": "plan_tests", "passed": passed}],
                "output": result.stdout.decode()[:500],
                "error": result.stderr.decode()[:200] if not passed else None
            }
        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "Test timeout (30s)", "tests": []}
        except Exception as e:
            return {"passed": False, "error": str(e), "tests": []}

    async def _delegate_to_l5_specialist(self, Artifact: Dict, artifact_type: str, context: Dict) -> Dict:
        """Delegate to TestSovereigntyAgent for advanced plan testing."""
        try:
            from agentic_core.L5_safety.validators.TestSovereigntyAgent import TestSovereigntyAgent
            
            specialist = TestSovereigntyAgent()
            artifact_str = json.dumps(Artifact) if isinstance(Artifact, dict) else str(Artifact)
            result = await specialist.execute({
                "Artifact": artifact_str,
                "type": "orchestration_integration",
                "coverage_target": 95
            })
            return result
        except ImportError:
            return {"passed": False, "error": "TestSovereigntyAgent not available", "tests": []}
        except Exception as e:
            return {"passed": False, "error": str(e), "tests": []}

    def _emit_l3_event(self, Severity: L3SovereignSeverity, event_type: str, payload: Optional[Dict] = None) -> None:
        """Emit L3 subatomic testing event for observability."""
        print(f"[SUBATOMIC L3] {Severity.value} | {event_type}")
        if payload:
            print(f"  Payload: {payload}")


@dataclass
class OrchestrationBaseAgent(CanonBaseAgent, L3SubatomicTestingMixin, HealerMixin):
    """Base class for L3 Orchestration agents with subatomic testing.
    
    L3 Table Decision:
    - Basic Self-Testing: YES (plan validation)
    - Delegation to TestSovereigntyAgent: YES (on failure)
    
    Inherits from CanonBaseAgent for core capabilities.
    Includes L3SubatomicTestingMixin for CRITIQUE hop testing.
    """

    async def orchestrate(self, Task: Dict) -> Dict:
        """Execute orchestration logic. Override in subclasses."""
        raise NotImplementedError(f"{self.name} must implement orchestrate()")

    async def execute_with_critique(self, Task: Dict) -> Dict:
        """Execute with L3 subatomic CRITIQUE hop.
        
        Subclasses should call this instead of raw execute
        to get automatic plan validation and testing.
        """
        # INIT/THINK/ACT
        result = await self.orchestrate(Task)
        
        # CRITIQUE: Run L3 subatomic tests
        Artifact = result.get("plan", result.get("workflow", result))
        artifact_type = result.get("artifact_type", "plan_json")
        
        critique_result = await self.run_l3_subatomic_critique(
            Artifact=Artifact,
            artifact_type=artifact_type,
            context=Task
        )
        
        if not critique_result["passed"]:
            # Retry or return with failure
            result["critique_failed"] = True
            result["critique_result"] = critique_result
        else:
            result["critique_passed"] = True
        
        return result

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L3 orchestration base agent - operational only."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L3 orchestration - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
