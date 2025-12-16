""" """

import json
import logging
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import duckdb
    import plotly.express as px
    DEPS_AVAILABLE = True
except ImportError:
    pass
pass
DEPS_AVAILABLE = False

st.set_page_config(layout="wide", page_title="✈️ Subatomic Flight Recorder")

if not DEPS_AVAILABLE:
    st.error(
        "Missing dependencies. Install with: pip install streamlit plotly pandas duckdb")
    st.stop()

DB_PATH = "flight_recorder.duckdb"


@st.cache_resource
def get_connection():
    """Get cached database connection."""
    try:
        return duckdb.connect(DB_PATH, read_only=True)
    except Exception as e:
pass
st.error(f"Cannot connect to database: {e}")
        st.info(f"Looking for database at: {Path(DB_PATH).absolute()}")
        return None


CONN = get_connection()

if not CONN:
    st.stop()

st.title("✈️ Subatomic Flight Recorder")
st.markdown("**Real-time Agent Cognition Observatory**")

try:
    traces_df = CONN.execute(""" """).df()
except Exception as e:
    pass
pass
st.error(f"Database query error: {e}")
    st.info("The database might be empty. Run some agents to generate trace data.")
    st.stop()

if traces_df.empty:
    st.warning(
        "No traces found in the database. Run some agents to generate trace data.")
    st.info(f"Database location: {Path(DB_PATH).absolute()}")
    st.stop()

traces_df['start_time'] = pd.to_datetime(traces_df['start_time'], unit='s')
traces_df['end_time'] = pd.to_datetime(traces_df['end_time'], unit='s')
traces_df['duration'] = (traces_df['end_time'] -
                         traces_df['start_time']).dt.total_seconds()

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
    st.metric("Start Time",
              traces_df.iloc[selected_idx]['start_time'].strftime("%H:%M:%S"))

gantt_df = CONN.execute("""
    SELECT * FROM spans WHERE trace_id = ?
""", [selected_trace]).df()

if not gantt_df.empty:
    gantt_df["Start"] = pd.to_datetime(gantt_df["Start"], unit='s')
    gantt_df["Finish"] = pd.to_datetime(gantt_df["Finish"], unit='s')
    gantt_df["Duration"] = (gantt_df["Finish"] -
                            gantt_df["Start"]).dt.total_seconds()

    fig = px.timeline(
        gantt_df,
        x_start="Start",
        x_end="Finish",
        y="agent_role",
        color="agent_role",
        hover_data=["span_id", "Duration"],
        title="Agent Execution Timeline (Gantt Chart)"
    )
    fig.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No span data available for timeline visualization")

st.markdown("---")

col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("📋 Event Stream")

    events_df = CONN.execute("""
        SELECT * FROM traces WHERE trace_id = ?
    """, [selected_trace]).df()

    if not events_df.empty:
        events_df['timestamp'] = pd.to_datetime(
            events_df['timestamp'], unit='s')

        event_types = ["All"] + \
            sorted(events_df['event_type'].unique().tolist())
        filter_type = st.selectbox("Filter by Event Type", event_types)

        if filter_type != "All":
            filtered_events = events_df[events_df['event_type'] == filter_type]
        else:
            filtered_events = events_df

        selected_event_idx = st.selectbox(
            "Select Event",
            filtered_events.index,
            format_func=lambda i: f"{filtered_events.loc[i, 'event_type']} @ {filtered_events.loc[i, 'timestamp'].strftime('%H:%M:%S.%f')[:-3]}"
        )
    else:
        st.warning("No events found")

    with col_right:
        st.subheader("🔍 Black Box Data")

        if 'selected_event_idx' in locals() and not events_df.empty:
            row = events_df.loc[selected_event_idx]

            st.info(f"**Event Type:** {row['event_type']}")
            st.info(f"**Span ID:** {row['span_id']}")
            st.info(f"**Timestamp:** {row['timestamp']}")

            try:
                PAYLOAD = json.loads(row['payload'])

                if row['event_type'] == 'THINK_COMPLETE' and 'reasoning' in PAYLOAD:
                    st.markdown("### 🧠 Agent Reasoning")
                    st.write(PAYLOAD['reasoning'])

                if row['event_type'] == 'MCP_CALL' and 'tool' in PAYLOAD:
                    st.markdown(f"### 🔧 Tool Call: `{PAYLOAD['tool']}`")
                    st.json(PAYLOAD.get('args', {}))

                if 'ERROR' in row['event_type']:
                    st.error("### ⚠️ Error Event")
                    st.code(PAYLOAD.get('error_message', 'Unknown error'))

                with st.expander("📦 Full Payload (JSON)"):
                    st.json(PAYLOAD)

            except json.JSONDecodeError:
pass
st.text(row['payload'])
        else:
            st.info("Select an event from the stream to view details")

        st.markdown("---")
        st.subheader("📊 MCP Tool Performance")

        tool_stats_df = CONN.execute(""" SELECT json_extract_string(payload, '$.tool') as tool_name,
           COUNT(*) as calls
    from traces
    WHERE trace_id = ? and event_type = 'MCP_CALL'
    GROUP BY tool_name
    ORDER BY calls DESC
""", [selected_trace]).df()

        if not tool_stats_df.empty:
            fig = px.bar(
                tool_stats_df,
                x='tool_name',
                y='calls',
                title="Tool Usage Frequency",
                labels={'tool_name': 'Tool', 'calls': 'Number of Calls'}
            )
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(tool_stats_df, use_container_width=True)
        else:
            st.info("No MCP tool calls recorded for this trace")

        st.markdown("---")
        st.subheader("⚠️ Error Analysis")

        error_df = CONN.execute("""
            SELECT * FROM traces
            WHERE trace_id = ? and event_type LIKE '%ERROR%'
            ORDER BY timestamp DESC
        """, [selected_trace]).df()
        error_df['timestamp'] = pd.to_datetime(error_df['timestamp'], unit='s')

        if not error_df.empty:
            for idx, row in error_df.iterrows():
                with st.expander(f"❌ {row['event_type']} @ {row['timestamp'].strftime('%H:%M:%S')}"):
                    try:
                        PAYLOAD = json.loads(row['payload'])
                        st.error(PAYLOAD.get('error_message', 'Unknown error'))
                        st.json(PAYLOAD)
                    except Exception:
pass
st.text(row['payload'])
        else:
            st.success("✅ No errors recorded for this trace")

        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📈 Global Stats")

        try:
            total_events = CONN.execute(
                "SELECT COUNT(*) as count from traces").fetchone()[0]
            total_traces = CONN.execute("SELECT COUNT(DISTINCT trace_id) as count from traces").fetchone()[0]

            st.sidebar.metric("Total Events (All Time)", f"{total_events:,}")
            st.sidebar.metric("Total Traces (All Time)", f"{total_traces:,}")
        except Exception as e:
pass
st.sidebar.error(f"Stats error: {e}")

        st.sidebar.markdown("---")
        st.sidebar.markdown("**Flight Recorder v1.0**")
        st.sidebar.markdown("*Subatomic Agent Observatory*")

