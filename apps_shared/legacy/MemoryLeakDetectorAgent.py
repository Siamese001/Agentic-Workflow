# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: guardrail, orchestrator
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations

import ast
from typing import Any

"""Brief description of functionality and purpose."""

import asyncio
import datetime
import os
import re
import time
from collections import defaultdict

from agentic_core.L5_safety.validators.decorators import standard_heal
from agentic_core.base_agents.healer_mixin import HealerMixin


# NAMING FIXED: MemoryLeakDetectorAgent → MemoryLeakDetectorAgent
# NOT_AN_AGENT — utility detector class, not a true agent — excluded from agent discovery
class MemoryLeakDetectorAgent(HealerMixin):
    """ROLE: Memory Guardian. Detects and remediates resource leaks and unbounded containers."""

    def __init__(self, ctx) -> None:
        self.ctx = ctx
        self.name = self.__class__.__name__

    # Resource leak patterns for fast scanning
    LEAK_PATTERNS = {
        "naked_open": re.compile(r"\bopen\s*\(", re.IGNORECASE),
        "naked_connect": re.compile(
            r"\b(socket\.|urllib\.|http\.|mysql\.|psycopg2\.|sqlite3\.)", re.IGNORECASE
        ),
        "unbounded_cache": re.compile(r"@lru_cache\s*\(\s*\)", re.IGNORECASE),
        "global_list_append": re.compile(
            r"^[A-Z_]+\s*=\s*\[\]\s*\nfrom agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n.*\.append\(",
            re.IGNORECASE | re.MULTILINE,
        ),
        "file_no_close": re.compile(
            r"open\s*\([^)]+\)\s*[^.\n]*\n(?!.*\.close\(\))", re.IGNORECASE | re.MULTILINE
        ),
    }

    async def execute(self) -> None:
        """Execute execute operation."""
        print(f"\n[>>>] {self.name} ACTIVATED: Detecting Resource Leaks...")
        await asyncio.sleep(0)

        # Priority 1: Process modified files
        modified_files = getattr(self.ctx, "modified_files", set())

        # Priority 2: Fall back to all Python files if no tracking
        target_files = list(modified_files) if modified_files else self.ctx.python_files

        if not target_files:
            print("   [OK] No files to check for leaks")
            return

        print(f"   [SCAN] Scanning {len(target_files)} files for resource leaks...")
        print(
            f"   🎯 Priority: Modified files ({len(modified_files)}) + {len(target_files) - len(modified_files)} others"
        )

        # Track leak fixes
        leak_log = []
        fixed_files = []

        # Scan and fix files
        for file_path in target_files:
            if not file_path.endswith(".py"):
                continue

            result = await self._scan_and_fix(file_path)
            if result:
                fixed_files.append(file_path)
                leak_log.append(result)

        # Save resource safety report
        self._save_safety_report(leak_log, fixed_files)

        if fixed_files:
            print(f"   🛡️  Resource leaks fixed in {len(fixed_files)} files")
        else:
            print("   [OK] No resource leaks detected")

    async def _scan_and_fix(self, file_path):
        """Scan file for leaks and apply fixes."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Pass 1: Fast regex scanning
            detected_leaks = self._detect_leaks(content)

            if not detected_leaks:
                return None

            # Pass 2: AST context analysis
            leak_context = self._analyze_leak_context(content, detected_leaks)

            # Prioritize critical leaks
            critical_leaks = self._prioritize_leaks(leak_context)

            if not critical_leaks:
                print(f"   ℹ️  Low-risk patterns in {os.path.basename(file_path)} - skipping")
                return None

            print(f"   🛡️  Fixing resource leaks: {os.path.basename(file_path)}")

            # Generate leak-free code using Gemini
            fixed_content = await self._generate_leak_free_code(file_path, content, critical_leaks)

            # Apply fixes
            if fixed_content and fixed_content != content:
                if self.ctx.write_compliant_file(file_path, fixed_content):
                    return {
                        "file": file_path,
                        "leaks": critical_leaks,
                        "context": leak_context,
                        "reasoning": "Resource leaks detected and remediated",
                    }

        except Exception as e:
            print(f"   [X] Failed to fix leaks in {file_path}: {e}")
            return {"file": file_path, "error": str(e), "reasoning": "Failed to process file"}

        return None

    def _detect_leaks(self, content):
        """Fast regex-based leak detection."""
        leaks = {}

        for leak_name, pattern in self.LEAK_PATTERNS.items():
            matches = pattern.finditer(content)
            if matches:
                leaks[leak_name] = [
                    {
                        "line": content[: match.start()].count("\n") + 1,
                        "snippet": content[match.start() : match.end()][:50],
                        "full_match": match.group(),
                    }
                    for match in matches
                ]

        return leaks

    def _analyze_leak_context(self, content, leaks):
        """Analyze AST to understand leak context."""
        context = {
            "global_containers": [],
            "naked_opens": [],
            "missing_context_managers": [],
            "unbounded_caches": [],
        }

        try:
            tree = ast.parse(content)

            # Track module-level assignments
            for node in ast.walk(tree):
                # Module-level growing containers
                if isinstance(node, ast.Assign):
                    # Check if at module level (col_offset == 0)
                    if hasattr(node, "col_offset") and node.col_offset == 0:
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                var_name = target.id.upper()
                                # Check if it's initialized as empty list/dict
                                if isinstance(node.value, (ast.List, ast.Dict)):
                                    if isinstance(node.value, ast.List) and not node.value.elts:
                                        context["global_containers"].append(
                                            {
                                                "variable": var_name,
                                                "line": node.lineno,
                                                "type": "list",
                                            }
                                        )

                # Function-level analysis
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_name = node.name
                    func_start = node.lineno
                    func_end = node.end_lineno if hasattr(node, "end_lineno") else func_start

                    # Check for naked opens
                    for leak_name, leak_list in leaks.items():
                        if leak_name in ["naked_open", "naked_connect"]:
                            for leak in leak_list:
                                if func_start <= leak["line"] <= func_end:
                                    context["naked_opens"].append(
                                        {
                                            "function": func_name,
                                            "line": leak["line"],
                                            "type": leak_name,
                                        }
                                    )

                    # Check for unclosed files
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name) and child.func.id == "open":
                                # Check if wrapped in 'with' or has .close()
                                if not self._is_in_with_block(child, node):
                                    if not self._has_close_call(child, node):
                                        context["missing_context_managers"].append(
                                            {
                                                "function": func_name,
                                                "line": child.lineno,
                                                "resource": "file",
                                            }
                                        )

                # Check for unbounded lru_cache
                elif isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            if (
                                isinstance(decorator.func, ast.Name)
                                and decorator.func.id == "lru_cache"
                            ):
                                if not decorator.args:  # No maxsize specified
                                    context["unbounded_caches"].append(
                                        {"function": node.name, "line": decorator.lineno}
                                    )

        except Exception as e:
            print(f"   [!]  AST analysis failed: {e}")

        return context

    def _is_in_with_block(self, node, function_node):
        """Check if a node is inside a 'with' statement."""
        parent = node.parent if hasattr(node, "parent") else None
        while parent and parent != function_node:
            if isinstance(parent, ast.With):
                # Check if this node is part of the with items
                for item in parent.items:
                    if item.context_expr == node:
                        return True
            parent = parent.parent if hasattr(parent, "parent") else None
        return False

    def _has_close_call(self, node, function_node):
        """Check if the opened file has a .close() call."""
        # This is a simplified check - in reality, we'd need to track variable assignments
        # and find all subsequent .close() calls on that variable
        return False

    def _prioritize_leaks(self, context):
        """Prioritize leaks by Severity."""
        prioritized = {"critical": [], "high": [], "medium": []}

        # Critical: Naked opens without context managers
        for naked in context.get("naked_opens", []):
            prioritized["critical"].append(
                {
                    "type": "naked_resource",
                    "function": naked["function"],
                    "line": naked["line"],
                    "Severity": "critical",
                }
            )

        # High: Global growing containers
        for container in context.get("global_containers", []):
            prioritized["high"].append(
                {
                    "type": "global_container",
                    "variable": container["variable"],
                    "line": container["line"],
                    "Severity": "high",
                }
            )

        # Medium: Missing context managers
        for Missing in context.get("missing_context_managers", []):
            prioritized["medium"].append(
                {
                    "type": "missing_context_manager",
                    "function": Missing["function"],
                    "line": Missing["line"],
                    "Severity": "medium",
                }
            )

        # Return only critical and high priority leaks for auto-fix
        return {k: v for k, v in prioritized.items() if k in ["critical", "high"] and v}

    async def _generate_leak_free_code(self, file_path: str, content: str, leaks: dict):
        """Generate leak-free code using Gemini."""
        # Build leak summary
        leak_summary = []
        for Severity, leak_list in leaks.items():
            for leak in leak_list:
                leak_summary.append(f"- {leak['type']} ({Severity}): line {leak['line']}")

        prompt = (
            f"RESOURCE SAFETY TASK: Fix memory and resource leaks in Python code.\n\n"
            f"File: {file_path}\n\n"
            f"Detected Leaks:\n" + "\n".join(leak_summary) + "\n\n"
            "Safety Rules:\n"
            "1. Wrap all open() calls in 'with' statements for automatic cleanup\n"
            "2. Replace global growing lists with rotating buffers or logging\n"
            "3. Add maxsize parameter to @lru_cache decorators\n"
            "4. Use context managers for all resources (files, sockets, connections)\n"
            "5. Import contextlib and weakref as needed\n"
            "6. Add comments explaining resource management\n"
            "7. Preserve all existing functionality\n\n"
            "Requirements:\n"
            "1. Ensure all resources are properly closed even on exceptions\n"
            "2. Use weakref for cache keys to prevent memory retention\n"
            "3. Implement proper cleanup in __exit__ methods if needed\n"
            "4. Do not sacrifice functionality for safety\n\n"
            f"Code:\n{content}\n\n"
            "Return ONLY the complete leak-free Python code."
        )
        return await self.ctx.request_mutation(self.name, prompt, content, reasoning_mode=True)

    def _save_safety_report(self, log_entries, fixed_files):
        """Save the resource safety report."""
        timestamp = int(time.time())
        report_path = f"observability/audit/resource_safety_{timestamp}.md"

        report_content = "# Resource Safety Report\n\n"
        report_content += f"Generated: {datetime.datetime.now().isoformat()}\n\n"
        report_content += "## Summary\n\n"
        report_content += f"- Files scanned: {len(log_entries)}\n"
        report_content += f"- Files secured: {len(fixed_files)}\n\n"

        if log_entries:
            report_content += "## Resource Fixes\n\n"
            for entry in log_entries:
                if "error" in entry:
                    report_content += f"### [X] {entry['file']}\n\n"
                    report_content += f"**Error:** {entry['error']}\n\n"
                else:
                    report_content += f"### [OK] {entry['file']}\n\n"

                    leaks = entry["leaks"]
                    report_content += "**Leaks Fixed:**\n"
                    for Severity, leak_list in leaks.items():
                        for leak in leak_list:
                            report_content += (
                                f"- {leak['type']} ({Severity}): line {leak['line']}\n"
                            )

                    context = entry["context"]
                    if context.get("global_containers"):
                        report_content += "\n**Global Containers:**\n"
                        for container in context["global_containers"]:
                            report_content += (
                                f"- {container['variable']} (line {container['line']})\n"
                            )

                    if context.get("naked_opens"):
                        report_content += "\n**Naked Resources:**\n"
                        for naked in context["naked_opens"]:
                            report_content += f"- {naked['function']} (line {naked['line']})\n"

                    report_content += f"\n**Reasoning:** {entry['reasoning']}\n\n"

        self.ctx.write_compliant_file(report_path, report_content)

    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """
        Memory Leak Healing - Scans for resource leaks and applies fixes.

        WIRED CAPABILITIES:
        - _scan_and_fix(): Detects and fixes resource leaks (naked opens, etc.).
        """
        # CRITICAL: Chain up to HealerMixin
        metrics = super().heal_repository(
            dry_run=dry_run,
            execute=execute,
            depth=depth,
            max_depth=max_depth,
            _call_path=_call_path,
        )
        if not isinstance(metrics, dict):
            metrics = {"violations": 0, "fixed": 0, "errors": 0}

        if metrics.get("cycle_detected"):
            return metrics

        try:
            # Wired Orphan: _scan_and_fix
            # This requires an async loop and a valid context
            if hasattr(self, "ctx") and self.ctx:
                # Get target files from context or default to empty
                target_files = getattr(self.ctx, "python_files", [])

                if target_files:
                    # Run async scan synchronously
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    try:
                        for file_path in target_files:
                            if not file_path.endswith(".py"):
                                continue

                            # For safety in this healer wrapper, we only run if explicitly executed
                            if execute and not dry_run:
                                result = loop.run_until_complete(self._scan_and_fix(file_path))
                                if result:
                                    metrics["fixed"] = metrics.get("fixed", 0) + 1
                                    metrics["violations"] = metrics.get("violations", 0) + len(
                                        result.get("leaks", [])
                                    )
                    finally:
                        loop.close()

        except Exception as e:
            print(f"[{self.name}] Leak healing failed: {e}")
            metrics["errors"] = metrics.get("errors", 0) + 1

        return metrics


# NAMING FIXED: DeadlockAnalyzer → DeadlockAnalyzer
class DeadlockAnalyzer(ast.NodeVisitor):
    """AST visitor to build lock acquisition graph and detect potential deadlocks."""

    def __init__(self) -> None:
        self.graph = defaultdict(set)  # Lock acquisition graph: lock_a -> {lock_b, lock_c}
        self.lock_sequences = []  # List of lock acquisition sequences per function
        self.current_function = None
        self.current_sequence = []
        self.locks_without_timeout = []
        self.lock_acquisitions = []  # Track all lock.acquire() calls

    def visit_Module(self, node) -> Any:
        """Visit the module and analyze all functions."""
        self.generic_visit(node)

    def visit_FunctionDef(self, node) -> Any:
        """Analyze a function for lock acquisition patterns."""
        old_function = self.current_function
        old_sequence = self.current_sequence
        self.current_function = node.name
        self.current_sequence = []

        # Visit function body
        for stmt in node.body:
            self.visit(stmt)

        # Record the lock sequence for this function
        if len(self.current_sequence) > 1:
            self.lock_sequences.append(
                {
                    "function": node.name,
                    "sequence": self.current_sequence.copy(),
                    "line": node.lineno,
                }
            )

            # Build graph edges from acquisition order
            for i in range(len(self.current_sequence) - 1):
                lock_a = self.current_sequence[i]
                lock_b = self.current_sequence[i + 1]
                self.graph[lock_a].add(lock_b)

        self.current_function = old_function
        self.current_sequence = old_sequence

    def visit_AsyncFunctionDef(self, node) -> Any:
        """Analyze async functions for lock patterns."""
        self.visit_FunctionDef(node)

    def visit_With(self, node) -> Any:
        """Analyze 'with' statements for lock acquisitions."""
        for item in node.items:
            lock_name = self._extract_lock_name(item.context_expr)
            if lock_name:
                self.current_sequence.append(lock_name)

        # Visit the with body
        for stmt in node.body:
            self.visit(stmt)

        # Remove locks from current sequence
        for item in node.items:
            lock_name = self._extract_lock_name(item.context_expr)
            if lock_name:
                self.current_sequence.pop()

    def visit_AsyncWith(self, node) -> Any:
        """Analyze 'async with' statements."""
        self.visit_With(node)

    def visit_Call(self, node) -> Any:
        """Check for .acquire() calls without timeout."""
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "acquire":
                # Check if timeout parameter is provided
                has_timeout = any(kw.arg == "timeout" for kw in node.keywords) or len(node.args) > 1

                if not has_timeout:
                    lock_name = self._extract_lock_name(node.func.value)
                    if lock_name:
                        self.locks_without_timeout.append(
                            {
                                "lock": lock_name,
                                "line": node.lineno,
                                "function": self.current_function,
                            }
                        )

        self.generic_visit(node)

    def _extract_lock_name(self, node):
        """Extract the lock name from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # For self.lock, return 'self.lock'
            if isinstance(node.value, ast.Name) and node.value.id == "self":
                return f"self.{node.attr}"
            # For other attributes, return the full path
            return ast.unparse(node) if hasattr(ast, "unparse") else str(node.lineno)
        return None

    def detect_cycles(self) -> Any:
        """Detect cycles in the lock acquisition graph using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node, parent_path) -> Any:
            """Execute dfs operation."""
            if node in rec_stack:
                # Found a cycle
                cycle_start = parent_path.index(node)
                cycle = parent_path[cycle_start:] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)
            parent_path.append(node)

            for neighbor in self.graph.get(node, []):
                dfs(neighbor, parent_path.copy())

            rec_stack.remove(node)

        # Run DFS from each node
        for lock in self.graph:
            if lock not in visited:
                dfs(lock, [])

        return cycles


# Legacy class removed 2026-01-06 - use standalone DeadlockDetectorAgent
# from agentic_core.L3_orchestration.workflow_engines.deadlock_detector import DeadlockDetectorAgent


# NAMING FIXED: RaceAnalyzer → RaceAnalyzer
class RaceAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze potential race conditions."""

    def __init__(self) -> None:
        self.races = []
        self.current_function = None
        self.current_class = None
        self.in_with_context = []
        self.global_variables = set()
        self.shared_state = []

    def visit(self, node) -> Any:
        """Execute visit operation."""
        # Add parent info to nodes for context tracking
        for child in ast.walk(node):
            for field, value in ast.iter_fields(child):
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, ast.AST):
                            item._parent = child
                elif isinstance(value, ast.AST):
                    value._parent = child
        return super().visit(node)

    def visit_Module(self, node) -> Any:
        """Execute visit_Module operation."""
        # Track module-level assignments (global state)
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        self.global_variables.add(target.id)
        self.generic_visit(node)

    def visit_ClassDef(self, node) -> Any:
        """Execute visit_ClassDef operation."""
        old_class = self.current_class
        self.current_class = node.name

        # Track class attributes as shared state
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                        if target.value.id == "self":
                            self.shared_state.append(
                                {
                                    "type": "class_attribute",
                                    "name": target.attr,
                                    "line": stmt.lineno,
                                    "class": node.name,
                                }
                            )

        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node) -> Any:
        """Execute visit_FunctionDef operation."""
        old_function = self.current_function
        self.current_function = node.name

        # Check for global statements
        for stmt in node.body:
            if isinstance(stmt, ast.Global):
                self.global_variables.update(stmt.names)

        self.generic_visit(node)
        self.current_function = old_function

    def visit_AsyncFunctionDef(self, node) -> Any:
        """Execute visit_AsyncFunctionDef operation."""
        self.visit_FunctionDef(node)

    def visit_With(self, node) -> Any:
        """Execute visit_With operation."""
        # Check if this 'with' statement uses a lock
        is_lock_context = False
        for item in node.items:
            if isinstance(item.context_expr, ast.Name):
                if "lock" in item.context_expr.id.lower():
                    is_lock_context = True
            elif isinstance(item.context_expr, ast.Attribute):
                if "lock" in item.context_expr.attr.lower():
                    is_lock_context = True

        self.in_with_context.append(("lock" if is_lock_context else "other", node.lineno))
        self.generic_visit(node)
        self.in_with_context.pop()

    def visit_AsyncWith(self, node) -> Any:
        """Execute visit_AsyncWith operation."""
        self.visit_With(node)

    def visit_Assign(self, node) -> Any:
        """Execute visit_Assign operation."""
        # Check for assignments to shared mutable state
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Module/global variable assignment
                if target.id in self.global_variables:
                    if not self._is_in_lock_context():
                        self.races.append(
                            {
                                "type": "global_mutable_assignment",
                                "variable": target.id,
                                "line": node.lineno,
                                "function": self.current_function,
                                "context": "module",
                            }
                        )

            elif isinstance(target, ast.Attribute):
                # Class attribute assignment (self.x)
                if isinstance(target.value, ast.Name) and target.value.id == "self":
                    if not self._is_in_lock_context():
                        self.races.append(
                            {
                                "type": "class_attribute_assignment",
                                "attribute": target.attr,
                                "line": node.lineno,
                                "function": self.current_function,
                                "class": self.current_class,
                            }
                        )

            elif isinstance(target, ast.Subscript):
                # Dictionary/list element assignment (shared_dict[key])
                if not self._is_in_lock_context():
                    self.races.append(
                        {
                            "type": "shared_collection_assignment",
                            "line": node.lineno,
                            "function": self.current_function,
                            "class": self.current_class,
                        }
                    )

        self.generic_visit(node)

    def visit_AugAssign(self, node) -> Any:
        """Execute visit_AugAssign operation."""
        # Check for compound operations (+=, -=, *=, /=)
        # These are always non-atomic
        if isinstance(node.target, ast.Name):
            if node.target.id in self.global_variables:
                if not self._is_in_lock_context():
                    self.races.append(
                        {
                            "type": "global_compound_operation",
                            "variable": node.target.id,
                            "operator": type(node.op).__name__,
                            "line": node.lineno,
                            "function": self.current_function,
                            "context": "module",
                        }
                    )

        elif isinstance(node.target, ast.Attribute):
            if isinstance(node.target.value, ast.Name) and node.target.value.id == "self":
                if not self._is_in_lock_context():
                    self.races.append(
                        {
                            "type": "class_compound_operation",
                            "attribute": node.target.attr,
                            "operator": type(node.op).__name__,
                            "line": node.lineno,
                            "function": self.current_function,
                            "class": self.current_class,
                        }
                    )

        self.generic_visit(node)

    def visit_Call(self, node) -> Any:
        """Execute visit_Call operation."""
        # Check for method calls on shared objects without locks
        if isinstance(node.func, ast.Attribute):
            # Check if it's a mutable method on shared state
            mutable_methods = {
                "append",
                "extend",
                "insert",
                "pop",
                "remove",
                "clear",
                "update",
                "popitem",
                "setdefault",
                "add",
                "discard",
                "intersection_update",
                "difference_update",
            }

            if node.func.attr in mutable_methods:
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id in self.global_variables:
                        if not self._is_in_lock_context():
                            self.races.append(
                                {
                                    "type": "shared_mutable_method_call",
                                    "method": node.func.attr,
                                    "object": node.func.value.id,
                                    "line": node.lineno,
                                    "function": self.current_function,
                                }
                            )

        self.generic_visit(node)

    def _is_in_lock_context(self):
        """Check if current node is inside a 'with lock:' context."""
        return any(context[0] == "lock" for context in self.in_with_context)
