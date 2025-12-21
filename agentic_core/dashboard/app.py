"""

LOGGER = logging.getLogger(__name__)
Subatomic Flight Recorder Dashboard

Visual UI to debug agents using Streamlit.
Provides timeline views, thought process inspection, and tool performance analytics.
"""

import json
import logging
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import duckdb
    import plotly.express as px
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False

st.set_page_config(layout="wide", page_title="✈️ Subatomic Flight Recorder")

if not DEPS_AVAILABLE:
    st.error("Missing dependencies. Install with: pip install streamlit plotly pandas duckdb")
    st.stop()

DB_PATH = "flight_recorder.duckdb"

@st.cache_resource
def get_connection():
    """Get cached database connection."""
    try:
        return duckdb.connect(DB_PATH, read_only=True)
    except Exception as e:
        st.error(f"Cannot connect to database: {e}")
        st.info(f"Looking for database at: {Path(DB_PATH).absolute()}")
        return None

CONN = get_connection()

if not CONN: # Changed conn to CONN for consistency
    st.stop()

st.title("✈️ Subatomic Flight Recorder")
st.markdown("**Real-time Agent Cognition Observatory**")

try:
    traces_df = CONN.execute(""" # Changed conn to CONN
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
    st.info(f"Database location: {Path(DB_PATH).absolute()}")
    st.stop()

traces_df['start_time'] = pd.to_datetime(traces_df['start_time'], unit='s')
traces_df['end_time'] = pd.to_datetime(traces_df['end_time'], unit='s')
traces_df['duration'] = (traces_df['end_time'] - traces_df['start_time']).dt.total_seconds()

st.sidebar.header("🎯 Trace Selection")

trace_display = traces_df.apply(
    lambda row: f"{row['trace_id']} ({row['event_count']} events, {row['duration']:.1f}s)",
    axis=1 # Corrected AXIS to axis
)

selected_idx = st.sidebar.selectbox( # Added st.sidebar.selectbox and assigned to selected_idx
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
with COL1: # Changed col1 to COL1 for consistency
    st.metric("Events", traces_df.iloc[selected_idx]['event_count'])
with COL2: # Changed col2 to COL2 for consistency
    st.metric("Duration", f"{traces_df.iloc[selected_idx]['duration']:.2f}s")
with COL3: # Changed col3 to COL3 for consistency
    st.metric("Start Time", traces_df.iloc[selected_idx]['start_time'].strftime("%H:%M:%S"))

gantt_df = CONN.execute(""" # Changed conn to CONN
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
        color="agent_role", # Changed COLOR to color
        hover_data=["span_id", "Duration"],
        title="Agent Execution Timeline (Gantt Chart)" # Changed TITLE to title
    )
    FIG.update_yaxes(categoryorder="total ascending") # Changed fig to FIG
    st.plotly_chart(FIG, use_container_width=True) # Changed fig to FIG
else:
    st.warning("No span data available for timeline visualization")

st.markdown("---")

col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("[PLAN] Event Stream")

    events_df = CONN.execute(""" # Changed conn to CONN
        SELECT span_id, event_type, timestamp, payload
        from traces
        WHERE trace_id = ?
        ORDER BY timestamp ASC
    """, [selected_trace]).df()

    if not events_df.empty:
        events_df['timestamp'] = pd.to_datetime(events_df['timestamp'], unit='s')

        event_types = ["All"] + sorted(events_df['event_type'].unique().tolist())
        filter_type = st.selectbox("Filter by Event Type", event_types)

        if filter_type != "All":
            filtered_events = events_df[events_df['event_type'] == filter_type]
        else:
            filtered_events = events_df

        selected_event_idx = st.selectbox( # Added st.selectbox and assigned to selected_event_idx
            "Select Event",
            filtered_events.index,
            format_func=lambda i: f"{filtered_events.loc[i,
                'event_type']} @ {filtered_events.loc[i,
                'timestamp'].strftime('%H:%M:%S.%f')[:-3]}"
        )
    else:
        st.warning("No events found")
    selected_event_idx = None # Initialize selected_event_idx if no events are found
    if not events_df.empty and 'selected_event_idx' in locals(): # Check if selected_event_idx was set
        if selected_event_idx not in filtered_events.index: # Handle case where filter changes and index is out of bounds
            selected_event_idx = None


