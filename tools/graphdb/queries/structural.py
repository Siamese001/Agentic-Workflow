"""Structural Conformance Queries - Query pack for architectural rule validation.

This module provides queries to check structural conformance against
architectural policies and governance rules.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

import networkx as nx
from tqdm import tqdm


class StructuralQueries:
    """Structural conformance query pack for ADG graph analysis."""

    def __init__(self, graph: nx.Graph):
        """Initialize with a NetworkX graph.

        Args:
            graph: NetworkX graph with ADG projection
        """
        self.graph = graph

    def gravity_import_violations(self) -> List[Dict[str, Any]]:
        """Find imports that violate layer gravity rules.

        Returns:
            List of violations with details
        """
        violations = []

        # Define layer hierarchy (lower numbers = deeper layers)
        layer_hierarchy = {
            "L0": 0,
            "L1": 1,
            "L2": 2,
            "L3": 3,
            "L4": 4,
            "L5": 5,
            "L6": 6,
        }

        for u, v, attrs in tqdm(self.graph.edges(data=True), desc="import edges", unit="edge", leave=False):
            if attrs.get("graph_type") == "IMPORTS":
                u_attrs = self.graph.nodes[u]
                v_attrs = self.graph.nodes[v]

                u_layer = u_attrs.get("properties", {}).get("layer")
                v_layer = v_attrs.get("properties", {}).get("layer")

                if u_layer and v_layer:
                    u_level = layer_hierarchy.get(u_layer)
                    v_level = layer_hierarchy.get(v_layer)

                    if u_level is not None and v_level is not None:
                        # Import should go from higher to lower layer (or same)
                        if v_level > u_level:
                            violations.append(
                                {
                                    "type": "gravity_import_violation",
                                    "from_node": u,
                                    "to_node": v,
                                    "from_layer": u_layer,
                                    "to_layer": v_layer,
                                    "from_level": u_level,
                                    "to_level": v_level,
                                    "violation": f"Import from {u_layer} to {v_layer} violates gravity",
                                    "line_number": attrs.get("properties", {}).get("line_number"),
                                }
                            )

        return violations

    def illegal_layer_reach(self) -> List[Dict[str, Any]]:
        """Find cross-layer dependencies that violate architecture.

        Returns:
            List of illegal cross-layer dependencies
        """
        violations = []

        # Define forbidden layer transitions
        forbidden_transitions = {
            # L6 (Infrastructure) should not depend on L2 (Execution)
            ("L6", "L2"): "Infrastructure should not depend on execution logic",
            # L5 (Safety) should not depend on L2 (Execution) directly
            ("L5", "L2"): "Safety should not directly depend on execution logic",
            # L4 (State) should not depend on L0 (Routing)
            ("L4", "L0"): "State should not depend on routing",
        }

        for u, v, attrs in tqdm(self.graph.edges(data=True), desc="layer edges", unit="edge", leave=False):
            u_attrs = self.graph.nodes[u]
            v_attrs = self.graph.nodes[v]

            u_layer = u_attrs.get("properties", {}).get("layer")
            v_layer = v_attrs.get("properties", {}).get("layer")

            if u_layer and v_layer:
                transition = (u_layer, v_layer)
                if transition in forbidden_transitions:
                    violations.append(
                        {
                            "type": "illegal_layer_reach",
                            "from_node": u,
                            "to_node": v,
                            "from_layer": u_layer,
                            "to_layer": v_layer,
                            "edge_type": attrs.get("graph_type"),
                            "reason": forbidden_transitions[transition],
                            "line_number": attrs.get("properties", {}).get("line_number"),
                        }
                    )

        return violations

    def l2_lifecycle_conformance(self) -> Dict[str, Any]:
        """Check L2 execution phases against canonical sub-phases.

        Returns:
            Dictionary with conformance results
        """
        # Get all L2 modules
        l2_modules = [
            node
            for node, attrs in self.graph.nodes(data=True)
            if attrs.get("properties", {}).get("layer") == "L2"
        ]

        # Define expected L2 sub-phases
        expected_subphases = {
            "execution": ["execute", "run", "process"],
            "orchestration": ["orchestrate", "coordinate", "manage"],
            "validation": ["validate", "verify", "check"],
            "error_handling": ["handle", "catch", "recover"],
        }

        results = {
            "total_l2_modules": len(l2_modules),
            "conformant_modules": [],
            "non_conformant_modules": [],
            "missing_subphases": {},
            "analysis": {},
        }

        for module in tqdm(l2_modules, desc="L2 modules", unit="module", leave=False):
            module_attrs = self.graph.nodes[module]
            module_name = module_attrs.get("name", "")

            # Check if module follows expected naming patterns
            conformant = False
            matched_phase = None

            for phase, patterns in expected_subphases.items():
                if any(pattern in module_name.lower() for pattern in patterns):
                    conformant = True
                    matched_phase = phase
                    break

            if conformant:
                results["conformant_modules"].append(
                    {
                        "module": module,
                        "name": module_name,
                        "phase": matched_phase,
                    }
                )
            else:
                results["non_conformant_modules"].append(
                    {
                        "module": module,
                        "name": module_name,
                        "issue": "Does not match expected L2 sub-phase patterns",
                    }
                )

        # Calculate conformance rate
        if results["total_l2_modules"] > 0:
            conformance_rate = len(results["conformant_modules"]) / results["total_l2_modules"]
            results["conformance_rate"] = conformance_rate
        else:
            results["conformance_rate"] = 0.0

        return results

    def uwg_durable_write_conformance(self) -> List[Dict[str, Any]]:
        """Verify all durable writes go through UWG.

        Returns:
            List of non-conformant writes
        """
        violations = []

        # Find UWG gateways
        uwg_gateways = [
            node
            for node, attrs in self.graph.nodes(data=True)
            if attrs.get("graph_type") == "Gateway" and "uwg" in attrs.get("name", "").lower()
        ]

        # Find all write operations
        write_edges = [
            (u, v, attrs)
            for u, v, attrs in self.graph.edges(data=True)
            if attrs.get("graph_type") in ["WRITES_TO", "WRITES_THROUGH"]
        ]

        for u, v, attrs in tqdm(write_edges, desc="write edges", unit="edge", leave=False):
            # Check if write goes through UWG
            goes_through_uwg = False

            # Check if edge is WRITES_THROUGH (implies gateway usage)
            if attrs.get("graph_type") == "WRITES_THROUGH":
                goes_through_uwg = True
            else:
                # Check if target is a UWG gateway
                v_attrs = self.graph.nodes[v]
                if v_attrs.get("graph_type") == "Gateway" and "uwg" in v_attrs.get("name", "").lower():
                    goes_through_uwg = True

            if not goes_through_uwg:
                violations.append(
                    {
                        "type": "uwg_bypass_violation",
                        "from_node": u,
                        "to_node": v,
                        "edge_type": attrs.get("graph_type"),
                        "issue": "Write does not go through UWG",
                        "line_number": attrs.get("properties", {}).get("line_number"),
                    }
                )

        return violations

    def capability_tool_provider_chokepoint_conformance(self) -> Dict[str, Any]:
        """Check capability/tool/provider choke-point conformance.

        Returns:
            Dictionary with choke-point analysis
        """
        results = {
            "capabilities": {"total": 0, "chokepointed": 0, "violations": []},
            "tools": {"total": 0, "chokepointed": 0, "violations": []},
            "providers": {"total": 0, "chokepointed": 0, "violations": []},
        }

        # Analyze capabilities
        capabilities = [
            node
            for node, attrs in self.graph.nodes(data=True)
            if attrs.get("graph_type") == "CapabilityToken"
        ]

        results["capabilities"]["total"] = len(capabilities)

        for capability in tqdm(capabilities, desc="capabilities", unit="cap", leave=False):
            # Check if capability is properly gated
            incoming_edges = list(self.graph.in_edges(capability, data=True))
            has_gate = any(
                attrs.get("graph_type") in ["GATED_BY_CONFIDENCE", "APPLIES_GUARDRAIL"]
                for _, _, attrs in incoming_edges
            )

            if has_gate:
                results["capabilities"]["chokepointed"] += 1
            else:
                results["capabilities"]["violations"].append(
                    {
                        "capability": capability,
                        "issue": "Capability not properly gated",
                    }
                )

        # Similar analysis for tools and providers
        tools = [node for node, attrs in self.graph.nodes(data=True) if attrs.get("graph_type") == "Tool"]

        results["tools"]["total"] = len(tools)

        for tool in tqdm(tools, desc="tools", unit="tool", leave=False):
            incoming_edges = list(self.graph.in_edges(tool, data=True))
            has_gate = any(
                attrs.get("graph_type") in ["GATED_BY_CONFIDENCE", "APPLIES_GUARDRAIL"]
                for _, _, attrs in incoming_edges
            )

            if has_gate:
                results["tools"]["chokepointed"] += 1
            else:
                results["tools"]["violations"].append(
                    {
                        "tool": tool,
                        "issue": "Tool not properly gated",
                    }
                )

        providers = [
            node for node, attrs in self.graph.nodes(data=True) if attrs.get("graph_type") == "Provider"
        ]

        results["providers"]["total"] = len(providers)

        for provider in tqdm(providers, desc="providers", unit="provider", leave=False):
            incoming_edges = list(self.graph.in_edges(provider, data=True))
            has_gate = any(
                attrs.get("graph_type") in ["GATED_BY_CONFIDENCE", "APPLIES_GUARDRAIL"]
                for _, _, attrs in incoming_edges
            )

            if has_gate:
                results["providers"]["chokepointed"] += 1
            else:
                results["providers"]["violations"].append(
                    {
                        "provider": provider,
                        "issue": "Provider not properly gated",
                    }
                )

        return results

    def agentic_spine_completeness(self) -> Dict[str, Any]:
        """Check agentic spine completeness.

        Returns:
            Dictionary with spine analysis
        """
        # Define expected spine components
        expected_spine = {
            "routing": ["L0"],
            "reasoning": ["L1"],
            "execution": ["L2"],
            "orchestration": ["L3"],
            "state": ["L4"],
            "safety": ["L5"],
            "infrastructure": ["L6"],
        }

        results = {
            "spine_complete": True,
            "missing_components": [],
            "layer_analysis": {},
        }

        for component, expected_layers in tqdm(
            expected_spine.items(), desc="spine check", unit="component", leave=False
        ):
            found_nodes = []

            for layer in expected_layers:
                layer_nodes = [
                    node
                    for node, attrs in self.graph.nodes(data=True)
                    if attrs.get("properties", {}).get("layer") == layer
                ]
                found_nodes.extend(layer_nodes)

            if not found_nodes:
                results["spine_complete"] = False
                results["missing_components"].append(component)

            results["layer_analysis"][component] = {
                "expected_layers": expected_layers,
                "found_nodes": len(found_nodes),
                "complete": len(found_nodes) > 0,
            }

        return results

    def l0_l1_l6_role_purity(self) -> Dict[str, Any]:
        """Check L0/L1/L6 role purity.

        Returns:
            Dictionary with role purity analysis
        """
        purity_violations = {
            "L0": [],
            "L1": [],
            "L6": [],
        }

        # Define expected roles for each layer
        expected_roles = {
            "L0": ["routing", "dispatch", "coordinate", "orchestrate"],
            "L1": ["reasoning", "planning", "analysis", "decision"],
            "L6": ["infrastructure", "storage", "network", "system"],
        }

        for layer in tqdm(["L0", "L1", "L6"], desc="grounding layers", unit="layer", leave=False):
            layer_nodes = [
                node
                for node, attrs in self.graph.nodes(data=True)
                if attrs.get("properties", {}).get("layer") == layer
            ]

            for node in tqdm(layer_nodes, desc="  nodes", unit="node", leave=False):
                node_attrs = self.graph.nodes[node]
                node_name = node_attrs.get("name", "").lower()

                # Check if node has unexpected role indicators
                expected_keywords = expected_roles[layer]
                has_expected_role = any(keyword in node_name for keyword in expected_keywords)

                # Check for role violations (keywords from other layers)
                violation_keywords = []
                for other_layer, other_keywords in expected_roles.items():
                    if other_layer != layer:
                        for keyword in other_keywords:
                            if keyword in node_name:
                                violation_keywords.append(f"{other_layer}:{keyword}")

                if violation_keywords:
                    purity_violations[layer].append(
                        {
                            "node": node,
                            "name": node_attrs.get("name"),
                            "violations": violation_keywords,
                            "issue": f"Node contains {other_layer} role indicators",
                        }
                    )

        return {
            "purity_violations": purity_violations,
            "total_violations": sum(len(violations) for violations in purity_violations.values()),
            "is_pure": all(len(violations) == 0 for violations in purity_violations.values()),
        }

    def grounding_contract_separation(self) -> List[Dict[str, Any]]:
        """Check grounding contract and C0/prompt assembly separation.

        Returns:
            List of separation violations
        """
        violations = []

        # Find grounding contracts
        grounding_contracts = [
            node
            for node, attrs in self.graph.nodes(data=True)
            if "grounding" in attrs.get("name", "").lower() or "contract" in attrs.get("name", "").lower()
        ]

        # Find prompt assembly components
        prompt_assembly = [
            node
            for node, attrs in self.graph.nodes(data=True)
            if attrs.get("graph_type") in ["PromptTemplate", "PromptSlot", "PromptAssembly"]
        ]

        # Check for improper dependencies
        for contract in tqdm(grounding_contracts, desc="contracts", unit="contract", leave=False):
            for prompt_comp in tqdm(prompt_assembly, desc="  prompt comps", unit="comp", leave=False):
                if self.graph.has_edge(contract, prompt_comp):
                    attrs = self.graph.edges[contract, prompt_comp]
                    violations.append(
                        {
                            "type": "grounding_prompt_mixing",
                            "from_node": contract,
                            "to_node": prompt_comp,
                            "edge_type": attrs.get("graph_type"),
                            "issue": "Grounding contract directly depends on prompt assembly",
                        }
                    )

        return violations

    def trace_replay_eval_coverage(self) -> Dict[str, Any]:
        """Check trace/replay/eval coverage.

        Returns:
            Dictionary with coverage analysis
        """
        # Find trace, replay, and evaluation components
        trace_components = [
            node
            for node, attrs in self.graph.nodes(data=True)
            if attrs.get("graph_type") in ["ExecutionTrace", "TraceSurface"]
        ]

        replay_components = [
            node for node, attrs in self.graph.nodes(data=True) if "replay" in attrs.get("name", "").lower()
        ]

        eval_components = [
            node
            for node, attrs in self.graph.nodes(data=True)
            if attrs.get("graph_type") in ["Evaluator", "EvalMetric"]
        ]

        # Find execution components that should be traced
        execution_components = [
            node
            for node, attrs in self.graph.nodes(data=True)
            if attrs.get("properties", {}).get("layer") in ["L2", "L3"]
        ]

        # Check coverage
        traced_execution = set()
        for exec_comp in execution_components:
            # Check if execution component has trace edges
            trace_edges = [
                (u, v, attrs)
                for u, v, attrs in self.graph.edges(exec_comp, data=True)
                if attrs.get("graph_type") == "EMITS_TRACE"
            ]
            if trace_edges:
                traced_execution.add(exec_comp)

        return {
            "trace_components": len(trace_components),
            "replay_components": len(replay_components),
            "eval_components": len(eval_components),
            "execution_components": len(execution_components),
            "traced_execution": len(traced_execution),
            "trace_coverage": len(traced_execution) / len(execution_components)
            if execution_components
            else 0.0,
            "coverage_complete": len(traced_execution) == len(execution_components),
        }
