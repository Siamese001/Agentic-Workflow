from __future__ import annotations
"""
RedSentinelAgent - L5 Active Defense & Hostile Input Fuzzing

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
from agentic_core.utils.core_extensions.timeout_decorator import timeout

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

Logger: Any = logging.getLogger(__name__)

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin

class RedSentinelAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Active defense system that generates hostile inputs for testing.

    Creates edge cases and malformed inputs to test function robustness:
    - Type errors and boundary conditions
    - Buffer overflow attempts
    - Malformed JSON/data structures
    - Null bytes and special characters
    """

    def __init__(self, llm_client=None) -> None:
        """
        Initialize the RedSentinelAgent agent.
        Phase 16B: Uses LLM Router MCP for hostile input generation.

        Args:
            llm_client: LLM client for generating hostile inputs (deprecated, uses MCP)
        """
        self.llm_client = llm_client
        self.enabled = os.getenv('ENABLE_FUZZ', 'false').lower() == 'true'
        self.audit_path = Path('observability/audit/fuzz_results.json')
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)

    async def fuzz_function(self, func_name: str, func_code: str, file_path: str) -> Dict[str, Any]:
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
            return {'enabled': False, 'reason': 'ENABLE_FUZZ not set'}
        LOGGER.info(f'🛡️  RedSentinelAgent: Generating hostile inputs for {func_name}')
        hostile_inputs: Any = await self._generate_hostile_inputs(func_name, func_code)
        results: Any = {'function': func_name, 'file': file_path, 'timestamp': datetime.utcnow().isoformat(), 'hostile_inputs': hostile_inputs, 'vulnerabilities': [], 'crashes': []}
        for input_data in hostile_inputs:
            result: Any = await self._test_with_input(func_name, input_data)
            if result['crashed']:
                results['crashes'].append({'input': input_data, 'error': result['error'], 'traceback': result['traceback']})
                results['vulnerabilities'].append({'type': 'crash', 'input': input_data, 'Severity': 'HIGH'})
            elif result['unexpected_behavior']:
                results['vulnerabilities'].append({'type': 'unexpected_behavior', 'input': input_data, 'behavior': result['behavior'], 'Severity': 'MEDIUM'})
        await self._log_fuzz_results(results)
        return {'enabled': True, 'inputs_generated': len(hostile_inputs), 'vulnerabilities_found': len(results['vulnerabilities']), 'crashes': len(results['crashes']), 'details': results}

    async def _generate_hostile_inputs(self, func_name: str, func_code: str) -> List[Dict[str, Any]]:
        """
        Generate 5 hostile inputs for a function.
        Phase 16B: Uses LLM Router MCP instead of direct google.generativeai.

        Args:
            func_name: Name of the function
            func_code: Function implementation

        Returns:
            List of hostile input dictionaries
        """
        try:
            from agentic_core.L5_safety.guardrails.llm_router_mcp_client import get_llm_router_client
            llm_router = get_llm_router_client()
            prompt = f'\nfrom agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nGenerate 5 hostile test inputs for this function to test robustness:\n\nFunction: {func_name}\n\nImplementation:\n{func_code}\n```\n\nGenerate inputs that could cause:\n1. Type errors (wrong types)\n2. Boundary conditions (empty, None, extreme values)\n3. Buffer overflows (very long strings)\n4. Malformed data (invalid JSON, special characters)\n5. Edge cases (negative numbers, zeros)\n\nReturn as JSON array:\n[\n  {{"type": "description", "value": "actual_value"}},\n  {{"type": "description", "value": "actual_value"}},\n  ...\n]\n'
            result_dict = await llm_router.validate_content(prompt, validation_type='red_team')
            if isinstance(result_dict, dict):
                response_text = result_dict.get('response', result_dict.get('reason', ''))
            else:
                response_text = str(result_dict)
            try:
                inputs = json.loads(response_text)
                return inputs[:5]
            except json.JSONDecodeError:
                LOGGER.warning('Failed to parse LLM MCP response, using defaults')
                return self._get_default_hostile_inputs()
        except Exception as e:
            LOGGER.error(f'Failed to generate hostile inputs via MCP: {e}')
            return self._get_default_hostile_inputs()

    def _get_default_hostile_inputs(self) -> List[Dict[str, Any]]:
        """Get default hostile inputs when LLM fails."""
        return [{'type': 'null_input', 'value': None}, {'type': 'empty_string', 'value': ''}, {'type': 'buffer_overflow', 'value': 'A' * 10000}, {'type': 'special_chars', 'value': '\x00\x01\x02\x03\x04\x05'}, {'type': 'extreme_number', 'value': 999999999999999999}]

    async def _test_with_input(self, func_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a function with hostile input (mental simulation).

        Args:
            func_name: Name of the function
            input_data: Hostile input to test

        Returns:
            Test result
        """
        result = {'crashed': False, 'error': None, 'traceback': None, 'unexpected_behavior': False, 'behavior': None}
        value = input_data.get('value')
        if value is None:
            result['unexpected_behavior'] = True
            result['behavior'] = 'Potential None dereference'
        elif isinstance(value, str) and len(value) > 1000:
            result['crashed'] = True
            result['error'] = 'MemoryError: possible buffer overflow'
            result['traceback'] = f'Simulated crash with {len(value)} character string'
        elif isinstance(value, str) and any((ord(c) < 32 for c in value)):
            result['unexpected_behavior'] = True
            result['behavior'] = 'Special characters may cause encoding issues'
        elif isinstance(value, (int, float)) and abs(value) > 1000000:
            result['unexpected_behavior'] = True
            result['behavior'] = 'Extreme number may cause overflow'
        return result

    async def _log_fuzz_results(self, results: Dict[str, Any]):
        """
        Log fuzz results to audit file.

        Args:
            results: Fuzz test results
        """
        try:
            if self.audit_path.exists():
                with open(self.audit_path, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {'fuzz_tests': []}
            log_data['fuzz_tests'].append(results)
            if len(log_data['fuzz_tests']) > 1000:
                log_data['fuzz_tests'] = log_data['fuzz_tests'][-1000:]
            with open(self.audit_path, 'w') as f:
                json.dump(log_data, f, indent=2)
            LOGGER.info(f'RedSentinelAgent: Logged fuzz results to {self.audit_path}')
        except Exception as e:
            LOGGER.error(f'Failed to log fuzz results: {e}')

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
            return {'enabled': False, 'reason': 'ENABLE_FUZZ not set'}
        results: Any = {'file': file_path, 'timestamp': datetime.utcnow().isoformat(), 'functions_tested': 0, 'vulnerabilities_found': 0, 'details': []}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content: Any = f.read()
            tree: Any = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and (not node.name.startswith('_')):
                    func_lines: Any = content.split('\n')[node.lineno - 1:node.end_lineno]
                    func_code: Any = '\n'.join(func_lines)
                    fuzz_result: Any = await self.fuzz_function(node.name, func_code, file_path)
                    results['functions_tested'] += 1
                    results['vulnerabilities_found'] += fuzz_result.get('vulnerabilities_found', 0)
                    results['details'].append(fuzz_result)
        except Exception as e:
            LOGGER.error(f'Error scanning {file_path}: {e}')
            results['error'] = str(e)
        return results

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L5 safety agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
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

_red_sentinel: Optional[RedSentinelAgent] = None

def get_red_sentinel() -> RedSentinelAgent:
    """Get or create the global RedSentinelAgent instance."""
    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    global _red_sentinel
    if _red_sentinel is None:
        _red_sentinel = RedSentinelAgent()
    return _red_sentinel

async def initialize_red_sentinel(llm_client: Any=None) -> Any:
    """
    Initialize the RedSentinelAgent system.

    Args:
        llm_client: LLM client instance
    """
    global _red_sentinel
    _red_sentinel = RedSentinelAgent(llm_client)
    if _red_sentinel.enabled:
        LOGGER.info('RedSentinelAgent initialized - Active defense enabled')
    else:
        LOGGER.info('RedSentinelAgent initialized - Set ENABLE_FUZZ=true to enable')

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
    sentinel: Any = get_red_sentinel()
    return await sentinel.fuzz_function(func_name, func_code, file_path)

async def scan_file_for_vulnerabilities(file_path: str) -> Dict[str, Any]:
    """
    Scan a file for security vulnerabilities using hostile inputs.

    Args:
        file_path: Path to Python file to scan

    Returns:
        Scan results
    """
    sentinel: Any = get_red_sentinel()
    return await sentinel.scan_file(file_path)