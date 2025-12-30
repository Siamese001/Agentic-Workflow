"""
[L5 SAFETY] Layer Capability Agent
Enforces the Sovereign Principle: "Each capability lives in exactly one L-layer."
Uses AST analysis to detect behavioral drift and gravity violations (Key 20).
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Tuple, Any, Set
from agentic_core.L1_cognition.thought_engine.canon_base_agent import sub_atomic_agent as BaseAgent

class LayerCapabilityAgent(BaseAgent):
    """
    L5 Safety Agent: Validates ≤2 layer capabilities per agent class.
    Ensures primary residency in exactly one dominant L-layer (L1–L5).
    """

    # AST-based layer responsibility signatures (v2 — structural analysis)
    # These patterns match function names and call signatures to identify behavioral drift.
    LAYER_METHOD_PATTERNS = {
        "L1": [
            "plan", "reason", "think_step_by_step", "critique", "reflect",
            "decompose", "generate_plan", "hypothesize", "self_critique"
        ],
        "L2": [
            "execute", "run_tool", "call_tool", "retrieve", "fetch",
            "get_evidence", "perform_action", "tool_use"
        ],
        "L3": [
            "orchestrate", "route", "dispatch", "schedule", "coordinate",
            "next_node", "handle_retry", "manage_flow"
        ],
        "L4": [
            "apply_patch", "merge_patch", "update_state", "persist",
            "load_memory", "save_episode"
        ],
        "L5": [
            "check_safety", "apply_guardrail", "veto", "filter_output",
            "constitutional_review", "policy_enforce", "override"
        ]
    }

    # Forbidden cross-layer call targets (Enforcing Key 18 - Gravity)
    # L1 and L2 workers must not drive higher-level management (L3).
    FORBIDDEN_CALLS = {
        "L1": {"L2", "L3", "L4", "L5"},  # L1 only thinks — no execution/state/safety calls
        "L2": {"L1", "L3", "L5"},        # L2 executes — no reasoning/orchestration/safety
        "L3": set(),                      # L3 orchestrates — coordination calls permitted
    }

    MAX_CAPABILITIES = 2

    def __init__(self, project_root: Path = None):
        super().__init__(name="LayerCapabilityAgent", layer="L5")
        self.project_root = project_root

    def analyze_file_ast(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse AST and collect layer signals from method definitions and call sites.
        [SOVEREIGN HARDENING] Distinguishes logic implementation from logic usage.
        """
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except SyntaxError as e:
            return {"error": f"SyntaxError: {e}"}
        except Exception as e:
            return {"error": f"ReadError: {e}"}

        signals = {
            "defined_methods": {layer: set() for layer in self.LAYER_METHOD_PATTERNS},
            "called_methods": {layer: set() for layer in self.LAYER_METHOD_PATTERNS}
        }

        class AgentVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node: ast.FunctionDef):
                method_name = node.name.lower()
                for layer, patterns in LayerCapabilityAgent.LAYER_METHOD_PATTERNS.items():
                    if any(p.lower() in method_name for p in patterns):
                        signals["defined_methods"][layer].add(method_name)
                self.generic_visit(node)

            def visit_Call(self, node: ast.Call):
                # Detect target function name from direct call or attribute access
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id.lower()
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr.lower()

                for layer, patterns in LayerCapabilityAgent.LAYER_METHOD_PATTERNS.items():
                    if any(p.lower() in func_name for p in patterns):
                        signals["called_methods"][layer].add(func_name)
                self.generic_visit(node)

        visitor = AgentVisitor()
        visitor.visit(tree)
        return signals

    def determine_primary_layer(self, defined_methods: Dict[str, set]) -> Tuple[str, int]:
        """
        Identify the dominant layer based on the highest count of defined responsibility methods.
        """
        counts = {layer: len(methods) for layer, methods in defined_methods.items()}
        if not any(counts.values()):
            return "UNKNOWN", 0
        primary = max(counts, key=counts.get)
        return primary, counts[primary]

    def execute(self) -> List[dict]:
        """Scan all *Agent*.py files and report violations"""
        violations = []
        agent_files = list(self.project_root.rglob("*Agent*.py"))

        for file_path in agent_files:
            rel_path = file_path.relative_to(self.project_root)
            analysis = self.analyze_file_ast(file_path)
            
            if "error" in analysis:
                violations.append({
                    "file": str(rel_path),
                    "issue": "PARSE_ERROR",
                    "detail": analysis["error"]
                })
                continue

            defined = analysis["defined_methods"]
            called = analysis["called_methods"]
            active_defined_layers = [l for l, methods in defined.items() if methods]
            primary_layer, primary_count = self.determine_primary_layer(defined)

            # Violation 1: Exceeding capability limit (Key 13 - Span of Two)
            if len(active_defined_layers) > self.MAX_CAPABILITIES:
                violations.append({
                    "file": str(rel_path),
                    "issue": "TOO_MANY_CAPABILITIES_DEFINED",
                    "detected_layers": active_defined_layers,
                    "detail": f"Defines methods from {len(active_defined_layers)} layers (max {self.MAX_CAPABILITIES})"
                })

            # Violation 2: Weak Primary Residency (Unclear domain dominance)
            if len(active_defined_layers) > 1:
                secondary_max = max(len(defined[l]) for l in active_defined_layers if l != primary_layer)
                if primary_count <= secondary_max:
                    violations.append({
                        "file": str(rel_path),
                        "issue": "WEAK_PRIMARY_RESIDENCY",
                        "primary": primary_layer,
                        "detail": f"Primary {primary_layer} ({primary_count}) not clearly dominant over secondary ({secondary_max})"
                    })

            # Violation 3: Forbidden Cross-Layer Calls (Key 18 - Gravity Enforcement)
            if primary_layer != "UNKNOWN" and primary_layer in self.FORBIDDEN_CALLS:
                forbidden = self.FORBIDDEN_CALLS[primary_layer]
                violated_calls = []
                for forbidden_layer in forbidden:
                    if called.get(forbidden_layer):
                        violated_calls.extend(list(called[forbidden_layer]))
                
                if violated_calls:
                    violations.append({
                        "file": str(rel_path),
                        "issue": "FORBIDDEN_CROSS_LAYER_CALL",
                        "primary": primary_layer,
                        "detail": f"Layer {primary_layer} agent violates gravity by calling forbidden methods: {violated_calls}"
                    })

        return violations
