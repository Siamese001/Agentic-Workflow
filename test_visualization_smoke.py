#!/usr/bin/env python3
"""
Smoke test for visualization tools - ADG data visualization end-to-end test.
Tests matplotlib, seaborn, plotly, pyvis, and graphviz with ADG data.
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test all visualization imports."""
    print("\n[1/6] Testing visualization library imports...")
    try:
        import matplotlib

        matplotlib.use("Agg")  # Non-interactive backend for testing
        import matplotlib.pyplot as plt  # noqa: F401

        print("  ✓ matplotlib")
    except ImportError as e:
        print(f"  ✗ matplotlib: {e}")
        return False

    try:
        import seaborn as sns  # noqa: F401

        print("  ✓ seaborn")
    except ImportError as e:
        print(f"  ✗ seaborn: {e}")
        return False

    try:
        import plotly.express as px  # noqa: F401
        import plotly.graph_objects as go  # noqa: F401

        print("  ✓ plotly")
    except ImportError as e:
        print(f"  ✗ plotly: {e}")
        return False

    try:
        from pyvis.network import Network  # noqa: F401

        print("  ✓ pyvis")
    except ImportError as e:
        print(f"  ✗ pyvis: {e}")
        return False

    try:
        import graphviz  # noqa: F401

        print("  ✓ graphviz")
    except ImportError as e:
        print(f"  ✗ graphviz: {e}")
        return False

    try:
        import pandas as pd  # noqa: F401

        print("  ✓ pandas")
    except ImportError as e:
        print(f"  ✗ pandas: {e}")
        return False

    print("  All imports successful!")
    return True


def test_adg_connection():
    """Test connection to ADG SQLite database."""
    print("\n[2/6] Testing ADG database connection...")

    # Find ADG SQLite files
    artifacts_dir = Path("artifacts/adg")
    if not artifacts_dir.exists():
        print("  ⚠ artifacts/adg directory not found, checking artifacts/adg_clean/")
        artifacts_dir = Path("artifacts/adg_clean")

    if not artifacts_dir.exists():
        print("  ⚠ No ADG artifacts directory found - using synthetic test data")
        return None

    sqlite_files = list(artifacts_dir.glob("*.sqlite"))
    if not sqlite_files:
        print(f"  ⚠ No SQLite files found in {artifacts_dir}")
        return None

    # Use most recent file
    adg_file = sorted(sqlite_files, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    print(f"  ✓ Found ADG database: {adg_file}")

    try:
        conn = sqlite3.connect(str(adg_file))
        cursor = conn.cursor()

        # Test query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"  ✓ Connected successfully, tables: {[t[0] for t in tables]}")

        # Get node and edge counts
        cursor.execute("SELECT COUNT(*) FROM nodes")
        node_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM edges")
        edge_count = cursor.fetchone()[0]
        print(f"  ✓ Database stats: {node_count:,} nodes, {edge_count:,} edges")

        conn.close()
        return str(adg_file), node_count, edge_count
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return None


def test_matplotlib_visualization(node_count=1000, edge_count=5000):
    """Test matplotlib chart creation."""
    print("\n[3/6] Testing matplotlib static chart...")

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Create sample ADG stats visualization
        fig, ax = plt.subplots(figsize=(10, 6))

        categories = ["Nodes", "Edges", "Modules", "Relations"]
        values = [node_count, edge_count, node_count // 10, 15]
        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12"]

        bars = ax.bar(categories, values, color=colors)
        ax.set_title("ADG Graph Statistics", fontsize=14, fontweight="bold")
        ax.set_ylabel("Count")

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{int(height):,}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
            )

        output_path = Path("test_output_matplotlib.png")
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

        file_size = output_path.stat().st_size
        print(f"  ✓ Chart created: {output_path} ({file_size:,} bytes)")
        output_path.unlink()  # Clean up
        return True
    except Exception as e:
        print(f"  ✗ matplotlib test failed: {e}")
        return False


def test_plotly_interactive(node_count=1000, edge_count=5000):
    """Test Plotly interactive chart."""
    print("\n[4/6] Testing Plotly interactive chart...")

    try:
        import pandas as pd
        import plotly.graph_objects as go

        # Create sample ADG layer distribution data
        data = {
            "Layer": [
                "L0_routing",
                "L1_cognition",
                "L2_execution",
                "L3_orchestration",
                "L4_state",
                "L5_safety",
                "L6_runtime",
            ],
            "Node_Count": [
                node_count // 7,
                node_count // 6,
                node_count // 5,
                node_count // 4,
                node_count // 6,
                node_count // 8,
                node_count // 10,
            ],
            "Edge_Count": [
                edge_count // 7,
                edge_count // 6,
                edge_count // 5,
                edge_count // 4,
                edge_count // 6,
                edge_count // 8,
                edge_count // 10,
            ],
        }
        df = pd.DataFrame(data)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["Layer"], y=df["Node_Count"], name="Nodes", marker_color="#3498db"))
        fig.add_trace(go.Bar(x=df["Layer"], y=df["Edge_Count"], name="Edges", marker_color="#e74c3c"))

        fig.update_layout(
            title="ADG Layer Distribution (Interactive)",
            barmode="group",
            xaxis_title="Architecture Layer",
            yaxis_title="Count",
        )

        output_path = Path("test_output_plotly.html")
        fig.write_html(str(output_path))

        file_size = output_path.stat().st_size
        print(f"  ✓ Interactive chart created: {output_path} ({file_size:,} bytes)")
        output_path.unlink()  # Clean up
        return True
    except Exception as e:
        print(f"  ✗ plotly test failed: {e}")
        return False


