import os
import json
import time
import hashlib
from typing import Any, Dict, Optional
from datetime import datetime

# Import core utilities for P5 compliance
from core_utils import (
    add_observations,
    register_process,
    log_action,
    convert_time,
)

# Import hardened MCP functions
from mcp_hardening import (
    ensure_brand_compliance,
    get_brand_style_guide
)

# Import egress filter for Protocol 8
from network_utils import strict_egress_filter, NetworkViolationError

# Import consensus engine for P6
from consensus_engine import jury

# Configuration variables
MAX_PITCH_REFINEMENTS = int(os.environ.get("MAX_PITCH_REFINEMENTS", "2"))
SHADOW_MODE_ACTIVE = os.environ.get("AGENT_MODE", "PRODUCTION") == "SHADOW"

# Define the specific allow-list for the Outreach Engine
OUTREACH_ALLOWED_HOSTS = [
    "api.openai.com", "anthropic.com", "genai.google.com",  # LLM APIs
    "smtp.sendgrid.net", "mailgun.com",  # Email/SMTP providers
    "linkedin.com", "www.linkedin.com"  # Professional networking
]

# P8 Egress Filter decorator for network calls
@strict_egress_filter(allowed_domains=OUTREACH_ALLOWED_HOSTS)
def _fetch_company_content(url: str, fetch_tool: Any, max_length: int = 1000) -> Optional[str]:
    """Fetches company content with egress filtering."""
    return fetch_tool(url=url, max_length=max_length)

# P10 Shadow Mode Engine
class ShadowModeEngine:
    """Handles pitch refinement in shadow mode without side effects."""
    
    @staticmethod
    def refine_pitch(pitch: str, error_reason: str) -> Dict[str, Any]:
        """
        Refines a pitch based on compliance errors in shadow mode.
        Returns refined pitch without executing any side effects.
        """
        # Simple refinement logic - in production this would use LLM
        refined_pitch = pitch
        
        # Common brand compliance fixes
        if "spam" in error_reason.lower():
            refined_pitch = refined_pitch.replace("!!!", "!").replace("$$$", "$")
        
        if "unprofessional" in error_reason.lower():
            refined_pitch = refined_pitch.replace("hey", "Dear").replace("yo", "Hello")
        
        if "too long" in error_reason.lower():
            # Truncate to reasonable length
            sentences = refined_pitch.split(". ")
            refined_pitch = ". ".join(sentences[:5]) + "."
        
        return {
            "status": "SUCCESS",
            "content": refined_pitch,
            "refinements_applied": error_reason
        }

# Pitch Generator
class PitchGenerator:
    """Generates personalized outreach pitches."""
    
    @staticmethod
    def generate_pitch(context: str, relationships: str) -> Dict[str, Any]:
        """Generate initial personalized pitch."""
        # Simple pitch generation - in production this would use LLM
        subject = "Potential Collaboration Opportunity"
        
        pitch_body = f"""Dear [Contact Name],

I hope this message finds you well. I wanted to reach out regarding potential collaboration opportunities.

{context[:200]}...

Given my background and expertise, I believe there could be valuable opportunities for collaboration.

I would appreciate the chance to discuss how I might contribute to your team's success.

Best regards,
[Your Name]

Generated via Agentic Workflow Outreach Engine
"""
        
        return {
            "status": "SUCCESS",
            "subject": subject,
            "content": pitch_body
        }

