from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "time_utils_impl", "L2")
_emit_routes_through("p1", "time_utils_impl", "L2")
_emit_escalates_to_human("p1", "time_utils_impl", "L2")
_emit_reads_policy_state("p1", "time_utils_impl", "L2")

_emit_applies_guardrail("p0", "time_utils_impl", "p0_governance")
_emit_snapshots_state("p0", "time_utils_impl", "state_snapshot")

"\nTime Tools - Atomic Module\nExtracted from action_registry.py via Atomic Fission Protocol\nTool ID Prefix: ACT-008\n"
import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)

Logger: Any = logging.getLogger("ActionRegistry.TimeTools")


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
            return f"Error during fallback import for time tools: {e}"
        try:
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
            return now.isoformat()
        except pytz.UnknownTimeZoneError:
            return f"Error: Unknown timezone '{timezone}'. Please provide a valid IANA timezone string."
        # guardian: allow-silent-swallow
        except Exception as e:
            return f"Error getting time with pytz: {e}"

    def get_current_time(self, timezone: str = "UTC") -> str:
        """
        Gets the current date, time, and timezone in ISO 8601 format.
        Tool ID: ACT-008

        Args:
            timezone (str): The IANA timezone string (e.g., "UTC", "America/New_York").
                            Defaults to "UTC".

        Returns:
            str: The current time in ISO 8601 format or an error message.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "TimeTools.get_current_time")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TimeTools.get_current_time".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        Logger.info(f"⏰ Getting current time for timezone: '{timezone}'")
        try:
            from mcp_time_client import get_current_time as mcp_get_time

            return mcp_get_time(timezone)
        except ImportError:
            Logger.warning("MCP Time client not found, falling back to local time calculation.")
            return self._get_current_time_fallback(timezone)
        # guardian: allow-silent-swallow
        except Exception as e:
            return f"Error with MCP Time client for get_current_time: {e}"

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
            return f"Error with MCP Time client for convert_time: {e}"


__all__ = ["TimeTools"]
