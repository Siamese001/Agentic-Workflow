#!/usr/bin/env python3
"""
Example usage of EventEmissionMixin in agent implementations
"""

import asyncio
import logging
from agentic_core.utils.core_extensions.event_emission_mixin import EventEmissionMixin, SovereignEvent

class MockBaseAgent:
    """Mock base agent to avoid circular imports"""
    def __init__(self):
        self.name = "MockAgent"

class HealingAgent(EventEmissionMixin, MockBaseAgent):
    """
    Example healing agent with comprehensive event emission
    """
    
    def __init__(self):
        super().__init__()
        self.heal_count = 0
        self.failure_count = 0
    
    @EventEmissionMixin.observe_execution("healing")
    async def heal_violation(self, violation):
        """Heal a violation with automatic event emission"""
        self.heal_count += 1
        
        # Simulate healing work
        await asyncio.sleep(0.01)
        
        # Simulate occasional failure
        if violation.get("type") == "critical_error":
            raise RuntimeError("Critical violation cannot be healed")
        
        return {"success": True, "violation": violation, "heal_id": self.heal_count}
    
    async def batch_heal(self, violations):
        """Batch heal with manual event emission"""
        self.emit_event("batch_healing.started", {
            "violation_count": len(violations),
            "batch_id": f"batch_{self.heal_count}"
        })
        
        results = []
        failed = []
        
        for violation in violations:
            try:
                result = await self.heal_violation(violation)
                results.append(result)
            except Exception as e:
                failed.append({"violation": violation, "error": str(e)})
                self.failure_count += 1
        
        self.emit_event("batch_healing.completed", {
            "success_count": len(results),
            "failure_count": len(failed),
            "batch_id": f"batch_{self.heal_count}"
        }, severity="WARNING" if failed else "INFO")
        
        return {"results": results, "failed": failed}

class DataProcessingAgent(EventEmissionMixin, MockBaseAgent):
    """
    Example data processing agent with trace correlation
    """
    
    def __init__(self):
        super().__init__()
        self.processed_count = 0
    
    @EventEmissionMixin.observe_execution("data_processing")
    async def process_data(self, data, trace_id=None):
        """Process data with trace correlation"""
        self.processed_count += 1
        
        # Simulate processing
        await asyncio.sleep(0.02)
        
        # Emit progress event with trace correlation
        self.emit_event("processing.progress", {
            "processed_count": self.processed_count,
            "data_size": len(str(data)),
            "trace_id": trace_id
        }, trace_id=trace_id)
        
        # Simulate occasional processing error
        if data.get("should_fail"):
            raise ValueError("Data processing failed")
        
        return {"processed": True, "count": self.processed_count, "trace_id": trace_id}

class MonitoringAgent(EventEmissionMixin, MockBaseAgent):
    """
    Example monitoring agent with severity-based events
    """
    
    def __init__(self):
        super().__init__()
        self.alert_count = 0
    
    async def check_system_health(self):
        """Check system health and emit appropriate events"""
        # Simulate health check
        await asyncio.sleep(0.01)
        
        # Simulate different health scenarios
        health_scenarios = [
            {"status": "healthy", "cpu": 45, "memory": 60},
            {"status": "warning", "cpu": 85, "memory": 75},
            {"status": "critical", "cpu": 95, "memory": 90}
        ]
        
        import random
        scenario = random.choice(health_scenarios)
        
        # Emit health event with appropriate severity
        severity = "INFO"
        if scenario["status"] == "warning":
            severity = "WARNING"
        elif scenario["status"] == "critical":
            severity = "ERROR"
            self.alert_count += 1
        
        self.emit_event("system.health", scenario, severity=severity)
        
        return scenario

class OrchestratorAgent(EventEmissionMixin, MockBaseAgent):
    """
    Example orchestrator agent with complex event flows
    """
    
    def __init__(self):
        super().__init__()
        self.operation_count = 0
    
    async def orchestrate_workflow(self, workflow_data):
        """Orchestrate a complex workflow with multiple events"""
        trace_id = f"workflow_{self.operation_count}"
        
        # Start workflow
        self.emit_event("workflow.started", {
            "workflow_type": workflow_data.get("type", "unknown"),
            "steps": len(workflow_data.get("steps", [])),
            "trace_id": trace_id
        }, trace_id=trace_id)
        
        try:
            # Execute workflow steps
            results = []
            for i, step in enumerate(workflow_data.get("steps", [])):
                self.emit_event("workflow.step_started", {
                    "step_number": i + 1,
                    "step_type": step.get("type"),
                    "trace_id": trace_id
                }, trace_id=trace_id)
                
                # Simulate step execution
                await asyncio.sleep(0.01)
                
                # Simulate step failure
                if step.get("should_fail"):
                    raise RuntimeError(f"Step {i + 1} failed")
                
                result = f"Step {i + 1} completed"
                results.append(result)
                
                self.emit_event("workflow.step_completed", {
                    "step_number": i + 1,
                    "result": result,
                    "trace_id": trace_id
                }, trace_id=trace_id)
            
            # Complete workflow
            self.emit_event("workflow.completed", {
                "workflow_type": workflow_data.get("type"),
                "steps_completed": len(results),
                "trace_id": trace_id
            }, trace_id=trace_id)
            
            self.operation_count += 1
            return {"success": True, "results": results, "trace_id": trace_id}
            
        except Exception as e:
            self.emit_event("workflow.failed", {
                "error": str(e),
                "steps_completed": len(results) if 'results' in locals() else 0,
                "trace_id": trace_id
            }, severity="ERROR", trace_id=trace_id)
            raise

