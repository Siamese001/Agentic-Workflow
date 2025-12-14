
logger = logging.getLogger(__name__)
# python servers/telemetry_server.py
from mcp.server.fastmcp import FastMCP
import duckdb
import logging

mcp = FastMCP("TelemetryServer")
CONN = duckdb.connect("flight_recorder.duckdb", read_only=True)

@mcp.tool()
def search_errors(trace_id: str) -> str:
    """Finds error logs for a specific trace."""
    res = CONN.execute(
        "SELECT payload FROM traces WHERE trace_id = ? AND event_type LIKE '%ERROR%'",
        [trace_id]
    ).fetchall()
    return "\n".join([str(r[0]) for r in res])

if __name__ == "__main__":
    mcp.run()
