from __future__ import annotations
'\nTime Tools - Atomic Module\nExtracted from action_registry.py via Atomic Fission Protocol\nTool ID Prefix: ACT-008\n'
import logging
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger: Any = logging.getLogger('ActionRegistry.TimeTools')

class TimeTools:
    """
    Provides time-related functionalities, including current time and conversion.
    Tool ID Prefix: ACT-008
    """

    def __init__(self):
        """Initializes TimeTools. No specific state needed."""

    def _get_current_time_fallback(self, timezone: str) -> str:
        """
        Helper to get current time using datetime/pytz if mcp_time_client is unavailable.

        Args:
            timezone (str): The IANA timezone string (e.g., "UTC", "America/New_York").

        Returns:
            str: The current time in ISO 8601 format or an error message.
        """
        try:
            from datetime import datetime
            import pytz
        except ImportError:
            return "Error: 'pytz' module not installed for timezone operations. Please install it (`pip install pytz`)."
        # guardian: allow-silent-swallow
        except Exception as e:
            return f'Error during fallback import for time tools: {e}'
        try:
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
            return now.isoformat()
        except pytz.UnknownTimeZoneError:
            return f"Error: Unknown timezone '{timezone}'. Please provide a valid IANA timezone string."
        # guardian: allow-silent-swallow
        except Exception as e:
            return f'Error getting time with pytz: {e}'

    def get_current_time(self, timezone: str='UTC') -> str:
        """
        Gets the current date, time, and timezone in ISO 8601 format.
        Tool ID: ACT-008

        Args:
            timezone (str): The IANA timezone string (e.g., "UTC", "America/New_York").
                            Defaults to "UTC".

        Returns:
            str: The current time in ISO 8601 format or an error message.
        """
        Logger.info(f"⏰ Getting current time for timezone: '{timezone}'")
        try:
            from mcp_time_client import get_current_time as mcp_get_time
            return mcp_get_time(timezone)
        except ImportError:
            Logger.warning('MCP Time client not found, falling back to local time calculation.')
            return self._get_current_time_fallback(timezone)
        # guardian: allow-silent-swallow
        except Exception as e:
            return f'Error with MCP Time client for get_current_time: {e}'

    def convert_time(self, source_timezone: str, time: str, target_timezone: str) -> str:
        """
        Converts a time string between two specified IANA timezones.
        Tool ID: ACT-009

        Args:
            source_timezone (str): The IANA timezone of the input `time`.
            time (str): The time string to convert (e.g., "2023-10-27T10:00:00+00:00").
            target_timezone (str): The IANA timezone to convert the time to.

        Returns:
            str: The converted time string in ISO 8601 format or an error message.
        """
        Logger.info(f"[~] Converting time '{time}' from '{source_timezone}' to '{target_timezone}'")
        try:
            from mcp_time_client import convert_time as mcp_convert_time
            return mcp_convert_time(source_timezone, time, target_timezone)
        except ImportError:
            return "Error: MCP Time client not available for time conversion. This functionality requires 'mcp_time_client'."
        # guardian: allow-silent-swallow
        except Exception as e:
            return f'Error with MCP Time client for convert_time: {e}'
__all__ = ['TimeTools']
