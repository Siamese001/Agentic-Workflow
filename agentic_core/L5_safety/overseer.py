"""Constitutional Overseer for validating ActionRequests.

Validates actions against forbidden commands and safety rules.
"""

import logging
import re
from typing import Any, Dict, List

from agentic_core.interfaces import ActionRequest

LOGGER = logging.getLogger(__name__)


class ViolationCheck:
    """Result of a safety violation check."""
    def __init__(self, is_violation: bool, reason: str = ""):
        self.is_violation = is_violation
        self.reason = reason


class ConstitutionalOverseer:
    """Overseer that validates ActionRequests against safety rules."""
    
    def __init__(self):
        """Initialize the overseer with default safety rules."""
        self._forbidden_commands = [
            # Dangerous file operations
            r'rm\s+-rf\s+/',           # Delete root filesystem
            r'rm\s+-rf\s+\.',           # Delete current directory recursively
            r'dd\s+if=/dev/zero',       # Disk wiping
            r'mkfs\.',                  # Filesystem formatting
            
            # Network restrictions
            r'curl\s+https?://(?!localhost|127\.0\.0\.1)',  # External URLs
            r'wget\s+https?://(?!localhost|127\.0\.0\.1)',   # External URLs
            r'nc\s+-l',                 # Netcat listening
            r'telnet\s+\d',             # Telnet to external
            
            # System commands
            r'sudo\s+su',               # Privilege escalation
            r'chmod\s+777',             # Dangerous permissions
            r'chown\s+root',            # Ownership changes
            
            # Package management
            r'apt-get\s+install',       # Package installation
            r'pip\s+install\s+--force', # Forced package install
            r'yum\s+install',           # Package installation
            
            # Dangerous scripts
            r'eval\s+\$',               # Code execution
            r'exec\s+\$',               # Command execution
            r'sh\s+-c',                 # Shell execution
        ]
        
        # Compile regex patterns for performance
        self._compiled_patterns = [re.compile(pattern, re.IGNORECASE) 
                                  for pattern in self._forbidden_commands]
        
        LOGGER.info(f"Constitutional Overseer initialized with {len(self._forbidden_commands)} forbidden patterns")
    
    async def validate_action(self, request: ActionRequest) -> ViolationCheck:
        """Validate an ActionRequest against safety rules.
        
        Args:
            request: The ActionRequest to validate
            
        Returns:
            ViolationCheck with validation result
        """
        # Check action type
        if request.action_type == "tool_execution":
            return await self._validate_tool_execution(request)
        elif request.action_type == "file_operations":
            return await self._validate_file_operations(request)
        elif request.action_type == "diagnostic_tool_creation":
            return ViolationCheck(False, "Diagnostic tool creation is allowed")
        else:
            return ViolationCheck(True, f"Unknown action type: {request.action_type}")
    
    async def _validate_tool_execution(self, request: ActionRequest) -> ViolationCheck:
        """Validate tool execution requests."""
        tool_path = request.parameters.get("tool_path", "")
        args = request.parameters.get("args", [])
        
        # Check tool path
        if tool_path:
            violation = self._check_forbidden_patterns(tool_path)
            if violation:
                return violation
        
        # Check arguments
        for arg in args:
            violation = self._check_forbidden_patterns(str(arg))
            if violation:
                return violation
        
        # Additional checks for shell commands
        if "shell" in request.parameters.get("execution_mode", ""):
            shell_cmd = request.parameters.get("shell_command", "")
            violation = self._check_forbidden_patterns(shell_cmd)
            if violation:
                return violation
        
        return ViolationCheck(False, "Action validated - SAFE")
    
    async def _validate_file_operations(self, request: ActionRequest) -> ViolationCheck:
        """Validate file operation requests."""
        operation = request.parameters.get("operation", "")
        file_path = request.parameters.get("file_path", "")
        
        # Check for dangerous file paths
        dangerous_paths = [
            "/etc/passwd",
            "/etc/shadow",
            "/etc/sudoers",
            "/root/",
            "/sys/",
            "/proc/",
            "/dev/",
        ]
        
        for path in dangerous_paths:
            if path in file_path:
                return ViolationCheck(True, f"Access to sensitive path forbidden: {path}")
        
        # Check operation safety
        if operation == "delete":
            # Prevent deletion of critical files
            critical_extensions = [".py", ".sh", ".bat", ".cmd", ".ps1"]
            if any(file_path.endswith(ext) for ext in critical_extensions):
                return ViolationCheck(True, "Deletion of executable files is forbidden")
        
        return ViolationCheck(False, "File operation validated - SAFE")
    
    def _check_forbidden_patterns(self, text: str) -> ViolationCheck:
        """Check text against forbidden command patterns.
        
        Args:
            text: Text to check
            
        Returns:
            ViolationCheck if violation found, None if safe
        """
        for pattern in self._compiled_patterns:
            if pattern.search(text):
                return ViolationCheck(True, f"Forbidden command pattern detected: {pattern.pattern}")
        
        return None
    
    def add_forbidden_pattern(self, pattern: str):
        """Add a new forbidden pattern.
        
        Args:
            pattern: Regex pattern to add
        """
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
            self._compiled_patterns.append(compiled)
            self._forbidden_commands.append(pattern)
            LOGGER.info(f"Added forbidden pattern: {pattern}")
        except re.error as e:
            LOGGER.error(f"Invalid regex pattern: {e}")
    
    def get_forbidden_patterns(self) -> List[str]:
        """Get list of forbidden patterns.
        
        Returns:
            List of forbidden command patterns
        """
        return self._forbidden_commands.copy()


def create_overseer() -> ConstitutionalOverseer:
    """Factory function to create overseer instance."""
    return ConstitutionalOverseer()