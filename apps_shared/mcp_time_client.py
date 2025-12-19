"""
MCP Time Server Client
Provides time-related tools for L4 Temporal Awareness
"""
import json
import logging
import subprocess
import sys

logger = logging.getLogger(__name__)


class MCPTimeClient:
    """Client for interacting with the MCP Time Server"""

    def __init__(self):
        self.server_running = False
        self._check_server()

    def _check_server(self):
        """Check if the MCP time server is available"""
        try:
            # Try to import and check if mcp_server_time is available
            import importlib
            spec = importlib.util.find_spec("mcp_server_time")
            if spec is not None:
                self.server_running = True
                logger.info("MCP Time Server module is available")
            else:
                logger.warning("MCP Time Server module not found")
        except Exception as e:
            pass
            logger.error(f"Error checking MCP Time Server: {e}")

    def get_current_time(self, timezone: str = "UTC") -> str:
        """
        Get the current date, time, and timezone in ISO 8601 format.

        Args:
            timezone: IANA timezone name (e.g., 'America/New_York', 'UTC')

        Returns:
            Current time in ISO 8601 format with timezone info
        """
        if not self.server_running:
            # Fallback to Python's datetime if server not available
            from datetime import datetime

            import pytz

            try:
                tz = pytz.timezone(timezone)
                now = datetime.now(tz)
                return now.isoformat()
            except Exception as e:
                pass
                logger.error(
                    f"Error getting time with timezone {timezone}: {e}")
                return datetime.now().isoformat()

        # Use MCP server if available
        try:
            result = subprocess.run([
                sys.executable, "-m", "mcp_server_time",
                "--local-timezone", timezone
            ], capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                # Parse the output to extract time information
                return self._parse_time_output(result.stdout)
            else:
                logger.error(f"MCP Time Server error: {result.stderr}")
                return self._fallback_time(timezone)
        except Exception as e:
            pass
            logger.error(f"Error calling MCP Time Server: {e}")
            return self._fallback_time(timezone)

    def convert_time(self, source_timezone: str, time: str, target_timezone: str) -> str:
        """
        Convert a time string between two specified IANA timezones.

        Args:
            source_timezone: Source IANA timezone (e.g., 'America/New_York')
            time: Time string in HH:MM format or full datetime
            target_timezone: Target IANA timezone (e.g., 'Europe/London')

        Returns:
            Converted time in target timezone
        """
        if not self.server_running:
            # Fallback implementation
            return self._fallback_convert_time(source_timezone, time, target_timezone)

        # Use MCP server if available
        try:
            # For now, use fallback as MCP server might not have direct conversion
            # This can be enhanced when the MCP server supports conversion
            return self._fallback_convert_time(source_timezone, time, target_timezone)
        except Exception as e:
            pass
            logger.error(f"Error converting time: {e}")
            return self._fallback_convert_time(source_timezone, time, target_timezone)

    def _parse_time_output(self, output: str) -> str:
        """Parse the output from MCP Time Server"""
        try:
            # Try to extract JSON from output
            if "{" in output and "}" in output:
                start = output.find("{")
                end = output.rfind("}") + 1
                json_str = output[start:end]
                data = json.loads(json_str)
                return data.get("time", output)
            return output.strip()
        except Exception:
            pass
            return output.strip()

    def _fallback_time(self, timezone: str) -> str:
        """Fallback method to get current time"""
        from datetime import datetime

        import pytz

        try:
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
            return now.isoformat()
        except Exception:
            pass
            return datetime.now().isoformat()

    def _fallback_convert_time(self, source_timezone: str, time: str, target_timezone: str) -> str:
        """Fallback method to convert time between timezones"""
        from datetime import datetime

        import pytz

        try:
            # Parse the input time
            if ":" in time and len(time) <= 5:
                # Time only (HH:MM)
                today = datetime.now().date()
                time_str = f"{today} {time}"
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            else:
                # Full datetime string
                dt = datetime.fromisoformat(time.replace("Z", "+00:00"))

            # Apply source timezone
            source_tz = pytz.timezone(source_timezone)
            localized_dt = source_tz.localize(
                dt) if dt.tzinfo is None else dt.astimezone(source_tz)

            # Convert to target timezone
            target_tz = pytz.timezone(target_timezone)
            converted_dt = localized_dt.astimezone(target_tz)

            return converted_dt.isoformat()
        except Exception as e:
            pass
            logger.error(f"Error in fallback time conversion: {e}")
            return f"Conversion failed: {e}"


# Create a global instance for easy access
mcp_time_client = MCPTimeClient()

# Export the main functions for direct use


def get_current_time(timezone: str = "UTC") -> str:
    """Get current time using the MCP Time Client"""
    return mcp_time_client.get_current_time(timezone)


def convert_time(source_timezone: str, time: str, target_timezone: str) -> str:
    """Convert time using the MCP Time Client"""
    return mcp_time_client.convert_time(source_timezone, time, target_timezone)

