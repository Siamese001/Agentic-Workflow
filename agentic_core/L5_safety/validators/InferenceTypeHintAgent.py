import ast
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from pathlib import Path
from typing import Dict, Any, List, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

# NAMING CANON ABSOLUTE — renamed for eternal sovereign discovery — Phase 4 — 2025-12-30
class InferenceTypeHintAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Uses LLM inference to add accurate type hints to functions/methods.

    Why gated (not ungated):
    - Invokes SubAtomicEngine → API cost and rate limits
    - Higher risk of hallucinated types (mitigated by safety guardrail)
    - Best used in focused healing missions, not daily runs

    Strategy:
    - Extract functions without full type hints
    - Prompt SubAtomicEngine for precise annotations
    - Apply via AST + unparse (preserves formatting)
    """
    PROMPT_TEMPLATE: str = '\nfrom agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\nAdd precise Python type hints to the following function/method.\n\nRules:\n- Use concrete types when possible (List[str], Dict[str, int], etc.)\n- Use from __future__ import annotations if needed\n- Preserve all existing code, comments, and formatting\n- Only modify type annotations (parameters and return)\n- If uncertain, use Any from typing\n\nOutput ONLY the fully annotated function (no explanations, no markdown).\n\nFUNCTION:\n{code}\n'

    def __init__(self, ctx: Any, project_root: Optional[str] = None) -> None:
        """
        Initialize with mandatory ctx for sovereign operation.
        
        Args:
            ctx: Execution context (mandatory)
            project_root: Optional project root directory
        
        Raises:
            ValueError: If ctx is None
        """
        if ctx is None:
            raise ValueError("ctx is mandatory for InferenceTypeHintAgent (sovereign agent)")
        self.ctx = ctx
        self.project_root = project_root

    async def execute(self, file_path: str) -> Dict[str, Any]:
        """
        Execute method for validator compatibility.
        
        Args:
            file_path: Path to file to validate
        
        Returns:
            Dict with healed status
        """
        return await self.heal_violation(Path(file_path), self.ctx)

    async def heal_violation(self, file_path: Path, ctx: Optional[Any] = None) -> Dict[str, Any]:
        """
        Per-file healing: invoke LLM for precise type inference.
        
        Args:
            file_path: Path to file to heal
            ctx: Optional execution context (uses self.ctx if None)
        
        Returns:
            Dict with healed status and functions annotated count
        """
        ctx = ctx or self.ctx
        if not getattr(ctx, 'RUN_HIERARCHY_HEALING', False):
            return {'healed': False}
        if not hasattr(ctx, 'engine') or ctx.engine is None:
            print(f'   [!] InferenceTypeHintAgent: SubAtomicEngine not available')
            return {'healed': False}
        try:
            source: str = file_path.read_text(encoding='utf-8')
            tree: ast.Module = ast.parse(source)
            targets: List[Dict] = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name.startswith('_'):
                        continue
                    missing_param: bool = any((arg.annotation is None for arg in node.args.args if arg.arg not in ('self', 'cls')))
                    missing_return: bool = node.returns is None
                    if missing_param or missing_return:
                        code_segment: Optional[str] = ast.get_source_segment(source, node)
                        if code_segment:
                            targets.append({'node': node, 'code': code_segment, 'lineno': node.lineno})
            if not targets:
                return {'healed': False}
            healed_count: Any = 0
            lines: Any = source.splitlines(keepends=True)
            for target in reversed(targets):
                prompt: Any = self.PROMPT_TEMPLATE.format(code=target['code'])
                try:
                    inferred_code: Any = await ctx.engine.resilient_mutation(file_path=str(file_path), code=target['code'], Task=prompt, round_num=1, fission_active=False)
                    if isinstance(inferred_code, str):
                        inferred_code: Any = inferred_code.strip()
                        if inferred_code.startswith('```'):
                            inferred_code: Any = '\n'.join(inferred_code.splitlines()[1:-1])
                    start_idx: Any = target['lineno'] - 1
                    end_idx: Any = start_idx + target['code'].count('\n') + 1
                    original_block: Any = ''.join(lines[start_idx:end_idx])
                    if inferred_code and inferred_code != original_block.strip():
                        indent: Any = lines[start_idx][:len(lines[start_idx]) - len(lines[start_idx].lstrip())]
                        indented_inferred: Any = '\n'.join((indent + l if i > 0 else l for i, l in enumerate(inferred_code.splitlines())))
                        lines[start_idx:end_idx] = [indented_inferred + '\n']
                        healed_count += 1
                except Exception as e:
                    print(f"      [!] LLM inference failed for {file_path.name}:{target['lineno']}: {e}")
                    continue
            if healed_count > 0:
                new_content: Any = ''.join(lines)
                file_path.write_text(new_content, encoding='utf-8')
                message: Any = f'Inferred {healed_count} precise type hint(s) via LLM'
                print(f'      [HEALED] {file_path.name}: {message}')
                ctx.report(self.__class__.__name__, 18, True, message)
                return {'status': 'complete', 'added_hints': len(targets)}
            return {'healed': False}
        except Exception as e:
            ctx.report(self.__class__.__name__, 18, False, f'Inference healing failed: {str(e)[:100]}')
            return {'healed': False}

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """Operational validator - requires LLM context."""
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
            print(f"[{agent_name}] Requires LLM context - operational mode only")
            return {"skipped": 1, "requires_llm": True}
        finally:
            _call_path.discard(agent_name)

def get_inference_type_hint_agent() -> Any:
    """Brief description of functionality and purpose."""
    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    return InferenceTypeHintAgent()
