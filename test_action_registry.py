from action_registry import ActionRegistry

# Test the Action Registry directly
actions = ActionRegistry()
tools = actions.get_tool_map()

print("Available tools:", list(tools.keys()))

# Test search_web
if "search_web" in tools:
    print("\nTesting search_web...")
    result = tools["search_web"]("test query")
    print("Result:", result[:200] + "..." if len(result) > 200 else result)

