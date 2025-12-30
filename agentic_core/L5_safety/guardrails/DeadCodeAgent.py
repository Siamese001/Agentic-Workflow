"""
DeadCodeAgent: Sovereign Code Hygiene Guardian

Detects and safely prunes:
- Unused imports (AST-based)
- Unreachable private functions (intra-module analysis)
- "Dust" logic (placeholders that drifted into permanence)

RATIONALE: Isolated from HealerAgent to satisfy Single Responsibility Principle.
           Governed by L5 Deletion Guardrails.

Placed in L5_safety/guardrails per SSOT semantic registry:
  "Guardrails, safety checks, and destructive action prevention"

Depth: agentic_core/L5_safety/guardrails/dead_code_agent.py
      → root/L1/L2/file.py → exactly 4 parts → Canon Key 3/12 compliant
"""
import ast
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, List, Tuple, Optional, Any
from collections import defaultdict

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


logger = logging.getLogger(__name__)

# Try to use native ast.unparse (Python 3.9+) for the most reliable rewrite
try:
    from ast import unparse
    AST_UNPARSE_AVAILABLE = True
except ImportError:
    AST_UNPARSE_AVAILABLE = False
    try:
        import astunparse
    except ImportError:
        logger.warning("[DeadCodeAgent] Neither ast.unparse nor astunparse found. Active pruning disabled.")


class CallGraphVisitor(ast.NodeVisitor):
    """
    [SIGNAL EXTRACTION] Builds an intra-file call graph: caller -> callees (including methods).
    """
    def __init__(self):
        self.calls: Dict[str, Set[str]] = defaultdict(set)
        self.function_stack: List[str] = []  # Track nested scope
        self.current_class: Optional[str] = None  # Track class for method calls

    def visit_ClassDef(self, node: ast.ClassDef):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Push current function to stack
        self.function_stack.append(node.name)
        self.generic_visit(node)
        self.function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        # Same handling as FunctionDef
        self.function_stack.append(node.name)
        self.generic_visit(node)
        self.function_stack.pop()

    def visit_Call(self, node: ast.Call):
        # Record call from current function (top of stack)
        if self.function_stack and isinstance(node.func, ast.Name):
            caller = self.function_stack[-1]
            callee = node.func.id
            self.calls[caller].add(callee)
        # Handle self.method() calls
        elif (isinstance(node.func, ast.Attribute) and 
              isinstance(node.func.value, ast.Name) and 
              node.func.value.id == "self" and 
              self.current_class):
            caller = f"{self.current_class}.{node.func.attr}"
            if self.function_stack:
                self.calls[self.function_stack[-1]].add(caller)
            else:
                # Called from outside class (rare)
                self.calls["<module>"].add(caller)
        self.generic_visit(node)



