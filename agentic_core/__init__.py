AGENTIC CORE: THE BRAIN (Key 40)
================================
The sovereign domain for domain-agnostic agentic reasoning.
This package contains the 5 Atomic Layers of the architecture.

STRUCTURE:
- L1_cognition/       : Strategy, Planning, Reflection
- L2_execution/       : Tools, Engines, IO
- L3_orchestration/   : Workflows, Fission, Delegation
- L4_state/           : Context, Memory, Persistence
- L5_safety/          : Guardrails, Security, PII

COMPLIANCE:
- This package is SOVEREIGN. It must NOT import from 'apps_*'.
- Domain-specific logic (e.g., 'BulletNarrative') belongs in 'apps_rg'.
"""

import json
import logging
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# ==============================================================================
# 1. SOVEREIGN CONFIGURATION
# ==============================================================================

__version__ = "2.8.0"
__author__ = "Architecture Governor"

# Configure centralized logger for The Brain
_logger = logging.getLogger("agentic_core")
_logger.setLevel(logging.INFO) # Can be overridden by Key 0 (Global Config)

# ==============================================================================
# 2. LAYER EXPOSURE
# ==============================================================================

# We explicitly do NOT import all agents here to prevent:
# 1. Circular Dependencies (The "Mega-Init" anti-pattern)
# 2. Premature loading of heavy ML libraries
# 3. Violation of Fission (Agents should be imported only when needed)

# Agents should be discovered via 'canon_validator' or imported specifically:
# from agentic_core.L5_safety import PIISanitizerAgent

# ==============================================================================
# 3. RUNTIME BRIDGE (The Janitor)
# ==============================================================================

# Expose compliance tools for external validators (Key 46/47)
try:
    from .runtime import compliance
except ImportError:
    # Allow partial initialization during bootstrapping/migration
    _logger.warning("agentic_core.runtime.compliance not found. Skipping bridge.")
    compliance = None

# ==============================================================================
# 4. FLIGHT RECORDER DASHBOARD (Architectural Violation for Debugging)
# ==============================================================================
# WARNING: This section introduces UI/DB dependencies into agentic_core,
# violating its sovereign principles. It is intended for debugging purposes only
# and should ideally reside in a separate 'apps_debug' package.

try:
    import duckdb
    import plotly.express as px
    _DASHBOARD_DEPS_AVAILABLE = True
except ImportError:
    _DASHBOARD_DEPS_AVAILABLE = False

_DASHBOARD_DB_PATH = "flight_recorder.duckdb"

@st.cache_resource
def _get_dashboard_connection():
    """Get cached database connection for the Flight Recorder Dashboard."""
    try:
        return duckdb.connect(_DASHBOARD_DB_PATH, read_only=True)
    except Exception as e:
        _logger.error(f"Cannot connect to dashboard database: {e}")
        _logger.info(f"Looking for dashboard database at: {Path(_DASHBOARD_DB_PATH).absolute()}")
        return None

def run_flight_recorder_dashboard():
    """
    Launches the Subatomic Flight Recorder Dashboard.
    This function encapsulates the Streamlit UI logic.
    To run: `streamlit run path/to/agentic_core/__init__.py`
    (Note: Running __init__.py directly with streamlit is unusual,
    consider creating a dedicated launcher script if this becomes permanent.)
    """
    if not _DASHBOARD_DEPS_AVAILABLE:
        st.error("Missing dashboard dependencies. Install with: pip install streamlit plotly pandas duckdb")
        st.stop()

    st.set_page_config(layout="wide", page_title="✈️ Subatomic Flight Recorder")

    _dashboard_conn = _get_dashboard_connection()

    if not _dashboard_conn:
        st.stop()

    st.title("✈️ Subatomic Flight Recorder")
    st.markdown("**Real-time Agent Cognition Observatory**")

    try:
        traces_df = _dashboard_conn.execute("""
            SELECT DISTINCT trace_id,
                   MIN(timestamp) as start_time,
                   MAX(timestamp) as end_time,
                   COUNT(*) as event_count
            from traces
            GROUP BY trace_id
            ORDER BY start_time DESC
            LIMIT 50
        """).df()
    except Exception as e:
        st.error(f"Database query error: {e}")
        st.info("The database might be empty. Run some agents to generate trace data.")
        st.stop()

    if traces_df.empty:
        st.warning("No traces found in the database. Run some agents to generate trace data.")
        st.info(f"Database location: {Path(_DASHBOARD_DB_PATH).absolute()}")
        st.stop()

    traces_df['start_time'] = pd.to_datetime(traces_df['start_time'], unit='s')
    traces_df['end_time'] = pd.to_datetime(traces_df['end_time'], unit='s')
    traces_df['duration'] = (traces_df['end_time'] - traces_df['start_time']).dt.total_seconds()

    st.sidebar.header("🎯 Trace Selection")

    trace_display = traces_df.apply(
        lambda row: f"{row['trace_id']} ({row['event_count']} events, {row['duration']:.1f}s)",
        axis=1
    )

    selected_idx = st.sidebar.selectbox(
        "Select Mission Trace",
        range(len(traces_df)),
        format_func=lambda i: trace_display.iloc[i]
    )

    selected_trace = traces_df.iloc[selected_idx]['trace_id']

    st.sidebar.markdown("---")
    st.sidebar.metric("Total Traces", len(traces_df))
    st.sidebar.metric("Total Events", traces_df['event_count'].sum())

    st.header(f"🛸 Mission Timeline: `{selected_trace}`")

    COL1, COL2, COL3 = st.columns(3)
    with COL1:
        st.metric("Events", traces_df.iloc[selected_idx]['event_count'])
    with COL2:
        st.metric("Duration", f"{traces_df.iloc[selected_idx]['duration']:.2f}s")
    with COL3:
        st.metric("Start Time", traces_df.iloc[selected_idx]['start_time'].strftime("%H:%M:%S"))

    gantt_df = _dashboard_conn.execute("""
        SELECT span_id, agent_role,
               MIN(timestamp) as Start,
               MAX(timestamp) as Finish
        from traces
        WHERE trace_id = ?
        GROUP BY span_id, agent_role
        ORDER BY Start ASC
    """, [selected_trace]).df()

    if not gantt_df.empty:
        gantt_df["Start"] = pd.to_datetime(gantt_df["Start"], unit='s')
        gantt_df["Finish"] = pd.to_datetime(gantt_df["Finish"], unit='s')
        gantt_df["Duration"] = (gantt_df["Finish"] - gantt_df["Start"]).dt.total_seconds()

        FIG = px.timeline(
            gantt_df,
            x_start="Start",
            x_end="Finish",
            y="agent_role",
            color="agent_role",
            hover_data=["span_id", "Duration"],
            title="Agent Execution Timeline (Gantt Chart)"
        )
        FIG.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(FIG, use_container_width=True)
    else:
        st.warning("No span data available for timeline visualization")

    st.markdown("---")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("[PLAN] Event Stream")

        events_df = _dashboard_conn.execute("""
            SELECT span_id, event_type, timestamp, payload
            from traces
            WHERE trace_id = ?
            ORDER BY timestamp ASC
        """, [selected_trace]).df()

        selected_event_idx = None # Initialize selected_event_idx

        if not events_df.empty:
            events_df['timestamp'] = pd.to_datetime(events_df['timestamp'], unit='s')

            event_types = ["All"] + sorted(events_df['event_type'].unique().tolist())
            filter_type = st.selectbox("Filter by Event Type", event_types)

            if filter_type != "All":
                filtered_events = events_df[events_df['event_type'] == filter_type]
            else:
                filtered_events = events_df

            if not filtered_events.empty:
                selected_event_idx = st.selectbox(
                    "Select Event",
                    filtered_events.index,
                    format_func=lambda i: f"{filtered_events.loc[i,
                        'event_type']} @ {filtered_events.loc[i,
                        'timestamp'].strftime('%H:%M:%S.%f')[:-3]}"
                )
            else:
                st.info("No events match the selected filter.")
        else:
            st.warning("No events found")


    with col_right:
        st.subheader("[SCAN] Black Box Data")

        if selected_event_idx is not None and not events_df.empty:
            ROW = events_df.loc[selected_event_idx]

            st.info(f"**Event Type:** {ROW['event_type']}")
            st.info(f"**Span ID:** {ROW['span_id']}")
            st.info(f"**Timestamp:** {ROW['timestamp']}")

            try:
                PAYLOAD = json.loads(ROW['payload'])

                if ROW['event_type'] == 'THINK_COMPLETE' and 'reasoning' in PAYLOAD:
                    st.markdown("### 🧠 Agent Reasoning")
                    st.write(PAYLOAD['reasoning'])

                if ROW['event_type'] == 'MCP_CALL' and 'tool' in PAYLOAD:
                    st.markdown(f"### [+] Tool Call: `{PAYLOAD['tool']}`")
                    st.json(PAYLOAD.get('args', {}))

                if 'ERROR' in ROW['event_type']:
                    st.error("### [!] Error Event")
                    st.code(PAYLOAD.get('error_message', 'Unknown error'))

                with st.expander("📦 Full Payload (JSON)"):
                    st.json(PAYLOAD)

            except json.JSONDecodeError:
                st.text(ROW['payload'])
        else:
            st.info("Select an event from the stream to view details")

    st.markdown("---")
    st.subheader("[STATS] MCP Tool Performance")

    tool_stats_df = _dashboard_conn.execute("""
        SELECT json_extract_string(payload, '$.tool') as tool_name,
               COUNT(*) as calls
        from traces
        WHERE trace_id = ? and event_type = 'MCP_CALL'
        GROUP BY tool_name
        ORDER BY calls DESC
    """, [selected_trace]).df()

    if not tool_stats_df.empty:
        COL1, COL2 = st.columns([2, 1])

        with COL1:
            FIG = px.bar(
                tool_stats_df,
                x='tool_name',
                y='calls',
                title="Tool Usage Frequency",
                labels={'tool_name': 'Tool', 'calls': 'Number of Calls'}
            )
            st.plotly_chart(FIG, use_container_width=True)

        with COL2:
            st.dataframe(tool_stats_df, use_container_width=True)
    else:
        st.info("No MCP tool calls recorded for this trace")

    st.markdown("---")
    st.subheader("[!] Error Analysis")

    error_df = _dashboard_conn.execute("""
        SELECT span_id, event_type, timestamp, payload
        from traces
        WHERE trace_id = ? and event_type LIKE '%ERROR%'
        ORDER BY timestamp DESC
    """, [selected_trace]).df()

    if not error_df.empty:
        error_df['timestamp'] = pd.to_datetime(error_df['timestamp'], unit='s')

        for idx, ROW in error_df.iterrows():
            with st.expander(f"[X] {ROW['event_type']} @ {ROW['timestamp'].strftime('%H:%M:%S')}"):
                try:
                    PAYLOAD = json.loads(ROW['payload'])
                    st.error(PAYLOAD.get('error_message', 'Unknown error'))
                    st.json(PAYLOAD)
                except Exception:
                    st.text(ROW['payload'])
    else:
        st.success("[OK] No errors recorded for this trace")

    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Global Stats")

    try:
        total_events = _dashboard_conn.execute("SELECT COUNT(*) as count from traces").fetchone()[0]
        total_traces = _dashboard_conn.execute("SELECT COUNT(DISTINCT trace_id) as count from traces").fetchone()[0]

        st.sidebar.metric("Total Events (All Time)", f"{total_events:,}")
        st.sidebar.metric("Total Traces (All Time)", f"{total_traces:,}")
    except Exception as e:
        st.sidebar.error(f"Stats error: {e}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Flight Recorder v1.0**")
    st.sidebar.markdown("*Subatomic Agent Observatory*")

__all__ = [
    "__version__",
    "compliance",
    "run_flight_recorder_dashboard", # Expose the dashboard launcher
]

# This block allows the __init__.py to be run directly by Streamlit for the dashboard
if __name__ == "__main__":
    # Check if Streamlit is running this script
    if 'streamlit' in sys.modules and st._is_running_with_streamlit:
        run_flight_recorder_dashboard()
    else:
        # If imported or run as a regular Python script, do not launch UI
        _logger.info("agentic_core package imported. Flight Recorder Dashboard not launched automatically.")
        _logger.info("To run the dashboard, use: streamlit run path/to/agentic_core/__init__.py")