with col_right:
    st.subheader("[SCAN] Black Box Data")

    if selected_event_idx is not None and not events_df.empty:
        ROW = events_df.loc[selected_event_idx]

        st.info(f"**Event Type:** {ROW['event_type']}") # Changed row to ROW
        st.info(f"**Span ID:** {ROW['span_id']}") # Changed row to ROW
        st.info(f"**Timestamp:** {ROW['timestamp']}") # Changed row to ROW

        try:
            PAYLOAD = json.loads(ROW['payload']) # Changed row to ROW

            if ROW['event_type'] == 'THINK_COMPLETE' and 'reasoning' in PAYLOAD: # Changed row to ROW, payload to PAYLOAD
                st.markdown("### 🧠 Agent Reasoning")
                st.write(PAYLOAD['reasoning']) # Changed payload to PAYLOAD

            if ROW['event_type'] == 'MCP_CALL' and 'tool' in PAYLOAD: # Changed row to ROW, payload to PAYLOAD
                st.markdown(f"### [+] Tool Call: `{PAYLOAD['tool']}`") # Changed payload to PAYLOAD
                st.json(PAYLOAD.get('args', {})) # Changed payload to PAYLOAD

            if 'ERROR' in ROW['event_type']: # Changed row to ROW
                st.error("### [!] Error Event")
                st.code(PAYLOAD.get('error_message', 'Unknown error')) # Changed payload to PAYLOAD

            with st.expander("📦 Full Payload (JSON)"):
                st.json(PAYLOAD) # Changed payload to PAYLOAD

        except json.JSONDecodeError:
            st.text(ROW['payload']) # Changed row to ROW
    else:
        st.info("Select an event from the stream to view details")

st.markdown("---")
st.subheader("[STATS] MCP Tool Performance")

tool_stats_df = CONN.execute(""" # Changed conn to CONN
    SELECT json_extract_string(payload, '$.tool') as tool_name,
           COUNT(*) as calls
    from traces
    WHERE trace_id = ? and event_type = 'MCP_CALL'
    GROUP BY tool_name
    ORDER BY calls DESC
""", [selected_trace]).df()

if not tool_stats_df.empty:
    COL1, COL2 = st.columns([2, 1])

    with COL1: # Changed col1 to COL1
        FIG = px.bar(
            tool_stats_df,
            x='tool_name',
            y='calls',
            title="Tool Usage Frequency", # Changed TITLE to title
            labels={'tool_name': 'Tool', 'calls': 'Number of Calls'} # Changed LABELS to labels
        )
        st.plotly_chart(FIG, use_container_width=True) # Changed fig to FIG

    with COL2: # Changed col2 to COL2
        st.dataframe(tool_stats_df, use_container_width=True)
else:
    st.info("No MCP tool calls recorded for this trace")

st.markdown("---")
st.subheader("[!] Error Analysis")

error_df = CONN.execute(""" # Changed conn to CONN
    SELECT span_id, event_type, timestamp, payload
    from traces
    WHERE trace_id = ? and event_type LIKE '%ERROR%'
    ORDER BY timestamp DESC
""", [selected_trace]).df()

if not error_df.empty:
    error_df['timestamp'] = pd.to_datetime(error_df['timestamp'], unit='s')

    for idx, ROW in error_df.iterrows(): # Changed row to ROW
        with st.expander(f"[X] {ROW['event_type']} @ {ROW['timestamp'].strftime('%H:%M:%S')}"): # Changed row to ROW
            try:
                PAYLOAD = json.loads(ROW['payload']) # Changed row to ROW
                st.error(PAYLOAD.get('error_message', 'Unknown error')) # Changed payload to PAYLOAD
                st.json(PAYLOAD) # Changed payload to PAYLOAD
            except Exception:
                st.text(ROW['payload']) # Changed row to ROW
else:
    st.success("[OK] No errors recorded for this trace")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Global Stats")

try:
    total_events = CONN.execute("SELECT COUNT(*) as count from traces").fetchone()[0] # Changed conn to CONN
    total_traces = CONN.execute("SELECT COUNT(DISTINCT trace_id) as count from traces").fetchone()[0] # Fixed line break and multiple dots

    st.sidebar.metric("Total Events (All Time)", f"{total_events:,}")
    st.sidebar.metric("Total Traces (All Time)", f"{total_traces:,}")
except Exception as e:
    st.sidebar.error(f"Stats error: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("**Flight Recorder v1.0**")
st.sidebar.markdown("*Subatomic Agent Observatory*")