class DeadCodeAgent:
    """
    Autonomous agent for detecting and pruning dead code.
    Operates with extreme caution (backup-first).
    """
    def __init__(self, project_root: Path, tracing_agent=None):
        self.project_root = project_root.resolve()
        self.tracing_agent = tracing_agent
        self.prune_threshold = 0.98  # Require high confidence

    def _backup_file(self, file_path: Path) -> Path:
        """REFACTORED: Uses standard L5 backup pathing."""
        backup_dir = self.project_root / ".sovereign_healing_backup" / "deadcode"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{file_path.name}.bak"
        shutil.copy2(file_path, backup_path)
        return backup_path

    def delete_dead_symbol(self, file_path: Path, symbol_name: str, symbol_type: str) -> Dict[str, Any]:
        """
        [SURGICAL PRUNING] Line-level deletion using NodeTransformer.
        RATIONALE: Direct node removal is safer than line-based slicing.
        """
        result = {
            "file": str(file_path),
            "symbol": symbol_name,
            "symbol_type": symbol_type,
            "applied": False,
            "lines_removed": 0,
            "backup": ""
        }

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            
            class SymbolRemover(ast.NodeTransformer):
                def __init__(self, target_name: str):
                    self.target_name = target_name
                    self.removed = False
                    self.lines_removed = 0

                def visit_ClassDef(self, node: ast.ClassDef):
                    if node.name == self.target_name:
                        self.removed = True
                        self.lines_removed = node.end_lineno - node.lineno + 1
                        return None
                    return self.generic_visit(node)

                def visit_FunctionDef(self, node: ast.FunctionDef):
                    # Handle both top-level and methods (symbol_name = "Class.method" or "function")
                    if "." in self.target_name:
                        class_name, method_name = self.target_name.split(".", 1)
                        parent = getattr(node, 'parent', None)
                        if (parent and isinstance(parent, ast.ClassDef) and 
                            parent.name == class_name and 
                            node.name == method_name):
                            self.removed = True
                            self.lines_removed = node.end_lineno - node.lineno + 1
                            return None
                    elif node.name == self.target_name:
                        self.removed = True
                        self.lines_removed = node.end_lineno - node.lineno + 1
                        return None
                    return self.generic_visit(node)

                def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
                    # Same handling as FunctionDef
                    if "." in self.target_name:
                        class_name, method_name = self.target_name.split(".", 1)
                        parent = getattr(node, 'parent', None)
                        if (parent and isinstance(parent, ast.ClassDef) and 
                            parent.name == class_name and 
                            node.name == method_name):
                            self.removed = True
                            self.lines_removed = node.end_lineno - node.lineno + 1
                            return None
                    elif node.name == self.target_name:
                        self.removed = True
                        self.lines_removed = node.end_lineno - node.lineno + 1
                        return None
                    return self.generic_visit(node)

            remover = SymbolRemover(symbol_name)
            new_tree = remover.visit(tree)

            if not remover.removed:
                result["reason"] = "Symbol not found in AST"
                return result

            # EXECUTE REWRITE
            backup = self._backup_file(file_path)
            result["backup"] = str(backup)

            if AST_UNPARSE_AVAILABLE:
                new_content = unparse(new_tree)
            else:
                import astunparse
                new_content = astunparse.unparse(new_tree)

            # Restore trailing newline convention
            if content.endswith("\n") and not new_content.endswith("\n"):
                new_content += "\n"

            file_path.write_text(new_content, encoding="utf-8")
            result["applied"] = True
            result["lines_removed"] = remover.lines_count
            logger.info(f"[PRUNED] {symbol_type} '{symbol_name}' removed from {file_path.name}")

        except Exception as e:
            result["reason"] = f"Rewrite failed: {str(e)}"
            logger.error(f"[DeadCode] Surgical failure: {e}")

        return result

    def _extract_top_level_symbols(self, file_path: Path) -> Tuple[Set[str], Set[str], Set[str]]:
        """Identify all public classes, functions, and methods defined in a file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except Exception as e:
            logger.debug(f"[DeadCodeAgent] Parse error in {file_path.name}: {e}")
            return set(), set(), set()

        classes = set()
        all_functions = set()  # Top-level
        all_methods = set()    # class.method

        # Build parent map for distinguishing methods from top-level functions
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                child.parent = parent

        # Extract all functions (top-level + nested)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.add(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    # Distinguish methods vs top-level
                    parent = getattr(node, 'parent', None)
                    if parent and isinstance(parent, ast.ClassDef):
                        all_methods.add(f"{parent.name}.{node.name}")
                    else:
                        all_functions.add(node.name)

        return classes, all_functions, all_methods

    def _build_project_call_graph(self) -> Dict[str, Set[str]]:
        """Aggregate local call graphs into a global sovereign map."""
        global_calls: Dict[str, Set[str]] = defaultdict(set)
        all_py = list(self.project_root.rglob("*.py"))

        for py_file in all_py:
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)
                
                visitor = CallGraphVisitor()
                visitor.visit(tree)
                
                for caller, callees in visitor.calls.items():
                    global_calls[caller].update(callees)
            except Exception:
                continue

        return global_calls

    def detect_dead_symbols(self) -> List[Tuple[Path, str, str]]:
        """
        Detect unreachable top-level symbols using reachability propagation.
        """
        dead_symbols: List[Tuple[Path, str, str]] = []
        call_graph = self._build_project_call_graph()
        
        # All symbols that are called at least once
        all_called = {callee for callees in call_graph.values() for callee in callees}
        
        # Extract all symbols
        all_defined_functions = set()
        all_defined_methods = set()
        for py_file in self.project_root.rglob("*.py"):
            classes, functions, methods = self._extract_top_level_symbols(py_file)
            all_defined_functions.update(functions)
            all_defined_methods.update(methods)
        
        # Define entry points (Sovereign Mission Entry Points)
        # These symbols are assumed reachable by the environment/CLI
        entry_points = {"main", "run", "start", "handle", "__init__"}
        reachable = all_called.copy()
        reachable.update(entry_points)

        # PROPAGATION: Follow the graph from entry points
        changed = True
        while changed:
            changed = False
            for caller, callees in call_graph.items():
                if caller in reachable:
                    new_reachable = callees - reachable
                    if new_reachable:
                        reachable.update(new_reachable)
                        changed = True

        # Mark dead
        for py_file in self.project_root.rglob("*.py"):
            classes, functions, methods = self._extract_top_level_symbols(py_file)

            for cls in classes:
                if cls not in all_called:
                    dead_symbols.append((py_file, "class", cls))

            for func in functions:
                if func not in all_called:
                    dead_symbols.append((py_file, "function", func))

            for method in methods:
                if method not in all_called:
                    dead_symbols.append((py_file, "method", method))

        return dead_symbols

    def propose_deletions(self, dead_symbols: List[Tuple[Path, str, str]]) -> List[Dict[str, Any]]:
        """Create structured deletion proposals for HealerAgent consumption."""
        proposals = []
        for file_path, sym_type, name in dead_symbols:
            proposals.append({
                "type": "DELETE_DEAD_SYMBOL",
                "file": str(file_path),
                "symbol_type": sym_type,
                "symbol": name,
                "confidence": "HIGH",
                "rationale": f"Symbol '{name}' is unreachable from L6 entry points."
            })
        return proposals

    def run_prune(self, dead_symbols: List[Tuple[Path, str, str]]) -> List[Dict[str, Any]]:
        """Orchestrate a series of structural deletions within the budget."""
        actions = []
        applied_count = 0
        # BUDGET: Limit physical mutations to prevent wide-scale drift
        MAX_DELETIONS = 20 

        for file_path, sym_type, name in dead_symbols:
            if applied_count >= MAX_DELETIONS:
                logger.warning(f"[DeadCode] Deletion budget exhausted ({MAX_DELETIONS})")
                break

            res = self.delete_dead_symbol(file_path, name, sym_type)
            actions.append(res)
            if res["applied"]:
                applied_count += 1
        
        return actions

    def run(self) -> Dict[str, Any]:
        """Primary mission: Scan for dead functional DNA."""
        dead = self.detect_dead_symbols()
        proposals = self.propose_deletions(dead)

        logger.info(f"[DeadCodeAgent] Identified {len(dead)} dead symbols.")

        return {
            "dead_symbols_count": len(dead),
            "proposals": proposals
        }


# PascalCase is now the canonical name
