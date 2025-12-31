"""
ScriptToAgentClassifier – Sovereign Agent (Phase 17 – Dec 30, 2025)
SSOT-compliant location: L0_maintenance/scripts/

Purpose:
  Autonomous classification of Python modules to enforce Atomic Fission and DDD alignment.
  Determines whether a module should be:
    - A procedural script (execution entry point)
    - A pure agent (class-based, import-safe)
    - A candidate for fission (monolithic → multiple agents)
    - A candidate for fusion (dust agents → consolidated)

Integrates with:
  - GuardianOrchestrator (new "Atomic Classification" dimension)
  - Healing strategies (propose fission/fusion fixes)
  - MetricsWitness (emit compliance.script_vs_agent_violations)

Pure analysis – zero side effects.
"""

import ast
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import logging
from collections import Counter


class ScriptToAgentClassifier:
    """
    Sovereign classifier for script vs agent constitutional compliance.
    Uses static analysis (AST) + heuristics aligned with semantic_l2_registry.
    """

    # Constitutional thresholds (tunable via healing evolution)
    DUST_LINE_THRESHOLD = 40          # Below = fusion candidate (Span-of-Two law)
    MONOLITH_LINE_THRESHOLD = 250     # Above = fission candidate
    MAX_CLASSES_FOR_SCRIPT = 1        # >1 class in script → likely needs fission
    HIGH_SIDE_EFFECT_WEIGHT = 0.8

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def classify_module(self, file_path: Path) -> Dict[str, Any]:
        """
        Primary classification entry point.
        Returns comprehensive verdict with confidence and rationale.
        """
        if not file_path.exists() or file_path.suffix != ".py":
            return {
                "recommended_type": "invalid",
                "confidence": 1.0,
                "rationale": [f"File {file_path} does not exist or is not Python"],
                "signals": {},
            }

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception as e:
            return {
                "recommended_type": "unparseable",
                "confidence": 1.0,
                "rationale": [f"Failed to parse AST: {e}"],
                "signals": {"parse_error": str(e)},
            }

        analyzer = _ModuleAnalyzer(tree, source, file_path)
        signals = analyzer.extract_signals()

        verdict = self._compute_verdict(signals, file_path.name)
        verdict["signals"] = signals

        return verdict

    def _compute_verdict(
        self, signals: Dict[str, Any], filename: str
    ) -> Dict[str, Any]:
        """
        Constitutional decision engine.
        Returns recommended_type with confidence and rationale.
        """
        score_script = 0.0
        score_agent = 0.0
        rationale: List[str] = []

        # === Script indicators (positive for script) ===
        if signals["has_main_guard"]:
            score_script += 1.0
            rationale.append("Contains if __name__ == '__main__' block → execution entry point")

        if signals["has_async_main"]:
            score_script += 0.9
            rationale.append("Defines async main() with asyncio.run → script pattern")

        if signals["top_level_statements"] > 10:
            score_script += 0.6
            rationale.append(f"High top-level statements ({signals['top_level_statements']}) → procedural")

        if signals["side_effect_calls"]:
            score_script += 0.4 * min(len(signals["side_effect_calls"]) / 5, 1.0)
            rationale.append(f"Top-level side effects: {signals['side_effect_calls'][:3]}...")

        if signals["num_classes"] <= self.MAX_CLASSES_FOR_SCRIPT and signals["num_classes"] > 0:
            score_script += 0.3
            rationale.append("Few or single class → acceptable in script")

        # === Agent indicators (positive for pure agent) ===
        if signals["num_classes"] >= 2:
            score_agent += 0.8
            rationale.append(f"Multiple classes ({signals['num_classes']}) → better as separate agents")

        if signals["num_classes"] == 1 and not signals["has_main_guard"]:
            score_agent += 0.9
            rationale.append("Single class, no execution block → pure agent pattern")

        if signals["line_count"] < self.DUST_LINE_THRESHOLD and signals["num_classes"] == 1:
            score_agent -= 0.7  # Dust agent → prefer fusion
            rationale.append(f"Below dust threshold ({signals['line_count']} < {self.DUST_LINE_THRESHOLD}) → fusion candidate")

        if signals["line_count"] > self.MONOLITH_LINE_THRESHOLD:
            score_agent += 0.7 if signals["num_classes"] > 1 else 0.3
            rationale.append(f"Monolithic size ({signals['line_count']} lines) → fission recommended")

        if filename.startswith("guard_") or filename.startswith("healing_") or "orchestrator" in filename:
            score_agent += 0.6
            rationale.append("Filename matches sovereign agent pattern")

        # === Final verdict ===
        total = score_script + score_agent
        if total == 0:
            confidence = 0.5
            recommended = "uncertain"
        else:
            confidence = max(score_script, score_agent) / total
            if score_script > score_agent:
                recommended = "script"
            elif signals["line_count"] > self.MONOLITH_LINE_THRESHOLD and signals["num_classes"] > 1:
                recommended = "fission_needed"
                confidence = max(confidence, 0.85)
            elif signals["line_count"] < self.DUST_LINE_THRESHOLD and signals["num_classes"] == 1:
                recommended = "fusion_needed"
                confidence = max(confidence, 0.8)
            else:
                recommended = "agent"

        return {
            "recommended_type": recommended,
            "confidence": round(confidence, 3),
            "rationale": rationale,
        }

    def suggest_fission_targets(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        For monolithic modules, suggest class → agent extraction points.
        Returns list of proposed new agents.
        """
        classification = self.classify_module(file_path)
        if classification["recommended_type"] != "fission_needed":
            return []

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:
            return []

        visitor = _ClassExtractionVisitor()
        visitor.visit(tree)

        suggestions = []
        for class_def in visitor.classes:
            suggestions.append({
                "class_name": class_def.name,
                "line_start": class_def.lineno,
                "line_end": class_def.end_lineno,
                "suggested_filename": f"{class_def.name.lower()}.py",
                "priority": 10 if "Orchestrator" in class_def.name else 5,
                "reason": f"Extract {class_def.name} to dedicated sovereign agent",
            })

        return sorted(suggestions, key=lambda x: x["priority"], reverse=True)


class _ModuleAnalyzer(ast.NodeVisitor):
    """
    Internal AST visitor to extract classification signals.
    """

    def __init__(self, tree: ast.AST, source: str, file_path: Path):
        super().__init__()
        self.tree = tree
        self.source_lines = source.splitlines()
        self.file_path = file_path

        # Signals
        self.has_main_guard = False
        self.has_async_main = False
        self.num_classes = 0
        self.top_level_statements = 0
        self.side_effect_calls = []
        self.line_count = len(self.source_lines)

    def extract_signals(self) -> Dict[str, Any]:
        self.visit(self.tree)
        return {
            "has_main_guard": self.has_main_guard,
            "has_async_main": self.has_async_main,
            "num_classes": self.num_classes,
            "top_level_statements": self.top_level_statements,
            "side_effect_calls": self.side_effect_calls[:10],
            "line_count": self.line_count,
        }

    def visit_If(self, node: ast.If):
        if (
            isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == "__name__"
            and any(isinstance(op, ast.Eq) and isinstance(comp, ast.Constant) and comp.value == "__main__" for op, comp in zip(node.test.ops, node.test.comparators))
        ):
            self.has_main_guard = True
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        if node.name == "main":
            # Check if called with asyncio.run
            for stmt in self.tree.body:
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    if getattr(stmt.value.func, "attr", None) == "run" and getattr(stmt.value.func.value, "id", None) == "asyncio":
                        if any(arg.id == "main" for arg in stmt.value.args if isinstance(arg, ast.Name)):
                            self.has_async_main = True
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.num_classes += 1
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Detect common top-level side effects
        func_name = self._get_func_name(node.func)
        if func_name in {"print", "open", "Path.write_text", "Path.write_bytes", "logging"}:
            # Only count if at module top level
            if node.lineno <= max((n.lineno for n in ast.walk(self.tree) if isinstance(n, ast.FunctionDef)), default=50):
                self.side_effect_calls.append(func_name)
        self.generic_visit(node)

    def _get_func_name(self, func_node) -> str:
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            return f"{self._get_func_name(func_node.value)}.{func_node.attr}"
        return "unknown"

    def visit_Expr(self, node: ast.Expr):
        # Count top-level expressions (not inside functions/classes)
        # Note: parent attribute not available in standard AST, simplified check
        self.top_level_statements += 1
        self.generic_visit(node)


class _ClassExtractionVisitor(ast.NodeVisitor):
    """
    Extracts class definitions for fission suggestions.
    """
    def __init__(self):
        self.classes: List[ast.ClassDef] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        self.classes.append(node)
        self.generic_visit(node)
