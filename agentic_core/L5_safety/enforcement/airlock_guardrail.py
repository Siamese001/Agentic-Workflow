from __future__ import annotations
import logging
'Brief description of functionality and purpose.'
'Brief description of functionality and purpose.'
from typing import Any
from agentic_core.L5_safety.config.structure_blueprint.ssot import GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class AirlockProtocol:
    """
    L5 Safety Guardrail: The Execution Airlock.
    Validates tool calls against a mission-specific Permission matrix.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.allowed_tools = config.get('allowed_tools', ['read_file', 'search_web', 'get_status'])
        self.high_risk_tools = ['run_python', 'write_file', 'delete_file', 'execute_shell']

    async def acquire_permission(self, tool_name: str, args: dict[str, Any]) -> bool:
        """Determines if a tool execution is safe to proceed under Zero-Trust."""
        if tool_name not in self.allowed_tools and tool_name not in self.high_risk_tools:
            raise PermissionError(f"Airlock Block: Tool '{tool_name}' is not in the Sovereign Registry.")
        if tool_name in self.high_risk_tools:
            logging.info(f"Airlock: Evaluating High-Risk tool '{tool_name}'...")
            return self._validate_risk_parameters(tool_name, args)
        return True

    def _validate_risk_parameters(self, tool: str, args: dict) -> bool:
        path = str(args.get('path', '')).lower()
        protected_targets = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS
        if any((bad in path for bad in protected_targets)):
            logging.error(f'Airlock: Blocked access attempt to protected path: {path}')
            return False
        return True
