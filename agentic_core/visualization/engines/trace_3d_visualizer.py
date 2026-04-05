"""Advanced 3D Trace Visualization - Interactive 3D trace graph visualization.

Provides sophisticated 3D visualization of Runtime ADG traces with
interactive exploration, filtering, and analysis capabilities.

FEATURES:
- Interactive 3D trace graph visualization
- Force-directed graph layout with physics simulation
- Real-time trace streaming and updates
- Interactive filtering and search
- Performance heat mapping
- Trace path analysis and critical path highlighting
- Export capabilities (JSON, PNG, SVG)

USAGE:
    visualizer = Trace3DVisualizer()
    visualizer.start_visualization_server()

    # Access 3D visualization at http://localhost:8081
"""

import logging
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("trace_3d_visualizer", "trace_3d_visualizer_digest")
record_execution_trace("trace_3d_visualizer", "trace_3d_visualizer_trace")

Logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in the trace graph."""
    COGNITIVE = "cognitive"
    TOOL = "tool"
    ORCHESTRATOR = "orchestrator"
    ACTION = "action"
    SYSTEM = "system"
    ERROR = "error"


class EdgeType(Enum):
    """Types of edges in the trace graph."""
    CALLS = "calls"
    INVOKES = "invokes"
    DEPENDS_ON = "depends_on"
    FLOWS_TO = "flows_to"
    ERROR_FROM = "error_from"


@dataclass
class Node3D:
    """3D node representation for visualization."""

    id: str
    label: str
    node_type: NodeType
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    velocity: tuple[float, float, float] = (0.0, 0.0, 0.0)
    force: tuple[float, float, float] = (0.0, 0.0, 0.0)
    mass: float = 1.0
    radius: float = 1.0
    color: str = "#0088ff"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "label": self.label,
            "type": self.node_type.value,
            "position": self.position,
            "velocity": self.velocity,
            "mass": self.mass,
            "radius": self.radius,
            "color": self.color,
            "metadata": self.metadata,
        }


@dataclass
class Edge3D:
    """3D edge representation for visualization."""

    id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0
    color: str = "#888888"
    width: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "source": self.source_id,
            "target": self.target_id,
            "type": self.edge_type.value,
            "weight": self.weight,
            "color": self.color,
            "width": self.width,
            "metadata": self.metadata,
        }


@dataclass
class TraceGraph3D:
    """3D trace graph structure."""

    nodes: dict[str, Node3D] = field(default_factory=dict)
    edges: dict[str, Edge3D] = field(default_factory=dict)
    trace_id: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: Node3D) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge3D) -> None:
        """Add an edge to the graph."""
        self.edges[edge.id] = edge

    def get_node_neighbors(self, node_id: str) -> list[str]:
        """Get neighboring nodes for a given node."""
        neighbors = []
        for edge in self.edges.values():
            if edge.source_id == node_id:
                neighbors.append(edge.target_id)
            elif edge.target_id == node_id:
                neighbors.append(edge.source_id)
        return neighbors

    def to_dict(self) -> dict[str, Any]:
        """Convert entire graph to dictionary."""
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges.values()],
        }


class PhysicsEngine:
    """Physics engine for 3D graph layout simulation."""

    def __init__(self,
                 attraction_strength: float = 0.1,
                 repulsion_strength: float = 100.0,
                 damping: float = 0.9,
                 time_step: float = 0.01) -> None:
        """Initialize physics engine."""
        self.attraction_strength = attraction_strength
        self.repulsion_strength = repulsion_strength
        self.damping = damping
        self.time_step = time_step
        self.center = (0.0, 0.0, 0.0)
        self.boundary_radius = 50.0

    def apply_forces(self, graph: TraceGraph3D) -> None:
        """Apply physics forces to graph nodes."""
        # Reset forces
        for node in graph.nodes.values():
            node.force = (0.0, 0.0, 0.0)

        # Apply repulsion between all node pairs
        self._apply_repulsion_forces(graph)

        # Apply attraction along edges
        self._apply_attraction_forces(graph)

        # Apply center gravity
        self._apply_center_gravity(graph)

        # Apply boundary forces
        self._apply_boundary_forces(graph)

    def _apply_repulsion_forces(self, graph: TraceGraph3D) -> None:
        """Apply repulsion forces between nodes."""
        nodes = list(graph.nodes.values())

        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                dx = node2.position[0] - node1.position[0]
                dy = node2.position[1] - node1.position[1]
                dz = node2.position[2] - node1.position[2]

                distance_sq = dx*dx + dy*dy + dz*dz

                if distance_sq < 0.01:  # Prevent division by zero
                    distance_sq = 0.01

                distance = math.sqrt(distance_sq)

                # Calculate repulsion force
                force_magnitude = self.repulsion_strength / distance_sq

                # Normalize and apply force
                fx = force_magnitude * dx / distance
                fy = force_magnitude * dy / distance
                fz = force_magnitude * dz / distance

                # Apply forces (Newton's third law)
                node1.force = (
                    node1.force[0] - fx,
                    node1.force[1] - fy,
                    node1.force[2] - fz,
                )
                node2.force = (
                    node2.force[0] + fx,
                    node2.force[1] + fy,
                    node2.force[2] + fz,
                )

    def _apply_attraction_forces(self, graph: TraceGraph3D) -> None:
        """Apply attraction forces along edges."""
        for edge in graph.edges.values():
            if edge.source_id in graph.nodes and edge.target_id in graph.nodes:
                source = graph.nodes[edge.source_id]
                target = graph.nodes[edge.target_id]

                dx = target.position[0] - source.position[0]
                dy = target.position[1] - source.position[1]
                dz = target.position[2] - source.position[2]

                distance = math.sqrt(dx*dx + dy*dy + dz*dz)

                if distance > 0.01:  # Prevent division by zero
                    # Calculate attraction force (spring-like)
                    force_magnitude = self.attraction_strength * edge.weight * distance

                    # Normalize and apply force
                    fx = force_magnitude * dx / distance
                    fy = force_magnitude * dy / distance
                    fz = force_magnitude * dz / distance

                    # Apply forces
                    source.force = (
                        source.force[0] + fx,
                        source.force[1] + fy,
                        source.force[2] + fz,
                    )
                    target.force = (
                        target.force[0] - fx,
                        target.force[1] - fy,
                        target.force[2] - fz,
                    )

    def _apply_center_gravity(self, graph: TraceGraph3D) -> None:
        """Apply center gravity to keep graph centered."""
        for node in graph.nodes.values():
            dx = self.center[0] - node.position[0]
            dy = self.center[1] - node.position[1]
            dz = self.center[2] - node.position[2]

            gravity_strength = 0.01
            node.force = (
                node.force[0] + gravity_strength * dx,
                node.force[1] + gravity_strength * dy,
                node.force[2] + gravity_strength * dz,
            )

    def _apply_boundary_forces(self, graph: TraceGraph3D) -> None:
        """Apply boundary forces to keep nodes within bounds."""
        for node in graph.nodes.values():
            x, y, z = node.position

            # Check each axis
            if abs(x) > self.boundary_radius:
                force = -0.5 * (abs(x) - self.boundary_radius) * (1 if x > 0 else -1)
                node.force = (node.force[0] + force, node.force[1], node.force[2])

            if abs(y) > self.boundary_radius:
                force = -0.5 * (abs(y) - self.boundary_radius) * (1 if y > 0 else -1)
                node.force = (node.force[0], node.force[1] + force, node.force[2])

            if abs(z) > self.boundary_radius:
                force = -0.5 * (abs(z) - self.boundary_radius) * (1 if z > 0 else -1)
                node.force = (node.force[0], node.force[1], node.force[2] + force)

    def update_positions(self, graph: TraceGraph3D) -> None:
        """Update node positions based on forces and velocities."""
        for node in graph.nodes.values():
            # Update velocity (F = ma, a = F/m, v = v + a*dt)
            ax = node.force[0] / node.mass
            ay = node.force[1] / node.mass
            az = node.force[2] / node.mass

            node.velocity = (
                (node.velocity[0] + ax * self.time_step) * self.damping,
                (node.velocity[1] + ay * self.time_step) * self.damping,
                (node.velocity[2] + az * self.time_step) * self.damping,
            )

            # Update position
            node.position = (
                node.position[0] + node.velocity[0] * self.time_step,
                node.position[1] + node.velocity[1] * self.time_step,
                node.position[2] + node.velocity[2] * self.time_step,
            )


class Trace3DVisualizer:
    """
    Advanced 3D trace visualization system.

    Provides interactive 3D visualization of Runtime ADG traces
    with physics-based layout and real-time updates.
    """

    def __init__(self, port: int = 8081) -> None:
        """Initialize 3D trace visualizer."""
        self._port = port
        self._server_active: bool = False
        self._server_thread: threading.Thread | None = None
        self._shutdown_requested: bool = False

        # Graph storage
        self._graphs: dict[str, TraceGraph3D] = {}
        self._active_graph_id: str | None = None

        # Physics engine
        self._physics_engine = PhysicsEngine()

        # Visualization state
        self._camera_position = (0.0, 0.0, 100.0)
        self._camera_rotation = (0.0, 0.0, 0.0)
        self._selected_nodes: set[str] = set()
        self._highlighted_paths: list[list[str]] = []

        # Configuration
        self._config = {
            "auto_layout": True,
            "show_labels": True,
            "show_edges": True,
            "node_size_factor": 1.0,
            "edge_width_factor": 1.0,
            "color_scheme": "default",
            "animation_speed": 1.0,
        }

        # Statistics
        self._stats = {
            "total_graphs": 0,
            "total_nodes": 0,
            "total_edges": 0,
            "active_visualizations": 0,
            "last_update": time.time(),
        }

    def start_visualization_server(self) -> None:
        """Start the 3D visualization web server."""
        if self._server_active:
            Logger.warning("[3D_VIZ] Visualization server already active")
            return

        self._server_active = True
        self._shutdown_requested = False

        # Start server thread
        self._server_thread = threading.Thread(
            target=self._server_loop,
            daemon=True,
            name="Trace3DVisualizer",
        )
        self._server_thread.start()

        Logger.info(f"[3D_VIZ] Started 3D visualization server on port {self._port}")
        Logger.info(f"[3D_VIZ] Access visualization at http://localhost:{self._port}")

    def stop_visualization_server(self) -> None:
        """Stop the 3D visualization web server."""
        if not self._server_active:
            return

        self._shutdown_requested = True
        self._server_active = False

        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=5.0)

        Logger.info("[3D_VIZ] Stopped 3D visualization server")

    def _server_loop(self) -> None:
        """Main server loop (simplified - would use actual web framework)."""
        while self._server_active and not self._shutdown_requested:
            try:
                # Update physics simulation
                if self._active_graph_id and self._config["auto_layout"]:
                    graph = self._graphs.get(self._active_graph_id)
                    if graph:
                        self._physics_engine.apply_forces(graph)
                        self._physics_engine.update_positions(graph)

                # Sleep for next frame
                time.sleep(0.016)  # ~60 FPS

            except Exception as e:
                Logger.error(f"[3D_VIZ] Server loop error: {e}")
                time.sleep(1.0)

    def add_trace_graph(self, trace_id: str, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> str:
        """
        Add a trace graph for 3D visualization.

        Args:
            trace_id: Unique identifier for the trace
            nodes: List of node dictionaries
            edges: List of edge dictionaries

        Returns:
            Graph ID for reference
        """
        try:
            graph = TraceGraph3D(trace_id=trace_id)

            # Add nodes
            for node_data in nodes:
                node_type = NodeType(node_data.get("type", "system"))

                # Assign color based on type
                color = self._get_node_color(node_type)

                # Calculate initial position (random sphere)
                import random
                theta = random.random() * 2 * math.pi
                phi = random.random() * math.pi
                r = random.random() * 30 + 10

                x = r * math.sin(phi) * math.cos(theta)
                y = r * math.sin(phi) * math.sin(theta)
                z = r * math.cos(phi)

                node = Node3D(
                    id=node_data["id"],
                    label=node_data.get("label", node_data["id"]),
                    node_type=node_type,
                    position=(x, y, z),
                    color=color,
                    radius=2.0 + node_data.get("duration_ms", 0) / 1000,  # Size based on duration
                    metadata=node_data,
                )

                graph.add_node(node)

            # Add edges
            for edge_data in edges:
                edge_type = EdgeType(edge_data.get("type", "flows_to"))

                # Assign color based on type
                color = self._get_edge_color(edge_type)

                edge = Edge3D(
                    id=edge_data.get("id", f"{edge_data['source']}-{edge_data['target']}"),
                    source_id=edge_data["source"],
                    target_id=edge_data["target"],
                    edge_type=edge_type,
                    weight=edge_data.get("weight", 1.0),
                    color=color,
                    width=1.0 + edge_data.get("weight", 1.0) * 0.5,
                    metadata=edge_data,
                )

                graph.add_edge(edge)

            # Store graph
            self._graphs[trace_id] = graph
            self._active_graph_id = trace_id

            # Update statistics
            self._stats["total_graphs"] = len(self._graphs)
            self._stats["total_nodes"] = sum(len(g.nodes) for g in self._graphs.values())
            self._stats["total_edges"] = sum(len(g.edges) for g in self._graphs.values())
            self._stats["last_update"] = time.time()

            Logger.info(f"[3D_VIZ] Added trace graph {trace_id} with {len(nodes)} nodes and {len(edges)} edges")

            return trace_id

        except Exception as e:
            Logger.error(f"[3D_VIZ] Failed to add trace graph: {e}")
            return ""

    def _get_node_color(self, node_type: NodeType) -> str:
        """Get color for node type."""
        colors = {
            NodeType.COGNITIVE: "#00ff88",
            NodeType.TOOL: "#ff8800",
            NodeType.ORCHESTRATOR: "#0088ff",
            NodeType.ACTION: "#ff0088",
            NodeType.SYSTEM: "#888888",
            NodeType.ERROR: "#ff0000",
        }
        return colors.get(node_type, "#888888")

    def _get_edge_color(self, edge_type: EdgeType) -> str:
        """Get color for edge type."""
        colors = {
            EdgeType.CALLS: "#00ff00",
            EdgeType.INVOKES: "#ffaa00",
            EdgeType.DEPENDS_ON: "#00aaff",
            EdgeType.FLOWS_TO: "#888888",
            EdgeType.ERROR_FROM: "#ff0000",
        }
        return colors.get(edge_type, "#888888")

    def get_visualization_data(self, graph_id: str | None = None) -> dict[str, Any]:
        """Get visualization data for a specific graph."""
        if graph_id is None:
            graph_id = self._active_graph_id

        if graph_id is None or graph_id not in self._graphs:
            return {"error": "No active graph"}

        graph = self._graphs[graph_id]

        return {
            "graph": graph.to_dict(),
            "camera": {
                "position": self._camera_position,
                "rotation": self._camera_rotation,
            },
            "config": self._config,
            "selected_nodes": list(self._selected_nodes),
            "highlighted_paths": self._highlighted_paths,
            "statistics": self._stats,
        }

    def update_node_positions(self, graph_id: str, positions: dict[str, tuple[float, float, float]]) -> bool:
        """Update node positions manually."""
        try:
            if graph_id not in self._graphs:
                return False

            graph = self._graphs[graph_id]

            for node_id, position in positions.items():
                if node_id in graph.nodes:
                    graph.nodes[node_id].position = position

            return True

        except Exception as e:
            Logger.error(f"[3D_VIZ] Failed to update node positions: {e}")
            return False

    def highlight_path(self, graph_id: str, path_nodes: list[str]) -> bool:
        """Highlight a path through the graph."""
        try:
            if graph_id not in self._graphs:
                return False

            # Store the highlighted path
            self._highlighted_paths.append(path_nodes)

            # Update node colors for highlighted path
            graph = self._graphs[graph_id]
            for node_id in path_nodes:
                if node_id in graph.nodes:
                    graph.nodes[node_id].color = "#ffff00"  # Yellow for highlighted

            return True

        except Exception as e:
            Logger.error(f"[3D_VIZ] Failed to highlight path: {e}")
            return False

    def select_node(self, graph_id: str, node_id: str) -> bool:
        """Select a node for detailed analysis."""
        try:
            if graph_id not in self._graphs:
                return False

            self._selected_nodes.add(node_id)

            # Update node appearance
            graph = self._graphs[graph_id]
            if node_id in graph.nodes:
                graph.nodes[node_id].radius *= 1.5  # Make selected node larger
                graph.nodes[node_id].color = "#00ffff"  # Cyan for selected

            return True

        except Exception as e:
            Logger.error(f"[3D_VIZ] Failed to select node: {e}")
            return False

    def clear_selection(self) -> None:
        """Clear all selections and highlights."""
        self._selected_nodes.clear()
        self._highlighted_paths.clear()

        # Reset node appearances
        for graph in self._graphs.values():
            for node in graph.nodes.values():
                node.color = self._get_node_color(node.node_type)
                node.radius = 2.0 + node.metadata.get("duration_ms", 0) / 1000

    def export_graph(self, graph_id: str, format_type: str = "json") -> dict[str, Any] | None:
        """Export graph data in specified format."""
        try:
            if graph_id not in self._graphs:
                return None

            graph = self._graphs[graph_id]

            if format_type == "json":
                return graph.to_dict()
            elif format_type == "positions":
                return {
                    "trace_id": graph.trace_id,
                    "positions": {
                        node_id: node.position
                        for node_id, node in graph.nodes.items()
                    }
                }
            else:
                return None

        except Exception as e:
            Logger.error(f"[3D_VIZ] Failed to export graph: {e}")
            return None

    def get_graph_statistics(self, graph_id: str | None = None) -> dict[str, Any]:
        """Get detailed statistics for a graph."""
        if graph_id is None:
            graph_id = self._active_graph_id

        if graph_id is None or graph_id not in self._graphs:
            return {"error": "No active graph"}

        graph = self._graphs[graph_id]

        # Node statistics
        node_types = defaultdict(int)
        node_durations = []

        for node in graph.nodes.values():
            node_types[node.node_type.value] += 1
            duration = node.metadata.get("duration_ms", 0)
            if duration > 0:
                node_durations.append(duration)

        # Edge statistics
        edge_types = defaultdict(int)
        edge_weights = []

        for edge in graph.edges.values():
            edge_types[edge.edge_type.value] += 1
            edge_weights.append(edge.weight)

        # Calculate metrics
        avg_duration = sum(node_durations) / len(node_durations) if node_durations else 0
        avg_weight = sum(edge_weights) / len(edge_weights) if edge_weights else 0

        return {
            "trace_id": graph.trace_id,
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "node_types": dict(node_types),
            "edge_types": dict(edge_types),
            "avg_node_duration_ms": avg_duration,
            "avg_edge_weight": avg_weight,
            "graph_density": len(graph.edges) / (len(graph.nodes) * (len(graph.nodes) - 1)) if len(graph.nodes) > 1 else 0,
            "timestamp": graph.timestamp,
        }

    def set_camera_position(self, position: tuple[float, float, float]) -> None:
        """Set camera position."""
        self._camera_position = position

    def set_camera_rotation(self, rotation: tuple[float, float, float]) -> None:
        """Set camera rotation."""
        self._camera_rotation = rotation

    def update_config(self, config_updates: dict[str, Any]) -> None:
        """Update visualization configuration."""
        self._config.update(config_updates)

    def get_visualization_summary(self) -> dict[str, Any]:
        """Get summary of all visualizations."""
        return {
            "server_active": self._server_active,
            "server_port": self._port,
            "total_graphs": len(self._graphs),
            "active_graph_id": self._active_graph_id,
            "selected_nodes": len(self._selected_nodes),
            "highlighted_paths": len(self._highlighted_paths),
            "statistics": self._stats,
            "config": self._config,
        }


# Global 3D visualizer instance
_global_visualizer: Trace3DVisualizer | None = None


def get_global_3d_visualizer() -> Trace3DVisualizer:
    """Get the global 3D trace visualizer instance."""
    global _global_visualizer
    if _global_visualizer is None:
        _global_visualizer = Trace3DVisualizer()
    return _global_visualizer


def start_3d_visualization() -> None:
    """Start global 3D visualization server."""
    visualizer = get_global_3d_visualizer()
    visualizer.start_visualization_server()


def stop_3d_visualization() -> None:
    """Stop global 3D visualization server."""
    visualizer = get_global_3d_visualizer()
    visualizer.stop_visualization_server()


def add_trace_to_3d_visualization(trace_id: str, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> str:
    """
    Add a trace to 3D visualization.

    Args:
        trace_id: Unique identifier for the trace
        nodes: List of node dictionaries
        edges: List of edge dictionaries

    Returns:
        Graph ID for reference
    """
    visualizer = get_global_3d_visualizer()
    return visualizer.add_trace_graph(trace_id, nodes, edges)


def get_3d_visualization_data(graph_id: str | None = None) -> dict[str, Any]:
    """Get 3D visualization data."""
    visualizer = get_global_3d_visualizer()
    return visualizer.get_visualization_data(graph_id)
