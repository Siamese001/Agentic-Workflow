"""
HallucinationDetectionMixin - V10 Epistemic Cascade Prevention.

Provides structural validation to prevent agents from acting on hallucinated
targets that don't exist in the actual codebase.

References:
- Verification Gate integration
- AST-based target validation
- Epistemic Cascade prevention (Landmine #2)
"""

import ast
import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)


class HallucinationDetectionMixin:
    """
    Mixin providing hallucination detection capabilities.

    Prevents Epistemic Cascade by verifying that action targets actually
    exist before allowing operations to proceed.

    MRO RULE: This mixin MUST precede base agent classes in inheritance.

    Usage:
        class MyAgent(HallucinationDetectionMixin, SovereignBaseAgent):
            pass
    """

    _hallucination_cache: dict[str, bool] = {}

    def verify_target_exists(self, file_path: Path, target_type: str, target_name: str) -> bool:
        """
        Verify that a target node exists in the file.

        Args:
            file_path: Path to the file to check
            target_type: Type of target ('function', 'class', 'import', 'variable')
            target_name: Name of the target to find

        Returns:
            True if target exists, False if hallucinated
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HallucinationDetectionMixin.verify_target_exists")

        if not file_path.exists():
            logger.warning(f"Hallucination check: file does not exist: {file_path}")
            return False
        cache_key = f"{file_path}:{target_type}:{target_name}"
        if cache_key in self._hallucination_cache:
            return self._hallucination_cache[cache_key]
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            result = self._find_target_in_ast(tree, target_type, target_name)
            self._hallucination_cache[cache_key] = result
            if not result:
                logger.warning(
                    f"Hallucination detected: {target_type} '{target_name}' not found in {file_path}"
                )
            return result
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.warning(f"Cannot parse {file_path} for hallucination check: {e}")
            return False

    def _find_target_in_ast(self, tree: ast.AST, target_type: str, target_name: str) -> bool:
        """Find target in AST based on type."""
        for node in ast.walk(tree):
            if target_type == "function":
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    if node.name == target_name:
                        return True
            elif target_type == "class":
                if isinstance(node, ast.ClassDef):
                    if node.name == target_name:
                        return True
            elif target_type == "import":
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == target_name or (alias.asname and alias.asname == target_name):
                            return True
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name == target_name or (alias.asname and alias.asname == target_name):
                            return True
            elif target_type == "variable":
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == target_name:
                            return True
        return False

    def clear_hallucination_cache(self) -> None:
        """Clear the hallucination detection cache."""
        self._hallucination_cache.clear()

    def get_hallucination_stats(self) -> dict[str, Any]:
        """Get statistics about hallucination detection."""
        return {
            "cache_size": len(self._hallucination_cache),
            "cached_targets": list(self._hallucination_cache.keys())[:10],
        }
