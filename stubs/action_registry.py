"""Stub for action_registry module."""

class ActionRegistry:
    """Stub for action registration and management."""
    def __init__(self):
        self.actions = {}
        self._tool_map = {
            "save_file": lambda content, path: {"status": "saved", "path": path},
            "read_file": lambda path: "stub file content",
            "send_email": lambda to, subject, body: {"status": "sent", "to": to}
        }
    
    def register(self, name: str, action):
        self.actions[name] = action
        return True
    
    def get(self, name: str):
        return self.actions.get(name)
    
    def list_actions(self):
        return list(self.actions.keys())
    
    def get_tool_map(self):
        return self._tool_map
