#!/usr/bin/env python3
"""
Windsurf Real-Time Progress Dashboard — Plotly Dash App

Real-time monitoring of healing, MCP hardening, and validation progress.
Auto-refreshes every 30 seconds from windsurf_log.json.

Run: python scripts/windsurf_realtime_dashboard_util.py
Open: http://127.0.0.1:8050

Prerequisites: pip install dash pandas plotly
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import dash
    from dash import dcc, html
    from dash.dependencies import Input, Output
except ImportError as _err:
    raise ImportError(
        "dash is required for this module. Install with: pip install -e '.[infra]'",
    ) from _err
try:
    import pandas as pd
except ImportError as _err:
    raise ImportError(
        "pandas is required for this module. Install with: pip install -e '.[infra]'",
    ) from _err
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError as _err:
    raise ImportError(
        "plotly is required for this module. Install with: pip install -e '.[infra]'",
    ) from _err

# Path to log file (project root)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = PROJECT_ROOT / "windsurf_log.json"

# Lazy initialization - app created only when run directly
_app = None


def _get_app():
    """Get or create the Dash app (lazy initialization)."""
    global _app
    if _app is None:
        _app = dash.Dash(__name__, title="Windsurf Real-Time Progress", update_title=None)
    return _app


def load_data() -> pd.DataFrame:
    """Load data from windsurf_log.json."""
    if LOG_PATH.exists():
        try:
            with open(LOG_PATH) as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["date"])
            df["cumulative_commits"] = df["commits"].cumsum()
            # Handle optional fields
            if "mcp_hardened" not in df.columns:
                df["mcp_hardened"] = 0
            if "regressions" not in df.columns:
                df["regressions"] = 0
            return df
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()
    return pd.DataFrame()


def get_latest_stats(df: pd.DataFrame) -> dict[str, Any]:
    """Get latest statistics from dataframe."""
    if df.empty:
        return {"healing_pct": 0, "healed": 0, "total": 0, "mcp": 0, "commits": 0, "regressions": 0}
    latest = df.iloc[-1]
    return {
        "healing_pct": latest.get("healing_core_pct", 0),
        "healed": latest.get("healed_agents", 0),
        "total": latest.get("total_core", 0),
        "mcp": latest.get("mcp_hardened", 0),
        "commits": df["commits"].sum(),
        "regressions": latest.get("regressions", 0),
    }


def _create_layout():
    """Create the app layout (called only when app is initialized)."""
    return html.Div(
        [
            # Header
            html.Div(
                [
                    html.H1(
                        "🌊 Windsurf Real-Time Progress Dashboard",
                        style={"textAlign": "center", "color": "#1E3A8A", "marginBottom": "10px"},
                    ),
                    html.P(
                        "Autonomous Healing & MCP Hardening Progress",
                        style={"textAlign": "center", "color": "#6B7280", "marginTop": "0"},
                    ),
                ],
                style={
                    "backgroundColor": "#F3F4F6",
                    "padding": "20px",
                    "borderRadius": "10px",
                    "marginBottom": "20px",
                },
            ),
            # Auto-refresh interval (30 seconds)
            dcc.Interval(id="interval-component", interval=30 * 1000, n_intervals=0),
            # Stats cards row
            html.Div(
                id="stats-cards",
                style={
                    "display": "flex",
                    "justifyContent": "space-around",
                    "marginBottom": "30px",
                    "flexWrap": "wrap",
                },
            ),
            # Charts row 1
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="healing-line-chart")],
                        style={"width": "60%", "display": "inline-block", "verticalAlign": "top"},
                    ),
                    html.Div(
                        [dcc.Graph(id="coverage-pie-chart")],
                        style={"width": "38%", "display": "inline-block", "verticalAlign": "top"},
                    ),
                ],
                style={"marginBottom": "20px"},
            ),
            # Charts row 2
            html.Div([dcc.Graph(id="cumulative-dual-chart")], style={"marginBottom": "20px"}),
            # Charts row 3 (MCP if available)
            html.Div([dcc.Graph(id="mcp-progress-chart")], style={"marginBottom": "20px"}),
            # Footer with last update
            html.Div(
                id="last-update",
                style={
                    "textAlign": "center",
                    "padding": "15px",
                    "backgroundColor": "#F3F4F6",
                    "borderRadius": "10px",
                    "color": "#6B7280",
                },
            ),
        ],
        style={
            "fontFamily": "Arial, sans-serif",
            "padding": "20px",
            "maxWidth": "1400px",
            "margin": "0 auto",
        },
    )


def create_stat_card(title: str, value: str, color: str, icon: str) -> html.Div:
    """Create a statistics card component."""
    return html.Div(
        [
            html.Div(icon, style={"fontSize": "24px", "marginBottom": "5px"}),
            html.Div(value, style={"fontSize": "28px", "fontWeight": "bold", "color": color}),
            html.Div(title, style={"fontSize": "14px", "color": "#6B7280"}),
        ],
        style={
            "backgroundColor": "white",
            "padding": "20px",
            "borderRadius": "10px",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
            "textAlign": "center",
            "minWidth": "150px",
            "margin": "5px",
        },
    )


def _register_callbacks(app):
    """Register callbacks on the app (called only when app is initialized)."""

    @app.callback(
        [
            Output("stats-cards", "children"),
            Output("healing-line-chart", "figure"),
            Output("coverage-pie-chart", "figure"),
            Output("cumulative-dual-chart", "figure"),
            Output("mcp-progress-chart", "figure"),
            Output("last-update", "children"),
        ],
        Input("interval-component", "n_intervals"),
    )
    def update_dashboard(n_intervals):
        """Update all dashboard components."""
        df = load_data()
        stats = get_latest_stats(df)

        # Stats cards
        cards = [
            create_stat_card("Core Healing", f"{stats['healing_pct']}%", "#10B981", "G"),
            create_stat_card("Healed Agents", f"{stats['healed']}/{stats['total']}", "#1E3A8A", "W"),
            create_stat_card("MCP Hardened", f"{stats['mcp']}", "#8B5CF6", "S"),
            create_stat_card("Total Commits", f"{stats['commits']}", "#F59E0B", "C"),
            create_stat_card(
                "Regressions",
                f"{stats['regressions']}",
                "#10B981" if stats["regressions"] == 0 else "#EF4444",
                "!",
            ),
        ]

        if df.empty:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="No data available",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font={"size": 20},
            )
            return cards, empty_fig, empty_fig, empty_fig, empty_fig, "No data loaded"

        # Line chart: Healing % Progress
        fig_line = px.line(
            df,
            x="batch",
            y="healing_core_pct",
            markers=True,
            title="Core Healing % Progress Over Time",
        )
        fig_line.update_traces(line_color="#10B981", line_width=3, marker_size=10)
        fig_line.add_hline(
            y=70,
            line_dash="dash",
            line_color="#EF4444",
            annotation_text="70% Target",
            annotation_position="right",
        )
        fig_line.add_hline(
            y=100,
            line_dash="dot",
            line_color="#8B5CF6",
            annotation_text="100% Goal",
            annotation_position="right",
        )
        fig_line.update_layout(
            xaxis_title="Batch",
            yaxis_title="Healing %",
            yaxis_range=[0, 105],
            template="plotly_white",
        )

        # Pie chart: Current Coverage
        fig_pie = px.pie(
            values=[stats["healed"], stats["total"] - stats["healed"]],
            names=["Healed", "Unhealed"],
            title="Current Core Coverage",
            color_discrete_sequence=["#10B981", "#E5E7EB"],
        )
        fig_pie.update_traces(textinfo="percent+value", pull=[0.05, 0])

        # Dual axis: Cumulative Progress
        fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
        fig_dual.add_trace(
            go.Scatter(
                x=df["batch"],
                y=df["healed_agents"],
                name="Healed Agents",
                line={"color": "#1E3A8A", "width": 3},
                mode="lines+markers",
            ),
            secondary_y=False,
        )
        fig_dual.add_trace(
            go.Scatter(
                x=df["batch"],
                y=df["cumulative_commits"],
                name="Cumulative Commits",
                line={"color": "#F59E0B", "width": 3},
                mode="lines+markers",
            ),
            secondary_y=True,
        )
        fig_dual.update_layout(title="Healed Agents vs Cumulative Commits", template="plotly_white")
        fig_dual.update_yaxes(title_text="Healed Agents", secondary_y=False)
        fig_dual.update_yaxes(title_text="Cumulative Commits", secondary_y=True)

        # MCP Progress chart
        if "mcp_hardened" in df.columns and df["mcp_hardened"].sum() > 0:
            fig_mcp = px.bar(
                df,
                x="batch",
                y="mcp_hardened",
                title="MCP Hardened Agents Progress",
                color="mcp_hardened",
                color_continuous_scale=["#E5E7EB", "#8B5CF6"],
            )
            fig_mcp.update_layout(template="plotly_white", showlegend=False)
        else:
            fig_mcp = go.Figure()
            fig_mcp.add_annotation(
                text="MCP Hardening data will appear after Phase 4",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            fig_mcp.update_layout(title="MCP Hardened Agents Progress")

        # Last update timestamp
        last_update = f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refresh every 30s"

        return cards, fig_line, fig_pie, fig_dual, fig_mcp, last_update


def _initialize_app():
    """Initialize the app with layout and callbacks."""
    app = _get_app()
    app.layout = _create_layout()
    _register_callbacks(app)
    return app


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Windsurf Real-Time Progress Dashboard")
    print("=" * 60)
    print(f"\nLoading data from: {LOG_PATH}")
    print("Dashboard URL: http://127.0.0.1:8050")
    print("Auto-refresh: Every 30 seconds")
    print("\nPress Ctrl+C to stop the server\n")

    app = _initialize_app()
    app.run(debug=True, host="127.0.0.1", port=8050)