def test_pyvis_network():
    """Test PyVis interactive network graph."""
    print("\n[5/6] Testing PyVis interactive network...")

    try:
        from pyvis.network import Network

        # Create sample ADG subgraph
        net = Network(height="400px", width="100%", bgcolor="#222222", font_color="white")
        net.barnes_hut()

        # Add sample nodes representing ADG architecture
        nodes = [
            ("L0_routing", "#3498db", 30),
            ("L1_cognition", "#2ecc71", 25),
            ("L2_execution", "#e74c3c", 25),
            ("L3_orchestration", "#f39c12", 20),
            ("L4_state", "#9b59b6", 20),
            ("L5_safety", "#1abc9c", 15),
            ("L6_runtime", "#34495e", 15),
        ]

        for node_id, color, size in nodes:
            net.add_node(node_id, label=node_id, color=color, size=size)

        # Add edges representing dependencies (lower layers -> higher layers)
        edges = [
            ("L0_routing", "L1_cognition"),
            ("L1_cognition", "L2_execution"),
            ("L2_execution", "L3_orchestration"),
            ("L3_orchestration", "L4_state"),
            ("L4_state", "L5_safety"),
            ("L5_safety", "L6_runtime"),
        ]

        for src, dst in edges:
            net.add_edge(src, dst)

        output_path = Path("test_output_pyvis.html")
        net.save_graph(str(output_path))

        file_size = output_path.stat().st_size
        print(f"  ✓ Interactive network created: {output_path} ({file_size:,} bytes)")
        output_path.unlink()  # Clean up
        return True
    except Exception as e:
        print(f"  ✗ pyvis test failed: {e}")
        return False


def test_graphviz_dot():
    """Test Graphviz DOT rendering."""
    print("\n[6/6] Testing Graphviz DOT rendering...")

    try:
        import graphviz

        # Create sample ADG architecture diagram
        dot = graphviz.Digraph(comment="ADG Architecture", format="png")
        dot.attr(rankdir="TB", bgcolor="#f8f9fa")

        # Add nodes for each layer
        layers = [
            ("L0", "L0: Routing", "#3498db"),
            ("L1", "L1: Cognition", "#2ecc71"),
            ("L2", "L2: Execution", "#e74c3c"),
            ("L3", "L3: Orchestration", "#f39c12"),
            ("L4", "L4: State", "#9b59b6"),
            ("L5", "L5: Safety", "#1abc9c"),
            ("L6", "L6: Runtime", "#34495e"),
        ]

        for layer_id, label, color in layers:
            dot.node(layer_id, label, style="filled", fillcolor=color, fontcolor="white")

        # Add edges
        for i in range(len(layers) - 1):
            dot.edge(layers[i][0], layers[i + 1][0])

        output_path = Path("test_output_graphviz")
        dot.render(str(output_path), cleanup=True)

        png_path = Path("test_output_graphviz.png")
        if png_path.exists():
            file_size = png_path.stat().st_size
            print(f"  ✓ DOT diagram rendered: {png_path} ({file_size:,} bytes)")
            png_path.unlink()
            return True
        else:
            print("  ✗ PNG output not found")
            return False
    except Exception as e:
        print(f"  ✗ graphviz test failed: {e}")
        return False


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("ADG Visualization Smoke Test - End-to-End")
    print("=" * 60)

    results = {}

    # Test 1: Imports
    results["imports"] = test_imports()

    # Test 2: ADG Connection
    adg_info = test_adg_connection()
    results["adg_connection"] = adg_info is not None

    # Use real ADG data if available, otherwise use synthetic
    if adg_info:
        _, node_count, edge_count = adg_info
    else:
        node_count, edge_count = 1000, 5000

    # Test 3: Matplotlib
    results["matplotlib"] = test_matplotlib_visualization(node_count, edge_count)

    # Test 4: Plotly
    results["plotly"] = test_plotly_interactive(node_count, edge_count)

    # Test 5: PyVis
    results["pyvis"] = test_pyvis_network()

    # Test 6: Graphviz
    results["graphviz"] = test_graphviz_dot()

    # Summary
    print("\n" + "=" * 60)
    print("SMOKE TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"  {status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed ({passed / total * 100:.0f}%)")

    if passed == total:
        print("\n🎉 All smoke tests PASSED! Visualization stack is ready.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
