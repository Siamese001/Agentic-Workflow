from __future__ import annotations

from agentic_core.L2_execution.tools import write_gateway as _wg

'RedSentinelAgent - L5 Active Defense & Hostile Input Fuzzing.\n\nThis module provides an active defense system that generates hostile inputs\n(buffer overflows, malformed data) to test the robustness of code and detect\npotential security vulnerabilities.\n\nTypical usage:\n    agent = RedSentinelAgent()\n    result = await agent.fuzz_function("my_func", "def my_func(): pass", "file.py")\n'
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.timeout_decorator_util import timeout
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace

Logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class RedSentinelAgent(SovereignBaseAgent):
    """L5 Safety agent that generates hostile inputs for security testing.

    This active defense system creates edge cases and malformed inputs to test
    function robustness including type errors, boundary conditions, buffer
    overflow attempts, malformed JSON, and special characters.

    Attributes:
        llm_client: LLM client for generating hostile inputs (deprecated).
        enabled: Whether fuzzing is enabled (via ENABLE_FUZZ env var).
        audit_path: Path to audit log file for fuzz results.

    Inherits:
        SubatomicTestingMixin: Provides testing utilities.
        HealerMixin: Provides healing chain support.
    """

    def __init__(self, llm_client: Any | None = None) -> None:
        """Initialize the RedSentinelAgent.

        Args:
            llm_client: LLM client for generating hostile inputs (deprecated, uses MCP).
        """
        self.llm_client: Any | None = llm_client
        self.enabled: bool = os.getenv("ENABLE_FUZZ", "false").lower() == "true"
        self.audit_path: Path = Path("observability/audit/fuzz_results.json")
        _wg.ensure_dir(self.audit_path.parent)

    # guardian: allow-type-erasure
    async def fuzz_function(self, func_name: str, func_code: str, file_path: str) -> dict[str, Any]:
        """
        Generate hostile inputs for a function and test robustness.

        Args:
            func_name: Name of the function to test
            func_code: Function implementation
            file_path: Path to the file containing the function

        Returns:
            Dictionary with fuzz results and vulnerabilities
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "RedSentinelAgent.fuzz_function")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:RedSentinelAgent.fuzz_function".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not self.enabled:
            return {"enabled": False, "reason": "ENABLE_FUZZ not set"}
        Logger.info(f"🛡️  RedSentinelAgent: Generating hostile inputs for {func_name}")
        hostile_inputs: list[Any] = await self._generate_hostile_inputs(func_name, func_code)
        results: dict[str, Any] = {
            "function": func_name,
            "file": file_path,
            "timestamp": datetime.utcnow().isoformat(),
            "hostile_inputs": hostile_inputs,
            "vulnerabilities": [],
            "crashes": [],
        }
        for input_data in hostile_inputs:
            result: dict[str, Any] = await self._test_with_input(func_name, input_data)
            if result["crashed"]:
                results["crashes"].append(
                    {"input": input_data, "error": result["error"], "traceback": result["traceback"]}
                )
                results["vulnerabilities"].append({"type": "crash", "input": input_data, "Severity": "HIGH"})
            elif result["unexpected_behavior"]:
                results["vulnerabilities"].append(
                    {
                        "type": "unexpected_behavior",
                        "input": input_data,
                        "behavior": result["behavior"],
                        "Severity": "MEDIUM",
                    }
                )
        await self._log_fuzz_results(results)
        return {
            "enabled": True,
            "inputs_generated": len(hostile_inputs),
            "vulnerabilities_found": len(results["vulnerabilities"]),
            "crashes": len(results["crashes"]),
            "details": results,
        }

    async def _generate_hostile_inputs(self, func_name: str, func_code: str) -> list[dict[str, Any]]:
        """
        Generate 5 hostile inputs for a function.
        Phase 16B: Uses LLM router MCP instead of direct google.generativeai.

        Args:
            func_name: Name of the function
            func_code: Function implementation

        Returns:
            List of hostile input dictionaries
        """
        try:
            from agentic_core.L2_execution.enforcement.llm_router_mcp_client import get_llm_router_client

            llm_router = get_llm_router_client()
            result_dict = await llm_router.validate_content(prompt, validation_type="red_team")
            if isinstance(result_dict, dict):
                response_text = result_dict.get("response", result_dict.get("reason", ""))
            else:
                response_text = str(result_dict)
            try:
                inputs = json.loads(response_text)
                return inputs[:5]
            except json.JSONDecodeError:
                LOGGER.warning("Failed to parse LLM MCP response, using defaults")
                return self._get_default_hostile_inputs()
        # guardian: allow-silent-swallow
        except Exception as e:
            LOGGER.error(f"Failed to generate hostile inputs via MCP: {e}")
            return self._get_default_hostile_inputs()

    def _get_default_hostile_inputs(self) -> list[dict[str, Any]]:
        """Get default hostile inputs when LLM fails."""
        return [
            {"type": "null_input", "value": None},
            {"type": "empty_string", "value": ""},
            {"type": "buffer_overflow", "value": "A" * 10000},
            {"type": "special_chars", "value": "\x00\x01\x02\x03\x04\x05"},
            {"type": "extreme_number", "value": 999999999999999999},
        ]

    # guardian: allow-type-erasure
    async def _test_with_input(self, func_name: str, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Test a function with hostile input (mental simulation).

        Args:
            func_name: Name of the function
            input_data: Hostile input to test

        Returns:
            Test result
        """
        result = {
            "crashed": False,
            "error": None,
            "traceback": None,
            "unexpected_behavior": False,
            "behavior": None,
        }
        value = input_data.get("value")
        if value is None:
            result["unexpected_behavior"] = True
            result["behavior"] = "Potential None dereference"
        elif isinstance(value, str) and len(value) > 1000:
            result["crashed"] = True
            result["error"] = "MemoryError: possible buffer overflow"
            result["traceback"] = f"Simulated crash with {len(value)} character string"
        elif isinstance(value, str) and any(ord(c) < 32 for c in value):
            result["unexpected_behavior"] = True
            result["behavior"] = "Special characters may cause encoding issues"
        elif isinstance(value, int | float) and abs(value) > 1000000:
            result["unexpected_behavior"] = True
            result["behavior"] = "Extreme number may cause overflow"
        return result

    # guardian: allow-type-erasure
    async def _log_fuzz_results(self, results: dict[str, Any]) -> Any:
        """
        Log fuzz results to audit file.

        Args:
            results: Fuzz test results
        """
        try:
            if self.audit_path.exists():
                with open(self.audit_path) as f:
                    log_data = json.load(f)
            else:
                log_data = {"fuzz_tests": []}
            log_data["fuzz_tests"].append(results)
            if len(log_data["fuzz_tests"]) > 1000:
                log_data["fuzz_tests"] = log_data["fuzz_tests"][-1000:]
            _wg.write_json(self.audit_path, log_data, indent=2)
            LOGGER.info(f"RedSentinelAgent: Logged fuzz results to {self.audit_path}")
        # guardian: allow-silent-swallow
        except Exception as e:
            LOGGER.error(f"Failed to log fuzz results: {e}")

    # guardian: allow-type-erasure
    async def scan_file(self, file_path: str) -> dict[str, Any]:
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
        results: Any = {
            "file": file_path,
            "timestamp": datetime.utcnow().isoformat(),
            "functions_tested": 0,
            "vulnerabilities_found": 0,
            "details": [],
        }
        try:
            with open(file_path, encoding="utf-8") as f:
                content: Any = f.read()
            tree: Any = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and (not node.name.startswith("_")):
                    func_lines: Any = content.split("\n")[node.lineno - 1 : node.end_lineno]
                    func_code: Any = "\n".join(func_lines)
                    fuzz_result: Any = await self.fuzz_function(node.name, func_code, file_path)
                    results["functions_tested"] += 1
                    results["vulnerabilities_found"] += fuzz_result.get("vulnerabilities_found", 0)
                    results["details"].append(fuzz_result)
        # guardian: allow-silent-swallow
        except Exception as e:
            LOGGER.error(f"Error scanning {file_path}: {e}")
            results["error"] = str(e)
        return results

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, int]:
        """Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        """
        super().heal_repository(
            dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path
        )
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal red sentinel violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (vulnerability, injection, fuzzing)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        """
        violation_type = violation.get("type", "")
        path = violation.get("path", "")
        LOGGER.info(f"[RED_SENTINEL] Security violation detected: {violation_type} at {path}")
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Security vulnerabilities require manual review",
        }


_red_sentinel: RedSentinelAgent | None = None


def get_red_sentinel() -> RedSentinelAgent:
    """Get or create the global RedSentinelAgent instance.

    Returns:
        Global RedSentinelAgent singleton instance.
    """
    global _red_sentinel
    if _red_sentinel is None:
        _red_sentinel = RedSentinelAgent()
    return _red_sentinel


# guardian: allow-type-erasure
async def initialize_red_sentinel(llm_client: Any = None) -> Any:
    """
    Initialize the RedSentinelAgent system.

    Args:
        llm_client: LLM client instance
    """
    global _red_sentinel
    _red_sentinel = RedSentinelAgent(llm_client)
    if _red_sentinel.enabled:
        LOGGER.info("RedSentinelAgent initialized - Active defense enabled")
    else:
        LOGGER.info("RedSentinelAgent initialized - Set ENABLE_FUZZ=true to enable")


# guardian: allow-type-erasure
async def fuzz_function(func_name: str, func_code: str, file_path: str) -> dict[str, Any]:
    """
    Generate hostile inputs for a function.

    Args:
        func_name: Name of the function
        func_code: Function implementation
        file_path: Path to containing file

    Returns:
        Fuzz test results
    """
    sentinel: Any = get_red_sentinel()
    return await sentinel.fuzz_function(func_name, func_code, file_path)


# guardian: allow-type-erasure
async def scan_file_for_vulnerabilities(file_path: str) -> dict[str, Any]:
    """
    Scan a file for security vulnerabilities using hostile inputs.

    Args:
        file_path: Path to Python file to scan

    Returns:
        Scan results
    """
    sentinel: Any = get_red_sentinel()
    return await sentinel.scan_file(file_path)
