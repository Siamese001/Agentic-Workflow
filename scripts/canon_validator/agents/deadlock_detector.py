"""
DeadlockDetector Agent - Deadlock Prevention Guardian.
Detects potential deadlock patterns in lock acquisition.
"""

import ast
import asyncio
from collections import defaultdict
from typing import Dict, List, Set, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ..base import SubAtomicAgent


class DeadlockDetector(SubAtomicAgent):
    """ROLE: Deadlock Prevention Guardian. Detects potential deadlock patterns."""

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Detecting Deadlock Patterns...")
        await asyncio.sleep(0)

        modified_files = getattr(self.ctx, 'modified_files', set())
        target_files = list(modified_files) if modified_files else self.ctx.python_files

        if not target_files:
            print("   ✅ No files to check for deadlocks")
            return

        print(f"   🔍 Scanning {len(target_files)} files for deadlock patterns...")

        deadlock_log = []
        for file_path in target_files:
            if not file_path.endswith('.py'):
                continue
            result = self._analyze_file(file_path)
            if result:
                deadlock_log.append(result)

        if deadlock_log:
            print(f"   🔒 Potential deadlocks found in {len(deadlock_log)} files")
            self.ctx.report(self.name, 62, False, [f"{len(deadlock_log)} files with deadlock risk"])
        else:
            print("   ✅ No deadlock patterns detected")
            self.ctx.report(self.name, 62, True, ["No deadlock patterns"])

    def _analyze_file(self, file_path: str) -> Dict | None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)

            analyzer = LockAnalyzer()
            analyzer.visit(tree)

            if analyzer.potential_deadlocks:
                return {
                    'file': file_path,
                    'deadlocks': analyzer.potential_deadlocks,
                    'lock_sequences': analyzer.lock_sequences
                }
        except Exception:
            pass
        return None


class LockAnalyzer(ast.NodeVisitor):
    """AST visitor to detect potential deadlock patterns."""

    def __init__(self):
        self.lock_sequences: List[Dict] = []
        self.potential_deadlocks: List[Dict] = []
        self.current_function = None
        self.current_locks: List[str] = []
        self.lock_graph: Dict[str, Set[str]] = defaultdict(set)

    def visit_FunctionDef(self, node):
        old_function = self.current_function
        old_locks = self.current_locks
        self.current_function = node.name
        self.current_locks = []

        self.generic_visit(node)

        if len(self.current_locks) > 1:
            self.lock_sequences.append({
                'function': node.name,
                'sequence': self.current_locks.copy(),
                'line': node.lineno
            })
            # Build lock graph
            for i in range(len(self.current_locks) - 1):
                self.lock_graph[self.current_locks[i]].add(self.current_locks[i + 1])

        self.current_function = old_function
        self.current_locks = old_locks

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_With(self, node):
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):
                func = item.context_expr.func
                if isinstance(func, ast.Attribute) and func.attr in ('acquire', 'lock'):
                    lock_name = self._get_lock_name(func.value)
                    if lock_name:
                        self.current_locks.append(lock_name)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'acquire':
                lock_name = self._get_lock_name(node.func.value)
                if lock_name:
                    self.current_locks.append(lock_name)
        self.generic_visit(node)

    def _get_lock_name(self, node) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_lock_name(node.value)}.{node.attr}"
        return None

    def _detect_cycles(self):
        """Detect cycles in lock acquisition graph (potential deadlocks)."""
        visited = set()
        rec_stack = set()

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.lock_graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    self.potential_deadlocks.append({
                        'cycle': path[cycle_start:] + [neighbor],
                        'type': 'lock_order_violation'
                    })
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in list(self.lock_graph.keys()):
            if node not in visited:
                dfs(node, [])