def execute_outreach_zse(
    company_url: str,
    contact_info: Dict[str, Any],
    tools: Dict[str, Any],
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Execute Zero-Side Effect (ZSE) Outreach with P6 Vetting and P10 Shadow Mode.
    
    Args:
        company_url: Target company URL
        contact_info: Contact information including email, name, timezone
        tools: Dictionary of MCP tools
        logger: Optional logger instance
    
    Returns:
        Dict with execution status and details
    """
    # P5 Compliance: Register the process ID for Watchdog monitoring
    register_process()
    log_action("PROCESS_REGISTRATION_COMPLETE", "OutreachEngineZSE ZSE process started")
    
    if logger:
        logger.info(f"🚀 Starting ZSE Outreach for {company_url}")
    
    # Extract tools
    fetch_tool = tools.get('fetch')
    search_nodes = tools.get('search_nodes')
    send_email = tools.get('send_email')
    
    # Validate required tools
    if not all([fetch_tool, search_nodes, send_email]):
        return {
            "status": "FAILED",
            "reason": "Required MCP tools not available"
        }
    
    # --- Step 1: Fetch Company Context (L1) ---
    try:
        log_action("L1_FETCH_START", f"Retrieving company context from {company_url}")
        company_context = _fetch_company_content(company_url, fetch_tool, max_length=1000)
        if logger:
            logger.info(f"✅ Fetched company context from {company_url}")
    except NetworkViolationError as e:
        log_action("P8_VIOLATION", f"Egress filter blocked: {str(e)}")
        return {
            "status": "FAILED",
            "reason": "P8_EGRESS_VIOLATION",
            "details": str(e)
        }
    except Exception as e:
        log_action("L1_FETCH_ERROR", str(e))
        return {
            "status": "FAILED",
            "reason": "FETCH_ERROR",
            "details": str(e)
        }
    
    # --- Step 2: L5 Knowledge Retrieval ---
    try:
        log_action("L5_SEARCH_START", "Retrieving contact relationships")
        contact_query = f"Contact relationships for {company_url}"
        contacts_str = search_nodes(query=contact_query)
        contacts_data = json.loads(contacts_str) if contacts_str else {"entities": []}
        
        # Extract primary contact
        primary_contact = contact_info if contact_info else {
            "name": "Hiring Manager",
            "email": "contact@company.com",
            "timezone": "America/New_York"
        }
        
        if logger:
            logger.info(f"✅ Retrieved contact context for {primary_contact['name']}")
    except Exception as e:
        log_action("L5_SEARCH_ERROR", str(e))
        return {
            "status": "FAILED",
            "reason": "L5_SEARCH_ERROR",
            "details": str(e)
        }
    
    # --- Step 3: L4 Time Conversion ---
    try:
        log_action("L4_TIME_START", "Converting to optimal send time")
        # Get current time and convert to contact's timezone
        optimal_send_time = convert_time(
            source_timezone="America/New_York",
            time="09:00",  # 9 AM local time
            target_timezone=primary_contact.get("timezone", "America/New_York")
        )
        if logger:
            logger.info(f"✅ Optimal send time calculated: {optimal_send_time}")
    except Exception as e:
        log_action("L4_TIME_ERROR", str(e))
        optimal_send_time = "09:00"  # Default fallback
    
    # --- Step 4: Initial Pitch Generation ---
    try:
        log_action("PITCH_GENERATE_START", "Generating initial personalized pitch")
        pitch_result = PitchGenerator.generate_pitch(
            context=company_context,
            relationships=contacts_str or "No prior relationship"
        )
        
        pitch_draft = {
            "subject": pitch_result["subject"],
            "content": pitch_result["content"]
        }
        
        if logger:
            logger.info("✅ Initial pitch generated")
    except Exception as e:
        log_action("PITCH_GENERATE_ERROR", str(e))
        return {
            "status": "FAILED",
            "reason": "PITCH_GENERATION_ERROR",
            "details": str(e)
        }
    
    # --- Step 5: ZSE Loop: VET, SHADOW MODE, AND SELF-CORRECT ---
    refinement_count = 0
    
    while refinement_count <= MAX_PITCH_REFINEMENTS:
        # Check max attempts
        if refinement_count > 0 and refinement_count > MAX_PITCH_REFINEMENTS:
            log_action("ZSE_FAIL_MAX_ATTEMPTS", f"Max {MAX_PITCH_REFINEMENTS} refinements reached")
            add_observations([{
                "entityName": f"ZSE_Outreach_{hash(company_url)}",
                "observations": [f"ZSE_FAIL_MAX_ATTEMPTS: {refinement_count} attempts made"]
            }])
            return {
                "status": "FAILED",
                "reason": "ZSE_MAX_ATTEMPTS_REACHED",
                "attempts": refinement_count
            }
        
        # P6 Consensus Vetting
        try:
            log_action("P6_VET_START", f"Vetting pitch compliance (attempt {refinement_count + 1})")
            
            # Get brand style guide
            brand_guide = get_brand_style_guide(brand_id="default")
            
            # Use consensus engine to vet the pitch
            p6_result = jury.judge_artifact(
                artifact=pitch_draft["content"],
                criteria=brand_guide.get("rules", ["professional", "no_spam", "brand_compliant"])
            )
            
            # Convert consensus result to simple pass/fail
            if p6_result.get("verdict") == "APPROVED":
                p6_vet_result = {"status": "SUCCESS"}
            else:
                p6_vet_result = {
                    "status": "FAIL",
                    "reason": p6_result.get("reason", "Brand compliance failure")
                }
            
            if logger:
                logger.info(f"✅ P6 vetting complete: {p6_vet_result['status']}")
                
        except Exception as e:
            log_action("P6_VET_ERROR", str(e))
            p6_vet_result = {
                "status": "FAIL",
                "reason": f"P6 vetting error: {str(e)}"
            }
        
        # ZSE Vetting Gate
        if p6_vet_result["status"] == "SUCCESS":
            # Pitch passed compliance - proceed to send
            break
        else:
            # Pitch failed compliance - trigger P10 Shadow Mode
            if refinement_count >= MAX_PITCH_REFINEMENTS:
                log_action("ZSE_FAIL_MAX_ATTEMPTS", "Max refinements reached")
                add_observations([{
                    "entityName": f"ZSE_Outreach_{hash(company_url)}",
                    "observations": [f"ZSE_FAIL_MAX_ATTEMPTS: Could not achieve compliance"]
                }])
                return {
                    "status": "FAILED",
                    "reason": "ZSE_MAX_ATTEMPTS_REACHED",
                    "attempts": refinement_count + 1
                }
            
            refinement_count += 1
            log_action("P10_SHADOW_START", f"Refinement attempt {refinement_count}")
            
            # P10 Shadow Mode Self-Correction
            try:
                shadow_result = ShadowModeEngine.refine_pitch(
                    pitch=pitch_draft["content"],
                    error_reason=p6_vet_result["reason"]
                )
                
                # Apply the refinement
                pitch_draft["content"] = shadow_result["content"]
                
                # Log the refinement
                add_observations([{
                    "entityName": f"ZSE_Outreach_{hash(company_url)}",
                    "observations": [
                        f"P10_SHADOW_REFINEMENT_{refinement_count}",
                        f"Reason: {p6_vet_result['reason']}",
                        f"Refinements: {shadow_result.get('refinements_applied', 'N/A')}"
                    ]
                }])
                
                if logger:
                    logger.info(f"✅ P10 shadow refinement applied (attempt {refinement_count})")
                    
            except Exception as e:
                log_action("P10_SHADOW_ERROR", str(e))
                return {
                    "status": "FAILED",
                    "reason": "P10_REFINEMENT_ERROR",
                    "details": str(e)
                }
    
    # --- Step 6: FINALIZATION (ZSE Success Path) ---
    log_action("ZSE_SUCCESS", "Pitch passed P6 compliance. Executing final side effect.")
    
    # Prepare final email
    final_subject = pitch_draft["subject"].replace("[Contact Name]", primary_contact["name"])
    final_body = pitch_draft["content"].replace("[Contact Name]", primary_contact["name"])
    final_body = final_body.replace("[Your Name]", "Agentic Workflow User")
    
    # Execute Side Effect (Send Email)
    try:
        if SHADOW_MODE_ACTIVE:
            # Shadow mode - don't actually send
            log_action("SEND_EMAIL_SHADOW", f"Shadow mode: Email to {primary_contact['email']} blocked")
            send_result = {"status": "SUCCESS", "result": "SHADOW_BLOCKED"}
            
            if logger:
                logger.warning(f"👻 SHADOW MODE: Email to {primary_contact['email']} blocked")
        else:
            # Production mode - send the email
            send_result = send_email(
                recipient=primary_contact["email"],
                subject=final_subject,
                body=final_body
            )
            
            log_action("SEND_EMAIL_SUCCESS", f"Email sent to {primary_contact['email']}")
            
            if logger:
                logger.info(f"✅ Email sent to {primary_contact['email']}")
    
    except Exception as e:
        log_action("SEND_EMAIL_ERROR", str(e))
        return {
            "status": "FAILED",
            "reason": "SEND_EMAIL_ERROR",
            "details": str(e)
        }
    
    # Final P5 and L5 Logging
    pitch_hash = hashlib.sha256(final_body.encode()).hexdigest()[:16]
    
    # L5 updates the Knowledge Graph
    add_observations([{
        "entityName": f"ZSE_Outreach_{hash(company_url)}",
        "observations": [
            "OUTREACH_COMPLETE",
            f"Status: SENT",
            f"Recipient: {primary_contact['email']}",
            f"Pitch hash: {pitch_hash}",
            f"Refinements: {refinement_count}"
        ]
    }])
    
    return {
        "status": "SUCCESS",
        "message": "ZSE Outreach completed successfully",
        "recipient": primary_contact["email"],
        "refinements": refinement_count,
        "pitch_hash": pitch_hash,
        "send_result": send_result
    }
