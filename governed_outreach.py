"""
Governed Outreach Sequence - Master Function for Outreach Engine
Integrates L4 Temporal Awareness with Action Layer and L5 MEMemory
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Import the temporal vetting function
from temporal_vetting import vet_lead_optimal_time

def execute_governed_outreach_sequence(
    lead_timezone: str, 
    pitch_content: str, 
    recipient_email: str, 
    tools: Dict[str, Any],
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Master function for Outreach Engine. Orchestrates temporal compliance check (L4) 
    before executing the final Send Email action. (Hardened Governance)
    
    Args:
        lead_timezone: IANA timezone for the lead (e.g., 'America/New_York')
        pitch_content: Email content to send
        recipient_email: Target email address
        tools: Dictionary containing MCP tools
        logger: Optional logger instance
    
    Returns:
        Dictionary containing the final status and audit information
    """
    if logger:
        logger.info(f"🚀 Starting Governed Outreach Sequence for {recipient_email}")

    # Extract required tools
    get_current_time = tools.get('get_current_time')
    send_email = tools.get('send_email')
    add_observations = tools.get('add_observations')
    
    # Validate tools
    if not all([get_current_time, send_email]):
        return {
            "status": "ERROR_TOOLS_MISSING",
            "message": "Required MCP tools not available"
        }
    
    final_status = "PENDING"
    
    # --- 1. Get Current Time (L4 Time) ---
    try:
        time_str = get_current_time("UTC")
        # Extract only the HH:MM part for the conversion check
        current_utc_time_hm = datetime.fromisoformat(time_str.replace('Z', '+00:00')).strftime('%H:%M')
        
        if logger:
            logger.info(f"Current UTC time: {current_utc_time_hm}")
    except Exception as e:
        if logger:
            logger.error(f"Failed to get current time: {e}")
        return {
            "status": "ERROR_TIME_FETCH",
            "message": "Failed to retrieve current time"
        }
    
    # --- 2. Temporal Compliance Check (L4 Time, Sequential Thinking) ---
    vetting_result = vet_lead_optimal_time(lead_timezone, current_utc_time_hm, tools, logger)
    
    send_allowed = vetting_result['send_now']
    lead_local_time = vetting_result['lead_local_time']
    decision = vetting_result['decision']
    
    # --- 3. Action Gateway (Sequential Thinking) ---
    if send_allowed:
        # A. SEND NOW Path (Compliance Passed)
        try:
            # Create email subject from pitch content
            subject = f"Contextual Outreach: {pitch_content[:50]}..."
            
            # Send the email
            email_result = send_email(
                recipient=recipient_email,
                subject=subject,
                body=pitch_content
            )
            
            final_status = "SENT_COMPLIANT"
            
            if logger:
                logger.info(f"✅ Compliance Passed. Email DISPATCHED. Result: {email_result}")
                
        except Exception as e:
            final_status = "SENT_FAILED"
            if logger:
                logger.error(f"❌ Email Dispatch Failed: {e}")
            
    else:
        # B. DELAY Path (Compliance Failed)
        final_status = "TEMPORAL_DELAY"
        
        # Calculate next optimal send time (simplified)
        next_send_time = calculate_next_business_time(lead_local_time, lead_timezone)
        
        if logger:
            logger.warning(f"⚠️ Temporal Delay. Local Time ({lead_local_time}) is outside business hours. Action DEFERRED.")
            logger.info(f"💡 Next optimal send time: {next_send_time}")

    # --- 4. Audit Log (L5 MEMemory) ---
    try:
        if add_observations:
            audit_message = f"OUTREACH AUDIT: Status={final_status}. Recipient={recipient_email}. LeadTZ={lead_timezone}. LocalTime={lead_local_time}. Decision={decision}."
            add_observations(observations=[{
                "entityName": "OutreachAudit",
                "contents": [audit_message]
            }])
    except:
        if logger:
            logger.warning("⚠️ L5 MEMemory logging failed (non-critical).")

    # Build result
    result = {
        "status": final_status,
        "lead_timezone": lead_timezone,
        "lead_local_time": lead_local_time,
        "decision": decision,
        "message": f"Sequence finished with status: {final_status}."
    }
    
    # Add next send time for delayed messages
    if final_status == "TEMPORAL_DELAY":
        result["next_optimal_send_time"] = next_send_time
    
    return result

def calculate_next_business_time(current_local_time: str, timezone: str) -> str:
    """
    Calculates the next optimal business time for sending.
    Simplified implementation - in production would use Time MCP for precise calculation.
    """
    try:
        current_hour = int(current_local_time.split(':')[0])
        
        if current_hour < 9:  # Before business hours
            return f"09:00 {timezone}"
        elif current_hour >= 17:  # After business hours
            return f"09:00 {timezone} (next business day)"
        else:
            return f"{current_local_time} {timezone}"
    except:
        return f"09:00 {timezone} (next business day)"

# Example usage and test
if __name__ == "__main__":
    # Mock tools for testing
    def mock_get_current_time(tz):
        return "2025-12-15T14:00:00Z"
    
    def mock_send_email(recipient, subject, body):
        return f"Email sent to {recipient}"
    
    def mock_add_observations(observations):
        pass
    
    mock_tools = {
        'get_current_time': mock_get_current_time,
        'send_email': mock_send_email,
        'add_observations': mock_add_observations
    }
    
    # Test with different timezones
    print("=== Governed Outreach Test Results ===")
    
    # Test case 1: Should send (New York - 10:00 AM)
    result1 = execute_governed_outreach_sequence(
        lead_timezone="America/New_York",
        pitch_content="Hello, I'd like to connect...",
        recipient_email="lead@example.com",
        tools=mock_tools
    )
    print(f"\nTest 1 - New York:")
    print(f"Status: {result1['status']}")
    print(f"Decision: {result1['decision']}")
    print(f"Local Time: {result1['lead_local_time']}")
    
    # Test case 2: Should delay (Shanghai - 10:00 PM)
    result2 = execute_governed_outreach_sequence(
        lead_timezone="Asia/Shanghai",
        pitch_content="Hello, I'd like to connect...",
        recipient_email="lead@example.com",
        tools=mock_tools
    )
    print(f"\nTest 2 - Shanghai:")
    print(f"Status: {result2['status']}")
    print(f"Decision: {result2['decision']}")
    print(f"Local Time: {result2['lead_local_time']}")
    if 'next_optimal_send_time' in result2:
        print(f"Next Send Time: {result2['next_optimal_send_time']}")
