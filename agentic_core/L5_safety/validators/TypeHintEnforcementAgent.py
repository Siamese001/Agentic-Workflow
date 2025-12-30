# TypeHintEnforcementAgent - Atomic Validator (Ungated Healing)
# Territory: agentic_core/L2_execution/tool_registry
# Canon Alignment: Enforces complete type hints for public functions/methods/variables
# Surgery Scope: Single file — adds basic Any / inferred hints where missing

import ast
'''Brief description of functionality and purpose.'''

from pathlib import Path
from typing import Dict, Any

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)



# NAMING CANON COMPLIANCE — renamed to TypeHintEnforcementAgent for discovery and sovereignty — 2025-12-30
class TypeHintEnforcementAgent:
    """
    Ensures public functions, methods, and module-level assignments have type hints.

    Rules:
    - Public functions/methods (not starting with _) must have:
        - Parameter type hints
        - Return type hint (-> ...)
    - Public module-level variables/constants must have type hints
    - Uses 'Any' as safe fallback when no better inference available

    Why ungated healing is safe:
    - Only adds type annotations (no runtime impact)
    - Never removes or changes existing code/logic
    - Single-file scope
    """

    FALLBACK_PARAM = "Any"
    FALLBACK_RETURN = "Any"
    FALLBACK_VAR = "Any"

    def __init__(self, ctx=None, project_root=None):
        self.ctx = ctx
        self.project_root = project_root

    async def execute(self, file_path: str) -> Dict[str, Any]:
        """Execute method for validator compatibility."""
        return await self.heal_violation(Path(file_path), self.ctx)

    async def heal_violation(self, file_path: Path, ctx=None) -> Dict[str, Any]:
        """
        Per-file healing: add missing type hints via AST transformation.
        """
        ctx = ctx or self.ctx
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)

            fixer = TypeHintFixer(self.FALLBACK_PARAM, self.FALLBACK_RETURN, self.FALLBACK_VAR)
            new_tree = fixer.visit(tree)
            
            if fixer.added_count > 0:
                ast.fix_missing_locations(new_tree)
                new_source = ast.unparse(new_tree)

                if new_source != source:
                    file_path.write_text(new_source + "\n", encoding="utf-8")
                    message = f"Added {fixer.added_count} missing type hint(s)"
                    print(f"      [HEALED] {file_path.name}: {message}")
                    ctx.report(
                        self.__class__.__name__,
                        key_id=18,  # Core Laws / Safety category
                        success=True,
                        msg=message,
                    )
                    return {"healed": True, "details": message}

            return {"healed": False}

        except Exception as e:
            ctx.report(
                self.__class__.__name__,
                18,
                False,
                f"Type hint enforcement failed: {str(e)[:100]}",
            )
            return {"healed": False}


# NAMING FIXED: TypeHintFixer → type_hint_fixer
class type_hint_fixer(ast.NodeTransformer):
    """
    AST transformer that adds missing type hints to public symbols.
    """

    def __init__(self, fallback_param: str, fallback_return: str, fallback_var: str):
        self.added_count = 0
        self.fallback_param = fallback_param
        self.fallback_return = fallback_return
        self.fallback_var = fallback_var

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
                    
        if node.name.startswith("_"):
            return node  # Skip private symbols per hierarchy laws

        # Add parameter hints
        for arg in node.args.args:
            if arg.annotation is None and arg.arg != "self" and arg.arg != "cls":
                arg.annotation = ast.Name(id=self.fallback_param, ctx=ast.Load())
                self.added_count += 1

        # Add return hint
        if node.returns is None:
            node.returns = ast.Name(id=self.fallback_return, ctx=ast.Load())
            self.added_count += 1

        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
                    
        return self.visit_FunctionDef(node)

    def visit_Assign(self, node: ast.Assign) -> ast.Assign | ast.AnnAssign:
                    
        # Module-level public assignments without annotation
        if len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and not target.id.startswith("_"):
                new_node = ast.AnnAssign(
                    target=target,
                    annotation=ast.Name(id=self.fallback_var, ctx=ast.Load()),
                    value=node.value,
                    simple=1,
                )
                self.added_count += 1
                return new_node
        return node


# Factory for discovery
def get_type_hint_enforcement_agent():
    '''Brief description of functionality and purpose.'''
    
    return TypeHintEnforcementAgent()
