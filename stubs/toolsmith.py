class Toolsmith:
    """Stub for the L2 tool-forging system."""
    def forge(self, spec: dict): return {"ready": True, "name": spec.get("name")}
    def list_tools(self): return ["stub_tool_v1"]
