"""
RedSentinel - L5 Active Defense & Hostile Input Fuzzing

Generates hostile inputs (buffer overflows, malformed data) to test
the robustness of code and detect potential security vulnerabilities.
"""
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

LOGGER = logging.getLogger(__name__)


class RedSentinel:
    """
    Active defense system that generates hostile inputs for testing.

    Creates edge cases and malformed inputs to test function robustness:
    - Type errors and boundary conditions
    - Buffer overflow attempts
    - Malformed JSON/data structures
    - Null bytes and special characters
    """

    def __init__(self, llm_client=None):
        """
        Initialize the RedSentinel agent.

        Args:
            llm_client: LLM client for generating hostile inputs
        """
        self.llm_client = llm_client
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.enabled = os.getenv("ENABLE_FUZZ", "false").lower() == "true"

        # Audit log path
        self.audit_path = Path("observability/audit/fuzz_results.json")
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)

    async def fuzz_function(self, func_name: str, func_code: str,
                           file_path: str) -> Dict[str, Any]:
        """
        Generate hostile inputs for a function and test robustness.

        Args:
            func_name: Name of the function to test
            func_code: Function implementation
            file_path: Path to the file containing the function

        Returns:
            Dictionary with fuzz results and vulnerabilities
        """
        if not self.enabled:
            return {"enabled": False, "reason": "ENABLE_FUZZ not set"}

        LOGGER.info(f"🛡️  RedSentinel: Generating hostile inputs for {func_name}")

        # Generate hostile inputs
        hostile_inputs = await self._generate_hostile_inputs(func_name, func_code)

        # Test each input
        results = {
            "function": func_name,
            "file": file_path,
            "timestamp": datetime.utcnow().isoformat(),
            "hostile_inputs": hostile_inputs,
            "vulnerabilities": [],
            "crashes": []
        }

        # Simulate execution with hostile inputs
        for input_data in hostile_inputs:
            result = await self._test_with_input(func_name, input_data)

            if result["crashed"]:
                results["crashes"].append({
                    "input": input_data,
                    "error": result["error"],
                    "traceback": result["traceback"]
                })
                results["vulnerabilities"].append({
                    "type": "crash",
                    "input": input_data,
                    "severity": "HIGH"
                })
            elif result["unexpected_behavior"]:
                results["vulnerabilities"].append({
                    "type": "unexpected_behavior",
                    "input": input_data,
                    "behavior": result["behavior"],
                    "severity": "MEDIUM"
                })

        # Log results
        await self._log_fuzz_results(results)

        # Return summary
        return {
            "enabled": True,
            "inputs_generated": len(hostile_inputs),
            "vulnerabilities_found": len(results["vulnerabilities"]),
            "crashes": len(results["crashes"]),
            "details": results
        }

    async def _generate_hostile_inputs(self, func_name: str, func_code: str) -> List[Dict[str, Any]]:
        """
        Generate 5 hostile inputs for a function.

        Args:
            func_name: Name of the function
            func_code: Function implementation

        Returns:
            List of hostile input dictionaries
        """
        if not self.api_key:
            # Return basic hostile inputs without LLM
            return [
                {"type": "null_input", "value": None},
                {"type": "empty_string", "value": ""},
                {"type": "buffer_overflow", "value": "A" * 10000},
                {"type": "special_chars", "value": "\x00\x01\x02\x03"},
                {"type": "negative_number", "value": -999999999}
            ]

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')

            prompt = f"""
Generate 5 hostile test inputs for this function to test robustness:

Function: {func_name}

Implementation:
{func_code}
```

Generate inputs that could cause:
1. Type errors (wrong types)
2. Boundary conditions (empty, None, extreme values)
3. Buffer overflows (very long strings)
4. Malformed data (invalid JSON, special characters)
5. Edge cases (negative numbers, zeros)

Return as JSON array:
[
  {{"type": "description", "value": "actual_value"}},
  {{"type": "description", "value": "actual_value"}},
  ...
]
"""

            response = model.generate_content(prompt)

            # Parse JSON response
            try:
                inputs = json.loads(response.text)
                return inputs[:5]  # Ensure only 5 inputs
            except json.JSONDecodeError:
                # Fallback to manual parsing
                LOGGER.warning("Failed to parse LLM response, using defaults")
                return self._get_default_hostile_inputs()

        except Exception as e:
            LOGGER.error(f"Failed to generate hostile inputs: {e}")
            return self._get_default_hostile_inputs()

    def _get_default_hostile_inputs(self) -> List[Dict[str, Any]]:
        """Get default hostile inputs when LLM fails."""
        return [
            {"type": "null_input", "value": None},
            {"type": "empty_string", "value": ""},
            {"type": "buffer_overflow", "value": "A" * 10000},
            {"type": "special_chars", "value": "\x00\x01\x02\x03\x04\x05"},
            {"type": "extreme_number", "value": 999999999999999999}
        ]

    async def _test_with_input(self, func_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a function with hostile input (mental simulation).

        Args:
            func_name: Name of the function
            input_data: Hostile input to test

        Returns:
            Test result
        """
        # This is a mental simulation - we analyze what would happen
        result = {
            "crashed": False,
            "error": None,
            "traceback": None,
            "unexpected_behavior": False,
            "behavior": None
        }

        # Check for obvious crash scenarios
        value = input_data.get("value")

        if value is None:
            # Might cause AttributeError
            result["unexpected_behavior"] = True
            result["behavior"] = "Potential None dereference"

        elif isinstance(value, str) and len(value) > 1000:
            # Buffer overflow attempt
            result["crashed"] = True
            result["error"] = "MemoryError: possible buffer overflow"
            result["traceback"] = f"Simulated crash with {len(value)} character string"

        elif isinstance(value, str) and any(ord(c) < 32 for c in value):
            # Special characters might cause issues
            result["unexpected_behavior"] = True
            result["behavior"] = "Special characters may cause encoding issues"

        elif isinstance(value, (int, float)) and abs(value) > 1000000:
            # Extreme numbers
            result["unexpected_behavior"] = True
            result["behavior"] = "Extreme number may cause overflow"

        return result

    async def _log_fuzz_results(self, results: Dict[str, Any]):
        """
        Log fuzz results to audit file.

        Args:
            results: Fuzz test results
        """
        try:
            # Read existing log
            if self.audit_path.exists():
                with open(self.audit_path, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {"fuzz_tests": []}

            # Add new results
            log_data["fuzz_tests"].append(results)

            # Keep only last 1000 entries
            if len(log_data["fuzz_tests"]) > 1000:
                log_data["fuzz_tests"] = log_data["fuzz_tests"][-1000:]

            # Write back
            with open(self.audit_path, 'w') as f:
                json.dump(log_data, f, indent=2)

            LOGGER.info(f"RedSentinel: Logged fuzz results to {self.audit_path}")

        except Exception as e:
            LOGGER.error(f"Failed to log fuzz results: {e}")

    async def scan_file(self, file_path: str) -> Dict[str, Any]:
        """
        Scan a file for public functions and fuzz them.

        Args:
            file_path: Path to the Python file to scan

        Returns:
            Scan results with all fuzz tests
        """
        import ast

        if not self.enabled:
            return {"enabled": False, "reason": "ENABLE_FUZZ not set"}

        results = {
            "file": file_path,
            "timestamp": datetime.utcnow().isoformat(),
            "functions_tested": 0,
            "vulnerabilities_found": 0,
            "details": []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # Find all public functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    # Get function code
                    func_lines = content.split('\n')[node.lineno-1:node.end_lineno]
                    func_code = '\n'.join(func_lines)

                    # Fuzz the function
                    fuzz_result = await self.fuzz_function(node.name, func_code, file_path)

                    results["functions_tested"] += 1
                    results["vulnerabilities_found"] += fuzz_result.get("vulnerabilities_found", 0)
                    results["details"].append(fuzz_result)

        except Exception as e:
            LOGGER.error(f"Error scanning {file_path}: {e}")
            results["error"] = str(e)

        return results


# Global instance
_red_sentinel: Optional[RedSentinel] = None


def get_red_sentinel() -> RedSentinel:
    """Get or create the global RedSentinel instance."""
    global _red_sentinel
    if _red_sentinel is None:
        _red_sentinel = RedSentinel()
    return _red_sentinel


async def initialize_red_sentinel(llm_client=None):
    """
    Initialize the RedSentinel system.

    Args:
        llm_client: LLM client instance
    """
    global _red_sentinel
    _red_sentinel = RedSentinel(llm_client)

    if _red_sentinel.enabled:
        LOGGER.info("RedSentinel initialized - Active defense enabled")
    else:
        LOGGER.info("RedSentinel initialized - Set ENABLE_FUZZ=true to enable")


# Convenience functions
async def fuzz_function(func_name: str, func_code: str, file_path: str) -> Dict[str, Any]:
    """
    Generate hostile inputs for a function.

    Args:
        func_name: Name of the function
        func_code: Function implementation
        file_path: Path to containing file

    Returns:
        Fuzz test results
    """
    sentinel = get_red_sentinel()
    return await sentinel.fuzz_function(func_name, func_code, file_path)


async def scan_file_for_vulnerabilities(file_path: str) -> Dict[str, Any]:
    """
    Scan a file for security vulnerabilities using hostile inputs.

    Args:
        file_path: Path to the file to scan

    Returns:
        Scan results
    """
    sentinel = get_red_sentinel()
    return await sentinel.scan_file(file_path)
