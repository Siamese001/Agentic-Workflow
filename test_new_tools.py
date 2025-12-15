# Test the new Action Registry tools
from action_registry import ActionRegistry

# Initialize the registry
actions = ActionRegistry()
tools = actions.get_tool_map()

print("Available tools:", list(tools.keys()))

# Test save_file
print("\nTesting save_file...")
result = tools["save_file"]("Hello, World!", "test_output.txt")
print(result)

# Test read_file
print("\nTesting read_file...")
result = tools["read_file"]("test_output.txt")
print("Content:", result)

# Test mock_send_email
print("\nTesting mock_send_email...")
result = tools["send_email"]("test@example.com", "Test Subject", "Test Body")
print(result)

