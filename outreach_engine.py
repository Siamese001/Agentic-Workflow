import time
import json
from typing import Dict, Any, Optional

def automated_lead_vetting(company_url: str, user_name: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Implements the 'Automated Lead Vetting & Contact' use case, integrating L1 (Fetch), 
    L3 (Pinecone), and L5 (MEMemory) to perform context-aware outreach.
    """
    if logger:
        logger.info(f"🚀 Starting Automated Lead Vetting for {company_url} (User: {user_name})...")

    # Extract tools from the tools dictionary
    fetch = tools.get('fetch')
    search_nodes = tools.get('search_nodes')
    search_records = tools.get('search_records')
    send_email = tools.get('send_email')

    # Validate required tools
    if not all([fetch, search_nodes, search_records, send_email]):
        return {"status": "error", "message": "Required MCP tools not available"}

    # --- Step 1: Fetch Company News (L1 Fetch) ---
    try:
        # Fetch the company's latest news or press releases
        company_news = fetch(url=company_url, max_length=1000)
        if logger:
            logger.info(f"✅ Fetched company content from {company_url}")
    except Exception as e:
        return {"status": "error", "message": f"Fetch MCP failed to retrieve company data: {e}"}

    # --- Step 2: Get Contact Context (L5 MEMemory) ---
    try:
        # Search for the user's connections at the target company
        contact_query = f"{user_name} connections contacts relationships at company from {company_url}"
        contacts_str = search_nodes(query=contact_query)
        contacts_data = json.loads(contacts_str)
        
        # Extract relevant contacts
        target_contacts = []
        for entity in contacts_data.get('entities', []):
            if 'CEO' in entity.get('title', '') or 'Manager' in entity.get('title', ''):
                target_contacts.append(entity)
        
        if logger:
            logger.info(f"✅ Found {len(target_contacts)} key contacts in MEMemory")
    except Exception as e:
        return {"status": "error", "message": f"MEMemory MCP failed to retrieve contacts: {e}"}

    # --- Step 3: Retrieve Outreach Template (L3 Pinecone) ---
    # Use the company news to find the most relevant outreach template
    pinecone_query = f"Best outreach pitch template for: {company_news[:200]}..."
    try:
        search_result_str = search_records(query=pinecone_query, index="outreach_templates", top_k=1, namespace="outreach")
        search_result = json.loads(search_result_str)
        outreach_template = search_result[0].get('text', '')
        
        if not outreach_template:
            outreach_template = "I hope this message finds you well. I wanted to reach out regarding..."
        
        if logger:
            logger.info("✅ Retrieved L3 outreach template from Pinecone.")
            
    except Exception as e:
        # Fallback to generic template if Pinecone fails
        outreach_template = "I hope this message finds you well. I wanted to reach out regarding potential collaboration opportunities."
        if logger:
            logger.warning(f"⚠️ Pinecone lookup failed, using fallback template: {e}")
        
    # --- Step 4: Synthesize Personalized Pitch ---
    
    # Extract key information from company news for personalization
    news_keywords = []
    if 'launch' in company_news.lower():
        news_keywords.append('recent launch')
    if 'funding' in company_news.lower():
        news_keywords.append('recent funding')
    if 'award' in company_news.lower():
        news_keywords.append('recent achievement')
    
    # Build personalized email content
    primary_contact = target_contacts[0] if target_contacts else {"name": "Hiring Manager", "email": "contact@company.com"}
    
    personalized_pitch = f"""Subject: Re: {', '.join(news_keywords) if news_keywords else 'Potential Collaboration'}

Dear {primary_contact.get('name', 'Hiring Manager')},

{outreach_template}

I was particularly impressed by {', '.join(news_keywords) if news_keywords else 'the innovative work'} at your organization. Given my background and expertise, I believe there could be valuable opportunities for collaboration.

I would appreciate the chance to discuss how I might contribute to your team's success.

Best regards,
{user_name}

---
Generated via Agentic Workflow Outreach Engine
Context: Automated lead vetting based on recent company activity
"""

    # --- Step 5: Send Email (Action Tool) ---
    try:
        email_result = send_email(
            recipient=primary_contact.get('email', 'contact@company.com'),
            subject=f"Re: {', '.join(news_keywords) if news_keywords else 'Potential Collaboration'}",
            body=personalized_pitch
        )
        
        if logger:
            logger.info(f"✅ Email sent to {primary_contact.get('email')}")
            
    except Exception as e:
        return {"status": "error", "message": f"Failed to send email: {e}"}

    # --- Step 6: Update Memory with Outreach Activity ---
    try:
        # Log the outreach activity for future reference
        memory_update = [{
            "entityName": user_name,
            "contents": [
                f"Reached out to {primary_contact.get('name')} at {company_url} on {time.strftime('%Y-%m-%d')}",
                f"Context: {', '.join(news_keywords) if news_keywords else 'General outreach'}"
            ]
        }]
        
        add_observations = tools.get('add_observations')
        if add_observations:
            add_observations(observations=memory_update)
            if logger:
                logger.info("✅ MEMemory updated with outreach activity")
        
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ Memory update failed (non-critical): {e}")

    return {
        "status": "success",
        "message": f"Lead vetted and outreach email sent to {primary_contact.get('name')}",
        "contact": primary_contact.get('name'),
        "email": primary_contact.get('email'),
        "context": news_keywords,
        "email_result": email_result
    }

def vet_lead_optimal_time(lead_email: str, lead_timezone: str, pitch_body: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Leverages the Time MCP (L4) and MEMemory (L5) to determine the best time to contact a lead, 
    and then sends the initial email using the Send Email MCP.
    """
    if logger:
        logger.info(f"⏰ Starting optimal contact time vetting for {lead_email} in {lead_timezone}.")

    # Extract Time MCP tools
    get_current_time = tools.get('get_current_time')
    convert_time = tools.get('convert_time')
    send_email = tools.get('send_email')
    search_nodes = tools.get('search_nodes')

    # Validate required tools
    if not all([get_current_time, convert_time, send_email, search_nodes]):
        return {"status": "error", "message": "Required Time MCP tools not available"}

    # --- Step 1: Get System Time (L4 Time MCP) ---
    try:
        # Get the current time in the agent's system timezone (local time)
        system_time_str = get_current_time(timezone=None)
        system_time_data = json.loads(system_time_str)
        # We need to extract the current time in HH:MM format for the next step
        current_time_hhmm = system_time_data['datetime'][11:16] 

        if logger:
            logger.info(f"✅ Retrieved agent's current time: {current_time_hhmm}")
    except Exception as e:
        return {"status": "error", "message": f"Time MCP (get_current_time) failed: {e}"}

    # --- Step 2: Convert Time to Lead's Local Time (L4 Time MCP) ---
    # We use the current system time to estimate what time it is RIGHT NOW for the lead.
    try:
        # Assuming agent's system timezone is 'America/New_York' for this example
        converted_time_str = convert_time(
            source_timezone="America/New_York",
            time=current_time_hhmm, 
            target_timezone=lead_timezone
        )
        converted_data = json.loads(converted_time_str)
        lead_local_time = converted_data['target']['datetime'][11:16] 

        if logger:
            logger.info(f"✅ Lead's current local time: {lead_local_time}")
            
    except Exception as e:
        return {"status": "error", "message": f"Time MCP (convert_time) failed: {e}"}

    # --- Step 3: Strategic Decision (LLM/Cognitive Node) ---
    # Decide if the current time is appropriate (e.g., between 9:00 and 17:00 local time)
    lead_hour = int(lead_local_time.split(':')[0])
    
    if 9 <= lead_hour < 17:
        decision = "Optimal: Proceed with outreach now."
        send_now = True
    else:
        decision = "Off-Hours: Defer outreach until next business day (Requires Calendar MCP)."
        send_now = False

    if logger:
        logger.info(f"🧠 Decision: {decision}")
    
    # --- Step 4: Execute Action (Send Email MCP) ---
    if send_now:
        try:
            subject = f"Contextual Pitch: {pitch_body[:20]}..."
            send_result = send_email(recipient=lead_email, subject=subject, body=pitch_body)
            
            # L5: Log successful outreach (MEMemory)
            try:
                memory_update = [{
                    "entityName": "outreach_engine",
                    "contents": [
                        f"Sent pitch to {lead_email} at {lead_local_time} local time.",
                        f"Timezone: {lead_timezone}, Decision: {decision}"
                    ]
                }]
                add_observations = tools.get('add_observations')
                if add_observations:
                    add_observations(observations=memory_update)
            except Exception as mem_e:
                if logger:
                    logger.warning(f"⚠️ MEMemory logging failed (non-critical): {mem_e}")
            
            return {"status": "contacted", "message": f"Email dispatched at optimal time. {send_result}"}
            
        except Exception as e:
            return {"status": "error", "message": f"Send Email MCP failed: {e}"}
            
    else:
        # L5: Log deferred outreach
        try:
            memory_update = [{
                "entityName": "outreach_engine",
                "contents": [
                    f"Outreach to {lead_email} deferred.",
                    f"Local time was {lead_local_time} in {lead_timezone}.",
                    f"Reason: Outside business hours (9:00-17:00). Requires Calendar MCP for auto-scheduling."
                ]
            }]
            add_observations = tools.get('add_observations')
            if add_observations:
                add_observations(observations=memory_update)
        except Exception as mem_e:
            if logger:
                logger.warning(f"⚠️ MEMemory logging failed (non-critical): {mem_e}")

        return {"status": "deferred", "message": f"Outreach deferred. Local time {lead_local_time} is outside business hours. Requires Calendar MCP for auto-scheduling."}
