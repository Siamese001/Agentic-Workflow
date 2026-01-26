# Scope: Test the Loop Logic, Tooling, and State Transitions
# Mandatory: 100% Pass Rate required.

import pytest
import asyncio
from agentic_core.runtime.tools import BaseTool, ToolRegistry, FunctionalTool
from agentic_core.runtime.engine import AgentEngine
from agentic_core.patterns.react import ReActPattern
from agentic_core.runtime.state import AgentState

# --- Helper: Mock Tool ---
class MockSearchTool(BaseTool):
    name: str = "search_tool"
    description: str = "Searches things"
    async def run(self, query: str) -> str:
        return f"Results for {query}"

class MockCalcTool(BaseTool):
    name: str = "calc_tool"
    description: str = "Calculates things"
    async def run(self, expression: str) -> str:
        return "4"

# --- TestCase 1: Tool Registry Logic ---
def test_tool_registry():
    """
    Verify tool registration and retrieval.
    Edge Case: Duplicate registration.
    """
    registry = ToolRegistry()
    t1 = MockSearchTool()
    
    registry.register(t1)
    assert registry.get("search_tool") == t1
    
    # Duplicate check
    with pytest.raises(ValueError):
        registry.register(t1)
        
    assert "search_tool" in registry.list_tools()

# --- TestCase 2: The Happy Path (ReAct Simulation) ---
@pytest.mark.asyncio
async def test_engine_happy_path():
    """
    Run the Mock ReAct pattern.
    Should go: Search -> Calc -> Finish.
    """
    registry = ToolRegistry()
    registry.register(MockSearchTool())
    registry.register(MockCalcTool())
    
    pattern = ReActPattern()
    engine = AgentEngine(pattern, registry, max_turns=10)
    
    final_state = await engine.run("Hello World")
    
    assert final_state.is_terminated
    assert final_state.termination_reason == "COMPLETED"
    # Turn 0 (Search) + Turn 1 (Calc) = 2 turns incremented. 
    # The loop breaks on Turn 2 (Final Answer) before incrementing.
    assert final_state.turn_count == 2
    
    # Check history trace
    history = [m.content for m in final_state.messages]
    assert any("search_tool" in m for m in history)
    assert any("calc_tool" in m for m in history)
    assert any("Final Answer" in m for m in history)

# --- TestCase 3: Max Turns Enforcement (Infinite Loop Protection) ---
@pytest.mark.asyncio
async def test_max_turns_enforcement():
    """
    Verify the engine kills the agent if it loops too long.
    """
    registry = ToolRegistry()
    registry.register(MockSearchTool())
    
    # Pattern logic: Turn 0->Search, Turn 1->Calc.
    # If we set max_turns=1, it should stop after Search (Turn 0 finished, loop checks count vs max).
    
    pattern = ReActPattern()
    engine = AgentEngine(pattern, registry, max_turns=1)
    
    final_state = await engine.run("Loop check")
    
    assert final_state.is_terminated
    assert final_state.termination_reason == "MAX_TURNS_REACHED"
    assert final_state.turn_count == 1

# --- TestCase 4: Missing Tool Handling ---
@pytest.mark.asyncio
async def test_missing_tool_handling():
    """
    Verify engine doesn't crash if pattern selects a non-existent tool.
    """
    registry = ToolRegistry()
    # Don't register anything!
    
    pattern = ReActPattern() # Will try to call 'search_tool'
    engine = AgentEngine(pattern, registry, max_turns=5)
    
    final_state = await engine.run("Test Missing")
    
    # Logic: Pattern calls search_tool -> Engine fails to find -> Observation Error -> Increment Turn
    # Next turn: Pattern calls calc_tool -> ...
    
    # Check the first observation
    obs_message = next(m for m in final_state.messages if "Observation" in m.content)
    assert "Error: Tool 'search_tool' not found" in obs_message.content
