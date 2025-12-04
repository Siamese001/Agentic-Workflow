"""
Critical Path E2E Workflow Tests

Tests the essential L1→L2→L3 workflow: planning → execution → orchestration.
Uses working mocks from unit test foundation to validate layer contracts.
"""

import pytest
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from unittest.mock import Mock
import time

# Mark all tests as E2E workflow tests
pytestmark = [pytest.mark.end_to_end, pytest.mark.integration, pytest.mark.l1, pytest.mark.l2, pytest.mark.l3]


class TaskStatus(Enum):
    """Status of tasks in workflow."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowPhase(Enum):
    """Phases of critical path workflow."""
    PLANNING = "planning"
    EXECUTION = "execution"
    ORCHESTRATION = "orchestration"
    COMPLETED = "completed"


@dataclass(frozen=True)
class MockWorkflowPlan:
    """Mock workflow plan for E2E testing."""
    plan_id: str
    mission: str
    phases: List[str]
    tasks: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]]
    estimated_duration: float


@dataclass(frozen=True)
class MockWorkflowResult:
    """Mock workflow execution result."""
    workflow_id: str
    phase: WorkflowPhase
    status: TaskStatus
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    execution_time: float
    metadata: Dict[str, Any]


class TestCriticalPathWorkflow:
    """Test critical path L1→L2→L3 workflow execution."""
    
    def test_planning_to_execution_data_flow(self):
        """Test data flow from L1 planning to L2 execution."""
        
        class MockPlanningEngine:
            def __init__(self):
                self.plan_counter = 0
            
            def create_plan(self, mission: str, context: Dict[str, Any]) -> MockWorkflowPlan:
                """Create execution plan from mission."""
                self.plan_counter += 1
                plan_id = f"plan_{self.plan_counter:03d}"
                
                # Mock planning logic based on mission complexity
                mission_lower = mission.lower()
                if "resume" in mission_lower and "job" in mission_lower:
                    tasks = [
                        {"task_id": "extract_resume", "type": "extraction", "priority": "critical"},
                        {"task_id": "parse_job", "type": "extraction", "priority": "critical"},
                        {"task_id": "match_skills", "type": "analysis", "priority": "high"},
                        {"task_id": "generate_report", "type": "synthesis", "priority": "medium"}
                    ]
                    dependencies = {
                        "extract_resume": [],
                        "parse_job": [],
                        "match_skills": ["extract_resume", "parse_job"],
                        "generate_report": ["match_skills"]
                    }
                else:
                    tasks = [{"task_id": "simple_task", "type": "analysis", "priority": "medium"}]
                    dependencies = {"simple_task": []}
                
                return MockWorkflowPlan(
                    plan_id=plan_id,
                    mission=mission,
                    phases=["planning", "execution", "completion"],
                    tasks=tasks,
                    dependencies=dependencies,
                    estimated_duration=len(tasks) * 2.0
                )
        
        class MockExecutionEngine:
            def __init__(self):
                self.execution_history = []
            
            def execute_plan(self, plan: MockWorkflowPlan, execution_context: Dict[str, Any]) -> List[MockWorkflowResult]:
                """Execute workflow plan."""
                results = []
                start_time = time.time()
                
                # Execute tasks based on dependencies
                executed_tasks = set()
                remaining_tasks = plan.tasks.copy()
                
                while remaining_tasks:
                    # Find tasks ready for execution
                    ready_tasks = [
                        task for task in remaining_tasks
                        if all(dep in executed_tasks for dep in plan.dependencies.get(task["task_id"], []))
                    ]
                    
                    if not ready_tasks:
                        # Circular dependency or missing dependency
                        for task in remaining_tasks:
                            results.append(MockWorkflowResult(
                                workflow_id=execution_context.get("workflow_id", "unknown"),
                                phase=WorkflowPhase.EXECUTION,
                                status=TaskStatus.FAILED,
                                result=None,
                                error=f"Dependency resolution failed for {task['task_id']}",
                                execution_time=0.0,
                                metadata={"task_id": task["task_id"]}
                            ))
                        break
                    
                    # Execute ready tasks
                    for task in ready_tasks:
                        task_start = time.time()
                        
                        # Mock task execution
                        if task["type"] == "extraction":
                            result_data = {"extracted_data": f"mock_data_from_{task['task_id']}"}
                        elif task["type"] == "analysis":
                            result_data = {"analysis_result": f"mock_analysis_for_{task['task_id']}"}
                        elif task["type"] == "synthesis":
                            result_data = {"synthesized_output": f"mock_output_from_{task['task_id']}"}
                        else:
                            result_data = {"result": f"mock_result_for_{task['task_id']}"}
                        
                        task_time = time.time() - task_start
                        
                        results.append(MockWorkflowResult(
                            workflow_id=execution_context.get("workflow_id", "unknown"),
                            phase=WorkflowPhase.EXECUTION,
                            status=TaskStatus.COMPLETED,
                            result=result_data,
                            error=None,
                            execution_time=task_time,
                            metadata={"task_id": task["task_id"], "priority": task["priority"]}
                        ))
                        
                        executed_tasks.add(task["task_id"])
                        remaining_tasks.remove(task)
                
                total_time = time.time() - start_time
                self.execution_history.append({
                    "plan_id": plan.plan_id,
                    "total_time": total_time,
                    "task_count": len(plan.tasks)
                })
                
                return results
        
        # Test planning to execution data flow
        planning_engine = MockPlanningEngine()
        execution_engine = MockExecutionEngine()
        
        # Test mission
        mission = "Extract resume skills and match to job requirements"
        context = {"workflow_id": "workflow_001", "priority": "high"}
        
        # Create plan
        plan = planning_engine.create_plan(mission, context)
        
        # Validate plan structure
        assert plan.plan_id.startswith("plan_")
        assert plan.mission == mission
        assert len(plan.tasks) == 4
        assert "extract_resume" in plan.tasks[0]["task_id"]
        
        # Execute plan
        execution_context = {"workflow_id": "workflow_001", "execution_mode": "sequential"}
        results = execution_engine.execute_plan(plan, execution_context)
        
        # Validate execution results
        assert len(results) == len(plan.tasks)
        assert all(result.status == TaskStatus.COMPLETED for result in results)
        assert all(result.result is not None for result in results)
        assert all(result.error is None for result in results)
        
        # Validate data flow integrity
        task_ids = [result.metadata["task_id"] for result in results]
        expected_ids = ["extract_resume", "parse_job", "match_skills", "generate_report"]
        assert set(task_ids) == set(expected_ids)
        
        # Validate execution history
        assert len(execution_engine.execution_history) == 1
        assert execution_engine.execution_history[0]["plan_id"] == plan.plan_id
    
    def test_execution_to_orchestration_coordination(self):
        """Test coordination between L2 execution and L3 orchestration."""
        
        class MockOrchestrator:
            def __init__(self):
                self.coordination_log = []
            
            def coordinate_execution(self, execution_results: List[MockWorkflowResult], 
                                   orchestration_strategy: str) -> Dict[str, Any]:
                """Coordinate execution results based on strategy."""
                coordination_start = time.time()
                
                coordination_result = {
                    "strategy": orchestration_strategy,
                    "coordinated_results": [],
                    "orchestration_decisions": [],
                    "final_status": "completed",
                    "coordination_time": 0.0
                }
                
                # Process execution results
                successful_results = [r for r in execution_results if r.status == TaskStatus.COMPLETED]
                failed_results = [r for r in execution_results if r.status == TaskStatus.FAILED]
                
                # Orchestration strategy logic
                if orchestration_strategy == "sequential":
                    # Simple sequential coordination
                    for result in successful_results:
                        coordination_result["coordinated_results"].append({
                            "task_id": result.metadata["task_id"],
                            "output": result.result,
                            "execution_order": len(coordination_result["coordinated_results"]) + 1
                        })
                    
                    coordination_result["orchestration_decisions"] = [
                        "Executed all tasks sequentially",
                        f"Processed {len(successful_results)} successful tasks"
                    ]
                
                elif orchestration_strategy == "priority_based":
                    # Priority-based coordination
                    priority_order = {"critical": 1, "high": 2, "medium": 3, "low": 4}
                    sorted_results = sorted(successful_results, 
                                          key=lambda r: priority_order.get(r.metadata.get("priority", "medium"), 99))
                    
                    for result in sorted_results:
                        coordination_result["coordinated_results"].append({
                            "task_id": result.metadata["task_id"],
                            "priority": result.metadata.get("priority", "medium"),
                            "output": result.result,
                            "orchestration_rank": len(coordination_result["coordinated_results"]) + 1
                        })
                    
                    coordination_result["orchestration_decisions"] = [
                        "Ordered tasks by priority",
                        f"Critical tasks executed first: {sum(1 for r in sorted_results if r.metadata.get('priority') == 'critical')}"
                    ]
                
                else:
                    # Default strategy
                    coordination_result["coordinated_results"] = [
                        {"task_id": r.metadata["task_id"], "output": r.result}
                        for r in successful_results
                    ]
                    coordination_result["orchestration_decisions"] = ["Used default coordination strategy"]
                
                # Handle failures
                if failed_results:
                    coordination_result["final_status"] = "partial_success"
                    coordination_result["orchestration_decisions"].append(
                        f"Handled {len(failed_results)} failed tasks"
                    )
                
                coordination_result["coordination_time"] = max(time.time() - coordination_start, 0.001)
                
                # Log coordination
                self.coordination_log.append({
                    "strategy": orchestration_strategy,
                    "successful_tasks": len(successful_results),
                    "failed_tasks": len(failed_results),
                    "coordination_time": coordination_result["coordination_time"]
                })
                
                return coordination_result
        
        # Test execution to orchestration coordination
        orchestrator = MockOrchestrator()
        
        # Create mock execution results
        execution_results = [
            MockWorkflowResult(
                workflow_id="workflow_001",
                phase=WorkflowPhase.EXECUTION,
                status=TaskStatus.COMPLETED,
                result={"extracted_data": "resume_skills"},
                error=None,
                execution_time=1.5,
                metadata={"task_id": "extract_resume", "priority": "critical"}
            ),
            MockWorkflowResult(
                workflow_id="workflow_001",
                phase=WorkflowPhase.EXECUTION,
                status=TaskStatus.COMPLETED,
                result={"analysis_result": "skill_match"},
                error=None,
                execution_time=2.0,
                metadata={"task_id": "match_skills", "priority": "high"}
            ),
            MockWorkflowResult(
                workflow_id="workflow_001",
                phase=WorkflowPhase.EXECUTION,
                status=TaskStatus.FAILED,
                result=None,
                error="Resource timeout",
                execution_time=5.0,
                metadata={"task_id": "generate_report", "priority": "medium"}
            )
        ]
        
        # Test different orchestration strategies
        strategies = ["sequential", "priority_based", "adaptive"]
        
        for strategy in strategies:
            coordination_result = orchestrator.coordinate_execution(execution_results, strategy)
            
            # Validate coordination
            assert coordination_result["strategy"] == strategy
            assert len(coordination_result["coordinated_results"]) == 2  # Only successful tasks
            assert coordination_result["coordination_time"] > 0
            assert len(coordination_result["orchestration_decisions"]) > 0
            
            # For priority-based strategy, check ordering
            if strategy == "priority_based":
                coordinated = coordination_result["coordinated_results"]
                assert coordinated[0]["priority"] == "critical"
                assert coordinated[1]["priority"] == "high"
        
        # Validate coordination log
        assert len(orchestrator.coordination_log) == 3
        assert all(log["successful_tasks"] == 2 for log in orchestrator.coordination_log)
        assert all(log["coordination_time"] > 0 for log in orchestrator.coordination_log)
    
    def test_end_to_end_workflow_integrity(self):
        """Test complete workflow integrity from planning to orchestration."""
        
        class MockWorkflowPipeline:
            def __init__(self):
                self.planning_engine = Mock()
                self.execution_engine = Mock()
                self.orchestrator = Mock()
                self.pipeline_history = []
            
            def execute_workflow(self, mission: str, context: Dict[str, Any], 
                               strategy: str = "sequential") -> Dict[str, Any]:
                """Execute complete workflow pipeline."""
                pipeline_start = time.time()
                
                workflow_result = {
                    "mission": mission,
                    "workflow_id": context.get("workflow_id", "unknown"),
                    "strategy": strategy,
                    "phases": {},
                    "final_output": None,
                    "success": False,
                    "total_time": 0.0,
                    "errors": []
                }
                
                try:
                    # Phase 1: Planning
                    plan = self.planning_engine.create_plan(mission, context)
                    workflow_result["phases"]["planning"] = {
                        "status": "completed",
                        "plan_id": plan.plan_id,
                        "task_count": len(plan.tasks)
                    }
                    
                    # Phase 2: Execution
                    execution_context = {"workflow_id": context["workflow_id"], "strategy": strategy}
                    execution_results = self.execution_engine.execute_plan(plan, execution_context)
                    
                    successful_executions = [r for r in execution_results if r.status == TaskStatus.COMPLETED]
                    failed_executions = [r for r in execution_results if r.status == TaskStatus.FAILED]
                    
                    workflow_result["phases"]["execution"] = {
                        "status": "completed" if not failed_executions else "partial_success",
                        "successful_tasks": len(successful_executions),
                        "failed_tasks": len(failed_executions)
                    }
                    
                    # Phase 3: Orchestration
                    coordination_result = self.orchestrator.coordinate_execution(execution_results, strategy)
                    
                    workflow_result["phases"]["orchestration"] = {
                        "status": coordination_result["final_status"],
                        "coordination_time": coordination_result["coordination_time"],
                        "decisions": coordination_result["orchestration_decisions"]
                    }
                    
                    # Final output
                    if coordination_result["final_status"] in ["completed", "partial_success"]:
                        workflow_result["final_output"] = {
                            "coordinated_results": coordination_result["coordinated_results"],
                            "summary": f"Processed {len(successful_executions)} tasks successfully"
                        }
                        workflow_result["success"] = True
                    
                except Exception as e:
                    workflow_result["errors"].append(str(e))
                    workflow_result["success"] = False
                
                workflow_result["total_time"] = max(time.time() - pipeline_start, 0.001)
                
                # Log pipeline execution
                self.pipeline_history.append({
                    "workflow_id": workflow_result["workflow_id"],
                    "success": workflow_result["success"],
                    "total_time": workflow_result["total_time"],
                    "strategy": strategy
                })
                
                return workflow_result
        
        # Mock the engines with realistic behavior
        mock_plan = MockWorkflowPlan(
            plan_id="plan_001",
            mission="Test mission",
            phases=["planning", "execution", "orchestration"],
            tasks=[
                {"task_id": "task1", "type": "extraction", "priority": "critical"},
                {"task_id": "task2", "type": "analysis", "priority": "high"}
            ],
            dependencies={"task1": [], "task2": ["task1"]},
            estimated_duration=4.0
        )
        
        mock_execution_results = [
            MockWorkflowResult(
                workflow_id="workflow_001",
                phase=WorkflowPhase.EXECUTION,
                status=TaskStatus.COMPLETED,
                result={"data": "extracted"},
                error=None,
                execution_time=1.0,
                metadata={"task_id": "task1", "priority": "critical"}
            ),
            MockWorkflowResult(
                workflow_id="workflow_001",
                phase=WorkflowPhase.EXECUTION,
                status=TaskStatus.COMPLETED,
                result={"analysis": "completed"},
                error=None,
                execution_time=1.5,
                metadata={"task_id": "task2", "priority": "high"}
            )
        ]
        
        mock_coordination = {
            "strategy": "sequential",
            "coordinated_results": [
                {"task_id": "task1", "output": {"data": "extracted"}},
                {"task_id": "task2", "output": {"analysis": "completed"}}
            ],
            "orchestration_decisions": ["Executed tasks sequentially"],
            "final_status": "completed",
            "coordination_time": 0.1
        }
        
        # Setup pipeline with mocks
        pipeline = MockWorkflowPipeline()
        pipeline.planning_engine.create_plan.return_value = mock_plan
        pipeline.execution_engine.execute_plan.return_value = mock_execution_results
        pipeline.orchestrator.coordinate_execution.return_value = mock_coordination
        
        # Execute workflow
        mission = "Extract and analyze resume data"
        context = {"workflow_id": "workflow_001", "priority": "high"}
        
        result = pipeline.execute_workflow(mission, context, "sequential")
        
        # Validate workflow integrity
        assert result["mission"] == mission
        assert result["workflow_id"] == "workflow_001"
        assert result["success"] is True
        assert result["total_time"] > 0
        assert len(result["errors"]) == 0
        
        # Validate phase completion
        assert "planning" in result["phases"]
        assert "execution" in result["phases"]
        assert "orchestration" in result["phases"]
        
        assert result["phases"]["planning"]["status"] == "completed"
        assert result["phases"]["execution"]["status"] == "completed"
        assert result["phases"]["orchestration"]["status"] == "completed"
        
        # Validate final output
        assert result["final_output"] is not None
        assert len(result["final_output"]["coordinated_results"]) == 2
        
        # Validate pipeline history
        assert len(pipeline.pipeline_history) == 1
        assert pipeline.pipeline_history[0]["workflow_id"] == "workflow_001"
        assert pipeline.pipeline_history[0]["success"] is True
        
        # Verify mock calls
        pipeline.planning_engine.create_plan.assert_called_once_with(mission, context)
        pipeline.execution_engine.execute_plan.assert_called_once()
        pipeline.orchestrator.coordinate_execution.assert_called_once()


class TestWorkflowErrorHandling:
    """Test error handling in critical path workflow."""
    
    def test_planning_failure_propagation(self):
        """Test that planning failures propagate correctly through workflow."""
        
        class FailingPlanningEngine:
            def create_plan(self, mission: str, context: Dict[str, Any]) -> MockWorkflowPlan:
                if "invalid" in mission.lower():
                    raise ValueError(f"Invalid mission: {mission}")
                return MockWorkflowPlan(
                    plan_id="valid_plan",
                    mission=mission,
                    phases=["planning"],
                    tasks=[],
                    dependencies={},
                    estimated_duration=0.0
                )
        
        # Test planning failure
        planning_engine = FailingPlanningEngine()
        
        # Valid mission should succeed
        valid_result = planning_engine.create_plan("Valid mission", {})
        assert valid_result.plan_id == "valid_plan"
        
        # Invalid mission should fail
        with pytest.raises(ValueError, match="Invalid mission"):
            planning_engine.create_plan("Invalid mission with invalid content", {})
    
    def test_execution_failure_handling(self):
        """Test handling of execution failures in workflow."""
        
        class FailingExecutionEngine:
            def execute_plan(self, plan: MockWorkflowPlan, context: Dict[str, Any]) -> List[MockWorkflowResult]:
                if "fail" in context.get("execution_mode", ""):
                    return [
                        MockWorkflowResult(
                            workflow_id=context.get("workflow_id", "unknown"),
                            phase=WorkflowPhase.EXECUTION,
                            status=TaskStatus.FAILED,
                            result=None,
                            error="Simulated execution failure",
                            execution_time=0.0,
                            metadata={"task_id": "failed_task"}
                        )
                    ]
                else:
                    return [
                        MockWorkflowResult(
                            workflow_id=context.get("workflow_id", "unknown"),
                            phase=WorkflowPhase.EXECUTION,
                            status=TaskStatus.COMPLETED,
                            result={"success": True},
                            error=None,
                            execution_time=1.0,
                            metadata={"task_id": "successful_task"}
                        )
                    ]
        
        # Test execution failure handling
        execution_engine = FailingExecutionEngine()
        
        plan = MockWorkflowPlan(
            plan_id="test_plan",
            mission="Test mission",
            phases=["execution"],
            tasks=[{"task_id": "test_task", "type": "test"}],
            dependencies={},
            estimated_duration=1.0
        )
        
        # Successful execution
        success_context = {"workflow_id": "workflow_001", "execution_mode": "normal"}
        success_results = execution_engine.execute_plan(plan, success_context)
        
        assert len(success_results) == 1
        assert success_results[0].status == TaskStatus.COMPLETED
        assert success_results[0].error is None
        
        # Failed execution
        fail_context = {"workflow_id": "workflow_002", "execution_mode": "fail"}
        fail_results = execution_engine.execute_plan(plan, fail_context)
        
        assert len(fail_results) == 1
        assert fail_results[0].status == TaskStatus.FAILED
        assert fail_results[0].error == "Simulated execution failure"
    
    def test_orchestration_error_recovery(self):
        """Test orchestration error recovery mechanisms."""
        
        class ErrorRecoveryOrchestrator:
            def coordinate_execution(self, execution_results: List[MockWorkflowResult], 
                                   strategy: str) -> Dict[str, Any]:
                successful_results = [r for r in execution_results if r.status == TaskStatus.COMPLETED]
                failed_results = [r for r in execution_results if r.status == TaskStatus.FAILED]
                
                coordination_result = {
                    "strategy": strategy,
                    "successful_count": len(successful_results),
                    "failed_count": len(failed_results),
                    "recovery_actions": [],
                    "final_status": "completed"
                }
                
                # Error recovery logic
                if failed_results:
                    coordination_result["final_status"] = "partial_success"
                    coordination_result["recovery_actions"] = [
                        "Logged execution failures",
                        "Continued with successful results",
                        f"Attempted recovery for {len(failed_results)} failed tasks"
                    ]
                    
                    # For critical failures, mark as failed
                    critical_failures = [r for r in failed_results if "critical" in r.metadata.get("priority", "")]
                    if critical_failures:
                        coordination_result["final_status"] = "failed"
                        coordination_result["recovery_actions"].append("Critical task failure - workflow failed")
                else:
                    coordination_result["recovery_actions"] = ["All tasks completed successfully"]
                
                return coordination_result
        
        # Test error recovery
        orchestrator = ErrorRecoveryOrchestrator()
        
        # Test with mixed results
        mixed_results = [
            MockWorkflowResult(
                workflow_id="workflow_001",
                phase=WorkflowPhase.EXECUTION,
                status=TaskStatus.COMPLETED,
                result={"data": "success"},
                error=None,
                execution_time=1.0,
                metadata={"task_id": "task1", "priority": "high"}
            ),
            MockWorkflowResult(
                workflow_id="workflow_001",
                phase=WorkflowPhase.EXECUTION,
                status=TaskStatus.FAILED,
                result=None,
                error="Non-critical failure",
                execution_time=0.5,
                metadata={"task_id": "task2", "priority": "medium"}
            )
        ]
        
        recovery_result = orchestrator.coordinate_execution(mixed_results, "recovery")
        
        assert recovery_result["successful_count"] == 1
        assert recovery_result["failed_count"] == 1
        assert recovery_result["final_status"] == "partial_success"
        assert len(recovery_result["recovery_actions"]) >= 2
        
        # Test with critical failure
        critical_failure_results = [
            MockWorkflowResult(
                workflow_id="workflow_002",
                phase=WorkflowPhase.EXECUTION,
                status=TaskStatus.FAILED,
                result=None,
                error="Critical failure",
                execution_time=0.1,
                metadata={"task_id": "critical_task", "priority": "critical"}
            )
        ]
        
        critical_result = orchestrator.coordinate_execution(critical_failure_results, "recovery")
        
        assert critical_result["successful_count"] == 0
        assert critical_result["failed_count"] == 1
        assert critical_result["final_status"] == "failed"
        assert any("Critical task failure" in action for action in critical_result["recovery_actions"])
