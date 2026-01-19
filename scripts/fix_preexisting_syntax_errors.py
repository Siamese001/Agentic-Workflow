#!/usr/bin/env python3
"""
Fix Pre-existing Syntax Errors in the Codebase

These are known issues that exist in the committed code and need to be fixed
before any batch refactoring can be applied.
"""
from __future__ import annotations

import re
from pathlib import Path


def fix_file(file_path: Path, fixes: list) -> bool:
    """Apply fixes to a file.
    
    Args:
        file_path: Path to the file
        fixes: List of (old_string, new_string) tuples
        
    Returns:
        True if file was modified
    """
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    for old, new in fixes:
        content = content.replace(old, new)
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False


def main():
    root = Path(__file__).parent.parent
    
    fixes = {
        # 1. agent_capability_supplement.py - incomplete import
        root / "agentic_core/L0_maintenance/scripts/agent_capability_supplement.py": [
            (
                "from agent_discovery_audit import (\n\nfrom agentic_core.L5_safety.validators.structure_blueprint import (",
                "from agentic_core.L5_safety.validators.structure_blueprint import ("
            ),
            (
                "    get_validated_project_root,\n)\n    PROJECT_ROOT,\n    AGENTIC_CORE,\n    ASTNormalizer,\n    generate_fingerprint,\n)",
                "    PROJECT_ROOT,\n    AGENTIC_CORE,\n    get_validated_project_root,\n)"
            ),
        ],
        
        # 2. TestAgent.py - wrong indentation and duplicate code
        root / "agentic_core/L0_maintenance/scripts/TestAgent.py": [
            (
                "    return all_passed\n\n\ndef heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> Dict[str, Any]:\n            \"\"\"",
                "    return all_passed\n\n\n    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> Dict[str, Any]:\n        \"\"\""
            ),
            (
                "    return {\"violations\": 0, \"fixed\": 0, \"errors\": 0}\n            \n            Returns:\n                Dict with healing summary\n            \"\"\"\n            return {\"violations\": 0, \"fixed\": 0, \"errors\": 0}\n\ndef test_initialization_chain():",
                "    return {\"violations\": 0, \"fixed\": 0, \"errors\": 0}\n\n\ndef test_initialization_chain():"
            ),
        ],
        
        # 3. HistorianAgent.py - duplicate docstring
        root / "agentic_core/L2_execution/ToolRegistry/HistorianAgent.py": [
            (
                "        def on_modified(self, event) -> Any:\n           \"\"\"Execute on_modified operation.\"\"\"\n            \"\"\"Execute on_modified operation.\"\"\"\n            if event.is_directory: return",
                "        def on_modified(self, event) -> Any:\n            \"\"\"Execute on_modified operation.\"\"\"\n            if event.is_directory: return"
            ),
            (
                "        def on_modified(self, event) -> Any:\n           \"\"\"Execute on_modified operation.\"\"\"\n            \"\"\"Execute on_modified operation.\"\"\"\n            pass",
                "        def on_modified(self, event) -> Any:\n            \"\"\"Execute on_modified operation.\"\"\"\n            pass"
            ),
        ],
        
        # 4. MemoryLeakDetectorAgent.py - duplicate docstrings
        root / "agentic_core/L2_execution/ToolRegistry/MemoryLeakDetectorAgent.py": [
            (
                "    def visit_Module(self, node) -> Any:\n       \"\"\"Execute visit_Module operation.\"\"\"\n        \"\"\"Visit the module and analyze all functions.\"\"\"",
                "    def visit_Module(self, node) -> Any:\n        \"\"\"Visit the module and analyze all functions.\"\"\""
            ),
            (
                "    def visit_FunctionDef(self, node) -> Any:\n       \"\"\"Execute visit_FunctionDef operation.\"\"\"\n        \"\"\"Analyze a function for lock acquisition patterns.\"\"\"",
                "    def visit_FunctionDef(self, node) -> Any:\n        \"\"\"Analyze a function for lock acquisition patterns.\"\"\""
            ),
            (
                "    def visit_AsyncFunctionDef(self, node) -> Any:\n       \"\"\"Execute visit_AsyncFunctionDef operation.\"\"\"\n        \"\"\"Analyze async functions for lock patterns.\"\"\"",
                "    def visit_AsyncFunctionDef(self, node) -> Any:\n        \"\"\"Analyze async functions for lock patterns.\"\"\""
            ),
            (
                "    def visit_With(self, node) -> Any:\n       \"\"\"Execute visit_With operation.\"\"\"\n        \"\"\"Analyze 'with' statements for lock acquisitions.\"\"\"",
                "    def visit_With(self, node) -> Any:\n        \"\"\"Analyze 'with' statements for lock acquisitions.\"\"\""
            ),
            (
                "    def visit_Call(self, node) -> Any:\n       \"\"\"Execute visit_Call operation.\"\"\"\n        \"\"\"Check for .acquire() calls without timeout.\"\"\"",
                "    def visit_Call(self, node) -> Any:\n        \"\"\"Check for .acquire() calls without timeout.\"\"\""
            ),
        ],
        
        # 5. BenchmarkingAgent.py - duplicate docstrings
        root / "agentic_core/L3_orchestration/workflow_engines/BenchmarkingAgent.py": [
            (
                "        def decorator(func: Callable) -> Callable:\n           \"\"\"Execute decorator operation.\"\"\"\n            \"\"\"Execute decorator operation.\"\"\"\n            @wraps(func)\n            def wrapper(*args, **kwargs) -> Any:\n               \"\"\"Execute wrapper operation.\"\"\"\n                \"\"\"Execute wrapper operation.\"\"\"",
                "        def decorator(func: Callable) -> Callable:\n            \"\"\"Execute decorator operation.\"\"\"\n            @wraps(func)\n            def wrapper(*args, **kwargs) -> Any:\n                \"\"\"Execute wrapper operation.\"\"\""
            ),
            (
                "        def decorator(func: Callable) -> Callable:\n           \"\"\"Execute decorator operation.\"\"\"\n            \"\"\"Execute decorator operation.\"\"\"\n            @wraps(func)\n            async def wrapper(*args, **kwargs) -> Any:\n               \"\"\"Execute wrapper operation.\"\"\"\n                \"\"\"Execute wrapper operation.\"\"\"",
                "        def decorator(func: Callable) -> Callable:\n            \"\"\"Execute decorator operation.\"\"\"\n            @wraps(func)\n            async def wrapper(*args, **kwargs) -> Any:\n                \"\"\"Execute wrapper operation.\"\"\""
            ),
        ],
        
        # 6. OrchestrationHandshakeAgent.py - import inside multi-line import
        root / "agentic_core/L3_orchestration/workflow_engines/OrchestrationHandshakeAgent.py": [
            (
                "from agentic_core.L5_safety.validators.structure_blueprint import (\nfrom agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\n    SOVEREIGN_REGISTRY,",
                "from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\nfrom agentic_core.L5_safety.validators.structure_blueprint import (\n    SOVEREIGN_REGISTRY,"
            ),
        ],
        
        # 7. TracingAgent.py - duplicate docstrings
        root / "agentic_core/L3_orchestration/workflow_engines/TracingAgent.py": [
            (
                "    def end(self, status: str = \"SUCCESS\") -> None:\n       \"\"\"Execute end operation.\"\"\"\n        \"\"\"Execute end operation.\"\"\"",
                "    def end(self, status: str = \"SUCCESS\") -> None:\n        \"\"\"Execute end operation.\"\"\""
            ),
            (
                "    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:\n       \"\"\"Execute add_event operation.\"\"\"\n        \"\"\"Execute add_event operation.\"\"\"",
                "    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:\n        \"\"\"Execute add_event operation.\"\"\""
            ),
            (
                "    def set_attribute(self, key: str, value: Any) -> None:\n     \"\"\"Execute set_attribute operation.\"\"\"\n      \"\"\"Execute set_attribute operation.\"\"\"\n       \"\"\"Execute set_attribute operation.\"\"\"\n        \"\"\"Set a Span attribute.\"\"\"",
                "    def set_attribute(self, key: str, value: Any) -> None:\n        \"\"\"Set a Span attribute.\"\"\""
            ),
            (
                "    def set_attribute(self, span_id: str, key: str, value: Any) -> None:\n      \"\"\"Execute set_attribute operation.\"\"\"\n       \"\"\"Execute set_attribute operation.\"\"\"\n        \"\"\"Execute set_attribute operation.\"\"\"",
                "    def set_attribute(self, span_id: str, key: str, value: Any) -> None:\n        \"\"\"Set an attribute on a span.\"\"\""
            ),
            (
                "    def add_event(self, span_id: str, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:\n     \"\"\"Execute add_event operation.\"\"\"\n      \"\"\"Execute add_event operation.\"\"\"\n       \"\"\"Execute add_event operation.\"\"\"\n        \"\"\"Execute add_event operation.\"\"\"",
                "    def add_event(self, span_id: str, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:\n        \"\"\"Add an event to a span.\"\"\""
            ),
        ],
        
        # 8. ConstitutionalReviewerAgent.py - import inside multi-line import
        root / "agentic_core/L5_safety/guardrails/ConstitutionalReviewerAgent.py": [
            (
                "from agentic_core.L5_safety.validators.structure_blueprint import (\nfrom agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\n    AGENT_DISCOVERY_JSON,",
                "from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\nfrom agentic_core.L5_safety.validators.structure_blueprint import (\n    AGENT_DISCOVERY_JSON,"
            ),
        ],
        
        # 9. PromptInjectionDetectorAgent.py - import inside multi-line import
        root / "agentic_core/L5_safety/guardrails/PromptInjectionDetectorAgent.py": [
            (
                "from agentic_core.L5_safety.validators.structure_blueprint import (\nfrom agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\n    AGENT_DISCOVERY_JSON,",
                "from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\nfrom agentic_core.L5_safety.validators.structure_blueprint import (\n    AGENT_DISCOVERY_JSON,"
            ),
        ],
        
        # 10. BoundaryTestingAgent.py - import inside multi-line import
        root / "agentic_core/L5_safety/red_teaming/BoundaryTestingAgent.py": [
            (
                "from agentic_core.L5_safety.validators.structure_blueprint import (\nfrom agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\n    AGENT_DISCOVERY_JSON,",
                "from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\nfrom agentic_core.L5_safety.validators.structure_blueprint import (\n    AGENT_DISCOVERY_JSON,"
            ),
        ],
        
        # 11. ChaosEngineeringAgent.py - import inside multi-line import
        root / "agentic_core/L5_safety/red_teaming/ChaosEngineeringAgent.py": [
            (
                "from agentic_core.L5_safety.validators.structure_blueprint import (\nfrom agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\n    AGENT_DISCOVERY_JSON,",
                "from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\nfrom agentic_core.L5_safety.validators.structure_blueprint import (\n    AGENT_DISCOVERY_JSON,"
            ),
        ],
        
        # 12. PromptInjectionAgent.py - import inside multi-line import
        root / "agentic_core/L5_safety/red_teaming/PromptInjectionAgent.py": [
            (
                "from agentic_core.L5_safety.validators.structure_blueprint import (\nfrom agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\n    AGENT_DISCOVERY_JSON,",
                "from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\nfrom agentic_core.L5_safety.validators.structure_blueprint import (\n    AGENT_DISCOVERY_JSON,"
            ),
        ],
        
        # 13. GravityValidatorAgent.py - import inside multi-line import
        root / "agentic_core/L5_safety/validators/GravityValidatorAgent.py": [
            (
                "from agentic_core.L5_safety.validators.structure_blueprint import (\nfrom agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\n    CORE_SUBFOLDER_MAP,",
                "from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\nfrom agentic_core.L5_safety.validators.structure_blueprint import (\n    CORE_SUBFOLDER_MAP,"
            ),
        ],
        
        # 14. TypeHintEnforcementAgent.py - duplicate docstring
        root / "agentic_core/L5_safety/validators/TypeHintEnforcementAgent.py": [
            (
                "class TypeHintEnforcementAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):\n   \"\"\"TypeHintEnforcementAgent agent for autonomous operations.\"\"\"\n    \"\"\"\n    Ensures public functions, methods, and module-level assignments have type hints.",
                "class TypeHintEnforcementAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):\n    \"\"\"\n    Ensures public functions, methods, and module-level assignments have type hints."
            ),
        ],
        
        # 15. verify_patches.py - incomplete import
        root / "agentic_core/utils/core_extensions/verify_patches.py": [
            (
                "from import ALLOWED_CORE_STAGES, CANONICAL_DEPTH_MAP, validate_file_location",
                "from agentic_core.L5_safety.validators.structure_blueprint import ALLOWED_CORE_STAGES, CANONICAL_DEPTH_MAP, validate_file_location"
            ),
        ],
    }
    
    print("Fixing pre-existing syntax errors...")
    fixed_count = 0
    
    for file_path, file_fixes in fixes.items():
        if file_path.exists():
            if fix_file(file_path, file_fixes):
                print(f"  ✓ Fixed: {file_path.relative_to(root)}")
                fixed_count += 1
            else:
                print(f"  - No changes needed: {file_path.relative_to(root)}")
        else:
            print(f"  ✗ File not found: {file_path.relative_to(root)}")
    
    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
