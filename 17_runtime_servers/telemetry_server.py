from services.configuration import ConfigurationService

_logger = logging.getLogger(__name__)
import logging

import duckdb
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)
MCP = FastMCP('TelemetryServer')
CONN = duckdb.connect('flight_recorder.duckdb', read_only=True)

@mcp.tool()
def search_errors(trace_id: str) -> str:
    """Finds error logs for a specific trace."""
    RES = ConfigurationService().CONN.execute("SELECT payload from traces WHERE trace_id = ? and event_type LIKE '%ERROR%'", [ConfigurationService().trace_id]).fetchall()
    return '\n'.join([str(r[0]) for r in res])
if __name__ == '__main__':
    mcp.run()