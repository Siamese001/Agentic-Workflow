"""L5 Safety: MCP Sovereign Shield
Enforces zero-trust auditing and auto-immune responses for all MCP tool calls.
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPSovereignAuthority:
    """Monitors the health and authorization of the MCP nervous system."""
    
    def __init__(self):
        self.violation_count = 0
        self.breach_log = []
        self.is_locked = False

    def is_authorized(self) -> bool:
        """Sovereignty check: Kill connections if breaches exceed threshold."""
        if self.violation_count > 5:
            self.is_locked = True
        return not self.is_locked

    def record_breach(self, error_msg: str):
        """Log a tool failure or unauthorized access attempt."""
        self.violation_count += 1
        self.breach_log.append({
            "timestamp": datetime.now().isoformat(),
            "error": error_msg
        })
        logger.warning(f"[L5 MCP BREACH] Violation recorded. Count: {self.violation_count}")

    def shield_call(self, tool_name: str, args: dict):
        """L5 Audit: Log every physical tool call before execution."""
        logger.info(f"[L5 MCP AUDIT] Authorizing call to '{tool_name}' with args: {args}")
        
        # [L2 TOOL HARDENING] Extra validation for external tools
        if tool_name in {"brave_search", "fetch", "playwright"}:
            query = args.get('query') or args.get('url', '')
            if len(str(query)) > 1000:
                raise ValueError(f"L2 tool input too long — potential exfiltration risk.")
            
            forbidden = ["password", "api_key", "secret", "private_key", ".env"]
            if any(bad in str(query).lower() for bad in forbidden):
                raise PermissionError(f"L2 tool query contains forbidden terms — blocked by shield.")

        if not self.is_authorized():
            raise PermissionError("MCP Sovereign Shield active: Tool call blocked due to chronic breaches.")

mcp_authority = MCPSovereignAuthority()
