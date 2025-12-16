"""
Temporal Vetting Module for Outreach Engine
L4 Temporal Awareness - Ensures optimal contact times
"""
from datetime import datetime
from typing import Any, Dict, Optional


def vet_lead_optimal_time(lead_timezone: str, current_send_time_utc: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Vets the lead's local time using the Time MCP (L4) to determine optimal outreach time.
    Enforces temporal compliance (Sequential Thinking).

    Args:
        lead_timezone: IANA timezone string for the lead (e.g., 'America/New_York')
        current_send_time_utc: Current time in UTC in HH:MM format
        tools: Dictionary containing MCP tools
        logger: Optional logger instance

    Returns:
        Dictionary containing:
        - send_now (bool): Whether to send the email now
        - lead_local_time (str): Lead's local time in HH:MM format
        - decision (str): Human-readable decision
    """
    if logger:
        logger.info(f"⌚ Starting Temporal Vetting for {lead_timezone}")

    # --- 1. Define Business Hours ---
    # Target window is 9:00 AM to 5:00 PM (Exclusive of 5 PM)
    START_HOUR = 9
    END_HOUR = 17

    send_now = False
    lead_local_time = "N/A"

    # --- 2. Convert Time (L4 Time) ---
    # Note: current_send_time_utc should be the HH:MM part of the Time MCP output
    source_timezone = "UTC"  # Assuming the input time is provided in UTC

    try:
        # Get convert_time from tools dictionary
        convert_time = tools.get('convert_time')
        if not convert_time:
            raise Exception("convert_time tool not available")

        # Use the actual Time MCP to convert time
        conversion_result_str = convert_time(
            source_timezone, current_send_time_utc, lead_timezone)

        # Parse the ISO format result to extract HH:MM
        converted_time = datetime.fromisoformat(
            conversion_result_str.replace('Z', '+00:00'))
        lead_local_time = converted_time.strftime('%H:%M')

        # --- 3. Temporal Vetting (Sequential Thinking) ---

        # Parse the hour part (e.g., '10:00' -> 10)
        local_hour = int(lead_local_time.split(':')[0])

        if START_HOUR <= local_hour < END_HOUR:
            send_now = True
            decision = "SEND NOW"
        else:
            decision = "DELAY"

        if logger:
            logger.info(
                f"Lead Local Time: {lead_local_time}. Decision: {decision}.")

    except Exception as e:
        if logger:
            logger.error(
                f"Time conversion/vetting failed: {e}. Defaulting to DELAY for safety.")
        decision = "ERROR_DELAY"
        send_now = False

    # --- 4. Audit Log (L5 MEMemory) ---
    try:
        # Get add_observations from tools if available
        add_observations = tools.get('add_observations')
        if add_observations:
            add_observations(observations=[{
                "entityName": "TemporalAudit",
                "contents": [f"Temporal Vetting: TZ={lead_timezone}. LocalTime={lead_local_time}. Decision={decision}."]
            }])
        if logger:
            logger.info(
                f"Audit: Temporal Vetting - TZ={lead_timezone}, LocalTime={lead_local_time}, Decision={decision}")
    except Exception:
        if logger:
            logger.warning("⚠️ L5 MEMemory logging failed (non-critical).")

    return {
        "send_now": send_now,
        "lead_local_time": lead_local_time,
        "decision": decision
    }


# Example usage and test cases
if __name__ == "__main__":
    # Test cases for different timezones
    test_cases = [
        ("America/New_York", "14:00"),  # Should be 10:00 AM (SEND NOW)
        ("Asia/Shanghai", "14:00"),     # Should be 10:00 PM (DELAY)
        ("Europe/London", "14:00"),      # Should be 2:00 PM (SEND NOW)
        ("Australia/Sydney", "14:00"),   # Should be 1:00 AM next day (DELAY)
    ]

    # print("=== Temporal Vetting Test Results ===")  # [Security Fix]
    for tz, utc_time in test_cases:
        result = vet_lead_optimal_time(tz, utc_time, {}) # Mock tools for example
        # print(f"\nTimezone: {tz}")  # [Security Fix]
        # print(f"UTC Time: {utc_time}")  # [Security Fix]
        # print(f"Local Time: {result['lead_local_time']}")  # [Security Fix]
        # print(f"Decision: {result['decision']}")  # [Security Fix]