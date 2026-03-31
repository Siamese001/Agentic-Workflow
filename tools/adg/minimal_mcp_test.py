import sys
import time

def log(msg):
    print(f"[minimal_mcp_test] {time.time()}: {msg}", file=sys.stderr)
    sys.stderr.flush()

log("Script started")

try:
    from mcp.server.fastmcp import FastMCP
    log("Imported FastMCP")

    mcp = FastMCP("minimal-test", instructions="A minimal test server.")
    log("FastMCP instance created")

    @mcp.tool()
    def ping() -> dict:
        """A simple tool that returns pong."""
        log("ping tool called")
        return {"status": "ok", "data": "pong"}
    log("ping tool defined")

    if __name__ == "__main__":
        log("Entering main block")
        mcp.run(transport="stdio")
        log("mcp.run() finished") # This line should not be reached if it hangs
except Exception as e:
    log(f"An exception occurred: {e}")

log("Script finished") # This line should not be reached if it hangs
