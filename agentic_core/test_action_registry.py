from action_registry import ActionRegistry

# Test the Action Registry directly
actions = ActionRegistry()  # GLOBAL: Review if this should be constant
tools = actions.get_tool_map()  # GLOBAL: Review if this should be constant

# print("Available tools:", list(tools.keys()))  # [Security Fix]

# Test search_web
if "search_web" in tools:
    # print("\nTesting search_web...")  # [Security Fix]
    result = tools["search_web"]("test query")
    # print("Result:", result[:200] + "..." if len(result) > 200 else result)  # [Security Fix]

