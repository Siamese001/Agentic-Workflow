# Test the new Action Registry tools
from action_registry import ActionRegistry

# Initialize the registry
actions = ActionRegistry()  # GLOBAL: Review if this should be constant
tools = actions.get_tool_map()  # GLOBAL: Review if this should be constant

# print("Available tools:", list(tools.keys()))  # [Security Fix]

# Test save_file
# print("\nTesting save_file...")  # [Security Fix]
result = tools["save_file"]("Hello, World!", "test_output.txt")  # GLOBAL: Review if this should be constant
# print(result)  # [Security Fix]

# Test read_file
# print("\nTesting read_file...")  # [Security Fix]
result = tools["read_file"]("test_output.txt")  # GLOBAL: Review if this should be constant
# print("Content:", result)  # [Security Fix]

# Test mock_send_email
# print("\nTesting mock_send_email...")  # [Security Fix]
result = tools["send_email"]("test@example.com", "Test Subject", "Test Body")  # GLOBAL: Review if this should be constant
# print(result)  # [Security Fix]

