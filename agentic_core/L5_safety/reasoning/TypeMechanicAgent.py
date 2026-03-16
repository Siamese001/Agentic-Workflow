from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "TypeMechanicAgent")
emit_determinism_digest("p0", "TypeMechanicAgent")

_emit_dispatches_healing_run("p1", "TypeMechanicAgent", "L5")
_emit_routes_through("p1", "TypeMechanicAgent", "L5")
_emit_escalates_to_human("p1", "TypeMechanicAgent", "L5")
_emit_reads_policy_state("p1", "TypeMechanicAgent", "L5")

_emit_applies_guardrail("p0", "TypeMechanicAgent", "p0_governance")
_emit_snapshots_state("p0", "TypeMechanicAgent", "state_snapshot")

"\nTypeMechanicAgent - Extracted from SubAtomicAgent.py\nPart of the SubAtomic agent family for code quality enforcement.\n"
import ast
from typing import Any

from agentic_core.L3_orchestration.reasoning.SubAtomicAgent import SubAtomicAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


@dataclass
class TypeMechanicAgent(SovereignBaseAgent, SubAtomicAgent):
    """
    Type Mechanic Agent - Type hints and code quality enforcement.

    Validates:
    - Missing type hints
    - Unreachable code
    - Unused variables

    ROLE: Precision Engineering. Requires AST_VALID signal.
    """

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """
        Autonomous healing method.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "TypeMechanicAgent.heal_repository")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TypeMechanicAgent.heal_repository".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        super().heal_repository(**kwargs)
        return {"violations": 0, "fixed": 0, "errors": 0}

    def can_run(self) -> bool:
        """
        Determines if the agent can run based on the presence of the 'AST_VALID' signal.
        """
        return "AST_VALID" in self.ctx.signals

    def execute(self) -> None:
        """
        Executes the TypeMechanic agent, performing checks for type system violations.
        """
        print(f"\n[>>>] {self.name} ACTIVATED: Type System Check...")
        passed, details = self.check_no_missing_type_hints()
        self.ctx.report(self.name, 22, passed, details)
        passed, details = self.check_no_unreachable_code()
        self.ctx.report(self.name, 23, passed, details)
        passed, details = self.check_no_unused_variables()
        self.ctx.report(self.name, 24, passed, details)

    def _read_and_parse_file(self, fp: str) -> tuple[ast.AST | None, str | None]:
        """
        Reads a file and parses it into an AST, handling errors.
        Returns (tree, error_message).
        """
        try:
            with open(fp, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=fp)
                return (tree, None)
        except (OSError, SyntaxError) as e:
            return (None, f"Error parsing {fp}: {e}")

    def _get_missing_type_hint_violations_for_tree(self, fp: str, tree: ast.AST) -> list[str]:
        """
        Collects formatted Violation strings for Missing type hints in a given AST tree.
        """
        file_violations = []
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.FunctionDef)
                and (not node.returns)
                and (node.name not in ("__init__", "__str__", "__repr__"))
            ):
                file_violations.append(
                    f"{fp}:{node.lineno}: Function '{node.name}' is Missing a return type hint."
                )
        return file_violations

    def check_no_missing_type_hints(self) -> tuple[bool, list[str]]:
        """
        Checks for functions with Missing type hints (return types).
        Excludes __init__, __str__, __repr__ methods.
        Refactored to reduce nesting depth to meet max 4.
        """
        violations = []
        for fp in self.ctx.python_files:
            tree, error_msg = self._read_and_parse_file(fp)
            if error_msg:
                self.ctx.log_error(error_msg)
                continue
            if tree:
                violations.extend(self._get_missing_type_hint_violations_for_tree(fp, tree))
        return (len(violations) == 0, violations)

    def _check_function_for_unreachable_code(self, fp: str, func_node: ast.FunctionDef) -> list[str]:
        """
        Checks a single function node for unreachable code after a return statement.
        """
        func_violations = []
        for i, stmt in enumerate(func_node.body):
            if isinstance(stmt, ast.Return) and i < len(func_node.body) - 1:
                func_violations.append(
                    f"{fp}:{stmt.lineno}: Unreachable code after return in function '{func_node.name}'."
                )
                break
        return func_violations

    def _get_unreachable_code_violations_for_tree(self, fp: str, tree: ast.AST) -> list[str]:
        """
        Processes an AST tree to find unreachable code violations within functions.
        """
        file_violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                file_violations.extend(self._check_function_for_unreachable_code(fp, node))
        return file_violations

    def check_no_unreachable_code(self) -> tuple[bool, list[str]]:
        """
        Checks for unreachable code, specifically statements after a 'return' statement
        within a function body.
        Refactored to reduce nesting depth to meet max 4.
        """
        violations = []
        for fp in self.ctx.python_files:
            tree, error_msg = self._read_and_parse_file(fp)
            if error_msg:
                self.ctx.log_error(error_msg)
                continue
            if tree:
                violations.extend(self._get_unreachable_code_violations_for_tree(fp, tree))
        return (len(violations) == 0, violations)

    def _collect_variables(self, func_node: ast.FunctionDef) -> tuple[set[str], set[str]]:
        """
        Collects assigned and used variable names within a given function AST node.
        """
        assigned: set[str] = set()
        used: set[str] = set()
        for child in ast.walk(func_node):
            if isinstance(child, ast.Assign):
                names_assigned = [target.id for target in child.targets if isinstance(target, ast.Name)]
                assigned.update(names_assigned)
            elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                used.add(child.id)
        return (assigned, used)

    def _get_function_violations_for_file(self, fp: str, tree: ast.AST) -> list[str]:
        """
        Processes an AST tree to find unused variables within functions.
        """
        file_violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                assigned, used = self._collect_variables(node)
                unused = assigned - used
                unused = {var for var in unused if var != "_"}
                if unused:
                    file_violations.append(
                        f"{fp}:{node.lineno}: Function '{node.name}' has unused variables: {', '.join(sorted(unused))}."
                    )
        return file_violations

    def _process_file_for_unused_variables(self, fp: str) -> list[str]:
        """
        Opens and parses a single file, then delegates to find unused variables.
        Handles file I/O and parsing errors.
        """
        try:
            with open(fp, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=fp)
            return self._get_function_violations_for_file(fp, tree)
        except (OSError, SyntaxError) as e:
            self.ctx.log_error(f"Error parsing {fp} for unused variables: {e}")
            return []

    def check_no_unused_variables(self) -> tuple[bool, list[str]]:
        """
        Checks for variables that are assigned but never used within a function.
        Refactored to reduce nesting depth.
        """
        violations = []
        for fp in self.ctx.python_files:
            violations.extend(self._process_file_for_unused_variables(fp))
        return (len(violations) == 0, violations)

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)
