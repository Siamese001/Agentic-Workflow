"""Constitutional Overseer for validating ActionRequests.

Validates actions against forbidden commands and safety rules.
Includes SafetyInspector with Socratic Judge for false positive mitigation.
"""

import logging
import os
import re
from typing import Dict, List

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


class SafetyInspector:
    """
    L5 Safety Inspector with Socratic Judge for false positive mitigation.
    
    KEYS: 0 (Secrets), 1 (TODO/FIXME), 2 (Print), 3 (Debugger), 4 (Empty Except), 5 (Bare Except), 6 (Eval/Exec)
    ROLE: Security Compliance with intelligent violation verification.
    """
    
    def __init__(self, enable_socratic_judge: bool = True):
        """
        Initialize the SafetyInspector.
        
        Args:
            enable_socratic_judge: Whether to use LLM verification for false positives
        """
        self.enable_socratic_judge = enable_socratic_judge
        self._false_positive_cache = set()  # Cache to avoid re-checking
        
        # Security patterns to check
        self.secret_patterns = [
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'secret[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'password\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'aws[_-]?access[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'aws[_-]?secret[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'private[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'auth[_-]?token\s*=\s*["\'][^"\']+["\']',
            r'client[_-]?secret\s*=\s*["\'][^"\']+["\']',
            r'database[_-]?url\s*=\s*["\'][^"\']+["\']',
        ]
        
        self.todo_patterns = [
            r'#\s*TODO',
            r'#\s*FIXME',
            r'#\s*HACK',
            r'#\s*XXX',
        ]
        
        self.print_patterns = [
            r'print\s*\(',
            r'sys\.stdout\.write',
        ]
        
        self.debugger_patterns = [
            r'import pdb',
            r'pdb\.set_trace',
            r'import ipdb',
            r'ipdb\.set_trace',
            r'breakpoint\(\)',
        ]
        
        self.eval_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'compile\s*\(',
        ]
        
        LOGGER.info(f"SafetyInspector initialized (Socratic Judge: {enable_socratic_judge})")
    
    async def scan_file(self, file_path: str) -> Dict[str, List[str]]:
        """
        Scan a file for security violations.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            Dictionary mapping violation types to list of violations
        """
        violations = {
            "secrets": [],
            "todos": [],
            "prints": [],
            "debuggers": [],
            "empty_except": [],
            "bare_except": [],
            "evals": [],
        }
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split('\n')
            
            # Key 0: Check for hardcoded secrets
            for pattern in self.secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Use Socratic Judge to verify if it's actually a secret
                    if self.enable_socratic_judge and file_path not in self._false_positive_cache:
                        verification = await self._socratic_verify(
                            file_path,
                            f"Potential secret matching pattern: {pattern}",
                            "Is this actually a hardcoded secret or a false positive (test data, example, placeholder)?"
                        )
                        if verification == "YES":
                            violations["secrets"].append(f"Line with potential secret: {pattern}")
                        else:
                            # Cache as false positive
                            self._false_positive_cache.add(file_path)
                            LOGGER.info(f"Socratic Judge marked as false positive: {file_path}")
                    else:
                        violations["secrets"].append(f"Line with potential secret: {pattern}")
                    break
            
            # Key 1: Check for TODO/FIXME comments
            for i, line in enumerate(lines, 1):
                for pattern in self.todo_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        violations["todos"].append(f"Line {i}: {line.strip()}")
            
            # Key 2: Check for print statements
            for i, line in enumerate(lines, 1):
                for pattern in self.print_patterns:
                    if re.search(pattern, line):
                        violations["prints"].append(f"Line {i}: {line.strip()}")
            
            # Key 3: Check for debugger statements
            for i, line in enumerate(lines, 1):
                for pattern in self.debugger_patterns:
                    if re.search(pattern, line):
                        violations["debuggers"].append(f"Line {i}: {line.strip()}")
            
            # Key 4 & 5: Check for except blocks
            for i, line in enumerate(lines, 1):
                if re.search(r'except\s*:', line):
                    violations["bare_except"].append(f"Line {i}: {line.strip()}")
                elif re.search(r'except\s+pass\s*:', line) or re.search(r'except\s*\n\s*pass', content):
                    violations["empty_except"].append(f"Line {i}: {line.strip()}")
            
            # Key 6: Check for eval/exec
            for i, line in enumerate(lines, 1):
                for pattern in self.eval_patterns:
                    if re.search(pattern, line):
                        # Use Socratic Judge for eval/exec as well
                        if self.enable_socratic_judge and file_path not in self._false_positive_cache:
                            verification = await self._socratic_verify(
                                file_path,
                                f"Dangerous eval/exec usage: {line.strip()}",
                                "Is this actually dangerous dynamic execution or a safe usage (e.g., JSON parsing, AST manipulation)?"
                            )
                            if verification == "YES":
                                violations["evals"].append(f"Line {i}: {line.strip()}")
                            else:
                                self._false_positive_cache.add(file_path)
                                LOGGER.info(f"Socratic Judge marked eval as false positive: {file_path}")
                        else:
                            violations["evals"].append(f"Line {i}: {line.strip()}")
            
        except Exception as e:
            LOGGER.error(f"Error scanning file {file_path}: {e}")
        
        return violations
    
    async def _socratic_verify(self, file_path: str, issue: str, question: str) -> str:
        """
        Ask Gemini to verify if an issue is actually a violation.
        
        Args:
            file_path: Path to the file being checked
            issue: Description of the potential issue
            question: Specific question about the issue
            
        Returns:
            "YES" if it's a real violation, "NO" if it's a false positive
        """
        try:
            # Try to import google.generativeai
            import google.generativeai as genai

            # Check for API key
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                LOGGER.warning("GOOGLE_API_KEY not found - Socratic Judge disabled")
                return "YES"  # Default to treating as violation
            
            # Read the code snippet
            with open(file_path, "r", encoding="utf-8") as f:
                code_snippet = f.read()
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            # Build the Socratic Judge prompt
            prompt = f"""
Role: Socratic Judge - Expert Code Security Reviewer

Context: Analyzing potential code violation in {file_path}
Issue: {issue}
Question: {question}

Code Snippet:
```python
{code_snippet[:2000]}  # Limit to first 2000 chars
```

Instructions:
1. Analyze the code context carefully
2. Determine if this is a REAL security violation or just:
   - Test data/example code
   - Placeholder/mock value
   - Documentation comment
   - Safe usage of a potentially dangerous function

3. Consider:
   - Is the code in a test file?
   - Is the value obviously fake (e.g., "xxx", "test", "example")?
   - Is this a demonstration or documentation?
   - Is the usage actually safe in this context?

Answer with ONLY "YES" if it's a real violation or "NO" if it's a false positive.
"""
            
            # Get response from Gemini
            response = model.generate_content(prompt)
            result = response.text.strip().upper()
            
            # Extract YES/NO from response
            if "YES" in result[:10]:
                LOGGER.info(f"Socratic Judge: REAL violation in {file_path}")
                return "YES"
            elif "NO" in result[:10]:
                LOGGER.info(f"Socratic Judge: False positive in {file_path}")
                return "NO"
            else:
                LOGGER.warning(f"Socratic Judge ambiguous response: {result}")
                return "YES"  # Default to safe
            
        except ImportError:
            LOGGER.warning("google.generativeai not installed - Socratic Judge disabled")
            return "YES"
        except Exception as e:
            LOGGER.error(f"Socratic Judge error: {e}")
            return "YES"  # Default to treating as violation
    
    def clear_false_positive_cache(self):
        """Clear the false positive cache."""
        self._false_positive_cache.clear()
        LOGGER.info("False positive cache cleared")


def create_overseer() -> ConstitutionalOverseer:
    """Factory function to create overseer instance."""
    return ConstitutionalOverseer()


def create_safety_inspector(enable_socratic_judge: bool = True) -> SafetyInspector:
    """Factory function to create SafetyInspector instance."""
    return SafetyInspector(enable_socratic_judge)