async def demonstrate_manual_events():
    """Demonstrate manual event emission"""
    print("\n1. Manual Event Emission:")
    print("-" * 40)
    
    agent = HealingAgent()
    
    # Manual event emission
    event = agent.emit_event("test.manual", {
        "message": "Manual test event",
        "timestamp": "2026-01-13T11:00:00Z"
    })
    
    print(f"  ✅ Manual event emitted: {event.event_id[:8]}")
    print(f"  📋 Event type: {event.event_type}")
    print(f"  🤖 Source agent: {event.source_agent}")
    print(f"  🔍 Severity: {event.severity}")

async def demonstrate_decorator_events():
    """Demonstrate decorator-based event emission"""
    print("\n2. Decorator Event Emission:")
    print("-" * 40)
    
    agent = HealingAgent()
    
    # Successful operation with decorator
    result = await agent.heal_violation({"type": "syntax_error", "file": "test.py"})
    print(f"  ✅ Healing completed: {result['success']}")
    print(f"  📊 Heal count: {agent.heal_count}")
    
    # Failed operation with decorator
    try:
        await agent.heal_violation({"type": "critical_error", "file": "critical.py"})
    except RuntimeError as e:
        print(f"  ❌ Healing failed as expected: {e}")
        print(f"  📊 Failure count: {agent.failure_count}")

async def demonstrate_trace_correlation():
    """Demonstrate trace ID correlation"""
    print("\n3. Trace ID Correlation:")
    print("-" * 40)
    
    agent = DataProcessingAgent()
    
    # Process data with trace correlation
    trace_id = "trace_12345"
    result = await agent.process_data({"data": "test"}, trace_id=trace_id)
    
    print(f"  ✅ Data processed: {result['processed']}")
    print(f"  🔗 Trace ID: {result['trace_id']}")
    print(f"  📊 Processed count: {agent.processed_count}")

async def demonstrate_severity_events():
    """Demonstrate severity-based event emission"""
    print("\n4. Severity-Based Events:")
    print("-" * 40)
    
    agent = MonitoringAgent()
    
    # Check system health multiple times to see different severities
    for i in range(3):
        health = await agent.check_system_health()
        print(f"  📊 Health check {i+1}: {health['status']} (CPU: {health['cpu']}%, Memory: {health['memory']}%)")
    
    print(f"  🚨 Total alerts: {agent.alert_count}")

async def demonstrate_complex_workflow():
    """Demonstrate complex workflow with multiple events"""
    print("\n5. Complex Workflow Events:")
    print("-" * 40)
    
    agent = OrchestratorAgent()
    
    # Successful workflow
    workflow_data = {
        "type": "data_pipeline",
        "steps": [
            {"type": "extract"},
            {"type": "transform"},
            {"type": "load"}
        ]
    }
    
    try:
        result = await agent.orchestrate_workflow(workflow_data)
        print(f"  ✅ Workflow completed: {result['success']}")
        print(f"  📊 Steps completed: {len(result['results'])}")
        print(f"  🔗 Trace ID: {result['trace_id']}")
    except Exception as e:
        print(f"  ❌ Workflow failed: {e}")
    
    # Failed workflow
    failed_workflow = {
        "type": "backup_pipeline",
        "steps": [
            {"type": "backup", "should_fail": True}
        ]
    }
    
    try:
        await agent.orchestrate_workflow(failed_workflow)
    except Exception as e:
        print(f"  ❌ Failed workflow as expected: {e}")

async def demonstrate_batch_operations():
    """Demonstrate batch operation events"""
    print("\n6. Batch Operation Events:")
    print("-" * 40)
    
    agent = HealingAgent()
    
    violations = [
        {"type": "syntax_error", "file": "file1.py"},
        {"type": "import_error", "file": "file2.py"},
        {"type": "runtime_error", "file": "file3.py"}
    ]
    
    result = await agent.batch_heal(violations)
    print(f"  ✅ Batch healing completed")
    print(f"  📊 Success count: {len(result['results'])}")
    print(f"  ❌ Failure count: {len(result['failed'])}")
    print(f"  📊 Total heal count: {agent.heal_count}")

async def main():
    """Run all demonstrations"""
    print("=" * 60)
    print("EVENT EMISSION MIXIN USAGE DEMONSTRATIONS")
    print("=" * 60)
    
    await demonstrate_manual_events()
    await demonstrate_decorator_events()
    await demonstrate_trace_correlation()
    await demonstrate_severity_events()
    await demonstrate_complex_workflow()
    await demonstrate_batch_operations()
    
    print("\n" + "=" * 60)
    print("✅ ALL DEMONSTRATIONS COMPLETE")
    print("=" * 60)
    
    print("\nKey Features Demonstrated:")
    print("• Manual event emission with structured schema")
    print("• Decorator-based automatic lifecycle events")
    print("• Trace ID correlation for distributed tracking")
    print("• Severity-based event filtering")
    print("• Complex workflow event orchestration")
    print("• Batch operation event tracking")
    print("• Pydantic schema validation")

if __name__ == "__main__":
    asyncio.run(main())
