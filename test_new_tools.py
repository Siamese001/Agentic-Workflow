# Test the new Action Registry tools
from action_registry import ActionRegistry

# Initialize the registry
actions = ActionRegistry()
tools = actions.get_tool_map()

# print("Available tools:", list(tools.keys()))  # [Security Fix]

# Test save_file
# print("\nTesting save_file...")  # [Security Fix]
result = tools["save_file"]("Hello, World!", "test_output.txt")
# print(result)  # [Security Fix]

# Test read_file
# print("\nTesting read_file...")  # [Security Fix]
result = tools["read_file"]("test_output.txt")
# print("Content:", result)  # [Security Fix]

# Test mock_send_email
# print("\nTesting mock_send_email...")  # [Security Fix]
result = tools["send_email"]("test@example.com", "Test Subject", "Test Body")
# print(result)  # [Security Fix]

