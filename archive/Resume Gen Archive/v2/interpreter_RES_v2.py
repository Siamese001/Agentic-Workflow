# File: interpreter_RES_v2.py
# Code Interpreter Tool Module - V18 Architecture (Refactored)
# Version: 18.00 (Removed validate_word_count - moved to validator)
# This is a powerful and high-risk sandboxed tool

import json
import logging
import os
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

# ==============================================================================
# CODE INTERPRETER TOOL
# ==============================================================================

class CodeInterpreterTool:
    """
    Code Interpreter for deterministic operations on LLM outputs.
    Provides Python execution environment for validation and transformation tasks.
    This is a powerful and high-risk sandboxed tool that must be in its own module
    for clear isolation, security auditing, and maintenance.
    (Extracted from utils_RES_v2.py lines 651-809)
    """
    
    def __init__(self):
        """Initialize Code Interpreter."""
        self.enabled = True
        self.sandbox_globals = {
            'json': json,
            're': re,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'sorted': sorted,
            'sum': sum,
            'max': max,
            'min': min,
        }
    
    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute Python code in a sandboxed environment.
        
        Args:
            code: Python code to execute
            context: Optional context dictionary to inject into execution environment
            
        Returns:
            Result of the execution
            
        Raises:
            Exception: If code execution fails
        """
        if not self.enabled:
            raise RuntimeError("Code Interpreter is disabled")
        
        # Merge context with sandbox globals
        exec_globals = self.sandbox_globals.copy()
        if context:
            exec_globals.update(context)
        
        # Execute code and capture result
        exec_locals = {}
        try:
            exec(code, exec_globals, exec_locals)
        except Exception as e:
            logging.error(f"CodeInterpreter execution failed: {e}\nCode:\n{code}")
            raise
        
        # Return 'result' variable if it exists
        return exec_locals.get('result', None)

    def run(self, script: str) -> Tuple[bool, str]:
        """
        Runs a Python script in a sandboxed environment and captures stdout.
        This is the preferred method for complex operations.

        Args:
            script: The Python script to execute.

        Returns:
            Tuple[bool, str]: (success, output)
                             If success is True, output is the stdout.
                             If success is False, output is the stderr.
        """
        if not self.enabled:
            return False, "Code Interpreter is disabled"

        # Create a temporary file to hold the script
        try:
            with open("temp_code_interpreter_script.py", "w", encoding="utf-8") as f:
                f.write(script)

            # Execute the script using a subprocess with a timeout
            # This is safer as it isolates the execution completely
            result = subprocess.run(
                [sys.executable, "temp_code_interpreter_script.py"],
                capture_output=True,
                text=True,
                timeout=10,  # 10-second timeout
                encoding="utf-8"
            )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()

        except subprocess.TimeoutExpired:
            return False, "Code execution timed out (10 seconds)"
        except Exception as e:
            return False, f"Code execution failed: {e}"
        finally:
            # Clean up the temporary file
            if os.path.exists("temp_code_interpreter_script.py"):
                os.remove("temp_code_interpreter_script.py")

    def reorder_bullets_by_score(self, bullets: List[str], scores: List[float]) -> List[str]:
        """
        Reorders bullets by score deterministically.
        
        Args:
            bullets: List of bullet strings
            scores: List of relevance scores (same length as bullets)
            
        Returns:
            Reordered list of bullets
        """
        code = f"""
import json
bullets = {json.dumps(bullets)}
scores = {json.dumps(scores)}
paired = list(zip(bullets, scores))
sorted_pairs = sorted(paired, key=lambda x: x[1], reverse=True)
result = [bullet for bullet, score in sorted_pairs]
print(json.dumps(result))
"""
        success, output = self.run(code)
        if success:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return bullets # Return original on failure
        return bullets # Return original on failure
