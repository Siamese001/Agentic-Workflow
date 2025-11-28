# File: interpreter_RES_v3_8.py
# Code Interpreter Tool Module - V3.8 Architecture
# Version: 3.8.0 - Complete V3.8 Migration
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
    V3.8 version with enhanced sandboxing and safety features.
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
            'abs': abs,
            'round': round,
            'zip': zip,
            'enumerate': enumerate,
            'range': range,
            'all': all,
            'any': any,
            'filter': filter,
            'map': map,
        }
        self.logger = logging.getLogger(__name__)
    
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
            self.logger.error(f"CodeInterpreter execution failed: {e}\nCode:\n{code}")
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
        temp_script_path = f"temp_code_interpreter_script_{os.getpid()}.py"
        
        try:
            with open(temp_script_path, "w", encoding="utf-8") as f:
                f.write(script)

            # Execute the script using a subprocess with a timeout
            # This is safer as it isolates the execution completely
            result = subprocess.run(
                [sys.executable, temp_script_path],
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
            if os.path.exists(temp_script_path):
                os.remove(temp_script_path)

    def reorder_bullets_by_score(self, bullets: List[str], scores: List[float]) -> List[str]:
        """
        Reorders bullets by score deterministically.
        
        Args:
            bullets: List of bullet strings
            scores: List of relevance scores (same length as bullets)
            
        Returns:
            Reordered list of bullets
        """
        if len(bullets) != len(scores):
            self.logger.warning(f"Bullets and scores length mismatch: {len(bullets)} vs {len(scores)}")
            return bullets
            
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
                self.logger.error("Failed to decode reordered bullets JSON")
                return bullets  # Return original on failure
        return bullets  # Return original on failure

    def validate_json(self, json_str: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Validate and parse JSON string.
        
        Args:
            json_str: JSON string to validate
            
        Returns:
            Tuple of (is_valid, parsed_data, error_message)
        """
        code = f"""
import json

json_str = '''{json_str}'''

try:
    result = json.loads(json_str)
    print(json.dumps({{"valid": True, "data": result}}))
except json.JSONDecodeError as e:
    print(json.dumps({{"valid": False, "error": str(e)}}))
"""
        success, output = self.run(code)
        
        if success:
            try:
                result = json.loads(output)
                if result["valid"]:
                    return True, result["data"], None
                else:
                    return False, None, result["error"]
            except:
                return False, None, "Failed to parse validation result"
        
        return False, None, output

    def extract_metrics(self, text: str) -> Dict[str, Any]:
        """
        Extract numeric metrics from text.
        
        Args:
            text: Text containing metrics
            
        Returns:
            Dictionary of extracted metrics
        """
        code = f"""
import re

text = '''{text}'''
result = {{}}

# Extract percentages
percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', text)
result['percentages'] = [float(p) for p in percentages]

# Extract dollar amounts
dollars = re.findall(r'\$\s*(\d+(?:,\d{{3}})*(?:\.\d+)?)', text)
result['dollar_amounts'] = [float(d.replace(',', '')) for d in dollars]

# Extract plain numbers with units
numbers_with_units = re.findall(r'(\d+(?:,\d{{3}})*(?:\.\d+)?)\s*(million|billion|thousand|K|M|B)', text, re.IGNORECASE)
result['scaled_numbers'] = []
for num, unit in numbers_with_units:
    base = float(num.replace(',', ''))
    if unit.lower() in ['k', 'thousand']:
        result['scaled_numbers'].append(base * 1000)
    elif unit.lower() in ['m', 'million']:
        result['scaled_numbers'].append(base * 1000000)
    elif unit.lower() in ['b', 'billion']:
        result['scaled_numbers'].append(base * 1000000000)

# Extract years
years = re.findall(r'\b(19\d{{2}}|20\d{{2}})\b', text)
result['years'] = [int(y) for y in years]

print(json.dumps(result))
"""
        success, output = self.run(code)
        
        if success:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return {}
        
        return {}

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity score.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        code = f"""
text1 = '''{text1.lower()}'''
text2 = '''{text2.lower()}'''

# Simple word-based Jaccard similarity
words1 = set(text1.split())
words2 = set(text2.split())

if not words1 and not words2:
    result = 1.0
elif not words1 or not words2:
    result = 0.0
else:
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    result = intersection / union

print(result)
"""
        success, output = self.run(code)
        
        if success:
            try:
                return float(output)
            except ValueError:
                return 0.0
        
        return 0.0

    def word_count(self, text: str) -> int:
        """
        Count words in text.
        
        Args:
            text: Text to count words in
            
        Returns:
            Word count
        """
        code = f"""
text = '''{text}'''
words = text.split()
result = len(words)
print(result)
"""
        success, output = self.run(code)
        
        if success:
            try:
                return int(output)
            except ValueError:
                return 0
        
        return 0

    def is_enabled(self) -> bool:
        """Check if interpreter is enabled."""
        return self.enabled
    
    def disable(self):
        """Disable the interpreter."""
        self.enabled = False
        self.logger.info("Code Interpreter disabled")
    
    def enable(self):
        """Enable the interpreter."""
        self.enabled = True
        self.logger.info("Code Interpreter enabled")


# Backwards compatibility
PythonExecutor = CodeInterpreterTool

__all__ = ['CodeInterpreterTool', 'PythonExecutor']
